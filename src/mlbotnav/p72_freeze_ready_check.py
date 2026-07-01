from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.readiness import check_action_allowed, load_readiness


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _check(name: str, ok: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": details or {}}


def _latest(root: Path, pattern: str) -> Path | None:
    items = sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return items[0] if items else None


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="P7.2 freeze-ready check before next contour.")
    parser.add_argument("--qa-dir", default="reports/qa_gate")
    parser.add_argument(
        "--mode",
        choices=("freeze", "release"),
        default="freeze",
        help="freeze: expect project_ready=false and blocked training actions; release: expect project_ready=true and allowed training actions.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    qa_dir = (project_root / args.qa_dir).resolve()
    qa_dir.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    p71 = _latest(qa_dir, "p71_release_bundle_*.json")
    p71_ok = False
    p71_obj = None
    if p71 and p71.exists():
        p71_obj = _load_json(p71)
        p71_ok = str(p71_obj.get("status", "")).upper() == "PASS"
    checks.append(_check("p71_release_bundle_pass", p71_ok, {"path": str(p71) if p71 else None}))

    readiness = load_readiness(project_root)
    checks.append(_check("readiness_enforce_freeze_true", bool(readiness.get("enforce_freeze", False)), {"enforce_freeze": readiness.get("enforce_freeze")}))
    project_ready = bool(readiness.get("project_ready", True))
    if args.mode == "freeze":
        checks.append(_check("readiness_project_ready_false", not project_ready, {"project_ready": readiness.get("project_ready"), "mode": args.mode}))
    else:
        checks.append(_check("readiness_project_ready_true", project_ready, {"project_ready": readiness.get("project_ready"), "mode": args.mode}))

    block_actions = set(str(x) for x in (readiness.get("block_actions") or []))
    required_block_actions = {"search_gate_candidate", "pipeline_train_eval"}
    checks.append(
        _check(
            "readiness_block_actions_include_core_train_steps",
            required_block_actions.issubset(block_actions),
            {"required": sorted(required_block_actions), "found": sorted(block_actions)},
        )
    )

    c_search = check_action_allowed(project_root, action="search_gate_candidate")
    c_train = check_action_allowed(project_root, action="pipeline_train_eval")
    if args.mode == "freeze":
        checks.append(_check("freeze_blocks_search_gate_candidate", not bool(c_search.get("allowed", True)), {"check": c_search, "mode": args.mode}))
        checks.append(_check("freeze_blocks_pipeline_train_eval", not bool(c_train.get("allowed", True)), {"check": c_train, "mode": args.mode}))
    else:
        checks.append(_check("release_allows_search_gate_candidate", bool(c_search.get("allowed", False)), {"check": c_search, "mode": args.mode}))
        checks.append(_check("release_allows_pipeline_train_eval", bool(c_train.get("allowed", False)), {"check": c_train, "mode": args.mode}))

    failed = int(sum(1 for c in checks if not c["ok"]))
    status = "PASS" if failed == 0 else "FAIL"
    payload = {
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "summary": {"total": len(checks), "failed": failed},
    }
    out = qa_dir / f"p72_freeze_ready_{_utc_tag()}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": status, "report_path": str(out), "failed": failed}, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
