import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from mlbotnav.visual_entry_low_cluster_ranker_runner import run_search


def _manual_entry(start: datetime, entry_idx: int) -> dict:
    signal_idx = entry_idx - 1
    return {
        "entry_id": "ME_LCR_1",
        "entry_number": 1,
        "side": "long",
        "signal_candle_time_utc": (start + timedelta(minutes=signal_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "target_entry_time_utc": (start + timedelta(minutes=entry_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_open_price": 100.0,
        "entry_price_with_slippage": 100.05,
        "tolerance_bars_before": 0,
        "tolerance_bars_after": 0,
    }


def _row(start: datetime, idx: int, *, setup: bool = False, stronger: bool = False) -> dict:
    return {
        "open_time_utc": start + timedelta(minutes=idx),
        "open": 100.0,
        "high": 100.20,
        "low": 99.65 if setup else 99.95,
        "close": 100.15 if stronger else (100.05 if setup else 100.0),
        "volume": 1000.0,
        "range_pos_60": 0.04 if setup else 0.90,
        "low_range_pos_60": 0.01 if setup else 0.90,
        "local_low_5": setup,
        "local_low_10": setup,
        "local_low_20": setup,
        "support_touch_count_60": 18 if setup else 0,
        "ret_6_pct": -0.10 if setup else 0.30,
        "ret_12_pct": -0.35 if setup else 0.50,
        "ret_24_pct": -0.55 if setup else 0.70,
        "rsi14": 38.0 if setup else 90.0,
        "stoch_k14": 30.0 if setup else 90.0,
        "mfi14": 32.0 if setup else 90.0,
        "lower_wick_share": 0.35 if setup else 0.0,
        "close_pos_candle": 0.85 if stronger else (0.60 if setup else 0.0),
        "vol_z20": 0.40 if setup else -0.20,
        "ema20_slope_5_pct": -0.01 if setup else 0.0,
        "ema_gap_pct": -0.05,
        "lower_low_streak_5": 1,
        "new_low_count_20": 3,
    }


class VisualEntryLowClusterRankerRunnerTests(unittest.TestCase):
    def test_ranker_selects_one_cluster_winner_and_next_open(self):
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
                        "entries": [_manual_entry(start, 83)],
                    }
                ),
                encoding="utf-8",
            )
            rows = [_row(start, idx) for idx in range(130)]
            rows[80] = _row(start, 80, setup=True)
            rows[82] = _row(start, 82, setup=True, stronger=True)

            with (
                patch(
                    "mlbotnav.visual_entry_low_cluster_ranker_runner._prepare_rows",
                    return_value=({}, rows),
                ),
                patch(
                    "mlbotnav.visual_entry_low_cluster_ranker_runner._enrich_quality_rows",
                    return_value=None,
                ),
                patch(
                    "mlbotnav.visual_entry_low_cluster_ranker_runner.render_family_candidate_overlay",
                    return_value=tmp_path / "overlay.png",
                ),
            ):
                payload = run_search(manual_entries, tmp_path, render_top=1)

            self.assertEqual(payload["status"], "DEV_LOW_CLUSTER_RANKER_V2_ENTRY_ONLY_NO_ML")
            self.assertTrue(payload["cluster_selection_used"])
            self.assertFalse(payload["cooldown_used"])
            self.assertFalse(payload["future_trade_outcome_used"])
            self.assertFalse(payload["ml_transfer_allowed"])
            top = payload["best_overall"][0]
            self.assertGreaterEqual(top["score"]["target_hits"], 1)
            signal = top["signals"][0]
            self.assertEqual(signal["signal_time_utc"], "2026-05-14T01:22:00Z")
            self.assertEqual(signal["entry_time_utc"], "2026-05-14T01:23:00Z")
            self.assertEqual(signal["entry_rule"], "next_bar_open_after_signal_close")
            self.assertEqual(signal["lookahead"], "NO")
            self.assertGreaterEqual(signal["cluster_size"], 2)


if __name__ == "__main__":
    unittest.main()
