from __future__ import annotations

import argparse
import hashlib
import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import optuna
import numpy as np
import pandas as pd

from mlbotnav.backtest import run_prob_backtest
from mlbotnav.dataset import FEATURE_COLUMNS, FEATURE_GROUPS, RUNTIME_ACTION_COLUMNS, build_feature_frame, load_ohlcv_range
from mlbotnav.optuna_engine import (
    apply_stage_overrides,
    build_study_plan,
    enforce_storage_parallel_compat,
    load_optuna_engine_config,
    resolve_stage_profile,
    resolve_storage_url,
)
from mlbotnav.optuna_objective import ObjectiveWeights, compute_trial_score
from mlbotnav.optuna_space import compile_optuna_space, evaluate_runtime_constraints_detailed, load_calibration_matrix
from mlbotnav.readiness import enforce_action_allowed
from mlbotnav.runtime_diagnostics import MIN_MOVE_UNREACHABLE, classify_backtest_outcome, is_min_move_unreachable
from mlbotnav.search_gate_candidate import _gate_decision, _load_thresholds
from mlbotnav.validation import FoldResult, aggregate_fold_metrics, leakage_sanity_checks, walk_forward_validate

OPTUNA_REPORT_CONTRACT_VERSION = "optuna_report_v1"
CORE_SEARCH_PARAM_NAMES = {
    "horizon_bars",
    "p_enter_long",
    "p_enter_short",
    "min_expected_move",
    "min_expected_move_pct",
    "notional_usd",
}


def _csv_ints(raw: str) -> list[int]:
    return [int(x.strip()) for x in str(raw).split(",") if x.strip()]


def _csv_floats(raw: str) -> list[float]:
    return [float(x.strip()) for x in str(raw).split(",") if x.strip()]


def _prepare_horizon_cache(
    *,
    raw_df: pd.DataFrame,
    horizon_bars: int,
    feature_columns: list[str],
    min_train_rows: int,
    n_folds: int,
    execution_mode: str,
    ml_signal_backend: str,
    calibration_params: dict[str, float] | None = None,
) -> dict[str, Any]:
    frame = build_feature_frame(
        raw_df.copy(),
        horizon_bars=int(horizon_bars),
        calibration_params=calibration_params,
    )
    n_folds_eff = max(2, int(n_folds))
    min_train_rows_eff = int(min_train_rows)
    # 1d/1d windows can be shorter than default min_train_rows.
    # Relax safely to keep walk-forward feasible instead of hard-failing search.
    max_feasible_train = max(120, int(len(frame) - (n_folds_eff * 20) - 1))
    min_train_rows_eff = min(min_train_rows_eff, max_feasible_train)
    if len(frame) <= (min_train_rows_eff + n_folds_eff * 20):
        return {
            "error": (
                f"not_enough_rows_for_walk_forward rows={len(frame)} "
                f"min_train_rows_eff={min_train_rows_eff} n_folds={n_folds_eff}"
            )
        }
    issues = leakage_sanity_checks(frame)
    if issues:
        return {"error": f"leakage_issues={issues}"}
    backend = str(ml_signal_backend or "on").strip().lower()
    if backend == "off":
        folds, oof = _walk_forward_rule_only_validate(
            frame,
            min_train_rows=min_train_rows_eff,
            n_folds=n_folds_eff,
            feature_columns=list(feature_columns),
        )
    else:
        folds, oof = walk_forward_validate(
            frame,
            min_train_rows=min_train_rows_eff,
            n_folds=n_folds_eff,
            feature_columns=list(feature_columns),
        )
    fold_metrics = aggregate_fold_metrics(folds)
    if str(execution_mode).strip().lower() == "exchange_like":
        req_cols = ["open", "high", "low", "close", "open_time_utc"]
        missing = [c for c in req_cols if c not in oof.columns]
        if missing:
            return {"error": f"exchange_like_requires_columns_missing={missing}"}
    return {"fold_metrics": fold_metrics, "oof": oof}


def _zscore_series(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan).astype("float64")
    mean = float(s.mean()) if not s.empty else 0.0
    std = float(s.std(ddof=0)) if not s.empty else 0.0
    if std <= 1e-12:
        return pd.Series(0.0, index=s.index, dtype="float64")
    return (s.fillna(mean) - mean) / std


def _auc_from_scores(y_true: pd.Series, y_score: pd.Series) -> float:
    y = pd.to_numeric(y_true, errors="coerce").fillna(0).astype(int)
    s = pd.to_numeric(y_score, errors="coerce").fillna(0.5).astype("float64")
    n_pos = int((y == 1).sum())
    n_neg = int((y == 0).sum())
    if n_pos == 0 or n_neg == 0:
        return 0.5
    ranks = s.rank(method="average")
    rank_sum_pos = float(ranks[y == 1].sum())
    auc = (rank_sum_pos - (n_pos * (n_pos + 1) / 2.0)) / float(n_pos * n_neg)
    return float(max(0.0, min(1.0, auc)))


def _f1_binary(y_true: pd.Series, y_pred: pd.Series) -> float:
    yt = pd.to_numeric(y_true, errors="coerce").fillna(0).astype(int)
    yp = pd.to_numeric(y_pred, errors="coerce").fillna(0).astype(int)
    tp = int(((yt == 1) & (yp == 1)).sum())
    fp = int(((yt == 0) & (yp == 1)).sum())
    fn = int(((yt == 1) & (yp == 0)).sum())
    if tp == 0:
        return 0.0
    precision = float(tp) / float(tp + fp) if (tp + fp) > 0 else 0.0
    recall = float(tp) / float(tp + fn) if (tp + fn) > 0 else 0.0
    if precision + recall <= 0.0:
        return 0.0
    return float(2.0 * precision * recall / (precision + recall))


def _rule_only_prob_up(test: pd.DataFrame, feature_columns: list[str]) -> pd.Series:
    feature_set = {str(x).strip() for x in list(feature_columns or [])}
    parts: list[pd.Series] = []
    if "ema_gap" in feature_set and "ema_gap" in test.columns:
        parts.append(_zscore_series(test["ema_gap"]))
    if "ret_1" in feature_set and "ret_1" in test.columns:
        parts.append(_zscore_series(test["ret_1"]))
    if "macd_hist" in feature_set and "macd_hist" in test.columns:
        parts.append(_zscore_series(test["macd_hist"]))
    if "rsi14" in feature_set and "rsi14" in test.columns:
        rsi = pd.to_numeric(test["rsi14"], errors="coerce").fillna(50.0).clip(lower=0.0, upper=100.0)
        parts.append((rsi - 50.0) / 10.0)
    if "mfi14" in feature_set and "mfi14" in test.columns:
        mfi = pd.to_numeric(test["mfi14"], errors="coerce").fillna(50.0).clip(lower=0.0, upper=100.0)
        parts.append((mfi - 50.0) / 10.0)
    if "vwap_distance" in feature_set and "vwap_distance" in test.columns:
        parts.append(_zscore_series(test["vwap_distance"]))
    if "delta_volume" in feature_set and "delta_volume" in test.columns:
        parts.append(_zscore_series(test["delta_volume"]))
    if not parts:
        if "close" in test.columns:
            parts.append(_zscore_series(pd.to_numeric(test["close"], errors="coerce").pct_change().fillna(0.0)))
        else:
            return pd.Series(0.5, index=test.index, dtype="float64")
    score = parts[0].copy()
    for part in parts[1:]:
        score = score.add(part, fill_value=0.0)
    score = score / float(max(1, len(parts)))
    score = score.clip(lower=-8.0, upper=8.0)
    prob = 1.0 / (1.0 + np.exp(-score.to_numpy(dtype="float64")))
    return pd.Series(prob, index=test.index, dtype="float64").clip(lower=0.001, upper=0.999)


