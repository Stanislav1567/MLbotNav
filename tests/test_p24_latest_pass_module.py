from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mlbotnav.p24_latest_pass_contract import resolve_latest_pass_contract


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _touch(path: Path, dt: datetime) -> None:
    ts = dt.timestamp()
    os.utime(path, (ts, ts))


class P24LatestPassModuleTests(unittest.TestCase):
    def _prepare(self) -> tuple[Path, Path, datetime]:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        qa = root / "reports" / "qa_gate"
        final = root / "reports" / "final_review"
        qa.mkdir(parents=True, exist_ok=True)
        final.mkdir(parents=True, exist_ok=True)

        now = datetime.now(timezone.utc).replace(microsecond=0)
        cutoff = now - timedelta(minutes=20)
        fresh = now
        stale = cutoff - timedelta(minutes=15)

        p23 = qa / "p23_operator_unified_20260526T150424Z.json"
        _write_json(p23, {"status": "PASS", "mode": "table_chain"})
        _touch(p23, fresh)

        for n in [
            "table_convergence_5plus_20260526T150434Z.json",
            "features_block_audit_20260526T150505Z.json",
            "orderbook_source_audit_20260526T150448Z.json",
            "tz_gate_20260526T150449Z.json",
            "p72_freeze_ready_20260526T150505Z.json",
        ]:
            f = qa / n
            _write_json(f, {"status": "PASS"})
            _touch(f, fresh)

        stress = final / "stress_backtest_contour_SOLUSDT_1m_2026-05-20_short_only_20260526T144231Z.json"
        _write_json(stress, {"status": "PASS"})
        _touch(stress, stale)
        return root, p23, cutoff

    def test_baseline_latest_bypass_for_stress(self) -> None:
        root, p23, cutoff = self._prepare()
        patterns = [
            "reports/qa_gate/daily_long_short_cycle_*.json",
            "reports/qa_gate/table_convergence_5plus_*.json",
            "reports/qa_gate/features_block_audit_*.json",
            "reports/qa_gate/orderbook_source_audit_*.json",
            "reports/qa_gate/tz_gate_*.json",
            "reports/qa_gate/p72_freeze_ready_*.json",
            "reports/qa_gate/p23_operator_unified_*.json",
            "reports/final_review/stress_backtest_contour_*.json",
        ]
        out = resolve_latest_pass_contract(
            project_root=root,
            patterns=patterns,
            source_p23_mode="table_chain",
            resolved_source_p23=str(p23),
            epoch_lock_enabled=True,
            epoch_cutoff_utc=cutoff,
            epoch_lock_bypass_patterns=["reports/final_review/stress_backtest_contour_*.json"],
        )
        self.assertTrue(out["p23_exact_match"])
        stress = next(x for x in out["items"] if x["pattern"] == "reports/final_review/stress_backtest_contour_*.json")
        self.assertEqual(stress["resolution_mode"], "baseline_latest")
        self.assertTrue(stress["epoch_lock_bypass"])
        self.assertEqual(stress["status"], "PASS")

    def test_missing_epoch_locked_without_bypass(self) -> None:
        root, p23, cutoff = self._prepare()
        patterns = [
            "reports/qa_gate/daily_long_short_cycle_*.json",
            "reports/qa_gate/table_convergence_5plus_*.json",
            "reports/qa_gate/features_block_audit_*.json",
            "reports/qa_gate/orderbook_source_audit_*.json",
            "reports/qa_gate/tz_gate_*.json",
            "reports/qa_gate/p72_freeze_ready_*.json",
            "reports/qa_gate/p23_operator_unified_*.json",
            "reports/final_review/stress_backtest_contour_*.json",
        ]
        out = resolve_latest_pass_contract(
            project_root=root,
            patterns=patterns,
            source_p23_mode="table_chain",
            resolved_source_p23=str(p23),
            epoch_lock_enabled=True,
            epoch_cutoff_utc=cutoff,
            epoch_lock_bypass_patterns=["reports/final_review/non_matching_*.json"],
        )
        stress = next(x for x in out["items"] if x["pattern"] == "reports/final_review/stress_backtest_contour_*.json")
        self.assertEqual(stress["resolution_mode"], "epoch_locked")
        self.assertFalse(stress["epoch_lock_bypass"])
        self.assertEqual(stress["status"], "missing_epoch_locked")
        self.assertGreater(out["missing_count"], 0)


if __name__ == "__main__":
    unittest.main()
