from __future__ import annotations

import argparse
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
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _latest_file(pattern: str, root: Path) -> Path | None:
    files = sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_from_cycle_report(path: Path, contour: str, cycle_name: str) -> list[dict[str, Any]]:
    obj = _load_json(path)
    part = ((obj.get("results") or {}).get(contour) or {})
    ad = part.get("adaptive_run") or {}
    parsed = ad.get("parsed_json") or {}
    summary_path_raw = str(parsed.get("summary_path", "") or "").strip()
    if not summary_path_raw:
        return []
    summary_path = Path(summary_path_raw)
    if not summary_path.is_absolute():
        summary_path = (path.parents[3] / summary_path).resolve()
    if not summary_path.exists():
        return []
    summary = _load_json(summary_path)
    best = summary.get("best_oos") or {}
    cand = best.get("candidate") or {}
    trend_filter = str(cand.get("trend_filter", "") or "").strip()
    if not trend_filter:
        return []
    trades = int(best.get("oos_trades", 0) or 0)
    ret = float(best.get("oos_net_return_pct", 0.0) or 0.0)
    score = (1 if trades > 0 else 0, ret, trades)
    return [
        {
            "cycle": cycle_name,
            "source_report": str(path),
            "summary_path": str(summary_path),
            "trend_filter": trend_filter,
            "min_abs_ema_gap": float(cand.get("min_abs_ema_gap", 0.0) or 0.0),
            "oos_trades": trades,
            "oos_net_return_pct": ret,
            "score_tuple": score,
        }
    ]


def _build_shortlist_for_contour(
    project_root: Path,
    contour: str,
    top_k: int,
    min_trades: int,
    min_net_return_pct: float,
) -> dict[str, Any]:
    sources: list[dict[str, Any]] = []
    # Latest reports from P4/P5/P6 cycles
    m = {
        "hyp_only": "reports/akfp/hyp_only/akfp_hyp_only_cycle_*.json",
        "feat_only": "reports/akfp/feat_only/akfp_feat_only_cycle_*.json",
        "hyp_plus_feat": "reports/akfp/hyp_plus_feat/akfp_hyp_plus_feat_cycle_*.json",
    }
    for cycle_name, pattern in m.items():
        p = _latest_file(pattern, project_root)
        if p is None:
            continue
        sources.extend(_extract_from_cycle_report(p, contour, cycle_name))

    # Deduplicate filters by best score.
    by_filter: dict[str, dict[str, Any]] = {}
    for row in sources:
        tf = str(row["trend_filter"])
        if tf not in by_filter or tuple(row["score_tuple"]) > tuple(by_filter[tf]["score_tuple"]):
            by_filter[tf] = row

    ranked = sorted(by_filter.values(), key=lambda r: tuple(r["score_tuple"]), reverse=True)
    shortlist = [
        r
        for r in ranked
        if int(r.get("oos_trades", 0)) >= int(min_trades)
        and float(r.get("oos_net_return_pct", 0.0)) >= float(min_net_return_pct)
    ]
    fallback_used = False
    if not shortlist:
        fallback_used = True
        shortlist = ranked
    shortlist = shortlist[: max(1, int(top_k))]
    if not shortlist:
        fallback_used = True
        shortlist = [
            {
                "cycle": "fallback",
                "source_report": None,
                "summary_path": None,
                "trend_filter": "none",
                "min_abs_ema_gap": 0.0,
                "oos_trades": 0,
                "oos_net_return_pct": 0.0,
                "score_tuple": (0, 0.0, 0),
            }
        ]

    return {
        "contour_id": contour,
        "sources_count": len(sources),
        "shortlist_count": len(shortlist),
        "fallback_used": fallback_used,
        "shortlist": shortlist,
        "trend_filters_csv": ",".join([str(x["trend_filter"]) for x in shortlist]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AKFP P3 shortlist agent: collect best filters from P4/P5/P6 and publish shortlist."
    )
    parser.add_argument("--policy", default="configs/akfp_policy.yaml")
    parser.add_argument("--output-dir", default="reports/akfp/shortlist")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    policy_path = Path(args.policy)
    if not policy_path.is_absolute():
        policy_path = (project_root / policy_path).resolve()
    cfg = _load_yaml(policy_path)
    akfp = dict(cfg.get("akfp") or {})
    cal = dict(akfp.get("calibration") or {})
    top_k = int(cal.get("shortlist_top_k", 5))
    min_trades = int(cal.get("shortlist_min_trades", 1))
    min_net_return_pct = float(cal.get("shortlist_min_net_return_pct", 0.0))

    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = (project_root / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    long_part = _build_shortlist_for_contour(
        project_root, "long_only", top_k=top_k, min_trades=min_trades, min_net_return_pct=min_net_return_pct
    )
    short_part = _build_shortlist_for_contour(
        project_root, "short_only", top_k=top_k, min_trades=min_trades, min_net_return_pct=min_net_return_pct
    )

    payload = {
        "status": "PASS",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "policy_path": str(policy_path),
        "params": {
            "shortlist_top_k": top_k,
            "shortlist_min_trades": min_trades,
            "shortlist_min_net_return_pct": min_net_return_pct,
        },
        "results": {"long_only": long_part, "short_only": short_part},
    }
    out = out_dir / f"akfp_shortlist_{_utc_tag()}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    latest = out_dir / "akfp_shortlist_latest.json"
    latest.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "PASS", "report_path": str(out), "latest_path": str(latest)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
