from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd


STATUS_CURRENT = "CURRENT_TZ_ENTRY_ML_TRAIN_1_14_FORWARD_15_PLUS_NO_TP_NO_API"
PROJECT_ROOT = Path(__file__).resolve().parents[2]

TRAIN_START_DAY = "2026-05-01"
TRAIN_END_DAY = "2026-05-14"
FORWARD_START_DAY = "2026-05-15"
FORWARD_END_DAY = "2026-05-20"

STAS5_ROOT = PROJECT_ROOT / "STAS5_ML_CORE"
STAS5_ARTIFACTS_DIR = STAS5_ROOT / "artifacts"

DEFAULT_MANUAL_LABEL_DIR = (
    PROJECT_ROOT
    / "STAS4_FEATURE_HYPOTHESIS_REVIEW"
    / "density_structure_20260501_20260514_combo_spectrum"
    / "manual_labels"
)
DEFAULT_STAS2_TRAIN_RUN_DIR = (
    PROJECT_ROOT
    / "STAS2_MARKET_PHASE_REVIEW"
    / "runs"
    / "stas2_20260501_20260514_from_stas1_carry48_full_v1_20260709_142757"
)
DEFAULT_STAS1_TRAIN_RUN_DIR = (
    PROJECT_ROOT
    / "STAS1_GOOD_LOW_REVIEW"
    / "runs"
    / "stas1_20260501_20260514_carry48_for_stas2_v1_20260709_135847"
)

LEDGER_BASENAME = "stas5_ml_ledger_20260501_20260514_v0"
FEATURE_BASENAME = "stas5_feature_snapshot_20260501_20260514_v0"
MODEL_BASENAME = "stas5_entry_ranker_20260501_20260514_v0"

DEFAULT_LEDGER_PATH = STAS5_ARTIFACTS_DIR / "ledger" / f"{LEDGER_BASENAME}.csv"
DEFAULT_LEDGER_MANIFEST_PATH = STAS5_ARTIFACTS_DIR / "ledger" / f"{LEDGER_BASENAME}.manifest.json"
DEFAULT_FEATURE_PATH = STAS5_ARTIFACTS_DIR / "features" / f"{FEATURE_BASENAME}.csv"
DEFAULT_FEATURE_MANIFEST_PATH = STAS5_ARTIFACTS_DIR / "features" / f"{FEATURE_BASENAME}.manifest.json"
DEFAULT_GUARD_REPORT_PATH = STAS5_ARTIFACTS_DIR / "guard" / "stas5_leakage_guard_20260501_20260514_v0.json"
DEFAULT_AUDIT_REPORT_PATH = STAS5_ARTIFACTS_DIR / "audit" / "STAS5_PRE_ML_AUDIT_20260501_20260514_RU.md"
DEFAULT_AUDIT_JSON_PATH = STAS5_ARTIFACTS_DIR / "audit" / "stas5_pre_ml_audit_20260501_20260514_v0.json"
DEFAULT_MODEL_DIR = STAS5_ARTIFACTS_DIR / "model"
DEFAULT_MODEL_PATH = DEFAULT_MODEL_DIR / f"{MODEL_BASENAME}.joblib"
DEFAULT_MODEL_MANIFEST_PATH = DEFAULT_MODEL_DIR / f"{MODEL_BASENAME}.manifest.json"
DEFAULT_TRAIN_PREDICTIONS_PATH = DEFAULT_MODEL_DIR / f"{MODEL_BASENAME}.train_predictions.csv"

JOIN_KEYS = ["day", "candidate_id", "record_id"]

LABEL_COLUMNS = [
    "human_label",
    "label_status",
    "label_source",
    "yellow_x",
    "yellow_x_role",
    "yellow_x_conflict",
]

METADATA_COLUMNS = [
    "day",
    "candidate_id",
    "record_id",
    "anchor_time_utc",
    "entry_time_utc",
    "entry_open_price",
    "entry_price_5bps",
    "anchor_low_price",
    "source_stas1_run",
    "source_stas2_run",
    "source_manual_label_file",
    "context_max_open_time_utc",
]

