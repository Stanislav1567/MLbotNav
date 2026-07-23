import pandas as pd

from mlbotnav.stas5_v5c_safety_pulse_preview import (
    POLICY_DOWN_CHANNEL_NO_LONG,
    POLICY_HARD_BLOCK_ONLY,
    _balanced_safety_decision,
    build_safety_pulse_predictions,
)


def test_balanced_safety_blocks_and_demotes() -> None:
    assert (
        _balanced_safety_decision(
            pd.Series({"ENTRY_ML_LIVE_DECISION_BEFORE_RISKGATE": "ENTER", "RISK_GATE_ACTION": "WOULD_BLOCK"})
        )[0]
        == "SKIP"
    )
    assert (
        _balanced_safety_decision(
            pd.Series({"ENTRY_ML_LIVE_DECISION_BEFORE_RISKGATE": "ENTER", "RISK_GATE_ACTION": "WOULD_DEMOTE"})
        )[0]
        == "WATCH"
    )
    assert (
        _balanced_safety_decision(
            pd.Series(
                {
                    "ENTRY_ML_LIVE_DECISION_BEFORE_RISKGATE": "ENTER",
                    "RISK_GATE_ACTION": "KEEP",
                    "RISKGATE_ML_LIVE_DECISION": "BLOCK_RISK",
                }
            )
        )[0]
        == "WATCH"
    )


def test_hard_block_only_keeps_non_fatal_enter() -> None:
    assert (
        _balanced_safety_decision(
            pd.Series({"ENTRY_ML_LIVE_DECISION_BEFORE_RISKGATE": "ENTER", "RISK_GATE_ACTION": "WOULD_DEMOTE"}),
            policy=POLICY_HARD_BLOCK_ONLY,
        )[0]
        == "ENTER"
    )


def test_down_channel_no_long_blocks_bad_long_edge() -> None:
    row = pd.Series(
        {
            "ENTRY_ML_LIVE_DECISION_BEFORE_RISKGATE": "ENTER",
            "RISK_GATE_ACTION": "KEEP",
            "RISK_GATE_STATUS": "PASS_RISK",
            "cs_return_60m_pct": -0.8,
            "cs_return_120m_pct": -1.2,
            "cs_return_240m_pct": -2.1,
            "cs_range_60m_pct": 0.8,
            "cs_range_120m_pct": 1.1,
            "cs_lower_lows_count_30m": 16,
            "cs_lower_highs_count_30m": 15,
            "cs_short_pressure_now": 0.82,
            "cs_long_pressure_now": 0.25,
            "cs_dump_acceleration_score": 0.78,
            "cs_price_breaking_recent_support": 1.0,
            "cs_bounce_from_recent_low_pct": 0.2,
            "fcs_channel_slope_pct_per_min": -0.006,
            "fcs_channel_position_0_1": 0.08,
            "fcs_channel_breakdown_recent": 1.0,
        }
    )
    decision, action, reason = _balanced_safety_decision(row, policy=POLICY_DOWN_CHANNEL_NO_LONG)
    assert decision == "SKIP"
    assert action == "DOWN_CHANNEL_NO_LONG_BLOCK_TO_SKIP"
    assert reason == "DOWN_CHANNEL_NO_LONG"


def test_down_channel_no_long_keeps_grounded_rebound_exception() -> None:
    row = pd.Series(
        {
            "ENTRY_ML_LIVE_DECISION_BEFORE_RISKGATE": "ENTER",
            "RISK_GATE_ACTION": "KEEP",
            "RISK_GATE_STATUS": "PASS_RISK",
            "cs_return_60m_pct": -0.8,
            "cs_return_120m_pct": -1.2,
            "cs_return_240m_pct": -2.1,
            "cs_lower_lows_count_30m": 16,
            "cs_lower_highs_count_30m": 15,
            "cs_short_pressure_now": 0.60,
            "cs_long_pressure_now": 0.38,
            "cs_dump_acceleration_score": 0.55,
            "cs_bounce_from_recent_low_pct": 0.92,
            "cs_sell_pressure_exhaustion_score": 0.66,
            "fcs_channel_slope_pct_per_min": -0.006,
            "fcs_channel_position_0_1": 0.08,
            "fcs_channel_breakdown_recent": 1.0,
            "fcs_grounding_confirmed_score": 0.80,
            "fcs_retest_after_knife_score": 0.82,
            "fcs_knife_exhaustion_score": 0.70,
        }
    )
    decision, action, reason = _balanced_safety_decision(row, policy=POLICY_DOWN_CHANNEL_NO_LONG)
    assert decision == "ENTER"
    assert action == "KEEP_GOOD_REBOUND_EXCEPTION"
    assert reason == "GOOD_REBOUND_EXCEPTION"


