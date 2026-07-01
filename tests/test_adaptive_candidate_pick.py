from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from mlbotnav.adaptive_auto_train import (
    _candidate_min_move_unreachable,
    _candidate_pool_from_search_report,
    _pick_candidate,
    _read_json_report_with_retry,
    _resolve_effective_repeats,
    _sig,
)


class AdaptiveCandidatePickTests(unittest.TestCase):
    def test_candidate_min_move_unreachable_detects_post_gate_block(self) -> None:
        candidate = {
            "score": 100.0,
            "min_expected_move_pct": 0.01,
            "backtest": {
                "trades": 0,
                "net_return_pct": 0.0,
                "max_drawdown_pct": 0.0,
                "min_expected_move_pct": 0.01,
                "trend_filter_diagnostics": {
                    "signal_count_after_entry_action_gates": 10,
                    "signal_count_after_filter": 10,
                    "signal_count_after_min_move": 0,
                    "entries_filled": 0,
                },
            },
        }

        self.assertTrue(_candidate_min_move_unreachable(candidate))

    def test_pick_candidate_skips_min_move_unreachable_zero_trade_candidate(self) -> None:
        unreachable = {
            "score": 100.0,
            "horizon_bars": 1,
            "p_enter_long": 0.7,
            "p_enter_short": 0.3,
            "min_expected_move_pct": 0.01,
            "backtest": {
                "trades": 0,
                "net_return_pct": 0.0,
                "max_drawdown_pct": 0.0,
                "min_expected_move_pct": 0.01,
                "trend_filter_diagnostics": {
                    "signal_count_after_entry_action_gates": 10,
                    "signal_count_after_filter": 10,
                    "signal_count_after_min_move": 0,
                    "entries_filled": 0,
                },
            },
        }
        reachable = {
            "score": 1.0,
            "horizon_bars": 1,
            "p_enter_long": 0.7,
            "p_enter_short": 0.3,
            "min_expected_move_pct": 0.001,
            "backtest": {"trades": 1, "net_return_pct": -1.0, "max_drawdown_pct": -1.0},
        }

        picked, mode = _pick_candidate(
            candidates=[unreachable, reachable],
            rejected=set(),
            goal_net_return_pct=10.0,
            strict_goal_only=False,
            min_candidate_trades=1,
        )

        self.assertIs(picked, reachable)
        self.assertEqual(mode, "best_tradeful_fallback")

    def test_all_rejected_reuses_best_available_in_non_strict_mode(self) -> None:
        candidates = [
            {"score": -10.0, "backtest": {"trades": 0, "net_return_pct": 0.0, "max_drawdown_pct": 0.0}},
            {"score": -9.0, "backtest": {"trades": 0, "net_return_pct": 0.0, "max_drawdown_pct": 0.0}},
        ]
        rejected = {
            "None|None|None|None|None|None",  # irrelevant shape: signature mismatch must not crash
        }
        # Reject all by using signatures generated from provided candidates.
        rejected = set()
        for c in candidates:
            rejected.add(
                "|".join(
                    [
                        str(c.get("horizon_bars")),
                        str(c.get("p_enter_long")),
                        str(c.get("p_enter_short")),
                        str(c.get("min_expected_move_pct")),
                        str(c.get("trend_filter", "none")),
                        str(c.get("min_abs_ema_gap", 0.0)),
                    ]
                )
            )
        picked, mode = _pick_candidate(
            candidates=candidates,
            rejected=rejected,
            goal_net_return_pct=1.0,
            strict_goal_only=False,
            min_candidate_trades=1,
        )
        self.assertIsNotNone(picked)
        self.assertEqual(mode, "best_available_reuse_all_rejected")

    def test_all_rejected_returns_none_in_strict_mode(self) -> None:
        candidates = [
            {"score": -10.0, "backtest": {"trades": 0, "net_return_pct": 0.0, "max_drawdown_pct": 0.0}},
        ]
        rejected = {
            "|".join(
                [
                    str(candidates[0].get("horizon_bars")),
                    str(candidates[0].get("p_enter_long")),
                    str(candidates[0].get("p_enter_short")),
                    str(candidates[0].get("min_expected_move_pct")),
                    str(candidates[0].get("trend_filter", "none")),
                    str(candidates[0].get("min_abs_ema_gap", 0.0)),
                ]
            )
        }
        picked, mode = _pick_candidate(
            candidates=candidates,
            rejected=rejected,
            goal_net_return_pct=1.0,
            strict_goal_only=True,
            min_candidate_trades=0,
        )
        self.assertIsNone(picked)
        self.assertEqual(mode, "all_rejected")

    def test_candidate_pool_prefers_full_candidates_with_calibration_params(self) -> None:
        search_report = {
            "all_candidates_lite": [
                {
                    "horizon_bars": 8,
                    "p_enter_long": 0.6,
                    "p_enter_short": 0.46,
                    "min_expected_move_pct": 0.002,
                    "score": -10.0,
                    "backtest": {"trades": 1, "net_return_pct": -7.0, "max_drawdown_pct": -7.0},
                }
            ],
            "top_candidates": [
                {
                    "horizon_bars": 8,
                    "p_enter_long": 0.6,
                    "p_enter_short": 0.46,
                    "min_expected_move_pct": 0.002,
                    "score": -10.0,
                    "backtest": {"trades": 1, "net_return_pct": -7.0, "max_drawdown_pct": -7.0},
                    "calibration_params": {"pattern_window": 120.0, "vol_z_window": 40.0},
                }
            ],
        }

        candidates = _candidate_pool_from_search_report(search_report)

        self.assertEqual(candidates[0]["calibration_params"]["pattern_window"], 120.0)

    def test_candidate_signature_includes_calibration_params_when_present(self) -> None:
        base = {
            "horizon_bars": 8,
            "p_enter_long": 0.6,
            "p_enter_short": 0.46,
            "min_expected_move_pct": 0.002,
            "trend_filter": "none",
            "min_abs_ema_gap": 0.0,
        }

        sig_a = _sig({**base, "calibration_params": {"pattern_window": 80.0}})
        sig_b = _sig({**base, "calibration_params": {"pattern_window": 120.0}})

        self.assertNotEqual(sig_a, sig_b)

    def test_resolve_effective_repeats_without_enforce_allows_expansion(self) -> None:
        effective, mismatch = _resolve_effective_repeats(
            requested_repeats=1,
            hypothesis_plan_len=16,
            enforce_requested_equals_effective=False,
        )
        self.assertEqual(effective, 16)
        self.assertTrue(mismatch)

    def test_resolve_effective_repeats_with_enforce_rejects_expansion(self) -> None:
        with self.assertRaises(ValueError):
            _resolve_effective_repeats(
                requested_repeats=1,
                hypothesis_plan_len=16,
                enforce_requested_equals_effective=True,
            )

    def test_resolve_effective_repeats_with_enforce_passes_when_equal(self) -> None:
        effective, mismatch = _resolve_effective_repeats(
            requested_repeats=1,
            hypothesis_plan_len=1,
            enforce_requested_equals_effective=True,
        )
        self.assertEqual(effective, 1)
        self.assertFalse(mismatch)

    def test_read_json_report_with_retry_handles_empty_report(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "empty.json"
            path.write_text("", encoding="utf-8")

            payload, error = _read_json_report_with_retry(path, attempts=1, delay_sec=0)

        self.assertIsNone(payload)
        self.assertIsNotNone(error)
        self.assertIn("empty", str(error))


if __name__ == "__main__":
    unittest.main()
