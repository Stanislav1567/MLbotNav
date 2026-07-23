from __future__ import annotations

import pandas as pd

from mlbotnav.stas5_v4_group_rank_train import apply_v4_decision_policy, group_rank_metrics


def test_v4_group_rank_metrics_prioritize_winner_inside_group() -> None:
    rows = pd.DataFrame(
        [
            {
                "day": "2026-05-15",
                "group_id": "G1",
                "candidate_id": "LA001",
                "record_id": "R1",
                "entry_time_utc": "2026-05-15T00:01:00Z",
                "rank_label": "BAD_IN_GROUP",
                "is_group_winner": 0,
                "score": 0.90,
            },
            {
                "day": "2026-05-15",
                "group_id": "G1",
                "candidate_id": "LA002",
                "record_id": "R2",
                "entry_time_utc": "2026-05-15T00:02:00Z",
                "rank_label": "BEST_GOOD",
                "is_group_winner": 1,
                "score": 0.80,
            },
            {
                "day": "2026-05-15",
                "group_id": "G2",
                "candidate_id": "LA003",
                "record_id": "R3",
                "entry_time_utc": "2026-05-15T00:03:00Z",
                "rank_label": "BEST_GOOD",
                "is_group_winner": 1,
                "score": 0.70,
            },
            {
                "day": "2026-05-15",
                "group_id": "G2",
                "candidate_id": "LA004",
                "record_id": "R4",
                "entry_time_utc": "2026-05-15T00:04:00Z",
                "rank_label": "BAD_IN_GROUP",
                "is_group_winner": 0,
                "score": 0.10,
            },
        ]
    )

    metrics = group_rank_metrics(rows, score_column="score")

    assert metrics["trade_groups"] == 2
    assert metrics["top1_group_accuracy"] == 0.5
    assert metrics["winner_in_top2"] == 1.0
    assert metrics["bad_in_group_top1_count"] == 1


def test_v4_decision_policy_selects_group_top_rows_not_all_high_rows() -> None:
    rows = pd.DataFrame(
        [
            {"day": "2026-05-26", "group_id": "G1", "score": 0.90},
            {"day": "2026-05-26", "group_id": "G1", "score": 0.80},
            {"day": "2026-05-26", "group_id": "G2", "score": 0.40},
            {"day": "2026-05-26", "group_id": "G2", "score": 0.39},
            {"day": "2026-05-26", "group_id": "G3", "score": 0.20},
        ]
    )

    out = apply_v4_decision_policy(rows, score_column="score", enter_threshold=0.50, unsure_threshold=0.35)

    assert out["V4_DECISION"].tolist().count("ENTER") == 2
    assert out.loc[1, "V4_DECISION"] == "UNSURE"
    assert out.loc[3, "V4_DECISION"] == "UNSURE"
    assert out.loc[4, "V4_DECISION"] == "SKIP"
