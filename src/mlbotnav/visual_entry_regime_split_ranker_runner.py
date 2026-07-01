from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.render_visual_entry_overlay import render_family_candidate_overlay
from mlbotnav.visual_entry_low_cluster_ranker_runner import _rank_score
from mlbotnav.visual_entry_no_lookahead_candidates import _prepare_rows
from mlbotnav.visual_entry_quality_filter_runner import _enrich_quality_rows
from mlbotnav.visual_entry_reversal_bottom_knife_drop_runner import _low_zone, _value
from mlbotnav.visual_entry_score import TradeEntry, load_manual_entries, score_entries
from mlbotnav.visual_entry_significant_low_selector_runner import (
    SLIPPAGE_BPS,
    _score_deep,
    _score_hot,
    _score_summary,
    _score_support,
    _score_trend,
    _signal_payload,
)


STATUS = "DEV_REGIME_SPLIT_RANKER_V1_ENTRY_ONLY_NO_ML"


REGIME_VARIANTS: list[dict[str, Any]] = [
    {
        "family_id": "RSR01_DEEP_CAPITULATION_CLUSTER",
        "regime": "DEEP_CAPITULATION",
        "min_score": 10,
        "cluster_gap_bars": 8,
        "rank_mode": "strict_hot_deep",
        "description_ru": "Глубокий пролив/капитуляция: холодные осцилляторы, нижняя зона диапазона, локальный low, падение и wick/reclaim.",
    },
    {
        "family_id": "RSR02_DEEP_CAPITULATION_RECLAIM_CLEAN",
        "regime": "DEEP_CAPITULATION",
        "min_score": 11,
        "cluster_gap_bars": 10,
        "rank_mode": "clean",
        "description_ru": "Более чистый deep-вариант: оставляет только сильные low с wick/reclaim и режет часть цепочек падающего ножа.",
    },
    {
        "family_id": "RSR03_HOT_RECLAIM_SUPPORT_CLUSTER",
        "regime": "HOT_RECLAIM_SUPPORT",
        "min_score": 9,
        "cluster_gap_bars": 8,
        "rank_mode": "late_low_reclaim",
        "description_ru": "Горячий reclaim/support: вход около поддержки, осцилляторы могут быть не холодными, важнее wick/close reclaim.",
    },
    {
        "family_id": "RSR04_HOT_RECLAIM_SUPPORT_CLEAN",
        "regime": "HOT_RECLAIM_SUPPORT",
        "min_score": 10,
        "cluster_gap_bars": 12,
        "rank_mode": "clean",
        "description_ru": "Чистый hot/support вариант: требует более явный возврат свечи и поддержку, чтобы не ловить каждый микролой.",
    },
    {
        "family_id": "RSR05_TREND_DIP_CONTINUATION_CLUSTER",
        "regime": "TREND_DIP_CONTINUATION",
        "min_score": 9,
        "cluster_gap_bars": 8,
        "rank_mode": "balanced",
        "description_ru": "Trend dip continuation: локальный откат в живом движении, EMA не мертвая, цена не слишком высоко в диапазоне.",
    },
    {
        "family_id": "RSR06_TREND_DIP_CONTINUATION_CLEAN",
        "regime": "TREND_DIP_CONTINUATION",
        "min_score": 10,
        "cluster_gap_bars": 10,
        "rank_mode": "late_low_reclaim",
        "description_ru": "Чистый trend-dip: предпочитает поздний значимый low после отката, а не первый слабый микролой.",
    },
    {
        "family_id": "RSR07_STRUCTURE_BOS_FIBO_VOLUME_CLUSTER",
        "regime": "STRUCTURE_BOS_FIBO_VOLUME",
        "min_score": 9,
        "cluster_gap_bars": 10,
        "rank_mode": "balanced",
        "description_ru": "Структурный режим: support-touch, нижняя зона, reclaim и объем как приближение к BOS/FIBO/volume без будущих данных.",
    },
    {
        "family_id": "RSR08_STRUCTURE_VOLUME_RECLAIM_CLEAN",
        "regime": "STRUCTURE_BOS_FIBO_VOLUME",
        "min_score": 10,
        "cluster_gap_bars": 14,
        "rank_mode": "clean",
        "description_ru": "Чистый структурный режим: жестче требует поддержку, reclaim и объем, чтобы отделить реальные зоны от шумных low.",
    },
]


def _family_scores(row: dict[str, Any]) -> dict[str, tuple[int, list[str]]]:
    return {
        "deep": _score_deep(row),
        "support": _score_support(row),
        "trend": _score_trend(row),
        "hot": _score_hot(row),
    }


