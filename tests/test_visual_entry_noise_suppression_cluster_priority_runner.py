import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from mlbotnav.visual_entry_noise_suppression_cluster_priority_runner import run_search


def _row(start: datetime, idx: int, *, score_shape: str) -> dict:
    weak = score_shape == "weak"
    return {
        "open_time_utc": start + timedelta(minutes=idx),
        "open": 100.0 - idx * 0.01,
        "high": 100.05 - idx * 0.01,
        "low": 99.90 - idx * 0.01,
        "close": 99.98 - idx * 0.01,
        "range_pos_60": 0.05,
        "low_range_pos_60": 0.03,
        "local_low_5": True,
        "local_low_20": True,
        "support_touch_count_60": 3,
        "ret_6_pct": -0.20,
        "ret_12_pct": -0.40,
        "ret_24_pct": -0.60,
        "rsi14": 35.0,
        "stoch_k14": 30.0,
        "mfi14": 40.0,
        "lower_wick_share": 0.05 if weak else 0.30,
        "close_pos_candle": 0.05 if weak else 0.45,
        "vol_z20": 0.1 if weak else 1.2,
        "lower_low_streak_5": 5 if weak else 2,
        "new_low_count_20": 14 if weak else 5,
        "ema20_slope_5_pct": -0.30 if weak else -0.05,
    }


