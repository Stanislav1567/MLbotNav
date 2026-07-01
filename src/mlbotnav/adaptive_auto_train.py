from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from mlbotnav.cpu_budget import (
    apply_thread_limits,
    choose_next_threads,
    choose_next_threads_sustained,
    read_total_cpu_pct,
    sample_cpu_window,
    wait_for_cpu_budget,
)
from mlbotnav.dataset import FEATURE_COLUMNS
from mlbotnav.hypothesis_registry import load_backlog_registry
from mlbotnav.preflight_policy import resolve_preflight_runtime_args
from mlbotnav.readiness import check_action_allowed, load_readiness, save_readiness
from mlbotnav.runtime_diagnostics import MIN_MOVE_UNREACHABLE, is_min_move_unreachable
from mlbotnav.top_strategy import publish_best_oos_from_adaptive


def _parse_ymd(value: str, *, arg_name: str) -> date:
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except Exception as e:
        raise ValueError(f"{arg_name} must be YYYY-MM-DD, got: {value}") from e


def _validate_fixed_daily_windows(train_start: str, train_end: str, test_day: str, test_end_day: str | None) -> dict:
    ts = _parse_ymd(train_start, arg_name="--train-start")
    te = _parse_ymd(train_end, arg_name="--train-end")
    td = _parse_ymd(test_day, arg_name="--test-day")
    ted = _parse_ymd(test_end_day, arg_name="--test-end-day") if test_end_day else td

    # Fixed mode: one full UTC day for train and one full UTC day for test.
    if ted != td:
        raise ValueError("--test-end-day must equal --test-day (exactly one 24h test day).")
    if ts != te:
        raise ValueError("--train-start must equal --train-end (exactly one 24h train day).")
    if ts != (td - timedelta(days=1)):
        raise ValueError("Train day must be exactly previous UTC day of test day.")

    # Test day must be fully closed (cannot be today UTC).
    today_utc = datetime.now(timezone.utc).date()
    last_closed_day = today_utc - timedelta(days=1)
    if td > last_closed_day:
        raise ValueError(
            f"Test day must be closed UTC day. Latest allowed now: {last_closed_day.isoformat()}, got: {td.isoformat()}."
        )
    return {
        "train_day": ts.isoformat(),
        "test_day": td.isoformat(),
        "last_closed_day_utc": last_closed_day.isoformat(),
    }


def _validate_multiday_windows(train_start: str, train_end: str, test_day: str, test_end_day: str | None) -> dict:
    ts = _parse_ymd(train_start, arg_name="--train-start")
    te = _parse_ymd(train_end, arg_name="--train-end")
    td = _parse_ymd(test_day, arg_name="--test-day")
    ted = _parse_ymd(test_end_day, arg_name="--test-end-day") if test_end_day else td

    if te < ts:
        raise ValueError("--train-end must be >= --train-start.")
    if ted < td:
        raise ValueError("--test-end-day must be >= --test-day.")

    # Require contiguous non-overlapping windows where test starts the day after train ends.
    if td != (te + timedelta(days=1)):
        raise ValueError("For multiday policy, test_day must be exactly next day after train_end.")

    today_utc = datetime.now(timezone.utc).date()
    last_closed_day = today_utc - timedelta(days=1)
    if ted > last_closed_day:
        raise ValueError(
            f"Test window must end on closed UTC day. Latest allowed now: {last_closed_day.isoformat()}, got: {ted.isoformat()}."
        )

    train_days = (te - ts).days + 1
    test_days = (ted - td).days + 1
    return {
        "train_start": ts.isoformat(),
        "train_end": te.isoformat(),
        "train_days": int(train_days),
        "test_start": td.isoformat(),
        "test_end": ted.isoformat(),
        "test_days": int(test_days),
        "last_closed_day_utc": last_closed_day.isoformat(),
    }


def _unlock_marker_path(project_root: Path) -> Path:
    return project_root / "reports" / "readiness" / "temp_unlock_marker.json"


def _pid_alive(pid: int) -> bool:
    try:
        if pid <= 0:
            return False
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def _restore_stale_temporary_unlock(project_root: Path) -> dict | None:
    marker_path = _unlock_marker_path(project_root)
    if not marker_path.exists():
        return None
    try:
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
        if not isinstance(marker, dict):
            return None
        owner_pid = int(marker.get("owner_pid", 0) or 0)
        original = marker.get("original_readiness", None)
        if not isinstance(original, dict):
            return None
        if _pid_alive(owner_pid):
            return {"restored": False, "reason": "owner_pid_alive", "owner_pid": owner_pid}
        save_readiness(project_root, original)
        marker_path.unlink(missing_ok=True)
        return {"restored": True, "reason": "stale_marker_recovered", "owner_pid": owner_pid}
    except Exception as e:
        return {"restored": False, "reason": f"stale_marker_error:{e}"}


def _write_unlock_marker(project_root: Path, *, original_readiness: dict) -> Path:
    marker_path = _unlock_marker_path(project_root)
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "owner_pid": int(os.getpid()),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "original_readiness": original_readiness,
    }
    marker_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return marker_path


def _clear_unlock_marker(project_root: Path) -> None:
    try:
        _unlock_marker_path(project_root).unlink(missing_ok=True)
    except Exception:
        pass


def _extract_json(stdout: str) -> dict | None:
    txt = (stdout or "").strip()
    if not txt:
        return None
    try:
        obj = json.loads(txt)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    lines = [x.strip() for x in txt.splitlines() if x.strip()]
    for line in reversed(lines):
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                return obj
        except Exception:
            continue
    return None


def _sha256_path(path: Path) -> str | None:
    try:
        if not path.exists() or not path.is_file():
            return None
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def _build_repro_manifest(project_root: Path) -> dict:
    rel_files = [
        "src/mlbotnav/adaptive_auto_train.py",
        "src/mlbotnav/search_gate_candidate.py",
        "src/mlbotnav/pipeline_train_eval.py",
        "src/mlbotnav/oos_evaluate.py",
        "src/mlbotnav/backtest.py",
        "src/mlbotnav/validation.py",
        "src/mlbotnav/dataset.py",
        "src/mlbotnav/top_strategy.py",
    ]
    files: dict[str, str] = {}
    for rel in rel_files:
        p = project_root / Path(rel)
        digest = _sha256_path(p)
        if digest:
            files[rel] = digest
    joined = "|".join(f"{k}:{files[k]}" for k in sorted(files.keys()))
    core_hash = hashlib.sha256(joined.encode("utf-8")).hexdigest() if joined else None
    feature_schema_raw = "|".join(str(x) for x in FEATURE_COLUMNS)
    feature_schema_hash = hashlib.sha256(feature_schema_raw.encode("utf-8")).hexdigest() if feature_schema_raw else None
    return {
        "core_files_sha256": files,
        "core_snapshot_hash": core_hash,
        "feature_schema_hash": feature_schema_hash,
        "feature_count_declared": int(len(FEATURE_COLUMNS)),
    }


def _read_train_report_meta(path_raw: str | None) -> dict:
    if not path_raw:
        return {}
    try:
        p = Path(str(path_raw))
        if not p.exists():
            return {}
        rep = json.loads(p.read_text(encoding="utf-8"))
        return {
            "train_report_path": str(p),
            "rows_raw": int(rep.get("rows_raw", 0)) if rep.get("rows_raw") is not None else None,
            "rows_featured": int(rep.get("rows_featured", 0)) if rep.get("rows_featured") is not None else None,
            "horizon_bars": int(rep.get("horizon_bars", 0)) if rep.get("horizon_bars") is not None else None,
            "selected_model": rep.get("selected_model"),
            "gate_pass": bool((rep.get("gate") or {}).get("pass", False)),
            "gate_reasons": list((rep.get("gate") or {}).get("reasons", [])),
            "report_sha256": _sha256_path(p),
        }
    except Exception:
        return {}


def _run(
    project_root: Path,
    cmd: list[str],
    *,
    cpu_max: float,
    max_threads: int,
    budget_check_interval_sec: float = 2.0,
    budget_max_wait_sec: float = 120.0,
    budget_consecutive_ok: int = 1,
) -> tuple[int, dict | None, str, str]:
    wait_for_cpu_budget(
        max_cpu_pct=cpu_max,
        check_interval_sec=float(budget_check_interval_sec),
        max_wait_sec=float(budget_max_wait_sec),
        consecutive_ok=max(1, int(budget_consecutive_ok)),
    )
    env = apply_thread_limits(os.environ.copy(), max_threads=max_threads)
    env["PYTHONPATH"] = "src"
    p = subprocess.run(cmd, cwd=project_root, env=env, capture_output=True, text=True)
    parsed = _extract_json(p.stdout or "")
    return int(p.returncode), parsed, (p.stdout or ""), (p.stderr or "")


def _run_preflight_window_once(
    project_root: Path,
    *,
    symbol: str,
    timeframe: str,
    train_start: str,
    train_end: str,
    test_day: str,
    test_end_day: str,
    min_train_rows: int,
    n_folds: int,
    horizons_grid: str,
    layer: str,
) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    cmd = [
        sys.executable,
        "-m",
        "mlbotnav.preflight_window",
        "--symbol",
        str(symbol),
        "--timeframe",
        str(timeframe),
        "--train-start",
        str(train_start),
        "--train-end",
        str(train_end),
        "--test-day",
        str(test_day),
        "--test-end-day",
        str(test_end_day),
        "--min-train-rows",
        str(int(min_train_rows)),
        "--n-folds",
        str(int(n_folds)),
        "--horizons-grid",
        str(horizons_grid),
        "--layer",
        str(layer),
    ]
    p = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, env=env)
    parsed = _extract_json(p.stdout or "")
    return {
        "cmd": cmd,
        "returncode": int(p.returncode),
        "parsed_json": parsed,
        "stdout_tail": (p.stdout or "")[-3000:],
        "stderr_tail": (p.stderr or "")[-3000:],
    }


def _read_json_report_with_retry(
    report_path: str | Path,
    *,
    attempts: int = 5,
    delay_sec: float = 0.2,
) -> tuple[dict | None, str | None]:
    path = Path(report_path)
    last_error: str | None = None
    for attempt in range(max(1, int(attempts))):
        try:
            text = path.read_text(encoding="utf-8")
            if not text.strip():
                raise ValueError("report file is empty")
            payload = json.loads(text)
            if not isinstance(payload, dict):
                raise ValueError("report JSON is not an object")
            return payload, None
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < max(1, int(attempts)) - 1:
                time.sleep(max(0.0, float(delay_sec)))
    return None, last_error


