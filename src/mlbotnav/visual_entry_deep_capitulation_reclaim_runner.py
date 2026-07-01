from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from mlbotnav.render_visual_entry_overlay import render_family_candidate_overlay
from mlbotnav.visual_entry_early_flush_runner import (
    EARLY_VARIANTS,
    _combine_signals,
    _quality_q09,
    _run_variant as _run_early_variant,
)
from mlbotnav.visual_entry_no_lookahead_candidates import _prepare_rows
from mlbotnav.visual_entry_quality_filter_runner import _enrich_quality_rows
from mlbotnav.visual_entry_score import TradeEntry, load_manual_entries, score_entries


def _value(row: dict[str, Any], key: str, default: float) -> float:
    value = row.get(key)
    if value is None:
        return default
    return float(value)


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


def _low_zone(row: dict[str, Any]) -> float:
    return min(_value(row, "range_pos_60", 1.0), _value(row, "low_range_pos_60", 1.0))


def _deep_capitulation_absorption(rows: list[dict[str, Any]], signal_idx: int) -> tuple[bool, list[str]]:
    row = rows[signal_idx]
    votes: list[str] = []
    if bool(row.get("local_low_20")) or bool(row.get("local_low_60")):
        votes.append("LOCAL_DEEP_LOW")
    if _low_zone(row) <= 0.13:
        votes.append("LOW_ZONE_13")
    if _value(row, "ret_6_pct", 999.0) <= -0.35 or _value(row, "ret_12_pct", 999.0) <= -0.55:
        votes.append("FLUSH_RET")
    if (
        _value(row, "rsi14", 999.0) <= 25.0
        and _value(row, "stoch_k14", 999.0) <= 25.0
        and _value(row, "mfi14", 999.0) <= 25.0
    ):
        votes.append("TRIPLE_COLD_25")
    if _value(row, "lower_wick_share", 0.0) >= 0.18 or _value(row, "close_pos_candle", 0.0) >= 0.18:
        votes.append("ABSORPTION_RECLAIM")
    if _value(row, "ema_gap_pct", 999.0) <= 0.0 and _value(row, "ema20_slope_5_pct", 999.0) <= -0.05:
        votes.append("EMA_DOWN")
    required = {
        "LOCAL_DEEP_LOW",
        "LOW_ZONE_13",
        "FLUSH_RET",
        "TRIPLE_COLD_25",
        "ABSORPTION_RECLAIM",
        "EMA_DOWN",
    }
    return required.issubset(votes), votes


def _terminal_exhaustion_stall(rows: list[dict[str, Any]], signal_idx: int) -> tuple[bool, list[str]]:
    row = rows[signal_idx]
    votes: list[str] = []
    if bool(row.get("local_low_20")) or bool(row.get("local_low_60")):
        votes.append("LOCAL_DEEP_LOW")
    if _low_zone(row) <= 0.07:
        votes.append("ULTRA_LOW_ZONE")
    if _value(row, "ret_12_pct", 999.0) <= -1.05 or _value(row, "ret_24_pct", 999.0) <= -0.85:
        votes.append("MAX_FLUSH_RET")
    if _value(row, "mfi14", 999.0) <= 2.0 and _value(row, "stoch_k14", 999.0) <= 8.0:
        votes.append("EXTREME_MFI_STOCH")
    close_pos = _value(row, "close_pos_candle", 0.0)
    if 0.15 <= close_pos <= 0.25 and _value(row, "lower_wick_share", 0.0) >= 0.15:
        votes.append("TINY_RECLAIM")
    if abs(_value(row, "body_pct", 0.0)) <= 0.07:
        votes.append("BODY_STALLS")
    if _value(row, "vol_z20", 999.0) <= 1.0:
        votes.append("VOL_EXHAUSTED")
    return len(votes) >= 6, votes


def _recent_deep_capitulation_index(rows: list[dict[str, Any]], signal_idx: int, lookback: int) -> int | None:
    start = max(60, signal_idx - lookback)
    last: int | None = None
    for probe_idx in range(start, signal_idx):
        probe = rows[probe_idx]
        if not bool(probe.get("local_low_20")):
            continue
        if _low_zone(probe) > 0.07:
            continue
        if _value(probe, "ret_12_pct", 999.0) <= -0.80 or _value(probe, "mfi14", 999.0) <= 5.0:
            last = probe_idx
    return last


