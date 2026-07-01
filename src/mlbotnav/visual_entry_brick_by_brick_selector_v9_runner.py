from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.render_visual_entry_overlay import render_family_candidate_overlay
from mlbotnav.visual_entry_generalization_v7_runner import _online_duplicate_filter, _to_trade
from mlbotnav.visual_entry_negative_context_suppression_v8_runner import (
    VARIANTS as V8_VARIANTS,
    _filtered_source_signals,
)
from mlbotnav.visual_entry_no_lookahead_candidates import _prepare_rows
from mlbotnav.visual_entry_online_low_event_quality_runner import _with_event_features
from mlbotnav.visual_entry_quality_filter_runner import _enrich_quality_rows
from mlbotnav.visual_entry_score import load_manual_entries, score_entries
from mlbotnav.visual_entry_significant_low_selector_runner import SLIPPAGE_BPS, _score_summary


STATUS = "DEV_BRICK_BY_BRICK_SELECTOR_V9_ENTRY_ONLY_NO_ML"


VARIANTS: list[dict[str, Any]] = [
    {
        "family_id": "V9_01_HOT_CHAIN_EVENT_LOW_BRICK",
        "source_family_id": "V8_02_HOT_CHAIN_EVENT_LOW_SUPPRESSION",
        "bucket": "HOT_CHAIN_EVENT_LOW_BRICK",
        "brick": "HOT_CHAIN_EVENT_LOW",
        "duplicate_gap_bars": 2,
        "candidate_for_clean_union": True,
        "description_ru": "Чистый hot-chain кирпич: зрелый восходящий участок, сигнал только на event-low серии.",
    },
    {
        "family_id": "V9_02_HOT_FIRST_STRONG_RECLAIM_BRICK",
        "source_family_id": "V8_01_HOT_FIRST_NEGATIVE_SUPPRESSION",
        "bucket": "HOT_FIRST_STRONG_RECLAIM_BRICK",
        "brick": "HOT_FIRST_STRONG_RECLAIM",
        "duplicate_gap_bars": 4,
        "candidate_for_clean_union": False,
        "description_ru": "Hot-first кирпич: первый горячий reclaim после лоя, без верхней полки и перегрева.",
    },
    {
        "family_id": "V9_03_WARM_STRUCTURAL_RECLAIM_BRICK",
        "source_family_id": "V8_03_WARM_RETEST_NEGATIVE_SUPPRESSION",
        "bucket": "WARM_STRUCTURAL_RECLAIM_BRICK",
        "brick": "WARM_STRUCTURAL_RECLAIM",
        "duplicate_gap_bars": 5,
        "candidate_for_clean_union": False,
        "description_ru": "Warm/retest кирпич: структурный локальный лой с reclaim или сильным нижним фитилем.",
    },
    {
        "family_id": "V9_04_DEEP_TERMINAL_RECLAIM_BRICK",
        "source_family_id": "V8_04_DEEP_EVENT_NEGATIVE_SUPPRESSION",
        "bucket": "DEEP_TERMINAL_RECLAIM_BRICK",
        "brick": "DEEP_TERMINAL_RECLAIM",
        "duplicate_gap_bars": 6,
        "candidate_for_clean_union": False,
        "description_ru": "Deep-terminal кирпич: капитуляционный низ или сильный провал с первым reclaim.",
    },
    {
        "family_id": "V9_20_CLEAN_BRICKS_UNION",
        "source_family_ids": ["V9_01_HOT_CHAIN_EVENT_LOW_BRICK"],
        "bucket": "CLEAN_BRICKS_UNION",
        "duplicate_gap_bars": 3,
        "description_ru": "Строгий union только из кирпичей, которые уже показали чистый режим; шумные слои сюда не входят.",
    },
    {
        "family_id": "V9_90_RESEARCH_UNION_ALL_BRICKS_DIAG",
        "source_family_ids": [
            "V9_01_HOT_CHAIN_EVENT_LOW_BRICK",
            "V9_02_HOT_FIRST_STRONG_RECLAIM_BRICK",
            "V9_03_WARM_STRUCTURAL_RECLAIM_BRICK",
            "V9_04_DEEP_TERMINAL_RECLAIM_BRICK",
        ],
        "bucket": "RESEARCH_UNION_ALL_BRICKS_DIAG",
        "duplicate_gap_bars": 3,
        "description_ru": "Диагностический union всех V9-кирпичей; нужен только для карты покрытия, не кандидат.",
    },
]


def _debug(signal: dict[str, Any], key: str, default: float = 0.0) -> float:
    value = (signal.get("debug") or {}).get(key, default)
    if value is None:
        return default
    return float(value)


def _bool_debug(signal: dict[str, Any], key: str) -> bool:
    return bool((signal.get("debug") or {}).get(key))


