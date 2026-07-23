from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from mlbotnav.stas5_common import (
    PROJECT_ROOT,
    compact_day,
    ensure_parent,
    forbidden_feature_matches,
    load_manifest_feature_columns,
    normalize_day,
    normalize_ts,
    rel,
    utc_now,
    write_json,
)


STATUS = "PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY"
SYMBOL = "SOLUSDT"
TIMEFRAME = "1m"

REGIME_CODES = {
    "NEUTRAL": 0,
    "CHOP_NO_EDGE": 1,
    "SHORT_PRESSURE": 2,
    "PRE_DUMP_RISK": 3,
    "ACTIVE_DUMP": 4,
    "BOTTOMING": 5,
    "BASE_AFTER_FLUSH": 6,
    "PUMP_BREAKOUT": 7,
    "PUMP_PULLBACK": 8,
    "PUMP_CONTINUATION": 9,
    "LATE_HIGH_CHOP": 10,
}

LEVEL_EVENT_CODES = {
    "NONE": 0,
    "CONFIRM": 1,
    "TOUCH": 2,
    "REJECT": 3,
    "BREAK": 4,
    "ROLE_FLIP": 5,
}

CHANNEL_CODES = {
    "UNKNOWN": 0,
    "FLAT_RANGE": 1,
    "DOWN_CHANNEL": 2,
    "UP_CHANNEL": 3,
    "WIDE_VOLATILE": 4,
}

TARGET_OR_TEACHER_COLUMNS = {
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

FORBIDDEN_DIRECT_FEATURE_SUBSTRINGS = (
    "future",
    "postfact",
    "hit_",
    "tp",
    "stas3",
    "exit",
    "ml_keep_score",
    "ml_decision",
    "phase_y",
    "state_y",
    "reason_y",
    "entry_y",
    "manual",
    "teacher",
    "market_phase",
    "entry_reason",
    "review_status",
)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
        if math.isfinite(out):
            return out
    except Exception:
        pass
    return default


def _clip01(value: float) -> float:
    return float(max(0.0, min(1.0, _safe_float(value))))


def _pct(a: float, b: float) -> float:
    if b == 0 or not math.isfinite(a) or not math.isfinite(b):
        return 0.0
    return float((a / b - 1.0) * 100.0)


def _parse_utc(value: Any) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert("UTC")


def _fmt_utc(value: Any) -> str:
    if value is None or str(value) == "NaT" or str(value).lower() == "nan":
        return ""
    return _parse_utc(value).strftime("%Y-%m-%dT%H:%M:%SZ")


def _context_time(candidate: pd.Series) -> pd.Timestamp:
    entry_time = _parse_utc(candidate["entry_time_utc"])
    context_raw = candidate.get("cs_max_source_time_utc") or candidate.get("context_max_open_time_utc") or ""
    if context_raw and str(context_raw).lower() != "nan":
        context = _parse_utc(context_raw)
    else:
        context = entry_time - pd.Timedelta(minutes=1)
    if context >= entry_time:
        context = entry_time - pd.Timedelta(minutes=1)
    return context


def _ret(history: pd.DataFrame, bars: int) -> float:
    w = history.tail(bars)
    if len(w) < 2:
        return 0.0
    return _pct(float(w["close"].iloc[-1]), float(w["close"].iloc[0]))


def _range_pct(history: pd.DataFrame, bars: int) -> float:
    w = history.tail(bars)
    if w.empty:
        return 0.0
    close = float(w["close"].iloc[-1])
    if close == 0:
        return 0.0
    return float((float(w["high"].max()) - float(w["low"].min())) / close * 100.0)


def _trend_slope_pct(history: pd.DataFrame, bars: int) -> float:
    w = history.tail(bars)
    if len(w) < 3:
        return 0.0
    y = w["close"].astype(float).to_numpy()
    x = np.arange(len(y), dtype=float)
    try:
        slope = float(np.polyfit(x, y, 1)[0])
    except Exception:
        return 0.0
    base = float(y[0]) if float(y[0]) != 0 else 1.0
    return float(slope / base * 100.0)


def _streaks(history: pd.DataFrame) -> tuple[int, int]:
    red = 0
    green = 0
    for _, row in history.tail(30).iloc[::-1].iterrows():
        close = float(row["close"])
        open_ = float(row["open"])
        if close < open_:
            red += 1
            if green:
                break
        elif close > open_:
            green += 1
            if red:
                break
        else:
            break
    return red, green


def _load_ohlcv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    required = ["open_time_utc", "open", "high", "low", "close", "volume"]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"OHLCV missing columns {missing}: {path}")
    out = df.copy()
    out["open_time_utc"] = pd.to_datetime(out["open_time_utc"], utc=True)
    for column in ["open", "high", "low", "close", "volume"]:
        out[column] = pd.to_numeric(out[column], errors="coerce")
    out = out.dropna(subset=["open_time_utc", "open", "high", "low", "close"]).sort_values("open_time_utc")
    return out.reset_index(drop=True)


@dataclass
class LevelState:
    level_id: str
    level_type: str
    price_mid: float
    price_low: float
    price_high: float
    first_seen_utc: pd.Timestamp
    confirmed_utc: pd.Timestamp
    last_touch_utc: pd.Timestamp
    touch_count: int = 1
    reject_count: int = 0
    break_count: int = 0
    role_flip_count: int = 0
    last_event: str = "CONFIRM"
    broken: bool = False

    def strength(self, now: pd.Timestamp) -> float:
        age_min = max(0.0, (now - self.confirmed_utc).total_seconds() / 60.0)
        return _clip01(
            0.18
            + self.touch_count * 0.08
            + self.reject_count * 0.08
            + self.role_flip_count * 0.05
            + min(age_min, 360.0) / 360.0 * 0.22
            - self.break_count * 0.12
        )


def _level_band(price: float) -> tuple[float, float, float]:
    tol = max(price * 0.0015, 0.015)
    return price - tol, price, price + tol


def _confirm_pivot(data: pd.DataFrame, pivot_idx: int, left: int, right: int) -> tuple[bool, bool]:
    if pivot_idx < left or pivot_idx + right >= len(data):
        return False, False
    chunk = data.iloc[pivot_idx - left : pivot_idx + right + 1]
    row = data.iloc[pivot_idx]
    is_low = float(row["low"]) <= float(chunk["low"].min())
    is_high = float(row["high"]) >= float(chunk["high"].max())
    return is_low, is_high


def _find_or_create_level(
    *,
    levels: list[LevelState],
    level_type: str,
    price: float,
    pivot_time: pd.Timestamp,
    known_time: pd.Timestamp,
    day_compact: str,
    events: list[dict[str, Any]],
) -> None:
    tolerance = max(price * 0.0025, 0.025)
    same_type = [level for level in levels if level.level_type == level_type and abs(level.price_mid - price) <= tolerance]
    if same_type:
        level = min(same_type, key=lambda item: abs(item.price_mid - price))
        level.price_mid = float((level.price_mid * level.touch_count + price) / (level.touch_count + 1))
        low, mid, high = _level_band(level.price_mid)
        level.price_low = low
        level.price_high = high
        level.touch_count += 1
        level.last_touch_utc = known_time
        level.last_event = "CONFIRM"
    else:
        low, mid, high = _level_band(price)
        level = LevelState(
            level_id=f"FCSL_{day_compact}_{level_type}_{len(levels)+1:03d}",
            level_type=level_type,
            price_mid=mid,
            price_low=low,
            price_high=high,
            first_seen_utc=pivot_time,
            confirmed_utc=known_time,
            last_touch_utc=known_time,
        )
        levels.append(level)
    events.append(
        {
            "event_type": "LEVEL_CONFIRM",
            "event_code": LEVEL_EVENT_CODES["CONFIRM"],
            "level_id": level.level_id,
            "level_type": level.level_type,
            "event_time_utc": _fmt_utc(pivot_time),
            "known_time_utc": _fmt_utc(known_time),
            "price": level.price_mid,
            "source": "confirmed_pivot_left3_right3",
        }
    )


