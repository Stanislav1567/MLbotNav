from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

import yaml

from mlbotnav.ml_approved_package_registry_reader import read_approved_package_registry


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


def _write_package(project_root: Path, run_id: str) -> Path:
    package_dir = project_root / "reports" / "ml_candidates" / run_id
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
                "status": "DRAFT",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (package_dir / "audit.md").write_text("ML decision: `NO_GO_FOR_ML`\n", encoding="utf-8")
    with (package_dir / "trade_log.csv").open("w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(
            f,
            fieldnames=[
                "run_id",
                "symbol",
                "timeframe",
                "data_layer",
                "train_start",
                "train_end",
                "test_start",
                "test_end",
                "block_id",
                "passport_id",
                "action_id",
                "side",
                "calibration_params_json",
                "entry_signal_time_utc",
                "entry_time_utc",
                "exit_time_utc",
                "entry_price",
                "exit_price",
                "exit_reason",
                "net_return",
                "net_pnl_usd",
                "trade_id",
                "bars_in_trade",
                "tp_hit",
                "sl_hit",
                "timeout_hit",
                "mae_pct",
                "mfe_pct",
            ],
        )
        wr.writeheader()
        wr.writerow(
            {
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
                "trade_id": "T1",
                "bars_in_trade": "1",
                "tp_hit": "true",
                "sl_hit": "false",
                "timeout_hit": "false",
                "mae_pct": "-0.001",
                "mfe_pct": "0.02",
            }
        )
    return package_dir


class MLApprovedPackageRegistryReaderTests(unittest.TestCase):
    def test_empty_registry_returns_pass_with_no_packages(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registry = root / "configs" / "ml_approved_calibration_packages.yaml"
            _write_registry(registry, [])

            result = read_approved_package_registry(project_root=root, registry_path=registry)

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["approved_count"], 0)
            self.assertEqual(result["packages"], [])
            self.assertEqual(result["failures"], [])

    def test_reads_valid_approved_package(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run_id = "oos_SOLUSDT_1m_test_short_only"
            package_dir = _write_package(root, run_id)
            registry = root / "configs" / "ml_approved_calibration_packages.yaml"
            _write_registry(
                registry,
                [
                    {
                        "run_id": run_id,
                        "status": "APPROVED_FOR_ML",
                        "package_path": package_dir.relative_to(root).as_posix(),
                        "approved_by": "manual",
                        "approved_utc": "2026-06-23T00:00:00Z",
                        "comment": "manual approval after OOS audit",
                    }
                ],
            )

            result = read_approved_package_registry(project_root=root, registry_path=registry)

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["approved_count"], 1)
            self.assertEqual(result["packages"][0]["run_id"], run_id)
            self.assertEqual(result["packages"][0]["trade_log_path"], f"reports/ml_candidates/{run_id}/trade_log.csv")
            self.assertEqual(result["packages"][0]["action_id"], "F051_BOSDOWN_ALLOW")

    def test_rejects_no_go_registry_entry(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run_id = "oos_SOLUSDT_1m_test_short_only"
            package_dir = _write_package(root, run_id)
            registry = root / "configs" / "ml_approved_calibration_packages.yaml"
            _write_registry(
                registry,
                [
                    {
                        "run_id": run_id,
                        "status": "NO_GO",
                        "package_path": package_dir.relative_to(root).as_posix(),
                        "approved_by": "manual",
                        "approved_utc": "2026-06-23T00:00:00Z",
                        "comment": "manual approval after OOS audit",
                    }
                ],
            )

            result = read_approved_package_registry(project_root=root, registry_path=registry)

            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["approved_count"], 1)
            self.assertEqual(result["packages"], [])
            self.assertIn("invalid_status:not_approved_for_ml", result["failures"][0]["errors"])


if __name__ == "__main__":
    unittest.main()
