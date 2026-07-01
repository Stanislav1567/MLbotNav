from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

import yaml

from mlbotnav.ml_large_clean_window_manifest_audit import audit_large_clean_window_manifest


def _date_range(start: str, end: str) -> list[str]:
    current = datetime.strptime(start, "%Y-%m-%d")
    last = datetime.strptime(end, "%Y-%m-%d")
    days: list[str] = []
    while current <= last:
        days.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return days


def _write_manifest(path: Path, **overrides: object) -> None:
    data = {
        "schema_version": 1,
        "wbs_item": "8.1",
        "manifest_status": "LARGE_CLEAN_WINDOW_FIXED",
        "symbol": "SOLUSDT",
        "timeframe": "1m",
        "data_layer": "core",
        "train_window": {"start": "2026-05-11", "end": "2026-05-24"},
        "test_window": {"start": "2026-05-25", "end": "2026-05-31"},
        "data_root": "data/core/bybit_ohlcv",
        "expected_file_name": "part-final.csv",
        "forbidden_dates": ["2026-06-01"],
        "forbidden_data_layers": ["raw", "quarantine", "raw/quarantine"],
        "stage_8_boundaries": {
            "optuna_calibration_started": False,
            "package_created": False,
            "package_approved_for_ml": False,
            "ml_ingest_started": False,
            "ml_training_started": False,
        },
        "next_wbs_item": "8.2 Run Optuna calibration",
    }
    data.update(overrides)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _touch_core_files(root: Path, days: list[str]) -> None:
    for day in days:
        path = root / "data" / "core" / "bybit_ohlcv" / f"dt={day}" / "tf=1m" / "symbol=SOLUSDT" / "part-final.csv"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("timestamp,open,high,low,close,volume\n", encoding="utf-8")


class MLLargeCleanWindowManifestAuditTests(unittest.TestCase):
    def test_valid_manifest_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            days = _date_range("2026-05-11", "2026-05-31")
            _touch_core_files(root, days)
            manifest = root / "configs" / "ml_large_clean_window_manifest.yaml"
            _write_manifest(manifest)

            result = audit_large_clean_window_manifest(project_root=root, manifest_path=manifest)

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(len(result["train_dates"]), 14)
            self.assertEqual(len(result["test_dates"]), 7)
            self.assertEqual(result["errors"], [])

    def test_wrong_window_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            days = _date_range("2026-05-12", "2026-05-31")
            _touch_core_files(root, days)
            manifest = root / "configs" / "ml_large_clean_window_manifest.yaml"
            _write_manifest(manifest, train_window={"start": "2026-05-12", "end": "2026-05-24"})

            result = audit_large_clean_window_manifest(project_root=root, manifest_path=manifest)

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("invalid_train_window:not_stage_8_large_clean", result["errors"])

    def test_missing_core_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            days = _date_range("2026-05-11", "2026-05-30")
            _touch_core_files(root, days)
            manifest = root / "configs" / "ml_large_clean_window_manifest.yaml"
            _write_manifest(manifest)

            result = audit_large_clean_window_manifest(project_root=root, manifest_path=manifest)

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("missing_core_ohlcv_files", result["errors"])

    def test_boundaries_must_stay_false(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            days = _date_range("2026-05-11", "2026-05-31")
            _touch_core_files(root, days)
            manifest = root / "configs" / "ml_large_clean_window_manifest.yaml"
            _write_manifest(
                manifest,
                stage_8_boundaries={
                    "optuna_calibration_started": True,
                    "package_created": False,
                    "package_approved_for_ml": False,
                    "ml_ingest_started": False,
                    "ml_training_started": False,
                },
            )

            result = audit_large_clean_window_manifest(project_root=root, manifest_path=manifest)

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("invalid_boundary:optuna_calibration_started_must_be_false", result["errors"])


if __name__ == "__main__":
    unittest.main()
