from __future__ import annotations

import json

import pandas as pd

from mlbotnav.stas5_v3_training_dataset_builder import build_v3_training_dataset


def test_v3_training_dataset_combines_old_snapshot_and_review_rows(tmp_path) -> None:
    old_snapshot = tmp_path / "old.csv"
    old_manifest = tmp_path / "old.json"
    ledger_path = tmp_path / "ledger.csv"
    ledger_manifest = tmp_path / "ledger.json"
    forward_path = tmp_path / "forward.csv"
    out_csv = tmp_path / "v3.csv"
    out_manifest = tmp_path / "v3.json"

    feature_columns = ["score", "context_cat"]
    metadata_columns = [
        "day",
        "candidate_id",
        "record_id",
        "entry_time_utc",
        "entry_open_price",
        "entry_price_5bps",
        "human_label",
        "label_status",
        "label_source",
        "yellow_x",
        "yellow_x_role",
        "yellow_x_conflict",
        "v2_combo_feature_time_utc",
        "v2_combo_feature_available_before_entry",
    ]
    pd.DataFrame(
        [
            {
                "day": "2026-05-01",
                "candidate_id": "LA001",
                "record_id": "O1",
                "entry_time_utc": "2026-05-01T00:02:00Z",
                "entry_open_price": 1.0,
                "entry_price_5bps": 1.0005,
                "human_label": "KEEP_DRAFT",
                "label_status": "DRAFT",
                "label_source": "OLD",
                "yellow_x": 0,
                "yellow_x_role": "AUDIT_ONLY",
                "yellow_x_conflict": 0,
                "v2_combo_feature_time_utc": "2026-05-01T00:01:00Z",
                "v2_combo_feature_available_before_entry": True,
                "score": 5.0,
                "context_cat": "a",
            },
            {
                "day": "2026-05-02",
                "candidate_id": "LA002",
                "record_id": "O2",
                "entry_time_utc": "2026-05-02T00:02:00Z",
                "entry_open_price": 1.0,
                "entry_price_5bps": 1.0005,
                "human_label": "CUT_DRAFT",
                "label_status": "DRAFT",
                "label_source": "OLD",
                "yellow_x": 0,
                "yellow_x_role": "AUDIT_ONLY",
                "yellow_x_conflict": 0,
                "v2_combo_feature_time_utc": "2026-05-02T00:01:00Z",
                "v2_combo_feature_available_before_entry": True,
                "score": 1.0,
                "context_cat": "b",
            },
        ]
    ).to_csv(old_snapshot, index=False, encoding="utf-8-sig")
    old_manifest.write_text(
        json.dumps(
            {
                "status": "PASS",
                "feature_columns": feature_columns,
                "feature_count": 2,
                "v1_feature_columns": ["score"],
                "v2_feature_columns": ["context_cat"],
                "metadata_columns": metadata_columns,
            }
        ),
        encoding="utf-8",
    )
    pd.DataFrame(
        [
            {
                "day": "2026-05-16",
                "candidate_id": "LA010",
                "record_id": "F10",
                "entry_time_utc": "2026-05-16T00:10:00Z",
                "training_label": "KEEP_APPROVED",
                "label_source": "REVIEW",
                "train_usage": "TRAIN_LABEL",
                "user_review_label": "USER_GOOD_ENTRY",
                "user_review_reason": "GOOD",
                "user_note": "",
                "source_review_file": "review.csv",
                "current_ml_decision": "ENTER",
                "current_ml_score": 0.9,
                "is_auto_bad_unmarked": 0,
            },
            {
                "day": "2026-05-16",
                "candidate_id": "LA011",
                "record_id": "F11",
                "entry_time_utc": "2026-05-16T00:11:00Z",
                "training_label": "CUT_APPROVED",
                "label_source": "REVIEW",
                "train_usage": "TRAIN_LABEL_AUTO_BAD_UNMARKED_ENTER_UNSURE",
                "user_review_label": "USER_BAD_ENTRY",
                "user_review_reason": "AUTO_BAD",
                "user_note": "",
                "source_review_file": "",
                "current_ml_decision": "ENTER",
                "current_ml_score": 0.8,
                "is_auto_bad_unmarked": 1,
            },
        ]
    ).to_csv(ledger_path, index=False, encoding="utf-8-sig")
    ledger_manifest.write_text(json.dumps({"status": "PASS"}), encoding="utf-8")
    pd.DataFrame(
        [
            {
                "day": "2026-05-16",
                "candidate_id": "LA010",
                "record_id": "F10",
                "entry_time_utc": "2026-05-16T00:10:00Z",
                "entry_open_price": 1.0,
                "entry_price_5bps": 1.0005,
                "v2_combo_feature_time_utc": "2026-05-16T00:09:00Z",
                "v2_combo_feature_available_before_entry": True,
                "score": 4.0,
                "context_cat": "a",
                "ML_KEEP_SCORE_V2": 0.9,
            },
            {
                "day": "2026-05-16",
                "candidate_id": "LA011",
                "record_id": "F11",
                "entry_time_utc": "2026-05-16T00:11:00Z",
                "entry_open_price": 1.0,
                "entry_price_5bps": 1.0005,
                "v2_combo_feature_time_utc": "2026-05-16T00:10:00Z",
                "v2_combo_feature_available_before_entry": True,
                "score": 1.0,
                "context_cat": "b",
                "ML_KEEP_SCORE_V2": 0.8,
            },
        ]
    ).to_csv(forward_path, index=False, encoding="utf-8-sig")

    dataset, manifest = build_v3_training_dataset(
        old_snapshot_path=old_snapshot,
        old_snapshot_manifest_path=old_manifest,
        user_review_ledger_path=ledger_path,
        user_review_ledger_manifest_path=ledger_manifest,
        forward_predictions_path=forward_path,
        output_csv=out_csv,
        manifest_path=out_manifest,
    )

    assert manifest["status"] == "PASS"
    assert manifest["rows"] == 4
    assert manifest["feature_columns"] == feature_columns
    assert "ML_KEEP_SCORE_V2" not in manifest["feature_columns"]
    assert set(dataset["human_label"]) == {"KEEP_DRAFT", "CUT_DRAFT", "KEEP_APPROVED", "CUT_APPROVED"}
