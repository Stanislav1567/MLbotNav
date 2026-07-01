import csv
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mlbotnav.visual_entry_feature_audit import build_audit


class VisualEntryFeatureAuditTests(unittest.TestCase):
    def test_builds_feature_audit_from_core_csv(self):
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
                price = 100.0
                for i in range(90):
                    price -= 0.05 if i < 70 else -0.03
                    writer.writerow(
                        {
                            "open_time_utc": (start + timedelta(minutes=i)).isoformat(),
                            "open": price,
                            "high": price + 0.1,
                            "low": price - 0.1,
                            "close": price + (0.03 if i == 70 else 0.0),
                            "volume": 1000 + (2000 if i == 69 else 0),
                        }
                    )
            manual_entries = tmp_path / "manual_entries.json"
            manual_entries.write_text(
                json.dumps(
                    {
                        "source_images": [
                            {
                                "source_csv": str(core_csv),
                                "source_csv_sha256": "test",
                            }
                        ],
                        "entries": [
                            {
                                "entry_id": "ME_1",
                                "target_entry_time_utc": (start + timedelta(minutes=70)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            audit = build_audit(manual_entries)

        self.assertEqual(audit["entries_total"], 1)
        self.assertIn("entries", audit)
        self.assertIn("candidate_families", audit)


if __name__ == "__main__":
    unittest.main()
