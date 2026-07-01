from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.data_window_readiness import evaluate_data_window_readiness, write_data_window_readiness_report
from mlbotnav.preflight_policy import get_core_preflight_cfg, resolve_preflight_runtime_args


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _parse_last_json(stdout: str) -> dict[str, Any] | None:
    for line in reversed([x.strip() for x in (stdout or "").splitlines() if x.strip()]):
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                return obj
        except Exception:
            continue
    return None


def _run(project_root: Path, cmd: list[str]) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    try:
        p = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, env=env)
    except KeyboardInterrupt:
        return {
            "cmd": cmd,
            "returncode": 130,
            "stdout_tail": "",
            "stderr_tail": "keyboard_interrupt",
            "parsed_json": {"status": "INTERRUPTED", "reason": "keyboard_interrupt"},
        }
    return {
        "cmd": cmd,
        "returncode": int(p.returncode),
        "stdout_tail": (p.stdout or "")[-6000:],
        "stderr_tail": (p.stderr or "")[-6000:],
        "parsed_json": _parse_last_json(p.stdout or ""),
    }


def _resolve_cycle_outcome(*, failed: bool, steps: list[dict[str, Any]]) -> tuple[str, int]:
    for st in steps:
        if not isinstance(st, dict):
            continue
        if int(st.get("returncode", 0) or 0) == 130:
            return "INTERRUPTED", 130
        parsed = st.get("parsed_json")
        if isinstance(parsed, dict) and str(parsed.get("status", "")).upper() == "INTERRUPTED":
            return "INTERRUPTED", 130
    if bool(failed):
        return "FAIL", 1
    return "PASS", 0


def _extract_interruption_details(steps: list[dict[str, Any]]) -> dict[str, str] | None:
    for st in steps:
        if not isinstance(st, dict):
            continue
        task = str(st.get("task", "") or "").strip()
        reason = ""
        if int(st.get("returncode", 0) or 0) == 130:
            reason = "keyboard_interrupt"
        parsed = st.get("parsed_json")
        if isinstance(parsed, dict):
            p_status = str(parsed.get("status", "")).upper()
            p_reason = str(parsed.get("reason", "") or "").strip()
            if p_status == "INTERRUPTED":
                reason = p_reason or reason or "interrupted"
        if reason:
            return {"interrupted_task": task or "unknown_task", "interrupted_reason": reason}
    return None


def _extract_failure_details(steps: list[dict[str, Any]]) -> dict[str, str] | None:
    for st in steps:
        if not isinstance(st, dict):
            continue
        rc = int(st.get("returncode", 0) or 0)
        if rc == 0 or rc == 130:
            continue
        task = str(st.get("task", "") or "").strip() or "unknown_task"
        reason = ""
        parsed = st.get("parsed_json")
        if isinstance(parsed, dict):
            reason = str(parsed.get("reason", "") or "").strip()
            if not reason:
                reason = str(parsed.get("error", "") or "").strip()
        if not reason:
            reason = str(st.get("error", "") or "").strip()
        if not reason:
            reason = f"returncode_{rc}"
        return {"failed_task": task, "failed_reason": reason}
    return None


