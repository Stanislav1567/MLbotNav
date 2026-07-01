import csv
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mlbotnav.visual_entry_prefilter_search import search


class VisualEntryPrefilterSearchTests(unittest.TestCase):
    def test_search_returns_top_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            core_csv = tmp_path / "part-final.csv"
            start = datetime(2026, 5, 12, tzinfo=timezone.utc)
            with core_csv.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=["open_time_utc", "open", "high", "low", "close", "volume"],
                )
                writer.writeheader()
                for i in range(120):
                    price = 100.0 - min(i, 70) * 0.05 + max(0, i - 70) * 0.02
                    writer.writerow(
                        {
                            "open_time_utc": (start + timedelta(minutes=i)).isoformat(),
                            "open": price,
                            "high": price + 0.1,
                            "low": price - 0.1,
                            "close": price,
                            "volume": 1000,
                        }
                    )
            manual_entries = tmp_path / "manual_entries.json"
            manual_entries.write_text(
                json.dumps(
                    {
                        "source_images": [{"source_csv": str(core_csv), "source_csv_sha256": "test"}],
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

            payload = search(manual_entries)

        self.assertGreaterEqual(payload["results_total"], 1)
        self.assertGreaterEqual(payload["top_results"][0]["score"]["target_hits"], 1)


if __name__ == "__main__":
    unittest.main()
