from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml


REQUIRED_FIELDS = (
    "schema_version",
    "wbs_item",
    "manifest_status",
    "symbol",
    "timeframe",
    "data_layer",
    "train_window",
    "test_window",
    "data_root",
    "expected_file_name",
    "forbidden_dates",
    "forbidden_data_layers",
    "stage_8_boundaries",
    "next_wbs_item",
)

EXPECTED_TRAIN = ("2026-05-11", "2026-05-24")
EXPECTED_TEST = ("2026-05-25", "2026-05-31")
EXPECTED_WBS = "8.1"
EXPECTED_STATUS = "LARGE_CLEAN_WINDOW_FIXED"
EXPECTED_NEXT = "8.2 Run Optuna calibration"


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
        raise ValueError(f"manifest root must be an object: {path}")
    return data


def _parse_ymd(value: object) -> datetime | None:
    try:
        return datetime.strptime(str(value or "").strip(), "%Y-%m-%d")
    except Exception:
        return None


def _date_range(start: datetime, end: datetime) -> list[str]:
    days: list[str] = []
    current = start
    while current <= end:
        days.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return days


def _window_values(manifest: dict[str, Any], key: str) -> tuple[str, str]:
    raw_window = manifest.get(key)
    window = raw_window if isinstance(raw_window, dict) else {}
    return str(window.get("start") or "").strip(), str(window.get("end") or "").strip()


