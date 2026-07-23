from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import (
    JOIN_KEYS,
    PROJECT_ROOT,
    STAS5_ARTIFACTS_DIR,
    compact_day,
    forbidden_feature_matches,
    normalize_day,
    normalize_ts,
    read_csv,
    rel,
    utc_now,
    write_json,
)
from mlbotnav.stas5_feature_snapshot_builder import classify_feature_columns
from mlbotnav.stas5_v2_feature_snapshot_builder import (
    DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH,
    DEFAULT_V2_FEATURE_SNAPSHOT_PATH,
)
from mlbotnav.stas5_v3_user_review_ledger import (
    DEFAULT_V3_USER_REVIEW_LEDGER_MANIFEST_PATH,
    DEFAULT_V3_USER_REVIEW_LEDGER_PATH,
)


STATUS = "STAS5_V3_TRAIN_DATASET_READY_1_14_PLUS_REVIEW_16_20_NO_TP_NO_API_NO_STAS3"
DEFAULT_V2_FORWARD_ALL_PREDICTIONS_PATH = (
    STAS5_ARTIFACTS_DIR / "v2" / "forward" / "STAS5_V2_FORWARD_ALL_PREDICTIONS_20260515_20260520.csv"
)
DEFAULT_V3_FEATURE_DIR = STAS5_ARTIFACTS_DIR / "v3" / "features"
DEFAULT_V3_TRAIN_DATASET_PATH = DEFAULT_V3_FEATURE_DIR / "STAS5_V3_TRAIN_DATASET_20260501_20260520.csv"
DEFAULT_V3_TRAIN_DATASET_MANIFEST_PATH = DEFAULT_V3_TRAIN_DATASET_PATH.with_suffix(".manifest.json")

