from __future__ import annotations

import argparse
import json
import subprocess
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


def _extract_json(stdout: str) -> dict[str, Any] | None:
    txt = (stdout or "").strip()
    if not txt:
        return None
    try:
        obj = json.loads(txt)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    for line in reversed([x.strip() for x in txt.splitlines() if x.strip()]):
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                return obj
        except Exception:
            continue
    return None


def _run(cmd: list[str], cwd: Path) -> dict[str, Any]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    parsed = _extract_json(p.stdout or "")
    return {
        "returncode": int(p.returncode),
        "cmd": cmd,
        "stdout_tail": (p.stdout or "")[-4000:],
        "stderr_tail": (p.stderr or "")[-4000:],
        "parsed_json": parsed,
    }


def _chunked(values: list[str], size: int) -> list[list[str]]:
    out: list[list[str]] = []
    if size <= 0:
        return out
    for i in range(0, len(values), size):
        part = [x for x in values[i : i + size] if x]
        if part:
            out.append(part)
    return out


def _build_working_tools(project_root: Path, contour: str) -> dict[str, Any]:
    reg = load_backlog_registry(
        project_root=project_root,
        features_config="configs/features_block.yaml",
        run_signal_mode=contour,
    )
    active_items = [x for x in (reg.get("active_items") or []) if isinstance(x, dict)]
    tools = [str(x.get("name", "")).strip() for x in active_items if str(x.get("name", "")).strip()]
    return {"registry": reg, "working_tools": tools}


