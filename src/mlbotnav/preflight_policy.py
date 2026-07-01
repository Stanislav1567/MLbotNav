from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


DEFAULT_PREFLIGHT_POLICY: dict[str, Any] = {
    "preflight": {
        "raw": {
            "layer": "raw",
            "min_train_rows": 900,
            "n_folds": 2,
            "horizons_grid": "1,2,3,4,6,8,12",
        },
        "core": {
            "layer": "core",
            "require_full_coverage": True,
        },
    }
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)  # type: ignore[arg-type]
        else:
            out[k] = v
    return out


def _to_int(value: Any, *, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return int(default)


def _to_bool(value: Any, *, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return bool(default)
    if isinstance(value, (int, float)):
        return bool(value)
    s = str(value).strip().lower()
    if s in {"1", "true", "yes", "y", "on"}:
        return True
    if s in {"0", "false", "no", "n", "off"}:
        return False
    return bool(default)


def load_preflight_policy(project_root: Path, *, policy_path: str = "configs/preflight_policy.yaml") -> dict[str, Any]:
    merged = dict(DEFAULT_PREFLIGHT_POLICY)
    p = Path(policy_path)
    if not p.is_absolute():
        p = project_root / p
    if not p.exists():
        return merged
    try:
        cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return merged
    if not isinstance(cfg, dict):
        return merged
    return _deep_merge(merged, cfg)


def get_raw_preflight_cfg(project_root: Path, *, policy_path: str = "configs/preflight_policy.yaml") -> dict[str, Any]:
    cfg = load_preflight_policy(project_root, policy_path=policy_path)
    raw = (((cfg.get("preflight") or {}).get("raw")) or {})
    if not isinstance(raw, dict):
        raw = {}
    return {
        "layer": str(raw.get("layer", "raw")),
        "min_train_rows": _to_int(raw.get("min_train_rows", 900), default=900),
        "n_folds": _to_int(raw.get("n_folds", 2), default=2),
        "horizons_grid": str(raw.get("horizons_grid", "1,2,3,4,6,8,12")),
    }


def get_core_preflight_cfg(project_root: Path, *, policy_path: str = "configs/preflight_policy.yaml") -> dict[str, Any]:
    cfg = load_preflight_policy(project_root, policy_path=policy_path)
    core = (((cfg.get("preflight") or {}).get("core")) or {})
    if not isinstance(core, dict):
        core = {}
    return {
        "layer": str(core.get("layer", "core")),
        "require_full_coverage": _to_bool(core.get("require_full_coverage", True), default=True),
    }


def resolve_preflight_runtime_args(
    project_root: Path,
    *,
    policy_path: str,
    min_train_rows: int,
    n_folds: int,
    horizons_grid: str,
    legacy_min_train_rows: int,
    legacy_n_folds: int,
    legacy_horizons_grid: str,
) -> dict[str, Any]:
    raw = get_raw_preflight_cfg(project_root, policy_path=policy_path)
    out_min = int(min_train_rows)
    out_folds = int(n_folds)
    out_hg = str(horizons_grid)
    if int(min_train_rows) == int(legacy_min_train_rows):
        out_min = int(raw["min_train_rows"])
    if int(n_folds) == int(legacy_n_folds):
        out_folds = int(raw["n_folds"])
    if str(horizons_grid).strip() == str(legacy_horizons_grid).strip():
        out_hg = str(raw["horizons_grid"])
    return {
        "min_train_rows": out_min,
        "n_folds": out_folds,
        "horizons_grid": out_hg,
        "raw_layer": str(raw["layer"]),
    }