class VisualEntryNoiseSuppressionClusterPriorityRunnerTests(unittest.TestCase):
    def test_runner_creates_reports_and_overlay(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            start = datetime(2026, 5, 12, tzinfo=timezone.utc)
            manual_entries = tmp_path / "manual_entries.json"
            manual_entries.write_text(
                json.dumps(
                    {
                        "symbol": "SOLUSDT",
                        "timeframe": "1m",
                        "source_images": [
                            {"date_utc": "2026-05-12", "source_csv": str(tmp_path / "part-final.csv")}
                        ],
                        "entries": [
                            {
                                "entry_id": "ME_1",
                                "entry_number": 1,
                                "side": "long",
                                "signal_candle_time_utc": (start + timedelta(minutes=86)).strftime(
                                    "%Y-%m-%dT%H:%M:%SZ"
                                ),
                                "target_entry_time_utc": (start + timedelta(minutes=87)).strftime(
                                    "%Y-%m-%dT%H:%M:%SZ"
                                ),
                                "entry_open_price": 99.13,
                                "entry_price_with_slippage": 99.179565,
                                "tolerance_bars_before": 0,
                                "tolerance_bars_after": 0,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            rows = [_row(start, idx, score_shape="strong") for idx in range(120)]
            signals = [
                _signal(start, 80),
                _signal(start, 83),
                _signal(start, 86),
            ]
            source_payload = {
                "status": "DEV_DEEP_CAPITULATION_RECLAIM_DIAGNOSTIC_NO_ML",
                "json_path": str(tmp_path / "source.json"),
                "best_overall": [
                    {
                        "family_id": "DQ01_EQ01_PLUS_DEEP_RECLAIM",
                        "signals": signals,
                        "score": {},
                    }
                ],
            }

            def fake_render(**kwargs):
                png_path = tmp_path / "overlay.png"
                png_path.write_bytes(b"png")
                return png_path

            with (
                patch(
                    "mlbotnav.visual_entry_noise_suppression_cluster_priority_runner._prepare_rows",
                    return_value=({}, rows),
                ),
                patch(
                    "mlbotnav.visual_entry_noise_suppression_cluster_priority_runner._enrich_quality_rows",
                    return_value=None,
                ),
                patch(
                    "mlbotnav.visual_entry_noise_suppression_cluster_priority_runner._run_deep_search",
                    return_value=source_payload,
                ),
                patch(
                    "mlbotnav.visual_entry_noise_suppression_cluster_priority_runner.render_family_candidate_overlay",
                    side_effect=fake_render,
                ),
            ):
                payload = run_search(manual_entries, tmp_path, render_top=1)

            self.assertEqual(payload["status"], "DEV_NOISE_SUPPRESSION_CLUSTER_PRIORITY_DIAGNOSTIC_NO_ML")
            self.assertFalse(payload["ml_transfer_allowed"])
            self.assertTrue((tmp_path / "visual_entry_noise_suppression_cluster_priority_20260512_DEV.json").exists())
            self.assertTrue((tmp_path / "visual_entry_noise_suppression_cluster_priority_20260512_DEV_RU.md").exists())
            self.assertTrue(payload["rendered_overlays"])
            self.assertTrue(Path(payload["rendered_overlays"][0]["visual_png"]).exists())

    def test_cluster_priority_keeps_one_entry_per_cluster(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            start = datetime(2026, 5, 12, tzinfo=timezone.utc)
            manual_entries = tmp_path / "manual_entries.json"
            manual_entries.write_text(
                json.dumps(
                    {
                        "symbol": "SOLUSDT",
                        "timeframe": "1m",
                        "source_images": [{"date_utc": "2026-05-12", "source_csv": "synthetic.csv"}],
                        "entries": [
                            {
                                "entry_id": "ME_1",
                                "entry_number": 1,
                                "side": "long",
                                "signal_candle_time_utc": (start + timedelta(minutes=86)).strftime(
                                    "%Y-%m-%dT%H:%M:%SZ"
                                ),
                                "target_entry_time_utc": (start + timedelta(minutes=87)).strftime(
                                    "%Y-%m-%dT%H:%M:%SZ"
                                ),
                                "entry_open_price": 99.13,
                                "entry_price_with_slippage": 99.179565,
                                "tolerance_bars_before": 0,
                                "tolerance_bars_after": 0,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            rows = [_row(start, idx, score_shape="strong") for idx in range(120)]
            rows[80] = _row(start, 80, score_shape="weak")
            rows[83] = _row(start, 83, score_shape="weak")
            rows[86] = _row(start, 86, score_shape="strong")
            source_payload = {
                "status": "DEV_DEEP_CAPITULATION_RECLAIM_DIAGNOSTIC_NO_ML",
                "json_path": str(tmp_path / "source.json"),
                "best_overall": [
                    {
                        "family_id": "DQ01_EQ01_PLUS_DEEP_RECLAIM",
                        "signals": [_signal(start, 80), _signal(start, 83), _signal(start, 86)],
                        "score": {},
                    }
                ],
            }

            with (
                patch(
                    "mlbotnav.visual_entry_noise_suppression_cluster_priority_runner._prepare_rows",
                    return_value=({}, rows),
                ),
                patch(
                    "mlbotnav.visual_entry_noise_suppression_cluster_priority_runner._enrich_quality_rows",
                    return_value=None,
                ),
                patch(
                    "mlbotnav.visual_entry_noise_suppression_cluster_priority_runner._run_deep_search",
                    return_value=source_payload,
                ),
                patch(
                    "mlbotnav.visual_entry_noise_suppression_cluster_priority_runner.render_family_candidate_overlay",
                    return_value=tmp_path / "overlay.png",
                ),
            ):
                payload = run_search(manual_entries, tmp_path, render_top=0)

            top = payload["best_overall"][0]
            self.assertEqual(top["signals"][0]["entry_time_utc"], "2026-05-12T01:27:00Z")
            self.assertEqual(top["signals"][0]["lookahead"], "NO")
            self.assertEqual(top["signals"][0]["entry_rule"], "next_bar_open_after_signal_close")
            self.assertAlmostEqual(
                top["signals"][0]["entry_price_with_slippage"],
                top["signals"][0]["entry_open_price"] * 1.0005,
            )
            self.assertEqual(top["clusters_total"], 1)
            self.assertEqual(top["score"]["target_hits"], 1)
            self.assertEqual(top["score"]["false_entries"], 0)

    def test_recovery_variant_adds_nowick_and_late_retest_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            start = datetime(2026, 5, 12, tzinfo=timezone.utc)
            manual_entries = tmp_path / "manual_entries.json"
            manual_entries.write_text(
                json.dumps(
                    {
                        "symbol": "SOLUSDT",
                        "timeframe": "1m",
                        "source_images": [{"date_utc": "2026-05-12", "source_csv": "synthetic.csv"}],
                        "entries": [
                            _manual_entry(start, 31, "ME_BASE"),
                            _manual_entry(start, 50, "ME_NOWICK"),
                            _manual_entry(start, 100, "ME_LATE"),
                        ],
                    }
                ),
                encoding="utf-8",
            )
            rows = [_row(start, idx, score_shape="strong") for idx in range(130)]
            rows[49].update(
                {
                    "range_pos_60": 0.24,
                    "low_range_pos_60": 0.24,
                    "local_low_5": True,
                    "local_low_20": False,
                    "support_touch_count_60": 12,
                    "ret_6_pct": 0.02,
                    "ret_12_pct": -0.02,
                    "ret_24_pct": -0.39,
                    "rsi14": 43.0,
                    "stoch_k14": 45.0,
                    "mfi14": 24.0,
                    "lower_wick_share": 0.0,
                    "close_pos_candle": 0.0,
                    "vol_z20": -0.2,
                    "lower_low_streak_5": 2,
                    "new_low_count_20": 7,
                    "ema_gap_pct": -0.14,
                }
            )
            rows[99].update(
                {
                    "range_pos_60": 0.32,
                    "low_range_pos_60": 0.32,
                    "local_low_5": False,
                    "local_low_20": False,
                    "support_touch_count_60": 9,
                    "ret_6_pct": 0.12,
                    "ret_24_pct": -0.29,
                    "rsi14": 45.0,
                    "mfi14": 30.0,
                    "dist_from_low_60_pct": 0.25,
                    "lower_wick_share": 0.0,
                    "close_pos_candle": 0.0,
                    "ema_gap_pct": -0.10,
                    "ema20_slope_5_pct": 0.005,
                }
            )
            source_payload = {
                "status": "DEV_DEEP_CAPITULATION_RECLAIM_DIAGNOSTIC_NO_ML",
                "json_path": str(tmp_path / "source.json"),
                "best_overall": [
                    {
                        "family_id": "DQ01_EQ01_PLUS_DEEP_RECLAIM",
                        "signals": [
                            _signal(start, 30),
                            {
                                **_signal(start, 99),
                                "trigger_votes": ["D03_LATE_RETEST_PROBE_CD15"],
                                "context_votes": ["RECENT_DEEP_CAPITULATION_93B"],
                            },
                        ],
                        "score": {},
                    },
                    {
                        "family_id": "DQ03_EQ03_HIGH_RECALL_PLUS_DEEP",
                        "signals": [
                            {
                                **_signal(start, 49),
                                "trigger_votes": ["E05_NO_WICK_LOW_CLOSE_CD15"],
                                "context_votes": ["NO_RECLAIM_CLOSE_LOW"],
                            }
                        ],
                        "score": {},
                    },
                ],
            }

            with (
                patch(
                    "mlbotnav.visual_entry_noise_suppression_cluster_priority_runner._prepare_rows",
                    return_value=({}, rows),
                ),
                patch(
                    "mlbotnav.visual_entry_noise_suppression_cluster_priority_runner._enrich_quality_rows",
                    return_value=None,
                ),
                patch(
                    "mlbotnav.visual_entry_noise_suppression_cluster_priority_runner._run_deep_search",
                    return_value=source_payload,
                ),
                patch(
                    "mlbotnav.visual_entry_noise_suppression_cluster_priority_runner.render_family_candidate_overlay",
                    return_value=tmp_path / "overlay.png",
                ),
            ):
                payload = run_search(manual_entries, tmp_path, render_top=0)

            top = payload["best_overall"][0]
            self.assertEqual(top["family_id"], "CP06_CP01_RECOVER_NOWICK_LATE_RETEST")
            self.assertEqual(top["score"]["target_hits"], 3)
            self.assertEqual(top["score"]["false_entries"], 0)
            self.assertEqual(
                [item["entry_time_utc"] for item in top["recovered_entries"]],
                ["2026-05-12T00:50:00Z", "2026-05-12T01:40:00Z"],
            )


def _signal(start: datetime, signal_idx: int) -> dict:
    entry_idx = signal_idx + 1
    return {
        "family_id": "DQ01_EQ01_PLUS_DEEP_RECLAIM",
        "source_family_id": "DQ01_EQ01_PLUS_DEEP_RECLAIM",
        "side": "long",
        "signal_row_index": signal_idx,
        "entry_row_index": entry_idx,
        "signal_time_utc": (start + timedelta(minutes=signal_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_time_utc": (start + timedelta(minutes=entry_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_open_price": 100.0,
        "entry_price_with_slippage": 100.05,
        "slippage_bps": 5.0,
        "context_votes": [],
        "trigger_votes": [],
        "confirm_votes": [],
        "lookahead": "NO",
        "entry_rule": "next_bar_open_after_signal_close",
    }


def _manual_entry(start: datetime, entry_idx: int, entry_id: str) -> dict:
    signal_idx = entry_idx - 1
    return {
        "entry_id": entry_id,
        "entry_number": entry_idx,
        "side": "long",
        "signal_candle_time_utc": (start + timedelta(minutes=signal_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "target_entry_time_utc": (start + timedelta(minutes=entry_idx)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "entry_open_price": 100.0,
        "entry_price_with_slippage": 100.05,
        "tolerance_bars_before": 0,
        "tolerance_bars_after": 0,
    }


if __name__ == "__main__":
    unittest.main()
