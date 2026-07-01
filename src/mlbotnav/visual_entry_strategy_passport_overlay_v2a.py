from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from mlbotnav.visual_entry_low_anchor_suggester import _bar_width_days, _draw_candles, _load_ohlcv, _style_axis


STATUS = "V2A_STRUCTURE_LAYER_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA"
RAIL_POINT = "V2A_STRUCTURE_LAYER"
SYMBOL = "SOLUSDT"
TIMEFRAME = "1m"
SLIPPAGE_BPS = 5.0


@dataclass(frozen=True)
class Pivot:
    idx: int
    confirm_idx: int
    time_utc: pd.Timestamp
    kind: str
    price: float


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def _fmt_ts(value: pd.Timestamp) -> str:
    return value.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def _fmt_min(value: pd.Timestamp | str) -> str:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert("UTC").strftime("%H:%M")


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def _source_csv(root: Path, day: str) -> Path:
    return root / "data" / "core" / "bybit_ohlcv" / f"dt={day}" / "tf=1m" / f"symbol={SYMBOL}" / "part-final.csv"


def _ledger_path(root: Path, day: str) -> Path:
    if day != "2026-05-14":
        raise ValueError("V2A first pass is fixed to the 2026-05-14 M01-M19 manual ledger.")
    return root / "reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_M01_M19.json"


def _load_targets(root: Path, day: str) -> list[dict[str, Any]]:
    payload = json.loads(_ledger_path(root, day).read_text(encoding="utf-8"))
    targets: list[dict[str, Any]] = []
    for item in payload["targets"]:
        execution = item.get("execution_price", {})
        entry_time = pd.Timestamp(item["entry_time_utc"]).tz_convert("UTC")
        signal_time = pd.Timestamp(item["signal_time_utc"]).tz_convert("UTC")
        targets.append(
            {
                "target_id": str(item["target_id"]),
                "legacy_order_id": str(item.get("legacy_order_id") or item["target_id"]),
                "target_type": str(item.get("target_type") or "UNKNOWN"),
                "signal_time_utc": _fmt_ts(signal_time),
                "entry_time_utc": _fmt_ts(entry_time),
                "entry_open_price": _safe_float(execution.get("entry_open_price")),
                "entry_price_plus_5bps": _safe_float(execution.get("entry_price_with_slippage")),
                "slippage_bps": _safe_float(execution.get("slippage_bps"), SLIPPAGE_BPS),
                "status": str(item.get("status") or "manual_gold"),
            }
        )
    return targets


def _row_index_at_time(df: pd.DataFrame, time_utc: str) -> int:
    ts = pd.Timestamp(time_utc).tz_convert("UTC")
    matched = df.index[df["open_time_utc"] == ts].tolist()
    if not matched:
        raise ValueError(f"No OHLCV row for {time_utc}")
    return int(matched[0])


def _add_closed_bar_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for window in [60, 120, 240]:
        out[f"range_low_{window}"] = out["low"].rolling(window, min_periods=1).min()
        out[f"range_high_{window}"] = out["high"].rolling(window, min_periods=1).max()
        denom = (out[f"range_high_{window}"] - out[f"range_low_{window}"]).replace(0, np.nan)
        out[f"range_pos_{window}"] = (out["close"] - out[f"range_low_{window}"]) / denom
        out[f"room_to_high_{window}_bps"] = (out[f"range_high_{window}"] - out["close"]) / out["close"] * 10000.0
        out[f"dist_from_low_{window}_bps"] = (out["close"] - out[f"range_low_{window}"]) / out["close"] * 10000.0
    out["range"] = out["high"] - out["low"]
    out["body"] = (out["close"] - out["open"]).abs()
    out["lower_wick"] = np.minimum(out["open"], out["close"]) - out["low"]
    out["upper_wick"] = out["high"] - np.maximum(out["open"], out["close"])
    out["volume_ma20_prior"] = out["volume"].rolling(20, min_periods=1).mean().shift(1)
    out["volume_ratio20"] = out["volume"] / out["volume_ma20_prior"].replace(0, np.nan)
    return out


def _raw_pivots(df: pd.DataFrame, *, left: int, right: int) -> list[Pivot]:
    pivots: list[Pivot] = []
    highs = df["high"].to_numpy()
    lows = df["low"].to_numpy()
    for idx in range(left, len(df) - right):
        high_window = highs[idx - left : idx + right + 1]
        low_window = lows[idx - left : idx + right + 1]
        current_high = highs[idx]
        current_low = lows[idx]
        time = pd.Timestamp(df.iloc[idx]["open_time_utc"]).tz_convert("UTC")
        if current_high >= float(np.max(high_window)) and np.count_nonzero(high_window == current_high) == 1:
            pivots.append(Pivot(idx=idx, confirm_idx=idx + right, time_utc=time, kind="H", price=float(current_high)))
        if current_low <= float(np.min(low_window)) and np.count_nonzero(low_window == current_low) == 1:
            pivots.append(Pivot(idx=idx, confirm_idx=idx + right, time_utc=time, kind="L", price=float(current_low)))
    return sorted(pivots, key=lambda item: (item.idx, item.kind))


