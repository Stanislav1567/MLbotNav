from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from mlbotnav.optuna_single_pass_ledger_audit import REQUIRED_COLUMNS, audit_ledger


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=REQUIRED_COLUMNS)
        wr.writeheader()
        for r in rows:
            wr.writerow(r)


class OptunaSinglePassLedgerAuditTests(unittest.TestCase):
    def test_passes_for_valid_row(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            summary = root / "summary.json"
            summary.write_text("{}", encoding="utf-8")
            ledger = root / "runs.csv"
            row = {
                "ts_utc": "2026-05-27T11:00:00Z",
                "task_id": "T1",
                "mode": "short_only",
                "symbol": "SOLUSDT",
                "timeframe": "1m",
                "train_date": "2026-05-19",
                "test_date": "2026-05-20",
                "optuna_stage": "B",
                "repeats_requested": "1",
                "repeats_effective": "1",
                "repeats_effective_mismatch": "False",
                "result_status": "goal_fail",
                "oos_net_return_pct": "-12.5",
                "oos_trades": "10",
                "summary_path": str(summary),
            }
            _write_csv(ledger, [row])
            res = audit_ledger(ledger, require_summary_exists=True)
            self.assertEqual(res["status"], "PASS")
            self.assertEqual(res["rows_total"], 1)
            self.assertEqual(len(res["failed_rows"]), 0)

    def test_fails_on_decimal_comma(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            summary = root / "summary.json"
            summary.write_text("{}", encoding="utf-8")
            ledger = root / "runs.csv"
            row = {
                "ts_utc": "2026-05-27T11:00:00Z",
                "task_id": "T1",
                "mode": "short_only",
                "symbol": "SOLUSDT",
                "timeframe": "1m",
                "train_date": "2026-05-19",
                "test_date": "2026-05-20",
                "optuna_stage": "B",
                "repeats_requested": "1",
                "repeats_effective": "1",
                "repeats_effective_mismatch": "False",
                "result_status": "goal_fail",
                "oos_net_return_pct": "-12,5",
                "oos_trades": "10",
                "summary_path": str(summary),
            }
            _write_csv(ledger, [row])
            res = audit_ledger(ledger, require_summary_exists=True)
            self.assertEqual(res["status"], "FAIL")
            self.assertEqual(len(res["failed_rows"]), 1)
            self.assertIn("decimal_comma:oos_net_return_pct", res["failed_rows"][0]["errors"])

    def test_fails_if_summary_missing_when_required(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ledger = root / "runs.csv"
            row = {
                "ts_utc": "2026-05-27T11:00:00Z",
                "task_id": "T1",
                "mode": "short_only",
                "symbol": "SOLUSDT",
                "timeframe": "1m",
                "train_date": "2026-05-19",
                "test_date": "2026-05-20",
                "optuna_stage": "B",
                "repeats_requested": "1",
                "repeats_effective": "1",
                "repeats_effective_mismatch": "False",
                "result_status": "goal_fail",
                "oos_net_return_pct": "-12.5",
                "oos_trades": "10",
                "summary_path": str(root / "missing-summary.json"),
            }
            _write_csv(ledger, [row])
            res = audit_ledger(ledger, require_summary_exists=True)
            self.assertEqual(res["status"], "FAIL")
            self.assertIn("missing:summary_path", res["failed_rows"][0]["errors"])


if __name__ == "__main__":
    unittest.main()

