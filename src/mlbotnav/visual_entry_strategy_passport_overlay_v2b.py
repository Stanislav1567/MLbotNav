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
    _fmt_ts,
    _load_targets,
    _rel,
    _row_index_at_time,
    _safe_float,
    _source_csv,
)


STATUS = "V2B_FLOW_DENSITY_LAYER_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA"
RAIL_POINT = "V2B_FLOW_DENSITY_LAYER"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _density_window_features(
    typical: np.ndarray,
    volume: np.ndarray,
    close: np.ndarray,
    idx: int,
    *,
    window: int,
    bins: int = 28,
) -> dict[str, float | None]:
    start = max(0, idx - window + 1)
    prices = typical[start : idx + 1]
    vols = volume[start : idx + 1]
    if len(prices) < 5 or float(np.nansum(vols)) <= 0:
        return {
            f"density_vpoc_{window}": None,
            f"density_vpoc_distance_{window}_pct": None,
            f"density_bin_share_{window}": None,
            f"density_cluster_share_{window}": None,
            f"density_vpoc_share_{window}": None,
        }
    lo = float(np.nanmin(prices))
    hi = float(np.nanmax(prices))
    if not np.isfinite(lo) or not np.isfinite(hi) or hi <= lo:
        return {
            f"density_vpoc_{window}": None,
            f"density_vpoc_distance_{window}_pct": None,
            f"density_bin_share_{window}": None,
            f"density_cluster_share_{window}": None,
            f"density_vpoc_share_{window}": None,
        }
    hist, edges = np.histogram(prices, bins=bins, range=(lo, hi), weights=vols)
    total = float(np.sum(hist)) or 1.0
    vpoc_idx = int(np.argmax(hist))
    vpoc_price = float((edges[vpoc_idx] + edges[vpoc_idx + 1]) / 2.0)
    current_bin = int(np.clip(np.searchsorted(edges, close[idx], side="right") - 1, 0, bins - 1))
    cluster_start = max(0, current_bin - 1)
    cluster_end = min(bins, current_bin + 2)
    return {
        f"density_vpoc_{window}": vpoc_price,
        f"density_vpoc_distance_{window}_pct": (float(close[idx]) - vpoc_price) / max(float(close[idx]), 1e-9) * 100.0,
        f"density_bin_share_{window}": float(hist[current_bin]) / total,
        f"density_cluster_share_{window}": float(np.sum(hist[cluster_start:cluster_end])) / total,
        f"density_vpoc_share_{window}": float(hist[vpoc_idx]) / total,
    }


def _add_flow_density_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    typical = ((out["high"] + out["low"] + out["close"]) / 3.0).to_numpy(dtype=float)
    volume = out["volume"].to_numpy(dtype=float)
    close = out["close"].to_numpy(dtype=float)

    out["volume_ma20_prior"] = out["volume"].rolling(20, min_periods=1).mean().shift(1)
    out["volume_std20_prior"] = out["volume"].rolling(20, min_periods=2).std().shift(1)
    out["volume_ratio20"] = out["volume"] / out["volume_ma20_prior"].replace(0, np.nan)
    out["volume_z20"] = (out["volume"] - out["volume_ma20_prior"]) / out["volume_std20_prior"].replace(0, np.nan)
    out["vol_chg_1m"] = out["volume"].pct_change(1)
    out["delta_volume_1m"] = out["volume"].diff(1)
    out["delta_volume_ratio20"] = out["delta_volume_1m"] / out["volume_ma20_prior"].replace(0, np.nan)

    cum_pv = np.cumsum(typical * volume)
    cum_v = np.cumsum(volume)
    out["session_vwap"] = cum_pv / np.where(cum_v == 0, np.nan, cum_v)
    out["vwap_distance_pct"] = (out["close"] - out["session_vwap"]) / out["close"].replace(0, np.nan) * 100.0

    rows: list[dict[str, float | None]] = []
    for idx in range(len(out)):
        row = {}
        row.update(_density_window_features(typical, volume, close, idx, window=60))
        row.update(_density_window_features(typical, volume, close, idx, window=240))
        rows.append(row)
    dens = pd.DataFrame(rows)
    out = pd.concat([out.reset_index(drop=True), dens.reset_index(drop=True)], axis=1)
    out["density_vpoc_drift_20_pct"] = out["density_vpoc_distance_60_pct"] - out["density_vpoc_distance_60_pct"].shift(20)
    out["density_cluster_ratio_60_240"] = out["density_cluster_share_60"] / out["density_cluster_share_240"].replace(0, np.nan)
    return out


