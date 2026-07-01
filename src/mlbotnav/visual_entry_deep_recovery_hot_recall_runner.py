from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.render_visual_entry_overlay import render_family_candidate_overlay
from mlbotnav.visual_entry_no_lookahead_candidates import _prepare_rows
from mlbotnav.visual_entry_online_low_event_quality_runner import (
    EVENT_VARIANTS,
    _low_zone,
    _run_event_variant,
    _run_union as _run_olev_union,
    _source_candidates,
    _with_event_features,
)
from mlbotnav.visual_entry_quality_filter_runner import _enrich_quality_rows
from mlbotnav.visual_entry_regime_split_ranker_runner import REGIME_VARIANTS, _raw_candidates, _select_online_no_rewrite
from mlbotnav.visual_entry_score import TradeEntry, load_manual_entries, score_entries
from mlbotnav.visual_entry_significant_low_selector_runner import SLIPPAGE_BPS, _score_summary


STATUS = "DEV_DEEP_RECOVERY_AND_HOT_RECALL_V4_ENTRY_ONLY_NO_ML"


def _value(row: dict[str, Any], key: str, default: float = 0.0) -> float:
    value = row.get(key)
    if value is None:
        return default
    return float(value)


def _signal_payload(rows: list[dict[str, Any]], signal_idx: int, family_id: str, bucket: str, votes: list[str]) -> dict[str, Any]:
    signal = rows[signal_idx]
    entry = rows[signal_idx + 1]
    entry_open = float(entry["open"])
    return {
        "family_id": family_id,
        "bucket": bucket,
        "side": "long",
        "signal_row_index": signal_idx,
        "entry_row_index": signal_idx + 1,
        "signal_time_utc": signal["open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_time_utc": entry["open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_open_price": entry_open,
        "entry_price_with_slippage": entry_open * (1.0 + SLIPPAGE_BPS / 10000.0),
        "slippage_bps": SLIPPAGE_BPS,
        "entry_rule": "next_bar_open_after_signal_close",
        "strategy_scope": "entry_only_deep_recovery_hot_recall",
        "lookahead": "NO",
        "cooldown_used": False,
        "future_trade_outcome_used": False,
        "context_votes": votes,
        "trigger_votes": ["NEXT_OPEN_ENTRY_ONLY", family_id],
        "confirm_votes": [],
        "suppress_votes": [],
        "debug": {
            "low_zone": _low_zone(signal),
            "ret_12_pct": _value(signal, "ret_12_pct", 0.0),
            "ret_24_pct": _value(signal, "ret_24_pct", 0.0),
            "rsi14": _value(signal, "rsi14", 0.0),
            "stoch_k14": _value(signal, "stoch_k14", 0.0),
            "mfi14": _value(signal, "mfi14", 0.0),
            "lower_wick_share": _value(signal, "lower_wick_share", 0.0),
            "close_pos_candle": _value(signal, "close_pos_candle", 0.0),
            "new_low_count_20": _value(signal, "new_low_count_20", 0.0),
            "lower_low_streak_5": _value(signal, "lower_low_streak_5", 0.0),
            "support_touch_count_60": _value(signal, "support_touch_count_60", 0.0),
            "distance_to_event_low_pct": _value(signal, "distance_to_event_low_pct", 999.0),
            "pullback_from_recent_high_20_pct": _value(signal, "pullback_from_recent_high_20_pct", 0.0),
        },
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


def _deep_recovery_signals(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    raw: list[dict[str, Any]] = []
    for signal_idx in range(60, len(rows) - 1):
        row = rows[signal_idx]
        low_zone = _low_zone(row)
        if low_zone > 0.12:
            continue
        if not (_value(row, "ret_12_pct", 0.0) <= -0.35 or _value(row, "ret_24_pct", 0.0) <= -0.55):
            continue
        if max(_value(row, "rsi14", 999.0), _value(row, "stoch_k14", 999.0), _value(row, "mfi14", 999.0)) > 45.0:
            continue
        if _value(row, "new_low_count_20", 0.0) > 12:
            continue
        if _value(row, "lower_low_streak_5", 0.0) > 3:
            continue
        if _value(row, "lower_wick_share", 0.0) < 0.20 and _value(row, "close_pos_candle", 0.0) < 0.25:
            continue
        raw.append(
            _signal_payload(
                rows,
                signal_idx,
                "DRHR01_DEEP_RECOVERY_COLD_RECLAIM",
                "DEEP_RECOVERY",
                ["DEEP_LOW_ZONE", "RECENT_DROP", "COLD_OSC", "RECLAIM_OR_WICK", "NEW_LOW_CHAIN_CONTROL"],
            )
        )
    return _select_online_no_rewrite(raw, min_gap_bars=10)


def _hot_trend_recall_signals(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    source_variants = [
        item
        for item in REGIME_VARIANTS
        if item["family_id"]
        in {
            "RSR03_HOT_RECLAIM_SUPPORT_CLUSTER",
            "RSR05_TREND_DIP_CONTINUATION_CLUSTER",
            "RSR07_STRUCTURE_BOS_FIBO_VOLUME_CLUSTER",
        }
    ]
    by_idx: dict[int, dict[str, Any]] = {}
    for variant in source_variants:
        for signal in _raw_candidates(rows, variant):
            by_idx.setdefault(int(signal["signal_row_index"]), signal)

    raw: list[dict[str, Any]] = []
    for signal_idx in sorted(by_idx):
        row = rows[signal_idx]
        if _low_zone(row) > 0.82:
            continue
        if _value(row, "distance_to_event_low_pct", 999.0) > 0.55:
            continue
        if _value(row, "pullback_from_recent_high_20_pct", 0.0) < 0.10:
            continue
        if _value(row, "support_touch_count_60", 0.0) < 18:
            continue
        if _value(row, "close_pos_candle", 0.0) < 0.90 and _value(row, "lower_wick_share", 0.0) < 0.30:
            continue
        if _value(row, "new_low_count_20", 0.0) > 8:
            continue
        if _value(row, "ret_24_pct", 0.0) > 0.10:
            continue
        if (
            _value(row, "ret_24_pct", 0.0) > 0.0
            and _low_zone(row) > 0.55
            and max(_value(row, "rsi14", 0.0), _value(row, "stoch_k14", 0.0), _value(row, "mfi14", 0.0)) > 78.0
            and _value(row, "lower_wick_share", 0.0) < 0.25
        ):
            continue
        raw.append(
            _signal_payload(
                rows,
                signal_idx,
                "DRHR02_HOT_TREND_RECALL_DIAGNOSTIC",
                "HOT_TREND_RECALL_DIAGNOSTIC",
                ["SUPPORT_RECLAIM", "EVENT_LOW_DISTANCE", "PULLBACK_CONTEXT", "HOT_SHELF_SUPPRESS"],
            )
        )
    return _select_online_no_rewrite(raw, min_gap_bars=10)


def _run_result(family_id: str, bucket: str, description_ru: str, signals: list[dict[str, Any]], manual_entries: list[Any]) -> dict[str, Any]:
    score = score_entries(manual_entries, [_to_trade(item) for item in signals])
    return {
        "family_id": family_id,
        "bucket": bucket,
        "regime": bucket,
        "description_ru": description_ru,
        "params": {"cooldown_used": False, "selection_rule": "first_qualified_no_future_rewrite"},
        "raw_candidates_total": len(signals),
        "suppressed_candidates_total": 0,
        "filtered_candidates_total": len(signals),
        "clusters_total": len(signals),
        "score": _score_summary(score),
        "hit_details": score["hit_details"],
        "missed_target_details": score["missed_target_details"],
        "false_entry_details": score["false_entry_details"][:250],
        "signals": signals,
        "selection_rule": "first_qualified_no_future_rewrite",
    }


def _union_signals(source_results: list[dict[str, Any]], *, family_id: str, gap_bars: int) -> list[dict[str, Any]]:
    raw: list[dict[str, Any]] = []
    for result in source_results:
        for signal in result.get("signals", []):
            enriched = dict(signal)
            enriched["source_family_id"] = result["family_id"]
            enriched["family_id"] = family_id
            enriched["bucket"] = "DEEP_RECOVERY_HOT_RECALL_UNION"
            enriched["trigger_votes"] = list(enriched.get("trigger_votes", [])) + ["DRHR_UNION"]
            raw.append(enriched)
    return _select_online_no_rewrite(raw, min_gap_bars=gap_bars)


def _build_olev20(rows: list[dict[str, Any]], manual_entries: list[Any]) -> dict[str, Any]:
    source_by_family = _source_candidates(rows)
    event_results = [_run_event_variant(source_by_family, manual_entries, variant) for variant in EVENT_VARIANTS if "quality_min_score" in variant]
    params = next(item for item in EVENT_VARIANTS if item["family_id"] == "OLEV20_UNION_EVENT_QUALITY_BALANCED")
    result = _run_olev_union(event_results, manual_entries, params)
    result["family_id"] = "DRHR00_BASE_OLEV20_EVENT_QUALITY"
    result["bucket"] = "BASE_EVENT_QUALITY"
    result["description_ru"] = "Базовый чистый OLEV20 из V3 без изменений."
    return result


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Deep Recovery And Hot Recall V4",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "Контракт: entry-only, signal-свеча закрыта, вход LONG на `open` следующей свечи, `lookahead=NO`, slippage `5 bps`.",
        "",
        "Граница: сделки, TP/SL, MFE/MAE, future return, entry-candle OHLCV, cooldown-сетки `30/45/60/90` и ML-export не используются.",
        "",
        "| rank | family | hits | miss | false | entries | f1 |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for rank, item in enumerate(payload["best_overall"], 1):
        score = item["score"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{:.4f}` |".format(
                rank,
                item["family_id"],
                score["target_hits"],
                score["missed_targets"],
                score["false_entries"],
                score["entries_total"],
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
            "V4 добавляет deep-recovery поверх чистого OLEV20. Hot/trend recall оставлен диагностическим, потому что пока тянет слишком много ложных входов.",
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
        "DRHR01_DEEP_RECOVERY_COLD_RECLAIM",
        "DEEP_RECOVERY",
        "Deep-recovery: холодный low с падением, контролем цепочки новых low и wick/reclaim.",
        _deep_recovery_signals(rows),
        manual_entries,
    )
    hot = _run_result(
        "DRHR02_HOT_TREND_RECALL_DIAGNOSTIC",
        "HOT_TREND_RECALL_DIAGNOSTIC",
        "Диагностический hot/trend recall. Пока не входит в основной union из-за высокого false.",
        _hot_trend_recall_signals(rows),
        manual_entries,
    )
    union = _run_result(
        "DRHR20_OLEV20_PLUS_DEEP_RECOVERY",
        "DEEP_RECOVERY_HOT_RECALL_UNION",
        "Основной V4 union: чистый OLEV20 плюс deep-recovery, без hot/trend diagnostic.",
        _union_signals([base, deep], family_id="DRHR20_OLEV20_PLUS_DEEP_RECOVERY", gap_bars=8),
        manual_entries,
    )
    union_diag = _run_result(
        "DRHR21_FULL_DIAGNOSTIC_WITH_HOT_TREND",
        "DEEP_RECOVERY_HOT_RECALL_UNION",
        "Диагностический полный union: OLEV20 + deep + hot/trend recall.",
        _union_signals([base, deep, hot], family_id="DRHR21_FULL_DIAGNOSTIC_WITH_HOT_TREND", gap_bars=8),
        manual_entries,
    )
    results = [union, base, deep, hot, union_diag]
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
            label=f"deep_recovery_hot_recall_v4_{rank:02d}_{result['family_id'].lower()}",
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
        "strategy_scope": "entry_only_deep_recovery_hot_recall",
        "online_event_state_used": True,
        "online_duplicate_suppression_used": True,
        "cooldown_used": False,
        "future_trade_outcome_used": False,
        "entry_candle_ohlcv_features_used": False,
        "ml_transfer_allowed": False,
        "best_overall": results,
        "rendered_overlays": rendered,
    }
    json_path = out_dir / f"visual_entry_deep_recovery_hot_recall_v4_{day}_{safe_role}.json"
    md_path = out_dir / f"visual_entry_deep_recovery_hot_recall_v4_{day}_{safe_role}_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deep recovery and hot recall V4 visual-entry diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/deep_recovery_hot_recall")
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
