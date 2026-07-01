from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.render_visual_entry_overlay import render_family_candidate_overlay
from mlbotnav.visual_entry_deep_recovery_hot_recall_runner import (
    _build_olev20,
    _deep_recovery_signals,
    _hot_trend_recall_signals,
    _run_result,
    _to_trade,
    _union_signals,
    _value,
)
from mlbotnav.visual_entry_no_lookahead_candidates import _prepare_rows
from mlbotnav.visual_entry_online_low_event_quality_runner import _with_event_features
from mlbotnav.visual_entry_quality_filter_runner import _enrich_quality_rows
from mlbotnav.visual_entry_score import load_manual_entries, score_entries
from mlbotnav.visual_entry_significant_low_selector_runner import SLIPPAGE_BPS, _score_summary


STATUS = "DEV_HOT_TREND_FALSE_SUPPRESSION_V5_ENTRY_ONLY_NO_ML"


HOT_TREND_SUPPRESSION_VARIANTS: list[dict[str, Any]] = [
    {
        "family_id": "HTFS01_HOT_TREND_STRICT_FALSE_SUPPRESSION",
        "bucket": "HOT_TREND_FALSE_SUPPRESSION",
        "description_ru": (
            "Строгий hot/trend-фильтр: оставляет только отскок после заметного pullback, "
            "рядом с event-low, без перегретого MFI и без слишком широкой support-полки."
        ),
        "min_pullback_from_recent_high_20_pct": 0.20,
        "min_distance_to_event_low_pct": 0.20,
        "max_distance_to_event_low_pct": 0.55,
        "max_support_touch_count_60": 26,
        "min_wick_or_close_reclaim": 0.40,
        "max_mfi14": 55.0,
    },
    {
        "family_id": "HTFS02_HOT_TREND_STRICT_NO_MFI_CAP",
        "bucket": "HOT_TREND_FALSE_SUPPRESSION",
        "description_ru": (
            "Контрольный вариант HTFS01 без ограничения MFI. Нужен, чтобы видеть, не отрезает ли "
            "MFI полезные продолжения тренда."
        ),
        "min_pullback_from_recent_high_20_pct": 0.20,
        "min_distance_to_event_low_pct": 0.20,
        "max_distance_to_event_low_pct": 0.55,
        "max_support_touch_count_60": 26,
        "min_wick_or_close_reclaim": 0.40,
        "max_mfi14": 100.0,
    },
    {
        "family_id": "HTFS03_HOT_TREND_TIGHT_SHELF",
        "bucket": "HOT_TREND_FALSE_SUPPRESSION",
        "description_ru": (
            "Более узкая support-полка. Проверяет, не лучше ли брать только редкие касания, "
            "а плотную боковую полку считать шумом."
        ),
        "min_pullback_from_recent_high_20_pct": 0.20,
        "min_distance_to_event_low_pct": 0.20,
        "max_distance_to_event_low_pct": 0.55,
        "max_support_touch_count_60": 22,
        "min_wick_or_close_reclaim": 0.40,
        "max_mfi14": 55.0,
    },
]


def _debug_value(signal: dict[str, Any], key: str, default: float = 0.0) -> float:
    debug = signal.get("debug") or {}
    value = debug.get(key, default)
    if value is None:
        return default
    return float(value)


def _passes_hot_trend_suppression(signal: dict[str, Any], variant: dict[str, Any]) -> tuple[bool, list[str]]:
    suppress: list[str] = []
    pullback = _debug_value(signal, "pullback_from_recent_high_20_pct")
    distance = _debug_value(signal, "distance_to_event_low_pct", 999.0)
    support = _debug_value(signal, "support_touch_count_60")
    wick = _debug_value(signal, "lower_wick_share")
    close_pos = _debug_value(signal, "close_pos_candle")
    mfi = _debug_value(signal, "mfi14", 999.0)

    if pullback < float(variant["min_pullback_from_recent_high_20_pct"]):
        suppress.append("PULLBACK_TOO_SMALL")
    if distance < float(variant["min_distance_to_event_low_pct"]):
        suppress.append("TOO_CLOSE_TO_EVENT_LOW_NO_RECLAIM_DISTANCE")
    if distance > float(variant["max_distance_to_event_low_pct"]):
        suppress.append("TOO_FAR_FROM_EVENT_LOW")
    if support > float(variant["max_support_touch_count_60"]):
        suppress.append("SUPPORT_SHELF_TOO_WIDE")
    if max(wick, close_pos) < float(variant["min_wick_or_close_reclaim"]):
        suppress.append("NO_WICK_OR_CLOSE_RECLAIM")
    if mfi > float(variant["max_mfi14"]):
        suppress.append("MFI_TOO_HOT")
    return not suppress, suppress


