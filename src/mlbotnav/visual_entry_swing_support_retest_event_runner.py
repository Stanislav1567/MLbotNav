from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.render_visual_entry_overlay import render_family_candidate_overlay
from mlbotnav.visual_entry_no_lookahead_candidates import _prepare_rows
from mlbotnav.visual_entry_quality_filter_runner import _enrich_quality_rows
from mlbotnav.visual_entry_reversal_bottom_knife_drop_runner import _low_zone, _score_summary, _value
from mlbotnav.visual_entry_score import TradeEntry, load_manual_entries, score_entries


STATUS = "DEV_SWING_SUPPORT_RETEST_EVENT_V1_ENTRY_ONLY_NO_ML"
SLIPPAGE_BPS = 5.0


EVENT_VARIANTS: list[dict[str, Any]] = [
    {
        "family_id": "SSRE01_SUPPORT_RETEST_FIRST_LOW_ENTRY",
        "bucket": "SUPPORT_RETEST",
        "cooldown_bars": 45,
        "event_timeout_bars": 8,
        "event_min_score": 8,
        "trigger_min_score": 3,
        "support_touches_min": 12,
        "low_zone_max": 0.70,
        "rsi_max": 90.0,
        "ret12_max": 0.85,
        "ema20_slope_min": -0.04,
        "wick_min": 0.10,
        "closepos_min": 0.20,
        "description_ru": "Ретест поддержки: сначала открывается событие зоны low/support, затем берется первый вход на следующем open.",
    },
    {
        "family_id": "SSRE02_TREND_DIP_FIRST_LOW_ENTRY",
        "bucket": "TREND_DIP",
        "cooldown_bars": 45,
        "event_timeout_bars": 6,
        "event_min_score": 7,
        "trigger_min_score": 3,
        "support_touches_min": 8,
        "low_zone_max": 0.95,
        "rsi_max": 88.0,
        "ret6_max": 0.20,
        "ret12_max": 0.75,
        "ema20_slope_min": 0.00,
        "wick_min": 0.10,
        "closepos_min": 0.20,
        "description_ru": "Дип в живом движении: ищет локальный провал у поддержки без требования классической перепроданности.",
    },
    {
        "family_id": "SSRE03_DEEP_KNIFE_FIRST_RECLAIM_ENTRY",
        "bucket": "DEEP_KNIFE",
        "cooldown_bars": 60,
        "event_timeout_bars": 10,
        "event_min_score": 7,
        "trigger_min_score": 3,
        "support_touches_min": 1,
        "low_zone_max": 0.42,
        "rsi_max": 72.0,
        "ret6_max": 0.25,
        "ret12_max": 0.20,
        "ret24_max": -0.05,
        "ema20_slope_min": -0.30,
        "wick_min": 0.08,
        "closepos_min": 0.10,
        "description_ru": "Глубокий нож/провал: событие открывается на сильном low-контексте, вход один раз на первом reclaim/low-триггере.",
    },
    {
        "family_id": "SSRE04_HOT_SUPPORT_CONTINUATION_LOW_ENTRY",
        "bucket": "HOT_SUPPORT_CONTINUATION",
        "cooldown_bars": 60,
        "event_timeout_bars": 6,
        "event_min_score": 8,
        "trigger_min_score": 4,
        "support_touches_min": 16,
        "low_zone_max": 1.00,
        "rsi_max": 92.0,
        "ret6_max": 0.22,
        "ret12_max": 0.90,
        "ema20_slope_min": 0.00,
        "wick_min": 0.20,
        "closepos_min": 0.45,
        "description_ru": "Горячий continuation-ретест: для ручных low-входов, где осцилляторы не холодные, но есть поддержка и локальный откат.",
    },
]


def _is_local_low(row: dict[str, Any], bars: int) -> bool:
    return bool(row.get(f"local_low_{bars}"))


