from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import PROJECT_ROOT, compact_day, ensure_parent, rel, utc_now, write_json
from mlbotnav.stas5_v5c_review_ladder import (
    _archive_extra_visual_pngs,
    _load_source_rows,
    _make_output_paths,
    _render_annotated_review_png,
    _visual_all_entries_png_path,
)


V5C_ROOT = PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5c"
REVIEW_ROOT = V5C_ROOT / "review"
FORWARD_RUNS_DIR = V5C_ROOT / "forward" / "runs"
GALLERY_ROOT = REVIEW_ROOT / "_ALL_ROUNDS_VISUAL_REVIEW"
GALLERY_ROOT_BOLLINGER = REVIEW_ROOT / "_ALL_ROUNDS_VISUAL_REVIEW_BOLLINGER20_2SIGMA"

DEFAULT_FORWARD_RUNS = {
    "R2": "stas5_v5c_continuous_forward_20260228_20260306_20260716_155343",
    "R3": "stas5_v5c_r2q_forward_20260307_20260313_wide_v2",
    "R4": "stas5_v5c_r3_forward_20260314_20260320_wide_v1",
}


def _round_dir(round_id: str) -> Path:
    return REVIEW_ROOT / f"{round_id.lower()}_user_review"


def _day_from_compact(value: str) -> str:
    return pd.Timestamp(f"{value[:4]}-{value[4:6]}-{value[6:8]}").strftime("%Y-%m-%d")


def _available_days(round_id: str) -> list[str]:
    root = _round_dir(round_id)
    if not root.exists():
        return []
    days = []
    for item in root.iterdir():
        if item.is_dir() and item.name.isdigit() and len(item.name) == 8:
            days.append(_day_from_compact(item.name))
    return sorted(days)


def _first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def _review_paths(round_id: str, day: str) -> dict[str, Path | None]:
    compact = compact_day(day)
    base = _round_dir(round_id) / compact
    prefix = f"STAS5_V5C_{round_id}_USER_REVIEW_{compact}"
    risk_prefix = f"STAS5_V5C_{round_id}_USER_RISKGATE_REVIEW_{compact}"
    entry_csv = _first_existing([base / f"{prefix}_APPROVED.csv", base / f"{prefix}_DRAFT.csv"])
    risk_csv = _first_existing([base / f"{risk_prefix}_APPROVED.csv", base / f"{risk_prefix}_DRAFT.csv"])
    return {"base": base, "entry_csv": entry_csv, "risk_csv": risk_csv}


def _status_from_path(path: Path | None) -> str:
    if not path:
        return "DRAFT"
    return "APPROVED" if "_APPROVED" in path.name else "DRAFT"


def _load_csv(path: Path | None) -> pd.DataFrame:
    if not path:
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig")


def _normalize_entry_rows(df: pd.DataFrame, round_id: str) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    round_target = f"{round_id.lower()}_entry_y"
    if "entry_y" not in out.columns:
        if round_target in out.columns:
            out["entry_y"] = pd.to_numeric(out[round_target], errors="coerce").fillna(0).astype(int)
        elif "user_label" in out.columns:
            out["entry_y"] = out["user_label"].astype(str).str.upper().eq("GOOD").astype(int)
        else:
            out["entry_y"] = 0
    return out


def _normalize_risk_rows(df: pd.DataFrame, round_id: str) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    round_target = f"{round_id.lower()}_risk_bad_y"
    if "risk_bad_y" not in out.columns:
        if round_target in out.columns:
            out["risk_bad_y"] = pd.to_numeric(out[round_target], errors="coerce").fillna(0).astype(int)
        elif "risk_bad_target" in out.columns:
            out["risk_bad_y"] = pd.to_numeric(out["risk_bad_target"], errors="coerce").fillna(0).astype(int)
        else:
            out["risk_bad_y"] = 1
    if round_target not in out.columns:
        out[round_target] = out["risk_bad_y"]
    return out


def _copy_if_exists(src: Path | None, dst: Path) -> str:
    if not src or not src.exists():
        return ""
    ensure_parent(dst)
    shutil.copy2(src, dst)
    return rel(dst)


