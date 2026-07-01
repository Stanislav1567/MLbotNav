from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.render_visual_entry_overlay import render_family_candidate_overlay
from mlbotnav.visual_entry_no_lookahead_candidates import _prepare_rows
from mlbotnav.visual_entry_quality_filter_runner import _enrich_quality_rows
from mlbotnav.visual_entry_score import TradeEntry, load_manual_entries, score_entries


STATUS = "DEV_REVERSAL_BOTTOM_KNIFE_DROP_V0_DIAGNOSTIC_NO_ML"
SLIPPAGE_BPS = 5.0


FAMILY_VARIANTS: list[dict[str, Any]] = [
    {
        "family_id": "RBKD01_DEEP_KNIFE_RECLAIM_STRICT",
        "bucket": "DEEP_KNIFE_REVERSAL",
        "cluster_gap_bars": 12,
        "cooldown_bars": 0,
        "min_score": 13,
        "local_low_bars": 20,
        "low_zone_max": 0.18,
        "ret12_max": -0.35,
        "ret24_max": -0.55,
        "rsi_max": 42.0,
        "stoch_max": 42.0,
        "mfi_max": 45.0,
        "wick_min": 0.14,
        "closepos_min": 0.14,
        "volz_min": 0.25,
        "support_touches_min": 1,
        "max_lower_low_streak": 4,
        "max_new_low_count_20": 12,
        "description_ru": "Глубокий нож/капитуляция: локальное дно, сильное падение, холодные осцилляторы и хотя бы слабый reclaim/фитиль.",
    },
    {
        "family_id": "RBKD02_DEEP_KNIFE_RECLAIM_SOFT",
        "bucket": "DEEP_KNIFE_REVERSAL",
        "cluster_gap_bars": 12,
        "cooldown_bars": 0,
        "min_score": 12,
        "local_low_bars": 10,
        "low_zone_max": 0.26,
        "ret12_max": -0.22,
        "ret24_max": -0.35,
        "rsi_max": 52.0,
        "stoch_max": 55.0,
        "mfi_max": 58.0,
        "wick_min": 0.08,
        "closepos_min": 0.08,
        "volz_min": -0.25,
        "support_touches_min": 1,
        "max_lower_low_streak": 5,
        "max_new_low_count_20": 15,
        "description_ru": "Мягкий нож: допускает ранний вход у дна без сильного фитиля, если контекст падения и низкая зона подтверждены.",
    },
    {
        "family_id": "RBKD03_PULLBACK_AFTER_RECLAIM",
        "bucket": "PULLBACK_AFTER_RECLAIM",
        "cluster_gap_bars": 15,
        "cooldown_bars": 0,
        "min_score": 12,
        "local_low_bars": 5,
        "low_zone_max": 0.42,
        "recent_deep_lookback": 180,
        "recent_deep_min_gap": 6,
        "recent_deep_low_zone_max": 0.16,
        "recent_deep_ret12_max": -0.40,
        "ret6_min": -0.12,
        "ret24_max": 0.35,
        "rsi_max": 60.0,
        "stoch_max": 68.0,
        "mfi_max": 65.0,
        "wick_min": 0.06,
        "closepos_min": 0.06,
        "support_touches_min": 3,
        "max_lower_low_streak": 3,
        "max_new_low_count_20": 10,
        "description_ru": "Откат после глубокого сброса: сначала был сильный низ, потом цена повторно проверяет зону и дает следующий open.",
    },
    {
        "family_id": "RBKD04_TREND_DIP_CONTINUATION",
        "bucket": "TREND_DIP_CONTINUATION",
        "cluster_gap_bars": 12,
        "cooldown_bars": 0,
        "min_score": 12,
        "local_low_bars": 5,
        "low_zone_max": 0.50,
        "ema20_slope_min": -0.03,
        "ret24_min": -0.20,
        "rsi_max": 68.0,
        "stoch_max": 72.0,
        "mfi_max": 75.0,
        "wick_min": 0.04,
        "closepos_min": 0.05,
        "support_touches_min": 2,
        "max_lower_low_streak": 3,
        "max_new_low_count_20": 9,
        "description_ru": "Дип в живом движении: не ловим нож, а берем локальный провал в уже ожившем/растущем контексте.",
    },
    {
        "family_id": "RBKD05_SUPPORT_WICK_MICRO_BOTTOM",
        "bucket": "SUPPORT_WICK_MICRO_BOTTOM",
        "cluster_gap_bars": 10,
        "cooldown_bars": 0,
        "min_score": 11,
        "local_low_bars": 5,
        "low_zone_max": 0.34,
        "rsi_max": 62.0,
        "stoch_max": 68.0,
        "mfi_max": 70.0,
        "wick_min": 0.16,
        "closepos_min": 0.12,
        "support_touches_min": 4,
        "max_lower_low_streak": 4,
        "max_new_low_count_20": 12,
        "description_ru": "Микро-дно у поддержки: локальный low, касания уровня и небольшой фитиль/reclaim без требования сильного падения.",
    },
]


