from __future__ import annotations

import unittest

from mlbotnav.stage_ladder import _date_window, _days_by_stage


class StageLadderHelperTests(unittest.TestCase):
    def test_days_by_stage_defaults(self) -> None:
        d = _days_by_stage({})
        self.assertEqual(d["D1"], 1)
        self.assertEqual(d["D30"], 30)

    def test_date_window(self) -> None:
        start, end = _date_window("2026-05-21", days=3)
        self.assertEqual(end, "2026-05-21")
        self.assertEqual(start, "2026-05-19")


if __name__ == "__main__":
    unittest.main()

