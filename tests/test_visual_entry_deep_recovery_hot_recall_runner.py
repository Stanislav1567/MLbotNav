import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from mlbotnav.visual_entry_deep_recovery_hot_recall_runner import run_search


def _manual_entry(start: datetime, entry_idx: int, number: int) -> dict:
    signal_idx = entry_idx - 1
    return {
        "entry_id": f"ME_DRHR_{number}",
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
        "range_pos_60": 0.90,
        "low_range_pos_60": 0.90,
        "local_low_5": False,
        "local_low_10": False,
        "local_low_20": False,
        "support_touch_count_60": 1,
        "ret_6_pct": 0.30,
        "ret_12_pct": 0.40,
        "ret_24_pct": 0.60,
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


def _deep_recovery_row(start: datetime, idx: int) -> dict:
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
            "support_touch_count_60": 12,
            "ret_6_pct": -0.10,
            "ret_12_pct": -0.40,
            "ret_24_pct": -0.60,
            "rsi14": 38.0,
            "stoch_k14": 34.0,
            "mfi14": 36.0,
            "lower_wick_share": 0.25,
            "close_pos_candle": 0.40,
            "vol_z20": 0.50,
            "ema20_slope_5_pct": -0.03,
            "new_low_count_20": 8,
            "lower_low_streak_5": 2,
        }
    )
    return row


def _manual_payload(tmp_path: Path, start: datetime) -> Path:
    path = tmp_path / "manual_entries.json"
    path.write_text(
        json.dumps(
            {
                "symbol": "SOLUSDT",
                "timeframe": "1m",
                "dataset_role": "HOLDOUT_DAY",
                "source_images": [{"date_utc": "2026-05-14", "source_csv": str(tmp_path / "part-final.csv")}],
                "entries": [_manual_entry(start, 71, 1)],
            }
        ),
        encoding="utf-8",
    )
    return path


class VisualEntryDeepRecoveryHotRecallRunnerTests(unittest.TestCase):
    def test_deep_recovery_report_uses_next_open_and_no_ml(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            start = datetime(2026, 5, 14, tzinfo=timezone.utc)
            manual_entries = _manual_payload(tmp_path, start)
            rows = [_base_row(start, idx) for idx in range(90)]
            rows[70] = _deep_recovery_row(start, 70)

            with (
                patch("mlbotnav.visual_entry_deep_recovery_hot_recall_runner._prepare_rows", return_value=({}, rows)),
                patch("mlbotnav.visual_entry_deep_recovery_hot_recall_runner._enrich_quality_rows", return_value=None),
                patch(
                    "mlbotnav.visual_entry_deep_recovery_hot_recall_runner.render_family_candidate_overlay",
                    return_value=tmp_path / "overlay.png",
                ),
            ):
                payload = run_search(manual_entries, tmp_path, render_top=4)

            self.assertEqual(payload["status"], "DEV_DEEP_RECOVERY_AND_HOT_RECALL_V4_ENTRY_ONLY_NO_ML")
            self.assertTrue(payload["online_event_state_used"])
            self.assertFalse(payload["cooldown_used"])
            self.assertFalse(payload["future_trade_outcome_used"])
            self.assertFalse(payload["entry_candle_ohlcv_features_used"])
            self.assertFalse(payload["ml_transfer_allowed"])
            deep = next(item for item in payload["best_overall"] if item["family_id"] == "DRHR01_DEEP_RECOVERY_COLD_RECLAIM")
            signal = deep["signals"][0]
            self.assertEqual(signal["signal_row_index"], 70)
            self.assertEqual(signal["entry_row_index"], 71)
            self.assertEqual(signal["entry_rule"], "next_bar_open_after_signal_close")
            self.assertEqual(signal["lookahead"], "NO")

    def test_entry_candle_ohlcv_does_not_change_deep_recovery_signal(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            start = datetime(2026, 5, 14, tzinfo=timezone.utc)
            manual_entries = _manual_payload(tmp_path, start)
            rows_a = [_base_row(start, idx) for idx in range(90)]
            rows_a[70] = _deep_recovery_row(start, 70)
            rows_b = [dict(row) for row in rows_a]
            rows_b[71] = dict(rows_b[71])
            rows_b[71].update({"high": 150.0, "low": 50.0, "close": 140.0, "volume": 999999.0})

            def run(rows):
                with (
                    patch("mlbotnav.visual_entry_deep_recovery_hot_recall_runner._prepare_rows", return_value=({}, rows)),
                    patch("mlbotnav.visual_entry_deep_recovery_hot_recall_runner._enrich_quality_rows", return_value=None),
                    patch(
                        "mlbotnav.visual_entry_deep_recovery_hot_recall_runner.render_family_candidate_overlay",
                        return_value=tmp_path / "overlay.png",
                    ),
                ):
                    return run_search(manual_entries, tmp_path, render_top=4)

            payload_a = run(rows_a)
            payload_b = run(rows_b)
            deep_a = next(item for item in payload_a["best_overall"] if item["family_id"] == "DRHR01_DEEP_RECOVERY_COLD_RECLAIM")
            deep_b = next(item for item in payload_b["best_overall"] if item["family_id"] == "DRHR01_DEEP_RECOVERY_COLD_RECLAIM")

            self.assertEqual(deep_a["signals"][0]["signal_row_index"], 70)
            self.assertEqual(deep_b["signals"][0]["signal_row_index"], 70)
            self.assertEqual(deep_a["signals"][0]["entry_time_utc"], deep_b["signals"][0]["entry_time_utc"])


if __name__ == "__main__":
    unittest.main()
