from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


def _utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        for line in lines:
            f.write(str(line).rstrip("\n"))
            f.write("\n")


def main() -> int:
    p = argparse.ArgumentParser(description="Append one entry to ACTIVE_WORK_ITEMS and/or CHANGELOG chronologies.")
    p.add_argument("--project-root", default=".")
    p.add_argument("--active-line", default="", help="Single markdown table row to append to ACTIVE_WORK_ITEMS_RU.md")
    p.add_argument("--changelog-header", default="", help="Header line for changelog block, e.g. ### [..] ...")
    p.add_argument(
        "--changelog-line",
        action="append",
        default=[],
        help="One changelog body line; may be provided multiple times.",
    )
    p.add_argument("--tag", default="", help="Optional tag included in no-op/status output.")
    args = p.parse_args()

    root = Path(args.project_root).resolve()
    active_path = root / "docs" / "ACTIVE_WORK_ITEMS_RU.md"
    changelog_path = root / "docs" / "CHANGELOG_CHRONOLOGY_RU.md"

    wrote_active = False
    wrote_changelog = False

    active_line = str(args.active_line or "").rstrip("\n")
    if active_line:
        _append_lines(active_path, [active_line])
        wrote_active = True

    header = str(args.changelog_header or "").rstrip("\n")
    body = [str(x).rstrip("\n") for x in list(args.changelog_line or [])]
    if header:
        lines = ["", header]
        lines.extend(body)
        _append_lines(changelog_path, lines)
        wrote_changelog = True

    print(
        {
            "status": "ok",
            "tag": str(args.tag or ""),
            "utc": _utc_iso(),
            "wrote_active": wrote_active,
            "wrote_changelog": wrote_changelog,
            "active_path": str(active_path),
            "changelog_path": str(changelog_path),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
