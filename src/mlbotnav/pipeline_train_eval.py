from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
import yaml

from mlbotnav.audit import audit_event
from mlbotnav.backtest import run_prob_backtest
from mlbotnav.dataset import FEATURE_COLUMNS, FEATURE_GROUPS, build_feature_frame, load_ohlcv_range
from mlbotnav.model_registry import promote_if_pass, register_candidate
from mlbotnav.ml_trade_dataset_enrichment import (
    add_duration_label_columns,
    add_hit_label_columns,
    add_mae_mfe_columns,
    add_passport_context_columns,
    add_run_context_columns,
    add_trade_identity_columns,
)
from mlbotnav.pct_units import normalize_min_expected_move_pct
from mlbotnav.readiness import enforce_action_allowed
from mlbotnav.security import require_role
from mlbotnav.validation import aggregate_fold_metrics, create_model, leakage_sanity_checks, walk_forward_validate
from mlbotnav.workflow_gate import enforce_training_scope


def _parse_calibration_params_json(raw: str | None) -> dict[str, float]:
    text = str(raw or "").strip()
    if not text:
        return {}
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("--calibration-params-json must be a JSON object")
    out: dict[str, float] = {}
    for key, value in data.items():
        if value is None:
            continue
        out[str(key)] = float(value)
    return out


def _load_thresholds(project_root: Path) -> dict:
    p = project_root / "configs" / "thresholds.yaml"
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _apply_gate_signal_mode_overrides(thresholds: dict, signal_mode: str) -> dict:
    if not isinstance(thresholds, dict):
        return {}
    mode_key = str(signal_mode or "").strip().lower()
    if mode_key not in {"both", "long_only", "short_only"}:
        return thresholds

    override_map = (
        thresholds.get("gates_signal_mode_overrides")
        or thresholds.get("gate_signal_mode_overrides")
        or {}
    )
    if not isinstance(override_map, dict):
        return thresholds
    mode_override = override_map.get(mode_key)
    if not isinstance(mode_override, dict):
        return thresholds

    merged = dict(thresholds)
    merged_gates = dict((thresholds.get("gates") or {}))
    for key, value in mode_override.items():
        merged_gates[str(key)] = value
    merged["gates"] = merged_gates
    return merged


def _gate_decision(metrics: dict, backtest: dict, thresholds: dict) -> tuple[bool, list[str]]:
    g = thresholds.get("gates", {})
    min_auc = float(g.get("min_auc", 0.52))
    min_f1 = float(g.get("min_f1", 0.05))
    max_mdd = float(g.get("max_drawdown_pct_abs", 20.0))
    min_trades = int(g.get("min_trades", 20))
    max_no_trade_ratio = float(g.get("max_no_trade_ratio", 0.8))
    max_no_trade_ratio_days = float(g.get("max_no_trade_ratio_days", max_no_trade_ratio))
    trades_per_day_min_req = float(g.get("trades_per_day_min", 0))
    trades_per_day_max_req = float(g.get("trades_per_day_max", 10_000))
    min_sortino = float(g.get("min_sortino", -999.0))
    min_cagr = float(g.get("min_cagr", -1.0))
    min_net_return_pct = float(g.get("min_net_return_pct", -1e9))

    reasons: list[str] = []
    if metrics.get("auc_mean", 0.0) < min_auc:
        reasons.append(f"auc_below_threshold:{metrics.get('auc_mean', 0.0):.4f}<{min_auc:.4f}")
    if metrics.get("f1_mean", 0.0) < min_f1:
        reasons.append(f"f1_below_threshold:{metrics.get('f1_mean', 0.0):.4f}<{min_f1:.4f}")
    if abs(backtest.get("max_drawdown_pct", 0.0)) > max_mdd:
        reasons.append(
            f"max_drawdown_exceeded:{abs(backtest.get('max_drawdown_pct', 0.0)):.3f}>{max_mdd:.3f}"
        )
    if backtest.get("trades", 0) < min_trades:
        reasons.append(f"trades_below_min:{backtest.get('trades', 0)}<{min_trades}")
    if backtest.get("no_trade_ratio_days", backtest.get("no_trade_ratio", 1.0)) > max_no_trade_ratio_days:
        reasons.append(
            f"no_trade_ratio_days_high:{backtest.get('no_trade_ratio_days', backtest.get('no_trade_ratio', 1.0)):.3f}>{max_no_trade_ratio_days:.3f}"
        )
    if backtest.get("trades_per_day_avg", 0.0) < trades_per_day_min_req:
        reasons.append(
            f"trades_per_day_avg_low:{backtest.get('trades_per_day_avg', 0.0):.3f}<{trades_per_day_min_req}"
        )
    if backtest.get("trades_per_day_avg", 0.0) > trades_per_day_max_req:
        reasons.append(
            f"trades_per_day_avg_high:{backtest.get('trades_per_day_avg', 0.0):.3f}>{trades_per_day_max_req}"
        )
    if float(backtest.get("sortino", 0.0)) < min_sortino:
        reasons.append(f"sortino_below_threshold:{float(backtest.get('sortino', 0.0)):.4f}<{min_sortino:.4f}")
    if float(backtest.get("cagr", 0.0)) < min_cagr:
        reasons.append(f"cagr_below_threshold:{float(backtest.get('cagr', 0.0)):.6f}<{min_cagr:.6f}")
    if float(backtest.get("net_return_pct", 0.0)) < min_net_return_pct:
        reasons.append(f"net_return_pct_below_threshold:{float(backtest.get('net_return_pct', 0.0)):.4f}<{min_net_return_pct:.4f}")
    return len(reasons) == 0, reasons


