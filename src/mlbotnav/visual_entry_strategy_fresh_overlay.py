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

from mlbotnav.visual_entry_no_lookahead_candidates import _prepare_rows
from mlbotnav.visual_entry_quality_filter_runner import _enrich_quality_rows
from mlbotnav.visual_entry_reversal_bottom_knife_drop_runner import _low_zone, _value
from mlbotnav.visual_entry_score import TradeEntry, load_manual_entries, score_entries


STATUS = "DEV_STRATEGY_FRESH_OVERLAY_ENTRY_ONLY_NO_CALIBRATION"
SLIPPAGE_BPS = 5.0

STRATEGIES: list[dict[str, Any]] = [
    {
        "strategy_id": "S01_SUPPORT_RETEST_LOW",
        "color": "#00e5ff",
        "threshold": 10,
        "description_ru": "Ретест поддержки у low.",
    },
    {
        "strategy_id": "S02_TREND_DIP_LOW",
        "color": "#00e676",
        "threshold": 10,
        "description_ru": "Локальный dip в живом движении.",
    },
    {
        "strategy_id": "S03_DEEP_KNIFE_LOW",
        "color": "#b388ff",
        "threshold": 9,
        "description_ru": "Глубокий провал/нож у low.",
    },
    {
        "strategy_id": "S04_HOT_CONTINUATION_LOW",
        "color": "#ffd54f",
        "threshold": 10,
        "description_ru": "Горячий continuation-low без требования холодных осцилляторов.",
    },
]


def _bar_width_days(tf: str) -> float:
    if tf.endswith("m"):
        return (int(tf[:-1]) / (24 * 60)) * 0.8
    return (1 / (24 * 60)) * 0.8


def _format_time(ts: pd.Timestamp) -> str:
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def _score_strategy(row: dict[str, Any], strategy_id: str) -> tuple[int, list[str]]:
    score = 0
    votes: list[str] = []
    low_zone = _low_zone(row)
    touch = _value(row, "support_touch_count_60", 0.0)
    wick = _value(row, "lower_wick_share", 0.0)
    closepos = _value(row, "close_pos_candle", 0.0)
    ret6 = _value(row, "ret_6_pct", 0.0)
    ret12 = _value(row, "ret_12_pct", 0.0)
    ret24 = _value(row, "ret_24_pct", 0.0)
    rsi = _value(row, "rsi14", 999.0)
    slope = _value(row, "ema20_slope_5_pct", -999.0)
    local5 = bool(row.get("local_low_5"))
    local10 = bool(row.get("local_low_10"))
    local20 = bool(row.get("local_low_20"))

    if strategy_id == "S01_SUPPORT_RETEST_LOW":
        if touch >= 24:
            score += 3
            votes.append("support_touch_60>=24")
        if low_zone <= 0.60:
            score += 2
            votes.append("low_zone<=0.60")
        if local5 or local10:
            score += 2
            votes.append("local_low_5_or_10")
        if wick >= 0.20:
            score += 1
            votes.append("lower_wick>=0.20")
        if closepos >= 0.45:
            score += 1
            votes.append("close_reclaim>=0.45")
        if ret12 <= 0.50 and rsi <= 90:
            score += 1
            votes.append("not_overextended")
    elif strategy_id == "S02_TREND_DIP_LOW":
        if slope >= -0.02:
            score += 2
            votes.append("ema20_slope_alive")
        if touch >= 24:
            score += 2
            votes.append("support_touch_60>=24")
        if ret6 <= 0.20:
            score += 1
            votes.append("ret6_not_extended")
        if local5 or wick >= 0.10 or closepos >= 0.20:
            score += 2
            votes.append("dip_trigger")
        if low_zone <= 0.70:
            score += 1
            votes.append("low_zone<=0.70")
        if rsi <= 90:
            score += 1
            votes.append("rsi_allowed")
        if local10:
            score += 1
            votes.append("local_low_10")
    elif strategy_id == "S03_DEEP_KNIFE_LOW":
        if low_zone <= 0.35:
            score += 3
            votes.append("deep_low_zone")
        if ret12 <= -0.10 or ret24 <= -0.30:
            score += 2
            votes.append("drop_context")
        if local5:
            score += 2
            votes.append("local_low_5")
        if local20:
            score += 1
            votes.append("local_low_20")
        if wick >= 0.10 or closepos >= 0.20:
            score += 1
            votes.append("weak_reclaim")
        if rsi <= 70:
            score += 1
            votes.append("rsi_not_hot")
    elif strategy_id == "S04_HOT_CONTINUATION_LOW":
        if touch >= 32:
            score += 3
            votes.append("dense_support>=32")
        if slope >= 0.0:
            score += 2
            votes.append("ema20_slope_positive")
        if wick >= 0.20 or closepos >= 0.45:
            score += 2
            votes.append("hot_reclaim")
        if ret6 <= 0.18:
            score += 1
            votes.append("ret6_not_extended")
        if rsi <= 92 and low_zone <= 0.90:
            score += 1
            votes.append("hot_allowed")
        if local5 or local10:
            score += 1
            votes.append("local_low")
    return score, votes


