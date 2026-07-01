import csv
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mlbotnav.visual_entry_deep_capitulation_reclaim_runner import run_search


class VisualEntryDeepCapitulationReclaimRunnerTests(unittest.TestCase):
    def test_runner_creates_deep_capitulation_reports(self):
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
                for i in range(160):
                    base = 100.0 - min(i, 120) * 0.04
                    open_time = start + timedelta(minutes=i)
                    row = {
                        "open": base,
                        "high": base + 0.04,
                        "low": base - 0.04,
                        "close": base - 0.02,
                        "volume": 1000,
                    }
                    if i == 120:
                        row = {
                            "open": base,
                            "high": base + 0.08,
                            "low": base - 0.55,
                            "close": base - 0.03,
                            "volume": 900,
                        }
                    writer.writerow(
                        {
                            "open_time_utc": open_time.isoformat(),
                            "close_time_utc": (open_time + timedelta(minutes=1)).isoformat(),
                            **row,
                        }
                    )

            manual_entries = tmp_path / "manual_entries.json"
            manual_entries.write_text(
                json.dumps(
                    {
                        "symbol": "SOLUSDT",
                        "timeframe": "1m",
                        "source_images": [
                            {"date_utc": "2026-05-12", "source_csv": str(core_csv), "source_csv_sha256": "test"}
                        ],
                        "entries": [
                            {
                                "entry_id": "ME_1",
                                "entry_number": 1,
                                "side": "long",
                                "signal_candle_time_utc": (start + timedelta(minutes=120)).strftime(
                                    "%Y-%m-%dT%H:%M:%SZ"
                                ),
                                "target_entry_time_utc": (start + timedelta(minutes=121)).strftime(
                                    "%Y-%m-%dT%H:%M:%SZ"
                                ),
                                "entry_open_price": 95.0,
                                "entry_price_with_slippage": 95.0475,
                                "tolerance_bars_before": 0,
                                "tolerance_bars_after": 0,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            payload = run_search(manual_entries, tmp_path, render_top=1)

            self.assertEqual(payload["status"], "DEV_DEEP_CAPITULATION_RECLAIM_DIAGNOSTIC_NO_ML")
            self.assertTrue((tmp_path / "visual_entry_deep_capitulation_reclaim_20260512_DEV.json").exists())
            self.assertTrue((tmp_path / "visual_entry_deep_capitulation_reclaim_20260512_DEV_RU.md").exists())
            self.assertFalse(payload["ml_transfer_allowed"])


if __name__ == "__main__":
    unittest.main()
