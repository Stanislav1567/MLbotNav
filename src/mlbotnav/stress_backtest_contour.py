from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _parse_json_tail(raw_text: str) -> dict | None:
    if not raw_text:
        return None
    lines = raw_text.splitlines()
    for line in reversed(lines):
        s = line.strip()
        if not s:
            continue
        try:
            obj = json.loads(s)
        except Exception:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def _parse_profiles(raw: str) -> list[tuple[str, float]]:
    """
    Parse profile string like:
    - "base:5,stress_1:10,stress_2:15"
    - "5,10,15" (names will be generated)
    Returns list of (profile_name, slippage_bps).
    """
    out: list[tuple[str, float]] = []
    chunks = [c.strip() for c in str(raw or "").split(",") if c.strip()]
    if not chunks:
        return [("base", 5.0), ("stress_1", 10.0), ("stress_2", 15.0)]
    for idx, chunk in enumerate(chunks, start=1):
        if ":" in chunk:
            name, value = chunk.split(":", 1)
            profile = (name.strip() or f"profile_{idx}")
            slip = float(value.strip())
        else:
            profile = "base" if idx == 1 else f"stress_{idx - 1}"
            slip = float(chunk)
        out.append((profile, slip))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run formal OOS stress contour by re-evaluating the same train report with slippage profiles."
    )
    parser.add_argument("--oos-report", required=True, help="Path to baseline oos_report_*.json")
    parser.add_argument(
        "--slippage-profiles",
        default="base:5,stress_1:10,stress_2:15",
        help="Comma list of slippage profiles. Example: base:5,stress_1:10,stress_2:15",
    )
    parser.add_argument("--fee-bps", type=float, default=None, help="Optional fixed fee bps for all profiles; default uses baseline OOS strategy.fee_bps")
    parser.add_argument("--layer", default="raw", help="Data layer for OOS re-evaluation (raw/core).")
    parser.add_argument("--goal-net-return-pct", type=float, default=None, help="Optional goal override; default uses baseline oos_report goal_net_return_pct_day")
    parser.add_argument("--output-dir", default=None, help="Optional output directory for stress report.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    oos_path = Path(args.oos_report).resolve()
    if not oos_path.exists():
        raise FileNotFoundError(f"oos_report not found: {oos_path}")

    baseline = _load_json(oos_path)
    train_report = str(baseline.get("train_pipeline_report", "")).strip()
    test_day = str(baseline.get("test_day", "")).strip()
    test_end_day = str(baseline.get("test_end_day", test_day)).strip()
    if not train_report or not test_day:
        raise RuntimeError("oos_report must include train_pipeline_report and test_day")

    strategy = baseline.get("strategy", {}) if isinstance(baseline, dict) else {}
    risk = baseline.get("risk_policy", {}) if isinstance(baseline, dict) else {}
    base_fee_bps = float(args.fee_bps) if args.fee_bps is not None else float(strategy.get("fee_bps", 10.0))
    goal = float(args.goal_net_return_pct) if args.goal_net_return_pct is not None else float(baseline.get("goal_net_return_pct_day", 100.0))
    signal_mode = str(risk.get("signal_mode", "both"))
    execution_mode = str(risk.get("execution_mode", "research"))
    order_type = str(risk.get("order_type", "market"))
    limit_offset_bps = float(risk.get("limit_offset_bps", 2.0))
    leverage = float(risk.get("leverage", 1.0))

    profiles = _parse_profiles(args.slippage_profiles)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_dir = Path(args.output_dir) if args.output_dir else (project_root / "reports" / "final_review")
    output_dir.mkdir(parents=True, exist_ok=True)

    runs: list[dict] = []
    for profile_name, slippage_bps in profiles:
        cmd = [
            sys.executable,
            "-m",
            "mlbotnav.oos_evaluate",
            "--train-pipeline-report",
            train_report,
            "--test-day",
            test_day,
            "--test-end-day",
            test_end_day,
            "--layer",
            str(args.layer),
            "--goal-net-return-pct",
            str(goal),
            "--signal-mode",
            signal_mode,
            "--execution-mode",
            execution_mode,
            "--order-type",
            order_type,
            "--limit-offset-bps",
            str(limit_offset_bps),
            "--leverage",
            str(leverage),
            "--fee-bps",
            str(base_fee_bps),
            "--slippage-bps",
            str(float(slippage_bps)),
        ]
        proc = subprocess.run(
            cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        parsed = _parse_json_tail(proc.stdout or "")
        if proc.returncode != 0 or not parsed:
            runs.append(
                {
                    "profile": profile_name,
                    "fee_bps": float(base_fee_bps),
                    "slippage_bps": float(slippage_bps),
                    "returncode": int(proc.returncode),
                    "status": "FAIL",
                    "stderr_tail": (proc.stderr or "")[-1200:],
                    "stdout_tail": (proc.stdout or "")[-1200:],
                }
            )
            continue

        run_oos_path = Path(str(parsed.get("oos_report", ""))).resolve()
        if not run_oos_path.exists():
            runs.append(
                {
                    "profile": profile_name,
                    "fee_bps": float(base_fee_bps),
                    "slippage_bps": float(slippage_bps),
                    "returncode": int(proc.returncode),
                    "status": "FAIL",
                    "error": f"oos_report not found from evaluator: {run_oos_path}",
                }
            )
            continue

        run_oos = _load_json(run_oos_path)
        bt = run_oos.get("backtest", {}) if isinstance(run_oos, dict) else {}
        runs.append(
            {
                "profile": profile_name,
                "fee_bps": float(base_fee_bps),
                "slippage_bps": float(slippage_bps),
                "returncode": int(proc.returncode),
                "status": "PASS",
                "oos_report": str(run_oos_path),
                "backtest_path": ((run_oos.get("artifacts") or {}).get("backtest_path")),
                "net_return_pct": float(bt.get("net_return_pct", 0.0)),
                "trades": int(bt.get("trades", 0)),
                "goal_pass": bool(run_oos.get("goal_pass", False)),
            }
        )

    pass_runs = [r for r in runs if r.get("status") == "PASS"]
    ordered_pass = sorted(pass_runs, key=lambda x: float(x.get("slippage_bps", 0.0)))
    monotonic_cost_impact = True
    for i in range(1, len(ordered_pass)):
        prev_v = float(ordered_pass[i - 1].get("net_return_pct", 0.0))
        cur_v = float(ordered_pass[i].get("net_return_pct", 0.0))
        if cur_v > prev_v + 1e-9:
            monotonic_cost_impact = False
            break

    base_run = next((r for r in runs if r.get("profile") == "base" and r.get("status") == "PASS"), None)
    if base_run is None:
        base_run = ordered_pass[0] if ordered_pass else None
    edge_preserved_under_stress = None
    edge_rule_note = "not_applicable"
    if base_run is not None:
        base_net = float(base_run.get("net_return_pct", 0.0))
        if base_net > 0.0:
            stress_nets = [
                float(r.get("net_return_pct", 0.0))
                for r in ordered_pass
                if float(r.get("slippage_bps", 0.0)) > float(base_run.get("slippage_bps", 0.0))
            ]
            if stress_nets:
                edge_preserved_under_stress = all(v > 0.0 for v in stress_nets)
                edge_rule_note = "base_positive_requires_positive_stress"
            else:
                edge_preserved_under_stress = True
                edge_rule_note = "no_stress_profiles_after_base"
        else:
            edge_rule_note = "base_non_positive"

    symbol = str(baseline.get("symbol", "UNK"))
    timeframe = str(baseline.get("timeframe", "UNK"))
    mode = str(signal_mode)
    day_tag = test_day if test_day == test_end_day else f"{test_day}_to_{test_end_day}"
    stress_report_path = output_dir / f"stress_backtest_contour_{symbol}_{timeframe}_{day_tag}_{mode}_{ts}.json"

    report = {
        "run_utc": ts,
        "source_oos_report": str(oos_path),
        "source_train_pipeline_report": train_report,
        "symbol": symbol,
        "timeframe": timeframe,
        "test_day": test_day,
        "test_end_day": test_end_day,
        "signal_mode": signal_mode,
        "execution_mode": execution_mode,
        "order_type": order_type,
        "layer": str(args.layer),
        "goal_net_return_pct_day": float(goal),
        "profiles_input": [{"profile": name, "slippage_bps": float(slip)} for name, slip in profiles],
        "fee_bps": float(base_fee_bps),
        "runs": runs,
        "checks": {
            "all_profiles_pass": len(pass_runs) == len(profiles),
            "monotonic_cost_impact_non_increasing_net_return_pct": bool(monotonic_cost_impact),
            "edge_preserved_under_stress": edge_preserved_under_stress,
            "edge_rule_note": edge_rule_note,
        },
        "status": "PASS" if len(pass_runs) == len(profiles) else "FAIL",
    }
    stress_report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": report["status"],
                "stress_report": str(stress_report_path),
                "profiles_total": len(profiles),
                "profiles_pass": len(pass_runs),
                "monotonic_cost_impact_non_increasing_net_return_pct": bool(monotonic_cost_impact),
                "edge_preserved_under_stress": edge_preserved_under_stress,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