def _zigzag_pivots(raw: list[Pivot], *, deviation_pct: float) -> list[Pivot]:
    accepted: list[Pivot] = []
    for pivot in raw:
        if not accepted:
            accepted.append(pivot)
            continue
        last = accepted[-1]
        if pivot.kind == last.kind:
            more_extreme = (pivot.kind == "H" and pivot.price > last.price) or (pivot.kind == "L" and pivot.price < last.price)
            if more_extreme:
                accepted[-1] = pivot
            continue
        move_pct = abs(pivot.price / max(last.price, 1e-9) - 1.0) * 100.0
        if move_pct >= deviation_pct:
            accepted.append(pivot)
    return accepted


def _confirmed_before(pivots: list[Pivot], idx: int, *, lookback: int | None = None) -> list[Pivot]:
    start = 0 if lookback is None else max(0, idx - lookback)
    return [pivot for pivot in pivots if pivot.confirm_idx <= idx and pivot.idx >= start]


def _merge_levels(pivots: list[Pivot], *, merge_tolerance_pct: float = 0.15) -> list[dict[str, Any]]:
    levels: list[dict[str, Any]] = []
    for pivot in sorted(pivots, key=lambda item: item.price):
        found: dict[str, Any] | None = None
        for level in levels:
            if abs(pivot.price / max(float(level["price"]), 1e-9) - 1.0) * 100.0 <= merge_tolerance_pct:
                found = level
                break
        if found is None:
            levels.append({"price": pivot.price, "touches": 1, "first_idx": pivot.idx, "last_idx": pivot.idx})
        else:
            touches = int(found["touches"]) + 1
            found["price"] = (float(found["price"]) * int(found["touches"]) + pivot.price) / touches
            found["touches"] = touches
            found["last_idx"] = max(int(found["last_idx"]), pivot.idx)
    return levels


def _nearest_levels(df: pd.DataFrame, pivots_3: list[Pivot], idx: int) -> dict[str, Any]:
    row = df.iloc[idx]
    close = float(row["close"])
    confirmed = _confirmed_before(pivots_3, idx, lookback=240)
    low_levels = _merge_levels([pivot for pivot in confirmed if pivot.kind == "L"])
    high_levels = _merge_levels([pivot for pivot in confirmed if pivot.kind == "H"])
    support_pool = [level for level in low_levels if float(level["price"]) <= close * 1.001]
    resistance_pool = [level for level in high_levels if float(level["price"]) >= close * 0.999]
    support = max(support_pool, key=lambda level: float(level["price"]), default=None)
    resistance = min(resistance_pool, key=lambda level: float(level["price"]), default=None)
    support_price = float(support["price"]) if support else None
    resistance_price = float(resistance["price"]) if resistance else None
    support_dist_pct = None if support_price is None else (close / support_price - 1.0) * 100.0
    resistance_dist_pct = None if resistance_price is None else (resistance_price / close - 1.0) * 100.0
    return {
        "support_price": support_price,
        "support_touches": int(support["touches"]) if support else 0,
        "support_dist_pct": support_dist_pct,
        "resistance_price": resistance_price,
        "resistance_touches": int(resistance["touches"]) if resistance else 0,
        "resistance_dist_pct": resistance_dist_pct,
        "level_count": len(low_levels) + len(high_levels),
    }


