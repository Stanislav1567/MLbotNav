from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from mlbotnav.stas5_common import (
    DEFAULT_AUDIT_JSON_PATH,
    DEFAULT_FEATURE_MANIFEST_PATH,
    DEFAULT_FEATURE_PATH,
    DEFAULT_GUARD_REPORT_PATH,
    DEFAULT_MODEL_MANIFEST_PATH,
    DEFAULT_MODEL_PATH,
    DEFAULT_TRAIN_PREDICTIONS_PATH,
    STATUS_CURRENT,
    forbidden_feature_matches,
    label_target,
    read_csv,
    rel,
    score_to_decision,
    utc_now,
    write_json,
)


def _load_feature_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _prepare_feature_matrix(df: pd.DataFrame, *, feature_columns: list[str], numeric_columns: list[str], categorical_columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for column in feature_columns:
        if column not in out:
            out[column] = pd.NA
    for column in numeric_columns:
        out[column] = pd.to_numeric(out[column], errors="coerce")
    for column in categorical_columns:
        out[column] = out[column].astype("string")
    return out[feature_columns]


def _build_pipeline(*, numeric_columns: list[str], categorical_columns: list[str]) -> Pipeline:
    numeric_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler(with_mean=False)),
        ]
    )
    categorical_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="__MISSING__")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
        ]
    )
    transformers = []
    if numeric_columns:
        transformers.append(("num", numeric_pipe, numeric_columns))
    if categorical_columns:
        transformers.append(("cat", categorical_pipe, categorical_columns))
    return Pipeline(
        steps=[
            ("preprocess", ColumnTransformer(transformers=transformers, remainder="drop")),
            ("model", LogisticRegression(max_iter=2000, class_weight="balanced", solver="liblinear", random_state=42)),
        ]
    )


def _positive_proba(model: Pipeline, x: pd.DataFrame) -> np.ndarray:
    proba = model.predict_proba(x)
    classes = list(model.named_steps["model"].classes_)
    if 1 in classes:
        return proba[:, classes.index(1)]
    return np.zeros(len(x), dtype=float)


def _metrics_from_scores(
    *,
    y_true: np.ndarray,
    scores: np.ndarray,
    labels: pd.Series,
    yellow_conflict: pd.Series,
    days: pd.Series,
    enter_threshold: float,
    unsure_threshold: float,
) -> dict[str, Any]:
    decisions = np.array([score_to_decision(score, enter_threshold=enter_threshold, unsure_threshold=unsure_threshold) for score in scores])
    keep_mask = y_true == 1
    cut_mask = y_true == 0
    enter_mask = decisions == "ENTER"
    unsure_plus_mask = np.isin(decisions, ["ENTER", "UNSURE"])
    skip_mask = decisions == "SKIP"
    yellow_keep_mask = keep_mask & yellow_conflict.astype(int).to_numpy().astype(bool)

    try:
        auc = float(roc_auc_score(y_true, scores))
    except Exception:
        auc = None

    by_day: list[dict[str, Any]] = []
    for day in sorted(days.astype(str).unique()):
        idx = days.astype(str) == day
        day_y = y_true[idx.to_numpy()]
        day_d = decisions[idx.to_numpy()]
        by_day.append(
            {
                "day": day,
                "rows": int(idx.sum()),
                "keep": int((day_y == 1).sum()),
                "cut": int((day_y == 0).sum()),
                "ENTER": int((day_d == "ENTER").sum()),
                "UNSURE": int((day_d == "UNSURE").sum()),
                "SKIP": int((day_d == "SKIP").sum()),
                "keep_recall_enter": round(float(((day_y == 1) & (day_d == "ENTER")).sum()) / max(int((day_y == 1).sum()), 1), 6),
                "keep_recall_unsure_plus": round(float(((day_y == 1) & np.isin(day_d, ["ENTER", "UNSURE"])).sum()) / max(int((day_y == 1).sum()), 1), 6),
            }
        )

    score_distribution = {
        "min": round(float(np.nanmin(scores)), 8),
        "p10": round(float(np.nanquantile(scores, 0.10)), 8),
        "p25": round(float(np.nanquantile(scores, 0.25)), 8),
        "p50": round(float(np.nanquantile(scores, 0.50)), 8),
        "p75": round(float(np.nanquantile(scores, 0.75)), 8),
        "p90": round(float(np.nanquantile(scores, 0.90)), 8),
        "max": round(float(np.nanmax(scores)), 8),
    }
    return {
        "auc_leave_one_day_out": auc,
        "thresholds": {"ENTER": enter_threshold, "UNSURE": unsure_threshold},
        "rows": int(len(y_true)),
        "keep": int(keep_mask.sum()),
        "cut": int(cut_mask.sum()),
        "decision_counts": {decision: int((decisions == decision).sum()) for decision in ["ENTER", "UNSURE", "SKIP"]},
        "keep_recall_enter": round(float((keep_mask & enter_mask).sum()) / max(int(keep_mask.sum()), 1), 6),
        "keep_recall_unsure_plus": round(float((keep_mask & unsure_plus_mask).sum()) / max(int(keep_mask.sum()), 1), 6),
        "cut_precision_skip": round(float((cut_mask & skip_mask).sum()) / max(int(skip_mask.sum()), 1), 6),
        "keep_with_yellow_x": int(yellow_keep_mask.sum()),
        "keep_with_yellow_x_recall_enter": round(float((yellow_keep_mask & enter_mask).sum()) / max(int(yellow_keep_mask.sum()), 1), 6),
        "keep_with_yellow_x_recall_unsure_plus": round(float((yellow_keep_mask & unsure_plus_mask).sum()) / max(int(yellow_keep_mask.sum()), 1), 6),
        "score_distribution": score_distribution,
        "by_day": by_day,
        "label_counts": labels.astype(str).value_counts().to_dict(),
    }


