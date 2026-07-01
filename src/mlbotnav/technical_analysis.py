from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from mlbotnav.audit import audit_event
from mlbotnav.dataset import load_ohlcv_range
from mlbotnav.pct_units import normalize_min_expected_move_pct
from mlbotnav.runtime_contract import CALIBRATION_MODE_NONE, SIGNAL_CONTRACT_VERSION
from mlbotnav.storage_registry import ensure_storage_layout, register_partition

CANDLE_PATTERN_TYPES: tuple[str, ...] = (
    "doji",
    "inside_bar",
    "engulf_bull",
    "engulf_bear",
    "hammer",
    "shooting_star",
    "pin_bar_bull",
    "pin_bar_bear",
)

FIGURE_PATTERN_TYPES: tuple[str, ...] = (
    "double_bottom",
    "double_top",
    "head_and_shoulders",
    "inverse_head_and_shoulders",
    "macd_bull_divergence",
    "macd_bear_divergence",
    "obv_bull_divergence",
    "obv_bear_divergence",
    "pennant",
    "range",
    "rsi_bear_divergence",
    "rsi_bull_divergence",
    "triangle",
    "wedge_falling",
    "wedge_rising",
)

ALL_PATTERN_TYPES: tuple[str, ...] = CANDLE_PATTERN_TYPES + FIGURE_PATTERN_TYPES


def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _load_ta_profile(project_root: Path, timeframe: str) -> dict:
    p = project_root / "configs" / "ta_policy.yaml"
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    root = cfg.get("ta", {})
    profiles = root.get("profiles", {})
    merged = _deep_merge(profiles.get("default", {}), profiles.get(str(timeframe), {}))
    return merged


def _uid(prefix: str, *parts: object) -> str:
    raw = "|".join(str(p) for p in parts)
    return f"{prefix}_{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:16]}"


def _utc_iso_z(value: object) -> str:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_table(path: Path, frame: pd.DataFrame, id_col: str, dedupe_cols: list[str] | None = None) -> int:
    if frame.empty:
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            frame.to_csv(path, index=False)
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        old = pd.read_csv(path)
        merged = pd.concat([old, frame], ignore_index=True)
        # Canonicalize UTC timestamp text to avoid duplicate keys caused by
        # mixed representations (+00:00 vs Z) across runs.
        for c in merged.columns:
            if c.endswith("_utc"):
                ts = pd.to_datetime(merged[c], utc=True, errors="coerce")
                mask = ts.notna()
                if int(mask.sum()) > 0:
                    merged.loc[mask, c] = ts[mask].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        if "contract_version" in merged.columns:
            merged["contract_version"] = merged["contract_version"].replace({"": np.nan}).fillna(SIGNAL_CONTRACT_VERSION)
        if "calibration_mode" in merged.columns:
            merged["calibration_mode"] = merged["calibration_mode"].replace({"": np.nan}).fillna(CALIBRATION_MODE_NONE)
        if dedupe_cols:
            merged = merged.drop_duplicates(subset=dedupe_cols, keep="last")
        elif id_col in merged.columns:
            merged = merged.drop_duplicates(subset=[id_col], keep="last")
    else:
        merged = frame.copy()
    merged.to_csv(path, index=False)
    return len(frame)


def _swing_flags(df: pd.DataFrame, order: int = 3) -> tuple[pd.Series, pd.Series]:
    hi = pd.Series(True, index=df.index)
    lo = pd.Series(True, index=df.index)
    for k in range(1, order + 1):
        hi = hi & (df["high"] > df["high"].shift(k)) & (df["high"] >= df["high"].shift(-k))
        lo = lo & (df["low"] < df["low"].shift(k)) & (df["low"] <= df["low"].shift(-k))
    return hi.fillna(False), lo.fillna(False)


def _build_levels(df: pd.DataFrame, *, symbol: str, timeframe: str, run_id: str) -> pd.DataFrame:
    work = df.copy()
    swing_high, swing_low = _swing_flags(work, order=3)
    candidates = []
    tol_ratio = 0.0015
    for idx in work.index[swing_high]:
        price = float(work.at[idx, "high"])
        ts = work.at[idx, "open_time_utc"]
        touches = int(((work["high"] - price).abs() / max(price, 1e-9) <= tol_ratio).sum())
        strength = float(min(1.0, touches / 8.0))
        candidates.append(
            {
                "level_id": _uid("lvl", symbol, timeframe, ts, price, "R"),
                "symbol": symbol,
                "timeframe": timeframe,
                "detected_at_utc": ts.isoformat(),
                "level_price": price,
                "level_type": "resistance",
                "strength_score": strength,
                "touches_count": touches,
                "valid_from_utc": ts.isoformat(),
                "valid_to_utc": (ts + timedelta(days=7)).isoformat(),
                "run_id": run_id,
            }
        )
    for idx in work.index[swing_low]:
        price = float(work.at[idx, "low"])
        ts = work.at[idx, "open_time_utc"]
        touches = int(((work["low"] - price).abs() / max(price, 1e-9) <= tol_ratio).sum())
        strength = float(min(1.0, touches / 8.0))
        candidates.append(
            {
                "level_id": _uid("lvl", symbol, timeframe, ts, price, "S"),
                "symbol": symbol,
                "timeframe": timeframe,
                "detected_at_utc": ts.isoformat(),
                "level_price": price,
                "level_type": "support",
                "strength_score": strength,
                "touches_count": touches,
                "valid_from_utc": ts.isoformat(),
                "valid_to_utc": (ts + timedelta(days=7)).isoformat(),
                "run_id": run_id,
            }
        )
    out = pd.DataFrame(candidates)
    if out.empty:
        return out
    return out.sort_values("detected_at_utc").reset_index(drop=True)


