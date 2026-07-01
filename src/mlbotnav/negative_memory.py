from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _to_iso(dt: datetime) -> str:
    return dt.isoformat()


def build_fingerprint(*, params: dict, context: dict) -> str:
    payload = {"params": params, "context": context}
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _reason_tags(reason: str) -> list[str]:
    tags: list[str] = []
    for part in (reason or "").split(";"):
        p = part.strip()
        if not p:
            continue
        tags.append(p.split(":", 1)[0])
    return sorted(set(tags))


def _param_signature(params: dict) -> str:
    raw = json.dumps(params or {}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def _path(project_root: Path) -> Path:
    return project_root / "data" / "meta" / "negative_memory.jsonl"


def add_negative_event(
    project_root: Path,
    *,
    fingerprint: str,
    stage: str,
    reason: str,
    params: dict,
    context: dict,
    cooldown_hours: int,
) -> dict:
    p = _path(project_root)
    p.parent.mkdir(parents=True, exist_ok=True)
    now = _now_utc()
    row = {
        "ts_utc": _to_iso(now),
        "fingerprint": fingerprint,
        "stage": stage,
        "reason": reason,
        "reason_tags": _reason_tags(reason),
        "param_signature": _param_signature(params),
        "cooldown_until_utc": _to_iso(now + timedelta(hours=cooldown_hours)),
        "params": params,
        "context": context,
    }
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def is_fingerprint_blocked(project_root: Path, *, fingerprint: str) -> tuple[bool, dict | None]:
    p = _path(project_root)
    if not p.exists():
        return False, None
    now = _now_utc()
    last_match = None
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("fingerprint") != fingerprint:
            continue
        last_match = row
    if not last_match:
        return False, None
    cooldown_until = datetime.fromisoformat(last_match["cooldown_until_utc"])
    if now < cooldown_until:
        remaining = (cooldown_until - now).total_seconds() / 3600.0
        enriched = dict(last_match)
        enriched["cooldown_remaining_hours"] = round(max(0.0, remaining), 3)
        return True, enriched
    return False, last_match


def summarize_negative_memory(project_root: Path, *, stage: str | None = None) -> dict:
    p = _path(project_root)
    if not p.exists():
        return {
            "rows_total": 0,
            "rows_stage": 0,
            "active_blocks": 0,
            "unique_fingerprints": 0,
            "reason_tag_counts": {},
        }
    now = _now_utc()
    rows = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except Exception:
            continue
        if stage and row.get("stage") != stage:
            continue
        rows.append(row)
    active = 0
    reason_counts: dict[str, int] = {}
    fp = set()
    for row in rows:
        fp.add(row.get("fingerprint"))
        for t in row.get("reason_tags", []) or []:
            reason_counts[t] = reason_counts.get(t, 0) + 1
        cu = row.get("cooldown_until_utc")
        try:
            if cu and now < datetime.fromisoformat(cu):
                active += 1
        except Exception:
            pass
    return {
        "rows_total": len(rows),
        "rows_stage": len(rows),
        "active_blocks": active,
        "unique_fingerprints": len(fp),
        "reason_tag_counts": reason_counts,
    }
