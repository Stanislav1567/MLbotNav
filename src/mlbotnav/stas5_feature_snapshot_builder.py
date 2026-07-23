from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import (
    DEFAULT_FEATURE_MANIFEST_PATH,
    DEFAULT_FEATURE_PATH,
    DEFAULT_LEDGER_PATH,
    DEFAULT_STAS2_TRAIN_RUN_DIR,
    JOIN_KEYS,
    LABEL_COLUMNS,
    METADATA_COLUMNS,
    STATUS_CURRENT,
    forbidden_feature_matches,
    normalize_day,
    normalize_ts,
    read_csv,
    rel,
    utc_now,
    write_json,
)


FEATURE_EXACT_COLUMNS = {
    "suggested_type",
    "score",
    "day_type",
    "is_weekend",
    "session_time_bucket_code",
    "effective_session_code",
    "real_tradfi_session_open",
    "stas1_risk_flags",
    "stas1_anchor_age_bars",
    "context_before_entry_check",
    "entry_setup_quality_code",
    "entry_setup_quality_rank",
}

FEATURE_PREFIXES = (
    "stas1_feature_",
    "pre_",
    "session_so_far_",
    "day_so_far_",
)

NON_MODEL_SUFFIXES = (
    "_time_utc",
    "_input",
    "_reason",
    "_price",
)

NON_MODEL_EXACT = {
    "source_run",
    "day_utc",
    "candidate_id",
    "record_id",
    "anchor_time_utc",
    "entry_time_utc",
    "entry_open_price",
    "entry_price_5bps",
    "anchor_low_price",
    "review_label",
    "outcome_status",
    "is_good_stas1_review",
    "session_time_bucket_label",
    "effective_session_label",
    "entry_setup_quality_label",
    "entry_setup_decision_input",
    "context_max_open_time_utc",
    "phase_decision_input",
    "long_wave_decision_input",
    "stas2_boundary",
}


def _load_stas2_records(stas2_run_dir: Path) -> pd.DataFrame:
    path = stas2_run_dir / "STAS2_RECORDS.csv"
    if not path.exists():
        raise FileNotFoundError(f"STAS2_RECORDS.csv not found: {path}")
    out = read_csv(path)
    out["day"] = out["day_utc"].map(normalize_day)
    out["anchor_time_utc"] = out["anchor_time_utc"].map(normalize_ts)
    out["entry_time_utc"] = out["entry_time_utc"].map(normalize_ts)
    out["candidate_id"] = out["candidate_id"].astype(str)
    out["record_id"] = out["record_id"].astype(str)
    out["source_stas2_run"] = rel(stas2_run_dir)
    return out


def is_candidate_feature_column(column: str) -> bool:
    if column in NON_MODEL_EXACT:
        return False
    if any(column.endswith(suffix) for suffix in NON_MODEL_SUFFIXES):
        return False
    if column in FEATURE_EXACT_COLUMNS:
        return True
    if column.startswith(FEATURE_PREFIXES):
        return True
    return False


def select_feature_columns(stas2_columns: list[str]) -> list[str]:
    columns = [column for column in stas2_columns if is_candidate_feature_column(str(column))]
    forbidden = forbidden_feature_matches(columns)
    return [column for column in columns if column not in forbidden]


def classify_feature_columns(df: pd.DataFrame, feature_columns: list[str]) -> tuple[list[str], list[str], list[str]]:
    numeric: list[str] = []
    categorical: list[str] = []
    boolean: list[str] = []
    for column in feature_columns:
        if column not in df:
            categorical.append(column)
            continue
        series = df[column]
        if pd.api.types.is_bool_dtype(series):
            boolean.append(column)
            categorical.append(column)
        elif pd.api.types.is_numeric_dtype(series):
            numeric.append(column)
        else:
            categorical.append(column)
    return numeric, categorical, boolean


