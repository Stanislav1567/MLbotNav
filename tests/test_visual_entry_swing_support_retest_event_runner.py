import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from mlbotnav.visual_entry_swing_support_retest_event_runner import run_search


def _manual_entry(start: datetime, entry_idx: int, entry_id: str = "ME_1") -> dict:
    signal_idx = entry_idx - 1
    return {
        "entry_id": entry_id,
        "entry_number": 1,
        "side": "long",
        "signal_candle_time_utc": (start + timedelta(minutes=signal_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "target_entry_time_utc": (start + timedelta(minutes=entry_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_open_price": 100.0,
        "entry_price_with_slippage": 100.05,
        "tolerance_bars_before": 0,
        "tolerance_bars_after": 0,
    }


def _row(start: datetime, idx: int, *, setup: bool = False) -> dict:
    return {
        "open_time_utc": start + timedelta(minutes=idx),
        "open": 100.0,
        "high": 100.10,
        "low": 99.80,
        "close": 99.95,
        "volume": 1000.0,
        "range_pos_60": 0.25 if setup else 0.90,
        "low_range_pos_60": 0.20 if setup else 0.90,
        "local_low_5": setup,
        "local_low_10": setup,
        "local_low_20": setup,
        "local_low_60": setup,
        "support_touch_count_60": 20 if setup else 0,
        "ret_6_pct": -0.05 if setup else 0.30,
        "ret_12_pct": 0.10 if setup else 1.10,
        "ret_24_pct": -0.10 if setup else 1.20,
        "rsi14": 55.0 if setup else 95.0,
        "stoch_k14": 50.0 if setup else 95.0,
        "mfi14": 55.0 if setup else 95.0,
        "lower_wick_share": 0.20 if setup else 0.0,
        "close_pos_candle": 0.35 if setup else 0.0,
        "vol_z20": 0.0,
        "lower_low_streak_5": 1,
        "new_low_count_20": 4,
        "ema20_slope_5_pct": 0.02 if setup else -0.20,
        "ema_gap_pct": -0.02,
    }


class VisualEntrySwingSupportRetestEventRunnerTests(unittest.TestCase):
    def test_event_runner_uses_next_open_and_entry_only_scope(self):
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
                        "entries": [_manual_entry(start, 81)],
                    }
                ),
                encoding="utf-8",
            )
            rows = [_row(start, idx) for idx in range(130)]
            rows[80] = _row(start, 80, setup=True)
            rows[81] = _row(start, 81)

            with (
                patch(
                    "mlbotnav.visual_entry_swing_support_retest_event_runner._prepare_rows",
                    return_value=({}, rows),
                ),
                patch(
                    "mlbotnav.visual_entry_swing_support_retest_event_runner._enrich_quality_rows",
                    return_value=None,
                ),
                patch(
                    "mlbotnav.visual_entry_swing_support_retest_event_runner.render_family_candidate_overlay",
                    return_value=tmp_path / "overlay.png",
                ),
            ):
                payload = run_search(manual_entries, tmp_path, render_top=1)

            self.assertEqual(payload["status"], "DEV_SWING_SUPPORT_RETEST_EVENT_V1_ENTRY_ONLY_NO_ML")
            self.assertEqual(payload["strategy_scope"], "entry_only_low_detection")
            self.assertFalse(payload["future_trade_outcome_used"])
            self.assertFalse(payload["ml_transfer_allowed"])
            top = payload["best_overall"][0]
            self.assertEqual(top["score"]["target_hits"], 1)
            self.assertEqual(top["score"]["false_entries"], 0)
            self.assertEqual(len(top["signals"]), 1)
            signal = top["signals"][0]
            self.assertEqual(signal["signal_time_utc"], "2026-05-13T01:20:00Z")
            self.assertEqual(signal["entry_time_utc"], "2026-05-13T01:21:00Z")
            self.assertEqual(signal["entry_rule"], "next_bar_open_after_signal_close")
            self.assertEqual(signal["strategy_scope"], "entry_only_low_detection")
            self.assertEqual(signal["lookahead"], "NO")


if __name__ == "__main__":
    unittest.main()

