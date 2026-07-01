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


def _status_is_pass(path: Path | None) -> tuple[bool, str | None]:
    if not path or not path.exists():
        return False, None
    try:
        obj = _load_json(path)
        return str(obj.get("status", "")).upper() == "PASS", str(path)
    except Exception:
        return False, str(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a single release-style PASS/FAIL bundle for P5.3.")
    parser.add_argument("--qa-dir", default="reports/qa_gate")
    parser.add_argument("--table-chain-report", default="reports/table_canon_current/audit_chain_report.json")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    qa_dir = (root / args.qa_dir).resolve()
    qa_dir.mkdir(parents=True, exist_ok=True)
    chain_path = (root / args.table_chain_report).resolve()

    out_json = qa_dir / f"p53_release_bundle_{_utc_tag()}.json"
    out_md = qa_dir / f"p53_release_bundle_{_utc_tag()}.md"

    latest = {
        "daily_cycle": _latest(qa_dir, "daily_long_short_cycle_*.json"),
        "dual_acceptance": _latest(qa_dir, "p53_dual_acceptance_*.json"),
        "snapshot": _latest(qa_dir, "p53_snapshot_*.json"),
        "gate": _latest(qa_dir, "tz_gate_*.json"),
        "long_cycle": _latest(qa_dir, "contour_cycle_long_only_*.json"),
        "short_cycle": _latest(qa_dir, "contour_cycle_short_only_*.json"),
        "hypo_long": _latest(qa_dir, "hypothesis_coverage_long_only_*.json"),
        "hypo_short": _latest(qa_dir, "hypothesis_coverage_short_only_*.json"),
        "table_conv": _latest(qa_dir, "table_convergence_5plus_*.json"),
    }

    checks: list[dict[str, Any]] = []
    for name, path in latest.items():
        ok, p = _status_is_pass(path)
        checks.append(_check(f"{name}_pass", ok, {"path": p}))

    chain_ok, chain_ref = _status_is_pass(chain_path)
    checks.append(_check("table_chain_pass", chain_ok, {"path": chain_ref}))

    failed = int(sum(1 for c in checks if not c["ok"]))
    status = "PASS" if failed == 0 else "FAIL"

    payload = {
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "summary": {"total": len(checks), "failed": failed},
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# P5.3 Release Bundle ({status})",
        f"Generated at: {payload['generated_at_utc']}",
        "",
        "| Check | Status | Path |",
        "|---|---|---|",
    ]
    for c in checks:
        lines.append(f"| {c['name']} | {'PASS' if c['ok'] else 'FAIL'} | {c['details'].get('path', '')} |")
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"status": status, "report_path": str(out_json), "markdown_path": str(out_md)}, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
