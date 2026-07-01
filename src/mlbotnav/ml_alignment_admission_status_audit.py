from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from mlbotnav.ml_approval_registry_validator import validate_approval_registry
from mlbotnav.ml_ingest_source_policy import classify_ml_ingest_source_path


APPROVED_STATUS = "APPROVED_FOR_ML"
APPROVED_AUDIT_DECISION = "GO_FOR_ML"


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


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be an object: {path}")
    return data


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def _audit_decision_from_text(text: str) -> str:
    if f"ML decision: `{APPROVED_AUDIT_DECISION}`" in text or f"ML decision: {APPROVED_AUDIT_DECISION}" in text:
        return APPROVED_AUDIT_DECISION
    if "ML decision: `NO_GO_FOR_ML`" in text or "ML decision: NO_GO_FOR_ML" in text:
        return "NO_GO_FOR_ML"
    return ""


def audit_registry_admission_status(*, project_root: Path, registry_path: Path) -> dict[str, Any]:
    root = project_root.resolve()
    resolved_registry = _resolve_project_path(root, registry_path)
    registry_policy = classify_ml_ingest_source_path(project_root=root, source_path=resolved_registry)
    if registry_policy.get("status") != "ALLOW":
        return {
            "status": "FAIL",
            "reason": "registry_source_denied",
            "registry_path": _project_relative(root, resolved_registry),
            "packages_total": 0,
            "failed_packages": [{"run_id": "", "errors": [str(registry_policy.get("reason") or "")]}],
            "package_results": [],
        }

    registry: dict[str, Any]
    try:
        registry = _load_yaml(resolved_registry)
    except Exception as exc:
        return {
            "status": "FAIL",
            "reason": "registry_load_failed",
            "registry_path": _project_relative(root, resolved_registry),
            "packages_total": 0,
            "failed_packages": [{"run_id": "", "errors": [f"invalid_registry:{type(exc).__name__}"]}],
            "package_results": [],
        }

    validator = validate_approval_registry(project_root=root, registry_path=resolved_registry)
    approved_entries = registry.get("approved_packages")
    approved_entries = approved_entries if isinstance(approved_entries, list) else []
    if not approved_entries:
        return {
            "status": "PASS",
            "reason": "NO_APPROVED_PACKAGES",
            "registry_path": _project_relative(root, resolved_registry),
            "registry_status": str(registry.get("registry_status") or ""),
            "packages_total": 0,
            "failed_packages": [],
            "package_results": [],
            "validator": validator,
        }

    package_results: list[dict[str, Any]] = []
    failed_packages: list[dict[str, Any]] = []
    for index, entry in enumerate(approved_entries):
        if not isinstance(entry, dict):
            failure = {"index": index, "run_id": "", "errors": ["invalid_entry:not_object"]}
            failed_packages.append(failure)
            package_results.append({**failure, "status": "FAIL"})
            continue

        run_id = str(entry.get("run_id") or "").strip()
        registry_entry_status = str(entry.get("status") or "").strip()
        package_dir = _resolve_project_path(root, entry.get("package_path"))
        manifest_path = package_dir / "manifest.json"
        calibration_path = package_dir / "calibration_package.json"
        audit_path = package_dir / "audit.md"

        errors: list[str] = []
        values: dict[str, str] = {
            "registry_entry_status": registry_entry_status,
            "manifest_status": "",
            "calibration_package_status": "",
            "audit_decision": "",
        }

        if registry_entry_status != APPROVED_STATUS:
            errors.append("registry_status_not_approved_for_ml")

        package_policy = classify_ml_ingest_source_path(project_root=root, source_path=package_dir)
        if package_policy.get("status") != "ALLOW":
            errors.append(str(package_policy.get("reason") or "package_source_denied"))

        if not manifest_path.exists():
            errors.append("missing_file:manifest.json")
        else:
            try:
                manifest = _load_json(manifest_path)
                values["manifest_status"] = str(manifest.get("status") or "").strip()
                if values["manifest_status"] != APPROVED_STATUS:
                    errors.append("manifest_status_not_approved_for_ml")
            except Exception as exc:
                errors.append(f"invalid_json:manifest.json:{type(exc).__name__}")

        if not calibration_path.exists():
            errors.append("missing_file:calibration_package.json")
        else:
            try:
                calibration = _load_json(calibration_path)
                values["calibration_package_status"] = str(calibration.get("status") or "").strip()
                if values["calibration_package_status"] != APPROVED_STATUS:
                    errors.append("calibration_package_status_not_approved_for_ml")
            except Exception as exc:
                errors.append(f"invalid_json:calibration_package.json:{type(exc).__name__}")

        if not audit_path.exists():
            errors.append("missing_file:audit.md")
        else:
            try:
                values["audit_decision"] = _audit_decision_from_text(audit_path.read_text(encoding="utf-8"))
                if values["audit_decision"] != APPROVED_AUDIT_DECISION:
                    errors.append("audit_decision_not_go_for_ml")
            except Exception as exc:
                errors.append(f"invalid_text:audit.md:{type(exc).__name__}")

        result = {
            "status": "PASS" if not errors else "FAIL",
            "index": index,
            "run_id": run_id,
            "package_path": _project_relative(root, package_dir),
            "manifest_path": _project_relative(root, manifest_path),
            "calibration_package_path": _project_relative(root, calibration_path),
            "audit_path": _project_relative(root, audit_path),
            "values": values,
            "errors": errors,
        }
        package_results.append(result)
        if errors:
            failed_packages.append(
                {
                    "index": index,
                    "run_id": run_id,
                    "package_path": result["package_path"],
                    "errors": errors,
                }
            )

    validator_failures = validator.get("failures")
    validator_failures = validator_failures if isinstance(validator_failures, list) else []
    if validator.get("status") != "PASS":
        failed_packages.append(
            {
                "index": -1,
                "run_id": "",
                "package_path": "",
                "errors": ["approval_registry_validator_failed"],
                "validator_failures": validator_failures,
            }
        )

    return {
        "status": "PASS" if not failed_packages else "FAIL",
        "reason": "OK" if not failed_packages else "ADMISSION_STATUS_FAIL",
        "registry_path": _project_relative(root, resolved_registry),
        "registry_status": str(registry.get("registry_status") or ""),
        "packages_total": int(len(approved_entries)),
        "failed_packages": failed_packages,
        "package_results": package_results,
        "validator": validator,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit ML admission statuses across registry, package JSON, and audit.md.")
    parser.add_argument("--registry-path", default="configs/ml_approved_calibration_packages.yaml")
    parser.add_argument("--out-dir", default="reports/qa_gate")
    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parents[2]
    result = audit_registry_admission_status(project_root=project_root, registry_path=Path(args.registry_path))

    out_dir = _resolve_project_path(project_root, args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"ml_alignment_admission_status_audit_{_utc_tag()}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": result["status"],
                "reason": result.get("reason", "OK" if result["status"] == "PASS" else "ADMISSION_STATUS_FAIL"),
                "report_path": str(out_path),
                "packages_total": result.get("packages_total", 0),
                "failed_packages": len(result.get("failed_packages", [])) if isinstance(result.get("failed_packages"), list) else 0,
            },
            ensure_ascii=False,
        )
    )
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
