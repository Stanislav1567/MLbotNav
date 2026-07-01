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


STATUS = "DEV_SIGNIFICANT_LOW_SELECTOR_V1_ENTRY_ONLY_NO_ML"
SLIPPAGE_BPS = 5.0


VARIANTS: list[dict[str, Any]] = [
    {
        "family_id": "SLS01_DEEP_CAPITULATION_LOW",
        "bucket": "DEEP_KNIFE",
        "min_score": 8,
        "description_ru": "Глубокий low после сброса: trailing local-low, низ диапазона, холодные осцилляторы, падение и фитиль/reclaim.",
    },
    {
        "family_id": "SLS02_SUPPORT_RECLAIM_LOW",
        "bucket": "SUPPORT_RETEST",
        "min_score": 8,
        "description_ru": "Ретест поддержки: много касаний зоны, свеча у low, есть фитиль или закрытие выше тела.",
    },
    {
        "family_id": "SLS03_TREND_DIP_CONTINUATION_LOW",
        "bucket": "TREND_DIP",
        "min_score": 8,
        "description_ru": "Дип в живом движении: EMA не мертвая, откат не перегрет, есть локальный low/reclaim.",
    },
    {
        "family_id": "SLS04_HOT_RECLAIM_LOW",
        "bucket": "HOT_RECLAIM",
        "min_score": 9,
        "description_ru": "Горячий reclaim-low: допускает не холодные RSI/Stoch, если есть поддержка, фитиль и закрытие в верхней части свечи.",
    },
    {
        "family_id": "SLS05_DEEP_CAPITULATION_STRICT_FALSE_CONTROL",
        "bucket": "DEEP_KNIFE_STRICT",
        "min_score": 11,
        "description_ru": "Строгий deep-low контроль false: оставляет только самые сильные ножи/капитуляции.",
    },
    {
        "family_id": "SLS06_HOT_RECLAIM_STRICT_FALSE_CONTROL",
        "bucket": "HOT_RECLAIM_STRICT",
        "min_score": 10,
        "description_ru": "Строгий hot-reclaim контроль false: меньше входов, но ближе к чистому визуальному слою.",
    },
    {
        "family_id": "SLS10_COMBINED_SIGNIFICANT_LOW",
        "bucket": "COMBINED",
        "min_score": 10,
        "description_ru": "Сводный significant-low слой: смешивает deep/support/trend/hot признаки без TP/SL и без будущей доходности.",
    },
    {
        "family_id": "SLS11_COMBINED_BALANCED_FALSE_CONTROL",
        "bucket": "COMBINED_BALANCED",
        "min_score": 11,
        "description_ru": "Сводный balanced слой: меньше recall, но заметно меньше ложных входов, чем широкий combined.",
    },
]


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


def _osc_cold(row: dict[str, Any], threshold: float) -> bool:
    return (
        _value(row, "rsi14", 999.0) <= threshold
        or _value(row, "stoch_k14", 999.0) <= threshold
        or _value(row, "mfi14", 999.0) <= threshold
    )


def _local_low(row: dict[str, Any]) -> bool:
    return bool(row.get("local_low_5") or row.get("local_low_10") or row.get("local_low_20"))


def _score_deep(row: dict[str, Any]) -> tuple[int, list[str]]:
    score = 0
    votes: list[str] = []
    if _low_zone(row) <= 0.18:
        score += 3
        votes.append("DEEP_LOW_ZONE")
    if _local_low(row):
        score += 2
        votes.append("TRAILING_LOCAL_LOW")
    if _value(row, "ret_12_pct", 999.0) <= -0.25 or _value(row, "ret_24_pct", 999.0) <= -0.45:
        score += 2
        votes.append("RECENT_DROP")
    if _osc_cold(row, 45.0):
        score += 2
        votes.append("COLD_OSC")
    if _value(row, "lower_wick_share", 0.0) >= 0.20 or _value(row, "close_pos_candle", 0.0) >= 0.45:
        score += 1
        votes.append("WICK_OR_RECLAIM")
    if _value(row, "vol_z20", -999.0) >= 0.25:
        score += 1
        votes.append("VOLUME_PRESENT")
    return score, votes


