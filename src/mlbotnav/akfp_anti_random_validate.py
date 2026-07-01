from __future__ import annotations

import argparse
import json
import subprocess
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def _parse_ymd(x: str) -> date:
    return datetime.strptime(str(x), "%Y-%m-%d").date()


def _run_validation(
    *,
    project_root: Path,
    python_exe: str,
    symbol: str,
    timeframe: str,
    train_date: str,
    test_date: str,
    contour: str,
    combo_filters: list[str],
    repeats: int,
    threads: int,
    search_workers: int,
    cpu_max_pct: float,
    stage_label: str,
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
        f"AKFP P8 {stage_label} {contour}",
    ]
    run = _run(cmd, project_root)
    parsed = run.get("parsed_json") or {}
    top = parsed.get("top_strategy") if isinstance(parsed, dict) else None
    top_card_path = None
    if isinstance(top, dict):
        raw = top.get("top_card")
        if isinstance(raw, str) and raw.strip():
            top_card_path = raw.strip()
    top_card = None
    if top_card_path and Path(top_card_path).exists():
        try:
            top_card = _load_json(Path(top_card_path))
        except Exception:
            top_card = None

    net_return_pct = None
    trades = None
    train_gate_pass = None
    if isinstance(top_card, dict):
        metrics = top_card.get("metrics") or {}
        diag = top_card.get("diagnostics") or {}
        try:
            net_return_pct = float(metrics.get("net_return_pct")) if metrics.get("net_return_pct") is not None else None
        except Exception:
            net_return_pct = None
        try:
            trades = int(metrics.get("trades")) if metrics.get("trades") is not None else None
        except Exception:
            trades = None
        train_gate_pass = bool(diag.get("train_gate_pass")) if diag.get("train_gate_pass") is not None else None

    return {
        "run": run,
        "summary_path": parsed.get("summary_path") if isinstance(parsed, dict) else None,
        "top_card_path": top_card_path,
        "top_card": top_card,
        "net_return_pct": net_return_pct,
        "trades": trades,
        "train_gate_pass": train_gate_pass,
    }