def _walk_forward_rule_only_validate(
    df: pd.DataFrame,
    *,
    min_train_rows: int = 1200,
    n_folds: int = 4,
    feature_columns: list[str] | None = None,
) -> tuple[list[FoldResult], pd.DataFrame]:
    if len(df) <= min_train_rows + n_folds * 20:
        raise ValueError(f"Not enough rows for walk-forward: {len(df)}")
    fold_size = max(20, (len(df) - min_train_rows) // n_folds)
    results: list[FoldResult] = []
    oof_parts: list[pd.DataFrame] = []
    cols = feature_columns if feature_columns is not None else FEATURE_COLUMNS

    for fold in range(n_folds):
        train_end = min_train_rows + fold * fold_size
        test_end = min(len(df), train_end + fold_size)
        if test_end - train_end < 20:
            continue
        train = df.iloc[:train_end].copy()
        test = df.iloc[train_end:test_end].copy()
        if train["open_time_utc"].max() >= test["open_time_utc"].min():
            raise ValueError("Temporal leakage risk: train overlaps test by time")

        y_test = pd.to_numeric(test["target_up"], errors="coerce").fillna(0).astype(int)
        prob = _rule_only_prob_up(test, cols)
        pred = (prob >= 0.5).astype(int)
        acc = float((pred.to_numpy() == y_test.to_numpy()).mean()) if len(y_test) else 0.0
        f1 = _f1_binary(y_test, pred)
        auc = _auc_from_scores(y_test, prob)
        results.append(
            FoldResult(
                fold_id=fold + 1,
                train_rows=int(len(train)),
                test_rows=int(len(test)),
                accuracy=acc,
                f1=f1,
                auc=auc,
            )
        )

        base_cols = [
            "open_time_utc",
            "close_time_utc",
            "open",
            "high",
            "low",
            "close",
            "future_return",
            "target_up",
            "atr14",
            "ema_gap",
        ]
        optional_cols = list(FEATURE_COLUMNS) + list(RUNTIME_ACTION_COLUMNS) + ["ema20", "ema50", "ema200"]
        ordered_cols = list(dict.fromkeys(base_cols + optional_cols))
        cols_out = [c for c in ordered_cols if c in test.columns]
        part = test[cols_out].copy()
        part["prob_up"] = prob.to_numpy(dtype="float64")
        part["pred_up"] = pred.to_numpy(dtype="int64")
        part["fold_id"] = fold + 1
        oof_parts.append(part)

    if not oof_parts:
        raise ValueError("No walk-forward folds were produced")
    oof = pd.concat(oof_parts, ignore_index=True).sort_values("open_time_utc").reset_index(drop=True)
    return results, oof


def _trend_choices_from_space(space: dict[str, Any], fallback: str) -> list[str]:
    rows = list(space.get("hypothesis_rows") or [])
    out: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = str(row.get("hypothesis", "")).strip()
        if name:
            out.append(name)
    return sorted(set(out)) or ["none"]


def _feature_columns_from_blocks(active_blocks: list[str]) -> list[str]:
    active_set = {str(x).strip() for x in active_blocks if str(x).strip()}
    cols: list[str] = []
    for c in FEATURE_COLUMNS:
        for b in active_set:
            if c in FEATURE_GROUPS.get(b, []):
                cols.append(c)
                break
    # keep order stable and unique
    seen: set[str] = set()
    out: list[str] = []
    for c in cols:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def _feature_columns_from_space_rows(
    *,
    active_blocks: list[str],
    context_blocks: list[str] | None = None,
    feature_rows: list[dict[str, Any]],
) -> list[str]:
    """
    Enforce feature-level toggle behavior:
    only features explicitly present in compiled space.feature_rows
    are allowed into runtime feature columns.
    """
    active_set = {str(x).strip() for x in list(active_blocks or []) if str(x).strip()}
    for block in list(context_blocks or []):
        block_name = str(block).strip()
        if block_name:
            active_set.add(block_name)
    allowed_from_rows: set[str] = set()
    for row in list(feature_rows or []):
        if not isinstance(row, dict):
            continue
        block = str(row.get("block", "")).strip()
        feat = str(row.get("feature", "")).strip()
        if not block or not feat:
            continue
        if block in active_set:
            allowed_from_rows.add(feat)
    out = [c for c in FEATURE_COLUMNS if c in allowed_from_rows]
    if out:
        return out
    # Safety fallback for legacy/incomplete matrices.
    return _feature_columns_from_blocks(list(active_set))


def _collect_active_profile_names(
    *,
    space: dict[str, Any],
    active_blocks: list[str],
    context_blocks: list[str] | None = None,
    enabled_hypotheses: list[str],
) -> list[str]:
    profile_map = dict(space.get("profiles") or {})
    if not profile_map:
        return []
    active_block_set = {str(x).strip() for x in list(active_blocks or []) if str(x).strip()}
    for block in list(context_blocks or []):
        block_name = str(block).strip()
        if block_name:
            active_block_set.add(block_name)
    enabled_hyp_set = {str(x).strip() for x in list(enabled_hypotheses or []) if str(x).strip()}
    names: set[str] = set()

    for row in list(space.get("feature_rows") or []):
        if not isinstance(row, dict):
            continue
        block = str(row.get("block", "")).strip()
        if block and block not in active_block_set:
            continue
        for p in list(row.get("params") or []):
            name = str(p).strip()
            if name and name in profile_map:
                names.add(name)

    for row in list(space.get("hypothesis_rows") or []):
        if not isinstance(row, dict):
            continue
        hyp = str(row.get("hypothesis", "")).strip()
        if hyp and hyp not in enabled_hyp_set:
            continue
        for p in list(row.get("params") or []):
            name = str(p).strip()
            if name and name in profile_map:
                names.add(name)

    # Keep explicitly sampled gap profile always present when available.
    if "min_abs_ema_gap" in profile_map:
        names.add("min_abs_ema_gap")
    return sorted(names)


def _collect_linked_profile_names(*, space: dict[str, Any]) -> list[str]:
    profile_map = dict(space.get("profiles") or {})
    if not profile_map:
        return []
    names: set[str] = set()
    for section in ("feature_rows", "hypothesis_rows"):
        for row in list(space.get(section) or []):
            if not isinstance(row, dict):
                continue
            for p in list(row.get("params") or []):
                name = str(p).strip()
                if name and name in profile_map:
                    names.add(name)
    if "min_abs_ema_gap" in profile_map:
        names.add("min_abs_ema_gap")
    return sorted(names)


def _resolve_profile_sampling_policy(cfg: dict[str, Any]) -> tuple[str, list[str]]:
    """
    Resolve runtime profile sampling policy.

    Policies:
      - conditional_active: sample only profiles linked to active blocks/hypotheses in current trial
      - linked_union: sample all profiles linked in matrix rows (legacy/full mode)
    """
    mode_raw = str((cfg or {}).get("profile_sampling_mode", "conditional_active")).strip().lower()
    if mode_raw not in {"conditional_active", "linked_union"}:
        mode_raw = "conditional_active"
    always_raw = list((cfg or {}).get("always_sample_profiles") or [])
    always_names = sorted({str(x).strip() for x in always_raw if str(x).strip()})
    return mode_raw, always_names


def _resolve_calibration_grid_preset(*, cfg: dict[str, Any], cli_value: str) -> str:
    cli = str(cli_value or "").strip().lower()
    if cli in {"wide", "medium", "narrow"}:
        return cli
    cfg_value = str((cfg or {}).get("calibration_grid_preset", "wide")).strip().lower()
    if cfg_value in {"wide", "medium", "narrow"}:
        return cfg_value
    return "wide"


def _resolve_profile_edge_coverage_mode(*, cfg: dict[str, Any], cli_value: str) -> bool:
    cli = str(cli_value or "").strip().lower()
    if cli == "on":
        return True
    if cli == "off":
        return False
    return bool((cfg or {}).get("force_profile_edge_coverage", False))


def _worker_index_from_contour_id(contour_id: str) -> int:
    raw = str(contour_id or "").strip().lower()
    marker = "_w"
    if marker not in raw:
        return 0
    suffix = raw.rsplit(marker, 1)[-1]
    try:
        ix = int(suffix)
    except ValueError:
        return 0
    return max(0, ix - 1)


def _profile_edge_task_window(*, worker_index: int, worker_count: int, task_count: int) -> tuple[int, int]:
    total = max(0, int(task_count))
    if total <= 0:
        return 0, 0
    workers = max(1, int(worker_count))
    worker_ix = min(max(0, int(worker_index)), workers - 1)
    base = total // workers
    extra = total % workers
    count = base + (1 if worker_ix < extra else 0)
    start = worker_ix * base + min(worker_ix, extra)
    return int(start), int(count)


def _profile_edge_run_index_for_worker(
    *,
    local_profile_index: int,
    worker_index: int,
    worker_count: int,
    task_count: int,
) -> int:
    total = max(0, int(task_count))
    local_ix = max(0, int(local_profile_index))
    if total <= 0 or int(worker_count) <= 1:
        return int(local_ix)
    start, count = _profile_edge_task_window(
        worker_index=int(worker_index),
        worker_count=int(worker_count),
        task_count=int(total),
    )
    if count <= 0 or local_ix >= count:
        return int(total + local_ix)
    return int(start + local_ix)


def _maybe_force_edge_value(
    *,
    values: list[Any],
    value: Any,
    name: str,
    index: int,
    run_trial_index: int,
    item_count: int,
    force_edge_coverage: bool,
) -> tuple[Any, dict[str, Any] | None]:
    seq = list(values or [])
    if not seq:
        return value, None
    count = max(1, int(item_count))
    edge_phase = int(run_trial_index // count)
    edge_target_ix = int(run_trial_index % count)
    forced_edge = bool(force_edge_coverage and edge_phase in {0, 1} and int(index) == edge_target_ix)
    if not forced_edge:
        return value, None
    forced_value = seq[0] if edge_phase == 0 else seq[-1]
    return forced_value, {
        "parameter": str(name),
        "edge": "min" if edge_phase == 0 else "max",
        "value": forced_value,
        "run_trial_index": int(run_trial_index),
        "parameter_order_index": int(index),
    }


def _sample_profile_values(
    *,
    trial: optuna.trial.Trial,
    space: dict[str, Any],
    profile_names: list[str],
    run_trial_index: int = 0,
    force_edge_coverage: bool = False,
) -> dict[str, float]:
    profile_map = dict(space.get("profiles") or {})
    sampled: dict[str, float] = {}
    forced_edges: list[dict[str, Any]] = []
    names_ordered = [str(x) for x in list(profile_names or [])]
    profile_count = len(names_ordered)
    edge_phase = int(run_trial_index // max(1, profile_count))
    edge_target_ix = int(run_trial_index % max(1, profile_count))
    for idx, name in enumerate(names_ordered):
        prof = dict(profile_map.get(str(name), {}) or {})
        values = [float(x) for x in list(prof.get("values") or [])]
        if not values:
            continue
        key = f"profile__{name}"
        sampled_value = float(trial.suggest_categorical(key, values))
        forced_edge = bool(force_edge_coverage and profile_count > 0 and edge_phase in {0, 1} and idx == edge_target_ix)
        if forced_edge:
            forced_value = float(values[0] if edge_phase == 0 else values[-1])
            sampled[str(name)] = float(forced_value)
            forced_edges.append(
                {
                    "profile": str(name),
                    "edge": "min" if edge_phase == 0 else "max",
                    "value": float(forced_value),
                    "run_trial_index": int(run_trial_index),
                    "profile_order_index": int(idx),
                }
            )
        else:
            sampled[str(name)] = float(sampled_value)
    trial.set_user_attr("calibration_params", {str(k): float(v) for k, v in sampled.items()})
    trial.set_user_attr("sampled_profiles", names_ordered)
    trial.set_user_attr("calibration_forced_edges", forced_edges)
    return sampled


def _ensure_selected_trend_enabled(
    *,
    selected_trend: str,
    toggle_map: dict[str, bool],
) -> tuple[dict[str, bool], list[str], bool]:
    """
    Keep Optuna hypothesis toggles consistent with selected trend_filter.

    Without this, low-budget runs can end up with all-pruned trials because
    trend_filter is sampled independently from hypothesis toggles.
    """
    updated: dict[str, bool] = {str(k): bool(v) for k, v in dict(toggle_map or {}).items()}
    trend = str(selected_trend or "").strip()
    forced = False
    if trend:
        if trend not in updated:
            updated[trend] = True
            forced = True
        elif not bool(updated.get(trend, False)):
            updated[trend] = True
            forced = True
    enabled = [name for name, on in updated.items() if bool(on)]
    return updated, enabled, forced


def _resolve_trial_trend_filter(
    *,
    run_trial_index: int,
    hypothesis_names: list[str],
    preferred_trend: str,
    sampled_trend: str,
) -> tuple[str, bool]:
    """
    For low-budget runs keep trial#0 deterministic by trying preferred trend first.
    """
    preferred = str(preferred_trend or "").strip()
    sampled = str(sampled_trend or "").strip()
    if int(run_trial_index) == 0 and preferred and preferred in list(hypothesis_names or []):
        return preferred, True
    return sampled, False


def _extract_signal_count_after_filter(backtest: dict[str, Any]) -> int:
    diag = (backtest or {}).get("trend_filter_diagnostics") or {}
    return int(diag.get("signal_count_after_filter", -1))


def _extract_signal_count_after_min_move(backtest: dict[str, Any]) -> int:
    diag = (backtest or {}).get("trend_filter_diagnostics") or {}
    return int(diag.get("signal_count_after_min_move", -1))


def _extract_signal_count_raw(backtest: dict[str, Any]) -> int:
    diag = (backtest or {}).get("trend_filter_diagnostics") or {}
    return int(diag.get("signal_count_raw", -1))


def _should_relax_zero_raw(
    *,
    signal_mode: str,
    signal_count_raw: int,
    objective_cfg: dict[str, Any],
) -> bool:
    if int(signal_count_raw) != 0:
        return False
    if str(signal_mode).strip().lower() != "short_only":
        return False
    return bool(objective_cfg.get("zero_raw_relax_short_thresholds", True))


def _should_relax_zero_filter(
    *,
    signal_mode: str,
    selected_trend: str,
    signal_count_after_filter: int,
    available_hypotheses: list[str],
    objective_cfg: dict[str, Any],
) -> bool:
    if int(signal_count_after_filter) != 0:
        return False
    if str(selected_trend).strip() == "none":
        return False
    if "none" not in list(available_hypotheses or []):
        return False
    if str(signal_mode).strip().lower() != "short_only":
        return False
    return bool(objective_cfg.get("zero_filter_relax_short_to_none", True))


def _apply_zero_signal_penalties(
    *,
    score: float,
    signal_count_raw: int,
    signal_count_after_filter: int,
    objective_cfg: dict[str, Any],
) -> float:
    adjusted = float(score)
    if int(signal_count_raw) == 0:
        adjusted -= float(objective_cfg.get("zero_raw_penalty", 1.0))
    if int(signal_count_after_filter) == 0:
        adjusted -= float(objective_cfg.get("zero_filter_penalty", 2.0))
    return float(adjusted)


def _apply_min_move_unreachable_guard(
    *,
    gate_pass: bool,
    fail_keys: list[str],
    backtest: dict[str, Any],
) -> tuple[bool, list[str], str]:
    status = classify_backtest_outcome(backtest)
    keys = [str(x) for x in list(fail_keys or [])]
    if status == MIN_MOVE_UNREACHABLE:
        gate_pass = False
        if MIN_MOVE_UNREACHABLE not in keys:
            keys.append(MIN_MOVE_UNREACHABLE)
    return bool(gate_pass), keys, str(status)


def _apply_min_move_unreachable_penalty(
    *,
    score: float,
    runtime_diagnostic_status: str,
    objective_cfg: dict[str, Any],
) -> float:
    if str(runtime_diagnostic_status) != MIN_MOVE_UNREACHABLE:
        return float(score)
    penalty = float(objective_cfg.get("min_move_unreachable_penalty", 25.0))
    return float(score) - penalty


def _apply_objective_mode_overrides(
    *,
    objective_cfg: dict[str, Any],
    signal_mode: str,
) -> dict[str, Any]:
    """
    Apply optional signal_mode-specific objective overrides without mutating source config.
    Supported forms:
      - objective.signal_mode_overrides.<mode> = {...}
      - objective.<mode>_overrides = {...}  (legacy alias)
    """
    merged: dict[str, Any] = dict(objective_cfg or {})
    mode = str(signal_mode or "").strip().lower()
    if not mode:
        return merged
    mode_overrides = (
        (objective_cfg or {}).get("signal_mode_overrides", {}) or {}
    )
    scoped = mode_overrides.get(mode, {}) if isinstance(mode_overrides, dict) else {}
    if isinstance(scoped, dict):
        merged.update(scoped)
    legacy_key = f"{mode}_overrides"
    legacy = (objective_cfg or {}).get(legacy_key, {})
    if isinstance(legacy, dict):
        merged.update(legacy)
    return merged


def _apply_gate_mode_overrides(
    *,
    thresholds: dict[str, Any],
    cfg: dict[str, Any],
    signal_mode: str,
) -> dict[str, Any]:
    """
    Apply signal-mode gate overrides with single-source precedence.

    Canonical source:
      thresholds.gates_signal_mode_overrides.<mode>.<gate_key> = value

    Legacy/fallback source (deprecated):
      optuna.gate_signal_mode_overrides.<mode>.<gate_key> = value

    If both sources provide overlapping keys with different values,
    raise explicit error to prevent silent divergence.
    """
    out: dict[str, Any] = dict(thresholds or {})
    gates = dict(out.get("gates") or {})
    mode = str(signal_mode or "").strip().lower()
    if not mode:
        out["gates"] = gates
        return out

    thresholds_mode_map = dict(out.get("gates_signal_mode_overrides") or {})
    thresholds_scoped = thresholds_mode_map.get(mode, {}) if isinstance(thresholds_mode_map, dict) else {}
    if not isinstance(thresholds_scoped, dict):
        thresholds_scoped = {}

    cfg_mode_map = dict(cfg.get("gate_signal_mode_overrides") or {})
    cfg_scoped = cfg_mode_map.get(mode, {}) if isinstance(cfg_mode_map, dict) else {}
    if not isinstance(cfg_scoped, dict):
        cfg_scoped = {}

    if thresholds_scoped and cfg_scoped:
        overlap = sorted(set(thresholds_scoped.keys()) & set(cfg_scoped.keys()))
        conflicts: list[str] = []
        for key in overlap:
            if str(thresholds_scoped.get(key)) != str(cfg_scoped.get(key)):
                conflicts.append(str(key))
        if conflicts:
            raise RuntimeError(
                "Gate override conflict between thresholds.gates_signal_mode_overrides "
                "and optuna.gate_signal_mode_overrides for mode "
                f"'{mode}': {conflicts}"
            )

    if thresholds_scoped:
        gates.update(thresholds_scoped)
    elif cfg_scoped:
        gates.update(cfg_scoped)

    out["gates"] = gates
    return out


def _build_run_signature(
    *,
    args: argparse.Namespace,
    study_plan: dict[str, Any],
    weights: ObjectiveWeights,
    thresholds: dict[str, Any] | None = None,
    space_signature: str = "",
) -> str:
    objective_cfg = dict(study_plan.get("objective") or {})
    gates_cfg = dict((thresholds or {}).get("gates") or {})
    gates_signature = json.dumps(gates_cfg, ensure_ascii=False, sort_keys=True)
    parts = [
        str(args.symbol),
        str(args.timeframe),
        str(args.start_date),
        str(args.end_date),
        str(args.test_day),
        str(args.contour_id),
        str(args.signal_mode),
        str(args.execution_mode),
        str(args.order_type),
        str(args.fee_bps),
        str(args.slippage_bps),
        str(args.stop_loss_pct),
        str(args.take_profit_pct),
        str(args.tp_min_factor),
        str(args.min_tp_reach_prob),
        str(args.cooldown_bars),
        str(args.limit_offset_bps),
        str(args.trend_filter),
        str(args.min_abs_ema_gap),
        str(args.min_train_rows),
        str(args.n_folds),
        str(args.horizons_grid),
        str(args.p_long_grid),
        str(args.p_short_grid),
        str(args.min_expected_move_grid),
        str(args.notional_usd_grid),
        str(getattr(args, "ml_signal_backend", "on")),
        str(getattr(args, "stage", "auto")),
        str(study_plan.get("n_trials")),
        str(study_plan.get("timeout_sec")),
        str(study_plan.get("seed")),
        str(weights),
        str(objective_cfg.get("drawdown_penalty", "")),
        str(objective_cfg.get("gate_bonus", "")),
        str(objective_cfg.get("no_trade_penalty", "")),
        str(objective_cfg.get("lambda_block", "")),
        str(objective_cfg.get("lambda_hypothesis", "")),
        str(objective_cfg.get("zero_raw_penalty", "")),
        str(objective_cfg.get("zero_filter_penalty", "")),
        str(objective_cfg.get("zero_filter_relax_short_to_none", "")),
        str(objective_cfg.get("zero_raw_relax_short_thresholds", "")),
        str(gates_signature),
        str(space_signature or ""),
    ]
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def _build_space_signature(space: dict[str, Any]) -> str:
    """
    Isolate Optuna studies by executable calibration space.

    Passport matrices can share the same dates, mode, and core grids. The
    signature keeps F013/F014/F015 from resuming each other's stored trials.
    """
    payload = {
        "passport_mode": dict((space or {}).get("passport_mode") or {}),
        "profiles": sorted(str(k) for k in dict((space or {}).get("profiles") or {}).keys()),
        "feature_rows": [
            {
                "block": str(row.get("block", "")),
                "feature": str(row.get("feature", "")),
                "action_id": str(row.get("action_id", "")),
                "params": [str(x) for x in list(row.get("params") or [])],
            }
            for row in list((space or {}).get("feature_rows") or [])
            if isinstance(row, dict)
        ],
        "hypothesis_rows": [
            {
                "hypothesis": str(row.get("hypothesis", "")),
                "params": [str(x) for x in list(row.get("params") or [])],
            }
            for row in list((space or {}).get("hypothesis_rows") or [])
            if isinstance(row, dict)
        ],
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def _active_entry_action_columns_from_space(space: dict[str, Any]) -> list[str]:
    passport_mode = dict((space or {}).get("passport_mode") or {})
    action_id = str(passport_mode.get("action_id", "")).strip()
    runtime_action_columns = set(str(x) for x in RUNTIME_ACTION_COLUMNS)
    if action_id.endswith("_ALLOW") and action_id in runtime_action_columns:
        return [action_id]
    rows = list((space or {}).get("feature_rows") or [])
    out: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        row_action = str(row.get("action_id", "")).strip()
        if row_action.endswith("_ALLOW") and row_action in runtime_action_columns and row_action not in out:
            out.append(row_action)
    return out


def _row_trend_filter(*, trial_params: dict[str, Any], trial_user_attrs: dict[str, Any], fallback: str) -> str:
    # Prefer runtime-selected trend (can differ from initial param due to enabled hypothesis set).
    selected = str((trial_user_attrs or {}).get("selected_trend_filter", "")).strip()
    if selected:
        return selected
    p = str((trial_params or {}).get("trend_filter", "")).strip()
    return p or str(fallback)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return float(default)


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    s = pd.Series(values, dtype="float64")
    return float(s.quantile(q))


def _is_strict_1d1d_protocol(*, start_date: str, end_date: str, test_day: str) -> bool:
    try:
        s = datetime.strptime(str(start_date), "%Y-%m-%d").date()
        e = datetime.strptime(str(end_date), "%Y-%m-%d").date()
        t = datetime.strptime(str(test_day), "%Y-%m-%d").date()
        train_days = (e - s).days + 1
        test_offset_days = (t - e).days
        return bool(train_days == 1 and test_offset_days == 1)
    except Exception:
        return False


def _stage_label(*, signal_mode: str, start_date: str, end_date: str, test_day: str) -> str:
    try:
        mode = str(signal_mode).strip().lower()
        # Stage A/B is only valid for strict 1d(train) -> next day(test) protocol.
        is_1d1d = _is_strict_1d1d_protocol(
            start_date=str(start_date),
            end_date=str(end_date),
            test_day=str(test_day),
        )
        if is_1d1d and mode == "long_only":
            return "A_long_1d1d"
        if is_1d1d and mode == "short_only":
            return "B_short_1d1d"
        return "C_multiday_stability"
    except Exception:
        return "C_multiday_stability"


def _resolve_stage(
    *,
    stage_arg: str,
    signal_mode: str,
    start_date: str,
    end_date: str,
    test_day: str,
) -> str:
    requested = str(stage_arg or "").strip().upper()
    if requested in {"A", "B", "C"}:
        mode = str(signal_mode or "").strip().lower()
        if requested == "A" and mode != "long_only":
            raise ValueError("stage A is only valid for signal_mode=long_only")
        if requested == "B" and mode != "short_only":
            raise ValueError("stage B is only valid for signal_mode=short_only")
        if requested in {"A", "B"} and not _is_strict_1d1d_protocol(
            start_date=str(start_date),
            end_date=str(end_date),
            test_day=str(test_day),
        ):
            raise ValueError(f"stage {requested} requires strict 1d/1d date protocol")
        return requested
    lbl = _stage_label(
        signal_mode=str(signal_mode),
        start_date=str(start_date),
        end_date=str(end_date),
        test_day=str(test_day),
    )
    if str(lbl).startswith("A_"):
        return "A"
    if str(lbl).startswith("B_"):
        return "B"
    return "C"


def _validate_contour_signal_mode(*, contour_id: str, signal_mode: str) -> None:
    cid = str(contour_id or "").strip().lower()
    mode = str(signal_mode or "").strip().lower()

    def _has_mode_token(text: str, token: str) -> bool:
        import re

        pat = rf"(^|[^a-z0-9]){re.escape(token)}($|[^a-z0-9])"
        return re.search(pat, text) is not None

    has_long = _has_mode_token(cid, "long_only")
    has_short = _has_mode_token(cid, "short_only")
    if has_long and has_short:
        raise ValueError("contour_id cannot contain both long_only and short_only tokens")
    if has_long and mode != "long_only":
        raise ValueError("contour_id long_only requires signal_mode=long_only")
    if has_short and mode != "short_only":
        raise ValueError("contour_id short_only requires signal_mode=short_only")


def _build_stability_report(
    *,
    candidates: list[dict[str, Any]],
    pass_candidates: list[dict[str, Any]],
    goal_candidates: list[dict[str, Any]],
    signal_mode: str,
    start_date: str,
    end_date: str,
    test_day: str,
) -> dict[str, Any]:
    total = int(len(candidates))
    pass_n = int(len(pass_candidates))
    goal_n = int(len(goal_candidates))
    returns = [_safe_float((x.get("backtest") or {}).get("net_return_pct", 0.0)) for x in candidates]
    mdds = [abs(_safe_float((x.get("backtest") or {}).get("max_drawdown_pct", 0.0))) for x in candidates]
    trades = [int((x.get("backtest") or {}).get("trades", 0) or 0) for x in candidates]
    raw_zero_count = 0
    filter_zero_count = 0
    relax_attempted_count = 0
    relax_applied_count = 0
    min_move_unreachable_count = 0
    min_move_relax_attempted_count = 0
    min_move_relax_applied_count = 0
    for c in candidates:
        bt = dict(c.get("backtest") or {})
        diag = dict(bt.get("trend_filter_diagnostics") or {})
        signal_count_raw = int(c.get("signal_count_raw", diag.get("signal_count_raw", -1)))
        signal_count_after_filter = int(
            c.get("signal_count_after_filter", diag.get("signal_count_after_filter", -1))
        )
        if signal_count_raw == 0:
            raw_zero_count += 1
        if signal_count_after_filter == 0:
            filter_zero_count += 1
        if bool(c.get("zero_raw_relax_attempted", False)) or bool(c.get("zero_filter_relax_attempted", False)):
            relax_attempted_count += 1
        if bool(c.get("zero_raw_relax_applied", False)) or bool(c.get("zero_filter_relax_applied", False)):
            relax_applied_count += 1
        if bool(c.get("min_move_unreachable", False)) or is_min_move_unreachable(bt):
            min_move_unreachable_count += 1
        if bool(c.get("min_move_unreachable_relax_attempted", False)):
            min_move_relax_attempted_count += 1
        if bool(c.get("min_move_unreachable_relax_applied", False)):
            min_move_relax_applied_count += 1
    return {
        "stage_label": _stage_label(
            signal_mode=str(signal_mode),
            start_date=str(start_date),
            end_date=str(end_date),
            test_day=str(test_day),
        ),
        "candidates_total": total,
        "pass_rate": (float(pass_n) / float(total)) if total > 0 else 0.0,
        "goal_rate": (float(goal_n) / float(total)) if total > 0 else 0.0,
        "tradeful_rate": (float(sum(1 for t in trades if t > 0)) / float(total)) if total > 0 else 0.0,
        "net_return_pct": {
            "median": _quantile(returns, 0.5),
            "p10": _quantile(returns, 0.1),
            "p90": _quantile(returns, 0.9),
            "min": min(returns) if returns else 0.0,
            "max": max(returns) if returns else 0.0,
        },
        "drawdown_abs_pct": {
            "median": _quantile(mdds, 0.5),
            "p90": _quantile(mdds, 0.9),
            "max": max(mdds) if mdds else 0.0,
        },
        "zero_signal_diagnostics": {
            "raw_zero_count": int(raw_zero_count),
            "raw_zero_rate": (float(raw_zero_count) / float(total)) if total > 0 else 0.0,
            "filter_zero_count": int(filter_zero_count),
            "filter_zero_rate": (float(filter_zero_count) / float(total)) if total > 0 else 0.0,
            "relax_attempted_count": int(relax_attempted_count),
            "relax_attempted_rate": (float(relax_attempted_count) / float(total)) if total > 0 else 0.0,
            "relax_applied_count": int(relax_applied_count),
            "relax_applied_rate": (float(relax_applied_count) / float(total)) if total > 0 else 0.0,
        },
        "min_move_diagnostics": {
            "unreachable_after_action_gate_count": int(min_move_unreachable_count),
            "unreachable_after_action_gate_rate": (float(min_move_unreachable_count) / float(total)) if total > 0 else 0.0,
            "relax_attempted_count": int(min_move_relax_attempted_count),
            "relax_attempted_rate": (float(min_move_relax_attempted_count) / float(total)) if total > 0 else 0.0,
            "relax_applied_count": int(min_move_relax_applied_count),
            "relax_applied_rate": (float(min_move_relax_applied_count) / float(total)) if total > 0 else 0.0,
        },
    }


def _build_resource_profile_table(
    *,
    workers_requested: int,
    workers_used: int,
    horizons_count: int,
    cfg: dict[str, Any],
    study_plan: dict[str, Any],
    storage_url: str,
    trials_with_signature: list[optuna.trial.FrozenTrial],
) -> list[dict[str, Any]]:
    resources_cfg = dict(cfg.get("resources") or {})
    completed = sum(1 for t in trials_with_signature if t.state == optuna.trial.TrialState.COMPLETE)
    pruned = sum(1 for t in trials_with_signature if t.state == optuna.trial.TrialState.PRUNED)
    failed = sum(1 for t in trials_with_signature if t.state == optuna.trial.TrialState.FAIL)
    storage_scheme = str(storage_url).split(":", 1)[0]
    return [
        {"metric": "cpu_target_pct", "value": int(resources_cfg.get("cpu_target_pct", 85)), "unit": "%", "note": "policy_cap"},
        {
            "metric": "cpu_ramp_allowed_pct",
            "value": int(resources_cfg.get("cpu_ramp_allowed_pct", 35)),
            "unit": "%",
            "note": "policy_headroom",
        },
        {"metric": "workers_requested", "value": int(workers_requested), "unit": "count", "note": "cli_or_plan"},
        {"metric": "workers_used", "value": int(workers_used), "unit": "count", "note": "effective"},
        {"metric": "horizons_count", "value": int(horizons_count), "unit": "count", "note": "grid_domain"},
        {"metric": "n_trials_planned", "value": int(study_plan.get("n_trials", 0)), "unit": "count", "note": "study_plan"},
        {"metric": "timeout_sec", "value": int(study_plan.get("timeout_sec", 0)), "unit": "sec", "note": "study_plan"},
        {"metric": "trials_completed", "value": int(completed), "unit": "count", "note": "run_signature_scope"},
        {"metric": "trials_pruned", "value": int(pruned), "unit": "count", "note": "run_signature_scope"},
        {"metric": "trials_failed", "value": int(failed), "unit": "count", "note": "run_signature_scope"},
        {"metric": "storage_scheme", "value": storage_scheme, "unit": "type", "note": "optuna_storage"},
    ]


def _effective_study_name(*, base_study_name: str, run_signature: str) -> str:
    base = str(base_study_name).strip()
    sig = str(run_signature).strip()
    if not base:
        base = "optuna_study"
    if not sig:
        return base
    # Keep isolated search spaces in separate studies while preserving resume per run signature.
    return f"{base}__{sig}"


def _shared_study_id(value: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    safe = re.sub(r"[^A-Za-z0-9_.:-]+", "_", raw)
    return safe.strip("_")


def _apply_cli_study_overrides(
    *,
    study_plan: dict[str, Any],
    n_trials_override: int | None,
    timeout_sec_override: int | None,
) -> dict[str, Any]:
    out = dict(study_plan or {})
    if int(n_trials_override or 0) > 0:
        out["n_trials"] = int(n_trials_override)
    if int(timeout_sec_override or 0) > 0:
        out["timeout_sec"] = int(timeout_sec_override)
    return out


def _optuna_mode_dir(*, project_root: Path, signal_mode: str) -> Path:
    mode = str(signal_mode).strip().lower()
    if mode not in {"long_only", "short_only"}:
        raise ValueError(f"invalid signal_mode for optuna artifacts: {signal_mode!r}")
    out_dir = project_root / "reports" / "optuna" / mode
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def _canonical_contract_meta(*, signal_mode: str, contract_version: str) -> dict[str, str]:
    mode = str(signal_mode).strip().lower()
    if mode not in {"long_only", "short_only"}:
        raise ValueError(f"invalid signal_mode for optuna artifacts: {signal_mode!r}")
    version = str(contract_version).strip()
    if not version:
        raise ValueError("invalid contract_version for optuna artifacts: empty")
    return {
        "signal_mode": mode,
        "contract_version": version,
    }


def _build_trial_history_rows(
    candidates: list[dict[str, Any]],
    *,
    signal_mode: str = "",
    contract_version: str = OPTUNA_REPORT_CONTRACT_VERSION,
) -> list[dict[str, Any]]:
    raw_mode = str(signal_mode).strip()
    if raw_mode:
        contract_meta = _canonical_contract_meta(
            signal_mode=raw_mode,
            contract_version=str(contract_version),
        )
    else:
        # Backward-compatible row builder behavior for direct helper calls in tests.
        version = str(contract_version).strip() or str(OPTUNA_REPORT_CONTRACT_VERSION)
        contract_meta = {
            "signal_mode": "",
            "contract_version": version,
        }
    rows: list[dict[str, Any]] = []
    for c in candidates:
        bt = dict(c.get("backtest") or {})
        diag = dict(bt.get("trend_filter_diagnostics") or {})
        runtime_status = str(c.get("runtime_diagnostic_status") or classify_backtest_outcome(bt))
        row = {
            "contract_version": str(contract_meta["contract_version"]),
            "signal_mode": str(contract_meta["signal_mode"]),
            "worker_contour_id": str(c.get("worker_contour_id", "")),
            "study_namespace": str(c.get("study_namespace", "")),
            "shared_study_id": str(c.get("shared_study_id", "")),
            "shared_optuna_study": bool(c.get("shared_optuna_study", False)),
            "sampler_seed_effective": int(c.get("sampler_seed_effective", 0)),
            "profile_edge_worker_offset": int(c.get("profile_edge_worker_offset", 0)),
            "trial_number": int(c.get("trial_number", -1)),
            "score": float(c.get("score", 0.0)),
            "gate_pass": bool(c.get("gate_pass", False)),
            "horizon_bars": int(c.get("horizon_bars", 0)),
            "p_enter_long": float(c.get("p_enter_long", 0.0)),
            "p_enter_short": float(c.get("p_enter_short", 0.0)),
            "min_expected_move_pct": float(c.get("min_expected_move_pct", 0.0)),
            "notional_usd": float(c.get("notional_usd", 0.0)),
            "trend_filter": str(c.get("trend_filter", "")),
            "active_blocks_count": int(len(c.get("active_blocks") or [])),
            "enabled_hypotheses_count": int(len(c.get("enabled_hypotheses") or [])),
            "feature_columns_count": int(c.get("feature_columns_count", 0)),
            "signal_count_raw": int(c.get("signal_count_raw", diag.get("signal_count_raw", -1))),
            "signal_count_after_entry_action_gates": int(
                c.get("signal_count_after_entry_action_gates", diag.get("signal_count_after_entry_action_gates", -1))
            ),
            "signal_count_after_filter": int(c.get("signal_count_after_filter", diag.get("signal_count_after_filter", -1))),
            "signal_count_after_min_move": int(
                c.get("signal_count_after_min_move", diag.get("signal_count_after_min_move", -1))
            ),
            "entries_filled": int(c.get("entries_filled", diag.get("entries_filled", -1))),
            "signal_count_raw_initial": int(c.get("signal_count_raw_initial", -1)),
            "signal_count_raw_relaxed": int(c.get("signal_count_raw_relaxed", -1)),
            "signal_count_after_filter_initial": int(c.get("signal_count_after_filter_initial", -1)),
            "signal_count_after_filter_relaxed": int(c.get("signal_count_after_filter_relaxed", -1)),
            "signal_count_after_min_move_initial": int(c.get("signal_count_after_min_move_initial", -1)),
            "signal_count_after_min_move_relaxed": int(c.get("signal_count_after_min_move_relaxed", -1)),
            "zero_raw_relax_attempted": bool(c.get("zero_raw_relax_attempted", False)),
            "zero_raw_relax_applied": bool(c.get("zero_raw_relax_applied", False)),
            "zero_filter_relax_attempted": bool(c.get("zero_filter_relax_attempted", False)),
            "zero_filter_relax_applied": bool(c.get("zero_filter_relax_applied", False)),
            "zero_filter_gate": bool(c.get("zero_filter_gate", False)),
            "min_move_unreachable": bool(c.get("min_move_unreachable", is_min_move_unreachable(bt))),
            "min_move_unreachable_after_action_gate": bool(diag.get("min_move_unreachable_after_action_gate", False)),
            "min_move_unreachable_relax_attempted": bool(c.get("min_move_unreachable_relax_attempted", False)),
            "min_move_unreachable_relax_applied": bool(c.get("min_move_unreachable_relax_applied", False)),
            "runtime_diagnostic_status": runtime_status,
            "trades": int(bt.get("trades", 0)),
            "net_return_pct": float(bt.get("net_return_pct", 0.0)),
            "max_drawdown_pct": float(bt.get("max_drawdown_pct", 0.0)),
            "hit_rate": float(bt.get("hit_rate", 0.0)),
            "trades_per_day_avg": float(bt.get("trades_per_day_avg", 0.0)),
            "fail_keys": ",".join(str(x) for x in (c.get("fail_keys") or [])),
        }
        calibration_params = dict(c.get("calibration_params") or {})
        for k in sorted(calibration_params.keys()):
            row[f"param_profile__{str(k)}"] = float(calibration_params[k])
        rows.append(row)
    return rows


def _trial_state_counts(trials: list[optuna.trial.FrozenTrial]) -> dict[str, int]:
    return {
        "total": int(len(trials)),
        "completed": int(sum(1 for t in trials if t.state == optuna.trial.TrialState.COMPLETE)),
        "pruned": int(sum(1 for t in trials if t.state == optuna.trial.TrialState.PRUNED)),
        "failed": int(sum(1 for t in trials if t.state == optuna.trial.TrialState.FAIL)),
    }


def _build_grid_edge_coverage_audit(
    *,
    trials: list[optuna.trial.FrozenTrial],
    space: dict[str, Any],
    core_domains: dict[str, list[float | int]],
    grid_preset: str,
    force_profile_edge_coverage: bool,
) -> dict[str, Any]:
    profile_rows: list[dict[str, Any]] = []
    for name, profile in sorted(dict(space.get("profiles") or {}).items()):
        if str(name) in CORE_SEARCH_PARAM_NAMES:
            continue
        values = [float(x) for x in list((profile or {}).get("values") or [])]
        if not values:
            continue
        seen_values: set[float] = set()
        sampled_trial_numbers: list[int] = []
        forced_min_trials: list[int] = []
        forced_max_trials: list[int] = []
        for tr in trials:
            attrs = dict(tr.user_attrs or {})
            params = dict(attrs.get("calibration_params") or {})
            if str(name) in params:
                seen_values.add(float(params[str(name)]))
                sampled_trial_numbers.append(int(tr.number))
            for edge in list(attrs.get("calibration_forced_edges") or []):
                if not isinstance(edge, dict) or str(edge.get("profile")) != str(name):
                    continue
                edge_name = str(edge.get("edge", "")).strip().lower()
                if edge_name == "min":
                    forced_min_trials.append(int(tr.number))
                elif edge_name == "max":
                    forced_max_trials.append(int(tr.number))
        expected_min = float(values[0])
        expected_max = float(values[-1])
        min_seen = any(abs(v - expected_min) < 1e-12 for v in seen_values)
        max_seen = any(abs(v - expected_max) < 1e-12 for v in seen_values)
        profile_rows.append(
            {
                "profile": str(name),
                "expected_values_count": int(len(values)),
                "expected_min": expected_min,
                "expected_max": expected_max,
                "sampled_trials_count": int(len(set(sampled_trial_numbers))),
                "observed_values_count": int(len(seen_values)),
                "observed_min": (float(min(seen_values)) if seen_values else None),
                "observed_max": (float(max(seen_values)) if seen_values else None),
                "min_seen": bool(min_seen),
                "max_seen": bool(max_seen),
                "forced_min_trial_numbers": sorted(set(forced_min_trials)),
                "forced_max_trial_numbers": sorted(set(forced_max_trials)),
                "forced_min_seen": bool(forced_min_trials),
                "forced_max_seen": bool(forced_max_trials),
                "coverage_pass": bool(min_seen and max_seen),
            }
        )

    core_rows: list[dict[str, Any]] = []
    for name, raw_values in sorted(dict(core_domains or {}).items()):
        values = [float(x) for x in list(raw_values or [])]
        if not values:
            continue
        seen_values: set[float] = set()
        suggested_values: set[float] = set()
        forced_min_trials: list[int] = []
        forced_max_trials: list[int] = []
        for tr in trials:
            attrs = dict(tr.user_attrs or {})
            effective_params = dict(attrs.get("core_params") or {})
            suggested_params = dict(attrs.get("core_params_suggested") or {})
            params = dict(tr.params or {})
            if str(name) in effective_params:
                seen_values.add(float(effective_params[str(name)]))
            elif str(name) in params:
                seen_values.add(float(params[str(name)]))
            if str(name) in suggested_params:
                suggested_values.add(float(suggested_params[str(name)]))
            elif str(name) in params:
                suggested_values.add(float(params[str(name)]))
            for edge in list(attrs.get("core_forced_edges") or []):
                if not isinstance(edge, dict) or str(edge.get("parameter")) != str(name):
                    continue
                edge_name = str(edge.get("edge", "")).strip().lower()
                if edge_name == "min":
                    forced_min_trials.append(int(tr.number))
                elif edge_name == "max":
                    forced_max_trials.append(int(tr.number))
        expected_min = float(min(values))
        expected_max = float(max(values))
        min_seen = any(abs(v - expected_min) < 1e-12 for v in seen_values)
        max_seen = any(abs(v - expected_max) < 1e-12 for v in seen_values)
        suggested_min_seen = any(abs(v - expected_min) < 1e-12 for v in suggested_values)
        suggested_max_seen = any(abs(v - expected_max) < 1e-12 for v in suggested_values)
        core_rows.append(
            {
                "parameter": str(name),
                "expected_values_count": int(len(values)),
                "expected_min": expected_min,
                "expected_max": expected_max,
                "observed_values_count": int(len(seen_values)),
                "observed_min": (float(min(seen_values)) if seen_values else None),
                "observed_max": (float(max(seen_values)) if seen_values else None),
                "min_seen": bool(min_seen),
                "max_seen": bool(max_seen),
                "suggested_values_count": int(len(suggested_values)),
                "suggested_min_seen": bool(suggested_min_seen),
                "suggested_max_seen": bool(suggested_max_seen),
                "forced_min_trial_numbers": sorted(set(forced_min_trials)),
                "forced_max_trial_numbers": sorted(set(forced_max_trials)),
                "forced_min_seen": bool(forced_min_trials),
                "forced_max_seen": bool(forced_max_trials),
                "coverage_pass": bool(min_seen and max_seen),
                "forced_coverage_pass": bool(forced_min_trials and forced_max_trials),
            }
        )

    profile_pass = sum(1 for row in profile_rows if bool(row.get("coverage_pass", False)))
    core_pass = sum(1 for row in core_rows if bool(row.get("coverage_pass", False)))
    return {
        "grid_preset": str(grid_preset),
        "force_profile_edge_coverage": bool(force_profile_edge_coverage),
        "trial_state_counts": _trial_state_counts(list(trials)),
        "profile_count": int(len(profile_rows)),
        "profile_coverage_pass_count": int(profile_pass),
        "profile_coverage_fail_count": int(len(profile_rows) - profile_pass),
        "core_parameter_count": int(len(core_rows)),
        "core_coverage_pass_count": int(core_pass),
        "core_coverage_fail_count": int(len(core_rows) - core_pass),
        "profiles": profile_rows,
        "core_parameters": core_rows,
    }


def _build_resume_report(
    *,
    pre_counts: dict[str, int],
    post_counts: dict[str, int],
    scope: str = "effective_study_name",
) -> dict[str, Any]:
    delta_total = int(post_counts.get("total", 0)) - int(pre_counts.get("total", 0))
    delta_completed = int(post_counts.get("completed", 0)) - int(pre_counts.get("completed", 0))
    delta_pruned = int(post_counts.get("pruned", 0)) - int(pre_counts.get("pruned", 0))
    delta_failed = int(post_counts.get("failed", 0)) - int(pre_counts.get("failed", 0))
    return {
        "scope": str(scope),
        "resumed_from_existing_study": bool(int(pre_counts.get("total", 0)) > 0),
        "pre": dict(pre_counts),
        "post": dict(post_counts),
        "added_trials_total": int(max(0, delta_total)),
        "added_trials_completed": int(max(0, delta_completed)),
        "added_trials_pruned": int(max(0, delta_pruned)),
        "added_trials_failed": int(max(0, delta_failed)),
    }


def _write_optuna_artifacts(
    *,
    project_root: Path,
    signal_mode: str,
    ts: str,
    artifact_suffix: str = "",
    summary_payload: dict[str, Any],
    top_candidates: list[dict[str, Any]],
    all_completed_rows: list[dict[str, Any]],
    grid_edge_coverage_audit: dict[str, Any] | None = None,
    contract_version: str = OPTUNA_REPORT_CONTRACT_VERSION,
) -> dict[str, str]:
    contract_meta = _canonical_contract_meta(
        signal_mode=str(signal_mode),
        contract_version=str(contract_version),
    )
    mode = str(contract_meta["signal_mode"])
    out_dir = _optuna_mode_dir(project_root=project_root, signal_mode=mode)
    safe_suffix = _shared_study_id(str(artifact_suffix or ""))
    stamp = f"{ts}_{safe_suffix}" if safe_suffix else ts
    summary_path = out_dir / f"study_summary_{stamp}.json"
    topk_path = out_dir / f"best_trials_topk_{stamp}.json"
    history_path = out_dir / f"trial_history_{stamp}.csv"
    edge_audit_path = out_dir / f"grid_edge_coverage_audit_{stamp}.json"

    summary_payload_out = dict(summary_payload or {})
    # Canonicalize contract meta across all artifacts to prevent payload drift.
    summary_payload_out["contract_version"] = str(contract_meta["contract_version"])
    summary_payload_out["signal_mode"] = str(contract_meta["signal_mode"])
    summary_path.write_text(json.dumps(summary_payload_out, ensure_ascii=False, indent=2), encoding="utf-8")

    top_k_rows: list[dict[str, Any]] = []
    for row in list(top_candidates[:20]):
        x = dict(row or {})
        x["signal_mode"] = str(contract_meta["signal_mode"])
        x["contract_version"] = str(contract_meta["contract_version"])
        top_k_rows.append(x)
    topk_payload = {
        "generated_utc": ts,
        "signal_mode": str(contract_meta["signal_mode"]),
        "contract_version": str(contract_meta["contract_version"]),
        "top_k": top_k_rows,
    }
    topk_path.write_text(json.dumps(topk_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    history_rows = _build_trial_history_rows(
        list(all_completed_rows),
        signal_mode=mode,
        contract_version=str(contract_meta["contract_version"]),
    )
    pd.DataFrame(history_rows).to_csv(history_path, index=False, encoding="utf-8")
    artifacts = {
        "study_summary_path": str(summary_path),
        "best_trials_topk_path": str(topk_path),
        "trial_history_path": str(history_path),
    }
    if grid_edge_coverage_audit is not None:
        edge_payload = dict(grid_edge_coverage_audit or {})
        edge_payload["signal_mode"] = str(contract_meta["signal_mode"])
        edge_payload["contract_version"] = str(contract_meta["contract_version"])
        edge_audit_path.write_text(json.dumps(edge_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        artifacts["grid_edge_coverage_audit_path"] = str(edge_audit_path)
    return artifacts


def _build_artifact_hashes(artifact_paths: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, raw_path in dict(artifact_paths or {}).items():
        p = Path(str(raw_path))
        if not p.exists() or not p.is_file():
            continue
        h = hashlib.sha256()
        with p.open("rb") as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                h.update(chunk)
        out[str(key)] = h.hexdigest()
    return out


def _build_input_fingerprints(
    *,
    project_root: Path,
    rel_paths: list[str],
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    files: dict[str, str] = {}
    for rel in list(rel_paths or []):
        p = (project_root / str(rel)).resolve()
        if not p.exists() or not p.is_file():
            continue
        h = hashlib.sha256()
        with p.open("rb") as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                h.update(chunk)
        files[str(rel)] = h.hexdigest()
    meta = dict(metadata or {})
    meta_raw = json.dumps(meta, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    meta_hash = hashlib.sha256(meta_raw.encode("utf-8")).hexdigest()
    return {
        "files": files,
        "meta": meta,
        "meta_hash": meta_hash,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Real Optuna candidate search (P24) for isolated long/short contours.")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--layer", default="raw", choices=["raw", "core"], help="Data layer for Optuna search input.")
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--test-day", required=True)
    parser.add_argument("--contour-id", required=True)
    parser.add_argument("--signal-mode", required=True, choices=["long_only", "short_only"])
    parser.add_argument(
        "--ml-signal-backend",
        default="on",
        choices=["on", "off"],
        help="Signal backend for Optuna objective: on=ML probability path, off=rule-only deterministic path.",
    )

    parser.add_argument("--min-train-rows", type=int, default=2200)
    parser.add_argument("--n-folds", type=int, default=4)
    parser.add_argument("--fee-bps", type=float, default=10.0)
    parser.add_argument("--slippage-bps", type=float, default=5.0)
    parser.add_argument("--stop-loss-pct", type=float, default=0.01)
    parser.add_argument("--take-profit-pct", type=float, default=0.02)
    parser.add_argument("--tp-min-factor", type=float, default=0.7)
    parser.add_argument("--min-tp-reach-prob", type=float, default=0.58)
    parser.add_argument("--cooldown-bars", type=int, default=0)
    parser.add_argument("--trend-filter", default="none")
    parser.add_argument("--min-abs-ema-gap", type=float, default=0.0)
    parser.add_argument("--leverage", type=float, default=1.0)
    parser.add_argument("--execution-mode", default="research", choices=["research", "exchange_like"])
    parser.add_argument("--order-type", default="market", choices=["market", "limit"])
    parser.add_argument("--limit-offset-bps", type=float, default=2.0)
    parser.add_argument("--disable-timeout-exit", action="store_true", help="Disable time-based trade exit in backtest.")
    parser.add_argument("--horizons-grid", default="1,2,3,4,6,8")
    parser.add_argument("--p-long-grid", default="0.52,0.54,0.56,0.58,0.60")
    parser.add_argument("--p-short-grid", default="0.48,0.46,0.44,0.42,0.40")
    parser.add_argument("--min-expected-move-grid", default="0.0,0.001,0.002,0.003")
    parser.add_argument("--notional-usd-grid", default="10")
    parser.add_argument("--min-net-return-pct-goal", type=float, default=100.0)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--process-workers-total", type=int, default=1)
    parser.add_argument("--stage", default="auto", choices=["auto", "A", "B", "C"])
    parser.add_argument("--n-trials-override", type=int, default=0)
    parser.add_argument("--timeout-sec-override", type=int, default=0)
    parser.add_argument(
        "--shared-study-id",
        default="",
        help="Optional shared Optuna study namespace used by multiple worker contours.",
    )
    parser.add_argument("--calibration-grid-preset", default="auto", choices=["auto", "wide", "medium", "narrow"])
    parser.add_argument("--force-profile-edge-coverage", default="auto", choices=["auto", "on", "off"])
    args = parser.parse_args()
    data_layer = str(getattr(args, "layer", "raw"))

    project_root = Path(__file__).resolve().parents[2]
    enforce_action_allowed(project_root, action="search_gate_candidate")
    try:
        _validate_contour_signal_mode(contour_id=str(args.contour_id), signal_mode=str(args.signal_mode))
    except Exception as e:
        print(json.dumps({"error": str(e), "status": "invalid_contour_signal_mode"}, ensure_ascii=False))
        return 2

    cfg = load_optuna_engine_config(project_root)
    if not bool(cfg.get("enabled", False)):
        print(json.dumps({"error": "optuna engine disabled in configs/optuna_engine.yaml"}, ensure_ascii=False))
        return 2

    shared_study_id = _shared_study_id(str(getattr(args, "shared_study_id", "")))
    study_namespace = shared_study_id or str(args.contour_id)
    study_plan = build_study_plan(
        contour_id=str(study_namespace),
        test_day=str(args.test_day),
        cfg=cfg,
        symbol=str(args.symbol),
        timeframe=str(args.timeframe),
        start_date=str(args.start_date),
        end_date=str(args.end_date),
    )
    try:
        effective_stage = _resolve_stage(
            stage_arg=str(args.stage),
            signal_mode=str(args.signal_mode),
            start_date=str(args.start_date),
            end_date=str(args.end_date),
            test_day=str(args.test_day),
        )
    except Exception as e:
        print(json.dumps({"error": str(e), "status": "invalid_optuna_stage"}, ensure_ascii=False))
        return 2
    stage_profile = resolve_stage_profile(cfg=cfg, stage=effective_stage)
    study_plan = apply_stage_overrides(study_plan=study_plan, stage_profile=stage_profile)
    study_plan = _apply_cli_study_overrides(
        study_plan=study_plan,
        n_trials_override=int(args.n_trials_override),
        timeout_sec_override=int(args.timeout_sec_override),
    )

    storage_url = resolve_storage_url(project_root, cfg)
    storage_scheme = str(storage_url).split(":", 1)[0].strip().lower()
    if shared_study_id and storage_scheme == "sqlite":
        print(
            json.dumps(
                {
                    "error": "shared-study mode requires non-sqlite Optuna storage",
                    "status": "invalid_shared_study_storage",
                    "storage_scheme": storage_scheme,
                    "shared_study_id": shared_study_id,
                },
                ensure_ascii=False,
            )
        )
        return 2
    thresholds = _load_thresholds(project_root)
    matrix = load_calibration_matrix(project_root)
    calibration_grid_preset = _resolve_calibration_grid_preset(
        cfg=cfg,
        cli_value=str(getattr(args, "calibration_grid_preset", "")),
    )
    force_profile_edge_coverage = _resolve_profile_edge_coverage_mode(
        cfg=cfg,
        cli_value=str(getattr(args, "force_profile_edge_coverage", "")),
    )
    space = compile_optuna_space(
        matrix,
        contour_id=str(args.contour_id),
        min_enabled_blocks=1,
        grid_preset=str(calibration_grid_preset),
    )

    raw_df = load_ohlcv_range(
        project_root,
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=args.start_date,
        end_date=args.end_date,
        layer=data_layer,
    )

    horizons = sorted(set(_csv_ints(args.horizons_grid)))
    p_long_grid = sorted(set(_csv_floats(args.p_long_grid)))
    p_short_grid = sorted(set(_csv_floats(args.p_short_grid)))
    min_move_grid = sorted(set(_csv_floats(args.min_expected_move_grid)))
    notional_grid = sorted(set(_csv_floats(args.notional_usd_grid)))
    trend_choices = _trend_choices_from_space(space, fallback=str(args.trend_filter))

    if not horizons or not p_long_grid or not p_short_grid or not min_move_grid or not notional_grid:
        print(json.dumps({"error": "empty search grid detected"}, ensure_ascii=False))
        return 2

    objective_cfg_base = dict(cfg.get("objective") or {})
    objective_cfg = _apply_objective_mode_overrides(
        objective_cfg=objective_cfg_base,
        signal_mode=str(args.signal_mode),
    )
    thresholds = _apply_gate_mode_overrides(
        thresholds=thresholds,
        cfg=cfg,
        signal_mode=str(args.signal_mode),
    )
    # Keep emitted study metadata aligned with runtime-effective objective settings.
    study_plan["objective"] = dict(objective_cfg)
    weights = ObjectiveWeights(
        drawdown_penalty=float(objective_cfg.get("drawdown_penalty", 0.5)),
        gate_bonus=float(objective_cfg.get("gate_bonus", 2.0)),
        no_trade_penalty=float(objective_cfg.get("no_trade_penalty", 100.0)),
        lambda_block=float(objective_cfg.get("lambda_block", 0.2)),
        lambda_hypothesis=float(objective_cfg.get("lambda_hypothesis", 0.1)),
    )
    space_signature = _build_space_signature(space)
    original_contour_id = str(args.contour_id)
    if shared_study_id:
        args.contour_id = str(study_namespace)
    run_signature = _build_run_signature(
        args=args,
        study_plan=study_plan,
        weights=weights,
        thresholds=thresholds,
        space_signature=space_signature,
    )
    args.contour_id = original_contour_id

    horizon_cache: dict[tuple[int, str, tuple[tuple[str, float], ...]], dict[str, Any]] = {}
    trial_index_lock = threading.Lock()
    trial_index_counter = {"value": 0}
    profile_edge_index_counter = {"value": 0}
    profile_edge_worker_index = int(_worker_index_from_contour_id(str(args.contour_id)))
    profile_edge_worker_count = max(1, int(getattr(args, "process_workers_total", 1) or 1))
    profile_edge_worker_offset = int(profile_edge_worker_index) * int(study_plan["n_trials"])
    block_names = list(space.get("enabled_blocks") or [])
    hypothesis_rows = list(space.get("hypothesis_rows") or [])
    hypothesis_names = [
        str(x.get("hypothesis", "")).strip()
        for x in hypothesis_rows
        if isinstance(x, dict) and str(x.get("hypothesis", "")).strip()
    ]
    if not hypothesis_names:
        hypothesis_names = list(trend_choices)
    feature_rows_compiled = list(space.get("feature_rows") or [])
    context_blocks_compiled = [
        str(x).strip() for x in list(space.get("context_blocks") or []) if str(x).strip()
    ]
    effective_feature_blocks_compiled = [
        str(x).strip() for x in list(space.get("effective_feature_blocks") or []) if str(x).strip()
    ]
    profile_sampling_mode, always_sample_profiles_cfg = _resolve_profile_sampling_policy(cfg)
    profile_map = dict(space.get("profiles") or {})
    profile_all_names = set(profile_map.keys())
    always_sample_profiles = [x for x in always_sample_profiles_cfg if x in profile_all_names]
    linked_profile_names = _collect_linked_profile_names(space=space)

    def objective(trial: optuna.trial.Trial) -> float:
        with trial_index_lock:
            run_trial_index = int(trial_index_counter["value"])
            trial_index_counter["value"] = int(run_trial_index + 1)
        trial.set_user_attr("run_signature", run_signature)
        trial.set_user_attr("run_trial_index", int(run_trial_index))
        trial.set_user_attr("profile_edge_worker_offset", int(profile_edge_worker_offset))
        trial.set_user_attr("calibration_grid_preset", str(calibration_grid_preset))
        trial.set_user_attr("force_profile_edge_coverage", bool(force_profile_edge_coverage))
        core_domains = [
            ("horizon_bars", [int(x) for x in horizons]),
            ("p_enter_long", [float(x) for x in p_long_grid]),
            ("p_enter_short", [float(x) for x in p_short_grid]),
            ("min_expected_move_pct", [float(x) for x in min_move_grid]),
            ("notional_usd", [float(x) for x in notional_grid]),
        ]
        h_raw = int(trial.suggest_categorical("horizon_bars", horizons))
        pl_raw = float(trial.suggest_categorical("p_enter_long", p_long_grid))
        ps_raw = float(trial.suggest_categorical("p_enter_short", p_short_grid))
        min_move_raw = float(trial.suggest_categorical("min_expected_move_pct", min_move_grid))
        notional_raw = float(trial.suggest_categorical("notional_usd", notional_grid))
        forced_core_edges: list[dict[str, Any]] = []
        h_forced, edge = _maybe_force_edge_value(
            values=core_domains[0][1],
            value=h_raw,
            name=core_domains[0][0],
            index=0,
            run_trial_index=int(run_trial_index),
            item_count=len(core_domains),
            force_edge_coverage=bool(force_profile_edge_coverage),
        )
        if edge:
            forced_core_edges.append(edge)
        pl_forced, edge = _maybe_force_edge_value(
            values=core_domains[1][1],
            value=pl_raw,
            name=core_domains[1][0],
            index=1,
            run_trial_index=int(run_trial_index),
            item_count=len(core_domains),
            force_edge_coverage=bool(force_profile_edge_coverage),
        )
        if edge:
            forced_core_edges.append(edge)
        ps_forced, edge = _maybe_force_edge_value(
            values=core_domains[2][1],
            value=ps_raw,
            name=core_domains[2][0],
            index=2,
            run_trial_index=int(run_trial_index),
            item_count=len(core_domains),
            force_edge_coverage=bool(force_profile_edge_coverage),
        )
        if edge:
            forced_core_edges.append(edge)
        min_move_forced, edge = _maybe_force_edge_value(
            values=core_domains[3][1],
            value=min_move_raw,
            name=core_domains[3][0],
            index=3,
            run_trial_index=int(run_trial_index),
            item_count=len(core_domains),
            force_edge_coverage=bool(force_profile_edge_coverage),
        )
        if edge:
            forced_core_edges.append(edge)
        notional_forced, edge = _maybe_force_edge_value(
            values=core_domains[4][1],
            value=notional_raw,
            name=core_domains[4][0],
            index=4,
            run_trial_index=int(run_trial_index),
            item_count=len(core_domains),
            force_edge_coverage=bool(force_profile_edge_coverage),
        )
        if edge:
            forced_core_edges.append(edge)
        h = int(h_forced)
        pl = float(pl_forced)
        ps = float(ps_forced)
        min_move = float(min_move_forced)
        notional = float(notional_forced)
        trial.set_user_attr(
            "core_params_suggested",
            {
                "horizon_bars": int(h_raw),
                "p_enter_long": float(pl_raw),
                "p_enter_short": float(ps_raw),
                "min_expected_move_pct": float(min_move_raw),
                "notional_usd": float(notional_raw),
            },
        )
        trial.set_user_attr("core_forced_edges", forced_core_edges)
        signal_mode = str(args.signal_mode).strip().lower()
        if signal_mode == "both":
            if float(ps) >= float(pl):
                trial.set_user_attr("invalid_reason", "short_threshold_not_below_long")
                raise optuna.TrialPruned("short_threshold_not_below_long")
        elif signal_mode == "long_only" and float(ps) >= float(pl):
            # In long-only search, short threshold does not drive entries.
            # Auto-clamp to keep cross-threshold constraints satisfiable and avoid full-study prune-outs.
            ps = float(max(0.0, min(float(ps), float(pl) - 1e-6)))
            trial.set_user_attr("short_threshold_auto_clamped_for_long_only", True)
        elif signal_mode == "short_only" and float(ps) >= float(pl):
            # Symmetric guard for short-only: keep long threshold above short threshold.
            pl = float(min(1.0, max(float(pl), float(ps) + 1e-6)))
            trial.set_user_attr("long_threshold_auto_clamped_for_short_only", True)
        trial.set_user_attr(
            "core_params",
            {
                "horizon_bars": int(h),
                "p_enter_long": float(pl),
                "p_enter_short": float(ps),
                "min_expected_move_pct": float(min_move),
                "notional_usd": float(notional),
            },
        )

        use_blocks: dict[str, bool] = {}
        for b in block_names:
            use_blocks[b] = bool(trial.suggest_categorical(f"use_block__{b}", [True, False]))
        active_block_names = [b for b, on in use_blocks.items() if bool(on)]
        min_enabled_blocks = int(space.get("min_enabled_blocks", 1))
        if len(active_block_names) < min_enabled_blocks:
            raise optuna.TrialPruned("min_enabled_blocks_not_met")
        feature_columns = _feature_columns_from_space_rows(
            active_blocks=active_block_names,
            context_blocks=context_blocks_compiled,
            feature_rows=feature_rows_compiled,
        )
        if not feature_columns:
            raise optuna.TrialPruned("no_feature_columns_from_rows")

        use_hyp_map: dict[str, bool] = {}
        for hname in hypothesis_names:
            use_hyp_map[hname] = bool(trial.suggest_categorical(f"use_hypothesis__{hname}", [True, False]))
        sampled_trend = str(trial.suggest_categorical("trend_filter", hypothesis_names))
        trend, trend_seed_forced_first_trial = _resolve_trial_trend_filter(
            run_trial_index=int(run_trial_index),
            hypothesis_names=hypothesis_names,
            preferred_trend=str(args.trend_filter),
            sampled_trend=sampled_trend,
        )
        if trend_seed_forced_first_trial:
            trial.set_user_attr("trend_seed_forced_first_trial", True)
        use_hyp_map, enabled_hypotheses, trend_forced_enabled = _ensure_selected_trend_enabled(
            selected_trend=trend,
            toggle_map=use_hyp_map,
        )
        if not enabled_hypotheses:
            raise optuna.TrialPruned("no_enabled_hypothesis")
        if trend_forced_enabled:
            trial.set_user_attr("trend_forced_enabled_by_toggle", True)
        active_hypotheses = len(enabled_hypotheses)

        active_profile_names = _collect_active_profile_names(
            space=space,
            active_blocks=active_block_names,
            context_blocks=context_blocks_compiled,
            enabled_hypotheses=enabled_hypotheses,
        )
        if profile_sampling_mode == "linked_union":
            # Legacy/full mode: sample all linked profiles regardless of trial-enabled blocks/hypotheses.
            profile_names_to_sample = sorted(set(linked_profile_names) | set(always_sample_profiles))
        elif bool(force_profile_edge_coverage):
            # Calibration proof mode: when edge coverage is explicitly enabled,
            # force the whole linked profile set so min/max can be audited for
            # the block, not only for whichever rows were active in a trial.
            profile_names_to_sample = sorted(
                (set(linked_profile_names) | set(always_sample_profiles)) - set(CORE_SEARCH_PARAM_NAMES)
            )
        else:
            # P477: conditional runtime profile coverage - sample only currently active profile set.
            profile_names_to_sample = sorted(
                (set(active_profile_names) | set(always_sample_profiles)) - set(CORE_SEARCH_PARAM_NAMES)
            )
        with trial_index_lock:
            local_profile_edge_index = int(profile_edge_index_counter["value"])
            profile_edge_index_counter["value"] = int(local_profile_edge_index + 1)
        profile_edge_task_count = int(2 * len(profile_names_to_sample))
        profile_edge_run_trial_index = _profile_edge_run_index_for_worker(
            local_profile_index=int(local_profile_edge_index),
            worker_index=int(profile_edge_worker_index),
            worker_count=int(profile_edge_worker_count if shared_study_id else 1),
            task_count=int(profile_edge_task_count),
        )
        trial.set_user_attr("profile_edge_local_index", int(local_profile_edge_index))
        trial.set_user_attr("profile_edge_run_trial_index", int(profile_edge_run_trial_index))
        trial.set_user_attr("profile_edge_worker_count", int(profile_edge_worker_count))
        calibration_params = _sample_profile_values(
            trial=trial,
            space=space,
            profile_names=profile_names_to_sample,
            run_trial_index=int(profile_edge_run_trial_index),
            force_edge_coverage=bool(force_profile_edge_coverage),
        )
        gap = float(calibration_params.get("min_abs_ema_gap", float(args.min_abs_ema_gap)))

        runtime_values: dict[str, Any] = {
            "p_long": pl,
            "p_short": ps,
            "min_expected_move_pct": min_move,
            "notional_usd": notional,
            "min_abs_ema_gap": gap,
            "window": h,
            "time_direction": "past_only",
        }
        runtime_values.update({str(k): float(v) for k, v in calibration_params.items()})
        constraints_report = evaluate_runtime_constraints_detailed(list(space.get("constraints") or []), runtime_values)
        trial.set_user_attr("constraints_report", dict(constraints_report))
        failed_constraints = list(constraints_report.get("failed") or [])
        if failed_constraints:
            trial.set_user_attr("invalid_reason", "runtime_constraints_not_met")
            trial.set_user_attr("failed_constraints", list(failed_constraints))
            raise optuna.TrialPruned("runtime_constraints_not_met")

        calibration_signature = tuple((str(k), float(calibration_params[k])) for k in sorted(calibration_params.keys()))
        cache_key = (int(h), "|".join(feature_columns), calibration_signature)
        if cache_key not in horizon_cache:
            horizon_cache[cache_key] = _prepare_horizon_cache(
                raw_df=raw_df,
                horizon_bars=h,
                feature_columns=feature_columns,
                min_train_rows=int(args.min_train_rows),
                n_folds=int(args.n_folds),
                execution_mode=str(args.execution_mode),
                ml_signal_backend=str(getattr(args, "ml_signal_backend", "off")),
                calibration_params=calibration_params,
            )
        cache_row = horizon_cache[cache_key]
        if cache_row.get("error"):
            trial.set_user_attr("horizon_error", str(cache_row.get("error")))
            raise optuna.TrialPruned(str(cache_row.get("error")))

        fold_metrics = dict(cache_row["fold_metrics"])
        oof = cache_row["oof"]
        active_entry_action_columns = _active_entry_action_columns_from_space(space)
        def _run_backtest(
            *,
            trend_filter_name: str,
            p_short_value: float,
            min_move_value: float,
        ) -> dict[str, Any]:
            _, bt_local = run_prob_backtest(
                oof,
                p_enter_long=pl,
                p_enter_short=float(p_short_value),
                fee_bps=float(args.fee_bps),
                slippage_bps=float(args.slippage_bps),
                stop_loss_pct=float(args.stop_loss_pct),
                take_profit_pct=float(args.take_profit_pct),
                min_expected_move_pct=float(min_move_value),
                min_tp_reach_prob=float(args.min_tp_reach_prob),
                tp_min_factor=float(args.tp_min_factor),
                dynamic_tp_enabled=True,
                cooldown_bars=int(args.cooldown_bars),
                trend_filter=str(trend_filter_name),
                min_abs_ema_gap=float(gap),
                notional_usd=float(notional),
                leverage=float(args.leverage),
                signal_mode=str(args.signal_mode),
                execution_mode=str(args.execution_mode),
                order_type=str(args.order_type),
                hold_bars=int(h),
                limit_offset_bps=float(args.limit_offset_bps),
                require_trend_filter_features=True,
                calibration_params=calibration_params,
                active_entry_action_columns=active_entry_action_columns,
                timeout_exit_enabled=not bool(args.disable_timeout_exit),
            )
            return bt_local

        p_short_effective = float(ps)
        min_move_effective = float(min_move)
        trend_effective = str(trend)
        bt = _run_backtest(
            trend_filter_name=trend_effective,
            p_short_value=float(p_short_effective),
            min_move_value=float(min_move_effective),
        )
        signal_count_raw = _extract_signal_count_raw(bt)
        trial.set_user_attr("signal_count_raw_initial", int(signal_count_raw))
        if _should_relax_zero_raw(
            signal_mode=str(args.signal_mode),
            signal_count_raw=int(signal_count_raw),
            objective_cfg=objective_cfg,
        ):
            trial.set_user_attr("zero_raw_relax_attempted", True)
            p_short_relaxed = float(min(p_short_grid or [p_short_effective]))
            min_move_relaxed = float(min(min_move_grid or [min_move_effective]))
            if p_short_relaxed != p_short_effective or min_move_relaxed != min_move_effective:
                bt_raw_relaxed = _run_backtest(
                    trend_filter_name=trend_effective,
                    p_short_value=float(p_short_relaxed),
                    min_move_value=float(min_move_relaxed),
                )
                signal_count_raw_relaxed = _extract_signal_count_raw(bt_raw_relaxed)
                trial.set_user_attr("signal_count_raw_relaxed", int(signal_count_raw_relaxed))
                if int(signal_count_raw_relaxed) > int(signal_count_raw):
                    bt = bt_raw_relaxed
                    signal_count_raw = int(signal_count_raw_relaxed)
                    p_short_effective = float(p_short_relaxed)
                    min_move_effective = float(min_move_relaxed)
                    trial.set_user_attr("zero_raw_relax_applied", True)
                    trial.set_user_attr("zero_raw_relaxed_p_short_from", float(ps))
                    trial.set_user_attr("zero_raw_relaxed_p_short_to", float(p_short_effective))
                    trial.set_user_attr("zero_raw_relaxed_min_move_from", float(min_move))
                    trial.set_user_attr("zero_raw_relaxed_min_move_to", float(min_move_effective))

        signal_count_after_filter = _extract_signal_count_after_filter(bt)
        trial.set_user_attr("signal_count_after_filter_initial", int(signal_count_after_filter))
        if _should_relax_zero_filter(
            signal_mode=str(args.signal_mode),
            selected_trend=str(trend_effective),
            signal_count_after_filter=int(signal_count_after_filter),
            available_hypotheses=hypothesis_names,
            objective_cfg=objective_cfg,
        ):
            trial.set_user_attr("zero_filter_relax_attempted", True)
            bt_relaxed = _run_backtest(
                trend_filter_name="none",
                p_short_value=float(p_short_effective),
                min_move_value=float(min_move_effective),
            )
            signal_count_relaxed = _extract_signal_count_after_filter(bt_relaxed)
            trial.set_user_attr("signal_count_after_filter_relaxed", int(signal_count_relaxed))
            if int(signal_count_relaxed) > int(signal_count_after_filter):
                trend_effective = "none"
                bt = bt_relaxed
                signal_count_after_filter = int(signal_count_relaxed)
                trial.set_user_attr("zero_filter_relax_applied", True)
                trial.set_user_attr("zero_filter_relaxed_from", str(trend))
                trial.set_user_attr("zero_filter_relaxed_to", str(trend_effective))
                use_hyp_map, enabled_hypotheses, trend_relax_forced_enabled = _ensure_selected_trend_enabled(
                    selected_trend=trend_effective,
                    toggle_map=use_hyp_map,
                )
                if trend_relax_forced_enabled:
                    trial.set_user_attr("trend_forced_enabled_by_relax", True)
                active_hypotheses = len(enabled_hypotheses)

        signal_count_after_min_move = _extract_signal_count_after_min_move(bt)
        trial.set_user_attr("signal_count_after_min_move_initial", int(signal_count_after_min_move))
        if bool(objective_cfg.get("min_move_unreachable_relax_to_grid_min", True)) and is_min_move_unreachable(bt):
            min_move_relaxed = float(min(min_move_grid or [min_move_effective]))
            if float(min_move_relaxed) < float(min_move_effective):
                trial.set_user_attr("min_move_unreachable_relax_attempted", True)
                bt_min_relaxed = _run_backtest(
                    trend_filter_name=str(trend_effective),
                    p_short_value=float(p_short_effective),
                    min_move_value=float(min_move_relaxed),
                )
                signal_count_after_min_move_relaxed = _extract_signal_count_after_min_move(bt_min_relaxed)
                trial.set_user_attr(
                    "signal_count_after_min_move_relaxed",
                    int(signal_count_after_min_move_relaxed),
                )
                if (
                    int(signal_count_after_min_move_relaxed) > int(signal_count_after_min_move)
                    or not is_min_move_unreachable(bt_min_relaxed)
                ):
                    bt = bt_min_relaxed
                    min_move_effective = float(min_move_relaxed)
                    signal_count_after_filter = _extract_signal_count_after_filter(bt)
                    signal_count_after_min_move = int(signal_count_after_min_move_relaxed)
                    trial.set_user_attr("min_move_unreachable_relax_applied", True)
                    trial.set_user_attr("min_move_unreachable_relaxed_from", float(min_move))
                    trial.set_user_attr("min_move_unreachable_relaxed_to", float(min_move_effective))
        final_signal_count_raw = int(_extract_signal_count_raw(bt))
        trial.set_user_attr("signal_count_raw", int(final_signal_count_raw))
        trial.set_user_attr("signal_count_after_filter", int(signal_count_after_filter))
        final_signal_count_after_min_move = int(_extract_signal_count_after_min_move(bt))
        trial.set_user_attr("signal_count_after_min_move", int(final_signal_count_after_min_move))
        if signal_count_after_filter == 0:
            trial.set_user_attr("zero_filter_gate", True)
        gate_pass, fail_keys = _gate_decision(fold_metrics, bt, thresholds)
        gate_pass, fail_keys, runtime_diagnostic_status = _apply_min_move_unreachable_guard(
            gate_pass=bool(gate_pass),
            fail_keys=[str(x) for x in fail_keys],
            backtest=bt,
        )
        score = compute_trial_score(
            oos_net_return_pct=float(bt.get("net_return_pct", 0.0)),
            max_drawdown_pct=float(bt.get("max_drawdown_pct", 0.0)),
            gate_pass=bool(gate_pass),
            trades=int(bt.get("trades", 0)),
            active_blocks=int(len(active_block_names)),
            active_hypotheses=int(active_hypotheses),
            weights=weights,
        )
        score = _apply_zero_signal_penalties(
            score=float(score),
            signal_count_raw=int(final_signal_count_raw),
            signal_count_after_filter=int(signal_count_after_filter),
            objective_cfg=objective_cfg,
        )
        score = _apply_min_move_unreachable_penalty(
            score=float(score),
            runtime_diagnostic_status=str(runtime_diagnostic_status),
            objective_cfg=objective_cfg,
        )
        trial.set_user_attr("gate_pass", bool(gate_pass))
        trial.set_user_attr("fail_keys", [str(x) for x in fail_keys])
        trial.set_user_attr("runtime_diagnostic_status", str(runtime_diagnostic_status))
        trial.set_user_attr("min_move_unreachable", str(runtime_diagnostic_status) == MIN_MOVE_UNREACHABLE)
        trial.set_user_attr("ml_signal_backend", str(getattr(args, "ml_signal_backend", "off")))
        trial.set_user_attr("selected_trend_filter", str(trend_effective))
        trial.set_user_attr("selected_trend_filter_sampled", str(trend))
        trial.set_user_attr("selected_p_enter_short", float(p_short_effective))
        trial.set_user_attr("selected_min_expected_move_pct", float(min_move_effective))
        trial.set_user_attr("active_blocks", active_block_names)
        trial.set_user_attr("context_blocks", context_blocks_compiled)
        trial.set_user_attr("effective_feature_blocks", effective_feature_blocks_compiled)
        trial.set_user_attr("active_profiles", active_profile_names)
        trial.set_user_attr("sampled_profiles", profile_names_to_sample)
        trial.set_user_attr("profile_sampling_mode", str(profile_sampling_mode))
        trial.set_user_attr("linked_profiles_count", int(len(linked_profile_names)))
        trial.set_user_attr("calibration_params", {str(k): float(v) for k, v in calibration_params.items()})
        trial.set_user_attr("enabled_hypotheses", enabled_hypotheses)
        trial.set_user_attr("feature_columns", list(feature_columns))
        trial.set_user_attr("feature_columns_count", int(len(feature_columns)))
        trial.set_user_attr("backtest", bt)
        trial.set_user_attr("walk_forward", fold_metrics)
        trial.report(float(score), step=1)
        if trial.should_prune():
            raise optuna.TrialPruned("pruner")
        return float(score)

    sampler_cfg = dict(study_plan.get("sampler") or {})
    pruner_cfg = dict(study_plan.get("pruner") or {})
    base_seed = int(study_plan.get("seed", 20260526))
    contour_id_for_seed = str(getattr(args, "contour_id", "") or "").strip()
    if contour_id_for_seed:
        seed_offset = int(hashlib.sha256(contour_id_for_seed.encode("utf-8")).hexdigest()[:8], 16)
        sampler_seed = int((base_seed + seed_offset) % 2147483647)
        if sampler_seed <= 0:
            sampler_seed = base_seed
    else:
        sampler_seed = base_seed
    sampler = optuna.samplers.TPESampler(
        multivariate=bool(sampler_cfg.get("multivariate", True)),
        group=bool(sampler_cfg.get("group", True)),
        constant_liar=bool(sampler_cfg.get("constant_liar", False)),
        n_startup_trials=int(sampler_cfg.get("n_startup_trials", 40)),
        seed=sampler_seed,
    )
    pruner = optuna.pruners.MedianPruner(
        n_startup_trials=int(pruner_cfg.get("n_startup_trials", 30)),
        n_warmup_steps=int(pruner_cfg.get("n_warmup_steps", 1)),
        interval_steps=int(pruner_cfg.get("interval_steps", 1)),
        n_min_trials=int(pruner_cfg.get("n_min_trials", 10)),
    )

    workers_cli_requested = int(args.workers)
    requested_jobs = workers_cli_requested if workers_cli_requested > 0 else int(study_plan["n_jobs"])
    if requested_jobs <= 0:
        requested_jobs = 1
    # Keep worker semantics aligned with legacy grid backend.
    workers_stage_max = int(stage_profile.get("workers_max", 0) or 0)
    if workers_stage_max > 0:
        requested_jobs = min(requested_jobs, workers_stage_max)
    # For Optuna backend, parallelism is trial-level (n_jobs) and should not be
    # artificially capped by horizons count. Keeping requested_jobs preserves
    # expected CPU utilization in accelerated profiles.
    effective_n_jobs = max(1, int(requested_jobs))
    effective_n_jobs, storage_parallel_guard = enforce_storage_parallel_compat(
        storage_url=storage_url,
        n_jobs=effective_n_jobs,
    )

    study_name = _effective_study_name(base_study_name=str(study_plan.get("study_name", "")), run_signature=run_signature)
    study = optuna.create_study(
        study_name=study_name,
        storage=storage_url,
        direction=str(study_plan["direction"]),
        sampler=sampler,
        pruner=pruner,
        load_if_exists=True,
    )
    pre_counts = _trial_state_counts(list(study.trials))
    study.optimize(
        objective,
        n_trials=int(study_plan["n_trials"]),
        timeout=int(study_plan["timeout_sec"]),
        n_jobs=int(effective_n_jobs),
    )
    post_counts = _trial_state_counts(list(study.trials))
    resume_report = _build_resume_report(pre_counts=pre_counts, post_counts=post_counts, scope="effective_study_name")

    trials_with_signature = [
        t
        for t in study.trials
        if str((t.user_attrs or {}).get("run_signature", "")) == run_signature
    ]
    completed_trials = [
        t
        for t in trials_with_signature
        if t.state == optuna.trial.TrialState.COMPLETE and str((t.user_attrs or {}).get("run_signature", "")) == run_signature
    ]
    if not completed_trials:
        print(json.dumps({"error": "no completed optuna trials for current run_signature"}, ensure_ascii=False))
        return 1

    completed_trials.sort(key=lambda t: float(t.value if t.value is not None else -1e18), reverse=True)
    top = completed_trials[:100]
    top_numbers = {int(t.number) for t in top}

    all_candidates_lite: list[dict[str, Any]] = []
    top_candidates: list[dict[str, Any]] = []
    all_completed_rows: list[dict[str, Any]] = []
    for tr in completed_trials:
        params = dict(tr.params or {})
        user_attrs = dict(tr.user_attrs or {})
        bt = dict(user_attrs.get("backtest") or {})
        bt_diag = dict(bt.get("trend_filter_diagnostics") or {})
        wf = dict(user_attrs.get("walk_forward") or {})
        gate_pass = bool(user_attrs.get("gate_pass", False))
        fail_keys = list(user_attrs.get("fail_keys") or [])
        runtime_diagnostic_status = str(user_attrs.get("runtime_diagnostic_status") or classify_backtest_outcome(bt))
        trend_filter_effective = _row_trend_filter(
            trial_params=params,
            trial_user_attrs=user_attrs,
            fallback=str(args.trend_filter),
        )
        row = {
            "worker_contour_id": str(args.contour_id),
            "study_namespace": str(study_namespace),
            "shared_study_id": str(shared_study_id),
            "shared_optuna_study": bool(shared_study_id),
            "sampler_seed_effective": int(sampler_seed),
            "profile_edge_worker_offset": int(profile_edge_worker_offset),
            "horizon_bars": int(params.get("horizon_bars", 1)),
            "p_enter_long": float(params.get("p_enter_long", 0.55)),
            "p_enter_short": float(user_attrs.get("selected_p_enter_short", params.get("p_enter_short", 0.45))),
            "min_expected_move_pct": float(
                user_attrs.get("selected_min_expected_move_pct", params.get("min_expected_move_pct", 0.0))
            ),
            "notional_usd": float(params.get("notional_usd", 10.0)),
            "leverage": float(args.leverage),
            "signal_mode": str(args.signal_mode),
            "trend_filter": trend_filter_effective,
            "min_abs_ema_gap": float(
                dict(user_attrs.get("calibration_params") or {}).get(
                    "min_abs_ema_gap",
                    params.get("min_abs_ema_gap", args.min_abs_ema_gap),
                )
            ),
            "gate_pass": gate_pass,
            "fail_keys": [str(x) for x in fail_keys],
            "score": float(tr.value if tr.value is not None else -1e18),
            "runtime_diagnostic_status": str(runtime_diagnostic_status),
            "min_move_unreachable": bool(user_attrs.get("min_move_unreachable", is_min_move_unreachable(bt))),
            "walk_forward": wf,
            "backtest": bt,
            "active_blocks": list((tr.user_attrs or {}).get("active_blocks") or []),
            "context_blocks": list((tr.user_attrs or {}).get("context_blocks") or []),
            "effective_feature_blocks": list((tr.user_attrs or {}).get("effective_feature_blocks") or []),
            "active_profiles": list((tr.user_attrs or {}).get("active_profiles") or []),
            "calibration_params": dict((tr.user_attrs or {}).get("calibration_params") or {}),
            "enabled_hypotheses": list((tr.user_attrs or {}).get("enabled_hypotheses") or []),
            "feature_columns": list((tr.user_attrs or {}).get("feature_columns") or []),
            "feature_columns_count": int((tr.user_attrs or {}).get("feature_columns_count", 0)),
            "signal_count_raw": int((tr.user_attrs or {}).get("signal_count_raw", -1)),
            "signal_count_after_entry_action_gates": int(bt_diag.get("signal_count_after_entry_action_gates", -1)),
            "signal_count_after_filter": int((tr.user_attrs or {}).get("signal_count_after_filter", -1)),
            "signal_count_after_min_move": int((tr.user_attrs or {}).get("signal_count_after_min_move", -1)),
            "entries_filled": int(bt_diag.get("entries_filled", -1)),
            "signal_count_raw_initial": int((tr.user_attrs or {}).get("signal_count_raw_initial", -1)),
            "signal_count_raw_relaxed": int((tr.user_attrs or {}).get("signal_count_raw_relaxed", -1)),
            "signal_count_after_filter_initial": int((tr.user_attrs or {}).get("signal_count_after_filter_initial", -1)),
            "signal_count_after_filter_relaxed": int((tr.user_attrs or {}).get("signal_count_after_filter_relaxed", -1)),
            "signal_count_after_min_move_initial": int((tr.user_attrs or {}).get("signal_count_after_min_move_initial", -1)),
            "signal_count_after_min_move_relaxed": int((tr.user_attrs or {}).get("signal_count_after_min_move_relaxed", -1)),
            "zero_raw_relax_attempted": bool((tr.user_attrs or {}).get("zero_raw_relax_attempted", False)),
            "zero_raw_relax_applied": bool((tr.user_attrs or {}).get("zero_raw_relax_applied", False)),
            "zero_filter_relax_attempted": bool((tr.user_attrs or {}).get("zero_filter_relax_attempted", False)),
            "zero_filter_relax_applied": bool((tr.user_attrs or {}).get("zero_filter_relax_applied", False)),
            "zero_filter_gate": bool((tr.user_attrs or {}).get("zero_filter_gate", False)),
            "min_move_unreachable_relax_attempted": bool(
                (tr.user_attrs or {}).get("min_move_unreachable_relax_attempted", False)
            ),
            "min_move_unreachable_relax_applied": bool(
                (tr.user_attrs or {}).get("min_move_unreachable_relax_applied", False)
            ),
            "trial_number": int(tr.number),
        }
        all_completed_rows.append(row)
        if int(tr.number) not in top_numbers:
            continue
        all_candidates_lite.append(
            {
                "horizon_bars": row["horizon_bars"],
                "p_enter_long": row["p_enter_long"],
                "p_enter_short": row["p_enter_short"],
                "min_expected_move_pct": row["min_expected_move_pct"],
                "notional_usd": row["notional_usd"],
                "leverage": row["leverage"],
                "signal_mode": row["signal_mode"],
                "trend_filter": row["trend_filter"],
                "min_abs_ema_gap": row["min_abs_ema_gap"],
                "gate_pass": row["gate_pass"],
                "fail_keys": row["fail_keys"],
                "score": row["score"],
                "runtime_diagnostic_status": row["runtime_diagnostic_status"],
                "min_move_unreachable": row["min_move_unreachable"],
                "backtest": {
                    "trades": int(bt.get("trades", 0)),
                    "net_return_pct": float(bt.get("net_return_pct", 0.0)),
                    "max_drawdown_pct": float(bt.get("max_drawdown_pct", 0.0)),
                    "hit_rate": float(bt.get("hit_rate", 0.0)),
                    "no_trade_ratio_days": float(bt.get("no_trade_ratio_days", bt.get("no_trade_ratio", 1.0))),
                    "trades_per_day_avg": float(bt.get("trades_per_day_avg", 0.0)),
                    "min_expected_move_pct": float(bt.get("min_expected_move_pct", row["min_expected_move_pct"])),
                    "trend_filter_diagnostics": {
                        "signal_count_after_entry_action_gates": int(
                            bt_diag.get("signal_count_after_entry_action_gates", -1)
                        ),
                        "signal_count_after_filter": int(bt_diag.get("signal_count_after_filter", -1)),
                        "signal_count_after_min_move": int(bt_diag.get("signal_count_after_min_move", -1)),
                        "entries_filled": int(bt_diag.get("entries_filled", -1)),
                        "min_move_unreachable_after_action_gate": bool(
                            bt_diag.get("min_move_unreachable_after_action_gate", False)
                        ),
                        "min_move_proxy_after_action_gate_max": float(
                            bt_diag.get("min_move_proxy_after_action_gate_max", 0.0)
                        ),
                    },
                },
                "active_blocks": row["active_blocks"],
                "context_blocks": row["context_blocks"],
                "effective_feature_blocks": row["effective_feature_blocks"],
                "enabled_hypotheses": row["enabled_hypotheses"],
                "feature_columns": row["feature_columns"],
                "feature_columns_count": row["feature_columns_count"],
                "worker_contour_id": row["worker_contour_id"],
                "study_namespace": row["study_namespace"],
                "shared_study_id": row["shared_study_id"],
                "shared_optuna_study": row["shared_optuna_study"],
                "sampler_seed_effective": row["sampler_seed_effective"],
                "profile_edge_worker_offset": row["profile_edge_worker_offset"],
            }
        )
        top_candidates.append(row)

    best = top_candidates[0]
    passed = [x for x in top_candidates if bool(x.get("gate_pass", False))]
    goal_min = float(args.min_net_return_pct_goal)
    goal_hits = [x for x in top_candidates if float((x.get("backtest") or {}).get("net_return_pct", 0.0)) >= goal_min]
    stability_passed = [x for x in all_completed_rows if bool(x.get("gate_pass", False))]
    stability_goal_hits = [
        x for x in all_completed_rows if float((x.get("backtest") or {}).get("net_return_pct", 0.0)) >= goal_min
    ]
    best_pass = passed[0] if passed else None
    best_goal = goal_hits[0] if goal_hits else None
    stability_report = _build_stability_report(
        candidates=all_completed_rows,
        pass_candidates=stability_passed,
        goal_candidates=stability_goal_hits,
        signal_mode=str(args.signal_mode),
        start_date=str(args.start_date),
        end_date=str(args.end_date),
        test_day=str(args.test_day),
    )
    resource_profile_table = _build_resource_profile_table(
        workers_requested=int(requested_jobs),
        workers_used=int(effective_n_jobs),
        horizons_count=int(len(horizons)),
        cfg=cfg,
        study_plan=study_plan,
        storage_url=storage_url,
        trials_with_signature=trials_with_signature,
    )
    grid_edge_coverage_audit = _build_grid_edge_coverage_audit(
        trials=list(trials_with_signature),
        space=space,
        core_domains={
            "horizon_bars": [int(x) for x in horizons],
            "p_enter_long": [float(x) for x in p_long_grid],
            "p_enter_short": [float(x) for x in p_short_grid],
            "min_expected_move_pct": [float(x) for x in min_move_grid],
            "notional_usd": [float(x) for x in notional_grid],
        },
        grid_preset=str(calibration_grid_preset),
        force_profile_edge_coverage=bool(force_profile_edge_coverage),
    )

    out = {
        "contract_version": OPTUNA_REPORT_CONTRACT_VERSION,
        "run_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "data_layer": data_layer,
        "date_range": {"start": args.start_date, "end": args.end_date},
        "workers_cli_requested": int(workers_cli_requested),
        "workers_requested": int(requested_jobs),
        "workers_used": int(effective_n_jobs),
        "shared_optuna_study": bool(shared_study_id),
        "shared_study_id": str(shared_study_id),
        "worker_contour_id": str(args.contour_id),
        "study_namespace": str(study_namespace),
        "storage_parallel_guard": dict(storage_parallel_guard),
        "resume_report": dict(resume_report),
        "total_candidates": int(len(top_candidates)),
        "pass_candidates": int(len(passed)),
        "goal_min_net_return_pct": goal_min,
        "goal_candidates": int(len(goal_hits)),
        "horizon_errors": [
            {
                "horizon_bars": int(k[0]),
                "feature_signature": str(k[1]),
                "calibration_signature": str(k[2]),
                "error": str(v.get("error")),
            }
            for k, v in sorted(horizon_cache.items(), key=lambda x: (x[0][0], x[0][1], str(x[0][2])))
            if isinstance(v, dict) and v.get("error")
        ],
        "horizon_proxy_stats": [],
        "best_candidate": best,
        "best_pass_candidate": best_pass,
        "best_goal_candidate": best_goal,
        "all_candidates_lite": all_candidates_lite,
        "top5": top_candidates[:5],
        "top_candidates": top_candidates,
        "stability_report": stability_report,
        "grid_edge_coverage_audit": grid_edge_coverage_audit,
        "resource_profile_table": resource_profile_table,
        "search_engine": {
            "mode": "optuna_real",
            "contour_id": str(args.contour_id),
            "worker_contour_id": str(args.contour_id),
            "study_namespace": str(study_namespace),
            "shared_optuna_study": bool(shared_study_id),
            "shared_study_id": str(shared_study_id),
            "signal_mode": str(args.signal_mode),
            "stage_requested": str(args.stage),
            "stage_effective": str(effective_stage),
            "ml_signal_backend": str(getattr(args, "ml_signal_backend", "off")),
            "decoupled_ml": bool(str(getattr(args, "ml_signal_backend", "off")).strip().lower() == "off"),
            "stage_profile": stage_profile,
            "run_signature": run_signature,
            "space_signature": space_signature,
            "study_name_effective": study_name,
            "study_plan": study_plan,
            "sampler_seed_effective": int(sampler_seed),
            "core_executable_params_only": False,
            "block_hypothesis_toggles_runtime_enabled": True,
            "calibration_grid_preset": str(calibration_grid_preset),
            "force_profile_edge_coverage": bool(force_profile_edge_coverage),
            "storage_url_redacted": str(storage_url).split("@")[-1],
        },
    }
    out["input_fingerprints"] = _build_input_fingerprints(
        project_root=project_root,
        rel_paths=[
            "configs/calibration_full_matrix_v1.yaml",
            "configs/optuna_engine.yaml",
            "configs/thresholds.yaml",
        ],
        metadata={
            "run_signature": str(run_signature),
            "space_signature": str(space_signature),
            "stage_effective": str(effective_stage),
            "signal_mode": str(args.signal_mode),
            "contour_id": str(args.contour_id),
        },
    )

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out["optuna_artifacts"] = _write_optuna_artifacts(
        project_root=project_root,
        signal_mode=str(args.signal_mode),
        ts=ts,
        artifact_suffix=str(args.contour_id),
        summary_payload=out,
        top_candidates=top_candidates,
        all_completed_rows=all_completed_rows,
        grid_edge_coverage_audit=grid_edge_coverage_audit,
        contract_version=OPTUNA_REPORT_CONTRACT_VERSION,
    )
    out["artifact_hashes"] = _build_artifact_hashes(dict(out.get("optuna_artifacts") or {}))

    out_dir = project_root / "reports" / "pipeline"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"optuna_search_candidate_{args.symbol}_{args.timeframe}_{ts}_{_shared_study_id(str(args.contour_id))}.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "report_path": str(out_path),
                "optuna_artifacts": dict(out.get("optuna_artifacts") or {}),
                "pass_candidates": int(len(passed)),
                "best_score": float(best.get("score", -1e18)),
                "search_engine": "optuna_real",
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
