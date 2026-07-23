from __future__ import annotations

import pandas as pd

from mlbotnav.stas5_v2_forward_entry_review import render_v2_forward_day


def test_render_v2_forward_day_creates_png(tmp_path) -> None:
    times = pd.date_range("2026-05-15T00:00:00Z", periods=20, freq="min")
    day_df = pd.DataFrame(
        {
            "open_time_utc": times,
            "open": [100.0 + i * 0.02 for i in range(20)],
            "high": [100.1 + i * 0.02 for i in range(20)],
            "low": [99.9 + i * 0.02 for i in range(20)],
            "close": [100.02 + i * 0.02 for i in range(20)],
            "volume": [10.0 + i for i in range(20)],
        }
    )
    rows = pd.DataFrame(
        [
            {
                "day": "2026-05-15",
                "candidate_id": "LA001",
                "record_id": "R1",
                "entry_time_utc": "2026-05-15T00:03:00Z",
                "entry_price_5bps": 100.1,
                "ML_KEEP_SCORE_V2": 0.82,
                "ML_DECISION_V2": "ENTER",
                "stas5_v2_risk_knife_pre_entry": 0.2,
                "stas4_v2_combo_short_pressure_score": 0.2,
                "stas4_v2_block_density_structure_net_score": 2.0,
                "stas4_v2_block_pattern_structure_net_score": 1.0,
                "stas4_v2_block_structure_volume_net_score": 0.5,
                "stas4_v2_block_structure_trend_net_score": -0.5,
                "stas4_v2_structure_support_score": 1.0,
                "stas4_v2_structure_conflict_score": 0.0,
                "stas4_v2_density_support_score": 1.0,
                "stas4_v2_density_conflict_score": 0.0,
                "stas5_v2_gate_long_allowed_final": 1,
                "stas4_v2_combo_rsi14": 45.0,
                "stas4_v2_combo_rsi_signal": 40.0,
                "stas4_v2_combo_stoch_k14": 30.0,
                "stas4_v2_combo_macd_hist_norm": 0.1,
            }
        ]
    )
    out_path = tmp_path / "v2_forward.png"

    render_v2_forward_day(
        day_df=day_df,
        rows=rows,
        hour_rows=[],
        macro_wave_rows=[],
        day="2026-05-15",
        symbol="SOLUSDT",
        timeframe="1m",
        out_path=out_path,
    )

    assert out_path.exists()
    assert out_path.stat().st_size > 1024
