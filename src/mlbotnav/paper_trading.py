from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import joblib

from mlbotnav.audit import audit_event
from mlbotnav.backtest import run_prob_backtest
from mlbotnav.dataset import FEATURE_COLUMNS, build_feature_frame, load_ohlcv_range
from mlbotnav.model_registry import load_active_model_snapshot
from mlbotnav.security import require_role
from mlbotnav.workflow_gate import enforce_training_scope


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _resolve_strategy(project_root: Path) -> dict:
    champion_path = project_root / "models" / "registry" / "champion.json"
    defaults = {
        "p_enter_long": 0.55,
        "p_enter_short": 0.45,
        "horizon_bars": 1,
        "fee_bps": 10.0,
        "slippage_bps": 5.0,
        "notional_usd": 10.0,
        "tp_min_factor": 0.7,
        "dynamic_tp_enabled": True,
        "cooldown_bars": 0,
    }
    if not champion_path.exists():
        return defaults
    row = _load_json(champion_path)
    rp = row.get("report_path")
    if not rp or not Path(rp).exists():
        return defaults
    rep = _load_json(Path(rp))
    s = rep.get("strategy", {})
    defaults["p_enter_long"] = float(s.get("p_enter_long", defaults["p_enter_long"]))
    defaults["p_enter_short"] = float(s.get("p_enter_short", defaults["p_enter_short"]))
    defaults["horizon_bars"] = int(s.get("horizon_bars", defaults["horizon_bars"]))
    defaults["fee_bps"] = float(s.get("fee_bps", defaults["fee_bps"]))
    defaults["slippage_bps"] = float(s.get("slippage_bps", defaults["slippage_bps"]))
    defaults["notional_usd"] = float(rep.get("risk_policy", {}).get("notional_usd", defaults["notional_usd"]))
    defaults["tp_min_factor"] = float(rep.get("risk_policy", {}).get("tp_min_factor", defaults["tp_min_factor"]))
    defaults["dynamic_tp_enabled"] = bool(rep.get("risk_policy", {}).get("dynamic_tp_enabled", defaults["dynamic_tp_enabled"]))
    defaults["cooldown_bars"] = int(rep.get("risk_policy", {}).get("cooldown_bars", defaults["cooldown_bars"]))
    return defaults


