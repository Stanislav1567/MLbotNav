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


def _latest_run_dir(root: Path) -> Path:
    runs_root = root / "reports" / "runs"
    runs = sorted([p for p in runs_root.glob("run_*") if p.is_dir()], key=lambda p: p.stat().st_mtime, reverse=True)
    if not runs:
        raise FileNotFoundError("No run_* directories found under reports/runs")
    return runs[0]


def _check(name: str, ok: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": details or {}}


def main() -> int:
    parser = argparse.ArgumentParser(description="P5.3 guard: ensure packaged CSV files are Excel-ready (; + manifest).")
    parser.add_argument("--run-dir", default=None, help="Optional explicit reports/runs/<run_id> dir.")
    parser.add_argument("--qa-dir", default="reports/qa_gate")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    qa_dir = (root / args.qa_dir).resolve()
    qa_dir.mkdir(parents=True, exist_ok=True)

    run_dir = Path(args.run_dir).resolve() if args.run_dir else _latest_run_dir(root)
    if not run_dir.is_absolute():
        run_dir = (root / run_dir).resolve()

    manifest_path = run_dir / "state" / "p4_pack_manifest.json"
    checks: list[dict[str, Any]] = []

    if not manifest_path.exists():
        checks.append(_check("pack_manifest_exists", False, {"path": str(manifest_path)}))
        failed = 1
    else:
        checks.append(_check("pack_manifest_exists", True, {"path": str(manifest_path)}))
        manifest = _load_json(manifest_path)
        normalized = manifest.get("normalized_csv") or []
        checks.append(_check("normalized_csv_present", isinstance(normalized, list) and len(normalized) >= 6, {"count": len(normalized)}))
        required_names = {
            "candles_canonical.csv",
            "feature_frame.csv",
            "feature_frame_full.csv",
            "signal_frame.csv",
            "execution_trace.csv",
            "strategy_summary.csv",
        }
        present_names = {Path(str((row or {}).get("path", ""))).name for row in normalized}
        missing_names = sorted(required_names - present_names)
        checks.append(_check("normalized_csv_required_files", len(missing_names) == 0, {"missing": missing_names}))
        for row in normalized:
            p = str((row or {}).get("path", ""))
            exists = bool((row or {}).get("exists", False))
            to_sep = str((row or {}).get("to_sep", ""))
            from_sep = str((row or {}).get("from_sep", ""))
            checks.append(_check(f"csv_exists::{Path(p).name}", exists, {"path": p}))
            checks.append(_check(f"csv_target_sep::{Path(p).name}", to_sep == ";", {"path": p, "to_sep": to_sep, "from_sep": from_sep}))
    failed = int(sum(1 for c in checks if not c["ok"]))
    payload = {
        "status": "PASS" if failed == 0 else "FAIL",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "manifest_path": str(manifest_path),
        "checks": checks,
        "summary": {"total": len(checks), "failed": failed},
    }
    out = qa_dir / f"p53_pack_csv_guard_{_utc_tag()}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "report_path": str(out), "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
