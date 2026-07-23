from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from mlbotnav.stas5_common import PROJECT_ROOT, compact_day, ensure_parent, iter_days, normalize_day, rel, run_stamp, utc_now, write_json
from mlbotnav.stas5_entry_ranker_train import _positive_proba, _prepare_feature_matrix
from mlbotnav.stas5_v5_batch_dataset_builder import (
    DEFAULT_EXPECTED_FEATURES,
    STATUS_PASS as BATCH_GUARD_PASS,
    TARGET_OR_MANUAL_COLUMNS,
    _fill_feature_gaps,
    _forbidden_feature_matches,
    _source_time_check,
    build_v5_batch_dataset,
)
from mlbotnav.stas5_v5c_bollinger_layer import (
    BOLLINGER_AUDIT_COLUMNS,
    BOLLINGER_FEATURE_COLUMNS,
    BOLLINGER_FEATURE_CONTRACT,
    BOLLINGER_LAYER_ID,
    attach_bollinger_features,
    bollinger_source_time_check,
)
from mlbotnav.stas5_v5_causal_structure_builder import build_causal_structure_package
from mlbotnav.stas5_v5_full_causal_structure_builder import STATUS as FULL_CAUSAL_GUARD_PASS
from mlbotnav.stas5_v5_full_causal_structure_builder import build_full_causal_structure_package
from mlbotnav.stas5_v5_two_block_ml import (
    KEY_COLUMNS,
    PHASE_PREFIX,
    POST_TRAIN_GUARD_PASS,
    STATE_PREFIX,
    _apply_entry_decision,
    _check,
    _proba_predictions,
    run_training_guard,
    train_two_block_ml,
)
from mlbotnav.stas5_v5c_riskgate_ml import (
    RISKGATE_POST_TRAIN_GUARD_PASS,
    apply_riskgate_to_entry_decisions,
    apply_v5c_riskgate_forward,
    riskgate_dataset_paths,
    train_v5c_riskgate_ml,
)


TRAIN_START_DAY = "2026-01-27"
TRAIN_END_DAY = "2026-03-06"
FORWARD_START_DAY = "2026-03-07"
FORWARD_END_DAY = "2026-03-13"
EXPECTED_FORWARD_DAYS = 7
DEFAULT_CONTEXT_WARMUP_MINUTES = 720

SYMBOL = "SOLUSDT"
TIMEFRAME = "1m"

SOURCE_V5_ROOT = PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5"
V5C_ROOT = PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5c"
V5C_CONTEXT_DIR = V5C_ROOT / "ohlcv_contexts"
V5C_MODEL_RUNS_DIR = V5C_ROOT / "model" / "runs"
V5C_FORWARD_RUNS_DIR = V5C_ROOT / "forward" / "runs"
V5C_LATEST_MODEL_POINTER = V5C_ROOT / "model" / "STAS5_V5C_LATEST_TWO_BLOCK_MODEL_RUN.json"
V5C_LATEST_FORWARD_POINTER = V5C_ROOT / "forward" / "STAS5_V5C_LATEST_TWO_BLOCK_FORWARD_RUN.json"
FULL274_RUNS_DIR = PROJECT_ROOT / "STAS5_ML_CORE" / "runs"

V5C_TRAIN_MARKET_PASSPORTS_PASS = "PASS_V5C_CONTINUOUS_TRAIN_MARKET_PASSPORTS_READY"
V5C_TRAIN_MARKET_PASSPORTS_FAIL = "FAIL_V5C_CONTINUOUS_TRAIN_MARKET_PASSPORTS"
V5C_FORWARD_DATASET_PASS = "PASS_V5C_CONTINUOUS_FORWARD_DATASET_READY_NO_FUTURE"
V5C_FORWARD_DATASET_FAIL = "FAIL_V5C_CONTINUOUS_FORWARD_DATASET"
ENTRY_DECISION_POLICY_QUANTILES = {
    "normal": {"enter": 0.90, "watch": 0.60},
    "wide_review": {"enter": 0.80, "watch": 0.50},
}


def _v5c_forward_pass_status(start_day: str, end_day: str) -> str:
    return f"PASS_V5C_CONTINUOUS_TWO_BLOCK_FORWARD_{compact_day(start_day)}_{compact_day(end_day)}_BLIND_NO_FUTURE"


def _v5c_forward_fail_status(start_day: str, end_day: str) -> str:
    return f"FAIL_V5C_CONTINUOUS_TWO_BLOCK_FORWARD_{compact_day(start_day)}_{compact_day(end_day)}"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _thresholds_for_entry_decision_policy(
    *,
    train_manifest: dict[str, Any],
    selected_model_key: str,
    selected_package: dict[str, Any],
    entry_decision_policy: str,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, Any]:
    policy = str(entry_decision_policy or "trained").strip().lower()
    base_thresholds = dict(selected_package["thresholds"])
    if policy == "trained":
        base_thresholds["active_decision_policy"] = "trained_manifest_thresholds"
        return base_thresholds
    if policy not in ENTRY_DECISION_POLICY_QUANTILES:
        raise ValueError(f"unknown entry_decision_policy: {entry_decision_policy}")

    score_column = "ENTRY_BASELINE_OOF_SCORE" if selected_model_key == "entry_baseline" else "ENTRY_ML_OOF_SCORE"
    predictions_rel = train_manifest.get("artifacts", {}).get("train_oof_predictions", "")
    if not predictions_rel:
        raise ValueError("train_oof_predictions artifact is missing; cannot calibrate decision policy")
    predictions_path = project_root / predictions_rel
    train_oof = pd.read_csv(predictions_path, encoding="utf-8-sig")
    if score_column not in train_oof.columns:
        raise ValueError(f"train OOF score column is missing for policy calibration: {score_column}")
    scores = pd.to_numeric(train_oof[score_column], errors="coerce").dropna()
    if scores.empty:
        raise ValueError(f"train OOF score column has no numeric values: {score_column}")

    quantiles = ENTRY_DECISION_POLICY_QUANTILES[policy]
    enter_threshold = float(scores.quantile(float(quantiles["enter"])))
    watch_threshold = float(scores.quantile(float(quantiles["watch"])))
    if watch_threshold > enter_threshold:
        watch_threshold = enter_threshold
    calibrated = dict(base_thresholds)
    calibrated["entry_enter_threshold"] = round(enter_threshold, 10)
    calibrated["entry_watch_threshold"] = round(watch_threshold, 10)
    calibrated["active_decision_policy"] = f"train_oof_quantile_{policy}_no_forward_tuning"
    calibrated["policy"] = calibrated["active_decision_policy"]
    calibrated["source_score_column"] = score_column
    calibrated["source_train_oof_predictions"] = rel(predictions_path)
    calibrated["enter_quantile"] = float(quantiles["enter"])
    calibrated["watch_quantile"] = float(quantiles["watch"])
    calibrated["train_oof_rows"] = int(len(scores))
    calibrated["train_oof_predicted_enter"] = int((scores >= enter_threshold).sum())
    calibrated["train_oof_predicted_watch_or_enter"] = int((scores >= watch_threshold).sum())
    return calibrated


def _read_allowlist(path: Path) -> list[str]:
    return [str(column) for column in _load_json(path).get("feature_columns", [])]


def _ohlcv_day_path(day: str, *, project_root: Path = PROJECT_ROOT) -> Path:
    return (
        project_root
        / "data"
        / "core"
        / "bybit_ohlcv"
        / f"dt={normalize_day(day)}"
        / f"tf={TIMEFRAME}"
        / f"symbol={SYMBOL}"
        / "part-final.csv"
    )


