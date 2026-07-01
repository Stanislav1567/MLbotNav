from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd

from mlbotnav.backtest import run_prob_backtest
from mlbotnav.dataset import FEATURE_COLUMNS, RUNTIME_ACTION_COLUMNS, build_feature_frame, load_ohlcv_range
from mlbotnav.ml_trade_dataset_enrichment import (
    add_duration_label_columns,
    add_hit_label_columns,
    add_mae_mfe_columns,
    add_passport_context_columns,
    add_run_context_columns,
    add_trade_identity_columns,
)
from mlbotnav.pct_units import normalize_min_expected_move_pct
from mlbotnav.runtime_diagnostics import classify_backtest_outcome, is_min_move_unreachable
from mlbotnav.runtime_trading_fields import build_runtime_trading_fields


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _coerce_calibration_params(data: object) -> dict[str, float]:
    if not isinstance(data, dict):
        return {}
    out: dict[str, float] = {}
    for key, value in data.items():
        if value is None:
            continue
        out[str(key)] = float(value)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Out-of-sample evaluation on one day or date range using trained pipeline report.")
    parser.add_argument("--train-pipeline-report", required=True)
    parser.add_argument("--test-day", required=True, help="UTC day YYYY-MM-DD")
    parser.add_argument("--test-end-day", default=None, help="Optional end day YYYY-MM-DD for multi-day OOS")
    parser.add_argument("--layer", default="raw", help="Data layer for OOS day: raw/core")
    parser.add_argument("--goal-net-return-pct", type=float, default=100.0)
    parser.add_argument("--leverage", type=float, default=None, help="Override leverage; default uses train report risk_policy.leverage")
    parser.add_argument("--signal-mode", default=None, choices=["both", "long_only", "short_only"], help="Override signal mode; default uses train report risk_policy.signal_mode")
    parser.add_argument("--execution-mode", default=None, choices=["research", "exchange_like"], help="Override execution mode; default uses train report risk_policy.execution_mode")
    parser.add_argument("--order-type", default=None, choices=["market", "limit"], help="Override order type; default uses train report risk_policy.order_type")
    parser.add_argument("--limit-offset-bps", type=float, default=None, help="Override limit offset bps; default uses train report risk_policy.limit_offset_bps")
    parser.add_argument("--disable-timeout-exit", action="store_true", help="Disable time-based trade exit; default uses train report risk_policy.timeout_exit_enabled.")
    parser.add_argument("--fee-bps", type=float, default=None, help="Override fee bps; default uses train report strategy.fee_bps")
    parser.add_argument("--slippage-bps", type=float, default=None, help="Override slippage bps; default uses train report strategy.slippage_bps")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    train_report_path = Path(args.train_pipeline_report)
    rep = _load_json(train_report_path)
    symbol = str(rep.get("symbol", "SOLUSDT"))
    timeframe = str(rep.get("timeframe", "1m"))
    strategy = rep.get("strategy", {}) if isinstance(rep, dict) else {}
    risk = rep.get("risk_policy", {}) if isinstance(rep, dict) else {}
    strategy_eff = dict(strategy)
    if args.fee_bps is not None:
        strategy_eff["fee_bps"] = float(args.fee_bps)
    if args.slippage_bps is not None:
        strategy_eff["slippage_bps"] = float(args.slippage_bps)
    min_expected_move_pct = normalize_min_expected_move_pct(risk.get("min_expected_move_pct", 0.0))
    model_path = Path((rep.get("artifacts") or {}).get("model_path", ""))
    if not model_path.exists():
        raise FileNotFoundError(f"Model path not found: {model_path}")

    payload = joblib.load(model_path)
    model = payload["model"]
    features = payload["features"]
    calibration_params = _coerce_calibration_params(rep.get("calibration_params"))
    if not calibration_params:
        calibration_params = _coerce_calibration_params(risk.get("calibration_params"))
    if not calibration_params:
        calibration_params = _coerce_calibration_params(payload.get("calibration_params"))

    horizon = int(strategy.get("horizon_bars", 1))
    test_end = str(args.test_end_day) if args.test_end_day else str(args.test_day)
    raw = load_ohlcv_range(
        project_root,
        symbol=symbol,
        timeframe=timeframe,
        start_date=args.test_day,
        end_date=test_end,
        layer=args.layer,
    )
    feat = build_feature_frame(
        raw,
        horizon_bars=horizon,
        include_targets=True,
        calibration_params=calibration_params,
    )
    base_cols = [
        "open_time_utc",
        "close_time_utc",
        "open",
        "high",
        "low",
        "close",
        "future_return",
        "target_up",
        "atr14",
        "ema_gap",
    ]
    optional_cols = list(FEATURE_COLUMNS) + list(RUNTIME_ACTION_COLUMNS) + ["ema20", "ema50", "ema200"]
    ordered_cols = list(dict.fromkeys(base_cols + optional_cols))
    score = feat[[c for c in ordered_cols if c in feat.columns]].copy()
    score["prob_up"] = model.predict_proba(feat[features])[:, 1]
    score["pred_up"] = (score["prob_up"] >= 0.5).astype(int)

    bt_df, bt_summary = run_prob_backtest(
        score,
        p_enter_long=float(strategy_eff.get("p_enter_long", 0.55)),
        p_enter_short=float(strategy_eff.get("p_enter_short", 0.45)),
        fee_bps=float(strategy_eff.get("fee_bps", 10.0)),
        slippage_bps=float(strategy_eff.get("slippage_bps", 5.0)),
        stop_loss_pct=float(risk.get("stop_loss_pct", 0.01)),
        take_profit_pct=float(risk.get("take_profit_pct", 0.02)),
        min_expected_move_pct=min_expected_move_pct,
        tp_min_factor=float(risk.get("tp_min_factor", 0.7)),
        dynamic_tp_enabled=bool(risk.get("dynamic_tp_enabled", True)),
        cooldown_bars=int(risk.get("cooldown_bars", 0)),
        trend_filter=str(risk.get("trend_filter", "none")),
        min_abs_ema_gap=float(risk.get("min_abs_ema_gap", 0.0)),
        notional_usd=float(risk.get("notional_usd", 10.0)),
        leverage=float(args.leverage) if args.leverage is not None else float(risk.get("leverage", 1.0)),
        signal_mode=str(args.signal_mode) if args.signal_mode else str(risk.get("signal_mode", "both")),
        execution_mode=str(args.execution_mode) if args.execution_mode else str(risk.get("execution_mode", "research")),
        order_type=str(args.order_type) if args.order_type else str(risk.get("order_type", "market")),
        hold_bars=int(strategy.get("horizon_bars", 1)),
        limit_offset_bps=float(args.limit_offset_bps) if args.limit_offset_bps is not None else float(risk.get("limit_offset_bps", 2.0)),
        require_trend_filter_features=True,
        calibration_params=calibration_params,
        timeout_exit_enabled=(False if bool(args.disable_timeout_exit) else bool(risk.get("timeout_exit_enabled", True))),
    )

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = project_root / "reports" / "final_review"
    out_dir.mkdir(parents=True, exist_ok=True)
    day_tag = str(args.test_day) if test_end == str(args.test_day) else f"{args.test_day}_to_{test_end}"
    mode_tag = str(args.signal_mode) if args.signal_mode else str(risk.get("signal_mode", "both"))
    run_id = f"oos_{symbol}_{timeframe}_{day_tag}_{mode_tag}_{ts}"
    backtest_path = out_dir / f"oos_backtest_trades_{symbol}_{timeframe}_{day_tag}_{mode_tag}_{ts}.csv"
    report_path = out_dir / f"oos_report_{symbol}_{timeframe}_{day_tag}_{mode_tag}_{ts}.json"
    pipeline_like_path = out_dir / f"oos_pipeline_like_{symbol}_{timeframe}_{day_tag}_{mode_tag}_{ts}.json"
    date_range = rep.get("date_range") if isinstance(rep.get("date_range"), dict) else {}
    bt_df = add_run_context_columns(
        bt_df,
        run_id=run_id,
        symbol=symbol,
        timeframe=timeframe,
        data_layer=str(args.layer),
        train_start=str(date_range.get("start", "")),
        train_end=str(date_range.get("end", "")),
        test_start=str(args.test_day),
        test_end=str(test_end),
    )
    bt_diag = bt_summary.get("trend_filter_diagnostics")
    bt_diag = bt_diag if isinstance(bt_diag, dict) else {}
    bt_df = add_passport_context_columns(
        bt_df,
        project_root=project_root,
        calibration_params=calibration_params,
        entry_action_gate_columns=bt_diag.get("entry_action_gate_columns"),
    )
    bt_df = add_trade_identity_columns(bt_df)
    bt_df = add_duration_label_columns(bt_df)
    bt_df = add_hit_label_columns(bt_df)
    bt_df = add_mae_mfe_columns(bt_df)
    bt_df.to_csv(backtest_path, index=False)

    goal = float(args.goal_net_return_pct)
    risk_eff = dict(risk)
    risk_eff["signal_mode"] = str(args.signal_mode) if args.signal_mode else str(risk.get("signal_mode", "both"))
    risk_eff["execution_mode"] = str(args.execution_mode) if args.execution_mode else str(risk.get("execution_mode", "research"))
    risk_eff["order_type"] = str(args.order_type) if args.order_type else str(risk.get("order_type", "market"))
    risk_eff["limit_offset_bps"] = float(args.limit_offset_bps) if args.limit_offset_bps is not None else float(risk.get("limit_offset_bps", 2.0))
    risk_eff["timeout_exit_enabled"] = False if bool(args.disable_timeout_exit) else bool(risk.get("timeout_exit_enabled", True))
    risk_eff["min_expected_move_pct"] = min_expected_move_pct
    if args.leverage is not None:
        risk_eff["leverage"] = float(args.leverage)
        risk_eff["effective_notional_usd"] = float(risk_eff.get("notional_usd", 10.0)) * float(args.leverage)
    risk_eff["calibration_params"] = calibration_params
    runtime_diagnostic_status = classify_backtest_outcome(bt_summary)
    risk_eff["runtime_diagnostic_status"] = str(runtime_diagnostic_status)

    oos = {
        "run_id": run_id,
        "run_utc": ts,
        "train_pipeline_report": str(train_report_path.resolve()),
        "test_day": args.test_day,
        "test_end_day": test_end,
        "symbol": symbol,
        "timeframe": timeframe,
        "data_layer": str(args.layer),
        "date_range": {
            "start": str(date_range.get("start", "")),
            "end": str(date_range.get("end", "")),
        },
        "train_start": str(date_range.get("start", "")),
        "train_end": str(date_range.get("end", "")),
        "test_start": str(args.test_day),
        "test_end": str(test_end),
        "model_path": str(model_path),
        "calibration_params": calibration_params,
        "strategy": strategy_eff,
        "risk_policy": risk_eff,
        "backtest": bt_summary,
        "runtime_diagnostic_status": str(runtime_diagnostic_status),
        "runtime_diagnostics": {
            "status": str(runtime_diagnostic_status),
            "min_move_unreachable": bool(is_min_move_unreachable(bt_summary)),
        },
        "goal_net_return_pct_day": goal,
        "goal_pass": float(bt_summary.get("net_return_pct", 0.0)) >= goal,
        "artifacts": {"backtest_path": str(backtest_path), "pipeline_like_path": str(pipeline_like_path)},
    }
    oos["trading_fields_contract"] = build_runtime_trading_fields(
        symbol=symbol,
        timeframe=timeframe,
        signal_mode=risk_eff.get("signal_mode"),
        execution_mode=risk_eff.get("execution_mode"),
        order_type=risk_eff.get("order_type"),
        stop_loss_pct=risk_eff.get("stop_loss_pct"),
        take_profit_pct=risk_eff.get("take_profit_pct"),
        min_expected_move_pct=risk_eff.get("min_expected_move_pct"),
        min_tp_reach_prob=bt_summary.get("min_tp_reach_prob"),
        trades=bt_summary.get("trades"),
        net_return_pct=bt_summary.get("net_return_pct"),
        goal_pass=float(bt_summary.get("net_return_pct", 0.0)) >= goal,
    )
    report_path.write_text(json.dumps(oos, ensure_ascii=False, indent=2), encoding="utf-8")
    pipeline_like = {
        "symbol": symbol,
        "timeframe": timeframe,
        "data_layer": str(args.layer),
        "date_range": {
            "start": str(date_range.get("start", "")),
            "end": str(date_range.get("end", "")),
        },
        "strategy": strategy_eff,
        "risk_policy": risk_eff,
        "artifacts": {"backtest_path": str(backtest_path)},
    }
    pipeline_like_path.write_text(json.dumps(pipeline_like, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "oos_report": str(report_path),
                "pipeline_like": str(pipeline_like_path),
                "backtest_path": str(backtest_path),
                "net_return_pct": bt_summary.get("net_return_pct"),
                "trades": bt_summary.get("trades"),
                "goal_pass": oos["goal_pass"],
                "signal_mode": mode_tag,
                "test_end_day": test_end,
                "fee_bps": strategy_eff.get("fee_bps"),
                "slippage_bps": strategy_eff.get("slippage_bps"),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