def _write_index(rounds: list[dict[str, Any]], out_path: Path) -> None:
    lines = [
        "# STAS5 V5C общая витрина review-графиков",
        "",
        f"Обновлено UTC: `{utc_now()}`.",
        "",
        "Сюда складываются только визуальные review-артефакты. Обучение, forward и дневные passports этот сборщик не запускает.",
        "",
        "| round | day | status | ENTRY GOOD | ENTRY BAD | RISK BAD | current review |",
        "|---|---|---|---:|---:|---:|---|",
    ]
    for row in rounds:
        lines.append(
            "| {round_id} | {day} | {status} | {entry_good} | {entry_bad} | {risk_bad} | `{current}` |".format(
                round_id=row["round_id"],
                day=row["day"],
                status=row["review_status"],
                entry_good=row["entry_good_count"],
                entry_bad=row["entry_bad_count"],
                risk_bad=row["risk_bad_count"],
                current=row.get("gallery_current_review_png", ""),
            )
        )
    ensure_parent(out_path)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_global_index(gallery_root: Path = GALLERY_ROOT) -> None:
    rows: list[dict[str, Any]] = []
    for manifest_path in sorted(gallery_root.glob("R*/STAS5_V5C_R*_REVIEW_GALLERY_MANIFEST_V1.json")):
        payload = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        rows.extend(payload.get("rows", []))
    rows = sorted(rows, key=lambda row: (str(row.get("round_id", "")), str(row.get("day", ""))))
    write_json(
        gallery_root / "STAS5_V5C_ALL_ROUNDS_REVIEW_GALLERY_MANIFEST_V1.json",
        {
            "status": "PASS_V5C_ALL_ROUNDS_REVIEW_GALLERY_READY_NO_TRAINING",
            "gallery_dir": rel(gallery_root),
            "days": len(rows),
            "rows": rows,
            "no_training": True,
            "no_forward": True,
        },
    )
    _write_index(rows, gallery_root / "STAS5_V5C_ALL_ROUNDS_REVIEW_GALLERY_INDEX_RU.md")


