from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RUN_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]*$")


@dataclass(frozen=True)
class CandidatePackageStructure:
    run_id: str
    package_dir: Path
    created_utc: str
    status: str

    def as_dict(self, project_root: Path) -> dict[str, str]:
        return {
            "run_id": self.run_id,
            "package_dir": str(self.package_dir.relative_to(project_root).as_posix()),
            "created_utc": self.created_utc,
            "status": self.status,
        }


def validate_run_id(run_id: str) -> str:
    value = str(run_id or "").strip()
    if not value:
        raise ValueError("run_id is required")
    if "/" in value or "\\" in value or ".." in value:
        raise ValueError(f"unsafe run_id: {run_id!r}")
    if not RUN_ID_PATTERN.fullmatch(value):
        raise ValueError(f"unsupported run_id characters: {run_id!r}")
    return value


def create_candidate_package_structure(*, project_root: Path, run_id: str) -> CandidatePackageStructure:
    """Create the Stage 3.1 candidate package root directory."""
    root = project_root.resolve()
    safe_run_id = validate_run_id(run_id)
    package_dir = (root / "reports" / "ml_candidates" / safe_run_id).resolve()
    expected_root = (root / "reports" / "ml_candidates").resolve()
    if expected_root not in package_dir.parents:
        raise ValueError(f"package_dir escaped candidate root: {package_dir}")
    package_dir.mkdir(parents=True, exist_ok=True)
    return CandidatePackageStructure(
        run_id=safe_run_id,
        package_dir=package_dir,
        created_utc=datetime.now(timezone.utc).isoformat(),
        status="STRUCTURE_READY",
    )


