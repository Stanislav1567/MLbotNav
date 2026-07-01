from __future__ import annotations

import argparse
import itertools
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

from mlbotnav.visual_entry_feature_audit import _read_core_csv, enrich_rows
from mlbotnav.visual_entry_score import ManualEntry, TradeEntry, load_manual_entries, score_entries


def _safe_div(num: float, den: float) -> float | None:
    if den == 0:
        return None
    return num / den


def _compute_extra_features(rows: list[dict[str, Any]]) -> None:
    df = pd.DataFrame(rows)
    close = pd.to_numeric(df["close"], errors="coerce")
    high = pd.to_numeric(df["high"], errors="coerce")
    low = pd.to_numeric(df["low"], errors="coerce")
    volume = pd.to_numeric(df["volume"], errors="coerce")

    macd_line = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    macd_signal = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = macd_line - macd_signal
    typical = (high + low + close) / 3.0
    money_flow = typical * volume
    pos_flow = money_flow.where(typical.diff() > 0, 0.0)
    neg_flow = money_flow.where(typical.diff() < 0, 0.0).abs()
    mfr = pos_flow.rolling(14).sum() / neg_flow.rolling(14).sum().replace(0.0, pd.NA)
    mfi14 = 100.0 - (100.0 / (1.0 + mfr))

    for i, row in enumerate(rows):
        row["macd_line"] = float(macd_line.iloc[i]) if pd.notna(macd_line.iloc[i]) else None
        row["macd_signal"] = float(macd_signal.iloc[i]) if pd.notna(macd_signal.iloc[i]) else None
        row["macd_hist"] = float(macd_hist.iloc[i]) if pd.notna(macd_hist.iloc[i]) else None
        row["macd_hist_delta_3"] = float(macd_hist.iloc[i] - macd_hist.iloc[i - 3]) if i >= 3 and pd.notna(macd_hist.iloc[i]) and pd.notna(macd_hist.iloc[i - 3]) else None
        row["mfi14"] = float(mfi14.iloc[i]) if pd.notna(mfi14.iloc[i]) else None
        prev = rows[i - 1] if i > 0 else None
        if prev:
            prev_body = abs(float(prev["close"]) - float(prev["open"]))
            body = abs(float(row["close"]) - float(row["open"]))
            bullish = row["close"] > row["open"]
            prev_bear = prev["close"] < prev["open"]
            row["bullish_engulf_like"] = bool(
                bullish
                and prev_bear
                and row["close"] >= prev["open"]
                and row["open"] <= prev["close"]
                and body >= max(prev_body * 0.8, 1e-8)
            )
        else:
            row["bullish_engulf_like"] = False
        candle_range = float(row["high"]) - float(row["low"])
        body_abs = abs(float(row["close"]) - float(row["open"]))
        lower = min(float(row["open"]), float(row["close"])) - float(row["low"])
        upper = float(row["high"]) - max(float(row["open"]), float(row["close"]))
        row["hammer_like"] = bool(candle_range > 0 and lower / candle_range >= 0.45 and upper / candle_range <= 0.30 and body_abs / candle_range <= 0.45)


def _iter_grid() -> list[dict[str, Any]]:
    grid = {
        "context_min_votes": [3, 4],
        "trigger_min_votes": [1, 2],
        "ret12_max": [-0.15, -0.25, -0.40],
        "ret24_max": [-0.20, -0.40, -0.60],
        "range_pos_max": [0.25, 0.35, 0.50],
        "rsi_max": [35.0, 40.0, 45.0],
        "stoch_max": [35.0, 50.0],
        "vol_z_min": [0.5, 1.0],
        "cooldown_bars": [20, 45, 60],
        "require_green_entry": [True],
        "max_range_pos_for_suppression": [0.35, 0.50],
    }
    keys = list(grid)
    return [dict(zip(keys, values)) for values in itertools.product(*(grid[key] for key in keys))]


