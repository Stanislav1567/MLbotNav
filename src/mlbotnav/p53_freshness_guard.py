from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_tag() -> str:
    return _utc_now().strftime("%Y%m%dT%H%M%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest(root: Path, pattern: str) -> Path | None:
    files = sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def _check(name: str, ok: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": details or {}}


def _status_pass(path: Path | None) -> tuple[bool, dict[str, Any]]:
    if not path or not path.exists():
        return False, {"path": str(path) if path else None, "reason": "missing"}
    try:
        obj = _load_json(path)
        ok = str(obj.get("status", "")).upper() == "PASS"
        return ok, {"path": str(path), "status": obj.get("status")}
    except Exception as e:
        return False, {"path": str(path), "reason": f"parse_error:{e}"}


def _is_fresh(path: Path, *, max_age_minutes: int) -> tuple[bool, dict[str, Any]]:
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    age = _utc_now() - mtime
    ok = age <= timedelta(minutes=max_age_minutes)
    return ok, {"path": str(path), "mtime_utc": mtime.isoformat(), "age_sec": int(age.total_seconds()), "max_age_minutes": int(max_age_minutes)}


def main() -> int:
    parser = argparse.ArgumentParser(description="P5.3 freshness guard for release artifacts.")
    parser.add_argument("--qa-dir", default="reports/qa_gate")
    parser.add_argument("--table-chain-report", default="reports/table_canon_current/audit_chain_report.json")
    parser.add_argument("--max-age-minutes", type=int, default=20)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    qa_dir = (root / args.qa_dir).resolve()
    chain_report = (root / args.table_chain_report).resolve()
    qa_dir.mkdir(parents=True, exist_ok=True)
    out = qa_dir / f"p53_freshness_guard_{_utc_tag()}.json"

    latest = {
        "daily_cycle": _latest(qa_dir, "daily_long_short_cycle_*.json"),
        "dual_acceptance": _latest(qa_dir, "p53_dual_acceptance_*.json"),
        "snapshot": _latest(qa_dir, "p53_snapshot_*.json"),
        "release_bundle": _latest(qa_dir, "p53_release_bundle_*.json"),
        "gate": _latest(qa_dir, "tz_gate_*.json"),
    }

    checks: list[dict[str, Any]] = []
    for name, path in latest.items():
        ok_status, det_status = _status_pass(path)
        checks.append(_check(f"{name}_pass", ok_status, det_status))
        if path and path.exists():
            ok_fresh, det_fresh = _is_fresh(path, max_age_minutes=int(args.max_age_minutes))
            checks.append(_check(f"{name}_fresh", ok_fresh, det_fresh))
        else:
            checks.append(_check(f"{name}_fresh", False, {"path": str(path) if path else None, "reason": "missing"}))

    # Ensure table-chain report is PASS and has non-zero execution rows for 5+ quality bar.
    if chain_report.exists():
        try:
            chain = _load_json(chain_report)
            checks.append(_check("table_chain_pass", str(chain.get("status", "")).upper() == "PASS", {"path": str(chain_report)}))
            exec_rows = None
            exec_match = None
            for c in chain.get("checks", []):
                if not isinstance(c, dict):
                    continue
                if str(c.get("name")) == "execution_trace_rows_non_negative":
                    exec_rows = int((c.get("details") or {}).get("rows", -1))
                if str(c.get("name")) == "execution_trace_rows_match_summary":
                    exec_match = bool(c.get("ok", False))
            checks.append(_check("table_chain_execution_rows_positive", (exec_rows is not None and exec_rows > 0), {"rows": exec_rows}))
            checks.append(_check("table_chain_execution_match_summary", bool(exec_match), {"ok": exec_match}))
        except Exception as e:
            checks.append(_check("table_chain_parseable", False, {"path": str(chain_report), "error": str(e)}))
    else:
        checks.append(_check("table_chain_exists", False, {"path": str(chain_report)}))

    failed = int(sum(1 for c in checks if not c["ok"]))
    payload = {
        "status": "PASS" if failed == 0 else "FAIL",
        "generated_at_utc": _utc_now().isoformat(),
        "max_age_minutes": int(args.max_age_minutes),
        "checks": checks,
        "summary": {"total": len(checks), "failed": failed},
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "report_path": str(out), "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
