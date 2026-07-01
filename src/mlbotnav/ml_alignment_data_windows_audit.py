from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.ml_approved_package_registry_reader import read_approved_package_registry


DATA_WINDOW_FIELDS = ("data_layer", "train_start", "train_end", "test_start", "test_end")


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


def _parse_ymd(value: object) -> datetime | None:
    raw = str(value or "").strip()
    try:
        return datetime.strptime(raw, "%Y-%m-%d")
    except Exception:
        return None


def _extract_manifest_window_context(manifest: dict[str, Any]) -> tuple[dict[str, str], list[str]]:
    train_window = manifest.get("train_window")
    test_window = manifest.get("test_window")
    train_window = train_window if isinstance(train_window, dict) else {}
    test_window = test_window if isinstance(test_window, dict) else {}
    values = {
        "data_layer": str(manifest.get("data_layer") or "").strip(),
        "train_start": str(train_window.get("start") or "").strip(),
        "train_end": str(train_window.get("end") or "").strip(),
        "test_start": str(test_window.get("start") or "").strip(),
        "test_end": str(test_window.get("end") or "").strip(),
    }
    errors = [f"empty:manifest.{field}" for field, value in values.items() if not value]
    errors.extend(_validate_window_values(values, prefix="manifest"))
    return values, errors


def _extract_oos_window_context(oos: dict[str, Any]) -> tuple[dict[str, str], list[str]]:
    date_range = oos.get("date_range")
    date_range = date_range if isinstance(date_range, dict) else {}
    values = {
        "data_layer": str(oos.get("data_layer") or "").strip(),
        "train_start": str(date_range.get("start") or oos.get("train_start") or "").strip(),
        "train_end": str(date_range.get("end") or oos.get("train_end") or "").strip(),
        "test_start": str(oos.get("test_day") or oos.get("test_start") or "").strip(),
        "test_end": str(oos.get("test_end_day") or oos.get("test_end") or oos.get("test_day") or "").strip(),
    }
    missing = [field for field, value in values.items() if not value]
    if missing:
        return values, [f"missing_oos_window_fields:{','.join(missing)}"]
    return values, _validate_window_values(values, prefix="oos_report")


def _validate_window_values(values: dict[str, str], *, prefix: str) -> list[str]:
    errors: list[str] = []
    if values.get("data_layer") != "core":
        errors.append(f"invalid:{prefix}.data_layer_not_core")
    train_start = _parse_ymd(values.get("train_start"))
    train_end = _parse_ymd(values.get("train_end"))
    test_start = _parse_ymd(values.get("test_start"))
    test_end = _parse_ymd(values.get("test_end"))
    parsed = {
        "train_start": train_start,
        "train_end": train_end,
        "test_start": test_start,
        "test_end": test_end,
    }
    for field, value in parsed.items():
        if values.get(field) and value is None:
            errors.append(f"invalid_date:{prefix}.{field}")
    if train_start and train_end and train_start > train_end:
        errors.append(f"invalid_window:{prefix}.train_start_gt_train_end")
    if test_start and test_end and test_start > test_end:
        errors.append(f"invalid_window:{prefix}.test_start_gt_test_end")
    return errors


def _read_trade_log_window_context(path: Path) -> tuple[dict[str, list[str]], list[dict[str, Any]]]:
    values: dict[str, list[str]] = {field: [] for field in DATA_WINDOW_FIELDS}
    row_errors: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        missing = [field for field in DATA_WINDOW_FIELDS if field not in fieldnames]
        if missing:
            row_errors.append({"row_index": 0, "errors": [f"missing_column:{field}" for field in missing]})
            return values, row_errors
        row_count = 0
        for row_index, row in enumerate(reader, start=1):
            row_count += 1
            row_context: dict[str, str] = {}
            errors: list[str] = []
            for field in DATA_WINDOW_FIELDS:
                value = str(row.get(field) or "").strip()
                if not value:
                    errors.append(f"empty:{field}")
                else:
                    values[field].append(value)
                    row_context[field] = value
            if not errors:
                errors.extend(_validate_window_values(row_context, prefix="trade_log"))
            if errors:
                row_errors.append({"row_index": row_index, "errors": errors})
    if row_count == 0:
        row_errors.append({"row_index": 0, "errors": ["empty_trade_log:no_rows"]})
    return {field: sorted(set(items)) for field, items in values.items()}, row_errors


