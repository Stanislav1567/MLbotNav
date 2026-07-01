import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from mlbotnav.visual_entry_regime_false_suppression_runner import _passes_filters, run_search


def _manual_entry(start: datetime, entry_idx: int, number: int) -> dict:
    signal_idx = entry_idx - 1
    return {
        "entry_id": f"ME_FSV_{number}",
        "entry_number": number,
        "side": "long",
        "signal_candle_time_utc": (start + timedelta(minutes=signal_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "target_entry_time_utc": (start + timedelta(minutes=entry_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_open_price": 100.0,
        "entry_price_with_slippage": 100.05,
        "tolerance_bars_before": 0,
        "tolerance_bars_after": 0,
    }


def _base_row(start: datetime, idx: int) -> dict:
    return {
        "open_time_utc": start + timedelta(minutes=idx),
        "open": 100.0,
        "high": 100.20,
        "low": 99.95,
        "close": 100.0,
        "volume": 1000.0,
        "range_pos_60": 0.90,
        "low_range_pos_60": 0.90,
        "local_low_5": False,
        "local_low_10": False,
        "local_low_20": False,
        "support_touch_count_60": 0,
        "ret_6_pct": 0.40,
        "ret_12_pct": 0.50,
        "ret_24_pct": 0.70,
        "rsi14": 90.0,
        "stoch_k14": 90.0,
        "mfi14": 90.0,
        "lower_wick_share": 0.0,
        "close_pos_candle": 0.0,
        "vol_z20": -0.20,
        "ema20_slope_5_pct": -0.08,
        "ema_gap_pct": -0.05,
        "lower_low_streak_5": 1,
        "new_low_count_20": 3,
    }


def _setup_row(start: datetime, idx: int, regime: str) -> dict:
    row = _base_row(start, idx)
    row.update(
        {
            "low": 99.55,
            "close": 100.12,
            "range_pos_60": 0.08,
            "low_range_pos_60": 0.04,
            "local_low_5": True,
            "local_low_10": True,
            "local_low_20": True,
            "support_touch_count_60": 20,
            "ret_6_pct": -0.08,
            "ret_12_pct": -0.38,
            "ret_24_pct": -0.60,
            "rsi14": 38.0,
            "stoch_k14": 34.0,
            "mfi14": 36.0,
            "lower_wick_share": 0.34,
            "close_pos_candle": 0.86,
            "vol_z20": 0.50,
            "ema20_slope_5_pct": -0.01,
        }
    )
    if regime == "hot":
        row.update({"ret_12_pct": 0.04, "ret_24_pct": 0.18, "rsi14": 64.0, "stoch_k14": 62.0, "mfi14": 58.0})
    elif regime == "trend":
        row.update({"ret_12_pct": -0.05, "ret_24_pct": 0.08, "rsi14": 62.0, "stoch_k14": 66.0, "mfi14": 64.0, "ema20_slope_5_pct": 0.03})
    elif regime == "structure":
        row.update({"ret_12_pct": -0.04, "ret_24_pct": -0.05, "rsi14": 72.0, "stoch_k14": 74.0, "mfi14": 52.0, "vol_z20": 1.10})
    return row


class VisualEntryRegimeFalseSuppressionRunnerTests(unittest.TestCase):
    def test_filter_aliases_match_signal_debug_keys(self):
        signal = {
            "debug": {
                "low_zone": 0.04,
                "ret_12_pct": -0.38,
                "rsi14": 38.0,
                "stoch_k14": 34.0,
                "mfi14": 36.0,
                "lower_wick_share": 0.34,
                "close_pos_candle": 0.86,
                "vol_z20": 0.50,
            }
        }

        ok, passed, suppressed = _passes_filters(
            signal,
            {
                "low_zone_max": 0.14,
                "ret12_max": -0.30,
                "rsi_max": 45.0,
                "stoch_max": 45.0,
                "mfi_max": 45.0,
                "wick_min": 0.25,
                "closepos_min": 0.30,
                "volz_min": 0.15,
            },
        )

        self.assertTrue(ok)
        self.assertGreaterEqual(len(passed), 8)
        self.assertEqual(suppressed, [])

    def test_report_uses_next_open_no_ml_and_counts_suppression(self):
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
                        "entries": [
                            _manual_entry(start, 71, 1),
                            _manual_entry(start, 86, 2),
                            _manual_entry(start, 101, 3),
                            _manual_entry(start, 116, 4),
                        ],
                    }
                ),
                encoding="utf-8",
            )
            rows = [_base_row(start, idx) for idx in range(150)]
            rows[70] = _setup_row(start, 70, "deep")
            rows[85] = _setup_row(start, 85, "hot")
            rows[100] = _setup_row(start, 100, "trend")
            rows[115] = _setup_row(start, 115, "structure")
            suppressed_candidate = _setup_row(start, 125, "deep")
            suppressed_candidate["close_pos_candle"] = 0.05
            suppressed_candidate["lower_wick_share"] = 0.05
            rows[125] = suppressed_candidate

            with (
                patch("mlbotnav.visual_entry_regime_false_suppression_runner._prepare_rows", return_value=({}, rows)),
                patch("mlbotnav.visual_entry_regime_false_suppression_runner._enrich_quality_rows", return_value=None),
                patch(
                    "mlbotnav.visual_entry_regime_false_suppression_runner.render_family_candidate_overlay",
                    return_value=tmp_path / "overlay.png",
                ),
            ):
                payload = run_search(manual_entries, tmp_path, render_top=4)

            self.assertEqual(payload["status"], "DEV_REGIME_FALSE_SUPPRESSION_V2_ENTRY_ONLY_NO_ML")
            self.assertTrue(payload["online_duplicate_suppression_used"])
            self.assertFalse(payload["cooldown_used"])
            self.assertFalse(payload["future_trade_outcome_used"])
            self.assertFalse(payload["ml_transfer_allowed"])
            self.assertTrue(payload["best_overall"])
            self.assertTrue(any(item["suppressed_candidates_total"] > 0 for item in payload["best_overall"]))
            for result in payload["best_overall"]:
                for signal in result["signals"]:
                    self.assertEqual(signal["entry_row_index"], signal["signal_row_index"] + 1)
                    self.assertEqual(signal["entry_rule"], "next_bar_open_after_signal_close")
                    self.assertEqual(signal["lookahead"], "NO")


if __name__ == "__main__":
    unittest.main()
