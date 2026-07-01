from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.render_visual_entry_overlay import render_family_candidate_overlay
from mlbotnav.visual_entry_brick_by_brick_selector_v9_runner import (
    VARIANTS as V9_VARIANTS,
    _brick_reject_reasons,
    _debug,
    _source_variant,
)
from mlbotnav.visual_entry_generalization_v7_runner import _online_duplicate_filter, _to_trade
from mlbotnav.visual_entry_negative_context_suppression_v8_runner import _filtered_source_signals
from mlbotnav.visual_entry_no_lookahead_candidates import _prepare_rows
from mlbotnav.visual_entry_online_low_event_quality_runner import _with_event_features
from mlbotnav.visual_entry_quality_filter_runner import _enrich_quality_rows
from mlbotnav.visual_entry_score import load_manual_entries, score_entries
from mlbotnav.visual_entry_significant_low_selector_runner import SLIPPAGE_BPS, _score_summary


STATUS = "DEV_EVENT_RANKED_BRICKS_V10_ENTRY_ONLY_NO_ML"


VARIANTS: list[dict[str, Any]] = [
    {
        "family_id": "V10_01_HOT_CHAIN_EVENT_LOW_RANKED",
        "source_family_id": "V9_01_HOT_CHAIN_EVENT_LOW_BRICK",
        "bucket": "HOT_CHAIN_EVENT_LOW_RANKED",
        "brick": "HOT_CHAIN_EVENT_LOW",
        "duplicate_gap_bars": 2,
        "description_ru": "Hot-chain event-low с выбором одного лучшего сигнала внутри event.",
    },
    {
        "family_id": "V10_02_HOT_FIRST_EVENT_RANKED",
        "source_family_id": "V9_02_HOT_FIRST_STRONG_RECLAIM_BRICK",
        "bucket": "HOT_FIRST_EVENT_RANKED",
        "brick": "HOT_FIRST_STRONG_RECLAIM",
        "duplicate_gap_bars": 4,
        "description_ru": "Hot-first reclaim: один лучший первый hot-сигнал внутри event, без серии дублей.",
    },
    {
        "family_id": "V10_03_WARM_EVENT_RANKED",
        "source_family_id": "V9_03_WARM_STRUCTURAL_RECLAIM_BRICK",
        "bucket": "WARM_EVENT_RANKED",
        "brick": "WARM_STRUCTURAL_RECLAIM",
        "duplicate_gap_bars": 5,
        "description_ru": "Warm/retest: один лучший структурный reclaim внутри support/event-зоны.",
    },
    {
        "family_id": "V10_04_DEEP_TERMINAL_EVENT_RANKED",
        "source_family_id": "V9_04_DEEP_TERMINAL_RECLAIM_BRICK",
        "bucket": "DEEP_TERMINAL_EVENT_RANKED",
        "brick": "DEEP_TERMINAL_RECLAIM",
        "duplicate_gap_bars": 6,
        "description_ru": "Deep-terminal: один лучший капитуляционный/terminal reclaim внутри falling-event.",
    },
    {
        "family_id": "V10_20_APPROVED_BRICKS_UNION_DIAG",
        "source_family_ids": [
            "V10_01_HOT_CHAIN_EVENT_LOW_RANKED",
            "V10_02_HOT_FIRST_EVENT_RANKED",
            "V10_03_WARM_EVENT_RANKED",
            "V10_04_DEEP_TERMINAL_EVENT_RANKED",
        ],
        "bucket": "APPROVED_BRICKS_UNION_DIAG",
        "duplicate_gap_bars": 3,
        "description_ru": "Диагностический union ranked-кирпичей; не ML-кандидат до стабильной multi-day проверки.",
    },
]


def _v9_variant(source_family_id: str) -> dict[str, Any]:
    for variant in V9_VARIANTS:
        if variant.get("family_id") == source_family_id:
            return variant
    raise KeyError(source_family_id)


def _event_key(signal: dict[str, Any]) -> str:
    debug = signal.get("debug") or {}
    event_start_idx = debug.get("low_event_start_idx")
    event_low_idx = debug.get("event_low_idx")
    bars_since_event_low = _debug(signal, "bars_since_event_low", 999.0)
    if event_start_idx is None:
        event_start_idx = event_low_idx
    if event_start_idx is None:
        event_start_idx = int(signal["signal_row_index"])
    if event_low_idx is None:
        event_low_idx = int(signal["signal_row_index"]) - int(max(0.0, min(bars_since_event_low, 999.0)))
    return f"{event_start_idx}:{event_low_idx}"


