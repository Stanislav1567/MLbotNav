from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, precision_recall_fscore_support, roc_auc_score

from mlbotnav.stas5_common import PROJECT_ROOT, compact_day, ensure_parent, rel, utc_now, write_json
from mlbotnav.stas5_entry_ranker_train import _positive_proba, _prepare_feature_matrix
from mlbotnav.stas5_v5_batch_dataset_builder import TARGET_OR_MANUAL_COLUMNS, _forbidden_feature_matches, _source_time_check
from mlbotnav.stas5_v5_two_block_ml import (
    EXPECTED_FEATURES,
    KEY_COLUMNS,
    _build_model_pipeline,
    _check,
    _fill_feature_gaps,
    _fit_with_optional_weights,
    _infer_column_types,
    _run_binary_lodo_scores,
    _select_candidate,
)


RISKGATE_DATASET_GUARD_PASS = "PASS_V5C_RISKGATE_TRAIN_DATASET_GUARD_READY_NO_TRAINING"
RISKGATE_TRAINING_GUARD_PASS = "PASS_V5C_RISKGATE_ML_TRAINING_GUARD_READY_FOR_TRAINING"
RISKGATE_TRAINING_GUARD_FAIL = "FAIL_V5C_RISKGATE_ML_TRAINING_GUARD"
RISKGATE_TRAIN_STATUS = "PASS_V5C_RISKGATE_ML_TRAINED_POST_TRAIN_GUARD_READY_FOR_FORWARD"
RISKGATE_POST_TRAIN_GUARD_PASS = "PASS_V5C_RISKGATE_ML_POST_TRAIN_GUARD_READY_FOR_FORWARD"
RISKGATE_POST_TRAIN_GUARD_FAIL = "FAIL_V5C_RISKGATE_ML_POST_TRAIN_GUARD"
RISKGATE_MODEL_CANDIDATES = ["extra_trees_balanced", "logistic_balanced"]

V5C_ROOT = PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5c"

RISKGATE_TARGET_OR_MANUAL_COLUMNS = set(TARGET_OR_MANUAL_COLUMNS).union(
    {
        "risk_bad_y",
        "risk_sample_role",
        "entry_review_label",
        "risk_review_label",
        "risk_user_hint",
        "user_text_raw",
        "entry_from_risk_bad",
        "riskgate_raw_status_at_review",
        "riskgate_good_exception_candidate",
        "RISK_GATE_STATUS",
        "RISK_GATE_ACTION",
        "RISK_GATE_PRIMARY_REGIME",
        "RISK_GATE_TAGS",
        "RISK_NO_FUTURE_OK",
    }
)


def riskgate_dataset_paths(start_day: str, end_day: str, output_dir: Path = V5C_ROOT, expected_features: int = EXPECTED_FEATURES) -> dict[str, Path]:
    prefix = f"STAS5_V5C_RISKGATE_TRAIN_DATASET_{compact_day(start_day)}_{compact_day(end_day)}"
    return {
        "dataset": output_dir / f"{prefix}_X{expected_features}_RISK_BAD_Y_V1.csv",
        "allowlist": output_dir / f"{prefix}_FEATURE_ALLOWLIST_{expected_features}F_V1.json",
        "guard": output_dir / f"{prefix}_GUARD_V1.json",
        "manifest": output_dir / f"{prefix}_MANIFEST_V1.json",
    }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _read_allowlist(path: Path) -> list[str]:
    payload = _load_json(path)
    return [str(column) for column in payload.get("feature_columns", [])]


def _read_riskgate_dataset(dataset_path: Path, allowlist_path: Path) -> tuple[pd.DataFrame, list[str]]:
    feature_columns = _read_allowlist(allowlist_path)
    df = pd.read_csv(dataset_path, encoding="utf-8-sig", low_memory=False)
    df, _fill = _fill_feature_gaps(df, feature_columns)
    return df, feature_columns


