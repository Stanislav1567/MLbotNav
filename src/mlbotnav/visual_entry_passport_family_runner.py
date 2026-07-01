from __future__ import annotations

import argparse
import itertools
import json
import warnings
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.errors import PerformanceWarning

from mlbotnav.dataset import build_feature_frame
from mlbotnav.render_visual_entry_overlay import render_family_candidate_overlay
from mlbotnav.visual_entry_score import TradeEntry, load_manual_entries, score_entries


SHIFTED_TO_ENTRY_ROW = {
    "F026_BINSHARE60_ALLOW",
    "F027_CLUSTERSHARE60_ALLOW",
    "F028_VPOCSHARE60_ALLOW",
    "F030_BINSHARE240_ALLOW",
    "F031_CLUSTERSHARE240_ALLOW",
    "F032_VPOCSHARE240_ALLOW",
    "F038_RANGEPOSE_ALLOW",
    "F039_CHANNELPOS_ALLOW",
    "F046_FALSEBREAK_ALLOW",
    "F047_RETEST_ALLOW",
    "F050_BOSUP_ALLOW",
    "F052_CHOCH_ALLOW",
    "F055_PINBULL_ALLOW",
    "F057_HAMMER_ALLOW",
    "F059_ENGULFBULL_ALLOW",
    "F061_RSIBULLDIV_ALLOW",
    "F063_MACDBULLDIV_ALLOW",
    "F065_OBVBULLDIV_ALLOW",
    "F078_PATTERNVOLCONF_ALLOW",
    "F079_PATTERNLEVELCONF_ALLOW",
}


@dataclass(frozen=True)
class ActionRef:
    column: str
    offset: int = 0


@dataclass(frozen=True)
class FamilySpec:
    family_id: str
    description_ru: str
    param_grid: dict[str, list[Any]]
    context: tuple[ActionRef, ...]
    trigger: tuple[ActionRef, ...]
    confirm: tuple[ActionRef, ...] = ()
    suppress: tuple[ActionRef, ...] = ()


def action(column: str) -> ActionRef:
    return ActionRef(column=column, offset=1 if column in SHIFTED_TO_ENTRY_ROW else 0)


def _cartesian(grid: dict[str, list[Any]]) -> list[dict[str, Any]]:
    keys = list(grid)
    return [dict(zip(keys, values)) for values in itertools.product(*(grid[key] for key in keys))]