ENSEMBLE_VARIANTS: list[dict[str, Any]] = [
    {
        "family_id": "RBKD10_UNION_KNIFE_PULLBACK_TREND_CLUSTER",
        "source_family_ids": [
            "RBKD01_DEEP_KNIFE_RECLAIM_STRICT",
            "RBKD02_DEEP_KNIFE_RECLAIM_SOFT",
            "RBKD03_PULLBACK_AFTER_RECLAIM",
            "RBKD04_TREND_DIP_CONTINUATION",
            "RBKD05_SUPPORT_WICK_MICRO_BOTTOM",
        ],
        "cluster_gap_bars": 12,
        "min_priority_score": 11,
        "description_ru": "Сводный слой: объединяет нож, ретест после ножа, трендовый дип и микро-дно, затем оставляет один лучший вход в кластере.",
    },
    {
        "family_id": "RBKD11_UNION_NO_TREND_DIP_STRICTER",
        "source_family_ids": [
            "RBKD01_DEEP_KNIFE_RECLAIM_STRICT",
            "RBKD02_DEEP_KNIFE_RECLAIM_SOFT",
            "RBKD03_PULLBACK_AFTER_RECLAIM",
            "RBKD05_SUPPORT_WICK_MICRO_BOTTOM",
        ],
        "cluster_gap_bars": 12,
        "min_priority_score": 12,
        "description_ru": "Сводный слой без трендового dip: проверка, сколько шума дает именно continuation-подсемейство.",
    },
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


def _local_low(row: dict[str, Any], bars: int) -> bool:
    return bool(row.get(f"local_low_{bars}"))


def _recent_deep_index(rows: list[dict[str, Any]], signal_idx: int, params: dict[str, Any]) -> int | None:
    lookback = int(params.get("recent_deep_lookback", 0))
    if lookback <= 0:
        return None
    min_gap = int(params.get("recent_deep_min_gap", 1))
    start = max(60, signal_idx - lookback)
    last: int | None = None
    for probe_idx in range(start, max(start, signal_idx - min_gap + 1)):
        probe = rows[probe_idx]
        if not (bool(probe.get("local_low_20")) or bool(probe.get("local_low_60"))):
            continue
        if _low_zone(probe) <= float(params["recent_deep_low_zone_max"]) or _value(
            probe, "ret_12_pct", 999.0
        ) <= float(params["recent_deep_ret12_max"]):
            last = probe_idx
    return last


def _candidate_score(rows: list[dict[str, Any]], signal_idx: int, params: dict[str, Any]) -> tuple[int, list[str], list[str], list[str], list[str]]:
    row = rows[signal_idx]
    score = 0
    context: list[str] = []
    trigger: list[str] = []
    confirm: list[str] = []
    suppress: list[str] = []
    bucket = str(params["bucket"])

    local_low_bars = int(params["local_low_bars"])
    if _local_low(row, local_low_bars):
        score += 3
        context.append(f"CTX_LOCAL_LOW_{local_low_bars}")
    if _local_low(row, 20):
        score += 1
        context.append("CTX_LOCAL_LOW_20")
    if _low_zone(row) <= float(params["low_zone_max"]):
        score += 3
        context.append("CTX_LOW_ZONE")
    if _value(row, "support_touch_count_60", 0.0) >= float(params["support_touches_min"]):
        score += 2
        context.append("CTX_SUPPORT_TOUCH_60")

    if bucket == "DEEP_KNIFE_REVERSAL":
        if _value(row, "ret_12_pct", 999.0) <= float(params["ret12_max"]):
            score += 2
            context.append("CTX_RET12_KNIFE")
        if _value(row, "ret_24_pct", 999.0) <= float(params["ret24_max"]):
            score += 2
            context.append("CTX_RET24_KNIFE")
    elif bucket == "PULLBACK_AFTER_RECLAIM":
        recent_idx = _recent_deep_index(rows, signal_idx, params)
        if recent_idx is not None:
            score += 4
            context.append(f"CTX_RECENT_DEEP_{signal_idx - recent_idx}B")
        if _value(row, "ret_6_pct", -999.0) >= float(params["ret6_min"]):
            score += 1
            context.append("CTX_SELLING_SLOWED_RET6")
        if _value(row, "ret_24_pct", 999.0) <= float(params["ret24_max"]):
            score += 1
            context.append("CTX_NOT_EXTENDED_UP_RET24")
    elif bucket == "TREND_DIP_CONTINUATION":
        if _value(row, "ema20_slope_5_pct", -999.0) >= float(params["ema20_slope_min"]):
            score += 2
            context.append("CTX_EMA20_FLAT_OR_UP")
        if _value(row, "ret_24_pct", -999.0) >= float(params["ret24_min"]):
            score += 2
            context.append("CTX_RECENT_CONTEXT_ALIVE")

    if _value(row, "lower_wick_share", 0.0) >= float(params["wick_min"]):
        score += 2
        trigger.append("TRG_LOWER_WICK")
    if _value(row, "close_pos_candle", 0.0) >= float(params["closepos_min"]):
        score += 2
        trigger.append("TRG_RECLAIM_CLOSE")
    if _value(row, "rsi14", 999.0) <= float(params["rsi_max"]):
        score += 1
        confirm.append("CONF_RSI_OK")
    if _value(row, "stoch_k14", 999.0) <= float(params["stoch_max"]):
        score += 1
        confirm.append("CONF_STOCH_OK")
    if _value(row, "mfi14", 999.0) <= float(params["mfi_max"]):
        score += 1
        confirm.append("CONF_MFI_OK")
    if "volz_min" in params and _value(row, "vol_z20", -999.0) >= float(params["volz_min"]):
        score += 1
        confirm.append("CONF_VOLUME_Z20")

    if _value(row, "lower_low_streak_5", 0.0) > float(params["max_lower_low_streak"]):
        if _value(row, "lower_wick_share", 0.0) < float(params["wick_min"]) and _value(
            row, "close_pos_candle", 0.0
        ) < float(params["closepos_min"]):
            score -= 5
            suppress.append("SUPPRESS_FALLING_KNIFE_NO_RECLAIM")
    if _value(row, "new_low_count_20", 0.0) > float(params["max_new_low_count_20"]):
        score -= 2
        suppress.append("SUPPRESS_LOW_CHAIN_TOO_DENSE")

    if not context:
        suppress.append("SUPPRESS_NO_CONTEXT")
    if not trigger:
        suppress.append("SUPPRESS_NO_TRIGGER")
    return score, context, trigger, confirm, suppress


def _to_trade(signal: dict[str, Any]) -> TradeEntry:
    entry_time = datetime.fromisoformat(str(signal["entry_time_utc"]).replace("Z", "+00:00"))
    return TradeEntry(
        row_index=int(signal["entry_row_index"]),
        side="long",
        entry_time=entry_time,
        exit_time_raw="",
        net_return=0.0,
        mae_pct=None,
        mfe_pct=None,
    )


def _build_signal(rows: list[dict[str, Any]], signal_idx: int, params: dict[str, Any], score: int, context: list[str], trigger: list[str], confirm: list[str], suppress: list[str]) -> dict[str, Any]:
    entry_idx = signal_idx + 1
    signal_row = rows[signal_idx]
    entry_row = rows[entry_idx]
    entry_open = float(entry_row["open"])
    return {
        "family_id": str(params["family_id"]),
        "bucket": str(params["bucket"]),
        "side": "long",
        "signal_row_index": signal_idx,
        "entry_row_index": entry_idx,
        "signal_time_utc": signal_row["open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_time_utc": entry_row["open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_open_price": entry_open,
        "entry_price_with_slippage": entry_open * (1.0 + SLIPPAGE_BPS / 10000.0),
        "slippage_bps": SLIPPAGE_BPS,
        "entry_rule": "next_bar_open_after_signal_close",
        "lookahead": "NO",
        "priority_score": int(score),
        "context_votes": context,
        "trigger_votes": trigger + [str(params["bucket"])],
        "confirm_votes": confirm,
        "suppress_votes": suppress,
        "debug": {
            "low_zone": _low_zone(signal_row),
            "ret_6_pct": _value(signal_row, "ret_6_pct", 0.0),
            "ret_12_pct": _value(signal_row, "ret_12_pct", 0.0),
            "ret_24_pct": _value(signal_row, "ret_24_pct", 0.0),
            "rsi14": _value(signal_row, "rsi14", 0.0),
            "stoch_k14": _value(signal_row, "stoch_k14", 0.0),
            "mfi14": _value(signal_row, "mfi14", 0.0),
            "lower_wick_share": _value(signal_row, "lower_wick_share", 0.0),
            "close_pos_candle": _value(signal_row, "close_pos_candle", 0.0),
            "vol_z20": _value(signal_row, "vol_z20", 0.0),
            "support_touch_count_60": _value(signal_row, "support_touch_count_60", 0.0),
            "lower_low_streak_5": _value(signal_row, "lower_low_streak_5", 0.0),
            "new_low_count_20": _value(signal_row, "new_low_count_20", 0.0),
            "ema20_slope_5_pct": _value(signal_row, "ema20_slope_5_pct", 0.0),
            "ema_gap_pct": _value(signal_row, "ema_gap_pct", 0.0),
        },
    }


def _select_online_first_qualified(candidates: list[dict[str, Any]], cooldown_bars: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    last_entry_idx = -10_000
    for candidate in sorted(candidates, key=lambda item: int(item["entry_row_index"])):
        entry_idx = int(candidate["entry_row_index"])
        if entry_idx - last_entry_idx <= cooldown_bars:
            continue
        enriched = dict(candidate)
        enriched["online_selection_rule"] = "first_qualified_after_cooldown"
        enriched["cooldown_bars"] = cooldown_bars
        selected.append(enriched)
        last_entry_idx = entry_idx
    return selected


def _run_variant(rows: list[dict[str, Any]], manual_entries: list[Any], params: dict[str, Any]) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    last_entry_idx = -10_000
    for signal_idx in range(60, len(rows) - 1):
        if signal_idx + 1 - last_entry_idx < int(params.get("cooldown_bars", 0)):
            continue
        score, context, trigger, confirm, suppress = _candidate_score(rows, signal_idx, params)
        if score < int(params["min_score"]) or not context or not trigger:
            continue
        signal = _build_signal(rows, signal_idx, params, score, context, trigger, confirm, suppress)
        candidates.append(signal)
        last_entry_idx = signal_idx + 1

    selected = _select_online_first_qualified(candidates, int(params["cluster_gap_bars"]))

    score = score_entries(manual_entries, [_to_trade(signal) for signal in selected])
    return {
        "family_id": str(params["family_id"]),
        "bucket": str(params["bucket"]),
        "description_ru": str(params["description_ru"]),
        "params": {key: value for key, value in params.items() if key != "description_ru"},
        "score": _score_summary(score),
        "hit_details": score["hit_details"],
        "missed_target_details": score["missed_target_details"],
        "false_entry_details": score["false_entry_details"][:200],
        "signals": selected,
        "candidate_count_before_cluster": len(candidates),
        "clusters_total": len(selected),
        "selection_rule": "online_first_qualified_after_cooldown",
    }


def _run_ensemble(results: list[dict[str, Any]], manual_entries: list[Any], params: dict[str, Any]) -> dict[str, Any]:
    by_time: dict[str, dict[str, Any]] = {}
    source_set = {str(item) for item in params["source_family_ids"]}
    raw_count = 0
    for result in results:
        if str(result["family_id"]) not in source_set:
            continue
        for signal in result.get("signals", []):
            if int(signal.get("priority_score", 0)) < int(params["min_priority_score"]):
                continue
            raw_count += 1
            key = str(signal["entry_time_utc"])
            current = by_time.get(key)
            if current is None or int(signal["priority_score"]) > int(current.get("priority_score", 0)):
                enriched = dict(signal)
                enriched["source_family_id"] = signal["family_id"]
                enriched["family_id"] = str(params["family_id"])
                enriched["trigger_votes"] = list(enriched.get("trigger_votes", [])) + ["ENSEMBLE_CLUSTER"]
                by_time[key] = enriched
    selected = _select_online_first_qualified(list(by_time.values()), int(params["cluster_gap_bars"]))
    score = score_entries(manual_entries, [_to_trade(signal) for signal in selected])
    return {
        "family_id": str(params["family_id"]),
        "bucket": "ENSEMBLE",
        "description_ru": str(params["description_ru"]),
        "params": dict(params),
        "score": _score_summary(score),
        "hit_details": score["hit_details"],
        "missed_target_details": score["missed_target_details"],
        "false_entry_details": score["false_entry_details"][:200],
        "signals": selected,
        "candidate_count_before_cluster": raw_count,
        "clusters_total": len(selected),
        "selection_rule": "online_first_qualified_after_cooldown",
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


def _manual_target_diagnostics(rows: list[dict[str, Any]], manual_payload: dict[str, Any]) -> list[dict[str, Any]]:
    row_by_time = {row["open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"): idx for idx, row in enumerate(rows)}
    out: list[dict[str, Any]] = []
    for raw in manual_payload.get("entries", []):
        signal_time = str(raw.get("signal_candle_time_utc"))
        signal_idx = row_by_time.get(signal_time)
        if signal_idx is None:
            continue
        family_scores: list[dict[str, Any]] = []
        for params in FAMILY_VARIANTS:
            score, context, trigger, confirm, suppress = _candidate_score(rows, signal_idx, params)
            family_scores.append(
                {
                    "family_id": params["family_id"],
                    "bucket": params["bucket"],
                    "score": score,
                    "pass": score >= int(params["min_score"]) and bool(context) and bool(trigger),
                    "context_votes": context,
                    "trigger_votes": trigger,
                    "confirm_votes": confirm,
                    "suppress_votes": suppress,
                }
            )
        family_scores.sort(key=lambda item: (int(item["score"]), bool(item["pass"])), reverse=True)
        row = rows[signal_idx]
        out.append(
            {
                "entry_id": raw.get("entry_id"),
                "entry_number": raw.get("entry_number"),
                "signal_time_utc": signal_time,
                "target_entry_time_utc": raw.get("target_entry_time_utc"),
                "best_family": family_scores[0] if family_scores else None,
                "all_family_scores": family_scores,
                "signal_features": {
                    "low_zone": _low_zone(row),
                    "ret_6_pct": _value(row, "ret_6_pct", 0.0),
                    "ret_12_pct": _value(row, "ret_12_pct", 0.0),
                    "ret_24_pct": _value(row, "ret_24_pct", 0.0),
                    "rsi14": _value(row, "rsi14", 0.0),
                    "stoch_k14": _value(row, "stoch_k14", 0.0),
                    "mfi14": _value(row, "mfi14", 0.0),
                    "lower_wick_share": _value(row, "lower_wick_share", 0.0),
                    "close_pos_candle": _value(row, "close_pos_candle", 0.0),
                    "support_touch_count_60": _value(row, "support_touch_count_60", 0.0),
                },
            }
        )
    return out


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Visual Entry REVERSAL_BOTTOM_KNIFE_DROP_V0",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "Контракт: сигнал считается только на закрытой свечке дна/провала; вход LONG ставится на `open` следующей свечи; `lookahead=NO`; slippage `5 bps`; отбор сигналов online `first_qualified_after_cooldown`; ML запрещен.",
        "",
        "| rank | family | bucket | hits | miss | false | entries | precision | recall | f1 | raw | clusters |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, item in enumerate(payload["best_overall"], 1):
        score = item["score"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{:.4f}` | `{:.4f}` | `{:.4f}` | `{}` | `{}` |".format(
                rank,
                item["family_id"],
                item.get("bucket", ""),
                score["target_hits"],
                score["missed_targets"],
                score["false_entries"],
                score["entries_total"],
                score["precision"],
                score["recall"],
                score["f1_visual"],
                item.get("candidate_count_before_cluster", 0),
                item.get("clusters_total", 0),
            )
        )
    lines.extend(["", "## PNG", ""])
    for item in payload.get("rendered_overlays", []):
        lines.append(f"- `{item['family_id']}`: `{item['visual_png']}`")
    lines.extend(["", "## Ручные точки: какой слой их видит", ""])
    lines.append("| entry | signal -> entry | best_family | score | pass | key_votes |")
    lines.append("|---:|---|---|---:|---:|---|")
    for item in payload.get("manual_target_diagnostics", []):
        best = item.get("best_family") or {}
        votes = ", ".join((best.get("context_votes") or [])[:3] + (best.get("trigger_votes") or [])[:3])
        lines.append(
            "| `{}` | `{}` -> `{}` | `{}` | `{}` | `{}` | {} |".format(
                item.get("entry_number"),
                str(item.get("signal_time_utc"))[11:16],
                str(item.get("target_entry_time_utc"))[11:16],
                best.get("family_id", ""),
                best.get("score", ""),
                "yes" if best.get("pass") else "no",
                votes or "-",
            )
        )
    lines.extend(
        [
            "",
            "## Решение",
            "",
            "Это diagnostic-only слой для разбора входов у дна. Он не является production/ML-кандидатом: сначала нужно визуально проверить PNG, затем без подкрутки повторить на соседних днях и только после отдельного ручного `APPROVED_FOR_ML` думать о передаче в ML.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_search(manual_entries_path: Path, out_dir: Path, *, render_top: int = 6) -> dict[str, Any]:
    manual_payload, manual_entries = load_manual_entries(manual_entries_path)
    _, rows = _prepare_rows(manual_entries_path)
    _enrich_quality_rows(rows)

    base_results = [_run_variant(rows, manual_entries, dict(params)) for params in FAMILY_VARIANTS]
    ensemble_results = [_run_ensemble(base_results, manual_entries, dict(params)) for params in ENSEMBLE_VARIANTS]
    results = [item for item in base_results + ensemble_results if int(item["score"]["entries_total"]) > 0]
    results.sort(key=_sort_key, reverse=True)

    out_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[dict[str, str]] = []
    for rank, result in enumerate(results[:render_top], 1):
        label = f"rbkd_{rank:02d}_{result['family_id'].lower()}"
        png_path = render_family_candidate_overlay(
            manual_entries_path=manual_entries_path,
            result=result,
            out_dir=out_dir,
            label=label,
            slippage_bps=SLIPPAGE_BPS,
        )
        rendered.append({"rank": str(rank), "family_id": result["family_id"], "visual_png": str(png_path)})

    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "manual_entries": str(manual_entries_path),
        "variants_total": len(FAMILY_VARIANTS),
        "ensemble_variants_total": len(ENSEMBLE_VARIANTS),
        "results_total": len(results),
        "best_overall": results,
        "manual_target_diagnostics": _manual_target_diagnostics(rows, manual_payload),
        "rendered_overlays": rendered,
        "ml_transfer_allowed": False,
    }
    slug = _manual_slug(manual_payload)
    json_path = out_dir / f"visual_entry_reversal_bottom_knife_drop_{slug}.json"
    md_path = out_dir / f"visual_entry_reversal_bottom_knife_drop_{slug}_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run visual-entry REVERSAL_BOTTOM_KNIFE_DROP_V0 diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/reversal_bottom_knife_drop")
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
                        "bucket": item.get("bucket"),
                        "score": item["score"],
                        "candidate_count_before_cluster": item.get("candidate_count_before_cluster", 0),
                        "clusters_total": item.get("clusters_total", 0),
                    }
                    for item in payload["best_overall"][:5]
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
