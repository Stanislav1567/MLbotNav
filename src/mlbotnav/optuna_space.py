from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

from mlbotnav.backtest import _trend_filter_required_columns


class OptunaSpaceCompileError(ValueError):
    pass


_RE_BIN = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(<=|>=|<|>|=)\s*([A-Za-z_][A-Za-z0-9_]*|[-+]?\d+(?:\.\d+)?)\s*$")
_RE_DIFF = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*-\s*([A-Za-z_][A-Za-z0-9_]*)\s*(<=|>=|<|>|=)\s*([-+]?\d+(?:\.\d+)?)\s*$"
)
_RE_PLUS = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(<=|>=|<|>|=)\s*([A-Za-z_][A-Za-z0-9_]*)\s*\+\s*([-+]?\d+(?:\.\d+)?)\s*$"
)
_RE_CHAIN = re.compile(
    r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*(<=|<|>=|>)\s*([A-Za-z_][A-Za-z0-9_]*)\s*(<=|<|>=|>)\s*([A-Za-z_][A-Za-z0-9_]*)\s*$"
)


LONG_ONLY_HYPOTHESES = {
    "ema_stack_bull",
    "swing_hl_hh_long",
    "max_low_pullback_long",
}

SHORT_ONLY_HYPOTHESES = {
    "swing_lh_ll_short",
}

COLUMN_BLOCK_ALIASES = {
    "ema20": "trend_momentum",
    "ema50": "trend_momentum",
    "ema200": "trend_momentum",
}


def _contour_mode(contour_id: str) -> str:
    cid = str(contour_id or "").strip().lower()
    if "long_only" in cid:
        return "long_only"
    if "short_only" in cid:
        return "short_only"
    return "both"


def _hypothesis_allowed_for_contour(row: dict[str, Any], *, contour_id: str) -> bool:
    mode = _contour_mode(contour_id)
    if mode == "both":
        return True

    explicit_modes = row.get("signal_modes")
    if isinstance(explicit_modes, list):
        normalized = {str(x).strip().lower() for x in explicit_modes}
        if normalized:
            if "both" in normalized:
                return True
            return mode in normalized

    name = str(row.get("hypothesis", "")).strip().lower()
    if not name:
        return False

    if mode == "long_only" and name in SHORT_ONLY_HYPOTHESES:
        return False
    if mode == "short_only" and name in LONG_ONLY_HYPOTHESES:
        return False

    if mode == "long_only" and "short" in name:
        return False
    if mode == "short_only" and "long" in name:
        return False
    return True


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    txt = str(value).strip().lower()
    return txt in {"1", "true", "yes", "on"}


def _as_float(value: Any, *, field: str) -> float:
    try:
        return float(value)
    except Exception as e:
        raise OptunaSpaceCompileError(f"Invalid float for '{field}': {value}") from e


def _as_int(value: Any, *, field: str) -> int:
    try:
        return int(value)
    except Exception as e:
        raise OptunaSpaceCompileError(f"Invalid int for '{field}': {value}") from e


def _to_number(value: Any) -> float:
    if isinstance(value, bool):
        return float(int(value))
    return float(value)


def _cmp_ok(left: Any, op: str, right: Any) -> bool:
    if op == "=":
        return str(left) == str(right)
    lv = _to_number(left)
    rv = _to_number(right)
    if op == "<":
        return lv < rv
    if op == "<=":
        return lv <= rv
    if op == ">":
        return lv > rv
    if op == ">=":
        return lv >= rv
    return False