FAMILY_SPECS: list[FamilySpec] = [
    FamilySpec(
        family_id="DEEP_CAPITULATION_NEXT_OPEN",
        description_ru="Глубокое падение/перепроданность плюс свечной разворот, вход на следующий open.",
        param_grid={
            "B001_family_move": [-1],
            "F004_thr_pct": [0.25, 0.40],
            "F005_thr_pct": [0.45],
            "F012_signal_mode": [1],
            "F012_cmp": [-1],
            "F012_level": [35, 45],
            "F017_F018_signal_mode": [1],
            "F017_F018_line": [1],
            "F017_F018_cmp": [-1],
            "F017_F018_level": [40],
            "F023_signal_mode": [1],
            "F023_cmp": [-1],
            "F023_level": [40],
            "F020_state": [1],
            "F020_z_level": [0.0],
            "F055_wick_body_ratio": [1.2],
            "F055_wick_min_pct": [45],
            "F055_opposite_wick_max_pct": [35],
            "F055_body_zone_pct": [55],
            "F055_min_range_pct": [0.01],
            "F057_wick_body_ratio": [1.2],
            "F057_lower_wick_min_pct": [45],
            "F057_upper_wick_max_pct": [35],
            "F057_body_zone_pct": [55],
            "F057_trend_lookback_bars": [3],
            "F057_trend_min_drop_pct": [0.0],
            "min_context_votes": [3],
            "min_trigger_votes": [1],
            "min_confirm_votes": [0, 1],
            "cooldown_bars": [15, 30],
        },
        context=(
            action("F004_RET12_ALLOW"),
            action("F005_RET24_ALLOW"),
            action("F012_RSI14_ALLOW"),
            action("F017_F018_STOCH14_ALLOW"),
            action("F023_MFI14_ALLOW"),
        ),
        trigger=(action("F055_PINBULL_ALLOW"), action("F057_HAMMER_ALLOW")),
        confirm=(action("F020_VOLZ20_ALLOW"),),
    ),
    FamilySpec(
        family_id="SUPPORT_WICK_REVERSAL_NEXT_OPEN",
        description_ru="Подход к поддержке/нижней зоне диапазона плюс pin/hammer/engulf, вход на следующий open.",
        param_grid={
            "F035_distance_state": [-1],
            "F035_dist_thr_pct": [0.10],
            "F038_zone": [-1],
            "F038_level": [35, 50],
            "F009_bias": [-1],
            "F009_thr_pct": [0.0],
            "F010_slope": [-1],
            "F010_thr_pct": [0.0],
            "F055_wick_body_ratio": [1.2],
            "F055_wick_min_pct": [45],
            "F055_opposite_wick_max_pct": [40],
            "F055_body_zone_pct": [60],
            "F055_min_range_pct": [0.01],
            "F057_wick_body_ratio": [1.2],
            "F057_lower_wick_min_pct": [45],
            "F057_upper_wick_max_pct": [40],
            "F057_body_zone_pct": [60],
            "F057_trend_lookback_bars": [3],
            "F057_trend_min_drop_pct": [0.0],
            "F059_engulf_mode": [1, 2],
            "F059_min_engulf_ratio": [1.0],
            "F059_min_body_pct": [5],
            "F059_trend_lookback_bars": [2],
            "F059_trend_min_drop_pct": [0.0],
            "min_context_votes": [2, 3],
            "min_trigger_votes": [1],
            "min_confirm_votes": [0],
            "cooldown_bars": [15, 30],
        },
        context=(
            action("F035_SUPPORTDIST_ALLOW"),
            action("F038_RANGEPOSE_ALLOW"),
            action("F009_EMAGAP_ALLOW"),
            action("F010_EMASLOPE5_ALLOW"),
        ),
        trigger=(action("F055_PINBULL_ALLOW"), action("F057_HAMMER_ALLOW"), action("F059_ENGULFBULL_ALLOW")),
    ),
    FamilySpec(
        family_id="DIVERGENCE_AT_SUPPORT_NEXT_OPEN",
        description_ru="Поддержка/нижний диапазон плюс bullish divergence, вход на следующий open.",
        param_grid={
            "F035_distance_state": [-1],
            "F035_dist_thr_pct": [0.10],
            "F038_zone": [-1],
            "F038_level": [35],
            "F061_pivot_scope": [1],
            "F061_div_type": [1],
            "F061_price_delta_min_pct": [0.05],
            "F061_rsi_delta_min": [1],
            "F061_max_pivot_gap_bars": [40],
            "F061_confirm_mode": [1],
            "F061_reaction_confirm_pct": [0.0],
            "F063_pivot_scope": [1],
            "F063_div_type": [1],
            "F063_macd_component": [3],
            "F063_price_delta_min_pct": [0.05],
            "F063_macd_delta_min_pct": [0.0],
            "F063_max_pivot_gap_bars": [40],
            "F063_confirm_mode": [1],
            "F063_reaction_confirm_pct": [0.0],
            "F057_wick_body_ratio": [1.2],
            "F057_lower_wick_min_pct": [40],
            "F057_upper_wick_max_pct": [45],
            "F057_body_zone_pct": [65],
            "F057_trend_lookback_bars": [3],
            "F057_trend_min_drop_pct": [0.0],
            "min_context_votes": [1, 2],
            "min_trigger_votes": [1],
            "min_confirm_votes": [0],
            "cooldown_bars": [30],
        },
        context=(action("F035_SUPPORTDIST_ALLOW"), action("F038_RANGEPOSE_ALLOW")),
        trigger=(action("F061_RSIBULLDIV_ALLOW"), action("F063_MACDBULLDIV_ALLOW"), action("F057_HAMMER_ALLOW")),
    ),
    FamilySpec(
        family_id="CHOCH_REENTRY_AFTER_BOTTOM_NEXT_OPEN",
        description_ru="Нижняя зона/поддержка плюс разворот структуры CHOCH/BOS, вход на следующий open.",
        param_grid={
            "F035_distance_state": [-1],
            "F035_dist_thr_pct": [0.15],
            "F038_zone": [-1],
            "F038_level": [35, 55],
            "F050_structure_scope": [1],
            "F050_break_buffer_pct": [0.0],
            "F050_confirm_bars": [1],
            "F050_require_bias": [2],
            "F052_structure_scope": [1],
            "F052_choch_dir": [1],
            "F052_break_buffer_pct": [0.0],
            "F052_confirm_bars": [1],
            "F052_require_opposite_bias": [0],
            "F055_wick_body_ratio": [1.2],
            "F055_wick_min_pct": [45],
            "F055_opposite_wick_max_pct": [40],
            "F055_body_zone_pct": [60],
            "F055_min_range_pct": [0.01],
            "F059_engulf_mode": [1],
            "F059_min_engulf_ratio": [1.0],
            "F059_min_body_pct": [5],
            "F059_trend_lookback_bars": [2],
            "F059_trend_min_drop_pct": [0.0],
            "min_context_votes": [1, 2],
            "min_trigger_votes": [1],
            "min_confirm_votes": [0, 1],
            "cooldown_bars": [15, 30],
        },
        context=(action("F035_SUPPORTDIST_ALLOW"), action("F038_RANGEPOSE_ALLOW")),
        trigger=(action("F055_PINBULL_ALLOW"), action("F059_ENGULFBULL_ALLOW")),
        confirm=(action("F050_BOSUP_ALLOW"), action("F052_CHOCH_ALLOW")),
    ),
    FamilySpec(
        family_id="VPOC_RANGE_RECLAIM_NEXT_OPEN",
        description_ru="VPOC/density/range reclaim около нижней зоны, вход на следующий open.",
        param_grid={
            "F025_signal_mode": [2],
            "F025_distance_state": [-1],
            "F025_dist_thr_pct": [0.10],
            "F028_cmp": [1],
            "F028_share_thr_pct": [1.0],
            "F032_cmp": [1],
            "F032_share_thr_pct": [0.5],
            "F038_zone": [-1],
            "F038_level": [35, 55],
            "F046_level_source_mode": [2],
            "F046_break_dir": [-1],
            "F046_false_mode": [1],
            "F046_break_buffer_pct": [0.0],
            "F046_return_window_bars": [3],
            "F046_return_tolerance_pct": [0.10],
            "F047_level_source_mode": [2],
            "F047_break_dir": [1],
            "F047_retest_window_bars": [10],
            "F047_retest_tolerance_pct": [0.15],
            "F047_reaction_confirm_pct": [0.0],
            "F020_state": [1],
            "F020_z_level": [0.0],
            "min_context_votes": [2, 3],
            "min_trigger_votes": [1],
            "min_confirm_votes": [0, 1],
            "cooldown_bars": [20, 45],
        },
        context=(
            action("F025_VPOCDIST60_ALLOW"),
            action("F028_VPOCSHARE60_ALLOW"),
            action("F032_VPOCSHARE240_ALLOW"),
            action("F038_RANGEPOSE_ALLOW"),
        ),
        trigger=(action("F046_FALSEBREAK_ALLOW"), action("F047_RETEST_ALLOW")),
        confirm=(action("F020_VOLZ20_ALLOW"),),
    ),
]


