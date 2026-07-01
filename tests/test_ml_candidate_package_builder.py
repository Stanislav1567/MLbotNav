from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from mlbotnav.ml_candidate_package_builder import (
    copy_trade_log_csv,
    copy_source_reports,
    create_calibration_package_json,
    create_candidate_package_structure,
    create_manifest_json,
    create_package_audit_md,
    validate_run_id,
)


class MLCandidatePackageBuilderTests(unittest.TestCase):
    def test_create_candidate_package_structure(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project_root = Path(td)
            out = create_candidate_package_structure(project_root=project_root, run_id="oos_SOLUSDT_1m_test")

            self.assertEqual(out.run_id, "oos_SOLUSDT_1m_test")
            self.assertEqual(out.status, "STRUCTURE_READY")
            self.assertTrue(out.package_dir.exists())
            self.assertEqual(out.package_dir, project_root / "reports" / "ml_candidates" / "oos_SOLUSDT_1m_test")
            self.assertEqual(out.as_dict(project_root)["package_dir"], "reports/ml_candidates/oos_SOLUSDT_1m_test")

    def test_validate_run_id_rejects_path_escape(self) -> None:
        for value in ("../bad", "bad/name", "bad\\name", ""):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    validate_run_id(value)

    def test_create_calibration_package_json_from_trade_csv(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project_root = Path(td)
            trade_csv = project_root / "trade.csv"
            with trade_csv.open("w", encoding="utf-8", newline="") as f:
                wr = csv.DictWriter(
                    f,
                    fieldnames=[
                        "run_id",
                        "block_id",
                        "passport_id",
                        "action_id",
                        "calibration_params_json",
                    ],
                )
                wr.writeheader()
                wr.writerow(
                    {
                        "run_id": "oos_SOLUSDT_1m_test_short_only",
                        "block_id": "B018",
                        "passport_id": "F051",
                        "action_id": "F051_BOSDOWN_ALLOW",
                        "calibration_params_json": '{"F051_break_buffer_pct":0.06}',
                    }
                )
            oos_report = project_root / "oos_report.json"
            oos_report.write_text(
                json.dumps({"risk_policy": {"signal_mode": "short_only"}}, ensure_ascii=False),
                encoding="utf-8",
            )

            out_path, payload = create_calibration_package_json(
                project_root=project_root,
                run_id="oos_SOLUSDT_1m_test_short_only",
                trade_csv_path=trade_csv,
                oos_report_path=oos_report,
            )

            self.assertTrue(out_path.exists())
            self.assertEqual(out_path.name, "calibration_package.json")
            self.assertEqual(payload["run_id"], "oos_SOLUSDT_1m_test_short_only")
            self.assertEqual(payload["block_id"], "B018")
            self.assertEqual(payload["passport_id"], "F051")
            self.assertEqual(payload["action_id"], "F051_BOSDOWN_ALLOW")
            self.assertEqual(payload["calibration_params"], {"F051_break_buffer_pct": 0.06})
            self.assertEqual(payload["signal_mode"], "short_only")
            self.assertEqual(payload["status"], "DRAFT")
            self.assertEqual(json.loads(out_path.read_text(encoding="utf-8")), payload)

    def test_create_calibration_package_json_rejects_run_id_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project_root = Path(td)
            trade_csv = project_root / "trade.csv"
            with trade_csv.open("w", encoding="utf-8", newline="") as f:
                wr = csv.DictWriter(
                    f,
                    fieldnames=[
                        "run_id",
                        "block_id",
                        "passport_id",
                        "action_id",
                        "calibration_params_json",
                    ],
                )
                wr.writeheader()
                wr.writerow(
                    {
                        "run_id": "other_run",
                        "block_id": "B018",
                        "passport_id": "F051",
                        "action_id": "F051_BOSDOWN_ALLOW",
                        "calibration_params_json": '{"F051_break_buffer_pct":0.06}',
                    }
                )

            with self.assertRaises(ValueError):
                create_calibration_package_json(
                    project_root=project_root,
                    run_id="expected_run",
                    trade_csv_path=trade_csv,
                )

    def test_copy_trade_log_csv_into_package(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project_root = Path(td)
            trade_csv = project_root / "source_trade.csv"
            source_text = (
                "run_id,block_id,passport_id,action_id,calibration_params_json\n"
                'oos_SOLUSDT_1m_test_short_only,B018,F051,F051_BOSDOWN_ALLOW,"{""F051_break_buffer_pct"":0.06}"\n'
            )
            trade_csv.write_text(source_text, encoding="utf-8")

            out_path = copy_trade_log_csv(
                project_root=project_root,
                run_id="oos_SOLUSDT_1m_test_short_only",
                trade_csv_path=trade_csv,
            )

            self.assertEqual(out_path, project_root / "reports" / "ml_candidates" / "oos_SOLUSDT_1m_test_short_only" / "trade_log.csv")
            self.assertEqual(out_path.read_text(encoding="utf-8"), source_text)

    def test_copy_trade_log_csv_rejects_run_id_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project_root = Path(td)
            trade_csv = project_root / "source_trade.csv"
            trade_csv.write_text(
                "run_id,block_id,passport_id,action_id,calibration_params_json\n"
                'other_run,B018,F051,F051_BOSDOWN_ALLOW,"{""F051_break_buffer_pct"":0.06}"\n',
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                copy_trade_log_csv(
                    project_root=project_root,
                    run_id="expected_run",
                    trade_csv_path=trade_csv,
                )

    def test_copy_source_reports_into_package(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project_root = Path(td)
            oos_report = project_root / "oos_report_source.json"
            pipeline_report = project_root / "pipeline_report_source.json"
            oos_report.write_text(json.dumps({"run_id": "oos_SOLUSDT_1m_test_short_only"}), encoding="utf-8")
            pipeline_report.write_text(json.dumps({"run_id": "pipeline_SOLUSDT_1m_test"}), encoding="utf-8")

            out_path, payload = copy_source_reports(
                project_root=project_root,
                run_id="oos_SOLUSDT_1m_test_short_only",
                oos_report_path=oos_report,
                pipeline_report_path=pipeline_report,
            )

            package_dir = project_root / "reports" / "ml_candidates" / "oos_SOLUSDT_1m_test_short_only"
            self.assertEqual(out_path, package_dir / "source_reports.json")
            self.assertTrue((package_dir / "source_reports" / "oos_report.json").exists())
            self.assertTrue((package_dir / "source_reports" / "pipeline_report.json").exists())
            self.assertFalse((package_dir / "source_reports" / "optuna_report.json").exists())
            self.assertEqual(payload["source_reports"]["oos_report"]["status"], "COPIED")
            self.assertEqual(payload["source_reports"]["pipeline_report"]["status"], "COPIED")
            self.assertEqual(payload["source_reports"]["optuna_report"]["status"], "NOT_PROVIDED")
            self.assertEqual(json.loads(out_path.read_text(encoding="utf-8")), payload)

    def test_copy_source_reports_rejects_missing_required_report(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project_root = Path(td)
            oos_report = project_root / "missing_oos_report.json"
            pipeline_report = project_root / "pipeline_report_source.json"
            pipeline_report.write_text(json.dumps({"run_id": "pipeline_SOLUSDT_1m_test"}), encoding="utf-8")

            with self.assertRaises(FileNotFoundError):
                copy_source_reports(
                    project_root=project_root,
                    run_id="oos_SOLUSDT_1m_test_short_only",
                    oos_report_path=oos_report,
                    pipeline_report_path=pipeline_report,
                )

    def test_create_manifest_json_from_package_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project_root = Path(td)
            run_id = "oos_SOLUSDT_1m_test_short_only"
            package_dir = project_root / "reports" / "ml_candidates" / run_id
            package_dir.mkdir(parents=True)
            (package_dir / "calibration_package.json").write_text(
                json.dumps(
                    {
                        "run_id": run_id,
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
            (package_dir / "source_reports.json").write_text(
                json.dumps(
                    {
                        "run_id": run_id,
                        "source_reports": {
                            "oos_report": {"status": "COPIED", "package_path": "reports/ml_candidates/run/source_reports/oos_report.json"},
                            "pipeline_report": {"status": "COPIED", "package_path": "reports/ml_candidates/run/source_reports/pipeline_report.json"},
                            "optuna_report": {"status": "NOT_PROVIDED"},
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
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
                    }
                )

            out_path, payload = create_manifest_json(project_root=project_root, run_id=run_id)

            self.assertEqual(out_path, package_dir / "manifest.json")
            self.assertEqual(payload["run_id"], run_id)
            self.assertEqual(payload["symbol"], "SOLUSDT")
            self.assertEqual(payload["timeframe"], "1m")
            self.assertEqual(payload["data_layer"], "core")
            self.assertEqual(payload["train_window"], {"start": "2026-05-25", "end": "2026-05-26"})
            self.assertEqual(payload["test_window"], {"start": "2026-05-27", "end": "2026-05-27"})
            self.assertEqual(payload["block_id"], "B018")
            self.assertEqual(payload["passport_id"], "F051")
            self.assertEqual(payload["action_id"], "F051_BOSDOWN_ALLOW")
            self.assertEqual(payload["status"], "DRAFT")
            self.assertIn("source_reports", payload)
            self.assertEqual(json.loads(out_path.read_text(encoding="utf-8")), payload)

    def test_create_manifest_json_rejects_run_id_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project_root = Path(td)
            run_id = "oos_SOLUSDT_1m_test_short_only"
            package_dir = project_root / "reports" / "ml_candidates" / run_id
            package_dir.mkdir(parents=True)
            (package_dir / "calibration_package.json").write_text(
                json.dumps({"run_id": "other_run", "block_id": "B018", "passport_id": "F051", "action_id": "F051_BOSDOWN_ALLOW"}),
                encoding="utf-8",
            )
            (package_dir / "source_reports.json").write_text(
                json.dumps({"run_id": run_id, "source_reports": {"oos_report": {"status": "COPIED"}}}),
                encoding="utf-8",
            )
            (package_dir / "trade_log.csv").write_text(
                "run_id,symbol,timeframe,data_layer,train_start,train_end,test_start,test_end\n"
                f"{run_id},SOLUSDT,1m,core,2026-05-25,2026-05-26,2026-05-27,2026-05-27\n",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                create_manifest_json(project_root=project_root, run_id=run_id)

    def test_create_package_audit_md_from_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project_root = Path(td)
            run_id = "oos_SOLUSDT_1m_test_short_only"
            package_dir = project_root / "reports" / "ml_candidates" / run_id
            package_dir.mkdir(parents=True)
            (package_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "run_id": run_id,
                        "symbol": "SOLUSDT",
                        "timeframe": "1m",
                        "data_layer": "core",
                        "train_window": {"start": "2026-05-25", "end": "2026-05-26"},
                        "test_window": {"start": "2026-05-27", "end": "2026-05-27"},
                        "block_id": "B018",
                        "passport_id": "F051",
                        "action_id": "F051_BOSDOWN_ALLOW",
                        "status": "DRAFT",
                        "package_files": {
                            "calibration_package": "reports/ml_candidates/run/calibration_package.json",
                            "trade_log": "reports/ml_candidates/run/trade_log.csv",
                            "source_reports_index": "reports/ml_candidates/run/source_reports.json",
                        },
                        "source_reports": {
                            "oos_report": {"status": "COPIED", "package_path": "reports/ml_candidates/run/source_reports/oos_report.json"},
                            "pipeline_report": {"status": "COPIED", "package_path": "reports/ml_candidates/run/source_reports/pipeline_report.json"},
                            "optuna_report": {"status": "NOT_PROVIDED"},
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            out_path, text = create_package_audit_md(project_root=project_root, run_id=run_id)

            self.assertEqual(out_path, package_dir / "audit.md")
            self.assertIn("ML decision: `NO_GO_FOR_ML`", text)
            self.assertIn("Review state: `READY_FOR_MANUAL_REVIEW`", text)
            self.assertIn("Package is DRAFT", text)
            self.assertIn("F051_BOSDOWN_ALLOW", text)
            self.assertEqual(out_path.read_text(encoding="utf-8"), text)

    def test_create_package_audit_md_requires_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            project_root = Path(td)
            run_id = "oos_SOLUSDT_1m_test_short_only"

            with self.assertRaises(FileNotFoundError):
                create_package_audit_md(project_root=project_root, run_id=run_id)


if __name__ == "__main__":
    unittest.main()
