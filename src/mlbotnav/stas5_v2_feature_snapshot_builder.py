from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import (
    DEFAULT_FEATURE_MANIFEST_PATH,
    DEFAULT_FEATURE_PATH,
    DEFAULT_LEDGER_PATH,
    JOIN_KEYS,
    LABEL_COLUMNS,
    METADATA_COLUMNS,
    STAS5_ARTIFACTS_DIR,
    forbidden_feature_matches,
    is_keep_label,
    load_manifest_feature_columns,
    normalize_day,
    normalize_ts,
    read_csv,
    rel,
    utc_now,
    write_json,
)
from mlbotnav.stas5_feature_snapshot_builder import classify_feature_columns
from mlbotnav.stas5_v2_combo_feature_exporter import DEFAULT_V2_COMBO_FEATURE_PATH


STATUS = "STAS5_V2_FEATURE_SNAPSHOT_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3"
V2_FEATURE_SNAPSHOT_BASENAME = "stas5_v2_feature_snapshot_20260501_20260514_v0"
DEFAULT_V2_FEATURE_SNAPSHOT_PATH = STAS5_ARTIFACTS_DIR / "v2" / "features" / f"{V2_FEATURE_SNAPSHOT_BASENAME}.csv"
DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH = (
    STAS5_ARTIFACTS_DIR / "v2" / "features" / f"{V2_FEATURE_SNAPSHOT_BASENAME}.manifest.json"
)
DEFAULT_V2_COMBO_MANIFEST_PATH = DEFAULT_V2_COMBO_FEATURE_PATH.with_suffix(".manifest.json")

V2_COMBO_METADATA_RENAME = {
    "anchor_time_utc": "v2_combo_anchor_time_utc",
    "entry_time_utc": "v2_combo_entry_time_utc",
    "feature_time_utc": "v2_combo_feature_time_utc",
    "feature_available_before_entry": "v2_combo_feature_available_before_entry",
    "entry_price_5bps": "v2_combo_entry_price_5bps",
    "source_stas2_run": "v2_combo_source_stas2_run",
    "source_ohlcv": "v2_combo_source_ohlcv",
    "audit_no_trade_reason": "v2_combo_audit_no_trade_reason",
}


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


def _duplicate_count(df: pd.DataFrame) -> int:
    return int(df.duplicated(JOIN_KEYS).sum())


def _keep_yellow_count(df: pd.DataFrame) -> int:
    if "human_label" not in df or "yellow_x" not in df:
        return 0
    yellow = pd.to_numeric(df["yellow_x"], errors="coerce").fillna(0).astype(int)
    return int(sum(bool(is_keep_label(label)) and int(flag) == 1 for label, flag in zip(df["human_label"], yellow)))


def _prepare_combo_payload(combo: pd.DataFrame, v2_feature_columns: list[str]) -> pd.DataFrame:
    combo = _normalize_keys(combo)
    needed = JOIN_KEYS + [column for column in V2_COMBO_METADATA_RENAME if column in combo.columns] + list(v2_feature_columns)
    payload = combo[needed].copy()
    return payload.rename(columns={key: value for key, value in V2_COMBO_METADATA_RENAME.items() if key in payload.columns})


