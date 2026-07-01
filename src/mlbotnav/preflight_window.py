from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mlbotnav.dataset import build_feature_frame, canonical_timeframe, list_available_days, load_ohlcv_range


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _check(name: str, ok: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "details": details or {}}


def _parse_horizons(raw: str) -> list[int]:
    out: list[int] = []
    for tok in str(raw or "").split(","):
        t = tok.strip()
        if not t:
            continue
        try:
            h = int(t)
            if h > 0:
                out.append(h)
        except Exception:
            continue
    return sorted(set(out))


def main() -> int:
    parser = argparse.ArgumentParser(description="Preflight check for daily window before adaptive/search runs.")
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--timeframe", required=True)
    parser.add_argument("--train-start", required=True)
    parser.add_argument("--train-end", required=True)
    parser.add_argument("--test-day", required=True)
    parser.add_argument("--test-end-day", required=True)
    parser.add_argument("--min-train-rows", type=int, required=True)
    parser.add_argument("--n-folds", type=int, required=True)
    parser.add_argument("--horizons-grid", required=True)
    parser.add_argument("--layer", default="raw")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    qa_dir = project_root / "reports" / "qa_gate"
    qa_dir.mkdir(parents=True, exist_ok=True)
    report = qa_dir / f"preflight_window_{_utc_tag()}.json"

    checks: list[dict[str, Any]] = []
    tf = canonical_timeframe(str(args.timeframe))
    available_days = list_available_days(project_root, layer=str(args.layer))
    checks.append(_check("available_days_non_empty", len(available_days) > 0, {"count": len(available_days), "max_day": max(available_days) if available_days else None}))

    def _has_day(day: str) -> bool:
        return day in set(available_days)

    checks.append(_check("train_start_day_present", _has_day(str(args.train_start)), {"day": str(args.train_start)}))
    checks.append(_check("train_end_day_present", _has_day(str(args.train_end)), {"day": str(args.train_end)}))
    checks.append(_check("test_day_present", _has_day(str(args.test_day)), {"day": str(args.test_day)}))
    checks.append(_check("test_end_day_present", _has_day(str(args.test_end_day)), {"day": str(args.test_end_day)}))

    raw_train = None
    raw_test = None
    try:
        raw_train = load_ohlcv_range(
            project_root,
            symbol=str(args.symbol),
            timeframe=tf,
            start_date=str(args.train_start),
            end_date=str(args.train_end),
            layer=str(args.layer),
        )
        checks.append(_check("train_raw_loaded", True, {"rows": int(len(raw_train))}))
    except Exception as e:
        checks.append(_check("train_raw_loaded", False, {"error": str(e)}))
    try:
        raw_test = load_ohlcv_range(
            project_root,
            symbol=str(args.symbol),
            timeframe=tf,
            start_date=str(args.test_day),
            end_date=str(args.test_end_day),
            layer=str(args.layer),
        )
        checks.append(_check("test_raw_loaded", True, {"rows": int(len(raw_test))}))
    except Exception as e:
        checks.append(_check("test_raw_loaded", False, {"error": str(e)}))

    horizons = _parse_horizons(str(args.horizons_grid))
    checks.append(_check("horizons_non_empty", len(horizons) > 0, {"horizons": horizons}))

    wf_required = int(args.min_train_rows) + int(args.n_folds) * 20
    checks.append(_check("wf_required_positive", wf_required > 0, {"wf_required_rows": wf_required}))

    horizon_results: list[dict[str, Any]] = []
    if raw_train is not None and len(horizons) > 0:
        for h in horizons:
            try:
                ff = build_feature_frame(raw_train, horizon_bars=int(h))
                rows = int(len(ff))
                ok = rows > wf_required
                horizon_results.append({"horizon": int(h), "rows_feature": rows, "wf_required_rows": wf_required, "ok": ok})
            except Exception as e:
                horizon_results.append({"horizon": int(h), "error": str(e), "ok": False})
        checks.append(
            _check(
                "all_horizons_satisfy_walk_forward_rows",
                all(bool(x.get("ok")) for x in horizon_results),
                {"results": horizon_results},
            )
        )

    failed = int(sum(1 for c in checks if not c["ok"]))
    payload = {
        "status": "PASS" if failed == 0 else "FAIL",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "params": {
            "symbol": str(args.symbol),
            "timeframe": tf,
            "train_start": str(args.train_start),
            "train_end": str(args.train_end),
            "test_day": str(args.test_day),
            "test_end_day": str(args.test_end_day),
            "min_train_rows": int(args.min_train_rows),
            "n_folds": int(args.n_folds),
            "horizons": horizons,
            "layer": str(args.layer),
        },
        "checks": checks,
        "summary": {"total": len(checks), "failed": failed},
    }
    report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "report_path": str(report), "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
