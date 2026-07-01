from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

from mlbotnav.visual_entry_feature_audit import _read_core_csv, enrich_rows
from mlbotnav.visual_entry_prefilter_search import _signals_for_params
from mlbotnav.visual_entry_score import (
    TradeEntry,
    load_manual_entries,
    load_trade_entries,
    score_entries,
)


def _bar_width_days(tf: str) -> float:
    if tf.endswith("m"):
        return (int(tf[:-1]) / (24 * 60)) * 0.8
    if tf.endswith("h"):
        return (int(tf[:-1]) * 60 / (24 * 60)) * 0.8
    if tf.endswith("d"):
        return int(tf[:-1]) * 0.8
    return (1 / (24 * 60)) * 0.8


def _format_time(value: pd.Timestamp) -> str:
    return value.strftime("%H:%M")


def _load_core_dataframe(source_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(source_csv)
    df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], utc=True, errors="coerce")
    df = df.dropna(subset=["open_time_utc"]).sort_values("open_time_utc").reset_index(drop=True)
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    return df


def _parse_utc(value: Any) -> pd.Timestamp:
    return pd.to_datetime(str(value), utc=True, errors="coerce")


def _time_key(value: Any) -> str:
    ts = _parse_utc(value)
    if pd.isna(ts):
        return ""
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def _candidate_trades_from_result(result: dict[str, Any]) -> list[TradeEntry]:
    details = result.get("signals") or result.get("first_signals") or []
    trades: list[TradeEntry] = []
    for index, item in enumerate(details, 1):
        entry_ts = _parse_utc(item.get("entry_time_utc"))
        if pd.isna(entry_ts):
            continue
        trades.append(
            TradeEntry(
                row_index=int(item.get("entry_row_index") or index),
                side=str(item.get("side") or "long"),
                entry_time=entry_ts.to_pydatetime(),
                exit_time_raw="",
                net_return=float(item.get("net_return") or 0.0),
                mae_pct=None,
                mfe_pct=None,
            )
        )
    return sorted(trades, key=lambda item: item.entry_time)


def _load_prefilter_trades(prefilter_json: Path, top_index: int, manual_entries_path: Path) -> list[TradeEntry]:
    payload = json.loads(prefilter_json.read_text(encoding="utf-8"))
    try:
        params = payload["top_results"][top_index]["params"]
    except IndexError as exc:
        raise ValueError(f"top_index out of range: {top_index}") from exc
    manual_payload = json.loads(manual_entries_path.read_text(encoding="utf-8"))
    rows = _read_core_csv(Path(manual_payload["source_images"][0]["source_csv"]))
    enrich_rows(rows)
    trades, _ = _signals_for_params(rows, params)
    return trades


def _side_price(row: pd.Series, side: str) -> float:
    if side == "long":
        return float(row["low"])
    return float(row["high"])


