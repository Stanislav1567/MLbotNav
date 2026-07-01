from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.render_visual_entry_overlay import render_family_candidate_overlay
from mlbotnav.visual_entry_no_lookahead_candidates import _prepare_rows
from mlbotnav.visual_entry_quality_filter_runner import _enrich_quality_rows
from mlbotnav.visual_entry_regime_false_suppression_runner import (
    SUPPRESSION_VARIANTS,
    _enrich_filter_debug,
    _passes_filters,
)
from mlbotnav.visual_entry_regime_split_ranker_runner import (
    _raw_candidates as _regime_raw_candidates,
    _select_online_no_rewrite,
)
from mlbotnav.visual_entry_score import TradeEntry, load_manual_entries, score_entries
from mlbotnav.visual_entry_significant_low_selector_runner import SLIPPAGE_BPS, _score_summary


STATUS = "DEV_ONLINE_LOW_EVENT_QUALITY_V3_ENTRY_ONLY_NO_ML"


SOURCE_FAMILIES = {
    "FSV02_DEEP_CAPITULATION_SOFT_NOWICK",
    "FSV03_HOT_SUPPORT_STRONG_RECLAIM",
    "FSV05_TREND_DIP_EMA_RECLAIM",
    "FSV07_STRUCTURE_VOLUME_RETEST",
}


EVENT_VARIANTS: list[dict[str, Any]] = [
    {
        "family_id": "OLEV01_DEEP_MATURE_EVENT",
        "source_family_ids": ["FSV02_DEEP_CAPITULATION_SOFT_NOWICK"],
        "duplicate_gap_bars": 8,
        "quality_min_score": 7,
        "filters": {
            "low_event_age_bars_min": 0,
            "low_event_age_bars_max": 150,
            "candidate_order_in_event_min": 1,
            "distance_to_event_low_pct_max": 0.45,
            "pullback_from_recent_high_20_pct_min": 0.30,
        },
        "suppress": {
            "hot_pump": False,
            "overcrowded_hot_support": False,
            "deep_no_reclaim_requires_maturity": True,
        },
        "description_ru": "Deep event: оставляет зрелые капитуляционные low около event-low, без требования сделки или будущего роста.",
    },
    {
        "family_id": "OLEV02_HOT_RECLAIM_EVENT_FILTERED",
        "source_family_ids": ["FSV03_HOT_SUPPORT_STRONG_RECLAIM"],
        "duplicate_gap_bars": 8,
        "quality_min_score": 7,
        "filters": {
            "low_event_age_bars_min": 1,
            "low_event_age_bars_max": 170,
            "candidate_order_in_event_min": 1,
            "candidate_order_in_event_max": 140,
            "distance_to_event_low_pct_max": 0.65,
            "pullback_from_recent_high_20_pct_min": 0.05,
            "low_zone_max": 0.78,
        },
        "suppress": {
            "hot_pump": True,
            "overcrowded_hot_support": True,
            "deep_no_reclaim_requires_maturity": False,
        },
        "description_ru": "Hot/support event: вход только если reclaim находится рядом с event-low, а не на горячей верхней полке.",
    },
    {
        "family_id": "OLEV03_TREND_PULLBACK_EVENT_FILTERED",
        "source_family_ids": ["FSV05_TREND_DIP_EMA_RECLAIM"],
        "duplicate_gap_bars": 8,
        "quality_min_score": 7,
        "filters": {
            "low_event_age_bars_min": 1,
            "low_event_age_bars_max": 180,
            "candidate_order_in_event_min": 1,
            "candidate_order_in_event_max": 145,
            "distance_to_event_low_pct_max": 0.68,
            "pullback_from_recent_high_20_pct_min": 0.05,
            "low_zone_max": 0.78,
        },
        "suppress": {
            "hot_pump": True,
            "overcrowded_hot_support": True,
            "deep_no_reclaim_requires_maturity": False,
        },
        "description_ru": "Trend pullback event: берет откат в живом движении, но режет верхние полки и поздние шумные касания.",
    },
    {
        "family_id": "OLEV04_STRUCTURE_VOLUME_NEGATIVE_CONTEXT",
        "source_family_ids": ["FSV07_STRUCTURE_VOLUME_RETEST"],
        "duplicate_gap_bars": 8,
        "quality_min_score": 7,
        "filters": {
            "low_event_age_bars_min": 1,
            "low_event_age_bars_max": 180,
            "candidate_order_in_event_min": 1,
            "candidate_order_in_event_max": 145,
            "distance_to_event_low_pct_max": 0.68,
            "pullback_from_recent_high_20_pct_min": 0.05,
            "low_zone_max": 0.78,
        },
        "suppress": {
            "hot_pump": True,
            "overcrowded_hot_support": True,
            "structure_volume_negative_context": True,
        },
        "description_ru": "Structure/volume event: объем учитывается только в низком или нейтрально-негативном контексте.",
    },
    {
        "family_id": "OLEV20_UNION_EVENT_QUALITY_BALANCED",
        "source_family_ids": [
            "OLEV01_DEEP_MATURE_EVENT",
            "OLEV02_HOT_RECLAIM_EVENT_FILTERED",
            "OLEV03_TREND_PULLBACK_EVENT_FILTERED",
            "OLEV04_STRUCTURE_VOLUME_NEGATIVE_CONTEXT",
        ],
        "duplicate_gap_bars": 6,
        "description_ru": "Сводный event-quality слой из четырех режимных источников.",
    },
    {
        "family_id": "OLEV21_UNION_EVENT_QUALITY_STRICT",
        "source_family_ids": [
            "OLEV01_DEEP_MATURE_EVENT",
            "OLEV02_HOT_RECLAIM_EVENT_FILTERED",
            "OLEV04_STRUCTURE_VOLUME_NEGATIVE_CONTEXT",
        ],
        "duplicate_gap_bars": 8,
        "description_ru": "Более строгий event-quality union без широкого trend recall.",
    },
]


