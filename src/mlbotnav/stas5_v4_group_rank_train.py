from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from mlbotnav.stas5_common import STAS5_ARTIFACTS_DIR, forbidden_feature_matches, read_csv, rel, run_stamp, utc_now, write_json
from mlbotnav.stas5_entry_ranker_train import _build_pipeline, _positive_proba, _prepare_feature_matrix
from mlbotnav.stas5_v4_group_rank_dataset import (
    DEFAULT_V4_DATASET_MANIFEST_PATH,
    DEFAULT_V4_DATASET_PATH,
    V4_GROUP_MODEL_FEATURE_COLUMNS,
)


STATUS = "STAS5_V4_GROUP_RANKER_READY_20260501_20260525"
MODEL_BASENAME = "stas5_v4_group_ranker_20260501_20260525_v0"
DEFAULT_V4_MODEL_DIR = STAS5_ARTIFACTS_DIR / "v4" / "model"
DEFAULT_V4_MODEL_RUNS_DIR = DEFAULT_V4_MODEL_DIR / "runs"
DEFAULT_V4_MODEL_PATH = DEFAULT_V4_MODEL_DIR / f"{MODEL_BASENAME}.joblib"
DEFAULT_V4_MODEL_MANIFEST_PATH = DEFAULT_V4_MODEL_DIR / f"{MODEL_BASENAME}.manifest.json"
DEFAULT_V4_TRAIN_PREDICTIONS_PATH = DEFAULT_V4_MODEL_DIR / f"{MODEL_BASENAME}.train_predictions.csv"


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


def _dcg(values: list[float]) -> float:
    return float(sum(rel / np.log2(idx + 2) for idx, rel in enumerate(values)))


def group_rank_metrics(df: pd.DataFrame, *, score_column: str) -> dict[str, Any]:
    rows = df.copy()
    rows["is_group_winner"] = pd.to_numeric(rows["is_group_winner"], errors="coerce").fillna(0).astype(int)
    rows[score_column] = pd.to_numeric(rows[score_column], errors="coerce").fillna(-1.0)

    trade_groups = []
    top1_hits = 0
    top2_hits = 0
    reciprocal_ranks: list[float] = []
    ndcg_values: list[float] = []
    bad_top1 = 0
    good_alt_top1 = 0
    top1_rows: list[dict[str, Any]] = []

    for group_id, group in rows.groupby("group_id", sort=False):
        if int(group["is_group_winner"].sum()) != 1:
            continue
        ranked = group.sort_values([score_column, "entry_time_utc", "record_id"], ascending=[False, True, True]).reset_index(drop=True)
        winner_positions = ranked.index[ranked["is_group_winner"] == 1].tolist()
        if not winner_positions:
            continue
        winner_rank = int(winner_positions[0]) + 1
        top1 = ranked.iloc[0]
        top1_label = str(top1["rank_label"])
        trade_groups.append(str(group_id))
        top1_hits += int(winner_rank == 1)
        top2_hits += int(winner_rank <= 2)
        reciprocal_ranks.append(1.0 / winner_rank)
        rel = ranked["rank_label"].astype(str).map({"BEST_GOOD": 1.0, "GOOD_ALT": 0.5}).fillna(0.0).head(3).tolist()
        ideal = sorted(ranked["rank_label"].astype(str).map({"BEST_GOOD": 1.0, "GOOD_ALT": 0.5}).fillna(0.0).tolist(), reverse=True)[:3]
        ideal_dcg = _dcg(ideal)
        ndcg_values.append(_dcg(rel) / ideal_dcg if ideal_dcg > 0 else 0.0)
        bad_top1 += int(top1_label == "BAD_IN_GROUP")
        good_alt_top1 += int(top1_label == "GOOD_ALT")
        top1_rows.append(
            {
                "day": str(top1["day"]),
                "group_id": str(group_id),
                "candidate_id": str(top1["candidate_id"]),
                "rank_label": top1_label,
                "score": float(top1[score_column]),
            }
        )

    denom = max(len(trade_groups), 1)
    return {
        "trade_groups": len(trade_groups),
        "top1_group_accuracy": round(top1_hits / denom, 6),
        "winner_in_top2": round(top2_hits / denom, 6),
        "MRR": round(float(np.mean(reciprocal_ranks)) if reciprocal_ranks else 0.0, 6),
        "NDCG@3": round(float(np.mean(ndcg_values)) if ndcg_values else 0.0, 6),
        "bad_in_group_top1_count": int(bad_top1),
        "good_alt_top1_count": int(good_alt_top1),
        "top1_rows_by_day": {
            str(day): rows_day[["group_id", "candidate_id", "rank_label", "score"]].to_dict("records")
            for day, rows_day in pd.DataFrame(top1_rows).groupby("day", sort=True)
        }
        if top1_rows
        else {},
    }


