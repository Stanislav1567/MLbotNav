from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.render_visual_entry_overlay import render_family_candidate_overlay
from mlbotnav.visual_entry_no_lookahead_candidates import _prepare_rows
from mlbotnav.visual_entry_quality_filter_runner import _enrich_quality_rows
from mlbotnav.visual_entry_regime_split_ranker_runner import (
    _raw_candidates as _regime_raw_candidates,
    _select_online_no_rewrite,
)
from mlbotnav.visual_entry_score import TradeEntry, load_manual_entries, score_entries
from mlbotnav.visual_entry_significant_low_selector_runner import SLIPPAGE_BPS, _score_summary


STATUS = "DEV_REGIME_FALSE_SUPPRESSION_V2_ENTRY_ONLY_NO_ML"


SUPPRESSION_VARIANTS: list[dict[str, Any]] = [
    {
        "family_id": "FSV01_DEEP_CAPITULATION_CLEAN_RECLAIM",
        "regime": "DEEP_CAPITULATION",
        "source_min_score": 10,
        "rank_mode": "strict_hot_deep",
        "duplicate_gap_bars": 10,
        "filters": {
            "low_zone_max": 0.14,
            "ret12_max": -0.30,
            "rsi_max": 45.0,
            "stoch_max": 45.0,
            "mfi_max": 45.0,
            "wick_min": 0.25,
            "closepos_min": 0.30,
            "volz_min": 0.15,
            "new_low_count_20_max": 12,
            "lower_low_streak_5_max": 4,
        },
        "description_ru": "Чистая capitulation/reclaim: глубокая зона, холодные осцилляторы, падение, wick/reclaim и объем.",
    },
    {
        "family_id": "FSV02_DEEP_CAPITULATION_SOFT_NOWICK",
        "regime": "DEEP_CAPITULATION",
        "source_min_score": 10,
        "rank_mode": "strict_hot_deep",
        "duplicate_gap_bars": 10,
        "filters": {
            "low_zone_max": 0.16,
            "ret12_max": -0.25,
            "ret24_max": -0.45,
            "rsi_max": 42.0,
            "stoch_max": 35.0,
            "mfi_max": 45.0,
            "new_low_count_20_max": 12,
            "lower_low_streak_5_max": 4,
        },
        "description_ru": "Мягкий deep/no-wick: разрешает сильный low без reclaim, если падение и холодные осцилляторы очень явные.",
    },
    {
        "family_id": "FSV03_HOT_SUPPORT_STRONG_RECLAIM",
        "regime": "HOT_RECLAIM_SUPPORT",
        "source_min_score": 9,
        "rank_mode": "late_low_reclaim",
        "duplicate_gap_bars": 10,
        "filters": {
            "support_touch_count_60_min": 14,
            "low_zone_max": 0.75,
            "closepos_min": 0.80,
            "wick_min": 0.20,
            "ema20_slope_5_pct_min": -0.02,
            "new_low_count_20_max": 8,
            "lower_low_streak_5_max": 1,
        },
        "description_ru": "Hot/support с сильным reclaim: поддержка, высокая позиция закрытия свечи, wick и живая EMA.",
    },
    {
        "family_id": "FSV04_HOT_SUPPORT_CLOSE_RECLAIM",
        "regime": "HOT_RECLAIM_SUPPORT",
        "source_min_score": 9,
        "rank_mode": "late_low_reclaim",
        "duplicate_gap_bars": 12,
        "filters": {
            "support_touch_count_60_min": 18,
            "low_zone_max": 0.75,
            "closepos_min": 0.82,
            "ema20_slope_5_pct_min": -0.02,
            "new_low_count_20_max": 8,
            "lower_low_streak_5_max": 1,
        },
        "description_ru": "Hot/support close reclaim: wick не обязателен, если поддержка плотная и свеча закрылась вверху.",
    },
    {
        "family_id": "FSV05_TREND_DIP_EMA_RECLAIM",
        "regime": "TREND_DIP_CONTINUATION",
        "source_min_score": 9,
        "rank_mode": "late_low_reclaim",
        "duplicate_gap_bars": 10,
        "filters": {
            "support_touch_count_60_min": 10,
            "low_zone_max": 0.76,
            "closepos_min": 0.50,
            "ema20_slope_5_pct_min": 0.0,
            "ret24_min": -0.15,
            "new_low_count_20_max": 8,
            "lower_low_streak_5_max": 1,
        },
        "description_ru": "Trend-dip EMA reclaim: откат в живом движении, EMA не падает, есть reclaim и нет цепочки новых low.",
    },
    {
        "family_id": "FSV06_TREND_DIP_HIGH_ZONE_STRUCTURE",
        "regime": "TREND_DIP_CONTINUATION",
        "source_min_score": 9,
        "rank_mode": "balanced",
        "duplicate_gap_bars": 12,
        "filters": {
            "support_touch_count_60_min": 7,
            "low_zone_min": 0.78,
            "low_zone_max": 0.88,
            "closepos_min": 0.80,
            "ema20_slope_5_pct_min": 0.05,
            "ret24_min": 0.0,
            "new_low_count_20_max": 7,
            "lower_low_streak_5_max": 1,
        },
        "description_ru": "Trend high-zone structure: отдельный режим для высоких структурных pullback, которые не являются deep-low.",
    },
    {
        "family_id": "FSV07_STRUCTURE_VOLUME_RETEST",
        "regime": "STRUCTURE_BOS_FIBO_VOLUME",
        "source_min_score": 9,
        "rank_mode": "balanced",
        "duplicate_gap_bars": 12,
        "filters": {
            "support_touch_count_60_min": 12,
            "low_zone_max": 0.75,
            "closepos_min": 0.30,
            "wick_min": 0.20,
            "volz_min": 0.20,
            "new_low_count_20_max": 10,
            "lower_low_streak_5_max": 2,
        },
        "description_ru": "Structure/volume retest: поддержка, объем, low-zone и wick/reclaim как приближение к структурному уровню.",
    },
    {
        "family_id": "FSV08_STRUCTURE_SUPPORT_RECLAIM",
        "regime": "STRUCTURE_BOS_FIBO_VOLUME",
        "source_min_score": 9,
        "rank_mode": "late_low_reclaim",
        "duplicate_gap_bars": 12,
        "filters": {
            "support_touch_count_60_min": 18,
            "low_zone_max": 0.75,
            "closepos_min": 0.80,
            "ema20_slope_5_pct_min": -0.02,
            "new_low_count_20_max": 8,
            "lower_low_streak_5_max": 1,
        },
        "description_ru": "Structure support reclaim: плотная поддержка и сильное закрытие свечи без требования перепроданности.",
    },
]