def _context_votes(signal: dict[str, Any], params: dict[str, Any]) -> list[str]:
    votes: list[str] = []
    if signal.get("ret_12_pct") is not None and signal["ret_12_pct"] <= params["ret12_max"]:
        votes.append("F004_RET12_DIP")
    if signal.get("ret_24_pct") is not None and signal["ret_24_pct"] <= params["ret24_max"]:
        votes.append("F005_RET24_DIP")
    if signal.get("range_pos_60") is not None and signal["range_pos_60"] <= params["range_pos_max"]:
        votes.append("F038_RANGEPOSE_LOW")
    if signal.get("rsi14") is not None and signal["rsi14"] <= params["rsi_max"]:
        votes.append("F012_RSI_COLD")
    if signal.get("stoch_k14") is not None and signal["stoch_k14"] <= params["stoch_max"]:
        votes.append("F017_F018_STOCH_LOW")
    if signal.get("ema20_slope_5_pct") is not None and signal["ema20_slope_5_pct"] < 0:
        votes.append("F010_EMASLOPE_DOWN")
    if signal.get("ema_gap_pct") is not None and signal["ema_gap_pct"] < 0:
        votes.append("F009_EMAGAP_DOWN")
    return votes


def _trigger_votes(signal: dict[str, Any], entry: dict[str, Any], params: dict[str, Any]) -> list[str]:
    votes: list[str] = []
    if entry.get("green_candle"):
        votes.append("GREEN_ENTRY_CANDLE")
    if entry["close"] > signal["close"]:
        votes.append("RECLAIM_SIGNAL_CLOSE")
    if signal.get("lower_wick_share") is not None and signal["lower_wick_share"] >= 0.40:
        votes.append("F055_F057_LOWER_WICK")
    if entry.get("bullish_engulf_like"):
        votes.append("F059_ENGULF_LIKE")
    if signal.get("hammer_like") or entry.get("hammer_like"):
        votes.append("F057_HAMMER_LIKE")
    if entry.get("macd_hist_delta_3") is not None and entry["macd_hist_delta_3"] > 0:
        votes.append("F015_MACD_HIST_RISING")
    if signal.get("vol_z20") is not None and signal["vol_z20"] >= params["vol_z_min"]:
        votes.append("F020_VOLZ_CONFIRM")
    return votes


def _passes_suppression(signal: dict[str, Any], entry: dict[str, Any], params: dict[str, Any]) -> bool:
    if params["require_green_entry"] and not entry.get("green_candle"):
        return False
    range_pos = signal.get("range_pos_60")
    if range_pos is not None and range_pos > params["max_range_pos_for_suppression"]:
        return False
    # Avoid chasing after too much immediate rebound from the local low.
    dist = signal.get("dist_from_low_60_pct")
    if dist is not None and dist > 0.75 and signal.get("ret_12_pct", 0.0) > -0.15:
        return False
    return True