def _candidate_score(metrics: dict, backtest: dict) -> float:
    return float(
        backtest.get("net_return_pct", 0.0)
        - abs(backtest.get("max_drawdown_pct", 0.0)) * 0.5
        + metrics.get("auc_mean", 0.0) * 10.0
        + metrics.get("f1_mean", 0.0) * 5.0
    )


def _evaluate_candidate(
    *,
    frame: pd.DataFrame,
    feature_columns: list[str],
    model_type: str,
    thresholds: dict,
    min_train_rows: int,
    n_folds: int,
    p_enter_long: float,
    p_enter_short: float,
    fee_bps: float,
    slippage_bps: float,
    stop_loss_pct: float,
    take_profit_pct: float,
    min_expected_move_pct: float,
    tp_min_factor: float,
    dynamic_tp_enabled: bool,
    cooldown_bars: int,
    trend_filter: str,
    min_abs_ema_gap: float,
    notional_usd: float,
    leverage: float,
    signal_mode: str,
    execution_mode: str,
    order_type: str,
    limit_offset_bps: float,
    hold_bars: int,
    calibration_params: dict[str, float] | None = None,
    timeout_exit_enabled: bool = True,
) -> dict:
    folds, oof = walk_forward_validate(
        frame,
        min_train_rows=min_train_rows,
        n_folds=n_folds,
        feature_columns=feature_columns,
        model_type=model_type,
    )
    fold_metrics = aggregate_fold_metrics(folds)
    bt_df, bt_summary = run_prob_backtest(
        oof,
        p_enter_long=p_enter_long,
        p_enter_short=p_enter_short,
        fee_bps=fee_bps,
        slippage_bps=slippage_bps,
        stop_loss_pct=stop_loss_pct,
        take_profit_pct=take_profit_pct,
        min_expected_move_pct=min_expected_move_pct,
        tp_min_factor=tp_min_factor,
        dynamic_tp_enabled=dynamic_tp_enabled,
        cooldown_bars=cooldown_bars,
        trend_filter=trend_filter,
        min_abs_ema_gap=min_abs_ema_gap,
        notional_usd=notional_usd,
        leverage=leverage,
        signal_mode=signal_mode,
        execution_mode=execution_mode,
        order_type=order_type,
        hold_bars=hold_bars,
        limit_offset_bps=limit_offset_bps,
        require_trend_filter_features=True,
        calibration_params=calibration_params,
        timeout_exit_enabled=bool(timeout_exit_enabled),
    )
    gate_pass, gate_reasons = _gate_decision(fold_metrics, bt_summary, thresholds)
    return {
        "model_type": model_type,
        "feature_columns": feature_columns,
        "feature_count": len(feature_columns),
        "walk_forward": fold_metrics,
        "backtest": bt_summary,
        "gate_pass": gate_pass,
        "gate_reasons": gate_reasons,
        "score": _candidate_score(fold_metrics, bt_summary),
        "oof": oof,
        "backtest_df": bt_df,
    }


