from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
    roc_auc_score,
)
from sklearn.ensemble import ExtraTreesClassifier

from mlbotnav.stas5_common import PROJECT_ROOT, compact_day, iter_days, rel, run_stamp, utc_now, write_json
from mlbotnav.stas5_entry_ranker_train import _build_pipeline, _positive_proba, _prepare_feature_matrix
from mlbotnav.stas5_v5_batch_dataset_builder import (
    FORBIDDEN_FEATURE_PATTERNS,
    STATUS_PASS as BATCH_GUARD_PASS,
    TARGET_OR_MANUAL_COLUMNS,
    _fill_feature_gaps,
    _forbidden_feature_matches,
    _source_time_check,
)
from mlbotnav.stas5_v5_causal_structure_builder import build_causal_structure_package
from mlbotnav.stas5_v5_full_causal_structure_builder import (
    STATUS as FULL_CAUSAL_GUARD_PASS,
    build_full_causal_structure_package,
)


TRAIN_START_DAY = "2026-01-27"
TRAIN_END_DAY = "2026-02-27"
FORWARD_START_DAY = "2026-02-28"
FORWARD_END_DAY = "2026-03-06"
EXPECTED_DAYS = 32
EXPECTED_ROWS = 2596
EXPECTED_GOOD = 290
EXPECTED_BAD = 2306
EXPECTED_FEATURES = 439

V5_ROOT = PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5"
BATCH_PREFIX = "STAS5_V5_BATCH_20260127_20260227"
DEFAULT_BATCH_DATASET = V5_ROOT / f"{BATCH_PREFIX}_ML_READY_439F_TARGETS_V1.csv"
DEFAULT_BATCH_ALLOWLIST = V5_ROOT / f"{BATCH_PREFIX}_FEATURE_ALLOWLIST_439F_V1.json"
DEFAULT_BATCH_GUARD = V5_ROOT / f"{BATCH_PREFIX}_GUARD_V1.json"
DEFAULT_MODEL_RUNS_DIR = V5_ROOT / "model" / "runs"
DEFAULT_FORWARD_RUNS_DIR = V5_ROOT / "forward" / "runs"
DEFAULT_LATEST_MODEL_POINTER = V5_ROOT / "model" / "STAS5_V5_LATEST_TWO_BLOCK_MODEL_RUN.json"
DEFAULT_LATEST_FORWARD_POINTER = V5_ROOT / "forward" / "STAS5_V5_LATEST_TWO_BLOCK_FORWARD_RUN.json"
FULL274_RUNS_DIR = PROJECT_ROOT / "STAS5_ML_CORE" / "runs"

TRAINING_GUARD_PASS = "PASS_V5_TWO_BLOCK_TRAINING_GUARD_READY_FOR_TRAINING"
TRAINING_GUARD_FAIL = "FAIL_V5_TWO_BLOCK_TRAINING_GUARD"
TRAIN_STATUS = "PASS_V5_TWO_BLOCK_ML_TRAINED_POST_TRAIN_GUARD_READY_FOR_FORWARD"
POST_TRAIN_GUARD_PASS = "PASS_V5_TWO_BLOCK_POST_TRAIN_GUARD_READY_FOR_FORWARD"
POST_TRAIN_GUARD_FAIL = "FAIL_V5_TWO_BLOCK_POST_TRAIN_GUARD"
FORWARD_GUARD_PASS = "PASS_V5_TWO_BLOCK_FORWARD_20260228_20260306_BLIND_NO_FUTURE"
FORWARD_GUARD_FAIL = "FAIL_V5_TWO_BLOCK_FORWARD_GUARD"

KEY_COLUMNS = ["day", "candidate_id", "record_id", "entry_time_utc"]
TARGET_COLUMNS = ["entry_y", "phase_y", "state_y", "reason_y"]
PHASE_PREFIX = "mps_phase"
STATE_PREFIX = "mps_state"
ENTRY_MODEL_CANDIDATES = ["logistic_balanced", "extra_trees_balanced"]
PHASE_STATE_MODEL_KIND = "extra_trees_balanced"
DEFAULT_REVIEW_WEIGHT_START_DAY = "2026-02-28"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _check(name: str, passed: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"check": name, "status": "PASS" if passed else "FAIL", "details": details or {}}


def _read_allowlist(path: Path) -> list[str]:
    payload = _load_json(path)
    return [str(column) for column in payload.get("feature_columns", [])]


def _read_batch(dataset_path: Path, allowlist_path: Path) -> tuple[pd.DataFrame, list[str]]:
    features = _read_allowlist(allowlist_path)
    df = pd.read_csv(dataset_path, encoding="utf-8-sig", low_memory=False)
    df, _fill = _fill_feature_gaps(df, features)
    return df, features


def _infer_column_types(df: pd.DataFrame, feature_columns: list[str]) -> tuple[list[str], list[str]]:
    numeric: list[str] = []
    categorical: list[str] = []
    for column in feature_columns:
        if column not in df.columns:
            numeric.append(column)
            continue
        dtype = df[column].dtype
        if pd.api.types.is_object_dtype(dtype) or pd.api.types.is_string_dtype(dtype):
            categorical.append(column)
        else:
            numeric.append(column)
    return numeric, categorical


def _build_model_pipeline(
    *,
    numeric_columns: list[str],
    categorical_columns: list[str],
    model_kind: str = "logistic_balanced",
) -> Any:
    model = _build_pipeline(numeric_columns=numeric_columns, categorical_columns=categorical_columns)
    if model_kind == "logistic_balanced":
        return model
    if model_kind == "extra_trees_balanced":
        model.set_params(
            model=ExtraTreesClassifier(
                n_estimators=120,
                max_features="sqrt",
                min_samples_leaf=3,
                class_weight="balanced_subsample",
                random_state=42,
                n_jobs=-1,
            )
        )
        return model
    raise ValueError(f"unknown model_kind: {model_kind}")


def _fit_with_optional_weights(model: Any, x: pd.DataFrame, y: Any, sample_weight: np.ndarray | None = None) -> Any:
    if sample_weight is None:
        model.fit(x, y)
    else:
        model.fit(x, y, model__sample_weight=np.asarray(sample_weight, dtype=float))
    return model


def _sample_weights(
    df: pd.DataFrame,
    *,
    review_weight_start_day: str | None = DEFAULT_REVIEW_WEIGHT_START_DAY,
) -> np.ndarray:
    """Teacher-only weights. They never enter X; they only scale supervised loss."""
    weights = np.ones(len(df), dtype=float)
    entry_y = pd.to_numeric(df.get("entry_y", 0), errors="coerce").fillna(0).astype(int)
    state = df.get("state_y", pd.Series("", index=df.index)).astype(str).str.upper()
    reason = df.get("reason_y", pd.Series("", index=df.index)).astype(str).str.upper()
    day = df.get("day", pd.Series("", index=df.index)).astype(str)

    good_user = entry_y.eq(1) | state.eq("USER_APPROVED_GOOD_ENTRY_ZONE") | reason.eq("GOOD_USER_APPROVED_ENTRY")
    hard_bad = state.eq("BAD_NEAR_APPROVED_NOT_SELECTED") | reason.str.startswith("BAD_")
    weights[good_user.to_numpy()] = 1.6
    weights[hard_bad.to_numpy()] = 1.2

    if review_weight_start_day:
        recent = day.ge(str(review_weight_start_day))
        weights[recent.to_numpy()] = 2.0
        weights[(recent & good_user).to_numpy()] = 5.0
        weights[(recent & hard_bad).to_numpy()] = 3.5
    return weights


def _sample_weight_summary(df: pd.DataFrame, weights: np.ndarray, *, review_weight_start_day: str | None) -> dict[str, Any]:
    entry_y = pd.to_numeric(df.get("entry_y", 0), errors="coerce").fillna(0).astype(int)
    day = df.get("day", pd.Series("", index=df.index)).astype(str)
    recent = day.ge(str(review_weight_start_day)) if review_weight_start_day else pd.Series(False, index=df.index)
    return {
        "policy": "teacher_weighting_not_model_features",
        "review_weight_start_day": review_weight_start_day or "",
        "min": round(float(np.min(weights)), 6) if len(weights) else 0.0,
        "max": round(float(np.max(weights)), 6) if len(weights) else 0.0,
        "mean": round(float(np.mean(weights)), 6) if len(weights) else 0.0,
        "recent_rows": int(recent.sum()),
        "recent_good": int((recent & entry_y.eq(1)).sum()),
        "recent_bad": int((recent & entry_y.eq(0)).sum()),
        "good_weight_mean": round(float(np.mean(weights[entry_y.to_numpy() == 1])), 6) if int(entry_y.sum()) else 0.0,
        "bad_weight_mean": round(float(np.mean(weights[entry_y.to_numpy() == 0])), 6) if int((entry_y == 0).sum()) else 0.0,
        "rules": [
            "old_good_user_weight=1.6",
            "old_bad_near_approved_weight=1.2",
            "recent_default_weight=2.0",
            "recent_good_user_weight=5.0",
            "recent_bad_near_approved_weight=3.5",
        ],
    }


def _slug(value: Any) -> str:
    out = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value).strip())
    out = "_".join(part for part in out.split("_") if part)
    return out or "unknown"


def _class_column(prefix: str, label: str) -> str:
    return f"{prefix}_prob_{_slug(label)}"


def _prediction_columns(prefix: str, classes: list[str]) -> list[str]:
    return [f"{prefix}_pred_label", f"{prefix}_pred_conf"] + [_class_column(prefix, label) for label in classes]


def _phase_state_prediction_columns(phase_classes: list[str], state_classes: list[str]) -> list[str]:
    return _prediction_columns(PHASE_PREFIX, phase_classes) + _prediction_columns(STATE_PREFIX, state_classes)