def _source_variant(source_family_id: str) -> dict[str, Any]:
    for variant in V8_VARIANTS:
        if variant.get("family_id") == source_family_id:
            return variant
    raise KeyError(source_family_id)


def _brick_reject_reasons(signal: dict[str, Any], brick: str) -> list[str]:
    low_zone = _debug(signal, "low_zone", 1.0)
    support = _debug(signal, "support_touch_count_60")
    distance = _debug(signal, "distance_to_event_low_pct", 999.0)
    pullback20 = _debug(signal, "pullback_from_recent_high_20_pct")
    pullback60 = _debug(signal, "pullback_from_recent_high_60_pct")
    ret6 = _debug(signal, "ret_6_pct")
    ret12 = _debug(signal, "ret_12_pct")
    ret24 = _debug(signal, "ret_24_pct")
    rsi = _debug(signal, "rsi14")
    stoch = _debug(signal, "stoch_k14")
    mfi = _debug(signal, "mfi14")
    wick = _debug(signal, "lower_wick_share")
    closepos = _debug(signal, "close_pos_candle")
    slope = _debug(signal, "ema20_slope_5_pct")
    new_lows = _debug(signal, "new_low_count_20")
    lower_streak = _debug(signal, "lower_low_streak_5")
    hot_run = _debug(signal, "hot_run_len")
    bars_since_high20 = _debug(signal, "bars_since_recent_high_20", 999.0)
    bars_since_event_low = _debug(signal, "bars_since_event_low", 999.0)
    prior_event_candidates = _debug(signal, "v8_prior_event_candidates", 0.0)
    local_low_5 = _bool_debug(signal, "local_low_5")
    local_low_10 = _bool_debug(signal, "local_low_10")
    local_low_20 = _bool_debug(signal, "local_low_20")

    reasons: list[str] = []
    if brick == "HOT_CHAIN_EVENT_LOW":
        if distance > 0.08:
            reasons.append("V9_HOT_CHAIN_NOT_EVENT_LOW")
        if bars_since_event_low > 0:
            reasons.append("V9_HOT_CHAIN_NOT_FRESH_EVENT_LOW")
        if lower_streak < 3:
            reasons.append("V9_HOT_CHAIN_NOT_TERMINAL_LOWER_LOW")
        if slope < 0.10:
            reasons.append("V9_HOT_CHAIN_EMA_SLOPE_WEAK")
        if pullback20 < 0.18:
            reasons.append("V9_HOT_CHAIN_PULLBACK_SMALL")
        if support > 8:
            reasons.append("V9_HOT_CHAIN_CROWDED_SUPPORT")
    elif brick == "HOT_FIRST_STRONG_RECLAIM":
        if hot_run != 1:
            reasons.append("V9_HOT_FIRST_NOT_FIRST")
        if not (0.55 <= low_zone <= 0.86):
            reasons.append("V9_HOT_FIRST_LOW_ZONE_OUT")
        if closepos < 0.85 and wick < 0.30:
            reasons.append("V9_HOT_FIRST_RECLAIM_WEAK")
        if mfi > 80.0:
            reasons.append("V9_HOT_FIRST_MFI_OVERHEATED")
        if ret24 > 0.60:
            reasons.append("V9_HOT_FIRST_RET24_POST_IMPULSE")
        if bars_since_high20 <= 2 and pullback20 < 0.08:
            reasons.append("V9_HOT_FIRST_NO_PULLBACK_AFTER_HIGH")
        if support > 30 and distance > 0.55:
            reasons.append("V9_HOT_FIRST_CROWDED_FAR_SHELF")
    elif brick == "WARM_STRUCTURAL_RECLAIM":
        strong_reclaim = closepos >= 0.74 or wick >= 0.45
        structural_low = distance <= 0.45 or bars_since_event_low <= 10 or local_low_10 or local_low_20
        if not (0.24 <= low_zone <= 0.64):
            reasons.append("V9_WARM_LOW_ZONE_OUT")
        if not strong_reclaim:
            reasons.append("V9_WARM_RECLAIM_WEAK")
        if not structural_low:
            reasons.append("V9_WARM_NOT_STRUCTURAL_LOW")
        if support < 8 or support > 28:
            reasons.append("V9_WARM_SUPPORT_OUT")
        if ret24 > 0.36:
            reasons.append("V9_WARM_POST_IMPULSE_RET24")
        if mfi > 72.0:
            reasons.append("V9_WARM_MFI_OVERHEATED")
        if new_lows > 9 and closepos < 0.85:
            reasons.append("V9_WARM_FALLING_CHAIN")
        if bars_since_high20 <= 1 and ret12 > 0.22 and pullback20 < 0.12:
            reasons.append("V9_WARM_HIGH_CONTINUATION")
    elif brick == "DEEP_TERMINAL_RECLAIM":
        deep_context = low_zone <= 0.18 or ret24 <= -0.40 or pullback60 >= 1.00
        reclaim = closepos >= 0.35 or wick >= 0.30
        near_low = distance <= 0.45 or low_zone <= 0.05
        if not deep_context:
            reasons.append("V9_DEEP_CONTEXT_WEAK")
        if not reclaim:
            reasons.append("V9_DEEP_RECLAIM_WEAK")
        if not near_low:
            reasons.append("V9_DEEP_TOO_FAR_FROM_LOW")
        if new_lows > 12 or lower_streak > 4:
            reasons.append("V9_DEEP_KNIFE_STILL_FALLING")
        if support > 20 and not (low_zone <= 0.05 and wick >= 0.30):
            reasons.append("V9_DEEP_SUPPORT_TOO_CROWDED")
        if mfi > 55.0 and not (closepos >= 0.75 and low_zone <= 0.18):
            reasons.append("V9_DEEP_MFI_NOT_CAPITULATION")
        if ret6 > 0.25 and ret12 > 0.15 and pullback20 < 0.20:
            reasons.append("V9_DEEP_ALREADY_REBOUNDED")
    else:
        reasons.append("V9_UNKNOWN_BRICK")
    return reasons


