from __future__ import annotations

import pandas as pd

from mlbotnav.visual_entry_stas3_v2_clean_review import _analyze_path, build_percent_ladder


def test_clean_v2_ladder_contract() -> None:
    ladder = build_percent_ladder()

    assert 0.2 not in ladder
    assert ladder[:8] == [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    assert ladder.count(2.0) == 1
    assert ladder[-1] == 20.0


def test_clean_v2_path_uses_entry_price_for_tp_and_drawdown() -> None:
    candles = pd.DataFrame(
        [
            {
                "open_time_utc": pd.Timestamp("2026-05-10T00:01:00Z"),
                "open": 100.0,
                "high": 100.2,
                "low": 99.7,
                "close": 100.1,
                "volume": 1.0,
            },
            {
                "open_time_utc": pd.Timestamp("2026-05-10T00:02:00Z"),
                "open": 100.1,
                "high": 101.1,
                "low": 99.8,
                "close": 101.0,
                "volume": 1.0,
            },
        ]
    )

    path, hit_map = _analyze_path(
        candles,
        pd.Timestamp("2026-05-10T00:01:00Z"),
        100.0,
        1.0,
        [0.3, 1.0],
    )

    assert path["path_status"] == "OK"
    assert hit_map[0.3]["hit"] is True
    assert hit_map[1.0]["hit"] is True
    assert hit_map[1.0]["target_price"] == 101.0
    assert round(hit_map[1.0]["drawdown_before_hit_pct"], 6) == 0.300903