def _late_retest_probe(rows: list[dict[str, Any]], signal_idx: int) -> tuple[bool, list[str]]:
    row = rows[signal_idx]
    votes: list[str] = []
    recent = _recent_deep_capitulation_index(rows, signal_idx, 120)
    if recent is not None and 8 <= signal_idx - recent <= 120:
        votes.append(f"RECENT_DEEP_CAPITULATION_{signal_idx - recent}B")
    if 0.20 <= _low_zone(row) <= 0.42 or _value(row, "dist_from_low_60_pct", 999.0) <= 0.35:
        votes.append("NEAR_LOW_RETEST")
    if 28.0 <= _value(row, "mfi14", 999.0) <= 38.0 and _value(row, "rsi14", 999.0) <= 50.0:
        votes.append("COLDISH_RETEST")
    if _value(row, "ema_gap_pct", 999.0) <= -0.07 and _value(row, "ema20_slope_5_pct", 999.0) <= 0.02:
        votes.append("EMA_WEAK_FLAT")
    if _value(row, "ret_24_pct", 999.0) <= -0.20 and _value(row, "ret_6_pct", 999.0) >= -0.05:
        votes.append("POST_FLUSH_RETEST")
    if _value(row, "close_pos_candle", 1.0) <= 0.10 and _value(row, "lower_wick_share", 1.0) <= 0.10:
        votes.append("CLOSE_LOW_PROBE")
    return len(votes) >= 6, votes


DEEP_VARIANTS: list[dict[str, Any]] = [
    {
        "variant_id": "D01_DEEP_CAPITULATION_ABSORB_CD20",
        "cooldown_bars": 20,
        "checker": _deep_capitulation_absorption,
        "description_ru": "Глубокая капитуляция у low-уровня с холодными RSI/Stoch/MFI и признаком absorption/reclaim; цель DEV - 12:33.",
    },
    {
        "variant_id": "D02_TERMINAL_EXHAUSTION_STALL_CD20",
        "cooldown_bars": 20,
        "checker": _terminal_exhaustion_stall,
        "description_ru": "Финальная свеча сброса: очень низкая зона, крайний MFI/Stoch, маленькое тело и иссякший объем; цель DEV - 15:26.",
    },
    {
        "variant_id": "D03_LATE_RETEST_PROBE_CD15",
        "cooldown_bars": 15,
        "checker": _late_retest_probe,
        "description_ru": "Поздний ретест после глубокой капитуляции: цена рядом с low-зоной, EMA слабая, свеча закрыта у low; цель DEV - 17:00.",
    },
]