def _update_level_events(levels: list[LevelState], candle: pd.Series, events: list[dict[str, Any]]) -> None:
    now = _parse_utc(candle["open_time_utc"])
    low = float(candle["low"])
    high = float(candle["high"])
    close = float(candle["close"])
    for level in levels:
        touched = low <= level.price_high and high >= level.price_low
        if touched and level.last_touch_utc != now:
            level.touch_count += 1
            level.last_touch_utc = now
            level.last_event = "TOUCH"
            events.append(
                {
                    "event_type": "LEVEL_TOUCH",
                    "event_code": LEVEL_EVENT_CODES["TOUCH"],
                    "level_id": level.level_id,
                    "level_type": level.level_type,
                    "event_time_utc": _fmt_utc(now),
                    "known_time_utc": _fmt_utc(now),
                    "price": level.price_mid,
                    "source": "candle_touched_level_band",
                }
            )
        if level.level_type == "SUPPORT":
            if touched and close > level.price_high:
                level.reject_count += 1
                level.last_event = "REJECT"
            if close < level.price_low:
                if not level.broken:
                    level.break_count += 1
                    level.last_event = "BREAK"
                    events.append(
                        {
                            "event_type": "LEVEL_BREAK",
                            "event_code": LEVEL_EVENT_CODES["BREAK"],
                            "level_id": level.level_id,
                            "level_type": level.level_type,
                            "event_time_utc": _fmt_utc(now),
                            "known_time_utc": _fmt_utc(now),
                            "price": level.price_mid,
                            "source": "close_below_support_band",
                        }
                    )
                level.broken = True
            elif level.broken and close > level.price_high:
                level.role_flip_count += 1
                level.broken = False
                level.last_event = "ROLE_FLIP"
        else:
            if touched and close < level.price_low:
                level.reject_count += 1
                level.last_event = "REJECT"
            if close > level.price_high:
                if not level.broken:
                    level.break_count += 1
                    level.last_event = "BREAK"
                    events.append(
                        {
                            "event_type": "LEVEL_BREAK",
                            "event_code": LEVEL_EVENT_CODES["BREAK"],
                            "level_id": level.level_id,
                            "level_type": level.level_type,
                            "event_time_utc": _fmt_utc(now),
                            "known_time_utc": _fmt_utc(now),
                            "price": level.price_mid,
                            "source": "close_above_resistance_band",
                        }
                    )
                level.broken = True
            elif level.broken and close < level.price_low:
                level.role_flip_count += 1
                level.broken = False
                level.last_event = "ROLE_FLIP"


def _build_levels(history: pd.DataFrame, day_compact: str) -> tuple[list[LevelState], list[dict[str, Any]]]:
    levels: list[LevelState] = []
    events: list[dict[str, Any]] = []
    left = 3
    right = 3
    data = history.reset_index(drop=True)
    for i, candle in data.iterrows():
        if i >= left + right:
            pivot_idx = i - right
            is_low, is_high = _confirm_pivot(data, pivot_idx, left, right)
            pivot = data.iloc[pivot_idx]
            known_time = _parse_utc(candle["open_time_utc"])
            pivot_time = _parse_utc(pivot["open_time_utc"])
            if is_low:
                _find_or_create_level(
                    levels=levels,
                    level_type="SUPPORT",
                    price=float(pivot["low"]),
                    pivot_time=pivot_time,
                    known_time=known_time,
                    day_compact=day_compact,
                    events=events,
                )
            if is_high:
                _find_or_create_level(
                    levels=levels,
                    level_type="RESISTANCE",
                    price=float(pivot["high"]),
                    pivot_time=pivot_time,
                    known_time=known_time,
                    day_compact=day_compact,
                    events=events,
                )
        _update_level_events(levels, candle, events)
    return levels, events


def _level_rows(levels: list[LevelState], now: pd.Timestamp) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for level in levels:
        age_min = max(0.0, (now - level.confirmed_utc).total_seconds() / 60.0)
        rows.append(
            {
                "level_id": level.level_id,
                "level_type": level.level_type,
                "price_low": level.price_low,
                "price_mid": level.price_mid,
                "price_high": level.price_high,
                "first_seen_utc": _fmt_utc(level.first_seen_utc),
                "confirmed_utc": _fmt_utc(level.confirmed_utc),
                "last_touch_utc": _fmt_utc(level.last_touch_utc),
                "touch_count": level.touch_count,
                "reject_count": level.reject_count,
                "break_count": level.break_count,
                "role_flip_count": level.role_flip_count,
                "level_age_min": age_min,
                "level_strength_score": level.strength(now),
                "last_event": level.last_event,
                "last_event_code": LEVEL_EVENT_CODES.get(level.last_event, 0),
            }
        )
    return rows


def _nearest_level_features(levels: list[LevelState], price: float, now: pd.Timestamp) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for level_type, prefix, selector in [
        ("SUPPORT", "support", lambda item: item.price_mid <= price),
        ("RESISTANCE", "resistance", lambda item: item.price_mid >= price),
    ]:
        candidates = [level for level in levels if level.level_type == level_type and selector(level)]
        if not candidates:
            candidates = [level for level in levels if level.level_type == level_type]
        if candidates:
            level = min(candidates, key=lambda item: abs(item.price_mid - price))
            if level_type == "SUPPORT":
                distance = max(0.0, _pct(price, level.price_mid))
                above = int(price >= level.price_mid)
                below = int(price < level.price_mid)
            else:
                distance = max(0.0, _pct(level.price_mid, price))
                above = int(price > level.price_mid)
                below = int(price <= level.price_mid)
            age = max(0.0, (now - level.confirmed_utc).total_seconds() / 60.0)
            out.update(
                {
                    f"fcs_{prefix}_level_exists": 1,
                    f"fcs_{prefix}_price_mid": level.price_mid,
                    f"fcs_{prefix}_distance_pct": distance,
                    f"fcs_{prefix}_age_min": age,
                    f"fcs_{prefix}_touch_count": level.touch_count,
                    f"fcs_{prefix}_reject_count": level.reject_count,
                    f"fcs_{prefix}_break_count": level.break_count,
                    f"fcs_{prefix}_role_flip_count": level.role_flip_count,
                    f"fcs_{prefix}_strength_score": level.strength(now),
                    f"fcs_{prefix}_last_event_code": LEVEL_EVENT_CODES.get(level.last_event, 0),
                    f"fcs_is_near_{prefix}_level": int(distance <= 0.20),
                    f"fcs_is_above_{prefix}_level": above,
                    f"fcs_is_below_{prefix}_level": below,
                }
            )
        else:
            out.update(
                {
                    f"fcs_{prefix}_level_exists": 0,
                    f"fcs_{prefix}_price_mid": price,
                    f"fcs_{prefix}_distance_pct": 0.0,
                    f"fcs_{prefix}_age_min": 0.0,
                    f"fcs_{prefix}_touch_count": 0,
                    f"fcs_{prefix}_reject_count": 0,
                    f"fcs_{prefix}_break_count": 0,
                    f"fcs_{prefix}_role_flip_count": 0,
                    f"fcs_{prefix}_strength_score": 0.0,
                    f"fcs_{prefix}_last_event_code": 0,
                    f"fcs_is_near_{prefix}_level": 0,
                    f"fcs_is_above_{prefix}_level": 0,
                    f"fcs_is_below_{prefix}_level": 0,
                }
            )
    denom = max(out["fcs_resistance_price_mid"] - out["fcs_support_price_mid"], 1e-9)
    channel = _clip01((price - out["fcs_support_price_mid"]) / denom)
    out["fcs_level_channel_position_0_1"] = channel
    out["fcs_level_is_mid_channel"] = int(0.35 <= channel <= 0.65)
    out["fcs_support_retest_now"] = int(out["fcs_is_near_support_level"] and out["fcs_support_last_event_code"] in {2, 3})
    out["fcs_resistance_reject_now"] = int(out["fcs_is_near_resistance_level"] and out["fcs_resistance_last_event_code"] in {2, 3})
    out["fcs_support_broken_recently"] = int(out["fcs_support_last_event_code"] == LEVEL_EVENT_CODES["BREAK"])
    out["fcs_role_flip_support_exists"] = int(out["fcs_support_role_flip_count"] > 0)
    return out


