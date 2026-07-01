from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from mlbotnav.dataset import FEATURE_COLUMNS, build_feature_frame
from mlbotnav.validation import walk_forward_validate


class ValidationOofColumnsTests(unittest.TestCase):
    def test_walk_forward_oof_contains_feature_space_for_trend_filters(self) -> None:
        n = 900
        idx = pd.date_range("2026-01-01", periods=n, freq="1min", tz="UTC")
        base = 100.0 + np.linspace(0.0, 1.5, n)
        osc = 0.15 * np.sin(np.linspace(0.0, 12.0, n))
        close = base + osc
        open_ = close + 0.01
        high = close + 0.05
        low = close - 0.05
        volume = 1000.0 + 50.0 * np.cos(np.linspace(0.0, 20.0, n))

        raw = pd.DataFrame(
            {
                "open_time_utc": idx,
                "close_time_utc": idx + pd.Timedelta(minutes=1),
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
            }
        )
        frame = build_feature_frame(raw, horizon_bars=1)
        folds, oof = walk_forward_validate(
            frame,
            min_train_rows=220,
            n_folds=2,
            feature_columns=list(FEATURE_COLUMNS),
        )

        self.assertGreater(len(folds), 0)
        required_runtime_cols = [
            "ema20",
            "ema50",
            "ema200",
            "breakout_flag",
            "retest_flag",
            "swing_low_break_flag",
            "density_vpoc_distance_60",
            "density_cluster_ratio_60_240",
        ]
        for col in required_runtime_cols:
            self.assertIn(col, oof.columns)


if __name__ == "__main__":
    unittest.main()
