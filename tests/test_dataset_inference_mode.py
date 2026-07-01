from __future__ import annotations

import unittest
import math
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from mlbotnav.dataset import FEATURE_COLUMNS, build_feature_frame


class DatasetInferenceModeTests(unittest.TestCase):
    def test_build_feature_frame_without_targets(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        px = 100.0
        for i in range(400):
            px *= 1.0002
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": px * 0.999,
                    "high": px * 1.001,
                    "low": px * 0.998,
                    "close": px,
                    "volume": 100 + i,
                }
            )
        df = pd.DataFrame(rows)
        out = build_feature_frame(df, horizon_bars=3, include_targets=False)
        self.assertFalse(out.empty)
        self.assertNotIn("future_return", out.columns)
        self.assertNotIn("target_up", out.columns)
        for c in FEATURE_COLUMNS:
            self.assertIn(c, out.columns)

    def test_volume_flow_uses_calibrated_return_lookback(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        close = 100.0
        for i in range(80):
            close += 0.25
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.05,
                    "high": close + 0.15,
                    "low": close - 0.15,
                    "close": close,
                    "volume": 1000.0 + (i * 10.0),
                }
            )
        raw = pd.DataFrame(rows)
        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"return_lookback": 3},
        )

        expected_obv = (np.sign(raw["close"].diff(1)).fillna(0.0) * raw["volume"]).cumsum()
        self.assertAlmostEqual(float(out.loc[10, "vol_chg"]), float(raw["volume"].pct_change(3).loc[10]))
        self.assertAlmostEqual(float(out.loc[10, "delta_volume"]), float(raw["volume"].diff(3).loc[10]))
        self.assertAlmostEqual(float(out.loc[10, "obv_slope_5"]), float(expected_obv.pct_change(3).loc[10]))

    def test_f001_ret1_allow_uses_passport_move_and_threshold(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        closes = [100.0, 100.02, 100.10, 100.00, 99.90]
        rows = []
        for i, close in enumerate(closes):
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close,
                    "high": close * 1.001,
                    "low": close * 0.999,
                    "close": close,
                    "volume": 1000.0 + i,
                }
            )
        raw = pd.DataFrame(rows)

        up = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F001_move": 1, "F001_thr_pct": 0.05},
        )
        down = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F001_move": -1, "F001_thr_pct": 0.05},
        )

        self.assertEqual(int(up.loc[2, "F001_RET1_ALLOW"]), 1)
        self.assertEqual(int(up.loc[3, "F001_RET1_ALLOW"]), 0)
        self.assertEqual(int(down.loc[3, "F001_RET1_ALLOW"]), 1)
        self.assertEqual(int(down.loc[2, "F001_RET1_ALLOW"]), 0)

    def test_ret_n_passport_actions_are_enabled_by_their_own_params(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        closes = [
            100.00,
            100.01,
            100.02,
            100.80,
            100.82,
            100.84,
            99.60,
            99.58,
            99.56,
            99.54,
            99.52,
            99.50,
            101.00,
            101.02,
            101.04,
            101.06,
            101.08,
            101.10,
            101.12,
            101.14,
            101.16,
            101.18,
            101.20,
            101.22,
            98.00,
        ]
        rows = []
        for i, close in enumerate(closes):
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close,
                    "high": close * 1.001,
                    "low": close * 0.999,
                    "close": close,
                    "volume": 1000.0 + i,
                }
            )
        raw = pd.DataFrame(rows)

        f002 = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F002_move": 1, "F002_thr_pct": 0.50},
        )
        self.assertIn("F002_RET3_ALLOW", f002.columns)
        self.assertNotIn("F003_RET6_ALLOW", f002.columns)
        self.assertEqual(int(f002.loc[3, "F002_RET3_ALLOW"]), 1)

        f003 = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F003_move": -1, "F003_thr_pct": 0.30},
        )
        self.assertEqual(int(f003.loc[6, "F003_RET6_ALLOW"]), 1)

        f004 = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F004_move": 1, "F004_thr_pct": 1.00},
        )
        self.assertEqual(int(f004.loc[12, "F004_RET12_ALLOW"]), 1)

        f005 = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F005_move": -1, "F005_thr_pct": 1.50},
        )
        self.assertEqual(int(f005.loc[24, "F005_RET24_ALLOW"]), 1)

    def test_b001_family_move_controls_all_ret_n_passports(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        closes = [100.0 + (i * 0.10) for i in range(30)]
        rows = []
        for i, close in enumerate(closes):
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close,
                    "high": close * 1.001,
                    "low": close * 0.999,
                    "close": close,
                    "volume": 1000.0 + i,
                }
            )
        raw = pd.DataFrame(rows)

        params = {
            "B001_family_move": 1,
            "F001_thr_pct": 0.01,
            "F002_thr_pct": 0.01,
            "F003_thr_pct": 0.01,
            "F004_thr_pct": 0.01,
            "F005_thr_pct": 0.01,
        }
        up = build_feature_frame(raw, horizon_bars=1, include_dropna=False, calibration_params=params)
        self.assertEqual(int(up.loc[24, "F001_RET1_ALLOW"]), 1)
        self.assertEqual(int(up.loc[24, "F002_RET3_ALLOW"]), 1)
        self.assertEqual(int(up.loc[24, "F003_RET6_ALLOW"]), 1)
        self.assertEqual(int(up.loc[24, "F004_RET12_ALLOW"]), 1)
        self.assertEqual(int(up.loc[24, "F005_RET24_ALLOW"]), 1)

        down_params = dict(params)
        down_params["B001_family_move"] = -1
        down = build_feature_frame(raw, horizon_bars=1, include_dropna=False, calibration_params=down_params)
        self.assertEqual(int(down.loc[24, "F001_RET1_ALLOW"]), 0)
        self.assertEqual(int(down.loc[24, "F005_RET24_ALLOW"]), 0)

    def test_f006_hl_spread_allow_uses_cmp_and_threshold(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        specs = [
            (100.0, 100.10, 99.95),
            (100.0, 100.70, 99.90),
            (100.0, 100.15, 99.95),
        ]
        for i, (open_, high, low) in enumerate(specs):
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": open_,
                    "high": high,
                    "low": low,
                    "close": open_,
                    "volume": 1000.0 + i,
                }
            )
        raw = pd.DataFrame(rows)

        greater = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F006_cmp": 1, "F006_thr_pct": 0.50},
        )
        less = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F006_cmp": -1, "F006_thr_pct": 0.30},
        )

        self.assertIn("F006_HLSPREAD_ALLOW", greater.columns)
        self.assertEqual(int(greater.loc[1, "F006_HLSPREAD_ALLOW"]), 1)
        self.assertEqual(int(greater.loc[0, "F006_HLSPREAD_ALLOW"]), 0)
        self.assertEqual(int(less.loc[0, "F006_HLSPREAD_ALLOW"]), 1)
        self.assertEqual(int(less.loc[1, "F006_HLSPREAD_ALLOW"]), 0)

    def test_f007_rolling_std20_allow_uses_cmp_and_threshold(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        closes = []
        px = 100.0
        for i in range(60):
            px *= 1.006 if i % 2 == 0 else 0.994
            closes.append(px)
        rows = []
        for i, close in enumerate(closes):
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close,
                    "high": close * 1.001,
                    "low": close * 0.999,
                    "close": close,
                    "volume": 1000.0 + i,
                }
            )
        raw = pd.DataFrame(rows)

        greater = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F007_cmp": 1, "F007_thr_pct": 0.30},
        )
        less = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F007_cmp": -1, "F007_thr_pct": 0.01},
        )

        self.assertIn("F007_RSTD20_ALLOW", greater.columns)
        self.assertEqual(int(greater.loc[25, "F007_RSTD20_ALLOW"]), 1)
        self.assertEqual(int(less.loc[25, "F007_RSTD20_ALLOW"]), 0)

    def test_f008_atr14_allow_uses_wilder_cmp_and_threshold(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        close = 100.0
        for i in range(40):
            high = close + (1.0 if i < 20 else 3.0)
            low = close - (1.0 if i < 20 else 3.0)
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close,
                    "high": high,
                    "low": low,
                    "close": close,
                    "volume": 1000.0 + i,
                }
            )
            close += 0.05
        raw = pd.DataFrame(rows)

        greater = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F008_cmp": 1, "F008_thr_pct": 1.0},
        )
        less = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F008_cmp": -1, "F008_thr_pct": 1.0},
        )

        self.assertIn("F008_ATR14_ALLOW", greater.columns)
        self.assertEqual(int(greater.loc[25, "F008_ATR14_ALLOW"]), 1)
        self.assertEqual(int(less.loc[25, "F008_ATR14_ALLOW"]), 0)

    def test_f009_f011_ema_passport_actions_use_fixed_ema_rules(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        close = 100.0
        for i in range(260):
            close *= 1.0015
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close * 0.999,
                    "high": close * 1.002,
                    "low": close * 0.998,
                    "close": close,
                    "volume": 1000.0 + i,
                }
            )
        raw = pd.DataFrame(rows)

        f009_above = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F009_bias": 1, "F009_thr_pct": 0.30},
        )
        f009_below = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F009_bias": -1, "F009_thr_pct": 0.30},
        )
        self.assertIn("F009_EMAGAP_ALLOW", f009_above.columns)
        self.assertEqual(int(f009_above.loc[120, "F009_EMAGAP_ALLOW"]), 1)
        self.assertEqual(int(f009_below.loc[120, "F009_EMAGAP_ALLOW"]), 0)

        f010_up = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F010_slope": 1, "F010_thr_pct": 0.05},
        )
        f010_down = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F010_slope": -1, "F010_thr_pct": 0.05},
        )
        self.assertIn("F010_EMASLOPE5_ALLOW", f010_up.columns)
        self.assertEqual(int(f010_up.loc[120, "F010_EMASLOPE5_ALLOW"]), 1)
        self.assertEqual(int(f010_down.loc[120, "F010_EMASLOPE5_ALLOW"]), 0)

        f011_above = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F011_position": 1, "F011_thr_pct": 1.00},
        )
        f011_below = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F011_position": -1, "F011_thr_pct": 1.00},
        )
        self.assertIn("F011_EMA200GAP_ALLOW", f011_above.columns)
        self.assertEqual(int(f011_above.loc[240, "F011_EMA200GAP_ALLOW"]), 1)
        self.assertEqual(int(f011_below.loc[240, "F011_EMA200GAP_ALLOW"]), 0)

    def test_f012_rsi14_combined_passport_action_uses_fixed_rsi_modes(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        closes = [100.0 + i * 0.1 for i in range(30)] + [103.0 - i * 0.25 for i in range(30)]
        rows = []
        for i, close in enumerate(closes):
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close,
                    "high": close * 1.001,
                    "low": close * 0.999,
                    "close": close,
                    "volume": 1000.0 + i,
                }
            )
        raw = pd.DataFrame(rows)

        level_greater = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F012_signal_mode": 1, "F012_cmp": 1, "F012_level": 70},
        )
        level_less = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F012_signal_mode": 1, "F012_cmp": -1, "F012_level": 30},
        )
        self.assertIn("F012_RSI14_ALLOW", level_greater.columns)
        self.assertEqual(int(level_greater.loc[20, "F012_RSI14_ALLOW"]), 1)
        self.assertEqual(int(level_less.loc[55, "F012_RSI14_ALLOW"]), 1)

        ma_above = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F012_signal_mode": 2, "F012_relation": 1, "F012_gap": 1},
        )
        ma_below = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F012_signal_mode": 2, "F012_relation": -1, "F012_gap": 1},
        )
        self.assertEqual(int(ma_above.loc[30, "F012_RSI14_ALLOW"]), 0)
        self.assertEqual(int(ma_below.loc[45, "F012_RSI14_ALLOW"]), 1)

    def test_f013_f015_macd_passport_actions_use_fixed_macd_rules(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        close = 100.0
        for i in range(120):
            close *= 1.002 if i < 70 else 0.998
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close * 0.999,
                    "high": close * 1.001,
                    "low": close * 0.998,
                    "close": close,
                    "volume": 1000.0 + i,
                }
            )
        raw = pd.DataFrame(rows)

        f013_pos = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F013_state": 1, "F013_thr_pct": 0.05, "macd_fast_period": 5},
        )
        f013_neg = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F013_state": -1, "F013_thr_pct": 0.05, "macd_fast_period": 5},
        )
        self.assertIn("F013_MACDLINE_ALLOW", f013_pos.columns)
        self.assertEqual(int(f013_pos.loc[50, "F013_MACDLINE_ALLOW"]), 1)
        self.assertEqual(int(f013_neg.loc[50, "F013_MACDLINE_ALLOW"]), 0)

        f014_pos = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F014_state": 1, "F014_thr_pct": 0.03},
        )
        f014_neg = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F014_state": -1, "F014_thr_pct": 0.03},
        )
        self.assertIn("F014_MACDSIGNAL_ALLOW", f014_pos.columns)
        self.assertEqual(int(f014_pos.loc[50, "F014_MACDSIGNAL_ALLOW"]), 1)
        self.assertEqual(int(f014_neg.loc[50, "F014_MACDSIGNAL_ALLOW"]), 0)

        f015_pos = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F015_state": 1, "F015_thr_pct": 0.005},
        )
        f015_neg = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F015_state": -1, "F015_thr_pct": 0.005},
        )
        self.assertIn("F015_MACDHIST_ALLOW", f015_pos.columns)
        self.assertEqual(int(f015_pos.loc[40, "F015_MACDHIST_ALLOW"]), 1)
        self.assertEqual(int(f015_neg.loc[90, "F015_MACDHIST_ALLOW"]), 1)

    def test_f016_adx14_allow_uses_passport_cmp_and_level(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        close = 100.0
        for i in range(120):
            close += 0.35
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.15,
                    "high": close + 0.30,
                    "low": close - 0.10,
                    "close": close,
                    "volume": 1000.0 + i,
                }
            )
        raw = pd.DataFrame(rows)

        greater = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F016_cmp": 1, "F016_level": 20},
        )
        less = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F016_cmp": -1, "F016_level": 20},
        )

        self.assertIn("F016_ADX14_ALLOW", greater.columns)
        self.assertEqual(int(greater.loc[60, "F016_ADX14_ALLOW"]), 1)
        self.assertEqual(int(less.loc[60, "F016_ADX14_ALLOW"]), 0)

    def test_f017_f018_stoch14_allow_uses_level_and_cross_modes(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        close = 100.0
        for i in range(120):
            close += 0.25 if i < 70 else -0.30
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.10,
                    "high": close + 0.20,
                    "low": close - 1.00,
                    "close": close,
                    "volume": 1000.0 + i,
                }
            )
        raw = pd.DataFrame(rows)

        level_greater = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={
                "F017_F018_signal_mode": 1,
                "F017_F018_line": 1,
                "F017_F018_cmp": 1,
                "F017_F018_level": 70,
            },
        )
        level_less = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={
                "F017_F018_signal_mode": 1,
                "F017_F018_line": 1,
                "F017_F018_cmp": -1,
                "F017_F018_level": 30,
            },
        )
        cross = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={
                "F017_F018_signal_mode": 2,
                "F017_F018_cross_dir": -1,
                "F017_F018_zone_filter": 0,
                "F017_F018_low_level": 20,
                "F017_F018_high_level": 80,
                "F017_F018_gap": 0,
            },
        )

        self.assertIn("F017_F018_STOCH14_ALLOW", level_greater.columns)
        self.assertEqual(int(level_greater.loc[40, "F017_F018_STOCH14_ALLOW"]), 1)
        self.assertEqual(int(level_less.loc[40, "F017_F018_STOCH14_ALLOW"]), 0)
        self.assertIn("F017_F018_STOCH14_ALLOW", cross.columns)
        self.assertTrue(set(cross["F017_F018_STOCH14_ALLOW"].dropna().unique()).issubset({0, 1}))

    def test_volume_f019_f021_allow_columns_use_passport_params(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        close = 100.0
        volume = 1000.0
        for i in range(80):
            close += 0.5 if i % 2 == 0 else -0.2
            volume *= 1.10 if i % 4 == 0 else 0.95
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - (0.20 if i % 3 == 0 else -0.10),
                    "high": close + 0.50,
                    "low": close - 0.50,
                    "close": close,
                    "volume": volume,
                }
            )
        raw = pd.DataFrame(rows)

        f019_up = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F019_direction": 1, "F019_thr_pct": 5},
        )
        f020_high = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F020_state": 1, "F020_z_level": 0.0},
        )
        f021_buy = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F021_delta_mode": 2, "F021_pressure": 1, "F021_delta_thr": 5},
        )
        f021_true_missing = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F021_delta_mode": 1, "F021_pressure": 1, "F021_delta_thr": 5},
        )

        self.assertIn("F019_VOLCHG_ALLOW", f019_up.columns)
        self.assertEqual(int(f019_up.loc[4, "F019_VOLCHG_ALLOW"]), 1)
        self.assertEqual(int(f019_up.loc[5, "F019_VOLCHG_ALLOW"]), 0)
        self.assertIn("F020_VOLZ20_ALLOW", f020_high.columns)
        self.assertTrue(set(f020_high["F020_VOLZ20_ALLOW"].dropna().unique()).issubset({0, 1}))
        self.assertIn("F021_DELTAVOL_ALLOW", f021_buy.columns)
        self.assertEqual(int(f021_buy.loc[6, "F021_DELTAVOL_ALLOW"]), 1)
        self.assertEqual(int(f021_true_missing["F021_DELTAVOL_ALLOW"].sum()), 0)

    def test_f022_obv_slope5_allow_uses_fixed_volume_normalized_slope(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(80):
            close = 100.0 + float(i)
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.1,
                    "high": close + 0.2,
                    "low": close - 0.2,
                    "close": close,
                    "volume": 1000.0,
                }
            )
        raw = pd.DataFrame(rows)

        up = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F022_slope_dir": 1, "F022_slope_thr": 4.0},
        )
        down = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F022_slope_dir": -1, "F022_slope_thr": 4.0},
        )

        self.assertIn("F022_OBVSLOPE5_ALLOW", up.columns)
        self.assertEqual(int(up.loc[30, "F022_OBVSLOPE5_ALLOW"]), 1)
        self.assertEqual(int(down.loc[30, "F022_OBVSLOPE5_ALLOW"]), 0)

    def test_f023_mfi14_allow_supports_level_and_cross_level_modes(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        close = 100.0
        for i in range(90):
            close += -0.5 if i < 35 else 0.7
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.1,
                    "high": close + 0.2,
                    "low": close - 0.2,
                    "close": close,
                    "volume": 1000.0,
                }
            )
        raw = pd.DataFrame(rows)

        level_greater = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F023_signal_mode": 1, "F023_cmp": 1, "F023_level": 90},
        )
        level_less = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F023_signal_mode": 1, "F023_cmp": -1, "F023_level": 10},
        )
        cross_up = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F023_signal_mode": 2, "F023_cross_dir": 1, "F023_cross_level": 50},
        )

        self.assertIn("F023_MFI14_ALLOW", level_greater.columns)
        self.assertEqual(int(level_greater.loc[60, "F023_MFI14_ALLOW"]), 1)
        self.assertEqual(int(level_less.loc[60, "F023_MFI14_ALLOW"]), 0)
        self.assertGreater(int(cross_up["F023_MFI14_ALLOW"].sum()), 0)

    def test_density_vpoc_drift_uses_div_lookback(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        close = 100.0
        for i in range(160):
            close += 0.1 + (0.02 if i % 3 == 0 else -0.01)
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.05,
                    "high": close + 0.2,
                    "low": close - 0.2,
                    "close": close,
                    "volume": 1000.0 + ((i % 11) * 17.0),
                }
            )
        raw = pd.DataFrame(rows)
        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"return_lookback": 3, "div_lookback": 7, "density_window_short": 20},
        )

        expected = out["density_vpoc_distance_60"].diff(7)
        valid = expected.dropna().index[-1]
        self.assertAlmostEqual(float(out.loc[valid, "density_vpoc_drift_20"]), float(expected.loc[valid]))

    def test_density_vpoc_core_action_columns_use_passport_params(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(320):
            close = 100.0 + i * 0.01
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.02,
                    "high": close + 0.05,
                    "low": close - 0.05,
                    "close": close,
                    "volume": 1000.0 + (i % 7) * 10.0,
                }
            )
        raw = pd.DataFrame(rows)

        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={
                "F025_signal_mode": 2,
                "F025_distance_state": 1,
                "F025_dist_thr_pct": 0.0,
                "F029_signal_mode": 2,
                "F029_distance_state": 1,
                "F029_dist_thr_pct": 0.0,
                "F033_drift_dir": 1,
                "F033_drift_thr_pct": 0.0,
                "F034_cmp": 1,
                "F034_ratio_level": 2.5,
            },
        )

        ix = out["density_vpoc_distance_240"].dropna().index[-1]
        for col in [
            "F025_VPOCDIST60_ALLOW",
            "F029_VPOCDIST240_ALLOW",
            "F033_VPOCDRIFT20_ALLOW",
            "F034_CLUSTERRATIO_ALLOW",
        ]:
            self.assertIn(col, out.columns)
            self.assertIn(int(out.loc[ix, col]), {0, 1})
        self.assertEqual(int(out.loc[ix, "F025_VPOCDIST60_ALLOW"]), 1)
        self.assertEqual(int(out.loc[ix, "F029_VPOCDIST240_ALLOW"]), 1)
        self.assertEqual(int(out.loc[ix, "F033_VPOCDRIFT20_ALLOW"]), 1)
        self.assertEqual(int(out.loc[ix, "F034_CLUSTERRATIO_ALLOW"]), 1)

    def test_density_bin_share60_action_column_uses_passport_params(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(120):
            close = 100.0 + (i % 12) * 0.01
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.01,
                    "high": close + 0.03,
                    "low": close - 0.03,
                    "close": close,
                    "volume": 1000.0 + (i % 3) * 50.0,
                }
            )
        raw = pd.DataFrame(rows)

        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"density_window_short": 20, "F026_cmp": 1, "F026_share_thr_pct": 1},
        )

        ix = out["density_bin_share_60"].shift(1).dropna().index[-1]
        self.assertIn("F026_BINSHARE60_ALLOW", out.columns)
        self.assertIn(int(out.loc[ix, "F026_BINSHARE60_ALLOW"]), {0, 1})

    def test_density_cluster_share60_action_column_uses_passport_params(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(120):
            close = 100.0 + (i % 12) * 0.01
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.01,
                    "high": close + 0.03,
                    "low": close - 0.03,
                    "close": close,
                    "volume": 1000.0 + (i % 3) * 50.0,
                }
            )
        raw = pd.DataFrame(rows)

        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"density_window_short": 20, "F027_cmp": 1, "F027_share_thr_pct": 2},
        )

        ix = out["density_cluster_share_60"].shift(1).dropna().index[-1]
        self.assertIn("F027_CLUSTERSHARE60_ALLOW", out.columns)
        self.assertIn(int(out.loc[ix, "F027_CLUSTERSHARE60_ALLOW"]), {0, 1})

    def test_density_vpoc_share60_action_column_uses_passport_params(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(120):
            close = 100.0 + (i % 12) * 0.01
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.01,
                    "high": close + 0.03,
                    "low": close - 0.03,
                    "close": close,
                    "volume": 1000.0 + (i % 3) * 50.0,
                }
            )
        raw = pd.DataFrame(rows)

        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"density_window_short": 20, "F028_cmp": 1, "F028_share_thr_pct": 1},
        )

        ix = out["density_vpoc_share_60"].shift(1).dropna().index[-1]
        self.assertIn("F028_VPOCSHARE60_ALLOW", out.columns)
        self.assertIn(int(out.loc[ix, "F028_VPOCSHARE60_ALLOW"]), {0, 1})

    def test_density_bin_share240_action_column_uses_passport_params(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(320):
            close = 100.0 + (i % 20) * 0.01
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.01,
                    "high": close + 0.03,
                    "low": close - 0.03,
                    "close": close,
                    "volume": 1000.0 + (i % 5) * 50.0,
                }
            )
        raw = pd.DataFrame(rows)

        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F030_cmp": 1, "F030_share_thr_pct": 0.5},
        )

        ix = out["density_bin_share_240"].shift(1).dropna().index[-1]
        self.assertIn("F030_BINSHARE240_ALLOW", out.columns)
        self.assertIn(int(out.loc[ix, "F030_BINSHARE240_ALLOW"]), {0, 1})

    def test_density_cluster_share240_action_column_uses_passport_params(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(320):
            close = 100.0 + (i % 20) * 0.01
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.01,
                    "high": close + 0.03,
                    "low": close - 0.03,
                    "close": close,
                    "volume": 1000.0 + (i % 5) * 50.0,
                }
            )
        raw = pd.DataFrame(rows)

        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F031_cmp": 1, "F031_share_thr_pct": 1},
        )

        ix = out["density_cluster_share_240"].shift(1).dropna().index[-1]
        self.assertIn("F031_CLUSTERSHARE240_ALLOW", out.columns)
        self.assertIn(int(out.loc[ix, "F031_CLUSTERSHARE240_ALLOW"]), {0, 1})

    def test_density_vpoc_share240_action_column_uses_passport_params(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(320):
            close = 100.0 + (i % 20) * 0.01
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.01,
                    "high": close + 0.03,
                    "low": close - 0.03,
                    "close": close,
                    "volume": 1000.0 + (i % 5) * 50.0,
                }
            )
        raw = pd.DataFrame(rows)

        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F032_cmp": 1, "F032_share_thr_pct": 0.5},
        )

        ix = out["density_vpoc_share_240"].shift(1).dropna().index[-1]
        self.assertIn("F032_VPOCSHARE240_ALLOW", out.columns)
        self.assertIn(int(out.loc[ix, "F032_VPOCSHARE240_ALLOW"]), {0, 1})

    def test_vwap_distance_action_column_uses_passport_params(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(80):
            close = 100.0 + (i % 20) * 0.05
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.02,
                    "high": close + 0.04,
                    "low": close - 0.04,
                    "close": close,
                    "volume": 1000.0 + (i % 4) * 25.0,
                }
            )
        raw = pd.DataFrame(rows)

        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={
                "F024_signal_mode": 2,
                "F024_distance_state": 1,
                "F024_dist_thr_pct": 0.0,
            },
        )

        valid_ix = out["vwap_distance"].shift(1).dropna().index[-1]
        self.assertIn("F024_VWAPDIST_ALLOW", out.columns)
        self.assertEqual(int(out.loc[valid_ix, "F024_VWAPDIST_ALLOW"]), 1)

    def test_level_range_channel_block_a_actions_use_passport_params(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(320):
            close = 100.0 + i * 0.01
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.01,
                    "high": close + 0.03,
                    "low": close - 0.03,
                    "close": close,
                    "volume": 1000.0 + (i % 5) * 20.0,
                }
            )
        raw = pd.DataFrame(rows)

        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={
                "F035_distance_state": -1,
                "F035_dist_thr_pct": 3.0,
                "F036_distance_state": -1,
                "F036_dist_thr_pct": 3.0,
                "F037_level_type": 1,
                "F037_strength_state": -1,
                "F037_strength_thr": 10.0,
            },
        )

        ix = out["support_distance"].dropna().index[-1]
        for col in ["F035_SUPPORTDIST_ALLOW", "F036_RESDIST_ALLOW", "F037_LEVELSTRENGTH_ALLOW"]:
            self.assertIn(col, out.columns)
            self.assertIn(int(out.loc[ix, col]), {0, 1})
        self.assertEqual(int(out.loc[ix, "F035_SUPPORTDIST_ALLOW"]), 1)
        self.assertEqual(int(out.loc[ix, "F036_RESDIST_ALLOW"]), 1)
        self.assertEqual(int(out.loc[ix, "F037_LEVELSTRENGTH_ALLOW"]), 1)

    def test_position_in_range_action_column_uses_passport_params(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(320):
            close = 100.0 + (i % 50) * 0.03
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.02,
                    "high": close + 0.10,
                    "low": close - 0.10,
                    "close": close,
                    "volume": 1000.0 + (i % 7) * 20.0,
                }
            )
        raw = pd.DataFrame(rows)

        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F038_zone": -1, "F038_level": 95},
        )

        closed_high = out["high"].shift(1).rolling(240, min_periods=240).max()
        ix = closed_high.dropna().index[-1]
        self.assertIn("F038_RANGEPOSE_ALLOW", out.columns)
        self.assertIn(int(out.loc[ix, "F038_RANGEPOSE_ALLOW"]), {0, 1})

    def test_trend_channel_pos_action_column_uses_passport_params(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(260):
            close = 100.0 + i * 0.02 + math.sin(i / 9.0) * 0.30
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.02,
                    "high": close + 0.10,
                    "low": close - 0.10,
                    "close": close,
                    "volume": 1000.0 + (i % 7) * 20.0,
                }
            )
        raw = pd.DataFrame(rows)

        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"F039_zone": 1, "F039_level": 100, "F039_outside_thr": 0},
        )

        ix = out["close"].shift(1).rolling(120, min_periods=120).count().dropna().index[-1]
        self.assertIn("F039_CHANNELPOS_ALLOW", out.columns)
        self.assertIn(int(out.loc[ix, "F039_CHANNELPOS_ALLOW"]), {0, 1})

    def test_fibonacci_anchor_grid_actions_use_confirmed_pivots(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(360):
            close = 100.0 + 5.0 * math.sin(i / 18.0) + i * 0.005
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.05,
                    "high": close + 0.20,
                    "low": close - 0.20,
                    "close": close,
                    "volume": 1000.0 + (i % 9),
                }
            )
        raw = pd.DataFrame(rows)

        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={
                "F040_signal_mode": 2,
                "F040_distance_state": 1,
                "F040_dist_thr_pct": 0.0,
                "F041_signal_mode": 2,
                "F041_distance_state": 1,
                "F041_dist_thr_pct": 0.0,
            },
        )

        for col in ["fib_0382", "fib_0618", "fib_direction", "F040_FIB0382DIST_ALLOW", "F041_FIB0618DIST_ALLOW"]:
            self.assertIn(col, out.columns)
        self.assertGreater(int(out["F040_FIB0382DIST_ALLOW"].sum()), 0)
        self.assertGreater(int(out["F041_FIB0618DIST_ALLOW"].sum()), 0)
        ix = out["fib_0382"].dropna().index[-1]
        self.assertEqual(int(out.loc[ix, "F040_FIB0382DIST_ALLOW"]), 1)
        self.assertEqual(int(out.loc[ix, "F041_FIB0618DIST_ALLOW"]), 1)

    def test_entry_quality_context_actions_emit_side_aware_gates(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(320):
            close = 100.0 + 2.0 * math.sin(i / 12.0)
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.05,
                    "high": close + 1.50,
                    "low": close - 1.50,
                    "close": close,
                    "volume": 1000.0 + (i % 7),
                }
            )
        raw = pd.DataFrame(rows)

        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={
                "F042_level_source_mode": 1,
                "F042_cmp": 1,
                "F042_tp_dist_thr_pct": 0.05,
                "F043_level_source_mode": 1,
                "F043_cmp": 1,
                "F043_sl_dist_thr_pct": 0.05,
                "F044_level_source_mode": 1,
                "F044_rr_state": 1,
                "F044_rr_level": 0.50,
            },
        )

        for col in (
            "F042_TPCONTEXT_ALLOW",
            "F042_TPCONTEXT_ALLOW_LONG",
            "F042_TPCONTEXT_ALLOW_SHORT",
            "F043_SLCONTEXT_ALLOW",
            "F043_SLCONTEXT_ALLOW_LONG",
            "F043_SLCONTEXT_ALLOW_SHORT",
            "F044_RRCONTEXT_ALLOW",
            "F044_RRCONTEXT_ALLOW_LONG",
            "F044_RRCONTEXT_ALLOW_SHORT",
        ):
            self.assertIn(col, out.columns)
            self.assertGreaterEqual(int(out[col].sum()), 0)
        self.assertGreater(int(out["F042_TPCONTEXT_ALLOW_LONG"].sum()), 0)
        self.assertGreater(int(out["F043_SLCONTEXT_ALLOW_SHORT"].sum()), 0)
        self.assertGreater(int(out["F044_RRCONTEXT_ALLOW"].sum()), 0)

    def test_breakout_retest_passport_actions_emit_runtime_gates(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(360):
            close = 100.0 + math.sin(i / 7.0) * 2.0 + math.sin(i / 17.0) * 0.7
            if i >= 260:
                close += (i - 260) * 0.035
            if 310 <= i < 320:
                close -= (i - 310) * 0.12
            if i >= 320:
                close -= 1.2
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.05,
                    "high": close + 0.35 + 0.03 * (i % 3),
                    "low": close - 0.35 - 0.02 * (i % 4),
                    "close": close,
                    "volume": 1000.0 + i,
                }
            )
        raw = pd.DataFrame(rows)
        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={
                "F048_break_buffer_pct": 0.0,
                "F048_confirm_bars": 1,
                "F049_break_buffer_pct": 0.0,
                "F049_confirm_bars": 1,
                "F045_level_source_mode": 1,
                "F045_break_dir": 1,
                "F045_break_buffer_pct": 0.0,
                "F045_confirm_bars": 1,
                "F046_level_source_mode": 1,
                "F046_break_dir": 1,
                "F046_false_mode": 1,
                "F046_break_buffer_pct": 0.0,
                "F046_return_window_bars": 5,
                "F046_return_tolerance_pct": 0.30,
                "F047_level_source_mode": 1,
                "F047_break_dir": 1,
                "F047_retest_window_bars": 30,
                "F047_retest_tolerance_pct": 0.50,
                "F047_reaction_confirm_pct": 0.0,
            },
        )

        for col in (
            "F045_BREAKOUT_ALLOW",
            "F046_FALSEBREAK_ALLOW",
            "F047_RETEST_ALLOW",
            "F048_SWINGHIGHBREAK_ALLOW",
            "F049_SWINGLOWBREAK_ALLOW",
        ):
            self.assertIn(col, out.columns)
            self.assertGreater(int(out[col].sum()), 0)
            self.assertTrue(set(out[col].dropna().unique()).issubset({0, 1}))

    def test_market_structure_passport_actions_emit_runtime_gates(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(420):
            close = 100.0 + math.sin(i / 6.0) * 1.8 + math.sin(i / 19.0) * 0.6
            if i < 150:
                close += i * 0.035
            elif i < 280:
                close += 150 * 0.035 - (i - 150) * 0.045
            else:
                close += 150 * 0.035 - 130 * 0.045 + (i - 280) * 0.055
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.04,
                    "high": close + 0.35 + 0.02 * (i % 4),
                    "low": close - 0.35 - 0.02 * (i % 3),
                    "close": close,
                    "volume": 1000.0 + i,
                }
            )
        raw = pd.DataFrame(rows)
        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={
                "F050_structure_scope": 1,
                "F050_break_buffer_pct": 0.0,
                "F050_confirm_bars": 1,
                "F050_require_bias": 2,
                "F051_structure_scope": 1,
                "F051_break_buffer_pct": 0.0,
                "F051_confirm_bars": 1,
                "F051_require_bias": 2,
                "F052_structure_scope": 1,
                "F052_choch_dir": 1,
                "F052_break_buffer_pct": 0.0,
                "F052_confirm_bars": 1,
                "F052_require_opposite_bias": 0,
            },
        )

        for col in ("F050_BOSUP_ALLOW", "F051_BOSDOWN_ALLOW", "F052_CHOCH_ALLOW"):
            self.assertIn(col, out.columns)
            self.assertGreater(int(out[col].sum()), 0)
            self.assertTrue(set(out[col].dropna().unique()).issubset({0, 1}))

    def test_candle_pattern_passport_actions_emit_runtime_gates(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(80):
            close = 100.0 + math.sin(i / 8.0) * 0.15
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.03,
                    "high": close + 0.40,
                    "low": close - 0.40,
                    "close": close,
                    "volume": 1000.0 + i,
                }
            )
        raw = pd.DataFrame(rows)

        def candle(i: int, open_: float, high: float, low: float, close: float) -> None:
            raw.loc[i, ["open", "high", "low", "close"]] = [open_, high, low, close]

        candle(20, 100.00, 101.00, 99.00, 100.02)
        candle(24, 100.00, 102.00, 98.00, 101.00)
        candle(25, 100.00, 101.00, 99.00, 100.50)
        candle(26, 101.00, 101.40, 100.80, 101.00)
        candle(29, 99.10, 99.40, 98.90, 99.10)
        candle(30, 100.00, 100.40, 98.00, 100.20)
        candle(41, 99.00, 99.30, 98.80, 99.00)
        candle(44, 101.00, 101.30, 100.80, 101.00)
        candle(45, 100.00, 102.00, 99.60, 99.80)
        candle(52, 101.00, 101.20, 100.80, 101.00)
        candle(54, 101.00, 101.20, 99.80, 100.00)
        candle(55, 99.80, 101.50, 99.70, 101.30)
        candle(62, 99.80, 100.00, 99.60, 99.80)
        candle(64, 100.00, 101.20, 99.80, 101.00)
        candle(65, 101.20, 101.40, 99.50, 99.70)

        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={
                "F053_max_body_pct": 15,
                "F053_min_range_pct": 0.01,
                "F053_wick_mode": 1,
                "F053_wick_balance_max_pct": 80,
                "F054_containment_mode": 2,
                "F054_max_inside_range_ratio": 1.0,
                "F054_mother_min_range_pct": 0.02,
                "F055_wick_body_ratio": 1.5,
                "F055_wick_min_pct": 50,
                "F055_opposite_wick_max_pct": 30,
                "F055_body_zone_pct": 50,
                "F055_min_range_pct": 0.02,
                "F056_wick_body_ratio": 1.5,
                "F056_wick_min_pct": 50,
                "F056_opposite_wick_max_pct": 30,
                "F056_body_zone_pct": 50,
                "F056_min_range_pct": 0.02,
                "F057_wick_body_ratio": 1.5,
                "F057_lower_wick_min_pct": 50,
                "F057_upper_wick_max_pct": 25,
                "F057_body_zone_pct": 50,
                "F057_trend_lookback_bars": 3,
                "F057_trend_min_drop_pct": 0.05,
                "F058_wick_body_ratio": 1.5,
                "F058_upper_wick_min_pct": 50,
                "F058_lower_wick_max_pct": 25,
                "F058_body_zone_pct": 50,
                "F058_trend_lookback_bars": 3,
                "F058_trend_min_rise_pct": 0.05,
                "F059_engulf_mode": 1,
                "F059_min_engulf_ratio": 1.0,
                "F059_min_body_pct": 10,
                "F059_trend_lookback_bars": 2,
                "F059_trend_min_drop_pct": 0.0,
                "F060_engulf_mode": 1,
                "F060_min_engulf_ratio": 1.0,
                "F060_min_body_pct": 10,
                "F060_trend_lookback_bars": 2,
                "F060_trend_min_rise_pct": 0.0,
            },
        )

        for col in (
            "F053_DOJI_ALLOW",
            "F054_INSIDEBAR_ALLOW",
            "F055_PINBULL_ALLOW",
            "F056_PINBEAR_ALLOW",
            "F057_HAMMER_ALLOW",
            "F058_SHOOTINGSTAR_ALLOW",
            "F059_ENGULFBULL_ALLOW",
            "F060_ENGULFBEAR_ALLOW",
        ):
            self.assertIn(col, out.columns)
            self.assertGreater(int(out[col].sum()), 0)
            self.assertTrue(set(out[col].dropna().unique()).issubset({0, 1}))

    def test_divergence_pattern_passport_actions_emit_runtime_gates(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(720):
            close = 100.0 + math.sin(i / 9.0) * 2.5 + math.sin(i / 31.0) * 1.5 + (i / 720.0) * 1.5
            if 160 < i < 260:
                close -= (i - 160) * 0.015
            if 420 < i < 520:
                close += (i - 420) * 0.015
            open_ = close + math.sin(i / 4.0) * 0.1
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": open_,
                    "high": max(open_, close) + 0.25 + 0.03 * (i % 4),
                    "low": min(open_, close) - 0.25 - 0.03 * (i % 3),
                    "close": close,
                    "volume": max(10.0, 1000.0 + 200.0 * math.sin(i / 7.0) + 50.0 * (i % 5)),
                }
            )
        raw = pd.DataFrame(rows)
        calibration_params = {}
        for prefix in ("F061", "F062"):
            calibration_params.update(
                {
                    f"{prefix}_pivot_scope": 1,
                    f"{prefix}_div_type": 1,
                    f"{prefix}_price_delta_min_pct": 0.05,
                    f"{prefix}_rsi_delta_min": 1,
                    f"{prefix}_max_pivot_gap_bars": 120,
                    f"{prefix}_confirm_mode": 1,
                    f"{prefix}_reaction_confirm_pct": 0.0,
                }
            )
        for prefix in ("F063", "F064"):
            calibration_params.update(
                {
                    f"{prefix}_pivot_scope": 1,
                    f"{prefix}_div_type": 1,
                    f"{prefix}_macd_component": 2,
                    f"{prefix}_price_delta_min_pct": 0.05,
                    f"{prefix}_macd_delta_min_pct": 0.0,
                    f"{prefix}_max_pivot_gap_bars": 120,
                    f"{prefix}_confirm_mode": 1,
                    f"{prefix}_reaction_confirm_pct": 0.0,
                }
            )
        for prefix in ("F065", "F066"):
            calibration_params.update(
                {
                    f"{prefix}_pivot_scope": 1,
                    f"{prefix}_div_type": 1,
                    f"{prefix}_price_delta_min_pct": 0.05,
                    f"{prefix}_obv_delta_min_norm": 0.5,
                    f"{prefix}_max_pivot_gap_bars": 120,
                    f"{prefix}_confirm_mode": 1,
                    f"{prefix}_reaction_confirm_pct": 0.0,
                }
            )
        out = build_feature_frame(raw, horizon_bars=1, include_dropna=False, calibration_params=calibration_params)

        for col in (
            "F061_RSIBULLDIV_ALLOW",
            "F062_RSIBEARDIV_ALLOW",
            "F063_MACDBULLDIV_ALLOW",
            "F064_MACDBEARDIV_ALLOW",
            "F065_OBVBULLDIV_ALLOW",
            "F066_OBVBEARDIV_ALLOW",
        ):
            self.assertIn(col, out.columns)
            self.assertGreater(int(out[col].sum()), 0)
            self.assertTrue(set(out[col].dropna().unique()).issubset({0, 1}))

    def test_pattern_quality_passport_actions_emit_runtime_gates(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(80):
            close = 100.0 + math.sin(i / 5.0) * 0.2
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close,
                    "high": close + 0.5,
                    "low": close - 0.5,
                    "close": close,
                    "volume": 1000.0 + i,
                }
            )
        raw = pd.DataFrame(rows)
        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={
                "F067_strength_state": 1,
                "F067_strength_thr": 1.0,
                "F067_require_confirmation": 0,
                "F067_require_context": 0,
                "F068_age_mode": 1,
                "F068_min_age_bars": 0,
                "F068_max_age_bars": 5,
            },
        )

        for col in ("F067_PATTERNSTRENGTH_ALLOW", "F068_PATTERNAGE_ALLOW"):
            self.assertIn(col, out.columns)
            self.assertGreater(int(out[col].sum()), 0)
            self.assertTrue(set(out[col].dropna().unique()).issubset({0, 1}))

    def test_chart_pattern_passport_actions_emit_runtime_gates(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(500):
            close = 100.0 + math.sin(i / 8.0) * 2.0 + math.sin(i / 35.0) * 4.0 + (i % 80 - 40) * 0.02
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.05,
                    "high": close + 0.6 + 0.2 * math.sin(i / 5.0),
                    "low": close - 0.6 - 0.2 * math.cos(i / 6.0),
                    "close": close,
                    "volume": 1000.0 + (i % 17),
                }
            )
        raw = pd.DataFrame(rows)
        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={
                "F069_bottom_tolerance_pct": 1.0,
                "F069_min_separation_bars": 5,
                "F069_neckline_break_required": 0,
                "F069_break_buffer_pct": 0.0,
                "F069_max_pattern_age_bars": 240,
                "F070_top_tolerance_pct": 1.0,
                "F070_min_separation_bars": 5,
                "F070_neckline_break_required": 0,
                "F070_break_buffer_pct": 0.0,
                "F070_max_pattern_age_bars": 240,
                "F071_shoulder_tolerance_pct": 1.5,
                "F071_head_min_excess_pct": 0.1,
                "F071_neckline_break_required": 0,
                "F071_break_buffer_pct": 0.0,
                "F071_max_pattern_age_bars": 240,
                "F072_shoulder_tolerance_pct": 1.5,
                "F072_head_min_excess_pct": 0.1,
                "F072_neckline_break_required": 0,
                "F072_break_buffer_pct": 0.0,
                "F072_max_pattern_age_bars": 240,
                "F073_triangle_type": 1,
                "F073_min_touches": 2,
                "F073_convergence_min_pct": 5,
                "F073_breakout_required": 0,
                "F073_break_dir": 0,
                "F073_break_buffer_pct": 0.0,
                "F074_impulse_dir": 1,
                "F074_impulse_min_pct": 0.3,
                "F074_consolidation_bars": 10,
                "F074_compression_min_pct": 5,
                "F074_breakout_required": 0,
                "F074_break_buffer_pct": 0.0,
                "F075_min_touches": 2,
                "F075_convergence_min_pct": 5,
                "F075_breakout_required": 0,
                "F075_break_dir": 0,
                "F075_break_buffer_pct": 0.0,
                "F076_min_touches": 2,
                "F076_convergence_min_pct": 5,
                "F076_breakout_required": 0,
                "F076_break_dir": 0,
                "F076_break_buffer_pct": 0.0,
                "F077_range_lookback": 20,
                "F077_max_range_pct": 5.0,
                "F077_min_touches_high": 1,
                "F077_min_touches_low": 1,
                "F077_range_pos_mode": 1,
                "F077_range_pos_level": 10,
            },
        )

        for col in (
            "F069_DOUBLEBOTTOM_ALLOW",
            "F070_DOUBLETOP_ALLOW",
            "F071_HEADSHOULDERS_ALLOW",
            "F072_INVHEADSHOULDERS_ALLOW",
            "F073_TRIANGLE_ALLOW",
            "F074_PENNANT_ALLOW",
            "F075_WEDGERISING_ALLOW",
            "F076_WEDGEFALLING_ALLOW",
            "F077_RANGEFLAG_ALLOW",
        ):
            self.assertIn(col, out.columns)
            self.assertGreater(int(out[col].sum()), 0)
            self.assertTrue(set(out[col].dropna().unique()).issubset({0, 1}))

    def test_pattern_confirmation_passport_actions_emit_runtime_gates(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(120):
            close = 100.0 + math.sin(i / 7.0) * 0.4
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - (0.01 if i % 2 == 0 else -0.01),
                    "high": close + 0.15,
                    "low": close - 0.15,
                    "close": close,
                    "volume": 1000.0 + i * 5.0,
                }
            )
        raw = pd.DataFrame(rows)
        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={
                "F078_confirm_mode": 1,
                "F078_ratio_thr": 1.0,
                "F078_z_thr": 0.0,
                "F078_confirm_bar_mode": 1,
                "F078_direction_filter": 1,
                "F079_level_source_mode": 5,
                "F079_confirm_type": 1,
                "F079_dist_thr_pct": 2.0,
                "F079_reaction_confirm_pct": 0.0,
                "F079_direction_filter": 1,
            },
        )

        for col in ("F078_PATTERNVOLCONF_ALLOW", "F079_PATTERNLEVELCONF_ALLOW"):
            self.assertIn(col, out.columns)
            self.assertGreater(int(out[col].sum()), 0)
            self.assertTrue(set(out[col].dropna().unique()).issubset({0, 1}))

    def test_pattern_composite_entry_passport_actions_emit_runtime_gates(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(180):
            close = 100.0 + math.sin(i / 6.0) * 0.5
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - (0.01 if i % 2 == 0 else -0.01),
                    "high": close + 0.20,
                    "low": close - 0.20,
                    "close": close,
                    "volume": 1000.0 + i * 4.0,
                }
            )
        raw = pd.DataFrame(rows)
        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={
                "F080_pattern_family_filter": 1,
                "F080_direction_mode": 2,
                "F080_logic_mode": 1,
                "F080_use_strength": 0,
                "F080_use_age": 0,
                "F080_use_volume_confirm": 0,
                "F080_use_level_confirm": 0,
                "F080_structure_filter": 1,
                "F080_breakout_filter": 1,
                "F080_min_score": 2,
                "F080_block_opposite_pattern": 0,
                "F081_pattern_family_filter": 1,
                "F081_direction_mode": 2,
                "F081_logic_mode": 1,
                "F081_use_strength": 0,
                "F081_use_age": 0,
                "F081_use_volume_confirm": 0,
                "F081_use_level_confirm": 0,
                "F081_structure_filter": 1,
                "F081_breakout_filter": 1,
                "F081_min_score": 2,
                "F081_block_opposite_pattern": 0,
            },
        )

        for col in ("F080_PATTERNLONG_ALLOW", "F081_PATTERNSHORT_ALLOW"):
            self.assertIn(col, out.columns)
            self.assertGreater(int(out[col].sum()), 0)
            self.assertTrue(set(out[col].dropna().unique()).issubset({0, 1}))

    def test_pattern_trade_context_passport_actions_emit_runtime_gates(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(240):
            close = 100.0 + math.sin(i / 8.0) * 0.6 + (i % 30) * 0.01
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - (0.02 if i % 2 == 0 else -0.02),
                    "high": close + 0.25,
                    "low": close - 0.25,
                    "close": close,
                    "volume": 1000.0 + i * 3.0,
                }
            )
        raw = pd.DataFrame(rows)
        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={
                "F082_sl_anchor_mode": 1,
                "F082_buffer_mode": 1,
                "F082_buffer_pct": 0.0,
                "F082_atr_mult": 1.0,
                "F082_range_mult": 0.5,
                "F082_sl_distance_mode": 2,
                "F082_min_sl_dist_pct": 0.02,
                "F082_max_sl_dist_pct": 5.0,
                "F083_target_source_mode": 6,
                "F083_min_targets": 1,
                "F083_min_rr_to_target": 0.5,
                "F083_target_spacing_min_pct": 0.05,
                "F083_require_clear_path": 0,
                "F083_ladder_state": 1,
                "F083_ladder_score_thr": 1.0,
            },
        )

        for col in (
            "F082_PATTERNSLBUF_ALLOW",
            "F082_PATTERNSLBUF_ALLOW_LONG",
            "F082_PATTERNSLBUF_ALLOW_SHORT",
            "F083_PATTERNTPLADDER_ALLOW",
            "F083_PATTERNTPLADDER_ALLOW_LONG",
            "F083_PATTERNTPLADDER_ALLOW_SHORT",
        ):
            self.assertIn(col, out.columns)
            self.assertTrue(set(out[col].dropna().unique()).issubset({0, 1}))
        self.assertGreater(int(out["F082_PATTERNSLBUF_ALLOW"].sum()), 0)
        self.assertGreater(int(out["F083_PATTERNTPLADDER_ALLOW"].sum()), 0)

    def test_structure_threshold_controls_retest_and_false_breakout(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        closes = [99.5, 99.7, 99.8, 100.5, 100.95, 99.0, 99.1, 99.2, 99.3, 99.4]
        highs = [100.0, 100.0, 100.0, 101.0, 101.0, 100.0, 99.5, 99.6, 99.7, 99.8]
        lows = [99.0, 99.0, 99.0, 100.0, 100.5, 98.5, 98.8, 98.9, 99.0, 99.1]
        rows = []
        for i, close in enumerate(closes):
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.02,
                    "high": highs[i],
                    "low": lows[i],
                    "close": close,
                    "volume": 1000.0 + i,
                }
            )
        raw = pd.DataFrame(rows)

        narrow = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"rolling_window": 3, "threshold_fine": 0.0001},
        )
        wide = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"rolling_window": 3, "threshold_fine": 0.001},
        )

        self.assertEqual(int(narrow.loc[4, "retest_flag"]), 0)
        self.assertEqual(int(wide.loc[4, "retest_flag"]), 1)
        self.assertEqual(int(narrow.loc[4, "false_breakout_flag"]), 1)
        self.assertEqual(int(wide.loc[4, "false_breakout_flag"]), 0)

    def test_fibo_uses_calibrated_window_and_level(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(40):
            close = 100.0 + i
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close - 0.1,
                    "high": close + (i % 5) + 0.5,
                    "low": close - (i % 4) - 0.5,
                    "close": close,
                    "volume": 1000.0 + i,
                }
            )
        raw = pd.DataFrame(rows)
        out = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={"fib_window": 5, "fib_level": 0.236},
        )

        ix = 20
        fib_high = raw["high"].rolling(5).max().loc[ix]
        fib_low = raw["low"].rolling(5).min().loc[ix]
        fib_range = fib_high - fib_low
        primary = fib_low + fib_range * 0.236
        pair = fib_low + fib_range * 0.764
        self.assertAlmostEqual(float(out.loc[ix, "fib_0382_distance"]), float((raw.loc[ix, "close"] - primary) / raw.loc[ix, "close"]))
        self.assertAlmostEqual(float(out.loc[ix, "fib_0618_distance"]), float((raw.loc[ix, "close"] - pair) / raw.loc[ix, "close"]))

    def test_pattern_structure_volume_entry_uses_volume_threshold(self) -> None:
        t0 = datetime(2026, 5, 20, 0, 0, tzinfo=timezone.utc)
        rows = []
        for i in range(80):
            close = 100.0 + ((i % 6) * 0.02)
            low = close - 0.08
            volume = 1000.0
            if i in (30, 35):
                close = 98.05
                low = 98.0
            if i == 35:
                volume = 1800.0
            rows.append(
                {
                    "open_time_utc": t0 + timedelta(minutes=i),
                    "close_time_utc": t0 + timedelta(minutes=i + 1),
                    "open": close + 0.01,
                    "high": close + 0.12,
                    "low": low,
                    "close": close,
                    "volume": volume,
                }
            )
        raw = pd.DataFrame(rows)
        enabled = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={
                "rolling_window": 10,
                "pattern_window": 10,
                "min_touches": 2,
                "level_distance_threshold": 0.002,
                "vol_z_window": 10,
                "volume_confirm_threshold": 0.5,
            },
        )
        blocked = build_feature_frame(
            raw,
            horizon_bars=1,
            include_dropna=False,
            calibration_params={
                "rolling_window": 10,
                "pattern_window": 10,
                "min_touches": 2,
                "level_distance_threshold": 0.002,
                "vol_z_window": 10,
                "volume_confirm_threshold": 99.0,
            },
        )

        self.assertEqual(int(enabled.loc[35, "double_bottom_flag"]), 1)
        self.assertEqual(int(enabled.loc[35, "pattern_level_confirm_flag"]), 1)
        self.assertEqual(int(enabled.loc[35, "pattern_volume_confirm_flag"]), 1)
        self.assertEqual(int(enabled.loc[35, "pattern_structure_volume_entry_long"]), 1)
        self.assertEqual(int(blocked.loc[35, "pattern_volume_confirm_flag"]), 0)
        self.assertEqual(int(blocked.loc[35, "pattern_structure_volume_entry_long"]), 0)


if __name__ == "__main__":
    unittest.main()