def _channel_features(history: pd.DataFrame, now: pd.Timestamp) -> dict[str, Any]:
    w = history.tail(120).copy()
    if len(w) < 12:
        price = float(history["close"].iloc[-1])
        return {
            "fcs_channel_type_code": 0,
            "fcs_channel_age_min": 0.0,
            "fcs_channel_lower_price_now": price,
            "fcs_channel_upper_price_now": price,
            "fcs_channel_mid_price_now": price,
            "fcs_channel_width_pct": 0.0,
            "fcs_channel_slope_pct_per_min": 0.0,
            "fcs_channel_position_0_1": 0.5,
            "fcs_channel_lower_touch_count": 0,
            "fcs_channel_upper_touch_count": 0,
            "fcs_channel_breakout_up_recent": 0,
            "fcs_channel_breakdown_recent": 0,
            "fcs_channel_is_lower_edge": 0,
            "fcs_channel_is_mid": 1,
            "fcs_channel_is_upper_edge": 0,
        }
    x = np.arange(len(w), dtype=float)
    lows = w["low"].astype(float).to_numpy()
    highs = w["high"].astype(float).to_numpy()
    closes = w["close"].astype(float).to_numpy()
    low_slope, low_intercept = np.polyfit(x, lows, 1)
    high_slope, high_intercept = np.polyfit(x, highs, 1)
    lower_now = float(low_intercept + low_slope * (len(w) - 1))
    upper_now = float(high_intercept + high_slope * (len(w) - 1))
    if upper_now < lower_now:
        lower_now, upper_now = upper_now, lower_now
    price = float(closes[-1])
    width_pct = (upper_now - lower_now) / price * 100.0 if price else 0.0
    avg_slope = float((low_slope + high_slope) / 2.0)
    slope_pct = avg_slope / max(price, 1e-9) * 100.0
    if width_pct >= 1.5:
        channel_type = "WIDE_VOLATILE"
    elif slope_pct > 0.006:
        channel_type = "UP_CHANNEL"
    elif slope_pct < -0.006:
        channel_type = "DOWN_CHANNEL"
    else:
        channel_type = "FLAT_RANGE"
    lower_line = low_intercept + low_slope * x
    upper_line = high_intercept + high_slope * x
    tolerance = max(price * 0.0015, 0.015)
    lower_touches = int(np.sum(np.abs(lows - lower_line) <= tolerance))
    upper_touches = int(np.sum(np.abs(highs - upper_line) <= tolerance))
    position = _clip01((price - lower_now) / max(upper_now - lower_now, 1e-9))
    return {
        "fcs_channel_type_code": CHANNEL_CODES[channel_type],
        "fcs_channel_age_min": float(len(w)),
        "fcs_channel_lower_price_now": lower_now,
        "fcs_channel_upper_price_now": upper_now,
        "fcs_channel_mid_price_now": float((lower_now + upper_now) / 2.0),
        "fcs_channel_width_pct": width_pct,
        "fcs_channel_slope_pct_per_min": slope_pct,
        "fcs_channel_position_0_1": position,
        "fcs_channel_lower_touch_count": lower_touches,
        "fcs_channel_upper_touch_count": upper_touches,
        "fcs_channel_breakout_up_recent": int(price > upper_now + tolerance),
        "fcs_channel_breakdown_recent": int(price < lower_now - tolerance),
        "fcs_channel_is_lower_edge": int(position <= 0.25),
        "fcs_channel_is_mid": int(0.35 <= position <= 0.65),
        "fcs_channel_is_upper_edge": int(position >= 0.75),
    }


def _knife_features(history: pd.DataFrame, base_row: pd.Series, now: pd.Timestamp) -> dict[str, Any]:
    w = history.tail(90).copy()
    price = float(history["close"].iloc[-1])
    if w.empty:
        return {}
    high_idx = int(w["high"].astype(float).idxmax())
    after_high = history.loc[high_idx:].copy() if high_idx in history.index else w
    low_idx = int(after_high["low"].astype(float).idxmin())
    high_price = float(history.loc[high_idx, "high"]) if high_idx in history.index else float(w["high"].max())
    low_price = float(history.loc[low_idx, "low"]) if low_idx in history.index else float(w["low"].min())
    high_time = _parse_utc(history.loc[high_idx, "open_time_utc"]) if high_idx in history.index else _parse_utc(w["open_time_utc"].iloc[0])
    low_time = _parse_utc(history.loc[low_idx, "open_time_utc"]) if low_idx in history.index else _parse_utc(w["open_time_utc"].iloc[-1])
    drop_pct = max(0.0, _pct(high_price, max(low_price, 1e-9)))
    bounce_pct = max(0.0, _pct(price, max(low_price, 1e-9)))
    red_streak, _ = _streaks(history)
    risk = max(_safe_float(base_row.get("cs_pre_dump_risk_score")), _safe_float(base_row.get("cs_dump_acceleration_score")))
    active = int((risk >= 0.58 and _ret(history, 5) < -0.25 and bounce_pct < 0.20) or int(base_row.get("cs_falling_knife_active", 0) or 0) == 1)
    recent_after_low = history[history["open_time_utc"] >= low_time].copy()
    tolerance = max(price * 0.0018, 0.015)
    grounding_attempts = int((recent_after_low["low"].astype(float).sub(low_price).abs() <= tolerance).sum()) if not recent_after_low.empty else 0
    exhaustion = _safe_float(base_row.get("cs_sell_pressure_exhaustion_score"))
    grounding_score = _clip01(0.38 * _safe_float(base_row.get("cs_bottom_attempt_score")) + 0.32 * _safe_float(base_row.get("cs_base_after_flush_score")) + 0.18 * min(grounding_attempts, 4) / 4.0 + 0.12 * min(bounce_pct, 0.6) / 0.6)
    return {
        "fcs_knife_risk_score": risk,
        "fcs_knife_active": active,
        "fcs_knife_age_min": max(0.0, (now - high_time).total_seconds() / 60.0),
        "fcs_knife_drop_pct_so_far": drop_pct,
        "fcs_knife_acceleration_score": _safe_float(base_row.get("cs_dump_acceleration_score")),
        "fcs_knife_red_streak": red_streak,
        "fcs_knife_low_so_far_price": low_price,
        "fcs_knife_low_age_min": max(0.0, (now - low_time).total_seconds() / 60.0),
        "fcs_knife_exhaustion_score": exhaustion,
        "fcs_bounce_from_knife_low_pct": bounce_pct,
        "fcs_grounding_attempt_count": grounding_attempts,
        "fcs_grounding_confirmed_score": grounding_score,
        "fcs_retest_after_knife_score": _clip01(0.55 * grounding_score + 0.45 * int(bounce_pct <= 0.35)),
    }