def audit_package_data_windows_alignment(*, project_root: Path, package_path: Path) -> dict[str, Any]:
    root = project_root.resolve()
    package_dir = _resolve_project_path(root, package_path)
    manifest_path = package_dir / "manifest.json"
    trade_log_path = package_dir / "trade_log.csv"
    oos_report_path = package_dir / "source_reports" / "oos_report.json"

    errors: list[str] = []
    values: dict[str, Any] = {
        "manifest": {},
        "trade_log": {field: [] for field in DATA_WINDOW_FIELDS},
        "oos_report": {},
    }

    manifest: dict[str, Any] | None = None
    if not manifest_path.exists():
        errors.append("missing_file:manifest.json")
    else:
        try:
            manifest = _load_json(manifest_path)
            context, context_errors = _extract_manifest_window_context(manifest)
            values["manifest"] = context
            errors.extend(context_errors)
        except Exception as exc:
            errors.append(f"invalid_json:manifest.json:{type(exc).__name__}")

    trade_row_errors: list[dict[str, Any]] = []
    if not trade_log_path.exists():
        errors.append("missing_file:trade_log.csv")
    else:
        trade_values, trade_row_errors = _read_trade_log_window_context(trade_log_path)
        values["trade_log"] = trade_values
        if trade_row_errors:
            errors.append("invalid_trade_log_data_window_rows")

    oos_checked = False
    if oos_report_path.exists():
        oos_checked = True
        try:
            oos = _load_json(oos_report_path)
            context, context_errors = _extract_oos_window_context(oos)
            values["oos_report"] = context
            errors.extend(context_errors)
        except Exception as exc:
            errors.append(f"invalid_json:oos_report.json:{type(exc).__name__}")

    expected_context: dict[str, str] = {}
    mismatch_fields: list[dict[str, Any]] = []
    for field in DATA_WINDOW_FIELDS:
        field_values: list[str] = []
        manifest_value = str(values.get("manifest", {}).get(field, "")).strip()
        if manifest_value:
            field_values.append(manifest_value)
        field_values.extend([str(v) for v in values.get("trade_log", {}).get(field, []) if str(v).strip()])
        oos_value = str(values.get("oos_report", {}).get(field, "")).strip()
        if oos_value:
            field_values.append(oos_value)
        unique_values = sorted(set(field_values))
        expected_context[field] = unique_values[0] if len(unique_values) == 1 else ""
        if len(unique_values) > 1:
            mismatch_fields.append({"field": field, "values": unique_values})

    if mismatch_fields:
        errors.append("data_window_mismatch")

    status = "PASS" if not errors else "FAIL"
    return {
        "status": status,
        "package_path": _project_relative(root, package_dir),
        "manifest_path": _project_relative(root, manifest_path),
        "trade_log_path": _project_relative(root, trade_log_path),
        "oos_report_path": _project_relative(root, oos_report_path),
        "oos_report_checked": bool(oos_checked),
        "expected_context": expected_context,
        "values": values,
        "mismatch_fields": mismatch_fields,
        "trade_log_row_errors": trade_row_errors,
        "errors": errors,
        "files_checked": {
            "manifest_json": bool(manifest is not None),
            "trade_log_csv": bool(trade_log_path.exists()),
            "oos_report_json": bool(oos_checked),
        },
    }


def audit_registry_data_windows_alignment(*, project_root: Path, registry_path: Path) -> dict[str, Any]:
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
        result = audit_package_data_windows_alignment(
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
                    "mismatch_fields": result.get("mismatch_fields", []),
                }
            )

    return {
        "status": "PASS" if not failed_packages else "FAIL",
        "reason": "OK" if not failed_packages else "DATA_WINDOWS_ALIGNMENT_FAIL",
        "registry_path": _project_relative(root, resolved_registry),
        "packages_total": int(len(packages)),
        "failed_packages": failed_packages,
        "package_results": package_results,
        "registry_reader": registry_result,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit data window alignment between manifest, trade_log, and optional OOS report.")
    parser.add_argument("--registry-path", default="configs/ml_approved_calibration_packages.yaml")
    parser.add_argument("--package-path", default=None, help="Optional direct package path to audit instead of approved registry.")
    parser.add_argument("--out-dir", default="reports/qa_gate")
    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parents[2]
    if args.package_path:
        result = audit_package_data_windows_alignment(project_root=project_root, package_path=Path(args.package_path))
    else:
        result = audit_registry_data_windows_alignment(project_root=project_root, registry_path=Path(args.registry_path))

    out_dir = _resolve_project_path(project_root, args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"ml_alignment_data_windows_audit_{_utc_tag()}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": result["status"],
                "reason": result.get("reason", "OK" if result["status"] == "PASS" else "DATA_WINDOWS_ALIGNMENT_FAIL"),
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
