from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import (
    DEFAULT_LEDGER_MANIFEST_PATH,
    DEFAULT_LEDGER_PATH,
    DEFAULT_MANUAL_LABEL_DIR,
    DEFAULT_STAS2_TRAIN_RUN_DIR,
    JOIN_KEYS,
    STATUS_CURRENT,
    compact_day,
    default_expected_train_counts,
    ensure_parent,
    is_keep_label,
    label_status_from_human_label,
    normalize_day,
    normalize_ts,
    read_csv,
    rel,
    to_int_flag,
    utc_now,
    write_json,
)


LEDGER_COLUMNS = [
    "day",
    "candidate_id",
    "record_id",
    "anchor_time_utc",
    "entry_time_utc",
    "anchor_low_price",
    "entry_open_price",
    "entry_price_5bps",
    "human_label",
    "label_status",
    "label_source",
    "yellow_x",
    "yellow_x_role",
    "yellow_x_conflict",
    "source_stas1_run",
    "source_stas2_run",
    "source_manual_label_file",
]


def _load_manual_labels(label_dir: Path, *, start_day: str, end_day: str) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for day in pd.date_range(pd.Timestamp(start_day), pd.Timestamp(end_day), freq="D"):
        compact = day.strftime("%Y%m%d")
        path = label_dir / f"LABELS_{compact}_ALL_ENTRIES_DRAFT.csv"
        if not path.exists():
            raise FileNotFoundError(f"manual label file not found: {path}")
        frame = read_csv(path)
        frame["source_manual_label_file"] = rel(path)
        rows.append(frame)
    if not rows:
        raise FileNotFoundError(f"no manual labels in {label_dir}")
    out = pd.concat(rows, ignore_index=True)
    out["day"] = out["day"].map(normalize_day)
    out["anchor_time_utc"] = out["anchor_time_utc"].map(normalize_ts)
    out["entry_time_utc"] = out["entry_time_utc"].map(normalize_ts)
    out["candidate_id"] = out["candidate_id"].astype(str)
    out["record_id"] = out["record_id"].astype(str)
    return out


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


def _count_labels(df: pd.DataFrame) -> dict[str, int]:
    labels = df["human_label"].astype(str)
    return {
        "rows": int(len(df)),
        "KEEP_DRAFT": int((labels == "KEEP_DRAFT").sum()),
        "CUT_DRAFT": int((labels == "CUT_DRAFT").sum()),
        "KEEP_APPROVED": int((labels == "KEEP_APPROVED").sum()),
        "CUT_APPROVED": int((labels == "CUT_APPROVED").sum()),
        "KEEP_DRAFT_yellow_x": int(((labels == "KEEP_DRAFT") & (df["yellow_x"].astype(int) == 1)).sum()),
        "KEEP_total_yellow_x": int((labels.map(is_keep_label) & (df["yellow_x"].astype(int) == 1)).sum()),
        "yellow_x_total": int((df["yellow_x"].astype(int) == 1).sum()),
    }


