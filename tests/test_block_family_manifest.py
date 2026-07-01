from __future__ import annotations

import unittest
from pathlib import Path

from mlbotnav.block_family_manifest import build_block_manifest


class BlockFamilyManifestTests(unittest.TestCase):
    def test_b001_manifest_uses_solo_family_rows_in_f_order(self) -> None:
        project_root = Path(__file__).resolve().parents[1]

        manifest = build_block_manifest(project_root=project_root, block_id="B001")

        self.assertEqual(manifest["mode"], "family_solo_selection")
        self.assertEqual(
            [row["passport_id"] for row in manifest["rows"]],
            ["F001", "F002", "F003", "F004", "F005"],
        )
        self.assertEqual(manifest["combination_policy"], "solo_f_selection_only")
        self.assertIn("B001_RET_N_TOURNAMENT", manifest["diagnostic_only_passports"])

    def test_b021_manifest_keeps_pattern_quality_family_together(self) -> None:
        project_root = Path(__file__).resolve().parents[1]

        manifest = build_block_manifest(project_root=project_root, block_id="B021")

        self.assertEqual(manifest["mode"], "family_solo_selection")
        self.assertEqual([row["passport_id"] for row in manifest["rows"]], ["F067", "F068"])
        self.assertEqual(
            [row["action_id"] for row in manifest["rows"]],
            ["F067_PATTERNSTRENGTH_ALLOW", "F068_PATTERNAGE_ALLOW"],
        )


if __name__ == "__main__":
    unittest.main()
