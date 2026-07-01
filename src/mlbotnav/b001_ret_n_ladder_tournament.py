from __future__ import annotations

import argparse
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from mlbotnav.optuna_space import compile_optuna_space, load_calibration_matrix


PASSPORT_MATRIX_PATHS = {
    "F001": "configs/calibration_matrices/passport_actions/F001_ret1_entry_filter.yaml",
    "F002": "configs/calibration_matrices/passport_actions/F002_ret3_entry_filter.yaml",
    "F003": "configs/calibration_matrices/passport_actions/F003_ret6_entry_filter.yaml",
    "F004": "configs/calibration_matrices/passport_actions/F004_ret12_entry_filter.yaml",
    "F005": "configs/calibration_matrices/passport_actions/F005_ret24_entry_filter.yaml",
}


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _combo_id(passports: tuple[str, ...]) -> str:
    return "B001_RET_N_" + "_".join(passports)


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise RuntimeError(f"YAML root must be a mapping: {path}")
    return data


def _copy_profiles_and_rows(project_root: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for passport_id, rel_path in PASSPORT_MATRIX_PATHS.items():
        matrix = _load_yaml(project_root / rel_path)
        profiles = dict(matrix.get("parameter_profiles") or {})
        rows = list(matrix.get("feature_rows") or [])
        if len(rows) != 1 or not isinstance(rows[0], dict):
            raise RuntimeError(f"Expected one feature row in {rel_path}")
        out[passport_id] = {
            "matrix_path": rel_path,
            "profiles": profiles,
            "feature_row": dict(rows[0]),
        }
    return out


def build_combo_matrix(
    *,
    project_root: Path,
    passports: tuple[str, ...],
    generated_utc: str,
    family_move_values: list[int] | None = None,
    strict_confirmations: int | None = None,
) -> dict[str, Any]:
    source = _copy_profiles_and_rows(project_root)
    parameter_profiles: dict[str, Any] = {}
    feature_rows: list[dict[str, Any]] = []
    allowed_params: list[str] = []
    family_move_enabled = family_move_values is not None

    for passport_id in passports:
        row = dict(source[passport_id]["feature_row"])
        row["calibrate"] = True
        row["optuna_toggle"] = True
        row_params = [str(x).strip() for x in list(row.get("params") or []) if str(x).strip()]
        next_params: list[str] = []
        for param in row_params:
            if family_move_enabled and param.endswith("_move"):
                continue
            parameter_profiles[param] = dict(source[passport_id]["profiles"][param])
            allowed_params.append(param)
            next_params.append(param)
        row["params"] = next_params
        feature_rows.append(row)

    if family_move_enabled:
        values = [int(v) for v in list(family_move_values or []) if int(v) in {-1, 1}]
        if not values:
            raise ValueError("family_move_values must contain -1 or 1")
        parameter_profiles["B001_family_move"] = {
            "values": values,
            "count": len(values),
            "axis": "family_direction",
        }
        allowed_params.append("B001_family_move")

    confirmation_values = list(range(1, len(passports) + 1))
    axis = "n_of_m"
    if strict_confirmations is not None:
        fixed_n = max(1, min(len(passports), int(strict_confirmations)))
        confirmation_values = [fixed_n]
        axis = "strict_all" if fixed_n == len(passports) else "strict_fixed_n"
    parameter_profiles["entry_action_min_confirmations"] = {
        "values": confirmation_values,
        "count": len(confirmation_values),
        "axis": axis,
    }
    allowed_params.append("entry_action_min_confirmations")
    if feature_rows:
        first_params = [str(x).strip() for x in list(feature_rows[0].get("params") or []) if str(x).strip()]
        if family_move_enabled and "B001_family_move" not in first_params:
            first_params = first_params + ["B001_family_move"]
        if "entry_action_min_confirmations" not in first_params:
            feature_rows[0]["params"] = first_params + ["entry_action_min_confirmations"]
        else:
            feature_rows[0]["params"] = first_params

    cid = _combo_id(passports)
    gate_policy = "n_of_m_runtime_action_columns"
    if strict_confirmations is not None and int(strict_confirmations) >= len(passports):
        gate_policy = "strict_all_runtime_action_columns"
    if family_move_enabled:
        gate_policy = "family_unified_" + gate_policy
    return {
        "version": 1,
        "status": "generated_b001_ret_n_ladder_matrix",
        "generated_utc": generated_utc,
        "source_of_truth": {
            "action_passport_registry": "configs/calibration_action_passports.yaml",
            "action_passport": "docs/CALIBRATION_NODE_CURRENT/passports/features/RET_N_F001_F005_strict_passports.md",
            "generator": "src/mlbotnav/b001_ret_n_ladder_tournament.py",
        },
        "passport_mode": {
            "enabled": True,
            "registry_path": "configs/calibration_action_passports.yaml",
            "registry_block_id": "B001",
            "registry_passport_id": "B001_RET_N_TOURNAMENT",
            "action_passport_id": "B001_RET_N_TOURNAMENT",
            "action_id": "B001_RET_N_ALLOW",
            "policy": "subset_allowlist",
            "allowed_calibration_params": allowed_params,
        },
        "tournament": {
            "combo_id": cid,
            "passports": list(passports),
            "combination_size": len(passports),
            "gate_policy": gate_policy,
            "selection_policy": "best_tradeful_oos_first",
            "family_move_enabled": bool(family_move_enabled),
        },
        "notes_ru": [
            f"Generated B001 RET_N tournament matrix: {cid}.",
            "Калибруются только ручки паспортов, входящих в этот состав.",
            "Общий вход разрешается только когда все присутствующие runtime action columns равны 1.",
        ],
        "optuna_switches": {
            "enabled": True,
            "block_switches": {
                "price_volatility": True,
                "trend_momentum": False,
                "volume_flow": False,
                "density_profile": False,
                "structure_ta": False,
                "pattern": False,
            },
            "hypothesis_switches": {
                "enabled": True,
                "strict_block_purity": True,
            },
            "context_blocks": {
                "enabled": False,
                "always_on": [],
                "calibration_policy": "passport_action_only",
                "comparison_policy": "none",
            },
        },
        "grid_presets": {
            "wide": {"description": "full passport profile value range"},
            "medium": {"description": "every second passport value with preserved max"},
            "narrow": {"description": "compact passport value set with preserved min/max anchors"},
        },
        "parameter_profiles": parameter_profiles,
        "feature_rows": feature_rows,
        "hypothesis_rows": [
            {
                "hypothesis": "none",
                "calibrate": True,
                "optuna_toggle": True,
                "params": [],
            }
        ],
        "search_grid_rows": [],
        "constraints": [],
        "backtest_subpassport": {
            "exit_policy": "tp_sl_timeout",
            "timeout_exit_enabled": True,
            "disable_timeout_exit": False,
            "note": "Tournament compares RET_N entry-filter combinations; exits stay baseline.",
        },
    }


def generate_tournament_matrices(
    *,
    project_root: Path,
    output_dir: Path,
    grid_preset: str = "wide",
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_utc = datetime.now(timezone.utc).isoformat()
    manifest_rows: list[dict[str, Any]] = []

    passport_ids = tuple(PASSPORT_MATRIX_PATHS.keys())
    combo_index = 0
    for size in range(1, len(passport_ids) + 1):
        for passports in itertools.combinations(passport_ids, size):
            combo_index += 1
            matrix = build_combo_matrix(project_root=project_root, passports=passports, generated_utc=generated_utc)
            combo_id = str(matrix["tournament"]["combo_id"])
            filename = f"{combo_index:02d}_{combo_id}.yaml"
            path = output_dir / filename
            with path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(matrix, f, allow_unicode=True, sort_keys=False)

            loaded = load_calibration_matrix(project_root, rel_path=str(path.relative_to(project_root).as_posix()))
            space = compile_optuna_space(loaded, contour_id="long_only", min_enabled_blocks=1, grid_preset=grid_preset)
            manifest_rows.append(
                {
                    "index": combo_index,
                    "combo_id": combo_id,
                    "passports": list(passports),
                    "combination_size": size,
                    "matrix_path": str(path.relative_to(project_root).as_posix()),
                    "profiles": sorted(space.get("profiles", {}).keys()),
                    "runtime_gate_policy": "N_OF_M_present_action_columns",
                }
            )

    manifest = {
        "status": "B001_RET_N_LADDER_MATRICES_READY",
        "generated_utc": generated_utc,
        "output_dir": str(output_dir.relative_to(project_root).as_posix()),
        "combinations_count": len(manifest_rows),
        "selection_policy": "best_tradeful_oos_first",
        "rows": manifest_rows,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path = output_dir / "manifest_RU.md"
    md_lines = [
        "# B001 RET_N Ladder Tournament",
        "",
        f"Status: `{manifest['status']}`.",
        "",
        "Правило: каждая строка это один диагностический состав B001. Backtest разрешает вход, когда сработало минимум `entry_action_min_confirmations` из присутствующих `*_ALLOW` колонок.",
        "",
        "| # | Combo | Passports | Profiles | Matrix |",
        "|---:|---|---|---|---|",
    ]
    for row in manifest_rows:
        md_lines.append(
            "| {index} | `{combo_id}` | `{passports}` | `{profiles}` | `{matrix_path}` |".format(
                index=row["index"],
                combo_id=row["combo_id"],
                passports=",".join(row["passports"]),
                profiles=",".join(row["profiles"]),
                matrix_path=row["matrix_path"],
            )
        )
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    manifest["manifest_path"] = str(manifest_path.relative_to(project_root).as_posix())
    manifest["manifest_ru_path"] = str(md_path.relative_to(project_root).as_posix())
    return manifest


def generate_family_unified_matrix(
    *,
    project_root: Path,
    output_dir: Path,
    family_move_values: list[int],
    strict_confirmations: int = 5,
    grid_preset: str = "wide",
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    passports = tuple(PASSPORT_MATRIX_PATHS.keys())
    generated_utc = datetime.now(timezone.utc).isoformat()
    matrix = build_combo_matrix(
        project_root=project_root,
        passports=passports,
        generated_utc=generated_utc,
        family_move_values=family_move_values,
        strict_confirmations=int(strict_confirmations),
    )
    direction_label = "long" if family_move_values == [1] else "short" if family_move_values == [-1] else "both"
    path = output_dir / f"B001_F001_F005_FAMILY_UNIFIED_{direction_label}_{int(strict_confirmations)}OF5.yaml"
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(matrix, f, allow_unicode=True, sort_keys=False)

    loaded = load_calibration_matrix(project_root, rel_path=str(path.relative_to(project_root).as_posix()))
    space = compile_optuna_space(loaded, contour_id="long_only", min_enabled_blocks=1, grid_preset=grid_preset)
    manifest = {
        "status": "B001_FAMILY_UNIFIED_MATRIX_READY",
        "generated_utc": generated_utc,
        "output_dir": str(output_dir.relative_to(project_root).as_posix()),
        "matrix_path": str(path.relative_to(project_root).as_posix()),
        "family_move_values": list(family_move_values),
        "strict_confirmations": int(strict_confirmations),
        "profiles": sorted(space.get("profiles", {}).keys()),
        "rule_ru": "Все F001-F005 используют одно направление B001_family_move; вход B001 разрешается только по общему семейному совпадению.",
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate B001 RET_N ladder tournament matrices.")
    parser.add_argument("--project-root", default=".", help="Project root.")
    parser.add_argument("--output-dir", default="", help="Output directory. Defaults to reports/qa_gate/b001_ret_n_ladder_<utc>.")
    parser.add_argument("--grid-preset", default="wide", choices=["wide", "medium", "narrow"])
    parser.add_argument("--family-unified", action="store_true", help="Generate one unified B001 family matrix instead of all subset ladder matrices.")
    parser.add_argument("--family-move", type=int, default=0, choices=[-1, 0, 1], help="-1 for SHORT family, 1 for LONG family, 0 for both directions.")
    parser.add_argument("--strict-confirmations", type=int, default=5, help="Fixed N for entry_action_min_confirmations in --family-unified mode.")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve()
    if args.output_dir:
        output_dir = (project_root / args.output_dir).resolve()
    else:
        prefix = "b001_family_unified_matrices" if args.family_unified else "b001_ret_n_ladder_matrices"
        output_dir = (project_root / "reports" / "qa_gate" / f"{prefix}_{_utc_tag()}").resolve()
    if args.family_unified:
        move_values = [-1, 1] if int(args.family_move) == 0 else [int(args.family_move)]
        manifest = generate_family_unified_matrix(
            project_root=project_root,
            output_dir=output_dir,
            family_move_values=move_values,
            strict_confirmations=int(args.strict_confirmations),
            grid_preset=str(args.grid_preset),
        )
    else:
        manifest = generate_tournament_matrices(project_root=project_root, output_dir=output_dir, grid_preset=str(args.grid_preset))
    print(json.dumps(manifest, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
