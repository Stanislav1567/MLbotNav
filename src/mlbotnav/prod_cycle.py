from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from mlbotnav.audit import audit_event
from mlbotnav.cpu_budget import apply_thread_limits, wait_for_cpu_budget
from mlbotnav.pct_units import normalize_min_expected_move_pct
from mlbotnav.readiness import enforce_action_allowed
from mlbotnav.stage_state import load_stage_state, next_stage, save_stage_state
from mlbotnav.workflow_gate import enforce_training_scope


def _run(project_root: Path, cmd: list[str], *, step_name: str, cpu_budget_cfg: dict | None = None) -> tuple[int, str, str, dict]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    cpu_meta = {
        "enabled": False,
        "max_cpu_pct": None,
        "check_interval_sec": None,
        "max_wait_sec": None,
        "max_threads_per_job": None,
        "waited_sec": 0.0,
        "last_cpu_pct": None,
        "checks": 0,
        "timed_out": False,
        "duration_ms": None,
    }
    cfg = cpu_budget_cfg or {}
    if cfg.get("enabled", False):
        max_cpu_pct = float(cfg.get("max_cpu_pct", 85.0))
        check_interval_sec = float(cfg.get("check_interval_sec", 5))
        max_wait_sec = float(cfg.get("max_wait_sec", 300))
        max_threads = int(cfg.get("max_threads_per_job", 1))
        wait = wait_for_cpu_budget(
            max_cpu_pct=max_cpu_pct,
            check_interval_sec=check_interval_sec,
            max_wait_sec=max_wait_sec,
        )
        env = apply_thread_limits(env, max_threads=max_threads)
        cpu_meta = {
            "enabled": True,
            "max_cpu_pct": max_cpu_pct,
            "check_interval_sec": check_interval_sec,
            "max_wait_sec": max_wait_sec,
            "max_threads_per_job": max_threads,
            "waited_sec": round(wait.waited_sec, 3),
            "last_cpu_pct": wait.last_cpu_pct,
            "checks": wait.checks,
            "timed_out": wait.timed_out,
            "duration_ms": None,
        }
        audit_event(
            project_root,
            event="cpu_budget_checked",
            payload={"step": step_name, **cpu_meta},
        )
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, cwd=project_root, env=env, capture_output=True, text=True)
    cpu_meta["duration_ms"] = round((time.perf_counter() - t0) * 1000.0, 2)
    return proc.returncode, proc.stdout, proc.stderr, cpu_meta


