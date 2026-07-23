from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import (
    FORWARD_END_DAY,
    FORWARD_START_DAY,
    JOIN_KEYS,
    STAS5_ARTIFACTS_DIR,
    iter_days,
    normalize_day,
    read_csv,
    rel,
    to_bool,
    utc_now,
    write_json,
)

STATUS = "STAS5_V2_FORWARD_ERROR_LEDGER_READY_AUDIT_ONLY_NO_TRAINING_NO_TP_NO_API"
DEFAULT_FORWARD_ROOT = STAS5_ARTIFACTS_DIR / "forward"
DEFAULT_USER_REVIEW_ROOT = STAS5_ARTIFACTS_DIR / "v2" / "user_review"
DEFAULT_V2_AUDIT_DIR = STAS5_ARTIFACTS_DIR / "v2_audit"
DEFAULT_V2_COMBO_FORWARD_FEATURE_PATH = (
    STAS5_ARTIFACTS_DIR / "v2" / "features" / "stas5_v2_combo_features_20260515_20260520_forward_v0.csv"
)
DEFAULT_FORWARD_ERROR_LEDGER_PATH = DEFAULT_V2_AUDIT_DIR / "stas5_forward_error_ledger_20260515_20260520_v0.csv"
DEFAULT_FORWARD_ERROR_LEDGER_MANIFEST_PATH = (
    DEFAULT_V2_AUDIT_DIR / "stas5_forward_error_ledger_20260515_20260520_v0.manifest.json"
)

REQUIRED_OUTPUT_COLUMNS = [
    "day",
    "candidate_id",
    "entry_time",
    "ML_DECISION_V1",
    "ML_KEEP_SCORE_V1",
    "visual_user_review",
    "postfact_hit_0p5",
    "postfact_hit_1p0",
    "postfact_max_up_pct",
    "postfact_max_drawdown_pct",
    "error_class",
    "error_reason",
    "v2_expected_decision",
]

DIAGNOSTIC_COLUMNS = [
    "record_id",
    "entry_price_5bps",
    "v2_feature_time_utc",
    "v2_feature_available_before_entry",
    "user_note",
    "risk_bucket",
    "risk_primary_reason",
    "risk_reason_flags",
    "stas5_v2_risk_knife_pre_entry",
    "stas5_v2_risk_too_high_in_drop",
    "stas5_v2_risk_weak_bounce_inside_drop",
    "stas5_v2_risk_no_clear_low",
    "stas5_v2_risk_after_spike",
    "stas5_v2_risk_low_volume_confirmation",
    "stas5_v2_risk_drawdown_proxy_score",
    "stas4_v2_combo_short_pressure_score",
    "stas4_v2_combo_long_recovery_score",
    "stas5_v2_gate_long_allowed_final",
    "stas5_v2_gate_bullish_evidence_score",
    "stas5_v2_gate_no_trade_reason_code",
    "audit_no_trade_reason",
    "postfact_usage",
    "ledger_usage",
]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or str(value).strip() == "":
            return default
        out = float(value)
        if pd.isna(out):
            return default
        return out
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or str(value).strip() == "":
            return default
        out = float(value)
        if pd.isna(out):
            return default
        return int(out)
    except Exception:
        return default


def _normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["day"] = out["day"].map(normalize_day)
    out["candidate_id"] = out["candidate_id"].astype(str)
    out["record_id"] = out["record_id"].astype(str)
    return out


def _read_forward_v1_frames(forward_root: Path, start_day: str, end_day: str) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    missing: list[str] = []
    for day in iter_days(start_day, end_day):
        compact = day.replace("-", "")
        path = forward_root / compact / f"STAS5_FORWARD_ENTRIES_{compact}.csv"
        if path.exists():
            frames.append(read_csv(path))
        else:
            missing.append(rel(path))
    if missing:
        raise FileNotFoundError(f"missing forward V1 CSV files: {missing}")
    if not frames:
        raise ValueError("no forward V1 CSV files loaded")
    return _normalize_keys(pd.concat(frames, ignore_index=True))


def _read_user_review_labels(user_review_root: Path, start_day: str, end_day: str) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for day in iter_days(start_day, end_day):
        compact = day.replace("-", "")
        path = user_review_root / compact / f"STAS5_V2_USER_REVIEW_TEMPLATE_{compact}.csv"
        if path.exists():
            frame = read_csv(path)
            if "user_review_label" not in frame.columns:
                frame["user_review_label"] = "PENDING_USER_REVIEW"
            if "user_note" not in frame.columns:
                frame["user_note"] = ""
            if "risk_bucket" not in frame.columns:
                frame["risk_bucket"] = ""
            frames.append(frame[JOIN_KEYS + ["user_review_label", "user_note", "risk_bucket"]])
    if not frames:
        return pd.DataFrame(columns=JOIN_KEYS + ["user_review_label", "user_note", "risk_bucket"])
    return _normalize_keys(pd.concat(frames, ignore_index=True))


