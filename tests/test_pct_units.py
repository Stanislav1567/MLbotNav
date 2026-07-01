from __future__ import annotations

import unittest

from mlbotnav.pct_units import normalize_min_expected_move_pct


class PctUnitsTests(unittest.TestCase):
    def test_fraction_is_preserved(self) -> None:
        self.assertAlmostEqual(normalize_min_expected_move_pct(0.01), 0.01, places=12)
        self.assertAlmostEqual(normalize_min_expected_move_pct(0.003), 0.003, places=12)

    def test_percent_points_are_converted_to_fraction(self) -> None:
        self.assertAlmostEqual(normalize_min_expected_move_pct(1.0), 0.01, places=12)
        self.assertAlmostEqual(normalize_min_expected_move_pct(2.5), 0.025, places=12)

    def test_negative_and_invalid_values(self) -> None:
        self.assertAlmostEqual(normalize_min_expected_move_pct(-1.0), 0.01, places=12)
        self.assertAlmostEqual(normalize_min_expected_move_pct("bad"), 0.0, places=12)


if __name__ == "__main__":
    unittest.main()

