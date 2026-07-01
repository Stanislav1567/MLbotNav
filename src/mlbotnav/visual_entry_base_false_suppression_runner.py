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
    _union_signals,
)
from mlbotnav.visual_entry_hot_trend_false_suppression_runner import (
    HOT_TREND_SUPPRESSION_VARIANTS,
    _run_filtered_hot_result,
)
from mlbotnav.visual_entry_no_lookahead_candidates import _prepare_rows
from mlbotnav.visual_entry_online_low_event_quality_runner import _with_event_features
from mlbotnav.visual_entry_quality_filter_runner import _enrich_quality_rows
from mlbotnav.visual_entry_score import load_manual_entries
from mlbotnav.visual_entry_significant_low_selector_runner import SLIPPAGE_BPS


STATUS = "DEV_BASE_FALSE_SUPPRESSION_V6_ENTRY_ONLY_NO_ML"


BASE_SUPPRESSION_VARIANTS: list[dict[str, Any]] = [
    {
        "family_id": "BFS01_BASE_SOURCE_SPLIT_STRICT_FALSE_SUPPRESSION",
        "bucket": "BASE_FALSE_SUPPRESSION",
        "description_ru": (
            "Строгий source-split фильтр базовой V4-части: OLEV-support reclaim и deep-recovery "
            "режутся разными past-only правилами."
        ),
        "event_low_zone_min": 0.25,
        "event_low_zone_max": 0.55,
        "event_max_support_touch_count_60": 36,
        "event_max_mfi14": 55.0,
        "event_max_ret_24_pct": 0.15,
        "event_max_lower_low_streak_5": 0,
        "deep_early_min_rsi14": 40.0,
        "deep_early_max_ret_24_pct": -0.55,
        "deep_early_max_lower_low_streak_5": 1,
        "deep_early_max_new_low_count_20": 7,
        "deep_early_max_distance_to_event_low_pct": 0.10,
        "deep_late_min_distance_to_event_low_pct": 0.45,
        "deep_late_max_distance_to_event_low_pct": 0.60,
        "deep_late_max_lower_low_streak_5": 0,
        "deep_late_max_ret_24_pct": -0.80,
        "deep_late_max_new_low_count_20": 12,
    },
    {
        "family_id": "BFS02_BASE_SOURCE_SPLIT_RELAXED_DIAGNOSTIC",
        "bucket": "BASE_FALSE_SUPPRESSION",
        "description_ru": "Контрольный relaxed-вариант BFS01: показывает цену небольшого ослабления фильтров.",
        "event_low_zone_min": 0.20,
        "event_low_zone_max": 0.60,
        "event_max_support_touch_count_60": 38,
        "event_max_mfi14": 60.0,
        "event_max_ret_24_pct": 0.18,
        "event_max_lower_low_streak_5": 0,
        "deep_early_min_rsi14": 38.0,
        "deep_early_max_ret_24_pct": -0.52,
        "deep_early_max_lower_low_streak_5": 1,
        "deep_early_max_new_low_count_20": 8,
        "deep_early_max_distance_to_event_low_pct": 0.12,
        "deep_late_min_distance_to_event_low_pct": 0.44,
        "deep_late_max_distance_to_event_low_pct": 0.62,
        "deep_late_max_lower_low_streak_5": 0,
        "deep_late_max_ret_24_pct": -0.75,
        "deep_late_max_new_low_count_20": 12,
    },
    {
        "family_id": "BFS03_BASE_SOURCE_SPLIT_TIGHT_DEEP",
        "bucket": "BASE_FALSE_SUPPRESSION",
        "description_ru": "Более жесткий deep-фильтр для контроля переобучения на поздних ножах.",
        "event_low_zone_min": 0.25,
        "event_low_zone_max": 0.55,
        "event_max_support_touch_count_60": 36,
        "event_max_mfi14": 55.0,
        "event_max_ret_24_pct": 0.15,
        "event_max_lower_low_streak_5": 0,
        "deep_early_min_rsi14": 42.0,
        "deep_early_max_ret_24_pct": -0.55,
        "deep_early_max_lower_low_streak_5": 1,
        "deep_early_max_new_low_count_20": 7,
        "deep_early_max_distance_to_event_low_pct": 0.10,
        "deep_late_min_distance_to_event_low_pct": 0.48,
        "deep_late_max_distance_to_event_low_pct": 0.56,
        "deep_late_max_lower_low_streak_5": 0,
        "deep_late_max_ret_24_pct": -0.90,
        "deep_late_max_new_low_count_20": 12,
    },
]


