from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

from mlbotnav.audit import audit_event
from mlbotnav.negative_memory import add_negative_event, build_fingerprint, is_fingerprint_blocked
from mlbotnav.readiness import enforce_action_allowed


def _load_stage_cfg(project_root: Path) -> dict:
    p = project_root / "configs" / "stage_plan.yaml"
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _rating_from_report(report: dict) -> float:
    bt = report.get("backtest", {})
    net = float(bt.get("net_return_pct", 0.0))
    mdd = abs(float(bt.get("max_drawdown_pct", 0.0)))
    sharpe = float(bt.get("sharpe_like", 0.0))
    hit = float(bt.get("hit_rate", 0.0))
    no_trade_days = float(bt.get("no_trade_ratio_days", 1.0))
    score = (
        0.35 * max(min(net * 2.0 + 50.0, 100.0), 0.0)
        + 0.25 * max(min(sharpe * 10.0 + 50.0, 100.0), 0.0)
        + 0.20 * max(min(100.0 - mdd * 4.0, 100.0), 0.0)
        + 0.10 * max(min(hit * 100.0, 100.0), 0.0)
        + 0.10 * max(min((1.0 - no_trade_days) * 100.0, 100.0), 0.0)
    )
    return float(round(score, 3))


def _daily_trade_stats(report: dict) -> dict:
    bt_path = ((report.get("artifacts") or {}).get("backtest_path") or "").strip()
    if not bt_path:
        return {"available": False}
    p = Path(bt_path)
    if not p.exists():
        return {"available": False}
    df = pd.read_csv(p)
    if df.empty:
        return {"available": True, "positive_days_ratio": 0.0, "all_days_positive": False}
    df["_date"] = pd.to_datetime(df["open_time_utc"], utc=True).dt.strftime("%Y-%m-%d")
    by_day = df.groupby("_date")["net_return"].sum()
    positive_days_ratio = float((by_day > 0).mean()) if len(by_day) else 0.0
    all_days_positive = bool((by_day > 0).all()) if len(by_day) else False
    return {
        "available": True,
        "positive_days_ratio": positive_days_ratio,
        "all_days_positive": all_days_positive,
        "days_count": int(len(by_day)),
    }


def _evaluate_stage(
    report: dict,
    *,
    stage: str,
    cfg: dict,
    prev_stage_meta: dict | None = None,
) -> tuple[bool, list[str], float, dict]:
    trans = (cfg.get("stage_plan", {}).get("transitions", {}) or {}).get(stage, {})
    min_rating = float(trans.get("min_rating", 0))
    max_dd = float(trans.get("max_drawdown_pct_abs", 1000.0))
    min_trades = int(trans.get("min_trades", 0))
    max_no_trade_ratio_days = float(trans.get("max_no_trade_ratio_days", 1.0))
    min_stability_score = float(trans.get("min_stability_score", 0.0))
    require_positive_net_pnl_each_day = bool(trans.get("require_positive_net_pnl_each_day", False))
    max_drawdown_regression_pp_vs_prev = trans.get("max_drawdown_regression_pp_vs_prev_stage", None)
    rating = _rating_from_report(report)
    bt = report.get("backtest", {})
    day_stats = _daily_trade_stats(report)
    stability_score = float(day_stats.get("positive_days_ratio", 0.0)) if day_stats.get("available") else 0.0
    reasons: list[str] = []
    if rating < min_rating:
        reasons.append(f"rating_low:{rating}<{min_rating}")
    if abs(float(bt.get("max_drawdown_pct", 0.0))) > max_dd:
        reasons.append(f"drawdown_high:{abs(float(bt.get('max_drawdown_pct', 0.0))):.3f}>{max_dd:.3f}")
    if int(bt.get("trades", 0)) < min_trades:
        reasons.append(f"trades_low:{int(bt.get('trades', 0))}<{min_trades}")
    if float(bt.get("no_trade_ratio_days", 1.0)) > max_no_trade_ratio_days:
        reasons.append(
            f"no_trade_ratio_days_high:{float(bt.get('no_trade_ratio_days', 1.0)):.3f}>{max_no_trade_ratio_days:.3f}"
        )
    if stability_score < min_stability_score:
        reasons.append(f"stability_low:{stability_score:.3f}<{min_stability_score:.3f}")
    if require_positive_net_pnl_each_day:
        if not day_stats.get("available"):
            reasons.append("daily_pnl_unavailable")
        elif not day_stats.get("all_days_positive", False):
            reasons.append("daily_pnl_not_positive_each_day")
    if max_drawdown_regression_pp_vs_prev is not None and prev_stage_meta:
        prev_dd = abs(float(prev_stage_meta.get("max_drawdown_pct", 0.0)))
        cur_dd = abs(float(bt.get("max_drawdown_pct", 0.0)))
        dd_delta = cur_dd - prev_dd
        if dd_delta > float(max_drawdown_regression_pp_vs_prev):
            reasons.append(
                f"drawdown_regression_high:{dd_delta:.3f}>{float(max_drawdown_regression_pp_vs_prev):.3f}"
            )
    if not report.get("gate", {}).get("pass", False):
        reasons.append("pipeline_gate_not_passed")
    meta = {
        "stability_score": stability_score,
        "no_trade_ratio_days": float(bt.get("no_trade_ratio_days", 1.0)),
        "max_drawdown_pct": float(bt.get("max_drawdown_pct", 0.0)),
        "daily_stats": day_stats,
    }
    return len(reasons) == 0, reasons, rating, meta


