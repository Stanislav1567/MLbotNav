from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import PROJECT_ROOT, compact_day, ensure_parent, iter_days, rel, utc_now, write_json
from mlbotnav.stas5_v5_forward_visual_review import (
    DECISION_COLUMN,
    SCORE_COLUMN,
    _build_strength_strip_rows,
    render_forward_day_overview,
)
from mlbotnav.visual_entry_low_anchor_suggester import _load_ohlcv, _source_csv


STATUS_PASS = "PASS_V5_BASE_R2_STYLE_REVIEW_GALLERY_READY_NO_TRAINING_NO_FORWARD"
STATUS_WARN = "WARN_V5_BASE_R2_STYLE_REVIEW_GALLERY_READY_WITH_NOTES"
SYMBOL = "SOLUSDT"
TIMEFRAME = "1m"
V5_ROOT = PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5"
V5C_REVIEW_ROOT = PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5c" / "review"
DEFAULT_GALLERY_ROOT = V5C_REVIEW_ROOT / "_BASE_R2_STYLE_VISUAL_REVIEW_20260127_20260227"


def _ml_ready_path(day: str) -> Path:
    compact = compact_day(day)
    return (
        V5_ROOT
        / "market_passports"
        / compact
        / f"STAS5_V5_MARKET_PASSPORT_{compact}_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv"
    )


def _load_day_ohlcv(day: str) -> pd.DataFrame:
    path = _source_csv(PROJECT_ROOT, day, TIMEFRAME, SYMBOL)
    if not path.exists():
        raise FileNotFoundError(f"OHLCV source not found for {day}: {path}")
    return _load_ohlcv(path)


def _load_strength_context(start_day: str, end_day: str) -> pd.DataFrame:
    start = (pd.Timestamp(start_day) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    end = (pd.Timestamp(end_day) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    frames: list[pd.DataFrame] = []
    for day in iter_days(start, end):
        path = _source_csv(PROJECT_ROOT, day, TIMEFRAME, SYMBOL)
        if path.exists():
            frames.append(_load_ohlcv(path))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True).drop_duplicates(subset=["open_time_utc"]).sort_values("open_time_utc")


def _prepare_base_plot_rows(df: pd.DataFrame, day: str) -> pd.DataFrame:
    out = df.copy()
    out["day"] = day
    out["candidate_id"] = out["candidate_id"].astype(str).str.upper()
    out["entry_ts"] = pd.to_datetime(out["entry_time_utc"], utc=True, errors="raise", format="mixed")
    entry_y = pd.to_numeric(out["entry_y"], errors="coerce").fillna(0).astype(int)
    out[DECISION_COLUMN] = entry_y.map({1: "ENTER", 0: "SKIP"}).fillna("SKIP")
    out[SCORE_COLUMN] = entry_y.astype(float)
    if "entry_price_visual" not in out.columns:
        out["entry_price_visual"] = pd.to_numeric(out["entry_price_5bps"], errors="coerce")
    return out


def _annotation_rows(rows: pd.DataFrame) -> list[dict[str, Any]]:
    out = rows[["day", "candidate_id", "record_id", "entry_time_utc", "entry_y"]].copy()
    out["entry_review_label"] = out["entry_y"].map(lambda value: "GOOD" if int(value) == 1 else "BAD")
    out["user_label"] = out["entry_review_label"]
    return out.to_dict("records")


def _write_contact_sheet(image_paths: list[Path], out_path: Path, title: str) -> str:
    try:
        from PIL import Image, ImageDraw
    except Exception:
        return ""
    if not image_paths:
        return ""
    thumb_w = 760
    pad = 18
    label_h = 34
    cols = 4
    thumbs = []
    for path in image_paths:
        image = Image.open(path).convert("RGB")
        ratio = thumb_w / image.width
        image = image.resize((thumb_w, max(1, int(image.height * ratio))))
        thumbs.append((path, image))
    max_h = max(image.height for _, image in thumbs)
    row_count = math.ceil(len(thumbs) / cols)
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = 70 + row_count * (max_h + label_h + pad) + pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), (18, 22, 25))
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 18), title, fill=(245, 245, 245))
    for index, (path, image) in enumerate(thumbs):
        col = index % cols
        row = index // cols
        x = pad + col * (thumb_w + pad)
        y = 60 + row * (max_h + label_h + pad)
        draw.text((x, y), path.name[:100], fill=(255, 230, 0))
        sheet.paste(image, (x, y + label_h))
    ensure_parent(out_path)
    sheet.save(out_path, quality=92)
    return rel(out_path)