def audit_large_clean_window_manifest(*, project_root: Path, manifest_path: Path) -> dict[str, Any]:
    root = project_root.resolve()
    resolved_manifest = _resolve_project_path(root, manifest_path)
    errors: list[str] = []
    checked_files: list[str] = []
    missing_files: list[str] = []
    train_dates: list[str] = []
    test_dates: list[str] = []

    try:
        manifest = _load_yaml(resolved_manifest)
    except Exception as exc:
        return {
            "status": "FAIL",
            "reason": "invalid_manifest",
            "manifest_path": _project_relative(root, resolved_manifest),
            "errors": [f"invalid_yaml:{type(exc).__name__}"],
            "train_dates": [],
            "test_dates": [],
            "checked_files": [],
            "missing_files": [],
        }

    for field in REQUIRED_FIELDS:
        if field not in manifest:
            errors.append(f"missing_field:{field}")

    if str(manifest.get("wbs_item") or "").strip() != EXPECTED_WBS:
        errors.append("invalid_wbs_item:not_8.1")
    if str(manifest.get("manifest_status") or "").strip() != EXPECTED_STATUS:
        errors.append("invalid_manifest_status")
    if str(manifest.get("next_wbs_item") or "").strip() != EXPECTED_NEXT:
        errors.append("invalid_next_wbs_item")
    if str(manifest.get("data_layer") or "").strip() != "core":
        errors.append("invalid_data_layer:not_core")

    forbidden_layers = {str(v).strip() for v in manifest.get("forbidden_data_layers", []) if str(v).strip()}
    data_layer = str(manifest.get("data_layer") or "").strip()
    if data_layer in forbidden_layers:
        errors.append(f"forbidden_data_layer:{data_layer}")

    train_start_raw, train_end_raw = _window_values(manifest, "train_window")
    test_start_raw, test_end_raw = _window_values(manifest, "test_window")
    if (train_start_raw, train_end_raw) != EXPECTED_TRAIN:
        errors.append("invalid_train_window:not_stage_8_large_clean")
    if (test_start_raw, test_end_raw) != EXPECTED_TEST:
        errors.append("invalid_test_window:not_stage_8_large_clean")

    parsed = {
        "train_start": _parse_ymd(train_start_raw),
        "train_end": _parse_ymd(train_end_raw),
        "test_start": _parse_ymd(test_start_raw),
        "test_end": _parse_ymd(test_end_raw),
    }
    for field, value in parsed.items():
        if value is None:
            errors.append(f"invalid_date:{field}")

    if parsed["train_start"] and parsed["train_end"] and parsed["train_start"] > parsed["train_end"]:
        errors.append("invalid_window:train_start_gt_train_end")
    if parsed["test_start"] and parsed["test_end"] and parsed["test_start"] > parsed["test_end"]:
        errors.append("invalid_window:test_start_gt_test_end")
    if parsed["train_end"] and parsed["test_start"] and parsed["train_end"] >= parsed["test_start"]:
        errors.append("invalid_window:train_must_end_before_test")

    if all(parsed.values()):
        train_dates = _date_range(parsed["train_start"], parsed["train_end"])  # type: ignore[arg-type]
        test_dates = _date_range(parsed["test_start"], parsed["test_end"])  # type: ignore[arg-type]
        selected_dates = train_dates + test_dates
        forbidden_dates = {str(v).strip() for v in manifest.get("forbidden_dates", []) if str(v).strip()}
        for day in sorted(set(selected_dates).intersection(forbidden_dates)):
            errors.append(f"forbidden_date:{day}")
        if len(train_dates) != 14:
            errors.append("invalid_train_day_count:not_14")
        if len(test_dates) != 7:
            errors.append("invalid_test_day_count:not_7")
    else:
        selected_dates = []

    boundaries = manifest.get("stage_8_boundaries")
    boundaries = boundaries if isinstance(boundaries, dict) else {}
    for key in (
        "optuna_calibration_started",
        "package_created",
        "package_approved_for_ml",
        "ml_ingest_started",
        "ml_training_started",
    ):
        if boundaries.get(key) is not False:
            errors.append(f"invalid_boundary:{key}_must_be_false")

    symbol = str(manifest.get("symbol") or "").strip()
    timeframe = str(manifest.get("timeframe") or "").strip()
    data_root = _resolve_project_path(root, manifest.get("data_root"))
    expected_file = str(manifest.get("expected_file_name") or "").strip() or "part-final.csv"
    for day in selected_dates:
        path = data_root / f"dt={day}" / f"tf={timeframe}" / f"symbol={symbol}" / expected_file
        checked_files.append(_project_relative(root, path))
        if not path.exists():
            missing_files.append(_project_relative(root, path))
    if missing_files:
        errors.append("missing_core_ohlcv_files")

    return {
        "status": "PASS" if not errors else "FAIL",
        "reason": "OK" if not errors else "LARGE_CLEAN_WINDOW_MANIFEST_FAIL",
        "manifest_path": _project_relative(root, resolved_manifest),
        "wbs_item": str(manifest.get("wbs_item") or ""),
        "symbol": symbol,
        "timeframe": timeframe,
        "data_layer": data_layer,
        "train_window": {"start": train_start_raw, "end": train_end_raw},
        "test_window": {"start": test_start_raw, "end": test_end_raw},
        "train_dates": train_dates,
        "test_dates": test_dates,
        "selected_dates": selected_dates,
        "checked_files": checked_files,
        "missing_files": missing_files,
        "errors": errors,
        "boundary": {key: bool(boundaries.get(key)) for key in (
            "optuna_calibration_started",
            "package_created",
            "package_approved_for_ml",
            "ml_ingest_started",
            "ml_training_started",
        )},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Stage 8.1 large clean window manifest.")
    parser.add_argument("--manifest-path", default="configs/ml_large_clean_window_manifest.yaml")
    parser.add_argument("--out-dir", default="reports/qa_gate")
    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parents[2]
    result = audit_large_clean_window_manifest(project_root=project_root, manifest_path=Path(args.manifest_path))

    out_dir = _resolve_project_path(project_root, args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"ml_large_clean_window_manifest_audit_{_utc_tag()}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": result["status"],
                "reason": result["reason"],
                "report_path": str(out_path),
                "train_days": len(result.get("train_dates", [])),
                "test_days": len(result.get("test_dates", [])),
                "missing_files": len(result.get("missing_files", [])),
                "errors": len(result.get("errors", [])),
            },
            ensure_ascii=False,
        )
    )
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
