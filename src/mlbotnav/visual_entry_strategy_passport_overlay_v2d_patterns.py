from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from mlbotnav.visual_entry_low_anchor_suggester import _bar_width_days, _draw_candles, _load_ohlcv, _style_axis
from mlbotnav.visual_entry_strategy_passport_overlay_v2a import (
    SLIPPAGE_BPS,
    SYMBOL,
    TIMEFRAME,
    _fmt_min,
    _load_targets,
    _rel,
    _row_index_at_time,
    _safe_float,
    _source_csv,
)


STATUS = "V2D_PATTERN_LAYER_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA"
RAIL_POINT = "V2D_PATTERN_LAYER"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period, min_periods=period).mean()
    avg_loss = loss.rolling(period, min_periods=period).mean().replace(0, np.nan)
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def _bars_since(mask: pd.Series, cap: int = 99) -> pd.Series:
    last = np.full(len(mask), np.nan, dtype=float)
    last_idx = -10**9
    for i, value in enumerate(mask.fillna(False).to_numpy(dtype=bool)):
        if value:
            last_idx = i
        age = i - last_idx
        if age <= cap:
            last[i] = float(age)
    return pd.Series(last, index=mask.index)


def _confirmed_pivot_lows(df: pd.DataFrame, *, left: int = 3, right: int = 3) -> pd.Series:
    low = df["low"].astype(float)
    out = pd.Series(False, index=df.index)
    for idx in range(left, len(df) - right):
        center = low.iloc[idx]
        if center <= float(low.iloc[idx - left : idx].min()) and center < float(low.iloc[idx + 1 : idx + right + 1].min()):
            out.iloc[idx] = True
    # A pivot at idx is only usable after right bars have closed.
    return out.shift(right).fillna(False).astype(bool)


