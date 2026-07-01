from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.render_visual_entry_overlay import render_family_candidate_overlay
from mlbotnav.visual_entry_generalization_v7_runner import (
    VARIANTS as G7_VARIANTS,
    _online_duplicate_filter,
    _raw_variant_signals,
    _to_trade,
)
from mlbotnav.visual_entry_no_lookahead_candidates import _prepare_rows
from mlbotnav.visual_entry_online_low_event_quality_runner import _with_event_features
from mlbotnav.visual_entry_quality_filter_runner import _enrich_quality_rows
from mlbotnav.visual_entry_score import load_manual_entries, score_entries
from mlbotnav.visual_entry_significant_low_selector_runner import SLIPPAGE_BPS, _score_summary


STATUS = "DEV_NEGATIVE_CONTEXT_SUPPRESSION_V8_ENTRY_ONLY_NO_ML"


VARIANTS: list[dict[str, Any]] = [
    {
        "family_id": "V8_01_HOT_FIRST_NEGATIVE_SUPPRESSION",
        "source_family_id": "G7_01_HOT_FIRST_RECLAIM_DIAG",
        "bucket": "HOT_FIRST_NEGATIVE_SUPPRESSION",
        "duplicate_gap_bars": 4,
        "description_ru": "Hot-first V7 плюс запреты верхней горячей полки, post-impulse и не-первого hot-сигнала.",
    },
    {
        "family_id": "V8_02_HOT_CHAIN_EVENT_LOW_SUPPRESSION",
        "source_family_id": "G7_02_HOT_CHAIN_DIP_DIAG",
        "bucket": "HOT_CHAIN_EVENT_LOW_SUPPRESSION",
        "duplicate_gap_bars": 2,
        "description_ru": "Hot-chain V7 только если это event-low рядом с минимумом серии, а не рядовой микролой.",
    },
    {
        "family_id": "V8_03_WARM_RETEST_NEGATIVE_SUPPRESSION",
        "source_family_id": "G7_03_WARM_RETEST_DIAG",
        "bucket": "WARM_RETEST_NEGATIVE_SUPPRESSION",
        "duplicate_gap_bars": 5,
        "description_ru": "Warm-retest V7 плюс запреты слабого reclaim, crowded shelf, down-drift и перегретого continuation.",
    },
    {
        "family_id": "V8_04_DEEP_EVENT_NEGATIVE_SUPPRESSION",
        "source_family_id": "G7_04_DEEP_EVENT_RECLAIM_DIAG",
        "bucket": "DEEP_EVENT_NEGATIVE_SUPPRESSION",
        "duplicate_gap_bars": 6,
        "description_ru": "Deep/event V7 плюс запреты падающего ножа без reclaim, far-from-event-low и post-pump контекста.",
    },
    {
        "family_id": "V8_20_UNION_NEGATIVE_SUPPRESSION",
        "source_family_ids": [
            "V8_01_HOT_FIRST_NEGATIVE_SUPPRESSION",
            "V8_02_HOT_CHAIN_EVENT_LOW_SUPPRESSION",
            "V8_03_WARM_RETEST_NEGATIVE_SUPPRESSION",
            "V8_04_DEEP_EVENT_NEGATIVE_SUPPRESSION",
        ],
        "bucket": "UNION_NEGATIVE_SUPPRESSION",
        "duplicate_gap_bars": 3,
        "description_ru": "Union V8 после отрицательных фильтров по каждому режиму.",
    },
]


def _debug(signal: dict[str, Any], key: str, default: float = 0.0) -> float:
    value = (signal.get("debug") or {}).get(key, default)
    if value is None:
        return default
    return float(value)


