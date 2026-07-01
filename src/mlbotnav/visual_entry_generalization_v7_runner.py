from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from mlbotnav.render_visual_entry_overlay import render_family_candidate_overlay
from mlbotnav.visual_entry_no_lookahead_candidates import _prepare_rows
from mlbotnav.visual_entry_online_low_event_quality_runner import _with_event_features
from mlbotnav.visual_entry_quality_filter_runner import _enrich_quality_rows
from mlbotnav.visual_entry_reversal_bottom_knife_drop_runner import _low_zone, _value
from mlbotnav.visual_entry_score import TradeEntry, load_manual_entries, score_entries
from mlbotnav.visual_entry_significant_low_selector_runner import (
    SLIPPAGE_BPS,
    _score_deep,
    _score_hot,
    _score_support,
    _score_summary,
    _score_trend,
    _signal_payload,
)


STATUS = "DEV_GENERALIZATION_V7_ENTRY_ONLY_NO_ML"


VARIANTS: list[dict[str, Any]] = [
    {
        "family_id": "G7_01_HOT_FIRST_RECLAIM_DIAG",
        "bucket": "HOT_FIRST_RECLAIM",
        "min_score": 8,
        "start_idx": 14,
        "duplicate_gap_bars": 4,
        "description_ru": "Ранний hot/reclaim: пробует поймать первые лои в живом импульсе 13-го дня, без ожидания 60 баров.",
    },
    {
        "family_id": "G7_02_HOT_CHAIN_DIP_DIAG",
        "bucket": "HOT_CHAIN_DIP",
        "min_score": 8,
        "start_idx": 14,
        "duplicate_gap_bars": 2,
        "description_ru": "Зрелый hot-chain dip: ищет повторный лой внутри уже идущего восходящего участка.",
    },
    {
        "family_id": "G7_03_WARM_RETEST_DIAG",
        "bucket": "WARM_RETEST",
        "min_score": 8,
        "start_idx": 14,
        "duplicate_gap_bars": 5,
        "description_ru": "Теплый retest: локальный лой рядом с поддержкой/событием, когда рынок уже не холодный deep.",
    },
    {
        "family_id": "G7_04_DEEP_EVENT_RECLAIM_DIAG",
        "bucket": "DEEP_EVENT",
        "min_score": 8,
        "start_idx": 30,
        "duplicate_gap_bars": 6,
        "description_ru": "Deep/event reclaim: поздние ножи, провалы и возвраты к event-low.",
    },
    {
        "family_id": "G7_20_UNION_HOT_WARM_DEEP_DIAG",
        "bucket": "UNION",
        "source_family_ids": [
            "G7_01_HOT_FIRST_RECLAIM_DIAG",
            "G7_02_HOT_CHAIN_DIP_DIAG",
            "G7_03_WARM_RETEST_DIAG",
            "G7_04_DEEP_EVENT_RECLAIM_DIAG",
        ],
        "duplicate_gap_bars": 3,
        "description_ru": "Сводный V7 diagnostic union: объединяет hot-first, hot-chain, warm retest и deep/event.",
    },
]


def _bool(row: dict[str, Any], key: str) -> bool:
    return bool(row.get(key))


def _local_low(row: dict[str, Any]) -> bool:
    return _bool(row, "local_low_5") or _bool(row, "local_low_10") or _bool(row, "local_low_20")


def _hot_pred(row: dict[str, Any]) -> bool:
    return (
        _low_zone(row) >= 0.55
        and _value(row, "ema20_slope_5_pct", -999.0) >= 0.012
        and _value(row, "rsi14", 0.0) >= 58.0
        and _value(row, "stoch_k14", 0.0) >= 65.0
        and _value(row, "ret_12_pct", -999.0) >= 0.06
        and _value(row, "new_low_count_20", 999.0) <= 9.0
        and _value(row, "pullback_from_recent_high_20_pct", 999.0) <= 0.32
    )


def _hot_run_len(rows: list[dict[str, Any]], idx: int) -> int:
    length = 0
    cur = idx
    while cur >= 0 and _hot_pred(rows[cur]):
        length += 1
        cur -= 1
    return length


