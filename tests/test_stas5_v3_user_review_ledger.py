from __future__ import annotations

import pandas as pd

from mlbotnav.stas5_v3_user_review_ledger import build_v3_user_review_ledger


def test_v3_user_review_ledger_auto_bad_unmarked_enter_unsure(tmp_path) -> None:
    review_root = tmp_path / "review"
    day_dir = review_root / "20260516"
    day_dir.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "day": "2026-05-16",
                "candidate_id": "LA002",
                "entry_time_utc": "2026-05-16T00:02:00Z",
                "current_ml_decision": "UNSURE",
                "current_ml_score": 0.5,
                "user_review_label": "USER_GOOD_ENTRY",
                "user_review_reason": "GOOD",
                "notes": "",
            },
            {
                "day": "2026-05-16",
                "candidate_id": "LA004",
                "entry_time_utc": "2026-05-16T00:04:00Z",
                "current_ml_decision": "SKIP",
                "current_ml_score": 0.2,
                "user_review_label": "USER_MISSED_GOOD",
                "user_review_reason": "MISSED",
                "notes": "",
            },
            {
                "day": "2026-05-16",
                "candidate_id": "NO_CANDIDATE_1",
                "entry_time_utc": "2026-05-16T00:06:00Z",
                "current_ml_decision": "NO_CANDIDATE",
                "current_ml_score": "",
                "user_review_label": "USER_NO_CANDIDATE_ZONE",
                "user_review_reason": "GAP",
                "notes": "",
            },
        ]
    ).to_csv(day_dir / "STAS5_V2_USER_REVIEW_SCREEN_DRAFT_20260516.csv", index=False, encoding="utf-8-sig")

    forward_path = tmp_path / "forward.csv"
    pd.DataFrame(
        [
            {
                "day": "2026-05-16",
                "candidate_id": "LA001",
                "record_id": "R1",
                "entry_time_utc": "2026-05-16T00:01:00Z",
                "entry_open_price": 1.0,
                "entry_price_5bps": 1.0005,
                "ML_DECISION_V2": "ENTER",
                "ML_KEEP_SCORE_V2": 0.8,
            },
            {
                "day": "2026-05-16",
                "candidate_id": "LA002",
                "record_id": "R2",
                "entry_time_utc": "2026-05-16T00:02:00Z",
                "entry_open_price": 1.0,
                "entry_price_5bps": 1.0005,
                "ML_DECISION_V2": "UNSURE",
                "ML_KEEP_SCORE_V2": 0.5,
            },
            {
                "day": "2026-05-16",
                "candidate_id": "LA003",
                "record_id": "R3",
                "entry_time_utc": "2026-05-16T00:03:00Z",
                "entry_open_price": 1.0,
                "entry_price_5bps": 1.0005,
                "ML_DECISION_V2": "SKIP",
                "ML_KEEP_SCORE_V2": 0.1,
            },
            {
                "day": "2026-05-16",
                "candidate_id": "LA004",
                "record_id": "R4",
                "entry_time_utc": "2026-05-16T00:04:00Z",
                "entry_open_price": 1.0,
                "entry_price_5bps": 1.0005,
                "ML_DECISION_V2": "SKIP",
                "ML_KEEP_SCORE_V2": 0.2,
            },
        ]
    ).to_csv(forward_path, index=False, encoding="utf-8-sig")

    ledger, manifest = build_v3_user_review_ledger(
        review_root=review_root,
        all_predictions_path=forward_path,
        start_day="2026-05-16",
        end_day="2026-05-16",
        output_csv=tmp_path / "ledger.csv",
        manifest_path=tmp_path / "ledger.json",
    )

    assert manifest["status"] == "PASS"
    assert manifest["auto_bad_unmarked_enter_unsure"] == 1
    assert set(ledger["candidate_id"]) == {"LA001", "LA002", "LA004", "NO_CANDIDATE_1"}
    assert ledger.loc[ledger["candidate_id"] == "LA001", "training_label"].item() == "CUT_APPROVED"
    assert ledger.loc[ledger["candidate_id"] == "LA004", "training_label"].item() == "KEEP_APPROVED"
    assert ledger.loc[ledger["candidate_id"] == "NO_CANDIDATE_1", "train_usage"].item() == "NO_CANDIDATE_AUDIT_ONLY"
