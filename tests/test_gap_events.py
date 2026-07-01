from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from mlbotnav.dq import detect_gap_events_for_step
from mlbotnav.meta_store import append_gap_events


class GapEventsTests(unittest.TestCase):
    def test_detect_gap_events_for_step_lists_missing_candles(self) -> None:
        df = pd.DataFrame(
            {
                "open_time_utc": [
                    "2026-05-20T00:00:00+00:00",
                    "2026-05-20T00:01:00+00:00",
                    "2026-05-20T00:04:00+00:00",
                ]
            }
        )
        gaps = detect_gap_events_for_step(df, time_col="open_time_utc", step_seconds=60)
        self.assertEqual(
            gaps,
            [
                "2026-05-20T00:02:00+00:00",
                "2026-05-20T00:03:00+00:00",
            ],
        )

    def test_append_gap_events_file_mode_deduplicates(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "project"
            dq_root = root / "data" / "dq"
            rows = [
                {
                    "run_id": "r1",
                    "dataset": "bybit_ohlcv",
                    "symbol": "SOLUSDT",
                    "timeframe": "1m",
                    "trade_date_utc": "2026-05-20",
                    "expected_open_time_utc": "2026-05-20T00:02:00+00:00",
                    "created_at_utc": "2026-05-21T00:00:00+00:00",
                },
                {
                    "run_id": "r1",
                    "dataset": "bybit_ohlcv",
                    "symbol": "SOLUSDT",
                    "timeframe": "1m",
                    "trade_date_utc": "2026-05-20",
                    "expected_open_time_utc": "2026-05-20T00:02:00+00:00",
                    "created_at_utc": "2026-05-21T00:00:01+00:00",
                },
            ]
            append_gap_events(dq_root, rows)
            out = pd.read_csv(dq_root / "gap_events.csv")
            self.assertEqual(len(out), 1)


if __name__ == "__main__":
    unittest.main()
