from __future__ import annotations

import argparse
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import yaml

from mlbotnav.backtest import run_prob_backtest
from mlbotnav.dataset import build_feature_frame, load_ohlcv_range
from mlbotnav.readiness import enforce_action_allowed
from mlbotnav.validation import aggregate_fold_metrics, leakage_sanity_checks, walk_forward_validate


def _load_thresholds(project_root: Path) -> dict:
    p = project_root / "configs" / "thresholds.yaml"
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _gate_decision(metrics: dict, backtest: dict, thresholds: dict) -> tuple[bool, list[str]]:
    g = thresholds.get("gates", {})
    min_auc = float(g.get("min_auc", 0.52))
    min_f1 = float(g.get("min_f1", 0.05))
    max_mdd = float(g.get("max_drawdown_pct_abs", 20.0))
    min_trades = int(g.get("min_trades", 20))
    max_no_trade_ratio = float(g.get("max_no_trade_ratio", 0.8))
    max_no_trade_ratio_days = float(g.get("max_no_trade_ratio_days", max_no_trade_ratio))
    trades_per_day_min_req = int(g.get("trades_per_day_min", 0))
    trades_per_day_max_req = int(g.get("trades_per_day_max", 10_000))
    min_sortino = float(g.get("min_sortino", -999.0))
    min_cagr = float(g.get("min_cagr", -1.0))
    min_net_return_pct = float(g.get("min_net_return_pct", -1e9))
    reasons = []
    if metrics.get("auc_mean", 0.0) < min_auc:
        reasons.append("auc")
    if metrics.get("f1_mean", 0.0) < min_f1:
        reasons.append("f1")
    if abs(backtest.get("max_drawdown_pct", 0.0)) > max_mdd:
        reasons.append("mdd")
    if backtest.get("trades", 0) < min_trades:
        reasons.append("trades")
    if backtest.get("no_trade_ratio_days", backtest.get("no_trade_ratio", 1.0)) > max_no_trade_ratio_days:
        reasons.append("no_trade")
    if backtest.get("trades_per_day_avg", 0.0) < trades_per_day_min_req:
        reasons.append("trades_per_day_low")
    if backtest.get("trades_per_day_avg", 0.0) > trades_per_day_max_req:
        reasons.append("trades_per_day_high")
    if float(backtest.get("sortino", 0.0)) < min_sortino:
        reasons.append("sortino")
    if float(backtest.get("cagr", 0.0)) < min_cagr:
        reasons.append("cagr")
    if float(backtest.get("net_return_pct", 0.0)) < min_net_return_pct:
        reasons.append("net_return_pct")
    return len(reasons) == 0, reasons