def _negative_reasons(signal: dict[str, Any], source_family_id: str) -> list[str]:
    low_zone = _debug(signal, "low_zone", 1.0)
    support = _debug(signal, "support_touch_count_60")
    distance = _debug(signal, "distance_to_event_low_pct", 999.0)
    pullback = _debug(signal, "pullback_from_recent_high_20_pct")
    ret12 = _debug(signal, "ret_12_pct")
    ret24 = _debug(signal, "ret_24_pct")
    mfi = _debug(signal, "mfi14")
    closepos = _debug(signal, "close_pos_candle")
    wick = _debug(signal, "lower_wick_share")
    slope = _debug(signal, "ema20_slope_5_pct")
    new_lows = _debug(signal, "new_low_count_20")
    lower_streak = _debug(signal, "lower_low_streak_5")
    hot_run = _debug(signal, "hot_run_len")
    ret6 = _debug(signal, "ret_6_pct")
    rsi = _debug(signal, "rsi14")
    stoch = _debug(signal, "stoch_k14")
    bars_since_high20 = _debug(signal, "bars_since_recent_high_20", 999.0)
    event_age = _debug(signal, "low_event_age_bars", 999.0)
    bars_since_event_low = _debug(signal, "bars_since_event_low", 999.0)
    prior_event_candidates = _debug(signal, "v8_prior_event_candidates", 0.0)
    local_low_5 = bool((signal.get("debug") or {}).get("local_low_5"))
    local_low_10 = bool((signal.get("debug") or {}).get("local_low_10"))
    local_low_20 = bool((signal.get("debug") or {}).get("local_low_20"))
    has_local_low = local_low_5 or local_low_10 or local_low_20
    strong_allow = (
        closepos >= 0.75
        or wick >= 0.30
        or local_low_10
        or local_low_20
        or (low_zone <= 0.15 and ret24 <= -0.60 and mfi <= 40.0)
    )

    reasons: list[str] = []
    if (
        0.25 <= low_zone <= 0.80
        and pullback < 0.12
        and abs(ret24) < 0.20
        and support >= 8
        and wick < 0.25
        and closepos < 0.65
        and not (local_low_10 or local_low_20)
    ):
        reasons.append("NCS01_SIDEWAYS_MICRO_LOW")
    if (
        low_zone >= 0.78
        and ret12 >= 0.05
        and pullback <= 0.25
        and max(rsi, stoch, mfi) >= 70.0
        and not has_local_low
        and closepos < 0.85
    ):
        reasons.append("NCS02_HOT_UPPER_SHELF")
    if (
        prior_event_candidates >= 3
        and event_age > 3
        and bars_since_event_low > 3
        and distance > 0.20
        and not strong_allow
    ):
        reasons.append("NCS03_RETEST_SERIES_SATURATION")
    if (
        (ret6 >= 0.18 or ret12 >= 0.30)
        and bars_since_high20 <= 3
        and pullback <= 0.18
        and low_zone >= 0.45
        and distance > 0.15
        and closepos < 0.85
        and wick < 0.25
        and not local_low_5
    ):
        reasons.append("NCS04_POST_IMPULSE_NO_PULLBACK")
    if (
        not has_local_low
        and wick < 0.12
        and closepos < 0.35
        and distance > 0.15
        and not (low_zone <= 0.15 and ret24 <= -0.60)
    ):
        reasons.append("NCS05_WEAK_RECLAIM_NO_LOCAL_LOW")

    if source_family_id == "G7_01_HOT_FIRST_RECLAIM_DIAG":
        if hot_run != 1:
            reasons.append("HOT_NOT_FIRST_SIGNAL")
        if low_zone > 0.87:
            reasons.append("HOT_UPPER_SHELF")
        if ret24 > 0.62:
            reasons.append("HOT_POST_IMPULSE_RET24")
        if mfi > 85.0:
            reasons.append("HOT_MFI_EXHAUSTED")
        if closepos < 0.55:
            reasons.append("HOT_WEAK_RECLAIM")
        if support > 34 and distance > 0.70:
            reasons.append("HOT_OVERCROWDED_FAR_SHELF")
    elif source_family_id == "G7_02_HOT_CHAIN_DIP_DIAG":
        if distance > 0.08:
            reasons.append("HOT_CHAIN_NOT_EVENT_LOW")
        if lower_streak < 3:
            reasons.append("HOT_CHAIN_NOT_LOWER_LOW_TERMINAL")
        if pullback < 0.18:
            reasons.append("HOT_CHAIN_PULLBACK_TOO_SMALL")
        if slope < 0.10:
            reasons.append("HOT_CHAIN_EMA_NOT_STRONG")
        if support > 8:
            reasons.append("HOT_CHAIN_TOO_CROWDED")
    elif source_family_id == "G7_03_WARM_RETEST_DIAG":
        if closepos < 0.45 and wick < 0.18:
            reasons.append("WARM_NO_RECLAIM")
        if support < 8 and distance > 0.12:
            reasons.append("WARM_SUPPORT_TOO_WEAK")
        if ret12 > 0.55 or ret24 > 0.55:
            reasons.append("WARM_POST_IMPULSE")
        if low_zone > 0.72 and support > 28:
            reasons.append("WARM_HIGH_CROWDED_SHELF")
        if new_lows > 10 and closepos < 0.75:
            reasons.append("WARM_FALLING_CHAIN_CONTINUES")
        if slope < -0.09 and closepos < 0.80:
            reasons.append("WARM_DOWNDRIFT_NO_STRONG_RECLAIM")
    elif source_family_id == "G7_04_DEEP_EVENT_RECLAIM_DIAG":
        if closepos < 0.32 and wick < 0.20:
            reasons.append("DEEP_NO_RECLAIM")
        if distance > 0.75:
            reasons.append("DEEP_FAR_FROM_EVENT_LOW")
        if new_lows > 12 or lower_streak > 4:
            reasons.append("DEEP_FALLING_KNIFE_CONTINUES")
        if ret24 > 0.45 and low_zone > 0.35:
            reasons.append("DEEP_POST_PUMP_NOT_DEEP")
        if support > 45:
            reasons.append("DEEP_OVERCROWDED_SUPPORT")
    return reasons


def _source_variant(source_family_id: str) -> dict[str, Any]:
    for variant in G7_VARIANTS:
        if variant.get("family_id") == source_family_id:
            return variant
    raise KeyError(source_family_id)


