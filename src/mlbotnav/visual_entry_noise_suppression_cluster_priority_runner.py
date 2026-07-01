from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.render_visual_entry_overlay import render_family_candidate_overlay
from mlbotnav.visual_entry_deep_capitulation_reclaim_runner import run_search as _run_deep_search
from mlbotnav.visual_entry_no_lookahead_candidates import _prepare_rows
from mlbotnav.visual_entry_quality_filter_runner import _enrich_quality_rows
from mlbotnav.visual_entry_score import TradeEntry, load_manual_entries, score_entries


STATUS = "DEV_NOISE_SUPPRESSION_CLUSTER_PRIORITY_DIAGNOSTIC_NO_ML"


CLUSTER_VARIANTS: list[dict[str, Any]] = [
    {
        "variant_id": "CP01_DQ01_CLUSTER10_SCORE12",
        "source_family_ids": ("DQ01_EQ01_PLUS_DEEP_RECLAIM",),
        "cluster_gap_bars": 10,
        "min_priority_score": 12,
        "low_zone_max": 0.35,
        "osc_max": 60.0,
        "mfi_max": 70.0,
        "wick_min": 0.12,
        "closepos_min": 0.12,
        "volz_min": 0.8,
        "support_touches_min": 2,
        "max_lower_low_streak": 4,
        "max_new_low_count_20": 12,
        "ret6_max": -0.12,
        "ret12_max": -0.25,
        "ret24_max": -0.35,
        "bad_slope_pct": -0.25,
        "bad_slope_closepos_min": 0.15,
        "description_ru": "Основной noise-suppression слой поверх DQ01: короткий кластер и высокий priority-score.",
    },
    {
        "variant_id": "CP02_DQ01_CLUSTER08_SCORE12",
        "source_family_ids": ("DQ01_EQ01_PLUS_DEEP_RECLAIM",),
        "cluster_gap_bars": 8,
        "min_priority_score": 12,
        "low_zone_max": 0.35,
        "osc_max": 60.0,
        "mfi_max": 70.0,
        "wick_min": 0.12,
        "closepos_min": 0.12,
        "volz_min": 0.8,
        "support_touches_min": 2,
        "max_lower_low_streak": 4,
        "max_new_low_count_20": 12,
        "ret6_max": -0.12,
        "ret12_max": -0.25,
        "ret24_max": -0.35,
        "bad_slope_pct": -0.25,
        "bad_slope_closepos_min": 0.15,
        "description_ru": "Более узкий кластер поверх DQ01 для проверки сохранения соседних сигналов.",
    },
    {
        "variant_id": "CP03_DQ01_CLUSTER10_SCORE11_RECALL",
        "source_family_ids": ("DQ01_EQ01_PLUS_DEEP_RECLAIM",),
        "cluster_gap_bars": 10,
        "min_priority_score": 11,
        "low_zone_max": 0.42,
        "osc_max": 60.0,
        "mfi_max": 70.0,
        "wick_min": 0.12,
        "closepos_min": 0.12,
        "volz_min": 0.8,
        "support_touches_min": 2,
        "max_lower_low_streak": 4,
        "max_new_low_count_20": 12,
        "ret6_max": -0.12,
        "ret12_max": -0.25,
        "ret24_max": -0.35,
        "bad_slope_pct": -0.25,
        "bad_slope_closepos_min": 0.15,
        "description_ru": "Recall-вариант DQ01: мягче score, больше входов, нужен для сравнения.",
    },
    {
        "variant_id": "CP04_DQ03_CLUSTER10_SCORE12_HIGH_RECALL_SOURCE",
        "source_family_ids": ("DQ03_EQ03_HIGH_RECALL_PLUS_DEEP",),
        "cluster_gap_bars": 10,
        "min_priority_score": 12,
        "low_zone_max": 0.35,
        "osc_max": 60.0,
        "mfi_max": 70.0,
        "wick_min": 0.12,
        "closepos_min": 0.12,
        "volz_min": 0.8,
        "support_touches_min": 2,
        "max_lower_low_streak": 4,
        "max_new_low_count_20": 12,
        "ret6_max": -0.12,
        "ret12_max": -0.25,
        "ret24_max": -0.35,
        "bad_slope_pct": -0.25,
        "bad_slope_closepos_min": 0.15,
        "description_ru": "Проверка high-recall источника DQ03 после такого же suppression.",
    },
    {
        "variant_id": "CP05_DQ01_DQ03_CLUSTER10_SCORE12_UNION",
        "source_family_ids": ("DQ01_EQ01_PLUS_DEEP_RECLAIM", "DQ03_EQ03_HIGH_RECALL_PLUS_DEEP"),
        "cluster_gap_bars": 10,
        "min_priority_score": 12,
        "low_zone_max": 0.35,
        "osc_max": 60.0,
        "mfi_max": 70.0,
        "wick_min": 0.12,
        "closepos_min": 0.12,
        "volz_min": 0.8,
        "support_touches_min": 2,
        "max_lower_low_streak": 4,
        "max_new_low_count_20": 12,
        "ret6_max": -0.12,
        "ret12_max": -0.25,
        "ret24_max": -0.35,
        "bad_slope_pct": -0.25,
        "bad_slope_closepos_min": 0.15,
        "description_ru": "Union DQ01/DQ03: проверка, можно ли добрать пропуски без взрыва false.",
    },
]


