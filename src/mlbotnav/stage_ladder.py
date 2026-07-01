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
from mlbotnav.negative_memory import summarize_negative_memory
from mlbotnav.pct_units import normalize_min_expected_move_pct
from mlbotnav.readiness import enforce_action_allowed
from mlbotnav.stage_engine import evaluate_stage_transition
from mlbotnav.stage_state import load_stage_state, next_stage, save_stage_state
from mlbotnav.workflow_gate import enforce_training_scope


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _run(project_root: Path, cmd: list[str], *, step_name: str, cpu_budget_cfg: dict) -> tuple[int, str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    if cpu_budget_cfg.get("enabled", False):
        wait_for_cpu_budget(
            max_cpu_pct=float(cpu_budget_cfg.get("max_cpu_pct", 85.0)),
            check_interval_sec=float(cpu_budget_cfg.get("check_interval_sec", 5)),
            max_wait_sec=float(cpu_budget_cfg.get("max_wait_sec", 300)),
        )
        env = apply_thread_limits(env, max_threads=int(cpu_budget_cfg.get("max_threads_per_job", 1)))
    proc = subprocess.run(cmd, cwd=project_root, env=env, capture_output=True, text=True)
    audit_event(
        project_root,
        event="stage_ladder_step_ran",
        payload={
            "step": step_name,
            "cmd": cmd,
            "rc": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-800:],
            "stderr_tail": (proc.stderr or "")[-800:],
        },
    )
    return proc.returncode, proc.stdout, proc.stderr


def _latest(glob_pattern: str, root: Path) -> Path | None:
    files = sorted(root.glob(glob_pattern), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def _days_by_stage(cfg: dict) -> dict:
    out = {"D1": 1, "D2": 2, "D3": 3, "D5": 5, "D30": 30, "D60": 60, "D90": 90}
    out.update(((cfg.get("stage_plan", {}) or {}).get("windows_days", {}) or {}))
    return {k: int(v) for k, v in out.items()}


def _date_window(end_date: str, *, days: int) -> tuple[str, str]:
    end_d = datetime.strptime(end_date, "%Y-%m-%d").date()
    start_d = end_d - timedelta(days=max(1, int(days)) - 1)
    return start_d.strftime("%Y-%m-%d"), end_d.strftime("%Y-%m-%d")


def _parse_json_line(text: str) -> dict | None:
    lines = [x.strip() for x in (text or "").splitlines() if x.strip()]
    if not lines:
        return None
    for ln in reversed(lines):
        try:
            obj = json.loads(ln)
        except Exception:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def _build_stage_params_from_report(report: dict) -> dict:
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
        "model_family": str(report.get("selected_model", "auto")),
    }


def _run_d1_search(
    *,
    project_root: Path,
    symbol: str,
    timeframe: str,
    start_date: str,
    end_date: str,
    cfg: dict,
    cpu_budget: dict,
) -> tuple[dict | None, dict]:
    d1_cfg = (((cfg.get("stage_plan", {}) or {}).get("d1_exhaustive", {}) or {}))
    if not bool(d1_cfg.get("enabled", True)):
        return None, {"enabled": False}
    cmd = [
        sys.executable,
        "-m",
        "mlbotnav.search_gate_candidate",
        "--symbol",
        symbol,
        "--timeframe",
        timeframe,
        "--start-date",
        start_date,
        "--end-date",
        end_date,
        "--min-train-rows",
        str(int(d1_cfg.get("min_train_rows", 800))),
        "--n-folds",
        str(int(d1_cfg.get("n_folds", 3))),
        "--horizons-grid",
        str(d1_cfg.get("horizons_grid", "1,2,3,4,6,8")),
        "--p-long-grid",
        str(d1_cfg.get("p_long_grid", "0.52,0.54,0.56,0.58,0.60")),
        "--p-short-grid",
        str(d1_cfg.get("p_short_grid", "0.48,0.46,0.44,0.42,0.40")),
        "--min-expected-move-grid",
        str(d1_cfg.get("min_expected_move_grid", "0.0,0.001,0.002,0.003")),
        "--notional-usd-grid",
        str(d1_cfg.get("notional_usd_grid", d1_cfg.get("position_size_grid", "10"))),
    ]
    rc, out, _err = _run(project_root, cmd, step_name="d1_exhaustive_search", cpu_budget_cfg=cpu_budget)
    if rc != 0:
        return None, {"enabled": True, "rc": rc}
    parsed = _parse_json_line(out)
    if not parsed:
        return None, {"enabled": True, "rc": rc}
    rep_path = parsed.get("report_path")
    if not rep_path or not Path(rep_path).exists():
        return None, {"enabled": True, "rc": rc}
    report = json.loads(Path(rep_path).read_text(encoding="utf-8"))
    best = report.get("best_candidate", {}) if isinstance(report, dict) else {}
    params = {
        "horizon_bars": int(best.get("horizon_bars", 1)),
        "p_enter_long": float(best.get("p_enter_long", 0.55)),
        "p_enter_short": float(best.get("p_enter_short", 0.45)),
        "min_expected_move_pct": normalize_min_expected_move_pct(best.get("min_expected_move_pct", 0.0)),
        "notional_usd": float(best.get("notional_usd", best.get("position_size", 10.0))),
        "model_family": "auto",
    }
    coverage = {
        "enabled": True,
        "report_path": rep_path,
        "total_candidates": int(report.get("total_candidates", 0)),
        "pass_candidates": int(report.get("pass_candidates", 0)),
    }
    return params, coverage


