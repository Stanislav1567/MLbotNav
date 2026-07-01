from __future__ import annotations

import unittest

from mlbotnav.runtime_trading_fields import (
    RUNTIME_TRADING_FIELDS_KEYS,
    build_runtime_trading_fields,
    validate_runtime_trading_fields,
)


class RuntimeTradingFieldsContractTests(unittest.TestCase):
    def test_build_runtime_trading_fields_emits_full_keyset(self) -> None:
        payload = build_runtime_trading_fields(
            symbol="SOLUSDT",
            timeframe="1m",
            signal_mode="short_only",
            execution_mode="exchange_like",
            order_type="market",
            stop_loss_pct=0.01,
            take_profit_pct=0.02,
            min_expected_move_pct=0.003,
            min_tp_reach_prob=0.58,
            trades=7,
            net_return_pct=1.25,
            goal_pass=True,
        )
        self.assertEqual(set(payload.keys()), set(RUNTIME_TRADING_FIELDS_KEYS))
        self.assertEqual(payload["symbol"], "SOLUSDT")
        self.assertEqual(payload["timeframe"], "1m")
        self.assertEqual(payload["signal_mode"], "short_only")
        self.assertEqual(payload["execution_mode"], "exchange_like")
        self.assertEqual(payload["order_type"], "market")
        self.assertEqual(payload["trades"], 7)
        self.assertAlmostEqual(float(payload["net_return_pct"]), 1.25, places=12)
        self.assertTrue(payload["goal_pass"])

    def test_validate_runtime_trading_fields_detects_missing_keys(self) -> None:
        payload = {"symbol": "SOLUSDT"}
        missing = validate_runtime_trading_fields(payload)
        self.assertIn("timeframe", missing)
        self.assertIn("goal_pass", missing)
        self.assertNotIn("symbol", missing)

    def test_build_runtime_trading_fields_normalizes_types(self) -> None:
        payload = build_runtime_trading_fields(
            symbol="SOLUSDT",
            timeframe="1m",
            signal_mode="both",
            execution_mode="research",
            order_type="market",
            stop_loss_pct="0.01",
            take_profit_pct="0.02",
            min_expected_move_pct="0.003",
            min_tp_reach_prob="0.58",
            trades="9",
            net_return_pct="1.75",
            goal_pass="true",
        )
        self.assertEqual(payload["trades"], 9)
        self.assertAlmostEqual(float(payload["stop_loss_pct"]), 0.01, places=12)
        self.assertAlmostEqual(float(payload["take_profit_pct"]), 0.02, places=12)
        self.assertAlmostEqual(float(payload["min_expected_move_pct"]), 0.003, places=12)
        self.assertAlmostEqual(float(payload["min_tp_reach_prob"]), 0.58, places=12)
        self.assertAlmostEqual(float(payload["net_return_pct"]), 1.75, places=12)
        self.assertTrue(payload["goal_pass"])


if __name__ == "__main__":
    unittest.main()