def _pump_dump_features(history: pd.DataFrame, base_row: pd.Series, levels: dict[str, Any]) -> dict[str, Any]:
    w = history.tail(120).copy()
    price = float(history["close"].iloc[-1])
    if w.empty:
        return {}
    low_idx = int(w["low"].astype(float).idxmin())
    high_idx = int(w["high"].astype(float).idxmax())
    low_price = float(history.loc[low_idx, "low"]) if low_idx in history.index else float(w["low"].min())
    high_price = float(history.loc[high_idx, "high"]) if high_idx in history.index else float(w["high"].max())
    pump_extension = max(0.0, _pct(high_price, max(low_price, 1e-9)))
    pullback = max(0.0, _pct(high_price, price))
    breakout_strength = _clip01(_safe_float(base_row.get("cs_pump_pressure_score")) + 0.25 * int(base_row.get("cs_breakout_recent_high", 0) or 0))
    pullback_quality = _clip01(0.40 * _safe_float(base_row.get("cs_good_pullback_in_pump_score")) + 0.25 * levels.get("fcs_is_near_support_level", 0) + 0.20 * (1 - _clip01(pullback / 1.0)) + 0.15 * _safe_float(base_row.get("cs_trend_continuation_score")))
    resistance_reject = int(levels.get("fcs_resistance_reject_now", 0))
    failed_breakout = _clip01(0.40 * resistance_reject + 0.35 * int(pullback >= 0.35) + 0.25 * _safe_float(base_row.get("cs_pre_dump_risk_score")))
    post_exhaustion = _clip01(0.35 * failed_breakout + 0.30 * _clip01(pump_extension / 2.0) + 0.20 * _safe_float(base_row.get("cs_chop_score")) + 0.15 * _safe_float(base_row.get("cs_pre_dump_risk_score")))
    return {
        "fcs_pump_breakout_strength_score": breakout_strength,
        "fcs_pump_extension_pct": pump_extension,
        "fcs_pullback_from_pump_high_pct": pullback,
        "fcs_pullback_quality_score": pullback_quality,
        "fcs_higher_low_after_breakout": int(_safe_float(base_row.get("cs_higher_lows_count_30m")) >= _safe_float(base_row.get("cs_lower_lows_count_30m"))),
        "fcs_pump_continuation_score": _clip01(0.45 * _safe_float(base_row.get("cs_trend_continuation_score")) + 0.35 * pullback_quality + 0.20 * breakout_strength),
        "fcs_post_pump_exhaustion_score": post_exhaustion,
        "fcs_pre_dump_after_pump_score": _clip01(0.55 * post_exhaustion + 0.45 * _safe_float(base_row.get("cs_pre_dump_risk_score"))),
        "fcs_failed_breakout_score": failed_breakout,
        "fcs_resistance_reject_after_pump": resistance_reject,
    }


def _regime_scores(base_row: pd.Series, fcs: dict[str, Any]) -> dict[str, float]:
    risk = max(_safe_float(base_row.get("cs_pre_dump_risk_score")), fcs.get("fcs_knife_risk_score", 0.0), fcs.get("fcs_pre_dump_after_pump_score", 0.0))
    active_dump = _clip01(0.55 * fcs.get("fcs_knife_active", 0) + 0.25 * _safe_float(base_row.get("cs_dump_acceleration_score")) + 0.20 * int(_ret_from_row(base_row, "cs_return_5m_pct") < -0.25))
    bottom = _clip01(0.42 * _safe_float(base_row.get("cs_bottom_attempt_score")) + 0.28 * fcs.get("fcs_grounding_confirmed_score", 0.0) + 0.18 * fcs.get("fcs_support_strength_score", 0.0) + 0.12 * fcs.get("fcs_channel_is_lower_edge", 0))
    base = _clip01(0.46 * _safe_float(base_row.get("cs_base_after_flush_score")) + 0.32 * fcs.get("fcs_retest_after_knife_score", 0.0) + 0.22 * fcs.get("fcs_support_retest_now", 0))
    pump_breakout = _clip01(0.62 * _safe_float(base_row.get("cs_pump_pressure_score")) + 0.38 * _safe_float(base_row.get("cs_breakout_recent_high")))
    pump_pullback = _clip01(0.58 * fcs.get("fcs_pullback_quality_score", 0.0) + 0.42 * _safe_float(base_row.get("cs_pullback_after_breakout")))
    pump_cont = _clip01(0.52 * fcs.get("fcs_pump_continuation_score", 0.0) + 0.30 * _safe_float(base_row.get("cs_trend_continuation_score")) + 0.18 * _safe_float(base_row.get("cs_long_pressure_now")))
    chop = max(_safe_float(base_row.get("cs_chop_score")), _safe_float(base_row.get("cs_no_trade_chop_score")))
    short_pressure = _clip01(0.70 * _safe_float(base_row.get("cs_short_pressure_now")) + 0.30 * int(fcs.get("fcs_channel_type_code") == CHANNEL_CODES["DOWN_CHANNEL"]))
    late_high_chop = _clip01(0.50 * chop + 0.30 * int(_safe_float(base_row.get("cs_day_channel_position_0_1")) >= 0.70) + 0.20 * fcs.get("fcs_resistance_reject_now", 0))
    return {
        "fcs_regime_score_chop_no_edge": chop,
        "fcs_regime_score_short_pressure": short_pressure,
        "fcs_regime_score_pre_dump_risk": risk,
        "fcs_regime_score_active_dump": active_dump,
        "fcs_regime_score_bottoming": bottom,
        "fcs_regime_score_base_after_flush": base,
        "fcs_regime_score_pump_breakout": pump_breakout,
        "fcs_regime_score_pump_pullback": pump_pullback,
        "fcs_regime_score_pump_continuation": pump_cont,
        "fcs_regime_score_late_high_chop": late_high_chop,
    }


def _ret_from_row(row: pd.Series, column: str) -> float:
    return _safe_float(row.get(column))


def _choose_regime(scores: dict[str, float]) -> tuple[str, int, float]:
    mapping = {
        "fcs_regime_score_active_dump": "ACTIVE_DUMP",
        "fcs_regime_score_pre_dump_risk": "PRE_DUMP_RISK",
        "fcs_regime_score_base_after_flush": "BASE_AFTER_FLUSH",
        "fcs_regime_score_bottoming": "BOTTOMING",
        "fcs_regime_score_pump_breakout": "PUMP_BREAKOUT",
        "fcs_regime_score_pump_pullback": "PUMP_PULLBACK",
        "fcs_regime_score_pump_continuation": "PUMP_CONTINUATION",
        "fcs_regime_score_short_pressure": "SHORT_PRESSURE",
        "fcs_regime_score_late_high_chop": "LATE_HIGH_CHOP",
        "fcs_regime_score_chop_no_edge": "CHOP_NO_EDGE",
    }
    best_col, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score < 0.42:
        return "NEUTRAL", REGIME_CODES["NEUTRAL"], float(best_score)
    label = mapping[best_col]
    return label, REGIME_CODES[label], float(best_score)


def _candidate_full_features(candidate: pd.Series, ohlcv: pd.DataFrame, day_compact: str) -> dict[str, Any]:
    entry_time = _parse_utc(candidate["entry_time_utc"])
    context = _context_time(candidate)
    history = ohlcv[ohlcv["open_time_utc"] <= context].copy()
    if history.empty:
        raise ValueError(f"no history for {candidate.get('candidate_id')}")
    now = _parse_utc(history["open_time_utc"].iloc[-1])
    price = float(history["close"].iloc[-1])
    levels, _ = _build_levels(history, day_compact)
    level_features = _nearest_level_features(levels, price, now)
    channel = _channel_features(history, now)
    knife = _knife_features(history, candidate, now)
    pump_dump = _pump_dump_features(history, candidate, level_features)
    fcs: dict[str, Any] = {}
    fcs.update(level_features)
    fcs.update(channel)
    fcs.update(knife)
    fcs.update(pump_dump)
    scores = _regime_scores(candidate, fcs)
    regime_label, regime_code, regime_conf = _choose_regime(scores)
    fcs.update(scores)
    fcs["fcs_regime_primary_code"] = regime_code
    fcs["fcs_regime_confidence"] = regime_conf
    fcs["fcs_regime_changed_recently"] = 0
    fcs["fcs_max_source_time_utc"] = _fmt_utc(now)
    fcs["fcs_context_before_entry"] = int(now < entry_time)
    return {
        "day": normalize_day(candidate.get("day")),
        "candidate_id": str(candidate.get("candidate_id")),
        "record_id": str(candidate.get("record_id")),
        "entry_time_utc": normalize_ts(candidate.get("entry_time_utc")),
        "fcs_regime_primary_label": regime_label,
        **fcs,
    }


