from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import optuna
import pandas as pd

from mlbotnav.dataset import FEATURE_COLUMNS
import mlbotnav.optuna_search_candidate as osc
from mlbotnav.optuna_objective import ObjectiveWeights
from mlbotnav.optuna_search_candidate import (
    OPTUNA_REPORT_CONTRACT_VERSION,
    _apply_gate_mode_overrides,
    _apply_objective_mode_overrides,
    _apply_cli_study_overrides,
    _build_artifact_hashes,
    _build_grid_edge_coverage_audit,
    _canonical_contract_meta,
    _ensure_selected_trend_enabled,
    _apply_zero_signal_penalties,
    _resolve_trial_trend_filter,
    _should_relax_zero_raw,
    _should_relax_zero_filter,
    _shared_study_id,
    _build_input_fingerprints,
    _build_resume_report,
    _build_resource_profile_table,
    _build_trial_history_rows,
    _build_run_signature,
    _build_space_signature,
    _profile_edge_run_index_for_worker,
    _profile_edge_task_window,
    _sample_profile_values,
    _effective_study_name,
    _build_stability_report,
    _feature_columns_from_blocks,
    _feature_columns_from_space_rows,
    _collect_active_profile_names,
    _trend_choices_from_space,
    _write_optuna_artifacts,
    _is_strict_1d1d_protocol,
    _resolve_stage,
    _row_trend_filter,
    _stage_label,
    _validate_contour_signal_mode,
    _worker_index_from_contour_id,
)


