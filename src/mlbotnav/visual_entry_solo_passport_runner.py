from __future__ import annotations

import argparse
import itertools
import json
from datetime import timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.dataset import build_feature_frame
from mlbotnav.render_visual_entry_overlay import render_overlay
from mlbotnav.visual_entry_score import TradeEntry, load_manual_entries, score_entries


PASSPORTS: dict[str, dict[str, Any]] = {
    "F012_RSI14": {
        "action_col": "F012_RSI14_ALLOW",
        "grid": {
            "F012_signal_mode": [1],
            "F012_cmp": [-1],
            "F012_level": [30, 35, 40, 45],
            "cooldown_bars": [10, 20, 60],
        },
    },
    "F017_F018_STOCH14": {
        "action_col": "F017_F018_STOCH14_ALLOW",
        "grid": {
            "F017_F018_signal_mode": [1],
            "F017_F018_line": [1],
            "F017_F018_cmp": [-1],
            "F017_F018_level": [20, 30, 40, 50],
            "cooldown_bars": [10, 20, 60],
        },
    },
    "F038_RANGEPOSE": {
        "action_col": "F038_RANGEPOSE_ALLOW",
        "grid": {
            "F038_zone": [-1],
            "F038_level": [20, 25, 35, 50],
            "cooldown_bars": [10, 20, 60],
        },
    },
    "F035_SUPPORTDIST": {
        "action_col": "F035_SUPPORTDIST_ALLOW",
        "grid": {
            "F035_distance_state": [-1],
            "F035_dist_thr_pct": [0.05, 0.10, 0.20, 0.35],
            "cooldown_bars": [10, 20, 60],
        },
    },
    "F055_PINBULL": {
        "action_col": "F055_PINBULL_ALLOW",
        "grid": {
            "F055_wick_body_ratio": [1.5, 2.5],
            "F055_wick_min_pct": [50, 65],
            "F055_opposite_wick_max_pct": [20],
            "F055_body_zone_pct": [40],
            "F055_min_range_pct": [0.02],
            "cooldown_bars": [20, 60],
        },
    },
    "F057_HAMMER": {
        "action_col": "F057_HAMMER_ALLOW",
        "grid": {
            "F057_wick_body_ratio": [1.5, 2.5],
            "F057_lower_wick_min_pct": [50, 65],
            "F057_upper_wick_max_pct": [20],
            "F057_body_zone_pct": [40],
            "F057_trend_lookback_bars": [3, 12],
            "F057_trend_min_drop_pct": [0.05, 0.30],
            "cooldown_bars": [20, 60],
        },
    },
    "F059_ENGULFBULL": {
        "action_col": "F059_ENGULFBULL_ALLOW",
        "grid": {
            "F059_engulf_mode": [1, 2],
            "F059_min_engulf_ratio": [1.0, 1.5],
            "F059_min_body_pct": [10, 30],
            "F059_trend_lookback_bars": [2, 12],
            "F059_trend_min_drop_pct": [0.0, 0.30],
            "cooldown_bars": [20, 60],
        },
    },
    "F009_EMAGAP_DOWN": {
        "action_col": "F009_EMAGAP_ALLOW",
        "grid": {
            "F009_bias": [-1],
            "F009_thr_pct": [0.0, 0.05, 0.10, 0.20],
            "cooldown_bars": [10, 20, 60],
        },
    },
    "F010_EMASLOPE_DOWN": {
        "action_col": "F010_EMASLOPE5_ALLOW",
        "grid": {
            "F010_slope": [-1],
            "F010_thr_pct": [0.0, 0.02, 0.05, 0.10],
            "cooldown_bars": [10, 20, 60],
        },
    },
    "F020_VOLZ20_HIGH": {
        "action_col": "F020_VOLZ20_ALLOW",
        "grid": {
            "F020_state": [1],
            "F020_z_level": [0.0, 0.5, 1.0, 1.5, 2.0],
            "cooldown_bars": [10, 20, 60],
        },
    },
    "B001_RET_N_FIXED": {
        "action_col": None,
        "grid": {
            "B001_family_move": [1],
            "F001_thr_pct": [0.02],
            "F002_thr_pct": [0.04],
            "F003_thr_pct": [0.10],
            "F004_thr_pct": [0.95],
            "F005_thr_pct": [0.35],
            "entry_action_min_confirmations": [3],
            "cooldown_bars": [0],
        },
        "action_cols": [
            "F001_RET1_ALLOW",
            "F002_RET3_ALLOW",
            "F003_RET6_ALLOW",
            "F004_RET12_ALLOW",
            "F005_RET24_ALLOW",
        ],
    },
}


