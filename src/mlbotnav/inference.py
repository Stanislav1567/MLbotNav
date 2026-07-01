from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from mlbotnav.audit import audit_event
from mlbotnav.dataset import build_feature_frame, load_ohlcv_range
from mlbotnav.model_registry import load_active_model_snapshot
from mlbotnav.pct_units import normalize_min_expected_move_pct
from mlbotnav.runtime_contract import CALIBRATION_MODE_NONE, SIGNAL_CONTRACT_VERSION
from mlbotnav.runtime_trading_fields import build_runtime_trading_fields
from mlbotnav.security import require_role
from mlbotnav.workflow_gate import enforce_training_scope


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _resolve_strategy_defaults(project_root: Path) -> dict:
    champion_path = project_root / "models" / "registry" / "champion.json"
    defaults = {
        "p_enter_long": 0.55,
        "p_enter_short": 0.45,
        "horizon_bars": 1,
        "stop_loss_pct": 0.01,
        "take_profit_pct": 0.02,
        "min_expected_move_pct": 0.003,
        "min_tp_reach_prob": 0.58,
        "dynamic_tp_enabled": True,
        "tp_min_factor": 0.7,
        "fee_bps": 10.0,
        "slippage_bps": 5.0,
    }
    if not champion_path.exists():
        return defaults
    row = _load_json(champion_path)
    metrics_bt = row.get("metrics", {}).get("backtest", {})
    rep_path = row.get("report_path")
    if rep_path and Path(rep_path).exists():
        rep = _load_json(Path(rep_path))
        strategy = rep.get("strategy", {})
        metrics_bt = rep.get("metrics", {}).get("backtest", metrics_bt)
        return {
            "p_enter_long": float(strategy.get("p_enter_long", defaults["p_enter_long"])),
            "p_enter_short": float(strategy.get("p_enter_short", defaults["p_enter_short"])),
            "horizon_bars": int(strategy.get("horizon_bars", defaults["horizon_bars"])),
            "stop_loss_pct": float(strategy.get("stop_loss_pct", metrics_bt.get("stop_loss_pct", defaults["stop_loss_pct"]))),
            "take_profit_pct": float(strategy.get("take_profit_pct", metrics_bt.get("take_profit_pct", defaults["take_profit_pct"]))),
            "min_expected_move_pct": normalize_min_expected_move_pct(strategy.get("min_expected_move_pct", metrics_bt.get("min_expected_move_pct", defaults["min_expected_move_pct"]))),
            "min_tp_reach_prob": float(strategy.get("min_tp_reach_prob", metrics_bt.get("min_tp_reach_prob", defaults["min_tp_reach_prob"]))),
            "dynamic_tp_enabled": bool(strategy.get("dynamic_tp_enabled", defaults["dynamic_tp_enabled"])),
            "tp_min_factor": float(strategy.get("tp_min_factor", defaults["tp_min_factor"])),
            "fee_bps": float(strategy.get("fee_bps", metrics_bt.get("fee_bps", defaults["fee_bps"]))),
            "slippage_bps": float(strategy.get("slippage_bps", metrics_bt.get("slippage_bps", defaults["slippage_bps"]))),
        }
    merged = dict(defaults)
    for key in ("stop_loss_pct", "take_profit_pct", "min_expected_move_pct", "min_tp_reach_prob", "fee_bps", "slippage_bps"):
        if key in metrics_bt:
            if key == "min_expected_move_pct":
                merged[key] = normalize_min_expected_move_pct(metrics_bt[key])
            else:
                merged[key] = float(metrics_bt[key])
    return merged


def _fallback_latest_model_path(project_root: Path) -> Path | None:
    model_dir = project_root / "models" / "pipeline"
    if not model_dir.exists():
        return None
    cands = sorted(model_dir.glob("champion_candidate_*.joblib"), key=lambda p: p.stat().st_mtime, reverse=True)
    return cands[0] if cands else None


def _signal_id(symbol: str, timeframe: str, signal_time_utc: str) -> str:
    compact = signal_time_utc.replace("-", "").replace(":", "").replace("T", "_").replace("Z", "")
    return f"sig_{symbol}_{timeframe}_{compact}"


