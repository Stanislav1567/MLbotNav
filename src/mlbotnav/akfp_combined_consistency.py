from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _latest(pattern: str, root: Path) -> Path | None:
    files = sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def main() -> int:
    parser = argparse.ArgumentParser(description="AKFP P11: combined consistency (long/short isolation + chain checks).")
    parser.add_argument("--test-day", default="2026-05-20")
    parser.add_argument("--output-dir", default="reports/akfp/combined")
    parser.add_argument("--long-pkg", default="")
    parser.add_argument("--short-pkg", default="")
    parser.add_argument("--long-oos", default="")
    parser.add_argument("--short-oos", default="")
    parser.add_argument("--p23-report", default="")
    parser.add_argument("--p24-report", default="")
    parser.add_argument("--tz-report", default="")
    parser.add_argument("--convergence-report", default="")
    parser.add_argument("--p72-report", default="")
    parser.add_argument("--chain-report", default="")
    parser.add_argument("--chain-manifest", default="")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    qa = project_root / "reports" / "qa_gate"
    fr = project_root / "reports" / "final_review"

    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = (project_root / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_obj: dict[str, Any] = {}
    manifest_paths: dict[str, Any] = {}
    if str(args.chain_manifest).strip():
        mp = Path(str(args.chain_manifest)).resolve()
        if mp.exists():
            manifest_obj = _load_json(mp)
            manifest_paths = dict(manifest_obj.get("artifact_paths") or {})
            if str(manifest_obj.get("test_day", "")).strip() and str(manifest_obj.get("test_day")).strip() != str(args.test_day).strip():
                raise RuntimeError(f"chain_manifest test_day mismatch: {manifest_obj.get('test_day')} != {args.test_day}")
        else:
            raise RuntimeError(f"chain_manifest not found: {mp}")

    def _pick(raw_arg: str, manifest_key: str, fallback: Path | None) -> Path | None:
        if str(raw_arg).strip():
            return Path(str(raw_arg)).resolve()
        m = str(manifest_paths.get(manifest_key, "")).strip()
        if m:
            return Path(m).resolve()
        return fallback

    long_pkg = _pick(args.long_pkg, "long_pkg", (project_root / "reports" / "akfp" / "final_long" / "LONG_FINAL_PACKAGE.json"))
    short_pkg = _pick(args.short_pkg, "short_pkg", (project_root / "reports" / "akfp" / "final_short" / "SHORT_FINAL_PACKAGE.json"))
    long_oos = _pick(args.long_oos, "long_oos", _latest(f"oos_report_*_{args.test_day}_long_only_*.json", fr))
    short_oos = _pick(args.short_oos, "short_oos", _latest(f"oos_report_*_{args.test_day}_short_only_*.json", fr))
    p23 = _pick(args.p23_report, "p23_report", _latest("p23_operator_unified_*.json", qa))
    p24 = _pick(args.p24_report, "p24_report", _latest("p24_latest_pass_*.json", qa))
    tz = _pick(args.tz_report, "tz_report", _latest("tz_gate_*.json", qa))
    conv = _pick(args.convergence_report, "convergence_report", _latest("table_convergence_5plus_*.json", qa))
    p72 = _pick(args.p72_report, "p72_report", _latest("p72_freeze_ready_*.json", qa))
    chain = _pick(args.chain_report, "chain_report", (project_root / "reports" / "table_canon_current" / "audit_chain_report.json"))

    checks: list[dict[str, Any]] = []
    checks.append({"name": "long_pkg_exists", "ok": long_pkg.exists(), "path": str(long_pkg)})
    checks.append({"name": "short_pkg_exists", "ok": short_pkg.exists(), "path": str(short_pkg)})
    checks.append({"name": "long_oos_exists", "ok": bool(long_oos and long_oos.exists()), "path": str(long_oos) if long_oos else None})
    checks.append({"name": "short_oos_exists", "ok": bool(short_oos and short_oos.exists()), "path": str(short_oos) if short_oos else None})
    checks.append(
        {
            "name": "long_short_oos_isolated",
            "ok": bool(long_oos and short_oos and long_oos != short_oos and "long_only" in long_oos.name and "short_only" in short_oos.name),
            "details": {"long_oos": str(long_oos) if long_oos else None, "short_oos": str(short_oos) if short_oos else None},
        }
    )
    checks.append({"name": "p23_exists", "ok": bool(p23 and p23.exists()), "path": str(p23) if p23 else None})
    checks.append({"name": "p24_exists", "ok": bool(p24 and p24.exists()), "path": str(p24) if p24 else None})
    checks.append({"name": "tz_gate_exists", "ok": bool(tz and tz.exists()), "path": str(tz) if tz else None})
    checks.append({"name": "convergence_exists", "ok": bool(conv and conv.exists()), "path": str(conv) if conv else None})
    checks.append({"name": "p72_exists", "ok": bool(p72 and p72.exists()), "path": str(p72) if p72 else None})
    checks.append({"name": "audit_chain_exists", "ok": chain.exists(), "path": str(chain)})

    def _status_ok(path: Path | None) -> bool:
        if not path or not path.exists():
            return False
        try:
            obj = _load_json(path)
            return str(obj.get("status", "")).upper() == "PASS"
        except Exception:
            return False

    checks.append({"name": "p23_status_pass", "ok": _status_ok(p23), "path": str(p23) if p23 else None})
    checks.append({"name": "p24_status_pass", "ok": _status_ok(p24), "path": str(p24) if p24 else None})
    checks.append({"name": "tz_gate_status_pass", "ok": _status_ok(tz), "path": str(tz) if tz else None})
    checks.append({"name": "convergence_status_pass", "ok": _status_ok(conv), "path": str(conv) if conv else None})
    checks.append({"name": "p72_status_pass", "ok": _status_ok(p72), "path": str(p72) if p72 else None})
    checks.append({"name": "audit_chain_status_pass", "ok": _status_ok(chain), "path": str(chain)})
    try:
        long_pkg_obj = _load_json(long_pkg) if long_pkg.exists() else {}
    except Exception:
        long_pkg_obj = {}
    try:
        short_pkg_obj = _load_json(short_pkg) if short_pkg.exists() else {}
    except Exception:
        short_pkg_obj = {}
    checks.append({"name": "long_pkg_strategy_pass", "ok": bool((long_pkg_obj or {}).get("strategy_pass") is True), "path": str(long_pkg)})
    checks.append({"name": "short_pkg_strategy_pass", "ok": bool((short_pkg_obj or {}).get("strategy_pass") is True), "path": str(short_pkg)})
    try:
        p24_obj = _load_json(p24) if p24 and p24.exists() else {}
    except Exception:
        p24_obj = {}
    p24_p23_used = str((p24_obj or {}).get("p23_report_used", "")).strip()
    checks.append(
        {
            "name": "p24_links_to_same_p23",
            "ok": bool(p23 and p24_p23_used and Path(p24_p23_used).resolve() == Path(p23).resolve()),
            "details": {"p23_report": str(p23) if p23 else None, "p24_report_used": p24_p23_used or None},
        }
    )

    failed = sum(1 for c in checks if not bool(c["ok"]))
    status = "PASS" if failed == 0 else "FAIL"
    payload = {
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "test_day": str(args.test_day),
        "chain_manifest": str(args.chain_manifest).strip() or None,
        "summary": {"total": len(checks), "failed": int(failed)},
        "checks": checks,
    }
    out = out_dir / f"akfp_combined_consistency_{args.test_day}_{_utc_tag()}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": status, "report_path": str(out)}, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
