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
    TRAIN_END_DAY,
    TRAIN_START_DAY,
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
from mlbotnav.stas5_v2_feature_snapshot_builder import (
    DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH,
    DEFAULT_V2_FEATURE_SNAPSHOT_PATH,
)
from mlbotnav.stas5_v2_leakage_guard import DEFAULT_V2_GUARD_REPORT_PATH
from mlbotnav.stas5_v2_pre_ml_audit import DEFAULT_V2_PRE_ML_AUDIT_JSON_PATH


STATUS = "STAS5_V2_CONTROLLED_MODEL_READY_NO_FORWARD_TUNING_NO_TP_NO_API_NO_STAS3"
MODEL_BASENAME = "stas5_v2_entry_ranker_20260501_20260514_v0"
DEFAULT_V2_MODEL_DIR = STAS5_ARTIFACTS_DIR / "v2" / "model"
DEFAULT_V2_MODEL_RUNS_DIR = DEFAULT_V2_MODEL_DIR / "runs"
DEFAULT_V2_MODEL_PATH = DEFAULT_V2_MODEL_DIR / f"{MODEL_BASENAME}.joblib"
DEFAULT_V2_MODEL_MANIFEST_PATH = DEFAULT_V2_MODEL_DIR / f"{MODEL_BASENAME}.manifest.json"
DEFAULT_V2_TRAIN_PREDICTIONS_PATH = DEFAULT_V2_MODEL_DIR / f"{MODEL_BASENAME}.train_predictions.csv"
DEFAULT_V2_ABLATION_JSON_PATH = DEFAULT_V2_MODEL_DIR / "stas5_v2_ablation_baseline_20260501_20260514_v0.json"
DEFAULT_V2_ABLATION_CSV_PATH = DEFAULT_V2_MODEL_DIR / "stas5_v2_ablation_baseline_20260501_20260514_v0.csv"
DEFAULT_V2_ABLATION_REPORT_PATH = DEFAULT_V2_MODEL_DIR / "STAS5_V2_ABLATION_BASELINE_20260501_20260514_RU.md"


V2_PREFIX_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("v2_combo_indicator", ("stas4_v2_combo_", "stas4_v2_indicator_")),
    ("v2_density_structure_divergence", ("stas4_v2_density_", "stas4_v2_structure_", "stas4_v2_div_")),
    ("v2_stas4_blocks", ("stas4_v2_block_",)),
    ("v2_pattern", ("stas4_v2_pattern_",)),
    ("v2_short_wave", ("stas5_v2_short_wave_",)),
    ("v2_risk_gate", ("stas5_v2_risk_", "stas5_v2_gate_")),
    ("v2_volume", ("stas4_v2_volume_",)),
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _feature_group(column: str, *, v1_columns: set[str]) -> str:
    if column in v1_columns:
        if column.startswith("pre_"):
            return "v1_stas2_pre_windows"
        if column.startswith("stas1_feature_"):
            return "v1_stas1_candidate"
        if column.startswith(("session_", "day_", "effective_", "real_")) or column in {"day_type", "is_weekend"}:
            return "v1_session_time"
        return "v1_other"
    for group, prefixes in V2_PREFIX_GROUPS:
        if column.startswith(prefixes):
            return group
    return "v2_other"


