from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


MOJIBAKE_TOKENS = (
    "\u0403",
    "\u040c",
    "\u040f",
    "\u0402",
    "\u0452",
    "\u0453",
    "\u0454",
    "\u045e",
    "\u045c",
    "\u045f",
)

# Secondary heuristic for cp1251/cp866 mojibake rendered as UTF-8.
MOJIBAKE_LEAD_ORDS = {0x0420, 0x0421}  # 'Р', 'С'
MOJIBAKE_FOLLOW_ORDS = (
    set(range(0x00A0, 0x00C0))
    | set(range(0x0400, 0x0410))
    | set(range(0x0450, 0x0460))
    | set(range(0x2013, 0x203B))
    | {0x20AC, 0x2116}
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iter_targets(root: Path) -> Iterable[Path]:
    seen: set[str] = set()

    def _emit(path: Path) -> Iterable[Path]:
        key = str(path.resolve())
        if key in seen:
            return []
        seen.add(key)
        return [path]

    for rel in ("docs", "AKFP", "APTuna", "configs", "src", "tests"):
        base = root / rel
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix.lower() in {".md", ".py", ".yaml", ".yml", ".json"}:
                for item in _emit(p):
                    yield item
    for p in root.glob("*"):
        if p.is_file() and p.suffix.lower() in {".md", ".py", ".yaml", ".yml", ".json", ".ps1", ".txt"}:
            for item in _emit(p):
                yield item
    for p in root.glob("run_*.ps1"):
        if p.is_file():
            for item in _emit(p):
                yield item
    req = root / "requirements.txt"
    if req.exists():
        for item in _emit(req):
            yield item


def file_scan(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
        utf8_ok = True
    except UnicodeDecodeError:
        return {
            "file": str(path),
            "utf8_ok": False,
            "qmarks_3plus": 0,
            "mojibake_score": 0,
            "size_bytes": path.stat().st_size,
        }

    qmarks_3plus = text.count("???")
    mojibake_score = sum(text.count(tok) for tok in MOJIBAKE_TOKENS)
    mojibake_pair_score = 0
    for i in range(len(text) - 1):
        lead = ord(text[i])
        follow = ord(text[i + 1])
        if lead in MOJIBAKE_LEAD_ORDS and follow in MOJIBAKE_FOLLOW_ORDS:
            mojibake_pair_score += 1
    if mojibake_pair_score >= 4:
        mojibake_score += mojibake_pair_score

    if path.name == "text_guard.py":
        qmarks_3plus = 0
        mojibake_score = 0

    return {
        "file": str(path),
        "utf8_ok": utf8_ok,
        "qmarks_3plus": qmarks_3plus,
        "mojibake_score": mojibake_score,
        "size_bytes": path.stat().st_size,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Text integrity guard for core project files.")
    parser.add_argument("--out-dir", default="reports/qa_gate", help="Where to write guard report JSON.")
    parser.add_argument(
        "--allow-qmarks-in",
        nargs="*",
        default=[],
        help="Optional path fragments where ??? is tolerated.",
    )
    args = parser.parse_args()

    root = Path.cwd()
    rows = [file_scan(p) for p in iter_targets(root)]
    rows.sort(key=lambda r: r["file"])

    suspects = []
    allow_qmarks_in = tuple(args.allow_qmarks_in)
    for r in rows:
        file_path = r["file"]
        qmark_hit = r["qmarks_3plus"] > 0 and not any(fragment in file_path for fragment in allow_qmarks_in)
        if (not r["utf8_ok"]) or qmark_hit or r["mojibake_score"] > 0:
            suspects.append(r)

    now = utc_now()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"recovery_r5_text_guard_{now.strftime('%Y%m%dT%H%M%SZ')}.json"

    payload = {
        "status": "PASS" if not suspects else "FAIL",
        "generated_at_utc": now.isoformat(),
        "scope": "docs+AKFP+APTuna+configs+src+tests+root_text_files+run_*.ps1+requirements.txt",
        "scanned_files": len(rows),
        "suspect_files": len(suspects),
        "top_suspects": sorted(
            suspects,
            key=lambda x: (x["mojibake_score"], x["qmarks_3plus"], int(not x["utf8_ok"])),
            reverse=True,
        )[:50],
    }

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report_path": str(out_path), "status": payload["status"], "suspect_files": payload["suspect_files"]}))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