def _prepare_v2_payload(v2_forward: pd.DataFrame) -> pd.DataFrame:
    v2 = _normalize_keys(v2_forward)
    rename = {
        "entry_time_utc": "v2_entry_time_utc",
        "feature_time_utc": "v2_feature_time_utc",
        "feature_available_before_entry": "v2_feature_available_before_entry",
    }
    columns = JOIN_KEYS + [
        "entry_time_utc",
        "feature_time_utc",
        "feature_available_before_entry",
        "audit_no_trade_reason",
        "stas5_v2_risk_knife_pre_entry",
        "stas5_v2_risk_too_high_in_drop",
        "stas5_v2_risk_weak_bounce_inside_drop",
        "stas5_v2_risk_no_clear_low",
        "stas5_v2_risk_after_spike",
        "stas5_v2_risk_low_volume_confirmation",
        "stas5_v2_risk_drawdown_proxy_score",
        "stas4_v2_combo_short_pressure_score",
        "stas4_v2_combo_long_recovery_score",
        "stas5_v2_gate_long_allowed_final",
        "stas5_v2_gate_bullish_evidence_score",
        "stas5_v2_gate_no_trade_reason_code",
        "stas4_v2_div_bullish_recent",
        "stas4_v2_div_hidden_bullish_recent",
        "stas4_v2_density_support_score",
        "stas4_v2_structure_support_score",
    ]
    for column in columns:
        if column not in v2.columns:
            v2[column] = pd.NA
    return v2[columns].rename(columns=rename)


def _risk_flags(row: pd.Series) -> list[str]:
    flags: list[str] = []
    allowed = _safe_int(row.get("stas5_v2_gate_long_allowed_final"), 1)
    knife = _safe_float(row.get("stas5_v2_risk_knife_pre_entry"))
    short = _safe_float(row.get("stas4_v2_combo_short_pressure_score"))
    too_high = _safe_int(row.get("stas5_v2_risk_too_high_in_drop"))
    weak_bounce = _safe_int(row.get("stas5_v2_risk_weak_bounce_inside_drop"))
    no_clear_low = _safe_int(row.get("stas5_v2_risk_no_clear_low"))
    after_spike = _safe_int(row.get("stas5_v2_risk_after_spike"))
    low_volume = _safe_int(row.get("stas5_v2_risk_low_volume_confirmation"))
    long_recovery = _safe_float(row.get("stas4_v2_combo_long_recovery_score"))
    bullish_evidence = _safe_float(row.get("stas5_v2_gate_bullish_evidence_score"))
    bull_div = _safe_int(row.get("stas4_v2_div_bullish_recent"))
    hidden_bull_div = _safe_int(row.get("stas4_v2_div_hidden_bullish_recent"))
    density_support = _safe_float(row.get("stas4_v2_density_support_score"))
    structure_support = _safe_float(row.get("stas4_v2_structure_support_score"))

    if allowed == 0:
        flags.append("GATE_BLOCKED")
    if knife >= 0.55 or short >= 0.80:
        flags.append("FALLING_KNIFE")
    if too_high:
        flags.append("TOO_HIGH")
    if weak_bounce:
        flags.append("WEAK_BOUNCE")
    if no_clear_low:
        flags.append("NO_CLEAR_LOW")
    if after_spike:
        flags.append("AFTER_SPIKE")
    if low_volume:
        flags.append("LOW_VOLUME_CONFIRMATION")

    has_reversal = (
        long_recovery >= 0.50
        or bullish_evidence >= 0.50
        or bull_div == 1
        or hidden_bull_div == 1
        or density_support >= 3
        or structure_support >= 3
    )
    if not has_reversal:
        flags.append("NO_REVERSAL")
    return flags


def _primary_risk_reason(flags: list[str]) -> str:
    for item in ["GATE_BLOCKED", "FALLING_KNIFE", "TOO_HIGH", "NO_REVERSAL", "WEAK_BOUNCE", "NO_CLEAR_LOW"]:
        if item in flags:
            return item
    return "OK"


def _is_user_keep(label: Any) -> bool:
    return str(label or "").strip().upper() == "USER_KEEP_FORWARD_AUDIT"


