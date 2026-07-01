from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from mlbotnav.render_visual_entry_overlay import render_family_candidate_overlay
from mlbotnav.visual_entry_no_lookahead_candidates import _prepare_rows
from mlbotnav.visual_entry_quality_filter_runner import (
    QUALITY_VARIANTS,
    _combine_results as _combine_quality_results,
    _enrich_quality_rows,
    _run_variant as _run_quality_variant,
)
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


def _severe_flush(row: dict[str, Any]) -> tuple[bool, list[str]]:
    votes: list[str] = []
    if bool(row.get("local_low_20")) or bool(row.get("local_low_60")):
        votes.append("LOCAL_DEEP_LOW")
    if _low_zone(row) <= 0.10:
        votes.append("DEEP_RANGE_ZONE")
    if _value(row, "ret_12_pct", 999.0) <= -0.80 or _value(row, "ret_24_pct", 999.0) <= -0.90:
        votes.append("SEVERE_FLUSH_RET")
    if (
        _value(row, "rsi14", 999.0) <= 20.0
        and _value(row, "stoch_k14", 999.0) <= 25.0
        and _value(row, "mfi14", 999.0) <= 25.0
    ):
        votes.append("TRIPLE_OSC_COLD")
    if (
        _value(row, "vol_z20", -999.0) >= 0.50
        or _value(row, "lower_wick_share", 0.0) >= 0.35
        or _value(row, "close_pos_candle", 0.0) >= 0.35
    ):
        votes.append("ABSORPTION_HINT")
    if _value(row, "ema20_slope_5_pct", 999.0) <= -0.08:
        votes.append("EMA20_SLOPE_DOWN")
    required = {"LOCAL_DEEP_LOW", "SEVERE_FLUSH_RET", "TRIPLE_OSC_COLD"}
    return required.issubset(votes) and len(votes) >= 5, votes


def _soft_support_pullback(row: dict[str, Any]) -> tuple[bool, list[str]]:
    votes: list[str] = []
    if bool(row.get("local_low_5")):
        votes.append("LOCAL_LOW_5")
    if _low_zone(row) <= 0.35:
        votes.append("LOW_ZONE_35")
    if _value(row, "mfi14", 999.0) <= 30.0:
        votes.append("MFI_COLD_30")
    if _value(row, "ret_24_pct", 999.0) <= -0.25 or _value(row, "ret_3_pct", 999.0) <= -0.15:
        votes.append("RECENT_DIP")
    if _value(row, "ema_gap_pct", 999.0) <= 0.0 or _value(row, "ema20_slope_5_pct", 999.0) <= 0.02:
        votes.append("EMA_WEAK")
    if _value(row, "rsi14", 999.0) <= 55.0 and _value(row, "stoch_k14", 999.0) <= 75.0:
        votes.append("OSC_NOT_HOT")
    return "LOCAL_LOW_5" in votes and len(votes) >= 5, votes


def _broad_early_reversal(row: dict[str, Any]) -> tuple[bool, list[str]]:
    votes: list[str] = []
    if bool(row.get("local_low_5")):
        votes.append("LOCAL_LOW_5")
    if _low_zone(row) <= 0.45:
        votes.append("LOW_ZONE_45")
    if _value(row, "mfi14", 999.0) <= 25.0:
        votes.append("MFI_COLD_25")
    if _value(row, "stoch_k14", 999.0) <= 80.0:
        votes.append("STOCH_NOT_HOT")
    if _value(row, "rsi14", 999.0) <= 60.0:
        votes.append("RSI_NOT_HOT")
    if _value(row, "ema_gap_pct", 999.0) <= 0.05:
        votes.append("EMA_NOT_HOT")
    if _value(row, "ret_3_pct", 999.0) <= -0.05 or _value(row, "ret_24_pct", 999.0) <= -0.15:
        votes.append("PULLBACK_RET")
    return "LOCAL_LOW_5" in votes and len(votes) >= 6, votes


