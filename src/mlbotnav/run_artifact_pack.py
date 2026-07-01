from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _copy_if_exists(src: Path | None, dst: Path, copied: list[str]) -> bool:
    if src is None or not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    copied.append(str(dst))
    return True


def _latest(path_glob: str, root: Path) -> Path | None:
    files = sorted(root.glob(path_glob), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def _sanitize_slug(value: str) -> str:
    raw = str(value or "").strip().lower()
    if not raw:
        return ""
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789_-")
    out = "".join(ch if ch in allowed else "_" for ch in raw)
    while "__" in out:
        out = out.replace("__", "_")
    return out.strip("_")


def _choose_top_card(project_root: Path, explicit: str | None, *, contour_id: str | None = None) -> Path | None:
    if explicit:
        p = Path(explicit)
        if not p.is_absolute():
            p = (project_root / p).resolve()
        return p if p.exists() else None

    roots: list[Path] = []
    top_root = project_root / "reports" / "top_strategy"
    cid = _sanitize_slug(str(contour_id or ""))
    if cid:
        roots.append(top_root / cid)
    roots.append(top_root)

    for root in roots:
        candidates = [
            root / "TOP_PRODUCTION_LATEST.json",
            root / "TOP_LATEST.json",
            root / "TOP_EXPERIMENTAL_LATEST.json",
        ]
        for p in candidates:
            if p.exists():
                return p
    return None


def _determine_run_id(source_run_dir: Path, explicit_run_id: str | None) -> str:
    if explicit_run_id:
        return str(explicit_run_id)
    if source_run_dir.name.startswith("run_"):
        return source_run_dir.name
    manifest = source_run_dir / "state" / "run_manifest.json"
    if manifest.exists():
        try:
            run_id = str((_load_json(manifest) or {}).get("run_id", "")).strip()
            if run_id.startswith("run_"):
                return run_id
        except Exception:
            pass
    return f"run_{_utc_tag()}_artifactpack"


def _build_index(run_dir: Path) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for p in sorted(run_dir.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(run_dir).as_posix()
        files.append({"path": rel, "bytes": int(p.stat().st_size), "sha256": _sha256(p)})
    return {"files": files, "files_count": len(files)}


def _read_csv_auto(path: Path) -> tuple[pd.DataFrame, str]:
    for sep in (";", ","):
        try:
            df = pd.read_csv(path, sep=sep)
            if df.shape[1] > 1:
                return df, sep
        except Exception:
            continue
    return pd.read_csv(path), ","


def _normalize_excel_csv(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "exists": False, "changed": False, "from_sep": None, "to_sep": None}
    df, sep = _read_csv_auto(path)
    changed = bool(sep != ";")
    if changed:
        df.to_csv(path, index=False, sep=";", encoding="utf-8-sig")
    return {"path": str(path), "exists": True, "changed": changed, "from_sep": sep, "to_sep": ";"}


def main() -> int:
    parser = argparse.ArgumentParser(description="P4: collect per-run artifacts into reports/runs/<run_id>")
    parser.add_argument("--source-run-dir", default="reports/table_canon_current")
    parser.add_argument("--run-id", default=None, help="Optional explicit run id")
    parser.add_argument("--top-card", default=None, help="Optional explicit top card JSON path")
    parser.add_argument("--oos-report", default=None, help="Optional explicit OOS report path")
    parser.add_argument("--contour-id", default="auto", help="Contour namespace for top-strategy selection (auto => from OOS signal_mode)")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    source_run_dir = Path(args.source_run_dir)
    if not source_run_dir.is_absolute():
        source_run_dir = (project_root / source_run_dir).resolve()
    if not source_run_dir.exists():
        raise FileNotFoundError(f"source-run-dir not found: {source_run_dir}")

    run_id = _determine_run_id(source_run_dir, args.run_id)
    dst_run_dir = (project_root / "reports" / "runs" / run_id).resolve()
    dst_run_dir.mkdir(parents=True, exist_ok=True)

    copied: list[str] = []
    if source_run_dir != dst_run_dir:
        shutil.copytree(source_run_dir, dst_run_dir, dirs_exist_ok=True)

    # Ensure canonical subfolders for P4.
    for sub in ["pipeline", "oos", "trade_simulation", "top_strategy", "state", "data"]:
        (dst_run_dir / sub).mkdir(parents=True, exist_ok=True)

    if args.oos_report:
        oos_report_src = Path(args.oos_report)
        if not oos_report_src.is_absolute():
            oos_report_src = (project_root / oos_report_src).resolve()
    else:
        oos_report_src = None
        oos_report_src = _latest("reports/final_review/oos_report_*.json", project_root)

    oos = _load_json(oos_report_src) if oos_report_src and oos_report_src.exists() else {}
    mode_from_oos = str(((oos.get("risk_policy") or {}).get("signal_mode", ""))).strip().lower() if isinstance(oos, dict) else ""
    contour_id = str(args.contour_id or "auto").strip().lower()
    if contour_id in {"", "auto"}:
        contour_id = mode_from_oos if mode_from_oos else ""

    top_card_path = _choose_top_card(project_root, args.top_card, contour_id=contour_id)
    top_card = _load_json(top_card_path) if top_card_path and top_card_path.exists() else {}
    top_art = (top_card.get("artifacts") or {}) if isinstance(top_card, dict) else {}
    oos_art = (oos.get("artifacts") or {}) if isinstance(oos, dict) else {}
    oos_backtest_src = Path(str(oos_art.get("backtest_path", ""))) if oos_art.get("backtest_path") else None
    train_pipeline_src = Path(str(oos.get("train_pipeline_report", ""))) if oos.get("train_pipeline_report") else None
    pipeline_like_src = Path(str(oos_art.get("pipeline_like_path", ""))) if oos_art.get("pipeline_like_path") else None

    # Top-run artifacts fallback.
    top_run_dir = Path(str(top_art.get("run_dir", ""))) if top_art.get("run_dir") else None
    if top_run_dir and top_run_dir.exists():
        _copy_if_exists(top_run_dir / "top_strategy_card.json", dst_run_dir / "top_strategy" / "top_strategy_card.json", copied)
        _copy_if_exists(top_run_dir / "TOP_STRATEGY_CARD.md", dst_run_dir / "top_strategy" / "TOP_STRATEGY_CARD.md", copied)
        _copy_if_exists(top_run_dir / "ranked_candidates.json", dst_run_dir / "top_strategy" / "ranked_candidates.json", copied)

    # Core pipeline/oos/visual links.
    _copy_if_exists(oos_report_src, dst_run_dir / "oos" / "oos_report.json", copied)
    _copy_if_exists(oos_backtest_src, dst_run_dir / "oos" / "oos_backtest_trades.csv", copied)
    _copy_if_exists(train_pipeline_src, dst_run_dir / "pipeline" / "train_pipeline_report.json", copied)
    _copy_if_exists(pipeline_like_src, dst_run_dir / "pipeline" / "oos_pipeline_like.json", copied)

    # Trade simulation (prefer top-card links, fallback to top run directory files).
    trade_png_src = Path(str(top_art.get("trade_simulation_png", ""))) if top_art.get("trade_simulation_png") else None
    trade_sum_src = Path(str(top_art.get("trade_simulation_summary", ""))) if top_art.get("trade_simulation_summary") else None
    if (trade_png_src is None or not trade_png_src.exists()) and top_run_dir and top_run_dir.exists():
        trade_png_src = top_run_dir / "trade_simulation.png"
    if (trade_sum_src is None or not trade_sum_src.exists()) and top_run_dir and top_run_dir.exists():
        trade_sum_src = top_run_dir / "trade_simulation_summary.json"
    _copy_if_exists(trade_png_src, dst_run_dir / "trade_simulation" / "trade_simulation.png", copied)
    _copy_if_exists(trade_sum_src, dst_run_dir / "trade_simulation" / "trade_simulation_summary.json", copied)

    # Normalize canonical CSV tables so RU Excel opens them into columns without manual import.
    normalized_csv = []
    for rel in [
        "data/candles_canonical.csv",
        "data/feature_frame.csv",
        "data/feature_frame_full.csv",
        "data/signal_frame.csv",
        "data/execution_trace.csv",
        "data/strategy_summary.csv",
    ]:
        normalized_csv.append(_normalize_excel_csv(dst_run_dir / rel))

    # Save packing manifest.
    pack_manifest = {
        "run_id": run_id,
        "packed_at_utc": _utc_now_iso(),
        "source_run_dir": str(source_run_dir),
        "dest_run_dir": str(dst_run_dir),
        "sources": {
            "top_card": str(top_card_path) if top_card_path else None,
            "oos_report": str(oos_report_src) if oos_report_src else None,
            "oos_backtest": str(oos_backtest_src) if oos_backtest_src else None,
            "train_pipeline_report": str(train_pipeline_src) if train_pipeline_src else None,
            "pipeline_like": str(pipeline_like_src) if pipeline_like_src else None,
            "trade_simulation_png": str(trade_png_src) if trade_png_src else None,
            "trade_simulation_summary": str(trade_sum_src) if trade_sum_src else None,
            "top_run_dir": str(top_run_dir) if top_run_dir else None,
        },
        "copied_files_count": len(copied),
        "copied_files": copied,
        "normalized_csv": normalized_csv,
    }
    (dst_run_dir / "state" / "p4_pack_manifest.json").write_text(
        json.dumps(pack_manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    index_payload = _build_index(dst_run_dir)
    (dst_run_dir / "index.json").write_text(json.dumps(index_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # Update status marker.
    status_path = dst_run_dir / "state" / "status.json"
    status_obj: dict[str, Any] = {}
    if status_path.exists():
        try:
            status_obj = _load_json(status_path)
        except Exception:
            status_obj = {}
    status_obj["updated_at_utc"] = _utc_now_iso()
    status_obj["active_step"] = "P4"
    status_obj["p4_pack_ready"] = True
    status_obj["p4_copied_files_count"] = len(copied)
    status_path.write_text(json.dumps(status_obj, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "ok",
                "run_id": run_id,
                "run_dir": str(dst_run_dir),
                "copied_files_count": len(copied),
                "index_path": str(dst_run_dir / "index.json"),
                "pack_manifest": str(dst_run_dir / "state" / "p4_pack_manifest.json"),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
