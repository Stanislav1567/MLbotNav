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


def _run(project_root: Path, cmd: list[str]) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    p = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, env=env)
    return {
        "cmd": cmd,
        "returncode": int(p.returncode),
        "stdout_tail": (p.stdout or "")[-4000:],
        "stderr_tail": (p.stderr or "")[-4000:],
    }


def _latest_oos_report(project_root: Path) -> Path | None:
    files = sorted(
        (project_root / "reports" / "final_review").glob("oos_report_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


def _latest_gate_report(project_root: Path) -> Path | None:
    files = sorted(
        (project_root / "reports" / "qa_gate").glob("tz_gate_*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return files[0] if files else None


def main() -> int:
    parser = argparse.ArgumentParser(description="5+ convergence audit: execution_trace_pack -> strict table-chain audit -> gate.")
    parser.add_argument("--oos-report", default="", help="Optional explicit oos_report path. If omitted, latest from reports/final_review is used.")
    parser.add_argument("--run-dir", default="reports/table_canon_current")
    parser.add_argument("--with-gate", action="store_true", help="Run tz_gate_runner --step P4 after table audit.")
    parser.add_argument(
        "--require-trades-strict",
        action="store_true",
        help="Fail convergence when no trades are present (strategy strict mode).",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    qa_dir = project_root / "reports" / "qa_gate"
    qa_dir.mkdir(parents=True, exist_ok=True)
    out_report = qa_dir / f"table_convergence_5plus_{_utc_tag()}.json"

    oos_path = Path(str(args.oos_report)) if str(args.oos_report).strip() else _latest_oos_report(project_root)
    if oos_path is None:
        payload = {
            "status": "FAIL",
            "error": "No oos_report found.",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        out_report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": "FAIL", "report_path": str(out_report), "error": payload["error"]}, ensure_ascii=False))
        return 1
    if not oos_path.is_absolute():
        oos_path = (project_root / oos_path).resolve()

    tasks: list[dict[str, Any]] = []
    failed = False

    t1 = _run(
        project_root,
        [
            sys.executable,
            "-m",
            "mlbotnav.execution_trace_pack",
            "--oos-report",
            str(oos_path),
            "--output-dir",
            f"{args.run_dir}/data",
        ],
    )
    t1["task"] = "execution_trace_pack"
    tasks.append(t1)
    if t1["returncode"] != 0:
        failed = True

    if not failed:
        t2_cmd = [sys.executable, "-m", "mlbotnav.audit_table_chain", "--run-dir", str(args.run_dir)]
        if bool(args.require_trades_strict):
            t2_cmd.append("--require-trades")
        t2 = _run(project_root, t2_cmd)
        t2["task"] = "audit_table_chain_require_trades"
        tasks.append(t2)
        if t2["returncode"] != 0:
            failed = True

    # Informational strategy signal: number of executed trades in OOS.
    oos_trades = None
    try:
        obj = json.loads(oos_path.read_text(encoding="utf-8-sig"))
        oos_trades = int(((obj.get("backtest") or {}).get("trades", 0)))
    except Exception:
        oos_trades = None
    tasks.append(
        {
            "task": "oos_trades_informational",
            "oos_trades": oos_trades,
            "note": "Informational only in technical convergence mode.",
            "strict_mode": bool(args.require_trades_strict),
        }
    )

    if (not failed) and bool(args.with_gate):
        t3 = _run(
            project_root,
            [
                sys.executable,
                "-m",
                "mlbotnav.tz_gate_runner",
                "--step",
                "P4",
                "--oos-report",
                str(oos_path),
            ],
        )
        t3["task"] = "tz_gate_runner_p4"
        tasks.append(t3)
        if t3["returncode"] != 0:
            failed = True

    payload = {
        "status": "FAIL" if failed else "PASS",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "oos_report": str(oos_path),
        "run_dir": str((project_root / args.run_dir).resolve()),
        "latest_gate_report": str(_latest_gate_report(project_root)) if _latest_gate_report(project_root) else None,
        "tasks": tasks,
    }
    out_report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "report_path": str(out_report)}, ensure_ascii=False))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
