import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from mlbotnav.visual_entry_hot_trend_false_suppression_runner import (
    HOT_TREND_SUPPRESSION_VARIANTS,
    _passes_hot_trend_suppression,
    _run_result,
    _strict_hot_trend_signals,
    run_search,
)


def _manual_entry(start: datetime, entry_idx: int, number: int) -> dict:
    signal_idx = entry_idx - 1
    return {
        "entry_id": f"ME_HTFS_{number}",
        "entry_number": number,
        "side": "long",
        "signal_candle_time_utc": (start + timedelta(minutes=signal_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "target_entry_time_utc": (start + timedelta(minutes=entry_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_open_price": 100.0,
        "entry_price_with_slippage": 100.05,
        "tolerance_bars_before": 0,
        "tolerance_bars_after": 0,
    }


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


def _signal(start: datetime, signal_idx: int, *, family_id: str = "SRC", **debug) -> dict:
    entry_idx = signal_idx + 1
    values = {
        "pullback_from_recent_high_20_pct": 0.25,
        "distance_to_event_low_pct": 0.30,
        "support_touch_count_60": 20.0,
        "lower_wick_share": 0.50,
        "close_pos_candle": 0.45,
        "mfi14": 45.0,
    }
    values.update(debug)
    return {
        "family_id": family_id,
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
        "strategy_scope": "entry_only_test",
        "lookahead": "NO",
        "cooldown_used": False,
        "future_trade_outcome_used": False,
        "context_votes": [],
        "trigger_votes": [],
        "confirm_votes": [],
        "suppress_votes": [],
        "debug": values,
    }


class VisualEntryHotTrendFalseSuppressionRunnerTests(unittest.TestCase):
    def test_strict_hot_filter_keeps_reclaim_and_suppresses_wide_shelf(self):
        start = datetime(2026, 5, 14, tzinfo=timezone.utc)
        variant = HOT_TREND_SUPPRESSION_VARIANTS[0]
        good = _signal(start, 70)
        bad = _signal(start, 80, support_touch_count_60=50.0)

        ok, suppress = _passes_hot_trend_suppression(good, variant)
        self.assertTrue(ok)
        self.assertEqual(suppress, [])

        ok_bad, suppress_bad = _passes_hot_trend_suppression(bad, variant)
        self.assertFalse(ok_bad)
        self.assertIn("SUPPORT_SHELF_TOO_WIDE", suppress_bad)

        kept = _strict_hot_trend_signals([bad, good], variant)
        self.assertEqual([item["entry_row_index"] for item in kept], [71])
        self.assertEqual(kept[0]["entry_rule"], "next_bar_open_after_signal_close")
        self.assertEqual(kept[0]["lookahead"], "NO")

    def test_run_search_keeps_entry_only_contract_and_no_ml(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            start = datetime(2026, 5, 14, tzinfo=timezone.utc)
            manual_entries = _manual_payload(tmp_path, start)
            base_signal = _signal(start, 70, family_id="BASE")
            hot_signal = _signal(start, 70, family_id="HOT")
            rows = [{"open_time_utc": start + timedelta(minutes=idx)} for idx in range(90)]

            with (
                patch("mlbotnav.visual_entry_hot_trend_false_suppression_runner._prepare_rows", return_value=({}, rows)),
                patch("mlbotnav.visual_entry_hot_trend_false_suppression_runner._enrich_quality_rows", return_value=None),
                patch("mlbotnav.visual_entry_hot_trend_false_suppression_runner._with_event_features", return_value=None),
                patch(
                    "mlbotnav.visual_entry_hot_trend_false_suppression_runner._build_olev20",
                    return_value=_run_result("BASE", "BASE", "base", [base_signal], []),
                ),
                patch("mlbotnav.visual_entry_hot_trend_false_suppression_runner._deep_recovery_signals", return_value=[]),
                patch("mlbotnav.visual_entry_hot_trend_false_suppression_runner._hot_trend_recall_signals", return_value=[hot_signal]),
                patch(
                    "mlbotnav.visual_entry_hot_trend_false_suppression_runner.render_family_candidate_overlay",
                    return_value=tmp_path / "overlay.png",
                ),
            ):
                payload = run_search(manual_entries, tmp_path, render_top=4)

            self.assertEqual(payload["status"], "DEV_HOT_TREND_FALSE_SUPPRESSION_V5_ENTRY_ONLY_NO_ML")
            self.assertTrue(payload["online_event_state_used"])
            self.assertFalse(payload["cooldown_used"])
            self.assertFalse(payload["future_trade_outcome_used"])
            self.assertFalse(payload["entry_candle_ohlcv_features_used"])
            self.assertFalse(payload["ml_transfer_allowed"])
            union = next(item for item in payload["best_overall"] if item["family_id"].startswith("HTFS20_UNION_"))
            self.assertEqual(union["signals"][0]["entry_rule"], "next_bar_open_after_signal_close")
            self.assertEqual(union["signals"][0]["lookahead"], "NO")


if __name__ == "__main__":
    unittest.main()
