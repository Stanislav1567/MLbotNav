from __future__ import annotations

import pandas as pd

from mlbotnav.stas5_v2_feature_snapshot_builder import build_v2_feature_snapshot_from_frames


def _v1_snapshot() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "day": "2026-05-01",
                "candidate_id": "LA001",
                "record_id": "G1P_20260501_LA001",
                "anchor_time_utc": "2026-05-01T00:34:00Z",
                "entry_time_utc": "2026-05-01T00:35:00Z",
                "entry_open_price": 100.0,
                "entry_price_5bps": 100.05,
                "anchor_low_price": 99.8,
                "human_label": "KEEP_DRAFT",
                "label_status": "DRAFT",
                "yellow_x": 1,
                "yellow_x_role": "AUDIT_ONLY",
                "yellow_x_conflict": 1,
                "suggested_type": "LOW_ANCHOR",
                "pre_15m_range_pct": 0.40,
            },
            {
                "day": "2026-05-02",
                "candidate_id": "LA001",
                "record_id": "G1P_20260502_LA001",
                "anchor_time_utc": "2026-05-02T00:34:00Z",
                "entry_time_utc": "2026-05-02T00:35:00Z",
                "entry_open_price": 101.0,
                "entry_price_5bps": 101.05,
                "anchor_low_price": 100.8,
                "human_label": "CUT_DRAFT",
                "label_status": "DRAFT",
                "yellow_x": 0,
                "yellow_x_role": "AUDIT_ONLY",
                "yellow_x_conflict": 0,
                "suggested_type": "LOW_ANCHOR",
                "pre_15m_range_pct": 0.52,
            },
        ]
    )


def _v2_combo(*, entry_time_second_row: str = "2026-05-02T00:35:00Z") -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "day": "2026-05-01",
                "candidate_id": "LA001",
                "record_id": "G1P_20260501_LA001",
                "anchor_time_utc": "2026-05-01T00:34:00Z",
                "entry_time_utc": "2026-05-01T00:35:00Z",
                "feature_time_utc": "2026-05-01T00:34:00Z",
                "feature_available_before_entry": True,
                "entry_price_5bps": 100.05,
                "source_ohlcv": "unit",
                "audit_no_trade_reason": "OK",
                "stas4_v2_combo_rsi14": 42.0,
                "stas5_v2_risk_knife_pre_entry": 0.35,
            },
            {
                "day": "2026-05-02",
                "candidate_id": "LA001",
                "record_id": "G1P_20260502_LA001",
                "anchor_time_utc": "2026-05-02T00:34:00Z",
                "entry_time_utc": entry_time_second_row,
                "feature_time_utc": "2026-05-02T00:34:00Z",
                "feature_available_before_entry": True,
                "entry_price_5bps": 101.05,
                "source_ohlcv": "unit",
                "audit_no_trade_reason": "OK",
                "stas4_v2_combo_rsi14": 37.0,
                "stas5_v2_risk_knife_pre_entry": 0.62,
            },
        ]
    )


def test_v2_feature_snapshot_merges_v1_and_combo_without_losing_labels():
    snapshot, manifest = build_v2_feature_snapshot_from_frames(
        v1_snapshot=_v1_snapshot(),
        v2_combo=_v2_combo(),
        v1_feature_columns=["suggested_type", "pre_15m_range_pct"],
        v2_feature_columns=["stas4_v2_combo_rsi14", "stas5_v2_risk_knife_pre_entry"],
        ledger=_v1_snapshot(),
    )

    assert manifest["status"] == "PASS"
    assert len(snapshot) == 2
    assert manifest["feature_count"] == 4
    assert manifest["checks"]["keep_yellow_x_rows"] == 1
    assert "human_label" in snapshot.columns
    assert "yellow_x" in snapshot.columns
    assert "yellow_x" not in manifest["feature_columns"]
    assert "stas4_v2_combo_rsi14" in manifest["feature_columns"]
    assert "v2_combo_feature_time_utc" in snapshot.columns
    assert snapshot.loc[0, "record_id"] == "G1P_20260501_LA001"
    assert snapshot.loc[1, "record_id"] == "G1P_20260502_LA001"


def test_v2_feature_snapshot_fails_on_entry_time_mismatch():
    _snapshot, manifest = build_v2_feature_snapshot_from_frames(
        v1_snapshot=_v1_snapshot(),
        v2_combo=_v2_combo(entry_time_second_row="2026-05-02T00:36:00Z"),
        v1_feature_columns=["suggested_type", "pre_15m_range_pct"],
        v2_feature_columns=["stas4_v2_combo_rsi14", "stas5_v2_risk_knife_pre_entry"],
        ledger=_v1_snapshot(),
    )

    assert manifest["status"] == "FAIL"
    assert manifest["checks"]["entry_time_mismatch"] == 1


def test_v2_feature_snapshot_fails_if_forbidden_feature_requested():
    _snapshot, manifest = build_v2_feature_snapshot_from_frames(
        v1_snapshot=_v1_snapshot(),
        v2_combo=_v2_combo(),
        v1_feature_columns=["suggested_type"],
        v2_feature_columns=["stas4_v2_combo_rsi14", "stas3_tp_pct"],
        ledger=_v1_snapshot(),
    )

    assert manifest["status"] == "FAIL"
    assert "stas3_tp_pct" in manifest["checks"]["forbidden_feature_columns"]