def build_continuous_ohlcv_context(
    *,
    start_day: str,
    end_day: str,
    min_open_time_utc: str | pd.Timestamp | None = None,
    output_dir: Path = V5C_CONTEXT_DIR,
    project_root: Path = PROJECT_ROOT,
    strict: bool = True,
) -> dict[str, Any]:
    start_day = normalize_day(start_day)
    end_day = normalize_day(end_day)
    days = iter_days(start_day, end_day)
    frames: list[pd.DataFrame] = []
    inputs: list[dict[str, Any]] = []
    missing: list[str] = []
    for day in days:
        path = _ohlcv_day_path(day, project_root=project_root)
        if not path.exists():
            missing.append(day)
            continue
        frame = pd.read_csv(path, encoding="utf-8-sig")
        if "open_time_utc" not in frame.columns:
            raise ValueError(f"OHLCV missing open_time_utc: {path}")
        frame = frame.copy()
        frame["open_time_utc"] = pd.to_datetime(frame["open_time_utc"], utc=True)
        frames.append(frame)
        inputs.append({"day": day, "path": rel(path), "rows": int(len(frame))})

    context = pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()
    duplicate_open_time_count = 0
    if not context.empty:
        duplicate_open_time_count = int(context.duplicated(["open_time_utc"]).sum())
        context = (
            context.sort_values("open_time_utc")
            .drop_duplicates(["open_time_utc"], keep="last")
            .reset_index(drop=True)
        )
        if min_open_time_utc is not None:
            min_open_time = pd.Timestamp(min_open_time_utc)
            if min_open_time.tzinfo is None:
                min_open_time = min_open_time.tz_localize("UTC")
            min_open_time = min_open_time.tz_convert("UTC")
            context = context[context["open_time_utc"] >= min_open_time].reset_index(drop=True)
        else:
            min_open_time = None
    else:
        min_open_time = None

    prefix = f"STAS5_V5C_OHLCV_CONTEXT_{compact_day(start_day)}_{compact_day(end_day)}"
    if min_open_time is not None:
        prefix += f"_FROM_{min_open_time.strftime('%Y%m%d_%H%M')}"
    output_csv = output_dir / f"{prefix}.csv"
    output_manifest = output_dir / f"{prefix}.manifest.json"
    ensure_parent(output_csv)
    context.to_csv(output_csv, index=False, encoding="utf-8-sig")

    first_time = context["open_time_utc"].iloc[0] if not context.empty else ""
    last_time = context["open_time_utc"].iloc[-1] if not context.empty else ""
    checks = [
        _check("context_days_present", not missing and len(inputs) == len(days), {"missing_days": missing, "actual": len(inputs), "expected": len(days)}),
        _check("context_rows_positive", len(context) > 0, {"rows": int(len(context))}),
        _check("context_open_time_unique", duplicate_open_time_count == 0, {"duplicate_open_time_count": duplicate_open_time_count}),
    ]
    status = "PASS_V5C_CONTINUOUS_OHLCV_CONTEXT_READY" if all(item["status"] == "PASS" for item in checks) else "FAIL_V5C_CONTINUOUS_OHLCV_CONTEXT"
    manifest = {
        "status": status,
        "created_utc": utc_now(),
        "context_start_day": start_day,
        "context_end_day": end_day,
        "min_open_time_utc": min_open_time,
        "days": days,
        "rows": int(len(context)),
        "first_open_time_utc": first_time,
        "last_open_time_utc": last_time,
        "duplicate_open_time_count": duplicate_open_time_count,
        "source_inputs": inputs,
        "outputs": {"context_csv": rel(output_csv), "manifest": rel(output_manifest)},
        "checks": checks,
    }
    write_json(output_manifest, manifest)
    if strict and status.startswith("FAIL"):
        raise ValueError(f"continuous OHLCV context guard failed: {status}")
    return manifest


def _rolling_context_window(target_day: str, *, global_start_day: str, warmup_minutes: int) -> tuple[str, pd.Timestamp | None]:
    target_day = normalize_day(target_day)
    global_start_day = normalize_day(global_start_day)
    if warmup_minutes <= 0:
        return global_start_day, None
    target_start = pd.Timestamp(f"{target_day}T00:00:00Z")
    min_open_time = target_start - pd.Timedelta(minutes=int(warmup_minutes))
    source_start = max(pd.Timestamp(global_start_day), min_open_time.normalize().tz_localize(None))
    return source_start.strftime("%Y-%m-%d"), min_open_time


def _approved_train_source_paths(day: str) -> dict[str, Path]:
    compact = compact_day(day)
    day_dir = SOURCE_V5_ROOT / "market_passports" / compact
    prefix = f"STAS5_V5_MARKET_PASSPORT_{compact}"
    return {
        "ml_ready_274": day_dir / f"{prefix}_ML_READY_274F_ENTRY_PHASE_STATE_REASON_TARGETS_V2.csv",
        "allowlist_274": day_dir / f"{prefix}_FEATURE_ALLOWLIST_274_ENTRY_PHASE_STATE_REASON_V2.json",
    }


def _v5c_day_dir(day: str) -> Path:
    return V5C_ROOT / "market_passports" / compact_day(day)


def _v5c_full_day_paths(day: str) -> dict[str, Path]:
    compact = compact_day(day)
    day_dir = _v5c_day_dir(day)
    prefix = f"STAS5_V5_MARKET_PASSPORT_{compact}"
    return {
        "csv": day_dir / f"{prefix}_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv",
        "allowlist": day_dir / f"{prefix}_FEATURE_ALLOWLIST_274_PLUS_FULL_CAUSAL_STRUCTURE_V1.json",
    }


def _v5c_expected_train_counts_from_daily(
    *,
    start_day: str,
    end_day: str,
    strict: bool = True,
) -> dict[str, Any]:
    start_day = normalize_day(start_day)
    end_day = normalize_day(end_day)
    days = iter_days(start_day, end_day)
    rows = 0
    good = 0
    bad = 0
    feature_columns: list[str] | None = None
    missing: list[str] = []
    mismatched_allowlists: list[str] = []

    for day in days:
        paths = _v5c_full_day_paths(day)
        if not paths["csv"].exists() or not paths["allowlist"].exists():
            missing.append(day)
            continue
        features = _read_allowlist(paths["allowlist"])
        if feature_columns is None:
            feature_columns = features
        elif features != feature_columns:
            mismatched_allowlists.append(day)
        frame = pd.read_csv(paths["csv"], encoding="utf-8-sig", usecols=lambda column: column == "entry_y")
        if "entry_y" not in frame.columns:
            raise ValueError(f"entry_y missing in V5C daily market passport: {paths['csv']}")
        entry_y = pd.to_numeric(frame["entry_y"], errors="coerce").fillna(-1).astype(int)
        rows += int(len(frame))
        good += int(entry_y.eq(1).sum())
        bad += int(entry_y.eq(0).sum())

    if strict and (missing or mismatched_allowlists):
        raise ValueError(
            "V5C expected train counts cannot be computed: "
            f"missing_days={missing}, mismatched_allowlists={mismatched_allowlists}"
        )
    return {
        "source": "v5c_daily_market_passports",
        "start_day": start_day,
        "end_day": end_day,
        "days": len(days),
        "rows": rows,
        "good": good,
        "bad": bad,
        "features": len(feature_columns or []),
        "missing_days": missing,
        "mismatched_allowlists": mismatched_allowlists,
    }


def _v5c_expected_train_counts_from_manifest(paths: dict[str, Path]) -> dict[str, Any] | None:
    if not paths["manifest"].exists():
        return None
    manifest = _load_json(paths["manifest"])
    entry_counts = manifest.get("expected_entry_y_counts") or manifest.get("entry_y_counts") or {}
    try:
        return {
            "source": "v5c_batch_manifest",
            "start_day": manifest["range"]["start_day"],
            "end_day": manifest["range"]["end_day"],
            "days": int(manifest.get("expected_day_count", manifest.get("day_count", 0))),
            "rows": int(manifest.get("expected_rows", manifest.get("rows", 0))),
            "good": int(entry_counts.get("1", 0)),
            "bad": int(entry_counts.get("0", 0)),
            "features": int(manifest.get("expected_feature_count", manifest.get("feature_count", DEFAULT_EXPECTED_FEATURES))),
        }
    except (KeyError, TypeError, ValueError):
        return None


def _v5c_expected_train_counts(
    *,
    start_day: str,
    end_day: str,
    paths: dict[str, Path] | None = None,
    strict: bool = True,
) -> dict[str, Any]:
    if paths:
        from_manifest = _v5c_expected_train_counts_from_manifest(paths)
        if from_manifest:
            return from_manifest
    return _v5c_expected_train_counts_from_daily(start_day=start_day, end_day=end_day, strict=strict)


