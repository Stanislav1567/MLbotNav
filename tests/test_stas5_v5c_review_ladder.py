from __future__ import annotations

import pandas as pd
import pytest

import mlbotnav.stas5_v5c_review_ladder as review_ladder
from mlbotnav.stas5_v5c_review_ladder import build_review_ladder, normalize_candidate_id, parse_review_text


def test_normalize_candidate_id_accepts_short_forms() -> None:
    assert normalize_candidate_id("7") == "LA007"
    assert normalize_candidate_id("LA7") == "LA007"
    assert normalize_candidate_id("0.8") == "LA008"
    assert normalize_candidate_id("0-20") == "LA020"


def test_parse_review_text_splits_entry_and_risk_layers() -> None:
    items = parse_review_text(
        "5 крестик хорошо; 14 плохо; 22 ромбик хорошо; 47 крестик вход; "
        "40 риск плохо; 47 треугольник риск плохо; 59 хорошо"
    )

    by_id_layer = {(item.candidate_id, item.entry_review_label or item.risk_review_label): item for item in items}

    assert by_id_layer[("LA005", "GOOD_MISSED")].entry_y_action == "promote_to_good"
    assert by_id_layer[("LA014", "BAD")].entry_y_action == "keep_bad"
    assert by_id_layer[("LA022", "GOOD")].marker_user == "yellow_diamond"
    assert by_id_layer[("LA047", "GOOD_MISSED")].entry_y_action == "promote_to_good"
    assert by_id_layer[("LA040", "RISK_BAD")].entry_review_label == ""
    assert by_id_layer[("LA047", "RISK_BAD")].marker_user == "green_triangle"
    assert by_id_layer[("LA059", "GOOD")].risk_review_label == ""


def test_risk_good_is_rejected() -> None:
    with pytest.raises(ValueError, match="risk good"):
        parse_review_text("59 риск хорошо")


def test_build_review_ladder_dry_run_uses_visual_entries(tmp_path) -> None:
    day = "2026-03-18"
    compact = "20260318"
    visual_dir = tmp_path / "visual_review" / compact
    visual_dir.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "day": day,
                "candidate_id": "LA014",
                "record_id": "G1P_20260318_LA014",
                "entry_time_utc": "2026-03-18T03:12:00Z",
                "ENTRY_ML_LIVE_SCORE": 0.4,
                "ENTRY_ML_LIVE_DECISION": "ENTER",
                "entry_price_5bps": 90.0,
            },
            {
                "day": day,
                "candidate_id": "LA022",
                "record_id": "G1P_20260318_LA022",
                "entry_time_utc": "2026-03-18T04:12:00Z",
                "ENTRY_ML_LIVE_SCORE": 0.2,
                "ENTRY_ML_LIVE_DECISION": "WATCH",
                "entry_price_5bps": 89.0,
            },
            {
                "day": day,
                "candidate_id": "LA040",
                "record_id": "G1P_20260318_LA040",
                "entry_time_utc": "2026-03-18T11:12:00Z",
                "ENTRY_ML_LIVE_SCORE": 0.8,
                "ENTRY_ML_LIVE_DECISION": "ENTER",
                "entry_price_5bps": 85.0,
            },
        ]
    ).to_csv(visual_dir / f"STAS5_V5_FORWARD_VISUAL_REVIEW_ENTRIES_{compact}.csv", index=False, encoding="utf-8-sig")

    result = build_review_ladder(
        day=day,
        round_id="R4",
        review_text="14 плохо; 22 ромбик хорошо; 40 риск плохо",
        forward_run_dir=str(tmp_path),
        dry_run=True,
    )

    assert result["status"] == "V5C_REVIEW_LADDER_DRAFT_NO_TRAINING"
    assert result["entry_good_ids"] == ["LA022"]
    assert result["entry_bad_ids"] == ["LA014", "LA040"]
    assert result["risk_bad_ids"] == ["LA040"]
    assert result["risk_bad_y_count"] == 1
    assert result["risk_bad_also_entry_bad_ids"] == ["LA040"]
    assert result["dry_run"] is True


