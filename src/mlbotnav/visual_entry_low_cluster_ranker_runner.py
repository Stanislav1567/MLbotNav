from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.render_visual_entry_overlay import render_family_candidate_overlay
from mlbotnav.visual_entry_no_lookahead_candidates import _prepare_rows
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


STATUS = "DEV_LOW_CLUSTER_RANKER_V2_ENTRY_ONLY_NO_ML"


VARIANTS: list[dict[str, Any]] = [
    {
        "family_id": "LCR01_WIDE_SIGNIFICANT_LOW_CLUSTER",
        "bucket": "WIDE_CLUSTER",
        "candidate_min_score": 10,
        "cluster_gap_bars": 6,
        "rank_mode": "balanced",
        "description_ru": "Широкая карта significant-low, затем один лучший low внутри короткого кластера.",
    },
    {
        "family_id": "LCR02_BALANCED_FALSE_CONTROL_CLUSTER",
        "bucket": "BALANCED_CLUSTER",
        "candidate_min_score": 11,
        "cluster_gap_bars": 8,
        "rank_mode": "balanced",
        "description_ru": "Более строгий balanced-кластер: меньше recall, меньше ложных входов.",
    },
    {
        "family_id": "LCR03_STRICT_HOT_DEEP_CLUSTER",
        "bucket": "STRICT_HOT_DEEP",
        "candidate_min_score": 10,
        "cluster_gap_bars": 8,
        "rank_mode": "strict_hot_deep",
        "description_ru": "Только сильные hot-reclaim или deep-capitulation low, один вход на кластер.",
    },
    {
        "family_id": "LCR04_LATE_LOW_WITH_RECLAIM_CLUSTER",
        "bucket": "LATE_LOW_RECLAIM",
        "candidate_min_score": 9,
        "cluster_gap_bars": 10,
        "rank_mode": "late_low_reclaim",
        "description_ru": "Выбирает более поздний значимый low с reclaim внутри зоны, чтобы не брать первый микролой.",
    },
    {
        "family_id": "LCR05_CLEAN_FALSE_CONTROL_CLUSTER",
        "bucket": "CLEAN_FALSE_CONTROL",
        "candidate_min_score": 11,
        "cluster_gap_bars": 4,
        "rank_mode": "clean",
        "description_ru": "Самый чистый контроль false: короткие кластеры и жесткое ранжирование.",
    },
    {
        "family_id": "LCR06_STRICT_HOT_DEEP_RECALL_CLUSTER",
        "bucket": "STRICT_HOT_DEEP_RECALL",
        "candidate_min_score": 10,
        "cluster_gap_bars": 3,
        "rank_mode": "strict_hot_deep",
        "description_ru": "Recall-вариант strict hot/deep: меньше режет кластеры, чтобы сохранить больше пользовательских входов.",
    },
    {
        "family_id": "LCR07_ULTRA_CLEAN_CLUSTER",
        "bucket": "ULTRA_CLEAN",
        "candidate_min_score": 9,
        "cluster_gap_bars": 16,
        "rank_mode": "clean",
        "description_ru": "Ультра-чистый контроль: минимум ложных входов, используется как нижняя граница шума.",
    },
]


def _combined_score(row: dict[str, Any]) -> tuple[int, list[str], dict[str, int]]:
    deep_score, deep_votes = _score_deep(row)
    support_score, support_votes = _score_support(row)
    trend_score, trend_votes = _score_trend(row)
    hot_score, hot_votes = _score_hot(row)
    family_scores = {
        "deep": deep_score,
        "support": support_score,
        "trend": trend_score,
        "hot": hot_score,
    }
    combined = max(family_scores.values())
    votes: list[str] = []
    for prefix, score, source_votes in [
        ("DEEP", deep_score, deep_votes),
        ("SUPPORT", support_score, support_votes),
        ("TREND", trend_score, trend_votes),
        ("HOT", hot_score, hot_votes),
    ]:
        if score >= 7:
            votes.extend(f"{prefix}:{vote}" for vote in source_votes)
    if sum(score >= 7 for score in family_scores.values()) >= 2:
        combined += 1
        votes.append("MULTI_FAMILY_CONFIRM")
    return combined, votes, family_scores


def _rank_score(row: dict[str, Any], candidate_score: int, family_scores: dict[str, int], mode: str) -> float:
    low_zone = _low_zone(row)
    wick = _value(row, "lower_wick_share", 0.0)
    closepos = _value(row, "close_pos_candle", 0.0)
    volume = _value(row, "vol_z20", 0.0)
    support = _value(row, "support_touch_count_60", 0.0)
    ret12 = _value(row, "ret_12_pct", 0.0)
    ret24 = _value(row, "ret_24_pct", 0.0)
    new_lows = _value(row, "new_low_count_20", 0.0)
    slope = _value(row, "ema20_slope_5_pct", 0.0)
    base = float(candidate_score) * 10.0

    if mode == "strict_hot_deep":
        if family_scores["hot"] < 10 and family_scores["deep"] < 11:
            return -1_000_000.0
        return base + family_scores["hot"] * 4 + family_scores["deep"] * 4 + closepos * 6 + wick * 3 - low_zone * 4
    if mode == "late_low_reclaim":
        return base + closepos * 8 + wick * 3 + max(0.0, slope) * 20 + support * 0.05 - abs(ret12) * 0.2 - low_zone * 2
    if mode == "clean":
        if closepos < 0.45 and wick < 0.30 and family_scores["deep"] < 11:
            return -1_000_000.0
        return base + closepos * 5 + wick * 5 + volume * 0.5 - new_lows * 0.15 - low_zone * 5

    return (
        base
        + closepos * 4
        + wick * 3
        + volume * 0.4
        + support * 0.04
        - low_zone * 3
        - max(0.0, ret12) * 0.3
        - max(0.0, ret24) * 0.2
    )