def build_continuous_train_market_passports(
    *,
    start_day: str = TRAIN_START_DAY,
    end_day: str = TRAIN_END_DAY,
    context_start_day: str = TRAIN_START_DAY,
    context_warmup_minutes: int = DEFAULT_CONTEXT_WARMUP_MINUTES,
    strict: bool = True,
) -> dict[str, Any]:
    start_day = normalize_day(start_day)
    end_day = normalize_day(end_day)
    context_start_day = normalize_day(context_start_day)
    outputs: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []

    for day in iter_days(start_day, end_day):
        source = _approved_train_source_paths(day)
        missing_sources = [name for name, path in source.items() if not path.exists()]
        checks.append(_check(f"{compact_day(day)}_approved_274_source_present", not missing_sources, {"missing": missing_sources}))
        if missing_sources:
            if strict:
                raise FileNotFoundError(f"approved V5 274 source missing for {day}: {missing_sources}")
            continue

        source_start_day, min_open_time = _rolling_context_window(
            day,
            global_start_day=context_start_day,
            warmup_minutes=context_warmup_minutes,
        )
        context = build_continuous_ohlcv_context(
            start_day=source_start_day,
            end_day=day,
            min_open_time_utc=min_open_time,
            output_dir=V5C_CONTEXT_DIR / "train",
            strict=strict,
        )
        day_dir = _v5c_day_dir(day)
        day_dir.mkdir(parents=True, exist_ok=True)
        causal_guard = build_causal_structure_package(
            day=day,
            ml_ready_path=source["ml_ready_274"],
            allowlist_path=source["allowlist_274"],
            ohlcv_path=PROJECT_ROOT / context["outputs"]["context_csv"],
            output_dir=day_dir,
        )
        full_guard = build_full_causal_structure_package(
            day=day,
            ml_ready_plus_path=Path(causal_guard["outputs"]["ml_ready_274f_plus_causal_structure_targets"]),
            allowlist_plus_path=Path(causal_guard["outputs"]["feature_allowlist_274_plus_causal_structure"]),
            ohlcv_path=PROJECT_ROOT / context["outputs"]["context_csv"],
            output_dir=day_dir,
            draw_plot=False,
        )
        full_pass = full_guard.get("status") == FULL_CAUSAL_GUARD_PASS
        checks.append(_check(f"{compact_day(day)}_full_causal_guard_pass", full_pass, {"status": full_guard.get("status")}))
        outputs.append(
            {
                "day": day,
                "source_ml_ready_274": rel(source["ml_ready_274"]),
                "source_allowlist_274": rel(source["allowlist_274"]),
                "context_start_day": context_start_day,
                "context_source_start_day": source_start_day,
                "context_end_day": day,
                "context_warmup_minutes": context_warmup_minutes,
                "context_csv": context["outputs"]["context_csv"],
                "context_rows": context["rows"],
                "rows": int(full_guard.get("rows", 0)),
                "feature_count": int(full_guard.get("feature_count", 0)),
                "guard_status": full_guard.get("status", ""),
                "ml_ready_full": full_guard["outputs"]["ml_ready_full"],
                "guard_full": full_guard["outputs"]["guard"],
            }
        )

    status = V5C_TRAIN_MARKET_PASSPORTS_PASS if all(item["status"] == "PASS" for item in checks) else V5C_TRAIN_MARKET_PASSPORTS_FAIL
    manifest_path = V5C_ROOT / f"STAS5_V5C_CONTINUOUS_TRAIN_MARKET_PASSPORTS_{compact_day(start_day)}_{compact_day(end_day)}_MANIFEST_V1.json"
    manifest = {
        "status": status,
        "created_utc": utc_now(),
        "pipeline_variant": "V5C_CONTINUOUS",
        "range": {"start_day": start_day, "end_day": end_day},
        "context_policy": {
            "mode": "rolling_past_context",
            "mode_detail": "rolling_continuous_warmup",
            "context_start_day": context_start_day,
            "context_warmup_minutes": context_warmup_minutes,
            "context_end_day": "target_day",
            "feature_rule": "for each candidate cs/fcs use only OHLCV with source_time < entry_time_utc",
        },
        "day_count": len(outputs),
        "expected_day_count": len(iter_days(start_day, end_day)),
        "outputs": outputs,
        "checks": checks,
        "manifest_path": rel(manifest_path),
    }
    write_json(manifest_path, manifest)
    if strict and status != V5C_TRAIN_MARKET_PASSPORTS_PASS:
        raise ValueError(f"continuous train market passports guard failed: {status}")
    return manifest


def _write_v5c_batch_audit(path: Path, manifest: dict[str, Any], guard: dict[str, Any], train_context_manifest: dict[str, Any]) -> None:
    lines = [
        "# STAS5 V5C Continuous Batch Audit",
        "",
        f"Статус: `{guard['status']}`.",
        "",
        "Контур `V5C_CONTINUOUS` пересобирает `cs_*` и `fcs_*` не на изолированном дневном файле, а на расширяющемся прошлом контексте.",
        "Граница дня остается только отчетной границей, а не сбросом рыночной памяти.",
        "",
        f"- train range: `{manifest['range']['start_day']}..{manifest['range']['end_day']}`",
        f"- rows: `{manifest['rows']}`",
        f"- entry_y: `{manifest['entry_y_counts']}`",
        f"- features: `{manifest['feature_count']}`",
        f"- continuous market passports: `{train_context_manifest['status']}`",
        "",
        "No-future правило: каждая строка-кандидат использует только `cs_max_source_time_utc` и `fcs_max_source_time_utc` не позже своего `entry_time_utc`.",
        "Teacher-поля `entry_y/phase_y/state_y/reason_y` остаются целями/разметкой и не входят в `X`.",
        "",
        "Checks:",
    ]
    for item in guard["checks"]:
        lines.append(f"- `{item['check']}`: `{item['status']}`")
    ensure_parent(path)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_continuous_batch(
    *,
    start_day: str = TRAIN_START_DAY,
    end_day: str = TRAIN_END_DAY,
    context_start_day: str = TRAIN_START_DAY,
    context_warmup_minutes: int = DEFAULT_CONTEXT_WARMUP_MINUTES,
    strict: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any]]:
    train_context_manifest = build_continuous_train_market_passports(
        start_day=start_day,
        end_day=end_day,
        context_start_day=context_start_day,
        context_warmup_minutes=context_warmup_minutes,
        strict=strict,
    )
    expected = _v5c_expected_train_counts_from_daily(start_day=start_day, end_day=end_day, strict=strict)
    dataset, manifest, guard = build_v5_batch_dataset(
        start_day=start_day,
        end_day=end_day,
        v5_root=V5C_ROOT,
        output_dir=V5C_ROOT,
        batch_family="STAS5_V5C",
        expected_days=expected["days"],
        expected_rows=expected["rows"],
        expected_good=expected["good"],
        expected_bad=expected["bad"],
        expected_features=expected["features"] or DEFAULT_EXPECTED_FEATURES,
        require_no_training_forward_artifacts=False,
        strict=strict,
    )

    manifest["pipeline_variant"] = "V5C_CONTINUOUS"
    manifest["continuous_context_manifest"] = train_context_manifest["manifest_path"]
    manifest["continuous_context_policy"] = train_context_manifest["context_policy"]
    manifest["expected_train_counts"] = expected
    guard["pipeline_variant"] = "V5C_CONTINUOUS"
    guard["continuous_context_manifest"] = train_context_manifest["manifest_path"]
    guard["continuous_context_policy"] = train_context_manifest["context_policy"]
    guard["expected_train_counts"] = expected
    guard["checks"].append(
        _check(
            "continuous_train_context_ready",
            train_context_manifest["status"] == V5C_TRAIN_MARKET_PASSPORTS_PASS,
            {"status": train_context_manifest["status"], "day_count": train_context_manifest["day_count"]},
        )
    )
    guard["status"] = BATCH_GUARD_PASS if all(item["status"] == "PASS" for item in guard["checks"]) else "FAIL_V5C_CONTINUOUS_BATCH_GUARD"
    manifest["status"] = guard["status"]

    outputs = manifest["outputs"]
    write_json(PROJECT_ROOT / outputs["manifest"], manifest)
    write_json(PROJECT_ROOT / outputs["guard"], guard)
    _write_v5c_batch_audit(PROJECT_ROOT / outputs["audit"], manifest, guard, train_context_manifest)
    if strict and guard["status"] != BATCH_GUARD_PASS:
        raise ValueError(f"V5C continuous batch guard failed: {guard['status']}")
    return dataset, manifest, guard