def evaluate_runtime_constraints_detailed(constraints: list[str], values: dict[str, Any]) -> dict[str, Any]:
    failed: list[str] = []
    skipped_missing_values: list[str] = []
    skipped_unparsed: list[str] = []
    evaluated: list[str] = []
    val = dict(values or {})
    for raw in list(constraints or []):
        expr = str(raw).strip()
        if not expr:
            continue

        m = _RE_CHAIN.match(expr)
        if m:
            a, op1, b, op2, c = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
            if a not in val or b not in val or c not in val:
                skipped_missing_values.append(expr)
                continue
            evaluated.append(expr)
            ok1 = _cmp_ok(val[a], op1, val[b])
            ok2 = _cmp_ok(val[b], op2, val[c])
            if not (ok1 and ok2):
                failed.append(expr)
            continue

        m = _RE_DIFF.match(expr)
        if m:
            a, b, op, cst = m.group(1), m.group(2), m.group(3), m.group(4)
            if a not in val or b not in val:
                skipped_missing_values.append(expr)
                continue
            left = _to_number(val[a]) - _to_number(val[b])
            evaluated.append(expr)
            if not _cmp_ok(left, op, float(cst)):
                failed.append(expr)
            continue

        m = _RE_PLUS.match(expr)
        if m:
            a, op, b, cst = m.group(1), m.group(2), m.group(3), m.group(4)
            if a not in val or b not in val:
                skipped_missing_values.append(expr)
                continue
            right = _to_number(val[b]) + float(cst)
            evaluated.append(expr)
            if not _cmp_ok(_to_number(val[a]), op, right):
                failed.append(expr)
            continue

        m = _RE_BIN.match(expr)
        if m:
            left_name, op, right_token = m.group(1), m.group(2), m.group(3)
            if left_name not in val:
                skipped_missing_values.append(expr)
                continue
            if right_token in val:
                right_value = val[right_token]
            else:
                try:
                    right_value = float(right_token)
                except Exception:
                    if op == "=":
                        right_value = str(right_token)
                    else:
                        # Right-side symbolic parameter is not available in runtime values.
                        # Treat as unresolved runtime dependency, not as hard parser error.
                        skipped_missing_values.append(expr)
                        continue
            evaluated.append(expr)
            if not _cmp_ok(val[left_name], op, right_value):
                failed.append(expr)
            continue
        skipped_unparsed.append(expr)
    return {
        "failed": failed,
        "evaluated": evaluated,
        "skipped_missing_values": skipped_missing_values,
        "skipped_unparsed": skipped_unparsed,
        "total": len(list(constraints or [])),
    }


def evaluate_runtime_constraints(constraints: list[str], values: dict[str, Any]) -> list[str]:
    return list(evaluate_runtime_constraints_detailed(constraints, values).get("failed") or [])


def _passport_mode_config(matrix: dict[str, Any]) -> dict[str, Any]:
    cfg = matrix.get("passport_mode") or {}
    return cfg if isinstance(cfg, dict) else {}


def _load_passport_registry(matrix: dict[str, Any], registry_path_raw: str) -> tuple[dict[str, Any], Path]:
    registry_path = Path(str(registry_path_raw or "").strip())
    if not str(registry_path):
        raise OptunaSpaceCompileError("passport_mode registry_path must not be empty")
    if not registry_path.is_absolute():
        project_root_raw = matrix.get("__project_root")
        if project_root_raw:
            registry_path = Path(str(project_root_raw)) / registry_path
        else:
            registry_path = Path.cwd() / registry_path
    registry_path = registry_path.resolve()
    if not registry_path.exists():
        raise OptunaSpaceCompileError(f"passport registry not found: {registry_path}")
    with registry_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise OptunaSpaceCompileError(f"passport registry must be a mapping: {registry_path}")
    return data, registry_path


def _registry_passport_entry(
    registry: dict[str, Any],
    *,
    block_id: str,
    passport_id: str,
) -> dict[str, Any]:
    blocks = registry.get("blocks") or {}
    if not isinstance(blocks, dict):
        raise OptunaSpaceCompileError("passport registry blocks must be a mapping")
    block = blocks.get(str(block_id))
    if not isinstance(block, dict):
        raise OptunaSpaceCompileError(f"passport registry block not found: {block_id}")
    passports = block.get("active_passports") or {}
    if not isinstance(passports, dict):
        raise OptunaSpaceCompileError(f"passport registry active_passports must be a mapping: {block_id}")
    passport = passports.get(str(passport_id))
    if not isinstance(passport, dict):
        raise OptunaSpaceCompileError(f"active passport not found in registry: {block_id}.{passport_id}")
    return passport


