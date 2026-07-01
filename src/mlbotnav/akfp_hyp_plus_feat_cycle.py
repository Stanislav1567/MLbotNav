from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _extract_json(stdout: str) -> dict[str, Any] | None:
    txt = (stdout or "").strip()
    if not txt:
        return None
    try:
        obj = json.loads(txt)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    for line in reversed([x.strip() for x in txt.splitlines() if x.strip()]):
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                return obj
        except Exception:
            continue
    return None


def _run(cmd: list[str], cwd: Path) -> dict[str, Any]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    parsed = _extract_json(p.stdout or "")
    return {
        "returncode": int(p.returncode),
        "cmd": cmd,
        "stdout_tail": (p.stdout or "")[-4000:],
        "stderr_tail": (p.stderr or "")[-4000:],
        "parsed_json": parsed,
    }


def _side_run(
    *,
    project_root: Path,
    python_exe: str,
    symbol: str,
    timeframe: str,
    train_date: str,
    test_date: str,
    repeats: int,
    threads: int,
    search_workers: int,
    cpu_max_pct: float,
    side_mode: str,
) -> dict[str, Any]:
    contour = "long_only" if side_mode == "long_only" else "short_only"
    cmd = [
        python_exe,
        "-m",
        "mlbotnav.adaptive_auto_train",
        "--symbol",
        symbol,
        "--timeframe",
        timeframe,
        "--train-start",
        train_date,
        "--train-end",
        train_date,
        "--test-day",
        test_date,
        "--test-end-day",
        test_date,
        "--signal-mode",
        contour,
        "--use-hypothesis-profile",
        "--contour-id",
        contour,
        "--repeats",
        str(int(repeats)),
        "--goal-net-return-pct",
        "1",
        "--allow-subgoal-candidates",
        "--min-train-rows",
        "900",
        "--n-folds",
        "2",
        "--horizons-grid",
        "5,8,12,20,30,45,60,90",
        "--min-expected-move-grid",
        "0.001,0.0015,0.002,0.003,0.004,0.005",
        "--execution-mode",
        "exchange_like",
        "--order-type",
        "market",
        "--notional-usd",
        "10",
        "--leverage",
        "10",
        "--cpu-max-pct",
        str(float(cpu_max_pct)),
        "--max-threads",
        str(int(threads)),
        "--search-workers",
        str(int(search_workers)),
        "--speed-profile",
        "turbo",
        "--temporary-unlock-readiness",
        "--unlock-reason",
        f"AKFP P6 HYP_PLUS_FEAT {contour}",
    ]
    run = _run(cmd, project_root)

    cov_cmd = [
        python_exe,
        "-m",
        "mlbotnav.hypothesis_coverage_audit",
        "--contour-id",
        contour,
        "--min-coverage-ratio",
        "0.08",
        "--min-covered-count",
        "1",
    ]
    cov = _run(cov_cmd, project_root)
    return {"contour_id": contour, "adaptive_run": run, "coverage_audit": cov}


def main() -> int:
    parser = argparse.ArgumentParser(description="AKFP P6: HYP_PLUS_FEAT cycle (long/short separately).")
    parser.add_argument("--policy", default="configs/akfp_policy.yaml")
    parser.add_argument("--output-dir", default="reports/akfp/hyp_plus_feat")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    policy_path = Path(args.policy)
    if not policy_path.is_absolute():
        policy_path = (project_root / policy_path).resolve()
    cfg = _load_yaml(policy_path)
    akfp = dict(cfg.get("akfp") or {})
    exe = dict(akfp.get("execution") or {})

    symbol = str(exe.get("symbol", "SOLUSDT"))
    timeframe = str(exe.get("timeframe", "1m"))
    train_date = str(exe.get("train_date", "2026-05-19"))
    test_date = str(exe.get("test_date", "2026-05-20"))
    repeats = max(2, int(exe.get("repeats", 2)))
    threads = int(exe.get("threads", 8))
    search_workers = int(exe.get("search_workers", 8))
    cpu_max_pct = float(exe.get("cpu_max_pct", 85))

    python_exe = str((project_root / ".venv" / "Scripts" / "python.exe").resolve())
    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = (project_root / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    long_part = _side_run(
        project_root=project_root,
        python_exe=python_exe,
        symbol=symbol,
        timeframe=timeframe,
        train_date=train_date,
        test_date=test_date,
        repeats=repeats,
        threads=threads,
        search_workers=search_workers,
        cpu_max_pct=cpu_max_pct,
        side_mode="long_only",
    )
    short_part = _side_run(
        project_root=project_root,
        python_exe=python_exe,
        symbol=symbol,
        timeframe=timeframe,
        train_date=train_date,
        test_date=test_date,
        repeats=repeats,
        threads=threads,
        search_workers=search_workers,
        cpu_max_pct=cpu_max_pct,
        side_mode="short_only",
    )

    checks = []
    for part in [long_part, short_part]:
        contour = part["contour_id"]
        ad = part["adaptive_run"]
        cv = part["coverage_audit"]
        checks.append(
            {
                "name": f"{contour}_adaptive_rc_zero",
                "ok": int(ad.get("returncode", 1)) == 0,
                "details": {"returncode": ad.get("returncode"), "summary": (ad.get("parsed_json") or {}).get("summary_path")},
            }
        )
        checks.append(
            {
                "name": f"{contour}_coverage_rc_zero",
                "ok": int(cv.get("returncode", 1)) == 0,
                "details": {"returncode": cv.get("returncode"), "report": (cv.get("parsed_json") or {}).get("report_path")},
            }
        )

    failed = sum(1 for c in checks if not bool(c["ok"]))
    status = "PASS" if failed == 0 else "FAIL"

    payload = {
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol,
        "timeframe": timeframe,
        "train_date": train_date,
        "test_date": test_date,
        "repeats": repeats,
        "checks": checks,
        "results": {
            "long_only": long_part,
            "short_only": short_part,
        },
        "summary": {"total": len(checks), "failed": int(failed)},
    }
    out = out_dir / f"akfp_hyp_plus_feat_cycle_{symbol}_{timeframe}_{test_date}_{_utc_tag()}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": status, "report_path": str(out)}, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
