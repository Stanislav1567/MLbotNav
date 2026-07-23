from __future__ import annotations

import pandas as pd

from mlbotnav.stas5_ml_ledger_builder import build_ledger


def test_build_ledger_preserves_keep_yellow_conflict(tmp_path):
    label_dir = tmp_path / "labels"
    stas2_dir = tmp_path / "stas2"
    label_dir.mkdir()
    stas2_dir.mkdir()

    labels = pd.DataFrame(
        [
            {
                "day": "2026-05-01",
                "candidate_id": "LA001",
                "record_id": "G1P_20260501_LA001",
                "anchor_time_utc": "2026-05-01T00:00:00Z",
                "entry_time_utc": "2026-05-01T00:01:00Z",
                "anchor_low_price": 99.0,
                "entry_open_price": 100.0,
                "human_label": "KEEP_DRAFT",
                "label_source": "unit",
                "stas4_density_structure_yellow_x": 1,
                "notes": "",
            },
            {
                "day": "2026-05-01",
                "candidate_id": "LA002",
                "record_id": "G1P_20260501_LA002",
                "anchor_time_utc": "2026-05-01T00:10:00Z",
                "entry_time_utc": "2026-05-01T00:11:00Z",
                "anchor_low_price": 98.0,
                "entry_open_price": 99.0,
                "human_label": "CUT_DRAFT",
                "label_source": "unit",
                "stas4_density_structure_yellow_x": 1,
                "notes": "",
            },
        ]
    )
    labels.to_csv(label_dir / "LABELS_20260501_ALL_ENTRIES_DRAFT.csv", index=False, encoding="utf-8-sig")
    stas2 = pd.DataFrame(
        [
            {
                "day_utc": "2026-05-01",
                "candidate_id": "LA001",
                "record_id": "G1P_20260501_LA001",
                "anchor_time_utc": "2026-05-01T00:00:00Z",
                "entry_time_utc": "2026-05-01T00:01:00Z",
                "entry_price_5bps": 100.05,
                "source_run": "stas1/unit",
            },
            {
                "day_utc": "2026-05-01",
                "candidate_id": "LA002",
                "record_id": "G1P_20260501_LA002",
                "anchor_time_utc": "2026-05-01T00:10:00Z",
                "entry_time_utc": "2026-05-01T00:11:00Z",
                "entry_price_5bps": 99.0495,
                "source_run": "stas1/unit",
            },
        ]
    )
    stas2.to_csv(stas2_dir / "STAS2_RECORDS.csv", index=False, encoding="utf-8-sig")

    ledger, manifest = build_ledger(
        manual_label_dir=label_dir,
        stas2_run_dir=stas2_dir,
        output_csv=tmp_path / "ledger.csv",
        manifest_path=tmp_path / "ledger.manifest.json",
        start_day="2026-05-01",
        end_day="2026-05-01",
        expected_counts={"rows": 2, "KEEP_DRAFT": 1, "CUT_DRAFT": 1, "KEEP_DRAFT_yellow_x": 1},
    )

    assert manifest["status"] == "PASS"
    assert len(ledger) == 2
    assert int(ledger["yellow_x_conflict"].sum()) == 1
    assert set(ledger["yellow_x_role"]) == {"AUDIT_ONLY"}
    assert ledger.loc[ledger["candidate_id"] == "LA001", "entry_price_5bps"].iloc[0] == 100.05