FORBIDDEN_FEATURE_PATTERNS = [
    r"future",
    r"target_up",
    r"review_label",
    r"outcome_status",
    r"is_good_stas1_review",
    r"(^|_)hit_",
    r"target_1pct",
    r"time_to_",
    r"hold_minutes",
    r"carried_overnight",
    r"mfe",
    r"mae",
    r"post_entry",
    r"ideal_review_tp_pct",
    r"max_feasible_review_tp_pct",
    r"yellow",
    r"strategy_vote",
    r"strategy_cut",
    r"would_cut",
    r"old_removed",
    r"new_candidate",
    r"hard_cut",
    r"hard_filter",
    r"final_decision",
    r"trading_permission",
    r"stas3",
    r"(^|_)tp($|_)",
    r"exit",
    r"entry_candle",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def rel(path: Path, root: Path = PROJECT_ROOT) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except Exception:
        return path.as_posix()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return rel(value)
    if isinstance(value, (pd.Timestamp, datetime)):
        ts = pd.Timestamp(value)
        if ts.tzinfo is None:
            ts = ts.tz_localize("UTC")
        return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        import numpy as np

        if isinstance(value, (np.integer,)):
            return int(value)
        if isinstance(value, (np.floating,)):
            return float(value)
        if isinstance(value, (np.bool_,)):
            return bool(value)
    except Exception:
        pass
    return str(value)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=json_default) + "\n", encoding="utf-8")


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def write_csv(path: Path, rows: Iterable[dict[str, Any]], columns: list[str] | None = None) -> None:
    ensure_parent(path)
    rows_list = list(rows)
    fieldnames = list(columns or [])
    for row in rows_list:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows_list:
            out = {}
            for key in fieldnames:
                value = row.get(key, "")
                if isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False, sort_keys=True)
                out[key] = value
            writer.writerow(out)


def iter_days(start_day: str, end_day: str) -> list[str]:
    start = pd.Timestamp(start_day)
    end = pd.Timestamp(end_day)
    if end < start:
        raise ValueError("end_day must be >= start_day")
    return [item.strftime("%Y-%m-%d") for item in pd.date_range(start, end, freq="D")]


def compact_day(day: str) -> str:
    return str(day).replace("-", "")


def normalize_day(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return pd.Timestamp(text).strftime("%Y-%m-%d")


def normalize_ts(value: Any) -> str:
    text = str(value or "").strip()
    if not text or text.lower() == "nan":
        return ""
    ts = pd.Timestamp(text)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def to_int_flag(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, bool):
        return int(value)
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "keep", "x"}:
        return 1
    return 0


def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return to_int_flag(value) == 1


def label_status_from_human_label(label: Any) -> str:
    text = str(label or "").strip().upper()
    if text.endswith("_APPROVED"):
        return "APPROVED"
    if text.endswith("_DRAFT"):
        return "DRAFT"
    return "UNKNOWN"


def is_keep_label(label: Any) -> bool:
    return str(label or "").strip().upper().startswith("KEEP")


def is_cut_label(label: Any) -> bool:
    return str(label or "").strip().upper().startswith("CUT")


def label_target(label: Any) -> int | None:
    if is_keep_label(label):
        return 1
    if is_cut_label(label):
        return 0
    return None


def forbidden_feature_matches(columns: Iterable[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for column in columns:
        text = str(column)
        hits = [pattern for pattern in FORBIDDEN_FEATURE_PATTERNS if re.search(pattern, text, flags=re.IGNORECASE)]
        if hits:
            out[text] = hits
    return out


def is_forbidden_feature_column(column: str) -> bool:
    return bool(forbidden_feature_matches([column]))


def load_manifest_feature_columns(manifest_path: Path) -> list[str]:
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    columns = payload.get("feature_columns") or payload.get("model_feature_columns") or []
    return [str(item) for item in columns]


def default_expected_train_counts() -> dict[str, int]:
    return {
        "rows": 972,
        "KEEP_DRAFT": 115,
        "CUT_DRAFT": 857,
        "KEEP_DRAFT_yellow_x": 30,
    }


def score_to_decision(score: float, *, enter_threshold: float = 0.65, unsure_threshold: float = 0.45) -> str:
    value = float(score)
    if value >= float(enter_threshold):
        return "ENTER"
    if value >= float(unsure_threshold):
        return "UNSURE"
    return "SKIP"
