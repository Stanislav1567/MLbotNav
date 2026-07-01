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


def _canonical_json_object(value: object) -> tuple[str, dict[str, Any] | None, str]:
    if not isinstance(value, dict):
        return "", None, "not_object"
    if not value:
        return "", None, "empty_object"
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")), value, ""


def _parse_calibration_params_json(raw: object) -> tuple[str, dict[str, Any] | None, str]:
    try:
        parsed = json.loads(str(raw or "").strip())
    except Exception:
        return "", None, "invalid_json"
    canonical, payload, error = _canonical_json_object(parsed)
    return canonical, payload, error


def _read_trade_log_calibration_params(path: Path) -> tuple[list[str], list[dict[str, Any]], list[dict[str, Any]]]:
    canonical_values: list[str] = []
    parsed_values: list[dict[str, Any]] = []
    row_errors: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        if "calibration_params_json" not in fieldnames:
            row_errors.append({"row_index": 0, "errors": ["missing_column:calibration_params_json"]})
            return canonical_values, parsed_values, row_errors
        row_count = 0
        for row_index, row in enumerate(reader, start=1):
            row_count += 1
            canonical, payload, error = _parse_calibration_params_json(row.get("calibration_params_json"))
            if error:
                row_errors.append({"row_index": row_index, "errors": [f"invalid:calibration_params_json:{error}"]})
                continue
            canonical_values.append(canonical)
            if payload is not None:
                parsed_values.append(payload)
    if row_count == 0:
        row_errors.append({"row_index": 0, "errors": ["empty_trade_log:no_rows"]})
    return sorted(set(canonical_values)), parsed_values, row_errors


def _read_optional_oos_params(path: Path) -> tuple[str, dict[str, Any] | None, list[str], bool]:
    if not path.exists():
        return "", None, [], False
    try:
        oos = _load_json(path)
    except Exception as exc:
        return "", None, [f"invalid_json:oos_report.json:{type(exc).__name__}"], True
    canonical, payload, error = _canonical_json_object(oos.get("calibration_params"))
    if error:
        return "", None, [f"invalid:oos_report.calibration_params:{error}"], True
    return canonical, payload, [], True


def audit_package_calibration_params_alignment(*, project_root: Path, package_path: Path) -> dict[str, Any]:
    root = project_root.resolve()
    package_dir = _resolve_project_path(root, package_path)
    calibration_path = package_dir / "calibration_package.json"
    trade_log_path = package_dir / "trade_log.csv"
    oos_report_path = package_dir / "source_reports" / "oos_report.json"

    errors: list[str] = []
    values: dict[str, Any] = {
        "calibration_package": {},
        "trade_log": [],
        "oos_report": {},
    }
    canonical_sources: dict[str, list[str]] = {
        "calibration_package": [],
        "trade_log": [],
        "oos_report": [],
    }

    calibration: dict[str, Any] | None = None
    if not calibration_path.exists():
        errors.append("missing_file:calibration_package.json")
    else:
        try:
            calibration = _load_json(calibration_path)
            canonical, payload, error = _canonical_json_object(calibration.get("calibration_params"))
            if error:
                errors.append(f"invalid:calibration_package.calibration_params:{error}")
            else:
                canonical_sources["calibration_package"].append(canonical)
                values["calibration_package"] = payload or {}
        except Exception as exc:
            errors.append(f"invalid_json:calibration_package.json:{type(exc).__name__}")

    trade_row_errors: list[dict[str, Any]] = []
    if not trade_log_path.exists():
        errors.append("missing_file:trade_log.csv")
    else:
        trade_canonical, trade_payloads, trade_row_errors = _read_trade_log_calibration_params(trade_log_path)
        canonical_sources["trade_log"] = trade_canonical
        values["trade_log"] = trade_payloads
        if trade_row_errors:
            errors.append("invalid_trade_log_calibration_params_rows")

    oos_errors: list[str] = []
    oos_checked = False
    oos_canonical, oos_payload, oos_errors, oos_checked = _read_optional_oos_params(oos_report_path)
    if oos_errors:
        errors.extend(oos_errors)
    if oos_canonical:
        canonical_sources["oos_report"].append(oos_canonical)
        values["oos_report"] = oos_payload or {}

    all_canonical_values: list[str] = []
    for source_values in canonical_sources.values():
        all_canonical_values.extend([v for v in source_values if v])
    unique_values = sorted(set(all_canonical_values))
    if len(unique_values) > 1:
        errors.append("calibration_params_mismatch")

    status = "PASS" if not errors else "FAIL"
    return {
        "status": status,
        "package_path": _project_relative(root, package_dir),
        "calibration_package_path": _project_relative(root, calibration_path),
        "trade_log_path": _project_relative(root, trade_log_path),
        "oos_report_path": _project_relative(root, oos_report_path),
        "oos_report_checked": bool(oos_checked),
        "expected_calibration_params_json": unique_values[0] if len(unique_values) == 1 else "",
        "canonical_sources": canonical_sources,
        "values": values,
        "trade_log_row_errors": trade_row_errors,
        "errors": errors,
        "files_checked": {
            "calibration_package_json": bool(calibration is not None),
            "trade_log_csv": bool(trade_log_path.exists()),
            "oos_report_json": bool(oos_checked),
        },
    }


def audit_registry_calibration_params_alignment(*, project_root: Path, registry_path: Path) -> dict[str, Any]:
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
        result = audit_package_calibration_params_alignment(
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
        "reason": "OK" if not failed_packages else "CALIBRATION_PARAMS_ALIGNMENT_FAIL",
        "registry_path": _project_relative(root, resolved_registry),
        "packages_total": int(len(packages)),
        "failed_packages": failed_packages,
        "package_results": package_results,
        "registry_reader": registry_result,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit calibration params alignment between calibration_package, trade_log, and optional OOS report."
    )
    parser.add_argument("--registry-path", default="configs/ml_approved_calibration_packages.yaml")
    parser.add_argument("--package-path", default=None, help="Optional direct package path to audit instead of approved registry.")
    parser.add_argument("--out-dir", default="reports/qa_gate")
    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parents[2]
    if args.package_path:
        result = audit_package_calibration_params_alignment(project_root=project_root, package_path=Path(args.package_path))
    else:
        result = audit_registry_calibration_params_alignment(project_root=project_root, registry_path=Path(args.registry_path))

    out_dir = _resolve_project_path(project_root, args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"ml_alignment_calibration_params_audit_{_utc_tag()}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": result["status"],
                "reason": result.get("reason", "OK" if result["status"] == "PASS" else "CALIBRATION_PARAMS_ALIGNMENT_FAIL"),
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
