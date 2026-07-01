from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

import yaml

from mlbotnav.ml_rejection_reason_log import build_rejection_reason_log
from mlbotnav.ml_trade_dataset_contract import REQUIRED_COLUMNS


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


def _valid_row(run_id: str, *, data_layer: str = "core") -> dict[str, str]:
    return {
        "run_id": run_id,
        "symbol": "SOLUSDT",
        "timeframe": "1m",
        "data_layer": data_layer,
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
    project_root: Path,
    run_id: str,
    *,
    manifest_data_layer: str = "core",
    trade_data_layer: str = "core",
    omit_trade_columns: list[str] | None = None,
) -> Path:
    package_dir = project_root / "reports" / "ml_candidates" / run_id
    package_dir.mkdir(parents=True, exist_ok=True)
    (package_dir / "manifest.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "created_utc": "2026-06-23T00:00:00+00:00",
                "symbol": "SOLUSDT",
                "timeframe": "1m",
                "data_layer": manifest_data_layer,
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
    omitted = set(omit_trade_columns or [])
    columns = [col for col in REQUIRED_COLUMNS if col not in omitted]
    with (package_dir / "trade_log.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        row = _valid_row(run_id, data_layer=trade_data_layer)
        writer.writerow({col: row.get(col, "") for col in columns})
    return package_dir


def _categories(result: dict[str, object]) -> set[str]:
    out: set[str] = set()
    for rejection in result["rejections"]:  # type: ignore[index]
        for reason in rejection["reasons"]:
            out.add(reason["category"])
    return out


class MLRejectionReasonLogTests(unittest.TestCase):
    def test_empty_registry_writes_no_rejections_log(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            registry = root / "configs" / "ml_approved_calibration_packages.yaml"
            _write_registry(registry, [])

            result = build_rejection_reason_log(
                project_root=root,
                registry_path=registry,
                out_dir=root / "reports" / "ml_rejections",
                log_name="unit_empty",
            )

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["reason"], "NO_REJECTIONS")
            self.assertEqual(result["rejections_total"], 0)
            self.assertTrue((root / result["log_path"]).exists())

    def test_no_go_status_records_not_approved_and_bad_status(self) -> None:
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
                        "comment": "manual rejection",
                    }
                ],
            )

            result = build_rejection_reason_log(
                project_root=root,
                registry_path=registry,
                out_dir=root / "reports" / "ml_rejections",
                log_name="unit_no_go",
            )

            self.assertEqual(result["reason"], "REJECTIONS_RECORDED")
            self.assertEqual(result["rejections_total"], 1)
            self.assertIn("not_approved", _categories(result))
            self.assertIn("bad_status", _categories(result))

    def test_bad_data_layer_records_reason(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run_id = "oos_SOLUSDT_1m_test_short_only"
            package_dir = _write_package(root, run_id, manifest_data_layer="raw", trade_data_layer="raw")
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
                        "comment": "manual approval",
                    }
                ],
            )

            result = build_rejection_reason_log(
                project_root=root,
                registry_path=registry,
                out_dir=root / "reports" / "ml_rejections",
                log_name="unit_bad_layer",
            )

            self.assertIn("bad_data_layer", _categories(result))

    def test_missing_required_columns_records_reason(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            run_id = "oos_SOLUSDT_1m_test_short_only"
            package_dir = _write_package(root, run_id, omit_trade_columns=["calibration_params_json"])
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
                        "comment": "manual approval",
                    }
                ],
            )

            result = build_rejection_reason_log(
                project_root=root,
                registry_path=registry,
                out_dir=root / "reports" / "ml_rejections",
                log_name="unit_missing_columns",
            )

            self.assertIn("missing_required_columns", _categories(result))
            self.assertIn("contract_fail", _categories(result))


if __name__ == "__main__":
    unittest.main()