def _load_shortlist_filters(shortlist_path: Path, contour: str) -> list[str]:
    if not shortlist_path.exists():
        return []
    try:
        obj = json.loads(shortlist_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    part = ((obj.get("results") or {}).get(contour) or {})
    rows = list(part.get("shortlist") or [])
    out: list[str] = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        tf = str(r.get("trend_filter", "")).strip()
        if tf and tf not in out:
            out.append(tf)
    return out


def _run_combo(
    *,
    project_root: Path,
    python_exe: str,
    symbol: str,
    timeframe: str,
    train_date: str,
    test_date: str,
    contour: str,
    repeats: int,
    threads: int,
    search_workers: int,
    cpu_max_pct: float,
    combo_filters: list[str],
    combo_id: str,
) -> dict[str, Any]:
    cmd = [
        python_exe,
        "-m",
        "mlbotnav.adaptive_auto_train",
        "--symbol",
        symbol,
        "--timeframe",
        timeframe,
        "--train-start",
        train_date,
        "--train-end",
        train_date,
        "--test-day",
        test_date,
        "--test-end-day",
        test_date,
        "--signal-mode",
        contour,
        "--trend-hypothesis-grid",
        ",".join(combo_filters),
        "--disable-backlog-active-append",
        "--contour-id",
        contour,
        "--repeats",
        str(int(repeats)),
        "--goal-net-return-pct",
        "1",
        "--allow-subgoal-candidates",
        "--min-train-rows",
        "900",
        "--n-folds",
        "2",
        "--horizons-grid",
        "5,8,12,20,30,45,60,90",
        "--min-expected-move-grid",
        "0.001,0.0015,0.002,0.003,0.004,0.005",
        "--execution-mode",
        "exchange_like",
        "--order-type",
        "market",
        "--notional-usd",
        "10",
        "--leverage",
        "10",
        "--cpu-max-pct",
        str(float(cpu_max_pct)),
        "--max-threads",
        str(int(threads)),
        "--search-workers",
        str(int(search_workers)),
        "--speed-profile",
        "turbo",
        "--temporary-unlock-readiness",
        "--unlock-reason",
        f"AKFP P7 COMBO_WORKING {contour} {combo_id}",
    ]
    run = _run(cmd, project_root)
    parsed = run.get("parsed_json") or {}
    summary_path = str(parsed.get("summary_path", "")).strip()
    adaptive_success = bool(parsed.get("success") is True)
    has_top_strategy = bool(parsed.get("top_strategy"))
    summary_exists = bool(summary_path and Path(summary_path).exists())

    # Hard-reject rule (strict):
    # a combo is accepted only when adaptive loop actually succeeded and produced top strategy.
    # This prevents "search_failed" runs from being promoted to BEST_COMBOS.
    accepted = bool(
        int(run.get("returncode", 1)) == 0
        and summary_exists
        and adaptive_success
        and has_top_strategy
    )
    reject_reasons: list[str] = []
    if int(run.get("returncode", 1)) != 0:
        reject_reasons.append("adaptive_rc_nonzero")
    if not summary_exists:
        reject_reasons.append("missing_summary_path")
    if not adaptive_success:
        reject_reasons.append("adaptive_success_false")
    if not has_top_strategy:
        reject_reasons.append("missing_top_strategy")

    return {
        "combo_id": combo_id,
        "combo_filters": combo_filters,
        "adaptive_run": run,
        "accepted": accepted,
        "reject_reasons": reject_reasons,
        "summary_path": summary_path or None,
        "acceptance_checks": {
            "returncode_zero": bool(int(run.get("returncode", 1)) == 0),
            "summary_exists": summary_exists,
            "adaptive_success": adaptive_success,
            "has_top_strategy": has_top_strategy,
        },
    }


def _contour_cycle(
    *,
    project_root: Path,
    python_exe: str,
    symbol: str,
    timeframe: str,
    train_date: str,
    test_date: str,
    contour: str,
    repeats: int,
    threads: int,
    search_workers: int,
    cpu_max_pct: float,
    max_candidates: int,
    shortlist_filters: list[str],
) -> dict[str, Any]:
    wt = _build_working_tools(project_root, contour)
    tools = list(wt["working_tools"])
    max_candidates = max(1, int(max_candidates))
    raw_combos: list[list[str]] = []
    for tf in shortlist_filters:
        if tf:
            raw_combos.append([tf])
    # Always include neutral baseline combo first.
    raw_combos.append(["none"])
    # Add medium-size mixes to test interaction effects without full-grid explosion.
    raw_combos.extend(_chunked(tools, 2))
    # Add single-tool probes to avoid over-constrained packs.
    raw_combos.extend([[t] for t in tools if t])
    if tools:
        raw_combos.append(tools)

    # Deduplicate preserving order.
    combos: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for combo in raw_combos:
        clean = tuple(x for x in combo if x)
        if not clean:
            continue
        if clean in seen:
            continue
        seen.add(clean)
        combos.append(list(clean))
        if len(combos) >= max_candidates:
            break

    runs: list[dict[str, Any]] = []
    for idx, combo in enumerate(combos, start=1):
        combo_id = f"{contour}_combo_{idx:02d}"
        runs.append(
            _run_combo(
                project_root=project_root,
                python_exe=python_exe,
                symbol=symbol,
                timeframe=timeframe,
                train_date=train_date,
                test_date=test_date,
                contour=contour,
                repeats=repeats,
                threads=threads,
                search_workers=search_workers,
                cpu_max_pct=cpu_max_pct,
                combo_filters=combo,
                combo_id=combo_id,
            )
        )

    accepted = [x for x in runs if bool(x.get("accepted"))]
    best_combo = accepted[0] if accepted else None
    return {
        "contour_id": contour,
        "working_tools": tools,
        "shortlist_filters": shortlist_filters,
        "combo_candidates_total": len(combos),
        "combo_runs": runs,
        "accepted_total": len(accepted),
        "best_combo": best_combo,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="AKFP P7: COMBO_WORKING cycle (long/short separately).")
    parser.add_argument("--policy", default="configs/akfp_policy.yaml")
    parser.add_argument("--output-dir", default="reports/akfp/combo_working")
    parser.add_argument("--shortlist-path", default="reports/akfp/shortlist/akfp_shortlist_latest.json")
    parser.add_argument("--max-candidates-override", type=int, default=0, help="Optional override for fast smoke runs.")
    parser.add_argument("--repeats-override", type=int, default=0, help="Optional override for fast smoke runs.")
    parser.add_argument("--strict-acceptance", action="store_true", help="Fail when no accepted combo found.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    policy_path = Path(args.policy)
    if not policy_path.is_absolute():
        policy_path = (project_root / policy_path).resolve()
    cfg = _load_yaml(policy_path)
    akfp = dict(cfg.get("akfp") or {})
    exe = dict(akfp.get("execution") or {})
    cal = dict(akfp.get("calibration") or {})

    symbol = str(exe.get("symbol", "SOLUSDT"))
    timeframe = str(exe.get("timeframe", "1m"))
    train_date = str(exe.get("train_date", "2026-05-19"))
    test_date = str(exe.get("test_date", "2026-05-20"))
    repeats = max(1, int(args.repeats_override) if int(args.repeats_override) > 0 else int(exe.get("repeats", 1)))
    threads = int(exe.get("threads", 8))
    search_workers = int(exe.get("search_workers", 8))
    cpu_max_pct = float(exe.get("cpu_max_pct", 85))
    max_candidates = max(
        1, int(args.max_candidates_override) if int(args.max_candidates_override) > 0 else int(cal.get("max_candidates_per_contour", 4))
    )
    strict_acceptance = bool(args.strict_acceptance) or bool(cal.get("combo_strict_acceptance", False))

    python_exe = str((project_root / ".venv" / "Scripts" / "python.exe").resolve())
    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = (project_root / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    shortlist_path = Path(args.shortlist_path)
    if not shortlist_path.is_absolute():
        shortlist_path = (project_root / shortlist_path).resolve()
    short_long = _load_shortlist_filters(shortlist_path, "long_only")
    short_short = _load_shortlist_filters(shortlist_path, "short_only")

    long_part = _contour_cycle(
        project_root=project_root,
        python_exe=python_exe,
        symbol=symbol,
        timeframe=timeframe,
        train_date=train_date,
        test_date=test_date,
        contour="long_only",
        repeats=repeats,
        threads=threads,
        search_workers=search_workers,
        cpu_max_pct=cpu_max_pct,
        max_candidates=max_candidates,
        shortlist_filters=short_long,
    )
    short_part = _contour_cycle(
        project_root=project_root,
        python_exe=python_exe,
        symbol=symbol,
        timeframe=timeframe,
        train_date=train_date,
        test_date=test_date,
        contour="short_only",
        repeats=repeats,
        threads=threads,
        search_workers=search_workers,
        cpu_max_pct=cpu_max_pct,
        max_candidates=max_candidates,
        shortlist_filters=short_short,
    )

    quality_checks = [
        {
            "name": "long_only_has_candidate",
            "ok": bool(long_part.get("accepted_total", 0) > 0),
            "details": {"accepted_total": long_part.get("accepted_total", 0)},
        },
        {
            "name": "short_only_has_candidate",
            "ok": bool(short_part.get("accepted_total", 0) > 0),
            "details": {"accepted_total": short_part.get("accepted_total", 0)},
        },
    ]
    technical_checks = [
        {
            "name": "long_only_combo_runs_exist",
            "ok": bool((long_part.get("combo_runs") or [])),
            "details": {"combo_runs": len(long_part.get("combo_runs") or [])},
        },
        {
            "name": "short_only_combo_runs_exist",
            "ok": bool((short_part.get("combo_runs") or [])),
            "details": {"combo_runs": len(short_part.get("combo_runs") or [])},
        },
    ]
    technical_failed = sum(1 for c in technical_checks if not bool(c["ok"]))
    quality_failed = sum(1 for c in quality_checks if not bool(c["ok"]))
    status = "PASS" if (technical_failed == 0 and (not strict_acceptance or quality_failed == 0)) else "FAIL"

    registries = {
        "WORKING_TOOLS": {
            "long_only": long_part.get("working_tools", []),
            "short_only": short_part.get("working_tools", []),
        },
        "BEST_COMBOS": {
            "long_only": long_part.get("best_combo"),
            "short_only": short_part.get("best_combo"),
        },
    }

    payload = {
        "status": status,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol,
        "timeframe": timeframe,
        "train_date": train_date,
        "test_date": test_date,
        "repeats": repeats,
        "max_candidates": max_candidates,
        "strict_acceptance": strict_acceptance,
        "technical_checks": technical_checks,
        "quality_checks": quality_checks,
        "shortlist_path": str(shortlist_path),
        "registries": registries,
        "results": {
            "long_only": long_part,
            "short_only": short_part,
        },
        "summary": {
            "technical_total": len(technical_checks),
            "technical_failed": int(technical_failed),
            "quality_total": len(quality_checks),
            "quality_failed": int(quality_failed),
        },
    }

    out = out_dir / f"akfp_combo_working_cycle_{symbol}_{timeframe}_{test_date}_{_utc_tag()}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    reg_working = out_dir / "WORKING_TOOLS.json"
    reg_best = out_dir / "BEST_COMBOS.json"
    reg_working.write_text(json.dumps(registries["WORKING_TOOLS"], ensure_ascii=False, indent=2), encoding="utf-8")
    reg_best.write_text(json.dumps(registries["BEST_COMBOS"], ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": status,
                "report_path": str(out),
                "working_tools_registry": str(reg_working),
                "best_combos_registry": str(reg_best),
            },
            ensure_ascii=False,
        )
    )
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