def _event_score(row: dict[str, Any], params: dict[str, Any]) -> tuple[int, list[str]]:
    score = 0
    votes: list[str] = []
    bucket = str(params["bucket"])
    support_touches = _value(row, "support_touch_count_60", 0.0)
    low_zone = _low_zone(row)

    if support_touches >= float(params["support_touches_min"]):
        score += 3
        votes.append("EV_SUPPORT_TOUCH_60")
    if low_zone <= float(params["low_zone_max"]):
        score += 2
        votes.append("EV_LOW_ZONE")
    if _is_local_low(row, 5):
        score += 2
        votes.append("EV_LOCAL_LOW_5")
    if _is_local_low(row, 10):
        score += 1
        votes.append("EV_LOCAL_LOW_10")
    if _value(row, "rsi14", 999.0) <= float(params["rsi_max"]):
        score += 1
        votes.append("EV_RSI_ALLOWED")
    if _value(row, "ret_12_pct", 999.0) <= float(params["ret12_max"]):
        score += 1
        votes.append("EV_RET12_ALLOWED")
    if _value(row, "ema20_slope_5_pct", -999.0) >= float(params["ema20_slope_min"]):
        score += 1
        votes.append("EV_EMA_SLOPE_ALLOWED")

    if bucket == "DEEP_KNIFE":
        if _value(row, "ret_24_pct", 999.0) <= float(params["ret24_max"]):
            score += 2
            votes.append("EV_RET24_DROP")
        if low_zone <= min(0.30, float(params["low_zone_max"])):
            score += 1
            votes.append("EV_DEEP_LOW_ZONE")
    elif bucket == "HOT_SUPPORT_CONTINUATION":
        if support_touches >= float(params["support_touches_min"]) + 8:
            score += 1
            votes.append("EV_DENSE_SUPPORT")
        if _value(row, "ema20_slope_5_pct", -999.0) >= 0.03:
            score += 1
            votes.append("EV_POSITIVE_EMA_SLOPE")

    return score, votes


def _trigger_score(row: dict[str, Any], params: dict[str, Any]) -> tuple[int, list[str]]:
    score = 0
    votes: list[str] = []
    if _is_local_low(row, 5):
        score += 2
        votes.append("TRG_LOCAL_LOW_5")
    if _value(row, "lower_wick_share", 0.0) >= float(params["wick_min"]):
        score += 1
        votes.append("TRG_LOWER_WICK")
    if _value(row, "close_pos_candle", 0.0) >= float(params["closepos_min"]):
        score += 1
        votes.append("TRG_CLOSE_RECLAIM")
    if _value(row, "ret_6_pct", 999.0) <= float(params.get("ret6_max", 999.0)):
        score += 1
        votes.append("TRG_RET6_NOT_EXTENDED")
    if _value(row, "lower_low_streak_5", 0.0) <= 3:
        score += 1
        votes.append("TRG_NOT_LONG_FALLING_CHAIN")
    return score, votes


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


