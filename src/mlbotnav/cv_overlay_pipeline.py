from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from mlbotnav.audit import audit_event
from mlbotnav.dataset import build_feature_frame, load_ohlcv_range


def _ensure_base_chart(project_root: Path, *, date: str, symbol: str, timeframe: str) -> Path:
    pattern = project_root / "reports" / "screenshots"
    candidates = sorted(pattern.glob(f"candles_clean_v2_{symbol}_{timeframe}_{date}_*.png"))
    if candidates:
        return candidates[-1]
    raise FileNotFoundError(f"Base chart not found for {symbol} {timeframe} {date}")


def _calc_levels(df: pd.DataFrame, window: int = 30) -> tuple[list[float], list[float]]:
    h = df["high"].rolling(window).max()
    l = df["low"].rolling(window).min()
    res = sorted(set(np.round(h.dropna().tail(5), 4).tolist()))
    sup = sorted(set(np.round(l.dropna().tail(5), 4).tolist()))
    return sup[-3:], res[-3:]


def _build_signals(feat: pd.DataFrame) -> pd.DataFrame:
    s = feat.copy()
    s["signal"] = 0
    long_cond = (s["ema_gap"] > 0) & (s["breakout_flag"] == 1) & (s["engulf_bull_flag"] == 1)
    short_cond = (s["ema_gap"] < 0) & (s["breakout_flag"] == 1) & (s["engulf_bear_flag"] == 1)
    s.loc[long_cond, "signal"] = 1
    s.loc[short_cond, "signal"] = -1
    return s


