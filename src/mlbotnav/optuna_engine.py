from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


def _read_dotenv_key_values(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return out
    for raw in text.splitlines():
        line = str(raw).strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        k = str(key).strip()
        if not k:
            continue
        v = str(value).strip()
        if len(v) >= 2 and ((v[0] == '"' and v[-1] == '"') or (v[0] == "'" and v[-1] == "'")):
            v = v[1:-1]
        out[k] = v
    return out


def load_optuna_engine_config(
    project_root: Path,
    *,
    rel_path: str = "configs/optuna_engine.yaml",
) -> dict[str, Any]:
    path = (project_root / rel_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Optuna engine config not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Invalid yaml mapping in: {path}")
    return dict(data.get("optuna") or {})


def resolve_storage_url(
    project_root: Path,
    cfg: dict[str, Any],
    *,
    env: dict[str, str] | None = None,
) -> str:
    source_env = env or os.environ
    storage = dict(cfg.get("storage") or {})
    mode = str(storage.get("mode", "postgres")).strip().lower()
    if mode == "postgres":
        direct_url = str(storage.get("url", "")).strip()
        if direct_url:
            return direct_url
        url_env = str(storage.get("url_env", "OPTUNA_STORAGE_URL")).strip()
        candidate_envs: list[str] = [url_env, "OPTUNA_STORAGE_URL", "POSTGRES_DSN", "DATABASE_URL"]
        seen: set[str] = set()
        for key in candidate_envs:
            k = str(key or "").strip()
            if not k or k in seen:
                continue
            seen.add(k)
            url = str(source_env.get(k, "")).strip()
            if url:
                return url
        dotenv_values = _read_dotenv_key_values((project_root / ".env").resolve())
        for key in candidate_envs:
            k = str(key or "").strip()
            if not k:
                continue
            url = str(dotenv_values.get(k, "")).strip()
            if url:
                return url
        require_postgres = bool(storage.get("require_postgres", False))
        if require_postgres:
            dotenv_path = (project_root / ".env").resolve()
            keys_csv = ", ".join(candidate_envs)
            raise RuntimeError(
                "Postgres storage is required, but DSN was not found. "
                f"Set one of: {keys_csv}. Checked env and {dotenv_path}."
            )
    sqlite_rel = str(storage.get("sqlite_fallback_path", "reports/optuna/optuna_local.db")).strip()
    sqlite_path = (project_root / sqlite_rel).resolve()
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{sqlite_path.as_posix()}"


def enforce_storage_parallel_compat(
    *,
    storage_url: str,
    n_jobs: int,
) -> tuple[int, dict[str, Any]]:
    requested = int(n_jobs)
    effective = max(1, requested)
    scheme = str(storage_url).split(":", 1)[0].strip().lower()
    reason = ""
    forced = False
    # TZ v1 contract: sqlite fallback is allowed only with single worker.
    if scheme == "sqlite" and effective != 1:
        effective = 1
        forced = True
        reason = "sqlite_single_worker_enforced"
    return effective, {
        "storage_scheme": scheme,
        "requested_n_jobs": requested,
        "effective_n_jobs": effective,
        "forced_single_worker": forced,
        "reason": reason,
    }


def build_study_plan(
    *,
    contour_id: str,
    test_day: str,
    cfg: dict[str, Any],
    symbol: str | None = None,
    timeframe: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    direction = str(cfg.get("direction", "maximize")).strip().lower()
    if direction not in {"maximize", "minimize"}:
        direction = "maximize"
    seed = int(cfg.get("seed", 20260526))
    scope = "_".join(
        [
            str(symbol or "symbol"),
            str(timeframe or "tf"),
            str(start_date or "start"),
            str(end_date or "end"),
            str(test_day or "test"),
        ]
    )
    name = f"optuna_{contour_id}_{scope}"
    return {
        "study_name": name,
        "direction": direction,
        "n_trials": int(cfg.get("n_trials", 200)),
        "timeout_sec": int(cfg.get("timeout_sec", 7200)),
        "n_jobs": int(cfg.get("n_jobs", 1)),
        "seed": seed,
        "sampler": dict(cfg.get("sampler") or {}),
        "pruner": dict(cfg.get("pruner") or {}),
        "objective": dict(cfg.get("objective") or {}),
        "resources": dict(cfg.get("resources") or {}),
    }


def resolve_stage_profile(
    *,
    cfg: dict[str, Any],
    stage: str,
) -> dict[str, Any]:
    stages = dict(cfg.get("stages") or {})
    key = str(stage or "").strip().upper()
    if key not in {"A", "B", "C"}:
        return {}
    prof = stages.get(key)
    if isinstance(prof, dict):
        return dict(prof)
    return {}


def apply_stage_overrides(
    *,
    study_plan: dict[str, Any],
    stage_profile: dict[str, Any],
) -> dict[str, Any]:
    out = dict(study_plan or {})
    prof = dict(stage_profile or {})
    if "n_trials" in prof:
        out["n_trials"] = int(prof.get("n_trials"))
    if "timeout_sec" in prof:
        out["timeout_sec"] = int(prof.get("timeout_sec"))
    return out