def _no_wick_low_close(row: dict[str, Any]) -> tuple[bool, list[str]]:
    votes: list[str] = []
    if bool(row.get("local_low_5")):
        votes.append("LOCAL_LOW_5")
    if _low_zone(row) <= 0.28:
        votes.append("LOW_ZONE_28")
    if _value(row, "mfi14", 999.0) <= 32.0:
        votes.append("MFI_COLD_32")
    if _value(row, "ret_24_pct", 999.0) <= -0.25 or _value(row, "ret_3_pct", 999.0) <= -0.12:
        votes.append("PULLBACK_RET")
    if _value(row, "ema_gap_pct", 999.0) <= 0.0 or _value(row, "ema20_slope_5_pct", 999.0) <= 0.02:
        votes.append("EMA_WEAK")
    if _value(row, "close_pos_candle", 0.0) <= 0.25 and _value(row, "lower_wick_share", 0.0) <= 0.15:
        votes.append("NO_RECLAIM_CLOSE_LOW")
    if _value(row, "rsi14", 999.0) <= 50.0 and _value(row, "stoch_k14", 999.0) <= 55.0:
        votes.append("OSC_COLDISH")
    required = {"LOCAL_LOW_5", "NO_RECLAIM_CLOSE_LOW"}
    return required.issubset(votes) and len(votes) >= 6, votes


EARLY_VARIANTS: list[dict[str, Any]] = [
    {
        "variant_id": "E01_SEVERE_FLUSH_LOCKOUT20",
        "cooldown_bars": 20,
        "checker": _severe_flush,
        "description_ru": "Жесткий сброс у локального дна: глубокая зона, сильный минус, холодные RSI/Stoch/MFI, затем вход на следующий open.",
    },
    {
        "variant_id": "E02_SOFT_SUPPORT_PULLBACK_CD45",
        "cooldown_bars": 45,
        "checker": _soft_support_pullback,
        "description_ru": "Мягкий откат к нижней зоне с холодным MFI и слабой EMA, длинный cooldown против частого шума.",
    },
    {
        "variant_id": "E03_SOFT_SUPPORT_PULLBACK_CD30",
        "cooldown_bars": 30,
        "checker": _soft_support_pullback,
        "description_ru": "Та же мягкая структура, но с меньшим cooldown для проверки пропущенных ранних входов.",
    },
    {
        "variant_id": "E04_BROAD_EARLY_PULLBACK_CD20",
        "cooldown_bars": 20,
        "checker": _broad_early_reversal,
        "description_ru": "Более широкий ранний разворот: useful для поиска формы, но обычно шумнее.",
    },
    {
        "variant_id": "E05_NO_WICK_LOW_CLOSE_CD15",
        "cooldown_bars": 15,
        "checker": _no_wick_low_close,
        "description_ru": "Свеча закрылась у low без фитиля, но в нижней зоне и с холодным MFI: отдельная проверка для 08:26.",
    },
]


def _run_variant(rows: list[dict[str, Any]], manual_entries: list[Any], params: dict[str, Any]) -> dict[str, Any]:
    checker: Callable[[dict[str, Any]], tuple[bool, list[str]]] = params["checker"]
    family_id = str(params["variant_id"])
    trades: list[TradeEntry] = []
    signals: list[dict[str, Any]] = []
    last_signal_idx = -10_000
    for signal_idx in range(60, len(rows) - 1):
        if signal_idx - last_signal_idx < int(params["cooldown_bars"]):
            continue
        signal = rows[signal_idx]
        ok, votes = checker(signal)
        if not ok:
            continue
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
                    "ret_3_pct": _value(signal, "ret_3_pct", 0.0),
                    "ret_12_pct": _value(signal, "ret_12_pct", 0.0),
                    "ret_24_pct": _value(signal, "ret_24_pct", 0.0),
                    "rsi14": _value(signal, "rsi14", 0.0),
                    "stoch_k14": _value(signal, "stoch_k14", 0.0),
                    "mfi14": _value(signal, "mfi14", 0.0),
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


def _combine_signals(
    results: list[dict[str, Any]],
    manual_entries: list[Any],
    family_ids: tuple[str, ...],
    combo_id: str,
    description_ru: str,
) -> dict[str, Any]:
    by_time: dict[str, dict[str, Any]] = {}
    for result in results:
        if result["family_id"] not in family_ids:
            continue
        for signal in result.get("signals", []):
            copy = dict(signal)
            copy["family_id"] = combo_id
            copy["trigger_votes"] = list(copy.get("trigger_votes", [])) + ["ENSEMBLE_UNION"]
            by_time.setdefault(str(copy["entry_time_utc"]), copy)
    signals = [by_time[key] for key in sorted(by_time)]
    trades = [
        TradeEntry(
            row_index=int(signal["entry_row_index"]),
            side="long",
            entry_time=datetime.fromisoformat(str(signal["entry_time_utc"]).replace("Z", "+00:00")),
            exit_time_raw="",
            net_return=0.0,
            mae_pct=None,
            mfe_pct=None,
        )
        for signal in signals
    ]
    score = score_entries(manual_entries, trades)
    return {
        "family_id": combo_id,
        "description_ru": description_ru,
        "params": {"ensemble_family_ids": list(family_ids), "dedupe": "entry_time_utc"},
        "score": _score_summary(score),
        "hit_details": score["hit_details"],
        "missed_target_details": score["missed_target_details"],
        "false_entry_details": score["false_entry_details"][:200],
        "signals": signals,
    }