def _run_deep_variant(rows: list[dict[str, Any]], manual_entries: list[Any], params: dict[str, Any]) -> dict[str, Any]:
    checker: Callable[[list[dict[str, Any]], int], tuple[bool, list[str]]] = params["checker"]
    family_id = str(params["variant_id"])
    trades: list[TradeEntry] = []
    signals: list[dict[str, Any]] = []
    last_signal_idx = -10_000
    for signal_idx in range(60, len(rows) - 1):
        if signal_idx - last_signal_idx < int(params["cooldown_bars"]):
            continue
        ok, votes = checker(rows, signal_idx)
        if not ok:
            continue
        signal = rows[signal_idx]
        entry_idx = signal_idx + 1
        entry = rows[entry_idx]
        last_signal_idx = signal_idx
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
                "context_votes": votes,
                "trigger_votes": [family_id],
                "confirm_votes": [],
                "lookahead": "NO",
                "entry_rule": "next_bar_open_after_signal_close",
                "debug": {
                    "range_low_zone": _low_zone(signal),
                    "ret_6_pct": _value(signal, "ret_6_pct", 0.0),
                    "ret_12_pct": _value(signal, "ret_12_pct", 0.0),
                    "ret_24_pct": _value(signal, "ret_24_pct", 0.0),
                    "rsi14": _value(signal, "rsi14", 0.0),
                    "stoch_k14": _value(signal, "stoch_k14", 0.0),
                    "mfi14": _value(signal, "mfi14", 0.0),
                    "close_pos_candle": _value(signal, "close_pos_candle", 0.0),
                    "lower_wick_share": _value(signal, "lower_wick_share", 0.0),
                },
            }
        )
    score = score_entries(manual_entries, trades)
    public_params = {key: value for key, value in params.items() if key != "checker"}
    return {
        "family_id": family_id,
        "description_ru": str(params["description_ru"]),
        "params": public_params,
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


def _manual_slug(manual_payload: dict[str, Any]) -> str:
    source = (manual_payload.get("source_images") or [{}])[0]
    date_utc = str(source.get("date_utc") or "unknown").replace("-", "")
    role = str(manual_payload.get("dataset_role") or "DEV").upper()
    safe_role = "".join(ch if ch.isalnum() else "_" for ch in role).strip("_") or "DEV"
    return f"{date_utc}_{safe_role}"


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Visual Entry DEEP_CAPITULATION_RECLAIM runner",
        "",
        "Статус: `DEV_DEEP_CAPITULATION_RECLAIM_DIAGNOSTIC_NO_ML`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "Контракт: закрытая signal-свеча и прошлая история -> вход LONG на `open` следующей свечи; `lookahead=NO`; slippage `5 bps`.",
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
            "Это DEV diagnostic-only. Слой полезен как разбор пропущенных глубоких/поздних входов, но шум ансамблей еще слишком высокий для ML. В ML ничего не передавать без validation/holdout и отдельного ручного `APPROVED_FOR_ML`.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_search(manual_entries_path: Path, out_dir: Path, *, render_top: int = 6) -> dict[str, Any]:
    manual_payload, manual_entries = load_manual_entries(manual_entries_path)
    _, rows = _prepare_rows(manual_entries_path)
    _enrich_quality_rows(rows)

    early_results = [_run_early_variant(rows, manual_entries, dict(params)) for params in EARLY_VARIANTS]
    q09 = _quality_q09(rows, manual_entries)
    eq01 = _combine_signals(
        early_results + [q09],
        manual_entries,
        (
            "Q09_QUALITY_BASELINE",
            "E01_SEVERE_FLUSH_LOCKOUT20",
            "E02_SOFT_SUPPORT_PULLBACK_CD45",
        ),
        "EQ01_Q09_SEVERE_SOFT45",
        "Текущий лучший early/quality baseline, включен как база для cumulative ensemble.",
    )
    eq02 = _combine_signals(
        early_results + [q09],
        manual_entries,
        (
            "Q09_QUALITY_BASELINE",
            "E01_SEVERE_FLUSH_LOCKOUT20",
            "E03_SOFT_SUPPORT_PULLBACK_CD30",
        ),
        "EQ02_Q09_SEVERE_SOFT30",
        "Альтернативный baseline, который ловит 08:26, но теряет 07:16.",
    )
    eq03 = _combine_signals(
        early_results + [q09],
        manual_entries,
        (
            "Q09_QUALITY_BASELINE",
            "E01_SEVERE_FLUSH_LOCKOUT20",
            "E02_SOFT_SUPPORT_PULLBACK_CD45",
            "E05_NO_WICK_LOW_CLOSE_CD15",
        ),
        "EQ03_Q09_SEVERE_SOFT45_NOWICK",
        "High-recall baseline с рискованным no-wick каналом.",
    )
    deep_results = [_run_deep_variant(rows, manual_entries, dict(params)) for params in DEEP_VARIANTS]
    all_results = [q09, eq01, eq02, eq03] + deep_results
    all_results.extend(
        [
            _combine_signals(
                all_results,
                manual_entries,
                (
                    "EQ01_Q09_SEVERE_SOFT45",
                    "D01_DEEP_CAPITULATION_ABSORB_CD20",
                    "D02_TERMINAL_EXHAUSTION_STALL_CD20",
                    "D03_LATE_RETEST_PROBE_CD15",
                ),
                "DQ01_EQ01_PLUS_DEEP_RECLAIM",
                "Рабочий cumulative ensemble: early/quality baseline плюс три deep/retest подсемейства.",
            ),
            _combine_signals(
                all_results,
                manual_entries,
                (
                    "EQ02_Q09_SEVERE_SOFT30",
                    "D01_DEEP_CAPITULATION_ABSORB_CD20",
                    "D02_TERMINAL_EXHAUSTION_STALL_CD20",
                    "D03_LATE_RETEST_PROBE_CD15",
                ),
                "DQ02_EQ02_PLUS_DEEP_RECLAIM",
                "Альтернативный cumulative ensemble: добирает 08:26 вместо 07:16.",
            ),
            _combine_signals(
                all_results,
                manual_entries,
                (
                    "EQ03_Q09_SEVERE_SOFT45_NOWICK",
                    "D01_DEEP_CAPITULATION_ABSORB_CD20",
                    "D02_TERMINAL_EXHAUSTION_STALL_CD20",
                    "D03_LATE_RETEST_PROBE_CD15",
                ),
                "DQ03_EQ03_HIGH_RECALL_PLUS_DEEP",
                "High-recall diagnostic: проверяет, можно ли закрыть все DEV-стрелки ценой большого шума.",
            ),
        ]
    )
    results = [item for item in all_results if int(item["score"]["target_hits"]) > 0]
    results.sort(key=_sort_key, reverse=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[dict[str, str]] = []
    for rank, result in enumerate(results[:render_top], 1):
        label = f"deep_reclaim_{rank:02d}_{result['family_id'].lower()}"
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
        "status": "DEV_DEEP_CAPITULATION_RECLAIM_DIAGNOSTIC_NO_ML",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "manual_entries": str(manual_entries_path),
        "variants_total": len(DEEP_VARIANTS),
        "results_total": len(results),
        "best_overall": results,
        "rendered_overlays": rendered,
        "ml_transfer_allowed": False,
    }
    slug = _manual_slug(manual_payload)
    json_path = out_dir / f"visual_entry_deep_capitulation_reclaim_{slug}.json"
    md_path = out_dir / f"visual_entry_deep_capitulation_reclaim_{slug}_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run visual-entry deep capitulation/reclaim diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/deep_capitulation_reclaim")
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
