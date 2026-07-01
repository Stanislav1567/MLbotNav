from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle


def _bar_width_days(tf: str) -> float:
    if tf.endswith("d"):
        return int(tf[:-1]) * 0.7
    if tf.endswith("h"):
        return (int(tf[:-1]) * 60 / (24 * 60)) * 0.8
    return (int(tf[:-1]) / (24 * 60)) * 0.8


def _load_latest_raw(project_root: Path, day: str, tf: str, symbol: str) -> Path:
    base = project_root / "data" / "raw" / "bybit_ohlcv" / f"dt={day}" / f"tf={tf}" / f"symbol={symbol}"
    direct = base / "part-final.csv"
    if direct.exists():
        return direct
    files = sorted(base.glob("part-*.csv"))
    if not files:
        raise FileNotFoundError(f"No raw OHLCV files in {base}")
    return files[-1]


def _load_raw_range(project_root: Path, start_day: str, end_day: str, tf: str, symbol: str) -> pd.DataFrame:
    days = pd.date_range(start=start_day, end=end_day, freq="D")
    chunks: list[pd.DataFrame] = []
    for d in days:
        day = d.strftime("%Y-%m-%d")
        path = _load_latest_raw(project_root, day, tf, symbol)
        x = pd.read_csv(path)
        x["open_time_utc"] = pd.to_datetime(x["open_time_utc"], utc=True, errors="coerce")
        chunks.append(x)
    if not chunks:
        raise FileNotFoundError(f"No raw OHLCV in range {start_day}..{end_day}")
    raw = pd.concat(chunks, ignore_index=True)
    raw = raw.dropna(subset=["open_time_utc"]).sort_values("open_time_utc").drop_duplicates(subset=["open_time_utc"]).reset_index(drop=True)
    return raw