def test_down_channel_no_long_does_not_reuse_old_taxonomy_hard_block() -> None:
    decision, action, reason = _balanced_safety_decision(
        pd.Series(
            {
                "ENTRY_ML_LIVE_DECISION_BEFORE_RISKGATE": "ENTER",
                "RISK_GATE_ACTION": "WOULD_BLOCK",
                "RISK_GATE_STATUS": "BLOCK_HARD",
            }
        ),
        policy=POLICY_DOWN_CHANNEL_NO_LONG,
    )
    assert decision == "ENTER"
    assert action == "KEEP_DOWN_CHANNEL_NO_LONG_CLEAN"
    assert reason == "NO_DOWN_CHANNEL_NO_LONG"


def test_preview_joins_x439_for_down_channel_policy() -> None:
    predictions = pd.DataFrame(
        [
            {
                "day": "2026-03-26",
                "candidate_id": "LA001",
                "record_id": "r1",
                "entry_time_utc": "2026-03-26T01:00:00Z",
                "ENTRY_ML_LIVE_DECISION_BEFORE_RISKGATE": "ENTER",
                "ENTRY_ML_LIVE_DECISION": "ENTER",
                "ENTRY_ML_LIVE_SCORE": 0.7,
            }
        ]
    )
    audit = pd.DataFrame(
        [
            {
                "day": "2026-03-26",
                "candidate_id": "LA001",
                "record_id": "r1",
                "entry_time_utc": "2026-03-26T01:00:00Z",
                "RISK_GATE_ACTION": "KEEP",
                "RISK_GATE_STATUS": "PASS_RISK",
                "RISK_NO_FUTURE_OK": True,
            }
        ]
    )
    x439 = pd.DataFrame(
        [
            {
                "day": "2026-03-26",
                "candidate_id": "LA001",
                "record_id": "r1",
                "entry_time_utc": "2026-03-26T01:00:00Z",
                "cs_return_60m_pct": -0.8,
                "cs_return_120m_pct": -1.2,
                "cs_return_240m_pct": -2.1,
                "cs_range_60m_pct": 0.8,
                "cs_range_120m_pct": 1.1,
                "cs_lower_lows_count_30m": 16,
                "cs_lower_highs_count_30m": 15,
                "cs_short_pressure_now": 0.82,
                "cs_long_pressure_now": 0.25,
                "cs_dump_acceleration_score": 0.78,
                "cs_price_breaking_recent_support": 1.0,
                "cs_bounce_from_recent_low_pct": 0.2,
                "fcs_channel_slope_pct_per_min": -0.006,
                "fcs_channel_position_0_1": 0.08,
                "fcs_channel_breakdown_recent": 1.0,
            }
        ]
    )
    out = build_safety_pulse_predictions(
        predictions=predictions,
        audit_rows=audit,
        x439_rows=x439,
        policy=POLICY_DOWN_CHANNEL_NO_LONG,
    )
    assert out.loc[0, "ENTRY_ML_LIVE_DECISION"] == "SKIP"
    assert out.loc[0, "DOWN_CHANNEL_NO_LONG_FLAG"] == 1
    assert "DESCENDING_CHANNEL" in out.loc[0, "DOWN_CHANNEL_NO_LONG_TAGS"]


def test_preview_preserves_original_final_decision() -> None:
    predictions = pd.DataFrame(
        [
            {
                "day": "2026-03-21",
                "candidate_id": "LA001",
                "record_id": "r1",
                "entry_time_utc": "2026-03-21T01:00:00Z",
                "ENTRY_ML_LIVE_DECISION_BEFORE_RISKGATE": "ENTER",
                "ENTRY_ML_LIVE_DECISION": "ENTER",
                "ENTRY_ML_LIVE_SCORE": 0.7,
            }
        ]
    )
    audit = pd.DataFrame(
        [
            {
                "day": "2026-03-21",
                "candidate_id": "LA001",
                "record_id": "r1",
                "entry_time_utc": "2026-03-21T01:00:00Z",
                "RISK_GATE_ACTION": "WOULD_BLOCK",
                "RISK_GATE_STATUS": "BLOCK_HARD",
                "RISK_NO_FUTURE_OK": True,
            }
        ]
    )
    out = build_safety_pulse_predictions(predictions=predictions, audit_rows=audit)
    assert out.loc[0, "ENTRY_ML_LIVE_DECISION_ORIGINAL_FINAL"] == "ENTER"
    assert out.loc[0, "ENTRY_ML_LIVE_DECISION"] == "SKIP"
    assert out.loc[0, "BALANCED_SAFETY_PULSE_ACTION"] == "TAXONOMY_BLOCK_TO_SKIP"