def _fib_state(zigzag_10: list[Pivot], idx: int) -> dict[str, Any]:
    confirmed = _confirmed_before(zigzag_10, idx, lookback=240)
    if len(confirmed) < 2:
        return {"status": "no_confirmed_pivot_pair", "levels": {}}
    b = confirmed[-1]
    a = next((pivot for pivot in reversed(confirmed[:-1]) if pivot.kind != b.kind), None)
    if a is None:
        return {"status": "no_alternating_pair", "levels": {}}
    if a.kind == "L" and b.kind == "H":
        direction = "UP_LEG"
        swing_low = float(a.price)
        swing_high = float(b.price)
        span = swing_high - swing_low
        levels = {
            "0.000": swing_high,
            "0.236": swing_high - span * 0.236,
            "0.382": swing_high - span * 0.382,
            "0.500": swing_high - span * 0.500,
            "0.618": swing_high - span * 0.618,
            "0.786": swing_high - span * 0.786,
            "1.000": swing_low,
        }
    elif a.kind == "H" and b.kind == "L":
        direction = "DOWN_LEG"
        swing_high = float(a.price)
        swing_low = float(b.price)
        span = swing_high - swing_low
        levels = {
            "0.000": swing_low,
            "0.236": swing_low + span * 0.236,
            "0.382": swing_low + span * 0.382,
            "0.500": swing_low + span * 0.500,
            "0.618": swing_low + span * 0.618,
            "0.786": swing_low + span * 0.786,
            "1.000": swing_high,
        }
    else:
        return {"status": "invalid_pair", "levels": {}}
    if span <= 0:
        return {"status": "invalid_range", "levels": {}}
    return {
        "status": "ok",
        "direction": direction,
        "anchor_a": {"kind": a.kind, "time_utc": _fmt_ts(a.time_utc), "price": round(float(a.price), 8)},
        "anchor_b": {"kind": b.kind, "time_utc": _fmt_ts(b.time_utc), "price": round(float(b.price), 8)},
        "levels": {key: round(float(value), 8) for key, value in levels.items()},
    }


def _channel_state(df: pd.DataFrame, idx: int, *, window: int = 120) -> dict[str, Any]:
    start = max(0, idx - window + 1)
    win = df.iloc[start : idx + 1]
    if len(win) < 20:
        return {"status": "not_enough_bars"}
    x = np.arange(len(win), dtype=float)
    y = win["close"].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    fitted = slope * x + intercept
    resid = y - fitted
    sigma = float(np.std(resid)) or 1e-9
    current_center = float(fitted[-1])
    current_close = float(y[-1])
    pos_sigma = (current_close - current_center) / sigma
    return {
        "status": "ok",
        "window": window,
        "slope_per_bar": round(float(slope), 8),
        "center_price": round(current_center, 8),
        "upper_price": round(current_center + sigma, 8),
        "lower_price": round(current_center - sigma, 8),
        "pos_sigma": round(float(pos_sigma), 6),
    }


def _last_structure_event(df: pd.DataFrame, pivots: list[Pivot], idx: int, *, lookback: int, max_age: int) -> dict[str, Any]:
    confirmed = _confirmed_before(pivots, idx, lookback=lookback)
    highs = [pivot for pivot in confirmed if pivot.kind == "H"]
    lows = [pivot for pivot in confirmed if pivot.kind == "L"]
    last_high = highs[-1] if highs else None
    last_low = lows[-1] if lows else None
    row = df.iloc[idx]
    close = float(row["close"])
    bos_up = bool(last_high and idx - last_high.idx <= max_age and close >= last_high.price)
    bos_down = bool(last_low and idx - last_low.idx <= max_age and close <= last_low.price)

    prev_events: list[dict[str, Any]] = []
    scan_start = max(0, idx - max_age)
    for j in range(scan_start, idx + 1):
        local_confirmed = _confirmed_before(pivots, j, lookback=lookback)
        local_highs = [pivot for pivot in local_confirmed if pivot.kind == "H"]
        local_lows = [pivot for pivot in local_confirmed if pivot.kind == "L"]
        local_close = float(df.iloc[j]["close"])
        if local_highs and local_close >= local_highs[-1].price:
            prev_events.append({"idx": j, "event": "BOS_UP", "level": local_highs[-1].price})
        if local_lows and local_close <= local_lows[-1].price:
            prev_events.append({"idx": j, "event": "BOS_DOWN", "level": local_lows[-1].price})
    last_event = prev_events[-1] if prev_events else None
    previous_opposite = None
    if last_event:
        opposite_name = "BOS_DOWN" if last_event["event"] == "BOS_UP" else "BOS_UP"
        previous_opposite = next((event for event in reversed(prev_events[:-1]) if event["event"] == opposite_name), None)
    choch_like = bool(last_event and previous_opposite and last_event["idx"] >= idx - 12)
    return {
        "last_high": None if last_high is None else {"time_utc": _fmt_ts(last_high.time_utc), "price": round(last_high.price, 8)},
        "last_low": None if last_low is None else {"time_utc": _fmt_ts(last_low.time_utc), "price": round(last_low.price, 8)},
        "bos_up_now": bos_up,
        "bos_down_now": bos_down,
        "last_event": last_event["event"] if last_event else None,
        "last_event_age_bars": None if last_event is None else idx - int(last_event["idx"]),
        "choch_like_near_signal": choch_like,
    }