def _value(row: dict[str, Any], key: str, default: float = 0.0) -> float:
    value = row.get(key)
    if value is None:
        return default
    return float(value)


def _low_zone(row: dict[str, Any]) -> float:
    return min(_value(row, "range_pos_60", 1.0), _value(row, "low_range_pos_60", 1.0))


def _with_event_features(rows: list[dict[str, Any]]) -> None:
    active = False
    event_start_idx = 0
    event_low_idx = 0
    event_low_price = 0.0
    candidate_order = 0

    for idx, row in enumerate(rows):
        low_zone = _low_zone(row)
        low_like = (
            low_zone <= 0.78
            or bool(row.get("local_low_10"))
            or (_value(row, "support_touch_count_60", 0.0) >= 10 and low_zone <= 0.88)
        )
        reset = active and (
            (low_zone >= 0.94 and _value(row, "ret_6_pct", 0.0) >= 0.35)
            or idx - event_start_idx > 180
        )
        if reset:
            active = False
            candidate_order = 0
        if not active and low_like:
            active = True
            event_start_idx = idx
            event_low_idx = idx
            event_low_price = float(row["low"])
            candidate_order = 0
        if active and float(row["low"]) <= event_low_price:
            event_low_idx = idx
            event_low_price = float(row["low"])
        candidate_like = active and (
            bool(row.get("local_low_5"))
            or _value(row, "lower_wick_share", 0.0) >= 0.20
            or _value(row, "close_pos_candle", 0.0) >= 0.65
        ) and low_zone <= 0.88
        if candidate_like:
            candidate_order += 1

        recent20 = rows[max(0, idx - 19) : idx + 1]
        recent60 = rows[max(0, idx - 59) : idx + 1]
        high20_idx_rel, high20 = max(enumerate(recent20), key=lambda item: float(item[1]["high"]))
        high60_idx_rel, high60 = max(enumerate(recent60), key=lambda item: float(item[1]["high"]))
        high20_idx = max(0, idx - 19) + high20_idx_rel
        high60_idx = max(0, idx - 59) + high60_idx_rel

        row["low_event_active"] = active
        row["low_event_start_idx"] = event_start_idx if active else None
        row["low_event_age_bars"] = idx - event_start_idx if active else 999
        row["candidate_order_in_event"] = candidate_order if active else 0
        row["event_low_idx"] = event_low_idx if active else None
        row["bars_since_event_low"] = idx - event_low_idx if active else 999
        row["distance_to_event_low_pct"] = (
            (float(row["low"]) - event_low_price) / float(row["close"]) * 100.0
            if active and float(row["close"]) > 0
            else 999.0
        )
        row["bars_since_recent_high_20"] = idx - high20_idx
        row["bars_since_recent_high_60"] = idx - high60_idx
        row["pullback_from_recent_high_20_pct"] = (
            (float(high20["high"]) - float(row["low"])) / float(high20["high"]) * 100.0
            if float(high20["high"]) > 0
            else 0.0
        )
        row["pullback_from_recent_high_60_pct"] = (
            (float(high60["high"]) - float(row["low"])) / float(high60["high"]) * 100.0
            if float(high60["high"]) > 0
            else 0.0
        )


