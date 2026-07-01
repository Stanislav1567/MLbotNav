from __future__ import annotations

import argparse
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.render_visual_entry_overlay import render_family_candidate_overlay
from mlbotnav.visual_entry_no_lookahead_candidates import _prepare_rows
from mlbotnav.visual_entry_score import TradeEntry, load_manual_entries, score_entries


def _value(row: dict[str, Any], key: str, default: float) -> float:
    value = row.get(key)
    if value is None:
        return default
    return float(value)


GRID: dict[str, list[Any]] = {
    "local_low_bars": [5, 10],
    "range_thr": [0.35, 0.50],
    "rsi_thr": [55.0, 65.0, 100.0],
    "stoch_thr": [75.0, 100.0],
    "mfi_thr": [65.0, 100.0],
    "ema_gap_thr": [0.05, 1.0],
    "ema_slope_thr": [0.05, 1.0],
    "ret12_thr": [0.10, 999.0],
    "ret24_thr": [-0.10, 999.0],
    "wick_thr": [0.30, 999.0],
    "closepos_thr": [0.50, 999.0],
    "min_votes": [4, 5],
    "cooldown_bars": [5, 10],
}


def _iter_grid(grid: dict[str, list[Any]]) -> list[dict[str, Any]]:
    keys = list(grid)
    return [dict(zip(keys, values)) for values in itertools.product(*(grid[key] for key in keys))]


def _row_votes(row: dict[str, Any], params: dict[str, Any]) -> list[str]:
    votes: list[str] = []
    low_pos = min(_value(row, "range_pos_60", 1.0), _value(row, "low_range_pos_60", 1.0))
    if low_pos <= float(params["range_thr"]):
        votes.append("RANGE_LOW_60")
    if _value(row, "rsi14", 999.0) <= float(params["rsi_thr"]):
        votes.append("RSI_COLD")
    if _value(row, "stoch_k14", 999.0) <= float(params["stoch_thr"]):
        votes.append("STOCH_LOW")
    if _value(row, "mfi14", 999.0) <= float(params["mfi_thr"]):
        votes.append("MFI_COLD")
    if _value(row, "ema_gap_pct", 999.0) <= float(params["ema_gap_thr"]):
        votes.append("EMA_NOT_HOT")
    if _value(row, "ema20_slope_5_pct", 999.0) <= float(params["ema_slope_thr"]):
        votes.append("EMA_SLOPE_NOT_UP")
    if _value(row, "ret_12_pct", 999.0) <= float(params["ret12_thr"]) or _value(row, "ret_24_pct", 999.0) <= float(params["ret24_thr"]):
        votes.append("DIP_RET")
    if _value(row, "lower_wick_share", 0.0) >= float(params["wick_thr"]) or _value(row, "close_pos_candle", 0.0) >= float(params["closepos_thr"]):
        votes.append("WICK_OR_RECLAIM")
    return votes