def _breakout_retest_state(df: pd.DataFrame, pivots_3: list[Pivot], idx: int) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    scan_start = max(0, idx - 60)
    for j in range(scan_start, idx + 1):
        levels = _nearest_levels(df, pivots_3, max(0, j - 1))
        close = float(df.iloc[j]["close"])
        high_level = levels.get("resistance_price")
        low_level = levels.get("support_price")
        if high_level and close >= float(high_level):
            events.append({"idx": j, "event": "BREAK_UP", "level": float(high_level)})
        if low_level and close <= float(low_level):
            events.append({"idx": j, "event": "BREAK_DOWN", "level": float(low_level)})
    last_break = events[-1] if events else None
    row = df.iloc[idx]
    retest = False
    retest_side = None
    if last_break:
        level = float(last_break["level"])
        tolerance = 0.001
        if last_break["event"] == "BREAK_UP":
            retest = bool(float(row["low"]) <= level * (1.0 + tolerance) and float(row["close"]) >= level * (1.0 - tolerance))
            retest_side = "UP_RETEST_SUPPORT" if retest else None
        else:
            retest = bool(float(row["high"]) >= level * (1.0 - tolerance) and float(row["close"]) <= level * (1.0 + tolerance))
            retest_side = "DOWN_RETEST_RESISTANCE" if retest else None
    return {
        "last_break_event": None if last_break is None else last_break["event"],
        "last_break_age_bars": None if last_break is None else idx - int(last_break["idx"]),
        "last_break_level": None if last_break is None else round(float(last_break["level"]), 8),
        "retest_near_signal": retest,
        "retest_side": retest_side,
    }


def _analysis_for_target(
    df: pd.DataFrame,
    target: dict[str, Any],
    *,
    pivots_3: list[Pivot],
    pivots_internal: list[Pivot],
    pivots_external: list[Pivot],
    zigzag_10: list[Pivot],
) -> dict[str, Any]:
    signal_idx = _row_index_at_time(df, str(target["signal_time_utc"]))
    entry_idx = _row_index_at_time(df, str(target["entry_time_utc"]))
    row = df.iloc[signal_idx]
    levels = _nearest_levels(df, pivots_3, signal_idx)
    fib = _fib_state(zigzag_10, signal_idx)
    channel = _channel_state(df, signal_idx)
    breakout = _breakout_retest_state(df, pivots_3, signal_idx)
    internal = _last_structure_event(df, pivots_internal, signal_idx, lookback=120, max_age=120)
    external = _last_structure_event(df, pivots_external, signal_idx, lookback=240, max_age=240)

    fib_0382 = fib.get("levels", {}).get("0.382")
    fib_0618 = fib.get("levels", {}).get("0.618")
    close = float(row["close"])
    fib_0382_dist_pct = None if fib_0382 is None else (close / float(fib_0382) - 1.0) * 100.0
    fib_0618_dist_pct = None if fib_0618 is None else (close / float(fib_0618) - 1.0) * 100.0

    range_pos_240 = _safe_float(row.get("range_pos_240"), 0.5)
    support_dist = levels.get("support_dist_pct")
    resistance_dist = levels.get("resistance_dist_pct")
    support_hint = support_dist is not None and abs(float(support_dist)) <= 0.25
    range_hint = range_pos_240 <= 0.35
    fib_hint = any(value is not None and abs(float(value)) <= 0.25 for value in [fib_0382_dist_pct, fib_0618_dist_pct])
    retest_hint = bool(breakout.get("retest_near_signal"))
    structure_hint = bool(internal.get("bos_up_now") or internal.get("choch_like_near_signal") or external.get("bos_up_now"))
    conflict_hint = bool(range_pos_240 >= 0.80 and not support_hint)

    return {
        **target,
        "signal_idx": signal_idx,
        "entry_idx": entry_idx,
        "signal_close": round(close, 8),
        "range_pos_240": round(range_pos_240, 6),
        "room_to_high_240_bps": round(_safe_float(row.get("room_to_high_240_bps")), 4),
        "volume_ratio20": round(_safe_float(row.get("volume_ratio20")), 4),
        "B014_level_range_channel": {
            **levels,
            "range_low_240": round(_safe_float(row.get("range_low_240")), 8),
            "range_high_240": round(_safe_float(row.get("range_high_240")), 8),
            "range_pos_240": round(range_pos_240, 6),
            "channel": channel,
            "visual_state": "support" if support_hint or range_hint else ("conflict" if conflict_hint else "silent"),
        },
        "B015_fibonacci_grid": {
            **fib,
            "fib_0382_dist_pct": None if fib_0382_dist_pct is None else round(float(fib_0382_dist_pct), 6),
            "fib_0618_dist_pct": None if fib_0618_dist_pct is None else round(float(fib_0618_dist_pct), 6),
            "visual_state": "support" if fib_hint else "silent",
        },
        "B017_breakout_retest": {
            **breakout,
            "visual_state": "support" if retest_hint else "silent",
        },
        "B018_market_structure": {
            "internal": internal,
            "external": external,
            "visual_state": "support" if structure_hint else "silent",
        },
        "V2A_visual_summary": {
            "supporting_blocks": [
                block
                for block, ok in [
                    ("B014_LEVEL_RANGE_CHANNEL", support_hint or range_hint),
                    ("B015_FIBONACCI_GRID", fib_hint),
                    ("B017_BREAKOUT_RETEST", retest_hint),
                    ("B018_MARKET_STRUCTURE", structure_hint),
                ]
                if ok
            ],
            "conflict_blocks": ["B014_LEVEL_RANGE_CHANNEL"] if conflict_hint else [],
            "note": "visual_evidence_only_not_allow_signal",
        },
    }


