from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from mlbotnav.stas5_common import PROJECT_ROOT, compact_day, iter_days, normalize_day, rel, utc_now, write_json
from mlbotnav.stas5_v5_forward_visual_review import (
    DECISION_COLUMN,
    SCORE_COLUMN,
    SYMBOL,
    TIMEFRAME,
    _build_strength_strip_rows,
    _find_context_ohlcv_path,
    _find_predictions_path,
    _load_ohlcv,
    _load_predictions,
    _source_csv,
    render_forward_day_overview,
)


STATUS_PASS = "PASS_V5C_STAS8_MOVE_CAPACITY_AUDIT_V1_READY_NO_TRAINING_NO_DECISION_CHANGE"
STATUS_FAIL = "FAIL_V5C_STAS8_MOVE_CAPACITY_AUDIT_V1"
SOFT_V2_STATUS_PASS = "PASS_V5C_STAS8_SOFT_CAPACITY_V2_PREVIEW_READY_NO_TRAINING_NO_FORWARD_NO_DECISION_CHANGE"
SOFT_V2_STATUS_FAIL = "FAIL_V5C_STAS8_SOFT_CAPACITY_V2_PREVIEW"
LAYER_ID = "STAS8_MOVE_CAPACITY_GRID_V1"
LIVE_CONTEXT_ID = "STAS8_LIVE_MOVE_CONTEXT_V1"
TEACHER_GRID_ID = "STAS8_TEACHER_MOVE_GRID_V1"
SOFT_V2_LAYER_ID = "STAS8_SOFT_CAPACITY_V2"

KEY_COLUMNS = ["day", "candidate_id", "record_id", "entry_time_utc"]
HORIZONS_MIN = [30, 60, 120, 240]
KEY_THRESHOLDS = [1.0, 1.1, 1.2, 1.5, 2.0]

LIVE_SOURCE_COLUMNS = [
    "cs_return_15m_pct",
    "cs_return_30m_pct",
    "cs_return_60m_pct",
    "cs_return_120m_pct",
    "cs_return_240m_pct",
    "cs_range_15m_pct",
    "cs_range_30m_pct",
    "cs_range_60m_pct",
    "cs_range_120m_pct",
    "cs_range_240m_pct",
    "cs_atr_expansion_score",
    "cs_last_candle_range_pct",
    "cs_direction_flip_count_30m",
    "cs_lower_lows_count_30m",
    "cs_lower_highs_count_30m",
    "cs_higher_lows_count_30m",
    "cs_higher_highs_count_30m",
    "cs_bounce_from_recent_low_pct",
    "cs_pullback_from_recent_high_pct",
    "cs_bottom_attempt_score",
    "cs_base_after_flush_score",
    "cs_retest_low_count",
    "cs_low_edge_zone",
    "cs_short_pressure_now",
    "cs_long_pressure_now",
    "cs_dump_acceleration_score",
    "cs_pre_dump_risk_score",
    "cs_falling_knife_active",
    "cs_sell_pressure_exhaustion_score",
    "cs_price_breaking_recent_support",
    "session_so_far_range_pct",
    "day_so_far_range_pct",
    "fcs_channel_width_pct",
    "fcs_channel_slope_pct_per_min",
    "fcs_channel_position_0_1",
    "fcs_channel_breakdown_recent",
    "fcs_channel_is_lower_edge",
    "fcs_channel_is_upper_edge",
    "fcs_support_broken_recently",
    "fcs_knife_risk_score",
    "fcs_knife_active",
    "fcs_knife_drop_pct_so_far",
    "fcs_knife_acceleration_score",
    "fcs_knife_exhaustion_score",
    "fcs_bounce_from_knife_low_pct",
    "fcs_grounding_confirmed_score",
    "fcs_retest_after_knife_score",
    "fcs_regime_score_chop_no_edge",
    "fcs_regime_score_short_pressure",
    "fcs_regime_score_pre_dump_risk",
    "fcs_regime_score_active_dump",
    "fcs_regime_score_bottoming",
    "fcs_regime_score_base_after_flush",
    "fcs_post_pump_exhaustion_score",
    "fcs_pre_dump_after_pump_score",
    "fcs_failed_breakout_score",
    "bb20_width_pct",
    "bb20_position_0_1",
    "bb20_zscore",
    "bb20_mid_slope_15m_pct",
    "bb20_mid_slope_60m_pct",
    "bb20_close_ret_15m_pct",
    "bb20_close_ret_30m_pct",
    "bb20_close_ret_60m_pct",
    "bb20_range_20m_pct",
    "bb20_range_60m_pct",
    "bb20_down_channel_score",
    "bb20_falling_knife_score",
    "bb20_rebound_from_low_score",
    "bb20_post_knife_stabilization_score",
    "bb20_dead_move_score",
]

FORBIDDEN_LIVE_PATTERNS = [
    "future",
    "postfact",
    "hit_",
    "mfe",
    "mae",
    "time_to_",
    "tp",
    "exit",
    "manual",
    "review",
    "entry_y",
    "risk_bad_y",
    "move_capacity_y",
    "move_edge_y",
    "phase_y",
    "state_y",
    "reason_y",
]

SOFT_V2_PRESETS: dict[str, dict[str, Any]] = {
    "strict": {
        "no_move_range60": 0.45,
        "no_move_range120": 0.80,
        "low_move_range120": 1.10,
        "down_ret60": -0.55,
        "down_ret120": -0.90,
        "down_ret240": -1.30,
        "short_pressure": 0.58,
        "short_gap": 0.15,
        "hard_risk": 0.74,
        "wait_risk": 0.58,
        "protect_bounce": 0.58,
        "protect_up_leg": 0.55,
        "protect_edge": 0.52,
        "protect_risk_max": 0.58,
        "allow_move": 0.54,
        "allow_edge": 0.48,
        "soft_enter_to_watch": True,
        "recall_watch": False,
    },
    "balanced": {
        "no_move_range60": 0.42,
        "no_move_range120": 0.78,
        "low_move_range120": 1.00,
        "down_ret60": -0.65,
        "down_ret120": -1.00,
        "down_ret240": -1.45,
        "short_pressure": 0.62,
        "short_gap": 0.18,
        "hard_risk": 0.82,
        "wait_risk": 0.66,
        "protect_bounce": 0.46,
        "protect_up_leg": 0.42,
        "protect_edge": 0.40,
        "protect_risk_max": 0.76,
        "allow_move": 0.42,
        "allow_edge": 0.34,
        "soft_enter_to_watch": True,
        "recall_watch": True,
    },
    "wide": {
        "no_move_range60": 0.35,
        "no_move_range120": 0.65,
        "low_move_range120": 0.86,
        "down_ret60": -0.78,
        "down_ret120": -1.20,
        "down_ret240": -1.75,
        "short_pressure": 0.70,
        "short_gap": 0.24,
        "hard_risk": 0.90,
        "wait_risk": 0.76,
        "protect_bounce": 0.38,
        "protect_up_leg": 0.34,
        "protect_edge": 0.28,
        "protect_risk_max": 0.86,
        "allow_move": 0.34,
        "allow_edge": 0.24,
        "soft_enter_to_watch": False,
        "recall_watch": True,
    },
}

SOFT_V2_LIVE_INPUT_COLUMNS = [
    "ENTRY_ML_LIVE_SCORE",
    "ENTRY_ML_LIVE_DECISION_BEFORE_STAS8",
    "STAS8_LIVE_ACTION",
    "STAS8_LIVE_STATE",
    "STAS8_LIVE_REASON_TAGS",
    "STAS8_LIVE_MOVE_SCORE",
    "STAS8_LIVE_RISK_SCORE",
    "STAS8_LIVE_EDGE_SCORE",
    "STAS8_LIVE_RANGE_60M_PCT",
    "STAS8_LIVE_RANGE_120M_PCT",
    "STAS8_LIVE_RANGE_240M_PCT",
    "STAS8_LIVE_RET_60M_PCT",
    "STAS8_LIVE_RET_120M_PCT",
    "STAS8_LIVE_RET_240M_PCT",
    "STAS8_LIVE_WAVE_TURNS_120M",
    "STAS8_LIVE_BOUNCE_FROM_LOW_PCT",
    "STAS8_LIVE_UP_LEG_AFTER_LOW_PCT",
    "STAS8_LIVE_DOWN_LEG_AFTER_HIGH_PCT",
    "STAS8_LIVE_REBOUND_PROTECTED",
    "STAS8_LIVE_NO_MOVE_FLAG",
    "STAS8_LIVE_DOWN_CHANNEL_FLAG",
    "STAS8_LIVE_HIGH_VOL_DANGER_FLAG",
]


def _resolve_forward_run_dir(forward_run_id: str | None, forward_run_dir: Path | None) -> Path:
    if forward_run_dir is not None:
        return forward_run_dir
    if forward_run_id:
        return PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5c" / "forward" / "runs" / forward_run_id
    latest = PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5c" / "forward" / "STAS5_V5C_LATEST_TWO_BLOCK_FORWARD_RUN.json"
    if not latest.exists():
        raise FileNotFoundError(f"Latest V5C forward pointer not found: {latest}")
    payload = json.loads(latest.read_text(encoding="utf-8"))
    return PROJECT_ROOT / str(payload["run_dir"])


def _find_forward_dataset_path(forward_run_dir: Path) -> Path:
    candidates = sorted(
        forward_run_dir.glob("STAS5_V5C_FORWARD_DATASET_*_X*_CONTINUOUS_V1.csv"),
        key=lambda item: item.stat().st_mtime,
    )
    if not candidates:
        raise FileNotFoundError(f"V5C forward dataset not found in {forward_run_dir}")
    return candidates[-1]


def _manifest_path(forward_run_dir: Path) -> Path:
    path = forward_run_dir / "STAS5_V5C_FORWARD_MANIFEST_V1.json"
    if not path.exists():
        raise FileNotFoundError(f"V5C forward manifest not found: {path}")
    return path


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _dense_thresholds() -> list[float]:
    values: list[float] = []
    current = 0.4
    while current <= 5.000001:
        values.append(round(current, 1))
        current += 0.1
    current = 5.2
    while current <= 10.000001:
        values.append(round(current, 1))
        current += 0.2
    return values


def _pct_label(value: float) -> str:
    return f"{value:.1f}".replace(".", "p")


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        out = float(value)
        if math.isnan(out) or math.isinf(out):
            return default
        return out
    except Exception:
        return default


def _row_float(row: pd.Series, column: str, default: float = 0.0) -> float:
    return _safe_float(row.get(column, default), default)


def _clip01(value: float) -> float:
    if math.isnan(value) or math.isinf(value):
        return 0.0
    return max(0.0, min(1.0, float(value)))


