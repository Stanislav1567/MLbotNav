from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mlbotnav.p24_latest_pass_contract import resolve_latest_pass_contract
from mlbotnav.p26_audit_lock_contract import resolve_required_reports_contract


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _touch(path: Path, dt: datetime) -> None:
    ts = dt.timestamp()
    os.utime(path, (ts, ts))


class P24P26ContractIntegrationTests(unittest.TestCase):
    def test_p24_and_p26_contracts_are_consistent_on_same_dataset(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            qa = root / "reports" / "qa_gate"
            final_review = root / "reports" / "final_review"
            qa.mkdir(parents=True, exist_ok=True)
            final_review.mkdir(parents=True, exist_ok=True)

            now = datetime.now(timezone.utc).replace(microsecond=0)
            cutoff = now - timedelta(minutes=20)
            fresh = now
            stale = cutoff - timedelta(minutes=40)

            p23 = qa / "p23_operator_unified_20260526T150424Z.json"
            _write_json(p23, {"status": "PASS", "mode": "table_chain"})
            _touch(p23, fresh)

            # Required QA reports for both P24/P26.
            for n in [
                "daily_long_short_cycle_20260525T223031Z.json",
                "table_convergence_5plus_20260526T150434Z.json",
                "features_block_audit_20260526T150505Z.json",
                "orderbook_source_audit_20260526T150448Z.json",
                "tz_gate_20260526T150449Z.json",
                "p72_freeze_ready_20260526T150505Z.json",
            ]:
                f = qa / n
                _write_json(f, {"status": "PASS"})
                _touch(f, fresh)

            stress = final_review / "stress_backtest_contour_SOLUSDT_1m_2026-05-20_short_only_20260526T144231Z.json"
            _write_json(stress, {"status": "PASS"})
            _touch(stress, stale)

            p24_patterns = [
                "reports/qa_gate/daily_long_short_cycle_*.json",
                "reports/qa_gate/table_convergence_5plus_*.json",
                "reports/qa_gate/features_block_audit_*.json",
                "reports/qa_gate/orderbook_source_audit_*.json",
                "reports/qa_gate/tz_gate_*.json",
                "reports/qa_gate/p72_freeze_ready_*.json",
                "reports/qa_gate/p23_operator_unified_*.json",
                "reports/final_review/stress_backtest_contour_*.json",
            ]
            p26_patterns = [
                "reports/qa_gate/p23_operator_unified_*.json",
                "reports/qa_gate/daily_long_short_cycle_*.json",
                "reports/qa_gate/table_convergence_5plus_*.json",
                "reports/qa_gate/features_block_audit_*.json",
                "reports/qa_gate/orderbook_source_audit_*.json",
                "reports/qa_gate/tz_gate_*.json",
                "reports/qa_gate/p72_freeze_ready_*.json",
                "reports/final_review/stress_backtest_contour_*.json",
            ]

            p24 = resolve_latest_pass_contract(
                project_root=root,
                patterns=p24_patterns,
                source_p23_mode="table_chain",
                resolved_source_p23=str(p23),
                epoch_lock_enabled=True,
                epoch_cutoff_utc=cutoff,
                epoch_lock_bypass_patterns=["reports/final_review/stress_backtest_contour_*.json"],
            )
            p26 = resolve_required_reports_contract(project_root=root, required_patterns=p26_patterns)

            self.assertTrue(bool(p24["p23_exact_match"]))
            self.assertEqual(int(p24["non_pass_count"]), 0)
            self.assertEqual(int(p24["missing_count"]), 0)

            stress_item = next(x for x in p24["items"] if x["pattern"] == "reports/final_review/stress_backtest_contour_*.json")
            self.assertEqual(stress_item["status"], "PASS")
            self.assertEqual(stress_item["resolution_mode"], "baseline_latest")
            self.assertTrue(bool(stress_item["epoch_lock_bypass"]))

            # P26 on same dataset should observe all required artifacts PASS as well.
            self.assertEqual(p26["missing"], [])
            self.assertEqual(p26["non_pass_reports"], [])
            p26_stress = next(x for x in p26["reports"] if x["pattern"] == "reports/final_review/stress_backtest_contour_*.json")
            self.assertEqual(p26_stress["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
