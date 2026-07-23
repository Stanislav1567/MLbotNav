from __future__ import annotations

import pandas as pd

from mlbotnav.stas5_v5c_bollinger_layer import (
    BOLLINGER_FEATURE_COLUMNS,
    attach_bollinger_features,
    bollinger_source_time_check,
)


def _ohlcv(rows: int = 80) -> pd.DataFrame:
    start = pd.Timestamp("2026-03-01T00:00:00Z")
    data = []
    price = 100.0
    for index in range(rows):
        price += 0.03 if index < 40 else -0.02
        data.append(
            {
                "open_time_utc": start + pd.Timedelta(minutes=index),
                "open": price,
                "high": price + 0.10,
                "low": price - 0.10,
                "close": price,
                "volume": 1000 + index,
            }
        )
    return pd.DataFrame(data)


def test_bollinger_features_use_only_closed_bars_before_entry() -> None:
    candidates = pd.DataFrame(
        [
            {
                "day": "2026-03-01",
                "candidate_id": "LA001",
                "record_id": "R1",
                "entry_time_utc": "2026-03-01T00:40:00Z",
                "entry_price_5bps": 101.2,
                "entry_y": 1,
            }
        ]
    )
    before, before_summary = attach_bollinger_features(candidates, _ohlcv())

    changed_future = _ohlcv()
    changed_future.loc[changed_future["open_time_utc"] >= pd.Timestamp("2026-03-01T00:40:00Z"), "close"] += 25.0
    changed_future.loc[changed_future["open_time_utc"] >= pd.Timestamp("2026-03-01T00:40:00Z"), "high"] += 25.0
    changed_future.loc[changed_future["open_time_utc"] >= pd.Timestamp("2026-03-01T00:40:00Z"), "low"] += 25.0
    after, after_summary = attach_bollinger_features(candidates, changed_future)

    assert before_summary["source_after_entry_rows"] == 0
    assert after_summary["source_after_entry_rows"] == 0
    assert before.loc[0, "bb_source_time_utc"] == "2026-03-01T00:39:00Z"
    assert after.loc[0, "bb_source_time_utc"] == "2026-03-01T00:39:00Z"
    for column in BOLLINGER_FEATURE_COLUMNS:
        assert before.loc[0, column] == after.loc[0, column]
    assert bollinger_source_time_check(before)["source_after_entry_rows"] == 0
