from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from mlbotnav.stas5_common import PROJECT_ROOT, compact_day, ensure_parent, iter_days, normalize_day, normalize_ts, rel, utc_now, write_json
from mlbotnav.stas5_v5_batch_dataset_builder import (
    DEFAULT_EXPECTED_FEATURES,
    STATUS_PASS as ENTRY_BATCH_STATUS_PASS,
    TARGET_OR_MANUAL_COLUMNS,
    _check,
    _fill_feature_gaps,
    _forbidden_feature_matches,
    _source_time_check,
)
from mlbotnav.stas5_v5c_bollinger_layer import (
    BOLLINGER_AUDIT_COLUMNS,
    BOLLINGER_FEATURE_COLUMNS,
    BOLLINGER_FEATURE_CONTRACT,
    BOLLINGER_LAYER_ID,
    attach_bollinger_features,
    bollinger_feature_count,
    bollinger_source_time_check,
    extended_feature_columns,
    load_ohlcv_context_for_range,
)
from mlbotnav.stas5_v5c_review_ladder import normalize_candidate_id


ENTRY_BATCH_STATUS_FAIL = "FAIL_V5C_REVIEW_SUPERVISED_ENTRY_BATCH_GUARD"
RISKGATE_STATUS_PASS = "PASS_V5C_RISKGATE_TRAIN_DATASET_GUARD_READY_NO_TRAINING"
RISKGATE_STATUS_FAIL = "FAIL_V5C_RISKGATE_TRAIN_DATASET_GUARD"

BASE_START_DAY = "2026-01-27"
BASE_END_DAY = "2026-02-27"
TRAIN_START_DAY = "2026-01-27"
TRAIN_END_DAY = "2026-03-20"
REVIEW_START_DAY = "2026-02-28"
REVIEW_END_DAY = "2026-03-20"

BASE_EXPECTED_DAYS = 32
BASE_EXPECTED_ROWS = 2596
BASE_EXPECTED_GOOD = 290
BASE_EXPECTED_BAD = 2306
REVIEW_EXPECTED_DAYS = 21
REVIEW_EXPECTED_ROWS = 689
REVIEW_EXPECTED_GOOD = 227
REVIEW_EXPECTED_BAD = 462
REVIEW_EXPECTED_RISK_BAD = 400

ENTRY_EXPECTED_DAYS = 53
ENTRY_EXPECTED_ROWS = 3285
ENTRY_EXPECTED_GOOD = 517
ENTRY_EXPECTED_BAD = 2768
RISKGATE_EXPECTED_POSITIVE = 400
RISKGATE_EXPECTED_SAFE_NEGATIVE = 227

V5_ROOT = PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5"
V5C_ROOT = PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5c"
V5C_FORWARD_RUNS_DIR = V5C_ROOT / "forward" / "runs"
REVIEW_PACK_DIR = (
    V5C_ROOT
    / "review"
    / "_APPROVED_REVIEW_PACKS"
    / "STAS5_V5C_REVIEW_PACK_R2_R3_R4_20260228_20260320_V1"
)

BASE_BATCH_CSV = V5_ROOT / "STAS5_V5_BATCH_20260127_20260227_ML_READY_439F_TARGETS_V1.csv"
BASE_ALLOWLIST_JSON = V5_ROOT / "STAS5_V5_BATCH_20260127_20260227_FEATURE_ALLOWLIST_439F_V1.json"
BASE_GUARD_JSON = V5_ROOT / "STAS5_V5_BATCH_20260127_20260227_GUARD_V1.json"

REVIEW_ENTRY_NAME = "STAS5_V5C_R2_R3_R4_ENTRY_REVIEW_APPROVED_ALL_V1.csv"
REVIEW_RISKGATE_NAME = "STAS5_V5C_R2_R3_R4_RISKGATE_REVIEW_APPROVED_ALL_V1.csv"
REVIEW_MANIFEST_NAME = "STAS5_V5C_R2_R3_R4_REVIEW_PACK_MANIFEST_V1.json"
REVIEW_GUARD_NAME = "STAS5_V5C_R2_R3_R4_REVIEW_PACK_GUARD_V1.json"