def _v5c_batch_feature_count_from_manifest(start_day: str, end_day: str) -> int:
    prefix = f"STAS5_V5C_BATCH_{compact_day(start_day)}_{compact_day(end_day)}"
    manifest_path = V5C_ROOT / f"{prefix}_MANIFEST_V1.json"
    if manifest_path.exists():
        try:
            manifest = _load_json(manifest_path)
            return int(manifest.get("feature_count") or manifest.get("expected_feature_count") or DEFAULT_EXPECTED_FEATURES)
        except Exception:
            return DEFAULT_EXPECTED_FEATURES
    return DEFAULT_EXPECTED_FEATURES


def _v5c_batch_paths(
    start_day: str = TRAIN_START_DAY,
    end_day: str = TRAIN_END_DAY,
    *,
    expected_features: int | None = None,
) -> dict[str, Path]:
    prefix = f"STAS5_V5C_BATCH_{compact_day(start_day)}_{compact_day(end_day)}"
    feature_count = int(expected_features or _v5c_batch_feature_count_from_manifest(start_day, end_day))
    return {
        "dataset": V5C_ROOT / f"{prefix}_ML_READY_{feature_count}F_TARGETS_V1.csv",
        "allowlist": V5C_ROOT / f"{prefix}_FEATURE_ALLOWLIST_{feature_count}F_V1.json",
        "guard": V5C_ROOT / f"{prefix}_GUARD_V1.json",
        "manifest": V5C_ROOT / f"{prefix}_MANIFEST_V1.json",
        "audit": V5C_ROOT / f"{prefix}_AUDIT_RU.md",
    }


def run_continuous_training_guard(
    *,
    start_day: str = TRAIN_START_DAY,
    end_day: str = TRAIN_END_DAY,
    run_id: str | None = None,
) -> dict[str, Any]:
    paths = _v5c_batch_paths(start_day, end_day)
    expected = _v5c_expected_train_counts(start_day=start_day, end_day=end_day, paths=paths)
    run_id = run_id or f"stas5_v5c_continuous_guard_{run_stamp()}"
    return run_training_guard(
        run_dir=V5C_MODEL_RUNS_DIR / run_id,
        dataset_path=paths["dataset"],
        allowlist_path=paths["allowlist"],
        batch_guard_path=paths["guard"],
        expected_days=expected["days"],
        expected_rows=expected["rows"],
        expected_good=expected["good"],
        expected_bad=expected["bad"],
        expected_features=expected["features"] or DEFAULT_EXPECTED_FEATURES,
    )


def train_continuous_two_block(
    *,
    start_day: str = TRAIN_START_DAY,
    end_day: str = TRAIN_END_DAY,
    run_id: str | None = None,
    skip_riskgate_ml: bool = False,
    strict: bool = True,
) -> dict[str, Any]:
    paths = _v5c_batch_paths(start_day, end_day)
    expected = _v5c_expected_train_counts(start_day=start_day, end_day=end_day, paths=paths, strict=strict)
    run_id = run_id or f"stas5_v5c_continuous_train_{run_stamp()}"
    manifest = train_two_block_ml(
        run_id=run_id,
        dataset_path=paths["dataset"],
        allowlist_path=paths["allowlist"],
        batch_guard_path=paths["guard"],
        run_root=V5C_MODEL_RUNS_DIR,
        latest_model_pointer=V5C_LATEST_MODEL_POINTER,
        expected_days=expected["days"],
        expected_rows=expected["rows"],
        expected_good=expected["good"],
        expected_bad=expected["bad"],
        expected_features=expected["features"] or DEFAULT_EXPECTED_FEATURES,
        strict=strict,
    )
    risk_paths = riskgate_dataset_paths(start_day, end_day, output_dir=V5C_ROOT, expected_features=expected["features"] or DEFAULT_EXPECTED_FEATURES)
    riskgate_manifest: dict[str, Any] | None = None
    if skip_riskgate_ml:
        manifest["riskgate_ml_status"] = "SKIPPED_BY_OPERATOR_ENTRY_ONLY_TRAIN"
        manifest["riskgate_ml_post_train_guard_status"] = "SKIPPED"
        manifest["riskgate_ml"] = {
            "status": "SKIPPED_BY_OPERATOR_ENTRY_ONLY_TRAIN",
            "reason_ru": "RiskGate ML намеренно не обучался в этом run: нужен ENTRY-only baseline/wide review без safety-enforce.",
            "expected_dataset_path": rel(risk_paths["dataset"]),
            "expected_guard_path": rel(risk_paths["guard"]),
        }
        manifest.setdefault("guardrails", []).append("riskgate_ml_skipped_by_operator_entry_only_train")
    elif risk_paths["dataset"].exists() and risk_paths["allowlist"].exists() and risk_paths["guard"].exists():
        riskgate_manifest = train_v5c_riskgate_ml(
            run_dir=V5C_MODEL_RUNS_DIR / run_id,
            dataset_path=risk_paths["dataset"],
            allowlist_path=risk_paths["allowlist"],
            dataset_guard_path=risk_paths["guard"],
            strict=strict,
            expected_features=expected["features"] or DEFAULT_EXPECTED_FEATURES,
        )
        manifest["riskgate_ml_status"] = riskgate_manifest["status"]
        manifest["riskgate_ml_post_train_guard_status"] = riskgate_manifest.get("post_train_guard_status", "")
        manifest["riskgate_ml_manifest"] = riskgate_manifest["artifacts"]["riskgate_train_manifest"]
        manifest["riskgate_ml"] = {
            "status": riskgate_manifest["status"],
            "post_train_guard_status": riskgate_manifest.get("post_train_guard_status", ""),
            "dataset_path": rel(risk_paths["dataset"]),
            "guard_path": rel(risk_paths["guard"]),
            "rows": riskgate_manifest["rows"],
            "risk_bad_y_counts": riskgate_manifest["risk_bad_y_counts"],
            "selected_model_kind": riskgate_manifest["riskgate_selected_model_kind"],
            "thresholds": riskgate_manifest["thresholds"],
            "manifest_path": riskgate_manifest["artifacts"]["riskgate_train_manifest"],
        }
        manifest["artifacts"]["riskgate_ml_model"] = riskgate_manifest["artifacts"]["riskgate_ml_model"]
        manifest["artifacts"]["riskgate_ml_manifest"] = riskgate_manifest["artifacts"]["riskgate_train_manifest"]
        manifest["artifacts"]["riskgate_ml_metrics_json"] = riskgate_manifest["artifacts"]["riskgate_metrics_json"]
        manifest["artifacts"]["riskgate_ml_post_train_guard_json"] = riskgate_manifest["artifacts"]["riskgate_post_train_guard_json"]
    else:
        manifest["riskgate_ml_status"] = "SKIPPED_RISKGATE_DATASET_NOT_FOUND"
        manifest["riskgate_ml_post_train_guard_status"] = "SKIPPED"
        manifest["riskgate_ml"] = {
            "status": "SKIPPED_RISKGATE_DATASET_NOT_FOUND",
            "expected_dataset_path": rel(risk_paths["dataset"]),
            "expected_guard_path": rel(risk_paths["guard"]),
        }
    manifest["pipeline_variant"] = "V5C_CONTINUOUS"
    manifest["continuous_batch_manifest"] = rel(paths["manifest"])
    manifest["expected_train_counts"] = expected
    manifest_path = V5C_MODEL_RUNS_DIR / run_id / "STAS5_V5_TWO_BLOCK_TRAIN_MANIFEST_V1.json"
    write_json(manifest_path, manifest)
    write_json(
        V5C_LATEST_MODEL_POINTER,
        {
            "status": "LATEST_V5C_CONTINUOUS_TWO_BLOCK_MODEL_RUN",
            "created_utc": utc_now(),
            "run_id": run_id,
            "run_dir": rel(V5C_MODEL_RUNS_DIR / run_id),
            "manifest_path": rel(manifest_path),
            "post_train_guard_status": manifest.get("post_train_guard_status", ""),
            "riskgate_ml_status": manifest.get("riskgate_ml_status", ""),
            "riskgate_ml_post_train_guard_status": manifest.get("riskgate_ml_post_train_guard_status", ""),
        },
    )
    return manifest