def _riskgate_decision_threshold(scores: np.ndarray, y_true: np.ndarray, days: pd.Series) -> dict[str, Any]:
    clean_scores = np.asarray(scores, dtype=float)
    clean_y = np.asarray(y_true, dtype=int)
    total_positive = max(int(clean_y.sum()), 1)
    candidate_thresholds: list[dict[str, Any]] = []
    quantiles = [0.98, 0.96, 0.94, 0.92, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.50, 0.45, 0.40, 0.35, 0.30]
    for quantile in quantiles:
        threshold = float(np.nanquantile(clean_scores, quantile))
        pred = clean_scores >= threshold
        predicted_block = int(pred.sum())
        true_block = int(((clean_y == 1) & pred).sum())
        safe_blocked = int(((clean_y == 0) & pred).sum())
        precision = true_block / predicted_block if predicted_block else 0.0
        recall = true_block / total_positive
        f2 = (5.0 * precision * recall / ((4.0 * precision) + recall)) if (precision + recall) else 0.0
        candidate_thresholds.append(
            {
                "quantile": round(float(quantile), 6),
                "threshold": round(threshold, 10),
                "predicted_block": predicted_block,
                "risk_bad_blocked": true_block,
                "explicit_safe_blocked": safe_blocked,
                "precision": round(float(precision), 6),
                "recall": round(float(recall), 6),
                "f2": round(float(f2), 6),
                "day_coverage": int(days.astype(str)[pred].nunique()) if predicted_block else 0,
            }
        )
    eligible = [row for row in candidate_thresholds if row["predicted_block"] >= 5 and row["precision"] >= 0.65]
    if not eligible:
        eligible = [row for row in candidate_thresholds if row["predicted_block"] >= 5] or candidate_thresholds
    best = max(
        eligible,
        key=lambda row: (
            float(row["f2"]),
            float(row["recall"]),
            float(row["precision"]),
            -int(row["explicit_safe_blocked"]),
        ),
    )
    block = float(best["threshold"])
    warn_quantile = max(0.30, min(0.75, float(best["quantile"]) - 0.20))
    warn = float(np.nanquantile(clean_scores, warn_quantile))
    if warn > block:
        warn = block
    return {
        "risk_block_threshold": round(block, 10),
        "risk_warn_threshold": round(warn, 10),
        "policy": "train_oof_f2_safety_gate_no_forward_tuning",
        "block_quantile": best["quantile"],
        "warn_quantile": round(float(warn_quantile), 6),
        "selected_candidate": best,
        "candidate_thresholds": candidate_thresholds,
    }


def apply_riskgate_decision(scores: np.ndarray, thresholds: dict[str, Any]) -> np.ndarray:
    block = float(thresholds["risk_block_threshold"])
    warn = float(thresholds["risk_warn_threshold"])
    return np.where(scores >= block, "BLOCK_RISK", np.where(scores >= warn, "WARN_RISK", "PASS_RISK"))


