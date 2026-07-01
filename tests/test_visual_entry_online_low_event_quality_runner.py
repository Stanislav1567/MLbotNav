import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from mlbotnav.visual_entry_online_low_event_quality_runner import _with_event_features, run_search


def _manual_entry(start: datetime, entry_idx: int, number: int) -> dict:
    signal_idx = entry_idx - 1
    return {
        "entry_id": f"ME_OLEV_{number}",
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
        "high": 100.25,
        "low": 99.95,
        "close": 100.0,
        "volume": 1000.0,
        "range_pos_60": 0.92,
        "low_range_pos_60": 0.92,
        "local_low_5": False,
        "local_low_10": False,
        "local_low_20": False,
        "support_touch_count_60": 2,
        "ret_6_pct": 0.35,
        "ret_12_pct": 0.45,
        "ret_24_pct": 0.65,
        "rsi14": 80.0,
        "stoch_k14": 82.0,
        "mfi14": 78.0,
        "lower_wick_share": 0.0,
        "close_pos_candle": 0.20,
        "vol_z20": -0.10,
        "ema20_slope_5_pct": -0.08,
        "ema_gap_pct": -0.04,
        "lower_low_streak_5": 1,
        "new_low_count_20": 3,
    }


def _setup_row(start: datetime, idx: int, regime: str = "deep") -> dict:
    row = _base_row(start, idx)
    row.update(
        {
            "high": 100.35,
            "low": 99.20,
            "close": 100.12,
            "range_pos_60": 0.08,
            "low_range_pos_60": 0.04,
            "local_low_5": True,
            "local_low_10": True,
            "local_low_20": True,
            "support_touch_count_60": 20,
            "ret_6_pct": -0.10,
            "ret_12_pct": -0.38,
            "ret_24_pct": -0.60,
            "rsi14": 38.0,
            "stoch_k14": 34.0,
            "mfi14": 36.0,
            "lower_wick_share": 0.34,
            "close_pos_candle": 0.86,
            "vol_z20": 0.50,
            "ema20_slope_5_pct": -0.01,
            "new_low_count_20": 5,
        }
    )
    if regime == "hot":
        row.update({"ret_12_pct": 0.04, "ret_24_pct": 0.02, "rsi14": 64.0, "stoch_k14": 62.0, "mfi14": 58.0})
    elif regime == "trend":
        row.update({"ret_12_pct": -0.05, "ret_24_pct": 0.02, "rsi14": 62.0, "stoch_k14": 66.0, "mfi14": 64.0, "ema20_slope_5_pct": 0.03})
    elif regime == "structure":
        row.update({"ret_12_pct": -0.04, "ret_24_pct": -0.05, "rsi14": 60.0, "stoch_k14": 58.0, "mfi14": 52.0, "vol_z20": 1.10})
    return row


def _payload(tmp_path: Path, start: datetime) -> Path:
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
    return manual_entries


class VisualEntryOnlineLowEventQualityRunnerTests(unittest.TestCase):
    def test_event_features_are_online_and_signal_scoped(self):
        start = datetime(2026, 5, 14, tzinfo=timezone.utc)
        rows = [_base_row(start, idx) for idx in range(90)]
        rows[70] = _setup_row(start, 70, "deep")
        _with_event_features(rows)

        self.assertTrue(rows[70]["low_event_active"])
        self.assertEqual(rows[70]["low_event_age_bars"], 0)
        self.assertEqual(rows[70]["candidate_order_in_event"], 1)
        self.assertEqual(rows[70]["bars_since_event_low"], 0)
        self.assertGreaterEqual(rows[70]["pullback_from_recent_high_20_pct"], 0.0)

    def test_report_uses_next_open_no_ml_and_event_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            start = datetime(2026, 5, 14, tzinfo=timezone.utc)
            manual_entries = _payload(tmp_path, start)
            rows = [_base_row(start, idx) for idx in range(150)]
            rows[70] = _setup_row(start, 70, "deep")
            rows[85] = _setup_row(start, 85, "hot")
            rows[100] = _setup_row(start, 100, "trend")
            rows[115] = _setup_row(start, 115, "structure")

            with (
                patch("mlbotnav.visual_entry_online_low_event_quality_runner._prepare_rows", return_value=({}, rows)),
                patch("mlbotnav.visual_entry_online_low_event_quality_runner._enrich_quality_rows", return_value=None),
                patch(
                    "mlbotnav.visual_entry_online_low_event_quality_runner.render_family_candidate_overlay",
                    return_value=tmp_path / "overlay.png",
                ),
            ):
                payload = run_search(manual_entries, tmp_path, render_top=4)

            self.assertEqual(payload["status"], "DEV_ONLINE_LOW_EVENT_QUALITY_V3_ENTRY_ONLY_NO_ML")
            self.assertTrue(payload["online_event_state_used"])
            self.assertFalse(payload["cooldown_used"])
            self.assertFalse(payload["future_trade_outcome_used"])
            self.assertFalse(payload["entry_candle_ohlcv_features_used"])
            self.assertFalse(payload["ml_transfer_allowed"])
            self.assertTrue(payload["best_overall"])
            signal = payload["best_overall"][0]["signals"][0]
            self.assertEqual(signal["entry_row_index"], signal["signal_row_index"] + 1)
            self.assertEqual(signal["entry_rule"], "next_bar_open_after_signal_close")
            self.assertEqual(signal["lookahead"], "NO")
            self.assertIn("low_event_age_bars", signal["debug"])

    def test_entry_candle_ohlcv_does_not_change_previous_signal_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            start = datetime(2026, 5, 14, tzinfo=timezone.utc)
            manual_entries = _payload(tmp_path, start)
            rows_a = [_base_row(start, idx) for idx in range(90)]
            rows_a[70] = _setup_row(start, 70, "deep")
            rows_b = [dict(row) for row in rows_a]
            rows_b[71] = dict(rows_b[71])
            rows_b[71].update({"high": 150.0, "low": 50.0, "close": 140.0, "volume": 999999.0})

            def run(rows):
                with (
                    patch("mlbotnav.visual_entry_online_low_event_quality_runner._prepare_rows", return_value=({}, rows)),
                    patch("mlbotnav.visual_entry_online_low_event_quality_runner._enrich_quality_rows", return_value=None),
                    patch(
                        "mlbotnav.visual_entry_online_low_event_quality_runner.render_family_candidate_overlay",
                        return_value=tmp_path / "overlay.png",
                    ),
                ):
                    return run_search(manual_entries, tmp_path, render_top=1)

            payload_a = run(rows_a)
            payload_b = run(rows_b)
            first_a = payload_a["best_overall"][0]["signals"][0]
            first_b = payload_b["best_overall"][0]["signals"][0]

            self.assertEqual(first_a["signal_row_index"], 70)
            self.assertEqual(first_b["signal_row_index"], 70)
            self.assertEqual(first_a["entry_time_utc"], first_b["entry_time_utc"])


if __name__ == "__main__":
    unittest.main()
