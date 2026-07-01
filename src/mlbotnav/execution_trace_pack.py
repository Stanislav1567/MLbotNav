from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from mlbotnav.pct_units import normalize_min_expected_move_pct
from mlbotnav.runtime_contract import CALIBRATION_MODE_NONE, SIGNAL_CONTRACT_VERSION
from mlbotnav.runtime_trading_fields import build_runtime_trading_fields


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _detect_sep(path: Path) -> str:
    try:
        df = pd.read_csv(path, sep=";")
        if df.shape[1] > 1:
            return ";"
    except Exception:
        pass
    return ","


def _latest_oos_report(project_root: Path) -> Path:
    files = sorted(
        (project_root / "reports" / "final_review").glob("oos_report_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not files:
        raise FileNotFoundError("No oos_report_*.json found in reports/final_review")
    return files[0]


def _side_by_prob(prob: float, p_long: float, p_short: float) -> int:
    if prob >= p_long:
        return 1
    if prob <= p_short:
        return -1
    return 0


def _apply_mode(side: int, mode: str) -> int:
    m = str(mode or "both").strip().lower()
    if m == "long_only" and side < 0:
        return 0
    if m == "short_only" and side > 0:
        return 0
    return side


def _split_cost_usd(total_cost_usd: float, fee_bps: float, slippage_bps: float) -> tuple[float, float]:
    bps = float(fee_bps) + float(slippage_bps)
    if bps <= 0:
        return 0.0, 0.0
    fee_share = float(fee_bps) / bps
    fee_usd = total_cost_usd * fee_share
    slip_usd = total_cost_usd - fee_usd
    return float(fee_usd), float(slip_usd)


def _excel_safe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Excel cannot store timezone-aware datetimes.
    Convert tz-aware datetime columns to UTC naive before XLSX export.
    """
    out = df.copy()
    for col in out.columns:
        s = out[col]
        if isinstance(s.dtype, pd.DatetimeTZDtype):
            out[col] = s.dt.tz_convert("UTC").dt.tz_localize(None)
    return out


def _col_or_default(frame: pd.DataFrame, name: str, default: object) -> pd.Series:
    if name in frame.columns:
        return frame[name]
    return pd.Series([default] * len(frame), index=frame.index)


def main() -> int:
    parser = argparse.ArgumentParser(description="P3: build signal_frame and execution_trace from OOS artifacts")
    parser.add_argument("--oos-report", default=None, help="Path to oos_report_*.json. Default: latest from reports/final_review")
    parser.add_argument("--output-dir", default="reports/table_canon_current/data", help="Output directory")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    oos_report_path = Path(args.oos_report) if args.oos_report else _latest_oos_report(project_root)
    if not oos_report_path.is_absolute():
        oos_report_path = (project_root / oos_report_path).resolve()
    if not oos_report_path.exists():
        raise FileNotFoundError(f"OOS report not found: {oos_report_path}")

    oos = _load_json(oos_report_path)
    artifacts = oos.get("artifacts") or {}
    backtest_path = Path(str(artifacts.get("backtest_path", ""))).resolve()
    if not backtest_path.exists():
        raise FileNotFoundError(f"Backtest CSV not found: {backtest_path}")

    out_dir = (project_root / args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    sep = _detect_sep(backtest_path)
    bt = pd.read_csv(backtest_path, sep=sep)
    for c in ["open_time_utc", "entry_time_utc", "exit_time_utc"]:
        if c in bt.columns:
            bt[c] = pd.to_datetime(bt[c], utc=True, errors="coerce")

    strategy = oos.get("strategy") or {}
    risk = oos.get("risk_policy") or {}
    p_long = float(strategy.get("p_enter_long", 0.55))
    p_short = float(strategy.get("p_enter_short", 0.45))
    signal_mode = str(risk.get("signal_mode", "both"))
    trend_filter = str(risk.get("trend_filter", "none"))
    min_abs_ema_gap = float(risk.get("min_abs_ema_gap", 0.0))
    min_expected_move_pct = normalize_min_expected_move_pct(risk.get("min_expected_move_pct", 0.0))
    fee_bps = float(strategy.get("fee_bps", 10.0))
    slippage_bps = float(strategy.get("slippage_bps", 5.0))
    leverage = float(risk.get("leverage", 1.0))
    notional_usd = float(risk.get("notional_usd", 10.0))
    execution_mode = str(risk.get("execution_mode", "research"))
    order_type = str(risk.get("order_type", "market"))

    run_id = f"trace_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"

    # Signal frame: all bars with model probability and signal stages.
    signal = pd.DataFrame()
    signal["open_time_utc"] = bt["open_time_utc"]
    signal["prob_up"] = bt.get("prob_up", 0.5)
    signal["p_enter_long"] = p_long
    signal["p_enter_short"] = p_short
    signal["signal_mode"] = signal_mode
    signal["trend_filter"] = trend_filter
    signal["min_abs_ema_gap"] = min_abs_ema_gap
    signal["min_expected_move_pct"] = min_expected_move_pct
    signal["side_raw"] = signal["prob_up"].apply(lambda x: _side_by_prob(float(x), p_long, p_short))
    signal["side_mode_filtered"] = signal["side_raw"].apply(lambda s: _apply_mode(int(s), signal_mode))
    signal["side_executed"] = bt.get("side", 0).astype(int)
    signal["expected_move_pct"] = bt.get("expected_move_pct", 0.0)
    signal["ev"] = bt.get("ev", 0.0)
    signal["ev_usd"] = bt.get("ev_usd", 0.0)
    signal["contract_version"] = SIGNAL_CONTRACT_VERSION
    signal["calibration_mode"] = CALIBRATION_MODE_NONE
    signal["run_id"] = run_id

    # Execution trace: only executed trades.
    t = bt[(bt.get("side", 0) != 0)].copy().reset_index(drop=True)
    trace = pd.DataFrame()
    trace["trade_id"] = [f"{run_id}_{i+1:05d}" for i in range(len(t))]
    trace["signal_time_utc"] = t.get("open_time_utc").to_numpy()
    trace["entry_time_utc"] = t.get("entry_time_utc").to_numpy()
    trace["exit_time_utc"] = t.get("exit_time_utc").to_numpy()
    trace["order_type"] = order_type
    trace["execution_mode"] = execution_mode
    trace["side"] = t.get("side", 0).astype(int).to_numpy()
    trace["entry_price"] = t.get("entry_price", 0.0).to_numpy()
    trace["exit_price"] = t.get("exit_price", 0.0).to_numpy()
    trace["gross_return"] = t.get("gross_return", 0.0).to_numpy()
    trace["net_return_unlevered"] = t.get("net_return_unlevered", 0.0).to_numpy()
    trace["net_return"] = t.get("net_return", 0.0).to_numpy()
    trace["gross_pnl_usd"] = trace["gross_return"].astype(float) * leverage * notional_usd
    trace["net_pnl_usd"] = t.get("net_pnl_usd", 0.0).to_numpy()
    total_cost_usd = (trace["gross_pnl_usd"] - trace["net_pnl_usd"]).astype(float)
    fee_usd: list[float] = []
    slip_usd: list[float] = []
    for v in total_cost_usd.tolist():
        f, s = _split_cost_usd(float(v), fee_bps=fee_bps, slippage_bps=slippage_bps)
        fee_usd.append(f)
        slip_usd.append(s)
    trace["fee_usd_est"] = fee_usd
    trace["slippage_usd_est"] = slip_usd
    trace["expected_move_pct"] = _col_or_default(t, "expected_move_pct", 0.0).to_numpy()
    trace["dynamic_tp_initial_pct"] = _col_or_default(t, "dynamic_tp_initial_pct", 0.0).to_numpy()
    trace["dynamic_tp_pct"] = _col_or_default(t, "dynamic_tp_pct", 0.0).to_numpy()
    trace["dynamic_tp_update_count"] = _col_or_default(t, "dynamic_tp_update_count", 0).to_numpy()
    trace["dynamic_tp_events_json"] = _col_or_default(t, "dynamic_tp_events_json", "").to_numpy()
    trace["final_tp_price"] = _col_or_default(t, "final_tp_price", 0.0).to_numpy()
    trace["time_to_target_bars"] = _col_or_default(t, "time_to_target_bars", None).to_numpy()
    trace["time_to_target_sec"] = _col_or_default(t, "time_to_target_sec", None).to_numpy()
    trace["exit_reason"] = _col_or_default(t, "exit_reason", "").to_numpy()
    trace["contract_version"] = SIGNAL_CONTRACT_VERSION
    trace["calibration_mode"] = CALIBRATION_MODE_NONE
    trace["run_id"] = run_id
    trace["source_oos_report"] = str(oos_report_path)
    trace["source_backtest_csv"] = str(backtest_path)

    # Save files (Excel-friendly + xlsx).
    sig_csv = out_dir / "signal_frame.csv"
    sig_xlsx = out_dir / "signal_frame.xlsx"
    trace_csv = out_dir / "execution_trace.csv"
    trace_xlsx = out_dir / "execution_trace.xlsx"
    strategy_summary_csv = out_dir / "strategy_summary.csv"
    strategy_summary_xlsx = out_dir / "strategy_summary.xlsx"

    signal.to_csv(sig_csv, index=False, sep=";", encoding="utf-8-sig")
    trace.to_csv(trace_csv, index=False, sep=";", encoding="utf-8-sig")
    signal_xlsx_df = _excel_safe(signal)
    trace_xlsx_df = _excel_safe(trace)
    with pd.ExcelWriter(sig_xlsx, engine="xlsxwriter") as w:
        signal_xlsx_df.to_excel(w, sheet_name="signal_frame", index=False)
    with pd.ExcelWriter(trace_xlsx, engine="xlsxwriter") as w:
        trace_xlsx_df.to_excel(w, sheet_name="execution_trace", index=False)

    backtest = oos.get("backtest") or {}
    strategy_summary_df = pd.DataFrame(
        [
            {
                "run_id": run_id,
                "net_return_pct": float(backtest.get("net_return_pct", 0.0)),
                "trades": int(backtest.get("trades", len(trace))),
                "hit_rate": float(backtest.get("hit_rate", 0.0)),
                "max_drawdown_pct": float(backtest.get("max_drawdown_pct", 0.0)),
                "sortino": backtest.get("sortino"),
                "cagr": backtest.get("cagr"),
                "no_trade_ratio_days": backtest.get("no_trade_ratio_days"),
                "trades_per_day_avg": backtest.get("trades_per_day_avg"),
                "contract_version": SIGNAL_CONTRACT_VERSION,
                "calibration_mode": CALIBRATION_MODE_NONE,
                "params_json": json.dumps(
                    {
                        "strategy": strategy,
                        "risk_policy": risk,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
            }
        ]
    )
    strategy_summary_df.to_csv(strategy_summary_csv, index=False, sep=";", encoding="utf-8-sig")
    with pd.ExcelWriter(strategy_summary_xlsx, engine="xlsxwriter") as w:
        strategy_summary_df.to_excel(w, sheet_name="strategy_summary", index=False)

    summary = {
        "generated_at_utc": _utc_now_iso(),
        "run_id": run_id,
        "source_oos_report": str(oos_report_path),
        "source_backtest_csv": str(backtest_path),
        "signal_rows": int(len(signal)),
        "execution_rows": int(len(trace)),
        "execution_mode": execution_mode,
        "order_type": order_type,
        "signal_mode": signal_mode,
        "contract_version": SIGNAL_CONTRACT_VERSION,
        "calibration_mode": CALIBRATION_MODE_NONE,
        "files": {
            "signal_frame_csv": str(sig_csv),
            "signal_frame_xlsx": str(sig_xlsx),
            "execution_trace_csv": str(trace_csv),
            "execution_trace_xlsx": str(trace_xlsx),
            "strategy_summary_csv": str(strategy_summary_csv),
            "strategy_summary_xlsx": str(strategy_summary_xlsx),
        },
    }
    summary["trading_fields_contract"] = build_runtime_trading_fields(
        symbol=oos.get("symbol"),
        timeframe=oos.get("timeframe"),
        signal_mode=risk.get("signal_mode"),
        execution_mode=execution_mode,
        order_type=order_type,
        stop_loss_pct=risk.get("stop_loss_pct"),
        take_profit_pct=risk.get("take_profit_pct"),
        min_expected_move_pct=min_expected_move_pct,
        min_tp_reach_prob=backtest.get("min_tp_reach_prob"),
        trades=backtest.get("trades", len(trace)),
        net_return_pct=backtest.get("net_return_pct"),
        goal_pass=oos.get("goal_pass"),
    )
    (out_dir / "execution_trace_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
