from __future__ import annotations

import pandas as pd
import pytest

from mlbotnav.stas5_v2_entry_ranker_train import run_v2_ablation_from_frames


def _snapshot() -> pd.DataFrame:
    rows = []
    for day in ["2026-05-01", "2026-05-02", "2026-05-03"]:
        for idx in range(6):
            keep = idx < 2
            rows.append(
                {
                    "day": day,
                    "candidate_id": f"LA{idx:03d}",
                    "record_id": f"{day}-R{idx}",
                    "entry_time_utc": f"{day}T00:{idx:02d}:00Z",
                    "human_label": "KEEP_DRAFT" if keep else "CUT_DRAFT",
                    "yellow_x_conflict": 1 if keep and idx == 0 else 0,
                    "score": 4.0 if keep else 1.0,
                    "pre_5m_long_wave_up_from_low_pct": 1.2 if keep else 0.1,
                    "stas4_v2_combo_long_recovery_score": 0.8 if keep else 0.1,
                    "stas4_v2_block_density_structure_net_score": 4.0 if keep else -2.0,
                    "stas5_v2_risk_knife_pre_entry": 0.1 if keep else 0.8,
                }
            )
    return pd.DataFrame(rows)


def test_v2_ablation_runs_feature_sets() -> None:
    feature_columns = [
        "score",
        "pre_5m_long_wave_up_from_low_pct",
        "stas4_v2_combo_long_recovery_score",
        "stas4_v2_block_density_structure_net_score",
        "stas5_v2_risk_knife_pre_entry",
    ]
    summary = run_v2_ablation_from_frames(
        snapshot=_snapshot(),
        feature_columns=feature_columns,
        numeric_columns=feature_columns,
        categorical_columns=[],
        v1_feature_columns=["score", "pre_5m_long_wave_up_from_low_pct"],
    )

    assert summary["status"] == "STAS5_V2_ABLATION_BASELINE_READY"
    assert summary["rows"] == 18
    assert any(row["feature_set"] == "full_v2_all_274" for row in summary["ablation_rows"])


def test_v2_ablation_rejects_forward_days() -> None:
    snapshot = _snapshot()
    snapshot.loc[0, "day"] = "2026-05-15"

    with pytest.raises(ValueError, match="forward days"):
        run_v2_ablation_from_frames(
            snapshot=snapshot,
            feature_columns=["score"],
            numeric_columns=["score"],
            categorical_columns=[],
            v1_feature_columns=["score"],
        )


def test_v2_ablation_rejects_forbidden_features() -> None:
    snapshot = _snapshot()
    snapshot["yellow_x"] = 1

    with pytest.raises(ValueError, match="forbidden feature"):
        run_v2_ablation_from_frames(
            snapshot=snapshot,
            feature_columns=["yellow_x"],
            numeric_columns=["yellow_x"],
            categorical_columns=[],
            v1_feature_columns=[],
        )