def _rank_score(signal: dict[str, Any], brick: str) -> float:
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
    bars_since_event_low = _debug(signal, "bars_since_event_low", 999.0)
    prior_event_candidates = _debug(signal, "v8_prior_event_candidates", 0.0)

    reclaim = max(closepos, min(1.0, wick * 1.6))
    near_event = max(0.0, 1.0 - min(distance, 1.0))
    fresh_event = max(0.0, 1.0 - min(bars_since_event_low, 20.0) / 20.0)
    support_mid = max(0.0, 1.0 - abs(support - 12.0) / 24.0)

    if brick == "HOT_CHAIN_EVENT_LOW":
        return (
            3.0 * near_event
            + 2.0 * fresh_event
            + 2.0 * min(1.0, lower_streak / 4.0)
            + 1.5 * min(1.0, slope / 0.18)
            + 1.0 * min(1.0, pullback20 / 0.35)
            - 0.4 * max(0.0, support - 8.0)
        )
    if brick == "HOT_FIRST_STRONG_RECLAIM":
        hot_first_bonus = 1.0 if hot_run == 1 else -2.0
        return (
            2.8 * reclaim
            + 1.4 * min(1.0, pullback20 / 0.35)
            + 1.2 * max(0.0, 1.0 - abs(low_zone - 0.72) / 0.22)
            + 1.0 * min(1.0, max(ret6, 0.0) / 0.32)
            + hot_first_bonus
            - 0.9 * max(0.0, mfi - 72.0) / 28.0
            - 0.9 * max(0.0, ret24 - 0.42) / 0.35
            - 0.04 * max(0.0, prior_event_candidates - 3.0)
        )
    if brick == "WARM_STRUCTURAL_RECLAIM":
        return (
            2.6 * reclaim
            + 1.9 * near_event
            + 1.2 * max(0.0, 1.0 - abs(low_zone - 0.42) / 0.24)
            + 1.1 * support_mid
            + 0.8 * min(1.0, pullback60 / 0.75)
            - 0.9 * max(0.0, ret24 - 0.18) / 0.32
            - 0.7 * max(0.0, mfi - 62.0) / 30.0
            - 0.06 * max(0.0, prior_event_candidates - 4.0)
        )
    if brick == "DEEP_TERMINAL_RECLAIM":
        deepness = max(0.0, 1.0 - min(low_zone, 0.45) / 0.45)
        capitulation = min(1.0, max(-ret24, pullback60) / 1.0)
        terminal = max(0.0, 1.0 - abs(lower_streak - 2.0) / 4.0)
        not_continuing = max(0.0, 1.0 - max(new_lows - 8.0, 0.0) / 6.0)
        return (
            2.4 * deepness
            + 1.8 * capitulation
            + 1.6 * reclaim
            + 1.2 * near_event
            + 0.9 * terminal
            + 0.8 * not_continuing
            - 0.8 * max(0.0, mfi - 45.0) / 35.0
            - 0.8 * max(0.0, ret6 - 0.22) / 0.35
        )
    return 0.0


def _rank_floor_reject_reasons(signal: dict[str, Any], brick: str, score: float) -> list[str]:
    mfi = _debug(signal, "mfi14")
    ret24 = _debug(signal, "ret_24_pct")
    support = _debug(signal, "support_touch_count_60")
    distance = _debug(signal, "distance_to_event_low_pct", 999.0)
    bars_since_event_low = _debug(signal, "bars_since_event_low", 999.0)
    prior_event_candidates = _debug(signal, "v8_prior_event_candidates", 0.0)
    low_zone = _debug(signal, "low_zone", 1.0)
    closepos = _debug(signal, "close_pos_candle")
    wick = _debug(signal, "lower_wick_share")
    new_lows = _debug(signal, "new_low_count_20")
    lower_streak = _debug(signal, "lower_low_streak_5")

    reasons: list[str] = []
    if brick == "HOT_CHAIN_EVENT_LOW":
        if score < 5.5:
            reasons.append("V10_HOT_CHAIN_RANK_TOO_WEAK")
    elif brick == "HOT_FIRST_STRONG_RECLAIM":
        if score < 3.7:
            reasons.append("V10_HOT_FIRST_RANK_TOO_WEAK")
        if bars_since_event_low > 60 and distance > 0.55:
            reasons.append("V10_HOT_FIRST_OLD_FAR_EVENT")
    elif brick == "WARM_STRUCTURAL_RECLAIM":
        if score < 4.2:
            reasons.append("V10_WARM_RANK_TOO_WEAK")
        if prior_event_candidates > 45 and bars_since_event_low > 20:
            reasons.append("V10_WARM_CROWDED_OLD_RETEST_SERIES")
        if mfi > 65.0 and ret24 > 0.15:
            reasons.append("V10_WARM_OVERHEATED_RETEST")
    elif brick == "DEEP_TERMINAL_RECLAIM":
        if score < 4.2:
            reasons.append("V10_DEEP_RANK_TOO_WEAK")
        if support > 20 and not (low_zone <= 0.05 and (closepos >= 0.35 or wick >= 0.30)):
            reasons.append("V10_DEEP_CROWDED_NOT_TERMINAL")
        if new_lows > 12 or lower_streak > 4:
            reasons.append("V10_DEEP_STILL_FALLING")
    return reasons


