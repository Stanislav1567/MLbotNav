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


STATUS = "INDICATOR_HYPOTHESIS_REVIEW_V0_READY_NO_ML_NO_OPTUNA"
RAIL_POINT = "VISUAL_INDICATOR_HYPOTHESIS_REVIEW_NO_ML_NO_OPTUNA"
SLIPPAGE_BPS = 5.0


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _source_csv(root: Path, day: str) -> Path:
    return root / "data" / "core" / "bybit_ohlcv" / f"dt={day}" / "tf=1m" / "symbol=SOLUSDT" / "part-final.csv"


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def _add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    delta = out["close"].diff()
    gain = delta.clip(lower=0).rolling(14, min_periods=1).mean()
    loss = (-delta.clip(upper=0)).rolling(14, min_periods=1).mean()
    rs = gain / loss.replace(0, np.nan)
    out["rsi14"] = 100.0 - (100.0 / (1.0 + rs))

    ema12 = out["close"].ewm(span=12, adjust=False).mean()
    ema26 = out["close"].ewm(span=26, adjust=False).mean()
    out["macd"] = ema12 - ema26
    out["macd_signal"] = out["macd"].ewm(span=9, adjust=False).mean()
    out["macd_hist"] = out["macd"] - out["macd_signal"]

    out["range"] = out["high"] - out["low"]
    out["body"] = (out["close"] - out["open"]).abs()
    out["lower_wick"] = np.minimum(out["open"], out["close"]) - out["low"]
    out["upper_wick"] = out["high"] - np.maximum(out["open"], out["close"])
    out["lower_wick_to_body"] = out["lower_wick"] / out["body"].replace(0, np.nan)
    out["close_pos_candle"] = (out["close"] - out["low"]) / out["range"].replace(0, np.nan)
    out["volume_ma20_prior"] = out["volume"].rolling(20, min_periods=1).mean().shift(1)
    out["volume_ratio20"] = out["volume"] / out["volume_ma20_prior"]
    out["volume_std20_prior"] = out["volume"].rolling(20, min_periods=2).std().shift(1)
    out["volume_z20"] = (out["volume"] - out["volume_ma20_prior"]) / out["volume_std20_prior"].replace(0, np.nan)

    for window in [20, 60, 180]:
        out[f"rolling_low_{window}"] = out["low"].rolling(window, min_periods=1).min()
        out[f"rolling_high_{window}"] = out["high"].rolling(window, min_periods=1).max()
        denom = (out[f"rolling_high_{window}"] - out[f"rolling_low_{window}"]).replace(0, np.nan)
        out[f"range_pos_{window}"] = (out["close"] - out[f"rolling_low_{window}"]) / denom
        out[f"room_to_high_{window}_bps"] = (out[f"rolling_high_{window}"] - out["close"]) / out["close"] * 10000.0
        out[f"distance_from_low_{window}_bps"] = (out["close"] - out[f"rolling_low_{window}"]) / out["close"] * 10000.0
    for window in [12, 30, 60, 120]:
        out[f"ret_{window}m_pct"] = out["close"].pct_change(window) * 100.0

    out["trail_swing_low_5"] = out["low"] <= out["low"].rolling(5, min_periods=1).min()
    out["trail_swing_high_5"] = out["high"] >= out["high"].rolling(5, min_periods=1).max()
    out["bos_up_60"] = out["close"] > out["high"].rolling(60, min_periods=1).max().shift(1)
    out["bos_down_60"] = out["close"] < out["low"].rolling(60, min_periods=1).min().shift(1)
    return out


def _entry_price(entry_open: float) -> float:
    return float(entry_open) * (1.0 + SLIPPAGE_BPS / 10000.0)