def _load_incumbent_net(project_root: Path, contour: str) -> float | None:
    root = project_root / "reports" / "top_strategy" / contour
    if not root.exists():
        return None
    cards = sorted(root.rglob("top_strategy_card.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not cards:
        return None
    try:
        card = _load_json(cards[0])
        return float(((card.get("metrics") or {}).get("net_return_pct")))
    except Exception:
        return None


def _evaluate_contour(contour: str, incumbent_net: float | None, repeat_res: dict[str, Any], holdout_res: dict[str, Any]) -> dict[str, Any]:
    r1 = int((repeat_res.get("run") or {}).get("returncode", 1)) == 0
    r2 = int((holdout_res.get("run") or {}).get("returncode", 1)) == 0
    n1 = repeat_res.get("net_return_pct")
    n2 = holdout_res.get("net_return_pct")
    g1 = bool(repeat_res.get("train_gate_pass") is True)
    g2 = bool(holdout_res.get("train_gate_pass") is True)
    t1 = repeat_res.get("trades")
    t2 = holdout_res.get("trades")
    t_ok = (isinstance(t1, int) and t1 > 0) and (isinstance(t2, int) and t2 > 0)
    stab_ok = (n1 is not None and n2 is not None and abs(float(n1) - float(n2)) <= 25.0)
    if incumbent_net is None:
        improv_ok = (n1 is not None and n2 is not None)
    else:
        improv_ok = (n1 is not None and n2 is not None and float(n1) > float(incumbent_net) and float(n2) > float(incumbent_net))

    pass_flag = bool(r1 and r2 and g1 and g2 and t_ok and stab_ok and improv_ok)
    reasons = []
    if not r1:
        reasons.append("repeat_run_failed")
    if not r2:
        reasons.append("holdout_run_failed")
    if not g1:
        reasons.append("repeat_train_gate_not_pass")
    if not g2:
        reasons.append("holdout_train_gate_not_pass")
    if not t_ok:
        reasons.append("no_trades_in_repeat_or_holdout")
    if not stab_ok:
        reasons.append("stability_diff_too_high_or_missing_net")
    if not improv_ok:
        reasons.append("not_better_than_incumbent_or_missing_net")

    return {
        "contour_id": contour,
        "pass": pass_flag,
        "reject_reasons": reasons,
        "incumbent_net_return_pct": incumbent_net,
        "repeat_net_return_pct": n1,
        "holdout_net_return_pct": n2,
        "repeat_trades": t1,
        "holdout_trades": t2,
        "repeat_train_gate_pass": g1,
        "holdout_train_gate_pass": g2,
        "stability_abs_diff": (abs(float(n1) - float(n2)) if n1 is not None and n2 is not None else None),
        "repeat_run_ok": r1,
        "holdout_run_ok": r2,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="AKFP P8: anti-random validation (repeats + holdout).")
    parser.add_argument("--policy", default="configs/akfp_policy.yaml")
    parser.add_argument("--best-combos", default="reports/akfp/combo_working/BEST_COMBOS.json")
    parser.add_argument("--output-dir", default="reports/akfp/anti_random")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    policy_path = Path(args.policy)
    if not policy_path.is_absolute():
        policy_path = (project_root / policy_path).resolve()
    cfg = _load_yaml(policy_path)
    akfp = dict(cfg.get("akfp") or {})
    exe = dict(akfp.get("execution") or {})

    symbol = str(exe.get("symbol", "SOLUSDT"))
    timeframe = str(exe.get("timeframe", "1m"))
    base_train = str(exe.get("train_date", "2026-05-19"))
    base_test = str(exe.get("test_date", "2026-05-20"))
    holdout_test = (_parse_ymd(base_test) + timedelta(days=1)).strftime("%Y-%m-%d")
    holdout_train = base_test
    repeats = max(2, int(exe.get("repeats", 2)))
    threads = int(exe.get("threads", 8))
    search_workers = int(exe.get("search_workers", 8))
    cpu_max_pct = float(exe.get("cpu_max_pct", 85))

    best_combos_path = Path(args.best_combos)
    if not best_combos_path.is_absolute():
        best_combos_path = (project_root / best_combos_path).resolve()
    best_combos = _load_json(best_combos_path) if best_combos_path.exists() else {}

    python_exe = str((project_root / ".venv" / "Scripts" / "python.exe").resolve())
    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = (project_root / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    contours = ["long_only", "short_only"]
    details: dict[str, Any] = {}
    checks: list[dict[str, Any]] = []
    winners: dict[str, Any] = {}

    for contour in contours:
        best = best_combos.get(contour) if isinstance(best_combos, dict) else None
        filters = []
        if isinstance(best, dict):
            filters = [str(x) for x in (best.get("combo_filters") or []) if str(x).strip()]
        if not filters:
            filters = ["none"]
        repeat_res = _run_validation(
            project_root=project_root,
            python_exe=python_exe,
            symbol=symbol,
            timeframe=timeframe,
            train_date=base_train,
            test_date=base_test,
            contour=contour,
            combo_filters=filters,
            repeats=repeats,
            threads=threads,
            search_workers=search_workers,
            cpu_max_pct=cpu_max_pct,
            stage_label="repeat_window",
        )
        holdout_res = _run_validation(
            project_root=project_root,
            python_exe=python_exe,
            symbol=symbol,
            timeframe=timeframe,
            train_date=holdout_train,
            test_date=holdout_test,
            contour=contour,
            combo_filters=filters,
            repeats=repeats,
            threads=threads,
            search_workers=search_workers,
            cpu_max_pct=cpu_max_pct,
            stage_label="holdout_window",
        )
        incumbent = _load_incumbent_net(project_root, contour)
        verdict = _evaluate_contour(contour, incumbent, repeat_res, holdout_res)
        details[contour] = {
            "combo_filters": filters,
            "repeat_window": {"train_date": base_train, "test_date": base_test, **repeat_res},
            "holdout_window": {"train_date": holdout_train, "test_date": holdout_test, **holdout_res},
            "verdict": verdict,
        }
        checks.append(
            {
                "name": f"{contour}_validation_executed",
                "ok": bool(verdict.get("repeat_run_ok") and verdict.get("holdout_run_ok")),
                "details": {
                    "repeat_run_ok": verdict.get("repeat_run_ok"),
                    "holdout_run_ok": verdict.get("holdout_run_ok"),
                },
            }
        )
        checks.append(
            {
                "name": f"{contour}_anti_random_pass",
                "ok": bool(verdict.get("pass")),
                "details": verdict,
                "informational": True,
            }
        )
        if bool(verdict.get("pass")):
            winners[contour] = verdict

    failed = sum(1 for c in checks if (not bool(c.get("ok"))) and (not bool(c.get("informational"))))
    strategy_pass = all(bool((details.get(c) or {}).get("verdict", {}).get("pass", False)) for c in contours)
    # P0 truth gate: PASS only when technical checks and strategy verdict are both green.
    status = "PASS" if (failed == 0 and strategy_pass) else "FAIL"
    payload = {
        "status": status,
        "strategy_pass": bool(strategy_pass),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbol": symbol,
        "timeframe": timeframe,
        "checks": checks,
        "summary": {
            "total": len(checks),
            "failed": int(failed),
            "informational_failed": int(sum(1 for c in checks if bool(c.get("informational")) and not bool(c.get("ok")))),
        },
        "details": details,
        "winners": winners,
        "decision": "accept_winners" if strategy_pass else "formal_reject_and_fix",
    }
    out = out_dir / f"akfp_anti_random_validate_{symbol}_{timeframe}_{base_test}_{_utc_tag()}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": status, "report_path": str(out)}, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
