from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_last_json(stdout: str) -> dict[str, Any] | None:
    for line in reversed([x.strip() for x in (stdout or "").splitlines() if x.strip()]):
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                return obj
        except Exception:
            continue
    return None


def _run(project_root: Path, args: list[str]) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    p = subprocess.run(args, cwd=project_root, capture_output=True, text=True, env=env)
    return {
        "cmd": args,
        "returncode": p.returncode,
        "stdout_tail": (p.stdout or "")[-6000:],
        "stderr_tail": (p.stderr or "")[-6000:],
        "parsed_json": _parse_last_json(p.stdout or ""),
    }


def _load_default_params(project_root: Path) -> dict[str, Any]:
    p = project_root / "reports" / "table_canon_current" / "state" / "params_snapshot.json"
    if not p.exists():
        return {}
    try:
        return _load_json(p)
    except Exception:
        return {}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run strict TZ gate: step check + full chain check after each fix."
    )
    parser.add_argument("--step", default="P3", help="Current TZ step label (P1/P2/P3/...)")
    parser.add_argument("--symbol", default=None)
    parser.add_argument("--timeframe", default=None)
    parser.add_argument("--start-date", default=None)
    parser.add_argument("--end-date", default=None)
    parser.add_argument("--horizon-bars", type=int, default=None)
    parser.add_argument("--layer", default=None, choices=["raw", "core"])
    parser.add_argument("--oos-report", default=None, help="Optional explicit oos_report path for execution trace")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    defaults = _load_default_params(project_root)

    symbol = str(args.symbol or defaults.get("symbol") or "SOLUSDT")
    timeframe = str(args.timeframe or defaults.get("timeframe") or "1m")
    start_date = str(args.start_date or defaults.get("start_date") or "")
    end_date = str(args.end_date or defaults.get("end_date") or "")
    horizon_bars = int(args.horizon_bars or defaults.get("horizon_bars") or 1)
    layer = str(args.layer or defaults.get("layer") or "raw")
    step = str(args.step or "P3")
    if not start_date or not end_date:
        raise RuntimeError(
            "start/end date are required. Pass --start-date/--end-date or prepare reports/table_canon_current/state/params_snapshot.json"
        )

    ts = _utc_tag()
    qa_dir = project_root / "reports" / "qa_gate"
    qa_dir.mkdir(parents=True, exist_ok=True)
    report_path = qa_dir / f"tz_gate_{ts}.json"

    tasks: list[tuple[str, list[str]]] = []
    # Step-level check first.
    if str(step).upper() == "P3":
        cmd = [sys.executable, "-m", "mlbotnav.execution_trace_pack"]
        if args.oos_report:
            cmd += ["--oos-report", str(args.oos_report)]
        tasks.append(("step_check_execution_trace", cmd))
    elif str(step).upper() == "P4":
        # P4 is checked after full chain rebuild to ensure we pack the latest canonical state.
        pass

    # Full chain from start of active TZ scope.
    tasks.append(
        (
            "full_chain_table_canon",
            [
                sys.executable,
                "-m",
                "mlbotnav.table_canon_pack",
                "--symbol",
                symbol,
                "--timeframe",
                timeframe,
                "--start-date",
                start_date,
                "--end-date",
                end_date,
                "--horizon-bars",
                str(horizon_bars),
                "--layer",
                layer,
                "--output-mode",
                "stable",
            ],
        )
    )
    tasks.append(
        (
            "full_chain_execution_trace",
            [sys.executable, "-m", "mlbotnav.execution_trace_pack"] + (["--oos-report", str(args.oos_report)] if args.oos_report else []),
        )
    )
    tasks.append(
        (
            "full_chain_audit",
            [sys.executable, "-m", "mlbotnav.audit_table_chain", "--run-dir", "reports/table_canon_current"],
        )
    )
    tasks.append(
        (
            "full_chain_features_block_audit",
            [sys.executable, "-m", "mlbotnav.features_block_audit"],
        )
    )

    results: list[dict[str, Any]] = []
    failed = False
    packed_run_dir: str | None = None
    for name, cmd in tasks:
        r = _run(project_root, cmd)
        r["task"] = name
        results.append(r)
        parsed = r.get("parsed_json")
        if name == "step_check_run_artifact_pack" and isinstance(parsed, dict) and parsed.get("run_dir"):
            packed_run_dir = str(parsed.get("run_dir"))
        if int(r.get("returncode", 1)) != 0:
            failed = True
            break

    if (not failed) and str(step).upper() == "P4":
        pack_cmd = [sys.executable, "-m", "mlbotnav.run_artifact_pack", "--source-run-dir", "reports/table_canon_current"]
        if args.oos_report:
            pack_cmd += ["--oos-report", str(args.oos_report)]
        r = _run(project_root, pack_cmd)
        r["task"] = "step_check_run_artifact_pack"
        results.append(r)
        parsed = r.get("parsed_json")
        if isinstance(parsed, dict) and parsed.get("run_dir"):
            packed_run_dir = str(parsed.get("run_dir"))
        if int(r.get("returncode", 1)) != 0:
            failed = True

    if (not failed) and str(step).upper() == "P4":
        p4_audit_cmd = [
            sys.executable,
            "-m",
            "mlbotnav.audit_run_artifacts",
            "--run-dir",
            packed_run_dir or "reports/runs",
        ]
        r = _run(project_root, p4_audit_cmd)
        r["task"] = "step_check_run_artifact_audit"
        results.append(r)
        if int(r.get("returncode", 1)) != 0:
            failed = True

    payload = {
        "run_utc": ts,
        "status": "FAIL" if failed else "PASS",
        "step": step,
        "params": {
            "symbol": symbol,
            "timeframe": timeframe,
            "start_date": start_date,
            "end_date": end_date,
            "horizon_bars": horizon_bars,
            "layer": layer,
            "oos_report": args.oos_report,
        },
        "tasks": results,
    }
    report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "report_path": str(report_path)}, ensure_ascii=False))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
