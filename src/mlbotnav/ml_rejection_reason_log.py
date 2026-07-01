from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from mlbotnav.ml_approval_registry_validator import REQUIRED_MANIFEST_FIELDS, validate_approval_registry
from mlbotnav.ml_trade_dataset_contract import validate_trade_dataset_csv


REJECTION_CATEGORY_DESCRIPTIONS = {
    "missing_required_columns": "trade_log.csv is missing required ML dataset columns",
    "invalid_manifest": "manifest.json is missing, invalid, or incomplete",
    "not_approved": "registry entry status is not APPROVED_FOR_ML",
    "bad_data_layer": "manifest or trade_log uses a non-core data layer",
    "bad_status": "registry entry uses a forbidden or empty status",
    "missing_package_file": "required package file is missing",
    "missing_manual_metadata": "manual approval metadata is incomplete",
    "invalid_package_path": "package path is missing, outside reports/ml_candidates, or not found",
    "contract_fail": "trade_log.csv failed ML trade dataset contract validation",
    "invalid_registry_entry": "registry entry is not a valid object",
}


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
        raise ValueError(f"registry root must be an object: {path}")
    return data


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def _append_reason(reasons: list[dict[str, Any]], category: str, code: str, detail: Any = None) -> None:
    item: dict[str, Any] = {
        "category": category,
        "code": code,
        "description": REJECTION_CATEGORY_DESCRIPTIONS.get(category, category),
    }
    if detail is not None:
        item["detail"] = detail
    reasons.append(item)


def _status_reasons(entry: dict[str, Any], forbidden_statuses: set[str]) -> list[dict[str, Any]]:
    reasons: list[dict[str, Any]] = []
    status = str(entry.get("status") or "").strip()
    if status != "APPROVED_FOR_ML":
        _append_reason(reasons, "not_approved", "status_not_approved_for_ml", status)
    if not status:
        _append_reason(reasons, "bad_status", "empty_status")
    elif status in forbidden_statuses:
        _append_reason(reasons, "bad_status", "forbidden_status", status)
    return reasons


def _manual_metadata_reasons(entry: dict[str, Any]) -> list[dict[str, Any]]:
    reasons: list[dict[str, Any]] = []
    missing = [key for key in ("approved_by", "approved_utc", "comment") if not str(entry.get(key) or "").strip()]
    if missing:
        _append_reason(reasons, "missing_manual_metadata", "missing_manual_metadata", missing)
    return reasons


def _package_path_reasons(project_root: Path, package_path: Path) -> list[dict[str, Any]]:
    reasons: list[dict[str, Any]] = []
    expected_root = (project_root / "reports" / "ml_candidates").resolve()
    if expected_root not in package_path.parents:
        _append_reason(reasons, "invalid_package_path", "not_under_ml_candidates", _project_relative(project_root, package_path))
    if not package_path.exists():
        _append_reason(reasons, "invalid_package_path", "package_path_missing", _project_relative(project_root, package_path))
    return reasons


def _required_file_reasons(project_root: Path, package_path: Path, required_files: list[str]) -> list[dict[str, Any]]:
    reasons: list[dict[str, Any]] = []
    missing = [rel for rel in required_files if not (package_path / rel).exists()]
    if missing:
        _append_reason(reasons, "missing_package_file", "missing_package_file", missing)
    return reasons


def _manifest_reasons(project_root: Path, package_path: Path, run_id: str, forbidden_layers: set[str]) -> list[dict[str, Any]]:
    reasons: list[dict[str, Any]] = []
    manifest_path = package_path / "manifest.json"
    if not manifest_path.exists():
        _append_reason(reasons, "invalid_manifest", "manifest_missing", _project_relative(project_root, manifest_path))
        return reasons
    try:
        manifest = _load_json(manifest_path)
    except Exception as exc:
        _append_reason(reasons, "invalid_manifest", "manifest_invalid_json", type(exc).__name__)
        return reasons

    missing = [key for key in REQUIRED_MANIFEST_FIELDS if not manifest.get(key)]
    if missing:
        _append_reason(reasons, "invalid_manifest", "missing_manifest_fields", missing)
    if run_id and str(manifest.get("run_id") or "").strip() != run_id:
        _append_reason(
            reasons,
            "invalid_manifest",
            "manifest_run_id_mismatch",
            {"registry_run_id": run_id, "manifest_run_id": str(manifest.get("run_id") or "").strip()},
        )

    data_layer = str(manifest.get("data_layer") or "").strip()
    if data_layer in forbidden_layers or data_layer != "core":
        _append_reason(reasons, "bad_data_layer", "manifest_data_layer_not_core", data_layer)
    return reasons


def _trade_log_reasons(project_root: Path, package_path: Path) -> list[dict[str, Any]]:
    reasons: list[dict[str, Any]] = []
    trade_log_path = package_path / "trade_log.csv"
    contract = validate_trade_dataset_csv(trade_log_path, approved_mode=True)
    if contract.get("status") == "PASS":
        return reasons

    missing_columns = contract.get("missing_columns")
    if isinstance(missing_columns, list) and missing_columns:
        _append_reason(reasons, "missing_required_columns", "missing_required_columns", missing_columns)

    failed_rows = contract.get("failed_rows")
    if isinstance(failed_rows, list):
        for failed in failed_rows:
            if not isinstance(failed, dict):
                continue
            errors = failed.get("errors")
            errors = errors if isinstance(errors, list) else []
            if "invalid:data_layer_not_core" in errors:
                _append_reason(
                    reasons,
                    "bad_data_layer",
                    "trade_log_data_layer_not_core",
                    {"row_index": failed.get("row_index"), "run_id": failed.get("run_id")},
                )
                break

    _append_reason(
        reasons,
        "contract_fail",
        "trade_log_contract_fail",
        {
            "trade_log_path": _project_relative(project_root, trade_log_path),
            "rows_total": contract.get("rows_total", 0),
            "failed_rows": len(contract.get("failed_rows", [])) if isinstance(contract.get("failed_rows"), list) else 0,
        },
    )
    return reasons


