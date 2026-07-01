from __future__ import annotations

import argparse
import itertools
import json
from datetime import timedelta
from pathlib import Path
from typing import Any

from mlbotnav.visual_entry_feature_audit import _read_core_csv, enrich_rows
from mlbotnav.visual_entry_score import TradeEntry, load_manual_entries, score_entries


def _passes(row: dict[str, Any], params: dict[str, Any]) -> tuple[bool, list[str]]:
    votes: list[str] = []
    if row.get("ema20_slope_5_pct") is not None and row["ema20_slope_5_pct"] <= 0:
        votes.append("ema20_down")
    if row.get("range_pos_60") is not None and row["range_pos_60"] <= params["range_pos_max"]:
        votes.append("near_low")
    if row.get("rsi14") is not None and row["rsi14"] <= params["rsi_max"]:
        votes.append("rsi_cold")
    if row.get("stoch_k14") is not None and row["stoch_k14"] <= params["stoch_max"]:
        votes.append("stoch_low")
    if row.get("ret_12_pct") is not None and row["ret_12_pct"] <= params["ret12_max"]:
        votes.append("ret12_dip")
    if row.get("ret_24_pct") is not None and row["ret_24_pct"] <= params["ret24_max"]:
        votes.append("ret24_dip")
    if params["require_green"] and row.get("green_candle"):
        votes.append("green_signal")
    if row.get("lower_wick_share") is not None and row["lower_wick_share"] >= params["lower_wick_min"]:
        votes.append("lower_wick")
    if row.get("vol_z20") is not None and row["vol_z20"] >= params["vol_z_min"]:
        votes.append("volume_confirm")
    return len(votes) >= params["min_votes"], votes


def _iter_param_grid() -> list[dict[str, Any]]:
    grid = {
        "range_pos_max": [0.25, 0.35, 0.50],
        "rsi_max": [35.0, 40.0, 45.0],
        "stoch_max": [25.0, 35.0, 50.0],
        "ret12_max": [-0.30, -0.15, 0.0],
        "ret24_max": [-0.60, -0.30, 0.0],
        "require_green": [False, True],
        "lower_wick_min": [0.0, 0.50],
        "vol_z_min": [0.0],
        "min_votes": [3, 4, 5],
        "cooldown_bars": [10, 20, 30, 60],
    }
    keys = list(grid)
    return [dict(zip(keys, values)) for values in itertools.product(*(grid[key] for key in keys))]


def _signals_for_params(rows: list[dict[str, Any]], params: dict[str, Any]) -> tuple[list[TradeEntry], list[dict[str, Any]]]:
    trades: list[TradeEntry] = []
    details: list[dict[str, Any]] = []
    last_signal_index = -10_000
    for idx, row in enumerate(rows[:-1]):
        if idx < 60:
            continue
        ok, votes = _passes(row, params)
        if not ok:
            continue
        if idx - last_signal_index < params["cooldown_bars"]:
            continue
        last_signal_index = idx
        entry_time = row["open_time_utc"] + timedelta(minutes=1)
        trades.append(
            TradeEntry(
                row_index=idx,
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
                "signal_time_utc": row["open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_time_utc": entry_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "votes": votes,
            }
        )
    return trades, details


def search(manual_entries_path: Path) -> dict[str, Any]:
    manual_payload, manual_entries = load_manual_entries(manual_entries_path)
    rows = _read_core_csv(Path(manual_payload["source_images"][0]["source_csv"]))
    enrich_rows(rows)
    results: list[dict[str, Any]] = []
    for params in _iter_param_grid():
        trades, details = _signals_for_params(rows, params)
        if not trades:
            continue
        score = score_entries(manual_entries, trades)
        if score["target_hits"] <= 0:
            continue
        results.append(
            {
                "params": params,
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
                        "entry_lag_bars_avg",
                        "entry_lag_bars_abs_max",
                        "duplicate_hits",
                        "visual_status",
                    ]
                },
                "hit_details": score["hit_details"],
                "missed_target_details": score["missed_target_details"],
                "first_signals": details[:20],
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
        "manual_entries": str(manual_entries_path),
        "search_space": "REVERSAL_DIP_BUY_LONG_PREFILTER_V0",
        "results_total": len(results),
        "top_results": results[:30],
    }


def write_reports(payload: dict[str, Any], out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "visual_entry_prefilter_search_20260512_DEV.json"
    md_path = out_dir / "visual_entry_prefilter_search_20260512_DEV_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    return json_path, md_path


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Visual Entry Prefilter Search 2026-05-12",
        "",
        "Статус: `DEV_PREFILTER_DIAGNOSTIC_ONLY`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        f"Search space: `{payload['search_space']}`.",
        f"Всего непустых вариантов с попаданиями: `{payload['results_total']}`.",
        "",
        "## Top Results",
        "",
        "| rank | hits | false | entries | precision | recall | f1 | params |",
        "|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for rank, item in enumerate(payload["top_results"][:15], 1):
        score = item["score"]
        lines.append(
            "| `{rank}` | `{hits}` | `{false}` | `{entries}` | `{precision:.4f}` | `{recall:.4f}` | `{f1:.4f}` | `{params}` |".format(
                rank=rank,
                hits=score["target_hits"],
                false=score["false_entries"],
                entries=score["entries_total"],
                precision=score["precision"],
                recall=score["recall"],
                f1=score["f1_visual"],
                params=json.dumps(item["params"], ensure_ascii=False, sort_keys=True),
            )
        )
    if payload["top_results"]:
        best = payload["top_results"][0]
        lines.extend(["", "## Лучший вариант", ""])
        lines.append(f"Параметры: `{json.dumps(best['params'], ensure_ascii=False, sort_keys=True)}`")
        lines.append("")
        lines.append("Попадания:")
        for hit in best["hit_details"]:
            lines.append(
                f"- `{hit['manual_entry_id']}` target `{hit['target_entry_time_utc']}` matched `{hit['matched_entry_time_utc']}`, lag `{hit['lag_bars']}`"
            )
        lines.append("")
        lines.append("Пропуски:")
        for missed in best["missed_target_details"]:
            lines.append(f"- `{missed['manual_entry_id']}` target `{missed['target_entry_time_utc']}`")
    lines.extend(
        [
            "",
            "## Решение",
            "",
            "Это быстрый prefilter без backtest exit-логики и без допуска в ML. Его задача: выбрать черновой набор условий для следующего полноценного backtest/Optuna-кандидата.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search simple reversal/dip-buy prefilters against manual visual entries.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/qa_gate")
    args = parser.parse_args(argv)
    payload = search(Path(args.manual_entries))
    json_path, md_path = write_reports(payload, Path(args.out_dir))
    print(json.dumps({"status": "OK", "json": str(json_path), "md": str(md_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
