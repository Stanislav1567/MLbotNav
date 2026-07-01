from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _latest(root: Path, pattern: str) -> Path | None:
    items = sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return items[0] if items else None


def _load_json_status(path: Path) -> str:
    try:
        obj = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(obj, dict) and "status" in obj:
            return str(obj.get("status", "unknown"))
    except Exception:
        pass
    return "unknown"


def resolve_required_reports_contract(
    *,
    project_root: Path,
    required_patterns: list[str],
    source_p23_mode: str = "",
) -> dict[str, Any]:
    reports: list[dict[str, Any]] = []
    missing: list[str] = []
    non_pass_reports: list[str] = []
    mode = str(source_p23_mode or "").strip().lower()

    for pattern in required_patterns:
        if mode == "table_chain" and pattern == "reports/qa_gate/daily_long_short_cycle_*.json":
            reports.append(
                {
                    "pattern": pattern,
                    "file": None,
                    "status": "not_required_for_table_chain",
                    "updated_utc": None,
                }
            )
            continue
        p = _latest(project_root, pattern)
        if p is None:
            missing.append(pattern)
            continue
        status = _load_json_status(p)
        if status != "PASS":
            non_pass_reports.append(str(p.resolve()))
        reports.append(
            {
                "pattern": pattern,
                "file": str(p.resolve()),
                "status": status,
                "updated_utc": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat(),
            }
        )

    return {
        "missing": missing,
        "non_pass_reports": non_pass_reports,
        "reports": reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve P26 required reports contract.")
    parser.add_argument("--request-json", required=True)
    args = parser.parse_args()

    req_path = Path(args.request_json).resolve()
    req = json.loads(req_path.read_text(encoding="utf-8-sig"))
    root = Path(str(req.get("project_root") or "")).resolve()
    patterns = [str(x) for x in (req.get("required_patterns") or [])]
    source_p23_mode = str(req.get("source_p23_mode") or "")
    out = resolve_required_reports_contract(
        project_root=root,
        required_patterns=patterns,
        source_p23_mode=source_p23_mode,
    )
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