def test_build_review_ladder_copies_all_entries_png(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(review_ladder, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(review_ladder, "V5C_ROOT", tmp_path / "out")
    day = "2026-03-18"
    compact = "20260318"
    visual_dir = tmp_path / "forward" / "visual_review" / compact
    visual_dir.mkdir(parents=True)
    ohlcv_dir = tmp_path / "data" / "core" / "bybit_ohlcv" / f"dt={day}" / "tf=1m" / "symbol=SOLUSDT"
    ohlcv_dir.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "open_time_utc": "2026-03-18T04:11:00Z",
                "close_time_utc": "2026-03-18T04:11:59Z",
                "open": 88.8,
                "high": 89.2,
                "low": 88.7,
                "close": 89.0,
                "volume": 1000,
            },
            {
                "open_time_utc": "2026-03-18T04:12:00Z",
                "close_time_utc": "2026-03-18T04:12:59Z",
                "open": 89.0,
                "high": 89.3,
                "low": 88.9,
                "close": 89.1,
                "volume": 1200,
            },
            {
                "open_time_utc": "2026-03-18T04:13:00Z",
                "close_time_utc": "2026-03-18T04:13:59Z",
                "open": 89.1,
                "high": 89.4,
                "low": 89.0,
                "close": 89.2,
                "volume": 900,
            },
        ]
    ).to_csv(ohlcv_dir / "part-final.csv", index=False)
    (visual_dir / f"STAS5_V5_FORWARD_VISUAL_REVIEW_{compact}_ENTER_ARROWS.png").write_bytes(b"png bytes")
    pd.DataFrame(
        [
            {
                "day": day,
                "candidate_id": "LA022",
                "record_id": "G1P_20260318_LA022",
                "entry_time_utc": "2026-03-18T04:12:00Z",
                "ENTRY_ML_LIVE_SCORE": 0.2,
                "ENTRY_ML_LIVE_DECISION": "WATCH",
                "entry_price_5bps": 89.0,
            },
            {
                "day": day,
                "candidate_id": "LA040",
                "record_id": "G1P_20260318_LA040",
                "entry_time_utc": "2026-03-18T04:13:00Z",
                "ENTRY_ML_LIVE_SCORE": 0.8,
                "ENTRY_ML_LIVE_DECISION": "ENTER",
                "entry_price_5bps": 89.1,
            }
        ]
    ).to_csv(visual_dir / f"STAS5_V5_FORWARD_VISUAL_REVIEW_ENTRIES_{compact}.csv", index=False, encoding="utf-8-sig")

    result = build_review_ladder(
        day=day,
        round_id="R4",
        review_text="22 ромбик хорошо; 40 риск плохо",
        forward_run_dir=str(tmp_path / "forward"),
    )

    day_review_dir = tmp_path / "out" / "review" / "r4_user_review" / compact
    archive_dir = day_review_dir / "_visual_archive"
    out_png = archive_dir / f"STAS5_V5C_R4_USER_REVIEW_{compact}_DRAFT_ALL_ENTRIES.png"
    annotated_png = archive_dir / f"STAS5_V5C_R4_USER_REVIEW_{compact}_DRAFT_ANNOTATED.png"
    current_png = day_review_dir / f"STAS5_V5C_R4_USER_REVIEW_{compact}_CURRENT_REVIEW.png"
    visual_manifest = day_review_dir / f"STAS5_V5C_R4_USER_REVIEW_{compact}_CURRENT_VISUAL_MANIFEST_V1.json"
    assert result["outputs"]["all_entries_png"].endswith(f"STAS5_V5C_R4_USER_REVIEW_{compact}_DRAFT_ALL_ENTRIES.png")
    assert out_png.read_bytes() == b"png bytes"
    assert result["outputs"]["annotated_png"].endswith(f"STAS5_V5C_R4_USER_REVIEW_{compact}_DRAFT_ANNOTATED.png")
    assert result["annotated_png_created"] is True
    assert annotated_png.exists()
    assert result["outputs"]["current_review_png"].endswith(f"STAS5_V5C_R4_USER_REVIEW_{compact}_CURRENT_REVIEW.png")
    assert current_png.exists()
    assert visual_manifest.exists()
    assert sorted(path.name for path in day_review_dir.glob("*.png")) == [current_png.name]
    assert result["entry_bad_ids"] == ["LA040"]
    assert result["risk_bad_y_count"] == 1
    assert result["risk_bad_also_entry_bad_ids"] == ["LA040"]

    entry_csv = tmp_path / "out" / "review" / "r4_user_review" / compact / f"STAS5_V5C_R4_USER_REVIEW_{compact}_DRAFT.csv"
    entry_rows = pd.read_csv(entry_csv, encoding="utf-8-sig")
    risk_entry = entry_rows.loc[entry_rows["candidate_id"].eq("LA040")].iloc[0]
    assert int(risk_entry["entry_y"]) == 0
    assert int(risk_entry["entry_from_risk_bad"]) == 1

    risk_csv = tmp_path / "out" / "review" / "r4_user_review" / compact / f"STAS5_V5C_R4_USER_RISKGATE_REVIEW_{compact}_DRAFT.csv"
    risk_rows = pd.read_csv(risk_csv, encoding="utf-8-sig")
    assert risk_rows.loc[0, "candidate_id"] == "LA040"
    assert int(risk_rows.loc[0, "risk_bad_y"]) == 1
    assert int(risk_rows.loc[0, "r4_risk_bad_y"]) == 1
