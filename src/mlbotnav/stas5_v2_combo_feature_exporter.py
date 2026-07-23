from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from mlbotnav.stas5_common import (
    DEFAULT_STAS2_TRAIN_RUN_DIR,
    PROJECT_ROOT,
    STAS5_ARTIFACTS_DIR,
    TRAIN_END_DAY,
    TRAIN_START_DAY,
    forbidden_feature_matches,
    iter_days,
    normalize_day,
    normalize_ts,
    read_csv,
    rel,
    utc_now,
    write_json,
)
from mlbotnav.visual_entry_low_anchor_suggester import _load_ohlcv, _source_csv
from mlbotnav.visual_entry_strategy_passport_overlay_v2d_patterns import _add_pattern_features
from mlbotnav.visual_entry_stas4_family_overlay import (
    _add_combo_spectrum_features,
    _add_density_profile_features,
    _add_price_volatility_features,
    _add_volume_flow_features,
    _divergence_segments,
    _structure_context,
    _structure_votes,
)


STATUS = "STAS5_V2_COMBO_FEATURE_EXPORTER_READY_CAUSAL_NO_TP_NO_API_NO_STAS3"
SYMBOL = "SOLUSDT"
TIMEFRAME = "1m"

V2_COMBO_BASENAME = "stas5_v2_combo_features_20260501_20260514_v0"
DEFAULT_V2_COMBO_FEATURE_PATH = STAS5_ARTIFACTS_DIR / "v2" / "features" / f"{V2_COMBO_BASENAME}.csv"
DEFAULT_V2_COMBO_MANIFEST_PATH = STAS5_ARTIFACTS_DIR / "v2" / "features" / f"{V2_COMBO_BASENAME}.manifest.json"

METADATA_COLUMNS = [
    "day",
    "candidate_id",
    "record_id",
    "anchor_time_utc",
    "entry_time_utc",
    "feature_time_utc",
    "feature_available_before_entry",
    "entry_price_5bps",
    "source_stas2_run",
    "source_ohlcv",
    "audit_no_trade_reason",
]


@dataclass(frozen=True)
class DayContext:
    day: str
    ohlcv_source: str
    enriched: pd.DataFrame
    pivots_3: Any
    pivots_10: Any
    divergences: list[dict[str, Any]]


def _fmt_ts(value: Any) -> str:
    if value is None or str(value).strip() == "":
        return ""
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe_float(value: Any, default: float = math.nan) -> float:
    try:
        if value is None:
            return default
        out = float(value)
        if not math.isfinite(out):
            return default
        return out
    except Exception:
        return default


def _flag(value: Any) -> int:
    if isinstance(value, bool):
        return int(value)
    text = str(value or "").strip().lower()
    if text in {"1", "true", "yes", "y"}:
        return 1
    return 0