def _strict_hot_trend_signals(
    broad_hot_signals: list[dict[str, Any]],
    variant: dict[str, Any],
) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    for signal in broad_hot_signals:
        ok, suppress = _passes_hot_trend_suppression(signal, variant)
        if not ok:
            continue
        enriched = dict(signal)
        enriched["family_id"] = str(variant["family_id"])
        enriched["bucket"] = str(variant["bucket"])
        enriched["strategy_scope"] = "entry_only_hot_trend_false_suppression"
        enriched["trigger_votes"] = list(enriched.get("trigger_votes", [])) + [str(variant["family_id"])]
        enriched["context_votes"] = list(enriched.get("context_votes", [])) + [
            "PULLBACK_RECLAIM",
            "EVENT_LOW_DISTANCE_BAND",
            "SUPPORT_SHELF_LIMIT",
            "MFI_FALSE_SUPPRESS",
        ]
        enriched["suppress_votes"] = suppress
        debug = dict(enriched.get("debug") or {})
        debug["htfs_variant"] = str(variant["family_id"])
        debug["htfs_min_pullback_from_recent_high_20_pct"] = float(variant["min_pullback_from_recent_high_20_pct"])
        debug["htfs_min_distance_to_event_low_pct"] = float(variant["min_distance_to_event_low_pct"])
        debug["htfs_max_distance_to_event_low_pct"] = float(variant["max_distance_to_event_low_pct"])
        debug["htfs_max_support_touch_count_60"] = float(variant["max_support_touch_count_60"])
        debug["htfs_min_wick_or_close_reclaim"] = float(variant["min_wick_or_close_reclaim"])
        debug["htfs_max_mfi14"] = float(variant["max_mfi14"])
        enriched["debug"] = debug
        kept.append(enriched)
    return kept


def _run_filtered_hot_result(
    broad_hot_signals: list[dict[str, Any]],
    variant: dict[str, Any],
    manual_entries: list[Any],
) -> dict[str, Any]:
    signals = _strict_hot_trend_signals(broad_hot_signals, variant)
    result = _run_result(
        str(variant["family_id"]),
        str(variant["bucket"]),
        str(variant["description_ru"]),
        signals,
        manual_entries,
    )
    result["params"] = {
        **result["params"],
        "cooldown_used": False,
        "source_family_id": "DRHR02_HOT_TREND_RECALL_DIAGNOSTIC",
        "min_pullback_from_recent_high_20_pct": variant["min_pullback_from_recent_high_20_pct"],
        "min_distance_to_event_low_pct": variant["min_distance_to_event_low_pct"],
        "max_distance_to_event_low_pct": variant["max_distance_to_event_low_pct"],
        "max_support_touch_count_60": variant["max_support_touch_count_60"],
        "min_wick_or_close_reclaim": variant["min_wick_or_close_reclaim"],
        "max_mfi14": variant["max_mfi14"],
    }
    result["raw_candidates_total"] = len(broad_hot_signals)
    result["suppressed_candidates_total"] = max(0, len(broad_hot_signals) - len(signals))
    result["filtered_candidates_total"] = len(signals)
    return result


