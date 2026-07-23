from __future__ import annotations

import pandas as pd

from mlbotnav.stas5_v2_leakage_guard import run_v2_leakage_guard_from_frames


def _snapshot(*, bad_time: bool = False, day: str = "2026-05-01") -> pd.DataFrame:
    feature_time = "2026-05-01T00:35:00Z" if bad_time else "2026-05-01T00:34:00Z"
    return pd.DataFrame(
        [
            {
                "day": day,
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
                "v2_combo_anchor_time_utc": "2026-05-01T00:34:00Z",
                "v2_combo_entry_time_utc": "2026-05-01T00:35:00Z",
                "v2_combo_feature_time_utc": feature_time,
                "v2_combo_feature_available_before_entry": True,
                "suggested_type": "LOW_ANCHOR",
                "stas4_v2_combo_rsi14": 42.0,
                "stas5_v2_risk_knife_pre_entry": 0.25,
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
                "v2_combo_anchor_time_utc": "2026-05-02T00:34:00Z",
                "v2_combo_entry_time_utc": "2026-05-02T00:35:00Z",
                "v2_combo_feature_time_utc": "2026-05-02T00:34:00Z",
                "v2_combo_feature_available_before_entry": True,
                "suggested_type": "LOW_ANCHOR",
                "stas4_v2_combo_rsi14": 37.0,
                "stas5_v2_risk_knife_pre_entry": 0.71,
            },
        ]
    )


def _manifest(feature_columns: list[str]) -> dict[str, object]:
    return {
        "status": "PASS",
        "rows": 2,
        "pipeline_status": "unit",
        "feature_columns": feature_columns,
    }


def test_v2_leakage_guard_passes_clean_snapshot_contract():
    report = run_v2_leakage_guard_from_frames(
        snapshot=_snapshot(),
        manifest=_manifest(["suggested_type", "stas4_v2_combo_rsi14", "stas5_v2_risk_knife_pre_entry"]),
        expected_rows=2,
        expected_keep_yellow_rows=1,
    )

    assert report["status"] == "PASS"
    assert report["checks"]["v2_combo_feature_time_not_before_entry"] == 0
    assert report["checks"]["keep_yellow_x_rows"] == 1


def test_v2_leakage_guard_fails_if_yellow_or_stas3_becomes_feature():
    frame = _snapshot()
    frame["stas3_tp_pct"] = 1.0
    frame["old_removed_candidate"] = 1
    report = run_v2_leakage_guard_from_frames(
        snapshot=frame,
        manifest=_manifest(["suggested_type", "yellow_x", "stas3_tp_pct", "old_removed_candidate"]),
        expected_rows=2,
        expected_keep_yellow_rows=1,
    )

    assert report["status"] == "FAIL"
    assert "yellow_x" in report["checks"]["label_columns_in_features"]
    assert "yellow_x" in report["checks"]["forbidden_feature_columns"]
    assert "stas3_tp_pct" in report["checks"]["forbidden_feature_columns"]
    assert "old_removed_candidate" in report["checks"]["forbidden_feature_columns"]


def test_v2_leakage_guard_fails_if_feature_time_is_not_before_entry():
    report = run_v2_leakage_guard_from_frames(
        snapshot=_snapshot(bad_time=True),
        manifest=_manifest(["suggested_type", "stas4_v2_combo_rsi14", "stas5_v2_risk_knife_pre_entry"]),
        expected_rows=2,
        expected_keep_yellow_rows=1,
    )

    assert report["status"] == "FAIL"
    assert report["checks"]["v2_combo_feature_time_not_before_entry"] == 1


def test_v2_leakage_guard_fails_if_forward_day_leaks_into_train_snapshot():
    report = run_v2_leakage_guard_from_frames(
        snapshot=_snapshot(day="2026-05-15"),
        manifest=_manifest(["suggested_type", "stas4_v2_combo_rsi14", "stas5_v2_risk_knife_pre_entry"]),
        expected_rows=2,
        expected_keep_yellow_rows=1,
    )

    assert report["status"] == "FAIL"
    assert report["checks"]["forward_days_present"] == 1