def build_rejection_reason_log(
    *,
    project_root: Path,
    registry_path: Path,
    out_dir: Path,
    log_name: str | None = None,
) -> dict[str, Any]:
    root = project_root.resolve()
    resolved_registry = _resolve_project_path(root, registry_path)
    resolved_out_dir = _resolve_project_path(root, out_dir)
    resolved_out_dir.mkdir(parents=True, exist_ok=True)

    registry = _load_yaml(resolved_registry)
    validator = validate_approval_registry(project_root=root, registry_path=resolved_registry)
    bans = registry.get("approval_bans")
    bans = bans if isinstance(bans, dict) else {}
    forbidden_statuses = {str(v) for v in bans.get("forbidden_statuses", [])}
    forbidden_layers = {str(v) for v in bans.get("forbid_clean_input_data_layers", [])}
    required_files = [str(v) for v in bans.get("forbid_missing_package_files", ["manifest.json", "trade_log.csv", "audit.md"])]

    approved_packages = registry.get("approved_packages")
    entries = approved_packages if isinstance(approved_packages, list) else []
    rejections: list[dict[str, Any]] = []

    if not isinstance(approved_packages, list):
        rejections.append(
            {
                "index": -1,
                "run_id": "",
                "package_path": "",
                "reasons": [
                    {
                        "category": "invalid_registry_entry",
                        "code": "approved_packages_not_list",
                        "description": REJECTION_CATEGORY_DESCRIPTIONS["invalid_registry_entry"],
                    }
                ],
            }
        )

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            rejections.append(
                {
                    "index": index,
                    "run_id": "",
                    "package_path": "",
                    "reasons": [
                        {
                            "category": "invalid_registry_entry",
                            "code": "entry_not_object",
                            "description": REJECTION_CATEGORY_DESCRIPTIONS["invalid_registry_entry"],
                        }
                    ],
                }
            )
            continue

        run_id = str(entry.get("run_id") or "").strip()
        package_path = _resolve_project_path(root, entry.get("package_path"))
        reasons: list[dict[str, Any]] = []
        reasons.extend(_status_reasons(entry, forbidden_statuses))
        reasons.extend(_manual_metadata_reasons(entry))
        reasons.extend(_package_path_reasons(root, package_path))
        reasons.extend(_required_file_reasons(root, package_path, required_files))
        reasons.extend(_manifest_reasons(root, package_path, run_id, forbidden_layers))
        reasons.extend(_trade_log_reasons(root, package_path))

        if reasons:
            rejections.append(
                {
                    "index": index,
                    "run_id": run_id,
                    "package_path": _project_relative(root, package_path),
                    "status": str(entry.get("status") or "").strip(),
                    "reasons": reasons,
                }
            )

    reason_counts: dict[str, int] = {}
    for rejection in rejections:
        for reason in rejection.get("reasons", []):
            if not isinstance(reason, dict):
                continue
            category = str(reason.get("category") or "unknown")
            reason_counts[category] = reason_counts.get(category, 0) + 1

    status = "PASS"
    reason = "REJECTIONS_RECORDED" if rejections else "NO_REJECTIONS"
    payload: dict[str, Any] = {
        "status": status,
        "reason": reason,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "registry_path": _project_relative(root, resolved_registry),
        "entries_total": int(len(entries)),
        "rejections_total": int(len(rejections)),
        "reason_counts": reason_counts,
        "rejections": rejections,
        "validator": validator,
        "boundary": {
            "manual_approval_required": True,
            "registry_modified": False,
            "ml_training_started": False,
            "direct_optuna_report_scan": False,
        },
    }

    stem = str(log_name or f"ml_rejection_reasons_{_utc_tag()}").strip() or f"ml_rejection_reasons_{_utc_tag()}"
    log_path = resolved_out_dir / f"{stem}.json"
    log_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    payload["log_path"] = _project_relative(root, log_path)
    log_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write ML admission rejection reason log.")
    parser.add_argument("--registry-path", default="configs/ml_approved_calibration_packages.yaml")
    parser.add_argument("--out-dir", default="reports/ml_rejections")
    parser.add_argument("--log-name", default=None)
    parser.add_argument("--report-dir", default="reports/qa_gate")
    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parents[2]
    result = build_rejection_reason_log(
        project_root=project_root,
        registry_path=Path(args.registry_path),
        out_dir=Path(args.out_dir),
        log_name=args.log_name,
    )

    report_dir = _resolve_project_path(project_root, args.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"ml_rejection_reason_log_{_utc_tag()}.json"
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": result["status"],
                "reason": result["reason"],
                "report_path": str(report_path),
                "log_path": result["log_path"],
                "entries_total": result["entries_total"],
                "rejections_total": result["rejections_total"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