def apply_v4_decision_policy(
    rows: pd.DataFrame,
    *,
    score_column: str,
    enter_threshold: float = 0.50,
    unsure_threshold: float = 0.35,
    min_enter_per_day: int = 2,
    soft_max_enter_per_day: int = 8,
) -> pd.DataFrame:
    out = rows.copy()
    out[score_column] = pd.to_numeric(out[score_column], errors="coerce").fillna(0.0)
    out["V4_GROUP_SCORE_RANK"] = (
        out.groupby("group_id", sort=False)[score_column].rank(method="first", ascending=False).astype(int)
    )
    out["V4_IS_GROUP_TOP1"] = (out["V4_GROUP_SCORE_RANK"] == 1).astype(int)
    out["V4_DECISION"] = "SKIP"
    out.loc[(out["V4_GROUP_SCORE_RANK"] == 2) & (out[score_column] >= unsure_threshold), "V4_DECISION"] = "UNSURE"

    for day, day_rows in out.groupby("day", sort=False):
        top_rows = day_rows[day_rows["V4_IS_GROUP_TOP1"] == 1].sort_values(score_column, ascending=False)
        selected_idx: list[Any] = []
        for idx, row in top_rows.iterrows():
            if len(selected_idx) < min_enter_per_day or float(row[score_column]) >= enter_threshold:
                selected_idx.append(idx)
            if len(selected_idx) >= soft_max_enter_per_day:
                break
        out.loc[selected_idx, "V4_DECISION"] = "ENTER"
        unsure_top_idx = top_rows[(top_rows[score_column] >= unsure_threshold) & (~top_rows.index.isin(selected_idx))].index
        out.loc[unsure_top_idx, "V4_DECISION"] = "UNSURE"
    return out


def _decision_counts_by_day(rows: pd.DataFrame) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for day, day_rows in rows.groupby("day", sort=True):
        counts = day_rows["V4_DECISION"].astype(str).value_counts().to_dict()
        out.append(
            {
                "day": str(day),
                "rows": int(len(day_rows)),
                "ENTER": int(counts.get("ENTER", 0)),
                "UNSURE": int(counts.get("UNSURE", 0)),
                "SKIP": int(counts.get("SKIP", 0)),
            }
        )
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
    y = train["target_v4_winner"].to_numpy(dtype=int)
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