def _build_cycle_payload(
    *,
    status: str,
    generated_at_utc: str,
    params: dict[str, Any],
    steps: list[dict[str, Any]],
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": str(status),
        "generated_at_utc": str(generated_at_utc),
        "params": dict(params or {}),
        "steps": list(steps or []),
    }
    interruption = _extract_interruption_details(list(steps or []))
    if interruption is not None:
        payload.update(interruption)
    elif str(status).upper() == "FAIL":
        failure = _extract_failure_details(list(steps or []))
        if failure is not None:
            payload.update(failure)
    return payload


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_core_table_window_readiness(project_root: Path, args: argparse.Namespace) -> dict[str, Any]:
    policy_path = str(getattr(args, "preflight_policy", "configs/preflight_policy.yaml"))
    core_cfg = get_core_preflight_cfg(project_root, policy_path=policy_path)
    payload = evaluate_data_window_readiness(
        project_root,
        symbol=str(args.symbol),
        timeframe=str(args.timeframe),
        start_date=str(args.test_day),
        end_date=str(args.test_end_day),
        layer=str(core_cfg["layer"]),
        require_full_coverage=bool(core_cfg["require_full_coverage"]),
    )
    rp = write_data_window_readiness_report(
        project_root,
        payload=payload,
        action_name=f"contour_cycle_{str(args.mode)}_core_preflight",
    )
    return {
        "cmd": ["python", "-m", "mlbotnav.data_window_readiness(core:test-window)"],
        "returncode": 0 if str(payload.get("status")) == "PASS" else 1,
        "stdout_tail": "",
        "stderr_tail": "",
        "parsed_json": {
            "status": payload.get("status"),
            "report_path": str(rp),
            "failed": int(payload.get("summary", {}).get("missing_days", 0)),
        },
    }


