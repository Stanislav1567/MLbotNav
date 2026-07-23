from __future__ import annotations

import json

import pandas as pd

from mlbotnav.stas5_v5_batch_dataset_builder import STATUS_PASS, build_v5_batch_dataset


def _write_day(v5_root, day_compact: str, rows: list[dict], feature_columns: list[str]) -> None:
    day_dir = v5_root / "market_passports" / day_compact
    day_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"STAS5_V5_MARKET_PASSPORT_{day_compact}"
    pd.DataFrame(rows).to_csv(
        day_dir / f"{prefix}_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv",
        index=False,
        encoding="utf-8-sig",
    )
    (day_dir / f"{prefix}_FEATURE_ALLOWLIST_274_PLUS_FULL_CAUSAL_STRUCTURE_V1.json").write_text(
        json.dumps(
            {
                "status": "PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY",
                "feature_columns": feature_columns,
                "feature_count": len(feature_columns),
            }
        ),
        encoding="utf-8",
    )
    (day_dir / f"{prefix}_FULL_CAUSAL_STRUCTURE_GUARD_V1.json").write_text(
        json.dumps({"status": "PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY"}),
        encoding="utf-8",
    )


def test_v5_batch_dataset_builds_guard_and_fills_feature_gaps(tmp_path) -> None:
    v5_root = tmp_path / "v5"
    output_dir = tmp_path / "out"
    feature_columns = ["score", "cs_pressure_now", "fcs_context_before_entry"]

    _write_day(
        v5_root,
        "20260127",
        [
            {
                "day": "2026-01-27",
                "candidate_id": "LA001",
                "record_id": "R1",
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
                "record_id": "R2",
                "entry_time_utc": "2026-01-27T00:03:00Z",
                "cs_max_source_time_utc": "2026-01-27T00:02:00Z",
                "fcs_max_source_time_utc": "2026-01-27T00:02:00Z",
                "entry_y": 0,
                "phase_y": "P1",
                "state_y": "S2",
                "reason_y": "BAD",
                "score": None,
                "cs_pressure_now": 0.2,
                "fcs_context_before_entry": 1,
            },
        ],
        feature_columns,
    )
    _write_day(
        v5_root,
        "20260128",
        [
            {
                "day": "2026-01-28",
                "candidate_id": "LA001",
                "record_id": "R1",
                "entry_time_utc": "2026-01-28T00:02:00Z",
                "cs_max_source_time_utc": "2026-01-28T00:01:00Z",
                "fcs_max_source_time_utc": "2026-01-28T00:01:00Z",
                "entry_y": 0,
                "phase_y": "P2",
                "state_y": "S3",
                "reason_y": "NO_TRADE",
                "score": 0.5,
                "cs_pressure_now": 0.1,
                "fcs_context_before_entry": 1,
            }
        ],
        feature_columns,
    )

    dataset, manifest, guard = build_v5_batch_dataset(
        start_day="2026-01-27",
        end_day="2026-01-28",
        v5_root=v5_root,
        output_dir=output_dir,
        expected_days=2,
        expected_rows=3,
        expected_good=1,
        expected_bad=2,
        expected_features=3,
    )

    assert guard["status"] == STATUS_PASS
    assert manifest["rows"] == 3
    assert manifest["feature_count"] == 3
    assert manifest["entry_y_counts"] == {"0": 2, "1": 1}
    assert manifest["feature_fill_summary"]["feature_missing_before_fill"] == 1
    assert int(dataset["score"].isna().sum()) == 0
    assert float(dataset.loc[dataset["candidate_id"].eq("LA002"), "score"].iloc[0]) == 0.0
    assert "phase_y" not in guard["feature_columns"]
    assert (output_dir / "STAS5_V5_BATCH_20260127_20260128_GUARD_V1.json").exists()