def _analysis_for_target(df: pd.DataFrame, target: dict[str, Any]) -> dict[str, Any]:
    signal_idx = _row_index_at_time(df, str(target["signal_time_utc"]))
    entry_idx = _row_index_at_time(df, str(target["entry_time_utc"]))
    row = df.iloc[signal_idx]

    volume_ratio = _safe_float(row.get("volume_ratio20"))
    volume_z = _safe_float(row.get("volume_z20"))
    delta_ratio = _safe_float(row.get("delta_volume_ratio20"))
    vol_chg = _safe_float(row.get("vol_chg_1m"))
    vpoc60_dist = _safe_float(row.get("density_vpoc_distance_60_pct"))
    vpoc240_dist = _safe_float(row.get("density_vpoc_distance_240_pct"))
    bin60 = _safe_float(row.get("density_bin_share_60"))
    cluster60 = _safe_float(row.get("density_cluster_share_60"))
    vpoc_share60 = _safe_float(row.get("density_vpoc_share_60"))
    cluster_ratio = _safe_float(row.get("density_cluster_ratio_60_240"))
    vwap_dist = _safe_float(row.get("vwap_distance_pct"))

    volume_support = bool(volume_ratio >= 1.25 or volume_z >= 1.0 or delta_ratio >= 0.75)
    volume_conflict = bool(volume_ratio > 0 and volume_ratio <= 0.55 and abs(delta_ratio) <= 0.25)
    density_support = bool(abs(vpoc60_dist) <= 0.20 or abs(vpoc240_dist) <= 0.28 or cluster60 >= 0.18 or cluster_ratio >= 1.25)
    density_conflict = bool(abs(vpoc60_dist) > 0.75 and abs(vpoc240_dist) > 0.75 and cluster60 < 0.12)
    vwap_support = bool(-1.20 <= vwap_dist <= 0.30)
    vwap_conflict = bool(vwap_dist > 0.85)

    supporting_blocks = [
        block
        for block, ok in [
            ("B010_VOLUME_FLOW", volume_support),
            ("B013_DENSITY_VPOC", density_support),
            ("B026_VWAP_DISTANCE", vwap_support),
        ]
        if ok
    ]
    conflict_blocks = [
        block
        for block, bad in [
            ("B010_VOLUME_FLOW", volume_conflict),
            ("B013_DENSITY_VPOC", density_conflict),
            ("B026_VWAP_DISTANCE", vwap_conflict),
        ]
        if bad
    ]

    return {
        **target,
        "signal_idx": signal_idx,
        "entry_idx": entry_idx,
        "signal_close": round(float(row["close"]), 8),
        "B010_volume_flow": {
            "vol_chg_1m": round(vol_chg, 6),
            "volume_ratio20": round(volume_ratio, 6),
            "volume_z20": round(volume_z, 6),
            "delta_volume_1m": round(_safe_float(row.get("delta_volume_1m")), 6),
            "delta_volume_ratio20": round(delta_ratio, 6),
            "visual_state": "support" if volume_support else ("conflict" if volume_conflict else "silent"),
        },
        "B013_density_vpoc": {
            "density_vpoc_60": round(_safe_float(row.get("density_vpoc_60")), 8),
            "density_vpoc_distance_60_pct": round(vpoc60_dist, 6),
            "density_bin_share_60": round(bin60, 6),
            "density_cluster_share_60": round(cluster60, 6),
            "density_vpoc_share_60": round(vpoc_share60, 6),
            "density_vpoc_240": round(_safe_float(row.get("density_vpoc_240")), 8),
            "density_vpoc_distance_240_pct": round(vpoc240_dist, 6),
            "density_bin_share_240": round(_safe_float(row.get("density_bin_share_240")), 6),
            "density_cluster_share_240": round(_safe_float(row.get("density_cluster_share_240")), 6),
            "density_vpoc_share_240": round(_safe_float(row.get("density_vpoc_share_240")), 6),
            "density_vpoc_drift_20_pct": round(_safe_float(row.get("density_vpoc_drift_20_pct")), 6),
            "density_cluster_ratio_60_240": round(cluster_ratio, 6),
            "visual_state": "support" if density_support else ("conflict" if density_conflict else "silent"),
        },
        "B026_vwap_distance": {
            "session_vwap": round(_safe_float(row.get("session_vwap")), 8),
            "vwap_distance_pct": round(vwap_dist, 6),
            "visual_state": "support" if vwap_support else ("conflict" if vwap_conflict else "silent"),
        },
        "V2B_visual_summary": {
            "supporting_blocks": supporting_blocks,
            "conflict_blocks": conflict_blocks,
            "note": "visual_evidence_only_not_allow_signal",
        },
    }


