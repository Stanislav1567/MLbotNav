from __future__ import annotations

import pandas as pd

from mlbotnav.stas5_feature_snapshot_builder import build_feature_snapshot_from_frames, select_feature_columns


def test_feature_allowlist_excludes_future_yellow_and_outcome_columns():
    columns = [
        "day_utc",
        "candidate_id",
        "record_id",
        "review_label",
        "outcome_status",
        "future_return",
        "yellow_x",
        "stas3_tp_pct",
        "suggested_type",
        "score",
        "pre_15m_range_pct",
        "pre_15m_last_open_time_utc",
        "pre_15m_window_low_price",
        "entry_setup_quality_code",
        "context_before_entry_check",
    ]

    features = select_feature_columns(columns)

    assert "suggested_type" in features
    assert "score" in features
    assert "pre_15m_range_pct" in features
    assert "entry_setup_quality_code" in features
    assert "context_before_entry_check" in features
    assert "future_return" not in features
    assert "yellow_x" not in features
    assert "review_label" not in features
    assert "outcome_status" not in features
    assert "stas3_tp_pct" not in features
    assert "pre_15m_last_open_time_utc" not in features
    assert "pre_15m_window_low_price" not in features


def test_feature_snapshot_keeps_labels_as_metadata_not_features():
    ledger = pd.DataFrame(
        [
            {
                "day": "2026-05-01",
                "candidate_id": "LA001",
                "record_id": "G1P_20260501_LA001",
                "anchor_time_utc": "2026-05-01T00:00:00Z",
                "entry_time_utc": "2026-05-01T00:01:00Z",
                "entry_open_price": 100.0,
                "entry_price_5bps": 100.05,
                "anchor_low_price": 99.0,
                "human_label": "KEEP_DRAFT",
                "label_status": "DRAFT",
                "yellow_x": 1,
                "yellow_x_role": "AUDIT_ONLY",
                "yellow_x_conflict": 1,
            }
        ]
    )
    stas2 = pd.DataFrame(
        [
            {
                "day_utc": "2026-05-01",
                "candidate_id": "LA001",
                "record_id": "G1P_20260501_LA001",
                "anchor_time_utc": "2026-05-01T00:00:00Z",
                "entry_time_utc": "2026-05-01T00:01:00Z",
                "entry_open_price": 100.0,
                "entry_price_5bps": 100.05,
                "anchor_low_price": 99.0,
                "suggested_type": "LOW_ANCHOR",
                "score": 3.0,
                "pre_15m_range_pct": 0.42,
                "context_before_entry_check": True,
            }
        ]
    )

    snapshot, manifest = build_feature_snapshot_from_frames(stas2=stas2, ledger=ledger, source_stas2_run="unit")

    assert manifest["status"] == "PASS"
    assert "human_label" in snapshot.columns
    assert "yellow_x" in snapshot.columns
    assert "human_label" not in manifest["feature_columns"]
    assert "yellow_x" not in manifest["feature_columns"]
    assert "pre_15m_range_pct" in manifest["feature_columns"]
