from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _parse_bool(text: str | bool | None) -> bool:
    if isinstance(text, bool):
        return text
    t = str(text or "").strip().lower()
    return t in {"1", "true", "yes", "y", "on"}


def _parse_dt_utc(text: str | None) -> datetime | None:
    raw = str(text or "").strip()
    if not raw:
        return None
    raw = raw.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(raw)
    except Exception:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _load_json_status(path: Path) -> str:
    try:
        obj = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(obj, dict) and "status" in obj:
            return str(obj.get("status", "unknown"))
    except Exception:
        pass
    return "unknown"


def _latest(root: Path, pattern: str) -> Path | None:
    items = sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return items[0] if items else None


def _latest_after(root: Path, pattern: str, cutoff_utc: datetime) -> Path | None:
    items: list[Path] = []
    for p in root.glob(pattern):
        try:
            dt = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
            if dt >= cutoff_utc:
                items.append(p)
        except Exception:
            continue
    items.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return items[0] if items else None


def resolve_latest_pass_contract(
    *,
    project_root: Path,
    patterns: list[str],
    source_p23_mode: str,
    resolved_source_p23: str | None,
    epoch_lock_enabled: bool,
    epoch_cutoff_utc: datetime | None,
    epoch_lock_bypass_patterns: list[str],
) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    bypass = {str(x).strip() for x in epoch_lock_bypass_patterns if str(x).strip()}
    resolved_p23_path = Path(resolved_source_p23).resolve() if str(resolved_source_p23 or "").strip() else None

    for pattern in patterns:
        if str(source_p23_mode) == "table_chain" and pattern == "reports/qa_gate/daily_long_short_cycle_*.json":
            items.append({"pattern": pattern, "file": None, "updated_utc": None, "status": "not_required_for_table_chain"})
            continue

        is_bypass = pattern in bypass
        resolution_mode = "latest"
        selected: Path | None = None
        if pattern == "reports/qa_gate/p23_operator_unified_*.json" and resolved_p23_path is not None and resolved_p23_path.exists():
            selected = resolved_p23_path
            resolution_mode = "pinned_source"
        elif bool(epoch_lock_enabled) and epoch_cutoff_utc is not None and not is_bypass:
            selected = _latest_after(project_root, pattern, epoch_cutoff_utc)
            resolution_mode = "epoch_locked"
        else:
            selected = _latest(project_root, pattern)
            if bool(epoch_lock_enabled) and is_bypass:
                resolution_mode = "baseline_latest"

        if selected is not None and selected.exists():
            items.append(
                {
                    "pattern": pattern,
                    "file": str(selected.resolve()),
                    "updated_utc": datetime.fromtimestamp(selected.stat().st_mtime, tz=timezone.utc).isoformat(),
                    "status": _load_json_status(selected),
                    "resolution_mode": resolution_mode,
                    "epoch_lock_bypass": bool(is_bypass),
                }
            )
            continue

        miss_status = "missing_epoch_locked" if bool(epoch_lock_enabled) and not is_bypass else "missing"
        items.append(
            {
                "pattern": pattern,
                "file": None,
                "updated_utc": None,
                "status": miss_status,
                "resolution_mode": resolution_mode,
                "epoch_lock_bypass": bool(is_bypass),
            }
        )

    pass_count = sum(1 for x in items if str(x.get("status")) == "PASS")
    non_pass_count = sum(
        1
        for x in items
        if str(x.get("status")) not in {"PASS", "missing", "missing_epoch_locked", "not_required_for_table_chain"}
    )
    missing_count = sum(1 for x in items if str(x.get("status")) in {"missing", "missing_epoch_locked"})
    epoch_locked_missing_count = sum(1 for x in items if str(x.get("status")) == "missing_epoch_locked")

    p23_item = next((x for x in items if str(x.get("pattern")) == "reports/qa_gate/p23_operator_unified_*.json"), None)
    p23_report_used = str((p23_item or {}).get("file") or "")
    if resolved_p23_path is None:
        p23_exact_match = True
    else:
        try:
            p23_exact_match = Path(p23_report_used).resolve() == resolved_p23_path
        except Exception:
            p23_exact_match = False

    return {
        "items": items,
        "pass_count": int(pass_count),
        "non_pass_count": int(non_pass_count),
        "missing_count": int(missing_count),
        "epoch_locked_missing_count": int(epoch_locked_missing_count),
        "p23_report_used": p23_report_used,
        "p23_exact_match": bool(p23_exact_match),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve P24 latest-pass contract items.")
    parser.add_argument("--request-json", required=True)
    args = parser.parse_args()

    req_path = Path(args.request_json).resolve()
    req = json.loads(req_path.read_text(encoding="utf-8-sig"))
    project_root = Path(str(req.get("project_root") or "")).resolve()
    patterns = [str(x) for x in (req.get("patterns") or [])]
    source_p23_mode = str(req.get("source_p23_mode") or "")
    resolved_source_p23 = str(req.get("resolved_source_p23") or "").strip() or None
    epoch_lock_enabled = _parse_bool(req.get("epoch_lock_enabled"))
    epoch_cutoff_utc = _parse_dt_utc(req.get("epoch_cutoff_utc"))
    bypass_patterns = [str(x) for x in (req.get("epoch_lock_bypass_patterns") or [])]

    out = resolve_latest_pass_contract(
        project_root=project_root,
        patterns=patterns,
        source_p23_mode=source_p23_mode,
        resolved_source_p23=resolved_source_p23,
        epoch_lock_enabled=epoch_lock_enabled,
        epoch_cutoff_utc=epoch_cutoff_utc,
        epoch_lock_bypass_patterns=bypass_patterns,
    )
    print(json.dumps(out, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