def _family_scores(row: dict[str, Any]) -> dict[str, int]:
    return {
        "deep": _score_deep(row)[0],
        "support": _score_support(row)[0],
        "trend": _score_trend(row)[0],
        "hot": _score_hot(row)[0],
    }


def _base_debug(row: dict[str, Any], *, hot_run_len: int = 0, family_scores: dict[str, int] | None = None) -> dict[str, Any]:
    debug = {
        "low_zone": _low_zone(row),
        "support_touch_count_60": _value(row, "support_touch_count_60", 0.0),
        "distance_to_event_low_pct": _value(row, "distance_to_event_low_pct", 999.0),
        "pullback_from_recent_high_20_pct": _value(row, "pullback_from_recent_high_20_pct", 0.0),
        "ret_6_pct": _value(row, "ret_6_pct", 0.0),
        "ret_12_pct": _value(row, "ret_12_pct", 0.0),
        "ret_24_pct": _value(row, "ret_24_pct", 0.0),
        "rsi14": _value(row, "rsi14", 0.0),
        "stoch_k14": _value(row, "stoch_k14", 0.0),
        "mfi14": _value(row, "mfi14", 0.0),
        "lower_wick_share": _value(row, "lower_wick_share", 0.0),
        "close_pos_candle": _value(row, "close_pos_candle", 0.0),
        "vol_z20": _value(row, "vol_z20", 0.0),
        "ema20_slope_5_pct": _value(row, "ema20_slope_5_pct", 0.0),
        "new_low_count_20": _value(row, "new_low_count_20", 0.0),
        "lower_low_streak_5": _value(row, "lower_low_streak_5", 0.0),
        "local_low_5": bool(row.get("local_low_5")),
        "local_low_10": bool(row.get("local_low_10")),
        "local_low_20": bool(row.get("local_low_20")),
        "low_event_start_idx": row.get("low_event_start_idx"),
        "low_event_age_bars": _value(row, "low_event_age_bars", 999.0),
        "candidate_order_in_event": _value(row, "candidate_order_in_event", 0.0),
        "bars_since_event_low": _value(row, "bars_since_event_low", 999.0),
        "event_low_idx": row.get("event_low_idx"),
        "bars_since_recent_high_20": _value(row, "bars_since_recent_high_20", 999.0),
        "bars_since_recent_high_60": _value(row, "bars_since_recent_high_60", 999.0),
        "pullback_from_recent_high_60_pct": _value(row, "pullback_from_recent_high_60_pct", 0.0),
        "hot_run_len": hot_run_len,
    }
    if family_scores is not None:
        debug["family_scores"] = family_scores
    return debug


def _score_hot_first(rows: list[dict[str, Any]], idx: int) -> tuple[int, list[str], list[str], dict[str, Any]] | None:
    row = rows[idx]
    hot_run = _hot_run_len(rows, idx)
    if not _hot_pred(row) or hot_run > 3:
        return None
    score = 5
    votes = ["HOT_CONTEXT", "EARLY_HOT_CLUSTER"]
    if _local_low(row):
        score += 2
        votes.append("LOCAL_LOW")
    if _value(row, "close_pos_candle", 0.0) >= 0.45:
        score += 2
        votes.append("CLOSE_RECLAIM")
    if _value(row, "lower_wick_share", 0.0) >= 0.10:
        score += 1
        votes.append("LOWER_WICK")
    if _value(row, "support_touch_count_60", 0.0) >= 4:
        score += 1
        votes.append("SUPPORT_PRESENT")
    return score, votes, ["HOT_FIRST_RECLAIM_TRIGGER"], _base_debug(row, hot_run_len=hot_run)


