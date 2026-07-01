from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from mlbotnav.technical_analysis import (
    _apply_pattern_density_controls,
    _build_signals,
    _load_ta_profile,
)
from mlbotnav.runtime_contract import CALIBRATION_MODE_NONE, SIGNAL_CONTRACT_VERSION


def _make_ohlcv(n: int = 120) -> pd.DataFrame:
    ts0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
    rows = []
    px = 100.0
    for i in range(n):
        px = px * (1.0005 if i % 3 else 1.0015)
        high = px * 1.001
        low = px * 0.999
        close = px
        open_ = px * (0.9995 if i % 2 else 1.0005)
        rows.append(
            {
                "open_time_utc": ts0 + timedelta(minutes=i),
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": 1000 + i,
            }
        )
    return pd.DataFrame(rows)


class TechnicalAnalysisTests(unittest.TestCase):
    def test_profile_deep_merge(self) -> None:
        root = Path(__file__).resolve().parents[1]
        cfg = _load_ta_profile(root, "1m")
        self.assertIn("pattern_detection", cfg)
        self.assertIn("signal", cfg)
        self.assertIn("density_controls", cfg)
        # key from default should remain after profile override
        self.assertIn("double_tolerance", cfg["pattern_detection"])

    def test_density_control_caps_per_day_type(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        frame = pd.DataFrame(
            {
                "pattern_id": [f"p{i}" for i in range(200)],
                "symbol": ["SOLUSDT"] * 200,
                "timeframe": ["1m"] * 200,
                "pattern_type": ["range"] * 200,
                "direction": ["neutral"] * 200,
                "start_time_utc": [(t0 + timedelta(minutes=i)).isoformat() for i in range(200)],
                "end_time_utc": [(t0 + timedelta(minutes=i)).isoformat() for i in range(200)],
                "confidence_score": np.linspace(0.0, 1.0, 200),
                "target_price": [100.0] * 200,
                "stop_price": [99.0] * 200,
                "invalidation_price": [99.0] * 200,
                "run_id": ["r1"] * 200,
            }
        )
        cfg = {"density_controls": {"enabled": True, "default_max_events_per_day": 50, "per_pattern_type": {"range": 30}}}
        out = _apply_pattern_density_controls(frame, ta_cfg=cfg)
        self.assertEqual(len(out), 30)
        self.assertGreaterEqual(out["confidence_score"].min(), 0.84)

    def test_signal_invariants_force_no_trade_under_strict_rr(self) -> None:
        ohlcv = _make_ohlcv(120)
        # build simple level context
        levels = pd.DataFrame(
            {
                "level_id": ["l1", "l2"],
                "symbol": ["SOLUSDT", "SOLUSDT"],
                "timeframe": ["1m", "1m"],
                "detected_at_utc": [ohlcv["open_time_utc"].iloc[20].isoformat(), ohlcv["open_time_utc"].iloc[20].isoformat()],
                "level_price": [float(ohlcv["close"].iloc[20] * 0.99), float(ohlcv["close"].iloc[20] * 1.01)],
                "level_type": ["support", "resistance"],
                "strength_score": [0.9, 0.9],
                "touches_count": [5, 5],
                "valid_from_utc": [ohlcv["open_time_utc"].iloc[20].isoformat(), ohlcv["open_time_utc"].iloc[20].isoformat()],
                "valid_to_utc": [ohlcv["open_time_utc"].iloc[110].isoformat(), ohlcv["open_time_utc"].iloc[110].isoformat()],
                "run_id": ["r1", "r1"],
            }
        )
        patterns = pd.DataFrame()
        ta_cfg = {"signal": {"adx_min": 1.0, "mfi_long_min": 0.0, "mfi_short_max": 100.0, "rr_min": 100.0, "enable_structure_fallback": False}}
        signals, _fallback = _build_signals(
            ohlcv,
            symbol="SOLUSDT",
            timeframe="1m",
            run_id="r1",
            levels_df=levels,
            patterns_df=patterns,
            ta_cfg=ta_cfg,
            min_tp_pct=0.01,
            min_expected_move_pct=0.002,
        )
        self.assertTrue((signals["decision"] == "NO_TRADE").all())
        self.assertTrue((signals["side"] == 0).all())

    def test_signal_entry_price_uses_next_candle_open(self) -> None:
        ohlcv = _make_ohlcv(120)
        levels = pd.DataFrame(
            {
                "level_id": ["l1", "l2"],
                "symbol": ["SOLUSDT", "SOLUSDT"],
                "timeframe": ["1m", "1m"],
                "detected_at_utc": [ohlcv["open_time_utc"].iloc[20].isoformat(), ohlcv["open_time_utc"].iloc[20].isoformat()],
                "level_price": [float(ohlcv["close"].iloc[20] * 0.99), float(ohlcv["close"].iloc[20] * 1.01)],
                "level_type": ["support", "resistance"],
                "strength_score": [0.9, 0.9],
                "touches_count": [5, 5],
                "valid_from_utc": [ohlcv["open_time_utc"].iloc[20].isoformat(), ohlcv["open_time_utc"].iloc[20].isoformat()],
                "valid_to_utc": [ohlcv["open_time_utc"].iloc[110].isoformat(), ohlcv["open_time_utc"].iloc[110].isoformat()],
                "run_id": ["r1", "r1"],
            }
        )
        signals, _fallback = _build_signals(
            ohlcv,
            symbol="SOLUSDT",
            timeframe="1m",
            run_id="r1",
            levels_df=levels,
            patterns_df=pd.DataFrame(),
            ta_cfg={"signal": {"adx_min": 0.0, "mfi_long_min": 0.0, "mfi_short_max": 100.0, "rr_min": 0.0, "enable_structure_fallback": False}},
            min_tp_pct=0.01,
            min_expected_move_pct=0.002,
        )
        actionable = signals[signals["decision"].isin(["BUY", "SELL"])]
        if not actionable.empty:
            row = actionable.iloc[0]
            signal_idx = int(ohlcv.index[ohlcv["open_time_utc"].dt.strftime("%Y-%m-%dT%H:%M:%S%z") == pd.Timestamp(row["signal_time_utc"]).strftime("%Y-%m-%dT%H:%M:%S%z")][0])
            self.assertAlmostEqual(float(row["entry_price"]), float(ohlcv.iloc[signal_idx + 1]["open"]))

    def test_signal_config_accepts_min_tp_reach_prob(self) -> None:
        ohlcv = _make_ohlcv(120)
        levels = pd.DataFrame(
            {
                "level_id": ["l1", "l2"],
                "symbol": ["SOLUSDT", "SOLUSDT"],
                "timeframe": ["1m", "1m"],
                "detected_at_utc": [ohlcv["open_time_utc"].iloc[20].isoformat(), ohlcv["open_time_utc"].iloc[20].isoformat()],
                "level_price": [float(ohlcv["close"].iloc[20] * 0.97), float(ohlcv["close"].iloc[20] * 1.03)],
                "level_type": ["support", "resistance"],
                "strength_score": [0.0, 0.0],
                "touches_count": [1, 1],
                "valid_from_utc": [ohlcv["open_time_utc"].iloc[20].isoformat(), ohlcv["open_time_utc"].iloc[20].isoformat()],
                "valid_to_utc": [ohlcv["open_time_utc"].iloc[110].isoformat(), ohlcv["open_time_utc"].iloc[110].isoformat()],
                "run_id": ["r1", "r1"],
            }
        )
        signals, _fallback = _build_signals(
            ohlcv,
            symbol="SOLUSDT",
            timeframe="1m",
            run_id="r1",
            levels_df=levels,
            patterns_df=pd.DataFrame(),
            ta_cfg={"signal": {"adx_min": 0.0, "mfi_long_min": 0.0, "mfi_short_max": 100.0, "rr_min": 0.0, "min_tp_reach_prob": 0.99, "enable_structure_fallback": False}},
            min_tp_pct=0.01,
            min_expected_move_pct=0.002,
        )
        self.assertIn("reason_code", signals.columns)
        self.assertGreater(len(signals), 0)

    def test_signal_contract_side_and_time_and_expected_move_format(self) -> None:
        ohlcv = _make_ohlcv(120)
        levels = pd.DataFrame(
            {
                "level_id": ["l1", "l2"],
                "symbol": ["SOLUSDT", "SOLUSDT"],
                "timeframe": ["1m", "1m"],
                "detected_at_utc": [ohlcv["open_time_utc"].iloc[20].isoformat(), ohlcv["open_time_utc"].iloc[20].isoformat()],
                "level_price": [float(ohlcv["close"].iloc[20] * 0.99), float(ohlcv["close"].iloc[20] * 1.01)],
                "level_type": ["support", "resistance"],
                "strength_score": [0.9, 0.9],
                "touches_count": [5, 5],
                "valid_from_utc": [ohlcv["open_time_utc"].iloc[20].isoformat(), ohlcv["open_time_utc"].iloc[20].isoformat()],
                "valid_to_utc": [ohlcv["open_time_utc"].iloc[110].isoformat(), ohlcv["open_time_utc"].iloc[110].isoformat()],
                "run_id": ["r1", "r1"],
            }
        )
        signals, _fallback = _build_signals(
            ohlcv,
            symbol="SOLUSDT",
            timeframe="1m",
            run_id="r1",
            levels_df=levels,
            patterns_df=pd.DataFrame(),
            ta_cfg={"signal": {"adx_min": 0.0, "mfi_long_min": 0.0, "mfi_short_max": 100.0, "rr_min": 0.0, "enable_structure_fallback": False}},
            min_tp_pct=0.01,
            min_expected_move_pct=0.002,
        )
        self.assertTrue(signals["side"].isin([-1, 0, 1]).all())
        self.assertTrue(signals["signal_time_utc"].astype(str).str.endswith("Z").all())
        self.assertGreaterEqual(float(pd.to_numeric(signals["expected_move_pct"], errors="coerce").min()), 0.0)
        self.assertTrue((signals["contract_version"] == SIGNAL_CONTRACT_VERSION).all())
        self.assertTrue((signals["calibration_mode"] == CALIBRATION_MODE_NONE).all())


if __name__ == "__main__":
    unittest.main()