def render_overlay(
    *,
    manual_entries_path: Path,
    trades: list[TradeEntry],
    label: str,
    out_dir: Path,
) -> tuple[Path, Path]:
    manual_payload, manual_entries = load_manual_entries(manual_entries_path)
    source = manual_payload["source_images"][0]
    source_csv = Path(source["source_csv"])
    symbol = str(manual_payload.get("symbol", "SOLUSDT"))
    timeframe = str(manual_payload.get("timeframe", "1m"))
    df = _load_core_dataframe(source_csv)
    score = score_entries(manual_entries, trades)

    hit_times = {item["matched_entry_time_utc"] for item in score["hit_details"]}
    false_times = {item["entry_time_utc"] for item in score["false_entry_details"]}

    bg = "#101418"
    fig, (ax_price, ax_vol) = plt.subplots(
        2,
        1,
        figsize=(22, 10.5),
        sharex=True,
        gridspec_kw={"height_ratios": [4.2, 1.2]},
    )
    fig.patch.set_facecolor(bg)
    ax_price.set_facecolor(bg)
    ax_vol.set_facecolor(bg)

    x = mdates.date2num(df["open_time_utc"].to_numpy())
    width = _bar_width_days(timeframe)
    up_color = "#26a69a"
    down_color = "#ef5350"
    wick_color = "#cfd8dc"

    ax_price.vlines(x, df["low"], df["high"], color=wick_color, linewidth=0.65, alpha=0.85, zorder=1)
    for i, row in df.iterrows():
        open_px = float(row["open"])
        close_px = float(row["close"])
        lower = min(open_px, close_px)
        height = max(abs(close_px - open_px), 1e-8)
        color = up_color if close_px >= open_px else down_color
        ax_price.add_patch(
            Rectangle(
                (x[i] - width / 2, lower),
                width,
                height,
                facecolor=color,
                edgecolor=color,
                linewidth=0.45,
                alpha=0.95,
            )
        )
    ax_price.plot(df["open_time_utc"], df["ema20"], color="#ffd54f", linewidth=1.0, label="EMA20")
    ax_price.plot(df["open_time_utc"], df["ema50"], color="#64b5f6", linewidth=1.0, label="EMA50")
    vol_colors = [up_color if close_px >= open_px else down_color for open_px, close_px in zip(df["open"], df["close"])]
    ax_vol.bar(df["open_time_utc"], df["volume"], width=width, color=vol_colors, alpha=0.75)

    time_index = {pd.Timestamp(ts).strftime("%Y-%m-%dT%H:%M:%SZ"): i for i, ts in enumerate(df["open_time_utc"])}
    manual_hit_ids = {item["manual_entry_id"] for item in score["hit_details"]}
    for manual in manual_entries:
        ts = pd.Timestamp(manual.target_time)
        key = manual.target_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        idx = time_index.get(key)
        if idx is None:
            continue
        y = _side_price(df.iloc[idx], manual.side)
        color = "#ff1744" if manual.entry_id not in manual_hit_ids else "#00e676"
        ax_price.annotate(
            manual.target_time.strftime("%H:%M"),
            xy=(ts, y),
            xytext=(ts, y - 0.55),
            ha="center",
            va="top",
            color=color,
            fontsize=8,
            arrowprops={"arrowstyle": "-|>", "color": color, "linewidth": 2.0},
            zorder=8,
        )
        ax_price.axvspan(
            manual.window_start,
            manual.window_end,
            color=color,
            alpha=0.06,
            linewidth=0,
            zorder=0,
        )

    for trade in trades:
        ts = pd.Timestamp(trade.entry_time)
        key = trade.entry_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        idx = time_index.get(key)
        if idx is None:
            continue
        y = float(df.iloc[idx]["close"])
        if key in hit_times:
            ax_price.scatter([ts], [y], marker="^", s=76, color="#00e676", edgecolors="black", linewidths=0.7, zorder=9)
        elif key in false_times:
            ax_price.scatter([ts], [y], marker="X", s=86, color="#ff1744", edgecolors="white", linewidths=0.9, zorder=10)
        else:
            ax_price.scatter([ts], [y], marker=".", s=20, color="#b0bec5", zorder=5)

    score_text = (
        f"hits={score['target_hits']}/{score['targets_total']}  "
        f"false={score['false_entries']}  entries={score['entries_total']}  "
        f"precision={score['precision']:.3f}  recall={score['recall']:.3f}  f1={score['f1_visual']:.3f}"
    )
    day = str(source.get("date_utc", ""))
    ax_price.set_title(
        f"{symbol} {timeframe} {day} UTC | visual overlay | {label}\n{score_text}",
        color="white",
        fontsize=13,
        pad=10,
    )
    ax_price.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    for ax in (ax_price, ax_vol):
        ax.grid(color="#2f3a40", alpha=0.45, linewidth=0.6)
        ax.tick_params(colors="#e0e0e0")
        for spine in ax.spines.values():
            spine.set_color("#3a444b")
    ax_price.legend(facecolor="#172026", edgecolor="#3a444b", labelcolor="white", fontsize=9, loc="upper left", ncol=3)
    fig.autofmt_xdate()
    plt.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    safe_label = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in label.lower())
    ts_now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    png_path = out_dir / f"visual_entry_overlay_{day}_{safe_label}_{ts_now}.png"
    json_path = out_dir / f"visual_entry_overlay_{day}_{safe_label}_{ts_now}.json"
    plt.savefig(png_path, dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)
    summary = {
        "label": label,
        "manual_entries": str(manual_entries_path),
        "source_csv": str(source_csv),
        "visual_png": str(png_path),
        "score": score,
    }
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return png_path, json_path


