from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mlbotnav.ml_ingest_source_policy import (
    classify_ml_ingest_source_path,
    validate_ml_ingest_source_paths,
)


class MLIngestSourcePolicyTests(unittest.TestCase):
    def test_allows_registry_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            out = classify_ml_ingest_source_path(
                project_root=root,
                source_path="configs/ml_approved_calibration_packages.yaml",
            )

            self.assertEqual(out["status"], "ALLOW")
            self.assertEqual(out["source_class"], "approval_registry")

    def test_allows_candidate_package_trade_log(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            out = classify_ml_ingest_source_path(
                project_root=root,
                source_path="reports/ml_candidates/run_001/trade_log.csv",
            )

            self.assertEqual(out["status"], "ALLOW")
            self.assertEqual(out["source_class"], "approved_candidate_package")

    def test_denies_direct_pipeline_report_source(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            out = classify_ml_ingest_source_path(
                project_root=root,
                source_path="reports/pipeline/backtest_trades_SOLUSDT_1m.csv",
            )

            self.assertEqual(out["status"], "DENY")
            self.assertEqual(out["reason"], "direct_report_source_forbidden:reports/pipeline")

    def test_denies_direct_optuna_and_final_review_sources(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            result = validate_ml_ingest_source_paths(
                project_root=root,
                source_paths=[
                    "reports/optuna/short_only/study_summary.json",
                    "reports/final_review/oos_backtest_trades.csv",
                ],
            )

            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(result["allowed_count"], 0)
            self.assertEqual(result["denied_count"], 2)
            self.assertTrue(
                all(
                    str(check["reason"]).startswith("direct_report_source_forbidden:")
                    for check in result["checks"]
                )
            )

    def test_denies_unknown_raw_source(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)

            out = classify_ml_ingest_source_path(
                project_root=root,
                source_path="data/raw/bybit_ohlcv/dt=2026-05-27/part-000.csv",
            )

            self.assertEqual(out["status"], "DENY")
            self.assertEqual(out["reason"], "not_approved_registry_or_package_source")


if __name__ == "__main__":
    unittest.main()
