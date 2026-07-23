from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import (
    DEFAULT_LEDGER_PATH,
    FORWARD_END_DAY,
    FORWARD_START_DAY,
    JOIN_KEYS,
    LABEL_COLUMNS,
    METADATA_COLUMNS,
    STAS5_ARTIFACTS_DIR,
    TRAIN_END_DAY,
    TRAIN_START_DAY,
    default_expected_train_counts,
    forbidden_feature_matches,
    is_keep_label,
    load_manifest_feature_columns,
    normalize_day,
    read_csv,
    rel,
    utc_now,
    write_json,
)
from mlbotnav.stas5_v2_feature_snapshot_builder import (
    DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH,
    DEFAULT_V2_FEATURE_SNAPSHOT_PATH,
    STATUS as V2_SNAPSHOT_STATUS,
    V2_COMBO_METADATA_RENAME,
)


STATUS = "STAS5_V2_LEAKAGE_GUARD_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3"
DEFAULT_V2_GUARD_REPORT_PATH = (
    STAS5_ARTIFACTS_DIR / "v2" / "guard" / "stas5_v2_leakage_guard_20260501_20260514_v0.json"
)

REQUIRED_METADATA_COLUMNS = [
    "day",
    "candidate_id",
    "record_id",
    "anchor_time_utc",
    "entry_time_utc",
    "human_label",
    "yellow_x",
    "yellow_x_role",
    "yellow_x_conflict",
    "v2_combo_anchor_time_utc",
    "v2_combo_entry_time_utc",
    "v2_combo_feature_time_utc",
    "v2_combo_feature_available_before_entry",
]


def _load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _duplicate_count(df: pd.DataFrame, columns: list[str]) -> int:
    if any(column not in df.columns for column in columns):
        return 0
    return int(df.duplicated(columns).sum())


def _parse_utc(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True, errors="coerce")


