from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from mlbotnav.audit import audit_event
from mlbotnav.cpu_budget import apply_thread_limits, wait_for_cpu_budget
from mlbotnav.workflow_gate import load_workflow_gate


def _date_range(start_date: str, end_date: str) -> list[str]:
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    if end < start:
        raise ValueError("end_date must be >= start_date")
    days = []
    cur = start
    while cur <= end:
        days.append(cur.strftime("%Y-%m-%d"))
        cur = cur + timedelta(days=1)
    return days


def _load_prod_policy(project_root: Path) -> dict:
    p = project_root / "configs" / "prod_policy.yaml"
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill daily Bybit ingestion over date range.")
    parser.add_argument("--start-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end-date", required=True, help="YYYY-MM-DD")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframes", default="1")
    parser.add_argument("--continue-on-error", action="store_true")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    cpu_budget_cfg = (_load_prod_policy(project_root).get("prod", {})).get("cpu_budget", {})
    days = _date_range(args.start_date, args.end_date)
    gate = load_workflow_gate(project_root)
    timeframe_tokens = [t.strip().lower() for t in str(args.timeframes).split(",") if t.strip()]
    locked_tf = str(gate.get("locked_timeframe", "1m")).lower()
    if locked_tf == "1m":
        allowed_tokens = {"1", "1m"}
        if any(t not in allowed_tokens for t in timeframe_tokens):
            raise RuntimeError(
                "Workflow gate blocked: backfill currently locked to minute timeframe only (1m). "
                f"Requested timeframes='{args.timeframes}'."
            )
    require_confirm = bool(gate.get("require_user_confirmation_for_30d", True))
    allow_30d = bool(gate.get("allow_30d_window", False))
    if require_confirm and (not allow_30d) and len(days) >= 30:
        raise RuntimeError(
            "Workflow gate blocked: 30-day backfill is disabled until user confirms minute-stage result."
        )

    ok_days: list[str] = []
    failed_days: list[dict] = []
    cpu_budget_events: list[dict] = []

    for d in days:
        cmd = [
            sys.executable,
            "-m",
            "mlbotnav.ingest_day",
            "--date",
            d,
            "--symbol",
            args.symbol,
            "--timeframes",
            args.timeframes,
        ]
        env = os.environ.copy()
        env["PYTHONPATH"] = "src"
        cpu_event = {
            "date": d,
            "enabled": False,
            "waited_sec": 0.0,
            "last_cpu_pct": None,
            "checks": 0,
            "timed_out": False,
            "max_cpu_pct": None,
            "max_threads_per_job": None,
        }
        if cpu_budget_cfg.get("enabled", False):
            max_cpu_pct = float(cpu_budget_cfg.get("max_cpu_pct", 85.0))
            check_interval_sec = float(cpu_budget_cfg.get("check_interval_sec", 5))
            max_wait_sec = float(cpu_budget_cfg.get("max_wait_sec", 300))
            max_threads = int(cpu_budget_cfg.get("max_threads_per_job", 1))
            wait = wait_for_cpu_budget(
                max_cpu_pct=max_cpu_pct,
                check_interval_sec=check_interval_sec,
                max_wait_sec=max_wait_sec,
            )
            env = apply_thread_limits(env, max_threads=max_threads)
            cpu_event = {
                "date": d,
                "enabled": True,
                "waited_sec": round(wait.waited_sec, 3),
                "last_cpu_pct": wait.last_cpu_pct,
                "checks": wait.checks,
                "timed_out": wait.timed_out,
                "max_cpu_pct": max_cpu_pct,
                "max_threads_per_job": max_threads,
            }
            audit_event(project_root, event="cpu_budget_checked", payload={"step": "ingest_backfill_day", **cpu_event})
        cpu_budget_events.append(cpu_event)
        proc = subprocess.run(cmd, cwd=project_root, env=env, capture_output=True, text=True)
        if proc.returncode == 0:
            ok_days.append(d)
        else:
            failed_days.append({"date": d, "returncode": proc.returncode, "stderr": proc.stderr[-2000:]})
            if not args.continue_on_error:
                break

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = project_root / "reports" / "ingestion"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"backfill_{args.symbol}_{args.start_date}_{args.end_date}_{ts}.json"
    report = {
        "run_utc": ts,
        "symbol": args.symbol,
        "timeframes": args.timeframes,
        "start_date": args.start_date,
        "end_date": args.end_date,
        "days_total": len(days),
        "days_success": len(ok_days),
        "days_failed": len(failed_days),
        "ok_days": ok_days,
        "failed_days": failed_days,
        "cpu_budget": cpu_budget_events,
    }
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    audit_event(
        project_root,
        event="ingest_backfill_completed",
        payload={
            "symbol": args.symbol,
            "start_date": args.start_date,
            "end_date": args.end_date,
            "days_success": len(ok_days),
            "days_failed": len(failed_days),
            "report_path": str(out_path),
        },
    )

    print(json.dumps({"report_path": str(out_path), "days_success": len(ok_days), "days_failed": len(failed_days)}))
    return 0 if not failed_days else 1


if __name__ == "__main__":
    raise SystemExit(main())