def _draw_volume(ax: Any, df: pd.DataFrame, *, alpha: float = 0.62) -> None:
    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(df["open"], df["close"])]
    ax.bar(df["open_time_utc"].dt.tz_convert(None), df["volume"], width=_bar_width_days(TIMEFRAME), color=colors, alpha=alpha)


def _draw_target_marker(ax: Any, target: dict[str, Any], *, show_price: bool) -> None:
    signal = pd.Timestamp(target["signal_time_utc"]).tz_convert(None)
    entry = pd.Timestamp(target["entry_time_utc"]).tz_convert(None)
    price = float(target["entry_price_plus_5bps"])
    ax.axvline(signal, color="#ffd54f", alpha=0.65, linewidth=1.0, zorder=3)
    ax.axvline(entry, color="#00e676", alpha=0.85, linewidth=1.25, zorder=3)
    ax.scatter([entry], [price], marker="^", s=72, color="#00e676", edgecolors="white", linewidths=0.55, zorder=8)
    label = f"{target['target_id']} {entry.strftime('%H:%M')}"
    if show_price:
        label += f" p+5={price:.4f}"
    ax.annotate(label, xy=(entry, price), xytext=(4, 7), textcoords="offset points", color="#00e676", fontsize=7)


def _draw_levels(ax: Any, item: dict[str, Any], *, xmin: Any, xmax: Any) -> None:
    level_block = item["B014_level_range_channel"]
    support = level_block.get("support_price")
    resistance = level_block.get("resistance_price")
    range_low = level_block.get("range_low_240")
    range_high = level_block.get("range_high_240")
    if support:
        ax.hlines(float(support), xmin, xmax, color="#4dd0e1", linestyle="-", alpha=0.62, linewidth=0.9)
        ax.text(xmax, float(support), "S", color="#4dd0e1", fontsize=7, ha="right", va="bottom")
    if resistance:
        ax.hlines(float(resistance), xmin, xmax, color="#ffb74d", linestyle="-", alpha=0.54, linewidth=0.9)
        ax.text(xmax, float(resistance), "R", color="#ffb74d", fontsize=7, ha="right", va="bottom")
    if range_low:
        ax.hlines(float(range_low), xmin, xmax, color="#26c6da", linestyle=":", alpha=0.34, linewidth=0.8)
    if range_high:
        ax.hlines(float(range_high), xmin, xmax, color="#ffa726", linestyle=":", alpha=0.30, linewidth=0.8)


def _draw_fib(ax: Any, item: dict[str, Any], *, xmin: Any, xmax: Any) -> None:
    fib = item["B015_fibonacci_grid"]
    if fib.get("status") != "ok":
        return
    colors = {
        "0.382": "#ce93d8",
        "0.500": "#b0bec5",
        "0.618": "#f48fb1",
    }
    for key, color in colors.items():
        price = fib.get("levels", {}).get(key)
        if price is None:
            continue
        ax.hlines(float(price), xmin, xmax, color=color, linestyle="--", alpha=0.58, linewidth=0.8)
        ax.text(xmax, float(price), f"F{key}", color=color, fontsize=6.5, ha="right", va="center")


def _draw_channel(ax: Any, item: dict[str, Any], win: pd.DataFrame) -> None:
    channel = item["B014_level_range_channel"].get("channel", {})
    if channel.get("status") != "ok":
        return
    signal = pd.Timestamp(item["signal_time_utc"]).tz_convert("UTC")
    hist = win[win["open_time_utc"] <= signal]
    if hist.empty:
        return
    x = np.arange(len(hist), dtype=float)
    y = hist["close"].to_numpy(dtype=float)
    slope = float(channel["slope_per_bar"])
    center_signal = float(channel["center_price"])
    center = center_signal + slope * (x - x[-1])
    sigma = float(channel["upper_price"]) - center_signal
    times = hist["open_time_utc"].dt.tz_convert(None)
    ax.plot(times, center, color="#90a4ae", linewidth=0.8, alpha=0.55)
    ax.plot(times, center + sigma, color="#90a4ae", linewidth=0.65, linestyle=":", alpha=0.40)
    ax.plot(times, center - sigma, color="#90a4ae", linewidth=0.65, linestyle=":", alpha=0.40)


