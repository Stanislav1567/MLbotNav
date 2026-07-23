from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import (
    PROJECT_ROOT,
    compact_day,
    ensure_parent,
    iter_days,
    normalize_day,
    normalize_ts,
    rel,
    utc_now,
    write_json,
)


STATUS_PASS = "PASS_V5_BATCH_GUARD_READY_FOR_TWO_BLOCK_ML_NO_TRAINING"
STATUS_FAIL = "FAIL_V5_BATCH_GUARD"

DEFAULT_START_DAY = "2026-01-27"
DEFAULT_END_DAY = "2026-02-27"
DEFAULT_EXPECTED_DAYS = 32
DEFAULT_EXPECTED_ROWS = 2596
DEFAULT_EXPECTED_GOOD = 290
DEFAULT_EXPECTED_BAD = 2306
DEFAULT_EXPECTED_FEATURES = 439

TARGET_OR_MANUAL_COLUMNS = {
    "entry_y",
    "entry_y_class",
    "phase_y",
    "phase_y_code",
    "state_y",
    "state_y_code",
    "reason_y",
    "reason_y_code",
    "reason_y_family",
    "entry_label",
    "rank_label",
    "human_label",
    "label_status",
    "label_source",
    "yellow_x",
    "yellow_x_role",
    "yellow_x_conflict",
    "entry_reason_primary",
    "entry_reason_secondary",
    "market_phase_primary",
    "market_phase_secondary",
    "phase_label_status",
    "train_label_binary",
    "train_target_good",
    "train_target_bad_or_no_trade",
    "train_use_default",
    "review_status",
    "phase_segment_id",
    "phase_segment_label",
    "phase_y_source",
    "state_y_source",
    "reason_y_source",
    "targets_are_features",
}

FORBIDDEN_FEATURE_PATTERNS = [
    r"future",
    r"postfact",
    r"(^|_)hit_",
    r"(^|_)tp($|_)",
    r"stas3",
    r"exit",
    r"ml_keep_score",
    r"ml_decision",
    r"manual",
    r"teacher",
    r"phase_y",
    r"state_y",
    r"reason_y",
    r"entry_y",
    r"entry_label",
    r"rank_label",
    r"market_phase",
    r"entry_reason",
    r"full_group",
    r"group_low",
    r"post_candidate",
    r"best_low",
    r"target_up",
    r"outcome",
    r"post_entry",
    r"mfe",
    r"mae",
]


def _v5_root() -> Path:
    return PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5"


def _batch_prefix(start_day: str, end_day: str, family: str = "STAS5_V5") -> str:
    family = str(family or "STAS5_V5").strip().upper()
    return f"{family}_BATCH_{compact_day(start_day)}_{compact_day(end_day)}"


def _day_paths(v5_root: Path, day: str) -> dict[str, Path]:
    day_compact = compact_day(day)
    day_dir = v5_root / "market_passports" / day_compact
    prefix = f"STAS5_V5_MARKET_PASSPORT_{day_compact}"
    return {
        "day_dir": day_dir,
        "csv": day_dir / f"{prefix}_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv",
        "allowlist": day_dir / f"{prefix}_FEATURE_ALLOWLIST_274_PLUS_FULL_CAUSAL_STRUCTURE_V1.json",
        "guard": day_dir / f"{prefix}_FULL_CAUSAL_STRUCTURE_GUARD_V1.json",
    }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_allowlist(path: Path) -> list[str]:
    payload = _load_json(path)
    return [str(column) for column in payload.get("feature_columns", [])]


