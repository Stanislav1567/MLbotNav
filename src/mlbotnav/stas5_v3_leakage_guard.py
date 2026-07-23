from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import (
    JOIN_KEYS,
    STAS5_ARTIFACTS_DIR,
    forbidden_feature_matches,
    normalize_ts,
    read_csv,
    rel,
    utc_now,
    write_json,
)
from mlbotnav.stas5_v3_training_dataset_builder import (
    DEFAULT_V3_TRAIN_DATASET_MANIFEST_PATH,
    DEFAULT_V3_TRAIN_DATASET_PATH,
)


STATUS = "STAS5_V3_LEAKAGE_GUARD_READY_NO_TP_NO_API_NO_STAS3"
DEFAULT_V3_GUARD_DIR = STAS5_ARTIFACTS_DIR / "v3" / "guard"
DEFAULT_V3_GUARD_REPORT_PATH = DEFAULT_V3_GUARD_DIR / "STAS5_V3_LEAKAGE_GUARD_20260501_20260520.json"
ALLOWED_TRAIN_DAYS = {f"2026-05-{day:02d}" for day in range(1, 15)} | {f"2026-05-{day:02d}" for day in range(16, 21)}
EXCLUDED_DAYS = {"2026-05-15"}
HOLDOUT_DAYS = {f"2026-05-{day:02d}" for day in range(21, 26)}
METADATA_PREFIXES = ("v3_",)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _time_not_before_entry_count(dataset: pd.DataFrame) -> int:
    if "v2_combo_feature_time_utc" not in dataset.columns or "entry_time_utc" not in dataset.columns:
        return 0
    feature_ts = pd.to_datetime(dataset["v2_combo_feature_time_utc"].map(normalize_ts), utc=True, errors="coerce")
    entry_ts = pd.to_datetime(dataset["entry_time_utc"].map(normalize_ts), utc=True, errors="coerce")
    bad = feature_ts.notna() & entry_ts.notna() & (feature_ts >= entry_ts)
    return int(bad.sum())


def _available_before_entry_false_count(dataset: pd.DataFrame) -> int:
    if "v2_combo_feature_available_before_entry" not in dataset.columns:
        return 0
    return int((dataset["v2_combo_feature_available_before_entry"].astype(str).str.lower() != "true").sum())


def run_v3_leakage_guard(
    *,
    dataset_path: Path = DEFAULT_V3_TRAIN_DATASET_PATH,
    dataset_manifest_path: Path = DEFAULT_V3_TRAIN_DATASET_MANIFEST_PATH,
    output_path: Path = DEFAULT_V3_GUARD_REPORT_PATH,
    strict: bool = True,
) -> dict[str, Any]:
    if not dataset_path.exists():
        raise FileNotFoundError(f"V3 dataset not found: {dataset_path}")
    if not dataset_manifest_path.exists():
        raise FileNotFoundError(f"V3 dataset manifest not found: {dataset_manifest_path}")

    dataset = read_csv(dataset_path)
    manifest = _load_json(dataset_manifest_path)
    feature_columns = [str(column) for column in manifest.get("feature_columns", [])]
    metadata_columns = [str(column) for column in manifest.get("metadata_columns", [])]

    forbidden = forbidden_feature_matches(feature_columns)
    duplicate_keys = int(dataset.duplicated(JOIN_KEYS).sum())
    days = set(dataset["day"].astype(str))
    not_allowed_days = sorted(days - ALLOWED_TRAIN_DAYS)
    excluded_present = sorted(days & EXCLUDED_DAYS)
    holdout_present = sorted(days & HOLDOUT_DAYS)
    missing_features = [column for column in feature_columns if column not in dataset.columns]
    feature_columns_that_look_like_metadata = [
        column for column in feature_columns if column in metadata_columns or column.startswith(METADATA_PREFIXES)
    ]
    label_counts = Counter(dataset["human_label"].astype(str)) if "human_label" in dataset.columns else Counter()
    source_counts = Counter(dataset["v3_train_source"].astype(str)) if "v3_train_source" in dataset.columns else Counter()
    time_not_before = _time_not_before_entry_count(dataset)
    available_false = _available_before_entry_false_count(dataset)
    status_pass = (
        manifest.get("status") == "PASS"
        and int(manifest.get("feature_count", -1)) == len(feature_columns)
        and len(feature_columns) == 274
        and not forbidden
        and not missing_features
        and not feature_columns_that_look_like_metadata
        and duplicate_keys == 0
        and not not_allowed_days
        and not excluded_present
        and not holdout_present
        and time_not_before == 0
        and available_false == 0
        and int(label_counts.get("KEEP_APPROVED", 0)) > 0
        and int(label_counts.get("CUT_APPROVED", 0)) > 0
        and int(label_counts.get("KEEP_DRAFT", 0)) > 0
        and int(label_counts.get("CUT_DRAFT", 0)) > 0
    )
    report = {
        "status": "PASS" if status_pass else "FAIL",
        "pipeline_status": STATUS,
        "created_utc": utc_now(),
        "dataset_path": rel(dataset_path),
        "dataset_manifest_path": rel(dataset_manifest_path),
        "rows": int(len(dataset)),
        "feature_count": len(feature_columns),
        "label_counts": dict(label_counts),
        "source_counts": dict(source_counts),
        "checks": {
            "dataset_manifest_status": manifest.get("status"),
            "manifest_feature_count": manifest.get("feature_count"),
            "feature_count_is_274": len(feature_columns) == 274,
            "duplicate_keys": duplicate_keys,
            "forbidden_feature_columns": forbidden,
            "missing_features": missing_features,
            "feature_columns_that_look_like_metadata": feature_columns_that_look_like_metadata,
            "not_allowed_days": not_allowed_days,
            "excluded_days_present": excluded_present,
            "holdout_days_present": holdout_present,
            "v2_combo_feature_time_not_before_entry": time_not_before,
            "v2_combo_available_before_entry_false": available_false,
        },
        "guardrails": [
            "train_days_allowed_only_20260501_20260514_and_20260516_20260520",
            "20260515_excluded",
            "20260521_20260525_holdout_excluded",
            "feature_columns_only_no_v3_review_metadata",
            "no_future_postfact_tp_stas3_exit_features",
            "combo_feature_time_must_be_before_entry_time",
        ],
    }
    write_json(output_path, report)
    if strict and report["status"] != "PASS":
        raise ValueError(f"STAS5 V3 leakage guard failed checks: {report['checks']}")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run STAS5 V3 leakage guard before training.")
    parser.add_argument("--dataset-path", default=str(DEFAULT_V3_TRAIN_DATASET_PATH))
    parser.add_argument("--dataset-manifest-path", default=str(DEFAULT_V3_TRAIN_DATASET_MANIFEST_PATH))
    parser.add_argument("--output-path", default=str(DEFAULT_V3_GUARD_REPORT_PATH))
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()
    report = run_v3_leakage_guard(
        dataset_path=Path(args.dataset_path),
        dataset_manifest_path=Path(args.dataset_manifest_path),
        output_path=Path(args.output_path),
        strict=not args.no_strict,
    )
    print(
        {
            "status": report["status"],
            "rows": report["rows"],
            "feature_count": report["feature_count"],
            "label_counts": report["label_counts"],
            "checks": report["checks"],
        }
    )
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
