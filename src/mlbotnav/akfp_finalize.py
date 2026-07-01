from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from mlbotnav.hypothesis_registry import load_backlog_registry


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _latest_by_glob(root: Path, pattern: str) -> Path | None:
    files = list(root.glob(pattern))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def _classify_contour(
    *,
    contour: str,
    backlog_registry: dict[str, Any],
    working_tools_raw: list[str],
    best_combo_filters: list[str],
) -> dict[str, Any]:
    items = [x for x in (backlog_registry.get("items") or []) if isinstance(x, dict)]
    by_name = {str(x.get("name", "")).strip(): x for x in items if str(x.get("name", "")).strip()}
    active_names = {
        str(x.get("name", "")).strip()
        for x in (backlog_registry.get("active_items") or [])
        if isinstance(x, dict) and str(x.get("name", "")).strip()
    }

    disabled: list[dict[str, Any]] = []
    for nm, rec in by_name.items():
        status = str(rec.get("status", "")).strip().lower()
        enabled = bool(rec.get("enabled_for_run"))
        if status not in {"active", "validated"} or not enabled:
            disabled.append(
                {
                    "name": nm,
                    "status": status or "missing_status",
                    "reasons": rec.get("disabled_reasons") or [],
                }
            )

    dangerous: list[dict[str, Any]] = []
    for nm in working_tools_raw:
        r = by_name.get(nm)
        if r is None:
            dangerous.append({"name": nm, "reason": "not_found_in_backlog_registry"})
            continue
        if not bool(r.get("enabled_for_run")):
            dangerous.append(
                {
                    "name": nm,
                    "reason": "present_in_working_but_not_enabled_for_run",
                    "disabled_reasons": r.get("disabled_reasons") or [],
                }
            )

    dangerous_names = {str(x.get("name", "")).strip() for x in dangerous if str(x.get("name", "")).strip()}
    working_sanitized = sorted({x for x in working_tools_raw if x in active_names and x not in dangerous_names})

    weak = sorted([x for x in active_names if x not in set(best_combo_filters)])

    return {
        "contour": contour,
        "working_sanitized": working_sanitized,
        "weak_tools": weak,
        "dangerous_tools": dangerous,
        "disabled_tools": sorted(disabled, key=lambda d: str(d.get("name", ""))),
        "active_total": len(active_names),
        "working_raw_total": len(working_tools_raw),
        "working_sanitized_total": len(working_sanitized),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="AKFP P12: final registries and final config package.")
    parser.add_argument("--policy", default="configs/akfp_policy.yaml")
    parser.add_argument("--output-dir", default="reports/akfp/finalization")
    parser.add_argument("--working-tools", default="")
    parser.add_argument("--best-combos", default="")
    parser.add_argument("--long-pkg", default="")
    parser.add_argument("--short-pkg", default="")
    parser.add_argument("--combined-report", default="")
    parser.add_argument("--p24-report", default="")
    parser.add_argument("--chain-manifest", default="")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    policy_path = Path(args.policy)
    if not policy_path.is_absolute():
        policy_path = (project_root / policy_path).resolve()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = (project_root / output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    cfg = _load_yaml(policy_path)
    akfp = dict(cfg.get("akfp") or {})
    exe = dict(akfp.get("execution") or {})
    windows = dict(akfp.get("calibration_windows") or {})

    symbol = str(exe.get("symbol", "SOLUSDT"))
    timeframe = str(exe.get("timeframe", "1m"))
    train_date = str(exe.get("train_date", "2026-05-19"))
    test_date = str(exe.get("test_date", "2026-05-20"))

    manifest_obj: dict[str, Any] = {}
    manifest_paths: dict[str, Any] = {}
    if str(args.chain_manifest).strip():
        mp = Path(str(args.chain_manifest)).resolve()
        if not mp.exists():
            raise RuntimeError(f"chain_manifest not found: {mp}")
        manifest_obj = _load_json(mp)
        manifest_paths = dict(manifest_obj.get("artifact_paths") or {})

    def _pick(raw_arg: str, manifest_key: str, fallback: Path | None) -> Path | None:
        if str(raw_arg).strip():
            return Path(str(raw_arg)).resolve()
        m = str(manifest_paths.get(manifest_key, "")).strip()
        if m:
            return Path(m).resolve()
        return fallback

    working_tools_path = _pick(args.working_tools, "working_tools", (project_root / "reports" / "akfp" / "combo_working" / "WORKING_TOOLS.json").resolve())
    best_combos_path = _pick(args.best_combos, "best_combos", (project_root / "reports" / "akfp" / "combo_working" / "BEST_COMBOS.json").resolve())
    long_pkg_path = _pick(args.long_pkg, "long_pkg", (project_root / "reports" / "akfp" / "final_long" / "LONG_FINAL_PACKAGE.json").resolve())
    short_pkg_path = _pick(args.short_pkg, "short_pkg", (project_root / "reports" / "akfp" / "final_short" / "SHORT_FINAL_PACKAGE.json").resolve())

    combined_latest = _pick(args.combined_report, "combined_report", _latest_by_glob(project_root, "reports/akfp/combined/akfp_combined_consistency_*.json"))
    p24_latest = _pick(args.p24_report, "p24_report", _latest_by_glob(project_root, "reports/qa_gate/p24_latest_pass_*.json"))

    working_raw_obj = _load_json(working_tools_path) if working_tools_path.exists() else {}
    best_combos_obj = _load_json(best_combos_path) if best_combos_path.exists() else {}
    long_pkg = _load_json(long_pkg_path) if long_pkg_path.exists() else {}
    short_pkg = _load_json(short_pkg_path) if short_pkg_path.exists() else {}
    combined_obj = _load_json(combined_latest) if combined_latest else {}
    p24_obj = _load_json(p24_latest) if p24_latest else {}

    long_reg = load_backlog_registry(
        project_root=project_root,
        features_config="configs/features_block.yaml",
        run_signal_mode="long_only",
    )
    short_reg = load_backlog_registry(
        project_root=project_root,
        features_config="configs/features_block.yaml",
        run_signal_mode="short_only",
    )

    long_working_raw = [str(x) for x in (working_raw_obj.get("long_only") or []) if str(x).strip()]
    short_working_raw = [str(x) for x in (working_raw_obj.get("short_only") or []) if str(x).strip()]
    long_combo_filters = [str(x) for x in ((best_combos_obj.get("long_only") or {}).get("combo_filters") or []) if str(x).strip()]
    short_combo_filters = [str(x) for x in ((best_combos_obj.get("short_only") or {}).get("combo_filters") or []) if str(x).strip()]

    long_cls = _classify_contour(
        contour="long_only",
        backlog_registry=long_reg,
        working_tools_raw=long_working_raw,
        best_combo_filters=long_combo_filters,
    )
    short_cls = _classify_contour(
        contour="short_only",
        backlog_registry=short_reg,
        working_tools_raw=short_working_raw,
        best_combo_filters=short_combo_filters,
    )

    working_tools = {
        "long_only": long_cls["working_sanitized"],
        "short_only": short_cls["working_sanitized"],
    }
    weak_tools = {
        "long_only": long_cls["weak_tools"],
        "short_only": short_cls["weak_tools"],
    }
    dangerous_tools = {
        "long_only": long_cls["dangerous_tools"],
        "short_only": short_cls["dangerous_tools"],
    }
    disabled_tools = {
        "long_only": long_cls["disabled_tools"],
        "short_only": short_cls["disabled_tools"],
    }
    best_combos = {
        "long_only": best_combos_obj.get("long_only"),
        "short_only": best_combos_obj.get("short_only"),
    }

    active_profile = str(windows.get("active_profile", "")).strip()
    profiles = dict(windows.get("profiles") or {})
    active_window = dict(profiles.get(active_profile) or {})

    final_config = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol,
        "timeframe": timeframe,
        "train_date": train_date,
        "test_date": test_date,
        "policy_path": str(policy_path),
        "profiles": {
            "active_profile": active_profile,
            "active_window": active_window,
            "all_profiles": profiles,
            "rules": dict(windows.get("rules") or {}),
        },
        "contours": {
            "long_only": {
                "final_package": long_pkg,
                "best_combo_filters": long_combo_filters,
                "working_tools": working_tools["long_only"],
            },
            "short_only": {
                "final_package": short_pkg,
                "best_combo_filters": short_combo_filters,
                "working_tools": working_tools["short_only"],
            },
        },
        "combined_status": {
            "combined_report_path": str(combined_latest) if combined_latest else None,
            "combined_status": combined_obj.get("status") if isinstance(combined_obj, dict) else None,
            "latest_pass_report_path": str(p24_latest) if p24_latest else None,
            "latest_pass_status": p24_obj.get("status") if isinstance(p24_obj, dict) else None,
            "chain_manifest": str(args.chain_manifest).strip() or None,
        },
        "guardrails": {
            "separate_long_short_required": True,
            "closed_day_test_only": True,
            "strict_24h_test_window": True,
            "restore_readiness_after_run": True,
        },
    }

    def _write(name: str, obj: Any) -> str:
        p = output_dir / name
        p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(p)

    paths = {
        "WORKING_TOOLS": _write("WORKING_TOOLS.json", working_tools),
        "WEAK_TOOLS": _write("WEAK_TOOLS.json", weak_tools),
        "DANGEROUS_TOOLS": _write("DANGEROUS_TOOLS.json", dangerous_tools),
        "DISABLED_TOOLS": _write("DISABLED_TOOLS.json", disabled_tools),
        "BEST_COMBOS": _write("BEST_COMBOS.json", best_combos),
        "FINAL_CONFIG": _write("FINAL_CONFIG.json", final_config),
    }

    checks = [
        {"name": "working_tools_non_empty_long", "ok": bool(len(working_tools["long_only"]) > 0)},
        {"name": "working_tools_non_empty_short", "ok": bool(len(working_tools["short_only"]) > 0)},
        {"name": "final_long_technical_pass", "ok": bool((long_pkg or {}).get("technical_pass") is True)},
        {"name": "final_short_technical_pass", "ok": bool((short_pkg or {}).get("technical_pass") is True)},
        {"name": "final_long_strategy_pass", "ok": bool((long_pkg or {}).get("strategy_pass") is True)},
        {"name": "final_short_strategy_pass", "ok": bool((short_pkg or {}).get("strategy_pass") is True)},
        {"name": "combined_pass", "ok": bool((combined_obj or {}).get("status") == "PASS")},
        {"name": "latest_pass_report_status_pass", "ok": bool((p24_obj or {}).get("status") == "PASS")},
        {"name": "active_window_profile_present", "ok": bool(active_profile and active_window)},
    ]
    failed = sum(1 for c in checks if not bool(c["ok"]))
    status = "PASS" if failed == 0 else "FAIL"

    report = {
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "summary": {"total": len(checks), "failed": failed},
        "checks": checks,
        "registry_paths": paths,
        "classifiers": {"long_only": long_cls, "short_only": short_cls},
    }
    report_path = output_dir / f"akfp_p12_finalize_{symbol}_{timeframe}_{test_date}_{_utc_tag()}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": status,
                "report_path": str(report_path),
                "registry_paths": paths,
            },
            ensure_ascii=False,
        )
    )
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
