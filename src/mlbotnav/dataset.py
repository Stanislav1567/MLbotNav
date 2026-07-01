from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from mlbotnav.timeframes import timeframe_aliases, canonical_timeframe


def _safe_canonical_tf(value: str) -> str:
    try:
        return canonical_timeframe(str(value))
    except Exception:
        return str(value)


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    rsi = rsi.where(~((avg_loss == 0) & (avg_gain > 0)), 100.0)
    rsi = rsi.where(~((avg_gain == 0) & (avg_loss > 0)), 0.0)
    rsi = rsi.where(~((avg_gain == 0) & (avg_loss == 0)), 50.0)
    return rsi


def _rolling_density_profile_features(
    close: pd.Series,
    volume: pd.Series,
    *,
    window: int,
    bin_pct: float = 0.0005,
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """
    Volume-at-price density proxies without future leakage.
    Uses only past-and-current bars in a sliding window.
    """
    c = pd.to_numeric(close, errors="coerce").to_numpy(dtype=float)
    v = pd.to_numeric(volume, errors="coerce").fillna(0.0).to_numpy(dtype=float)
    n = len(c)
    if n == 0:
        z = pd.Series(dtype=float)
        return z, z, z, z

    ref_price = float(np.nanmedian(c)) if np.isfinite(np.nanmedian(c)) else 1.0
    step = max(ref_price * float(bin_pct), 1e-8)
    bins = np.rint(c / step).astype(np.int64)

    vpoc_distance = np.full(n, np.nan, dtype=float)
    bin_share = np.full(n, np.nan, dtype=float)
    cluster_share = np.full(n, np.nan, dtype=float)
    vpoc_share = np.full(n, np.nan, dtype=float)

    hist: dict[int, float] = {}
    total_vol = 0.0
    w = max(2, int(window))
    for i in range(n):
        b_new = int(bins[i])
        v_new = max(float(v[i]), 0.0)
        hist[b_new] = hist.get(b_new, 0.0) + v_new
        total_vol += v_new

        if i >= w:
            b_old = int(bins[i - w])
            v_old = max(float(v[i - w]), 0.0)
            old = hist.get(b_old, 0.0) - v_old
            if old <= 1e-12:
                hist.pop(b_old, None)
            else:
                hist[b_old] = old
            total_vol -= v_old

        if i < (w - 1) or total_vol <= 1e-12 or not hist:
            continue

        b_cur = int(bins[i])
        cur_bin_vol = hist.get(b_cur, 0.0)
        b_vpoc, v_vpoc = max(hist.items(), key=lambda kv: kv[1])
        vpoc_px = float(b_vpoc) * step

        close_i = c[i]
        if np.isfinite(close_i) and abs(close_i) > 1e-12:
            vpoc_distance[i] = (close_i - vpoc_px) / close_i
        bin_share[i] = cur_bin_vol / total_vol
        cluster_share[i] = (hist.get(b_cur - 1, 0.0) + cur_bin_vol + hist.get(b_cur + 1, 0.0)) / total_vol
        vpoc_share[i] = v_vpoc / total_vol

    return (
        pd.Series(vpoc_distance, index=close.index),
        pd.Series(bin_share, index=close.index),
        pd.Series(cluster_share, index=close.index),
        pd.Series(vpoc_share, index=close.index),
    )


def _confirmed_fib_anchor_grid_features(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    *,
    max_lookback_bars: int = 240,
    depth_bars: int = 10,
    deviation_pct: float = 0.30,
) -> dict[str, pd.Series]:
    h = pd.to_numeric(high, errors="coerce").to_numpy(dtype=float)
    l = pd.to_numeric(low, errors="coerce").to_numpy(dtype=float)
    c = pd.to_numeric(close, errors="coerce").to_numpy(dtype=float)
    n = len(c)
    idx = close.index
    values = {
        "fib_0000": np.full(n, np.nan, dtype=float),
        "fib_0236": np.full(n, np.nan, dtype=float),
        "fib_0382": np.full(n, np.nan, dtype=float),
        "fib_0500": np.full(n, np.nan, dtype=float),
        "fib_0618": np.full(n, np.nan, dtype=float),
        "fib_0786": np.full(n, np.nan, dtype=float),
        "fib_1000": np.full(n, np.nan, dtype=float),
        "fib_direction": np.full(n, np.nan, dtype=float),
        "anchor_a_price": np.full(n, np.nan, dtype=float),
        "anchor_b_price": np.full(n, np.nan, dtype=float),
        "anchor_a_bar": np.full(n, np.nan, dtype=float),
        "anchor_b_bar": np.full(n, np.nan, dtype=float),
        "fib_0382_distance_pct": np.full(n, np.nan, dtype=float),
        "fib_0618_distance_pct": np.full(n, np.nan, dtype=float),
    }
    depth = max(1, int(depth_bars))
    max_lookback = max(depth * 2 + 1, int(max_lookback_bars))
    deviation = max(0.0, float(deviation_pct))
    pivots: list[tuple[str, int, float]] = []

    def _accept_pivot(kind: str, bar: int, price: float) -> None:
        if not np.isfinite(price) or price <= 0.0:
            return
        if not pivots:
            pivots.append((kind, bar, price))
            return
        last_kind, last_bar, last_price = pivots[-1]
        if kind == last_kind:
            replace = (kind == "HIGH" and price > last_price) or (kind == "LOW" and price < last_price)
            if replace:
                pivots[-1] = (kind, bar, price)
            return
        if last_price <= 0.0:
            return
        move_pct = abs(price / last_price - 1.0) * 100.0
        if move_pct >= deviation:
            pivots.append((kind, bar, price))

    for i in range(n):
        pivot_bar = i - depth
        if pivot_bar >= depth:
            left = pivot_bar - depth
            right = pivot_bar + depth + 1
            high_window = h[left:right]
            low_window = l[left:right]
            high_price = h[pivot_bar]
            low_price = l[pivot_bar]
            is_high = np.isfinite(high_price) and high_price >= np.nanmax(high_window)
            is_low = np.isfinite(low_price) and low_price <= np.nanmin(low_window)
            if is_high and not is_low:
                _accept_pivot("HIGH", pivot_bar, float(high_price))
            elif is_low and not is_high:
                _accept_pivot("LOW", pivot_bar, float(low_price))

        if len(pivots) < 2:
            continue
        a_kind, a_bar, a_price = pivots[-2]
        b_kind, b_bar, b_price = pivots[-1]
        if a_kind == b_kind:
            continue
        if (i - a_bar) > max_lookback or (i - b_bar) > max_lookback:
            continue
        swing_high = max(a_price, b_price)
        swing_low = min(a_price, b_price)
        fib_range = swing_high - swing_low
        close_i = c[i]
        if fib_range <= 0.0 or not np.isfinite(close_i) or close_i <= 0.0:
            continue
        up_leg = a_kind == "LOW" and b_kind == "HIGH"
        if up_leg:
            levels = {
                "fib_0000": swing_high,
                "fib_0236": swing_high - fib_range * 0.236,
                "fib_0382": swing_high - fib_range * 0.382,
                "fib_0500": swing_high - fib_range * 0.500,
                "fib_0618": swing_high - fib_range * 0.618,
                "fib_0786": swing_high - fib_range * 0.786,
                "fib_1000": swing_low,
            }
            direction = 1.0
        else:
            levels = {
                "fib_0000": swing_low,
                "fib_0236": swing_low + fib_range * 0.236,
                "fib_0382": swing_low + fib_range * 0.382,
                "fib_0500": swing_low + fib_range * 0.500,
                "fib_0618": swing_low + fib_range * 0.618,
                "fib_0786": swing_low + fib_range * 0.786,
                "fib_1000": swing_high,
            }
            direction = -1.0
        for name, price in levels.items():
            values[name][i] = price
        values["fib_direction"][i] = direction
        values["anchor_a_price"][i] = a_price
        values["anchor_b_price"][i] = b_price
        values["anchor_a_bar"][i] = float(a_bar)
        values["anchor_b_bar"][i] = float(b_bar)
        values["fib_0382_distance_pct"][i] = (close_i / levels["fib_0382"] - 1.0) * 100.0
        values["fib_0618_distance_pct"][i] = (close_i / levels["fib_0618"] - 1.0) * 100.0

    return {name: pd.Series(arr, index=idx) for name, arr in values.items()}


def _nearest_context_from_levels(
    entry_ref: pd.Series,
    levels: list[pd.Series],
) -> dict[str, pd.Series]:
    if not levels:
        empty = pd.Series(np.nan, index=entry_ref.index)
        return {
            "tp_long": empty,
            "sl_long": empty,
            "tp_short": empty,
            "sl_short": empty,
            "tp_dist_long": empty,
            "sl_dist_long": empty,
            "rr_long": empty,
            "tp_dist_short": empty,
            "sl_dist_short": empty,
            "rr_short": empty,
        }

    clean_levels = [pd.to_numeric(level, errors="coerce").reindex(entry_ref.index) for level in levels]
    candidates = pd.concat(clean_levels, axis=1)
    ref = pd.to_numeric(entry_ref, errors="coerce")
    valid_ref = ref > 0.0
    above = candidates.where(candidates.gt(ref, axis=0))
    below = candidates.where(candidates.lt(ref, axis=0))
    nearest_above = above.min(axis=1, skipna=True)
    nearest_below = below.max(axis=1, skipna=True)

    tp_long = nearest_above.where(valid_ref)
    sl_long = nearest_below.where(valid_ref)
    tp_short = nearest_below.where(valid_ref)
    sl_short = nearest_above.where(valid_ref)

    tp_dist_long = (tp_long / ref - 1.0) * 100.0
    sl_dist_long = (ref / sl_long - 1.0) * 100.0
    tp_dist_short = (ref / tp_short - 1.0) * 100.0
    sl_dist_short = (sl_short / ref - 1.0) * 100.0
    rr_long = tp_dist_long / sl_dist_long.replace(0, np.nan)
    rr_short = tp_dist_short / sl_dist_short.replace(0, np.nan)
    return {
        "tp_long": tp_long,
        "sl_long": sl_long,
        "tp_short": tp_short,
        "sl_short": sl_short,
        "tp_dist_long": tp_dist_long,
        "sl_dist_long": sl_dist_long,
        "rr_long": rr_long,
        "tp_dist_short": tp_dist_short,
        "sl_dist_short": sl_dist_short,
        "rr_short": rr_short,
    }


def _confirmed_swing_levels(
    high: pd.Series,
    low: pd.Series,
    *,
    lookback_bars: int = 240,
    pivot_left: int = 3,
    pivot_right: int = 3,
) -> dict[str, pd.Series]:
    h = pd.to_numeric(high, errors="coerce").to_numpy(dtype=float)
    l = pd.to_numeric(low, errors="coerce").to_numpy(dtype=float)
    n = len(h)
    idx = high.index
    last_high = np.full(n, np.nan, dtype=float)
    last_low = np.full(n, np.nan, dtype=float)
    last_high_price = np.nan
    last_low_price = np.nan
    last_high_pivot = -10**9
    last_low_pivot = -10**9
    left = max(1, int(pivot_left))
    right = max(1, int(pivot_right))
    lookback = max(left + right + 1, int(lookback_bars))
    high_confirms: dict[int, tuple[int, float]] = {}
    low_confirms: dict[int, tuple[int, float]] = {}

    for pivot in range(left, max(left, n - right)):
        hi = h[pivot]
        lo = l[pivot]
        if np.isfinite(hi):
            window = h[pivot - left : pivot + right + 1]
            if len(window) and hi >= np.nanmax(window):
                high_confirms[pivot + right] = (pivot, float(hi))
        if np.isfinite(lo):
            window = l[pivot - left : pivot + right + 1]
            if len(window) and lo <= np.nanmin(window):
                low_confirms[pivot + right] = (pivot, float(lo))

    for i in range(n):
        if i in high_confirms:
            last_high_pivot, last_high_price = high_confirms[i]
        if i in low_confirms:
            last_low_pivot, last_low_price = low_confirms[i]
        if i - last_high_pivot <= lookback and np.isfinite(last_high_price):
            last_high[i] = last_high_price
        if i - last_low_pivot <= lookback and np.isfinite(last_low_price):
            last_low[i] = last_low_price

    return {
        "last_swing_high": pd.Series(last_high, index=idx),
        "last_swing_low": pd.Series(last_low, index=idx),
    }


def _confirmed_market_structure_state(
    high: pd.Series,
    low: pd.Series,
    *,
    lookback_bars: int,
    pivot_left: int,
    pivot_right: int,
    min_swing_pct: float,
) -> dict[str, pd.Series]:
    h = pd.to_numeric(high, errors="coerce").to_numpy(dtype=float)
    l = pd.to_numeric(low, errors="coerce").to_numpy(dtype=float)
    n = len(h)
    idx = high.index
    left = max(1, int(pivot_left))
    right = max(1, int(pivot_right))
    lookback = max(left + right + 1, int(lookback_bars))
    min_pct = max(0.0, float(min_swing_pct)) / 100.0
    high_confirms: dict[int, tuple[int, float]] = {}
    low_confirms: dict[int, tuple[int, float]] = {}

    for pivot in range(left, max(left, n - right)):
        hi = h[pivot]
        lo = l[pivot]
        if np.isfinite(hi):
            window = h[pivot - left : pivot + right + 1]
            if len(window) and hi >= np.nanmax(window):
                high_confirms[pivot + right] = (pivot, float(hi))
        if np.isfinite(lo):
            window = l[pivot - left : pivot + right + 1]
            if len(window) and lo <= np.nanmin(window):
                low_confirms[pivot + right] = (pivot, float(lo))

    last_high = np.full(n, np.nan, dtype=float)
    prev_high = np.full(n, np.nan, dtype=float)
    last_low = np.full(n, np.nan, dtype=float)
    prev_low = np.full(n, np.nan, dtype=float)
    protected_high = np.full(n, np.nan, dtype=float)
    protected_low = np.full(n, np.nan, dtype=float)
    bias = np.zeros(n, dtype=float)
    lh = np.nan
    ph = np.nan
    ll = np.nan
    pl = np.nan
    lh_pivot = -10**9
    ll_pivot = -10**9

    for i in range(n):
        if i in high_confirms:
            pivot, price = high_confirms[i]
            if not np.isfinite(lh) or abs(price / lh - 1.0) >= min_pct:
                ph = lh
                lh = price
                lh_pivot = pivot
        if i in low_confirms:
            pivot, price = low_confirms[i]
            if not np.isfinite(ll) or abs(price / ll - 1.0) >= min_pct:
                pl = ll
                ll = price
                ll_pivot = pivot
        high_valid = i - lh_pivot <= lookback and np.isfinite(lh) and lh > 0.0
        low_valid = i - ll_pivot <= lookback and np.isfinite(ll) and ll > 0.0
        if high_valid:
            last_high[i] = lh
            prev_high[i] = ph
        if low_valid:
            last_low[i] = ll
            prev_low[i] = pl
        if high_valid and low_valid and np.isfinite(ph) and np.isfinite(pl):
            if lh > ph and ll > pl:
                bias[i] = 1.0
                protected_low[i] = ll
            elif lh < ph and ll < pl:
                bias[i] = -1.0
                protected_high[i] = lh

    return {
        "last_structure_high": pd.Series(last_high, index=idx),
        "prev_structure_high": pd.Series(prev_high, index=idx),
        "last_structure_low": pd.Series(last_low, index=idx),
        "prev_structure_low": pd.Series(prev_low, index=idx),
        "protected_high": pd.Series(protected_high, index=idx),
        "protected_low": pd.Series(protected_low, index=idx),
        "structure_bias": pd.Series(bias, index=idx),
    }


def _confirmed_divergence_pivot_pairs(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    indicator: pd.Series,
    *,
    pivot_kind: str,
    lookback_bars: int,
    pivot_left: int,
    pivot_right: int,
    min_price_swing_pct: float,
) -> dict[str, pd.Series]:
    h = pd.to_numeric(high, errors="coerce").to_numpy(dtype=float)
    l = pd.to_numeric(low, errors="coerce").to_numpy(dtype=float)
    c = pd.to_numeric(close, errors="coerce").to_numpy(dtype=float)
    ind = pd.to_numeric(indicator, errors="coerce").to_numpy(dtype=float)
    n = len(c)
    idx = close.index
    left = max(1, int(pivot_left))
    right = max(1, int(pivot_right))
    lookback = max(left + right + 1, int(lookback_bars))
    min_pct = max(0.0, float(min_price_swing_pct)) / 100.0
    use_high = str(pivot_kind).lower() == "high"
    source = h if use_high else l
    confirms: dict[int, tuple[int, float, float, float]] = {}

    for pivot in range(left, max(left, n - right)):
        price = source[pivot]
        close_px = c[pivot]
        ind_value = ind[pivot]
        if not (np.isfinite(price) and price > 0.0 and np.isfinite(close_px) and close_px > 0.0 and np.isfinite(ind_value)):
            continue
        window = source[pivot - left : pivot + right + 1]
        if not len(window):
            continue
        if use_high:
            is_pivot = price >= np.nanmax(window)
        else:
            is_pivot = price <= np.nanmin(window)
        if is_pivot:
            confirms[pivot + right] = (pivot, float(price), float(ind_value), float(close_px))

    prev_price = np.full(n, np.nan, dtype=float)
    last_price = np.full(n, np.nan, dtype=float)
    prev_indicator = np.full(n, np.nan, dtype=float)
    last_indicator = np.full(n, np.nan, dtype=float)
    last_close = np.full(n, np.nan, dtype=float)
    gap_bars = np.full(n, np.nan, dtype=float)
    prev_pivot = -10**9
    last_pivot = -10**9
    pp = np.nan
    lp = np.nan
    pi = np.nan
    li = np.nan
    lc = np.nan

    for i in range(n):
        if i in confirms:
            pivot, price, ind_value, close_px = confirms[i]
            if not np.isfinite(lp) or abs(price / lp - 1.0) >= min_pct:
                prev_pivot = last_pivot
                pp = lp
                pi = li
                last_pivot = pivot
                lp = price
                li = ind_value
                lc = close_px
        valid_pair = (
            np.isfinite(pp)
            and np.isfinite(lp)
            and np.isfinite(pi)
            and np.isfinite(li)
            and np.isfinite(lc)
            and i - last_pivot <= lookback
        )
        if valid_pair:
            prev_price[i] = pp
            last_price[i] = lp
            prev_indicator[i] = pi
            last_indicator[i] = li
            last_close[i] = lc
            gap_bars[i] = float(last_pivot - prev_pivot)

    return {
        "prev_price": pd.Series(prev_price, index=idx),
        "last_price": pd.Series(last_price, index=idx),
        "prev_indicator": pd.Series(prev_indicator, index=idx),
        "last_indicator": pd.Series(last_indicator, index=idx),
        "last_close": pd.Series(last_close, index=idx),
        "gap_bars": pd.Series(gap_bars, index=idx),
    }


def _nearest_break_levels(
    ref_price: pd.Series,
    levels: list[pd.Series],
) -> dict[str, pd.Series]:
    if not levels:
        empty = pd.Series(np.nan, index=ref_price.index)
        return {"up": empty, "down": empty}
    clean_levels = [pd.to_numeric(level, errors="coerce").reindex(ref_price.index) for level in levels]
    candidates = pd.concat(clean_levels, axis=1)
    ref = pd.to_numeric(ref_price, errors="coerce")
    valid_ref = ref > 0.0
    up = candidates.where(candidates.ge(ref, axis=0)).min(axis=1, skipna=True).where(valid_ref)
    down = candidates.where(candidates.le(ref, axis=0)).max(axis=1, skipna=True).where(valid_ref)
    return {"up": up, "down": down}


def list_available_days(project_root: Path, *, layer: str = "raw") -> list[str]:
    base = project_root / "data" / layer / "bybit_ohlcv"
    if not base.exists():
        return []
    out: list[str] = []
    for d in base.glob("dt=*"):
        if d.is_dir():
            out.append(d.name.split("=", 1)[1])
    return sorted(out)


def load_ohlcv_range(
    project_root: Path,
    *,
    symbol: str,
    timeframe: str,
    start_date: str | None = None,
    end_date: str | None = None,
    layer: str = "raw",
) -> pd.DataFrame:
    tf_aliases = timeframe_aliases(timeframe)
    canonical_tf = canonical_timeframe(timeframe)
    days = list_available_days(project_root, layer=layer)
    if start_date:
        days = [d for d in days if d >= start_date]
    if end_date:
        days = [d for d in days if d <= end_date]

    frames: list[pd.DataFrame] = []
    for day in days:
        for tf_label in tf_aliases:
            p = (
                project_root
                / "data"
                / layer
                / "bybit_ohlcv"
                / f"dt={day}"
                / f"tf={tf_label}"
                / f"symbol={symbol}"
                / "part-final.csv"
            )
            if p.exists():
                frames.append(pd.read_csv(p))
                break

    if not frames:
        raise FileNotFoundError(
            f"No part-final.csv for symbol={symbol}, timeframe={canonical_tf}, layer={layer}, range=({start_date}, {end_date})"
        )

    df = pd.concat(frames, ignore_index=True)
    if "timeframe" in df.columns:
        df["timeframe"] = df["timeframe"].astype(str).map(_safe_canonical_tf)
    # Mixed-format safe parse: supports both "YYYY-MM-DDTHH:MM:SS+00:00" and
    # "YYYY-MM-DD HH:MM:SS+00:00" across different ingest runs.
    df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], utc=True, errors="coerce", format="mixed")
    df["close_time_utc"] = pd.to_datetime(df["close_time_utc"], utc=True, errors="coerce", format="mixed")
    df = df.dropna(subset=["open_time_utc", "close_time_utc"])
    df = df.sort_values("open_time_utc").drop_duplicates(subset=["open_time_utc"]).reset_index(drop=True)
    return df


