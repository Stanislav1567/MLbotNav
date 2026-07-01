from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

REQUIRED_CANDIDATE_TYPES = [
    "STRAT_BASELINE",
    "HYP_ONLY",
    "FEAT_ONLY",
    "HYP_PLUS_FEAT",
    "COMBO_WORKING",
]


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _mode_to_runner_mode(signal_mode: str) -> str:
    sm = str(signal_mode).strip().lower()
    if sm == "long_only":
        return "long"
    if sm == "short_only":
        return "short"
    return "combined"


def _parse_ymd(value: str) -> date:
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def _resolve_profile_windows(akfp: dict[str, Any], execution: dict[str, Any]) -> dict[str, Any]:
    """
    Resolve train/test windows from policy calibration profile.
    Anchor is execution.test_date (treated as test_end day).
    """
    cw = dict(akfp.get("calibration_windows") or {})
    profiles = dict(cw.get("profiles") or {})
    active_profile = str(cw.get("active_profile", "") or "").strip()
    prof = dict(profiles.get(active_profile) or {})

    # Explicit overrides win if provided.
    train_start_raw = str(execution.get("train_start_date", "") or "").strip()
    train_end_raw = str(execution.get("train_end_date", "") or "").strip()
    test_start_raw = str(execution.get("test_start_date", "") or "").strip()
    test_end_raw = str(execution.get("test_end_date", "") or "").strip()
    anchor_test_end_raw = str(execution.get("test_date", "2026-05-20"))

    if train_start_raw and train_end_raw and test_start_raw and test_end_raw:
        return {
            "active_profile": active_profile or "manual_override",
            "train_start": train_start_raw,
            "train_end": train_end_raw,
            "test_start": test_start_raw,
            "test_end": test_end_raw,
            "train_days": ( _parse_ymd(train_end_raw) - _parse_ymd(train_start_raw) ).days + 1,
            "test_days": ( _parse_ymd(test_end_raw) - _parse_ymd(test_start_raw) ).days + 1,
            "source": "manual_override",
        }

    train_days = int(prof.get("train_days", 1) or 1)
    test_days = int(prof.get("test_days", 1) or 1)
    repeats = int(prof.get("repeats", 1) or 1)
    test_end = _parse_ymd(anchor_test_end_raw)
    test_start = test_end - timedelta(days=max(1, test_days) - 1)
    train_end = test_start - timedelta(days=1)
    train_start = train_end - timedelta(days=max(1, train_days) - 1)
    return {
        "active_profile": active_profile or "default_1d1d",
        "train_start": train_start.isoformat(),
        "train_end": train_end.isoformat(),
        "test_start": test_start.isoformat(),
        "test_end": test_end.isoformat(),
        "train_days": train_days,
        "test_days": test_days,
        "repeats": repeats,
        "source": "profile",
    }

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
    lines = [x.strip() for x in txt.splitlines() if x.strip()]
    for line in reversed(lines):
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                return obj
        except Exception:
            continue
    return None


def _extract_p23_report_path(stdout: str) -> str | None:
    txt = str(stdout or "")
    if not txt.strip():
        return None
    # Prefer explicit p23 summary report path from stdout/log text.
    m = re.findall(r"([A-Za-z]:\\[^\r\n]*p23_operator_unified_[^\\\r\n]*\.json)", txt)
    if m:
        return str(m[-1]).strip()
    return None