def _run_ablation(
    *,
    frame: pd.DataFrame,
    selected_model: str,
    thresholds: dict,
    min_train_rows: int,
    n_folds: int,
    p_enter_long: float,
    p_enter_short: float,
    fee_bps: float,
    slippage_bps: float,
    stop_loss_pct: float,
    take_profit_pct: float,
    min_expected_move_pct: float,
    tp_min_factor: float,
    dynamic_tp_enabled: bool,
    cooldown_bars: int,
    trend_filter: str,
    min_abs_ema_gap: float,
    notional_usd: float,
    leverage: float,
    signal_mode: str,
    execution_mode: str,
    order_type: str,
    limit_offset_bps: float,
    hold_bars: int,
    baseline_score: float,
    baseline_metrics: dict,
    baseline_backtest: dict,
    calibration_params: dict[str, float] | None = None,
    timeout_exit_enabled: bool = True,
) -> tuple[list[dict], pd.DataFrame]:
    rows: list[dict] = []
    for group_name, group_cols in FEATURE_GROUPS.items():
        reduced = [c for c in FEATURE_COLUMNS if c not in set(group_cols)]
        if len(reduced) < 5:
            continue
        try:
            res = _evaluate_candidate(
                frame=frame,
                feature_columns=reduced,
                model_type=selected_model,
                thresholds=thresholds,
                min_train_rows=min_train_rows,
                n_folds=n_folds,
                p_enter_long=p_enter_long,
                p_enter_short=p_enter_short,
                fee_bps=fee_bps,
                slippage_bps=slippage_bps,
                stop_loss_pct=stop_loss_pct,
                take_profit_pct=take_profit_pct,
                min_expected_move_pct=min_expected_move_pct,
                tp_min_factor=tp_min_factor,
                dynamic_tp_enabled=dynamic_tp_enabled,
                cooldown_bars=cooldown_bars,
                trend_filter=trend_filter,
                min_abs_ema_gap=min_abs_ema_gap,
                notional_usd=notional_usd,
                leverage=leverage,
                signal_mode=signal_mode,
                execution_mode=execution_mode,
                order_type=order_type,
                hold_bars=hold_bars,
                limit_offset_bps=limit_offset_bps,
                calibration_params=calibration_params,
                timeout_exit_enabled=bool(timeout_exit_enabled),
            )
            row = {
                "group_removed": group_name,
                "features_removed": len(group_cols),
                "score": res["score"],
                "score_delta_vs_full": res["score"] - baseline_score,
                "auc_mean": res["walk_forward"].get("auc_mean", 0.0),
                "auc_delta_vs_full": res["walk_forward"].get("auc_mean", 0.0) - baseline_metrics.get("auc_mean", 0.0),
                "f1_mean": res["walk_forward"].get("f1_mean", 0.0),
                "f1_delta_vs_full": res["walk_forward"].get("f1_mean", 0.0) - baseline_metrics.get("f1_mean", 0.0),
                "net_return_pct": res["backtest"].get("net_return_pct", 0.0),
                "net_return_delta_vs_full": res["backtest"].get("net_return_pct", 0.0) - baseline_backtest.get("net_return_pct", 0.0),
                "max_drawdown_pct_abs": abs(res["backtest"].get("max_drawdown_pct", 0.0)),
                "gate_pass": bool(res["gate_pass"]),
                "gate_reasons": ";".join(res["gate_reasons"]),
                "status": "ok",
            }
        except Exception as e:
            row = {
                "group_removed": group_name,
                "features_removed": len(group_cols),
                "status": "failed",
                "error": str(e),
            }
        rows.append(row)
    df = pd.DataFrame(rows)
    summary_rows = pd.DataFrame()
    if not df.empty and "status" in df.columns:
        summary_rows = df[df["status"] == "ok"].copy()
    summary: list[dict] = []
    if not summary_rows.empty:
        summary_rows = summary_rows.sort_values("score_delta_vs_full")
        for _, r in summary_rows.head(3).iterrows():
            summary.append(
                {
                    "group_removed": r["group_removed"],
                    "score_delta_vs_full": float(r["score_delta_vs_full"]),
                    "auc_delta_vs_full": float(r["auc_delta_vs_full"]),
                    "f1_delta_vs_full": float(r["f1_delta_vs_full"]),
                    "net_return_delta_vs_full": float(r["net_return_delta_vs_full"]),
                }
            )
    return summary, df


