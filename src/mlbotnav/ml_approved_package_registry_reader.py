from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from mlbotnav.ml_approval_registry_validator import validate_approval_registry
from mlbotnav.ml_ingest_source_policy import classify_ml_ingest_source_path


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"registry root must be an object: {path}")
    return data


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


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


def read_approved_package_registry(*, project_root: Path, registry_path: Path) -> dict[str, Any]:
    root = project_root.resolve()
    resolved_registry = _resolve_project_path(root, registry_path)
    registry_policy = classify_ml_ingest_source_path(project_root=root, source_path=resolved_registry)
    if registry_policy["status"] != "ALLOW":
        return {
            "status": "FAIL",
            "registry_path": str(resolved_registry),
            "approved_count": 0,
            "packages": [],
            "failures": [{"scope": "registry_source", "errors": [registry_policy["reason"]]}],
            "validator": None,
        }

    validator = validate_approval_registry(project_root=root, registry_path=resolved_registry)
    if validator.get("status") != "PASS":
        return {
            "status": "FAIL",
            "registry_path": str(resolved_registry),
            "approved_count": int(validator.get("approved_count", 0)),
            "packages": [],
            "failures": validator.get("failures", []),
            "validator": validator,
        }

    registry = _load_yaml(resolved_registry)
    approved_entries = registry.get("approved_packages")
    approved_entries = approved_entries if isinstance(approved_entries, list) else []

    packages: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for index, entry in enumerate(approved_entries):
        if not isinstance(entry, dict):
            failures.append({"index": index, "run_id": "", "errors": ["invalid_entry:not_object"]})
            continue

        package_dir = _resolve_project_path(root, entry.get("package_path"))
        package_policy = classify_ml_ingest_source_path(project_root=root, source_path=package_dir)
        if package_policy["status"] != "ALLOW":
            failures.append(
                {
                    "index": index,
                    "run_id": str(entry.get("run_id") or ""),
                    "errors": [package_policy["reason"]],
                }
            )
            continue

        manifest_path = package_dir / "manifest.json"
        manifest = _load_json(manifest_path)
        packages.append(
            {
                "run_id": str(entry.get("run_id") or ""),
                "status": str(entry.get("status") or ""),
                "package_path": _project_relative(root, package_dir),
                "manifest_path": _project_relative(root, manifest_path),
                "trade_log_path": _project_relative(root, package_dir / "trade_log.csv"),
                "audit_path": _project_relative(root, package_dir / "audit.md"),
                "approved_by": str(entry.get("approved_by") or ""),
                "approved_utc": str(entry.get("approved_utc") or ""),
                "comment": str(entry.get("comment") or ""),
                "symbol": str(manifest.get("symbol") or ""),
                "timeframe": str(manifest.get("timeframe") or ""),
                "data_layer": str(manifest.get("data_layer") or ""),
                "block_id": str(manifest.get("block_id") or ""),
                "passport_id": str(manifest.get("passport_id") or ""),
                "action_id": str(manifest.get("action_id") or ""),
            }
        )

    return {
        "status": "PASS" if not failures else "FAIL",
        "registry_path": str(resolved_registry),
        "approved_count": len(packages),
        "packages": packages,
        "failures": failures,
        "validator": validator,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read approved ML calibration package registry.")
    parser.add_argument("--registry-path", default="configs/ml_approved_calibration_packages.yaml")
    parser.add_argument("--out-dir", default="reports/qa_gate")
    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parents[2]
    registry_path = _resolve_project_path(project_root, args.registry_path)
    result = read_approved_package_registry(project_root=project_root, registry_path=registry_path)

    out_dir = _resolve_project_path(project_root, args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"ml_approved_package_registry_reader_{_utc_tag()}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": result["status"],
                "report_path": str(out_path),
                "approved_count": result["approved_count"],
                "failures": len(result["failures"]),
            },
            ensure_ascii=False,
        )
    )
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
