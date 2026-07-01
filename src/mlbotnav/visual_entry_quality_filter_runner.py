from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.render_visual_entry_overlay import render_family_candidate_overlay
from mlbotnav.visual_entry_no_lookahead_candidates import _prepare_rows
from mlbotnav.visual_entry_score import TradeEntry, load_manual_entries, score_entries


def _value(row: dict[str, Any], key: str, default: float) -> float:
    value = row.get(key)
    if value is None:
        return default
    return float(value)


QUALITY_VARIANTS: list[dict[str, Any]] = [
    {
        "variant_id": "Q01_RECLAIM_SUPPORT_BALANCED",
        "local_low_bars": 5,
        "base_min_votes": 5,
        "quality_min_votes": 2,
        "cooldown_bars": 20,
        "wick_min": 0.35,
        "closepos_min": 0.55,
        "support_lowpos_max": 0.10,
        "support_dist_max_pct": 0.20,
        "support_touches_min": 2,
        "vol_z_min": 1.0,
        "dip_ret12_max": -0.30,
        "dip_ret24_max": -0.60,
        "osc_max": 45.0,
        "capitulation_votes_min": 2,
        "cluster_min_events": 2,
        "cluster_max_events": 6,
        "max_lower_low_streak": 3,
        "max_new_low_count_20": 6,
        "bad_slope_pct": -0.20,
    },
    {
        "variant_id": "Q02_DEEP_CAPITULATION_ABSORPTION",
        "local_low_bars": 5,
        "base_min_votes": 5,
        "quality_min_votes": 2,
        "cooldown_bars": 20,
        "wick_min": 0.25,
        "closepos_min": 0.45,
        "support_lowpos_max": 0.10,
        "support_dist_max_pct": 0.15,
        "support_touches_min": 1,
        "vol_z_min": 0.50,
        "dip_ret12_max": -0.50,
        "dip_ret24_max": -0.60,
        "osc_max": 35.0,
        "capitulation_votes_min": 2,
        "cluster_min_events": 2,
        "cluster_max_events": 8,
        "max_lower_low_streak": 3,
        "max_new_low_count_20": 8,
        "bad_slope_pct": -0.30,
    },
    {
        "variant_id": "Q03_STRICT_RECLAIM",
        "local_low_bars": 5,
        "base_min_votes": 5,
        "quality_min_votes": 2,
        "cooldown_bars": 20,
        "wick_min": 0.45,
        "closepos_min": 0.65,
        "support_lowpos_max": 0.20,
        "support_dist_max_pct": 0.35,
        "support_touches_min": 2,
        "vol_z_min": 1.50,
        "dip_ret12_max": -0.15,
        "dip_ret24_max": -0.30,
        "osc_max": 55.0,
        "capitulation_votes_min": 3,
        "cluster_min_events": 2,
        "cluster_max_events": 6,
        "max_lower_low_streak": 2,
        "max_new_low_count_20": 6,
        "bad_slope_pct": -0.15,
    },
    {
        "variant_id": "Q04_SUPPORT_CLUSTER",
        "local_low_bars": 10,
        "base_min_votes": 5,
        "quality_min_votes": 2,
        "cooldown_bars": 30,
        "wick_min": 0.25,
        "closepos_min": 0.55,
        "support_lowpos_max": 0.20,
        "support_dist_max_pct": 0.35,
        "support_touches_min": 3,
        "vol_z_min": 999.0,
        "dip_ret12_max": -0.15,
        "dip_ret24_max": -0.30,
        "osc_max": 55.0,
        "capitulation_votes_min": 2,
        "cluster_min_events": 3,
        "cluster_max_events": 8,
        "max_lower_low_streak": 3,
        "max_new_low_count_20": 8,
        "bad_slope_pct": -0.20,
    },
    {
        "variant_id": "Q05_LOW_NO_HARD_RECLAIM",
        "local_low_bars": 5,
        "base_min_votes": 6,
        "quality_min_votes": 1,
        "cooldown_bars": 20,
        "wick_min": 0.50,
        "closepos_min": 0.70,
        "support_lowpos_max": 0.05,
        "support_dist_max_pct": 0.15,
        "support_touches_min": 2,
        "vol_z_min": 1.0,
        "dip_ret12_max": -0.30,
        "dip_ret24_max": -0.60,
        "osc_max": 45.0,
        "capitulation_votes_min": 2,
        "cluster_min_events": 2,
        "cluster_max_events": 8,
        "max_lower_low_streak": 3,
        "max_new_low_count_20": 8,
        "bad_slope_pct": -0.25,
    },
    {
        "variant_id": "Q06_LONG_COOLDOWN_EVENT",
        "local_low_bars": 5,
        "base_min_votes": 5,
        "quality_min_votes": 1,
        "cooldown_bars": 45,
        "wick_min": 0.35,
        "closepos_min": 0.55,
        "support_lowpos_max": 0.10,
        "support_dist_max_pct": 0.20,
        "support_touches_min": 2,
        "vol_z_min": 1.0,
        "dip_ret12_max": -0.30,
        "dip_ret24_max": -0.60,
        "osc_max": 45.0,
        "capitulation_votes_min": 2,
        "cluster_min_events": 2,
        "cluster_max_events": 6,
        "max_lower_low_streak": 3,
        "max_new_low_count_20": 6,
        "bad_slope_pct": -0.20,
    },
    {
        "variant_id": "Q07_BROAD_EVENT_LOCAL10",
        "local_low_bars": 10,
        "base_min_votes": 6,
        "quality_min_votes": 1,
        "cooldown_bars": 45,
        "wick_min": 0.25,
        "closepos_min": 0.45,
        "support_lowpos_max": 0.10,
        "support_dist_max_pct": 0.35,
        "support_touches_min": 99,
        "vol_z_min": 1.0,
        "dip_ret12_max": -0.30,
        "dip_ret24_max": -0.60,
        "osc_max": 45.0,
        "capitulation_votes_min": 3,
        "cluster_min_events": 99,
        "cluster_max_events": 99,
        "max_lower_low_streak": 5,
        "max_new_low_count_20": 20,
        "bad_slope_pct": -1.0,
    },
    {
        "variant_id": "Q08_BROAD_EVENT_LOCAL10_STRICT_RANGE",
        "local_low_bars": 10,
        "base_min_votes": 6,
        "quality_min_votes": 1,
        "cooldown_bars": 45,
        "wick_min": 0.35,
        "closepos_min": 0.55,
        "support_lowpos_max": 0.05,
        "support_dist_max_pct": 0.20,
        "support_touches_min": 99,
        "vol_z_min": 1.0,
        "dip_ret12_max": -0.30,
        "dip_ret24_max": -0.60,
        "osc_max": 45.0,
        "capitulation_votes_min": 3,
        "cluster_min_events": 99,
        "cluster_max_events": 99,
        "max_lower_low_streak": 5,
        "max_new_low_count_20": 20,
        "bad_slope_pct": -1.0,
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


def _enrich_quality_rows(rows: list[dict[str, Any]]) -> None:
    for idx, row in enumerate(rows):
        start20 = max(0, idx - 19)
        new_low_count = 0
        support_touches = 0
        current_low = float(row["low"])
        for probe_idx in range(start20, idx + 1):
            probe = rows[probe_idx]
            low_window = rows[max(0, probe_idx - 4) : probe_idx + 1]
            if float(probe["low"]) <= min(float(item["low"]) for item in low_window) + 1e-12:
                new_low_count += 1
        start60 = max(0, idx - 59)
        for probe in rows[start60 : idx + 1]:
            if current_low > 0:
                distance_pct = abs(float(probe["low"]) - current_low) / current_low * 100.0
                if distance_pct <= 0.10:
                    support_touches += 1
        streak = 0
        for probe_idx in range(idx, max(0, idx - 5), -1):
            if float(rows[probe_idx]["low"]) < float(rows[probe_idx - 1]["low"]):
                streak += 1
            else:
                break
        row["new_low_count_20"] = new_low_count
        row["support_touch_count_60"] = support_touches
        row["lower_low_streak_5"] = streak
        row["prev_close"] = float(rows[idx - 1]["close"]) if idx > 0 else float(row["close"])


def _base_votes(signal: dict[str, Any]) -> list[str]:
    votes: list[str] = []
    low_pos = min(_value(signal, "range_pos_60", 1.0), _value(signal, "low_range_pos_60", 1.0))
    if low_pos <= 0.35:
        votes.append("RANGE_LOW_60")
    if _value(signal, "rsi14", 999.0) <= 55.0:
        votes.append("RSI_COLD")
    if _value(signal, "stoch_k14", 999.0) <= 75.0:
        votes.append("STOCH_LOW")
    if _value(signal, "mfi14", 999.0) <= 65.0:
        votes.append("MFI_COLD")
    if _value(signal, "ema_gap_pct", 999.0) <= 0.05:
        votes.append("EMA_NOT_HOT")
    if _value(signal, "ema20_slope_5_pct", 999.0) <= 0.05:
        votes.append("EMA_SLOPE_NOT_UP")
    if _value(signal, "ret_12_pct", 999.0) <= 0.10 or _value(signal, "ret_24_pct", 999.0) <= -0.10:
        votes.append("DIP_RET")
    return votes


def _quality_votes(signal: dict[str, Any], params: dict[str, Any]) -> list[str]:
    votes: list[str] = []
    if _value(signal, "lower_wick_share", 0.0) >= float(params["wick_min"]) or _value(
        signal, "close_pos_candle", 0.0
    ) >= float(params["closepos_min"]):
        votes.append("RECLAIM_QUALITY")
    if (
        _value(signal, "low_range_pos_60", 1.0) <= float(params["support_lowpos_max"])
        or _value(signal, "dist_from_low_60_pct", 999.0) <= float(params["support_dist_max_pct"])
        or int(signal.get("support_touch_count_60", 0)) >= int(params["support_touches_min"])
    ):
        votes.append("SUPPORT_CONFLUENCE")
    capitulation_votes = 0
    if _value(signal, "vol_z20", -999.0) >= float(params["vol_z_min"]):
        capitulation_votes += 1
    if _value(signal, "ret_12_pct", 999.0) <= float(params["dip_ret12_max"]) or _value(
        signal, "ret_24_pct", 999.0
    ) <= float(params["dip_ret24_max"]):
        capitulation_votes += 1
    if min(_value(signal, "rsi14", 999.0), _value(signal, "stoch_k14", 999.0), _value(signal, "mfi14", 999.0)) <= float(
        params["osc_max"]
    ):
        capitulation_votes += 1
    if _value(signal, "lower_wick_share", 0.0) >= 0.35 or _value(signal, "close_pos_candle", 0.0) >= 0.55:
        capitulation_votes += 1
    if capitulation_votes >= int(params["capitulation_votes_min"]):
        votes.append("CAPITULATION_ABSORPTION")
    new_low_count = int(signal.get("new_low_count_20", 0))
    if int(params["cluster_min_events"]) <= new_low_count <= int(params["cluster_max_events"]):
        votes.append("BOTTOM_EVENT_CLUSTER")
    return votes


def _is_suppressed(signal: dict[str, Any], params: dict[str, Any]) -> bool:
    if int(signal.get("lower_low_streak_5", 0)) > int(params["max_lower_low_streak"]):
        return True
    if int(signal.get("new_low_count_20", 0)) > int(params["max_new_low_count_20"]):
        return True
    if (
        _value(signal, "ema20_slope_5_pct", 0.0) <= float(params["bad_slope_pct"])
        and _value(signal, "lower_wick_share", 0.0) < 0.35
        and _value(signal, "vol_z20", -999.0) < float(params["vol_z_min"])
    ):
        return True
    return False


def _run_variant(rows: list[dict[str, Any]], manual_entries: list[Any], params: dict[str, Any]) -> dict[str, Any]:
    trades: list[TradeEntry] = []
    signals: list[dict[str, Any]] = []
    last_entry_idx = -10_000
    family_id = str(params["variant_id"])
    for signal_idx in range(60, len(rows) - 1):
        entry_idx = signal_idx + 1
        if entry_idx - last_entry_idx < int(params["cooldown_bars"]):
            continue
        signal = rows[signal_idx]
        if not bool(signal.get(f"local_low_{int(params['local_low_bars'])}")):
            continue
        base = _base_votes(signal)
        if len(base) < int(params["base_min_votes"]):
            continue
        quality = _quality_votes(signal, params)
        if len(quality) < int(params["quality_min_votes"]):
            continue
        if _is_suppressed(signal, params):
            continue
        entry = rows[entry_idx]
        last_entry_idx = entry_idx
        trades.append(
            TradeEntry(
                row_index=entry_idx,
                side="long",
                entry_time=entry["open_time_utc"],
                exit_time_raw="",
                net_return=0.0,
                mae_pct=None,
                mfe_pct=None,
            )
        )
        entry_open = float(entry["open"])
        signals.append(
            {
                "family_id": family_id,
                "side": "long",
                "signal_row_index": int(signal_idx),
                "entry_row_index": int(entry_idx),
                "signal_time_utc": signal["open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_time_utc": entry["open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_open_price": entry_open,
                "entry_price_with_slippage": entry_open * 1.0005,
                "slippage_bps": 5.0,
                "context_votes": base,
                "trigger_votes": quality,
                "confirm_votes": [],
                "lookahead": "NO",
                "entry_rule": "next_bar_open_after_signal_close",
                "debug": {
                    "new_low_count_20": int(signal.get("new_low_count_20", 0)),
                    "support_touch_count_60": int(signal.get("support_touch_count_60", 0)),
                    "lower_low_streak_5": int(signal.get("lower_low_streak_5", 0)),
                },
            }
        )
    score = score_entries(manual_entries, trades)
    return {
        "family_id": family_id,
        "description_ru": "Micro-bottom с фильтрами качества и подавлением ложных входов без lookahead.",
        "params": params,
        "score": _score_summary(score),
        "hit_details": score["hit_details"],
        "missed_target_details": score["missed_target_details"],
        "false_entry_details": score["false_entry_details"][:200],
        "signals": signals,
    }


def _combine_results(results: list[dict[str, Any]], manual_entries: list[Any], family_ids: tuple[str, ...], combo_id: str) -> dict[str, Any]:
    by_time: dict[str, dict[str, Any]] = {}
    for result in results:
        if result["family_id"] not in family_ids:
            continue
        for signal in result.get("signals", []):
            by_time.setdefault(str(signal["entry_time_utc"]), dict(signal))
    signals = [by_time[key] for key in sorted(by_time)]
    trades: list[TradeEntry] = []
    for signal in signals:
        entry_time = datetime.fromisoformat(str(signal["entry_time_utc"]).replace("Z", "+00:00"))
        trades.append(
            TradeEntry(
                row_index=int(signal["entry_row_index"]),
                side="long",
                entry_time=entry_time,
                exit_time_raw="",
                net_return=0.0,
                mae_pct=None,
                mfe_pct=None,
            )
        )
        signal["family_id"] = combo_id
        signal["trigger_votes"] = list(signal.get("trigger_votes", [])) + ["ENSEMBLE_UNION"]
    score = score_entries(manual_entries, trades)
    return {
        "family_id": combo_id,
        "description_ru": "Ансамбль quality-вариантов без lookahead.",
        "params": {"ensemble_family_ids": list(family_ids), "dedupe": "entry_time_utc"},
        "score": _score_summary(score),
        "hit_details": score["hit_details"],
        "missed_target_details": score["missed_target_details"],
        "false_entry_details": score["false_entry_details"][:200],
        "signals": signals,
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


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Visual Entry quality filter runner",
        "",
        "Статус: `DEV_QUALITY_FILTER_DIAGNOSTIC_NO_ML`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "Контракт: closed signal candle -> next open, `lookahead=NO`, slippage `5 bps`.",
        "",
        "| rank | variant | hits | miss | false | entries | precision | recall | f1 |",
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
            "Это DEV diagnostic-only. В ML ничего не передавать без validation/holdout и ручного `APPROVED_FOR_ML`.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_search(manual_entries_path: Path, out_dir: Path, *, render_top: int = 6) -> dict[str, Any]:
    _, manual_entries = load_manual_entries(manual_entries_path)
    _, rows = _prepare_rows(manual_entries_path)
    _enrich_quality_rows(rows)
    all_results = [_run_variant(rows, manual_entries, dict(params)) for params in QUALITY_VARIANTS]
    ensemble_results = [
        _combine_results(
            all_results,
            manual_entries,
            ("Q07_BROAD_EVENT_LOCAL10", "Q01_RECLAIM_SUPPORT_BALANCED"),
            "Q09_ENSEMBLE_Q07_Q01",
        ),
        _combine_results(
            all_results,
            manual_entries,
            ("Q07_BROAD_EVENT_LOCAL10", "Q03_STRICT_RECLAIM"),
            "Q10_ENSEMBLE_Q07_Q03",
        ),
    ]
    results = all_results + ensemble_results
    results = [item for item in results if int(item["score"]["target_hits"]) > 0]
    results.sort(key=_sort_key, reverse=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[dict[str, str]] = []
    for rank, result in enumerate(results[:render_top], 1):
        label = f"quality_{rank:02d}_{result['family_id'].lower()}"
        png_path = render_family_candidate_overlay(
            manual_entries_path=manual_entries_path,
            result=result,
            out_dir=out_dir,
            label=label,
            slippage_bps=5.0,
        )
        rendered.append({"rank": str(rank), "family_id": result["family_id"], "visual_png": str(png_path)})
    payload = {
        "schema_version": 1,
        "status": "DEV_QUALITY_FILTER_DIAGNOSTIC_NO_ML",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "manual_entries": str(manual_entries_path),
        "variants_total": len(QUALITY_VARIANTS),
        "results_total": len(results),
        "best_overall": results,
        "rendered_overlays": rendered,
        "ml_transfer_allowed": False,
    }
    json_path = out_dir / "visual_entry_quality_filter_20260512_DEV.json"
    md_path = out_dir / "visual_entry_quality_filter_20260512_DEV_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run visual-entry quality/suppression diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/quality_filter")
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
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
