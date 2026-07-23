from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import (
    PROJECT_ROOT,
    STAS5_ARTIFACTS_DIR,
    compact_day,
    iter_days,
    normalize_day,
    normalize_ts,
    read_csv,
    rel,
    utc_now,
    write_json,
)


STATUS = "STAS5_V3_USER_REVIEW_LEDGER_READY_REVIEW_16_20_NO_TP_NO_API_NO_STAS3"
DEFAULT_REVIEW_ROOT = STAS5_ARTIFACTS_DIR / "v2" / "user_review"
DEFAULT_FORWARD_ROOT = STAS5_ARTIFACTS_DIR / "v2" / "forward"
DEFAULT_FORWARD_ALL_PREDICTIONS_PATH = DEFAULT_FORWARD_ROOT / "STAS5_V2_FORWARD_ALL_PREDICTIONS_20260515_20260520.csv"
DEFAULT_V3_USER_REVIEW_DIR = STAS5_ARTIFACTS_DIR / "v3" / "user_review"
DEFAULT_V3_USER_REVIEW_LEDGER_PATH = (
    DEFAULT_V3_USER_REVIEW_DIR / "STAS5_V3_USER_REVIEW_LEDGER_20260516_20260520.csv"
)
DEFAULT_V3_USER_REVIEW_LEDGER_MANIFEST_PATH = DEFAULT_V3_USER_REVIEW_LEDGER_PATH.with_suffix(".manifest.json")

TRAIN_LABEL_BY_USER_LABEL = {
    "USER_GOOD_ENTRY": "KEEP_APPROVED",
    "USER_MISSED_GOOD": "KEEP_APPROVED",
    "USER_BAD_ENTRY": "CUT_APPROVED",
}
TRAIN_USAGE_BY_USER_LABEL = {
    "USER_GOOD_ENTRY": "TRAIN_LABEL",
    "USER_MISSED_GOOD": "TRAIN_LABEL_MISSED_BY_CURRENT_MODEL",
    "USER_BAD_ENTRY": "TRAIN_LABEL",
    "USER_NO_CANDIDATE_ZONE": "NO_CANDIDATE_AUDIT_ONLY",
}
AUTO_BAD_REASON = "AUTO_BAD_UNMARKED_ENTER_UNSURE"


def _review_file(review_root: Path, day: str) -> Path:
    compact = compact_day(day)
    return review_root / compact / f"STAS5_V2_USER_REVIEW_SCREEN_DRAFT_{compact}.csv"


def _load_forward_rows(forward_root: Path, all_predictions_path: Path, *, start_day: str, end_day: str) -> pd.DataFrame:
    if all_predictions_path.exists():
        forward = read_csv(all_predictions_path)
    else:
        parts: list[pd.DataFrame] = []
        for day in iter_days(start_day, end_day):
            compact = compact_day(day)
            path = forward_root / compact / f"STAS5_V2_FORWARD_ENTRIES_{compact}.csv"
            if path.exists():
                parts.append(read_csv(path))
        if not parts:
            raise FileNotFoundError(f"forward predictions not found: {all_predictions_path}")
        forward = pd.concat(parts, ignore_index=True, sort=False)
    forward = forward.copy()
    forward["day"] = forward["day"].map(normalize_day)
    forward["candidate_id"] = forward["candidate_id"].astype(str)
    forward["record_id"] = forward["record_id"].astype(str)
    forward["entry_time_utc"] = forward["entry_time_utc"].map(normalize_ts)
    days = set(iter_days(start_day, end_day))
    return forward[forward["day"].isin(days)].copy()


def _load_review_rows(review_root: Path, *, start_day: str, end_day: str) -> tuple[pd.DataFrame, list[str]]:
    frames: list[pd.DataFrame] = []
    missing: list[str] = []
    for day in iter_days(start_day, end_day):
        path = _review_file(review_root, day)
        if not path.exists():
            missing.append(rel(path))
            continue
        df = read_csv(path)
        df["source_review_file"] = rel(path)
        frames.append(df)
    if not frames:
        raise FileNotFoundError(f"user review CSV files not found under {review_root}")
    review = pd.concat(frames, ignore_index=True, sort=False)
    review["day"] = review["day"].map(normalize_day)
    review["candidate_id"] = review["candidate_id"].astype(str)
    review["entry_time_utc"] = review["entry_time_utc"].map(normalize_ts)
    review["user_review_label"] = review["user_review_label"].astype(str).str.strip().str.upper()
    return review, missing


def _forward_lookup(forward: pd.DataFrame) -> dict[tuple[str, str], pd.Series]:
    duplicates = forward.duplicated(["day", "candidate_id"], keep=False)
    if int(duplicates.sum()):
        dup = forward.loc[duplicates, ["day", "candidate_id", "record_id"]].head(10).to_dict("records")
        raise ValueError(f"duplicate forward candidate ids: {dup}")
    return {(str(row.day), str(row.candidate_id)): row for row in forward.itertuples(index=False)}


