from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _parse_yyyy_mm_dd(v: str) -> datetime:
    return datetime.strptime(v, "%Y-%m-%d")


def _check(name: str, ok: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": details or {}}


def main() -> int:
    p = argparse.ArgumentParser(description="AKFP profiles/rules audit for calibration windows.")
    p.add_argument("--policy", default="configs/akfp_policy.yaml")
    p.add_argument("--output-dir", default="reports/qa_gate")
    args = p.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    policy_path = Path(args.policy)
    if not policy_path.is_absolute():
        policy_path = (project_root / policy_path).resolve()

    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = (project_root / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    cfg = _load_yaml(policy_path)
    akfp = dict(cfg.get("akfp") or {})
    exe = dict(akfp.get("execution") or {})
    cw = dict(akfp.get("calibration_windows") or {})
    profiles = dict(cw.get("profiles") or {})
    rules = dict(cw.get("rules") or {})
    active = str(cw.get("active_profile", "")).strip()

    checks: list[dict[str, Any]] = []
    checks.append(_check("policy_present", bool(akfp)))
    checks.append(_check("calibration_windows_present", bool(cw)))
    checks.append(_check("profiles_present", bool(profiles)))
    checks.append(_check("active_profile_present", bool(active)))
    checks.append(_check("active_profile_exists", bool(active in profiles), {"active_profile": active}))

    required_profiles = {"smoke_1d1d", "tuning_1d1d", "tuning_3d2d", "preprod_14d7d", "production_21d7d"}
    checks.append(
        _check(
            "required_profiles_present",
            required_profiles.issubset(set(profiles.keys())),
            {"missing": sorted(required_profiles.difference(set(profiles.keys())))},
        )
    )

    for profile_name, profile in profiles.items():
        td = int((profile or {}).get("train_days", 0))
        vd = int((profile or {}).get("test_days", 0))
        rp = int((profile or {}).get("repeats", 0))
        checks.append(_check(f"profile::{profile_name}::train_days_positive", td > 0, {"train_days": td}))
        checks.append(_check(f"profile::{profile_name}::test_days_positive", vd > 0, {"test_days": vd}))
        checks.append(_check(f"profile::{profile_name}::repeats_positive", rp > 0, {"repeats": rp}))

    checks.append(_check("rule_closed_day_only", bool(rules.get("closed_day_only") is True)))
    checks.append(_check("rule_disallow_current_unclosed_day", bool(rules.get("disallow_current_unclosed_day") is True)))
    checks.append(_check("rule_strict_24h_test_window", bool(rules.get("strict_24h_test_window") is True)))
    checks.append(
        _check("rule_force_restore_readiness_after_run", bool(rules.get("force_restore_readiness_after_run") is True))
    )

    train_date = str(exe.get("train_date", "")).strip()
    test_date = str(exe.get("test_date", "")).strip()
    repeats = int(exe.get("repeats", 0))
    checks.append(_check("execution_train_date_present", bool(train_date)))
    checks.append(_check("execution_test_date_present", bool(test_date)))
    checks.append(_check("execution_repeats_positive", repeats > 0, {"repeats": repeats}))

    date_parse_ok = False
    gap_days = None
    utc_today = datetime.now(timezone.utc).date()
    try:
        d_train = _parse_yyyy_mm_dd(train_date).date()
        d_test = _parse_yyyy_mm_dd(test_date).date()
        date_parse_ok = True
        gap_days = (d_test - d_train).days
        checks.append(_check("execution_test_after_train", d_test > d_train, {"train_date": train_date, "test_date": test_date}))
        checks.append(_check("execution_test_day_closed_utc", d_test < utc_today, {"test_date": test_date, "utc_today": utc_today.isoformat()}))
    except Exception as exc:
        checks.append(_check("execution_dates_parseable", False, {"error": str(exc)}))
    else:
        checks.append(_check("execution_dates_parseable", True))

    active_profile = dict(profiles.get(active) or {})
    if active_profile and gap_days is not None:
        td = int(active_profile.get("train_days", 0))
        vd = int(active_profile.get("test_days", 0))
        expected_gap_min = 1
        checks.append(
            _check(
                "active_profile_gap_consistent",
                bool(gap_days >= expected_gap_min),
                {"gap_days": gap_days, "train_days": td, "test_days": vd},
            )
        )
        checks.append(
            _check(
                "active_profile_repeats_match_execution",
                bool(repeats == int(active_profile.get("repeats", repeats))),
                {"execution_repeats": repeats, "profile_repeats": int(active_profile.get("repeats", repeats))},
            )
        )

    # Forecast helper for operator: if test_date is T, derive train_start for each profile.
    forecast: list[dict[str, Any]] = []
    if date_parse_ok:
        d_test = _parse_yyyy_mm_dd(test_date).date()
        for profile_name, profile in profiles.items():
            td = int((profile or {}).get("train_days", 1))
            vd = int((profile or {}).get("test_days", 1))
            # Train ends the day before test window starts.
            test_start = d_test - timedelta(days=vd - 1)
            train_end = test_start - timedelta(days=1)
            train_start = train_end - timedelta(days=td - 1)
            forecast.append(
                {
                    "profile": profile_name,
                    "train_start": train_start.isoformat(),
                    "train_end": train_end.isoformat(),
                    "test_start": test_start.isoformat(),
                    "test_end": d_test.isoformat(),
                    "repeats": int((profile or {}).get("repeats", 1)),
                }
            )

    failed = sum(1 for c in checks if not bool(c["ok"]))
    status = "PASS" if failed == 0 else "FAIL"
    out = {
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "policy_path": str(policy_path),
        "active_profile": active,
        "execution": {"train_date": train_date, "test_date": test_date, "repeats": repeats},
        "summary": {"total": len(checks), "failed": failed},
        "checks": checks,
        "windows_forecast": forecast,
    }
    out_path = out_dir / f"akfp_profiles_audit_{_utc_tag()}.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": status, "report_path": str(out_path)}, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

