from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _copy_if_exists(src: Path, dst: Path) -> None:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def _format_return_tag(net_return_pct: float) -> str:
    sign = "+" if net_return_pct >= 0 else "-"
    return f"{sign}{abs(net_return_pct):.4f}pct"


def _window_label(test_day: str, test_end_day: str) -> str:
    try:
        d1 = datetime.strptime(str(test_day), "%Y-%m-%d").date()
        d2 = datetime.strptime(str(test_end_day), "%Y-%m-%d").date()
        days = max(1, (d2 - d1).days + 1)
        return f"{days}-day test"
    except Exception:
        if str(test_end_day) == str(test_day):
            return "1-day test"
        return f"test {test_day}..{test_end_day}"


def _build_tmp_pipeline_like(project_root: Path, oos_report: dict[str, Any], out_dir: Path) -> Path:
    tmp = out_dir / "_tmp_pipeline_like_for_render.json"
    payload = {
        "symbol": oos_report.get("symbol"),
        "timeframe": oos_report.get("timeframe"),
        "strategy": oos_report.get("strategy", {}),
        "risk_policy": oos_report.get("risk_policy", {}),
        "artifacts": oos_report.get("artifacts", {}),
    }
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return tmp


def _python_candidates(project_root: Path) -> list[Path]:
    cands: list[Path] = []
    seen: set[str] = set()
    for p in [Path(sys.executable), project_root / ".venv" / "Scripts" / "python.exe"]:
        key = str(p).lower()
        if key in seen:
            continue
        seen.add(key)
        if p.exists():
            cands.append(p)
    return cands


def _has_matplotlib(project_root: Path, py_exe: Path) -> bool:
    cmd = [str(py_exe), "-c", "import matplotlib; import matplotlib.pyplot"]
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    try:
        p = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, env=env, timeout=60)
        return p.returncode == 0
    except Exception:
        return False


def _pick_python_for_render(project_root: Path) -> tuple[Path | None, list[str]]:
    tried: list[str] = []
    for py in _python_candidates(project_root):
        ok = _has_matplotlib(project_root, py)
        tried.append(f"{py}::matplotlib={'ok' if ok else 'missing'}")
        if ok:
            return py, tried
    return None, tried


def _render_trade_simulation(
    project_root: Path, pipeline_like_path: Path, test_day: str, test_end_day: str
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    py_exe, tried = _pick_python_for_render(project_root)
    if py_exe is None:
        return None, {
            "stage": "precheck",
            "reason": "matplotlib_not_found_in_available_interpreters",
            "interpreters": tried,
        }
    cmd = [
        str(py_exe),
        "-m",
        "mlbotnav.render_trade_simulation",
        "--pipeline-report",
        str(pipeline_like_path),
        "--date",
        str(test_day),
        "--end-date",
        str(test_end_day),
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    try:
        proc = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True, env=env, timeout=300)
    except Exception as exc:
        return None, {"stage": "spawn", "error": str(exc), "python": str(py_exe), "interpreters": tried}
    if proc.returncode != 0:
        return None, {
            "stage": "run",
            "returncode": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-3000:],
            "stderr_tail": (proc.stderr or "")[-3000:],
            "python": str(py_exe),
            "interpreters": tried,
        }
    lines = [x.strip() for x in (proc.stdout or "").splitlines() if x.strip()]
    for line in reversed(lines):
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                return obj, None
        except Exception:
            continue
    return None, {
        "stage": "parse",
        "returncode": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-3000:],
        "stderr_tail": (proc.stderr or "")[-3000:],
        "python": str(py_exe),
        "interpreters": tried,
    }


def _load_best_positive_from_history(history_path: Path) -> dict[str, Any] | None:
    if not history_path.exists():
        return None
    best: dict[str, Any] | None = None
    best_ret = -1e18
    for raw in history_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if not isinstance(obj, dict):
            continue
        ret = float((obj.get("metrics") or {}).get("net_return_pct", -1e18))
        if _is_production_candidate(obj) and ret > best_ret:
            best = obj
            best_ret = ret
    return best


def _derive_train_gate_pass(card: dict[str, Any]) -> bool:
    diag = card.get("diagnostics") or {}
    if "train_gate_pass" in diag:
        return bool(diag.get("train_gate_pass", False))
    summary_path = card.get("summary_path")
    if not summary_path:
        return False
    try:
        summary = _load_json(Path(str(summary_path)))
    except Exception:
        return False
    return bool(summary.get("best_train_gate_pass", False))