def _read_first_csv_row(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            return {str(k): str(v if v is not None else "") for k, v in row.items()}
    raise ValueError(f"CSV has no rows: {path}")


def _load_json_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def _project_relative_path(project_root: Path, path: Path) -> str:
    resolved_root = project_root.resolve()
    resolved_path = path.resolve()
    try:
        return resolved_path.relative_to(resolved_root).as_posix()
    except ValueError:
        return str(resolved_path)


def _extract_signal_mode(*, oos_report: dict[str, Any] | None, run_id: str) -> str:
    if oos_report:
        risk = oos_report.get("risk_policy")
        if isinstance(risk, dict) and str(risk.get("signal_mode") or "").strip():
            return str(risk["signal_mode"]).strip()
        backtest = oos_report.get("backtest")
        if isinstance(backtest, dict) and str(backtest.get("signal_mode") or "").strip():
            return str(backtest["signal_mode"]).strip()
    for value in ("long_only", "short_only", "both"):
        if value in run_id:
            return value
    return ""


def create_calibration_package_json(
    *,
    project_root: Path,
    run_id: str,
    trade_csv_path: Path,
    oos_report_path: Path | None = None,
    status: str = "DRAFT",
) -> tuple[Path, dict[str, Any]]:
    """Create Stage 3.2 calibration_package.json from an enriched trade CSV."""
    structure = create_candidate_package_structure(project_root=project_root, run_id=run_id)
    trade_csv = trade_csv_path.resolve()
    if not trade_csv.exists():
        raise FileNotFoundError(f"trade CSV not found: {trade_csv}")

    row = _read_first_csv_row(trade_csv)
    row_run_id = str(row.get("run_id") or "").strip()
    if row_run_id != structure.run_id:
        raise ValueError(f"trade CSV run_id mismatch: expected {structure.run_id}, got {row_run_id}")

    calibration_raw = str(row.get("calibration_params_json") or "").strip()
    calibration_params = json.loads(calibration_raw)
    if not isinstance(calibration_params, dict) or not calibration_params:
        raise ValueError("calibration_params_json must be a non-empty JSON object")

    oos_report = _load_json_file(oos_report_path.resolve()) if oos_report_path else None
    payload: dict[str, Any] = {
        "run_id": structure.run_id,
        "block_id": str(row.get("block_id") or "").strip(),
        "passport_id": str(row.get("passport_id") or "").strip(),
        "action_id": str(row.get("action_id") or "").strip(),
        "calibration_params": calibration_params,
        "signal_mode": _extract_signal_mode(oos_report=oos_report, run_id=structure.run_id),
        "status": str(status or "DRAFT").strip() or "DRAFT",
    }
    for key in ("block_id", "passport_id", "action_id", "signal_mode", "status"):
        if not str(payload.get(key) or "").strip():
            raise ValueError(f"missing required calibration package field: {key}")

    out_path = structure.package_dir / "calibration_package.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return out_path, payload


def copy_trade_log_csv(*, project_root: Path, run_id: str, trade_csv_path: Path) -> Path:
    """Copy the enriched trade CSV into the candidate package as trade_log.csv."""
    structure = create_candidate_package_structure(project_root=project_root, run_id=run_id)
    trade_csv = trade_csv_path.resolve()
    if not trade_csv.exists():
        raise FileNotFoundError(f"trade CSV not found: {trade_csv}")
    row = _read_first_csv_row(trade_csv)
    row_run_id = str(row.get("run_id") or "").strip()
    if row_run_id != structure.run_id:
        raise ValueError(f"trade CSV run_id mismatch: expected {structure.run_id}, got {row_run_id}")

    out_path = structure.package_dir / "trade_log.csv"
    shutil.copy2(trade_csv, out_path)
    return out_path


def copy_source_reports(
    *,
    project_root: Path,
    run_id: str,
    oos_report_path: Path,
    pipeline_report_path: Path,
    optuna_report_path: Path | None = None,
) -> tuple[Path, dict[str, Any]]:
    """Copy Stage 3.4 source reports into the candidate package."""
    structure = create_candidate_package_structure(project_root=project_root, run_id=run_id)
    reports_dir = structure.package_dir / "source_reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_specs: list[tuple[str, Path | None, str, bool]] = [
        ("oos_report", oos_report_path, "oos_report.json", True),
        ("pipeline_report", pipeline_report_path, "pipeline_report.json", True),
        ("optuna_report", optuna_report_path, "optuna_report.json", False),
    ]
    source_reports: dict[str, Any] = {}
    for report_key, source_path, package_name, required in report_specs:
        if source_path is None:
            if required:
                raise ValueError(f"{report_key} path is required")
            source_reports[report_key] = {"status": "NOT_PROVIDED"}
            continue

        source = source_path.resolve()
        if not source.exists():
            raise FileNotFoundError(f"{report_key} not found: {source}")
        _load_json_file(source)

        destination = reports_dir / package_name
        shutil.copy2(source, destination)
        source_reports[report_key] = {
            "status": "COPIED",
            "source_path": _project_relative_path(project_root, source),
            "package_path": _project_relative_path(project_root, destination),
        }

    payload: dict[str, Any] = {
        "run_id": structure.run_id,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_reports": source_reports,
    }
    out_path = structure.package_dir / "source_reports.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return out_path, payload