def _load_day_targets(root: Path, day: str) -> list[dict[str, Any]]:
    if day == "2026-05-14":
        path = root / "reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_M01_M19.json"
        payload = _read_json(path)
        rows: list[dict[str, Any]] = []
        for item in payload["targets"]:
            execution = item.get("execution_price", {})
            rows.append(
                {
                    "target_id": str(item["target_id"]),
                    "day_utc": day,
                    "signal_time_utc": str(item["signal_time_utc"]),
                    "entry_time_utc": str(item["entry_time_utc"]),
                    "entry_price_plus_5bps": float(execution.get("entry_price_with_slippage")),
                    "review_label": "manual_gold",
                    "target_type": str(item.get("target_type") or "UNKNOWN"),
                }
            )
        return rows

    feedback = root / (
        "reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/"
        "day_20260515_compact_v0/user_feedback_v2/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.json"
    )
    transfer = root / (
        "reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/"
        "day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_20260515.json"
    )
    feedback_payload = _read_json(feedback)
    transfer_payload = _read_json(transfer)
    by_id = {str(item["candidate_id"]): item for item in transfer_payload["candidates"]}
    rows = []
    for item in feedback_payload["records"]:
        cid = str(item["candidate_id"])
        source = by_id[cid]
        rows.append(
            {
                "target_id": cid,
                "day_utc": day,
                "signal_time_utc": str(item["signal_time_utc"]),
                "entry_time_utc": str(item["entry_time_utc"]),
                "entry_price_plus_5bps": float(item["entry_price_plus_5bps"]),
                "review_label": str(item["review_label"]),
                "target_type": str(source.get("transfer_type") or "UNKNOWN"),
            }
        )
    return rows


def _row_at_time(df: pd.DataFrame, time_utc: str) -> pd.Series | None:
    ts = pd.Timestamp(time_utc).tz_convert("UTC")
    matched = df[df["open_time_utc"] == ts]
    if matched.empty:
        return None
    return matched.iloc[0]


def _indicator_votes(df: pd.DataFrame, target: dict[str, Any]) -> dict[str, Any]:
    row = _row_at_time(df, str(target["signal_time_utc"]))
    if row is None:
        return {"target_id": target["target_id"], "status": "missing_signal_row"}
    votes: list[str] = []
    cautions: list[str] = []
    if _safe_float(row.get("rsi14"), 50.0) <= 38.0:
        votes.append("RSI_COLD")
    elif _safe_float(row.get("rsi14"), 50.0) >= 58.0:
        cautions.append("RSI_NOT_LOW")
    if _safe_float(row.get("macd_hist")) > _safe_float(df.iloc[max(0, int(row.name) - 3) : int(row.name) + 1]["macd_hist"].min()):
        votes.append("MACD_HIST_RECOVERING")
    if _safe_float(row.get("volume_ratio20")) >= 1.25:
        votes.append("VOLUME_ABOVE_PRIOR20")
    if _safe_float(row.get("range_pos_60"), 1.0) <= 0.25:
        votes.append("LOW_IN_60M_RANGE")
    if _safe_float(row.get("room_to_high_60_bps")) >= 40.0:
        votes.append("ROOM_TO_HIGH")
    else:
        cautions.append("ROOM_SMALL")
    if _safe_float(row.get("lower_wick_to_body")) >= 0.55 or _safe_float(row.get("close_pos_candle")) >= 0.55:
        votes.append("WICK_OR_CLOSE_RECLAIM")
    if bool(row.get("bos_down_60")):
        cautions.append("BOS_DOWN_CONTEXT")
    if bool(row.get("bos_up_60")):
        votes.append("BOS_UP_BREAK")
    return {
        "target_id": target["target_id"],
        "day_utc": target["day_utc"],
        "review_label": target["review_label"],
        "target_type": target["target_type"],
        "signal_time_utc": target["signal_time_utc"],
        "entry_time_utc": target["entry_time_utc"],
        "entry_price_plus_5bps": target["entry_price_plus_5bps"],
        "votes": votes,
        "cautions": cautions,
        "rsi14": round(_safe_float(row.get("rsi14")), 4),
        "macd_hist": round(_safe_float(row.get("macd_hist")), 6),
        "volume_ratio20": round(_safe_float(row.get("volume_ratio20")), 4),
        "volume_z20": round(_safe_float(row.get("volume_z20")), 4),
        "range_pos_60": round(_safe_float(row.get("range_pos_60")), 4),
        "room_to_high_60_bps": round(_safe_float(row.get("room_to_high_60_bps")), 4),
        "lower_wick_to_body": round(_safe_float(row.get("lower_wick_to_body")), 4),
        "close_pos_candle": round(_safe_float(row.get("close_pos_candle")), 4),
        "bos_up_60": bool(row.get("bos_up_60")),
        "bos_down_60": bool(row.get("bos_down_60")),
    }