def _build_patterns(df: pd.DataFrame, *, symbol: str, timeframe: str, run_id: str, ta_cfg: dict) -> pd.DataFrame:
    work = df.copy()
    body = (work["close"] - work["open"]).abs()
    rng = (work["high"] - work["low"]).replace(0, np.nan)
    upper_wick = work["high"] - work[["open", "close"]].max(axis=1)
    lower_wick = work[["open", "close"]].min(axis=1) - work["low"]

    prev_open = work["open"].shift(1)
    prev_close = work["close"].shift(1)
    prev_body_low = np.minimum(prev_open, prev_close)
    prev_body_high = np.maximum(prev_open, prev_close)
    cur_body_low = np.minimum(work["open"], work["close"])
    cur_body_high = np.maximum(work["open"], work["close"])

    flags = {
        "doji": ((body / rng) <= 0.1),
        "inside_bar": ((work["high"] <= work["high"].shift(1)) & (work["low"] >= work["low"].shift(1))),
        "engulf_bull": ((prev_close < prev_open) & (work["close"] > work["open"]) & (cur_body_low <= prev_body_low) & (cur_body_high >= prev_body_high)),
        "engulf_bear": ((prev_close > prev_open) & (work["close"] < work["open"]) & (cur_body_low <= prev_body_low) & (cur_body_high >= prev_body_high)),
        "hammer": ((lower_wick > body * 2.2) & (upper_wick < body * 0.8)),
        "shooting_star": ((upper_wick > body * 2.2) & (lower_wick < body * 0.8)),
        "pin_bar_bull": ((lower_wick > body * 2.0) & (upper_wick < body)),
        "pin_bar_bear": ((upper_wick > body * 2.0) & (lower_wick < body)),
    }

    rows = []
    for name, mask in flags.items():
        idxs = work.index[mask.fillna(False)]
        for idx in idxs:
            ts = work.at[idx, "open_time_utc"]
            px = float(work.at[idx, "close"])
            if name in {"engulf_bull", "hammer", "pin_bar_bull"}:
                direction = "long"
            elif name in {"engulf_bear", "shooting_star", "pin_bar_bear"}:
                direction = "short"
            else:
                direction = "neutral"
            confidence = float(min(1.0, max(0.05, (rng.iloc[idx] or 0.0) / max(px, 1e-9) * 50.0)))
            target = px * (1.01 if direction == "long" else 0.99 if direction == "short" else 1.0)
            stop = float(work.at[idx, "low"] * 0.999 if direction == "long" else work.at[idx, "high"] * 1.001)
            rows.append(
                {
                    "pattern_id": _uid("ptn", symbol, timeframe, name, ts),
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "pattern_type": name,
                    "direction": direction,
                    "start_time_utc": ts.isoformat(),
                    "end_time_utc": ts.isoformat(),
                    "confidence_score": confidence,
                    "target_price": target,
                    "stop_price": stop,
                    "invalidation_price": stop,
                    "run_id": run_id,
                }
            )
    out = pd.DataFrame(rows)
    # Figure-pattern and divergence extensions (deterministic numeric rules).
    ext = _build_figure_and_divergence_patterns(work, symbol=symbol, timeframe=timeframe, run_id=run_id, ta_cfg=ta_cfg)
    if not ext.empty:
        out = pd.concat([out, ext], ignore_index=True)
    if out.empty:
        return out
    out = out.drop_duplicates(subset=["pattern_id"]).sort_values("start_time_utc").reset_index(drop=True)
    out = _apply_pattern_density_controls(out, ta_cfg=ta_cfg)
    return out


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean().replace(0, np.nan)
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def _compute_indicators(work: pd.DataFrame) -> pd.DataFrame:
    out = work.copy()
    high = out["high"]
    low = out["low"]
    close = out["close"]
    volume = out["volume"]

    # ATR / ADX
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr = tr.rolling(14).mean()
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    plus_di = 100 * pd.Series(plus_dm, index=out.index).rolling(14).mean() / atr.replace(0, np.nan)
    minus_di = 100 * pd.Series(minus_dm, index=out.index).rolling(14).mean() / atr.replace(0, np.nan)
    dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)).replace([np.inf, -np.inf], np.nan)
    adx = dx.rolling(14).mean()

    # MFI
    tp = (high + low + close) / 3.0
    mf = tp * volume
    tp_diff = tp.diff()
    pos_mf = pd.Series(np.where(tp_diff > 0, mf, 0.0), index=out.index)
    neg_mf = pd.Series(np.where(tp_diff < 0, mf, 0.0), index=out.index)
    pos_mf14 = pos_mf.rolling(14).sum()
    neg_mf14 = neg_mf.rolling(14).sum().replace(0, np.nan)
    mfr = pos_mf14 / neg_mf14
    mfi = 100 - (100 / (1 + mfr))

    # Stochastic
    ll14 = low.rolling(14).min()
    hh14 = high.rolling(14).max()
    stoch_k = 100 * (close - ll14) / (hh14 - ll14).replace(0, np.nan)
    stoch_d = stoch_k.rolling(3).mean()

    out["rsi14"] = _rsi(close, period=14)
    out["adx14"] = adx
    out["plus_di14"] = plus_di
    out["minus_di14"] = minus_di
    out["mfi14"] = mfi
    out["stoch_k14"] = stoch_k
    out["stoch_d14"] = stoch_d
    return out


def _apply_pattern_density_controls(patterns: pd.DataFrame, *, ta_cfg: dict) -> pd.DataFrame:
    dc = (ta_cfg.get("density_controls", {}) if isinstance(ta_cfg, dict) else {})
    if not dc.get("enabled", True) or patterns.empty:
        return patterns
    per_type = dc.get("per_pattern_type", {}) or {}
    default_cap = int(dc.get("default_max_events_per_day", 800))

    work = patterns.copy()
    work["start_time_utc"] = pd.to_datetime(work["start_time_utc"], utc=True)
    work["_day"] = work["start_time_utc"].dt.strftime("%Y-%m-%d")
    keep_idx = []
    for (ptype, day), grp in work.groupby(["pattern_type", "_day"], sort=False):
        cap = int(per_type.get(ptype, default_cap))
        if len(grp) <= cap:
            keep_idx.extend(grp.index.tolist())
            continue
        top = grp.sort_values("confidence_score", ascending=False).head(cap)
        keep_idx.extend(top.index.tolist())
    out = work.loc[sorted(set(keep_idx))].drop(columns=["_day"]).sort_values("start_time_utc").reset_index(drop=True)
    out["start_time_utc"] = out["start_time_utc"].dt.strftime("%Y-%m-%dT%H:%M:%S%z")
    # Normalize UTC suffix for consistency.
    out["start_time_utc"] = out["start_time_utc"].str.replace(r"(\+0000)$", "+00:00", regex=True)
    return out