def _iter_grid(grid: dict[str, list[Any]]) -> list[dict[str, Any]]:
    keys = list(grid)
    return [dict(zip(keys, values)) for values in itertools.product(*(grid[key] for key in keys))]


def _load_core(manual_payload: dict[str, Any]) -> pd.DataFrame:
    source_csv = Path(manual_payload["source_images"][0]["source_csv"])
    df = pd.read_csv(source_csv)
    df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], utc=True, errors="coerce", format="mixed")
    if "close_time_utc" in df.columns:
        df["close_time_utc"] = pd.to_datetime(df["close_time_utc"], utc=True, errors="coerce", format="mixed")
    else:
        df["close_time_utc"] = df["open_time_utc"] + pd.Timedelta(minutes=1)
    return df.dropna(subset=["open_time_utc"]).sort_values("open_time_utc").reset_index(drop=True)


def _signals_from_frame(
    frame: pd.DataFrame,
    *,
    action_cols: list[str],
    min_confirmations: int,
    cooldown_bars: int,
) -> list[TradeEntry]:
    trades: list[TradeEntry] = []
    last_idx = -10_000
    for idx, row in frame.iterrows():
        if idx < 60:
            continue
        votes = 0
        for col in action_cols:
            if col in frame.columns and float(row.get(col, 0) or 0) >= 1.0:
                votes += 1
        if votes < min_confirmations:
            continue
        if cooldown_bars > 0 and idx - last_idx < cooldown_bars:
            continue
        last_idx = int(idx)
        entry_time = pd.Timestamp(row["open_time_utc"]).to_pydatetime() + timedelta(minutes=1)
        trades.append(
            TradeEntry(
                row_index=int(idx),
                side="long",
                entry_time=entry_time,
                exit_time_raw="",
                net_return=0.0,
                mae_pct=None,
                mfe_pct=None,
            )
        )
    return trades


def run_search(manual_entries_path: Path, out_dir: Path, *, render_top: int = 6) -> dict[str, Any]:
    manual_payload, manual_entries = load_manual_entries(manual_entries_path)
    core = _load_core(manual_payload)
    all_results: list[dict[str, Any]] = []
    best_by_passport: list[dict[str, Any]] = []

    for passport_id, spec in PASSPORTS.items():
        passport_results: list[dict[str, Any]] = []
        for params in _iter_grid(spec["grid"]):
            cooldown = int(params.pop("cooldown_bars", 20))
            frame = build_feature_frame(
                core,
                horizon_bars=1,
                calibration_params=params,
                include_targets=False,
                include_dropna=False,
            )
            action_cols = list(spec.get("action_cols") or [spec["action_col"]])
            min_confirmations = int(params.get("entry_action_min_confirmations", 1))
            trades = _signals_from_frame(
                frame,
                action_cols=action_cols,
                min_confirmations=min_confirmations,
                cooldown_bars=cooldown,
            )
            if not trades:
                continue
            score = score_entries(manual_entries, trades)
            if score["target_hits"] <= 0:
                continue
            result = {
                "passport_id": passport_id,
                "action_columns": action_cols,
                "params": {**params, "cooldown_bars": cooldown},
                "score": _score_summary(score),
                "hit_details": score["hit_details"],
                "missed_target_details": score["missed_target_details"],
                "_trades": trades,
            }
            passport_results.append(result)
            all_results.append(result)
        passport_results.sort(key=_result_sort_key, reverse=True)
        if passport_results:
            best_by_passport.append(passport_results[0])

    all_results.sort(key=_result_sort_key, reverse=True)
    best_by_passport.sort(key=_result_sort_key, reverse=True)

    rendered: list[dict[str, str]] = []
    for rank, result in enumerate(best_by_passport[:render_top], 1):
        label = f"SOLO_{rank:02d}_{result['passport_id']}"
        png_path, json_path = render_overlay(
            manual_entries_path=manual_entries_path,
            trades=result["_trades"],
            label=label,
            out_dir=out_dir,
        )
        rendered.append(
            {
                "passport_id": result["passport_id"],
                "visual_png": str(png_path),
                "summary_json": str(json_path),
            }
        )

    payload = {
        "schema_version": 1,
        "manual_entries": str(manual_entries_path),
        "results_total": len(all_results),
        "best_overall": _public_results(all_results[:30]),
        "best_by_passport": _public_results(best_by_passport),
        "rendered_overlays": rendered,
        "ml_transfer_allowed": False,
    }
    write_reports(payload, out_dir)
    return payload


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