def build_review_gallery(
    *,
    round_id: str,
    forward_run_id: str = "",
    days: list[str] | None = None,
    bollinger_preview: bool = False,
) -> dict[str, Any]:
    round_id = str(round_id or "").upper()
    if round_id not in DEFAULT_FORWARD_RUNS and not forward_run_id:
        raise ValueError(f"ForwardRunId is required for unknown round: {round_id}")
    forward_run_id = forward_run_id or DEFAULT_FORWARD_RUNS[round_id]
    forward_run_dir = FORWARD_RUNS_DIR / forward_run_id
    if not forward_run_dir.exists():
        raise FileNotFoundError(f"forward run dir not found: {forward_run_dir}")

    selected_days = sorted(days or _available_days(round_id))
    gallery_root = GALLERY_ROOT_BOLLINGER if bollinger_preview else GALLERY_ROOT
    rows: list[dict[str, Any]] = []
    for day in selected_days:
        day = pd.Timestamp(day).strftime("%Y-%m-%d")
        compact = compact_day(day)
        review_paths = _review_paths(round_id, day)
        entry_df = _normalize_entry_rows(_load_csv(review_paths["entry_csv"]), round_id)
        risk_df = _normalize_risk_rows(_load_csv(review_paths["risk_csv"]), round_id)
        status = _status_from_path(review_paths["entry_csv"] or review_paths["risk_csv"])

        source_rows, source_path = _load_source_rows(forward_run_dir, day)
        all_entries_src = _visual_all_entries_png_path(forward_run_dir, day)
        day_paths = _make_output_paths(round_id, day, approved=status == "APPROVED")
        if bollinger_preview:
            day_paths["all_entries_png"] = day_paths["all_entries_png"].with_name(
                f"{day_paths['all_entries_png'].stem}_BOLLINGER20_2SIGMA{day_paths['all_entries_png'].suffix}"
            )
            day_paths["annotated_png"] = day_paths["annotated_png"].with_name(
                f"{day_paths['annotated_png'].stem}_BOLLINGER20_2SIGMA{day_paths['annotated_png'].suffix}"
            )
            day_paths["current_review_png"] = day_paths["current_review_png"].with_name(
                f"{day_paths['current_review_png'].stem}_BOLLINGER20_2SIGMA{day_paths['current_review_png'].suffix}"
            )

        all_entries_review = ""
        if bollinger_preview:
            if _render_annotated_review_png(
                forward_run_dir=forward_run_dir,
                day=day,
                source_rows=source_rows,
                entry_rows=[],
                risk_rows=[],
                out_path=day_paths["all_entries_png"],
                bollinger_preview=True,
            ):
                all_entries_review = rel(day_paths["all_entries_png"])
        else:
            all_entries_review = _copy_if_exists(all_entries_src, day_paths["all_entries_png"])
        annotated_created = False
        if not entry_df.empty or not risk_df.empty:
            annotated_created = _render_annotated_review_png(
                forward_run_dir=forward_run_dir,
                day=day,
                source_rows=source_rows,
                entry_rows=entry_df.to_dict("records"),
                risk_rows=risk_df.to_dict("records"),
                out_path=day_paths["annotated_png"],
                bollinger_preview=bollinger_preview,
            )
        day_current_source = day_paths["annotated_png"] if annotated_created and day_paths["annotated_png"].exists() else day_paths["all_entries_png"]
        day_current_rel = ""
        if day_current_source.exists():
            ensure_parent(day_paths["current_review_png"])
            shutil.copy2(day_current_source, day_paths["current_review_png"])
            day_current_rel = rel(day_paths["current_review_png"])
        archived_day_pngs = [] if bollinger_preview else _archive_extra_visual_pngs(day_paths["base"], {day_paths["current_review_png"]})

        gallery_dir = gallery_root / round_id / compact
        gallery_archive = gallery_dir / "_visual_archive"
        suffix = "_BOLLINGER20_2SIGMA" if bollinger_preview else ""
        gallery_all = gallery_archive / f"STAS5_V5C_{round_id}_{compact}_ALL_ENTRIES{suffix}.png"
        gallery_annotated = gallery_archive / f"STAS5_V5C_{round_id}_{compact}_ANNOTATED_ENTRY_RISK{suffix}.png"
        gallery_current = gallery_dir / f"STAS5_V5C_{round_id}_{compact}_CURRENT_REVIEW{suffix}.png"
        gallery_entry_csv = gallery_dir / f"STAS5_V5C_{round_id}_{compact}_ENTRY_REVIEW.csv"
        gallery_risk_csv = gallery_dir / f"STAS5_V5C_{round_id}_{compact}_RISKGATE_REVIEW.csv"

        gallery_all_rel = _copy_if_exists(day_paths["all_entries_png"], gallery_all)
        gallery_annotated_rel = _copy_if_exists(day_paths["annotated_png"] if annotated_created else None, gallery_annotated)
        gallery_current_rel = _copy_if_exists(day_paths["current_review_png"] if day_paths["current_review_png"].exists() else day_current_source, gallery_current)
        archived_gallery_pngs = _archive_extra_visual_pngs(gallery_dir, {gallery_current})
        if not entry_df.empty:
            ensure_parent(gallery_entry_csv)
            entry_df.to_csv(gallery_entry_csv, index=False, encoding="utf-8-sig")
        if not risk_df.empty:
            ensure_parent(gallery_risk_csv)
            risk_df.to_csv(gallery_risk_csv, index=False, encoding="utf-8-sig")

        entry_y = pd.to_numeric(entry_df.get("entry_y", pd.Series(dtype=float)), errors="coerce").fillna(0).astype(int)
        risk_y = pd.to_numeric(risk_df.get("risk_bad_y", pd.Series(dtype=float)), errors="coerce").fillna(0).astype(int)
        rows.append(
            {
                "round_id": round_id,
                "day": day,
                "compact_day": compact,
                "forward_run_id": forward_run_id,
                "source_candidates_path": rel(source_path),
                "review_status": status,
                "entry_review_csv": rel(review_paths["entry_csv"]) if review_paths["entry_csv"] else "",
                "riskgate_review_csv": rel(review_paths["risk_csv"]) if review_paths["risk_csv"] else "",
                "entry_good_count": int(entry_y.eq(1).sum()),
                "entry_bad_count": int(entry_y.eq(0).sum()) if not entry_df.empty else 0,
                "risk_bad_count": int(risk_y.eq(1).sum()) if not risk_df.empty else 0,
                "review_all_entries_png": all_entries_review,
                "review_annotated_png": rel(day_paths["annotated_png"]) if annotated_created else "",
                "review_current_png": day_current_rel,
                "gallery_all_entries_png": gallery_all_rel,
                "gallery_annotated_png": gallery_annotated_rel,
                "gallery_current_review_png": gallery_current_rel,
                "gallery_visual_archive": rel(gallery_archive),
                "bollinger_preview": bool(bollinger_preview),
                "archived_review_root_pngs": archived_day_pngs,
                "archived_gallery_root_pngs": archived_gallery_pngs,
            }
        )

    manifest = {
        "status": "PASS_V5C_REVIEW_GALLERY_READY_NO_TRAINING",
        "round_id": round_id,
        "forward_run_id": forward_run_id,
        "forward_run_dir": rel(forward_run_dir),
        "gallery_dir": rel(gallery_root / round_id),
        "bollinger_preview": bool(bollinger_preview),
        "bollinger_contract": "BOLLINGER20_2SIGMA_VISUAL_OVERLAY_FOR_REVIEW_GALLERY" if bollinger_preview else "",
        "days": len(rows),
        "rows": rows,
        "no_training": True,
        "no_forward": True,
    }
    round_manifest = gallery_root / round_id / f"STAS5_V5C_{round_id}_REVIEW_GALLERY_MANIFEST_V1.json"
    write_json(round_manifest, manifest)
    _write_index(rows, gallery_root / round_id / f"STAS5_V5C_{round_id}_REVIEW_GALLERY_INDEX_RU.md")
    _write_global_index(gallery_root)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build STAS5 V5C review graph gallery")
    parser.add_argument("--round-id", default="R2")
    parser.add_argument("--forward-run-id", default="")
    parser.add_argument("--days", default="", help="Comma-separated YYYY-MM-DD list. Empty = all review days for the round.")
    parser.add_argument("--bollinger-preview", action="store_true")
    args = parser.parse_args(argv)

    days = [part.strip() for part in args.days.split(",") if part.strip()]
    result = build_review_gallery(
        round_id=args.round_id,
        forward_run_id=args.forward_run_id,
        days=days or None,
        bollinger_preview=args.bollinger_preview,
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
