from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from mlbotnav.stas5_common import STAS5_ARTIFACTS_DIR, read_csv, rel, run_stamp, utc_now, write_json
from mlbotnav.stas5_entry_ranker_train import _build_pipeline, _positive_proba, _prepare_feature_matrix
from mlbotnav.stas5_v4_group_rank_train import group_rank_metrics
from mlbotnav.stas5_v4l_live_safe_dataset import (
    DEFAULT_V4L_DATASET_MANIFEST_PATH,
    DEFAULT_V4L_DATASET_PATH,
    V4L_GROUP_FEATURE_COLUMNS,
    v4l_forbidden_feature_matches,
)


STATUS = "STAS5_V4L_LIVE_SAFE_GROUP_RANKER_READY_20260501_20260525"
MODEL_BASENAME = "stas5_v4l_live_safe_group_ranker_20260501_20260525_v0"
DEFAULT_V4L_MODEL_DIR = STAS5_ARTIFACTS_DIR / "v4l" / "model"
DEFAULT_V4L_MODEL_RUNS_DIR = DEFAULT_V4L_MODEL_DIR / "runs"
DEFAULT_V4L_MODEL_PATH = DEFAULT_V4L_MODEL_DIR / f"{MODEL_BASENAME}.joblib"
DEFAULT_V4L_MODEL_MANIFEST_PATH = DEFAULT_V4L_MODEL_DIR / f"{MODEL_BASENAME}.manifest.json"
DEFAULT_V4L_TRAIN_PREDICTIONS_PATH = DEFAULT_V4L_MODEL_DIR / f"{MODEL_BASENAME}.train_predictions.csv"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _target(label: Any) -> int:
    return 1 if str(label).strip().upper() == "BEST_GOOD" else 0


def _sample_weights(labels: pd.Series) -> np.ndarray:
    mapping = {
        "BEST_GOOD": 3.0,
        "GOOD_ALT": 0.45,
        "BAD_IN_GROUP": 1.0,
        "NO_TRADE_GROUP": 0.7,
    }
    return labels.astype(str).str.upper().map(mapping).fillna(0.75).to_numpy(dtype=float)


def apply_v4l_live_decision_policy(
    rows: pd.DataFrame,
    *,
    score_column: str,
    enter_threshold: float = 0.50,
    unsure_threshold: float = 0.35,
    require_lowest_so_far: bool = True,
    one_enter_per_group: bool = True,
) -> pd.DataFrame:
    out = rows.copy()
    out[score_column] = pd.to_numeric(out[score_column], errors="coerce").fillna(0.0)
    out["V4L_LIVE_SCORE"] = out[score_column]
    out["V4L_LIVE_DECISION"] = "SKIP"
    out["V4L_LIVE_GROUP_ENTERED_BEFORE"] = 0
    out["V4L_LIVE_SCORE_BEST_SO_FAR"] = 0.0
    out["V4L_LIVE_SCORE_IMPROVED_SO_FAR"] = 0

    for _group_id, group in out.sort_values(["day", "group_id", "entry_time_utc", "record_id"]).groupby(
        "group_id", sort=False, dropna=False
    ):
        entered = False
        best_score = -np.inf
        for idx, row in group.iterrows():
            score = float(row[score_column])
            improved = score > best_score
            best_score = max(best_score, score)
            can_enter_by_low = (not require_lowest_so_far) or int(row.get("v4l_is_lowest_so_far", 0)) == 1
            can_enter_by_group = (not one_enter_per_group) or not entered
            decision = "SKIP"
            if score >= enter_threshold and can_enter_by_low and can_enter_by_group:
                decision = "ENTER"
                entered = True
            elif score >= unsure_threshold:
                decision = "UNSURE"
            out.loc[idx, "V4L_LIVE_DECISION"] = decision
            out.loc[idx, "V4L_LIVE_GROUP_ENTERED_BEFORE"] = int(entered and decision != "ENTER")
            out.loc[idx, "V4L_LIVE_SCORE_BEST_SO_FAR"] = round(float(best_score), 10)
            out.loc[idx, "V4L_LIVE_SCORE_IMPROVED_SO_FAR"] = int(improved)
    return out


