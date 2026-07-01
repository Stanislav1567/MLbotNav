from __future__ import annotations

import unittest

import pandas as pd

from mlbotnav.audit_table_chain import (
    _normalize_signal_side,
    _side_representation_kind,
    _signal_contract_checks,
)


class AuditTableChainContractTests(unittest.TestCase):
    def test_normalize_signal_side_accepts_numeric_and_text_domains(self) -> None:
        self.assertEqual(_normalize_signal_side(1), 1)
        self.assertEqual(_normalize_signal_side(0), 0)
        self.assertEqual(_normalize_signal_side(-1), -1)
        self.assertEqual(_normalize_signal_side("BUY"), 1)
        self.assertEqual(_normalize_signal_side("SELL"), -1)
        self.assertEqual(_normalize_signal_side("NO_TRADE"), 0)
        self.assertIsNone(_normalize_signal_side("BROKEN"))

    def test_side_representation_kind_detects_numeric_vs_text(self) -> None:
        self.assertEqual(_side_representation_kind(pd.Series([1, 0, -1])), "numeric")
        self.assertEqual(_side_representation_kind(pd.Series(["BUY", "SELL", "NO_TRADE"])), "text")
        self.assertEqual(_side_representation_kind(pd.Series(["BUY", 0, "SELL"])), "mixed")

    def test_signal_contract_checks_validate_canonical_contract(self) -> None:
        frame = pd.DataFrame(
            [
                {
                    "signal_id": "sig_1",
                    "symbol": "SOLUSDT",
                    "timeframe": "1m",
                    "signal_time_utc": "2026-05-26T12:00:00Z",
                    "side": 1,
                    "entry_price": 100.0,
                    "stop_price": 99.0,
                    "take_profit_price": 102.0,
                    "expected_move_pct": 0.02,
                    "tp_reach_prob": 0.7,
                    "decision": "BUY",
                    "reason_code": "long_threshold_pass",
                    "run_id": "run_1",
                }
            ]
        )
        checks = _signal_contract_checks(frame, "sample")
        failed = [c["name"] for c in checks if not c["ok"]]
        self.assertEqual(failed, [])


if __name__ == "__main__":
    unittest.main()