def _build_signal(
    rows: list[dict[str, Any]],
    signal_idx: int,
    params: dict[str, Any],
    event_open_idx: int,
    event_votes: list[str],
    trigger_votes: list[str],
    event_score: int,
    trigger_score: int,
) -> dict[str, Any]:
    signal_row = rows[signal_idx]
    entry_row = rows[signal_idx + 1]
    entry_open = float(entry_row["open"])
    return {
        "family_id": str(params["family_id"]),
        "bucket": str(params["bucket"]),
        "side": "long",
        "signal_row_index": signal_idx,
        "entry_row_index": signal_idx + 1,
        "signal_time_utc": signal_row["open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_time_utc": entry_row["open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_open_price": entry_open,
        "entry_price_with_slippage": entry_open * (1.0 + SLIPPAGE_BPS / 10000.0),
        "slippage_bps": SLIPPAGE_BPS,
        "entry_rule": "next_bar_open_after_signal_close",
        "strategy_scope": "entry_only_low_detection",
        "lookahead": "NO",
        "online_selection_rule": "event_state_first_entry_then_cooldown",
        "event_open_row_index": event_open_idx,
        "event_age_bars": signal_idx - event_open_idx,
        "priority_score": event_score + trigger_score,
        "context_votes": event_votes,
        "trigger_votes": trigger_votes + ["NEXT_OPEN_ENTRY_ONLY"],
        "confirm_votes": [],
        "suppress_votes": [],
        "debug": {
            "event_score": event_score,
            "trigger_score": trigger_score,
            "low_zone": _low_zone(signal_row),
            "ret_6_pct": _value(signal_row, "ret_6_pct", 0.0),
            "ret_12_pct": _value(signal_row, "ret_12_pct", 0.0),
            "ret_24_pct": _value(signal_row, "ret_24_pct", 0.0),
            "rsi14": _value(signal_row, "rsi14", 0.0),
            "stoch_k14": _value(signal_row, "stoch_k14", 0.0),
            "mfi14": _value(signal_row, "mfi14", 0.0),
            "lower_wick_share": _value(signal_row, "lower_wick_share", 0.0),
            "close_pos_candle": _value(signal_row, "close_pos_candle", 0.0),
            "support_touch_count_60": _value(signal_row, "support_touch_count_60", 0.0),
            "ema20_slope_5_pct": _value(signal_row, "ema20_slope_5_pct", 0.0),
        },
    }


def _run_variant(rows: list[dict[str, Any]], manual_entries: list[Any], params: dict[str, Any]) -> dict[str, Any]:
    signals: list[dict[str, Any]] = []
    cooldown_until = -1
    event_open_idx: int | None = None
    event_votes: list[str] = []
    event_score = 0
    events_opened = 0
    events_expired = 0

    for signal_idx in range(60, len(rows) - 1):
        if signal_idx <= cooldown_until:
            continue

        row = rows[signal_idx]
        current_event_score, current_event_votes = _event_score(row, params)
        if event_open_idx is None and current_event_score >= int(params["event_min_score"]):
            event_open_idx = signal_idx
            event_votes = current_event_votes
            event_score = current_event_score
            events_opened += 1

        if event_open_idx is None:
            continue

        if signal_idx - event_open_idx > int(params["event_timeout_bars"]):
            events_expired += 1
            event_open_idx = None
            event_votes = []
            event_score = 0
            continue

        trigger_score, trigger_votes = _trigger_score(row, params)
        if trigger_score < int(params["trigger_min_score"]):
            continue

        signals.append(
            _build_signal(
                rows,
                signal_idx,
                params,
                event_open_idx,
                event_votes,
                trigger_votes,
                event_score,
                trigger_score,
            )
        )
        event_open_idx = None
        event_votes = []
        event_score = 0
        cooldown_until = signal_idx + int(params["cooldown_bars"])

    score = score_entries(manual_entries, [_to_trade(signal) for signal in signals])
    return {
        "family_id": str(params["family_id"]),
        "bucket": str(params["bucket"]),
        "description_ru": str(params["description_ru"]),
        "params": {key: value for key, value in params.items() if key != "description_ru"},
        "score": _score_summary(score),
        "hit_details": score["hit_details"],
        "missed_target_details": score["missed_target_details"],
        "false_entry_details": score["false_entry_details"][:200],
        "signals": signals,
        "events_opened": events_opened,
        "events_expired": events_expired,
        "selection_rule": "online_event_state_first_entry_then_cooldown",
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
        "# Visual Entry SWING_SUPPORT_RETEST_EVENT_V1",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "Контракт: ищем только входы у low/дна. Signal-свеча должна быть закрыта; вход LONG ставится на `open` следующей свечи; `lookahead=NO`; slippage `5 bps`; TP/SL, MFE/MAE и будущая доходность не используются.",
        "",
        "| rank | family | bucket | hits | miss | false | entries | precision | recall | f1 | events | expired |",
        "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, item in enumerate(payload["best_overall"], 1):
        score = item["score"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{:.4f}` | `{:.4f}` | `{:.4f}` | `{}` | `{}` |".format(
                rank,
                item["family_id"],
                item["bucket"],
                score["target_hits"],
                score["missed_targets"],
                score["false_entries"],
                score["entries_total"],
                score["precision"],
                score["recall"],
                score["f1_visual"],
                item.get("events_opened", 0),
                item.get("events_expired", 0),
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
            "Это entry-only diagnostic. Его задача - проверить, насколько правила входа у low совпадают с ручной разметкой. В ML ничего не передавать до ручного подтверждения PNG и отдельного `APPROVED_FOR_ML`.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_search(manual_entries_path: Path, out_dir: Path, *, render_top: int = 4) -> dict[str, Any]:
    manual_payload, manual_entries = load_manual_entries(manual_entries_path)
    _, rows = _prepare_rows(manual_entries_path)
    _enrich_quality_rows(rows)
    results = [_run_variant(rows, manual_entries, dict(params)) for params in EVENT_VARIANTS]
    results = [item for item in results if int(item["score"]["entries_total"]) > 0]
    results.sort(key=_sort_key, reverse=True)

    out_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[dict[str, str]] = []
    for rank, result in enumerate(results[:render_top], 1):
        label = f"ssre_{rank:02d}_{result['family_id'].lower()}"
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
        "strategy_scope": "entry_only_low_detection",
        "future_trade_outcome_used": False,
        "ml_transfer_allowed": False,
        "variants_total": len(EVENT_VARIANTS),
        "results_total": len(results),
        "best_overall": results,
        "rendered_overlays": rendered,
    }
    slug = _manual_slug(manual_payload)
    json_path = out_dir / f"visual_entry_swing_support_retest_event_{slug}.json"
    md_path = out_dir / f"visual_entry_swing_support_retest_event_{slug}_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run entry-only swing/support/retest visual diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/swing_support_retest_event")
    parser.add_argument("--render-top", type=int, default=4)
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
                        "bucket": item["bucket"],
                        "score": item["score"],
                        "events_opened": item.get("events_opened", 0),
                        "events_expired": item.get("events_expired", 0),
                    }
                    for item in payload["best_overall"][:5]
                ],
                "future_trade_outcome_used": payload["future_trade_outcome_used"],
                "ml_transfer_allowed": payload["ml_transfer_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

