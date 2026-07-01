from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


_PASSPORT_ID_RE = re.compile(r"^F(\d{3})(?:_F(\d{3}))?$")


def _passport_sort_key(value: str) -> tuple[int, str]:
    text = str(value or "").strip()
    match = _PASSPORT_ID_RE.match(text)
    if not match:
        return (9999, text)
    return (int(match.group(1)), text)


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise RuntimeError(f"YAML root must be a mapping: {path}")
    return data


def build_block_manifest(*, project_root: Path, block_id: str) -> dict[str, Any]:
    block_key = str(block_id or "").strip().upper()
    if not re.fullmatch(r"B\d{3}", block_key):
        raise ValueError(f"BlockId must look like B001, got: {block_id!r}")

    registry_path = project_root / "configs" / "calibration_action_passports.yaml"
    registry = _load_yaml(registry_path)
    blocks = registry.get("blocks")
    if not isinstance(blocks, dict) or block_key not in blocks:
        raise KeyError(f"Block not found in registry: {block_key}")
    block = blocks[block_key]
    if not isinstance(block, dict):
        raise RuntimeError(f"Invalid block payload: {block_key}")

    active_passports = block.get("active_passports")
    if not isinstance(active_passports, dict):
        raise RuntimeError(f"Block has no active_passports: {block_key}")

    rows: list[dict[str, Any]] = []
    diagnostic_rows: list[str] = []
    for passport_id, payload in active_passports.items():
        pid = str(passport_id).strip()
        if not pid.startswith("F"):
            diagnostic_rows.append(pid)
            continue
        item = payload if isinstance(payload, dict) else {}
        matrix_rel = str(item.get("active_matrix_path", "")).strip()
        if not matrix_rel:
            raise RuntimeError(f"Passport has no active_matrix_path: {block_key}/{pid}")
        matrix_path = project_root / matrix_rel
        if not matrix_path.exists():
            raise FileNotFoundError(f"Matrix not found for {block_key}/{pid}: {matrix_rel}")
        rows.append(
            {
                "passport_id": pid,
                "action_id": str(item.get("action_id", "")),
                "action_type": str(item.get("action_type", "")),
                "feature_key": str(item.get("feature_key", "")),
                "matrix_path": matrix_rel,
                "runtime_action_columns": list(item.get("runtime_action_columns") or []),
            }
        )

    rows.sort(key=lambda x: _passport_sort_key(str(x.get("passport_id", ""))))
    mode = "single_passport_block" if len(rows) == 1 else "family_solo_selection"
    return {
        "status": "BLOCK_FAMILY_MANIFEST_READY",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "block_id": block_key,
        "block_key": str(block.get("block_key", "")),
        "name_en": str(block.get("name_en", "")),
        "mode": mode,
        "selection_policy": "reachable_tradeful_positive_oos_first",
        "combination_policy": "solo_f_selection_only",
        "diagnostic_only_passports": diagnostic_rows,
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a block-family solo-selection manifest from the passport registry.")
    parser.add_argument("--project-root", default=".", help="Project root.")
    parser.add_argument("--block-id", required=True, help="Block id, for example B001.")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    manifest = build_block_manifest(project_root=project_root, block_id=str(args.block_id))
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
