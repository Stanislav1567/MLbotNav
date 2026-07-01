from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

import yaml

from mlbotnav.ml_alignment_admission_status_audit import audit_registry_admission_status
from mlbotnav.ml_trade_dataset_contract import REQUIRED_COLUMNS


def _row(run_id: str) -> dict[str, str]:
    return {
        "run_id": run_id,
        "symbol": "SOLUSDT",
        "timeframe": "1m",
        "data_layer": "core",
        "train_start": "2026-05-25",
        "train_end": "2026-05-26",
        "test_start": "2026-05-27",
        "test_end": "2026-05-27",
        "block_id": "B018",
        "passport_id": "F051",
        "action_id": "F051_BOSDOWN_ALLOW",
        "side": "SHORT",
        "calibration_params_json": '{"F051_break_buffer_pct":0.06}',
        "entry_signal_time_utc": "2026-05-27T00:00:00+00:00",
        "entry_time_utc": "2026-05-27T00:01:00+00:00",
        "exit_time_utc": "2026-05-27T00:02:00+00:00",
        "entry_price": "100",
        "exit_price": "98",
        "exit_reason": "tp",
        "net_return": "0.02",
        "net_pnl_usd": "0.2",
        "trade_id": f"{run_id}:T1",
        "bars_in_trade": "1",
        "tp_hit": "true",
        "sl_hit": "false",
        "timeout_hit": "false",
        "mae_pct": "-0.001",
        "mfe_pct": "0.02",
    }