def _run_variant(rows: list[dict[str, Any]], manual_entries: list[Any], variant: dict[str, Any]) -> dict[str, Any]:
    source = _source_variant(str(variant["source_family_id"]))
    source_signals, source_suppressed = _filtered_source_signals(rows, source)
    kept: list[dict[str, Any]] = []
    brick_rejected: list[dict[str, Any]] = []
    for signal in source_signals:
        enriched = dict(signal)
        debug = dict(enriched.get("debug") or {})
        reasons = _brick_reject_reasons(enriched, str(variant["brick"]))
        debug["v9_brick"] = str(variant["brick"])
        debug["v9_reject_reasons"] = reasons
        enriched["debug"] = debug
        if reasons:
            enriched["suppress_votes"] = list(enriched.get("suppress_votes", [])) + reasons
            brick_rejected.append(enriched)
            continue
        enriched["family_id"] = str(variant["family_id"])
        enriched["bucket"] = str(variant["bucket"])
        enriched["strategy_scope"] = "entry_only_brick_by_brick_selector_v9"
        enriched["trigger_votes"] = list(enriched.get("trigger_votes", [])) + ["V9_BRICK_PASSED"]
        enriched["suppress_votes"] = list(enriched.get("suppress_votes", []))
        kept.append(enriched)
    signals = _online_duplicate_filter(kept, duplicate_gap_bars=int(variant["duplicate_gap_bars"]))
    score = score_entries(manual_entries, [_to_trade(item) for item in signals])
    return {
        "family_id": str(variant["family_id"]),
        "bucket": str(variant["bucket"]),
        "description_ru": str(variant["description_ru"]),
        "params": {
            "source_family_id": str(variant["source_family_id"]),
            "brick": str(variant["brick"]),
            "duplicate_gap_bars": int(variant["duplicate_gap_bars"]),
            "candidate_for_clean_union": bool(variant.get("candidate_for_clean_union", False)),
            "cooldown_used": False,
        },
        "raw_candidates_total": len(source_signals) + len(source_suppressed),
        "v8_suppressed_candidates_total": len(source_suppressed),
        "brick_rejected_candidates_total": len(brick_rejected),
        "filtered_candidates_total": len(signals),
        "score": _score_summary(score),
        "hit_details": score["hit_details"],
        "missed_target_details": score["missed_target_details"],
        "false_entry_details": score["false_entry_details"][:250],
        "signals": signals,
    }


def _union_result(results: list[dict[str, Any]], manual_entries: list[Any], variant: dict[str, Any]) -> dict[str, Any]:
    source_ids = set(variant["source_family_ids"])
    raw = [signal for result in results if result["family_id"] in source_ids for signal in result["signals"]]
    signals: list[dict[str, Any]] = []
    for signal in _online_duplicate_filter(raw, duplicate_gap_bars=int(variant["duplicate_gap_bars"])):
        enriched = dict(signal)
        enriched["family_id"] = str(variant["family_id"])
        enriched["bucket"] = str(variant["bucket"])
        enriched["strategy_scope"] = "entry_only_brick_by_brick_selector_v9"
        enriched["trigger_votes"] = list(enriched.get("trigger_votes", [])) + ["V9_BRICK_UNION"]
        signals.append(enriched)
    score = score_entries(manual_entries, [_to_trade(item) for item in signals])
    return {
        "family_id": str(variant["family_id"]),
        "bucket": str(variant["bucket"]),
        "description_ru": str(variant["description_ru"]),
        "params": {
            "source_family_ids": sorted(source_ids),
            "duplicate_gap_bars": int(variant["duplicate_gap_bars"]),
            "cooldown_used": False,
        },
        "raw_candidates_total": len(raw),
        "v8_suppressed_candidates_total": 0,
        "brick_rejected_candidates_total": 0,
        "filtered_candidates_total": len(signals),
        "score": _score_summary(score),
        "hit_details": score["hit_details"],
        "missed_target_details": score["missed_target_details"],
        "false_entry_details": score["false_entry_details"][:250],
        "signals": signals,
    }


