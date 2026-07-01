from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mlbotnav.data_window_readiness import evaluate_data_window_readiness
from mlbotnav.workflow_gate import enforce_training_scope


def _mk_day_file(root: Path, *, day: str, tf: str = "1m", symbol: str = "SOLUSDT", layer: str = "raw") -> None:
    p = (
        root
        / "data"
        / layer
        / "bybit_ohlcv"
        / f"dt={day}"
        / f"tf={tf}"
        / f"symbol={symbol}"
        / "part-final.csv"
    )
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("open_time_utc,close_time_utc,open,high,low,close,volume\n", encoding="utf-8")


class DataWindowReadinessTests(unittest.TestCase):
    def test_evaluate_data_window_readiness_pass(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _mk_day_file(root, day="2026-05-01")
            _mk_day_file(root, day="2026-05-02")
            out = evaluate_data_window_readiness(
                root,
                symbol="SOLUSDT",
                timeframe="1m",
                start_date="2026-05-01",
                end_date="2026-05-02",
                layer="raw",
                require_full_coverage=True,
            )
            self.assertEqual(out["status"], "PASS")
            self.assertEqual(out["summary"]["missing_days"], 0)

    def test_evaluate_data_window_readiness_fail_on_missing_day(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _mk_day_file(root, day="2026-05-01")
            _mk_day_file(root, day="2026-05-03")
            out = evaluate_data_window_readiness(
                root,
                symbol="SOLUSDT",
                timeframe="1m",
                start_date="2026-05-01",
                end_date="2026-05-03",
                layer="raw",
                require_full_coverage=True,
            )
            self.assertEqual(out["status"], "FAIL")
            self.assertEqual(out["summary"]["missing_days"], 1)
            self.assertIn("2026-05-02", out["missing_days"])

    def test_enforce_training_scope_blocks_long_window_if_data_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "configs").mkdir(parents=True, exist_ok=True)
            (root / "configs" / "workflow_gate.yaml").write_text(
                (
                    "locked_timeframe: 1m\n"
                    "require_user_confirmation_for_30d: true\n"
                    "allow_30d_window: true\n"
                    "require_data_window_readiness: true\n"
                    "data_window_readiness_min_days: 30\n"
                    "data_window_readiness_layer: raw\n"
                    "data_window_readiness_require_full_coverage: true\n"
                ),
                encoding="utf-8",
            )
            # 30-day window: miss one day on purpose.
            for d in range(1, 31):
                day = f"2026-04-{d:02d}"
                if day == "2026-04-15":
                    continue
                _mk_day_file(root, day=day)
            with self.assertRaises(RuntimeError) as ctx:
                enforce_training_scope(
                    project_root=root,
                    symbol="SOLUSDT",
                    timeframe="1m",
                    start_date="2026-04-01",
                    end_date="2026-04-30",
                    action_name="test_long_window",
                )
            self.assertIn("data_window_readiness_failed", str(ctx.exception))
            reports = list((root / "reports" / "qa_gate").glob("data_window_readiness_test_long_window_*.json"))
            self.assertTrue(reports)


if __name__ == "__main__":
    unittest.main()
