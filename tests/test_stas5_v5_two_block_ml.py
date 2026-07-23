from __future__ import annotations

import json

import numpy as np
import pandas as pd

from mlbotnav.stas5_v5_batch_dataset_builder import STATUS_PASS as BATCH_GUARD_PASS
from mlbotnav.stas5_v5_two_block_ml import (
    PHASE_STATE_MODEL_KIND,
    TRAINING_GUARD_FAIL,
    TRAINING_GUARD_PASS,
    _proba_predictions,
    _run_multiclass_lodo_predictions,
    run_training_guard,
)


def _write_batch(tmp_path, *, feature_columns: list[str]) -> tuple:
    dataset_path = tmp_path / "batch.csv"
    allowlist_path = tmp_path / "allowlist.json"
    guard_path = tmp_path / "guard.json"
    rows = [
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
            "f1": 1.0,
            "cs_f2": 0.2,
        },
        {
            "day": "2026-01-28",
            "candidate_id": "LA001",
            "record_id": "R1",
            "entry_time_utc": "2026-01-28T00:02:00Z",
            "cs_max_source_time_utc": "2026-01-28T00:01:00Z",
            "fcs_max_source_time_utc": "2026-01-28T00:01:00Z",
            "entry_y": 0,
            "phase_y": "P2",
            "state_y": "S2",
            "reason_y": "BAD",
            "f1": 0.5,
            "cs_f2": 0.1,
        },
    ]
    pd.DataFrame(rows).to_csv(dataset_path, index=False, encoding="utf-8-sig")
    allowlist_path.write_text(json.dumps({"feature_columns": feature_columns}), encoding="utf-8")
    guard_path.write_text(json.dumps({"status": BATCH_GUARD_PASS}), encoding="utf-8")
    return dataset_path, allowlist_path, guard_path


def test_training_guard_passes_on_clean_small_batch(tmp_path) -> None:
    dataset_path, allowlist_path, guard_path = _write_batch(tmp_path, feature_columns=["f1", "cs_f2"])
    guard = run_training_guard(
        run_dir=tmp_path / "run",
        dataset_path=dataset_path,
        allowlist_path=allowlist_path,
        batch_guard_path=guard_path,
        expected_days=2,
        expected_rows=2,
        expected_good=1,
        expected_bad=1,
        expected_features=2,
    )
    assert guard["status"] == TRAINING_GUARD_PASS
    assert guard["feature_count"] == 2


def test_training_guard_fails_when_target_enters_features(tmp_path) -> None:
    dataset_path, allowlist_path, guard_path = _write_batch(tmp_path, feature_columns=["f1", "entry_y"])
    guard = run_training_guard(
        run_dir=tmp_path / "run",
        dataset_path=dataset_path,
        allowlist_path=allowlist_path,
        batch_guard_path=guard_path,
        expected_days=2,
        expected_rows=2,
        expected_good=1,
        expected_bad=1,
        expected_features=2,
    )
    assert guard["status"] == TRAINING_GUARD_FAIL
    checks = {item["check"]: item["status"] for item in guard["checks"]}
    assert checks["target_manual_columns_not_in_X"] == "FAIL"


def test_phase_state_raw_nan_proba_is_not_silently_sanitized() -> None:
    class _BadEstimator:
        classes_ = np.array(["A", "B"])

    class _BadPipeline:
        named_steps = {"model": _BadEstimator()}

        def predict_proba(self, _x):
            return np.array([[float("nan"), 0.0]])

    try:
        _proba_predictions(_BadPipeline(), pd.DataFrame({"f": [1.0]}), classes=["A", "B"], prefix="mps_state")
    except ValueError as exc:
        assert "raw predict_proba produced NaN/inf" in str(exc)
    else:
        raise AssertionError("raw NaN probabilities must fail instead of being sanitized")


def test_phase_state_lodo_uses_multiclass_safe_model() -> None:
    df = pd.DataFrame(
        [
            {"day": "2026-01-27", "phase_y": "P1", "f1": 0.1},
            {"day": "2026-01-28", "phase_y": "P2", "f1": 0.2},
            {"day": "2026-01-29", "phase_y": "P3", "f1": 0.3},
            {"day": "2026-01-30", "phase_y": "P1", "f1": 0.4},
        ]
    )
    pred, folds = _run_multiclass_lodo_predictions(
        df,
        target="phase_y",
        prefix="mps_phase",
        classes=["P1", "P2", "P3"],
        feature_columns=["f1"],
        numeric_columns=["f1"],
        categorical_columns=[],
    )
    assert len(pred) == len(df)
    assert not pred.isna().any().any()
    assert {fold["model_kind"] for fold in folds} == {PHASE_STATE_MODEL_KIND}
