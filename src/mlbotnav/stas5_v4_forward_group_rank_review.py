from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from mlbotnav.stas5_common import PROJECT_ROOT, STAS5_ARTIFACTS_DIR, compact_day, iter_days, rel, run_stamp, utc_now, write_json
from mlbotnav.stas5_entry_ranker_train import _positive_proba, _prepare_feature_matrix
from mlbotnav.stas5_forward_entry_review import _add_postfact_audit, ensure_forward_stas2_run
from mlbotnav.stas5_v2_combo_feature_exporter import TIMEFRAME, build_combo_features
from mlbotnav.stas5_v2_feature_snapshot_builder import DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH
from mlbotnav.stas5_v2_forward_entry_review import build_v2_forward_snapshot, render_v2_forward_day
from mlbotnav.stas5_v2_feature_visual_approval import _read_rows
from mlbotnav.stas5_v4_group_rank_dataset import _add_group_features
from mlbotnav.stas5_v4_group_rank_train import (
    DEFAULT_V4_MODEL_DIR,
    DEFAULT_V4_MODEL_MANIFEST_PATH,
    DEFAULT_V4_MODEL_PATH,
    apply_v4_decision_policy,
)
from mlbotnav.visual_entry_low_anchor_suggester import _load_ohlcv, _source_csv


STATUS = "STAS5_V4_FORWARD_GROUP_RANK_REVIEW_READY_BLIND_NO_TP_NO_API_NO_STAS3"
SYMBOL = "SOLUSDT"
DEFAULT_START_DAY = "2026-05-26"
DEFAULT_END_DAY = "2026-05-30"
DEFAULT_V4_FORWARD_ROOT = STAS5_ARTIFACTS_DIR / "v4" / "forward"
DEFAULT_V4_FORWARD_RUNS_DIR = DEFAULT_V4_FORWARD_ROOT / "runs"
DEFAULT_V4_FORWARD_SOURCE_DIR = STAS5_ARTIFACTS_DIR / "v4" / "forward_source"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_model_manifest() -> Path:
    pointer = DEFAULT_V4_MODEL_DIR / "STAS5_V4_LATEST_MODEL_RUN.json"
    if pointer.exists():
        payload = _load_json(pointer)
        manifest_path = Path(payload.get("manifest_path", ""))
        if not manifest_path.is_absolute():
            manifest_path = PROJECT_ROOT / manifest_path
        if manifest_path.exists():
            return manifest_path
    manifests = sorted(
        DEFAULT_V4_MODEL_DIR.glob("runs/*/stas5_v4_group_ranker_20260501_20260525_v0.manifest.json"),
        key=lambda item: item.stat().st_mtime,
    )
    if manifests:
        return manifests[-1]
    if DEFAULT_V4_MODEL_MANIFEST_PATH.exists():
        return DEFAULT_V4_MODEL_MANIFEST_PATH
    raise FileNotFoundError("no STAS5 V4 model manifest found")


def _model_path_from_manifest(manifest_path: Path) -> Path:
    payload = _load_json(manifest_path)
    model_path = Path(payload.get("model_path", ""))
    if not model_path.is_absolute():
        model_path = PROJECT_ROOT / model_path
    if not model_path.exists():
        raise FileNotFoundError(f"model file from manifest not found: {model_path}")
    return model_path