EXTENDED_TARGET_OR_MANUAL_COLUMNS = set(TARGET_OR_MANUAL_COLUMNS).union(
    {
        "risk_bad_y",
        "entry_review_label",
        "risk_review_label",
        "user_text_raw",
        "risk_user_hint",
        "entry_from_risk_bad",
        "model_decision",
        "marker",
        "marker_user",
        "entry_ml_live_score",
        "riskgate_raw_status_at_review",
        "riskgate_good_exception_candidate",
        "RISK_GATE_STATUS",
        "RISK_GATE_ACTION",
        "RISK_GATE_PRIMARY_REGIME",
        "RISK_GATE_TAGS",
        "RISK_GATE_RAW_STATUS",
        "RISK_GATE_RAW_PRIMARY_REGIME",
        "RISK_NO_FUTURE_OK",
    }
).union(
    set(BOLLINGER_AUDIT_COLUMNS)
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _load_allowlist(path: Path) -> list[str]:
    payload = _load_json(path)
    return [str(column) for column in payload.get("feature_columns", [])]


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def _find_required(path: Path, fallback_dir: Path, pattern: str) -> Path:
    if path.exists():
        return path
    matches = sorted(fallback_dir.glob(pattern))
    if len(matches) == 1:
        return matches[0]
    raise FileNotFoundError(f"required file not found: {path}; fallback pattern={pattern}")


def _normalize_keys(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "day" in out.columns:
        out["day"] = out["day"].map(normalize_day)
    if "candidate_id" in out.columns:
        out["candidate_id"] = out["candidate_id"].map(lambda value: normalize_candidate_id(str(value)))
    if "record_id" in out.columns:
        out["record_id"] = out["record_id"].astype(str)
    for column in ["entry_time_utc", "anchor_time_utc", "cs_max_source_time_utc", "fcs_max_source_time_utc"]:
        if column in out.columns:
            out[column] = out[column].map(normalize_ts)
    return out


def _phase_y_from_entry_time(value: Any) -> str:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    ts = ts.tz_convert("UTC")
    minute = ts.hour * 60 + ts.minute
    if minute <= 6 * 60:
        return "P1_ASIA_EARLY_STRUCTURE"
    if minute <= 12 * 60:
        return "P2_MORNING_STRUCTURE"
    if minute <= 16 * 60:
        return "P3_MIDDAY_STRUCTURE"
    if minute <= 20 * 60:
        return "P4_NY_STRUCTURE"
    return "P5_LATE_STRUCTURE"


def _entry_output_paths(output_dir: Path, start_day: str, end_day: str, expected_features: int) -> dict[str, Path]:
    prefix = f"STAS5_V5C_BATCH_{compact_day(start_day)}_{compact_day(end_day)}"
    return {
        "csv": output_dir / f"{prefix}_ML_READY_{expected_features}F_TARGETS_V1.csv",
        "allowlist": output_dir / f"{prefix}_FEATURE_ALLOWLIST_{expected_features}F_V1.json",
        "manifest": output_dir / f"{prefix}_MANIFEST_V1.json",
        "audit": output_dir / f"{prefix}_AUDIT_RU.md",
        "guard": output_dir / f"{prefix}_GUARD_V1.json",
    }


def _riskgate_output_paths(output_dir: Path, start_day: str, end_day: str, expected_features: int) -> dict[str, Path]:
    prefix = f"STAS5_V5C_RISKGATE_TRAIN_DATASET_{compact_day(start_day)}_{compact_day(end_day)}"
    return {
        "csv": output_dir / f"{prefix}_X{expected_features}_RISK_BAD_Y_V1.csv",
        "allowlist": output_dir / f"{prefix}_FEATURE_ALLOWLIST_{expected_features}F_V1.json",
        "manifest": output_dir / f"{prefix}_MANIFEST_V1.json",
        "audit": output_dir / f"{prefix}_AUDIT_RU.md",
        "guard": output_dir / f"{prefix}_GUARD_V1.json",
    }


def _ensure_output_paths_available(paths: list[Path], *, force: bool) -> None:
    existing = [path for path in paths if path.exists()]
    if existing and not force:
        rendered = ", ".join(rel(path) for path in existing)
        raise FileExistsError(f"output already exists; rerun with --force to overwrite: {rendered}")


def _review_source_run_by_day(pack_manifest: dict[str, Any], entry_review: pd.DataFrame) -> dict[str, str]:
    out: dict[str, str] = {}
    for row in pack_manifest.get("day_rows", []):
        day = normalize_day(row.get("day", ""))
        run_id = str(row.get("forward_run_id") or row.get("source_forward_run_id") or "").strip()
        if day and run_id:
            out[day] = run_id
    if out:
        return out
    grouped = entry_review.groupby("day")["source_forward_run_id"].unique()
    for day, values in grouped.items():
        clean = [str(value).strip() for value in values if str(value).strip()]
        if len(set(clean)) == 1:
            out[str(day)] = clean[0]
    return out


def _source_day_paths(forward_runs_dir: Path, run_id: str, day: str) -> dict[str, Path]:
    compact = compact_day(day)
    day_dir = forward_runs_dir / run_id / "forward_market_passports" / compact
    prefix = f"STAS5_V5_MARKET_PASSPORT_{compact}"
    return {
        "csv": day_dir / f"{prefix}_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv",
        "allowlist": day_dir / f"{prefix}_FEATURE_ALLOWLIST_274_PLUS_FULL_CAUSAL_STRUCTURE_V1.json",
        "guard": day_dir / f"{prefix}_FULL_CAUSAL_STRUCTURE_GUARD_V1.json",
    }


def _validate_feature_values(df: pd.DataFrame, features: list[str]) -> dict[str, Any]:
    if not features or df.empty:
        return {"feature_nulls": 0, "feature_inf_count": 0}
    numeric = df[features].select_dtypes(include=[np.number])
    inf_count = int(np.isinf(numeric.to_numpy(dtype=float)).sum()) if not numeric.empty else 0
    return {"feature_nulls": int(df[features].isna().sum().sum()), "feature_inf_count": inf_count}


def _day_summary(df: pd.DataFrame, *, target_column: str = "entry_y") -> dict[str, dict[str, Any]]:
    if df.empty or "day" not in df.columns:
        return {}
    out: dict[str, dict[str, Any]] = {}
    for day, rows in df.groupby("day", sort=True):
        target = pd.to_numeric(rows[target_column], errors="coerce").fillna(-1).astype(int) if target_column in rows else pd.Series(dtype=int)
        item = {"rows": int(len(rows))}
        for value, count in target.value_counts().sort_index().items():
            item[f"{target_column}_{int(value)}"] = int(count)
        out[str(day)] = item
    return out


def _write_entry_audit(path: Path, manifest: dict[str, Any], guard: dict[str, Any]) -> None:
    lines = [
        "# STAS5 V5C ENTRY Train Dataset Audit",
        "",
        f"Статус: `{guard['status']}`.",
        "",
        "Сборка не запускает обучение и forward. Она переносит approved-разметку R2/R3/R4 на causal признаки; при включенном Bollinger Layer добавляются только `bb_*` признаки, посчитанные до `entry_time_utc`.",
        "",
        "## Сводка",
        "",
        f"- range: `{manifest['range']['start_day']}..{manifest['range']['end_day']}`",
        f"- rows: `{manifest['rows']}`",
        f"- days: `{manifest['day_count']}`",
        f"- entry_y=1 GOOD: `{manifest['entry_y_counts'].get('1', 0)}`",
        f"- entry_y=0 BAD: `{manifest['entry_y_counts'].get('0', 0)}`",
        f"- features: `{manifest['feature_count']}`",
        f"- base features: `{manifest.get('base_feature_count', manifest['feature_count'])}`",
        f"- Bollinger Layer: `{'ON' if manifest.get('bollinger_layer', {}).get('enabled') else 'OFF'}`",
        f"- review rows: `{manifest['review_pack']['entry_rows']}`",
        f"- review risk_bad_y=1 rows: `{manifest['review_pack']['risk_bad']}`",
        "",
        "## Правило",
        "",
        "`риск плохо` остается двойной целью: `entry_y=0 + risk_bad_y=1`. `risk_bad_y` не входит в X.",
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
    ensure_parent(path)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_riskgate_audit(path: Path, manifest: dict[str, Any], guard: dict[str, Any]) -> None:
    lines = [
        "# STAS5 V5C RiskGate Train Dataset Audit",
        "",
        f"Статус: `{guard['status']}`.",
        "",
        "RiskGate dataset отделен от ENTRY: те же causal признаки, но цель другая - `risk_bad_y`.",
        "",
        "## Сводка",
        "",
        f"- rows: `{manifest['rows']}`",
        f"- risk_bad_y=1: `{manifest['risk_bad_y_counts'].get('1', 0)}`",
        f"- risk_bad_y=0 explicit safe: `{manifest['risk_bad_y_counts'].get('0', 0)}`",
        f"- features: `{manifest['feature_count']}`",
        f"- base features: `{manifest.get('base_feature_count', manifest['feature_count'])}`",
        f"- Bollinger Layer: `{'ON' if manifest.get('bollinger_layer', {}).get('enabled') else 'OFF'}`",
        f"- negative policy: `{manifest['negative_policy']}`",
        "",
        "Неразмеченная тишина не считается безопасностью. В V1 отрицательные RiskGate-примеры берутся только из явно подтвержденных ENTRY GOOD.",
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
    ensure_parent(path)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_v5c_review_supervised_datasets(
    *,
    train_start_day: str = TRAIN_START_DAY,
    train_end_day: str = TRAIN_END_DAY,
    base_start_day: str = BASE_START_DAY,
    base_end_day: str = BASE_END_DAY,
    review_start_day: str = REVIEW_START_DAY,
    review_end_day: str = REVIEW_END_DAY,
    base_batch_csv: Path = BASE_BATCH_CSV,
    base_allowlist_json: Path = BASE_ALLOWLIST_JSON,
    base_guard_json: Path = BASE_GUARD_JSON,
    review_pack_dir: Path = REVIEW_PACK_DIR,
    forward_runs_dir: Path = V5C_FORWARD_RUNS_DIR,
    output_dir: Path = V5C_ROOT,
    expected_features: int = DEFAULT_EXPECTED_FEATURES,
    expected_base_days: int = BASE_EXPECTED_DAYS,
    expected_base_rows: int = BASE_EXPECTED_ROWS,
    expected_base_good: int = BASE_EXPECTED_GOOD,
    expected_base_bad: int = BASE_EXPECTED_BAD,
    expected_review_days: int = REVIEW_EXPECTED_DAYS,
    expected_review_rows: int = REVIEW_EXPECTED_ROWS,
    expected_review_good: int = REVIEW_EXPECTED_GOOD,
    expected_review_bad: int = REVIEW_EXPECTED_BAD,
    expected_review_risk_bad: int = REVIEW_EXPECTED_RISK_BAD,
    expected_entry_days: int = ENTRY_EXPECTED_DAYS,
    expected_entry_rows: int = ENTRY_EXPECTED_ROWS,
    expected_entry_good: int = ENTRY_EXPECTED_GOOD,
    expected_entry_bad: int = ENTRY_EXPECTED_BAD,
    expected_risk_positive: int = RISKGATE_EXPECTED_POSITIVE,
    expected_risk_safe_negative: int = RISKGATE_EXPECTED_SAFE_NEGATIVE,
    enable_bollinger_layer: bool = False,
    bollinger_ohlcv_csv: Path | None = None,
    force: bool = False,
    strict: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any], dict[str, Any], dict[str, Any]]:
    train_start_day = normalize_day(train_start_day)
    train_end_day = normalize_day(train_end_day)
    base_start_day = normalize_day(base_start_day)
    base_end_day = normalize_day(base_end_day)
    review_start_day = normalize_day(review_start_day)
    review_end_day = normalize_day(review_end_day)
    output_dir.mkdir(parents=True, exist_ok=True)

    active_expected_features = int(expected_features) + (bollinger_feature_count() if enable_bollinger_layer else 0)
    entry_paths = _entry_output_paths(output_dir, train_start_day, train_end_day, active_expected_features)
    risk_paths = _riskgate_output_paths(output_dir, train_start_day, train_end_day, active_expected_features)
    _ensure_output_paths_available(list(entry_paths.values()) + list(risk_paths.values()), force=force)

    review_entry_path = _find_required(review_pack_dir / "entry" / REVIEW_ENTRY_NAME, review_pack_dir / "entry", "*ENTRY_REVIEW_APPROVED_ALL*.csv")
    review_risk_path = _find_required(
        review_pack_dir / "riskgate" / REVIEW_RISKGATE_NAME,
        review_pack_dir / "riskgate",
        "*RISKGATE_REVIEW_APPROVED_ALL*.csv",
    )
    review_manifest_path = _find_required(review_pack_dir / REVIEW_MANIFEST_NAME, review_pack_dir, "*REVIEW_PACK_MANIFEST*.json")
    review_guard_path = _find_required(review_pack_dir / REVIEW_GUARD_NAME, review_pack_dir, "*REVIEW_PACK_GUARD*.json")

    base = _normalize_keys(_read_csv(base_batch_csv))
    base_feature_columns = _load_allowlist(base_allowlist_json)
    feature_columns = extended_feature_columns(base_feature_columns) if enable_bollinger_layer else list(base_feature_columns)
    base_guard = _load_json(base_guard_json)
    review_manifest = _load_json(review_manifest_path)
    review_guard = _load_json(review_guard_path)
    bollinger_context_manifest: dict[str, Any] = {
        "status": "DISABLED",
        "layer_id": BOLLINGER_LAYER_ID,
        "feature_contract": "",
        "feature_count": 0,
    }
    bollinger_context = pd.DataFrame()
    if enable_bollinger_layer:
        if bollinger_ohlcv_csv is not None:
            bollinger_context = pd.read_csv(bollinger_ohlcv_csv, encoding="utf-8-sig")
            bollinger_context_manifest = {
                "status": "PASS_V5C_BOLLINGER_OHLCV_CONTEXT_READY_FROM_OPERATOR_CSV",
                "layer_id": BOLLINGER_LAYER_ID,
                "feature_contract": BOLLINGER_FEATURE_CONTRACT,
                "feature_count": bollinger_feature_count(),
                "context_csv": rel(bollinger_ohlcv_csv),
                "rows": int(len(bollinger_context)),
            }
        else:
            bollinger_context, bollinger_context_manifest = load_ohlcv_context_for_range(
                start_day=train_start_day,
                end_day=train_end_day,
                warmup_days=1,
                strict=strict,
            )

    missing_base_features = [column for column in feature_columns if column not in base.columns]
    for column in missing_base_features:
        base[column] = pd.NA
    base, base_fill_summary = _fill_feature_gaps(base, feature_columns)
    base = base.copy()
    base["supervision_source"] = "base_v5_32d"
    if "risk_bad_y" not in base.columns:
        base["risk_bad_y"] = ""
    else:
        base["risk_bad_y"] = base["risk_bad_y"].fillna("").astype(str)
    base_bollinger_summary: dict[str, Any] = {"status": "DISABLED"}
    if enable_bollinger_layer:
        base, base_bollinger_summary = attach_bollinger_features(base, bollinger_context)
        base, base_fill_summary = _fill_feature_gaps(base, feature_columns)

    entry_review = _normalize_keys(_read_csv(review_entry_path))
    risk_review = _normalize_keys(_read_csv(review_risk_path))
    entry_review["entry_y"] = pd.to_numeric(entry_review["entry_y"], errors="coerce").fillna(-1).astype(int)
    risk_review["risk_bad_y"] = pd.to_numeric(risk_review["risk_bad_y"], errors="coerce").fillna(-1).astype(int)

    source_run_by_day = _review_source_run_by_day(review_manifest, entry_review)
    expected_review_day_list = iter_days(review_start_day, review_end_day)
    review_frames: list[pd.DataFrame] = []
    source_inputs: list[dict[str, Any]] = []
    missing_source_days: list[str] = []
    allowlist_mismatch_days: dict[str, dict[str, Any]] = {}
    full_guard_failures: dict[str, str] = {}
    missing_join_ids: dict[str, list[str]] = {}
    record_mismatches: list[dict[str, str]] = []
    time_mismatches: list[dict[str, str]] = []

    risk_keys = set(zip(risk_review["day"].astype(str), risk_review["candidate_id"].astype(str)))
    risk_meta_columns = [
        column
        for column in [
            "day",
            "candidate_id",
            "risk_bad_y",
            "risk_review_label",
            "risk_user_hint",
            "RISK_GATE_STATUS",
            "RISK_GATE_ACTION",
            "RISK_GATE_PRIMARY_REGIME",
            "RISK_GATE_TAGS",
            "RISK_GATE_RAW_STATUS",
            "RISK_GATE_RAW_PRIMARY_REGIME",
            "RISK_NO_FUTURE_OK",
        ]
        if column in risk_review.columns
    ]
    risk_meta = risk_review[risk_meta_columns].copy() if risk_meta_columns else pd.DataFrame(columns=["day", "candidate_id", "risk_bad_y"])

    for day in expected_review_day_list:
        run_id = source_run_by_day.get(day, "")
        if not run_id:
            missing_source_days.append(day)
            continue
        paths = _source_day_paths(forward_runs_dir, run_id, day)
        if not paths["csv"].exists() or not paths["allowlist"].exists() or not paths["guard"].exists():
            missing_source_days.append(day)
            continue

        day_allowlist = _load_allowlist(paths["allowlist"])
        if day_allowlist != base_feature_columns:
            allowlist_mismatch_days[day] = {
                "feature_count": len(day_allowlist),
                "same_set": set(day_allowlist) == set(base_feature_columns),
            }
        full_guard_status = str(_load_json(paths["guard"]).get("status", ""))
        if full_guard_status != "PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY":
            full_guard_failures[day] = full_guard_status

        source = _normalize_keys(_read_csv(paths["csv"]))
        missing_day_features = [column for column in base_feature_columns if column not in source.columns]
        for column in missing_day_features:
            source[column] = pd.NA

        labels = entry_review.loc[entry_review["day"].astype(str).eq(day)].copy()
        joined = labels.merge(source, on=["day", "candidate_id"], how="left", suffixes=("_review", ""))
        missing = joined.loc[joined["record_id"].isna() if "record_id" in joined.columns else pd.Series(True, index=joined.index)]
        if not missing.empty:
            missing_join_ids[day] = sorted(missing["candidate_id"].astype(str).unique().tolist())

        joined = joined.loc[joined["record_id"].notna()].copy() if "record_id" in joined.columns else joined.iloc[0:0].copy()
        if "record_id_review" in joined.columns:
            mismatch = joined.loc[
                joined["record_id_review"].astype(str).str.strip().ne(joined["record_id"].astype(str).str.strip())
            ]
            record_mismatches.extend(
                {
                    "day": str(row["day"]),
                    "candidate_id": str(row["candidate_id"]),
                    "review_record_id": str(row["record_id_review"]),
                    "source_record_id": str(row["record_id"]),
                }
                for row in mismatch.to_dict("records")
            )
        if "entry_time_utc_review" in joined.columns:
            mismatch = joined.loc[
                joined["entry_time_utc_review"].map(normalize_ts).astype(str).ne(joined["entry_time_utc"].map(normalize_ts).astype(str))
            ]
            time_mismatches.extend(
                {
                    "day": str(row["day"]),
                    "candidate_id": str(row["candidate_id"]),
                    "review_entry_time_utc": normalize_ts(row["entry_time_utc_review"]),
                    "source_entry_time_utc": normalize_ts(row["entry_time_utc"]),
                }
                for row in mismatch.to_dict("records")
            )

        joined = joined.merge(risk_meta, on=["day", "candidate_id"], how="left", suffixes=("", "_risk"))
        joined["risk_bad_y"] = pd.to_numeric(joined.get("risk_bad_y", 0), errors="coerce").fillna(0).astype(int)
        joined["entry_y"] = pd.to_numeric(joined["entry_y"], errors="coerce").fillna(0).astype(int)
        joined["phase_y"] = joined["entry_time_utc"].map(_phase_y_from_entry_time)
        joined["state_y"] = np.where(
            joined["entry_y"].eq(1),
            "USER_APPROVED_GOOD_ENTRY_ZONE",
            "BAD_NEAR_APPROVED_NOT_SELECTED",
        )
        joined["reason_y"] = np.where(
            joined["entry_y"].eq(1),
            "GOOD_USER_APPROVED_ENTRY",
            np.where(joined["risk_bad_y"].eq(1), "BAD_RISKGATE_USER_MARKED_FATAL_RISK", "BAD_USER_REVIEWED_ENTRY"),
        )
        joined["human_label"] = np.where(joined["entry_y"].eq(1), "GOOD_USER_REVIEW", "BAD_USER_REVIEW")
        joined["label_status"] = "APPROVED_R2_R3_R4_USER_REVIEW"
        joined["supervision_source"] = "approved_review_pack_r2_r3_r4"
        joined["source_forward_run_id_for_x439"] = run_id
        joined["source_forward_market_passport_csv"] = rel(paths["csv"])
        joined["source_forward_full_guard_status"] = full_guard_status
        if "entry_from_risk_bad" in joined.columns:
            joined["entry_from_risk_bad"] = pd.to_numeric(joined["entry_from_risk_bad"], errors="coerce").fillna(0).astype(int)
        else:
            joined["entry_from_risk_bad"] = joined["risk_bad_y"]
        review_frames.append(joined)
        source_inputs.append(
            {
                "day": day,
                "forward_run_id": run_id,
                "source_csv": rel(paths["csv"]),
                "allowlist": rel(paths["allowlist"]),
                "guard": rel(paths["guard"]),
                "source_rows": int(len(source)),
                "review_label_rows": int(len(labels)),
                "joined_rows": int(len(joined)),
                "entry_good": int(joined["entry_y"].eq(1).sum()),
                "entry_bad": int(joined["entry_y"].eq(0).sum()),
                "risk_bad": int(joined["risk_bad_y"].eq(1).sum()),
                "feature_count": len(day_allowlist),
                "guard_status": full_guard_status,
            }
        )

    review_labeled = pd.concat(review_frames, ignore_index=True, sort=False) if review_frames else pd.DataFrame()
    review_bollinger_summary: dict[str, Any] = {"status": "DISABLED"}
    if enable_bollinger_layer and not review_labeled.empty:
        review_labeled, review_bollinger_summary = attach_bollinger_features(review_labeled, bollinger_context)
    review_labeled, review_fill_summary = _fill_feature_gaps(review_labeled, feature_columns) if not review_labeled.empty else (review_labeled, {})

    base_columns = list(base.columns)
    extra_columns = [column for column in review_labeled.columns if column not in base_columns]
    output_columns = base_columns + extra_columns
    entry_batch = pd.concat(
        [base.reindex(columns=output_columns), review_labeled.reindex(columns=output_columns)],
        ignore_index=True,
        sort=False,
    )
    entry_batch = _normalize_keys(entry_batch)
    entry_batch, entry_fill_summary = _fill_feature_gaps(entry_batch, feature_columns)
    sort_columns = [column for column in ["day", "entry_time_utc", "candidate_id", "record_id"] if column in entry_batch.columns]
    entry_batch = entry_batch.sort_values(sort_columns).reset_index(drop=True)
    entry_batch["entry_y"] = pd.to_numeric(entry_batch["entry_y"], errors="coerce").fillna(0).astype(int)

    risk_dataset = review_labeled.loc[
        review_labeled["risk_bad_y"].astype(int).eq(1)
        | (review_labeled["entry_y"].astype(int).eq(1) & review_labeled["risk_bad_y"].astype(int).eq(0))
    ].copy()
    risk_dataset["risk_bad_y"] = pd.to_numeric(risk_dataset["risk_bad_y"], errors="coerce").fillna(0).astype(int)
    risk_dataset["risk_sample_role"] = np.where(
        risk_dataset["risk_bad_y"].eq(1),
        "RISK_BAD_POSITIVE",
        "EXPLICIT_SAFE_ENTRY_GOOD_NEGATIVE",
    )
    risk_dataset, risk_fill_summary = _fill_feature_gaps(risk_dataset, feature_columns)
    risk_dataset = risk_dataset.sort_values(sort_columns).reset_index(drop=True)

    entry_y_counts = {
        str(int(key)): int(value)
        for key, value in entry_batch["entry_y"].value_counts(dropna=False).sort_index().items()
        if pd.notna(key)
    }
    risk_y_counts = {
        str(int(key)): int(value)
        for key, value in risk_dataset["risk_bad_y"].value_counts(dropna=False).sort_index().items()
        if pd.notna(key)
    }
    actual_entry_days = sorted(entry_batch["day"].astype(str).unique().tolist())
    actual_review_days = sorted(review_labeled["day"].astype(str).unique().tolist()) if not review_labeled.empty else []

    entry_target_columns_in_features = sorted(set(feature_columns).intersection(EXTENDED_TARGET_OR_MANUAL_COLUMNS))
    forbidden_features = _forbidden_feature_matches(feature_columns)
    missing_entry_features = [column for column in feature_columns if column not in entry_batch.columns]
    missing_risk_features = [column for column in feature_columns if column not in risk_dataset.columns]
    entry_feature_values = _validate_feature_values(entry_batch, feature_columns)
    risk_feature_values = _validate_feature_values(risk_dataset, feature_columns)
    entry_cs_time = _source_time_check(entry_batch, "cs_max_source_time_utc")
    entry_fcs_time = _source_time_check(entry_batch, "fcs_max_source_time_utc")
    risk_cs_time = _source_time_check(risk_dataset, "cs_max_source_time_utc")
    risk_fcs_time = _source_time_check(risk_dataset, "fcs_max_source_time_utc")
    entry_bb_time = bollinger_source_time_check(entry_batch) if enable_bollinger_layer else {"disabled": True}
    risk_bb_time = bollinger_source_time_check(risk_dataset) if enable_bollinger_layer else {"disabled": True}
    bollinger_audit_columns_in_features = sorted(set(feature_columns).intersection(BOLLINGER_AUDIT_COLUMNS))
    bollinger_feature_nulls = (
        int(entry_batch[BOLLINGER_FEATURE_COLUMNS].isna().sum().sum())
        if enable_bollinger_layer and set(BOLLINGER_FEATURE_COLUMNS).issubset(entry_batch.columns)
        else 0
    )

    entry_duplicate_day_candidate = int(entry_batch.duplicated(["day", "candidate_id"]).sum())
    entry_duplicate_day_record = int(entry_batch.duplicated(["day", "record_id"]).sum())
    risk_duplicate_day_candidate = int(risk_dataset.duplicated(["day", "candidate_id"]).sum())
    risk_duplicate_day_record = int(risk_dataset.duplicated(["day", "record_id"]).sum())

    entry_keys = set(zip(entry_review["day"].astype(str), entry_review["candidate_id"].astype(str)))
    entry_good_keys = set(
        zip(
            entry_review.loc[entry_review["entry_y"].eq(1), "day"].astype(str),
            entry_review.loc[entry_review["entry_y"].eq(1), "candidate_id"].astype(str),
        )
    )
    entry_bad_keys = set(
        zip(
            entry_review.loc[entry_review["entry_y"].eq(0), "day"].astype(str),
            entry_review.loc[entry_review["entry_y"].eq(0), "candidate_id"].astype(str),
        )
    )
    risk_not_entry_bad = sorted([f"{day}:{candidate}" for day, candidate in risk_keys if (day, candidate) not in entry_bad_keys])
    good_risk_conflicts = sorted([f"{day}:{candidate}" for day, candidate in risk_keys.intersection(entry_good_keys)])
    risk_dataset_base_rows = int(risk_dataset.get("supervision_source", pd.Series(dtype=str)).astype(str).ne("approved_review_pack_r2_r3_r4").sum())
    risk_negative_not_explicit_good = int(
        risk_dataset.loc[risk_dataset["risk_bad_y"].eq(0)]
        .apply(lambda row: (str(row["day"]), str(row["candidate_id"])) not in entry_good_keys, axis=1)
        .sum()
    )

    base_entry_y = pd.to_numeric(base["entry_y"], errors="coerce").fillna(-1).astype(int)
    review_entry_y = pd.to_numeric(entry_review["entry_y"], errors="coerce").fillna(-1).astype(int)
    base_actual_days = sorted(base["day"].astype(str).unique().tolist()) if "day" in base else []
    review_actual_days = sorted(entry_review["day"].astype(str).unique().tolist()) if "day" in entry_review else []

    entry_checks = [
        _check("base_guard_pass", base_guard.get("status") == ENTRY_BATCH_STATUS_PASS, {"status": base_guard.get("status", "")}),
        _check(
            "base_32d_counts_match",
            len(base_actual_days) == expected_base_days
            and len(base) == expected_base_rows
            and int(base_entry_y.eq(1).sum()) == expected_base_good
            and int(base_entry_y.eq(0).sum()) == expected_base_bad,
            {
                "days": len(base_actual_days),
                "rows": int(len(base)),
                "good": int(base_entry_y.eq(1).sum()),
                "bad": int(base_entry_y.eq(0).sum()),
            },
        ),
        _check("review_pack_guard_pass", review_guard.get("status") == "PASS_V5C_REVIEW_PACK_GUARD_READY_NO_TRAINING", {"status": review_guard.get("status", "")}),
        _check(
            "review_pack_counts_match",
            len(review_actual_days) == expected_review_days
            and len(entry_review) == expected_review_rows
            and int(review_entry_y.eq(1).sum()) == expected_review_good
            and int(review_entry_y.eq(0).sum()) == expected_review_bad
            and int(risk_review["risk_bad_y"].eq(1).sum()) == expected_review_risk_bad,
            {
                "days": len(review_actual_days),
                "entry_rows": int(len(entry_review)),
                "entry_good": int(review_entry_y.eq(1).sum()),
                "entry_bad": int(review_entry_y.eq(0).sum()),
                "risk_bad": int(risk_review["risk_bad_y"].eq(1).sum()),
            },
        ),
        _check("review_days_joined_to_x439", not missing_source_days and not missing_join_ids, {"missing_source_days": missing_source_days, "missing_join_ids": missing_join_ids}),
        _check("review_record_ids_match_source", not record_mismatches, {"mismatches": record_mismatches[:20], "mismatch_count": len(record_mismatches)}),
        _check("review_entry_times_match_source", not time_mismatches, {"mismatches": time_mismatches[:20], "mismatch_count": len(time_mismatches)}),
        _check("source_allowlist_matches_base_x439", not allowlist_mismatch_days, allowlist_mismatch_days),
        _check("source_full_causal_guards_pass", not full_guard_failures, full_guard_failures),
        _check(
            "entry_dataset_counts_match",
            len(actual_entry_days) == expected_entry_days
            and len(entry_batch) == expected_entry_rows
            and int(entry_y_counts.get("1", 0)) == expected_entry_good
            and int(entry_y_counts.get("0", 0)) == expected_entry_bad,
            {"days": len(actual_entry_days), "rows": int(len(entry_batch)), "entry_y_counts": entry_y_counts},
        ),
        _check("feature_count_expected", len(feature_columns) == active_expected_features, {"expected": active_expected_features, "actual": len(feature_columns)}),
        _check("target_manual_columns_not_in_X", not entry_target_columns_in_features, {"columns": entry_target_columns_in_features}),
        _check("forbidden_leakage_columns_absent_from_X", not forbidden_features, forbidden_features),
        _check("required_feature_columns_present", not missing_entry_features, {"missing": missing_entry_features[:50], "missing_count": len(missing_entry_features)}),
        _check(
            "entry_feature_values_no_null_or_inf",
            entry_feature_values["feature_nulls"] == 0 and entry_feature_values["feature_inf_count"] == 0,
            entry_feature_values,
        ),
        _check(
            "cs_max_source_time_utc_lte_entry_time_utc",
            not entry_cs_time.get("missing_column")
            and entry_cs_time.get("source_after_entry_rows", 0) == 0
            and entry_cs_time.get("source_na_rows", 0) == 0
            and entry_cs_time.get("entry_na_rows", 0) == 0,
            entry_cs_time,
        ),
        _check(
            "fcs_max_source_time_utc_lte_entry_time_utc",
            not entry_fcs_time.get("missing_column")
            and entry_fcs_time.get("source_after_entry_rows", 0) == 0
            and entry_fcs_time.get("source_na_rows", 0) == 0
            and entry_fcs_time.get("entry_na_rows", 0) == 0,
            entry_fcs_time,
        ),
        _check(
            "bollinger_layer_guard",
            (not enable_bollinger_layer)
            or (
                bollinger_context_manifest.get("status", "").startswith("PASS")
                and not bollinger_audit_columns_in_features
                and bollinger_feature_nulls == 0
                and entry_bb_time.get("source_after_entry_rows", 1) == 0
                and entry_bb_time.get("source_na_ready_rows", 1) == 0
            ),
            {
                "enabled": bool(enable_bollinger_layer),
                "context_status": bollinger_context_manifest.get("status", ""),
                "feature_contract": BOLLINGER_FEATURE_CONTRACT if enable_bollinger_layer else "",
                "bb_feature_count": bollinger_feature_count() if enable_bollinger_layer else 0,
                "audit_columns_in_X": bollinger_audit_columns_in_features,
                "bb_feature_nulls": bollinger_feature_nulls,
                "bb_source_time": entry_bb_time,
            },
        ),
        _check(
            "no_duplicate_day_candidate_or_record_id",
            entry_duplicate_day_candidate == 0 and entry_duplicate_day_record == 0,
            {"duplicate_day_candidate": entry_duplicate_day_candidate, "duplicate_day_record_id": entry_duplicate_day_record},
        ),
        _check("risk_bad_y_1_is_always_entry_y_0", not risk_not_entry_bad, {"risk_not_entry_bad": risk_not_entry_bad[:50], "count": len(risk_not_entry_bad)}),
        _check("no_good_vs_risk_conflicts", not good_risk_conflicts, {"conflicts": good_risk_conflicts[:50], "count": len(good_risk_conflicts)}),
        _check("training_and_forward_not_launched_by_builder", True, {"policy": "dataset_builder_only_no_training_no_forward"}),
    ]
    entry_status = ENTRY_BATCH_STATUS_PASS if all(item["status"] == "PASS" for item in entry_checks) else ENTRY_BATCH_STATUS_FAIL

    risk_checks = [
        _check("review_pack_guard_pass", review_guard.get("status") == "PASS_V5C_REVIEW_PACK_GUARD_READY_NO_TRAINING", {"status": review_guard.get("status", "")}),
        _check("risk_bad_y_1_is_always_entry_y_0", not risk_not_entry_bad, {"risk_not_entry_bad": risk_not_entry_bad[:50], "count": len(risk_not_entry_bad)}),
        _check("no_good_vs_risk_conflicts", not good_risk_conflicts, {"conflicts": good_risk_conflicts[:50], "count": len(good_risk_conflicts)}),
        _check(
            "riskgate_positive_negative_counts_match",
            int(risk_y_counts.get("1", 0)) == expected_risk_positive
            and int(risk_y_counts.get("0", 0)) >= expected_risk_safe_negative
            and len(risk_dataset) == int(risk_y_counts.get("1", 0)) + int(risk_y_counts.get("0", 0)),
            {"risk_bad_y_counts": risk_y_counts, "expected_positive": expected_risk_positive, "expected_safe_negative_min": expected_risk_safe_negative, "rows": int(len(risk_dataset))},
        ),
        _check("riskgate_negatives_explicit_safe_only", risk_negative_not_explicit_good == 0, {"negative_not_explicit_good": risk_negative_not_explicit_good}),
        _check("riskgate_dataset_uses_no_base_proxy_negatives", risk_dataset_base_rows == 0, {"base_proxy_rows": risk_dataset_base_rows}),
        _check("feature_count_expected", len(feature_columns) == active_expected_features, {"expected": active_expected_features, "actual": len(feature_columns)}),
        _check("target_manual_columns_not_in_X", not entry_target_columns_in_features, {"columns": entry_target_columns_in_features}),
        _check("forbidden_leakage_columns_absent_from_X", not forbidden_features, forbidden_features),
        _check("required_feature_columns_present", not missing_risk_features, {"missing": missing_risk_features[:50], "missing_count": len(missing_risk_features)}),
        _check(
            "riskgate_feature_values_no_null_or_inf",
            risk_feature_values["feature_nulls"] == 0 and risk_feature_values["feature_inf_count"] == 0,
            risk_feature_values,
        ),
        _check(
            "cs_max_source_time_utc_lte_entry_time_utc",
            not risk_cs_time.get("missing_column")
            and risk_cs_time.get("source_after_entry_rows", 0) == 0
            and risk_cs_time.get("source_na_rows", 0) == 0
            and risk_cs_time.get("entry_na_rows", 0) == 0,
            risk_cs_time,
        ),
        _check(
            "fcs_max_source_time_utc_lte_entry_time_utc",
            not risk_fcs_time.get("missing_column")
            and risk_fcs_time.get("source_after_entry_rows", 0) == 0
            and risk_fcs_time.get("source_na_rows", 0) == 0
            and risk_fcs_time.get("entry_na_rows", 0) == 0,
            risk_fcs_time,
        ),
        _check(
            "riskgate_bollinger_layer_guard",
            (not enable_bollinger_layer)
            or (
                bollinger_context_manifest.get("status", "").startswith("PASS")
                and not bollinger_audit_columns_in_features
                and risk_bb_time.get("source_after_entry_rows", 1) == 0
                and risk_bb_time.get("source_na_ready_rows", 1) == 0
            ),
            {
                "enabled": bool(enable_bollinger_layer),
                "context_status": bollinger_context_manifest.get("status", ""),
                "feature_contract": BOLLINGER_FEATURE_CONTRACT if enable_bollinger_layer else "",
                "bb_feature_count": bollinger_feature_count() if enable_bollinger_layer else 0,
                "audit_columns_in_X": bollinger_audit_columns_in_features,
                "bb_source_time": risk_bb_time,
            },
        ),
        _check(
            "no_duplicate_day_candidate_or_record_id",
            risk_duplicate_day_candidate == 0 and risk_duplicate_day_record == 0,
            {"duplicate_day_candidate": risk_duplicate_day_candidate, "duplicate_day_record_id": risk_duplicate_day_record},
        ),
        _check("training_and_forward_not_launched_by_builder", True, {"policy": "dataset_builder_only_no_training_no_forward"}),
    ]
    risk_status = RISKGATE_STATUS_PASS if all(item["status"] == "PASS" for item in risk_checks) else RISKGATE_STATUS_FAIL

    allowlist_payload = {
        "status": entry_status,
        "created_utc": utc_now(),
        "schema_version": 1,
        "range": {"start_day": train_start_day, "end_day": train_end_day},
        "feature_columns": feature_columns,
        "feature_count": len(feature_columns),
        "base_feature_count": len(base_feature_columns),
        "bollinger_layer": {
            "enabled": bool(enable_bollinger_layer),
            "layer_id": BOLLINGER_LAYER_ID if enable_bollinger_layer else "",
            "feature_contract": BOLLINGER_FEATURE_CONTRACT if enable_bollinger_layer else "",
            "feature_columns": BOLLINGER_FEATURE_COLUMNS if enable_bollinger_layer else [],
            "audit_columns_not_X": BOLLINGER_AUDIT_COLUMNS if enable_bollinger_layer else [],
        },
        "target_columns_allowed_as_y_not_X": sorted([column for column in EXTENDED_TARGET_OR_MANUAL_COLUMNS if column in entry_batch.columns]),
        "guardrails": [
            "X439_causal_features_plus_optional_bollinger_causal_features",
            "review_labels_are_teacher_targets_not_features",
            "risk_bad_y_is_target_not_feature",
            "risk_bad_y_1_always_entry_y_0",
            "cs_fcs_source_times_lte_entry_time",
            "bb_source_time_lte_entry_time_when_bollinger_enabled",
            "bb_preview_audit_columns_are_not_X",
        ],
    }
    risk_allowlist_payload = dict(allowlist_payload)
    risk_allowlist_payload["status"] = risk_status
    risk_allowlist_payload["target"] = "risk_bad_y"

    entry_manifest = {
        "status": entry_status,
        "created_utc": utc_now(),
        "schema_version": 1,
        "dataset_kind": "ENTRY_TRAIN_DATASET",
        "pipeline_variant": "V5C_REVIEW_SUPERVISED",
        "range": {"start_day": train_start_day, "end_day": train_end_day},
        "day_count": len(actual_entry_days),
        "expected_day_count": expected_entry_days,
        "rows": int(len(entry_batch)),
        "expected_rows": expected_entry_rows,
        "entry_y_counts": entry_y_counts,
        "expected_entry_y_counts": {"1": expected_entry_good, "0": expected_entry_bad},
        "feature_count": len(feature_columns),
        "expected_feature_count": active_expected_features,
        "feature_columns": feature_columns,
        "base_feature_count": len(base_feature_columns),
        "base_feature_columns": base_feature_columns,
        "bollinger_layer": {
            "enabled": bool(enable_bollinger_layer),
            "layer_id": BOLLINGER_LAYER_ID if enable_bollinger_layer else "",
            "feature_contract": BOLLINGER_FEATURE_CONTRACT if enable_bollinger_layer else "",
            "feature_count": bollinger_feature_count() if enable_bollinger_layer else 0,
            "feature_columns": BOLLINGER_FEATURE_COLUMNS if enable_bollinger_layer else [],
            "audit_columns_not_X": BOLLINGER_AUDIT_COLUMNS if enable_bollinger_layer else [],
            "context": bollinger_context_manifest,
            "base_summary": base_bollinger_summary,
            "review_summary": review_bollinger_summary,
            "preview_policy_ru": "Bollinger preview только показывает риск входа на хаях/down-channel/falling-knife/low-move-capacity; ручной GOOD/BAD не переписывается.",
        },
        "base_source": {
            "start_day": base_start_day,
            "end_day": base_end_day,
            "batch_csv": rel(base_batch_csv),
            "allowlist_json": rel(base_allowlist_json),
            "guard_json": rel(base_guard_json),
            "rows": int(len(base)),
            "entry_good": int(base_entry_y.eq(1).sum()),
            "entry_bad": int(base_entry_y.eq(0).sum()),
            "feature_fill_summary": base_fill_summary,
        },
        "review_pack": {
            "pack_dir": rel(review_pack_dir),
            "entry_csv": rel(review_entry_path),
            "riskgate_csv": rel(review_risk_path),
            "manifest_json": rel(review_manifest_path),
            "guard_json": rel(review_guard_path),
            "start_day": review_start_day,
            "end_day": review_end_day,
            "days": len(actual_review_days),
            "entry_rows": int(len(entry_review)),
            "entry_good": int(review_entry_y.eq(1).sum()),
            "entry_bad": int(review_entry_y.eq(0).sum()),
            "risk_bad": int(risk_review["risk_bad_y"].eq(1).sum()),
            "policy": "risk_bad_y_1_also_entry_y_0",
        },
        "source_inputs": source_inputs,
        "days": _day_summary(entry_batch, target_column="entry_y"),
        "feature_fill_summary": entry_fill_summary,
        "next_required_step": "training_guard_then_user_runs_train_no_forward_until_model_pass",
        "outputs": {
            "batch_csv": rel(entry_paths["csv"]),
            "feature_allowlist": rel(entry_paths["allowlist"]),
            "manifest": rel(entry_paths["manifest"]),
            "audit": rel(entry_paths["audit"]),
            "guard": rel(entry_paths["guard"]),
            "riskgate_dataset_csv": rel(risk_paths["csv"]),
            "riskgate_guard": rel(risk_paths["guard"]),
        },
    }
    entry_guard = {
        "status": entry_status,
        "created_utc": utc_now(),
        "schema_version": 1,
        "dataset_kind": "ENTRY_TRAIN_DATASET",
        "range": entry_manifest["range"],
        "rows": int(len(entry_batch)),
        "expected_rows": expected_entry_rows,
        "entry_y_counts": entry_y_counts,
        "expected_entry_y_counts": entry_manifest["expected_entry_y_counts"],
        "feature_count": len(feature_columns),
        "expected_feature_count": active_expected_features,
        "feature_columns": feature_columns,
        "bollinger_layer": entry_manifest["bollinger_layer"],
        "checks": entry_checks,
        "outputs": entry_manifest["outputs"],
        "no_training_no_forward": True,
    }

    risk_manifest = {
        "status": risk_status,
        "created_utc": utc_now(),
        "schema_version": 1,
        "dataset_kind": "RISKGATE_TRAIN_DATASET",
        "pipeline_variant": "V5C_REVIEW_SUPERVISED",
        "range": {"start_day": train_start_day, "end_day": train_end_day},
        "review_range": {"start_day": review_start_day, "end_day": review_end_day},
        "rows": int(len(risk_dataset)),
        "risk_bad_y_counts": risk_y_counts,
        "expected_risk_bad_y_counts": {"1": expected_risk_positive, "0_min": expected_risk_safe_negative},
        "negative_policy": "explicit_safe_only_review_entry_good",
        "base_good_proxy_audit_pool": expected_base_good,
        "base_good_proxy_used_as_training_negative": False,
        "feature_count": len(feature_columns),
        "expected_feature_count": active_expected_features,
        "feature_columns": feature_columns,
        "base_feature_count": len(base_feature_columns),
        "base_feature_columns": base_feature_columns,
        "bollinger_layer": entry_manifest["bollinger_layer"],
        "days": _day_summary(risk_dataset, target_column="risk_bad_y"),
        "feature_fill_summary": risk_fill_summary,
        "outputs": {
            "riskgate_dataset_csv": rel(risk_paths["csv"]),
            "feature_allowlist": rel(risk_paths["allowlist"]),
            "manifest": rel(risk_paths["manifest"]),
            "audit": rel(risk_paths["audit"]),
            "guard": rel(risk_paths["guard"]),
        },
    }
    risk_guard = {
        "status": risk_status,
        "created_utc": utc_now(),
        "schema_version": 1,
        "dataset_kind": "RISKGATE_TRAIN_DATASET",
        "range": risk_manifest["range"],
        "rows": int(len(risk_dataset)),
        "risk_bad_y_counts": risk_y_counts,
        "feature_count": len(feature_columns),
        "expected_feature_count": active_expected_features,
        "feature_columns": feature_columns,
        "bollinger_layer": entry_manifest["bollinger_layer"],
        "checks": risk_checks,
        "outputs": risk_manifest["outputs"],
        "no_training_no_forward": True,
    }

    entry_batch.to_csv(entry_paths["csv"], index=False, encoding="utf-8-sig")
    risk_dataset.to_csv(risk_paths["csv"], index=False, encoding="utf-8-sig")
    write_json(entry_paths["allowlist"], allowlist_payload)
    write_json(entry_paths["manifest"], entry_manifest)
    write_json(entry_paths["guard"], entry_guard)
    _write_entry_audit(entry_paths["audit"], entry_manifest, entry_guard)
    write_json(risk_paths["allowlist"], risk_allowlist_payload)
    write_json(risk_paths["manifest"], risk_manifest)
    write_json(risk_paths["guard"], risk_guard)
    _write_riskgate_audit(risk_paths["audit"], risk_manifest, risk_guard)

    if strict and entry_status != ENTRY_BATCH_STATUS_PASS:
        raise ValueError(f"ENTRY dataset guard failed: {entry_status}")
    if strict and risk_status != RISKGATE_STATUS_PASS:
        raise ValueError(f"RiskGate dataset guard failed: {risk_status}")

    combined_manifest = {
        "status": "PASS_V5C_REVIEW_SUPERVISED_DATASETS_READY_NO_TRAINING"
        if entry_status == ENTRY_BATCH_STATUS_PASS and risk_status == RISKGATE_STATUS_PASS
        else "FAIL_V5C_REVIEW_SUPERVISED_DATASETS",
        "created_utc": utc_now(),
        "entry_dataset": entry_manifest,
        "entry_guard": entry_guard,
        "riskgate_dataset": risk_manifest,
        "riskgate_guard": risk_guard,
    }
    return entry_batch, risk_dataset, combined_manifest, entry_guard, risk_guard


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build STAS5 V5C ENTRY and RiskGate supervised train datasets from approved R2/R3/R4 review pack.")
    parser.add_argument("--train-start-day", default=TRAIN_START_DAY)
    parser.add_argument("--train-end-day", default=TRAIN_END_DAY)
    parser.add_argument("--review-pack-dir", type=Path, default=REVIEW_PACK_DIR)
    parser.add_argument("--forward-runs-dir", type=Path, default=V5C_FORWARD_RUNS_DIR)
    parser.add_argument("--output-dir", type=Path, default=V5C_ROOT)
    parser.add_argument("--enable-bollinger-layer", action="store_true")
    parser.add_argument("--bollinger-ohlcv-csv", type=Path, default=None)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args(argv)

    _entry, _risk, manifest, entry_guard, risk_guard = build_v5c_review_supervised_datasets(
        train_start_day=args.train_start_day,
        train_end_day=args.train_end_day,
        review_pack_dir=args.review_pack_dir,
        forward_runs_dir=args.forward_runs_dir,
        output_dir=args.output_dir,
        enable_bollinger_layer=args.enable_bollinger_layer,
        bollinger_ohlcv_csv=args.bollinger_ohlcv_csv,
        force=args.force,
        strict=not args.no_strict,
    )
    summary = {
        "status": manifest["status"],
        "entry_guard_status": entry_guard["status"],
        "riskgate_guard_status": risk_guard["status"],
        "entry_rows": manifest["entry_dataset"]["rows"],
        "entry_y_counts": manifest["entry_dataset"]["entry_y_counts"],
        "feature_count": manifest["entry_dataset"]["feature_count"],
        "bollinger_layer": manifest["entry_dataset"].get("bollinger_layer", {}),
        "riskgate_rows": manifest["riskgate_dataset"]["rows"],
        "risk_bad_y_counts": manifest["riskgate_dataset"]["risk_bad_y_counts"],
        "outputs": {
            "entry_batch_csv": manifest["entry_dataset"]["outputs"]["batch_csv"],
            "entry_guard": manifest["entry_dataset"]["outputs"]["guard"],
            "riskgate_dataset_csv": manifest["riskgate_dataset"]["outputs"]["riskgate_dataset_csv"],
            "riskgate_guard": manifest["riskgate_dataset"]["outputs"]["guard"],
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
