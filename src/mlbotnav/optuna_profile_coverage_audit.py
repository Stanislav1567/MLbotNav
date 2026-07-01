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


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    return dict(data) if isinstance(data, dict) else {}


def _collect_linked_profiles(cfg: dict[str, Any]) -> list[str]:
    out: set[str] = set()
    for section_name in ("feature_rows", "hypothesis_rows"):
        rows = cfg.get(section_name) or []
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            if not bool(row.get("calibrate", False)):
                continue
            if not bool(row.get("optuna_toggle", False)):
                continue
            params = row.get("params") or []
            if isinstance(params, list):
                for p in params:
                    if isinstance(p, str) and p.strip():
                        out.add(p.strip())
    return sorted(out)


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


def audit_profile_coverage(
    *,
    config_path: Path,
    trial_history_path: Path,
    mode: str,
    strict_linked_coverage: bool = False,
    min_linked_coverage_ratio: float = 0.0,
    require_min_max_hits: bool = False,
    min_linked_minmax_ratio: float = 0.0,
    minmax_tolerance: float = 1e-9,
) -> dict[str, Any]:
    cfg = _load_yaml(config_path)
    profiles = dict(cfg.get("parameter_profiles") or {})
    profile_names_defined = sorted(str(k) for k in profiles.keys())
    linked_profiles = _collect_linked_profiles(cfg)

    checks: list[dict[str, Any]] = []

    def add_check(name: str, ok: bool, details: dict[str, Any]) -> None:
        checks.append({"name": name, "ok": bool(ok), "details": details})

    add_check("config_exists", config_path.exists(), {"path": str(config_path)})
    add_check("trial_history_exists", trial_history_path.exists(), {"path": str(trial_history_path)})
    if not trial_history_path.exists():
        status = "FAIL"
        return {
            "status": status,
            "mode": mode,
            "config_path": str(config_path),
            "trial_history_path": str(trial_history_path),
            "checks": checks,
            "summary": {
                "defined_profiles_count": len(profile_names_defined),
                "linked_profiles_count": len(linked_profiles),
                "history_profile_columns_count": 0,
                "linked_coverage_ratio": 0.0,
                "linked_minmax_hit_ratio": 0.0,
            },
        }

    with trial_history_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    add_check("trial_history_non_empty", len(rows) > 0, {"rows": len(rows)})
    if not rows:
        status = "FAIL"
        return {
            "status": status,
            "mode": mode,
            "config_path": str(config_path),
            "trial_history_path": str(trial_history_path),
            "checks": checks,
            "summary": {
                "defined_profiles_count": len(profile_names_defined),
                "linked_profiles_count": len(linked_profiles),
                "history_profile_columns_count": 0,
                "linked_coverage_ratio": 0.0,
                "linked_minmax_hit_ratio": 0.0,
            },
        }

    fieldnames = list(rows[0].keys())
    history_profile_cols = sorted(c for c in fieldnames if c.startswith("param_profile__"))
    history_profile_names = sorted(c.replace("param_profile__", "", 1) for c in history_profile_cols)
    history_profile_set = set(history_profile_names)

    linked_set = set(linked_profiles)
    missing_linked = sorted(linked_set - history_profile_set)
    linked_present = sorted(linked_set & history_profile_set)
    linked_coverage_ratio = float(len(linked_present) / len(linked_set)) if linked_set else 1.0
    add_check(
        "linked_profiles_coverage_ratio",
        linked_coverage_ratio >= float(min_linked_coverage_ratio),
        {
            "linked_profiles_count": len(linked_set),
            "linked_present_count": len(linked_present),
            "linked_coverage_ratio": linked_coverage_ratio,
            "min_linked_coverage_ratio": float(min_linked_coverage_ratio),
            "missing_linked_profiles": missing_linked,
        },
    )
    if strict_linked_coverage:
        add_check(
            "linked_profiles_full_coverage",
            len(missing_linked) == 0,
            {"missing_linked_profiles": missing_linked},
        )

    profile_non_empty: dict[str, int] = {}
    profile_out_of_range: dict[str, dict[str, Any]] = {}
    profile_minmax_hits: dict[str, dict[str, Any]] = {}
    for p in history_profile_names:
        col = f"param_profile__{p}"
        non_empty = 0
        out_rows: list[int] = []
        values_seen: list[float] = []
        low = _float_or_none((profiles.get(p) or {}).get("min"))
        high = _float_or_none((profiles.get(p) or {}).get("max"))
        for idx, row in enumerate(rows, start=1):
            v = _float_or_none(row.get(col))
            if v is None:
                continue
            non_empty += 1
            values_seen.append(float(v))
            if low is not None and v < low:
                out_rows.append(idx)
            elif high is not None and v > high:
                out_rows.append(idx)
        profile_non_empty[p] = non_empty
        observed_min = min(values_seen) if values_seen else None
        observed_max = max(values_seen) if values_seen else None
        min_hit = bool(values_seen) and (low is not None) and any(abs(float(v) - float(low)) <= float(minmax_tolerance) for v in values_seen)
        max_hit = bool(values_seen) and (high is not None) and any(
            abs(float(v) - float(high)) <= float(minmax_tolerance) for v in values_seen
        )
        profile_minmax_hits[p] = {
            "target_min": low,
            "target_max": high,
            "observed_min": observed_min,
            "observed_max": observed_max,
            "min_hit": bool(min_hit),
            "max_hit": bool(max_hit),
            "both_hit": bool(min_hit and max_hit),
            "samples_non_empty": int(non_empty),
            "tolerance": float(minmax_tolerance),
        }
        if out_rows:
            profile_out_of_range[p] = {
                "min": low,
                "max": high,
                "out_of_range_rows_count": len(out_rows),
                "first_rows": out_rows[:20],
            }

    empty_present_profiles = sorted([p for p, n in profile_non_empty.items() if n == 0])
    add_check(
        "present_profile_columns_have_values",
        len(empty_present_profiles) == 0,
        {
            "empty_present_profiles": empty_present_profiles,
            "history_profile_columns_count": len(history_profile_names),
        },
    )
    add_check(
        "present_profile_values_within_min_max",
        len(profile_out_of_range) == 0,
        {"out_of_range_profiles": profile_out_of_range},
    )

    linked_minmax_rows: dict[str, dict[str, Any]] = {}
    linked_both_hit_count = 0
    linked_with_targets = 0
    for p in linked_present:
        row = dict(profile_minmax_hits.get(p) or {})
        low = row.get("target_min")
        high = row.get("target_max")
        if low is not None and high is not None:
            linked_with_targets += 1
            if bool(row.get("both_hit", False)):
                linked_both_hit_count += 1
        linked_minmax_rows[p] = row
    linked_minmax_hit_ratio = (
        float(linked_both_hit_count / linked_with_targets) if linked_with_targets > 0 else 1.0
    )
    add_check(
        "linked_profiles_minmax_hit_ratio",
        linked_minmax_hit_ratio >= float(min_linked_minmax_ratio),
        {
            "linked_with_targets": int(linked_with_targets),
            "linked_both_hit_count": int(linked_both_hit_count),
            "linked_minmax_hit_ratio": float(linked_minmax_hit_ratio),
            "min_linked_minmax_ratio": float(min_linked_minmax_ratio),
        },
    )
    if require_min_max_hits:
        missing_minmax = sorted([p for p, info in linked_minmax_rows.items() if not bool(info.get("both_hit", False))])
        add_check(
            "linked_profiles_full_minmax_hits",
            len(missing_minmax) == 0,
            {"missing_linked_minmax_hits": missing_minmax},
        )

    status = "PASS" if all(bool(c.get("ok")) for c in checks) else "FAIL"
    return {
        "status": status,
        "mode": mode,
        "config_path": str(config_path),
        "trial_history_path": str(trial_history_path),
        "checks": checks,
        "summary": {
            "defined_profiles_count": len(profile_names_defined),
            "linked_profiles_count": len(linked_profiles),
            "history_profile_columns_count": len(history_profile_names),
            "linked_present_count": len(linked_present),
            "linked_coverage_ratio": linked_coverage_ratio,
            "linked_minmax_hit_ratio": linked_minmax_hit_ratio,
            "missing_linked_profiles": missing_linked,
        },
        "profile_non_empty_counts": profile_non_empty,
        "profile_minmax_hits": profile_minmax_hits,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Audit Optuna profile coverage in trial_history CSV.")
    p.add_argument("--mode", choices=["long_only", "short_only"], required=True)
    p.add_argument("--config-path", default="configs/calibration_full_matrix_v1.yaml")
    p.add_argument("--reports-root", default="reports")
    p.add_argument("--trial-history-path", default="")
    p.add_argument("--strict-linked-coverage", action="store_true")
    p.add_argument("--min-linked-coverage-ratio", type=float, default=0.0)
    p.add_argument("--require-min-max-hits", action="store_true")
    p.add_argument("--min-linked-minmax-ratio", type=float, default=0.0)
    p.add_argument("--minmax-tolerance", type=float, default=1e-9)
    p.add_argument("--out-dir", default="reports/qa_gate")
    args = p.parse_args()

    config_path = Path(args.config_path).resolve()
    reports_root = Path(args.reports_root).resolve()
    trial_history_path = Path(args.trial_history_path).resolve() if str(args.trial_history_path).strip() else None
    if trial_history_path is None:
        latest = _latest_trial_history(reports_root, args.mode)
        if latest is None:
            result = {
                "status": "FAIL",
                "mode": args.mode,
                "reason": "trial_history_not_found",
                "reports_root": str(reports_root),
            }
            out_dir = Path(args.out_dir).resolve()
            out_dir.mkdir(parents=True, exist_ok=True)
            out = out_dir / f"optuna_profile_coverage_{args.mode}_{_utc_tag()}.json"
            out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps({"status": result["status"], "report_path": str(out)}))
            return 1
        trial_history_path = latest

    result = audit_profile_coverage(
        config_path=config_path,
        trial_history_path=trial_history_path,
        mode=args.mode,
        strict_linked_coverage=bool(args.strict_linked_coverage),
        min_linked_coverage_ratio=float(args.min_linked_coverage_ratio),
        require_min_max_hits=bool(args.require_min_max_hits),
        min_linked_minmax_ratio=float(args.min_linked_minmax_ratio),
        minmax_tolerance=float(args.minmax_tolerance),
    )
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"optuna_profile_coverage_{args.mode}_{_utc_tag()}.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": result["status"], "report_path": str(out)}))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