def _candidate_to_trade(candidate: dict[str, Any]) -> TradeEntry:
    return TradeEntry(
        row_index=int(candidate["entry_row_index"]),
        side="long",
        entry_time=datetime.fromisoformat(str(candidate["entry_time_utc"]).replace("Z", "+00:00")),
        exit_time_raw="",
        net_return=0.0,
        mae_pct=None,
        mfe_pct=None,
    )


def _collect_candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    strategy_by_id = {item["strategy_id"]: item for item in STRATEGIES}
    for signal_idx in range(60, len(rows) - 1):
        signal = rows[signal_idx]
        entry = rows[signal_idx + 1]
        for strategy in STRATEGIES:
            score, votes = _score_strategy(signal, str(strategy["strategy_id"]))
            if score < int(strategy["threshold"]):
                continue
            entry_open = float(entry["open"])
            candidates.append(
                {
                    "strategy_id": strategy["strategy_id"],
                    "family_id": strategy["strategy_id"],
                    "bucket": strategy["strategy_id"],
                    "color": strategy_by_id[strategy["strategy_id"]]["color"],
                    "side": "long",
                    "signal_row_index": signal_idx,
                    "entry_row_index": signal_idx + 1,
                    "signal_time_utc": signal["open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "entry_time_utc": entry["open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "entry_open_price": entry_open,
                    "entry_price_with_slippage": entry_open * (1.0 + SLIPPAGE_BPS / 10000.0),
                    "slippage_bps": SLIPPAGE_BPS,
                    "entry_rule": "next_bar_open_after_signal_close",
                    "strategy_scope": "entry_only_low_detection",
                    "lookahead": "NO",
                    "priority_score": score,
                    "context_votes": votes,
                    "trigger_votes": ["FRESH_OVERLAY_DEFAULT_NO_CALIBRATION"],
                    "debug": {
                        "low_zone": _low_zone(signal),
                        "support_touch_count_60": _value(signal, "support_touch_count_60", 0.0),
                        "ret_6_pct": _value(signal, "ret_6_pct", 0.0),
                        "ret_12_pct": _value(signal, "ret_12_pct", 0.0),
                        "ret_24_pct": _value(signal, "ret_24_pct", 0.0),
                        "rsi14": _value(signal, "rsi14", 0.0),
                        "lower_wick_share": _value(signal, "lower_wick_share", 0.0),
                        "close_pos_candle": _value(signal, "close_pos_candle", 0.0),
                        "ema20_slope_5_pct": _value(signal, "ema20_slope_5_pct", 0.0),
                    },
                }
            )
    return candidates


def _load_df(source_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(source_csv)
    df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], utc=True, errors="coerce")
    df = df.dropna(subset=["open_time_utc"]).sort_values("open_time_utc").reset_index(drop=True)
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    return df