RECOVERY_VARIANTS: list[dict[str, Any]] = [
    {
        "variant_id": "CP06_CP01_RECOVER_NOWICK_LATE_RETEST",
        "base_family_id": "CP01_DQ01_CLUSTER10_SCORE12",
        "recover_nowick_source_family_ids": ("DQ03_EQ03_HIGH_RECALL_PLUS_DEEP",),
        "recover_late_source_family_ids": ("DQ01_EQ01_PLUS_DEEP_RECLAIM", "DQ03_EQ03_HIGH_RECALL_PLUS_DEEP"),
        "nowick_low_zone_max": 0.35,
        "nowick_mfi_max": 35.0,
        "nowick_support_touches_min": 10,
        "nowick_closepos_max": 0.08,
        "nowick_wick_max": 0.08,
        "nowick_ret24_max": -0.25,
        "nowick_ret12_min": -0.10,
        "nowick_ret6_min": -0.05,
        "nowick_volz_min": -0.50,
        "nowick_rsi_min": 35.0,
        "nowick_rsi_max": 55.0,
        "nowick_stoch_min": 30.0,
        "nowick_stoch_max": 60.0,
        "nowick_lower_low_streak_max": 3,
        "nowick_new_low_count_20_max": 8,
        "nowick_ema_gap_max": 0.0,
        "late_low_zone_max": 0.35,
        "late_mfi_max": 40.0,
        "late_rsi_max": 50.0,
        "late_dist_from_low_60_max_pct": 0.30,
        "late_support_touches_min": 5,
        "late_closepos_max": 0.12,
        "late_wick_max": 0.10,
        "late_ret24_max": -0.15,
        "late_ret6_min": -0.05,
        "late_ema_gap_max": 0.0,
        "late_ema20_slope_max": 0.02,
        "description_ru": "CP01 плюс узкий recover: no-wick support-pullback для 08:26 и D03 late-retest для 17:00.",
    }
]


def _value(row: dict[str, Any], key: str, default: float) -> float:
    value = row.get(key)
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


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


def _low_zone(row: dict[str, Any]) -> float:
    return min(_value(row, "range_pos_60", 1.0), _value(row, "low_range_pos_60", 1.0))