def create_manifest_json(*, project_root: Path, run_id: str) -> tuple[Path, dict[str, Any]]:
    """Create Stage 3.5 manifest.json from package-local candidate artifacts."""
    structure = create_candidate_package_structure(project_root=project_root, run_id=run_id)
    package_dir = structure.package_dir
    calibration_path = package_dir / "calibration_package.json"
    trade_log_path = package_dir / "trade_log.csv"
    source_reports_path = package_dir / "source_reports.json"

    for path in (calibration_path, trade_log_path, source_reports_path):
        if not path.exists():
            raise FileNotFoundError(f"required package artifact not found: {path}")

    calibration = _load_json_file(calibration_path)
    source_reports_index = _load_json_file(source_reports_path)
    first_trade_row = _read_first_csv_row(trade_log_path)

    for artifact_name, artifact_run_id in (
        ("calibration_package.json", calibration.get("run_id")),
        ("source_reports.json", source_reports_index.get("run_id")),
        ("trade_log.csv", first_trade_row.get("run_id")),
    ):
        if str(artifact_run_id or "").strip() != structure.run_id:
            raise ValueError(f"{artifact_name} run_id mismatch: expected {structure.run_id}, got {artifact_run_id}")

    payload: dict[str, Any] = {
        "run_id": structure.run_id,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": str(first_trade_row.get("symbol") or "").strip(),
        "timeframe": str(first_trade_row.get("timeframe") or "").strip(),
        "data_layer": str(first_trade_row.get("data_layer") or "").strip(),
        "train_window": {
            "start": str(first_trade_row.get("train_start") or "").strip(),
            "end": str(first_trade_row.get("train_end") or "").strip(),
        },
        "test_window": {
            "start": str(first_trade_row.get("test_start") or "").strip(),
            "end": str(first_trade_row.get("test_end") or "").strip(),
        },
        "block_id": str(calibration.get("block_id") or "").strip(),
        "passport_id": str(calibration.get("passport_id") or "").strip(),
        "action_id": str(calibration.get("action_id") or "").strip(),
        "source_reports": source_reports_index.get("source_reports"),
        "status": str(calibration.get("status") or "DRAFT").strip() or "DRAFT",
        "package_files": {
            "calibration_package": _project_relative_path(project_root, calibration_path),
            "trade_log": _project_relative_path(project_root, trade_log_path),
            "source_reports_index": _project_relative_path(project_root, source_reports_path),
        },
    }
    required = (
        "run_id",
        "created_utc",
        "symbol",
        "timeframe",
        "data_layer",
        "block_id",
        "passport_id",
        "action_id",
        "source_reports",
        "status",
    )
    for key in required:
        if not payload.get(key):
            raise ValueError(f"missing required manifest field: {key}")
    for window_name in ("train_window", "test_window"):
        window = payload[window_name]
        if not isinstance(window, dict) or not window.get("start") or not window.get("end"):
            raise ValueError(f"missing required manifest field: {window_name}")

    out_path = package_dir / "manifest.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return out_path, payload