def build_feature_frame(
    df: pd.DataFrame,
    *,
    horizon_bars: int = 1,
    calibration_params: dict[str, float] | None = None,
    include_targets: bool = True,
    include_dropna: bool = True,
) -> pd.DataFrame:
    out = df.copy()
    cp = dict(calibration_params or {})

    def _cp_int(name: str, default: int, min_v: int = 1) -> int:
        try:
            v = int(round(float(cp.get(name, default))))
        except Exception:
            v = int(default)
        return int(max(min_v, v))

    def _cp_float(name: str, default: float, min_v: float = 0.0) -> float:
        try:
            v = float(cp.get(name, default))
        except Exception:
            v = float(default)
        return float(max(min_v, v))

    return_lookback = _cp_int("return_lookback", 1, min_v=1)
    rolling_window = _cp_int("rolling_window", 20, min_v=2)
    period_standard = _cp_int("period_standard", 14, min_v=2)
    ema_slow_period = _cp_int("ema_slow_period", 50, min_v=2)
    ema_ultra_period = _cp_int("ema_ultra_period", 200, min_v=2)
    macd_fast_period = _cp_int("macd_fast_period", 12, min_v=2)
    macd_slow_period = _cp_int("macd_slow_period", 26, min_v=3)
    if macd_slow_period <= macd_fast_period:
        macd_slow_period = macd_fast_period + 1
    macd_signal_period = _cp_int("macd_signal_period", 9, min_v=2)
    stoch_d_period = _cp_int("stoch_d_period", 3, min_v=2)
    threshold_fine = _cp_float("threshold_fine", 0.0015, min_v=0.0)
    fib_window = _cp_int("fib_window", rolling_window, min_v=2)
    fib_level = min(3.0, _cp_float("fib_level", 0.382, min_v=0.0))
    pattern_window = _cp_int("pattern_window", rolling_window, min_v=5)
    min_touches = _cp_int("min_touches", 2, min_v=1)
    breakout_threshold = _cp_float("breakout_threshold", threshold_fine, min_v=0.0)
    retest_window = _cp_int("retest_window", return_lookback, min_v=1)
    level_distance_threshold = _cp_float("level_distance_threshold", threshold_fine, min_v=0.0)
    volume_confirm_threshold = _cp_float("volume_confirm_threshold", 0.5, min_v=0.0)
    vol_z_window = _cp_int("vol_z_window", rolling_window, min_v=5)
    sl_buffer = _cp_float("sl_buffer", 0.001, min_v=0.0)
    tp_ladder = _cp_int("tp_ladder", 3, min_v=1)
    doji_threshold = _cp_float("doji_threshold", 0.10, min_v=0.0)
    ratio_pattern = _cp_float("ratio_pattern", 2.0, min_v=0.1)
    ratio_opposite_wick_cap = _cp_float("ratio_opposite_wick_cap", 1.0, min_v=0.0)
    density_window_short = _cp_int("density_window_short", 60, min_v=5)
    density_window_long = _cp_int("density_window_long", 240, min_v=10)
    if density_window_long <= density_window_short:
        density_window_long = density_window_short + 10
    density_bin_pct = _cp_float("density_bin_pct", 0.0005, min_v=1e-6)
    div_lookback = _cp_int("div_lookback", 10, min_v=1)
    pattern_age_cap = _cp_int("pattern_age_cap", 10_000, min_v=1)
    out["ret_1"] = out["close"].pct_change(return_lookback)
    out["ret_3"] = out["close"].pct_change(return_lookback * 3)
    out["ret_6"] = out["close"].pct_change(return_lookback * 6)
    out["ret_12"] = out["close"].pct_change(return_lookback * 12)
    out["ret_24"] = out["close"].pct_change(return_lookback * 24)
    cp_keys = set(dict(calibration_params or {}).keys())
    ret_n_family_move_active = "B001_family_move" in cp_keys
    ret_n_family_move = 1 if _cp_float("B001_family_move", 1.0, min_v=-1.0) >= 0.0 else -1
    for spec in RET_N_ACTION_SPECS:
        if not ret_n_family_move_active and spec["move_param"] not in cp_keys and spec["thr_param"] not in cp_keys:
            continue
        move = ret_n_family_move if ret_n_family_move_active else 1 if _cp_float(spec["move_param"], 1.0, min_v=-1.0) >= 0.0 else -1
        thr_pct = min(
            float(spec["thr_max"]),
            _cp_float(spec["thr_param"], float(spec["thr_min"]), min_v=float(spec["thr_min"])),
        )
        ret_pct = out["close"].pct_change(int(spec["n"])) * 100.0
        out[str(spec["column"])] = np.where(
            ((move > 0) & (ret_pct >= thr_pct)) | ((move < 0) & (ret_pct <= -thr_pct)),
            1,
            0,
        ).astype("int64")
    out["hl_spread"] = (out["high"] - out["low"]) / out["open"].replace(0, np.nan)
    if "F006_cmp" in cp_keys or "F006_thr_pct" in cp_keys:
        cmp_raw = _cp_float("F006_cmp", 1.0, min_v=-1.0)
        is_greater = cmp_raw >= 0.0
        thr_pct = min(1.50, _cp_float("F006_thr_pct", 0.02, min_v=0.02))
        hl_spread_pct = out["hl_spread"] * 100.0
        out["F006_HLSPREAD_ALLOW"] = np.where(
            ((is_greater) & (hl_spread_pct >= thr_pct)) | ((not is_greater) & (hl_spread_pct <= thr_pct)),
            1,
            0,
        ).astype("int64")
    out["rolling_std_20"] = out["close"].pct_change().rolling(rolling_window).std()
    if "F007_cmp" in cp_keys or "F007_thr_pct" in cp_keys:
        cmp_raw = _cp_float("F007_cmp", 1.0, min_v=-1.0)
        is_greater = cmp_raw >= 0.0
        thr_pct = min(0.50, _cp_float("F007_thr_pct", 0.01, min_v=0.01))
        rstd20_pct = (out["close"].pct_change() * 100.0).rolling(20).std(ddof=0)
        out["F007_RSTD20_ALLOW"] = np.where(
            ((is_greater) & (rstd20_pct >= thr_pct)) | ((not is_greater) & (rstd20_pct <= thr_pct)),
            1,
            0,
        ).astype("int64")
    out["vol_chg"] = out["volume"].pct_change(return_lookback)
    out["vol_z"] = (out["volume"] - out["volume"].rolling(vol_z_window).mean()) / out["volume"].rolling(vol_z_window).std()
    if "F019_direction" in cp_keys or "F019_thr_pct" in cp_keys:
        direction_raw = _cp_float("F019_direction", 1.0, min_v=-1.0)
        is_up = direction_raw >= 0.0
        thr_pct = min(300.0, _cp_float("F019_thr_pct", 5.0, min_v=5.0))
        prev_volume = out["volume"].shift(1)
        vol_chg_pct = (out["volume"] / prev_volume.replace(0, np.nan) - 1.0) * 100.0
        valid = prev_volume > 0.0
        out["F019_VOLCHG_ALLOW"] = np.where(
            valid & (((is_up) & (vol_chg_pct >= thr_pct)) | ((not is_up) & (vol_chg_pct <= -thr_pct))),
            1,
            0,
        ).astype("int64")
    if "F020_state" in cp_keys or "F020_z_level" in cp_keys:
        state_raw = _cp_float("F020_state", 1.0, min_v=-1.0)
        is_high = state_raw >= 0.0
        z_level = min(5.0, _cp_float("F020_z_level", 0.0, min_v=0.0))
        vol_mean20 = out["volume"].rolling(20).mean()
        vol_std20 = out["volume"].rolling(20).std(ddof=0)
        vol_z20 = (out["volume"] - vol_mean20) / vol_std20.replace(0, np.nan)
        valid = vol_std20 > 0.0
        out["F020_VOLZ20_ALLOW"] = np.where(
            valid & (((is_high) & (vol_z20 >= z_level)) | ((not is_high) & (vol_z20 <= -z_level))),
            1,
            0,
        ).astype("int64")
    out["ema20"] = out["close"].ewm(span=period_standard, adjust=False).mean()
    out["ema50"] = out["close"].ewm(span=ema_slow_period, adjust=False).mean()
    out["ema200"] = out["close"].ewm(span=ema_ultra_period, adjust=False).mean()
    out["ema_gap"] = (out["ema20"] - out["ema50"]) / out["close"].replace(0, np.nan)
    out["ema_slope_5"] = out["ema20"].pct_change(return_lookback)
    out["ema200_gap"] = (out["close"] - out["ema200"]) / out["close"].replace(0, np.nan)
    ema20_fixed = out["close"].ewm(span=20, adjust=False).mean()
    ema50_fixed = out["close"].ewm(span=50, adjust=False).mean()
    ema200_fixed = out["close"].ewm(span=200, adjust=False).mean()
    if "F009_bias" in cp_keys or "F009_thr_pct" in cp_keys:
        bias_raw = _cp_float("F009_bias", 1.0, min_v=-1.0)
        is_above = bias_raw >= 0.0
        thr_pct = min(2.00, _cp_float("F009_thr_pct", 0.0, min_v=0.0))
        ema_gap_pct = (ema20_fixed / ema50_fixed.replace(0, np.nan) - 1.0) * 100.0
        out["F009_EMAGAP_ALLOW"] = np.where(
            ((is_above) & (ema_gap_pct >= thr_pct)) | ((not is_above) & (ema_gap_pct <= -thr_pct)),
            1,
            0,
        ).astype("int64")
    if "F010_slope" in cp_keys or "F010_thr_pct" in cp_keys:
        slope_raw = _cp_float("F010_slope", 1.0, min_v=-1.0)
        is_up = slope_raw >= 0.0
        thr_pct = min(1.00, _cp_float("F010_thr_pct", 0.0, min_v=0.0))
        ema_slope_5_pct = (ema20_fixed / ema20_fixed.shift(5).replace(0, np.nan) - 1.0) * 100.0
        out["F010_EMASLOPE5_ALLOW"] = np.where(
            ((is_up) & (ema_slope_5_pct >= thr_pct)) | ((not is_up) & (ema_slope_5_pct <= -thr_pct)),
            1,
            0,
        ).astype("int64")
    if "F011_position" in cp_keys or "F011_thr_pct" in cp_keys:
        position_raw = _cp_float("F011_position", 1.0, min_v=-1.0)
        is_above = position_raw >= 0.0
        thr_pct = min(5.00, _cp_float("F011_thr_pct", 0.0, min_v=0.0))
        ema200_gap_pct = (out["close"] / ema200_fixed.replace(0, np.nan) - 1.0) * 100.0
        out["F011_EMA200GAP_ALLOW"] = np.where(
            ((is_above) & (ema200_gap_pct >= thr_pct)) | ((not is_above) & (ema200_gap_pct <= -thr_pct)),
            1,
            0,
        ).astype("int64")

    ema12 = out["close"].ewm(span=macd_fast_period, adjust=False).mean()
    ema26 = out["close"].ewm(span=macd_slow_period, adjust=False).mean()
    out["macd_line"] = ema12 - ema26
    out["macd_signal"] = out["macd_line"].ewm(span=macd_signal_period, adjust=False).mean()
    out["macd_hist"] = out["macd_line"] - out["macd_signal"]
    prev_close_for_macd = out["close"].shift(1).replace(0, np.nan)
    macd_ema12_fixed = out["close"].ewm(span=12, adjust=False).mean()
    macd_ema26_fixed = out["close"].ewm(span=26, adjust=False).mean()
    macd_line_fixed = macd_ema12_fixed - macd_ema26_fixed
    macd_signal_fixed = macd_line_fixed.ewm(span=9, adjust=False).mean()
    macd_hist_fixed = macd_line_fixed - macd_signal_fixed
    if "F013_state" in cp_keys or "F013_thr_pct" in cp_keys:
        state_raw = _cp_float("F013_state", 1.0, min_v=-1.0)
        is_positive = state_raw >= 0.0
        thr_pct = min(2.00, _cp_float("F013_thr_pct", 0.0, min_v=0.0))
        macd_line_pct = (macd_line_fixed / prev_close_for_macd) * 100.0
        out["F013_MACDLINE_ALLOW"] = np.where(
            ((is_positive) & (macd_line_pct >= thr_pct)) | ((not is_positive) & (macd_line_pct <= -thr_pct)),
            1,
            0,
        ).astype("int64")
    if "F014_state" in cp_keys or "F014_thr_pct" in cp_keys:
        state_raw = _cp_float("F014_state", 1.0, min_v=-1.0)
        is_positive = state_raw >= 0.0
        thr_pct = min(2.00, _cp_float("F014_thr_pct", 0.0, min_v=0.0))
        macd_signal_pct = (macd_signal_fixed / prev_close_for_macd) * 100.0
        out["F014_MACDSIGNAL_ALLOW"] = np.where(
            ((is_positive) & (macd_signal_pct >= thr_pct)) | ((not is_positive) & (macd_signal_pct <= -thr_pct)),
            1,
            0,
        ).astype("int64")
    if "F015_state" in cp_keys or "F015_thr_pct" in cp_keys:
        state_raw = _cp_float("F015_state", 1.0, min_v=-1.0)
        is_positive = state_raw >= 0.0
        thr_pct = min(1.00, _cp_float("F015_thr_pct", 0.0, min_v=0.0))
        macd_hist_pct = (macd_hist_fixed / prev_close_for_macd) * 100.0
        out["F015_MACDHIST_ALLOW"] = np.where(
            ((is_positive) & (macd_hist_pct >= thr_pct)) | ((not is_positive) & (macd_hist_pct <= -thr_pct)),
            1,
            0,
        ).astype("int64")
    out["rsi14"] = _rsi(out["close"], period=period_standard)
    if any(k in cp_keys for k in ("F012_signal_mode", "F012_cmp", "F012_level", "F012_relation", "F012_gap")):
        signal_mode = int(round(_cp_float("F012_signal_mode", 1.0, min_v=1.0)))
        rsi14_fixed = _rsi(out["close"], period=14)
        if signal_mode <= 1:
            cmp_raw = _cp_float("F012_cmp", 1.0, min_v=-1.0)
            is_greater = cmp_raw >= 0.0
            level = min(90, _cp_int("F012_level", 50, min_v=10))
            out["F012_RSI14_ALLOW"] = np.where(
                ((is_greater) & (rsi14_fixed >= float(level))) | ((not is_greater) & (rsi14_fixed <= float(level))),
                1,
                0,
            ).astype("int64")
        else:
            relation_raw = _cp_float("F012_relation", 1.0, min_v=-1.0)
            is_above = relation_raw >= 0.0
            gap = min(20, _cp_int("F012_gap", 0, min_v=0))
            rsi_ma_gap = rsi14_fixed - rsi14_fixed.rolling(14).mean()
            out["F012_RSI14_ALLOW"] = np.where(
                ((is_above) & (rsi_ma_gap >= float(gap))) | ((not is_above) & (rsi_ma_gap <= -float(gap))),
                1,
                0,
            ).astype("int64")

    prev_close = out["close"].shift(1)
    tr = pd.concat(
        [
            (out["high"] - out["low"]).abs(),
            (out["high"] - prev_close).abs(),
            (out["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    out["atr14"] = tr.rolling(period_standard).mean() / out["close"].replace(0, np.nan)
    if "F008_cmp" in cp_keys or "F008_thr_pct" in cp_keys:
        cmp_raw = _cp_float("F008_cmp", 1.0, min_v=-1.0)
        is_greater = cmp_raw >= 0.0
        thr_pct = min(3.00, _cp_float("F008_thr_pct", 0.01, min_v=0.01))
        atr14_wilder_pct = (tr.ewm(alpha=1.0 / 14.0, adjust=False, min_periods=14).mean() / out["close"].replace(0, np.nan)) * 100.0
        out["F008_ATR14_ALLOW"] = np.where(
            ((is_greater) & (atr14_wilder_pct >= thr_pct)) | ((not is_greater) & (atr14_wilder_pct <= thr_pct)),
            1,
            0,
        ).astype("int64")

    up_move = out["high"].diff()
    down_move = -out["low"].diff()
    plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0.0), index=out.index)
    minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0.0), index=out.index)
    atr_raw = tr.rolling(period_standard).mean().replace(0, np.nan)
    plus_di = 100.0 * plus_dm.rolling(period_standard).mean() / atr_raw
    minus_di = 100.0 * minus_dm.rolling(period_standard).mean() / atr_raw
    dx = (100.0 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)).replace([np.inf, -np.inf], np.nan)
    out["adx14"] = dx.rolling(period_standard).mean()
    if "F016_cmp" in cp_keys or "F016_level" in cp_keys:
        cmp_raw = _cp_float("F016_cmp", 1.0, min_v=-1.0)
        is_greater = cmp_raw >= 0.0
        level = min(60, _cp_int("F016_level", 25, min_v=5))
        atr14_wilder_raw = tr.ewm(alpha=1.0 / 14.0, adjust=False, min_periods=14).mean().replace(0, np.nan)
        plus_di14 = 100.0 * plus_dm.ewm(alpha=1.0 / 14.0, adjust=False, min_periods=14).mean() / atr14_wilder_raw
        minus_di14 = 100.0 * minus_dm.ewm(alpha=1.0 / 14.0, adjust=False, min_periods=14).mean() / atr14_wilder_raw
        dx14 = (100.0 * (plus_di14 - minus_di14).abs() / (plus_di14 + minus_di14).replace(0, np.nan)).replace(
            [np.inf, -np.inf],
            np.nan,
        )
        adx14_fixed = dx14.ewm(alpha=1.0 / 14.0, adjust=False, min_periods=14).mean()
        out["F016_ADX14_ALLOW"] = np.where(
            ((is_greater) & (adx14_fixed >= float(level))) | ((not is_greater) & (adx14_fixed <= float(level))),
            1,
            0,
        ).astype("int64")

    ll14 = out["low"].rolling(period_standard).min()
    hh14 = out["high"].rolling(period_standard).max()
    out["stoch_k14"] = 100.0 * (out["close"] - ll14) / (hh14 - ll14).replace(0, np.nan)
    out["stoch_d14"] = out["stoch_k14"].rolling(stoch_d_period).mean()
    if any(
        k in cp_keys
        for k in (
            "F017_F018_signal_mode",
            "F017_F018_line",
            "F017_F018_cmp",
            "F017_F018_level",
            "F017_F018_cross_dir",
            "F017_F018_zone_filter",
            "F017_F018_low_level",
            "F017_F018_high_level",
            "F017_F018_gap",
        )
    ):
        signal_mode = int(round(_cp_float("F017_F018_signal_mode", 1.0, min_v=1.0)))
        ll14_fixed = out["low"].rolling(14).min()
        hh14_fixed = out["high"].rolling(14).max()
        stoch_k14_fixed = 100.0 * (out["close"] - ll14_fixed) / (hh14_fixed - ll14_fixed).replace(0, np.nan)
        stoch_d14_fixed = stoch_k14_fixed.rolling(3).mean()
        if signal_mode <= 1:
            line_raw = int(round(_cp_float("F017_F018_line", 1.0, min_v=1.0)))
            cmp_raw = _cp_float("F017_F018_cmp", 1.0, min_v=-1.0)
            level = min(90, _cp_int("F017_F018_level", 50, min_v=10))
            line_values = stoch_k14_fixed if line_raw <= 1 else stoch_d14_fixed
            is_greater = cmp_raw >= 0.0
            out["F017_F018_STOCH14_ALLOW"] = np.where(
                ((is_greater) & (line_values >= float(level))) | ((not is_greater) & (line_values <= float(level))),
                1,
                0,
            ).astype("int64")
        else:
            cross_dir_raw = _cp_float("F017_F018_cross_dir", 1.0, min_v=-1.0)
            zone_raw = int(round(_cp_float("F017_F018_zone_filter", 0.0, min_v=-1.0)))
            low_level = min(40, _cp_int("F017_F018_low_level", 20, min_v=10))
            high_level = min(90, _cp_int("F017_F018_high_level", 80, min_v=60))
            gap = min(10, _cp_int("F017_F018_gap", 0, min_v=0))
            cross_up = (stoch_k14_fixed.shift(1) <= stoch_d14_fixed.shift(1)) & (stoch_k14_fixed >= (stoch_d14_fixed + float(gap)))
            cross_down = (stoch_k14_fixed.shift(1) >= stoch_d14_fixed.shift(1)) & (stoch_k14_fixed <= (stoch_d14_fixed - float(gap)))
            if zone_raw < 0:
                zone_ok = (stoch_k14_fixed.shift(1) <= float(low_level)) & (stoch_d14_fixed.shift(1) <= float(low_level))
            elif zone_raw > 0:
                zone_ok = (stoch_k14_fixed.shift(1) >= float(high_level)) & (stoch_d14_fixed.shift(1) >= float(high_level))
            else:
                zone_ok = pd.Series(True, index=out.index)
            is_up = cross_dir_raw >= 0.0
            out["F017_F018_STOCH14_ALLOW"] = np.where(
                (((is_up) & cross_up) | ((not is_up) & cross_down)) & zone_ok,
                1,
                0,
            ).astype("int64")

    # Structure/TA feature block (past-and-current only, leakage-safe).
    win = rolling_window
    out["roll_max_20"] = out["high"].rolling(win).max()
    out["roll_min_20"] = out["low"].rolling(win).min()
    out["support_distance"] = (out["close"] - out["roll_min_20"]) / out["close"].replace(0, np.nan)
    out["resistance_distance"] = (out["roll_max_20"] - out["close"]) / out["close"].replace(0, np.nan)
    out["range_width"] = (out["roll_max_20"] - out["roll_min_20"]).replace(0, np.nan)
    out["position_in_range"] = (out["close"] - out["roll_min_20"]) / out["range_width"]
    support_touch = ((out["low"] - out["roll_min_20"]).abs() / out["close"].replace(0, np.nan) <= threshold_fine).astype(float)
    resistance_touch = ((out["high"] - out["roll_max_20"]).abs() / out["close"].replace(0, np.nan) <= threshold_fine).astype(float)
    out["level_strength"] = (support_touch.rolling(rolling_window).mean().fillna(0.0) + resistance_touch.rolling(rolling_window).mean().fillna(0.0)) / 2.0
    if any(
        k in cp_keys
        for k in (
            "F035_distance_state",
            "F035_dist_thr_pct",
            "F036_distance_state",
            "F036_dist_thr_pct",
            "F037_level_type",
            "F037_strength_state",
            "F037_strength_thr",
        )
    ):
        level_lookback = 240
        touch_tolerance_pct = 0.10
        avg_volume_window = 20
        max_volume_score = 3.0
        fixed_support = out["low"].rolling(level_lookback, min_periods=level_lookback).min()
        fixed_resistance = out["high"].rolling(level_lookback, min_periods=level_lookback).max()
        support_abs_distance_pct = ((out["close"] / fixed_support.replace(0, np.nan)) - 1.0).abs() * 100.0
        resistance_abs_distance_pct = ((fixed_resistance / out["close"].replace(0, np.nan)) - 1.0).abs() * 100.0

        if "F035_distance_state" in cp_keys or "F035_dist_thr_pct" in cp_keys:
            distance_state_raw = _cp_float("F035_distance_state", -1.0, min_v=-1.0)
            is_far = distance_state_raw >= 0.0
            dist_thr_pct = min(3.0, _cp_float("F035_dist_thr_pct", 0.0, min_v=0.0))
            valid_support = support_abs_distance_pct.notna()
            out["F035_SUPPORTDIST_ALLOW"] = np.where(
                valid_support
                & (
                    ((is_far) & (support_abs_distance_pct >= float(dist_thr_pct)))
                    | ((not is_far) & (support_abs_distance_pct <= float(dist_thr_pct)))
                ),
                1,
                0,
            ).astype("int64")

        if "F036_distance_state" in cp_keys or "F036_dist_thr_pct" in cp_keys:
            distance_state_raw = _cp_float("F036_distance_state", -1.0, min_v=-1.0)
            is_far = distance_state_raw >= 0.0
            dist_thr_pct = min(3.0, _cp_float("F036_dist_thr_pct", 0.0, min_v=0.0))
            valid_resistance = resistance_abs_distance_pct.notna()
            out["F036_RESDIST_ALLOW"] = np.where(
                valid_resistance
                & (
                    ((is_far) & (resistance_abs_distance_pct >= float(dist_thr_pct)))
                    | ((not is_far) & (resistance_abs_distance_pct <= float(dist_thr_pct)))
                ),
                1,
                0,
            ).astype("int64")

        if any(k in cp_keys for k in ("F037_level_type", "F037_strength_state", "F037_strength_thr")):
            close_ref = out["close"].replace(0, np.nan)
            support_touch_fixed = ((out["low"] - fixed_support).abs() / close_ref <= (touch_tolerance_pct / 100.0)).astype(float)
            resistance_touch_fixed = ((out["high"] - fixed_resistance).abs() / close_ref <= (touch_tolerance_pct / 100.0)).astype(float)
            support_touch_count = support_touch_fixed.rolling(level_lookback, min_periods=1).sum().fillna(0.0)
            resistance_touch_count = resistance_touch_fixed.rolling(level_lookback, min_periods=1).sum().fillna(0.0)
            support_age = _bars_since_event(support_touch_fixed).fillna(float(level_lookback)).clip(upper=float(level_lookback))
            resistance_age = _bars_since_event(resistance_touch_fixed).fillna(float(level_lookback)).clip(upper=float(level_lookback))
            support_recency_score = (1.0 - (support_age / float(level_lookback))).clip(lower=0.0)
            resistance_recency_score = (1.0 - (resistance_age / float(level_lookback))).clip(lower=0.0)
            avg_volume = out["volume"].rolling(avg_volume_window, min_periods=avg_volume_window).mean()
            support_touch_avg_volume = (
                (out["volume"] * support_touch_fixed).rolling(level_lookback, min_periods=1).sum()
                / support_touch_count.replace(0, np.nan)
            )
            resistance_touch_avg_volume = (
                (out["volume"] * resistance_touch_fixed).rolling(level_lookback, min_periods=1).sum()
                / resistance_touch_count.replace(0, np.nan)
            )
            support_volume_score = (support_touch_avg_volume / avg_volume.replace(0, np.nan)).fillna(0.0).clip(
                upper=max_volume_score
            )
            resistance_volume_score = (resistance_touch_avg_volume / avg_volume.replace(0, np.nan)).fillna(0.0).clip(
                upper=max_volume_score
            )
            support_strength_score = support_touch_count + support_recency_score + support_volume_score
            resistance_strength_score = resistance_touch_count + resistance_recency_score + resistance_volume_score
            level_type_raw = int(round(_cp_float("F037_level_type", 3.0, min_v=1.0)))
            strength_state_raw = _cp_float("F037_strength_state", 1.0, min_v=-1.0)
            strength_thr = min(10.0, _cp_float("F037_strength_thr", 2.0, min_v=2.0))
            support_valid = fixed_support.notna()
            resistance_valid = fixed_resistance.notna()
            nearest_is_support = support_abs_distance_pct <= resistance_abs_distance_pct
            selected_score = pd.Series(np.nan, index=out.index, dtype="float64")
            selected_valid = pd.Series(False, index=out.index)
            if level_type_raw <= 1:
                selected_score = support_strength_score
                selected_valid = support_valid
            elif level_type_raw == 2:
                selected_score = resistance_strength_score
                selected_valid = resistance_valid
            else:
                selected_score = pd.Series(
                    np.where(nearest_is_support.fillna(False), support_strength_score, resistance_strength_score),
                    index=out.index,
                    dtype="float64",
                )
                selected_valid = support_valid | resistance_valid
            is_strong = strength_state_raw >= 0.0
            out["F037_LEVELSTRENGTH_ALLOW"] = np.where(
                selected_valid
                & (
                    ((is_strong) & (selected_score >= float(strength_thr)))
                    | ((not is_strong) & (selected_score <= float(strength_thr)))
                ),
                1,
                0,
            ).astype("int64")
    if "F038_zone" in cp_keys or "F038_level" in cp_keys:
        range_lookback = 240
        closed_range_high = out["high"].shift(1).rolling(range_lookback, min_periods=range_lookback).max()
        closed_range_low = out["low"].shift(1).rolling(range_lookback, min_periods=range_lookback).min()
        closed_range_size = closed_range_high - closed_range_low
        position_in_range_pct = ((out["close"].shift(1) - closed_range_low) / closed_range_size.replace(0, np.nan)) * 100.0
        zone_raw = _cp_float("F038_zone", -1.0, min_v=-1.0)
        is_high_zone = zone_raw >= 0.0
        level = min(95, _cp_int("F038_level", 5, min_v=5))
        valid_range = closed_range_size > 0.0
        out["F038_RANGEPOSE_ALLOW"] = np.where(
            valid_range
            & (
                ((not is_high_zone) & (position_in_range_pct <= float(level)))
                | ((is_high_zone) & (position_in_range_pct >= float(level)))
            ),
            1,
            0,
        ).astype("int64")
    out["breakout_up"] = (out["close"] > out["roll_max_20"].shift(1)).astype(int)
    out["breakout_down"] = (out["close"] < out["roll_min_20"].shift(1)).astype(int)
    out["breakout_flag"] = ((out["breakout_up"] == 1) | (out["breakout_down"] == 1)).astype(int)

    # False breakout and retest are defined using previous-bar breakout only (no future lookup).
    out["false_breakout_flag"] = (
        (
            (out["breakout_up"].shift(1) == 1)
            & (((out["roll_max_20"].shift(1) - out["close"]) / out["close"].replace(0, np.nan)) >= threshold_fine)
        )
        | (
            (out["breakout_down"].shift(1) == 1)
            & (((out["close"] - out["roll_min_20"].shift(1)) / out["close"].replace(0, np.nan)) >= threshold_fine)
        )
    ).astype(int)
    out["retest_flag"] = (
        ((out["breakout_up"].shift(1) == 1) & ((out["close"] - out["roll_max_20"].shift(1)).abs() / out["close"].replace(0, np.nan) <= threshold_fine))
        | ((out["breakout_down"].shift(1) == 1) & ((out["close"] - out["roll_min_20"].shift(1)).abs() / out["close"].replace(0, np.nan) <= threshold_fine))
    ).astype(int)

    # Structure proxies: swing context, BOS, CHOCH, trend channel, VWAP/fib distances.
    swing_win = max(3, return_lookback * 2)
    prev_high_max = out["high"].rolling(swing_win).max().shift(1)
    prev_low_min = out["low"].rolling(swing_win).min().shift(1)
    out["swing_high_break_flag"] = (out["high"] > prev_high_max).astype(int)
    out["swing_low_break_flag"] = (out["low"] < prev_low_min).astype(int)
    out["bos_up_flag"] = ((out["swing_high_break_flag"] == 1) & (out["ema_slope_5"] > 0)).astype(int)
    out["bos_down_flag"] = ((out["swing_low_break_flag"] == 1) & (out["ema_slope_5"] < 0)).astype(int)
    trend_sign = np.sign(out["ema_gap"]).replace(0, np.nan).ffill().fillna(0)
    out["choch_flag"] = (trend_sign != trend_sign.shift(1)).astype(int)

    channel_win = max(rolling_window, period_standard * 2)
    out["channel_high_50"] = out["high"].rolling(channel_win).max()
    out["channel_low_50"] = out["low"].rolling(channel_win).min()
    out["channel_width_50"] = (out["channel_high_50"] - out["channel_low_50"]).replace(0, np.nan)
    out["trend_channel_pos"] = (out["close"] - out["channel_low_50"]) / out["channel_width_50"]
    if any(k in cp_keys for k in ("F039_zone", "F039_level", "F039_outside_thr")):
        channel_lookback = 120
        channel_k = 2.0
        x = np.arange(channel_lookback, dtype="float64")
        n = float(channel_lookback)
        sum_x = float(x.sum())
        sum_x2 = float((x * x).sum())
        denom = (n * sum_x2) - (sum_x * sum_x)
        y = out["close"].shift(1)
        sum_y = y.rolling(channel_lookback, min_periods=channel_lookback).sum()
        sum_y2 = (y * y).rolling(channel_lookback, min_periods=channel_lookback).sum()
        sum_xy = y.rolling(channel_lookback, min_periods=channel_lookback).apply(
            lambda arr: float(np.dot(arr, x)),
            raw=True,
        )
        slope = ((n * sum_xy) - (sum_x * sum_y)) / denom
        intercept = (sum_y - (slope * sum_x)) / n
        channel_mid = intercept + (slope * (n - 1.0))
        sse = (
            sum_y2
            - (2.0 * intercept * sum_y)
            - (2.0 * slope * sum_xy)
            + (n * intercept * intercept)
            + (2.0 * intercept * slope * sum_x)
            + (slope * slope * sum_x2)
        ).clip(lower=0.0)
        residual_std = np.sqrt(sse / n)
        channel_width = residual_std * channel_k
        channel_lower = channel_mid - channel_width
        channel_upper = channel_mid + channel_width
        channel_pos_pct = ((y - channel_lower) / (channel_upper - channel_lower).replace(0, np.nan)) * 100.0
        zone = int(round(_cp_float("F039_zone", 1.0, min_v=1.0)))
        level = min(100, _cp_int("F039_level", 50, min_v=0))
        outside_thr = min(50, _cp_int("F039_outside_thr", 0, min_v=0))
        valid_channel = channel_upper > channel_lower
        if zone <= 1:
            allow_039 = channel_pos_pct <= float(level)
        elif zone == 2:
            allow_039 = channel_pos_pct >= float(level)
        elif zone == 3:
            allow_039 = channel_pos_pct >= (100.0 + float(outside_thr))
        else:
            allow_039 = channel_pos_pct <= (0.0 - float(outside_thr))
        out["F039_CHANNELPOS_ALLOW"] = np.where(valid_channel & allow_039.fillna(False), 1, 0).astype("int64")

    day_key = out["open_time_utc"].dt.strftime("%Y-%m-%d")
    typical = (out["high"] + out["low"] + out["close"]) / 3.0
    cum_tp_vol = (typical * out["volume"]).groupby(day_key).cumsum()
    cum_vol = out["volume"].groupby(day_key).cumsum().replace(0, np.nan)
    out["vwap"] = cum_tp_vol / cum_vol
    out["vwap_distance"] = (out["close"] - out["vwap"]) / out["close"].replace(0, np.nan)
    if any(k in cp_keys for k in ("F024_signal_mode", "F024_side_state", "F024_distance_state", "F024_dist_thr_pct")):
        signal_mode = int(round(_cp_float("F024_signal_mode", 1.0, min_v=1.0)))
        side_state_raw = _cp_float("F024_side_state", 1.0, min_v=-1.0)
        distance_state_raw = _cp_float("F024_distance_state", -1.0, min_v=-1.0)
        dist_thr_pct = min(5.0, _cp_float("F024_dist_thr_pct", 0.0, min_v=0.0))
        vwap_distance_pct = out["vwap_distance"].shift(1) * 100.0
        if signal_mode <= 1:
            is_above = side_state_raw >= 0.0
            allow_024 = ((is_above) & (vwap_distance_pct >= dist_thr_pct)) | (
                (not is_above) & (vwap_distance_pct <= -dist_thr_pct)
            )
        else:
            is_far = distance_state_raw >= 0.0
            abs_dist = vwap_distance_pct.abs()
            allow_024 = ((is_far) & (abs_dist >= dist_thr_pct)) | ((not is_far) & (abs_dist <= dist_thr_pct))
        out["F024_VWAPDIST_ALLOW"] = np.where(allow_024.fillna(False), 1, 0).astype("int64")
    out["delta_volume"] = out["volume"].diff(return_lookback)
    if any(k in cp_keys for k in ("F021_delta_mode", "F021_pressure", "F021_delta_thr")):
        delta_mode = int(round(_cp_float("F021_delta_mode", 2.0, min_v=1.0)))
        pressure_raw = _cp_float("F021_pressure", 1.0, min_v=-1.0)
        is_buy = pressure_raw >= 0.0
        delta_thr = min(80, _cp_int("F021_delta_thr", 5, min_v=5))
        if delta_mode <= 1:
            if {"buy_volume", "sell_volume"}.issubset(out.columns):
                buy_volume = pd.to_numeric(out["buy_volume"], errors="coerce")
                sell_volume = pd.to_numeric(out["sell_volume"], errors="coerce")
                total_side_volume = buy_volume + sell_volume
                delta_value = ((buy_volume - sell_volume) / total_side_volume.replace(0, np.nan)) * 100.0
                valid_delta = total_side_volume > 0.0
            else:
                delta_value = pd.Series(np.nan, index=out.index)
                valid_delta = pd.Series(False, index=out.index)
        else:
            candle_range = out["high"] - out["low"]
            delta_value = ((out["close"] - out["open"]) / candle_range.replace(0, np.nan)) * 100.0
            valid_delta = candle_range > 0.0
        out["F021_DELTAVOL_ALLOW"] = np.where(
            valid_delta & (((is_buy) & (delta_value >= float(delta_thr))) | ((not is_buy) & (delta_value <= -float(delta_thr)))),
            1,
            0,
        ).astype("int64")
    out["obv"] = (np.sign(out["close"].diff(1)).fillna(0.0) * out["volume"]).cumsum()
    out["obv_slope_5"] = out["obv"].pct_change(return_lookback)
    if "F022_slope_dir" in cp_keys or "F022_slope_thr" in cp_keys:
        slope_raw = _cp_float("F022_slope_dir", 1.0, min_v=-1.0)
        is_up = slope_raw >= 0.0
        slope_thr = min(10.0, _cp_float("F022_slope_thr", 0.0, min_v=0.0))
        avg_volume_20 = out["volume"].rolling(20).mean()
        obv_slope_5_norm = (out["obv"] - out["obv"].shift(5)) / avg_volume_20.replace(0, np.nan)
        valid_obv_slope = avg_volume_20 > 0.0
        out["F022_OBVSLOPE5_ALLOW"] = np.where(
            valid_obv_slope
            & (((is_up) & (obv_slope_5_norm >= slope_thr)) | ((not is_up) & (obv_slope_5_norm <= -slope_thr))),
            1,
            0,
        ).astype("int64")

    mf = typical * out["volume"]
    tp_diff = typical.diff()
    pos_mf = pd.Series(np.where(tp_diff > 0, mf, 0.0), index=out.index)
    neg_mf = pd.Series(np.where(tp_diff < 0, mf, 0.0), index=out.index)
    pos14 = pos_mf.rolling(period_standard).sum()
    neg14 = neg_mf.rolling(period_standard).sum()
    mfr = pos14 / neg14.replace(0, np.nan)
    mfi = 100.0 - (100.0 / (1.0 + mfr))
    mfi = mfi.where(~((neg14 == 0) & (pos14 > 0)), 100.0)
    mfi = mfi.where(~((pos14 == 0) & (neg14 > 0)), 0.0)
    mfi = mfi.where(~((pos14 == 0) & (neg14 == 0)), 50.0)
    out["mfi14"] = mfi
    if any(k in cp_keys for k in ("F023_signal_mode", "F023_cmp", "F023_level", "F023_cross_dir", "F023_cross_level")):
        signal_mode = int(round(_cp_float("F023_signal_mode", 1.0, min_v=1.0)))
        if signal_mode <= 1:
            cmp_raw = _cp_float("F023_cmp", 1.0, min_v=-1.0)
            is_greater = cmp_raw >= 0.0
            level = min(90, _cp_int("F023_level", 50, min_v=10))
            out["F023_MFI14_ALLOW"] = np.where(
                ((is_greater) & (mfi >= float(level))) | ((not is_greater) & (mfi <= float(level))),
                1,
                0,
            ).astype("int64")
        else:
            cross_dir_raw = _cp_float("F023_cross_dir", 1.0, min_v=-1.0)
            is_up = cross_dir_raw >= 0.0
            cross_level = min(90, _cp_int("F023_cross_level", 50, min_v=10))
            cross_up = (mfi.shift(1) < float(cross_level)) & (mfi >= float(cross_level))
            cross_down = (mfi.shift(1) > float(cross_level)) & (mfi <= float(cross_level))
            out["F023_MFI14_ALLOW"] = np.where(
                ((is_up) & cross_up) | ((not is_up) & cross_down),
                1,
                0,
            ).astype("int64")

    fib_high = out["high"].rolling(fib_window).max()
    fib_low = out["low"].rolling(fib_window).min()
    fib_range = (fib_high - fib_low).replace(0, np.nan)
    fib_pair_level = 1.0 - fib_level if 0.0 <= fib_level <= 1.0 else fib_level
    fib_0382 = fib_low + fib_range * fib_level
    fib_0618 = fib_low + fib_range * fib_pair_level
    out["fib_0382_distance"] = (out["close"] - fib_0382) / out["close"].replace(0, np.nan)
    out["fib_0618_distance"] = (out["close"] - fib_0618) / out["close"].replace(0, np.nan)
    if any(
        k in cp_keys
        for k in (
            "F040_signal_mode",
            "F040_side_state",
            "F040_distance_state",
            "F040_dist_thr_pct",
            "F041_signal_mode",
            "F041_side_state",
            "F041_distance_state",
            "F041_dist_thr_pct",
        )
    ):
        fib_grid = _confirmed_fib_anchor_grid_features(
            out["high"],
            out["low"],
            out["close"],
            max_lookback_bars=240,
            depth_bars=10,
            deviation_pct=0.30,
        )
        for col in (
            "fib_0000",
            "fib_0236",
            "fib_0382",
            "fib_0500",
            "fib_0618",
            "fib_0786",
            "fib_1000",
            "fib_direction",
            "anchor_a_price",
            "anchor_b_price",
            "anchor_a_bar",
            "anchor_b_bar",
        ):
            out[col] = fib_grid[col]

        for spec in (
            ("F040", "fib_0382_distance_pct", "F040_FIB0382DIST_ALLOW"),
            ("F041", "fib_0618_distance_pct", "F041_FIB0618DIST_ALLOW"),
        ):
            prefix, distance_key, allow_col = spec
            if not any(
                k in cp_keys
                for k in (
                    f"{prefix}_signal_mode",
                    f"{prefix}_side_state",
                    f"{prefix}_distance_state",
                    f"{prefix}_dist_thr_pct",
                )
            ):
                continue
            distance_pct = fib_grid[distance_key]
            abs_distance_pct = distance_pct.abs()
            signal_mode = int(round(_cp_float(f"{prefix}_signal_mode", 2.0, min_v=1.0)))
            side_state_raw = _cp_float(f"{prefix}_side_state", 1.0, min_v=-1.0)
            distance_state_raw = _cp_float(f"{prefix}_distance_state", -1.0, min_v=-1.0)
            dist_thr_pct = min(3.0, _cp_float(f"{prefix}_dist_thr_pct", 0.0, min_v=0.0))
            valid_fib = distance_pct.notna()
            if signal_mode <= 1:
                is_above = side_state_raw >= 0.0
                allow = valid_fib & (
                    ((is_above) & (distance_pct >= float(dist_thr_pct)))
                    | ((not is_above) & (distance_pct <= -float(dist_thr_pct)))
                )
            else:
                is_far = distance_state_raw >= 0.0
                allow = valid_fib & (
                    ((is_far) & (abs_distance_pct >= float(dist_thr_pct)))
                    | ((not is_far) & (abs_distance_pct <= float(dist_thr_pct)))
                )
            out[allow_col] = np.where(allow, 1, 0).astype("int64")
    out["tp_context_distance"] = out["resistance_distance"]
    out["sl_context_distance"] = out["support_distance"]
    out["rr_context_estimate"] = out["tp_context_distance"] / out["sl_context_distance"].replace(0, np.nan)

    # Pattern block: candle signals plus classic figure proxies, all past/current only.
    body = (out["close"] - out["open"]).abs()
    rng = (out["high"] - out["low"]).replace(0, np.nan)
    upper_wick = out["high"] - out[["open", "close"]].max(axis=1)
    lower_wick = out[["open", "close"]].min(axis=1) - out["low"]
    out["doji_flag"] = ((body / rng) <= doji_threshold).astype(int)
    out["inside_bar_flag"] = ((out["high"] <= out["high"].shift(1)) & (out["low"] >= out["low"].shift(1))).astype(int)
    out["pin_bar_bull_flag"] = (
        (lower_wick > body * ratio_pattern) & (upper_wick <= body * ratio_opposite_wick_cap)
    ).astype(int)
    out["pin_bar_bear_flag"] = (
        (upper_wick > body * ratio_pattern) & (lower_wick <= body * ratio_opposite_wick_cap)
    ).astype(int)
    out["hammer_flag"] = ((lower_wick > body * ratio_pattern) & (upper_wick <= body * ratio_opposite_wick_cap)).astype(int)
    out["shooting_star_flag"] = ((upper_wick > body * ratio_pattern) & (lower_wick <= body * ratio_opposite_wick_cap)).astype(int)
    prev_open = out["open"].shift(1)
    prev_close2 = out["close"].shift(1)
    prev_body_low = np.minimum(prev_open, prev_close2)
    prev_body_high = np.maximum(prev_open, prev_close2)
    cur_body_low = np.minimum(out["open"], out["close"])
    cur_body_high = np.maximum(out["open"], out["close"])
    out["engulf_bull_flag"] = (
        (prev_close2 < prev_open)
        & (out["close"] > out["open"])
        & (cur_body_low <= prev_body_low)
        & (cur_body_high >= prev_body_high)
    ).astype(int)
    out["engulf_bear_flag"] = (
        (prev_close2 > prev_open)
        & (out["close"] < out["open"])
        & (cur_body_low <= prev_body_low)
        & (cur_body_high >= prev_body_high)
    ).astype(int)

    pwin = max(5, pattern_window)
    seg = max(2, pwin // 3)
    slope_span = max(2, pwin // 4)
    close_ref = out["close"].replace(0, np.nan)
    support_touch_count = support_touch.rolling(pwin).sum().fillna(0.0)
    resistance_touch_count = resistance_touch.rolling(pwin).sum().fillna(0.0)
    near_support = (out["support_distance"].abs() <= level_distance_threshold).fillna(False)
    near_resistance = (out["resistance_distance"].abs() <= level_distance_threshold).fillna(False)
    out["double_bottom_flag"] = ((support_touch_count >= min_touches) & near_support).astype(int)
    out["double_top_flag"] = ((resistance_touch_count >= min_touches) & near_resistance).astype(int)

    left_high = out["high"].shift(2 * seg).rolling(seg).max()
    head_high = out["high"].shift(seg).rolling(seg).max()
    right_high = out["high"].rolling(seg).max()
    shoulders_close = ((left_high - right_high).abs() / close_ref <= level_distance_threshold).fillna(False)
    out["head_shoulders_flag"] = (
        (head_high > left_high * (1.0 + breakout_threshold))
        & (head_high > right_high * (1.0 + breakout_threshold))
        & shoulders_close
    ).astype(int)

    left_low = out["low"].shift(2 * seg).rolling(seg).min()
    head_low = out["low"].shift(seg).rolling(seg).min()
    right_low = out["low"].rolling(seg).min()
    inv_shoulders_close = ((left_low - right_low).abs() / close_ref <= level_distance_threshold).fillna(False)
    out["inverse_head_shoulders_flag"] = (
        (head_low < left_low * (1.0 - breakout_threshold))
        & (head_low < right_low * (1.0 - breakout_threshold))
        & inv_shoulders_close
    ).astype(int)

    range_prev = out["range_width"].shift(max(1, pwin // 2))
    narrowing = (out["range_width"] < range_prev * (1.0 - breakout_threshold)).fillna(False)
    high_slope = out["high"].rolling(seg).mean().diff(slope_span) / close_ref
    low_slope = out["low"].rolling(seg).mean().diff(slope_span) / close_ref
    impulse = out["close"].pct_change(max(2, pwin // 2)).abs() >= breakout_threshold
    out["triangle_flag"] = narrowing.astype(int)
    out["pennant_flag"] = (narrowing & impulse.fillna(False)).astype(int)
    out["wedge_rising_flag"] = (narrowing & (high_slope > 0) & (low_slope > 0) & (low_slope >= high_slope)).astype(int)
    out["wedge_falling_flag"] = (narrowing & (high_slope < 0) & (low_slope < 0) & (low_slope <= high_slope)).astype(int)
    out["range_flag"] = ((support_touch_count >= min_touches) & (resistance_touch_count >= min_touches)).astype(int)

    recent_retest = out["retest_flag"].rolling(retest_window).max().fillna(0.0) > 0
    breakout_up_confirm = (out["close"] > out["roll_max_20"].shift(1) * (1.0 + breakout_threshold)).fillna(False)
    breakout_down_confirm = (out["close"] < out["roll_min_20"].shift(1) * (1.0 - breakout_threshold)).fillna(False)
    volume_confirm = (out["vol_z"] >= volume_confirm_threshold).fillna(False)
    level_confirm_long = (near_support | recent_retest | breakout_up_confirm).fillna(False)
    level_confirm_short = (near_resistance | recent_retest | breakout_down_confirm).fillna(False)
    bullish_figure = (
        (out["double_bottom_flag"] == 1)
        | (out["inverse_head_shoulders_flag"] == 1)
        | (out["wedge_falling_flag"] == 1)
        | (out["pennant_flag"] == 1)
    )
    bearish_figure = (
        (out["double_top_flag"] == 1)
        | (out["head_shoulders_flag"] == 1)
        | (out["wedge_rising_flag"] == 1)
        | (out["pennant_flag"] == 1)
    )
    out["pattern_volume_confirm_flag"] = volume_confirm.astype(int)
    out["pattern_level_confirm_flag"] = (level_confirm_long | level_confirm_short).astype(int)
    out["pattern_structure_volume_entry_long"] = (bullish_figure & level_confirm_long & volume_confirm).astype(int)
    out["pattern_structure_volume_entry_short"] = (bearish_figure & level_confirm_short & volume_confirm).astype(int)
    out["pattern_sl_buffer_distance"] = out["sl_context_distance"] + (out["atr14"].fillna(0.0) * sl_buffer)
    out["pattern_tp_ladder_score"] = out["rr_context_estimate"].clip(lower=0.0, upper=float(tp_ladder))

    out["pattern_strength"] = (
        out["doji_flag"]
        + out["inside_bar_flag"]
        + out["pin_bar_bull_flag"]
        + out["pin_bar_bear_flag"]
        + out["hammer_flag"]
        + out["shooting_star_flag"]
        + out["engulf_bull_flag"]
        + out["engulf_bear_flag"]
        + out["double_bottom_flag"]
        + out["double_top_flag"]
        + out["head_shoulders_flag"]
        + out["inverse_head_shoulders_flag"]
        + out["triangle_flag"]
        + out["pennant_flag"]
        + out["wedge_rising_flag"]
        + out["wedge_falling_flag"]
        + out["range_flag"]
        + out["pattern_structure_volume_entry_long"]
        + out["pattern_structure_volume_entry_short"]
    )
    pattern_any = (out["pattern_strength"] > 0).astype(int)
    out["pattern_age_bars"] = _bars_since_event(pattern_any).fillna(float(pattern_age_cap)).clip(upper=float(pattern_age_cap))

    out["rsi_bull_div_flag"] = ((out["close"] < out["close"].shift(div_lookback)) & (out["rsi14"] > out["rsi14"].shift(div_lookback))).astype(int)
    out["rsi_bear_div_flag"] = ((out["close"] > out["close"].shift(div_lookback)) & (out["rsi14"] < out["rsi14"].shift(div_lookback))).astype(int)
    out["macd_bull_div_flag"] = ((out["close"] < out["close"].shift(div_lookback)) & (out["macd_hist"] > out["macd_hist"].shift(div_lookback))).astype(int)
    out["macd_bear_div_flag"] = ((out["close"] > out["close"].shift(div_lookback)) & (out["macd_hist"] < out["macd_hist"].shift(div_lookback))).astype(int)
    out["obv_bull_div_flag"] = ((out["close"] < out["close"].shift(div_lookback)) & (out["obv"] > out["obv"].shift(div_lookback))).astype(int)
    out["obv_bear_div_flag"] = ((out["close"] > out["close"].shift(div_lookback)) & (out["obv"] < out["obv"].shift(div_lookback))).astype(int)

    # Price-density features (HVN/LVN proxies from rolling volume-at-price).
    d60 = _rolling_density_profile_features(
        out["close"],
        out["volume"],
        window=density_window_short,
        bin_pct=density_bin_pct,
    )
    out["density_vpoc_distance_60"] = d60[0]
    out["density_bin_share_60"] = d60[1]
    out["density_cluster_share_60"] = d60[2]
    out["density_vpoc_share_60"] = d60[3]

    d240 = _rolling_density_profile_features(
        out["close"],
        out["volume"],
        window=density_window_long,
        bin_pct=density_bin_pct,
    )
    out["density_vpoc_distance_240"] = d240[0]
    out["density_bin_share_240"] = d240[1]
    out["density_cluster_share_240"] = d240[2]
    out["density_vpoc_share_240"] = d240[3]

    out["density_vpoc_drift_20"] = out["density_vpoc_distance_60"].diff(max(2, div_lookback))
    out["density_cluster_ratio_60_240"] = out["density_cluster_share_60"] / out["density_cluster_share_240"].replace(0, np.nan)
    density_vpoc_distance_60_pct = (
        out["density_vpoc_distance_60"] / (1.0 - out["density_vpoc_distance_60"]).replace(0, np.nan)
    ) * 100.0
    density_vpoc_distance_240_pct = (
        out["density_vpoc_distance_240"] / (1.0 - out["density_vpoc_distance_240"]).replace(0, np.nan)
    ) * 100.0
    if any(k in cp_keys for k in ("F025_signal_mode", "F025_side_state", "F025_distance_state", "F025_dist_thr_pct")):
        signal_mode = int(round(_cp_float("F025_signal_mode", 1.0, min_v=1.0)))
        side_state_raw = _cp_float("F025_side_state", 1.0, min_v=-1.0)
        distance_state_raw = _cp_float("F025_distance_state", -1.0, min_v=-1.0)
        dist_thr_pct = min(3.0, _cp_float("F025_dist_thr_pct", 0.0, min_v=0.0))
        if signal_mode <= 1:
            is_above = side_state_raw >= 0.0
            allow_025 = ((is_above) & (density_vpoc_distance_60_pct >= dist_thr_pct)) | (
                (not is_above) & (density_vpoc_distance_60_pct <= -dist_thr_pct)
            )
        else:
            is_far = distance_state_raw >= 0.0
            abs_dist = density_vpoc_distance_60_pct.abs()
            allow_025 = ((is_far) & (abs_dist >= dist_thr_pct)) | ((not is_far) & (abs_dist <= dist_thr_pct))
        out["F025_VPOCDIST60_ALLOW"] = np.where(allow_025.fillna(False), 1, 0).astype("int64")
    if "F026_cmp" in cp_keys or "F026_share_thr_pct" in cp_keys:
        cmp_raw = _cp_float("F026_cmp", 1.0, min_v=-1.0)
        is_greater = cmp_raw >= 0.0
        share_thr_pct = min(40.0, _cp_float("F026_share_thr_pct", 1.0, min_v=1.0))
        bin_share_60 = out["density_bin_share_60"].shift(1)
        out["F026_BINSHARE60_ALLOW"] = np.where(
            ((is_greater) & (bin_share_60 >= share_thr_pct)) | ((not is_greater) & (bin_share_60 <= share_thr_pct)),
            1,
            0,
        ).astype("int64")
    if "F027_cmp" in cp_keys or "F027_share_thr_pct" in cp_keys:
        cmp_raw = _cp_float("F027_cmp", 1.0, min_v=-1.0)
        is_greater = cmp_raw >= 0.0
        share_thr_pct = min(70.0, _cp_float("F027_share_thr_pct", 2.0, min_v=2.0))
        cluster_share_60 = out["density_cluster_share_60"].shift(1)
        out["F027_CLUSTERSHARE60_ALLOW"] = np.where(
            ((is_greater) & (cluster_share_60 >= share_thr_pct)) | ((not is_greater) & (cluster_share_60 <= share_thr_pct)),
            1,
            0,
        ).astype("int64")
    if "F028_cmp" in cp_keys or "F028_share_thr_pct" in cp_keys:
        cmp_raw = _cp_float("F028_cmp", 1.0, min_v=-1.0)
        is_greater = cmp_raw >= 0.0
        share_thr_pct = min(50.0, _cp_float("F028_share_thr_pct", 1.0, min_v=1.0))
        vpoc_share_60 = out["density_vpoc_share_60"].shift(1)
        out["F028_VPOCSHARE60_ALLOW"] = np.where(
            ((is_greater) & (vpoc_share_60 >= share_thr_pct)) | ((not is_greater) & (vpoc_share_60 <= share_thr_pct)),
            1,
            0,
        ).astype("int64")
    if any(k in cp_keys for k in ("F029_signal_mode", "F029_side_state", "F029_distance_state", "F029_dist_thr_pct")):
        signal_mode = int(round(_cp_float("F029_signal_mode", 1.0, min_v=1.0)))
        side_state_raw = _cp_float("F029_side_state", 1.0, min_v=-1.0)
        distance_state_raw = _cp_float("F029_distance_state", -1.0, min_v=-1.0)
        dist_thr_pct = min(5.0, _cp_float("F029_dist_thr_pct", 0.0, min_v=0.0))
        if signal_mode <= 1:
            is_above = side_state_raw >= 0.0
            allow_029 = ((is_above) & (density_vpoc_distance_240_pct >= dist_thr_pct)) | (
                (not is_above) & (density_vpoc_distance_240_pct <= -dist_thr_pct)
            )
        else:
            is_far = distance_state_raw >= 0.0
            abs_dist = density_vpoc_distance_240_pct.abs()
            allow_029 = ((is_far) & (abs_dist >= dist_thr_pct)) | ((not is_far) & (abs_dist <= dist_thr_pct))
        out["F029_VPOCDIST240_ALLOW"] = np.where(allow_029.fillna(False), 1, 0).astype("int64")
    if "F030_cmp" in cp_keys or "F030_share_thr_pct" in cp_keys:
        cmp_raw = _cp_float("F030_cmp", 1.0, min_v=-1.0)
        is_greater = cmp_raw >= 0.0
        share_thr_pct = min(25.0, _cp_float("F030_share_thr_pct", 0.5, min_v=0.5))
        bin_share_240 = out["density_bin_share_240"].shift(1)
        out["F030_BINSHARE240_ALLOW"] = np.where(
            ((is_greater) & (bin_share_240 >= share_thr_pct)) | ((not is_greater) & (bin_share_240 <= share_thr_pct)),
            1,
            0,
        ).astype("int64")
    if "F031_cmp" in cp_keys or "F031_share_thr_pct" in cp_keys:
        cmp_raw = _cp_float("F031_cmp", 1.0, min_v=-1.0)
        is_greater = cmp_raw >= 0.0
        share_thr_pct = min(60.0, _cp_float("F031_share_thr_pct", 1.0, min_v=1.0))
        cluster_share_240 = out["density_cluster_share_240"].shift(1)
        out["F031_CLUSTERSHARE240_ALLOW"] = np.where(
            ((is_greater) & (cluster_share_240 >= share_thr_pct))
            | ((not is_greater) & (cluster_share_240 <= share_thr_pct)),
            1,
            0,
        ).astype("int64")
    if "F032_cmp" in cp_keys or "F032_share_thr_pct" in cp_keys:
        cmp_raw = _cp_float("F032_cmp", 1.0, min_v=-1.0)
        is_greater = cmp_raw >= 0.0
        share_thr_pct = min(35.0, _cp_float("F032_share_thr_pct", 0.5, min_v=0.5))
        vpoc_share_240 = out["density_vpoc_share_240"].shift(1)
        out["F032_VPOCSHARE240_ALLOW"] = np.where(
            ((is_greater) & (vpoc_share_240 >= share_thr_pct)) | ((not is_greater) & (vpoc_share_240 <= share_thr_pct)),
            1,
            0,
        ).astype("int64")
    if "F033_drift_dir" in cp_keys or "F033_drift_thr_pct" in cp_keys:
        drift_dir_raw = _cp_float("F033_drift_dir", 1.0, min_v=-1.0)
        is_up = drift_dir_raw >= 0.0
        drift_thr_pct = min(2.0, _cp_float("F033_drift_thr_pct", 0.0, min_v=0.0))
        vpoc_60_price = out["close"] * (1.0 - out["density_vpoc_distance_60"])
        vpoc_drift_20_pct = (vpoc_60_price / vpoc_60_price.shift(20).replace(0, np.nan) - 1.0) * 100.0
        out["F033_VPOCDRIFT20_ALLOW"] = np.where(
            ((is_up) & (vpoc_drift_20_pct >= drift_thr_pct)) | ((not is_up) & (vpoc_drift_20_pct <= -drift_thr_pct)),
            1,
            0,
        ).astype("int64")
    if "F034_cmp" in cp_keys or "F034_ratio_level" in cp_keys:
        cmp_raw = _cp_float("F034_cmp", 1.0, min_v=-1.0)
        is_greater = cmp_raw >= 0.0
        ratio_level = min(2.50, _cp_float("F034_ratio_level", 1.0, min_v=0.50))
        ratio_valid = out["density_cluster_share_240"] > 0.0
        out["F034_CLUSTERRATIO_ALLOW"] = np.where(
            ratio_valid
            & (
                ((is_greater) & (out["density_cluster_ratio_60_240"] >= ratio_level))
                | ((not is_greater) & (out["density_cluster_ratio_60_240"] <= ratio_level))
            ),
            1,
            0,
        ).astype("int64")

    breakout_retest_keys = (
        "F045_level_source_mode",
        "F045_break_dir",
        "F045_break_buffer_pct",
        "F045_confirm_bars",
        "F046_level_source_mode",
        "F046_break_dir",
        "F046_false_mode",
        "F046_break_buffer_pct",
        "F046_return_window_bars",
        "F046_return_tolerance_pct",
        "F047_level_source_mode",
        "F047_break_dir",
        "F047_retest_window_bars",
        "F047_retest_tolerance_pct",
        "F047_reaction_confirm_pct",
        "F048_break_buffer_pct",
        "F048_confirm_bars",
        "F049_break_buffer_pct",
        "F049_confirm_bars",
    )
    if any(k in cp_keys for k in breakout_retest_keys):
        swing_levels = _confirmed_swing_levels(
            out["high"],
            out["low"],
            lookback_bars=240,
            pivot_left=3,
            pivot_right=3,
        )
        last_swing_high = swing_levels["last_swing_high"]
        last_swing_low = swing_levels["last_swing_low"]

        def _br_level_source_mode(prefix: str) -> int:
            raw = int(round(_cp_float(f"{prefix}_level_source_mode", 1.0, min_v=1.0)))
            return min(3, max(1, raw))

        break_level_cache: dict[int, dict[str, pd.Series]] = {}

        def _break_levels_for_mode(mode_id: int) -> dict[str, pd.Series]:
            if mode_id in break_level_cache:
                return break_level_cache[mode_id]
            if mode_id == 1:
                levels = [last_swing_low, last_swing_high]
            elif mode_id == 2:
                levels = [
                    out["close"] * (1.0 - out["density_vpoc_distance_60"]),
                    out["close"] * (1.0 - out["density_vpoc_distance_240"]),
                ]
            else:
                if "fib_0236" not in out.columns:
                    fib_grid_br = _confirmed_fib_anchor_grid_features(
                        out["high"],
                        out["low"],
                        out["close"],
                        max_lookback_bars=240,
                        depth_bars=10,
                        deviation_pct=0.30,
                    )
                    for col in ("fib_0236", "fib_0382", "fib_0500", "fib_0618", "fib_0786"):
                        out[col] = fib_grid_br[col]
                levels = [out[col] for col in ("fib_0236", "fib_0382", "fib_0500", "fib_0618", "fib_0786")]
            break_level_cache[mode_id] = _nearest_break_levels(out["close"].shift(2), levels)
            return break_level_cache[mode_id]

        def _confirmed_closes(level: pd.Series, *, is_up: bool, buffer_pct: float, bars: int) -> pd.Series:
            threshold = level * (1.0 + float(buffer_pct) / 100.0) if is_up else level * (1.0 - float(buffer_pct) / 100.0)
            allow = pd.Series(True, index=out.index)
            for offset in range(1, max(1, int(bars)) + 1):
                shifted_close = out["close"].shift(offset)
                if is_up:
                    allow &= shifted_close >= threshold
                else:
                    allow &= shifted_close <= threshold
            return allow & level.notna() & (level > 0.0)

        def _internal_breakout_memory(
            *,
            mode_id: int,
            is_up: bool,
            window_bars: int,
        ) -> tuple[pd.Series, pd.Series]:
            levels = _break_levels_for_mode(mode_id)
            target = levels["up"] if is_up else levels["down"]
            event = _confirmed_closes(target, is_up=is_up, buffer_pct=0.0, bars=1)
            level_arr = target.to_numpy(dtype=float)
            event_arr = event.fillna(False).to_numpy(dtype=bool)
            n = len(out)
            mem_level = np.full(n, np.nan, dtype=float)
            mem_age = np.full(n, np.nan, dtype=float)
            max_window = max(1, int(window_bars))
            last_event = -10**9
            last_level = np.nan
            for i in range(n):
                prev = i - 1
                if prev >= 0 and event_arr[prev] and np.isfinite(level_arr[prev]) and level_arr[prev] > 0.0:
                    last_event = prev
                    last_level = level_arr[prev]
                age = i - last_event
                if age <= max_window and np.isfinite(last_level) and last_level > 0.0:
                    mem_level[i] = last_level
                    mem_age[i] = float(age)
            return pd.Series(mem_level, index=out.index), pd.Series(mem_age, index=out.index)

        if "F048_break_buffer_pct" in cp_keys or "F048_confirm_bars" in cp_keys:
            buffer_pct = min(1.0, _cp_float("F048_break_buffer_pct", 0.0, min_v=0.0))
            confirm_bars = min(3, _cp_int("F048_confirm_bars", 1, min_v=1))
            allow = _confirmed_closes(last_swing_high, is_up=True, buffer_pct=buffer_pct, bars=confirm_bars)
            out["F048_SWINGHIGHBREAK_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if "F049_break_buffer_pct" in cp_keys or "F049_confirm_bars" in cp_keys:
            buffer_pct = min(1.0, _cp_float("F049_break_buffer_pct", 0.0, min_v=0.0))
            confirm_bars = min(3, _cp_int("F049_confirm_bars", 1, min_v=1))
            allow = _confirmed_closes(last_swing_low, is_up=False, buffer_pct=buffer_pct, bars=confirm_bars)
            out["F049_SWINGLOWBREAK_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(k in cp_keys for k in ("F045_level_source_mode", "F045_break_dir", "F045_break_buffer_pct", "F045_confirm_bars")):
            mode_id = _br_level_source_mode("F045")
            break_dir_raw = _cp_float("F045_break_dir", 1.0, min_v=-1.0)
            is_up = break_dir_raw >= 0.0
            buffer_pct = min(1.0, _cp_float("F045_break_buffer_pct", 0.0, min_v=0.0))
            confirm_bars = min(3, _cp_int("F045_confirm_bars", 1, min_v=1))
            levels = _break_levels_for_mode(mode_id)
            target = levels["up"] if is_up else levels["down"]
            allow = _confirmed_closes(target, is_up=is_up, buffer_pct=buffer_pct, bars=confirm_bars)
            out["F045_BREAKOUT_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(
            k in cp_keys
            for k in (
                "F046_level_source_mode",
                "F046_break_dir",
                "F046_false_mode",
                "F046_break_buffer_pct",
                "F046_return_window_bars",
                "F046_return_tolerance_pct",
            )
        ):
            mode_id = _br_level_source_mode("F046")
            break_dir_raw = _cp_float("F046_break_dir", 1.0, min_v=-1.0)
            is_up = break_dir_raw >= 0.0
            false_mode = int(round(_cp_float("F046_false_mode", 1.0, min_v=1.0)))
            buffer_pct = min(1.0, _cp_float("F046_break_buffer_pct", 0.0, min_v=0.0))
            return_window = min(10, _cp_int("F046_return_window_bars", 1, min_v=1))
            tolerance_pct = min(0.30, _cp_float("F046_return_tolerance_pct", 0.0, min_v=0.0))
            levels = _break_levels_for_mode(mode_id)
            target = levels["up"] if is_up else levels["down"]
            if is_up:
                wick_reject = (out["high"].shift(1) >= target * (1.0 + buffer_pct / 100.0)) & (
                    out["close"].shift(1) <= target * (1.0 + tolerance_pct / 100.0)
                )
            else:
                wick_reject = (out["low"].shift(1) <= target * (1.0 - buffer_pct / 100.0)) & (
                    out["close"].shift(1) >= target * (1.0 - tolerance_pct / 100.0)
                )
            close_return_event = pd.Series(False, index=out.index)
            for offset in range(2, return_window + 2):
                shifted_close = out["close"].shift(offset)
                if is_up:
                    close_return_event |= shifted_close >= target * (1.0 + buffer_pct / 100.0)
                else:
                    close_return_event |= shifted_close <= target * (1.0 - buffer_pct / 100.0)
            if is_up:
                close_return = close_return_event & (out["close"].shift(1) <= target * (1.0 + tolerance_pct / 100.0))
            else:
                close_return = close_return_event & (out["close"].shift(1) >= target * (1.0 - tolerance_pct / 100.0))
            allow = (wick_reject if false_mode <= 1 else close_return) & target.notna() & (target > 0.0)
            out["F046_FALSEBREAK_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(
            k in cp_keys
            for k in (
                "F047_level_source_mode",
                "F047_break_dir",
                "F047_retest_window_bars",
                "F047_retest_tolerance_pct",
                "F047_reaction_confirm_pct",
            )
        ):
            mode_id = _br_level_source_mode("F047")
            break_dir_raw = _cp_float("F047_break_dir", 1.0, min_v=-1.0)
            is_up = break_dir_raw >= 0.0
            retest_window_bars = min(30, _cp_int("F047_retest_window_bars", 1, min_v=1))
            retest_tol_pct = min(0.50, _cp_float("F047_retest_tolerance_pct", 0.0, min_v=0.0))
            reaction_pct = min(1.0, _cp_float("F047_reaction_confirm_pct", 0.0, min_v=0.0))
            broken_level, _broken_age = _internal_breakout_memory(
                mode_id=mode_id,
                is_up=is_up,
                window_bars=retest_window_bars,
            )
            if is_up:
                allow = (out["low"].shift(1) <= broken_level * (1.0 + retest_tol_pct / 100.0)) & (
                    out["close"].shift(1) >= broken_level * (1.0 + reaction_pct / 100.0)
                )
            else:
                allow = (out["high"].shift(1) >= broken_level * (1.0 - retest_tol_pct / 100.0)) & (
                    out["close"].shift(1) <= broken_level * (1.0 - reaction_pct / 100.0)
                )
            allow = allow & broken_level.notna() & (broken_level > 0.0)
            out["F047_RETEST_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

    market_structure_keys = (
        "F050_structure_scope",
        "F050_break_buffer_pct",
        "F050_confirm_bars",
        "F050_require_bias",
        "F051_structure_scope",
        "F051_break_buffer_pct",
        "F051_confirm_bars",
        "F051_require_bias",
        "F052_structure_scope",
        "F052_choch_dir",
        "F052_break_buffer_pct",
        "F052_confirm_bars",
        "F052_require_opposite_bias",
    )
    if any(k in cp_keys for k in market_structure_keys):
        ms_cache: dict[int, dict[str, pd.Series]] = {}

        def _ms_scope(prefix: str) -> int:
            raw = int(round(_cp_float(f"{prefix}_structure_scope", 1.0, min_v=1.0)))
            return 2 if raw >= 2 else 1

        def _ms_state(scope_id: int) -> dict[str, pd.Series]:
            if scope_id in ms_cache:
                return ms_cache[scope_id]
            if scope_id == 2:
                state = _confirmed_market_structure_state(
                    out["high"],
                    out["low"],
                    lookback_bars=240,
                    pivot_left=10,
                    pivot_right=10,
                    min_swing_pct=0.30,
                )
            else:
                state = _confirmed_market_structure_state(
                    out["high"],
                    out["low"],
                    lookback_bars=120,
                    pivot_left=3,
                    pivot_right=3,
                    min_swing_pct=0.15,
                )
            ms_cache[scope_id] = state
            return state

        def _ms_confirmed_closes(level: pd.Series, *, is_up: bool, buffer_pct: float, bars: int) -> pd.Series:
            threshold = level * (1.0 + float(buffer_pct) / 100.0) if is_up else level * (1.0 - float(buffer_pct) / 100.0)
            allow = pd.Series(True, index=out.index)
            for offset in range(1, max(1, int(bars)) + 1):
                shifted_close = out["close"].shift(offset)
                if is_up:
                    allow &= shifted_close >= threshold
                else:
                    allow &= shifted_close <= threshold
            return allow & level.notna() & (level > 0.0)

        if any(k in cp_keys for k in ("F050_structure_scope", "F050_break_buffer_pct", "F050_confirm_bars", "F050_require_bias")):
            state = _ms_state(_ms_scope("F050"))
            buffer_pct = min(1.0, _cp_float("F050_break_buffer_pct", 0.0, min_v=0.0))
            confirm_bars = min(3, _cp_int("F050_confirm_bars", 1, min_v=1))
            require_bias = int(round(_cp_float("F050_require_bias", 1.0, min_v=1.0)))
            bias = state["structure_bias"].shift(1).fillna(0.0)
            bias_allow = bias > 0.0 if require_bias <= 1 else bias >= 0.0
            allow = _ms_confirmed_closes(
                state["last_structure_high"],
                is_up=True,
                buffer_pct=buffer_pct,
                bars=confirm_bars,
            ) & bias_allow
            out["F050_BOSUP_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(k in cp_keys for k in ("F051_structure_scope", "F051_break_buffer_pct", "F051_confirm_bars", "F051_require_bias")):
            state = _ms_state(_ms_scope("F051"))
            buffer_pct = min(1.0, _cp_float("F051_break_buffer_pct", 0.0, min_v=0.0))
            confirm_bars = min(3, _cp_int("F051_confirm_bars", 1, min_v=1))
            require_bias = int(round(_cp_float("F051_require_bias", 1.0, min_v=1.0)))
            bias = state["structure_bias"].shift(1).fillna(0.0)
            bias_allow = bias < 0.0 if require_bias <= 1 else bias <= 0.0
            allow = _ms_confirmed_closes(
                state["last_structure_low"],
                is_up=False,
                buffer_pct=buffer_pct,
                bars=confirm_bars,
            ) & bias_allow
            out["F051_BOSDOWN_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(
            k in cp_keys
            for k in (
                "F052_structure_scope",
                "F052_choch_dir",
                "F052_break_buffer_pct",
                "F052_confirm_bars",
                "F052_require_opposite_bias",
            )
        ):
            state = _ms_state(_ms_scope("F052"))
            choch_dir = _cp_float("F052_choch_dir", 1.0, min_v=-1.0)
            is_bullish = choch_dir >= 0.0
            buffer_pct = min(1.0, _cp_float("F052_break_buffer_pct", 0.0, min_v=0.0))
            confirm_bars = min(3, _cp_int("F052_confirm_bars", 1, min_v=1))
            require_opposite = _cp_float("F052_require_opposite_bias", 1.0, min_v=0.0) >= 1.0
            bias = state["structure_bias"].shift(1).fillna(0.0)
            if is_bullish:
                target = state["protected_high"].where(state["protected_high"].notna(), state["last_structure_high"])
                bias_allow = bias < 0.0 if require_opposite else pd.Series(True, index=out.index)
                confirmed = _ms_confirmed_closes(target, is_up=True, buffer_pct=buffer_pct, bars=confirm_bars)
            else:
                target = state["protected_low"].where(state["protected_low"].notna(), state["last_structure_low"])
                bias_allow = bias > 0.0 if require_opposite else pd.Series(True, index=out.index)
                confirmed = _ms_confirmed_closes(target, is_up=False, buffer_pct=buffer_pct, bars=confirm_bars)
            allow = confirmed & bias_allow
            out["F052_CHOCH_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

    candle_pattern_keys = (
        "F053_max_body_pct",
        "F053_min_range_pct",
        "F053_wick_mode",
        "F053_wick_balance_max_pct",
        "F054_containment_mode",
        "F054_max_inside_range_ratio",
        "F054_mother_min_range_pct",
        "F055_wick_body_ratio",
        "F055_wick_min_pct",
        "F055_opposite_wick_max_pct",
        "F055_body_zone_pct",
        "F055_min_range_pct",
        "F056_wick_body_ratio",
        "F056_wick_min_pct",
        "F056_opposite_wick_max_pct",
        "F056_body_zone_pct",
        "F056_min_range_pct",
        "F057_wick_body_ratio",
        "F057_lower_wick_min_pct",
        "F057_upper_wick_max_pct",
        "F057_body_zone_pct",
        "F057_trend_lookback_bars",
        "F057_trend_min_drop_pct",
        "F058_wick_body_ratio",
        "F058_upper_wick_min_pct",
        "F058_lower_wick_max_pct",
        "F058_body_zone_pct",
        "F058_trend_lookback_bars",
        "F058_trend_min_rise_pct",
        "F059_engulf_mode",
        "F059_min_engulf_ratio",
        "F059_min_body_pct",
        "F059_trend_lookback_bars",
        "F059_trend_min_drop_pct",
        "F060_engulf_mode",
        "F060_min_engulf_ratio",
        "F060_min_body_pct",
        "F060_trend_lookback_bars",
        "F060_trend_min_rise_pct",
    )
    if any(k in cp_keys for k in candle_pattern_keys):
        open_1 = out["open"].shift(1)
        high_1 = out["high"].shift(1)
        low_1 = out["low"].shift(1)
        close_1 = out["close"].shift(1)
        open_2 = out["open"].shift(2)
        high_2 = out["high"].shift(2)
        low_2 = out["low"].shift(2)
        close_2 = out["close"].shift(2)

        range_1 = high_1 - low_1
        range_2 = high_2 - low_2
        body_1 = (close_1 - open_1).abs()
        body_2 = (close_2 - open_2).abs()
        body_top_1 = pd.concat([open_1, close_1], axis=1).max(axis=1)
        body_bottom_1 = pd.concat([open_1, close_1], axis=1).min(axis=1)
        upper_wick_1 = high_1 - body_top_1
        lower_wick_1 = body_bottom_1 - low_1
        range_1_safe = range_1.replace(0.0, np.nan)
        range_2_safe = range_2.replace(0.0, np.nan)
        open_1_safe = open_1.replace(0.0, np.nan)
        open_2_safe = open_2.replace(0.0, np.nan)
        body_pct_1 = body_1 / range_1_safe * 100.0
        upper_wick_pct_1 = upper_wick_1 / range_1_safe * 100.0
        lower_wick_pct_1 = lower_wick_1 / range_1_safe * 100.0
        range_pct_1 = range_1 / open_1_safe * 100.0
        mother_range_pct = range_2 / open_2_safe * 100.0
        inside_range_ratio = range_1 / range_2_safe
        valid_1 = (range_1 > 0.0) & (open_1 > 0.0)
        valid_2 = (range_2 > 0.0) & (open_2 > 0.0)
        bull_1 = close_1 > open_1
        bear_1 = close_1 < open_1
        bull_2 = close_2 > open_2
        bear_2 = close_2 < open_2

        def _cp_enum_int(name: str, default: int, *, min_v: int, max_v: int) -> int:
            return min(max_v, _cp_int(name, default, min_v=min_v))

        def _pretrend_pct(lookback_bars: int) -> pd.Series:
            ref = out["close"].shift(2 + int(lookback_bars)).replace(0.0, np.nan)
            return (close_2 / ref - 1.0) * 100.0

        if any(k in cp_keys for k in ("F053_max_body_pct", "F053_min_range_pct", "F053_wick_mode", "F053_wick_balance_max_pct")):
            max_body_pct = min(15.0, _cp_float("F053_max_body_pct", 2.0, min_v=2.0))
            min_range_pct = min(0.50, _cp_float("F053_min_range_pct", 0.01, min_v=0.01))
            wick_mode = _cp_enum_int("F053_wick_mode", 1, min_v=1, max_v=2)
            wick_balance_max_pct = min(80.0, _cp_float("F053_wick_balance_max_pct", 20.0, min_v=20.0))
            base = valid_1 & (body_pct_1 <= max_body_pct) & (range_pct_1 >= min_range_pct)
            balanced = (upper_wick_pct_1 - lower_wick_pct_1).abs() <= wick_balance_max_pct
            allow = base if wick_mode <= 1 else base & balanced
            out["F053_DOJI_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(k in cp_keys for k in ("F054_containment_mode", "F054_max_inside_range_ratio", "F054_mother_min_range_pct")):
            containment_mode = _cp_enum_int("F054_containment_mode", 1, min_v=1, max_v=2)
            max_inside_range_ratio = min(1.0, _cp_float("F054_max_inside_range_ratio", 0.30, min_v=0.30))
            mother_min_range_pct = min(2.0, _cp_float("F054_mother_min_range_pct", 0.02, min_v=0.02))
            strict_inside = (high_1 < high_2) & (low_1 > low_2)
            equal_allowed_inside = (high_1 <= high_2) & (low_1 >= low_2)
            inside = strict_inside if containment_mode <= 1 else equal_allowed_inside
            allow = (
                valid_1
                & valid_2
                & inside
                & (inside_range_ratio <= max_inside_range_ratio)
                & (mother_range_pct >= mother_min_range_pct)
            )
            out["F054_INSIDEBAR_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(
            k in cp_keys
            for k in (
                "F055_wick_body_ratio",
                "F055_wick_min_pct",
                "F055_opposite_wick_max_pct",
                "F055_body_zone_pct",
                "F055_min_range_pct",
            )
        ):
            ratio = min(5.0, _cp_float("F055_wick_body_ratio", 1.5, min_v=1.5))
            wick_min_pct = min(85.0, _cp_float("F055_wick_min_pct", 50.0, min_v=50.0))
            opposite_max_pct = min(30.0, _cp_float("F055_opposite_wick_max_pct", 0.0, min_v=0.0))
            body_zone_pct = min(50.0, _cp_float("F055_body_zone_pct", 20.0, min_v=20.0))
            min_range_pct = min(1.0, _cp_float("F055_min_range_pct", 0.02, min_v=0.02))
            top_zone = body_bottom_1 >= high_1 - range_1 * body_zone_pct / 100.0
            allow = (
                valid_1
                & (lower_wick_1 >= body_1 * ratio)
                & (lower_wick_pct_1 >= wick_min_pct)
                & (upper_wick_pct_1 <= opposite_max_pct)
                & top_zone
                & (range_pct_1 >= min_range_pct)
            )
            out["F055_PINBULL_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(
            k in cp_keys
            for k in (
                "F056_wick_body_ratio",
                "F056_wick_min_pct",
                "F056_opposite_wick_max_pct",
                "F056_body_zone_pct",
                "F056_min_range_pct",
            )
        ):
            ratio = min(5.0, _cp_float("F056_wick_body_ratio", 1.5, min_v=1.5))
            wick_min_pct = min(85.0, _cp_float("F056_wick_min_pct", 50.0, min_v=50.0))
            opposite_max_pct = min(30.0, _cp_float("F056_opposite_wick_max_pct", 0.0, min_v=0.0))
            body_zone_pct = min(50.0, _cp_float("F056_body_zone_pct", 20.0, min_v=20.0))
            min_range_pct = min(1.0, _cp_float("F056_min_range_pct", 0.02, min_v=0.02))
            bottom_zone = body_top_1 <= low_1 + range_1 * body_zone_pct / 100.0
            allow = (
                valid_1
                & (upper_wick_1 >= body_1 * ratio)
                & (upper_wick_pct_1 >= wick_min_pct)
                & (lower_wick_pct_1 <= opposite_max_pct)
                & bottom_zone
                & (range_pct_1 >= min_range_pct)
            )
            out["F056_PINBEAR_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(
            k in cp_keys
            for k in (
                "F057_wick_body_ratio",
                "F057_lower_wick_min_pct",
                "F057_upper_wick_max_pct",
                "F057_body_zone_pct",
                "F057_trend_lookback_bars",
                "F057_trend_min_drop_pct",
            )
        ):
            ratio = min(5.0, _cp_float("F057_wick_body_ratio", 1.5, min_v=1.5))
            lower_min_pct = min(85.0, _cp_float("F057_lower_wick_min_pct", 50.0, min_v=50.0))
            upper_max_pct = min(25.0, _cp_float("F057_upper_wick_max_pct", 0.0, min_v=0.0))
            body_zone_pct = min(50.0, _cp_float("F057_body_zone_pct", 20.0, min_v=20.0))
            lookback = min(20, _cp_int("F057_trend_lookback_bars", 3, min_v=3))
            min_drop_pct = min(2.0, _cp_float("F057_trend_min_drop_pct", 0.05, min_v=0.05))
            top_zone = body_bottom_1 >= high_1 - range_1 * body_zone_pct / 100.0
            allow = (
                valid_1
                & (lower_wick_1 >= body_1 * ratio)
                & (lower_wick_pct_1 >= lower_min_pct)
                & (upper_wick_pct_1 <= upper_max_pct)
                & top_zone
                & (_pretrend_pct(lookback) <= -min_drop_pct)
            )
            out["F057_HAMMER_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(
            k in cp_keys
            for k in (
                "F058_wick_body_ratio",
                "F058_upper_wick_min_pct",
                "F058_lower_wick_max_pct",
                "F058_body_zone_pct",
                "F058_trend_lookback_bars",
                "F058_trend_min_rise_pct",
            )
        ):
            ratio = min(5.0, _cp_float("F058_wick_body_ratio", 1.5, min_v=1.5))
            upper_min_pct = min(85.0, _cp_float("F058_upper_wick_min_pct", 50.0, min_v=50.0))
            lower_max_pct = min(25.0, _cp_float("F058_lower_wick_max_pct", 0.0, min_v=0.0))
            body_zone_pct = min(50.0, _cp_float("F058_body_zone_pct", 20.0, min_v=20.0))
            lookback = min(20, _cp_int("F058_trend_lookback_bars", 3, min_v=3))
            min_rise_pct = min(2.0, _cp_float("F058_trend_min_rise_pct", 0.05, min_v=0.05))
            bottom_zone = body_top_1 <= low_1 + range_1 * body_zone_pct / 100.0
            allow = (
                valid_1
                & (upper_wick_1 >= body_1 * ratio)
                & (upper_wick_pct_1 >= upper_min_pct)
                & (lower_wick_pct_1 <= lower_max_pct)
                & bottom_zone
                & (_pretrend_pct(lookback) >= min_rise_pct)
            )
            out["F058_SHOOTINGSTAR_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(
            k in cp_keys
            for k in (
                "F059_engulf_mode",
                "F059_min_engulf_ratio",
                "F059_min_body_pct",
                "F059_trend_lookback_bars",
                "F059_trend_min_drop_pct",
            )
        ):
            engulf_mode = _cp_enum_int("F059_engulf_mode", 1, min_v=1, max_v=2)
            min_ratio = min(2.0, _cp_float("F059_min_engulf_ratio", 1.0, min_v=1.0))
            min_body_pct = min(70.0, _cp_float("F059_min_body_pct", 10.0, min_v=10.0))
            lookback = min(20, _cp_int("F059_trend_lookback_bars", 2, min_v=2))
            min_drop_pct = min(2.0, _cp_float("F059_trend_min_drop_pct", 0.0, min_v=0.0))
            body_engulf = bear_2 & bull_1 & (open_1 <= close_2) & (close_1 >= open_2)
            range_engulf = bear_2 & bull_1 & (low_1 <= low_2) & (high_1 >= high_2)
            engulf = body_engulf if engulf_mode <= 1 else range_engulf
            body_ratio = body_1 / body_2.replace(0.0, np.nan)
            allow = (
                valid_1
                & valid_2
                & (body_2 > 0.0)
                & engulf
                & (body_ratio >= min_ratio)
                & (body_pct_1 >= min_body_pct)
                & (_pretrend_pct(lookback) <= -min_drop_pct)
            )
            out["F059_ENGULFBULL_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(
            k in cp_keys
            for k in (
                "F060_engulf_mode",
                "F060_min_engulf_ratio",
                "F060_min_body_pct",
                "F060_trend_lookback_bars",
                "F060_trend_min_rise_pct",
            )
        ):
            engulf_mode = _cp_enum_int("F060_engulf_mode", 1, min_v=1, max_v=2)
            min_ratio = min(2.0, _cp_float("F060_min_engulf_ratio", 1.0, min_v=1.0))
            min_body_pct = min(70.0, _cp_float("F060_min_body_pct", 10.0, min_v=10.0))
            lookback = min(20, _cp_int("F060_trend_lookback_bars", 2, min_v=2))
            min_rise_pct = min(2.0, _cp_float("F060_trend_min_rise_pct", 0.0, min_v=0.0))
            body_engulf = bull_2 & bear_1 & (open_1 >= close_2) & (close_1 <= open_2)
            range_engulf = bull_2 & bear_1 & (high_1 >= high_2) & (low_1 <= low_2)
            engulf = body_engulf if engulf_mode <= 1 else range_engulf
            body_ratio = body_1 / body_2.replace(0.0, np.nan)
            allow = (
                valid_1
                & valid_2
                & (body_2 > 0.0)
                & engulf
                & (body_ratio >= min_ratio)
                & (body_pct_1 >= min_body_pct)
                & (_pretrend_pct(lookback) >= min_rise_pct)
            )
            out["F060_ENGULFBEAR_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

    divergence_pattern_keys = (
        "F061_pivot_scope",
        "F061_div_type",
        "F061_price_delta_min_pct",
        "F061_rsi_delta_min",
        "F061_max_pivot_gap_bars",
        "F061_confirm_mode",
        "F061_reaction_confirm_pct",
        "F062_pivot_scope",
        "F062_div_type",
        "F062_price_delta_min_pct",
        "F062_rsi_delta_min",
        "F062_max_pivot_gap_bars",
        "F062_confirm_mode",
        "F062_reaction_confirm_pct",
        "F063_pivot_scope",
        "F063_div_type",
        "F063_macd_component",
        "F063_price_delta_min_pct",
        "F063_macd_delta_min_pct",
        "F063_max_pivot_gap_bars",
        "F063_confirm_mode",
        "F063_reaction_confirm_pct",
        "F064_pivot_scope",
        "F064_div_type",
        "F064_macd_component",
        "F064_price_delta_min_pct",
        "F064_macd_delta_min_pct",
        "F064_max_pivot_gap_bars",
        "F064_confirm_mode",
        "F064_reaction_confirm_pct",
        "F065_pivot_scope",
        "F065_div_type",
        "F065_price_delta_min_pct",
        "F065_obv_delta_min_norm",
        "F065_max_pivot_gap_bars",
        "F065_confirm_mode",
        "F065_reaction_confirm_pct",
        "F066_pivot_scope",
        "F066_div_type",
        "F066_price_delta_min_pct",
        "F066_obv_delta_min_norm",
        "F066_max_pivot_gap_bars",
        "F066_confirm_mode",
        "F066_reaction_confirm_pct",
    )
    if any(k in cp_keys for k in divergence_pattern_keys):
        closed_high = out["high"].shift(1)
        closed_low = out["low"].shift(1)
        closed_close = out["close"].shift(1)
        rsi_div = _rsi(out["close"], period=14).shift(1)
        close_for_macd_pct = out["close"].shift(1).replace(0.0, np.nan)
        macd_line_div = ((macd_line_fixed / close_for_macd_pct) * 100.0).shift(1)
        macd_hist_div = ((macd_hist_fixed / close_for_macd_pct) * 100.0).shift(1)
        avg_volume_20_div = out["volume"].rolling(20).mean()
        obv_norm_div = (out["obv"] / avg_volume_20_div.replace(0.0, np.nan)).shift(1)
        closed_close_for_confirm = out["close"].shift(1)
        div_cache: dict[tuple[int, str, str], dict[str, pd.Series]] = {}

        def _div_enum(name: str, default: int, max_v: int = 2) -> int:
            return min(max_v, _cp_int(name, default, min_v=1))

        def _div_scope(prefix: str) -> tuple[int, int, int, int, float]:
            scope = _div_enum(f"{prefix}_pivot_scope", 1)
            if scope >= 2:
                return (2, 240, 10, 10, 0.30)
            return (1, 120, 3, 3, 0.10)

        def _div_pairs(prefix: str, indicator: pd.Series, pivot_kind: str) -> dict[str, pd.Series]:
            scope_id, lookback, left, right, min_swing_pct = _div_scope(prefix)
            cache_key = (scope_id, pivot_kind, str(indicator.name or prefix))
            if cache_key not in div_cache:
                div_cache[cache_key] = _confirmed_divergence_pivot_pairs(
                    closed_high,
                    closed_low,
                    closed_close,
                    indicator,
                    pivot_kind=pivot_kind,
                    lookback_bars=lookback,
                    pivot_left=left,
                    pivot_right=right,
                    min_price_swing_pct=min_swing_pct,
                )
            return div_cache[cache_key]

        def _divergence_allow(
            *,
            prefix: str,
            indicator: pd.Series,
            pivot_kind: str,
            is_bullish: bool,
            indicator_delta_min: float,
            price_delta_min_pct: float,
            max_gap_bars: int,
            confirm_mode: int,
            reaction_confirm_pct: float,
        ) -> pd.Series:
            pairs = _div_pairs(prefix, indicator, pivot_kind)
            price_a = pairs["prev_price"]
            price_b = pairs["last_price"]
            ind_a = pairs["prev_indicator"]
            ind_b = pairs["last_indicator"]
            gap_bars = pairs["gap_bars"]
            pivot_b_close = pairs["last_close"]
            delta = float(price_delta_min_pct) / 100.0
            if is_bullish:
                regular = (price_b <= price_a * (1.0 - delta)) & (ind_b >= ind_a + float(indicator_delta_min))
                hidden = (price_b >= price_a * (1.0 + delta)) & (ind_b <= ind_a - float(indicator_delta_min))
                confirm = closed_close_for_confirm >= pivot_b_close * (1.0 + float(reaction_confirm_pct) / 100.0)
            else:
                regular = (price_b >= price_a * (1.0 + delta)) & (ind_b <= ind_a - float(indicator_delta_min))
                hidden = (price_b <= price_a * (1.0 - delta)) & (ind_b >= ind_a + float(indicator_delta_min))
                confirm = closed_close_for_confirm <= pivot_b_close * (1.0 - float(reaction_confirm_pct) / 100.0)
            div_type = _div_enum(f"{prefix}_div_type", 1)
            div_ok = regular if div_type <= 1 else hidden
            confirm_ok = pd.Series(True, index=out.index) if confirm_mode <= 1 else confirm
            valid = (
                price_a.notna()
                & price_b.notna()
                & ind_a.notna()
                & ind_b.notna()
                & pivot_b_close.notna()
                & (gap_bars <= float(max_gap_bars))
            )
            return valid & div_ok & confirm_ok

        if any(
            k in cp_keys
            for k in (
                "F061_pivot_scope",
                "F061_div_type",
                "F061_price_delta_min_pct",
                "F061_rsi_delta_min",
                "F061_max_pivot_gap_bars",
                "F061_confirm_mode",
                "F061_reaction_confirm_pct",
            )
        ):
            price_delta = min(3.0, _cp_float("F061_price_delta_min_pct", 0.05, min_v=0.05))
            rsi_delta = min(30, _cp_int("F061_rsi_delta_min", 1, min_v=1))
            max_gap = min(120, _cp_int("F061_max_pivot_gap_bars", 5, min_v=5))
            confirm_mode = _div_enum("F061_confirm_mode", 1)
            reaction = min(1.0, _cp_float("F061_reaction_confirm_pct", 0.0, min_v=0.0))
            allow = _divergence_allow(
                prefix="F061",
                indicator=rsi_div.rename("rsi14_div"),
                pivot_kind="low",
                is_bullish=True,
                indicator_delta_min=float(rsi_delta),
                price_delta_min_pct=price_delta,
                max_gap_bars=max_gap,
                confirm_mode=confirm_mode,
                reaction_confirm_pct=reaction,
            )
            out["F061_RSIBULLDIV_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(
            k in cp_keys
            for k in (
                "F062_pivot_scope",
                "F062_div_type",
                "F062_price_delta_min_pct",
                "F062_rsi_delta_min",
                "F062_max_pivot_gap_bars",
                "F062_confirm_mode",
                "F062_reaction_confirm_pct",
            )
        ):
            price_delta = min(3.0, _cp_float("F062_price_delta_min_pct", 0.05, min_v=0.05))
            rsi_delta = min(30, _cp_int("F062_rsi_delta_min", 1, min_v=1))
            max_gap = min(120, _cp_int("F062_max_pivot_gap_bars", 5, min_v=5))
            confirm_mode = _div_enum("F062_confirm_mode", 1)
            reaction = min(1.0, _cp_float("F062_reaction_confirm_pct", 0.0, min_v=0.0))
            allow = _divergence_allow(
                prefix="F062",
                indicator=rsi_div.rename("rsi14_div"),
                pivot_kind="high",
                is_bullish=False,
                indicator_delta_min=float(rsi_delta),
                price_delta_min_pct=price_delta,
                max_gap_bars=max_gap,
                confirm_mode=confirm_mode,
                reaction_confirm_pct=reaction,
            )
            out["F062_RSIBEARDIV_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(
            k in cp_keys
            for k in (
                "F063_pivot_scope",
                "F063_div_type",
                "F063_macd_component",
                "F063_price_delta_min_pct",
                "F063_macd_delta_min_pct",
                "F063_max_pivot_gap_bars",
                "F063_confirm_mode",
                "F063_reaction_confirm_pct",
            )
        ):
            component = _div_enum("F063_macd_component", 1)
            indicator = macd_line_div.rename("macd_line_pct_div") if component <= 1 else macd_hist_div.rename("macd_hist_pct_div")
            price_delta = min(3.0, _cp_float("F063_price_delta_min_pct", 0.05, min_v=0.05))
            macd_delta = min(0.50, _cp_float("F063_macd_delta_min_pct", 0.0, min_v=0.0))
            max_gap = min(120, _cp_int("F063_max_pivot_gap_bars", 5, min_v=5))
            confirm_mode = _div_enum("F063_confirm_mode", 1)
            reaction = min(1.0, _cp_float("F063_reaction_confirm_pct", 0.0, min_v=0.0))
            allow = _divergence_allow(
                prefix="F063",
                indicator=indicator,
                pivot_kind="low",
                is_bullish=True,
                indicator_delta_min=macd_delta,
                price_delta_min_pct=price_delta,
                max_gap_bars=max_gap,
                confirm_mode=confirm_mode,
                reaction_confirm_pct=reaction,
            )
            out["F063_MACDBULLDIV_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(
            k in cp_keys
            for k in (
                "F064_pivot_scope",
                "F064_div_type",
                "F064_macd_component",
                "F064_price_delta_min_pct",
                "F064_macd_delta_min_pct",
                "F064_max_pivot_gap_bars",
                "F064_confirm_mode",
                "F064_reaction_confirm_pct",
            )
        ):
            component = _div_enum("F064_macd_component", 1)
            indicator = macd_line_div.rename("macd_line_pct_div") if component <= 1 else macd_hist_div.rename("macd_hist_pct_div")
            price_delta = min(3.0, _cp_float("F064_price_delta_min_pct", 0.05, min_v=0.05))
            macd_delta = min(0.50, _cp_float("F064_macd_delta_min_pct", 0.0, min_v=0.0))
            max_gap = min(120, _cp_int("F064_max_pivot_gap_bars", 5, min_v=5))
            confirm_mode = _div_enum("F064_confirm_mode", 1)
            reaction = min(1.0, _cp_float("F064_reaction_confirm_pct", 0.0, min_v=0.0))
            allow = _divergence_allow(
                prefix="F064",
                indicator=indicator,
                pivot_kind="high",
                is_bullish=False,
                indicator_delta_min=macd_delta,
                price_delta_min_pct=price_delta,
                max_gap_bars=max_gap,
                confirm_mode=confirm_mode,
                reaction_confirm_pct=reaction,
            )
            out["F064_MACDBEARDIV_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(
            k in cp_keys
            for k in (
                "F065_pivot_scope",
                "F065_div_type",
                "F065_price_delta_min_pct",
                "F065_obv_delta_min_norm",
                "F065_max_pivot_gap_bars",
                "F065_confirm_mode",
                "F065_reaction_confirm_pct",
            )
        ):
            price_delta = min(3.0, _cp_float("F065_price_delta_min_pct", 0.05, min_v=0.05))
            obv_delta = min(20.0, _cp_float("F065_obv_delta_min_norm", 0.5, min_v=0.5))
            max_gap = min(120, _cp_int("F065_max_pivot_gap_bars", 5, min_v=5))
            confirm_mode = _div_enum("F065_confirm_mode", 1)
            reaction = min(1.0, _cp_float("F065_reaction_confirm_pct", 0.0, min_v=0.0))
            allow = _divergence_allow(
                prefix="F065",
                indicator=obv_norm_div.rename("obv_norm_div"),
                pivot_kind="low",
                is_bullish=True,
                indicator_delta_min=obv_delta,
                price_delta_min_pct=price_delta,
                max_gap_bars=max_gap,
                confirm_mode=confirm_mode,
                reaction_confirm_pct=reaction,
            ) & (avg_volume_20_div.shift(1) > 0.0)
            out["F065_OBVBULLDIV_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(
            k in cp_keys
            for k in (
                "F066_pivot_scope",
                "F066_div_type",
                "F066_price_delta_min_pct",
                "F066_obv_delta_min_norm",
                "F066_max_pivot_gap_bars",
                "F066_confirm_mode",
                "F066_reaction_confirm_pct",
            )
        ):
            price_delta = min(3.0, _cp_float("F066_price_delta_min_pct", 0.05, min_v=0.05))
            obv_delta = min(20.0, _cp_float("F066_obv_delta_min_norm", 0.5, min_v=0.5))
            max_gap = min(120, _cp_int("F066_max_pivot_gap_bars", 5, min_v=5))
            confirm_mode = _div_enum("F066_confirm_mode", 1)
            reaction = min(1.0, _cp_float("F066_reaction_confirm_pct", 0.0, min_v=0.0))
            allow = _divergence_allow(
                prefix="F066",
                indicator=obv_norm_div.rename("obv_norm_div"),
                pivot_kind="high",
                is_bullish=False,
                indicator_delta_min=obv_delta,
                price_delta_min_pct=price_delta,
                max_gap_bars=max_gap,
                confirm_mode=confirm_mode,
                reaction_confirm_pct=reaction,
            ) & (avg_volume_20_div.shift(1) > 0.0)
            out["F066_OBVBEARDIV_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

    pattern_quality_keys = (
        "F067_strength_state",
        "F067_strength_thr",
        "F067_require_confirmation",
        "F067_require_context",
        "F068_age_mode",
        "F068_min_age_bars",
        "F068_max_age_bars",
    )
    if any(k in cp_keys for k in pattern_quality_keys):
        def _closed_flag(col: str) -> pd.Series:
            if col not in out.columns:
                return pd.Series(False, index=out.index)
            return pd.to_numeric(out[col], errors="coerce").fillna(0.0).shift(1).fillna(0.0) > 0.0

        simple_candle = _closed_flag("doji_flag") | _closed_flag("inside_bar_flag")
        directional_candle = (
            _closed_flag("pin_bar_bull_flag")
            | _closed_flag("pin_bar_bear_flag")
            | _closed_flag("hammer_flag")
            | _closed_flag("shooting_star_flag")
            | _closed_flag("engulf_bull_flag")
            | _closed_flag("engulf_bear_flag")
        )
        chart_pattern = (
            _closed_flag("double_bottom_flag")
            | _closed_flag("double_top_flag")
            | _closed_flag("head_shoulders_flag")
            | _closed_flag("inverse_head_shoulders_flag")
            | _closed_flag("triangle_flag")
            | _closed_flag("pennant_flag")
            | _closed_flag("wedge_rising_flag")
            | _closed_flag("wedge_falling_flag")
            | _closed_flag("range_flag")
        )
        divergence_pattern = (
            _closed_flag("rsi_bull_div_flag")
            | _closed_flag("rsi_bear_div_flag")
            | _closed_flag("macd_bull_div_flag")
            | _closed_flag("macd_bear_div_flag")
            | _closed_flag("obv_bull_div_flag")
            | _closed_flag("obv_bear_div_flag")
            | _closed_flag("F061_RSIBULLDIV_ALLOW")
            | _closed_flag("F062_RSIBEARDIV_ALLOW")
            | _closed_flag("F063_MACDBULLDIV_ALLOW")
            | _closed_flag("F064_MACDBEARDIV_ALLOW")
            | _closed_flag("F065_OBVBULLDIV_ALLOW")
            | _closed_flag("F066_OBVBEARDIV_ALLOW")
        )
        bullish_pattern = (
            _closed_flag("pin_bar_bull_flag")
            | _closed_flag("hammer_flag")
            | _closed_flag("engulf_bull_flag")
            | _closed_flag("double_bottom_flag")
            | _closed_flag("inverse_head_shoulders_flag")
            | _closed_flag("wedge_falling_flag")
            | _closed_flag("rsi_bull_div_flag")
            | _closed_flag("macd_bull_div_flag")
            | _closed_flag("obv_bull_div_flag")
            | _closed_flag("F061_RSIBULLDIV_ALLOW")
            | _closed_flag("F063_MACDBULLDIV_ALLOW")
            | _closed_flag("F065_OBVBULLDIV_ALLOW")
        )
        bearish_pattern = (
            _closed_flag("pin_bar_bear_flag")
            | _closed_flag("shooting_star_flag")
            | _closed_flag("engulf_bear_flag")
            | _closed_flag("double_top_flag")
            | _closed_flag("head_shoulders_flag")
            | _closed_flag("wedge_rising_flag")
            | _closed_flag("rsi_bear_div_flag")
            | _closed_flag("macd_bear_div_flag")
            | _closed_flag("obv_bear_div_flag")
            | _closed_flag("F062_RSIBEARDIV_ALLOW")
            | _closed_flag("F064_MACDBEARDIV_ALLOW")
            | _closed_flag("F066_OBVBEARDIV_ALLOW")
        )
        pattern_event = simple_candle | directional_candle | chart_pattern | divergence_pattern
        base_score = pd.Series(
            np.maximum.reduce(
                [
                    np.where(simple_candle, 1.0, 0.0),
                    np.where(directional_candle, 2.0, 0.0),
                    np.where(divergence_pattern, 3.0, 0.0),
                    np.where(chart_pattern, 3.0, 0.0),
                ]
            ),
            index=out.index,
        )
        level_bonus = _closed_flag("pattern_level_confirm_flag").astype(float)
        volume_bonus = _closed_flag("pattern_volume_confirm_flag").astype(float)
        structure_up = _closed_flag("bos_up_flag") | _closed_flag("F050_BOSUP_ALLOW") | _closed_flag("pattern_structure_volume_entry_long")
        structure_down = _closed_flag("bos_down_flag") | _closed_flag("F051_BOSDOWN_ALLOW") | _closed_flag("pattern_structure_volume_entry_short")
        structure_bonus = ((bullish_pattern & structure_up) | (bearish_pattern & structure_down)).astype(float)
        close_1 = out["close"].shift(1)
        close_2 = out["close"].shift(2)
        confirmation_bonus = (
            (bullish_pattern & (close_1 > close_2))
            | (bearish_pattern & (close_1 < close_2))
            | (~(bullish_pattern | bearish_pattern) & pattern_event)
        ).astype(float)
        strength_score = (
            base_score
            + level_bonus
            + volume_bonus
            + structure_bonus
            + confirmation_bonus
        ).where(pattern_event, 0.0).clip(lower=0.0, upper=7.0)

        if any(k in cp_keys for k in ("F067_strength_state", "F067_strength_thr", "F067_require_confirmation", "F067_require_context")):
            strength_state = _cp_int("F067_strength_state", 1, min_v=1)
            strength_thr = min(7.0, _cp_float("F067_strength_thr", 1.0, min_v=1.0))
            require_confirmation = _cp_float("F067_require_confirmation", 0.0, min_v=0.0) >= 1.0
            require_context = _cp_float("F067_require_context", 0.0, min_v=0.0) >= 1.0
            confirmation_ok = (
                confirmation_bonus > 0.0 if require_confirmation else pd.Series(True, index=out.index)
            )
            context_ok = (
                (level_bonus + volume_bonus + structure_bonus) > 0.0
                if require_context
                else pd.Series(True, index=out.index)
            )
            if strength_state <= 1:
                strength_allow = pattern_event & (strength_score >= strength_thr) & confirmation_ok & context_ok
            else:
                strength_allow = pattern_event & (strength_score <= strength_thr) & confirmation_ok & context_ok
            out["F067_PATTERNSTRENGTH_ALLOW"] = np.where(strength_allow.fillna(False), 1, 0).astype("int64")

        if any(k in cp_keys for k in ("F068_age_mode", "F068_min_age_bars", "F068_max_age_bars")):
            age_mode = min(3, _cp_int("F068_age_mode", 1, min_v=1))
            min_age = min(20, _cp_int("F068_min_age_bars", 0, min_v=0))
            max_age = min(120, _cp_int("F068_max_age_bars", 1, min_v=1))
            if max_age < min_age:
                max_age = min_age
            pattern_age = _bars_since_event(pattern_event.astype(int))
            if age_mode <= 1:
                age_allow = pattern_age <= float(max_age)
            elif age_mode == 2:
                age_allow = (pattern_age >= float(min_age)) & (pattern_age <= float(max_age))
            else:
                age_allow = pattern_age > float(max_age)
            out["F068_PATTERNAGE_ALLOW"] = np.where(age_allow.fillna(False), 1, 0).astype("int64")

    chart_pattern_keys = (
        "F069_bottom_tolerance_pct",
        "F069_min_separation_bars",
        "F069_neckline_break_required",
        "F069_break_buffer_pct",
        "F069_max_pattern_age_bars",
        "F070_top_tolerance_pct",
        "F070_min_separation_bars",
        "F070_neckline_break_required",
        "F070_break_buffer_pct",
        "F070_max_pattern_age_bars",
        "F071_shoulder_tolerance_pct",
        "F071_head_min_excess_pct",
        "F071_neckline_break_required",
        "F071_break_buffer_pct",
        "F071_max_pattern_age_bars",
        "F072_shoulder_tolerance_pct",
        "F072_head_min_excess_pct",
        "F072_neckline_break_required",
        "F072_break_buffer_pct",
        "F072_max_pattern_age_bars",
        "F073_triangle_type",
        "F073_min_touches",
        "F073_convergence_min_pct",
        "F073_breakout_required",
        "F073_break_dir",
        "F073_break_buffer_pct",
        "F074_impulse_dir",
        "F074_impulse_min_pct",
        "F074_consolidation_bars",
        "F074_compression_min_pct",
        "F074_breakout_required",
        "F074_break_buffer_pct",
        "F075_min_touches",
        "F075_convergence_min_pct",
        "F075_breakout_required",
        "F075_break_dir",
        "F075_break_buffer_pct",
        "F076_min_touches",
        "F076_convergence_min_pct",
        "F076_breakout_required",
        "F076_break_dir",
        "F076_break_buffer_pct",
        "F077_range_lookback",
        "F077_max_range_pct",
        "F077_min_touches_high",
        "F077_min_touches_low",
        "F077_range_pos_mode",
        "F077_range_pos_level",
    )
    if any(k in cp_keys for k in chart_pattern_keys):
        h1 = out["high"].shift(1)
        l1 = out["low"].shift(1)
        c1 = out["close"].shift(1)
        c_ref = c1.replace(0.0, np.nan)

        def _bool_param(name: str, default: int = 0) -> bool:
            return _cp_float(name, float(default), min_v=0.0) >= 1.0

        def _dir_param(name: str, default: int = 0) -> int:
            raw = int(round(_cp_float(name, float(default), min_v=-1.0)))
            if raw > 0:
                return 1
            if raw < 0:
                return -1
            return 0

        def _break_ok(
            *,
            required: bool,
            direction: int,
            close: pd.Series,
            upper: pd.Series,
            lower: pd.Series,
            buffer_pct: float,
        ) -> pd.Series:
            if not required:
                return pd.Series(True, index=out.index)
            up = close >= upper * (1.0 + float(buffer_pct) / 100.0)
            down = close <= lower * (1.0 - float(buffer_pct) / 100.0)
            if direction > 0:
                return up
            if direction < 0:
                return down
            return up | down

        def _chart_geometry(window: int = 60) -> dict[str, pd.Series]:
            half = max(5, int(window) // 2)
            first_high = h1.shift(half).rolling(half).max()
            first_low = l1.shift(half).rolling(half).min()
            second_high = h1.rolling(half).max()
            second_low = l1.rolling(half).min()
            first_range = first_high - first_low
            second_range = second_high - second_low
            convergence = ((first_range - second_range) / first_range.replace(0.0, np.nan)) * 100.0
            upper_slope = (second_high - first_high) / c_ref
            lower_slope = (second_low - first_low) / c_ref
            near_upper = (h1 >= second_high - second_range.abs() * 0.15).astype(float).rolling(half).sum()
            near_lower = (l1 <= second_low + second_range.abs() * 0.15).astype(float).rolling(half).sum()
            return {
                "first_high": first_high,
                "first_low": first_low,
                "second_high": second_high,
                "second_low": second_low,
                "first_range": first_range,
                "second_range": second_range,
                "convergence": convergence,
                "upper_slope": upper_slope,
                "lower_slope": lower_slope,
                "near_upper": near_upper,
                "near_lower": near_lower,
            }

        geom = _chart_geometry(60)

        if any(
            k in cp_keys
            for k in (
                "F069_bottom_tolerance_pct",
                "F069_min_separation_bars",
                "F069_neckline_break_required",
                "F069_break_buffer_pct",
                "F069_max_pattern_age_bars",
            )
        ):
            tol = min(1.0, _cp_float("F069_bottom_tolerance_pct", 0.05, min_v=0.05))
            sep = min(60, _cp_int("F069_min_separation_bars", 5, min_v=5))
            required = _bool_param("F069_neckline_break_required", 0)
            buffer_pct = min(1.0, _cp_float("F069_break_buffer_pct", 0.0, min_v=0.0))
            age = min(240, _cp_int("F069_max_pattern_age_bars", 20, min_v=20))
            bottom_1 = l1.shift(sep).rolling(age).min()
            bottom_2 = l1.rolling(sep).min()
            neckline = h1.rolling(age).max()
            bottoms_match = ((bottom_2 / bottom_1.replace(0.0, np.nan) - 1.0).abs() * 100.0) <= tol
            break_ok = (c1 >= neckline * (1.0 + buffer_pct / 100.0)) if required else pd.Series(True, index=out.index)
            allow = bottoms_match & break_ok & bottom_1.notna() & bottom_2.notna() & neckline.notna()
            out["F069_DOUBLEBOTTOM_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(
            k in cp_keys
            for k in (
                "F070_top_tolerance_pct",
                "F070_min_separation_bars",
                "F070_neckline_break_required",
                "F070_break_buffer_pct",
                "F070_max_pattern_age_bars",
            )
        ):
            tol = min(1.0, _cp_float("F070_top_tolerance_pct", 0.05, min_v=0.05))
            sep = min(60, _cp_int("F070_min_separation_bars", 5, min_v=5))
            required = _bool_param("F070_neckline_break_required", 0)
            buffer_pct = min(1.0, _cp_float("F070_break_buffer_pct", 0.0, min_v=0.0))
            age = min(240, _cp_int("F070_max_pattern_age_bars", 20, min_v=20))
            top_1 = h1.shift(sep).rolling(age).max()
            top_2 = h1.rolling(sep).max()
            neckline = l1.rolling(age).min()
            tops_match = ((top_2 / top_1.replace(0.0, np.nan) - 1.0).abs() * 100.0) <= tol
            break_ok = (c1 <= neckline * (1.0 - buffer_pct / 100.0)) if required else pd.Series(True, index=out.index)
            allow = tops_match & break_ok & top_1.notna() & top_2.notna() & neckline.notna()
            out["F070_DOUBLETOP_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(
            k in cp_keys
            for k in (
                "F071_shoulder_tolerance_pct",
                "F071_head_min_excess_pct",
                "F071_neckline_break_required",
                "F071_break_buffer_pct",
                "F071_max_pattern_age_bars",
            )
        ):
            tol = min(1.5, _cp_float("F071_shoulder_tolerance_pct", 0.05, min_v=0.05))
            excess = min(3.0, _cp_float("F071_head_min_excess_pct", 0.10, min_v=0.10))
            required = _bool_param("F071_neckline_break_required", 0)
            buffer_pct = min(1.0, _cp_float("F071_break_buffer_pct", 0.0, min_v=0.0))
            age = min(240, _cp_int("F071_max_pattern_age_bars", 30, min_v=30))
            seg = max(10, age // 6)
            left_shoulder = h1.shift(seg * 2).rolling(seg).max()
            head = h1.shift(seg).rolling(seg).max()
            right_shoulder = h1.rolling(seg).max()
            neckline = l1.rolling(seg * 3).min()
            shoulders_match = ((right_shoulder / left_shoulder.replace(0.0, np.nan) - 1.0).abs() * 100.0) <= tol
            head_ok = head >= pd.concat([left_shoulder, right_shoulder], axis=1).max(axis=1) * (1.0 + excess / 100.0)
            break_ok = (c1 <= neckline * (1.0 - buffer_pct / 100.0)) if required else pd.Series(True, index=out.index)
            allow = shoulders_match & head_ok & break_ok & neckline.notna()
            out["F071_HEADSHOULDERS_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(
            k in cp_keys
            for k in (
                "F072_shoulder_tolerance_pct",
                "F072_head_min_excess_pct",
                "F072_neckline_break_required",
                "F072_break_buffer_pct",
                "F072_max_pattern_age_bars",
            )
        ):
            tol = min(1.5, _cp_float("F072_shoulder_tolerance_pct", 0.05, min_v=0.05))
            excess = min(3.0, _cp_float("F072_head_min_excess_pct", 0.10, min_v=0.10))
            required = _bool_param("F072_neckline_break_required", 0)
            buffer_pct = min(1.0, _cp_float("F072_break_buffer_pct", 0.0, min_v=0.0))
            age = min(240, _cp_int("F072_max_pattern_age_bars", 30, min_v=30))
            seg = max(10, age // 6)
            left_shoulder = l1.shift(seg * 2).rolling(seg).min()
            head = l1.shift(seg).rolling(seg).min()
            right_shoulder = l1.rolling(seg).min()
            neckline = h1.rolling(seg * 3).max()
            shoulders_match = ((right_shoulder / left_shoulder.replace(0.0, np.nan) - 1.0).abs() * 100.0) <= tol
            head_ok = head <= pd.concat([left_shoulder, right_shoulder], axis=1).min(axis=1) * (1.0 - excess / 100.0)
            break_ok = (c1 >= neckline * (1.0 + buffer_pct / 100.0)) if required else pd.Series(True, index=out.index)
            allow = shoulders_match & head_ok & break_ok & neckline.notna()
            out["F072_INVHEADSHOULDERS_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(k in cp_keys for k in ("F073_triangle_type", "F073_min_touches", "F073_convergence_min_pct", "F073_breakout_required", "F073_break_dir", "F073_break_buffer_pct")):
            tri_type = min(3, _cp_int("F073_triangle_type", 1, min_v=1))
            touches = min(5, _cp_int("F073_min_touches", 2, min_v=2))
            convergence = min(60.0, _cp_float("F073_convergence_min_pct", 5.0, min_v=5.0))
            required = _bool_param("F073_breakout_required", 0)
            break_dir = _dir_param("F073_break_dir", 0)
            buffer_pct = min(1.0, _cp_float("F073_break_buffer_pct", 0.0, min_v=0.0))
            upper = geom["second_high"]
            lower = geom["second_low"]
            if tri_type == 2:
                geometry = (geom["upper_slope"].abs() <= 0.002) & (geom["lower_slope"] > 0.0)
            elif tri_type == 3:
                geometry = (geom["upper_slope"] < 0.0) & (geom["lower_slope"].abs() <= 0.002)
            else:
                geometry = (geom["upper_slope"] <= 0.0) & (geom["lower_slope"] >= 0.0)
            allow = (
                geometry
                & (geom["convergence"] >= convergence)
                & (geom["near_upper"] >= touches)
                & (geom["near_lower"] >= touches)
                & _break_ok(required=required, direction=break_dir, close=c1, upper=upper, lower=lower, buffer_pct=buffer_pct)
            )
            out["F073_TRIANGLE_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(k in cp_keys for k in ("F074_impulse_dir", "F074_impulse_min_pct", "F074_consolidation_bars", "F074_compression_min_pct", "F074_breakout_required", "F074_break_buffer_pct")):
            impulse_dir = _dir_param("F074_impulse_dir", 1)
            impulse_min = min(5.0, _cp_float("F074_impulse_min_pct", 0.30, min_v=0.30))
            bars = min(60, _cp_int("F074_consolidation_bars", 3, min_v=3))
            compression = min(70.0, _cp_float("F074_compression_min_pct", 5.0, min_v=5.0))
            required = _bool_param("F074_breakout_required", 0)
            buffer_pct = min(1.0, _cp_float("F074_break_buffer_pct", 0.0, min_v=0.0))
            impulse_pct = (c1.shift(bars) / c1.shift(bars * 2).replace(0.0, np.nan) - 1.0) * 100.0
            impulse_ok = impulse_pct >= impulse_min if impulse_dir >= 0 else impulse_pct <= -impulse_min
            range_now = (h1.rolling(bars).max() - l1.rolling(bars).min()) / c_ref * 100.0
            range_prev = (h1.shift(bars).rolling(bars).max() - l1.shift(bars).rolling(bars).min()) / c1.shift(bars).replace(0.0, np.nan) * 100.0
            compression_ok = ((range_prev - range_now) / range_prev.replace(0.0, np.nan) * 100.0) >= compression
            upper = h1.rolling(bars).max()
            lower = l1.rolling(bars).min()
            allow = impulse_ok & compression_ok & _break_ok(required=required, direction=impulse_dir, close=c1, upper=upper, lower=lower, buffer_pct=buffer_pct)
            out["F074_PENNANT_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(k in cp_keys for k in ("F075_min_touches", "F075_convergence_min_pct", "F075_breakout_required", "F075_break_dir", "F075_break_buffer_pct")):
            touches = min(5, _cp_int("F075_min_touches", 2, min_v=2))
            convergence = min(60.0, _cp_float("F075_convergence_min_pct", 5.0, min_v=5.0))
            required = _bool_param("F075_breakout_required", 0)
            break_dir = _dir_param("F075_break_dir", -1)
            buffer_pct = min(1.0, _cp_float("F075_break_buffer_pct", 0.0, min_v=0.0))
            geometry = (geom["upper_slope"] > 0.0) & (geom["lower_slope"] > geom["upper_slope"])
            allow = geometry & (geom["convergence"] >= convergence) & (geom["near_upper"] >= touches) & (geom["near_lower"] >= touches) & _break_ok(
                required=required, direction=break_dir, close=c1, upper=geom["second_high"], lower=geom["second_low"], buffer_pct=buffer_pct
            )
            out["F075_WEDGERISING_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(k in cp_keys for k in ("F076_min_touches", "F076_convergence_min_pct", "F076_breakout_required", "F076_break_dir", "F076_break_buffer_pct")):
            touches = min(5, _cp_int("F076_min_touches", 2, min_v=2))
            convergence = min(60.0, _cp_float("F076_convergence_min_pct", 5.0, min_v=5.0))
            required = _bool_param("F076_breakout_required", 0)
            break_dir = _dir_param("F076_break_dir", 1)
            buffer_pct = min(1.0, _cp_float("F076_break_buffer_pct", 0.0, min_v=0.0))
            geometry = (geom["upper_slope"] < geom["lower_slope"]) & (geom["lower_slope"] < 0.0)
            allow = geometry & (geom["convergence"] >= convergence) & (geom["near_upper"] >= touches) & (geom["near_lower"] >= touches) & _break_ok(
                required=required, direction=break_dir, close=c1, upper=geom["second_high"], lower=geom["second_low"], buffer_pct=buffer_pct
            )
            out["F076_WEDGEFALLING_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(k in cp_keys for k in ("F077_range_lookback", "F077_max_range_pct", "F077_min_touches_high", "F077_min_touches_low", "F077_range_pos_mode", "F077_range_pos_level")):
            lookback = min(240, _cp_int("F077_range_lookback", 20, min_v=20))
            max_range_pct = min(5.0, _cp_float("F077_max_range_pct", 0.10, min_v=0.10))
            min_high = min(5, _cp_int("F077_min_touches_high", 1, min_v=1))
            min_low = min(5, _cp_int("F077_min_touches_low", 1, min_v=1))
            pos_mode = min(4, _cp_int("F077_range_pos_mode", 1, min_v=1))
            pos_level = min(90, _cp_int("F077_range_pos_level", 10, min_v=10))
            range_high = h1.rolling(lookback).max()
            range_low = l1.rolling(lookback).min()
            range_width = range_high - range_low
            range_size_pct = (range_high / range_low.replace(0.0, np.nan) - 1.0) * 100.0
            touch_band = range_width * 0.10
            touches_high = (h1 >= range_high - touch_band).astype(float).rolling(lookback).sum()
            touches_low = (l1 <= range_low + touch_band).astype(float).rolling(lookback).sum()
            range_pos = ((c1 - range_low) / range_width.replace(0.0, np.nan)) * 100.0
            if pos_mode == 2:
                pos_ok = range_pos <= float(pos_level)
            elif pos_mode == 3:
                pos_ok = range_pos >= float(pos_level)
            elif pos_mode == 4:
                pos_ok = (range_pos - 50.0).abs() <= float(pos_level)
            else:
                pos_ok = pd.Series(True, index=out.index)
            allow = (range_size_pct <= max_range_pct) & (touches_high >= min_high) & (touches_low >= min_low) & pos_ok
            out["F077_RANGEFLAG_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

    pattern_confirmation_keys = (
        "F078_confirm_mode",
        "F078_ratio_thr",
        "F078_z_thr",
        "F078_confirm_bar_mode",
        "F078_direction_filter",
        "F079_level_source_mode",
        "F079_confirm_type",
        "F079_dist_thr_pct",
        "F079_reaction_confirm_pct",
        "F079_direction_filter",
    )
    if any(k in cp_keys for k in pattern_confirmation_keys):
        def _pc_closed_flag(col: str) -> pd.Series:
            if col not in out.columns:
                return pd.Series(False, index=out.index)
            return pd.to_numeric(out[col], errors="coerce").fillna(0.0).shift(1).fillna(0.0) > 0.0

        bullish_pattern = (
            _pc_closed_flag("pin_bar_bull_flag")
            | _pc_closed_flag("hammer_flag")
            | _pc_closed_flag("engulf_bull_flag")
            | _pc_closed_flag("double_bottom_flag")
            | _pc_closed_flag("inverse_head_shoulders_flag")
            | _pc_closed_flag("wedge_falling_flag")
            | _pc_closed_flag("rsi_bull_div_flag")
            | _pc_closed_flag("macd_bull_div_flag")
            | _pc_closed_flag("obv_bull_div_flag")
            | _pc_closed_flag("F055_PINBULL_ALLOW")
            | _pc_closed_flag("F057_HAMMER_ALLOW")
            | _pc_closed_flag("F059_ENGULFBULL_ALLOW")
            | _pc_closed_flag("F061_RSIBULLDIV_ALLOW")
            | _pc_closed_flag("F063_MACDBULLDIV_ALLOW")
            | _pc_closed_flag("F065_OBVBULLDIV_ALLOW")
            | _pc_closed_flag("F069_DOUBLEBOTTOM_ALLOW")
            | _pc_closed_flag("F072_INVHEADSHOULDERS_ALLOW")
            | _pc_closed_flag("F076_WEDGEFALLING_ALLOW")
        )
        bearish_pattern = (
            _pc_closed_flag("pin_bar_bear_flag")
            | _pc_closed_flag("shooting_star_flag")
            | _pc_closed_flag("engulf_bear_flag")
            | _pc_closed_flag("double_top_flag")
            | _pc_closed_flag("head_shoulders_flag")
            | _pc_closed_flag("wedge_rising_flag")
            | _pc_closed_flag("rsi_bear_div_flag")
            | _pc_closed_flag("macd_bear_div_flag")
            | _pc_closed_flag("obv_bear_div_flag")
            | _pc_closed_flag("F056_PINBEAR_ALLOW")
            | _pc_closed_flag("F058_SHOOTINGSTAR_ALLOW")
            | _pc_closed_flag("F060_ENGULFBEAR_ALLOW")
            | _pc_closed_flag("F062_RSIBEARDIV_ALLOW")
            | _pc_closed_flag("F064_MACDBEARDIV_ALLOW")
            | _pc_closed_flag("F066_OBVBEARDIV_ALLOW")
            | _pc_closed_flag("F070_DOUBLETOP_ALLOW")
            | _pc_closed_flag("F071_HEADSHOULDERS_ALLOW")
            | _pc_closed_flag("F075_WEDGERISING_ALLOW")
        )
        neutral_pattern = (
            _pc_closed_flag("doji_flag")
            | _pc_closed_flag("inside_bar_flag")
            | _pc_closed_flag("triangle_flag")
            | _pc_closed_flag("pennant_flag")
            | _pc_closed_flag("range_flag")
            | _pc_closed_flag("F053_DOJI_ALLOW")
            | _pc_closed_flag("F054_INSIDEBAR_ALLOW")
            | _pc_closed_flag("F073_TRIANGLE_ALLOW")
            | _pc_closed_flag("F074_PENNANT_ALLOW")
            | _pc_closed_flag("F077_RANGEFLAG_ALLOW")
        )
        pattern_event = bullish_pattern | bearish_pattern | neutral_pattern
        pattern_neutral_only = neutral_pattern & ~(bullish_pattern | bearish_pattern)

        if any(k in cp_keys for k in ("F078_confirm_mode", "F078_ratio_thr", "F078_z_thr", "F078_confirm_bar_mode", "F078_direction_filter")):
            confirm_mode = min(3, _cp_int("F078_confirm_mode", 1, min_v=1))
            ratio_thr = min(5.0, _cp_float("F078_ratio_thr", 1.0, min_v=1.0))
            z_thr = min(5.0, _cp_float("F078_z_thr", 0.0, min_v=0.0))
            bar_mode = min(3, _cp_int("F078_confirm_bar_mode", 1, min_v=1))
            direction_filter = min(2, _cp_int("F078_direction_filter", 1, min_v=1))

            volume_avg = out["volume"].rolling(20, min_periods=20).mean()
            volume_std = out["volume"].rolling(20, min_periods=20).std(ddof=0)
            if bar_mode <= 1:
                vol = out["volume"].shift(1)
                avg = volume_avg.shift(1)
                std = volume_std.shift(1)
                open_confirm = out["open"].shift(1)
                close_confirm = out["close"].shift(1)
            else:
                vol = out["volume"]
                avg = volume_avg
                std = volume_std
                open_confirm = out["open"]
                close_confirm = out["close"]

            vol_ratio = vol / avg.replace(0.0, np.nan)
            vol_z = (vol - avg) / std.replace(0.0, np.nan)
            ratio_ok = vol_ratio >= ratio_thr
            z_ok = vol_z >= z_thr
            if confirm_mode <= 1:
                mode_ok = ratio_ok
            elif confirm_mode == 2:
                mode_ok = z_ok
            else:
                mode_ok = ratio_ok & z_ok
            if direction_filter <= 1:
                direction_ok = pd.Series(True, index=out.index)
            else:
                direction_ok = (
                    (bullish_pattern & (close_confirm > open_confirm))
                    | (bearish_pattern & (close_confirm < open_confirm))
                    | pattern_neutral_only
                )
            allow = pattern_event & mode_ok & direction_ok & avg.gt(0.0)
            out["F078_PATTERNVOLCONF_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(k in cp_keys for k in ("F079_level_source_mode", "F079_confirm_type", "F079_dist_thr_pct", "F079_reaction_confirm_pct", "F079_direction_filter")):
            source_mode = min(5, _cp_int("F079_level_source_mode", 1, min_v=1))
            confirm_type = min(3, _cp_int("F079_confirm_type", 1, min_v=1))
            dist_thr_pct = min(2.0, _cp_float("F079_dist_thr_pct", 0.0, min_v=0.0))
            reaction_pct = min(1.0, _cp_float("F079_reaction_confirm_pct", 0.0, min_v=0.0))
            direction_filter = min(2, _cp_int("F079_direction_filter", 1, min_v=1))

            pattern_price = out["close"].shift(1)
            pattern_low = out["low"].shift(1)
            pattern_high = out["high"].shift(1)
            close_confirm = out["close"]

            swing_levels = [out["roll_min_20"].shift(1), out["roll_max_20"].shift(1)]
            density_levels = [
                (out["close"] * (1.0 - out["density_vpoc_distance_60"])).shift(1),
                (out["close"] * (1.0 - out["density_vpoc_distance_240"])).shift(1),
            ]
            if "fib_0236" not in out.columns:
                fib_grid_pc = _confirmed_fib_anchor_grid_features(
                    out["high"],
                    out["low"],
                    out["close"],
                    max_lookback_bars=240,
                    depth_bars=10,
                    deviation_pct=0.30,
                )
                for col in ("fib_0236", "fib_0382", "fib_0500", "fib_0618", "fib_0786"):
                    out[col] = fib_grid_pc[col]
            fib_levels = [out[col].shift(1) for col in ("fib_0236", "fib_0382", "fib_0500", "fib_0618", "fib_0786")]
            vwap_levels = [out["vwap"].shift(1)]

            if source_mode <= 1:
                levels = swing_levels
            elif source_mode == 2:
                levels = density_levels
            elif source_mode == 3:
                levels = fib_levels
            elif source_mode == 4:
                levels = vwap_levels
            else:
                levels = swing_levels + density_levels + fib_levels + vwap_levels

            candidates = pd.concat([pd.to_numeric(level, errors="coerce").reindex(out.index) for level in levels], axis=1)
            distance_pct = candidates.sub(pattern_price, axis=0).abs().div(pattern_price.replace(0.0, np.nan), axis=0) * 100.0
            nearest_distance_pct = distance_pct.min(axis=1, skipna=True)
            nearest_level = candidates.where(distance_pct.eq(nearest_distance_pct, axis=0)).bfill(axis=1).iloc[:, 0]

            level_valid = nearest_level.notna() & nearest_level.gt(0.0) & pattern_price.gt(0.0)
            near_level_ok = nearest_distance_pct <= dist_thr_pct
            if direction_filter <= 1:
                direction_ok = pd.Series(True, index=out.index)
            else:
                direction_ok = bullish_pattern | bearish_pattern | pattern_neutral_only

            bullish_rejection = (
                bullish_pattern
                & (pattern_low <= nearest_level * (1.0 + dist_thr_pct / 100.0))
                & (close_confirm >= nearest_level * (1.0 + reaction_pct / 100.0))
            )
            bearish_rejection = (
                bearish_pattern
                & (pattern_high >= nearest_level * (1.0 - dist_thr_pct / 100.0))
                & (close_confirm <= nearest_level * (1.0 - reaction_pct / 100.0))
            )
            bullish_breakout = bullish_pattern & (close_confirm >= nearest_level * (1.0 + reaction_pct / 100.0))
            bearish_breakout = bearish_pattern & (close_confirm <= nearest_level * (1.0 - reaction_pct / 100.0))

            if confirm_type <= 1:
                confirm_ok = near_level_ok & direction_ok
            elif confirm_type == 2:
                confirm_ok = bullish_rejection | bearish_rejection
            else:
                confirm_ok = bullish_breakout | bearish_breakout
            allow = pattern_event & level_valid & confirm_ok
            out["F079_PATTERNLEVELCONF_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

    pattern_composite_keys = (
        "F080_pattern_family_filter",
        "F080_direction_mode",
        "F080_logic_mode",
        "F080_use_strength",
        "F080_use_age",
        "F080_use_volume_confirm",
        "F080_use_level_confirm",
        "F080_structure_filter",
        "F080_breakout_filter",
        "F080_min_score",
        "F080_block_opposite_pattern",
        "F081_pattern_family_filter",
        "F081_direction_mode",
        "F081_logic_mode",
        "F081_use_strength",
        "F081_use_age",
        "F081_use_volume_confirm",
        "F081_use_level_confirm",
        "F081_structure_filter",
        "F081_breakout_filter",
        "F081_min_score",
        "F081_block_opposite_pattern",
    )
    if any(k in cp_keys for k in pattern_composite_keys):
        def _pce_flag(col: str) -> pd.Series:
            if col not in out.columns:
                return pd.Series(False, index=out.index)
            return pd.to_numeric(out[col], errors="coerce").fillna(0.0).shift(1).fillna(0.0) > 0.0

        candle_family = (
            _pce_flag("doji_flag")
            | _pce_flag("inside_bar_flag")
            | _pce_flag("pin_bar_bull_flag")
            | _pce_flag("pin_bar_bear_flag")
            | _pce_flag("hammer_flag")
            | _pce_flag("shooting_star_flag")
            | _pce_flag("engulf_bull_flag")
            | _pce_flag("engulf_bear_flag")
            | _pce_flag("F053_DOJI_ALLOW")
            | _pce_flag("F054_INSIDEBAR_ALLOW")
            | _pce_flag("F055_PINBULL_ALLOW")
            | _pce_flag("F056_PINBEAR_ALLOW")
            | _pce_flag("F057_HAMMER_ALLOW")
            | _pce_flag("F058_SHOOTINGSTAR_ALLOW")
            | _pce_flag("F059_ENGULFBULL_ALLOW")
            | _pce_flag("F060_ENGULFBEAR_ALLOW")
        )
        divergence_family = (
            _pce_flag("rsi_bull_div_flag")
            | _pce_flag("rsi_bear_div_flag")
            | _pce_flag("macd_bull_div_flag")
            | _pce_flag("macd_bear_div_flag")
            | _pce_flag("obv_bull_div_flag")
            | _pce_flag("obv_bear_div_flag")
            | _pce_flag("F061_RSIBULLDIV_ALLOW")
            | _pce_flag("F062_RSIBEARDIV_ALLOW")
            | _pce_flag("F063_MACDBULLDIV_ALLOW")
            | _pce_flag("F064_MACDBEARDIV_ALLOW")
            | _pce_flag("F065_OBVBULLDIV_ALLOW")
            | _pce_flag("F066_OBVBEARDIV_ALLOW")
        )
        chart_family = (
            _pce_flag("double_bottom_flag")
            | _pce_flag("double_top_flag")
            | _pce_flag("head_shoulders_flag")
            | _pce_flag("inverse_head_shoulders_flag")
            | _pce_flag("triangle_flag")
            | _pce_flag("pennant_flag")
            | _pce_flag("wedge_rising_flag")
            | _pce_flag("wedge_falling_flag")
            | _pce_flag("range_flag")
            | _pce_flag("F069_DOUBLEBOTTOM_ALLOW")
            | _pce_flag("F070_DOUBLETOP_ALLOW")
            | _pce_flag("F071_HEADSHOULDERS_ALLOW")
            | _pce_flag("F072_INVHEADSHOULDERS_ALLOW")
            | _pce_flag("F073_TRIANGLE_ALLOW")
            | _pce_flag("F074_PENNANT_ALLOW")
            | _pce_flag("F075_WEDGERISING_ALLOW")
            | _pce_flag("F076_WEDGEFALLING_ALLOW")
            | _pce_flag("F077_RANGEFLAG_ALLOW")
        )
        bullish_pattern = (
            _pce_flag("pin_bar_bull_flag")
            | _pce_flag("hammer_flag")
            | _pce_flag("engulf_bull_flag")
            | _pce_flag("double_bottom_flag")
            | _pce_flag("inverse_head_shoulders_flag")
            | _pce_flag("wedge_falling_flag")
            | _pce_flag("rsi_bull_div_flag")
            | _pce_flag("macd_bull_div_flag")
            | _pce_flag("obv_bull_div_flag")
            | _pce_flag("F055_PINBULL_ALLOW")
            | _pce_flag("F057_HAMMER_ALLOW")
            | _pce_flag("F059_ENGULFBULL_ALLOW")
            | _pce_flag("F061_RSIBULLDIV_ALLOW")
            | _pce_flag("F063_MACDBULLDIV_ALLOW")
            | _pce_flag("F065_OBVBULLDIV_ALLOW")
            | _pce_flag("F069_DOUBLEBOTTOM_ALLOW")
            | _pce_flag("F072_INVHEADSHOULDERS_ALLOW")
            | _pce_flag("F076_WEDGEFALLING_ALLOW")
        )
        bearish_pattern = (
            _pce_flag("pin_bar_bear_flag")
            | _pce_flag("shooting_star_flag")
            | _pce_flag("engulf_bear_flag")
            | _pce_flag("double_top_flag")
            | _pce_flag("head_shoulders_flag")
            | _pce_flag("wedge_rising_flag")
            | _pce_flag("rsi_bear_div_flag")
            | _pce_flag("macd_bear_div_flag")
            | _pce_flag("obv_bear_div_flag")
            | _pce_flag("F056_PINBEAR_ALLOW")
            | _pce_flag("F058_SHOOTINGSTAR_ALLOW")
            | _pce_flag("F060_ENGULFBEAR_ALLOW")
            | _pce_flag("F062_RSIBEARDIV_ALLOW")
            | _pce_flag("F064_MACDBEARDIV_ALLOW")
            | _pce_flag("F066_OBVBEARDIV_ALLOW")
            | _pce_flag("F070_DOUBLETOP_ALLOW")
            | _pce_flag("F071_HEADSHOULDERS_ALLOW")
            | _pce_flag("F075_WEDGERISING_ALLOW")
        )
        neutral_pattern = (
            _pce_flag("doji_flag")
            | _pce_flag("inside_bar_flag")
            | _pce_flag("triangle_flag")
            | _pce_flag("pennant_flag")
            | _pce_flag("range_flag")
            | _pce_flag("F053_DOJI_ALLOW")
            | _pce_flag("F054_INSIDEBAR_ALLOW")
            | _pce_flag("F073_TRIANGLE_ALLOW")
            | _pce_flag("F074_PENNANT_ALLOW")
            | _pce_flag("F077_RANGEFLAG_ALLOW")
        ) & ~(bullish_pattern | bearish_pattern)
        pattern_event = candle_family | divergence_family | chart_family

        ms_state = _confirmed_market_structure_state(
            out["high"],
            out["low"],
            lookback_bars=120,
            pivot_left=3,
            pivot_right=3,
            min_swing_pct=0.15,
        )
        structure_bias = ms_state["structure_bias"].shift(1).fillna(0.0)
        bullish_bias = structure_bias > 0.0
        bearish_bias = structure_bias < 0.0
        choch_base = _pce_flag("choch_flag") | _pce_flag("F052_CHOCH_ALLOW")
        bullish_choch = choch_base & (out["ema_gap"].shift(1).fillna(0.0) > 0.0)
        bearish_choch = choch_base & (out["ema_gap"].shift(1).fillna(0.0) < 0.0)
        bos_up = _pce_flag("bos_up_flag") | _pce_flag("F050_BOSUP_ALLOW")
        bos_down = _pce_flag("bos_down_flag") | _pce_flag("F051_BOSDOWN_ALLOW")

        breakout_up = _pce_flag("breakout_up") | (_pce_flag("F045_BREAKOUT_ALLOW") & (out["close"].shift(1) > out["roll_max_20"].shift(2)))
        breakout_down = _pce_flag("breakout_down") | (_pce_flag("F045_BREAKOUT_ALLOW") & (out["close"].shift(1) < out["roll_min_20"].shift(2)))
        retest_up = _pce_flag("F047_RETEST_ALLOW") & (out["close"].shift(1) >= out["roll_max_20"].shift(2))
        retest_down = _pce_flag("F047_RETEST_ALLOW") & (out["close"].shift(1) <= out["roll_min_20"].shift(2))
        swing_high_break = _pce_flag("swing_high_break_flag") | _pce_flag("F048_SWINGHIGHBREAK_ALLOW")
        swing_low_break = _pce_flag("swing_low_break_flag") | _pce_flag("F049_SWINGLOWBREAK_ALLOW")

        strength_ok = _pce_flag("F067_PATTERNSTRENGTH_ALLOW")
        age_ok = _pce_flag("F068_PATTERNAGE_ALLOW")
        volume_ok = _pce_flag("F078_PATTERNVOLCONF_ALLOW") | _pce_flag("pattern_volume_confirm_flag")
        level_ok = _pce_flag("F079_PATTERNLEVELCONF_ALLOW") | _pce_flag("pattern_level_confirm_flag")

        def _pce_common(prefix: str) -> dict[str, int | bool]:
            return {
                "family": min(4, _cp_int(f"{prefix}_pattern_family_filter", 1, min_v=1)),
                "direction_mode": min(2, _cp_int(f"{prefix}_direction_mode", 1, min_v=1)),
                "logic_mode": min(2, _cp_int(f"{prefix}_logic_mode", 1, min_v=1)),
                "use_strength": _cp_float(f"{prefix}_use_strength", 0.0, min_v=0.0) >= 1.0,
                "use_age": _cp_float(f"{prefix}_use_age", 0.0, min_v=0.0) >= 1.0,
                "use_volume": _cp_float(f"{prefix}_use_volume_confirm", 0.0, min_v=0.0) >= 1.0,
                "use_level": _cp_float(f"{prefix}_use_level_confirm", 0.0, min_v=0.0) >= 1.0,
                "min_score": min(7, _cp_int(f"{prefix}_min_score", 2, min_v=2)),
                "block_opposite": _cp_float(f"{prefix}_block_opposite_pattern", 1.0, min_v=0.0) >= 1.0,
            }

        def _family_ok(family_id: int) -> pd.Series:
            if family_id == 2:
                return candle_family
            if family_id == 3:
                return divergence_family
            if family_id == 4:
                return chart_family
            return pattern_event

        def _composite_score(structure_ok: pd.Series, breakout_ok: pd.Series) -> pd.Series:
            return (
                pattern_event.astype(int)
                + strength_ok.astype(int)
                + age_ok.astype(int)
                + volume_ok.astype(int)
                + level_ok.astype(int)
                + structure_ok.astype(int)
                + breakout_ok.astype(int)
            )

        if any(k.startswith("F080_") for k in cp_keys):
            params = _pce_common("F080")
            structure_filter = min(5, _cp_int("F080_structure_filter", 1, min_v=1))
            breakout_filter = min(5, _cp_int("F080_breakout_filter", 1, min_v=1))
            if structure_filter == 2:
                structure_ok = bullish_bias
            elif structure_filter == 3:
                structure_ok = bos_up
            elif structure_filter == 4:
                structure_ok = bullish_choch
            elif structure_filter == 5:
                structure_ok = bullish_bias | bos_up | bullish_choch
            else:
                structure_ok = pd.Series(True, index=out.index)
            if breakout_filter == 2:
                breakout_ok = breakout_up
            elif breakout_filter == 3:
                breakout_ok = retest_up
            elif breakout_filter == 4:
                breakout_ok = swing_high_break
            elif breakout_filter == 5:
                breakout_ok = breakout_up | retest_up | swing_high_break
            else:
                breakout_ok = pd.Series(True, index=out.index)
            score = _composite_score(structure_ok, breakout_ok)
            direction_ok = bullish_pattern | ((params["direction_mode"] >= 2) & neutral_pattern & (score >= int(params["min_score"])))
            if bool(params["block_opposite"]):
                direction_ok &= ~bearish_pattern
            family_ok = _family_ok(int(params["family"]))
            strict_ok = (
                family_ok
                & pattern_event
                & direction_ok
                & structure_ok
                & breakout_ok
                & ((not bool(params["use_strength"])) | strength_ok)
                & ((not bool(params["use_age"])) | age_ok)
                & ((not bool(params["use_volume"])) | volume_ok)
                & ((not bool(params["use_level"])) | level_ok)
            )
            score_ok = family_ok & pattern_event & direction_ok & (score >= int(params["min_score"]))
            allow = strict_ok if int(params["logic_mode"]) <= 1 else score_ok
            out["F080_PATTERNLONG_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

        if any(k.startswith("F081_") for k in cp_keys):
            params = _pce_common("F081")
            structure_filter = min(5, _cp_int("F081_structure_filter", 1, min_v=1))
            breakout_filter = min(5, _cp_int("F081_breakout_filter", 1, min_v=1))
            if structure_filter == 2:
                structure_ok = bearish_bias
            elif structure_filter == 3:
                structure_ok = bos_down
            elif structure_filter == 4:
                structure_ok = bearish_choch
            elif structure_filter == 5:
                structure_ok = bearish_bias | bos_down | bearish_choch
            else:
                structure_ok = pd.Series(True, index=out.index)
            if breakout_filter == 2:
                breakout_ok = breakout_down
            elif breakout_filter == 3:
                breakout_ok = retest_down
            elif breakout_filter == 4:
                breakout_ok = swing_low_break
            elif breakout_filter == 5:
                breakout_ok = breakout_down | retest_down | swing_low_break
            else:
                breakout_ok = pd.Series(True, index=out.index)
            score = _composite_score(structure_ok, breakout_ok)
            direction_ok = bearish_pattern | ((params["direction_mode"] >= 2) & neutral_pattern & (score >= int(params["min_score"])))
            if bool(params["block_opposite"]):
                direction_ok &= ~bullish_pattern
            family_ok = _family_ok(int(params["family"]))
            strict_ok = (
                family_ok
                & pattern_event
                & direction_ok
                & structure_ok
                & breakout_ok
                & ((not bool(params["use_strength"])) | strength_ok)
                & ((not bool(params["use_age"])) | age_ok)
                & ((not bool(params["use_volume"])) | volume_ok)
                & ((not bool(params["use_level"])) | level_ok)
            )
            score_ok = family_ok & pattern_event & direction_ok & (score >= int(params["min_score"]))
            allow = strict_ok if int(params["logic_mode"]) <= 1 else score_ok
            out["F081_PATTERNSHORT_ALLOW"] = np.where(allow.fillna(False), 1, 0).astype("int64")

    pattern_trade_context_keys = (
        "F082_sl_anchor_mode",
        "F082_buffer_mode",
        "F082_buffer_pct",
        "F082_atr_mult",
        "F082_range_mult",
        "F082_sl_distance_mode",
        "F082_min_sl_dist_pct",
        "F082_max_sl_dist_pct",
        "F083_target_source_mode",
        "F083_min_targets",
        "F083_min_rr_to_target",
        "F083_target_spacing_min_pct",
        "F083_require_clear_path",
        "F083_ladder_state",
        "F083_ladder_score_thr",
    )
    if any(k in cp_keys for k in pattern_trade_context_keys):
        def _ptc_flag(col: str) -> pd.Series:
            if col not in out.columns:
                return pd.Series(False, index=out.index)
            return pd.to_numeric(out[col], errors="coerce").fillna(0.0).shift(1).fillna(0.0) > 0.0

        pattern_event = (
            _ptc_flag("doji_flag")
            | _ptc_flag("inside_bar_flag")
            | _ptc_flag("pin_bar_bull_flag")
            | _ptc_flag("pin_bar_bear_flag")
            | _ptc_flag("hammer_flag")
            | _ptc_flag("shooting_star_flag")
            | _ptc_flag("engulf_bull_flag")
            | _ptc_flag("engulf_bear_flag")
            | _ptc_flag("double_bottom_flag")
            | _ptc_flag("double_top_flag")
            | _ptc_flag("head_shoulders_flag")
            | _ptc_flag("inverse_head_shoulders_flag")
            | _ptc_flag("triangle_flag")
            | _ptc_flag("pennant_flag")
            | _ptc_flag("wedge_rising_flag")
            | _ptc_flag("wedge_falling_flag")
            | _ptc_flag("range_flag")
            | _ptc_flag("rsi_bull_div_flag")
            | _ptc_flag("rsi_bear_div_flag")
            | _ptc_flag("macd_bull_div_flag")
            | _ptc_flag("macd_bear_div_flag")
            | _ptc_flag("obv_bull_div_flag")
            | _ptc_flag("obv_bear_div_flag")
            | _ptc_flag("F053_DOJI_ALLOW")
            | _ptc_flag("F054_INSIDEBAR_ALLOW")
            | _ptc_flag("F055_PINBULL_ALLOW")
            | _ptc_flag("F056_PINBEAR_ALLOW")
            | _ptc_flag("F057_HAMMER_ALLOW")
            | _ptc_flag("F058_SHOOTINGSTAR_ALLOW")
            | _ptc_flag("F059_ENGULFBULL_ALLOW")
            | _ptc_flag("F060_ENGULFBEAR_ALLOW")
            | _ptc_flag("F061_RSIBULLDIV_ALLOW")
            | _ptc_flag("F062_RSIBEARDIV_ALLOW")
            | _ptc_flag("F063_MACDBULLDIV_ALLOW")
            | _ptc_flag("F064_MACDBEARDIV_ALLOW")
            | _ptc_flag("F065_OBVBULLDIV_ALLOW")
            | _ptc_flag("F066_OBVBEARDIV_ALLOW")
            | _ptc_flag("F069_DOUBLEBOTTOM_ALLOW")
            | _ptc_flag("F070_DOUBLETOP_ALLOW")
            | _ptc_flag("F071_HEADSHOULDERS_ALLOW")
            | _ptc_flag("F072_INVHEADSHOULDERS_ALLOW")
            | _ptc_flag("F073_TRIANGLE_ALLOW")
            | _ptc_flag("F074_PENNANT_ALLOW")
            | _ptc_flag("F075_WEDGERISING_ALLOW")
            | _ptc_flag("F076_WEDGEFALLING_ALLOW")
            | _ptc_flag("F077_RANGEFLAG_ALLOW")
            | _ptc_flag("F080_PATTERNLONG_ALLOW")
            | _ptc_flag("F081_PATTERNSHORT_ALLOW")
        )
        entry_ref = out["close"].shift(1)
        valid_entry = entry_ref > 0.0
        pattern_low = out["low"].shift(1)
        pattern_high = out["high"].shift(1)
        pattern_mid = (pattern_low + pattern_high) / 2.0
        pattern_range_pct = ((pattern_high - pattern_low).abs() / entry_ref.replace(0, np.nan)) * 100.0

        if "fib_0236" not in out.columns:
            fib_grid_ptc = _confirmed_fib_anchor_grid_features(
                out["high"],
                out["low"],
                out["close"],
                max_lookback_bars=240,
                depth_bars=10,
                deviation_pct=0.30,
            )
            for col in ("fib_0236", "fib_0382", "fib_0500", "fib_0618", "fib_0786"):
                out[col] = fib_grid_ptc[col]

        support_level = out["roll_min_20"].shift(1)
        resistance_level = out["roll_max_20"].shift(1)
        density_60_level = (out["close"] * (1.0 - out["density_vpoc_distance_60"])).shift(1)
        density_240_level = (out["close"] * (1.0 - out["density_vpoc_distance_240"])).shift(1)
        vwap_level = out["vwap"].shift(1) if "vwap" in out.columns else entry_ref * (1.0 - out["vwap_distance"].shift(1))
        fib_levels = [out[col].shift(1) for col in ("fib_0236", "fib_0382", "fib_0500", "fib_0618", "fib_0786")]
        all_levels = [support_level, resistance_level, density_60_level, density_240_level, vwap_level] + fib_levels
        all_context = _nearest_context_from_levels(entry_ref, all_levels)
        structure_context = _nearest_context_from_levels(entry_ref, [support_level, resistance_level])
        pattern_height = (pattern_high - pattern_low).abs()
        pattern_target_long = entry_ref + pattern_height
        pattern_target_short = entry_ref - pattern_height

        def _valid_level(level: pd.Series) -> pd.Series:
            return pd.to_numeric(level, errors="coerce").where(lambda s: s > 0.0)

        def _anchor_context(mode: int) -> tuple[pd.Series, pd.Series]:
            if mode <= 1:
                return _valid_level(pattern_low), _valid_level(pattern_high)
            if mode == 2:
                return structure_context["sl_long"], structure_context["sl_short"]
            return all_context["sl_long"], all_context["sl_short"]

        def _buffer_pct() -> pd.Series:
            buffer_mode = min(3, _cp_int("F082_buffer_mode", 1, min_v=1))
            if buffer_mode == 2:
                atr_mult = min(3.0, _cp_float("F082_atr_mult", 1.0, min_v=0.2))
                atr_pct = pd.to_numeric(out["atr14"], errors="coerce").shift(1).fillna(0.0) * 100.0
                return (atr_pct * float(atr_mult)).clip(lower=0.0)
            if buffer_mode == 3:
                range_mult = min(1.0, _cp_float("F082_range_mult", 0.5, min_v=0.1))
                return (pattern_range_pct.fillna(0.0) * float(range_mult)).clip(lower=0.0)
            buffer_pct = min(1.0, _cp_float("F082_buffer_pct", 0.0, min_v=0.0))
            return pd.Series(float(buffer_pct), index=out.index)

        sl_distance_long = pd.Series(np.nan, index=out.index)
        sl_distance_short = pd.Series(np.nan, index=out.index)
        if any(k.startswith("F082_") for k in cp_keys):
            anchor_mode = min(3, _cp_int("F082_sl_anchor_mode", 1, min_v=1))
            sl_distance_mode = min(3, _cp_int("F082_sl_distance_mode", 1, min_v=1))
            min_sl_dist_pct = min(2.0, _cp_float("F082_min_sl_dist_pct", 0.02, min_v=0.02))
            max_sl_dist_pct = min(5.0, _cp_float("F082_max_sl_dist_pct", 1.0, min_v=0.05))
            invalid_long, invalid_short = _anchor_context(anchor_mode)
            buffer = _buffer_pct()
            sl_long = invalid_long * (1.0 - buffer / 100.0)
            sl_short = invalid_short * (1.0 + buffer / 100.0)
            sl_distance_long = (entry_ref / sl_long.replace(0, np.nan) - 1.0) * 100.0
            sl_distance_short = (sl_short / entry_ref.replace(0, np.nan) - 1.0) * 100.0
            valid_long = pattern_event & valid_entry & (sl_long > 0.0) & (sl_distance_long > 0.0)
            valid_short = pattern_event & valid_entry & (sl_short > 0.0) & (sl_distance_short > 0.0)
            if sl_distance_mode <= 1:
                long_allow = valid_long & (sl_distance_long <= float(max_sl_dist_pct))
                short_allow = valid_short & (sl_distance_short <= float(max_sl_dist_pct))
            elif sl_distance_mode == 2:
                long_allow = valid_long & (sl_distance_long >= float(min_sl_dist_pct))
                short_allow = valid_short & (sl_distance_short >= float(min_sl_dist_pct))
            else:
                long_allow = valid_long & (sl_distance_long >= float(min_sl_dist_pct)) & (sl_distance_long <= float(max_sl_dist_pct))
                short_allow = valid_short & (sl_distance_short >= float(min_sl_dist_pct)) & (sl_distance_short <= float(max_sl_dist_pct))
            out["F082_PATTERNSLBUF_ALLOW_LONG"] = np.where(long_allow.fillna(False), 1, 0).astype("int64")
            out["F082_PATTERNSLBUF_ALLOW_SHORT"] = np.where(short_allow.fillna(False), 1, 0).astype("int64")
            out["F082_PATTERNSLBUF_ALLOW"] = np.where((long_allow | short_allow).fillna(False), 1, 0).astype("int64")

        if any(k.startswith("F083_") for k in cp_keys):
            target_source_mode = min(6, _cp_int("F083_target_source_mode", 6, min_v=1))
            min_targets = min(5, _cp_int("F083_min_targets", 1, min_v=1))
            min_rr_to_target = min(5.0, _cp_float("F083_min_rr_to_target", 1.0, min_v=0.5))
            spacing_min_pct = min(2.0, _cp_float("F083_target_spacing_min_pct", 0.05, min_v=0.05))
            require_clear_path = _cp_float("F083_require_clear_path", 0.0, min_v=0.0) >= 1.0
            ladder_state = min(2, _cp_int("F083_ladder_state", 1, min_v=1))
            ladder_score_thr = min(10.0, _cp_float("F083_ladder_score_thr", 1.0, min_v=1.0))

            source_levels: list[pd.Series] = []
            if target_source_mode in (1, 6):
                source_levels.extend([pattern_target_long, pattern_target_short])
            if target_source_mode in (2, 6):
                source_levels.extend([support_level, resistance_level])
            if target_source_mode in (3, 6):
                source_levels.extend([density_60_level, density_240_level])
            if target_source_mode in (4, 6):
                source_levels.extend(fib_levels)
            if target_source_mode in (5, 6):
                source_levels.append(vwap_level)
            if not source_levels:
                source_levels = all_levels
            candidates = pd.concat([pd.to_numeric(level, errors="coerce").reindex(out.index) for level in source_levels], axis=1)
            above = candidates.where(candidates.gt(entry_ref, axis=0))
            below = candidates.where(candidates.lt(entry_ref, axis=0))

            def _ladder(side: str) -> tuple[pd.Series, pd.Series]:
                target_frame = above if side == "long" else below
                distances: list[pd.Series] = []
                for col in target_frame.columns:
                    target = target_frame[col]
                    if side == "long":
                        distances.append((target / entry_ref.replace(0, np.nan) - 1.0) * 100.0)
                    else:
                        distances.append((entry_ref / target.replace(0, np.nan) - 1.0) * 100.0)
                if not distances:
                    zero = pd.Series(0.0, index=out.index)
                    return zero, zero
                dist_frame = pd.concat(distances, axis=1)
                valid_targets = dist_frame.gt(0.0)
                target_count = valid_targets.sum(axis=1).astype(float)
                risk = sl_distance_long if side == "long" else sl_distance_short
                fallback_risk = out["pattern_sl_buffer_distance"].shift(1).abs() * 100.0
                risk = pd.to_numeric(risk, errors="coerce").where(lambda s: s > 0.0, fallback_risk)
                rr_count = dist_frame.div(risk.replace(0, np.nan), axis=0).ge(float(min_rr_to_target)).sum(axis=1).astype(float)
                sorted_dist = np.sort(np.where(valid_targets, dist_frame, np.nan), axis=1)
                spacing_ok = pd.Series(0.0, index=out.index)
                if sorted_dist.shape[1] >= 2:
                    diffs = np.diff(sorted_dist, axis=1)
                    spacing_ok = pd.Series(np.nansum(diffs >= float(spacing_min_pct), axis=1), index=out.index)
                nearest_dist = dist_frame.min(axis=1, skipna=True)
                blocking_dist = (resistance_level / entry_ref.replace(0, np.nan) - 1.0) * 100.0 if side == "long" else (entry_ref / support_level.replace(0, np.nan) - 1.0) * 100.0
                clear_path = ((blocking_dist <= 0.0) | blocking_dist.isna() | (blocking_dist >= nearest_dist)).astype(float)
                score = target_count + rr_count + spacing_ok + clear_path
                base_ok = (target_count >= float(min_targets)) & ((not require_clear_path) | (clear_path >= 1.0))
                if ladder_state <= 1:
                    allow = pattern_event & valid_entry & base_ok & (score >= float(ladder_score_thr))
                else:
                    allow = pattern_event & valid_entry & base_ok & (score <= float(ladder_score_thr))
                return score, allow

            score_long, allow_long = _ladder("long")
            score_short, allow_short = _ladder("short")
            out["F083_PATTERNTPLADDER_ALLOW_LONG"] = np.where(allow_long.fillna(False), 1, 0).astype("int64")
            out["F083_PATTERNTPLADDER_ALLOW_SHORT"] = np.where(allow_short.fillna(False), 1, 0).astype("int64")
            out["F083_PATTERNTPLADDER_ALLOW"] = np.where((allow_long | allow_short).fillna(False), 1, 0).astype("int64")
            out["pattern_tp_ladder_score"] = pd.concat([score_long, score_short], axis=1).max(axis=1).fillna(out["pattern_tp_ladder_score"])

    entry_quality_keys = (
        "F042_level_source_mode",
        "F042_cmp",
        "F042_tp_dist_thr_pct",
        "F043_level_source_mode",
        "F043_cmp",
        "F043_sl_dist_thr_pct",
        "F044_level_source_mode",
        "F044_rr_state",
        "F044_rr_level",
    )
    if any(k in cp_keys for k in entry_quality_keys):
        entry_ref = out["close"].shift(1)
        level_contexts: dict[int, dict[str, pd.Series]] = {}

        def _level_source_mode(prefix: str) -> int:
            raw = int(round(_cp_float(f"{prefix}_level_source_mode", 1.0, min_v=1.0)))
            return min(3, max(1, raw))

        def _context_for_mode(mode_id: int) -> dict[str, pd.Series]:
            if mode_id in level_contexts:
                return level_contexts[mode_id]
            if mode_id == 1:
                levels = [
                    out["low"].rolling(240, min_periods=240).min(),
                    out["high"].rolling(240, min_periods=240).max(),
                ]
            elif mode_id == 2:
                levels = [
                    out["close"] * (1.0 - out["density_vpoc_distance_60"]),
                    out["close"] * (1.0 - out["density_vpoc_distance_240"]),
                ]
            else:
                if "fib_0236" not in out.columns:
                    fib_grid_ctx = _confirmed_fib_anchor_grid_features(
                        out["high"],
                        out["low"],
                        out["close"],
                        max_lookback_bars=240,
                        depth_bars=10,
                        deviation_pct=0.30,
                    )
                    for col in ("fib_0236", "fib_0382", "fib_0500", "fib_0618", "fib_0786"):
                        out[col] = fib_grid_ctx[col]
                levels = [out[col] for col in ("fib_0236", "fib_0382", "fib_0500", "fib_0618", "fib_0786")]
            level_contexts[mode_id] = _nearest_context_from_levels(entry_ref, levels)
            return level_contexts[mode_id]

        def _set_entry_quality_allow(prefix: str, metric_key: str, allow_col: str, threshold: float, is_high_state: bool) -> None:
            ctx = _context_for_mode(_level_source_mode(prefix))
            long_metric = ctx[f"{metric_key}_long"]
            short_metric = ctx[f"{metric_key}_short"]
            long_valid = np.isfinite(long_metric) & (long_metric > 0.0)
            short_valid = np.isfinite(short_metric) & (short_metric > 0.0)
            if is_high_state:
                long_allow = long_valid & (long_metric >= float(threshold))
                short_allow = short_valid & (short_metric >= float(threshold))
            else:
                long_allow = long_valid & (long_metric <= float(threshold))
                short_allow = short_valid & (short_metric <= float(threshold))
            out[f"{allow_col}_LONG"] = np.where(long_allow.fillna(False), 1, 0).astype("int64")
            out[f"{allow_col}_SHORT"] = np.where(short_allow.fillna(False), 1, 0).astype("int64")
            out[allow_col] = np.where((long_allow | short_allow).fillna(False), 1, 0).astype("int64")

        if any(k in cp_keys for k in ("F042_level_source_mode", "F042_cmp", "F042_tp_dist_thr_pct")):
            cmp_raw = _cp_float("F042_cmp", 1.0, min_v=-1.0)
            tp_thr_pct = min(5.0, _cp_float("F042_tp_dist_thr_pct", 0.05, min_v=0.05))
            _set_entry_quality_allow("F042", "tp_dist", "F042_TPCONTEXT_ALLOW", tp_thr_pct, cmp_raw >= 0.0)

        if any(k in cp_keys for k in ("F043_level_source_mode", "F043_cmp", "F043_sl_dist_thr_pct")):
            cmp_raw = _cp_float("F043_cmp", 1.0, min_v=-1.0)
            sl_thr_pct = min(5.0, _cp_float("F043_sl_dist_thr_pct", 0.05, min_v=0.05))
            _set_entry_quality_allow("F043", "sl_dist", "F043_SLCONTEXT_ALLOW", sl_thr_pct, cmp_raw >= 0.0)

        if any(k in cp_keys for k in ("F044_level_source_mode", "F044_rr_state", "F044_rr_level")):
            rr_state_raw = _cp_float("F044_rr_state", 1.0, min_v=-1.0)
            rr_level = min(5.0, _cp_float("F044_rr_level", 0.50, min_v=0.50))
            _set_entry_quality_allow("F044", "rr", "F044_RRCONTEXT_ALLOW", rr_level, rr_state_raw >= 0.0)

    out = out.replace([np.inf, -np.inf], np.nan)

    if include_targets:
        out["future_return"] = out["close"].shift(-horizon_bars) / out["close"] - 1.0
        out["target_up"] = (out["future_return"] > 0).astype(int)
        if include_dropna:
            out = out.dropna().reset_index(drop=True)
        else:
            out = out.reset_index(drop=True)
    else:
        if include_dropna:
            out = out.dropna(subset=FEATURE_COLUMNS).reset_index(drop=True)
        else:
            out = out.reset_index(drop=True)
    return out


RET_N_ACTION_SPECS = [
    {
        "passport_id": "F001",
        "n": 1,
        "move_param": "F001_move",
        "thr_param": "F001_thr_pct",
        "thr_min": 0.01,
        "thr_max": 0.50,
        "column": "F001_RET1_ALLOW",
    },
    {
        "passport_id": "F002",
        "n": 3,
        "move_param": "F002_move",
        "thr_param": "F002_thr_pct",
        "thr_min": 0.02,
        "thr_max": 0.90,
        "column": "F002_RET3_ALLOW",
    },
    {
        "passport_id": "F003",
        "n": 6,
        "move_param": "F003_move",
        "thr_param": "F003_thr_pct",
        "thr_min": 0.03,
        "thr_max": 1.20,
        "column": "F003_RET6_ALLOW",
    },
    {
        "passport_id": "F004",
        "n": 12,
        "move_param": "F004_move",
        "thr_param": "F004_thr_pct",
        "thr_min": 0.05,
        "thr_max": 1.75,
        "column": "F004_RET12_ALLOW",
    },
    {
        "passport_id": "F005",
        "n": 24,
        "move_param": "F005_move",
        "thr_param": "F005_thr_pct",
        "thr_min": 0.10,
        "thr_max": 2.50,
        "column": "F005_RET24_ALLOW",
    },
]


RUNTIME_ACTION_COLUMNS = [
    str(spec["column"])
    for spec in RET_N_ACTION_SPECS
] + [
    "F006_HLSPREAD_ALLOW",
    "F007_RSTD20_ALLOW",
    "F008_ATR14_ALLOW",
    "F009_EMAGAP_ALLOW",
    "F010_EMASLOPE5_ALLOW",
    "F011_EMA200GAP_ALLOW",
    "F012_RSI14_ALLOW",
    "F013_MACDLINE_ALLOW",
    "F014_MACDSIGNAL_ALLOW",
    "F015_MACDHIST_ALLOW",
    "F016_ADX14_ALLOW",
    "F017_F018_STOCH14_ALLOW",
    "F019_VOLCHG_ALLOW",
    "F020_VOLZ20_ALLOW",
    "F021_DELTAVOL_ALLOW",
    "F022_OBVSLOPE5_ALLOW",
    "F023_MFI14_ALLOW",
    "F024_VWAPDIST_ALLOW",
    "F025_VPOCDIST60_ALLOW",
    "F026_BINSHARE60_ALLOW",
    "F027_CLUSTERSHARE60_ALLOW",
    "F028_VPOCSHARE60_ALLOW",
    "F029_VPOCDIST240_ALLOW",
    "F030_BINSHARE240_ALLOW",
    "F031_CLUSTERSHARE240_ALLOW",
    "F032_VPOCSHARE240_ALLOW",
    "F033_VPOCDRIFT20_ALLOW",
    "F034_CLUSTERRATIO_ALLOW",
    "F035_SUPPORTDIST_ALLOW",
    "F036_RESDIST_ALLOW",
    "F037_LEVELSTRENGTH_ALLOW",
    "F038_RANGEPOSE_ALLOW",
    "F039_CHANNELPOS_ALLOW",
    "F040_FIB0382DIST_ALLOW",
    "F041_FIB0618DIST_ALLOW",
    "F042_TPCONTEXT_ALLOW",
    "F042_TPCONTEXT_ALLOW_LONG",
    "F042_TPCONTEXT_ALLOW_SHORT",
    "F043_SLCONTEXT_ALLOW",
    "F043_SLCONTEXT_ALLOW_LONG",
    "F043_SLCONTEXT_ALLOW_SHORT",
    "F044_RRCONTEXT_ALLOW",
    "F044_RRCONTEXT_ALLOW_LONG",
    "F044_RRCONTEXT_ALLOW_SHORT",
    "F045_BREAKOUT_ALLOW",
    "F046_FALSEBREAK_ALLOW",
    "F047_RETEST_ALLOW",
    "F048_SWINGHIGHBREAK_ALLOW",
    "F049_SWINGLOWBREAK_ALLOW",
    "F050_BOSUP_ALLOW",
    "F051_BOSDOWN_ALLOW",
    "F052_CHOCH_ALLOW",
    "F053_DOJI_ALLOW",
    "F054_INSIDEBAR_ALLOW",
    "F055_PINBULL_ALLOW",
    "F056_PINBEAR_ALLOW",
    "F057_HAMMER_ALLOW",
    "F058_SHOOTINGSTAR_ALLOW",
    "F059_ENGULFBULL_ALLOW",
    "F060_ENGULFBEAR_ALLOW",
    "F061_RSIBULLDIV_ALLOW",
    "F062_RSIBEARDIV_ALLOW",
    "F063_MACDBULLDIV_ALLOW",
    "F064_MACDBEARDIV_ALLOW",
    "F065_OBVBULLDIV_ALLOW",
    "F066_OBVBEARDIV_ALLOW",
    "F067_PATTERNSTRENGTH_ALLOW",
    "F068_PATTERNAGE_ALLOW",
    "F069_DOUBLEBOTTOM_ALLOW",
    "F070_DOUBLETOP_ALLOW",
    "F071_HEADSHOULDERS_ALLOW",
    "F072_INVHEADSHOULDERS_ALLOW",
    "F073_TRIANGLE_ALLOW",
    "F074_PENNANT_ALLOW",
    "F075_WEDGERISING_ALLOW",
    "F076_WEDGEFALLING_ALLOW",
    "F077_RANGEFLAG_ALLOW",
    "F078_PATTERNVOLCONF_ALLOW",
    "F079_PATTERNLEVELCONF_ALLOW",
    "F080_PATTERNLONG_ALLOW",
    "F081_PATTERNSHORT_ALLOW",
    "F082_PATTERNSLBUF_ALLOW",
    "F082_PATTERNSLBUF_ALLOW_LONG",
    "F082_PATTERNSLBUF_ALLOW_SHORT",
    "F083_PATTERNTPLADDER_ALLOW",
    "F083_PATTERNTPLADDER_ALLOW_LONG",
    "F083_PATTERNTPLADDER_ALLOW_SHORT",
]


FEATURE_COLUMNS = [
    "ret_1",
    "ret_3",
    "ret_6",
    "ret_12",
    "ret_24",
    "hl_spread",
    "rolling_std_20",
    "atr14",
    "vol_chg",
    "vol_z",
    "delta_volume",
    "obv_slope_5",
    "mfi14",
    "ema_gap",
    "ema_slope_5",
    "ema200_gap",
    "rsi14",
    "macd_line",
    "macd_signal",
    "macd_hist",
    "adx14",
    "stoch_k14",
    "stoch_d14",
    "vwap_distance",
    "support_distance",
    "resistance_distance",
    "level_strength",
    "position_in_range",
    "trend_channel_pos",
    "fib_0382_distance",
    "fib_0618_distance",
    "tp_context_distance",
    "sl_context_distance",
    "rr_context_estimate",
    "breakout_flag",
    "false_breakout_flag",
    "retest_flag",
    "swing_high_break_flag",
    "swing_low_break_flag",
    "bos_up_flag",
    "bos_down_flag",
    "choch_flag",
    "doji_flag",
    "inside_bar_flag",
    "pin_bar_bull_flag",
    "pin_bar_bear_flag",
    "hammer_flag",
    "shooting_star_flag",
    "engulf_bull_flag",
    "engulf_bear_flag",
    "double_bottom_flag",
    "double_top_flag",
    "head_shoulders_flag",
    "inverse_head_shoulders_flag",
    "triangle_flag",
    "pennant_flag",
    "wedge_rising_flag",
    "wedge_falling_flag",
    "range_flag",
    "pattern_volume_confirm_flag",
    "pattern_level_confirm_flag",
    "pattern_structure_volume_entry_long",
    "pattern_structure_volume_entry_short",
    "pattern_sl_buffer_distance",
    "pattern_tp_ladder_score",
    "rsi_bull_div_flag",
    "rsi_bear_div_flag",
    "macd_bull_div_flag",
    "macd_bear_div_flag",
    "obv_bull_div_flag",
    "obv_bear_div_flag",
    "pattern_strength",
    "pattern_age_bars",
    "density_vpoc_distance_60",
    "density_bin_share_60",
    "density_cluster_share_60",
    "density_vpoc_share_60",
    "density_vpoc_distance_240",
    "density_bin_share_240",
    "density_cluster_share_240",
    "density_vpoc_share_240",
    "density_vpoc_drift_20",
    "density_cluster_ratio_60_240",
]


FEATURE_GROUPS: dict[str, list[str]] = {
    "price_volatility": [
        "ret_1",
        "ret_3",
        "ret_6",
        "ret_12",
        "ret_24",
        "hl_spread",
        "rolling_std_20",
        "atr14",
    ],
    "trend_momentum": [
        "ema_gap",
        "ema_slope_5",
        "ema200_gap",
        "rsi14",
        "macd_line",
        "macd_signal",
        "macd_hist",
        "adx14",
        "stoch_k14",
        "stoch_d14",
    ],
    "volume_flow": [
        "vol_chg",
        "vol_z",
        "delta_volume",
        "obv_slope_5",
        "mfi14",
        "vwap_distance",
    ],
    "density_profile": [
        "density_vpoc_distance_60",
        "density_bin_share_60",
        "density_cluster_share_60",
        "density_vpoc_share_60",
        "density_vpoc_distance_240",
        "density_bin_share_240",
        "density_cluster_share_240",
        "density_vpoc_share_240",
        "density_vpoc_drift_20",
        "density_cluster_ratio_60_240",
    ],
    "structure_ta": [
        "support_distance",
        "resistance_distance",
        "level_strength",
        "position_in_range",
        "trend_channel_pos",
        "fib_0382_distance",
        "fib_0618_distance",
        "tp_context_distance",
        "sl_context_distance",
        "rr_context_estimate",
        "breakout_flag",
        "false_breakout_flag",
        "retest_flag",
        "swing_high_break_flag",
        "swing_low_break_flag",
        "bos_up_flag",
        "bos_down_flag",
        "choch_flag",
    ],
    "pattern": [
        "doji_flag",
        "inside_bar_flag",
        "pin_bar_bull_flag",
        "pin_bar_bear_flag",
        "hammer_flag",
        "shooting_star_flag",
        "engulf_bull_flag",
        "engulf_bear_flag",
        "double_bottom_flag",
        "double_top_flag",
        "head_shoulders_flag",
        "inverse_head_shoulders_flag",
        "triangle_flag",
        "pennant_flag",
        "wedge_rising_flag",
        "wedge_falling_flag",
        "range_flag",
        "pattern_volume_confirm_flag",
        "pattern_level_confirm_flag",
        "pattern_structure_volume_entry_long",
        "pattern_structure_volume_entry_short",
        "pattern_sl_buffer_distance",
        "pattern_tp_ladder_score",
        "rsi_bull_div_flag",
        "rsi_bear_div_flag",
        "macd_bull_div_flag",
        "macd_bear_div_flag",
        "obv_bull_div_flag",
        "obv_bear_div_flag",
        "pattern_strength",
        "pattern_age_bars",
    ],
}


def _bars_since_event(event_flag: pd.Series) -> pd.Series:
    idx = np.arange(len(event_flag), dtype=float)
    event_idx = np.where(event_flag.values > 0, idx, np.nan)
    last_event_idx = pd.Series(event_idx).ffill().to_numpy()
    age = idx - last_event_idx
    age[np.isnan(last_event_idx)] = np.nan
    return pd.Series(age, index=event_flag.index)