def _add_pattern_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    open_ = out["open"].astype(float)
    high = out["high"].astype(float)
    low = out["low"].astype(float)
    close = out["close"].astype(float)
    volume = out["volume"].astype(float)

    body = (close - open_).abs()
    rng = (high - low).replace(0, np.nan)
    upper_wick = high - pd.concat([open_, close], axis=1).max(axis=1)
    lower_wick = pd.concat([open_, close], axis=1).min(axis=1) - low
    body_low = pd.concat([open_, close], axis=1).min(axis=1)
    body_high = pd.concat([open_, close], axis=1).max(axis=1)
    prev_body_low = body_low.shift(1)
    prev_body_high = body_high.shift(1)
    prev_open = open_.shift(1)
    prev_close = close.shift(1)

    out["doji_flag"] = ((body / rng) <= 0.12).fillna(False)
    out["inside_bar_flag"] = ((high <= high.shift(1)) & (low >= low.shift(1))).fillna(False)
    out["pin_bar_bull_flag"] = ((lower_wick >= body * 1.8) & ((lower_wick / rng) >= 0.45) & ((upper_wick / rng) <= 0.35)).fillna(False)
    out["pin_bar_bear_flag"] = ((upper_wick >= body * 1.8) & ((upper_wick / rng) >= 0.45) & ((lower_wick / rng) <= 0.35)).fillna(False)
    out["hammer_flag"] = ((lower_wick >= body * 2.0) & ((upper_wick / rng) <= 0.30) & ((body_high - low) / rng >= 0.55)).fillna(False)
    out["shooting_star_flag"] = ((upper_wick >= body * 2.0) & ((lower_wick / rng) <= 0.30)).fillna(False)
    out["engulf_bull_flag"] = (
        (prev_close < prev_open)
        & (close > open_)
        & (body_low <= prev_body_low)
        & (body_high >= prev_body_high)
    ).fillna(False)
    out["engulf_bear_flag"] = (
        (prev_close > prev_open)
        & (close < open_)
        & (body_low <= prev_body_low)
        & (body_high >= prev_body_high)
    ).fillna(False)
    out["bull_candle_pattern"] = (
        out["pin_bar_bull_flag"] | out["hammer_flag"] | out["engulf_bull_flag"] | out["doji_flag"] | out["inside_bar_flag"]
    )
    out["bear_candle_pattern"] = out["pin_bar_bear_flag"] | out["shooting_star_flag"] | out["engulf_bear_flag"]

    out["rsi14"] = _rsi(close)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    out["macd_hist"] = (ema12 - ema26) - (ema12 - ema26).ewm(span=9, adjust=False).mean()
    direction = np.where(close >= open_, volume, -volume)
    out["obv"] = pd.Series(direction, index=out.index).cumsum()

    pivot_low_usable = _confirmed_pivot_lows(out)
    out["pivot_low_usable"] = pivot_low_usable
    rsi_bull = np.zeros(len(out), dtype=bool)
    macd_bull = np.zeros(len(out), dtype=bool)
    obv_bull = np.zeros(len(out), dtype=bool)
    pivot_indices: list[int] = []
    for idx, usable in enumerate(pivot_low_usable.to_numpy(dtype=bool)):
        if usable:
            pivot_indices.append(idx)
        recent = [p for p in pivot_indices if p <= idx]
        if len(recent) < 2:
            continue
        p1, p2 = recent[-2], recent[-1]
        if idx - p2 > 18 or p2 - p1 > 80:
            continue
        price_lower = low.iloc[p2] <= low.iloc[p1] * 1.001
        if price_lower and out["rsi14"].iloc[p2] > out["rsi14"].iloc[p1] + 1.0:
            rsi_bull[idx] = True
        if price_lower and out["macd_hist"].iloc[p2] > out["macd_hist"].iloc[p1]:
            macd_bull[idx] = True
        if price_lower and out["obv"].iloc[p2] > out["obv"].iloc[p1]:
            obv_bull[idx] = True
    out["rsi_bull_div_flag"] = pd.Series(rsi_bull, index=out.index)
    out["macd_bull_div_flag"] = pd.Series(macd_bull, index=out.index)
    out["obv_bull_div_flag"] = pd.Series(obv_bull, index=out.index)
    out["bull_divergence_pattern"] = out["rsi_bull_div_flag"] | out["macd_bull_div_flag"] | out["obv_bull_div_flag"]

    range_low = low.shift(1).rolling(60, min_periods=20).min()
    range_high = high.shift(1).rolling(60, min_periods=20).max()
    range_width = (range_high - range_low).replace(0, np.nan)
    range_pos = (close.shift(1) - range_low) / range_width
    out["range_pos60_prior"] = range_pos
    out["near_range_low"] = (range_pos <= 0.25).fillna(False)
    out["range_flag"] = (range_width / close.shift(1).replace(0, np.nan) <= 0.018).fillna(False)
    out["double_bottom_like"] = (out["near_range_low"] & (low <= range_low * 1.003) & (close > open_)).fillna(False)
    high_slope = high.shift(1).rolling(8).mean().diff(8) / close.replace(0, np.nan)
    low_slope = low.shift(1).rolling(8).mean().diff(8) / close.replace(0, np.nan)
    out["wedge_falling_like"] = ((high_slope < 0) & (low_slope < 0) & (low_slope <= high_slope)).fillna(False)
    out["chart_long_pattern"] = out["double_bottom_like"] | out["range_flag"] | out["wedge_falling_like"]

    out["volume_ma20_prior"] = volume.rolling(20, min_periods=1).mean().shift(1)
    out["volume_ratio20"] = volume / out["volume_ma20_prior"].replace(0, np.nan)
    out["level_confirm_long"] = (out["near_range_low"] | (low <= range_low * 1.003)).fillna(False)
    out["volume_confirm"] = (out["volume_ratio20"] >= 1.20).fillna(False)
    out["pattern_confirm"] = out["level_confirm_long"] | out["volume_confirm"]

    out["pattern_strength"] = (
        out["bull_candle_pattern"].astype(int)
        + out["bull_divergence_pattern"].astype(int)
        + out["chart_long_pattern"].astype(int)
        + out["pattern_confirm"].astype(int)
    )
    out["pattern_age_bars"] = _bars_since(out["bull_candle_pattern"] | out["bull_divergence_pattern"] | out["chart_long_pattern"], cap=40)
    out["pattern_long_composite"] = (
        ((out["bull_candle_pattern"] | out["bull_divergence_pattern"] | out["chart_long_pattern"]) & out["pattern_confirm"])
        | (out["pattern_strength"] >= 3)
    )
    return out


