from __future__ import annotations

import pandas as pd

from mlbotnav.stas5_v2_forward_error_ledger import build_forward_error_ledger_from_frames


def _v1_forward() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "day": "2026-05-15",
                "candidate_id": "LA001",
                "record_id": "STAS5F_20260515_LA001",
                "entry_time_utc": "2026-05-15T01:00:00Z",
                "entry_price_5bps": 100.0,
                "ML_DECISION": "ENTER",
                "ML_KEEP_SCORE": 0.81,
                "postfact_hit_0p5_pct": False,
                "postfact_hit_1p0_pct": False,
                "postfact_max_up_pct": 0.12,
                "postfact_max_drawdown_pct": -2.40,
                "postfact_usage": "audit_only",
            },
            {
                "day": "2026-05-15",
                "candidate_id": "LA002",
                "record_id": "STAS5F_20260515_LA002",
                "entry_time_utc": "2026-05-15T02:00:00Z",
                "entry_price_5bps": 99.0,
                "ML_DECISION": "SKIP",
                "ML_KEEP_SCORE": 0.31,
                "postfact_hit_0p5_pct": True,
                "postfact_hit_1p0_pct": True,
                "postfact_max_up_pct": 1.42,
                "postfact_max_drawdown_pct": -0.34,
                "postfact_usage": "audit_only",
            },
            {
                "day": "2026-05-15",
                "candidate_id": "LA003",
                "record_id": "STAS5F_20260515_LA003",
                "entry_time_utc": "2026-05-15T03:00:00Z",
                "entry_price_5bps": 98.0,
                "ML_DECISION": "UNSURE",
                "ML_KEEP_SCORE": 0.51,
                "postfact_hit_0p5_pct": False,
                "postfact_hit_1p0_pct": False,
                "postfact_max_up_pct": 0.20,
                "postfact_max_drawdown_pct": -0.60,
                "postfact_usage": "audit_only",
            },
        ]
    )


def _v2_forward() -> pd.DataFrame:
    base = {
        "feature_available_before_entry": True,
        "audit_no_trade_reason": "OK",
        "stas5_v2_risk_too_high_in_drop": 0,
        "stas5_v2_risk_weak_bounce_inside_drop": 0,
        "stas5_v2_risk_no_clear_low": 0,
        "stas5_v2_risk_after_spike": 0,
        "stas5_v2_risk_low_volume_confirmation": 0,
        "stas5_v2_risk_drawdown_proxy_score": 0.30,
        "stas5_v2_gate_long_allowed_final": 1,
        "stas5_v2_gate_bullish_evidence_score": 0.10,
        "stas5_v2_gate_no_trade_reason_code": 0,
        "stas4_v2_div_bullish_recent": 0,
        "stas4_v2_div_hidden_bullish_recent": 0,
        "stas4_v2_density_support_score": 1,
        "stas4_v2_structure_support_score": 1,
    }
    return pd.DataFrame(
        [
            {
                **base,
                "day": "2026-05-15",
                "candidate_id": "LA001",
                "record_id": "STAS5F_20260515_LA001",
                "entry_time_utc": "2026-05-15T01:00:00Z",
                "feature_time_utc": "2026-05-15T00:59:00Z",
                "stas5_v2_risk_knife_pre_entry": 0.64,
                "stas4_v2_combo_short_pressure_score": 0.90,
                "stas4_v2_combo_long_recovery_score": 0.00,
            },
            {
                **base,
                "day": "2026-05-15",
                "candidate_id": "LA002",
                "record_id": "STAS5F_20260515_LA002",
                "entry_time_utc": "2026-05-15T02:00:00Z",
                "feature_time_utc": "2026-05-15T01:59:00Z",
                "stas5_v2_risk_knife_pre_entry": 0.20,
                "stas4_v2_combo_short_pressure_score": 0.20,
                "stas4_v2_combo_long_recovery_score": 0.80,
            },
            {
                **base,
                "day": "2026-05-15",
                "candidate_id": "LA003",
                "record_id": "STAS5F_20260515_LA003",
                "entry_time_utc": "2026-05-15T03:00:00Z",
                "feature_time_utc": "2026-05-15T02:59:00Z",
                "stas5_v2_risk_knife_pre_entry": 0.22,
                "stas4_v2_combo_short_pressure_score": 0.30,
                "stas4_v2_combo_long_recovery_score": 0.70,
            },
        ]
    )


def test_forward_error_ledger_classifies_bad_green_and_missed_skip():
    ledger, manifest = build_forward_error_ledger_from_frames(
        forward_v1=_v1_forward(),
        v2_forward=_v2_forward(),
        user_review=pd.DataFrame(columns=["day", "candidate_id", "record_id", "user_review_label", "user_note", "risk_bucket"]),
    )

    assert manifest["status"] == "PASS"
    assert ledger.loc[0, "error_class"] == "GREEN_BAD_FALLING_KNIFE"
    assert ledger.loc[0, "v2_expected_decision"] == "SKIP"
    assert ledger.loc[1, "error_class"] == "SKIP_MISSED_GOOD"
    assert ledger.loc[1, "v2_expected_decision"] == "ENTER"


def test_forward_error_ledger_user_keep_turns_unsure_into_yellow_good():
    user_review = pd.DataFrame(
        [
            {
                "day": "2026-05-15",
                "candidate_id": "LA003",
                "record_id": "STAS5F_20260515_LA003",
                "user_review_label": "USER_KEEP_FORWARD_AUDIT",
                "user_note": "manual keep",
                "risk_bucket": "LOW_RISK",
            }
        ]
    )
    ledger, _manifest = build_forward_error_ledger_from_frames(
        forward_v1=_v1_forward(),
        v2_forward=_v2_forward(),
        user_review=user_review,
    )

    row = ledger[ledger["candidate_id"] == "LA003"].iloc[0]
    assert row["visual_user_review"] == "USER_KEEP_FORWARD_AUDIT"
    assert row["error_class"] == "YELLOW_GOOD"
    assert row["v2_expected_decision"] == "ENTER"


def test_forward_error_ledger_fails_manifest_when_v2_join_loses_row():
    v2_missing = _v2_forward()[lambda frame: frame["candidate_id"] != "LA002"]
    _ledger, manifest = build_forward_error_ledger_from_frames(
        forward_v1=_v1_forward(),
        v2_forward=v2_missing,
        user_review=None,
    )

    assert manifest["status"] == "FAIL"
    assert manifest["missing_v2_rows_after_join"] == 1
