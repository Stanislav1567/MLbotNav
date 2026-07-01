from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mlbotnav.p24_latest_pass_contract import resolve_latest_pass_contract
from mlbotnav.p26_audit_lock_contract import resolve_required_reports_contract
from mlbotnav.qa_audit_lock_expectations import get_p26_lock_files, get_p26_required_table_files
from mlbotnav.qa_required_patterns import (
    STRESS_PATTERN,
    get_p24_epoch_lock_baseline_allowed_patterns,
    get_p24_required_patterns,
    get_p26_required_patterns,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _touch(path: Path, dt: datetime) -> None:
    ts = dt.timestamp()
    os.utime(path, (ts, ts))


class SharedContractsFullIntegrationTests(unittest.TestCase):
    def test_shared_contracts_remain_consistent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            qa = root / "reports" / "qa_gate"
            final_review = root / "reports" / "final_review"
            qa.mkdir(parents=True, exist_ok=True)
            final_review.mkdir(parents=True, exist_ok=True)

            now = datetime.now(timezone.utc).replace(microsecond=0)
            cutoff = now - timedelta(minutes=20)
            fresh = now
            stale = cutoff - timedelta(minutes=35)

            p23 = qa / "p23_operator_unified_20260526T150424Z.json"
            _write_json(p23, {"status": "PASS", "mode": "table_chain"})
            _touch(p23, fresh)

            for name in [
                "daily_long_short_cycle_20260525T223031Z.json",
                "table_convergence_5plus_20260526T150434Z.json",
                "features_block_audit_20260526T150505Z.json",
                "orderbook_source_audit_20260526T150448Z.json",
                "tz_gate_20260526T150449Z.json",
                "p72_freeze_ready_20260526T150505Z.json",
            ]:
                f = qa / name
                _write_json(f, {"status": "PASS"})
                _touch(f, fresh)

            stress = final_review / "stress_backtest_contour_SOLUSDT_1m_2026-05-20_short_only_20260526T144231Z.json"
            _write_json(stress, {"status": "PASS"})
            _touch(stress, stale)

            for rel in get_p26_required_table_files():
                fp = root / rel
                fp.parent.mkdir(parents=True, exist_ok=True)
                fp.write_bytes(b"ok")
                _touch(fp, fresh)

            for rel in get_p26_lock_files():
                fp = root / rel
                fp.parent.mkdir(parents=True, exist_ok=True)
                fp.write_text("lock", encoding="utf-8")
                _touch(fp, fresh)

            p24_patterns = get_p24_required_patterns(require_stress=True)
            p26_patterns = get_p26_required_patterns(require_stress=True)
            self.assertEqual(p24_patterns, p26_patterns)
            self.assertIn(STRESS_PATTERN, p24_patterns)
            self.assertEqual(get_p24_epoch_lock_baseline_allowed_patterns(require_stress=True), [STRESS_PATTERN])

            p24 = resolve_latest_pass_contract(
                project_root=root,
                patterns=p24_patterns,
                source_p23_mode="table_chain",
                resolved_source_p23=str(p23),
                epoch_lock_enabled=True,
                epoch_cutoff_utc=cutoff,
                epoch_lock_bypass_patterns=get_p24_epoch_lock_baseline_allowed_patterns(require_stress=True),
            )
            p26 = resolve_required_reports_contract(project_root=root, required_patterns=p26_patterns)

            self.assertTrue(p24["p23_exact_match"])
            self.assertEqual(p24["missing_count"], 0)
            self.assertEqual(p24["non_pass_count"], 0)
            self.assertEqual(p26["missing"], [])
            self.assertEqual(p26["non_pass_reports"], [])

            stress_item = next(x for x in p24["items"] if x["pattern"] == STRESS_PATTERN)
            self.assertEqual(stress_item["status"], "PASS")
            self.assertEqual(stress_item["resolution_mode"], "baseline_latest")
            self.assertTrue(stress_item["epoch_lock_bypass"])


if __name__ == "__main__":
    unittest.main()