def _score_hot_chain(rows: list[dict[str, Any]], idx: int) -> tuple[int, list[str], list[str], dict[str, Any]] | None:
    row = rows[idx]
    hot_run = _hot_run_len(rows, idx)
    if not _hot_pred(row) or hot_run < 4:
        return None
    if _value(row, "lower_low_streak_5", 0.0) < 1 and not _local_low(row):
        return None
    score = 5
    votes = ["HOT_CONTEXT", "MATURE_HOT_CHAIN"]
    if _value(row, "ema20_slope_5_pct", 0.0) >= 0.05:
        score += 2
        votes.append("EMA20_STRONG")
    if _value(row, "close_pos_candle", 0.0) >= 0.25 or _value(row, "lower_wick_share", 0.0) >= 0.10:
        score += 2
        votes.append("DIP_RECLAIM_OR_WICK")
    if _low_zone(row) <= 0.82:
        score += 1
        votes.append("NOT_TOP_ZONE")
    return score, votes, ["HOT_CHAIN_DIP_TRIGGER"], _base_debug(row, hot_run_len=hot_run)


def _score_warm_retest(rows: list[dict[str, Any]], idx: int) -> tuple[int, list[str], list[str], dict[str, Any]] | None:
    row = rows[idx]
    low_zone = _low_zone(row)
    if low_zone < 0.30 or low_zone > 0.78:
        return None
    if _value(row, "support_touch_count_60", 0.0) < 4 and _value(row, "distance_to_event_low_pct", 999.0) > 0.75:
        return None
    score = 4
    votes = ["WARM_RETEST_CONTEXT"]
    if _local_low(row):
        score += 2
        votes.append("LOCAL_LOW")
    if _value(row, "pullback_from_recent_high_20_pct", 0.0) >= 0.05:
        score += 1
        votes.append("HAS_PULLBACK")
    if _value(row, "ret_12_pct", 0.0) >= -0.45:
        score += 1
        votes.append("NOT_DEAD_RET12")
    if _value(row, "rsi14", 0.0) >= 42.0:
        score += 1
        votes.append("RSI_RECOVERED")
    if _value(row, "close_pos_candle", 0.0) >= 0.25 or _value(row, "lower_wick_share", 0.0) >= 0.10:
        score += 2
        votes.append("RECLAIM_OR_WICK")
    return score, votes, ["WARM_RETEST_TRIGGER"], _base_debug(row)


def _score_deep_event(rows: list[dict[str, Any]], idx: int) -> tuple[int, list[str], list[str], dict[str, Any]] | None:
    row = rows[idx]
    family_scores = _family_scores(row)
    deep_like = (
        _low_zone(row) <= 0.45
        or _value(row, "ret_24_pct", 0.0) <= -0.40
        or _value(row, "pullback_from_recent_high_20_pct", 0.0) >= 0.35
    )
    if not deep_like:
        return None
    score = max(family_scores["deep"], family_scores["support"], family_scores["trend"])
    votes = ["DEEP_EVENT_CONTEXT"]
    if _local_low(row):
        score += 2
        votes.append("LOCAL_LOW")
    if _value(row, "distance_to_event_low_pct", 999.0) <= 0.65:
        score += 1
        votes.append("NEAR_EVENT_LOW")
    if _value(row, "close_pos_candle", 0.0) >= 0.35 or _value(row, "lower_wick_share", 0.0) >= 0.20:
        score += 2
        votes.append("RECLAIM_OR_WICK")
    return score, votes, ["DEEP_EVENT_RECLAIM_TRIGGER"], _base_debug(row, family_scores=family_scores)


SCORERS: dict[str, Callable[[list[dict[str, Any]], int], tuple[int, list[str], list[str], dict[str, Any]] | None]] = {
    "G7_01_HOT_FIRST_RECLAIM_DIAG": _score_hot_first,
    "G7_02_HOT_CHAIN_DIP_DIAG": _score_hot_chain,
    "G7_03_WARM_RETEST_DIAG": _score_warm_retest,
    "G7_04_DEEP_EVENT_RECLAIM_DIAG": _score_deep_event,
}


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


def _online_duplicate_filter(signals: list[dict[str, Any]], *, duplicate_gap_bars: int) -> list[dict[str, Any]]:
    if duplicate_gap_bars <= 0:
        return sorted(signals, key=lambda item: int(item["signal_row_index"]))
    kept: list[dict[str, Any]] = []
    last_signal_idx: int | None = None
    for signal in sorted(signals, key=lambda item: int(item["signal_row_index"])):
        signal_idx = int(signal["signal_row_index"])
        if last_signal_idx is not None and signal_idx - last_signal_idx <= duplicate_gap_bars:
            continue
        kept.append(signal)
        last_signal_idx = signal_idx
    return kept