def _recent_flags(df: pd.DataFrame, idx: int, columns: list[str], lookback: int = 3) -> dict[str, bool]:
    start = max(0, idx - lookback + 1)
    win = df.iloc[start : idx + 1]
    return {col: bool(win[col].fillna(False).astype(bool).any()) for col in columns}


def _state_counts(records: list[dict[str, Any]], block: str, state: str) -> int:
    return sum(1 for item in records if item[block]["visual_state"] == state)


def _analysis_for_target(df: pd.DataFrame, target: dict[str, Any]) -> dict[str, Any]:
    signal_idx = _row_index_at_time(df, str(target["signal_time_utc"]))
    entry_idx = _row_index_at_time(df, str(target["entry_time_utc"]))
    row = df.iloc[signal_idx]
    entry_row = df.iloc[entry_idx]

    candle_flags = _recent_flags(
        df,
        signal_idx,
        ["pin_bar_bull_flag", "hammer_flag", "engulf_bull_flag", "doji_flag", "inside_bar_flag", "pin_bar_bear_flag", "shooting_star_flag", "engulf_bear_flag"],
        lookback=3,
    )
    div_flags = _recent_flags(df, signal_idx, ["rsi_bull_div_flag", "macd_bull_div_flag", "obv_bull_div_flag"], lookback=8)
    chart_flags = _recent_flags(df, signal_idx, ["double_bottom_like", "range_flag", "wedge_falling_like"], lookback=8)
    confirm_flags = _recent_flags(df, signal_idx, ["volume_confirm", "level_confirm_long"], lookback=3)

    candle_support = any(candle_flags[key] for key in ["pin_bar_bull_flag", "hammer_flag", "engulf_bull_flag", "doji_flag", "inside_bar_flag"])
    candle_conflict = any(candle_flags[key] for key in ["pin_bar_bear_flag", "shooting_star_flag", "engulf_bear_flag"])
    div_support = any(div_flags.values())
    quality_support = bool(_safe_float(row.get("pattern_strength")) >= 2 or _safe_float(row.get("pattern_age_bars")) <= 5)
    chart_support = any(chart_flags.values())
    confirm_support = any(confirm_flags.values())
    composite_support = bool(_safe_float(row.get("pattern_strength")) >= 3 or bool(row.get("pattern_long_composite")))

    blocks = {
        "B019_candle_patterns": ("support" if candle_support else ("conflict" if candle_conflict else "silent")),
        "B020_divergence_patterns": ("support" if div_support else "silent"),
        "B021_pattern_quality": ("support" if quality_support else "silent"),
        "B022_chart_patterns": ("support" if chart_support else "silent"),
        "B023_pattern_confirmation": ("support" if confirm_support else "silent"),
        "B024_pattern_composite_entry": ("support" if composite_support else "silent"),
    }
    supporting_blocks = [
        name.upper()
        for name, state in blocks.items()
        if state == "support"
    ]
    conflict_blocks = [
        name.upper()
        for name, state in blocks.items()
        if state == "conflict"
    ]
    entry_open = _safe_float(entry_row.get("open"))
    return {
        "target_id": str(target["target_id"]),
        "target_type": str(target.get("target_type") or "UNKNOWN"),
        "signal_time_utc": str(target["signal_time_utc"]),
        "entry_time_utc": str(target["entry_time_utc"]),
        "entry_open_price": entry_open,
        "entry_price_plus_5bps": entry_open * (1.0 + SLIPPAGE_BPS / 10000.0),
        "signal_close": _safe_float(row.get("close")),
        "B019_candle_patterns": {
            "visual_state": blocks["B019_candle_patterns"],
            "bull_flags": [key for key, value in candle_flags.items() if value and key not in {"pin_bar_bear_flag", "shooting_star_flag", "engulf_bear_flag"}],
            "bear_flags": [key for key, value in candle_flags.items() if value and key in {"pin_bar_bear_flag", "shooting_star_flag", "engulf_bear_flag"}],
        },
        "B020_divergence_patterns": {
            "visual_state": blocks["B020_divergence_patterns"],
            "bull_flags": [key for key, value in div_flags.items() if value],
        },
        "B021_pattern_quality": {
            "visual_state": blocks["B021_pattern_quality"],
            "pattern_strength": _safe_float(row.get("pattern_strength")),
            "pattern_age_bars": _safe_float(row.get("pattern_age_bars")),
        },
        "B022_chart_patterns": {
            "visual_state": blocks["B022_chart_patterns"],
            "bull_flags": [key for key, value in chart_flags.items() if value],
            "range_pos60_prior": _safe_float(row.get("range_pos60_prior")),
        },
        "B023_pattern_confirmation": {
            "visual_state": blocks["B023_pattern_confirmation"],
            "flags": [key for key, value in confirm_flags.items() if value],
            "volume_ratio20": _safe_float(row.get("volume_ratio20")),
        },
        "B024_pattern_composite_entry": {
            "visual_state": blocks["B024_pattern_composite_entry"],
            "pattern_long_composite": bool(row.get("pattern_long_composite")),
        },
        "V2D_visual_summary": {
            "supporting_blocks": supporting_blocks,
            "conflict_blocks": conflict_blocks,
            "visual_only_not_allow_signal": True,
        },
    }


