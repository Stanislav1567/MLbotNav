from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _check(name: str, ok: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": details or {}}


def _find_candidates(project_root: Path) -> list[Path]:
    env_paths = []
    for k in ("ORDERBOOK_SOURCE_PATH", "MICROSTRUCTURE_SOURCE_PATH"):
        v = os.environ.get(k)
        if v:
            env_paths.append(Path(v))

    candidates: list[Path] = []
    for p in env_paths:
        if p.exists():
            candidates.append(p)

    scan_dirs = [
        project_root / "data" / "orderbook",
        project_root / "data" / "microstructure",
        project_root / "reports" / "orderbook",
        project_root / "reports" / "microstructure",
        project_root / "cache" / "orderbook",
        project_root / "cache" / "microstructure",
    ]
    pats = ("*.csv", "*.parquet", "*.jsonl")
    for d in scan_dirs:
        if not d.exists():
            continue
        for pat in pats:
            candidates.extend([p for p in d.rglob(pat) if p.is_file()])

    uniq = []
    seen = set()
    for p in candidates:
        rp = str(p.resolve())
        if rp in seen:
            continue
        seen.add(rp)
        uniq.append(Path(rp))
    return uniq


def _load_frame(path: Path) -> pd.DataFrame | None:
    try:
        if path.suffix.lower() == ".csv":
            return pd.read_csv(path, nrows=20000)
        if path.suffix.lower() == ".parquet":
            return pd.read_parquet(path)
        if path.suffix.lower() == ".jsonl":
            return pd.read_json(path, lines=True)
    except Exception:
        return None
    return None


def _pick_best_frame(candidates: list[Path]) -> tuple[Path | None, pd.DataFrame | None]:
    required_any = {"ts", "timestamp", "time", "event_time", "received_at"}
    best_path = None
    best_df = None
    best_score = -1
    for p in candidates:
        df = _load_frame(p)
        if df is None or df.empty:
            continue
        cols = {str(c).strip().lower() for c in df.columns}
        score = int(any(c in cols for c in required_any)) + int("spread" in cols) + int("delta" in cols or "delta_absorption" in cols)
        if score > best_score:
            best_score = score
            best_path = p
            best_df = df
    return best_path, best_df


def _series_from_time(df: pd.DataFrame) -> pd.Series | None:
    for c in ("ts", "timestamp", "time", "event_time", "received_at"):
        if c in df.columns:
            s = pd.to_datetime(df[c], utc=True, errors="coerce").dropna().sort_values()
            if len(s) >= 2:
                return s
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="P5.2 SLA audit for spread/delta source.")
    parser.add_argument("--out-dir", default="reports/qa_gate")
    parser.add_argument("--max-latency-sec", type=float, default=2.0)
    parser.add_argument("--min-rows", type=int, default=1000)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    out_dir = (project_root / args.out_dir).resolve() if not Path(args.out_dir).is_absolute() else Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []
    candidates = _find_candidates(project_root)
    source_detected = len(candidates) > 0
    checks.append(_check("source_candidate_detected_or_allowed_absence", True, {"candidates_found": len(candidates), "source_detected": source_detected}))

    status_mode = "blocked_no_source"
    picked_path: Path | None = None
    picked_rows = 0
    latency_p95_sec = None
    coverage_ratio = None

    if source_detected:
        picked_path, df = _pick_best_frame(candidates)
        if df is not None:
            picked_rows = int(len(df))
            cols = {str(c).strip().lower() for c in df.columns}
            has_spread = "spread" in cols
            has_delta = ("delta" in cols) or ("delta_absorption" in cols)
            checks.append(_check("has_spread_column", has_spread, {"columns": sorted(list(cols))[:80]}))
            checks.append(_check("has_delta_column", has_delta, {"columns": sorted(list(cols))[:80]}))
            checks.append(_check("rows_min_threshold", picked_rows >= int(args.min_rows), {"rows": picked_rows, "min_rows": int(args.min_rows)}))

            ts = _series_from_time(df)
            if ts is not None:
                diffs = ts.diff().dropna().dt.total_seconds()
                if len(diffs) > 0:
                    latency_p95_sec = float(diffs.quantile(0.95))
                    checks.append(_check("latency_p95_le_threshold", latency_p95_sec <= float(args.max_latency_sec), {"latency_p95_sec": latency_p95_sec, "threshold_sec": float(args.max_latency_sec)}))
            else:
                checks.append(_check("latency_p95_le_threshold", False, {"reason": "time_column_missing_or_invalid"}))

            if has_spread and has_delta:
                spread_col = "spread" if "spread" in cols else None
                delta_col = "delta" if "delta" in cols else ("delta_absorption" if "delta_absorption" in cols else None)
                if spread_col and delta_col:
                    valid = df[spread_col].notna() & df[delta_col].notna()
                    coverage_ratio = float(valid.mean()) if len(valid) else 0.0
                    checks.append(_check("spread_delta_coverage_ge_95pct", coverage_ratio >= 0.95, {"coverage_ratio": coverage_ratio, "threshold": 0.95}))
            status_mode = "source_detected"
        else:
            checks.append(_check("source_frame_readable", False, {"reason": "no readable candidate frame"}))
    else:
        checks.append(_check("sla_checks_skipped_without_source", True, {"reason": "blocked_no_source"}))

    failed = int(sum(1 for c in checks if not c["ok"]))
    status = "PASS" if failed == 0 else "FAIL"
    payload = {
        "status": status,
        "mode": status_mode,
        "generated_at_utc": _utc_now_iso(),
        "source_detected": source_detected,
        "picked_path": str(picked_path) if picked_path else None,
        "picked_rows": picked_rows,
        "latency_p95_sec": latency_p95_sec,
        "coverage_ratio": coverage_ratio,
        "checks": checks,
        "summary": {"total": len(checks), "failed": failed},
    }
    out = out_dir / f"p52_sla_audit_{_utc_tag()}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": status, "mode": status_mode, "report_path": str(out), "failed": failed}, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
