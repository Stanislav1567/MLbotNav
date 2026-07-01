from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import yaml

from mlbotnav.audit import audit_event


def _load_policy(project_root: Path) -> dict:
    p = project_root / "configs" / "prod_policy.yaml"
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _pct(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    return float(np.percentile(np.array(values, dtype=float), q))


def main() -> int:
    parser = argparse.ArgumentParser(description="SLA monitor for prod cycle (latency/error/perf).")
    parser.add_argument("--prod-cycle-report", required=True, help="Path to reports/prod_cycle/prod_cycle_*.json")
    parser.add_argument("--hard-fail-on-breach", action="store_true", help="Return non-zero when SLA/perf/trigger breaches are detected.")
    parser.add_argument("--require-inference-metrics", action="store_true", help="Treat missing inference_service metrics as SLA breach.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    policy = _load_policy(project_root).get("prod", {})
    rollback = policy.get("rollback", {}) or {}
    kpi = policy.get("kpi", {}) or {}
    rep = _read_json(Path(args.prod_cycle_report))
    steps = rep.get("steps", []) if isinstance(rep, dict) else []
    total_steps = len(steps)
    failed_steps = sum(1 for s in steps if int(s.get("rc", 1)) != 0)
    error_rate = float(failed_steps / total_steps) if total_steps > 0 else 1.0
    latencies_ms = []
    for s in steps:
        cpu_meta = s.get("cpu_budget", {}) if isinstance(s, dict) else {}
        dur = cpu_meta.get("duration_ms")
        if isinstance(dur, (int, float)):
            latencies_ms.append(float(dur))
    p95_ms = _pct(latencies_ms, 95.0)
    max_ms = max(latencies_ms) if latencies_ms else 0.0

    perf_breaches = []
    trigger_sla_breaches = []
    inference_service_metrics: dict = {}
    pipe_path = rep.get("latest_pipeline_report")
    pipe = _read_json(Path(pipe_path)) if pipe_path and Path(pipe_path).exists() else {}
    wf = pipe.get("walk_forward", {}) if isinstance(pipe, dict) else {}
    bt = pipe.get("backtest", {}) if isinstance(pipe, dict) else {}
    if wf:
        if float(wf.get("auc_mean", 0.0)) < float(kpi.get("min_walkforward_auc", 0.52)):
            perf_breaches.append("walkforward_auc_low")
        if float(wf.get("f1_mean", 0.0)) < float(kpi.get("min_walkforward_f1", 0.05)):
            perf_breaches.append("walkforward_f1_low")
    if bt:
        if abs(float(bt.get("max_drawdown_pct", 0.0))) > float(kpi.get("max_drawdown_pct_abs", 20.0)):
            perf_breaches.append("max_drawdown_high")
        no_trade_days = float(bt.get("no_trade_ratio_days", bt.get("no_trade_ratio", 1.0)))
        if no_trade_days > float(kpi.get("max_no_trade_ratio_days", kpi.get("max_no_trade_ratio", 0.8))):
            perf_breaches.append("no_trade_ratio_days_high")
    for s in steps:
        if str(s.get("step")) != "drift_retrain_trigger":
            continue
        parsed = s.get("parsed", {}) if isinstance(s, dict) else {}
        if isinstance(parsed, dict) and bool(parsed.get("sla_breach", False)):
            trigger_sla_breaches.append("drift_trigger_sla_breach")
    for s in steps:
        if str(s.get("step")) != "inference_service_probe":
            continue
        parsed = s.get("parsed", {}) if isinstance(s, dict) else {}
        if not isinstance(parsed, dict):
            continue
        rp = parsed.get("report_path")
        if rp and Path(rp).exists():
            inference_service_metrics = _read_json(Path(rp))
            break

    sla_breaches = []
    if error_rate > float(rollback.get("max_allowed_error_rate", 0.03)):
        sla_breaches.append(f"error_rate_high:{error_rate:.3f}")
    if p95_ms > float(rollback.get("max_allowed_latency_ms", 300.0)):
        sla_breaches.append(f"p95_latency_high:{p95_ms:.1f}ms")
    if inference_service_metrics:
        av = float(inference_service_metrics.get("availability_pct", 0.0))
        inf_p95 = float(inference_service_metrics.get("latency_ms_p95", 0.0))
        min_av = float(kpi.get("min_inference_availability_pct", 99.5))
        max_inf_p95 = float(kpi.get("max_inference_p95_latency_ms", 300.0))
        if av < min_av:
            sla_breaches.append(f"inference_availability_low:{av:.3f}<{min_av:.3f}")
        if inf_p95 > max_inf_p95:
            sla_breaches.append(f"inference_p95_latency_high:{inf_p95:.3f}ms>{max_inf_p95:.3f}ms")
    elif args.require_inference_metrics:
        sla_breaches.append("inference_metrics_missing")

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = project_root / "reports" / "monitoring"
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"sla_report_{ts}.json"
    alert_required = bool(sla_breaches or perf_breaches or trigger_sla_breaches)
    report = {
        "run_utc": ts,
        "prod_cycle_report": str(Path(args.prod_cycle_report).resolve()),
        "pipeline_report": str(pipe_path) if pipe_path else None,
        "metrics": {
            "steps_total": total_steps,
            "steps_failed": failed_steps,
            "error_rate": error_rate,
            "latency_ms_p95": p95_ms,
            "latency_ms_max": max_ms,
            "inference_service": inference_service_metrics,
        },
        "thresholds": {
            "max_allowed_error_rate": float(rollback.get("max_allowed_error_rate", 0.03)),
            "max_allowed_latency_ms": float(rollback.get("max_allowed_latency_ms", 300.0)),
            "min_walkforward_auc": float(kpi.get("min_walkforward_auc", 0.52)),
            "min_walkforward_f1": float(kpi.get("min_walkforward_f1", 0.05)),
            "max_drawdown_pct_abs": float(kpi.get("max_drawdown_pct_abs", 20.0)),
            "max_no_trade_ratio_days": float(kpi.get("max_no_trade_ratio_days", kpi.get("max_no_trade_ratio", 0.8))),
            "min_inference_availability_pct": float(kpi.get("min_inference_availability_pct", 99.5)),
            "max_inference_p95_latency_ms": float(kpi.get("max_inference_p95_latency_ms", 300.0)),
        },
        "sla_breaches": sla_breaches,
        "perf_breaches": perf_breaches,
        "trigger_sla_breaches": trigger_sla_breaches,
        "alert_required": alert_required,
        "status": "FAIL" if alert_required else "PASS",
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    alert_path = None
    if alert_required:
        alert_path = out_dir / f"sla_alert_{ts}.json"
        alert_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    audit_event(
        project_root,
        event="sla_monitor_completed",
        payload={
            "report_path": str(report_path),
            "alert_required": report["alert_required"],
            "sla_breaches": sla_breaches,
            "perf_breaches": perf_breaches,
            "trigger_sla_breaches": trigger_sla_breaches,
        },
    )
    print(json.dumps({"status": report["status"], "report_path": str(report_path), "alert_path": str(alert_path) if alert_path else None}))
    if args.hard_fail_on_breach and alert_required:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