def _write_index(rows: list[dict[str, Any]], out_path: Path, manifest: dict[str, Any]) -> None:
    lines = [
        "# STAS5 V5 base review gallery в стиле R2/R3/R4",
        "",
        f"Обновлено UTC: `{manifest['created_utc']}`.",
        "",
        "Это только визуальная галерея для ручной проверки базы. Обучение и forward не запускались.",
        "",
        f"Статус: `{manifest['status']}`.",
        f"Папка: `{manifest['gallery_dir']}`.",
        f"Дней: `{manifest['days']}`.",
        f"Rows: `{manifest['rows_total']}`.",
        f"GOOD: `{manifest['entry_good_total']}`.",
        f"BAD/SKIP: `{manifest['entry_bad_total']}`.",
        "",
        "Смысл маркеров базы:",
        "",
        "- `entry_y=1` -> зеленый треугольник `ENTER` + зеленый круг `GOOD`.",
        "- `entry_y=0` -> желтый `X/SKIP` + красный квадрат `BAD`.",
        "- RiskGate в базовой галерее не рисуется.",
        "- Полосы силы/волны снизу визуальные, не являются X для обучения.",
        "",
        "## День за днем",
        "",
        "| day | rows | GOOD | BAD/SKIP | current review | all entries |",
        "|---|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {day} | {rows} | {good} | {bad} | `{current}` | `{all_entries}` |".format(
                day=row["day"],
                rows=row["rows"],
                good=row["entry_good_count"],
                bad=row["entry_bad_count"],
                current=row["current_review_png"],
                all_entries=row["all_entries_png"],
            )
        )
    ensure_parent(out_path)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_base_review_gallery(
    *,
    start_day: str = "2026-01-27",
    end_day: str = "2026-02-27",
    gallery_root: Path = DEFAULT_GALLERY_ROOT,
) -> dict[str, Any]:
    start_day = pd.Timestamp(start_day).strftime("%Y-%m-%d")
    end_day = pd.Timestamp(end_day).strftime("%Y-%m-%d")
    gallery_root.mkdir(parents=True, exist_ok=True)
    strength_context = _load_strength_context(start_day, end_day)
    rows_out: list[dict[str, Any]] = []
    errors: list[str] = []
    current_pngs: list[Path] = []

    for day in iter_days(start_day, end_day):
        compact = compact_day(day)
        day_dir = gallery_root / compact
        day_dir.mkdir(parents=True, exist_ok=True)
        ml_path = _ml_ready_path(day)
        if not ml_path.exists():
            errors.append(f"missing_ml_ready:{rel(ml_path)}")
            continue
        try:
            day_df = _load_day_ohlcv(day)
            source = pd.read_csv(ml_path, encoding="utf-8-sig")
            plot_rows = _prepare_base_plot_rows(source, day)
            day_context = strength_context if not strength_context.empty else day_df
            strength_rows = _build_strength_strip_rows(
                day_context,
                day,
                has_next_render_day=bool(
                    not day_context.empty
                    and day_context["open_time_utc"].ge(pd.Timestamp(day, tz="UTC") + pd.Timedelta(days=1)).any()
                ),
            )
            all_entries_png = day_dir / f"STAS5_V5_BASE_R2_STYLE_REVIEW_{compact}_ALL_ENTRIES.png"
            current_png = day_dir / f"STAS5_V5_BASE_R2_STYLE_REVIEW_{compact}_CURRENT_REVIEW.png"
            render_forward_day_overview(
                day_df=day_df,
                rows=plot_rows,
                strength_hour_rows=strength_rows["hour_rows"],
                strength_macro_wave_rows=strength_rows["macro_wave_rows"],
                day=day,
                symbol=SYMBOL,
                timeframe=TIMEFRAME,
                out_path=all_entries_png,
                review_annotations=None,
                title_prefix="STAS5 V5 base teacher visual review",
            )
            render_forward_day_overview(
                day_df=day_df,
                rows=plot_rows,
                strength_hour_rows=strength_rows["hour_rows"],
                strength_macro_wave_rows=strength_rows["macro_wave_rows"],
                day=day,
                symbol=SYMBOL,
                timeframe=TIMEFRAME,
                out_path=current_png,
                review_annotations={
                    str(row["candidate_id"]).upper(): ["GOOD"] if int(row["entry_y"]) == 1 else ["BAD"]
                    for row in _annotation_rows(plot_rows)
                },
                review_panel_title="BASE TEACHER MARKERS",
                title_prefix="STAS5 V5 base teacher visual review",
            )
            entry_y = pd.to_numeric(source["entry_y"], errors="coerce").fillna(0).astype(int)
            row = {
                "day": day,
                "compact_day": compact,
                "rows": int(len(source)),
                "entry_good_count": int(entry_y.eq(1).sum()),
                "entry_bad_count": int(entry_y.eq(0).sum()),
                "ml_ready_csv": rel(ml_path),
                "all_entries_png": rel(all_entries_png),
                "current_review_png": rel(current_png),
                "strength_context_rows": int(len(day_context)),
                "no_training": True,
                "no_forward": True,
            }
            rows_out.append(row)
            current_pngs.append(current_png)
        except Exception as exc:
            errors.append(f"{day}:{type(exc).__name__}:{exc}")

    contact_sheet = _write_contact_sheet(
        current_pngs,
        gallery_root / "00_CONTACT_SHEET_BASE_R2_STYLE_CURRENT_REVIEW.png",
        f"BASE R2-style review {start_day}..{end_day}",
    )
    manifest = {
        "status": STATUS_PASS if not errors else STATUS_WARN,
        "created_utc": utc_now(),
        "gallery_dir": rel(gallery_root),
        "start_day": start_day,
        "end_day": end_day,
        "days": len(rows_out),
        "rows_total": int(sum(int(row["rows"]) for row in rows_out)),
        "entry_good_total": int(sum(int(row["entry_good_count"]) for row in rows_out)),
        "entry_bad_total": int(sum(int(row["entry_bad_count"]) for row in rows_out)),
        "contact_sheet": contact_sheet,
        "errors": errors,
        "rows": rows_out,
        "no_training": True,
        "no_forward": True,
        "visual_contract": {
            "entry_y_1": "ENTER green triangle + GOOD green circle",
            "entry_y_0": "SKIP yellow X + BAD red square",
            "riskgate": "disabled_for_base_teacher_gallery",
            "strength_strips": "visual_only_not_model_features",
        },
    }
    write_json(gallery_root / "STAS5_V5_BASE_R2_STYLE_REVIEW_GALLERY_MANIFEST_V1.json", manifest)
    _write_index(rows_out, gallery_root / "STAS5_V5_BASE_R2_STYLE_REVIEW_GALLERY_INDEX_RU.md", manifest)
    pd.DataFrame(rows_out).to_csv(
        gallery_root / "STAS5_V5_BASE_R2_STYLE_REVIEW_GALLERY_INDEX_V1.csv",
        index=False,
        encoding="utf-8-sig",
    )
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build V5 base review gallery in R2/R3/R4 visual style")
    parser.add_argument("--start-day", default="2026-01-27")
    parser.add_argument("--end-day", default="2026-02-27")
    parser.add_argument("--gallery-root", default="")
    args = parser.parse_args(argv)
    gallery_root = Path(args.gallery_root) if args.gallery_root else DEFAULT_GALLERY_ROOT
    if not gallery_root.is_absolute():
        gallery_root = PROJECT_ROOT / gallery_root
    result = build_base_review_gallery(
        start_day=args.start_day,
        end_day=args.end_day,
        gallery_root=gallery_root,
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