def _apply_speed_profile(args: argparse.Namespace) -> None:
    profile = str(getattr(args, "speed_profile", "custom") or "custom").strip().lower()
    if profile == "custom":
        return
    default_horizons = "1,2,3,4,6,8,12,20"
    default_min_move = "0.0,0.001,0.002,0.003"
    default_p_long = "0.52,0.54,0.56,0.58,0.60,0.62,0.65"
    default_p_short = "0.48,0.46,0.44,0.42,0.40,0.38,0.35"
    # Presets are intentionally conservative for quality and predictable wall-clock.
    if profile == "turbo":
        # Keep user-defined repeats in turbo mode.
        # Tune grids only if they are still defaults, so explicit CLI grids are preserved.
        if str(getattr(args, "horizons_grid", "")).strip() == default_horizons:
            args.horizons_grid = "20,30,45,60,90"
        if str(getattr(args, "min_expected_move_grid", "")).strip() == default_min_move:
            args.min_expected_move_grid = "0.0,0.001,0.002,0.003"
        if str(args.signal_mode) == "long_only":
            if str(getattr(args, "p_long_grid", "")).strip() == default_p_long:
                args.p_long_grid = "0.58,0.60,0.62,0.65,0.68,0.72,0.75,0.80"
            if str(getattr(args, "p_short_grid", "")).strip() == default_p_short:
                args.p_short_grid = "0.40"
        elif str(args.signal_mode) == "short_only":
            if str(getattr(args, "p_long_grid", "")).strip() == default_p_long:
                args.p_long_grid = "0.60"
            if str(getattr(args, "p_short_grid", "")).strip() == default_p_short:
                args.p_short_grid = "0.42,0.40,0.38,0.35,0.32,0.30,0.28,0.25,0.20"
        # Faster ramp/control defaults for calibration loops (preserve explicit CLI values).
        # Faster control loop for turbo calibration (still smooth, less idle time).
        if float(getattr(args, "cpu_control_window_sec", 10.0)) == 10.0:
            args.cpu_control_window_sec = 2.0
        if float(getattr(args, "cpu_sample_interval_sec", 1.0)) == 1.0:
            args.cpu_sample_interval_sec = 0.5
        if float(getattr(args, "cpu_budget_check_interval_sec", 2.0)) == 2.0:
            args.cpu_budget_check_interval_sec = 1.0
        if float(getattr(args, "cpu_budget_max_wait_sec", 120.0)) == 120.0:
            args.cpu_budget_max_wait_sec = 60.0
        if int(getattr(args, "cpu_budget_consecutive_ok", 1)) == 1:
            args.cpu_budget_consecutive_ok = 1
    elif profile == "balanced":
        args.repeats = min(int(args.repeats), 12)
        if str(getattr(args, "horizons_grid", "")).strip() == default_horizons:
            args.horizons_grid = "12,20,30,45,60,90,120"
        if str(getattr(args, "min_expected_move_grid", "")).strip() == default_min_move:
            args.min_expected_move_grid = "0.0,0.001,0.002,0.003"
    elif profile == "full":
        # Keep user-provided grids; only soften repeated heavy loops if extreme.
        args.repeats = min(int(args.repeats), 20)


def _next_threads(
    *,
    runtime_threads: int,
    iter_threads: int,
    ramp_min: int,
    cpu_ramp_enabled: bool,
    cpu_max_pct: float,
    cpu_ramp_up_step: int,
    cpu_ramp_down_step: int,
    cpu_control_window_sec: float,
    cpu_sample_interval_sec: float,
    cpu_hot_threshold_pct: float,
    cpu_cool_threshold_pct: float,
) -> tuple[int, float | None, dict]:
    if not cpu_ramp_enabled:
        return int(iter_threads), None, {"mode": "disabled"}
    stats = sample_cpu_window(window_sec=float(cpu_control_window_sec), sample_interval_sec=float(cpu_sample_interval_sec))
    nxt = choose_next_threads_sustained(
        current_threads=int(runtime_threads),
        max_threads=int(iter_threads),
        min_threads=int(ramp_min),
        cpu_window_avg_pct=stats.avg_pct,
        cpu_window_max_pct=stats.max_pct,
        cpu_hot_threshold_pct=float(cpu_hot_threshold_pct),
        cpu_cool_threshold_pct=float(cpu_cool_threshold_pct),
        up_step=int(cpu_ramp_up_step),
        down_step=int(cpu_ramp_down_step),
    )
    dbg = {
        "mode": "window",
        "window_sec": float(cpu_control_window_sec),
        "sample_interval_sec": float(cpu_sample_interval_sec),
        "avg_pct": stats.avg_pct,
        "max_pct": stats.max_pct,
        "min_pct": stats.min_pct,
        "samples": int(stats.samples),
    }
    return int(nxt), stats.avg_pct, dbg