def _render(
    *,
    manual_entries_path: Path,
    candidates: list[dict[str, Any]],
    out_dir: Path,
    label: str,
) -> Path:
    manual_payload, manual_entries = load_manual_entries(manual_entries_path)
    source = manual_payload["source_images"][0]
    source_csv = Path(source["source_csv"])
    symbol = str(manual_payload.get("symbol", "SOLUSDT"))
    timeframe = str(manual_payload.get("timeframe", "1m"))
    day = str(source.get("date_utc", ""))
    df = _load_df(source_csv)

    score = score_entries(manual_entries, [_candidate_to_trade(item) for item in candidates])
    hit_times = {item["matched_entry_time_utc"] for item in score["hit_details"]}
    false_times = {item["entry_time_utc"] for item in score["false_entry_details"]}
    manual_hit_ids = {item["manual_entry_id"] for item in score["hit_details"]}

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

    width = _bar_width_days(timeframe)
    x = mdates.date2num(df["open_time_utc"].to_numpy())
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
        ax_price.add_patch(Rectangle((x[i] - width / 2, lower), width, height, facecolor=color, edgecolor=color, linewidth=0.45, alpha=0.95))
    ax_price.plot(df["open_time_utc"], df["ema20"], color="#ffd54f", linewidth=1.0, label="EMA20")
    ax_price.plot(df["open_time_utc"], df["ema50"], color="#64b5f6", linewidth=1.0, label="EMA50")
    vol_colors = [up_color if close_px >= open_px else down_color for open_px, close_px in zip(df["open"], df["close"])]
    ax_vol.bar(df["open_time_utc"], df["volume"], width=width, color=vol_colors, alpha=0.75)

    time_index = {_format_time(ts): i for i, ts in enumerate(df["open_time_utc"])}
    price_span = max(float(df["high"].max() - df["low"].min()), 1e-6)
    y_offset = price_span * 0.030
    manual_raw_by_id = {str(item.get("entry_id")): item for item in manual_payload.get("entries", [])}
    for manual in manual_entries:
        raw = manual_raw_by_id.get(manual.entry_id, {})
        entry_key = manual.target_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        idx = time_index.get(entry_key)
        if idx is None:
            continue
        color = "#ff1744" if manual.entry_id not in manual_hit_ids else "#00e676"
        ts = df.iloc[idx]["open_time_utc"]
        entry_open = float(raw.get("entry_open_price") or df.iloc[idx]["open"])
        entry_number = raw.get("entry_number") or manual.entry_id.rsplit("_", 1)[-1]
        ax_price.scatter([ts], [entry_open - y_offset * 0.15], marker="^", s=110, facecolors="none", edgecolors=color, linewidths=2.0, zorder=14)
        ax_price.text(ts, entry_open - y_offset * 0.55, f"M{entry_number}", color=color, fontsize=8, ha="center", va="top", zorder=15)

    marker_by_strategy = {
        "S01_SUPPORT_RETEST_LOW": "o",
        "S02_TREND_DIP_LOW": "s",
        "S03_DEEP_KNIFE_LOW": "D",
        "S04_HOT_CONTINUATION_LOW": "P",
    }
    for candidate in candidates:
        key = str(candidate["entry_time_utc"])
        idx = time_index.get(key)
        if idx is None:
            continue
        row = df.iloc[idx]
        ts = row["open_time_utc"]
        y = float(candidate["entry_open_price"])
        color = str(candidate["color"])
        edge = "#ffffff" if key in false_times else "#000000"
        size = 42 if key not in hit_times else 90
        zorder = 9 if key not in hit_times else 16
        ax_price.scatter([ts], [y], marker=marker_by_strategy.get(str(candidate["strategy_id"]), "."), s=size, color=color, edgecolors=edge, linewidths=0.6, alpha=0.86, zorder=zorder)
        if key in hit_times:
            ax_price.text(ts, y + y_offset * 0.30, "H", color=color, fontsize=8, ha="center", va="bottom", zorder=17)

    for strategy in STRATEGIES:
        ax_price.scatter([], [], marker=marker_by_strategy[strategy["strategy_id"]], s=55, color=strategy["color"], label=strategy["strategy_id"])

    score_text = (
        f"fresh default strategies | hits={score['target_hits']}/{score['targets_total']} "
        f"false={score['false_entries']} entries={score['entries_total']} "
        f"lookahead=NO no_cooldown no_calibration entry_only"
    )
    ax_price.set_title(f"{symbol} {timeframe} {day} UTC | clean fresh strategy overlay\n{score_text}", color="white", fontsize=13, pad=10)
    ax_price.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    for ax in (ax_price, ax_vol):
        ax.grid(color="#2f3a40", alpha=0.45, linewidth=0.6)
        ax.tick_params(colors="#e0e0e0")
        for spine in ax.spines.values():
            spine.set_color("#3a444b")
    ax_price.legend(facecolor="#172026", edgecolor="#3a444b", labelcolor="white", fontsize=8, loc="upper left", ncol=3)
    fig.autofmt_xdate()
    plt.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    safe_label = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in label.lower())
    ts_now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    png_path = out_dir / f"visual_entry_fresh_strategy_overlay_{day}_{safe_label}_{ts_now}.png"
    plt.savefig(png_path, dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)
    return png_path