def _signals_for_params(rows: list[dict[str, Any]], params: dict[str, Any]) -> tuple[list[TradeEntry], list[dict[str, Any]]]:
    trades: list[TradeEntry] = []
    details: list[dict[str, Any]] = []
    last_idx = -10_000
    for idx in range(60, len(rows) - 1):
        signal = rows[idx]
        entry = rows[idx + 1]
        context = _context_votes(signal, params)
        trigger = _trigger_votes(signal, entry, params)
        if len(context) < params["context_min_votes"] or len(trigger) < params["trigger_min_votes"]:
            continue
        if not _passes_suppression(signal, entry, params):
            continue
        if idx - last_idx < params["cooldown_bars"]:
            continue
        last_idx = idx
        entry_time = entry["open_time_utc"]
        trades.append(
            TradeEntry(
                row_index=idx + 1,
                side="long",
                entry_time=entry_time,
                exit_time_raw="",
                net_return=0.0,
                mae_pct=None,
                mfe_pct=None,
            )
        )
        details.append(
            {
                "signal_time_utc": signal["open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_time_utc": entry_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_open_price": float(entry["open"]),
                "context_votes": context,
                "trigger_votes": trigger,
            }
        )
    return trades, details


def _with_match_tolerance(manual_entries: list[ManualEntry], tolerance_bars: int) -> list[ManualEntry]:
    if tolerance_bars <= 0:
        return manual_entries
    return [
        ManualEntry(
            entry_id=item.entry_id,
            side=item.side,
            target_time=item.target_time,
            tolerance_before=max(item.tolerance_before, tolerance_bars),
            tolerance_after=max(item.tolerance_after, tolerance_bars),
        )
        for item in manual_entries
    ]


def search(manual_entries_path: Path, *, top_n: int = 30, match_tolerance_bars: int = 2) -> dict[str, Any]:
    manual_payload, manual_entries = load_manual_entries(manual_entries_path)
    scoring_entries = _with_match_tolerance(manual_entries, match_tolerance_bars)
    rows = _read_core_csv(Path(manual_payload["source_images"][0]["source_csv"]))
    enrich_rows(rows)
    _compute_extra_features(rows)
    results: list[dict[str, Any]] = []
    for params in _iter_grid():
        trades, details = _signals_for_params(rows, params)
        if not trades:
            continue
        score = score_entries(scoring_entries, trades)
        if score["target_hits"] <= 0:
            continue
        results.append(
            {
                "family_id": "REVERSAL_DIP_BUY_LONG_V0",
                "params": params,
                "score": {key: score[key] for key in [
                    "targets_total",
                    "target_hits",
                    "missed_targets",
                    "false_entries",
                    "entries_total",
                    "precision",
                    "recall",
                    "f1_visual",
                    "entry_lag_bars_avg",
                    "entry_lag_bars_abs_max",
                    "duplicate_hits",
                    "visual_status",
                ]},
                "hit_details": score["hit_details"],
                "missed_target_details": score["missed_target_details"],
                "false_entry_details": score["false_entry_details"][:30],
                "first_signals": details[:30],
            }
        )
    results.sort(
        key=lambda item: (
            item["score"]["f1_visual"],
            item["score"]["recall"],
            item["score"]["precision"],
            -item["score"]["false_entries"],
            -item["score"]["entries_total"],
        ),
        reverse=True,
    )
    return {
        "schema_version": 1,
        "status": "DEV_COMBO_DIAGNOSTIC_ONLY_NO_ML",
        "manual_entries": str(manual_entries_path),
        "match_tolerance_bars": int(match_tolerance_bars),
        "total_results_with_hits": len(results),
        "top_results": results[:top_n],
    }


def _load_core_df(source_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(source_csv)
    df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], utc=True, errors="coerce", format="mixed")
    df = df.dropna(subset=["open_time_utc"]).sort_values("open_time_utc").reset_index(drop=True)
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    return df