def train_entry_ranker(
    *,
    feature_path: Path = DEFAULT_FEATURE_PATH,
    feature_manifest_path: Path = DEFAULT_FEATURE_MANIFEST_PATH,
    guard_report_path: Path = DEFAULT_GUARD_REPORT_PATH,
    audit_json_path: Path = DEFAULT_AUDIT_JSON_PATH,
    model_path: Path = DEFAULT_MODEL_PATH,
    manifest_path: Path = DEFAULT_MODEL_MANIFEST_PATH,
    predictions_path: Path = DEFAULT_TRAIN_PREDICTIONS_PATH,
    enter_threshold: float = 0.65,
    unsure_threshold: float = 0.45,
    allow_missing_audit: bool = False,
    strict: bool = True,
) -> tuple[Pipeline, dict[str, Any], pd.DataFrame]:
    feature_manifest = _load_feature_manifest(feature_manifest_path)
    feature_columns = [str(column) for column in feature_manifest["feature_columns"]]
    numeric_columns = [str(column) for column in feature_manifest.get("numeric_columns", []) if str(column) in feature_columns]
    categorical_columns = [str(column) for column in feature_manifest.get("categorical_columns", []) if str(column) in feature_columns]
    forbidden = forbidden_feature_matches(feature_columns)
    if forbidden:
        raise ValueError(f"forbidden feature columns: {forbidden}")

    guard_status = None
    if guard_report_path.exists():
        guard_status = json.loads(guard_report_path.read_text(encoding="utf-8")).get("status")
        if strict and guard_status != "PASS":
            raise ValueError(f"leakage guard status is not PASS: {guard_status}")

    audit_status = None
    if audit_json_path.exists():
        audit_status = json.loads(audit_json_path.read_text(encoding="utf-8")).get("status")
        if strict and audit_status != "READY_FOR_CONTROLLED_BASELINE":
            raise ValueError(f"pre-ML audit status is not READY_FOR_CONTROLLED_BASELINE: {audit_status}")
    elif strict and not allow_missing_audit:
        raise FileNotFoundError(f"pre-ML audit json not found: {audit_json_path}")

    df = read_csv(feature_path)
    df["target_keep"] = df["human_label"].map(label_target)
    train = df.dropna(subset=["target_keep"]).copy()
    train["target_keep"] = train["target_keep"].astype(int)
    if (train["day"].astype(str) > "2026-05-14").any():
        raise ValueError("forward days detected in training data")
    if train["target_keep"].nunique() != 2:
        raise ValueError("training data must contain both KEEP and CUT labels")

    x = _prepare_feature_matrix(train, feature_columns=feature_columns, numeric_columns=numeric_columns, categorical_columns=categorical_columns)
    y = train["target_keep"].to_numpy(dtype=int)
    days = train["day"].astype(str)

    oof = np.full(len(train), np.nan, dtype=float)
    folds: list[dict[str, Any]] = []
    for day in sorted(days.unique()):
        val_mask = days == day
        train_mask = ~val_mask
        if len(set(y[train_mask.to_numpy()])) < 2:
            continue
        model = _build_pipeline(numeric_columns=numeric_columns, categorical_columns=categorical_columns)
        model.fit(x.loc[train_mask], y[train_mask.to_numpy()])
        fold_scores = _positive_proba(model, x.loc[val_mask])
        oof[val_mask.to_numpy()] = fold_scores
        folds.append({"day": day, "train_rows": int(train_mask.sum()), "validation_rows": int(val_mask.sum())})
    if np.isnan(oof).any():
        raise ValueError("leave-one-day-out did not produce scores for all rows")

    final_model = _build_pipeline(numeric_columns=numeric_columns, categorical_columns=categorical_columns)
    final_model.fit(x, y)
    train_scores = _positive_proba(final_model, x)

    metrics = _metrics_from_scores(
        y_true=y,
        scores=oof,
        labels=train["human_label"],
        yellow_conflict=train.get("yellow_x_conflict", pd.Series(0, index=train.index)),
        days=days,
        enter_threshold=enter_threshold,
        unsure_threshold=unsure_threshold,
    )
    predictions = train[
        [
            "day",
            "candidate_id",
            "record_id",
            "entry_time_utc",
            "entry_open_price",
            "entry_price_5bps",
            "human_label",
            "label_status",
            "yellow_x",
            "yellow_x_conflict",
        ]
    ].copy()
    predictions["oof_ml_keep_score"] = oof
    predictions["train_fit_ml_keep_score"] = train_scores
    predictions["ml_decision"] = [score_to_decision(score, enter_threshold=enter_threshold, unsure_threshold=unsure_threshold) for score in oof]
    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(predictions_path, index=False, encoding="utf-8-sig")

    package = {
        "pipeline": final_model,
        "feature_columns": feature_columns,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "thresholds": {"enter": enter_threshold, "unsure": unsure_threshold},
        "model_id": "STAS5_ENTRY_RANKER_V0_CONTROLLED_BASELINE",
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(package, model_path)

    manifest = {
        "status": "CONTROLLED_BASELINE_READY",
        "pipeline_status": STATUS_CURRENT,
        "created_utc": utc_now(),
        "model_id": package["model_id"],
        "model_path": rel(model_path),
        "predictions_path": rel(predictions_path),
        "feature_path": rel(feature_path),
        "feature_manifest_path": rel(feature_manifest_path),
        "guard_status": guard_status,
        "audit_status": audit_status,
        "train_window": {"start_day": "2026-05-01", "end_day": "2026-05-14"},
        "forward_window_policy": "2026-05-15+ is never used for training or threshold tuning",
        "label_status_warning": "DRAFT_REVIEW_ONLY: labels are KEEP_DRAFT/CUT_DRAFT, not final approved production labels",
        "model_type": "LogisticRegression(class_weight=balanced)",
        "feature_columns": feature_columns,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "thresholds": package["thresholds"],
        "folds": folds,
        "metrics": metrics,
        "guardrails": [
            "no_yellow_x_in_feature_columns",
            "no_strategy_vote_in_feature_columns",
            "no_future_outcome_in_feature_columns",
            "no_stas3_tp_exit_in_feature_columns",
            "leave_one_day_out_only_inside_train_window",
            "forward_days_not_used_for_threshold",
        ],
    }
    write_json(manifest_path, manifest)
    return final_model, manifest, predictions


def main() -> int:
    parser = argparse.ArgumentParser(description="Train STAS5 controlled baseline entry ranker.")
    parser.add_argument("--feature-path", default=str(DEFAULT_FEATURE_PATH))
    parser.add_argument("--feature-manifest-path", default=str(DEFAULT_FEATURE_MANIFEST_PATH))
    parser.add_argument("--guard-report-path", default=str(DEFAULT_GUARD_REPORT_PATH))
    parser.add_argument("--audit-json-path", default=str(DEFAULT_AUDIT_JSON_PATH))
    parser.add_argument("--model-path", default=str(DEFAULT_MODEL_PATH))
    parser.add_argument("--manifest-path", default=str(DEFAULT_MODEL_MANIFEST_PATH))
    parser.add_argument("--predictions-path", default=str(DEFAULT_TRAIN_PREDICTIONS_PATH))
    parser.add_argument("--enter-threshold", type=float, default=0.65)
    parser.add_argument("--unsure-threshold", type=float, default=0.45)
    parser.add_argument("--allow-missing-audit", action="store_true")
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()

    _model, manifest, _predictions = train_entry_ranker(
        feature_path=Path(args.feature_path),
        feature_manifest_path=Path(args.feature_manifest_path),
        guard_report_path=Path(args.guard_report_path),
        audit_json_path=Path(args.audit_json_path),
        model_path=Path(args.model_path),
        manifest_path=Path(args.manifest_path),
        predictions_path=Path(args.predictions_path),
        enter_threshold=args.enter_threshold,
        unsure_threshold=args.unsure_threshold,
        allow_missing_audit=args.allow_missing_audit,
        strict=not args.no_strict,
    )
    print(
        {
            "status": manifest["status"],
            "model_path": manifest["model_path"],
            "metrics": manifest["metrics"],
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
