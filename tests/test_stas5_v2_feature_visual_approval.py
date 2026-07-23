from __future__ import annotations

import pandas as pd

from mlbotnav.stas5_v2_feature_visual_approval import approval_bucket, risk_bucket, strategy_audit_counts, visual_marker_counts


def test_approval_bucket_keeps_yellow_conflict_separate() -> None:
    row = pd.Series({"human_label": "KEEP_DRAFT", "yellow_x": 1, "yellow_x_conflict": 1})
    assert approval_bucket(row) == "CONFLICT"


def test_approval_bucket_yellow_cut_is_audit_marker() -> None:
    row = pd.Series({"human_label": "CUT_DRAFT", "yellow_x": 1, "yellow_x_conflict": 0})
    assert approval_bucket(row) == "YELLOW_X"


def test_risk_bucket_blocks_long_allowed_zero() -> None:
    row = pd.Series(
        {
            "stas5_v2_gate_long_allowed_final": 0,
            "stas5_v2_risk_knife_pre_entry": 0.1,
            "stas4_v2_combo_short_pressure_score": 0.1,
        }
    )
    assert risk_bucket(row) == "BLOCKED"


def test_visual_marker_counts_draws_conflict_as_keep_plus_overlay() -> None:
    rows = pd.DataFrame(
        [
            {"human_label": "KEEP_DRAFT", "yellow_x": 1, "yellow_x_conflict": 1},
            {"human_label": "KEEP_DRAFT", "yellow_x": 0, "yellow_x_conflict": 0},
            {"human_label": "CUT_DRAFT", "yellow_x": 1, "yellow_x_conflict": 0},
        ]
    )

    assert visual_marker_counts(rows) == {
        "human_keep_green_markers": 2,
        "human_cut_red_markers": 1,
        "yellow_x_cut_overlay_markers": 1,
        "keep_yellow_conflict_cyan_overlay_markers": 1,
    }


def test_strategy_audit_counts_keeps_layers_audit_only() -> None:
    payload = [
        {
            "family": "density_profile+structure_ta",
            "label": "density+structure",
            "role": "main yellow-X audit",
            "old_removed": [{"candidate_id": "LA001"}, {"candidate_id": "LA002"}],
            "new_candidates": [{"candidate_id": "STAS4_DS_0100"}],
        }
    ]

    assert strategy_audit_counts(payload) == {
        "density_profile+structure_ta": {
            "label": "density+structure",
            "role": "main yellow-X audit",
            "old_removed": 2,
            "new_candidates": 1,
        }
    }
