from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mlbotnav.negative_memory import add_negative_event, build_fingerprint, is_fingerprint_blocked, summarize_negative_memory


class NegativeMemoryTests(unittest.TestCase):
    def test_reason_tags_and_summary(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            fp = build_fingerprint(params={"a": 1}, context={"b": 2})
            add_negative_event(
                root,
                fingerprint=fp,
                stage="D1",
                reason="rating_low:12;pipeline_gate_not_passed",
                params={"a": 1},
                context={"b": 2},
                cooldown_hours=48,
            )
            blocked, meta = is_fingerprint_blocked(root, fingerprint=fp)
            self.assertTrue(blocked)
            self.assertIn("cooldown_remaining_hours", meta or {})
            self.assertIn("reason_tags", meta or {})
            summary = summarize_negative_memory(root, stage="D1")
            self.assertEqual(summary["rows_total"], 1)
            self.assertEqual(summary["active_blocks"], 1)
            self.assertIn("rating_low", summary["reason_tag_counts"])


if __name__ == "__main__":
    unittest.main()

