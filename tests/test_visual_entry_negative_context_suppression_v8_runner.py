import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from mlbotnav.visual_entry_negative_context_suppression_v8_runner import (
    STATUS,
    _negative_reasons,
    run_search,
)


def _manual_entry(start: datetime, entry_idx: int) -> dict:
    signal_idx = entry_idx - 1
    return {
        "entry_id": "ME_V8_1",
        "entry_number": 1,
        "side": "long",
        "signal_candle_time_utc": (start + timedelta(minutes=signal_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "target_entry_time_utc": (start + timedelta(minutes=entry_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_open_price": 100.0,
        "entry_price_with_slippage": 100.05,
        "tolerance_bars_before": 0,
        "tolerance_bars_after": 0,
    }


def _row(start: datetime, idx: int, *, hot_first: bool = False, upper_shelf: bool = False) -> dict:
    return {
        "open_time_utc": start + timedelta(minutes=idx),
        "open": 100.0,
        "high": 100.25,
        "low": 99.75 if hot_first or upper_shelf else 99.95,
        "close": 100.18 if hot_first or upper_shelf else 100.0,
        "volume": 1000.0,
        "range_pos_60": 0.91 if upper_shelf else (0.66 if hot_first else 0.92),
        "low_range_pos_60": 0.90 if upper_shelf else (0.62 if hot_first else 0.92),
        "local_low_5": hot_first or upper_shelf,
        "local_low_10": hot_first or upper_shelf,
        "local_low_20": hot_first or upper_shelf,
        "support_touch_count_60": 10,
        "distance_to_event_low_pct": 0.15,
        "pullback_from_recent_high_20_pct": 0.12,
        "ret_6_pct": 0.02,
        "ret_12_pct": 0.16,
        "ret_24_pct": 0.70 if upper_shelf else 0.12,
        "rsi14": 68.0,
        "stoch_k14": 82.0,
        "mfi14": 90.0 if upper_shelf else 62.0,
        "lower_wick_share": 0.18,
        "close_pos_candle": 0.70,
        "vol_z20": 0.2,
        "ema20_slope_5_pct": 0.03,
        "ema_gap_pct": 0.02,
        "new_low_count_20": 3,
        "lower_low_streak_5": 0,
    }


class VisualEntryNegativeContextSuppressionV8RunnerTests(unittest.TestCase):
    def test_negative_reasons_reject_hot_upper_shelf(self):
        signal = {
            "debug": {
                "low_zone": 0.91,
                "support_touch_count_60": 12,
                "distance_to_event_low_pct": 0.2,
                "ret_24_pct": 0.70,
                "mfi14": 90.0,
                "close_pos_candle": 0.8,
                "hot_run_len": 1,
            }
        }
        reasons = _negative_reasons(signal, "G7_01_HOT_FIRST_RECLAIM_DIAG")
        self.assertIn("HOT_UPPER_SHELF", reasons)
        self.assertIn("HOT_POST_IMPULSE_RET24", reasons)
        self.assertIn("HOT_MFI_EXHAUSTED", reasons)

    def test_run_search_keeps_next_open_and_no_ml_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            start = datetime(2026, 5, 14, tzinfo=timezone.utc)
            manual_entries = tmp_path / "manual_entries.json"
            manual_entries.write_text(
                json.dumps(
                    {
                        "symbol": "SOLUSDT",
                        "timeframe": "1m",
                        "dataset_role": "HOLDOUT_DAY",
                        "source_images": [{"date_utc": "2026-05-14", "source_csv": str(tmp_path / "part-final.csv")}],
                        "entries": [_manual_entry(start, 18)],
                    }
                ),
                encoding="utf-8",
            )
            rows = [_row(start, idx) for idx in range(45)]
            rows[17] = _row(start, 17, hot_first=True)
            rows[28] = _row(start, 28, upper_shelf=True)

            with (
                patch("mlbotnav.visual_entry_negative_context_suppression_v8_runner._prepare_rows", return_value=({}, rows)),
                patch("mlbotnav.visual_entry_negative_context_suppression_v8_runner._enrich_quality_rows", return_value=None),
                patch("mlbotnav.visual_entry_negative_context_suppression_v8_runner._with_event_features", return_value=None),
                patch(
                    "mlbotnav.visual_entry_negative_context_suppression_v8_runner.render_family_candidate_overlay",
                    return_value=tmp_path / "overlay.png",
                ),
            ):
                payload = run_search(manual_entries, tmp_path, render_top=1)

            self.assertEqual(payload["status"], STATUS)
            self.assertFalse(payload["cooldown_used"])
            self.assertFalse(payload["future_trade_outcome_used"])
            self.assertFalse(payload["entry_candle_ohlcv_features_used"])
            self.assertFalse(payload["ml_transfer_allowed"])
            top = payload["best_overall"][0]
            self.assertGreaterEqual(top["score"]["target_hits"], 1)
            signal = top["signals"][0]
            self.assertEqual(signal["signal_time_utc"], "2026-05-14T00:17:00Z")
            self.assertEqual(signal["entry_time_utc"], "2026-05-14T00:18:00Z")
            self.assertEqual(signal["entry_rule"], "next_bar_open_after_signal_close")
            self.assertEqual(signal["lookahead"], "NO")
            self.assertTrue(any(item["suppressed_candidates_total"] >= 1 for item in payload["best_overall"]))


if __name__ == "__main__":
    unittest.main()
