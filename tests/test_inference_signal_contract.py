from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from mlbotnav.inference import build_inference_events_frame
from mlbotnav.runtime_contract import CALIBRATION_MODE_NONE, SIGNAL_CONTRACT_VERSION


class InferenceSignalContractTests(unittest.TestCase):
    def test_build_inference_events_frame_contains_canonical_fields(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        feat = pd.DataFrame(
            [
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "open": 100.0 + i,
                    "high": 101.0 + i,
                    "low": 99.0 + i,
                    "close": 100.5 + i,
                    "volume": 10.0 + i,
                    "atr14": 0.02,
                }
                for i in range(3)
            ]
        )
        probs = np.array([0.8, 0.5, 0.2], dtype=float)
        out = build_inference_events_frame(
            feat,
            probs,
            symbol="SOLUSDT",
            timeframe="1m",
            p_long=0.55,
            p_short=0.45,
            horizon_bars=1,
            stop_loss_pct=0.01,
            take_profit_pct=0.02,
            min_expected_move_pct=0.003,
            min_tp_reach_prob=0.58,
            dynamic_tp_enabled=True,
            tp_min_factor=0.7,
            run_id="20260526T000000Z",
        )
        required = {
            "signal_id",
            "symbol",
            "timeframe",
            "signal_time_utc",
            "side",
            "entry_price",
            "stop_price",
            "take_profit_price",
            "expected_move_pct",
            "tp_reach_prob",
            "decision",
            "reason_code",
            "run_id",
        }
        self.assertTrue(required.issubset(set(out.columns)))
        self.assertEqual(out.iloc[0]["decision"], "BUY")
        self.assertEqual(out.iloc[1]["decision"], "NO_TRADE")
        self.assertEqual(out.iloc[2]["decision"], "NO_TRADE")
        self.assertEqual(out.iloc[2]["reason_code"], "no_next_candle")
        self.assertAlmostEqual(float(out.iloc[0]["entry_price"]), float(feat.iloc[1]["open"]))
        self.assertAlmostEqual(float(out.iloc[1]["entry_price"]), float(feat.iloc[2]["open"]))
        self.assertTrue((out["contract_version"] == SIGNAL_CONTRACT_VERSION).all())
        self.assertTrue((out["calibration_mode"] == CALIBRATION_MODE_NONE).all())

    def test_min_expected_move_gate_sets_no_trade_reason(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        feat = pd.DataFrame(
            [
                {
                    "open_time_utc": t0,
                    "open": 100.0,
                    "high": 101.0,
                    "low": 99.0,
                    "close": 100.5,
                    "volume": 10.0,
                    "atr14": 0.001,
                },
                {
                    "open_time_utc": t0 + timedelta(minutes=1),
                    "open": 100.1,
                    "high": 101.1,
                    "low": 99.1,
                    "close": 100.6,
                    "volume": 11.0,
                    "atr14": 0.001,
                },
            ]
        )
        out = build_inference_events_frame(
            feat,
            np.array([0.9, 0.5], dtype=float),
            symbol="SOLUSDT",
            timeframe="1m",
            p_long=0.55,
            p_short=0.45,
            horizon_bars=1,
            stop_loss_pct=0.01,
            take_profit_pct=0.02,
            min_expected_move_pct=0.01,
            min_tp_reach_prob=0.58,
            dynamic_tp_enabled=True,
            tp_min_factor=0.7,
            run_id="20260526T000000Z",
        )
        self.assertEqual(int(out.iloc[0]["side"]), 0)
        self.assertEqual(out.iloc[0]["decision"], "NO_TRADE")
        self.assertEqual(out.iloc[0]["reason_code"], "min_move_fail")

    def test_last_candle_without_next_open_forces_no_trade(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        feat = pd.DataFrame(
            [
                {
                    "open_time_utc": t0,
                    "open": 100.0,
                    "high": 101.0,
                    "low": 99.0,
                    "close": 100.5,
                    "volume": 10.0,
                    "atr14": 0.02,
                }
            ]
        )
        out = build_inference_events_frame(
            feat,
            np.array([0.9], dtype=float),
            symbol="SOLUSDT",
            timeframe="1m",
            p_long=0.55,
            p_short=0.45,
            horizon_bars=1,
            stop_loss_pct=0.01,
            take_profit_pct=0.02,
            min_expected_move_pct=0.003,
            min_tp_reach_prob=0.58,
            dynamic_tp_enabled=True,
            tp_min_factor=0.7,
            run_id="20260526T000000Z",
        )
        self.assertEqual(int(out.iloc[0]["side"]), 0)
        self.assertEqual(out.iloc[0]["reason_code"], "no_next_candle")

    def test_low_tp_probability_forces_no_trade_reason(self) -> None:
        t0 = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
        feat = pd.DataFrame(
            [
                {
                    "open_time_utc": t0,
                    "open": 100.0,
                    "high": 101.0,
                    "low": 99.0,
                    "close": 100.5,
                    "volume": 10.0,
                    "atr14": 0.05,
                },
                {
                    "open_time_utc": t0 + timedelta(minutes=1),
                    "open": 100.1,
                    "high": 101.1,
                    "low": 99.1,
                    "close": 100.6,
                    "volume": 11.0,
                    "atr14": 0.05,
                },
            ]
        )
        out = build_inference_events_frame(
            feat,
            np.array([0.55, 0.5], dtype=float),
            symbol="SOLUSDT",
            timeframe="1m",
            p_long=0.55,
            p_short=0.45,
            horizon_bars=1,
            stop_loss_pct=0.01,
            take_profit_pct=0.02,
            min_expected_move_pct=0.003,
            min_tp_reach_prob=0.58,
            dynamic_tp_enabled=True,
            tp_min_factor=0.7,
            run_id="20260526T000000Z",
        )
        self.assertEqual(int(out.iloc[0]["side"]), 0)
        self.assertEqual(out.iloc[0]["decision"], "NO_TRADE")
        self.assertEqual(out.iloc[0]["reason_code"], "tp_prob_below_min")


if __name__ == "__main__":
    unittest.main()