def main() -> int:
    parser = argparse.ArgumentParser(description="Unified ML pipeline: features -> walk-forward -> backtest -> gate")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--start-date", default=None, help="YYYY-MM-DD")
    parser.add_argument("--end-date", default=None, help="YYYY-MM-DD")
    parser.add_argument("--layer", default="raw", help="Data layer for pipeline input: raw/core")
    parser.add_argument("--horizon-bars", type=int, default=1)
    parser.add_argument("--min-train-rows", type=int, default=1200)
    parser.add_argument("--n-folds", type=int, default=4)
    parser.add_argument("--fee-bps", type=float, default=10.0)
    parser.add_argument("--slippage-bps", type=float, default=5.0)
    parser.add_argument("--p-enter-long", type=float, default=0.55)
    parser.add_argument("--p-enter-short", type=float, default=0.45)
    parser.add_argument("--stop-loss-pct", type=float, default=0.01)
    parser.add_argument("--take-profit-pct", type=float, default=0.02)
    parser.add_argument("--min-expected-move-pct", type=float, default=0.0)
    parser.add_argument("--tp-min-factor", type=float, default=0.7, help="Dynamic TP floor factor: tp_min_pct = factor * min_expected_move_pct")
    parser.add_argument("--disable-dynamic-tp", action="store_true")
    parser.add_argument("--cooldown-bars", type=int, default=0)
    parser.add_argument(
        "--trend-filter",
        default="none",
        choices=[
            "none",
            "ema_gap_sign",
            "ema_cross_20_50",
            "ema_cross_20_200",
            "ema_stack_bull",
            "channel_breakout_50",
            "adx_trend_18",
            "fib_retrace_0382_0618_trend_resume",
            "fib_extension_targets",
            "swing_hl_hh_long",
            "swing_lh_ll_short",
            "bos_continuation_confirm",
            "min_max_range_revert",
            "max_low_pullback_long",
            "hvn_lvn_density_reaction",
            "volume_profile_poc_vah_val_retest",
            "value_area_rotation_vs_breakout",
            "wedge_breakout_plus_profile_acceptance",
            "orderbook_imbalance_l1_l50",
            "spread_pressure_and_delta_absorption",
        ],
    )
    parser.add_argument("--min-abs-ema-gap", type=float, default=0.0)
    parser.add_argument("--notional-usd", type=float, default=10.0)
    parser.add_argument("--leverage", type=float, default=1.0)
    parser.add_argument("--signal-mode", default="both", choices=["both", "long_only", "short_only"])
    parser.add_argument("--execution-mode", default="research", choices=["research", "exchange_like"])
    parser.add_argument("--order-type", default="market", choices=["market", "limit"])
    parser.add_argument("--limit-offset-bps", type=float, default=2.0)
    parser.add_argument("--position-size", type=float, default=None, help="Deprecated alias for --notional-usd")
    parser.add_argument("--model-family", default="auto", help="auto|logreg|lightgbm|xgboost")
    parser.add_argument("--disable-ablation", action="store_true")
    parser.add_argument("--disable-timeout-exit", action="store_true", help="Disable time-based trade exit; positions close only by TP/SL or end of data.")
    parser.add_argument("--promote-if-pass", action="store_true")
    parser.add_argument(
        "--calibration-params-json",
        default="{}",
        help="JSON object with Optuna calibration params to apply to feature formulas and final backtest.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    enforce_action_allowed(project_root, action="pipeline_train_eval")
    role = require_role(project_root, action="train_eval")
    if not role["allowed"]:
        raise PermissionError(f"RBAC denied for action=train_eval: {role['reason']}")
    enforce_training_scope(
        project_root=project_root,
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=args.start_date,
        end_date=args.end_date,
        action_name="pipeline_train_eval",
    )
    thresholds = _apply_gate_signal_mode_overrides(_load_thresholds(project_root), str(args.signal_mode))
    notional_usd = float(args.position_size) if args.position_size is not None else float(args.notional_usd)
    min_expected_move_pct = normalize_min_expected_move_pct(args.min_expected_move_pct)
    calibration_params = _parse_calibration_params_json(args.calibration_params_json)

    raw = load_ohlcv_range(
        project_root,
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=args.start_date,
        end_date=args.end_date,
        layer=str(args.layer),
    )
    frame = build_feature_frame(raw, horizon_bars=args.horizon_bars, calibration_params=calibration_params)

    leakage_issues = leakage_sanity_checks(frame)
    if leakage_issues:
        raise RuntimeError(f"Leakage/time integrity checks failed: {leakage_issues}")

    mf = (args.model_family or "auto").strip().lower()
    if mf == "auto":
        model_candidates = ["logreg", "lightgbm", "xgboost"]
    elif mf in {"logreg", "lightgbm", "xgboost"}:
        model_candidates = [mf]
    else:
        raise ValueError(f"Unsupported --model-family={args.model_family}")

    eval_results: list[dict] = []
    skipped: list[dict] = []
    for m in model_candidates:
        try:
            res = _evaluate_candidate(
                frame=frame,
                feature_columns=FEATURE_COLUMNS,
                model_type=m,
                thresholds=thresholds,
                min_train_rows=args.min_train_rows,
                n_folds=args.n_folds,
                p_enter_long=args.p_enter_long,
                p_enter_short=args.p_enter_short,
                fee_bps=args.fee_bps,
                slippage_bps=args.slippage_bps,
                stop_loss_pct=args.stop_loss_pct,
                take_profit_pct=args.take_profit_pct,
                min_expected_move_pct=min_expected_move_pct,
                tp_min_factor=args.tp_min_factor,
                dynamic_tp_enabled=(not args.disable_dynamic_tp),
                cooldown_bars=int(args.cooldown_bars),
                trend_filter=str(args.trend_filter),
                min_abs_ema_gap=float(args.min_abs_ema_gap),
                notional_usd=notional_usd,
                leverage=float(args.leverage),
                signal_mode=str(args.signal_mode),
                execution_mode=str(args.execution_mode),
                order_type=str(args.order_type),
                limit_offset_bps=float(args.limit_offset_bps),
                hold_bars=int(args.horizon_bars),
                calibration_params=calibration_params,
                timeout_exit_enabled=not bool(args.disable_timeout_exit),
            )
            eval_results.append(res)
        except Exception as e:
            skipped.append({"model_type": m, "reason": str(e)})

    if not eval_results:
        raise RuntimeError(f"No model candidates were successfully evaluated. skipped={skipped}")

    eval_results = sorted(
        eval_results,
        key=lambda r: (1 if r["gate_pass"] else 0, r["score"]),
        reverse=True,
    )
    best = eval_results[0]
    selected_model_type = best["model_type"]
    selected_features = best["feature_columns"]
    fold_metrics = best["walk_forward"]
    bt_summary = best["backtest"]
    bt_df = best["backtest_df"]
    oof = best["oof"]
    gate_pass = bool(best["gate_pass"])
    gate_reasons = list(best["gate_reasons"])

    x = frame[selected_features]
    y = frame["target_up"]
    final_model = create_model(selected_model_type)
    final_model.fit(x, y)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    model_dir = project_root / "models" / "pipeline"
    report_dir = project_root / "reports" / "pipeline"
    model_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / f"champion_candidate_{selected_model_type}_{args.symbol}_{args.timeframe}_{ts}.joblib"
    oof_path = report_dir / f"oof_{args.symbol}_{args.timeframe}_{ts}.csv"
    bt_path = report_dir / f"backtest_trades_{args.symbol}_{args.timeframe}_{ts}.csv"
    ablation_path = report_dir / f"ablation_{args.symbol}_{args.timeframe}_{ts}.csv"
    report_path = report_dir / f"pipeline_report_{args.symbol}_{args.timeframe}_{ts}.json"
    run_id = f"pipeline_{args.symbol}_{args.timeframe}_{ts}"

    ablation_summary = []
    ablation_rows_df = pd.DataFrame()
    if not args.disable_ablation:
        ablation_summary, ablation_rows_df = _run_ablation(
            frame=frame,
            selected_model=selected_model_type,
            thresholds=thresholds,
            min_train_rows=args.min_train_rows,
            n_folds=args.n_folds,
            p_enter_long=args.p_enter_long,
            p_enter_short=args.p_enter_short,
            fee_bps=args.fee_bps,
            slippage_bps=args.slippage_bps,
            stop_loss_pct=args.stop_loss_pct,
            take_profit_pct=args.take_profit_pct,
            min_expected_move_pct=min_expected_move_pct,
            tp_min_factor=args.tp_min_factor,
            dynamic_tp_enabled=(not args.disable_dynamic_tp),
            cooldown_bars=int(args.cooldown_bars),
            trend_filter=str(args.trend_filter),
            min_abs_ema_gap=float(args.min_abs_ema_gap),
            notional_usd=notional_usd,
            leverage=float(args.leverage),
            signal_mode=str(args.signal_mode),
            execution_mode=str(args.execution_mode),
            order_type=str(args.order_type),
            limit_offset_bps=float(args.limit_offset_bps),
            hold_bars=int(args.horizon_bars),
            baseline_score=float(best["score"]),
            baseline_metrics=fold_metrics,
            baseline_backtest=bt_summary,
            calibration_params=calibration_params,
            timeout_exit_enabled=not bool(args.disable_timeout_exit),
        )
        if not ablation_rows_df.empty:
            ablation_rows_df.to_csv(ablation_path, index=False)

    joblib.dump(
        {
            "model": final_model,
            "features": selected_features,
            "horizon_bars": args.horizon_bars,
            "model_type": selected_model_type,
            "calibration_params": calibration_params,
        },
        model_path,
    )
    oof.to_csv(oof_path, index=False)
    bt_df = add_run_context_columns(
        bt_df,
        run_id=run_id,
        symbol=str(args.symbol),
        timeframe=str(args.timeframe),
        data_layer=str(args.layer),
        train_start=str(args.start_date or ""),
        train_end=str(args.end_date or ""),
        test_start=str(args.start_date or ""),
        test_end=str(args.end_date or ""),
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
    bt_df.to_csv(bt_path, index=False)

    report = {
        "run_id": run_id,
        "run_utc": ts,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "data_layer": str(args.layer),
        "date_range": {"start": args.start_date, "end": args.end_date},
        "rows_raw": int(len(raw)),
        "rows_featured": int(len(frame)),
        "horizon_bars": args.horizon_bars,
        "calibration_params": calibration_params,
        "leakage_issues": leakage_issues,
        "walk_forward": fold_metrics,
        "backtest": bt_summary,
        "selected_model": selected_model_type,
        "model_selection": {
            "requested_model_family": mf,
            "selected_model": selected_model_type,
            "selected_score": float(best["score"]),
            "candidates": [
                {
                    "model_type": r["model_type"],
                    "score": float(r["score"]),
                    "gate_pass": bool(r["gate_pass"]),
                    "gate_reasons": r["gate_reasons"],
                    "walk_forward": r["walk_forward"],
                    "backtest": r["backtest"],
                }
                for r in eval_results
            ],
            "skipped": skipped,
        },
        "ablation": {
            "enabled": not args.disable_ablation,
            "summary": ablation_summary,
            "groups_total": len(FEATURE_GROUPS),
        },
        "risk_policy": {
            "stop_loss_pct": args.stop_loss_pct,
            "take_profit_pct": args.take_profit_pct,
            "min_expected_move_pct": min_expected_move_pct,
            "tp_min_factor": args.tp_min_factor,
            "dynamic_tp_enabled": bool(not args.disable_dynamic_tp),
            "timeout_exit_enabled": bool(not args.disable_timeout_exit),
            "cooldown_bars": int(args.cooldown_bars),
            "trend_filter": str(args.trend_filter),
            "min_abs_ema_gap": float(args.min_abs_ema_gap),
            "notional_usd": notional_usd,
            "leverage": float(args.leverage),
            "effective_notional_usd": float(notional_usd) * float(args.leverage),
            "signal_mode": str(args.signal_mode),
            "execution_mode": str(args.execution_mode),
            "order_type": str(args.order_type),
            "limit_offset_bps": float(args.limit_offset_bps),
        },
        "strategy": {
            "type": "probability_threshold_long_short",
            "horizon_bars": args.horizon_bars,
            "p_enter_long": args.p_enter_long,
            "p_enter_short": args.p_enter_short,
            "fee_bps": args.fee_bps,
            "slippage_bps": args.slippage_bps,
        },
        "gate": {"pass": gate_pass, "reasons": gate_reasons},
        "artifacts": {
            "model_path": str(model_path),
            "oof_path": str(oof_path),
            "backtest_path": str(bt_path),
            "ablation_path": str(ablation_path) if ablation_path.exists() else None,
        },
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report["_report_path"] = str(report_path)
    register_candidate(project_root, report=report)
    promoted = False
    champion_path = None
    promote_reason = "not_requested"
    if args.promote_if_pass:
        promoted, champion_path_obj, promote_reason = promote_if_pass(project_root, report=report)
        champion_path = str(champion_path_obj)

    audit_event(
        project_root,
        event="pipeline_train_eval_completed",
        payload={
            "symbol": args.symbol,
            "timeframe": args.timeframe,
            "report_path": str(report_path),
            "gate_pass": gate_pass,
            "promoted": promoted,
            "promote_reason": promote_reason,
            "rbac": role,
        },
    )
    print(
        json.dumps(
            {
                "report_path": str(report_path),
                "gate_pass": gate_pass,
                "reasons": gate_reasons,
                "promoted": promoted,
                "champion_path": champion_path,
                "promote_reason": promote_reason,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