def _build_figure_and_divergence_patterns(work: pd.DataFrame, *, symbol: str, timeframe: str, run_id: str, ta_cfg: dict) -> pd.DataFrame:
    rows = []
    swing_high, swing_low = _swing_flags(work, order=3)
    highs = work.loc[swing_high, ["open_time_utc", "high", "low", "close"]].copy()
    lows = work.loc[swing_low, ["open_time_utc", "high", "low", "close"]].copy()

    pd_cfg = ta_cfg.get("pattern_detection", {}) if isinstance(ta_cfg, dict) else {}
    tol = float(pd_cfg.get("double_tolerance", 0.003))
    min_sep = int(pd_cfg.get("min_sep_bars", 5))
    max_sep = int(pd_cfg.get("max_sep_bars", 120))
    hs_should_tol = float(pd_cfg.get("hs_shoulder_tolerance", 0.008))
    hs_head_min = float(pd_cfg.get("hs_head_excess_min", 0.003))
    tri_width_max = float(pd_cfg.get("triangle_width_max", 0.04))
    wedge_width_max = float(pd_cfg.get("wedge_width_max", 0.035))
    range_width_max = float(pd_cfg.get("range_width_max", 0.02))
    div_lookback = int(pd_cfg.get("divergence_lookback_bars", 10))

    # double top / bottom
    for i in range(len(highs) - 1):
        p1 = float(highs.iloc[i]["high"])
        t1 = highs.iloc[i]["open_time_utc"]
        for j in range(i + 1, len(highs)):
            t2 = highs.iloc[j]["open_time_utc"]
            sep = int((t2 - t1).total_seconds() / 60.0)
            if sep < min_sep:
                continue
            if sep > max_sep:
                break
            p2 = float(highs.iloc[j]["high"])
            if abs(p1 - p2) / max(p1, 1e-9) <= tol:
                conf = float(max(0.1, min(1.0, 1.0 - abs(p1 - p2) / max(p1, 1e-9) / tol)))
                mid = work[(work["open_time_utc"] >= t1) & (work["open_time_utc"] <= t2)]
                neckline = float(mid["low"].min()) if len(mid) else float(highs.iloc[j]["low"])
                rows.append(
                    {
                        "pattern_id": _uid("ptn", symbol, timeframe, "double_top", t1, t2),
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "pattern_type": "double_top",
                        "direction": "short",
                        "start_time_utc": t1.isoformat(),
                        "end_time_utc": t2.isoformat(),
                        "confidence_score": conf,
                        "target_price": neckline,
                        "stop_price": max(p1, p2) * 1.001,
                        "invalidation_price": max(p1, p2) * 1.001,
                        "run_id": run_id,
                    }
                )
                break
    for i in range(len(lows) - 1):
        p1 = float(lows.iloc[i]["low"])
        t1 = lows.iloc[i]["open_time_utc"]
        for j in range(i + 1, len(lows)):
            t2 = lows.iloc[j]["open_time_utc"]
            sep = int((t2 - t1).total_seconds() / 60.0)
            if sep < min_sep:
                continue
            if sep > max_sep:
                break
            p2 = float(lows.iloc[j]["low"])
            if abs(p1 - p2) / max(abs(p1), 1e-9) <= tol:
                conf = float(max(0.1, min(1.0, 1.0 - abs(p1 - p2) / max(abs(p1), 1e-9) / tol)))
                mid = work[(work["open_time_utc"] >= t1) & (work["open_time_utc"] <= t2)]
                neckline = float(mid["high"].max()) if len(mid) else float(lows.iloc[j]["high"])
                rows.append(
                    {
                        "pattern_id": _uid("ptn", symbol, timeframe, "double_bottom", t1, t2),
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "pattern_type": "double_bottom",
                        "direction": "long",
                        "start_time_utc": t1.isoformat(),
                        "end_time_utc": t2.isoformat(),
                        "confidence_score": conf,
                        "target_price": neckline,
                        "stop_price": min(p1, p2) * 0.999,
                        "invalidation_price": min(p1, p2) * 0.999,
                        "run_id": run_id,
                    }
                )
                break

    # Head-and-shoulders / inverse H&S from 3 swings.
    for i in range(1, len(highs) - 1):
        left = highs.iloc[i - 1]
        head = highs.iloc[i]
        right = highs.iloc[i + 1]
        t_l = left["open_time_utc"]
        t_h = head["open_time_utc"]
        t_r = right["open_time_utc"]
        sep_lr = int((t_r - t_l).total_seconds() / 60.0)
        if sep_lr < 10 or sep_lr > 240:
            continue
        p_l = float(left["high"])
        p_h = float(head["high"])
        p_r = float(right["high"])
        shoulders_close = abs(p_l - p_r) / max(p_h, 1e-9) <= hs_should_tol
        head_above = p_h > p_l and p_h > p_r and ((p_h - max(p_l, p_r)) / max(p_h, 1e-9) >= hs_head_min)
        if shoulders_close and head_above:
            mid = work[(work["open_time_utc"] >= t_l) & (work["open_time_utc"] <= t_r)]
            neckline = float(mid["low"].min()) if len(mid) else float(right["low"])
            conf = float(max(0.1, min(1.0, 0.4 + (p_h - max(p_l, p_r)) / max(p_h, 1e-9) * 20.0)))
            rows.append(
                {
                    "pattern_id": _uid("ptn", symbol, timeframe, "head_shoulders", t_l, t_h, t_r),
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "pattern_type": "head_and_shoulders",
                    "direction": "short",
                    "start_time_utc": t_l.isoformat(),
                    "end_time_utc": t_r.isoformat(),
                    "confidence_score": conf,
                    "target_price": neckline,
                    "stop_price": p_h * 1.001,
                    "invalidation_price": p_h * 1.001,
                    "run_id": run_id,
                }
            )

    for i in range(1, len(lows) - 1):
        left = lows.iloc[i - 1]
        head = lows.iloc[i]
        right = lows.iloc[i + 1]
        t_l = left["open_time_utc"]
        t_h = head["open_time_utc"]
        t_r = right["open_time_utc"]
        sep_lr = int((t_r - t_l).total_seconds() / 60.0)
        if sep_lr < 10 or sep_lr > 240:
            continue
        p_l = float(left["low"])
        p_h = float(head["low"])
        p_r = float(right["low"])
        shoulders_close = abs(p_l - p_r) / max(abs(p_h), 1e-9) <= hs_should_tol
        head_below = p_h < p_l and p_h < p_r and ((min(p_l, p_r) - p_h) / max(abs(p_h), 1e-9) >= hs_head_min)
        if shoulders_close and head_below:
            mid = work[(work["open_time_utc"] >= t_l) & (work["open_time_utc"] <= t_r)]
            neckline = float(mid["high"].max()) if len(mid) else float(right["high"])
            conf = float(max(0.1, min(1.0, 0.4 + (min(p_l, p_r) - p_h) / max(abs(p_h), 1e-9) * 20.0)))
            rows.append(
                {
                    "pattern_id": _uid("ptn", symbol, timeframe, "inv_head_shoulders", t_l, t_h, t_r),
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "pattern_type": "inverse_head_and_shoulders",
                    "direction": "long",
                    "start_time_utc": t_l.isoformat(),
                    "end_time_utc": t_r.isoformat(),
                    "confidence_score": conf,
                    "target_price": neckline,
                    "stop_price": p_h * 0.999,
                    "invalidation_price": p_h * 0.999,
                    "run_id": run_id,
                }
            )

    # triangle / wedge / range approximation from rolling slope compression.
    win = 30
    h_slope = work["high"].rolling(win).apply(lambda x: np.polyfit(np.arange(len(x)), x, 1)[0] if len(x) == win else np.nan, raw=False)
    l_slope = work["low"].rolling(win).apply(lambda x: np.polyfit(np.arange(len(x)), x, 1)[0] if len(x) == win else np.nan, raw=False)
    width = (work["high"].rolling(win).max() - work["low"].rolling(win).min()) / work["close"].replace(0, np.nan)
    for idx in range(win, len(work)):
        ts = work.at[idx, "open_time_utc"]
        hs = float(h_slope.iloc[idx]) if pd.notna(h_slope.iloc[idx]) else np.nan
        ls = float(l_slope.iloc[idx]) if pd.notna(l_slope.iloc[idx]) else np.nan
        wd = float(width.iloc[idx]) if pd.notna(width.iloc[idx]) else np.nan
        if np.isnan(hs) or np.isnan(ls) or np.isnan(wd):
            continue
        # converging lines with opposite signs -> triangle
        if hs < 0 and ls > 0 and wd < tri_width_max:
            pole = (work["close"].iloc[idx - win] - work["close"].iloc[max(idx - 2 * win, 0)]) / max(
                work["close"].iloc[max(idx - 2 * win, 0)], 1e-9
            )
            rows.append(
                {
                    "pattern_id": _uid("ptn", symbol, timeframe, "triangle", ts),
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "pattern_type": "triangle",
                    "direction": "neutral",
                    "start_time_utc": (ts - timedelta(minutes=win)).isoformat(),
                    "end_time_utc": ts.isoformat(),
                    "confidence_score": float(max(0.1, min(1.0, (tri_width_max - wd) / max(tri_width_max, 1e-9)))),
                    "target_price": float(work.at[idx, "close"]),
                    "stop_price": float(work.at[idx, "close"]),
                    "invalidation_price": float(work.at[idx, "close"]),
                    "run_id": run_id,
                }
            )
            if abs(pole) >= 0.01:
                rows.append(
                    {
                        "pattern_id": _uid("ptn", symbol, timeframe, "pennant", ts),
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "pattern_type": "pennant",
                        "direction": "long" if pole > 0 else "short",
                        "start_time_utc": (ts - timedelta(minutes=win)).isoformat(),
                        "end_time_utc": ts.isoformat(),
                        "confidence_score": float(max(0.1, min(1.0, abs(pole) * 10.0))),
                        "target_price": float(work.at[idx, "close"] * (1.01 if pole > 0 else 0.99)),
                        "stop_price": float(work.at[idx, "low"] * 0.999 if pole > 0 else work.at[idx, "high"] * 1.001),
                        "invalidation_price": float(work.at[idx, "low"] * 0.999 if pole > 0 else work.at[idx, "high"] * 1.001),
                        "run_id": run_id,
                    }
                )
        # same-sign narrowing slopes -> wedge
        if hs < 0 and ls < 0 and wd < wedge_width_max:
            rows.append(
                {
                    "pattern_id": _uid("ptn", symbol, timeframe, "falling_wedge", ts),
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "pattern_type": "wedge_falling",
                    "direction": "long",
                    "start_time_utc": (ts - timedelta(minutes=win)).isoformat(),
                    "end_time_utc": ts.isoformat(),
                    "confidence_score": float(max(0.1, min(1.0, (wedge_width_max - wd) / max(wedge_width_max, 1e-9)))),
                    "target_price": float(work.at[idx, "close"] * 1.01),
                    "stop_price": float(work.at[idx, "low"] * 0.999),
                    "invalidation_price": float(work.at[idx, "low"] * 0.999),
                    "run_id": run_id,
                }
            )
        if hs > 0 and ls > 0 and wd < wedge_width_max:
            rows.append(
                {
                    "pattern_id": _uid("ptn", symbol, timeframe, "rising_wedge", ts),
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "pattern_type": "wedge_rising",
                    "direction": "short",
                    "start_time_utc": (ts - timedelta(minutes=win)).isoformat(),
                    "end_time_utc": ts.isoformat(),
                    "confidence_score": float(max(0.1, min(1.0, (wedge_width_max - wd) / max(wedge_width_max, 1e-9)))),
                    "target_price": float(work.at[idx, "close"] * 0.99),
                    "stop_price": float(work.at[idx, "high"] * 1.001),
                    "invalidation_price": float(work.at[idx, "high"] * 1.001),
                    "run_id": run_id,
                }
            )
        if wd < range_width_max:
            rows.append(
                {
                    "pattern_id": _uid("ptn", symbol, timeframe, "range", ts),
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "pattern_type": "range",
                    "direction": "neutral",
                    "start_time_utc": (ts - timedelta(minutes=win)).isoformat(),
                    "end_time_utc": ts.isoformat(),
                    "confidence_score": float(max(0.1, min(1.0, (range_width_max - wd) / max(range_width_max, 1e-9)))),
                    "target_price": float(work.at[idx, "close"]),
                    "stop_price": float(work.at[idx, "close"]),
                    "invalidation_price": float(work.at[idx, "close"]),
                    "run_id": run_id,
                }
            )

    # RSI/MACD/OBV divergence flags
    close = work["close"]
    rsi = _rsi(close, period=14)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    obv = (np.sign(close.diff().fillna(0)) * work["volume"]).cumsum()
    for idx in range(max(20, div_lookback + 1), len(work)):
        ts = work.at[idx, "open_time_utc"]
        p_now = float(close.iloc[idx])
        p_prev = float(close.iloc[idx - div_lookback])
        rsi_now, rsi_prev = float(rsi.iloc[idx]), float(rsi.iloc[idx - div_lookback])
        macd_now, macd_prev = float(macd.iloc[idx]), float(macd.iloc[idx - div_lookback])
        obv_now, obv_prev = float(obv.iloc[idx]), float(obv.iloc[idx - div_lookback])
        if p_now < p_prev and rsi_now > rsi_prev:
            rows.append(
                {
                    "pattern_id": _uid("ptn", symbol, timeframe, "rsi_bull_div", ts),
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "pattern_type": "rsi_bull_divergence",
                    "direction": "long",
                    "start_time_utc": (ts - timedelta(minutes=div_lookback)).isoformat(),
                    "end_time_utc": ts.isoformat(),
                    "confidence_score": float(max(0.1, min(1.0, (rsi_now - rsi_prev) / 20.0))),
                    "target_price": p_now * 1.01,
                    "stop_price": float(work.at[idx, "low"] * 0.999),
                    "invalidation_price": float(work.at[idx, "low"] * 0.999),
                    "run_id": run_id,
                }
            )
        if p_now > p_prev and rsi_now < rsi_prev:
            rows.append(
                {
                    "pattern_id": _uid("ptn", symbol, timeframe, "rsi_bear_div", ts),
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "pattern_type": "rsi_bear_divergence",
                    "direction": "short",
                    "start_time_utc": (ts - timedelta(minutes=div_lookback)).isoformat(),
                    "end_time_utc": ts.isoformat(),
                    "confidence_score": float(max(0.1, min(1.0, (rsi_prev - rsi_now) / 20.0))),
                    "target_price": p_now * 0.99,
                    "stop_price": float(work.at[idx, "high"] * 1.001),
                    "invalidation_price": float(work.at[idx, "high"] * 1.001),
                    "run_id": run_id,
                }
            )
        if p_now < p_prev and macd_now > macd_prev:
            rows.append(
                {
                    "pattern_id": _uid("ptn", symbol, timeframe, "macd_bull_div", ts),
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "pattern_type": "macd_bull_divergence",
                    "direction": "long",
                    "start_time_utc": (ts - timedelta(minutes=div_lookback)).isoformat(),
                    "end_time_utc": ts.isoformat(),
                    "confidence_score": 0.5,
                    "target_price": p_now * 1.01,
                    "stop_price": float(work.at[idx, "low"] * 0.999),
                    "invalidation_price": float(work.at[idx, "low"] * 0.999),
                    "run_id": run_id,
                }
            )
        if p_now > p_prev and macd_now < macd_prev:
            rows.append(
                {
                    "pattern_id": _uid("ptn", symbol, timeframe, "macd_bear_div", ts),
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "pattern_type": "macd_bear_divergence",
                    "direction": "short",
                    "start_time_utc": (ts - timedelta(minutes=div_lookback)).isoformat(),
                    "end_time_utc": ts.isoformat(),
                    "confidence_score": 0.5,
                    "target_price": p_now * 0.99,
                    "stop_price": float(work.at[idx, "high"] * 1.001),
                    "invalidation_price": float(work.at[idx, "high"] * 1.001),
                    "run_id": run_id,
                }
            )
        if p_now < p_prev and obv_now > obv_prev:
            rows.append(
                {
                    "pattern_id": _uid("ptn", symbol, timeframe, "obv_bull_div", ts),
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "pattern_type": "obv_bull_divergence",
                    "direction": "long",
                    "start_time_utc": (ts - timedelta(minutes=div_lookback)).isoformat(),
                    "end_time_utc": ts.isoformat(),
                    "confidence_score": 0.45,
                    "target_price": p_now * 1.01,
                    "stop_price": float(work.at[idx, "low"] * 0.999),
                    "invalidation_price": float(work.at[idx, "low"] * 0.999),
                    "run_id": run_id,
                }
            )
        if p_now > p_prev and obv_now < obv_prev:
            rows.append(
                {
                    "pattern_id": _uid("ptn", symbol, timeframe, "obv_bear_div", ts),
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "pattern_type": "obv_bear_divergence",
                    "direction": "short",
                    "start_time_utc": (ts - timedelta(minutes=div_lookback)).isoformat(),
                    "end_time_utc": ts.isoformat(),
                    "confidence_score": 0.45,
                    "target_price": p_now * 0.99,
                    "stop_price": float(work.at[idx, "high"] * 1.001),
                    "invalidation_price": float(work.at[idx, "high"] * 1.001),
                    "run_id": run_id,
                }
            )

    out = pd.DataFrame(rows)
    if out.empty:
        return out
    return out