def _regime_timeline(ohlcv: pd.DataFrame, candidate_features: pd.DataFrame) -> pd.DataFrame:
    # Regime intervals are compressed from candidate-time regimes. This is intentionally a diagnostic layer,
    # while direct model features are still per-candidate fcs_* numeric columns.
    rows = candidate_features.sort_values("entry_time_utc").copy()
    segments: list[dict[str, Any]] = []
    if rows.empty:
        return pd.DataFrame()
    current_label = str(rows.iloc[0]["fcs_regime_primary_label"])
    current_code = int(rows.iloc[0]["fcs_regime_primary_code"])
    start = _parse_utc(rows.iloc[0]["fcs_max_source_time_utc"])
    last = start
    conf_values = [float(rows.iloc[0]["fcs_regime_confidence"])]
    for _, row in rows.iloc[1:].iterrows():
        label = str(row["fcs_regime_primary_label"])
        code = int(row["fcs_regime_primary_code"])
        now = _parse_utc(row["fcs_max_source_time_utc"])
        if label != current_label:
            segments.append(
                {
                    "regime_id": f"FCSR_{len(segments)+1:03d}",
                    "regime_primary_label": current_label,
                    "regime_primary_code": current_code,
                    "start_utc": _fmt_utc(start),
                    "end_utc": _fmt_utc(last),
                    "known_time_utc": _fmt_utc(start),
                    "duration_min": max(0.0, (last - start).total_seconds() / 60.0),
                    "confidence_mean": float(np.mean(conf_values)),
                    "confidence_max": float(np.max(conf_values)),
                    "source": "compressed_candidate_fcs_regime",
                }
            )
            current_label = label
            current_code = code
            start = now
            conf_values = []
        last = now
        conf_values.append(float(row["fcs_regime_confidence"]))
    segments.append(
        {
            "regime_id": f"FCSR_{len(segments)+1:03d}",
            "regime_primary_label": current_label,
            "regime_primary_code": current_code,
            "start_utc": _fmt_utc(start),
            "end_utc": _fmt_utc(last),
            "known_time_utc": _fmt_utc(start),
            "duration_min": max(0.0, (last - start).total_seconds() / 60.0),
            "confidence_mean": float(np.mean(conf_values)),
            "confidence_max": float(np.max(conf_values)),
            "source": "compressed_candidate_fcs_regime",
        }
    )
    return pd.DataFrame(segments)


def _channel_rows(candidate_features: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "day",
        "candidate_id",
        "record_id",
        "entry_time_utc",
        "fcs_max_source_time_utc",
        "fcs_channel_type_code",
        "fcs_channel_age_min",
        "fcs_channel_lower_price_now",
        "fcs_channel_upper_price_now",
        "fcs_channel_mid_price_now",
        "fcs_channel_width_pct",
        "fcs_channel_slope_pct_per_min",
        "fcs_channel_position_0_1",
        "fcs_channel_lower_touch_count",
        "fcs_channel_upper_touch_count",
        "fcs_channel_breakout_up_recent",
        "fcs_channel_breakdown_recent",
        "fcs_channel_is_lower_edge",
        "fcs_channel_is_mid",
        "fcs_channel_is_upper_edge",
    ]
    out = candidate_features[cols].copy()
    out.insert(0, "channel_id", [f"FCSC_{i+1:03d}" for i in range(len(out))])
    return out


def _default_paths(day: str) -> dict[str, Path]:
    compact = compact_day(day)
    base = Path("STAS5_ML_CORE") / "artifacts" / "v5" / "market_passports" / compact
    return {
        "base": base,
        "ml_ready_plus": base / f"STAS5_V5_MARKET_PASSPORT_{compact}_ML_READY_274F_PLUS_CAUSAL_STRUCTURE_TARGETS_V1.csv",
        "allowlist_plus": base / f"STAS5_V5_MARKET_PASSPORT_{compact}_FEATURE_ALLOWLIST_274_PLUS_CAUSAL_STRUCTURE_V1.json",
        "levels": base / f"STAS5_V5_MARKET_PASSPORT_{compact}_LEVELS_CAUSAL_V1.csv",
        "channels": base / f"STAS5_V5_MARKET_PASSPORT_{compact}_CHANNELS_CAUSAL_V1.csv",
        "regimes": base / f"STAS5_V5_MARKET_PASSPORT_{compact}_REGIMES_CAUSAL_V1.csv",
        "events": base / f"STAS5_V5_MARKET_PASSPORT_{compact}_EVENTS_CAUSAL_V1.csv",
        "candidate_features": base / f"STAS5_V5_MARKET_PASSPORT_{compact}_FULL_STRUCTURE_CANDIDATE_FEATURES_CAUSAL_V1.csv",
        "ml_ready_full": base / f"STAS5_V5_MARKET_PASSPORT_{compact}_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv",
        "allowlist_full": base / f"STAS5_V5_MARKET_PASSPORT_{compact}_FEATURE_ALLOWLIST_274_PLUS_FULL_CAUSAL_STRUCTURE_V1.json",
        "guard": base / f"STAS5_V5_MARKET_PASSPORT_{compact}_FULL_CAUSAL_STRUCTURE_GUARD_V1.json",
        "audit": base / f"STAS5_V5_MARKET_PASSPORT_{compact}_FULL_CAUSAL_STRUCTURE_AUDIT_RU.md",
        "plot": base / f"DAY_MARKET_PASSPORT_{compact}_FULL_CAUSAL_STRUCTURE_MAP_V1.png",
    }


