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


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _norm_pair(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "trend_filter": str(item.get("trend_filter", "none")),
        "min_abs_ema_gap": float(item.get("min_abs_ema_gap", 0.0)),
    }


def _pairs_equal(a: list[dict[str, Any]], b: list[dict[str, Any]]) -> bool:
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if str(x.get("trend_filter")) != str(y.get("trend_filter")):
            return False
        if abs(float(x.get("min_abs_ema_gap", 0.0)) - float(y.get("min_abs_ema_gap", 0.0))) > 1e-12:
            return False
    return True


def _latest_adaptive_summary(adaptive_dir: Path) -> Path | None:
    files = sorted(adaptive_dir.glob("adaptive_loop_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def _check(name: str, ok: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": details or {}}


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit hypothesis-plan coverage and contour isolation.")
    parser.add_argument("--contour-id", required=True, help="Contour namespace, e.g. long_only/short_only")
    parser.add_argument("--summary-path", default=None, help="Optional explicit adaptive_loop summary path")
    parser.add_argument("--features-config", default="configs/features_block.yaml")
    parser.add_argument(
        "--min-coverage-ratio",
        type=float,
        default=0.0,
        help="Minimum required coverage ratio for active backlog hypotheses (0.0..1.0).",
    )
    parser.add_argument(
        "--min-covered-count",
        type=int,
        default=0,
        help="Minimum required number of covered active backlog hypotheses.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    contour_id = str(args.contour_id).strip().lower()
    adaptive_dir = (project_root / "reports" / "adaptive" / contour_id).resolve()
    top_dir = (project_root / "reports" / "top_strategy" / contour_id).resolve()
    qa_dir = (project_root / "reports" / "qa_gate").resolve()
    qa_dir.mkdir(parents=True, exist_ok=True)

    summary_path = Path(args.summary_path) if args.summary_path else _latest_adaptive_summary(adaptive_dir)
    if summary_path is not None and not summary_path.is_absolute():
        summary_path = (project_root / summary_path).resolve()

    checks: list[dict[str, Any]] = []
    checks.append(_check("adaptive_dir_exists", adaptive_dir.exists(), {"path": str(adaptive_dir)}))
    checks.append(_check("top_dir_exists", top_dir.exists(), {"path": str(top_dir)}))
    checks.append(_check("summary_exists", summary_path is not None and summary_path.exists(), {"path": str(summary_path) if summary_path else None}))

    if not (summary_path and summary_path.exists()):
        payload = {
            "status": "FAIL",
            "generated_at_utc": _utc_now_iso(),
            "contour_id": contour_id,
            "checks": checks,
            "summary": {"total": len(checks), "failed": int(sum(1 for c in checks if not c["ok"]))},
        }
        out = qa_dir / f"hypothesis_coverage_{contour_id}_{_utc_tag()}.json"
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": payload["status"], "report_path": str(out)}, ensure_ascii=False))
        return 1

    summary = _load_json(summary_path)
    signal_mode = str(summary.get("signal_mode", "")).strip().lower()
    summary_contour = str(summary.get("contour_id", "")).strip().lower()
    checks.append(_check("summary_contour_matches", summary_contour == contour_id, {"summary_contour": summary_contour, "expected": contour_id}))
    checks.append(_check("summary_path_in_contour_dir", str(summary_path).lower().find(str(adaptive_dir).lower()) >= 0, {"summary_path": str(summary_path)}))

    top_obj = summary.get("top_strategy") if isinstance(summary, dict) else None
    top_dir_from_summary = None
    if isinstance(top_obj, dict):
        top_dir_from_summary = str(top_obj.get("top_run_dir", ""))
    if top_dir_from_summary:
        checks.append(
            _check(
                "top_strategy_in_same_contour",
                str(top_dir_from_summary).lower().find(str(top_dir).lower()) >= 0,
                {"top_run_dir": top_dir_from_summary, "expected_top_root": str(top_dir)},
            )
        )
    else:
        checks.append(_check("top_strategy_in_same_contour", True, {"note": "top_strategy not published in summary"}))

    # Hypothesis-plan consistency for profile-based mode.
    plan_source = str(summary.get("hypothesis_plan_source", "") or "").strip().lower()
    profile_name = str(summary.get("hypothesis_profile", "") or "").strip()
    use_profile_mode = bool(
        summary.get("use_hypothesis_profile_effective", False)
        or summary.get("use_hypothesis_profile", False)
        or summary.get("long_style_1m", False)
    )
    if use_profile_mode and profile_name and plan_source in {"features_config", "default_fallback"}:
        cfg_path = Path(args.features_config)
        if not cfg_path.is_absolute():
            cfg_path = (project_root / cfg_path).resolve()
        cfg = _load_yaml(cfg_path) if cfg_path.exists() else {}
        expected_raw = (((cfg.get("hypotheses") or {}).get(profile_name)) or [])
        expected = [_norm_pair(x) for x in expected_raw if isinstance(x, dict)]
        plan_raw = summary.get("hypothesis_plan", []) if isinstance(summary, dict) else []
        planned = [_norm_pair(x) for x in plan_raw if isinstance(x, dict)]

        checks.append(_check("features_config_loaded", cfg_path.exists(), {"path": str(cfg_path)}))
        checks.append(_check("profile_expected_not_empty", len(expected) > 0, {"profile": profile_name, "expected_count": len(expected)}))
        checks.append(
            _check(
                "profile_plan_matches_config",
                _pairs_equal(planned, expected),
                {"profile": profile_name, "planned_count": len(planned), "expected_count": len(expected), "source": plan_source},
            )
        )

        history = summary.get("history", []) if isinstance(summary, dict) else []
        observed_set = {
            (str(h.get("trend_filter", "none")), float(h.get("min_abs_ema_gap", 0.0)))
            for h in history
            if isinstance(h, dict)
        }
        checks.append(
            _check(
                "history_hypotheses_subset_of_plan",
                observed_set.issubset({(x["trend_filter"], float(x["min_abs_ema_gap"])) for x in planned}),
                {"history_unique": len(observed_set), "planned_unique": len(planned)},
            )
        )
    else:
        # For non-long-style runs, contour separation is the primary check.
        checks.append(
            _check(
                "non_profile_mode_expected",
                signal_mode in {"short_only", "both", "long_only"},
                {"signal_mode": signal_mode, "plan_source": plan_source, "profile": profile_name},
            )
        )

    # P6.2: dedicated coverage section for active backlog hypotheses in history.
    cfg_path = Path(args.features_config)
    if not cfg_path.is_absolute():
        cfg_path = (project_root / cfg_path).resolve()
    run_mode = signal_mode if signal_mode in {"both", "long_only", "short_only"} else contour_id
    backlog_reg = load_backlog_registry(
        project_root=project_root,
        features_config=str(cfg_path),
        run_signal_mode=run_mode,
    )
    checks.append(
        _check(
            "active_backlog_registry_loaded",
            str(backlog_reg.get("status", "")).lower() == "ok",
            {"registry_status": backlog_reg.get("status"), "config_path": backlog_reg.get("config_path"), "run_mode": run_mode},
        )
    )

    active_items = [x for x in (backlog_reg.get("active_items") or []) if isinstance(x, dict)]
    expected_active_names = sorted({str(x.get("name", "")).strip() for x in active_items if str(x.get("name", "")).strip()})
    history = summary.get("history", []) if isinstance(summary, dict) else []
    observed_filters = sorted(
        {
            str(h.get("trend_filter", "")).strip()
            for h in history
            if isinstance(h, dict) and str(h.get("trend_filter", "")).strip()
        }
    )
    covered = sorted(set(expected_active_names).intersection(observed_filters))
    missing = sorted(set(expected_active_names) - set(observed_filters))
    coverage_ratio = float(len(covered) / len(expected_active_names)) if expected_active_names else 1.0

    checks.append(
        _check(
            "active_backlog_expected_set_built",
            True,
            {
                "expected_active_count": len(expected_active_names),
                "expected_active_names": expected_active_names,
            },
        )
    )
    checks.append(
        _check(
            "active_backlog_history_coverage_present",
            (len(expected_active_names) == 0) or (len(covered) > 0),
            {
                "covered_count": len(covered),
                "missing_count": len(missing),
                "coverage_ratio": coverage_ratio,
                "covered_names": covered,
                "missing_names": missing,
                "observed_history_filters": observed_filters,
            },
        )
    )
    threshold_ratio = float(args.min_coverage_ratio)
    threshold_count = int(args.min_covered_count)
    ratio_ok = coverage_ratio >= threshold_ratio
    count_ok = len(covered) >= threshold_count
    checks.append(
        _check(
            "active_backlog_coverage_threshold_met",
            (len(expected_active_names) == 0) or (ratio_ok and count_ok),
            {
                "coverage_ratio": coverage_ratio,
                "covered_count": len(covered),
                "threshold_ratio": threshold_ratio,
                "threshold_count": threshold_count,
            },
        )
    )

    failed = int(sum(1 for c in checks if not c["ok"]))
    payload = {
        "status": "PASS" if failed == 0 else "FAIL",
        "generated_at_utc": _utc_now_iso(),
        "contour_id": contour_id,
        "summary_path": str(summary_path),
        "checks": checks,
        "summary": {"total": len(checks), "failed": failed},
    }
    out = qa_dir / f"hypothesis_coverage_{contour_id}_{_utc_tag()}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "report_path": str(out), "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