def build_inference_events_frame(
    feat: pd.DataFrame,
    prob_up: np.ndarray,
    *,
    symbol: str,
    timeframe: str,
    p_long: float,
    p_short: float,
    horizon_bars: int,
    stop_loss_pct: float,
    take_profit_pct: float,
    min_expected_move_pct: float,
    min_tp_reach_prob: float,
    dynamic_tp_enabled: bool,
    tp_min_factor: float,
    run_id: str,
) -> pd.DataFrame:
    base_cols = ["open_time_utc", "open", "high", "low", "close", "volume"]
    density_cols = [c for c in feat.columns if c.startswith("density_")]
    out = feat[base_cols + density_cols].copy()
    out["prob_up"] = prob_up.astype(float)

    raw_side = np.zeros(len(out), dtype=int)
    raw_side[out["prob_up"].to_numpy(dtype=float) >= float(p_long)] = 1
    raw_side[out["prob_up"].to_numpy(dtype=float) <= float(p_short)] = -1

    conf = np.clip(np.abs(out["prob_up"].to_numpy(dtype=float) - 0.5) * 2.0, 0.0, 1.0)
    atr_proxy = (
        np.abs(feat["atr14"].to_numpy(dtype=float))
        if "atr14" in feat.columns
        else np.zeros(len(out), dtype=float)
    )
    pred_move_proxy = conf * np.maximum(atr_proxy, 0.0) * math.sqrt(max(1, int(horizon_bars)))
    active_side = raw_side.copy()
    next_open = out["open"].shift(-1).to_numpy(dtype=float)
    has_next_open = np.isfinite(next_open)
    min_move = normalize_min_expected_move_pct(min_expected_move_pct)
    if min_move > 0:
        active_side[(active_side != 0) & (pred_move_proxy < min_move)] = 0
    min_tp_prob = max(0.0, min(1.0, float(min_tp_reach_prob)))
    if min_tp_prob > 0:
        active_side[(active_side != 0) & (conf < min_tp_prob)] = 0
    active_side[(active_side != 0) & (~has_next_open)] = 0

    tp_floor = max(0.0, float(tp_min_factor) * min_move)
    if bool(dynamic_tp_enabled):
        dyn_tp = np.maximum(float(take_profit_pct), np.maximum(tp_floor, float(tp_min_factor) * np.maximum(pred_move_proxy, 0.0)))
    else:
        dyn_tp = np.full(len(out), float(take_profit_pct), dtype=float)

    close_price = out["close"].to_numpy(dtype=float)
    entry_price = np.where(has_next_open, next_open, close_price)
    stop_price = entry_price.copy()
    take_profit_price = entry_price.copy()

    long_mask = active_side > 0
    short_mask = active_side < 0
    stop_price[long_mask] = entry_price[long_mask] * (1.0 - abs(float(stop_loss_pct)))
    stop_price[short_mask] = entry_price[short_mask] * (1.0 + abs(float(stop_loss_pct)))
    take_profit_price[long_mask] = entry_price[long_mask] * (1.0 + dyn_tp[long_mask])
    take_profit_price[short_mask] = entry_price[short_mask] * (1.0 - dyn_tp[short_mask])

    reason = np.full(len(out), "no_edge", dtype=object)
    reason[(raw_side != 0) & (active_side == 0)] = "min_move_fail"
    reason[(raw_side != 0) & (pred_move_proxy >= min_move) & (conf < min_tp_prob)] = "tp_prob_below_min"
    reason[(raw_side != 0) & (~has_next_open)] = "no_next_candle"
    reason[(active_side > 0)] = "long_threshold_pass"
    reason[(active_side < 0)] = "short_threshold_pass"

    signal_time = pd.to_datetime(out["open_time_utc"], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    side_name = pd.Series(active_side).map({1: "BUY", -1: "SELL", 0: "NO_TRADE"}).fillna("NO_TRADE")

    out["signal_id"] = [_signal_id(symbol, timeframe, t) for t in signal_time]
    out["symbol"] = symbol
    out["timeframe"] = timeframe
    out["signal_time_utc"] = signal_time
    out["side"] = active_side
    out["entry_price"] = entry_price
    out["stop_price"] = stop_price
    out["take_profit_price"] = take_profit_price
    out["expected_move_pct"] = pred_move_proxy
    out["tp_reach_prob"] = conf
    out["sl_hit_prob"] = 1.0 - conf
    out["dynamic_tp_pct"] = dyn_tp
    out["decision"] = side_name
    out["reason_code"] = reason
    out["run_id"] = run_id
    out["contract_version"] = SIGNAL_CONTRACT_VERSION
    out["calibration_mode"] = CALIBRATION_MODE_NONE
    out["time_to_target_bars"] = np.where(active_side != 0, int(horizon_bars), np.nan)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Run inference on active model and emit signal events.")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--start-date", default=None, help="YYYY-MM-DD")
    parser.add_argument("--end-date", default=None, help="YYYY-MM-DD")
    parser.add_argument("--p-enter-long", type=float, default=None)
    parser.add_argument("--p-enter-short", type=float, default=None)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    role = require_role(project_root, action="inference")
    if not role["allowed"]:
        raise PermissionError(f"RBAC denied for action=inference: {role['reason']}")
    active = load_active_model_snapshot(project_root)
    if not active:
        raise RuntimeError("No active model/champion found in registry.")
    model_path = Path(active["model_path"])
    if not model_path.exists():
        fb = _fallback_latest_model_path(project_root)
        if fb is None:
            raise FileNotFoundError(f"Active model not found and no fallback model in models/pipeline: {model_path}")
        model_path = fb

    defaults = _resolve_strategy_defaults(project_root)
    p_long = float(args.p_enter_long) if args.p_enter_long is not None else float(defaults["p_enter_long"])
    p_short = float(args.p_enter_short) if args.p_enter_short is not None else float(defaults["p_enter_short"])
    horizon_bars = int(defaults["horizon_bars"])

    if args.end_date is None:
        args.end_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    if args.start_date is None:
        args.start_date = (datetime.strptime(args.end_date, "%Y-%m-%d").date() - timedelta(days=2)).strftime("%Y-%m-%d")
    enforce_training_scope(
        project_root=project_root,
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=args.start_date,
        end_date=args.end_date,
        action_name="inference",
    )

    raw = load_ohlcv_range(
        project_root,
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=args.start_date,
        end_date=args.end_date,
    )
    feat = build_feature_frame(raw, horizon_bars=horizon_bars, include_targets=False)

    payload = joblib.load(model_path)
    model = payload["model"]
    features = payload["features"]
    x = feat[features]
    prob_up = model.predict_proba(x)[:, 1]

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = build_inference_events_frame(
        feat,
        prob_up,
        symbol=args.symbol,
        timeframe=args.timeframe,
        p_long=p_long,
        p_short=p_short,
        horizon_bars=horizon_bars,
        stop_loss_pct=float(defaults["stop_loss_pct"]),
        take_profit_pct=float(defaults["take_profit_pct"]),
        min_expected_move_pct=float(defaults["min_expected_move_pct"]),
        min_tp_reach_prob=float(defaults["min_tp_reach_prob"]),
        dynamic_tp_enabled=bool(defaults["dynamic_tp_enabled"]),
        tp_min_factor=float(defaults["tp_min_factor"]),
        run_id=ts,
    )
    out_dir = project_root / "reports" / "inference"
    out_dir.mkdir(parents=True, exist_ok=True)
    events_csv = out_dir / f"inference_events_{args.symbol}_{args.timeframe}_{ts}.csv"
    mql_latest_csv = out_dir / f"mql_bridge_latest_{args.symbol}_{args.timeframe}.csv"
    report_json = out_dir / f"inference_report_{args.symbol}_{args.timeframe}_{ts}.json"
    out.to_csv(events_csv, index=False)
    out.to_csv(mql_latest_csv, index=False)

    side_counts = out["decision"].value_counts().to_dict()
    report = {
        "run_utc": ts,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "date_range": {"start": args.start_date, "end": args.end_date},
        "active_model": active,
        "model_path": str(model_path),
        "feature_count": len(features),
        "density_feature_count": len([c for c in features if str(c).startswith("density_")]),
        "horizon_bars": horizon_bars,
        "thresholds": {"p_enter_long": p_long, "p_enter_short": p_short},
        "strategy_defaults": defaults,
        "contract_version": SIGNAL_CONTRACT_VERSION,
        "calibration_mode": CALIBRATION_MODE_NONE,
        "rows_scored": int(len(out)),
        "side_counts": side_counts,
        "signal_contract_columns": [
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
        ],
        "time_to_target_mode": "estimated_by_horizon",
        "time_to_target_bars_avg": float(out["time_to_target_bars"].dropna().mean()) if out["time_to_target_bars"].notna().any() else None,
        "events_csv": str(events_csv),
        "mql_bridge_latest_csv": str(mql_latest_csv),
        "mql_bridge_note": "Use events_csv as bridge feed for MT5/MQL (includes density_* columns).",
    }
    report["trading_fields_contract"] = build_runtime_trading_fields(
        symbol=args.symbol,
        timeframe=args.timeframe,
        signal_mode="both",
        execution_mode=None,
        order_type=None,
        stop_loss_pct=defaults.get("stop_loss_pct"),
        take_profit_pct=defaults.get("take_profit_pct"),
        min_expected_move_pct=defaults.get("min_expected_move_pct"),
        min_tp_reach_prob=defaults.get("min_tp_reach_prob"),
        trades=None,
        net_return_pct=None,
        goal_pass=None,
    )
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    audit_event(
        project_root,
        event="inference_completed",
        payload={
            "symbol": args.symbol,
            "timeframe": args.timeframe,
            "rows_scored": int(len(out)),
            "report_path": str(report_json),
            "rbac": role,
        },
    )
    print(
        json.dumps(
            {
                "report_path": str(report_json),
                "events_csv": str(events_csv),
                "mql_bridge_latest_csv": str(mql_latest_csv),
                "rows_scored": int(len(out)),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
