import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from mlbotnav.visual_entry_event_ranked_bricks_v10_runner import (
    STATUS,
    VARIANTS,
    _select_best_per_event,
    run_search,
)


def _manual_entry(start: datetime, entry_idx: int) -> dict:
    signal_idx = entry_idx - 1
    return {
        "entry_id": "ME_V10_1",
        "entry_number": 1,
        "side": "long",
        "signal_candle_time_utc": (start + timedelta(minutes=signal_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "target_entry_time_utc": (start + timedelta(minutes=entry_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_open_price": 100.0,
        "entry_price_with_slippage": 100.05,
        "tolerance_bars_before": 0,
        "tolerance_bars_after": 0,
    }


def _row(start: datetime, idx: int, *, hot_chain: bool = False, event_idx: int | None = None) -> dict:
    return {
        "open_time_utc": start + timedelta(minutes=idx),
        "open": 100.0,
        "high": 100.25,
        "low": 99.55 if hot_chain else 99.95,
        "close": 99.60 if hot_chain else 100.0,
        "volume": 1000.0,
        "range_pos_60": 0.75 if hot_chain else 0.92,
        "low_range_pos_60": 0.72 if hot_chain else 0.92,
        "local_low_5": hot_chain,
        "local_low_10": hot_chain,
        "local_low_20": hot_chain,
        "support_touch_count_60": 4,
        "distance_to_event_low_pct": 0.0 if hot_chain else 0.3,
        "pullback_from_recent_high_20_pct": 0.23 if hot_chain else 0.12,
        "ret_6_pct": -0.08 if hot_chain else 0.1,
        "ret_12_pct": 0.45 if hot_chain else 0.16,
        "ret_24_pct": 0.40 if hot_chain else 0.12,
        "rsi14": 78.0,
        "stoch_k14": 72.0,
        "mfi14": 70.0,
        "lower_wick_share": 0.10,
        "close_pos_candle": 0.10,
        "vol_z20": 0.2,
        "ema20_slope_5_pct": 0.16,
        "ema_gap_pct": 0.02,
        "new_low_count_20": 6,
        "lower_low_streak_5": 3,
        "bars_since_event_low": 0 if hot_chain else 3,
        "bars_since_recent_high_20": 3,
        "low_event_start_idx": event_idx if event_idx is not None else idx,
    }


def _signal(start: datetime, signal_idx: int, *, distance: float, event_low_idx: int) -> dict:
    entry_idx = signal_idx + 1
    return {
        "family_id": "V8_TEST",
        "bucket": "TEST",
        "side": "long",
        "signal_row_index": signal_idx,
        "entry_row_index": entry_idx,
        "signal_time_utc": (start + timedelta(minutes=signal_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_time_utc": (start + timedelta(minutes=entry_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_open_price": 100.0,
        "entry_price_with_slippage": 100.05,
        "slippage_bps": 5,
        "entry_rule": "next_bar_open_after_signal_close",
        "strategy_scope": "test",
        "lookahead": "NO",
        "cooldown_used": False,
        "future_trade_outcome_used": False,
        "priority_score": 10,
        "context_votes": [],
        "trigger_votes": [],
        "confirm_votes": [],
        "suppress_votes": [],
        "debug": {
            "low_event_start_idx": 15,
            "event_low_idx": event_low_idx,
            "distance_to_event_low_pct": distance,
            "bars_since_event_low": 0 if distance == 0.0 else 3,
            "lower_low_streak_5": 3,
            "ema20_slope_5_pct": 0.16,
            "pullback_from_recent_high_20_pct": 0.23,
            "support_touch_count_60": 4,
        },
    }


class VisualEntryEventRankedBricksV10RunnerTests(unittest.TestCase):
    def test_select_best_per_event_keeps_single_rank_winner(self):
        weak = {
            "signal_row_index": 10,
            "entry_row_index": 11,
            "debug": {
                "low_event_start_idx": 7,
                "event_low_idx": 7,
                "distance_to_event_low_pct": 0.3,
                "bars_since_event_low": 3,
                "lower_low_streak_5": 3,
                "ema20_slope_5_pct": 0.16,
                "pullback_from_recent_high_20_pct": 0.23,
                "support_touch_count_60": 4,
            },
        }
        strong = {
            "signal_row_index": 12,
            "entry_row_index": 13,
            "debug": {
                "low_event_start_idx": 7,
                "event_low_idx": 7,
                "distance_to_event_low_pct": 0.0,
                "bars_since_event_low": 0,
                "lower_low_streak_5": 3,
                "ema20_slope_5_pct": 0.16,
                "pullback_from_recent_high_20_pct": 0.23,
                "support_touch_count_60": 4,
            },
        }
        selected, rejected = _select_best_per_event([weak, strong], "HOT_CHAIN_EVENT_LOW")
        self.assertEqual(len(selected), 1)
        self.assertEqual(len(rejected), 1)
        self.assertEqual(selected[0]["signal_row_index"], 12)
        self.assertEqual(rejected[0]["debug"]["v10_rank_reject_reason"], "V10_LOWER_RANK_IN_SAME_EVENT")

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
            for idx in range(15, 18):
                rows[idx] = _row(start, idx, hot_chain=True, event_idx=15)
            rows[18] = _row(start, 18, hot_chain=True, event_idx=15)

            with (
                patch("mlbotnav.visual_entry_event_ranked_bricks_v10_runner._prepare_rows", return_value=({}, rows)),
                patch("mlbotnav.visual_entry_event_ranked_bricks_v10_runner._enrich_quality_rows", return_value=None),
                patch("mlbotnav.visual_entry_event_ranked_bricks_v10_runner._with_event_features", return_value=None),
                patch(
                    "mlbotnav.visual_entry_event_ranked_bricks_v10_runner.VARIANTS",
                    [VARIANTS[0]],
                ),
                patch(
                    "mlbotnav.visual_entry_event_ranked_bricks_v10_runner._filtered_source_signals",
                    return_value=([_signal(start, 16, distance=0.3, event_low_idx=15), _signal(start, 18, distance=0.0, event_low_idx=15)], []),
                ),
                patch(
                    "mlbotnav.visual_entry_event_ranked_bricks_v10_runner.render_family_candidate_overlay",
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