def _plot_volume_profile(ax: Any, df: pd.DataFrame, *, bins: int = 46, color: str = "#546e7a") -> None:
    if df.empty:
        return
    lo = float(df["low"].min())
    hi = float(df["high"].max())
    if hi <= lo:
        return
    typical = (df["high"] + df["low"] + df["close"]) / 3.0
    hist, edges = np.histogram(typical, bins=bins, range=(lo, hi), weights=df["volume"])
    if hist.max() <= 0:
        return
    x0, x1 = ax.get_xlim()
    max_width = (x1 - x0) * 0.07
    for value, left, right in zip(hist, edges[:-1], edges[1:]):
        if value <= 0:
            continue
        y = (left + right) / 2.0
        width = max_width * (float(value) / float(hist.max()))
        ax.hlines(y, x1 - width, x1, color=color, alpha=0.20, linewidth=2.2, zorder=0)


def _draw_structure(ax: Any, df: pd.DataFrame) -> None:
    stride_lows = df[df["trail_swing_low_5"]]
    stride_highs = df[df["trail_swing_high_5"]]
    ax.scatter(
        stride_lows["open_time_utc"].dt.tz_convert(None),
        stride_lows["low"],
        marker="v",
        s=10,
        color="#4dd0e1",
        alpha=0.33,
        zorder=4,
    )
    ax.scatter(
        stride_highs["open_time_utc"].dt.tz_convert(None),
        stride_highs["high"],
        marker="^",
        s=10,
        color="#ffb74d",
        alpha=0.25,
        zorder=4,
    )
    for _, row in df[df["bos_up_60"]].iloc[::8].iterrows():
        ax.text(row["open_time_utc"].tz_convert(None), row["high"], "BOS+", color="#00e676", fontsize=7, alpha=0.72)
    for _, row in df[df["bos_down_60"]].iloc[::8].iterrows():
        ax.text(row["open_time_utc"].tz_convert(None), row["low"], "BOS-", color="#ff5252", fontsize=7, alpha=0.62, va="top")


def _draw_targets(ax: Any, targets: list[dict[str, Any]], *, show_price: bool = False) -> None:
    for target in targets:
        signal = pd.Timestamp(target["signal_time_utc"]).tz_convert(None)
        entry = pd.Timestamp(target["entry_time_utc"]).tz_convert(None)
        price = float(target["entry_price_plus_5bps"])
        label = str(target["target_id"])
        if show_price:
            label = f"{label} {entry.strftime('%H:%M')} p={price:.4f}"
        review = str(target["review_label"])
        if review == "manual_gold":
            color = "#00e676"
            marker = "^"
            size = 76
        elif review == "bad_noise":
            color = "#ff1744"
            marker = "x"
            size = 90
        else:
            color = "#26c6da"
            marker = "^"
            size = 70
        ax.axvline(signal, color=color, alpha=0.16 if review == "bad_noise" else 0.22, linewidth=1.0, zorder=0)
        ax.scatter([entry], [price], marker=marker, s=size, color=color, edgecolors="white" if marker != "x" else None, linewidths=0.55 if marker != "x" else 1.9, zorder=8)
        ax.annotate(label, xy=(entry, price), xytext=(2, 8), textcoords="offset points", fontsize=8, color=color)


