from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_matrix(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    return dict(data) if isinstance(data, dict) else {}


def _latest_trial_history(reports_root: Path, mode: str) -> Path | None:
    mode_dir = reports_root / "optuna" / mode
    files = sorted(mode_dir.glob("trial_history_*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def _float_or_none(v: Any) -> float | None:
    if v is None:
        return None
    s = str(v).strip()
    if not s:
        return None
    try:
        return float(s)
    except Exception:
        return None


def _history_column_for_search_name(name: str) -> str:
    n = str(name).strip()
    if n == "min_expected_move":
        return "min_expected_move_pct"
    return n


def audit_search_grid_coverage(
    *,
    matrix_path: Path,
    trial_history_path: Path,
    mode: str,
    tolerance: float = 1e-9,
) -> dict[str, Any]:
    matrix = _load_matrix(matrix_path)
    profiles = dict(matrix.get("parameter_profiles") or {})
    search_rows = [r for r in list(matrix.get("search_grid_rows") or []) if isinstance(r, dict)]

    checks: list[dict[str, Any]] = []

    def add_check(name: str, ok: bool, details: dict[str, Any]) -> None:
        checks.append({"name": str(name), "ok": bool(ok), "details": dict(details or {})})

    add_check("matrix_exists", matrix_path.exists(), {"path": str(matrix_path)})
    add_check("trial_history_exists", trial_history_path.exists(), {"path": str(trial_history_path)})
    if not trial_history_path.exists():
        return {
            "status": "FAIL",
            "mode": str(mode),
            "matrix_path": str(matrix_path),
            "trial_history_path": str(trial_history_path),
            "checks": checks,
            "summary": {"rows_total": 0, "rows_passed": 0, "coverage_ratio": 0.0},
        }

    with trial_history_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    add_check("trial_history_non_empty", len(rows) > 0, {"rows": len(rows)})
    if not rows:
        return {
            "status": "FAIL",
            "mode": str(mode),
            "matrix_path": str(matrix_path),
            "trial_history_path": str(trial_history_path),
            "checks": checks,
            "summary": {"rows_total": 0, "rows_passed": 0, "coverage_ratio": 0.0},
        }

    coverage_rows: list[dict[str, Any]] = []
    passed = 0
    for row in search_rows:
        name = str(row.get("name", "")).strip()
        profile_name = str(row.get("profile", "")).strip()
        hist_col = _history_column_for_search_name(name)
        target = dict(profiles.get(profile_name) or {})
        tmin = _float_or_none(target.get("min"))
        tmax = _float_or_none(target.get("max"))
        vals: list[float] = []
        for r in rows:
            v = _float_or_none(r.get(hist_col))
            if v is not None:
                vals.append(float(v))
        obs_min = min(vals) if vals else None
        obs_max = max(vals) if vals else None
        min_hit = bool(vals) and (tmin is not None) and any(abs(v - float(tmin)) <= float(tolerance) for v in vals)
        max_hit = bool(vals) and (tmax is not None) and any(abs(v - float(tmax)) <= float(tolerance) for v in vals)
        both_hit = bool(min_hit and max_hit)
        if both_hit:
            passed += 1
        coverage_rows.append(
            {
                "name": name,
                "history_column": hist_col,
                "profile": profile_name,
                "target_min": tmin,
                "target_max": tmax,
                "observed_min": obs_min,
                "observed_max": obs_max,
                "min_hit": bool(min_hit),
                "max_hit": bool(max_hit),
                "both_hit": bool(both_hit),
                "samples_non_empty": int(len(vals)),
            }
        )

    total = len(coverage_rows)
    ratio = float(passed / total) if total > 0 else 0.0
    add_check(
        "search_grid_full_minmax_coverage",
        bool(total > 0 and passed == total),
        {"rows_total": int(total), "rows_passed": int(passed), "coverage_ratio": float(ratio)},
    )

    status = "PASS" if all(bool(c.get("ok")) for c in checks) else "FAIL"
    return {
        "status": status,
        "mode": str(mode),
        "matrix_path": str(matrix_path),
        "trial_history_path": str(trial_history_path),
        "checks": checks,
        "summary": {"rows_total": int(total), "rows_passed": int(passed), "coverage_ratio": float(ratio)},
        "search_grid_rows": coverage_rows,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Audit min/max coverage for base search-grid rows in Optuna trial history.")
    p.add_argument("--mode", choices=["long_only", "short_only"], required=True)
    p.add_argument("--matrix-path", default="configs/calibration_full_matrix_v1.yaml")
    p.add_argument("--reports-root", default="reports")
    p.add_argument("--trial-history-path", default="")
    p.add_argument("--tolerance", type=float, default=1e-9)
    p.add_argument("--out-dir", default="reports/qa_gate")
    args = p.parse_args()

    matrix_path = Path(args.matrix_path).resolve()
    reports_root = Path(args.reports_root).resolve()
    trial_history_path = Path(args.trial_history_path).resolve() if str(args.trial_history_path).strip() else None
    if trial_history_path is None:
        latest = _latest_trial_history(reports_root, str(args.mode))
        if latest is None:
            result = {
                "status": "FAIL",
                "mode": str(args.mode),
                "reason": "trial_history_not_found",
                "reports_root": str(reports_root),
            }
            out_dir = Path(args.out_dir).resolve()
            out_dir.mkdir(parents=True, exist_ok=True)
            out = out_dir / f"optuna_search_grid_coverage_{args.mode}_{_utc_tag()}.json"
            out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps({"status": result["status"], "report_path": str(out)}))
            return 1
        trial_history_path = latest

    result = audit_search_grid_coverage(
        matrix_path=matrix_path,
        trial_history_path=trial_history_path,
        mode=str(args.mode),
        tolerance=float(args.tolerance),
    )
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"optuna_search_grid_coverage_{args.mode}_{_utc_tag()}.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": result["status"], "report_path": str(out)}))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