def _draw_pivots(ax: Any, pivots: list[Pivot], start: pd.Timestamp, end: pd.Timestamp) -> None:
    shown = [pivot for pivot in pivots if start <= pivot.time_utc <= end]
    for pivot in shown:
        marker = "^" if pivot.kind == "H" else "v"
        color = "#ffb74d" if pivot.kind == "H" else "#4dd0e1"
        ax.scatter([pivot.time_utc.tz_convert(None)], [pivot.price], marker=marker, s=14, color=color, alpha=0.45, zorder=5)


def _render_full_day(df: pd.DataFrame, records: list[dict[str, Any]], *, day: str, out_path: Path) -> None:
    fig = plt.figure(figsize=(28, 12), facecolor="#101418")
    grid = fig.add_gridspec(2, 1, height_ratios=[4.6, 1.15], hspace=0.06)
    ax_price = fig.add_subplot(grid[0, 0])
    ax_vol = fig.add_subplot(grid[1, 0], sharex=ax_price)
    for ax in [ax_price, ax_vol]:
        _style_axis(ax)

    _draw_candles(ax_price, df, TIMEFRAME, linewidth=0.28)
    ax_price.plot(df["open_time_utc"].dt.tz_convert(None), df["range_low_240"], color="#26c6da", alpha=0.35, linewidth=0.75)
    ax_price.plot(df["open_time_utc"].dt.tz_convert(None), df["range_high_240"], color="#ffb74d", alpha=0.28, linewidth=0.75)

    for item in records:
        signal = pd.Timestamp(item["signal_time_utc"]).tz_convert("UTC")
        start = signal - pd.Timedelta(minutes=42)
        end = signal + pd.Timedelta(minutes=28)
        ax_price.axvspan(start.tz_convert(None), signal.tz_convert(None), color="#1565c0", alpha=0.035, zorder=0)
        ax_price.axvspan(signal.tz_convert(None), end.tz_convert(None), color="#00e676", alpha=0.030, zorder=0)
        _draw_target_marker(ax_price, item, show_price=False)

    _draw_volume(ax_vol, df)
    ax_price.set_title(
        f"{SYMBOL} {TIMEFRAME} {day} | V2A STRUCTURE PASSPORT OVERLAY | B014/B015/B017/B018 | NO ML/OPTUNA",
        color="white",
        fontsize=15,
    )
    ax_price.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    day_start = pd.Timestamp(f"{day}T00:00:00")
    day_end = day_start + pd.Timedelta(days=1)
    ax_price.set_xlim(day_start.to_pydatetime(), day_end.to_pydatetime())
    ax_vol.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 3)))
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate()
    fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def _render_zoom_page(
    df: pd.DataFrame,
    records: list[dict[str, Any]],
    *,
    pivots_3: list[Pivot],
    page: int,
    day: str,
    out_path: Path,
) -> None:
    cols = 2
    rows = int(np.ceil(len(records) / cols))
    fig = plt.figure(figsize=(24, max(7.0 * rows, 8.0)), facecolor="#101418")
    grid = fig.add_gridspec(rows * 2, cols, height_ratios=[4.0, 0.95] * rows, hspace=0.24, wspace=0.10)
    for n, item in enumerate(records):
        row = n // cols
        col = n % cols
        ax_price = fig.add_subplot(grid[row * 2, col])
        ax_vol = fig.add_subplot(grid[row * 2 + 1, col], sharex=ax_price)
        for ax in [ax_price, ax_vol]:
            _style_axis(ax)
        signal = pd.Timestamp(item["signal_time_utc"]).tz_convert("UTC")
        start = signal - pd.Timedelta(minutes=42)
        end = signal + pd.Timedelta(minutes=38)
        win = df[(df["open_time_utc"] >= start) & (df["open_time_utc"] <= end)].reset_index(drop=True)
        _draw_candles(ax_price, win, TIMEFRAME, linewidth=0.58)
        xmin = start.tz_convert(None).to_pydatetime()
        xmax = end.tz_convert(None).to_pydatetime()
        ax_price.axvspan(start.tz_convert(None), signal.tz_convert(None), color="#1565c0", alpha=0.055, zorder=0)
        ax_price.axvspan(signal.tz_convert(None), end.tz_convert(None), color="#00e676", alpha=0.040, zorder=0)
        _draw_levels(ax_price, item, xmin=xmin, xmax=xmax)
        _draw_fib(ax_price, item, xmin=xmin, xmax=xmax)
        _draw_channel(ax_price, item, win)
        _draw_pivots(ax_price, pivots_3, start, end)
        _draw_target_marker(ax_price, item, show_price=True)
        _draw_volume(ax_vol, win, alpha=0.66)
        ax_price.set_xlim(xmin, xmax)
        summary = item["V2A_visual_summary"]
        support = ",".join(summary["supporting_blocks"]) or "none"
        conflict = ",".join(summary["conflict_blocks"]) or "none"
        title = (
            f"{item['target_id']} {item['target_type']} | signal {_fmt_min(item['signal_time_utc'])} -> entry {_fmt_min(item['entry_time_utc'])} "
            f"| p+5 {float(item['entry_price_plus_5bps']):.4f} | support={support} | conflict={conflict}"
        )
        ax_price.set_title(title, color="white", fontsize=8.2)
        ax_price.set_ylabel("Price", color="white")
        ax_vol.set_ylabel("Vol", color="white")
        ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.suptitle(
        f"{SYMBOL} {TIMEFRAME} {day} | V2A zoom page {page:02d} | local strategy squares | visual only",
        color="white",
        fontsize=15,
    )
    fig.savefig(out_path, dpi=145, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def _write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    columns = [
        "target_id",
        "target_type",
        "signal_time_utc",
        "entry_time_utc",
        "entry_price_plus_5bps",
        "signal_close",
        "range_pos_240",
        "room_to_high_240_bps",
        "volume_ratio20",
        "support_price",
        "support_dist_pct",
        "resistance_price",
        "resistance_dist_pct",
        "fib_status",
        "fib_direction",
        "fib_0382_dist_pct",
        "fib_0618_dist_pct",
        "break_event",
        "retest_near_signal",
        "bos_up_internal",
        "bos_down_internal",
        "choch_like_internal",
        "supporting_blocks",
        "conflict_blocks",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for item in records:
            level = item["B014_level_range_channel"]
            fib = item["B015_fibonacci_grid"]
            breakout = item["B017_breakout_retest"]
            structure = item["B018_market_structure"]["internal"]
            summary = item["V2A_visual_summary"]
            writer.writerow(
                {
                    "target_id": item["target_id"],
                    "target_type": item["target_type"],
                    "signal_time_utc": item["signal_time_utc"],
                    "entry_time_utc": item["entry_time_utc"],
                    "entry_price_plus_5bps": item["entry_price_plus_5bps"],
                    "signal_close": item["signal_close"],
                    "range_pos_240": item["range_pos_240"],
                    "room_to_high_240_bps": item["room_to_high_240_bps"],
                    "volume_ratio20": item["volume_ratio20"],
                    "support_price": level.get("support_price"),
                    "support_dist_pct": level.get("support_dist_pct"),
                    "resistance_price": level.get("resistance_price"),
                    "resistance_dist_pct": level.get("resistance_dist_pct"),
                    "fib_status": fib.get("status"),
                    "fib_direction": fib.get("direction"),
                    "fib_0382_dist_pct": fib.get("fib_0382_dist_pct"),
                    "fib_0618_dist_pct": fib.get("fib_0618_dist_pct"),
                    "break_event": breakout.get("last_break_event"),
                    "retest_near_signal": breakout.get("retest_near_signal"),
                    "bos_up_internal": structure.get("bos_up_now"),
                    "bos_down_internal": structure.get("bos_down_now"),
                    "choch_like_internal": structure.get("choch_like_near_signal"),
                    "supporting_blocks": ",".join(summary["supporting_blocks"]),
                    "conflict_blocks": ",".join(summary["conflict_blocks"]),
                }
            )


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# V2A Structure Layer 2026-05-14",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: наложить первый структурный слой паспортов на ручной эталон `SOLUSDT 1m 2026-05-14 M01..M19`.",
        "",
        "Это визуальный overlay. Это не scorer, не target-lock, не Optuna и не ML-export.",
        "",
        "## Что наложено",
        "",
        "1. `B014 LEVEL/RANGE/CHANNEL`: ближайшая поддержка/сопротивление, позиция в диапазоне 240 баров, локальный канал.",
        "2. `B015 FIBONACCI_GRID`: сетка по последней подтвержденной чередующейся pivot-ноге, не по zoom min/max.",
        "3. `B017 BREAKOUT_RETEST`: память последнего пробоя и ретест рядом с signal.",
        "4. `B018 MARKET_STRUCTURE`: internal/external BOS и CHOCH-like по подтвержденным swing-точкам.",
        "",
        "## Граница no-lookahead",
        "",
        "- Все расчеты заканчиваются на закрытой signal-свече.",
        "- Pivot считается доступным только после `PIVOT_RIGHT` закрытых свечей.",
        "- Entry open и цена `+5 bps` показаны только как execution/control, не как feature выбора.",
        "- EMA, scorer, TP/SL, MFE/MAE, Optuna и ML здесь не используются.",
        "",
        "## Артефакты",
        "",
    ]
    for key, value in payload["artifacts"].items():
        if isinstance(value, list):
            for item in value:
                lines.append(f"- `{item}`")
        else:
            lines.append(f"- `{value}`")
    lines.extend(
        [
            "",
            "## Короткий аудит",
            "",
            f"- Входов в эталоне: `{payload['record_count']}`.",
            "- `support/conflict/silent` в CSV означает только визуальную поддержку блока, а не разрешение сделки.",
            "- Если картинка перегружена, следующий фикс: вынести Fibo/BOS/retest в отдельные страницы, оставив на full-day только manual entries и strategy squares.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(day: str, out_dir: Path) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    df = _add_closed_bar_features(_load_ohlcv(_source_csv(root, day)))
    targets = _load_targets(root, day)
    pivots_3 = _raw_pivots(df, left=3, right=3)
    pivots_10_raw = _raw_pivots(df, left=10, right=10)
    zigzag_10 = _zigzag_pivots(pivots_10_raw, deviation_pct=0.30)
    pivots_internal = _zigzag_pivots(pivots_3, deviation_pct=0.15)
    pivots_external = zigzag_10

    records = [
        _analysis_for_target(
            df,
            target,
            pivots_3=pivots_3,
            pivots_internal=pivots_internal,
            pivots_external=pivots_external,
            zigzag_10=zigzag_10,
        )
        for target in targets
    ]

    day_tag = day.replace("-", "")
    full_day_path = out_dir / f"V2A_STRUCTURE_FULL_DAY_{day_tag}.png"
    zoom_page_01_path = out_dir / f"V2A_STRUCTURE_ZOOM_PAGE_01_{day_tag}.png"
    zoom_page_02_path = out_dir / f"V2A_STRUCTURE_ZOOM_PAGE_02_{day_tag}.png"
    json_path = out_dir / f"V2A_STRUCTURE_OVERLAY_{day_tag}.json"
    csv_path = out_dir / f"V2A_STRUCTURE_OVERLAY_{day_tag}.csv"
    report_path = out_dir / f"V2A_STRUCTURE_OVERLAY_{day_tag}_RU.md"

    _render_full_day(df, records, day=day, out_path=full_day_path)
    _render_zoom_page(df, records[:10], pivots_3=pivots_3, page=1, day=day, out_path=zoom_page_01_path)
    _render_zoom_page(df, records[10:], pivots_3=pivots_3, page=2, day=day, out_path=zoom_page_02_path)

    artifacts = {
        "full_day_png": _rel(root, full_day_path),
        "zoom_png": [_rel(root, zoom_page_01_path), _rel(root, zoom_page_02_path)],
        "json": _rel(root, json_path),
        "csv": _rel(root, csv_path),
        "report_ru": _rel(root, report_path),
    }
    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "rail_point": RAIL_POINT,
        "day_utc": day,
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "record_count": len(records),
        "contracts": {
            "visual_only": True,
            "no_scorer": True,
            "no_target_lock": True,
            "no_optuna": True,
            "no_ml_export": True,
            "entry_price_role": "execution_control_only_not_selection_feature",
            "feature_cutoff": "closed_signal_candle",
            "pivot_confirmation": "pivot_right_must_be_closed_before_signal",
        },
        "passport_blocks": {
            "B014": ["F035_SUPPORTDIST_ALLOW", "F036_RESDIST_ALLOW", "F037_LEVELSTRENGTH_ALLOW", "F038_RANGEPOSE_ALLOW", "F039_CHANNELPOS_ALLOW"],
            "B015": ["F040_FIB0382DIST_ALLOW", "F041_FIB0618DIST_ALLOW"],
            "B017": ["F045_BREAKOUT_ALLOW", "F046_FALSEBREAK_ALLOW", "F047_RETEST_ALLOW", "F048_SWINGHIGHBREAK_ALLOW", "F049_SWINGLOWBREAK_ALLOW"],
            "B018": ["F050_BOSUP_ALLOW", "F051_BOSDOWN_ALLOW", "F052_CHOCH_ALLOW"],
        },
        "records": records,
        "artifacts": artifacts,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_csv(csv_path, records)
    _write_report(report_path, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Render V2A structure passport overlay for fresh target-led manual entries.")
    parser.add_argument("--day", default="2026-05-14", help="UTC day. First pass is 2026-05-14.")
    parser.add_argument(
        "--out-dir",
        default="reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2a",
        help="Output directory.",
    )
    args = parser.parse_args()
    payload = run(args.day, Path(args.out_dir))
    print(json.dumps({"status": payload["status"], "artifacts": payload["artifacts"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