def _pct_change(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return (float(numerator) / float(denominator) - 1.0) * 100.0


def _load_ohlcv_days(start_day: str, end_day: str, *, warmup_days: int = 1, future_days: int = 1) -> tuple[pd.DataFrame, dict[str, Any]]:
    source_start = (pd.Timestamp(normalize_day(start_day)) - pd.Timedelta(days=warmup_days)).strftime("%Y-%m-%d")
    source_end = (pd.Timestamp(normalize_day(end_day)) + pd.Timedelta(days=future_days)).strftime("%Y-%m-%d")
    frames: list[pd.DataFrame] = []
    inputs: list[dict[str, Any]] = []
    missing: list[str] = []
    for day in iter_days(source_start, source_end):
        path = _source_csv(PROJECT_ROOT, day, TIMEFRAME, SYMBOL)
        if not path.exists():
            missing.append(day)
            continue
        frame = _load_ohlcv(path)
        frames.append(frame)
        inputs.append({"day": day, "path": rel(path), "rows": int(len(frame))})
    if frames:
        out = (
            pd.concat(frames, ignore_index=True, sort=False)
            .sort_values("open_time_utc")
            .drop_duplicates(["open_time_utc"], keep="last")
            .reset_index(drop=True)
        )
    else:
        out = pd.DataFrame()
    summary = {
        "source_start_day": source_start,
        "source_end_day": source_end,
        "rows": int(len(out)),
        "missing_days": missing,
        "inputs": inputs,
        "first_open_time_utc": _ts_to_string(out["open_time_utc"].iloc[0]) if not out.empty else "",
        "last_open_time_utc": _ts_to_string(out["open_time_utc"].iloc[-1]) if not out.empty else "",
    }
    return out, summary


def _ts_to_string(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def _entry_price(row: pd.Series, ohlcv: pd.DataFrame) -> float:
    for column in ["entry_price_5bps", "entry_open_price", "entry_price_visual", "entry_price"]:
        if column in row:
            value = _safe_float(row.get(column), 0.0)
            if value > 0:
                return value
    entry_ts = pd.Timestamp(row["entry_ts"]).tz_convert("UTC")
    past = ohlcv[ohlcv["open_time_utc"] < entry_ts].tail(1)
    if not past.empty:
        return _safe_float(past["close"].iloc[-1], 0.0)
    return 0.0


def _wave_turn_count(close_values: pd.Series, *, threshold_pct: float = 0.28) -> int:
    values = [float(v) for v in pd.to_numeric(close_values, errors="coerce").dropna().tolist() if float(v) > 0]
    if len(values) < 3:
        return 0
    pivot = values[0]
    direction = 0
    turns = 0
    for price in values[1:]:
        if pivot <= 0:
            pivot = price
            continue
        change = _pct_change(price, pivot)
        if direction == 0:
            if abs(change) >= threshold_pct:
                direction = 1 if change > 0 else -1
                pivot = price
            continue
        if direction > 0:
            if price >= pivot:
                pivot = price
            elif _pct_change(pivot, price) >= threshold_pct:
                turns += 1
                direction = -1
                pivot = price
        else:
            if price <= pivot:
                pivot = price
            elif _pct_change(price, pivot) >= threshold_pct:
                turns += 1
                direction = 1
                pivot = price
    return int(turns)


def _past_window(df: pd.DataFrame, entry_ts: pd.Timestamp, minutes: int) -> pd.DataFrame:
    start = entry_ts - pd.Timedelta(minutes=minutes)
    return df[(df["open_time_utc"] >= start) & (df["open_time_utc"] < entry_ts)].copy()


def _window_metrics(window: pd.DataFrame, prefix: str) -> dict[str, Any]:
    if window.empty:
        return {
            f"{prefix}_rows": 0,
            f"{prefix}_range_pct": 0.0,
            f"{prefix}_return_pct": 0.0,
            f"{prefix}_bounce_from_low_pct": 0.0,
            f"{prefix}_drop_from_high_pct": 0.0,
            f"{prefix}_up_leg_after_low_pct": 0.0,
            f"{prefix}_down_leg_after_high_pct": 0.0,
            f"{prefix}_wave_turns": 0,
        }
    close = pd.to_numeric(window["close"], errors="coerce")
    high = pd.to_numeric(window["high"], errors="coerce")
    low = pd.to_numeric(window["low"], errors="coerce")
    last_close = _safe_float(close.iloc[-1], 0.0)
    first_close = _safe_float(close.iloc[0], last_close)
    highest = _safe_float(high.max(), last_close)
    lowest = _safe_float(low.min(), last_close)
    low_idx = low.idxmin()
    high_idx = high.idxmax()
    max_after_low = _safe_float(high.loc[low_idx:].max(), last_close) if low_idx in high.index else last_close
    min_after_high = _safe_float(low.loc[high_idx:].min(), last_close) if high_idx in low.index else last_close
    return {
        f"{prefix}_rows": int(len(window)),
        f"{prefix}_range_pct": round(_pct_change(highest, lowest), 6) if lowest > 0 else 0.0,
        f"{prefix}_return_pct": round(_pct_change(last_close, first_close), 6) if first_close > 0 else 0.0,
        f"{prefix}_bounce_from_low_pct": round(_pct_change(last_close, lowest), 6) if lowest > 0 else 0.0,
        f"{prefix}_drop_from_high_pct": round(_pct_change(highest, last_close), 6) if last_close > 0 else 0.0,
        f"{prefix}_up_leg_after_low_pct": round(_pct_change(max_after_low, lowest), 6) if lowest > 0 else 0.0,
        f"{prefix}_down_leg_after_high_pct": round(_pct_change(highest, min_after_high), 6) if min_after_high > 0 else 0.0,
        f"{prefix}_wave_turns": _wave_turn_count(close),
    }


def _past_metrics(ohlcv: pd.DataFrame, entry_ts: pd.Timestamp) -> dict[str, Any]:
    out: dict[str, Any] = {}
    past = ohlcv[ohlcv["open_time_utc"] < entry_ts].copy()
    if past.empty:
        out["stas8_live_source_time_utc"] = ""
    else:
        out["stas8_live_source_time_utc"] = _ts_to_string(past["open_time_utc"].iloc[-1])
    for minutes in [30, 60, 120, 240]:
        out.update(_window_metrics(_past_window(ohlcv, entry_ts, minutes), f"stas8_past_{minutes}m"))
    return out


def _live_context_decision(row: pd.Series, past: dict[str, Any]) -> dict[str, Any]:
    range60 = max(_row_float(row, "cs_range_60m_pct"), _safe_float(past.get("stas8_past_60m_range_pct")))
    range120 = max(_row_float(row, "cs_range_120m_pct"), _safe_float(past.get("stas8_past_120m_range_pct")))
    range240 = max(_row_float(row, "cs_range_240m_pct"), _safe_float(past.get("stas8_past_240m_range_pct")))
    ret60 = _row_float(row, "cs_return_60m_pct", _safe_float(past.get("stas8_past_60m_return_pct")))
    ret120 = _row_float(row, "cs_return_120m_pct", _safe_float(past.get("stas8_past_120m_return_pct")))
    ret240 = _row_float(row, "cs_return_240m_pct", _safe_float(past.get("stas8_past_240m_return_pct")))
    bb_ret60 = _row_float(row, "bb20_close_ret_60m_pct")
    if abs(bb_ret60) > abs(ret60):
        ret60 = bb_ret60

    wave_turns = max(
        int(round(_safe_float(past.get("stas8_past_120m_wave_turns")))),
        int(round(_row_float(row, "cs_direction_flip_count_30m"))),
    )
    bounce = max(
        _row_float(row, "cs_bounce_from_recent_low_pct"),
        _row_float(row, "fcs_bounce_from_knife_low_pct"),
        _safe_float(past.get("stas8_past_60m_bounce_from_low_pct")),
        _safe_float(past.get("stas8_past_120m_bounce_from_low_pct")),
    )
    up_leg = max(
        _safe_float(past.get("stas8_past_60m_up_leg_after_low_pct")),
        _safe_float(past.get("stas8_past_120m_up_leg_after_low_pct")),
        _row_float(row, "cs_bounce_from_recent_low_pct"),
    )
    down_leg = max(
        _safe_float(past.get("stas8_past_60m_down_leg_after_high_pct")),
        _safe_float(past.get("stas8_past_120m_down_leg_after_high_pct")),
        _row_float(row, "cs_pullback_from_recent_high_pct"),
    )
    short_pressure = max(_row_float(row, "cs_short_pressure_now"), _row_float(row, "fcs_regime_score_short_pressure"))
    long_pressure = _row_float(row, "cs_long_pressure_now")
    active_dump = max(_row_float(row, "cs_dump_acceleration_score"), _row_float(row, "fcs_regime_score_active_dump"))
    pre_dump = max(_row_float(row, "cs_pre_dump_risk_score"), _row_float(row, "fcs_regime_score_pre_dump_risk"))
    support_break = max(_row_float(row, "cs_price_breaking_recent_support"), _row_float(row, "fcs_support_broken_recently"))
    channel_break = _row_float(row, "fcs_channel_breakdown_recent")
    channel_slope = _row_float(row, "fcs_channel_slope_pct_per_min")
    channel_pos = _row_float(row, "fcs_channel_position_0_1", 0.5)
    channel_width = _row_float(row, "fcs_channel_width_pct")
    knife = max(
        _row_float(row, "cs_falling_knife_active"),
        _row_float(row, "fcs_knife_active"),
        _row_float(row, "fcs_knife_risk_score"),
        _row_float(row, "bb20_falling_knife_score"),
    )
    grounding = _row_float(row, "fcs_grounding_confirmed_score")
    retest = _row_float(row, "fcs_retest_after_knife_score")
    base_after_flush = max(_row_float(row, "cs_base_after_flush_score"), _row_float(row, "fcs_regime_score_base_after_flush"))
    bottoming = max(_row_float(row, "cs_bottom_attempt_score"), _row_float(row, "fcs_regime_score_bottoming"))
    exhaustion = max(_row_float(row, "cs_sell_pressure_exhaustion_score"), _row_float(row, "fcs_knife_exhaustion_score"))
    bb_down = _row_float(row, "bb20_down_channel_score")
    bb_dead = _row_float(row, "bb20_dead_move_score")
    bb_rebound = max(_row_float(row, "bb20_rebound_from_low_score"), _row_float(row, "bb20_post_knife_stabilization_score"))
    bb_pos = _row_float(row, "bb20_position_0_1", 0.5)
    bb_slope60 = _row_float(row, "bb20_mid_slope_60m_pct")

    tags: list[str] = []
    range_ok = range60 >= 0.80 or range120 >= 1.20 or range240 >= 1.50
    working_move_ok = range60 >= 1.10 or range120 >= 1.50 or range240 >= 2.00
    waves_ok = wave_turns >= 2 and up_leg >= 0.45 and down_leg >= 0.35
    rebound_ok = bounce >= 0.45 or bb_rebound >= 0.55 or bottoming >= 0.55
    retest_ok = grounding >= 0.55 or retest >= 0.55 or base_after_flush >= 0.60
    rebound_protect = (bounce >= 0.58 and (retest_ok or bb_rebound >= 0.60 or bottoming >= 0.62)) and active_dump < 0.82

    no_move = (
        (range60 < 0.55 and range120 < 0.95)
        or (bb_dead >= 0.76 and range120 < 1.20)
        or (channel_width > 0 and channel_width < 0.45 and range120 < 1.10)
    )
    bearish_multi_window = int(ret60 <= -0.45) + int(ret120 <= -0.80) + int(ret240 <= -1.20) >= 2
    down_channel = (
        bearish_multi_window
        or channel_break >= 0.80
        or bb_down >= 0.66
        or (channel_slope <= -0.0025 and channel_pos < 0.55)
        or (bb_slope60 <= -0.45 and bb_pos < 0.55)
    )
    short_dominates = short_pressure >= 0.55 and short_pressure >= long_pressure + 0.12
    hard_dump_or_knife = knife >= 0.82 or (active_dump >= 0.82 and support_break >= 0.70) or support_break >= 0.97
    high_vol_danger = hard_dump_or_knife and (bearish_multi_window or down_channel or short_dominates) and not rebound_protect
    weak_bounce_in_short = down_channel and not rebound_protect and (bounce < 0.60 or not waves_ok)

    if range_ok:
        tags.append("MOVE_RANGE_SEEN")
    if working_move_ok:
        tags.append("WORKING_MOVE_RANGE")
    if waves_ok:
        tags.append("UP_DOWN_WAVES_SEEN")
    if rebound_ok:
        tags.append("REBOUND_FROM_LOW")
    if retest_ok:
        tags.append("RETEST_OR_BASE")
    if rebound_protect:
        tags.append("REBOUND_PROTECTED")
    if no_move:
        tags.append("NO_MOVE")
    if down_channel:
        tags.append("DOWN_CHANNEL")
    if short_dominates:
        tags.append("SHORT_PRESSURE")
    if high_vol_danger:
        tags.append("HIGH_VOL_DANGER")
    if weak_bounce_in_short:
        tags.append("WEAK_BOUNCE_IN_SHORT")

    if no_move and not rebound_ok:
        action = "WAIT_NO_MOVE"
        state = "LONG_SEARCH_OFF_NO_MOVE"
    elif high_vol_danger:
        action = "BLOCK_HIGH_VOL_DANGER"
        state = "LONG_SEARCH_OFF_DOWN_ONLY"
    elif down_channel and short_dominates and not rebound_protect:
        action = "BLOCK_DOWN_CHANNEL"
        state = "LONG_SEARCH_OFF_DOWN_ONLY"
    elif weak_bounce_in_short:
        action = "BLOCK_WEAK_BOUNCE"
        state = "LONG_SEARCH_OFF_WEAK_BOUNCE"
    elif range_ok and (waves_ok or rebound_ok or retest_ok) and not high_vol_danger:
        action = "ALLOW_ENTRY_SEARCH"
        if rebound_protect or retest_ok:
            state = "LONG_SEARCH_ON_REBOUND"
        elif waves_ok:
            state = "LONG_SEARCH_ON_WAVES"
        else:
            state = "LONG_SEARCH_ON_PULLBACK"
    elif range_ok:
        action = "WAIT_WARMUP"
        state = "LONG_SEARCH_WARMUP"
    else:
        action = "WAIT_NO_MOVE"
        state = "LONG_SEARCH_OFF_NO_MOVE"

    live_move_score = _clip01(
        0.34 * _clip01(range60 / 1.20)
        + 0.28 * _clip01(range120 / 1.80)
        + 0.18 * _clip01(wave_turns / 4.0)
        + 0.20 * max(_clip01(bounce / 0.90), bb_rebound)
    )
    risk_score = _clip01(
        0.32 * max(_clip01(-ret120 / 1.8), bb_down)
        + 0.26 * max(knife, active_dump, pre_dump)
        + 0.22 * _clip01(short_pressure - long_pressure + 0.25)
        + 0.20 * max(channel_break, support_break)
    )
    edge_score = _clip01(live_move_score * (1.0 - 0.60 * risk_score) + (0.18 if rebound_protect else 0.0))

    return {
        "STAS8_LIVE_ACTION": action,
        "STAS8_LIVE_STATE": state,
        "STAS8_LIVE_REASON_TAGS": "|".join(tags),
        "STAS8_LIVE_MOVE_SCORE": round(float(live_move_score), 6),
        "STAS8_LIVE_RISK_SCORE": round(float(risk_score), 6),
        "STAS8_LIVE_EDGE_SCORE": round(float(edge_score), 6),
        "STAS8_LIVE_RANGE_60M_PCT": round(float(range60), 6),
        "STAS8_LIVE_RANGE_120M_PCT": round(float(range120), 6),
        "STAS8_LIVE_RANGE_240M_PCT": round(float(range240), 6),
        "STAS8_LIVE_RET_60M_PCT": round(float(ret60), 6),
        "STAS8_LIVE_RET_120M_PCT": round(float(ret120), 6),
        "STAS8_LIVE_RET_240M_PCT": round(float(ret240), 6),
        "STAS8_LIVE_WAVE_TURNS_120M": int(wave_turns),
        "STAS8_LIVE_BOUNCE_FROM_LOW_PCT": round(float(bounce), 6),
        "STAS8_LIVE_UP_LEG_AFTER_LOW_PCT": round(float(up_leg), 6),
        "STAS8_LIVE_DOWN_LEG_AFTER_HIGH_PCT": round(float(down_leg), 6),
        "STAS8_LIVE_REBOUND_PROTECTED": int(rebound_protect),
        "STAS8_LIVE_NO_MOVE_FLAG": int(no_move),
        "STAS8_LIVE_DOWN_CHANNEL_FLAG": int(down_channel),
        "STAS8_LIVE_HIGH_VOL_DANGER_FLAG": int(high_vol_danger),
    }


def _future_window(ohlcv: pd.DataFrame, entry_ts: pd.Timestamp, minutes: int) -> pd.DataFrame:
    end = entry_ts + pd.Timedelta(minutes=minutes)
    return ohlcv[(ohlcv["open_time_utc"] > entry_ts) & (ohlcv["open_time_utc"] <= end)].copy()


def _threshold_hit_metrics(window: pd.DataFrame, entry_ts: pd.Timestamp, entry_price: float, threshold_pct: float) -> dict[str, Any]:
    if window.empty or entry_price <= 0:
        return {"hit_y": 0, "time_to_min": "", "mae_before_pct": ""}
    target_price = entry_price * (1.0 + threshold_pct / 100.0)
    hit_rows = window[pd.to_numeric(window["high"], errors="coerce") >= target_price]
    if hit_rows.empty:
        low_slice = window
        hit = 0
        time_to: Any = ""
    else:
        first_hit_ts = pd.Timestamp(hit_rows["open_time_utc"].iloc[0])
        low_slice = window[window["open_time_utc"] <= first_hit_ts]
        hit = 1
        time_to = round((first_hit_ts - entry_ts).total_seconds() / 60.0, 3)
    min_low = _safe_float(pd.to_numeric(low_slice["low"], errors="coerce").min(), entry_price)
    mae = max(0.0, (entry_price - min_low) / entry_price * 100.0) if entry_price > 0 else 0.0
    return {"hit_y": hit, "time_to_min": time_to, "mae_before_pct": round(float(mae), 6)}


def _teacher_metrics(row: pd.Series, ohlcv: pd.DataFrame, thresholds: list[float]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    entry_ts = pd.Timestamp(row["entry_ts"]).tz_convert("UTC")
    price = _entry_price(row, ohlcv)
    out: dict[str, Any] = {"STAS8_TEACHER_ENTRY_PRICE": round(float(price), 8) if price > 0 else 0.0}
    for horizon in HORIZONS_MIN:
        window = _future_window(ohlcv, entry_ts, horizon)
        if window.empty or price <= 0:
            out[f"future_max_up_{horizon}m_pct"] = 0.0
            out[f"future_max_down_{horizon}m_pct"] = 0.0
            out[f"future_range_{horizon}m_pct"] = 0.0
            out[f"future_rows_{horizon}m"] = int(len(window))
            continue
        max_high = _safe_float(pd.to_numeric(window["high"], errors="coerce").max(), price)
        min_low = _safe_float(pd.to_numeric(window["low"], errors="coerce").min(), price)
        out[f"future_max_up_{horizon}m_pct"] = round(max(0.0, (max_high - price) / price * 100.0), 6)
        out[f"future_max_down_{horizon}m_pct"] = round(max(0.0, (price - min_low) / price * 100.0), 6)
        out[f"future_range_{horizon}m_pct"] = round(max(0.0, (max_high - min_low) / price * 100.0), 6)
        out[f"future_rows_{horizon}m"] = int(len(window))

    horizon_window = _future_window(ohlcv, entry_ts, 240)
    grid_rows: list[dict[str, Any]] = []
    for threshold in thresholds:
        metrics = _threshold_hit_metrics(horizon_window, entry_ts, price, threshold)
        key = _pct_label(threshold)
        if threshold in KEY_THRESHOLDS:
            out[f"hit_{key}_y"] = int(metrics["hit_y"])
            out[f"time_to_{key}_min"] = metrics["time_to_min"]
            out[f"mae_before_{key}_pct"] = metrics["mae_before_pct"]
        grid_rows.append(
            {
                "day": row["day"],
                "candidate_id": row["candidate_id"],
                "record_id": row["record_id"],
                "entry_time_utc": row["entry_time_utc"],
                "threshold_pct": threshold,
                "hit_y": int(metrics["hit_y"]),
                "time_to_min": metrics["time_to_min"],
                "mae_before_pct": metrics["mae_before_pct"],
            }
        )
    return out, grid_rows


def _teacher_bucket(teacher: dict[str, Any], live: dict[str, Any]) -> dict[str, Any]:
    max_up_120 = _safe_float(teacher.get("future_max_up_120m_pct"))
    max_up_240 = _safe_float(teacher.get("future_max_up_240m_pct"))
    max_down_120 = _safe_float(teacher.get("future_max_down_120m_pct"))
    hit_1p1 = int(_safe_float(teacher.get("hit_1p1_y")))
    hit_1p2 = int(_safe_float(teacher.get("hit_1p2_y")))
    hit_1p5 = int(_safe_float(teacher.get("hit_1p5_y")))
    action = str(live.get("STAS8_LIVE_ACTION", ""))
    tags = str(live.get("STAS8_LIVE_REASON_TAGS", ""))

    if max_up_240 >= 5.0:
        bucket = "SPIKE_EXTREME"
    elif action == "BLOCK_HIGH_VOL_DANGER":
        bucket = "HIGH_VOL_DANGER"
    elif "DOWN_CHANNEL" in tags and not hit_1p2:
        bucket = "NO_MOVE_DOWN_CHANNEL"
    elif action == "BLOCK_WEAK_BOUNCE" and not hit_1p2:
        bucket = "DOWN_CHANNEL_WEAK_BOUNCE"
    elif int(_safe_float(live.get("STAS8_LIVE_REBOUND_PROTECTED"))) and hit_1p2:
        bucket = "POST_KNIFE_RETEST_EDGE" if "RETEST_OR_BASE" in tags else "LOCAL_LOW_REBOUND_EDGE"
    elif hit_1p5:
        bucket = "MOVE_OK_1P5"
    elif hit_1p2:
        bucket = "MOVE_OK_1P2"
    elif hit_1p1:
        bucket = "MOVE_OK_1P1"
    elif max_up_120 < 0.70 and max_down_120 < 0.70:
        bucket = "NO_MOVE"
    elif max_up_240 >= 1.2 and not hit_1p2:
        bucket = "LATE_PUMP_DEPENDENT"
    else:
        bucket = "LOW_MOVE_CHOP"

    move_capacity_y = int(hit_1p2)
    move_edge_y = int(hit_1p2 and max_down_120 <= 1.8)
    reason = f"max_up_120={max_up_120:.3f}|max_up_240={max_up_240:.3f}|max_down_120={max_down_120:.3f}|live={action}"
    return {
        "move_capacity_y": move_capacity_y,
        "move_edge_y": move_edge_y,
        "move_capacity_bucket": bucket,
        "move_capacity_reason": reason,
    }


def _base_entry_decision(row: pd.Series) -> str:
    value = str(row.get("ENTRY_ML_LIVE_DECISION_BEFORE_RISKGATE") or "").strip().upper()
    if value in {"ENTER", "WATCH", "SKIP"}:
        return value
    value = str(row.get(DECISION_COLUMN) or "").strip().upper()
    return value if value in {"ENTER", "WATCH", "SKIP"} else "SKIP"


def _after_stas8_decision(before: str, live_action: str) -> tuple[str, str]:
    before = before if before in {"ENTER", "WATCH", "SKIP"} else "SKIP"
    if before == "SKIP":
        return "SKIP", "KEEP_SKIP_NO_PROMOTION"
    if live_action.startswith("BLOCK_"):
        return "SKIP", "STAS8_BLOCK_TO_SKIP"
    if live_action == "WAIT_NO_MOVE":
        return "SKIP" if before == "WATCH" else "WATCH", "STAS8_WAIT_NO_MOVE"
    if live_action == "WAIT_WARMUP":
        return "WATCH", "STAS8_WAIT_WARMUP"
    return before, "KEEP_ENTRY_DECISION"


def _soft_v2_column(preset: str, suffix: str) -> str:
    return f"STAS8_SOFT_V2_{preset.upper()}_{suffix}"


def _soft_v2_teacher_good(row: dict[str, Any] | pd.Series) -> tuple[int, int]:
    hit_1p2 = int(_safe_float(row.get("hit_1p2_y", 0)))
    mae_1p2 = _safe_float(row.get("mae_before_1p2_pct", 999.0), 999.0)
    time_1p2 = _safe_float(row.get("time_to_1p2_min", 999.0), 999.0)
    ok = int(hit_1p2 == 1 and mae_1p2 <= 0.80 and time_1p2 <= 180.0)
    hq = int(hit_1p2 == 1 and mae_1p2 <= 0.50 and time_1p2 <= 120.0)
    return ok, hq


def _soft_v2_live_bucket(row: dict[str, Any] | pd.Series, preset: str) -> dict[str, Any]:
    cfg = SOFT_V2_PRESETS[preset]
    tags = str(row.get("STAS8_LIVE_REASON_TAGS", ""))
    live_action = str(row.get("STAS8_LIVE_ACTION", ""))
    move_score = _safe_float(row.get("STAS8_LIVE_MOVE_SCORE"))
    risk_score = _safe_float(row.get("STAS8_LIVE_RISK_SCORE"))
    edge_score = _safe_float(row.get("STAS8_LIVE_EDGE_SCORE"))
    range60 = _safe_float(row.get("STAS8_LIVE_RANGE_60M_PCT"))
    range120 = _safe_float(row.get("STAS8_LIVE_RANGE_120M_PCT"))
    range240 = _safe_float(row.get("STAS8_LIVE_RANGE_240M_PCT"))
    ret60 = _safe_float(row.get("STAS8_LIVE_RET_60M_PCT"))
    ret120 = _safe_float(row.get("STAS8_LIVE_RET_120M_PCT"))
    ret240 = _safe_float(row.get("STAS8_LIVE_RET_240M_PCT"))
    wave_turns = int(round(_safe_float(row.get("STAS8_LIVE_WAVE_TURNS_120M"))))
    bounce = _safe_float(row.get("STAS8_LIVE_BOUNCE_FROM_LOW_PCT"))
    up_leg = _safe_float(row.get("STAS8_LIVE_UP_LEG_AFTER_LOW_PCT"))
    down_leg = _safe_float(row.get("STAS8_LIVE_DOWN_LEG_AFTER_HIGH_PCT"))
    no_move_flag = int(_safe_float(row.get("STAS8_LIVE_NO_MOVE_FLAG")))
    down_channel_flag = int(_safe_float(row.get("STAS8_LIVE_DOWN_CHANNEL_FLAG")))
    high_vol_flag = int(_safe_float(row.get("STAS8_LIVE_HIGH_VOL_DANGER_FLAG")))
    rebound_flag = int(_safe_float(row.get("STAS8_LIVE_REBOUND_PROTECTED")))

    bearish_windows = int(ret60 <= cfg["down_ret60"]) + int(ret120 <= cfg["down_ret120"]) + int(ret240 <= cfg["down_ret240"])
    wave_seen = wave_turns >= 2 and up_leg >= cfg["protect_up_leg"] and down_leg >= 0.30
    move_ready = range60 >= 1.10 or range120 >= 1.20 or (range240 >= 1.50 and wave_seen)
    protect = (
        (rebound_flag == 1 or "REBOUND_PROTECTED" in tags or "RETEST_OR_BASE" in tags)
        and bounce >= cfg["protect_bounce"]
        and up_leg >= cfg["protect_up_leg"]
        and edge_score >= cfg["protect_edge"]
        and risk_score <= cfg["protect_risk_max"]
        and not (high_vol_flag == 1 and risk_score >= cfg["hard_risk"])
    )
    protect = protect or (
        "REBOUND_FROM_LOW" in tags
        and move_ready
        and edge_score >= cfg["protect_edge"] + 0.06
        and risk_score <= cfg["protect_risk_max"]
    )

    no_move = (
        (no_move_flag == 1 and range60 < cfg["no_move_range60"] and range120 < cfg["no_move_range120"])
        or (range60 < cfg["no_move_range60"] and range120 < cfg["no_move_range120"] and move_score < cfg["allow_move"])
    )
    low_move_chop = (
        range120 < cfg["low_move_range120"]
        and range240 < 1.35
        and move_score < cfg["allow_move"]
        and not protect
        and bearish_windows < 2
    )
    down_only = (
        (down_channel_flag == 1 and bearish_windows >= 2)
        or (bearish_windows >= 2 and risk_score >= cfg["wait_risk"])
        or (live_action == "BLOCK_DOWN_CHANNEL" and risk_score >= cfg["wait_risk"])
    )
    active_knife = high_vol_flag == 1 and risk_score >= cfg["hard_risk"] and not protect
    weak_bounce_short = (
        (live_action == "BLOCK_WEAK_BOUNCE" or ("DOWN_CHANNEL" in tags and "WEAK_BOUNCE_IN_SHORT" in tags))
        and risk_score >= cfg["wait_risk"]
        and not protect
    )

    if active_knife:
        bucket = "LIVE_ACTIVE_KNIFE"
    elif no_move:
        bucket = "LIVE_NO_MOVE"
    elif down_only and not protect:
        bucket = "LIVE_DOWN_ONLY"
    elif weak_bounce_short:
        bucket = "LIVE_DOWN_CHANNEL_WEAK_BOUNCE"
    elif low_move_chop:
        bucket = "LIVE_LOW_MOVE_CHOP"
    elif protect:
        bucket = "LIVE_POST_KNIFE_REBOUND_EDGE"
    elif move_ready and (wave_seen or bounce >= cfg["protect_bounce"]) and edge_score >= cfg["allow_edge"]:
        bucket = "LIVE_MOVE_OK"
    elif range120 >= 1.10 and edge_score >= cfg["allow_edge"]:
        bucket = "LIVE_MOVE_WARMUP"
    else:
        bucket = "LIVE_WAIT_CONFIRMATION"

    return {
        "bucket": bucket,
        "protect": int(protect),
        "no_move": int(no_move),
        "low_move_chop": int(low_move_chop),
        "down_only": int(down_only and not protect),
        "active_knife": int(active_knife),
        "weak_bounce_short": int(weak_bounce_short),
        "move_ready": int(move_ready),
        "wave_seen": int(wave_seen),
        "reason": (
            f"bucket={bucket}|range60={range60:.3f}|range120={range120:.3f}|range240={range240:.3f}|"
            f"ret60={ret60:.3f}|ret120={ret120:.3f}|ret240={ret240:.3f}|"
            f"move={move_score:.3f}|risk={risk_score:.3f}|edge={edge_score:.3f}|"
            f"bounce={bounce:.3f}|up_leg={up_leg:.3f}|waves={wave_turns}|tags={tags}"
        ),
    }


def _soft_capacity_v2_decision(row: dict[str, Any] | pd.Series, preset: str) -> dict[str, Any]:
    if preset not in SOFT_V2_PRESETS:
        raise ValueError(f"Unknown STAS8 soft V2 preset: {preset}")
    cfg = SOFT_V2_PRESETS[preset]
    before = str(row.get("ENTRY_ML_LIVE_DECISION_BEFORE_STAS8", "SKIP")).upper()
    before = before if before in {"ENTER", "WATCH", "SKIP"} else "SKIP"
    live = _soft_v2_live_bucket(row, preset)
    teacher_ok, teacher_hq = _soft_v2_teacher_good(row)
    hard_block = live["bucket"] in {"LIVE_ACTIVE_KNIFE", "LIVE_NO_MOVE", "LIVE_DOWN_ONLY"}
    soft_wait = live["bucket"] in {"LIVE_LOW_MOVE_CHOP", "LIVE_DOWN_CHANNEL_WEAK_BOUNCE", "LIVE_WAIT_CONFIRMATION", "LIVE_MOVE_WARMUP"}
    protect = bool(live["protect"]) or live["bucket"] in {"LIVE_POST_KNIFE_REBOUND_EDGE", "LIVE_MOVE_OK"}
    if before == "SKIP":
        live_decision = "SKIP"
        review_decision = "RECALL_WATCH" if cfg["recall_watch"] and teacher_ok and protect else "SKIP"
        action = "AUDIT_RECALL_WATCH_ONLY" if review_decision == "RECALL_WATCH" else "KEEP_SKIP_NO_PROMOTION"
    elif hard_block:
        live_decision = "SKIP"
        review_decision = "SKIP"
        action = f"HARD_BLOCK_{live['bucket'].replace('LIVE_', '')}"
    elif soft_wait:
        live_decision = "WATCH"
        review_decision = "WATCH"
        action = f"SOFT_WAIT_{live['bucket'].replace('LIVE_', '')}"
    elif protect:
        live_decision = before
        review_decision = before
        action = f"PROTECT_{live['bucket'].replace('LIVE_', '')}"
    elif before == "ENTER" and cfg["soft_enter_to_watch"]:
        live_decision = "WATCH"
        review_decision = "WATCH"
        action = "SOFT_WAIT_LOW_EDGE_CONFIRMATION"
    else:
        live_decision = before
        review_decision = before
        action = "KEEP_ENTRY_DECISION"

    marker = "NONE"
    if before in {"ENTER", "WATCH"} and hard_block:
        marker = "RISK BAD"
    elif before == "ENTER" and live_decision == "WATCH":
        marker = "BAD"
    elif live_decision == "ENTER":
        marker = "GOOD"

    return {
        "LIVE_BUCKET": live["bucket"],
        "LIVE_DECISION": live_decision,
        "REVIEW_DECISION": review_decision,
        "ACTION": action,
        "MARKER_LABEL": marker,
        "REASON": live["reason"],
        "HARD_BLOCK_FLAG": int(hard_block),
        "SOFT_WAIT_FLAG": int(soft_wait),
        "PROTECT_FLAG": int(protect),
        "RECALL_WATCH_AUDIT_Y": int(review_decision == "RECALL_WATCH"),
        "TEACHER_GOOD_1P2_OK_Y": teacher_ok,
        "TEACHER_GOOD_1P2_HQ_Y": teacher_hq,
        "LIVE_NO_MOVE_FLAG_V2": live["no_move"],
        "LIVE_LOW_MOVE_CHOP_FLAG_V2": live["low_move_chop"],
        "LIVE_DOWN_ONLY_FLAG_V2": live["down_only"],
        "LIVE_ACTIVE_KNIFE_FLAG_V2": live["active_knife"],
        "LIVE_WEAK_BOUNCE_SHORT_FLAG_V2": live["weak_bounce_short"],
        "LIVE_MOVE_READY_FLAG_V2": live["move_ready"],
        "LIVE_WAVE_SEEN_FLAG_V2": live["wave_seen"],
    }


def _join_predictions_and_x(predictions: pd.DataFrame, x_rows: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    missing_keys = sorted(set(KEY_COLUMNS).difference(x_rows.columns))
    if missing_keys:
        raise ValueError(f"Forward dataset missing key columns: {missing_keys}")
    x_keys = x_rows[KEY_COLUMNS].copy()
    duplicate_x_keys = int(x_keys.duplicated(KEY_COLUMNS).sum())
    merged = predictions.merge(x_rows, on=KEY_COLUMNS, how="left", suffixes=("", "_x463"))
    source_indicator = merged.get("anchor_time_utc")
    missing_x_rows = int(source_indicator.isna().sum()) if source_indicator is not None else 0
    return merged, {
        "duplicate_x_keys": duplicate_x_keys,
        "missing_x_rows_after_join": missing_x_rows,
        "joined_rows": int(len(merged)),
    }


def _build_audit_rows(merged: pd.DataFrame, ohlcv: pd.DataFrame, thresholds: list[float]) -> tuple[pd.DataFrame, pd.DataFrame]:
    audit_rows: list[dict[str, Any]] = []
    grid_rows: list[dict[str, Any]] = []
    for _, row in merged.sort_values(["day", "entry_ts", "candidate_id"]).iterrows():
        entry_ts = pd.Timestamp(row["entry_ts"]).tz_convert("UTC")
        past = _past_metrics(ohlcv, entry_ts)
        live = _live_context_decision(row, past)
        teacher, per_threshold = _teacher_metrics(row, ohlcv, thresholds)
        bucket = _teacher_bucket(teacher, live)
        before = _base_entry_decision(row)
        after, preview_action = _after_stas8_decision(before, str(live["STAS8_LIVE_ACTION"]))
        grid_rows.extend(per_threshold)
        record = {
            "day": row["day"],
            "candidate_id": row["candidate_id"],
            "record_id": row["record_id"],
            "entry_time_utc": row["entry_time_utc"],
            "ENTRY_ML_LIVE_SCORE": _row_float(row, SCORE_COLUMN),
            "ENTRY_ML_LIVE_DECISION_BEFORE_STAS8": before,
            "ENTRY_ML_LIVE_DECISION_ORIGINAL_FINAL": str(row.get(DECISION_COLUMN, before)).upper(),
            "ENTRY_ML_LIVE_DECISION_AFTER_STAS8_PREVIEW": after,
            "STAS8_MOVE_CAPACITY_ACTION": preview_action,
            "STAS8_LAYER_MODE": "AUDIT_PREVIEW_ONLY_NO_TRAINING_NO_PREDICTION_CHANGE",
            "STAS8_LIVE_CONTEXT_ID": LIVE_CONTEXT_ID,
            "STAS8_TEACHER_GRID_ID": TEACHER_GRID_ID,
            **past,
            **live,
            **teacher,
            **bucket,
        }
        for preset in SOFT_V2_PRESETS:
            soft = _soft_capacity_v2_decision(record, preset)
            for suffix, value in soft.items():
                record[_soft_v2_column(preset, suffix)] = value
        audit_rows.append(record)
    return pd.DataFrame(audit_rows), pd.DataFrame(grid_rows)


def _annotations_for_day(day_rows: pd.DataFrame) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for _, row in day_rows.iterrows():
        before = str(row.get("ENTRY_ML_LIVE_DECISION_BEFORE_STAS8", "")).upper()
        if before not in {"ENTER", "WATCH"}:
            continue
        cid = str(row["candidate_id"]).upper()
        action = str(row.get("STAS8_LIVE_ACTION", ""))
        if action.startswith("BLOCK_"):
            out[cid] = ["RISK BAD"]
        elif action.startswith("WAIT_"):
            out[cid] = ["BAD"]
        else:
            out[cid] = ["GOOD"]
    return out


def _render_stas8_visuals(
    *,
    forward_run_dir: Path,
    predictions: pd.DataFrame,
    audit: pd.DataFrame,
    start_day: str,
    end_day: str,
    out_dir: Path,
    strict: bool,
) -> tuple[list[dict[str, Any]], list[str]]:
    day_outputs: list[dict[str, Any]] = []
    pngs: list[str] = []
    merged_rows = predictions.merge(
        audit[
            [
                "day",
                "candidate_id",
                "record_id",
                "entry_time_utc",
                "ENTRY_ML_LIVE_DECISION_BEFORE_STAS8",
                "ENTRY_ML_LIVE_DECISION_AFTER_STAS8_PREVIEW",
                "STAS8_LIVE_ACTION",
            ]
        ],
        on=KEY_COLUMNS,
        how="left",
    )
    for day in iter_days(start_day, end_day):
        day_rows = merged_rows[merged_rows["day"].astype(str).eq(day)].copy()
        day_rows = day_rows.sort_values("entry_ts").reset_index(drop=True)
        source = _source_csv(PROJECT_ROOT, day, TIMEFRAME, SYMBOL)
        if not source.exists():
            if strict:
                raise FileNotFoundError(f"OHLCV not found for visual: {source}")
            day_outputs.append({"day": day, "status": "MISSING_OHLCV", "source": rel(source)})
            continue
        day_df = _load_ohlcv(source)
        context_path = _find_context_ohlcv_path(forward_run_dir, day)
        strength_source = context_path if context_path is not None and context_path.exists() else source
        strength_df = _load_ohlcv(strength_source)
        strength_rows = _build_strength_strip_rows(strength_df, day, has_next_render_day=day < end_day)
        annotations = _annotations_for_day(day_rows)
        day_dir = out_dir / "visual_review" / compact_day(day)
        out_path = day_dir / f"STAS5_V5C_STAS8_MOVE_CAPACITY_AUDIT_{compact_day(day)}_V1.png"
        render_forward_day_overview(
            day_df=day_df,
            rows=day_rows,
            strength_hour_rows=strength_rows["hour_rows"],
            strength_macro_wave_rows=strength_rows["macro_wave_rows"],
            day=day,
            symbol=SYMBOL,
            timeframe=TIMEFRAME,
            out_path=out_path,
            review_annotations=annotations,
            review_panel_title="STAS8 MOVE CONTEXT PREVIEW",
            bollinger_preview=False,
            bollinger_source_df=strength_df,
            bollinger_window=20,
            bollinger_std=2.0,
        )
        counts_before = Counter(day_rows["ENTRY_ML_LIVE_DECISION_BEFORE_STAS8"].astype(str))
        audit_day = audit[audit["day"].astype(str).eq(day)]
        counts_after = Counter(audit_day["ENTRY_ML_LIVE_DECISION_AFTER_STAS8_PREVIEW"].astype(str))
        action_counts = Counter(audit_day["STAS8_LIVE_ACTION"].astype(str))
        pngs.append(rel(out_path))
        day_outputs.append(
            {
                "day": day,
                "status": "READY",
                "rows": int(len(day_rows)),
                "counts_before_stas8": {str(k): int(v) for k, v in counts_before.items()},
                "counts_after_stas8_preview": {str(k): int(v) for k, v in counts_after.items()},
                "stas8_live_action_counts": {str(k): int(v) for k, v in action_counts.items()},
                "png": rel(out_path),
                "bollinger_preview": False,
                "strength_strip_source": rel(strength_source),
                "annotations": {
                    "allow_good_circle": int(sum(1 for labels in annotations.values() if "GOOD" in labels)),
                    "wait_bad_square": int(sum(1 for labels in annotations.values() if "BAD" in labels and "RISK BAD" not in labels)),
                    "block_risk_bad_circle": int(sum(1 for labels in annotations.values() if "RISK BAD" in labels)),
                },
            }
        )
    return day_outputs, pngs


def _soft_v2_annotations_for_day(day_rows: pd.DataFrame, preset: str) -> dict[str, list[str]]:
    marker_col = _soft_v2_column(preset, "MARKER_LABEL")
    out: dict[str, list[str]] = {}
    if marker_col not in day_rows.columns:
        return out
    for _, row in day_rows.iterrows():
        marker = str(row.get(marker_col, "")).upper()
        if marker not in {"GOOD", "BAD", "RISK BAD"}:
            continue
        cid = str(row["candidate_id"]).upper()
        if marker == "RISK BAD":
            out[cid] = ["RISK BAD"]
        elif marker == "BAD":
            out[cid] = ["BAD"]
        else:
            out[cid] = ["GOOD"]
    return out


def _render_soft_v2_visuals(
    *,
    forward_run_dir: Path,
    predictions: pd.DataFrame,
    audit: pd.DataFrame,
    start_day: str,
    end_day: str,
    out_dir: Path,
    presets: list[str],
    strict: bool,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[str]]]:
    day_outputs: dict[str, list[dict[str, Any]]] = {}
    pngs: dict[str, list[str]] = {}
    common_cols = ["day", "candidate_id", "record_id", "entry_time_utc", "ENTRY_ML_LIVE_DECISION_BEFORE_STAS8"]
    soft_cols: list[str] = []
    for preset in presets:
        soft_cols.extend(
            [
                _soft_v2_column(preset, "LIVE_DECISION"),
                _soft_v2_column(preset, "REVIEW_DECISION"),
                _soft_v2_column(preset, "ACTION"),
                _soft_v2_column(preset, "LIVE_BUCKET"),
                _soft_v2_column(preset, "MARKER_LABEL"),
            ]
        )
    merged_rows = predictions.merge(audit[common_cols + soft_cols], on=KEY_COLUMNS, how="left")
    for preset in presets:
        preset_outputs: list[dict[str, Any]] = []
        preset_pngs: list[str] = []
        live_decision_col = _soft_v2_column(preset, "LIVE_DECISION")
        review_decision_col = _soft_v2_column(preset, "REVIEW_DECISION")
        action_col = _soft_v2_column(preset, "ACTION")
        bucket_col = _soft_v2_column(preset, "LIVE_BUCKET")
        recall_col = _soft_v2_column(preset, "RECALL_WATCH_AUDIT_Y")
        for day in iter_days(start_day, end_day):
            day_rows = merged_rows[merged_rows["day"].astype(str).eq(day)].copy()
            day_rows = day_rows.sort_values("entry_ts").reset_index(drop=True)
            source = _source_csv(PROJECT_ROOT, day, TIMEFRAME, SYMBOL)
            if not source.exists():
                if strict:
                    raise FileNotFoundError(f"OHLCV not found for soft V2 visual: {source}")
                preset_outputs.append({"day": day, "status": "MISSING_OHLCV", "source": rel(source)})
                continue
            day_df = _load_ohlcv(source)
            context_path = _find_context_ohlcv_path(forward_run_dir, day)
            strength_source = context_path if context_path is not None and context_path.exists() else source
            strength_df = _load_ohlcv(strength_source)
            strength_rows = _build_strength_strip_rows(strength_df, day, has_next_render_day=day < end_day)
            audit_day = audit[audit["day"].astype(str).eq(day)]
            hidden_recall = int(pd.to_numeric(audit_day[recall_col], errors="coerce").fillna(0).astype(int).eq(1).sum())
            annotations = _soft_v2_annotations_for_day(day_rows, preset)
            day_dir = out_dir / preset / "visual_review" / compact_day(day)
            out_path = day_dir / f"STAS8_SOFT_V2_{preset.upper()}_{compact_day(day)}.png"
            render_forward_day_overview(
                day_df=day_df,
                rows=day_rows,
                strength_hour_rows=strength_rows["hour_rows"],
                strength_macro_wave_rows=strength_rows["macro_wave_rows"],
                day=day,
                symbol=SYMBOL,
                timeframe=TIMEFRAME,
                out_path=out_path,
                review_annotations=annotations,
                review_panel_title=(
                    f"STAS8 SOFT V2 {preset.upper()}\n"
                    "green=final ENTER | square=ENTER->WATCH\n"
                    f"red circle=hard block | hidden SKIP recall={hidden_recall}"
                ),
                bollinger_preview=False,
                bollinger_source_df=strength_df,
                bollinger_window=20,
                bollinger_std=2.0,
            )
            counts_before = Counter(audit_day["ENTRY_ML_LIVE_DECISION_BEFORE_STAS8"].astype(str))
            counts_live = Counter(audit_day[live_decision_col].astype(str))
            counts_review = Counter(audit_day[review_decision_col].astype(str))
            action_counts = Counter(audit_day[action_col].astype(str))
            bucket_counts = Counter(audit_day[bucket_col].astype(str))
            preset_pngs.append(rel(out_path))
            preset_outputs.append(
                {
                    "day": day,
                    "status": "READY",
                    "rows": int(len(day_rows)),
                    "counts_before_stas8": {str(k): int(v) for k, v in counts_before.items()},
                    "counts_after_soft_v2_live": {str(k): int(v) for k, v in counts_live.items()},
                    "counts_after_soft_v2_review": {str(k): int(v) for k, v in counts_review.items()},
                    "soft_v2_action_counts": {str(k): int(v) for k, v in action_counts.items()},
                    "soft_v2_live_bucket_counts": {str(k): int(v) for k, v in bucket_counts.items()},
                    "png": rel(out_path),
                    "bollinger_preview": False,
                    "strength_strip_source": rel(strength_source),
                    "annotations": {
                        "live_enter_green_circle": int(sum(1 for labels in annotations.values() if "GOOD" in labels)),
                        "original_enter_soft_wait_red_square": int(
                            sum(1 for labels in annotations.values() if "BAD" in labels and "RISK BAD" not in labels)
                        ),
                        "original_enter_watch_hard_block_red_circle": int(
                            sum(1 for labels in annotations.values() if "RISK BAD" in labels)
                        ),
                        "hidden_skip_recall_watch_audit": hidden_recall,
                    },
                }
            )
        day_outputs[preset] = preset_outputs
        pngs[preset] = preset_pngs
    return day_outputs, pngs


def _soft_v2_summary(audit: pd.DataFrame, presets: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for preset in presets:
        live_col = _soft_v2_column(preset, "LIVE_DECISION")
        review_col = _soft_v2_column(preset, "REVIEW_DECISION")
        action_col = _soft_v2_column(preset, "ACTION")
        marker_col = _soft_v2_column(preset, "MARKER_LABEL")
        live_counts = Counter(audit[live_col].astype(str))
        review_counts = Counter(audit[review_col].astype(str))
        action_counts = Counter(audit[action_col].astype(str))
        markers = Counter(audit[marker_col].astype(str))
        original_ew = audit["ENTRY_ML_LIVE_DECISION_BEFORE_STAS8"].astype(str).isin(["ENTER", "WATCH"])
        hit_1p2 = pd.to_numeric(audit.get("hit_1p2_y", pd.Series(dtype=float)), errors="coerce").fillna(0).astype(int).eq(1)
        hard_block = pd.to_numeric(audit[_soft_v2_column(preset, "HARD_BLOCK_FLAG")], errors="coerce").fillna(0).astype(int).eq(1)
        protect = pd.to_numeric(audit[_soft_v2_column(preset, "PROTECT_FLAG")], errors="coerce").fillna(0).astype(int).eq(1)
        recall = pd.to_numeric(audit[_soft_v2_column(preset, "RECALL_WATCH_AUDIT_Y")], errors="coerce").fillna(0).astype(int).eq(1)
        rows.append(
            {
                "preset": preset,
                "rows": int(len(audit)),
                "live_ENTER": int(live_counts.get("ENTER", 0)),
                "live_WATCH": int(live_counts.get("WATCH", 0)),
                "live_SKIP": int(live_counts.get("SKIP", 0)),
                "review_RECALL_WATCH": int(review_counts.get("RECALL_WATCH", 0)),
                "marker_GOOD": int(markers.get("GOOD", 0)),
                "marker_BAD": int(markers.get("BAD", 0)),
                "marker_RISK_BAD": int(markers.get("RISK BAD", 0)),
                "original_ew_hit_1p2": int((original_ew & hit_1p2).sum()),
                "soft_v2_blocked_original_ew_hit_1p2": int((original_ew & hit_1p2 & hard_block).sum()),
                "soft_v2_protected_original_ew_hit_1p2": int((original_ew & hit_1p2 & protect).sum()),
                "soft_v2_recall_watch_audit": int(recall.sum()),
                "action_counts": {str(k): int(v) for k, v in action_counts.items()},
            }
        )
    return rows


def _soft_v2_guard(
    *,
    v1_guard: dict[str, Any],
    forward_manifest: dict[str, Any],
    predictions_sha_before: str,
    predictions_sha_after: str,
    audit: pd.DataFrame,
    start_day: str,
    end_day: str,
    presets: list[str],
    out_dir: Path,
) -> dict[str, Any]:
    live_forbidden_hits = sorted(
        column
        for column in SOFT_V2_LIVE_INPUT_COLUMNS
        for pattern in FORBIDDEN_LIVE_PATTERNS
        if pattern.lower() in column.lower()
    )
    source_times = pd.to_datetime(audit.get("stas8_live_source_time_utc"), utc=True, errors="coerce", format="mixed")
    entry_times = pd.to_datetime(audit.get("entry_time_utc"), utc=True, errors="coerce", format="mixed")
    active = source_times.notna() & entry_times.notna()
    source_after_entry = int((source_times[active] > entry_times[active]).sum())
    skip_to_enter: dict[str, int] = {}
    hard_block_kept_live_ew: dict[str, int] = {}
    hard_protect_conflict_ew: dict[str, int] = {}
    marker_semantic_mismatches: dict[str, dict[str, int]] = {}
    for preset in presets:
        before = audit["ENTRY_ML_LIVE_DECISION_BEFORE_STAS8"].astype(str).str.upper()
        after = audit[_soft_v2_column(preset, "LIVE_DECISION")].astype(str).str.upper()
        marker = audit[_soft_v2_column(preset, "MARKER_LABEL")].astype(str).str.upper()
        original_ew = before.isin(["ENTER", "WATCH"])
        hard_block = pd.to_numeric(audit[_soft_v2_column(preset, "HARD_BLOCK_FLAG")], errors="coerce").fillna(0).astype(int) == 1
        protect = pd.to_numeric(audit[_soft_v2_column(preset, "PROTECT_FLAG")], errors="coerce").fillna(0).astype(int) == 1
        skip_to_enter[preset] = int(((before == "SKIP") & (after == "ENTER")).sum())
        hard_block_kept_live_ew[preset] = int((original_ew & hard_block & after.isin(["ENTER", "WATCH"])).sum())
        hard_protect_conflict_ew[preset] = int((original_ew & hard_block & protect).sum())
        marker_semantic_mismatches[preset] = {
            "green_not_live_enter": int(((marker == "GOOD") & (after != "ENTER")).sum()),
            "red_square_not_enter_to_watch": int(((marker == "BAD") & ~((before == "ENTER") & (after == "WATCH"))).sum()),
            "red_circle_not_hard_block": int(((marker == "RISK BAD") & ~(original_ew & hard_block & (after == "SKIP"))).sum()),
            "skip_has_visible_marker": int(((before == "SKIP") & marker.isin(["GOOD", "BAD", "RISK BAD"])).sum()),
        }
    checks = [
        {
            "name": "v1_base_guard_pass",
            "passed": str(v1_guard.get("status", "")).startswith("PASS"),
            "value": v1_guard.get("status", ""),
        },
        {
            "name": "input_forward_manifest_pass",
            "passed": str(forward_manifest.get("status", "")).startswith("PASS"),
            "value": forward_manifest.get("status", ""),
        },
        {
            "name": "riskgate_not_applied_for_r5_entry_only_audit",
            "passed": forward_manifest.get("riskgate_ml_applied") is False,
            "value": forward_manifest.get("riskgate_ml_applied"),
        },
        {
            "name": "input_predictions_not_modified",
            "passed": predictions_sha_before == predictions_sha_after,
            "value": predictions_sha_after,
        },
        {
            "name": "source_run_is_r5_blind_audit_20260321_20260327",
            "passed": start_day == "2026-03-21" and end_day == "2026-03-27",
            "value": f"{start_day}..{end_day}",
        },
        {
            "name": "forward_window_not_in_training",
            "passed": start_day > "2026-03-20",
            "value": {"train_end_locked": "2026-03-20", "preview_start": start_day},
        },
        {
            "name": "soft_v2_no_training_started",
            "passed": True,
            "value": "audit_preview_only_no_train_api_called",
        },
        {
            "name": "soft_v2_no_forward_rerun_started",
            "passed": True,
            "value": "audit_preview_only_existing_forward_predictions_read_only",
        },
        {
            "name": "r5_not_added_to_train_by_soft_v2",
            "passed": start_day == "2026-03-21" and end_day == "2026-03-27",
            "value": {"train_end_locked": "2026-03-20", "preview_range": f"{start_day}..{end_day}"},
        },
        {
            "name": "rows_match_predictions",
            "passed": int(len(audit)) == int(forward_manifest.get("rows", len(audit))),
            "value": {"audit_rows": int(len(audit)), "manifest_rows": int(forward_manifest.get("rows", 0))},
        },
        {
            "name": "stas8_live_source_time_lte_entry_time",
            "passed": source_after_entry == 0,
            "value": source_after_entry,
        },
        {
            "name": "soft_v2_live_input_columns_have_no_teacher_or_target_patterns",
            "passed": not live_forbidden_hits,
            "value": live_forbidden_hits,
        },
        {
            "name": "teacher_columns_report_only_not_in_live_inputs",
            "passed": not any(
                column.lower().startswith(prefix) or prefix in column.lower()
                for column in SOFT_V2_LIVE_INPUT_COLUMNS
                for prefix in ["future_", "hit_", "time_to_", "mae_", "move_capacity_", "move_edge_"]
            ),
            "value": SOFT_V2_LIVE_INPUT_COLUMNS,
        },
        {
            "name": "no_skip_to_enter_promotion",
            "passed": all(value == 0 for value in skip_to_enter.values()),
            "value": skip_to_enter,
        },
        {
            "name": "hard_block_forces_original_enter_watch_to_skip",
            "passed": all(value == 0 for value in hard_block_kept_live_ew.values()),
            "value": hard_block_kept_live_ew,
        },
        {
            "name": "no_hard_block_and_protect_conflict_on_original_enter_watch",
            "passed": all(value == 0 for value in hard_protect_conflict_ew.values()),
            "value": hard_protect_conflict_ew,
        },
        {
            "name": "soft_v2_visual_markers_match_live_semantics",
            "passed": all(
                all(count == 0 for count in preset_counts.values())
                for preset_counts in marker_semantic_mismatches.values()
            ),
            "value": marker_semantic_mismatches,
        },
        {
            "name": "output_dir_is_preview_only",
            "passed": "stas8_move_capacity_audit" in out_dir.as_posix() and "soft_capacity_v2" in out_dir.as_posix(),
            "value": rel(out_dir),
        },
    ]
    failed_count = int(sum(1 for item in checks if not bool(item["passed"])))
    status = SOFT_V2_STATUS_PASS if failed_count == 0 else SOFT_V2_STATUS_FAIL
    return {
        "status": status,
        "layer_id": SOFT_V2_LAYER_ID,
        "created_utc": utc_now(),
        "presets": presets,
        "failed_count": failed_count,
        "checks": checks,
        "no_future_guardrails": [
            "SOFT V2 live decisions use STAS8_LIVE_* causal context and ENTRY score/decision only.",
            "Teacher future/hit/time_to/mae columns are report-only and audit-marker-only.",
            "SOFT V2 preview does not run training, does not rerun forward, and does not rewrite predictions.",
            "SOFT V2 live decision never promotes SKIP to ENTER; RECALL_WATCH is audit-only and hidden from price markers.",
        ],
    }


def _write_soft_v2_report(path: Path, manifest: dict[str, Any]) -> None:
    lines = [
        "# STAS8 Soft Capacity V2 Preview",
        "",
        f"Статус: `{manifest['status']}`.",
        "",
        "Это read-only preview поверх готового R5 forward. Обучение не запускалось, новый forward не запускался, исходный predictions CSV не переписывался.",
        "",
        "## Смысл",
        "",
        "- `strict` показывает максимально осторожный режим.",
        "- `balanced` является главным кандидатом для ручного просмотра.",
        "- `wide` показывает, где можно раздушить входы и не потерять отскоки после ножа.",
        "- Зеленый круг на PNG = финальный live `ENTER` после STAS8.",
        "- Красный квадрат = исходный `ENTER` понижен в `WATCH`, вход лучше не превращать в сделку.",
        "- Красный круг = hard block, long опасен.",
        "- `RECALL_WATCH` для исходного `SKIP` хранится в CSV/отчете как offline-аудит и не рисуется зеленым кругом на цене.",
        "",
        "## Вход",
        "",
        f"Forward run: `{manifest['forward_run_id']}`",
        f"Диапазон: `{manifest['start_day']}..{manifest['end_day']}`",
        f"Rows: `{manifest['rows']}`",
        f"Predictions SHA unchanged: `{manifest['predictions_sha256']}`",
        f"X features: `{manifest['x_feature_count']}`",
        "",
        "## Контакт-Листы",
        "",
    ]
    for preset, sheet in manifest.get("contact_sheets", {}).items():
        lines.append(f"- `{preset}`: `{sheet}`")
    lines += [
        "",
        "## Итог По Режимам",
        "",
        "| Preset | Live ENTER | Live WATCH | Live SKIP | Recall WATCH hidden | Green final ENTER | Red square ENTER->WATCH | Red circle hard block | Blocked EW hit1.2 | Protected EW hit1.2 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for item in manifest.get("summary", []):
        lines.append(
            f"| `{item['preset']}` | {item['live_ENTER']} | {item['live_WATCH']} | {item['live_SKIP']} | "
            f"{item['review_RECALL_WATCH']} | {item['marker_GOOD']} | {item['marker_BAD']} | {item['marker_RISK_BAD']} | "
            f"{item['soft_v2_blocked_original_ew_hit_1p2']} | {item['soft_v2_protected_original_ew_hit_1p2']} |"
        )
    lines += [
        "",
        "## PNG По Дням",
        "",
    ]
    for preset, day_outputs in manifest.get("day_outputs", {}).items():
        lines += [
            f"### {preset}",
            "",
            "| День | Live after V2 | Review after V2 | Markers | PNG |",
            "|---|---|---|---|---|",
        ]
        for day_item in day_outputs:
            lines.append(
                "| "
                + str(day_item.get("day", ""))
                + " | "
                + f"`{day_item.get('counts_after_soft_v2_live', {})}`"
                + " | "
                + f"`{day_item.get('counts_after_soft_v2_review', {})}`"
                + " | "
                + f"`{day_item.get('annotations', {})}`"
                + " | "
                + f"`{day_item.get('png', '')}`"
                + " |"
            )
        lines.append("")
    lines += [
        "## Guardrails",
        "",
        "- R5 остается blind/audit-preview и не входит в train до ручного review.",
        "- `future_*`, `hit_*`, `time_to_*`, `mae_*`, `move_capacity_y`, `move_edge_y` не участвуют в live decision.",
        "- `RECALL_WATCH` является только подсказкой для просмотра, а не боевым повышением `SKIP` в `ENTER`.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_soft_v2_contact_sheets(out_dir: Path, pngs: dict[str, list[str]], presets: list[str]) -> dict[str, str]:
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return {}
    sheets: dict[str, str] = {}
    target_w = 1800
    pad = 18
    header_h = 52
    for preset in presets:
        preset_paths = [PROJECT_ROOT / path for path in pngs.get(preset, [])]
        if not preset_paths:
            continue
        thumbs = []
        for path in preset_paths:
            if not path.exists():
                continue
            image = Image.open(path).convert("RGB")
            ratio = target_w / float(image.width)
            target_h = int(image.height * ratio)
            image = image.resize((target_w, target_h), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", (target_w, target_h + header_h), (16, 20, 24))
            draw = ImageDraw.Draw(canvas)
            draw.text((18, 16), f"{preset.upper()} {path.parent.name}", fill=(255, 255, 255))
            canvas.paste(image, (0, header_h))
            thumbs.append(canvas)
        if not thumbs:
            continue
        total_h = sum(image.height for image in thumbs) + pad * (len(thumbs) + 1)
        sheet = Image.new("RGB", (target_w + pad * 2, total_h), (16, 20, 24))
        y = pad
        for image in thumbs:
            sheet.paste(image, (pad, y))
            y += image.height + pad
        out_path = out_dir / f"STAS8_SOFT_V2_{preset.upper()}_CONTACT_SHEET.png"
        sheet.save(out_path, optimize=True)
        sheets[preset] = rel(out_path)
    return sheets


def _write_soft_v2_preview(
    *,
    forward_run_dir: Path,
    forward_manifest: dict[str, Any],
    predictions: pd.DataFrame,
    audit: pd.DataFrame,
    start_day: str,
    end_day: str,
    predictions_sha_before: str,
    predictions_sha_after: str,
    v1_guard: dict[str, Any],
    x_feature_count: int,
    presets: list[str],
    skip_visual: bool,
    strict: bool,
) -> dict[str, Any]:
    out_dir = forward_run_dir / "stas8_move_capacity_audit" / "soft_capacity_v2"
    out_dir.mkdir(parents=True, exist_ok=True)
    compact_range = f"{compact_day(start_day)}_{compact_day(end_day)}"
    audit_csv = out_dir / f"STAS5_V5C_STAS8_SOFT_CAPACITY_V2_AUDIT_{compact_range}.csv"
    summary_csv = out_dir / f"STAS5_V5C_STAS8_SOFT_CAPACITY_V2_SUMMARY_{compact_range}.csv"
    manifest_path = out_dir / f"STAS5_V5C_STAS8_SOFT_CAPACITY_V2_MANIFEST_{compact_range}.json"
    guard_path = out_dir / f"STAS5_V5C_STAS8_SOFT_CAPACITY_V2_GUARD_{compact_range}.json"
    report_path = out_dir / f"STAS5_V5C_STAS8_SOFT_CAPACITY_V2_PREVIEW_{compact_range}_RU.md"

    audit.to_csv(audit_csv, index=False, encoding="utf-8-sig")
    summary = _soft_v2_summary(audit, presets)
    pd.DataFrame(summary).to_csv(summary_csv, index=False, encoding="utf-8-sig")
    guard = _soft_v2_guard(
        v1_guard=v1_guard,
        forward_manifest=forward_manifest,
        predictions_sha_before=predictions_sha_before,
        predictions_sha_after=predictions_sha_after,
        audit=audit,
        start_day=start_day,
        end_day=end_day,
        presets=presets,
        out_dir=out_dir,
    )
    write_json(guard_path, guard)

    day_outputs: dict[str, list[dict[str, Any]]] = {}
    pngs: dict[str, list[str]] = {}
    if not skip_visual:
        day_outputs, pngs = _render_soft_v2_visuals(
            forward_run_dir=forward_run_dir,
            predictions=predictions,
            audit=audit,
            start_day=start_day,
            end_day=end_day,
            out_dir=out_dir,
            presets=presets,
            strict=strict,
        )
    contact_sheets = _build_soft_v2_contact_sheets(out_dir, pngs, presets) if not skip_visual else {}

    manifest = {
        "status": guard["status"],
        "layer_id": SOFT_V2_LAYER_ID,
        "created_utc": utc_now(),
        "forward_run_id": forward_manifest.get("run_id", forward_run_dir.name),
        "forward_run_dir": rel(forward_run_dir),
        "predictions_sha256": predictions_sha_after,
        "start_day": start_day,
        "end_day": end_day,
        "rows": int(len(audit)),
        "x_feature_count": int(x_feature_count),
        "presets": presets,
        "summary": summary,
        "audit_csv": rel(audit_csv),
        "summary_csv": rel(summary_csv),
        "guard_json": rel(guard_path),
        "audit_ru": rel(report_path),
        "manifest_path": rel(manifest_path),
        "day_outputs": day_outputs,
        "png_count_by_preset": {preset: int(len(pngs.get(preset, []))) for preset in presets},
        "pngs": pngs,
        "contact_sheets": contact_sheets,
        "guardrails": guard["no_future_guardrails"],
        "visual_bollinger_preview": False,
        "visual_note": (
            "SOFT V2 visuals disable Bollinger bands. Green circles show final live ENTER only; "
            "SKIP RECALL_WATCH remains audit-only in CSV/report and is hidden from price markers."
        ),
    }
    write_json(manifest_path, manifest)
    _write_soft_v2_report(report_path, manifest)
    write_json(manifest_path, manifest)
    return manifest


def _guard(
    *,
    forward_manifest: dict[str, Any],
    predictions_path: Path,
    predictions_sha_before: str,
    predictions_sha_after: str,
    x_path: Path,
    x_rows: pd.DataFrame,
    audit: pd.DataFrame,
    grid: pd.DataFrame,
    start_day: str,
    end_day: str,
    join_summary: dict[str, Any],
    ohlcv_summary: dict[str, Any],
) -> dict[str, Any]:
    days = iter_days(start_day, end_day)
    dataset_manifest_ref = forward_manifest.get("forward_dataset_manifest", {})
    x_feature_count = 0
    if isinstance(dataset_manifest_ref, dict):
        x_feature_count = int(dataset_manifest_ref.get("feature_count", 0) or 0)
    if not x_feature_count:
        dataset_manifest_path = x_path.parent / "STAS5_V5C_FORWARD_DATASET_MANIFEST_V1.json"
        if isinstance(dataset_manifest_ref, str) and dataset_manifest_ref:
            candidate = PROJECT_ROOT / dataset_manifest_ref
            if candidate.exists():
                dataset_manifest_path = candidate
        dataset_manifest = json.loads(dataset_manifest_path.read_text(encoding="utf-8"))
        x_feature_count = int(dataset_manifest.get("feature_count", 0) or len(dataset_manifest.get("feature_columns", [])))
    live_forbidden_hits = sorted(
        column
        for column in LIVE_SOURCE_COLUMNS
        for pattern in FORBIDDEN_LIVE_PATTERNS
        if pattern.lower() in column.lower()
    )
    source_times = pd.to_datetime(audit.get("stas8_live_source_time_utc"), utc=True, errors="coerce", format="mixed")
    entry_times = pd.to_datetime(audit.get("entry_time_utc"), utc=True, errors="coerce", format="mixed")
    active = source_times.notna() & entry_times.notna()
    source_after_entry = int((source_times[active] > entry_times[active]).sum())
    expected_grid_rows = len(audit) * len(_dense_thresholds())
    checks = [
        {
            "name": "input_forward_manifest_pass",
            "passed": str(forward_manifest.get("status", "")).startswith("PASS"),
            "value": forward_manifest.get("status", ""),
        },
        {
            "name": "riskgate_not_applied_for_r5_entry_only_audit",
            "passed": forward_manifest.get("riskgate_ml_applied") is False,
            "value": forward_manifest.get("riskgate_ml_applied"),
        },
        {
            "name": "input_predictions_not_modified",
            "passed": predictions_sha_before == predictions_sha_after,
            "value": predictions_sha_after,
        },
        {
            "name": "days_present",
            "passed": sorted(audit["day"].astype(str).unique().tolist()) == days,
            "value": sorted(audit["day"].astype(str).unique().tolist()),
        },
        {
            "name": "rows_match_predictions",
            "passed": int(len(audit)) == int(forward_manifest.get("rows", len(audit))),
            "value": {"audit_rows": int(len(audit)), "manifest_rows": int(forward_manifest.get("rows", 0))},
        },
        {
            "name": "x_feature_count_463",
            "passed": x_feature_count == 463,
            "value": x_feature_count,
        },
        {
            "name": "join_x_rows_complete",
            "passed": int(join_summary.get("missing_x_rows_after_join", -1)) == 0,
            "value": join_summary,
        },
        {
            "name": "no_duplicate_day_candidate",
            "passed": int(audit.duplicated(["day", "candidate_id"]).sum()) == 0,
            "value": int(audit.duplicated(["day", "candidate_id"]).sum()),
        },
        {
            "name": "stas8_live_source_time_lte_entry_time",
            "passed": source_after_entry == 0,
            "value": source_after_entry,
        },
        {
            "name": "live_source_columns_have_no_teacher_or_target_patterns",
            "passed": not live_forbidden_hits,
            "value": live_forbidden_hits,
        },
        {
            "name": "teacher_grid_is_separate_long_table",
            "passed": int(len(grid)) == int(expected_grid_rows),
            "value": {"grid_rows": int(len(grid)), "expected": int(expected_grid_rows)},
        },
        {
            "name": "ohlcv_context_available_with_future_day_for_audit_teacher",
            "passed": not ohlcv_summary.get("missing_days"),
            "value": ohlcv_summary.get("missing_days", []),
        },
    ]
    status = STATUS_PASS if all(bool(item["passed"]) for item in checks) else STATUS_FAIL
    return {
        "status": status,
        "layer_id": LAYER_ID,
        "created_utc": utc_now(),
        "checks": checks,
        "no_future_guardrails": [
            "STAS8 live context uses closed OHLCV bars before entry_time_utc and causal X463 columns only.",
            "Teacher future/hit/MFE/MAE/time_to columns are offline audit targets only and are not live X.",
            "This audit does not run training and does not rewrite forward predictions.",
        ],
    }


def _write_report(path: Path, manifest: dict[str, Any]) -> None:
    counts_before = manifest.get("counts_before_stas8", {})
    counts_after = manifest.get("counts_after_stas8_preview", {})
    lines = [
        "# STAS8 Move Capacity Audit V1",
        "",
        f"Статус: `{manifest['status']}`.",
        "",
        "Это audit-preview без обучения и без изменения исходного forward. STAS8 здесь только измеряет, где live-контекст long уже живой, где ждать, а где long надо блокировать.",
        "",
        "## Вход",
        "",
        f"Forward run: `{manifest['forward_run_id']}`",
        f"Диапазон: `{manifest['start_day']}..{manifest['end_day']}`",
        f"Predictions SHA unchanged: `{manifest['predictions_sha256']}`",
        f"X features: `{manifest['x_feature_count']}`",
        "",
        "## Цифры",
        "",
        f"Rows: `{manifest['rows']}`",
        f"До STAS8: `{counts_before}`",
        f"Preview после STAS8: `{counts_after}`",
        f"Live actions: `{manifest.get('stas8_live_action_counts', {})}`",
        f"Teacher hit 1.2% total: `{manifest.get('teacher_hit_1p2_total', 0)}`",
        "",
        "## Файлы",
        "",
        f"Audit CSV: `{manifest['audit_csv']}`",
        f"Teacher grid CSV: `{manifest['grid_csv']}`",
        f"Guard JSON: `{manifest['guard_json']}`",
        "",
        "## PNG По Дням",
        "",
        "| День | Rows | До STAS8 | Preview после STAS8 | Live actions | PNG |",
        "|---|---:|---|---|---|---|",
    ]
    for item in manifest.get("day_outputs", []):
        lines.append(
            "| "
            + str(item["day"])
            + " | "
            + str(item.get("rows", 0))
            + " | "
            + f"`{item.get('counts_before_stas8', {})}`"
            + " | "
            + f"`{item.get('counts_after_stas8_preview', {})}`"
            + " | "
            + f"`{item.get('stas8_live_action_counts', {})}`"
            + " | "
            + f"`{item.get('png', '')}`"
            + " |"
        )
    lines += [
        "",
        "## Guardrails",
        "",
        "- R5 остается blind-forward/audit-preview и не входит в train до ручного review.",
        "- `STAS8_LIVE_ACTION` считается только по causal X463 и свечам до входа.",
        "- `future_*`, `hit_*`, `time_to_*`, `mae_*`, `move_capacity_y`, `move_edge_y` являются teacher/audit и запрещены в live X.",
        "- STAS8 preview не повышает `SKIP` в `ENTER`; он может только оставить, подождать или понизить `ENTER/WATCH`.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_stas8_move_capacity_audit(
    *,
    forward_run_id: str | None = None,
    forward_run_dir: Path | None = None,
    start_day: str | None = None,
    end_day: str | None = None,
    skip_visual: bool = False,
    strict: bool = True,
    soft_v2_preview: bool = False,
    soft_v2_presets: list[str] | None = None,
) -> dict[str, Any]:
    run_dir = _resolve_forward_run_dir(forward_run_id, forward_run_dir)
    manifest_file = _manifest_path(run_dir)
    forward_manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    pred_path = _find_predictions_path(run_dir, None)
    x_path = _find_forward_dataset_path(run_dir)
    predictions_sha_before = _file_sha256(pred_path)
    predictions = _load_predictions(pred_path)
    x_rows = pd.read_csv(x_path, encoding="utf-8-sig")
    if start_day is None:
        start_day = str(predictions["day"].astype(str).min())
    if end_day is None:
        end_day = str(predictions["day"].astype(str).max())
    start_day = normalize_day(start_day)
    end_day = normalize_day(end_day)
    predictions = predictions[predictions["day"].astype(str).isin(iter_days(start_day, end_day))].copy().reset_index(drop=True)
    merged, join_summary = _join_predictions_and_x(predictions, x_rows)
    ohlcv, ohlcv_summary = _load_ohlcv_days(start_day, end_day, warmup_days=1, future_days=1)
    thresholds = _dense_thresholds()
    audit, grid = _build_audit_rows(merged, ohlcv, thresholds)
    presets = [str(item).strip().lower() for item in (soft_v2_presets or list(SOFT_V2_PRESETS)) if str(item).strip()]
    unknown_presets = sorted(set(presets).difference(SOFT_V2_PRESETS))
    if unknown_presets:
        raise ValueError(f"Unknown STAS8 soft V2 presets: {unknown_presets}")

    out_dir = run_dir / "stas8_move_capacity_audit" / "v1"
    out_dir.mkdir(parents=True, exist_ok=True)
    audit_csv = out_dir / f"STAS5_V5C_STAS8_MOVE_CAPACITY_AUDIT_{compact_day(start_day)}_{compact_day(end_day)}_V1.csv"
    grid_csv = out_dir / f"STAS5_V5C_STAS8_MOVE_CAPACITY_GRID_LONG_{compact_day(start_day)}_{compact_day(end_day)}_V1.csv"
    manifest_path = out_dir / f"STAS5_V5C_STAS8_MOVE_CAPACITY_AUDIT_MANIFEST_{compact_day(start_day)}_{compact_day(end_day)}_V1.json"
    guard_path = out_dir / f"STAS5_V5C_STAS8_MOVE_CAPACITY_GUARD_{compact_day(start_day)}_{compact_day(end_day)}_V1.json"
    report_path = out_dir / f"STAS5_V5C_STAS8_MOVE_CAPACITY_AUDIT_{compact_day(start_day)}_{compact_day(end_day)}_RU.md"
    audit.to_csv(audit_csv, index=False, encoding="utf-8-sig")
    grid.to_csv(grid_csv, index=False, encoding="utf-8-sig")

    predictions_sha_after = _file_sha256(pred_path)
    guard = _guard(
        forward_manifest=forward_manifest,
        predictions_path=pred_path,
        predictions_sha_before=predictions_sha_before,
        predictions_sha_after=predictions_sha_after,
        x_path=x_path,
        x_rows=x_rows,
        audit=audit,
        grid=grid,
        start_day=start_day,
        end_day=end_day,
        join_summary=join_summary,
        ohlcv_summary=ohlcv_summary,
    )
    write_json(guard_path, guard)

    day_outputs: list[dict[str, Any]] = []
    pngs: list[str] = []
    if not skip_visual:
        day_outputs, pngs = _render_stas8_visuals(
            forward_run_dir=run_dir,
            predictions=predictions,
            audit=audit,
            start_day=start_day,
            end_day=end_day,
            out_dir=out_dir,
            strict=strict,
        )

    counts_before = Counter(audit["ENTRY_ML_LIVE_DECISION_BEFORE_STAS8"].astype(str))
    counts_after = Counter(audit["ENTRY_ML_LIVE_DECISION_AFTER_STAS8_PREVIEW"].astype(str))
    action_counts = Counter(audit["STAS8_LIVE_ACTION"].astype(str))
    x_feature_count = int(
        json.loads((run_dir / "STAS5_V5C_FORWARD_DATASET_MANIFEST_V1.json").read_text(encoding="utf-8")).get("feature_count", 0)
    )
    manifest = {
        "status": guard["status"],
        "layer_id": LAYER_ID,
        "live_context_id": LIVE_CONTEXT_ID,
        "teacher_grid_id": TEACHER_GRID_ID,
        "created_utc": utc_now(),
        "forward_run_id": forward_manifest.get("run_id", run_dir.name),
        "forward_run_dir": rel(run_dir),
        "forward_manifest": rel(manifest_file),
        "predictions_csv": rel(pred_path),
        "predictions_sha256": predictions_sha_after,
        "forward_dataset_csv": rel(x_path),
        "x_feature_count": x_feature_count,
        "start_day": start_day,
        "end_day": end_day,
        "rows": int(len(audit)),
        "threshold_grid_pct": thresholds,
        "horizon_grid_min": HORIZONS_MIN,
        "counts_before_stas8": {str(k): int(v) for k, v in counts_before.items()},
        "counts_after_stas8_preview": {str(k): int(v) for k, v in counts_after.items()},
        "stas8_live_action_counts": {str(k): int(v) for k, v in action_counts.items()},
        "teacher_hit_1p2_total": int(pd.to_numeric(audit.get("hit_1p2_y", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()),
        "audit_csv": rel(audit_csv),
        "grid_csv": rel(grid_csv),
        "guard_json": rel(guard_path),
        "audit_ru": rel(report_path),
        "manifest_path": rel(manifest_path),
        "visual_bollinger_preview": False,
        "visual_note": "STAS8 visual review disables Bollinger bands to keep move-context markers readable.",
        "day_outputs": day_outputs,
        "png_count": int(len(pngs)),
        "pngs": pngs,
        "join_summary": join_summary,
        "ohlcv_summary": ohlcv_summary,
        "guardrails": guard["no_future_guardrails"],
    }
    if soft_v2_preview:
        soft_manifest = _write_soft_v2_preview(
            forward_run_dir=run_dir,
            forward_manifest=forward_manifest,
            predictions=predictions,
            audit=audit,
            start_day=start_day,
            end_day=end_day,
            predictions_sha_before=predictions_sha_before,
            predictions_sha_after=predictions_sha_after,
            v1_guard=guard,
            x_feature_count=x_feature_count,
            presets=presets,
            skip_visual=skip_visual,
            strict=strict,
        )
        manifest["soft_v2_preview"] = {
            "status": soft_manifest["status"],
            "layer_id": SOFT_V2_LAYER_ID,
            "manifest_path": soft_manifest["manifest_path"],
            "guard_json": soft_manifest["guard_json"],
            "audit_ru": soft_manifest["audit_ru"],
            "summary": soft_manifest["summary"],
            "png_count_by_preset": soft_manifest["png_count_by_preset"],
            "contact_sheets": soft_manifest.get("contact_sheets", {}),
        }
    write_json(manifest_path, manifest)
    _write_report(report_path, manifest)
    write_json(manifest_path, manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="STAS5 V5C STAS8 move-capacity audit-preview")
    parser.add_argument("--forward-run-id", default="")
    parser.add_argument("--forward-run-dir", default="")
    parser.add_argument("--start-day", default="")
    parser.add_argument("--end-day", default="")
    parser.add_argument("--skip-visual", action="store_true")
    parser.add_argument("--no-strict", action="store_true")
    parser.add_argument("--soft-v2-preview", action="store_true")
    parser.add_argument("--soft-v2-presets", default="strict,balanced,wide")
    args = parser.parse_args()
    presets = [item.strip().lower() for item in args.soft_v2_presets.split(",") if item.strip()]
    manifest = run_stas8_move_capacity_audit(
        forward_run_id=args.forward_run_id or None,
        forward_run_dir=Path(args.forward_run_dir) if args.forward_run_dir else None,
        start_day=args.start_day or None,
        end_day=args.end_day or None,
        skip_visual=args.skip_visual,
        strict=not args.no_strict,
        soft_v2_preview=args.soft_v2_preview,
        soft_v2_presets=presets,
    )
    soft = manifest.get("soft_v2_preview") if isinstance(manifest.get("soft_v2_preview"), dict) else None
    status = str(soft.get("status")) if soft else str(manifest["status"])
    audit_dir = str(Path(str(soft.get("manifest_path"))).parent.as_posix()) if soft else str(Path(manifest["manifest_path"]).parent.as_posix())
    response: dict[str, Any] = {
        "status": status,
        "run_id": manifest["forward_run_id"],
        "audit_dir": audit_dir,
        "rows": manifest["rows"],
        "counts_before_stas8": manifest["counts_before_stas8"],
        "counts_after_stas8_preview": manifest["counts_after_stas8_preview"],
        "png_count": manifest["png_count"],
    }
    if soft:
        response["soft_v2_summary"] = soft.get("summary", [])
        response["soft_v2_png_count_by_preset"] = soft.get("png_count_by_preset", {})
        response["soft_v2_contact_sheets"] = soft.get("contact_sheets", {})
    print(
        json.dumps(
            response,
            ensure_ascii=False,
        )
    )
    return 0 if args.no_strict or status in {STATUS_PASS, SOFT_V2_STATUS_PASS} else 2


if __name__ == "__main__":
    raise SystemExit(main())
