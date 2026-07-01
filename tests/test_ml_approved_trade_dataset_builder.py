from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

import yaml

from mlbotnav.ml_approved_trade_dataset_builder import build_approved_trade_dataset
from mlbotnav.ml_trade_dataset_contract import REQUIRED_COLUMNS, validate_trade_dataset_csv


def _valid_row(run_id: str) -> dict[str, str]:
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
    (package_dir / "audit.md").write_text("ML decision: `GO_FOR_ML`\n", encoding="utf-8")
    with (package_dir / "trade_log.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerow(_valid_row(run_id))
    return package_dir


class MLApprovedTradeDatasetBuilderTests(unittest.TestCase):
    def test_empty_registry_is_pass_noop(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registry = root / "configs" / "ml_approved_calibration_packages.yaml"
            _write_registry(registry, [])

            result = build_approved_trade_dataset(
                project_root=root,
                registry_path=registry,
                out_dir=root / "reports" / "ml_datasets",
            )

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["reason"], "NO_APPROVED_PACKAGES")
            self.assertEqual(result["rows_total"], 0)
            self.assertEqual(result["dataset_path"], "")

    def test_builds_dataset_from_valid_approved_package(self) -> None:
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

            result = build_approved_trade_dataset(
                project_root=root,
                registry_path=registry,
                out_dir=root / "reports" / "ml_datasets",
                dataset_name="unit_dataset",
            )

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["rows_total"], 1)
            dataset_path = root / result["dataset_path"]
            manifest_path = root / result["manifest_path"]
            self.assertTrue(dataset_path.exists())
            self.assertTrue(manifest_path.exists())
            contract = validate_trade_dataset_csv(dataset_path)
            self.assertEqual(contract["status"], "PASS")
            with dataset_path.open("r", encoding="utf-8", newline="") as f:
                row = next(csv.DictReader(f))
            self.assertEqual(row["run_id"], run_id)
            self.assertEqual(row["source_package_path"], f"reports/ml_candidates/{run_id}")
            self.assertEqual(row["source_trade_log_path"], f"reports/ml_candidates/{run_id}/trade_log.csv")

    def test_registry_reader_failure_blocks_dataset(self) -> None:
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

            result = build_approved_trade_dataset(
                project_root=root,
                registry_path=registry,
                out_dir=root / "reports" / "ml_datasets",
            )

            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["reason"], "registry_reader_failed")
            self.assertEqual(result["dataset_path"], "")


if __name__ == "__main__":
    unittest.main()