def train_v4_group_ranker(
    *,
    dataset_path: Path = DEFAULT_V4_DATASET_PATH,
    dataset_manifest_path: Path = DEFAULT_V4_DATASET_MANIFEST_PATH,
    model_path: Path = DEFAULT_V4_MODEL_PATH,
    manifest_path: Path = DEFAULT_V4_MODEL_MANIFEST_PATH,
    predictions_path: Path = DEFAULT_V4_TRAIN_PREDICTIONS_PATH,
    enter_threshold: float = 0.50,
    unsure_threshold: float = 0.35,
    strict: bool = True,
) -> tuple[dict[str, Any], pd.DataFrame]:
    dataset_manifest = _load_json(dataset_manifest_path)
    if strict and dataset_manifest.get("status") != "PASS":
        raise ValueError(f"V4 dataset manifest is not PASS: {dataset_manifest.get('status')}")

    feature_columns = [str(column) for column in dataset_manifest["feature_columns"]]
    numeric_columns = [str(column) for column in dataset_manifest.get("numeric_columns", []) if column in feature_columns]
    categorical_columns = [str(column) for column in dataset_manifest.get("categorical_columns", []) if column in feature_columns]
    missing_group_features = [column for column in V4_GROUP_MODEL_FEATURE_COLUMNS if column not in feature_columns]
    if missing_group_features:
        raise ValueError(f"missing required V4 group features: {missing_group_features}")
    forbidden = forbidden_feature_matches(feature_columns)
    if forbidden:
        raise ValueError(f"forbidden feature columns: {forbidden}")

    train = read_csv(dataset_path)
    train["target_v4_winner"] = train["rank_label"].map(_target).astype(int)
    if train["target_v4_winner"].nunique() != 2:
        raise ValueError("V4 group-rank training data must contain winners and losers")
    bad_reason_missing = train[
        train["rank_label"].astype(str).isin(["BAD_IN_GROUP", "NO_TRADE_GROUP"])
        & train["primary_reason_code"].astype(str).str.strip().eq("")
    ]
    if strict and len(bad_reason_missing):
        raise ValueError(f"BAD/NO_TRADE rows without reason: {len(bad_reason_missing)}")

    oof, folds = _run_leave_one_day_scores(
        train,
        feature_columns=feature_columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
    )
    train_with_oof = train.copy()
    train_with_oof["V4_OOF_GROUP_RANK_SCORE"] = oof
    train_with_oof = apply_v4_decision_policy(
        train_with_oof,
        score_column="V4_OOF_GROUP_RANK_SCORE",
        enter_threshold=enter_threshold,
        unsure_threshold=unsure_threshold,
    )

    x = _prepare_feature_matrix(
        train,
        feature_columns=feature_columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
    )
    y = train["target_v4_winner"].to_numpy(dtype=int)
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
        + [column for column in V4_GROUP_MODEL_FEATURE_COLUMNS if column in train.columns]
    ].copy()
    predictions["V4_OOF_GROUP_RANK_SCORE"] = oof
    predictions["V4_TRAIN_FIT_GROUP_RANK_SCORE"] = fit_scores
    predictions = apply_v4_decision_policy(
        predictions,
        score_column="V4_OOF_GROUP_RANK_SCORE",
        enter_threshold=enter_threshold,
        unsure_threshold=unsure_threshold,
    )
    predictions_path.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(predictions_path, index=False, encoding="utf-8-sig")

    oof_group_metrics = group_rank_metrics(train_with_oof, score_column="V4_OOF_GROUP_RANK_SCORE")
    fit_scored = train.copy()
    fit_scored["V4_TRAIN_FIT_GROUP_RANK_SCORE"] = fit_scores
    fit_group_metrics = group_rank_metrics(fit_scored, score_column="V4_TRAIN_FIT_GROUP_RANK_SCORE")
    y_true = train["target_v4_winner"].to_numpy(dtype=int)

    package = {
        "pipeline": final_model,
        "feature_columns": feature_columns,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "thresholds": {"enter": enter_threshold, "unsure": unsure_threshold},
        "model_id": "STAS5_V4_HUMAN_STYLE_GROUP_RANKER_V0",
        "model_feature_set": "v2_context_274_plus_v4_group_features",
        "decision_policy": {
            "type": "rank_inside_group_then_day_top_groups",
            "enter_threshold": enter_threshold,
            "unsure_threshold": unsure_threshold,
            "min_enter_per_day": 2,
            "soft_max_enter_per_day": 8,
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
        "train_base_legacy_window": dataset_manifest.get("train_base_legacy_window"),
        "user_corrected_group_window": dataset_manifest.get("user_corrected_group_window"),
        "label_counts": dataset_manifest.get("rank_label_counts"),
        "source_counts": dataset_manifest.get("source_counts"),
        "winner_count": dataset_manifest.get("winner_count"),
        "feature_count": len(feature_columns),
        "v2_context_feature_count": dataset_manifest.get("v2_context_feature_count"),
        "v4_group_feature_count": len(V4_GROUP_MODEL_FEATURE_COLUMNS),
        "feature_columns": feature_columns,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "model_type": "LogisticRegression pointwise scorer with mandatory group-relative features",
        "ranker_policy": "final decisions are rank-inside-group, not row-by-row KEEP/CUT thresholding",
        "thresholds": package["thresholds"],
        "folds": folds,
        "metrics": {
            "row_auc_oof_reference_only": _row_auc(y_true, oof),
            "oof_group_rank": oof_group_metrics,
            "train_fit_group_rank": fit_group_metrics,
            "decision_counts_total_oof": predictions["V4_DECISION"].astype(str).value_counts().to_dict(),
            "decision_counts_by_day_oof": _decision_counts_by_day(predictions),
        },
        "guardrails": [
            "AUC_is_reference_only_not_main_metric",
            "top1_group_accuracy_winner_in_top2_MRR_NDCG_are_main_metrics",
            "old_ML_score_decision_not_features",
            "postfact_future_tp_stas3_exit_not_features",
            "GOOD_ALT_is_not_winner_but_kept_as_near-good_context",
            "NO_TRADE_GROUP_rows_train_as_negative_context",
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
    parser = argparse.ArgumentParser(description="Train STAS5 V4 human-style group ranker.")
    parser.add_argument("--dataset-path", default=str(DEFAULT_V4_DATASET_PATH))
    parser.add_argument("--dataset-manifest-path", default=str(DEFAULT_V4_DATASET_MANIFEST_PATH))
    parser.add_argument("--run-id", default="")
    parser.add_argument("--run-root", default=str(DEFAULT_V4_MODEL_RUNS_DIR))
    parser.add_argument("--model-path", default="")
    parser.add_argument("--manifest-path", default="")
    parser.add_argument("--predictions-path", default="")
    parser.add_argument("--enter-threshold", type=float, default=0.50)
    parser.add_argument("--unsure-threshold", type=float, default=0.35)
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()

    run_id = args.run_id or f"stas5_v4_train_{run_stamp()}"
    paths = _run_paths(run_id, Path(args.run_root))
    model_path = Path(args.model_path) if args.model_path else paths["model_path"]
    manifest_path = Path(args.manifest_path) if args.manifest_path else paths["manifest_path"]
    predictions_path = Path(args.predictions_path) if args.predictions_path else paths["predictions_path"]
    manifest, _predictions = train_v4_group_ranker(
        dataset_path=Path(args.dataset_path),
        dataset_manifest_path=Path(args.dataset_manifest_path),
        model_path=model_path,
        manifest_path=manifest_path,
        predictions_path=predictions_path,
        enter_threshold=args.enter_threshold,
        unsure_threshold=args.unsure_threshold,
        strict=not args.no_strict,
    )
    write_json(
        DEFAULT_V4_MODEL_DIR / "STAS5_V4_LATEST_MODEL_RUN.json",
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
            "metrics": manifest["metrics"],
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