def main() -> int:
    parser = argparse.ArgumentParser(description="Run paper-trading simulation on active model.")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--start-date", default=None, help="YYYY-MM-DD")
    parser.add_argument("--end-date", default=None, help="YYYY-MM-DD")
    parser.add_argument("--stop-loss-pct", type=float, default=0.01)
    parser.add_argument("--take-profit-pct", type=float, default=0.02)
    parser.add_argument("--min-expected-move-pct", type=float, default=0.0)
    parser.add_argument("--tp-min-factor", type=float, default=None)
    parser.add_argument("--disable-dynamic-tp", action="store_true")
    parser.add_argument("--cooldown-bars", type=int, default=None)
    parser.add_argument("--notional-usd", type=float, default=10.0)
    parser.add_argument("--execution-mode", default="exchange_like", choices=["research", "exchange_like"])
    parser.add_argument("--order-type", default="market", choices=["market", "limit"])
    parser.add_argument("--limit-offset-bps", type=float, default=2.0)
    parser.add_argument("--position-size", type=float, default=None, help="Deprecated alias for --notional-usd")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    role = require_role(project_root, action="paper_trading")
    if not role["allowed"]:
        raise PermissionError(f"RBAC denied for action=paper_trading: {role['reason']}")
    active = load_active_model_snapshot(project_root)
    if not active:
        raise RuntimeError("No active model/champion found for paper trading.")
    model_path = Path(active["model_path"])
    if not model_path.exists():
        raise FileNotFoundError(model_path)

    strategy = _resolve_strategy(project_root)
    if args.end_date is None:
        args.end_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    if args.start_date is None:
        args.start_date = (datetime.strptime(args.end_date, "%Y-%m-%d").date() - timedelta(days=7)).strftime("%Y-%m-%d")
    enforce_training_scope(
        project_root=project_root,
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=args.start_date,
        end_date=args.end_date,
        action_name="paper_trading",
    )

    raw = load_ohlcv_range(
        project_root,
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=args.start_date,
        end_date=args.end_date,
    )
    feat = build_feature_frame(raw, horizon_bars=int(strategy["horizon_bars"]), include_targets=True)
    payload = joblib.load(model_path)
    model = payload["model"]
    features = payload["features"]
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
    optional_cols = list(FEATURE_COLUMNS) + ["ema20", "ema50", "ema200"]
    ordered_cols = list(dict.fromkeys(base_cols + optional_cols))
    score_df = feat[[c for c in ordered_cols if c in feat.columns]].copy()
    score_df["prob_up"] = model.predict_proba(feat[features])[:, 1]
    score_df["pred_up"] = (score_df["prob_up"] >= 0.5).astype(int)

    notional_usd = float(args.position_size) if args.position_size is not None else float(args.notional_usd)
    tp_min_factor = float(args.tp_min_factor) if args.tp_min_factor is not None else float(strategy["tp_min_factor"])
    dynamic_tp_enabled = bool(strategy["dynamic_tp_enabled"]) and (not args.disable_dynamic_tp)
    cooldown_bars = int(args.cooldown_bars) if args.cooldown_bars is not None else int(strategy["cooldown_bars"])
    trades, summary = run_prob_backtest(
        score_df,
        p_enter_long=float(strategy["p_enter_long"]),
        p_enter_short=float(strategy["p_enter_short"]),
        fee_bps=float(strategy["fee_bps"]),
        slippage_bps=float(strategy["slippage_bps"]),
        stop_loss_pct=float(args.stop_loss_pct),
        take_profit_pct=float(args.take_profit_pct),
        min_expected_move_pct=float(args.min_expected_move_pct),
        tp_min_factor=tp_min_factor,
        dynamic_tp_enabled=dynamic_tp_enabled,
        cooldown_bars=cooldown_bars,
        notional_usd=float(notional_usd),
        execution_mode=str(args.execution_mode),
        order_type=str(args.order_type),
        hold_bars=int(strategy.get("horizon_bars", 1)),
        limit_offset_bps=float(args.limit_offset_bps),
        require_trend_filter_features=True,
    )

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = project_root / "reports" / "paper"
    out_dir.mkdir(parents=True, exist_ok=True)
    trades_csv = out_dir / f"paper_trades_{args.symbol}_{args.timeframe}_{ts}.csv"
    report_json = out_dir / f"paper_report_{args.symbol}_{args.timeframe}_{ts}.json"
    trades.to_csv(trades_csv, index=False)

    report = {
        "run_utc": ts,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "date_range": {"start": args.start_date, "end": args.end_date},
        "active_model": active,
        "strategy": strategy,
        "risk_policy": {
            "stop_loss_pct": args.stop_loss_pct,
            "take_profit_pct": args.take_profit_pct,
            "min_expected_move_pct": args.min_expected_move_pct,
            "tp_min_factor": tp_min_factor,
            "dynamic_tp_enabled": dynamic_tp_enabled,
            "cooldown_bars": cooldown_bars,
            "notional_usd": notional_usd,
            "execution_mode": str(args.execution_mode),
            "order_type": str(args.order_type),
            "limit_offset_bps": float(args.limit_offset_bps),
        },
        "summary": summary,
        "trades_csv": str(trades_csv),
    }
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    audit_event(
        project_root,
        event="paper_trading_completed",
        payload={
            "report_path": str(report_json),
            "symbol": args.symbol,
            "timeframe": args.timeframe,
            "trades": summary.get("trades"),
            "rbac": role,
        },
    )
    print(json.dumps({"report_path": str(report_json), "trades_csv": str(trades_csv), "trades": summary.get("trades")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
