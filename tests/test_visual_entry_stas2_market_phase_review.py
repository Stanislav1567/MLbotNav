from __future__ import annotations

import pandas as pd

from mlbotnav.visual_entry_stas2_market_phase_review import _continuous_wave_rows, _day_time_ticks, _hour_phase_rows, _macro_wave_rows


def _market_frame(items: list[tuple[str, float, float, float, float]]) -> pd.DataFrame:
    rows = []
    for ts, open_price, high, low, close in items:
        rows.append(
            {
                "open_time_utc": pd.Timestamp(ts),
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": 1.0,
                "day_utc": pd.Timestamp(ts).strftime("%Y-%m-%d"),
            }
        )
    df = pd.DataFrame(rows)
    df["candle_range_pct"] = (df["high"] - df["low"]) / df["open"] * 100.0
    df["close_step_abs_pct"] = df["close"].pct_change().abs().fillna(0.0) * 100.0
    return df


def test_hour_phase_rows_adds_ordered_short_wave() -> None:
    df = _market_frame(
        [
            ("2026-05-04T00:00:00Z", 100.0, 100.0, 99.0, 99.5),
            ("2026-05-04T00:10:00Z", 99.5, 102.0, 101.0, 101.5),
            ("2026-05-04T00:20:00Z", 101.5, 101.0, 98.0, 98.5),
        ]
    )

    rows = _hour_phase_rows(df)

    assert len(rows) == 1
    row = rows[0]
    assert row["hour_short_wave_high_time_utc"] == "2026-05-04T00:10:00Z"
    assert row["hour_short_wave_post_high_low_time_utc"] == "2026-05-04T00:20:00Z"
    assert row["hour_short_wave_down_from_high_pct"] > 3.9
    assert row["hour_short_wave_rank"] >= 5
    assert row["hour_direction_bias"] == "SHORT_DOMINANT"


def test_day_time_ticks_include_next_midnight() -> None:
    ticks, labels = _day_time_ticks("2026-05-11")

    assert labels[0] == "00:00"
    assert labels[-1] == "00:00"
    assert labels[-2] == "22:00"
    assert ticks[-1] == pd.Timestamp("2026-05-12")


def test_macro_wave_rows_builds_variable_swing_blocks() -> None:
    df = _market_frame(
        [
            ("2026-05-04T00:00:00Z", 100.0, 100.2, 100.0, 100.1),
            ("2026-05-04T00:10:00Z", 100.1, 102.0, 101.0, 101.8),
            ("2026-05-04T00:20:00Z", 101.8, 101.0, 99.0, 99.4),
            ("2026-05-04T00:30:00Z", 99.4, 101.5, 99.5, 101.2),
        ]
    )

    rows = _macro_wave_rows(df, reversal_pct=1.0)
    wave_rows = [row for row in rows if row["macro_wave_segment_kind"] == "WAVE"]
    gap_rows = [row for row in rows if row["macro_wave_segment_kind"] == "GAP"]

    assert [row["macro_wave_direction"] for row in wave_rows] == ["LONG", "SHORT", "LONG"]
    assert wave_rows[0]["macro_wave_start_time_utc"] == "2026-05-04T00:00:00Z"
    assert wave_rows[0]["macro_wave_end_time_utc"] == "2026-05-04T00:10:00Z"
    assert wave_rows[1]["macro_wave_move_pct"] > 2.9
    assert wave_rows[-1]["macro_wave_is_last_leg"] is True
    assert wave_rows[-1]["macro_wave_boundary"] == "continuous_macro_wave_day_slice_hindsight_review_not_entry_feature"
    assert len(gap_rows) == 1
    assert gap_rows[0]["macro_wave_direction"] == "GAP"
    assert gap_rows[0]["macro_wave_move_basis"] == "gap_range_pct"


def test_continuous_wave_crosses_day_boundary_and_day_rows_are_slices() -> None:
    df = _market_frame(
        [
            ("2026-05-04T23:40:00Z", 99.1, 99.2, 99.0, 99.2),
            ("2026-05-04T23:50:00Z", 99.2, 100.0, 99.1, 99.8),
            ("2026-05-05T00:00:00Z", 99.8, 101.0, 99.7, 100.8),
            ("2026-05-05T00:10:00Z", 100.8, 102.5, 100.7, 102.0),
            ("2026-05-05T00:20:00Z", 102.0, 101.9, 99.0, 99.5),
        ]
    )

    continuous_rows = _continuous_wave_rows(df, reversal_pct=1.0)
    wave_rows = [row for row in continuous_rows if row["continuous_wave_segment_kind"] == "WAVE"]

    assert len(wave_rows) >= 1
    assert wave_rows[0]["continuous_wave_direction"] == "LONG"
    assert wave_rows[0]["continuous_wave_start_time_utc"] == "2026-05-04T23:40:00Z"
    assert wave_rows[0]["continuous_wave_end_time_utc"] == "2026-05-05T00:10:00Z"
    assert wave_rows[0]["continuous_wave_crossed_day_count"] == 2

    day_rows = _macro_wave_rows(df, reversal_pct=1.0, continuous_rows=continuous_rows)
    first_wave_id = wave_rows[0]["continuous_wave_id"]
    slices = [row for row in day_rows if row["continuous_wave_id"] == first_wave_id]

    assert [row["day_utc"] for row in slices] == ["2026-05-04", "2026-05-05"]
    assert slices[0]["macro_wave_carry_to_next_day"] is True
    assert slices[1]["macro_wave_carry_from_prev_day"] is True
    assert slices[0]["macro_wave_full_move_pct"] == slices[1]["macro_wave_full_move_pct"]