def _sig(c: dict) -> str:
    parts = [
        str(c.get("horizon_bars")),
        str(c.get("p_enter_long")),
        str(c.get("p_enter_short")),
        str(c.get("min_expected_move_pct")),
        str(c.get("trend_filter", "none")),
        str(c.get("min_abs_ema_gap", 0.0)),
    ]
    params = c.get("calibration_params")
    if isinstance(params, dict) and params:
        parts.append(json.dumps(params, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
    return "|".join(parts)


def _default_hypothesis_profile(signal_mode: str) -> str:
    sm = str(signal_mode or "").strip().lower()
    if sm == "short_only":
        return "trend_filters_short_style_1m"
    if sm == "both":
        return "trend_filters_both_style_1m"
    return "trend_filters_long_style_1m"


def _build_hypothesis_plan(args: argparse.Namespace) -> tuple[list[dict], dict]:
    def _default_long_style() -> list[dict[str, Any]]:
        return [
            {"trend_filter": "none", "min_abs_ema_gap": 0.0},
            {"trend_filter": "ema_gap_sign", "min_abs_ema_gap": 0.0},
            {"trend_filter": "ema_gap_sign", "min_abs_ema_gap": 0.02},
            {"trend_filter": "ema_cross_20_50", "min_abs_ema_gap": 0.0},
            {"trend_filter": "ema_cross_20_200", "min_abs_ema_gap": 0.0},
            {"trend_filter": "ema_stack_bull", "min_abs_ema_gap": 0.0},
            {"trend_filter": "channel_breakout_50", "min_abs_ema_gap": 0.0},
            {"trend_filter": "adx_trend_18", "min_abs_ema_gap": 0.0},
        ]

    def _default_short_style() -> list[dict[str, Any]]:
        return [
            {"trend_filter": "none", "min_abs_ema_gap": 0.0},
            {"trend_filter": "ema_gap_sign", "min_abs_ema_gap": 0.0},
            {"trend_filter": "ema_gap_sign", "min_abs_ema_gap": 0.02},
            {"trend_filter": "ema_cross_20_50", "min_abs_ema_gap": 0.0},
            {"trend_filter": "ema_cross_20_200", "min_abs_ema_gap": 0.0},
            {"trend_filter": "channel_breakout_50", "min_abs_ema_gap": 0.0},
            {"trend_filter": "adx_trend_18", "min_abs_ema_gap": 0.0},
        ]

    def _default_both_style() -> list[dict[str, Any]]:
        return _default_long_style()

    def _load_profile_from_features_cfg(profile: str) -> tuple[list[dict[str, Any]] | None, str | None]:
        cfg_raw = str(getattr(args, "features_config", "") or "").strip()
        if not cfg_raw or not profile:
            return None, None
        cfg_path = Path(cfg_raw)
        if not cfg_path.is_absolute():
            cfg_path = Path(__file__).resolve().parents[2] / cfg_path
        if not cfg_path.exists():
            return None, str(cfg_path)
        try:
            import yaml  # type: ignore

            cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
        except Exception:
            return None, str(cfg_path)
        raw = (((cfg.get("hypotheses") or {}).get(profile)) or [])
        out: list[dict[str, Any]] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            tf = str(item.get("trend_filter", "")).strip()
            if not tf:
                continue
            out.append(
                {
                    "trend_filter": tf,
                    "min_abs_ema_gap": float(item.get("min_abs_ema_gap", 0.0)),
                }
            )
        return out or None, str(cfg_path)

    def _default_for_signal_mode() -> list[dict[str, Any]]:
        sm = str(getattr(args, "signal_mode", "both") or "both").strip().lower()
        if sm == "short_only":
            return _default_short_style()
        if sm == "both":
            return _default_both_style()
        return _default_long_style()

    # If explicit grid is provided, use it as source of truth.
    grid_raw = str(getattr(args, "trend_hypothesis_grid", "") or "").strip()
    if grid_raw:
        out: list[dict] = []
        for tok in grid_raw.split(","):
            tf = tok.strip()
            if not tf:
                continue
            out.append({"trend_filter": tf, "min_abs_ema_gap": float(args.min_abs_ema_gap)})
        plan = out or [{"trend_filter": str(args.trend_filter), "min_abs_ema_gap": float(args.min_abs_ema_gap)}]
        return plan, {"source": "cli_grid", "profile": None, "config_path": None}

    # Policy: hypothesis profiles from features config are ON by default.
    # Can be disabled explicitly via --disable-hypothesis-profile.
    disable_profile = bool(getattr(args, "disable_hypothesis_profile", False))
    use_profile = not disable_profile
    if (not disable_profile) and bool(
        getattr(args, "use_hypothesis_profile", False) or getattr(args, "long_style_1m", False)
    ):
        use_profile = True
    if use_profile:
        profile_raw = str(getattr(args, "trend_hypothesis_profile", "") or "").strip().lower()
        profile = _default_hypothesis_profile(str(getattr(args, "signal_mode", "both"))) if profile_raw in {"", "auto"} else profile_raw
        from_cfg, cfg_path = _load_profile_from_features_cfg(profile)
        if from_cfg:
            return from_cfg, {"source": "features_config", "profile": profile, "config_path": cfg_path}
        return _default_for_signal_mode(), {"source": "default_fallback", "profile": profile, "config_path": cfg_path}

    return (
        [{"trend_filter": str(args.trend_filter), "min_abs_ema_gap": float(args.min_abs_ema_gap)}],
        {"source": "single_filter", "profile": None, "config_path": None},
    )


def _dedupe_hypothesis_plan(plan: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, float]] = set()
    for item in plan:
        if not isinstance(item, dict):
            continue
        tf = str(item.get("trend_filter", "")).strip()
        if not tf:
            continue
        gap = float(item.get("min_abs_ema_gap", 0.0))
        key = (tf.lower(), round(gap, 8))
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def _resolve_effective_repeats(
    *,
    requested_repeats: int,
    hypothesis_plan_len: int,
    enforce_requested_equals_effective: bool,
) -> tuple[int, bool]:
    requested = max(1, int(requested_repeats))
    plan_len = max(1, int(hypothesis_plan_len))
    effective = max(requested, plan_len)
    mismatch = effective != requested
    if enforce_requested_equals_effective and mismatch:
        raise ValueError(
            "repeats_effective_mismatch:"
            f" repeats_requested={requested}"
            f" repeats_effective={effective}"
            " (disable profile/backlog expansion or increase --repeats)."
        )
    return int(effective), bool(mismatch)


def _candidate_backtest(candidate: dict) -> dict:
    if not isinstance(candidate, dict):
        return {}
    bt = candidate.get("backtest", {})
    return bt if isinstance(bt, dict) else {}


def _candidate_min_move_unreachable(candidate: dict) -> bool:
    if not isinstance(candidate, dict):
        return False
    if bool(candidate.get("min_move_unreachable", False)):
        return True
    if str(candidate.get("runtime_diagnostic_status", "")) == MIN_MOVE_UNREACHABLE:
        return True
    fail_keys = candidate.get("fail_keys") or []
    if isinstance(fail_keys, list) and MIN_MOVE_UNREACHABLE in {str(x) for x in fail_keys}:
        return True
    return is_min_move_unreachable(_candidate_backtest(candidate))


def _prefer_reachable_candidates(candidates: list[dict]) -> list[dict]:
    reachable = [c for c in candidates if not _candidate_min_move_unreachable(c)]
    return reachable if reachable else list(candidates)


def _has_calibration_params(candidate: dict) -> bool:
    if not isinstance(candidate, dict):
        return False
    params = candidate.get("calibration_params")
    return isinstance(params, dict) and bool(params)


def _candidate_pool_from_search_report(search_report: dict) -> list[dict]:
    if not isinstance(search_report, dict):
        return []
    lite = search_report.get("all_candidates_lite", [])
    full = search_report.get("top_candidates", [])
    lite_candidates = [c for c in lite if isinstance(c, dict)] if isinstance(lite, list) else []
    full_candidates = [c for c in full if isinstance(c, dict)] if isinstance(full, list) else []
    # `all_candidates_lite` intentionally omits heavy candidate metadata. For
    # calibration runs we must preserve params into the final train/OOS replay.
    if full_candidates and any(_has_calibration_params(c) for c in full_candidates):
        return full_candidates
    if lite_candidates:
        return lite_candidates
    return full_candidates


def _candidate_rank(candidate: dict) -> tuple[float, int, float, float]:
    bt = _candidate_backtest(candidate)
    net_ret = float(bt.get("net_return_pct", -1e18))
    trades = int(bt.get("trades", 0))
    score = float(candidate.get("score", -1e18))
    max_dd = float(bt.get("max_drawdown_pct", 0.0))
    # Rank: tradeful first, then return, then score, then lower drawdown.
    return (1.0 if trades > 0 else 0.0, net_ret, score, -abs(max_dd))


def _pick_candidate(
    *,
    candidates: list[dict],
    rejected: set[str],
    goal_net_return_pct: float,
    strict_goal_only: bool,
    min_candidate_trades: int,
) -> tuple[dict | None, str]:
    min_trades = max(0, int(min_candidate_trades))
    available = [c for c in candidates if _sig(c) not in rejected]
    if not available:
        # If memory rejected every signature, do not hard-stop non-strict loops:
        # reuse the best candidate from current search result and continue.
        if (not strict_goal_only) and candidates:
            reuse_pool = _prefer_reachable_candidates(candidates)
            tradeful_reuse = [c for c in reuse_pool if int(_candidate_backtest(c).get("trades", 0)) >= min_trades]
            if tradeful_reuse:
                return max(tradeful_reuse, key=_candidate_rank), "best_tradeful_reuse_all_rejected"
            return max(reuse_pool, key=_candidate_rank), "best_available_reuse_all_rejected"
        return None, "all_rejected"

    available = _prefer_reachable_candidates(available)
    goal_hits = [
        c
        for c in available
        if float(_candidate_backtest(c).get("net_return_pct", -1e18)) >= float(goal_net_return_pct)
    ]
    if goal_hits:
        goal_hits_tradeful = [c for c in goal_hits if int(_candidate_backtest(c).get("trades", 0)) >= min_trades]
        if goal_hits_tradeful:
            return max(goal_hits_tradeful, key=_candidate_rank), "best_goal_candidate"
        if strict_goal_only:
            return max(goal_hits, key=_candidate_rank), "best_goal_candidate_low_trade"

    if strict_goal_only:
        return None, "no_goal_candidate"

    tradeful = [c for c in available if int(_candidate_backtest(c).get("trades", 0)) >= min_trades]
    if not tradeful and min_trades > 1:
        tradeful = [c for c in available if int(_candidate_backtest(c).get("trades", 0)) > 0]
    if tradeful:
        return max(tradeful, key=_candidate_rank), "best_tradeful_fallback"
    return max(available, key=_candidate_rank), "best_available_fallback"


def _best_step_key(step: dict) -> tuple[int, float]:
    trades = int(step.get("oos_trades", 0))
    ret = float(step.get("oos_net_return_pct", -1e18))
    return (1 if trades > 0 else 0, ret)


def _memory_key(
    *,
    symbol: str,
    timeframe: str,
    train_start: str,
    train_end: str,
    test_day: str,
    test_end_day: str,
    goal_net_return_pct: float,
    signal_mode: str,
) -> str:
    return (
        f"{symbol}|{timeframe}|train={train_start}:{train_end}|"
        f"test={test_day}:{test_end_day}|goal={goal_net_return_pct:.6f}|mode={signal_mode}"
    )


def _sanitize_slug(value: str) -> str:
    raw = str(value or "").strip().lower()
    if not raw:
        return "default"
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789_-")
    out = "".join(ch if ch in allowed else "_" for ch in raw)
    while "__" in out:
        out = out.replace("__", "_")
    out = out.strip("_")
    return out or "default"


def _resolve_contour_id(*, signal_mode: str, contour_id: str) -> str:
    cid = str(contour_id or "").strip().lower()
    if cid in {"", "auto"}:
        cid = str(signal_mode or "both").strip().lower()
    return _sanitize_slug(cid)


def _resolve_engine_contour(
    *,
    signal_mode: str,
    contour_id: str,
    search_engine: str,
) -> tuple[str, str, str | None]:
    def _has_mode_token(text: str, token: str) -> bool:
        import re

        pat = rf"(^|[^a-z0-9]){re.escape(token)}($|[^a-z0-9])"
        return re.search(pat, str(text or "")) is not None

    engine = str(search_engine or "grid").strip().lower()
    mode = str(signal_mode or "both").strip().lower()
    resolved = _resolve_contour_id(signal_mode=mode, contour_id=contour_id)
    note: str | None = None
    if engine == "optuna":
        if mode == "both":
            raise ValueError("optuna search_engine requires signal_mode long_only or short_only")
        # Keep unique per-run contours (e.g. process-pool worker tags) as long as
        # they explicitly contain the correct mode token.
        if not _has_mode_token(resolved, mode):
            note = f"optuna_contour_forced:{resolved}->{mode}"
            resolved = mode
    return engine, resolved, note


def _build_optuna_overrides_payload(
    *,
    search_engine: str,
    n_trials_override: int,
    timeout_sec_override: int,
) -> dict[str, int | None]:
    if str(search_engine).strip().lower() != "optuna":
        return {"n_trials_override": None, "timeout_sec_override": None}
    n_trials = int(n_trials_override) if int(n_trials_override) > 0 else None
    timeout_sec = int(timeout_sec_override) if int(timeout_sec_override) > 0 else None
    return {"n_trials_override": n_trials, "timeout_sec_override": timeout_sec}


def _fmt_pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:+.4f}%"


def _fmt_hms(seconds: float | None) -> str:
    if seconds is None:
        return "n/a"
    sec = max(0, int(round(float(seconds))))
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def _append_progress(path: Path, line: str) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(line.rstrip() + "\n")


def _print_progress(
    *,
    progress_path: Path,
    step: dict,
    completed: int,
    total: int,
    run_started_perf: float,
    best_oos: dict | None,
) -> None:
    elapsed = time.perf_counter() - run_started_perf
    avg_per_repeat = (elapsed / completed) if completed > 0 else None
    remaining = (avg_per_repeat * max(0, total - completed)) if avg_per_repeat is not None else None
    step_oos = step.get("oos_net_return_pct")
    try:
        step_oos = float(step_oos) if step_oos is not None else None
    except Exception:
        step_oos = None
    step_trades = int(step.get("oos_trades", 0) or 0)
    best_rep = int(best_oos.get("repeat", 0)) if isinstance(best_oos, dict) else 0
    best_ret = None
    if isinstance(best_oos, dict):
        try:
            best_ret = float(best_oos.get("oos_net_return_pct"))
        except Exception:
            best_ret = None

    line = (
        f"{completed:02d}/{total:02d} | repeat={int(step.get('repeat', completed)):02d} "
        f"| status={str(step.get('status', 'unknown')):<18} "
        f"| oos={_fmt_pct(step_oos):>10} "
        f"| trades={step_trades:4d} "
        f"| best={_fmt_pct(best_ret):>10} (rep {best_rep:02d}) "
        f"| elapsed={_fmt_hms(elapsed)} "
        f"| eta={_fmt_hms(remaining)}"
    )
    print(line)
    _append_progress(progress_path, line)