def _select_best_per_event(signals: list[dict[str, Any]], brick: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for signal in signals:
        groups.setdefault(_event_key(signal), []).append(signal)

    selected: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for event_key, items in groups.items():
        ranked = sorted(
            items,
            key=lambda item: (
                _rank_score(item, brick),
                -abs(_debug(item, "bars_since_event_low", 999.0)),
                -int(item["signal_row_index"]),
            ),
            reverse=True,
        )
        winner = dict(ranked[0])
        winner_debug = dict(winner.get("debug") or {})
        winner_rank_score = _rank_score(winner, brick)
        winner_debug["v10_event_key"] = event_key
        winner_debug["v10_rank_score"] = winner_rank_score
        winner_debug["v10_event_candidates_total"] = len(items)
        winner["debug"] = winner_debug
        floor_reasons = _rank_floor_reject_reasons(winner, brick, winner_rank_score)
        if floor_reasons:
            winner_debug["v10_rank_floor_reject_reasons"] = floor_reasons
            winner["debug"] = winner_debug
            winner["suppress_votes"] = list(winner.get("suppress_votes", [])) + floor_reasons
            rejected.append(winner)
        else:
            selected.append(winner)

        for loser in ranked[1:]:
            dropped = dict(loser)
            debug = dict(dropped.get("debug") or {})
            debug["v10_event_key"] = event_key
            debug["v10_rank_score"] = _rank_score(dropped, brick)
            debug["v10_event_candidates_total"] = len(items)
            debug["v10_rank_reject_reason"] = "V10_LOWER_RANK_IN_SAME_EVENT"
            dropped["debug"] = debug
            dropped["suppress_votes"] = list(dropped.get("suppress_votes", [])) + ["V10_LOWER_RANK_IN_SAME_EVENT"]
            rejected.append(dropped)
    return selected, rejected


def _run_variant(rows: list[dict[str, Any]], manual_entries: list[Any], variant: dict[str, Any]) -> dict[str, Any]:
    source_v9 = _v9_variant(str(variant["source_family_id"]))
    source_v8 = _source_variant(str(source_v9["source_family_id"]))
    source_signals, source_suppressed = _filtered_source_signals(rows, source_v8)

    brick_kept: list[dict[str, Any]] = []
    brick_rejected: list[dict[str, Any]] = []
    for signal in source_signals:
        enriched = dict(signal)
        debug = dict(enriched.get("debug") or {})
        reasons = _brick_reject_reasons(enriched, str(variant["brick"]))
        debug["v10_brick"] = str(variant["brick"])
        debug["v10_v9_reject_reasons"] = reasons
        enriched["debug"] = debug
        if reasons:
            enriched["suppress_votes"] = list(enriched.get("suppress_votes", [])) + reasons
            brick_rejected.append(enriched)
            continue
        brick_kept.append(enriched)

    ranked, event_rank_rejected = _select_best_per_event(brick_kept, str(variant["brick"]))
    signals: list[dict[str, Any]] = []
    for signal in _online_duplicate_filter(ranked, duplicate_gap_bars=int(variant["duplicate_gap_bars"])):
        enriched = dict(signal)
        enriched["family_id"] = str(variant["family_id"])
        enriched["bucket"] = str(variant["bucket"])
        enriched["strategy_scope"] = "entry_only_event_ranked_bricks_v10"
        enriched["trigger_votes"] = list(enriched.get("trigger_votes", [])) + ["V10_EVENT_RANK_WINNER"]
        enriched["suppress_votes"] = list(enriched.get("suppress_votes", []))
        signals.append(enriched)

    score = score_entries(manual_entries, [_to_trade(item) for item in signals])
    return {
        "family_id": str(variant["family_id"]),
        "bucket": str(variant["bucket"]),
        "description_ru": str(variant["description_ru"]),
        "params": {
            "source_family_id": str(variant["source_family_id"]),
            "brick": str(variant["brick"]),
            "duplicate_gap_bars": int(variant["duplicate_gap_bars"]),
            "event_ranked": True,
            "cooldown_used": False,
        },
        "raw_candidates_total": len(source_signals) + len(source_suppressed),
        "v8_suppressed_candidates_total": len(source_suppressed),
        "brick_rejected_candidates_total": len(brick_rejected),
        "event_rank_rejected_candidates_total": len(event_rank_rejected),
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
        enriched["strategy_scope"] = "entry_only_event_ranked_bricks_v10"
        enriched["trigger_votes"] = list(enriched.get("trigger_votes", [])) + ["V10_EVENT_RANKED_UNION"]
        signals.append(enriched)
    score = score_entries(manual_entries, [_to_trade(item) for item in signals])
    return {
        "family_id": str(variant["family_id"]),
        "bucket": str(variant["bucket"]),
        "description_ru": str(variant["description_ru"]),
        "params": {
            "source_family_ids": sorted(source_ids),
            "duplicate_gap_bars": int(variant["duplicate_gap_bars"]),
            "event_ranked": True,
            "cooldown_used": False,
        },
        "raw_candidates_total": len(raw),
        "v8_suppressed_candidates_total": 0,
        "brick_rejected_candidates_total": 0,
        "event_rank_rejected_candidates_total": 0,
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
        .replace("v10_01_hot_chain_event_low_ranked", "hot_chain_ranked")
        .replace("v10_02_hot_first_event_ranked", "hot_first_ranked")
        .replace("v10_03_warm_event_ranked", "warm_ranked")
        .replace("v10_04_deep_terminal_event_ranked", "deep_ranked")
        .replace("v10_20_approved_bricks_union_diag", "ranked_union")
    )
    return f"v10_{rank:02d}_{compact[:60]}"


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Event Ranked Bricks V10",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "Контракт: сигнал появляется только после закрытия сигнальной свечи лоя, LONG ставится на `open` следующей свечи, `lookahead=NO`, slippage `5 bps`.",
        "",
        "Граница: V10 ранжирует past-only сигналы внутри одного low-event. TP/SL, MFE/MAE, future return, entry-candle OHLCV, cooldown `30/45/60/90` и ML-export не используются.",
        "",
        "| rank | family | hits | miss | false | entries | raw | v8_supp | brick_rej | rank_rej | filtered | precision | recall | f1 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, item in enumerate(payload["best_overall"], 1):
        score = item["score"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{:.4f}` | `{:.4f}` | `{:.4f}` |".format(
                rank,
                item["family_id"],
                score["target_hits"],
                score["missed_targets"],
                score["false_entries"],
                score["entries_total"],
                item["raw_candidates_total"],
                item["v8_suppressed_candidates_total"],
                item["brick_rejected_candidates_total"],
                item["event_rank_rejected_candidates_total"],
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
            "V10 проверяет, помогает ли выбор одного лучшего сигнала внутри low-event убрать визуальную кашу. "
            "Если слой остается шумным на validation/holdout, его нельзя передавать в ML.",
            "",
        ]
    )
    return "\n".join(lines)


def run_search(manual_entries_path: Path, out_dir: Path, *, render_top: int = 5) -> dict[str, Any]:
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
        "strategy_scope": "entry_only_event_ranked_bricks_v10",
        "online_event_state_used": True,
        "online_duplicate_suppression_used": True,
        "event_ranked_bricks_used": True,
        "cooldown_used": False,
        "future_trade_outcome_used": False,
        "entry_candle_ohlcv_features_used": False,
        "ml_transfer_allowed": False,
        "slippage_bps": SLIPPAGE_BPS,
        "best_overall": results,
        "summary_table": _summary_table(results),
        "rendered_overlays": rendered,
    }
    json_path = out_dir / f"visual_entry_event_ranked_bricks_v10_{day}_{safe_role}.json"
    md_path = out_dir / f"visual_entry_event_ranked_bricks_v10_{day}_{safe_role}_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run EVENT_RANKED_BRICKS_V10 visual-entry diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/event_ranked_bricks_v10")
    parser.add_argument("--render-top", type=int, default=5)
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
                        "event_rank_rejected_candidates_total": item["event_rank_rejected_candidates_total"],
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
