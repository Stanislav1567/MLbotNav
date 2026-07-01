from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

from mlbotnav.dataset import FEATURE_COLUMNS, RUNTIME_ACTION_COLUMNS


@dataclass(frozen=True)
class FoldResult:
    fold_id: int
    train_rows: int
    test_rows: int
    accuracy: float
    f1: float
    auc: float


def create_model(model_type: str):
    mt = (model_type or "logreg").strip().lower()
    if mt in {"logreg", "logistic", "logistic_regression"}:
        return LogisticRegression(max_iter=3000, solver="liblinear")
    if mt in {"lightgbm", "lgbm", "lgb"}:
        try:
            from lightgbm import LGBMClassifier
        except Exception as e:
            raise ImportError("lightgbm is not available") from e
        return LGBMClassifier(
            n_estimators=250,
            learning_rate=0.05,
            num_leaves=63,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="binary",
            random_state=42,
            n_jobs=-1,
            verbosity=-1,
        )
    if mt in {"xgboost", "xgb"}:
        try:
            from xgboost import XGBClassifier
        except Exception as e:
            raise ImportError("xgboost is not available") from e
        return XGBClassifier(
            n_estimators=250,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=42,
            n_jobs=-1,
            tree_method="hist",
            verbosity=0,
        )
    raise ValueError(f"Unsupported model_type: {model_type}")


def leakage_sanity_checks(df: pd.DataFrame) -> list[str]:
    issues: list[str] = []
    if not df["open_time_utc"].is_monotonic_increasing:
        issues.append("timestamps_not_monotonic")
    if df["open_time_utc"].duplicated().any():
        issues.append("duplicate_timestamps")
    if "future_return" in df.columns and df["future_return"].isna().any():
        issues.append("future_return_has_nan")
    return issues


def walk_forward_validate(
    df: pd.DataFrame,
    *,
    min_train_rows: int = 1200,
    n_folds: int = 4,
    feature_columns: list[str] | None = None,
    model_type: str = "logreg",
) -> tuple[list[FoldResult], pd.DataFrame]:
    if len(df) <= min_train_rows + n_folds * 20:
        raise ValueError(f"Not enough rows for walk-forward: {len(df)}")

    fold_size = max(20, (len(df) - min_train_rows) // n_folds)
    results: list[FoldResult] = []
    oof_parts: list[pd.DataFrame] = []

    cols = feature_columns if feature_columns is not None else FEATURE_COLUMNS

    for fold in range(n_folds):
        train_end = min_train_rows + fold * fold_size
        test_end = min(len(df), train_end + fold_size)
        if test_end - train_end < 20:
            continue

        train = df.iloc[:train_end].copy()
        test = df.iloc[train_end:test_end].copy()

        if train["open_time_utc"].max() >= test["open_time_utc"].min():
            raise ValueError("Temporal leakage risk: train overlaps test by time")

        x_train = train[cols]
        y_train = train["target_up"]
        x_test = test[cols]
        y_test = test["target_up"]

        model = create_model(model_type)
        model.fit(x_train, y_train)
        prob = model.predict_proba(x_test)[:, 1]
        pred = (prob >= 0.5).astype(int)

        auc = float(roc_auc_score(y_test, prob)) if y_test.nunique() > 1 else 0.5
        res = FoldResult(
            fold_id=fold + 1,
            train_rows=int(len(train)),
            test_rows=int(len(test)),
            accuracy=float(accuracy_score(y_test, pred)),
            f1=float(f1_score(y_test, pred, zero_division=0)),
            auc=auc,
        )
        results.append(res)

        base_cols = [
            "open_time_utc",
            "close_time_utc",
            "open",
            "high",
            "low",
            "close",
            "future_return",
            "target_up",
            "atr14",
            "ema_gap",
        ]
        # Keep all feature-space columns in OOF output so runtime filters
        # (including trend hypotheses) evaluate on actual values, not on
        # missing-column fallbacks.
        optional_cols = list(FEATURE_COLUMNS) + list(RUNTIME_ACTION_COLUMNS) + ["ema20", "ema50", "ema200"]
        ordered_cols = list(dict.fromkeys(base_cols + optional_cols))
        cols_out = [c for c in ordered_cols if c in test.columns]
        part = test[cols_out].copy()
        part["prob_up"] = prob
        part["pred_up"] = pred
        part["fold_id"] = fold + 1
        oof_parts.append(part)

    if not oof_parts:
        raise ValueError("No walk-forward folds were produced")

    oof = pd.concat(oof_parts, ignore_index=True).sort_values("open_time_utc").reset_index(drop=True)
    return results, oof


def aggregate_fold_metrics(folds: list[FoldResult]) -> dict:
    if not folds:
        return {"accuracy_mean": 0.0, "f1_mean": 0.0, "auc_mean": 0.0}
    return {
        "accuracy_mean": float(np.mean([f.accuracy for f in folds])),
        "f1_mean": float(np.mean([f.f1 for f in folds])),
        "auc_mean": float(np.mean([f.auc for f in folds])),
        "folds": [
            {
                "fold_id": f.fold_id,
                "train_rows": f.train_rows,
                "test_rows": f.test_rows,
                "accuracy": f.accuracy,
                "f1": f.f1,
                "auc": f.auc,
            }
            for f in folds
        ],
    }
