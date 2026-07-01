from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from mlbotnav.dataset import FEATURE_COLUMNS, FEATURE_GROUPS, build_feature_frame, load_ohlcv_range
from mlbotnav.timeframes import timeframe_aliases, timeframe_delta


class StableOutputLockError(RuntimeError):
    """Raised when stable output directory cannot be cleaned due to file lock."""

    def __init__(self, path: Path, retries: int, last_error: Exception, fallback_error: Exception):
        super().__init__(
            f"file_locked: failed to clean stable output dir '{path}' after {retries} retries; "
            f"last_error='{last_error}'; fallback_error='{fallback_error}'"
        )
        self.path = str(path)
        self.retries = int(retries)
        self.last_error = str(last_error)
        self.fallback_error = str(fallback_error)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _utc_now_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _iter_days(start_date: str, end_date: str) -> list[str]:
    days = pd.date_range(start=start_date, end=end_date, freq="D")
    return [d.strftime("%Y-%m-%d") for d in days]


def _sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _find_day_file(project_root: Path, *, layer: str, day: str, tf: str, symbol: str) -> Path | None:
    for tf_label in timeframe_aliases(tf):
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
            return p
    return None


def _row_hash(row: pd.Series) -> str:
    raw = "|".join(
        [
            str(row.get("symbol", "")),
            str(row.get("timeframe", "")),
            str(row.get("open_time_utc", "")),
            f"{float(row.get('open', 0.0)):.12f}",
            f"{float(row.get('high', 0.0)):.12f}",
            f"{float(row.get('low', 0.0)):.12f}",
            f"{float(row.get('close', 0.0)):.12f}",
            f"{float(row.get('volume', 0.0)):.12f}",
            f"{float(row.get('turnover', 0.0)):.12f}",
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _canonicalize_candles(df: pd.DataFrame, *, symbol: str, timeframe: str) -> pd.DataFrame:
    out = df.copy()
    out["symbol"] = out.get("symbol", symbol)
    out["timeframe"] = out.get("timeframe", timeframe)
    out["open_time_utc"] = pd.to_datetime(out["open_time_utc"], utc=True, errors="coerce")
    out["close_time_utc"] = pd.to_datetime(out["close_time_utc"], utc=True, errors="coerce")
    out = out.dropna(subset=["open_time_utc", "close_time_utc"]).copy()
    out = out.sort_values("open_time_utc").drop_duplicates(subset=["open_time_utc"], keep="last").reset_index(drop=True)
    out["source"] = "bybit_v5"
    out["row_hash"] = out.apply(_row_hash, axis=1)
    cols = [
        "symbol",
        "timeframe",
        "open_time_utc",
        "close_time_utc",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "turnover",
        "exchange",
        "market_type",
        "ingest_run_id",
        "source_ts_utc",
        "source",
        "row_hash",
    ]
    for c in cols:
        if c not in out.columns:
            out[c] = None
    return out[cols].copy()


def _daily_parity_report(
    project_root: Path,
    candles: pd.DataFrame,
    *,
    symbol: str,
    timeframe: str,
    start_date: str,
    end_date: str,
) -> tuple[pd.DataFrame, dict]:
    step_sec = int(timeframe_delta(timeframe).total_seconds())
    rows: list[dict] = []
    manifest: list[dict] = []

    for day in _iter_days(start_date, end_date):
        raw_path = _find_day_file(project_root, layer="raw", day=day, tf=timeframe, symbol=symbol)
        core_path = _find_day_file(project_root, layer="core", day=day, tf=timeframe, symbol=symbol)

        d0 = pd.Timestamp(day, tz="UTC")
        d1 = d0 + pd.Timedelta(days=1)
        day_df = candles[(candles["open_time_utc"] >= d0) & (candles["open_time_utc"] < d1)].copy()
        day_df = day_df.sort_values("open_time_utc")
        actual_rows = int(len(day_df))
        expected_rows = int((24 * 3600) / step_sec)
        duplicates = int(day_df["open_time_utc"].duplicated().sum())

        gap_count = 0
        if actual_rows > 1:
            dt = day_df["open_time_utc"].diff().dropna().dt.total_seconds()
            gap_count = int((dt != step_sec).sum())

        raw_rows = None
        core_rows = None
        raw_core_ohlcv_mismatch_rows = None
        raw_missing_in_core = None
        core_missing_in_raw = None

        if raw_path and core_path:
            raw_df = pd.read_csv(raw_path)
            core_df = pd.read_csv(core_path)
            raw_df["open_time_utc"] = pd.to_datetime(raw_df["open_time_utc"], utc=True, errors="coerce")
            core_df["open_time_utc"] = pd.to_datetime(core_df["open_time_utc"], utc=True, errors="coerce")
            raw_df = raw_df.dropna(subset=["open_time_utc"]).drop_duplicates(subset=["open_time_utc"]).sort_values("open_time_utc")
            core_df = core_df.dropna(subset=["open_time_utc"]).drop_duplicates(subset=["open_time_utc"]).sort_values("open_time_utc")
            raw_rows = int(len(raw_df))
            core_rows = int(len(core_df))
            m = raw_df.merge(core_df, on="open_time_utc", suffixes=("_raw", "_core"), how="outer", indicator=True)
            raw_missing_in_core = int((m["_merge"] == "left_only").sum())
            core_missing_in_raw = int((m["_merge"] == "right_only").sum())
            both = m[m["_merge"] == "both"].copy()
            mismatch = pd.Series(False, index=both.index)
            for c in ["open", "high", "low", "close", "volume", "turnover"]:
                x = pd.to_numeric(both[f"{c}_raw"], errors="coerce")
                y = pd.to_numeric(both[f"{c}_core"], errors="coerce")
                mismatch = mismatch | (~np.isclose(x, y, rtol=0.0, atol=1e-12, equal_nan=True))
            raw_core_ohlcv_mismatch_rows = int(mismatch.sum())

        manifest.append(
            {
                "day": day,
                "raw_path": str(raw_path) if raw_path else None,
                "raw_sha256": _sha256_path(raw_path) if raw_path and raw_path.exists() else None,
                "core_path": str(core_path) if core_path else None,
                "core_sha256": _sha256_path(core_path) if core_path and core_path.exists() else None,
            }
        )

        rows.append(
            {
                "day": day,
                "timeframe": timeframe,
                "symbol": symbol,
                "expected_rows": expected_rows,
                "actual_rows": actual_rows,
                "missing_rows_vs_expected": max(expected_rows - actual_rows, 0),
                "duplicates": duplicates,
                "gap_count": gap_count,
                "raw_rows": raw_rows,
                "core_rows": core_rows,
                "raw_missing_in_core": raw_missing_in_core,
                "core_missing_in_raw": core_missing_in_raw,
                "raw_core_ohlcv_mismatch_rows": raw_core_ohlcv_mismatch_rows,
                "parity_pass": bool(
                    (duplicates == 0)
                    and (gap_count == 0)
                    and (actual_rows == expected_rows)
                    and (raw_core_ohlcv_mismatch_rows in (0, None))
                    and (raw_missing_in_core in (0, None))
                    and (core_missing_in_raw in (0, None))
                ),
            }
        )

    daily = pd.DataFrame(rows).sort_values("day").reset_index(drop=True)
    summary = {
        "symbol": symbol,
        "timeframe": timeframe,
        "start_date": start_date,
        "end_date": end_date,
        "days_total": int(len(daily)),
        "days_passed": int(daily["parity_pass"].sum()) if len(daily) else 0,
        "days_failed": int((~daily["parity_pass"]).sum()) if len(daily) else 0,
        "any_fail": bool((~daily["parity_pass"]).any()) if len(daily) else False,
        "snapshot_manifest": manifest,
    }
    return daily, summary


def _feature_formula_map() -> dict[str, str]:
    return {
        "ret_1": "close(t)/close(t-1)-1",
        "ret_3": "close(t)/close(t-3)-1",
        "ret_6": "close(t)/close(t-6)-1",
        "ret_12": "close(t)/close(t-12)-1",
        "ret_24": "close(t)/close(t-24)-1",
        "hl_spread": "(high-low)/open",
        "rolling_std_20": "std(ret_1, window=20)",
        "atr14": "ATR(14)/close",
        "vol_chg": "volume(t)/volume(t-1)-1",
        "vol_z": "zscore(volume,20)",
        "delta_volume": "volume(t)-volume(t-1)",
        "obv_slope_5": "pct_change(OBV,5)",
        "mfi14": "MFI(14)",
        "ema_gap": "(ema20-ema50)/close",
        "ema_slope_5": "pct_change(ema20,5)",
        "ema200_gap": "(close-ema200)/close",
        "rsi14": "RSI(14)",
        "macd_line": "EMA12-EMA26",
        "macd_signal": "EMA(macd_line,9)",
        "macd_hist": "macd_line-macd_signal",
        "adx14": "ADX(14)",
        "stoch_k14": "100*(close-LL14)/(HH14-LL14)",
        "stoch_d14": "SMA(stoch_k14,3)",
        "vwap_distance": "(close-vwap)/close",
        "support_distance": "(close-roll_min_20)/close",
        "resistance_distance": "(roll_max_20-close)/close",
        "level_strength": "rolling touch score",
        "position_in_range": "(close-roll_min_20)/(roll_max_20-roll_min_20)",
        "trend_channel_pos": "(close-channel_low_50)/(channel_high_50-channel_low_50)",
        "fib_0382_distance": "(close-fib_0382)/close",
        "fib_0618_distance": "(close-fib_0618)/close",
        "tp_context_distance": "resistance_distance",
        "sl_context_distance": "support_distance",
        "rr_context_estimate": "tp_context_distance/sl_context_distance",
        "breakout_flag": "breakout_up OR breakout_down",
        "false_breakout_flag": "prev breakout reverted",
        "retest_flag": "post-breakout retest near level",
        "swing_high_break_flag": "high > rolling_max(10)_prev",
        "swing_low_break_flag": "low < rolling_min(10)_prev",
        "bos_up_flag": "swing_high_break AND ema_slope_5>0",
        "bos_down_flag": "swing_low_break AND ema_slope_5<0",
        "choch_flag": "sign change of ema_gap trend",
        "doji_flag": "abs(body)/range <= 0.1",
        "inside_bar_flag": "high<=prev_high AND low>=prev_low",
        "pin_bar_bull_flag": "lower_wick > 2*body AND upper_wick < body",
        "pin_bar_bear_flag": "upper_wick > 2*body AND lower_wick < body",
        "hammer_flag": "lower_wick > 2.2*body AND upper_wick < 0.8*body",
        "shooting_star_flag": "upper_wick > 2.2*body AND lower_wick < 0.8*body",
        "engulf_bull_flag": "bull engulf previous body",
        "engulf_bear_flag": "bear engulf previous body",
        "rsi_bull_div_flag": "close<close(-10) AND rsi>rsi(-10)",
        "rsi_bear_div_flag": "close>close(-10) AND rsi<rsi(-10)",
        "macd_bull_div_flag": "close<close(-10) AND macd_hist>macd_hist(-10)",
        "macd_bear_div_flag": "close>close(-10) AND macd_hist<macd_hist(-10)",
        "obv_bull_div_flag": "close<close(-10) AND obv>obv(-10)",
        "obv_bear_div_flag": "close>close(-10) AND obv<obv(-10)",
        "pattern_strength": "sum of candle pattern flags",
        "pattern_age_bars": "bars since last pattern event",
        "density_vpoc_distance_60": "(close-vpoc_60)/close",
        "density_bin_share_60": "volume share of current bin (60)",
        "density_cluster_share_60": "volume share of bin cluster (60)",
        "density_vpoc_share_60": "vpoc volume share (60)",
        "density_vpoc_distance_240": "(close-vpoc_240)/close",
        "density_bin_share_240": "volume share of current bin (240)",
        "density_cluster_share_240": "volume share of bin cluster (240)",
        "density_vpoc_share_240": "vpoc volume share (240)",
        "density_vpoc_drift_20": "vpoc_distance_60 - vpoc_distance_60(-20)",
        "density_cluster_ratio_60_240": "density_cluster_share_60 / density_cluster_share_240",
    }


def _build_feature_dictionary(project_root: Path) -> pd.DataFrame:
    cfg_path = project_root / "configs" / "features_block.yaml"
    ru_feature_names: dict[str, str] = {}
    if cfg_path.exists():
        cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
        ru_feature_names = (((cfg.get("ru_labels") or {}).get("feature_columns")) or {})

    group_map: dict[str, str] = {}
    for group, cols in FEATURE_GROUPS.items():
        for c in cols:
            group_map[c] = group

    formula_map = _feature_formula_map()
    rows: list[dict] = []
    for c in FEATURE_COLUMNS:
        rows.append(
            {
                "column_name_en": c,
                "column_name_ru": ru_feature_names.get(c, c),
                "block": group_map.get(c, "unknown"),
                "formula_text": formula_map.get(c, "see dataset.build_feature_frame"),
                "units": "ratio_or_flag",
                "computed_on": "close(t)",
                "used_in": "train,signal,backtest,report",
                "lookahead_safe": True,
                "notes": "",
            }
        )

    rows.extend(
        [
            {
                "column_name_en": "future_return",
                "column_name_ru": "Доходность будущего горизонта",
                "block": "target",
                "formula_text": "close(t+h)/close(t)-1",
                "units": "ratio",
                "computed_on": "post_close_label",
                "used_in": "train_label",
                "lookahead_safe": False,
                "notes": "Label only, not for real-time signal",
            },
            {
                "column_name_en": "target_up",
                "column_name_ru": "Цель вверх",
                "block": "target",
                "formula_text": "future_return > 0",
                "units": "binary_flag",
                "computed_on": "post_close_label",
                "used_in": "train_label",
                "lookahead_safe": False,
                "notes": "Label only, not for real-time signal",
            },
        ]
    )
    return pd.DataFrame(rows)


def _save_with_fallback_parquet(df: pd.DataFrame, csv_path: Path, parquet_path: Path) -> tuple[Path, Path | None]:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    pq_saved: Path | None = None
    try:
        df.to_parquet(parquet_path, index=False)
        pq_saved = parquet_path
    except Exception:
        pq_saved = None
    return csv_path, pq_saved


def _save_excel_friendly_csv(df: pd.DataFrame, src_csv_path: Path) -> Path:
    """
    RU Excel often expects ';' as delimiter. Save an additional UTF-8 BOM CSV
    that opens into columns without manual 'Text to Columns'.
    """
    out = src_csv_path.with_name(f"{src_csv_path.stem}_excel.csv")
    df.to_csv(out, index=False, sep=";", encoding="utf-8-sig")
    return out


def _build_index(run_dir: Path) -> dict:
    out: list[dict] = []
    for p in sorted(run_dir.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(run_dir).as_posix()
        out.append(
            {
                "path": rel,
                "bytes": int(p.stat().st_size),
                "sha256": _sha256_path(p),
            }
        )
    return {"files": out, "files_count": len(out)}


def _remove_tree_with_retry(path: Path, *, retries: int = 8, base_sleep_sec: float = 0.35) -> None:
    """
    Windows-safe recursive delete for stable output dir.
    Handles transient WinError 32 (file is locked by Excel/AV/indexer).
    """
    if not path.exists():
        return

    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            shutil.rmtree(path)
            return
        except FileNotFoundError:
            return
        except PermissionError as exc:
            last_exc = exc
        except OSError as exc:
            # WinError 32: file is being used by another process.
            if getattr(exc, "winerror", None) == 32:
                last_exc = exc
            else:
                raise
        time.sleep(base_sleep_sec * attempt)

    # Final fallback: move locked dir away so pipeline can continue cleanly.
    parked = path.parent / f"{path.name}_locked_{_utc_now_tag()}"
    try:
        path.rename(parked)
        return
    except Exception as exc:
        if last_exc is not None:
            raise StableOutputLockError(
                path=path,
                retries=retries,
                last_error=last_exc,
                fallback_error=exc,
            ) from exc
        raise


def _build_candles_dictionary() -> pd.DataFrame:
    rows = [
        ("symbol", "Торговая пара", "Идентификатор инструмента"),
        ("timeframe", "Таймфрейм", "Шаг свечи, например 1m"),
        ("open_time_utc", "Время открытия (UTC)", "Начало свечи в UTC"),
        ("close_time_utc", "Время закрытия (UTC)", "Конец свечи в UTC"),
        ("open", "Цена открытия", "Первая цена свечи"),
        ("high", "Максимум", "Максимальная цена за свечу"),
        ("low", "Минимум", "Минимальная цена за свечу"),
        ("close", "Цена закрытия", "Последняя цена свечи"),
        ("volume", "Объем", "Торговый объем за свечу"),
        ("turnover", "Оборот", "Оборот (quote volume)"),
        ("exchange", "Биржа", "Источник данных"),
        ("market_type", "Тип рынка", "Например linear/spot"),
        ("ingest_run_id", "ID инжеста", "Идентификатор загрузки"),
        ("source_ts_utc", "Время источника (UTC)", "Время получения данных"),
        ("source", "Источник", "Метка источника"),
        ("row_hash", "Хэш строки", "SHA256-контроль целостности"),
    ]
    return pd.DataFrame(rows, columns=["column_name_en", "column_name_ru", "notes"])
def main() -> int:
    parser = argparse.ArgumentParser(description="P1+P2: candles canonical parity + feature frame/dictionary pack")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--horizon-bars", type=int, default=1)
    parser.add_argument("--layer", default="raw", choices=["raw", "core"])
    parser.add_argument("--output-mode", default="stable", choices=["stable", "run"], help="stable=overwrite one folder, run=create unique run folder")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    run_id = (
        f"run_{_utc_now_tag()}_{str(args.symbol).lower()}_{str(args.timeframe).lower()}_"
        f"{args.start_date}_to_{args.end_date}_tablecanon_{uuid.uuid4().hex[:6]}"
    )
    if str(args.output_mode) == "stable":
        run_dir = project_root / "reports" / "table_canon_current"
        if run_dir.exists():
            try:
                _remove_tree_with_retry(run_dir)
            except StableOutputLockError as exc:
                print(
                    json.dumps(
                        {
                            "status": "FAIL",
                            "error_code": "file_locked",
                            "error": str(exc),
                            "stable_output_dir": exc.path,
                            "retries": exc.retries,
                            "last_error": exc.last_error,
                            "fallback_error": exc.fallback_error,
                        },
                        ensure_ascii=False,
                    )
                )
                return 2
    else:
        run_dir = project_root / "reports" / "runs" / run_id
    state_dir = run_dir / "state"
    data_dir = run_dir / "data"
    state_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    params = {
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "start_date": args.start_date,
        "end_date": args.end_date,
        "horizon_bars": int(args.horizon_bars),
        "layer": args.layer,
    }
    _write_json(state_dir / "params_snapshot.json", params)
    _write_json(
        state_dir / "run_manifest.json",
        {
            "run_id": run_id,
            "kind": "table_canon_pack",
            "created_at_utc": _utc_now_iso(),
            "active_tz": "docs/TZ_TABLE_CANON_BYBIT_PARITY_2026-05-23_RU.md",
            "active_lock": "docs/TZ_ACTIVE_LOCK_2026-05-23_RU.md",
            "params": params,
        },
    )
    _write_json(state_dir / "status.json", {"status": "running", "updated_at_utc": _utc_now_iso(), "active_step": "P1+P2"})

    raw_df = load_ohlcv_range(
        project_root,
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=args.start_date,
        end_date=args.end_date,
        layer=args.layer,
    )
    candles = _canonicalize_candles(raw_df, symbol=args.symbol, timeframe=args.timeframe)
    candles_csv, candles_pq = _save_with_fallback_parquet(
        candles,
        data_dir / "candles_canonical.csv",
        data_dir / "candles_canonical.parquet",
    )
    candles_csv_std = data_dir / "candles_canonical_std.csv"
    shutil.copy2(candles_csv, candles_csv_std)
    # Overwrite canonical CSV with RU Excel-friendly delimiter.
    candles.to_csv(candles_csv, index=False, sep=";", encoding="utf-8-sig")
    candles_csv_excel = _save_excel_friendly_csv(candles, candles_csv)

    parity_daily, parity_summary = _daily_parity_report(
        project_root,
        candles,
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=args.start_date,
        end_date=args.end_date,
    )
    parity_daily.to_csv(data_dir / "candles_parity_daily.csv", index=False)
    _write_json(data_dir / "raw_snapshot_manifest.json", {"snapshot": parity_summary.get("snapshot_manifest", [])})
    _write_json(
        data_dir / "candles_parity_report.json",
        {
            **parity_summary,
            "generated_at_utc": _utc_now_iso(),
            "candles_rows": int(len(candles)),
            "candles_csv": str(candles_csv),
            "candles_parquet": str(candles_pq) if candles_pq else None,
        },
    )

    feat_full = build_feature_frame(
        raw_df,
        horizon_bars=int(args.horizon_bars),
        include_targets=True,
        include_dropna=False,
    )
    feat_full["run_id"] = run_id
    feat_train = feat_full.dropna().reset_index(drop=True)

    feat_csv, feat_pq = _save_with_fallback_parquet(
        feat_train,
        data_dir / "feature_frame.csv",
        data_dir / "feature_frame.parquet",
    )
    feat_csv_std = data_dir / "feature_frame_std.csv"
    shutil.copy2(feat_csv, feat_csv_std)
    # Overwrite canonical CSV with RU Excel-friendly delimiter.
    feat_train.to_csv(feat_csv, index=False, sep=";", encoding="utf-8-sig")
    feat_csv_excel = _save_excel_friendly_csv(feat_train, feat_csv)

    feat_full_csv, feat_full_pq = _save_with_fallback_parquet(
        feat_full,
        data_dir / "feature_frame_full.csv",
        data_dir / "feature_frame_full.parquet",
    )
    feat_full.to_csv(feat_full_csv, index=False, sep=";", encoding="utf-8-sig")
    feat_full_csv_excel = _save_excel_friendly_csv(feat_full, feat_full_csv)

    fdict = _build_feature_dictionary(project_root)
    fdict_features = fdict[fdict["block"] != "target"].copy()
    fdict_targets = fdict[fdict["block"] == "target"].copy()
    candles_dict = _build_candles_dictionary()
    fdict_csv = data_dir / "feature_dictionary_ru.csv"
    fdict_xlsx = data_dir / "feature_dictionary_ru.xlsx"
    fdict_targets_csv = data_dir / "targets_dictionary_ru.csv"
    candles_dict_csv = data_dir / "candles_dictionary_ru.csv"
    fdict_features.to_csv(fdict_csv, index=False)
    fdict_targets.to_csv(fdict_targets_csv, index=False)
    candles_dict.to_csv(candles_dict_csv, index=False)
    _save_excel_friendly_csv(fdict_features, fdict_csv)
    _save_excel_friendly_csv(fdict_targets, fdict_targets_csv)
    _save_excel_friendly_csv(candles_dict, candles_dict_csv)

    readable_xlsx = data_dir / "readable_tables_ru.xlsx"
    run_summary = pd.DataFrame(
        [
            ["run_id", run_id],
            ["symbol", args.symbol],
            ["timeframe", args.timeframe],
            ["start_date", args.start_date],
            ["end_date", args.end_date],
            ["candles_rows", int(len(candles))],
            ["feature_rows_full", int(len(feat_full))],
            ["feature_rows_train", int(len(feat_train))],
            ["feature_rows_dropped", int(len(feat_full) - len(feat_train))],
            ["feature_columns_count", int(len(FEATURE_COLUMNS))],
            ["parity_fail", bool(parity_summary["any_fail"])],
        ],
        columns=["key", "value"],
    )

    candles_view = candles.copy()
    candles_view["open_time_utc"] = candles_view["open_time_utc"].astype(str)
    candles_view["close_time_utc"] = candles_view["close_time_utc"].astype(str)
    feat_view = feat_full.copy()
    if "open_time_utc" in feat_view.columns:
        feat_view["open_time_utc"] = feat_view["open_time_utc"].astype(str)
    if "close_time_utc" in feat_view.columns:
        feat_view["close_time_utc"] = feat_view["close_time_utc"].astype(str)
    feat_train_view = feat_train.copy()
    if "open_time_utc" in feat_train_view.columns:
        feat_train_view["open_time_utc"] = feat_train_view["open_time_utc"].astype(str)
    if "close_time_utc" in feat_train_view.columns:
        feat_train_view["close_time_utc"] = feat_train_view["close_time_utc"].astype(str)

    with pd.ExcelWriter(fdict_xlsx, engine="xlsxwriter") as w:
        fdict_features.to_excel(w, sheet_name="features_dictionary", index=False)
        fdict_targets.to_excel(w, sheet_name="targets_dictionary", index=False)

    candles_xlsx = data_dir / "candles_canonical.xlsx"
    feature_frame_xlsx = data_dir / "feature_frame.xlsx"
    feature_frame_full_xlsx = data_dir / "feature_frame_full.xlsx"
    with pd.ExcelWriter(candles_xlsx, engine="xlsxwriter") as w:
        candles_view.to_excel(w, sheet_name="candles_canonical", index=False)
    with pd.ExcelWriter(feature_frame_xlsx, engine="xlsxwriter") as w:
        feat_train_view.to_excel(w, sheet_name="feature_frame", index=False)
    with pd.ExcelWriter(feature_frame_full_xlsx, engine="xlsxwriter") as w:
        feat_view.to_excel(w, sheet_name="feature_frame_full", index=False)

    with pd.ExcelWriter(readable_xlsx, engine="xlsxwriter") as w:
        run_summary.to_excel(w, sheet_name="summary", index=False)
        candles_view.to_excel(w, sheet_name="candles_canonical", index=False)
        feat_train_view.to_excel(w, sheet_name="feature_frame", index=False)
        feat_view.to_excel(w, sheet_name="feature_frame_full", index=False)
        fdict_features.to_excel(w, sheet_name="feature_dictionary_ru", index=False)
        fdict_targets.to_excel(w, sheet_name="targets_dictionary_ru", index=False)
        candles_dict.to_excel(w, sheet_name="candles_dictionary_ru", index=False)

    _write_json(
        data_dir / "feature_frame_quality.json",
        {
            "run_id": run_id,
            "rows_full": int(len(feat_full)),
            "rows_train": int(len(feat_train)),
            "rows_dropped_for_train": int(len(feat_full) - len(feat_train)),
            "drop_policy": "dropna on full feature set + target labels",
            "note": "Use feature_frame_full for continuity audit; use feature_frame for ML-ready rows.",
            "generated_at_utc": _utc_now_iso(),
        },
    )

    index_payload = _build_index(run_dir)
    _write_json(run_dir / "index.json", index_payload)
    _write_json(
        state_dir / "status.json",
        {
            "status": "completed",
            "updated_at_utc": _utc_now_iso(),
            "active_step": "P1+P2",
            "rows": {
                "candles": int(len(candles)),
                "feature_frame_full": int(len(feat_full)),
                "feature_frame_train": int(len(feat_train)),
                "dictionary_features": int(len(fdict_features)),
            },
            "parity": {
                "days_total": parity_summary["days_total"],
                "days_failed": parity_summary["days_failed"],
                "any_fail": parity_summary["any_fail"],
            },
        },
    )

    print(
        json.dumps(
            {
                "run_id": run_id,
                "run_dir": str(run_dir),
                "candles_csv": str(candles_csv),
                "candles_csv_std": str(candles_csv_std),
                "candles_csv_excel": str(candles_csv_excel),
                "candles_xlsx": str(candles_xlsx),
                "feature_frame_csv": str(feat_csv),
                "feature_frame_csv_std": str(feat_csv_std),
                "feature_frame_csv_excel": str(feat_csv_excel),
                "feature_frame_xlsx": str(feature_frame_xlsx),
                "feature_frame_full_csv": str(feat_full_csv),
                "feature_frame_full_csv_excel": str(feat_full_csv_excel),
                "feature_frame_full_parquet": str(feat_full_pq) if feat_full_pq else None,
                "feature_frame_full_xlsx": str(feature_frame_full_xlsx),
                "feature_dictionary_xlsx": str(fdict_xlsx),
                "targets_dictionary_csv": str(fdict_targets_csv),
                "feature_quality_report": str(data_dir / "feature_frame_quality.json"),
                "readable_tables_xlsx": str(readable_xlsx),
                "parity_report": str(data_dir / "candles_parity_report.json"),
                "parity_fail": bool(parity_summary["any_fail"]),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