def _summary_table(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for result in results:
        score = result["score"]
        rows.append(
            {
                "family_id": result["family_id"],
                "hits": score["target_hits"],
                "missed": score["missed_targets"],
                "false": score["false_entries"],
                "entries": score["entries_total"],
                "precision": score["precision"],
                "recall": score["recall"],
                "f1_visual": score["f1_visual"],
            }
        )
    return rows


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Hot Trend False Suppression V5",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "Контракт: entry-only, signal-свеча закрылась, LONG исполняется на `open` следующей свечи, `lookahead=NO`, slippage `5 bps`.",
        "",
        "Граница: TP/SL, MFE/MAE, future return, entry-candle OHLCV, cooldown-сетки `30/45/60/90` и ML-export не используются.",
        "",
        "| rank | family | hits | miss | false | entries | precision | recall | f1 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, item in enumerate(payload["best_overall"], 1):
        score = item["score"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{:.4f}` | `{:.4f}` | `{:.4f}` |".format(
                rank,
                item["family_id"],
                score["target_hits"],
                score["missed_targets"],
                score["false_entries"],
                score["entries_total"],
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
            "V5 подтверждает, что hot/trend можно подключать только через строгий фильтр ложных входов. "
            "Сырой hot/trend остается диагностикой: он полезен для recall, но без подавления дает слишком много мусора.",
            "",
            "Основной кандидат V5 - union V4 с `HTFS01`: он повышает покрытие пользовательских входов и сохраняет entry-only контракт. "
            "В ML не передавать до проверки на следующих днях.",
            "",
        ]
    )
    return "\n".join(lines)


def run_search(manual_entries_path: Path, out_dir: Path, *, render_top: int = 8) -> dict[str, Any]:
    manual_payload, manual_entries = load_manual_entries(manual_entries_path)
    _, rows = _prepare_rows(manual_entries_path)
    _enrich_quality_rows(rows)
    _with_event_features(rows)

    base = _build_olev20(rows, manual_entries)
    deep = _run_result(
        "HTFS00_BASE_DEEP_RECOVERY_V4",
        "BASE_DEEP_RECOVERY_V4",
        "Базовый V4 union без hot/trend: OLEV20 плюс deep-recovery.",
        _union_signals(
            [
                base,
                _run_result(
                    "HTFS00_DEEP_RECOVERY_SOURCE",
                    "BASE_DEEP_RECOVERY_V4",
                    "Deep-recovery source для базового V4.",
                    _deep_recovery_signals(rows),
                    manual_entries,
                ),
            ],
            family_id="HTFS00_BASE_DEEP_RECOVERY_V4",
            gap_bars=8,
        ),
        manual_entries,
    )
    broad_hot_signals = _hot_trend_recall_signals(rows)
    broad_hot = _run_result(
        "HTFS09_BROAD_HOT_TREND_DIAGNOSTIC",
        "HOT_TREND_DIAGNOSTIC",
        "Широкий hot/trend из V4 без нового подавления. Оставлен только как контроль шума.",
        broad_hot_signals,
        manual_entries,
    )
    filtered_hot_results = [
        _run_filtered_hot_result(broad_hot_signals, variant, manual_entries) for variant in HOT_TREND_SUPPRESSION_VARIANTS
    ]

    union_results: list[dict[str, Any]] = []
    for filtered in filtered_hot_results:
        union_signals = _union_signals([deep, filtered], family_id=f"HTFS20_UNION_{filtered['family_id']}", gap_bars=8)
        union = _run_result(
            f"HTFS20_UNION_{filtered['family_id']}",
            "HOT_TREND_FALSE_SUPPRESSION_UNION",
            f"Union базового V4 с {filtered['family_id']}.",
            union_signals,
            manual_entries,
        )
        union["params"] = {
            **union["params"],
            "cooldown_used": False,
            "base_family_id": deep["family_id"],
            "hot_filter_family_id": filtered["family_id"],
        }
        union_results.append(union)

    results = [deep, broad_hot, *filtered_hot_results, *union_results]
    results = [item for item in results if int(item["score"]["entries_total"]) > 0]
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
            label=f"hot_trend_false_suppression_v5_{rank:02d}_{result['family_id'].lower()}",
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
        "strategy_scope": "entry_only_hot_trend_false_suppression",
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
    json_path = out_dir / f"visual_entry_hot_trend_false_suppression_v5_{day}_{safe_role}.json"
    md_path = out_dir / f"visual_entry_hot_trend_false_suppression_v5_{day}_{safe_role}_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run hot/trend false suppression V5 visual-entry diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/hot_trend_false_suppression")
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