def _debug_value(signal: dict[str, Any], key: str, default: float = 0.0) -> float:
    value = (signal.get("debug") or {}).get(key, default)
    if value is None:
        return default
    return float(value)


def _is_deep_source(signal: dict[str, Any]) -> bool:
    source = str(signal.get("source_family_id") or signal.get("family_id") or "")
    return "DEEP" in source or "RECOVERY_SOURCE" in source


def _passes_event_base(signal: dict[str, Any], variant: dict[str, Any]) -> tuple[bool, list[str]]:
    suppress: list[str] = []
    low_zone = _debug_value(signal, "low_zone", 999.0)
    if low_zone < float(variant["event_low_zone_min"]) or low_zone > float(variant["event_low_zone_max"]):
        suppress.append("EVENT_LOW_ZONE_OUT_OF_BAND")
    if _debug_value(signal, "support_touch_count_60") > float(variant["event_max_support_touch_count_60"]):
        suppress.append("EVENT_SUPPORT_SHELF_TOO_WIDE")
    if _debug_value(signal, "mfi14", 999.0) > float(variant["event_max_mfi14"]):
        suppress.append("EVENT_MFI_TOO_HOT")
    if _debug_value(signal, "ret_24_pct") > float(variant["event_max_ret_24_pct"]):
        suppress.append("EVENT_RET24_TOO_HOT")
    if _debug_value(signal, "lower_low_streak_5") > float(variant["event_max_lower_low_streak_5"]):
        suppress.append("EVENT_LOWER_LOW_STREAK_ACTIVE")
    return not suppress, suppress


def _passes_deep_base(signal: dict[str, Any], variant: dict[str, Any]) -> tuple[bool, list[str]]:
    early_ok = (
        _debug_value(signal, "rsi14") >= float(variant["deep_early_min_rsi14"])
        and _debug_value(signal, "ret_24_pct") <= float(variant["deep_early_max_ret_24_pct"])
        and _debug_value(signal, "lower_low_streak_5") <= float(variant["deep_early_max_lower_low_streak_5"])
        and _debug_value(signal, "new_low_count_20") <= float(variant["deep_early_max_new_low_count_20"])
        and _debug_value(signal, "distance_to_event_low_pct", 999.0)
        <= float(variant["deep_early_max_distance_to_event_low_pct"])
    )
    late_ok = (
        float(variant["deep_late_min_distance_to_event_low_pct"])
        <= _debug_value(signal, "distance_to_event_low_pct", 999.0)
        <= float(variant["deep_late_max_distance_to_event_low_pct"])
        and _debug_value(signal, "lower_low_streak_5") <= float(variant["deep_late_max_lower_low_streak_5"])
        and _debug_value(signal, "ret_24_pct") <= float(variant["deep_late_max_ret_24_pct"])
        and _debug_value(signal, "new_low_count_20") <= float(variant["deep_late_max_new_low_count_20"])
    )
    if early_ok or late_ok:
        return True, []
    return False, ["DEEP_NOT_EARLY_RECOVERY_OR_LATE_RETEST"]


def _passes_base_suppression(signal: dict[str, Any], variant: dict[str, Any]) -> tuple[bool, list[str]]:
    if _is_deep_source(signal):
        return _passes_deep_base(signal, variant)
    return _passes_event_base(signal, variant)


def _filter_base_signals(base_signals: list[dict[str, Any]], variant: dict[str, Any]) -> list[dict[str, Any]]:
    kept: list[dict[str, Any]] = []
    for signal in base_signals:
        ok, suppress = _passes_base_suppression(signal, variant)
        if not ok:
            continue
        enriched = dict(signal)
        enriched["family_id"] = str(variant["family_id"])
        enriched["bucket"] = str(variant["bucket"])
        enriched["strategy_scope"] = "entry_only_base_false_suppression"
        enriched["trigger_votes"] = list(enriched.get("trigger_votes", [])) + [str(variant["family_id"])]
        enriched["context_votes"] = list(enriched.get("context_votes", [])) + [
            "BASE_SOURCE_SPLIT",
            "PAST_ONLY_FALSE_SUPPRESSION",
        ]
        enriched["suppress_votes"] = suppress
        debug = dict(enriched.get("debug") or {})
        debug["bfs_variant"] = str(variant["family_id"])
        debug["bfs_source_type"] = "DEEP" if _is_deep_source(signal) else "EVENT"
        enriched["debug"] = debug
        kept.append(enriched)
    return kept