def _evaluate_horizon(
    *,
    raw_rows: list[dict],
    h: int,
    min_train_rows: int,
    n_folds: int,
    longs: list[float],
    shorts: list[float],
    min_move_grid: list[float],
    notional_usd_grid: list[float],
    fee_bps: float,
    slippage_bps: float,
    stop_loss_pct: float,
    take_profit_pct: float,
    min_tp_reach_prob: float,
    tp_min_factor: float,
    dynamic_tp_enabled: bool,
    cooldown_bars: int,
    trend_filter: str,
    min_abs_ema_gap: float,
    leverage: float,
    signal_mode: str,
    execution_mode: str,
    order_type: str,
    limit_offset_bps: float,
    thresholds: dict,
) -> tuple[int, list[dict], str | None, dict]:
    import pandas as pd

    raw = pd.DataFrame(raw_rows)
    proxy_stats: dict = {
        "horizon_bars": int(h),
        "execution_mode": str(execution_mode),
        "grid_min": float(min(min_move_grid)) if len(min_move_grid) else 0.0,
        "proxy_max": None,
    }
    frame = build_feature_frame(raw, horizon_bars=h)
    issues = leakage_sanity_checks(frame)
    if issues:
        return h, [], f"leakage_issues={issues}", proxy_stats
    folds, oof = walk_forward_validate(frame, min_train_rows=min_train_rows, n_folds=n_folds)
    fold_metrics = aggregate_fold_metrics(folds)
    if str(execution_mode).strip().lower() == "exchange_like":
        req_cols = ["open", "high", "low", "close", "open_time_utc"]
        missing = [c for c in req_cols if c not in oof.columns]
        if missing:
            return h, [], f"exchange_like_requires_columns_missing={missing}", proxy_stats
    # Fast sanity: in exchange_like mode entries are filtered by pred_move_proxy=confidence*atr14.
    # If grid min is above achievable proxy max, this horizon cannot produce any trades.
    if str(execution_mode).strip().lower() == "exchange_like":
        try:
            prob = pd.to_numeric(oof.get("prob_up"), errors="coerce")
            atr = pd.to_numeric(oof.get("atr14"), errors="coerce")
            conf = (prob - 0.5).abs() * 2.0
            # Keep sanity-check aligned with runtime backtest proxy logic.
            proxy = (conf * atr * (max(1, int(h)) ** 0.5)).replace([float("inf"), -float("inf")], pd.NA).dropna()
            proxy_max = float(proxy.max()) if len(proxy) else 0.0
            grid_min = float(min(min_move_grid)) if len(min_move_grid) else 0.0
            proxy_stats["proxy_max"] = proxy_max
            proxy_stats["grid_min"] = grid_min
            if grid_min > proxy_max:
                return (
                    h,
                    [],
                    (
                        "min_expected_move_grid_above_proxy_max:"
                        f"grid_min={grid_min:.6f}>proxy_max={proxy_max:.6f};"
                        "lower --min-expected-move-grid for this timeframe/day"
                    ),
                    proxy_stats,
                )
        except Exception:
            pass
    out: list[dict] = []
    for pl in longs:
        for ps in shorts:
            if ps >= pl:
                continue
            for min_move in min_move_grid:
                for notional_usd in notional_usd_grid:
                    _, bt = run_prob_backtest(
                        oof,
                        p_enter_long=pl,
                        p_enter_short=ps,
                        fee_bps=fee_bps,
                        slippage_bps=slippage_bps,
                        stop_loss_pct=stop_loss_pct,
                        take_profit_pct=take_profit_pct,
                        min_expected_move_pct=min_move,
                        min_tp_reach_prob=float(min_tp_reach_prob),
                        tp_min_factor=tp_min_factor,
                        dynamic_tp_enabled=dynamic_tp_enabled,
                        cooldown_bars=int(cooldown_bars),
                        trend_filter=str(trend_filter),
                        min_abs_ema_gap=float(min_abs_ema_gap),
                        notional_usd=notional_usd,
                        leverage=float(leverage),
                        signal_mode=str(signal_mode),
                        execution_mode=str(execution_mode),
                        order_type=str(order_type),
                        hold_bars=int(h),
                        limit_offset_bps=float(limit_offset_bps),
                        require_trend_filter_features=True,
                    )
                    passed, fail_keys = _gate_decision(fold_metrics, bt, thresholds)
                    score = bt["net_return_pct"] - abs(bt["max_drawdown_pct"]) * 0.5 + fold_metrics["auc_mean"] * 10.0
                    if int(bt.get("trades", 0)) == 0:
                        score -= 100.0
                    out.append(
                        {
                            "horizon_bars": h,
                            "p_enter_long": pl,
                            "p_enter_short": ps,
                            "min_expected_move_pct": min_move,
                            "trend_filter": str(trend_filter),
                            "min_abs_ema_gap": float(min_abs_ema_gap),
                            "notional_usd": notional_usd,
                            "leverage": float(leverage),
                            "signal_mode": str(signal_mode),
                            "gate_pass": passed,
                            "fail_keys": fail_keys,
                            "score": score,
                            "walk_forward": fold_metrics,
                            "backtest": bt,
                        }
                    )
    return h, out, None, proxy_stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Grid-search horizon and entry thresholds for gate pass.")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--layer", default="raw", choices=["raw", "core"], help="Data layer for search input.")
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--min-train-rows", type=int, default=2200)
    parser.add_argument("--n-folds", type=int, default=4)
    parser.add_argument("--fee-bps", type=float, default=10.0)
    parser.add_argument("--slippage-bps", type=float, default=5.0)
    parser.add_argument("--stop-loss-pct", type=float, default=0.01)
    parser.add_argument("--take-profit-pct", type=float, default=0.02)
    parser.add_argument("--min-tp-reach-prob", type=float, default=0.58)
    parser.add_argument("--tp-min-factor", type=float, default=0.7, help="Dynamic TP floor factor")
    parser.add_argument("--disable-dynamic-tp", action="store_true")
    parser.add_argument("--cooldown-bars", type=int, default=0, help="Cooldown bars between entries")
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
    parser.add_argument("--min-expected-move-grid", default="0.0,0.001,0.002,0.003", help="CSV of min expected move thresholds")
    parser.add_argument("--notional-usd-grid", default="10", help="CSV of fixed trade notional values in USD")
    parser.add_argument("--leverage", type=float, default=1.0)
    parser.add_argument("--signal-mode", default="both", choices=["both", "long_only", "short_only"])
    parser.add_argument("--execution-mode", default="research", choices=["research", "exchange_like"])
    parser.add_argument("--order-type", default="market", choices=["market", "limit"])
    parser.add_argument("--limit-offset-bps", type=float, default=2.0)
    parser.add_argument("--position-size-grid", default=None, help="Deprecated alias for --notional-usd-grid")
    parser.add_argument("--horizons-grid", default="1,2,3,4,6,8", help="CSV of horizon bars")
    parser.add_argument("--p-long-grid", default="0.52,0.54,0.56,0.58,0.60", help="CSV of long probability thresholds")
    parser.add_argument("--p-short-grid", default="0.48,0.46,0.44,0.42,0.40", help="CSV of short probability thresholds")
    parser.add_argument("--min-net-return-pct-goal", type=float, default=100.0, help="Goal filter for best setup selection")
    parser.add_argument("--workers", type=int, default=1, help="Parallel workers for horizon-level search")
    args = parser.parse_args()
    data_layer = str(getattr(args, "layer", "raw"))

    project_root = Path(__file__).resolve().parents[2]
    enforce_action_allowed(project_root, action="search_gate_candidate")
    thresholds = _load_thresholds(project_root)
    raw = load_ohlcv_range(
        project_root,
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=args.start_date,
        end_date=args.end_date,
        layer=data_layer,
    )

    horizons = [int(x.strip()) for x in args.horizons_grid.split(",") if x.strip()]
    longs = [float(x.strip()) for x in args.p_long_grid.split(",") if x.strip()]
    shorts = [float(x.strip()) for x in args.p_short_grid.split(",") if x.strip()]
    results: list[dict] = []
    horizon_errors: list[dict] = []
    horizon_proxy_stats: list[dict] = []
    min_move_grid = [float(x.strip()) for x in args.min_expected_move_grid.split(",") if x.strip()]
    notional_grid_raw = args.position_size_grid if args.position_size_grid else args.notional_usd_grid
    notional_usd_grid = [float(x.strip()) for x in notional_grid_raw.split(",") if x.strip()]
    workers_req = max(1, int(args.workers))
    workers_used = min(workers_req, max(1, len(horizons)))
    raw_rows = raw.to_dict(orient="records")
    if workers_used <= 1 or len(horizons) <= 1:
        for h in horizons:
            _, h_results, h_error, h_stats = _evaluate_horizon(
                raw_rows=raw_rows,
                h=int(h),
                min_train_rows=int(args.min_train_rows),
                n_folds=int(args.n_folds),
                longs=longs,
                shorts=shorts,
                min_move_grid=min_move_grid,
                notional_usd_grid=notional_usd_grid,
                fee_bps=float(args.fee_bps),
                slippage_bps=float(args.slippage_bps),
                stop_loss_pct=float(args.stop_loss_pct),
                take_profit_pct=float(args.take_profit_pct),
                min_tp_reach_prob=float(args.min_tp_reach_prob),
                tp_min_factor=float(args.tp_min_factor),
                dynamic_tp_enabled=(not args.disable_dynamic_tp),
                cooldown_bars=int(args.cooldown_bars),
                trend_filter=str(args.trend_filter),
                min_abs_ema_gap=float(args.min_abs_ema_gap),
                leverage=float(args.leverage),
                signal_mode=str(args.signal_mode),
                execution_mode=str(args.execution_mode),
                order_type=str(args.order_type),
                limit_offset_bps=float(args.limit_offset_bps),
                thresholds=thresholds,
            )
            results.extend(h_results)
            if isinstance(h_stats, dict):
                horizon_proxy_stats.append(h_stats)
            if h_error:
                horizon_errors.append({"horizon_bars": int(h), "error": str(h_error)})
    else:
        with ProcessPoolExecutor(max_workers=workers_used) as ex:
            fut_map = {
                ex.submit(
                    _evaluate_horizon,
                    raw_rows=raw_rows,
                    h=int(h),
                    min_train_rows=int(args.min_train_rows),
                    n_folds=int(args.n_folds),
                    longs=longs,
                    shorts=shorts,
                    min_move_grid=min_move_grid,
                    notional_usd_grid=notional_usd_grid,
                    fee_bps=float(args.fee_bps),
                    slippage_bps=float(args.slippage_bps),
                    stop_loss_pct=float(args.stop_loss_pct),
                    take_profit_pct=float(args.take_profit_pct),
                    min_tp_reach_prob=float(args.min_tp_reach_prob),
                    tp_min_factor=float(args.tp_min_factor),
                    dynamic_tp_enabled=(not args.disable_dynamic_tp),
                    cooldown_bars=int(args.cooldown_bars),
                    trend_filter=str(args.trend_filter),
                    min_abs_ema_gap=float(args.min_abs_ema_gap),
                    leverage=float(args.leverage),
                    signal_mode=str(args.signal_mode),
                    execution_mode=str(args.execution_mode),
                    order_type=str(args.order_type),
                    limit_offset_bps=float(args.limit_offset_bps),
                    thresholds=thresholds,
                ): int(h)
                for h in horizons
            }
            for fut in as_completed(fut_map):
                h = fut_map[fut]
                try:
                    _, h_results, h_error, h_stats = fut.result()
                    results.extend(h_results)
                    if isinstance(h_stats, dict):
                        horizon_proxy_stats.append(h_stats)
                    if h_error:
                        horizon_errors.append({"horizon_bars": int(h), "error": str(h_error)})
                except Exception as e:
                    horizon_errors.append({"horizon_bars": int(h), "error": f"worker_exception:{e}"})

    if not results:
        hint = (
            "No search results produced. "
            "Likely not enough rows for walk-forward given min_train_rows/n_folds/horizons. "
            f"Try lower --min-train-rows or --n-folds. horizon_errors={horizon_errors}"
        )
        raise RuntimeError(hint)

    results.sort(key=lambda x: x["score"], reverse=True)
    best = results[0]
    passed = [r for r in results if r["gate_pass"]]
    goal_min = float(args.min_net_return_pct_goal)
    goal_hits = [r for r in results if float((r.get("backtest") or {}).get("net_return_pct", 0.0)) >= goal_min]
    best_pass = passed[0] if passed else None
    best_goal = goal_hits[0] if goal_hits else None
    top_candidates = results[:100]
    all_candidates_lite = []
    for r in results:
        bt = r.get("backtest", {}) if isinstance(r, dict) else {}
        all_candidates_lite.append(
            {
                "horizon_bars": r.get("horizon_bars"),
                "p_enter_long": r.get("p_enter_long"),
                "p_enter_short": r.get("p_enter_short"),
                "min_expected_move_pct": r.get("min_expected_move_pct"),
                "notional_usd": r.get("notional_usd"),
                "leverage": r.get("leverage"),
                "signal_mode": r.get("signal_mode"),
                "gate_pass": r.get("gate_pass"),
                "fail_keys": r.get("fail_keys", []),
                "score": r.get("score"),
                "backtest": {
                    "trades": int(bt.get("trades", 0)),
                    "net_return_pct": float(bt.get("net_return_pct", 0.0)),
                    "max_drawdown_pct": float(bt.get("max_drawdown_pct", 0.0)),
                    "hit_rate": float(bt.get("hit_rate", 0.0)),
                    "no_trade_ratio_days": float(bt.get("no_trade_ratio_days", bt.get("no_trade_ratio", 1.0))),
                    "trades_per_day_avg": float(bt.get("trades_per_day_avg", 0.0)),
                },
            }
        )
    out = {
        "run_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "data_layer": data_layer,
        "date_range": {"start": args.start_date, "end": args.end_date},
        "workers_requested": workers_req,
        "workers_used": workers_used,
        "total_candidates": len(results),
        "pass_candidates": len(passed),
        "goal_min_net_return_pct": goal_min,
        "goal_candidates": len(goal_hits),
        "horizon_errors": horizon_errors,
        "horizon_proxy_stats": horizon_proxy_stats,
        "best_candidate": best,
        "best_pass_candidate": best_pass,
        "best_goal_candidate": best_goal,
        "all_candidates_lite": all_candidates_lite,
        "top5": results[:5],
        "top_candidates": top_candidates,
    }

    out_dir = project_root / "reports" / "pipeline"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = out_dir / f"search_gate_candidate_{args.symbol}_{args.timeframe}_{ts}.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report_path": str(out_path), "pass_candidates": len(passed), "best_score": best["score"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
