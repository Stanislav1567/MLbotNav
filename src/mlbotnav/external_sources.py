from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def _collect_files_from_dir(root: Path, patterns: list[str]) -> list[str]:
    found: set[str] = set()
    if not root.exists():
        return []
    for pat in patterns:
        for p in root.rglob(pat):
            if p.is_file():
                found.add(str(p.resolve()))
    return sorted(found)


def detect_external_sources(project_root: Path) -> dict[str, Any]:
    """
    Runtime detector for optional external data sources used by
    orderbook/microstructure hypotheses.
    """
    candidate_dirs = [
        project_root / "data" / "orderbook",
        project_root / "data" / "microstructure",
        project_root / "reports" / "orderbook",
        project_root / "reports" / "microstructure",
        project_root / "cache" / "orderbook",
        project_root / "cache" / "microstructure",
    ]
    patterns = [
        "*orderbook*",
        "*l1*",
        "*l50*",
        "*spread*",
        "*delta*",
        "*imbalance*",
    ]
    files: list[str] = []
    for d in candidate_dirs:
        files.extend(_collect_files_from_dir(d, patterns))
    files = sorted(set(files))

    env = {
        k: os.environ.get(k)
        for k in (
            "ORDERBOOK_SOURCE_PATH",
            "MICROSTRUCTURE_SOURCE_PATH",
            "ORDERBOOK_ENABLED",
            "MICROSTRUCTURE_ENABLED",
        )
        if os.environ.get(k)
    }

    orderbook_path = str(os.environ.get("ORDERBOOK_SOURCE_PATH", "")).strip()
    micro_path = str(os.environ.get("MICROSTRUCTURE_SOURCE_PATH", "")).strip()
    orderbook_path_ok = bool(orderbook_path) and Path(orderbook_path).exists()
    micro_path_ok = bool(micro_path) and Path(micro_path).exists()
    orderbook_enabled = str(os.environ.get("ORDERBOOK_ENABLED", "")).strip().lower() in {"1", "true", "yes", "on"}
    micro_enabled = str(os.environ.get("MICROSTRUCTURE_ENABLED", "")).strip().lower() in {"1", "true", "yes", "on"}

    lower_files = [f.lower() for f in files]
    has_orderbook_files = any(("orderbook" in f or "l1" in f or "l50" in f or "depth" in f or "book" in f) for f in lower_files)
    has_microstructure_files = any(("microstructure" in f or "spread" in f or "delta" in f) for f in lower_files)

    generic_detected = bool(files) or bool(env)
    source_ready = {
        "orderbook_l1_l50": bool(orderbook_path_ok or has_orderbook_files or orderbook_enabled),
        "microstructure_spread_delta": bool(micro_path_ok or has_microstructure_files or micro_enabled),
    }

    return {
        "source_detected": bool(generic_detected),
        "source_files": files,
        "source_files_total": len(files),
        "source_env": env,
        "has_orderbook_files": bool(has_orderbook_files),
        "has_microstructure_files": bool(has_microstructure_files),
        "source_ready": source_ready,
    }