V3_METADATA_COLUMNS = [
    "v3_train_source",
    "v3_user_review_label",
    "v3_user_review_reason",
    "v3_user_note",
    "v3_train_usage",
    "v3_source_review_file",
    "v3_current_ml_decision_before_review",
    "v3_current_ml_score_before_review",
    "v3_is_auto_bad_unmarked",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["day"] = out["day"].map(normalize_day)
    out["candidate_id"] = out["candidate_id"].astype(str)
    out["record_id"] = out["record_id"].astype(str)
    if "entry_time_utc" in out:
        out["entry_time_utc"] = out["entry_time_utc"].map(normalize_ts)
    if "anchor_time_utc" in out:
        out["anchor_time_utc"] = out["anchor_time_utc"].map(normalize_ts)
    return out


def _metadata_columns_from_manifest(manifest: dict[str, Any], old_snapshot: pd.DataFrame) -> list[str]:
    metadata = [str(column) for column in manifest.get("metadata_columns", []) if str(column) in old_snapshot.columns]
    for column in V3_METADATA_COLUMNS:
        if column not in metadata:
            metadata.append(column)
    return metadata


def _prepare_old_rows(old_snapshot: pd.DataFrame, metadata_columns: list[str], feature_columns: list[str]) -> pd.DataFrame:
    old = _normalize_keys(old_snapshot)
    for column in metadata_columns + feature_columns:
        if column not in old.columns:
            old[column] = pd.NA
    old["v3_train_source"] = "ORIGINAL_20260501_20260514_HUMAN_LABELS"
    old["v3_user_review_label"] = ""
    old["v3_user_review_reason"] = ""
    old["v3_user_note"] = ""
    old["v3_train_usage"] = "ORIGINAL_TRAIN_LABEL"
    old["v3_source_review_file"] = old.get("source_manual_label_file", "")
    old["v3_current_ml_decision_before_review"] = ""
    old["v3_current_ml_score_before_review"] = ""
    old["v3_is_auto_bad_unmarked"] = 0
    return old[metadata_columns + feature_columns].copy()


def _prepare_review_rows(
    *,
    user_review_ledger: pd.DataFrame,
    forward_predictions: pd.DataFrame,
    metadata_columns: list[str],
    feature_columns: list[str],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    ledger = _normalize_keys(user_review_ledger)
    forward = _normalize_keys(forward_predictions)
    train_ledger = ledger[ledger["train_usage"].astype(str).str.startswith("TRAIN_LABEL")].copy()

    duplicate_ledger = int(train_ledger.duplicated(JOIN_KEYS).sum()) if len(train_ledger) else 0
    duplicate_forward = int(forward.duplicated(JOIN_KEYS).sum()) if len(forward) else 0
    merged = train_ledger.merge(
        forward,
        on=JOIN_KEYS,
        how="left",
        suffixes=("_review", ""),
        indicator=True,
    )
    lost_after_forward_join = int((merged["_merge"] != "both").sum())
    merged = merged.drop(columns=["_merge"])

    for column in metadata_columns + feature_columns:
        if column not in merged.columns:
            merged[column] = pd.NA
    merged["human_label"] = merged["training_label"]
    merged["label_status"] = "APPROVED"
    source_label_column = "label_source_review" if "label_source_review" in merged.columns else "label_source"
    merged["label_source"] = merged[source_label_column]
    merged["yellow_x"] = 0
    merged["yellow_x_role"] = "NOT_AVAILABLE_FORWARD_REVIEW"
    merged["yellow_x_conflict"] = 0
    merged["source_manual_label_file"] = merged["source_review_file"]
    if "entry_time_utc_review" in merged.columns:
        merged["entry_time_utc"] = merged["entry_time_utc_review"].map(normalize_ts)
    merged["v3_train_source"] = "USER_REVIEW_20260516_20260520"
    merged["v3_user_review_label"] = merged["user_review_label"]
    merged["v3_user_review_reason"] = merged["user_review_reason"]
    merged["v3_user_note"] = merged["user_note"]
    merged["v3_train_usage"] = merged["train_usage"]
    merged["v3_source_review_file"] = merged["source_review_file"]
    merged["v3_current_ml_decision_before_review"] = merged["current_ml_decision"]
    merged["v3_current_ml_score_before_review"] = merged["current_ml_score"]
    merged["v3_is_auto_bad_unmarked"] = pd.to_numeric(merged["is_auto_bad_unmarked"], errors="coerce").fillna(0).astype(int)

    checks = {
        "train_ledger_rows": int(len(train_ledger)),
        "duplicate_ledger_keys": duplicate_ledger,
        "duplicate_forward_keys": duplicate_forward,
        "lost_after_forward_join": lost_after_forward_join,
    }
    return merged[metadata_columns + feature_columns].copy(), checks


def build_v3_training_dataset(
    *,
    old_snapshot_path: Path = DEFAULT_V2_FEATURE_SNAPSHOT_PATH,
    old_snapshot_manifest_path: Path = DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH,
    user_review_ledger_path: Path = DEFAULT_V3_USER_REVIEW_LEDGER_PATH,
    user_review_ledger_manifest_path: Path = DEFAULT_V3_USER_REVIEW_LEDGER_MANIFEST_PATH,
    forward_predictions_path: Path = DEFAULT_V2_FORWARD_ALL_PREDICTIONS_PATH,
    output_csv: Path = DEFAULT_V3_TRAIN_DATASET_PATH,
    manifest_path: Path = DEFAULT_V3_TRAIN_DATASET_MANIFEST_PATH,
    strict: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    for path in [old_snapshot_path, old_snapshot_manifest_path, user_review_ledger_path, forward_predictions_path]:
        if not path.exists():
            raise FileNotFoundError(f"required STAS5 V3 dataset input not found: {path}")

    old_manifest = _load_json(old_snapshot_manifest_path)
    ledger_manifest = _load_json(user_review_ledger_manifest_path) if user_review_ledger_manifest_path.exists() else {}
    if strict and ledger_manifest and ledger_manifest.get("status") != "PASS":
        raise ValueError(f"user-review ledger status is not PASS: {ledger_manifest.get('status')}")

    old_snapshot = read_csv(old_snapshot_path)
    ledger = read_csv(user_review_ledger_path)
    forward = read_csv(forward_predictions_path)

    feature_columns = [str(column) for column in old_manifest["feature_columns"]]
    v1_feature_columns = [str(column) for column in old_manifest.get("v1_feature_columns", []) if str(column) in feature_columns]
    v2_feature_columns = [str(column) for column in old_manifest.get("v2_feature_columns", []) if str(column) in feature_columns]
    metadata_columns = _metadata_columns_from_manifest(old_manifest, old_snapshot)

    old_rows = _prepare_old_rows(old_snapshot, metadata_columns, feature_columns)
    review_rows, review_checks = _prepare_review_rows(
        user_review_ledger=ledger,
        forward_predictions=forward,
        metadata_columns=metadata_columns,
        feature_columns=feature_columns,
    )
    dataset = pd.concat([old_rows, review_rows], ignore_index=True, sort=False)
    dataset = dataset.sort_values([column for column in ["day", "entry_time_utc", "record_id"] if column in dataset.columns]).reset_index(drop=True)

    forbidden = forbidden_feature_matches(feature_columns)
    numeric, categorical, boolean = classify_feature_columns(dataset, feature_columns)
    duplicate_keys = int(dataset.duplicated(JOIN_KEYS).sum())
    label_counts = Counter(dataset["human_label"].astype(str))
    source_counts = Counter(dataset["v3_train_source"].astype(str))
    day_counts = {
        day: {
            "rows": int(len(group)),
            "labels": dict(Counter(group["human_label"].astype(str))),
            "source": dict(Counter(group["v3_train_source"].astype(str))),
        }
        for day, group in dataset.groupby("day", sort=True)
    }
    days = sorted(dataset["day"].astype(str).unique().tolist())
    forbidden_days = [day for day in days if day in {"2026-05-15", "2026-05-21", "2026-05-22", "2026-05-23", "2026-05-24", "2026-05-25"}]
    status_pass = (
        len(feature_columns) == int(old_manifest.get("feature_count", len(feature_columns)))
        and not forbidden
        and duplicate_keys == 0
        and review_checks["lost_after_forward_join"] == 0
        and review_checks["duplicate_ledger_keys"] == 0
        and review_checks["duplicate_forward_keys"] == 0
        and int(label_counts.get("KEEP_APPROVED", 0)) > 0
        and int(label_counts.get("CUT_APPROVED", 0)) > 0
        and not forbidden_days
    )
    manifest = {
        "status": "PASS" if status_pass else "FAIL",
        "pipeline_status": STATUS,
        "created_utc": utc_now(),
        "schema_version": 0,
        "train_policy": "V3 trains on original 2026-05-01..2026-05-14 plus user-reviewed 2026-05-16..2026-05-20; 2026-05-15 excluded; 2026-05-21..2026-05-25 holdout.",
        "train_days": days,
        "excluded_days": ["2026-05-15"],
        "holdout_days": ["2026-05-21", "2026-05-22", "2026-05-23", "2026-05-24", "2026-05-25"],
        "rows": int(len(dataset)),
        "old_train_rows": int(len(old_rows)),
        "review_train_rows": int(len(review_rows)),
        "label_counts": dict(label_counts),
        "source_counts": dict(source_counts),
        "day_counts": day_counts,
        "feature_columns": feature_columns,
        "feature_count": len(feature_columns),
        "v1_feature_columns": v1_feature_columns,
        "v1_feature_count": len(v1_feature_columns),
        "v2_feature_columns": v2_feature_columns,
        "v2_feature_count": len(v2_feature_columns),
        "numeric_columns": numeric,
        "categorical_columns": categorical,
        "boolean_columns": boolean,
        "metadata_columns": metadata_columns,
        "checks": {
            "old_snapshot_status": old_manifest.get("status"),
            "user_review_ledger_status": ledger_manifest.get("status"),
            "duplicate_output_keys": duplicate_keys,
            "forbidden_feature_columns": forbidden,
            "forbidden_days_present": forbidden_days,
            **review_checks,
        },
        "inputs": {
            "old_snapshot_path": rel(old_snapshot_path),
            "old_snapshot_manifest_path": rel(old_snapshot_manifest_path),
            "user_review_ledger_path": rel(user_review_ledger_path),
            "user_review_ledger_manifest_path": rel(user_review_ledger_manifest_path),
            "forward_predictions_path": rel(forward_predictions_path),
        },
        "output_csv": rel(output_csv),
        "manifest_path": rel(manifest_path),
        "guardrails": [
            "feature_columns_are_inherited_from_v2_full274_manifest",
            "v3_user_review_fields_are_metadata_not_features",
            "current_ml_scores_are_metadata_not_features",
            "postfact_fields_are_not_features",
            "2026_05_15_excluded_until_review_is_final",
            "2026_05_21_2026_05_25_holdout_not_in_training",
            "no_tp_stas3_exit_api_fields",
        ],
    }
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(output_csv, index=False, encoding="utf-8-sig")
    write_json(manifest_path, manifest)
    if strict and manifest["status"] != "PASS":
        raise ValueError(f"STAS5 V3 train dataset failed checks: {manifest['checks']}")
    return dataset, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build STAS5 V3 train dataset from V2 full274 snapshot plus user-reviewed forward days.")
    parser.add_argument("--old-snapshot-path", default=str(DEFAULT_V2_FEATURE_SNAPSHOT_PATH))
    parser.add_argument("--old-snapshot-manifest-path", default=str(DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH))
    parser.add_argument("--user-review-ledger-path", default=str(DEFAULT_V3_USER_REVIEW_LEDGER_PATH))
    parser.add_argument("--user-review-ledger-manifest-path", default=str(DEFAULT_V3_USER_REVIEW_LEDGER_MANIFEST_PATH))
    parser.add_argument("--forward-predictions-path", default=str(DEFAULT_V2_FORWARD_ALL_PREDICTIONS_PATH))
    parser.add_argument("--output-csv", default=str(DEFAULT_V3_TRAIN_DATASET_PATH))
    parser.add_argument("--manifest-path", default=str(DEFAULT_V3_TRAIN_DATASET_MANIFEST_PATH))
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()
    _dataset, manifest = build_v3_training_dataset(
        old_snapshot_path=Path(args.old_snapshot_path),
        old_snapshot_manifest_path=Path(args.old_snapshot_manifest_path),
        user_review_ledger_path=Path(args.user_review_ledger_path),
        user_review_ledger_manifest_path=Path(args.user_review_ledger_manifest_path),
        forward_predictions_path=Path(args.forward_predictions_path),
        output_csv=Path(args.output_csv),
        manifest_path=Path(args.manifest_path),
        strict=not args.no_strict,
    )
    print(
        {
            "status": manifest["status"],
            "rows": manifest["rows"],
            "old_train_rows": manifest["old_train_rows"],
            "review_train_rows": manifest["review_train_rows"],
            "feature_count": manifest["feature_count"],
            "label_counts": manifest["label_counts"],
            "output_csv": manifest["output_csv"],
        }
    )
    return 0 if manifest["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
