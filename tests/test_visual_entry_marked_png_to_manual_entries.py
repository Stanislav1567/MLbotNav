from __future__ import annotations

import unittest

import pandas as pd

from mlbotnav.visual_entry_marked_png_to_manual_entries import (
    pixel_x_to_time,
    select_auto_knife_candidates,
)


class VisualEntryMarkedPngToManualEntriesTests(unittest.TestCase):
    def test_pixel_x_to_time_rounds_to_nearest_minute(self) -> None:
        ts = pixel_x_to_time(
            x=159.0 + 52.625 * 3.5,
            date_utc="2026-05-13",
            x_utc_0000=159.0,
            px_per_hour=52.625,
        )
        self.assertEqual(ts.strftime("%Y-%m-%dT%H:%M:%SZ"), "2026-05-13T03:30:00Z")

    def test_auto_knife_candidates_are_spaced_by_cooldown(self) -> None:
        times = pd.date_range("2026-05-13T00:00:00Z", periods=90, freq="min")
        rows = []
        price = 100.0
        for idx, ts in enumerate(times):
            if idx in (35, 38, 70):
                close = price - 1.2
                low = close - 0.4
                volume = 50_000.0
            else:
                close = price + 0.01
                low = min(price, close) - 0.04
                volume = 1_000.0
            rows.append(
                {
                    "open_time_utc": ts,
                    "open": price,
                    "high": max(price, close) + 0.04,
                    "low": low,
                    "close": close,
                    "volume": volume,
                }
            )
            price = close
        df = pd.DataFrame(rows)

        candidates = select_auto_knife_candidates(df, top_n=4, cooldown_bars=10)

        signal_times = [item["signal_candle_time_utc"] for item in candidates]
        self.assertIn("2026-05-13T01:10:00Z", signal_times)
        self.assertFalse(
            "2026-05-13T00:35:00Z" in signal_times and "2026-05-13T00:38:00Z" in signal_times
        )


if __name__ == "__main__":
    unittest.main()
