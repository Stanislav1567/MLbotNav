from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

import yaml

from mlbotnav.ml_alignment_run_id_audit import audit_package_run_id_alignment, audit_registry_run_id_alignment
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


def _write_package(root: Path, run_id: str, *, manifest_run_id: str | None = None, calibration_run_id: str | None = None, trade_run_id: str | None = None) -> Path:
    package_dir = root / "reports" / "ml_candidates" / run_id
    package_dir.mkdir(parents=True, exist_ok=True)
    (package_dir / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": manifest_run_id or run_id,
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
                "status": "DRAFT",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (package_dir / "calibration_package.json").write_text(
        json.dumps(
            {
                "run_id": calibration_run_id or run_id,
                "block_id": "B018",
                "passport_id": "F051",
                "action_id": "F051_BOSDOWN_ALLOW",
                "calibration_params": {"F051_break_buffer_pct": 0.06},
                "signal_mode": "short_only",
                "status": "DRAFT",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    with (package_dir / "trade_log.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerow(_row(trade_run_id or run_id))
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


class MLAlignmentRunIdAuditTests(unittest.TestCase):
    def test_package_run_id_alignment_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            package = _write_package(root, "run_001")

            result = audit_package_run_id_alignment(project_root=root, package_path=package)

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["expected_run_id"], "run_001")
            self.assertEqual(result["errors"], [])

    def test_manifest_run_id_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            package = _write_package(root, "run_001", manifest_run_id="other")

            result = audit_package_run_id_alignment(project_root=root, package_path=package)

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("run_id_mismatch", result["errors"])

    def test_calibration_run_id_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            package = _write_package(root, "run_001", calibration_run_id="other")

            result = audit_package_run_id_alignment(project_root=root, package_path=package)

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("run_id_mismatch", result["errors"])

    def test_trade_log_run_id_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            package = _write_package(root, "run_001", trade_run_id="other")

            result = audit_package_run_id_alignment(project_root=root, package_path=package)

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("run_id_mismatch", result["errors"])

    def test_empty_registry_passes_as_no_approved_packages(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registry = root / "configs" / "ml_approved_calibration_packages.yaml"
            _write_registry(registry, [])

            result = audit_registry_run_id_alignment(project_root=root, registry_path=registry)

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["reason"], "NO_APPROVED_PACKAGES")
            self.assertEqual(result["packages_total"], 0)


if __name__ == "__main__":
    unittest.main()