def _run_variant(rows: list[dict[str, Any]], manual_entries: list[Any], params: dict[str, Any]) -> dict[str, Any]:
    details: list[dict[str, Any]] = []
    trades: list[TradeEntry] = []
    last_entry_idx = -10_000
    local_low_bars = params["local_low_bars"]
    for signal_idx in range(60, len(rows) - 1):
        entry_idx = signal_idx + 1
        if entry_idx - last_entry_idx < int(params["cooldown_bars"]):
            continue
        signal = rows[signal_idx]
        if local_low_bars is not None and not bool(signal.get(f"local_low_{int(local_low_bars)}")):
            continue
        votes = _row_votes(signal, params)
        if len(votes) < int(params["min_votes"]):
            continue
        entry = rows[entry_idx]
        last_entry_idx = entry_idx
        trades.append(
            TradeEntry(
                row_index=entry_idx,
                side="long",
                entry_time=entry["open_time_utc"],
                exit_time_raw="",
                net_return=0.0,
                mae_pct=None,
                mfe_pct=None,
            )
        )
        entry_open = float(entry["open"])
        details.append(
            {
                "family_id": "VISUAL_MICRO_BOTTOM_SIGNATURE_V0",
                "side": "long",
                "signal_row_index": int(signal_idx),
                "entry_row_index": int(entry_idx),
                "signal_time_utc": signal["open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_time_utc": entry["open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_open_price": entry_open,
                "entry_price_with_slippage": entry_open * 1.0005,
                "slippage_bps": 5.0,
                "context_votes": votes,
                "trigger_votes": ["MICRO_BOTTOM_SIGNATURE"],
                "confirm_votes": [],
                "lookahead": "NO",
                "entry_rule": "next_bar_open_after_signal_close",
            }
        )
    score = score_entries(manual_entries, trades)
    return {
        "family_id": "VISUAL_MICRO_BOTTOM_SIGNATURE_V0",
        "description_ru": "Диагностическая микро-подпись дна по core-признакам без lookahead.",
        "params": params,
        "score": _score_summary(score),
        "hit_details": score["hit_details"],
        "missed_target_details": score["missed_target_details"],
        "false_entry_details": score["false_entry_details"][:200],
        "signals": details,
    }


def _score_summary(score: dict[str, Any]) -> dict[str, Any]:
    return {
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
            "entry_lag_bars_avg",
            "entry_lag_bars_abs_max",
            "duplicate_hits",
            "visual_status",
        ]
    }


def _sort_key(item: dict[str, Any]) -> tuple[float, float, float, int, int]:
    score = item["score"]
    return (
        float(score["f1_visual"]),
        float(score["recall"]),
        float(score["precision"]),
        -int(score["false_entries"]),
        -int(score["entries_total"]),
    )


def _public_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in results:
        public = dict(item)
        public["signals"] = item.get("signals", [])[:300]
        out.append(public)
    return out


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Visual Entry micro-bottom signature runner",
        "",
        "Статус: `DEV_MICRO_BOTTOM_SIGNATURE_DIAGNOSTIC_NO_ML`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "Контракт: closed signal candle -> next open, `lookahead=NO`, slippage `5 bps`.",
        "",
        "| rank | hits | miss | false | entries | precision | recall | f1 | params |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    lines[2] = "Статус: `DEV_MICRO_BOTTOM_SIGNATURE_DIAGNOSTIC_NO_ML`."
    lines[6] = "Контракт: closed signal candle -> next open, `lookahead=NO`, slippage `5 bps`."
    for rank, item in enumerate(payload["best_overall"], 1):
        score = item["score"]
        params = item["params"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{:.4f}` | `{:.4f}` | `{:.4f}` | `{}` |".format(
                rank,
                score["target_hits"],
                score["missed_targets"],
                score["false_entries"],
                score["entries_total"],
                score["precision"],
                score["recall"],
                score["f1_visual"],
                params,
            )
        )
    lines.extend(["", "## PNG", ""])
    for item in payload.get("rendered_overlays", []):
        lines.append(f"- `{item['visual_png']}`")
    lines.extend(
        [
            "",
            "## Решение",
            "",
            "Это DEV diagnostic-only. В ML ничего не передавать без validation/holdout и ручного `APPROVED_FOR_ML`.",
        ]
    )
    lines[-3] = "## Решение"
    lines[-1] = "Это DEV diagnostic-only. В ML ничего не передавать без validation/holdout и ручного `APPROVED_FOR_ML`."
    return "\n".join(lines) + "\n"


def run_search(manual_entries_path: Path, out_dir: Path, *, render_top: int = 6) -> dict[str, Any]:
    _, manual_entries = load_manual_entries(manual_entries_path)
    _, rows = _prepare_rows(manual_entries_path)
    results: list[dict[str, Any]] = []
    for params in _iter_grid(GRID):
        result = _run_variant(rows, manual_entries, dict(params))
        score = result["score"]
        if score["target_hits"] <= 0:
            continue
        if score["entries_total"] > 140:
            continue
        results.append(result)
    results.sort(key=_sort_key, reverse=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[dict[str, str]] = []
    for rank, result in enumerate(results[:render_top], 1):
        label = f"micro_bottom_{rank:02d}"
        png_path = render_family_candidate_overlay(
            manual_entries_path=manual_entries_path,
            result=result,
            out_dir=out_dir,
            label=label,
            slippage_bps=5.0,
        )
        rendered.append({"rank": str(rank), "family_id": result["family_id"], "visual_png": str(png_path)})
    payload = {
        "schema_version": 1,
        "status": "DEV_MICRO_BOTTOM_SIGNATURE_DIAGNOSTIC_NO_ML",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "manual_entries": str(manual_entries_path),
        "results_total": len(results),
        "best_overall": _public_results(results[:30]),
        "rendered_overlays": rendered,
        "ml_transfer_allowed": False,
    }
    json_path = out_dir / "visual_entry_micro_bottom_signature_20260512_DEV.json"
    md_path = out_dir / "visual_entry_micro_bottom_signature_20260512_DEV_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run visual micro-bottom signature diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/micro_bottom_signature")
    parser.add_argument("--render-top", type=int, default=6)
    args = parser.parse_args(argv)
    payload = run_search(Path(args.manual_entries), Path(args.out_dir), render_top=int(args.render_top))
    print(
        json.dumps(
            {
                "status": payload["status"],
                "json_path": payload["json_path"],
                "md_path": payload["md_path"],
                "rendered": payload["rendered_overlays"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