def _load_core(manual_payload: dict[str, Any]) -> pd.DataFrame:
    source_csv = Path(manual_payload["source_images"][0]["source_csv"])
    frame = pd.read_csv(source_csv)
    frame["open_time_utc"] = pd.to_datetime(frame["open_time_utc"], utc=True, errors="coerce", format="mixed")
    if "close_time_utc" in frame.columns:
        frame["close_time_utc"] = pd.to_datetime(frame["close_time_utc"], utc=True, errors="coerce", format="mixed")
    else:
        frame["close_time_utc"] = frame["open_time_utc"] + pd.Timedelta(minutes=1)
    return frame.dropna(subset=["open_time_utc"]).sort_values("open_time_utc").reset_index(drop=True)


def _meta_from_params(params: dict[str, Any]) -> dict[str, Any]:
    return {
        "min_context_votes": int(params.pop("min_context_votes", 1)),
        "min_trigger_votes": int(params.pop("min_trigger_votes", 1)),
        "min_confirm_votes": int(params.pop("min_confirm_votes", 0)),
        "cooldown_bars": int(params.pop("cooldown_bars", 20)),
    }


def _vote(frame: pd.DataFrame, signal_idx: int, ref: ActionRef) -> bool:
    idx = signal_idx + ref.offset
    if idx < 0 or idx >= len(frame) or ref.column not in frame.columns:
        return False
    try:
        return float(frame.iloc[idx].get(ref.column, 0) or 0) >= 1.0
    except (TypeError, ValueError):
        return False