def _score_support(row: dict[str, Any]) -> tuple[int, list[str]]:
    score = 0
    votes: list[str] = []
    if _value(row, "support_touch_count_60", 0.0) >= 16:
        score += 3
        votes.append("SUPPORT_TOUCH_60")
    if _low_zone(row) <= 0.55:
        score += 2
        votes.append("LOW_ZONE")
    if _value(row, "lower_wick_share", 0.0) >= 0.20:
        score += 1
        votes.append("LOWER_WICK")
    if _value(row, "close_pos_candle", 0.0) >= 0.50:
        score += 2
        votes.append("CLOSE_RECLAIM")
    if _value(row, "ret_6_pct", 999.0) <= 0.25:
        score += 1
        votes.append("NOT_EXTENDED_RET6")
    if _value(row, "rsi14", 999.0) <= 75.0 or _value(row, "mfi14", 999.0) <= 60.0:
        score += 1
        votes.append("OSC_ALLOWED")
    return score, votes


def _score_trend(row: dict[str, Any]) -> tuple[int, list[str]]:
    score = 0
    votes: list[str] = []
    if _value(row, "ema20_slope_5_pct", -999.0) >= -0.03:
        score += 2
        votes.append("EMA20_ALIVE")
    if _value(row, "support_touch_count_60", 0.0) >= 10:
        score += 2
        votes.append("SUPPORT_TOUCH_60")
    if _value(row, "ret_6_pct", 999.0) <= 0.25:
        score += 1
        votes.append("RET6_NOT_EXTENDED")
    if _low_zone(row) <= 0.75:
        score += 1
        votes.append("NOT_HIGH_ZONE")
    if _value(row, "lower_wick_share", 0.0) >= 0.20 or _value(row, "close_pos_candle", 0.0) >= 0.50:
        score += 2
        votes.append("DIP_TRIGGER")
    if _value(row, "new_low_count_20", 999.0) <= 8:
        score += 1
        votes.append("NOT_TOO_MANY_NEW_LOWS")
    return score, votes


def _score_hot(row: dict[str, Any]) -> tuple[int, list[str]]:
    score = 0
    votes: list[str] = []
    if _value(row, "support_touch_count_60", 0.0) >= 14:
        score += 2
        votes.append("SUPPORT_TOUCH_60")
    if _value(row, "lower_wick_share", 0.0) >= 0.25:
        score += 2
        votes.append("LOWER_WICK")
    if _value(row, "close_pos_candle", 0.0) >= 0.75:
        score += 3
        votes.append("STRONG_RECLAIM_CLOSE")
    if _value(row, "ema20_slope_5_pct", -999.0) >= -0.01:
        score += 1
        votes.append("EMA_NOT_DEAD")
    if _value(row, "ret_6_pct", 999.0) <= 0.30:
        score += 1
        votes.append("RET6_NOT_EXTENDED")
    if _low_zone(row) <= 0.90:
        score += 1
        votes.append("LOW_ZONE_ALLOWED")
    return score, votes


def _score_variant(row: dict[str, Any], family_id: str) -> tuple[int, list[str], list[str], list[str]]:
    deep_score, deep_votes = _score_deep(row)
    support_score, support_votes = _score_support(row)
    trend_score, trend_votes = _score_trend(row)
    hot_score, hot_votes = _score_hot(row)
    if family_id in {"SLS01_DEEP_CAPITULATION_LOW", "SLS05_DEEP_CAPITULATION_STRICT_FALSE_CONTROL"}:
        return deep_score, deep_votes, ["DEEP_SIGNAL_LOW"], []
    if family_id == "SLS02_SUPPORT_RECLAIM_LOW":
        return support_score, support_votes, ["SUPPORT_RECLAIM_SIGNAL_LOW"], []
    if family_id == "SLS03_TREND_DIP_CONTINUATION_LOW":
        return trend_score, trend_votes, ["TREND_DIP_SIGNAL_LOW"], []
    if family_id in {"SLS04_HOT_RECLAIM_LOW", "SLS06_HOT_RECLAIM_STRICT_FALSE_CONTROL"}:
        return hot_score, hot_votes, ["HOT_RECLAIM_SIGNAL_LOW"], []

    combined = max(deep_score, support_score, trend_score, hot_score)
    votes: list[str] = []
    for prefix, score, source_votes in [
        ("DEEP", deep_score, deep_votes),
        ("SUPPORT", support_score, support_votes),
        ("TREND", trend_score, trend_votes),
        ("HOT", hot_score, hot_votes),
    ]:
        if score >= 7:
            votes.extend(f"{prefix}:{vote}" for vote in source_votes)
    if sum(score >= 7 for score in [deep_score, support_score, trend_score, hot_score]) >= 2:
        combined += 1
        votes.append("MULTI_FAMILY_CONFIRM")
    return combined, votes, ["COMBINED_SIGNIFICANT_LOW"], []


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


