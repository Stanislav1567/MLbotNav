from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.optuna_space import compile_optuna_space, load_calibration_matrix


def _iso_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _latest_trial_history(project_root: Path, contour_id: str) -> Path:
    mode = str(contour_id or "short_only").strip().lower()
    d = (project_root / "reports" / "optuna" / mode).resolve()
    files = sorted(d.glob("trial_history_*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise FileNotFoundError(f"No trial_history files under: {d}")
    return files[0]


def _as_float(v: Any) -> float | None:
    try:
        if pd.isna(v):
            return None
        return float(v)
    except Exception:
        return None


def build_coverage_report(
    *,
    project_root: Path,
    trial_history_path: Path,
    contour_id: str,
    calibration_matrix_rel: str = "configs/calibration_full_matrix_v1.yaml",
) -> dict[str, Any]:
    matrix = load_calibration_matrix(project_root, rel_path=calibration_matrix_rel)
    space = compile_optuna_space(matrix, contour_id=str(contour_id), min_enabled_blocks=1)
    profiles = dict(space.get("profiles") or {})
    expected_profiles = sorted(profiles.keys())

    df = pd.read_csv(trial_history_path)
    total_rows = int(len(df))
    rows_completed = int((pd.to_numeric(df.get("trial_number"), errors="coerce").notna()).sum())

    rows: list[dict[str, Any]] = []
    missing_columns: list[str] = []
    for name in expected_profiles:
        col = f"param_profile__{name}"
        prof = dict(profiles.get(name) or {})
        pmin = float(prof.get("min"))
        pmax = float(prof.get("max"))
        pstep = float(prof.get("step"))
        pcount = int(prof.get("count", 0)) if str(prof.get("count", "")).strip() else None

        if col not in df.columns:
            missing_columns.append(col)
            rows.append(
                {
                    "profile": name,
                    "column": col,
                    "present_in_trial_history": False,
                    "samples_non_null": 0,
                    "coverage_rate": 0.0,
                    "observed_min": None,
                    "observed_max": None,
                    "distinct_values": 0,
                    "min_target": pmin,
                    "max_target": pmax,
                    "step": pstep,
                    "count_target": pcount,
                    "hit_min": False,
                    "hit_max": False,
                }
            )
            continue

        series = pd.to_numeric(df[col], errors="coerce")
        non_null = series.dropna()
        non_null_count = int(non_null.shape[0])
        coverage_rate = float(non_null_count / total_rows) if total_rows > 0 else 0.0
        distinct_values = int(non_null.nunique()) if non_null_count > 0 else 0
        obs_min = _as_float(non_null.min()) if non_null_count > 0 else None
        obs_max = _as_float(non_null.max()) if non_null_count > 0 else None
        hit_min = bool(obs_min is not None and abs(float(obs_min) - float(pmin)) <= 1e-12)
        hit_max = bool(obs_max is not None and abs(float(obs_max) - float(pmax)) <= 1e-12)
        rows.append(
            {
                "profile": name,
                "column": col,
                "present_in_trial_history": True,
                "samples_non_null": non_null_count,
                "coverage_rate": coverage_rate,
                "observed_min": obs_min,
                "observed_max": obs_max,
                "distinct_values": distinct_values,
                "min_target": pmin,
                "max_target": pmax,
                "step": pstep,
                "count_target": pcount,
                "hit_min": hit_min,
                "hit_max": hit_max,
            }
        )

    profiles_total = len(expected_profiles)
    profiles_with_samples = int(sum(1 for r in rows if int(r.get("samples_non_null", 0)) > 0))
    profiles_hit_min = int(sum(1 for r in rows if bool(r.get("hit_min"))))
    profiles_hit_max = int(sum(1 for r in rows if bool(r.get("hit_max"))))
    profiles_never_sampled = sorted([str(r["profile"]) for r in rows if int(r.get("samples_non_null", 0)) == 0])

    return {
        "status": "PASS",
        "run_utc": _iso_utc(),
        "contour_id": str(contour_id),
        "trial_history_path": str(trial_history_path),
        "calibration_matrix_rel": calibration_matrix_rel,
        "totals": {
            "trial_rows": total_rows,
            "rows_with_trial_number": rows_completed,
            "profiles_expected": profiles_total,
            "profiles_with_samples": profiles_with_samples,
            "profiles_hit_min": profiles_hit_min,
            "profiles_hit_max": profiles_hit_max,
        },
        "missing_param_columns": missing_columns,
        "profiles_never_sampled": profiles_never_sampled,
        "coverage_rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Optuna profile coverage audit from trial_history CSV")
    parser.add_argument("--contour-id", default="short_only")
    parser.add_argument("--trial-history", default="")
    parser.add_argument("--calibration-matrix-rel", default="configs/calibration_full_matrix_v1.yaml")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    if str(args.trial_history).strip():
        trial_history_path = Path(str(args.trial_history)).resolve()
    else:
        trial_history_path = _latest_trial_history(project_root, str(args.contour_id))

    report = build_coverage_report(
        project_root=project_root,
        trial_history_path=trial_history_path,
        contour_id=str(args.contour_id),
        calibration_matrix_rel=str(args.calibration_matrix_rel),
    )
    out_dir = (project_root / "reports" / "qa_gate").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"optuna_profile_coverage_{str(args.contour_id).lower()}_{report['run_utc']}.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "PASS", "report_path": str(out_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

