from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from mlbotnav.stas5_common import (
    DEFAULT_FEATURE_MANIFEST_PATH,
    DEFAULT_FEATURE_PATH,
    DEFAULT_GUARD_REPORT_PATH,
    STATUS_CURRENT,
    forbidden_feature_matches,
    load_manifest_feature_columns,
    read_csv,
    rel,
    utc_now,
    write_json,
)


def scan_forbidden_columns(columns: list[str]) -> dict[str, list[str]]:
    return forbidden_feature_matches(columns)


def run_leakage_guard(
    *,
    feature_path: Path = DEFAULT_FEATURE_PATH,
    manifest_path: Path = DEFAULT_FEATURE_MANIFEST_PATH,
    output_path: Path = DEFAULT_GUARD_REPORT_PATH,
    columns_mode: str = "manifest_feature_columns",
    strict: bool = True,
) -> dict[str, Any]:
    if columns_mode not in {"manifest_feature_columns", "csv_all_columns"}:
        raise ValueError("columns_mode must be manifest_feature_columns or csv_all_columns")
    if columns_mode == "manifest_feature_columns":
        columns = load_manifest_feature_columns(manifest_path)
    else:
        if not feature_path.exists():
            raise FileNotFoundError(f"feature csv not found: {feature_path}")
        columns = list(read_csv(feature_path).columns)

    matches = scan_forbidden_columns(columns)
    report = {
        "status": "PASS" if not matches else "FAIL",
        "pipeline_status": STATUS_CURRENT,
        "created_utc": utc_now(),
        "columns_mode": columns_mode,
        "feature_path": rel(feature_path),
        "manifest_path": rel(manifest_path),
        "column_count_scanned": len(columns),
        "forbidden_columns": matches,
        "guardrails": [
            "scan_manifest_feature_columns_for_model_contract",
            "labels_and_yellow_audit_columns_may_exist_in_csv_but_must_not_be_feature_columns",
            "stas3_tp_exit_future_outcome_forbidden",
        ],
    }
    write_json(output_path, report)
    if strict and matches:
        raise ValueError(f"forbidden feature columns found: {sorted(matches)}")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Guard STAS5 feature matrix against leakage.")
    parser.add_argument("--feature-path", default=str(DEFAULT_FEATURE_PATH))
    parser.add_argument("--manifest-path", default=str(DEFAULT_FEATURE_MANIFEST_PATH))
    parser.add_argument("--output-path", default=str(DEFAULT_GUARD_REPORT_PATH))
    parser.add_argument("--columns-mode", default="manifest_feature_columns", choices=["manifest_feature_columns", "csv_all_columns"])
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()

    report = run_leakage_guard(
        feature_path=Path(args.feature_path),
        manifest_path=Path(args.manifest_path),
        output_path=Path(args.output_path),
        columns_mode=args.columns_mode,
        strict=not args.no_strict,
    )
    print(
        {
            "status": report["status"],
            "column_count_scanned": report["column_count_scanned"],
            "forbidden_columns": report["forbidden_columns"],
        }
    )
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
