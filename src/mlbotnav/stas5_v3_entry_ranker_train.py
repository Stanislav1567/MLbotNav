from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from mlbotnav.stas5_common import (
    STAS5_ARTIFACTS_DIR,
    forbidden_feature_matches,
    label_target,
    read_csv,
    rel,
    run_stamp,
    score_to_decision,
    utc_now,
    write_json,
)
from mlbotnav.stas5_entry_ranker_train import (
    _build_pipeline,
    _metrics_from_scores,
    _positive_proba,
    _prepare_feature_matrix,
)
from mlbotnav.stas5_v2_entry_ranker_train import (
    _metrics_row,
    _run_leave_one_day_scores,
    _select_feature_sets,
)
from mlbotnav.stas5_v3_leakage_guard import DEFAULT_V3_GUARD_REPORT_PATH
from mlbotnav.stas5_v3_training_dataset_builder import (
    DEFAULT_V3_TRAIN_DATASET_MANIFEST_PATH,
    DEFAULT_V3_TRAIN_DATASET_PATH,
)


STATUS = "STAS5_V3_ENTRY_RANKER_READY_REVIEW_16_20_FORWARD_21_25_NO_TP_NO_API_NO_STAS3"
MODEL_BASENAME = "stas5_v3_entry_ranker_20260501_20260520_v0"
DEFAULT_V3_MODEL_DIR = STAS5_ARTIFACTS_DIR / "v3" / "model"
DEFAULT_V3_MODEL_RUNS_DIR = DEFAULT_V3_MODEL_DIR / "runs"
DEFAULT_V3_MODEL_PATH = DEFAULT_V3_MODEL_DIR / f"{MODEL_BASENAME}.joblib"
DEFAULT_V3_MODEL_MANIFEST_PATH = DEFAULT_V3_MODEL_DIR / f"{MODEL_BASENAME}.manifest.json"
DEFAULT_V3_TRAIN_PREDICTIONS_PATH = DEFAULT_V3_MODEL_DIR / f"{MODEL_BASENAME}.train_predictions.csv"
DEFAULT_V3_ABLATION_JSON_PATH = DEFAULT_V3_MODEL_DIR / "STAS5_V3_ABLATION_20260501_20260520.json"
DEFAULT_V3_ABLATION_CSV_PATH = DEFAULT_V3_MODEL_DIR / "STAS5_V3_ABLATION_20260501_20260520.csv"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_v3_ablation_from_frames(
    *,
    dataset: pd.DataFrame,
    feature_columns: list[str],
    numeric_columns: list[str],
    categorical_columns: list[str],
    v1_feature_columns: list[str],
    enter_threshold: float = 0.65,
    unsure_threshold: float = 0.45,
) -> dict[str, Any]:
    forbidden = forbidden_feature_matches(feature_columns)
    if forbidden:
        raise ValueError(f"forbidden feature columns: {forbidden}")

    df = dataset.copy()
    df["target_keep"] = df["human_label"].map(label_target)
    train = df.dropna(subset=["target_keep"]).copy()
    train["target_keep"] = train["target_keep"].astype(int)
    if train["target_keep"].nunique() != 2:
        raise ValueError("V3 training data must contain both KEEP and CUT labels")

    feature_sets = _select_feature_sets(feature_columns=feature_columns, v1_feature_columns=v1_feature_columns)
    rows: list[dict[str, Any]] = []
    details: dict[str, Any] = {}
    for name, columns in feature_sets.items():
        subset_numeric = [column for column in numeric_columns if column in columns]
        subset_categorical = [column for column in categorical_columns if column in columns]
        scores, folds = _run_leave_one_day_scores(
            train,
            feature_columns=columns,
            numeric_columns=subset_numeric,
            categorical_columns=subset_categorical,
        )
        metrics = _metrics_from_scores(
            y_true=train["target_keep"].to_numpy(dtype=int),
            scores=scores,
            labels=train["human_label"],
            yellow_conflict=train.get("yellow_x_conflict", pd.Series(0, index=train.index)),
            days=train["day"].astype(str),
            enter_threshold=enter_threshold,
            unsure_threshold=unsure_threshold,
        )
        rows.append(
            _metrics_row(
                name,
                metrics=metrics,
                feature_count=len(columns),
                numeric_count=len(subset_numeric),
                categorical_count=len(subset_categorical),
            )
        )
        details[name] = {"feature_columns": columns, "folds": folds, "metrics": metrics}

    rows = sorted(
        rows,
        key=lambda item: (
            item["auc_leave_one_day_out"] if item["auc_leave_one_day_out"] is not None else -1.0,
            item["keep_with_yellow_x_recall_unsure_plus"],
            item["keep_recall_unsure_plus"],
        ),
        reverse=True,
    )
    return {
        "status": "STAS5_V3_ABLATION_READY",
        "created_utc": utc_now(),
        "train_policy": "V3 review train: 2026-05-01..2026-05-14 plus user-reviewed 2026-05-16..2026-05-20; no 2026-05-15; no 2026-05-21..2026-05-25.",
        "rows": int(len(train)),
        "label_counts": train["human_label"].astype(str).value_counts().to_dict(),
        "source_counts": train.get("v3_train_source", pd.Series("", index=train.index)).astype(str).value_counts().to_dict(),
        "threshold_policy": "fixed_train_policy_0p65_0p45_not_forward_tuned",
        "thresholds": {"enter": enter_threshold, "unsure": unsure_threshold},
        "feature_count": len(feature_columns),
        "v1_feature_count": len(v1_feature_columns),
        "ablation_rows": rows,
        "ablation_details": details,
        "guardrails": [
            "v3_review_labels_are_targets_not_features",
            "current_ml_score_decision_are_not_features",
            "forward_20260521_20260525_not_used_for_training_or_threshold",
            "no_postfact_future_stas3_tp_exit_features",
        ],
    }


