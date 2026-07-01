from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.ml_approved_package_registry_reader import read_approved_package_registry


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


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def _read_trade_log_run_ids(path: Path) -> tuple[list[str], list[dict[str, Any]]]:
    run_ids: list[str] = []
    row_errors: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        if "run_id" not in fieldnames:
            row_errors.append({"row_index": 0, "errors": ["missing_column:run_id"]})
            return run_ids, row_errors
        for row_index, row in enumerate(reader, start=1):
            run_id = str(row.get("run_id") or "").strip()
            if not run_id:
                row_errors.append({"row_index": row_index, "errors": ["empty:run_id"]})
            else:
                run_ids.append(run_id)
    if not run_ids and not row_errors:
        row_errors.append({"row_index": 0, "errors": ["empty_trade_log:no_rows"]})
    return run_ids, row_errors


def audit_package_run_id_alignment(*, project_root: Path, package_path: Path) -> dict[str, Any]:
    root = project_root.resolve()
    package_dir = _resolve_project_path(root, package_path)
    manifest_path = package_dir / "manifest.json"
    calibration_path = package_dir / "calibration_package.json"
    trade_log_path = package_dir / "trade_log.csv"

    errors: list[str] = []
    values: dict[str, Any] = {
        "manifest_run_id": "",
        "calibration_package_run_id": "",
        "trade_log_run_ids": [],
    }

    manifest: dict[str, Any] | None = None
    calibration: dict[str, Any] | None = None
    if not manifest_path.exists():
        errors.append("missing_file:manifest.json")
    else:
        try:
            manifest = _load_json(manifest_path)
            values["manifest_run_id"] = str(manifest.get("run_id") or "").strip()
            if not values["manifest_run_id"]:
                errors.append("empty:manifest.run_id")
        except Exception as exc:
            errors.append(f"invalid_json:manifest.json:{type(exc).__name__}")

    if not calibration_path.exists():
        errors.append("missing_file:calibration_package.json")
    else:
        try:
            calibration = _load_json(calibration_path)
            values["calibration_package_run_id"] = str(calibration.get("run_id") or "").strip()
            if not values["calibration_package_run_id"]:
                errors.append("empty:calibration_package.run_id")
        except Exception as exc:
            errors.append(f"invalid_json:calibration_package.json:{type(exc).__name__}")

    trade_row_errors: list[dict[str, Any]] = []
    trade_run_ids: list[str] = []
    if not trade_log_path.exists():
        errors.append("missing_file:trade_log.csv")
    else:
        trade_run_ids, trade_row_errors = _read_trade_log_run_ids(trade_log_path)
        values["trade_log_run_ids"] = sorted(set(trade_run_ids))
        if trade_row_errors:
            errors.append("invalid_trade_log_run_id_rows")

    non_empty_values: list[str] = []
    for key in ("manifest_run_id", "calibration_package_run_id"):
        value = str(values.get(key) or "").strip()
        if value:
            non_empty_values.append(value)
    non_empty_values.extend([str(v) for v in values.get("trade_log_run_ids", []) if str(v).strip()])
    unique_values = sorted(set(non_empty_values))
    if len(unique_values) > 1:
        errors.append("run_id_mismatch")

    expected = unique_values[0] if len(unique_values) == 1 else ""
    status = "PASS" if not errors else "FAIL"
    return {
        "status": status,
        "package_path": _project_relative(root, package_dir),
        "manifest_path": _project_relative(root, manifest_path),
        "calibration_package_path": _project_relative(root, calibration_path),
        "trade_log_path": _project_relative(root, trade_log_path),
        "expected_run_id": expected,
        "values": values,
        "trade_log_row_errors": trade_row_errors,
        "errors": errors,
        "files_checked": {
            "manifest_json": bool(manifest is not None),
            "calibration_package_json": bool(calibration is not None),
            "trade_log_csv": bool(trade_log_path.exists()),
        },
    }


def audit_registry_run_id_alignment(*, project_root: Path, registry_path: Path) -> dict[str, Any]:
    root = project_root.resolve()
    resolved_registry = _resolve_project_path(root, registry_path)
    registry_result = read_approved_package_registry(project_root=root, registry_path=resolved_registry)
    if registry_result.get("status") != "PASS":
        return {
            "status": "FAIL",
            "reason": "registry_reader_failed",
            "registry_path": _project_relative(root, resolved_registry),
            "packages_total": 0,
            "failed_packages": [],
            "registry_reader": registry_result,
        }

    packages = registry_result.get("packages")
    packages = packages if isinstance(packages, list) else []
    if not packages:
        return {
            "status": "PASS",
            "reason": "NO_APPROVED_PACKAGES",
            "registry_path": _project_relative(root, resolved_registry),
            "packages_total": 0,
            "failed_packages": [],
            "package_results": [],
            "registry_reader": registry_result,
        }

    package_results: list[dict[str, Any]] = []
    failed_packages: list[dict[str, Any]] = []
    for package in packages:
        if not isinstance(package, dict):
            failed_packages.append({"run_id": "", "errors": ["invalid_package:not_object"]})
            continue
        result = audit_package_run_id_alignment(
            project_root=root,
            package_path=_resolve_project_path(root, package.get("package_path")),
        )
        package_results.append(result)
        if result.get("status") != "PASS":
            failed_packages.append(
                {
                    "run_id": str(package.get("run_id") or ""),
                    "package_path": result.get("package_path", ""),
                    "errors": result.get("errors", []),
                }
            )

    return {
        "status": "PASS" if not failed_packages else "FAIL",
        "reason": "OK" if not failed_packages else "RUN_ID_ALIGNMENT_FAIL",
        "registry_path": _project_relative(root, resolved_registry),
        "packages_total": int(len(packages)),
        "failed_packages": failed_packages,
        "package_results": package_results,
        "registry_reader": registry_result,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit run_id alignment between manifest, calibration_package, and trade_log.")
    parser.add_argument("--registry-path", default="configs/ml_approved_calibration_packages.yaml")
    parser.add_argument("--package-path", default=None, help="Optional direct package path to audit instead of approved registry.")
    parser.add_argument("--out-dir", default="reports/qa_gate")
    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parents[2]
    if args.package_path:
        result = audit_package_run_id_alignment(project_root=project_root, package_path=Path(args.package_path))
    else:
        result = audit_registry_run_id_alignment(project_root=project_root, registry_path=Path(args.registry_path))

    out_dir = _resolve_project_path(project_root, args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"ml_alignment_run_id_audit_{_utc_tag()}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": result["status"],
                "reason": result.get("reason", "OK" if result["status"] == "PASS" else "RUN_ID_ALIGNMENT_FAIL"),
                "report_path": str(out_path),
                "packages_total": result.get("packages_total", 1),
                "failed_packages": len(result.get("failed_packages", [])) if isinstance(result.get("failed_packages"), list) else 0,
            },
            ensure_ascii=False,
        )
    )
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