def _classify_row(row: pd.Series) -> tuple[str, str, str, str, str]:
    decision = str(row.get("ML_DECISION_V1") or "").strip().upper()
    visual = str(row.get("visual_user_review") or "").strip().upper()
    hit_1p0 = to_bool(row.get("postfact_hit_1p0"))
    hit_0p5 = to_bool(row.get("postfact_hit_0p5"))
    max_up = _safe_float(row.get("postfact_max_up_pct"))
    max_dd = _safe_float(row.get("postfact_max_drawdown_pct"))
    score = _safe_float(row.get("ML_KEEP_SCORE_V1"))
    flags = _risk_flags(row)
    primary = _primary_risk_reason(flags)
    user_keep = _is_user_keep(visual)
    good = bool(user_keep or hit_1p0)

    if decision == "ENTER":
        if good:
            error_class = "GREEN_GOOD"
        elif primary in {"GATE_BLOCKED", "FALLING_KNIFE"}:
            error_class = "GREEN_BAD_FALLING_KNIFE"
        elif primary == "TOO_HIGH":
            error_class = "GREEN_BAD_TOO_HIGH"
        else:
            error_class = "GREEN_BAD_NO_REVERSAL"
    elif decision == "UNSURE":
        error_class = "YELLOW_GOOD" if good else "YELLOW_BAD"
    else:
        error_class = "SKIP_MISSED_GOOD" if good else "SKIP_CORRECT"

    if error_class in {"GREEN_GOOD", "YELLOW_GOOD", "SKIP_MISSED_GOOD"}:
        if user_keep or (hit_1p0 and primary == "OK"):
            expected = "ENTER"
        else:
            expected = "UNSURE"
    elif hit_0p5 and primary not in {"GATE_BLOCKED", "FALLING_KNIFE", "TOO_HIGH"} and max_dd > -1.5:
        expected = "UNSURE"
    else:
        expected = "SKIP"

    reason_parts = [
        f"decision={decision or 'UNKNOWN'}",
        f"score={score:.4f}",
        f"visual={visual or 'PENDING_USER_REVIEW'}",
        f"hit0p5={int(hit_0p5)}",
        f"hit1p0={int(hit_1p0)}",
        f"max_up={max_up:.4f}",
        f"max_dd={max_dd:.4f}",
        f"risk={primary}",
    ]
    if flags:
        reason_parts.append("flags=" + "|".join(flags))
    return error_class, "; ".join(reason_parts), expected, primary, "|".join(flags) if flags else "OK"