def _score_regime(row: dict[str, Any], variant: dict[str, Any]) -> tuple[int, list[str], dict[str, int]]:
    scores = _family_scores(row)
    family_scores = {key: value[0] for key, value in scores.items()}
    regime = str(variant["regime"])
    votes: list[str] = []

    if regime == "DEEP_CAPITULATION":
        score = family_scores["deep"]
        votes.extend(f"DEEP:{vote}" for vote in scores["deep"][1])
        if family_scores["support"] >= 8:
            score += 1
            votes.append("SUPPORT_CONFLUENCE")
        if _value(row, "new_low_count_20", 0.0) > 14 and _value(row, "close_pos_candle", 0.0) < 0.35:
            score -= 2
            votes.append("SUPPRESS_DENSE_LOW_CHAIN_NO_RECLAIM")
        return score, votes, family_scores

    if regime == "HOT_RECLAIM_SUPPORT":
        score = max(family_scores["hot"], family_scores["support"])
        if family_scores["hot"] >= 7:
            votes.extend(f"HOT:{vote}" for vote in scores["hot"][1])
        if family_scores["support"] >= 7:
            votes.extend(f"SUPPORT:{vote}" for vote in scores["support"][1])
        if _value(row, "close_pos_candle", 0.0) >= 0.65:
            score += 1
            votes.append("RECLAIM_CLOSE_PRIORITY")
        if _value(row, "support_touch_count_60", 0.0) < 8:
            score -= 1
            votes.append("SUPPRESS_WEAK_SUPPORT_CONTEXT")
        return score, votes, family_scores

    if regime == "TREND_DIP_CONTINUATION":
        score = family_scores["trend"]
        votes.extend(f"TREND:{vote}" for vote in scores["trend"][1])
        if _value(row, "ema20_slope_5_pct", -999.0) >= -0.01:
            score += 1
            votes.append("EMA20_ALIVE_PRIORITY")
        if _value(row, "ret_24_pct", -999.0) >= -0.25:
            score += 1
            votes.append("CONTEXT_NOT_CAPITULATION")
        if _low_zone(row) > 0.82:
            score -= 2
            votes.append("SUPPRESS_HIGH_ZONE")
        return score, votes, family_scores

    support_score, support_votes = scores["support"]
    hot_score, hot_votes = scores["hot"]
    score = max(support_score, hot_score)
    votes.extend(f"STRUCT_SUPPORT:{vote}" for vote in support_votes)
    if hot_score >= 7:
        votes.extend(f"STRUCT_HOT:{vote}" for vote in hot_votes)
    if _value(row, "support_touch_count_60", 0.0) >= 16:
        score += 1
        votes.append("STRUCTURE_SUPPORT_TOUCH_CLUSTER")
    if _value(row, "vol_z20", -999.0) >= 0.25:
        score += 1
        votes.append("VOLUME_CONFIRM")
    if _value(row, "ema20_slope_5_pct", -999.0) >= -0.02:
        score += 1
        votes.append("BOS_PROXY_EMA_ALIVE")
    if _value(row, "close_pos_candle", 0.0) < 0.35 and _value(row, "lower_wick_share", 0.0) < 0.18:
        score -= 2
        votes.append("SUPPRESS_NO_RECLAIM_OR_WICK")
    return score, votes, family_scores


