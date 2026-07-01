from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from mlbotnav.audit import audit_event


def load_governance_policy(project_root: Path) -> dict:
    p = project_root / "configs" / "security_governance.yaml"
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def enforce_retention(project_root: Path, *, logs_days: int, reports_days: int, packs_days: int) -> dict:
    now = datetime.now(timezone.utc)
    deleted = {"logs": 0, "reports": 0, "packs": 0}

    def _purge_under(root: Path, keep_days: int, key: str) -> None:
        if not root.exists():
            return
        cutoff = now - timedelta(days=keep_days)
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
            if mtime < cutoff:
                p.unlink(missing_ok=True)
                deleted[key] += 1

    _purge_under(project_root / "logs", logs_days, "logs")
    _purge_under(project_root / "reports", reports_days, "reports")
    _purge_under(project_root / "packs", packs_days, "packs")
    return deleted


def archive_old_packs(
    project_root: Path,
    *,
    keep_days: int,
    archive_root: str = "data/cold_storage/packs",
) -> dict:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=int(keep_days))
    packs_root = project_root / "packs"
    cold_root = project_root / archive_root
    cold_root.mkdir(parents=True, exist_ok=True)
    moved_dirs = 0
    moved_files = 0
    if not packs_root.exists():
        return {"moved_dirs": 0, "moved_files": 0, "archive_root": str(cold_root)}
    for day_dir in packs_root.glob("20??-??-??"):
        if not day_dir.is_dir():
            continue
        try:
            day_dt = datetime.strptime(day_dir.name, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except Exception:
            continue
        if day_dt >= cutoff:
            continue
        target_day = cold_root / day_dir.name
        target_day.mkdir(parents=True, exist_ok=True)
        for item in day_dir.iterdir():
            dst = target_day / item.name
            if dst.exists():
                continue
            shutil.move(str(item), str(dst))
            moved_dirs += 1 if dst.is_dir() else 0
            if dst.is_dir():
                moved_files += sum(1 for _ in dst.rglob("*") if _.is_file())
            else:
                moved_files += 1
        # Remove empty day folder after move.
        if not any(day_dir.iterdir()):
            day_dir.rmdir()
    return {"moved_dirs": moved_dirs, "moved_files": moved_files, "archive_root": str(cold_root)}


def quarantine_day(
    project_root: Path,
    *,
    date: str,
    symbol: str,
    timeframe: str,
    reason: str,
) -> dict:
    src = project_root / "data" / "raw" / "bybit_ohlcv" / f"dt={date}" / f"tf={timeframe}" / f"symbol={symbol}" / "part-final.csv"
    if not src.exists():
        return {"moved": False, "reason": "source_not_found"}

    dst_dir = project_root / "data" / "quarantine" / "bybit_ohlcv" / f"dt={date}" / f"tf={timeframe}" / f"symbol={symbol}"
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / "part-final.csv"
    shutil.copy2(src, dst)
    meta = {
        "date": date,
        "symbol": symbol,
        "timeframe": timeframe,
        "reason": reason,
        "quarantined_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_file": str(src),
        "quarantine_file": str(dst),
    }
    (dst_dir / "quarantine_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"moved": True, "dst": str(dst), "meta": str(dst_dir / "quarantine_meta.json")}


_SECRET_PATTERNS = [
    re.compile(r"BYBIT_API_KEY\s*[:=]\s*[A-Za-z0-9_\-]{8,}", re.IGNORECASE),
    re.compile(r"BYBIT_API_SECRET\s*[:=]\s*[A-Za-z0-9_\-]{8,}", re.IGNORECASE),
    re.compile(r"THREECOMMAS_API_KEY\s*[:=]\s*[A-Za-z0-9_\-]{16,}", re.IGNORECASE),
    re.compile(r"THREECOMMAS_API_SECRET\s*[:=]\s*[A-Za-z0-9_\-]{16,}", re.IGNORECASE),
]


def scan_secret_leaks(
    project_root: Path,
    *,
    include_roots: list[str],
    exclude_extensions: list[str],
) -> list[dict]:
    findings: list[dict] = []
    for rel in include_roots:
        root = project_root / rel
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() in {x.lower() for x in exclude_extensions}:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for rx in _SECRET_PATTERNS:
                m = rx.search(text)
                if m:
                    findings.append({"file": str(p), "pattern": rx.pattern, "snippet": m.group(0)[:120]})
    return findings


def run_governance_maintenance(project_root: Path) -> dict:
    policy = load_governance_policy(project_root).get("governance", {})
    ret = policy.get("retention", {})
    archive = {}
    if bool(ret.get("archive_packs_before_delete", True)):
        archive = archive_old_packs(
            project_root,
            keep_days=int(ret.get("packs_days", 90)),
            archive_root=str(ret.get("cold_storage_root", "data/cold_storage/packs")),
        )
    deleted = enforce_retention(
        project_root,
        logs_days=int(ret.get("logs_days", 30)),
        reports_days=int(ret.get("reports_days", 60)),
        packs_days=int(ret.get("packs_days", 90)),
    )
    ss = policy.get("secret_scan", {})
    findings = []
    if ss.get("enabled", True):
        findings = scan_secret_leaks(
            project_root,
            include_roots=list(ss.get("include_roots", ["reports", "logs", "packs"])),
            exclude_extensions=list(ss.get("exclude_extensions", [".png", ".jpg", ".jpeg", ".joblib", ".parquet", ".db"])),
        )

    result = {
        "run_utc": datetime.now(timezone.utc).isoformat(),
        "pack_archive": archive,
        "deleted_files": deleted,
        "secret_leak_findings_count": len(findings),
        "secret_leak_findings": findings[:100],
    }
    audit_event(
        project_root,
        event="governance_maintenance_completed",
        payload={
            "pack_archive": archive,
            "deleted_files": deleted,
            "secret_leak_findings_count": len(findings),
        },
    )
    return result