def create_package_audit_md(*, project_root: Path, run_id: str) -> tuple[Path, str]:
    """Create Stage 3.6 package-level audit.md from manifest.json."""
    structure = create_candidate_package_structure(project_root=project_root, run_id=run_id)
    package_dir = structure.package_dir
    manifest_path = package_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"required package artifact not found: {manifest_path}")

    manifest = _load_json_file(manifest_path)
    if str(manifest.get("run_id") or "").strip() != structure.run_id:
        raise ValueError(f"manifest.json run_id mismatch: expected {structure.run_id}, got {manifest.get('run_id')}")

    status = str(manifest.get("status") or "").strip()
    ml_decision = "GO_FOR_ML" if status == "APPROVED_FOR_ML" else "NO_GO_FOR_ML"
    review_state = "READY_FOR_MANUAL_REVIEW" if status == "DRAFT" else status
    reason = (
        "Package is DRAFT and requires manual approval before ML ingest."
        if ml_decision == "NO_GO_FOR_ML"
        else "Package status is APPROVED_FOR_ML."
    )

    package_files = manifest.get("package_files")
    if not isinstance(package_files, dict):
        raise ValueError("manifest package_files must be an object")
    source_reports = manifest.get("source_reports")
    if not isinstance(source_reports, dict):
        raise ValueError("manifest source_reports must be an object")

    artifact_lines = [
        f"- `manifest.json`: `{_project_relative_path(project_root, manifest_path)}`",
    ]
    for key in ("calibration_package", "trade_log", "source_reports_index"):
        if package_files.get(key):
            artifact_lines.append(f"- `{key}`: `{package_files[key]}`")
    for key in sorted(source_reports):
        value = source_reports[key]
        if isinstance(value, dict):
            report_status = str(value.get("status") or "").strip()
            report_path = str(value.get("package_path") or "").strip()
            if report_path:
                artifact_lines.append(f"- `source_report.{key}`: `{report_path}` (`{report_status}`)")
            else:
                artifact_lines.append(f"- `source_report.{key}`: `{report_status}`")

    text = "\n".join(
        [
            "# ML Candidate Package Audit",
            "",
            f"Run ID: `{structure.run_id}`",
            f"Created UTC: `{datetime.now(timezone.utc).isoformat()}`",
            f"Package status: `{status}`",
            f"Review state: `{review_state}`",
            f"ML decision: `{ml_decision}`",
            "",
            "## Summary",
            "",
            (
                f"Candidate package for `{manifest.get('symbol')}` `{manifest.get('timeframe')}` "
                f"`{manifest.get('data_layer')}` using `{manifest.get('block_id')}` / "
                f"`{manifest.get('passport_id')}` / `{manifest.get('action_id')}`."
            ),
            "",
            "## Decision Reason",
            "",
            reason,
            "",
            "## Windows",
            "",
            f"- Train: `{manifest.get('train_window', {}).get('start')}` to `{manifest.get('train_window', {}).get('end')}`",
            f"- Test: `{manifest.get('test_window', {}).get('start')}` to `{manifest.get('test_window', {}).get('end')}`",
            "",
            "## Artifacts",
            "",
            *artifact_lines,
            "",
            "## Boundary",
            "",
            "- This audit does not approve the package for ML.",
            "- ML approval must be done later through the manual approval registry.",
            "",
        ]
    )
    out_path = package_dir / "audit.md"
    out_path.write_text(text, encoding="utf-8")
    return out_path, text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create an ML candidate package directory.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--trade-csv", default=None, help="Enriched trade CSV to create calibration_package.json.")
    parser.add_argument("--oos-report", default=None, help="OOS report JSON used to resolve signal_mode.")
    parser.add_argument("--pipeline-report", default=None, help="Pipeline report JSON to copy into the package.")
    parser.add_argument("--optuna-report", default=None, help="Optional Optuna report JSON to copy into the package.")
    parser.add_argument("--status", default="DRAFT", help="Package status; default is DRAFT.")
    parser.add_argument("--copy-trade-log", action="store_true", help="Copy --trade-csv into package as trade_log.csv.")
    parser.add_argument("--copy-source-reports", action="store_true", help="Copy source reports into package/source_reports.")
    parser.add_argument("--create-manifest", action="store_true", help="Create package manifest.json from local artifacts.")
    parser.add_argument("--create-audit", action="store_true", help="Create package audit.md from manifest.json.")
    args = parser.parse_args(argv)

    project_root = Path(__file__).resolve().parents[2]
    structure = create_candidate_package_structure(project_root=project_root, run_id=args.run_id)
    result: dict[str, Any] = structure.as_dict(project_root)
    if args.trade_csv:
        calibration_path, payload = create_calibration_package_json(
            project_root=project_root,
            run_id=args.run_id,
            trade_csv_path=Path(args.trade_csv),
            oos_report_path=Path(args.oos_report) if args.oos_report else None,
            status=args.status,
        )
        result["calibration_package_path"] = str(calibration_path.relative_to(project_root).as_posix())
        result["calibration_package"] = payload
        if args.copy_trade_log:
            trade_log_path = copy_trade_log_csv(
                project_root=project_root,
                run_id=args.run_id,
                trade_csv_path=Path(args.trade_csv),
            )
            result["trade_log_path"] = str(trade_log_path.relative_to(project_root).as_posix())
    if args.copy_source_reports:
        if not args.oos_report or not args.pipeline_report:
            raise ValueError("--copy-source-reports requires --oos-report and --pipeline-report")
        source_reports_path, source_reports_payload = copy_source_reports(
            project_root=project_root,
            run_id=args.run_id,
            oos_report_path=Path(args.oos_report),
            pipeline_report_path=Path(args.pipeline_report),
            optuna_report_path=Path(args.optuna_report) if args.optuna_report else None,
        )
        result["source_reports_path"] = str(source_reports_path.relative_to(project_root).as_posix())
        result["source_reports"] = source_reports_payload["source_reports"]
    if args.create_manifest:
        manifest_path, manifest_payload = create_manifest_json(project_root=project_root, run_id=args.run_id)
        result["manifest_path"] = str(manifest_path.relative_to(project_root).as_posix())
        result["manifest"] = manifest_payload
    if args.create_audit:
        audit_path, _ = create_package_audit_md(project_root=project_root, run_id=args.run_id)
        result["audit_path"] = str(audit_path.relative_to(project_root).as_posix())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