def _priority_votes(row: dict[str, Any], params: dict[str, Any]) -> tuple[int, list[str], list[str], list[str], list[str]]:
    score = 0
    context_votes: list[str] = []
    trigger_votes: list[str] = []
    confirm_votes: list[str] = []
    suppress_votes: list[str] = []

    if _low_zone(row) <= float(params["low_zone_max"]):
        score += 3
        context_votes.append("CTX_LOW_ZONE")
    if bool(row.get("local_low_5")):
        score += 2
        context_votes.append("CTX_LOCAL_LOW_5")
    if bool(row.get("local_low_20")):
        score += 2
        context_votes.append("CTX_LOCAL_LOW_20")
    if _value(row, "support_touch_count_60", 0.0) >= float(params["support_touches_min"]):
        score += 1
        context_votes.append("CTX_SUPPORT_TOUCH_60")
    if _value(row, "ret_6_pct", 999.0) <= float(params["ret6_max"]):
        score += 1
        context_votes.append("CTX_RET6_DIP")
    if _value(row, "ret_12_pct", 999.0) <= float(params["ret12_max"]):
        score += 1
        context_votes.append("CTX_RET12_DIP")
    if _value(row, "ret_24_pct", 999.0) <= float(params["ret24_max"]):
        score += 1
        context_votes.append("CTX_RET24_DIP")
    if _value(row, "rsi14", 999.0) <= float(params["osc_max"]):
        score += 1
        confirm_votes.append("CONF_RSI_COLD")
    if _value(row, "stoch_k14", 999.0) <= float(params["osc_max"]):
        score += 1
        confirm_votes.append("CONF_STOCH_COLD")
    if _value(row, "mfi14", 999.0) <= float(params["mfi_max"]):
        score += 1
        confirm_votes.append("CONF_MFI_COLD")
    if _value(row, "lower_wick_share", 0.0) >= float(params["wick_min"]):
        score += 2
        trigger_votes.append("TRG_LOWER_WICK")
    if _value(row, "close_pos_candle", 0.0) >= float(params["closepos_min"]):
        score += 2
        trigger_votes.append("TRG_RECLAIM_CLOSE")
    if _value(row, "vol_z20", -999.0) >= float(params["volz_min"]):
        score += 1
        confirm_votes.append("CONF_VOLUME_Z20")

    if (
        _value(row, "lower_low_streak_5", 0.0) > float(params["max_lower_low_streak"])
        and _value(row, "lower_wick_share", 0.0) < 0.12
        and _value(row, "close_pos_candle", 0.0) < 0.12
    ):
        score -= 5
        suppress_votes.append("SUPPRESS_FALLING_KNIFE")
    if (
        _value(row, "new_low_count_20", 0.0) > float(params["max_new_low_count_20"])
        and _value(row, "vol_z20", -999.0) < 0.5
    ):
        score -= 2
        suppress_votes.append("SUPPRESS_LOW_CHAIN_NO_VOLUME")
    if (
        _value(row, "ema20_slope_5_pct", 0.0) <= float(params["bad_slope_pct"])
        and _value(row, "close_pos_candle", 0.0) < float(params["bad_slope_closepos_min"])
    ):
        score -= 2
        suppress_votes.append("SUPPRESS_BAD_SLOPE_NO_RECLAIM")

    return score, context_votes, trigger_votes, confirm_votes, suppress_votes


def _source_results_by_id(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["family_id"]): item for item in payload.get("best_overall", [])}


def _candidate_rows(
    *,
    rows: list[dict[str, Any]],
    source_results: dict[str, dict[str, Any]],
    params: dict[str, Any],
) -> list[dict[str, Any]]:
    by_entry_time: dict[str, dict[str, Any]] = {}
    for family_id in params["source_family_ids"]:
        result = source_results.get(str(family_id))
        if not result:
            continue
        for signal in result.get("signals", []):
            signal_idx = int(signal["signal_row_index"])
            entry_idx = int(signal["entry_row_index"])
            if signal_idx < 0 or entry_idx <= signal_idx or signal_idx >= len(rows) or entry_idx >= len(rows):
                continue
            score, context_votes, trigger_votes, confirm_votes, suppress_votes = _priority_votes(rows[signal_idx], params)
            if score < int(params["min_priority_score"]):
                continue
            entry_open = float(rows[entry_idx]["open"])
            enriched = dict(signal)
            enriched.update(
                {
                    "family_id": str(params["variant_id"]),
                    "source_family_id": str(family_id),
                    "priority_score": int(score),
                    "cluster_context_votes": context_votes,
                    "cluster_trigger_votes": trigger_votes,
                    "cluster_confirm_votes": confirm_votes,
                    "cluster_suppress_votes": suppress_votes,
                    "context_votes": list(signal.get("context_votes", [])) + context_votes,
                    "trigger_votes": list(signal.get("trigger_votes", [])) + trigger_votes + ["CLUSTER_PRIORITY"],
                    "confirm_votes": list(signal.get("confirm_votes", [])) + confirm_votes,
                    "suppress_votes": list(signal.get("suppress_votes", [])) + suppress_votes,
                    "entry_open_price": entry_open,
                    "entry_price_with_slippage": entry_open * 1.0005,
                    "slippage_bps": 5.0,
                    "lookahead": "NO",
                    "entry_rule": "next_bar_open_after_signal_close",
                    "debug_cluster": {
                        "low_zone": _low_zone(rows[signal_idx]),
                        "ret_6_pct": _value(rows[signal_idx], "ret_6_pct", 0.0),
                        "ret_12_pct": _value(rows[signal_idx], "ret_12_pct", 0.0),
                        "ret_24_pct": _value(rows[signal_idx], "ret_24_pct", 0.0),
                        "rsi14": _value(rows[signal_idx], "rsi14", 0.0),
                        "stoch_k14": _value(rows[signal_idx], "stoch_k14", 0.0),
                        "mfi14": _value(rows[signal_idx], "mfi14", 0.0),
                        "lower_wick_share": _value(rows[signal_idx], "lower_wick_share", 0.0),
                        "close_pos_candle": _value(rows[signal_idx], "close_pos_candle", 0.0),
                        "vol_z20": _value(rows[signal_idx], "vol_z20", 0.0),
                        "support_touch_count_60": _value(rows[signal_idx], "support_touch_count_60", 0.0),
                        "lower_low_streak_5": _value(rows[signal_idx], "lower_low_streak_5", 0.0),
                        "new_low_count_20": _value(rows[signal_idx], "new_low_count_20", 0.0),
                    },
                }
            )
            key = str(enriched["entry_time_utc"])
            current = by_entry_time.get(key)
            if current is None or int(enriched["priority_score"]) > int(current["priority_score"]):
                by_entry_time[key] = enriched
    return sorted(by_entry_time.values(), key=lambda item: int(item["entry_row_index"]))