def _load_rejected(mem_path: Path, key: str) -> set[str]:
    if not mem_path.exists():
        return set()
    try:
        old = json.loads(mem_path.read_text(encoding="utf-8"))
    except Exception:
        return set()

    # Legacy support: flat file with top-level rejected_signatures.
    if isinstance(old, dict) and isinstance(old.get("rejected_signatures"), list):
        return {str(x) for x in old.get("rejected_signatures", [])}

    sections = old.get("sections", {}) if isinstance(old, dict) else {}
    section = sections.get(key, {}) if isinstance(sections, dict) else {}
    values = section.get("rejected_signatures", []) if isinstance(section, dict) else []
    if not isinstance(values, list):
        return set()
    return {str(x) for x in values}


def _save_rejected(mem_path: Path, key: str, rejected: set[str], *, symbol: str, timeframe: str) -> None:
    payload: dict
    if mem_path.exists():
        try:
            payload = json.loads(mem_path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                payload = {}
        except Exception:
            payload = {}
    else:
        payload = {}
    sections = payload.get("sections", {})
    if not isinstance(sections, dict):
        sections = {}
    sections[key] = {
        "symbol": symbol,
        "timeframe": timeframe,
        "rejected_signatures": sorted(rejected),
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    payload = {
        "version": 2,
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "sections": sections,
    }
    mem_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _detect_filter_invariant_warning(history: list[dict]) -> dict:
    rows: list[dict[str, Any]] = []
    for step in history:
        if not isinstance(step, dict):
            continue
        trend = str(step.get("trend_filter", "")).strip()
        report_path = str(step.get("search_report_path", "")).strip()
        if not trend or not report_path:
            continue
        try:
            rep = json.loads(Path(report_path).read_text(encoding="utf-8"))
            best = rep.get("best_candidate") or {}
            bt = best.get("backtest") or {}
            fail_keys = tuple(sorted(str(x) for x in (best.get("fail_keys") or [])))
            diag = bt.get("trend_filter_diagnostics") or {}
            sig = (
                round(float(bt.get("net_return_pct", 0.0)), 6),
                int(bt.get("trades", 0)),
                round(float(bt.get("max_drawdown_pct", 0.0)), 6),
                round(float(best.get("score", 0.0)), 6),
                fail_keys,
                int(diag.get("signal_count_after_filter", -1)),
                int(diag.get("eligible_bars", -1)),
            )
            rows.append({"trend_filter": trend, "signature": sig, "search_report_path": report_path})
        except Exception:
            continue
    trends = sorted({str(x.get("trend_filter", "")) for x in rows if str(x.get("trend_filter", ""))})
    unique_signatures = {x.get("signature") for x in rows}
    invariant = len(trends) >= 2 and len(unique_signatures) == 1 and len(rows) >= 2
    out = {
        "filter_invariant_warning": bool(invariant),
        "compared_trend_filters": trends,
        "rows_compared": int(len(rows)),
    }
    if invariant and rows:
        out["invariant_signature"] = list(rows[0].get("signature") or [])
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Adaptive auto-train loop: train window -> search -> train -> OOS day, with repeats.")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--layer", default="raw", choices=["raw", "core"], help="Data layer for search/train/OOS input.")
    parser.add_argument("--train-start", required=True, help="YYYY-MM-DD")
    parser.add_argument("--train-end", required=True, help="YYYY-MM-DD")
    parser.add_argument("--test-day", required=True, help="YYYY-MM-DD")
    parser.add_argument("--test-end-day", default=None, help="Optional end day YYYY-MM-DD for multi-day OOS")
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--goal-net-return-pct", type=float, default=100.0)
    parser.add_argument("--min-train-rows", type=int, default=4000)
    parser.add_argument("--n-folds", type=int, default=3)
    parser.add_argument("--fee-bps", type=float, default=10.0)
    parser.add_argument("--slippage-bps", type=float, default=5.0)
    parser.add_argument("--stop-loss-pct", type=float, default=0.008)
    parser.add_argument("--take-profit-pct", type=float, default=0.012)
    parser.add_argument("--min-tp-reach-prob", type=float, default=0.58)
    parser.add_argument("--tp-min-factor", type=float, default=0.7)
    parser.add_argument("--cooldown-bars", type=int, default=0)
    parser.add_argument(
        "--trend-filter",
        default="none",
        choices=[
            "none",
            "ema_gap_sign",
            "ema_cross_20_50",
            "ema_cross_20_200",
            "ema_stack_bull",
            "channel_breakout_50",
            "adx_trend_18",
            "fib_retrace_0382_0618_trend_resume",
            "fib_extension_targets",
            "swing_hl_hh_long",
            "swing_lh_ll_short",
            "bos_continuation_confirm",
            "min_max_range_revert",
            "max_low_pullback_long",
            "hvn_lvn_density_reaction",
            "volume_profile_poc_vah_val_retest",
            "value_area_rotation_vs_breakout",
            "wedge_breakout_plus_profile_acceptance",
            "orderbook_imbalance_l1_l50",
            "spread_pressure_and_delta_absorption",
        ],
    )
    parser.add_argument("--min-abs-ema-gap", type=float, default=0.0)
    parser.add_argument(
        "--long-style-1m",
        action="store_true",
        help="Enable 1m long-style hypothesis ladder (multiple trend hypotheses per repeats).",
    )
    parser.add_argument(
        "--trend-hypothesis-grid",
        default="",
        help="Optional CSV override for trend hypotheses sequence by repeat.",
    )
    parser.add_argument(
        "--features-config",
        default="configs/features_block.yaml",
        help="Features/hypotheses config path used as source-of-truth for long-style hypothesis plan.",
    )
    parser.add_argument(
        "--trend-hypothesis-profile",
        default="auto",
        help="Profile key inside features config hypotheses.* for long-style plan.",
    )
    parser.add_argument(
        "--use-hypothesis-profile",
        action="store_true",
        help="Use hypothesis profile from features config for any signal_mode (long/short/both).",
    )
    parser.add_argument(
        "--disable-hypothesis-profile",
        action="store_true",
        help="Disable default profile-based hypothesis plan and use single --trend-filter mode.",
    )
    parser.add_argument(
        "--disable-backlog-active-append",
        action="store_true",
        help="Do not append active/validated backlog hypotheses to runtime hypothesis plan.",
    )
    parser.add_argument(
        "--enforce-repeats-effective-match",
        action="store_true",
        help="Fail fast when repeats_effective differs from repeats_requested.",
    )
    parser.add_argument("--horizons-grid", default="1,2,3,4,6,8,12,20")
    parser.add_argument("--p-long-grid", default="0.52,0.54,0.56,0.58,0.60,0.62,0.65")
    parser.add_argument("--p-short-grid", default="0.48,0.46,0.44,0.42,0.40,0.38,0.35")
    parser.add_argument("--min-expected-move-grid", default="0.0,0.001,0.002,0.003")
    parser.add_argument("--notional-usd-grid", default="")
    parser.add_argument(
        "--min-candidate-trades",
        type=int,
        default=1,
        help="Minimum trades in search candidate to prefer during adaptive selection.",
    )
    parser.add_argument(
        "--candidate-replay-attempts",
        type=int,
        default=8,
        help="How many current search candidates to try before marking the repeat failed.",
    )
    parser.add_argument("--notional-usd", type=float, default=10.0)
    parser.add_argument("--leverage", type=float, default=10.0)
    parser.add_argument("--signal-mode", default="both", choices=["both", "long_only", "short_only"])
    parser.add_argument(
        "--contour-id",
        default="auto",
        help="Logical contour namespace for artifacts/memory isolation (auto => signal_mode).",
    )
    parser.add_argument("--execution-mode", default="exchange_like", choices=["research", "exchange_like"])
    parser.add_argument("--order-type", default="market", choices=["market", "limit"])
    parser.add_argument("--limit-offset-bps", type=float, default=2.0)
    parser.add_argument("--disable-timeout-exit", action="store_true", help="Disable time-based trade exit in search/train/OOS backtests.")
    parser.add_argument("--cpu-max-pct", type=float, default=85.0)
    parser.add_argument("--max-threads", type=int, default=6)
    parser.add_argument("--search-workers", type=int, default=0, help="Workers for search_gate_candidate (0=auto from runtime threads)")
    parser.add_argument("--process-workers-total", type=int, default=1)
    parser.add_argument(
        "--search-engine",
        default="grid",
        choices=["grid", "optuna"],
        help="Search engine backend: grid (legacy) or optuna (isolated contour only).",
    )
    parser.add_argument(
        "--optuna-stage",
        default="auto",
        choices=["auto", "A", "B", "C"],
        help="Optuna stage profile: auto infers A/B/C, or force explicit stage.",
    )
    parser.add_argument("--optuna-n-trials-override", type=int, default=0, help="Optional positive override for Optuna n_trials.")
    parser.add_argument("--optuna-timeout-sec-override", type=int, default=0, help="Optional positive override for Optuna timeout_sec.")
    parser.add_argument(
        "--optuna-shared-study-id",
        default="",
        help="Optional shared Optuna study namespace for multi-process workers.",
    )
    parser.add_argument(
        "--optuna-ml-signal-backend",
        default="off",
        choices=["on", "off"],
        help="Optuna objective signal backend: off=rule-only calibration mode, on=legacy ML-probability mode.",
    )
    parser.add_argument(
        "--calibration-grid-preset",
        default="auto",
        choices=["auto", "wide", "medium", "narrow"],
        help="Optuna calibration grid preset passed to the isolated Optuna search contour.",
    )
    parser.add_argument(
        "--force-profile-edge-coverage",
        default="auto",
        choices=["auto", "on", "off"],
        help="Optuna profile edge coverage mode passed to the isolated Optuna search contour.",
    )
    parser.add_argument("--speed-profile", default="custom", choices=["custom", "turbo", "balanced", "full"])
    parser.add_argument("--cpu-ramp-disable", action="store_true", help="Disable smooth CPU-aware thread ramp (enabled by default).")
    parser.add_argument("--cpu-ramp-min-threads", type=int, default=4)
    parser.add_argument("--cpu-ramp-up-step", type=int, default=1)
    parser.add_argument("--cpu-ramp-down-step", type=int, default=2)
    parser.add_argument("--cpu-control-window-sec", type=float, default=10.0, help="CPU averaging window to avoid reacting to 1s spikes.")
    parser.add_argument("--cpu-sample-interval-sec", type=float, default=1.0)
    parser.add_argument("--cpu-budget-check-interval-sec", type=float, default=2.0, help="Pre-run CPU budget check interval.")
    parser.add_argument("--cpu-budget-max-wait-sec", type=float, default=120.0, help="Max pre-run wait for CPU budget.")
    parser.add_argument("--cpu-budget-consecutive-ok", type=int, default=1, help="Required consecutive CPU checks below budget before run.")
    parser.add_argument("--cpu-hot-threshold-pct", type=float, default=90.0, help="Sustained hot threshold for downshift.")
    parser.add_argument("--cpu-cool-threshold-pct", type=float, default=45.0, help="Sustained cool threshold for upshift.")
    parser.add_argument(
        "--thread-ramp",
        default="",
        help="Optional CSV ramp for threads by repeat, e.g. 6,8,10,12",
    )
    parser.add_argument("--strict-goal-only", action="store_true", default=True, help="Train only candidates with net_return_pct >= goal (default enabled).")
    parser.add_argument("--allow-subgoal-candidates", action="store_true", help="Disable strict goal mode (fallback to best available candidate).")
    parser.add_argument(
        "--stop-on-goal-pass",
        action="store_true",
        help="Legacy flag (ignored by policy): loop always continues to full repeats.",
    )
    parser.add_argument("--temporary-unlock-readiness", action="store_true", help="Explicitly and temporarily set project_ready=true for this run, then restore original readiness.")
    parser.add_argument("--unlock-reason", default="temporary adaptive run", help="Reason used when --temporary-unlock-readiness is enabled.")
    parser.add_argument(
        "--window-policy",
        default="fixed_1d",
        choices=["fixed_1d", "multiday"],
        help="Date-window policy: fixed_1d enforces 1d train + 1d closed test; multiday allows contiguous windows.",
    )
    parser.add_argument("--preflight-policy", default="configs/preflight_policy.yaml")
    args = parser.parse_args()
    _apply_speed_profile(args)
    project_root = Path(__file__).resolve().parents[2]
    preflight_resolved = resolve_preflight_runtime_args(
        project_root,
        policy_path=str(args.preflight_policy),
        min_train_rows=int(args.min_train_rows),
        n_folds=int(args.n_folds),
        horizons_grid=str(args.horizons_grid),
        legacy_min_train_rows=4000,
        legacy_n_folds=3,
        legacy_horizons_grid="1,2,3,4,6,8,12,20",
    )
    args.min_train_rows = int(preflight_resolved["min_train_rows"])
    args.n_folds = int(preflight_resolved["n_folds"])
    args.horizons_grid = str(preflight_resolved["horizons_grid"])
    runtime_data_layer = str(args.layer)
    preflight_raw_layer = runtime_data_layer
    # Hard policy: do not truncate search on first goal-pass.
    forced_stop_on_goal_pass_ignored = bool(args.stop_on_goal_pass)
    args.stop_on_goal_pass = False
    if bool(args.long_style_1m):
        if str(args.timeframe) != "1m":
            print(json.dumps({"error": "--long-style-1m requires --timeframe 1m"}, ensure_ascii=False))
            return 2
        if not bool(args.use_hypothesis_profile):
            args.signal_mode = "long_only"

    try:
        search_engine, contour_id, engine_contour_note = _resolve_engine_contour(
            signal_mode=str(args.signal_mode),
            contour_id=str(args.contour_id),
            search_engine=str(getattr(args, "search_engine", "grid")),
        )
    except Exception as e:
        print(
            json.dumps(
                {
                    "error": str(e),
                    "status": "invalid_search_engine_signal_mode",
                },
                ensure_ascii=False,
            )
        )
        return 2

    optuna_overrides = _build_optuna_overrides_payload(
        search_engine=str(search_engine),
        n_trials_override=int(args.optuna_n_trials_override),
        timeout_sec_override=int(args.optuna_timeout_sec_override),
    )

    stale_unlock_recovery = _restore_stale_temporary_unlock(project_root)
    try:
        if str(args.window_policy) == "fixed_1d":
            daily_window = _validate_fixed_daily_windows(
                train_start=str(args.train_start),
                train_end=str(args.train_end),
                test_day=str(args.test_day),
                test_end_day=(str(args.test_end_day) if args.test_end_day else None),
            )
        else:
            daily_window = _validate_multiday_windows(
                train_start=str(args.train_start),
                train_end=str(args.train_end),
                test_day=str(args.test_day),
                test_end_day=(str(args.test_end_day) if args.test_end_day else None),
            )
    except Exception as e:
        print(json.dumps({"error": str(e), "status": "invalid_daily_window"}, ensure_ascii=False))
        return 2
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = project_root / "reports" / "adaptive" / contour_id
    out_dir.mkdir(parents=True, exist_ok=True)
    mem_path = out_dir / "negative_setup_memory.json"
    summary_path = out_dir / f"adaptive_loop_{args.symbol}_{args.timeframe}_{args.test_day}_{ts}.json"
    audit_path = out_dir / f"adaptive_fix_audit_{ts}.json"
    progress_path = out_dir / f"adaptive_progress_{args.symbol}_{args.timeframe}_{args.test_day}_{ts}.log"
    strict_goal_only = bool(args.strict_goal_only and (not args.allow_subgoal_candidates))
    hypothesis_plan, hypothesis_meta = _build_hypothesis_plan(args)
    backlog_registry = load_backlog_registry(
        project_root=project_root,
        features_config=str(getattr(args, "features_config", "configs/features_block.yaml")),
        run_signal_mode=str(args.signal_mode),
    )
    active_backlog = list(backlog_registry.get("active_items", [])) if isinstance(backlog_registry, dict) else []
    if active_backlog and not bool(args.disable_backlog_active_append):
        backlog_plan: list[dict[str, Any]] = []
        for item in active_backlog:
            nm = str(item.get("name", "")).strip()
            if not nm:
                continue
            backlog_plan.append({"trend_filter": nm, "min_abs_ema_gap": 0.0, "from_backlog": True})
        if backlog_plan:
            hypothesis_plan = backlog_plan + hypothesis_plan
        src = str(hypothesis_meta.get("source", "") or "").strip().lower()
        if src in {"features_config", "default_fallback", "single_filter", "cli_grid"}:
            hypothesis_meta["source"] = f"{src}_plus_backlog_active"
    hypothesis_plan = _dedupe_hypothesis_plan(hypothesis_plan)
    # Always iterate at least one full pass over resolved hypothesis plan,
    # even when repeats=1, so short/long profile scans do not stop at first filter.
    requested_repeats = max(1, int(args.repeats))
    try:
        effective_repeats, repeats_effective_mismatch = _resolve_effective_repeats(
            requested_repeats=requested_repeats,
            hypothesis_plan_len=len(hypothesis_plan),
            enforce_requested_equals_effective=bool(args.enforce_repeats_effective_match),
        )
    except Exception as e:
        print(
            json.dumps(
                {
                    "error": str(e),
                    "status": "invalid_repeats_effective_policy",
                    "repeats_requested": int(args.repeats),
                    "hypothesis_plan_len": int(len(hypothesis_plan)),
                },
                ensure_ascii=False,
            )
        )
        return 2
    mem_key = _memory_key(
        symbol=args.symbol,
        timeframe=args.timeframe,
        train_start=args.train_start,
        train_end=args.train_end,
        test_day=args.test_day,
        test_end_day=(str(args.test_end_day) if args.test_end_day else str(args.test_day)),
        goal_net_return_pct=float(args.goal_net_return_pct),
        signal_mode=f"{args.signal_mode}|contour={contour_id}",
    )

    rejected: set[str] = _load_rejected(mem_path, mem_key)
    ramp_threads: list[int] = []
    if str(args.thread_ramp).strip():
        for tok in str(args.thread_ramp).split(","):
            t = tok.strip()
            if not t:
                continue
            try:
                ramp_threads.append(max(1, int(t)))
            except Exception:
                continue

    history: list[dict] = []
    success = False
    best_oos = None
    no_goal_candidate_iterations = 0

    original_readiness = load_readiness(project_root)
    readiness_restored = True
    unlock_applied = False
    blocked_checks = {}

    if args.temporary_unlock_readiness:
        _write_unlock_marker(project_root, original_readiness=original_readiness)
        temp = dict(original_readiness)
        temp["project_ready"] = True
        temp["reason"] = str(args.unlock_reason)
        temp["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
        save_readiness(project_root, temp)
        unlock_applied = True

    check_search = check_action_allowed(project_root, action="search_gate_candidate")
    check_train = check_action_allowed(project_root, action="pipeline_train_eval")
    blocked_checks = {"search_gate_candidate": check_search, "pipeline_train_eval": check_train}
    if (not check_search["allowed"]) or (not check_train["allowed"]):
        summary = {
            "run_utc": ts,
            "symbol": args.symbol,
            "timeframe": args.timeframe,
            "search_engine": str(search_engine),
            "optuna_stage": (str(args.optuna_stage) if str(search_engine) == "optuna" else None),
            "optuna_overrides": dict(optuna_overrides),
            "engine_contour_note": engine_contour_note,
            "train_window": {"start": args.train_start, "end": args.train_end},
            "test_day": args.test_day,
            "goal_net_return_pct": float(args.goal_net_return_pct),
            "repeats_requested": int(args.repeats),
            "repeats_effective": int(effective_repeats),
            "repeats_effective_mismatch": bool(repeats_effective_mismatch),
            "strict_goal_only": strict_goal_only,
            "status": "blocked_readiness",
            "readiness_checks": blocked_checks,
            "memory_key": mem_key,
            "contour_id": contour_id,
            "negative_memory_path": str(mem_path),
            "backlog_registry": backlog_registry,
            "history": history,
            "success": False,
        }
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        if unlock_applied:
            save_readiness(project_root, original_readiness)
            _clear_unlock_marker(project_root)
        readiness_after = load_readiness(project_root)
        readiness_restored = readiness_after == original_readiness
        audit = {
            "run_utc": ts,
            "summary_path": str(summary_path),
            "status": "blocked_readiness",
            "f1_no_auto_unlock_default": not bool(args.temporary_unlock_readiness),
            "f2_strict_goal_enabled": strict_goal_only,
            "f3_readiness_restored": readiness_restored,
            "f4_json_parsing_mode": "robust_scan_from_end",
            "f5_memory_key": mem_key,
            "contour_id": contour_id,
            "memory_path": str(mem_path),
        }
        audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"summary_path": str(summary_path), "audit_path": str(audit_path), "success": False}, ensure_ascii=False))
        return 2

    preflight_once = _run_preflight_window_once(
        project_root,
        symbol=str(args.symbol),
        timeframe=str(args.timeframe),
        train_start=str(args.train_start),
        train_end=str(args.train_end),
        test_day=str(args.test_day),
        test_end_day=(str(args.test_end_day) if args.test_end_day else str(args.test_day)),
        min_train_rows=int(args.min_train_rows),
        n_folds=int(args.n_folds),
        horizons_grid=str(args.horizons_grid),
        layer=str(preflight_raw_layer),
    )
    if int(preflight_once.get("returncode", 1)) != 0:
        summary = {
            "run_utc": ts,
            "symbol": args.symbol,
            "timeframe": args.timeframe,
            "search_engine": str(search_engine),
            "optuna_stage": (str(args.optuna_stage) if str(search_engine) == "optuna" else None),
            "optuna_overrides": dict(optuna_overrides),
            "engine_contour_note": engine_contour_note,
            "train_window": {"start": args.train_start, "end": args.train_end},
            "test_day": args.test_day,
            "test_end_day": str(args.test_end_day) if args.test_end_day else str(args.test_day),
            "data_layer": runtime_data_layer,
            "goal_net_return_pct": float(args.goal_net_return_pct),
            "repeats_requested": int(args.repeats),
            "strict_goal_only": strict_goal_only,
            "status": "blocked_preflight_window",
            "readiness_checks": blocked_checks,
            "preflight_window": preflight_once,
            "memory_key": mem_key,
            "contour_id": contour_id,
            "negative_memory_path": str(mem_path),
            "backlog_registry": backlog_registry,
            "history": history,
            "success": False,
        }
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        if unlock_applied:
            save_readiness(project_root, original_readiness)
            _clear_unlock_marker(project_root)
        readiness_after = load_readiness(project_root)
        readiness_restored = readiness_after == original_readiness
        audit = {
            "run_utc": ts,
            "summary_path": str(summary_path),
            "status": "blocked_preflight_window",
            "f1_no_auto_unlock_default": not bool(args.temporary_unlock_readiness),
            "f2_strict_goal_enabled": strict_goal_only,
            "f3_readiness_restored": readiness_restored,
            "f4_json_parsing_mode": "robust_scan_from_end",
            "f5_memory_key": mem_key,
            "contour_id": contour_id,
            "memory_path": str(mem_path),
        }
        audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"summary_path": str(summary_path), "audit_path": str(audit_path), "success": False}, ensure_ascii=False))
        return 2

    try:
        run_started_perf = time.perf_counter()
        header = (
            f"ADAPTIVE PROGRESS | run_utc={ts} | symbol={args.symbol} | tf={args.timeframe} "
            f"| repeats_req={requested_repeats} | repeats_eff={effective_repeats} "
            f"| mode={args.signal_mode} | goal={float(args.goal_net_return_pct):.4f}%"
        )
        print(header)
        _append_progress(progress_path, header)
        _append_progress(
            progress_path,
            "idx/total | repeat | status | oos_net_return_pct | trades | best_oos_pct (repeat) | elapsed | eta",
        )

        for i in range(1, effective_repeats + 1):
            step: dict = {"repeat": i}
            step["search_engine"] = search_engine
            step["engine_contour_note"] = engine_contour_note
            step["optuna_stage"] = (str(args.optuna_stage) if search_engine == "optuna" else None)
            step["optuna_ml_signal_backend"] = (str(args.optuna_ml_signal_backend) if search_engine == "optuna" else None)
            step["optuna_overrides"] = dict(optuna_overrides)
            hypo = hypothesis_plan[(i - 1) % len(hypothesis_plan)]
            if active_backlog:
                step["backlog_hypothesis_hint"] = str(active_backlog[(i - 1) % len(active_backlog)].get("name"))
            else:
                step["backlog_hypothesis_hint"] = None
            trend_filter_i = str(hypo.get("trend_filter", str(args.trend_filter)))
            min_abs_ema_gap_i = float(hypo.get("min_abs_ema_gap", float(args.min_abs_ema_gap)))
            step["trend_filter"] = trend_filter_i
            step["min_abs_ema_gap"] = min_abs_ema_gap_i
            iter_threads = int(args.max_threads)
            if ramp_threads:
                idx = min(i - 1, len(ramp_threads) - 1)
                iter_threads = int(ramp_threads[idx])
            step["max_threads_limit"] = int(iter_threads)
            cpu_ramp_enabled = not bool(args.cpu_ramp_disable)
            ramp_min = min(int(iter_threads), max(1, int(args.cpu_ramp_min_threads)))
            runtime_threads = int(ramp_min if cpu_ramp_enabled else iter_threads)
            step["cpu_ramp_enabled"] = cpu_ramp_enabled
            step["cpu_ramp_min_threads"] = int(ramp_min)
            step["cpu_ramp_up_step"] = int(args.cpu_ramp_up_step)
            step["cpu_ramp_down_step"] = int(args.cpu_ramp_down_step)

            runtime_threads, cpu_now, cpu_dbg = _next_threads(
                runtime_threads=runtime_threads,
                iter_threads=int(iter_threads),
                ramp_min=int(ramp_min),
                cpu_ramp_enabled=bool(cpu_ramp_enabled),
                cpu_max_pct=float(args.cpu_max_pct),
                cpu_ramp_up_step=int(args.cpu_ramp_up_step),
                cpu_ramp_down_step=int(args.cpu_ramp_down_step),
                cpu_control_window_sec=float(args.cpu_control_window_sec),
                cpu_sample_interval_sec=float(args.cpu_sample_interval_sec),
                cpu_hot_threshold_pct=float(args.cpu_hot_threshold_pct),
                cpu_cool_threshold_pct=float(args.cpu_cool_threshold_pct),
            )
            step["search_cpu_before_pct"] = cpu_now
            step["search_cpu_window"] = cpu_dbg
            step["search_threads"] = int(runtime_threads)
            search_workers = int(args.search_workers) if int(args.search_workers) > 0 else int(runtime_threads)
            step["search_workers"] = int(max(1, search_workers))
            search_module = "mlbotnav.search_gate_candidate" if search_engine == "grid" else "mlbotnav.optuna_search_candidate"
            search_cmd = [
                sys.executable,
                "-m",
                search_module,
                "--symbol",
                args.symbol,
                "--timeframe",
                args.timeframe,
                "--start-date",
                args.train_start,
                "--end-date",
                args.train_end,
                "--layer",
                runtime_data_layer,
                "--min-train-rows",
                str(int(args.min_train_rows)),
                "--n-folds",
                str(int(args.n_folds)),
                "--fee-bps",
                str(float(args.fee_bps)),
                "--slippage-bps",
                str(float(args.slippage_bps)),
                "--stop-loss-pct",
                str(float(args.stop_loss_pct)),
                "--take-profit-pct",
                str(float(args.take_profit_pct)),
                "--min-tp-reach-prob",
                str(float(args.min_tp_reach_prob)),
                "--tp-min-factor",
                str(float(args.tp_min_factor)),
                "--horizons-grid",
                args.horizons_grid,
                "--p-long-grid",
                args.p_long_grid,
                "--p-short-grid",
                args.p_short_grid,
                "--min-expected-move-grid",
                args.min_expected_move_grid,
                "--notional-usd-grid",
                str(args.notional_usd_grid).strip() or str(float(args.notional_usd)),
                "--leverage",
                str(float(args.leverage)),
                "--signal-mode",
                str(args.signal_mode),
                "--execution-mode",
                str(args.execution_mode),
                "--order-type",
                str(args.order_type),
                "--limit-offset-bps",
                str(float(args.limit_offset_bps)),
                "--min-net-return-pct-goal",
                str(float(args.goal_net_return_pct)),
                "--cooldown-bars",
                str(int(args.cooldown_bars)),
                "--trend-filter",
                trend_filter_i,
                "--min-abs-ema-gap",
                str(float(min_abs_ema_gap_i)),
                "--workers",
                str(int(max(1, search_workers))),
            ]
            if bool(args.disable_timeout_exit):
                search_cmd.append("--disable-timeout-exit")
            if search_engine == "optuna":
                search_cmd.extend(
                    [
                        "--contour-id",
                        str(contour_id),
                        "--test-day",
                        str(args.test_day),
                        "--stage",
                        str(args.optuna_stage),
                        "--calibration-grid-preset",
                        str(args.calibration_grid_preset),
                        "--force-profile-edge-coverage",
                        str(args.force_profile_edge_coverage),
                        "--process-workers-total",
                        str(int(max(1, args.process_workers_total))),
                    ]
                )
                if str(args.optuna_shared_study_id).strip():
                    search_cmd.extend(["--shared-study-id", str(args.optuna_shared_study_id).strip()])
                if int(args.optuna_n_trials_override) > 0:
                    search_cmd.extend(["--n-trials-override", str(int(args.optuna_n_trials_override))])
                if int(args.optuna_timeout_sec_override) > 0:
                    search_cmd.extend(["--timeout-sec-override", str(int(args.optuna_timeout_sec_override))])
                search_cmd.extend(["--ml-signal-backend", str(args.optuna_ml_signal_backend)])

            rc, parsed, so, se = _run(
                project_root,
                search_cmd,
                cpu_max=args.cpu_max_pct,
                max_threads=runtime_threads,
                budget_check_interval_sec=float(args.cpu_budget_check_interval_sec),
                budget_max_wait_sec=float(args.cpu_budget_max_wait_sec),
                budget_consecutive_ok=int(args.cpu_budget_consecutive_ok),
            )
            step["search_rc"] = rc
            step["search_module"] = search_module
            step["search_stdout_tail"] = so[-1200:]
            step["search_stderr_tail"] = se[-1200:]
            if rc != 0 or not parsed or not parsed.get("report_path"):
                step["status"] = "search_failed"
                step["search_error"] = "search subprocess failed or no parsable report_path in stdout"
                history.append(step)
                _print_progress(
                    progress_path=progress_path,
                    step=step,
                    completed=len(history),
                    total=int(effective_repeats),
                    run_started_perf=run_started_perf,
                    best_oos=best_oos,
                )
                continue
            step["search_report_path"] = parsed["report_path"]
            sr, sr_error = _read_json_report_with_retry(parsed["report_path"])
            if sr is None:
                step["status"] = "search_report_read_failed"
                step["search_error"] = sr_error or "search report could not be read"
                history.append(step)
                _print_progress(
                    progress_path=progress_path,
                    step=step,
                    completed=len(history),
                    total=int(effective_repeats),
                    run_started_perf=run_started_perf,
                    best_oos=best_oos,
                )
                continue
            candidates = _candidate_pool_from_search_report(sr)
            step["pass_candidates"] = int(sr.get("pass_candidates", 0)) if isinstance(sr, dict) else 0
            step["goal_candidates"] = int(sr.get("goal_candidates", 0)) if isinstance(sr, dict) else 0
            step["candidate_pool"] = int(len(candidates))
            parsed2 = None
            choice = None
            train_ready = False
            candidate_attempts: list[dict] = []
            current_candidates = [c for c in candidates if isinstance(c, dict)]
            max_candidate_attempts = max(1, int(args.candidate_replay_attempts))
            if current_candidates:
                max_candidate_attempts = min(max_candidate_attempts, len(current_candidates))
            step["candidate_replay_attempts_limit"] = int(max_candidate_attempts)
            attempt_rejected: set[str] = set()

            for candidate_attempt in range(1, max_candidate_attempts + 1):
                combined_rejected = set(rejected)
                combined_rejected.update(attempt_rejected)
                choice, selection_mode = _pick_candidate(
                    candidates=current_candidates,
                    rejected=combined_rejected,
                    goal_net_return_pct=float(args.goal_net_return_pct),
                    strict_goal_only=bool(strict_goal_only),
                    min_candidate_trades=int(args.min_candidate_trades),
                )
                step["selection_mode"] = str(selection_mode)
                step["candidate_attempt"] = int(candidate_attempt)
                if choice is None:
                    step["status"] = "no_goal_candidate" if strict_goal_only else "no_candidate"
                    step["reason"] = "no candidate matched goal threshold" if strict_goal_only else "no candidate available"
                    no_goal_candidate_iterations += 1 if strict_goal_only else 0
                    history.append(step)
                    _print_progress(
                        progress_path=progress_path,
                        step=step,
                        completed=len(history),
                        total=int(effective_repeats),
                        run_started_perf=run_started_perf,
                        best_oos=best_oos,
                    )
                    break

                step["candidate"] = {
                    "horizon_bars": choice.get("horizon_bars"),
                    "p_enter_long": choice.get("p_enter_long"),
                    "p_enter_short": choice.get("p_enter_short"),
                    "min_expected_move_pct": choice.get("min_expected_move_pct"),
                    "score": choice.get("score"),
                    "trend_filter": choice.get("trend_filter", trend_filter_i),
                    "min_abs_ema_gap": choice.get("min_abs_ema_gap", min_abs_ema_gap_i),
                    "calibration_params": dict(choice.get("calibration_params") or {}),
                }
                selected_calibration_params = dict(choice.get("calibration_params") or {})
                selected_trend_filter = str(choice.get("trend_filter", trend_filter_i))
                selected_min_abs_ema_gap = float(choice.get("min_abs_ema_gap", min_abs_ema_gap_i))
                step["selected_trend_filter"] = selected_trend_filter
                step["selected_min_abs_ema_gap"] = selected_min_abs_ema_gap
                step["selected_calibration_params"] = selected_calibration_params

                runtime_threads, cpu_now, cpu_dbg = _next_threads(
                    runtime_threads=runtime_threads,
                    iter_threads=int(iter_threads),
                    ramp_min=int(ramp_min),
                    cpu_ramp_enabled=bool(cpu_ramp_enabled),
                    cpu_max_pct=float(args.cpu_max_pct),
                    cpu_ramp_up_step=int(args.cpu_ramp_up_step),
                    cpu_ramp_down_step=int(args.cpu_ramp_down_step),
                    cpu_control_window_sec=float(args.cpu_control_window_sec),
                    cpu_sample_interval_sec=float(args.cpu_sample_interval_sec),
                    cpu_hot_threshold_pct=float(args.cpu_hot_threshold_pct),
                    cpu_cool_threshold_pct=float(args.cpu_cool_threshold_pct),
                )
                step["train_cpu_before_pct"] = cpu_now
                step["train_cpu_window"] = cpu_dbg
                step["train_threads"] = int(runtime_threads)

                train_cmd = [
                    sys.executable,
                    "-m",
                    "mlbotnav.pipeline_train_eval",
                    "--symbol",
                    args.symbol,
                    "--timeframe",
                    args.timeframe,
                    "--start-date",
                    args.train_start,
                    "--end-date",
                    args.train_end,
                    "--layer",
                    runtime_data_layer,
                    "--horizon-bars",
                    str(int(choice.get("horizon_bars", 1))),
                    "--min-train-rows",
                    str(int(args.min_train_rows)),
                    "--n-folds",
                    str(int(args.n_folds)),
                    "--fee-bps",
                    str(float(args.fee_bps)),
                    "--slippage-bps",
                    str(float(args.slippage_bps)),
                    "--p-enter-long",
                    str(float(choice.get("p_enter_long", 0.55))),
                    "--p-enter-short",
                    str(float(choice.get("p_enter_short", 0.45))),
                    "--stop-loss-pct",
                    str(float(args.stop_loss_pct)),
                    "--take-profit-pct",
                    str(float(args.take_profit_pct)),
                    "--min-expected-move-pct",
                    str(float(choice.get("min_expected_move_pct", 0.0))),
                    "--tp-min-factor",
                    str(float(args.tp_min_factor)),
                    "--cooldown-bars",
                    str(int(args.cooldown_bars)),
                    "--trend-filter",
                    selected_trend_filter,
                    "--min-abs-ema-gap",
                    str(float(selected_min_abs_ema_gap)),
                    "--notional-usd",
                    str(float(args.notional_usd)),
                    "--leverage",
                    str(float(args.leverage)),
                    "--signal-mode",
                    str(args.signal_mode),
                    "--execution-mode",
                    str(args.execution_mode),
                    "--order-type",
                    str(args.order_type),
                    "--limit-offset-bps",
                    str(float(args.limit_offset_bps)),
                    "--disable-ablation",
                    "--model-family",
                    "auto",
                    "--calibration-params-json",
                    json.dumps(selected_calibration_params, ensure_ascii=True, sort_keys=True),
                ]
                if bool(args.disable_timeout_exit):
                    train_cmd.append("--disable-timeout-exit")

                rc2, parsed2, so2, se2 = _run(
                    project_root,
                    train_cmd,
                    cpu_max=args.cpu_max_pct,
                    max_threads=runtime_threads,
                    budget_check_interval_sec=float(args.cpu_budget_check_interval_sec),
                    budget_max_wait_sec=float(args.cpu_budget_max_wait_sec),
                    budget_consecutive_ok=int(args.cpu_budget_consecutive_ok),
                )
                step["train_rc"] = rc2
                step["train_stdout_tail"] = so2[-1200:]
                step["train_stderr_tail"] = se2[-1200:]
                attempt_info = {
                    "attempt": int(candidate_attempt),
                    "selection_mode": str(selection_mode),
                    "signature": _sig(choice),
                    "candidate": dict(step["candidate"]),
                    "train_rc": int(rc2),
                }
                if rc2 != 0 or not parsed2 or not parsed2.get("report_path"):
                    attempt_info["status"] = "train_failed"
                    candidate_attempts.append(attempt_info)
                    step["candidate_attempts"] = candidate_attempts
                    rejected.add(_sig(choice))
                    attempt_rejected.add(_sig(choice))
                    if candidate_attempt < max_candidate_attempts:
                        continue
                    step["status"] = "train_failed"
                    step["train_error"] = "train subprocess failed or no parsable report_path in stdout"
                    history.append(step)
                    _print_progress(
                        progress_path=progress_path,
                        step=step,
                        completed=len(history),
                        total=int(effective_repeats),
                        run_started_perf=run_started_perf,
                        best_oos=best_oos,
                    )
                    break

                attempt_info["status"] = "train_ok"
                attempt_info["train_report_path"] = str(parsed2.get("report_path"))
                candidate_attempts.append(attempt_info)
                step["candidate_attempts"] = candidate_attempts
                train_ready = True
                break

            if not train_ready:
                continue
            step["train_gate_pass"] = bool(parsed2.get("gate_pass", False))
            raw_reasons = parsed2.get("reasons", [])
            if isinstance(raw_reasons, list):
                step["train_gate_reasons"] = [str(x) for x in raw_reasons]
            else:
                step["train_gate_reasons"] = []
            step["train_report_path"] = str(parsed2.get("report_path"))

            runtime_threads, cpu_now, cpu_dbg = _next_threads(
                runtime_threads=runtime_threads,
                iter_threads=int(iter_threads),
                ramp_min=int(ramp_min),
                cpu_ramp_enabled=bool(cpu_ramp_enabled),
                cpu_max_pct=float(args.cpu_max_pct),
                cpu_ramp_up_step=int(args.cpu_ramp_up_step),
                cpu_ramp_down_step=int(args.cpu_ramp_down_step),
                cpu_control_window_sec=float(args.cpu_control_window_sec),
                cpu_sample_interval_sec=float(args.cpu_sample_interval_sec),
                cpu_hot_threshold_pct=float(args.cpu_hot_threshold_pct),
                cpu_cool_threshold_pct=float(args.cpu_cool_threshold_pct),
            )
            step["oos_cpu_before_pct"] = cpu_now
            step["oos_cpu_window"] = cpu_dbg
            step["oos_threads"] = int(runtime_threads)

            oos_cmd = [
                sys.executable,
                "-m",
                "mlbotnav.oos_evaluate",
                "--train-pipeline-report",
                str(parsed2["report_path"]),
                "--test-day",
                args.test_day,
                "--test-end-day",
                str(args.test_end_day) if args.test_end_day else str(args.test_day),
                "--layer",
                runtime_data_layer,
                "--goal-net-return-pct",
                str(float(args.goal_net_return_pct)),
                "--leverage",
                str(float(args.leverage)),
                "--signal-mode",
                str(args.signal_mode),
                "--execution-mode",
                str(args.execution_mode),
                "--order-type",
                str(args.order_type),
                "--limit-offset-bps",
                str(float(args.limit_offset_bps)),
            ]
            if bool(args.disable_timeout_exit):
                oos_cmd.append("--disable-timeout-exit")

            rc3, parsed3, so3, se3 = _run(
                project_root,
                oos_cmd,
                cpu_max=args.cpu_max_pct,
                max_threads=runtime_threads,
                budget_check_interval_sec=float(args.cpu_budget_check_interval_sec),
                budget_max_wait_sec=float(args.cpu_budget_max_wait_sec),
                budget_consecutive_ok=int(args.cpu_budget_consecutive_ok),
            )
            step["oos_rc"] = rc3
            step["oos_stdout_tail"] = so3[-1200:]
            step["oos_stderr_tail"] = se3[-1200:]
            if rc3 != 0 or not parsed3 or not parsed3.get("oos_report"):
                step["status"] = "oos_failed"
                step["oos_error"] = "oos subprocess failed or no parsable oos_report in stdout"
                rejected.add(_sig(choice))
                history.append(step)
                _print_progress(
                    progress_path=progress_path,
                    step=step,
                    completed=len(history),
                    total=int(effective_repeats),
                    run_started_perf=run_started_perf,
                    best_oos=best_oos,
                )
                continue

            step["oos_report"] = parsed3["oos_report"]
            oos, oos_error = _read_json_report_with_retry(parsed3["oos_report"])
            if oos is None:
                step["status"] = "oos_report_read_failed"
                step["oos_error"] = oos_error or "oos report could not be read"
                rejected.add(_sig(choice))
                history.append(step)
                _print_progress(
                    progress_path=progress_path,
                    step=step,
                    completed=len(history),
                    total=int(effective_repeats),
                    run_started_perf=run_started_perf,
                    best_oos=best_oos,
                )
                continue
            step["oos_net_return_pct"] = float((oos.get("backtest") or {}).get("net_return_pct", 0.0))
            step["oos_trades"] = int((oos.get("backtest") or {}).get("trades", 0))
            step["goal_pass"] = bool(oos.get("goal_pass", False))
            if best_oos is None or _best_step_key(step) > _best_step_key(best_oos):
                best_oos = step
            if step["goal_pass"]:
                step["status"] = "goal_pass"
                success = True
                history.append(step)
                _print_progress(
                    progress_path=progress_path,
                    step=step,
                    completed=len(history),
                    total=int(effective_repeats),
                    run_started_perf=run_started_perf,
                    best_oos=best_oos,
                )
                if bool(args.stop_on_goal_pass):
                    break
                # Keep searching for an even better setup; avoid repeating same signature.
                step["continue_search"] = True
                rejected.add(_sig(choice))
                continue
            step["status"] = "goal_fail"
            rejected.add(_sig(choice))
            history.append(step)
            _print_progress(
                progress_path=progress_path,
                step=step,
                completed=len(history),
                total=int(effective_repeats),
                run_started_perf=run_started_perf,
                best_oos=best_oos,
            )
    finally:
        if unlock_applied:
            save_readiness(project_root, original_readiness)
            _clear_unlock_marker(project_root)
        readiness_after = load_readiness(project_root)
        readiness_restored = readiness_after == original_readiness

    _save_rejected(mem_path, mem_key, rejected, symbol=args.symbol, timeframe=args.timeframe)

    best_train_meta = _read_train_report_meta(best_oos.get("train_report_path") if isinstance(best_oos, dict) else None)
    repro_manifest = _build_repro_manifest(project_root)
    search_workers_observed = [
        int(x.get("search_workers", 0))
        for x in history
        if isinstance(x, dict) and int(x.get("search_workers", 0)) > 0
    ]
    effective_profile_mode = str(hypothesis_meta.get("source", "") or "").strip().lower() not in {"single_filter", "cli_grid"}
    if isinstance(best_train_meta, dict) and best_train_meta:
        repro_manifest["best_train_rows_raw"] = best_train_meta.get("rows_raw")
        repro_manifest["best_train_rows_featured"] = best_train_meta.get("rows_featured")
        repro_manifest["best_train_report_sha256"] = best_train_meta.get("report_sha256")
    filter_invariance = _detect_filter_invariant_warning(history)
    success_effective = bool(success)
    success_blocked_by_filter_invariant_warning = False
    if bool(filter_invariance.get("filter_invariant_warning", False)) and success_effective:
        success_effective = False
        success_blocked_by_filter_invariant_warning = True

    summary = {
        "run_utc": ts,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "search_engine": str(search_engine),
        "optuna_stage": (str(args.optuna_stage) if str(search_engine) == "optuna" else None),
        "optuna_overrides": dict(optuna_overrides),
        "engine_contour_note": engine_contour_note,
        "train_window": {"start": args.train_start, "end": args.train_end},
        "test_day": args.test_day,
        "test_end_day": str(args.test_end_day) if args.test_end_day else str(args.test_day),
        "goal_net_return_pct": float(args.goal_net_return_pct),
        "cooldown_bars": int(args.cooldown_bars),
        "trend_filter": str(args.trend_filter),
        "min_abs_ema_gap": float(args.min_abs_ema_gap),
        "long_style_1m": bool(args.long_style_1m),
        "use_hypothesis_profile": bool(args.use_hypothesis_profile),
        "use_hypothesis_profile_effective": bool(effective_profile_mode),
        "hypothesis_profile": hypothesis_meta.get("profile"),
        "hypothesis_plan_source": hypothesis_meta.get("source"),
        "hypothesis_plan_config_path": hypothesis_meta.get("config_path"),
        "hypothesis_plan": hypothesis_plan,
        "backlog_registry": backlog_registry,
        "backlog_active_names": [str(x.get("name")) for x in active_backlog],
        "strict_goal_only": strict_goal_only,
        "stop_on_goal_pass": bool(args.stop_on_goal_pass),
        "forced_stop_on_goal_pass_ignored": bool(forced_stop_on_goal_pass_ignored),
        "notional_usd": float(args.notional_usd),
        "leverage": float(args.leverage),
        "effective_notional_usd": float(args.notional_usd) * float(args.leverage),
        "signal_mode": str(args.signal_mode),
        "execution_mode": str(args.execution_mode),
        "order_type": str(args.order_type),
        "limit_offset_bps": float(args.limit_offset_bps),
        "repeats_requested": int(args.repeats),
        "repeats_effective": int(effective_repeats),
        "repeats_effective_mismatch": bool(repeats_effective_mismatch),
        "candidate_replay_attempts": int(args.candidate_replay_attempts),
        "max_threads": int(args.max_threads),
        "search_workers_requested": int(args.search_workers),
        "search_workers_effective_min": (min(search_workers_observed) if search_workers_observed else None),
        "search_workers_effective_max": (max(search_workers_observed) if search_workers_observed else None),
        "thread_ramp": ramp_threads,
        "cpu_ramp_enabled": (not bool(args.cpu_ramp_disable)),
        "speed_profile": str(args.speed_profile),
        "cpu_ramp_min_threads": int(args.cpu_ramp_min_threads),
        "cpu_ramp_up_step": int(args.cpu_ramp_up_step),
        "cpu_ramp_down_step": int(args.cpu_ramp_down_step),
        "cpu_control_window_sec": float(args.cpu_control_window_sec),
        "cpu_sample_interval_sec": float(args.cpu_sample_interval_sec),
        "cpu_budget_check_interval_sec": float(args.cpu_budget_check_interval_sec),
        "cpu_budget_max_wait_sec": float(args.cpu_budget_max_wait_sec),
        "cpu_budget_consecutive_ok": int(args.cpu_budget_consecutive_ok),
        "cpu_hot_threshold_pct": float(args.cpu_hot_threshold_pct),
        "cpu_cool_threshold_pct": float(args.cpu_cool_threshold_pct),
        "no_goal_candidate_iterations": int(no_goal_candidate_iterations),
        "success": success_effective,
        "success_blocked_by_filter_invariant_warning": bool(success_blocked_by_filter_invariant_warning),
        "history": history,
        "best_oos": best_oos,
        "best_train_meta": best_train_meta,
        "best_train_gate_pass": bool(best_oos.get("train_gate_pass", False)) if isinstance(best_oos, dict) else None,
        "best_train_gate_reasons": list(best_oos.get("train_gate_reasons", [])) if isinstance(best_oos, dict) else [],
        "readiness_checks": blocked_checks,
        "preflight_window": preflight_once,
        "readiness_restored": readiness_restored,
        "temporary_unlock_readiness": bool(args.temporary_unlock_readiness),
        "stale_unlock_recovery": stale_unlock_recovery,
        "daily_window_policy": ("fixed_24h_train_prev_day_and_24h_closed_test_day" if str(args.window_policy) == "fixed_1d" else "contiguous_multiday_windows"),
        "daily_window_validated": daily_window,
        "memory_key": mem_key,
        "contour_id": contour_id,
        "negative_memory_path": str(mem_path),
        "progress_log_path": str(progress_path),
        "repro_manifest": repro_manifest,
        "filter_invariance_check": filter_invariance,
    }
    top_publish_error = None
    top_publish = None
    try:
        top_publish = publish_best_oos_from_adaptive(
            project_root=project_root,
            summary_path=summary_path,
            summary=summary,
            top_root=(project_root / "reports" / "top_strategy" / contour_id),
        )
    except Exception as e:
        top_publish_error = str(e)
    if top_publish is not None:
        summary["top_strategy"] = top_publish
    if top_publish_error:
        summary["top_strategy_error"] = top_publish_error

    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    audit = {
        "run_utc": ts,
        "summary_path": str(summary_path),
        "status": "completed",
        "f1_no_auto_unlock_default": not bool(args.temporary_unlock_readiness),
        "f2_strict_goal_enabled": strict_goal_only,
        "f3_readiness_restored": readiness_restored,
        "f4_json_parsing_mode": "robust_scan_from_end",
        "f5_memory_key": mem_key,
        "f6_filter_invariant_warning": bool(filter_invariance.get("filter_invariant_warning", False)),
        "f7_success_blocked_by_filter_invariant_warning": bool(success_blocked_by_filter_invariant_warning),
        "contour_id": contour_id,
        "memory_path": str(mem_path),
        "progress_log_path": str(progress_path),
    }
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "summary_path": str(summary_path),
                "audit_path": str(audit_path),
                "success": success_effective,
                "iterations_done": len(history),
                "top_strategy": top_publish,
                "top_strategy_error": top_publish_error,
                "progress_log_path": str(progress_path),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
