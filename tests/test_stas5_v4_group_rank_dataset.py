from __future__ import annotations

import json

import pandas as pd

from mlbotnav.stas5_v4_group_rank_dataset import (
    V4_GROUP_AUDIT_COLUMNS,
    V4_GROUP_MODEL_FEATURE_COLUMNS,
    build_v4_group_rank_dataset,
)


def test_v4_group_rank_dataset_joins_review_ledger_and_blocks_old_ml_features(tmp_path) -> None:
    old_snapshot_path = tmp_path / "old.csv"
    old_manifest_path = tmp_path / "old.manifest.json"
    ledger_path = tmp_path / "ledger.csv"
    forward_15_20_path = tmp_path / "forward_15_20.csv"
    forward_21_25_path = tmp_path / "forward_21_25.csv"
    output_csv = tmp_path / "v4.csv"
    manifest_path = tmp_path / "v4.manifest.json"

    feature_columns = ["context_score", "context_cat"]
    pd.DataFrame(
        [
            {
                "day": "2026-05-01",
                "candidate_id": "LA001",
                "record_id": "O1",
                "entry_time_utc": "2026-05-01T00:01:00Z",
                "entry_price_5bps": 10.0,
                "human_label": "CUT_DRAFT",
                "label_status": "DRAFT",
                "context_score": 1.0,
                "context_cat": "a",
            },
            {
                "day": "2026-05-01",
                "candidate_id": "LA002",
                "record_id": "O2",
                "entry_time_utc": "2026-05-01T00:05:00Z",
                "entry_price_5bps": 9.8,
                "human_label": "KEEP_DRAFT",
                "label_status": "DRAFT",
                "context_score": 2.0,
                "context_cat": "b",
            },
        ]
    ).to_csv(old_snapshot_path, index=False, encoding="utf-8-sig")
    old_manifest_path.write_text(
        json.dumps(
            {
                "status": "PASS",
                "feature_columns": feature_columns,
                "numeric_columns": ["context_score"],
                "categorical_columns": ["context_cat"],
            }
        ),
        encoding="utf-8",
    )

    pd.DataFrame(
        [
            {
                "day": "2026-05-15",
                "symbol": "SOLUSDT",
                "timeframe": "1m",
                "group_id": "G1",
                "candidate_id": "LA010",
                "record_id": "F10",
                "entry_time_utc": "2026-05-15T00:10:00Z",
                "entry_price_5bps": 10.0,
                "rank_label": "BAD_IN_GROUP",
                "is_group_winner": 0,
                "primary_reason_code": "BAD_TOO_EARLY",
                "secondary_reason_codes": "",
                "label_status": "DRAFT",
                "source_review_file": "review.md",
                "notes": "",
            },
            {
                "day": "2026-05-15",
                "symbol": "SOLUSDT",
                "timeframe": "1m",
                "group_id": "G1",
                "candidate_id": "LA011",
                "record_id": "F11",
                "entry_time_utc": "2026-05-15T00:12:00Z",
                "entry_price_5bps": 9.7,
                "rank_label": "BEST_GOOD",
                "is_group_winner": 1,
                "primary_reason_code": "GOOD_BEST_LOCAL_LOW",
                "secondary_reason_codes": "",
                "label_status": "DRAFT",
                "source_review_file": "review.md",
                "notes": "",
            },
        ]
    ).to_csv(ledger_path, index=False, encoding="utf-8-sig")

    forward_columns = [
        "day",
        "candidate_id",
        "record_id",
        "entry_time_utc",
        "entry_price_5bps",
        "context_score",
        "context_cat",
        "ML_KEEP_SCORE_V2",
        "ML_DECISION_V2",
    ]
    pd.DataFrame(
        [
            {
                "day": "2026-05-15",
                "candidate_id": "LA010",
                "record_id": "F10",
                "entry_time_utc": "2026-05-15T00:10:00Z",
                "entry_price_5bps": 10.0,
                "context_score": 0.5,
                "context_cat": "x",
                "ML_KEEP_SCORE_V2": 0.9,
                "ML_DECISION_V2": "ENTER",
            },
            {
                "day": "2026-05-15",
                "candidate_id": "LA011",
                "record_id": "F11",
                "entry_time_utc": "2026-05-15T00:12:00Z",
                "entry_price_5bps": 9.7,
                "context_score": 3.0,
                "context_cat": "y",
                "ML_KEEP_SCORE_V2": 0.8,
                "ML_DECISION_V2": "ENTER",
            },
        ],
        columns=forward_columns,
    ).to_csv(forward_15_20_path, index=False, encoding="utf-8-sig")
    pd.DataFrame(columns=forward_columns).to_csv(forward_21_25_path, index=False, encoding="utf-8-sig")

    dataset, manifest = build_v4_group_rank_dataset(
        old_snapshot_path=old_snapshot_path,
        old_snapshot_manifest_path=old_manifest_path,
        group_ledger_path=ledger_path,
        forward_15_20_path=forward_15_20_path,
        forward_21_25_path=forward_21_25_path,
        output_csv=output_csv,
        manifest_path=manifest_path,
    )

    assert manifest["status"] == "PASS"
    assert manifest["review_join_checks"]["missing_after_forward_join"] == 0
    assert manifest["rows"] == 4
    assert set(V4_GROUP_MODEL_FEATURE_COLUMNS).issubset(set(manifest["feature_columns"]))
    assert not set(V4_GROUP_AUDIT_COLUMNS).intersection(set(manifest["feature_columns"]))
    assert "ML_KEEP_SCORE_V2" not in manifest["feature_columns"]
    assert "ML_DECISION_V2" not in manifest["feature_columns"]
    assert int(dataset["is_group_winner"].sum()) == 2