def _build_adaptive_cmd(args: argparse.Namespace) -> list[str]:
    p_long = str(args.p_long_grid if args.mode == "long_only" else args.p_long_grid_short_mode)
    p_short = str(args.p_short_grid if args.mode == "short_only" else args.p_short_grid_long_mode)
    cmd = [
        sys.executable,
        "-m",
        "mlbotnav.adaptive_auto_train",
        "--symbol",
        args.symbol,
        "--timeframe",
        args.timeframe,
        "--train-start",
        args.train_start,
        "--train-end",
        args.train_end,
        "--test-day",
        args.test_day,
        "--test-end-day",
        args.test_end_day,
        "--window-policy",
        "fixed_1d",
        "--signal-mode",
        args.mode,
        "--use-hypothesis-profile",
        "--contour-id",
        args.mode,
        "--repeats",
        str(args.repeats),
        "--goal-net-return-pct",
        str(args.goal_net_return_pct),
        "--allow-subgoal-candidates",
        "--min-train-rows",
        str(args.min_train_rows),
        "--n-folds",
        str(args.n_folds),
        "--fee-bps",
        str(args.fee_bps),
        "--slippage-bps",
        str(args.slippage_bps),
        "--stop-loss-pct",
        str(args.stop_loss_pct),
        "--take-profit-pct",
        str(args.take_profit_pct),
        "--tp-min-factor",
        str(args.tp_min_factor),
        "--min-tp-reach-prob",
        str(args.min_tp_reach_prob),
        "--cooldown-bars",
        str(args.cooldown_bars),
        "--horizons-grid",
        str(args.horizons_grid),
        "--p-long-grid",
        p_long,
        "--p-short-grid",
        p_short,
        "--min-expected-move-grid",
        str(args.min_expected_move_grid),
        "--notional-usd",
        str(args.notional_usd),
        "--leverage",
        str(args.leverage),
        "--execution-mode",
        str(args.execution_mode),
        "--order-type",
        str(args.order_type),
        "--cpu-max-pct",
        str(args.cpu_max_pct),
        "--max-threads",
        str(args.max_threads),
        "--search-workers",
        str(args.search_workers),
        "--speed-profile",
        str(args.speed_profile),
        "--search-engine",
        str(args.search_engine),
        "--preflight-policy",
        str(args.preflight_policy),
        "--temporary-unlock-readiness",
        "--unlock-reason",
        f"P5.3.8 contour cycle {args.mode}",
    ]
    if str(args.search_engine) == "optuna":
        cmd.extend(["--optuna-stage", str(args.optuna_stage)])
        if int(getattr(args, "optuna_n_trials_override", 0)) > 0:
            cmd.extend(["--optuna-n-trials-override", str(int(getattr(args, "optuna_n_trials_override", 0)))])
        if int(getattr(args, "optuna_timeout_sec_override", 0)) > 0:
            cmd.extend(["--optuna-timeout-sec-override", str(int(getattr(args, "optuna_timeout_sec_override", 0)))])
    return cmd


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Single-contour daily cycle (strict separation): adaptive -> 5+ convergence -> hypothesis coverage."
    )
    parser.add_argument("--mode", required=True, choices=["long_only", "short_only"])
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--train-start", required=True)
    parser.add_argument("--train-end", required=True)
    parser.add_argument("--test-day", required=True)
    parser.add_argument("--test-end-day", required=True)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--goal-net-return-pct", type=float, default=1.0)
    parser.add_argument("--min-train-rows", type=int, default=900)
    parser.add_argument("--n-folds", type=int, default=2)
    parser.add_argument("--fee-bps", type=float, default=10.0)
    parser.add_argument("--slippage-bps", type=float, default=5.0)
    parser.add_argument("--stop-loss-pct", type=float, default=0.004)
    parser.add_argument("--take-profit-pct", type=float, default=0.05)
    parser.add_argument("--tp-min-factor", type=float, default=0.7)
    parser.add_argument("--min-tp-reach-prob", type=float, default=0.58)
    parser.add_argument("--cooldown-bars", type=int, default=20)
    parser.add_argument("--horizons-grid", default="1,2,3,4,6,8,12")
    parser.add_argument("--p-long-grid", default="0.55,0.58,0.60,0.62,0.65,0.68,0.72")
    parser.add_argument("--p-short-grid", default="0.45,0.42,0.40,0.38,0.35,0.32,0.30")
    parser.add_argument("--p-short-grid-long-mode", default="0.45")
    parser.add_argument("--p-long-grid-short-mode", default="0.55")
    parser.add_argument("--min-expected-move-grid", default="0.001,0.002,0.003,0.005,0.008")
    parser.add_argument("--notional-usd", type=float, default=10.0)
    parser.add_argument("--leverage", type=float, default=10.0)
    parser.add_argument("--execution-mode", default="exchange_like", choices=["research", "exchange_like"])
    parser.add_argument("--order-type", default="market", choices=["market", "limit"])
    parser.add_argument("--cpu-max-pct", type=float, default=85.0)
    parser.add_argument("--max-threads", type=int, default=8)
    parser.add_argument("--search-workers", type=int, default=8)
    parser.add_argument("--speed-profile", default="turbo", choices=["custom", "turbo", "balanced", "full"])
    parser.add_argument("--search-engine", default="grid", choices=["grid", "optuna"])
    parser.add_argument("--optuna-stage", default="auto", choices=["auto", "A", "B", "C"])
    parser.add_argument("--optuna-n-trials-override", type=int, default=0)
    parser.add_argument("--optuna-timeout-sec-override", type=int, default=0)
    parser.add_argument("--run-dir", default="reports/table_canon_current")
    parser.add_argument("--preflight-policy", default="configs/preflight_policy.yaml")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    preflight_resolved = resolve_preflight_runtime_args(
        project_root,
        policy_path=str(args.preflight_policy),
        min_train_rows=int(args.min_train_rows),
        n_folds=int(args.n_folds),
        horizons_grid=str(args.horizons_grid),
        legacy_min_train_rows=900,
        legacy_n_folds=2,
        legacy_horizons_grid="1,2,3,4,6,8,12",
    )
    args.min_train_rows = int(preflight_resolved["min_train_rows"])
    args.n_folds = int(preflight_resolved["n_folds"])
    args.horizons_grid = str(preflight_resolved["horizons_grid"])
    raw_layer = str(preflight_resolved["raw_layer"])
    qa_dir = project_root / "reports" / "qa_gate"
    qa_dir.mkdir(parents=True, exist_ok=True)
    out = qa_dir / f"contour_cycle_{args.mode}_{_utc_tag()}.json"

    steps: list[dict[str, Any]] = []
    failed = False
    preflight_cmd = [
        sys.executable,
        "-m",
        "mlbotnav.preflight_window",
        "--symbol",
        args.symbol,
        "--timeframe",
        args.timeframe,
        "--train-start",
        args.train_start,
        "--train-end",
        args.train_end,
        "--test-day",
        args.test_day,
        "--test-end-day",
        args.test_end_day,
        "--min-train-rows",
        str(args.min_train_rows),
        "--n-folds",
        str(args.n_folds),
        "--horizons-grid",
        str(args.horizons_grid),
        "--layer",
        raw_layer,
    ]
    rp = _run(project_root, preflight_cmd)
    rp["task"] = "preflight_window_raw"
    steps.append(rp)
    if rp["returncode"] != 0:
        failed = True
    if not failed:
        rp_core = _run_core_table_window_readiness(project_root, args)
        rp_core["task"] = "data_window_readiness_core_for_table_convergence"
        steps.append(rp_core)
        if rp_core["returncode"] != 0:
            failed = True

    adaptive_cmd = _build_adaptive_cmd(args)
    r1 = None
    if not failed:
        r1 = _run(project_root, adaptive_cmd)
        r1["task"] = f"adaptive_auto_train_{args.mode}"
        steps.append(r1)
        if r1["returncode"] != 0:
            failed = True

    summary_path = None
    oos_report = None
    if (not failed) and (r1 is not None):
        parsed = r1.get("parsed_json") or {}
        sp = str(parsed.get("summary_path", "") or "").strip()
        if not sp:
            failed = True
            steps.append({"task": "resolve_summary_path", "error": "summary_path_missing"})
        else:
            summary_path = Path(sp)
            if not summary_path.is_absolute():
                summary_path = (project_root / summary_path).resolve()
            if not summary_path.exists():
                failed = True
                steps.append({"task": "resolve_summary_path", "error": "summary_path_not_found", "summary_path": str(summary_path)})
    if not failed and summary_path is not None:
        sm = _load_json(summary_path)
        oos_report = str((sm.get("best_oos") or {}).get("oos_report", "") or "").strip()
        if not oos_report:
            failed = True
            steps.append({"task": "resolve_oos_report", "error": "oos_report_missing", "summary_path": str(summary_path)})

    if not failed and oos_report:
        r2 = _run(
            project_root,
            [
                sys.executable,
                "-m",
                "mlbotnav.table_convergence_5plus",
                "--oos-report",
                oos_report,
                "--run-dir",
                str(args.run_dir),
                "--with-gate",
            ],
        )
        r2["task"] = "table_convergence_5plus"
        steps.append(r2)
        if r2["returncode"] != 0:
            failed = True

    if not failed and summary_path is not None:
        r3 = _run(
            project_root,
            [
                sys.executable,
                "-m",
                "mlbotnav.hypothesis_coverage_audit",
                "--contour-id",
                args.mode,
                "--summary-path",
                str(summary_path),
            ],
        )
        r3["task"] = "hypothesis_coverage_audit"
        steps.append(r3)
        if r3["returncode"] != 0:
            failed = True

    final_status, exit_code = _resolve_cycle_outcome(failed=bool(failed), steps=steps)
    payload = _build_cycle_payload(
        status=final_status,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        params={
            "mode": args.mode,
            "symbol": args.symbol,
            "timeframe": args.timeframe,
            "train_start": args.train_start,
            "train_end": args.train_end,
            "test_day": args.test_day,
            "test_end_day": args.test_end_day,
            "repeats": int(args.repeats),
            "run_dir": str((project_root / args.run_dir).resolve()),
            "search_engine": str(args.search_engine),
            "optuna_stage": (str(args.optuna_stage) if str(args.search_engine) == "optuna" else None),
            "optuna_n_trials_override": (int(args.optuna_n_trials_override) if str(args.search_engine) == "optuna" else None),
            "optuna_timeout_sec_override": (int(args.optuna_timeout_sec_override) if str(args.search_engine) == "optuna" else None),
        },
        steps=steps,
    )
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "report_path": str(out)}, ensure_ascii=False))
    return int(exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