def evaluate_stage_transition(
    *,
    project_root: Path,
    stage: str,
    pipeline_report_path: Path,
    params: dict,
    context: dict,
) -> tuple[dict, int]:
    cfg = _load_stage_cfg(project_root)
    cooldown = int((cfg.get("negative_memory", {}) or {}).get("cooldown_hours", 48))
    report = json.loads(pipeline_report_path.read_text(encoding="utf-8"))
    fp = build_fingerprint(params=params, context=context)
    blocked, block_meta = is_fingerprint_blocked(project_root, fingerprint=fp)
    if blocked:
        return (
            {
                "stage": stage,
                "passed": False,
                "blocked_by_negative_memory": True,
                "block_meta": block_meta,
                "pipeline_report": str(pipeline_report_path),
            },
            1,
        )

    prev_stage_meta = context.get("prev_stage_meta") if isinstance(context, dict) else None
    passed, reasons, rating, eval_meta = _evaluate_stage(
        report,
        stage=stage,
        cfg=cfg,
        prev_stage_meta=prev_stage_meta if isinstance(prev_stage_meta, dict) else None,
    )
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = project_root / "reports" / "stages"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"stage_eval_{stage}_{report.get('symbol','NA')}_{report.get('timeframe','NA')}_{ts}.json"
    output = {
        "run_utc": ts,
        "stage": stage,
        "pipeline_report": str(pipeline_report_path),
        "rating": rating,
        "passed": passed,
        "reasons": reasons,
        "fingerprint": fp,
        "meta": eval_meta,
    }
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    if not passed:
        add_negative_event(
            project_root,
            fingerprint=fp,
            stage=stage,
            reason=";".join(reasons) if reasons else "stage_failed",
            params=params,
            context=context,
            cooldown_hours=cooldown,
        )

    audit_event(
        project_root,
        event="stage_evaluated",
        payload={
            "stage": stage,
            "passed": passed,
            "rating": rating,
            "reasons": reasons,
            "report_path": str(out_path),
        },
    )
    return {
        "report_path": str(out_path),
        "passed": passed,
        "rating": rating,
        "reasons": reasons,
        "meta": eval_meta,
    }, (0 if passed else 1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate stage transition with negative-memory controls.")
    parser.add_argument("--stage", required=True, help="D1,D2,D3,D5,D30,D60,D90")
    parser.add_argument("--pipeline-report", required=True, help="Path to pipeline_report_*.json")
    parser.add_argument("--params-json", default="{}", help="JSON object with strategy/model params")
    parser.add_argument("--context-json", default="{}", help="JSON object with market context")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    enforce_action_allowed(project_root, action="stage_engine")
    report_path = Path(args.pipeline_report)
    params = json.loads(args.params_json)
    context = json.loads(args.context_json)
    output, rc = evaluate_stage_transition(
        project_root=project_root,
        stage=args.stage,
        pipeline_report_path=report_path,
        params=params,
        context=context,
    )
    print(json.dumps(output, ensure_ascii=False))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