def _summary_table(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "family_id": item["family_id"],
            "hits": item["score"]["target_hits"],
            "missed": item["score"]["missed_targets"],
            "false": item["score"]["false_entries"],
            "entries": item["score"]["entries_total"],
            "precision": item["score"]["precision"],
            "recall": item["score"]["recall"],
            "f1_visual": item["score"]["f1_visual"],
        }
        for item in results
    ]


def _render_label(rank: int, family_id: str) -> str:
    compact = (
        family_id.lower()
        .replace("v9_01_hot_chain_event_low_brick", "hot_chain_event_low")
        .replace("v9_02_hot_first_strong_reclaim_brick", "hot_first_strong")
        .replace("v9_03_warm_structural_reclaim_brick", "warm_structural")
        .replace("v9_04_deep_terminal_reclaim_brick", "deep_terminal")
        .replace("v9_20_clean_bricks_union", "clean_union")
        .replace("v9_90_research_union_all_bricks_diag", "research_union_all")
    )
    return f"v9_{rank:02d}_{compact[:60]}"


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Brick By Brick Selector V9",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "Контракт: сигнал появляется только после закрытия сигнальной свечи лоя, LONG ставится на `open` следующей свечи, `lookahead=NO`, slippage `5 bps`.",
        "",
        "Граница: V9 выбирает отдельные кирпичи входа. TP/SL, MFE/MAE, future return, entry-candle OHLCV, cooldown-сетки `30/45/60/90` и ML-export не используются.",
        "",
        "| rank | family | hits | miss | false | entries | raw | v8_supp | brick_rej | filtered | precision | recall | f1 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, item in enumerate(payload["best_overall"], 1):
        score = item["score"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{:.4f}` | `{:.4f}` | `{:.4f}` |".format(
                rank,
                item["family_id"],
                score["target_hits"],
                score["missed_targets"],
                score["false_entries"],
                score["entries_total"],
                item["raw_candidates_total"],
                item["v8_suppressed_candidates_total"],
                item["brick_rejected_candidates_total"],
                item["filtered_candidates_total"],
                score["precision"],
                score["recall"],
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
            "V9 не является ML-кандидатом. Это слой разбора: какие механики можно оставить как чистые кирпичи, а какие пока дают слишком много лишних входов. "
            "В ML ничего не передавать до отдельного разрешения и до проверки на следующих днях.",
            "",
        ]
    )
    return "\n".join(lines)


def run_search(manual_entries_path: Path, out_dir: Path, *, render_top: int = 6) -> dict[str, Any]:
    manual_payload, manual_entries = load_manual_entries(manual_entries_path)
    _, rows = _prepare_rows(manual_entries_path)
    _enrich_quality_rows(rows)
    _with_event_features(rows)

    atomic_results = [_run_variant(rows, manual_entries, variant) for variant in VARIANTS if "source_family_id" in variant]
    union_results = [
        _union_result(atomic_results, manual_entries, variant) for variant in VARIANTS if "source_family_ids" in variant
    ]
    results = [*atomic_results, *union_results]
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
            label=_render_label(rank, str(result["family_id"])),
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
        "strategy_scope": "entry_only_brick_by_brick_selector_v9",
        "online_event_state_used": True,
        "online_duplicate_suppression_used": True,
        "brick_by_brick_selector_used": True,
        "cooldown_used": False,
        "future_trade_outcome_used": False,
        "entry_candle_ohlcv_features_used": False,
        "ml_transfer_allowed": False,
        "slippage_bps": SLIPPAGE_BPS,
        "best_overall": results,
        "summary_table": _summary_table(results),
        "rendered_overlays": rendered,
    }
    json_path = out_dir / f"visual_entry_brick_by_brick_selector_v9_{day}_{safe_role}.json"
    md_path = out_dir / f"visual_entry_brick_by_brick_selector_v9_{day}_{safe_role}_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run BRICK_BY_BRICK_SELECTOR_V9 visual-entry diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/brick_by_brick_selector_v9")
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
                "best": [
                    {
                        "family_id": item["family_id"],
                        "raw_candidates_total": item["raw_candidates_total"],
                        "v8_suppressed_candidates_total": item["v8_suppressed_candidates_total"],
                        "brick_rejected_candidates_total": item["brick_rejected_candidates_total"],
                        "filtered_candidates_total": item["filtered_candidates_total"],
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