def _raw_candidates(rows: list[dict[str, Any]], variant: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for signal_idx in range(60, len(rows) - 1):
        row = rows[signal_idx]
        score, votes, family_scores = _score_regime(row, variant)
        if score < int(variant["min_score"]):
            continue
        rank_score = _rank_score(row, score, family_scores, str(variant["rank_mode"]))
        if rank_score <= -999_999.0:
            continue
        signal = _signal_payload(
            rows,
            signal_idx,
            {"family_id": variant["family_id"], "bucket": variant["regime"]},
            score,
            votes,
            [f"REGIME_{variant['regime']}"],
        )
        signal["regime"] = str(variant["regime"])
        signal["rank_score"] = rank_score
        signal["family_scores"] = family_scores
        signal["cluster_gap_bars"] = int(variant["cluster_gap_bars"])
        out.append(signal)
    return out


def _select_online_no_rewrite(candidates: list[dict[str, Any]], *, min_gap_bars: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    last_signal_idx = -10_000
    for candidate in sorted(candidates, key=lambda item: int(item["signal_row_index"])):
        signal_idx = int(candidate["signal_row_index"])
        if signal_idx - last_signal_idx <= min_gap_bars:
            continue
        enriched = dict(candidate)
        enriched["online_selection_rule"] = "first_qualified_no_future_rewrite"
        enriched["duplicate_suppression_gap_bars"] = min_gap_bars
        enriched["trigger_votes"] = list(enriched.get("trigger_votes", [])) + ["REGIME_ONLINE_SELECTED"]
        selected.append(enriched)
        last_signal_idx = signal_idx
    return selected


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
    raw = _raw_candidates(rows, variant)
    signals = _select_online_no_rewrite(raw, min_gap_bars=int(variant["cluster_gap_bars"]))
    score = score_entries(manual_entries, [_to_trade(item) for item in signals])
    return {
        "family_id": str(variant["family_id"]),
        "bucket": str(variant["regime"]),
        "regime": str(variant["regime"]),
        "description_ru": str(variant["description_ru"]),
        "params": {
            "min_score": int(variant["min_score"]),
            "cluster_gap_bars": int(variant["cluster_gap_bars"]),
            "rank_mode": str(variant["rank_mode"]),
            "cooldown_used": False,
        },
        "raw_candidates_total": len(raw),
        "clusters_total": len(signals),
        "score": _score_summary(score),
        "hit_details": score["hit_details"],
        "missed_target_details": score["missed_target_details"],
        "false_entry_details": score["false_entry_details"][:250],
        "signals": signals,
    }


def _regime_summary(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for regime in ["DEEP_CAPITULATION", "HOT_RECLAIM_SUPPORT", "TREND_DIP_CONTINUATION", "STRUCTURE_BOS_FIBO_VOLUME"]:
        items = [item for item in results if item.get("regime") == regime]
        if not items:
            continue
        best = max(
            items,
            key=lambda item: (
                item["score"]["f1_visual"],
                item["score"]["target_hits"],
                item["score"]["precision"],
                -item["score"]["false_entries"],
            ),
        )
        out.append(
            {
                "regime": regime,
                "best_family_id": best["family_id"],
                "score": best["score"],
                "raw_candidates_total": best["raw_candidates_total"],
                "clusters_total": best["clusters_total"],
            }
        )
    return out


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Regime Split Ranker V1",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "Контракт: signal-свеча уже закрыта, LONG-вход ставится на `open` следующей свечи, `lookahead=NO`, slippage `5 bps`.",
        "",
        "Граница: это entry-only диагностика. Сделки, TP/SL, MFE/MAE, future return, cooldown-сетки `30/45/60/90` и ML-export не используются.",
        "",
        "Важно: режим использует online-style выбор `first_qualified_no_future_rewrite`. Будущий более сильный low не переписывает уже выбранный вход.",
        "",
        "## Лучшие режимы",
        "",
        "| regime | best family | hits | miss | false | entries | precision | recall | f1 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in payload["regime_summary"]:
        score = item["score"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{:.4f}` | `{:.4f}` | `{:.4f}` |".format(
                item["regime"],
                item["best_family_id"],
                score["target_hits"],
                score["missed_targets"],
                score["false_entries"],
                score["entries_total"],
                score["precision"],
                score["recall"],
                score["f1_visual"],
            )
        )
    lines.extend(
        [
            "",
            "## Все варианты",
            "",
            "| rank | family | regime | hits | miss | false | entries | raw | clusters | f1 |",
            "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for rank, item in enumerate(payload["best_overall"], 1):
        score = item["score"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{:.4f}` |".format(
                rank,
                item["family_id"],
                item["regime"],
                score["target_hits"],
                score["missed_targets"],
                score["false_entries"],
                score["entries_total"],
                item["raw_candidates_total"],
                item["clusters_total"],
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
            "V1 нужен, чтобы не смешивать разные типы дна в один ранкер. Если режим ловит мало, но чисто, его оставляем как кирпич. Если режим ловит много, но шумно, его не продвигаем, а используем как карту признаков для следующего фильтра. В ML ничего не передавать.",
            "",
        ]
    )
    return "\n".join(lines)


def run_search(manual_entries_path: Path, out_dir: Path, *, render_top: int = 8) -> dict[str, Any]:
    manual_payload, manual_entries = load_manual_entries(manual_entries_path)
    _, rows = _prepare_rows(manual_entries_path)
    _enrich_quality_rows(rows)
    results = [_run_variant(rows, manual_entries, variant) for variant in REGIME_VARIANTS]
    results.sort(
        key=lambda item: (
            item["score"]["f1_visual"],
            item["score"]["recall"],
            item["score"]["precision"],
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
            label=f"regime_split_v1_{rank:02d}_{result['family_id'].lower()}",
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
        "strategy_scope": "entry_only_low_detection_regime_split",
        "cluster_selection_used": False,
        "online_duplicate_suppression_used": True,
        "cooldown_used": False,
        "future_trade_outcome_used": False,
        "ml_transfer_allowed": False,
        "regime_summary": _regime_summary(results),
        "best_overall": results,
        "rendered_overlays": rendered,
    }
    json_path = out_dir / f"visual_entry_regime_split_ranker_v1_{day}_{safe_role}.json"
    md_path = out_dir / f"visual_entry_regime_split_ranker_v1_{day}_{safe_role}_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run regime-split ranker V1 visual-entry diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/regime_split_ranker")
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
                "regime_summary": payload["regime_summary"],
                "best": [
                    {
                        "family_id": item["family_id"],
                        "regime": item["regime"],
                        "raw_candidates_total": item["raw_candidates_total"],
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
