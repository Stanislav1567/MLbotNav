from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml


@dataclass
class Check:
    name: str
    ok: bool
    details: dict[str, Any] | None = None


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _parse_d(v: str) -> date:
    return datetime.strptime(v, "%Y-%m-%d").date()


def main() -> int:
    p = argparse.ArgumentParser(description="AKFP strict window gate checker.")
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
    windows = dict(akfp.get("calibration_windows") or {})
    rules = dict(windows.get("rules") or {})
    profiles = dict(windows.get("profiles") or {})
    active_profile = str(windows.get("active_profile", "")).strip()
    active = dict(profiles.get(active_profile) or {})

    train_date = str(exe.get("train_date", "")).strip()
    test_date = str(exe.get("test_date", "")).strip()
    repeats = int(exe.get("repeats", 1))

    checks: list[Check] = []
    checks.append(Check("policy_exists", bool(akfp)))
    checks.append(Check("active_profile_present", bool(active_profile and active)))
    checks.append(Check("execution_train_date_present", bool(train_date)))
    checks.append(Check("execution_test_date_present", bool(test_date)))

    d_train = None
    d_test = None
    parse_ok = False
    try:
        d_train = _parse_d(train_date)
        d_test = _parse_d(test_date)
        parse_ok = True
    except Exception:
        parse_ok = False
    checks.append(Check("dates_parseable", parse_ok))

    if parse_ok and d_train and d_test:
        checks.append(Check("test_after_train", d_test > d_train, {"train_date": train_date, "test_date": test_date}))
        gap_days = (d_test - d_train).days
        expected_train_days = int(active.get("train_days", 0))
        expected_test_days = int(active.get("test_days", 0))
        # For 1d1d policy, train and test are neighboring closed dates => delta=1 day.
        expected_gap_min = 1 if expected_train_days == 1 and expected_test_days == 1 else 1
        checks.append(
            Check(
                "window_gap_consistent",
                bool(gap_days >= expected_gap_min),
                {
                    "gap_days": gap_days,
                    "profile_train_days": expected_train_days,
                    "profile_test_days": expected_test_days,
                },
            )
        )
        if bool(rules.get("disallow_current_unclosed_day", False)):
            utc_today = datetime.now(timezone.utc).date()
            checks.append(
                Check(
                    "test_day_is_closed",
                    bool(d_test < utc_today),
                    {"test_date": test_date, "utc_today": utc_today.isoformat()},
                )
            )

    expected_repeats = int(active.get("repeats", repeats if repeats > 0 else 1))
    checks.append(
        Check(
            "repeats_match_profile",
            bool(repeats == expected_repeats),
            {"repeats": repeats, "expected_repeats": expected_repeats, "active_profile": active_profile},
        )
    )

    failed = sum(1 for c in checks if not c.ok)
    status = "PASS" if failed == 0 else "FAIL"
    payload = {
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "policy_path": str(policy_path),
        "active_profile": active_profile,
        "execution": {
            "train_date": train_date,
            "test_date": test_date,
            "repeats": repeats,
        },
        "profile": active,
        "rules": rules,
        "checks": [{"name": c.name, "ok": c.ok, "details": c.details or {}} for c in checks],
        "summary": {"total": len(checks), "failed": failed},
    }

    out = out_dir / f"akfp_window_gate_{_utc_tag()}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": status, "report_path": str(out)}, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