def _validate_passport_registry_match(matrix: dict[str, Any], cfg: dict[str, Any], allowed: set[str]) -> dict[str, Any]:
    registry_path_raw = str(cfg.get("registry_path", "") or "").strip()
    if not registry_path_raw:
        return {}
    block_id = str(cfg.get("registry_block_id", "") or "").strip()
    passport_id = str(cfg.get("registry_passport_id", "") or cfg.get("action_passport_id", "") or "").strip()
    if not block_id or not passport_id:
        raise OptunaSpaceCompileError("passport_mode registry_path requires registry_block_id and registry_passport_id")
    registry, registry_path = _load_passport_registry(matrix, registry_path_raw)
    passport = _registry_passport_entry(registry, block_id=block_id, passport_id=passport_id)
    registry_allowed = {
        str(x).strip()
        for x in list(passport.get("allowed_calibration_params") or [])
        if str(x).strip()
    }
    policy = str(cfg.get("policy", "allowlist")).strip().lower() or "allowlist"
    subset_policy = policy in {"subset_allowlist", "allowlist_subset", "registry_subset"}
    allowlist_ok = allowed.issubset(registry_allowed) if subset_policy else allowed == registry_allowed
    if not allowlist_ok:
        raise OptunaSpaceCompileError(
            f"passport registry allowlist mismatch for {block_id}.{passport_id}: "
            f"policy={policy} matrix={sorted(allowed)} registry={sorted(registry_allowed)}"
        )
    matrix_action_id = str(cfg.get("action_id", "") or "").strip()
    registry_action_id = str(passport.get("action_id", "") or "").strip()
    if matrix_action_id and registry_action_id and matrix_action_id != registry_action_id:
        raise OptunaSpaceCompileError(
            f"passport registry action_id mismatch for {block_id}.{passport_id}: "
            f"matrix={matrix_action_id} registry={registry_action_id}"
        )
    matrix_path_raw = str(matrix.get("__matrix_rel_path") or matrix.get("__matrix_path") or "").replace("\\", "/")
    registry_matrix_path = str(passport.get("active_matrix_path", "") or "").replace("\\", "/")
    if registry_matrix_path and matrix_path_raw and not matrix_path_raw.endswith(registry_matrix_path):
        raise OptunaSpaceCompileError(
            f"passport registry active_matrix_path mismatch for {block_id}.{passport_id}: "
            f"matrix={matrix_path_raw} registry={registry_matrix_path}"
        )
    return {
        "registry_path": str(registry_path),
        "registry_block_id": block_id,
        "registry_passport_id": passport_id,
        "registry_action_id": registry_action_id,
        "registry_active_matrix_path": registry_matrix_path,
        "registry_allowlist_policy": policy,
    }


def _validate_passport_mode_params(matrix: dict[str, Any]) -> dict[str, Any]:
    cfg = _passport_mode_config(matrix)
    enabled = _as_bool(cfg.get("enabled", False))
    if not enabled:
        return {"enabled": False}
    allowed = {
        str(x).strip()
        for x in list(cfg.get("allowed_calibration_params") or [])
        if str(x).strip()
    }
    if not allowed:
        raise OptunaSpaceCompileError("passport_mode.enabled requires allowed_calibration_params")

    violations: list[dict[str, Any]] = []
    for section_name in ("feature_rows", "hypothesis_rows", "search_grid_rows"):
        rows = list(matrix.get(section_name) or [])
        for ix, row in enumerate(rows):
            if not isinstance(row, dict):
                continue
            params = list(row.get("params") or [])
            if section_name == "search_grid_rows":
                profile = str(row.get("profile", "")).strip()
                params = [profile] if profile else []
            for param in params:
                name = str(param).strip()
                if name and name not in allowed:
                    violations.append(
                        {
                            "section": section_name,
                            "row_index": ix,
                            "param": name,
                            "action_passport_id": str(cfg.get("action_passport_id", "")).strip(),
                        }
                    )
    if violations:
        raise OptunaSpaceCompileError(f"passport_mode disallowed params: {violations}")
    registry_report = _validate_passport_registry_match(matrix, cfg, allowed)
    return {
        "enabled": True,
        "action_passport_id": str(cfg.get("action_passport_id", "")).strip(),
        "allowed_calibration_params": sorted(allowed),
        "policy": str(cfg.get("policy", "allowlist")).strip() or "allowlist",
        **registry_report,
    }