class OptunaSearchRuntimeTests(unittest.TestCase):
    def _ns(self, **overrides):
        base = {
            "symbol": "SOLUSDT",
            "timeframe": "1m",
            "start_date": "2026-05-19",
            "end_date": "2026-05-19",
            "test_day": "2026-05-20",
            "contour_id": "long_only",
            "signal_mode": "long_only",
            "execution_mode": "exchange_like",
            "order_type": "market",
            "fee_bps": 10.0,
            "slippage_bps": 5.0,
            "stop_loss_pct": 0.01,
            "take_profit_pct": 0.02,
            "min_tp_reach_prob": 0.58,
            "tp_min_factor": 0.7,
            "cooldown_bars": 0,
            "limit_offset_bps": 2.0,
            "trend_filter": "none",
            "min_abs_ema_gap": 0.0,
            "min_train_rows": 2200,
            "n_folds": 4,
            "horizons_grid": "1,2,3",
            "p_long_grid": "0.52,0.54",
            "p_short_grid": "0.48,0.46",
            "min_expected_move_grid": "0.001,0.002",
            "notional_usd_grid": "10,20",
        }
        base.update(overrides)
        return argparse.Namespace(**base)

    def test_run_signature_is_stable(self) -> None:
        args = self._ns()
        plan = {"n_trials": 200, "timeout_sec": 7200, "seed": 20260526}
        w = ObjectiveWeights()
        a = _build_run_signature(args=args, study_plan=plan, weights=w)
        b = _build_run_signature(args=args, study_plan=plan, weights=w)
        self.assertEqual(a, b)

    def test_worker_index_from_contour_id(self) -> None:
        self.assertEqual(_worker_index_from_contour_id("long_only_pool_20260604_w1"), 0)
        self.assertEqual(_worker_index_from_contour_id("long_only_pool_20260604_w3"), 2)
        self.assertEqual(_worker_index_from_contour_id("long_only"), 0)

    def test_shared_study_id_sanitizes_cli_value(self) -> None:
        self.assertEqual(_shared_study_id("B001 LONG 4/5 shared"), "B001_LONG_4_5_shared")
        self.assertEqual(_shared_study_id("  B001_LONG_4OF5  "), "B001_LONG_4OF5")
        self.assertEqual(_shared_study_id(""), "")

    def test_run_signature_changes_when_grid_changes(self) -> None:
        args_a = self._ns(horizons_grid="1,2,3")
        args_b = self._ns(horizons_grid="1,2,3,4")
        plan = {"n_trials": 200, "timeout_sec": 7200, "seed": 20260526}
        w = ObjectiveWeights()
        a = _build_run_signature(args=args_a, study_plan=plan, weights=w)
        b = _build_run_signature(args=args_b, study_plan=plan, weights=w)
        self.assertNotEqual(a, b)

    def test_run_signature_changes_when_min_tp_reach_prob_changes(self) -> None:
        args_a = self._ns(min_tp_reach_prob=0.58)
        args_b = self._ns(min_tp_reach_prob=0.73)
        plan = {"n_trials": 200, "timeout_sec": 7200, "seed": 20260526}
        w = ObjectiveWeights()
        a = _build_run_signature(args=args_a, study_plan=plan, weights=w)
        b = _build_run_signature(args=args_b, study_plan=plan, weights=w)
        self.assertNotEqual(a, b)

    def test_run_signature_changes_when_objective_penalties_change(self) -> None:
        args = self._ns()
        plan_a = {
            "n_trials": 200,
            "timeout_sec": 7200,
            "seed": 20260526,
            "objective": {"zero_raw_penalty": 1.0, "zero_filter_penalty": 2.0},
        }
        plan_b = {
            "n_trials": 200,
            "timeout_sec": 7200,
            "seed": 20260526,
            "objective": {"zero_raw_penalty": 1.5, "zero_filter_penalty": 2.0},
        }
        w = ObjectiveWeights()
        a = _build_run_signature(args=args, study_plan=plan_a, weights=w)
        b = _build_run_signature(args=args, study_plan=plan_b, weights=w)
        self.assertNotEqual(a, b)

    def test_run_signature_changes_when_space_signature_changes(self) -> None:
        args = self._ns()
        plan = {"n_trials": 200, "timeout_sec": 7200, "seed": 20260526}
        w = ObjectiveWeights()
        a = _build_run_signature(args=args, study_plan=plan, weights=w, space_signature="F013")
        b = _build_run_signature(args=args, study_plan=plan, weights=w, space_signature="F014")
        self.assertNotEqual(a, b)

    def test_space_signature_tracks_passport_profiles(self) -> None:
        base = {
            "passport_mode": {"registry_block_id": "B007", "registry_passport_id": "F013"},
            "profiles": {"F013_state": {}, "F013_thr_pct": {}},
            "feature_rows": [
                {
                    "block": "trend_momentum",
                    "feature": "macd_line_1m",
                    "action_id": "F013_MACDLINE_ALLOW",
                    "params": ["F013_state", "F013_thr_pct"],
                }
            ],
            "hypothesis_rows": [{"hypothesis": "none", "params": []}],
        }
        changed = dict(base)
        changed["passport_mode"] = {"registry_block_id": "B007", "registry_passport_id": "F014"}
        changed["profiles"] = {"F014_state": {}, "F014_thr_pct": {}}
        self.assertNotEqual(_build_space_signature(base), _build_space_signature(changed))

    def test_feature_columns_from_blocks_is_ordered_subset(self) -> None:
        cols = _feature_columns_from_blocks(["trend_momentum", "volume_flow"])
        self.assertGreater(len(cols), 0)
        self.assertTrue(all(c in FEATURE_COLUMNS for c in cols))
        self.assertEqual(cols, [c for c in FEATURE_COLUMNS if c in cols])

    def test_feature_columns_from_blocks_empty(self) -> None:
        cols = _feature_columns_from_blocks([])
        self.assertEqual(cols, [])

    def test_trend_choices_do_not_readd_incompatible_fallback(self) -> None:
        choices = _trend_choices_from_space(
            {"hypothesis_rows": [{"hypothesis": "none"}]},
            fallback="min_max_range_revert",
        )
        self.assertEqual(choices, ["none"])

    def test_feature_columns_from_space_rows_includes_context_blocks(self) -> None:
        cols = _feature_columns_from_space_rows(
            active_blocks=["structure_ta"],
            context_blocks=["volume_flow", "price_volatility"],
            feature_rows=[
                {"block": "structure_ta", "feature": "position_in_range"},
                {"block": "volume_flow", "feature": "mfi14"},
                {"block": "price_volatility", "feature": "ret_1"},
                {"block": "density_profile", "feature": "density_poc_distance"},
            ],
        )

        self.assertIn("position_in_range", cols)
        self.assertIn("mfi14", cols)
        self.assertIn("ret_1", cols)
        self.assertNotIn("density_poc_distance", cols)
        self.assertEqual(cols, [c for c in FEATURE_COLUMNS if c in cols])

    def test_active_profiles_include_context_block_params(self) -> None:
        names = _collect_active_profile_names(
            space={
                "profiles": {
                    "range_window_short": {"values": [12]},
                    "period_standard": {"values": [14]},
                    "return_lookback": {"values": [3]},
                    "density_bins": {"values": [24]},
                },
                "feature_rows": [
                    {"block": "structure_ta", "feature": "position_in_range", "params": ["range_window_short"]},
                    {"block": "volume_flow", "feature": "mfi14", "params": ["period_standard"]},
                    {"block": "price_volatility", "feature": "ret_1", "params": ["return_lookback"]},
                    {"block": "density_profile", "feature": "density_poc_distance", "params": ["density_bins"]},
                ],
                "hypothesis_rows": [],
            },
            active_blocks=["structure_ta"],
            context_blocks=["volume_flow", "price_volatility"],
            enabled_hypotheses=[],
        )

        self.assertIn("range_window_short", names)
        self.assertIn("period_standard", names)
        self.assertIn("return_lookback", names)
        self.assertNotIn("density_bins", names)

    def test_row_trend_filter_prefers_selected_runtime_value(self) -> None:
        trend = _row_trend_filter(
            trial_params={"trend_filter": "ema_cross_20_50"},
            trial_user_attrs={"selected_trend_filter": "adx_trend_18"},
            fallback="none",
        )
        self.assertEqual(trend, "adx_trend_18")

    def test_ensure_selected_trend_enabled_forces_selected_toggle(self) -> None:
        updated, enabled, forced = _ensure_selected_trend_enabled(
            selected_trend="fib_extension_targets",
            toggle_map={
                "fib_extension_targets": False,
                "ema_gap_sign": False,
            },
        )
        self.assertTrue(forced)
        self.assertTrue(updated["fib_extension_targets"])
        self.assertIn("fib_extension_targets", enabled)

    def test_ensure_selected_trend_enabled_adds_missing_selected_trend(self) -> None:
        updated, enabled, forced = _ensure_selected_trend_enabled(
            selected_trend="none",
            toggle_map={"ema_gap_sign": False},
        )
        self.assertTrue(forced)
        self.assertTrue(updated["none"])
        self.assertEqual(enabled, ["none"])

    def test_resolve_trial_trend_filter_forces_preferred_on_first_trial(self) -> None:
        trend, forced = _resolve_trial_trend_filter(
            run_trial_index=0,
            hypothesis_names=["none", "ema_gap_sign"],
            preferred_trend="none",
            sampled_trend="ema_gap_sign",
        )
        self.assertEqual(trend, "none")
        self.assertTrue(forced)

    def test_resolve_trial_trend_filter_keeps_sampled_after_first_trial(self) -> None:
        trend, forced = _resolve_trial_trend_filter(
            run_trial_index=1,
            hypothesis_names=["none", "ema_gap_sign"],
            preferred_trend="none",
            sampled_trend="ema_gap_sign",
        )
        self.assertEqual(trend, "ema_gap_sign")
        self.assertFalse(forced)

    def test_should_relax_zero_filter_short_mode(self) -> None:
        should = _should_relax_zero_filter(
            signal_mode="short_only",
            selected_trend="adx_trend_18",
            signal_count_after_filter=0,
            available_hypotheses=["none", "adx_trend_18"],
            objective_cfg={},
        )
        self.assertTrue(should)

    def test_should_not_relax_zero_filter_when_not_short(self) -> None:
        should = _should_relax_zero_filter(
            signal_mode="long_only",
            selected_trend="adx_trend_18",
            signal_count_after_filter=0,
            available_hypotheses=["none", "adx_trend_18"],
            objective_cfg={},
        )
        self.assertFalse(should)

    def test_should_relax_zero_raw_short_mode(self) -> None:
        should = _should_relax_zero_raw(
            signal_mode="short_only",
            signal_count_raw=0,
            objective_cfg={},
        )
        self.assertTrue(should)

    def test_should_not_relax_zero_raw_when_not_short(self) -> None:
        should = _should_relax_zero_raw(
            signal_mode="long_only",
            signal_count_raw=0,
            objective_cfg={},
        )
        self.assertFalse(should)

    def test_apply_zero_signal_penalties_applies_both(self) -> None:
        out = _apply_zero_signal_penalties(
            score=10.0,
            signal_count_raw=0,
            signal_count_after_filter=0,
            objective_cfg={"zero_raw_penalty": 1.5, "zero_filter_penalty": 2.0},
        )
        self.assertAlmostEqual(out, 6.5, places=8)

    def test_apply_zero_signal_penalties_noop_when_signals_present(self) -> None:
        out = _apply_zero_signal_penalties(
            score=10.0,
            signal_count_raw=5,
            signal_count_after_filter=2,
            objective_cfg={"zero_raw_penalty": 1.5, "zero_filter_penalty": 2.0},
        )
        self.assertAlmostEqual(out, 10.0, places=8)

    def test_apply_objective_mode_overrides_prefers_signal_mode_map(self) -> None:
        cfg = {
            "no_trade_penalty": 100.0,
            "zero_filter_penalty": 2.0,
            "signal_mode_overrides": {
                "short_only": {
                    "no_trade_penalty": 300.0,
                    "zero_filter_penalty": 8.0,
                }
            },
        }
        out = _apply_objective_mode_overrides(objective_cfg=cfg, signal_mode="short_only")
        self.assertEqual(float(out["no_trade_penalty"]), 300.0)
        self.assertEqual(float(out["zero_filter_penalty"]), 8.0)
        # Source config remains unchanged
        self.assertEqual(float(cfg["no_trade_penalty"]), 100.0)

    def test_apply_objective_mode_overrides_supports_legacy_alias(self) -> None:
        cfg = {
            "no_trade_penalty": 100.0,
            "short_only_overrides": {
                "no_trade_penalty": 250.0,
            },
        }
        out = _apply_objective_mode_overrides(objective_cfg=cfg, signal_mode="short_only")
        self.assertEqual(float(out["no_trade_penalty"]), 250.0)

    def test_apply_gate_mode_overrides_applies_short_only_scope(self) -> None:
        thresholds = {
            "gates": {
                "min_trades": 20,
                "min_net_return_pct": 10.0,
            }
        }
        cfg = {
            "gate_signal_mode_overrides": {
                "short_only": {
                    "min_trades": 5,
                    "min_net_return_pct": 5.0,
                }
            }
        }
        out = _apply_gate_mode_overrides(
            thresholds=thresholds,
            cfg=cfg,
            signal_mode="short_only",
        )
        self.assertEqual(int(out["gates"]["min_trades"]), 5)
        self.assertEqual(float(out["gates"]["min_net_return_pct"]), 5.0)
        # Source thresholds stay unchanged.
        self.assertEqual(int(thresholds["gates"]["min_trades"]), 20)

    def test_apply_gate_mode_overrides_noop_for_other_mode(self) -> None:
        thresholds = {"gates": {"min_trades": 20}}
        cfg = {"gate_signal_mode_overrides": {"short_only": {"min_trades": 5}}}
        out = _apply_gate_mode_overrides(
            thresholds=thresholds,
            cfg=cfg,
            signal_mode="long_only",
        )
        self.assertEqual(int(out["gates"]["min_trades"]), 20)

    def test_stage_label_requires_next_day_relation_for_1d1d(self) -> None:
        self.assertEqual(
            _stage_label(
                signal_mode="long_only",
                start_date="2026-05-19",
                end_date="2026-05-19",
                test_day="2026-05-20",
            ),
            "A_long_1d1d",
        )
        self.assertEqual(
            _stage_label(
                signal_mode="long_only",
                start_date="2026-05-19",
                end_date="2026-05-19",
                test_day="2026-05-19",
            ),
            "C_multiday_stability",
        )

    def test_is_strict_1d1d_protocol(self) -> None:
        self.assertTrue(
            _is_strict_1d1d_protocol(
                start_date="2026-05-19",
                end_date="2026-05-19",
                test_day="2026-05-20",
            )
        )
        self.assertFalse(
            _is_strict_1d1d_protocol(
                start_date="2026-05-18",
                end_date="2026-05-19",
                test_day="2026-05-20",
            )
        )
        self.assertFalse(
            _is_strict_1d1d_protocol(
                start_date="2026-05-19",
                end_date="2026-05-19",
                test_day="bad-date",
            )
        )

    def test_stability_report_uses_full_candidate_set(self) -> None:
        candidates = [
            {
                "gate_pass": True,
                "signal_count_raw": 5,
                "signal_count_after_filter": 2,
                "backtest": {"net_return_pct": 2.0, "max_drawdown_pct": -1.0, "trades": 2},
            },
            {
                "gate_pass": False,
                "signal_count_raw": 0,
                "signal_count_after_filter": 0,
                "zero_filter_relax_attempted": True,
                "backtest": {"net_return_pct": -1.0, "max_drawdown_pct": -2.0, "trades": 0},
            },
            {
                "gate_pass": False,
                "signal_count_raw": 1,
                "signal_count_after_filter": 0,
                "zero_filter_relax_attempted": True,
                "zero_filter_relax_applied": True,
                "backtest": {"net_return_pct": 0.0, "max_drawdown_pct": -0.5, "trades": 1},
            },
        ]
        report = _build_stability_report(
            candidates=candidates,
            pass_candidates=[candidates[0]],
            goal_candidates=[candidates[0]],
            signal_mode="long_only",
            start_date="2026-05-19",
            end_date="2026-05-19",
            test_day="2026-05-20",
        )
        self.assertEqual(report["candidates_total"], 3)
        self.assertAlmostEqual(report["pass_rate"], 1.0 / 3.0, places=6)
        self.assertAlmostEqual(report["tradeful_rate"], 2.0 / 3.0, places=6)
        z = report["zero_signal_diagnostics"]
        self.assertEqual(z["raw_zero_count"], 1)
        self.assertEqual(z["filter_zero_count"], 2)
        self.assertEqual(z["relax_attempted_count"], 2)
        self.assertEqual(z["relax_applied_count"], 1)

    def test_stability_report_counts_min_move_unreachable_candidates(self) -> None:
        candidates = [
            {
                "gate_pass": False,
                "min_move_unreachable": True,
                "backtest": {
                    "net_return_pct": 0.0,
                    "max_drawdown_pct": 0.0,
                    "trades": 0,
                    "min_expected_move_pct": 0.01,
                    "trend_filter_diagnostics": {
                        "signal_count_after_entry_action_gates": 10,
                        "signal_count_after_filter": 10,
                        "signal_count_after_min_move": 0,
                        "min_move_unreachable_after_action_gate": True,
                    },
                },
            },
            {
                "gate_pass": True,
                "backtest": {"net_return_pct": 2.0, "max_drawdown_pct": -1.0, "trades": 2},
            },
            {
                "gate_pass": False,
                "backtest": {"net_return_pct": -1.0, "max_drawdown_pct": -1.0, "trades": 1},
            },
        ]
        report = _build_stability_report(
            candidates=candidates,
            pass_candidates=[candidates[1]],
            goal_candidates=[candidates[1]],
            signal_mode="long_only",
            start_date="2026-05-19",
            end_date="2026-05-19",
            test_day="2026-05-20",
        )

        mm = report["min_move_diagnostics"]
        self.assertEqual(mm["unreachable_after_action_gate_count"], 1)
        self.assertAlmostEqual(mm["unreachable_after_action_gate_rate"], 1.0 / 3.0, places=6)

    def test_resolve_stage_auto_and_forced(self) -> None:
        auto_stage = _resolve_stage(
            stage_arg="auto",
            signal_mode="long_only",
            start_date="2026-05-19",
            end_date="2026-05-19",
            test_day="2026-05-20",
        )
        self.assertEqual(auto_stage, "A")
        forced_stage = _resolve_stage(
            stage_arg="C",
            signal_mode="long_only",
            start_date="2026-05-19",
            end_date="2026-05-19",
            test_day="2026-05-20",
        )
        self.assertEqual(forced_stage, "C")

    def test_resolve_stage_rejects_mismatched_forced_stage(self) -> None:
        with self.assertRaises(ValueError):
            _resolve_stage(
                stage_arg="B",
                signal_mode="long_only",
                start_date="2026-05-19",
                end_date="2026-05-19",
                test_day="2026-05-20",
            )

    def test_resolve_stage_rejects_forced_ab_when_not_1d1d(self) -> None:
        with self.assertRaises(ValueError):
            _resolve_stage(
                stage_arg="A",
                signal_mode="long_only",
                start_date="2026-05-18",
                end_date="2026-05-19",
                test_day="2026-05-20",
            )
        with self.assertRaises(ValueError):
            _resolve_stage(
                stage_arg="B",
                signal_mode="short_only",
                start_date="2026-05-19",
                end_date="2026-05-19",
                test_day="2026-05-19",
            )

    def test_resolve_stage_allows_forced_c_on_any_window(self) -> None:
        stage = _resolve_stage(
            stage_arg="C",
            signal_mode="long_only",
            start_date="2026-05-01",
            end_date="2026-05-19",
            test_day="2026-05-20",
        )
        self.assertEqual(stage, "C")

    def test_validate_contour_signal_mode_accepts_matching(self) -> None:
        _validate_contour_signal_mode(contour_id="long_only", signal_mode="long_only")
        _validate_contour_signal_mode(contour_id="short_only", signal_mode="short_only")
        _validate_contour_signal_mode(contour_id="daily_contour", signal_mode="long_only")

    def test_validate_contour_signal_mode_rejects_mismatch(self) -> None:
        with self.assertRaises(ValueError):
            _validate_contour_signal_mode(contour_id="long_only", signal_mode="short_only")
        with self.assertRaises(ValueError):
            _validate_contour_signal_mode(contour_id="short_only", signal_mode="long_only")
        with self.assertRaises(ValueError):
            _validate_contour_signal_mode(
                contour_id="optuna_long_only_short_only_conflict",
                signal_mode="long_only",
            )

    def test_validate_contour_signal_mode_ignores_substring_noise(self) -> None:
        _validate_contour_signal_mode(contour_id="prolong_onlyx", signal_mode="long_only")
        _validate_contour_signal_mode(contour_id="ultrashort_onlyx", signal_mode="short_only")

    def test_effective_study_name_includes_run_signature(self) -> None:
        name = _effective_study_name(base_study_name="optuna_long_only_x", run_signature="abc123")
        self.assertEqual(name, "optuna_long_only_x__abc123")

    def test_apply_cli_study_overrides_changes_only_positive_values(self) -> None:
        base = {"n_trials": 160, "timeout_sec": 3600, "direction": "maximize"}
        out = _apply_cli_study_overrides(study_plan=base, n_trials_override=24, timeout_sec_override=900)
        self.assertEqual(out["n_trials"], 24)
        self.assertEqual(out["timeout_sec"], 900)
        self.assertEqual(out["direction"], "maximize")

    def test_apply_cli_study_overrides_ignores_non_positive(self) -> None:
        base = {"n_trials": 160, "timeout_sec": 3600}
        out = _apply_cli_study_overrides(study_plan=base, n_trials_override=0, timeout_sec_override=-1)
        self.assertEqual(out["n_trials"], 160)
        self.assertEqual(out["timeout_sec"], 3600)

    def test_canonical_contract_meta_normalizes_and_validates(self) -> None:
        meta = _canonical_contract_meta(signal_mode=" LONG_ONLY ", contract_version="vX")
        self.assertEqual(meta["signal_mode"], "long_only")
        self.assertEqual(meta["contract_version"], "vX")
        trimmed = _canonical_contract_meta(signal_mode="short_only", contract_version="  vY  ")
        self.assertEqual(trimmed["signal_mode"], "short_only")
        self.assertEqual(trimmed["contract_version"], "vY")
        with self.assertRaisesRegex(ValueError, "invalid signal_mode"):
            _canonical_contract_meta(signal_mode="both", contract_version="vX")
        with self.assertRaisesRegex(ValueError, "invalid contract_version"):
            _canonical_contract_meta(signal_mode="long_only", contract_version="   ")

    def test_build_trial_history_rows_flattens_backtest_fields(self) -> None:
        rows = _build_trial_history_rows(
            [
                {
                    "trial_number": 7,
                    "score": 1.23,
                    "gate_pass": True,
                    "horizon_bars": 4,
                    "p_enter_long": 0.55,
                    "p_enter_short": 0.45,
                    "min_expected_move_pct": 0.001,
                    "notional_usd": 25.0,
                    "trend_filter": "none",
                    "active_blocks": ["trend_momentum", "volume_flow"],
                    "enabled_hypotheses": ["ema_cross_20_50"],
                    "feature_columns_count": 12,
                    "signal_count_raw": 7,
                    "signal_count_after_filter": 3,
                    "signal_count_raw_initial": 0,
                    "signal_count_raw_relaxed": 7,
                    "signal_count_after_filter_initial": 0,
                    "signal_count_after_filter_relaxed": 3,
                    "zero_raw_relax_attempted": True,
                    "zero_raw_relax_applied": True,
                    "zero_filter_relax_attempted": True,
                    "zero_filter_relax_applied": True,
                    "zero_filter_gate": False,
                    "fail_keys": ["x", "y"],
                    "backtest": {
                        "trades": 5,
                        "net_return_pct": 2.5,
                        "max_drawdown_pct": -1.1,
                        "hit_rate": 0.6,
                        "trades_per_day_avg": 3.0,
                    },
                }
            ],
            signal_mode="long_only",
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["trial_number"], 7)
        self.assertEqual(rows[0]["contract_version"], OPTUNA_REPORT_CONTRACT_VERSION)
        self.assertEqual(rows[0]["signal_mode"], "long_only")
        self.assertEqual(rows[0]["active_blocks_count"], 2)
        self.assertEqual(rows[0]["enabled_hypotheses_count"], 1)
        self.assertEqual(rows[0]["trades"], 5)
        self.assertEqual(rows[0]["fail_keys"], "x,y")
        self.assertEqual(rows[0]["signal_count_raw"], 7)
        self.assertEqual(rows[0]["signal_count_after_filter"], 3)
        self.assertTrue(rows[0]["zero_raw_relax_attempted"])
        self.assertTrue(rows[0]["zero_filter_relax_attempted"])

    def test_build_trial_history_rows_includes_shared_worker_fields(self) -> None:
        rows = _build_trial_history_rows(
            [
                {
                    "trial_number": 7,
                    "worker_contour_id": "long_only_pool_stamp_w2",
                    "study_namespace": "B001_SHARED",
                    "shared_study_id": "B001_SHARED",
                    "shared_optuna_study": True,
                    "sampler_seed_effective": 12345,
                    "profile_edge_worker_offset": 14,
                    "backtest": {"trades": 0, "net_return_pct": 0.0},
                }
            ],
            signal_mode="long_only",
        )
        row = rows[0]
        self.assertEqual(row["worker_contour_id"], "long_only_pool_stamp_w2")
        self.assertEqual(row["study_namespace"], "B001_SHARED")
        self.assertEqual(row["shared_study_id"], "B001_SHARED")
        self.assertTrue(row["shared_optuna_study"])
        self.assertEqual(row["sampler_seed_effective"], 12345)
        self.assertEqual(row["profile_edge_worker_offset"], 14)

    def test_build_trial_history_rows_flattens_min_move_gate_diagnostics(self) -> None:
        rows = _build_trial_history_rows(
            [
                {
                    "trial_number": 9,
                    "score": -1.0,
                    "min_expected_move_pct": 0.01,
                    "backtest": {
                        "trades": 0,
                        "net_return_pct": 0.0,
                        "max_drawdown_pct": 0.0,
                        "min_expected_move_pct": 0.01,
                        "trend_filter_diagnostics": {
                            "signal_count_after_entry_action_gates": 1415,
                            "signal_count_after_filter": 1415,
                            "signal_count_after_min_move": 0,
                            "entries_filled": 0,
                            "min_move_unreachable_after_action_gate": True,
                        },
                    },
                }
            ],
            signal_mode="long_only",
        )

        self.assertEqual(rows[0]["signal_count_after_entry_action_gates"], 1415)
        self.assertEqual(rows[0]["signal_count_after_min_move"], 0)
        self.assertEqual(rows[0]["entries_filled"], 0)
        self.assertTrue(rows[0]["min_move_unreachable_after_action_gate"])
        self.assertEqual(rows[0]["runtime_diagnostic_status"], "MIN_MOVE_UNREACHABLE")

    def test_build_trial_history_rows_defaults_signal_mode_to_empty(self) -> None:
        rows = _build_trial_history_rows(
            [
                {
                    "trial_number": 1,
                    "score": 0.0,
                    "backtest": {},
                }
            ]
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["signal_mode"], "")

    def test_build_trial_history_rows_fallback_contract_version_when_blank(self) -> None:
        rows = _build_trial_history_rows(
            [
                {
                    "trial_number": 1,
                    "score": 0.0,
                    "backtest": {},
                }
            ],
            signal_mode="",
            contract_version="   ",
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["signal_mode"], "")
        self.assertEqual(rows[0]["contract_version"], OPTUNA_REPORT_CONTRACT_VERSION)

    def test_build_trial_history_rows_uses_provided_contract_version(self) -> None:
        rows = _build_trial_history_rows(
            [
                {
                    "trial_number": 1,
                    "score": 0.0,
                    "backtest": {},
                }
            ],
            signal_mode="long_only",
            contract_version="optuna_report_v2_test",
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["contract_version"], "optuna_report_v2_test")

    def test_write_optuna_artifacts_creates_mode_files(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = _write_optuna_artifacts(
                project_root=root,
                signal_mode="long_only",
                ts="20260526T182500Z",
                summary_payload={
                    "contract_version": OPTUNA_REPORT_CONTRACT_VERSION,
                    "run_utc": "20260526T182500Z",
                    "symbol": "SOLUSDT",
                    "stability_report": {"candidates_total": 1},
                    "resource_profile_table": [{"metric": "workers_used", "value": 1}],
                },
                top_candidates=[{"trial_number": 1, "score": 0.5}, {"trial_number": 2, "score": 0.4}],
                all_completed_rows=[
                    {
                        "trial_number": 1,
                        "score": 0.5,
                        "gate_pass": True,
                        "horizon_bars": 2,
                        "p_enter_long": 0.56,
                        "p_enter_short": 0.44,
                        "min_expected_move_pct": 0.001,
                        "notional_usd": 10.0,
                        "trend_filter": "none",
                        "active_blocks": ["trend_momentum"],
                        "enabled_hypotheses": ["ema_cross_20_50"],
                        "feature_columns_count": 8,
                        "fail_keys": ["none"],
                        "backtest": {
                            "trades": 1,
                            "net_return_pct": 0.3,
                            "max_drawdown_pct": -0.1,
                            "hit_rate": 1.0,
                            "trades_per_day_avg": 1.0,
                        },
                    }
                ],
            )
            summary_path = Path(paths["study_summary_path"])
            topk_path = Path(paths["best_trials_topk_path"])
            history_path = Path(paths["trial_history_path"])

            self.assertTrue(summary_path.exists())
            self.assertTrue(topk_path.exists())
            self.assertTrue(history_path.exists())

            summary_posix = summary_path.as_posix()
            self.assertIn("/reports/optuna/long_only/", summary_posix)

            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertIn("run_utc", summary)
            self.assertIn("stability_report", summary)
            self.assertIn("resource_profile_table", summary)
            self.assertEqual(summary.get("contract_version"), OPTUNA_REPORT_CONTRACT_VERSION)
            self.assertEqual(summary.get("signal_mode"), "long_only")

            topk = json.loads(topk_path.read_text(encoding="utf-8"))
            self.assertIn("generated_utc", topk)
            self.assertEqual(topk.get("signal_mode"), "long_only")
            self.assertEqual(topk.get("contract_version"), OPTUNA_REPORT_CONTRACT_VERSION)
            self.assertIn("top_k", topk)
            self.assertLessEqual(len(list(topk.get("top_k") or [])), 20)
            if list(topk.get("top_k") or []):
                first = dict(list(topk.get("top_k") or [])[0] or {})
                self.assertEqual(first.get("signal_mode"), "long_only")
                self.assertEqual(first.get("contract_version"), OPTUNA_REPORT_CONTRACT_VERSION)

            history = pd.read_csv(history_path)
            expected_cols = {"contract_version", "signal_mode", "trial_number", "score", "trades", "net_return_pct", "fail_keys"}
            self.assertTrue(expected_cols.issubset(set(history.columns)))
            self.assertTrue((history["contract_version"] == OPTUNA_REPORT_CONTRACT_VERSION).all())
            self.assertTrue((history["signal_mode"] == "long_only").all())

    def test_grid_edge_coverage_audit_counts_pruned_forced_edges(self) -> None:
        class _Trial:
            def __init__(self, number, state, params, user_attrs) -> None:
                self.number = number
                self.state = state
                self.params = params
                self.user_attrs = user_attrs

        trials = [
            _Trial(
                1,
                optuna.trial.TrialState.COMPLETE,
                {"horizon_bars": 1},
                {
                    "core_params": {"horizon_bars": 1},
                    "core_forced_edges": [
                        {"parameter": "horizon_bars", "edge": "min", "value": 1}
                    ],
                    "calibration_params": {"pattern_window": 40.0},
                    "calibration_forced_edges": [
                        {"profile": "pattern_window", "edge": "min", "value": 40.0}
                    ],
                },
            ),
            _Trial(
                2,
                optuna.trial.TrialState.PRUNED,
                {"horizon_bars": 3},
                {
                    "core_params": {"horizon_bars": 3},
                    "core_forced_edges": [
                        {"parameter": "horizon_bars", "edge": "max", "value": 3}
                    ],
                    "calibration_params": {"pattern_window": 120.0},
                    "calibration_forced_edges": [
                        {"profile": "pattern_window", "edge": "max", "value": 120.0}
                    ],
                },
            ),
        ]

        audit = _build_grid_edge_coverage_audit(
            trials=trials,
            space={
                "profiles": {
                    "horizon_bars": {"values": [1, 2, 3]},
                    "pattern_window": {"values": [40.0, 80.0, 120.0]},
                }
            },
            core_domains={"horizon_bars": [1, 2, 3]},
            grid_preset="wide",
            force_profile_edge_coverage=True,
        )

        self.assertEqual(audit["trial_state_counts"]["completed"], 1)
        self.assertEqual(audit["trial_state_counts"]["pruned"], 1)
        self.assertEqual(audit["profile_count"], 1)
        row = dict(audit["profiles"][0])
        self.assertTrue(row["min_seen"])
        self.assertTrue(row["max_seen"])
        self.assertTrue(row["coverage_pass"])
        self.assertEqual(row["forced_min_trial_numbers"], [1])
        self.assertEqual(row["forced_max_trial_numbers"], [2])
        core_row = dict(audit["core_parameters"][0])
        self.assertTrue(core_row["min_seen"])
        self.assertTrue(core_row["max_seen"])
        self.assertTrue(core_row["coverage_pass"])
        self.assertEqual(core_row["forced_min_trial_numbers"], [1])
        self.assertEqual(core_row["forced_max_trial_numbers"], [2])

    def test_sample_profile_values_forces_profile_edges_by_local_trial_index(self) -> None:
        space = {
            "profiles": {
                "alpha": {"values": [1.0, 2.0]},
                "beta": {"values": [10.0, 20.0]},
            }
        }
        study = optuna.create_study(direction="maximize")
        forced_edges = []

        for ix in range(4):
            trial = study.ask()
            _sample_profile_values(
                trial=trial,
                space=space,
                profile_names=["alpha", "beta"],
                run_trial_index=ix,
                force_edge_coverage=True,
            )
            study.tell(trial, 0.0)
            forced_edges.extend(list(study.trials[-1].user_attrs.get("calibration_forced_edges") or []))

        self.assertEqual(
            [(x["profile"], x["edge"], x["run_trial_index"]) for x in forced_edges],
            [
                ("alpha", "min", 0),
                ("beta", "min", 1),
                ("alpha", "max", 2),
                ("beta", "max", 3),
            ],
        )

    def test_profile_edge_task_window_distributes_shared_study_edges(self) -> None:
        self.assertEqual(_profile_edge_task_window(worker_index=0, worker_count=3, task_count=14), (0, 5))
        self.assertEqual(_profile_edge_task_window(worker_index=1, worker_count=3, task_count=14), (5, 5))
        self.assertEqual(_profile_edge_task_window(worker_index=2, worker_count=3, task_count=14), (10, 4))
        self.assertEqual(
            [
                _profile_edge_run_index_for_worker(
                    local_profile_index=ix,
                    worker_index=2,
                    worker_count=3,
                    task_count=14,
                )
                for ix in range(4)
            ],
            [10, 11, 12, 13],
        )
        self.assertGreaterEqual(
            _profile_edge_run_index_for_worker(
                local_profile_index=4,
                worker_index=2,
                worker_count=3,
                task_count=14,
            ),
            14,
        )

    def test_write_optuna_artifacts_writes_grid_edge_coverage_audit(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = _write_optuna_artifacts(
                project_root=root,
                signal_mode="long_only",
                ts="20260526T182501Z",
                summary_payload={"run_utc": "20260526T182501Z"},
                top_candidates=[],
                all_completed_rows=[],
                grid_edge_coverage_audit={
                    "grid_preset": "wide",
                    "force_profile_edge_coverage": True,
                    "profiles": [],
                    "core_parameters": [],
                },
            )

            self.assertIn("grid_edge_coverage_audit_path", paths)
            edge_path = Path(paths["grid_edge_coverage_audit_path"])
            self.assertTrue(edge_path.exists())
            payload = json.loads(edge_path.read_text(encoding="utf-8"))
            self.assertEqual(payload.get("signal_mode"), "long_only")
            self.assertEqual(payload.get("contract_version"), OPTUNA_REPORT_CONTRACT_VERSION)
            self.assertEqual(payload.get("grid_preset"), "wide")

    def test_write_optuna_artifacts_canonicalizes_summary_contract_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = _write_optuna_artifacts(
                project_root=root,
                signal_mode="long_only",
                ts="20260526T200000Z",
                summary_payload={"run_utc": "20260526T200000Z"},
                top_candidates=[],
                all_completed_rows=[],
            )
            summary_path = Path(paths["study_summary_path"])
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary.get("contract_version"), OPTUNA_REPORT_CONTRACT_VERSION)
            self.assertEqual(summary.get("signal_mode"), "long_only")

    def test_write_optuna_artifacts_canonicalizes_summary_contract_version(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = _write_optuna_artifacts(
                project_root=root,
                signal_mode="long_only",
                ts="20260526T202000Z",
                summary_payload={
                    "run_utc": "20260526T202000Z",
                    "contract_version": "broken_contract_v0",
                },
                top_candidates=[],
                all_completed_rows=[],
            )
            summary_path = Path(paths["study_summary_path"])
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary.get("contract_version"), OPTUNA_REPORT_CONTRACT_VERSION)

    def test_write_optuna_artifacts_uses_provided_contract_version_globally(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = _write_optuna_artifacts(
                project_root=root,
                signal_mode="short_only",
                ts="20260526T202300Z",
                summary_payload={"run_utc": "20260526T202300Z"},
                top_candidates=[{"trial_number": 1, "score": 0.1}],
                all_completed_rows=[{"trial_number": 1, "score": 0.1, "backtest": {}}],
                contract_version="optuna_report_v2_test",
            )
            summary = json.loads(Path(paths["study_summary_path"]).read_text(encoding="utf-8"))
            topk = json.loads(Path(paths["best_trials_topk_path"]).read_text(encoding="utf-8"))
            history = pd.read_csv(Path(paths["trial_history_path"]))
            self.assertEqual(summary.get("contract_version"), "optuna_report_v2_test")
            self.assertEqual(topk.get("contract_version"), "optuna_report_v2_test")
            self.assertTrue((history["contract_version"] == "optuna_report_v2_test").all())

    def test_write_optuna_artifacts_trims_contract_version_whitespace(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = _write_optuna_artifacts(
                project_root=root,
                signal_mode="long_only",
                ts="20260526T202355Z",
                summary_payload={"run_utc": "20260526T202355Z"},
                top_candidates=[{"trial_number": 1, "score": 0.1}],
                all_completed_rows=[{"trial_number": 1, "score": 0.1, "backtest": {}}],
                contract_version="  optuna_report_v2_trim  ",
            )
            summary = json.loads(Path(paths["study_summary_path"]).read_text(encoding="utf-8"))
            topk = json.loads(Path(paths["best_trials_topk_path"]).read_text(encoding="utf-8"))
            history = pd.read_csv(Path(paths["trial_history_path"]))
            self.assertEqual(summary.get("contract_version"), "optuna_report_v2_trim")
            self.assertEqual(topk.get("contract_version"), "optuna_report_v2_trim")
            self.assertTrue((history["contract_version"] == "optuna_report_v2_trim").all())

    def test_write_optuna_artifacts_normalizes_mode_and_contract_row_level(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            paths = _write_optuna_artifacts(
                project_root=root,
                signal_mode=" LONG_ONLY ",
                ts="20260526T202500Z",
                summary_payload={"run_utc": "20260526T202500Z"},
                top_candidates=[
                    {
                        "trial_number": 1,
                        "score": 0.2,
                        "signal_mode": "short_only",
                        "contract_version": "stale",
                        "backtest": {"trades": 1, "net_return_pct": 0.1, "max_drawdown_pct": -0.1},
                    }
                ],
                all_completed_rows=[
                    {
                        "trial_number": 1,
                        "score": 0.2,
                        "backtest": {"trades": 1, "net_return_pct": 0.1, "max_drawdown_pct": -0.1},
                    }
                ],
                contract_version="  optuna_report_v2_norm  ",
            )
            self.assertIn("/reports/optuna/long_only/", Path(paths["study_summary_path"]).as_posix())
            self.assertIn("/reports/optuna/long_only/", Path(paths["best_trials_topk_path"]).as_posix())
            self.assertIn("/reports/optuna/long_only/", Path(paths["trial_history_path"]).as_posix())
            summary = json.loads(Path(paths["study_summary_path"]).read_text(encoding="utf-8"))
            topk = json.loads(Path(paths["best_trials_topk_path"]).read_text(encoding="utf-8"))
            history = pd.read_csv(Path(paths["trial_history_path"]))
            self.assertEqual(summary.get("signal_mode"), "long_only")
            self.assertEqual(summary.get("contract_version"), "optuna_report_v2_norm")
            self.assertEqual(topk.get("signal_mode"), "long_only")
            self.assertEqual(topk.get("contract_version"), "optuna_report_v2_norm")
            first = dict(list(topk.get("top_k") or [])[0] or {})
            self.assertEqual(first.get("signal_mode"), "long_only")
            self.assertEqual(first.get("contract_version"), "optuna_report_v2_norm")
            self.assertTrue((history["signal_mode"] == "long_only").all())
            self.assertTrue((history["contract_version"] == "optuna_report_v2_norm").all())

    def test_write_optuna_artifacts_normalized_short_mode_uses_short_dir(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source_top = [
                {
                    "trial_number": 1,
                    "score": 0.2,
                    "signal_mode": "long_only",
                    "contract_version": "stale",
                    "backtest": {"trades": 1, "net_return_pct": 0.1, "max_drawdown_pct": -0.1},
                }
            ]
            source_top_snapshot = json.loads(json.dumps(source_top))
            paths = _write_optuna_artifacts(
                project_root=root,
                signal_mode=" SHORT_ONLY ",
                ts="20260526T202650Z",
                summary_payload={"run_utc": "20260526T202650Z"},
                top_candidates=source_top,
                all_completed_rows=[{"trial_number": 1, "score": 0.2, "backtest": {}}],
                contract_version="  optuna_report_v2_short  ",
            )
            self.assertIn("/reports/optuna/short_only/", Path(paths["study_summary_path"]).as_posix())
            self.assertIn("/reports/optuna/short_only/", Path(paths["best_trials_topk_path"]).as_posix())
            self.assertIn("/reports/optuna/short_only/", Path(paths["trial_history_path"]).as_posix())
            summary = json.loads(Path(paths["study_summary_path"]).read_text(encoding="utf-8"))
            topk = json.loads(Path(paths["best_trials_topk_path"]).read_text(encoding="utf-8"))
            history = pd.read_csv(Path(paths["trial_history_path"]))
            self.assertEqual(summary.get("signal_mode"), "short_only")
            self.assertEqual(summary.get("contract_version"), "optuna_report_v2_short")
            self.assertEqual(topk.get("signal_mode"), "short_only")
            self.assertEqual(topk.get("contract_version"), "optuna_report_v2_short")
            first = dict(list(topk.get("top_k") or [])[0] or {})
            self.assertEqual(first.get("signal_mode"), "short_only")
            self.assertEqual(first.get("contract_version"), "optuna_report_v2_short")
            self.assertTrue((history["signal_mode"] == "short_only").all())
            self.assertTrue((history["contract_version"] == "optuna_report_v2_short").all())
            self.assertEqual(source_top, source_top_snapshot)

    def test_write_optuna_artifacts_short_history_stale_meta_does_not_leak(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source_completed = [
                {
                    "trial_number": 1,
                    "score": 0.2,
                    "signal_mode": "long_only",
                    "contract_version": "stale",
                    "backtest": {"trades": 2, "net_return_pct": 0.3, "max_drawdown_pct": -0.2},
                }
            ]
            source_completed_snapshot = json.loads(json.dumps(source_completed))
            paths = _write_optuna_artifacts(
                project_root=root,
                signal_mode=" short_only ",
                ts="20260526T202720Z",
                summary_payload={"run_utc": "20260526T202720Z"},
                top_candidates=[{"trial_number": 1, "score": 0.2}],
                all_completed_rows=source_completed,
                contract_version="  optuna_report_v2_short_hist  ",
            )
            history = pd.read_csv(Path(paths["trial_history_path"]))
            self.assertTrue((history["signal_mode"] == "short_only").all())
            self.assertTrue((history["contract_version"] == "optuna_report_v2_short_hist").all())
            self.assertEqual(source_completed, source_completed_snapshot)

    def test_write_optuna_artifacts_long_history_stale_meta_does_not_leak(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source_completed = [
                {
                    "trial_number": 1,
                    "score": 0.2,
                    "signal_mode": "short_only",
                    "contract_version": "stale",
                    "backtest": {"trades": 2, "net_return_pct": 0.3, "max_drawdown_pct": -0.2},
                }
            ]
            source_completed_snapshot = json.loads(json.dumps(source_completed))
            paths = _write_optuna_artifacts(
                project_root=root,
                signal_mode=" long_only ",
                ts="20260526T202730Z",
                summary_payload={"run_utc": "20260526T202730Z"},
                top_candidates=[{"trial_number": 1, "score": 0.2}],
                all_completed_rows=source_completed,
                contract_version="  optuna_report_v2_long_hist  ",
            )
            history = pd.read_csv(Path(paths["trial_history_path"]))
            self.assertTrue((history["signal_mode"] == "long_only").all())
            self.assertTrue((history["contract_version"] == "optuna_report_v2_long_hist").all())
            self.assertEqual(source_completed, source_completed_snapshot)

    def test_write_optuna_artifacts_long_topk_stale_meta_does_not_leak(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source_top = [
                {
                    "trial_number": 1,
                    "score": 0.2,
                    "signal_mode": "short_only",
                    "contract_version": "stale",
                    "backtest": {"trades": 1, "net_return_pct": 0.1, "max_drawdown_pct": -0.1},
                }
            ]
            source_top_snapshot = json.loads(json.dumps(source_top))
            paths = _write_optuna_artifacts(
                project_root=root,
                signal_mode=" long_only ",
                ts="20260526T202740Z",
                summary_payload={"run_utc": "20260526T202740Z"},
                top_candidates=source_top,
                all_completed_rows=[{"trial_number": 1, "score": 0.2, "backtest": {}}],
                contract_version="  optuna_report_v2_long_top  ",
            )
            self.assertIn("/reports/optuna/long_only/", Path(paths["best_trials_topk_path"]).as_posix())
            topk = json.loads(Path(paths["best_trials_topk_path"]).read_text(encoding="utf-8"))
            self.assertEqual(topk.get("signal_mode"), "long_only")
            self.assertEqual(topk.get("contract_version"), "optuna_report_v2_long_top")
            first = dict(list(topk.get("top_k") or [])[0] or {})
            self.assertEqual(first.get("signal_mode"), "long_only")
            self.assertEqual(first.get("contract_version"), "optuna_report_v2_long_top")
            self.assertEqual(source_top, source_top_snapshot)

    def test_write_optuna_artifacts_short_topk_stale_meta_does_not_leak(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source_top = [
                {
                    "trial_number": 1,
                    "score": 0.2,
                    "signal_mode": "long_only",
                    "contract_version": "stale",
                    "backtest": {"trades": 1, "net_return_pct": 0.1, "max_drawdown_pct": -0.1},
                }
            ]
            source_top_snapshot = json.loads(json.dumps(source_top))
            paths = _write_optuna_artifacts(
                project_root=root,
                signal_mode=" short_only ",
                ts="20260526T202745Z",
                summary_payload={"run_utc": "20260526T202745Z"},
                top_candidates=source_top,
                all_completed_rows=[{"trial_number": 1, "score": 0.2, "backtest": {}}],
                contract_version="  optuna_report_v2_short_top  ",
            )
            self.assertIn("/reports/optuna/short_only/", Path(paths["best_trials_topk_path"]).as_posix())
            topk = json.loads(Path(paths["best_trials_topk_path"]).read_text(encoding="utf-8"))
            self.assertEqual(topk.get("signal_mode"), "short_only")
            self.assertEqual(topk.get("contract_version"), "optuna_report_v2_short_top")
            first = dict(list(topk.get("top_k") or [])[0] or {})
            self.assertEqual(first.get("signal_mode"), "short_only")
            self.assertEqual(first.get("contract_version"), "optuna_report_v2_short_top")
            self.assertEqual(source_top, source_top_snapshot)

    def test_write_optuna_artifacts_rejects_invalid_signal_mode(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(ValueError, "invalid signal_mode"):
                _write_optuna_artifacts(
                    project_root=root,
                    signal_mode="both",
                    ts="20260526T201500Z",
                    summary_payload={},
                    top_candidates=[],
                    all_completed_rows=[],
                )

    def test_write_optuna_artifacts_rejects_empty_contract_version(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaisesRegex(ValueError, "invalid contract_version"):
                _write_optuna_artifacts(
                    project_root=root,
                    signal_mode="long_only",
                    ts="20260526T201550Z",
                    summary_payload={},
                    top_candidates=[],
                    all_completed_rows=[],
                    contract_version="   ",
                )

    def test_write_optuna_artifacts_canonicalizes_signal_mode_from_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source_top = [
                {
                    "trial_number": 1,
                    "score": 0.5,
                    "signal_mode": "long_only",
                    "contract_version": "broken_version",
                    "backtest": {"trades": 1, "net_return_pct": 0.1, "max_drawdown_pct": -0.1},
                }
            ]
            source_top_snapshot = json.loads(json.dumps(source_top))
            paths = _write_optuna_artifacts(
                project_root=root,
                signal_mode="short_only",
                ts="20260526T201700Z",
                summary_payload={
                    "run_utc": "20260526T201700Z",
                    # Intentional drift input; must be overridden by runtime mode.
                    "signal_mode": "long_only",
                },
                top_candidates=source_top,
                all_completed_rows=[
                    {
                        "trial_number": 1,
                        "score": 0.5,
                        "gate_pass": True,
                        "horizon_bars": 2,
                        "p_enter_long": 0.56,
                        "p_enter_short": 0.44,
                        "min_expected_move_pct": 0.001,
                        "notional_usd": 10.0,
                        "trend_filter": "none",
                        "active_blocks": ["trend_momentum"],
                        "enabled_hypotheses": ["ema_cross_20_50"],
                        "feature_columns_count": 8,
                        "fail_keys": [],
                        "backtest": {
                            "trades": 1,
                            "net_return_pct": 0.1,
                            "max_drawdown_pct": -0.1,
                            "hit_rate": 1.0,
                            "trades_per_day_avg": 1.0,
                        },
                    }
                ],
            )
            summary = json.loads(Path(paths["study_summary_path"]).read_text(encoding="utf-8"))
            topk = json.loads(Path(paths["best_trials_topk_path"]).read_text(encoding="utf-8"))
            history = pd.read_csv(Path(paths["trial_history_path"]))
            self.assertIn("/reports/optuna/short_only/", Path(paths["study_summary_path"]).as_posix())
            self.assertIn("/reports/optuna/short_only/", Path(paths["best_trials_topk_path"]).as_posix())
            self.assertIn("/reports/optuna/short_only/", Path(paths["trial_history_path"]).as_posix())
            self.assertEqual(summary.get("signal_mode"), "short_only")
            self.assertEqual(topk.get("signal_mode"), "short_only")
            self.assertEqual(dict(list(topk.get("top_k") or [])[0] or {}).get("signal_mode"), "short_only")
            self.assertEqual(
                dict(list(topk.get("top_k") or [])[0] or {}).get("contract_version"),
                OPTUNA_REPORT_CONTRACT_VERSION,
            )
            self.assertTrue((history["signal_mode"] == "short_only").all())
            self.assertEqual(source_top, source_top_snapshot)

    def test_resource_profile_table_uses_normalized_requested_workers(self) -> None:
        table = _build_resource_profile_table(
            workers_requested=6,
            workers_used=1,
            horizons_count=3,
            cfg={"resources": {"cpu_target_pct": 85, "cpu_ramp_allowed_pct": 35}},
            study_plan={"n_trials": 20, "timeout_sec": 120},
            storage_url="sqlite:///tmp/optuna.db",
            trials_with_signature=[],
        )
        by_metric = {str(x.get("metric")): x for x in table}
        self.assertEqual(int(by_metric["workers_requested"]["value"]), 6)
        self.assertEqual(int(by_metric["workers_used"]["value"]), 1)
        self.assertEqual(str(by_metric["storage_scheme"]["value"]), "sqlite")

    def test_build_resume_report_detects_resume_and_added_trials(self) -> None:
        report = _build_resume_report(
            pre_counts={"total": 10, "completed": 7, "pruned": 2, "failed": 1},
            post_counts={"total": 16, "completed": 11, "pruned": 3, "failed": 2},
        )
        self.assertEqual(str(report.get("scope")), "effective_study_name")
        self.assertTrue(bool(report.get("resumed_from_existing_study")))
        self.assertEqual(int(report.get("added_trials_total", -1)), 6)
        self.assertEqual(int(report.get("added_trials_completed", -1)), 4)
        self.assertEqual(int(report.get("added_trials_pruned", -1)), 1)
        self.assertEqual(int(report.get("added_trials_failed", -1)), 1)

    def test_build_artifact_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            f1 = root / "a.json"
            f2 = root / "b.csv"
            f1.write_text('{"x":1}', encoding="utf-8")
            f2.write_text("c1,c2\n1,2\n", encoding="utf-8")
            hashes = _build_artifact_hashes(
                {
                    "study_summary_path": str(f1),
                    "trial_history_path": str(f2),
                    "missing_path": str(root / "missing.txt"),
                }
            )
            self.assertIn("study_summary_path", hashes)
            self.assertIn("trial_history_path", hashes)
            self.assertNotIn("missing_path", hashes)
            self.assertEqual(len(hashes["study_summary_path"]), 64)
            self.assertEqual(len(hashes["trial_history_path"]), 64)

    def test_build_input_fingerprints(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            cfg = root / "configs"
            cfg.mkdir(parents=True, exist_ok=True)
            f1 = cfg / "optuna_engine.yaml"
            f1.write_text("optuna:\n  enabled: true\n", encoding="utf-8")
            fp = _build_input_fingerprints(
                project_root=root,
                rel_paths=["configs/optuna_engine.yaml", "configs/missing.yaml"],
                metadata={"run_signature": "abc", "stage_effective": "A"},
            )
            files = dict(fp.get("files") or {})
            meta = dict(fp.get("meta") or {})
            meta_hash = str(fp.get("meta_hash") or "")
            self.assertIn("configs/optuna_engine.yaml", files)
            self.assertNotIn("configs/missing.yaml", files)
            self.assertEqual(len(files["configs/optuna_engine.yaml"]), 64)
            self.assertEqual(meta.get("run_signature"), "abc")
            self.assertEqual(meta.get("stage_effective"), "A")
            self.assertEqual(len(meta_hash), 64)

    def test_main_writes_contract_version_consistently_across_artifacts(self) -> None:
        args = argparse.Namespace(
            symbol="SOLUSDT",
            timeframe="1m",
            start_date="2026-05-19",
            end_date="2026-05-19",
            test_day="2026-05-20",
            contour_id="long_only",
            signal_mode="long_only",
            min_train_rows=2200,
            n_folds=4,
            fee_bps=10.0,
            slippage_bps=5.0,
            stop_loss_pct=0.01,
            take_profit_pct=0.02,
            tp_min_factor=0.7,
            min_tp_reach_prob=0.58,
            cooldown_bars=0,
            trend_filter="none",
            min_abs_ema_gap=0.0,
            leverage=1.0,
            execution_mode="research",
            order_type="market",
            limit_offset_bps=2.0,
            horizons_grid="1",
            p_long_grid="0.56",
            p_short_grid="0.44",
            min_expected_move_grid="0.001",
            notional_usd_grid="10",
            min_net_return_pct_goal=1.0,
            workers=1,
            stage="A",
            n_trials_override=1,
            timeout_sec_override=1,
        )

        class _FakeTrial:
            def __init__(self) -> None:
                self.number = 1
                self.state = optuna.trial.TrialState.COMPLETE
                self.value = 1.5
                self.params = {
                    "horizon_bars": 1,
                    "p_enter_long": 0.56,
                    "p_enter_short": 0.44,
                    "min_expected_move_pct": 0.001,
                    "notional_usd": 10.0,
                    "min_abs_ema_gap": 0.0,
                }
                self.user_attrs = {
                    "run_signature": "sig_main_test",
                    "gate_pass": True,
                    "fail_keys": [],
                    "selected_trend_filter": "none",
                    "active_blocks": ["trend_momentum"],
                    "enabled_hypotheses": ["ema_cross_20_50"],
                    "feature_columns_count": 5,
                    "backtest": {
                        "trades": 2,
                        "net_return_pct": 2.4,
                        "max_drawdown_pct": -0.7,
                        "hit_rate": 0.5,
                        "no_trade_ratio_days": 0.0,
                        "trades_per_day_avg": 2.0,
                    },
                    "walk_forward": {"f1_mean": 0.55},
                }

        class _FakeStudy:
            def __init__(self) -> None:
                self.trials = [_FakeTrial()]

            def optimize(self, *args, **kwargs) -> None:
                return None

        printed: list[str] = []

        def _fake_print(msg: str, *args, **kwargs) -> None:
            printed.append(str(msg))

        with (
            patch("mlbotnav.optuna_search_candidate.argparse.ArgumentParser.parse_args", return_value=args),
            patch("mlbotnav.optuna_search_candidate.enforce_action_allowed", return_value=None),
            patch(
                "mlbotnav.optuna_search_candidate.load_optuna_engine_config",
                return_value={"enabled": True, "objective": {}, "resources": {"cpu_target_pct": 85, "cpu_ramp_allowed_pct": 35}},
            ),
            patch(
                "mlbotnav.optuna_search_candidate.build_study_plan",
                return_value={
                    "n_trials": 1,
                    "timeout_sec": 1,
                    "seed": 1,
                    "direction": "maximize",
                    "n_jobs": 1,
                    "sampler": {},
                    "pruner": {},
                    "study_name": "optuna_long_only_smoke",
                },
            ),
            patch("mlbotnav.optuna_search_candidate.resolve_stage_profile", return_value={}),
            patch("mlbotnav.optuna_search_candidate.apply_stage_overrides", side_effect=lambda study_plan, stage_profile: study_plan),
            patch("mlbotnav.optuna_search_candidate.resolve_storage_url", return_value="sqlite:///tmp/optuna_smoke.db"),
            patch("mlbotnav.optuna_search_candidate._load_thresholds", return_value={}),
            patch("mlbotnav.optuna_search_candidate.load_calibration_matrix", return_value={}),
            patch(
                "mlbotnav.optuna_search_candidate.compile_optuna_space",
                return_value={
                    "enabled_blocks": ["trend_momentum"],
                    "hypothesis_rows": [{"hypothesis": "ema_cross_20_50"}],
                    "profiles": {},
                    "constraints": [],
                    "min_enabled_blocks": 1,
                },
            ),
            patch("mlbotnav.optuna_search_candidate.load_ohlcv_range", return_value=pd.DataFrame({"open": [1.0], "high": [1.0], "low": [1.0], "close": [1.0]})),
            patch("mlbotnav.optuna_search_candidate._build_run_signature", return_value="sig_main_test"),
            patch(
                "mlbotnav.optuna_search_candidate.enforce_storage_parallel_compat",
                return_value=(
                    1,
                    {
                        "requested_n_jobs": 1,
                        "effective_n_jobs": 1,
                        "storage_scheme": "sqlite",
                        "forced_single_worker": True,
                        "reason": "sqlite_storage_single_writer",
                    },
                ),
            ),
            patch("mlbotnav.optuna_search_candidate.optuna.create_study", return_value=_FakeStudy()),
            patch("builtins.print", side_effect=_fake_print),
        ):
            rc = osc.main()
            self.assertEqual(rc, 0)

        self.assertTrue(len(printed) >= 1)
        payload = json.loads(printed[-1])
        report_path = Path(str(payload["report_path"]))
        self.assertTrue(report_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report.get("contract_version"), OPTUNA_REPORT_CONTRACT_VERSION)

        artifacts = dict(report.get("optuna_artifacts") or {})
        summary_path = Path(str(artifacts.get("study_summary_path", "")))
        topk_path = Path(str(artifacts.get("best_trials_topk_path", "")))
        history_path = Path(str(artifacts.get("trial_history_path", "")))
        self.assertTrue(summary_path.exists())
        self.assertTrue(topk_path.exists())
        self.assertTrue(history_path.exists())

        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        topk = json.loads(topk_path.read_text(encoding="utf-8"))
        history = pd.read_csv(history_path)
        self.assertEqual(summary.get("contract_version"), OPTUNA_REPORT_CONTRACT_VERSION)
        self.assertEqual(summary.get("signal_mode"), "long_only")
        self.assertEqual(topk.get("contract_version"), OPTUNA_REPORT_CONTRACT_VERSION)
        self.assertIn("contract_version", set(history.columns))
        self.assertIn("signal_mode", set(history.columns))
        self.assertFalse(history.empty)
        self.assertTrue((history["contract_version"] == OPTUNA_REPORT_CONTRACT_VERSION).all())
        self.assertTrue((history["signal_mode"] == "long_only").all())

        for p in [report_path, summary_path, topk_path, history_path]:
            try:
                if p.exists():
                    p.unlink()
            except Exception:
                pass

    def test_main_short_mode_writes_contract_version_consistently_across_artifacts(self) -> None:
        args = argparse.Namespace(
            symbol="SOLUSDT",
            timeframe="1m",
            start_date="2026-05-19",
            end_date="2026-05-19",
            test_day="2026-05-20",
            contour_id="short_only",
            signal_mode="short_only",
            min_train_rows=2200,
            n_folds=4,
            fee_bps=10.0,
            slippage_bps=5.0,
            stop_loss_pct=0.01,
            take_profit_pct=0.02,
            tp_min_factor=0.7,
            min_tp_reach_prob=0.58,
            cooldown_bars=0,
            trend_filter="none",
            min_abs_ema_gap=0.0,
            leverage=1.0,
            execution_mode="research",
            order_type="market",
            limit_offset_bps=2.0,
            horizons_grid="1",
            p_long_grid="0.56",
            p_short_grid="0.44",
            min_expected_move_grid="0.001",
            notional_usd_grid="10",
            min_net_return_pct_goal=1.0,
            workers=1,
            stage="B",
            n_trials_override=1,
            timeout_sec_override=1,
        )

        class _FakeTrial:
            def __init__(self) -> None:
                self.number = 2
                self.state = optuna.trial.TrialState.COMPLETE
                self.value = 1.2
                self.params = {
                    "horizon_bars": 1,
                    "p_enter_long": 0.56,
                    "p_enter_short": 0.44,
                    "min_expected_move_pct": 0.001,
                    "notional_usd": 10.0,
                    "min_abs_ema_gap": 0.0,
                }
                self.user_attrs = {
                    "run_signature": "sig_main_short_test",
                    "gate_pass": True,
                    "fail_keys": [],
                    "selected_trend_filter": "none",
                    "active_blocks": ["trend_momentum"],
                    "enabled_hypotheses": ["ema_cross_20_50"],
                    "feature_columns_count": 5,
                    "backtest": {
                        "trades": 1,
                        "net_return_pct": 1.1,
                        "max_drawdown_pct": -0.5,
                        "hit_rate": 1.0,
                        "no_trade_ratio_days": 0.0,
                        "trades_per_day_avg": 1.0,
                    },
                    "walk_forward": {"f1_mean": 0.51},
                }

        class _FakeStudy:
            def __init__(self) -> None:
                self.trials = [_FakeTrial()]

            def optimize(self, *args, **kwargs) -> None:
                return None

        printed: list[str] = []

        def _fake_print(msg: str, *args, **kwargs) -> None:
            printed.append(str(msg))

        with (
            patch("mlbotnav.optuna_search_candidate.argparse.ArgumentParser.parse_args", return_value=args),
            patch("mlbotnav.optuna_search_candidate.enforce_action_allowed", return_value=None),
            patch(
                "mlbotnav.optuna_search_candidate.load_optuna_engine_config",
                return_value={"enabled": True, "objective": {}, "resources": {"cpu_target_pct": 85, "cpu_ramp_allowed_pct": 35}},
            ),
            patch(
                "mlbotnav.optuna_search_candidate.build_study_plan",
                return_value={
                    "n_trials": 1,
                    "timeout_sec": 1,
                    "seed": 1,
                    "direction": "maximize",
                    "n_jobs": 1,
                    "sampler": {},
                    "pruner": {},
                    "study_name": "optuna_short_only_smoke",
                },
            ),
            patch("mlbotnav.optuna_search_candidate.resolve_stage_profile", return_value={}),
            patch("mlbotnav.optuna_search_candidate.apply_stage_overrides", side_effect=lambda study_plan, stage_profile: study_plan),
            patch("mlbotnav.optuna_search_candidate.resolve_storage_url", return_value="sqlite:///tmp/optuna_smoke.db"),
            patch("mlbotnav.optuna_search_candidate._load_thresholds", return_value={}),
            patch("mlbotnav.optuna_search_candidate.load_calibration_matrix", return_value={}),
            patch(
                "mlbotnav.optuna_search_candidate.compile_optuna_space",
                return_value={
                    "enabled_blocks": ["trend_momentum"],
                    "hypothesis_rows": [{"hypothesis": "ema_cross_20_50"}],
                    "profiles": {},
                    "constraints": [],
                    "min_enabled_blocks": 1,
                },
            ),
            patch("mlbotnav.optuna_search_candidate.load_ohlcv_range", return_value=pd.DataFrame({"open": [1.0], "high": [1.0], "low": [1.0], "close": [1.0]})),
            patch("mlbotnav.optuna_search_candidate._build_run_signature", return_value="sig_main_short_test"),
            patch(
                "mlbotnav.optuna_search_candidate.enforce_storage_parallel_compat",
                return_value=(
                    1,
                    {
                        "requested_n_jobs": 1,
                        "effective_n_jobs": 1,
                        "storage_scheme": "sqlite",
                        "forced_single_worker": True,
                        "reason": "sqlite_storage_single_writer",
                    },
                ),
            ),
            patch("mlbotnav.optuna_search_candidate.optuna.create_study", return_value=_FakeStudy()),
            patch("builtins.print", side_effect=_fake_print),
        ):
            rc = osc.main()
            self.assertEqual(rc, 0)

        self.assertTrue(len(printed) >= 1)
        payload = json.loads(printed[-1])
        report_path = Path(str(payload["report_path"]))
        self.assertTrue(report_path.exists())

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report.get("contract_version"), OPTUNA_REPORT_CONTRACT_VERSION)

        artifacts = dict(report.get("optuna_artifacts") or {})
        summary_path = Path(str(artifacts.get("study_summary_path", "")))
        topk_path = Path(str(artifacts.get("best_trials_topk_path", "")))
        history_path = Path(str(artifacts.get("trial_history_path", "")))
        self.assertTrue(summary_path.exists())
        self.assertTrue(topk_path.exists())
        self.assertTrue(history_path.exists())
        self.assertIn("/reports/optuna/short_only/", summary_path.as_posix())
        self.assertIn("/reports/optuna/short_only/", topk_path.as_posix())
        self.assertIn("/reports/optuna/short_only/", history_path.as_posix())

        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        topk = json.loads(topk_path.read_text(encoding="utf-8"))
        history = pd.read_csv(history_path)
        self.assertEqual(summary.get("contract_version"), OPTUNA_REPORT_CONTRACT_VERSION)
        self.assertEqual(summary.get("signal_mode"), "short_only")
        self.assertEqual(topk.get("contract_version"), OPTUNA_REPORT_CONTRACT_VERSION)
        self.assertEqual(topk.get("signal_mode"), "short_only")
        self.assertIn("contract_version", set(history.columns))
        self.assertIn("signal_mode", set(history.columns))
        self.assertFalse(history.empty)
        self.assertTrue((history["contract_version"] == OPTUNA_REPORT_CONTRACT_VERSION).all())
        self.assertTrue((history["signal_mode"] == "short_only").all())

        for p in [report_path, summary_path, topk_path, history_path]:
            try:
                if p.exists():
                    p.unlink()
            except Exception:
                pass


if __name__ == "__main__":
    unittest.main()
