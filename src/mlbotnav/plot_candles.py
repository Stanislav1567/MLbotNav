from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle


def _load_latest_csv(project_root: Path, day: str, tf: str, symbol: str) -> Path:
    base = project_root / "data" / "raw" / "bybit_ohlcv" / f"dt={day}" / f"tf={tf}" / f"symbol={symbol}"
    files = sorted(base.glob("part-*.csv"))
    if not files:
        raise FileNotFoundError(f"No data files in {base}")
    return files[-1]


def _timeframe_bar_width_days(tf: str) -> float:
    if tf.endswith("d"):
        days = int(tf[:-1])
        return days * 0.7
    minutes = int(tf[:-1])
    return (minutes / (24 * 60)) * 0.8


def main() -> int:
    parser = argparse.ArgumentParser(description="Render candlestick chart with volume and pattern markers.")
    parser.add_argument("--date", required=True, help="UTC date YYYY-MM-DD")
    parser.add_argument("--timeframe", default="1m", help="Timeframe folder, e.g. 1m, 5m, 1h, 1d")
    parser.add_argument("--symbol", default="SOLUSDT", help="Symbol folder")
    parser.add_argument("--show-volume", action="store_true", help="Show volume panel")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    src = _load_latest_csv(project_root, args.date, args.timeframe, args.symbol)

    df = pd.read_csv(src)
    df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], utc=True)
    df = df.sort_values("open_time_utc").reset_index(drop=True)

    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()

    x = mdates.date2num(df["open_time_utc"].to_numpy())
    width = _timeframe_bar_width_days(args.timeframe)

    up = df["close"] >= df["open"]

    if args.show_volume:
        fig, (ax_price, ax_vol) = plt.subplots(
            2,
            1,
            figsize=(18, 9),
            sharex=True,
            gridspec_kw={"height_ratios": [4, 1.4]},
        )
    else:
        fig, ax_price = plt.subplots(1, 1, figsize=(18, 7), sharex=True)
        ax_vol = None
    bg = "#101418"
    fig.patch.set_facecolor(bg)
    ax_price.set_facecolor(bg)
    if ax_vol is not None:
        ax_vol.set_facecolor(bg)

    up_color = "#26a69a"
    down_color = "#ef5350"
    wick_color = "#cfd8dc"

    # Wicks
    ax_price.vlines(x, df["low"], df["high"], color=wick_color, linewidth=0.8, alpha=0.85, zorder=1)

    # Candle bodies
    for i in range(len(df)):
        o = df.iloc[i]["open"]
        c = df.iloc[i]["close"]
        lower = min(o, c)
        height = max(abs(c - o), 1e-8)
        color = up_color if c >= o else down_color
        rect = Rectangle((x[i] - width / 2, lower), width, height, facecolor=color, edgecolor=color, linewidth=0.6)
        ax_price.add_patch(rect)

    ax_price.plot(df["open_time_utc"], df["ema20"], color="#ffd54f", linewidth=1.1, label="EMA20")
    ax_price.plot(df["open_time_utc"], df["ema50"], color="#64b5f6", linewidth=1.1, label="EMA50")

    if ax_vol is not None:
        vol_colors = [up_color if x else down_color for x in up]
        ax_vol.bar(df["open_time_utc"], df["volume"], width=width, color=vol_colors, alpha=0.85)

    title = f"{args.symbol} | Bybit Linear Futures | {args.timeframe} | {args.date} UTC | CLEAN"
    ax_price.set_title(title, color="white", fontsize=14, pad=10)
    ax_price.set_ylabel("Price", color="white")
    if ax_vol is not None:
        ax_vol.set_ylabel("Volume", color="white")

    axes = [ax_price] if ax_vol is None else [ax_price, ax_vol]
    for ax in axes:
        ax.grid(color="#2f3a40", alpha=0.45, linewidth=0.6)
        ax.tick_params(colors="#e0e0e0")
        for spine in ax.spines.values():
            spine.set_color("#3a444b")

    if ax_vol is not None:
        ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    else:
        ax_price.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate()

    ax_price.legend(facecolor="#172026", edgecolor="#3a444b", labelcolor="white", fontsize=9, ncol=3, loc="upper left")

    out_dir = project_root / "reports" / "screenshots"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = out_dir / f"candles_clean_v2_{args.symbol}_{args.timeframe}_{args.date}_{ts}.png"
    plt.tight_layout()
    plt.savefig(out_path, dpi=160, facecolor=fig.get_facecolor())
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