def _row_from_review(review_row: pd.Series, forward_row: pd.Series | None) -> dict[str, Any]:
    user_label = str(review_row.get("user_review_label") or "").strip().upper()
    no_candidate = user_label == "USER_NO_CANDIDATE_ZONE"
    training_label = TRAIN_LABEL_BY_USER_LABEL.get(user_label, "")
    train_usage = TRAIN_USAGE_BY_USER_LABEL.get(user_label, "AUDIT_ONLY_UNKNOWN_LABEL")
    return {
        "day": normalize_day(review_row.get("day")),
        "candidate_id": str(review_row.get("candidate_id") or ""),
        "record_id": "" if forward_row is None else str(forward_row.get("record_id") or ""),
        "entry_time_utc": normalize_ts(review_row.get("entry_time_utc")),
        "entry_open_price": "" if forward_row is None else forward_row.get("entry_open_price", ""),
        "entry_price_5bps": "" if forward_row is None else forward_row.get("entry_price_5bps", ""),
        "current_ml_decision": str(review_row.get("current_ml_decision") or ("" if forward_row is None else forward_row.get("ML_DECISION_V2", ""))),
        "current_ml_score": review_row.get("current_ml_score", "" if forward_row is None else forward_row.get("ML_KEEP_SCORE_V2", "")),
        "user_review_label": user_label,
        "user_review_reason": str(review_row.get("user_review_reason") or ""),
        "user_note": str(review_row.get("notes") or ""),
        "training_label": training_label,
        "label_status": "APPROVED" if training_label else ("AUDIT_ONLY" if no_candidate else "UNKNOWN"),
        "label_source": "STAS5_V3_USER_SCREEN_REVIEW",
        "train_usage": train_usage,
        "is_auto_bad_unmarked": 0,
        "source_review_file": str(review_row.get("source_review_file") or ""),
        "source_forward_csv": "" if forward_row is None else str(forward_row.get("__source_forward_csv", "")),
    }


def _row_from_auto_bad(forward_row: pd.Series) -> dict[str, Any]:
    return {
        "day": normalize_day(forward_row.get("day")),
        "candidate_id": str(forward_row.get("candidate_id") or ""),
        "record_id": str(forward_row.get("record_id") or ""),
        "entry_time_utc": normalize_ts(forward_row.get("entry_time_utc")),
        "entry_open_price": forward_row.get("entry_open_price", ""),
        "entry_price_5bps": forward_row.get("entry_price_5bps", ""),
        "current_ml_decision": str(forward_row.get("ML_DECISION_V2") or ""),
        "current_ml_score": forward_row.get("ML_KEEP_SCORE_V2", ""),
        "user_review_label": "USER_BAD_ENTRY",
        "user_review_reason": AUTO_BAD_REASON,
        "user_note": "Авто-CUT: ENTER/UNSURE был на графике, но пользователь не подчеркнул его как рабочий вход.",
        "training_label": "CUT_APPROVED",
        "label_status": "APPROVED",
        "label_source": "STAS5_V3_AUTO_BAD_FROM_UNMARKED_FORWARD_SCREEN",
        "train_usage": "TRAIN_LABEL_AUTO_BAD_UNMARKED_ENTER_UNSURE",
        "is_auto_bad_unmarked": 1,
        "source_review_file": "",
        "source_forward_csv": str(forward_row.get("__source_forward_csv", "")),
    }


