from __future__ import annotations

import copy
import unittest
from pathlib import Path

from mlbotnav.optuna_space import (
    OptunaSpaceCompileError,
    compile_optuna_space,
    evaluate_runtime_constraints,
    evaluate_runtime_constraints_detailed,
    expand_profile_values,
    load_calibration_matrix,
)


class OptunaSpaceConstraintsTests(unittest.TestCase):
    def test_compile_space_from_matrix(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        matrix = load_calibration_matrix(project_root)
        space = compile_optuna_space(matrix, contour_id="long_only", min_enabled_blocks=1)

        self.assertGreaterEqual(len(space["enabled_blocks"]), 1)
        self.assertGreater(len(space["feature_rows"]), 0)
        self.assertGreater(len(space["hypothesis_rows"]), 0)
        self.assertIn("p_short < p_long", space["constraints"])

    def test_profiles_have_values(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        matrix = load_calibration_matrix(project_root)
        space = compile_optuna_space(matrix, contour_id="long_only", min_enabled_blocks=1)
        for name, profile in space["profiles"].items():
            values = profile.get("values") or []
            self.assertGreater(len(values), 0, msg=f"profile '{name}' has empty values")

    def test_explicit_profile_values_are_preserved(self) -> None:
        values = expand_profile_values(
            {
                "min": 0.236,
                "max": 0.786,
                "step": 0.146,
                "values": [0.236, 0.382, 0.5, 0.618, 0.786],
            }
        )
        self.assertEqual(values, [0.236, 0.382, 0.5, 0.618, 0.786])

    def test_profile_range_preserves_max_anchor_when_step_misses_max(self) -> None:
        values = expand_profile_values({"min": 0.03, "max": 1.20, "step": 0.02, "count": 60})
        self.assertEqual(values[0], 0.03)
        self.assertEqual(values[-1], 1.20)
        self.assertIn(1.20, values)
        self.assertEqual(len(values), 60)

    def test_profile_count_truncation_keeps_max_anchor(self) -> None:
        values = expand_profile_values({"min": 0.0, "max": 1.0, "step": 0.1, "count": 5})
        self.assertEqual(values, [0.0, 0.1, 0.2, 0.3, 1.0])

    def test_hypothesis_rows_respect_contour_direction(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        matrix = load_calibration_matrix(project_root)
        long_space = compile_optuna_space(matrix, contour_id="long_only", min_enabled_blocks=1)
        short_space = compile_optuna_space(matrix, contour_id="short_only", min_enabled_blocks=1)
        long_names = {str(x.get("hypothesis", "")).strip() for x in long_space["hypothesis_rows"]}
        short_names = {str(x.get("hypothesis", "")).strip() for x in short_space["hypothesis_rows"]}

        self.assertNotIn("swing_lh_ll_short", long_names)
        self.assertNotIn("swing_hl_hh_long", short_names)
        self.assertNotIn("ema_stack_bull", short_names)
        self.assertIn("none", long_names)
        self.assertIn("none", short_names)

    def test_context_blocks_are_always_on_features_not_primary_blocks(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        matrix = copy.deepcopy(load_calibration_matrix(project_root))
        block_switches = matrix["optuna_switches"]["block_switches"]
        for block in list(block_switches.keys()):
            block_switches[block] = block == "structure_ta"
        matrix["optuna_switches"]["context_blocks"] = {
            "enabled": True,
            "always_on": ["volume_flow", "price_volatility"],
        }

        space = compile_optuna_space(matrix, contour_id="long_only", min_enabled_blocks=1)
        row_blocks = {str(row.get("block", "")).strip() for row in space["feature_rows"]}
        row_features = {str(row.get("feature", "")).strip() for row in space["feature_rows"]}

        self.assertEqual(space["enabled_blocks"], ["structure_ta"])
        self.assertEqual(space["context_blocks"], ["volume_flow", "price_volatility"])
        self.assertIn("structure_ta", space["effective_feature_blocks"])
        self.assertIn("volume_flow", space["effective_feature_blocks"])
        self.assertIn("price_volatility", space["effective_feature_blocks"])
        self.assertIn("structure_ta", row_blocks)
        self.assertIn("volume_flow", row_blocks)
        self.assertIn("price_volatility", row_blocks)
        self.assertIn("mfi14", row_features)
        self.assertIn("ret_1", row_features)

    def test_pattern_block_compiles_figure_entry_profiles(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        matrix = load_calibration_matrix(
            project_root,
            rel_path="configs/calibration_matrices/catalog_blocks/catalog_block_06_pattern.yaml",
        )
        space = compile_optuna_space(matrix, contour_id="long_only", min_enabled_blocks=1, grid_preset="wide")
        row_features = {str(row.get("feature", "")).strip() for row in space["feature_rows"]}
        profiles = set(space["profiles"].keys())

        self.assertIn("pattern_structure_volume_entry_long", row_features)
        self.assertIn("pattern_structure_volume_entry_short", row_features)
        for name in (
            "pattern_window",
            "min_touches",
            "breakout_threshold",
            "retest_window",
            "level_distance_threshold",
            "volume_confirm_threshold",
            "vol_z_window",
            "sl_buffer",
            "tp_ladder",
        ):
            self.assertIn(name, profiles)

    def test_passport_action_matrix_allows_only_passport_params(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        cases = [
            ("F001", "configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml"),
            ("F002", "configs/calibration_matrices/passport_actions/F002_ret3_entry_filter.yaml"),
            ("F003", "configs/calibration_matrices/passport_actions/F003_ret6_entry_filter.yaml"),
            ("F004", "configs/calibration_matrices/passport_actions/F004_ret12_entry_filter.yaml"),
            ("F005", "configs/calibration_matrices/passport_actions/F005_ret24_entry_filter.yaml"),
        ]
        for passport_id, rel_path in cases:
            with self.subTest(passport_id=passport_id):
                matrix = load_calibration_matrix(project_root, rel_path=rel_path)
                space = compile_optuna_space(matrix, contour_id="long_only", min_enabled_blocks=1, grid_preset="wide")

                self.assertTrue(space["passport_mode"]["enabled"])
                self.assertEqual(space["passport_mode"]["action_passport_id"], passport_id)
                self.assertEqual(space["passport_mode"]["registry_block_id"], "B001")
                self.assertEqual(space["passport_mode"]["registry_passport_id"], passport_id)
                self.assertEqual(set(space["profiles"].keys()), {f"{passport_id}_move", f"{passport_id}_thr_pct"})

        matrix = load_calibration_matrix(
            project_root,
            rel_path="configs/calibration_matrices/passport_actions/F006_hl_spread_1m_entry_filter.yaml",
        )
        space = compile_optuna_space(matrix, contour_id="long_only", min_enabled_blocks=1, grid_preset="wide")
        self.assertTrue(space["passport_mode"]["enabled"])
        self.assertEqual(space["passport_mode"]["action_passport_id"], "F006")
        self.assertEqual(space["passport_mode"]["registry_block_id"], "B002")
        self.assertEqual(space["passport_mode"]["registry_passport_id"], "F006")
        self.assertEqual(set(space["profiles"].keys()), {"F006_cmp", "F006_thr_pct"})

        matrix = load_calibration_matrix(
            project_root,
            rel_path="configs/calibration_matrices/passport_actions/F007_rolling_std20_1m_entry_filter.yaml",
        )
        space = compile_optuna_space(matrix, contour_id="long_only", min_enabled_blocks=1, grid_preset="wide")
        self.assertTrue(space["passport_mode"]["enabled"])
        self.assertEqual(space["passport_mode"]["action_passport_id"], "F007")
        self.assertEqual(space["passport_mode"]["registry_block_id"], "B003")
        self.assertEqual(space["passport_mode"]["registry_passport_id"], "F007")
        self.assertEqual(set(space["profiles"].keys()), {"F007_cmp", "F007_thr_pct"})

        matrix = load_calibration_matrix(
            project_root,
            rel_path="configs/calibration_matrices/passport_actions/F008_atr14_1m_entry_filter.yaml",
        )
        space = compile_optuna_space(matrix, contour_id="long_only", min_enabled_blocks=1, grid_preset="wide")
        self.assertTrue(space["passport_mode"]["enabled"])
        self.assertEqual(space["passport_mode"]["action_passport_id"], "F008")
        self.assertEqual(space["passport_mode"]["registry_block_id"], "B004")
        self.assertEqual(space["passport_mode"]["registry_passport_id"], "F008")
        self.assertEqual(set(space["profiles"].keys()), {"F008_cmp", "F008_thr_pct"})

        for rel_path, passport_id, expected_profiles in [
            (
                "configs/calibration_matrices/passport_actions/F009_ema_gap_20_50_1m_entry_filter.yaml",
                "F009",
                {"F009_bias", "F009_thr_pct"},
            ),
            (
                "configs/calibration_matrices/passport_actions/F010_ema20_slope_5_1m_entry_filter.yaml",
                "F010",
                {"F010_slope", "F010_thr_pct"},
            ),
            (
                "configs/calibration_matrices/passport_actions/F011_ema200_gap_1m_entry_filter.yaml",
                "F011",
                {"F011_position", "F011_thr_pct"},
            ),
        ]:
            matrix = load_calibration_matrix(project_root, rel_path=rel_path)
            space = compile_optuna_space(matrix, contour_id="long_only", min_enabled_blocks=1, grid_preset="wide")
            self.assertTrue(space["passport_mode"]["enabled"])
            self.assertEqual(space["passport_mode"]["action_passport_id"], passport_id)
            self.assertEqual(space["passport_mode"]["registry_block_id"], "B005")
            self.assertEqual(space["passport_mode"]["registry_passport_id"], passport_id)
            self.assertEqual(set(space["profiles"].keys()), expected_profiles)

        matrix = load_calibration_matrix(
            project_root,
            rel_path="configs/calibration_matrices/passport_actions/F012_rsi14_combined_entry_filter.yaml",
        )
        space = compile_optuna_space(matrix, contour_id="long_only", min_enabled_blocks=1, grid_preset="wide")
        self.assertTrue(space["passport_mode"]["enabled"])
        self.assertEqual(space["passport_mode"]["action_passport_id"], "F012")
        self.assertEqual(space["passport_mode"]["registry_block_id"], "B006")
        self.assertEqual(space["passport_mode"]["registry_passport_id"], "F012")
        self.assertEqual(
            set(space["profiles"].keys()),
            {"F012_signal_mode", "F012_cmp", "F012_level", "F012_relation", "F012_gap"},
        )

        for rel_path, passport_id, expected_profiles, expected_block_id in [
            (
                "configs/calibration_matrices/passport_actions/F013_macd_line_1m_entry_filter.yaml",
                "F013",
                {"F013_state", "F013_thr_pct"},
                "B007",
            ),
            (
                "configs/calibration_matrices/passport_actions/F014_macd_signal_1m_entry_filter.yaml",
                "F014",
                {"F014_state", "F014_thr_pct"},
                "B007",
            ),
            (
                "configs/calibration_matrices/passport_actions/F015_macd_hist_1m_entry_filter.yaml",
                "F015",
                {"F015_state", "F015_thr_pct"},
                "B007",
            ),
            (
                "configs/calibration_matrices/passport_actions/F016_adx14_1m_entry_filter.yaml",
                "F016",
                {"F016_cmp", "F016_level"},
                "B008",
            ),
            (
                "configs/calibration_matrices/passport_actions/F017_F018_stoch14_combined_entry_filter.yaml",
                "F017_F018",
                {
                    "F017_F018_signal_mode",
                    "F017_F018_line",
                    "F017_F018_cmp",
                    "F017_F018_level",
                    "F017_F018_cross_dir",
                    "F017_F018_zone_filter",
                    "F017_F018_low_level",
                    "F017_F018_high_level",
                    "F017_F018_gap",
                },
                "B009",
            ),
            (
                "configs/calibration_matrices/passport_actions/F019_vol_chg_1m_entry_filter.yaml",
                "F019",
                {"F019_direction", "F019_thr_pct"},
                "B010",
            ),
            (
                "configs/calibration_matrices/passport_actions/F020_vol_z20_1m_entry_filter.yaml",
                "F020",
                {"F020_state", "F020_z_level"},
                "B010",
            ),
            (
                "configs/calibration_matrices/passport_actions/F021_delta_volume_1m_entry_filter.yaml",
                "F021",
                {"F021_delta_mode", "F021_pressure", "F021_delta_thr"},
                "B010",
            ),
            (
                "configs/calibration_matrices/passport_actions/F022_obv_slope5_1m_entry_filter.yaml",
                "F022",
                {"F022_slope_dir", "F022_slope_thr"},
                "B011",
            ),
            (
                "configs/calibration_matrices/passport_actions/F023_mfi14_1m_combined_entry_filter.yaml",
                "F023",
                {"F023_signal_mode", "F023_cmp", "F023_level", "F023_cross_dir", "F023_cross_level"},
                "B012",
            ),
            (
                "configs/calibration_matrices/passport_actions/F024_vwapdist_entry_filter.yaml",
                "F024",
                {"F024_signal_mode", "F024_side_state", "F024_distance_state", "F024_dist_thr_pct"},
                "B026",
            ),
            (
                "configs/calibration_matrices/passport_actions/F025_vpocdist60_entry_filter.yaml",
                "F025",
                {"F025_signal_mode", "F025_side_state", "F025_distance_state", "F025_dist_thr_pct"},
                "B013",
            ),
            (
                "configs/calibration_matrices/passport_actions/F026_binshare60_entry_filter.yaml",
                "F026",
                {"F026_cmp", "F026_share_thr_pct"},
                "B013",
            ),
            (
                "configs/calibration_matrices/passport_actions/F027_clustershare60_entry_filter.yaml",
                "F027",
                {"F027_cmp", "F027_share_thr_pct"},
                "B013",
            ),
            (
                "configs/calibration_matrices/passport_actions/F028_vpocshare60_entry_filter.yaml",
                "F028",
                {"F028_cmp", "F028_share_thr_pct"},
                "B013",
            ),
            (
                "configs/calibration_matrices/passport_actions/F029_vpocdist240_entry_filter.yaml",
                "F029",
                {"F029_signal_mode", "F029_side_state", "F029_distance_state", "F029_dist_thr_pct"},
                "B013",
            ),
            (
                "configs/calibration_matrices/passport_actions/F030_binshare240_entry_filter.yaml",
                "F030",
                {"F030_cmp", "F030_share_thr_pct"},
                "B013",
            ),
            (
                "configs/calibration_matrices/passport_actions/F031_clustershare240_entry_filter.yaml",
                "F031",
                {"F031_cmp", "F031_share_thr_pct"},
                "B013",
            ),
            (
                "configs/calibration_matrices/passport_actions/F032_vpocshare240_entry_filter.yaml",
                "F032",
                {"F032_cmp", "F032_share_thr_pct"},
                "B013",
            ),
            (
                "configs/calibration_matrices/passport_actions/F033_vpocdrift20_entry_filter.yaml",
                "F033",
                {"F033_drift_dir", "F033_drift_thr_pct"},
                "B013",
            ),
            (
                "configs/calibration_matrices/passport_actions/F034_clusterratio_entry_filter.yaml",
                "F034",
                {"F034_cmp", "F034_ratio_level"},
                "B013",
            ),
            (
                "configs/calibration_matrices/passport_actions/F035_supportdist_entry_filter.yaml",
                "F035",
                {"F035_distance_state", "F035_dist_thr_pct"},
                "B014",
            ),
            (
                "configs/calibration_matrices/passport_actions/F036_resdist_entry_filter.yaml",
                "F036",
                {"F036_distance_state", "F036_dist_thr_pct"},
                "B014",
            ),
            (
                "configs/calibration_matrices/passport_actions/F037_levelstrength_entry_filter.yaml",
                "F037",
                {"F037_level_type", "F037_strength_state", "F037_strength_thr"},
                "B014",
            ),
            (
                "configs/calibration_matrices/passport_actions/F038_rangepose_entry_filter.yaml",
                "F038",
                {"F038_zone", "F038_level"},
                "B014",
            ),
            (
                "configs/calibration_matrices/passport_actions/F039_channelpos_entry_filter.yaml",
                "F039",
                {"F039_zone", "F039_level", "F039_outside_thr"},
                "B014",
            ),
            (
                "configs/calibration_matrices/passport_actions/F040_fib0382dist_entry_filter.yaml",
                "F040",
                {"F040_signal_mode", "F040_side_state", "F040_distance_state", "F040_dist_thr_pct"},
                "B015",
            ),
            (
                "configs/calibration_matrices/passport_actions/F041_fib0618dist_entry_filter.yaml",
                "F041",
                {"F041_signal_mode", "F041_side_state", "F041_distance_state", "F041_dist_thr_pct"},
                "B015",
            ),
            (
                "configs/calibration_matrices/passport_actions/F042_tpcontext_entry_filter.yaml",
                "F042",
                {"F042_level_source_mode", "F042_cmp", "F042_tp_dist_thr_pct"},
                "B016",
            ),
            (
                "configs/calibration_matrices/passport_actions/F043_slcontext_entry_filter.yaml",
                "F043",
                {"F043_level_source_mode", "F043_cmp", "F043_sl_dist_thr_pct"},
                "B016",
            ),
            (
                "configs/calibration_matrices/passport_actions/F044_rrcontext_entry_filter.yaml",
                "F044",
                {"F044_level_source_mode", "F044_rr_state", "F044_rr_level"},
                "B016",
            ),
            (
                "configs/calibration_matrices/passport_actions/F048_swinghighbreak_entry_filter.yaml",
                "F048",
                {"F048_break_buffer_pct", "F048_confirm_bars"},
                "B017",
            ),
            (
                "configs/calibration_matrices/passport_actions/F049_swinglowbreak_entry_filter.yaml",
                "F049",
                {"F049_break_buffer_pct", "F049_confirm_bars"},
                "B017",
            ),
            (
                "configs/calibration_matrices/passport_actions/F045_breakout_entry_filter.yaml",
                "F045",
                {"F045_level_source_mode", "F045_break_dir", "F045_break_buffer_pct", "F045_confirm_bars"},
                "B017",
            ),
            (
                "configs/calibration_matrices/passport_actions/F047_retest_entry_filter.yaml",
                "F047",
                {
                    "F047_level_source_mode",
                    "F047_break_dir",
                    "F047_retest_window_bars",
                    "F047_retest_tolerance_pct",
                    "F047_reaction_confirm_pct",
                },
                "B017",
            ),
            (
                "configs/calibration_matrices/passport_actions/F046_falsebreak_entry_filter.yaml",
                "F046",
                {
                    "F046_level_source_mode",
                    "F046_break_dir",
                    "F046_false_mode",
                    "F046_break_buffer_pct",
                    "F046_return_window_bars",
                    "F046_return_tolerance_pct",
                },
                "B017",
            ),
            (
                "configs/calibration_matrices/passport_actions/F050_bosup_entry_filter.yaml",
                "F050",
                {"F050_structure_scope", "F050_break_buffer_pct", "F050_confirm_bars", "F050_require_bias"},
                "B018",
            ),
            (
                "configs/calibration_matrices/passport_actions/F051_bosdown_entry_filter.yaml",
                "F051",
                {"F051_structure_scope", "F051_break_buffer_pct", "F051_confirm_bars", "F051_require_bias"},
                "B018",
            ),
            (
                "configs/calibration_matrices/passport_actions/F052_choch_entry_filter.yaml",
                "F052",
                {
                    "F052_structure_scope",
                    "F052_choch_dir",
                    "F052_break_buffer_pct",
                    "F052_confirm_bars",
                    "F052_require_opposite_bias",
                },
                "B018",
            ),
            (
                "configs/calibration_matrices/passport_actions/F055_pinbull_entry_filter.yaml",
                "F055",
                {
                    "F055_wick_body_ratio",
                    "F055_wick_min_pct",
                    "F055_opposite_wick_max_pct",
                    "F055_body_zone_pct",
                    "F055_min_range_pct",
                },
                "B019",
            ),
            (
                "configs/calibration_matrices/passport_actions/F056_pinbear_entry_filter.yaml",
                "F056",
                {
                    "F056_wick_body_ratio",
                    "F056_wick_min_pct",
                    "F056_opposite_wick_max_pct",
                    "F056_body_zone_pct",
                    "F056_min_range_pct",
                },
                "B019",
            ),
            (
                "configs/calibration_matrices/passport_actions/F059_engulfbull_entry_filter.yaml",
                "F059",
                {
                    "F059_engulf_mode",
                    "F059_min_engulf_ratio",
                    "F059_min_body_pct",
                    "F059_trend_lookback_bars",
                    "F059_trend_min_drop_pct",
                },
                "B019",
            ),
            (
                "configs/calibration_matrices/passport_actions/F060_engulfbear_entry_filter.yaml",
                "F060",
                {
                    "F060_engulf_mode",
                    "F060_min_engulf_ratio",
                    "F060_min_body_pct",
                    "F060_trend_lookback_bars",
                    "F060_trend_min_rise_pct",
                },
                "B019",
            ),
            (
                "configs/calibration_matrices/passport_actions/F057_hammer_entry_filter.yaml",
                "F057",
                {
                    "F057_wick_body_ratio",
                    "F057_lower_wick_min_pct",
                    "F057_upper_wick_max_pct",
                    "F057_body_zone_pct",
                    "F057_trend_lookback_bars",
                    "F057_trend_min_drop_pct",
                },
                "B019",
            ),
            (
                "configs/calibration_matrices/passport_actions/F058_shootingstar_entry_filter.yaml",
                "F058",
                {
                    "F058_wick_body_ratio",
                    "F058_upper_wick_min_pct",
                    "F058_lower_wick_max_pct",
                    "F058_body_zone_pct",
                    "F058_trend_lookback_bars",
                    "F058_trend_min_rise_pct",
                },
                "B019",
            ),
            (
                "configs/calibration_matrices/passport_actions/F054_insidebar_entry_filter.yaml",
                "F054",
                {"F054_containment_mode", "F054_max_inside_range_ratio", "F054_mother_min_range_pct"},
                "B019",
            ),
            (
                "configs/calibration_matrices/passport_actions/F053_doji_entry_filter.yaml",
                "F053",
                {"F053_max_body_pct", "F053_min_range_pct", "F053_wick_mode", "F053_wick_balance_max_pct"},
                "B019",
            ),
            (
                "configs/calibration_matrices/passport_actions/F061_rsibulldiv_entry_filter.yaml",
                "F061",
                {
                    "F061_pivot_scope",
                    "F061_div_type",
                    "F061_price_delta_min_pct",
                    "F061_rsi_delta_min",
                    "F061_max_pivot_gap_bars",
                    "F061_confirm_mode",
                    "F061_reaction_confirm_pct",
                },
                "B020",
            ),
            (
                "configs/calibration_matrices/passport_actions/F062_rsibeardiv_entry_filter.yaml",
                "F062",
                {
                    "F062_pivot_scope",
                    "F062_div_type",
                    "F062_price_delta_min_pct",
                    "F062_rsi_delta_min",
                    "F062_max_pivot_gap_bars",
                    "F062_confirm_mode",
                    "F062_reaction_confirm_pct",
                },
                "B020",
            ),
            (
                "configs/calibration_matrices/passport_actions/F063_macdbulldiv_entry_filter.yaml",
                "F063",
                {
                    "F063_pivot_scope",
                    "F063_div_type",
                    "F063_macd_component",
                    "F063_price_delta_min_pct",
                    "F063_macd_delta_min_pct",
                    "F063_max_pivot_gap_bars",
                    "F063_confirm_mode",
                    "F063_reaction_confirm_pct",
                },
                "B020",
            ),
            (
                "configs/calibration_matrices/passport_actions/F064_macdbeardiv_entry_filter.yaml",
                "F064",
                {
                    "F064_pivot_scope",
                    "F064_div_type",
                    "F064_macd_component",
                    "F064_price_delta_min_pct",
                    "F064_macd_delta_min_pct",
                    "F064_max_pivot_gap_bars",
                    "F064_confirm_mode",
                    "F064_reaction_confirm_pct",
                },
                "B020",
            ),
            (
                "configs/calibration_matrices/passport_actions/F065_obvbulldiv_entry_filter.yaml",
                "F065",
                {
                    "F065_pivot_scope",
                    "F065_div_type",
                    "F065_price_delta_min_pct",
                    "F065_obv_delta_min_norm",
                    "F065_max_pivot_gap_bars",
                    "F065_confirm_mode",
                    "F065_reaction_confirm_pct",
                },
                "B020",
            ),
            (
                "configs/calibration_matrices/passport_actions/F066_obvbeardiv_entry_filter.yaml",
                "F066",
                {
                    "F066_pivot_scope",
                    "F066_div_type",
                    "F066_price_delta_min_pct",
                    "F066_obv_delta_min_norm",
                    "F066_max_pivot_gap_bars",
                    "F066_confirm_mode",
                    "F066_reaction_confirm_pct",
                },
                "B020",
            ),
            (
                "configs/calibration_matrices/passport_actions/F067_patternstrength_entry_filter.yaml",
                "F067",
                {
                    "F067_strength_state",
                    "F067_strength_thr",
                    "F067_require_confirmation",
                    "F067_require_context",
                },
                "B021",
            ),
            (
                "configs/calibration_matrices/passport_actions/F068_patternage_entry_filter.yaml",
                "F068",
                {
                    "F068_age_mode",
                    "F068_min_age_bars",
                    "F068_max_age_bars",
                },
                "B021",
            ),
            (
                "configs/calibration_matrices/passport_actions/F069_doublebottom_entry_filter.yaml",
                "F069",
                {"F069_bottom_tolerance_pct", "F069_min_separation_bars", "F069_neckline_break_required", "F069_break_buffer_pct", "F069_max_pattern_age_bars"},
                "B022",
            ),
            (
                "configs/calibration_matrices/passport_actions/F070_doubletop_entry_filter.yaml",
                "F070",
                {"F070_top_tolerance_pct", "F070_min_separation_bars", "F070_neckline_break_required", "F070_break_buffer_pct", "F070_max_pattern_age_bars"},
                "B022",
            ),
            (
                "configs/calibration_matrices/passport_actions/F071_headshoulders_entry_filter.yaml",
                "F071",
                {"F071_shoulder_tolerance_pct", "F071_head_min_excess_pct", "F071_neckline_break_required", "F071_break_buffer_pct", "F071_max_pattern_age_bars"},
                "B022",
            ),
            (
                "configs/calibration_matrices/passport_actions/F072_invheadshoulders_entry_filter.yaml",
                "F072",
                {"F072_shoulder_tolerance_pct", "F072_head_min_excess_pct", "F072_neckline_break_required", "F072_break_buffer_pct", "F072_max_pattern_age_bars"},
                "B022",
            ),
            (
                "configs/calibration_matrices/passport_actions/F073_triangle_entry_filter.yaml",
                "F073",
                {"F073_triangle_type", "F073_min_touches", "F073_convergence_min_pct", "F073_breakout_required", "F073_break_dir", "F073_break_buffer_pct"},
                "B022",
            ),
            (
                "configs/calibration_matrices/passport_actions/F074_pennant_entry_filter.yaml",
                "F074",
                {"F074_impulse_dir", "F074_impulse_min_pct", "F074_consolidation_bars", "F074_compression_min_pct", "F074_breakout_required", "F074_break_buffer_pct"},
                "B022",
            ),
            (
                "configs/calibration_matrices/passport_actions/F075_wedgerising_entry_filter.yaml",
                "F075",
                {"F075_min_touches", "F075_convergence_min_pct", "F075_breakout_required", "F075_break_dir", "F075_break_buffer_pct"},
                "B022",
            ),
            (
                "configs/calibration_matrices/passport_actions/F076_wedgefalling_entry_filter.yaml",
                "F076",
                {"F076_min_touches", "F076_convergence_min_pct", "F076_breakout_required", "F076_break_dir", "F076_break_buffer_pct"},
                "B022",
            ),
            (
                "configs/calibration_matrices/passport_actions/F077_rangeflag_entry_filter.yaml",
                "F077",
                {"F077_range_lookback", "F077_max_range_pct", "F077_min_touches_high", "F077_min_touches_low", "F077_range_pos_mode", "F077_range_pos_level"},
                "B022",
            ),
            (
                "configs/calibration_matrices/passport_actions/F079_patternlevelconf_entry_filter.yaml",
                "F079",
                {
                    "F079_level_source_mode",
                    "F079_confirm_type",
                    "F079_dist_thr_pct",
                    "F079_reaction_confirm_pct",
                    "F079_direction_filter",
                },
                "B023",
            ),
            (
                "configs/calibration_matrices/passport_actions/F078_patternvolconf_entry_filter.yaml",
                "F078",
                {
                    "F078_confirm_mode",
                    "F078_ratio_thr",
                    "F078_z_thr",
                    "F078_confirm_bar_mode",
                    "F078_direction_filter",
                },
                "B023",
            ),
            (
                "configs/calibration_matrices/passport_actions/F080_patternlong_entry_filter.yaml",
                "F080",
                {
                    "F080_pattern_family_filter",
                    "F080_direction_mode",
                    "F080_logic_mode",
                    "F080_use_strength",
                    "F080_use_age",
                    "F080_use_volume_confirm",
                    "F080_use_level_confirm",
                    "F080_structure_filter",
                    "F080_breakout_filter",
                    "F080_min_score",
                    "F080_block_opposite_pattern",
                },
                "B024",
            ),
            (
                "configs/calibration_matrices/passport_actions/F081_patternshort_entry_filter.yaml",
                "F081",
                {
                    "F081_pattern_family_filter",
                    "F081_direction_mode",
                    "F081_logic_mode",
                    "F081_use_strength",
                    "F081_use_age",
                    "F081_use_volume_confirm",
                    "F081_use_level_confirm",
                    "F081_structure_filter",
                    "F081_breakout_filter",
                    "F081_min_score",
                    "F081_block_opposite_pattern",
                },
                "B024",
            ),
            (
                "configs/calibration_matrices/passport_actions/F082_patternslbuf_entry_filter.yaml",
                "F082",
                {
                    "F082_sl_anchor_mode",
                    "F082_buffer_mode",
                    "F082_buffer_pct",
                    "F082_atr_mult",
                    "F082_range_mult",
                    "F082_sl_distance_mode",
                    "F082_min_sl_dist_pct",
                    "F082_max_sl_dist_pct",
                },
                "B025",
            ),
            (
                "configs/calibration_matrices/passport_actions/F083_patterntpladder_entry_filter.yaml",
                "F083",
                {
                    "F083_target_source_mode",
                    "F083_min_targets",
                    "F083_min_rr_to_target",
                    "F083_target_spacing_min_pct",
                    "F083_require_clear_path",
                    "F083_ladder_state",
                    "F083_ladder_score_thr",
                },
                "B025",
            ),
        ]:
            matrix = load_calibration_matrix(project_root, rel_path=rel_path)
            space = compile_optuna_space(matrix, contour_id="long_only", min_enabled_blocks=1, grid_preset="wide")
            self.assertTrue(space["passport_mode"]["enabled"])
            self.assertEqual(space["passport_mode"]["action_passport_id"], passport_id)
            self.assertEqual(space["passport_mode"]["registry_block_id"], expected_block_id)
            self.assertEqual(space["passport_mode"]["registry_passport_id"], passport_id)
            self.assertEqual(set(space["profiles"].keys()), expected_profiles)

    def test_passport_action_matrix_rejects_registry_action_mismatch(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        matrix = load_calibration_matrix(
            project_root,
            rel_path="configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml",
        )
        matrix["passport_mode"]["action_id"] = "WRONG_ACTION"

        with self.assertRaisesRegex(OptunaSpaceCompileError, "passport registry action_id mismatch"):
            compile_optuna_space(matrix, contour_id="long_only", min_enabled_blocks=1)

    def test_passport_action_matrix_rejects_legacy_params(self) -> None:
        matrix = {
            "passport_mode": {
                "enabled": True,
                "action_passport_id": "F001",
                "allowed_calibration_params": ["F001_move", "F001_thr_pct"],
            },
            "optuna_switches": {
                "block_switches": {"price_volatility": True},
                "hypothesis_switches": {"enabled": True},
            },
            "parameter_profiles": {
                "F001_move": {"values": [-1, 1]},
                "F001_thr_pct": {"min": 0.01, "max": 0.5, "step": 0.01},
                "return_lookback": {"min": 3, "max": 30, "step": 3},
            },
            "feature_rows": [
                {
                    "block": "price_volatility",
                    "feature": "ret_1",
                    "calibrate": True,
                    "optuna_toggle": True,
                    "params": ["F001_move", "return_lookback"],
                }
            ],
        }

        with self.assertRaisesRegex(OptunaSpaceCompileError, "passport_mode disallowed params"):
            compile_optuna_space(matrix, contour_id="long_only", min_enabled_blocks=1)

    def test_strict_block_purity_filters_cross_block_hypotheses(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        matrix = copy.deepcopy(load_calibration_matrix(project_root))
        matrix["optuna_switches"]["hypothesis_switches"]["strict_block_purity"] = True
        matrix["optuna_switches"]["context_blocks"] = {
            "enabled": True,
            "always_on": ["volume_flow", "price_volatility"],
        }

        volume_matrix = copy.deepcopy(matrix)
        for block in list(volume_matrix["optuna_switches"]["block_switches"].keys()):
            volume_matrix["optuna_switches"]["block_switches"][block] = block == "volume_flow"
        volume_space = compile_optuna_space(volume_matrix, contour_id="long_only", min_enabled_blocks=1)
        volume_names = {str(x.get("hypothesis", "")).strip() for x in volume_space["hypothesis_rows"]}

        structure_matrix = copy.deepcopy(matrix)
        for block in list(structure_matrix["optuna_switches"]["block_switches"].keys()):
            structure_matrix["optuna_switches"]["block_switches"][block] = block == "structure_ta"
        structure_space = compile_optuna_space(structure_matrix, contour_id="long_only", min_enabled_blocks=1)
        structure_names = {str(x.get("hypothesis", "")).strip() for x in structure_space["hypothesis_rows"]}

        self.assertTrue(volume_space["strict_block_purity"])
        self.assertIn("none", volume_names)
        self.assertNotIn("min_max_range_revert", volume_names)
        self.assertIn("min_max_range_revert", structure_names)
        rejected = [
            x for x in volume_space["hypothesis_filter_report"]
            if x.get("hypothesis") == "min_max_range_revert"
        ]
        self.assertTrue(rejected)
        self.assertEqual(rejected[0]["reason"], "required_blocks_outside_effective_blocks")

    def test_runtime_constraints_detect_failures(self) -> None:
        failed = evaluate_runtime_constraints(
            [
                "p_short < p_long",
                "window >= lookback + 2",
                "time_direction = past_only",
            ],
            {
                "p_short": 0.60,
                "p_long": 0.55,
                "window": 5,
                "lookback": 5,
                "time_direction": "future",
            },
        )
        self.assertIn("p_short < p_long", failed)
        self.assertIn("window >= lookback + 2", failed)
        self.assertIn("time_direction = past_only", failed)

    def test_runtime_constraints_skip_unknown_values(self) -> None:
        failed = evaluate_runtime_constraints(
            ["ema_fast < ema_slow", "density_window_long > density_window_short"],
            {"p_short": 0.4, "p_long": 0.6},
        )
        self.assertEqual(failed, [])

    def test_runtime_constraints_detailed_reports_skipped(self) -> None:
        report = evaluate_runtime_constraints_detailed(
            ["ema_fast < ema_slow", "p_short < p_long", "bad syntax INVALID_SYNTAX_TOKEN"],
            {"p_short": 0.4, "p_long": 0.6},
        )
        self.assertEqual(report["failed"], [])
        self.assertIn("ema_fast < ema_slow", report["skipped_missing_values"])
        self.assertIn("bad syntax INVALID_SYNTAX_TOKEN", report["skipped_unparsed"])
        self.assertIn("p_short < p_long", report["evaluated"])

    def test_runtime_constraints_chain_supported(self) -> None:
        report_ok = evaluate_runtime_constraints_detailed(
            ["ema_fast < ema_slow < ema_ultra"],
            {"ema_fast": 20, "ema_slow": 50, "ema_ultra": 200},
        )
        self.assertEqual(report_ok["failed"], [])
        self.assertIn("ema_fast < ema_slow < ema_ultra", report_ok["evaluated"])

        report_bad = evaluate_runtime_constraints_detailed(
            ["ema_fast < ema_slow < ema_ultra"],
            {"ema_fast": 60, "ema_slow": 50, "ema_ultra": 200},
        )
        self.assertIn("ema_fast < ema_slow < ema_ultra", report_bad["failed"])


if __name__ == "__main__":
    unittest.main()