def _vote_names(frame: pd.DataFrame, signal_idx: int, refs: tuple[ActionRef, ...]) -> list[str]:
    return [ref.column for ref in refs if _vote(frame, signal_idx, ref)]


def _signal_detail(
    frame: pd.DataFrame,
    *,
    signal_idx: int,
    context_votes: list[str],
    trigger_votes: list[str],
    confirm_votes: list[str],
    family_id: str,
) -> dict[str, Any]:
    entry_idx = signal_idx + 1
    signal_row = frame.iloc[signal_idx]
    entry_row = frame.iloc[entry_idx]
    entry_open_price = float(entry_row["open"])
    slippage_bps = 5.0
    return {
        "family_id": family_id,
        "side": "long",
        "signal_row_index": int(signal_idx),
        "entry_row_index": int(entry_idx),
        "signal_time_utc": pd.Timestamp(signal_row["open_time_utc"]).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_time_utc": pd.Timestamp(entry_row["open_time_utc"]).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_open_price": entry_open_price,
        "entry_price_with_slippage": entry_open_price * (1.0 + slippage_bps / 10000.0),
        "slippage_bps": slippage_bps,
        "context_votes": context_votes,
        "trigger_votes": trigger_votes,
        "confirm_votes": confirm_votes,
        "lookahead": "NO",
        "entry_rule": "next_bar_open_after_signal_close",
    }


def _trades_from_details(details: list[dict[str, Any]]) -> list[TradeEntry]:
    trades: list[TradeEntry] = []
    for item in details:
        ts = pd.to_datetime(item["entry_time_utc"], utc=True, errors="coerce")
        if pd.isna(ts):
            continue
        trades.append(
            TradeEntry(
                row_index=int(item.get("entry_row_index") or 0),
                side="long",
                entry_time=ts.to_pydatetime(),
                exit_time_raw="",
                net_return=0.0,
                mae_pct=None,
                mfe_pct=None,
            )
        )
    return trades


def _run_family_variant(
    *,
    spec: FamilySpec,
    core: pd.DataFrame,
    manual_entries: list[Any],
    params: dict[str, Any],
) -> dict[str, Any]:
    meta = _meta_from_params(params)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PerformanceWarning)
        frame = build_feature_frame(
            core,
            horizon_bars=1,
            calibration_params=params,
            include_targets=False,
            include_dropna=False,
        )
    details: list[dict[str, Any]] = []
    last_entry_idx = -10_000
    for signal_idx in range(60, len(frame) - 1):
        entry_idx = signal_idx + 1
        if entry_idx - last_entry_idx < meta["cooldown_bars"]:
            continue
        suppress_votes = _vote_names(frame, signal_idx, spec.suppress)
        if suppress_votes:
            continue
        context_votes = _vote_names(frame, signal_idx, spec.context)
        if len(context_votes) < meta["min_context_votes"]:
            continue
        trigger_votes = _vote_names(frame, signal_idx, spec.trigger)
        if len(trigger_votes) < meta["min_trigger_votes"]:
            continue
        confirm_votes = _vote_names(frame, signal_idx, spec.confirm)
        if len(confirm_votes) < meta["min_confirm_votes"]:
            continue
        last_entry_idx = entry_idx
        details.append(
            _signal_detail(
                frame,
                signal_idx=signal_idx,
                context_votes=context_votes,
                trigger_votes=trigger_votes,
                confirm_votes=confirm_votes,
                family_id=spec.family_id,
            )
        )
    trades = _trades_from_details(details)
    score = score_entries(manual_entries, trades)
    return {
        "family_id": spec.family_id,
        "description_ru": spec.description_ru,
        "params": {**params, **meta},
        "score": _score_summary(score),
        "hit_details": score["hit_details"],
        "missed_target_details": score["missed_target_details"],
        "false_entry_details": score["false_entry_details"][:200],
        "signals": details,
    }


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