def _validate_ledger(df: pd.DataFrame, *, expected_counts: dict[str, int] | None = None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    counts = _count_labels(df)
    expected = expected_counts or {}
    for key, expected_value in expected.items():
        if counts.get(key) != int(expected_value):
            errors.append(f"{key}: expected {expected_value}, got {counts.get(key)}")

    duplicate_keys = int(df.duplicated(subset=JOIN_KEYS).sum())
    if duplicate_keys:
        errors.append(f"duplicate join keys: {duplicate_keys}")
    missing_entry_price = int(df["entry_price_5bps"].isna().sum()) if "entry_price_5bps" in df else len(df)
    if missing_entry_price:
        errors.append(f"entry_price_5bps missing rows: {missing_entry_price}")
    missing_source = int((df["source_stas1_run"].astype(str).str.len() == 0).sum()) if "source_stas1_run" in df else len(df)
    if missing_source:
        warnings.append(f"source_stas1_run empty rows: {missing_source}")
    return errors, warnings


def build_ledger(
    *,
    manual_label_dir: Path = DEFAULT_MANUAL_LABEL_DIR,
    stas2_run_dir: Path = DEFAULT_STAS2_TRAIN_RUN_DIR,
    output_csv: Path = DEFAULT_LEDGER_PATH,
    manifest_path: Path = DEFAULT_LEDGER_MANIFEST_PATH,
    start_day: str = "2026-05-01",
    end_day: str = "2026-05-14",
    expected_counts: dict[str, int] | None = None,
    strict: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    labels = _load_manual_labels(manual_label_dir, start_day=start_day, end_day=end_day)
    stas2 = _load_stas2_records(stas2_run_dir)
    stas2 = stas2[(stas2["day"] >= start_day) & (stas2["day"] <= end_day)].copy()

    manual_dupes = int(labels.duplicated(subset=JOIN_KEYS).sum())
    stas2_dupes = int(stas2.duplicated(subset=JOIN_KEYS).sum())
    if strict and (manual_dupes or stas2_dupes):
        raise ValueError(f"duplicate join keys: manual={manual_dupes}, stas2={stas2_dupes}")

    merged = labels.merge(
        stas2[
            [
                "day",
                "candidate_id",
                "record_id",
                "anchor_time_utc",
                "entry_time_utc",
                "entry_price_5bps",
                "source_run",
                "source_stas2_run",
            ]
        ].rename(
            columns={
                "anchor_time_utc": "stas2_anchor_time_utc",
                "entry_time_utc": "stas2_entry_time_utc",
                "source_run": "source_stas1_run",
            }
        ),
        on=JOIN_KEYS,
        how="left",
        indicator=True,
    )
    lost_after_join = int((merged["_merge"] != "both").sum())
    entry_time_mismatch = int((merged["entry_time_utc"] != merged["stas2_entry_time_utc"]).sum())
    anchor_time_mismatch = int((merged["anchor_time_utc"] != merged["stas2_anchor_time_utc"]).sum())

    merged["human_label"] = merged["human_label"].astype(str)
    merged["label_status"] = merged["human_label"].map(label_status_from_human_label)
    merged["yellow_x"] = merged["stas4_density_structure_yellow_x"].map(to_int_flag).astype(int)
    merged["yellow_x_role"] = "AUDIT_ONLY"
    merged["yellow_x_conflict"] = (merged["human_label"].map(is_keep_label) & (merged["yellow_x"] == 1)).astype(int)

    ledger = merged.copy()
    ledger["entry_price_5bps"] = pd.to_numeric(ledger["entry_price_5bps"], errors="coerce")
    ledger["anchor_low_price"] = pd.to_numeric(ledger["anchor_low_price"], errors="coerce")
    ledger["entry_open_price"] = pd.to_numeric(ledger["entry_open_price"], errors="coerce")
    for col in ["source_stas1_run", "source_stas2_run", "source_manual_label_file", "label_source"]:
        ledger[col] = ledger[col].fillna("").astype(str)
    ledger = ledger[LEDGER_COLUMNS].sort_values(["day", "entry_time_utc", "record_id"]).reset_index(drop=True)

    expected = expected_counts if expected_counts is not None else default_expected_train_counts()
    errors, warnings = _validate_ledger(ledger, expected_counts=expected)
    if lost_after_join:
        errors.append(f"lost rows after join with STAS2_RECORDS: {lost_after_join}")
    if entry_time_mismatch:
        errors.append(f"entry_time_utc mismatches with STAS2: {entry_time_mismatch}")
    if anchor_time_mismatch:
        errors.append(f"anchor_time_utc mismatches with STAS2: {anchor_time_mismatch}")

    counts = _count_labels(ledger)
    days = [normalize_day(day) for day in pd.date_range(pd.Timestamp(start_day), pd.Timestamp(end_day), freq="D")]
    per_day = {
        day: {
            "rows": int((ledger["day"] == day).sum()),
            "KEEP_DRAFT": int(((ledger["day"] == day) & (ledger["human_label"] == "KEEP_DRAFT")).sum()),
            "CUT_DRAFT": int(((ledger["day"] == day) & (ledger["human_label"] == "CUT_DRAFT")).sum()),
            "yellow_x": int(((ledger["day"] == day) & (ledger["yellow_x"] == 1)).sum()),
            "keep_yellow_x": int(((ledger["day"] == day) & (ledger["yellow_x_conflict"] == 1)).sum()),
        }
        for day in days
    }
    manifest = {
        "status": "PASS" if not errors else "FAIL",
        "pipeline_status": STATUS_CURRENT,
        "created_utc": utc_now(),
        "schema_version": 0,
        "train_window": {"start_day": start_day, "end_day": end_day},
        "manual_label_dir": rel(manual_label_dir),
        "stas2_run_dir": rel(stas2_run_dir),
        "output_csv": rel(output_csv),
        "counts": counts,
        "expected_counts": expected,
        "per_day": per_day,
        "checks": {
            "manual_duplicates": manual_dupes,
            "stas2_duplicates": stas2_dupes,
            "lost_after_join": lost_after_join,
            "entry_time_mismatch": entry_time_mismatch,
            "anchor_time_mismatch": anchor_time_mismatch,
            "entry_price_5bps_missing": int(ledger["entry_price_5bps"].isna().sum()),
        },
        "guardrails": [
            "human_label_is_target",
            "yellow_x_is_audit_only",
            "keep_yellow_x_rows_preserved",
            "no_stas3_tp_exit_fields",
        ],
        "warnings": warnings,
        "errors": errors,
    }

    ensure_parent(output_csv)
    ledger.to_csv(output_csv, index=False, encoding="utf-8-sig")
    write_json(manifest_path, manifest)
    if strict and errors:
        raise ValueError("; ".join(errors))
    return ledger, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build STAS5 ML ledger from human labels and STAS2 records.")
    parser.add_argument("--manual-label-dir", default=str(DEFAULT_MANUAL_LABEL_DIR))
    parser.add_argument("--stas2-run-dir", default=str(DEFAULT_STAS2_TRAIN_RUN_DIR))
    parser.add_argument("--output-csv", default=str(DEFAULT_LEDGER_PATH))
    parser.add_argument("--manifest-path", default=str(DEFAULT_LEDGER_MANIFEST_PATH))
    parser.add_argument("--start-day", default="2026-05-01")
    parser.add_argument("--end-day", default="2026-05-14")
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()

    _ledger, manifest = build_ledger(
        manual_label_dir=Path(args.manual_label_dir),
        stas2_run_dir=Path(args.stas2_run_dir),
        output_csv=Path(args.output_csv),
        manifest_path=Path(args.manifest_path),
        start_day=args.start_day,
        end_day=args.end_day,
        strict=not args.no_strict,
    )
    print(
        {
            "status": manifest["status"],
            "output_csv": manifest["output_csv"],
            "counts": manifest["counts"],
            "errors": manifest["errors"],
        }
    )
    return 0 if manifest["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
