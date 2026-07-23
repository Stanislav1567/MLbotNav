from __future__ import annotations

import pandas as pd

from mlbotnav.stas5_v2_numeric_coverage_audit import build_numeric_coverage_audit_from_frames


def test_numeric_coverage_maps_new_block_pattern_and_short_wave_features():
    snapshot = pd.DataFrame(
        [
            {
                "day": "2026-05-04",
                "candidate_id": "LA001",
                "human_label": "KEEP_DRAFT",
                "yellow_x": 1,
                "yellow_x_conflict": 1,
                "stas4_v2_block_density_structure_net_score": 1.0,
                "stas4_v2_pattern_strength": 3.0,
                "stas5_v2_short_wave_15m_down_from_high_pct": 0.42,
            }
        ]
    )
    feature_columns = [
        "session_time_bucket_code",
        "pre_15m_background_phase_rank",
        "pre_15m_long_wave_rank",
        "stas5_v2_short_wave_15m_down_from_high_pct",
        "stas4_v2_block_density_structure_net_score",
        "stas4_v2_pattern_strength",
        "stas4_v2_density_support_score",
        "stas4_v2_structure_support_score",
        "stas5_v2_risk_knife_pre_entry",
        "stas5_v2_gate_long_allowed_final",
        "stas4_v2_combo_rsi14",
    ]

    audit = build_numeric_coverage_audit_from_frames(
        snapshot=snapshot,
        feature_columns=feature_columns,
        day="2026-05-04",
    )

    by_block = {item["block"]: item for item in audit["block_coverage"]}
    assert by_block["STAS4 Audit: 4 выбранных блока"]["status"] == "FEATURE_READY_AS_NUMERIC_CONTEXT"
    assert by_block["Pattern / свечные конфликты"]["status"] == "FEATURE_READY"
    assert by_block["SHORT wave"]["status"] == "FEATURE_READY"
    assert audit["label_counts_for_day"]["keep_yellow_conflict"] == 1
