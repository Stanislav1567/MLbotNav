import csv
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mlbotnav.render_visual_entry_overlay import render_overlay
from mlbotnav.visual_entry_score import TradeEntry, load_manual_entries


class RenderVisualEntryOverlayTests(unittest.TestCase):
    def test_renders_overlay_png(self):
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
                for i in range(80):
                    price = 100 + i * 0.01
                    writer.writerow(
                        {
                            "open_time_utc": (start + timedelta(minutes=i)).isoformat(),
                            "open": price,
                            "high": price + 0.05,
                            "low": price - 0.05,
                            "close": price + 0.01,
                            "volume": 1000,
                        }
                    )
            manual_path = tmp_path / "manual_entries.json"
            manual_path.write_text(
                json.dumps(
                    {
                        "symbol": "SOLUSDT",
                        "timeframe": "1m",
                        "source_images": [
                            {
                                "date_utc": "2026-05-12",
                                "source_csv": str(core_csv),
                            }
                        ],
                        "entries": [
                            {
                                "entry_id": "ME_20260512_0030_LONG_001",
                                "side": "long",
                                "target_entry_time_utc": "2026-05-12T00:30:00Z",
                                "tolerance_bars_before": 2,
                                "tolerance_bars_after": 2,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            _, manual_entries = load_manual_entries(manual_path)
            trades = [
                TradeEntry(
                    row_index=1,
                    side="long",
                    entry_time=manual_entries[0].target_time,
                    exit_time_raw="",
                    net_return=0.0,
                    mae_pct=None,
                    mfe_pct=None,
                )
            ]
            png_path, json_path = render_overlay(
                manual_entries_path=manual_path,
                trades=trades,
                label="test",
                out_dir=tmp_path,
            )

            self.assertTrue(png_path.exists())
            self.assertTrue(json_path.exists())
            self.assertGreater(png_path.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
