from __future__ import annotations

import json

import pandas as pd

from mlbotnav.stas5_v5_batch_dataset_builder import STATUS_PASS as ENTRY_BATCH_STATUS_PASS
from mlbotnav.stas5_v5c_train_dataset_builder import (
    RISKGATE_STATUS_PASS,
    build_v5c_review_supervised_datasets,
)


def _write_json(path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_forward_day(forward_runs_dir, run_id: str, compact_day: str, rows: list[dict], feature_columns: list[str]) -> None:
    day_dir = forward_runs_dir / run_id / "forward_market_passports" / compact_day
    day_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"STAS5_V5_MARKET_PASSPORT_{compact_day}"
    pd.DataFrame(rows).to_csv(
        day_dir / f"{prefix}_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv",
        index=False,
        encoding="utf-8-sig",
    )
    _write_json(
        day_dir / f"{prefix}_FEATURE_ALLOWLIST_274_PLUS_FULL_CAUSAL_STRUCTURE_V1.json",
        {"status": "PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY", "feature_columns": feature_columns},
    )
    _write_json(
        day_dir / f"{prefix}_FULL_CAUSAL_STRUCTURE_GUARD_V1.json",
        {"status": "PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY"},
    )


def test_v5c_review_supervised_builder_outputs_entry_and_riskgate_datasets(tmp_path) -> None:
    feature_columns = ["score", "cs_pressure_now", "fcs_context_before_entry"]
    base_csv = tmp_path / "base.csv"
    base_allowlist = tmp_path / "base_allowlist.json"
    base_guard = tmp_path / "base_guard.json"
    review_pack = tmp_path / "pack"
    forward_runs = tmp_path / "forward" / "runs"
    output_dir = tmp_path / "out"

    pd.DataFrame(
        [
            {
                "day": "2026-01-27",
                "candidate_id": "LA001",
                "record_id": "B1",
                "entry_time_utc": "2026-01-27T00:02:00Z",
                "cs_max_source_time_utc": "2026-01-27T00:01:00Z",
                "fcs_max_source_time_utc": "2026-01-27T00:01:00Z",
                "entry_y": 1,
                "phase_y": "P1",
                "state_y": "S1",
                "reason_y": "GOOD",
                "score": 1.0,
                "cs_pressure_now": 0.4,
                "fcs_context_before_entry": 1,
            },
            {
                "day": "2026-01-27",
                "candidate_id": "LA002",
                "record_id": "B2",
                "entry_time_utc": "2026-01-27T00:03:00Z",
                "cs_max_source_time_utc": "2026-01-27T00:02:00Z",
                "fcs_max_source_time_utc": "2026-01-27T00:02:00Z",
                "entry_y": 0,
                "phase_y": "P1",
                "state_y": "S2",
                "reason_y": "BAD",
                "score": 0.5,
                "cs_pressure_now": 0.2,
                "fcs_context_before_entry": 1,
            },
        ]
    ).to_csv(base_csv, index=False, encoding="utf-8-sig")
    _write_json(base_allowlist, {"feature_columns": feature_columns})
    _write_json(base_guard, {"status": ENTRY_BATCH_STATUS_PASS})

    review_manifest = {
        "status": "V5C_REVIEW_PACK_BUILT_NO_TRAINING",
        "day_rows": [
            {
                "day": "2026-02-28",
                "forward_run_id": "forward_r2",
            }
        ],
    }
    _write_json(review_pack / "STAS5_V5C_R2_R3_R4_REVIEW_PACK_MANIFEST_V1.json", review_manifest)
    _write_json(
        review_pack / "STAS5_V5C_R2_R3_R4_REVIEW_PACK_GUARD_V1.json",
        {"status": "PASS_V5C_REVIEW_PACK_GUARD_READY_NO_TRAINING"},
    )
    (review_pack / "entry").mkdir(parents=True, exist_ok=True)
    (review_pack / "riskgate").mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        [
            {
                "round_id": "R2",
                "day": "2026-02-28",
                "candidate_id": "LA010",
                "record_id": "R10",
                "entry_time_utc": "2026-02-28T00:10:00Z",
                "entry_y": 1,
                "source_forward_run_id": "forward_r2",
            },
            {
                "round_id": "R2",
                "day": "2026-02-28",
                "candidate_id": "LA011",
                "record_id": "R11",
                "entry_time_utc": "2026-02-28T00:11:00Z",
                "entry_y": 0,
                "source_forward_run_id": "forward_r2",
            },
        ]
    ).to_csv(review_pack / "entry" / "STAS5_V5C_R2_R3_R4_ENTRY_REVIEW_APPROVED_ALL_V1.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(
        [
            {
                "round_id": "R2",
                "day": "2026-02-28",
                "candidate_id": "LA011",
                "record_id": "R11",
                "entry_time_utc": "2026-02-28T00:11:00Z",
                "risk_bad_y": 1,
                "source_forward_run_id": "forward_r2",
            }
        ]
    ).to_csv(
        review_pack / "riskgate" / "STAS5_V5C_R2_R3_R4_RISKGATE_REVIEW_APPROVED_ALL_V1.csv",
        index=False,
        encoding="utf-8-sig",
    )

    _write_forward_day(
        forward_runs,
        "forward_r2",
        "20260228",
        [
            {
                "day": "2026-02-28",
                "candidate_id": "LA010",
                "record_id": "R10",
                "entry_time_utc": "2026-02-28T00:10:00Z",
                "cs_max_source_time_utc": "2026-02-28T00:09:00Z",
                "fcs_max_source_time_utc": "2026-02-28T00:09:00Z",
                "score": 0.9,
                "cs_pressure_now": 0.1,
                "fcs_context_before_entry": 1,
            },
            {
                "day": "2026-02-28",
                "candidate_id": "LA011",
                "record_id": "R11",
                "entry_time_utc": "2026-02-28T00:11:00Z",
                "cs_max_source_time_utc": "2026-02-28T00:10:00Z",
                "fcs_max_source_time_utc": "2026-02-28T00:10:00Z",
                "score": 0.2,
                "cs_pressure_now": 0.8,
                "fcs_context_before_entry": 1,
            },
        ],
        feature_columns,
    )

    entry, risk, manifest, entry_guard, risk_guard = build_v5c_review_supervised_datasets(
        train_start_day="2026-01-27",
        train_end_day="2026-02-28",
        base_start_day="2026-01-27",
        base_end_day="2026-01-27",
        review_start_day="2026-02-28",
        review_end_day="2026-02-28",
        base_batch_csv=base_csv,
        base_allowlist_json=base_allowlist,
        base_guard_json=base_guard,
        review_pack_dir=review_pack,
        forward_runs_dir=forward_runs,
        output_dir=output_dir,
        expected_features=3,
        expected_base_days=1,
        expected_base_rows=2,
        expected_base_good=1,
        expected_base_bad=1,
        expected_review_days=1,
        expected_review_rows=2,
        expected_review_good=1,
        expected_review_bad=1,
        expected_review_risk_bad=1,
        expected_entry_days=2,
        expected_entry_rows=4,
        expected_entry_good=2,
        expected_entry_bad=2,
        expected_risk_positive=1,
        expected_risk_safe_negative=1,
    )

    assert entry_guard["status"] == ENTRY_BATCH_STATUS_PASS
    assert risk_guard["status"] == RISKGATE_STATUS_PASS
    assert manifest["status"] == "PASS_V5C_REVIEW_SUPERVISED_DATASETS_READY_NO_TRAINING"
    assert len(entry) == 4
    assert entry["entry_y"].value_counts().to_dict() == {1: 2, 0: 2}
    risk_bad_entry = entry.loc[entry["candidate_id"].eq("LA011")].iloc[0]
    assert int(risk_bad_entry["entry_y"]) == 0
    assert int(risk_bad_entry["risk_bad_y"]) == 1
    assert len(risk) == 2
    assert risk["risk_bad_y"].value_counts().to_dict() == {0: 1, 1: 1}
    assert set(risk["risk_sample_role"]) == {"RISK_BAD_POSITIVE", "EXPLICIT_SAFE_ENTRY_GOOD_NEGATIVE"}
    assert (output_dir / "STAS5_V5C_BATCH_20260127_20260228_GUARD_V1.json").exists()
    assert (output_dir / "STAS5_V5C_RISKGATE_TRAIN_DATASET_20260127_20260228_GUARD_V1.json").exists()
