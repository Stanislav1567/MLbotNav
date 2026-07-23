from __future__ import annotations

import pandas as pd
import pytest

from mlbotnav.stas5_v5c_riskgate_audit import _audit_dataframe, _day_user_pass_ids, riskgate_decision


BASE_ROW = {
    "candidate_id": "LA001",
    "entry_time_utc": "2026-03-18T11:32:00Z",
    "cs_max_source_time_utc": "2026-03-18T11:32:00Z",
    "fcs_max_source_time_utc": "2026-03-18T11:32:00Z",
}


def test_riskgate_blocks_active_dump_falling_knife() -> None:
    row = pd.Series(
        {
            **BASE_ROW,
            "candidate_id": "LA042",
            "fcs_regime_score_active_dump": 1.0,
            "cs_dump_acceleration_score": 1.0,
            "fcs_knife_risk_score": 1.0,
            "fcs_knife_acceleration_score": 1.0,
            "cs_short_pressure_now": 0.93,
            "fcs_regime_score_short_pressure": 0.95,
            "cs_price_breaking_recent_support": 1.0,
            "fcs_support_broken_recently": 1.0,
            "fcs_channel_breakdown_recent": 1.0,
        }
    )

    out = riskgate_decision(row)

    assert out["RISK_GATE_STATUS"] == "BLOCK_HARD"
    assert out["RISK_GATE_ACTION"] == "WOULD_BLOCK"
    assert out["RISK_GATE_REASON"] == "LIQUIDATION_CASCADE"
    assert out["RISK_GATE_PRIMARY_REGIME"] == "LIQUIDATION_CASCADE"
    assert out["RISK_MODE_LIQUIDATION_CASCADE_FLAG"] == 1
    assert out["RISK_NO_FUTURE_OK"] is True


def test_riskgate_user_pass_keeps_raw_block_status() -> None:
    row = pd.Series(
        {
            **BASE_ROW,
            "candidate_id": "LA078",
            "fcs_regime_score_active_dump": 1.0,
            "cs_dump_acceleration_score": 1.0,
            "fcs_knife_risk_score": 1.0,
            "fcs_knife_acceleration_score": 1.0,
            "cs_short_pressure_now": 0.72,
            "fcs_regime_score_short_pressure": 0.80,
            "cs_price_breaking_recent_support": 1.0,
            "fcs_channel_breakdown_recent": 1.0,
        }
    )

    out = riskgate_decision(row, user_pass_ids={"LA078"})

    assert out["RISK_GATE_RAW_STATUS"] == "BLOCK_HARD"
    assert out["RISK_GATE_RAW_PRIMARY_REGIME"] == "LIQUIDATION_CASCADE"
    assert "LIQUIDATION_CASCADE" in out["RISK_GATE_RAW_TAGS"]
    assert out["RISK_GATE_STATUS"] == "PASS_USER_REBOUND"
    assert out["RISK_GATE_PRIMARY_REGIME"] == "USER_APPROVED_REBOUND_EXCEPTION"
    assert out["RISK_GATE_ACTION"] == "KEEP_BY_USER_REVIEW"
    assert out["USER_VISUAL_VERDICT"] == "PASS"


def test_unqualified_user_pass_ids_are_single_day_only() -> None:
    assert _day_user_pass_ids({"LA059"}, day="2026-03-18", single_day=True) == {"LA059"}
    assert _day_user_pass_ids({"2026-03-18:LA059"}, day="2026-03-18", single_day=False) == {"LA059"}
    with pytest.raises(ValueError, match="single day"):
        _day_user_pass_ids({"LA059"}, day="2026-03-18", single_day=False)


@pytest.mark.parametrize(
    ("expected_regime", "fields"),
    [
        ("PRE_DUMP_RISK", {"cs_pre_dump_risk_score": 0.82}),
        ("ACTIVE_DUMP", {"fcs_regime_score_active_dump": 0.78}),
        ("FALLING_KNIFE", {"fcs_knife_risk_score": 0.84}),
        ("STRONG_SHORT_PRESSURE", {"cs_short_pressure_now": 0.82}),
        ("SHORT_CONTINUATION", {"cs_short_pressure_now": 0.75, "fcs_regime_score_active_dump": 0.66, "cs_consecutive_red_candles": 3}),
        (
            "PULLBACK_THEN_SHORT",
            {"cs_short_pressure_now": 0.82, "cs_pre_dump_risk_score": 0.76, "fcs_retest_after_knife_score": 0.78},
        ),
        ("SUPPORT_BREAKDOWN", {"cs_price_breaking_recent_support": 1.0}),
        ("CHANNEL_BREAKDOWN", {"fcs_channel_breakdown_recent": 1.0}),
        ("POST_PUMP_DUMP", {"fcs_post_pump_exhaustion_score": 0.76}),
        (
            "LIQUIDATION_CASCADE",
            {"fcs_regime_score_active_dump": 0.96, "fcs_knife_risk_score": 0.96, "cs_short_pressure_now": 0.80},
        ),
    ],
)
def test_riskgate_taxonomy_modes_have_explicit_primary_and_flag(expected_regime: str, fields: dict[str, float]) -> None:
    row = pd.Series({**BASE_ROW, **fields})

    out = riskgate_decision(row)

    assert out["RISK_GATE_PRIMARY_REGIME"] == expected_regime
    assert expected_regime in out["RISK_GATE_TAGS"]
    assert out[f"RISK_MODE_{expected_regime}_FLAG"] == 1


def test_riskgate_neutral_row_has_no_fatal_risk() -> None:
    out = riskgate_decision(pd.Series(BASE_ROW))

    assert out["RISK_GATE_STATUS"] == "PASS_RISK"
    assert out["RISK_GATE_PRIMARY_REGIME"] == "NO_FATAL_RISK"
    assert out["RISK_GATE_TAGS"] == "NO_FATAL_RISK"
    assert out["RISK_GATE_ACTIVE_MODE_COUNT"] == 0


def test_riskgate_audit_dataframe_does_not_change_entry_decision() -> None:
    predictions = pd.DataFrame([{**BASE_ROW, "day": "2026-03-18", "record_id": "r1", "ENTRY_ML_LIVE_DECISION": "ENTER", "ENTRY_ML_LIVE_SCORE": 0.9}])
    x439 = pd.DataFrame([{**BASE_ROW, "day": "2026-03-18", "record_id": "r1", "fcs_regime_score_active_dump": 1.0}])

    out = _audit_dataframe(predictions=predictions, x439=x439, day="2026-03-18", user_pass_ids=set())

    assert out.loc[0, "ENTRY_ALPHA_DECISION"] == "ENTER"
    assert out.loc[0, "ENTRY_FINAL_DECISION_AUDIT_ONLY"] == "ENTER"
    assert out.loc[0, "ENTRY_FINAL_REASON_AUDIT_ONLY"] == "audit_only_no_prediction_change"


def test_riskgate_source_time_guard_fails_on_future_source_time() -> None:
    row = pd.Series({**BASE_ROW, "cs_max_source_time_utc": "2026-03-18T11:33:00Z"})

    out = riskgate_decision(row)

    assert out["RISK_NO_FUTURE_OK"] is False
