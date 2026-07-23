from __future__ import annotations

import json

import pandas as pd

from mlbotnav.stas5_v3_leakage_guard import run_v3_leakage_guard


def _write_dataset(tmp_path, *, bad_day: bool = False) -> tuple:
    feature_columns = [f"feat_{idx:03d}" for idx in range(274)]
    rows = []
    labels = [
        ("2026-05-01", "KEEP_DRAFT"),
        ("2026-05-02", "CUT_DRAFT"),
        ("2026-05-16", "KEEP_APPROVED"),
        ("2026-05-17" if not bad_day else "2026-05-21", "CUT_APPROVED"),
    ]
    for idx, (day, label) in enumerate(labels):
        row = {
            "day": day,
            "candidate_id": f"LA{idx:03d}",
            "record_id": f"R{idx}",
            "entry_time_utc": f"{day}T00:02:00Z",
            "human_label": label,
            "v3_train_source": "TEST",
            "v2_combo_feature_time_utc": f"{day}T00:01:00Z",
            "v2_combo_feature_available_before_entry": True,
        }
        for feature in feature_columns:
            row[feature] = float(idx)
        rows.append(row)
    dataset_path = tmp_path / "dataset.csv"
    manifest_path = tmp_path / "dataset.json"
    pd.DataFrame(rows).to_csv(dataset_path, index=False, encoding="utf-8-sig")
    manifest_path.write_text(
        json.dumps(
            {
                "status": "PASS",
                "feature_columns": feature_columns,
                "feature_count": len(feature_columns),
                "numeric_columns": feature_columns,
                "categorical_columns": [],
                "metadata_columns": [
                    "day",
                    "candidate_id",
                    "record_id",
                    "entry_time_utc",
                    "human_label",
                    "v3_train_source",
                    "v2_combo_feature_time_utc",
                    "v2_combo_feature_available_before_entry",
                ],
            }
        ),
        encoding="utf-8",
    )
    return dataset_path, manifest_path


def test_v3_leakage_guard_passes_clean_274_feature_dataset(tmp_path) -> None:
    dataset_path, manifest_path = _write_dataset(tmp_path)
    report = run_v3_leakage_guard(
        dataset_path=dataset_path,
        dataset_manifest_path=manifest_path,
        output_path=tmp_path / "guard.json",
    )

    assert report["status"] == "PASS"
    assert report["feature_count"] == 274


def test_v3_leakage_guard_fails_holdout_day(tmp_path) -> None:
    dataset_path, manifest_path = _write_dataset(tmp_path, bad_day=True)
    report = run_v3_leakage_guard(
        dataset_path=dataset_path,
        dataset_manifest_path=manifest_path,
        output_path=tmp_path / "guard.json",
        strict=False,
    )

    assert report["status"] == "FAIL"
    assert report["checks"]["holdout_days_present"] == ["2026-05-21"]