def apply_riskgate_to_entry_decisions(entry_decisions: np.ndarray, risk_decisions: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    entry = np.asarray(entry_decisions, dtype=object)
    risk = np.asarray(risk_decisions, dtype=object)
    final = entry.copy()
    action = np.full(len(entry), "KEEP_ENTRY_DECISION", dtype=object)
    block = risk == "BLOCK_RISK"
    warn = risk == "WARN_RISK"
    final[np.isin(entry, ["ENTER", "WATCH"]) & block] = "SKIP"
    action[np.isin(entry, ["ENTER", "WATCH"]) & block] = "RISKGATE_BLOCK_TO_SKIP"
    final[(entry == "ENTER") & warn] = "WATCH"
    action[(entry == "ENTER") & warn] = "RISKGATE_WARN_DEMOTE_TO_WATCH"
    return final, action


def _riskgate_metrics(y_true: np.ndarray, scores: np.ndarray, days: pd.Series, thresholds: dict[str, Any]) -> dict[str, Any]:
    risk_decisions = apply_riskgate_decision(scores, thresholds)
    block_mask = risk_decisions == "BLOCK_RISK"
    warn_plus_mask = np.isin(risk_decisions, ["BLOCK_RISK", "WARN_RISK"])
    positive = y_true == 1
    negative = y_true == 0
    precision, recall, f1, _support = precision_recall_fscore_support(
        y_true,
        block_mask.astype(int),
        average="binary",
        zero_division=0,
    )
    try:
        auc = float(roc_auc_score(y_true, scores))
    except Exception:
        auc = None
    try:
        ap = float(average_precision_score(y_true, scores))
    except Exception:
        ap = None
    daily: list[dict[str, Any]] = []
    for day in sorted(days.astype(str).unique()):
        mask = days.astype(str).eq(day)
        day_y = y_true[mask.to_numpy()]
        day_decisions = risk_decisions[mask.to_numpy()]
        daily.append(
            {
                "day": day,
                "rows": int(mask.sum()),
                "risk_bad": int(day_y.sum()),
                "explicit_safe": int(len(day_y) - day_y.sum()),
                "BLOCK_RISK": int((day_decisions == "BLOCK_RISK").sum()),
                "WARN_RISK": int((day_decisions == "WARN_RISK").sum()),
                "PASS_RISK": int((day_decisions == "PASS_RISK").sum()),
            }
        )
    return {
        "rows": int(len(y_true)),
        "risk_bad_y_1": int(positive.sum()),
        "risk_bad_y_0": int(negative.sum()),
        "roc_auc": auc,
        "pr_auc": ap,
        "block_precision": round(float(precision), 6),
        "block_recall": round(float(recall), 6),
        "block_f1": round(float(f1), 6),
        "warn_plus_recall": round(float((positive & warn_plus_mask).sum()) / max(int(positive.sum()), 1), 6),
        "explicit_safe_blocked": int((negative & block_mask).sum()),
        "decision_counts": {str(k): int(v) for k, v in pd.Series(risk_decisions).value_counts().to_dict().items()},
        "thresholds": thresholds,
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


def _write_guard_md(path: Path, title: str, guard: dict[str, Any]) -> None:
    lines = [
        f"# {title}",
        "",
        f"Статус: `{guard['status']}`.",
        "",
        "## Checks",
        "",
    ]
    for item in guard.get("checks", []):
        lines.append(f"- `{item['check']}`: `{item['status']}`")
    ensure_parent(path)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_riskgate_training_guard(
    *,
    run_dir: Path,
    dataset_path: Path,
    allowlist_path: Path,
    dataset_guard_path: Path,
    expected_features: int = EXPECTED_FEATURES,
) -> dict[str, Any]:
    run_dir.mkdir(parents=True, exist_ok=True)
    df, feature_columns = _read_riskgate_dataset(dataset_path, allowlist_path)
    dataset_guard = _load_json(dataset_guard_path) if dataset_guard_path.exists() else {}
    y = pd.to_numeric(df.get("risk_bad_y", pd.Series(dtype=float)), errors="coerce").fillna(-1).astype(int)
    counts = {str(int(k)): int(v) for k, v in y.value_counts().sort_index().items() if int(k) in {0, 1}}
    missing_features = [column for column in feature_columns if column not in df.columns]
    target_in_features = sorted(set(feature_columns).intersection(RISKGATE_TARGET_OR_MANUAL_COLUMNS))
    forbidden = _forbidden_feature_matches(feature_columns)
    numeric_columns, _categorical = _infer_column_types(df, feature_columns)
    inf_count = 0
    for column in numeric_columns:
        if column in df.columns:
            values = pd.to_numeric(df[column], errors="coerce").to_numpy(dtype=float)
            inf_count += int(np.isinf(values).sum())
    feature_nulls = int(df[feature_columns].isna().sum().sum()) if feature_columns else -1
    duplicate_day_candidate = int(df.duplicated(["day", "candidate_id"]).sum()) if {"day", "candidate_id"}.issubset(df.columns) else -1
    duplicate_day_record = int(df.duplicated(["day", "record_id"]).sum()) if {"day", "record_id"}.issubset(df.columns) else -1
    cs_time = _source_time_check(df, "cs_max_source_time_utc") if not df.empty else {}
    fcs_time = _source_time_check(df, "fcs_max_source_time_utc") if not df.empty else {}
    risk_bad_entry_bad = True
    if {"risk_bad_y", "entry_y"}.issubset(df.columns):
        entry_y = pd.to_numeric(df["entry_y"], errors="coerce").fillna(-1).astype(int)
        risk_bad_entry_bad = bool(((y == 1) & (entry_y != 0)).sum() == 0)

    checks = [
        _check("riskgate_dataset_guard_pass", dataset_guard.get("status") == RISKGATE_DATASET_GUARD_PASS, {"status": dataset_guard.get("status", "")}),
        _check("rows_positive", len(df) > 0, {"rows": int(len(df))}),
        _check("risk_bad_y_has_both_classes", counts.get("1", 0) > 0 and counts.get("0", 0) > 0, {"risk_bad_y_counts": counts}),
        _check("feature_count_expected", len(feature_columns) == expected_features, {"actual": len(feature_columns), "expected": expected_features}),
        _check("feature_columns_present", not missing_features, {"missing": missing_features[:50], "missing_count": len(missing_features)}),
        _check("target_manual_columns_not_in_X", not target_in_features, {"columns": target_in_features}),
        _check("forbidden_columns_absent_from_X", not forbidden, forbidden),
        _check("feature_values_no_null", feature_nulls == 0, {"feature_nulls": feature_nulls}),
        _check("feature_values_no_inf", inf_count == 0, {"feature_inf_count": inf_count}),
        _check("no_duplicate_day_candidate", duplicate_day_candidate == 0, {"duplicates": duplicate_day_candidate}),
        _check("no_duplicate_day_record", duplicate_day_record == 0, {"duplicates": duplicate_day_record}),
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
        _check("risk_bad_y_1_is_entry_y_0", risk_bad_entry_bad, {}),
    ]
    guard = {
        "status": RISKGATE_TRAINING_GUARD_PASS if all(item["status"] == "PASS" for item in checks) else RISKGATE_TRAINING_GUARD_FAIL,
        "created_utc": utc_now(),
        "run_id": run_dir.name,
        "run_dir": rel(run_dir),
        "dataset_path": rel(dataset_path),
        "allowlist_path": rel(allowlist_path),
        "dataset_guard_path": rel(dataset_guard_path),
        "rows": int(len(df)),
        "risk_bad_y_counts": counts,
        "feature_count": len(feature_columns),
        "feature_columns": feature_columns,
        "checks": checks,
    }
    write_json(run_dir / "STAS5_V5C_RISKGATE_ML_TRAINING_GUARD_V1.json", guard)
    _write_guard_md(run_dir / "STAS5_V5C_RISKGATE_ML_TRAINING_GUARD_RU.md", "STAS5 V5C RiskGate ML Training Guard", guard)
    return guard


def _post_train_guard(run_dir: Path, manifest: dict[str, Any], *, expected_features: int) -> dict[str, Any]:
    artifacts = manifest.get("artifacts", {})
    checks = [
        _check("riskgate_training_guard_pass", manifest.get("training_guard_status") == RISKGATE_TRAINING_GUARD_PASS, {"status": manifest.get("training_guard_status")}),
        _check("riskgate_model_exists", (PROJECT_ROOT / artifacts.get("riskgate_ml_model", "")).exists(), {"path": artifacts.get("riskgate_ml_model", "")}),
        _check("riskgate_oof_predictions_exist", (PROJECT_ROOT / artifacts.get("riskgate_oof_predictions", "")).exists(), {"path": artifacts.get("riskgate_oof_predictions", "")}),
        _check("riskgate_features_match_expected_contract", manifest.get("feature_count") == expected_features, {"feature_count": manifest.get("feature_count"), "expected": expected_features}),
        _check("target_not_in_feature_columns", "risk_bad_y" not in set(manifest.get("feature_columns", [])), {}),
        _check("decision_thresholds_present", {"risk_block_threshold", "risk_warn_threshold"}.issubset(set(manifest.get("thresholds", {}).keys())), manifest.get("thresholds", {})),
    ]
    guard = {
        "status": RISKGATE_POST_TRAIN_GUARD_PASS if all(item["status"] == "PASS" for item in checks) else RISKGATE_POST_TRAIN_GUARD_FAIL,
        "created_utc": utc_now(),
        "run_id": run_dir.name,
        "run_dir": rel(run_dir),
        "checks": checks,
    }
    write_json(run_dir / "STAS5_V5C_RISKGATE_ML_POST_TRAIN_GUARD_V1.json", guard)
    _write_guard_md(run_dir / "STAS5_V5C_RISKGATE_ML_POST_TRAIN_GUARD_RU.md", "STAS5 V5C RiskGate ML Post-Train Guard", guard)
    return guard


def train_v5c_riskgate_ml(
    *,
    run_dir: Path,
    dataset_path: Path,
    allowlist_path: Path,
    dataset_guard_path: Path,
    strict: bool = True,
    model_candidates: list[str] | None = None,
    expected_features: int = EXPECTED_FEATURES,
) -> dict[str, Any]:
    guard = run_riskgate_training_guard(
        run_dir=run_dir,
        dataset_path=dataset_path,
        allowlist_path=allowlist_path,
        dataset_guard_path=dataset_guard_path,
        expected_features=expected_features,
    )
    if strict and guard["status"] != RISKGATE_TRAINING_GUARD_PASS:
        raise ValueError(f"RiskGate training guard is not PASS: {guard['status']}")

    train, feature_columns = _read_riskgate_dataset(dataset_path, allowlist_path)
    train = train.sort_values(["day", "entry_time_utc", "candidate_id", "record_id"]).reset_index(drop=True)
    train["risk_bad_y"] = pd.to_numeric(train["risk_bad_y"], errors="coerce").fillna(0).astype(int)
    y = train["risk_bad_y"].to_numpy(dtype=int)
    days = train["day"].astype(str)
    numeric_columns, categorical_columns = _infer_column_types(train, feature_columns)
    candidates = model_candidates or RISKGATE_MODEL_CANDIDATES

    candidate_payloads: dict[str, dict[str, Any]] = {}
    for model_kind in candidates:
        scores, folds = _run_binary_lodo_scores(
            train,
            target="risk_bad_y",
            feature_columns=feature_columns,
            numeric_columns=numeric_columns,
            categorical_columns=categorical_columns,
            model_kind=model_kind,
        )
        thresholds = _riskgate_decision_threshold(scores, y, days)
        metrics = _riskgate_metrics(y, scores, days, thresholds)
        metrics["model_kind"] = model_kind
        candidate_payloads[model_kind] = {
            "scores": scores,
            "folds": folds,
            "thresholds": thresholds,
            "metrics": metrics,
        }
    selected_model_kind = _select_candidate(candidate_payloads)
    selected = candidate_payloads[selected_model_kind]
    thresholds = selected["thresholds"]

    x = _prepare_feature_matrix(train, feature_columns=feature_columns, numeric_columns=numeric_columns, categorical_columns=categorical_columns)
    model = _build_model_pipeline(numeric_columns=numeric_columns, categorical_columns=categorical_columns, model_kind=selected_model_kind)
    _fit_with_optional_weights(model, x, y)

    model_path = run_dir / "STAS5_V5C_RISKGATE_ML_MODEL.joblib"
    package = {
        "model_id": "STAS5_V5C_RISKGATE_ML_V1",
        "pipeline": model,
        "model_kind": selected_model_kind,
        "feature_columns": feature_columns,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "thresholds": thresholds,
        "target": "risk_bad_y",
        "decision_policy": "BLOCK_RISK/WARN_RISK/PASS_RISK over X439 only",
    }
    joblib.dump(package, model_path)

    predictions = train[[column for column in KEY_COLUMNS if column in train.columns] + ["risk_bad_y"]].copy()
    if "entry_y" in train.columns:
        predictions["entry_y"] = pd.to_numeric(train["entry_y"], errors="coerce").fillna(-1).astype(int)
    for model_kind, payload in candidate_payloads.items():
        key = model_kind.upper()
        predictions[f"RISKGATE_{key}_OOF_SCORE"] = payload["scores"]
        predictions[f"RISKGATE_{key}_OOF_DECISION"] = apply_riskgate_decision(payload["scores"], payload["thresholds"])
    predictions["RISKGATE_ML_OOF_SCORE"] = selected["scores"]
    predictions["RISKGATE_ML_OOF_DECISION"] = apply_riskgate_decision(selected["scores"], thresholds)
    predictions_path = run_dir / "STAS5_V5C_RISKGATE_ML_OOF_PREDICTIONS_V1.csv"
    predictions.to_csv(predictions_path, index=False, encoding="utf-8-sig")

    metrics = {
        "status": "PASS_V5C_RISKGATE_ML_METRICS_READY",
        "created_utc": utc_now(),
        "rows": int(len(train)),
        "riskgate_model_candidates": candidates,
        "riskgate_selected_model_kind": selected_model_kind,
        "riskgate_candidates_oof": {kind: payload["metrics"] for kind, payload in candidate_payloads.items()},
        "riskgate_oof": selected["metrics"],
        "thresholds": thresholds,
    }
    metrics_path = run_dir / "STAS5_V5C_RISKGATE_ML_METRICS_V1.json"
    write_json(metrics_path, metrics)

    manifest = {
        "status": RISKGATE_TRAIN_STATUS,
        "created_utc": utc_now(),
        "run_id": run_dir.name,
        "run_dir": rel(run_dir),
        "dataset_path": rel(dataset_path),
        "allowlist_path": rel(allowlist_path),
        "dataset_guard_path": rel(dataset_guard_path),
        "rows": int(len(train)),
        "risk_bad_y_counts": {str(k): int(v) for k, v in train["risk_bad_y"].value_counts().sort_index().items()},
        "feature_columns": feature_columns,
        "feature_count": len(feature_columns),
        "expected_feature_count": expected_features,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "training_guard_status": guard["status"],
        "riskgate_selected_model_kind": selected_model_kind,
        "riskgate_model_candidates": candidates,
        "thresholds": thresholds,
        "artifacts": {
            "riskgate_ml_model": rel(model_path),
            "riskgate_oof_predictions": rel(predictions_path),
            "riskgate_metrics_json": rel(metrics_path),
            "riskgate_training_guard_json": rel(run_dir / "STAS5_V5C_RISKGATE_ML_TRAINING_GUARD_V1.json"),
        },
        "guardrails": [
            "risk_bad_y_is_target_not_feature",
            "riskgate_ml_uses_only_causal_feature_allowlist",
            "riskgate_blocks_after_entry_opportunity_not_before_feature_build",
            "forward_must_keep_entry_decision_before_riskgate_for_audit",
        ],
    }
    manifest_path = run_dir / "STAS5_V5C_RISKGATE_ML_TRAIN_MANIFEST_V1.json"
    write_json(manifest_path, manifest)
    post_guard = _post_train_guard(run_dir, manifest, expected_features=expected_features)
    manifest["post_train_guard_status"] = post_guard["status"]
    manifest["artifacts"]["riskgate_post_train_guard_json"] = rel(run_dir / "STAS5_V5C_RISKGATE_ML_POST_TRAIN_GUARD_V1.json")
    manifest["artifacts"]["riskgate_train_manifest"] = rel(manifest_path)
    write_json(manifest_path, manifest)
    if strict and post_guard["status"] != RISKGATE_POST_TRAIN_GUARD_PASS:
        raise ValueError(f"RiskGate post-train guard is not PASS: {post_guard['status']}")
    return manifest


def apply_v5c_riskgate_forward(dataset: pd.DataFrame, riskgate_manifest: dict[str, Any], *, project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    model_path = project_root / riskgate_manifest["artifacts"]["riskgate_ml_model"]
    package = joblib.load(model_path)
    feature_columns = [str(column) for column in package["feature_columns"]]
    numeric_columns = [str(column) for column in package["numeric_columns"]]
    categorical_columns = [str(column) for column in package["categorical_columns"]]
    x = _prepare_feature_matrix(dataset, feature_columns=feature_columns, numeric_columns=numeric_columns, categorical_columns=categorical_columns)
    scores = _positive_proba(package["pipeline"], x)
    decisions = apply_riskgate_decision(scores, package["thresholds"])
    return {
        "scores": scores,
        "decisions": decisions,
        "package": package,
        "checks": [
            _check("riskgate_post_train_guard_pass", riskgate_manifest.get("post_train_guard_status") == RISKGATE_POST_TRAIN_GUARD_PASS, {"status": riskgate_manifest.get("post_train_guard_status", "")}),
            _check("riskgate_model_exists", model_path.exists(), {"path": rel(model_path)}),
            _check("riskgate_forward_features_match_manifest", feature_columns == [str(c) for c in riskgate_manifest.get("feature_columns", [])], {"feature_count": len(feature_columns)}),
        ],
    }