def _write_package(
    root: Path,
    run_id: str,
    *,
    manifest_status: str = "APPROVED_FOR_ML",
    calibration_status: str = "APPROVED_FOR_ML",
    audit_decision: str = "GO_FOR_ML",
) -> Path:
    package_dir = root / "reports" / "ml_candidates" / run_id
    package_dir.mkdir(parents=True, exist_ok=True)
    (package_dir / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "created_utc": "2026-06-23T00:00:00+00:00",
                "symbol": "SOLUSDT",
                "timeframe": "1m",
                "data_layer": "core",
                "train_window": {"start": "2026-05-25", "end": "2026-05-26"},
                "test_window": {"start": "2026-05-27", "end": "2026-05-27"},
                "block_id": "B018",
                "passport_id": "F051",
                "action_id": "F051_BOSDOWN_ALLOW",
                "source_reports": {"oos_report": {"status": "COPIED"}},
                "status": manifest_status,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (package_dir / "calibration_package.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "block_id": "B018",
                "passport_id": "F051",
                "action_id": "F051_BOSDOWN_ALLOW",
                "calibration_params": {"F051_break_buffer_pct": 0.06},
                "signal_mode": "short_only",
                "status": calibration_status,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    with (package_dir / "trade_log.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerow(_row(run_id))
    (package_dir / "audit.md").write_text(f"ML decision: `{audit_decision}`\n", encoding="utf-8")
    return package_dir


def _write_registry(path: Path, approved_packages: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "registry_status": "TEST",
                "manual_approval_required": True,
                "deny_result": "ML_ADMISSION_DENY",
                "approval_bans": {
                    "forbidden_statuses": ["DRAFT", "NEEDS_AUDIT", "NO_GO", "VALIDATION_FAIL", "REJECTED", "UNKNOWN"],
                    "require_contract_audit_pass": True,
                    "require_manifest_valid": True,
                    "forbid_clean_input_data_layers": ["raw", "quarantine", "raw/quarantine"],
                    "forbid_missing_package_files": ["manifest.json", "trade_log.csv", "audit.md"],
                    "forbid_direct_ml_ingest_roots": ["reports/optuna", "reports/pipeline", "reports/final_review"],
                },
                "approved_packages": approved_packages,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )


class MLAlignmentAdmissionStatusAuditTests(unittest.TestCase):
    def test_empty_registry_passes_as_no_approved_packages(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registry = root / "configs" / "ml_approved_calibration_packages.yaml"
            _write_registry(registry, [])

            result = audit_registry_admission_status(project_root=root, registry_path=registry)

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["reason"], "NO_APPROVED_PACKAGES")
            self.assertEqual(result["packages_total"], 0)

    def test_all_admission_statuses_approved_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run_id = "run_001"
            package = _write_package(root, run_id)
            registry = root / "configs" / "ml_approved_calibration_packages.yaml"
            _write_registry(
                registry,
                [
                    {
                        "run_id": run_id,
                        "status": "APPROVED_FOR_ML",
                        "package_path": package.relative_to(root).as_posix(),
                        "approved_by": "manual",
                        "approved_utc": "2026-06-23T00:00:00Z",
                        "comment": "manual approval after OOS audit",
                    }
                ],
            )

            result = audit_registry_admission_status(project_root=root, registry_path=registry)

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["failed_packages"], [])

    def test_registry_status_not_approved_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run_id = "run_001"
            package = _write_package(root, run_id)
            registry = root / "configs" / "ml_approved_calibration_packages.yaml"
            _write_registry(
                registry,
                [
                    {
                        "run_id": run_id,
                        "status": "NO_GO",
                        "package_path": package.relative_to(root).as_posix(),
                        "approved_by": "manual",
                        "approved_utc": "2026-06-23T00:00:00Z",
                        "comment": "manual approval after OOS audit",
                    }
                ],
            )

            result = audit_registry_admission_status(project_root=root, registry_path=registry)

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("registry_status_not_approved_for_ml", result["package_results"][0]["errors"])

    def test_manifest_status_not_approved_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run_id = "run_001"
            package = _write_package(root, run_id, manifest_status="DRAFT")
            registry = root / "configs" / "ml_approved_calibration_packages.yaml"
            _write_registry(
                registry,
                [
                    {
                        "run_id": run_id,
                        "status": "APPROVED_FOR_ML",
                        "package_path": package.relative_to(root).as_posix(),
                        "approved_by": "manual",
                        "approved_utc": "2026-06-23T00:00:00Z",
                        "comment": "manual approval after OOS audit",
                    }
                ],
            )

            result = audit_registry_admission_status(project_root=root, registry_path=registry)

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("manifest_status_not_approved_for_ml", result["package_results"][0]["errors"])

    def test_calibration_package_status_not_approved_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run_id = "run_001"
            package = _write_package(root, run_id, calibration_status="DRAFT")
            registry = root / "configs" / "ml_approved_calibration_packages.yaml"
            _write_registry(
                registry,
                [
                    {
                        "run_id": run_id,
                        "status": "APPROVED_FOR_ML",
                        "package_path": package.relative_to(root).as_posix(),
                        "approved_by": "manual",
                        "approved_utc": "2026-06-23T00:00:00Z",
                        "comment": "manual approval after OOS audit",
                    }
                ],
            )

            result = audit_registry_admission_status(project_root=root, registry_path=registry)

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("calibration_package_status_not_approved_for_ml", result["package_results"][0]["errors"])

    def test_audit_decision_not_go_for_ml_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run_id = "run_001"
            package = _write_package(root, run_id, audit_decision="NO_GO_FOR_ML")
            registry = root / "configs" / "ml_approved_calibration_packages.yaml"
            _write_registry(
                registry,
                [
                    {
                        "run_id": run_id,
                        "status": "APPROVED_FOR_ML",
                        "package_path": package.relative_to(root).as_posix(),
                        "approved_by": "manual",
                        "approved_utc": "2026-06-23T00:00:00Z",
                        "comment": "manual approval after OOS audit",
                    }
                ],
            )

            result = audit_registry_admission_status(project_root=root, registry_path=registry)

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("audit_decision_not_go_for_ml", result["package_results"][0]["errors"])


if __name__ == "__main__":
    unittest.main()