def _is_production_candidate(card: dict[str, Any]) -> bool:
    if not isinstance(card, dict):
        return False
    metrics = card.get("metrics") or {}
    risk = card.get("risk_policy") or {}
    diag = card.get("diagnostics") or {}
    ret = float(metrics.get("net_return_pct", -1e18))
    trades = int(metrics.get("trades", 0))
    mode = str(risk.get("execution_mode", "")).strip().lower()
    gate_pass = _derive_train_gate_pass(card)
    return ret > 0.0 and trades > 0 and mode == "exchange_like" and gate_pass


def _load_best_production_from_history(root: Path) -> dict[str, Any] | None:
    history_candidates = [
        root / "TOP_PRODUCTION_HISTORY.jsonl",
        root / "TOP_HISTORY.jsonl",
    ]
    best: dict[str, Any] | None = None
    best_ret = -1e18
    for hist in history_candidates:
        if not hist.exists():
            continue
        for raw in hist.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if not isinstance(obj, dict) or not _is_production_candidate(obj):
                continue
            ret = float((obj.get("metrics") or {}).get("net_return_pct", -1e18))
            if ret > best_ret:
                best = obj
                best_ret = ret
    # Legacy fallback: if history files don't contain modern fields, inspect TOP_LATEST.
    latest = root / "TOP_LATEST.json"
    if latest.exists():
        try:
            obj = _load_json(latest)
        except Exception:
            obj = None
        if isinstance(obj, dict) and _is_production_candidate(obj):
            ret = float((obj.get("metrics") or {}).get("net_return_pct", -1e18))
            if ret > best_ret:
                best = obj
    return best


def _repair_latest_aliases(root: Path) -> None:
    best_prod = _load_best_production_from_history(root)
    if not isinstance(best_prod, dict):
        # Fail-closed: no strict production candidate -> remove stale production aliases.
        for p in [root / "TOP_PRODUCTION_LATEST.json", root / "TOP_LATEST.json"]:
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass
        return
    patched = dict(best_prod)
    test_day = str(patched.get("test_day", ""))
    test_end_day = str(patched.get("test_end_day", test_day))
    metrics = patched.get("metrics") or {}
    net_return_pct = float(metrics.get("net_return_pct", 0.0))
    patched["tagline"] = f"Best OOS: {net_return_pct:.4f}% for {_window_label(test_day, test_end_day)}"
    patched["selection_rule"] = (
        "max(oos.backtest.net_return_pct) within adaptive run; "
        "publish only if exchange_like and train_gate_pass=true"
    )
    patched["published_as_latest"] = True
    patched["publish_class"] = "production_top"
    patched["latest_skip_reason"] = None
    diagnostics = dict(patched.get("diagnostics") or {})
    diagnostics["train_gate_pass"] = bool(_derive_train_gate_pass(patched))
    patched["diagnostics"] = diagnostics
    payload = json.dumps(patched, ensure_ascii=False, indent=2)
    (root / "TOP_PRODUCTION_LATEST.json").write_text(payload, encoding="utf-8")
    (root / "TOP_LATEST.json").write_text(payload, encoding="utf-8")