def _filtered_source_signals(rows: list[dict[str, Any]], variant: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source_family_id = str(variant["source_family_id"])
    raw = _raw_variant_signals(rows, _source_variant(source_family_id))
    kept: list[dict[str, Any]] = []
    suppressed: list[dict[str, Any]] = []
    event_counts: dict[str, int] = {}
    for signal in raw:
        enriched = dict(signal)
        debug = dict(enriched.get("debug") or {})
        event_key = str(debug.get("low_event_start_idx"))
        debug["v8_prior_event_candidates"] = event_counts.get(event_key, 0)
        event_counts[event_key] = event_counts.get(event_key, 0) + 1
        debug["v8_source_family_id"] = source_family_id
        enriched["debug"] = debug
        reasons = _negative_reasons(enriched, source_family_id)
        debug["v8_negative_reasons"] = reasons
        enriched["debug"] = debug
        if reasons:
            enriched["suppress_votes"] = list(enriched.get("suppress_votes", [])) + reasons
            suppressed.append(enriched)
            continue
        enriched["family_id"] = str(variant["family_id"])
        enriched["bucket"] = str(variant["bucket"])
        enriched["trigger_votes"] = list(enriched.get("trigger_votes", [])) + ["V8_NEGATIVE_CONTEXT_PASSED"]
        enriched["suppress_votes"] = list(enriched.get("suppress_votes", []))
        kept.append(enriched)
    signals = _online_duplicate_filter(kept, duplicate_gap_bars=int(variant["duplicate_gap_bars"]))
    return signals, suppressed


def _run_variant(rows: list[dict[str, Any]], manual_entries: list[Any], variant: dict[str, Any]) -> dict[str, Any]:
    signals, suppressed = _filtered_source_signals(rows, variant)
    score = score_entries(manual_entries, [_to_trade(item) for item in signals])
    return {
        "family_id": str(variant["family_id"]),
        "bucket": str(variant["bucket"]),
        "description_ru": str(variant["description_ru"]),
        "params": {
            "source_family_id": str(variant["source_family_id"]),
            "duplicate_gap_bars": int(variant["duplicate_gap_bars"]),
            "cooldown_used": False,
        },
        "raw_candidates_total": len(signals) + len(suppressed),
        "suppressed_candidates_total": len(suppressed),
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
    signals = []
    for signal in _online_duplicate_filter(raw, duplicate_gap_bars=int(variant["duplicate_gap_bars"])):
        enriched = dict(signal)
        enriched["family_id"] = str(variant["family_id"])
        enriched["bucket"] = str(variant["bucket"])
        enriched["trigger_votes"] = list(enriched.get("trigger_votes", [])) + ["V8_UNION"]
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
        "suppressed_candidates_total": 0,
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
        .replace("v8_01_hot_first_negative_suppression", "hot_first_neg")
        .replace("v8_02_hot_chain_event_low_suppression", "hot_chain_event")
        .replace("v8_03_warm_retest_negative_suppression", "warm_neg")
        .replace("v8_04_deep_event_negative_suppression", "deep_neg")
        .replace("v8_20_union_negative_suppression", "union_neg")
    )
    return f"v8_{rank:02d}_{compact[:60]}"


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Negative Context Suppression V8",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "Контракт: сигнальная свеча закрыта, LONG ставится на `open` следующей свечи, `lookahead=NO`, slippage `5 bps`.",
        "",
        "Граница: V8 только подавляет отрицательные контексты поверх V7; TP/SL, MFE/MAE, future return, entry-candle OHLCV, cooldown-сетки `30/45/60/90` и ML-export не используются.",
        "",
        "| rank | family | hits | miss | false | entries | raw | suppressed | filtered | precision | recall | f1 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, item in enumerate(payload["best_overall"], 1):
        score = item["score"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{:.4f}` | `{:.4f}` | `{:.4f}` |".format(
                rank,
                item["family_id"],
                score["target_hits"],
                score["missed_targets"],
                score["false_entries"],
                score["entries_total"],
                item["raw_candidates_total"],
                item["suppressed_candidates_total"],
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
            "V8 проверяет, можно ли подавить шум V7 отрицательными past-only контекстами. "
            "Если слой все еще не проходит validation/holdout или теряет большую часть ручных целей, в ML его не передавать.",
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
        "strategy_scope": "entry_only_negative_context_suppression_v8",
        "online_event_state_used": True,
        "online_duplicate_suppression_used": True,
        "cooldown_used": False,
        "future_trade_outcome_used": False,
        "entry_candle_ohlcv_features_used": False,
        "ml_transfer_allowed": False,
        "slippage_bps": SLIPPAGE_BPS,
        "best_overall": results,
        "summary_table": _summary_table(results),
        "rendered_overlays": rendered,
    }
    json_path = out_dir / f"visual_entry_negative_context_suppression_v8_{day}_{safe_role}.json"
    md_path = out_dir / f"visual_entry_negative_context_suppression_v8_{day}_{safe_role}_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run NEGATIVE_CONTEXT_SUPPRESSION_V8 visual-entry diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/negative_context_suppression_v8")
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
                        "suppressed_candidates_total": item["suppressed_candidates_total"],
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