def _filter_value(signal: dict[str, Any], key: str) -> float:
    dbg = signal.get("debug") or {}
    aliases = {
        "low_zone": "low_zone",
        "low_event_age_bars": "low_event_age_bars",
        "candidate_order_in_event": "candidate_order_in_event",
        "distance_to_event_low_pct": "distance_to_event_low_pct",
        "pullback_from_recent_high_20_pct": "pullback_from_recent_high_20_pct",
        "low_zone": "low_zone",
    }
    metric_key = aliases.get(key, key)
    default = 999.0 if key.endswith("_bars") or "distance" in key else 0.0
    return float(dbg.get(metric_key, default))


def _passes_event_filters(signal: dict[str, Any], filters: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    passed: list[str] = []
    suppressed: list[str] = []
    for key, threshold in filters.items():
        metric = key.removesuffix("_min").removesuffix("_max")
        current = _filter_value(signal, metric)
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


def _event_quality_score(signal: dict[str, Any]) -> tuple[int, list[str], list[str]]:
    dbg = signal.get("debug") or {}
    score = 0
    votes: list[str] = []
    suppress: list[str] = []

    low_zone = float(dbg.get("low_zone", 1.0))
    event_age = float(dbg.get("low_event_age_bars", 999.0))
    order = float(dbg.get("candidate_order_in_event", 0.0))
    distance = float(dbg.get("distance_to_event_low_pct", 999.0))
    pullback20 = float(dbg.get("pullback_from_recent_high_20_pct", 0.0))
    ret24 = float(dbg.get("ret_24_pct", 0.0))
    wick = float(dbg.get("lower_wick_share", 0.0))
    closepos = float(dbg.get("close_pos_candle", 0.0))
    rsi = float(dbg.get("rsi14", 100.0))
    stoch = float(dbg.get("stoch_k14", 100.0))
    mfi = float(dbg.get("mfi14", 100.0))
    support = float(dbg.get("support_touch_count_60", 0.0))

    if event_age <= 90:
        score += 1
        votes.append("EVENT_AGE_OK")
    if 1 <= order <= 8:
        score += 2
        votes.append("CANDIDATE_ORDER_IN_EVENT_OK")
    if distance <= 0.20:
        score += 2
        votes.append("NEAR_EVENT_LOW")
    elif distance <= 0.40:
        score += 1
        votes.append("CLOSE_TO_EVENT_LOW")
    if pullback20 >= 0.20:
        score += 1
        votes.append("PULLBACK_FROM_RECENT_HIGH")
    if wick >= 0.20 or closepos >= 0.65:
        score += 1
        votes.append("RECLAIM_OR_WICK")
    if low_zone <= 0.35:
        score += 1
        votes.append("LOW_ZONE_REAL")
    if ret24 <= 0.05 or mfi <= 60.0:
        score += 1
        votes.append("NOT_HOT_CONTEXT")
    if support > 24 and ret24 > 0.0 and low_zone > 0.45 and max(rsi, stoch, mfi) > 70.0:
        score -= 2
        suppress.append("SUPPORT_OVERCROWDING_HOT")
    return score, votes, suppress


def _passes_named_suppression(signal: dict[str, Any], suppress_cfg: dict[str, Any]) -> tuple[bool, list[str]]:
    dbg = signal.get("debug") or {}
    low_zone = float(dbg.get("low_zone", 1.0))
    ret12 = float(dbg.get("ret_12_pct", 0.0))
    ret24 = float(dbg.get("ret_24_pct", 0.0))
    rsi = float(dbg.get("rsi14", 100.0))
    stoch = float(dbg.get("stoch_k14", 100.0))
    mfi = float(dbg.get("mfi14", 100.0))
    wick = float(dbg.get("lower_wick_share", 0.0))
    closepos = float(dbg.get("close_pos_candle", 0.0))
    support = float(dbg.get("support_touch_count_60", 0.0))
    order = float(dbg.get("candidate_order_in_event", 0.0))
    new_lows = float(dbg.get("new_low_count_20", 0.0))
    suppressed: list[str] = []

    if suppress_cfg.get("hot_pump") and ret24 > 0.05 and low_zone > 0.50 and max(rsi, stoch, mfi) > 70.0 and wick < 0.25:
        suppressed.append("HOT_PUMP_UPPER_SHELF")
    if suppress_cfg.get("overcrowded_hot_support") and support > 26 and ret24 > 0.0 and low_zone > 0.42 and closepos < 0.90:
        suppressed.append("OVERCROWDED_HOT_SUPPORT")
    if suppress_cfg.get("deep_no_reclaim_requires_maturity"):
        if wick < 0.18 and closepos < 0.25 and not (ret12 <= -0.35 and ret24 <= -0.55 and new_lows >= 4 and order >= 1):
            suppressed.append("DEEP_NO_RECLAIM_NOT_MATURE")
    if suppress_cfg.get("structure_volume_negative_context"):
        if ret24 > 0.10 and mfi > 65.0 and low_zone > 0.45:
            suppressed.append("STRUCTURE_VOLUME_POSITIVE_CONTEXT")
    return not suppressed, suppressed


def _enrich_event_debug(signal: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    enriched = _enrich_filter_debug(signal, row)
    dbg = dict(enriched.get("debug") or {})
    for key in (
        "low_event_active",
        "low_event_age_bars",
        "candidate_order_in_event",
        "bars_since_event_low",
        "distance_to_event_low_pct",
        "bars_since_recent_high_20",
        "bars_since_recent_high_60",
        "pullback_from_recent_high_20_pct",
        "pullback_from_recent_high_60_pct",
    ):
        dbg[key] = row.get(key)
    enriched["debug"] = dbg
    return enriched


def _source_candidates(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for variant in SUPPRESSION_VARIANTS:
        family_id = str(variant["family_id"])
        if family_id not in SOURCE_FAMILIES:
            continue
        source_variant = {
            "family_id": family_id,
            "regime": variant["regime"],
            "min_score": int(variant["source_min_score"]),
            "cluster_gap_bars": int(variant["duplicate_gap_bars"]),
            "rank_mode": variant["rank_mode"],
        }
        signals: list[dict[str, Any]] = []
        for raw_signal in _regime_raw_candidates(rows, source_variant):
            row = rows[int(raw_signal["signal_row_index"])]
            signal = _enrich_event_debug(raw_signal, row)
            ok, passed_votes, suppress_votes = _passes_filters(signal, dict(variant["filters"]))
            if not ok:
                continue
            enriched = dict(signal)
            enriched["family_id"] = family_id
            enriched["source_family_id"] = family_id
            enriched["bucket"] = str(variant["regime"])
            enriched["regime"] = str(variant["regime"])
            enriched["confirm_votes"] = list(enriched.get("confirm_votes", [])) + passed_votes
            enriched["suppress_votes"] = list(enriched.get("suppress_votes", [])) + suppress_votes
            enriched["trigger_votes"] = list(enriched.get("trigger_votes", [])) + ["FSV_SOURCE_PASS"]
            signals.append(enriched)
        out[family_id] = signals
    return out


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


def _run_event_variant(
    source_by_family: dict[str, list[dict[str, Any]]],
    manual_entries: list[Any],
    variant: dict[str, Any],
) -> dict[str, Any]:
    raw: list[dict[str, Any]] = []
    for source_id in variant["source_family_ids"]:
        raw.extend(source_by_family.get(str(source_id), []))

    filtered: list[dict[str, Any]] = []
    suppressed_total = 0
    for signal in sorted(raw, key=lambda item: int(item["signal_row_index"])):
        score, quality_votes, score_suppress = _event_quality_score(signal)
        filter_ok, filter_votes, filter_suppress = _passes_event_filters(signal, dict(variant["filters"]))
        suppress_ok, named_suppress = _passes_named_suppression(signal, dict(variant.get("suppress") or {}))
        if score < int(variant["quality_min_score"]) or not filter_ok or not suppress_ok or score_suppress:
            suppressed_total += 1
            continue
        enriched = dict(signal)
        enriched["family_id"] = str(variant["family_id"])
        enriched["bucket"] = "ONLINE_LOW_EVENT_QUALITY"
        enriched["event_quality_score"] = score
        enriched["confirm_votes"] = list(enriched.get("confirm_votes", [])) + quality_votes + filter_votes
        enriched["suppress_votes"] = list(enriched.get("suppress_votes", [])) + score_suppress + filter_suppress + named_suppress
        enriched["trigger_votes"] = list(enriched.get("trigger_votes", [])) + ["ONLINE_LOW_EVENT_QUALITY_PASS"]
        filtered.append(enriched)

    signals = _select_online_no_rewrite(filtered, min_gap_bars=int(variant["duplicate_gap_bars"]))
    score = score_entries(manual_entries, [_to_trade(item) for item in signals])
    return {
        "family_id": str(variant["family_id"]),
        "bucket": "ONLINE_LOW_EVENT_QUALITY",
        "regime": "EVENT_QUALITY",
        "description_ru": str(variant["description_ru"]),
        "params": {
            "source_family_ids": list(variant["source_family_ids"]),
            "duplicate_gap_bars": int(variant["duplicate_gap_bars"]),
            "quality_min_score": int(variant["quality_min_score"]),
            "filters": dict(variant["filters"]),
            "suppress": dict(variant.get("suppress") or {}),
            "cooldown_used": False,
        },
        "raw_candidates_total": len(raw),
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
            enriched["bucket"] = "ONLINE_LOW_EVENT_QUALITY_UNION"
            enriched["trigger_votes"] = list(enriched.get("trigger_votes", [])) + ["OLEV_UNION"]
            raw.append(enriched)
    signals = _select_online_no_rewrite(raw, min_gap_bars=int(params["duplicate_gap_bars"]))
    score = score_entries(manual_entries, [_to_trade(item) for item in signals])
    return {
        "family_id": str(params["family_id"]),
        "bucket": "ONLINE_LOW_EVENT_QUALITY_UNION",
        "regime": "EVENT_QUALITY_UNION",
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
        "# Online Low Event Quality V3",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "Контракт: entry-only, signal-свеча закрыта, вход LONG на `open` следующей свечи, `lookahead=NO`, slippage `5 bps`.",
        "",
        "Граница: сделки, TP/SL, MFE/MAE, future return, entry-candle high/low/close/volume, cooldown-сетки `30/45/60/90` и ML-export не используются.",
        "",
        "Event-state строится online по свечам до signal включительно: возраст low/support-события, порядок кандидата, расстояние до event-low и откат от recent high.",
        "",
        "| rank | family | hits | miss | false | entries | raw | suppressed | filtered | f1 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, item in enumerate(payload["best_overall"], 1):
        score = item["score"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{:.4f}` |".format(
                rank,
                item["family_id"],
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
            "V3 проверяет event-quality слой для low-входов. Это diagnostic-only слой: не ML-кандидат и не production GO без validation/holdout и ручного подтверждения.",
            "",
        ]
    )
    return "\n".join(lines)


def run_search(manual_entries_path: Path, out_dir: Path, *, render_top: int = 8) -> dict[str, Any]:
    manual_payload, manual_entries = load_manual_entries(manual_entries_path)
    _, rows = _prepare_rows(manual_entries_path)
    _enrich_quality_rows(rows)
    _with_event_features(rows)

    source_by_family = _source_candidates(rows)
    event_variants = [item for item in EVENT_VARIANTS if "quality_min_score" in item]
    union_variants = [item for item in EVENT_VARIANTS if "quality_min_score" not in item]
    event_results = [_run_event_variant(source_by_family, manual_entries, variant) for variant in event_variants]
    union_results = [_run_union(event_results, manual_entries, variant) for variant in union_variants]
    results = [item for item in event_results + union_results if int(item["score"]["entries_total"]) > 0]
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
            label=f"online_low_event_quality_v3_{rank:02d}_{result['family_id'].lower()}",
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
        "strategy_scope": "entry_only_online_low_event_quality",
        "online_event_state_used": True,
        "online_duplicate_suppression_used": True,
        "cooldown_used": False,
        "future_trade_outcome_used": False,
        "entry_candle_ohlcv_features_used": False,
        "ml_transfer_allowed": False,
        "source_families": sorted(SOURCE_FAMILIES),
        "best_overall": results,
        "rendered_overlays": rendered,
    }
    json_path = out_dir / f"visual_entry_online_low_event_quality_v3_{day}_{safe_role}.json"
    md_path = out_dir / f"visual_entry_online_low_event_quality_v3_{day}_{safe_role}_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run online low event-quality V3 visual-entry diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/online_low_event_quality")
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
