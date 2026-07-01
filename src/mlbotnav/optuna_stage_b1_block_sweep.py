from __future__ import annotations

import argparse
import itertools
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_matrix(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _write_matrix(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _matrix_for_active_blocks(base: dict[str, Any], active_blocks: list[str]) -> dict[str, Any]:
    out = dict(base)
    optuna_switches = dict(out.get("optuna_switches") or {})
    block_switches = dict(optuna_switches.get("block_switches") or {})
    active_set = {str(x).strip() for x in list(active_blocks or []) if str(x).strip()}
    for k in list(block_switches.keys()):
        block_switches[k] = bool(k in active_set)
    optuna_switches["block_switches"] = block_switches
    out["optuna_switches"] = optuna_switches
    return out


def _extract_final_fields(stdout: str) -> dict[str, Any]:
    text = str(stdout or "")
    result_status = None
    oos = None
    trades = None
    summary_path = None

    m = re.findall(r'"result_status"\s*:\s*"([^"]+)"', text)
    if m:
        result_status = m[-1]
    m = re.findall(r'"oos_net_return_pct"\s*:\s*"([^"]+)"', text)
    if m:
        try:
            oos = float(m[-1])
        except Exception:
            oos = None
    m = re.findall(r'"oos_trades"\s*:\s*([0-9]+)', text)
    if m:
        trades = int(m[-1])
    m = re.findall(r'"summary_path"\s*:\s*"([^"]+)"', text)
    if m:
        summary_path = m[-1].replace("\\\\", "\\")

    return {
        "result_status": result_status,
        "oos_net_return_pct": oos,
        "oos_trades": trades,
        "summary_path": summary_path,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage block-combo Optuna sweep (B1/B2/B3)")
    parser.add_argument("--mode", default="short_only", choices=["short_only", "long_only"])
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--train-date", default="2026-05-19")
    parser.add_argument("--test-date", default="2026-05-20")
    parser.add_argument("--threads", type=int, default=9)
    parser.add_argument("--search-workers", type=int, default=9)
    parser.add_argument("--optuna-trials", type=int, default=40)
    parser.add_argument("--optuna-timeout-sec", type=int, default=120)
    parser.add_argument("--optuna-stage", default="C", choices=["A", "B", "C", "auto"])
    parser.add_argument("--wait-for-runtime-lock-sec", type=int, default=30)
    parser.add_argument("--combo-size", type=int, default=1)
    parser.add_argument("--max-runs", type=int, default=0)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    matrix_path = (project_root / "configs" / "calibration_full_matrix_v1.yaml").resolve()
    aptuna_runner = (project_root / "APTuna" / "run_optuna_1d1d_stagec.ps1").resolve()
    if not matrix_path.exists():
        raise FileNotFoundError(f"Matrix not found: {matrix_path}")
    if not aptuna_runner.exists():
        raise FileNotFoundError(f"Runner not found: {aptuna_runner}")

    base_matrix = _load_matrix(matrix_path)
    block_switches = dict((base_matrix.get("optuna_switches") or {}).get("block_switches") or {})
    blocks = [str(k) for k, v in block_switches.items() if bool(v)]
    if not blocks:
        raise RuntimeError("No enabled blocks found in calibration matrix")
    combo_size = int(args.combo_size)
    if combo_size < 1:
        raise ValueError("--combo-size must be >= 1")
    if combo_size > len(blocks):
        raise ValueError(f"--combo-size={combo_size} exceeds enabled blocks count={len(blocks)}")
    combos = list(itertools.combinations(blocks, combo_size))
    if int(args.max_runs) > 0:
        combos = combos[: int(args.max_runs)]

    run_utc = _utc_stamp()
    sweep_tag = f"b{combo_size}"
    tmp_dir = (project_root / "tmp" / f"optuna_{sweep_tag}").resolve()
    log_dir = (project_root / "reports" / "logs").resolve()
    log_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []

    for idx, combo in enumerate(combos, start=1):
        active_blocks = [str(x) for x in combo]
        combo_label = "__".join(active_blocks)
        matrix_block = _matrix_for_active_blocks(base_matrix, active_blocks)
        matrix_block_path = tmp_dir / f"calibration_{sweep_tag}_{args.mode}_{run_utc}_{idx:03d}_{combo_label}.yaml"
        _write_matrix(matrix_block_path, matrix_block)

        cmd = [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(aptuna_runner),
            "-Mode",
            str(args.mode),
            "-Symbol",
            str(args.symbol),
            "-Timeframe",
            str(args.timeframe),
            "-TrainDate",
            str(args.train_date),
            "-TestDate",
            str(args.test_date),
            "-Threads",
            str(int(args.threads)),
            "-SearchWorkers",
            str(int(args.search_workers)),
            "-OptunaTrials",
            str(int(args.optuna_trials)),
            "-OptunaTimeoutSec",
            str(int(args.optuna_timeout_sec)),
            "-OptunaStage",
            str(args.optuna_stage),
            "-OptunaMlSignalBackend",
            "off",
            "-CalibrationMatrixPath",
            str(matrix_block_path),
            "-UseTemporaryUnlock",
            "-WaitForRuntimeLockSec",
            str(int(args.wait_for_runtime_lock_sec)),
        ]

        proc = subprocess.run(
            cmd,
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        out_text = str(proc.stdout or "")
        err_text = str(proc.stderr or "")
        parsed = _extract_final_fields(out_text)

        log_out = log_dir / f"optuna_{sweep_tag}_{args.mode}_{run_utc}_{idx:03d}_{combo_label}.log"
        log_err = log_dir / f"optuna_{sweep_tag}_{args.mode}_{run_utc}_{idx:03d}_{combo_label}.err.log"
        log_out.write_text(out_text, encoding="utf-8")
        log_err.write_text(err_text, encoding="utf-8")

        results.append(
            {
                "active_blocks": active_blocks,
                "combo_label": combo_label,
                "exit_code": int(proc.returncode),
                "matrix_path": str(matrix_block_path),
                "stdout_log": str(log_out),
                "stderr_log": str(log_err),
                **parsed,
            }
        )

    best = None
    ok = [r for r in results if r.get("exit_code") == 0 and r.get("oos_net_return_pct") is not None]
    if ok:
        best = sorted(ok, key=lambda x: float(x.get("oos_net_return_pct", -10**9)), reverse=True)[0]

    report = {
        "status": "OK",
        "run_utc": run_utc,
        "sweep_tag": sweep_tag,
        "combo_size": combo_size,
        "mode": str(args.mode),
        "symbol": str(args.symbol),
        "timeframe": str(args.timeframe),
        "train_date": str(args.train_date),
        "test_date": str(args.test_date),
        "blocks_total": len(blocks),
        "combos_total": len(combos),
        "optuna_trials": int(args.optuna_trials),
        "optuna_timeout_sec": int(args.optuna_timeout_sec),
        "results": results,
        "best_combo": best,
    }
    out_dir = (project_root / "reports" / "qa_gate").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"optuna_{sweep_tag}_block_sweep_{args.mode}_{run_utc}.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "OK", "report_path": str(out_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
