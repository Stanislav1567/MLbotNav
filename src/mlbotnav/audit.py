from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path


def audit_event(project_root: Path, *, event: str, payload: dict) -> None:
    logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    out = logs_dir / "audit.log"
    chain_state = logs_dir / "audit_chain_state.json"
    prev_hash = ""
    if chain_state.exists():
        try:
            prev_hash = json.loads(chain_state.read_text(encoding="utf-8")).get("last_hash", "") or ""
        except Exception:
            prev_hash = ""
    row = {
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "payload": payload,
        "prev_hash": prev_hash,
    }
    raw = json.dumps(row, ensure_ascii=False, sort_keys=True)
    row_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    row["row_hash"] = row_hash
    with out.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    chain_state.write_text(json.dumps({"last_hash": row_hash}, ensure_ascii=False), encoding="utf-8")
