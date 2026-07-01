import json
import tempfile
import unittest
from pathlib import Path

from mlbotnav.visual_entry_score import (
    load_manual_entries,
    load_trade_entries,
    score_entries,
)


class VisualEntryScoreTests(unittest.TestCase):
    def test_scores_hits_misses_false_entries_and_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manual_path = tmp_path / "manual_entries.json"
            trades_path = tmp_path / "trades.csv"
            manual_path.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "entry_id": "ME_1",
                                "side": "long",
                                "target_entry_time_utc": "2026-05-12T09:12:00Z",
                                "tolerance_bars_before": 2,
                                "tolerance_bars_after": 2,
                            },
                            {
                                "entry_id": "ME_2",
                                "side": "long",
                                "target_entry_time_utc": "2026-05-12T12:36:00Z",
                                "tolerance_bars_before": 2,
                                "tolerance_bars_after": 2,
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )
            trades_path.write_text(
                "\n".join(
                    [
                        "side,entry_time_utc,exit_time_utc,net_return,mae_pct,mfe_pct",
                        "1,2026-05-12T09:12:00+00:00,2026-05-12T09:16:00+00:00,0.01,-0.02,0.03",
                        "1,2026-05-12T09:13:00+00:00,2026-05-12T09:17:00+00:00,-0.02,-0.03,0.01",
                        "1,2026-05-12T14:00:00+00:00,2026-05-12T14:04:00+00:00,-0.03,-0.04,0.00",
                        "1,2026-05-12T15:00:00+00:00,2026-05-12T15:04:00+00:00,-0.01,-0.02,0.01",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            _, manual_entries = load_manual_entries(manual_path)
            trade_entries = load_trade_entries(trades_path)
            score = score_entries(manual_entries, trade_entries)

        self.assertEqual(score["targets_total"], 2)
        self.assertEqual(score["target_hits"], 1)
        self.assertEqual(score["missed_targets"], 1)
        self.assertEqual(score["false_entries"], 2)
        self.assertEqual(score["duplicate_hits"], 1)
        self.assertEqual(score["entries_total"], 4)
        self.assertAlmostEqual(score["recall"], 0.5)
        self.assertEqual(score["visual_status"], "VISUAL_HITS_WITH_TOO_MANY_FALSE_ENTRIES")


if __name__ == "__main__":
    unittest.main()