def main() -> int:
    parser = argparse.ArgumentParser(description="Render trade simulation with entry/exit markers for one day or date range.")
    parser.add_argument("--pipeline-report", required=True)
    parser.add_argument("--date", required=True, help="UTC start date YYYY-MM-DD")
    parser.add_argument("--end-date", default=None, help="Optional UTC end date YYYY-MM-DD")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    report = json.loads(Path(args.pipeline_report).read_text(encoding="utf-8"))
    symbol = str(report.get("symbol", "SOLUSDT"))
    timeframe = str(report.get("timeframe", "1m"))
    horizon = int((report.get("strategy", {}) or {}).get("horizon_bars", 1))
    bt_path = Path((report.get("artifacts", {}) or {}).get("backtest_path", ""))
    if not bt_path.exists():
        raise FileNotFoundError(f"Backtest path not found: {bt_path}")

    end_date = str(args.end_date) if args.end_date else str(args.date)
    raw = _load_raw_range(project_root, str(args.date), end_date, timeframe, symbol)
    raw["ema20"] = raw["close"].ewm(span=20, adjust=False).mean()
    raw["ema50"] = raw["close"].ewm(span=50, adjust=False).mean()

    bt = pd.read_csv(bt_path)
    bt["open_time_utc"] = pd.to_datetime(bt["open_time_utc"], utc=True, errors="coerce")
    start_ts = pd.Timestamp(str(args.date), tz="UTC")
    end_ts = pd.Timestamp(end_date, tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    trades = bt[(bt["side"] != 0) & (bt["open_time_utc"] >= start_ts) & (bt["open_time_utc"] <= end_ts)].copy()

    idx_map = {t: i for i, t in enumerate(raw["open_time_utc"])}
    trade_points: list[dict] = []
    for _, row in trades.iterrows():
        # Prefer explicit execution fields from exchange_like mode.
        et = pd.to_datetime(row.get("entry_time_utc"), utc=True, errors="coerce")
        xt = pd.to_datetime(row.get("exit_time_utc"), utc=True, errors="coerce")
        ep = row.get("entry_price")
        xp = row.get("exit_price")
        if pd.notna(et) and pd.notna(xt) and pd.notna(ep) and pd.notna(xp):
            entry_t = et
            exit_t = xt
            entry_px = float(ep)
            exit_px = float(xp)
        else:
            # Backward-compatible fallback (research mode).
            entry_t = row["open_time_utc"]
            if entry_t not in idx_map:
                continue
            i = idx_map[entry_t]
            j = i + horizon
            if j >= len(raw):
                continue
            exit_t = raw.iloc[j]["open_time_utc"]
            entry_px = float(raw.iloc[i]["close"])
            exit_px = float(raw.iloc[j]["close"])
        trade_points.append(
            {
                "entry_time": entry_t,
                "exit_time": exit_t,
                "entry_px": entry_px,
                "exit_px": exit_px,
                "side": int(row["side"]),
                "net_return": float(row.get("net_return", 0.0)),
            }
        )

    x = mdates.date2num(raw["open_time_utc"].to_numpy())
    width = _bar_width_days(timeframe)
    up = raw["close"] >= raw["open"]

    fig, (ax_price, ax_vol) = plt.subplots(
        2,
        1,
        figsize=(20, 10),
        sharex=True,
        gridspec_kw={"height_ratios": [4.2, 1.3]},
    )
    bg = "#101418"
    fig.patch.set_facecolor(bg)
    ax_price.set_facecolor(bg)
    ax_vol.set_facecolor(bg)

    up_color = "#26a69a"
    down_color = "#ef5350"
    wick_color = "#cfd8dc"

    ax_price.vlines(x, raw["low"], raw["high"], color=wick_color, linewidth=0.75, alpha=0.9, zorder=1)
    for i in range(len(raw)):
        o = float(raw.iloc[i]["open"])
        c = float(raw.iloc[i]["close"])
        lower = min(o, c)
        height = max(abs(c - o), 1e-8)
        color = up_color if c >= o else down_color
        rect = Rectangle((x[i] - width / 2, lower), width, height, facecolor=color, edgecolor=color, linewidth=0.55)
        ax_price.add_patch(rect)

    ax_price.plot(raw["open_time_utc"], raw["ema20"], color="#ffd54f", linewidth=1.0, label="EMA20")
    ax_price.plot(raw["open_time_utc"], raw["ema50"], color="#64b5f6", linewidth=1.0, label="EMA50")
    vol_colors = [up_color if b else down_color for b in up]
    ax_vol.bar(raw["open_time_utc"], raw["volume"], width=width, color=vol_colors, alpha=0.85)

    long_entries_x: list[pd.Timestamp] = []
    long_entries_y: list[float] = []
    short_entries_x: list[pd.Timestamp] = []
    short_entries_y: list[float] = []
    exits_x: list[pd.Timestamp] = []
    exits_y: list[float] = []
    exit_colors: list[str] = []
    for t in trade_points:
        if int(t["side"]) > 0:
            long_entries_x.append(t["entry_time"])
            long_entries_y.append(float(t["entry_px"]))
        else:
            short_entries_x.append(t["entry_time"])
            short_entries_y.append(float(t["entry_px"]))
        exits_x.append(t["exit_time"])
        exits_y.append(float(t["exit_px"]))
        exit_colors.append("#00e676" if float(t["net_return"]) > 0 else "#ff1744")

    if long_entries_x:
        ax_price.scatter(long_entries_x, long_entries_y, marker="^", s=45, color="#00e676", label="Entry Long", zorder=5)
    if short_entries_x:
        ax_price.scatter(short_entries_x, short_entries_y, marker="v", s=45, color="#ff1744", label="Entry Short", zorder=5)
    if exits_x:
        ax_price.scatter(exits_x, exits_y, marker="x", s=36, c=exit_colors, linewidths=1.2, label="Exit", zorder=5)

    signal_mode = str((report.get("risk_policy", {}) or {}).get("signal_mode", "both"))
    date_tag = str(args.date) if end_date == str(args.date) else f"{args.date}..{end_date}"
    ax_price.set_title(
        f"{symbol} {timeframe} {date_tag} UTC | mode={signal_mode} | Trade Simulation (Entry/Exit)",
        color="white",
        fontsize=14,
        pad=10,
    )
    ax_price.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    for ax in (ax_price, ax_vol):
        ax.grid(color="#2f3a40", alpha=0.45, linewidth=0.6)
        ax.tick_params(colors="#e0e0e0")
        for sp in ax.spines.values():
            sp.set_color("#3a444b")
    ax_price.legend(facecolor="#172026", edgecolor="#3a444b", labelcolor="white", fontsize=9, loc="upper left", ncol=4)
    fig.autofmt_xdate()
    plt.tight_layout()

    out_dir = project_root / "reports" / "final_review"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    day_tag = str(args.date) if end_date == str(args.date) else f"{args.date}_to_{end_date}"
    out_png = out_dir / f"trade_simulation_{symbol}_{timeframe}_{day_tag}_{signal_mode}_{ts}.png"
    out_json = out_dir / f"trade_simulation_{symbol}_{timeframe}_{day_tag}_{signal_mode}_{ts}.json"
    plt.savefig(out_png, dpi=170, facecolor=fig.get_facecolor())
    plt.close(fig)

    summary = {
        "pipeline_report": str(Path(args.pipeline_report).resolve()),
        "backtest_path": str(bt_path.resolve()),
        "symbol": symbol,
        "timeframe": timeframe,
        "date": args.date,
        "end_date": end_date,
        "signal_mode": signal_mode,
        "horizon_bars": horizon,
        "trades_on_day": int(len(trade_points)),
        "long_entries": int(len(long_entries_x)),
        "short_entries": int(len(short_entries_x)),
        "visual_png": str(out_png),
    }
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"visual_png": str(out_png), "summary_json": str(out_json), "trades_on_day": int(len(trade_points))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