def load_calibration_matrix(
    project_root: Path,
    *,
    rel_path: str = "configs/calibration_full_matrix_v1.yaml",
) -> dict[str, Any]:
    env_override = str(os.environ.get("MLBOTNAV_CALIBRATION_MATRIX_PATH", "") or "").strip()
    if env_override:
        override_path = Path(env_override)
        path = (override_path if override_path.is_absolute() else (project_root / override_path)).resolve()
        try:
            matrix_rel_path = path.relative_to(project_root.resolve()).as_posix()
        except ValueError:
            matrix_rel_path = str(path.as_posix())
    else:
        path = (project_root / rel_path).resolve()
        matrix_rel_path = str(Path(rel_path).as_posix())
    if not path.exists():
        raise FileNotFoundError(f"Calibration matrix not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise OptunaSpaceCompileError(f"Calibration matrix must be a mapping: {path}")
    data["__matrix_path"] = str(path)
    data["__matrix_rel_path"] = matrix_rel_path
    data["__project_root"] = str(project_root.resolve())
    return data


def expand_profile_values(profile: dict[str, Any]) -> list[float]:
    explicit_values = profile.get("values")
    if explicit_values is not None:
        if not isinstance(explicit_values, list):
            raise OptunaSpaceCompileError("Profile values must be a list")
        out = [round(_as_float(v, field="values"), 10) for v in explicit_values]
        if not out:
            raise OptunaSpaceCompileError("Profile values must not be empty")
        return out
    min_v = _as_float(profile.get("min"), field="min")
    max_v = _as_float(profile.get("max"), field="max")
    step = _as_float(profile.get("step"), field="step")
    if step <= 0.0:
        raise OptunaSpaceCompileError(f"Profile step must be > 0, got {step}")
    if max_v < min_v:
        raise OptunaSpaceCompileError(f"Profile max must be >= min, got min={min_v}, max={max_v}")
    out: list[float] = []
    cur = min_v
    for _ in range(10000):
        if cur > (max_v + 1e-12):
            break
        out.append(round(cur, 10))
        cur += step
    if not out:
        out = [round(min_v, 10)]
    max_anchor = round(max_v, 10)
    if out[-1] != max_anchor:
        out.append(max_anchor)
    expected_count_raw = profile.get("count", None)
    if expected_count_raw is not None:
        expected_count = _as_int(expected_count_raw, field="count")
        if expected_count > 0:
            out = out[:expected_count]
            if out and out[-1] != max_anchor:
                out[-1] = max_anchor
    return out


def _normalize_grid_preset(value: str) -> str:
    preset = str(value or "").strip().lower()
    if preset in {"wide", "medium", "narrow"}:
        return preset
    return "wide"


def _apply_grid_preset(values: list[float], *, preset: str) -> list[float]:
    seq = [float(x) for x in list(values or [])]
    if not seq:
        return []
    mode = _normalize_grid_preset(preset)
    if mode == "wide":
        return list(seq)

    if mode == "medium":
        picked = seq[::2]
        if seq[-1] not in picked:
            picked.append(seq[-1])
        return [float(x) for x in picked]

    # narrow: keep compact center-focused support while preserving range edges.
    n = len(seq)
    idxs = {
        0,
        n - 1,
        int(round((n - 1) * 0.25)),
        int(round((n - 1) * 0.50)),
        int(round((n - 1) * 0.75)),
    }
    out = [seq[i] for i in sorted(i for i in idxs if 0 <= i < n)]
    return [float(x) for x in out]


def _normalize_name_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        raw = [x.strip() for x in value.split(",")]
    elif isinstance(value, (list, tuple, set)):
        raw = [str(x).strip() for x in value]
    else:
        raw = [str(value).strip()]
    out: list[str] = []
    seen: set[str] = set()
    for name in raw:
        if not name or name in seen:
            continue
        seen.add(name)
        out.append(name)
    return out


def _feature_to_blocks_from_rows(feature_rows: list[dict[str, Any]]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for row in list(feature_rows or []):
        if not isinstance(row, dict):
            continue
        block = str(row.get("block", "")).strip()
        feature = str(row.get("feature", "")).strip()
        if not block or not feature:
            continue
        out.setdefault(feature, set()).add(block)
    for feature, block in COLUMN_BLOCK_ALIASES.items():
        out.setdefault(feature, set()).add(block)
    return out


def _hypothesis_required_block_report(
    hypothesis: str,
    *,
    feature_to_blocks: dict[str, set[str]],
) -> dict[str, Any]:
    name = str(hypothesis or "").strip()
    required_columns = list(_trend_filter_required_columns(name))
    required_blocks: set[str] = set()
    unknown_columns: list[str] = []
    for column in required_columns:
        blocks = set(feature_to_blocks.get(str(column), set()))
        if not blocks:
            unknown_columns.append(str(column))
            continue
        required_blocks.update(blocks)
    return {
        "hypothesis": name,
        "required_columns": required_columns,
        "required_blocks": sorted(required_blocks),
        "unknown_columns": sorted(unknown_columns),
    }


def _hypothesis_allowed_for_effective_blocks(
    row: dict[str, Any],
    *,
    effective_feature_blocks: list[str],
    feature_to_blocks: dict[str, set[str]],
) -> tuple[bool, dict[str, Any]]:
    name = str(row.get("hypothesis", "")).strip()
    report = _hypothesis_required_block_report(name, feature_to_blocks=feature_to_blocks)
    allowed_blocks = {str(x).strip() for x in list(effective_feature_blocks or []) if str(x).strip()}
    required_blocks = set(report.get("required_blocks") or [])
    unknown_columns = list(report.get("unknown_columns") or [])

    if name == "none":
        allowed = True
        reason = "universal_none"
    elif unknown_columns:
        allowed = False
        reason = "unknown_required_columns"
    elif not required_blocks:
        allowed = False
        reason = "no_required_block_map"
    elif required_blocks.issubset(allowed_blocks):
        allowed = True
        reason = "required_blocks_within_effective_blocks"
    else:
        allowed = False
        reason = "required_blocks_outside_effective_blocks"

    report["allowed"] = bool(allowed)
    report["reason"] = str(reason)
    report["effective_feature_blocks"] = sorted(allowed_blocks)
    return bool(allowed), report


def compile_optuna_space(
    matrix: dict[str, Any],
    *,
    contour_id: str,
    min_enabled_blocks: int = 1,
    grid_preset: str = "wide",
) -> dict[str, Any]:
    passport_mode_report = _validate_passport_mode_params(matrix)
    switches = dict(matrix.get("optuna_switches") or {})
    block_switches_raw = dict(switches.get("block_switches") or {})
    block_switches = {str(k): _as_bool(v) for k, v in block_switches_raw.items()}

    enabled_blocks = [k for k, v in block_switches.items() if v]
    if len(enabled_blocks) < int(min_enabled_blocks):
        raise OptunaSpaceCompileError(
            f"Enabled blocks ({len(enabled_blocks)}) < min_enabled_blocks ({min_enabled_blocks})"
        )

    context_cfg_raw = switches.get("context_blocks") or {}
    context_cfg = context_cfg_raw if isinstance(context_cfg_raw, dict) else {}
    context_enabled = _as_bool(context_cfg.get("enabled", False))
    context_blocks = _normalize_name_list(context_cfg.get("always_on", [])) if context_enabled else []
    unknown_context_blocks = sorted(x for x in context_blocks if x not in block_switches)
    if unknown_context_blocks:
        raise OptunaSpaceCompileError(f"Unknown context blocks: {unknown_context_blocks}")
    effective_feature_blocks = list(enabled_blocks)
    for block in context_blocks:
        if block not in effective_feature_blocks:
            effective_feature_blocks.append(block)
    effective_feature_block_set = set(effective_feature_blocks)
    hypothesis_switches = switches.get("hypothesis_switches") or {}
    hypothesis_switches = hypothesis_switches if isinstance(hypothesis_switches, dict) else {}
    strict_block_purity = _as_bool(hypothesis_switches.get("strict_block_purity", False))

    feature_rows_all = list(matrix.get("feature_rows") or [])
    feature_to_blocks = _feature_to_blocks_from_rows(
        [row for row in feature_rows_all if isinstance(row, dict)]
    )
    feature_rows: list[dict[str, Any]] = []
    for row in feature_rows_all:
        if not isinstance(row, dict):
            continue
        block = str(row.get("block", "")).strip()
        if not block:
            continue
        if block not in effective_feature_block_set:
            continue
        # Runtime feature set must include enabled-block features plus
        # always-on market context blocks such as volume/volatility.
        # `calibrate/optuna_toggle` only control whether row params are tunable,
        # not whether the feature is present in model input.
        feature_rows.append(row)

    hypothesis_rows_all = list(matrix.get("hypothesis_rows") or [])
    hypothesis_rows: list[dict[str, Any]] = []
    hypothesis_filter_report: list[dict[str, Any]] = []
    for row in hypothesis_rows_all:
        if not isinstance(row, dict):
            continue
        if not _as_bool(row.get("calibrate", False)):
            continue
        if not _as_bool(row.get("optuna_toggle", False)):
            continue
        if not _hypothesis_allowed_for_contour(row, contour_id=str(contour_id)):
            continue
        if strict_block_purity:
            allowed, report = _hypothesis_allowed_for_effective_blocks(
                row,
                effective_feature_blocks=effective_feature_blocks,
                feature_to_blocks=feature_to_blocks,
            )
            hypothesis_filter_report.append(report)
            if not allowed:
                continue
        hypothesis_rows.append(row)

    profile_names: set[str] = set()
    for row in feature_rows + hypothesis_rows:
        for p in (row.get("params") or []):
            profile_names.add(str(p))
    for row in list(matrix.get("search_grid_rows") or []):
        if isinstance(row, dict):
            prof = str(row.get("profile", "")).strip()
            if prof:
                profile_names.add(prof)

    all_profiles = dict(matrix.get("parameter_profiles") or {})
    missing = sorted(x for x in profile_names if x not in all_profiles)
    if missing:
        raise OptunaSpaceCompileError(f"Missing parameter_profiles: {missing}")

    preset_name = _normalize_grid_preset(grid_preset)
    profiles: dict[str, dict[str, Any]] = {}
    for name in sorted(profile_names):
        p = dict(all_profiles[name] or {})
        values_full = expand_profile_values(p)
        values_preset = _apply_grid_preset(values_full, preset=preset_name)
        profiles[name] = {
            **p,
            "values": values_preset,
            "values_wide": values_full,
            "grid_preset": preset_name,
        }

    return {
        "contour_id": str(contour_id),
        "min_enabled_blocks": int(min_enabled_blocks),
        "grid_preset": preset_name,
        "block_switches": block_switches,
        "enabled_blocks": enabled_blocks,
        "context_blocks": context_blocks,
        "effective_feature_blocks": effective_feature_blocks,
        "strict_block_purity": bool(strict_block_purity),
        "passport_mode": passport_mode_report,
        "hypothesis_filter_report": hypothesis_filter_report,
        "feature_rows": feature_rows,
        "hypothesis_rows": hypothesis_rows,
        "profiles": profiles,
        "search_grid_rows": list(matrix.get("search_grid_rows") or []),
        "constraints": list(matrix.get("constraints") or []),
    }
