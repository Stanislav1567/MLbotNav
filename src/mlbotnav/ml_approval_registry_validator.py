from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from mlbotnav.ml_trade_dataset_contract import validate_trade_dataset_csv


REQUIRED_MANIFEST_FIELDS = (
    "run_id",
    "created_utc",
    "symbol",
    "timeframe",
    "data_layer",
    "train_window",
    "test_window",
    "block_id",
    "passport_id",
    "action_id",
    "source_reports",
    "status",
)


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


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
        return project_root / "__missing_path__"
    path = Path(value)
    if not path.is_absolute():
        path = project_root / path
    return path.resolve()


def _entry_failure(index: int, run_id: str, errors: list[str]) -> dict[str, Any]:
    return {"index": index, "run_id": run_id, "errors": errors}


def validate_approval_registry(*, project_root: Path, registry_path: Path) -> dict[str, Any]:
    root = project_root.resolve()
    registry = _load_yaml(registry_path.resolve())
    approved_packages = registry.get("approved_packages")
    if not isinstance(approved_packages, list):
        return {
            "status": "FAIL",
            "deny_result": str(registry.get("deny_result") or "ML_ADMISSION_DENY"),
            "registry_path": str(registry_path),
            "approved_count": 0,
            "failures": [_entry_failure(-1, "", ["invalid_registry:approved_packages_not_list"])],
        }

    bans = registry.get("approval_bans")
    bans = bans if isinstance(bans, dict) else {}
    forbidden_statuses = {str(v) for v in bans.get("forbidden_statuses", [])}
    forbidden_layers = {str(v) for v in bans.get("forbid_clean_input_data_layers", [])}
    required_package_files = [str(v) for v in bans.get("forbid_missing_package_files", [])]

    failures: list[dict[str, Any]] = []
    for index, entry in enumerate(approved_packages):
        errors: list[str] = []
        if not isinstance(entry, dict):
            failures.append(_entry_failure(index, "", ["invalid_entry:not_object"]))
            continue

        run_id = str(entry.get("run_id") or "").strip()
        status = str(entry.get("status") or "").strip()
        package_path = _resolve_project_path(root, entry.get("package_path"))

        if not run_id:
            errors.append("missing:run_id")
        if status != "APPROVED_FOR_ML":
            errors.append("invalid_status:not_approved_for_ml")
        if status in forbidden_statuses:
            errors.append(f"forbidden_status:{status}")
        for key in ("approved_by", "approved_utc", "comment"):
            if not str(entry.get(key) or "").strip():
                errors.append(f"missing_manual_metadata:{key}")

        expected_root = (root / "reports" / "ml_candidates").resolve()
        if expected_root not in package_path.parents:
            errors.append("invalid_path:not_under_ml_candidates")
        if not package_path.exists():
            errors.append("missing:package_path")

        for rel_file in required_package_files:
            if not (package_path / rel_file).exists():
                errors.append(f"missing_package_file:{rel_file}")

        manifest_path = package_path / "manifest.json"
        manifest: dict[str, Any] | None = None
        if manifest_path.exists():
            try:
                manifest = _load_json(manifest_path)
                missing_manifest = [key for key in REQUIRED_MANIFEST_FIELDS if not manifest.get(key)]
                errors.extend(f"missing_manifest_field:{key}" for key in missing_manifest)
                if run_id and str(manifest.get("run_id") or "").strip() != run_id:
                    errors.append("manifest_run_id_mismatch")
                data_layer = str(manifest.get("data_layer") or "").strip()
                if data_layer in forbidden_layers:
                    errors.append(f"forbidden_data_layer:{data_layer}")
            except Exception as exc:
                errors.append(f"invalid_json:manifest:{type(exc).__name__}")

        trade_log_path = package_path / "trade_log.csv"
        contract_result = validate_trade_dataset_csv(trade_log_path, approved_mode=True)
        if contract_result.get("status") != "PASS":
            errors.append("contract_audit_not_pass")

        if errors:
            failures.append(_entry_failure(index, run_id, errors))

    return {
        "status": "PASS" if not failures else "FAIL",
        "deny_result": str(registry.get("deny_result") or "ML_ADMISSION_DENY"),
        "registry_path": str(registry_path),
        "approved_count": len(approved_packages),
        "failures": failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate manual ML approval registry.")
    parser.add_argument("--registry-path", default="configs/ml_approved_calibration_packages.yaml")
    parser.add_argument("--out-dir", default="reports/qa_gate")
    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parents[2]
    registry_path = _resolve_project_path(project_root, args.registry_path)
    result = validate_approval_registry(project_root=project_root, registry_path=registry_path)

    out_dir = _resolve_project_path(project_root, args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"ml_approval_registry_validator_{_utc_tag()}.json"
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
