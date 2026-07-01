from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from mlbotnav.p26_audit_lock_contract import resolve_required_reports_contract


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _touch(path: Path, dt: datetime) -> None:
    ts = dt.timestamp()
    os.utime(path, (ts, ts))


class P26AuditLockModuleTests(unittest.TestCase):
    def test_resolve_required_reports_with_missing_and_non_pass(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            qa = root / "reports" / "qa_gate"
            qa.mkdir(parents=True, exist_ok=True)
            now = datetime.now(timezone.utc).replace(microsecond=0)

            p_pass = qa / "p23_operator_unified_20260526T150424Z.json"
            _write_json(p_pass, {"status": "PASS"})
            _touch(p_pass, now)

            p_fail = qa / "features_block_audit_20260526T150505Z.json"
            _write_json(p_fail, {"status": "FAIL"})
            _touch(p_fail, now)

            out = resolve_required_reports_contract(
                project_root=root,
                required_patterns=[
                    "reports/qa_gate/p23_operator_unified_*.json",
                    "reports/qa_gate/features_block_audit_*.json",
                    "reports/qa_gate/tz_gate_*.json",
                ],
            )
            self.assertIn("reports/qa_gate/tz_gate_*.json", out["missing"])
            self.assertEqual(len(out["non_pass_reports"]), 1)
            self.assertTrue(str(p_fail.resolve()) in out["non_pass_reports"])
            self.assertEqual(len(out["reports"]), 2)

    def test_latest_file_is_selected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            qa = root / "reports" / "qa_gate"
            qa.mkdir(parents=True, exist_ok=True)
            now = datetime.now(timezone.utc).replace(microsecond=0)

            old_f = qa / "orderbook_source_audit_20260526T150001Z.json"
            new_f = qa / "orderbook_source_audit_20260526T150999Z.json"
            _write_json(old_f, {"status": "PASS"})
            _write_json(new_f, {"status": "PASS"})
            _touch(old_f, now.replace(second=1))
            _touch(new_f, now.replace(second=50))

            out = resolve_required_reports_contract(
                project_root=root,
                required_patterns=["reports/qa_gate/orderbook_source_audit_*.json"],
            )
            self.assertEqual(len(out["reports"]), 1)
            self.assertEqual(out["reports"][0]["file"], str(new_f.resolve()))
            self.assertEqual(out["reports"][0]["status"], "PASS")

    def test_daily_cycle_not_required_for_table_chain_mode(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            qa = root / "reports" / "qa_gate"
            qa.mkdir(parents=True, exist_ok=True)
            now = datetime.now(timezone.utc).replace(microsecond=0)

            p_fail = qa / "daily_long_short_cycle_20260527T010612Z.json"
            _write_json(p_fail, {"status": "FAIL"})
            _touch(p_fail, now)

            out = resolve_required_reports_contract(
                project_root=root,
                required_patterns=["reports/qa_gate/daily_long_short_cycle_*.json"],
                source_p23_mode="table_chain",
            )
            self.assertEqual(out["missing"], [])
            self.assertEqual(out["non_pass_reports"], [])
            self.assertEqual(len(out["reports"]), 1)
            self.assertEqual(out["reports"][0]["status"], "not_required_for_table_chain")
            self.assertIsNone(out["reports"][0]["file"])


if __name__ == "__main__":
    unittest.main()
