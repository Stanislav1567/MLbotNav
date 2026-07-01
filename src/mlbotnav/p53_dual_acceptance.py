from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest(glob_pat: str, root: Path) -> Path | None:
    files = sorted(root.glob(glob_pat), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def _check(name: str, ok: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": details or {}}


def _extract_step_report(step: dict[str, Any]) -> str | None:
    parsed = step.get("parsed_json")
    if isinstance(parsed, dict):
        rp = str(parsed.get("report_path", "") or "").strip()
        return rp or None
    return None


def _extract_summary_path(cycle_payload: dict[str, Any], mode: str) -> str | None:
    for st in cycle_payload.get("steps", []) or []:
        if not isinstance(st, dict):
            continue
        if str(st.get("task", "")).strip() == f"adaptive_auto_train_{mode}":
            parsed = st.get("parsed_json")
            if isinstance(parsed, dict):
                sp = str(parsed.get("summary_path", "") or "").strip()
                return sp or None
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="P5.3 dual acceptance audit: validate latest long+short contour cycles together.")
    parser.add_argument("--long-report", default="", help="Optional explicit contour_cycle_long_only report.")
    parser.add_argument("--short-report", default="", help="Optional explicit contour_cycle_short_only report.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    qa = root / "reports" / "qa_gate"
    qa.mkdir(parents=True, exist_ok=True)
    out = qa / f"p53_dual_acceptance_{_utc_tag()}.json"

    long_path = Path(args.long_report) if str(args.long_report).strip() else _latest("contour_cycle_long_only_*.json", qa)
    short_path = Path(args.short_report) if str(args.short_report).strip() else _latest("contour_cycle_short_only_*.json", qa)
    if long_path is not None and not long_path.is_absolute():
        long_path = (qa / long_path.name).resolve() if not long_path.exists() else long_path.resolve()
    if short_path is not None and not short_path.is_absolute():
        short_path = (qa / short_path.name).resolve() if not short_path.exists() else short_path.resolve()

    checks: list[dict[str, Any]] = []
    checks.append(_check("long_cycle_exists", long_path is not None and long_path.exists(), {"path": str(long_path) if long_path else None}))
    checks.append(_check("short_cycle_exists", short_path is not None and short_path.exists(), {"path": str(short_path) if short_path else None}))

    if not (long_path and long_path.exists() and short_path and short_path.exists()):
        payload = {
            "status": "FAIL",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "checks": checks,
            "summary": {"total": len(checks), "failed": int(sum(1 for c in checks if not c["ok"]))},
        }
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": "FAIL", "report_path": str(out)}, ensure_ascii=False))
        return 1

    long_obj = _load_json(long_path)
    short_obj = _load_json(short_path)

    checks.append(_check("long_cycle_status_pass", str(long_obj.get("status", "")).upper() == "PASS"))
    checks.append(_check("short_cycle_status_pass", str(short_obj.get("status", "")).upper() == "PASS"))

    lp = long_obj.get("params", {}) if isinstance(long_obj.get("params"), dict) else {}
    sp = short_obj.get("params", {}) if isinstance(short_obj.get("params"), dict) else {}
    for k in ["symbol", "timeframe", "train_start", "train_end", "test_day", "test_end_day", "repeats"]:
        checks.append(_check(f"params_{k}_match", str(lp.get(k)) == str(sp.get(k)), {"long": lp.get(k), "short": sp.get(k)}))

    # Ensure 5+ report PASS exists in each cycle.
    def _mode_checks(obj: dict[str, Any], mode: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        local: list[dict[str, Any]] = []
        steps = obj.get("steps", []) if isinstance(obj.get("steps"), list) else []
        conv = None
        hypo = None
        for st in steps:
            if not isinstance(st, dict):
                continue
            if str(st.get("task", "")) == "table_convergence_5plus":
                conv = st
            if str(st.get("task", "")) == "hypothesis_coverage_audit":
                hypo = st
        local.append(_check(f"{mode}_has_table_convergence_step", conv is not None))
        local.append(_check(f"{mode}_has_hypothesis_step", hypo is not None))
        conv_report = None
        if conv is not None:
            conv_report = _extract_step_report(conv)
            local.append(_check(f"{mode}_table_convergence_step_rc0", int(conv.get("returncode", 1)) == 0))
            if conv_report:
                p = Path(conv_report)
                if not p.is_absolute():
                    p = (root / p).resolve()
                if p.exists():
                    conv_obj = _load_json(p)
                    local.append(_check(f"{mode}_table_convergence_report_pass", str(conv_obj.get("status", "")).upper() == "PASS", {"report": str(p)}))
                else:
                    local.append(_check(f"{mode}_table_convergence_report_exists", False, {"report": str(p)}))
            else:
                local.append(_check(f"{mode}_table_convergence_report_path_present", False))
        if hypo is not None:
            local.append(_check(f"{mode}_hypothesis_step_rc0", int(hypo.get("returncode", 1)) == 0))
        return local, {"conv_report": conv_report}

    c1, m1 = _mode_checks(long_obj, "long")
    c2, m2 = _mode_checks(short_obj, "short")
    checks.extend(c1)
    checks.extend(c2)

    # Check final gate PASS (latest available).
    latest_gate = _latest("tz_gate_*.json", qa)
    if latest_gate and latest_gate.exists():
        gobj = _load_json(latest_gate)
        checks.append(_check("latest_gate_pass", str(gobj.get("status", "")).upper() == "PASS", {"report": str(latest_gate)}))
    else:
        checks.append(_check("latest_gate_exists", False))

    failed = int(sum(1 for c in checks if not c["ok"]))
    payload = {
        "status": "PASS" if failed == 0 else "FAIL",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "long_report": str(long_path),
        "short_report": str(short_path),
        "meta": {"long": m1, "short": m2},
        "checks": checks,
        "summary": {"total": len(checks), "failed": failed},
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "report_path": str(out), "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