def build_forward_error_ledger_from_frames(
    *,
    forward_v1: pd.DataFrame,
    v2_forward: pd.DataFrame,
    user_review: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    v1 = _normalize_keys(forward_v1)
    v2_payload = _prepare_v2_payload(v2_forward)
    merged = v1.merge(v2_payload, on=JOIN_KEYS, how="left", indicator=True)
    missing_v2_rows = int((merged["_merge"] != "both").sum())
    merged = merged.drop(columns=["_merge"])

    if user_review is not None and not user_review.empty:
        review = _normalize_keys(user_review)
        merged = merged.merge(review, on=JOIN_KEYS, how="left", suffixes=("", "_user_review"))
    else:
        merged["user_review_label"] = pd.NA
        merged["user_note"] = ""
        merged["risk_bucket"] = ""

    merged["ML_DECISION_V1"] = merged["ML_DECISION"].astype(str)
    merged["ML_KEEP_SCORE_V1"] = pd.to_numeric(merged["ML_KEEP_SCORE"], errors="coerce").round(6)
    merged["entry_time"] = merged["entry_time_utc"].astype(str)
    merged["visual_user_review"] = merged["user_review_label"].fillna("PENDING_USER_REVIEW").replace("", "PENDING_USER_REVIEW")
    merged["user_note"] = merged["user_note"].fillna("")
    merged["risk_bucket"] = merged["risk_bucket"].fillna("")
    merged["postfact_hit_0p5"] = merged["postfact_hit_0p5_pct"].map(to_bool)
    merged["postfact_hit_1p0"] = merged["postfact_hit_1p0_pct"].map(to_bool)
    merged["postfact_max_up_pct"] = pd.to_numeric(merged["postfact_max_up_pct"], errors="coerce").round(6)
    merged["postfact_max_drawdown_pct"] = pd.to_numeric(merged["postfact_max_drawdown_pct"], errors="coerce").round(6)
    merged["ledger_usage"] = "audit_only_not_training_not_threshold_tuning"

    classified = merged.apply(_classify_row, axis=1, result_type="expand")
    classified.columns = ["error_class", "error_reason", "v2_expected_decision", "risk_primary_reason", "risk_reason_flags"]
    merged = pd.concat([merged, classified], axis=1)

    for column in DIAGNOSTIC_COLUMNS:
        if column not in merged.columns:
            merged[column] = ""
    ordered = REQUIRED_OUTPUT_COLUMNS + DIAGNOSTIC_COLUMNS
    out = merged[ordered].sort_values(["day", "entry_time", "record_id"]).reset_index(drop=True)

    decision_counts = Counter(out["ML_DECISION_V1"].astype(str))
    error_counts = Counter(out["error_class"].astype(str))
    expected_counts = Counter(out["v2_expected_decision"].astype(str))
    day_counts = Counter(out["day"].astype(str))
    status_pass = missing_v2_rows == 0 and int(out.duplicated(JOIN_KEYS).sum()) == 0 and len(out) == len(v1)
    manifest = {
        "status": "PASS" if status_pass else "FAIL",
        "pipeline_status": STATUS,
        "created_utc": utc_now(),
        "rows": int(len(out)),
        "source_v1_rows": int(len(v1)),
        "source_v2_rows": int(len(v2_forward)),
        "missing_v2_rows_after_join": missing_v2_rows,
        "duplicate_output_keys": int(out.duplicated(JOIN_KEYS).sum()),
        "day_counts": {str(key): int(value) for key, value in sorted(day_counts.items())},
        "decision_counts_v1": {str(key): int(value) for key, value in sorted(decision_counts.items())},
        "error_class_counts": {str(key): int(value) for key, value in sorted(error_counts.items())},
        "v2_expected_decision_counts": {str(key): int(value) for key, value in sorted(expected_counts.items())},
        "output_columns": ordered,
        "required_contract_columns": REQUIRED_OUTPUT_COLUMNS,
        "guardrails": [
            "forward_error_ledger_is_audit_only",
            "postfact_fields_are_not_features",
            "visual_user_review_is_not_train_label_without_separate_approval",
            "no_threshold_tuning_on_20260515_plus",
            "stas3_tp_exit_not_used",
        ],
    }
    return out, manifest


def build_forward_error_ledger(
    *,
    start_day: str = FORWARD_START_DAY,
    end_day: str = FORWARD_END_DAY,
    forward_root: Path = DEFAULT_FORWARD_ROOT,
    v2_forward_path: Path = DEFAULT_V2_COMBO_FORWARD_FEATURE_PATH,
    user_review_root: Path = DEFAULT_USER_REVIEW_ROOT,
    output_csv: Path = DEFAULT_FORWARD_ERROR_LEDGER_PATH,
    manifest_path: Path = DEFAULT_FORWARD_ERROR_LEDGER_MANIFEST_PATH,
    strict: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if not v2_forward_path.exists():
        raise FileNotFoundError(f"V2 forward feature CSV not found: {v2_forward_path}")
    forward_v1 = _read_forward_v1_frames(forward_root, start_day, end_day)
    v2_forward = read_csv(v2_forward_path)
    user_review = _read_user_review_labels(user_review_root, start_day, end_day)
    ledger, manifest = build_forward_error_ledger_from_frames(
        forward_v1=forward_v1,
        v2_forward=v2_forward,
        user_review=user_review,
    )
    manifest.update(
        {
            "date_range": {"start_day": start_day, "end_day": end_day},
            "forward_root": rel(forward_root),
            "v2_forward_path": rel(v2_forward_path),
            "user_review_root": rel(user_review_root),
            "output_csv": rel(output_csv),
            "manifest_path": rel(manifest_path),
            "user_review_rows_loaded": int(len(user_review)),
        }
    )
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(output_csv, index=False, encoding="utf-8-sig")
    write_json(manifest_path, manifest)
    if strict and manifest["status"] != "PASS":
        raise ValueError(f"STAS5 V2 forward error ledger failed checks: {manifest}")
    return ledger, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Build STAS5 V2 forward error ledger audit-only table.")
    parser.add_argument("--start-day", default=FORWARD_START_DAY)
    parser.add_argument("--end-day", default=FORWARD_END_DAY)
    parser.add_argument("--forward-root", default=str(DEFAULT_FORWARD_ROOT))
    parser.add_argument("--v2-forward-path", default=str(DEFAULT_V2_COMBO_FORWARD_FEATURE_PATH))
    parser.add_argument("--user-review-root", default=str(DEFAULT_USER_REVIEW_ROOT))
    parser.add_argument("--output-csv", default=str(DEFAULT_FORWARD_ERROR_LEDGER_PATH))
    parser.add_argument("--manifest-path", default=str(DEFAULT_FORWARD_ERROR_LEDGER_MANIFEST_PATH))
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()
    _ledger, manifest = build_forward_error_ledger(
        start_day=args.start_day,
        end_day=args.end_day,
        forward_root=Path(args.forward_root),
        v2_forward_path=Path(args.v2_forward_path),
        user_review_root=Path(args.user_review_root),
        output_csv=Path(args.output_csv),
        manifest_path=Path(args.manifest_path),
        strict=not args.no_strict,
    )
    print(
        {
            "status": manifest["status"],
            "rows": manifest["rows"],
            "decision_counts_v1": manifest["decision_counts_v1"],
            "error_class_counts": manifest["error_class_counts"],
            "v2_expected_decision_counts": manifest["v2_expected_decision_counts"],
        }
    )
    return 0 if manifest["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