def _result_sort_key(item: dict[str, Any]) -> tuple[float, float, float, int, int]:
    s = item["score"]
    return (
        float(s["f1_visual"]),
        float(s["recall"]),
        float(s["precision"]),
        -int(s["false_entries"]),
        -int(s["entries_total"]),
    )


def _public_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for result in results:
        public = {k: v for k, v in result.items() if k != "_trades"}
        out.append(public)
    return out


def write_reports(payload: dict[str, Any], out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "visual_entry_solo_passport_runner_20260512_DEV.json"
    md_path = out_dir / "visual_entry_solo_passport_runner_20260512_DEV_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    return json_path, md_path


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Visual Entry Solo Passport Runner 2026-05-12",
        "",
        "Статус: `DEV_DIAGNOSTIC_ONLY_NO_ML`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        f"Всего вариантов с попаданиями: `{payload['results_total']}`.",
        "",
        "## Best By Passport",
        "",
        "| rank | passport | hits | false | entries | precision | recall | f1 | params |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for rank, result in enumerate(payload["best_by_passport"], 1):
        score = result["score"]
        lines.append(
            "| `{rank}` | `{passport}` | `{hits}` | `{false}` | `{entries}` | `{precision:.4f}` | `{recall:.4f}` | `{f1:.4f}` | `{params}` |".format(
                rank=rank,
                passport=result["passport_id"],
                hits=score["target_hits"],
                false=score["false_entries"],
                entries=score["entries_total"],
                precision=score["precision"],
                recall=score["recall"],
                f1=score["f1_visual"],
                params=json.dumps(result["params"], ensure_ascii=False, sort_keys=True),
            )
        )
    lines.extend(["", "## Rendered Overlays", ""])
    for item in payload["rendered_overlays"]:
        lines.append(f"- `{item['passport_id']}`: `{item['visual_png']}`")
    lines.extend(
        [
            "",
            "## Решение",
            "",
            "Это diagnostic-only слой. В ML ничего не передавать. Следующий шаг выбирать только после визуального просмотра PNG overlay.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run solo passport visual diagnostics against manual entries.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review")
    parser.add_argument("--render-top", type=int, default=6)
    args = parser.parse_args(argv)
    payload = run_search(Path(args.manual_entries), Path(args.out_dir), render_top=args.render_top)
    report_json = Path(args.out_dir) / "visual_entry_solo_passport_runner_20260512_DEV.json"
    report_md = Path(args.out_dir) / "visual_entry_solo_passport_runner_20260512_DEV_RU.md"
    print(
        json.dumps(
            {
                "status": "OK",
                "report_json": str(report_json),
                "report_md": str(report_md),
                "rendered": payload["rendered_overlays"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