def _signal_payload(rows: list[dict[str, Any]], signal_idx: int, variant: dict[str, Any], score: int, context: list[str], trigger: list[str]) -> dict[str, Any]:
    signal = rows[signal_idx]
    entry = rows[signal_idx + 1]
    entry_open = float(entry["open"])
    return {
        "family_id": str(variant["family_id"]),
        "bucket": str(variant["bucket"]),
        "side": "long",
        "signal_row_index": signal_idx,
        "entry_row_index": signal_idx + 1,
        "signal_time_utc": signal["open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_time_utc": entry["open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_open_price": entry_open,
        "entry_price_with_slippage": entry_open * (1.0 + SLIPPAGE_BPS / 10000.0),
        "slippage_bps": SLIPPAGE_BPS,
        "entry_rule": "next_bar_open_after_signal_close",
        "strategy_scope": "entry_only_low_detection",
        "lookahead": "NO",
        "cooldown_used": False,
        "future_trade_outcome_used": False,
        "priority_score": score,
        "context_votes": context,
        "trigger_votes": trigger + ["NEXT_OPEN_ENTRY_ONLY"],
        "confirm_votes": [],
        "suppress_votes": [],
        "debug": {
            "low_zone": _low_zone(signal),
            "support_touch_count_60": _value(signal, "support_touch_count_60", 0.0),
            "ret_6_pct": _value(signal, "ret_6_pct", 0.0),
            "ret_12_pct": _value(signal, "ret_12_pct", 0.0),
            "ret_24_pct": _value(signal, "ret_24_pct", 0.0),
            "rsi14": _value(signal, "rsi14", 0.0),
            "stoch_k14": _value(signal, "stoch_k14", 0.0),
            "mfi14": _value(signal, "mfi14", 0.0),
            "lower_wick_share": _value(signal, "lower_wick_share", 0.0),
            "close_pos_candle": _value(signal, "close_pos_candle", 0.0),
            "vol_z20": _value(signal, "vol_z20", 0.0),
            "ema20_slope_5_pct": _value(signal, "ema20_slope_5_pct", 0.0),
            "ema_gap_pct": _value(signal, "ema_gap_pct", 0.0),
            "local_low_5": bool(signal.get("local_low_5")),
            "local_low_10": bool(signal.get("local_low_10")),
            "local_low_20": bool(signal.get("local_low_20")),
        },
    }


def _run_variant(rows: list[dict[str, Any]], manual_entries: list[Any], variant: dict[str, Any]) -> dict[str, Any]:
    signals: list[dict[str, Any]] = []
    for signal_idx in range(60, len(rows) - 1):
        signal = rows[signal_idx]
        score, context, trigger, suppress = _score_variant(signal, str(variant["family_id"]))
        if score < int(variant["min_score"]):
            continue
        payload = _signal_payload(rows, signal_idx, variant, score, context, trigger)
        payload["suppress_votes"] = suppress
        signals.append(payload)

    trades = [_to_trade(item) for item in signals]
    score = score_entries(manual_entries, trades)
    return {
        "family_id": str(variant["family_id"]),
        "bucket": str(variant["bucket"]),
        "description_ru": str(variant["description_ru"]),
        "params": {"min_score": int(variant["min_score"]), "cooldown_used": False},
        "score": _score_summary(score),
        "hit_details": score["hit_details"],
        "missed_target_details": score["missed_target_details"],
        "false_entry_details": score["false_entry_details"][:250],
        "signals": signals,
    }


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Significant Low Selector V1",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "Контракт: signal-свеча уже закрыта, LONG-вход ставится на open следующей свечи, `lookahead=NO`, slippage `5 bps`.",
        "",
        "Граница: сделки не тянем, TP/SL/MFE/MAE/future return не используются, cooldown-сетки не используются.",
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
            "## Вывод",
            "",
            "Это DEV diagnostic-only. В ML ничего не передавать. Если слой дает много false, его надо использовать как карту признаков, а не как готовый вход.",
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
            label=f"sls_v1_{rank:02d}_{result['family_id'].lower()}",
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
        "cooldown_used": False,
        "future_trade_outcome_used": False,
        "ml_transfer_allowed": False,
        "best_overall": results,
        "rendered_overlays": rendered,
    }
    json_path = out_dir / f"visual_entry_significant_low_selector_v1_{day}_{safe_role}.json"
    md_path = out_dir / f"visual_entry_significant_low_selector_v1_{day}_{safe_role}_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run significant low selector visual-entry diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/significant_low_selector")
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
