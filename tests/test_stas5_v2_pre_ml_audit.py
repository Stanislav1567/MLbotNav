from __future__ import annotations

import pandas as pd

from mlbotnav.stas5_v2_pre_ml_audit import run_v2_pre_ml_audit_from_frames


def _snapshot() -> pd.DataFrame:
    rows = []
    for idx in range(8):
        keep = idx < 3
        rows.append(
            {
                "day": "2026-05-01",
                "candidate_id": f"LA{idx:03d}",
                "record_id": f"R{idx}",
                "human_label": "KEEP_DRAFT" if keep else "CUT_DRAFT",
                "yellow_x": 1 if keep and idx == 0 else 0,
                "suggested_type": "A" if keep else "B",
                "stas5_v2_risk_knife_pre_entry": 0.10 if keep else 0.80,
                "stas4_v2_combo_long_recovery_score": 0.90 if keep else 0.10,
                "stas5_v2_gate_long_allowed_final": 1 if keep else 0,
            }
        )
    return pd.DataFrame(rows)


def _forward_errors() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "error_class": "GREEN_BAD_FALLING_KNIFE",
                "v2_expected_decision": "SKIP",
                "ML_DECISION_V1": "ENTER",
                "ML_KEEP_SCORE_V1": 0.90,
                "postfact_max_up_pct": 0.20,
                "postfact_max_drawdown_pct": -2.0,
                "stas5_v2_risk_knife_pre_entry": 0.70,
                "stas4_v2_combo_short_pressure_score": 0.90,
                "stas4_v2_combo_long_recovery_score": 0.00,
                "risk_primary_reason": "FALLING_KNIFE",
            },
            {
                "error_class": "GREEN_GOOD",
                "v2_expected_decision": "ENTER",
                "ML_DECISION_V1": "ENTER",
                "ML_KEEP_SCORE_V1": 0.75,
                "postfact_max_up_pct": 1.20,
                "postfact_max_drawdown_pct": -0.2,
                "stas5_v2_risk_knife_pre_entry": 0.20,
                "stas4_v2_combo_short_pressure_score": 0.20,
                "stas4_v2_combo_long_recovery_score": 0.80,
                "risk_primary_reason": "OK",
            },
        ]
    )


def test_v2_pre_ml_audit_ranks_numeric_features_and_summarizes_forward_errors():
    summary = run_v2_pre_ml_audit_from_frames(
        snapshot=_snapshot(),
        feature_columns=[
            "suggested_type",
            "stas5_v2_risk_knife_pre_entry",
            "stas4_v2_combo_long_recovery_score",
            "stas5_v2_gate_long_allowed_final",
        ],
        guard_report={"status": "PASS"},
        forward_error_ledger=_forward_errors(),
        forward_error_manifest={"status": "PASS", "rows": 2},
    )

    assert summary["status"] == "NOT_READY"
    assert summary["forward_error_summary"]["error_class_counts"]["GREEN_BAD_FALLING_KNIFE"] == 1
    assert summary["top_numeric_features"][0]["abs_effect"] > 0
    assert any(row["group"] == "v2_risk" for row in summary["feature_group_summary"])


def test_v2_pre_ml_audit_can_be_ready_when_real_counts_match():
    snapshot = _snapshot()
    # Expand labels to the real required counts without changing the checked feature logic.
    keep_rows = [snapshot.iloc[[0]].assign(record_id=f"K{i}", candidate_id=f"LK{i:03d}") for i in range(115)]
    cut_rows = [snapshot.iloc[[4]].assign(record_id=f"C{i}", candidate_id=f"LC{i:03d}", yellow_x=0) for i in range(857)]
    real_like = pd.concat(keep_rows + cut_rows, ignore_index=True)
    real_like["yellow_x"] = 0
    real_like.loc[:29, "yellow_x"] = 1

    summary = run_v2_pre_ml_audit_from_frames(
        snapshot=real_like,
        feature_columns=["stas5_v2_risk_knife_pre_entry", "stas4_v2_combo_long_recovery_score"],
        guard_report={"status": "PASS"},
        forward_error_ledger=_forward_errors(),
        forward_error_manifest={"status": "PASS", "rows": 2},
    )

    assert summary["status"] == "READY_FOR_V2_ABLATION_BASELINE"
    assert summary["keep_yellow_x_rows"] == 30
    assert summary["label_counts"]["KEEP_DRAFT"] == 115
    assert summary["label_counts"]["CUT_DRAFT"] == 857


def test_v2_pre_ml_audit_not_ready_when_forbidden_feature_present():
    snapshot = _snapshot()
    snapshot["stas3_tp_pct"] = 1.0
    summary = run_v2_pre_ml_audit_from_frames(
        snapshot=snapshot,
        feature_columns=["stas3_tp_pct"],
        guard_report={"status": "PASS"},
        forward_error_ledger=_forward_errors(),
        forward_error_manifest={"status": "PASS", "rows": 2},
    )

    assert summary["status"] == "NOT_READY"
    assert "stas3_tp_pct" in summary["forbidden_feature_columns"]