def _draw_volume(ax: Any, df: pd.DataFrame, *, alpha: float = 0.70) -> None:
    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(df["open"], df["close"])]
    ax.bar(df["open_time_utc"].dt.tz_convert(None), df["volume"], width=_bar_width_days(TIMEFRAME), color=colors, alpha=alpha)
    ax.plot(df["open_time_utc"].dt.tz_convert(None), df["volume_ma20_prior"], color="#ffcc80", linewidth=0.85, alpha=0.85)


def _draw_flow_lines(ax: Any, df: pd.DataFrame, *, alpha: float = 0.74) -> None:
    times = df["open_time_utc"].dt.tz_convert(None)
    ax.plot(times, df["session_vwap"], color="#ffb74d", linewidth=0.95, alpha=alpha, label="VWAP")
    ax.plot(times, df["density_vpoc_60"], color="#26c6da", linewidth=0.75, alpha=0.62, label="VPOC60")
    ax.plot(times, df["density_vpoc_240"], color="#7e57c2", linewidth=0.75, alpha=0.52, label="VPOC240")


def _draw_density_profile(ax: Any, df: pd.DataFrame, *, bins: int = 32) -> None:
    if df.empty:
        return
    typical = ((df["high"] + df["low"] + df["close"]) / 3.0).to_numpy(dtype=float)
    volume = df["volume"].to_numpy(dtype=float)
    lo = float(np.nanmin(df["low"]))
    hi = float(np.nanmax(df["high"]))
    if hi <= lo:
        return
    hist, edges = np.histogram(typical, bins=bins, range=(lo, hi), weights=volume)
    if float(np.max(hist)) <= 0:
        return
    x0, x1 = ax.get_xlim()
    width = (x1 - x0) * 0.055
    left = x1 - width
    for value, low, high in zip(hist, edges[:-1], edges[1:]):
        share = float(value) / float(np.max(hist))
        ax.fill_betweenx([low, high], left, left + width * share, color="#546e7a", alpha=0.12, linewidth=0)


def _draw_target_marker(ax: Any, item: dict[str, Any], *, show_price: bool) -> None:
    entry = pd.Timestamp(item["entry_time_utc"]).tz_convert("UTC")
    price = float(item["entry_price_plus_5bps"])
    ax.axvline(entry.tz_convert(None), color="#00e676", linewidth=1.25, alpha=0.92)
    ax.scatter([entry.tz_convert(None)], [price], marker="^", s=58, color="#00e676", edgecolor="white", linewidth=0.65, zorder=8)
    label = f"{item['target_id']} {_fmt_min(item['entry_time_utc'])}"
    if show_price:
        label += f"\n+5 {price:.4f}"
    ax.text(entry.tz_convert(None), price, label, color="#00e676", fontsize=6.8, ha="left", va="bottom", zorder=9)