def _run_leave_one_day_scores(
    train: pd.DataFrame,
    *,
    feature_columns: list[str],
    numeric_columns: list[str],
    categorical_columns: list[str],
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    x = _prepare_feature_matrix(
        train,
        feature_columns=feature_columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
    )
    y = train["target_v4l_winner"].to_numpy(dtype=int)
    weights = _sample_weights(train["rank_label"])
    days = train["day"].astype(str)
    oof = np.full(len(train), np.nan, dtype=float)
    folds: list[dict[str, Any]] = []
    for day in sorted(days.unique()):
        val_mask = days == day
        train_mask = ~val_mask
        if len(set(y[train_mask.to_numpy()])) < 2:
            continue
        model = _build_pipeline(numeric_columns=numeric_columns, categorical_columns=categorical_columns)
        model.fit(x.loc[train_mask], y[train_mask.to_numpy()], model__sample_weight=weights[train_mask.to_numpy()])
        oof[val_mask.to_numpy()] = _positive_proba(model, x.loc[val_mask])
        folds.append({"day": day, "train_rows": int(train_mask.sum()), "validation_rows": int(val_mask.sum())})
    if np.isnan(oof).any():
        missing_days = sorted(days[np.isnan(oof)].unique().tolist())
        raise ValueError(f"leave-one-day-out did not produce scores for all rows; missing days: {missing_days}")
    return oof, folds


def _row_auc(y: np.ndarray, scores: np.ndarray) -> float | None:
    try:
        return float(roc_auc_score(y, scores))
    except Exception:
        return None


def _decision_counts_by_day(rows: pd.DataFrame, *, decision_column: str = "V4L_LIVE_DECISION") -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for day, day_rows in rows.groupby("day", sort=True):
        counts = Counter(day_rows[decision_column].astype(str))
        winners = day_rows[pd.to_numeric(day_rows["is_group_winner"], errors="coerce").fillna(0).astype(int) == 1]
        enter_rows = day_rows[day_rows[decision_column].astype(str) == "ENTER"]
        out.append(
            {
                "day": str(day),
                "rows": int(len(day_rows)),
                "winners": int(len(winners)),
                "ENTER": int(counts.get("ENTER", 0)),
                "UNSURE": int(counts.get("UNSURE", 0)),
                "SKIP": int(counts.get("SKIP", 0)),
                "winner_enter_count": int(enter_rows["is_group_winner"].astype(int).sum()) if len(enter_rows) else 0,
            }
        )
    return out


def _live_decision_metrics(rows: pd.DataFrame, *, decision_column: str = "V4L_LIVE_DECISION") -> dict[str, Any]:
    scored = rows.copy()
    scored["is_group_winner"] = pd.to_numeric(scored["is_group_winner"], errors="coerce").fillna(0).astype(int)
    enter_rows = scored[scored[decision_column].astype(str) == "ENTER"]
    winner_rows = scored[scored["is_group_winner"] == 1]
    bad_enter_rows = enter_rows[enter_rows["rank_label"].astype(str).isin(["BAD_IN_GROUP", "NO_TRADE_GROUP"])]
    return {
        "decision_counts_total": scored[decision_column].astype(str).value_counts().to_dict(),
        "decision_counts_by_day": _decision_counts_by_day(scored, decision_column=decision_column),
        "enter_count": int(len(enter_rows)),
        "winner_enter_count": int(enter_rows["is_group_winner"].sum()) if len(enter_rows) else 0,
        "winner_recall_by_enter": round(float(enter_rows["is_group_winner"].sum()) / max(len(winner_rows), 1), 6)
        if len(enter_rows)
        else 0.0,
        "bad_or_no_trade_enter_count": int(len(bad_enter_rows)),
        "enter_candidates_by_day": {
            str(day): day_rows[["candidate_id", "group_id", "rank_label", "entry_time_utc", "V4L_LIVE_SCORE"]].to_dict("records")
            for day, day_rows in enter_rows.groupby("day", sort=True)
        }
        if len(enter_rows)
        else {},
    }


def train_v4l_live_safe_group_ranker(
    *,
    dataset_path: Path = DEFAULT_V4L_DATASET_PATH,
    dataset_manifest_path: Path = DEFAULT_V4L_DATASET_MANIFEST_PATH,
    model_path: Path = DEFAULT_V4L_MODEL_PATH,
    manifest_path: Path = DEFAULT_V4L_MODEL_MANIFEST_PATH,
    predictions_path: Path = DEFAULT_V4L_TRAIN_PREDICTIONS_PATH,
    enter_threshold: float = 0.50,
    unsure_threshold: float = 0.35,
    require_lowest_so_far: bool = True,
    strict: bool = True,
) -> tuple[dict[str, Any], pd.DataFrame]:
    dataset_manifest = _load_json(dataset_manifest_path)
    if strict and dataset_manifest.get("status") != "PASS":
        raise ValueError(f"V4L dataset manifest is not PASS: {dataset_manifest.get('status')}")

    feature_columns = [str(column) for column in dataset_manifest["feature_columns"]]
    numeric_columns = [str(column) for column in dataset_manifest.get("numeric_columns", []) if column in feature_columns]
    categorical_columns = [str(column) for column in dataset_manifest.get("categorical_columns", []) if column in feature_columns]
    missing_live_features = [column for column in V4L_GROUP_FEATURE_COLUMNS if column not in feature_columns]
    if missing_live_features:
        raise ValueError(f"missing required V4L live group features: {missing_live_features}")
    forbidden = v4l_forbidden_feature_matches(feature_columns)
    if forbidden:
        raise ValueError(f"forbidden V4L feature columns: {forbidden}")

    train = read_csv(dataset_path)
    train["target_v4l_winner"] = train["rank_label"].map(_target).astype(int)
    if train["target_v4l_winner"].nunique() != 2:
        raise ValueError("V4L training data must contain winners and losers")

    oof, folds = _run_leave_one_day_scores(
        train,
        feature_columns=feature_columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
    )
    train_with_oof = train.copy()
    train_with_oof["V4L_OOF_LIVE_SAFE_SCORE"] = oof
    train_with_oof = apply_v4l_live_decision_policy(
        train_with_oof,
        score_column="V4L_OOF_LIVE_SAFE_SCORE",
        enter_threshold=enter_threshold,
        unsure_threshold=unsure_threshold,
        require_lowest_so_far=require_lowest_so_far,
    )

    x = _prepare_feature_matrix(
        train,
        feature_columns=feature_columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
    )
    y = train["target_v4l_winner"].to_numpy(dtype=int)
    weights = _sample_weights(train["rank_label"])
    final_model = _build_pipeline(numeric_columns=numeric_columns, categorical_columns=categorical_columns)
    final_model.fit(x, y, model__sample_weight=weights)
    fit_scores = _positive_proba(final_model, x)

    predictions = train[
        [
            "day",
            "candidate_id",
            "record_id",
            "entry_time_utc",
            "entry_price_5bps",
            "group_id",
            "rank_label",
            "is_group_winner",
            "primary_reason_code",
            "v4_train_source",
        ]
        + [column for column in V4L_GROUP_FEATURE_COLUMNS if column in train.columns]
    ].copy()
    predictions["V4L_OOF_LIVE_SAFE_SCORE"] = oof
    predictions["V4L_TRAIN_FIT_LIVE_SAFE_SCORE"] = fit_scores
    predictions = apply_v4l_live_decision_policy(
        predictions,
        score_column="V4L_OOF_LIVE_SAFE_SCORE",
        enter_threshold=enter_threshold,
        unsure_threshold=unsure_threshold,
        require_lowest_so_far=require_lowest_so_far,
    )
    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(predictions_path, index=False, encoding="utf-8-sig")

    fit_scored = train.copy()
    fit_scored["V4L_TRAIN_FIT_LIVE_SAFE_SCORE"] = fit_scores
    package = {
        "pipeline": final_model,
        "feature_columns": feature_columns,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "thresholds": {"enter": enter_threshold, "unsure": unsure_threshold},
        "model_id": "STAS5_V4L_LIVE_SAFE_GROUP_RANKER_V0",
        "model_feature_set": "v2_context_274_plus_v4l_prefix_so_far_features",
        "decision_policy": {
            "type": "live_prefix_score_threshold_one_enter_per_active_group",
            "enter_threshold": enter_threshold,
            "unsure_threshold": unsure_threshold,
            "require_lowest_so_far": require_lowest_so_far,
            "one_enter_per_group": True,
            "no_daily_top_n_after_close": True,
        },
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
        "train_window": dataset_manifest.get("train_window"),
        "forward_eval_window_next": dataset_manifest.get("forward_eval_window_next"),
        "label_counts": dataset_manifest.get("rank_label_counts"),
        "source_counts": dataset_manifest.get("source_counts"),
        "winner_count": dataset_manifest.get("winner_count"),
        "feature_count": len(feature_columns),
        "v2_context_feature_count": dataset_manifest.get("v2_context_feature_count"),
        "v4l_live_safe_group_feature_count": len(V4L_GROUP_FEATURE_COLUMNS),
        "feature_columns": feature_columns,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "model_type": "LogisticRegression pointwise scorer with live-safe prefix group features",
        "ranker_policy": "live prefix score threshold; no full-group rank, no day-end top-N selection",
        "thresholds": package["thresholds"],
        "folds": folds,
        "metrics": {
            "row_auc_oof_reference_only": _row_auc(y, oof),
            "oof_group_score_rank_reference_only": group_rank_metrics(
                train_with_oof, score_column="V4L_OOF_LIVE_SAFE_SCORE"
            ),
            "train_fit_group_score_rank_reference_only": group_rank_metrics(
                fit_scored, score_column="V4L_TRAIN_FIT_LIVE_SAFE_SCORE"
            ),
            "oof_live_decision": _live_decision_metrics(predictions),
        },
        "guardrails": [
            "model_features_are_v4l_prefix_only_so_far_group_features",
            "full_group_low_full_group_rank_post_candidate_lower_low_are_forbidden",
            "forward_decisions_must_not_use_day_end_top_n",
            "past_decisions_are_not_rewritten_after_later_candidates",
            "old_ML_score_decision_not_features",
            "postfact_future_tp_stas3_exit_not_features",
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
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Train STAS5 V4L live-safe group ranker.")
    parser.add_argument("--dataset-path", default=str(DEFAULT_V4L_DATASET_PATH))
    parser.add_argument("--dataset-manifest-path", default=str(DEFAULT_V4L_DATASET_MANIFEST_PATH))
    parser.add_argument("--run-id", default="")
    parser.add_argument("--run-root", default=str(DEFAULT_V4L_MODEL_RUNS_DIR))
    parser.add_argument("--model-path", default="")
    parser.add_argument("--manifest-path", default="")
    parser.add_argument("--predictions-path", default="")
    parser.add_argument("--enter-threshold", type=float, default=0.50)
    parser.add_argument("--unsure-threshold", type=float, default=0.35)
    parser.add_argument("--allow-non-lowest-so-far", action="store_true")
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()

    run_id = args.run_id or f"stas5_v4l_train_{run_stamp()}"
    paths = _run_paths(run_id, Path(args.run_root))
    model_path = Path(args.model_path) if args.model_path else paths["model_path"]
    manifest_path = Path(args.manifest_path) if args.manifest_path else paths["manifest_path"]
    predictions_path = Path(args.predictions_path) if args.predictions_path else paths["predictions_path"]
    manifest, _predictions = train_v4l_live_safe_group_ranker(
        dataset_path=Path(args.dataset_path),
        dataset_manifest_path=Path(args.dataset_manifest_path),
        model_path=model_path,
        manifest_path=manifest_path,
        predictions_path=predictions_path,
        enter_threshold=args.enter_threshold,
        unsure_threshold=args.unsure_threshold,
        require_lowest_so_far=not args.allow_non_lowest_so_far,
        strict=not args.no_strict,
    )
    write_json(
        DEFAULT_V4L_MODEL_DIR / "STAS5_V4L_LATEST_MODEL_RUN.json",
        {
            "status": "LATEST_MODEL_RUN_POINTER",
            "created_utc": utc_now(),
            "run_id": run_id,
            "run_dir": manifest["run_dir"],
            "model_path": manifest["model_path"],
            "manifest_path": rel(manifest_path),
        },
    )
    print(
        {
            "status": manifest["status"],
            "run_id": run_id,
            "run_dir": manifest["run_dir"],
            "model_path": manifest["model_path"],
            "feature_count": manifest["feature_count"],
            "oof_live_decision": manifest["metrics"]["oof_live_decision"],
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