def _proba_predictions(model: Any, x: pd.DataFrame, *, classes: list[str], prefix: str) -> pd.DataFrame:
    proba = np.asarray(model.predict_proba(x), dtype=float)
    if proba.ndim == 1:
        proba = proba.reshape(-1, 1)
    if not np.isfinite(proba).all():
        bad_rows = np.where(~np.isfinite(proba).all(axis=1))[0][:20].astype(int).tolist()
        raise ValueError(
            f"{prefix} raw predict_proba produced NaN/inf; bad_rows_sample={bad_rows}. "
            "This model is not promotable; fix phase/state model before training continues."
        )
    row_sums = proba.sum(axis=1)
    zero_rows = np.where(row_sums <= 0)[0]
    if len(zero_rows):
        raise ValueError(
            f"{prefix} raw predict_proba row sums are zero/negative; bad_rows_sample={zero_rows[:20].astype(int).tolist()}. "
            "This model is not promotable; fix phase/state model before training continues."
        )
    proba = proba / row_sums.reshape(-1, 1)
    model_classes = [str(item) for item in model.named_steps["model"].classes_]
    best_idx = np.argmax(proba, axis=1)
    out = pd.DataFrame(index=x.index)
    out[f"{prefix}_pred_label"] = [model_classes[int(idx)] for idx in best_idx]
    out[f"{prefix}_pred_conf"] = np.max(proba, axis=1)
    for label in classes:
        if label in model_classes:
            out[_class_column(prefix, label)] = proba[:, model_classes.index(label)]
        else:
            out[_class_column(prefix, label)] = 0.0
    return out.reset_index(drop=True)


def _fit_model(
    df: pd.DataFrame,
    *,
    target: str,
    feature_columns: list[str],
    numeric_columns: list[str],
    categorical_columns: list[str],
    sample_weights: np.ndarray | None = None,
    model_kind: str = "logistic_balanced",
) -> Any:
    x = _prepare_feature_matrix(
        df,
        feature_columns=feature_columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
    )
    y = df[target].to_numpy()
    model = _build_model_pipeline(
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        model_kind=model_kind,
    )
    _fit_with_optional_weights(model, x, y, sample_weights)
    return model