def _render_full_day(*, df: pd.DataFrame, targets: list[dict[str, Any]], day: str, out_path: Path) -> None:
    fig = plt.figure(figsize=(28, 16), facecolor="#101418")
    grid = fig.add_gridspec(4, 1, height_ratios=[4.8, 1.25, 1.15, 1.25], hspace=0.10)
    ax_price = fig.add_subplot(grid[0, 0])
    ax_vol = fig.add_subplot(grid[1, 0], sharex=ax_price)
    ax_rsi = fig.add_subplot(grid[2, 0], sharex=ax_price)
    ax_macd = fig.add_subplot(grid[3, 0], sharex=ax_price)
    for ax in [ax_price, ax_vol, ax_rsi, ax_macd]:
        _style_axis(ax)

    _draw_candles(ax_price, df, "1m", linewidth=0.30)
    _draw_structure(ax_price, df)
    _draw_targets(ax_price, targets)
    start = pd.Timestamp(f"{day}T00:00:00")
    end = start + pd.Timedelta(days=1)
    ax_price.set_xlim(start.to_pydatetime(), end.to_pydatetime())
    _plot_volume_profile(ax_price, df)
    ax_price.set_ylabel("Price", color="white")

    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(df["open"], df["close"])]
    ax_vol.bar(df["open_time_utc"].dt.tz_convert(None), df["volume"], width=_bar_width_days("1m"), color=colors, alpha=0.70)
    ax_vol.plot(df["open_time_utc"].dt.tz_convert(None), df["volume_ma20_prior"], color="#ffcc80", linewidth=0.8, alpha=0.85)
    ax_vol.set_ylabel("Volume", color="white")

    ax_rsi.plot(df["open_time_utc"].dt.tz_convert(None), df["rsi14"], color="#7e57c2", linewidth=0.9)
    for level, color in [(30, "#00e676"), (50, "#cfd8dc"), (70, "#ff5252")]:
        ax_rsi.axhline(level, color=color, linewidth=0.8, alpha=0.45)
    ax_rsi.set_ylim(0, 100)
    ax_rsi.set_ylabel("RSI14", color="white")

    hist_colors = ["#26a69a" if value >= 0 else "#ef5350" for value in df["macd_hist"]]
    ax_macd.bar(df["open_time_utc"].dt.tz_convert(None), df["macd_hist"], width=_bar_width_days("1m"), color=hist_colors, alpha=0.55)
    ax_macd.plot(df["open_time_utc"].dt.tz_convert(None), df["macd"], color="#4fc3f7", linewidth=0.85)
    ax_macd.plot(df["open_time_utc"].dt.tz_convert(None), df["macd_signal"], color="#ffcc80", linewidth=0.85)
    ax_macd.axhline(0, color="#cfd8dc", linewidth=0.75, alpha=0.45)
    ax_macd.set_ylabel("MACD", color="white")
    ax_macd.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 3)))
    ax_macd.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate()

    fig.suptitle(
        f"SOLUSDT 1m {day} | RSI/MACD/Volume/Density/Swing/BOS visual hypothesis | NO ML/OPTUNA",
        color="white",
        fontsize=16,
    )
    fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def _draw_fibo(ax: Any, win: pd.DataFrame, signal_time: pd.Timestamp) -> None:
    history = win[win["open_time_utc"] <= signal_time]
    if len(history) < 10:
        return
    lo = float(history["low"].min())
    hi = float(history["high"].max())
    if hi <= lo:
        return
    levels = [(0.382, "#80cbc4"), (0.5, "#ffcc80"), (0.618, "#ce93d8")]
    x0, x1 = ax.get_xlim()
    for level, color in levels:
        price = hi - (hi - lo) * level
        ax.hlines(price, x0, x1, color=color, alpha=0.45, linewidth=0.9, linestyle="--")
        ax.text(x1, price, f"F{level:.3f}", color=color, fontsize=7, va="center", ha="right")