def _columns_by_group(feature_columns: list[str], *, v1_columns: set[str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for column in feature_columns:
        groups.setdefault(_feature_group(column, v1_columns=v1_columns), []).append(column)
    return groups


def _ordered_unique(columns: list[str]) -> list[str]:
    return list(dict.fromkeys(columns))


def _select_feature_sets(
    *,
    feature_columns: list[str],
    v1_feature_columns: list[str],
) -> dict[str, list[str]]:
    groups = _columns_by_group(feature_columns, v1_columns=set(v1_feature_columns))
    v1 = [column for column in v1_feature_columns if column in feature_columns]

    def add_groups(*names: str) -> list[str]:
        out = list(v1)
        for name in names:
            out.extend(groups.get(name, []))
        return _ordered_unique([column for column in out if column in feature_columns])

    return {
        "v1_baseline_111": v1,
        "v1_plus_combo_indicator": add_groups("v2_combo_indicator"),
        "v1_plus_density_structure_divergence": add_groups("v2_density_structure_divergence"),
        "v1_plus_stas4_blocks": add_groups("v2_stas4_blocks"),
        "v1_plus_pattern": add_groups("v2_pattern"),
        "v1_plus_short_wave": add_groups("v2_short_wave"),
        "v1_plus_risk_gate": add_groups("v2_risk_gate"),
        "v1_plus_volume": add_groups("v2_volume"),
        "full_v2_all_274": list(feature_columns),
    }


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
        oof[val_mask.to_numpy()] = _positive_proba(model, x.loc[val_mask])
        folds.append({"day": day, "train_rows": int(train_mask.sum()), "validation_rows": int(val_mask.sum())})
    if np.isnan(oof).any():
        raise ValueError("leave-one-day-out did not produce scores for all rows")
    return oof, folds


def _metrics_row(
    name: str,
    *,
    metrics: dict[str, Any],
    feature_count: int,
    numeric_count: int,
    categorical_count: int,
) -> dict[str, Any]:
    return {
        "feature_set": name,
        "feature_count": feature_count,
        "numeric_count": numeric_count,
        "categorical_count": categorical_count,
        "auc_leave_one_day_out": metrics.get("auc_leave_one_day_out"),
        "keep_recall_enter": metrics.get("keep_recall_enter"),
        "keep_recall_unsure_plus": metrics.get("keep_recall_unsure_plus"),
        "cut_precision_skip": metrics.get("cut_precision_skip"),
        "keep_with_yellow_x": metrics.get("keep_with_yellow_x"),
        "keep_with_yellow_x_recall_enter": metrics.get("keep_with_yellow_x_recall_enter"),
        "keep_with_yellow_x_recall_unsure_plus": metrics.get("keep_with_yellow_x_recall_unsure_plus"),
        "ENTER": metrics.get("decision_counts", {}).get("ENTER", 0),
        "UNSURE": metrics.get("decision_counts", {}).get("UNSURE", 0),
        "SKIP": metrics.get("decision_counts", {}).get("SKIP", 0),
    }


def run_v2_ablation_from_frames(
    *,
    snapshot: pd.DataFrame,
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

    df = snapshot.copy()
    df["target_keep"] = df["human_label"].map(label_target)
    train = df.dropna(subset=["target_keep"]).copy()
    train["target_keep"] = train["target_keep"].astype(int)
    if (train["day"].astype(str) > TRAIN_END_DAY).any():
        raise ValueError("forward days detected in V2 training data")
    if train["target_keep"].nunique() != 2:
        raise ValueError("V2 training data must contain both KEEP and CUT labels")

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
        "status": "STAS5_V2_ABLATION_BASELINE_READY",
        "created_utc": utc_now(),
        "train_window": {"start_day": TRAIN_START_DAY, "end_day": TRAIN_END_DAY},
        "rows": int(len(train)),
        "label_counts": train["human_label"].astype(str).value_counts().to_dict(),
        "threshold_policy": "fixed_train_policy_0p65_0p45_not_forward_tuned",
        "thresholds": {"enter": enter_threshold, "unsure": unsure_threshold},
        "feature_count": len(feature_columns),
        "v1_feature_count": len(v1_feature_columns),
        "feature_group_counts": {
            group: len(columns) for group, columns in _columns_by_group(feature_columns, v1_columns=set(v1_feature_columns)).items()
        },
        "ablation_rows": rows,
        "ablation_details": details,
        "guardrails": [
            "train_window_20260501_20260514_only",
            "forward_20260515_plus_not_used",
            "yellow_x_and_conflict_are_not_features",
            "no_postfact_future_stas3_tp_exit_features",
            "fixed_threshold_policy_not_forward_tuning",
        ],
    }


def _write_ablation_artifacts(summary: dict[str, Any], *, json_path: Path, csv_path: Path, report_path: Path) -> None:
    write_json(json_path, summary)
    rows = pd.DataFrame(summary["ablation_rows"])
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    rows.to_csv(csv_path, index=False, encoding="utf-8-sig")
    lines = [
        "# STAS5 V2 Ablation Baseline",
        "",
        f"Статус: `{summary['status']}`.",
        "",
        f"Train: `{TRAIN_START_DAY}..{TRAIN_END_DAY}`. Rows: `{summary['rows']}`. Feature columns: `{summary['feature_count']}`.",
        "",
        "Граница: forward `2026-05-15+` не использован для обучения или threshold tuning. TP/Stas3/API/Optuna не запускались.",
        "",
        "## Итог По Группам",
        "",
        "| Feature set | Features | AUC LOO | KEEP->ENTER | KEEP->ENTER/UNSURE | Yellow KEEP->ENTER/UNSURE | ENTER | UNSURE | SKIP |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary["ablation_rows"]:
        auc = "" if row["auc_leave_one_day_out"] is None else f"{float(row['auc_leave_one_day_out']):.6f}"
        lines.append(
            "| {feature_set} | {feature_count} | {auc} | {keep_enter:.3f} | {keep_unsure:.3f} | {yellow_unsure:.3f} | {enter} | {unsure} | {skip} |".format(
                feature_set=row["feature_set"],
                feature_count=row["feature_count"],
                auc=auc,
                keep_enter=float(row["keep_recall_enter"]),
                keep_unsure=float(row["keep_recall_unsure_plus"]),
                yellow_unsure=float(row["keep_with_yellow_x_recall_unsure_plus"]),
                enter=int(row["ENTER"]),
                unsure=int(row["UNSURE"]),
                skip=int(row["SKIP"]),
            )
        )
    lines.extend(
        [
            "",
            "## Что Это Значит",
            "",
            "Ablation показывает, какие группы признаков помогают отличать human `KEEP` от `CUT` внутри train-окна. Это еще не production permission.",
            "",
            "Финальный V2 controlled model в этом проходе обучается на `full_v2_all_274`, потому что цель этапа - проверить полный числовой контур на blind-forward графиках.",
            "",
        ]
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def train_v2_entry_ranker(
    *,
    snapshot_path: Path = DEFAULT_V2_FEATURE_SNAPSHOT_PATH,
    snapshot_manifest_path: Path = DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH,
    guard_report_path: Path = DEFAULT_V2_GUARD_REPORT_PATH,
    audit_json_path: Path = DEFAULT_V2_PRE_ML_AUDIT_JSON_PATH,
    model_path: Path = DEFAULT_V2_MODEL_PATH,
    manifest_path: Path = DEFAULT_V2_MODEL_MANIFEST_PATH,
    predictions_path: Path = DEFAULT_V2_TRAIN_PREDICTIONS_PATH,
    ablation_json_path: Path = DEFAULT_V2_ABLATION_JSON_PATH,
    ablation_csv_path: Path = DEFAULT_V2_ABLATION_CSV_PATH,
    ablation_report_path: Path = DEFAULT_V2_ABLATION_REPORT_PATH,
    model_feature_set: str = "full_v2_all_274",
    enter_threshold: float = 0.65,
    unsure_threshold: float = 0.45,
    strict: bool = True,
) -> tuple[dict[str, Any], pd.DataFrame]:
    feature_manifest = _load_json(snapshot_manifest_path)
    feature_columns = [str(column) for column in feature_manifest["feature_columns"]]
    numeric_columns = [str(column) for column in feature_manifest.get("numeric_columns", []) if str(column) in feature_columns]
    categorical_columns = [str(column) for column in feature_manifest.get("categorical_columns", []) if str(column) in feature_columns]
    v1_feature_columns = [str(column) for column in feature_manifest.get("v1_feature_columns", []) if str(column) in feature_columns]
    forbidden = forbidden_feature_matches(feature_columns)
    if forbidden:
        raise ValueError(f"forbidden feature columns: {forbidden}")

    guard_status = None
    if guard_report_path.exists():
        guard_status = _load_json(guard_report_path).get("status")
        if strict and guard_status != "PASS":
            raise ValueError(f"V2 leakage guard status is not PASS: {guard_status}")

    audit_status = None
    if audit_json_path.exists():
        audit_status = _load_json(audit_json_path).get("status")
        if strict and audit_status != "READY_FOR_V2_ABLATION_BASELINE":
            raise ValueError(f"V2 pre-ML audit status is not READY_FOR_V2_ABLATION_BASELINE: {audit_status}")
    elif strict:
        raise FileNotFoundError(f"V2 pre-ML audit json not found: {audit_json_path}")

    snapshot = read_csv(snapshot_path)
    ablation = run_v2_ablation_from_frames(
        snapshot=snapshot,
        feature_columns=feature_columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        v1_feature_columns=v1_feature_columns,
        enter_threshold=enter_threshold,
        unsure_threshold=unsure_threshold,
    )
    _write_ablation_artifacts(ablation, json_path=ablation_json_path, csv_path=ablation_csv_path, report_path=ablation_report_path)

    feature_sets = _select_feature_sets(feature_columns=feature_columns, v1_feature_columns=v1_feature_columns)
    if model_feature_set not in feature_sets:
        raise ValueError(f"unknown model feature set: {model_feature_set}")
    selected_features = feature_sets[model_feature_set]
    selected_numeric = [column for column in numeric_columns if column in selected_features]
    selected_categorical = [column for column in categorical_columns if column in selected_features]

    df = snapshot.copy()
    df["target_keep"] = df["human_label"].map(label_target)
    train = df.dropna(subset=["target_keep"]).copy()
    train["target_keep"] = train["target_keep"].astype(int)
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
        "yellow_x",
        "yellow_x_conflict",
    ]
    predictions = train[[column for column in prediction_columns if column in train.columns]].copy()
    predictions["oof_ml_keep_score_v2"] = oof
    predictions["train_fit_ml_keep_score_v2"] = train_scores
    predictions["ml_decision_v2"] = [
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
        "model_id": "STAS5_V2_ENTRY_RANKER_FULL_V2_CONTROLLED",
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
        "snapshot_path": rel(snapshot_path),
        "snapshot_manifest_path": rel(snapshot_manifest_path),
        "guard_status": guard_status,
        "audit_status": audit_status,
        "train_window": {"start_day": TRAIN_START_DAY, "end_day": TRAIN_END_DAY},
        "forward_window_policy": "2026-05-15..2026-05-20 is blind review only and never threshold tuning",
        "label_status_warning": "DRAFT_REVIEW_ONLY: labels are KEEP_DRAFT/CUT_DRAFT, not approved production labels",
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
        "ablation_report_path": rel(ablation_report_path),
        "ablation_top_rows": ablation["ablation_rows"][:5],
        "guardrails": [
            "no_yellow_x_in_feature_columns",
            "no_strategy_vote_or_x_up_in_feature_columns",
            "no_future_outcome_in_feature_columns",
            "no_stas3_tp_exit_in_feature_columns",
            "leave_one_day_out_only_inside_train_window",
            "forward_days_not_used_for_threshold",
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
        "ablation_json_path": run_dir / "stas5_v2_ablation_baseline_20260501_20260514_v0.json",
        "ablation_csv_path": run_dir / "stas5_v2_ablation_baseline_20260501_20260514_v0.csv",
        "ablation_report_path": run_dir / "STAS5_V2_ABLATION_BASELINE_20260501_20260514_RU.md",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Train STAS5 V2 controlled entry ranker with ablation baseline.")
    parser.add_argument("--snapshot-path", default=str(DEFAULT_V2_FEATURE_SNAPSHOT_PATH))
    parser.add_argument("--snapshot-manifest-path", default=str(DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH))
    parser.add_argument("--guard-report-path", default=str(DEFAULT_V2_GUARD_REPORT_PATH))
    parser.add_argument("--audit-json-path", default=str(DEFAULT_V2_PRE_ML_AUDIT_JSON_PATH))
    parser.add_argument("--run-id", default="")
    parser.add_argument("--run-root", default=str(DEFAULT_V2_MODEL_RUNS_DIR))
    parser.add_argument("--model-path", default="")
    parser.add_argument("--manifest-path", default="")
    parser.add_argument("--predictions-path", default="")
    parser.add_argument("--ablation-json-path", default="")
    parser.add_argument("--ablation-csv-path", default="")
    parser.add_argument("--ablation-report-path", default="")
    parser.add_argument("--model-feature-set", default="full_v2_all_274")
    parser.add_argument("--enter-threshold", type=float, default=0.65)
    parser.add_argument("--unsure-threshold", type=float, default=0.45)
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()

    run_id = args.run_id or f"stas5_v2_train_{run_stamp()}"
    paths = _run_paths(run_id, Path(args.run_root))
    model_path = Path(args.model_path) if args.model_path else paths["model_path"]
    manifest_path = Path(args.manifest_path) if args.manifest_path else paths["manifest_path"]
    predictions_path = Path(args.predictions_path) if args.predictions_path else paths["predictions_path"]
    ablation_json_path = Path(args.ablation_json_path) if args.ablation_json_path else paths["ablation_json_path"]
    ablation_csv_path = Path(args.ablation_csv_path) if args.ablation_csv_path else paths["ablation_csv_path"]
    ablation_report_path = Path(args.ablation_report_path) if args.ablation_report_path else paths["ablation_report_path"]
    manifest, _predictions = train_v2_entry_ranker(
        snapshot_path=Path(args.snapshot_path),
        snapshot_manifest_path=Path(args.snapshot_manifest_path),
        guard_report_path=Path(args.guard_report_path),
        audit_json_path=Path(args.audit_json_path),
        model_path=model_path,
        manifest_path=manifest_path,
        predictions_path=predictions_path,
        ablation_json_path=ablation_json_path,
        ablation_csv_path=ablation_csv_path,
        ablation_report_path=ablation_report_path,
        model_feature_set=args.model_feature_set,
        enter_threshold=args.enter_threshold,
        unsure_threshold=args.unsure_threshold,
        strict=not args.no_strict,
    )
    write_json(
        DEFAULT_V2_MODEL_DIR / "STAS5_V2_LATEST_MODEL_RUN.json",
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