def _truthy_series(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin({"1", "true", "yes", "y"})


def _keep_yellow_count(df: pd.DataFrame) -> int:
    if "human_label" not in df.columns or "yellow_x" not in df.columns:
        return 0
    yellow = pd.to_numeric(df["yellow_x"], errors="coerce").fillna(0).astype(int)
    return int(sum(bool(is_keep_label(label)) and int(flag) == 1 for label, flag in zip(df["human_label"], yellow)))


def _label_counts(df: pd.DataFrame) -> dict[str, int]:
    if "human_label" not in df.columns:
        return {}
    return {str(key): int(value) for key, value in df["human_label"].value_counts(dropna=False).sort_index().items()}


def _train_day_checks(df: pd.DataFrame) -> dict[str, Any]:
    if "day" not in df.columns:
        return {
            "day_min": None,
            "day_max": None,
            "days_outside_train_range": None,
            "forward_days_present": None,
        }
    days = df["day"].map(normalize_day)
    outside = days[(days < TRAIN_START_DAY) | (days > TRAIN_END_DAY)]
    forward = days[(days >= FORWARD_START_DAY) & (days <= FORWARD_END_DAY)]
    return {
        "day_min": str(days.min()) if len(days) else None,
        "day_max": str(days.max()) if len(days) else None,
        "days_outside_train_range": int(outside.nunique()),
        "forward_days_present": int(forward.nunique()),
    }


def _time_checks(df: pd.DataFrame, *, strict_before_entry: bool) -> dict[str, int | None]:
    checks: dict[str, int | None] = {
        "entry_time_parse_fail": None,
        "v2_combo_feature_time_parse_fail": None,
        "v2_combo_feature_time_not_before_entry": None,
        "v2_combo_available_before_entry_false": None,
        "v2_combo_entry_time_mismatch": None,
        "v2_combo_anchor_time_mismatch": None,
        "context_max_open_time_after_entry": None,
    }
    if "entry_time_utc" not in df.columns:
        return checks

    entry = _parse_utc(df["entry_time_utc"])
    checks["entry_time_parse_fail"] = int(entry.isna().sum())

    if "v2_combo_feature_time_utc" in df.columns:
        feature_time = _parse_utc(df["v2_combo_feature_time_utc"])
        checks["v2_combo_feature_time_parse_fail"] = int(feature_time.isna().sum())
        if strict_before_entry:
            bad = feature_time.isna() | entry.isna() | (feature_time >= entry)
        else:
            bad = feature_time.isna() | entry.isna() | (feature_time > entry)
        checks["v2_combo_feature_time_not_before_entry"] = int(bad.sum())

    if "v2_combo_feature_available_before_entry" in df.columns:
        checks["v2_combo_available_before_entry_false"] = int((~_truthy_series(df["v2_combo_feature_available_before_entry"])).sum())

    if "v2_combo_entry_time_utc" in df.columns:
        combo_entry = _parse_utc(df["v2_combo_entry_time_utc"])
        checks["v2_combo_entry_time_mismatch"] = int((combo_entry != entry).sum())

    if "anchor_time_utc" in df.columns and "v2_combo_anchor_time_utc" in df.columns:
        anchor = _parse_utc(df["anchor_time_utc"])
        combo_anchor = _parse_utc(df["v2_combo_anchor_time_utc"])
        checks["v2_combo_anchor_time_mismatch"] = int((combo_anchor != anchor).sum())

    if "context_max_open_time_utc" in df.columns:
        context_time = _parse_utc(df["context_max_open_time_utc"])
        checks["context_max_open_time_after_entry"] = int((context_time > entry).sum())

    return checks


def run_v2_leakage_guard_from_frames(
    *,
    snapshot: pd.DataFrame,
    manifest: dict[str, Any],
    expected_rows: int | None = None,
    expected_keep_yellow_rows: int | None = None,
    strict_before_entry: bool = True,
) -> dict[str, Any]:
    feature_columns = [str(column) for column in (manifest.get("feature_columns") or [])]
    manifest_rows = manifest.get("rows")
    expected = default_expected_train_counts()
    if expected_rows is None:
        expected_rows = int(expected["rows"])
    if expected_keep_yellow_rows is None:
        expected_keep_yellow_rows = int(expected["KEEP_DRAFT_yellow_x"])

    all_columns = [str(column) for column in snapshot.columns]
    feature_set = set(feature_columns)
    metadata_allowed = set(METADATA_COLUMNS + LABEL_COLUMNS + list(V2_COMBO_METADATA_RENAME.values()))
    feature_columns_missing_in_csv = [column for column in feature_columns if column not in snapshot.columns]
    duplicate_feature_columns = sorted([column for column in set(feature_columns) if feature_columns.count(column) > 1])
    forbidden_features = forbidden_feature_matches(feature_columns)
    metadata_columns_in_features = sorted(feature_set.intersection(metadata_allowed))
    label_columns_in_features = sorted(feature_set.intersection(LABEL_COLUMNS))

    non_feature_columns = [column for column in all_columns if column not in feature_set]
    non_feature_forbidden = forbidden_feature_matches([column for column in non_feature_columns if column not in metadata_allowed])
    missing_required_metadata = [column for column in REQUIRED_METADATA_COLUMNS if column not in snapshot.columns]

    keep_yellow_rows = _keep_yellow_count(snapshot)
    day_checks = _train_day_checks(snapshot)
    time_checks = _time_checks(snapshot, strict_before_entry=strict_before_entry)

    checks: dict[str, Any] = {
        "manifest_status_pass": manifest.get("status") == "PASS",
        "manifest_pipeline_status": manifest.get("pipeline_status"),
        "row_count_matches_manifest": None if manifest_rows is None else int(len(snapshot)) == int(manifest_rows),
        "row_count_matches_expected_train": None if expected_rows is None else int(len(snapshot)) == int(expected_rows),
        "output_duplicate_keys": _duplicate_count(snapshot, JOIN_KEYS),
        "feature_columns_missing_in_csv": feature_columns_missing_in_csv,
        "duplicate_feature_columns": duplicate_feature_columns,
        "forbidden_feature_columns": forbidden_features,
        "label_columns_in_features": label_columns_in_features,
        "metadata_columns_in_features": metadata_columns_in_features,
        "unexpected_forbidden_nonfeature_columns": non_feature_forbidden,
        "missing_required_metadata_columns": missing_required_metadata,
        "keep_yellow_x_rows": keep_yellow_rows,
        "keep_yellow_x_rows_match_expected": None
        if expected_keep_yellow_rows is None
        else keep_yellow_rows == int(expected_keep_yellow_rows),
        "label_counts": _label_counts(snapshot),
        **day_checks,
        **time_checks,
    }

    fail_keys = [
        "manifest_status_pass",
        "row_count_matches_manifest",
        "row_count_matches_expected_train",
        "keep_yellow_x_rows_match_expected",
    ]
    zero_keys = [
        "output_duplicate_keys",
        "days_outside_train_range",
        "forward_days_present",
        "entry_time_parse_fail",
        "v2_combo_feature_time_parse_fail",
        "v2_combo_feature_time_not_before_entry",
        "v2_combo_available_before_entry_false",
        "v2_combo_entry_time_mismatch",
        "v2_combo_anchor_time_mismatch",
        "context_max_open_time_after_entry",
    ]
    list_or_dict_keys = [
        "feature_columns_missing_in_csv",
        "duplicate_feature_columns",
        "forbidden_feature_columns",
        "label_columns_in_features",
        "metadata_columns_in_features",
        "unexpected_forbidden_nonfeature_columns",
        "missing_required_metadata_columns",
    ]
    status_pass = all(checks.get(key) in {True, None} for key in fail_keys)
    status_pass = status_pass and all(checks.get(key) in {0, None} for key in zero_keys)
    status_pass = status_pass and all(not checks.get(key) for key in list_or_dict_keys)

    return {
        "status": "PASS" if status_pass else "FAIL",
        "pipeline_status": STATUS,
        "source_snapshot_status": V2_SNAPSHOT_STATUS,
        "created_utc": utc_now(),
        "rows": int(len(snapshot)),
        "manifest_rows": None if manifest_rows is None else int(manifest_rows),
        "feature_count": int(len(feature_columns)),
        "all_column_count": int(len(all_columns)),
        "train_range": {"start": TRAIN_START_DAY, "end": TRAIN_END_DAY},
        "forward_range_blocked": {"start": FORWARD_START_DAY, "end": FORWARD_END_DAY},
        "checks": checks,
        "guardrails": [
            "scan_only_manifest_feature_columns_for_model_features",
            "labels_yellow_strategy_votes_must_not_be_feature_columns",
            "no_future_postfact_outcome_stas3_tp_exit_features",
            "v2_combo_feature_time_utc_must_be_before_entry_time_utc",
            "forward_20260515_plus_must_not_be_in_train_snapshot",
            "KEEP_DRAFT_plus_yellow_x_rows_must_stay_present",
        ],
    }


def run_v2_leakage_guard(
    *,
    snapshot_path: Path = DEFAULT_V2_FEATURE_SNAPSHOT_PATH,
    manifest_path: Path = DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH,
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    output_path: Path = DEFAULT_V2_GUARD_REPORT_PATH,
    strict_before_entry: bool = True,
    strict: bool = True,
) -> dict[str, Any]:
    if not snapshot_path.exists():
        raise FileNotFoundError(f"V2 feature snapshot not found: {snapshot_path}")
    if not manifest_path.exists():
        raise FileNotFoundError(f"V2 feature snapshot manifest not found: {manifest_path}")

    snapshot = read_csv(snapshot_path)
    manifest = _load_manifest(manifest_path)
    expected_rows = None
    if ledger_path.exists():
        expected_rows = int(len(read_csv(ledger_path)))

    report = run_v2_leakage_guard_from_frames(
        snapshot=snapshot,
        manifest=manifest,
        expected_rows=expected_rows,
        expected_keep_yellow_rows=int(default_expected_train_counts()["KEEP_DRAFT_yellow_x"]),
        strict_before_entry=strict_before_entry,
    )
    report.update(
        {
            "snapshot_path": rel(snapshot_path),
            "manifest_path": rel(manifest_path),
            "ledger_path": rel(ledger_path) if ledger_path.exists() else None,
            "output_path": rel(output_path),
        }
    )
    write_json(output_path, report)
    if strict and report["status"] != "PASS":
        raise ValueError(f"STAS5 V2 leakage guard failed: {report['checks']}")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Guard STAS5 V2 feature matrix against leakage.")
    parser.add_argument("--snapshot-path", default=str(DEFAULT_V2_FEATURE_SNAPSHOT_PATH))
    parser.add_argument("--manifest-path", default=str(DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH))
    parser.add_argument("--ledger-path", default=str(DEFAULT_LEDGER_PATH))
    parser.add_argument("--output-path", default=str(DEFAULT_V2_GUARD_REPORT_PATH))
    parser.add_argument("--allow-equal-feature-entry-time", action="store_true")
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()

    report = run_v2_leakage_guard(
        snapshot_path=Path(args.snapshot_path),
        manifest_path=Path(args.manifest_path),
        ledger_path=Path(args.ledger_path),
        output_path=Path(args.output_path),
        strict_before_entry=not args.allow_equal_feature_entry_time,
        strict=not args.no_strict,
    )
    print(
        {
            "status": report["status"],
            "rows": report["rows"],
            "feature_count": report["feature_count"],
            "checks": report["checks"],
        }
    )
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