def _latest_continuous_train_manifest() -> Path:
    if V5C_LATEST_MODEL_POINTER.exists():
        pointer = _load_json(V5C_LATEST_MODEL_POINTER)
        path = PROJECT_ROOT / pointer["manifest_path"]
        if path.exists():
            return path
    manifests = sorted(V5C_MODEL_RUNS_DIR.glob("*/STAS5_V5_TWO_BLOCK_TRAIN_MANIFEST_V1.json"), key=lambda item: item.stat().st_mtime)
    if not manifests:
        raise FileNotFoundError("V5C continuous train manifest not found")
    return manifests[-1]


def _latest_full274_run(day: str) -> Path:
    compact = compact_day(day)
    runs = sorted(FULL274_RUNS_DIR.glob(f"full274_feature_collect_{compact}_*"), key=lambda item: item.stat().st_mtime)
    if not runs:
        raise FileNotFoundError(f"FULL274 run not found for {day}")
    return runs[-1]


def _forward_day_paths(run_dir: Path, day: str) -> dict[str, Path]:
    compact = compact_day(day)
    day_dir = run_dir / "forward_market_passports" / compact
    prefix = f"STAS5_V5_MARKET_PASSPORT_{compact}"
    return {
        "day_dir": day_dir,
        "ml_ready_full": day_dir / f"{prefix}_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv",
        "allowlist_full": day_dir / f"{prefix}_FEATURE_ALLOWLIST_274_PLUS_FULL_CAUSAL_STRUCTURE_V1.json",
        "guard_full": day_dir / f"{prefix}_FULL_CAUSAL_STRUCTURE_GUARD_V1.json",
    }