def _run_base_filter_result(
    base_signals: list[dict[str, Any]],
    variant: dict[str, Any],
    manual_entries: list[Any],
) -> dict[str, Any]:
    signals = _filter_base_signals(base_signals, variant)
    result = _run_result(
        str(variant["family_id"]),
        str(variant["bucket"]),
        str(variant["description_ru"]),
        signals,
        manual_entries,
    )
    result["raw_candidates_total"] = len(base_signals)
    result["suppressed_candidates_total"] = max(0, len(base_signals) - len(signals))
    result["filtered_candidates_total"] = len(signals)
    result["params"] = {**result["params"], **{k: v for k, v in variant.items() if k not in {"description_ru"}}}
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


def _render_label(rank: int, family_id: str) -> str:
    compact = (
        family_id.lower()
        .replace("bfs20_union_", "u_")
        .replace("base_source_split_", "bss_")
        .replace("_false_suppression", "_fs")
        .replace("_strict", "_s")
        .replace("_relaxed_diagnostic", "_rel")
        .replace("_tight_deep", "_td")
        .replace("_plus_htfs01", "_h01")
        .replace("bfs90_htfs01_hot_trend_strict_false_suppression", "h01")
        .replace("bfs00_base_v4_raw", "base_raw")
    )
    return f"bfs_v6_{rank:02d}_{compact[:80]}"


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Base False Suppression V6",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "Контракт: entry-only, signal-свеча закрыта, LONG исполняется на `open` следующей свечи, `lookahead=NO`, slippage `5 bps`.",
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
            "V6 резко уменьшает ложные входы базовой V4-части и сохраняет чистый `HTFS01`. "
            "Это лучший текущий entry-only результат на одном holdout-дне, но из-за риска подгонки по одному дню "
            "в ML его не передавать до проверки на следующих размеченных днях.",
            "",
        ]
    )
    return "\n".join(lines)


def run_search(manual_entries_path: Path, out_dir: Path, *, render_top: int = 8) -> dict[str, Any]:
    manual_payload, manual_entries = load_manual_entries(manual_entries_path)
    _, rows = _prepare_rows(manual_entries_path)
    _enrich_quality_rows(rows)
    _with_event_features(rows)

    event_base = _build_olev20(rows, manual_entries)
    deep_source = _run_result(
        "BFS00_DEEP_RECOVERY_SOURCE",
        "BASE_DEEP_RECOVERY_SOURCE",
        "Deep-recovery source для V6.",
        _deep_recovery_signals(rows),
        manual_entries,
    )
    base_v4_signals = _union_signals([event_base, deep_source], family_id="BFS00_BASE_V4_RAW", gap_bars=8)
    base_v4 = _run_result(
        "BFS00_BASE_V4_RAW",
        "BASE_V4_RAW",
        "Сырой базовый V4 union без hot/trend.",
        base_v4_signals,
        manual_entries,
    )
    base_results = [_run_base_filter_result(base_v4_signals, variant, manual_entries) for variant in BASE_SUPPRESSION_VARIANTS]

    broad_hot_signals = _hot_trend_recall_signals(rows)
    hot_result = _run_filtered_hot_result(
        broad_hot_signals,
        next(variant for variant in HOT_TREND_SUPPRESSION_VARIANTS if variant["family_id"] == "HTFS01_HOT_TREND_STRICT_FALSE_SUPPRESSION"),
        manual_entries,
    )
    hot_result["family_id"] = "BFS90_HTFS01_HOT_TREND_STRICT_FALSE_SUPPRESSION"

    union_results: list[dict[str, Any]] = []
    for base_result in base_results:
        union = _run_result(
            f"BFS20_UNION_{base_result['family_id']}_PLUS_HTFS01",
            "BASE_FALSE_SUPPRESSION_UNION",
            f"Union {base_result['family_id']} плюс чистый HTFS01.",
            _union_signals([base_result, hot_result], family_id=f"BFS20_UNION_{base_result['family_id']}_PLUS_HTFS01", gap_bars=8),
            manual_entries,
        )
        union["params"] = {
            **union["params"],
            "base_filter_family_id": base_result["family_id"],
            "hot_filter_family_id": hot_result["family_id"],
            "cooldown_used": False,
        }
        union_results.append(union)

    results = [base_v4, *base_results, hot_result, *union_results]
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
        "strategy_scope": "entry_only_base_false_suppression",
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
    json_path = out_dir / f"visual_entry_base_false_suppression_v6_{day}_{safe_role}.json"
    md_path = out_dir / f"visual_entry_base_false_suppression_v6_{day}_{safe_role}_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run base false suppression V6 visual-entry diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/base_false_suppression")
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
