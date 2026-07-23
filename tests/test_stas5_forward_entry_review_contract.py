from __future__ import annotations

import pandas as pd

from mlbotnav.stas5_common import score_to_decision
from mlbotnav.stas5_forward_entry_review import render_forward_day


def test_score_to_decision_contract():
    assert score_to_decision(0.80, enter_threshold=0.65, unsure_threshold=0.45) == "ENTER"
    assert score_to_decision(0.50, enter_threshold=0.65, unsure_threshold=0.45) == "UNSURE"
    assert score_to_decision(0.20, enter_threshold=0.65, unsure_threshold=0.45) == "SKIP"


def test_render_forward_day_creates_png_with_ml_statuses(tmp_path):
    times = pd.date_range("2026-05-15T00:00:00Z", periods=12, freq="min")
    day_df = pd.DataFrame(
        {
            "open_time_utc": times,
            "open": [100.0 + i * 0.02 for i in range(12)],
            "high": [100.1 + i * 0.02 for i in range(12)],
            "low": [99.9 + i * 0.02 for i in range(12)],
            "close": [100.02 + i * 0.02 for i in range(12)],
            "volume": [10.0 + i for i in range(12)],
        }
    )
    rows = pd.DataFrame(
        [
            {
                "day": "2026-05-15",
                "candidate_id": "LA001",
                "record_id": "STAS5F_20260515_LA001",
                "entry_time_utc": "2026-05-15T00:02:00Z",
                "entry_open_price": 100.04,
                "ML_KEEP_SCORE": 0.80,
                "ML_DECISION": "ENTER",
            },
            {
                "day": "2026-05-15",
                "candidate_id": "LA002",
                "record_id": "STAS5F_20260515_LA002",
                "entry_time_utc": "2026-05-15T00:05:00Z",
                "entry_open_price": 100.10,
                "ML_KEEP_SCORE": 0.52,
                "ML_DECISION": "UNSURE",
            },
            {
                "day": "2026-05-15",
                "candidate_id": "LA003",
                "record_id": "STAS5F_20260515_LA003",
                "entry_time_utc": "2026-05-15T00:08:00Z",
                "entry_open_price": 100.16,
                "ML_KEEP_SCORE": 0.20,
                "ML_DECISION": "SKIP",
            },
        ]
    )
    assert set(rows["ML_DECISION"]) == {"ENTER", "UNSURE", "SKIP"}

    out_path = tmp_path / "forward.png"
    render_forward_day(day_df=day_df, rows=rows, day="2026-05-15", symbol="SOLUSDT", timeframe="1m", out_path=out_path)

    assert out_path.exists()
    assert out_path.stat().st_size > 1024
