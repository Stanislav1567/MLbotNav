import csv
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from mlbotnav.visual_entry_quality_filter_runner import run_search


class VisualEntryQualityFilterRunnerTests(unittest.TestCase):
    def test_runner_creates_quality_reports(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            core_csv = tmp_path / "part-final.csv"
            start = datetime(2026, 5, 12, tzinfo=timezone.utc)
            with core_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["open_time_utc", "close_time_utc", "open", "high", "low", "close", "volume"],
                )
                writer.writeheader()
                for i in range(120):
                    price = 100.0 - min(i, 80) * 0.05 + max(0, i - 80) * 0.03
                    open_time = start + timedelta(minutes=i)
                    low = price - (0.4 if i == 80 else 0.05)
                    close = price + (0.15 if i == 80 else 0.0)
                    writer.writerow(
                        {
                            "open_time_utc": open_time.isoformat(),
                            "close_time_utc": (open_time + timedelta(minutes=1)).isoformat(),
                            "open": price,
                            "high": max(price, close) + 0.05,
                            "low": low,
                            "close": close,
                            "volume": 1000 + (3000 if i == 80 else 0),
                        }
                    )

            manual_entries = tmp_path / "manual_entries.json"
            manual_entries.write_text(
                json.dumps(
                    {
                        "symbol": "SOLUSDT",
                        "timeframe": "1m",
                        "source_images": [{"date_utc": "2026-05-12", "source_csv": str(core_csv), "source_csv_sha256": "test"}],
                        "entries": [
                            {
                                "entry_id": "ME_1",
                                "entry_number": 1,
                                "side": "long",
                                "signal_candle_time_utc": (start + timedelta(minutes=80)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "target_entry_time_utc": (start + timedelta(minutes=81)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "entry_open_price": 96.0,
                                "entry_price_with_slippage": 96.048,
                                "tolerance_bars_before": 0,
                                "tolerance_bars_after": 0,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            variant = {
                "variant_id": "TEST_QUALITY",
                "local_low_bars": 5,
                "base_min_votes": 3,
                "quality_min_votes": 1,
                "cooldown_bars": 10,
                "wick_min": 0.25,
                "closepos_min": 0.45,
                "support_lowpos_max": 0.20,
                "support_dist_max_pct": 0.50,
                "support_touches_min": 1,
                "vol_z_min": 0.50,
                "dip_ret12_max": -0.10,
                "dip_ret24_max": -0.20,
                "osc_max": 60.0,
                "capitulation_votes_min": 1,
                "cluster_min_events": 1,
                "cluster_max_events": 10,
                "max_lower_low_streak": 5,
                "max_new_low_count_20": 10,
                "bad_slope_pct": -1.0,
            }
            with patch("mlbotnav.visual_entry_quality_filter_runner.QUALITY_VARIANTS", [variant]):
                payload = run_search(manual_entries, tmp_path, render_top=1)

            self.assertEqual(payload["status"], "DEV_QUALITY_FILTER_DIAGNOSTIC_NO_ML")
            self.assertTrue((tmp_path / "visual_entry_quality_filter_20260512_DEV.json").exists())
            self.assertTrue((tmp_path / "visual_entry_quality_filter_20260512_DEV_RU.md").exists())


if __name__ == "__main__":
    unittest.main()