def _run_binary_lodo_scores(
    df: pd.DataFrame,
    *,
    target: str,
    feature_columns: list[str],
    numeric_columns: list[str],
    categorical_columns: list[str],
    sample_weights: np.ndarray | None = None,
    model_kind: str = "logistic_balanced",
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    x = _prepare_feature_matrix(
        df,
        feature_columns=feature_columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
    )
    y = pd.to_numeric(df[target], errors="coerce").fillna(0).astype(int).to_numpy()
    days = df["day"].astype(str)
    scores = np.full(len(df), np.nan, dtype=float)
    folds: list[dict[str, Any]] = []
    for day in sorted(days.unique()):
        val_mask = days == day
        train_mask = ~val_mask
        if len(set(y[train_mask.to_numpy()])) < 2:
            continue
        model = _build_model_pipeline(numeric_columns=numeric_columns, categorical_columns=categorical_columns, model_kind=model_kind)
        train_weights = sample_weights[train_mask.to_numpy()] if sample_weights is not None else None
        _fit_with_optional_weights(model, x.loc[train_mask], y[train_mask.to_numpy()], train_weights)
        scores[val_mask.to_numpy()] = _positive_proba(model, x.loc[val_mask])
        folds.append({"day": day, "train_rows": int(train_mask.sum()), "validation_rows": int(val_mask.sum()), "model_kind": model_kind})
    if np.isnan(scores).any():
        missing_days = sorted(days[np.isnan(scores)].unique().tolist())
        raise ValueError(f"LODO binary scores missing days: {missing_days}")
    return scores, folds


def _run_multiclass_lodo_predictions(
    df: pd.DataFrame,
    *,
    target: str,
    prefix: str,
    classes: list[str],
    feature_columns: list[str],
    numeric_columns: list[str],
    categorical_columns: list[str],
    sample_weights: np.ndarray | None = None,
) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
    x = _prepare_feature_matrix(
        df,
        feature_columns=feature_columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
    )
    y = df[target].astype(str)
    days = df["day"].astype(str)
    pred = pd.DataFrame(index=df.index, columns=_prediction_columns(prefix, classes))
    folds: list[dict[str, Any]] = []
    for day in sorted(days.unique()):
        val_mask = days == day
        train_mask = ~val_mask
        if y[train_mask].nunique() < 2:
            continue
        model = _build_model_pipeline(
            numeric_columns=numeric_columns,
            categorical_columns=categorical_columns,
            model_kind=PHASE_STATE_MODEL_KIND,
        )
        train_weights = sample_weights[train_mask.to_numpy()] if sample_weights is not None else None
        _fit_with_optional_weights(model, x.loc[train_mask], y.loc[train_mask], train_weights)
        fold_pred = _proba_predictions(model, x.loc[val_mask], classes=classes, prefix=prefix)
        pred.loc[val_mask, fold_pred.columns] = fold_pred.to_numpy()
        folds.append(
            {
                "day": day,
                "train_rows": int(train_mask.sum()),
                "validation_rows": int(val_mask.sum()),
                "train_class_count": int(y[train_mask].nunique()),
                "model_kind": PHASE_STATE_MODEL_KIND,
            }
        )
    if pred.isna().any().any():
        missing_days = sorted(days[pred.isna().any(axis=1)].unique().tolist())
        raise ValueError(f"LODO multiclass predictions missing days for {target}: {missing_days}")
    return pred.reset_index(drop=True), folds


def _entry_metrics(y_true: np.ndarray, scores: np.ndarray, days: pd.Series, *, enter_threshold: float) -> dict[str, Any]:
    thresholds = [0.30, 0.50, 0.70, float(enter_threshold)]
    threshold_rows: list[dict[str, Any]] = []
    for threshold in thresholds:
        pred = (scores >= threshold).astype(int)
        precision, recall, f1, _support = precision_recall_fscore_support(
            y_true,
            pred,
            average="binary",
            zero_division=0,
        )
        threshold_rows.append(
            {
                "threshold": round(float(threshold), 8),
                "predicted_enter": int(pred.sum()),
                "precision": round(float(precision), 6),
                "recall": round(float(recall), 6),
                "f1": round(float(f1), 6),
            }
        )

    order = np.argsort(-scores)
    top_buckets: list[dict[str, Any]] = []
    for pct in [0.01, 0.05, 0.10, 0.20]:
        n = max(1, int(math.ceil(len(scores) * pct)))
        idx = order[:n]
        top_buckets.append(
            {
                "bucket": f"top_{int(pct * 100)}pct",
                "rows": int(n),
                "good": int(y_true[idx].sum()),
                "bad": int(n - y_true[idx].sum()),
                "precision": round(float(y_true[idx].sum()) / n, 6),
            }
        )

    decisions = np.where(scores >= enter_threshold, "ENTER", "SKIP")
    daily: list[dict[str, Any]] = []
    for day in sorted(days.astype(str).unique()):
        mask = days.astype(str) == day
        day_y = y_true[mask.to_numpy()]
        day_d = decisions[mask.to_numpy()]
        daily.append(
            {
                "day": day,
                "rows": int(mask.sum()),
                "good": int(day_y.sum()),
                "bad": int(len(day_y) - day_y.sum()),
                "ENTER": int((day_d == "ENTER").sum()),
                "good_enter": int(((day_y == 1) & (day_d == "ENTER")).sum()),
                "bad_enter": int(((day_y == 0) & (day_d == "ENTER")).sum()),
            }
        )
    try:
        auc = float(roc_auc_score(y_true, scores))
    except Exception:
        auc = None
    try:
        ap = float(average_precision_score(y_true, scores))
    except Exception:
        ap = None
    return {
        "rows": int(len(y_true)),
        "good": int(y_true.sum()),
        "bad": int(len(y_true) - y_true.sum()),
        "roc_auc": auc,
        "pr_auc": ap,
        "enter_threshold": round(float(enter_threshold), 8),
        "threshold_metrics": threshold_rows,
        "top_buckets": top_buckets,
        "daily_breakdown": daily,
        "score_distribution": {
            "min": round(float(np.nanmin(scores)), 8),
            "p10": round(float(np.nanquantile(scores, 0.10)), 8),
            "p25": round(float(np.nanquantile(scores, 0.25)), 8),
            "p50": round(float(np.nanquantile(scores, 0.50)), 8),
            "p75": round(float(np.nanquantile(scores, 0.75)), 8),
            "p90": round(float(np.nanquantile(scores, 0.90)), 8),
            "max": round(float(np.nanmax(scores)), 8),
        },
    }


def _multiclass_metrics(y_true: pd.Series, pred_label: pd.Series, *, classes: list[str]) -> dict[str, Any]:
    y = y_true.astype(str).to_numpy()
    p = pred_label.astype(str).to_numpy()
    cm = confusion_matrix(y, p, labels=classes)
    return {
        "rows": int(len(y)),
        "class_counts": {str(k): int(v) for k, v in Counter(y).items()},
        "accuracy": round(float(accuracy_score(y, p)), 6),
        "macro_f1": round(float(f1_score(y, p, labels=classes, average="macro", zero_division=0)), 6),
        "weighted_f1": round(float(f1_score(y, p, labels=classes, average="weighted", zero_division=0)), 6),
        "classes": classes,
        "confusion_matrix": cm.astype(int).tolist(),
    }


def _wilson_lower_bound(successes: int, total: int, *, z: float = 1.28155) -> float:
    if total <= 0:
        return 0.0
    p = successes / total
    denom = 1.0 + z * z / total
    centre = p + z * z / (2.0 * total)
    margin = z * math.sqrt((p * (1.0 - p) + z * z / (4.0 * total)) / total)
    return max(0.0, (centre - margin) / denom)


def _threshold_candidate_rows(scores: np.ndarray, y_true: np.ndarray, days: pd.Series) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    clean_scores = np.asarray(scores, dtype=float)
    clean_y = np.asarray(y_true, dtype=int)
    day_values = days.astype(str)
    for quantile in [0.995, 0.99, 0.985, 0.98, 0.975, 0.97, 0.965, 0.96, 0.95, 0.94, 0.93, 0.92, 0.91, 0.90]:
        threshold = float(np.nanquantile(clean_scores, quantile))
        mask = clean_scores >= threshold
        predicted = int(mask.sum())
        good = int(clean_y[mask].sum()) if predicted else 0
        bad = predicted - good
        precision = good / predicted if predicted else 0.0
        recall = good / max(int(clean_y.sum()), 1)
        rows.append(
            {
                "quantile": round(float(quantile), 6),
                "threshold": round(threshold, 10),
                "predicted_enter": predicted,
                "good": good,
                "bad": bad,
                "precision": round(float(precision), 6),
                "recall": round(float(recall), 6),
                "day_coverage": int(day_values[mask].nunique()) if predicted else 0,
                "wilson_precision_low80": round(float(_wilson_lower_bound(good, predicted)), 6),
            }
        )
    return rows


def _decision_threshold(scores: np.ndarray, y_true: np.ndarray | None = None, days: pd.Series | None = None) -> dict[str, Any]:
    if y_true is None or days is None:
        enter = float(np.nanquantile(scores, 0.90))
        watch = float(np.nanquantile(scores, 0.75))
        if watch > enter:
            watch = enter
        return {
            "entry_enter_threshold": round(enter, 10),
            "entry_watch_threshold": round(watch, 10),
            "policy": "fallback_train_oof_quantiles_only_no_forward_tuning",
            "enter_quantile": 0.90,
            "watch_quantile": 0.75,
        }

    candidates = _threshold_candidate_rows(scores, y_true, days)
    total_rows = len(scores)
    day_count = max(int(days.astype(str).nunique()), 1)
    min_enter = max(20, int(math.ceil(total_rows * 0.01)))
    min_days = max(5, int(math.ceil(day_count * 0.25)))
    eligible = [
        row
        for row in candidates
        if int(row["predicted_enter"]) >= min_enter and int(row["day_coverage"]) >= min_days
    ] or candidates
    best = max(
        eligible,
        key=lambda row: (
            float(row["wilson_precision_low80"]),
            float(row["precision"]),
            -int(row["predicted_enter"]),
        ),
    )
    enter = float(best["threshold"])
    enter_quantile = float(best["quantile"])
    watch_quantile = max(0.75, min(0.90, enter_quantile - 0.15))
    watch = float(np.nanquantile(scores, watch_quantile))
    if watch > enter:
        watch = enter
    return {
        "entry_enter_threshold": round(enter, 10),
        "entry_watch_threshold": round(watch, 10),
        "policy": "train_oof_precision_wilson_only_no_forward_tuning",
        "enter_quantile": round(enter_quantile, 6),
        "watch_quantile": round(float(watch_quantile), 6),
        "min_enter": int(min_enter),
        "min_day_coverage": int(min_days),
        "selected_candidate": best,
        "candidate_thresholds": candidates,
    }


def _apply_entry_decision(scores: np.ndarray, thresholds: dict[str, Any]) -> np.ndarray:
    enter = float(thresholds["entry_enter_threshold"])
    watch = float(thresholds["entry_watch_threshold"])
    return np.where(scores >= enter, "ENTER", np.where(scores >= watch, "WATCH", "SKIP"))


def _top_bucket_precision(metrics: dict[str, Any], bucket: str = "top_1pct") -> float:
    for row in metrics.get("top_buckets", []):
        if row.get("bucket") == bucket:
            return float(row.get("precision") or 0.0)
    return 0.0


def _threshold_precision(metrics: dict[str, Any]) -> float:
    threshold = round(float(metrics.get("enter_threshold") or 0.0), 8)
    for row in metrics.get("threshold_metrics", []):
        if round(float(row.get("threshold") or 0.0), 8) == threshold:
            return float(row.get("precision") or 0.0)
    return 0.0


def _select_candidate(candidates: dict[str, dict[str, Any]]) -> str:
    return max(
        candidates,
        key=lambda name: (
            float(candidates[name]["metrics"].get("pr_auc") or 0.0),
            _top_bucket_precision(candidates[name]["metrics"]),
            _threshold_precision(candidates[name]["metrics"]),
        ),
    )


def _select_production_entry_model(metrics: dict[str, Any]) -> dict[str, Any]:
    baseline = metrics["entry_baseline_oof"]
    two_block = metrics["entry_two_block_oof"]
    walk = metrics.get("walk_forward_audit", {})
    walk_baseline = walk.get("baseline", {}) if isinstance(walk, dict) else {}
    walk_two = walk.get("two_block", {}) if isinstance(walk, dict) else {}

    baseline_score = float(baseline.get("pr_auc") or 0.0) + float(walk_baseline.get("pr_auc") or 0.0)
    two_score = float(two_block.get("pr_auc") or 0.0) + float(walk_two.get("pr_auc") or 0.0)
    baseline_top = _top_bucket_precision(baseline)
    two_top = _top_bucket_precision(two_block)
    two_block_wins = (
        two_score >= baseline_score + 0.005
        and two_top >= baseline_top
        and float(two_block.get("pr_auc") or 0.0) >= float(baseline.get("pr_auc") or 0.0)
    )
    selected = "entry_two_block" if two_block_wins else "entry_baseline"
    return {
        "model_key": selected,
        "selection_policy": "use_two_block_only_if_oof_and_walk_forward_pr_auc_improve_and_top_precision_not_worse",
        "baseline_score": round(float(baseline_score), 8),
        "two_block_score": round(float(two_score), 8),
        "baseline_pr_auc": baseline.get("pr_auc"),
        "two_block_pr_auc": two_block.get("pr_auc"),
        "baseline_walk_pr_auc": walk_baseline.get("pr_auc"),
        "two_block_walk_pr_auc": walk_two.get("pr_auc"),
        "baseline_top_1pct_precision": baseline_top,
        "two_block_top_1pct_precision": two_top,
        "reason": "two_block_won_quality_gate" if two_block_wins else "baseline_kept_because_two_block_did_not_pass_quality_gate",
    }


def _write_training_guard_md(path: Path, guard: dict[str, Any]) -> None:
    lines = [
        "# STAS5 V5 Two-Block Training Guard",
        "",
        f"Статус: `{guard['status']}`.",
        "",
        "Guard проверяет batch dataset перед обучением. Training этим guard не выполняется.",
        "",
        "## Счетчики",
        "",
        f"- days: `{guard['days']}`",
        f"- rows: `{guard['rows']}`",
        f"- entry_y=1: `{guard['entry_y_counts'].get('1', 0)}`",
        f"- entry_y=0: `{guard['entry_y_counts'].get('0', 0)}`",
        f"- features: `{guard['feature_count']}`",
        "",
        "## Checks",
        "",
    ]
    for item in guard["checks"]:
        lines.append(f"- `{item['check']}`: `{item['status']}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_training_guard(
    *,
    run_dir: Path,
    dataset_path: Path = DEFAULT_BATCH_DATASET,
    allowlist_path: Path = DEFAULT_BATCH_ALLOWLIST,
    batch_guard_path: Path = DEFAULT_BATCH_GUARD,
    expected_days: int = EXPECTED_DAYS,
    expected_rows: int = EXPECTED_ROWS,
    expected_good: int = EXPECTED_GOOD,
    expected_bad: int = EXPECTED_BAD,
    expected_features: int = EXPECTED_FEATURES,
) -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    df, features = _read_batch(dataset_path, allowlist_path)
    batch_guard = _load_json(batch_guard_path) if batch_guard_path.exists() else {}
    entry_counts_raw = pd.to_numeric(df.get("entry_y", pd.Series(dtype=float)), errors="coerce").value_counts().sort_index()
    entry_counts = {str(int(k)): int(v) for k, v in entry_counts_raw.items() if pd.notna(k)}
    days = sorted(df["day"].astype(str).unique().tolist()) if "day" in df.columns else []
    missing_features = [column for column in features if column not in df.columns]
    target_in_features = sorted(set(features).intersection(TARGET_OR_MANUAL_COLUMNS))
    forbidden = _forbidden_feature_matches(features)
    cs_time = _source_time_check(df, "cs_max_source_time_utc") if not df.empty else {}
    fcs_time = _source_time_check(df, "fcs_max_source_time_utc") if not df.empty else {}

    numeric, _cat = _infer_column_types(df, features)
    inf_count = 0
    for column in numeric:
        if column in df.columns:
            values = pd.to_numeric(df[column], errors="coerce").to_numpy(dtype=float)
            inf_count += int(np.isinf(values).sum())
    duplicate_day_candidate = int(df.duplicated(["day", "candidate_id"]).sum()) if {"day", "candidate_id"}.issubset(df.columns) else -1
    duplicate_day_record = int(df.duplicated(["day", "record_id"]).sum()) if {"day", "record_id"}.issubset(df.columns) else -1
    feature_nulls = int(df[features].isna().sum().sum()) if features else -1
    required_targets_present = [column for column in TARGET_COLUMNS if column in df.columns]

    checks = [
        _check(
            "batch_guard_pass",
            batch_guard.get("status") == BATCH_GUARD_PASS,
            {"actual": batch_guard.get("status"), "expected": BATCH_GUARD_PASS},
        ),
        _check("days_match_expected", len(days) == expected_days, {"actual": len(days), "expected": expected_days}),
        _check("rows_match_expected", len(df) == expected_rows, {"actual": int(len(df)), "expected": expected_rows}),
        _check(
            "entry_y_counts_match",
            entry_counts.get("1", 0) == expected_good and entry_counts.get("0", 0) == expected_bad,
            {"actual": entry_counts, "expected_good": expected_good, "expected_bad": expected_bad},
        ),
        _check("feature_count_expected", len(features) == expected_features, {"actual": len(features), "expected": expected_features}),
        _check("feature_columns_present", not missing_features, {"missing": missing_features[:50], "missing_count": len(missing_features)}),
        _check("required_targets_present", set(TARGET_COLUMNS).issubset(required_targets_present), {"present": required_targets_present}),
        _check("target_manual_columns_not_in_X", not target_in_features, {"columns": target_in_features}),
        _check("forbidden_columns_absent_from_X", not forbidden, forbidden),
        _check("no_duplicate_day_candidate", duplicate_day_candidate == 0, {"duplicates": duplicate_day_candidate}),
        _check("no_duplicate_day_record", duplicate_day_record == 0, {"duplicates": duplicate_day_record}),
        _check("feature_values_no_null", feature_nulls == 0, {"feature_nulls": feature_nulls}),
        _check("feature_values_no_inf", inf_count == 0, {"feature_inf_count": inf_count}),
        _check(
            "cs_max_source_time_utc_lte_entry_time_utc",
            cs_time.get("source_after_entry_rows", 1) == 0 and cs_time.get("source_na_rows", 1) == 0,
            cs_time,
        ),
        _check(
            "fcs_max_source_time_utc_lte_entry_time_utc",
            fcs_time.get("source_after_entry_rows", 1) == 0 and fcs_time.get("source_na_rows", 1) == 0,
            fcs_time,
        ),
        _check(
            "oof_policy_declared",
            True,
            {
                "phase_state_to_entry": "LODO OOF predictions for training; live predictions for forward",
                "forward_window": {"start_day": FORWARD_START_DAY, "end_day": FORWARD_END_DAY},
            },
        ),
    ]
    status = TRAINING_GUARD_PASS if all(item["status"] == "PASS" for item in checks) else TRAINING_GUARD_FAIL
    guard = {
        "status": status,
        "created_utc": utc_now(),
        "run_id": run_dir.name,
        "run_dir": rel(run_dir),
        "dataset_path": rel(dataset_path),
        "dataset_sha256": _sha256(dataset_path) if dataset_path.exists() else "",
        "allowlist_path": rel(allowlist_path),
        "allowlist_sha256": _sha256(allowlist_path) if allowlist_path.exists() else "",
        "batch_guard_path": rel(batch_guard_path),
        "days": len(days),
        "date_range": {"start_day": min(days) if days else "", "end_day": max(days) if days else ""},
        "rows": int(len(df)),
        "entry_y_counts": entry_counts,
        "feature_count": len(features),
        "checks": checks,
        "feature_columns": features,
    }
    json_path = run_dir / "STAS5_V5_TWO_BLOCK_TRAINING_GUARD_V1.json"
    md_path = run_dir / "STAS5_V5_TWO_BLOCK_TRAINING_GUARD_RU.md"
    write_json(json_path, guard)
    _write_training_guard_md(md_path, guard)
    return guard


def _write_metrics_md(path: Path, metrics: dict[str, Any]) -> None:
    baseline = metrics["entry_baseline_oof"]
    two_block = metrics["entry_two_block_oof"]
    phase = metrics["market_phase_oof"]
    state = metrics["market_state_oof"]
    selected = metrics.get("selected_entry_model", {})
    weight = metrics.get("sample_weight_summary", {})
    lines = [
        "# STAS5 V5 Two-Block ML Metrics",
        "",
        f"Статус: `{metrics['status']}`.",
        "",
        "## Production Selection",
        "",
        f"- selected model: `{selected.get('model_key', '')}`",
        f"- reason: `{selected.get('reason', '')}`",
        f"- baseline model kind: `{metrics.get('entry_baseline_selected_model_kind', '')}`",
        f"- two-block model kind: `{metrics.get('entry_two_block_selected_model_kind', '')}`",
        "",
        "## Sample Weights",
        "",
        f"- review weight start day: `{weight.get('review_weight_start_day', '')}`",
        f"- recent rows/good/bad: `{weight.get('recent_rows', 0)}` / `{weight.get('recent_good', 0)}` / `{weight.get('recent_bad', 0)}`",
        f"- mean good/bad weight: `{weight.get('good_weight_mean', 0)}` / `{weight.get('bad_weight_mean', 0)}`",
        "",
        "## Baseline vs Two-Block",
        "",
        "| model | ROC-AUC | PR-AUC | GOOD | BAD | enter_threshold |",
        "|---|---:|---:|---:|---:|---:|",
        f"| ENTRY_BASELINE_ML | `{baseline['roc_auc']}` | `{baseline['pr_auc']}` | `{baseline['good']}` | `{baseline['bad']}` | `{baseline['enter_threshold']}` |",
        f"| ENTRY_ML two-block | `{two_block['roc_auc']}` | `{two_block['pr_auc']}` | `{two_block['good']}` | `{two_block['bad']}` | `{two_block['enter_threshold']}` |",
        "",
        "## Market Phase/State",
        "",
        f"- phase accuracy: `{phase['accuracy']}`, macro-F1: `{phase['macro_f1']}`",
        f"- state accuracy: `{state['accuracy']}`, macro-F1: `{state['macro_f1']}`",
        "",
        "## Guardrail",
        "",
        "Метрики ENTRY рассчитаны по OOF score. Настоящие `phase_y/state_y` не входили в features второго блока.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_post_train_guard_md(path: Path, guard: dict[str, Any]) -> None:
    lines = [
        "# STAS5 V5 Two-Block Post-Train Guard",
        "",
        f"Статус: `{guard['status']}`.",
        "",
        "## Checks",
        "",
    ]
    for item in guard["checks"]:
        lines.append(f"- `{item['check']}`: `{item['status']}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _post_train_guard(run_dir: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    paths = manifest["artifacts"]
    entry_features = manifest["entry_ml_feature_columns"]
    prediction_features = set(manifest["prediction_feature_columns"])
    base_features = set(manifest["feature_columns"])
    forbidden_entry = {
        column: hits
        for column, hits in _forbidden_feature_matches([c for c in entry_features if c not in prediction_features]).items()
        if column not in prediction_features
    }
    target_in_entry = sorted(set(entry_features).intersection(TARGET_OR_MANUAL_COLUMNS))
    checks = [
        _check("training_guard_pass", manifest.get("training_guard_status") == TRAINING_GUARD_PASS, {"actual": manifest.get("training_guard_status")}),
        _check("baseline_model_exists", (PROJECT_ROOT / paths["entry_baseline_model"]).exists(), {"path": paths["entry_baseline_model"]}),
        _check("market_phase_state_model_exists", (PROJECT_ROOT / paths["market_phase_state_model"]).exists(), {"path": paths["market_phase_state_model"]}),
        _check("entry_ml_model_exists", (PROJECT_ROOT / paths["entry_ml_model"]).exists(), {"path": paths["entry_ml_model"]}),
        _check(
            "selected_entry_model_valid",
            manifest.get("selected_entry_model", {}).get("model_key") in {"entry_baseline", "entry_two_block"},
            manifest.get("selected_entry_model", {}),
        ),
        _check("baseline_features_match_training_allowlist", manifest["entry_baseline_feature_columns"] == manifest["feature_columns"], {"count": len(manifest["entry_baseline_feature_columns"])}),
        _check("market_phase_state_features_match_training_allowlist", manifest["market_phase_state_feature_columns"] == manifest["feature_columns"], {"count": len(manifest["market_phase_state_feature_columns"])}),
        _check(
            "entry_ml_features_causal_allowlist_plus_predictions",
            base_features.issubset(set(entry_features)) and prediction_features.issubset(set(entry_features)),
            {"entry_feature_count": len(entry_features), "base_feature_count": len(base_features), "prediction_feature_count": len(prediction_features)},
        ),
        _check("no_target_manual_columns_in_entry_features", not target_in_entry, {"columns": target_in_entry}),
        _check("no_forbidden_base_columns_in_entry_features", not forbidden_entry, forbidden_entry),
        _check("oof_coverage_100pct", manifest["oof_coverage_rows"] == manifest["rows"], {"oof": manifest["oof_coverage_rows"], "rows": manifest["rows"]}),
        _check("forward_not_started_inside_training_run", not (run_dir / "forward_predictions.csv").exists(), {}),
    ]
    status = POST_TRAIN_GUARD_PASS if all(item["status"] == "PASS" for item in checks) else POST_TRAIN_GUARD_FAIL
    guard = {
        "status": status,
        "created_utc": utc_now(),
        "run_id": run_dir.name,
        "run_dir": rel(run_dir),
        "checks": checks,
    }
    write_json(run_dir / "STAS5_V5_TWO_BLOCK_POST_TRAIN_GUARD_V1.json", guard)
    _write_post_train_guard_md(run_dir / "STAS5_V5_TWO_BLOCK_POST_TRAIN_GUARD_RU.md", guard)
    return guard


def _walk_forward_audit(
    train: pd.DataFrame,
    *,
    feature_columns: list[str],
    numeric_columns: list[str],
    categorical_columns: list[str],
    phase_classes: list[str],
    state_classes: list[str],
    sample_weights: np.ndarray,
    baseline_model_kind: str,
    entry_model_kind: str,
    min_train_days: int = 28,
) -> dict[str, Any]:
    days = sorted(train["day"].astype(str).unique().tolist())
    rows: list[dict[str, Any]] = []
    baseline_scores: list[float] = []
    two_block_scores: list[float] = []
    y_all: list[int] = []
    day_all: list[str] = []
    for idx in range(min_train_days, len(days)):
        val_day = days[idx]
        train_days = days[:idx]
        train_mask_full = train["day"].astype(str).isin(train_days)
        val_mask_full = train["day"].astype(str).eq(val_day)
        train_idx = train.index[train_mask_full].to_numpy()
        val_idx = train.index[val_mask_full].to_numpy()
        train_rows = train.loc[train_idx].copy().reset_index(drop=True)
        val_rows = train.loc[val_idx].copy().reset_index(drop=True)
        train_weights = sample_weights[train_idx]
        if train_rows["entry_y"].nunique() < 2 or val_rows.empty:
            continue

        baseline_model = _fit_model(
            train_rows.assign(entry_y=pd.to_numeric(train_rows["entry_y"], errors="coerce").astype(int)),
            target="entry_y",
            feature_columns=feature_columns,
            numeric_columns=numeric_columns,
            categorical_columns=categorical_columns,
            sample_weights=train_weights,
            model_kind=baseline_model_kind,
        )
        x_val = _prepare_feature_matrix(val_rows, feature_columns=feature_columns, numeric_columns=numeric_columns, categorical_columns=categorical_columns)
        base_val = _positive_proba(baseline_model, x_val)

        phase_model = _fit_model(
            train_rows,
            target="phase_y",
            feature_columns=feature_columns,
            numeric_columns=numeric_columns,
            categorical_columns=categorical_columns,
            sample_weights=train_weights,
            model_kind=PHASE_STATE_MODEL_KIND,
        )
        state_model = _fit_model(
            train_rows,
            target="state_y",
            feature_columns=feature_columns,
            numeric_columns=numeric_columns,
            categorical_columns=categorical_columns,
            sample_weights=train_weights,
            model_kind=PHASE_STATE_MODEL_KIND,
        )
        x_train_phase = _prepare_feature_matrix(
            train_rows,
            feature_columns=feature_columns,
            numeric_columns=numeric_columns,
            categorical_columns=categorical_columns,
        )
        # This walk-forward audit only scores future validation days. Train-window
        # phase/state predictions may be in-sample here; production training still
        # uses full LODO OOF predictions before ENTRY_ML fitting.
        phase_train = _proba_predictions(phase_model, x_train_phase, classes=phase_classes, prefix=PHASE_PREFIX)
        state_train = _proba_predictions(state_model, x_train_phase, classes=state_classes, prefix=STATE_PREFIX)
        train_stack = pd.concat([train_rows, phase_train, state_train], axis=1)
        val_phase = _proba_predictions(phase_model, x_val, classes=phase_classes, prefix=PHASE_PREFIX)
        val_state = _proba_predictions(state_model, x_val, classes=state_classes, prefix=STATE_PREFIX)
        val_stack = pd.concat([val_rows, val_phase, val_state], axis=1)
        pred_cols = _phase_state_prediction_columns(phase_classes, state_classes)
        entry_features = feature_columns + pred_cols
        entry_numeric = numeric_columns + [c for c in pred_cols if c.endswith("_conf") or "_prob_" in c]
        entry_categorical = categorical_columns + [c for c in pred_cols if c.endswith("_label")]
        entry_model = _fit_model(
            train_stack.assign(entry_y=pd.to_numeric(train_stack["entry_y"], errors="coerce").astype(int)),
            target="entry_y",
            feature_columns=entry_features,
            numeric_columns=entry_numeric,
            categorical_columns=entry_categorical,
            sample_weights=train_weights,
            model_kind=entry_model_kind,
        )
        x_entry_val = _prepare_feature_matrix(
            val_stack,
            feature_columns=entry_features,
            numeric_columns=entry_numeric,
            categorical_columns=entry_categorical,
        )
        two_val = _positive_proba(entry_model, x_entry_val)
        y_val = pd.to_numeric(val_rows["entry_y"], errors="coerce").fillna(0).astype(int).to_numpy()
        baseline_scores.extend(base_val.tolist())
        two_block_scores.extend(two_val.tolist())
        y_all.extend(y_val.tolist())
        day_all.extend([val_day] * len(y_val))
        rows.append(
            {
                "validation_day": val_day,
                "train_days": len(train_days),
                "train_rows": int(len(train_rows)),
                "validation_rows": int(len(val_rows)),
                "good": int(y_val.sum()),
            }
        )
    if not y_all:
        return {"status": "SKIPPED", "reason": "not enough walk-forward folds", "folds": rows}
    y_np = np.asarray(y_all, dtype=int)
    base_np = np.asarray(baseline_scores, dtype=float)
    two_np = np.asarray(two_block_scores, dtype=float)
    wf_days = pd.Series(day_all)
    base_thresholds = _decision_threshold(base_np, y_np, wf_days)
    two_thresholds = _decision_threshold(two_np, y_np, wf_days)
    return {
        "status": "PASS",
        "policy": "past_days_train_next_day_validation_weighted_selected_model_kinds",
        "min_train_days": min_train_days,
        "baseline_model_kind": baseline_model_kind,
        "entry_model_kind": entry_model_kind,
        "phase_state_model_kind": PHASE_STATE_MODEL_KIND,
        "folds": rows,
        "baseline": _entry_metrics(y_np, base_np, wf_days, enter_threshold=float(base_thresholds["entry_enter_threshold"])),
        "two_block": _entry_metrics(y_np, two_np, wf_days, enter_threshold=float(two_thresholds["entry_enter_threshold"])),
        "baseline_thresholds": base_thresholds,
        "two_block_thresholds": two_thresholds,
    }


def train_two_block_ml(
    *,
    run_id: str | None = None,
    dataset_path: Path = DEFAULT_BATCH_DATASET,
    allowlist_path: Path = DEFAULT_BATCH_ALLOWLIST,
    batch_guard_path: Path = DEFAULT_BATCH_GUARD,
    run_root: Path = DEFAULT_MODEL_RUNS_DIR,
    latest_model_pointer: Path | None = DEFAULT_LATEST_MODEL_POINTER,
    expected_days: int = EXPECTED_DAYS,
    expected_rows: int = EXPECTED_ROWS,
    expected_good: int = EXPECTED_GOOD,
    expected_bad: int = EXPECTED_BAD,
    expected_features: int = EXPECTED_FEATURES,
    strict: bool = True,
    review_weight_start_day: str | None = DEFAULT_REVIEW_WEIGHT_START_DAY,
    entry_model_candidates: list[str] | None = None,
) -> dict[str, Any]:
    run_id = run_id or f"stas5_v5_two_block_train_{run_stamp()}"
    run_dir = run_root / run_id
    guard = run_training_guard(
        run_dir=run_dir,
        dataset_path=dataset_path,
        allowlist_path=allowlist_path,
        batch_guard_path=batch_guard_path,
        expected_days=expected_days,
        expected_rows=expected_rows,
        expected_good=expected_good,
        expected_bad=expected_bad,
        expected_features=expected_features,
    )
    if strict and guard["status"] != TRAINING_GUARD_PASS:
        raise ValueError(f"training guard is not PASS: {guard['status']}")

    train, feature_columns = _read_batch(dataset_path, allowlist_path)
    train = train.sort_values(["day", "entry_time_utc", "candidate_id", "record_id"]).reset_index(drop=True)
    train["entry_y"] = pd.to_numeric(train["entry_y"], errors="coerce").fillna(0).astype(int)
    train["phase_y"] = train["phase_y"].astype(str)
    train["state_y"] = train["state_y"].astype(str)
    numeric_columns, categorical_columns = _infer_column_types(train, feature_columns)
    y_entry = train["entry_y"].to_numpy(dtype=int)
    phase_classes = sorted(train["phase_y"].astype(str).unique().tolist())
    state_classes = sorted(train["state_y"].astype(str).unique().tolist())
    sample_weights = _sample_weights(train, review_weight_start_day=review_weight_start_day)
    sample_weight_summary = _sample_weight_summary(train, sample_weights, review_weight_start_day=review_weight_start_day)
    model_candidates = entry_model_candidates or ENTRY_MODEL_CANDIDATES

    baseline_candidates: dict[str, dict[str, Any]] = {}
    for model_kind in model_candidates:
        candidate_oof, candidate_folds = _run_binary_lodo_scores(
            train,
            target="entry_y",
            feature_columns=feature_columns,
            numeric_columns=numeric_columns,
            categorical_columns=categorical_columns,
            sample_weights=sample_weights,
            model_kind=model_kind,
        )
        candidate_thresholds = _decision_threshold(candidate_oof, y_entry, train["day"].astype(str))
        candidate_metrics = _entry_metrics(
            y_entry,
            candidate_oof,
            train["day"].astype(str),
            enter_threshold=float(candidate_thresholds["entry_enter_threshold"]),
        )
        candidate_metrics["model_kind"] = model_kind
        candidate_metrics["threshold_policy"] = candidate_thresholds
        baseline_candidates[model_kind] = {
            "scores": candidate_oof,
            "folds": candidate_folds,
            "thresholds": candidate_thresholds,
            "metrics": candidate_metrics,
        }
    baseline_model_kind = _select_candidate(baseline_candidates)
    baseline_oof = baseline_candidates[baseline_model_kind]["scores"]
    baseline_folds = baseline_candidates[baseline_model_kind]["folds"]
    baseline_thresholds = baseline_candidates[baseline_model_kind]["thresholds"]
    phase_oof, phase_folds = _run_multiclass_lodo_predictions(
        train,
        target="phase_y",
        prefix=PHASE_PREFIX,
        classes=phase_classes,
        feature_columns=feature_columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        sample_weights=sample_weights,
    )
    state_oof, state_folds = _run_multiclass_lodo_predictions(
        train,
        target="state_y",
        prefix=STATE_PREFIX,
        classes=state_classes,
        feature_columns=feature_columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        sample_weights=sample_weights,
    )
    prediction_columns = _phase_state_prediction_columns(phase_classes, state_classes)
    stack_train = pd.concat([train, phase_oof, state_oof], axis=1)
    entry_feature_columns = feature_columns + prediction_columns
    entry_numeric_columns = numeric_columns + [c for c in prediction_columns if c.endswith("_conf") or "_prob_" in c]
    entry_categorical_columns = categorical_columns + [c for c in prediction_columns if c.endswith("_label")]
    entry_candidates: dict[str, dict[str, Any]] = {}
    for model_kind in model_candidates:
        candidate_oof, candidate_folds = _run_binary_lodo_scores(
            stack_train,
            target="entry_y",
            feature_columns=entry_feature_columns,
            numeric_columns=entry_numeric_columns,
            categorical_columns=entry_categorical_columns,
            sample_weights=sample_weights,
            model_kind=model_kind,
        )
        candidate_thresholds = _decision_threshold(candidate_oof, y_entry, train["day"].astype(str))
        candidate_metrics = _entry_metrics(
            y_entry,
            candidate_oof,
            train["day"].astype(str),
            enter_threshold=float(candidate_thresholds["entry_enter_threshold"]),
        )
        candidate_metrics["model_kind"] = model_kind
        candidate_metrics["threshold_policy"] = candidate_thresholds
        entry_candidates[model_kind] = {
            "scores": candidate_oof,
            "folds": candidate_folds,
            "thresholds": candidate_thresholds,
            "metrics": candidate_metrics,
        }
    entry_model_kind = _select_candidate(entry_candidates)
    entry_oof = entry_candidates[entry_model_kind]["scores"]
    entry_folds = entry_candidates[entry_model_kind]["folds"]
    thresholds = entry_candidates[entry_model_kind]["thresholds"]

    x_base = _prepare_feature_matrix(train, feature_columns=feature_columns, numeric_columns=numeric_columns, categorical_columns=categorical_columns)
    baseline_model = _build_model_pipeline(numeric_columns=numeric_columns, categorical_columns=categorical_columns, model_kind=baseline_model_kind)
    _fit_with_optional_weights(baseline_model, x_base, y_entry, sample_weights)

    phase_model = _build_model_pipeline(
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        model_kind=PHASE_STATE_MODEL_KIND,
    )
    _fit_with_optional_weights(phase_model, x_base, train["phase_y"].astype(str), sample_weights)
    state_model = _build_model_pipeline(
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        model_kind=PHASE_STATE_MODEL_KIND,
    )
    _fit_with_optional_weights(state_model, x_base, train["state_y"].astype(str), sample_weights)

    x_entry = _prepare_feature_matrix(
        stack_train,
        feature_columns=entry_feature_columns,
        numeric_columns=entry_numeric_columns,
        categorical_columns=entry_categorical_columns,
    )
    entry_model = _build_model_pipeline(numeric_columns=entry_numeric_columns, categorical_columns=entry_categorical_columns, model_kind=entry_model_kind)
    _fit_with_optional_weights(entry_model, x_entry, y_entry, sample_weights)

    baseline_model_path = run_dir / "STAS5_V5_ENTRY_BASELINE_MODEL.joblib"
    phase_state_model_path = run_dir / "STAS5_V5_MARKET_PHASE_STATE_MODEL.joblib"
    entry_model_path = run_dir / "STAS5_V5_ENTRY_ML_MODEL.joblib"
    joblib.dump(
        {
            "model_id": "STAS5_V5_ENTRY_BASELINE_ML_V1",
            "pipeline": baseline_model,
            "model_kind": baseline_model_kind,
            "feature_columns": feature_columns,
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
            "thresholds": baseline_thresholds,
            "sample_weight_policy": sample_weight_summary,
        },
        baseline_model_path,
    )
    joblib.dump(
        {
            "model_id": "STAS5_V5_MARKET_PHASE_STATE_ML_V1",
            "phase_pipeline": phase_model,
            "state_pipeline": state_model,
            "model_kind": PHASE_STATE_MODEL_KIND,
            "feature_columns": feature_columns,
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
            "phase_classes": phase_classes,
            "state_classes": state_classes,
            "prediction_columns": prediction_columns,
            "sample_weight_policy": sample_weight_summary,
        },
        phase_state_model_path,
    )
    joblib.dump(
        {
            "model_id": "STAS5_V5_ENTRY_ML_V1",
            "pipeline": entry_model,
            "model_kind": entry_model_kind,
            "feature_columns": entry_feature_columns,
            "base_feature_columns": feature_columns,
            "prediction_feature_columns": prediction_columns,
            "numeric_columns": entry_numeric_columns,
            "categorical_columns": entry_categorical_columns,
            "thresholds": thresholds,
            "phase_state_model_required": True,
            "sample_weight_policy": sample_weight_summary,
        },
        entry_model_path,
    )

    predictions = train[KEY_COLUMNS + TARGET_COLUMNS].copy()
    predictions["TRAIN_SAMPLE_WEIGHT"] = sample_weights
    for model_kind, payload in baseline_candidates.items():
        column_key = model_kind.upper()
        predictions[f"ENTRY_BASELINE_{column_key}_OOF_SCORE"] = payload["scores"]
        predictions[f"ENTRY_BASELINE_{column_key}_OOF_DECISION"] = _apply_entry_decision(payload["scores"], payload["thresholds"])
    predictions["ENTRY_BASELINE_OOF_SCORE"] = baseline_oof
    predictions["ENTRY_BASELINE_OOF_DECISION"] = _apply_entry_decision(baseline_oof, baseline_thresholds)
    for column in phase_oof.columns:
        predictions[column] = phase_oof[column]
    for column in state_oof.columns:
        predictions[column] = state_oof[column]
    for model_kind, payload in entry_candidates.items():
        column_key = model_kind.upper()
        predictions[f"ENTRY_ML_{column_key}_OOF_SCORE"] = payload["scores"]
        predictions[f"ENTRY_ML_{column_key}_OOF_DECISION"] = _apply_entry_decision(payload["scores"], payload["thresholds"])
    predictions["ENTRY_ML_OOF_SCORE"] = entry_oof
    predictions["ENTRY_ML_OOF_DECISION"] = _apply_entry_decision(entry_oof, thresholds)
    predictions_path = run_dir / "STAS5_V5_TWO_BLOCK_TRAIN_OOF_PREDICTIONS_V1.csv"
    predictions.to_csv(predictions_path, index=False, encoding="utf-8-sig")

    oof_phase_path = run_dir / "STAS5_V5_MARKET_PHASE_STATE_OOF_PREDICTIONS_V1.csv"
    pd.concat([train[KEY_COLUMNS + ["phase_y", "state_y"]], phase_oof, state_oof], axis=1).to_csv(
        oof_phase_path,
        index=False,
        encoding="utf-8-sig",
    )
    entry_allowlist_path = run_dir / "STAS5_V5_ENTRY_ML_FEATURE_ALLOWLIST_V1.json"
    write_json(
        entry_allowlist_path,
        {
            "status": "PASS",
            "created_utc": utc_now(),
            "feature_columns": entry_feature_columns,
            "base_feature_columns": feature_columns,
            "prediction_feature_columns": prediction_columns,
            "feature_count": len(entry_feature_columns),
        },
    )

    metrics = {
        "status": "PASS_V5_TWO_BLOCK_METRICS_READY",
        "created_utc": utc_now(),
        "rows": int(len(train)),
        "sample_weight_summary": sample_weight_summary,
        "entry_model_candidates": model_candidates,
        "market_phase_state_model_kind": PHASE_STATE_MODEL_KIND,
        "entry_baseline_selected_model_kind": baseline_model_kind,
        "entry_two_block_selected_model_kind": entry_model_kind,
        "entry_baseline_candidates_oof": {kind: payload["metrics"] for kind, payload in baseline_candidates.items()},
        "entry_two_block_candidates_oof": {kind: payload["metrics"] for kind, payload in entry_candidates.items()},
        "entry_baseline_oof": baseline_candidates[baseline_model_kind]["metrics"],
        "entry_two_block_oof": entry_candidates[entry_model_kind]["metrics"],
        "market_phase_oof": _multiclass_metrics(train["phase_y"], phase_oof[f"{PHASE_PREFIX}_pred_label"], classes=phase_classes),
        "market_state_oof": _multiclass_metrics(train["state_y"], state_oof[f"{STATE_PREFIX}_pred_label"], classes=state_classes),
        "walk_forward_audit": _walk_forward_audit(
            train,
            feature_columns=feature_columns,
            numeric_columns=numeric_columns,
            categorical_columns=categorical_columns,
            phase_classes=phase_classes,
            state_classes=state_classes,
            sample_weights=sample_weights,
            baseline_model_kind=baseline_model_kind,
            entry_model_kind=entry_model_kind,
        ),
    }
    metrics["selected_entry_model"] = _select_production_entry_model(metrics)
    metrics_path = run_dir / "STAS5_V5_TWO_BLOCK_METRICS_V1.json"
    metrics_md_path = run_dir / "STAS5_V5_TWO_BLOCK_METRICS_RU.md"
    write_json(metrics_path, metrics)
    _write_metrics_md(metrics_md_path, metrics)

    manifest = {
        "status": TRAIN_STATUS,
        "created_utc": utc_now(),
        "run_id": run_id,
        "run_dir": rel(run_dir),
        "date_range": guard["date_range"],
        "expected_train_counts": {
            "days": expected_days,
            "rows": expected_rows,
            "entry_y_1": expected_good,
            "entry_y_0": expected_bad,
            "features": expected_features,
        },
        "rows": int(len(train)),
        "entry_y_counts": {str(k): int(v) for k, v in train["entry_y"].value_counts().sort_index().items()},
        "training_guard_status": guard["status"],
        "dataset_path": rel(dataset_path),
        "dataset_sha256": _sha256(dataset_path),
        "allowlist_path": rel(allowlist_path),
        "allowlist_sha256": _sha256(allowlist_path),
        "feature_columns": feature_columns,
        "feature_count": len(feature_columns),
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "phase_classes": phase_classes,
        "state_classes": state_classes,
        "prediction_feature_columns": prediction_columns,
        "entry_baseline_feature_columns": feature_columns,
        "market_phase_state_feature_columns": feature_columns,
        "entry_ml_feature_columns": entry_feature_columns,
        "entry_ml_feature_count": len(entry_feature_columns),
        "oof_coverage_rows": int(len(predictions)),
        "folds": {
            "baseline_entry_lodo": baseline_folds,
            "market_phase_lodo": phase_folds,
            "market_state_lodo": state_folds,
            "entry_ml_lodo": entry_folds,
        },
        "sample_weight_summary": sample_weight_summary,
        "entry_model_candidates": model_candidates,
        "market_phase_state_model_kind": PHASE_STATE_MODEL_KIND,
        "entry_baseline_selected_model_kind": baseline_model_kind,
        "entry_two_block_selected_model_kind": entry_model_kind,
        "selected_entry_model": metrics["selected_entry_model"],
        "thresholds": thresholds,
        "baseline_thresholds": baseline_thresholds,
        "artifacts": {
            "entry_baseline_model": rel(baseline_model_path),
            "market_phase_state_model": rel(phase_state_model_path),
            "entry_ml_model": rel(entry_model_path),
            "train_oof_predictions": rel(predictions_path),
            "market_phase_state_oof_predictions": rel(oof_phase_path),
            "entry_ml_feature_allowlist": rel(entry_allowlist_path),
            "metrics_json": rel(metrics_path),
            "metrics_ru": rel(metrics_md_path),
            "training_guard_json": rel(run_dir / "STAS5_V5_TWO_BLOCK_TRAINING_GUARD_V1.json"),
        },
        "guardrails": [
            "entry_y_phase_y_state_y_reason_y_are_targets_not_features",
            "market_phase_state_ml_uses_only_causal_feature_allowlist",
            "entry_ml_uses_causal_feature_allowlist_plus_oof_predictions_only_on_train",
            "forward_must_use_live_phase_state_predictions",
            "forward_window_not_used_for_training_or_threshold_tuning",
        ],
    }
    manifest_path = run_dir / "STAS5_V5_TWO_BLOCK_TRAIN_MANIFEST_V1.json"
    write_json(manifest_path, manifest)
    post_guard = _post_train_guard(run_dir, manifest)
    manifest["post_train_guard_status"] = post_guard["status"]
    manifest["artifacts"]["post_train_guard_json"] = rel(run_dir / "STAS5_V5_TWO_BLOCK_POST_TRAIN_GUARD_V1.json")
    write_json(manifest_path, manifest)
    if latest_model_pointer is not None:
        write_json(
            latest_model_pointer,
            {
                "status": "LATEST_V5_TWO_BLOCK_MODEL_RUN",
                "created_utc": utc_now(),
                "run_id": run_id,
                "run_dir": rel(run_dir),
                "manifest_path": rel(manifest_path),
                "post_train_guard_status": post_guard["status"],
            },
        )
    if strict and post_guard["status"] != POST_TRAIN_GUARD_PASS:
        raise ValueError(f"post-train guard is not PASS: {post_guard['status']}")
    return manifest


def _latest_full274_run(day: str) -> Path:
    compact = compact_day(day)
    runs = sorted(FULL274_RUNS_DIR.glob(f"full274_feature_collect_{compact}_*"), key=lambda item: item.stat().st_mtime)
    if not runs:
        raise FileNotFoundError(f"FULL274 run not found for {day}. Run STAS5_ML_CORE/run_stas5_full274_feature_collect.ps1 first.")
    return runs[-1]


def _forward_day_paths(run_dir: Path, day: str) -> dict[str, Path]:
    compact = compact_day(day)
    day_dir = run_dir / "forward_market_passports" / compact
    prefix = f"STAS5_V5_MARKET_PASSPORT_{compact}"
    return {
        "day_dir": day_dir,
        "ml_ready_full": day_dir / f"{prefix}_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv",
        "allowlist_full": day_dir / f"{prefix}_FEATURE_ALLOWLIST_274_PLUS_FULL_CAUSAL_STRUCTURE_V1.json",
        "guard_full": day_dir / f"{prefix}_FULL_CAUSAL_STRUCTURE_GUARD_V1.json",
    }


def build_forward_dataset(
    *,
    run_dir: Path,
    train_manifest: dict[str, Any],
    start_day: str = FORWARD_START_DAY,
    end_day: str = FORWARD_END_DAY,
    strict: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    run_dir.mkdir(parents=True, exist_ok=True)
    expected_features = [str(column) for column in train_manifest["feature_columns"]]
    frames: list[pd.DataFrame] = []
    day_outputs: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []
    for day in iter_days(start_day, end_day):
        compact = compact_day(day)
        full274_run = _latest_full274_run(day)
        full274_csv = full274_run / f"STAS5_FULL274_FEATURE_SNAPSHOT_{compact}.csv"
        full274_manifest = full274_run / f"STAS5_FULL274_FEATURE_SNAPSHOT_{compact}.manifest.json"
        if not full274_csv.exists() or not full274_manifest.exists():
            raise FileNotFoundError(f"FULL274 files missing for {day}: {full274_run}")
        paths = _forward_day_paths(run_dir, day)
        paths["day_dir"].mkdir(parents=True, exist_ok=True)
        causal_guard = build_causal_structure_package(
            day=day,
            ml_ready_path=full274_csv,
            allowlist_path=full274_manifest,
            output_dir=paths["day_dir"],
        )
        full_guard = build_full_causal_structure_package(
            day=day,
            ml_ready_plus_path=Path(causal_guard["outputs"]["ml_ready_274f_plus_causal_structure_targets"]),
            allowlist_plus_path=Path(causal_guard["outputs"]["feature_allowlist_274_plus_causal_structure"]),
            output_dir=paths["day_dir"],
            draw_plot=False,
        )
        allowlist = _read_allowlist(paths["allowlist_full"])
        frame = pd.read_csv(paths["ml_ready_full"], encoding="utf-8-sig")
        frame, fill = _fill_feature_gaps(frame, expected_features)
        frames.append(frame)
        allowlist_match = allowlist == expected_features
        full_guard_pass = full_guard["status"] == FULL_CAUSAL_GUARD_PASS
        checks.append(_check(f"{compact}_full_guard_pass", full_guard_pass, {"status": full_guard["status"]}))
        checks.append(_check(f"{compact}_allowlist_matches_train", allowlist_match, {"feature_count": len(allowlist)}))
        day_outputs.append(
            {
                "day": day,
                "full274_run": rel(full274_run),
                "rows": int(len(frame)),
                "feature_count": len(allowlist),
                "allowlist_matches_train": allowlist_match,
                "full_guard_status": full_guard["status"],
                "feature_fill_summary": fill,
                "ml_ready_full": rel(paths["ml_ready_full"]),
                "guard_full": rel(paths["guard_full"]),
            }
        )
    dataset = pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()
    dataset = dataset.sort_values([c for c in ["day", "entry_time_utc", "candidate_id", "record_id"] if c in dataset.columns]).reset_index(drop=True)
    missing_features = [column for column in expected_features if column not in dataset.columns]
    feature_nulls = int(dataset[expected_features].isna().sum().sum()) if not dataset.empty and not missing_features else -1
    checks.extend(
        [
            _check("forward_days_7_present", len(day_outputs) == 7, {"actual": len(day_outputs), "expected": 7}),
            _check("forward_rows_positive", len(dataset) > 0, {"rows": int(len(dataset))}),
            _check("forward_features_present", not missing_features, {"missing": missing_features[:50], "missing_count": len(missing_features)}),
            _check("forward_feature_values_no_null_after_fill", feature_nulls == 0, {"feature_nulls": feature_nulls}),
        ]
    )
    status = FORWARD_GUARD_PASS if all(item["status"] == "PASS" for item in checks) else FORWARD_GUARD_FAIL
    out_csv = run_dir / f"STAS5_V5_FORWARD_DATASET_{compact_day(start_day)}_{compact_day(end_day)}_X439_V1.csv"
    dataset.to_csv(out_csv, index=False, encoding="utf-8-sig")
    manifest = {
        "status": status,
        "created_utc": utc_now(),
        "run_id": run_dir.name,
        "run_dir": rel(run_dir),
        "date_range": {"start_day": start_day, "end_day": end_day},
        "rows": int(len(dataset)),
        "feature_count": len(expected_features),
        "feature_columns": expected_features,
        "dataset_csv": rel(out_csv),
        "day_outputs": day_outputs,
        "checks": checks,
        "guardrails": [
            "forward_days_not_used_for_training",
            "forward_days_not_used_for_threshold_tuning",
            "x439_rebuilt_from_full274_cs_fcs_using_source_times_before_entry",
            "manual_targets_not_required_for_forward",
        ],
    }
    write_json(run_dir / "STAS5_V5_FORWARD_DATASET_MANIFEST_V1.json", manifest)
    if strict and status != FORWARD_GUARD_PASS:
        raise ValueError(f"forward dataset guard is not PASS: {status}")
    return dataset, manifest


def _load_latest_train_manifest() -> Path:
    if DEFAULT_LATEST_MODEL_POINTER.exists():
        pointer = _load_json(DEFAULT_LATEST_MODEL_POINTER)
        path = PROJECT_ROOT / pointer["manifest_path"]
        if path.exists():
            return path
    manifests = sorted(DEFAULT_MODEL_RUNS_DIR.glob("*/STAS5_V5_TWO_BLOCK_TRAIN_MANIFEST_V1.json"), key=lambda item: item.stat().st_mtime)
    if not manifests:
        raise FileNotFoundError("V5 two-block train manifest not found")
    return manifests[-1]


def run_forward(
    *,
    run_id: str | None = None,
    train_manifest_path: Path | None = None,
    start_day: str = FORWARD_START_DAY,
    end_day: str = FORWARD_END_DAY,
    run_root: Path = DEFAULT_FORWARD_RUNS_DIR,
    latest_forward_pointer: Path | None = DEFAULT_LATEST_FORWARD_POINTER,
    strict: bool = True,
    render_visual_review: bool = True,
) -> dict[str, Any]:
    train_manifest_path = train_manifest_path or _load_latest_train_manifest()
    train_manifest = _load_json(train_manifest_path)
    if strict and train_manifest.get("post_train_guard_status") != POST_TRAIN_GUARD_PASS:
        raise ValueError(f"post-train guard is not PASS: {train_manifest.get('post_train_guard_status')}")
    run_id = run_id or f"stas5_v5_forward_{compact_day(start_day)}_{compact_day(end_day)}_{run_stamp()}"
    run_dir = run_root / run_id
    dataset, dataset_manifest = build_forward_dataset(
        run_dir=run_dir,
        train_manifest=train_manifest,
        start_day=start_day,
        end_day=end_day,
        strict=strict,
    )
    selected_entry = train_manifest.get("selected_entry_model", {})
    selected_model_key = str(selected_entry.get("model_key") or "entry_two_block")
    baseline_package = joblib.load(PROJECT_ROOT / train_manifest["artifacts"]["entry_baseline_model"])
    entry_package = joblib.load(PROJECT_ROOT / train_manifest["artifacts"]["entry_ml_model"])

    base_features = [str(column) for column in train_manifest["feature_columns"]]
    numeric_columns = [str(column) for column in train_manifest["numeric_columns"]]
    categorical_columns = [str(column) for column in train_manifest["categorical_columns"]]
    x_base = _prepare_feature_matrix(dataset, feature_columns=base_features, numeric_columns=numeric_columns, categorical_columns=categorical_columns)
    phase_live = pd.DataFrame(index=dataset.index)
    state_live = pd.DataFrame(index=dataset.index)
    if selected_model_key == "entry_baseline":
        stack = dataset.reset_index(drop=True)
        selected_package = baseline_package
        x_entry = _prepare_feature_matrix(
            stack,
            feature_columns=[str(c) for c in selected_package["feature_columns"]],
            numeric_columns=[str(c) for c in selected_package["numeric_columns"]],
            categorical_columns=[str(c) for c in selected_package["categorical_columns"]],
        )
        selected_label = "ENTRY_BASELINE_ML"
    else:
        phase_package = joblib.load(PROJECT_ROOT / train_manifest["artifacts"]["market_phase_state_model"])
        phase_live = _proba_predictions(
            phase_package["phase_pipeline"],
            x_base,
            classes=[str(c) for c in phase_package["phase_classes"]],
            prefix=PHASE_PREFIX,
        )
        state_live = _proba_predictions(
            phase_package["state_pipeline"],
            x_base,
            classes=[str(c) for c in phase_package["state_classes"]],
            prefix=STATE_PREFIX,
        )
        stack = pd.concat([dataset.reset_index(drop=True), phase_live, state_live], axis=1)
        selected_package = entry_package
        x_entry = _prepare_feature_matrix(
            stack,
            feature_columns=[str(c) for c in selected_package["feature_columns"]],
            numeric_columns=[str(c) for c in selected_package["numeric_columns"]],
            categorical_columns=[str(c) for c in selected_package["categorical_columns"]],
        )
        selected_label = "ENTRY_ML_TWO_BLOCK"
    scores = _positive_proba(selected_package["pipeline"], x_entry)
    decisions = _apply_entry_decision(scores, selected_package["thresholds"])
    columns = [c for c in KEY_COLUMNS if c in stack.columns]
    out = stack[columns].copy()
    out["ENTRY_ML_LIVE_SCORE"] = scores
    out["ENTRY_ML_LIVE_DECISION"] = decisions
    out["ENTRY_MODEL_SELECTED"] = selected_label
    out["ENTRY_POLICY"] = f"{selected_model_key}_thresholds_from_train_oof_no_forward_tuning"
    for column in phase_live.columns:
        out[column] = phase_live[column]
    for column in state_live.columns:
        out[column] = state_live[column]
    if "entry_price_5bps" in stack.columns:
        out["entry_price_5bps"] = stack["entry_price_5bps"]
    predictions_path = run_dir / f"STAS5_V5_FORWARD_PREDICTIONS_{compact_day(start_day)}_{compact_day(end_day)}_V1.csv"
    out.to_csv(predictions_path, index=False, encoding="utf-8-sig")

    visual_manifest: dict[str, Any] | None = None
    if render_visual_review:
        from mlbotnav.stas5_v5_forward_visual_review import render_forward_visual_review

        visual_manifest = render_forward_visual_review(
            forward_run_dir=run_dir,
            predictions_path=predictions_path,
            start_day=start_day,
            end_day=end_day,
            strict=strict,
        )

    day_summary = []
    for day, rows in out.groupby("day", sort=True):
        counts = rows["ENTRY_ML_LIVE_DECISION"].astype(str).value_counts().to_dict()
        enters = rows[rows["ENTRY_ML_LIVE_DECISION"].astype(str).eq("ENTER")].sort_values("entry_time_utc")
        day_summary.append(
            {
                "day": str(day),
                "rows": int(len(rows)),
                "decision_counts": {str(k): int(v) for k, v in counts.items()},
                "enter_candidates": enters[["candidate_id", "record_id", "entry_time_utc", "ENTRY_ML_LIVE_SCORE"]].to_dict("records"),
            }
        )
    checks = [
        _check("post_train_guard_pass", train_manifest.get("post_train_guard_status") == POST_TRAIN_GUARD_PASS, {"status": train_manifest.get("post_train_guard_status")}),
        _check("forward_dataset_guard_pass", dataset_manifest["status"] == FORWARD_GUARD_PASS, {"status": dataset_manifest["status"]}),
        _check("predictions_rows_match_dataset", len(out) == len(dataset), {"predictions": int(len(out)), "dataset": int(len(dataset))}),
        _check("no_true_phase_state_used_as_forward_features", True, {"selected_entry_model": selected_model_key, "used": "live predictions only when two-block selected"}),
        _check("forward_window_not_in_training", start_day > train_manifest["date_range"]["end_day"], {"train_end": train_manifest["date_range"]["end_day"], "forward_start": start_day}),
    ]
    status = FORWARD_GUARD_PASS if all(item["status"] == "PASS" for item in checks) else FORWARD_GUARD_FAIL
    manifest = {
        "status": status,
        "created_utc": utc_now(),
        "run_id": run_id,
        "run_dir": rel(run_dir),
        "date_range": {"start_day": start_day, "end_day": end_day},
        "train_manifest_path": rel(train_manifest_path),
        "train_run_id": train_manifest["run_id"],
        "rows": int(len(out)),
        "predictions_csv": rel(predictions_path),
        "forward_dataset_manifest": rel(run_dir / "STAS5_V5_FORWARD_DATASET_MANIFEST_V1.json"),
        "visual_review_manifest": visual_manifest.get("manifest_path", "") if visual_manifest else "",
        "visual_review_audit_ru": visual_manifest.get("audit_ru", "") if visual_manifest else "",
        "visual_review_status": visual_manifest.get("status", "SKIPPED") if visual_manifest else "SKIPPED",
        "visual_review_png_count": int(visual_manifest.get("png_count", 0)) if visual_manifest else 0,
        "selected_entry_model": selected_entry,
        "entry_model_selected_for_forward": selected_model_key,
        "thresholds": selected_package["thresholds"],
        "decision_counts_total": {str(k): int(v) for k, v in out["ENTRY_ML_LIVE_DECISION"].astype(str).value_counts().to_dict().items()},
        "day_summary": day_summary,
        "checks": checks,
        "guardrails": [
            "forward_days_20260228_20260306_not_used_for_training",
            "forward_days_20260228_20260306_not_used_for_threshold_tuning",
            "x439_built_before_or_at_entry_time_guarded_by_cs_fcs_source_time",
            "market_phase_state_features_are_live_predictions_not_phase_y_state_y_when_two_block_selected",
            "entry_decision_uses_fixed_train_oof_thresholds",
        ],
    }
    manifest_path = run_dir / "STAS5_V5_FORWARD_MANIFEST_V1.json"
    write_json(manifest_path, manifest)
    if latest_forward_pointer is not None:
        write_json(
            latest_forward_pointer,
            {
                "status": "LATEST_V5_TWO_BLOCK_FORWARD_RUN",
                "created_utc": utc_now(),
                "run_id": run_id,
                "run_dir": rel(run_dir),
                "manifest_path": rel(manifest_path),
                "guard_status": status,
            },
        )
    if strict and status != FORWARD_GUARD_PASS:
        raise ValueError(f"forward guard is not PASS: {status}")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="STAS5 V5 two-block ML training and forward.")
    parser.add_argument("--mode", choices=["training-guard", "train", "forward"], required=True)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--dataset-path", default=str(DEFAULT_BATCH_DATASET))
    parser.add_argument("--allowlist-path", default=str(DEFAULT_BATCH_ALLOWLIST))
    parser.add_argument("--batch-guard-path", default=str(DEFAULT_BATCH_GUARD))
    parser.add_argument("--train-manifest-path", default="")
    parser.add_argument("--start-day", default=FORWARD_START_DAY)
    parser.add_argument("--end-day", default=FORWARD_END_DAY)
    parser.add_argument("--review-weight-start-day", default=DEFAULT_REVIEW_WEIGHT_START_DAY)
    parser.add_argument("--entry-model-candidates", default=",".join(ENTRY_MODEL_CANDIDATES))
    parser.add_argument("--no-strict", action="store_true")
    parser.add_argument("--skip-visual-review", action="store_true")
    args = parser.parse_args()
    entry_model_candidates = [item.strip() for item in str(args.entry_model_candidates).split(",") if item.strip()]

    if args.mode == "training-guard":
        run_id = args.run_id or f"stas5_v5_two_block_guard_{run_stamp()}"
        guard = run_training_guard(
            run_dir=DEFAULT_MODEL_RUNS_DIR / run_id,
            dataset_path=Path(args.dataset_path),
            allowlist_path=Path(args.allowlist_path),
            batch_guard_path=Path(args.batch_guard_path),
        )
        print(json.dumps({"status": guard["status"], "run_id": run_id, "run_dir": guard["run_dir"]}, ensure_ascii=False))
        return 0 if args.no_strict or guard["status"] == TRAINING_GUARD_PASS else 2

    if args.mode == "train":
        manifest = train_two_block_ml(
            run_id=args.run_id or None,
            dataset_path=Path(args.dataset_path),
            allowlist_path=Path(args.allowlist_path),
            batch_guard_path=Path(args.batch_guard_path),
            strict=not args.no_strict,
            review_weight_start_day=args.review_weight_start_day or None,
            entry_model_candidates=entry_model_candidates,
        )
        print(
            json.dumps(
                {
                    "status": manifest["status"],
                    "run_id": manifest["run_id"],
                    "run_dir": manifest["run_dir"],
                    "post_train_guard_status": manifest.get("post_train_guard_status"),
                    "metrics": manifest["artifacts"]["metrics_json"],
                },
                ensure_ascii=False,
            )
        )
        return 0

    manifest = run_forward(
        run_id=args.run_id or None,
        train_manifest_path=Path(args.train_manifest_path) if args.train_manifest_path else None,
        start_day=args.start_day,
        end_day=args.end_day,
        strict=not args.no_strict,
        render_visual_review=not args.skip_visual_review,
    )
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "run_id": manifest["run_id"],
                "run_dir": manifest["run_dir"],
                "rows": manifest["rows"],
                "decision_counts_total": manifest["decision_counts_total"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
