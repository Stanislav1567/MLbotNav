from __future__ import annotations

import unittest

import pandas as pd

from mlbotnav.backtest import run_prob_backtest


class BacktestNotionalTests(unittest.TestCase):
    def test_notional_usd_defaults_to_ten_and_pnl_is_reported(self) -> None:
        oof = pd.DataFrame(
            {
                "open_time_utc": [
                    "2025-01-01T00:00:00+00:00",
                    "2025-07-01T00:00:00+00:00",
                    "2026-01-01T00:00:00+00:00",
                ],
                "future_return": [0.01, -0.005, 0.02],
                "prob_up": [0.8, 0.2, 0.9],
            }
        )
        _df, summary = run_prob_backtest(oof, fee_bps=0.0, slippage_bps=0.0, notional_usd=10.0)
        self.assertEqual(float(summary["notional_usd"]), 10.0)
        self.assertIn("net_pnl_total_usd", summary)
        self.assertIn("avg_trade_pnl_usd", summary)

    def test_position_size_legacy_alias_maps_to_notional(self) -> None:
        oof = pd.DataFrame(
            {
                "open_time_utc": [
                    "2025-01-01T00:00:00+00:00",
                    "2026-01-01T00:00:00+00:00",
                ],
                "future_return": [0.01, 0.01],
                "prob_up": [0.9, 0.9],
            }
        )
        _df, summary = run_prob_backtest(oof, fee_bps=0.0, slippage_bps=0.0, position_size=7.0)
        self.assertEqual(float(summary["notional_usd"]), 7.0)


if __name__ == "__main__":
    unittest.main()
