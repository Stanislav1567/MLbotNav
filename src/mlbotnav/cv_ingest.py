from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from mlbotnav.audit import audit_event

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None

try:
    from PIL import Image
except Exception:  # pragma: no cover
    Image = None


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(1024 * 1024)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _perceptual_hash(path: Path) -> str:
    if Image is None:
        # Fallback signature when Pillow is unavailable.
        data = path.read_bytes()
        return hashlib.md5(data[:8192]).hexdigest()

    try:
        img = Image.open(path).convert("L").resize((8, 8))
        px = np.asarray(img, dtype=np.float32).reshape(-1)
        avg = float(px.mean())
        bits = "".join("1" if float(p) >= avg else "0" for p in px)
        return f"{int(bits, 2):016x}"
    except Exception:
        # Non-image payloads should still be processable by scanner/quarantine path.
        data = path.read_bytes()
        return hashlib.md5(data[:8192]).hexdigest()


def _hamming_hex(a: str, b: str) -> int:
    try:
        ia = int(a, 16)
        ib = int(b, 16)
    except Exception:
        return 999
    return (ia ^ ib).bit_count()


def _load_index_rows(index_path: Path) -> list[dict]:
    if not index_path.exists():
        return []
    with index_path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


@dataclass(frozen=True)
class CVScanResult:
    status: str
    reason: str
    details: list[str]


def _load_scan_policy(project_root: Path) -> dict:
    default = {
        "enabled": True,
        "mode": "quarantine",
        "max_file_size_mb": 20,
        "blocked_extensions": [".exe", ".dll", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".msi", ".scr"],
    }
    p = project_root / "configs" / "security_governance.yaml"
    if yaml is None or not p.exists():
        return default
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return default
    sec = data.get("security", {}) if isinstance(data, dict) else {}
    cv = sec.get("cv_scan", {}) if isinstance(sec, dict) else {}
    if not isinstance(cv, dict):
        cv = {}
    out = dict(default)
    out.update(cv)
    out["mode"] = str(out.get("mode", "quarantine")).strip().lower()
    if out["mode"] not in {"block", "quarantine", "report"}:
        out["mode"] = "quarantine"
    return out


