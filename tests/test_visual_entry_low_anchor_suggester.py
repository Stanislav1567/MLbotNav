from __future__ import annotations

import pandas as pd

from mlbotnav.visual_entry_low_anchor_suggester import _add_features, build_candidates


def _frame_with_delayed_confirmation_low() -> pd.DataFrame:
    start = pd.Timestamp("2026-05-02T00:00:00Z")
    rows = []
    for idx in range(45):
        open_px = 100.0
        close_px = 100.0
        low_px = 99.95
        high_px = 100.05
        volume = 1000.0

        if idx == 31:
            open_px = 100.0
            close_px = 99.92
            low_px = 99.40
            high_px = 100.03
            volume = 1800.0
        elif idx == 32:
            open_px = 99.94
            close_px = 99.96
            low_px = 99.70
            high_px = 100.00
            volume = 1200.0
        elif idx == 33:
            open_px = 99.98
            close_px = 100.25
            low_px = 99.92
            high_px = 100.30
            volume = 9000.0

        rows.append(
            {
                "open_time_utc": start + pd.Timedelta(minutes=idx),
                "close_time_utc": start + pd.Timedelta(minutes=idx + 1),
                "open": open_px,
                "high": high_px,
                "low": low_px,
                "close": close_px,
                "volume": volume,
            }
        )
    return pd.DataFrame(rows)


def test_build_candidates_entry_is_next_candle_after_anchor_low_even_if_confirmation_is_later() -> None:
    df = _add_features(_frame_with_delayed_confirmation_low())

    candidates = build_candidates(
        df,
        targets=[],
        anchor_lookback=5,
        max_anchor_age=3,
        cooldown_minutes=10,
        min_score=0.0,
        slippage_bps=5.0,
    )

    assert candidates, "expected at least one low-anchor candidate"
    delayed = [item for item in candidates if int(item.get("confirmation_idx", item["signal_idx"])) > int(item["signal_idx"])]
    assert delayed, "test fixture should produce a candidate confirmed after the anchor low"
    for item in delayed:
        assert int(item["signal_idx"]) == int(item["anchor_idx"])
        assert int(item["entry_idx"]) == int(item["anchor_idx"]) + 1
        assert int(item["execution_delay_bars_from_anchor"]) == 1
        assert pd.Timestamp(item["entry_time_utc"]) == pd.Timestamp(item["anchor_time_utc"]) + pd.Timedelta(minutes=1)
