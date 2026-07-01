from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from mlbotnav.ml_smoke_window_manifest_audit import audit_smoke_window_manifest


def _write_manifest(path: Path, **overrides: object) -> None:
    data = {
        "schema_version": 1,
        "wbs_item": "7.1",
        "manifest_status": "SMOKE_WINDOW_SELECTED",
        "symbol": "SOLUSDT",
        "timeframe": "1m",
        "data_layer": "core",
        "train_window": {"start": "2026-05-30", "end": "2026-05-30"},
        "test_window": {"start": "2026-05-31", "end": "2026-05-31"},
        "data_root": "data/core/bybit_ohlcv",
        "expected_file_name": "part-final.csv",
        "forbidden_dates": ["2026-06-01"],
        "forbidden_data_layers": ["raw", "quarantine", "raw/quarantine"],
        "stage_7_boundaries": {
            "package_created": False,
            "package_approved_for_ml": False,
            "registry_mutated": False,
            "ml_training_started": False,
            "ml_ingest_started": False,
        },
    }
    data.update(overrides)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _touch_core_file(root: Path, day: str) -> None:
    path = root / "data" / "core" / "bybit_ohlcv" / f"dt={day}" / "tf=1m" / "symbol=SOLUSDT" / "part-final.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("timestamp,open,high,low,close,volume\n", encoding="utf-8")


class MLSmokeWindowManifestAuditTests(unittest.TestCase):
    def test_valid_manifest_passes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _touch_core_file(root, "2026-05-30")
            _touch_core_file(root, "2026-05-31")
            manifest = root / "configs" / "ml_smoke_run_manifest.yaml"
            _write_manifest(manifest)

            result = audit_smoke_window_manifest(project_root=root, manifest_path=manifest)

            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["selected_dates"], ["2026-05-30", "2026-05-31"])
            self.assertEqual(result["errors"], [])

    def test_raw_layer_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _touch_core_file(root, "2026-05-30")
            _touch_core_file(root, "2026-05-31")
            manifest = root / "configs" / "ml_smoke_run_manifest.yaml"
            _write_manifest(manifest, data_layer="raw")

            result = audit_smoke_window_manifest(project_root=root, manifest_path=manifest)

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("invalid_data_layer:not_core", result["errors"])
            self.assertIn("forbidden_data_layer:raw", result["errors"])

    def test_forbidden_date_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _touch_core_file(root, "2026-05-31")
            _touch_core_file(root, "2026-06-01")
            manifest = root / "configs" / "ml_smoke_run_manifest.yaml"
            _write_manifest(manifest, test_window={"start": "2026-06-01", "end": "2026-06-01"})

            result = audit_smoke_window_manifest(project_root=root, manifest_path=manifest)

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("forbidden_date:2026-06-01", result["errors"])

    def test_missing_core_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _touch_core_file(root, "2026-05-30")
            manifest = root / "configs" / "ml_smoke_run_manifest.yaml"
            _write_manifest(manifest)

            result = audit_smoke_window_manifest(project_root=root, manifest_path=manifest)

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("missing_core_ohlcv_files", result["errors"])

    def test_registry_and_ml_boundaries_must_stay_false(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _touch_core_file(root, "2026-05-30")
            _touch_core_file(root, "2026-05-31")
            manifest = root / "configs" / "ml_smoke_run_manifest.yaml"
            _write_manifest(
                manifest,
                stage_7_boundaries={
                    "package_created": False,
                    "package_approved_for_ml": False,
                    "registry_mutated": True,
                    "ml_training_started": False,
                    "ml_ingest_started": False,
                },
            )

            result = audit_smoke_window_manifest(project_root=root, manifest_path=manifest)

            self.assertEqual(result["status"], "FAIL")
            self.assertIn("invalid_boundary:registry_mutated_must_be_false", result["errors"])


if __name__ == "__main__":
    unittest.main()
