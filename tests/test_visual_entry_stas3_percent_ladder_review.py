from __future__ import annotations

import pandas as pd

from mlbotnav.visual_entry_stas3_percent_ladder_review import PERCENT_LADDER, compute_stas3_rows


def test_compute_stas3_rows_ladder_and_post_windows() -> None:
    base = pd.Timestamp("2026-05-02T00:00:00Z")
    market = pd.DataFrame(
        [
            {
                "open_time_utc": base + pd.Timedelta(minutes=i),
                "close_time_utc": base + pd.Timedelta(minutes=i + 1),
                "open": 100.0,
                "high": high,
                "low": low,
                "close": close,
                "volume": 1.0,
            }
            for i, (high, low, close) in enumerate(
                [
                    (100.2, 99.8, 100.0),
                    (100.4, 99.7, 100.3),
                    (100.7, 99.9, 100.5),
                    (101.1, 100.1, 101.0),
                    (101.4, 100.8, 101.2),
                ]
            )
        ]
    )
    rows = [
        {
            "source_run": "stas2_test",
            "record_id": "G1P_20260502_LA001",
            "candidate_id": "LA001",
            "day_utc": "2026-05-02",
            "anchor_time_utc": "2026-05-01T23:59:00Z",
            "entry_time_utc": "2026-05-02T00:00:00Z",
            "entry_open_price": "100.0",
            "entry_price_5bps": "100.0",
            "review_label": "GOOD",
            "entry_setup_quality_rank": "3",
            "entry_setup_quality_label": "CLEAN",
            "effective_session_label": "test",
        }
    ]

    out = compute_stas3_rows(rows, market, hold_hours=1.0)

    assert len(out) == 1
    row = out[0]
    assert 0.2 not in PERCENT_LADDER
    assert PERCENT_LADDER[:7] == [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    assert PERCENT_LADDER[7:18] == [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]
    assert PERCENT_LADDER[-1] == 20.0
    assert row["hit_0p3pct"] is True
    assert row["hit_1p0pct"] is True
    assert row["hit_1p2pct"] is True
    assert row["hit_1p4pct"] is True
    assert row["hit_1p5pct"] is False
    assert row["time_to_1p0pct_min"] == 3.0
    assert row["max_ladder_hit_pct"] == 1.4
    assert row["max_feasible_review_tp_pct"] == 1.4
    assert row["ideal_review_tp_pct"] == 1.4
    assert row["entry_price_for_calc"] == 100.0
    assert row["entry_price_source"] == "entry_price_5bps"
    assert row["direction_scope"] == "LONG_ONLY"
    assert row["long_only_flag"] is True
    assert row["short_context_only_flag"] is True
    assert row["post_5m_mfe_pct"] == 1.4
    assert row["post_5m_mae_pct"] == -0.3
    assert row["mfe_from_signal_pct"] == 1.4
    assert row["mfe_from_entry_pct"] == 1.4
    assert row["entry_to_mfe_min"] == 4.0
    assert row["mae_before_mfe_pct"] == -0.3
    assert row["mae_before_0p3pct_pct"] == -0.3
    assert row["mfe_after_0p3pct_pct"] == 1.4
    assert row["extra_after_0p3pct_pct"] == 1.1
    assert row["giveback_after_mfe_to_close_pct"] == 0.2
    assert row["stas3_verdict"] == "FAST_CLEAN_1PCT"


def test_compute_stas3_rows_requires_entry_price_5bps_and_joins_short_risk_context() -> None:
    base = pd.Timestamp("2026-05-10T00:00:00Z")
    market = pd.DataFrame(
        [
            {
                "open_time_utc": base + pd.Timedelta(minutes=i),
                "close_time_utc": base + pd.Timedelta(minutes=i + 1),
                "open": 100.0,
                "high": 100.8,
                "low": 99.9,
                "close": 100.5,
                "volume": 1.0,
            }
            for i in range(3)
        ]
    )
    rows = [
        {
            "source_run": "stas2_test",
            "record_id": "missing",
            "candidate_id": "MISSING",
            "day_utc": "2026-05-10",
            "anchor_time_utc": "2026-05-10T00:00:00Z",
            "entry_time_utc": "2026-05-10T00:00:00Z",
            "entry_open_price": "100.0",
            "entry_price_5bps": "",
        },
        {
            "source_run": "stas2_test",
            "record_id": "ok",
            "candidate_id": "OK",
            "day_utc": "2026-05-10",
            "anchor_time_utc": "2026-05-10T00:00:00Z",
            "anchor_low_price": "99.9",
            "entry_time_utc": "2026-05-10T00:00:00Z",
            "entry_open_price": "100.0",
            "entry_price_5bps": "100.05",
            "entry_setup_quality_rank": "1",
            "entry_setup_quality_label": "WARN",
        },
    ]
    context_tables = {
        "hourly": [
            {
                "hour_start_utc": "2026-05-10T00:00:00Z",
                "hour_background_phase": "Средняя",
                "hour_long_wave_phase": "Рабочая LONG-волна",
                "hour_long_wave_up_from_low_pct": "0.8",
                "hour_short_wave_phase": "Рабочая SHORT-волна",
                "hour_short_wave_down_from_high_pct": "1.2",
                "hour_direction_bias": "SHORT_DOMINANT",
            }
        ],
        "macro": [
            {
                "macro_wave_start_time_utc": "2026-05-10T00:00:00Z",
                "macro_wave_end_time_utc": "2026-05-10T01:00:00Z",
                "macro_wave_direction": "SHORT",
                "macro_wave_visible_move_pct": "1.5",
                "continuous_wave_id": "CW_TEST",
            }
        ],
        "continuous": [],
    }
    skipped: list[dict[str, str]] = []

    out = compute_stas3_rows(rows, market, hold_hours=1.0, skipped_rows=skipped, context_tables=context_tables)

    assert len(out) == 1
    assert skipped[0]["skip_reason"] == "missing_entry_price_5bps"
    row = out[0]
    assert row["entry_price_for_calc"] == 100.05
    assert row["short_context_only_flag"] is True
    assert row["hour_short_wave_down_from_high_pct"] == "1.2"
    assert row["macro_wave_direction"] == "SHORT"
    assert row["wave_context_scope"] == "HINDSIGHT_WAVE_REVIEW"
    assert "SHORT" in row["ideal_review_tp_warning"]