def build_v2_feature_snapshot_from_frames(
    *,
    v1_snapshot: pd.DataFrame,
    v2_combo: pd.DataFrame,
    v1_feature_columns: list[str],
    v2_feature_columns: list[str],
    ledger: pd.DataFrame | None = None,
    source_v1_snapshot: str = "in_memory",
    source_v2_combo: str = "in_memory",
) -> tuple[pd.DataFrame, dict[str, Any]]:
    v1_snapshot = _normalize_keys(v1_snapshot)
    v2_combo = _normalize_keys(v2_combo)
    if ledger is not None:
        ledger = _normalize_keys(ledger)

    missing_v1_features = [column for column in v1_feature_columns if column not in v1_snapshot.columns]
    missing_v2_features = [column for column in v2_feature_columns if column not in v2_combo.columns]
    for column in missing_v1_features:
        v1_snapshot[column] = pd.NA
    for column in missing_v2_features:
        v2_combo[column] = pd.NA

    combo_payload = _prepare_combo_payload(v2_combo, v2_feature_columns)
    merged = v1_snapshot.merge(combo_payload, on=JOIN_KEYS, how="left", indicator=True)
    lost_after_combo_join = int((merged["_merge"] != "both").sum())
    merged = merged.drop(columns=["_merge"])

    if ledger is not None:
        ledger_keys = ledger[JOIN_KEYS + [column for column in ["entry_time_utc", "anchor_time_utc", "human_label", "yellow_x"] if column in ledger.columns]].copy()
        ledger_check = merged[JOIN_KEYS].merge(ledger_keys, on=JOIN_KEYS, how="left", indicator=True)
        lost_after_ledger_check = int((ledger_check["_merge"] != "both").sum())
    else:
        lost_after_ledger_check = None

    entry_mismatch = 0
    if "entry_time_utc" in merged.columns and "v2_combo_entry_time_utc" in merged.columns:
        entry_mismatch = int((merged["entry_time_utc"].astype(str) != merged["v2_combo_entry_time_utc"].astype(str)).sum())
    anchor_mismatch = 0
    if "anchor_time_utc" in merged.columns and "v2_combo_anchor_time_utc" in merged.columns:
        anchor_mismatch = int((merged["anchor_time_utc"].astype(str) != merged["v2_combo_anchor_time_utc"].astype(str)).sum())

    combo_context_false = 0
    if "v2_combo_feature_available_before_entry" in merged.columns:
        combo_context_false = int(
            (merged["v2_combo_feature_available_before_entry"].astype(str).str.lower() != "true").sum()
        )

    v1_feature_columns = list(dict.fromkeys(v1_feature_columns))
    v2_feature_columns = list(dict.fromkeys(v2_feature_columns))
    feature_columns = v1_feature_columns + [column for column in v2_feature_columns if column not in v1_feature_columns]
    forbidden = forbidden_feature_matches(feature_columns)
    numeric, categorical, boolean = classify_feature_columns(merged, feature_columns)

    metadata_columns = [column for column in METADATA_COLUMNS + LABEL_COLUMNS if column in merged.columns]
    metadata_columns += [column for column in V2_COMBO_METADATA_RENAME.values() if column in merged.columns]
    metadata_columns = list(dict.fromkeys(metadata_columns))
    ordered = metadata_columns + [column for column in feature_columns if column not in metadata_columns]
    out = merged[ordered].sort_values([c for c in ["day", "entry_time_utc", "record_id"] if c in merged.columns]).reset_index(drop=True)

    ledger_rows = None if ledger is None else int(len(ledger))
    keep_yellow = _keep_yellow_count(out)
    status_pass = (
        lost_after_combo_join == 0
        and (lost_after_ledger_check in {None, 0})
        and _duplicate_count(out) == 0
        and entry_mismatch == 0
        and anchor_mismatch == 0
        and combo_context_false == 0
        and not forbidden
        and not missing_v1_features
        and not missing_v2_features
        and (ledger_rows is None or int(len(out)) == ledger_rows)
    )
    manifest = {
        "status": "PASS" if status_pass else "FAIL",
        "pipeline_status": STATUS,
        "created_utc": utc_now(),
        "schema_version": 0,
        "rows": int(len(out)),
        "ledger_rows": ledger_rows,
        "source_v1_snapshot": source_v1_snapshot,
        "source_v2_combo": source_v2_combo,
        "feature_columns": feature_columns,
        "feature_count": len(feature_columns),
        "v1_feature_columns": v1_feature_columns,
        "v1_feature_count": len(v1_feature_columns),
        "v2_feature_columns": v2_feature_columns,
        "v2_feature_count": len(v2_feature_columns),
        "numeric_columns": numeric,
        "categorical_columns": categorical,
        "boolean_columns": boolean,
        "label_columns": [column for column in LABEL_COLUMNS if column in out.columns],
        "metadata_columns": metadata_columns,
        "checks": {
            "row_count_matches_ledger": None if ledger_rows is None else int(len(out)) == ledger_rows,
            "v1_duplicate_keys": _duplicate_count(v1_snapshot),
            "v2_duplicate_keys": _duplicate_count(v2_combo),
            "output_duplicate_keys": _duplicate_count(out),
            "lost_after_combo_join": lost_after_combo_join,
            "lost_after_ledger_check": lost_after_ledger_check,
            "entry_time_mismatch": entry_mismatch,
            "anchor_time_mismatch": anchor_mismatch,
            "v2_combo_feature_available_before_entry_false": combo_context_false,
            "forbidden_feature_columns": forbidden,
            "missing_v1_features": missing_v1_features,
            "missing_v2_features": missing_v2_features,
            "keep_yellow_x_rows": keep_yellow,
        },
        "guardrails": [
            "join_keys_day_candidate_id_record_id",
            "ledger_labels_are_metadata_not_features",
            "yellow_x_is_metadata_not_feature",
            "v2_combo_feature_time_must_be_before_entry_time",
            "no_postfact_future_stas3_tp_exit_feature_columns",
            "forward_20260515_plus_not_used_in_train_snapshot",
        ],
    }
    return out, manifest


