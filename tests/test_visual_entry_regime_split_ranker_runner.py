import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from mlbotnav.visual_entry_regime_split_ranker_runner import _select_online_no_rewrite, run_search


def _manual_entry(start: datetime, entry_idx: int, number: int) -> dict:
    signal_idx = entry_idx - 1
    return {
        "entry_id": f"ME_RSR_{number}",
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
            "support_touch_count_60": 18,
            "ret_6_pct": -0.08,
            "ret_12_pct": -0.38,
            "ret_24_pct": -0.60,
            "rsi14": 38.0,
            "stoch_k14": 34.0,
            "mfi14": 36.0,
            "lower_wick_share": 0.34,
            "close_pos_candle": 0.72,
            "vol_z20": 0.50,
            "ema20_slope_5_pct": -0.01,
        }
    )
    if regime == "hot":
        row.update({"ret_12_pct": 0.04, "ret_24_pct": 0.18, "rsi14": 64.0, "stoch_k14": 62.0, "mfi14": 58.0, "close_pos_candle": 0.86})
    elif regime == "trend":
        row.update({"ret_12_pct": -0.05, "ret_24_pct": 0.08, "rsi14": 62.0, "stoch_k14": 66.0, "mfi14": 64.0, "ema20_slope_5_pct": 0.02})
    elif regime == "structure":
        row.update({"ret_12_pct": -0.04, "ret_24_pct": -0.05, "rsi14": 72.0, "stoch_k14": 74.0, "mfi14": 52.0, "support_touch_count_60": 22, "vol_z20": 1.10})
    return row


class VisualEntryRegimeSplitRankerRunnerTests(unittest.TestCase):
    def test_regime_split_report_uses_next_open_and_no_ml(self):
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

            with (
                patch("mlbotnav.visual_entry_regime_split_ranker_runner._prepare_rows", return_value=({}, rows)),
                patch("mlbotnav.visual_entry_regime_split_ranker_runner._enrich_quality_rows", return_value=None),
                patch(
                    "mlbotnav.visual_entry_regime_split_ranker_runner.render_family_candidate_overlay",
                    return_value=tmp_path / "overlay.png",
                ),
            ):
                payload = run_search(manual_entries, tmp_path, render_top=4)

            self.assertEqual(payload["status"], "DEV_REGIME_SPLIT_RANKER_V1_ENTRY_ONLY_NO_ML")
            self.assertFalse(payload["cluster_selection_used"])
            self.assertTrue(payload["online_duplicate_suppression_used"])
            self.assertFalse(payload["cooldown_used"])
            self.assertFalse(payload["future_trade_outcome_used"])
            self.assertFalse(payload["ml_transfer_allowed"])
            self.assertEqual({item["regime"] for item in payload["regime_summary"]}, {
                "DEEP_CAPITULATION",
                "HOT_RECLAIM_SUPPORT",
                "TREND_DIP_CONTINUATION",
                "STRUCTURE_BOS_FIBO_VOLUME",
            })
            signal = payload["best_overall"][0]["signals"][0]
            self.assertEqual(signal["entry_row_index"], signal["signal_row_index"] + 1)
            self.assertEqual(signal["entry_rule"], "next_bar_open_after_signal_close")
            self.assertEqual(signal["lookahead"], "NO")

    def test_online_selection_does_not_rewrite_first_entry_with_future_low(self):
        candidates = [
            {"signal_row_index": 80, "entry_row_index": 81, "rank_score": 10.0},
            {"signal_row_index": 82, "entry_row_index": 83, "rank_score": 100.0},
            {"signal_row_index": 95, "entry_row_index": 96, "rank_score": 20.0},
        ]

        selected = _select_online_no_rewrite(candidates, min_gap_bars=8)

        self.assertEqual([item["signal_row_index"] for item in selected], [80, 95])
        self.assertEqual(selected[0]["online_selection_rule"], "first_qualified_no_future_rewrite")


if __name__ == "__main__":
    unittest.main()