def _render_full_day(df: pd.DataFrame, records: list[dict[str, Any]], *, day: str, out_path: Path) -> None:
    fig = plt.figure(figsize=(28, 13), facecolor="#101418")
    grid = fig.add_gridspec(3, 1, height_ratios=[4.8, 1.25, 1.15], hspace=0.06)
    ax_price = fig.add_subplot(grid[0, 0])
    ax_vol = fig.add_subplot(grid[1, 0], sharex=ax_price)
    ax_z = fig.add_subplot(grid[2, 0], sharex=ax_price)
    for ax in [ax_price, ax_vol, ax_z]:
        _style_axis(ax)

    _draw_candles(ax_price, df, TIMEFRAME, linewidth=0.28)
    _draw_flow_lines(ax_price, df)
    for item in records:
        signal = pd.Timestamp(item["signal_time_utc"]).tz_convert("UTC")
        start = signal - pd.Timedelta(minutes=42)
        end = signal + pd.Timedelta(minutes=28)
        ax_price.axvspan(start.tz_convert(None), signal.tz_convert(None), color="#1565c0", alpha=0.030, zorder=0)
        ax_price.axvspan(signal.tz_convert(None), end.tz_convert(None), color="#00e676", alpha=0.026, zorder=0)
        _draw_target_marker(ax_price, item, show_price=False)

    _draw_volume(ax_vol, df)
    colors = np.where(df["volume_z20"].fillna(0) >= 0, "#26a69a", "#ef5350")
    ax_z.bar(df["open_time_utc"].dt.tz_convert(None), df["volume_z20"].clip(-4, 6), width=_bar_width_days(TIMEFRAME), color=colors, alpha=0.58)
    ax_z.axhline(1.0, color="#ffcc80", linewidth=0.75, alpha=0.65)
    ax_z.axhline(0.0, color="#cfd8dc", linewidth=0.55, alpha=0.38)

    ax_price.legend(loc="upper left", fontsize=7, frameon=True, facecolor="#101418", edgecolor="#455a64")
    ax_price.set_title(
        f"{SYMBOL} {TIMEFRAME} {day} | V2B FLOW/DENSITY PASSPORT OVERLAY | B010/B013/B026 | NO ML/OPTUNA",
        color="white",
        fontsize=15,
    )
    ax_price.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    ax_z.set_ylabel("Vol z20", color="white")
    day_start = pd.Timestamp(f"{day}T00:00:00")
    day_end = day_start + pd.Timedelta(days=1)
    ax_price.set_xlim(day_start.to_pydatetime(), day_end.to_pydatetime())
    ax_z.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 3)))
    ax_z.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate()
    fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def _render_zoom_page(df: pd.DataFrame, records: list[dict[str, Any]], *, page: int, day: str, out_path: Path) -> None:
    cols = 2
    rows = int(np.ceil(len(records) / cols))
    fig = plt.figure(figsize=(24, max(7.0 * rows, 8.0)), facecolor="#101418")
    grid = fig.add_gridspec(rows * 2, cols, height_ratios=[4.2, 1.15] * rows, hspace=0.24, wspace=0.10)
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
        _draw_flow_lines(ax_price, win)
        ax_price.axvspan(start.tz_convert(None), signal.tz_convert(None), color="#1565c0", alpha=0.050, zorder=0)
        ax_price.axvspan(signal.tz_convert(None), end.tz_convert(None), color="#00e676", alpha=0.038, zorder=0)
        _draw_target_marker(ax_price, item, show_price=True)
        _draw_density_profile(ax_price, win)
        _draw_volume(ax_vol, win)
        ax_price.set_xlim(start.tz_convert(None).to_pydatetime(), end.tz_convert(None).to_pydatetime())
        support = "/".join(block.split("_", 1)[0] for block in item["V2B_visual_summary"]["supporting_blocks"]) or "none"
        conflict = "/".join(block.split("_", 1)[0] for block in item["V2B_visual_summary"]["conflict_blocks"]) or "none"
        vol = item["B010_volume_flow"]
        den = item["B013_density_vpoc"]
        vw = item["B026_vwap_distance"]
        title = (
            f"{item['target_id']} {item['target_type']} | signal {_fmt_min(item['signal_time_utc'])} -> entry {_fmt_min(item['entry_time_utc'])} "
            f"| volR {vol['volume_ratio20']:.2f} z {vol['volume_z20']:.2f} "
            f"| vpoc60 {den['density_vpoc_distance_60_pct']:.2f}% | vwap {vw['vwap_distance_pct']:.2f}% "
            f"| support={support} conflict={conflict}"
        )
        ax_price.set_title(title, color="white", fontsize=8.0)
        ax_price.set_ylabel("Price", color="white")
        ax_vol.set_ylabel("Vol", color="white")
        ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.suptitle(
        f"{SYMBOL} {TIMEFRAME} {day} | V2B zoom page {page:02d} | local flow/density squares | visual only",
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
        "volume_ratio20",
        "volume_z20",
        "delta_volume_ratio20",
        "density_vpoc_distance_60_pct",
        "density_bin_share_60",
        "density_cluster_share_60",
        "density_vpoc_distance_240_pct",
        "density_cluster_share_240",
        "density_vpoc_drift_20_pct",
        "density_cluster_ratio_60_240",
        "session_vwap",
        "vwap_distance_pct",
        "supporting_blocks",
        "conflict_blocks",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for item in records:
            vol = item["B010_volume_flow"]
            den = item["B013_density_vpoc"]
            vw = item["B026_vwap_distance"]
            summary = item["V2B_visual_summary"]
            writer.writerow(
                {
                    "target_id": item["target_id"],
                    "target_type": item["target_type"],
                    "signal_time_utc": item["signal_time_utc"],
                    "entry_time_utc": item["entry_time_utc"],
                    "entry_open_price": item["entry_open_price"],
                    "entry_price_plus_5bps": item["entry_price_plus_5bps"],
                    "signal_close": item["signal_close"],
                    "volume_ratio20": vol["volume_ratio20"],
                    "volume_z20": vol["volume_z20"],
                    "delta_volume_ratio20": vol["delta_volume_ratio20"],
                    "density_vpoc_distance_60_pct": den["density_vpoc_distance_60_pct"],
                    "density_bin_share_60": den["density_bin_share_60"],
                    "density_cluster_share_60": den["density_cluster_share_60"],
                    "density_vpoc_distance_240_pct": den["density_vpoc_distance_240_pct"],
                    "density_cluster_share_240": den["density_cluster_share_240"],
                    "density_vpoc_drift_20_pct": den["density_vpoc_drift_20_pct"],
                    "density_cluster_ratio_60_240": den["density_cluster_ratio_60_240"],
                    "session_vwap": vw["session_vwap"],
                    "vwap_distance_pct": vw["vwap_distance_pct"],
                    "supporting_blocks": ",".join(summary["supporting_blocks"]),
                    "conflict_blocks": ",".join(summary["conflict_blocks"]),
                }
            )


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    rows = payload["records"]
    block_ids = ["B010_VOLUME_FLOW", "B013_DENSITY_VPOC", "B026_VWAP_DISTANCE"]
    counts = {
        block: sum(1 for item in rows if block in item["V2B_visual_summary"]["supporting_blocks"])
        for block in block_ids
    }
    lines = [
        "# V2B Flow/Density Layer 2026-05-14",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: наложить второй слой паспортов на ручной эталон `SOLUSDT 1m 2026-05-14 M01..M19`.",
        "",
        "Это visual evidence layer. Это не scorer, не target-lock, не Optuna и не ML-export.",
        "",
        "## Что наложено",
        "",
        "1. `B010 VOLUME_FLOW`: volume change, volume z-score, delta volume.",
        "2. `B013 DENSITY/VPOC`: VPOC 60/240, bin/share/cluster context, VPOC drift.",
        "3. `B026 VWAP_DISTANCE`: session VWAP distance.",
        "",
        "`B011 OBV` и `B012 MFI` пока не включены в active layer: они идут позже, если B010/B013/B026 не хватает.",
        "",
        "## Support count",
        "",
    ]
    for block, count in counts.items():
        lines.append(f"- `{block}`: `{count}/{len(rows)}`.")
    lines.extend(
        [
            "",
            "## Граница no-lookahead",
            "",
            "- Все расчеты заканчиваются на закрытой signal-свече.",
            "- Entry open и цена `+5 bps` показаны только как execution/control, не как feature выбора.",
            "- Future return, TP/SL, MFE/MAE, entry-candle OHLCV, scorer, Optuna и ML здесь не используются.",
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
            "## Короткий аудит",
            "",
            "- Если блок поддерживает почти все входы, это фон/контекст, а не сигнал.",
            "- Если блок поддерживает только часть входов, его надо сравнивать с типами входа и позже переносить в summary matrix.",
            "- Следующий слой после пользовательского review: `V2C_MOMENTUM_LAYER` на 14 мая, а не переход к 15 мая.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(day: str, out_dir: Path) -> dict[str, Any]:
    if day != "2026-05-14":
        raise ValueError("V2B current pass is fixed to 2026-05-14 before moving to the second reference day.")
    root = Path(__file__).resolve().parents[2]
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    df = _add_flow_density_features(_load_ohlcv(_source_csv(root, day)))
    targets = _load_targets(root, day)
    records = [_analysis_for_target(df, target) for target in targets]

    day_tag = day.replace("-", "")
    full_day_path = out_dir / f"V2B_FLOW_DENSITY_FULL_DAY_{day_tag}.png"
    zoom_page_01_path = out_dir / f"V2B_FLOW_DENSITY_ZOOM_PAGE_01_{day_tag}.png"
    zoom_page_02_path = out_dir / f"V2B_FLOW_DENSITY_ZOOM_PAGE_02_{day_tag}.png"
    json_path = out_dir / f"V2B_FLOW_DENSITY_OVERLAY_{day_tag}.json"
    csv_path = out_dir / f"V2B_FLOW_DENSITY_OVERLAY_{day_tag}.csv"
    report_path = out_dir / f"V2B_FLOW_DENSITY_OVERLAY_{day_tag}_RU.md"

    _render_full_day(df, records, day=day, out_path=full_day_path)
    _render_zoom_page(df, records[:10], page=1, day=day, out_path=zoom_page_01_path)
    _render_zoom_page(df, records[10:], page=2, day=day, out_path=zoom_page_02_path)

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
            "slippage_bps": SLIPPAGE_BPS,
        },
        "passport_blocks": {
            "B010": ["F019_VOLCHG_ALLOW", "F020_VOLZ20_ALLOW", "F021_DELTAVOL_ALLOW"],
            "B013": [
                "F025_VPOCDIST60_ALLOW",
                "F026_BINSHARE60_ALLOW",
                "F027_CLUSTERSHARE60_ALLOW",
                "F028_VPOCSHARE60_ALLOW",
                "F029_VPOCDIST240_ALLOW",
                "F030_BINSHARE240_ALLOW",
                "F031_CLUSTERSHARE240_ALLOW",
                "F032_VPOCSHARE240_ALLOW",
                "F033_VPOCDRIFT20_ALLOW",
                "F034_CLUSTERRATIO_ALLOW",
            ],
            "B026": ["F024_VWAPDIST_ALLOW"],
        },
        "records": records,
        "artifacts": artifacts,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_csv(csv_path, records)
    _write_report(report_path, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Render V2B flow/density passport overlay for fresh target-led manual entries.")
    parser.add_argument("--day", default="2026-05-14", help="UTC day. Current V2B pass is fixed to 2026-05-14.")
    parser.add_argument(
        "--out-dir",
        default="reports/final_review/visual_entry_v3/fresh_target_led/strategy_passport_overlay_v2b",
        help="Output directory.",
    )
    args = parser.parse_args()
    payload = run(args.day, Path(args.out_dir))
    print(json.dumps({"status": payload["status"], "artifacts": payload["artifacts"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
