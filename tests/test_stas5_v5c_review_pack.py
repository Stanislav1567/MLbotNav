from __future__ import annotations

import json

import pandas as pd

import mlbotnav.stas5_v5c_review_pack as review_pack
from mlbotnav.stas5_v5c_review_pack import RoundSpec, STATUS_FAIL, STATUS_PASS, build_review_pack


def _write_forward_entries(forward_root, run_id: str, day: str, ids: list[str]) -> None:
    compact = day.replace("-", "")
    out_dir = forward_root / run_id / "visual_review" / compact
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for index, candidate_id in enumerate(ids, start=1):
        rows.append(
            {
                "day": day,
                "candidate_id": candidate_id,
                "record_id": f"{day}_{candidate_id}",
                "entry_time_utc": f"{day}T00:{index:02d}:00Z",
                "ENTRY_ML_LIVE_SCORE": 0.1 * index,
                "ENTRY_ML_LIVE_DECISION": "ENTER" if index % 2 else "WATCH",
            }
        )
    pd.DataFrame(rows).to_csv(
        out_dir / f"STAS5_V5_FORWARD_VISUAL_REVIEW_ENTRIES_{compact}.csv",
        index=False,
        encoding="utf-8-sig",
    )


def _write_day_review(review_root, round_id: str, day: str, entry_rows: list[dict], risk_rows: list[dict]) -> None:
    compact = day.replace("-", "")
    base = review_root / f"{round_id.lower()}_user_review" / compact
    base.mkdir(parents=True, exist_ok=True)
    prefix = f"STAS5_V5C_{round_id}_USER_REVIEW_{compact}"
    risk_prefix = f"STAS5_V5C_{round_id}_USER_RISKGATE_REVIEW_{compact}"

    pd.DataFrame(entry_rows).to_csv(base / f"{prefix}_APPROVED.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(risk_rows).to_csv(base / f"{risk_prefix}_APPROVED.csv", index=False, encoding="utf-8-sig")
    (base / f"{prefix}_APPROVED.json").write_text(json.dumps({"status": "APPROVED"}), encoding="utf-8")
    (base / f"{risk_prefix}_APPROVED.json").write_text(json.dumps({"status": "APPROVED"}), encoding="utf-8")
    (base / f"STAS5_V5C_{round_id}_REVIEW_LADDER_{compact}_APPROVED_RESULT.json").write_text(
        json.dumps({"status": "APPROVED"}),
        encoding="utf-8",
    )
    (base / f"STAS5_V5C_{round_id}_USER_REVIEW_{compact}_CURRENT_REVIEW.png").write_bytes(b"png")
    (base / f"STAS5_V5C_{round_id}_USER_REVIEW_{compact}_CURRENT_VISUAL_MANIFEST_V1.json").write_text(
        json.dumps({"status": "PASS", "current_review_png": "x.png"}),
        encoding="utf-8",
    )


def _entry(day: str, candidate_id: str, y: int, from_risk: int = 0) -> dict:
    return {
        "day": day,
        "candidate_id": candidate_id,
        "record_id": f"{day}_{candidate_id}",
        "entry_time_utc": f"{day}T00:01:00Z",
        "entry_y": y,
        "user_label": "GOOD" if y else "BAD",
        "entry_review_label": "GOOD" if y else "BAD",
        "entry_from_risk_bad": from_risk,
        "model_decision": "ENTER",
        "marker": "green_triangle",
        "marker_user": "green_triangle",
    }


def _risk(day: str, candidate_id: str) -> dict:
    return {
        "day": day,
        "candidate_id": candidate_id,
        "record_id": f"{day}_{candidate_id}",
        "entry_time_utc": f"{day}T00:01:00Z",
        "risk_bad_y": 1,
        "risk_bad_target": 1,
        "risk_review_label": "RISK_BAD",
        "model_decision": "ENTER",
        "marker": "green_triangle",
        "marker_user": "green_triangle",
    }


def test_review_pack_builds_pass_guard_and_outputs(tmp_path, monkeypatch) -> None:
    review_root = tmp_path / "review"
    forward_root = tmp_path / "forward" / "runs"
    packs_root = tmp_path / "packs"
    monkeypatch.setattr(review_pack, "REVIEW_ROOT", review_root)
    monkeypatch.setattr(review_pack, "FORWARD_RUNS_DIR", forward_root)
    monkeypatch.setattr(review_pack, "PACKS_ROOT", packs_root)

    run_id = "forward_r2"
    spec = (RoundSpec("R2", "2026-03-01", "2026-03-02", run_id),)
    for day in ["2026-03-01", "2026-03-02"]:
        _write_forward_entries(forward_root, run_id, day, ["LA001", "LA002", "LA003"])
        _write_day_review(
            review_root,
            "R2",
            day,
            [_entry(day, "LA001", 1), _entry(day, "LA002", 0, from_risk=1), _entry(day, "LA003", 0)],
            [_risk(day, "LA002")],
        )

    entry_df, risk_df, manifest, guard = build_review_pack(round_specs=spec, output_root=packs_root)

    assert guard["status"] == STATUS_PASS
    assert manifest["days"] == 2
    assert manifest["entry_rows"] == 6
    assert manifest["entry_good"] == 2
    assert manifest["entry_bad"] == 4
    assert manifest["risk_bad"] == 2
    assert len(manifest["visual_files"]) == 2
    assert len(entry_df) == 6
    assert len(risk_df) == 2
    assert (packs_root / review_pack.PACK_ID_DEFAULT / "entry" / review_pack.ENTRY_ALL_NAME).exists()
    assert (packs_root / review_pack.PACK_ID_DEFAULT / "riskgate" / review_pack.RISKGATE_ALL_NAME).exists()
    assert (packs_root / review_pack.PACK_ID_DEFAULT / review_pack.GUARD_NAME).exists()
    assert manifest["no_training"] is True
    assert manifest["no_forward"] is True


def test_review_pack_guard_fails_good_and_risk_conflict(tmp_path, monkeypatch) -> None:
    review_root = tmp_path / "review"
    forward_root = tmp_path / "forward" / "runs"
    packs_root = tmp_path / "packs"
    monkeypatch.setattr(review_pack, "REVIEW_ROOT", review_root)
    monkeypatch.setattr(review_pack, "FORWARD_RUNS_DIR", forward_root)
    monkeypatch.setattr(review_pack, "PACKS_ROOT", packs_root)

    run_id = "forward_r2"
    day = "2026-03-01"
    spec = (RoundSpec("R2", day, day, run_id),)
    _write_forward_entries(forward_root, run_id, day, ["LA001"])
    _write_day_review(review_root, "R2", day, [_entry(day, "LA001", 1)], [_risk(day, "LA001")])

    _entry_df, _risk_df, _manifest, guard = build_review_pack(
        pack_id="conflict_pack",
        round_specs=spec,
        output_root=packs_root,
        strict=False,
    )

    assert guard["status"] == STATUS_FAIL
    failed = {item["check"] for item in guard["failed_checks"]}
    assert "no_good_vs_risk_conflicts" in failed
    assert "risk_bad_also_entry_bad" in failed
