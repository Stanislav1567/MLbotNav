from __future__ import annotations

import json

import pandas as pd

from mlbotnav.stas5_v5c_riskgate_ml import (
    RISKGATE_POST_TRAIN_GUARD_PASS,
    RISKGATE_TRAIN_STATUS,
    RISKGATE_TRAINING_GUARD_PASS,
    apply_riskgate_to_entry_decisions,
    apply_v5c_riskgate_forward,
    train_v5c_riskgate_ml,
)


def _write_json(path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _row(day: str, candidate_id: str, target: int, score: float) -> dict:
    compact = day.replace("-", "")
    return {
        "day": day,
        "candidate_id": candidate_id,
        "record_id": f"{compact}_{candidate_id}",
        "entry_time_utc": f"{day}T00:10:00Z",
        "cs_max_source_time_utc": f"{day}T00:09:00Z",
        "fcs_max_source_time_utc": f"{day}T00:09:00Z",
        "entry_y": 0 if target else 1,
        "risk_bad_y": target,
        "risk_sample_role": "RISK_BAD_POSITIVE" if target else "EXPLICIT_SAFE_ENTRY_GOOD_NEGATIVE",
        "risk_score_feature": score,
        "cs_pressure_now": score * 0.5,
    }


def test_riskgate_ml_trains_and_applies_live_scores(tmp_path) -> None:
    dataset_path = tmp_path / "risk.csv"
    allowlist_path = tmp_path / "allowlist.json"
    guard_path = tmp_path / "guard.json"
    feature_columns = ["risk_score_feature", "cs_pressure_now"]
    rows = []
    for day, offset in [("2026-03-01", 0.0), ("2026-03-02", 0.02), ("2026-03-03", 0.04)]:
        rows.append(_row(day, "LA001", 1, 0.90 + offset))
        rows.append(_row(day, "LA002", 0, 0.10 + offset))
    pd.DataFrame(rows).to_csv(dataset_path, index=False, encoding="utf-8-sig")
    _write_json(allowlist_path, {"feature_columns": feature_columns})
    _write_json(guard_path, {"status": "PASS_V5C_RISKGATE_TRAIN_DATASET_GUARD_READY_NO_TRAINING"})

    manifest = train_v5c_riskgate_ml(
        run_dir=tmp_path / "run",
        dataset_path=dataset_path,
        allowlist_path=allowlist_path,
        dataset_guard_path=guard_path,
        expected_features=2,
    )

    assert manifest["status"] == RISKGATE_TRAIN_STATUS
    assert manifest["training_guard_status"] == RISKGATE_TRAINING_GUARD_PASS
    assert manifest["post_train_guard_status"] == RISKGATE_POST_TRAIN_GUARD_PASS
    assert (tmp_path / "run" / "STAS5_V5C_RISKGATE_ML_MODEL.joblib").exists()
    assert (tmp_path / "run" / "STAS5_V5C_RISKGATE_ML_OOF_PREDICTIONS_V1.csv").exists()

    live = pd.DataFrame(
        [
            _row("2026-03-04", "LA010", 1, 0.95),
            _row("2026-03-04", "LA011", 0, 0.05),
        ]
    )
    payload = apply_v5c_riskgate_forward(live, manifest, project_root=tmp_path)
    assert len(payload["scores"]) == 2
    assert set(payload["decisions"]).issubset({"BLOCK_RISK", "WARN_RISK", "PASS_RISK"})
    final, action = apply_riskgate_to_entry_decisions(["ENTER", "ENTER"], ["BLOCK_RISK", "PASS_RISK"])
    assert final.tolist() == ["SKIP", "ENTER"]
    assert action.tolist() == ["RISKGATE_BLOCK_TO_SKIP", "KEEP_ENTRY_DECISION"]