def _boolish(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y"}:
        return True
    try:
        return bool(int(float(text)))
    except Exception:
        return False


def _clip(value: float, low: float, high: float, default: float = 0.0) -> float:
    if not math.isfinite(value):
        return default
    return float(max(low, min(high, value)))


def _zone_code(value: float, levels: tuple[float, float, float, float]) -> int:
    if not math.isfinite(value):
        return -1
    a, b, c, d = levels
    if value < a:
        return 0
    if value < b:
        return 1
    if value < c:
        return 2
    if value < d:
        return 3
    return 4


def _event_code(value: Any) -> int:
    text = str(value or "").strip().upper()
    mapping = {
        "BREAK_UP": 1,
        "BREAK_DOWN": -1,
        "BOS_UP": 2,
        "BOS_DOWN": -2,
        "UP_RETEST_SUPPORT": 3,
        "DOWN_RETEST_RESISTANCE": -3,
    }
    return mapping.get(text, 0)


def _divergence_code(value: Any) -> int:
    text = str(value or "").strip()
    mapping = {
        "bullish_divergence": 1,
        "hidden_bullish_divergence": 2,
        "bearish_divergence": -1,
        "hidden_bearish_divergence": -2,
    }
    return mapping.get(text, 0)


def _short_wave_rank(down_pct: float) -> int:
    if not math.isfinite(down_pct):
        return -1
    thresholds = (0.10, 0.20, 0.35, 0.60, 1.00)
    for idx, upper in enumerate(thresholds):
        if down_pct < upper:
            return idx
    return len(thresholds)


def _load_stas2_records(stas2_run_dir: Path) -> pd.DataFrame:
    path = stas2_run_dir / "STAS2_RECORDS.csv"
    if not path.exists():
        raise FileNotFoundError(f"STAS2_RECORDS.csv not found: {path}")
    out = read_csv(path).copy()
    updates = {
        "day": out["day"].map(normalize_day) if "day" in out else out["day_utc"].map(normalize_day),
        "anchor_time_utc": out["anchor_time_utc"].map(normalize_ts),
        "entry_time_utc": out["entry_time_utc"].map(normalize_ts),
        "candidate_id": out["candidate_id"].astype(str),
        "record_id": out["record_id"].astype(str),
        "source_stas2_run": rel(stas2_run_dir),
    }
    out = pd.concat([out.drop(columns=[column for column in updates if column in out.columns]), pd.DataFrame(updates, index=out.index)], axis=1)
    return out


def _prepare_candidates(stas2: pd.DataFrame, *, start_day: str, end_day: str, source_stas2_run: str) -> pd.DataFrame:
    out = stas2.copy()
    if "day" not in out:
        out["day"] = out["day_utc"].map(normalize_day)
    else:
        out["day"] = out["day"].map(normalize_day)
    out["anchor_time_utc"] = out["anchor_time_utc"].map(normalize_ts)
    out["entry_time_utc"] = out["entry_time_utc"].map(normalize_ts)
    out["candidate_id"] = out["candidate_id"].astype(str)
    out["record_id"] = out["record_id"].astype(str)
    out["source_stas2_run"] = source_stas2_run
    allowed_days = set(iter_days(start_day, end_day))
    out = out[out["day"].isin(allowed_days)].copy()
    return out.sort_values(["day", "entry_time_utc", "record_id"]).reset_index(drop=True)


def _prepare_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["open_time_utc"] = pd.to_datetime(out["open_time_utc"], utc=True, errors="raise", format="mixed")
    if "close_time_utc" in out:
        out["close_time_utc"] = pd.to_datetime(out["close_time_utc"], utc=True, errors="raise", format="mixed")
    for column in ["open", "high", "low", "close", "volume"]:
        out[column] = out[column].astype(float)
    return out.sort_values("open_time_utc").reset_index(drop=True)


def _build_day_context(day: str, day_df: pd.DataFrame, *, ohlcv_source: str) -> DayContext:
    enriched = _prepare_ohlcv(day_df)
    enriched = _add_price_volatility_features(enriched)
    enriched = _add_combo_spectrum_features(enriched)
    enriched = _add_volume_flow_features(enriched)
    enriched = _add_density_profile_features(enriched)
    enriched = _add_pattern_features(enriched)
    enriched, pivots_3, pivots_10 = _structure_context(enriched)
    divergences = _divergence_segments(enriched, left=3, right=3)
    return DayContext(day=day, ohlcv_source=ohlcv_source, enriched=enriched, pivots_3=pivots_3, pivots_10=pivots_10, divergences=divergences)


def _idx_at_or_before(df: pd.DataFrame, time_utc: Any) -> int | None:
    if time_utc is None or str(time_utc).strip() == "":
        return None
    ts = pd.Timestamp(time_utc)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    ts = ts.tz_convert("UTC")
    matched = df.index[df["open_time_utc"] <= ts].tolist()
    if not matched:
        return None
    return int(matched[-1])


def _recent_divergence_features(divergences: list[dict[str, Any]], idx: int, *, lookback: int = 60) -> dict[str, Any]:
    available = [item for item in divergences if int(item.get("confirm_idx", 10**9)) <= idx]
    recent = [item for item in available if idx - int(item.get("confirm_idx", 10**9)) <= lookback]
    kinds = {str(item.get("kind") or "") for item in recent}
    latest = recent[-1] if recent else None
    latest_age = None if latest is None else idx - int(latest.get("confirm_idx", idx))
    bullish = [item for item in recent if "bullish" in str(item.get("kind") or "")]
    bearish = [item for item in recent if "bearish" in str(item.get("kind") or "")]
    return {
        "stas4_v2_div_bullish_recent": int("bullish_divergence" in kinds),
        "stas4_v2_div_hidden_bullish_recent": int("hidden_bullish_divergence" in kinds),
        "stas4_v2_div_bearish_recent": int("bearish_divergence" in kinds),
        "stas4_v2_div_hidden_bearish_recent": int("hidden_bearish_divergence" in kinds),
        "stas4_v2_div_recent_age_bars": -1 if latest_age is None else int(latest_age),
        "stas4_v2_div_bullish_age_bars": -1 if not bullish else int(idx - int(bullish[-1]["confirm_idx"])),
        "stas4_v2_div_bearish_age_bars": -1 if not bearish else int(idx - int(bearish[-1]["confirm_idx"])),
        "stas4_v2_div_type_code": 0 if latest is None else _divergence_code(latest.get("kind")),
        "stas4_v2_div_confirmed_count_60": len(recent),
    }


def _recent_bool(enriched: pd.DataFrame, idx: int, columns: list[str], lookback: int) -> dict[str, bool]:
    start = max(0, idx - lookback + 1)
    win = enriched.iloc[start : idx + 1]
    out: dict[str, bool] = {}
    for column in columns:
        if column not in win:
            out[column] = False
        else:
            out[column] = bool(win[column].fillna(False).astype(bool).any())
    return out


def _pattern_features(enriched: pd.DataFrame, idx: int) -> dict[str, Any]:
    row = enriched.iloc[idx]
    candle_flags = _recent_bool(
        enriched,
        idx,
        [
            "pin_bar_bull_flag",
            "hammer_flag",
            "engulf_bull_flag",
            "doji_flag",
            "inside_bar_flag",
            "pin_bar_bear_flag",
            "shooting_star_flag",
            "engulf_bear_flag",
        ],
        3,
    )
    div_flags = _recent_bool(enriched, idx, ["rsi_bull_div_flag", "macd_bull_div_flag", "obv_bull_div_flag"], 8)
    chart_flags = _recent_bool(enriched, idx, ["double_bottom_like", "range_flag", "wedge_falling_like"], 8)
    confirm_flags = _recent_bool(enriched, idx, ["volume_confirm", "level_confirm_long"], 3)
    bull_candle = any(candle_flags[key] for key in ["pin_bar_bull_flag", "hammer_flag", "engulf_bull_flag", "doji_flag", "inside_bar_flag"])
    bear_candle = any(candle_flags[key] for key in ["pin_bar_bear_flag", "shooting_star_flag", "engulf_bear_flag"])
    bull_div = any(div_flags.values())
    chart_long = any(chart_flags.values())
    confirm = any(confirm_flags.values())
    strength = _safe_float(row.get("pattern_strength"), 0.0)
    age = _safe_float(row.get("pattern_age_bars"), 99.0)
    return {
        "stas4_v2_pattern_bull_candle_recent3": int(bull_candle),
        "stas4_v2_pattern_bear_candle_recent3": int(bear_candle),
        "stas4_v2_pattern_bull_divergence_recent8": int(bull_div),
        "stas4_v2_pattern_chart_long_recent8": int(chart_long),
        "stas4_v2_pattern_confirm_recent3": int(confirm),
        "stas4_v2_pattern_long_composite": int(_boolish(row.get("pattern_long_composite"))),
        "stas4_v2_pattern_strength": strength,
        "stas4_v2_pattern_age_bars": age,
        "stas4_v2_pattern_volume_ratio20": _safe_float(row.get("volume_ratio20"), 0.0),
        "stas4_v2_pattern_range_pos60_prior": _safe_float(row.get("range_pos60_prior"), 0.5),
        "stas4_v2_pattern_pin_bar_bull_recent3": int(candle_flags["pin_bar_bull_flag"]),
        "stas4_v2_pattern_hammer_recent3": int(candle_flags["hammer_flag"]),
        "stas4_v2_pattern_engulf_bull_recent3": int(candle_flags["engulf_bull_flag"]),
        "stas4_v2_pattern_doji_recent3": int(candle_flags["doji_flag"]),
        "stas4_v2_pattern_inside_bar_recent3": int(candle_flags["inside_bar_flag"]),
        "stas4_v2_pattern_pin_bar_bear_recent3": int(candle_flags["pin_bar_bear_flag"]),
        "stas4_v2_pattern_shooting_star_recent3": int(candle_flags["shooting_star_flag"]),
        "stas4_v2_pattern_engulf_bear_recent3": int(candle_flags["engulf_bear_flag"]),
        "stas4_v2_pattern_double_bottom_recent8": int(chart_flags["double_bottom_like"]),
        "stas4_v2_pattern_range_recent8": int(chart_flags["range_flag"]),
        "stas4_v2_pattern_wedge_falling_recent8": int(chart_flags["wedge_falling_like"]),
        "stas4_v2_pattern_volume_confirm_recent3": int(confirm_flags["volume_confirm"]),
        "stas4_v2_pattern_level_confirm_recent3": int(confirm_flags["level_confirm_long"]),
    }


def _short_wave_features(enriched: pd.DataFrame, idx: int) -> dict[str, Any]:
    out: dict[str, Any] = {}
    max_rank = -1
    max_down = 0.0
    active_count = 0
    for minutes in (5, 15, 30, 60):
        start = max(0, idx - minutes + 1)
        win = enriched.iloc[start : idx + 1]
        if win.empty:
            down_pct = math.nan
            down_to_close_pct = math.nan
            bounce_pct = math.nan
            rank = -1
        else:
            high_values = win["high"].astype(float)
            high_pos = int(high_values.values.argmax())
            high_price = float(high_values.iloc[high_pos])
            after_high = win.iloc[high_pos:]
            low_price = float(after_high["low"].astype(float).min())
            last_close = float(win.iloc[-1]["close"])
            down_pct = (high_price - low_price) / high_price * 100.0 if high_price else math.nan
            down_to_close_pct = (high_price - last_close) / high_price * 100.0 if high_price else math.nan
            bounce_pct = (last_close / low_price - 1.0) * 100.0 if low_price else math.nan
            rank = _short_wave_rank(down_pct)
        if math.isfinite(down_pct):
            max_down = max(max_down, down_pct)
        if rank >= 2:
            active_count += 1
        max_rank = max(max_rank, rank)
        prefix = f"stas5_v2_short_wave_{minutes}m"
        out[f"{prefix}_down_from_high_pct"] = down_pct
        out[f"{prefix}_down_from_high_to_last_close_pct"] = down_to_close_pct
        out[f"{prefix}_bounce_from_post_low_pct"] = bounce_pct
        out[f"{prefix}_phase_rank"] = rank
    out["stas5_v2_short_wave_max_rank_5_15_30_60"] = max_rank
    out["stas5_v2_short_wave_max_down_from_high_pct"] = max_down
    out["stas5_v2_short_wave_active_window_count"] = active_count
    return out


def _indicator_features(enriched: pd.DataFrame, idx: int) -> dict[str, Any]:
    row = enriched.iloc[idx]
    prev = enriched.iloc[idx - 1] if idx > 0 else row
    rsi = _safe_float(row.get("F012_rsi14"))
    rsi_signal = _safe_float(row.get("combo_rsi_signal"))
    macd_hist = _safe_float(row.get("F015_macd_hist"))
    macd_hist_delta = _safe_float(row.get("F015_macd_hist_delta"))
    macd_hist_norm = _safe_float(row.get("combo_macd_hist_norm"))
    stoch_k = _safe_float(row.get("F017_stoch_k14"))
    stoch_d = _safe_float(row.get("F018_stoch_d14"))
    prev_k = _safe_float(prev.get("F017_stoch_k14"))
    prev_d = _safe_float(prev.get("F018_stoch_d14"))
    stoch_diff = stoch_k - stoch_d if math.isfinite(stoch_k) and math.isfinite(stoch_d) else math.nan
    rsi_component = _clip((rsi - 50.0) / 50.0, -1.0, 1.0)
    macd_component = math.tanh(macd_hist_norm / 5.0) if math.isfinite(macd_hist_norm) else 0.0
    stoch_component = _clip(stoch_diff / 100.0, -1.0, 1.0)
    momentum_score = 0.40 * rsi_component + 0.40 * macd_component + 0.20 * stoch_component
    short_pressure_bits = [
        rsi < 45.0 if math.isfinite(rsi) else False,
        macd_hist_norm < 0.0 if math.isfinite(macd_hist_norm) else False,
        macd_hist_delta < 0.0 if math.isfinite(macd_hist_delta) else False,
        stoch_diff < 0.0 if math.isfinite(stoch_diff) else False,
        _safe_float(row.get("F009_ema_gap"), 0.0) < 0.0,
    ]
    long_recovery_bits = [
        rsi > rsi_signal if math.isfinite(rsi) and math.isfinite(rsi_signal) else False,
        macd_hist_delta > 0.0 if math.isfinite(macd_hist_delta) else False,
        prev_k <= prev_d and stoch_k > stoch_d
        if all(math.isfinite(value) for value in [prev_k, prev_d, stoch_k, stoch_d])
        else False,
        rsi <= 45.0 and macd_hist_delta > 0.0 if math.isfinite(rsi) and math.isfinite(macd_hist_delta) else False,
    ]
    return {
        "stas4_v2_indicator_atr14_pct": _safe_float(row.get("F008_atr14")),
        "stas4_v2_indicator_adx14": _safe_float(row.get("F016_adx14")),
        "stas4_v2_combo_atr14_pct": _safe_float(row.get("combo_atr14_pct")),
        "stas4_v2_combo_rsi14": rsi,
        "stas4_v2_combo_rsi_signal9": rsi_signal,
        "stas4_v2_combo_rsi_minus_signal": rsi - rsi_signal if math.isfinite(rsi) and math.isfinite(rsi_signal) else math.nan,
        "stas4_v2_combo_rsi_slope3": rsi - _safe_float(enriched.iloc[max(0, idx - 3)].get("F012_rsi14")) if idx > 0 else 0.0,
        "stas4_v2_combo_rsi_zone_code": _zone_code(rsi, (30.0, 45.0, 55.0, 70.0)),
        "stas4_v2_combo_macd_line": _safe_float(row.get("F013_macd_line")),
        "stas4_v2_combo_macd_signal": _safe_float(row.get("F014_macd_signal")),
        "stas4_v2_combo_macd_hist": macd_hist,
        "stas4_v2_combo_macd_hist_delta": macd_hist_delta,
        "stas4_v2_combo_macd_hist_norm": macd_hist_norm,
        "stas4_v2_combo_macd_state_code": 1 if macd_hist_norm > 0 else (-1 if macd_hist_norm < 0 else 0),
        "stas4_v2_combo_macd_improving": int(macd_hist_delta > 0.0) if math.isfinite(macd_hist_delta) else 0,
        "stas4_v2_combo_macd_falling": int(macd_hist_delta < 0.0) if math.isfinite(macd_hist_delta) else 0,
        "stas4_v2_combo_stoch_k14": stoch_k,
        "stas4_v2_combo_stoch_d14": stoch_d,
        "stas4_v2_combo_stoch_k_minus_d": stoch_diff,
        "stas4_v2_combo_stoch_zone_code": _zone_code(stoch_k, (20.0, 40.0, 60.0, 80.0)),
        "stas4_v2_combo_stoch_cross_up": int(prev_k <= prev_d and stoch_k > stoch_d)
        if all(math.isfinite(value) for value in [prev_k, prev_d, stoch_k, stoch_d])
        else 0,
        "stas4_v2_combo_stoch_cross_down": int(prev_k >= prev_d and stoch_k < stoch_d)
        if all(math.isfinite(value) for value in [prev_k, prev_d, stoch_k, stoch_d])
        else 0,
        "stas4_v2_combo_ema20_ema50_gap_pct": _safe_float(row.get("F009_ema_gap")),
        "stas4_v2_combo_ema20_slope5_pct": _safe_float(row.get("F010_ema20_slope_5")),
        "stas4_v2_combo_ema200_gap_pct": _safe_float(row.get("F011_ema200_gap")),
        "stas4_v2_combo_momentum_score": round(float(momentum_score), 6),
        "stas4_v2_combo_short_pressure_score": round(float(sum(short_pressure_bits) / len(short_pressure_bits)), 6),
        "stas4_v2_combo_long_recovery_score": round(float(sum(long_recovery_bits) / len(long_recovery_bits)), 6),
    }


def _density_features(enriched: pd.DataFrame, idx: int) -> dict[str, Any]:
    row = enriched.iloc[idx]
    dist60 = _safe_float(row.get("density_vpoc_distance_60_pct"))
    dist240 = _safe_float(row.get("density_vpoc_distance_240_pct"))
    cluster60 = _safe_float(row.get("density_cluster_share_60"), 0.0)
    cluster240 = _safe_float(row.get("density_cluster_share_240"), 0.0)
    ratio = _safe_float(row.get("F034_cluster_ratio_60_240"), math.nan)
    near60 = int(math.isfinite(dist60) and abs(dist60) <= 0.20)
    near240 = int(math.isfinite(dist240) and abs(dist240) <= 0.35)
    dense60 = int(cluster60 >= 0.35)
    local_stronger = int(math.isfinite(ratio) and ratio >= 1.05)
    support_score = near60 + near240 + dense60 + local_stronger
    conflict_score = int(math.isfinite(dist60) and dist60 > 0.60) + int(math.isfinite(dist240) and dist240 > 0.90) + int(cluster60 < 0.12)
    return {
        "stas4_v2_density_vpoc60_dist_pct": dist60,
        "stas4_v2_density_bin_share_60": _safe_float(row.get("density_bin_share_60")),
        "stas4_v2_density_cluster_share_60": cluster60,
        "stas4_v2_density_vpoc_share_60": _safe_float(row.get("density_vpoc_share_60")),
        "stas4_v2_density_vpoc240_dist_pct": dist240,
        "stas4_v2_density_bin_share_240": _safe_float(row.get("density_bin_share_240")),
        "stas4_v2_density_cluster_share_240": cluster240,
        "stas4_v2_density_vpoc_share_240": _safe_float(row.get("density_vpoc_share_240")),
        "stas4_v2_density_vpoc_drift20": _safe_float(row.get("F033_vpoc_drift_20")),
        "stas4_v2_density_local_vs_long_ratio": ratio,
        "stas4_v2_density_near_vpoc60": near60,
        "stas4_v2_density_near_vpoc240": near240,
        "stas4_v2_density_cluster60_strength": dense60,
        "stas4_v2_density_local_stronger_than_long": local_stronger,
        "stas4_v2_density_vpoc_drift_state_code": 1
        if _safe_float(row.get("F033_vpoc_drift_20"), 0.0) > 0.05
        else (-1 if _safe_float(row.get("F033_vpoc_drift_20"), 0.0) < -0.05 else 0),
        "stas4_v2_density_support_score": support_score,
        "stas4_v2_density_conflict_score": conflict_score,
    }


def _structure_features(context: DayContext, idx: int) -> dict[str, Any]:
    state = _structure_votes(context.enriched, context.pivots_3, context.pivots_10, idx)
    levels = state.get("levels") or {}
    fib = state.get("fib") or {}
    channel = state.get("channel") or {}
    breakout = state.get("breakout") or {}
    internal = state.get("internal") or {}
    external = state.get("external") or {}
    row = context.enriched.iloc[idx]
    close = _safe_float(row.get("close"))
    fib_levels = fib.get("levels") or {}
    fib_0382 = _safe_float(fib_levels.get("0.382"))
    fib_0618 = _safe_float(fib_levels.get("0.618"))
    fib_0382_dist = (close / fib_0382 - 1.0) * 100.0 if math.isfinite(close) and math.isfinite(fib_0382) and fib_0382 else math.nan
    fib_0618_dist = (close / fib_0618 - 1.0) * 100.0 if math.isfinite(close) and math.isfinite(fib_0618) and fib_0618 else math.nan
    channel_pos = _safe_float(state.get("channel_pos"))
    range_pos = _safe_float(state.get("range_pos_240"), 0.5)
    support_score = (
        _flag(state.get("support_hint"))
        + _flag(state.get("range_hint"))
        + _flag(state.get("fib_hint"))
        + _flag(state.get("retest_hint"))
        + _flag(state.get("structure_hint"))
        + int(math.isfinite(channel_pos) and -1.20 <= channel_pos <= 0.25)
    )
    conflict_score = (
        _flag(state.get("conflict_hint"))
        + _flag(state.get("near_resistance"))
        + _flag(state.get("down_structure"))
        + int(math.isfinite(channel_pos) and channel_pos > 1.15)
        + int(str(breakout.get("last_break_event") or "") == "BREAK_DOWN" and _safe_float(breakout.get("last_break_age_bars"), 999.0) <= 12.0)
    )
    return {
        "stas4_v2_structure_support_dist_pct": _safe_float(levels.get("support_dist_pct")),
        "stas4_v2_structure_support_touches": int(_safe_float(levels.get("support_touches"), 0.0)),
        "stas4_v2_structure_resistance_dist_pct": _safe_float(levels.get("resistance_dist_pct")),
        "stas4_v2_structure_resistance_touches": int(_safe_float(levels.get("resistance_touches"), 0.0)),
        "stas4_v2_structure_level_count": int(_safe_float(levels.get("level_count"), 0.0)),
        "stas4_v2_structure_range_pos_240": range_pos,
        "stas4_v2_structure_lower_range_flag": int(range_pos <= 0.35),
        "stas4_v2_structure_high_range_flag": int(range_pos >= 0.80),
        "stas4_v2_structure_near_support": _flag(state.get("support_hint")),
        "stas4_v2_structure_near_resistance": _flag(state.get("near_resistance")),
        "stas4_v2_structure_near_fib_support": _flag(state.get("fib_hint")),
        "stas4_v2_structure_fib_0382_dist_pct": fib_0382_dist,
        "stas4_v2_structure_fib_0618_dist_pct": fib_0618_dist,
        "stas4_v2_structure_retest_hint": _flag(state.get("retest_hint")),
        "stas4_v2_structure_channel_pos_sigma": channel_pos,
        "stas4_v2_structure_channel_slope_per_bar": _safe_float(channel.get("slope_per_bar")),
        "stas4_v2_structure_bos_up_recent": int(bool(internal.get("bos_up_now") or external.get("bos_up_now"))),
        "stas4_v2_structure_bos_down_recent": int(bool(internal.get("bos_down_now") or external.get("bos_down_now"))),
        "stas4_v2_structure_choch_recent": int(bool(internal.get("choch_like_near_signal") or external.get("choch_like_near_signal"))),
        "stas4_v2_structure_internal_event_code": _event_code(internal.get("last_event")),
        "stas4_v2_structure_internal_event_age_bars": -1
        if internal.get("last_event_age_bars") is None
        else int(internal.get("last_event_age_bars")),
        "stas4_v2_structure_external_event_code": _event_code(external.get("last_event")),
        "stas4_v2_structure_external_event_age_bars": -1
        if external.get("last_event_age_bars") is None
        else int(external.get("last_event_age_bars")),
        "stas4_v2_structure_last_break_event_code": _event_code(breakout.get("last_break_event")),
        "stas4_v2_structure_last_break_age_bars": -1
        if breakout.get("last_break_age_bars") is None
        else int(breakout.get("last_break_age_bars")),
        "stas4_v2_structure_retest_side_code": _event_code(breakout.get("retest_side")),
        "stas4_v2_structure_support_score": support_score,
        "stas4_v2_structure_conflict_score": conflict_score,
    }


def _volume_features(enriched: pd.DataFrame, idx: int) -> dict[str, Any]:
    row = enriched.iloc[idx]
    return {
        "stas4_v2_volume_chg_pct": _safe_float(row.get("F019_vol_chg")),
        "stas4_v2_volume_z20": _safe_float(row.get("F020_vol_z20")),
        "stas4_v2_volume_delta_proxy": _safe_float(row.get("F021_delta_volume")),
        "stas4_v2_volume_obv_slope5": _safe_float(row.get("F022_obv_slope5")),
        "stas4_v2_volume_mfi14": _safe_float(row.get("F023_mfi14")),
        "stas4_v2_volume_vwap_distance_pct": _safe_float(row.get("F024_vwap_distance")),
    }


def _support_conflict_block_features(combined: dict[str, Any]) -> dict[str, Any]:
    density_support = _safe_float(combined.get("stas4_v2_density_support_score"), 0.0)
    density_conflict = _safe_float(combined.get("stas4_v2_density_conflict_score"), 0.0)
    structure_support = _safe_float(combined.get("stas4_v2_structure_support_score"), 0.0)
    structure_conflict = _safe_float(combined.get("stas4_v2_structure_conflict_score"), 0.0)

    pattern_support = (
        int(_safe_float(combined.get("stas4_v2_pattern_bull_candle_recent3"), 0.0) > 0)
        + int(_safe_float(combined.get("stas4_v2_pattern_bull_divergence_recent8"), 0.0) > 0)
        + int(_safe_float(combined.get("stas4_v2_pattern_chart_long_recent8"), 0.0) > 0)
        + int(_safe_float(combined.get("stas4_v2_pattern_confirm_recent3"), 0.0) > 0)
        + int(_safe_float(combined.get("stas4_v2_pattern_long_composite"), 0.0) > 0)
    )
    pattern_conflict = (
        int(_safe_float(combined.get("stas4_v2_pattern_bear_candle_recent3"), 0.0) > 0)
        + int(_safe_float(combined.get("stas4_v2_pattern_strength"), 0.0) <= 1.0)
        + int(_safe_float(combined.get("stas4_v2_pattern_age_bars"), 99.0) > 12.0)
        + int(_safe_float(combined.get("stas4_v2_pattern_confirm_recent3"), 0.0) == 0)
    )

    volume_z = _safe_float(combined.get("stas4_v2_volume_z20"), 0.0)
    delta = _safe_float(combined.get("stas4_v2_volume_delta_proxy"), 0.0)
    obv = _safe_float(combined.get("stas4_v2_volume_obv_slope5"), 0.0)
    mfi = _safe_float(combined.get("stas4_v2_volume_mfi14"), 50.0)
    vwap_dist = _safe_float(combined.get("stas4_v2_volume_vwap_distance_pct"), 0.0)
    volume_support = int(volume_z >= 1.0) + int(delta > 0.0) + int(obv > 0.0) + int(35.0 <= mfi <= 65.0) + int(abs(vwap_dist) <= 0.45)
    volume_conflict = int(volume_z < -0.55) + int(delta < 0.0) + int(obv < 0.0) + int(mfi < 35.0) + int(vwap_dist < -0.35)

    ema_gap = _safe_float(combined.get("stas4_v2_combo_ema20_ema50_gap_pct"), 0.0)
    ema_slope = _safe_float(combined.get("stas4_v2_combo_ema20_slope5_pct"), 0.0)
    ema200_gap = _safe_float(combined.get("stas4_v2_combo_ema200_gap_pct"), 0.0)
    rsi = _safe_float(combined.get("stas4_v2_combo_rsi14"), 50.0)
    macd_hist = _safe_float(combined.get("stas4_v2_combo_macd_hist"), 0.0)
    macd_delta = _safe_float(combined.get("stas4_v2_combo_macd_hist_delta"), 0.0)
    stoch_k = _safe_float(combined.get("stas4_v2_combo_stoch_k14"), 50.0)
    stoch_d = _safe_float(combined.get("stas4_v2_combo_stoch_d14"), 50.0)
    adx = _safe_float(combined.get("stas4_v2_indicator_adx14"), 0.0)
    trend_support = (
        int(ema_gap > 0.0)
        + int(ema_slope > 0.0)
        + int(ema200_gap > 0.0)
        + int(42.0 <= rsi <= 62.0)
        + int(macd_delta > 0.0)
        + int(stoch_k > stoch_d and stoch_k < 72.0)
        + int(adx >= 16.0)
    )
    trend_conflict = (
        int(ema_gap < 0.0 and ema200_gap < 0.0)
        + int(ema_slope < 0.0)
        + int(rsi < 38.0)
        + int(macd_hist < 0.0 and macd_delta < 0.0)
        + int(stoch_k < stoch_d and stoch_k < 35.0)
        + int(adx < 14.0)
    )

    blocks = {
        "density_structure": (density_support + structure_support, density_conflict + structure_conflict),
        "pattern_structure": (pattern_support + structure_support, pattern_conflict + structure_conflict),
        "structure_volume": (structure_support + volume_support, structure_conflict + volume_conflict),
        "structure_trend": (structure_support + trend_support, structure_conflict + trend_conflict),
    }
    out: dict[str, Any] = {
        "stas4_v2_block_pattern_support_score": pattern_support,
        "stas4_v2_block_pattern_conflict_score": pattern_conflict,
        "stas4_v2_block_volume_support_score": volume_support,
        "stas4_v2_block_volume_conflict_score": volume_conflict,
        "stas4_v2_block_trend_support_score": trend_support,
        "stas4_v2_block_trend_conflict_score": trend_conflict,
    }
    for name, (support, conflict) in blocks.items():
        out[f"stas4_v2_block_{name}_support_score"] = round(float(support), 6)
        out[f"stas4_v2_block_{name}_conflict_score"] = round(float(conflict), 6)
        out[f"stas4_v2_block_{name}_net_score"] = round(float(support - conflict), 6)
    return out


def _risk_and_gate_features(candidate: pd.Series, combined: dict[str, Any]) -> tuple[dict[str, Any], str]:
    pre15 = _safe_float(candidate.get("pre_15m_close_move_pct"), 0.0)
    pre30 = _safe_float(candidate.get("pre_30m_close_move_pct"), 0.0)
    pre60 = _safe_float(candidate.get("pre_60m_close_move_pct"), 0.0)
    negative_count = sum(value < 0.0 for value in [pre15, pre30, pre60])
    short_pressure = _safe_float(combined.get("stas4_v2_combo_short_pressure_score"), 0.0)
    long_recovery = _safe_float(combined.get("stas4_v2_combo_long_recovery_score"), 0.0)
    bullish_evidence = (
        _safe_float(combined.get("stas4_v2_structure_support_score"), 0.0)
        + _safe_float(combined.get("stas4_v2_density_support_score"), 0.0)
        + combined.get("stas4_v2_div_bullish_recent", 0)
        + combined.get("stas4_v2_div_hidden_bullish_recent", 0)
    )
    conflict = _safe_float(combined.get("stas4_v2_structure_conflict_score"), 0.0) + _safe_float(combined.get("stas4_v2_density_conflict_score"), 0.0)
    risk_flags = str(candidate.get("stas1_risk_flags") or "")
    weak_bounce = int(pre60 < -0.45 and 0.0 < pre15 < abs(pre60) * 0.35)
    range_pos = _safe_float(combined.get("stas4_v2_structure_range_pos_240"), 0.5)
    too_high = int(pre60 < -0.35 and range_pos >= 0.65)
    after_spike = int("CAUTION_AFTER_SPIKE" in risk_flags)
    no_clear_low = int("CAUTION_NO_CLEAR_LOW" in risk_flags)
    low_volume = int(_safe_float(combined.get("stas4_v2_volume_z20"), 0.0) < -0.60 and bullish_evidence < 2.0)
    asia_weekend = int(
        str(candidate.get("effective_session_label") or "").upper().find("ASIA") >= 0
        or str(candidate.get("session_time_bucket_label") or "").upper().find("ASIA") >= 0
        or _flag(candidate.get("is_weekend"))
    )
    knife_risk = _clip(
        0.26 * (negative_count / 3.0)
        + 0.24 * short_pressure
        + 0.16 * min(conflict / 4.0, 1.0)
        + 0.12 * weak_bounce
        + 0.10 * too_high
        + 0.06 * after_spike
        + 0.06 * no_clear_low,
        0.0,
        1.0,
    )
    trend_pressure = -1 if short_pressure >= 0.60 and negative_count >= 2 else (1 if long_recovery >= 0.50 and bullish_evidence >= 2.0 else 0)
    long_allowed_raw = int(not (short_pressure >= 0.75 and bullish_evidence < 2.0) and not (negative_count == 3 and bullish_evidence < 2.0))
    hard_risk = int(knife_risk >= 0.70 and bullish_evidence < 3.0)
    long_allowed_final = int(long_allowed_raw and not hard_risk and not (too_high and conflict >= 2.0))
    if not long_allowed_raw:
        reason = "SHORT_PRESSURE_WITHOUT_REVERSAL"
    elif hard_risk:
        reason = "FALLING_KNIFE_RISK"
    elif too_high and conflict >= 2.0:
        reason = "TOO_HIGH_IN_DROP"
    else:
        reason = "OK"
    drawdown_proxy = _clip(0.55 * knife_risk + 0.25 * short_pressure + 0.20 * min(conflict / 4.0, 1.0), 0.0, 1.0)
    phase_strength = _safe_float(candidate.get("pre_60m_phase_metric_pct"), 0.0)
    return (
        {
            "stas5_v2_risk_negative_window_count_15_30_60": int(negative_count),
            "stas5_v2_risk_knife_pre_entry": round(float(knife_risk), 6),
            "stas5_v2_risk_weak_bounce_inside_drop": weak_bounce,
            "stas5_v2_risk_too_high_in_drop": too_high,
            "stas5_v2_risk_after_spike": after_spike,
            "stas5_v2_risk_no_clear_low": no_clear_low,
            "stas5_v2_risk_low_volume_confirmation": low_volume,
            "stas5_v2_risk_asia_weekend": asia_weekend,
            "stas5_v2_risk_drawdown_proxy_score": round(float(drawdown_proxy), 6),
            "stas5_v2_gate_phase_strength": phase_strength,
            "stas5_v2_gate_trend_pressure_direction": trend_pressure,
            "stas5_v2_gate_bullish_evidence_score": round(float(bullish_evidence), 6),
            "stas5_v2_gate_long_allowed_raw": long_allowed_raw,
            "stas5_v2_gate_long_allowed_final": long_allowed_final,
            "stas5_v2_gate_no_trade_reason_code": {"OK": 0, "SHORT_PRESSURE_WITHOUT_REVERSAL": 1, "FALLING_KNIFE_RISK": 2, "TOO_HIGH_IN_DROP": 3}.get(reason, 99),
        },
        reason,
    )


def _extract_candidate_features(candidate: pd.Series, context: DayContext) -> dict[str, Any]:
    signal_idx = _idx_at_or_before(context.enriched, candidate.get("anchor_time_utc"))
    entry_ts = pd.Timestamp(candidate.get("entry_time_utc")).tz_convert("UTC")
    base = {
        "day": str(candidate.get("day") or context.day),
        "candidate_id": str(candidate.get("candidate_id") or ""),
        "record_id": str(candidate.get("record_id") or ""),
        "anchor_time_utc": _fmt_ts(candidate.get("anchor_time_utc")),
        "entry_time_utc": _fmt_ts(entry_ts),
        "feature_time_utc": "",
        "feature_available_before_entry": False,
        "entry_price_5bps": _safe_float(candidate.get("entry_price_5bps")),
        "source_stas2_run": str(candidate.get("source_stas2_run") or ""),
        "source_ohlcv": context.ohlcv_source,
        "audit_no_trade_reason": "MISSING_SIGNAL_BAR",
    }
    if signal_idx is None:
        return base
    feature_time = pd.Timestamp(context.enriched.iloc[signal_idx]["open_time_utc"]).tz_convert("UTC")
    combined: dict[str, Any] = {}
    combined.update(_indicator_features(context.enriched, signal_idx))
    combined.update(_density_features(context.enriched, signal_idx))
    combined.update(_structure_features(context, signal_idx))
    combined.update(_volume_features(context.enriched, signal_idx))
    combined.update(_pattern_features(context.enriched, signal_idx))
    combined.update(_recent_divergence_features(context.divergences, signal_idx))
    combined.update(_short_wave_features(context.enriched, signal_idx))
    combined.update(_support_conflict_block_features(combined))
    risk_gate, reason = _risk_and_gate_features(candidate, combined)
    combined.update(risk_gate)
    base.update(
        {
            "feature_time_utc": _fmt_ts(feature_time),
            "feature_available_before_entry": bool(feature_time < entry_ts),
            "audit_no_trade_reason": reason,
        }
    )
    base.update(combined)
    return base


def select_v2_feature_columns(columns: list[str]) -> list[str]:
    return [column for column in columns if column.startswith("stas4_v2_") or column.startswith("stas5_v2_")]


def classify_feature_columns(df: pd.DataFrame, feature_columns: list[str]) -> tuple[list[str], list[str], list[str]]:
    numeric: list[str] = []
    categorical: list[str] = []
    boolean: list[str] = []
    for column in feature_columns:
        if column not in df:
            continue
        series = df[column]
        if pd.api.types.is_bool_dtype(series):
            boolean.append(column)
            categorical.append(column)
        elif pd.api.types.is_numeric_dtype(series):
            unique_values = set(series.dropna().unique().tolist())
            if unique_values.issubset({0, 1, 0.0, 1.0}):
                boolean.append(column)
            numeric.append(column)
        else:
            categorical.append(column)
    return numeric, categorical, boolean


def build_combo_features_from_frames(
    *,
    stas2: pd.DataFrame,
    ohlcv_by_day: dict[str, pd.DataFrame],
    start_day: str,
    end_day: str,
    source_stas2_run: str = "in_memory",
    ohlcv_sources: dict[str, str] | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    candidates = _prepare_candidates(stas2, start_day=start_day, end_day=end_day, source_stas2_run=source_stas2_run)
    contexts: dict[str, DayContext] = {}
    missing_ohlcv_days: list[str] = []
    rows: list[dict[str, Any]] = []
    ohlcv_sources = ohlcv_sources or {}
    for day in iter_days(start_day, end_day):
        if day not in set(candidates["day"]):
            continue
        day_df = ohlcv_by_day.get(day)
        if day_df is None:
            missing_ohlcv_days.append(day)
            for _, candidate in candidates[candidates["day"] == day].iterrows():
                rows.append(
                    {
                        "day": day,
                        "candidate_id": str(candidate.get("candidate_id") or ""),
                        "record_id": str(candidate.get("record_id") or ""),
                        "anchor_time_utc": _fmt_ts(candidate.get("anchor_time_utc")),
                        "entry_time_utc": _fmt_ts(candidate.get("entry_time_utc")),
                        "feature_time_utc": "",
                        "feature_available_before_entry": False,
                        "entry_price_5bps": _safe_float(candidate.get("entry_price_5bps")),
                        "source_stas2_run": source_stas2_run,
                        "source_ohlcv": ohlcv_sources.get(day, ""),
                        "audit_no_trade_reason": "MISSING_OHLCV",
                    }
                )
            continue
        contexts[day] = _build_day_context(day, day_df, ohlcv_source=ohlcv_sources.get(day, "in_memory"))
        day_candidates = candidates[candidates["day"] == day]
        for _, candidate in day_candidates.iterrows():
            rows.append(_extract_candidate_features(candidate, contexts[day]))

    out = pd.DataFrame(rows)
    if out.empty:
        feature_columns: list[str] = []
        out = pd.DataFrame(columns=METADATA_COLUMNS)
    else:
        feature_columns = select_v2_feature_columns(list(out.columns))
        ordered = [column for column in METADATA_COLUMNS if column in out.columns]
        ordered += [column for column in feature_columns if column not in ordered]
        out = out[ordered].sort_values([c for c in ["day", "entry_time_utc", "record_id"] if c in out.columns]).reset_index(drop=True)

    numeric, categorical, boolean = classify_feature_columns(out, feature_columns)
    forbidden = forbidden_feature_matches(feature_columns)
    not_before = int((out.get("feature_available_before_entry", pd.Series(dtype=bool)).astype(str).str.lower() != "true").sum()) if len(out) else 0
    manifest = {
        "status": "PASS" if len(out) == len(candidates) and not missing_ohlcv_days and not forbidden and not_before == 0 else "FAIL",
        "pipeline_status": STATUS,
        "created_utc": utc_now(),
        "schema_version": 0,
        "rows": int(len(out)),
        "input_rows": int(len(candidates)),
        "start_day": normalize_day(start_day),
        "end_day": normalize_day(end_day),
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "source_stas2_run": source_stas2_run,
        "feature_columns": feature_columns,
        "feature_count": len(feature_columns),
        "numeric_columns": numeric,
        "categorical_columns": categorical,
        "boolean_columns": boolean,
        "metadata_columns": [column for column in METADATA_COLUMNS if column in out.columns],
        "checks": {
            "row_count_matches_input": len(out) == len(candidates),
            "missing_ohlcv_days": missing_ohlcv_days,
            "feature_available_before_entry_false": not_before,
            "forbidden_feature_columns": forbidden,
            "candidate_days": sorted(set(candidates["day"].tolist())) if len(candidates) else [],
        },
        "guardrails": [
            "snapshot_time_is_anchor_time_not_entry_candle",
            "feature_time_utc_must_be_before_entry_time_utc",
            "yellow_x_strategy_votes_not_exported_as_v2_features",
            "post_entry_outcome_mfe_mae_tp_exit_stas3_not_exported",
            "combo_spectrum_recomputed_from_ohlcv_not_read_from_png",
            "divergence_features_use_confirm_idx_less_or_equal_signal_idx",
            "day_wide_renderer_quantiles_not_used_as_features",
        ],
    }
    return out, manifest


def build_combo_features(
    *,
    stas2_run_dir: Path = DEFAULT_STAS2_TRAIN_RUN_DIR,
    start_day: str = TRAIN_START_DAY,
    end_day: str = TRAIN_END_DAY,
    output_csv: Path = DEFAULT_V2_COMBO_FEATURE_PATH,
    manifest_path: Path = DEFAULT_V2_COMBO_MANIFEST_PATH,
    strict: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    stas2 = _load_stas2_records(stas2_run_dir)
    ohlcv_by_day: dict[str, pd.DataFrame] = {}
    ohlcv_sources: dict[str, str] = {}
    for day in iter_days(start_day, end_day):
        source_path = _source_csv(PROJECT_ROOT, day, TIMEFRAME, SYMBOL)
        ohlcv_sources[day] = rel(source_path)
        if source_path.exists():
            ohlcv_by_day[day] = _load_ohlcv(source_path)
    features, manifest = build_combo_features_from_frames(
        stas2=stas2,
        ohlcv_by_day=ohlcv_by_day,
        start_day=start_day,
        end_day=end_day,
        source_stas2_run=rel(stas2_run_dir),
        ohlcv_sources=ohlcv_sources,
    )
    manifest["output_csv"] = rel(output_csv)
    manifest["manifest_path"] = rel(manifest_path)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_csv, index=False, encoding="utf-8-sig")
    write_json(manifest_path, manifest)
    if strict and manifest["status"] != "PASS":
        raise ValueError(f"STAS5 V2 combo feature export failed checks: {manifest['checks']}")
    return features, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Export causal STAS5 V2 combo/STAS4 features for entry ML.")
    parser.add_argument("--stas2-run-dir", default=str(DEFAULT_STAS2_TRAIN_RUN_DIR))
    parser.add_argument("--start-day", default=TRAIN_START_DAY)
    parser.add_argument("--end-day", default=TRAIN_END_DAY)
    parser.add_argument("--output-csv", default=str(DEFAULT_V2_COMBO_FEATURE_PATH))
    parser.add_argument("--manifest-path", default=str(DEFAULT_V2_COMBO_MANIFEST_PATH))
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args()
    _, manifest = build_combo_features(
        stas2_run_dir=Path(args.stas2_run_dir),
        start_day=args.start_day,
        end_day=args.end_day,
        output_csv=Path(args.output_csv),
        manifest_path=Path(args.manifest_path),
        strict=not args.no_strict,
    )
    print(manifest["status"], manifest["rows"], manifest["feature_count"], rel(Path(args.output_csv)))
    return 0 if manifest["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
