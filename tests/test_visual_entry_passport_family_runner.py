import csv
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from mlbotnav.visual_entry_passport_family_runner import FamilySpec, action, run_search


class VisualEntryPassportFamilyRunnerTests(unittest.TestCase):
    def test_runner_creates_family_reports(self):
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
                    price = 100.0 - min(i, 80) * 0.06 + max(0, i - 80) * 0.03
                    open_time = start + timedelta(minutes=i)
                    writer.writerow(
                        {
                            "open_time_utc": open_time.isoformat(),
                            "close_time_utc": (open_time + timedelta(minutes=1)).isoformat(),
                            "open": price,
                            "high": price + 0.05,
                            "low": price - 0.05,
                            "close": price,
                            "volume": 1000 + (2000 if i == 80 else 0),
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
                                "entry_open_price": 95.2,
                                "entry_price_with_slippage": 95.2476,
                                "tolerance_bars_before": 0,
                                "tolerance_bars_after": 0,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            tiny_family = FamilySpec(
                family_id="TEST_RSI_NEXT_OPEN",
                description_ru="test",
                param_grid={
                    "F012_signal_mode": [1],
                    "F012_cmp": [-1],
                    "F012_level": [40],
                    "min_context_votes": [1],
                    "min_trigger_votes": [1],
                    "min_confirm_votes": [0],
                    "cooldown_bars": [20],
                },
                context=(action("F012_RSI14_ALLOW"),),
                trigger=(action("F012_RSI14_ALLOW"),),
            )
            with patch("mlbotnav.visual_entry_passport_family_runner.FAMILY_SPECS", [tiny_family]):
                payload = run_search(manual_entries, tmp_path, render_top=1)

            self.assertEqual(payload["status"], "DEV_PASSPORT_FAMILY_DIAGNOSTIC_NO_ML")
            self.assertTrue((tmp_path / "visual_entry_passport_family_runner_20260512_DEV.json").exists())
            self.assertTrue((tmp_path / "visual_entry_passport_family_runner_20260512_DEV_RU.md").exists())


if __name__ == "__main__":
    unittest.main()