def publish_best_oos_from_adaptive(
    *,
    project_root: Path,
    summary_path: Path,
    summary: dict[str, Any],
    top_root: Path | None = None,
) -> dict[str, Any] | None:
    best = summary.get("best_oos")
    if not isinstance(best, dict):
        return None
    oos_report_raw = best.get("oos_report")
    if not oos_report_raw:
        return None

    oos_report_path = Path(str(oos_report_raw))
    if not oos_report_path.exists():
        return None

    oos = _load_json(oos_report_path)
    backtest_path = Path(str((oos.get("artifacts") or {}).get("backtest_path", "")))
    train_report_path = Path(str(oos.get("train_pipeline_report", "")))

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    symbol = str(oos.get("symbol", summary.get("symbol", "UNKNOWN")))
    timeframe = str(oos.get("timeframe", summary.get("timeframe", "1m")))
    test_day = str(oos.get("test_day", summary.get("test_day", "")))
    test_end_day = str(oos.get("test_end_day", summary.get("test_end_day", test_day)))
    signal_mode = str((oos.get("risk_policy", {}) or {}).get("signal_mode", "both"))
    execution_mode = str((oos.get("risk_policy", {}) or {}).get("execution_mode", "research")).strip().lower()
    train_gate_pass = bool(best.get("train_gate_pass", False))
    bt = oos.get("backtest", {}) if isinstance(oos, dict) else {}
    net_return_pct = float(bt.get("net_return_pct", 0.0))
    tf_tag = timeframe.upper()
    ret_tag = _format_return_tag(net_return_pct)
    # Folder name is intentionally human-readable for quick visual scan.
    day_tag = test_day if test_end_day == test_day else f"{test_day}_to_{test_end_day}"
    slug = f"{symbol}_{timeframe}_{day_tag}_{ts}_MODE-{signal_mode.upper()}_TF-{tf_tag}_RET-{ret_tag}"
    root = (top_root.resolve() if top_root is not None else (project_root / "reports" / "top_strategy").resolve())
    root.mkdir(parents=True, exist_ok=True)
    run_dir = root / f"top_{slug}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Copy core artifacts to immutable run dir.
    oos_copy = run_dir / "oos_report.json"
    bt_copy = run_dir / "oos_backtest_trades.csv"
    train_copy = run_dir / "train_pipeline_report.json"
    _copy_if_exists(oos_report_path, oos_copy)
    _copy_if_exists(backtest_path, bt_copy)
    _copy_if_exists(train_report_path, train_copy)

    # Build stable render input inside run_dir (no temporary/deleted references).
    render_input = run_dir / "pipeline_like_for_render.json"
    render_payload = {
        "symbol": oos.get("symbol"),
        "timeframe": oos.get("timeframe"),
        "strategy": oos.get("strategy", {}),
        "risk_policy": oos.get("risk_policy", {}),
        "artifacts": {
            "backtest_path": str(bt_copy if bt_copy.exists() else backtest_path),
        },
    }
    render_input.write_text(json.dumps(render_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # Build dedicated render for exactly this OOS backtest.
    render, render_err = _render_trade_simulation(project_root, render_input, test_day=test_day, test_end_day=test_end_day)
    if not isinstance(render, dict):
        render = {}

    render_png = Path(str(render.get("visual_png", ""))) if render.get("visual_png") else None
    render_json = Path(str(render.get("summary_json", ""))) if render.get("summary_json") else None
    render_verified = False
    render_meta: dict[str, Any] | None = None
    if render_json and render_json.exists():
        try:
            render_meta = _load_json(render_json)
        except Exception:
            render_meta = None
    expected_bt_path = bt_copy if bt_copy.exists() else backtest_path
    expected_backtest = str(expected_bt_path.resolve()) if expected_bt_path.exists() else str(expected_bt_path)
    got_backtest = str((render_meta or {}).get("backtest_path", ""))
    if render_png and render_png.exists() and render_json and render_json.exists() and expected_backtest and got_backtest:
        if Path(got_backtest).resolve() == Path(expected_backtest).resolve():
            _copy_if_exists(render_png, run_dir / "trade_simulation.png")
            _copy_if_exists(render_json, run_dir / "trade_simulation_summary.json")
            # Normalize summary links to stable in-run files.
            try:
                stable_sum = _load_json(run_dir / "trade_simulation_summary.json")
                stable_sum["pipeline_report"] = str(render_input.resolve())
                stable_sum["backtest_path"] = expected_backtest
                stable_sum["oos_report"] = str(oos_copy.resolve()) if oos_copy.exists() else str(oos_report_path)
                (run_dir / "trade_simulation_summary.json").write_text(
                    json.dumps(stable_sum, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
            except Exception:
                pass
            render_verified = True
        else:
            render_err = {
                "stage": "verify",
                "reason": "render_backtest_mismatch",
                "expected_backtest_path": expected_backtest,
                "got_backtest_path": got_backtest,
            }
    if not render_verified:
        if not isinstance(render_err, dict):
            render_err = {
                "stage": "verify",
                "reason": "render_missing_or_unverified",
                "expected_backtest_path": expected_backtest,
            }
        (run_dir / "render_error.log").write_text(
            json.dumps(render_err, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    trades = 0
    wins = 0
    losses = 0
    long_entries = 0
    short_entries = 0
    if backtest_path.exists():
        # Keep mixed-type diagnostic columns stable (time/exit/meta) without chunk-type warnings.
        df = pd.read_csv(backtest_path, low_memory=False)
        if "net_return" in df.columns:
            t = df[df["net_return"].abs() > 1e-12].copy()
            trades = int(len(t))
            if "side" in t.columns:
                long_entries = int((t["side"] > 0).sum())
                short_entries = int((t["side"] < 0).sum())
            wins = int((t["net_return"] > 0).sum())
            losses = int((t["net_return"] < 0).sum())

    publish_as_latest = (
        (float(net_return_pct) > 0.0)
        and (int(trades) > 0)
        and (execution_mode == "exchange_like")
        and bool(train_gate_pass)
    )
    skip_reasons: list[str] = []
    if float(net_return_pct) <= 0.0:
        skip_reasons.append("non_positive_oos")
    if int(trades) <= 0:
        skip_reasons.append("no_trades")
    if execution_mode != "exchange_like":
        skip_reasons.append("execution_mode_not_exchange_like")
    if not bool(train_gate_pass):
        skip_reasons.append("train_gate_not_passed")
    latest_skip_reason = None if publish_as_latest else ",".join(skip_reasons) if skip_reasons else "publish_policy_blocked"

    trade_png_out = run_dir / "trade_simulation.png"
    trade_json_out = run_dir / "trade_simulation_summary.json"
    window_label = _window_label(test_day, test_end_day)
    card = {
        "label": f"TOP-1 | {symbol} | {timeframe} | test_day={test_day}",
        "tagline": f"Best OOS: {net_return_pct:.4f}% for {window_label}",
        "selection_rule": "max(oos.backtest.net_return_pct) within adaptive run; publish only if exchange_like and train_gate_pass=true",
        "summary_path": str(summary_path),
        "adaptive_run_utc": summary.get("run_utc"),
        "adaptive_repeat": best.get("repeat"),
        "symbol": symbol,
        "timeframe": timeframe,
        "test_day": test_day,
        "test_end_day": test_end_day,
        "signal_mode": signal_mode,
        "goal_net_return_pct_day": oos.get("goal_net_return_pct_day"),
        "goal_pass": oos.get("goal_pass"),
        "published_as_latest": publish_as_latest,
        "publish_class": ("production_top" if publish_as_latest else "experimental_top"),
        "latest_skip_reason": latest_skip_reason,
        "diagnostics": {
            "likely_issue": "high_turnover_with_leverage_costs" if (float(bt.get("leverage", 1.0)) > 1.0 and int(trades) >= 100) else None,
            "train_gate_pass": bool(train_gate_pass),
            "train_gate_reasons": best.get("train_gate_reasons", []),
            "leverage": bt.get("leverage", (oos.get("risk_policy", {}) or {}).get("leverage")),
            "effective_notional_usd": bt.get(
                "effective_notional_usd",
                ((oos.get("risk_policy", {}) or {}).get("effective_notional_usd")),
            ),
            "avg_trade_return": bt.get("avg_trade_return"),
            "trades": int(trades),
        },
        "metrics": {
            "net_return_pct": bt.get("net_return_pct"),
            "hit_rate": bt.get("hit_rate"),
            "max_drawdown_pct": bt.get("max_drawdown_pct"),
            "trades": bt.get("trades", trades),
            "wins": wins,
            "losses": losses,
            "long_entries": long_entries,
            "short_entries": short_entries,
            "net_pnl_total_usd": bt.get("net_pnl_total_usd"),
            "notional_usd": (oos.get("risk_policy", {}) or {}).get("notional_usd"),
        },
        "strategy": oos.get("strategy", {}),
        "risk_policy": oos.get("risk_policy", {}),
        "artifacts": {
            "run_dir": str(run_dir),
            "oos_report": str(oos_copy),
            "oos_backtest_trades": str(bt_copy),
            "train_pipeline_report": str(train_copy),
            "render_source": "exact_oos_backtest_only",
            "trade_simulation_png": str(trade_png_out) if trade_png_out.exists() else None,
            "trade_simulation_summary": str(trade_json_out) if trade_json_out.exists() else None,
        },
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    # Teaching material: explain why this one is top across repeats.
    history = summary.get("history", []) if isinstance(summary, dict) else []
    rank_rows: list[dict[str, Any]] = []
    for step in history:
        if not isinstance(step, dict):
            continue
        rank_rows.append(
            {
                "repeat": step.get("repeat"),
                "status": step.get("status"),
                "oos_net_return_pct": step.get("oos_net_return_pct"),
                "goal_pass": step.get("goal_pass"),
                "oos_report": step.get("oos_report"),
            }
        )
    rank_rows = sorted(
        rank_rows,
        key=lambda x: float(x.get("oos_net_return_pct") if x.get("oos_net_return_pct") is not None else -1e18),
        reverse=True,
    )
    (run_dir / "ranked_candidates.json").write_text(
        json.dumps({"ranked_by_oos_net_return_pct": rank_rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    md_lines = [
        f"# TOP-1 Strategy Card ({symbol} {timeframe})",
        "",
        f"- Label: `{card['label']}`",
        f"- Test day: `{test_day}`",
        f"- Best OOS net return: `{float(bt.get('net_return_pct', 0.0)):.4f}%`",
        f"- Adaptive repeat: `{best.get('repeat')}`",
        f"- Goal `{oos.get('goal_net_return_pct_day')}%` pass: `{oos.get('goal_pass')}`",
        "",
        "## Quick Metrics",
        f"- Trades: `{card['metrics']['trades']}`",
        f"- Wins/Losses: `{wins}/{losses}`",
        f"- Long/Short: `{long_entries}/{short_entries}`",
        f"- Hit rate: `{bt.get('hit_rate')}`",
        f"- Max drawdown pct: `{bt.get('max_drawdown_pct')}`",
        f"- Net PnL USD: `{bt.get('net_pnl_total_usd')}`",
        "",
        "## Why This Strategy Was Selected",
        "- Selection rule: maximum OOS net return across adaptive repeats.",
        "- Details of all repeats are in `ranked_candidates.json`.",
        "",
        "## Artifacts",
        "- `oos_report.json`",
        "- `oos_backtest_trades.csv`",
        "- `train_pipeline_report.json`",
        "- `trade_simulation.png`",
        "- `trade_simulation_summary.json`",
    ]
    (run_dir / "TOP_STRATEGY_CARD.md").write_text("\n".join(md_lines), encoding="utf-8")
    (run_dir / "top_strategy_card.json").write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")

    latest_path = root / "TOP_LATEST.json"
    prod_latest_path = root / "TOP_PRODUCTION_LATEST.json"
    exp_latest_path = root / "TOP_EXPERIMENTAL_LATEST.json"
    history_path = root / "TOP_HISTORY.jsonl"
    prod_history_path = root / "TOP_PRODUCTION_HISTORY.jsonl"
    exp_history_path = root / "TOP_EXPERIMENTAL_HISTORY.jsonl"
    with history_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(card, ensure_ascii=False) + "\n")
    if publish_as_latest:
        latest_path.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
        prod_latest_path.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
        with prod_history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(card, ensure_ascii=False) + "\n")
    else:
        exp_latest_path.write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
        with exp_history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(card, ensure_ascii=False) + "\n")
        # Auto-heal: if TOP_LATEST currently points to non-positive run, restore best positive from history.
        current_latest: dict[str, Any] | None = None
        if latest_path.exists():
            try:
                current_latest = _load_json(latest_path)
            except Exception:
                current_latest = None
        cur_ret = float(((current_latest or {}).get("metrics") or {}).get("net_return_pct", -1e18))
        cur_trades = int(((current_latest or {}).get("metrics") or {}).get("trades", 0))
        if cur_ret <= 0.0 or cur_trades <= 0:
            healed = _load_best_positive_from_history(history_path)
            if isinstance(healed, dict):
                latest_path.write_text(json.dumps(healed, ensure_ascii=False, indent=2), encoding="utf-8")
                prod_latest_path.write_text(json.dumps(healed, ensure_ascii=False, indent=2), encoding="utf-8")

    # Always heal latest aliases to avoid legacy drift from old artifact formats.
    _repair_latest_aliases(root)

    return {
        "top_latest": str(latest_path) if publish_as_latest else None,
        "top_production_latest": str(prod_latest_path) if publish_as_latest else None,
        "top_experimental_latest": str(exp_latest_path) if not publish_as_latest else None,
        "published_as_latest": publish_as_latest,
        "latest_skip_reason": latest_skip_reason,
        "top_run_dir": str(run_dir),
        "top_card": str(run_dir / "top_strategy_card.json"),
    }