def _scan_file(path: Path, *, policy: dict) -> CVScanResult:
    if not bool(policy.get("enabled", True)):
        return CVScanResult(status="disabled", reason="scan_disabled", details=[])

    reasons: list[str] = []
    ext = path.suffix.lower()
    blocked_ext = {str(x).lower() for x in (policy.get("blocked_extensions") or [])}
    if ext in blocked_ext:
        reasons.append(f"blocked_extension:{ext}")

    max_file_size_mb = float(policy.get("max_file_size_mb", 20))
    size_mb = path.stat().st_size / (1024.0 * 1024.0)
    if size_mb > max_file_size_mb:
        reasons.append(f"file_too_large:{size_mb:.2f}mb>{max_file_size_mb:.2f}mb")

    header = path.read_bytes()[:256]
    if header.startswith(b"MZ"):
        reasons.append("pe_header_detected")
    if header.startswith(b"#!"):
        reasons.append("script_shebang_detected")

    if reasons:
        return CVScanResult(status="suspicious", reason=reasons[0], details=reasons)
    return CVScanResult(status="clean", reason="ok", details=[])


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest CV screenshot with integrity metadata.")
    parser.add_argument("--file", required=True, help="Path to screenshot file")
    parser.add_argument("--source-id", required=True, help="Source identifier")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--dedup-hamming-threshold", type=int, default=5)
    parser.add_argument("--dedup-policy", default="skip", choices=["skip", "merge", "allow"])
    args = parser.parse_args()

    src = Path(args.file)
    if not src.exists():
        raise FileNotFoundError(src)

    project_root = Path(__file__).resolve().parents[2]
    scan_policy = _load_scan_policy(project_root)
    scan = _scan_file(src, policy=scan_policy)
    scan_mode = str(scan_policy.get("mode", "quarantine"))
    ts = datetime.now(timezone.utc)
    day = ts.strftime("%Y-%m-%d")
    stamp = ts.strftime("%Y%m%dT%H%M%SZ")

    out_dir = project_root / "data" / "cv" / "original" / f"source_id={args.source_id}" / f"dt={day}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{stamp}_{src.name}"
    tmp_sha = _sha256(src)
    tmp_ph = _perceptual_hash(src)
    idx = project_root / "data" / "cv" / "cv_index.csv"
    idx.parent.mkdir(parents=True, exist_ok=True)
    existing_rows = _load_index_rows(idx)
    dedup_status = "unique"
    dedup_ref = ""
    duplicate_exact = next((r for r in reversed(existing_rows) if r.get("sha256") == tmp_sha), None)
    duplicate_sim = None
    if duplicate_exact is None:
        for r in reversed(existing_rows):
            ph_old = (r.get("perceptual_hash") or "").strip()
            if not ph_old:
                continue
            if r.get("symbol") != args.symbol or r.get("timeframe") != args.timeframe:
                continue
            if _hamming_hex(tmp_ph, ph_old) <= int(args.dedup_hamming_threshold):
                duplicate_sim = r
                break
    if duplicate_exact:
        dedup_status = "duplicate_exact"
        dedup_ref = duplicate_exact.get("original_file", "")
    elif duplicate_sim:
        dedup_status = "duplicate_similar"
        dedup_ref = duplicate_sim.get("original_file", "")

    should_store = True
    if dedup_status != "unique" and args.dedup_policy in {"skip", "merge"}:
        should_store = False
    if should_store:
        shutil.copy2(src, out_file)
        sha = _sha256(out_file)
        ph = _perceptual_hash(out_file)
    else:
        out_file = Path(dedup_ref) if dedup_ref else src
        sha = tmp_sha
        ph = tmp_ph
    metadata = {
        "source_id": args.source_id,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "timestamp_utc": ts.isoformat(),
        "original_file": str(out_file),
        "sha256": sha,
        "perceptual_hash": ph,
        "dedup_status": dedup_status,
        "dedup_policy": args.dedup_policy,
        "dedup_ref": dedup_ref,
        "pipeline_version": "cv_ingest_v1",
        "scanner_status": scan.status,
        "scanner_reason": scan.reason,
        "scanner_details": scan.details,
        "scanner_mode": scan_mode,
        "allowed_for_cv": scan.status in {"clean", "disabled"} or scan_mode == "report",
    }
    quarantine_file = ""
    if scan.status == "suspicious" and scan_mode == "quarantine":
        quarantine_dir = project_root / "data" / "quarantine" / "cv" / f"source_id={args.source_id}" / f"dt={day}"
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        quarantine_file = str(quarantine_dir / f"{stamp}_{src.name}")
        shutil.copy2(src, quarantine_file)
        metadata["quarantine_file"] = quarantine_file
        metadata["allowed_for_cv"] = False
        metadata["dedup_status"] = "scanner_quarantined"
        metadata["dedup_ref"] = ""
        dedup_status = "scanner_quarantined"
        dedup_ref = ""
    elif scan.status == "suspicious" and scan_mode == "block":
        metadata["allowed_for_cv"] = False
        metadata["dedup_status"] = "scanner_blocked"
        metadata["dedup_ref"] = ""
        dedup_status = "scanner_blocked"
        dedup_ref = ""

    if not bool(metadata["allowed_for_cv"]):
        should_store = False
        out_file = Path(metadata.get("quarantine_file", "")) if metadata.get("quarantine_file") else src
        sha = tmp_sha
        ph = tmp_ph
        metadata["original_file"] = str(out_file)
        metadata["sha256"] = sha
        metadata["perceptual_hash"] = ph

    meta_path = out_dir / f"{stamp}_metadata.json"
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    headers = [
        "timestamp_utc",
        "source_id",
        "symbol",
        "timeframe",
        "original_file",
        "sha256",
        "perceptual_hash",
        "dedup_status",
        "dedup_ref",
        "scanner_status",
        "scanner_reason",
        "allowed_for_cv",
        "quarantine_file",
        "metadata_file",
    ]
    row_dict = {
        "timestamp_utc": ts.isoformat(),
        "source_id": args.source_id,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "original_file": str(out_file),
        "sha256": sha,
        "perceptual_hash": ph,
        "dedup_status": dedup_status,
        "dedup_ref": dedup_ref,
        "scanner_status": scan.status,
        "scanner_reason": scan.reason,
        "allowed_for_cv": str(bool(metadata["allowed_for_cv"])).lower(),
        "quarantine_file": quarantine_file,
        "metadata_file": str(meta_path),
    }
    existing_rows_dict = existing_rows
    if existing_rows_dict:
        # Rewrite with migrated schema to keep CSV shape stable.
        with idx.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=headers)
            w.writeheader()
            for r in existing_rows_dict:
                merged = {h: r.get(h, "") for h in headers}
                w.writerow(merged)
            w.writerow(row_dict)
    else:
        with idx.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=headers)
            w.writeheader()
            w.writerow(row_dict)

    audit_event(
        project_root,
        event="cv_ingest_completed",
        payload={
            "source_id": args.source_id,
            "symbol": args.symbol,
            "timeframe": args.timeframe,
            "file": str(out_file),
            "dedup_status": dedup_status,
            "dedup_policy": args.dedup_policy,
            "dedup_ref": dedup_ref,
            "scanner_status": scan.status,
            "scanner_reason": scan.reason,
            "scanner_mode": scan_mode,
            "allowed_for_cv": bool(metadata["allowed_for_cv"]),
            "quarantine_file": quarantine_file,
        },
    )
    print(
        json.dumps(
            {
                "original_file": str(out_file),
                "metadata_file": str(meta_path),
                "index_file": str(idx),
                "dedup_status": dedup_status,
                "dedup_ref": dedup_ref,
                "stored_new_copy": should_store,
                "scanner_status": scan.status,
                "scanner_reason": scan.reason,
                "scanner_mode": scan_mode,
                "allowed_for_cv": bool(metadata["allowed_for_cv"]),
                "quarantine_file": quarantine_file,
            }
        )
    )
    if scan.status == "suspicious" and scan_mode == "block":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
