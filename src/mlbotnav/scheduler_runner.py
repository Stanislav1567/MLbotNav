from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


def _run(project_root: Path, cmd: list[str], *, timeout_sec: int) -> dict:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    t0 = time.time()
    p = subprocess.run(cmd, cwd=project_root, env=env, capture_output=True, text=True, timeout=timeout_sec)
    elapsed = time.time() - t0
    return {
        "cmd": cmd,
        "rc": int(p.returncode),
        "elapsed_sec": round(elapsed, 3),
        "stdout_tail": (p.stdout or "")[-1200:],
        "stderr_tail": (p.stderr or "")[-1200:],
    }


def _day_bounds_utc() -> tuple[str, str]:
    end = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    start = (datetime.strptime(end, "%Y-%m-%d").date() - timedelta(days=29)).strftime("%Y-%m-%d")
    return start, end


def main() -> int:
    parser = argparse.ArgumentParser(description="Simple scheduler runner for ingestion/prod/drift-trigger loops.")
    parser.add_argument("--task", default="all", choices=["ingest_incremental", "prod_cycle", "drift_trigger", "all"])
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--interval-sec", type=int, default=60)
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--timeout-sec", type=int, default=1800)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    tasks: list[str]
    if args.task == "all":
        tasks = ["ingest_incremental", "prod_cycle", "drift_trigger"]
    else:
        tasks = [args.task]

    runs: list[dict] = []
    for i in range(max(1, int(args.iterations))):
        batch: list[dict] = []
        start_date, end_date = _day_bounds_utc()
        if "ingest_incremental" in tasks:
            batch.append(
                _run(
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
                    timeout_sec=int(args.timeout_sec),
                )
            )
        if "prod_cycle" in tasks:
            batch.append(
                _run(
                    project_root,
                    [
                        sys.executable,
                        "-m",
                        "mlbotnav.prod_cycle",
                        "--symbol",
                        args.symbol,
                        "--timeframe",
                        args.timeframe,
                        "--start-date",
                        start_date,
                        "--end-date",
                        end_date,
                    ],
                    timeout_sec=int(args.timeout_sec),
                )
            )
        if "drift_trigger" in tasks:
            batch.append(
                _run(
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
                        "120",
                    ],
                    timeout_sec=int(args.timeout_sec),
                )
            )
        runs.append(
            {
                "iteration": i + 1,
                "started_at_utc": datetime.now(timezone.utc).isoformat(),
                "tasks": batch,
            }
        )
        if i + 1 < int(args.iterations):
            time.sleep(max(1, int(args.interval_sec)))

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = project_root / "reports" / "automation"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"scheduler_run_{args.symbol}_{args.timeframe}_{ts}.json"
    out = {
        "run_utc": ts,
        "task": args.task,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "interval_sec": int(args.interval_sec),
        "iterations": int(args.iterations),
        "runs": runs,
    }
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report_path": str(out_path), "iterations": int(args.iterations)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