def render_simple_entry_arrows(
    *,
    manual_entries_path: Path,
    result: dict[str, Any],
    out_dir: Path,
    label: str,
    slippage_bps: float = 5.0,
) -> Path:
    manual_payload = json.loads(manual_entries_path.read_text(encoding="utf-8"))
    source = manual_payload["source_images"][0]
    df = _load_core_df(Path(source["source_csv"]))
    by_time = {pd.Timestamp(ts).strftime("%Y-%m-%dT%H:%M:%SZ"): i for i, ts in enumerate(df["open_time_utc"])}
    entry_times = [item["entry_time_utc"] for item in result["first_signals"]]
    bg = "#101418"
    up = "#26a69a"
    down = "#ef5350"
    red = "#ff1010"
    fig, (ax_price, ax_vol) = plt.subplots(2, 1, figsize=(22, 10.5), sharex=True, gridspec_kw={"height_ratios": [4.2, 1.25]})
    fig.patch.set_facecolor(bg)
    ax_price.set_facecolor(bg)
    ax_vol.set_facecolor(bg)
    width = (1 / (24 * 60)) * 0.8
    x = mdates.date2num(df["open_time_utc"].to_numpy())
    ax_price.vlines(x, df["low"], df["high"], color="#cfd8dc", linewidth=0.65, alpha=0.85, zorder=1)
    for i, row in df.iterrows():
        o = float(row["open"])
        c = float(row["close"])
        lower = min(o, c)
        height = max(abs(c - o), 1e-8)
        color = up if c >= o else down
        ax_price.add_patch(Rectangle((x[i] - width / 2, lower), width, height, facecolor=color, edgecolor=color, linewidth=0.45, alpha=0.95, zorder=2))
    ax_price.plot(df["open_time_utc"], df["ema20"], color="#ffd54f", linewidth=1.0, label="EMA20", zorder=3)
    ax_price.plot(df["open_time_utc"], df["ema50"], color="#64b5f6", linewidth=1.0, label="EMA50", zorder=3)
    vol_colors = [up if c >= o else down for o, c in zip(df["open"], df["close"])]
    ax_vol.bar(df["open_time_utc"], df["volume"], width=width, color=vol_colors, alpha=0.75)

    slip = float(slippage_bps) / 10_000.0
    plotted = 0
    for n, entry_time_text in enumerate(entry_times, 1):
        idx = by_time.get(entry_time_text)
        if idx is None:
            continue
        row = df.iloc[idx]
        entry_time = pd.Timestamp(row["open_time_utc"])
        entry_open = float(row["open"])
        entry_slip = entry_open * (1.0 + slip)
        ax_price.annotate(
            f"{n}",
            xy=(entry_time, entry_open),
            xytext=(-18, -4),
            textcoords="offset points",
            ha="center",
            va="center",
            color=red,
            fontsize=8,
            fontweight="bold",
            arrowprops={"arrowstyle": "->", "color": red, "linewidth": 2.1, "shrinkA": 0, "shrinkB": 0},
            zorder=10,
        )
        ax_price.scatter([entry_time], [entry_open], marker="o", s=18, color=red, edgecolors="white", linewidths=0.45, zorder=11)
        ax_price.text(entry_time, entry_open - 0.10, f"{entry_slip:.4f}", color=red, fontsize=6.8, ha="center", va="top", zorder=11)
        plotted += 1
    score = result["score"]
    ax_price.set_title(
        f"SOLUSDT 1m 2026-05-12 UTC | {label} | hits={score['target_hits']}/{score['targets_total']} false={score['false_entries']} entries={score['entries_total']}",
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
    ax_price.legend(facecolor="#172026", edgecolor="#3a444b", labelcolor="white", fontsize=9, loc="upper left", ncol=2)
    fig.autofmt_xdate()
    plt.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    ts_now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = out_dir / f"visual_entry_combo_simple_arrows_{label.lower()}_{ts_now}.png"
    plt.savefig(path, dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


def write_reports(payload: dict[str, Any], out_dir: Path, manual_entries_path: Path, *, render_top: int) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "visual_entry_combo_search_20260512_DEV_v2.json"
    md_path = out_dir / "visual_entry_combo_search_20260512_DEV_v2_RU.md"
    rendered: list[dict[str, str]] = []
    for idx, result in enumerate(payload["top_results"][:render_top], 1):
        png = render_simple_entry_arrows(
            manual_entries_path=manual_entries_path,
            result=result,
            out_dir=out_dir,
            label=f"combo_top{idx}",
        )
        rendered.append({"rank": str(idx), "visual_png": str(png)})
    payload["rendered"] = rendered
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    return json_path, md_path


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Visual Entry Combo Search v2",
        "",
        "Статус: `DEV_COMBO_DIAGNOSTIC_ONLY_NO_ML`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        f"Всего вариантов с попаданиями: `{payload['total_results_with_hits']}`.",
        "",
        "## Top Results",
        "",
        "| rank | hits | false | entries | precision | recall | f1 | params |",
        "|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for idx, item in enumerate(payload["top_results"][:12], 1):
        score = item["score"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{:.4f}` | `{:.4f}` | `{:.4f}` | `{}` |".format(
                idx,
                score["target_hits"],
                score["false_entries"],
                score["entries_total"],
                score["precision"],
                score["recall"],
                score["f1_visual"],
                json.dumps(item["params"], ensure_ascii=False),
            )
        )
    lines.extend(["", "## Rendered", ""])
    for item in payload.get("rendered", []):
        lines.append(f"- rank `{item['rank']}`: `{item['visual_png']}`")
    lines.extend(["", "## Решение", "", "Это диагностический слой для подбора combo. В ML ничего не передавать.", ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search visual-entry combo hypotheses against manual next-open entries.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review")
    parser.add_argument("--top-n", type=int, default=30)
    parser.add_argument("--render-top", type=int, default=3)
    parser.add_argument("--match-tolerance-bars", type=int, default=2)
    args = parser.parse_args(argv)
    manual_path = Path(args.manual_entries)
    payload = search(manual_path, top_n=args.top_n, match_tolerance_bars=args.match_tolerance_bars)
    json_path, md_path = write_reports(payload, Path(args.out_dir), manual_path, render_top=args.render_top)
    print(json.dumps({"status": "OK", "json": str(json_path), "md": str(md_path), "rendered": payload.get("rendered", [])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
