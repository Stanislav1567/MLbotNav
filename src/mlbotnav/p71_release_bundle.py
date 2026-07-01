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


def _latest(root: Path, pattern: str) -> Path | None:
    items = sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return items[0] if items else None


def _check(name: str, ok: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": details or {}}


def _status_pass(path: Path | None) -> tuple[bool, str | None, dict[str, Any] | None]:
    if not path or not path.exists():
        return False, None, None
    try:
        obj = _load_json(path)
        return str(obj.get("status", "")).upper() == "PASS", str(path), obj
    except Exception:
        return False, str(path), None


def _has_active_backlog_section(obj: dict[str, Any] | None) -> bool:
    if not isinstance(obj, dict):
        return False
    checks = obj.get("checks") or []
    if not isinstance(checks, list):
        return False
    names = {str(c.get("name", "")).strip() for c in checks if isinstance(c, dict)}
    return "active_backlog_history_coverage_present" in names and "active_backlog_expected_set_built" in names


def main() -> int:
    parser = argparse.ArgumentParser(description="Build P7.1 final release bundle (coverage + table chain + gate).")
    parser.add_argument("--qa-dir", default="reports/qa_gate")
    parser.add_argument("--short-summary", default=None)
    parser.add_argument("--long-summary", default=None)
    parser.add_argument("--run-dir", default=None, help="Optional explicit run dir for audit_chain_report.json")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    qa_dir = (root / args.qa_dir).resolve()
    qa_dir.mkdir(parents=True, exist_ok=True)

    latest = {
        "features_block_audit": _latest(qa_dir, "features_block_audit_*.json"),
        "hypothesis_coverage_short": _latest(qa_dir, "hypothesis_coverage_short_only_*.json"),
        "hypothesis_coverage_long": _latest(qa_dir, "hypothesis_coverage_long_only_*.json"),
        "table_convergence": _latest(qa_dir, "table_convergence_5plus_*.json"),
        "tz_gate": _latest(qa_dir, "tz_gate_*.json"),
    }

    checks: list[dict[str, Any]] = []
    parsed: dict[str, dict[str, Any] | None] = {}
    for k, p in latest.items():
        ok, ref, obj = _status_pass(p)
        parsed[k] = obj
        checks.append(_check(f"{k}_pass", ok, {"path": ref}))

    # Ensure new P6.2 section is present in both coverage reports.
    checks.append(
        _check(
            "hypothesis_coverage_short_has_active_backlog_section",
            _has_active_backlog_section(parsed.get("hypothesis_coverage_short")),
            {"path": str(latest["hypothesis_coverage_short"]) if latest["hypothesis_coverage_short"] else None},
        )
    )
    checks.append(
        _check(
            "hypothesis_coverage_long_has_active_backlog_section",
            _has_active_backlog_section(parsed.get("hypothesis_coverage_long")),
            {"path": str(latest["hypothesis_coverage_long"]) if latest["hypothesis_coverage_long"] else None},
        )
    )

    # Check repeats>=3 control cycle summaries.
    short_summary = Path(args.short_summary).resolve() if args.short_summary else None
    long_summary = Path(args.long_summary).resolve() if args.long_summary else None
    if short_summary and short_summary.exists():
        s_obj = _load_json(short_summary)
        checks.append(
            _check(
                "short_control_cycle_repeats_ge_3",
                int(s_obj.get("repeats_requested", 0)) >= 3,
                {"path": str(short_summary), "repeats_requested": s_obj.get("repeats_requested")},
            )
        )
    else:
        checks.append(_check("short_control_cycle_repeats_ge_3", False, {"path": str(short_summary) if short_summary else None}))
    if long_summary and long_summary.exists():
        l_obj = _load_json(long_summary)
        checks.append(
            _check(
                "long_control_cycle_repeats_ge_3",
                int(l_obj.get("repeats_requested", 0)) >= 3,
                {"path": str(long_summary), "repeats_requested": l_obj.get("repeats_requested")},
            )
        )
    else:
        checks.append(_check("long_control_cycle_repeats_ge_3", False, {"path": str(long_summary) if long_summary else None}))

    # Table chain report from explicit run-dir (preferred) or fallback current.
    chain_path = None
    if args.run_dir:
        r = Path(args.run_dir)
        if not r.is_absolute():
            r = (root / r).resolve()
        chain_path = r / "audit_chain_report.json"
    if chain_path is None or not chain_path.exists():
        chain_path = (root / "reports" / "table_canon_current" / "audit_chain_report.json").resolve()
    chain_ok, chain_ref, _ = _status_pass(chain_path)
    checks.append(_check("audit_chain_report_pass", chain_ok, {"path": chain_ref}))

    failed = int(sum(1 for c in checks if not c["ok"]))
    status = "PASS" if failed == 0 else "FAIL"

    payload = {
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "summary": {"total": len(checks), "failed": failed},
    }
    out_json = qa_dir / f"p71_release_bundle_{_utc_tag()}.json"
    out_md = qa_dir / f"p71_release_bundle_{_utc_tag()}.md"
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# P7.1 Release Bundle ({status})",
        f"Generated at: {payload['generated_at_utc']}",
        "",
        "| Check | Status | Path/Details |",
        "|---|---|---|",
    ]
    for c in checks:
        details = c.get("details") or {}
        path_or_meta = details.get("path", details)
        lines.append(f"| {c['name']} | {'PASS' if c['ok'] else 'FAIL'} | {path_or_meta} |")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"status": status, "report_path": str(out_json), "markdown_path": str(out_md)}, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
