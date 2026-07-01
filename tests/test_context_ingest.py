from __future__ import annotations

import unittest

import pandas as pd

from mlbotnav.bybit_client import interval_to_oi_interval_time
from mlbotnav.context_contract import validate_funding_contract, validate_open_interest_contract
from mlbotnav.context_dq import run_context_dq


class ContextIngestTests(unittest.TestCase):
    def test_oi_interval_mapping_rejects_unsupported_1m(self) -> None:
        self.assertEqual(interval_to_oi_interval_time("5"), "5min")
        with self.assertRaises(ValueError):
            interval_to_oi_interval_time("1")

    def test_open_interest_contract_valid_for_5m_day(self) -> None:
        df = pd.DataFrame(
            [
                {
                    "exchange": "bybit_open_interest",
                    "market_type": "linear",
                    "symbol": "SOLUSDT",
                    "timeframe": "5m",
                    "open_time_utc": "2026-05-20T00:00:00+00:00",
                    "open_interest": "12345.6",
                    "ingest_run_id": "r1",
                    "source_ts_utc": "2026-05-21T00:00:00+00:00",
                },
                {
                    "exchange": "bybit_open_interest",
                    "market_type": "linear",
                    "symbol": "SOLUSDT",
                    "timeframe": "5m",
                    "open_time_utc": "2026-05-20T00:05:00+00:00",
                    "open_interest": "12346.6",
                    "ingest_run_id": "r1",
                    "source_ts_utc": "2026-05-21T00:00:00+00:00",
                },
            ]
        )
        result = validate_open_interest_contract(
            df,
            expected_symbol="SOLUSDT",
            expected_timeframe="5m",
            expected_market_type="linear",
            expected_trade_date_utc="2026-05-20",
        )
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.clean_df), 2)

    def test_funding_contract_valid_for_8h_day(self) -> None:
        df = pd.DataFrame(
            [
                {
                    "exchange": "bybit_funding",
                    "market_type": "linear",
                    "symbol": "SOLUSDT",
                    "timeframe": "8h",
                    "event_time_utc": "2026-05-20T00:00:00+00:00",
                    "funding_rate": "0.0001",
                    "ingest_run_id": "r1",
                    "source_ts_utc": "2026-05-21T00:00:00+00:00",
                }
            ]
        )
        result = validate_funding_contract(
            df,
            expected_symbol="SOLUSDT",
            expected_market_type="linear",
            expected_trade_date_utc="2026-05-20",
        )
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.clean_df), 1)

    def test_context_dq_empty_day_fails(self) -> None:
        df = pd.DataFrame(columns=["open_time_utc", "open_interest"])
        dq = run_context_dq(
            df,
            timeframe="5m",
            time_col="open_time_utc",
            value_col="open_interest",
            is_current_day=False,
        )
        self.assertEqual(dq.actual_rows, 0)
        self.assertEqual(dq.status, "FAIL")


if __name__ == "__main__":
    unittest.main()
