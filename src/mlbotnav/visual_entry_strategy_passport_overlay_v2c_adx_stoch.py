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


STATUS = "V2C_ADX_STOCH_LAYER_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA"
RAIL_POINT = "V2C_ADX_STOCH_LAYER"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _add_adx_stoch(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    high = out["high"].astype(float)
    low = out["low"].astype(float)
    close = out["close"].astype(float)

    prev_close = close.shift(1)
    tr = pd.concat([(high - low).abs(), (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=out.index)
    minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=out.index)

    atr14 = tr.ewm(alpha=1.0 / 14.0, adjust=False, min_periods=14).mean().replace(0, np.nan)
    plus_di14 = 100.0 * plus_dm.ewm(alpha=1.0 / 14.0, adjust=False, min_periods=14).mean() / atr14
    minus_di14 = 100.0 * minus_dm.ewm(alpha=1.0 / 14.0, adjust=False, min_periods=14).mean() / atr14
    dx14 = (100.0 * (plus_di14 - minus_di14).abs() / (plus_di14 + minus_di14).replace(0, np.nan)).replace(
        [np.inf, -np.inf],
        np.nan,
    )
    out["adx14"] = dx14.ewm(alpha=1.0 / 14.0, adjust=False, min_periods=14).mean()
    out["plus_di14"] = plus_di14
    out["minus_di14"] = minus_di14

    ll14 = low.rolling(14).min()
    hh14 = high.rolling(14).max()
    out["stoch_k14"] = 100.0 * (close - ll14) / (hh14 - ll14).replace(0, np.nan)
    out["stoch_d14"] = out["stoch_k14"].rolling(3).mean()
    out["stoch_cross_up"] = (out["stoch_k14"].shift(1) <= out["stoch_d14"].shift(1)) & (out["stoch_k14"] >= out["stoch_d14"])
    out["stoch_cross_down"] = (out["stoch_k14"].shift(1) >= out["stoch_d14"].shift(1)) & (out["stoch_k14"] <= out["stoch_d14"])
    return out


def _state_counts(records: list[dict[str, Any]], block: str, state: str) -> int:
    return sum(1 for item in records if item[block]["visual_state"] == state)


def _analysis_for_target(df: pd.DataFrame, target: dict[str, Any]) -> dict[str, Any]:
    signal_idx = _row_index_at_time(df, str(target["signal_time_utc"]))
    entry_idx = _row_index_at_time(df, str(target["entry_time_utc"]))
    row = df.iloc[signal_idx]

    adx = _safe_float(row.get("adx14"))
    plus_di = _safe_float(row.get("plus_di14"))
    minus_di = _safe_float(row.get("minus_di14"))
    stoch_k = _safe_float(row.get("stoch_k14"))
    stoch_d = _safe_float(row.get("stoch_d14"))
    cross_up = bool(row.get("stoch_cross_up"))
    cross_down = bool(row.get("stoch_cross_down"))

    adx_support = bool(adx >= 18.0)
    adx_conflict = bool(adx < 12.0)
    stoch_low = bool(stoch_k <= 35.0 or stoch_d <= 35.0)
    stoch_reclaim = bool(cross_up or (stoch_k > stoch_d and stoch_k <= 55.0))
    stoch_hot_conflict = bool(stoch_k >= 80.0 and stoch_d >= 75.0 and not cross_up)
    stoch_support = bool(stoch_low or stoch_reclaim)

    supporting_blocks = []
    conflict_blocks = []
    if adx_support:
        supporting_blocks.append("B008_ADX14")
    elif adx_conflict:
        conflict_blocks.append("B008_ADX14")
    if stoch_support:
        supporting_blocks.append("B009_STOCH14")
    elif stoch_hot_conflict or cross_down:
        conflict_blocks.append("B009_STOCH14")

    entry_row = df.iloc[entry_idx]
    entry_open = _safe_float(entry_row.get("open"))
    return {
        "target_id": str(target["target_id"]),
        "target_type": str(target.get("target_type") or "UNKNOWN"),
        "signal_time_utc": str(target["signal_time_utc"]),
        "entry_time_utc": str(target["entry_time_utc"]),
        "entry_open_price": entry_open,
        "entry_price_plus_5bps": entry_open * (1.0 + SLIPPAGE_BPS / 10000.0),
        "signal_close": _safe_float(row.get("close")),
        "B008_adx14": {
            "adx14": adx,
            "plus_di14": plus_di,
            "minus_di14": minus_di,
            "visual_state": "support" if adx_support else ("conflict" if adx_conflict else "silent"),
            "note": "strength_only_not_direction",
        },
        "B009_stoch14": {
            "stoch_k14": stoch_k,
            "stoch_d14": stoch_d,
            "cross_up": cross_up,
            "cross_down": cross_down,
            "visual_state": "support" if stoch_support else ("conflict" if stoch_hot_conflict or cross_down else "silent"),
            "note": "low_or_reclaim_visual_evidence_only",
        },
        "V2C_visual_summary": {
            "supporting_blocks": supporting_blocks,
            "conflict_blocks": conflict_blocks,
            "visual_only_not_allow_signal": True,
        },
    }


def _draw_target(ax: plt.Axes, item: dict[str, Any], *, show_price: bool) -> None:
    entry = pd.Timestamp(item["entry_time_utc"]).tz_convert("UTC").tz_convert(None)
    y = float(item["entry_open_price"])
    ax.axvline(entry.to_pydatetime(), color="#00e676", linewidth=1.6, alpha=0.92)
    ax.scatter([entry.to_pydatetime()], [y], marker="^", s=68, color="#00e676", edgecolor="white", linewidth=0.6, zorder=7)
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
    grid = fig.add_gridspec(4, 1, height_ratios=[4.6, 1.1, 1.1, 1.0], hspace=0.08)
    ax_price = fig.add_subplot(grid[0, 0])
    ax_adx = fig.add_subplot(grid[1, 0], sharex=ax_price)
    ax_stoch = fig.add_subplot(grid[2, 0], sharex=ax_price)
    ax_vol = fig.add_subplot(grid[3, 0], sharex=ax_price)
    for ax in [ax_price, ax_adx, ax_stoch, ax_vol]:
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
    ax_adx.plot(x, df["adx14"], color="#ffcc80", linewidth=0.8, label="ADX14")
    ax_adx.plot(x, df["plus_di14"], color="#26a69a", linewidth=0.55, alpha=0.65, label="+DI")
    ax_adx.plot(x, df["minus_di14"], color="#ef5350", linewidth=0.55, alpha=0.65, label="-DI")
    ax_adx.axhline(18, color="#00e676", linewidth=0.75, alpha=0.55)
    ax_adx.axhline(25, color="#ffcc80", linewidth=0.65, alpha=0.45)
    ax_adx.set_ylabel("ADX", color="white")
    ax_adx.legend(loc="upper left", fontsize=7, frameon=True, facecolor="#101418", edgecolor="#455a64")

    ax_stoch.plot(x, df["stoch_k14"], color="#4fc3f7", linewidth=0.75, label="%K")
    ax_stoch.plot(x, df["stoch_d14"], color="#ba68c8", linewidth=0.75, label="%D")
    for level, color in [(20, "#00e676"), (50, "#cfd8dc"), (80, "#ff5252")]:
        ax_stoch.axhline(level, color=color, linewidth=0.65, alpha=0.45)
    ax_stoch.set_ylim(0, 100)
    ax_stoch.set_ylabel("Stoch", color="white")
    ax_stoch.legend(loc="upper left", fontsize=7, frameon=True, facecolor="#101418", edgecolor="#455a64")

    colors = np.where(df["close"] >= df["open"], "#26a69a", "#ef5350")
    ax_vol.bar(x, df["volume"], width=_bar_width_days(TIMEFRAME), color=colors, alpha=0.42)
    ax_vol.set_ylabel("Volume", color="white")
    day_start = pd.Timestamp(f"{day}T00:00:00")
    day_end = day_start + pd.Timedelta(days=1)
    ax_price.set_xlim(day_start.to_pydatetime(), day_end.to_pydatetime())
    ax_vol.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 3)))
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax_price.set_title(
        f"{SYMBOL} {TIMEFRAME} {day} | V2C ADX/STOCH PASSPORT OVERLAY | B008/B009 | NO ML/OPTUNA",
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
    fig = plt.figure(figsize=(24, max(8.0 * rows, 8.0)), facecolor="#101418")
    grid = fig.add_gridspec(rows * 3, cols, height_ratios=[4.4, 1.15, 1.15] * rows, hspace=0.18, wspace=0.10)
    for n, item in enumerate(records):
        row = n // cols
        col = n % cols
        ax_price = fig.add_subplot(grid[row * 3, col])
        ax_adx = fig.add_subplot(grid[row * 3 + 1, col], sharex=ax_price)
        ax_stoch = fig.add_subplot(grid[row * 3 + 2, col], sharex=ax_price)
        for ax in [ax_price, ax_adx, ax_stoch]:
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

        adx = item["B008_adx14"]
        stoch = item["B009_stoch14"]
        support = "/".join(block.split("_", 1)[0] for block in item["V2C_visual_summary"]["supporting_blocks"]) or "none"
        conflict = "/".join(block.split("_", 1)[0] for block in item["V2C_visual_summary"]["conflict_blocks"]) or "none"
        ax_price.set_title(
            f"{item['target_id']} {item['target_type']} | signal {_fmt_min(item['signal_time_utc'])} -> entry {_fmt_min(item['entry_time_utc'])} "
            f"| ADX {adx['adx14']:.1f} +DI {adx['plus_di14']:.1f}/-DI {adx['minus_di14']:.1f} "
            f"| K/D {stoch['stoch_k14']:.1f}/{stoch['stoch_d14']:.1f} | support={support} conflict={conflict}",
            color="white",
            fontsize=7.8,
        )
        ax_price.set_ylabel("Price", color="white")

        ax_adx.plot(x, win["adx14"], color="#ffcc80", linewidth=0.8)
        ax_adx.plot(x, win["plus_di14"], color="#26a69a", linewidth=0.55, alpha=0.65)
        ax_adx.plot(x, win["minus_di14"], color="#ef5350", linewidth=0.55, alpha=0.65)
        ax_adx.axhline(18, color="#00e676", linewidth=0.65, alpha=0.48)
        ax_adx.axhline(25, color="#ffcc80", linewidth=0.55, alpha=0.40)
        ax_adx.set_ylabel("ADX", color="white")

        ax_stoch.plot(x, win["stoch_k14"], color="#4fc3f7", linewidth=0.75)
        ax_stoch.plot(x, win["stoch_d14"], color="#ba68c8", linewidth=0.75)
        for level, color in [(20, "#00e676"), (50, "#cfd8dc"), (80, "#ff5252")]:
            ax_stoch.axhline(level, color=color, linewidth=0.55, alpha=0.42)
        ax_stoch.set_ylim(0, 100)
        ax_stoch.set_ylabel("K/D", color="white")
        ax_stoch.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    fig.suptitle(
        f"{SYMBOL} {TIMEFRAME} {day} | V2C ADX/STOCH zoom page {page:02d} | visual only",
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
        "adx14",
        "plus_di14",
        "minus_di14",
        "adx_visual_state",
        "stoch_k14",
        "stoch_d14",
        "stoch_cross_up",
        "stoch_cross_down",
        "stoch_visual_state",
        "supporting_blocks",
        "conflict_blocks",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for item in records:
            adx = item["B008_adx14"]
            stoch = item["B009_stoch14"]
            summary = item["V2C_visual_summary"]
            writer.writerow(
                {
                    "target_id": item["target_id"],
                    "target_type": item["target_type"],
                    "signal_time_utc": item["signal_time_utc"],
                    "entry_time_utc": item["entry_time_utc"],
                    "entry_open_price": item["entry_open_price"],
                    "entry_price_plus_5bps": item["entry_price_plus_5bps"],
                    "signal_close": item["signal_close"],
                    "adx14": adx["adx14"],
                    "plus_di14": adx["plus_di14"],
                    "minus_di14": adx["minus_di14"],
                    "adx_visual_state": adx["visual_state"],
                    "stoch_k14": stoch["stoch_k14"],
                    "stoch_d14": stoch["stoch_d14"],
                    "stoch_cross_up": stoch["cross_up"],
                    "stoch_cross_down": stoch["cross_down"],
                    "stoch_visual_state": stoch["visual_state"],
                    "supporting_blocks": ",".join(summary["supporting_blocks"]),
                    "conflict_blocks": ",".join(summary["conflict_blocks"]),
                }
            )


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    rows = payload["records"]
    lines = [
        "# V2C ADX/Stochastic Layer 2026-05-14",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: по пользовательской правке не повторять RSI/MACD/EMA, а наложить `B008 ADX14` и `B009 Stochastic 14 K/D` на ручной эталон `SOLUSDT 1m 2026-05-14 M01..M19`.",
        "",
        "Это visual evidence layer. Это не scorer, не target-lock, не Optuna и не ML-export.",
        "",
        "## Support count",
        "",
        f"- `B008_ADX14`: support `{_state_counts(rows, 'B008_adx14', 'support')}/{len(rows)}`, conflict `{_state_counts(rows, 'B008_adx14', 'conflict')}/{len(rows)}`.",
        f"- `B009_STOCH14`: support `{_state_counts(rows, 'B009_stoch14', 'support')}/{len(rows)}`, conflict `{_state_counts(rows, 'B009_stoch14', 'conflict')}/{len(rows)}`.",
        "",
        "## Граница no-lookahead",
        "",
        "- Все расчеты заканчиваются на закрытой signal-свече.",
        "- Entry open и цена `+5 bps` показаны только как execution/control, не как feature выбора.",
        "- ADX показывает силу движения, но не направление сделки.",
        "- Stochastic показан как low/reclaim/cross evidence, не как готовый сигнал.",
        "",
        "## Артефакты",
        "",
    ]
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
            "После пользовательского visual review по этому слою идти в `V2D_PATTERN_LAYER` на 14 мая: `B019-B024`. `B025` не брать active без отдельного решения.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(day: str, out_dir: Path) -> dict[str, Any]:
    if day != "2026-05-14":
        raise ValueError("V2C ADX/Stoch current pass is fixed to 2026-05-14 before moving to the second reference day.")
    root = Path(__file__).resolve().parents[2]
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    df = _add_adx_stoch(_load_ohlcv(_source_csv(root, day)))
    targets = _load_targets(root, day)
    records = [_analysis_for_target(df, target) for target in targets]

    day_tag = day.replace("-", "")
    full_day_path = out_dir / f"V2C_ADX_STOCH_FULL_DAY_{day_tag}.png"
    zoom_paths = [out_dir / f"V2C_ADX_STOCH_ZOOM_PAGE_{page:02d}_{day_tag}.png" for page in range(1, 5)]
    json_path = out_dir / f"V2C_ADX_STOCH_OVERLAY_{day_tag}.json"
    csv_path = out_dir / f"V2C_ADX_STOCH_OVERLAY_{day_tag}.csv"
    report_path = out_dir / f"V2C_ADX_STOCH_OVERLAY_{day_tag}_RU.md"

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
        },
        "passport_blocks": {
            "B008": ["F016_ADX14_ALLOW"],
            "B009": ["F017_F018_STOCH14_ALLOW"],
        },
        "records": records,
        "artifacts": artifacts,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_csv(csv_path, records)
    _write_report(report_path, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Render V2C ADX/Stochastic passport overlay for fresh target-led manual entries.")
    parser.add_argument("--day", default="2026-05-14", help="UTC day. Current V2C ADX/Stoch pass is fixed to 2026-05-14.")
    parser.add_argument(
        "--out-dir",
        default="reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2c_adx_stoch",
        help="Output directory.",
    )
    args = parser.parse_args()
    payload = run(args.day, Path(args.out_dir))
    print(json.dumps({"status": payload["status"], "artifacts": payload["artifacts"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