def _raw_variant_signals(rows: list[dict[str, Any]], variant: dict[str, Any]) -> list[dict[str, Any]]:
    scorer = SCORERS[str(variant["family_id"])]
    raw: list[dict[str, Any]] = []
    for signal_idx in range(int(variant["start_idx"]), len(rows) - 1):
        scored = scorer(rows, signal_idx)
        if scored is None:
            continue
        priority_score, context, trigger, debug = scored
        if priority_score < int(variant["min_score"]):
            continue
        signal = _signal_payload(rows, signal_idx, variant, priority_score, context, trigger)
        signal["debug"] = {**signal.get("debug", {}), **debug}
        signal["strategy_scope"] = "entry_only_generalization_v7"
        raw.append(signal)
    return raw


def _run_variant(rows: list[dict[str, Any]], manual_entries: list[Any], variant: dict[str, Any]) -> dict[str, Any]:
    raw = _raw_variant_signals(rows, variant)
    signals = _online_duplicate_filter(raw, duplicate_gap_bars=int(variant["duplicate_gap_bars"]))
    trades = [_to_trade(item) for item in signals]
    score = score_entries(manual_entries, trades)
    return {
        "family_id": str(variant["family_id"]),
        "bucket": str(variant["bucket"]),
        "description_ru": str(variant["description_ru"]),
        "params": {
            "min_score": int(variant["min_score"]),
            "start_idx": int(variant["start_idx"]),
            "duplicate_gap_bars": int(variant["duplicate_gap_bars"]),
            "cooldown_used": False,
        },
        "raw_candidates_total": len(raw),
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
        enriched["trigger_votes"] = list(enriched.get("trigger_votes", [])) + ["G7_UNION"]
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
        .replace("g7_20_union_hot_warm_deep_diag", "union_hot_warm_deep")
        .replace("g7_01_hot_first_reclaim_diag", "hot_first")
        .replace("g7_02_hot_chain_dip_diag", "hot_chain")
        .replace("g7_03_warm_retest_diag", "warm_retest")
        .replace("g7_04_deep_event_reclaim_diag", "deep_event")
    )
    return f"g7_{rank:02d}_{compact[:60]}"


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Generalization V7",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "Контракт: сигнальная свеча уже закрыта, LONG ставится на `open` следующей свечи, `lookahead=NO`, slippage `5 bps`.",
        "",
        "Граница: TP/SL, MFE/MAE, future return, entry-candle OHLCV, cooldown-сетки `30/45/60/90` и ML-export не используются.",
        "",
        "| rank | family | hits | miss | false | entries | raw | filtered | precision | recall | f1 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, item in enumerate(payload["best_overall"], 1):
        score = item["score"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{:.4f}` | `{:.4f}` | `{:.4f}` |".format(
                rank,
                item["family_id"],
                score["target_hits"],
                score["missed_targets"],
                score["false_entries"],
                score["entries_total"],
                item["raw_candidates_total"],
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
            "V7 является диагностикой обобщения по типам лоя: hot-first, hot-chain, warm retest и deep/event. "
            "Если слой дает много ложных входов или проваливает один из дней, его нельзя передавать в ML; он остается картой признаков для следующей итерации.",
            "",
        ]
    )
    return "\n".join(lines)


def run_search(manual_entries_path: Path, out_dir: Path, *, render_top: int = 6) -> dict[str, Any]:
    manual_payload, manual_entries = load_manual_entries(manual_entries_path)
    _, rows = _prepare_rows(manual_entries_path)
    _enrich_quality_rows(rows)
    _with_event_features(rows)

    atomic_results = [_run_variant(rows, manual_entries, variant) for variant in VARIANTS if "source_family_ids" not in variant]
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
        "strategy_scope": "entry_only_generalization_v7",
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
    json_path = out_dir / f"visual_entry_generalization_v7_{day}_{safe_role}.json"
    md_path = out_dir / f"visual_entry_generalization_v7_{day}_{safe_role}_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run GENERALIZATION_V7 visual-entry diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/generalization_v7")
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
