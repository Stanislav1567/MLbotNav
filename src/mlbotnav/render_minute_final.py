from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle


def _latest(path_glob: str, root: Path) -> Path | None:
    files = sorted(root.glob(path_glob), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def _load_latest_raw(project_root: Path, day: str, tf: str, symbol: str) -> Path:
    base = project_root / "data" / "raw" / "bybit_ohlcv" / f"dt={day}" / f"tf={tf}" / f"symbol={symbol}"
    files = sorted(base.glob("part-*.csv"))
    if not files:
        raise FileNotFoundError(f"No raw OHLCV files in {base}")
    return files[-1]


def _bar_width_days(tf: str) -> float:
    if tf.endswith("d"):
        return int(tf[:-1]) * 0.7
    minutes = int(tf[:-1])
    return (minutes / (24 * 60)) * 0.8


def _build_visual(
    *,
    raw_df: pd.DataFrame,
    entry_time: pd.Timestamp,
    side: int,
    out_png: Path,
    symbol: str,
    timeframe: str,
) -> None:
    df = raw_df.sort_values("open_time_utc").reset_index(drop=True).copy()
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()

    idx = (df["open_time_utc"] - entry_time).abs().idxmin()
    left = max(0, int(idx) - 180)
    right = min(len(df) - 1, int(idx) + 180)
    win = df.iloc[left : right + 1].copy()

    x = mdates.date2num(win["open_time_utc"].to_numpy())
    width = _bar_width_days(timeframe)
    up = win["close"] >= win["open"]

    fig, (ax_price, ax_vol) = plt.subplots(
        2,
        1,
        figsize=(18, 9),
        sharex=True,
        gridspec_kw={"height_ratios": [4, 1.4]},
    )
    bg = "#101418"
    fig.patch.set_facecolor(bg)
    ax_price.set_facecolor(bg)
    ax_vol.set_facecolor(bg)

    up_color = "#26a69a"
    down_color = "#ef5350"
    wick_color = "#cfd8dc"
    ax_price.vlines(x, win["low"], win["high"], color=wick_color, linewidth=0.8, alpha=0.85, zorder=1)
    for i in range(len(win)):
        o = win.iloc[i]["open"]
        c = win.iloc[i]["close"]
        lower = min(o, c)
        height = max(abs(c - o), 1e-8)
        color = up_color if c >= o else down_color
        rect = Rectangle((x[i] - width / 2, lower), width, height, facecolor=color, edgecolor=color, linewidth=0.6)
        ax_price.add_patch(rect)

    ax_price.plot(win["open_time_utc"], win["ema20"], color="#ffd54f", linewidth=1.1, label="EMA20")
    ax_price.plot(win["open_time_utc"], win["ema50"], color="#64b5f6", linewidth=1.1, label="EMA50")

    vol_colors = [up_color if flag else down_color for flag in up]
    ax_vol.bar(win["open_time_utc"], win["volume"], width=width, color=vol_colors, alpha=0.85)

    entry_idx = (win["open_time_utc"] - entry_time).abs().idxmin()
    entry_row = win.loc[entry_idx]
    marker = "^" if side > 0 else "v"
    marker_color = "#00e676" if side > 0 else "#ff1744"
    ax_price.scatter(
        [entry_time],
        [entry_row["close"]],
        color=marker_color,
        marker=marker,
        s=170,
        linewidths=0.8,
        edgecolors="#ffffff",
        zorder=5,
        label="Entry",
    )

    title = f"{symbol} {timeframe} minute-stage final review | entry point"
    ax_price.set_title(title, color="white", fontsize=14, pad=10)
    ax_price.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    for ax in (ax_price, ax_vol):
        ax.grid(color="#2f3a40", alpha=0.45, linewidth=0.6)
        ax.tick_params(colors="#e0e0e0")
        for spine in ax.spines.values():
            spine.set_color("#3a444b")
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax_price.legend(facecolor="#172026", edgecolor="#3a444b", labelcolor="white", fontsize=9, loc="upper left")
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig(out_png, dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render final minute-stage visual summary with entry point.")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--pipeline-report", default=None)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    report_path = Path(args.pipeline_report) if args.pipeline_report else _latest(
        f"reports/pipeline/pipeline_report_{args.symbol}_{args.timeframe}_*.json", project_root
    )
    if report_path is None or not report_path.exists():
        raise FileNotFoundError("No pipeline report found for final minute summary.")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    backtest_path = Path(report["artifacts"]["backtest_path"])
    bt = pd.read_csv(backtest_path)
    bt["open_time_utc"] = pd.to_datetime(bt["open_time_utc"], utc=True)
    trades = bt[bt["side"] != 0].copy()
    if trades.empty:
        raise RuntimeError("No entry points found in backtest (trades=0).")

    best = trades.sort_values("net_return", ascending=False).iloc[0]
    entry_time = best["open_time_utc"]
    entry_day = entry_time.strftime("%Y-%m-%d")

    raw_path = _load_latest_raw(project_root, entry_day, args.timeframe, args.symbol)
    raw = pd.read_csv(raw_path)
    raw["open_time_utc"] = pd.to_datetime(raw["open_time_utc"], utc=True)

    out_dir = project_root / "reports" / "final_review"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_png = out_dir / f"minute_final_entry_{args.symbol}_{args.timeframe}_{ts}.png"
    out_json = out_dir / f"minute_final_summary_{args.symbol}_{args.timeframe}_{ts}.json"
    out_md = out_dir / f"minute_final_summary_{args.symbol}_{args.timeframe}_{ts}.md"

    _build_visual(
        raw_df=raw,
        entry_time=entry_time,
        side=int(best["side"]),
        out_png=out_png,
        symbol=args.symbol,
        timeframe=args.timeframe,
    )

    strategy = report.get("strategy", {})
    summary = {
        "pipeline_report_path": str(report_path),
        "symbol": report.get("symbol"),
        "timeframe": report.get("timeframe"),
        "date_range": report.get("date_range", {}),
        "gate": report.get("gate", {}),
        "walk_forward": report.get("walk_forward", {}),
        "backtest": report.get("backtest", {}),
        "risk_policy": report.get("risk_policy", {}),
        "strategy": strategy,
        "best_entry_point": {
            "open_time_utc": entry_time.isoformat(),
            "side": "long" if int(best["side"]) > 0 else "short",
            "prob_up": float(best["prob_up"]),
            "future_return": float(best["future_return"]),
            "net_return": float(best["net_return"]),
        },
        "visual_png": str(out_png),
    }
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md = []
    md.append("# Minute Stage Final Result")
    md.append("")
    md.append(f"- Symbol: `{summary['symbol']}`")
    md.append(f"- Timeframe: `{summary['timeframe']}`")
    md.append(f"- Window: `{summary['date_range'].get('start')} -> {summary['date_range'].get('end')}`")
    md.append(f"- Gate pass: `{summary['gate'].get('pass')}`")
    md.append("")
    md.append("## Strategy")
    md.append(
        f"- Type: `{strategy.get('type', 'probability_threshold_long_short')}`; long if `prob_up >= {strategy.get('p_enter_long')}`, "
        f"short if `prob_up <= {strategy.get('p_enter_short')}`"
    )
    md.append(f"- Horizon bars: `{strategy.get('horizon_bars')}`")
    md.append(
        f"- Costs: fee `{strategy.get('fee_bps')}` bps + slippage `{strategy.get('slippage_bps')}` bps"
    )
    md.append("")
    md.append("## Backtest Snapshot")
    bt_s = summary["backtest"]
    md.append(f"- Trades: `{bt_s.get('trades')}`")
    md.append(f"- Hit rate: `{bt_s.get('hit_rate')}`")
    md.append(f"- Net return pct: `{bt_s.get('net_return_pct')}`")
    md.append(f"- Max drawdown pct: `{bt_s.get('max_drawdown_pct')}`")
    md.append(f"- No trade ratio days: `{bt_s.get('no_trade_ratio_days')}`")
    md.append("")
    md.append("## Best Entry Point")
    ep = summary["best_entry_point"]
    md.append(f"- Time: `{ep.get('open_time_utc')}`")
    md.append(f"- Side: `{ep.get('side')}`")
    md.append(f"- Probability up: `{ep.get('prob_up')}`")
    md.append(f"- Net return on horizon: `{ep.get('net_return')}`")
    md.append("")
    md.append(f"- Visual screenshot: `{out_png}`")
    out_md.write_text("\n".join(md), encoding="utf-8")

    print(
        json.dumps(
            {"summary_json": str(out_json), "summary_md": str(out_md), "visual_png": str(out_png)},
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