def _draw_target(ax: plt.Axes, item: dict[str, Any], *, show_price: bool) -> None:
    entry = pd.Timestamp(item["entry_time_utc"]).tz_convert("UTC").tz_convert(None)
    y = float(item["entry_open_price"])
    ax.axvline(entry.to_pydatetime(), color="#00e676", linewidth=1.55, alpha=0.92)
    ax.scatter([entry.to_pydatetime()], [y], marker="^", s=66, color="#00e676", edgecolor="white", linewidth=0.6, zorder=7)
    label = f"{item['target_id']} {entry.strftime('%H:%M')}"
    if show_price:
        label += f"\nopen {y:.4f} | +5bps {float(item['entry_price_plus_5bps']):.4f}"
    ax.annotate(
        label,
        xy=(entry.to_pydatetime(), y),
        xytext=(8, 8),
        textcoords="offset points",
        color="#00e676",
        fontsize=6.7,
        arrowprops={"arrowstyle": "->", "color": "#00e676", "lw": 0.8},
    )


def _render_full_day(df: pd.DataFrame, records: list[dict[str, Any]], *, day: str, out_path: Path) -> None:
    fig = plt.figure(figsize=(28, 14.5), facecolor="#101418")
    grid = fig.add_gridspec(4, 1, height_ratios=[4.8, 1.0, 1.0, 1.0], hspace=0.08)
    ax_price = fig.add_subplot(grid[0, 0])
    ax_strength = fig.add_subplot(grid[1, 0], sharex=ax_price)
    ax_flags = fig.add_subplot(grid[2, 0], sharex=ax_price)
    ax_vol = fig.add_subplot(grid[3, 0], sharex=ax_price)
    for ax in [ax_price, ax_strength, ax_flags, ax_vol]:
        _style_axis(ax)

    _draw_candles(ax_price, df, TIMEFRAME, linewidth=0.26)
    for item in records:
        signal = pd.Timestamp(item["signal_time_utc"]).tz_convert("UTC")
        start = signal - pd.Timedelta(minutes=42)
        end = signal + pd.Timedelta(minutes=28)
        ax_price.axvspan(start.tz_convert(None), signal.tz_convert(None), color="#1565c0", alpha=0.022, zorder=0)
        ax_price.axvspan(signal.tz_convert(None), end.tz_convert(None), color="#00e676", alpha=0.018, zorder=0)
        _draw_target(ax_price, item, show_price=False)

    x = df["open_time_utc"].dt.tz_convert(None)
    ax_strength.step(x, df["pattern_strength"], where="post", color="#ffcc80", linewidth=0.85, label="pattern strength")
    ax_strength.step(x, df["pattern_age_bars"].clip(0, 20), where="post", color="#4fc3f7", linewidth=0.65, alpha=0.70, label="age<=20")
    ax_strength.axhline(2, color="#00e676", linewidth=0.65, alpha=0.50)
    ax_strength.set_ylabel("Strength", color="white")
    ax_strength.legend(loc="upper left", fontsize=7, frameon=True, facecolor="#101418", edgecolor="#455a64")

    flag_series = {
        "candle": df["bull_candle_pattern"].astype(int),
        "div": df["bull_divergence_pattern"].astype(int) * 2,
        "chart": df["chart_long_pattern"].astype(int) * 3,
        "confirm": df["pattern_confirm"].astype(int) * 4,
        "composite": df["pattern_long_composite"].astype(int) * 5,
    }
    colors = {"candle": "#80cbc4", "div": "#ba68c8", "chart": "#4fc3f7", "confirm": "#ffcc80", "composite": "#00e676"}
    for name, series in flag_series.items():
        mask = series > 0
        ax_flags.scatter(x[mask], series[mask], s=5, color=colors[name], label=name, alpha=0.75)
    ax_flags.set_ylim(0, 6)
    ax_flags.set_ylabel("B019-B024", color="white")
    ax_flags.legend(loc="upper left", fontsize=7, ncol=5, frameon=True, facecolor="#101418", edgecolor="#455a64")

    bar_colors = np.where(df["close"] >= df["open"], "#26a69a", "#ef5350")
    ax_vol.bar(x, df["volume"], width=_bar_width_days(TIMEFRAME), color=bar_colors, alpha=0.42)
    ax_vol.set_ylabel("Volume", color="white")
    day_start = pd.Timestamp(f"{day}T00:00:00")
    day_end = day_start + pd.Timedelta(days=1)
    ax_price.set_xlim(day_start.to_pydatetime(), day_end.to_pydatetime())
    ax_vol.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 3)))
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax_price.set_title(
        f"{SYMBOL} {TIMEFRAME} {day} | V2D PATTERN PASSPORT OVERLAY | B019-B024 | NO ML/OPTUNA",
        color="white",
        fontsize=15,
    )
    ax_price.set_ylabel("Price", color="white")
    fig.autofmt_xdate()
    fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def _render_zoom_page(df: pd.DataFrame, records: list[dict[str, Any]], *, page: int, day: str, out_path: Path) -> None:
    cols = 2
    rows = int(np.ceil(len(records) / cols))
    fig = plt.figure(figsize=(24, max(7.2 * rows, 8.0)), facecolor="#101418")
    grid = fig.add_gridspec(rows * 2, cols, height_ratios=[4.4, 1.25] * rows, hspace=0.18, wspace=0.10)
    for n, item in enumerate(records):
        row = n // cols
        col = n % cols
        ax_price = fig.add_subplot(grid[row * 2, col])
        ax_flags = fig.add_subplot(grid[row * 2 + 1, col], sharex=ax_price)
        for ax in [ax_price, ax_flags]:
            _style_axis(ax)
        signal = pd.Timestamp(item["signal_time_utc"]).tz_convert("UTC")
        start = signal - pd.Timedelta(minutes=42)
        end = signal + pd.Timedelta(minutes=38)
        win = df[(df["open_time_utc"] >= start) & (df["open_time_utc"] <= end)].reset_index(drop=True)
        x = win["open_time_utc"].dt.tz_convert(None)
        _draw_candles(ax_price, win, TIMEFRAME, linewidth=0.58)
        ax_price.axvspan(start.tz_convert(None), signal.tz_convert(None), color="#1565c0", alpha=0.050, zorder=0)
        ax_price.axvspan(signal.tz_convert(None), end.tz_convert(None), color="#00e676", alpha=0.038, zorder=0)
        _draw_target(ax_price, item, show_price=True)
        ax_price.set_xlim(start.tz_convert(None).to_pydatetime(), end.tz_convert(None).to_pydatetime())

        support = "/".join(block.split("_", 1)[0] for block in item["V2D_visual_summary"]["supporting_blocks"]) or "none"
        conflict = "/".join(block.split("_", 1)[0] for block in item["V2D_visual_summary"]["conflict_blocks"]) or "none"
        ax_price.set_title(
            f"{item['target_id']} {item['target_type']} | signal {_fmt_min(item['signal_time_utc'])} -> entry {_fmt_min(item['entry_time_utc'])} "
            f"| strength {item['B021_pattern_quality']['pattern_strength']:.0f} age {item['B021_pattern_quality']['pattern_age_bars']:.0f} "
            f"| support={support} conflict={conflict}",
            color="white",
            fontsize=7.8,
        )
        ax_price.set_ylabel("Price", color="white")

        flag_series = {
            "candle": win["bull_candle_pattern"].astype(int),
            "div": win["bull_divergence_pattern"].astype(int) * 2,
            "chart": win["chart_long_pattern"].astype(int) * 3,
            "confirm": win["pattern_confirm"].astype(int) * 4,
            "composite": win["pattern_long_composite"].astype(int) * 5,
        }
        colors = {"candle": "#80cbc4", "div": "#ba68c8", "chart": "#4fc3f7", "confirm": "#ffcc80", "composite": "#00e676"}
        for name, series in flag_series.items():
            mask = series > 0
            ax_flags.scatter(x[mask], series[mask], s=9, color=colors[name], label=name, alpha=0.82)
        ax_flags.step(x, win["pattern_strength"], where="post", color="#ffcc80", linewidth=0.55, alpha=0.55)
        ax_flags.set_ylim(0, 6)
        ax_flags.set_ylabel("patterns", color="white")
        ax_flags.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    fig.suptitle(
        f"{SYMBOL} {TIMEFRAME} {day} | V2D pattern zoom page {page:02d} | visual only",
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
        "entry_open_price",
        "entry_price_plus_5bps",
        "signal_close",
        "B019_state",
        "B020_state",
        "B021_state",
        "B022_state",
        "B023_state",
        "B024_state",
        "pattern_strength",
        "pattern_age_bars",
        "supporting_blocks",
        "conflict_blocks",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for item in records:
            summary = item["V2D_visual_summary"]
            writer.writerow(
                {
                    "target_id": item["target_id"],
                    "target_type": item["target_type"],
                    "signal_time_utc": item["signal_time_utc"],
                    "entry_time_utc": item["entry_time_utc"],
                    "entry_open_price": item["entry_open_price"],
                    "entry_price_plus_5bps": item["entry_price_plus_5bps"],
                    "signal_close": item["signal_close"],
                    "B019_state": item["B019_candle_patterns"]["visual_state"],
                    "B020_state": item["B020_divergence_patterns"]["visual_state"],
                    "B021_state": item["B021_pattern_quality"]["visual_state"],
                    "B022_state": item["B022_chart_patterns"]["visual_state"],
                    "B023_state": item["B023_pattern_confirmation"]["visual_state"],
                    "B024_state": item["B024_pattern_composite_entry"]["visual_state"],
                    "pattern_strength": item["B021_pattern_quality"]["pattern_strength"],
                    "pattern_age_bars": item["B021_pattern_quality"]["pattern_age_bars"],
                    "supporting_blocks": ",".join(summary["supporting_blocks"]),
                    "conflict_blocks": ",".join(summary["conflict_blocks"]),
                }
            )


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    rows = payload["records"]
    block_keys = [
        ("B019", "B019_candle_patterns"),
        ("B020", "B020_divergence_patterns"),
        ("B021", "B021_pattern_quality"),
        ("B022", "B022_chart_patterns"),
        ("B023", "B023_pattern_confirmation"),
        ("B024", "B024_pattern_composite_entry"),
    ]
    lines = [
        "# V2D Pattern Layer 2026-05-14",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: наложить pattern-паспорта `B019-B024` на ручной эталон `SOLUSDT 1m 2026-05-14 M01..M19`.",
        "",
        "Это visual evidence layer. Это не scorer, не target-lock, не Optuna и не ML-export.",
        "",
        "## Support count",
        "",
    ]
    for label, key in block_keys:
        lines.append(
            f"- `{label}`: support `{_state_counts(rows, key, 'support')}/{len(rows)}`, conflict `{_state_counts(rows, key, 'conflict')}/{len(rows)}`."
        )
    lines.extend(
        [
            "",
            "## Граница no-lookahead",
            "",
            "- Все расчеты заканчиваются на закрытой signal-свече.",
            "- Для divergence используются только уже подтвержденные прошлые pivot low.",
            "- Entry open и цена `+5 bps` показаны только как execution/control.",
            "- `B025 Pattern trade context` здесь не используется как active layer.",
            "",
            "## Артефакты",
            "",
        ]
    )
    for value in payload["artifacts"].values():
        if isinstance(value, list):
            for item in value:
                lines.append(f"- `{item}`")
        else:
            lines.append(f"- `{value}`")
    lines.extend(
        [
            "",
            "## Следующий подпункт",
            "",
            "После пользовательского visual review по этому слою собрать `V2E_SUMMARY_MATRIX` по 14 мая: `M01..M19 -> support/conflict/silent` по слоям `V2A/V2B/V2C/V2D`.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(day: str, out_dir: Path) -> dict[str, Any]:
    if day != "2026-05-14":
        raise ValueError("V2D current pass is fixed to 2026-05-14 before moving to the second reference day.")
    root = Path(__file__).resolve().parents[2]
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    df = _add_pattern_features(_load_ohlcv(_source_csv(root, day)))
    targets = _load_targets(root, day)
    records = [_analysis_for_target(df, target) for target in targets]

    day_tag = day.replace("-", "")
    full_day_path = out_dir / f"V2D_PATTERN_FULL_DAY_{day_tag}.png"
    zoom_paths = [out_dir / f"V2D_PATTERN_ZOOM_PAGE_{page:02d}_{day_tag}.png" for page in range(1, 5)]
    json_path = out_dir / f"V2D_PATTERN_OVERLAY_{day_tag}.json"
    csv_path = out_dir / f"V2D_PATTERN_OVERLAY_{day_tag}.csv"
    report_path = out_dir / f"V2D_PATTERN_OVERLAY_{day_tag}_RU.md"

    _render_full_day(df, records, day=day, out_path=full_day_path)
    for page, start in enumerate(range(0, len(records), 5), start=1):
        _render_zoom_page(df, records[start : start + 5], page=page, day=day, out_path=zoom_paths[page - 1])

    artifacts = {
        "full_day_png": _rel(root, full_day_path),
        "zoom_png": [_rel(root, path) for path in zoom_paths],
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
            "slippage_bps": SLIPPAGE_BPS,
            "B025_pattern_trade_context_active": False,
        },
        "passport_blocks": {
            "B019": ["F053-F060 candle patterns"],
            "B020": ["F061-F066 divergence patterns"],
            "B021": ["F067-F068 pattern quality"],
            "B022": ["F069-F077 chart patterns"],
            "B023": ["F078-F079 pattern confirmation"],
            "B024": ["F080-F081 pattern composite entry"],
        },
        "records": records,
        "artifacts": artifacts,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_csv(csv_path, records)
    _write_report(report_path, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Render V2D pattern passport overlay for fresh target-led manual entries.")
    parser.add_argument("--day", default="2026-05-14", help="UTC day. Current V2D pass is fixed to 2026-05-14.")
    parser.add_argument(
        "--out-dir",
        default="reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2d_patterns",
        help="Output directory.",
    )
    args = parser.parse_args()
    payload = run(args.day, Path(args.out_dir))
    print(json.dumps({"status": payload["status"], "artifacts": payload["artifacts"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