def _forbidden_feature_matches(feature_columns: list[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for column in feature_columns:
        hits = [
            pattern
            for pattern in FORBIDDEN_FEATURE_PATTERNS
            if re.search(pattern, column, flags=re.IGNORECASE)
        ]
        if hits:
            out[column] = hits
    return out


def _check(name: str, passed: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"check": name, "status": "PASS" if passed else "FAIL", "details": details or {}}


def _dir_has_files(path: Path) -> bool:
    if not path.exists():
        return False
    return any(item.is_file() for item in path.rglob("*"))


def _normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "day" in out.columns:
        out["day"] = out["day"].map(normalize_day)
    if "candidate_id" in out.columns:
        out["candidate_id"] = out["candidate_id"].astype(str)
    if "record_id" in out.columns:
        out["record_id"] = out["record_id"].astype(str)
    for column in ["entry_time_utc", "anchor_time_utc", "cs_max_source_time_utc", "fcs_max_source_time_utc"]:
        if column in out.columns:
            out[column] = out[column].map(normalize_ts)
    return out


def _fill_feature_gaps(df: pd.DataFrame, feature_columns: list[str]) -> tuple[pd.DataFrame, dict[str, Any]]:
    out = df.copy()
    per_feature: dict[str, dict[str, Any]] = {}
    total_missing_before = 0
    total_blank_before = 0

    for column in feature_columns:
        if column not in out.columns:
            continue
        missing_before = int(out[column].isna().sum())
        blank_before = 0
        if pd.api.types.is_object_dtype(out[column]) or pd.api.types.is_string_dtype(out[column]):
            as_text = out[column].astype("string")
            blank_mask = as_text.str.strip().isin(["", "nan", "NaN", "None", "<NA>"]).fillna(False)
            blank_before = int(blank_mask.sum())
            out[column] = as_text.mask(blank_mask, pd.NA).fillna("UNKNOWN").astype(str)
        elif pd.api.types.is_bool_dtype(out[column]):
            out[column] = out[column].fillna(False)
        else:
            out[column] = pd.to_numeric(out[column], errors="coerce").fillna(0.0)

        if missing_before or blank_before:
            per_feature[column] = {
                "missing_before": missing_before,
                "blank_before": blank_before,
                "fill_value": "UNKNOWN" if pd.api.types.is_object_dtype(df[column]) else 0,
            }
        total_missing_before += missing_before
        total_blank_before += blank_before

    missing_after = int(out[feature_columns].isna().sum().sum())
    blank_after = 0
    for column in feature_columns:
        if column in out.columns and (pd.api.types.is_object_dtype(out[column]) or pd.api.types.is_string_dtype(out[column])):
            blank_after += int(out[column].astype("string").str.strip().isin(["", "nan", "NaN", "None", "<NA>"]).fillna(False).sum())

    return out, {
        "feature_missing_before_fill": total_missing_before,
        "feature_blank_before_fill": total_blank_before,
        "feature_missing_after_fill": missing_after,
        "feature_blank_after_fill": blank_after,
        "feature_fill_columns": per_feature,
    }


def _source_time_check(df: pd.DataFrame, source_column: str) -> dict[str, Any]:
    if source_column not in df.columns:
        return {"missing_column": True, "source_after_entry_rows": 0, "source_na_rows": len(df), "equal_rows": 0}
    source = pd.to_datetime(df[source_column], utc=True, errors="coerce")
    entry = pd.to_datetime(df["entry_time_utc"], utc=True, errors="coerce")
    return {
        "missing_column": False,
        "source_after_entry_rows": int((source > entry).sum()),
        "source_na_rows": int(source.isna().sum()),
        "entry_na_rows": int(entry.isna().sum()),
        "equal_rows": int((source == entry).sum()),
    }


def _day_summary(df: pd.DataFrame, feature_columns: list[str]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for day, rows in df.groupby("day", sort=True):
        out[str(day)] = {
            "rows": int(len(rows)),
            "entry_y_1": int(pd.to_numeric(rows["entry_y"], errors="coerce").fillna(-1).eq(1).sum()),
            "entry_y_0": int(pd.to_numeric(rows["entry_y"], errors="coerce").fillna(-1).eq(0).sum()),
            "feature_count": len(feature_columns),
            "phase_y_counts": {str(k): int(v) for k, v in rows["phase_y"].astype(str).value_counts().sort_index().items()}
            if "phase_y" in rows.columns
            else {},
        }
    return out


def _write_audit(path: Path, manifest: dict[str, Any], guard: dict[str, Any]) -> None:
    lines: list[str] = [
        "# STAS5 V5 Batch Dataset Audit",
        "",
        f"Статус: `{guard['status']}`.",
        "",
        "Обучение V5 и forward V5 этим запуском не выполнялись.",
        "",
        "## Контракт",
        "",
        "```text",
        "X = 274 old causal + 81 cs_* + 84 fcs_* = 439 causal features",
        "y = entry_y / phase_y / state_y / reason_y и ручные teacher-поля",
        "```",
        "",
        "## Выходы",
        "",
        f"- batch CSV: `{manifest['outputs']['batch_csv']}`",
        f"- feature allowlist: `{manifest['outputs']['feature_allowlist']}`",
        f"- manifest: `{manifest['outputs']['manifest']}`",
        f"- guard: `{manifest['outputs']['guard']}`",
        "",
        "## Сводка",
        "",
        f"- days: `{manifest['day_count']}`",
        f"- rows: `{manifest['rows']}`",
        f"- entry_y=1 GOOD: `{manifest['entry_y_counts'].get('1', 0)}`",
        f"- entry_y=0 BAD/NO_TRADE: `{manifest['entry_y_counts'].get('0', 0)}`",
        f"- features: `{manifest['feature_count']}`",
        f"- old causal: `{manifest['old_causal_feature_count']}`",
        f"- cs_*: `{manifest['cs_feature_count']}`",
        f"- fcs_*: `{manifest['fcs_feature_count']}`",
        "",
        "## Guard",
        "",
        "| check | status | details |",
        "|---|---|---|",
    ]
    for item in guard["checks"]:
        details = json.dumps(item.get("details", {}), ensure_ascii=False, sort_keys=True)
        if len(details) > 220:
            details = details[:217] + "..."
        lines.append(f"| `{item['check']}` | `{item['status']}` | `{details}` |")

    fill = manifest["feature_fill_summary"]
    lines.extend(
        [
            "",
            "## Feature Fill",
            "",
            f"- пустых feature-значений до нормализации: `{fill['feature_missing_before_fill']}`",
            f"- пустых feature-значений после нормализации: `{fill['feature_missing_after_fill']}`",
            f"- feature-колонок с заполнением: `{len(fill['feature_fill_columns'])}`",
            "",
            "Заполнение применено только к разрешенным `X` колонкам: числовые пропуски заменены на `0`, категориальные пустоты на `UNKNOWN`.",
            "",
            "## Следующий Шаг",
            "",
            "После этого `PASS` можно готовить отдельный training guard и двухблочную схему:",
            "",
            "1. `MARKET_PHASE_STATE_ML`: учится на `phase_y/state_y`, но получает только 439 causal features.",
            "2. `ENTRY_ML`: учится на `entry_y`, получает 439 causal features плюс только OOF/live predictions первого блока, не настоящие `phase_y/state_y`.",
            "",
            "Forward разрешен только после сохраненной модели и отдельного forward/training guard `PASS`.",
            "",
        ]
    )
    ensure_parent(path)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_v5_batch_dataset(
    *,
    start_day: str = DEFAULT_START_DAY,
    end_day: str = DEFAULT_END_DAY,
    v5_root: Path | None = None,
    output_dir: Path | None = None,
    batch_family: str = "STAS5_V5",
    expected_days: int = DEFAULT_EXPECTED_DAYS,
    expected_rows: int = DEFAULT_EXPECTED_ROWS,
    expected_good: int = DEFAULT_EXPECTED_GOOD,
    expected_bad: int = DEFAULT_EXPECTED_BAD,
    expected_features: int = DEFAULT_EXPECTED_FEATURES,
    require_no_training_forward_artifacts: bool = True,
    strict: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any]]:
    start_day = normalize_day(start_day)
    end_day = normalize_day(end_day)
    v5_root = v5_root or _v5_root()
    output_dir = output_dir or v5_root
    prefix = _batch_prefix(start_day, end_day, batch_family)

    output_csv = output_dir / f"{prefix}_ML_READY_{expected_features}F_TARGETS_V1.csv"
    output_allowlist = output_dir / f"{prefix}_FEATURE_ALLOWLIST_{expected_features}F_V1.json"
    output_manifest = output_dir / f"{prefix}_MANIFEST_V1.json"
    output_audit = output_dir / f"{prefix}_AUDIT_RU.md"
    output_guard = output_dir / f"{prefix}_GUARD_V1.json"

    expected_day_list = iter_days(start_day, end_day)
    missing_days: list[str] = []
    daily_frames: list[pd.DataFrame] = []
    daily_inputs: list[dict[str, Any]] = []
    reference_features: list[str] | None = None
    allowlist_mismatch_days: dict[str, dict[str, Any]] = {}
    daily_guard_statuses: dict[str, str] = {}

    for day in expected_day_list:
        paths = _day_paths(v5_root, day)
        if not paths["csv"].exists() or not paths["allowlist"].exists():
            missing_days.append(day)
            continue

        features = _load_allowlist(paths["allowlist"])
        if reference_features is None:
            reference_features = features
        elif features != reference_features:
            allowlist_mismatch_days[day] = {
                "feature_count": len(features),
                "same_set": set(features) == set(reference_features),
            }

        frame = pd.read_csv(paths["csv"], encoding="utf-8-sig")
        frame = _normalize_keys(frame)
        daily_frames.append(frame)

        guard_status = ""
        if paths["guard"].exists():
            guard_status = str(_load_json(paths["guard"]).get("status", ""))
        daily_guard_statuses[day] = guard_status

        daily_inputs.append(
            {
                "day": day,
                "csv": rel(paths["csv"]),
                "allowlist": rel(paths["allowlist"]),
                "guard": rel(paths["guard"]),
                "rows": int(len(frame)),
                "entry_y_1": int(pd.to_numeric(frame["entry_y"], errors="coerce").fillna(-1).eq(1).sum())
                if "entry_y" in frame.columns
                else 0,
                "entry_y_0": int(pd.to_numeric(frame["entry_y"], errors="coerce").fillna(-1).eq(0).sum())
                if "entry_y" in frame.columns
                else 0,
                "feature_count": len(features),
                "guard_status": guard_status,
            }
        )

    feature_columns = reference_features or []
    if daily_frames:
        batch = pd.concat(daily_frames, ignore_index=True, sort=False)
    else:
        batch = pd.DataFrame()

    missing_feature_columns = [column for column in feature_columns if column not in batch.columns]
    for column in missing_feature_columns:
        batch[column] = pd.NA
    if not batch.empty:
        batch = _normalize_keys(batch)
        sort_columns = [column for column in ["day", "entry_time_utc", "candidate_id", "record_id"] if column in batch.columns]
        batch = batch.sort_values(sort_columns).reset_index(drop=True)
        batch, feature_fill_summary = _fill_feature_gaps(batch, feature_columns)
    else:
        feature_fill_summary = {
            "feature_missing_before_fill": 0,
            "feature_blank_before_fill": 0,
            "feature_missing_after_fill": 0,
            "feature_blank_after_fill": 0,
            "feature_fill_columns": {},
        }

    entry_y_numeric = pd.to_numeric(batch["entry_y"], errors="coerce") if "entry_y" in batch.columns else pd.Series(dtype=float)
    entry_y_counts = {str(int(k)): int(v) for k, v in entry_y_numeric.value_counts(dropna=False).sort_index().items() if pd.notna(k)}
    actual_days = sorted(batch["day"].astype(str).unique().tolist()) if "day" in batch.columns else []
    extra_days = [day for day in actual_days if day not in expected_day_list]
    missing_expected_days = [day for day in expected_day_list if day not in actual_days]

    target_columns_in_features = sorted(set(feature_columns).intersection(TARGET_OR_MANUAL_COLUMNS))
    forbidden_feature_columns = _forbidden_feature_matches(feature_columns)
    old_causal_features = [column for column in feature_columns if not column.startswith("cs_") and not column.startswith("fcs_")]
    cs_features = [column for column in feature_columns if column.startswith("cs_")]
    fcs_features = [column for column in feature_columns if column.startswith("fcs_")]

    cs_time = _source_time_check(batch, "cs_max_source_time_utc") if not batch.empty else {"source_after_entry_rows": 0}
    fcs_time = _source_time_check(batch, "fcs_max_source_time_utc") if not batch.empty else {"source_after_entry_rows": 0}

    duplicate_day_candidate = int(batch.duplicated(["day", "candidate_id"]).sum()) if {"day", "candidate_id"}.issubset(batch.columns) else -1
    duplicate_day_record = int(batch.duplicated(["day", "record_id"]).sum()) if {"day", "record_id"}.issubset(batch.columns) else -1
    duplicate_join_keys = (
        int(batch.duplicated(["day", "candidate_id", "record_id"]).sum())
        if {"day", "candidate_id", "record_id"}.issubset(batch.columns)
        else -1
    )
    daily_guard_failures = {
        day: status
        for day, status in daily_guard_statuses.items()
        if not status.startswith("PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY")
    }
    model_dir = v5_root / "model"
    forward_dir = v5_root / "forward"
    model_started = _dir_has_files(model_dir)
    forward_started = _dir_has_files(forward_dir)
    artifact_policy_pass = (not require_no_training_forward_artifacts) or (not model_started and not forward_started)

    checks = [
        _check(
            "all_expected_days_present",
            len(actual_days) == expected_days and not missing_days and not missing_expected_days and not extra_days,
            {
                "expected_days": expected_days,
                "actual_days": len(actual_days),
                "missing_input_files": missing_days,
                "missing_expected_days_in_batch": missing_expected_days,
                "extra_days": extra_days,
            },
        ),
        _check("rows_match_expected", len(batch) == expected_rows, {"expected": expected_rows, "actual": int(len(batch))}),
        _check(
            "entry_y_counts_match",
            int(entry_y_counts.get("1", 0)) == expected_good and int(entry_y_counts.get("0", 0)) == expected_bad,
            {"expected_good": expected_good, "expected_bad": expected_bad, "actual": entry_y_counts},
        ),
        _check("feature_count_expected", len(feature_columns) == expected_features, {"expected": expected_features, "actual": len(feature_columns)}),
        _check("allowlist_identical_all_days", not allowlist_mismatch_days, allowlist_mismatch_days),
        _check("daily_full_causal_guards_pass", not daily_guard_failures, daily_guard_failures),
        _check("target_manual_columns_not_in_X", not target_columns_in_features, {"columns": target_columns_in_features}),
        _check("forbidden_leakage_columns_absent_from_X", not forbidden_feature_columns, forbidden_feature_columns),
        _check("required_feature_columns_present", not missing_feature_columns, {"missing": missing_feature_columns}),
        _check(
            "no_empty_mandatory_feature_values_after_fill",
            feature_fill_summary["feature_missing_after_fill"] == 0 and feature_fill_summary["feature_blank_after_fill"] == 0,
            {
                "missing_after": feature_fill_summary["feature_missing_after_fill"],
                "blank_after": feature_fill_summary["feature_blank_after_fill"],
                "filled_before": feature_fill_summary["feature_missing_before_fill"],
            },
        ),
        _check(
            "cs_max_source_time_utc_lte_entry_time_utc",
            not cs_time.get("missing_column")
            and cs_time.get("source_after_entry_rows", 0) == 0
            and cs_time.get("source_na_rows", 0) == 0
            and cs_time.get("entry_na_rows", 0) == 0,
            cs_time,
        ),
        _check(
            "fcs_max_source_time_utc_lte_entry_time_utc",
            not fcs_time.get("missing_column")
            and fcs_time.get("source_after_entry_rows", 0) == 0
            and fcs_time.get("source_na_rows", 0) == 0
            and fcs_time.get("entry_na_rows", 0) == 0,
            fcs_time,
        ),
        _check(
            "no_duplicate_day_candidate_or_record_id",
            duplicate_day_candidate == 0 and duplicate_day_record == 0 and duplicate_join_keys == 0,
            {
                "duplicate_day_candidate": duplicate_day_candidate,
                "duplicate_day_record_id": duplicate_day_record,
                "duplicate_day_candidate_record_id": duplicate_join_keys,
            },
        ),
        _check(
            "training_and_forward_not_started",
            artifact_policy_pass,
            {
                "required": require_no_training_forward_artifacts,
                "policy": "must_be_empty_before_first_training"
                if require_no_training_forward_artifacts
                else "previous_artifacts_allowed_for_walk_forward_retrain",
                "model_dir": rel(model_dir),
                "model_started": model_started,
                "forward_dir": rel(forward_dir),
                "forward_started": forward_started,
            },
        ),
    ]
    status = STATUS_PASS if all(item["status"] == "PASS" for item in checks) else STATUS_FAIL

    feature_allowlist = {
        "status": status,
        "created_utc": utc_now(),
        "schema_version": 1,
        "range": {"start_day": start_day, "end_day": end_day},
        "feature_columns": feature_columns,
        "feature_count": len(feature_columns),
        "old_causal_feature_columns": old_causal_features,
        "old_causal_feature_count": len(old_causal_features),
        "cs_feature_columns": cs_features,
        "cs_feature_count": len(cs_features),
        "fcs_feature_columns": fcs_features,
        "fcs_feature_count": len(fcs_features),
        "target_columns_allowed_as_y_not_X": sorted([column for column in TARGET_OR_MANUAL_COLUMNS if column in batch.columns]),
        "guardrails": [
            "manual_targets_are_y_not_X",
            "phase_y_state_y_reason_y_are_not_model_features",
            "cs_fcs_source_time_must_be_lte_entry_time",
            "no_future_postfact_hit_tp_stas3_exit_old_ml_full_group_features",
            "entry_ml_may_use_only_oof_or_live_market_phase_predictions_not_true_phase_y_state_y",
        ],
    }

    manifest = {
        "status": status,
        "created_utc": utc_now(),
        "schema_version": 1,
        "range": {"start_day": start_day, "end_day": end_day},
        "day_count": len(actual_days),
        "expected_day_count": expected_days,
        "rows": int(len(batch)),
        "expected_rows": expected_rows,
        "entry_y_counts": entry_y_counts,
        "expected_entry_y_counts": {"1": expected_good, "0": expected_bad},
        "feature_count": len(feature_columns),
        "expected_feature_count": expected_features,
        "old_causal_feature_count": len(old_causal_features),
        "cs_feature_count": len(cs_features),
        "fcs_feature_count": len(fcs_features),
        "feature_columns": feature_columns,
        "days": _day_summary(batch, feature_columns) if not batch.empty else {},
        "daily_inputs": daily_inputs,
        "feature_fill_summary": feature_fill_summary,
        "training_started": model_started,
        "forward_started": forward_started,
        "training_forward_artifact_check_required": require_no_training_forward_artifacts,
        "next_required_step": "training_guard_then_MARKET_PHASE_STATE_ML_OOF_then_ENTRY_ML_no_true_phase_state_features",
        "outputs": {
            "batch_csv": rel(output_csv),
            "feature_allowlist": rel(output_allowlist),
            "manifest": rel(output_manifest),
            "audit": rel(output_audit),
            "guard": rel(output_guard),
        },
    }

    guard = {
        "status": status,
        "created_utc": utc_now(),
        "schema_version": 1,
        "range": {"start_day": start_day, "end_day": end_day},
        "rows": int(len(batch)),
        "entry_y_counts": entry_y_counts,
        "feature_count": len(feature_columns),
        "old_causal_feature_count": len(old_causal_features),
        "cs_feature_count": len(cs_features),
        "fcs_feature_count": len(fcs_features),
        "checks": checks,
        "outputs": manifest["outputs"],
        "feature_columns": feature_columns,
        "forbidden_feature_columns": forbidden_feature_columns,
        "target_columns_in_features": target_columns_in_features,
    }

    ensure_parent(output_csv)
    batch.to_csv(output_csv, index=False, encoding="utf-8-sig")
    write_json(output_allowlist, feature_allowlist)
    write_json(output_manifest, manifest)
    write_json(output_guard, guard)
    _write_audit(output_audit, manifest, guard)

    if strict and status != STATUS_PASS:
        raise ValueError(f"STAS5 V5 batch guard failed: {guard['checks']}")
    return batch, manifest, guard


def main() -> int:
    parser = argparse.ArgumentParser(description="Build STAS5 V5 batch dataset and leakage/no-future guard.")
    parser.add_argument("--start-day", default=DEFAULT_START_DAY)
    parser.add_argument("--end-day", default=DEFAULT_END_DAY)
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--batch-family", default="STAS5_V5")
    parser.add_argument("--expected-days", type=int, default=DEFAULT_EXPECTED_DAYS)
    parser.add_argument("--expected-rows", type=int, default=DEFAULT_EXPECTED_ROWS)
    parser.add_argument("--expected-good", type=int, default=DEFAULT_EXPECTED_GOOD)
    parser.add_argument("--expected-bad", type=int, default=DEFAULT_EXPECTED_BAD)
    parser.add_argument("--expected-features", type=int, default=DEFAULT_EXPECTED_FEATURES)
    parser.add_argument("--allow-existing-training-forward", action="store_true")
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()

    _batch, manifest, guard = build_v5_batch_dataset(
        start_day=args.start_day,
        end_day=args.end_day,
        output_dir=Path(args.output_dir) if args.output_dir else None,
        batch_family=args.batch_family,
        expected_days=args.expected_days,
        expected_rows=args.expected_rows,
        expected_good=args.expected_good,
        expected_bad=args.expected_bad,
        expected_features=args.expected_features,
        require_no_training_forward_artifacts=not args.allow_existing_training_forward,
        strict=not args.no_strict,
    )
    print(
        json.dumps(
            {
                "status": guard["status"],
                "rows": manifest["rows"],
                "entry_y_counts": manifest["entry_y_counts"],
                "feature_count": manifest["feature_count"],
                "day_count": manifest["day_count"],
                "batch_csv": manifest["outputs"]["batch_csv"],
                "guard": manifest["outputs"]["guard"],
                "audit": manifest["outputs"]["audit"],
            },
            ensure_ascii=False,
        )
    )
    return 0 if guard["status"] == STATUS_PASS else 2


if __name__ == "__main__":
    raise SystemExit(main())