def _raw_candidates(rows: list[dict[str, Any]], variant: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for signal_idx in range(60, len(rows) - 1):
        row = rows[signal_idx]
        candidate_score, context, family_scores = _combined_score(row)
        if candidate_score < int(variant["candidate_min_score"]):
            continue
        rank_score = _rank_score(row, candidate_score, family_scores, str(variant["rank_mode"]))
        if rank_score <= -999_999.0:
            continue
        signal = _signal_payload(
            rows,
            signal_idx,
            {
                "family_id": variant["family_id"],
                "bucket": variant["bucket"],
            },
            candidate_score,
            context,
            ["LOW_CLUSTER_RAW_CANDIDATE"],
        )
        signal["rank_score"] = rank_score
        signal["family_scores"] = family_scores
        signal["cluster_gap_bars"] = int(variant["cluster_gap_bars"])
        out.append(signal)
    return out


def _cluster_candidates(candidates: list[dict[str, Any]], *, cluster_gap_bars: int) -> list[list[dict[str, Any]]]:
    if not candidates:
        return []
    ordered = sorted(candidates, key=lambda item: int(item["signal_row_index"]))
    clusters: list[list[dict[str, Any]]] = [[ordered[0]]]
    for candidate in ordered[1:]:
        prev_idx = int(clusters[-1][-1]["signal_row_index"])
        cur_idx = int(candidate["signal_row_index"])
        if cur_idx - prev_idx <= cluster_gap_bars:
            clusters[-1].append(candidate)
        else:
            clusters.append([candidate])
    return clusters


def _select_cluster_winner(cluster: list[dict[str, Any]]) -> dict[str, Any]:
    winner = max(
        cluster,
        key=lambda item: (
            float(item["rank_score"]),
            int(item["priority_score"]),
            int(item["signal_row_index"]),
        ),
    )
    selected = dict(winner)
    selected["cluster_size"] = len(cluster)
    selected["cluster_start_signal_time_utc"] = cluster[0]["signal_time_utc"]
    selected["cluster_end_signal_time_utc"] = cluster[-1]["signal_time_utc"]
    selected["trigger_votes"] = list(selected.get("trigger_votes", [])) + ["LOW_CLUSTER_WINNER"]
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
    clusters = _cluster_candidates(raw, cluster_gap_bars=int(variant["cluster_gap_bars"]))
    signals = [_select_cluster_winner(cluster) for cluster in clusters]
    trades = [_to_trade(item) for item in signals]
    score = score_entries(manual_entries, trades)
    return {
        "family_id": str(variant["family_id"]),
        "bucket": str(variant["bucket"]),
        "description_ru": str(variant["description_ru"]),
        "params": {
            "candidate_min_score": int(variant["candidate_min_score"]),
            "cluster_gap_bars": int(variant["cluster_gap_bars"]),
            "rank_mode": str(variant["rank_mode"]),
            "cooldown_used": False,
        },
        "raw_candidates_total": len(raw),
        "clusters_total": len(clusters),
        "score": _score_summary(score),
        "hit_details": score["hit_details"],
        "missed_target_details": score["missed_target_details"],
        "false_entry_details": score["false_entry_details"][:250],
        "signals": signals,
    }


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Low Cluster Ranker V2",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "Контракт: signal-свеча закрыта, вход LONG на `open` следующей свечи, `lookahead=NO`, slippage `5 bps`.",
        "",
        "Граница: это не cooldown и не сделочный бэктест. TP/SL/MFE/MAE/future return не используются.",
        "",
        "| rank | family | hits | miss | false | entries | raw | clusters | precision | recall | f1 |",
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
                item["clusters_total"],
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
            "V2 диагностирует, насколько кластерный выбор снижает шум относительно V1. В ML ничего не передавать без отдельного подтверждения.",
            "",
        ]
    )
    return "\n".join(lines)


def run_search(manual_entries_path: Path, out_dir: Path, *, render_top: int = 5) -> dict[str, Any]:
    _, manual_entries = load_manual_entries(manual_entries_path)
    _, rows = _prepare_rows(manual_entries_path)
    _enrich_quality_rows(rows)
    results = [_run_variant(rows, manual_entries, variant) for variant in VARIANTS]
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
            label=f"lcr_v2_{rank:02d}_{result['family_id'].lower()}",
            slippage_bps=SLIPPAGE_BPS,
        )
        rendered.append({"rank": str(rank), "family_id": result["family_id"], "visual_png": str(png_path)})

    manual_payload, _ = load_manual_entries(manual_entries_path)
    day = str(manual_payload["source_images"][0].get("date_utc", "unknown")).replace("-", "")
    role = str(manual_payload.get("dataset_role", "DEV")).upper()
    safe_role = "".join(ch if ch.isalnum() else "_" for ch in role).strip("_")
    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "manual_entries": str(manual_entries_path),
        "strategy_scope": "entry_only_low_detection",
        "cluster_selection_used": True,
        "cooldown_used": False,
        "future_trade_outcome_used": False,
        "ml_transfer_allowed": False,
        "best_overall": results,
        "rendered_overlays": rendered,
    }
    json_path = out_dir / f"visual_entry_low_cluster_ranker_v2_{day}_{safe_role}.json"
    md_path = out_dir / f"visual_entry_low_cluster_ranker_v2_{day}_{safe_role}_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run low-cluster ranker V2 visual-entry diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/low_cluster_ranker")
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