def main() -> int:
    parser = argparse.ArgumentParser(description="Run full stage ladder D1->...->D90->READY")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--end-date", default=None, help="YYYY-MM-DD, default yesterday UTC")
    parser.add_argument("--max-stages", type=int, default=7, help="Safety cap for one run")
    parser.add_argument("--stop-at-stage", default=None, help="Optional D1..D90/READY")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    enforce_action_allowed(project_root, action="stage_ladder")
    prod_policy = _load_yaml(project_root / "configs" / "prod_policy.yaml").get("prod", {})
    cpu_budget = prod_policy.get("cpu_budget", {})
    stage_cfg = _load_yaml(project_root / "configs" / "stage_plan.yaml")
    stage_list = ((stage_cfg.get("stage_plan", {}) or {}).get("stages", []) or ["D1", "D2", "D3", "D5", "D30", "D60", "D90", "READY"])
    windows = _days_by_stage(stage_cfg)
    state = load_stage_state(project_root, stages=stage_list)
    stage = str(state.get("current_stage", stage_list[0]))
    if stage == "READY":
        print(json.dumps({"status": "ready", "message": "Already in READY stage"}))
        return 0

    end_date = args.end_date
    if end_date is None:
        end_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

    attempts = []
    for _ in range(max(1, args.max_stages)):
        if stage == "READY":
            break
        if args.stop_at_stage and stage != args.stop_at_stage and stage_list.index(stage) > stage_list.index(args.stop_at_stage):
            break
        days = int(windows.get(stage, 1))
        start_date, effective_end = _date_window(end_date, days=days)
        enforce_training_scope(
            project_root=project_root,
            symbol=args.symbol,
            timeframe=args.timeframe,
            start_date=start_date,
            end_date=effective_end,
            action_name=f"stage_ladder_{stage}",
        )

        stage_params = dict(state.get("active_params") or {})
        d1_coverage = None
        if stage == "D1":
            d1_params, d1_coverage = _run_d1_search(
                project_root=project_root,
                symbol=args.symbol,
                timeframe=args.timeframe,
                start_date=start_date,
                end_date=effective_end,
                cfg=stage_cfg,
                cpu_budget=cpu_budget,
            )
            if d1_params:
                stage_params.update(d1_params)

        cmd = [
            sys.executable,
            "-m",
            "mlbotnav.pipeline_train_eval",
            "--symbol",
            args.symbol,
            "--timeframe",
            args.timeframe,
            "--start-date",
            start_date,
            "--end-date",
            effective_end,
            "--horizon-bars",
            str(int(stage_params.get("horizon_bars", 1))),
            "--min-train-rows",
            str(int(max(400, min(days * 1200, 10000)))),
            "--n-folds",
            "4",
            "--fee-bps",
            "10",
            "--slippage-bps",
            "5",
            "--p-enter-long",
            str(float(stage_params.get("p_enter_long", 0.55))),
            "--p-enter-short",
            str(float(stage_params.get("p_enter_short", 0.45))),
            "--stop-loss-pct",
            str(float(stage_params.get("stop_loss_pct", 0.01))),
            "--take-profit-pct",
            str(float(stage_params.get("take_profit_pct", 0.02))),
            "--min-expected-move-pct",
            str(normalize_min_expected_move_pct(stage_params.get("min_expected_move_pct", 0.0))),
            "--notional-usd",
            str(float(stage_params.get("notional_usd", 10.0))),
            "--tp-min-factor",
            str(float(stage_params.get("tp_min_factor", 0.7))),
            "--cooldown-bars",
            str(int(stage_params.get("cooldown_bars", 0))),
            *(["--disable-dynamic-tp"] if not bool(stage_params.get("dynamic_tp_enabled", True)) else []),
            "--model-family",
            str(stage_params.get("model_family", "auto")),
        ]
        rc, out, err = _run(project_root, cmd, step_name=f"pipeline_{stage}", cpu_budget_cfg=cpu_budget)
        run_out = _parse_json_line(out) or {}
        report_path = run_out.get("report_path")
        if rc != 0 or not report_path or not Path(report_path).exists():
            attempts.append(
                {
                    "stage": stage,
                    "start_date": start_date,
                    "end_date": effective_end,
                    "failed_at": "pipeline_train_eval",
                    "rc": rc,
                    "stderr_tail": (err or "")[-1000:],
                }
            )
            break

        pipe = json.loads(Path(report_path).read_text(encoding="utf-8"))
        stage_params = _build_stage_params_from_report(pipe)
        context = {
            "symbol": args.symbol,
            "timeframe": args.timeframe,
            "date_range": {"start": start_date, "end": effective_end},
            "model": pipe.get("selected_model"),
        }
        prev_meta = state.get("last_result_meta")
        if isinstance(prev_meta, dict) and prev_meta:
            context["prev_stage_meta"] = prev_meta
        stage_out, stage_rc = evaluate_stage_transition(
            project_root=project_root,
            stage=stage,
            pipeline_report_path=Path(report_path),
            params=stage_params,
            context=context,
        )
        neg_stats = summarize_negative_memory(project_root, stage=stage)
        stage_passed = bool(stage_out.get("passed", False))
        attempts.append(
            {
                "stage": stage,
                "start_date": start_date,
                "end_date": effective_end,
                "pipeline_report": report_path,
                "stage_result": stage_out,
                "negative_memory": neg_stats,
                "d1_coverage": d1_coverage,
            }
        )

        if stage_passed:
            state["active_params"] = stage_params
            state["last_result_meta"] = stage_out.get("meta", {})
            state["last_completed_stage"] = stage
            state.setdefault("history", []).append(
                {
                    "at_utc": datetime.now(timezone.utc).isoformat(),
                    "stage": stage,
                    "passed": True,
                    "report_path": stage_out.get("report_path"),
                    "params": stage_params,
                }
            )
            nxt = next_stage(stage, stages=stage_list)
            if nxt:
                state["current_stage"] = nxt
                stage = nxt
            else:
                stage = "READY"
        else:
            state.setdefault("history", []).append(
                {
                    "at_utc": datetime.now(timezone.utc).isoformat(),
                    "stage": stage,
                    "passed": False,
                    "report_path": stage_out.get("report_path"),
                    "reasons": stage_out.get("reasons", []),
                    "params": stage_params,
                }
            )
            break
        save_stage_state(project_root, state)

    save_stage_state(project_root, state)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = project_root / "reports" / "stages"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"stage_ladder_{args.symbol}_{args.timeframe}_{ts}.json"
    result = {
        "run_utc": ts,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "end_date": end_date,
        "attempts": attempts,
        "state_after": state,
    }
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    audit_event(project_root, event="stage_ladder_completed", payload={"report_path": str(out_path), "attempts": len(attempts)})
    print(json.dumps({"report_path": str(out_path), "attempts": len(attempts), "current_stage": state.get("current_stage")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