def _build_signals(
    df: pd.DataFrame,
    *,
    symbol: str,
    timeframe: str,
    run_id: str,
    levels_df: pd.DataFrame,
    patterns_df: pd.DataFrame,
    ta_cfg: dict,
    min_tp_pct: float,
    min_expected_move_pct: float,
) -> pd.DataFrame:
    work = _compute_indicators(df.copy())
    min_expected_move_pct = normalize_min_expected_move_pct(min_expected_move_pct)
    roll_high = work["high"].rolling(50).max().shift(1)
    roll_low = work["low"].rolling(50).min().shift(1)

    body = (work["close"] - work["open"]).abs()
    rng = (work["high"] - work["low"]).replace(0, np.nan)
    upper_wick = work["high"] - work[["open", "close"]].max(axis=1)
    lower_wick = work[["open", "close"]].min(axis=1) - work["low"]
    engulf_bull = (
        (work["close"].shift(1) < work["open"].shift(1))
        & (work["close"] > work["open"])
        & (np.minimum(work["open"], work["close"]) <= np.minimum(work["open"].shift(1), work["close"].shift(1)))
        & (np.maximum(work["open"], work["close"]) >= np.maximum(work["open"].shift(1), work["close"].shift(1)))
    )
    engulf_bear = (
        (work["close"].shift(1) > work["open"].shift(1))
        & (work["close"] < work["open"])
        & (np.minimum(work["open"], work["close"]) <= np.minimum(work["open"].shift(1), work["close"].shift(1)))
        & (np.maximum(work["open"], work["close"]) >= np.maximum(work["open"].shift(1), work["close"].shift(1)))
    )
    hammer = (lower_wick > body * 2.2) & (upper_wick < body * 0.8)
    shooting_star = (upper_wick > body * 2.2) & (lower_wick < body * 0.8)

    breakout_up = work["close"] > roll_high
    breakout_down = work["close"] < roll_low

    levels_work = levels_df.copy() if levels_df is not None and len(levels_df) else pd.DataFrame()
    if len(levels_work):
        levels_work["detected_at_utc"] = pd.to_datetime(levels_work["detected_at_utc"], utc=True)
    patterns_work = patterns_df.copy() if patterns_df is not None and len(patterns_df) else pd.DataFrame()
    if len(patterns_work):
        patterns_work["end_time_utc"] = pd.to_datetime(patterns_work["end_time_utc"], utc=True)

    sig_cfg = ta_cfg.get("signal", {}) if isinstance(ta_cfg, dict) else {}
    adx_min = float(sig_cfg.get("adx_min", 18.0))
    mfi_long_min = float(sig_cfg.get("mfi_long_min", 45.0))
    mfi_short_max = float(sig_cfg.get("mfi_short_max", 55.0))
    rr_min = float(sig_cfg.get("rr_min", 1.0))
    min_tp_reach_prob = float(sig_cfg.get("min_tp_reach_prob", 0.58))
    enable_structure_fallback = bool(sig_cfg.get("enable_structure_fallback", True))

    rows = []
    fallback_rows = []
    for idx, row in work.iterrows():
        ts = row["open_time_utc"]
        close_px = float(row["close"])
        hist_lvls = levels_work[levels_work["detected_at_utc"] <= ts] if len(levels_work) else levels_work
        sup_cands = hist_lvls[(hist_lvls["level_type"] == "support") & (hist_lvls["level_price"] < close_px)] if len(hist_lvls) else hist_lvls
        res_cands = hist_lvls[(hist_lvls["level_type"] == "resistance") & (hist_lvls["level_price"] > close_px)] if len(hist_lvls) else hist_lvls

        if len(sup_cands):
            sup_row = sup_cands.sort_values(["level_price", "strength_score"], ascending=[False, False]).iloc[0]
            sup = float(sup_row["level_price"])
            sup_strength = float(sup_row["strength_score"])
        else:
            sup = float(roll_low.iloc[idx]) if pd.notna(roll_low.iloc[idx]) else close_px * 0.995
            sup_strength = 0.0
        if len(res_cands):
            res_row = res_cands.sort_values(["level_price", "strength_score"], ascending=[True, False]).iloc[0]
            res = float(res_row["level_price"])
            res_strength = float(res_row["strength_score"])
        else:
            res = float(roll_high.iloc[idx]) if pd.notna(roll_high.iloc[idx]) else close_px * 1.005
            res_strength = 0.0

        long_signal = bool(breakout_up.iloc[idx] or engulf_bull.iloc[idx] or hammer.iloc[idx])
        short_signal = bool(breakout_down.iloc[idx] or engulf_bear.iloc[idx] or shooting_star.iloc[idx])

        # Indicator context
        adx = float(work.at[idx, "adx14"]) if pd.notna(work.at[idx, "adx14"]) else np.nan
        mfi = float(work.at[idx, "mfi14"]) if pd.notna(work.at[idx, "mfi14"]) else np.nan
        st_k = float(work.at[idx, "stoch_k14"]) if pd.notna(work.at[idx, "stoch_k14"]) else np.nan
        st_d = float(work.at[idx, "stoch_d14"]) if pd.notna(work.at[idx, "stoch_d14"]) else np.nan
        plus_di = float(work.at[idx, "plus_di14"]) if pd.notna(work.at[idx, "plus_di14"]) else np.nan
        minus_di = float(work.at[idx, "minus_di14"]) if pd.notna(work.at[idx, "minus_di14"]) else np.nan
        indicator_ready = np.isfinite(adx) and np.isfinite(mfi) and np.isfinite(st_k) and np.isfinite(st_d)

        side = "NO_TRADE"
        reason = "no_pattern_or_breakout"
        next_open_px = float(work.iloc[idx + 1]["open"]) if (idx + 1) < len(work) else np.nan
        has_next_open = np.isfinite(next_open_px)
        entry = next_open_px if has_next_open else close_px
        stop = entry
        tp = entry
        expected_move = 0.0
        tp_prob = 0.0
        rr = 0.0

        indicator_long_ok = indicator_ready and adx >= adx_min and plus_di > minus_di and mfi >= mfi_long_min and st_k >= st_d
        indicator_short_ok = indicator_ready and adx >= adx_min and minus_di > plus_di and mfi <= mfi_short_max and st_k <= st_d

        if long_signal and not short_signal:
            tp_struct = res
            raw_expected_move = (tp_struct - close_px) / max(close_px, 1e-9)
            expected_move = max(0.0, float(raw_expected_move))
            stop = min(sup, entry * 0.995)
            risk = (entry - stop) / max(entry, 1e-9)
            rr = expected_move / max(risk, 1e-9) if (np.isfinite(risk) and risk > 0) else 0.0
            if not has_next_open:
                reason = "no_next_candle"
            elif tp_struct <= close_px:
                reason = "tp_context_invalid"
            elif (not np.isfinite(risk)) or (not np.isfinite(expected_move)) or risk <= 0:
                reason = "sl_context_invalid"
            elif expected_move < min_tp_pct:
                reason = "tp_lt_1pct"
            elif expected_move < min_expected_move_pct:
                reason = "expected_move_below_min"
            elif rr < rr_min:
                reason = "rr_below_1"
            elif not indicator_long_ok:
                reason = "indicator_fail"
            else:
                tp_prob = float(min(0.95, max(0.50, 0.55 + expected_move * 10 + res_strength * 0.05)))
                if tp_prob < min_tp_reach_prob:
                    reason = "tp_prob_below_min"
                else:
                    side = "BUY"
                    reason = "long_signal_pass"
                    tp = tp_struct
        elif short_signal and not long_signal:
            tp_struct = sup
            raw_expected_move = (close_px - tp_struct) / max(close_px, 1e-9)
            expected_move = max(0.0, float(raw_expected_move))
            stop = max(res, entry * 1.005)
            risk = (stop - entry) / max(entry, 1e-9)
            rr = expected_move / max(risk, 1e-9) if (np.isfinite(risk) and risk > 0) else 0.0
            if not has_next_open:
                reason = "no_next_candle"
            elif tp_struct >= close_px:
                reason = "tp_context_invalid"
            elif (not np.isfinite(risk)) or (not np.isfinite(expected_move)) or risk <= 0:
                reason = "sl_context_invalid"
            elif expected_move < min_tp_pct:
                reason = "tp_lt_1pct"
            elif expected_move < min_expected_move_pct:
                reason = "expected_move_below_min"
            elif rr < rr_min:
                reason = "rr_below_1"
            elif not indicator_short_ok:
                reason = "indicator_fail"
            else:
                tp_prob = float(min(0.95, max(0.50, 0.55 + expected_move * 10 + sup_strength * 0.05)))
                if tp_prob < min_tp_reach_prob:
                    reason = "tp_prob_below_min"
                else:
                    side = "SELL"
                    reason = "short_signal_pass"
                    tp = tp_struct
        else:
            reason = "signal_conflict_or_none"

        # Formal fallback logging chain.
        fallback_mode = "none"
        if reason == "indicator_fail" and enable_structure_fallback:
            fallback_mode = "structure_fallback"
            # If indicator failed, allow structure-only entry with tighter confidence.
            if (long_signal and not short_signal) or (short_signal and not long_signal):
                if expected_move >= min_tp_pct and expected_move >= min_expected_move_pct and rr >= 1.0:
                    tp_prob = float(min(0.80, max(0.45, 0.50 + expected_move * 8)))
                    if tp_prob < min_tp_reach_prob:
                        reason = "tp_prob_below_min"
                    else:
                        side = "BUY" if long_signal else "SELL"
                        reason = "structure_fallback_pass"
                else:
                    reason = "structure_fallback_no_trade"
        fallback_rows.append(
            {
                "event_time_utc": _utc_iso_z(ts),
                "symbol": symbol,
                "timeframe": timeframe,
                "base_signal_long": bool(long_signal),
                "base_signal_short": bool(short_signal),
                "indicator_ready": bool(indicator_ready),
                "indicator_long_ok": bool(indicator_long_ok),
                "indicator_short_ok": bool(indicator_short_ok),
                "fallback_mode": fallback_mode,
                "final_decision": side,
                "reason_code": reason,
                "run_id": run_id,
            }
        )

        rows.append(
                {
                "signal_id": _uid("sig", symbol, timeframe, ts),
                "symbol": symbol,
                "timeframe": timeframe,
                "signal_time_utc": _utc_iso_z(ts),
                "side": {"BUY": 1, "SELL": -1}.get(side, 0),
                "entry_price": entry,
                "stop_price": stop,
                "take_profit_price": tp,
                "expected_move_pct": float(expected_move),
                "tp_reach_prob": tp_prob,
                "rr_estimate": float(rr if np.isfinite(rr) else 0.0),
                "adx14": float(adx) if np.isfinite(adx) else np.nan,
                "mfi14": float(mfi) if np.isfinite(mfi) else np.nan,
                "stoch_k14": float(st_k) if np.isfinite(st_k) else np.nan,
                "stoch_d14": float(st_d) if np.isfinite(st_d) else np.nan,
                "decision": side,
                "reason_code": reason,
                "run_id": run_id,
                "contract_version": SIGNAL_CONTRACT_VERSION,
                "calibration_mode": CALIBRATION_MODE_NONE,
            }
        )
    out = pd.DataFrame(rows)
    fallback_df = pd.DataFrame(fallback_rows)
    if out.empty:
        return out, fallback_df
    return out.sort_values("signal_time_utc").reset_index(drop=True), fallback_df


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic technical-analysis pipeline to analytics layer.")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--min-tp-pct", type=float, default=0.01)
    parser.add_argument("--min-expected-move-pct", type=float, default=0.002)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    ensure_storage_layout(project_root)
    ta_cfg = _load_ta_profile(project_root, args.timeframe)

    try:
        df = load_ohlcv_range(
            project_root,
            symbol=args.symbol,
            timeframe=args.timeframe,
            start_date=args.start_date,
            end_date=args.end_date,
            layer="core",
        )
        source_layer = "core"
    except Exception:
        df = load_ohlcv_range(
            project_root,
            symbol=args.symbol,
            timeframe=args.timeframe,
            start_date=args.start_date,
            end_date=args.end_date,
            layer="raw",
        )
        source_layer = "raw"

    run_id = datetime.now(timezone.utc).strftime("ta_%Y%m%dT%H%M%SZ")
    min_expected_move_pct = normalize_min_expected_move_pct(args.min_expected_move_pct)
    levels = _build_levels(df, symbol=args.symbol, timeframe=args.timeframe, run_id=run_id)
    patterns = _build_patterns(df, symbol=args.symbol, timeframe=args.timeframe, run_id=run_id, ta_cfg=ta_cfg)
    signals, fallback_log = _build_signals(
        df,
        symbol=args.symbol,
        timeframe=args.timeframe,
        run_id=run_id,
        levels_df=levels,
        patterns_df=patterns,
        ta_cfg=ta_cfg,
        min_tp_pct=float(args.min_tp_pct),
        min_expected_move_pct=min_expected_move_pct,
    )

    analytics_dir = project_root / "data" / "analytics"
    levels_path = analytics_dir / "levels.csv"
    patterns_path = analytics_dir / "pattern_events.csv"
    signals_path = analytics_dir / "signal_events.csv"
    fallback_path = analytics_dir / "signal_fallback_events.csv"

    lvl_written = _append_table(levels_path, levels, "level_id")
    ptn_written = _append_table(patterns_path, patterns, "pattern_id")
    sig_written = _append_table(
        signals_path,
        signals,
        "signal_id",
        dedupe_cols=["symbol", "timeframe", "signal_time_utc"],
    )
    fb_written = _append_table(
        fallback_path,
        fallback_log,
        "run_id",
        dedupe_cols=["symbol", "timeframe", "event_time_utc"],
    )

    register_partition(
        project_root,
        layer="analytics",
        dataset="levels",
        trade_date_utc=args.end_date,
        symbol=args.symbol,
        timeframe=args.timeframe,
        file_path=levels_path,
        rows=len(levels),
        run_id=run_id,
        status="written",
    )
    register_partition(
        project_root,
        layer="analytics",
        dataset="signal_fallback_events",
        trade_date_utc=args.end_date,
        symbol=args.symbol,
        timeframe=args.timeframe,
        file_path=fallback_path,
        rows=len(fallback_log),
        run_id=run_id,
        status="written",
    )

    # Optional parquet/xlsx exports for TA artifacts (best effort).
    export_info = {"parquet": {}, "xlsx": None}
    for name, path in {
        "levels": levels_path,
        "pattern_events": patterns_path,
        "signal_events": signals_path,
        "signal_fallback_events": fallback_path,
    }.items():
        try:
            df_src = pd.read_csv(path)
            pq = path.with_suffix(".parquet")
            df_src.to_parquet(pq, index=False)
            export_info["parquet"][name] = str(pq)
        except Exception:
            export_info["parquet"][name] = None
    try:
        xlsx_path = analytics_dir / f"technical_analysis_{args.symbol}_{args.timeframe}_{run_id}.xlsx"
        with pd.ExcelWriter(xlsx_path) as writer:
            levels.to_excel(writer, sheet_name="levels", index=False)
            patterns.to_excel(writer, sheet_name="patterns", index=False)
            signals.to_excel(writer, sheet_name="signals", index=False)
            fallback_log.to_excel(writer, sheet_name="fallback", index=False)
        export_info["xlsx"] = str(xlsx_path)
    except Exception:
        export_info["xlsx"] = None
    register_partition(
        project_root,
        layer="analytics",
        dataset="pattern_events",
        trade_date_utc=args.end_date,
        symbol=args.symbol,
        timeframe=args.timeframe,
        file_path=patterns_path,
        rows=len(patterns),
        run_id=run_id,
        status="written",
    )
    register_partition(
        project_root,
        layer="analytics",
        dataset="signal_events",
        trade_date_utc=args.end_date,
        symbol=args.symbol,
        timeframe=args.timeframe,
        file_path=signals_path,
        rows=len(signals),
        run_id=run_id,
        status="written",
    )

    report = {
        "run_id": run_id,
        "source_layer": source_layer,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "date_range": {"start": args.start_date, "end": args.end_date},
        "counts": {
            "levels_generated": len(levels),
            "patterns_generated": len(patterns),
            "signals_generated": len(signals),
            "levels_written_rows": lvl_written,
            "patterns_written_rows": ptn_written,
            "signals_written_rows": sig_written,
            "fallback_written_rows": fb_written,
        },
        "invariants": {
            "min_tp_pct": float(args.min_tp_pct),
            "min_expected_move_pct": min_expected_move_pct,
        },
        "contract_version": SIGNAL_CONTRACT_VERSION,
        "calibration_mode": CALIBRATION_MODE_NONE,
        "ta_profile": ta_cfg,
        "artifacts": {
            "levels_csv": str(levels_path),
            "pattern_events_csv": str(patterns_path),
            "signal_events_csv": str(signals_path),
            "signal_fallback_events_csv": str(fallback_path),
        },
        "exports": export_info,
    }
    rep_dir = project_root / "reports" / "technical_analysis"
    rep_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rep_path = rep_dir / f"ta_report_{args.symbol}_{args.timeframe}_{ts}.json"
    rep_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    audit_event(
        project_root,
        event="technical_analysis_completed",
        payload={
            "run_id": run_id,
            "symbol": args.symbol,
            "timeframe": args.timeframe,
            "report_path": str(rep_path),
            "source_layer": source_layer,
            "fallback_rows": int(len(fallback_log)),
        },
    )
    print(json.dumps({"report_path": str(rep_path), "run_id": run_id, "source_layer": source_layer}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