def _render_pending_zoom(*, df: pd.DataFrame, targets: list[dict[str, Any]], day: str, out_path: Path) -> None:
    pending = [item for item in targets if item["review_label"] == "pending_user_visual_review"]
    rows = len(pending)
    if rows == 0:
        return
    fig = plt.figure(figsize=(22, max(4.8 * rows, 8)), facecolor="#101418")
    grid = fig.add_gridspec(rows * 3, 1, hspace=0.06)
    for idx, target in enumerate(pending):
        ax_price = fig.add_subplot(grid[idx * 3, 0])
        ax_rsi = fig.add_subplot(grid[idx * 3 + 1, 0], sharex=ax_price)
        ax_macd = fig.add_subplot(grid[idx * 3 + 2, 0], sharex=ax_price)
        for ax in [ax_price, ax_rsi, ax_macd]:
            _style_axis(ax)
        signal = pd.Timestamp(target["signal_time_utc"]).tz_convert("UTC")
        start = signal - pd.Timedelta(minutes=32)
        end = signal + pd.Timedelta(minutes=44)
        win = df[(df["open_time_utc"] >= start) & (df["open_time_utc"] <= end)].reset_index(drop=True)
        _draw_candles(ax_price, win, "1m", linewidth=0.62)
        _draw_structure(ax_price, win)
        _draw_targets(ax_price, [target], show_price=True)
        ax_price.set_xlim(start.tz_convert(None).to_pydatetime(), end.tz_convert(None).to_pydatetime())
        _draw_fibo(ax_price, win, signal)
        _plot_volume_profile(ax_price, win, bins=24)
        votes = _indicator_votes(df, target)
        ax_price.set_title(
            f"{target['target_id']} {target['target_type']} | entry {pd.Timestamp(target['entry_time_utc']).strftime('%H:%M')} "
            f"p+5bps {float(target['entry_price_plus_5bps']):.4f} "
            f"| votes={','.join(votes.get('votes', []))[:90]} | cautions={','.join(votes.get('cautions', []))[:60]}",
            color="white",
            fontsize=9,
        )
        colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(win["open"], win["close"])]
        price_floor = float(win["low"].min())
        price_span = float(win["high"].max()) - price_floor
        volume_height = win["volume"] / max(float(win["volume"].max()), 1.0) * price_span * 0.18
        ax_price.bar(
            win["open_time_utc"].dt.tz_convert(None),
            volume_height,
            bottom=price_floor,
            width=_bar_width_days("1m"),
            color=colors,
            alpha=0.16,
            zorder=0,
        )
        ax_rsi.plot(win["open_time_utc"].dt.tz_convert(None), win["rsi14"], color="#7e57c2", linewidth=0.9)
        for level, color in [(30, "#00e676"), (50, "#cfd8dc"), (70, "#ff5252")]:
            ax_rsi.axhline(level, color=color, linewidth=0.7, alpha=0.45)
        ax_rsi.set_ylim(0, 100)
        ax_rsi.set_ylabel("RSI", color="white")
        hist_colors = ["#26a69a" if value >= 0 else "#ef5350" for value in win["macd_hist"]]
        ax_macd.bar(win["open_time_utc"].dt.tz_convert(None), win["macd_hist"], width=_bar_width_days("1m"), color=hist_colors, alpha=0.56)
        ax_macd.plot(win["open_time_utc"].dt.tz_convert(None), win["macd"], color="#4fc3f7", linewidth=0.8)
        ax_macd.plot(win["open_time_utc"].dt.tz_convert(None), win["macd_signal"], color="#ffcc80", linewidth=0.8)
        ax_macd.axhline(0, color="#cfd8dc", linewidth=0.7, alpha=0.45)
        ax_macd.set_ylabel("MACD", color="white")
        ax_macd.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.suptitle(f"SOLUSDT 1m {day} | pending candidates indicator zoom | NO ML/OPTUNA", color="white", fontsize=15)
    fig.savefig(out_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = [
        "target_id",
        "day_utc",
        "review_label",
        "target_type",
        "signal_time_utc",
        "entry_time_utc",
        "entry_price_plus_5bps",
        "votes",
        "cautions",
        "rsi14",
        "macd_hist",
        "volume_ratio20",
        "volume_z20",
        "range_pos_60",
        "room_to_high_60_bps",
        "lower_wick_to_body",
        "close_pos_candle",
        "bos_up_60",
        "bos_down_60",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            out = dict(row)
            out["votes"] = ",".join(out.get("votes") or [])
            out["cautions"] = ",".join(out.get("cautions") or [])
            writer.writerow({col: out.get(col) for col in columns})


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Indicator Hypothesis Review V0",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: визуально наложить RSI, MACD, volume, density, swing/BOS и Fibo на дни `2026-05-14` и `2026-05-15`, чтобы понять, какие инструменты реально объясняют входы.",
        "",
        "Это не scorer, не стратегия, не ML dataset и не Optuna.",
        "",
        "## Лестница проверки",
        "",
        "1. `L0_PRICE_VOLUME`: свечи, volume, ручные входы.",
        "2. `L1_MOMENTUM`: RSI14 и MACD histogram.",
        "3. `L2_DENSITY`: volume profile / плотность цены справа на price-панели.",
        "4. `L3_STRUCTURE`: trailing swing low/high и BOS up/down по прошлым 60 барам.",
        "5. `L4_FIBO`: Fibo-зоны на zoom по прошлому окну до signal.",
        "6. `L5_DECISION`: ручной verdict, какие инструменты помогают, а какие шумят.",
        "",
        "## Граница no-lookahead",
        "",
        "- Индикаторы считаются по закрытой signal-свече и прошлому контексту.",
        "- Fibo на zoom строится по окну до signal.",
        "- Entry price остается только execution/control.",
        "- EMA не используется как active condition.",
        "- Future return, TP/SL, MFE/MAE не используются.",
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
            "## Следующий шаг",
            "",
            "Пользователь смотрит картинки и говорит, какие инструменты реально совпадают с хорошими входами и pending `T15L`, а какие дают ложную уверенность.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(out_dir: Path) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    all_records: list[dict[str, Any]] = []
    full_day_paths: list[Path] = []
    zoom_paths: list[Path] = []
    for day in ["2026-05-14", "2026-05-15"]:
        df = _add_indicators(_load_ohlcv(_source_csv(root, day)))
        targets = _load_day_targets(root, day)
        full_path = out_dir / f"INDICATOR_HYPOTHESIS_REVIEW_FULL_DAY_{day.replace('-', '')}.png"
        _render_full_day(df=df, targets=targets, day=day, out_path=full_path)
        full_day_paths.append(full_path)
        if day == "2026-05-15":
            zoom_path = out_dir / f"INDICATOR_HYPOTHESIS_REVIEW_PENDING_ZOOM_{day.replace('-', '')}.png"
            _render_pending_zoom(df=df, targets=targets, day=day, out_path=zoom_path)
            zoom_paths.append(zoom_path)
        all_records.extend(_indicator_votes(df, target) for target in targets)

    json_path = out_dir / "INDICATOR_HYPOTHESIS_REVIEW_V0_20260701.json"
    csv_path = out_dir / "INDICATOR_HYPOTHESIS_REVIEW_V0_20260701.csv"
    report_path = out_dir / "INDICATOR_HYPOTHESIS_REVIEW_V0_20260701_RU.md"
    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "rail_point": RAIL_POINT,
        "days": ["2026-05-14", "2026-05-15"],
        "record_count": len(all_records),
        "no_lookahead_boundary": {
            "indicator_features_end_at": "signal_candle_close",
            "entry_open_price_is_execution_price_only": True,
            "ema_active_condition": False,
            "forbidden_features": ["future_return", "tp_sl", "mfe_mae", "entry_candle_ohlcv_for_selection"],
            "optuna_allowed": False,
            "ml_allowed": False,
        },
        "records": all_records,
        "artifacts": {
            "json": _rel(root, json_path),
            "csv": _rel(root, csv_path),
            "report_ru": _rel(root, report_path),
            "full_day_pngs": [_rel(root, path) for path in full_day_paths],
            "pending_zoom_pngs": [_rel(root, path) for path in zoom_paths],
        },
        "optuna_allowed": False,
        "ml_allowed": False,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_csv(csv_path, all_records)
    _write_report(report_path, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Render visual indicator hypothesis review for target-led entries.")
    parser.add_argument(
        "--out-dir",
        default="reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0",
    )
    args = parser.parse_args()
    payload = run(Path(args.out_dir))
    print(
        json.dumps(
            {
                "status": payload["status"],
                "record_count": payload["record_count"],
                "artifacts": payload["artifacts"],
                "ml_allowed": payload["ml_allowed"],
                "optuna_allowed": payload["optuna_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