def _write_ablation(summary: dict[str, Any], *, json_path: Path, csv_path: Path) -> None:
    write_json(json_path, summary)
    rows = pd.DataFrame(summary["ablation_rows"])
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    rows.to_csv(csv_path, index=False, encoding="utf-8-sig")


def train_v3_entry_ranker(
    *,
    dataset_path: Path = DEFAULT_V3_TRAIN_DATASET_PATH,
    dataset_manifest_path: Path = DEFAULT_V3_TRAIN_DATASET_MANIFEST_PATH,
    guard_report_path: Path = DEFAULT_V3_GUARD_REPORT_PATH,
    model_path: Path = DEFAULT_V3_MODEL_PATH,
    manifest_path: Path = DEFAULT_V3_MODEL_MANIFEST_PATH,
    predictions_path: Path = DEFAULT_V3_TRAIN_PREDICTIONS_PATH,
    ablation_json_path: Path = DEFAULT_V3_ABLATION_JSON_PATH,
    ablation_csv_path: Path = DEFAULT_V3_ABLATION_CSV_PATH,
    model_feature_set: str = "full_v2_all_274",
    enter_threshold: float = 0.65,
    unsure_threshold: float = 0.45,
    strict: bool = True,
) -> tuple[dict[str, Any], pd.DataFrame]:
    feature_manifest = _load_json(dataset_manifest_path)
    if strict and feature_manifest.get("status") != "PASS":
        raise ValueError(f"V3 dataset manifest status is not PASS: {feature_manifest.get('status')}")
    guard_status = None
    if guard_report_path.exists():
        guard_status = _load_json(guard_report_path).get("status")
        if strict and guard_status != "PASS":
            raise ValueError(f"V3 leakage guard status is not PASS: {guard_status}")
    elif strict:
        raise FileNotFoundError(f"V3 leakage guard report not found: {guard_report_path}")

    feature_columns = [str(column) for column in feature_manifest["feature_columns"]]
    numeric_columns = [str(column) for column in feature_manifest.get("numeric_columns", []) if str(column) in feature_columns]
    categorical_columns = [str(column) for column in feature_manifest.get("categorical_columns", []) if str(column) in feature_columns]
    v1_feature_columns = [str(column) for column in feature_manifest.get("v1_feature_columns", []) if str(column) in feature_columns]
    forbidden = forbidden_feature_matches(feature_columns)
    if forbidden:
        raise ValueError(f"forbidden feature columns: {forbidden}")

    dataset = read_csv(dataset_path)
    ablation = run_v3_ablation_from_frames(
        dataset=dataset,
        feature_columns=feature_columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        v1_feature_columns=v1_feature_columns,
        enter_threshold=enter_threshold,
        unsure_threshold=unsure_threshold,
    )
    _write_ablation(ablation, json_path=ablation_json_path, csv_path=ablation_csv_path)

    feature_sets = _select_feature_sets(feature_columns=feature_columns, v1_feature_columns=v1_feature_columns)
    if model_feature_set not in feature_sets:
        raise ValueError(f"unknown model feature set: {model_feature_set}")
    selected_features = feature_sets[model_feature_set]
    selected_numeric = [column for column in numeric_columns if column in selected_features]
    selected_categorical = [column for column in categorical_columns if column in selected_features]

    df = dataset.copy()
    df["target_keep"] = df["human_label"].map(label_target)
    train = df.dropna(subset=["target_keep"]).copy()
    train["target_keep"] = train["target_keep"].astype(int)
    if train["target_keep"].nunique() != 2:
        raise ValueError("V3 training data must contain both KEEP and CUT labels")

    oof, folds = _run_leave_one_day_scores(
        train,
        feature_columns=selected_features,
        numeric_columns=selected_numeric,
        categorical_columns=selected_categorical,
    )
    x = _prepare_feature_matrix(
        train,
        feature_columns=selected_features,
        numeric_columns=selected_numeric,
        categorical_columns=selected_categorical,
    )
    y = train["target_keep"].to_numpy(dtype=int)
    final_model = _build_pipeline(numeric_columns=selected_numeric, categorical_columns=selected_categorical)
    final_model.fit(x, y)
    train_scores = _positive_proba(final_model, x)
    metrics = _metrics_from_scores(
        y_true=y,
        scores=oof,
        labels=train["human_label"],
        yellow_conflict=train.get("yellow_x_conflict", pd.Series(0, index=train.index)),
        days=train["day"].astype(str),
        enter_threshold=enter_threshold,
        unsure_threshold=unsure_threshold,
    )

    prediction_columns = [
        "day",
        "candidate_id",
        "record_id",
        "entry_time_utc",
        "entry_open_price",
        "entry_price_5bps",
        "human_label",
        "label_status",
        "label_source",
        "yellow_x",
        "yellow_x_conflict",
        "v3_train_source",
        "v3_user_review_label",
        "v3_user_review_reason",
        "v3_train_usage",
    ]
    predictions = train[[column for column in prediction_columns if column in train.columns]].copy()
    predictions["oof_ml_keep_score_v3"] = oof
    predictions["train_fit_ml_keep_score_v3"] = train_scores
    predictions["ml_decision_v3"] = [
        score_to_decision(score, enter_threshold=enter_threshold, unsure_threshold=unsure_threshold) for score in oof
    ]
    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(predictions_path, index=False, encoding="utf-8-sig")

    package = {
        "pipeline": final_model,
        "feature_columns": selected_features,
        "numeric_columns": selected_numeric,
        "categorical_columns": selected_categorical,
        "thresholds": {"enter": enter_threshold, "unsure": unsure_threshold},
        "model_id": "STAS5_V3_ENTRY_RANKER_REVIEW_16_20_FULL274",
        "model_feature_set": model_feature_set,
        "ablation_json_path": rel(ablation_json_path),
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(package, model_path)

    manifest = {
        "status": STATUS,
        "created_utc": utc_now(),
        "run_id": model_path.parent.name if model_path.parent.name else "",
        "run_dir": rel(model_path.parent),
        "model_id": package["model_id"],
        "model_path": rel(model_path),
        "predictions_path": rel(predictions_path),
        "dataset_path": rel(dataset_path),
        "dataset_manifest_path": rel(dataset_manifest_path),
        "guard_report_path": rel(guard_report_path),
        "guard_status": guard_status,
        "train_policy": feature_manifest.get("train_policy"),
        "train_days": feature_manifest.get("train_days"),
        "excluded_days": feature_manifest.get("excluded_days"),
        "holdout_days": feature_manifest.get("holdout_days"),
        "label_counts": feature_manifest.get("label_counts"),
        "source_counts": feature_manifest.get("source_counts"),
        "model_type": "LogisticRegression(class_weight=balanced)",
        "model_feature_set": model_feature_set,
        "feature_columns": selected_features,
        "feature_count": len(selected_features),
        "numeric_columns": selected_numeric,
        "categorical_columns": selected_categorical,
        "thresholds": package["thresholds"],
        "folds": folds,
        "metrics": metrics,
        "ablation_json_path": rel(ablation_json_path),
        "ablation_csv_path": rel(ablation_csv_path),
        "ablation_top_rows": ablation["ablation_rows"][:5],
        "guardrails": [
            "uses_full274_by_default",
            "review_16_20_used_as_human_targets",
            "20260515_excluded",
            "20260521_20260525_holdout_not_used",
            "no_forward_threshold_tuning",
            "no_tp_stas3_exit_api",
        ],
    }
    write_json(manifest_path, manifest)
    return manifest, predictions


def _run_paths(run_id: str, run_root: Path) -> dict[str, Path]:
    run_dir = run_root / run_id
    return {
        "run_dir": run_dir,
        "model_path": run_dir / f"{MODEL_BASENAME}.joblib",
        "manifest_path": run_dir / f"{MODEL_BASENAME}.manifest.json",
        "predictions_path": run_dir / f"{MODEL_BASENAME}.train_predictions.csv",
        "ablation_json_path": run_dir / "STAS5_V3_ABLATION_20260501_20260520.json",
        "ablation_csv_path": run_dir / "STAS5_V3_ABLATION_20260501_20260520.csv",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Train STAS5 V3 entry ranker on original 14d plus user-reviewed 16-20.")
    parser.add_argument("--dataset-path", default=str(DEFAULT_V3_TRAIN_DATASET_PATH))
    parser.add_argument("--dataset-manifest-path", default=str(DEFAULT_V3_TRAIN_DATASET_MANIFEST_PATH))
    parser.add_argument("--guard-report-path", default=str(DEFAULT_V3_GUARD_REPORT_PATH))
    parser.add_argument("--run-id", default="")
    parser.add_argument("--run-root", default=str(DEFAULT_V3_MODEL_RUNS_DIR))
    parser.add_argument("--model-path", default="")
    parser.add_argument("--manifest-path", default="")
    parser.add_argument("--predictions-path", default="")
    parser.add_argument("--ablation-json-path", default="")
    parser.add_argument("--ablation-csv-path", default="")
    parser.add_argument("--model-feature-set", default="full_v2_all_274")
    parser.add_argument("--enter-threshold", type=float, default=0.65)
    parser.add_argument("--unsure-threshold", type=float, default=0.45)
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()

    run_id = args.run_id or f"stas5_v3_train_{run_stamp()}"
    paths = _run_paths(run_id, Path(args.run_root))
    manifest, _predictions = train_v3_entry_ranker(
        dataset_path=Path(args.dataset_path),
        dataset_manifest_path=Path(args.dataset_manifest_path),
        guard_report_path=Path(args.guard_report_path),
        model_path=Path(args.model_path) if args.model_path else paths["model_path"],
        manifest_path=Path(args.manifest_path) if args.manifest_path else paths["manifest_path"],
        predictions_path=Path(args.predictions_path) if args.predictions_path else paths["predictions_path"],
        ablation_json_path=Path(args.ablation_json_path) if args.ablation_json_path else paths["ablation_json_path"],
        ablation_csv_path=Path(args.ablation_csv_path) if args.ablation_csv_path else paths["ablation_csv_path"],
        model_feature_set=args.model_feature_set,
        enter_threshold=args.enter_threshold,
        unsure_threshold=args.unsure_threshold,
        strict=not args.no_strict,
    )
    write_json(
        DEFAULT_V3_MODEL_DIR / "STAS5_V3_LATEST_MODEL_RUN.json",
        {
            "status": "LATEST_MODEL_RUN_POINTER",
            "created_utc": utc_now(),
            "run_id": run_id,
            "run_dir": manifest["run_dir"],
            "model_path": manifest["model_path"],
            "manifest_path": rel(Path(args.manifest_path) if args.manifest_path else paths["manifest_path"]),
        },
    )
    print(
        {
            "status": manifest["status"],
            "run_id": run_id,
            "run_dir": manifest["run_dir"],
            "model_path": manifest["model_path"],
            "feature_count": manifest["feature_count"],
            "metrics": manifest["metrics"],
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
