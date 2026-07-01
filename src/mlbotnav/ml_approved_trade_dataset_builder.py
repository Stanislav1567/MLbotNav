from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.ml_approved_package_registry_reader import read_approved_package_registry
from mlbotnav.ml_trade_dataset_contract import REQUIRED_COLUMNS, validate_trade_dataset_csv


PROVENANCE_COLUMNS = [
    "source_package_path",
    "source_trade_log_path",
]


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _resolve_project_path(project_root: Path, raw_path: object) -> Path:
    value = str(raw_path or "").strip()
    if not value:
        return (project_root / "__missing_path__").resolve()
    path = Path(value)
    if not path.is_absolute():
        path = project_root / path
    return path.resolve()


def _project_relative(project_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), [{str(k): str(v if v is not None else "") for k, v in row.items()} for row in reader]


def _ordered_fieldnames(source_fieldnames: list[list[str]]) -> list[str]:
    ordered = list(REQUIRED_COLUMNS)
    for col in PROVENANCE_COLUMNS:
        if col not in ordered:
            ordered.append(col)
    for fieldnames in source_fieldnames:
        for col in fieldnames:
            if col not in ordered:
                ordered.append(col)
    return ordered


def build_approved_trade_dataset(
    *,
    project_root: Path,
    registry_path: Path,
    out_dir: Path,
    dataset_name: str | None = None,
) -> dict[str, Any]:
    root = project_root.resolve()
    resolved_registry = _resolve_project_path(root, registry_path)
    resolved_out_dir = _resolve_project_path(root, out_dir)

    registry_result = read_approved_package_registry(project_root=root, registry_path=resolved_registry)
    if registry_result.get("status") != "PASS":
        return {
            "status": "FAIL",
            "reason": "registry_reader_failed",
            "registry_path": str(resolved_registry),
            "approved_count": int(registry_result.get("approved_count", 0)),
            "packages_total": 0,
            "rows_total": 0,
            "dataset_path": "",
            "manifest_path": "",
            "failures": registry_result.get("failures", []),
            "registry_reader": registry_result,
            "contract": None,
        }

    packages = registry_result.get("packages")
    packages = packages if isinstance(packages, list) else []
    if not packages:
        return {
            "status": "PASS",
            "reason": "NO_APPROVED_PACKAGES",
            "registry_path": str(resolved_registry),
            "approved_count": 0,
            "packages_total": 0,
            "rows_total": 0,
            "dataset_path": "",
            "manifest_path": "",
            "failures": [],
            "registry_reader": registry_result,
            "contract": None,
        }

    resolved_out_dir.mkdir(parents=True, exist_ok=True)
    tag = _utc_tag()
    dataset_stem = str(dataset_name or f"approved_trade_dataset_{tag}").strip()
    if not dataset_stem:
        dataset_stem = f"approved_trade_dataset_{tag}"
    dataset_path = resolved_out_dir / f"{dataset_stem}.csv"
    manifest_path = resolved_out_dir / f"{dataset_stem}.manifest.json"

    all_rows: list[dict[str, str]] = []
    all_fieldnames: list[list[str]] = []
    package_summaries: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for index, package in enumerate(packages):
        if not isinstance(package, dict):
            failures.append({"index": index, "run_id": "", "errors": ["invalid_package:not_object"]})
            continue

        run_id = str(package.get("run_id") or "").strip()
        trade_log_path = _resolve_project_path(root, package.get("trade_log_path"))
        contract = validate_trade_dataset_csv(trade_log_path, approved_mode=True)
        if contract.get("status") != "PASS":
            failures.append(
                {
                    "index": index,
                    "run_id": run_id,
                    "trade_log_path": _project_relative(root, trade_log_path),
                    "errors": ["contract_audit_not_pass"],
                    "contract": contract,
                }
            )
            continue

        fieldnames, rows = _read_csv(trade_log_path)
        all_fieldnames.append(fieldnames)
        package_path = str(package.get("package_path") or "").strip()
        rel_trade_log = _project_relative(root, trade_log_path)
        for row in rows:
            row["source_package_path"] = package_path
            row["source_trade_log_path"] = rel_trade_log
            all_rows.append(row)
        package_summaries.append(
            {
                "run_id": run_id,
                "package_path": package_path,
                "trade_log_path": rel_trade_log,
                "rows_total": int(len(rows)),
                "contract_status": str(contract.get("status") or ""),
            }
        )

    if failures:
        return {
            "status": "FAIL",
            "reason": "package_contract_failed",
            "registry_path": str(resolved_registry),
            "approved_count": int(registry_result.get("approved_count", len(packages))),
            "packages_total": int(len(packages)),
            "rows_total": int(len(all_rows)),
            "dataset_path": "",
            "manifest_path": "",
            "failures": failures,
            "registry_reader": registry_result,
            "contract": None,
        }

    fieldnames = _ordered_fieldnames(all_fieldnames)
    with dataset_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in all_rows:
            writer.writerow({col: row.get(col, "") for col in fieldnames})

    contract_result = validate_trade_dataset_csv(dataset_path, approved_mode=True)
    status = "PASS" if contract_result.get("status") == "PASS" else "FAIL"
    if status != "PASS":
        failures.append({"index": -1, "run_id": "", "errors": ["assembled_dataset_contract_not_pass"], "contract": contract_result})

    manifest: dict[str, Any] = {
        "status": status,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_path": _project_relative(root, dataset_path),
        "registry_path": _project_relative(root, resolved_registry),
        "approved_count": int(registry_result.get("approved_count", len(packages))),
        "packages_total": int(len(packages)),
        "rows_total": int(len(all_rows)),
        "packages": package_summaries,
        "contract": contract_result,
        "boundary": {
            "manual_approval_required": True,
            "ml_training_started": False,
            "direct_optuna_report_scan": False,
        },
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "status": status,
        "reason": "OK" if status == "PASS" else "assembled_dataset_contract_not_pass",
        "registry_path": str(resolved_registry),
        "approved_count": int(registry_result.get("approved_count", len(packages))),
        "packages_total": int(len(packages)),
        "rows_total": int(len(all_rows)),
        "dataset_path": _project_relative(root, dataset_path),
        "manifest_path": _project_relative(root, manifest_path),
        "failures": failures,
        "registry_reader": registry_result,
        "contract": contract_result,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build ML trade dataset from approved calibration packages.")
    parser.add_argument("--registry-path", default="configs/ml_approved_calibration_packages.yaml")
    parser.add_argument("--out-dir", default="reports/ml_datasets")
    parser.add_argument("--dataset-name", default=None)
    parser.add_argument("--report-dir", default="reports/qa_gate")
    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parents[2]
    result = build_approved_trade_dataset(
        project_root=project_root,
        registry_path=Path(args.registry_path),
        out_dir=Path(args.out_dir),
        dataset_name=args.dataset_name,
    )

    report_dir = _resolve_project_path(project_root, args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"ml_approved_trade_dataset_builder_{_utc_tag()}.json"
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": result["status"],
                "reason": result["reason"],
                "report_path": str(report_path),
                "dataset_path": result["dataset_path"],
                "packages_total": result["packages_total"],
                "rows_total": result["rows_total"],
                "failures": len(result["failures"]),
            },
            ensure_ascii=False,
        )
    )
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