UNION_VARIANTS: list[dict[str, Any]] = [
    {
        "family_id": "FSV20_UNION_CLEAN_RECALL_BALANCED",
        "source_family_ids": [
            "FSV01_DEEP_CAPITULATION_CLEAN_RECLAIM",
            "FSV04_HOT_SUPPORT_CLOSE_RECLAIM",
            "FSV05_TREND_DIP_EMA_RECLAIM",
            "FSV07_STRUCTURE_VOLUME_RETEST",
            "FSV08_STRUCTURE_SUPPORT_RECLAIM",
        ],
        "duplicate_gap_bars": 8,
        "description_ru": "Сводный чистый recall-баланс из режимных suppress-кирпичей.",
    },
    {
        "family_id": "FSV21_UNION_STRICT_FALSE_CONTROL",
        "source_family_ids": [
            "FSV01_DEEP_CAPITULATION_CLEAN_RECLAIM",
            "FSV03_HOT_SUPPORT_STRONG_RECLAIM",
            "FSV06_TREND_DIP_HIGH_ZONE_STRUCTURE",
            "FSV07_STRUCTURE_VOLUME_RETEST",
        ],
        "duplicate_gap_bars": 10,
        "description_ru": "Более строгий union для контроля false.",
    },
]


def _passes_filters(signal: dict[str, Any], filters: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    dbg = signal.get("debug") or {}
    passed: list[str] = []
    suppressed: list[str] = []
    aliases = {
        "ret6": "ret_6_pct",
        "ret12": "ret_12_pct",
        "ret24": "ret_24_pct",
        "rsi": "rsi14",
        "stoch": "stoch_k14",
        "mfi": "mfi14",
        "wick": "lower_wick_share",
        "closepos": "close_pos_candle",
        "volz": "vol_z20",
    }

    def val(key: str, default: float = 0.0) -> float:
        metric_key = aliases.get(key, key)
        if metric_key == "low_zone":
            return float(dbg.get("low_zone", 1.0))
        return float(dbg.get(metric_key, default))

    for key, threshold in filters.items():
        metric = key.removesuffix("_min").removesuffix("_max")
        current = val(metric)
        if key.endswith("_min"):
            if current < float(threshold):
                suppressed.append(f"{metric}_BELOW_{threshold}")
            else:
                passed.append(f"{metric}_MIN_OK")
        elif key.endswith("_max"):
            if current > float(threshold):
                suppressed.append(f"{metric}_ABOVE_{threshold}")
            else:
                passed.append(f"{metric}_MAX_OK")
    return not suppressed, passed, suppressed


def _enrich_filter_debug(signal: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(signal)
    dbg = dict(enriched.get("debug") or {})
    for key in (
        "new_low_count_20",
        "lower_low_streak_5",
        "support_touch_count_60",
        "ret_6_pct",
        "ret_12_pct",
        "ret_24_pct",
        "rsi14",
        "stoch_k14",
        "mfi14",
        "lower_wick_share",
        "close_pos_candle",
        "vol_z20",
        "ema20_slope_5_pct",
    ):
        if key not in dbg and key in row:
            dbg[key] = row[key]
    enriched["debug"] = dbg
    return enriched


def _to_trade(signal: dict[str, Any]) -> TradeEntry:
    return TradeEntry(
        row_index=int(signal["entry_row_index"]),
        side="long",
        entry_time=datetime.fromisoformat(str(signal["entry_time_utc"]).replace("Z", "+00:00")),
        exit_time_raw="",
        net_return=0.0,
        mae_pct=None,
        mfe_pct=None,
    )


def _run_variant(rows: list[dict[str, Any]], manual_entries: list[Any], variant: dict[str, Any]) -> dict[str, Any]:
    source_variant = {
        "family_id": variant["family_id"],
        "regime": variant["regime"],
        "min_score": int(variant["source_min_score"]),
        "cluster_gap_bars": int(variant["duplicate_gap_bars"]),
        "rank_mode": variant["rank_mode"],
    }
    source = _regime_raw_candidates(rows, source_variant)
    filtered: list[dict[str, Any]] = []
    suppressed_total = 0
    for signal in source:
        row = rows[int(signal["signal_row_index"])]
        signal = _enrich_filter_debug(signal, row)
        ok, passed_votes, suppress_votes = _passes_filters(signal, dict(variant["filters"]))
        if not ok:
            suppressed_total += 1
            continue
        enriched = dict(signal)
        enriched["family_id"] = str(variant["family_id"])
        enriched["bucket"] = str(variant["regime"])
        enriched["regime"] = str(variant["regime"])
        enriched["confirm_votes"] = list(enriched.get("confirm_votes", [])) + passed_votes
        enriched["suppress_votes"] = list(enriched.get("suppress_votes", [])) + suppress_votes
        enriched["trigger_votes"] = list(enriched.get("trigger_votes", [])) + ["REGIME_FALSE_SUPPRESSION_PASS"]
        filtered.append(enriched)
    signals = _select_online_no_rewrite(filtered, min_gap_bars=int(variant["duplicate_gap_bars"]))
    score = score_entries(manual_entries, [_to_trade(item) for item in signals])
    return {
        "family_id": str(variant["family_id"]),
        "bucket": str(variant["regime"]),
        "regime": str(variant["regime"]),
        "description_ru": str(variant["description_ru"]),
        "params": {
            "source_min_score": int(variant["source_min_score"]),
            "duplicate_gap_bars": int(variant["duplicate_gap_bars"]),
            "rank_mode": str(variant["rank_mode"]),
            "filters": dict(variant["filters"]),
            "cooldown_used": False,
        },
        "raw_candidates_total": len(source),
        "suppressed_candidates_total": suppressed_total,
        "filtered_candidates_total": len(filtered),
        "clusters_total": len(signals),
        "score": _score_summary(score),
        "hit_details": score["hit_details"],
        "missed_target_details": score["missed_target_details"],
        "false_entry_details": score["false_entry_details"][:250],
        "signals": signals,
        "selection_rule": "first_qualified_no_future_rewrite",
    }


def _run_union(results: list[dict[str, Any]], manual_entries: list[Any], params: dict[str, Any]) -> dict[str, Any]:
    source_ids = {str(item) for item in params["source_family_ids"]}
    raw: list[dict[str, Any]] = []
    for result in results:
        if str(result["family_id"]) not in source_ids:
            continue
        for signal in result.get("signals", []):
            enriched = dict(signal)
            enriched["source_family_id"] = result["family_id"]
            enriched["family_id"] = str(params["family_id"])
            enriched["bucket"] = "REGIME_SUPPRESSION_UNION"
            enriched["trigger_votes"] = list(enriched.get("trigger_votes", [])) + ["FSV_UNION"]
            raw.append(enriched)
    signals = _select_online_no_rewrite(raw, min_gap_bars=int(params["duplicate_gap_bars"]))
    score = score_entries(manual_entries, [_to_trade(item) for item in signals])
    return {
        "family_id": str(params["family_id"]),
        "bucket": "REGIME_SUPPRESSION_UNION",
        "regime": "UNION",
        "description_ru": str(params["description_ru"]),
        "params": dict(params) | {"cooldown_used": False},
        "raw_candidates_total": len(raw),
        "suppressed_candidates_total": 0,
        "filtered_candidates_total": len(raw),
        "clusters_total": len(signals),
        "score": _score_summary(score),
        "hit_details": score["hit_details"],
        "missed_target_details": score["missed_target_details"],
        "false_entry_details": score["false_entry_details"][:250],
        "signals": signals,
        "selection_rule": "first_qualified_no_future_rewrite",
    }


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Regime False Suppression V2",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "Контракт: entry-only, signal-свеча закрыта, вход LONG на `open` следующей свечи, `lookahead=NO`, slippage `5 bps`.",
        "",
        "Граница: сделки, TP/SL, MFE/MAE, future return, cooldown-сетки `30/45/60/90` и ML-export не используются.",
        "",
        "Выбор online-style: `first_qualified_no_future_rewrite`.",
        "",
        "| rank | family | regime | hits | miss | false | entries | raw | suppressed | filtered | f1 |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, item in enumerate(payload["best_overall"], 1):
        score = item["score"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{:.4f}` |".format(
                rank,
                item["family_id"],
                item["regime"],
                score["target_hits"],
                score["missed_targets"],
                score["false_entries"],
                score["entries_total"],
                item["raw_candidates_total"],
                item["suppressed_candidates_total"],
                item["filtered_candidates_total"],
                score["f1_visual"],
            )
        )
    lines.extend(["", "## PNG", ""])
    for item in payload.get("rendered_overlays", []):
        lines.append(f"- `{item['family_id']}`: `{item['visual_png']}`")
    lines.extend(
        [
            "",
            "## Решение",
            "",
            "V2 проверяет, можно ли резко уменьшить ложные входы в шумных режимах без использования будущего результата сделки. Это не ML-кандидат и не production GO.",
            "",
        ]
    )
    return "\n".join(lines)


def run_search(manual_entries_path: Path, out_dir: Path, *, render_top: int = 8) -> dict[str, Any]:
    manual_payload, manual_entries = load_manual_entries(manual_entries_path)
    _, rows = _prepare_rows(manual_entries_path)
    _enrich_quality_rows(rows)
    base_results = [_run_variant(rows, manual_entries, variant) for variant in SUPPRESSION_VARIANTS]
    union_results = [_run_union(base_results, manual_entries, params) for params in UNION_VARIANTS]
    results = [item for item in base_results + union_results if int(item["score"]["entries_total"]) > 0]
    results.sort(
        key=lambda item: (
            item["score"]["f1_visual"],
            item["score"]["precision"],
            item["score"]["recall"],
            -item["score"]["false_entries"],
        ),
        reverse=True,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[dict[str, str]] = []
    for rank, result in enumerate(results[:render_top], 1):
        png_path = render_family_candidate_overlay(
            manual_entries_path=manual_entries_path,
            result=result,
            out_dir=out_dir,
            label=f"regime_false_suppression_v2_{rank:02d}_{result['family_id'].lower()}",
            slippage_bps=SLIPPAGE_BPS,
        )
        rendered.append({"rank": str(rank), "family_id": result["family_id"], "visual_png": str(png_path)})

    source = (manual_payload.get("source_images") or [{}])[0]
    day = str(source.get("date_utc", "unknown")).replace("-", "")
    role = str(manual_payload.get("dataset_role", "DEV")).upper()
    safe_role = "".join(ch if ch.isalnum() else "_" for ch in role).strip("_") or "DEV"
    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "manual_entries": str(manual_entries_path),
        "strategy_scope": "entry_only_low_detection_regime_false_suppression",
        "online_duplicate_suppression_used": True,
        "cooldown_used": False,
        "future_trade_outcome_used": False,
        "ml_transfer_allowed": False,
        "best_overall": results,
        "rendered_overlays": rendered,
    }
    json_path = out_dir / f"visual_entry_regime_false_suppression_v2_{day}_{safe_role}.json"
    md_path = out_dir / f"visual_entry_regime_false_suppression_v2_{day}_{safe_role}_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run regime false-suppression V2 visual-entry diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/regime_false_suppression")
    parser.add_argument("--render-top", type=int, default=8)
    args = parser.parse_args(argv)
    payload = run_search(Path(args.manual_entries), Path(args.out_dir), render_top=int(args.render_top))
    print(
        json.dumps(
            {
                "status": payload["status"],
                "json_path": payload["json_path"],
                "md_path": payload["md_path"],
                "rendered": payload["rendered_overlays"],
                "best": [
                    {
                        "family_id": item["family_id"],
                        "regime": item["regime"],
                        "raw_candidates_total": item["raw_candidates_total"],
                        "suppressed_candidates_total": item["suppressed_candidates_total"],
                        "filtered_candidates_total": item["filtered_candidates_total"],
                        "clusters_total": item["clusters_total"],
                        "score": item["score"],
                    }
                    for item in payload["best_overall"]
                ],
                "ml_transfer_allowed": payload["ml_transfer_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