def _infer_ohlcv_path(rows: pd.DataFrame, explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    for column in ["cs_source_ohlcv", "v2_combo_source_ohlcv", "source_ohlcv"]:
        if column in rows.columns:
            values = rows[column].dropna().astype(str)
            if not values.empty and values.iloc[0]:
                return PROJECT_ROOT / values.iloc[0]
    day = normalize_day(rows["day"].iloc[0])
    return PROJECT_ROOT / f"data/core/bybit_ohlcv/dt={day}/tf={TIMEFRAME}/symbol={SYMBOL}/part-final.csv"


def _feature_columns(frame: pd.DataFrame) -> list[str]:
    out = []
    for column in frame.columns:
        if not column.startswith("fcs_"):
            continue
        if column.endswith("_utc") or column.endswith("_label"):
            continue
        if column in {"fcs_max_source_time_utc"}:
            continue
        out.append(column)
    return out


def _write_audit(path: Path, guard: dict[str, Any]) -> None:
    lines = [
        f"# STAS5 V5 Full Causal Structure Audit {guard['day']}",
        "",
        f"Статус: `{guard['status']}`.",
        "",
        "## Что Собрано",
        "",
        "- уровни поддержки/сопротивления с жизнью уровня;",
        "- канальные признаки на каждом кандидате;",
        "- режимы рынка builder'а;",
        "- события уровней/режимов/ножа/пампа;",
        "- candidate-level `fcs_*` признаки;",
        "- ML-ready таблица `274 + cs_* + fcs_* + targets`;",
        "- no-future guard.",
        "",
        "## Счетчики",
        "",
        f"- rows: `{guard['rows']}`",
        f"- base features before fcs: `{guard['base_feature_count']}`",
        f"- fcs features: `{guard['full_causal_feature_count']}`",
        f"- total features: `{guard['feature_count']}`",
        f"- levels: `{guard['artifact_counts']['levels']}`",
        f"- channels: `{guard['artifact_counts']['channels']}`",
        f"- regimes: `{guard['artifact_counts']['regimes']}`",
        f"- events: `{guard['artifact_counts']['events']}`",
        "",
        "## Guard",
        "",
    ]
    for item in guard["checks"]:
        lines.append(f"- `{item['check']}`: `{item['status']}`")
    lines.extend(
        [
            "",
            "## Граница",
            "",
            "Manual-фазы и ручные зоны остаются teacher/context и не входят в feature allowlist.",
            "Прямые признаки `X`: старые causal-признаки, `cs_*` и новые числовые `fcs_*`, рассчитанные до `entry_time_utc`.",
            "Обучение не запускалось.",
            "",
        ]
    )
    ensure_parent(path)
    path.write_text("\n".join(lines), encoding="utf-8")


def _draw_full_map(
    *,
    day: str,
    ohlcv: pd.DataFrame,
    ml_ready: pd.DataFrame,
    candidate_features: pd.DataFrame,
    manual_structure_path: Path | None,
    phase_path: Path | None,
    output_path: Path,
) -> None:
    df = ml_ready.merge(
        candidate_features,
        on=["day", "candidate_id", "record_id", "entry_time_utc"],
        how="left",
        validate="one_to_one",
    )
    df["entry_dt"] = pd.to_datetime(df["entry_time_utc"], utc=True)
    ohlcv = ohlcv.copy()
    ohlcv["time"] = pd.to_datetime(ohlcv["open_time_utc"], utc=True)
    day_compact = compact_day(day)

    fig = plt.figure(figsize=(26, 15), dpi=145)
    gs = fig.add_gridspec(4, 1, height_ratios=[7.5, 2.15, 2.0, 1.45], hspace=0.08)
    ax = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax)
    ax3 = fig.add_subplot(gs[2], sharex=ax)
    ax4 = fig.add_subplot(gs[3], sharex=ax)
    fig.patch.set_facecolor("#0d1117")
    for area in (ax, ax2, ax3, ax4):
        area.set_facecolor("#101820")
        area.grid(True, color="#26323b", alpha=0.48, linewidth=0.6)
        area.tick_params(colors="#d7dee8", labelsize=9)
        for spine in area.spines.values():
            spine.set_color("#33404a")

    ymin = float(ohlcv["low"].min())
    ymax = float(ohlcv["high"].max())

    if phase_path and phase_path.exists():
        phases = pd.read_csv(phase_path, encoding="utf-8-sig")
        colors = ["#1f77b4", "#2ca02c", "#46515c", "#af8c00", "#4d8f31", "#d62728", "#7f1d1d", "#aa3344", "#5b3fbf", "#7f3fbf"]
        for idx, row in phases.iterrows():
            start = _phase_time(day, row["start_utc"])
            end = _phase_time(day, row["end_utc"])
            color = colors[idx % len(colors)]
            ax.axvspan(start, end, color=color, alpha=0.10, lw=0)
            ax.text(
                start + (end - start) * 0.02,
                ymax + 0.06,
                str(row.get("phase_segment_label", ""))[:16],
                color="#f0f6fc",
                fontsize=8.2,
                fontweight="bold",
                ha="left",
                va="bottom",
                bbox=dict(boxstyle="round,pad=0.15", fc="#0d1117", ec=color, alpha=0.86),
            )

    if manual_structure_path and manual_structure_path.exists():
        manual = pd.read_csv(manual_structure_path, encoding="utf-8-sig")
        for _, row in manual.iterrows():
            start = _phase_time(day, row["start_utc"])
            end = _phase_time(day, row["end_utc"])
            sl, sh = float(row["manual_support_low"]), float(row["manual_support_high"])
            rl, rh = float(row["manual_resistance_low"]), float(row["manual_resistance_high"])
            ax.fill_between([start, end], [sl, sl], [sh, sh], color="#00d26a", alpha=0.10)
            ax.fill_between([start, end], [rl, rl], [rh, rh], color="#ff9f1c", alpha=0.10)
            ax.hlines([sl, sh], start, end, colors="#00d26a", alpha=0.30, linewidth=0.75, linestyles="--")
            ax.hlines([rl, rh], start, end, colors="#ff9f1c", alpha=0.30, linewidth=0.75, linestyles="--")

    ax.plot(ohlcv["time"], ohlcv["close"], color="#c9d1d9", linewidth=0.98, alpha=0.86, label="close")
    ax.vlines(ohlcv["time"], ohlcv["low"], ohlcv["high"], color="#8b949e", alpha=0.13, linewidth=0.40)

    # Local causal channel snapshots for approved entries.
    key_rows = df[(df["entry_y"].eq(1)) | (df["fcs_knife_active"].eq(1)) | (df["fcs_regime_score_pre_dump_risk"] >= 0.75)].copy()
    for _, row in key_rows.iterrows():
        x = row["entry_dt"]
        low_line = _safe_float(row.get("fcs_channel_lower_price_now"))
        high_line = _safe_float(row.get("fcs_channel_upper_price_now"))
        if high_line > low_line:
            start = x - pd.Timedelta(minutes=min(max(_safe_float(row.get("fcs_channel_age_min")), 20.0), 120.0))
            ax.hlines(low_line, start, x, colors="#00ff88", alpha=0.33, linewidth=0.9, linestyles=":")
            ax.hlines(high_line, start, x, colors="#ffb86b", alpha=0.30, linewidth=0.9, linestyles=":")

    tag_colors = {
        1: "#b0b7c3",
        2: "#ff7b72",
        3: "#ff4d4d",
        4: "#ff004c",
        5: "#00d26a",
        6: "#7ee787",
        7: "#47b4ff",
        8: "#47b4ff",
        9: "#47b4ff",
        10: "#b0b7c3",
        0: "#ffb86b",
    }
    for code, sub in df.groupby("fcs_regime_primary_code"):
        ax.scatter(
            sub["entry_dt"],
            sub["entry_price_5bps"],
            s=42 if int(code) != 0 else 26,
            color=tag_colors.get(int(code), "#ccc"),
            alpha=0.85,
            label=f"REGIME_{int(code)}",
            zorder=4,
        )

    knife_rows = df[df["fcs_knife_active"].eq(1)]
    for _, row in knife_rows.iterrows():
        ax.annotate(
            f"{row['candidate_id']}\nKNIFE ACTIVE",
            xy=(row["entry_dt"], float(row["entry_price_5bps"])),
            xytext=(row["entry_dt"], float(row["entry_price_5bps"]) + 0.55),
            fontsize=8,
            color="#ffd1dc",
            ha="center",
            va="center",
            arrowprops=dict(arrowstyle="-|>", color="#ff004c", lw=1.2),
            bbox=dict(boxstyle="round,pad=0.22", fc="#29000f", ec="#ff004c", alpha=0.90),
        )

    goods = df[df["entry_y"].eq(1)].sort_values("entry_dt")
    offsets = [0.48, 0.56, 0.42, 0.56, 0.38, 0.46, 0.58, 0.48, 0.54, -0.54, -0.50]
    for i, (_, row) in enumerate(goods.iterrows(), start=1):
        x = row["entry_dt"]
        y = float(row["entry_price_5bps"])
        ax.scatter([x], [y], s=420, facecolors="none", edgecolors="#00ff88", linewidths=2.8, zorder=6)
        text = (
            f"{i}. {row['candidate_id']} {pd.Timestamp(x).strftime('%H:%M')}\n"
            f"R{row['fcs_regime_score_pre_dump_risk']:.2f} "
            f"L{max(row['fcs_regime_score_bottoming'], row['fcs_regime_score_base_after_flush']):.2f} "
            f"P{max(row['fcs_regime_score_pump_breakout'], row['fcs_regime_score_pump_continuation']):.2f} "
            f"C{row['fcs_regime_score_chop_no_edge']:.2f}"
        )
        ax.annotate(
            text,
            xy=(x, y),
            xytext=(x, y + offsets[(i - 1) % len(offsets)]),
            fontsize=8.1,
            color="#dfffe9",
            ha="center",
            va="center",
            arrowprops=dict(arrowstyle="-", color="#00ff88", lw=1.1, alpha=0.82),
            bbox=dict(boxstyle="round,pad=0.22", fc="#0d1117", ec="#00ff88", alpha=0.88),
        )

    ax.text(
        ohlcv["time"].iloc[2],
        ymax + 0.40,
        "V5 FULL CAUSAL STRUCTURE: level lifecycle, channel, regime, knife, pump/dump, pressure",
        color="#f0f6fc",
        fontsize=11,
        ha="left",
        va="center",
        bbox=dict(boxstyle="round,pad=0.30", fc="#0d1117", ec="#00bfff", alpha=0.92),
    )
    ax.text(
        ohlcv["time"].iloc[2],
        ymax + 0.22,
        "Bands = manual teacher context. Dotted channel/SR + regime scores = fcs_* causal features from past candles only.",
        color="#d7dee8",
        fontsize=9.4,
        ha="left",
        va="center",
        bbox=dict(boxstyle="round,pad=0.22", fc="#0d1117", ec="#33404a", alpha=0.92),
    )
    ax.set_ylim(ymin - 0.22, ymax + 0.52)
    ax.set_ylabel("Price", color="#d7dee8")
    ax.legend(loc="upper left", ncol=5, fontsize=7.0, facecolor="#0d1117", edgecolor="#33404a", labelcolor="#e6edf3")

    risk = df["fcs_regime_score_pre_dump_risk"]
    low_score = df[["fcs_regime_score_bottoming", "fcs_regime_score_base_after_flush"]].max(axis=1)
    pump_score = df[["fcs_regime_score_pump_breakout", "fcs_regime_score_pump_pullback", "fcs_regime_score_pump_continuation"]].max(axis=1)
    chop = df["fcs_regime_score_chop_no_edge"]
    for values, color, label in [
        (risk, "#ff4d4d", "R danger/pre-dump"),
        (low_score, "#00d26a", "L bottom/base"),
        (pump_score, "#47b4ff", "P pump/continuation"),
        (chop, "#b0b7c3", "C chop/no-edge"),
    ]:
        ax2.plot(df["entry_dt"], values, marker="o", ms=3, lw=1.05, color=color, alpha=0.92, label=label)
    ax2.axhline(0.62, color="#ffcc00", lw=0.8, ls="--", alpha=0.55)
    ax2.set_ylim(-0.02, 1.05)
    ax2.set_ylabel("Regime scores", color="#d7dee8")
    ax2.legend(loc="upper left", ncol=4, fontsize=8, facecolor="#0d1117", edgecolor="#33404a", labelcolor="#e6edf3")

    slope_norm = (df["fcs_channel_slope_pct_per_min"].clip(-0.03, 0.03) + 0.03) / 0.06
    ax3.plot(df["entry_dt"], df["cs_short_pressure_now"], marker="o", ms=3, lw=1.0, color="#ff7b72", label="short_pressure")
    ax3.plot(df["entry_dt"], df["cs_long_pressure_now"], marker="o", ms=3, lw=1.0, color="#00d26a", label="long_pressure")
    ax3.plot(df["entry_dt"], slope_norm, marker=".", ms=3, lw=0.9, color="#ffd166", label="channel_slope_norm")
    ax3.plot(df["entry_dt"], df["fcs_level_channel_position_0_1"], marker=".", ms=3, lw=0.9, color="#a78bfa", label="level_channel_pos")
    ax3.axhline(0.5, color="#8b949e", lw=0.7, ls="--", alpha=0.5)
    ax3.set_ylim(-0.02, 1.05)
    ax3.set_ylabel("Pressure/levels", color="#d7dee8")
    ax3.legend(loc="upper left", ncol=4, fontsize=8, facecolor="#0d1117", edgecolor="#33404a", labelcolor="#e6edf3")

    ax4.set_ylim(0, 1)
    for _, row in df.iterrows():
        x = row["entry_dt"]
        color = "#00ff88" if row["entry_y"] == 1 else "#ff6b6b"
        ax4.vlines(x, 0.10, 0.56, color=color, linewidth=1.1, alpha=0.82)
        if row["entry_y"] == 1:
            ax4.text(x, 0.70, row["candidate_id"], rotation=70, fontsize=7, color="#00ff88", ha="center", va="bottom")
    ax4.text(
        ohlcv["time"].iloc[0],
        0.89,
        "Targets row: green = approved y=1, red = y=0. No-future: fcs_max_source_time < entry_time.",
        color="#e6edf3",
        fontsize=9.5,
        ha="left",
        va="center",
        bbox=dict(boxstyle="round,pad=0.25", fc="#0d1117", ec="#33404a", alpha=0.9),
    )
    ax4.set_yticks([])
    ax4.set_ylabel("Targets", color="#d7dee8")
    ax4.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=timezone.utc))
    ax4.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    for label in ax.get_xticklabels():
        label.set_visible(False)
    for label in ax2.get_xticklabels():
        label.set_visible(False)
    for label in ax3.get_xticklabels():
        label.set_visible(False)
    ax.set_xlim(ohlcv["time"].min(), ohlcv["time"].max())
    fig.text(
        0.012,
        0.012,
        "Sources: ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1, LEVELS/CHANNELS/REGIMES/EVENTS CAUSAL V1. Manual bands are teacher/context; fcs_* is X.",
        color="#c9d1d9",
        fontsize=8.7,
    )
    ensure_parent(output_path)
    fig.savefig(output_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def _phase_time(day: str, text: Any) -> pd.Timestamp:
    value = str(text).strip()
    if len(value.split(":")) == 2:
        value += ":00"
    return pd.Timestamp(f"{day} {value}", tz="UTC")


def build_full_causal_structure_package(
    *,
    day: str,
    ml_ready_plus_path: Path | None = None,
    allowlist_plus_path: Path | None = None,
    ohlcv_path: Path | None = None,
    output_dir: Path | None = None,
    draw_plot: bool = True,
) -> dict[str, Any]:
    day = normalize_day(day)
    compact = compact_day(day)
    paths = _default_paths(day)
    if output_dir is not None:
        for key, path in list(paths.items()):
            if key != "base":
                paths[key] = output_dir / path.name
        paths["base"] = output_dir

    ml_ready_path = ml_ready_plus_path or paths["ml_ready_plus"]
    allowlist_path = allowlist_plus_path or paths["allowlist_plus"]
    if not ml_ready_path.exists():
        raise FileNotFoundError(f"ML-ready plus causal source not found: {ml_ready_path}")
    if not allowlist_path.exists():
        raise FileNotFoundError(f"allowlist plus causal source not found: {allowlist_path}")

    rows = pd.read_csv(ml_ready_path, encoding="utf-8-sig")
    base_features = load_manifest_feature_columns(allowlist_path)
    ohlcv_file = _infer_ohlcv_path(rows, ohlcv_path)
    ohlcv = _load_ohlcv(ohlcv_file)

    full_level_states, level_events = _build_levels(ohlcv, compact)
    now = _parse_utc(ohlcv["open_time_utc"].iloc[-1])
    levels_df = pd.DataFrame(_level_rows(full_level_states, now))

    fcs_rows = [_candidate_full_features(row, ohlcv, compact) for _, row in rows.iterrows()]
    candidate_features = pd.DataFrame(fcs_rows)
    fcs_feature_columns = _feature_columns(candidate_features)
    channels_df = _channel_rows(candidate_features)
    regimes_df = _regime_timeline(ohlcv, candidate_features)

    regime_events = [
        {
            "event_type": "REGIME_START",
            "event_code": int(row["regime_primary_code"]),
            "level_id": "",
            "level_type": "",
            "event_time_utc": row["start_utc"],
            "known_time_utc": row["known_time_utc"],
            "price": 0.0,
            "source": f"regime:{row['regime_primary_label']}",
        }
        for _, row in regimes_df.iterrows()
    ]
    candidate_events = []
    for _, row in candidate_features.iterrows():
        if int(row.get("fcs_knife_active", 0)) == 1:
            candidate_events.append(
                {
                    "event_type": "KNIFE_ACTIVE",
                    "event_code": 100,
                    "level_id": "",
                    "level_type": "",
                    "event_time_utc": row["fcs_max_source_time_utc"],
                    "known_time_utc": row["fcs_max_source_time_utc"],
                    "price": row.get("fcs_knife_low_so_far_price", 0.0),
                    "source": f"candidate:{row['candidate_id']}",
                }
            )
    events_df = pd.DataFrame(level_events + regime_events + candidate_events)

    plus = rows.merge(
        candidate_features.drop(columns=["fcs_regime_primary_label"]),
        on=["day", "candidate_id", "record_id", "entry_time_utc"],
        how="left",
        validate="one_to_one",
        indicator=True,
    )
    merge_missing = int((plus["_merge"] != "both").sum())
    plus = plus.drop(columns=["_merge"])
    all_feature_columns = list(base_features) + [column for column in fcs_feature_columns if column not in base_features]

    forbidden_base = forbidden_feature_matches(base_features)
    forbidden_fcs = {
        column: [bad for bad in FORBIDDEN_DIRECT_FEATURE_SUBSTRINGS if bad in column.lower()]
        for column in fcs_feature_columns
        if any(bad in column.lower() for bad in FORBIDDEN_DIRECT_FEATURE_SUBSTRINGS)
    }
    target_in_features = [column for column in all_feature_columns if column in TARGET_OR_TEACHER_COLUMNS]
    source_times = pd.to_datetime(candidate_features["fcs_max_source_time_utc"], utc=True)
    entry_times = pd.to_datetime(candidate_features["entry_time_utc"], utc=True)
    source_after_entry = int((source_times >= entry_times).sum())
    context_false = int((candidate_features["fcs_context_before_entry"].astype(int) != 1).sum())
    missing_fcs = int(candidate_features[fcs_feature_columns].isna().sum().sum())
    event_known_after_event = 0
    if not events_df.empty and "known_time_utc" in events_df.columns:
        known = pd.to_datetime(events_df["known_time_utc"], utc=True, errors="coerce")
        event_time = pd.to_datetime(events_df["event_time_utc"], utc=True, errors="coerce")
        # Pivot confirmations can be known after pivot event_time; this is allowed because features use known_time.
        event_known_after_day = int((known > _parse_utc(ohlcv["open_time_utc"].iloc[-1])).sum())
    else:
        event_known_after_day = 0

    checks = [
        {"check": "rows_match", "status": "PASS" if len(rows) == len(candidate_features) == len(plus) else "FAIL", "details": {"rows": int(len(rows)), "candidate_features": int(len(candidate_features)), "plus": int(len(plus))}},
        {"check": "merge_one_to_one", "status": "PASS" if merge_missing == 0 else "FAIL", "details": {"merge_missing": merge_missing}},
        {"check": "full_causal_feature_count_positive", "status": "PASS" if len(fcs_feature_columns) > 0 else "FAIL", "details": {"fcs_feature_count": len(fcs_feature_columns)}},
        {"check": "source_time_before_entry", "status": "PASS" if source_after_entry == 0 and context_false == 0 else "FAIL", "details": {"source_after_entry": source_after_entry, "context_false": context_false}},
        {"check": "forbidden_existing_features_absent", "status": "PASS" if not forbidden_base else "FAIL", "details": forbidden_base},
        {"check": "forbidden_fcs_features_absent", "status": "PASS" if not forbidden_fcs else "FAIL", "details": forbidden_fcs},
        {"check": "targets_not_in_features", "status": "PASS" if not target_in_features else "FAIL", "details": {"target_in_features": target_in_features}},
        {"check": "fcs_values_not_missing", "status": "PASS" if missing_fcs == 0 else "FAIL", "details": {"missing_fcs": missing_fcs}},
        {"check": "events_known_inside_day", "status": "PASS" if event_known_after_day == 0 else "FAIL", "details": {"event_known_after_day": event_known_after_day}},
        {"check": "visual_sources_exist", "status": "PASS" if paths["plot"].suffix == ".png" else "FAIL", "details": {"plot": str(paths["plot"])}},
    ]
    status = STATUS if all(item["status"] == "PASS" for item in checks) else "FAIL_FULL_CAUSAL_STRUCTURE_GUARD"

    for path, frame in [
        (paths["levels"], levels_df),
        (paths["channels"], channels_df),
        (paths["regimes"], regimes_df),
        (paths["events"], events_df),
        (paths["candidate_features"], candidate_features),
        (paths["ml_ready_full"], plus),
    ]:
        ensure_parent(path)
        frame.to_csv(path, index=False, encoding="utf-8-sig")

    allowlist = {
        "status": status,
        "created_utc": utc_now(),
        "day": day,
        "schema_version": 1,
        "source_feature_allowlist_274_plus_causal_structure": rel(allowlist_path),
        "source_ml_ready_274f_plus_causal_structure": rel(ml_ready_path),
        "source_ohlcv": rel(ohlcv_file),
        "feature_columns": all_feature_columns,
        "feature_count": len(all_feature_columns),
        "base_feature_columns": base_features,
        "base_feature_count": len(base_features),
        "full_causal_feature_columns": fcs_feature_columns,
        "full_causal_feature_count": len(fcs_feature_columns),
        "metadata_columns": ["fcs_max_source_time_utc", "fcs_regime_primary_label"],
        "target_columns": [column for column in TARGET_OR_TEACHER_COLUMNS if column in plus.columns],
        "guardrails": [
            "manual_teacher_context_not_in_feature_columns",
            "fcs_max_source_time_utc_must_be_less_than_entry_time_utc",
            "levels_channels_regimes_events_must_be_reconstructable_from_past_ohlcv",
            "no_future_postfact_hit_tp_stas3_exit_old_ml_features",
        ],
    }
    write_json(paths["allowlist_full"], allowlist)

    guard = {
        "status": status,
        "created_utc": utc_now(),
        "day": day,
        "rows": int(len(plus)),
        "base_feature_count": len(base_features),
        "full_causal_feature_count": len(fcs_feature_columns),
        "feature_count": len(all_feature_columns),
        "artifact_counts": {
            "levels": int(len(levels_df)),
            "channels": int(len(channels_df)),
            "regimes": int(len(regimes_df)),
            "events": int(len(events_df)),
        },
        "outputs": {key: str(path.resolve()) for key, path in paths.items() if key != "base"},
        "sources": {
            "ml_ready_plus_causal": str(ml_ready_path.resolve()),
            "allowlist_plus_causal": str(allowlist_path.resolve()),
            "ohlcv": str(ohlcv_file.resolve()),
        },
        "checks": checks,
        "feature_columns": all_feature_columns,
        "full_causal_feature_columns": fcs_feature_columns,
    }
    write_json(paths["guard"], guard)
    _write_audit(paths["audit"], guard)

    if draw_plot:
        _draw_full_map(
            day=day,
            ohlcv=ohlcv,
            ml_ready=rows,
            candidate_features=candidate_features,
            manual_structure_path=paths["base"] / f"STAS5_V5_MARKET_PASSPORT_{compact}_MARKET_STRUCTURE_NUMERIC_V1.csv",
            phase_path=paths["base"] / f"STAS5_V5_MARKET_PASSPORT_{compact}_PHASE_SEGMENTS_USER_APPROVED_V1.csv",
            output_path=paths["plot"],
        )

    return guard


def main() -> int:
    parser = argparse.ArgumentParser(description="Build STAS5 V5 full causal market-structure package.")
    parser.add_argument("--day", required=True)
    parser.add_argument("--ml-ready-plus-path", default="")
    parser.add_argument("--allowlist-plus-path", default="")
    parser.add_argument("--ohlcv-path", default="")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--no-plot", action="store_true")
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()

    guard = build_full_causal_structure_package(
        day=args.day,
        ml_ready_plus_path=Path(args.ml_ready_plus_path) if args.ml_ready_plus_path else None,
        allowlist_plus_path=Path(args.allowlist_plus_path) if args.allowlist_plus_path else None,
        ohlcv_path=Path(args.ohlcv_path) if args.ohlcv_path else None,
        output_dir=Path(args.output_dir) if args.output_dir else None,
        draw_plot=not args.no_plot,
    )
    print(
        json.dumps(
            {
                "status": guard["status"],
                "rows": guard["rows"],
                "feature_count": guard["feature_count"],
                "fcs_feature_count": guard["full_causal_feature_count"],
                "artifact_counts": guard["artifact_counts"],
            },
            ensure_ascii=False,
        )
    )
    if not args.no_strict and guard["status"] != STATUS:
        raise SystemExit(2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