def _run(cmd: list[str], cwd: Path, execute: bool) -> dict[str, Any]:
    if not execute:
        return {"status": "DRY_RUN", "cmd": cmd, "returncode": 0}
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    parsed = _extract_json(p.stdout or "")
    return {
        "status": "PASS" if p.returncode == 0 else "FAIL",
        "cmd": cmd,
        "returncode": int(p.returncode),
        "stdout_tail": (p.stdout or "")[-4000:],
        "stderr_tail": (p.stderr or "")[-4000:],
        "parsed_json": parsed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="AKFP bridge orchestrator (toggle-enabled sidecar).")
    parser.add_argument("--policy", default="configs/akfp_policy.yaml")
    parser.add_argument("--execute", action="store_true", help="Actually run bridge commands. Default is dry-run.")
    parser.add_argument("--step-label", default="AKFP")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    policy_path = Path(args.policy)
    if not policy_path.is_absolute():
        policy_path = (project_root / policy_path).resolve()

    cfg = _load_yaml(policy_path)
    akfp = dict(cfg.get("akfp") or {})
    enabled = bool(akfp.get("enabled", False))
    mode = str(akfp.get("mode", "shadow")).strip().lower()
    calibration = dict(akfp.get("calibration") or {})
    candidate_types = [str(x).strip() for x in (calibration.get("candidate_types") or []) if str(x).strip()]
    missing_candidate_types = [x for x in REQUIRED_CANDIDATE_TYPES if x not in candidate_types]
    candidate_types_contract_ok = len(missing_candidate_types) == 0

    qa_dir = (project_root / "reports" / "qa_gate").resolve()
    qa_dir.mkdir(parents=True, exist_ok=True)

    if not enabled:
        payload = {
            "status": "SKIPPED",
            "reason": "akfp.enabled=false",
            "mode": mode,
            "policy_path": str(policy_path),
            "candidate_types_contract_ok": candidate_types_contract_ok,
            "candidate_types": candidate_types,
            "required_candidate_types": REQUIRED_CANDIDATE_TYPES,
            "missing_candidate_types": missing_candidate_types,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        out = qa_dir / f"akfp_bridge_{_utc_tag()}.json"
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": "SKIPPED", "report_path": str(out)}, ensure_ascii=False))
        return 0

    bridges = dict(akfp.get("bridges") or {})
    execution = dict(akfp.get("execution") or {})
    contours = dict(akfp.get("contours") or {})
    calibration = dict(akfp.get("calibration") or {})
    modes = list(contours.get("enabled_modes") or ["long_only", "short_only", "combined"])

    core_runner = str(bridges.get("core_runner", "run_p23_operator_unified.ps1"))
    latest_pass_runner = str(bridges.get("latest_pass_runner", "run_p24_latest_pass_report.ps1"))
    shortlist_agent_enabled = bool(calibration.get("shortlist_agent_enabled", True))
    symbol = str(execution.get("symbol", "SOLUSDT"))
    timeframe = str(execution.get("timeframe", "1m"))
    windows = _resolve_profile_windows(akfp, execution)
    train_date = str(windows.get("train_start", "2026-05-19"))
    train_end_date = str(windows.get("train_end", train_date))
    test_date = str(windows.get("test_start", "2026-05-20"))
    test_end_date = str(windows.get("test_end", test_date))
    repeats = int(execution.get("repeats", int(windows.get("repeats", 1) or 1)))
    threads = int(execution.get("threads", 8))
    search_workers = int(execution.get("search_workers", 8))
    freeze_check_mode = str(execution.get("freeze_check_mode", "release"))
    prefix = str(execution.get("step_label_prefix", "AKFP"))

    steps: list[dict[str, Any]] = []
    overall_fail = False

    if shortlist_agent_enabled:
        shortlist_cmd = [str((project_root / ".venv" / "Scripts" / "python.exe").resolve()), "-m", "mlbotnav.akfp_shortlist_agent"]
        s = _run(shortlist_cmd, project_root, execute=bool(args.execute))
        s["task"] = "akfp_shortlist_agent"
        steps.append(s)
        if s["status"] == "FAIL":
            overall_fail = True

    last_p23_report_path: str | None = None
    for idx, sm in enumerate(modes, start=1):
        run_mode = _mode_to_runner_mode(sm)
        step_label = f"{prefix}-{args.step_label}-{idx}"
        cmd = [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            f".\\{core_runner}",
            "-Mode",
            run_mode,
            "-Symbol",
            symbol,
            "-Timeframe",
            timeframe,
            "-TrainDate",
            train_date,
            "-TrainEndDate",
            train_end_date,
            "-TestDate",
            test_date,
            "-TestEndDate",
            test_end_date,
            "-Repeats",
            str(repeats),
            "-Threads",
            str(threads),
            "-SearchWorkers",
            str(search_workers),
            "-StepLabel",
            step_label,
            "-FreezeCheckMode",
            freeze_check_mode,
        ]
        r = _run(cmd, project_root, execute=bool(args.execute))
        r["signal_mode"] = sm
        r["runner_mode"] = run_mode
        r["step_label"] = step_label
        steps.append(r)
        rp = ""
        if isinstance(r.get("parsed_json"), dict):
            rp = str((r.get("parsed_json") or {}).get("report_path", "")).strip()
        if ("p23_operator_unified_" not in rp) or (not rp):
            rp2 = _extract_p23_report_path(str(r.get("stdout_tail", "") or ""))
            if rp2:
                rp = rp2
        if rp and ("p23_operator_unified_" in rp):
            last_p23_report_path = rp
        if r["status"] == "FAIL":
            overall_fail = True

    lp_cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", f".\\{latest_pass_runner}"]
    if last_p23_report_path:
        lp_cmd.extend(["-SourceP23ReportPath", last_p23_report_path])
    lp = _run(lp_cmd, project_root, execute=bool(args.execute))
    steps.append(lp)
    if lp["status"] == "FAIL":
        overall_fail = True

    status = "FAIL" if overall_fail else ("PASS" if args.execute else "DRY_RUN")
    payload = {
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "policy_path": str(policy_path),
        "execute": bool(args.execute),
        "mode": mode,
        "windows": windows,
        "candidate_types_contract_ok": candidate_types_contract_ok,
        "candidate_types": candidate_types,
        "required_candidate_types": REQUIRED_CANDIDATE_TYPES,
        "missing_candidate_types": missing_candidate_types,
        "steps": steps,
    }
    out = qa_dir / f"akfp_bridge_{_utc_tag()}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": status, "report_path": str(out)}, ensure_ascii=False))
    return 0 if status in {"PASS", "DRY_RUN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
