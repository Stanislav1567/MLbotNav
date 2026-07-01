from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from mlbotnav.dataset import FEATURE_COLUMNS
from mlbotnav.runtime_contract import CALIBRATION_MODE_NONE, SIGNAL_CONTRACT_VERSION
from mlbotnav.timeframes import timeframe_delta


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_csv_auto(path: Path) -> tuple[pd.DataFrame, str]:
    for sep in (";", ","):
        try:
            df = pd.read_csv(path, sep=sep)
            if df.shape[1] > 1:
                return df, sep
        except Exception:
            continue
    return pd.read_csv(path), ","


def _read_xlsx_auto(path: Path, sheet_name: str | None = None) -> pd.DataFrame:
    if sheet_name:
        try:
            return pd.read_excel(path, sheet_name=sheet_name)
        except Exception:
            pass
    return pd.read_excel(path)


def _check(name: str, ok: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": details or {}}


def _allclose_series(a: pd.Series, b: pd.Series, atol: float = 1e-9) -> tuple[bool, int]:
    av = pd.to_numeric(a, errors="coerce")
    bv = pd.to_numeric(b, errors="coerce")
    diff = (av - bv).abs()
    bad = int((diff > float(atol)).sum())
    return bad == 0, bad


def _numeric_clean_check(df: pd.DataFrame, cols: list[str]) -> tuple[bool, dict[str, int]]:
    bad_map: dict[str, int] = {}
    ok = True
    for c in cols:
        if c not in df.columns:
            continue
        s = pd.to_numeric(df[c], errors="coerce")
        finite = s.notna() & ~s.isin([float("inf"), float("-inf")])
        bad = int((~finite).sum())
        bad_map[c] = bad
        if bad > 0:
            ok = False
    return ok, bad_map


def _utc_suffix_bad_count(df: pd.DataFrame, col: str) -> int:
    if col not in df.columns:
        return 0
    s = df[col].astype(str).str.strip()
    s = s[s.ne("") & s.ne("nan") & s.ne("NaT")]
    if len(s) == 0:
        return 0
    return int((~s.str.contains(r"\+00:00$", regex=True)).sum())


def _recalc_side_raw(prob: pd.Series, p_long: pd.Series, p_short: pd.Series) -> pd.Series:
    p = pd.to_numeric(prob, errors="coerce")
    pl = pd.to_numeric(p_long, errors="coerce")
    ps = pd.to_numeric(p_short, errors="coerce")
    out = pd.Series(0, index=p.index, dtype="int64")
    out[p >= pl] = 1
    out[p <= ps] = -1
    return out


def _float_equal(a: Any, b: Any, atol: float = 1e-12, rtol: float = 1e-12) -> bool:
    av = pd.to_numeric(pd.Series([a]), errors="coerce").iloc[0]
    bv = pd.to_numeric(pd.Series([b]), errors="coerce").iloc[0]
    if pd.isna(av) and pd.isna(bv):
        return True
    if pd.isna(av) or pd.isna(bv):
        return False
    return math.isclose(float(av), float(bv), rel_tol=float(rtol), abs_tol=float(atol))


def _scalar_equal(a: Any, b: Any) -> bool:
    # Try numeric equality first.
    if _float_equal(a, b, atol=1e-12):
        return True
    # Then strict bool/text equality.
    if isinstance(a, bool) or isinstance(b, bool):
        return bool(a) == bool(b)
    return str(a).strip().lower() == str(b).strip().lower()


CANONICAL_SIGNAL_CONTRACT_COLUMNS = [
    "signal_id",
    "symbol",
    "timeframe",
    "signal_time_utc",
    "side",
    "entry_price",
    "stop_price",
    "take_profit_price",
    "expected_move_pct",
    "tp_reach_prob",
    "decision",
    "reason_code",
    "run_id",
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_inference_events_path(project_root: Path) -> Path | None:
    files = sorted(
        (project_root / "reports" / "inference").glob("inference_events_*.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


def _latest_inference_report_path(project_root: Path) -> Path | None:
    files = sorted(
        (project_root / "reports" / "inference").glob("inference_report_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


def _latest_ta_report_path(project_root: Path) -> Path | None:
    files = sorted(
        (project_root / "reports" / "technical_analysis").glob("ta_report_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


def _normalize_signal_side(value: Any) -> int | None:
    num = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.notna(num):
        iv = int(num)
        if iv in (-1, 0, 1):
            return iv
    text = str(value).strip().upper()
    if text in {"BUY", "LONG", "1"}:
        return 1
    if text in {"SELL", "SHORT", "-1"}:
        return -1
    if text in {"NO_TRADE", "NONE", "FLAT", "0"}:
        return 0
    return None


def _side_representation_kind(series: pd.Series) -> str:
    vals = series.dropna().astype(str).str.strip()
    if len(vals) == 0:
        return "empty"
    numeric_like = pd.to_numeric(vals, errors="coerce").notna().all()
    if numeric_like:
        return "numeric"
    text_domain = vals.str.upper().isin({"BUY", "SELL", "NO_TRADE", "LONG", "SHORT", "NONE", "FLAT"}).all()
    if text_domain:
        return "text"
    return "mixed"


def _signal_contract_checks(df: pd.DataFrame, dataset_name: str) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    missing = [c for c in CANONICAL_SIGNAL_CONTRACT_COLUMNS if c not in df.columns]
    checks.append(
        _check(
            f"{dataset_name}_canonical_signal_contract_columns_present",
            len(missing) == 0,
            {"missing": missing},
        )
    )
    if missing:
        return checks

    non_empty_cols = ["signal_id", "symbol", "timeframe", "signal_time_utc", "decision", "reason_code", "run_id"]
    for col in non_empty_cols:
        non_empty = int(df[col].astype(str).str.strip().replace({"nan": "", "NaT": ""}).ne("").sum())
        checks.append(
            _check(
                f"{dataset_name}_{col}_non_empty",
                non_empty == int(len(df)),
                {"non_empty": non_empty, "rows": int(len(df))},
            )
        )

    bad_ts = int(pd.to_datetime(df["signal_time_utc"], utc=True, errors="coerce").isna().sum())
    checks.append(_check(f"{dataset_name}_signal_time_utc_parseable", bad_ts == 0, {"bad_rows": bad_ts, "rows": int(len(df))}))

    for col in ["entry_price", "stop_price", "take_profit_price"]:
        s = pd.to_numeric(df[col], errors="coerce")
        bad = int((s.isna() | (s <= 0)).sum())
        checks.append(_check(f"{dataset_name}_{col}_positive", bad == 0, {"bad_rows": bad, "rows": int(len(df))}))

    for col in ["expected_move_pct", "tp_reach_prob"]:
        s = pd.to_numeric(df[col], errors="coerce")
        bad = int(s.isna().sum())
        checks.append(_check(f"{dataset_name}_{col}_parseable", bad == 0, {"bad_rows": bad, "rows": int(len(df))}))

    em = pd.to_numeric(df["expected_move_pct"], errors="coerce")
    checks.append(
        _check(
            f"{dataset_name}_expected_move_pct_non_negative",
            int((em < 0).sum()) == 0,
            {"bad_rows": int((em < 0).sum()), "rows": int(len(df))},
        )
    )
    tp = pd.to_numeric(df["tp_reach_prob"], errors="coerce")
    bad_tp = int((tp.isna() | (tp < 0.0) | (tp > 1.0)).sum())
    checks.append(_check(f"{dataset_name}_tp_reach_prob_in_0_1", bad_tp == 0, {"bad_rows": bad_tp, "rows": int(len(df))}))

    decision = df["decision"].astype(str).str.strip().str.upper()
    bad_decision = int((~decision.isin(["BUY", "SELL", "NO_TRADE"])).sum())
    checks.append(_check(f"{dataset_name}_decision_in_domain", bad_decision == 0, {"bad_rows": bad_decision, "rows": int(len(df))}))

    side_norm = df["side"].apply(_normalize_signal_side)
    bad_side = int(side_norm.isna().sum())
    checks.append(_check(f"{dataset_name}_side_normalizable_to_canonical_domain", bad_side == 0, {"bad_rows": bad_side, "rows": int(len(df))}))
    if bad_side == 0:
        decision_norm = decision.map({"BUY": 1, "SELL": -1, "NO_TRADE": 0})
        bad_side_vs_decision = int((side_norm.astype(int) != decision_norm.astype(int)).sum())
        checks.append(
            _check(
                f"{dataset_name}_side_matches_decision_semantics",
                bad_side_vs_decision == 0,
                {"bad_rows": bad_side_vs_decision, "rows": int(len(df))},
            )
        )

    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit canonical table chain integrity (candles -> features -> execution trace)")
    parser.add_argument("--run-dir", default="reports/table_canon_current")
    parser.add_argument("--require-trades", action="store_true", help="Fail if execution_trace has zero rows.")
    parser.add_argument("--inference-events-path", default=None, help="Optional path to inference_events CSV. Default: latest under reports/inference")
    parser.add_argument("--signal-events-path", default="data/analytics/signal_events.csv", help="Path to TA signal_events CSV")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    run_dir = (project_root / args.run_dir).resolve()
    data_dir = run_dir / "data"
    report_path = run_dir / "audit_chain_report.json"

    checks: list[dict[str, Any]] = []

    candles_path = data_dir / "candles_canonical.csv"
    feature_full_path = data_dir / "feature_frame_full.csv"
    feature_train_path = data_dir / "feature_frame.csv"
    feat_dict_path = data_dir / "feature_dictionary_ru.csv"
    tgt_dict_path = data_dir / "targets_dictionary_ru.csv"
    signal_path = data_dir / "signal_frame.csv"
    trace_path = data_dir / "execution_trace.csv"
    trace_summary_path = data_dir / "execution_trace_summary.json"
    strategy_summary_path = data_dir / "strategy_summary.csv"
    parity_report_path = data_dir / "candles_parity_report.json"
    inference_events_path = (
        Path(args.inference_events_path).resolve()
        if args.inference_events_path
        else _latest_inference_events_path(project_root)
    )
    inference_report_path = _latest_inference_report_path(project_root)
    ta_report_path = _latest_ta_report_path(project_root)
    signal_events_path = Path(args.signal_events_path)
    if not signal_events_path.is_absolute():
        signal_events_path = (project_root / signal_events_path).resolve()
    feat_dict_xlsx_path = data_dir / "feature_dictionary_ru.xlsx"
    candles_xlsx_path = data_dir / "candles_canonical.xlsx"
    feature_full_xlsx_path = data_dir / "feature_frame_full.xlsx"
    feature_train_xlsx_path = data_dir / "feature_frame.xlsx"
    signal_xlsx_path = data_dir / "signal_frame.xlsx"
    trace_xlsx_path = data_dir / "execution_trace.xlsx"
    strategy_summary_xlsx_path = data_dir / "strategy_summary.xlsx"

    required = [
        candles_path,
        feature_full_path,
        feature_train_path,
        feat_dict_path,
        tgt_dict_path,
        feat_dict_xlsx_path,
        signal_path,
        parity_report_path,
        strategy_summary_path,
        candles_xlsx_path,
        feature_full_xlsx_path,
        feature_train_xlsx_path,
        signal_xlsx_path,
        trace_xlsx_path,
        strategy_summary_xlsx_path,
    ]
    missing = [str(p) for p in required if not p.exists()]
    checks.append(_check("required_files_exist", len(missing) == 0, {"missing": missing}))
    if missing:
        payload = {
            "status": "FAIL",
            "generated_at_utc": _utc_now_iso(),
            "checks": checks,
            "summary": {"total": len(checks), "failed": int(sum(1 for c in checks if not c["ok"]))},
        }
        report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": "FAIL", "report_path": str(report_path), "missing": missing}, ensure_ascii=False))
        return 1

    candles, candles_sep = _read_csv_auto(candles_path)
    full, full_sep = _read_csv_auto(feature_full_path)
    train, train_sep = _read_csv_auto(feature_train_path)
    feat_dict, feat_dict_sep = _read_csv_auto(feat_dict_path)
    tgt_dict, tgt_dict_sep = _read_csv_auto(tgt_dict_path)

    checks.append(_check("excel_friendly_delimiter_candles", candles_sep == ";", {"detected_sep": candles_sep}))
    checks.append(_check("excel_friendly_delimiter_feature_full", full_sep == ";", {"detected_sep": full_sep}))
    checks.append(_check("excel_friendly_delimiter_feature_train", train_sep == ";", {"detected_sep": train_sep}))

    checks.append(_check("candles_rows_positive", len(candles) > 0, {"rows": int(len(candles))}))
    if "open_time_utc" in candles.columns:
        ts = pd.to_datetime(candles["open_time_utc"], utc=True, errors="coerce")
        checks.append(_check("candles_open_time_parseable", int(ts.isna().sum()) == 0, {"nan_rows": int(ts.isna().sum())}))
        checks.append(
            _check(
                "candles_open_time_utc_suffix",
                _utc_suffix_bad_count(candles, "open_time_utc") == 0,
                {"bad_rows": _utc_suffix_bad_count(candles, "open_time_utc")},
            )
        )
        checks.append(_check("candles_open_time_unique", int(ts.duplicated().sum()) == 0, {"duplicates": int(ts.duplicated().sum())}))
        checks.append(
            _check(
                "candles_open_time_monotonic",
                bool(ts.is_monotonic_increasing),
                {"monotonic": bool(ts.is_monotonic_increasing)},
            )
        )
        # Strict timeframe contract inside candles_canonical.
        tf_val = str(candles["timeframe"].iloc[0]).strip() if "timeframe" in candles.columns and len(candles) > 0 else "1m"
        tf_step = timeframe_delta(tf_val)
        if "close_time_utc" in candles.columns:
            cts = pd.to_datetime(candles["close_time_utc"], utc=True, errors="coerce")
            checks.append(
                _check(
                    "candles_close_time_utc_suffix",
                    _utc_suffix_bad_count(candles, "close_time_utc") == 0,
                    {"bad_rows": _utc_suffix_bad_count(candles, "close_time_utc")},
                )
            )
            dur = cts - ts
            bad_dur = int((dur != tf_step).sum())
            checks.append(
                _check(
                    "candles_close_minus_open_equals_timeframe_step",
                    bad_dur == 0,
                    {"bad_rows": bad_dur, "timeframe": tf_val, "expected_step_sec": int(tf_step.total_seconds())},
                )
            )
        if len(ts) > 1:
            dt = ts.diff().dropna()
            bad_step = int((dt != tf_step).sum())
            checks.append(
                _check(
                    "candles_open_time_step_equals_timeframe_step",
                    bad_step == 0,
                    {"bad_rows": bad_step, "timeframe": tf_val, "expected_step_sec": int(tf_step.total_seconds())},
                )
            )

    checks.append(_check("feature_full_rows_eq_candles", len(full) == len(candles), {"feature_full": int(len(full)), "candles": int(len(candles))}))
    checks.append(_check("feature_train_rows_positive", len(train) > 0, {"rows": int(len(train))}))
    checks.append(_check("feature_train_rows_le_full", len(train) <= len(full), {"feature_train": int(len(train)), "feature_full": int(len(full))}))
    # Numeric cleanliness (no NaN/Inf) in key fields.
    candles_num_ok, candles_num_bad = _numeric_clean_check(candles, ["open", "high", "low", "close", "volume", "turnover"])
    checks.append(_check("candles_key_numeric_clean", candles_num_ok, candles_num_bad))
    signal, signal_sep = _read_csv_auto(signal_path)
    signal_num_ok, signal_num_bad = _numeric_clean_check(signal, ["prob_up", "expected_move_pct", "ev", "ev_usd"])
    checks.append(_check("signal_key_numeric_clean", signal_num_ok, signal_num_bad))
    full_num_ok, full_num_bad = _numeric_clean_check(full, ["open", "high", "low", "close"])
    checks.append(_check("feature_full_price_numeric_clean", full_num_ok, full_num_bad))
    train_num_ok, train_num_bad = _numeric_clean_check(train, ["ema20", "ema50", "ema200", "atr14", "rsi14"])
    checks.append(_check("feature_train_indicator_numeric_clean", train_num_ok, train_num_bad))

    checks.append(_check("feature_dict_exact_68", len(feat_dict) == 68, {"rows": int(len(feat_dict)), "sep": feat_dict_sep}))
    checks.append(_check("targets_dict_exact_2", len(tgt_dict) == 2, {"rows": int(len(tgt_dict)), "sep": tgt_dict_sep}))
    # Feature dictionary completeness (human-readable contract).
    dict_required_cols = ["column_name_en", "column_name_ru", "formula_text", "computed_on", "used_in", "lookahead_safe"]
    missing_dict_cols = [c for c in dict_required_cols if c not in feat_dict.columns]
    checks.append(_check("feature_dict_required_columns_present", len(missing_dict_cols) == 0, {"missing": missing_dict_cols}))
    if len(missing_dict_cols) == 0 and len(feat_dict) > 0:
        bad_ru = int(feat_dict["column_name_ru"].astype(str).str.strip().replace({"nan": ""}).eq("").sum())
        bad_formula = int(feat_dict["formula_text"].astype(str).str.strip().replace({"nan": ""}).eq("").sum())
        bad_computed = int(feat_dict["computed_on"].astype(str).str.strip().replace({"nan": ""}).eq("").sum())
        bad_used = int(feat_dict["used_in"].astype(str).str.strip().replace({"nan": ""}).eq("").sum())
        checks.append(_check("feature_dict_column_name_ru_non_empty", bad_ru == 0, {"bad_rows": bad_ru, "rows": int(len(feat_dict))}))
        checks.append(_check("feature_dict_formula_text_non_empty", bad_formula == 0, {"bad_rows": bad_formula, "rows": int(len(feat_dict))}))
        checks.append(_check("feature_dict_computed_on_non_empty", bad_computed == 0, {"bad_rows": bad_computed, "rows": int(len(feat_dict))}))
        checks.append(_check("feature_dict_used_in_non_empty", bad_used == 0, {"bad_rows": bad_used, "rows": int(len(feat_dict))}))
        # computed_on domain contract.
        comp = feat_dict["computed_on"].astype(str).str.strip()
        bad_comp_domain = int((~comp.isin(["close(t)", "post_close_label"])).sum())
        checks.append(
            _check(
                "feature_dict_computed_on_domain_valid",
                bad_comp_domain == 0,
                {"bad_rows": bad_comp_domain, "allowed": ["close(t)", "post_close_label"]},
            )
        )
        # lookahead_safe should be boolean-like.
        las = feat_dict["lookahead_safe"].astype(str).str.strip().str.lower()
        bad_las = int((~las.isin(["true", "false", "1", "0"])).sum())
        checks.append(
            _check(
                "feature_dict_lookahead_safe_boolean_like",
                bad_las == 0,
                {"bad_rows": bad_las, "rows": int(len(feat_dict))},
            )
        )
    # Feature dictionary <-> feature frame source-of-truth parity.
    feature_cols_expected = [str(c) for c in FEATURE_COLUMNS]
    feature_cols_in_frame = [c for c in feature_cols_expected if c in full.columns]
    missing_feature_cols = [c for c in feature_cols_expected if c not in full.columns]
    checks.append(
        _check(
            "feature_frame_has_all_expected_feature_columns",
            len(missing_feature_cols) == 0,
            {"expected": len(feature_cols_expected), "present": len(feature_cols_in_frame), "missing": missing_feature_cols},
        )
    )
    if "column_name_en" in feat_dict.columns:
        dict_feature_cols = feat_dict["column_name_en"].astype(str).tolist()
        dict_dups = sorted({c for c in dict_feature_cols if dict_feature_cols.count(c) > 1})
        checks.append(_check("feature_dict_no_duplicate_column_name_en", len(dict_dups) == 0, {"duplicates": dict_dups}))
        missing_in_dict = sorted(set(feature_cols_expected) - set(dict_feature_cols))
        extra_in_dict = sorted(set(dict_feature_cols) - set(feature_cols_expected))
        checks.append(
            _check(
                "feature_dict_matches_expected_feature_columns",
                len(missing_in_dict) == 0 and len(extra_in_dict) == 0,
                {"missing_in_dict": missing_in_dict, "extra_in_dict": extra_in_dict},
            )
        )
    else:
        checks.append(_check("feature_dict_has_column_name_en", False, {"columns": [str(c) for c in feat_dict.columns]}))
    if "column_name_en" in tgt_dict.columns:
        tgt_set = set(tgt_dict["column_name_en"].astype(str).tolist())
        checks.append(
            _check(
                "targets_dict_exact_names",
                tgt_set == {"future_return", "target_up"},
                {"actual": sorted(tgt_set)},
            )
        )
    else:
        checks.append(_check("targets_dict_has_column_name_en", False, {"columns": [str(c) for c in tgt_dict.columns]}))
    # Dictionary CSV <-> XLSX parity checks.
    feat_dict_xlsx = _read_xlsx_auto(feat_dict_xlsx_path, sheet_name="features_dictionary")
    tgt_dict_xlsx = _read_xlsx_auto(feat_dict_xlsx_path, sheet_name="targets_dictionary")
    feat_cols_csv = [str(c) for c in feat_dict.columns]
    feat_cols_xlsx = [str(c) for c in feat_dict_xlsx.columns]
    tgt_cols_csv = [str(c) for c in tgt_dict.columns]
    tgt_cols_xlsx = [str(c) for c in tgt_dict_xlsx.columns]
    checks.append(
        _check(
            "feature_dictionary_xlsx_columns_match_csv",
            feat_cols_csv == feat_cols_xlsx,
            {"csv_cols_count": len(feat_cols_csv), "xlsx_cols_count": len(feat_cols_xlsx)},
        )
    )
    checks.append(
        _check(
            "feature_dictionary_xlsx_rows_match_csv",
            int(len(feat_dict_xlsx)) == int(len(feat_dict)),
            {"csv_rows": int(len(feat_dict)), "xlsx_rows": int(len(feat_dict_xlsx))},
        )
    )
    checks.append(
        _check(
            "targets_dictionary_xlsx_columns_match_csv",
            tgt_cols_csv == tgt_cols_xlsx,
            {"csv_cols_count": len(tgt_cols_csv), "xlsx_cols_count": len(tgt_cols_xlsx)},
        )
    )
    checks.append(
        _check(
            "targets_dictionary_xlsx_rows_match_csv",
            int(len(tgt_dict_xlsx)) == int(len(tgt_dict)),
            {"csv_rows": int(len(tgt_dict)), "xlsx_rows": int(len(tgt_dict_xlsx))},
        )
    )
    checks.append(_check("signal_frame_delimiter_semicolon", signal_sep == ";", {"detected_sep": signal_sep}))
    checks.append(_check("signal_frame_rows_positive", len(signal) > 0, {"rows": int(len(signal))}))
    checks.append(
        _check(
            "signal_open_time_utc_suffix",
            _utc_suffix_bad_count(signal, "open_time_utc") == 0,
            {"bad_rows": _utc_suffix_bad_count(signal, "open_time_utc")},
        )
    )
    if "prob_up" in signal.columns:
        prob = pd.to_numeric(signal["prob_up"], errors="coerce")
        bad_prob = int((prob.isna() | (prob < 0.0) | (prob > 1.0)).sum())
        checks.append(
            _check(
                "signal_prob_up_in_0_1",
                bad_prob == 0,
                {"bad_rows": bad_prob, "rows": int(len(signal))},
            )
        )
    if "expected_move_pct" in signal.columns:
        em = pd.to_numeric(signal["expected_move_pct"], errors="coerce")
        bad_em = int((em.isna() | (em < 0.0)).sum())
        checks.append(
            _check(
                "signal_expected_move_pct_non_negative",
                bad_em == 0,
                {"bad_rows": bad_em, "rows": int(len(signal))},
            )
        )
    if "p_enter_long" in signal.columns and "p_enter_short" in signal.columns:
        pl = pd.to_numeric(signal["p_enter_long"], errors="coerce")
        ps = pd.to_numeric(signal["p_enter_short"], errors="coerce")
        bad_pl = int((pl.isna() | (pl < 0.0) | (pl > 1.0)).sum())
        bad_ps = int((ps.isna() | (ps < 0.0) | (ps > 1.0)).sum())
        bad_order = int((pl <= ps).sum())
        checks.append(_check("signal_p_enter_long_in_0_1", bad_pl == 0, {"bad_rows": bad_pl, "rows": int(len(signal))}))
        checks.append(_check("signal_p_enter_short_in_0_1", bad_ps == 0, {"bad_rows": bad_ps, "rows": int(len(signal))}))
        checks.append(_check("signal_p_enter_long_gt_p_enter_short", bad_order == 0, {"bad_rows": bad_order, "rows": int(len(signal))}))
    if all(c in signal.columns for c in ["prob_up", "p_enter_long", "p_enter_short", "side_raw"]):
        side_expected = _recalc_side_raw(signal["prob_up"], signal["p_enter_long"], signal["p_enter_short"])
        side_actual = pd.to_numeric(signal["side_raw"], errors="coerce").fillna(0).astype(int)
        bad_side_raw = int((side_expected != side_actual).sum())
        checks.append(
            _check(
                "signal_side_raw_matches_prob_threshold_rule",
                bad_side_raw == 0,
                {"bad_rows": bad_side_raw, "rows": int(len(signal))},
            )
        )
    if "signal_mode" in signal.columns and "side_mode_filtered" in signal.columns:
        mode = signal["signal_mode"].astype(str).str.lower()
        sf = pd.to_numeric(signal["side_mode_filtered"], errors="coerce").fillna(0).astype(int)
        bad_long = int(((mode == "long_only") & (sf < 0)).sum())
        bad_short = int(((mode == "short_only") & (sf > 0)).sum())
        checks.append(
            _check(
                "signal_side_mode_filtered_respects_signal_mode",
                (bad_long + bad_short) == 0,
                {"bad_long_only_rows": bad_long, "bad_short_only_rows": bad_short, "rows": int(len(signal))},
            )
        )

    # Time-range and key-column checks for signal frame.
    if "open_time_utc" in signal.columns and "open_time_utc" in full.columns:
        sig_ts = pd.to_datetime(signal["open_time_utc"], utc=True, errors="coerce")
        full_ts = pd.to_datetime(full["open_time_utc"], utc=True, errors="coerce")
        sig_nan = int(sig_ts.isna().sum())
        checks.append(_check("signal_open_time_parseable", sig_nan == 0, {"nan_rows": sig_nan}))
        checks.append(_check("signal_open_time_unique", int(sig_ts.duplicated().sum()) == 0, {"duplicates": int(sig_ts.duplicated().sum())}))
        checks.append(_check("signal_open_time_monotonic", bool(sig_ts.is_monotonic_increasing), {"monotonic": bool(sig_ts.is_monotonic_increasing)}))
        if len(sig_ts) > 1 and "timeframe" in candles.columns and len(candles) > 0:
            sig_step = sig_ts.diff().dropna()
            tf_val_sig = str(candles["timeframe"].iloc[0]).strip()
            tf_delta_sig = timeframe_delta(tf_val_sig)
            tf_sec = int(tf_delta_sig.total_seconds())
            step_sec = sig_step.dt.total_seconds()
            # Allow sparse signal bars, but require positive steps aligned to timeframe grid.
            bad_sig_step = int(((step_sec <= 0) | ((step_sec % tf_sec) != 0)).sum())
            checks.append(
                _check(
                    "signal_open_time_step_is_positive_and_multiple_of_timeframe_step",
                    bad_sig_step == 0,
                    {"bad_rows": bad_sig_step, "timeframe": tf_val_sig, "timeframe_step_sec": tf_sec},
                )
            )
        if sig_nan == 0 and int(full_ts.isna().sum()) == 0 and len(full_ts) > 0:
            sig_min = sig_ts.min()
            sig_max = sig_ts.max()
            full_min = full_ts.min()
            full_max = full_ts.max()
            checks.append(
                _check(
                    "signal_time_range_within_feature_full",
                    bool(sig_min >= full_min and sig_max <= full_max),
                    {
                        "signal_min": str(sig_min),
                        "signal_max": str(sig_max),
                        "feature_min": str(full_min),
                        "feature_max": str(full_max),
                    },
                )
            )
    for col in ["prob_up", "side_raw", "side_mode_filtered", "side_executed", "run_id"]:
        if col in signal.columns:
            non_empty = int(signal[col].astype(str).str.strip().replace({"nan": "", "NaT": ""}).ne("").sum())
            checks.append(
                _check(
                    f"signal_{col}_non_empty",
                    non_empty == int(len(signal)),
                    {"non_empty": non_empty, "rows": int(len(signal))},
                )
            )
    # Side-domain checks for signal frame.
    for side_col in ["side_raw", "side_mode_filtered", "side_executed"]:
        if side_col in signal.columns:
            sv = pd.to_numeric(signal[side_col], errors="coerce")
            bad_side = int((~sv.isin([-1, 0, 1])).sum())
            checks.append(
                _check(
                    f"signal_{side_col}_in_domain_minus1_0_1",
                    bad_side == 0,
                    {"bad_rows": bad_side, "rows": int(len(signal))},
                )
            )
    # Runtime contract metadata in signal_frame.
    for col in ["contract_version", "calibration_mode"]:
        checks.append(_check(f"signal_frame_{col}_present", col in signal.columns, {"present": col in signal.columns}))
    if "contract_version" in signal.columns and len(signal) > 0:
        cv = signal["contract_version"].astype(str).str.strip()
        bad_cv = int(cv.eq("").sum())
        uniq_cv = sorted(set(cv.tolist()))
        checks.append(_check("signal_frame_contract_version_non_empty", bad_cv == 0, {"bad_rows": bad_cv, "rows": int(len(signal))}))
        checks.append(_check("signal_frame_contract_version_single", len(uniq_cv) == 1, {"values": uniq_cv}))
        if len(uniq_cv) == 1:
            checks.append(
                _check(
                    "signal_frame_contract_version_matches_runtime_constant",
                    uniq_cv[0] == SIGNAL_CONTRACT_VERSION,
                    {"value": uniq_cv[0], "expected": SIGNAL_CONTRACT_VERSION},
                )
            )
    if "calibration_mode" in signal.columns and len(signal) > 0:
        cm = signal["calibration_mode"].astype(str).str.strip().str.lower()
        bad_cm = int(cm.eq("").sum())
        uniq_cm = sorted(set(cm.tolist()))
        checks.append(_check("signal_frame_calibration_mode_non_empty", bad_cm == 0, {"bad_rows": bad_cm, "rows": int(len(signal))}))
        checks.append(_check("signal_frame_calibration_mode_single", len(uniq_cm) == 1, {"values": uniq_cm}))
        if len(uniq_cm) == 1:
            checks.append(
                _check(
                    "signal_frame_calibration_mode_none",
                    uniq_cm[0] == CALIBRATION_MODE_NONE,
                    {"value": uniq_cm[0], "expected": CALIBRATION_MODE_NONE},
                )
            )

    try:
        parity = json.loads(parity_report_path.read_text(encoding="utf-8"))
        days_failed = int(parity.get("days_failed", 0))
        checks.append(_check("parity_days_failed_zero", days_failed == 0, {"days_failed": days_failed}))
    except Exception as exc:
        checks.append(_check("parity_report_parseable", False, {"error": str(exc)}))

    if trace_path.exists():
        trace, trace_sep = _read_csv_auto(trace_path)
        checks.append(_check("execution_trace_delimiter_semicolon", trace_sep == ";", {"detected_sep": trace_sep}))
        checks.append(_check("execution_trace_rows_non_negative", len(trace) >= 0, {"rows": int(len(trace))}))
        if bool(args.require_trades):
            checks.append(_check("execution_trace_rows_positive_required", len(trace) > 0, {"rows": int(len(trace))}))
        if len(trace) > 0:
            if "run_id" in trace.columns:
                tr_run = trace["run_id"].astype(str).str.strip()
                tr_run_single = sorted(set(tr_run.tolist()))
                bad_run_empty = int(tr_run.eq("").sum())
                checks.append(_check("execution_trace_run_id_non_empty", bad_run_empty == 0, {"bad_rows": bad_run_empty, "rows": int(len(trace))}))
                checks.append(_check("execution_trace_run_id_single", len(tr_run_single) == 1, {"values": tr_run_single}))
                if len(tr_run_single) == 1:
                    looks_like_trace = tr_run_single[0].startswith("trace_")
                    checks.append(_check("execution_trace_run_id_format_trace_prefix", looks_like_trace, {"run_id": tr_run_single[0]}))
            for meta_col, expected_val in [("contract_version", SIGNAL_CONTRACT_VERSION), ("calibration_mode", CALIBRATION_MODE_NONE)]:
                if meta_col in trace.columns:
                    vals = trace[meta_col].astype(str).str.strip()
                    vals_norm = vals.str.lower() if meta_col == "calibration_mode" else vals
                    bad_empty = int(vals_norm.eq("").sum())
                    uniq = sorted(set(vals_norm.tolist()))
                    checks.append(_check(f"execution_trace_{meta_col}_non_empty", bad_empty == 0, {"bad_rows": bad_empty, "rows": int(len(trace))}))
                    checks.append(_check(f"execution_trace_{meta_col}_single", len(uniq) == 1, {"values": uniq}))
                    if len(uniq) == 1:
                        checks.append(
                            _check(
                                f"execution_trace_{meta_col}_matches_runtime_constant",
                                uniq[0] == (expected_val.lower() if meta_col == "calibration_mode" else expected_val),
                                {"value": uniq[0], "expected": expected_val},
                            )
                        )
            if "trade_id" in trace.columns:
                tid = trace["trade_id"].astype(str).str.strip()
                bad_empty_tid = int(tid.eq("").sum())
                dup_tid = int(tid.duplicated().sum())
                checks.append(
                    _check(
                        "execution_trade_id_non_empty",
                        bad_empty_tid == 0,
                        {"bad_rows": bad_empty_tid, "rows": int(len(trace))},
                    )
                )
                checks.append(
                    _check(
                        "execution_trade_id_unique",
                        dup_tid == 0,
                        {"duplicates": dup_tid, "rows": int(len(trace))},
                    )
                )
            for col in ["signal_time_utc", "entry_time_utc", "exit_time_utc", "side", "entry_price", "exit_price"]:
                if col in trace.columns:
                    non_empty = int(trace[col].astype(str).str.strip().replace({"nan": "", "NaT": ""}).ne("").sum())
                    checks.append(
                        _check(
                            f"execution_trace_{col}_non_empty",
                            non_empty == int(len(trace)),
                            {"non_empty": non_empty, "rows": int(len(trace))},
                        )
                    )
            if "side" in trace.columns:
                side_v = pd.to_numeric(trace["side"], errors="coerce")
                bad_trace_side = int((~side_v.isin([-1, 1])).sum())
                checks.append(
                    _check(
                        "execution_side_in_domain_minus1_plus1",
                        bad_trace_side == 0,
                        {"bad_rows": bad_trace_side, "rows": int(len(trace))},
                    )
                )
            if "entry_price" in trace.columns and "exit_price" in trace.columns:
                ep = pd.to_numeric(trace["entry_price"], errors="coerce")
                xp = pd.to_numeric(trace["exit_price"], errors="coerce")
                bad_price = int(((ep <= 0) | (xp <= 0) | ep.isna() | xp.isna()).sum())
                checks.append(
                    _check(
                        "execution_prices_positive",
                        bad_price == 0,
                        {"bad_rows": bad_price, "rows": int(len(trace))},
                    )
                )
            for src_col, check_name in [
                ("source_oos_report", "execution_trace_source_oos_report_consistent_and_exists"),
                ("source_backtest_csv", "execution_trace_source_backtest_csv_consistent_and_exists"),
            ]:
                if src_col in trace.columns:
                    src_vals = trace[src_col].astype(str).str.strip()
                    uniq = sorted(set(src_vals.tolist()))
                    consistent = len(uniq) == 1 and uniq[0] != ""
                    exists = Path(uniq[0]).exists() if consistent else False
                    checks.append(
                        _check(
                            check_name,
                            consistent and exists,
                            {"unique_values": uniq, "exists": bool(exists)},
                        )
                    )
            # Link integrity: each execution row must map to a signal_frame row by signal_time_utc and side.
            if "signal_time_utc" in trace.columns and "open_time_utc" in signal.columns and "side" in trace.columns and "side_executed" in signal.columns:
                sig_key = signal.copy()
                sig_key["open_time_utc"] = pd.to_datetime(sig_key["open_time_utc"], utc=True, errors="coerce")
                sig_key["side_executed"] = pd.to_numeric(sig_key["side_executed"], errors="coerce").fillna(0).astype(int)
                tr_key = trace.copy()
                tr_key["signal_time_utc"] = pd.to_datetime(tr_key["signal_time_utc"], utc=True, errors="coerce")
                tr_key["side"] = pd.to_numeric(tr_key["side"], errors="coerce").fillna(0).astype(int)
                merged_link = tr_key.merge(
                    sig_key[["open_time_utc", "side_executed"]],
                    left_on=["signal_time_utc", "side"],
                    right_on=["open_time_utc", "side_executed"],
                    how="left",
                    indicator=True,
                )
                bad_link = int((merged_link["_merge"] != "both").sum())
                checks.append(
                    _check(
                        "execution_rows_link_to_signal_frame_by_time_and_side",
                        bad_link == 0,
                        {"bad_rows": bad_link, "rows": int(len(tr_key))},
                    )
                )
            if "fee_usd_est" in trace.columns:
                fee = pd.to_numeric(trace["fee_usd_est"], errors="coerce")
                bad_fee = int((fee.isna() | (fee < 0.0)).sum())
                checks.append(
                    _check(
                        "execution_fee_usd_est_non_negative",
                        bad_fee == 0,
                        {"bad_rows": bad_fee, "rows": int(len(trace))},
                    )
                )
            if "slippage_usd_est" in trace.columns:
                slip = pd.to_numeric(trace["slippage_usd_est"], errors="coerce")
                bad_slip = int((slip.isna() | (slip < 0.0)).sum())
                checks.append(
                    _check(
                        "execution_slippage_usd_est_non_negative",
                        bad_slip == 0,
                        {"bad_rows": bad_slip, "rows": int(len(trace))},
                    )
                )
            # Validate execution time ordering and candles-boundary.
            sig_t = pd.to_datetime(trace["signal_time_utc"], utc=True, errors="coerce") if "signal_time_utc" in trace.columns else None
            ent_t = pd.to_datetime(trace["entry_time_utc"], utc=True, errors="coerce") if "entry_time_utc" in trace.columns else None
            ex_t = pd.to_datetime(trace["exit_time_utc"], utc=True, errors="coerce") if "exit_time_utc" in trace.columns else None
            if sig_t is not None and ent_t is not None:
                checks.append(
                    _check(
                        "execution_signal_before_or_equal_entry",
                        bool((sig_t <= ent_t).all()),
                        {"rows": int(len(trace))},
                    )
                )
                checks.append(
                    _check(
                        "execution_signal_time_monotonic",
                        bool(sig_t.is_monotonic_increasing),
                        {"monotonic": bool(sig_t.is_monotonic_increasing)},
                    )
                )
                checks.append(
                    _check(
                        "execution_signal_time_utc_suffix",
                        _utc_suffix_bad_count(trace, "signal_time_utc") == 0,
                        {"bad_rows": _utc_suffix_bad_count(trace, "signal_time_utc")},
                    )
                )
                checks.append(
                    _check(
                        "execution_entry_time_utc_suffix",
                        _utc_suffix_bad_count(trace, "entry_time_utc") == 0,
                        {"bad_rows": _utc_suffix_bad_count(trace, "entry_time_utc")},
                    )
                )
                checks.append(
                    _check(
                        "execution_exit_time_utc_suffix",
                        _utc_suffix_bad_count(trace, "exit_time_utc") == 0,
                        {"bad_rows": _utc_suffix_bad_count(trace, "exit_time_utc")},
                    )
                )
                # Market causality contract:
                # - entry cannot be earlier than the first candle open after signal;
                # - entry timestamp must match some candle open exactly.
                # This allows delayed entry (e.g. while previous position is still active)
                # but keeps anti-lookahead and candle-alignment guarantees.
                if "order_type" in trace.columns and "open_time_utc" in candles.columns:
                    market_mask = trace["order_type"].astype(str).str.lower().eq("market")
                    trace_m = trace[market_mask].copy()
                    if len(trace_m) > 0:
                        sig_m = pd.to_datetime(trace_m["signal_time_utc"], utc=True, errors="coerce")
                        ent_m = pd.to_datetime(trace_m["entry_time_utc"], utc=True, errors="coerce")
                        c_open = pd.to_datetime(candles["open_time_utc"], utc=True, errors="coerce").dropna().drop_duplicates().sort_values()
                        c_open_set = set(c_open.tolist())
                        expected_list: list[pd.Timestamp | pd.NaT] = []
                        mismatch_samples: list[dict[str, str]] = []
                        bad = 0
                        for s_ts, e_ts in zip(sig_m.tolist(), ent_m.tolist()):
                            if pd.isna(s_ts) or pd.isna(e_ts):
                                bad += 1
                                continue
                            pos = int(c_open.searchsorted(s_ts, side="left"))
                            if pos < len(c_open) and c_open.iloc[pos] == s_ts and (pos + 1) < len(c_open):
                                exp = c_open.iloc[pos + 1]
                            else:
                                # Fallback: first candle strictly after signal.
                                pos_r = int(c_open.searchsorted(s_ts, side="right"))
                                exp = c_open.iloc[pos_r] if pos_r < len(c_open) else pd.NaT
                            expected_list.append(exp)
                            # valid if entry is aligned to candle open and not earlier than expected.
                            is_open_aligned = e_ts in c_open_set
                            is_not_earlier = (not pd.isna(exp)) and (e_ts >= exp)
                            if (not is_open_aligned) or (not is_not_earlier):
                                bad += 1
                                if len(mismatch_samples) < 5:
                                    mismatch_samples.append(
                                        {
                                            "signal_time_utc": str(s_ts),
                                            "expected_entry_time_utc": str(exp),
                                            "actual_entry_time_utc": str(e_ts),
                                        }
                                    )
                        checks.append(
                            _check(
                                "execution_market_entry_on_next_candle_open",
                                bad == 0,
                                {"rows": int(len(trace_m)), "bad_rows": int(bad), "samples": mismatch_samples},
                            )
                        )
            if ent_t is not None and ex_t is not None:
                checks.append(
                    _check(
                        "execution_entry_before_or_equal_exit",
                        bool((ent_t <= ex_t).all()),
                        {"rows": int(len(trace))},
                    )
                )
                # Duration contract: non-negative and aligned to timeframe step.
                if "timeframe" in candles.columns and len(candles) > 0:
                    tf_val_dur = str(candles["timeframe"].iloc[0]).strip()
                    tf_sec_dur = int(timeframe_delta(tf_val_dur).total_seconds())
                    dur_sec = (ex_t - ent_t).dt.total_seconds()
                    bad_neg_dur = int((dur_sec < 0).sum())
                    dur_mod = (dur_sec % tf_sec_dur).fillna(0.0)
                    bad_step_dur = int((dur_mod != 0).sum())
                    checks.append(
                        _check(
                            "execution_duration_non_negative",
                            bad_neg_dur == 0,
                            {"bad_rows": bad_neg_dur, "rows": int(len(trace))},
                        )
                    )
                    checks.append(
                        _check(
                            "execution_duration_multiple_of_timeframe_step",
                            bad_step_dur == 0,
                            {"bad_rows": bad_step_dur, "rows": int(len(trace)), "timeframe_step_sec": tf_sec_dur},
                        )
                    )
                    if "time_to_target_sec" in trace.columns:
                        ttt = pd.to_numeric(trace["time_to_target_sec"], errors="coerce")
                        mask = ttt.notna()
                        if int(mask.sum()) > 0:
                            ttt_bad = int(((ttt[mask] < 0) | (ttt[mask] > dur_sec[mask])).sum())
                            checks.append(
                                _check(
                                    "execution_time_to_target_sec_within_trade_duration",
                                    ttt_bad == 0,
                                    {"bad_rows": ttt_bad, "checked_rows": int(mask.sum())},
                                )
                            )
            if "open_time_utc" in candles.columns:
                c_ts = pd.to_datetime(candles["open_time_utc"], utc=True, errors="coerce")
                if len(c_ts) > 0 and int(c_ts.isna().sum()) == 0 and ent_t is not None and ex_t is not None:
                    c_min, c_max = c_ts.min(), c_ts.max()
                    checks.append(
                        _check(
                            "execution_times_within_candles_range",
                            bool((ent_t >= c_min).all() and (ex_t <= c_max).all()),
                            {"candles_min": str(c_min), "candles_max": str(c_max)},
                        )
                    )
            # Financial consistency inside execution trace.
            required_fin_cols = {"gross_pnl_usd", "net_pnl_usd", "fee_usd_est", "slippage_usd_est"}
            if required_fin_cols.issubset(set(trace.columns)):
                lhs = pd.to_numeric(trace["gross_pnl_usd"], errors="coerce") - pd.to_numeric(trace["fee_usd_est"], errors="coerce") - pd.to_numeric(trace["slippage_usd_est"], errors="coerce")
                ok_fin, bad_fin = _allclose_series(lhs, trace["net_pnl_usd"], atol=1e-9)
                checks.append(
                    _check(
                        "execution_trace_cost_balance_gross_minus_costs_equals_net",
                        ok_fin,
                        {"bad_rows": bad_fin, "rows": int(len(trace)), "atol": 1e-9},
                    )
                )
        if trace_summary_path.exists():
            try:
                sm = json.loads(trace_summary_path.read_text(encoding="utf-8"))
                expected = int(sm.get("execution_rows", -1))
                checks.append(_check("execution_trace_rows_match_summary", int(len(trace)) == expected, {"trace_rows": int(len(trace)), "summary_rows": expected}))
                sm_cv = str(sm.get("contract_version", "")).strip()
                sm_cm = str(sm.get("calibration_mode", "")).strip().lower()
                checks.append(_check("execution_trace_summary_contract_version_non_empty", bool(sm_cv), {"contract_version": sm_cv}))
                checks.append(_check("execution_trace_summary_calibration_mode_none", sm_cm == CALIBRATION_MODE_NONE, {"calibration_mode": sm_cm}))
                checks.append(
                    _check(
                        "execution_trace_summary_contract_version_matches_runtime_constant",
                        sm_cv == SIGNAL_CONTRACT_VERSION,
                        {"value": sm_cv, "expected": SIGNAL_CONTRACT_VERSION},
                    )
                )
                if "run_id" in trace.columns:
                    tr_run_single = sorted(set(trace["run_id"].astype(str).str.strip().tolist()))
                    sm_run = str(sm.get("run_id", "")).strip()
                    if int(len(trace)) == 0 and expected == 0:
                        # No-trade scenario: trace table is empty by design, run_id comes from summary context.
                        checks.append(
                            _check(
                                "execution_trace_run_id_matches_summary",
                                bool(sm_run),
                                {"trace_run_id": tr_run_single, "summary_run_id": sm_run, "mode": "no_trades"},
                            )
                        )
                    else:
                        checks.append(
                            _check(
                                "execution_trace_run_id_matches_summary",
                                len(tr_run_single) == 1 and sm_run == tr_run_single[0],
                                {"trace_run_id": tr_run_single[0] if len(tr_run_single) == 1 else tr_run_single, "summary_run_id": sm_run},
                            )
                        )
                if "contract_version" in signal.columns:
                    sig_cv_vals = sorted(set(signal["contract_version"].astype(str).str.strip().tolist()))
                    if len(sig_cv_vals) == 1:
                        checks.append(
                            _check(
                                "execution_trace_summary_contract_version_matches_signal_frame",
                                sm_cv == sig_cv_vals[0],
                                {"summary_contract_version": sm_cv, "signal_frame_contract_version": sig_cv_vals[0]},
                            )
                        )
                if "calibration_mode" in signal.columns:
                    sig_cm_vals = sorted(set(signal["calibration_mode"].astype(str).str.strip().str.lower().tolist()))
                    if len(sig_cm_vals) == 1:
                        checks.append(
                            _check(
                                "execution_trace_summary_calibration_mode_matches_signal_frame",
                                sm_cm == sig_cm_vals[0],
                                {"summary_calibration_mode": sm_cm, "signal_frame_calibration_mode": sig_cm_vals[0]},
                            )
                        )
            except Exception as exc:
                checks.append(_check("execution_trace_summary_parseable", False, {"error": str(exc)}))
    else:
        checks.append(_check("execution_trace_exists", False, {"path": str(trace_path)}))

    strategy_summary, strategy_summary_sep = _read_csv_auto(strategy_summary_path)
    checks.append(_check("strategy_summary_delimiter_semicolon", strategy_summary_sep == ";", {"detected_sep": strategy_summary_sep}))
    checks.append(_check("strategy_summary_row_positive", len(strategy_summary) > 0, {"rows": int(len(strategy_summary))}))
    required_strategy_cols = [
        "run_id",
        "net_return_pct",
        "trades",
        "hit_rate",
        "max_drawdown_pct",
        "sortino",
        "cagr",
        "no_trade_ratio_days",
        "trades_per_day_avg",
        "params_json",
    ]
    missing_strategy_cols = [c for c in required_strategy_cols if c not in strategy_summary.columns]
    checks.append(
        _check(
            "strategy_summary_required_columns",
            len(missing_strategy_cols) == 0,
            {"missing": missing_strategy_cols},
        )
    )
    if len(strategy_summary) > 0 and "run_id" in strategy_summary.columns:
        non_empty_run = int(strategy_summary["run_id"].astype(str).str.strip().replace({"nan": ""}).ne("").sum())
        checks.append(
            _check(
                "strategy_summary_run_id_non_empty",
                non_empty_run == int(len(strategy_summary)),
                {"non_empty": non_empty_run, "rows": int(len(strategy_summary))},
            )
        )
        # run_id consistency across signal/execution/summary tables.
        sig_runs = sorted(set(signal["run_id"].astype(str).str.strip().tolist())) if "run_id" in signal.columns else []
        trace_runs = (
            sorted(set(trace["run_id"].astype(str).str.strip().tolist()))
            if "trace" in locals() and len(trace) > 0 and "run_id" in trace.columns
            else []
        )
        summary_runs = sorted(set(strategy_summary["run_id"].astype(str).str.strip().tolist()))
        trace_rows = int(len(trace)) if "trace" in locals() else 0
        trades_summary_for_mode = (
            int(pd.to_numeric(strategy_summary["trades"], errors="coerce").fillna(-1).iloc[0])
            if "trades" in strategy_summary.columns
            else -1
        )
        allow_empty_trace_mode = bool((not args.require_trades) and trace_rows == 0 and trades_summary_for_mode == 0)
        checks.append(_check("signal_run_id_single", len(sig_runs) == 1, {"values": sig_runs}))
        checks.append(
            _check(
                "execution_trace_run_id_single",
                bool(len(trace_runs) == 1 or allow_empty_trace_mode),
                {"values": trace_runs, "allow_empty_trace_mode": allow_empty_trace_mode, "trace_rows": trace_rows},
            )
        )
        checks.append(_check("strategy_summary_run_id_single", len(summary_runs) == 1, {"values": summary_runs}))
        if allow_empty_trace_mode and len(sig_runs) == 1 and len(summary_runs) == 1:
            checks.append(
                _check(
                    "run_id_consistency_signal_trace_summary",
                    sig_runs[0] == summary_runs[0],
                    {"signal_run_id": sig_runs[0], "summary_run_id": summary_runs[0], "mode": "no_trades"},
                )
            )
        elif len(sig_runs) == 1 and len(trace_runs) == 1 and len(summary_runs) == 1:
            checks.append(
                _check(
                    "run_id_consistency_signal_trace_summary",
                    sig_runs[0] == trace_runs[0] == summary_runs[0],
                    {"signal_run_id": sig_runs[0], "trace_run_id": trace_runs[0], "summary_run_id": summary_runs[0]},
                )
            )
        else:
            checks.append(
                _check(
                    "run_id_consistency_signal_trace_summary",
                    False,
                    {"signal_runs": sig_runs, "trace_runs": trace_runs, "summary_runs": summary_runs},
                )
            )
    if len(strategy_summary) > 0 and "trades" in strategy_summary.columns and "trace" in locals():
        trades_summary = int(pd.to_numeric(strategy_summary["trades"], errors="coerce").fillna(-1).iloc[0])
        checks.append(
            _check(
                "strategy_summary_trades_match_execution_trace",
                trades_summary == int(len(trace)),
                {"strategy_summary_trades": trades_summary, "execution_trace_rows": int(len(trace))},
            )
        )
    if len(strategy_summary) > 0 and "params_json" in strategy_summary.columns:
        params_raw = str(strategy_summary["params_json"].iloc[0])
        parsed_ok = True
        parsed_obj: dict[str, Any] = {}
        try:
            parsed_obj = json.loads(params_raw)
        except Exception:
            parsed_ok = False
        checks.append(_check("strategy_summary_params_json_parseable", parsed_ok, {"length": len(params_raw)}))
        if parsed_ok:
            checks.append(
                _check(
                    "strategy_summary_params_has_strategy_and_risk_policy",
                    isinstance(parsed_obj.get("strategy"), dict) and isinstance(parsed_obj.get("risk_policy"), dict),
                    {"keys": sorted(parsed_obj.keys())},
                )
            )
    # Metric parity: strategy_summary.net_return_pct must match OOS backtest net_return_pct.
    if "trace" in locals() and len(trace) > 0 and "source_oos_report" in trace.columns and "net_return_pct" in strategy_summary.columns:
        oos_path_raw = str(trace["source_oos_report"].iloc[0]).strip()
        oos_path = Path(oos_path_raw)
        if oos_path.exists():
            try:
                oos_obj = json.loads(oos_path.read_text(encoding="utf-8"))
                oos_net = float((oos_obj.get("backtest") or {}).get("net_return_pct"))
                sum_net = float(pd.to_numeric(strategy_summary["net_return_pct"], errors="coerce").iloc[0])
                checks.append(
                    _check(
                        "strategy_summary_net_return_matches_oos_backtest",
                        abs(oos_net - sum_net) <= 1e-9,
                        {"oos_net_return_pct": oos_net, "strategy_summary_net_return_pct": sum_net},
                    )
                )
                # Totals parity: trace PnL sum and summary trades/day must match OOS backtest.
                if "net_pnl_usd" in trace.columns:
                    trace_net_total = float(pd.to_numeric(trace["net_pnl_usd"], errors="coerce").fillna(0.0).sum())
                    oos_net_total = float((oos_obj.get("backtest") or {}).get("net_pnl_total_usd", 0.0))
                    checks.append(
                        _check(
                            "execution_trace_net_pnl_total_matches_oos_backtest",
                            abs(trace_net_total - oos_net_total) <= 1e-9,
                            {"trace_net_pnl_total_usd": trace_net_total, "oos_net_pnl_total_usd": oos_net_total},
                        )
                    )
                if len(strategy_summary) > 0 and "trades_per_day_avg" in strategy_summary.columns:
                    spd_summary = float(pd.to_numeric(strategy_summary["trades_per_day_avg"], errors="coerce").fillna(0.0).iloc[0])
                    spd_oos = float((oos_obj.get("backtest") or {}).get("trades_per_day_avg", 0.0))
                    checks.append(
                        _check(
                            "strategy_summary_trades_per_day_avg_matches_oos_backtest",
                            abs(spd_summary - spd_oos) <= 1e-12,
                            {"strategy_summary_trades_per_day_avg": spd_summary, "oos_trades_per_day_avg": spd_oos},
                        )
                    )
                # Extended strategy_summary metric parity with OOS backtest.
                if len(strategy_summary) > 0:
                    bt = oos_obj.get("backtest") or {}
                    metric_pairs = [
                        ("hit_rate", "hit_rate", "strategy_summary_hit_rate_matches_oos_backtest"),
                        ("max_drawdown_pct", "max_drawdown_pct", "strategy_summary_max_drawdown_matches_oos_backtest"),
                        ("sortino", "sortino", "strategy_summary_sortino_matches_oos_backtest"),
                        ("cagr", "cagr", "strategy_summary_cagr_matches_oos_backtest"),
                        ("no_trade_ratio_days", "no_trade_ratio_days", "strategy_summary_no_trade_ratio_days_matches_oos_backtest"),
                    ]
                    for s_col, b_key, check_name in metric_pairs:
                        if s_col in strategy_summary.columns and b_key in bt:
                            s_val = strategy_summary[s_col].iloc[0]
                            b_val = bt.get(b_key)
                            ok_metric = _float_equal(s_val, b_val, atol=1e-12)
                            checks.append(
                                _check(
                                    check_name,
                                    ok_metric,
                                    {"strategy_summary": s_val, "oos_backtest": b_val, "atol": 1e-12},
                                )
                            )
                # Signal mode parity with executed sides.
                signal_mode_oos = str((oos_obj.get("risk_policy") or {}).get("signal_mode", "")).strip().lower()
                if "side" in trace.columns and signal_mode_oos in {"long_only", "short_only", "both"}:
                    side_exec = pd.to_numeric(trace["side"], errors="coerce").fillna(0).astype(int)
                    bad_mode = 0
                    if signal_mode_oos == "long_only":
                        bad_mode = int((side_exec <= 0).sum())
                    elif signal_mode_oos == "short_only":
                        bad_mode = int((side_exec >= 0).sum())
                    else:
                        bad_mode = int((~side_exec.isin([-1, 1])).sum())
                    checks.append(
                        _check(
                            "execution_side_respects_oos_signal_mode",
                            bad_mode == 0,
                            {"signal_mode": signal_mode_oos, "bad_rows": bad_mode, "rows": int(len(trace))},
                        )
                    )
                # Signal frame config parity/constancy across all bars.
                if len(signal) > 0:
                    if "signal_mode" in signal.columns and signal_mode_oos:
                        sig_mode_vals = signal["signal_mode"].astype(str).str.strip().str.lower()
                        uniq_sig_mode = sorted(set(sig_mode_vals.tolist()))
                        checks.append(_check("signal_frame_signal_mode_single", len(uniq_sig_mode) == 1, {"values": uniq_sig_mode}))
                        bad_sig_mode = int((sig_mode_vals != signal_mode_oos).sum())
                        checks.append(
                            _check(
                                "signal_frame_signal_mode_matches_oos",
                                bad_sig_mode == 0,
                                {"oos_signal_mode": signal_mode_oos, "bad_rows": bad_sig_mode, "rows": int(len(signal))},
                            )
                        )
                    # Thresholds from strategy must be constant and match OOS.
                    o_pl = (oos_obj.get("strategy") or {}).get("p_enter_long")
                    o_ps = (oos_obj.get("strategy") or {}).get("p_enter_short")
                    for col_name, o_val, check_single, check_match in [
                        ("p_enter_long", o_pl, "signal_frame_p_enter_long_single", "signal_frame_p_enter_long_matches_oos"),
                        ("p_enter_short", o_ps, "signal_frame_p_enter_short_single", "signal_frame_p_enter_short_matches_oos"),
                    ]:
                        if col_name in signal.columns:
                            c = pd.to_numeric(signal[col_name], errors="coerce")
                            uniq = sorted(set([float(x) for x in c.dropna().unique().tolist()]))
                            checks.append(_check(check_single, len(uniq) <= 1, {"values": uniq}))
                            if o_val is not None:
                                bad = int((~c.apply(lambda x: _float_equal(x, o_val, atol=1e-12))).sum())
                                checks.append(
                                    _check(
                                        check_match,
                                        bad == 0,
                                        {"oos_value": o_val, "bad_rows": bad, "rows": int(len(signal))},
                                    )
                                )
                    # Risk filter fields must be constant and match OOS.
                    risk_map = [
                        ("trend_filter", (oos_obj.get("risk_policy") or {}).get("trend_filter")),
                        ("min_abs_ema_gap", (oos_obj.get("risk_policy") or {}).get("min_abs_ema_gap")),
                        ("min_expected_move_pct", (oos_obj.get("risk_policy") or {}).get("min_expected_move_pct")),
                    ]
                    for col_name, o_val in risk_map:
                        if col_name in signal.columns:
                            svals = signal[col_name]
                            if col_name == "trend_filter":
                                norm = svals.astype(str).str.strip().str.lower()
                                uniq = sorted(set(norm.tolist()))
                                checks.append(_check(f"signal_frame_{col_name}_single", len(uniq) == 1, {"values": uniq}))
                                if o_val is not None:
                                    bad = int((norm != str(o_val).strip().lower()).sum())
                                    checks.append(
                                        _check(
                                            f"signal_frame_{col_name}_matches_oos",
                                            bad == 0,
                                            {"oos_value": o_val, "bad_rows": bad, "rows": int(len(signal))},
                                        )
                                    )
                            else:
                                num = pd.to_numeric(svals, errors="coerce")
                                uniq = sorted(set([float(x) for x in num.dropna().unique().tolist()]))
                                checks.append(_check(f"signal_frame_{col_name}_single", len(uniq) <= 1, {"values": uniq}))
                                if o_val is not None:
                                    bad = int((~num.apply(lambda x: _float_equal(x, o_val, atol=1e-12))).sum())
                                    checks.append(
                                        _check(
                                            f"signal_frame_{col_name}_matches_oos",
                                            bad == 0,
                                            {"oos_value": o_val, "bad_rows": bad, "rows": int(len(signal))},
                                        )
                                    )
                # Execution metadata parity between trace rows and oos risk policy.
                o_exec_mode = str((oos_obj.get("risk_policy") or {}).get("execution_mode", "")).strip().lower()
                o_order_type = str((oos_obj.get("risk_policy") or {}).get("order_type", "")).strip().lower()
                if "execution_mode" in trace.columns:
                    em = trace["execution_mode"].astype(str).str.strip().str.lower()
                    bad_em = int((em != o_exec_mode).sum()) if o_exec_mode else 0
                    checks.append(
                        _check(
                            "execution_trace_execution_mode_matches_oos",
                            bad_em == 0,
                            {"oos_execution_mode": o_exec_mode, "bad_rows": bad_em, "rows": int(len(trace))},
                        )
                    )
                if "order_type" in trace.columns:
                    ot = trace["order_type"].astype(str).str.strip().str.lower()
                    bad_ot = int((ot != o_order_type).sum()) if o_order_type else 0
                    checks.append(
                        _check(
                            "execution_trace_order_type_matches_oos",
                            bad_ot == 0,
                            {"oos_order_type": o_order_type, "bad_rows": bad_ot, "rows": int(len(trace))},
                        )
                    )
                # Params parity between strategy_summary.params_json and oos_report.
                if len(strategy_summary) > 0 and "params_json" in strategy_summary.columns:
                    params_raw = str(strategy_summary["params_json"].iloc[0])
                    try:
                        params_obj = json.loads(params_raw)
                        p_strategy = (params_obj.get("strategy") or {}) if isinstance(params_obj, dict) else {}
                        p_risk = (params_obj.get("risk_policy") or {}) if isinstance(params_obj, dict) else {}
                        o_strategy = oos_obj.get("strategy") or {}
                        o_risk = oos_obj.get("risk_policy") or {}

                        mode_ok = str(p_risk.get("signal_mode", "")).lower() == str(o_risk.get("signal_mode", "")).lower()
                        exec_ok = str(p_risk.get("execution_mode", "")).lower() == str(o_risk.get("execution_mode", "")).lower()
                        order_ok = str(p_risk.get("order_type", "")).lower() == str(o_risk.get("order_type", "")).lower()
                        checks.append(
                            _check(
                                "strategy_summary_params_mode_match_oos",
                                mode_ok and exec_ok and order_ok,
                                {
                                    "params_signal_mode": p_risk.get("signal_mode"),
                                    "oos_signal_mode": o_risk.get("signal_mode"),
                                    "params_execution_mode": p_risk.get("execution_mode"),
                                    "oos_execution_mode": o_risk.get("execution_mode"),
                                    "params_order_type": p_risk.get("order_type"),
                                    "oos_order_type": o_risk.get("order_type"),
                                },
                            )
                        )

                        lev_ok = abs(float(p_risk.get("leverage", 0.0)) - float(o_risk.get("leverage", 0.0))) <= 1e-12
                        notion_ok = abs(float(p_risk.get("notional_usd", 0.0)) - float(o_risk.get("notional_usd", 0.0))) <= 1e-12
                        fee_ok = abs(float(p_strategy.get("fee_bps", 0.0)) - float(o_strategy.get("fee_bps", 0.0))) <= 1e-12
                        slip_ok = abs(float(p_strategy.get("slippage_bps", 0.0)) - float(o_strategy.get("slippage_bps", 0.0))) <= 1e-12
                        checks.append(
                            _check(
                                "strategy_summary_params_numeric_match_oos",
                                lev_ok and notion_ok and fee_ok and slip_ok,
                                {
                                    "params_leverage": p_risk.get("leverage"),
                                    "oos_leverage": o_risk.get("leverage"),
                                    "params_notional_usd": p_risk.get("notional_usd"),
                                    "oos_notional_usd": o_risk.get("notional_usd"),
                                    "params_fee_bps": p_strategy.get("fee_bps"),
                                    "oos_fee_bps": o_strategy.get("fee_bps"),
                                    "params_slippage_bps": p_strategy.get("slippage_bps"),
                                    "oos_slippage_bps": o_strategy.get("slippage_bps"),
                                },
                            )
                        )
                        # Extended parity for risk/strategy fields.
                        extended_pairs = [
                            ("risk_policy", "stop_loss_pct"),
                            ("risk_policy", "take_profit_pct"),
                            ("risk_policy", "min_expected_move_pct"),
                            ("risk_policy", "tp_min_factor"),
                            ("risk_policy", "cooldown_bars"),
                            ("risk_policy", "trend_filter"),
                            ("risk_policy", "min_abs_ema_gap"),
                            ("risk_policy", "dynamic_tp_enabled"),
                            ("strategy", "horizon_bars"),
                            ("strategy", "p_enter_long"),
                            ("strategy", "p_enter_short"),
                        ]
                        bad_ext: list[dict[str, Any]] = []
                        for section, key in extended_pairs:
                            if section == "risk_policy":
                                pv = p_risk.get(key)
                                ov = o_risk.get(key)
                            else:
                                pv = p_strategy.get(key)
                                ov = o_strategy.get(key)
                            if not _scalar_equal(pv, ov):
                                bad_ext.append({"section": section, "key": key, "params_value": pv, "oos_value": ov})
                        checks.append(
                            _check(
                                "strategy_summary_params_extended_match_oos",
                                len(bad_ext) == 0,
                                {"mismatches": bad_ext, "checked_fields": len(extended_pairs)},
                            )
                        )
                    except Exception as exc:
                        checks.append(_check("strategy_summary_params_match_oos_parseable", False, {"error": str(exc)}))
                # PnL/return consistency with oos notional_usd.
                notional_usd = float((oos_obj.get("risk_policy") or {}).get("notional_usd", 0.0) or 0.0)
                leverage_oos = float((oos_obj.get("risk_policy") or {}).get("leverage", 0.0) or 0.0)
                if notional_usd > 0 and "net_return" in trace.columns and "net_pnl_usd" in trace.columns:
                    expected_net_pnl = pd.to_numeric(trace["net_return"], errors="coerce") * notional_usd
                    ok_pnl_ret, bad_pnl_ret = _allclose_series(expected_net_pnl, trace["net_pnl_usd"], atol=1e-9)
                    checks.append(
                        _check(
                            "execution_trace_net_pnl_matches_net_return_times_notional",
                            ok_pnl_ret,
                            {
                                "bad_rows": bad_pnl_ret,
                                "rows": int(len(trace)),
                                "notional_usd": notional_usd,
                                "atol": 1e-9,
                            },
                        )
                    )
                # Return/leverage consistency checks.
                if leverage_oos > 0 and "net_return" in trace.columns and "net_return_unlevered" in trace.columns:
                    expected_net_return = pd.to_numeric(trace["net_return_unlevered"], errors="coerce") * leverage_oos
                    ok_nr, bad_nr = _allclose_series(expected_net_return, trace["net_return"], atol=1e-9)
                    checks.append(
                        _check(
                            "execution_net_return_matches_unlevered_times_leverage",
                            ok_nr,
                            {"bad_rows": bad_nr, "rows": int(len(trace)), "leverage": leverage_oos, "atol": 1e-9},
                        )
                    )
                if leverage_oos > 0 and notional_usd > 0 and "gross_return" in trace.columns and "gross_pnl_usd" in trace.columns:
                    expected_gross_pnl = pd.to_numeric(trace["gross_return"], errors="coerce") * leverage_oos * notional_usd
                    ok_gr, bad_gr = _allclose_series(expected_gross_pnl, trace["gross_pnl_usd"], atol=1e-9)
                    checks.append(
                        _check(
                            "execution_gross_pnl_matches_gross_return_times_notional_and_leverage",
                            ok_gr,
                            {
                                "bad_rows": bad_gr,
                                "rows": int(len(trace)),
                                "notional_usd": notional_usd,
                                "leverage": leverage_oos,
                                "atol": 1e-9,
                            },
                        )
                    )
                # OOS window alignment: all signal/execution timestamps must be inside [test_day, test_end_day].
                test_day = str(oos_obj.get("test_day", "")).strip()
                test_end_day = str(oos_obj.get("test_end_day", test_day)).strip()
                if test_day and test_end_day:
                    w_start = pd.Timestamp(test_day, tz="UTC")
                    w_end_exclusive = pd.Timestamp(test_end_day, tz="UTC") + pd.Timedelta(days=1)
                    if "open_time_utc" in signal.columns:
                        sig_ts = pd.to_datetime(signal["open_time_utc"], utc=True, errors="coerce")
                        sig_bad = int(((sig_ts < w_start) | (sig_ts >= w_end_exclusive)).sum())
                        checks.append(
                            _check(
                                "signal_frame_within_oos_window",
                                sig_bad == 0,
                                {"bad_rows": sig_bad, "window_start": str(w_start), "window_end_exclusive": str(w_end_exclusive)},
                            )
                        )
                    for col_name in ["signal_time_utc", "entry_time_utc", "exit_time_utc"]:
                        if col_name in trace.columns:
                            tr_ts = pd.to_datetime(trace[col_name], utc=True, errors="coerce")
                            tr_bad = int(((tr_ts < w_start) | (tr_ts >= w_end_exclusive)).sum())
                            checks.append(
                                _check(
                                    f"execution_{col_name}_within_oos_window",
                                    tr_bad == 0,
                                    {"bad_rows": tr_bad, "window_start": str(w_start), "window_end_exclusive": str(w_end_exclusive)},
                                )
                            )
            except Exception as exc:
                checks.append(_check("strategy_summary_net_return_matches_oos_backtest", False, {"error": str(exc), "oos_path": oos_path_raw}))
        else:
            checks.append(_check("strategy_summary_net_return_matches_oos_backtest", False, {"oos_path": oos_path_raw, "reason": "oos_report_missing"}))
    # Backtest source parity: executed trades from OOS backtest CSV must match execution_trace and summary.
    if "trace" in locals() and len(trace) > 0 and "source_backtest_csv" in trace.columns:
        bt_path_raw = str(trace["source_backtest_csv"].iloc[0]).strip()
        bt_path = Path(bt_path_raw)
        if bt_path.exists():
            try:
                bt_df, bt_sep = _read_csv_auto(bt_path)
                checks.append(_check("oos_backtest_csv_parseable", True, {"path": bt_path_raw, "detected_sep": bt_sep, "rows": int(len(bt_df))}))
                # Signal frame should be built from the same bar set as OOS backtest rows.
                checks.append(
                    _check(
                        "signal_frame_rows_match_oos_backtest_rows",
                        int(len(signal)) == int(len(bt_df)),
                        {"signal_rows": int(len(signal)), "oos_backtest_rows": int(len(bt_df))},
                    )
                )
                if "open_time_utc" in signal.columns and "open_time_utc" in bt_df.columns and len(signal) > 0 and len(bt_df) > 0:
                    sig_ts = pd.to_datetime(signal["open_time_utc"], utc=True, errors="coerce")
                    bt_ts = pd.to_datetime(bt_df["open_time_utc"], utc=True, errors="coerce")
                    sig_min, sig_max = sig_ts.min(), sig_ts.max()
                    bt_min, bt_max = bt_ts.min(), bt_ts.max()
                    checks.append(
                        _check(
                            "signal_frame_time_range_match_oos_backtest",
                            (sig_min == bt_min) and (sig_max == bt_max),
                            {
                                "signal_min": str(sig_min),
                                "signal_max": str(sig_max),
                                "oos_backtest_min": str(bt_min),
                                "oos_backtest_max": str(bt_max),
                            },
                        )
                    )
                    # Per-bar parity between signal_frame and oos_backtest source.
                    sig_cmp = signal.copy()
                    bt_cmp = bt_df.copy()
                    sig_cmp["open_time_utc"] = sig_ts
                    bt_cmp["open_time_utc"] = bt_ts
                    cols_need = ["open_time_utc", "prob_up", "side_executed"]
                    if all(c in sig_cmp.columns for c in cols_need) and all(c in bt_cmp.columns for c in ["open_time_utc", "prob_up", "side"]):
                        merged = sig_cmp[cols_need].merge(
                            bt_cmp[["open_time_utc", "prob_up", "side"]],
                            on="open_time_utc",
                            how="outer",
                            suffixes=("_signal", "_bt"),
                            indicator=True,
                        )
                        only_signal = int((merged["_merge"] == "left_only").sum())
                        only_bt = int((merged["_merge"] == "right_only").sum())
                        checks.append(
                            _check(
                                "signal_backtest_open_time_full_match",
                                only_signal == 0 and only_bt == 0,
                                {"only_signal": only_signal, "only_backtest": only_bt},
                            )
                        )
                        both = merged[merged["_merge"] == "both"].copy()
                        if len(both) > 0:
                            prob_sig = pd.to_numeric(both["prob_up_signal"], errors="coerce")
                            prob_bt = pd.to_numeric(both["prob_up_bt"], errors="coerce")
                            prob_bad = int(((prob_sig - prob_bt).abs() > 1e-12).sum())
                            checks.append(
                                _check(
                                    "signal_backtest_prob_up_match",
                                    prob_bad == 0,
                                    {"bad_rows": prob_bad, "rows": int(len(both)), "atol": 1e-12},
                                )
                            )
                            side_sig = pd.to_numeric(both["side_executed"], errors="coerce").fillna(0).astype(int)
                            side_bt = pd.to_numeric(both["side"], errors="coerce").fillna(0).astype(int)
                            side_bad = int((side_sig != side_bt).sum())
                            checks.append(
                                _check(
                                    "signal_backtest_side_match",
                                    side_bad == 0,
                                    {"bad_rows": side_bad, "rows": int(len(both))},
                                )
                            )
                            for field, atol in [("expected_move_pct", 1e-12), ("ev", 1e-12), ("ev_usd", 1e-9)]:
                                fs = f"{field}_signal"
                                fb = f"{field}_bt"
                                if fs in both.columns and fb in both.columns:
                                    vs = pd.to_numeric(both[fs], errors="coerce")
                                    vb = pd.to_numeric(both[fb], errors="coerce")
                                    bad = int(((vs - vb).abs() > atol).sum())
                                    checks.append(
                                        _check(
                                            f"signal_backtest_{field}_match",
                                            bad == 0,
                                            {"bad_rows": bad, "rows": int(len(both)), "atol": atol},
                                        )
                                    )
                if "side" in bt_df.columns:
                    bt_side = pd.to_numeric(bt_df["side"], errors="coerce").fillna(0.0)
                    bt_exec_rows = int((bt_side.abs() > 0).sum())
                    checks.append(
                        _check(
                            "oos_backtest_executed_rows_match_execution_trace",
                            bt_exec_rows == int(len(trace)),
                            {"oos_backtest_executed_rows": bt_exec_rows, "execution_trace_rows": int(len(trace))},
                        )
                    )
                    if len(strategy_summary) > 0 and "trades" in strategy_summary.columns:
                        trades_summary = int(pd.to_numeric(strategy_summary["trades"], errors="coerce").fillna(-1).iloc[0])
                        checks.append(
                            _check(
                                "oos_backtest_executed_rows_match_strategy_summary_trades",
                                bt_exec_rows == trades_summary,
                                {"oos_backtest_executed_rows": bt_exec_rows, "strategy_summary_trades": trades_summary},
                            )
                        )
                    # Row-level parity between execution_trace and executed rows from oos_backtest.
                    bt_exec = bt_df[bt_side.abs() > 0].copy().reset_index(drop=True)
                    if len(bt_exec) > 0 and all(c in bt_exec.columns for c in ["open_time_utc", "side"]):
                        bt_exec["open_time_utc"] = pd.to_datetime(bt_exec["open_time_utc"], utc=True, errors="coerce")
                        bt_exec["side"] = pd.to_numeric(bt_exec["side"], errors="coerce").fillna(0).astype(int)
                        tr_cmp = trace.copy()
                        tr_cmp["signal_time_utc"] = pd.to_datetime(tr_cmp["signal_time_utc"], utc=True, errors="coerce")
                        tr_cmp["side"] = pd.to_numeric(tr_cmp["side"], errors="coerce").fillna(0).astype(int)
                        bt_dup = int(bt_exec.duplicated(subset=["open_time_utc", "side"]).sum())
                        tr_dup = int(tr_cmp.duplicated(subset=["signal_time_utc", "side"]).sum())
                        checks.append(_check("oos_backtest_exec_key_unique", bt_dup == 0, {"duplicates": bt_dup}))
                        checks.append(_check("execution_trace_key_unique", tr_dup == 0, {"duplicates": tr_dup}))

                        merged_exec = tr_cmp.merge(
                            bt_exec,
                            left_on=["signal_time_utc", "side"],
                            right_on=["open_time_utc", "side"],
                            how="inner",
                            suffixes=("_trace", "_bt"),
                        )
                        checks.append(
                            _check(
                                "execution_trace_rows_match_oos_backtest_exec_keys",
                                int(len(merged_exec)) == int(len(tr_cmp)) == int(len(bt_exec)),
                                {"merged_rows": int(len(merged_exec)), "trace_rows": int(len(tr_cmp)), "oos_exec_rows": int(len(bt_exec))},
                            )
                        )
                        if len(merged_exec) > 0:
                            for base, name in [
                                ("entry_time_utc", "execution_entry_time_match_oos_backtest"),
                                ("exit_time_utc", "execution_exit_time_match_oos_backtest"),
                                ("entry_price", "execution_entry_price_match_oos_backtest"),
                                ("exit_price", "execution_exit_price_match_oos_backtest"),
                                ("net_pnl_usd", "execution_net_pnl_match_oos_backtest"),
                            ]:
                                tcol = f"{base}_trace"
                                bcol = f"{base}_bt"
                                if tcol in merged_exec.columns and bcol in merged_exec.columns:
                                    if "time" in base:
                                        tv = pd.to_datetime(merged_exec[tcol], utc=True, errors="coerce")
                                        bv = pd.to_datetime(merged_exec[bcol], utc=True, errors="coerce")
                                        bad = int((tv != bv).sum())
                                        checks.append(_check(name, bad == 0, {"bad_rows": bad, "rows": int(len(merged_exec))}))
                                    else:
                                        tv = pd.to_numeric(merged_exec[tcol], errors="coerce")
                                        bv = pd.to_numeric(merged_exec[bcol], errors="coerce")
                                        bad = int(((tv - bv).abs() > 1e-9).sum())
                                        checks.append(_check(name, bad == 0, {"bad_rows": bad, "rows": int(len(merged_exec)), "atol": 1e-9}))
                            if "exit_reason_trace" in merged_exec.columns and "exit_reason_bt" in merged_exec.columns:
                                er_t = merged_exec["exit_reason_trace"].astype(str).str.strip()
                                er_b = merged_exec["exit_reason_bt"].astype(str).str.strip()
                                bad_er = int((er_t != er_b).sum())
                                checks.append(_check("execution_exit_reason_match_oos_backtest", bad_er == 0, {"bad_rows": bad_er, "rows": int(len(merged_exec))}))
                else:
                    checks.append(_check("oos_backtest_has_side_column", False, {"columns": [str(c) for c in bt_df.columns]}))
            except Exception as exc:
                checks.append(_check("oos_backtest_csv_parseable", False, {"path": bt_path_raw, "error": str(exc)}))
        else:
            checks.append(_check("oos_backtest_csv_exists", False, {"path": bt_path_raw}))

    # Canonical ML-runtime signal contract parity across inference and TA signal layers.
    inference_exists = bool(inference_events_path and inference_events_path.exists())
    signal_events_exists = bool(signal_events_path.exists())
    checks.append(
        _check(
            "inference_events_csv_exists",
            inference_exists,
            {"path": str(inference_events_path) if inference_events_path else None},
        )
    )
    checks.append(_check("signal_events_csv_exists", signal_events_exists, {"path": str(signal_events_path)}))
    if inference_exists:
        inference_events, inference_sep = _read_csv_auto(inference_events_path)
        checks.append(_check("inference_events_rows_positive", len(inference_events) > 0, {"rows": int(len(inference_events)), "sep": inference_sep}))
        checks.extend(_signal_contract_checks(inference_events, "inference_events"))
    if signal_events_exists:
        signal_events, signal_events_sep = _read_csv_auto(signal_events_path)
        checks.append(_check("signal_events_rows_positive", len(signal_events) > 0, {"rows": int(len(signal_events)), "sep": signal_events_sep}))
        checks.extend(_signal_contract_checks(signal_events, "signal_events"))
    if inference_exists and signal_events_exists:
        inference_events, _ = _read_csv_auto(inference_events_path)
        signal_events, _ = _read_csv_auto(signal_events_path)
        inf_contract_cols = [c for c in CANONICAL_SIGNAL_CONTRACT_COLUMNS if c in inference_events.columns]
        ta_contract_cols = [c for c in CANONICAL_SIGNAL_CONTRACT_COLUMNS if c in signal_events.columns]
        checks.append(
            _check(
                "inference_and_ta_signal_contract_columns_identical",
                inf_contract_cols == ta_contract_cols == CANONICAL_SIGNAL_CONTRACT_COLUMNS,
                {"inference_cols": inf_contract_cols, "signal_events_cols": ta_contract_cols},
            )
        )
        inf_side_kind = _side_representation_kind(inference_events["side"]) if "side" in inference_events.columns else "missing"
        ta_side_kind = _side_representation_kind(signal_events["side"]) if "side" in signal_events.columns else "missing"
        checks.append(
            _check(
                "inference_and_ta_side_representation_identical",
                inf_side_kind == ta_side_kind,
                {"inference_side_kind": inf_side_kind, "signal_events_side_kind": ta_side_kind},
            )
        )
        inf_ts_kind = "utc_z" if inference_events["signal_time_utc"].astype(str).str.endswith("Z").all() else "utc_offset"
        ta_ts_kind = "utc_z" if signal_events["signal_time_utc"].astype(str).str.endswith("Z").all() else "utc_offset"
        checks.append(
            _check(
                "inference_and_ta_signal_time_representation_identical",
                inf_ts_kind == ta_ts_kind,
                {"inference_signal_time_kind": inf_ts_kind, "signal_events_signal_time_kind": ta_ts_kind},
            )
        )
    # Report-level runtime contract metadata parity.
    inf_report_exists = bool(inference_report_path and inference_report_path.exists())
    ta_report_exists = bool(ta_report_path and ta_report_path.exists())
    checks.append(_check("inference_report_json_exists", inf_report_exists, {"path": str(inference_report_path) if inference_report_path else None}))
    checks.append(_check("ta_report_json_exists", ta_report_exists, {"path": str(ta_report_path) if ta_report_path else None}))
    if inf_report_exists:
        try:
            inf_report = _read_json(inference_report_path)
            inf_ver = str(inf_report.get("contract_version", "")).strip()
            inf_cal = str(inf_report.get("calibration_mode", "")).strip().lower()
            checks.append(_check("inference_report_contract_version_non_empty", bool(inf_ver), {"contract_version": inf_ver}))
            checks.append(_check("inference_report_calibration_mode_none", inf_cal == "none", {"calibration_mode": inf_cal}))
        except Exception as exc:
            checks.append(_check("inference_report_json_parseable", False, {"error": str(exc), "path": str(inference_report_path)}))
    if ta_report_exists:
        try:
            ta_report = _read_json(ta_report_path)
            ta_ver = str(ta_report.get("contract_version", "")).strip()
            ta_cal = str(ta_report.get("calibration_mode", "")).strip().lower()
            checks.append(_check("ta_report_contract_version_non_empty", bool(ta_ver), {"contract_version": ta_ver}))
            checks.append(_check("ta_report_calibration_mode_none", ta_cal == "none", {"calibration_mode": ta_cal}))
        except Exception as exc:
            checks.append(_check("ta_report_json_parseable", False, {"error": str(exc), "path": str(ta_report_path)}))
    if inf_report_exists and ta_report_exists:
        try:
            inf_report = _read_json(inference_report_path)
            ta_report = _read_json(ta_report_path)
            inf_ver = str(inf_report.get("contract_version", "")).strip()
            ta_ver = str(ta_report.get("contract_version", "")).strip()
            inf_cal = str(inf_report.get("calibration_mode", "")).strip().lower()
            ta_cal = str(ta_report.get("calibration_mode", "")).strip().lower()
            checks.append(
                _check(
                    "inference_and_ta_report_contract_version_identical",
                    bool(inf_ver) and (inf_ver == ta_ver),
                    {"inference_contract_version": inf_ver, "ta_contract_version": ta_ver},
                )
            )
            checks.append(
                _check(
                    "inference_and_ta_report_calibration_mode_identical",
                    inf_cal == ta_cal == "none",
                    {"inference_calibration_mode": inf_cal, "ta_calibration_mode": ta_cal},
                )
            )
        except Exception as exc:
            checks.append(_check("inference_and_ta_report_meta_compare_parseable", False, {"error": str(exc)}))

    # CSV <-> XLSX parity checks for user-facing readability.
    csv_xlsx_pairs = [
        ("candles_canonical", candles_path, candles_xlsx_path, "candles_canonical"),
        ("feature_frame_full", feature_full_path, feature_full_xlsx_path, "feature_frame_full"),
        ("feature_frame", feature_train_path, feature_train_xlsx_path, "feature_frame"),
        ("signal_frame", signal_path, signal_xlsx_path, "signal_frame"),
        ("execution_trace", trace_path, trace_xlsx_path, "execution_trace"),
        ("strategy_summary", strategy_summary_path, strategy_summary_xlsx_path, "strategy_summary"),
    ]
    for table_name, csv_path, xlsx_path, sheet_name in csv_xlsx_pairs:
        csv_df, _ = _read_csv_auto(csv_path)
        xlsx_df = _read_xlsx_auto(xlsx_path, sheet_name=sheet_name)
        csv_cols = [str(c) for c in csv_df.columns]
        xlsx_cols = [str(c) for c in xlsx_df.columns]
        checks.append(
            _check(
                f"{table_name}_xlsx_columns_match_csv",
                csv_cols == xlsx_cols,
                {"csv_cols_count": len(csv_cols), "xlsx_cols_count": len(xlsx_cols)},
            )
        )
        checks.append(
            _check(
                f"{table_name}_xlsx_rows_match_csv",
                int(len(csv_df)) == int(len(xlsx_df)),
                {"csv_rows": int(len(csv_df)), "xlsx_rows": int(len(xlsx_df))},
            )
        )

    failed = int(sum(1 for c in checks if not c["ok"]))
    payload = {
        "status": "PASS" if failed == 0 else "FAIL",
        "generated_at_utc": _utc_now_iso(),
        "checks": checks,
        "summary": {"total": len(checks), "failed": failed},
    }
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "report_path": str(report_path), "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
