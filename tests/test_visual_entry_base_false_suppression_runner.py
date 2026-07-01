import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from mlbotnav.visual_entry_base_false_suppression_runner import (
    BASE_SUPPRESSION_VARIANTS,
    _filter_base_signals,
    _passes_base_suppression,
    run_search,
)
from mlbotnav.visual_entry_deep_recovery_hot_recall_runner import _run_result


def _manual_entry(start: datetime, entry_idx: int, number: int) -> dict:
    signal_idx = entry_idx - 1
    return {
        "entry_id": f"ME_BFS_{number}",
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


def _signal(start: datetime, signal_idx: int, *, source: str, **debug) -> dict:
    entry_idx = signal_idx + 1
    values = {
        "low_zone": 0.34,
        "support_touch_count_60": 21.0,
        "distance_to_event_low_pct": 0.06,
        "pullback_from_recent_high_20_pct": 0.24,
        "ret_12_pct": -0.14,
        "ret_24_pct": -0.08,
        "rsi14": 44.0,
        "stoch_k14": 48.0,
        "mfi14": 22.0,
        "lower_wick_share": 0.33,
        "close_pos_candle": 0.78,
        "new_low_count_20": 7.0,
        "lower_low_streak_5": 0.0,
    }
    values.update(debug)
    return {
        "family_id": "BASE",
        "source_family_id": source,
        "bucket": "BASE",
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


class VisualEntryBaseFalseSuppressionRunnerTests(unittest.TestCase):
    def test_source_split_keeps_event_reclaim_and_suppresses_lower_low_chain(self):
        start = datetime(2026, 5, 14, tzinfo=timezone.utc)
        variant = BASE_SUPPRESSION_VARIANTS[0]
        good = _signal(start, 70, source="DRHR00_BASE_OLEV20_EVENT_QUALITY")
        bad = _signal(start, 80, source="DRHR00_BASE_OLEV20_EVENT_QUALITY", lower_low_streak_5=2.0)

        ok, suppress = _passes_base_suppression(good, variant)
        self.assertTrue(ok)
        self.assertEqual(suppress, [])

        ok_bad, suppress_bad = _passes_base_suppression(bad, variant)
        self.assertFalse(ok_bad)
        self.assertIn("EVENT_LOWER_LOW_STREAK_ACTIVE", suppress_bad)

        kept = _filter_base_signals([bad, good], variant)
        self.assertEqual([item["entry_row_index"] for item in kept], [71])
        self.assertEqual(kept[0]["entry_rule"], "next_bar_open_after_signal_close")
        self.assertEqual(kept[0]["lookahead"], "NO")

    def test_deep_late_retest_requires_mature_drop(self):
        start = datetime(2026, 5, 14, tzinfo=timezone.utc)
        variant = BASE_SUPPRESSION_VARIANTS[0]
        mature = _signal(
            start,
            70,
            source="BFS00_DEEP_RECOVERY_SOURCE",
            distance_to_event_low_pct=0.50,
            ret_24_pct=-0.95,
            lower_low_streak_5=0.0,
            new_low_count_20=12.0,
            rsi14=20.0,
        )
        immature = _signal(
            start,
            80,
            source="BFS00_DEEP_RECOVERY_SOURCE",
            distance_to_event_low_pct=0.47,
            ret_24_pct=-0.39,
            lower_low_streak_5=2.0,
            new_low_count_20=12.0,
            rsi14=23.0,
        )

        self.assertTrue(_passes_base_suppression(mature, variant)[0])
        self.assertFalse(_passes_base_suppression(immature, variant)[0])

    def test_run_search_keeps_no_ml_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            start = datetime(2026, 5, 14, tzinfo=timezone.utc)
            manual_entries = _manual_payload(tmp_path, start)
            event_signal = _signal(start, 70, source="DRHR00_BASE_OLEV20_EVENT_QUALITY")
            hot_signal = _signal(start, 82, source="HTFS01_HOT_TREND_STRICT_FALSE_SUPPRESSION")
            rows = [{"open_time_utc": start + timedelta(minutes=idx)} for idx in range(100)]

            with (
                patch("mlbotnav.visual_entry_base_false_suppression_runner._prepare_rows", return_value=({}, rows)),
                patch("mlbotnav.visual_entry_base_false_suppression_runner._enrich_quality_rows", return_value=None),
                patch("mlbotnav.visual_entry_base_false_suppression_runner._with_event_features", return_value=None),
                patch(
                    "mlbotnav.visual_entry_base_false_suppression_runner._build_olev20",
                    return_value=_run_result("EVENT", "EVENT", "event", [event_signal], []),
                ),
                patch("mlbotnav.visual_entry_base_false_suppression_runner._deep_recovery_signals", return_value=[]),
                patch("mlbotnav.visual_entry_base_false_suppression_runner._hot_trend_recall_signals", return_value=[hot_signal]),
                patch(
                    "mlbotnav.visual_entry_base_false_suppression_runner.render_family_candidate_overlay",
                    return_value=tmp_path / "overlay.png",
                ),
            ):
                payload = run_search(manual_entries, tmp_path, render_top=4)

            self.assertEqual(payload["status"], "DEV_BASE_FALSE_SUPPRESSION_V6_ENTRY_ONLY_NO_ML")
            self.assertTrue(payload["online_event_state_used"])
            self.assertFalse(payload["cooldown_used"])
            self.assertFalse(payload["future_trade_outcome_used"])
            self.assertFalse(payload["entry_candle_ohlcv_features_used"])
            self.assertFalse(payload["ml_transfer_allowed"])
            union = next(item for item in payload["best_overall"] if item["family_id"].startswith("BFS20_UNION_"))
            self.assertEqual(union["signals"][0]["entry_rule"], "next_bar_open_after_signal_close")
            self.assertEqual(union["signals"][0]["lookahead"], "NO")


if __name__ == "__main__":
    unittest.main()
