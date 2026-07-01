from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(project_root: Path) -> Path:
    return project_root / "data" / "meta" / "stage_runtime_state.json"


def load_stage_state(project_root: Path, *, stages: list[str]) -> dict:
    p = _path(project_root)
    default_stage = stages[0] if stages else "D1"
    default = {
        "current_stage": default_stage,
        "last_completed_stage": None,
        "updated_at_utc": None,
        "history": [],
    }
    if not p.exists():
        return default
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default
    if not isinstance(obj, dict):
        return default
    merged = dict(default)
    merged.update(obj)
    if merged.get("current_stage") not in set(stages):
        merged["current_stage"] = default_stage
    if not isinstance(merged.get("history"), list):
        merged["history"] = []
    return merged


def save_stage_state(project_root: Path, state: dict) -> Path:
    p = _path(project_root)
    p.parent.mkdir(parents=True, exist_ok=True)
    state["updated_at_utc"] = _now_iso()
    p.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def next_stage(current_stage: str, *, stages: list[str]) -> str | None:
    if current_stage not in stages:
        return None
    i = stages.index(current_stage)
    if i >= len(stages) - 1:
        return None
    return stages[i + 1]