def build_v3_user_review_ledger(
    *,
    review_root: Path = DEFAULT_REVIEW_ROOT,
    forward_root: Path = DEFAULT_FORWARD_ROOT,
    all_predictions_path: Path = DEFAULT_FORWARD_ALL_PREDICTIONS_PATH,
    start_day: str = "2026-05-16",
    end_day: str = "2026-05-20",
    output_csv: Path = DEFAULT_V3_USER_REVIEW_LEDGER_PATH,
    manifest_path: Path = DEFAULT_V3_USER_REVIEW_LEDGER_MANIFEST_PATH,
    strict: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    forward = _load_forward_rows(forward_root, all_predictions_path, start_day=start_day, end_day=end_day)
    forward["__source_forward_csv"] = rel(all_predictions_path if all_predictions_path.exists() else forward_root)
    review, missing_review_files = _load_review_rows(review_root, start_day=start_day, end_day=end_day)
    lookup = _forward_lookup(forward)

    rows: list[dict[str, Any]] = []
    missing_review_candidates: list[dict[str, str]] = []
    explicit_keys: set[tuple[str, str]] = set()
    for _, review_row in review.iterrows():
        day = normalize_day(review_row.get("day"))
        candidate_id = str(review_row.get("candidate_id") or "")
        user_label = str(review_row.get("user_review_label") or "").strip().upper()
        key = (day, candidate_id)
        explicit_keys.add(key)
        if user_label == "USER_NO_CANDIDATE_ZONE":
            rows.append(_row_from_review(review_row, None))
            continue
        forward_row = lookup.get(key)
        if forward_row is None:
            missing_review_candidates.append({"day": day, "candidate_id": candidate_id})
            rows.append(_row_from_review(review_row, None))
            continue
        rows.append(_row_from_review(review_row, pd.Series(forward_row._asdict())))

    decisions = forward["ML_DECISION_V2"].astype(str).str.upper()
    for _, forward_row in forward[decisions.isin(["ENTER", "UNSURE"])].iterrows():
        key = (normalize_day(forward_row.get("day")), str(forward_row.get("candidate_id") or ""))
        if key in explicit_keys:
            continue
        rows.append(_row_from_auto_bad(forward_row))

    ledger = pd.DataFrame(rows)
    if not ledger.empty:
        ledger = ledger.sort_values(["day", "entry_time_utc", "candidate_id"], kind="stable").reset_index(drop=True)

    train_rows = ledger[ledger["train_usage"].astype(str).str.startswith("TRAIN_LABEL")].copy()
    duplicate_train_keys = int(train_rows.duplicated(["day", "candidate_id", "record_id"]).sum()) if not train_rows.empty else 0
    train_label_counts = Counter(train_rows["training_label"].astype(str))
    user_label_counts = Counter(ledger["user_review_label"].astype(str))
    per_day = {
        day: {
            "rows": int(len(group)),
            "train_rows": int(group["train_usage"].astype(str).str.startswith("TRAIN_LABEL").sum()),
            "labels": dict(Counter(group["user_review_label"].astype(str))),
            "training_labels": dict(Counter(group["training_label"].astype(str))),
        }
        for day, group in ledger.groupby("day", sort=True)
    }

    status_pass = (
        not missing_review_files
        and not missing_review_candidates
        and duplicate_train_keys == 0
        and int(train_label_counts.get("KEEP_APPROVED", 0)) > 0
        and int(train_label_counts.get("CUT_APPROVED", 0)) > 0
    )
    manifest = {
        "status": "PASS" if status_pass else "FAIL",
        "pipeline_status": STATUS,
        "created_utc": utc_now(),
        "review_window": {"start_day": normalize_day(start_day), "end_day": normalize_day(end_day)},
        "excluded_days": ["2026-05-15"],
        "forward_source_path": rel(all_predictions_path),
        "review_root": rel(review_root),
        "output_csv": rel(output_csv),
        "manifest_path": rel(manifest_path),
        "rows": int(len(ledger)),
        "train_rows": int(len(train_rows)),
        "user_label_counts": dict(user_label_counts),
        "training_label_counts": dict(train_label_counts),
        "auto_bad_unmarked_enter_unsure": int(ledger.get("is_auto_bad_unmarked", pd.Series(dtype=int)).astype(int).sum()),
        "per_day": per_day,
        "checks": {
            "missing_review_files": missing_review_files,
            "missing_review_candidates": missing_review_candidates,
            "duplicate_train_keys": duplicate_train_keys,
            "forward_rows_in_window": int(len(forward)),
        },
        "guardrails": [
            "2026_05_15_excluded_until_user_review_finalized",
            "user_good_and_user_missed_good_are_keep_approved",
            "user_bad_and_unmarked_enter_unsure_are_cut_approved",
            "skip_rows_are_not_auto_bad_unless_user_marked_them",
            "no_candidate_zones_are_detector_gap_audit_only_not_train_rows",
            "current_ml_score_decision_are_metadata_not_features",
        ],
    }
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(output_csv, index=False, encoding="utf-8-sig")
    write_json(manifest_path, manifest)
    if strict and manifest["status"] != "PASS":
        raise ValueError(f"STAS5 V3 user review ledger failed checks: {manifest['checks']}")
    return ledger, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build STAS5 V3 user-review ledger from 2026-05-16..2026-05-20 screenshots.")
    parser.add_argument("--review-root", default=str(DEFAULT_REVIEW_ROOT))
    parser.add_argument("--forward-root", default=str(DEFAULT_FORWARD_ROOT))
    parser.add_argument("--all-predictions-path", default=str(DEFAULT_FORWARD_ALL_PREDICTIONS_PATH))
    parser.add_argument("--start-day", default="2026-05-16")
    parser.add_argument("--end-day", default="2026-05-20")
    parser.add_argument("--output-csv", default=str(DEFAULT_V3_USER_REVIEW_LEDGER_PATH))
    parser.add_argument("--manifest-path", default=str(DEFAULT_V3_USER_REVIEW_LEDGER_MANIFEST_PATH))
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()
    _ledger, manifest = build_v3_user_review_ledger(
        review_root=Path(args.review_root),
        forward_root=Path(args.forward_root),
        all_predictions_path=Path(args.all_predictions_path),
        start_day=args.start_day,
        end_day=args.end_day,
        output_csv=Path(args.output_csv),
        manifest_path=Path(args.manifest_path),
        strict=not args.no_strict,
    )
    print(
        {
            "status": manifest["status"],
            "rows": manifest["rows"],
            "train_rows": manifest["train_rows"],
            "training_label_counts": manifest["training_label_counts"],
            "auto_bad_unmarked_enter_unsure": manifest["auto_bad_unmarked_enter_unsure"],
            "output_csv": manifest["output_csv"],
        }
    )
    return 0 if manifest["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
