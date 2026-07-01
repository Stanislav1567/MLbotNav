from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mlbotnav.b001_ret_n_ladder_tournament import generate_family_unified_matrix, generate_tournament_matrices
from mlbotnav.optuna_search_candidate import _active_entry_action_columns_from_space
from mlbotnav.optuna_space import compile_optuna_space, load_calibration_matrix


class B001RetNLadderTournamentTests(unittest.TestCase):
    def test_generate_all_non_empty_ret_n_combinations(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=project_root / "tmp") as tmp:
            manifest = generate_tournament_matrices(
                project_root=project_root,
                output_dir=Path(tmp),
                grid_preset="wide",
            )

            self.assertEqual(int(manifest["combinations_count"]), 31)
            rows = list(manifest["rows"])
            self.assertEqual(len(rows), 31)
            self.assertEqual(rows[0]["passports"], ["F001"])
            self.assertEqual(rows[-1]["passports"], ["F001", "F002", "F003", "F004", "F005"])
            self.assertTrue((Path(tmp) / "manifest.json").exists())
            self.assertTrue((Path(tmp) / "manifest_RU.md").exists())

    def test_generated_combo_matrix_uses_subset_passport_policy(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=project_root / "tmp") as tmp:
            manifest = generate_tournament_matrices(
                project_root=project_root,
                output_dir=Path(tmp),
                grid_preset="wide",
            )
            pair = next(row for row in manifest["rows"] if row["passports"] == ["F001", "F005"])
            matrix = load_calibration_matrix(project_root, rel_path=str(pair["matrix_path"]))
            space = compile_optuna_space(matrix, contour_id="long_only", min_enabled_blocks=1, grid_preset="wide")

            self.assertEqual(space["passport_mode"]["registry_passport_id"], "B001_RET_N_TOURNAMENT")
            self.assertEqual(space["passport_mode"]["registry_allowlist_policy"], "subset_allowlist")
            self.assertEqual(
                set(space["profiles"].keys()),
                {
                    "F001_move",
                    "F001_thr_pct",
                    "F005_move",
                    "F005_thr_pct",
                    "entry_action_min_confirmations",
                },
            )
            self.assertEqual(
                _active_entry_action_columns_from_space(space),
                ["F001_RET1_ALLOW", "F005_RET24_ALLOW"],
            )

    def test_generate_family_unified_matrix_uses_one_family_move(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(dir=project_root / "tmp") as tmp:
            manifest = generate_family_unified_matrix(
                project_root=project_root,
                output_dir=Path(tmp),
                family_move_values=[1],
                strict_confirmations=5,
                grid_preset="wide",
            )
            matrix = load_calibration_matrix(project_root, rel_path=str(manifest["matrix_path"]))
            space = compile_optuna_space(matrix, contour_id="long_only", min_enabled_blocks=1, grid_preset="wide")
            profiles = set(space["profiles"].keys())

            self.assertIn("B001_family_move", profiles)
            self.assertIn("entry_action_min_confirmations", profiles)
            self.assertNotIn("F001_move", profiles)
            self.assertNotIn("F005_move", profiles)
            self.assertEqual(space["profiles"]["B001_family_move"]["values"], [1])
            self.assertEqual(space["profiles"]["entry_action_min_confirmations"]["values"], [5])
            self.assertEqual(
                _active_entry_action_columns_from_space(space),
                ["F001_RET1_ALLOW", "F002_RET3_ALLOW", "F003_RET6_ALLOW", "F004_RET12_ALLOW", "F005_RET24_ALLOW"],
            )


if __name__ == "__main__":
    unittest.main()