def _auto_group_forward_candidates(
    rows: pd.DataFrame,
    *,
    max_gap_min: int = 75,
    max_group_duration_min: int = 300,
) -> pd.DataFrame:
    out = rows.copy()
    out["entry_time_utc"] = pd.to_datetime(out["entry_time_utc"], utc=True, errors="coerce")
    group_ids: dict[Any, str] = {}
    for day, day_rows in out.sort_values(["day", "entry_time_utc", "record_id"]).groupby("day", sort=True):
        group_idx = 0
        last_ts: pd.Timestamp | None = None
        group_start: pd.Timestamp | None = None
        for idx, row in day_rows.iterrows():
            ts = pd.Timestamp(row["entry_time_utc"])
            new_group = False
            if last_ts is None or group_start is None:
                new_group = True
            elif (ts - last_ts).total_seconds() / 60.0 > max_gap_min:
                new_group = True
            elif (ts - group_start).total_seconds() / 60.0 > max_group_duration_min:
                new_group = True
            if new_group:
                group_idx += 1
                group_start = ts
            group_ids[idx] = f"G{compact_day(str(day))}_AUTO_{group_idx:03d}"
            last_ts = ts
    out["entry_time_utc"] = out["entry_time_utc"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    out["group_id"] = out.index.map(group_ids)
    out["symbol"] = SYMBOL
    out["timeframe"] = TIMEFRAME
    out["rank_label"] = "REVIEW_ONLY"
    out["is_group_winner"] = 0
    out["primary_reason_code"] = "FORWARD_AUTO_GROUP_REVIEW_ONLY"
    out["secondary_reason_codes"] = ""
    out["label_status"] = "FORWARD_REVIEW_ONLY"
    out["source_review_file"] = "AUTO_FORWARD_GROUPS_20260526_20260530"
    out["notes"] = "auto group for blind V4 forward ranking"
    return _add_group_features(out)


def predict_v4_forward(
    *,
    snapshot: pd.DataFrame,
    model_package: dict[str, Any],
    model_manifest: dict[str, Any],
) -> pd.DataFrame:
    grouped = _auto_group_forward_candidates(snapshot)
    feature_columns = [str(column) for column in model_package["feature_columns"]]
    x = _prepare_feature_matrix(
        grouped,
        feature_columns=feature_columns,
        numeric_columns=[str(column) for column in model_package.get("numeric_columns", [])],
        categorical_columns=[str(column) for column in model_package.get("categorical_columns", [])],
    )
    scores = _positive_proba(model_package["pipeline"], x)
    out = grouped.copy()
    out["V4_GROUP_RANK_SCORE"] = scores
    thresholds = model_package.get("thresholds") or model_manifest.get("thresholds") or {"enter": 0.50, "unsure": 0.35}
    out = apply_v4_decision_policy(
        out,
        score_column="V4_GROUP_RANK_SCORE",
        enter_threshold=float(thresholds["enter"]),
        unsure_threshold=float(thresholds["unsure"]),
    )
    out["ML_KEEP_SCORE_V2"] = out["V4_GROUP_RANK_SCORE"]
    out["ML_DECISION_V2"] = out["V4_DECISION"]
    out["ML_KEEP_SCORE"] = out["V4_GROUP_RANK_SCORE"]
    out["ML_DECISION"] = out["V4_DECISION"]
    out["model_id"] = model_package.get("model_id") or model_manifest.get("model_id") or "STAS5_V4_HUMAN_STYLE_GROUP_RANKER_V0"
    out["model_feature_set"] = model_package.get("model_feature_set") or model_manifest.get("model_feature_set")
    out["threshold_enter"] = float(thresholds["enter"])
    out["threshold_unsure"] = float(thresholds["unsure"])
    out["forward_policy"] = "blind_forward_v4_rank_inside_auto_group_not_training_not_threshold_tuning"
    return out


def _day_summary(rows: pd.DataFrame) -> dict[str, Any]:
    counts = Counter(rows["V4_DECISION"].astype(str))
    top_entries = (
        rows[rows["V4_DECISION"].astype(str) == "ENTER"]
        .sort_values(["V4_GROUP_RANK_SCORE"], ascending=False)[
            ["candidate_id", "group_id", "entry_time_utc", "entry_price_5bps", "V4_GROUP_RANK_SCORE"]
        ]
        .to_dict("records")
    )
    return {
        "rows": int(len(rows)),
        "groups": int(rows["group_id"].nunique()),
        "decision_counts": dict(counts),
        "enter_candidates": top_entries,
    }


def run_v4_forward_group_rank_review(
    *,
    start_day: str = DEFAULT_START_DAY,
    end_day: str = DEFAULT_END_DAY,
    symbol: str = SYMBOL,
    timeframe: str = TIMEFRAME,
    model_path: Path = DEFAULT_V4_MODEL_PATH,
    model_manifest_path: Path = DEFAULT_V4_MODEL_MANIFEST_PATH,
    train_snapshot_manifest_path: Path = DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH,
    stas2_run_dir: Path | None = None,
    out_dir: Path = DEFAULT_V4_FORWARD_ROOT,
    forward_source_dir: Path = DEFAULT_V4_FORWARD_SOURCE_DIR,
    stas2_render_limit: int = 1,
) -> dict[str, Any]:
    model_package = joblib.load(model_path)
    model_manifest = _load_json(model_manifest_path)
    stas2_dir = ensure_forward_stas2_run(
        start_day=start_day,
        end_day=end_day,
        symbol=symbol,
        timeframe=timeframe,
        stas2_run_dir=stas2_run_dir,
        forward_source_dir=forward_source_dir,
        stas2_render_limit=stas2_render_limit,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    combo_path = out_dir / f"stas5_v4_combo_features_{compact_day(start_day)}_{compact_day(end_day)}_forward.csv"
    combo_manifest_path = combo_path.with_suffix(".manifest.json")
    _combo, combo_manifest = build_combo_features(
        stas2_run_dir=stas2_dir,
        start_day=start_day,
        end_day=end_day,
        output_csv=combo_path,
        manifest_path=combo_manifest_path,
        strict=True,
    )
    snapshot, snapshot_manifest = build_v2_forward_snapshot(
        stas2_run_dir=stas2_dir,
        v2_combo_path=combo_path,
        train_snapshot_manifest_path=train_snapshot_manifest_path,
    )
    if snapshot_manifest["status"] != "PASS":
        raise ValueError(f"V4 forward snapshot failed: {snapshot_manifest.get('checks')}")
    predictions = predict_v4_forward(snapshot=snapshot, model_package=model_package, model_manifest=model_manifest)

    all_predictions_path = out_dir / f"STAS5_V4_FORWARD_ALL_PREDICTIONS_{compact_day(start_day)}_{compact_day(end_day)}.csv"
    predictions.to_csv(all_predictions_path, index=False, encoding="utf-8-sig")

    day_outputs: list[dict[str, Any]] = []
    for day in iter_days(start_day, end_day):
        day_rows = predictions[predictions["day"].astype(str) == day].copy()
        day_dir = out_dir / compact_day(day)
        source = _source_csv(PROJECT_ROOT, day, timeframe, symbol)
        if not source.exists():
            day_outputs.append({"day": day, "status": "MISSING_OHLCV", "rows": int(len(day_rows)), "source": rel(source)})
            continue
        day_df = _load_ohlcv(source)
        day_rows = _add_postfact_audit(day_df, day_rows)
        csv_path = day_dir / f"STAS5_V4_FORWARD_GROUP_RANK_ENTRIES_{compact_day(day)}.csv"
        png_path = day_dir / f"STAS5_V4_FORWARD_GROUP_RANK_REVIEW_{compact_day(day)}.png"
        day_dir.mkdir(parents=True, exist_ok=True)
        day_rows.to_csv(csv_path, index=False, encoding="utf-8-sig")
        hour_rows = _read_rows(stas2_dir / "STAS2_HOURLY_PHASES.csv", day)
        macro_wave_rows = _read_rows(stas2_dir / "STAS2_MACRO_WAVES.csv", day)
        render_v2_forward_day(
            day_df=day_df,
            rows=day_rows,
            hour_rows=hour_rows,
            macro_wave_rows=macro_wave_rows,
            day=day,
            symbol=symbol,
            timeframe=timeframe,
            out_path=png_path,
        )
        summary = _day_summary(day_rows)
        day_outputs.append(
            {
                "day": day,
                "status": "READY",
                "rows": summary["rows"],
                "groups": summary["groups"],
                "decision_counts": summary["decision_counts"],
                "enter_candidates": summary["enter_candidates"],
                "csv": rel(csv_path),
                "png": rel(png_path),
            }
        )

    manifest = {
        "status": STATUS,
        "created_utc": utc_now(),
        "run_id": out_dir.name if out_dir.name else "",
        "run_dir": rel(out_dir),
        "date_range": {"start_day": start_day, "end_day": end_day},
        "symbol": symbol,
        "timeframe": timeframe,
        "model_path": rel(model_path),
        "model_manifest_path": rel(model_manifest_path),
        "model_id": model_package.get("model_id") or model_manifest.get("model_id"),
        "model_feature_set": model_package.get("model_feature_set") or model_manifest.get("model_feature_set"),
        "thresholds": model_package.get("thresholds") or model_manifest.get("thresholds"),
        "decision_policy": model_package.get("decision_policy"),
        "stas2_run_dir": rel(stas2_dir),
        "combo_path": rel(combo_path),
        "combo_manifest_status": combo_manifest.get("status"),
        "snapshot_manifest": snapshot_manifest,
        "all_predictions_csv": rel(all_predictions_path),
        "day_outputs": day_outputs,
        "decision_counts_total": dict(Counter(predictions["V4_DECISION"].astype(str))),
        "guardrails": [
            "forward_days_not_used_for_training",
            "forward_days_not_used_for_threshold_tuning",
            "auto_groups_are_for_review_and_rank_inside_group",
            "old_ml_score_decision_not_used_as_features",
            "postfact_columns_are_audit_only",
            "no_tp_stas3_api",
        ],
    }
    manifest_path = out_dir / "STAS5_V4_FORWARD_GROUP_RANK_REVIEW_MANIFEST.json"
    write_json(manifest_path, manifest)
    write_json(
        DEFAULT_V4_FORWARD_ROOT / "STAS5_V4_LATEST_FORWARD_RUN.json",
        {
            "status": "LATEST_FORWARD_RUN_POINTER",
            "created_utc": utc_now(),
            "run_id": manifest["run_id"],
            "run_dir": manifest["run_dir"],
            "manifest_path": rel(manifest_path),
        },
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Run STAS5 V4 blind forward group-rank review.")
    parser.add_argument("--start-day", default=DEFAULT_START_DAY)
    parser.add_argument("--end-day", default=DEFAULT_END_DAY)
    parser.add_argument("--symbol", default=SYMBOL)
    parser.add_argument("--timeframe", default=TIMEFRAME)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--run-root", default=str(DEFAULT_V4_FORWARD_RUNS_DIR))
    parser.add_argument("--model-path", default="")
    parser.add_argument("--model-manifest-path", default="")
    parser.add_argument("--train-snapshot-manifest-path", default=str(DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH))
    parser.add_argument("--stas2-run-dir", default="")
    parser.add_argument("--out-dir", default="")
    parser.add_argument("--forward-source-dir", default=str(DEFAULT_V4_FORWARD_SOURCE_DIR))
    parser.add_argument("--stas2-render-limit", type=int, default=1)
    args = parser.parse_args()

    model_manifest_path = Path(args.model_manifest_path) if args.model_manifest_path else _latest_model_manifest()
    model_path = Path(args.model_path) if args.model_path else _model_path_from_manifest(model_manifest_path)
    run_id = args.run_id or f"stas5_v4_forward_{compact_day(args.start_day)}_{compact_day(args.end_day)}_{run_stamp()}"
    out_dir = Path(args.out_dir) if args.out_dir else Path(args.run_root) / run_id
    manifest = run_v4_forward_group_rank_review(
        start_day=args.start_day,
        end_day=args.end_day,
        symbol=args.symbol,
        timeframe=args.timeframe,
        model_path=model_path,
        model_manifest_path=model_manifest_path,
        train_snapshot_manifest_path=Path(args.train_snapshot_manifest_path),
        stas2_run_dir=Path(args.stas2_run_dir) if args.stas2_run_dir else None,
        out_dir=out_dir,
        forward_source_dir=Path(args.forward_source_dir),
        stas2_render_limit=args.stas2_render_limit,
    )
    print(
        {
            "status": manifest["status"],
            "run_id": manifest["run_id"],
            "run_dir": manifest["run_dir"],
            "decision_counts_total": manifest["decision_counts_total"],
            "day_outputs": manifest["day_outputs"],
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
