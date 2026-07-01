from __future__ import annotations

import json
import unittest
from datetime import datetime, timedelta, timezone

import pandas as pd

from mlbotnav.backtest import run_prob_backtest


class BacktestFieldsTests(unittest.TestCase):
    def test_backtest_outputs_ev_and_prob_columns(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(20):
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7 if i % 2 == 0 else 0.3,
                    "future_return": 0.012 if i % 2 == 0 else -0.011,
                }
            )
        oof = pd.DataFrame(rows)
        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            stop_loss_pct=0.01,
            take_profit_pct=0.02,
        )
        for c in ("expected_move_pct", "tp_reach_prob", "sl_hit_prob", "ev", "time_to_target_bars", "time_to_target_sec"):
            self.assertIn(c, trades.columns)
        active = trades[trades["side"] != 0]
        self.assertTrue(((active["tp_reach_prob"] >= 0) & (active["tp_reach_prob"] <= 1)).all())
        self.assertTrue(((active["sl_hit_prob"] >= 0) & (active["sl_hit_prob"] <= 1)).all())
        self.assertIn("avg_ev", summary)
        self.assertIn("sortino", summary)
        self.assertIn("cagr", summary)

    def test_min_tp_reach_prob_gate_blocks_low_confidence_trades(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(20):
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "open": 100.0,
                    "high": 101.0,
                    "low": 99.0,
                    "close": 100.0,
                    "prob_up": 0.55,
                    "future_return": 0.02,
                    "atr14": 0.02,
                }
            )
        oof = pd.DataFrame(rows)
        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.55,
            p_enter_short=0.45,
            min_expected_move_pct=0.0,
            min_tp_reach_prob=0.58,
            execution_mode="exchange_like",
            hold_bars=1,
        )
        self.assertTrue((trades["side"] == 0).all())
        self.assertIn("min_tp_reach_prob", summary)

    def test_exchange_like_min_move_unreachable_after_entry_action_gate_is_diagnosed(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(20):
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "open": 100.0,
                    "high": 101.0,
                    "low": 99.0,
                    "close": 100.0,
                    "prob_up": 0.8,
                    "future_return": 0.01,
                    "atr14": 0.005,
                    "F067_PATTERNSTRENGTH_ALLOW": 1,
                }
            )
        oof = pd.DataFrame(rows)

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.7,
            p_enter_short=0.3,
            min_expected_move_pct=0.01,
            execution_mode="exchange_like",
            signal_mode="long_only",
            hold_bars=1,
        )

        self.assertTrue((trades["side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertEqual(diag["entry_action_gate_columns"], ["F067_PATTERNSTRENGTH_ALLOW"])
        self.assertGreater(int(diag["signal_count_after_entry_action_gates"]), 0)
        self.assertEqual(int(diag["signal_count_after_min_move"]), 0)
        self.assertEqual(int(diag["entries_filled"]), 0)
        self.assertTrue(bool(diag["min_move_unreachable_after_action_gate"]))
        self.assertEqual(diag["min_move_reachability_status"], "MIN_MOVE_UNREACHABLE")
        self.assertAlmostEqual(float(diag["min_move_proxy_after_action_gate_max"]), 0.003, places=6)
        self.assertGreater(
            float(diag["min_expected_move_pct"]),
            float(diag["min_move_proxy_after_action_gate_max"]),
        )

    def test_exchange_like_reachable_min_move_allows_entries_after_action_gate(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(20):
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "open": 100.0,
                    "high": 101.0,
                    "low": 99.0,
                    "close": 100.0,
                    "prob_up": 0.8,
                    "future_return": 0.01,
                    "atr14": 0.005,
                    "F067_PATTERNSTRENGTH_ALLOW": 1,
                }
            )
        oof = pd.DataFrame(rows)

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.7,
            p_enter_short=0.3,
            min_expected_move_pct=0.002,
            execution_mode="exchange_like",
            signal_mode="long_only",
            hold_bars=1,
        )

        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertGreater(int(diag["signal_count_after_entry_action_gates"]), 0)
        self.assertGreater(int(diag["signal_count_after_min_move"]), 0)
        self.assertGreater(int(diag["entries_filled"]), 0)
        self.assertFalse(trades[trades["side"] != 0].empty)
        self.assertFalse(bool(diag["min_move_unreachable_after_action_gate"]))

    def test_f001_ret1_allow_gate_blocks_runtime_entries(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F001_RET1_ALLOW": 1 if i % 2 == 0 else 0,
                }
                for i in range(20)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            stop_loss_pct=0.01,
            take_profit_pct=0.02,
        )

        self.assertTrue((trades.loc[trades["F001_RET1_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("F001_RET1_ALLOW_gate_active")))
        self.assertLess(
            int(diag.get("signal_count_after_f001_ret1_gate", 0)),
            int(diag.get("signal_count_after_mode", 0)),
        )

    def test_entry_action_allow_gate_supports_ret_n_family(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F002_RET3_ALLOW": 1 if i % 3 == 0 else 0,
                }
                for i in range(20)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            stop_loss_pct=0.01,
            take_profit_pct=0.02,
        )

        self.assertTrue((trades.loc[trades["F002_RET3_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(diag.get("entry_action_gate_columns"), ["F002_RET3_ALLOW"])
        self.assertFalse(bool(diag.get("F001_RET1_ALLOW_gate_active")))

    def test_entry_action_allow_gate_supports_n_of_m_confirmations(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F001_RET1_ALLOW": 1 if i % 2 == 0 else 0,
                    "F002_RET3_ALLOW": 1 if i % 3 == 0 else 0,
                }
                for i in range(20)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            stop_loss_pct=0.01,
            take_profit_pct=0.02,
            calibration_params={
                "F001_move": 1,
                "F001_thr_pct": 0.01,
                "F002_move": 1,
                "F002_thr_pct": 0.02,
                "entry_action_min_confirmations": 1,
            },
            active_entry_action_columns=["F001_RET1_ALLOW", "F002_RET3_ALLOW"],
        )

        allowed = (trades["F001_RET1_ALLOW"] >= 1) | (trades["F002_RET3_ALLOW"] >= 1)
        self.assertTrue((trades.loc[~allowed, "side"] == 0).all())
        self.assertGreater(int((trades["side"] != 0).sum()), 0)
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertEqual(diag.get("entry_action_gate_policy"), "n_of_m")
        self.assertEqual(int(diag.get("entry_action_min_confirmations")), 1)
        self.assertEqual(int(diag.get("entry_action_total_columns")), 2)

    def test_entry_action_allow_gate_supports_f006_hlspread(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F006_HLSPREAD_ALLOW": 1 if i % 4 == 0 else 0,
                }
                for i in range(20)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            stop_loss_pct=0.01,
            take_profit_pct=0.02,
        )

        self.assertTrue((trades.loc[trades["F006_HLSPREAD_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(diag.get("entry_action_gate_columns"), ["F006_HLSPREAD_ALLOW"])

    def test_entry_action_allow_gate_supports_f007_rstd20(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F007_RSTD20_ALLOW": 1 if i % 5 == 0 else 0,
                }
                for i in range(20)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            stop_loss_pct=0.01,
            take_profit_pct=0.02,
        )

        self.assertTrue((trades.loc[trades["F007_RSTD20_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(diag.get("entry_action_gate_columns"), ["F007_RSTD20_ALLOW"])

    def test_entry_action_allow_gate_supports_f008_atr14(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F008_ATR14_ALLOW": 1 if i % 6 == 0 else 0,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            stop_loss_pct=0.01,
            take_profit_pct=0.02,
        )

        self.assertTrue((trades.loc[trades["F008_ATR14_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(diag.get("entry_action_gate_columns"), ["F008_ATR14_ALLOW"])

    def test_entry_action_allow_gate_supports_ema_family(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F009_EMAGAP_ALLOW": 1 if i % 4 == 0 else 0,
                    "F010_EMASLOPE5_ALLOW": 1,
                    "F011_EMA200GAP_ALLOW": 1,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F009_EMAGAP_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(
            diag.get("entry_action_gate_columns"),
            ["F009_EMAGAP_ALLOW", "F010_EMASLOPE5_ALLOW", "F011_EMA200GAP_ALLOW"],
        )

    def test_entry_action_allow_gate_supports_f012_rsi14(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F012_RSI14_ALLOW": 1 if i % 5 == 0 else 0,
                }
                for i in range(25)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F012_RSI14_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(diag.get("entry_action_gate_columns"), ["F012_RSI14_ALLOW"])

    def test_entry_action_allow_gate_supports_macd_family(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F013_MACDLINE_ALLOW": 1 if i % 4 == 0 else 0,
                    "F014_MACDSIGNAL_ALLOW": 1,
                    "F015_MACDHIST_ALLOW": 1,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F013_MACDLINE_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(
            diag.get("entry_action_gate_columns"),
            ["F013_MACDLINE_ALLOW", "F014_MACDSIGNAL_ALLOW", "F015_MACDHIST_ALLOW"],
        )

    def test_entry_action_allow_gate_supports_f016_adx14(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F016_ADX14_ALLOW": 1 if i % 3 == 0 else 0,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F016_ADX14_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(diag.get("entry_action_gate_columns"), ["F016_ADX14_ALLOW"])

    def test_entry_action_allow_gate_supports_f017_f018_stoch14(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F017_F018_STOCH14_ALLOW": 1 if i % 4 == 0 else 0,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F017_F018_STOCH14_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(diag.get("entry_action_gate_columns"), ["F017_F018_STOCH14_ALLOW"])

    def test_entry_action_allow_gate_supports_volume_family(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F019_VOLCHG_ALLOW": 1 if i % 4 == 0 else 0,
                    "F020_VOLZ20_ALLOW": 1,
                    "F021_DELTAVOL_ALLOW": 1,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F019_VOLCHG_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(
            diag.get("entry_action_gate_columns"),
            ["F019_VOLCHG_ALLOW", "F020_VOLZ20_ALLOW", "F021_DELTAVOL_ALLOW"],
        )

    def test_entry_action_allow_gate_supports_f022_obv_slope5(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F022_OBVSLOPE5_ALLOW": 1 if i % 5 == 0 else 0,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F022_OBVSLOPE5_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(diag.get("entry_action_gate_columns"), ["F022_OBVSLOPE5_ALLOW"])

    def test_entry_action_allow_gate_supports_f023_mfi14(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F023_MFI14_ALLOW": 1 if i % 6 == 0 else 0,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F023_MFI14_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(diag.get("entry_action_gate_columns"), ["F023_MFI14_ALLOW"])

    def test_entry_action_allow_gate_supports_f024_vwap_distance(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F024_VWAPDIST_ALLOW": 1 if i % 5 == 0 else 0,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F024_VWAPDIST_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(diag.get("entry_action_gate_columns"), ["F024_VWAPDIST_ALLOW"])

    def test_entry_action_allow_gate_supports_density_vpoc_core(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F025_VPOCDIST60_ALLOW": 1 if i % 4 == 0 else 0,
                    "F029_VPOCDIST240_ALLOW": 1,
                    "F033_VPOCDRIFT20_ALLOW": 1,
                    "F034_CLUSTERRATIO_ALLOW": 1,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F025_VPOCDIST60_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(
            diag.get("entry_action_gate_columns"),
            [
                "F025_VPOCDIST60_ALLOW",
                "F029_VPOCDIST240_ALLOW",
                "F033_VPOCDRIFT20_ALLOW",
                "F034_CLUSTERRATIO_ALLOW",
            ],
        )

    def test_entry_action_allow_gate_supports_f026_bin_share60(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F026_BINSHARE60_ALLOW": 1 if i % 4 == 0 else 0,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F026_BINSHARE60_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(diag.get("entry_action_gate_columns"), ["F026_BINSHARE60_ALLOW"])

    def test_entry_action_allow_gate_supports_f027_cluster_share60(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F027_CLUSTERSHARE60_ALLOW": 1 if i % 4 == 0 else 0,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F027_CLUSTERSHARE60_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(diag.get("entry_action_gate_columns"), ["F027_CLUSTERSHARE60_ALLOW"])

    def test_entry_action_allow_gate_supports_f028_vpoc_share60(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F028_VPOCSHARE60_ALLOW": 1 if i % 4 == 0 else 0,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F028_VPOCSHARE60_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(diag.get("entry_action_gate_columns"), ["F028_VPOCSHARE60_ALLOW"])

    def test_entry_action_allow_gate_supports_f030_bin_share240(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F030_BINSHARE240_ALLOW": 1 if i % 4 == 0 else 0,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F030_BINSHARE240_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(diag.get("entry_action_gate_columns"), ["F030_BINSHARE240_ALLOW"])

    def test_entry_action_allow_gate_supports_f031_cluster_share240(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F031_CLUSTERSHARE240_ALLOW": 1 if i % 4 == 0 else 0,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F031_CLUSTERSHARE240_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(diag.get("entry_action_gate_columns"), ["F031_CLUSTERSHARE240_ALLOW"])

    def test_entry_action_allow_gate_supports_f032_vpoc_share240(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F032_VPOCSHARE240_ALLOW": 1 if i % 4 == 0 else 0,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F032_VPOCSHARE240_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(diag.get("entry_action_gate_columns"), ["F032_VPOCSHARE240_ALLOW"])

    def test_entry_action_allow_gate_supports_level_range_channel_block_a(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F035_SUPPORTDIST_ALLOW": 1 if i % 4 == 0 else 0,
                    "F036_RESDIST_ALLOW": 1,
                    "F037_LEVELSTRENGTH_ALLOW": 1,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F035_SUPPORTDIST_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(
            diag.get("entry_action_gate_columns"),
            ["F035_SUPPORTDIST_ALLOW", "F036_RESDIST_ALLOW", "F037_LEVELSTRENGTH_ALLOW"],
        )

    def test_entry_action_allow_gate_supports_f038_range_position(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F038_RANGEPOSE_ALLOW": 1 if i % 4 == 0 else 0,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F038_RANGEPOSE_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(diag.get("entry_action_gate_columns"), ["F038_RANGEPOSE_ALLOW"])

    def test_entry_action_allow_gate_supports_f039_channel_position(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F039_CHANNELPOS_ALLOW": 1 if i % 4 == 0 else 0,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F039_CHANNELPOS_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(diag.get("entry_action_gate_columns"), ["F039_CHANNELPOS_ALLOW"])

    def test_entry_action_allow_gate_ignores_stale_columns_when_passport_params_identify_active_action(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F038_RANGEPOSE_ALLOW": 0,
                    "F039_CHANNELPOS_ALLOW": 1,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
            calibration_params={"F039_zone": 1, "F039_level": 40, "F039_outside_thr": 0},
        )

        self.assertTrue((trades["side"] > 0).any())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertEqual(diag.get("entry_action_gate_columns"), ["F039_CHANNELPOS_ALLOW"])
        self.assertEqual(diag.get("entry_action_gate_ignored_columns"), ["F038_RANGEPOSE_ALLOW"])
        self.assertEqual(diag.get("entry_action_gate_inferred_prefixes"), ["F039"])

    def test_entry_action_allow_gate_supports_fibonacci_grid(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F040_FIB0382DIST_ALLOW": 1 if i % 4 == 0 else 0,
                    "F041_FIB0618DIST_ALLOW": 1,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        self.assertTrue((trades.loc[trades["F040_FIB0382DIST_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(
            diag.get("entry_action_gate_columns"),
            ["F040_FIB0382DIST_ALLOW", "F041_FIB0618DIST_ALLOW"],
        )

    def test_entry_quality_context_gate_uses_signal_side_columns(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F042_TPCONTEXT_ALLOW": 1,
                    "F042_TPCONTEXT_ALLOW_LONG": 1 if i % 4 == 0 else 0,
                    "F042_TPCONTEXT_ALLOW_SHORT": 1,
                    "F043_SLCONTEXT_ALLOW": 1,
                    "F043_SLCONTEXT_ALLOW_LONG": 1,
                    "F043_SLCONTEXT_ALLOW_SHORT": 1,
                    "F044_RRCONTEXT_ALLOW": 1,
                    "F044_RRCONTEXT_ALLOW_LONG": 1,
                    "F044_RRCONTEXT_ALLOW_SHORT": 1,
                }
                for i in range(24)
            ]
        )

        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.6,
            p_enter_short=0.4,
            min_expected_move_pct=0.0,
            signal_mode="long_only",
        )

        blocked_long = trades["F042_TPCONTEXT_ALLOW_LONG"] == 0
        self.assertTrue((trades.loc[blocked_long, "side"] == 0).all())
        self.assertTrue((trades.loc[trades["F042_TPCONTEXT_ALLOW_SHORT"] == 1, "F042_TPCONTEXT_ALLOW"] == 1).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertEqual(
            diag.get("entry_action_gate_columns"),
            ["F042_TPCONTEXT_ALLOW", "F043_SLCONTEXT_ALLOW", "F044_RRCONTEXT_ALLOW"],
        )

    def test_breakout_retest_gate_uses_passport_action_columns(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F045_BREAKOUT_ALLOW": 1,
                    "F046_FALSEBREAK_ALLOW": 1,
                    "F047_RETEST_ALLOW": 1,
                    "F048_SWINGHIGHBREAK_ALLOW": 1 if i % 4 == 0 else 0,
                    "F049_SWINGLOWBREAK_ALLOW": 1,
                }
                for i in range(24)
            ]
        )
        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.55,
            p_enter_short=0.45,
            execution_mode="signal_bar_close",
        )

        self.assertTrue((trades.loc[trades["F048_SWINGHIGHBREAK_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(
            diag.get("entry_action_gate_columns"),
            [
                "F045_BREAKOUT_ALLOW",
                "F046_FALSEBREAK_ALLOW",
                "F047_RETEST_ALLOW",
                "F048_SWINGHIGHBREAK_ALLOW",
                "F049_SWINGLOWBREAK_ALLOW",
            ],
        )

    def test_market_structure_gate_uses_passport_action_columns(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F050_BOSUP_ALLOW": 1,
                    "F051_BOSDOWN_ALLOW": 1 if i % 3 == 0 else 0,
                    "F052_CHOCH_ALLOW": 1,
                }
                for i in range(24)
            ]
        )
        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.55,
            p_enter_short=0.45,
            execution_mode="signal_bar_close",
        )

        self.assertTrue((trades.loc[trades["F051_BOSDOWN_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(
            diag.get("entry_action_gate_columns"),
            ["F050_BOSUP_ALLOW", "F051_BOSDOWN_ALLOW", "F052_CHOCH_ALLOW"],
        )

    def test_candle_pattern_gate_uses_passport_action_columns(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F053_DOJI_ALLOW": 1,
                    "F054_INSIDEBAR_ALLOW": 1,
                    "F055_PINBULL_ALLOW": 1,
                    "F056_PINBEAR_ALLOW": 1,
                    "F057_HAMMER_ALLOW": 1,
                    "F058_SHOOTINGSTAR_ALLOW": 1 if i % 4 == 0 else 0,
                    "F059_ENGULFBULL_ALLOW": 1,
                    "F060_ENGULFBEAR_ALLOW": 1,
                }
                for i in range(24)
            ]
        )
        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.55,
            p_enter_short=0.45,
            execution_mode="signal_bar_close",
        )

        self.assertTrue((trades.loc[trades["F058_SHOOTINGSTAR_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(
            diag.get("entry_action_gate_columns"),
            [
                "F053_DOJI_ALLOW",
                "F054_INSIDEBAR_ALLOW",
                "F055_PINBULL_ALLOW",
                "F056_PINBEAR_ALLOW",
                "F057_HAMMER_ALLOW",
                "F058_SHOOTINGSTAR_ALLOW",
                "F059_ENGULFBULL_ALLOW",
                "F060_ENGULFBEAR_ALLOW",
            ],
        )

    def test_divergence_pattern_gate_uses_passport_action_columns(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F061_RSIBULLDIV_ALLOW": 1,
                    "F062_RSIBEARDIV_ALLOW": 1,
                    "F063_MACDBULLDIV_ALLOW": 1,
                    "F064_MACDBEARDIV_ALLOW": 1 if i % 5 == 0 else 0,
                    "F065_OBVBULLDIV_ALLOW": 1,
                    "F066_OBVBEARDIV_ALLOW": 1,
                }
                for i in range(25)
            ]
        )
        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.55,
            p_enter_short=0.45,
            execution_mode="signal_bar_close",
        )

        self.assertTrue((trades.loc[trades["F064_MACDBEARDIV_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(
            diag.get("entry_action_gate_columns"),
            [
                "F061_RSIBULLDIV_ALLOW",
                "F062_RSIBEARDIV_ALLOW",
                "F063_MACDBULLDIV_ALLOW",
                "F064_MACDBEARDIV_ALLOW",
                "F065_OBVBULLDIV_ALLOW",
                "F066_OBVBEARDIV_ALLOW",
            ],
        )

    def test_pattern_quality_gate_uses_passport_action_columns(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F067_PATTERNSTRENGTH_ALLOW": 1,
                    "F068_PATTERNAGE_ALLOW": 1 if i % 4 != 0 else 0,
                }
                for i in range(25)
            ]
        )
        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.55,
            p_enter_short=0.45,
            execution_mode="signal_bar_close",
        )

        self.assertTrue((trades.loc[trades["F068_PATTERNAGE_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(
            diag.get("entry_action_gate_columns"),
            [
                "F067_PATTERNSTRENGTH_ALLOW",
                "F068_PATTERNAGE_ALLOW",
            ],
        )

    def test_chart_pattern_gate_uses_passport_action_columns(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F069_DOUBLEBOTTOM_ALLOW": 1,
                    "F070_DOUBLETOP_ALLOW": 1,
                    "F071_HEADSHOULDERS_ALLOW": 1,
                    "F072_INVHEADSHOULDERS_ALLOW": 1,
                    "F073_TRIANGLE_ALLOW": 1,
                    "F074_PENNANT_ALLOW": 1,
                    "F075_WEDGERISING_ALLOW": 1,
                    "F076_WEDGEFALLING_ALLOW": 1,
                    "F077_RANGEFLAG_ALLOW": 1 if i % 6 != 0 else 0,
                }
                for i in range(30)
            ]
        )
        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.55,
            p_enter_short=0.45,
            execution_mode="signal_bar_close",
        )

        self.assertTrue((trades.loc[trades["F077_RANGEFLAG_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(
            diag.get("entry_action_gate_columns"),
            [
                "F069_DOUBLEBOTTOM_ALLOW",
                "F070_DOUBLETOP_ALLOW",
                "F071_HEADSHOULDERS_ALLOW",
                "F072_INVHEADSHOULDERS_ALLOW",
                "F073_TRIANGLE_ALLOW",
                "F074_PENNANT_ALLOW",
                "F075_WEDGERISING_ALLOW",
                "F076_WEDGEFALLING_ALLOW",
                "F077_RANGEFLAG_ALLOW",
            ],
        )

    def test_pattern_confirmation_gate_uses_passport_action_columns(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7,
                    "future_return": 0.01,
                    "F078_PATTERNVOLCONF_ALLOW": 1,
                    "F079_PATTERNLEVELCONF_ALLOW": 1 if i % 5 != 0 else 0,
                }
                for i in range(30)
            ]
        )
        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.55,
            p_enter_short=0.45,
            execution_mode="signal_bar_close",
        )

        self.assertTrue((trades.loc[trades["F079_PATTERNLEVELCONF_ALLOW"] == 0, "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(
            diag.get("entry_action_gate_columns"),
            [
                "F078_PATTERNVOLCONF_ALLOW",
                "F079_PATTERNLEVELCONF_ALLOW",
            ],
        )

    def test_pattern_composite_entry_gate_uses_side_specific_action_columns(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(30):
            is_long_signal = i % 2 == 0
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7 if is_long_signal else 0.3,
                    "future_return": 0.01 if is_long_signal else -0.01,
                    "F080_PATTERNLONG_ALLOW": 1 if (not is_long_signal or i % 4 != 0) else 0,
                    "F081_PATTERNSHORT_ALLOW": 1 if (is_long_signal or i % 3 != 1) else 0,
                }
            )
        oof = pd.DataFrame(rows)
        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.55,
            p_enter_short=0.45,
            min_expected_move_pct=0.0,
            execution_mode="signal_bar_close",
        )

        self.assertTrue((trades.loc[(trades["prob_up"] > 0.5) & (trades["F080_PATTERNLONG_ALLOW"] == 0), "side"] == 0).all())
        self.assertTrue((trades.loc[(trades["prob_up"] < 0.5) & (trades["F081_PATTERNSHORT_ALLOW"] == 0), "side"] == 0).all())
        self.assertTrue((trades.loc[(trades["prob_up"] > 0.5) & (trades["F081_PATTERNSHORT_ALLOW"] == 0), "side"] >= 0).all())
        self.assertTrue((trades.loc[(trades["prob_up"] < 0.5) & (trades["F080_PATTERNLONG_ALLOW"] == 0), "side"] <= 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(
            diag.get("entry_action_gate_columns"),
            [
                "F080_PATTERNLONG_ALLOW",
                "F081_PATTERNSHORT_ALLOW",
            ],
        )

    def test_pattern_trade_context_gate_uses_side_aware_action_columns(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(30):
            is_long_signal = i % 2 == 0
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.7 if is_long_signal else 0.3,
                    "future_return": 0.01 if is_long_signal else -0.01,
                    "F082_PATTERNSLBUF_ALLOW": 1,
                    "F082_PATTERNSLBUF_ALLOW_LONG": 1 if (not is_long_signal or i % 4 != 0) else 0,
                    "F082_PATTERNSLBUF_ALLOW_SHORT": 1 if (is_long_signal or i % 3 != 1) else 0,
                    "F083_PATTERNTPLADDER_ALLOW": 1,
                    "F083_PATTERNTPLADDER_ALLOW_LONG": 1,
                    "F083_PATTERNTPLADDER_ALLOW_SHORT": 1,
                }
            )
        oof = pd.DataFrame(rows)
        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.55,
            p_enter_short=0.45,
            min_expected_move_pct=0.0,
            execution_mode="signal_bar_close",
        )

        self.assertTrue((trades.loc[(trades["prob_up"] > 0.5) & (trades["F082_PATTERNSLBUF_ALLOW_LONG"] == 0), "side"] == 0).all())
        self.assertTrue((trades.loc[(trades["prob_up"] < 0.5) & (trades["F082_PATTERNSLBUF_ALLOW_SHORT"] == 0), "side"] == 0).all())
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertTrue(bool(diag.get("entry_action_gate_active")))
        self.assertEqual(
            diag.get("entry_action_gate_columns"),
            [
                "F082_PATTERNSLBUF_ALLOW",
                "F083_PATTERNTPLADDER_ALLOW",
            ],
        )

    def test_dynamic_tp_event_ladder_records_updates(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        rows = []
        px = 100.0
        for i in range(12):
            px = px * 1.01
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "open": px,
                    "high": px * 1.01,
                    "low": px * 0.999,
                    "close": px * 1.005,
                    "prob_up": 0.9,
                    "future_return": 0.03,
                    "atr14": 0.03,
                }
            )
        oof = pd.DataFrame(rows)
        trades, _summary = run_prob_backtest(
            oof,
            p_enter_long=0.55,
            p_enter_short=0.45,
            min_expected_move_pct=0.0,
            min_tp_reach_prob=0.58,
            execution_mode="exchange_like",
            hold_bars=4,
            dynamic_tp_enabled=True,
            take_profit_pct=0.01,
            tp_min_factor=0.7,
        )
        active = trades[trades["side"] != 0]
        self.assertFalse(active.empty)
        self.assertIn("dynamic_tp_update_count", active.columns)
        self.assertIn("dynamic_tp_events_json", active.columns)
        self.assertTrue((active["dynamic_tp_initial_pct"] <= active["dynamic_tp_pct"]).all())
        has_eventful = active[active["dynamic_tp_update_count"] > 0]
        self.assertFalse(has_eventful.empty)
        events = json.loads(has_eventful.iloc[0]["dynamic_tp_events_json"])
        self.assertGreater(len(events), 0)

    def test_exchange_like_can_disable_timeout_exit(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(8):
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "open": 100.0,
                    "high": 100.1,
                    "low": 99.9,
                    "close": 100.0 + i * 0.01,
                    "prob_up": 0.9,
                    "future_return": 0.0,
                    "atr14": 0.001,
                }
            )
        oof = pd.DataFrame(rows)
        trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.55,
            p_enter_short=0.45,
            execution_mode="exchange_like",
            hold_bars=1,
            take_profit_pct=0.50,
            stop_loss_pct=0.50,
            timeout_exit_enabled=False,
        )

        active = trades[trades["side"] != 0]
        self.assertEqual(len(active), 1)
        self.assertEqual(str(active.iloc[0]["exit_reason"]), "end_of_data")
        self.assertFalse(bool(summary["timeout_exit_enabled"]))

    def test_min_expected_move_pct_percent_point_input_normalized_to_fraction(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.8,
                    "future_return": 0.02,
                    "atr14": 0.02,
                }
                for i in range(20)
            ]
        )
        _trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.55,
            p_enter_short=0.45,
            min_expected_move_pct=1.0,  # 1% legacy percent-point notation
        )
        self.assertAlmostEqual(float(summary["min_expected_move_pct"]), 0.01, places=12)

    def test_trend_filter_diagnostics_report_missing_columns(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.8 if i % 2 == 0 else 0.2,
                    "future_return": 0.01 if i % 2 == 0 else -0.01,
                }
                for i in range(20)
            ]
        )
        _trades, summary = run_prob_backtest(
            oof,
            p_enter_long=0.55,
            p_enter_short=0.45,
            trend_filter="ema_cross_20_50",
            require_trend_filter_features=False,
        )
        diag = dict(summary.get("trend_filter_diagnostics") or {})
        self.assertEqual(diag.get("trend_filter_normalized"), "ema_cross_20_50")
        self.assertTrue(bool(diag.get("trend_filter_degraded_noop_risk")))
        self.assertEqual(diag.get("trend_filter_missing_columns"), ["ema20", "ema50"])
        self.assertEqual(
            int(diag.get("signal_count_after_filter", -1)),
            int(diag.get("signal_count_after_mode", -2)),
        )

    def test_trend_filter_strict_guard_raises_on_missing_columns(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        oof = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "prob_up": 0.8 if i % 2 == 0 else 0.2,
                    "future_return": 0.01 if i % 2 == 0 else -0.01,
                }
                for i in range(20)
            ]
        )
        with self.assertRaisesRegex(RuntimeError, "missing in OOF/backtest frame"):
            run_prob_backtest(
                oof,
                p_enter_long=0.55,
                p_enter_short=0.45,
                trend_filter="ema_cross_20_50",
                require_trend_filter_features=True,
            )


if __name__ == "__main__":
    unittest.main()