def run_overlay(manual_entries_path: Path, out_dir: Path, *, label: str = "default4") -> dict[str, Any]:
    manual_payload, manual_entries = load_manual_entries(manual_entries_path)
    _, rows = _prepare_rows(manual_entries_path)
    _enrich_quality_rows(rows)
    all_candidates = _collect_candidates(rows)

    by_strategy: list[dict[str, Any]] = []
    for strategy in STRATEGIES:
        strategy_candidates = [item for item in all_candidates if item["strategy_id"] == strategy["strategy_id"]]
        score = score_entries(manual_entries, [_candidate_to_trade(item) for item in strategy_candidates])
        by_strategy.append(
            {
                "strategy_id": strategy["strategy_id"],
                "description_ru": strategy["description_ru"],
                "threshold": strategy["threshold"],
                "candidates_total": len(strategy_candidates),
                "score": {
                    key: score[key]
                    for key in [
                        "targets_total",
                        "target_hits",
                        "missed_targets",
                        "false_entries",
                        "entries_total",
                        "precision",
                        "recall",
                        "f1_visual",
                    ]
                },
            }
        )

    png_path = _render(
        manual_entries_path=manual_entries_path,
        candidates=all_candidates,
        out_dir=out_dir,
        label=label,
    )
    rendered_overlays: list[dict[str, str]] = [{"strategy_id": "ALL_DEFAULT4", "visual_png": str(png_path)}]
    for strategy in STRATEGIES:
        strategy_candidates = [item for item in all_candidates if item["strategy_id"] == strategy["strategy_id"]]
        strategy_png = _render(
            manual_entries_path=manual_entries_path,
            candidates=strategy_candidates,
            out_dir=out_dir,
            label=f"{label}_{strategy['strategy_id'].lower()}",
        )
        rendered_overlays.append({"strategy_id": str(strategy["strategy_id"]), "visual_png": str(strategy_png)})

    score_all = score_entries(manual_entries, [_candidate_to_trade(item) for item in all_candidates])
    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "manual_entries": str(manual_entries_path),
        "source_csv": str(manual_payload["source_images"][0]["source_csv"]),
        "strategy_scope": "entry_only_low_detection",
        "calibration_used": False,
        "cooldown_used": False,
        "future_trade_outcome_used": False,
        "ml_transfer_allowed": False,
        "strategies": by_strategy,
        "combined_score": {
            key: score_all[key]
            for key in [
                "targets_total",
                "target_hits",
                "missed_targets",
                "false_entries",
                "entries_total",
                "precision",
                "recall",
                "f1_visual",
            ]
        },
        "visual_png": str(png_path),
        "rendered_overlays": rendered_overlays,
        "candidates_total": len(all_candidates),
    }
    day = str(manual_payload["source_images"][0].get("date_utc", "")).replace("-", "")
    role = str(manual_payload.get("dataset_role", "DEV")).upper()
    safe_role = "".join(ch if ch.isalnum() else "_" for ch in role).strip("_")
    json_path = out_dir / f"visual_entry_fresh_strategy_overlay_{day}_{safe_role}.json"
    md_path = out_dir / f"visual_entry_fresh_strategy_overlay_{day}_{safe_role}_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_lines = [
        "# Fresh Strategy Overlay",
        "",
        f"Статус: `{STATUS}`.",
        "",
        f"Combined PNG: `{png_path}`.",
        "",
        "Это чистый свежий overlay без старых стрелок/каши: 4 базовые стратегии наложены дефолтно, без cooldown и без калибровки.",
        "",
        "| strategy | hits | false | entries | precision | recall | f1 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in by_strategy:
        s = item["score"]
        md_lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{:.4f}` | `{:.4f}` | `{:.4f}` |".format(
                item["strategy_id"],
                s["target_hits"],
                s["false_entries"],
                s["entries_total"],
                s["precision"],
                s["recall"],
                s["f1_visual"],
            )
        )
    md_lines.extend(["", "## PNG", ""])
    for item in rendered_overlays:
        md_lines.append(f"- `{item['strategy_id']}`: `{item['visual_png']}`")
    s = payload["combined_score"]
    md_lines.extend(
        [
            "",
            "Combined:",
            "",
            f"- hits: `{s['target_hits']}/{s['targets_total']}`",
            f"- false: `{s['false_entries']}`",
            f"- entries: `{s['entries_total']}`",
            "",
            "В ML не передавать. Следующий шаг - смотреть PNG глазами и калибровать только живые стратегии.",
            "",
        ]
    )
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render clean fresh entry-strategy overlays without calibration.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/fresh_strategy_overlay")
    parser.add_argument("--label", default="default4")
    args = parser.parse_args(argv)
    payload = run_overlay(Path(args.manual_entries), Path(args.out_dir), label=str(args.label))
    print(
        json.dumps(
            {
                "status": payload["status"],
                "visual_png": payload["visual_png"],
                "json_path": payload["json_path"],
                "md_path": payload["md_path"],
                "combined_score": payload["combined_score"],
                "strategies": payload["strategies"],
                "ml_transfer_allowed": payload["ml_transfer_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