def render_family_candidate_overlay(
    *,
    manual_entries_path: Path,
    result: dict[str, Any],
    out_dir: Path,
    label: str,
    slippage_bps: float = 5.0,
) -> Path:
    manual_payload, manual_entries = load_manual_entries(manual_entries_path)
    source = manual_payload["source_images"][0]
    source_csv = Path(source["source_csv"])
    symbol = str(manual_payload.get("symbol", "SOLUSDT"))
    timeframe = str(manual_payload.get("timeframe", "1m"))
    df = _load_core_dataframe(source_csv)
    candidate_trades = _candidate_trades_from_result(result)
    score = score_entries(manual_entries, candidate_trades)

    hit_manual_ids = {item["manual_entry_id"] for item in score["hit_details"]}
    missed_manual_ids = {item["manual_entry_id"] for item in score["missed_target_details"]}
    hit_entry_times = {item["matched_entry_time_utc"] for item in score["hit_details"]}
    false_entry_times = {item["entry_time_utc"] for item in score["false_entry_details"]}

    bg = "#101418"
    fig, (ax_price, ax_vol) = plt.subplots(
        2,
        1,
        figsize=(22, 10.8),
        sharex=True,
        gridspec_kw={"height_ratios": [4.2, 1.2]},
    )
    fig.patch.set_facecolor(bg)
    ax_price.set_facecolor(bg)
    ax_vol.set_facecolor(bg)

    x = mdates.date2num(df["open_time_utc"].to_numpy())
    width = _bar_width_days(timeframe)
    up_color = "#26a69a"
    down_color = "#ef5350"
    wick_color = "#cfd8dc"
    ax_price.vlines(x, df["low"], df["high"], color=wick_color, linewidth=0.65, alpha=0.85, zorder=1)
    for i, row in df.iterrows():
        open_px = float(row["open"])
        close_px = float(row["close"])
        lower = min(open_px, close_px)
        height = max(abs(close_px - open_px), 1e-8)
        color = up_color if close_px >= open_px else down_color
        ax_price.add_patch(
            Rectangle(
                (x[i] - width / 2, lower),
                width,
                height,
                facecolor=color,
                edgecolor=color,
                linewidth=0.45,
                alpha=0.95,
            )
        )
    ax_price.plot(df["open_time_utc"], df["ema20"], color="#ffd54f", linewidth=1.0, label="EMA20")
    ax_price.plot(df["open_time_utc"], df["ema50"], color="#64b5f6", linewidth=1.0, label="EMA50")
    vol_colors = [up_color if close_px >= open_px else down_color for open_px, close_px in zip(df["open"], df["close"])]
    ax_vol.bar(df["open_time_utc"], df["volume"], width=width, color=vol_colors, alpha=0.75)

    time_index = {_time_key(ts): i for i, ts in enumerate(df["open_time_utc"])}
    price_span = max(float(df["high"].max() - df["low"].min()), 1e-6)
    y_offset = price_span * 0.028
    manual_raw_by_id = {str(item.get("entry_id")): item for item in manual_payload.get("entries", [])}

    for manual in manual_entries:
        raw = manual_raw_by_id.get(manual.entry_id, {})
        entry_key = manual.target_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        entry_idx = time_index.get(entry_key)
        if entry_idx is None:
            continue
        signal_key = _time_key(raw.get("signal_candle_time_utc"))
        signal_idx = time_index.get(signal_key)
        entry_number = raw.get("entry_number") or manual.entry_id.rsplit("_", 1)[-1]
        is_hit = manual.entry_id in hit_manual_ids
        is_miss = manual.entry_id in missed_manual_ids
        color = "#00e676" if is_hit else "#ffb300" if is_miss else "#eceff1"
        entry_open = float(raw.get("entry_open_price") or df.iloc[entry_idx]["open"])
        slip_price = float(raw.get("entry_price_with_slippage") or (entry_open * (1.0 + slippage_bps / 10000.0)))

        if signal_idx is not None:
            signal_ts = df.iloc[signal_idx]["open_time_utc"]
            signal_y = float(df.iloc[signal_idx]["low"]) - y_offset * 0.25
            ax_price.scatter([signal_ts], [signal_y], marker="o", s=54, color=color, edgecolors="black", linewidths=0.7, zorder=8)
            ax_price.text(signal_ts, signal_y - y_offset * 0.35, f"S{entry_number}", color=color, fontsize=8, ha="center", va="top", zorder=9)

        entry_ts = df.iloc[entry_idx]["open_time_utc"]
        entry_y = entry_open - y_offset * 0.10
        ax_price.scatter([entry_ts], [entry_y], marker="^", s=78, facecolors="none", edgecolors=color, linewidths=1.7, zorder=9)
        ax_price.text(entry_ts, entry_y - y_offset * 0.42, f"E{entry_number}", color=color, fontsize=8, ha="center", va="top", zorder=10)
        ax_price.annotate(
            f"S{entry_number}->E{entry_number} open={entry_open:.4f} slip={slip_price:.4f}",
            xy=(entry_ts, entry_y),
            xytext=(entry_ts, entry_y - y_offset * 1.25),
            ha="center",
            va="top",
            color=color,
            fontsize=7,
            arrowprops={"arrowstyle": "-", "color": color, "linewidth": 0.8, "alpha": 0.75},
            zorder=7,
        )

    for detail in result.get("signals") or result.get("first_signals") or []:
        signal_key = _time_key(detail.get("signal_time_utc"))
        entry_key = _time_key(detail.get("entry_time_utc"))
        signal_idx = time_index.get(signal_key)
        entry_idx = time_index.get(entry_key)
        if signal_idx is not None:
            signal_ts = df.iloc[signal_idx]["open_time_utc"]
            signal_y = float(df.iloc[signal_idx]["low"]) - y_offset * 0.80
            ax_price.scatter([signal_ts], [signal_y], marker="D", s=42, color="#00e5ff", edgecolors="black", linewidths=0.55, zorder=11)
            ax_price.text(signal_ts, signal_y - y_offset * 0.35, "CS", color="#00e5ff", fontsize=7, ha="center", va="top", zorder=12)
        if entry_idx is None:
            continue
        entry_ts = df.iloc[entry_idx]["open_time_utc"]
        entry_y = float(detail.get("entry_open_price") or df.iloc[entry_idx]["open"])
        if entry_key in hit_entry_times:
            ax_price.scatter([entry_ts], [entry_y], marker="^", s=98, color="#00e676", edgecolors="black", linewidths=0.9, zorder=13)
            ax_price.text(entry_ts, entry_y + y_offset * 0.32, "H", color="#00e676", fontsize=8, ha="center", va="bottom", zorder=14)
        elif entry_key in false_entry_times:
            ax_price.scatter([entry_ts], [entry_y], marker="X", s=112, color="#ff1744", edgecolors="white", linewidths=1.0, zorder=14)
            ax_price.text(entry_ts, entry_y + y_offset * 0.34, "FALSE", color="#ff1744", fontsize=7, ha="center", va="bottom", zorder=15)
        else:
            ax_price.scatter([entry_ts], [entry_y], marker="v", s=56, color="#b0bec5", edgecolors="black", linewidths=0.55, zorder=10)

    score_text = (
        f"hits={score['target_hits']}/{score['targets_total']}  miss={score['missed_targets']}  "
        f"false={score['false_entries']}  entries={score['entries_total']}  "
        f"precision={score['precision']:.3f}  recall={score['recall']:.3f}  f1={score['f1_visual']:.3f}  "
        f"lookahead=NO  slippage_bps={slippage_bps:g}"
    )
    day = str(source.get("date_utc", ""))
    family_id = str(result.get("family_id") or result.get("combo_id") or label)
    ax_price.set_title(
        f"{symbol} {timeframe} {day} UTC | visual family overlay | {family_id}\n{score_text}",
        color="white",
        fontsize=13,
        pad=10,
    )
    ax_price.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    for ax in (ax_price, ax_vol):
        ax.grid(color="#2f3a40", alpha=0.45, linewidth=0.6)
        ax.tick_params(colors="#e0e0e0")
        for spine in ax.spines.values():
            spine.set_color("#3a444b")
    ax_price.legend(facecolor="#172026", edgecolor="#3a444b", labelcolor="white", fontsize=9, loc="upper left", ncol=3)
    fig.autofmt_xdate()
    plt.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    safe_label = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in label.lower())
    ts_now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    png_path = out_dir / f"visual_entry_family_overlay_{day}_{safe_label}_{ts_now}.png"
    plt.savefig(png_path, dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)
    return png_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render manual visual entries against test entries.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--trades-csv")
    parser.add_argument("--prefilter-json")
    parser.add_argument("--top-index", type=int, default=0)
    parser.add_argument("--label", required=True)
    parser.add_argument("--out-dir", default="reports/final_review")
    args = parser.parse_args(argv)
    manual_entries_path = Path(args.manual_entries)
    if args.trades_csv:
        trades = load_trade_entries(args.trades_csv)
    elif args.prefilter_json:
        trades = _load_prefilter_trades(Path(args.prefilter_json), args.top_index, manual_entries_path)
    else:
        raise SystemExit("Provide --trades-csv or --prefilter-json")
    png_path, json_path = render_overlay(
        manual_entries_path=manual_entries_path,
        trades=trades,
        label=args.label,
        out_dir=Path(args.out_dir),
    )
    print(json.dumps({"status": "OK", "visual_png": str(png_path), "summary_json": str(json_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