def build_v2_feature_snapshot(
    *,
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    v1_snapshot_path: Path = DEFAULT_FEATURE_PATH,
    v1_manifest_path: Path = DEFAULT_FEATURE_MANIFEST_PATH,
    v2_combo_path: Path = DEFAULT_V2_COMBO_FEATURE_PATH,
    v2_combo_manifest_path: Path = DEFAULT_V2_COMBO_MANIFEST_PATH,
    output_csv: Path = DEFAULT_V2_FEATURE_SNAPSHOT_PATH,
    manifest_path: Path = DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH,
    strict: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    for path in [ledger_path, v1_snapshot_path, v1_manifest_path, v2_combo_path, v2_combo_manifest_path]:
        if not path.exists():
            raise FileNotFoundError(f"required STAS5 V2 snapshot input not found: {path}")

    ledger = read_csv(ledger_path)
    v1_snapshot = read_csv(v1_snapshot_path)
    v2_combo = read_csv(v2_combo_path)
    v1_features = load_manifest_feature_columns(v1_manifest_path)
    v2_features = load_manifest_feature_columns(v2_combo_manifest_path)
    snapshot, manifest = build_v2_feature_snapshot_from_frames(
        v1_snapshot=v1_snapshot,
        v2_combo=v2_combo,
        v1_feature_columns=v1_features,
        v2_feature_columns=v2_features,
        ledger=ledger,
        source_v1_snapshot=rel(v1_snapshot_path),
        source_v2_combo=rel(v2_combo_path),
    )
    manifest["ledger_path"] = rel(ledger_path)
    manifest["v1_manifest_path"] = rel(v1_manifest_path)
    manifest["v2_combo_manifest_path"] = rel(v2_combo_manifest_path)
    manifest["output_csv"] = rel(output_csv)
    manifest["manifest_path"] = rel(manifest_path)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    snapshot.to_csv(output_csv, index=False, encoding="utf-8-sig")
    write_json(manifest_path, manifest)
    if strict and manifest["status"] != "PASS":
        raise ValueError(f"STAS5 V2 feature snapshot failed checks: {manifest['checks']}")
    return snapshot, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build STAS5 V2 combined feature snapshot.")
    parser.add_argument("--ledger-path", default=str(DEFAULT_LEDGER_PATH))
    parser.add_argument("--v1-snapshot-path", default=str(DEFAULT_FEATURE_PATH))
    parser.add_argument("--v1-manifest-path", default=str(DEFAULT_FEATURE_MANIFEST_PATH))
    parser.add_argument("--v2-combo-path", default=str(DEFAULT_V2_COMBO_FEATURE_PATH))
    parser.add_argument("--v2-combo-manifest-path", default=str(DEFAULT_V2_COMBO_MANIFEST_PATH))
    parser.add_argument("--output-csv", default=str(DEFAULT_V2_FEATURE_SNAPSHOT_PATH))
    parser.add_argument("--manifest-path", default=str(DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH))
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()
    _snapshot, manifest = build_v2_feature_snapshot(
        ledger_path=Path(args.ledger_path),
        v1_snapshot_path=Path(args.v1_snapshot_path),
        v1_manifest_path=Path(args.v1_manifest_path),
        v2_combo_path=Path(args.v2_combo_path),
        v2_combo_manifest_path=Path(args.v2_combo_manifest_path),
        output_csv=Path(args.output_csv),
        manifest_path=Path(args.manifest_path),
        strict=not args.no_strict,
    )
    print(
        {
            "status": manifest["status"],
            "rows": manifest["rows"],
            "feature_count": manifest["feature_count"],
            "v1_feature_count": manifest["v1_feature_count"],
            "v2_feature_count": manifest["v2_feature_count"],
            "checks": manifest["checks"],
        }
    )
    return 0 if manifest["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
