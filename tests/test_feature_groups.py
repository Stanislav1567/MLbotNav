from __future__ import annotations

import unittest

from mlbotnav.dataset import FEATURE_COLUMNS, FEATURE_GROUPS


class FeatureGroupsTests(unittest.TestCase):
    def test_groups_cover_all_features(self) -> None:
        grouped = []
        for cols in FEATURE_GROUPS.values():
            grouped.extend(cols)
        self.assertEqual(set(grouped), set(FEATURE_COLUMNS))
        self.assertEqual(len(grouped), len(FEATURE_COLUMNS))


if __name__ == "__main__":
    unittest.main()