def main() -> int:
    parser = argparse.ArgumentParser(description="CV overlay pipeline: analyze OHLCV and render annotation overlay.")
    parser.add_argument("--date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="60m", help="1m/5m/15m/30m/60m/240m/1d")
    parser.add_argument("--source-id", default="mlbotnav_cv")
    parser.add_argument("--scanner-status", default="unknown", help="clean|suspicious|disabled|unknown")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    raw = load_ohlcv_range(
        project_root,
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=args.date,
        end_date=args.date,
    )
    feat = build_feature_frame(raw, horizon_bars=1)
    sig = _build_signals(feat)

    sup_levels, res_levels = _calc_levels(raw)
    signal_rows = sig[sig["signal"] != 0].tail(8).copy()

    base_chart = _ensure_base_chart(project_root, date=args.date, symbol=args.symbol, timeframe=args.timeframe)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = project_root / "data" / "cv" / "artifacts" / f"source_id={args.source_id}" / f"dt={args.date}" / f"tf={args.timeframe}" / f"symbol={args.symbol}"
    out_dir.mkdir(parents=True, exist_ok=True)
    original_path = out_dir / f"{ts}_original.png"
    overlay_path = out_dir / f"{ts}_overlay.png"
    mask_path = out_dir / f"{ts}_mask.png"
    metadata_path = out_dir / f"{ts}_metadata.json"
    decision_path = out_dir / f"{ts}_decision.json"

    shutil.copy2(base_chart, original_path)

    # Render overlay from OHLCV (clean base + annotation layers).
    df = raw.copy().sort_values("open_time_utc").reset_index(drop=True)
    df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], utc=True)
    x = mdates.date2num(df["open_time_utc"].to_numpy())
    width = (60 / (24 * 60)) * 0.75 if args.timeframe == "60m" else (5 / (24 * 60))

    fig, ax = plt.subplots(figsize=(16, 7))
    fig.patch.set_facecolor("#0f1318")
    ax.set_facecolor("#0f1318")
    up_c = "#26a69a"
    dn_c = "#ef5350"
    wick = "#cfd8dc"
    up = df["close"] >= df["open"]

    ax.vlines(x, df["low"], df["high"], color=wick, linewidth=0.8, alpha=0.85, zorder=1)
    for i in range(len(df)):
        o = df.iloc[i]["open"]
        c = df.iloc[i]["close"]
        lo = min(o, c)
        h = max(abs(c - o), 1e-8)
        col = up_c if c >= o else dn_c
        ax.add_patch(plt.Rectangle((x[i] - width / 2, lo), width, h, facecolor=col, edgecolor=col, linewidth=0.6))

    for lvl in sup_levels:
        ax.axhline(y=lvl, color="#81c784", linewidth=1.0, alpha=0.7, linestyle="--")
    for lvl in res_levels:
        ax.axhline(y=lvl, color="#ff8a65", linewidth=1.0, alpha=0.7, linestyle="--")

    if not signal_rows.empty:
        signal_rows["open_time_utc"] = pd.to_datetime(signal_rows["open_time_utc"], utc=True)
        long_pts = signal_rows[signal_rows["signal"] == 1]
        short_pts = signal_rows[signal_rows["signal"] == -1]
        if not long_pts.empty:
            ax.scatter(long_pts["open_time_utc"], long_pts["low"] * 0.998, marker="^", s=60, color="#00e676", label="Entry Long")
        if not short_pts.empty:
            ax.scatter(short_pts["open_time_utc"], short_pts["high"] * 1.002, marker="v", s=60, color="#ff1744", label="Entry Short")

    ax.grid(color="#2f3a40", alpha=0.35)
    ax.tick_params(colors="#e0e0e0")
    ax.set_title(f"{args.symbol} {args.timeframe} | Overlay CV Annotations | {args.date} UTC", color="white")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    for sp in ax.spines.values():
        sp.set_color("#3a444b")
    if ax.get_legend_handles_labels()[0]:
        ax.legend(facecolor="#172026", edgecolor="#3a444b", labelcolor="white")
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(overlay_path, dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)

    # Render binary-like mask layer for downstream CV.
    fig_m, ax_m = plt.subplots(figsize=(16, 7))
    fig_m.patch.set_facecolor("black")
    ax_m.set_facecolor("black")
    for lvl in sup_levels:
        ax_m.axhline(y=lvl, color="white", linewidth=1.2, alpha=0.95, linestyle="--")
    for lvl in res_levels:
        ax_m.axhline(y=lvl, color="white", linewidth=1.2, alpha=0.95, linestyle="--")
    if not signal_rows.empty:
        signal_rows["open_time_utc"] = pd.to_datetime(signal_rows["open_time_utc"], utc=True)
        long_pts = signal_rows[signal_rows["signal"] == 1]
        short_pts = signal_rows[signal_rows["signal"] == -1]
        if not long_pts.empty:
            ax_m.scatter(long_pts["open_time_utc"], long_pts["low"] * 0.998, marker="^", s=80, color="white")
        if not short_pts.empty:
            ax_m.scatter(short_pts["open_time_utc"], short_pts["high"] * 1.002, marker="v", s=80, color="white")
    ax_m.set_xlim(mdates.date2num(df["open_time_utc"].iloc[0]), mdates.date2num(df["open_time_utc"].iloc[-1]))
    ax_m.set_ylim(float(df["low"].min()) * 0.997, float(df["high"].max()) * 1.003)
    ax_m.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(mask_path, dpi=160, facecolor="black")
    plt.close(fig_m)

    metadata = {
        "source_id": args.source_id,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "trade_date_utc": args.date,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "original_file": str(original_path),
        "overlay_file": str(overlay_path),
        "mask_file": str(mask_path),
        "support_levels": sup_levels,
        "resistance_levels": res_levels,
        "signals_count": int(len(signal_rows)),
        "scanner_status": args.scanner_status,
        "pipeline_version": "cv_overlay_v2",
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    decision = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "decision": "NO_TRADE" if signal_rows.empty else "SIGNAL_PRESENT",
        "reason_code": "no_pattern_confluence" if signal_rows.empty else "pattern_structure_confluence",
        "signals_preview": (
            signal_rows[["open_time_utc", "signal", "close"]]
            .tail(5)
            .assign(open_time_utc=lambda x: x["open_time_utc"].astype(str))
            .to_dict(orient="records")
            if not signal_rows.empty
            else []
        ),
        "mask_file": str(mask_path),
        "scanner_status": args.scanner_status,
    }
    decision_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")

    audit_event(
        project_root,
        event="cv_overlay_pipeline_completed",
        payload={
            "source_id": args.source_id,
            "symbol": args.symbol,
            "timeframe": args.timeframe,
            "date": args.date,
            "original_file": str(original_path),
            "overlay_file": str(overlay_path),
            "mask_file": str(mask_path),
            "metadata_file": str(metadata_path),
            "decision_file": str(decision_path),
        },
    )

    print(
        json.dumps(
            {
                "original_file": str(original_path),
                "overlay_file": str(overlay_path),
                "mask_file": str(mask_path),
                "metadata_file": str(metadata_path),
                "decision_file": str(decision_path),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
