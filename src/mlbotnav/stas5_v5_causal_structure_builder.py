from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

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


STATUS = "PASS_NO_TRAINING_CAUSAL_STRUCTURE_READY"
SYMBOL = "SOLUSDT"
TIMEFRAME = "1m"

TARGET_COLUMNS = {
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
    "market_phase_primary",
    "market_phase_secondary",
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
    if value is None or str(value) == "NaT":
        return ""
    return _parse_utc(value).strftime("%Y-%m-%dT%H:%M:%SZ")


def _norm_col(name: str) -> str:
    return "cs_" + str(name).strip().lower()


def _window(history: pd.DataFrame, bars: int) -> pd.DataFrame:
    if bars <= 0:
        return history.iloc[0:0]
    return history.tail(bars)


def _ret(history: pd.DataFrame, bars: int) -> float:
    w = _window(history, bars)
    if len(w) < 2:
        return 0.0
    return _pct(float(w["close"].iloc[-1]), float(w["close"].iloc[0]))


def _range_pct(history: pd.DataFrame, bars: int) -> float:
    w = _window(history, bars)
    if w.empty:
        return 0.0
    low = float(w["low"].min())
    high = float(w["high"].max())
    close = float(w["close"].iloc[-1])
    if close == 0:
        return 0.0
    return float((high - low) / close * 100.0)


def _trend_slope_pct(history: pd.DataFrame, bars: int) -> float:
    w = _window(history, bars)
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


def _true_range(df: pd.DataFrame) -> pd.Series:
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    prev_close = df["close"].astype(float).shift(1)
    return pd.concat([(high - low), (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)


def _streaks(history: pd.DataFrame) -> tuple[int, int]:
    red = 0
    green = 0
    for _, row in history.tail(20).iloc[::-1].iterrows():
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


def _lower_counts(history: pd.DataFrame, bars: int = 30) -> tuple[int, int, int, int]:
    w = _window(history, bars)
    if len(w) < 2:
        return 0, 0, 0, 0
    lows = w["low"].astype(float).to_numpy()
    highs = w["high"].astype(float).to_numpy()
    lower_lows = int(np.sum(lows[1:] < lows[:-1]))
    lower_highs = int(np.sum(highs[1:] < highs[:-1]))
    higher_lows = int(np.sum(lows[1:] > lows[:-1]))
    higher_highs = int(np.sum(highs[1:] > highs[:-1]))
    return lower_lows, lower_highs, higher_lows, higher_highs


def _confirmed_pivots(history: pd.DataFrame, *, left: int = 3, right: int = 3) -> tuple[list[tuple[pd.Timestamp, float]], list[tuple[pd.Timestamp, float]]]:
    if len(history) < left + right + 1:
        return [], []
    lows: list[tuple[pd.Timestamp, float]] = []
    highs: list[tuple[pd.Timestamp, float]] = []
    data = history.reset_index(drop=True)
    # Last possible pivot excludes the right confirmation bars, so every level is known before the candidate.
    for i in range(left, len(data) - right):
        chunk = data.iloc[i - left : i + right + 1]
        row = data.iloc[i]
        low = float(row["low"])
        high = float(row["high"])
        if low <= float(chunk["low"].min()):
            lows.append((_parse_utc(row["open_time_utc"]), low))
        if high >= float(chunk["high"].max()):
            highs.append((_parse_utc(row["open_time_utc"]), high))
    return lows, highs


def _nearest_levels(history: pd.DataFrame, price: float) -> dict[str, Any]:
    piv_lows, piv_highs = _confirmed_pivots(history)
    support_candidates = [(ts, value) for ts, value in piv_lows if value <= price]
    resistance_candidates = [(ts, value) for ts, value in piv_highs if value >= price]

    if support_candidates:
        support_ts, support = min(support_candidates, key=lambda item: abs(price - item[1]))
    else:
        support_ts, support = (None, float(history["low"].tail(120).min()) if len(history) else price)
    if resistance_candidates:
        resistance_ts, resistance = min(resistance_candidates, key=lambda item: abs(price - item[1]))
    else:
        resistance_ts, resistance = (None, float(history["high"].tail(120).max()) if len(history) else price)

    recent = _window(history, 240)
    tolerance = max(price * 0.0015, 0.01)
    support_touches = int((recent["low"].astype(float).sub(float(support)).abs() <= tolerance).sum()) if len(recent) else 0
    resistance_touches = int((recent["high"].astype(float).sub(float(resistance)).abs() <= tolerance).sum()) if len(recent) else 0
    denom = max(float(resistance) - float(support), 1e-9)
    channel_pos = _clip01((price - float(support)) / denom)
    return {
        "nearest_support_price": float(support),
        "nearest_support_time_utc": _fmt_utc(support_ts) if support_ts is not None else "",
        "distance_to_support_pct": max(0.0, _pct(price, float(support))),
        "support_touch_count": support_touches,
        "nearest_resistance_price": float(resistance),
        "nearest_resistance_time_utc": _fmt_utc(resistance_ts) if resistance_ts is not None else "",
        "distance_to_resistance_pct": max(0.0, _pct(float(resistance), price)),
        "resistance_touch_count": resistance_touches,
        "channel_position_0_1": channel_pos,
        "is_mid_channel": int(0.35 <= channel_pos <= 0.65),
        "is_near_support": int(max(0.0, _pct(price, float(support))) <= 0.20),
        "is_near_resistance": int(max(0.0, _pct(float(resistance), price)) <= 0.20),
    }


def _feature_row(candidate: pd.Series, ohlcv: pd.DataFrame) -> dict[str, Any]:
    entry_time = _parse_utc(candidate["entry_time_utc"])
    context_raw = candidate.get("context_max_open_time_utc") or candidate.get("v2_combo_feature_time_utc") or ""
    if context_raw and str(context_raw).lower() != "nan":
        context_time = _parse_utc(context_raw)
    else:
        context_time = entry_time - pd.Timedelta(minutes=1)
    if context_time >= entry_time:
        context_time = entry_time - pd.Timedelta(minutes=1)

    history = ohlcv[ohlcv["open_time_utc"] <= context_time].copy()
    if history.empty:
        raise ValueError(f"no pre-entry OHLCV for {candidate.get('candidate_id')} at {entry_time}")

    last = history.iloc[-1]
    price = float(last["close"])
    open_ = float(last["open"])
    high = float(last["high"])
    low = float(last["low"])
    volume = float(last["volume"])

    row: dict[str, Any] = {
        "day": normalize_day(candidate.get("day")),
        "candidate_id": str(candidate.get("candidate_id")),
        "record_id": str(candidate.get("record_id")),
        "entry_time_utc": normalize_ts(candidate.get("entry_time_utc")),
        "cs_max_source_time_utc": _fmt_utc(history["open_time_utc"].iloc[-1]),
        "cs_context_rows": int(len(history)),
        "cs_context_before_entry": int(_parse_utc(history["open_time_utc"].iloc[-1]) < entry_time),
        "cs_source_ohlcv": str(candidate.get("v2_combo_source_ohlcv") or candidate.get("source_ohlcv") or ""),
    }

    returns: dict[int, float] = {}
    ranges: dict[int, float] = {}
    for bars in (3, 5, 15, 30, 60, 120, 240):
        returns[bars] = _ret(history, bars)
        ranges[bars] = _range_pct(history, bars)
        row[f"cs_return_{bars}m_pct"] = returns[bars]
        row[f"cs_range_{bars}m_pct"] = ranges[bars]
        row[f"cs_rows_{bars}m"] = int(min(len(history), bars))

    row["cs_trend_slope_15m_pct_per_bar"] = _trend_slope_pct(history, 15)
    row["cs_trend_slope_30m_pct_per_bar"] = _trend_slope_pct(history, 30)
    row["cs_trend_slope_60m_pct_per_bar"] = _trend_slope_pct(history, 60)

    lower_lows, lower_highs, higher_lows, higher_highs = _lower_counts(history, 30)
    row["cs_lower_lows_count_30m"] = lower_lows
    row["cs_lower_highs_count_30m"] = lower_highs
    row["cs_higher_lows_count_30m"] = higher_lows
    row["cs_higher_highs_count_30m"] = higher_highs

    red_streak, green_streak = _streaks(history)
    row["cs_consecutive_red_candles"] = red_streak
    row["cs_consecutive_green_candles"] = green_streak

    tr = _true_range(history)
    atr5 = float(tr.tail(5).mean()) if len(tr) else 0.0
    atr60 = float(tr.tail(60).mean()) if len(tr) else atr5
    atr_exp = atr5 / atr60 if atr60 else 1.0
    vol5 = float(history["volume"].tail(5).mean())
    vol60 = float(history["volume"].tail(60).median()) if len(history) else vol5
    vol_exp = vol5 / vol60 if vol60 else 1.0
    row["cs_atr_expansion_score"] = _clip01((atr_exp - 1.0) / 1.5)
    row["cs_volume_expansion_score"] = _clip01((vol_exp - 1.0) / 2.0)
    row["cs_last_candle_range_pct"] = (high - low) / price * 100.0 if price else 0.0
    row["cs_last_candle_body_pct"] = abs(price - open_) / price * 100.0 if price else 0.0
    row["cs_last_candle_lower_wick_pct"] = (min(open_, price) - low) / price * 100.0 if price else 0.0
    row["cs_last_candle_upper_wick_pct"] = (high - max(open_, price)) / price * 100.0 if price else 0.0
    row["cs_last_candle_volume"] = volume

    recent60 = _window(history, 60)
    recent120 = _window(history, 120)
    recent_low = float(recent60["low"].min()) if len(recent60) else low
    recent_high = float(recent60["high"].max()) if len(recent60) else high
    day_low_so_far = float(history["low"].min())
    day_high_so_far = float(history["high"].max())
    row["cs_recent_low_60m_price"] = recent_low
    row["cs_recent_high_60m_price"] = recent_high
    row["cs_day_low_so_far_price"] = day_low_so_far
    row["cs_day_high_so_far_price"] = day_high_so_far
    row["cs_distance_to_recent_low_pct"] = max(0.0, _pct(price, recent_low))
    row["cs_distance_to_day_low_so_far_pct"] = max(0.0, _pct(price, day_low_so_far))
    row["cs_is_near_recent_low"] = int(row["cs_distance_to_recent_low_pct"] <= 0.15)
    row["cs_is_near_day_low_so_far"] = int(row["cs_distance_to_day_low_so_far_pct"] <= 0.20)
    row["cs_flush_depth_pct"] = (recent_high - recent_low) / price * 100.0 if price else 0.0
    row["cs_bounce_from_recent_low_pct"] = max(0.0, _pct(price, recent_low))
    row["cs_pullback_from_recent_high_pct"] = max(0.0, _pct(recent_high, price))
    row["cs_day_channel_position_0_1"] = _clip01((price - day_low_so_far) / max(day_high_so_far - day_low_so_far, 1e-9))

    prior_support_window = history.iloc[:-5] if len(history) > 10 else history.iloc[:-1]
    prior_support = float(prior_support_window["low"].tail(60).min()) if len(prior_support_window) else recent_low
    row["cs_price_breaking_recent_support"] = int(price < prior_support * 0.999)

    levels = _nearest_levels(history, price)
    for key, value in levels.items():
        row[f"cs_{key}"] = value

    red_ratio15 = float((_window(history, 15)["close"] < _window(history, 15)["open"]).mean()) if len(history) else 0.0
    green_ratio15 = float((_window(history, 15)["close"] > _window(history, 15)["open"]).mean()) if len(history) else 0.0
    neg15 = _clip01(-returns[15] / 0.8)
    neg30 = _clip01(-returns[30] / 1.2)
    pos15 = _clip01(returns[15] / 0.8)
    pos30 = _clip01(returns[30] / 1.2)
    lower_pressure = _clip01((lower_lows + lower_highs) / 30.0)
    higher_pressure = _clip01((higher_lows + higher_highs) / 30.0)

    short_pressure = _clip01(0.30 * neg15 + 0.20 * neg30 + 0.20 * red_ratio15 + 0.20 * lower_pressure + 0.10 * row["cs_atr_expansion_score"])
    long_pressure = _clip01(0.30 * pos15 + 0.20 * pos30 + 0.20 * green_ratio15 + 0.20 * higher_pressure + 0.10 * row["cs_volume_expansion_score"])
    row["cs_short_pressure_now"] = short_pressure
    row["cs_long_pressure_now"] = long_pressure

    accel = _clip01(max(0.0, -returns[3]) / 0.35 + max(0.0, -returns[5]) / 0.60 - max(0.0, -returns[30]) / 2.5)
    row["cs_dump_acceleration_score"] = accel
    row["cs_pre_dump_risk_score"] = _clip01(
        0.34 * short_pressure
        + 0.20 * accel
        + 0.16 * row["cs_price_breaking_recent_support"]
        + 0.14 * row["cs_atr_expansion_score"]
        + 0.10 * row["cs_volume_expansion_score"]
        + 0.06 * row["cs_is_mid_channel"]
    )
    row["cs_falling_knife_active"] = int(
        row["cs_pre_dump_risk_score"] >= 0.58
        and returns[5] < -0.25
        and row["cs_is_near_recent_low"] == 0
    )

    wick_strength = _clip01(row["cs_last_candle_lower_wick_pct"] / max(row["cs_last_candle_body_pct"], 0.02))
    bounce_score = _clip01(row["cs_bounce_from_recent_low_pct"] / 0.35)
    near_low_score = 1.0 - _clip01(row["cs_distance_to_recent_low_pct"] / 0.35)
    decel_score = _clip01(max(0.0, returns[3] - returns[15] / 5.0) / 0.35)
    row["cs_sell_pressure_exhaustion_score"] = _clip01(0.35 * near_low_score + 0.25 * wick_strength + 0.20 * bounce_score + 0.20 * decel_score)
    row["cs_bottom_attempt_score"] = _clip01(0.45 * near_low_score + 0.25 * bounce_score + 0.20 * wick_strength + 0.10 * short_pressure)
    row["cs_base_after_flush_score"] = _clip01(
        0.35 * _clip01(row["cs_flush_depth_pct"] / 1.5)
        + 0.25 * near_low_score
        + 0.25 * (1.0 - _clip01(ranges[15] / max(ranges[60], 0.01)))
        + 0.15 * row["cs_is_near_support"]
    )
    support_price = float(row["cs_nearest_support_price"])
    row["cs_retest_low_count"] = int((recent120["low"].astype(float).sub(support_price).abs() <= max(price * 0.0015, 0.01)).sum()) if len(recent120) else 0

    prior_high = float(history.iloc[:-3]["high"].tail(60).max()) if len(history) > 10 else recent_high
    row["cs_breakout_recent_high"] = int(price > prior_high * 1.001)
    row["cs_pump_pressure_score"] = _clip01(
        0.35 * long_pressure
        + 0.25 * _clip01(returns[15] / 1.0)
        + 0.15 * row["cs_breakout_recent_high"]
        + 0.15 * row["cs_volume_expansion_score"]
        + 0.10 * _clip01(row["cs_day_channel_position_0_1"])
    )
    row["cs_pullback_after_breakout"] = int(row["cs_pump_pressure_score"] >= 0.45 and row["cs_pullback_from_recent_high_pct"] >= 0.15)
    row["cs_trend_continuation_score"] = _clip01(0.40 * long_pressure + 0.25 * _clip01(row["cs_day_channel_position_0_1"]) + 0.20 * higher_pressure + 0.15 * row["cs_is_near_support"])
    row["cs_good_pullback_in_pump_score"] = _clip01(
        0.40 * row["cs_pump_pressure_score"]
        + 0.25 * row["cs_pullback_after_breakout"]
        + 0.20 * row["cs_is_near_support"]
        + 0.15 * near_low_score
    )

    direction = np.sign(_window(history, 30)["close"].astype(float).diff().dropna().to_numpy())
    direction = direction[direction != 0]
    flips = int(np.sum(direction[1:] != direction[:-1])) if len(direction) > 1 else 0
    row["cs_direction_flip_count_30m"] = flips
    row["cs_range_compression_score"] = _clip01(1.0 - ranges[30] / max(ranges[120], 0.01)) if len(history) >= 30 else 0.0
    row["cs_chop_score"] = _clip01(0.35 * _clip01(flips / 12.0) + 0.25 * row["cs_range_compression_score"] + 0.20 * (1.0 - abs(pos15 - neg15)) + 0.20 * row["cs_is_mid_channel"])
    row["cs_low_edge_zone"] = int(row["cs_channel_position_0_1"] <= 0.25 or row["cs_day_channel_position_0_1"] <= 0.25)
    row["cs_no_trade_chop_score"] = _clip01(0.60 * row["cs_chop_score"] + 0.25 * row["cs_is_mid_channel"] + 0.15 * (1 - row["cs_low_edge_zone"]))

    return row


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


def _default_paths(day: str) -> dict[str, Path]:
    compact = compact_day(day)
    base = Path("STAS5_ML_CORE") / "artifacts" / "v5" / "market_passports" / compact
    return {
        "base": base,
        "ml_ready": base / f"STAS5_V5_MARKET_PASSPORT_{compact}_ML_READY_274F_ENTRY_PHASE_STATE_REASON_TARGETS_V2.csv",
        "allowlist": base / f"STAS5_V5_MARKET_PASSPORT_{compact}_FEATURE_ALLOWLIST_274_ENTRY_PHASE_STATE_REASON_V2.json",
        "causal_features": base / f"STAS5_V5_MARKET_PASSPORT_{compact}_CAUSAL_STRUCTURE_FEATURES_V1.csv",
        "ml_ready_plus": base / f"STAS5_V5_MARKET_PASSPORT_{compact}_ML_READY_274F_PLUS_CAUSAL_STRUCTURE_TARGETS_V1.csv",
        "causal_allowlist": base / f"STAS5_V5_MARKET_PASSPORT_{compact}_FEATURE_ALLOWLIST_274_PLUS_CAUSAL_STRUCTURE_V1.json",
        "guard": base / f"STAS5_V5_MARKET_PASSPORT_{compact}_CAUSAL_STRUCTURE_GUARD_V1.json",
        "audit": base / f"STAS5_V5_MARKET_PASSPORT_{compact}_CAUSAL_STRUCTURE_AUDIT_RU.md",
    }


def _infer_ohlcv_path(rows: pd.DataFrame, explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit
    for column in ["v2_combo_source_ohlcv", "source_ohlcv", "cs_source_ohlcv"]:
        if column in rows.columns:
            values = rows[column].dropna().astype(str)
            if not values.empty:
                return PROJECT_ROOT / values.iloc[0]
    day = normalize_day(rows["day"].iloc[0])
    return PROJECT_ROOT / f"data/core/bybit_ohlcv/dt={day}/tf={TIMEFRAME}/symbol={SYMBOL}/part-final.csv"


def _ordered_ml_columns(plus: pd.DataFrame, original_columns: list[str], causal_columns: list[str]) -> list[str]:
    out = list(original_columns)
    for column in causal_columns:
        if column not in out:
            out.append(column)
    return out


def build_causal_structure_package(
    *,
    day: str,
    ml_ready_path: Path | None = None,
    allowlist_path: Path | None = None,
    ohlcv_path: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    paths = _default_paths(day)
    if output_dir is not None:
        compact = compact_day(day)
        paths["base"] = output_dir
        paths["causal_features"] = output_dir / f"STAS5_V5_MARKET_PASSPORT_{compact}_CAUSAL_STRUCTURE_FEATURES_V1.csv"
        paths["ml_ready_plus"] = output_dir / f"STAS5_V5_MARKET_PASSPORT_{compact}_ML_READY_274F_PLUS_CAUSAL_STRUCTURE_TARGETS_V1.csv"
        paths["causal_allowlist"] = output_dir / f"STAS5_V5_MARKET_PASSPORT_{compact}_FEATURE_ALLOWLIST_274_PLUS_CAUSAL_STRUCTURE_V1.json"
        paths["guard"] = output_dir / f"STAS5_V5_MARKET_PASSPORT_{compact}_CAUSAL_STRUCTURE_GUARD_V1.json"
        paths["audit"] = output_dir / f"STAS5_V5_MARKET_PASSPORT_{compact}_CAUSAL_STRUCTURE_AUDIT_RU.md"
    ml_ready = ml_ready_path or paths["ml_ready"]
    allowlist = allowlist_path or paths["allowlist"]
    if not ml_ready.exists():
        raise FileNotFoundError(f"ML-ready source not found: {ml_ready}")
    if not allowlist.exists():
        raise FileNotFoundError(f"allowlist not found: {allowlist}")

    rows = pd.read_csv(ml_ready, encoding="utf-8-sig")
    base_features = load_manifest_feature_columns(allowlist)
    ohlcv_file = _infer_ohlcv_path(rows, ohlcv_path)
    if not ohlcv_file.exists():
        raise FileNotFoundError(f"OHLCV not found: {ohlcv_file}")
    ohlcv = _load_ohlcv(ohlcv_file)

    causal_rows = [_feature_row(row, ohlcv) for _, row in rows.iterrows()]
    causal = pd.DataFrame(causal_rows)
    key_cols = ["day", "candidate_id", "record_id", "entry_time_utc"]
    causal_feature_columns = [
        column
        for column in causal.columns
        if column.startswith("cs_")
        and column not in {"cs_source_ohlcv", "cs_max_source_time_utc"}
        and not column.endswith("_time_utc")
    ]
    # Keep source-time fields as metadata, not model features.
    causal_metadata_columns = [column for column in causal.columns if column not in key_cols + causal_feature_columns]

    plus = rows.merge(causal, on=key_cols, how="left", validate="one_to_one", indicator=True)
    merge_missing = int((plus["_merge"] != "both").sum())
    plus = plus.drop(columns=["_merge"])

    all_feature_columns = list(base_features) + [column for column in causal_feature_columns if column not in base_features]
    forbidden_base = forbidden_feature_matches(base_features)
    forbidden_causal = {
        column: [bad for bad in FORBIDDEN_DIRECT_FEATURE_SUBSTRINGS if bad in column.lower()]
        for column in causal_feature_columns
        if any(bad in column.lower() for bad in FORBIDDEN_DIRECT_FEATURE_SUBSTRINGS)
    }
    target_in_features = [column for column in all_feature_columns if column in TARGET_COLUMNS]
    manual_in_causal = [column for column in causal_feature_columns if column in TARGET_COLUMNS]
    context_false = int((pd.to_numeric(causal["cs_context_before_entry"], errors="coerce").fillna(0).astype(int) != 1).sum())
    source_times = pd.to_datetime(causal["cs_max_source_time_utc"], utc=True)
    entry_times = pd.to_datetime(causal["entry_time_utc"], utc=True)
    source_after_entry = int((source_times >= entry_times).sum())
    missing_numeric = int(causal[causal_feature_columns].isna().sum().sum())
    duplicate_keys = int(causal.duplicated(["day", "candidate_id", "record_id"]).sum())

    checks = [
        {"check": "rows_match", "status": "PASS" if len(rows) == len(causal) == len(plus) else "FAIL", "details": {"ml_rows": int(len(rows)), "causal_rows": int(len(causal)), "plus_rows": int(len(plus))}},
        {"check": "merge_one_to_one", "status": "PASS" if merge_missing == 0 and duplicate_keys == 0 else "FAIL", "details": {"merge_missing": merge_missing, "duplicate_keys": duplicate_keys}},
        {"check": "base_feature_count_274", "status": "PASS" if len(base_features) == 274 else "FAIL", "details": {"base_feature_count": len(base_features)}},
        {"check": "causal_feature_count_positive", "status": "PASS" if len(causal_feature_columns) > 0 else "FAIL", "details": {"causal_feature_count": len(causal_feature_columns)}},
        {"check": "source_time_before_entry", "status": "PASS" if context_false == 0 and source_after_entry == 0 else "FAIL", "details": {"context_false": context_false, "source_after_entry": source_after_entry}},
        {"check": "forbidden_base_features_absent", "status": "PASS" if not forbidden_base else "FAIL", "details": forbidden_base},
        {"check": "forbidden_causal_features_absent", "status": "PASS" if not forbidden_causal else "FAIL", "details": forbidden_causal},
        {"check": "targets_not_in_features", "status": "PASS" if not target_in_features and not manual_in_causal else "FAIL", "details": {"target_in_features": target_in_features, "manual_in_causal": manual_in_causal}},
        {"check": "causal_values_not_missing", "status": "PASS" if missing_numeric == 0 else "FAIL", "details": {"missing_numeric_values": missing_numeric}},
    ]
    status = STATUS if all(item["status"] == "PASS" for item in checks) else "FAIL_CAUSAL_STRUCTURE_GUARD"

    ensure_parent(paths["causal_features"])
    causal.to_csv(paths["causal_features"], index=False, encoding="utf-8-sig")
    plus = plus[_ordered_ml_columns(plus, list(rows.columns), [column for column in causal.columns if column not in key_cols])]
    plus.to_csv(paths["ml_ready_plus"], index=False, encoding="utf-8-sig")

    feature_allowlist = {
        "status": status,
        "created_utc": utc_now(),
        "day": day,
        "schema_version": 1,
        "source_base_allowlist": rel(allowlist),
        "source_ml_ready": rel(ml_ready),
        "source_ohlcv": rel(ohlcv_file),
        "feature_columns": all_feature_columns,
        "feature_count": len(all_feature_columns),
        "base_feature_columns": base_features,
        "base_feature_count": len(base_features),
        "causal_structure_feature_columns": causal_feature_columns,
        "causal_structure_feature_count": len(causal_feature_columns),
        "causal_structure_metadata_columns": causal_metadata_columns,
        "target_columns": [column for column in TARGET_COLUMNS if column in plus.columns],
        "guardrails": [
            "causal_structure_features_use_only_ohlcv_open_time_lte_context_max_open_time_utc",
            "cs_max_source_time_utc_must_be_less_than_entry_time_utc",
            "manual_entry_y_phase_y_state_y_reason_y_are_targets_not_features",
            "no_future_postfact_hit_tp_stas3_exit_old_ml_decision_columns_in_features",
        ],
    }
    write_json(paths["causal_allowlist"], feature_allowlist)

    guard = {
        "status": status,
        "created_utc": utc_now(),
        "day": day,
        "rows": int(len(plus)),
        "base_feature_count": len(base_features),
        "causal_structure_feature_count": len(causal_feature_columns),
        "feature_count": len(all_feature_columns),
        "outputs": {
            "causal_structure_features": str(paths["causal_features"].resolve()),
            "ml_ready_274f_plus_causal_structure_targets": str(paths["ml_ready_plus"].resolve()),
            "feature_allowlist_274_plus_causal_structure": str(paths["causal_allowlist"].resolve()),
            "causal_structure_audit_ru": str(paths["audit"].resolve()),
        },
        "sources": {
            "ml_ready_274f_entry_phase_state_reason_targets_v2": str(ml_ready.resolve()),
            "feature_allowlist_274_entry_phase_state_reason_v2": str(allowlist.resolve()),
            "ohlcv": str(ohlcv_file.resolve()),
        },
        "checks": checks,
        "feature_columns": all_feature_columns,
        "causal_structure_feature_columns": causal_feature_columns,
    }
    write_json(paths["guard"], guard)

    audit = [
        f"# STAS5 V5 Causal Structure Audit {day}",
        "",
        f"Статус: `{status}`.",
        "",
        "## Что Сделано",
        "",
        "Создан отдельный causal market-structure builder. Он считает рыночную структуру по каждому кандидату только по свечам, доступным до `entry_time_utc`.",
        "",
        "## Файлы",
        "",
        f"- causal features: `{rel(paths['causal_features'])}`",
        f"- ML-ready plus causal: `{rel(paths['ml_ready_plus'])}`",
        f"- allowlist: `{rel(paths['causal_allowlist'])}`",
        f"- guard: `{rel(paths['guard'])}`",
        "",
        "## Счетчики",
        "",
        f"- rows: `{len(plus)}`",
        f"- old features: `{len(base_features)}`",
        f"- causal features: `{len(causal_feature_columns)}`",
        f"- total features: `{len(all_feature_columns)}`",
        "",
        "## Guard",
        "",
    ]
    for item in checks:
        audit.append(f"- `{item['check']}`: `{item['status']}`")
    audit.extend(
        [
            "",
            "## Важная Граница",
            "",
            "`entry_y`, `phase_y`, `state_y`, `reason_y` остаются ответами учителя. В `X` они не входят.",
            "Новые `cs_*` признаки считаются из OHLCV до текущего кандидата и могут использоваться как live-compatible features.",
            "",
        ]
    )
    paths["audit"].write_text("\n".join(audit), encoding="utf-8")

    return guard


def main() -> int:
    parser = argparse.ArgumentParser(description="Build STAS5 V5 causal market-structure features.")
    parser.add_argument("--day", required=True)
    parser.add_argument("--ml-ready-path", default="")
    parser.add_argument("--allowlist-path", default="")
    parser.add_argument("--ohlcv-path", default="")
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()

    guard = build_causal_structure_package(
        day=args.day,
        ml_ready_path=Path(args.ml_ready_path) if args.ml_ready_path else None,
        allowlist_path=Path(args.allowlist_path) if args.allowlist_path else None,
        ohlcv_path=Path(args.ohlcv_path) if args.ohlcv_path else None,
        output_dir=Path(args.output_dir) if args.output_dir else None,
    )
    print(json.dumps({"status": guard["status"], "rows": guard["rows"], "feature_count": guard["feature_count"]}, ensure_ascii=False))
    if not args.no_strict and guard["status"] != STATUS:
        raise SystemExit(2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
