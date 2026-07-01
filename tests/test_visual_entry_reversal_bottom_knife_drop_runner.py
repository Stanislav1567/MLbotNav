import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from mlbotnav.visual_entry_reversal_bottom_knife_drop_runner import run_search


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


def _row(start: datetime, idx: int, *, strong: bool = False) -> dict:
    return {
        "open_time_utc": start + timedelta(minutes=idx),
        "open": 100.0 - idx * 0.01,
        "high": 100.05 - idx * 0.01,
        "low": 99.90 - idx * 0.01,
        "close": 99.98 - idx * 0.01,
        "volume": 1000.0,
        "range_pos_60": 0.05 if strong else 0.80,
        "low_range_pos_60": 0.03 if strong else 0.80,
        "local_low_5": strong,
        "local_low_10": strong,
        "local_low_20": strong,
        "local_low_60": strong,
        "support_touch_count_60": 4 if strong else 0,
        "ret_6_pct": -0.25 if strong else 0.10,
        "ret_12_pct": -0.55 if strong else 0.15,
        "ret_24_pct": -0.75 if strong else 0.20,
        "rsi14": 32.0 if strong else 70.0,
        "stoch_k14": 25.0 if strong else 80.0,
        "mfi14": 30.0 if strong else 75.0,
        "lower_wick_share": 0.30 if strong else 0.02,
        "close_pos_candle": 0.40 if strong else 0.02,
        "vol_z20": 1.2 if strong else -0.3,
        "lower_low_streak_5": 2 if strong else 1,
        "new_low_count_20": 5 if strong else 1,
        "ema20_slope_5_pct": -0.02 if strong else 0.20,
        "ema_gap_pct": -0.10 if strong else 0.20,
        "dist_from_low_60_pct": 0.05 if strong else 1.50,
    }


class VisualEntryReversalBottomKnifeDropRunnerTests(unittest.TestCase):
    def test_runner_creates_reports_and_exact_next_open_signal(self):
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
                        "source_images": [
                            {"date_utc": "2026-05-13", "source_csv": str(tmp_path / "part-final.csv")}
                        ],
                        "entries": [_manual_entry(start, 81)],
                    }
                ),
                encoding="utf-8",
            )
            rows = [_row(start, idx) for idx in range(130)]
            rows[80] = _row(start, 80, strong=True)

            def fake_render(**kwargs):
                png_path = tmp_path / f"{kwargs['label']}.png"
                png_path.write_bytes(b"png")
                return png_path

            with (
                patch(
                    "mlbotnav.visual_entry_reversal_bottom_knife_drop_runner._prepare_rows",
                    return_value=({}, rows),
                ),
                patch(
                    "mlbotnav.visual_entry_reversal_bottom_knife_drop_runner._enrich_quality_rows",
                    return_value=None,
                ),
                patch(
                    "mlbotnav.visual_entry_reversal_bottom_knife_drop_runner.render_family_candidate_overlay",
                    side_effect=fake_render,
                ),
            ):
                payload = run_search(manual_entries, tmp_path, render_top=1)

            self.assertEqual(payload["status"], "DEV_REVERSAL_BOTTOM_KNIFE_DROP_V0_DIAGNOSTIC_NO_ML")
            self.assertFalse(payload["ml_transfer_allowed"])
            self.assertTrue((tmp_path / "visual_entry_reversal_bottom_knife_drop_20260513_VALIDATION_DAY.json").exists())
            self.assertTrue((tmp_path / "visual_entry_reversal_bottom_knife_drop_20260513_VALIDATION_DAY_RU.md").exists())
            top = payload["best_overall"][0]
            self.assertEqual(top["score"]["target_hits"], 1)
            self.assertEqual(top["score"]["false_entries"], 0)
            signal = top["signals"][0]
            self.assertEqual(signal["signal_time_utc"], "2026-05-13T01:20:00Z")
            self.assertEqual(signal["entry_time_utc"], "2026-05-13T01:21:00Z")
            self.assertEqual(signal["lookahead"], "NO")
            self.assertEqual(signal["entry_rule"], "next_bar_open_after_signal_close")
            self.assertAlmostEqual(signal["entry_price_with_slippage"], signal["entry_open_price"] * 1.0005)

    def test_manual_target_diagnostics_marks_missing_setup(self):
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
                        "source_images": [
                            {"date_utc": "2026-05-14", "source_csv": str(tmp_path / "part-final.csv")}
                        ],
                        "entries": [_manual_entry(start, 81)],
                    }
                ),
                encoding="utf-8",
            )
            rows = [_row(start, idx) for idx in range(130)]

            with (
                patch(
                    "mlbotnav.visual_entry_reversal_bottom_knife_drop_runner._prepare_rows",
                    return_value=({}, rows),
                ),
                patch(
                    "mlbotnav.visual_entry_reversal_bottom_knife_drop_runner._enrich_quality_rows",
                    return_value=None,
                ),
                patch(
                    "mlbotnav.visual_entry_reversal_bottom_knife_drop_runner.render_family_candidate_overlay",
                    return_value=tmp_path / "overlay.png",
                ),
            ):
                payload = run_search(manual_entries, tmp_path, render_top=0)

            self.assertTrue(payload["manual_target_diagnostics"])
            best = payload["manual_target_diagnostics"][0]["best_family"]
            self.assertFalse(best["pass"])


if __name__ == "__main__":
    unittest.main()
