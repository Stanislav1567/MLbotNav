from __future__ import annotations

from mlbotnav.stas5_leakage_guard import scan_forbidden_columns


def test_leakage_guard_flags_future_and_stas3_columns():
    matches = scan_forbidden_columns(
        [
            "pre_15m_range_pct",
            "future_return",
            "target_1pct_5bps",
            "stas3_tp_decision",
            "yellow_x",
        ]
    )

    assert "pre_15m_range_pct" not in matches
    assert "future_return" in matches
    assert "target_1pct_5bps" in matches
    assert "stas3_tp_decision" in matches
    assert "yellow_x" in matches


def test_leakage_guard_allows_causal_stas2_features():
    matches = scan_forbidden_columns(
        [
            "suggested_type",
            "score",
            "pre_30m_long_wave_rank",
            "session_so_far_range_pct",
            "entry_setup_quality_code",
            "context_before_entry_check",
        ]
    )

    assert matches == {}