def build_feature_snapshot_from_frames(
    *,
    stas2: pd.DataFrame,
    ledger: pd.DataFrame | None,
    source_stas2_run: str,
    feature_columns: list[str] | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    stas2 = stas2.copy()
    stas2["day"] = stas2["day"].map(normalize_day) if "day" in stas2 else stas2["day_utc"].map(normalize_day)
    stas2["entry_time_utc"] = stas2["entry_time_utc"].map(normalize_ts)
    stas2["anchor_time_utc"] = stas2["anchor_time_utc"].map(normalize_ts)
    stas2["candidate_id"] = stas2["candidate_id"].astype(str)
    stas2["record_id"] = stas2["record_id"].astype(str)
    stas2["source_stas2_run"] = source_stas2_run

    if feature_columns is None:
        feature_columns = select_feature_columns(list(stas2.columns))
    missing_features = [column for column in feature_columns if column not in stas2.columns]
    for column in missing_features:
        stas2[column] = pd.NA

    if ledger is not None:
        ledger = ledger.copy()
        ledger["day"] = ledger["day"].map(normalize_day)
        ledger["entry_time_utc"] = ledger["entry_time_utc"].map(normalize_ts)
        ledger["anchor_time_utc"] = ledger["anchor_time_utc"].map(normalize_ts)
        ledger["candidate_id"] = ledger["candidate_id"].astype(str)
        ledger["record_id"] = ledger["record_id"].astype(str)
        label_meta = ledger[[column for column in METADATA_COLUMNS + LABEL_COLUMNS if column in ledger.columns]].copy()
        join_payload_columns = JOIN_KEYS + [column for column in ["context_max_open_time_utc"] if column in stas2.columns] + feature_columns
        merged = label_meta.merge(
            stas2[join_payload_columns],
            on=JOIN_KEYS,
            how="left",
            indicator=True,
        )
        lost_after_join = int((merged["_merge"] != "both").sum())
        merged = merged.drop(columns=["_merge"])
    else:
        base_meta = [
            "day",
            "candidate_id",
            "record_id",
            "anchor_time_utc",
            "entry_time_utc",
            "entry_open_price",
            "entry_price_5bps",
            "anchor_low_price",
            "source_stas2_run",
            "context_max_open_time_utc",
        ]
        merged = stas2[[column for column in base_meta if column in stas2.columns] + feature_columns].copy()
        lost_after_join = 0

    for column in feature_columns:
        if column not in merged.columns:
            merged[column] = pd.NA

    ordered_columns = [column for column in METADATA_COLUMNS + LABEL_COLUMNS if column in merged.columns]
    ordered_columns += [column for column in feature_columns if column not in ordered_columns]
    out = merged[ordered_columns].sort_values([c for c in ["day", "entry_time_utc", "record_id"] if c in merged.columns]).reset_index(drop=True)

    numeric, categorical, boolean = classify_feature_columns(out, feature_columns)
    forbidden = forbidden_feature_matches(feature_columns)
    manifest = {
        "status": "PASS" if not forbidden and lost_after_join == 0 else "FAIL",
        "pipeline_status": STATUS_CURRENT,
        "created_utc": utc_now(),
        "schema_version": 0,
        "rows": int(len(out)),
        "source_stas2_run": source_stas2_run,
        "feature_columns": feature_columns,
        "feature_count": len(feature_columns),
        "numeric_columns": numeric,
        "categorical_columns": categorical,
        "boolean_columns": boolean,
        "label_columns": [column for column in LABEL_COLUMNS if column in out.columns],
        "metadata_columns": [column for column in METADATA_COLUMNS if column in out.columns],
        "missing_features_added": missing_features,
        "checks": {
            "lost_after_join": lost_after_join,
            "forbidden_feature_columns": forbidden,
            "context_before_entry_false": int((out.get("context_before_entry_check", pd.Series(dtype=bool)).astype(str).str.lower() == "false").sum())
            if "context_before_entry_check" in out
            else None,
        },
        "guardrails": [
            "features_selected_by_allowlist",
            "yellow_x_not_in_feature_columns",
            "strategy_votes_not_in_feature_columns",
            "stas3_tp_exit_not_in_feature_columns",
            "future_outcome_not_in_feature_columns",
        ],
    }
    return out, manifest


def build_feature_snapshot(
    *,
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    stas2_run_dir: Path = DEFAULT_STAS2_TRAIN_RUN_DIR,
    output_csv: Path = DEFAULT_FEATURE_PATH,
    manifest_path: Path = DEFAULT_FEATURE_MANIFEST_PATH,
    strict: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if not ledger_path.exists():
        raise FileNotFoundError(f"ledger not found: {ledger_path}")
    ledger = read_csv(ledger_path)
    stas2 = _load_stas2_records(stas2_run_dir)
    snapshot, manifest = build_feature_snapshot_from_frames(
        stas2=stas2,
        ledger=ledger,
        source_stas2_run=rel(stas2_run_dir),
    )
    manifest["ledger_path"] = rel(ledger_path)
    manifest["output_csv"] = rel(output_csv)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    snapshot.to_csv(output_csv, index=False, encoding="utf-8-sig")
    write_json(manifest_path, manifest)
    if strict and manifest["status"] != "PASS":
        raise ValueError(f"feature snapshot failed checks: {manifest['checks']}")
    return snapshot, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build STAS5 pre-entry feature snapshot.")
    parser.add_argument("--ledger-path", default=str(DEFAULT_LEDGER_PATH))
    parser.add_argument("--stas2-run-dir", default=str(DEFAULT_STAS2_TRAIN_RUN_DIR))
    parser.add_argument("--output-csv", default=str(DEFAULT_FEATURE_PATH))
    parser.add_argument("--manifest-path", default=str(DEFAULT_FEATURE_MANIFEST_PATH))
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()

    _snapshot, manifest = build_feature_snapshot(
        ledger_path=Path(args.ledger_path),
        stas2_run_dir=Path(args.stas2_run_dir),
        output_csv=Path(args.output_csv),
        manifest_path=Path(args.manifest_path),
        strict=not args.no_strict,
    )
    print(
        {
            "status": manifest["status"],
            "rows": manifest["rows"],
            "feature_count": manifest["feature_count"],
            "forbidden_feature_columns": manifest["checks"]["forbidden_feature_columns"],
        }
    )
    return 0 if manifest["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
