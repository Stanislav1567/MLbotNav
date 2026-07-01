from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _latest(root: Path, pattern: str) -> Path | None:
    files = sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def _resolve(project_root: Path, raw: str, fallback: Path | None = None) -> Path | None:
    if raw and str(raw).strip():
        p = Path(str(raw).strip())
        if not p.is_absolute():
            p = (project_root / p).resolve()
        return p
    return fallback


def main() -> int:
    parser = argparse.ArgumentParser(description="Build strict AKFP chain manifest with pinned artifact paths.")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--test-day", default="2026-05-20")
    parser.add_argument("--output-dir", default="reports/akfp/chain_manifest")
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
    parser.add_argument("--working-tools", default="reports/akfp/combo_working/WORKING_TOOLS.json")
    parser.add_argument("--best-combos", default="reports/akfp/combo_working/BEST_COMBOS.json")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    qa = project_root / "reports" / "qa_gate"
    fr = project_root / "reports" / "final_review"
    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = (project_root / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    paths: dict[str, Path | None] = {
        "long_pkg": _resolve(project_root, args.long_pkg, (project_root / "reports/akfp/final_long/LONG_FINAL_PACKAGE.json").resolve()),
        "short_pkg": _resolve(project_root, args.short_pkg, (project_root / "reports/akfp/final_short/SHORT_FINAL_PACKAGE.json").resolve()),
        "long_oos": _resolve(project_root, args.long_oos, _latest(fr, f"oos_report_*_{args.test_day}_long_only_*.json")),
        "short_oos": _resolve(project_root, args.short_oos, _latest(fr, f"oos_report_*_{args.test_day}_short_only_*.json")),
        "p23_report": _resolve(project_root, args.p23_report, _latest(qa, "p23_operator_unified_*.json")),
        "p24_report": _resolve(project_root, args.p24_report, _latest(qa, "p24_latest_pass_*.json")),
        "tz_report": _resolve(project_root, args.tz_report, _latest(qa, "tz_gate_*.json")),
        "convergence_report": _resolve(project_root, args.convergence_report, _latest(qa, "table_convergence_5plus_*.json")),
        "p72_report": _resolve(project_root, args.p72_report, _latest(qa, "p72_freeze_ready_*.json")),
        "chain_report": _resolve(project_root, args.chain_report, (project_root / "reports/table_canon_current/audit_chain_report.json").resolve()),
        "working_tools": _resolve(project_root, args.working_tools, None),
        "best_combos": _resolve(project_root, args.best_combos, None),
    }

    missing = [k for k, v in paths.items() if v is None or not Path(v).exists()]
    status = "PASS" if not missing else "FAIL"
    payload: dict[str, Any] = {
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "test_day": args.test_day,
        "artifact_paths": {k: (str(v.resolve()) if isinstance(v, Path) and v.exists() else None) for k, v in paths.items()},
        "missing_keys": missing,
    }
    out = out_dir / f"akfp_chain_manifest_{args.symbol}_{args.timeframe}_{args.test_day}_{_utc_tag()}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": status, "manifest_path": str(out)}, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