def _quality_q09(rows: list[dict[str, Any]], manual_entries: list[Any]) -> dict[str, Any]:
    quality_results = [_run_quality_variant(rows, manual_entries, dict(params)) for params in QUALITY_VARIANTS]
    q09 = _combine_quality_results(
        quality_results,
        manual_entries,
        ("Q07_BROAD_EVENT_LOCAL10", "Q01_RECLAIM_SUPPORT_BALANCED"),
        "Q09_QUALITY_BASELINE",
    )
    q09["description_ru"] = "Предыдущий лучший quality/suppression baseline, включен только для сравнения и ensemble."
    return q09


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
        "# Visual Entry EARLY_FLUSH_REVERSAL runner",
        "",
        "Статус: `DEV_EARLY_FLUSH_REVERSAL_DIAGNOSTIC_NO_ML`.",
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
            "Это DEV diagnostic-only. Даже лучший ensemble пока шумный, поэтому в ML ничего не передавать. Полезность слоя: он показывает, какие ранние дна можно добавить к текущему quality baseline, не нарушая правило next-open/no-lookahead.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_search(manual_entries_path: Path, out_dir: Path, *, render_top: int = 6) -> dict[str, Any]:
    _, manual_entries = load_manual_entries(manual_entries_path)
    _, rows = _prepare_rows(manual_entries_path)
    _enrich_quality_rows(rows)
    early_results = [_run_variant(rows, manual_entries, dict(params)) for params in EARLY_VARIANTS]
    q09 = _quality_q09(rows, manual_entries)
    all_results = early_results + [q09]
    all_results.extend(
        [
            _combine_signals(
                all_results,
                manual_entries,
                (
                    "Q09_QUALITY_BASELINE",
                    "E01_SEVERE_FLUSH_LOCKOUT20",
                    "E02_SOFT_SUPPORT_PULLBACK_CD45",
                ),
                "EQ01_Q09_SEVERE_SOFT45",
                "Quality baseline плюс строгий severe-flush и мягкий early support pullback.",
            ),
            _combine_signals(
                all_results,
                manual_entries,
                (
                    "Q09_QUALITY_BASELINE",
                    "E01_SEVERE_FLUSH_LOCKOUT20",
                    "E03_SOFT_SUPPORT_PULLBACK_CD30",
                ),
                "EQ02_Q09_SEVERE_SOFT30",
                "Quality baseline плюс severe-flush и более частый soft-pullback.",
            ),
            _combine_signals(
                all_results,
                manual_entries,
                (
                    "Q09_QUALITY_BASELINE",
                    "E01_SEVERE_FLUSH_LOCKOUT20",
                    "E02_SOFT_SUPPORT_PULLBACK_CD45",
                    "E05_NO_WICK_LOW_CLOSE_CD15",
                ),
                "EQ03_Q09_SEVERE_SOFT45_NOWICK",
                "Quality baseline плюс severe/soft и рискованный канал свечи без фитиля.",
            ),
            _combine_signals(
                early_results,
                manual_entries,
                (
                    "E01_SEVERE_FLUSH_LOCKOUT20",
                    "E02_SOFT_SUPPORT_PULLBACK_CD45",
                    "E05_NO_WICK_LOW_CLOSE_CD15",
                ),
                "E06_EARLY_ONLY_SEVERE_SOFT_NOWICK",
                "Только ранние подсемейства без quality baseline.",
            ),
        ]
    )
    results = [item for item in all_results if int(item["score"]["target_hits"]) > 0]
    results.sort(key=_sort_key, reverse=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[dict[str, str]] = []
    for rank, result in enumerate(results[:render_top], 1):
        label = f"early_flush_{rank:02d}_{result['family_id'].lower()}"
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
        "status": "DEV_EARLY_FLUSH_REVERSAL_DIAGNOSTIC_NO_ML",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "manual_entries": str(manual_entries_path),
        "variants_total": len(EARLY_VARIANTS),
        "results_total": len(results),
        "best_overall": results,
        "rendered_overlays": rendered,
        "ml_transfer_allowed": False,
    }
    json_path = out_dir / "visual_entry_early_flush_reversal_20260512_DEV.json"
    md_path = out_dir / "visual_entry_early_flush_reversal_20260512_DEV_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run visual-entry early flush reversal diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/early_flush_reversal")
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