def build_continuous_forward_dataset(
    *,
    run_dir: Path,
    train_manifest: dict[str, Any],
    start_day: str = FORWARD_START_DAY,
    end_day: str = FORWARD_END_DAY,
    context_start_day: str = TRAIN_START_DAY,
    context_warmup_minutes: int = DEFAULT_CONTEXT_WARMUP_MINUTES,
    strict: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    run_dir.mkdir(parents=True, exist_ok=True)
    start_day = normalize_day(start_day)
    end_day = normalize_day(end_day)
    context_start_day = normalize_day(context_start_day)
    expected_features = [str(column) for column in train_manifest["feature_columns"]]
    bollinger_enabled = all(column in expected_features for column in BOLLINGER_FEATURE_COLUMNS)
    base_expected_features = [column for column in expected_features if column not in BOLLINGER_FEATURE_COLUMNS]
    bollinger_audit_columns_in_features = sorted(set(expected_features).intersection(BOLLINGER_AUDIT_COLUMNS))
    frames: list[pd.DataFrame] = []
    day_outputs: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []

    for day in iter_days(start_day, end_day):
        compact = compact_day(day)
        full274_run = _latest_full274_run(day)
        full274_csv = full274_run / f"STAS5_FULL274_FEATURE_SNAPSHOT_{compact}.csv"
        full274_manifest = full274_run / f"STAS5_FULL274_FEATURE_SNAPSHOT_{compact}.manifest.json"
        if not full274_csv.exists() or not full274_manifest.exists():
            raise FileNotFoundError(f"FULL274 files missing for {day}: {full274_run}")

        source_start_day, min_open_time = _rolling_context_window(
            day,
            global_start_day=context_start_day,
            warmup_minutes=context_warmup_minutes,
        )
        context = build_continuous_ohlcv_context(
            start_day=source_start_day,
            end_day=day,
            min_open_time_utc=min_open_time,
            output_dir=run_dir / "ohlcv_contexts",
            strict=strict,
        )
        paths = _forward_day_paths(run_dir, day)
        paths["day_dir"].mkdir(parents=True, exist_ok=True)
        causal_guard = build_causal_structure_package(
            day=day,
            ml_ready_path=full274_csv,
            allowlist_path=full274_manifest,
            ohlcv_path=PROJECT_ROOT / context["outputs"]["context_csv"],
            output_dir=paths["day_dir"],
        )
        full_guard = build_full_causal_structure_package(
            day=day,
            ml_ready_plus_path=Path(causal_guard["outputs"]["ml_ready_274f_plus_causal_structure_targets"]),
            allowlist_plus_path=Path(causal_guard["outputs"]["feature_allowlist_274_plus_causal_structure"]),
            ohlcv_path=PROJECT_ROOT / context["outputs"]["context_csv"],
            output_dir=paths["day_dir"],
            draw_plot=False,
        )
        allowlist = _read_allowlist(paths["allowlist_full"])
        frame = pd.read_csv(paths["ml_ready_full"], encoding="utf-8-sig")
        bollinger_summary: dict[str, Any] = {"status": "DISABLED"}
        if bollinger_enabled:
            context_csv = PROJECT_ROOT / context["outputs"]["context_csv"]
            context_df = pd.read_csv(context_csv, encoding="utf-8-sig")
            frame, bollinger_summary = attach_bollinger_features(frame, context_df)
        frame, fill = _fill_feature_gaps(frame, expected_features)
        frames.append(frame)
        allowlist_match = allowlist == (base_expected_features if bollinger_enabled else expected_features)
        full_guard_pass = full_guard["status"] == FULL_CAUSAL_GUARD_PASS
        checks.append(_check(f"{compact}_full_guard_pass", full_guard_pass, {"status": full_guard["status"]}))
        checks.append(
            _check(
                f"{compact}_allowlist_matches_train_base_features",
                allowlist_match,
                {
                    "daily_feature_count": len(allowlist),
                    "train_feature_count": len(expected_features),
                    "base_expected_feature_count": len(base_expected_features),
                    "bollinger_enabled": bool(bollinger_enabled),
                },
            )
        )
        if bollinger_enabled:
            checks.append(
                _check(
                    f"{compact}_bollinger_features_attached",
                    bollinger_summary.get("source_after_entry_rows", 1) == 0
                    and int(bollinger_summary.get("ready_rows", 0)) > 0
                    and not bollinger_audit_columns_in_features,
                    {
                        "summary": bollinger_summary,
                        "audit_columns_in_X": bollinger_audit_columns_in_features,
                    },
                )
            )
        checks.append(_check(f"{compact}_continuous_context_ready", context["status"].startswith("PASS"), {"context_csv": context["outputs"]["context_csv"], "rows": context["rows"]}))
        day_outputs.append(
            {
                "day": day,
                "full274_run": rel(full274_run),
                "rows": int(len(frame)),
                "feature_count": len(expected_features),
                "base_feature_count": len(allowlist),
                "allowlist_matches_train": allowlist_match,
                "full_guard_status": full_guard["status"],
                "feature_fill_summary": fill,
                "bollinger_layer": bollinger_summary,
                "context_start_day": context_start_day,
                "context_source_start_day": source_start_day,
                "context_end_day": day,
                "context_warmup_minutes": context_warmup_minutes,
                "context_csv": context["outputs"]["context_csv"],
                "context_rows": context["rows"],
                "ml_ready_full": rel(paths["ml_ready_full"]),
                "guard_full": rel(paths["guard_full"]),
            }
        )

    dataset = pd.concat(frames, ignore_index=True, sort=False) if frames else pd.DataFrame()
    dataset = dataset.sort_values([c for c in ["day", "entry_time_utc", "candidate_id", "record_id"] if c in dataset.columns]).reset_index(drop=True)
    missing_features = [column for column in expected_features if column not in dataset.columns]
    feature_nulls = int(dataset[expected_features].isna().sum().sum()) if not dataset.empty and not missing_features else -1
    target_in_features = sorted(set(expected_features).intersection(TARGET_OR_MANUAL_COLUMNS))
    forbidden = _forbidden_feature_matches(expected_features)
    cs_time = _source_time_check(dataset, "cs_max_source_time_utc") if not dataset.empty else {"source_after_entry_rows": 0}
    fcs_time = _source_time_check(dataset, "fcs_max_source_time_utc") if not dataset.empty else {"source_after_entry_rows": 0}
    bb_time = bollinger_source_time_check(dataset) if bollinger_enabled else {"disabled": True}
    duplicate_day_candidate = int(dataset.duplicated(["day", "candidate_id"]).sum()) if {"day", "candidate_id"}.issubset(dataset.columns) else -1
    duplicate_day_record = int(dataset.duplicated(["day", "record_id"]).sum()) if {"day", "record_id"}.issubset(dataset.columns) else -1

    checks.extend(
        [
            _check(
                "forward_days_present",
                len(day_outputs) == len(iter_days(start_day, end_day)),
                {"actual": len(day_outputs), "expected": len(iter_days(start_day, end_day))},
            ),
            _check("forward_rows_positive", len(dataset) > 0, {"actual": int(len(dataset))}),
            _check("forward_features_present", not missing_features, {"missing": missing_features[:50], "missing_count": len(missing_features)}),
            _check("forward_feature_values_no_null_after_fill", feature_nulls == 0, {"feature_nulls": feature_nulls}),
            _check("target_manual_columns_not_in_forward_X", not target_in_features, {"columns": target_in_features}),
            _check("forbidden_columns_absent_from_forward_X", not forbidden, forbidden),
            _check("no_duplicate_day_candidate", duplicate_day_candidate == 0, {"duplicates": duplicate_day_candidate}),
            _check("no_duplicate_day_record", duplicate_day_record == 0, {"duplicates": duplicate_day_record}),
            _check(
                "cs_max_source_time_utc_lte_entry_time_utc",
                cs_time.get("source_after_entry_rows", 1) == 0 and cs_time.get("source_na_rows", 1) == 0,
                cs_time,
            ),
            _check(
                "fcs_max_source_time_utc_lte_entry_time_utc",
                fcs_time.get("source_after_entry_rows", 1) == 0 and fcs_time.get("source_na_rows", 1) == 0,
                fcs_time,
            ),
            _check(
                "bb_source_time_utc_lte_entry_time_utc",
                (not bollinger_enabled)
                or (
                    bb_time.get("source_after_entry_rows", 1) == 0
                    and bb_time.get("source_na_ready_rows", 1) == 0
                    and not bollinger_audit_columns_in_features
                ),
                {
                    "enabled": bool(bollinger_enabled),
                    "source_time": bb_time,
                    "audit_columns_in_X": bollinger_audit_columns_in_features,
                },
            ),
            _check(
                "continuous_context_declared",
                context_start_day <= start_day,
                {"context_start_day": context_start_day, "forward_start_day": start_day},
            ),
        ]
    )
    status = V5C_FORWARD_DATASET_PASS if all(item["status"] == "PASS" for item in checks) else V5C_FORWARD_DATASET_FAIL
    out_csv = run_dir / f"STAS5_V5C_FORWARD_DATASET_{compact_day(start_day)}_{compact_day(end_day)}_X{len(expected_features)}_CONTINUOUS_V1.csv"
    dataset.to_csv(out_csv, index=False, encoding="utf-8-sig")
    manifest_path = run_dir / "STAS5_V5C_FORWARD_DATASET_MANIFEST_V1.json"
    manifest = {
        "status": status,
        "created_utc": utc_now(),
        "pipeline_variant": "V5C_CONTINUOUS",
        "run_id": run_dir.name,
        "run_dir": rel(run_dir),
        "date_range": {"start_day": start_day, "end_day": end_day},
        "context_policy": {
            "mode": "rolling_past_context",
            "mode_detail": "rolling_continuous_warmup",
            "context_start_day": context_start_day,
            "context_warmup_minutes": context_warmup_minutes,
            "context_end_day": "target_forward_day",
            "feature_rule": "FULL274 -> cs_* -> fcs_*; each candidate keeps source_time <= entry_time_utc",
            "bollinger_rule": "optional bb_* from closed 1m OHLCV bars before entry_time_utc",
        },
        "rows": int(len(dataset)),
        "feature_count": len(expected_features),
        "feature_columns": expected_features,
        "base_feature_count": len(base_expected_features) if bollinger_enabled else len(expected_features),
        "bollinger_layer": {
            "enabled": bool(bollinger_enabled),
            "layer_id": BOLLINGER_LAYER_ID if bollinger_enabled else "",
            "feature_contract": BOLLINGER_FEATURE_CONTRACT if bollinger_enabled else "",
            "feature_columns": BOLLINGER_FEATURE_COLUMNS if bollinger_enabled else [],
            "audit_columns_not_X": BOLLINGER_AUDIT_COLUMNS if bollinger_enabled else [],
            "source_time_check": bb_time,
        },
        "dataset_csv": rel(out_csv),
        "day_outputs": day_outputs,
        "checks": checks,
        "guardrails": [
            "forward_days_not_used_for_training",
            "forward_days_not_used_for_threshold_tuning",
            "forward_x439_rebuilt_with_continuous_past_ohlcv_context",
            "optional_bollinger_features_rebuilt_from_closed_past_ohlcv_context",
            "manual_forward_targets_not_used",
            "cs_fcs_source_time_lte_entry_time",
            "bb_source_time_lte_entry_time_when_enabled",
        ],
    }
    write_json(manifest_path, manifest)
    if strict and status != V5C_FORWARD_DATASET_PASS:
        raise ValueError(f"V5C continuous forward dataset guard is not PASS: {status}")
    return dataset, manifest


def run_continuous_forward(
    *,
    run_id: str | None = None,
    train_manifest_path: Path | None = None,
    start_day: str = FORWARD_START_DAY,
    end_day: str = FORWARD_END_DAY,
    context_start_day: str = TRAIN_START_DAY,
    context_warmup_minutes: int = DEFAULT_CONTEXT_WARMUP_MINUTES,
    entry_decision_policy: str = "trained",
    disable_riskgate_ml: bool = False,
    strict: bool = True,
    render_visual_review: bool = True,
    bollinger_preview: bool = False,
) -> dict[str, Any]:
    start_day = normalize_day(start_day)
    end_day = normalize_day(end_day)
    context_start_day = normalize_day(context_start_day)
    train_manifest_path = train_manifest_path or _latest_continuous_train_manifest()
    train_manifest = _load_json(train_manifest_path)
    if strict and train_manifest.get("post_train_guard_status") != POST_TRAIN_GUARD_PASS:
        raise ValueError(f"post-train guard is not PASS: {train_manifest.get('post_train_guard_status')}")

    run_id = run_id or f"stas5_v5c_continuous_forward_{compact_day(start_day)}_{compact_day(end_day)}_{run_stamp()}"
    run_dir = V5C_FORWARD_RUNS_DIR / run_id
    dataset, dataset_manifest = build_continuous_forward_dataset(
        run_dir=run_dir,
        train_manifest=train_manifest,
        start_day=start_day,
        end_day=end_day,
        context_start_day=context_start_day,
        context_warmup_minutes=context_warmup_minutes,
        strict=strict,
    )

    selected_entry = train_manifest.get("selected_entry_model", {})
    selected_model_key = str(selected_entry.get("model_key") or "entry_two_block")
    baseline_package = joblib.load(PROJECT_ROOT / train_manifest["artifacts"]["entry_baseline_model"])
    entry_package = joblib.load(PROJECT_ROOT / train_manifest["artifacts"]["entry_ml_model"])
    base_features = [str(column) for column in train_manifest["feature_columns"]]
    numeric_columns = [str(column) for column in train_manifest["numeric_columns"]]
    categorical_columns = [str(column) for column in train_manifest["categorical_columns"]]
    x_base = _prepare_feature_matrix(dataset, feature_columns=base_features, numeric_columns=numeric_columns, categorical_columns=categorical_columns)
    phase_live = pd.DataFrame(index=dataset.index)
    state_live = pd.DataFrame(index=dataset.index)
    if selected_model_key == "entry_baseline":
        stack = dataset.reset_index(drop=True)
        selected_package = baseline_package
        x_entry = _prepare_feature_matrix(
            stack,
            feature_columns=[str(c) for c in selected_package["feature_columns"]],
            numeric_columns=[str(c) for c in selected_package["numeric_columns"]],
            categorical_columns=[str(c) for c in selected_package["categorical_columns"]],
        )
        selected_label = "ENTRY_BASELINE_ML"
    else:
        phase_package = joblib.load(PROJECT_ROOT / train_manifest["artifacts"]["market_phase_state_model"])
        phase_live = _proba_predictions(
            phase_package["phase_pipeline"],
            x_base,
            classes=[str(c) for c in phase_package["phase_classes"]],
            prefix=PHASE_PREFIX,
        )
        state_live = _proba_predictions(
            phase_package["state_pipeline"],
            x_base,
            classes=[str(c) for c in phase_package["state_classes"]],
            prefix=STATE_PREFIX,
        )
        stack = pd.concat([dataset.reset_index(drop=True), phase_live, state_live], axis=1)
        selected_package = entry_package
        x_entry = _prepare_feature_matrix(
            stack,
            feature_columns=[str(c) for c in selected_package["feature_columns"]],
            numeric_columns=[str(c) for c in selected_package["numeric_columns"]],
            categorical_columns=[str(c) for c in selected_package["categorical_columns"]],
        )
        selected_label = "ENTRY_ML_TWO_BLOCK"
    scores = _positive_proba(selected_package["pipeline"], x_entry)
    active_thresholds = _thresholds_for_entry_decision_policy(
        train_manifest=train_manifest,
        selected_model_key=selected_model_key,
        selected_package=selected_package,
        entry_decision_policy=entry_decision_policy,
    )
    decisions = _apply_entry_decision(scores, active_thresholds)
    decisions_before_riskgate = decisions.copy()
    riskgate_scores: Any = None
    riskgate_decisions: Any = None
    riskgate_actions: Any = None
    riskgate_manifest: dict[str, Any] | None = None
    riskgate_checks: list[dict[str, Any]] = []
    riskgate_status = str(train_manifest.get("riskgate_ml_status", ""))
    riskgate_manifest_rel = str(train_manifest.get("riskgate_ml_manifest") or train_manifest.get("riskgate_ml", {}).get("manifest_path", "")).strip()
    if disable_riskgate_ml:
        riskgate_checks.append(
            _check(
                "riskgate_disabled_by_operator_entry_only_forward",
                True,
                {
                    "riskgate_ml_status": riskgate_status or "MISSING",
                    "reason": "operator requested ENTRY-only forward; RiskGate ML not applied",
                },
            )
        )
    elif riskgate_status == "PASS_V5C_RISKGATE_ML_TRAINED_POST_TRAIN_GUARD_READY_FOR_FORWARD" and riskgate_manifest_rel:
        riskgate_manifest_path = PROJECT_ROOT / riskgate_manifest_rel
        riskgate_manifest = _load_json(riskgate_manifest_path)
        riskgate_payload = apply_v5c_riskgate_forward(dataset, riskgate_manifest)
        riskgate_scores = riskgate_payload["scores"]
        riskgate_decisions = riskgate_payload["decisions"]
        decisions, riskgate_actions = apply_riskgate_to_entry_decisions(decisions_before_riskgate, riskgate_decisions)
        riskgate_checks.extend(riskgate_payload["checks"])
        riskgate_checks.append(
            _check(
                "riskgate_applied_to_entry_decision",
                True,
                {"manifest_path": riskgate_manifest_rel, "policy": "ENTRY opportunity first, RiskGate safety second"},
            )
        )
    else:
        riskgate_checks.append(
            _check(
                "riskgate_not_applied",
                True,
                {"riskgate_ml_status": riskgate_status or "MISSING", "reason": "no trained PASS RiskGate manifest in train manifest"},
            )
        )
    columns = [c for c in KEY_COLUMNS if c in stack.columns]
    out = stack[columns].copy()
    out["ENTRY_ML_LIVE_SCORE"] = scores
    out["ENTRY_ML_LIVE_DECISION_BEFORE_RISKGATE"] = decisions_before_riskgate
    out["ENTRY_ML_LIVE_DECISION"] = decisions
    out["ENTRY_MODEL_SELECTED"] = selected_label
    out["ENTRY_POLICY"] = f"v5c_continuous_{selected_model_key}_{active_thresholds.get('active_decision_policy', 'trained_manifest_thresholds')}"
    if riskgate_scores is not None and riskgate_decisions is not None and riskgate_actions is not None:
        out["RISKGATE_ML_LIVE_SCORE"] = riskgate_scores
        out["RISKGATE_ML_LIVE_DECISION"] = riskgate_decisions
        out["RISKGATE_ML_ACTION"] = riskgate_actions
        out["ENTRY_POLICY"] = out["ENTRY_POLICY"] + "_plus_riskgate_ml_safety"
    for column in phase_live.columns:
        out[column] = phase_live[column]
    for column in state_live.columns:
        out[column] = state_live[column]
    if "entry_price_5bps" in stack.columns:
        out["entry_price_5bps"] = stack["entry_price_5bps"]

    predictions_path = run_dir / f"STAS5_V5C_FORWARD_PREDICTIONS_{compact_day(start_day)}_{compact_day(end_day)}_V1.csv"
    out.to_csv(predictions_path, index=False, encoding="utf-8-sig")

    visual_manifest: dict[str, Any] | None = None
    if render_visual_review:
        from mlbotnav.stas5_v5_forward_visual_review import render_forward_visual_review

        visual_manifest = render_forward_visual_review(
            forward_run_dir=run_dir,
            predictions_path=predictions_path,
            start_day=start_day,
            end_day=end_day,
            strict=strict,
            bollinger_preview=bollinger_preview,
        )

    day_summary = []
    for day, rows in out.groupby("day", sort=True):
        counts = rows["ENTRY_ML_LIVE_DECISION"].astype(str).value_counts().to_dict()
        enters = rows[rows["ENTRY_ML_LIVE_DECISION"].astype(str).eq("ENTER")].sort_values("entry_time_utc")
        day_summary.append(
            {
                "day": str(day),
                "rows": int(len(rows)),
                "decision_counts": {str(k): int(v) for k, v in counts.items()},
                "enter_candidates": enters[["candidate_id", "record_id", "entry_time_utc", "ENTRY_ML_LIVE_SCORE"]].to_dict("records"),
            }
        )
    checks = [
        _check("post_train_guard_pass", train_manifest.get("post_train_guard_status") == POST_TRAIN_GUARD_PASS, {"status": train_manifest.get("post_train_guard_status")}),
        _check("forward_dataset_guard_pass", dataset_manifest["status"] == V5C_FORWARD_DATASET_PASS, {"status": dataset_manifest["status"]}),
        _check("predictions_rows_match_dataset", len(out) == len(dataset), {"predictions": int(len(out)), "dataset": int(len(dataset))}),
        _check("forward_window_not_in_training", start_day > train_manifest["date_range"]["end_day"], {"train_end": train_manifest["date_range"]["end_day"], "forward_start": start_day}),
        _check("continuous_context_used", dataset_manifest["context_policy"]["context_start_day"] == context_start_day, dataset_manifest["context_policy"]),
        _check("no_true_phase_state_used_as_forward_features", True, {"selected_entry_model": selected_model_key, "used": "live MARKET_PHASE_STATE_ML predictions only when two-block selected"}),
        _check("entry_decision_policy_uses_train_oof_only", True, {"entry_decision_policy": entry_decision_policy, "threshold_policy": active_thresholds.get("active_decision_policy", "")}),
    ]
    checks.extend(riskgate_checks)
    status_pass = _v5c_forward_pass_status(start_day, end_day)
    status_fail = _v5c_forward_fail_status(start_day, end_day)
    status = status_pass if all(item["status"] == "PASS" for item in checks) else status_fail
    train_range = train_manifest.get("date_range", {})
    train_start = normalize_day(str(train_range.get("start_day", TRAIN_START_DAY)))
    train_end = normalize_day(str(train_range.get("end_day", TRAIN_END_DAY)))
    manifest = {
        "status": status,
        "created_utc": utc_now(),
        "pipeline_variant": "V5C_CONTINUOUS",
        "run_id": run_id,
        "run_dir": rel(run_dir),
        "date_range": {"start_day": start_day, "end_day": end_day},
        "context_policy": dataset_manifest["context_policy"],
        "train_manifest_path": rel(train_manifest_path),
        "train_run_id": train_manifest["run_id"],
        "rows": int(len(out)),
        "predictions_csv": rel(predictions_path),
        "forward_dataset_manifest": rel(run_dir / "STAS5_V5C_FORWARD_DATASET_MANIFEST_V1.json"),
        "visual_review_manifest": visual_manifest.get("manifest_path", "") if visual_manifest else "",
        "visual_review_audit_ru": visual_manifest.get("audit_ru", "") if visual_manifest else "",
        "visual_review_status": visual_manifest.get("status", "SKIPPED") if visual_manifest else "SKIPPED",
        "visual_review_png_count": int(visual_manifest.get("png_count", 0)) if visual_manifest else 0,
        "bollinger_visual_preview": bool(bollinger_preview),
        "selected_entry_model": selected_entry,
        "entry_model_selected_for_forward": selected_model_key,
        "riskgate_ml_status": riskgate_status or "NOT_PRESENT_IN_TRAIN_MANIFEST",
        "riskgate_ml_applied": bool(riskgate_scores is not None),
        "riskgate_ml_disabled_by_operator": bool(disable_riskgate_ml),
        "riskgate_ml_manifest": riskgate_manifest_rel,
        "entry_decision_policy": entry_decision_policy,
        "thresholds": active_thresholds,
        "decision_counts_total": {str(k): int(v) for k, v in out["ENTRY_ML_LIVE_DECISION"].astype(str).value_counts().to_dict().items()},
        "decision_counts_before_riskgate": {
            str(k): int(v) for k, v in out["ENTRY_ML_LIVE_DECISION_BEFORE_RISKGATE"].astype(str).value_counts().to_dict().items()
        },
        "riskgate_decision_counts_total": {
            str(k): int(v) for k, v in out.get("RISKGATE_ML_LIVE_DECISION", pd.Series(dtype=str)).astype(str).value_counts().to_dict().items()
        },
        "day_summary": day_summary,
        "checks": checks,
        "guardrails": [
            f"train_{compact_day(train_start)}_{compact_day(train_end)}_only",
            f"forward_{compact_day(start_day)}_{compact_day(end_day)}_not_used_for_training_or_threshold_tuning",
            "continuous_past_context_allowed_but_future_candles_for_each_entry_forbidden",
            "market_phase_state_features_are_live_predictions_not_phase_y_state_y_when_two_block_selected",
            "entry_decision_uses_fixed_train_oof_thresholds",
            "normal_or_wide_review_policy_uses_train_oof_quantiles_only_no_forward_tuning",
        ],
    }
    manifest_path = run_dir / "STAS5_V5C_FORWARD_MANIFEST_V1.json"
    write_json(manifest_path, manifest)
    write_json(
        V5C_LATEST_FORWARD_POINTER,
        {
            "status": "LATEST_V5C_CONTINUOUS_TWO_BLOCK_FORWARD_RUN",
            "created_utc": utc_now(),
            "run_id": run_id,
            "run_dir": rel(run_dir),
            "manifest_path": rel(manifest_path),
            "guard_status": status,
        },
    )
    if strict and status != status_pass:
        raise ValueError(f"V5C continuous forward guard is not PASS: {status}")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="STAS5 V5C continuous market-passport ML train/forward.")
    parser.add_argument("--mode", choices=["build-batch", "training-guard", "train", "forward", "train-forward", "all"], required=True)
    parser.add_argument("--train-run-id", default="")
    parser.add_argument("--forward-run-id", default="")
    parser.add_argument("--train-start-day", default=TRAIN_START_DAY)
    parser.add_argument("--train-end-day", default=TRAIN_END_DAY)
    parser.add_argument("--forward-start-day", default=FORWARD_START_DAY)
    parser.add_argument("--forward-end-day", default=FORWARD_END_DAY)
    parser.add_argument("--context-start-day", default=TRAIN_START_DAY)
    parser.add_argument("--context-warmup-minutes", type=int, default=DEFAULT_CONTEXT_WARMUP_MINUTES)
    parser.add_argument("--train-manifest-path", default="")
    parser.add_argument("--entry-decision-policy", choices=["trained", "normal", "wide_review"], default="trained")
    parser.add_argument("--skip-riskgate-ml", action="store_true")
    parser.add_argument("--disable-riskgate-ml", action="store_true")
    parser.add_argument("--no-strict", action="store_true")
    parser.add_argument("--skip-visual-review", action="store_true")
    parser.add_argument("--bollinger-preview", action="store_true")
    args = parser.parse_args()
    strict = not args.no_strict

    if args.mode in {"build-batch", "all"}:
        _dataset, manifest, guard = build_continuous_batch(
            start_day=args.train_start_day,
            end_day=args.train_end_day,
            context_start_day=args.context_start_day,
            context_warmup_minutes=args.context_warmup_minutes,
            strict=strict,
        )
        if args.mode == "build-batch":
            print(json.dumps({"status": guard["status"], "rows": manifest["rows"], "feature_count": manifest["feature_count"], "batch_csv": manifest["outputs"]["batch_csv"]}, ensure_ascii=False))
            return 0 if args.no_strict or guard["status"] == BATCH_GUARD_PASS else 2

    if args.mode == "training-guard":
        guard = run_continuous_training_guard(
            start_day=args.train_start_day,
            end_day=args.train_end_day,
            run_id=args.train_run_id or None,
        )
        print(json.dumps({"status": guard["status"], "run_id": guard["run_id"], "run_dir": guard["run_dir"]}, ensure_ascii=False))
        return 0 if args.no_strict or guard["status"].startswith("PASS") else 2

    train_manifest: dict[str, Any] | None = None
    if args.mode in {"train", "train-forward", "all"}:
        train_manifest = train_continuous_two_block(
            start_day=args.train_start_day,
            end_day=args.train_end_day,
            run_id=args.train_run_id or None,
            skip_riskgate_ml=args.skip_riskgate_ml,
            strict=strict,
        )
        if args.mode == "train":
            print(json.dumps({"status": train_manifest["status"], "run_id": train_manifest["run_id"], "run_dir": train_manifest["run_dir"], "post_train_guard_status": train_manifest.get("post_train_guard_status")}, ensure_ascii=False))
            return 0

    if args.mode in {"forward", "train-forward", "all"}:
        train_manifest_path = Path(args.train_manifest_path) if args.train_manifest_path else None
        if train_manifest is not None:
            train_manifest_path = V5C_MODEL_RUNS_DIR / train_manifest["run_id"] / "STAS5_V5_TWO_BLOCK_TRAIN_MANIFEST_V1.json"
        forward_manifest = run_continuous_forward(
            run_id=args.forward_run_id or None,
            train_manifest_path=train_manifest_path,
            start_day=args.forward_start_day,
            end_day=args.forward_end_day,
            context_start_day=args.context_start_day,
            context_warmup_minutes=args.context_warmup_minutes,
            entry_decision_policy=args.entry_decision_policy,
            disable_riskgate_ml=args.disable_riskgate_ml,
            strict=strict,
            render_visual_review=not args.skip_visual_review,
            bollinger_preview=args.bollinger_preview,
        )
        print(
            json.dumps(
                {
                    "status": forward_manifest["status"],
                    "run_id": forward_manifest["run_id"],
                    "run_dir": forward_manifest["run_dir"],
                    "rows": forward_manifest["rows"],
                    "decision_counts_total": forward_manifest["decision_counts_total"],
                    "visual_review_status": forward_manifest["visual_review_status"],
                    "visual_review_png_count": forward_manifest["visual_review_png_count"],
                },
                ensure_ascii=False,
            )
        )
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
