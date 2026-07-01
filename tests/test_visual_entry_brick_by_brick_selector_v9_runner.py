import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from mlbotnav.visual_entry_brick_by_brick_selector_v9_runner import (
    STATUS,
    _brick_reject_reasons,
    run_search,
)


def _manual_entry(start: datetime, entry_idx: int) -> dict:
    signal_idx = entry_idx - 1
    return {
        "entry_id": "ME_V9_1",
        "entry_number": 1,
        "side": "long",
        "signal_candle_time_utc": (start + timedelta(minutes=signal_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "target_entry_time_utc": (start + timedelta(minutes=entry_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_open_price": 100.0,
        "entry_price_with_slippage": 100.05,
        "tolerance_bars_before": 0,
        "tolerance_bars_after": 0,
    }


def _row(start: datetime, idx: int, *, hot_chain: bool = False, hot_first: bool = False) -> dict:
    return {
        "open_time_utc": start + timedelta(minutes=idx),
        "open": 100.0,
        "high": 100.25,
        "low": 99.55 if hot_chain else (99.75 if hot_first else 99.95),
        "close": 99.60 if hot_chain else (100.22 if hot_first else 100.0),
        "volume": 1000.0,
        "range_pos_60": 0.75 if hot_chain else (0.68 if hot_first else 0.92),
        "low_range_pos_60": 0.72 if hot_chain else (0.62 if hot_first else 0.92),
        "local_low_5": hot_chain or hot_first,
        "local_low_10": hot_chain or hot_first,
        "local_low_20": hot_chain or hot_first,
        "support_touch_count_60": 4 if hot_chain else 10,
        "distance_to_event_low_pct": 0.0 if hot_chain else 0.15,
        "pullback_from_recent_high_20_pct": 0.23 if hot_chain else 0.12,
        "ret_6_pct": -0.08 if hot_chain else 0.15,
        "ret_12_pct": 0.45 if hot_chain else 0.16,
        "ret_24_pct": 0.40 if hot_chain else 0.12,
        "rsi14": 78.0 if hot_chain else 68.0,
        "stoch_k14": 72.0 if hot_chain else 82.0,
        "mfi14": 70.0 if hot_chain else 62.0,
        "lower_wick_share": 0.10 if hot_chain else 0.18,
        "close_pos_candle": 0.10 if hot_chain else 0.90,
        "vol_z20": 0.2,
        "ema20_slope_5_pct": 0.16 if hot_chain else 0.03,
        "ema_gap_pct": 0.02,
        "new_low_count_20": 6,
        "lower_low_streak_5": 3 if hot_chain else 0,
        "bars_since_event_low": 0 if hot_chain else 5,
        "bars_since_recent_high_20": 3 if hot_chain else 10,
    }


class VisualEntryBrickByBrickSelectorV9RunnerTests(unittest.TestCase):
    def test_hot_chain_brick_rejects_non_event_low(self):
        signal = {
            "debug": {
                "distance_to_event_low_pct": 0.35,
                "bars_since_event_low": 4,
                "lower_low_streak_5": 3,
                "ema20_slope_5_pct": 0.16,
                "pullback_from_recent_high_20_pct": 0.25,
                "support_touch_count_60": 4,
            }
        }
        reasons = _brick_reject_reasons(signal, "HOT_CHAIN_EVENT_LOW")
        self.assertIn("V9_HOT_CHAIN_NOT_EVENT_LOW", reasons)
        self.assertIn("V9_HOT_CHAIN_NOT_FRESH_EVENT_LOW", reasons)

    def test_run_search_keeps_next_open_contract_and_blocks_ml(self):
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
                        "entries": [_manual_entry(start, 19)],
                    }
                ),
                encoding="utf-8",
            )
            rows = [_row(start, idx) for idx in range(45)]
            rows[14] = _row(start, 14, hot_first=True)
            for idx in range(15, 18):
                rows[idx] = _row(start, idx, hot_first=True)
            rows[18] = _row(start, 18, hot_chain=True)

            with (
                patch("mlbotnav.visual_entry_brick_by_brick_selector_v9_runner._prepare_rows", return_value=({}, rows)),
                patch("mlbotnav.visual_entry_brick_by_brick_selector_v9_runner._enrich_quality_rows", return_value=None),
                patch("mlbotnav.visual_entry_brick_by_brick_selector_v9_runner._with_event_features", return_value=None),
                patch(
                    "mlbotnav.visual_entry_brick_by_brick_selector_v9_runner.render_family_candidate_overlay",
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
            self.assertEqual(signal["signal_time_utc"], "2026-05-13T00:18:00Z")
            self.assertEqual(signal["entry_time_utc"], "2026-05-13T00:19:00Z")
            self.assertEqual(signal["entry_rule"], "next_bar_open_after_signal_close")
            self.assertEqual(signal["lookahead"], "NO")


if __name__ == "__main__":
    unittest.main()
