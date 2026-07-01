from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest(root: Path, glob_pat: str) -> Path | None:
    files = sorted(root.glob(glob_pat), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def _check(name: str, ok: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": details or {}}


def main() -> int:
    parser = argparse.ArgumentParser(description="P5 acceptance audit")
    parser.add_argument("--expect-step", default="P4")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    qa_root = project_root / "reports" / "qa_gate"
    qa_root.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    latest_gate = _latest(qa_root, "tz_gate_*.json")
    checks.append(_check("latest_tz_gate_exists", latest_gate is not None, {"path": str(latest_gate) if latest_gate else None}))

    gate_obj: dict[str, Any] = {}
    if latest_gate and latest_gate.exists():
        gate_obj = _load_json(latest_gate)
        checks.append(_check("latest_tz_gate_status_pass", str(gate_obj.get("status", "")).upper() == "PASS", {"status": gate_obj.get("status")}))
        checks.append(_check("latest_tz_gate_step_match", str(gate_obj.get("step", "")).upper() == str(args.expect_step).upper(), {"step": gate_obj.get("step"), "expected": args.expect_step}))
    else:
        checks.append(_check("latest_tz_gate_status_pass", False, {"reason": "missing gate report"}))
        checks.append(_check("latest_tz_gate_step_match", False, {"reason": "missing gate report"}))

    table_audit = project_root / "reports" / "table_canon_current" / "audit_chain_report.json"
    checks.append(_check("table_chain_audit_exists", table_audit.exists(), {"path": str(table_audit)}))
    if table_audit.exists():
        obj = _load_json(table_audit)
        checks.append(_check("table_chain_audit_pass", str(obj.get("status", "")).upper() == "PASS", {"status": obj.get("status")}))
    else:
        checks.append(_check("table_chain_audit_pass", False, {"reason": "missing audit_chain_report"}))

    run_dir = None
    for t in gate_obj.get("tasks", []) if isinstance(gate_obj, dict) else []:
        if str(t.get("task", "")) == "step_check_run_artifact_pack":
            parsed = t.get("parsed_json") or {}
            run_dir = parsed.get("run_dir")
            break
    run_dir_path = Path(str(run_dir)) if run_dir else None
    checks.append(_check("p4_run_dir_detected", run_dir_path is not None and run_dir_path.exists(), {"run_dir": str(run_dir_path) if run_dir_path else None}))

    p4_audit_path = (run_dir_path / "state" / "p4_audit_report.json") if run_dir_path else None
    checks.append(_check("p4_audit_exists", p4_audit_path is not None and p4_audit_path.exists(), {"path": str(p4_audit_path) if p4_audit_path else None}))
    if p4_audit_path and p4_audit_path.exists():
        obj = _load_json(p4_audit_path)
        checks.append(_check("p4_audit_pass", str(obj.get("status", "")).upper() == "PASS", {"status": obj.get("status")}))
    else:
        checks.append(_check("p4_audit_pass", False, {"reason": "missing p4 audit"}))

    failed = int(sum(1 for c in checks if not c["ok"]))
    payload = {
        "status": "PASS" if failed == 0 else "FAIL",
        "generated_at_utc": _utc_now_iso(),
        "expected_step": args.expect_step,
        "checks": checks,
        "summary": {"total": len(checks), "failed": failed},
    }
    out = qa_root / f"p5_acceptance_{_utc_tag()}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "report_path": str(out), "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
