import csv
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from mlbotnav.visual_entry_solo_passport_runner import PASSPORTS, run_search


class VisualEntrySoloPassportRunnerTests(unittest.TestCase):
    def test_runner_creates_reports_and_overlays(self):
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
                    price = 100.0 - min(i, 70) * 0.05 + max(0, i - 70) * 0.02
                    open_time = start + timedelta(minutes=i)
                    writer.writerow(
                        {
                            "open_time_utc": open_time.isoformat(),
                            "close_time_utc": (open_time + timedelta(minutes=1)).isoformat(),
                            "open": price,
                            "high": price + 0.1,
                            "low": price - 0.1,
                            "close": price,
                            "volume": 1000 + (1000 if i == 70 else 0),
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
                                "side": "long",
                                "target_entry_time_utc": (start + timedelta(minutes=71)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                "tolerance_bars_before": 2,
                                "tolerance_bars_after": 2,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            tiny_passports = {"F012_RSI14": PASSPORTS["F012_RSI14"]}
            tiny_passports["F012_RSI14"] = {
                **tiny_passports["F012_RSI14"],
                "grid": {
                    "F012_signal_mode": [1],
                    "F012_cmp": [-1],
                    "F012_level": [45],
                    "cooldown_bars": [20],
                },
            }
            with patch("mlbotnav.visual_entry_solo_passport_runner.PASSPORTS", tiny_passports):
                payload = run_search(manual_entries, tmp_path, render_top=1)

            self.assertIn("best_by_passport", payload)
            self.assertTrue((tmp_path / "visual_entry_solo_passport_runner_20260512_DEV.json").exists())


if __name__ == "__main__":
    unittest.main()
