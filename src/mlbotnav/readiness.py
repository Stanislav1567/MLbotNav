from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml


DEFAULT_READINESS = {
    "project_ready": False,
    "enforce_freeze": True,
    "reason": "P0 freeze: unresolved technical-spec blockers",
    "block_actions": [
        "train_baseline",
        "pipeline_train_eval",
        "search_gate_candidate",
        "prod_cycle",
        "stage_ladder",
        "stage_engine",
    ],
    "blockers": [],
}


def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _readiness_path(project_root: Path) -> Path:
    return project_root / "configs" / "readiness.yaml"


def load_readiness(project_root: Path) -> dict:
    p = _readiness_path(project_root)
    if not p.exists():
        return dict(DEFAULT_READINESS)
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    root = data.get("readiness", data if isinstance(data, dict) else {})
    if not isinstance(root, dict):
        root = {}
    return _deep_merge(DEFAULT_READINESS, root)


def save_readiness(project_root: Path, readiness: dict) -> Path:
    p = _readiness_path(project_root)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {"readiness": readiness}
    with p.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, allow_unicode=True, sort_keys=False)
    return p


def _parse_bool(text: str) -> bool:
    t = (text or "").strip().lower()
    if t in {"1", "true", "yes", "y", "on"}:
        return True
    if t in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"Unsupported bool value: {text}")


def blockers_summary(readiness: dict) -> dict:
    blockers = readiness.get("blockers", [])
    if not isinstance(blockers, list):
        blockers = []
    open_ids: list[str] = []
    for b in blockers:
        if not isinstance(b, dict):
            continue
        status = str(b.get("status", "open")).strip().lower()
        if status not in {"done", "closed", "resolved"}:
            open_ids.append(str(b.get("id", "unknown")))
    return {
        "total": len([b for b in blockers if isinstance(b, dict)]),
        "open_count": len(open_ids),
        "open_ids": open_ids,
    }


def check_action_allowed(project_root: Path, *, action: str) -> dict:
    readiness = load_readiness(project_root)
    summary = blockers_summary(readiness)
    project_ready = bool(readiness.get("project_ready", False))
    enforce_freeze = bool(readiness.get("enforce_freeze", True))
    block_actions = readiness.get("block_actions", [])
    if not isinstance(block_actions, list):
        block_actions = []

    blocked_by_freeze = enforce_freeze and (not project_ready) and (action in {str(x) for x in block_actions})
    allowed = not blocked_by_freeze
    reason = "ok"
    if blocked_by_freeze:
        reason = (
            f"project_not_ready_for_{action};"
            f"open_blockers={summary['open_count']};"
            f"freeze_reason={readiness.get('reason', '')}"
        )
    return {
        "action": action,
        "allowed": allowed,
        "reason": reason,
        "project_ready": project_ready,
        "enforce_freeze": enforce_freeze,
        "block_actions": block_actions,
        "blockers": summary,
    }


def enforce_action_allowed(project_root: Path, *, action: str) -> dict:
    check = check_action_allowed(project_root, action=action)
    if not check["allowed"]:
        raise RuntimeError(
            "Readiness gate blocked action "
            f"'{action}'. "
            f"Reason: {check['reason']}. "
            "Run `python -m mlbotnav.readiness --show` to inspect readiness state."
        )
    return check


def write_readiness_report(project_root: Path, *, check: dict | None = None) -> Path:
    readiness = load_readiness(project_root)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = project_root / "reports" / "readiness"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"readiness_check_{ts}.json"
    payload = {
        "run_utc": ts,
        "readiness": readiness,
        "blockers": blockers_summary(readiness),
        "check": check or {},
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Project readiness gate and report helper.")
    parser.add_argument("--show", action="store_true")
    parser.add_argument("--check-action", default=None, help="Action id to verify against readiness gate")
    parser.add_argument("--set-project-ready", default=None, help="true/false")
    parser.add_argument("--set-reason", default=None, help="Update readiness reason")
    parser.add_argument("--write-report", default="true", help="true/false")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    readiness = load_readiness(project_root)
    changed = False

    if args.set_project_ready is not None:
        readiness["project_ready"] = _parse_bool(args.set_project_ready)
        readiness["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
        changed = True
    if args.set_reason is not None:
        readiness["reason"] = args.set_reason
        readiness["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
        changed = True
    if changed:
        save_readiness(project_root, readiness)

    check = None
    if args.check_action:
        check = check_action_allowed(project_root, action=args.check_action)

    write_report = _parse_bool(args.write_report)
    report_path = None
    if write_report:
        report_path = write_readiness_report(project_root, check=check)

    out = {
        "readiness": load_readiness(project_root),
        "blockers": blockers_summary(load_readiness(project_root)),
        "check": check,
        "report_path": str(report_path) if report_path else None,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    if check and not check["allowed"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