def _sort_key(item: dict[str, Any]) -> tuple[float, float, float, int, int]:
    score = item["score"]
    return (
        float(score["f1_visual"]),
        float(score["recall"]),
        float(score["precision"]),
        -int(score["false_entries"]),
        -int(score["entries_total"]),
    )


def _public_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in results:
        public = dict(item)
        public["signals"] = item.get("signals", [])[:300]
        out.append(public)
    return out


def _write_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Visual Entry passport family runner",
        "",
        "Статус: `DEV_PASSPORT_FAMILY_DIAGNOSTIC_NO_ML`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "Контракт: сигнал считается на закрытой свече, LONG вход ставится на `open` следующей свечи, `lookahead=NO`, slippage `5 bps`.",
        "",
        "## Лучшие результаты",
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
    lines.extend(["", "## Лучшее по семействам", ""])
    for item in payload["best_by_family"]:
        score = item["score"]
        lines.append(
            "- `{}`: hits `{}/{}`, miss `{}`, false `{}`, entries `{}`, precision `{:.4f}`, recall `{:.4f}`, f1 `{:.4f}`.".format(
                item["family_id"],
                score["target_hits"],
                score["targets_total"],
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
    manual_payload, manual_entries = load_manual_entries(manual_entries_path)
    core = _load_core(manual_payload)
    all_results: list[dict[str, Any]] = []
    best_by_family: list[dict[str, Any]] = []

    for spec in FAMILY_SPECS:
        family_results: list[dict[str, Any]] = []
        for params_raw in _cartesian(spec.param_grid):
            params = dict(params_raw)
            result = _run_family_variant(
                spec=spec,
                core=core,
                manual_entries=manual_entries,
                params=params,
            )
            if result["score"]["entries_total"] <= 0:
                continue
            family_results.append(result)
            all_results.append(result)
        family_results.sort(key=_sort_key, reverse=True)
        if family_results:
            best_by_family.append(family_results[0])

    all_results.sort(key=_sort_key, reverse=True)
    best_by_family.sort(key=_sort_key, reverse=True)
    rendered: list[dict[str, str]] = []
    for rank, result in enumerate(all_results[:render_top], 1):
        label = f"family_{rank:02d}_{result['family_id']}"
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
        "status": "DEV_PASSPORT_FAMILY_DIAGNOSTIC_NO_ML",
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "manual_entries": str(manual_entries_path),
        "source_csv": str(manual_payload["source_images"][0]["source_csv"]),
        "source_csv_sha256": str(manual_payload["source_images"][0].get("source_csv_sha256", "")),
        "entry_contract": {
            "signal": "closed_signal_candle",
            "entry": "next_bar_open",
            "lookahead": "NO",
            "slippage_bps": 5.0,
        },
        "families_tested": [spec.family_id for spec in FAMILY_SPECS],
        "results_total": len(all_results),
        "best_overall": _public_results(all_results[:30]),
        "best_by_family": _public_results(best_by_family),
        "rendered_overlays": rendered,
        "ml_transfer_allowed": False,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "visual_entry_passport_family_runner_20260512_DEV.json"
    md_path = out_dir / "visual_entry_passport_family_runner_20260512_DEV_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_write_markdown(payload), encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["md_path"] = str(md_path)
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run no-lookahead visual entry passport family diagnostics.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/passport_family_runner")
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