def _latest(glob_pattern: str, root: Path) -> Path | None:
    files = sorted(root.glob(glob_pattern), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def _load_prod_policy(project_root: Path) -> dict:
    p = project_root / "configs" / "prod_policy.yaml"
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_stage_plan(project_root: Path) -> dict:
    p = project_root / "configs" / "stage_plan.yaml"
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _try_parse_json(text: str) -> dict | None:
    t = (text or "").strip()
    if not t:
        return None
    line = t.splitlines()[-1].strip()
    if not line:
        return None
    try:
        obj = json.loads(line)
    except Exception:
        return None
    return obj if isinstance(obj, dict) else None


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _build_stage_params(report: dict) -> dict:
    strategy = report.get("strategy", {}) if isinstance(report, dict) else {}
    risk = report.get("risk_policy", {}) if isinstance(report, dict) else {}
    return {
        "horizon_bars": int(strategy.get("horizon_bars", 1)),
        "p_enter_long": float(strategy.get("p_enter_long", 0.55)),
        "p_enter_short": float(strategy.get("p_enter_short", 0.45)),
        "stop_loss_pct": float(risk.get("stop_loss_pct", 0.01)),
        "take_profit_pct": float(risk.get("take_profit_pct", 0.02)),
        "min_expected_move_pct": normalize_min_expected_move_pct(risk.get("min_expected_move_pct", 0.0)),
        "tp_min_factor": float(risk.get("tp_min_factor", 0.7)),
        "dynamic_tp_enabled": bool(risk.get("dynamic_tp_enabled", True)),
        "cooldown_bars": int(risk.get("cooldown_bars", 0)),
        "notional_usd": float(risk.get("notional_usd", risk.get("position_size", 10.0))),
        "selected_model": str(report.get("selected_model", "unknown")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one prod-like cycle: ingest -> train/eval -> registry -> drift -> pack -> rollback-guard.")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--start-date", default=None)
    parser.add_argument("--end-date", default=None)
    parser.add_argument("--min-train-rows", type=int, default=10000)
    parser.add_argument("--n-folds", type=int, default=5)
    parser.add_argument("--horizon-bars", type=int, default=6)
    parser.add_argument("--p-enter-long", type=float, default=0.58)
    parser.add_argument("--p-enter-short", type=float, default=0.40)
    parser.add_argument("--stop-loss-pct", type=float, default=0.01)
    parser.add_argument("--take-profit-pct", type=float, default=0.02)
    parser.add_argument("--min-expected-move-pct", type=float, default=0.0)
    parser.add_argument("--tp-min-factor", type=float, default=0.7)
    parser.add_argument("--disable-dynamic-tp", action="store_true")
    parser.add_argument("--cooldown-bars", type=int, default=0)
    parser.add_argument("--notional-usd", type=float, default=10.0)
    parser.add_argument("--position-size", type=float, default=None, help="Deprecated alias for --notional-usd")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    enforce_action_allowed(project_root, action="prod_cycle")
    policy = _load_prod_policy(project_root).get("prod", {})
    cycle = policy.get("cycle", {})
    cpu_budget = policy.get("cpu_budget", {})
    hard_fail_on_sla = bool(cycle.get("hard_fail_on_sla", True))
    require_inference_metrics = bool(cycle.get("require_inference_metrics", True))
    stage_plan_cfg = _load_stage_plan(project_root)
    stage_list = (
        (stage_plan_cfg.get("stage_plan", {}) or {}).get("stages", [])
        or ["D1", "D2", "D3", "D5", "D30", "D60", "D90", "READY"]
    )

    notional_usd = float(args.position_size) if args.position_size is not None else float(args.notional_usd)
    min_expected_move_pct = normalize_min_expected_move_pct(args.min_expected_move_pct)
    if args.end_date is None:
        args.end_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    if args.start_date is None:
        args.start_date = (datetime.strptime(args.end_date, "%Y-%m-%d").date() - timedelta(days=29)).strftime("%Y-%m-%d")
    enforce_training_scope(
        project_root=project_root,
        symbol=args.symbol,
        timeframe=args.timeframe,
        start_date=args.start_date,
        end_date=args.end_date,
        action_name="prod_cycle",
    )

    steps = []

    if cycle.get("run_incremental_ingest", True):
        rc, out, err, cpu_meta = _run(
            project_root,
            [
                sys.executable,
                "-m",
                "mlbotnav.ingest_incremental",
                "--symbol",
                args.symbol,
                "--timeframes",
                "1,5,15,30,60,240,D",
                "--lookback-days",
                "3",
            ],
            step_name="ingest_incremental",
            cpu_budget_cfg=cpu_budget,
        )
        steps.append(
            {
                "step": "ingest_incremental",
                "rc": rc,
                "stdout_tail": out[-1000:],
                "stderr_tail": err[-1000:],
                "cpu_budget": cpu_meta,
            }
        )

    if cycle.get("run_technical_analysis", True):
        rc, out, err, cpu_meta = _run(
            project_root,
            [
                sys.executable,
                "-m",
                "mlbotnav.technical_analysis",
                "--symbol",
                args.symbol,
                "--timeframe",
                args.timeframe,
                "--start-date",
                args.start_date,
                "--end-date",
                args.end_date,
                "--min-tp-pct",
                "0.01",
                "--min-expected-move-pct",
                str(min_expected_move_pct),
            ],
            step_name="technical_analysis",
            cpu_budget_cfg=cpu_budget,
        )
        steps.append(
            {
                "step": "technical_analysis",
                "rc": rc,
                "stdout_tail": out[-1200:],
                "stderr_tail": err[-1200:],
                "cpu_budget": cpu_meta,
            }
        )

    rc, out, err, cpu_meta = _run(
        project_root,
        [
            sys.executable,
            "-m",
            "mlbotnav.pipeline_train_eval",
            "--symbol",
            args.symbol,
            "--timeframe",
            args.timeframe,
            "--start-date",
            args.start_date,
            "--end-date",
            args.end_date,
            "--horizon-bars",
            str(args.horizon_bars),
            "--min-train-rows",
            str(args.min_train_rows),
            "--n-folds",
            str(args.n_folds),
            "--fee-bps",
            "10",
            "--slippage-bps",
            "5",
            "--p-enter-long",
            str(args.p_enter_long),
            "--p-enter-short",
            str(args.p_enter_short),
            "--stop-loss-pct",
            str(args.stop_loss_pct),
            "--take-profit-pct",
            str(args.take_profit_pct),
            "--min-expected-move-pct",
            str(min_expected_move_pct),
            "--notional-usd",
            str(notional_usd),
            "--tp-min-factor",
            str(args.tp_min_factor),
            "--cooldown-bars",
            str(int(args.cooldown_bars)),
            *(["--disable-dynamic-tp"] if args.disable_dynamic_tp else []),
            "--promote-if-pass",
        ],
        step_name="pipeline_train_eval",
        cpu_budget_cfg=cpu_budget,
    )
    steps.append(
        {
            "step": "pipeline_train_eval",
            "rc": rc,
            "stdout_tail": out[-1200:],
            "stderr_tail": err[-1200:],
            "cpu_budget": cpu_meta,
        }
    )

    latest_report = _latest(f"reports/pipeline/pipeline_report_{args.symbol}_{args.timeframe}_*.json", project_root)
    if latest_report is None:
        raise RuntimeError("No pipeline report found after pipeline step")

    if cycle.get("run_stage_ladder", False):
        rc, out, err, cpu_meta = _run(
            project_root,
            [
                sys.executable,
                "-m",
                "mlbotnav.stage_ladder",
                "--symbol",
                args.symbol,
                "--timeframe",
                args.timeframe,
                "--end-date",
                args.end_date,
                "--max-stages",
                "7",
            ],
            step_name="stage_ladder",
            cpu_budget_cfg=cpu_budget,
        )
        steps.append(
            {
                "step": "stage_ladder",
                "rc": rc,
                "stdout_tail": out[-1200:],
                "stderr_tail": err[-1200:],
                "parsed": _try_parse_json(out),
                "cpu_budget": cpu_meta,
            }
        )
    elif cycle.get("run_stage_engine", True):
        state = load_stage_state(project_root, stages=stage_list)
        stage = str(state.get("current_stage", stage_list[0]))
        if stage != "READY":
            latest_rep_obj = _read_json(latest_report)
            stage_params = _build_stage_params(latest_rep_obj)
            context: dict = {}
            prev = state.get("last_result_meta")
            if isinstance(prev, dict) and prev:
                context["prev_stage_meta"] = prev
            context["symbol"] = args.symbol
            context["timeframe"] = args.timeframe
            context["date_range"] = {"start": args.start_date, "end": args.end_date}
            rc, out, err, cpu_meta = _run(
                project_root,
                [
                    sys.executable,
                    "-m",
                    "mlbotnav.stage_engine",
                    "--stage",
                    stage,
                    "--pipeline-report",
                    str(latest_report),
                    "--params-json",
                    json.dumps(stage_params, ensure_ascii=False),
                    "--context-json",
                    json.dumps(context, ensure_ascii=False),
                ],
                step_name="stage_engine",
                cpu_budget_cfg=cpu_budget,
            )
            parsed = _try_parse_json(out)
            stage_passed = bool((parsed or {}).get("passed", False))
            if parsed and not parsed.get("blocked_by_negative_memory", False):
                state["last_result_meta"] = parsed.get("meta", {}) if isinstance(parsed.get("meta"), dict) else {}
                state.setdefault("history", []).append(
                    {
                        "at_utc": datetime.now(timezone.utc).isoformat(),
                        "stage": stage,
                        "passed": stage_passed,
                        "rating": parsed.get("rating"),
                        "reasons": parsed.get("reasons", []),
                        "report_path": parsed.get("report_path"),
                    }
                )
                if stage_passed:
                    state["last_completed_stage"] = stage
                    nxt = next_stage(stage, stages=stage_list)
                    if nxt:
                        state["current_stage"] = nxt
                save_stage_state(project_root, state)
            steps.append(
                {
                    "step": "stage_engine",
                    "stage": stage,
                    "rc": rc,
                    "stdout_tail": out[-1200:],
                    "stderr_tail": err[-1200:],
                    "parsed": parsed,
                    "cpu_budget": cpu_meta,
                }
            )

    if cycle.get("run_inference", True):
        rc, out, err, cpu_meta = _run(
            project_root,
            [
                sys.executable,
                "-m",
                "mlbotnav.inference",
                "--symbol",
                args.symbol,
                "--timeframe",
                args.timeframe,
                "--start-date",
                args.start_date,
                "--end-date",
                args.end_date,
            ],
            step_name="inference",
            cpu_budget_cfg=cpu_budget,
        )
        steps.append(
            {
                "step": "inference",
                "rc": rc,
                "stdout_tail": out[-1000:],
                "stderr_tail": err[-1000:],
                "parsed": _try_parse_json(out),
                "cpu_budget": cpu_meta,
            }
        )

    if cycle.get("run_inference_service_probe", True):
        rc, out, err, cpu_meta = _run(
            project_root,
            [
                sys.executable,
                "-m",
                "mlbotnav.inference_service_probe",
                "--symbol",
                args.symbol,
                "--timeframe",
                args.timeframe,
                "--start-date",
                args.start_date,
                "--end-date",
                args.end_date,
                "--attempts",
                "20",
            ],
            step_name="inference_service_probe",
            cpu_budget_cfg=cpu_budget,
        )
        steps.append(
            {
                "step": "inference_service_probe",
                "rc": rc,
                "stdout_tail": out[-1000:],
                "stderr_tail": err[-1000:],
                "parsed": _try_parse_json(out),
                "cpu_budget": cpu_meta,
            }
        )

    if cycle.get("run_paper_trading", True):
        rc, out, err, cpu_meta = _run(
            project_root,
            [
                sys.executable,
                "-m",
                "mlbotnav.paper_trading",
                "--symbol",
                args.symbol,
                "--timeframe",
                args.timeframe,
                "--start-date",
                args.start_date,
                "--end-date",
                args.end_date,
                "--stop-loss-pct",
                str(args.stop_loss_pct),
                "--take-profit-pct",
                str(args.take_profit_pct),
            "--min-expected-move-pct",
            str(min_expected_move_pct),
                "--notional-usd",
                str(notional_usd),
                "--tp-min-factor",
                str(args.tp_min_factor),
                "--cooldown-bars",
                str(int(args.cooldown_bars)),
                *(["--disable-dynamic-tp"] if args.disable_dynamic_tp else []),
            ],
            step_name="paper_trading",
            cpu_budget_cfg=cpu_budget,
        )
        steps.append(
            {
                "step": "paper_trading",
                "rc": rc,
                "stdout_tail": out[-1000:],
                "stderr_tail": err[-1000:],
                "parsed": _try_parse_json(out),
                "cpu_budget": cpu_meta,
            }
        )

    if cycle.get("run_drift_monitor", True):
        ref_end = (datetime.strptime(args.end_date, "%Y-%m-%d").date() - timedelta(days=15)).strftime("%Y-%m-%d")
        ref_start = (datetime.strptime(ref_end, "%Y-%m-%d").date() - timedelta(days=14)).strftime("%Y-%m-%d")
        cur_start = (datetime.strptime(args.end_date, "%Y-%m-%d").date() - timedelta(days=14)).strftime("%Y-%m-%d")
        rc, out, err, cpu_meta = _run(
            project_root,
            [
                sys.executable,
                "-m",
                "mlbotnav.monitor_drift",
                "--symbol",
                args.symbol,
                "--timeframe",
                args.timeframe,
                "--reference-start",
                ref_start,
                "--reference-end",
                ref_end,
                "--current-start",
                cur_start,
                "--current-end",
                args.end_date,
                "--psi-alert-threshold",
                "0.2",
            ],
            step_name="monitor_drift",
            cpu_budget_cfg=cpu_budget,
        )
        steps.append(
            {
                "step": "monitor_drift",
                "rc": rc,
                "stdout_tail": out[-1000:],
                "stderr_tail": err[-1000:],
                "cpu_budget": cpu_meta,
            }
        )
    if cycle.get("run_drift_retrain_trigger", True):
        rc, out, err, cpu_meta = _run(
            project_root,
            [
                sys.executable,
                "-m",
                "mlbotnav.drift_retrain_trigger",
                "--symbol",
                args.symbol,
                "--timeframe",
                args.timeframe,
                "--max-alert-age-sec",
                str(int((policy.get("automation", {}) or {}).get("drift_alert_sla_sec", 120))),
            ],
            step_name="drift_retrain_trigger",
            cpu_budget_cfg=cpu_budget,
        )
        steps.append(
            {
                "step": "drift_retrain_trigger",
                "rc": rc,
                "stdout_tail": out[-1000:],
                "stderr_tail": err[-1000:],
                "parsed": _try_parse_json(out),
                "cpu_budget": cpu_meta,
            }
        )

    rc, out, err, cpu_meta = _run(
        project_root,
        [
            sys.executable,
            "-m",
            "mlbotnav.rollback_guard",
            "--pipeline-report",
            str(latest_report),
        ],
        step_name="rollback_guard",
        cpu_budget_cfg=cpu_budget,
    )
    steps.append(
        {
            "step": "rollback_guard",
            "rc": rc,
            "stdout_tail": out[-1000:],
            "stderr_tail": err[-1000:],
            "cpu_budget": cpu_meta,
        }
    )

    if cycle.get("run_pack_on_cycle", True):
        rc, out, err, cpu_meta = _run(
            project_root,
            [
                sys.executable,
                "-m",
                "mlbotnav.build_pack",
                "--date",
                args.end_date,
                "--symbol",
                args.symbol,
                "--timeframe",
                args.timeframe,
            ],
            step_name="build_pack",
            cpu_budget_cfg=cpu_budget,
        )
        steps.append(
            {
                "step": "build_pack",
                "rc": rc,
                "stdout_tail": out[-1000:],
                "stderr_tail": err[-1000:],
                "cpu_budget": cpu_meta,
            }
        )

    rc, out, err, cpu_meta = _run(
        project_root,
        [
            sys.executable,
            "-m",
            "mlbotnav.run_governance_maintenance",
        ],
        step_name="governance_maintenance",
        cpu_budget_cfg=cpu_budget,
    )
    steps.append(
        {
            "step": "governance_maintenance",
            "rc": rc,
            "stdout_tail": out[-1000:],
            "stderr_tail": err[-1000:],
            "cpu_budget": cpu_meta,
        }
    )

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = project_root / "reports" / "prod_cycle"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"prod_cycle_{args.symbol}_{args.timeframe}_{ts}.json"
    summary = {
        "run_utc": ts,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "date_range": {"start": args.start_date, "end": args.end_date},
        "latest_pipeline_report": str(latest_report),
        "steps": steps,
    }
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    if cycle.get("run_sla_monitor", True):
        sla_cmd = [
            sys.executable,
            "-m",
            "mlbotnav.monitor_sla",
            "--prod-cycle-report",
            str(out_path),
        ]
        if hard_fail_on_sla:
            sla_cmd.append("--hard-fail-on-breach")
        if require_inference_metrics:
            sla_cmd.append("--require-inference-metrics")
        rc, out, err, cpu_meta = _run(
            project_root,
            sla_cmd,
            step_name="monitor_sla",
            cpu_budget_cfg=cpu_budget,
        )
        steps.append(
            {
                "step": "monitor_sla",
                "rc": rc,
                "stdout_tail": out[-1000:],
                "stderr_tail": err[-1000:],
                "cpu_budget": cpu_meta,
                "parsed": _try_parse_json(out),
            }
        )
        summary["steps"] = steps
        out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        if rc != 0:
            audit_event(
                project_root,
                event="prod_cycle_sla_gate_failed",
                payload={"report_path": str(out_path), "monitor_sla_rc": rc},
            )
            print(json.dumps({"report_path": str(out_path), "steps": len(steps), "status": "FAIL", "failed_step": "monitor_sla"}))
            return int(rc)
    audit_event(project_root, event="prod_cycle_completed", payload={"report_path": str(out_path), "symbol": args.symbol, "timeframe": args.timeframe})
    print(json.dumps({"report_path": str(out_path), "steps": len(steps), "status": "PASS"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
