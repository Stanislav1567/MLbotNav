import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from mlbotnav.visual_entry_generalization_v7_runner import (
    STATUS,
    _online_duplicate_filter,
    _raw_variant_signals,
    run_search,
)


def _manual_entry(start: datetime, entry_idx: int) -> dict:
    signal_idx = entry_idx - 1
    return {
        "entry_id": "ME_G7_1",
        "entry_number": 1,
        "side": "long",
        "signal_candle_time_utc": (start + timedelta(minutes=signal_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "target_entry_time_utc": (start + timedelta(minutes=entry_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_open_price": 100.0,
        "entry_price_with_slippage": 100.05,
        "tolerance_bars_before": 0,
        "tolerance_bars_after": 0,
    }


def _row(start: datetime, idx: int, *, hot: bool = False, entry_only_hot: bool = False) -> dict:
    setup = hot or entry_only_hot
    return {
        "open_time_utc": start + timedelta(minutes=idx),
        "open": 100.0,
        "high": 100.25,
        "low": 99.75 if setup else 99.95,
        "close": 100.18 if setup else 100.0,
        "volume": 1000.0,
        "range_pos_60": 0.65 if setup else 0.92,
        "low_range_pos_60": 0.62 if setup else 0.92,
        "local_low_5": hot,
        "local_low_10": hot,
        "local_low_20": hot,
        "support_touch_count_60": 10 if setup else 0,
        "distance_to_event_low_pct": 0.15 if setup else 999.0,
        "pullback_from_recent_high_20_pct": 0.12 if setup else 0.0,
        "ret_6_pct": 0.02 if setup else 0.4,
        "ret_12_pct": 0.16 if setup else 0.0,
        "ret_24_pct": 0.12 if setup else 0.0,
        "rsi14": 68.0 if setup else 45.0,
        "stoch_k14": 82.0 if setup else 45.0,
        "mfi14": 62.0 if setup else 45.0,
        "lower_wick_share": 0.18 if setup else 0.0,
        "close_pos_candle": 0.70 if setup else 0.0,
        "vol_z20": 0.2 if setup else -0.1,
        "ema20_slope_5_pct": 0.03 if setup else 0.0,
        "ema_gap_pct": 0.02,
        "new_low_count_20": 3 if setup else 0,
        "lower_low_streak_5": 1 if setup else 0,
    }


class VisualEntryGeneralizationV7RunnerTests(unittest.TestCase):
    def test_run_search_keeps_contract_and_no_ml(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            start = datetime(2026, 5, 13, tzinfo=timezone.utc)
            manual_entries = tmp_path / "manual_entries.json"
            manual_entries.write_text(
                json.dumps(
                    {
                        "symbol": "SOLUSDT",
                        "timeframe": "1m",
                        "dataset_role": "VALIDATION_DAY",
                        "source_images": [{"date_utc": "2026-05-13", "source_csv": str(tmp_path / "part-final.csv")}],
                        "entries": [_manual_entry(start, 18)],
                    }
                ),
                encoding="utf-8",
            )
            rows = [_row(start, idx) for idx in range(40)]
            rows[17] = _row(start, 17, hot=True)

            with (
                patch("mlbotnav.visual_entry_generalization_v7_runner._prepare_rows", return_value=({}, rows)),
                patch("mlbotnav.visual_entry_generalization_v7_runner._enrich_quality_rows", return_value=None),
                patch("mlbotnav.visual_entry_generalization_v7_runner._with_event_features", return_value=None),
                patch(
                    "mlbotnav.visual_entry_generalization_v7_runner.render_family_candidate_overlay",
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
            self.assertEqual(signal["signal_time_utc"], "2026-05-13T00:17:00Z")
            self.assertEqual(signal["entry_time_utc"], "2026-05-13T00:18:00Z")
            self.assertEqual(signal["entry_rule"], "next_bar_open_after_signal_close")
            self.assertEqual(signal["lookahead"], "NO")

    def test_signal_does_not_use_entry_candle_features(self):
        start = datetime(2026, 5, 13, tzinfo=timezone.utc)
        rows = [_row(start, idx) for idx in range(19)]
        rows[17] = _row(start, 17, hot=False)
        rows[18] = _row(start, 18, entry_only_hot=True)
        variant = {
            "family_id": "G7_01_HOT_FIRST_RECLAIM_DIAG",
            "bucket": "HOT_FIRST_RECLAIM",
            "min_score": 8,
            "start_idx": 14,
            "duplicate_gap_bars": 4,
            "description_ru": "test",
        }
        signals = _raw_variant_signals(rows, variant)
        self.assertEqual(signals, [])

    def test_duplicate_filter_is_online_first_not_future_best(self):
        start = datetime(2026, 5, 13, tzinfo=timezone.utc)
        signals = [
            {"signal_row_index": 17, "signal_time_utc": (start + timedelta(minutes=17)).strftime("%Y-%m-%dT%H:%M:%SZ")},
            {"signal_row_index": 18, "signal_time_utc": (start + timedelta(minutes=18)).strftime("%Y-%m-%dT%H:%M:%SZ")},
            {"signal_row_index": 24, "signal_time_utc": (start + timedelta(minutes=24)).strftime("%Y-%m-%dT%H:%M:%SZ")},
        ]
        kept = _online_duplicate_filter(signals, duplicate_gap_bars=3)
        self.assertEqual([item["signal_row_index"] for item in kept], [17, 24])


if __name__ == "__main__":
    unittest.main()