def _cluster_candidates(candidates: list[dict[str, Any]], gap_bars: int) -> list[list[dict[str, Any]]]:
    clusters: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    for candidate in candidates:
        if not current:
            current = [candidate]
            continue
        if int(candidate["entry_row_index"]) - int(current[-1]["entry_row_index"]) <= gap_bars:
            current.append(candidate)
            continue
        clusters.append(current)
        current = [candidate]
    if current:
        clusters.append(current)
    return clusters


def _pick_cluster_winner(cluster: list[dict[str, Any]]) -> dict[str, Any]:
    return max(cluster, key=lambda item: (int(item["priority_score"]), int(item["entry_row_index"])))


def _trades_from_signals(signals: list[dict[str, Any]]) -> list[TradeEntry]:
    trades: list[TradeEntry] = []
    for signal in signals:
        entry_time = datetime.fromisoformat(str(signal["entry_time_utc"]).replace("Z", "+00:00"))
        trades.append(
            TradeEntry(
                row_index=int(signal["entry_row_index"]),
                side="long",
                entry_time=entry_time,
                exit_time_raw="",
                net_return=0.0,
                mae_pct=None,
                mfe_pct=None,
            )
        )
    return trades


def _run_cluster_variant(
    *,
    rows: list[dict[str, Any]],
    source_results: dict[str, dict[str, Any]],
    manual_entries: list[Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    candidates = _candidate_rows(rows=rows, source_results=source_results, params=params)
    clusters = _cluster_candidates(candidates, int(params["cluster_gap_bars"]))
    selected: list[dict[str, Any]] = []
    diagnostic_rows: list[dict[str, Any]] = []
    for cluster_id, cluster in enumerate(clusters, 1):
        winner = dict(_pick_cluster_winner(cluster))
        winner["cluster_id"] = cluster_id
        winner["cluster_size"] = len(cluster)
        selected.append(winner)
        for candidate in cluster:
            diagnostic_rows.append(
                {
                    "cluster_id": cluster_id,
                    "selected": candidate["entry_time_utc"] == winner["entry_time_utc"],
                    "entry_time_utc": candidate["entry_time_utc"],
                    "signal_time_utc": candidate["signal_time_utc"],
                    "source_family_id": candidate.get("source_family_id"),
                    "priority_score": candidate["priority_score"],
                    "cluster_context_votes": candidate.get("cluster_context_votes", []),
                    "cluster_trigger_votes": candidate.get("cluster_trigger_votes", []),
                    "cluster_confirm_votes": candidate.get("cluster_confirm_votes", []),
                    "cluster_suppress_votes": candidate.get("cluster_suppress_votes", []),
                }
            )
    score = score_entries(manual_entries, _trades_from_signals(selected))
    public_params = {
        key: value
        for key, value in params.items()
        if key not in {"description_ru"}
    }
    return {
        "family_id": str(params["variant_id"]),
        "description_ru": str(params["description_ru"]),
        "params": public_params,
        "score": _score_summary(score),
        "hit_details": score["hit_details"],
        "missed_target_details": score["missed_target_details"],
        "false_entry_details": score["false_entry_details"][:200],
        "signals": selected,
        "candidate_count_before_cluster": len(candidates),
        "clusters_total": len(clusters),
        "diagnostic_rows": diagnostic_rows[:500],
    }


def _has_vote(signal: dict[str, Any], needle: str) -> bool:
    return any(
        needle in str(vote)
        for key in ("context_votes", "trigger_votes", "confirm_votes")
        for vote in signal.get(key, [])
    )


def _is_nowick_recover(signal: dict[str, Any], row: dict[str, Any], params: dict[str, Any]) -> bool:
    if not (_has_vote(signal, "E05_NO_WICK") or _has_vote(signal, "NO_WICK")):
        return False
    return (
        _low_zone(row) <= float(params["nowick_low_zone_max"])
        and bool(row.get("local_low_5"))
        and _value(row, "mfi14", 999.0) <= float(params["nowick_mfi_max"])
        and float(params["nowick_rsi_min"]) <= _value(row, "rsi14", 999.0) <= float(params["nowick_rsi_max"])
        and float(params["nowick_stoch_min"])
        <= _value(row, "stoch_k14", 999.0)
        <= float(params["nowick_stoch_max"])
        and _value(row, "support_touch_count_60", 0.0) >= float(params["nowick_support_touches_min"])
        and _value(row, "close_pos_candle", 1.0) <= float(params["nowick_closepos_max"])
        and _value(row, "lower_wick_share", 1.0) <= float(params["nowick_wick_max"])
        and _value(row, "ret_24_pct", 999.0) <= float(params["nowick_ret24_max"])
        and _value(row, "ret_12_pct", -999.0) > float(params["nowick_ret12_min"])
        and _value(row, "ret_6_pct", -999.0) > float(params["nowick_ret6_min"])
        and _value(row, "vol_z20", -999.0) > float(params["nowick_volz_min"])
        and _value(row, "lower_low_streak_5", 999.0) <= float(params["nowick_lower_low_streak_max"])
        and _value(row, "new_low_count_20", 999.0) <= float(params["nowick_new_low_count_20_max"])
        and _value(row, "ema_gap_pct", 999.0) <= float(params["nowick_ema_gap_max"])
    )


def _is_late_retest_recover(signal: dict[str, Any], row: dict[str, Any], params: dict[str, Any]) -> bool:
    if not _has_vote(signal, "D03_LATE_RETEST"):
        return False
    return (
        _low_zone(row) <= float(params["late_low_zone_max"])
        and _value(row, "mfi14", 999.0) <= float(params["late_mfi_max"])
        and _value(row, "rsi14", 999.0) <= float(params["late_rsi_max"])
        and _value(row, "dist_from_low_60_pct", 999.0) <= float(params["late_dist_from_low_60_max_pct"])
        and _value(row, "support_touch_count_60", 0.0) >= float(params["late_support_touches_min"])
        and _value(row, "close_pos_candle", 1.0) <= float(params["late_closepos_max"])
        and _value(row, "lower_wick_share", 1.0) <= float(params["late_wick_max"])
        and _value(row, "ret_24_pct", 999.0) <= float(params["late_ret24_max"])
        and _value(row, "ret_6_pct", -999.0) >= float(params["late_ret6_min"])
        and _value(row, "ema_gap_pct", 999.0) <= float(params["late_ema_gap_max"])
        and _value(row, "ema20_slope_5_pct", 999.0) <= float(params["late_ema20_slope_max"])
    )


def _recover_source_signals(
    *,
    rows: list[dict[str, Any]],
    source_results: dict[str, dict[str, Any]],
    params: dict[str, Any],
) -> list[dict[str, Any]]:
    recovered: dict[str, dict[str, Any]] = {}
    nowick_sources = {str(item) for item in params["recover_nowick_source_family_ids"]}
    late_sources = {str(item) for item in params["recover_late_source_family_ids"]}
    for family_id, result in source_results.items():
        if family_id not in nowick_sources and family_id not in late_sources:
            continue
        for signal in result.get("signals", []):
            signal_idx = int(signal["signal_row_index"])
            entry_idx = int(signal["entry_row_index"])
            if signal_idx < 0 or entry_idx <= signal_idx or signal_idx >= len(rows) or entry_idx >= len(rows):
                continue
            row = rows[signal_idx]
            reasons: list[str] = []
            if family_id in nowick_sources and _is_nowick_recover(signal, row, params):
                reasons.append("RECOVER_NOWICK_SUPPORT_PULLBACK")
            if family_id in late_sources and _is_late_retest_recover(signal, row, params):
                reasons.append("RECOVER_D03_LATE_RETEST")
            if not reasons:
                continue
            entry_open = float(rows[entry_idx]["open"])
            enriched = dict(signal)
            enriched.update(
                {
                    "family_id": str(params["variant_id"]),
                    "source_family_id": family_id,
                    "recovery_reasons": reasons,
                    "trigger_votes": list(signal.get("trigger_votes", [])) + reasons,
                    "entry_open_price": entry_open,
                    "entry_price_with_slippage": entry_open * 1.0005,
                    "slippage_bps": 5.0,
                    "lookahead": "NO",
                    "entry_rule": "next_bar_open_after_signal_close",
                    "debug_recovery": {
                        "low_zone": _low_zone(row),
                        "ret_24_pct": _value(row, "ret_24_pct", 0.0),
                        "mfi14": _value(row, "mfi14", 0.0),
                        "rsi14": _value(row, "rsi14", 0.0),
                        "stoch_k14": _value(row, "stoch_k14", 0.0),
                        "close_pos_candle": _value(row, "close_pos_candle", 0.0),
                        "lower_wick_share": _value(row, "lower_wick_share", 0.0),
                        "vol_z20": _value(row, "vol_z20", 0.0),
                        "support_touch_count_60": _value(row, "support_touch_count_60", 0.0),
                        "dist_from_low_60_pct": _value(row, "dist_from_low_60_pct", 0.0),
                        "ema_gap_pct": _value(row, "ema_gap_pct", 0.0),
                    },
                }
            )
            recovered.setdefault(str(enriched["entry_time_utc"]), enriched)
    return sorted(recovered.values(), key=lambda item: int(item["entry_row_index"]))


def _run_recovery_variant(
    *,
    rows: list[dict[str, Any]],
    cluster_results: dict[str, dict[str, Any]],
    source_results: dict[str, dict[str, Any]],
    manual_entries: list[Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    base = cluster_results[str(params["base_family_id"])]
    selected: dict[str, dict[str, Any]] = {str(signal["entry_time_utc"]): dict(signal) for signal in base["signals"]}
    recovered_signals = _recover_source_signals(rows=rows, source_results=source_results, params=params)
    added: list[dict[str, Any]] = []
    for signal in recovered_signals:
        if str(signal["entry_time_utc"]) in selected:
            continue
        selected[str(signal["entry_time_utc"])] = signal
        added.append(signal)
    signals = sorted(selected.values(), key=lambda item: int(item["entry_row_index"]))
    score = score_entries(manual_entries, _trades_from_signals(signals))
    public_params = {key: value for key, value in params.items() if key not in {"description_ru"}}
    return {
        "family_id": str(params["variant_id"]),
        "description_ru": str(params["description_ru"]),
        "params": public_params,
        "score": _score_summary(score),
        "hit_details": score["hit_details"],
        "missed_target_details": score["missed_target_details"],
        "false_entry_details": score["false_entry_details"][:200],
        "signals": signals,
        "candidate_count_before_cluster": int(base.get("candidate_count_before_cluster", len(base["signals"]))),
        "clusters_total": int(base.get("clusters_total", len(base["signals"]))),
        "recovered_entries_total": len(added),
        "recovered_entries": [
            {
                "entry_time_utc": signal["entry_time_utc"],
                "signal_time_utc": signal["signal_time_utc"],
                "source_family_id": signal.get("source_family_id"),
                "recovery_reasons": signal.get("recovery_reasons", []),
            }
            for signal in added
        ],
    }


def _sort_key(item: dict[str, Any]) -> tuple[float, float, int, int, int]:
    score = item["score"]
    return (
        float(score["f1_visual"]),
        float(score["precision"]),
        int(score["target_hits"]),
        -int(score["false_entries"]),
        -int(score["entries_total"]),
    )


def _manual_slug(manual_payload: dict[str, Any]) -> str:
    source = (manual_payload.get("source_images") or [{}])[0]
    date_utc = str(source.get("date_utc") or "unknown").replace("-", "")
    role = str(manual_payload.get("dataset_role") or "DEV").upper()
    safe_role = "".join(ch if ch.isalnum() else "_" for ch in role).strip("_") or "DEV"
    return f"{date_utc}_{safe_role}"


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Visual Entry Noise Suppression Cluster Priority",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "Контракт: scoring использует закрытую signal-свечу и историю; вход LONG ставится на `open` следующей свечи; `lookahead=NO`; slippage `5 bps`.",
        "",
        "| rank | variant | hits | miss | false | entries | precision | recall | f1 | candidates | clusters |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, item in enumerate(payload["best_overall"], 1):
        score = item["score"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{:.4f}` | `{:.4f}` | `{:.4f}` | `{}` | `{}` |".format(
                rank,
                item["family_id"],
                score["target_hits"],
                score["missed_targets"],
                score["false_entries"],
                score["entries_total"],
                score["precision"],
                score["recall"],
                score["f1_visual"],
                item["candidate_count_before_cluster"],
                item["clusters_total"],
            )
        )
        if item.get("recovered_entries_total"):
            recovered = ", ".join(str(entry["entry_time_utc"])[11:16] for entry in item.get("recovered_entries", []))
            lines.append(f"|  | recover |  |  |  | `{item['recovered_entries_total']}` |  |  | `{recovered}` |  |  |")
    lines.extend(["", "## PNG", ""])
    for item in payload.get("rendered_overlays", []):
        lines.append(f"- `{item['family_id']}`: `{item['visual_png']}`")
    lines.extend(
        [
            "",
            "## Решение",
            "",
            "Это DEV diagnostic-only слой подавления шума. Результаты показывают, какие входы остаются после кластерного выбора, но в ML ничего не передавать без validation/holdout и отдельного ручного `APPROVED_FOR_ML`.",
            "",
            "Следующий шаг после этого отчета: визуально проверить PNG, затем без подкрутки повторить на `2026-05-13` и `2026-05-14`, если DEV-картинка устраивает.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_search(manual_entries_path: Path, out_dir: Path, *, render_top: int = 6) -> dict[str, Any]:
    manual_payload, manual_entries = load_manual_entries(manual_entries_path)
    _, rows = _prepare_rows(manual_entries_path)
    _enrich_quality_rows(rows)

    source_out_dir = out_dir / "_source_deep_capitulation_reclaim"
    source_payload = _run_deep_search(manual_entries_path, source_out_dir, render_top=0)
    source_results = _source_results_by_id(source_payload)

    cluster_results_list = [
        _run_cluster_variant(
            rows=rows,
            source_results=source_results,
            manual_entries=manual_entries,
            params=dict(params),
        )
        for params in CLUSTER_VARIANTS
    ]
    cluster_results_by_id = {item["family_id"]: item for item in cluster_results_list}
    recovery_results = [
        _run_recovery_variant(
            rows=rows,
            cluster_results=cluster_results_by_id,
            source_results=source_results,
            manual_entries=manual_entries,
            params=dict(params),
        )
        for params in RECOVERY_VARIANTS
        if str(params["base_family_id"]) in cluster_results_by_id
    ]
    results = cluster_results_list + recovery_results
    results = [item for item in results if int(item["score"]["entries_total"]) > 0]
    results.sort(key=_sort_key, reverse=True)

    out_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[dict[str, str]] = []
    for rank, result in enumerate(results[:render_top], 1):
        label = f"noise_cluster_{rank:02d}_{result['family_id'].lower()}"
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
        "status": STATUS,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "manual_entries": str(manual_entries_path),
        "source_status": source_payload.get("status"),
        "source_json_path": source_payload.get("json_path"),
        "variants_total": len(CLUSTER_VARIANTS),
        "recovery_variants_total": len(RECOVERY_VARIANTS),
        "results_total": len(results),
        "best_overall": results,
        "rendered_overlays": rendered,
        "ml_transfer_allowed": False,
    }
    slug = _manual_slug(manual_payload)
    json_path = out_dir / f"visual_entry_noise_suppression_cluster_priority_{slug}.json"
    md_path = out_dir / f"visual_entry_noise_suppression_cluster_priority_{slug}_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run visual-entry noise suppression cluster-priority diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/noise_suppression_cluster_priority")
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
                        "score": item["score"],
                        "candidate_count_before_cluster": item["candidate_count_before_cluster"],
                        "clusters_total": item["clusters_total"],
                    }
                    for item in payload["best_overall"][:3]
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
