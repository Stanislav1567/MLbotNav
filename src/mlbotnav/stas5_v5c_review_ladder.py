from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import PROJECT_ROOT, compact_day, ensure_parent, rel, utc_now, write_json
from mlbotnav.stas5_v5_forward_visual_review import (
    DECISION_COLUMN,
    SCORE_COLUMN,
    _build_strength_strip_rows,
    _find_context_ohlcv_path,
    _find_predictions_path,
    render_forward_day_overview,
)
from mlbotnav.visual_entry_low_anchor_suggester import _load_ohlcv, _source_csv


STATUS_DRAFT = "V5C_REVIEW_LADDER_DRAFT_NO_TRAINING"
STATUS_APPROVED = "V5C_REVIEW_LADDER_APPROVED_READY_FOR_DAY_LADDER"
SYMBOL = "SOLUSDT"
TIMEFRAME = "1m"
V5C_ROOT = PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5c"
FORWARD_RUNS_DIR = V5C_ROOT / "forward" / "runs"
LATEST_FORWARD_POINTER = V5C_ROOT / "forward" / "STAS5_V5C_LATEST_TWO_BLOCK_FORWARD_RUN.json"

ENTRY_GOOD_WORDS = (
    "хорош",
    "супер",
    "норм",
    "проходит",
    "пройдет",
    "заходит",
    "зайти",
)
ENTRY_WANT_WORDS = (
    "хочу",
    "хотел",
    "вход",
)
ENTRY_BAD_WORDS = (
    "плохо",
    "плохой",
    "плохая",
    "говно",
    "не вход",
    "неинтерес",
)
RISK_BAD_WORDS = (
    "плохо",
    "плохой",
    "плохая",
    "опас",
    "дамп",
    "слив",
    "нож",
    "шорт",
    "ликвид",
    "пролив",
    "скат",
    "падает",
)

MARKER_ALIASES = {
    "green_triangle": ("треуголь", "стрелк", "зелен"),
    "yellow_diamond": ("ромб", "diamond"),
    "yellow_x": ("крест", "икс", " x", "skip"),
}
DECISION_MARKER = {
    "ENTER": "green_triangle",
    "WATCH": "yellow_diamond",
    "SKIP": "yellow_x",
}


@dataclass(frozen=True)
class ReviewItem:
    candidate_id: str
    marker_user: str
    entry_review_label: str
    entry_y_action: str
    risk_review_label: str
    risk_user_hint: str
    user_text_raw: str


def normalize_candidate_id(value: str) -> str:
    text = str(value or "").strip().upper()
    text = text.replace("ЛА", "LA")
    if text.startswith("LA"):
        digits = re.sub(r"\D+", "", text[2:])
    else:
        digits = re.sub(r"\D+", "", text)
    if not digits:
        raise ValueError(f"candidate id is empty: {value!r}")
    return f"LA{int(digits):03d}"


def _split_review_text(text: str) -> list[str]:
    prepared = str(text or "").replace("\r", "\n")
    prepared = re.sub(r"\b(?:и|and)\s+(?=(?:LA|ЛА)?\d)", "; ", prepared, flags=re.IGNORECASE)
    prepared = re.sub(r"[,，]\s*(?=(?:LA|ЛА)?\d)", "; ", prepared, flags=re.IGNORECASE)
    parts = [part.strip(" \t\n\r,.;") for part in re.split(r"[;\n]+", prepared) if part.strip(" \t\n\r,.;")]
    return parts


def _extract_candidate_ids(segment: str) -> list[str]:
    ids: list[str] = []
    for match in re.finditer(r"(?<![A-Za-zА-Яа-я])(?:LA|ЛА)?\s*\d+(?:[\.-]\d+)?(?![A-Za-zА-Яа-я])", segment, flags=re.IGNORECASE):
        normalized = normalize_candidate_id(match.group(0))
        if normalized not in ids:
            ids.append(normalized)
    return ids


def _contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(needle in lowered for needle in needles)


def _infer_marker_user(segment: str) -> str:
    lowered = f" {segment.lower()} "
    if "ромб" in lowered or "diamond" in lowered:
        return "yellow_diamond"
    if "крест" in lowered or " икс" in lowered or " x" in lowered:
        return "yellow_x"
    if "треуголь" in lowered or "стрелк" in lowered or "зелен" in lowered:
        return "green_triangle"
    return ""


def _risk_hint(segment: str) -> str:
    lowered = segment.lower()
    hints = []
    mapping = [
        ("дамп", "dump"),
        ("слив", "dump"),
        ("нож", "falling_knife"),
        ("шорт", "short_pressure"),
        ("ликвид", "liquidation"),
        ("пролив", "liquidation"),
        ("скат", "short_continuation"),
        ("падает", "active_dump"),
    ]
    for needle, hint in mapping:
        if needle in lowered and hint not in hints:
            hints.append(hint)
    return "|".join(hints)


def _classify_segment(segment: str) -> tuple[str, str, str]:
    lowered = segment.lower()
    has_risk = "риск" in lowered or "risk" in lowered
    has_good = _contains_any(lowered, ENTRY_GOOD_WORDS) or _contains_any(lowered, ENTRY_WANT_WORDS)
    has_bad = _contains_any(lowered, ENTRY_BAD_WORDS)
    has_risk_bad = _contains_any(lowered, RISK_BAD_WORDS)

    entry_review_label = ""
    entry_y_action = ""
    risk_review_label = ""

    if has_risk:
        if has_risk_bad:
            risk_review_label = "RISK_BAD"
        elif has_good:
            raise ValueError(
                f"Unsupported phrase with 'risk good': {segment!r}. "
                "Use plain 'LAxxx хорошо' for a good rebound/entry; use only 'риск плохо' for RiskGate blocks."
            )

    if has_risk:
        if has_good:
            marker = _infer_marker_user(segment)
            entry_review_label = "GOOD_MISSED" if marker == "yellow_x" or "хотел" in lowered or "хочу" in lowered else "GOOD"
            entry_y_action = "promote_to_good"
    else:
        if has_bad and not has_good:
            entry_review_label = "BAD"
            entry_y_action = "keep_bad"
        elif has_good:
            marker = _infer_marker_user(segment)
            entry_review_label = "GOOD_MISSED" if marker == "yellow_x" or "хотел" in lowered or "хочу" in lowered else "GOOD"
            entry_y_action = "promote_to_good"

    if not entry_review_label and not risk_review_label:
        raise ValueError(f"Could not classify review phrase: {segment!r}")

    return entry_review_label, entry_y_action, risk_review_label


def parse_review_text(text: str) -> list[ReviewItem]:
    items: list[ReviewItem] = []
    seen: dict[tuple[str, str], int] = {}
    for segment in _split_review_text(text):
        ids = _extract_candidate_ids(segment)
        if not ids:
            if "день закрыт" in segment.lower():
                continue
            raise ValueError(f"Review phrase has no LA id: {segment!r}")
        entry_review_label, entry_y_action, risk_review_label = _classify_segment(segment)
        marker_user = _infer_marker_user(segment)
        hint = _risk_hint(segment)
        for candidate_id in ids:
            if entry_review_label:
                key = (candidate_id, "entry")
                if key in seen:
                    raise ValueError(f"Duplicate ENTRY label for {candidate_id}: {segment!r}")
                seen[key] = 1
            if risk_review_label:
                key = (candidate_id, "risk")
                if key in seen:
                    raise ValueError(f"Duplicate RiskGate label for {candidate_id}: {segment!r}")
                seen[key] = 1
            items.append(
                ReviewItem(
                    candidate_id=candidate_id,
                    marker_user=marker_user,
                    entry_review_label=entry_review_label,
                    entry_y_action=entry_y_action,
                    risk_review_label=risk_review_label,
                    risk_user_hint=hint,
                    user_text_raw=segment,
                )
            )
    return items


def _resolve_forward_run_dir(forward_run_id: str = "", forward_run_dir: str = "") -> Path:
    if forward_run_dir:
        path = Path(forward_run_dir)
        return path if path.is_absolute() else (PROJECT_ROOT / path)
    if forward_run_id:
        return FORWARD_RUNS_DIR / forward_run_id
    if LATEST_FORWARD_POINTER.exists():
        payload = json.loads(LATEST_FORWARD_POINTER.read_text(encoding="utf-8-sig"))
        return PROJECT_ROOT / str(payload["run_dir"])
    raise FileNotFoundError("ForwardRunId or ForwardRunDir is required; latest V5C forward pointer not found")


def _visual_entries_path(forward_run_dir: Path, day: str) -> Path | None:
    compact = compact_day(day)
    path = forward_run_dir / "visual_review" / compact / f"STAS5_V5_FORWARD_VISUAL_REVIEW_ENTRIES_{compact}.csv"
    return path if path.exists() else None


def _visual_all_entries_png_path(forward_run_dir: Path, day: str) -> Path | None:
    compact = compact_day(day)
    day_dir = forward_run_dir / "visual_review" / compact
    preferred = day_dir / f"STAS5_V5_FORWARD_VISUAL_REVIEW_{compact}_ENTER_ARROWS.png"
    if preferred.exists():
        return preferred
    candidates = sorted(day_dir.glob(f"STAS5_V5_FORWARD_VISUAL_REVIEW_{compact}*.png"), key=lambda item: item.stat().st_mtime)
    return candidates[-1] if candidates else None


def _load_source_rows(forward_run_dir: Path, day: str) -> tuple[pd.DataFrame, Path]:
    visual_path = _visual_entries_path(forward_run_dir, day)
    if visual_path:
        return pd.read_csv(visual_path, encoding="utf-8-sig"), visual_path
    predictions_path = _find_predictions_path(forward_run_dir)
    predictions = pd.read_csv(predictions_path, encoding="utf-8-sig")
    return predictions[predictions["day"].astype(str).eq(day)].copy(), predictions_path


def _latest_riskgate_path(forward_run_dir: Path, day: str) -> Path | None:
    compact = compact_day(day)
    day_dir = forward_run_dir / "riskgate_audit" / compact
    if not day_dir.exists():
        return None
    candidates = sorted(day_dir.glob(f"STAS5_V5C_RISKGATE_AUDIT_{compact}_V*.csv"), key=lambda item: item.stat().st_mtime)
    return candidates[-1] if candidates else None


def _load_riskgate_rows(forward_run_dir: Path, day: str) -> pd.DataFrame:
    path = _latest_riskgate_path(forward_run_dir, day)
    if not path:
        return pd.DataFrame()
    return pd.read_csv(path, encoding="utf-8-sig")


def _source_index(source: pd.DataFrame) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in source.to_dict("records"):
        cid = normalize_candidate_id(str(row.get("candidate_id", "")))
        index[cid] = row
    return index


def _row_decision(row: dict[str, Any]) -> str:
    return str(row.get("ENTRY_ML_LIVE_DECISION") or row.get("model_decision") or "").upper()


def _row_score(row: dict[str, Any]) -> Any:
    return row.get("ENTRY_ML_LIVE_SCORE", row.get("entry_ml_live_score", ""))


def _row_marker(row: dict[str, Any]) -> str:
    return DECISION_MARKER.get(_row_decision(row), "")


def _riskgate_index(riskgate: pd.DataFrame) -> dict[str, dict[str, Any]]:
    if riskgate.empty or "candidate_id" not in riskgate.columns:
        return {}
    return {normalize_candidate_id(str(row.get("candidate_id", ""))): row for row in riskgate.to_dict("records")}


def _make_output_paths(round_id: str, day: str, approved: bool) -> dict[str, Path]:
    compact = compact_day(day)
    round_upper = round_id.upper()
    round_lower = round_id.lower()
    status = "APPROVED" if approved else "DRAFT"
    base = V5C_ROOT / "review" / f"{round_lower}_user_review" / compact
    archive = base / "_visual_archive"
    prefix = f"STAS5_V5C_{round_upper}_USER_REVIEW_{compact}_{status}"
    risk_prefix = f"STAS5_V5C_{round_upper}_USER_RISKGATE_REVIEW_{compact}_{status}"
    return {
        "base": base,
        "visual_archive": archive,
        "entry_csv": base / f"{prefix}.csv",
        "entry_json": base / f"{prefix}.json",
        "entry_report": base / f"{prefix}_RU.md",
        "all_entries_png": archive / f"{prefix}_ALL_ENTRIES.png",
        "annotated_png": archive / f"{prefix}_ANNOTATED.png",
        "current_review_png": base / f"STAS5_V5C_{round_upper}_USER_REVIEW_{compact}_CURRENT_REVIEW.png",
        "visual_manifest_json": base / f"STAS5_V5C_{round_upper}_USER_REVIEW_{compact}_CURRENT_VISUAL_MANIFEST_V1.json",
        "risk_csv": base / f"{risk_prefix}.csv",
        "risk_json": base / f"{risk_prefix}.json",
        "risk_report": base / f"{risk_prefix}_RU.md",
        "result_json": base / f"STAS5_V5C_{round_upper}_REVIEW_LADDER_{compact}_{status}_RESULT.json",
    }


def build_review_ladder(
    *,
    day: str,
    round_id: str,
    review_text: str,
    forward_run_id: str = "",
    forward_run_dir: str = "",
    approved: bool = False,
    dry_run: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    day = pd.Timestamp(day).strftime("%Y-%m-%d")
    round_id = str(round_id or "R4").upper()
    items = parse_review_text(review_text)
    run_dir = _resolve_forward_run_dir(forward_run_id=forward_run_id, forward_run_dir=forward_run_dir)
    if not run_dir.exists():
        raise FileNotFoundError(f"forward run dir not found: {run_dir}")
    source, source_path = _load_source_rows(run_dir, day)
    if source.empty:
        raise ValueError(f"no source candidates for {day} in {source_path}")
    source_by_id = _source_index(source)
    missing_ids = sorted({item.candidate_id for item in items if item.candidate_id not in source_by_id})
    if missing_ids:
        raise ValueError(f"review ids not found in source day {day}: {', '.join(missing_ids)}")

    riskgate = _load_riskgate_rows(run_dir, day)
    riskgate_by_id = _riskgate_index(riskgate)
    all_entries_png = _visual_all_entries_png_path(run_dir, day)
    approved_utc = utc_now() if approved else ""
    review_status = f"USER_APPROVED_{round_id}_REVIEW_DAY_CLOSED" if approved else f"{round_id}_REVIEW_DRAFT"
    source_run_id = forward_run_id or run_dir.name

    entry_rows: list[dict[str, Any]] = []
    risk_rows: list[dict[str, Any]] = []
    entry_good_ids: list[str] = []
    entry_bad_ids: list[str] = []
    risk_bad_ids: list[str] = []
    risk_exception_good_ids: list[str] = []
    entry_label_by_id = {item.candidate_id: item.entry_review_label for item in items if item.entry_review_label}
    for item in items:
        if item.risk_review_label and entry_label_by_id.get(item.candidate_id) in {"GOOD", "GOOD_MISSED"}:
            raise ValueError(
                f"Conflicting labels for {item.candidate_id}: risk bad cannot be ENTRY GOOD. "
                "Use either plain 'LAxxx хорошо' or 'LAxxx риск плохо'."
            )

    for item in items:
        source_row = source_by_id[item.candidate_id]
        risk_row = riskgate_by_id.get(item.candidate_id, {})
        marker_model = _row_marker(source_row)
        marker_user = item.marker_user or marker_model
        entry_review_label = item.entry_review_label
        entry_y_action = item.entry_y_action
        entry_from_risk_bad = False
        if item.risk_review_label and not entry_review_label and item.candidate_id not in entry_label_by_id:
            entry_review_label = "BAD"
            entry_y_action = "keep_bad"
            entry_from_risk_bad = True

        if entry_review_label:
            entry_y = 1 if entry_review_label in {"GOOD", "GOOD_MISSED"} else 0
            if entry_y:
                entry_good_ids.append(item.candidate_id)
            else:
                entry_bad_ids.append(item.candidate_id)
            raw_risk_status = str(risk_row.get("RISK_GATE_RAW_STATUS") or risk_row.get("RISK_GATE_STATUS") or "")
            exception = bool(entry_y and raw_risk_status and raw_risk_status not in {"PASS_RISK", "PASS_USER_REBOUND"})
            if exception:
                risk_exception_good_ids.append(item.candidate_id)
            row = {
                "day": day,
                "candidate_id": item.candidate_id,
                "record_id": source_row.get("record_id", ""),
                "entry_time_utc": source_row.get("entry_time_utc", ""),
                "model_decision": _row_decision(source_row),
                "marker": marker_model,
                "marker_user": marker_user,
                "user_label": "GOOD" if entry_y else "BAD",
                f"{round_id.lower()}_entry_y": entry_y,
                "entry_y": entry_y,
                "entry_review_label": entry_review_label,
                "entry_y_action": entry_y_action,
                "entry_from_risk_bad": int(entry_from_risk_bad),
                "user_reason_ru": _entry_reason_ru(entry_review_label, marker_user),
                "entry_ml_live_score": _row_score(source_row),
                "source_forward_run_id": source_run_id,
                "review_status": review_status,
                "approved_utc": approved_utc,
                "user_text_raw": item.user_text_raw,
                "riskgate_raw_status_at_review": raw_risk_status,
                "riskgate_good_exception_candidate": int(exception),
            }
            entry_rows.append(row)

        if item.risk_review_label:
            risk_bad_ids.append(item.candidate_id)
            row = {
                "day": day,
                "candidate_id": item.candidate_id,
                "record_id": source_row.get("record_id", ""),
                "entry_time_utc": source_row.get("entry_time_utc", ""),
                "model_decision": _row_decision(source_row),
                "marker": marker_model,
                "marker_user": marker_user,
                "risk_review_label": item.risk_review_label,
                f"{round_id.lower()}_risk_bad_y": 1,
                "risk_bad_y": 1,
                "risk_bad_target": 1,
                "risk_user_hint": item.risk_user_hint,
                "risk_user_reason_ru": _risk_reason_ru(item.risk_user_hint),
                "entry_ml_live_score": _row_score(source_row),
                "source_forward_run_id": source_run_id,
                "review_status": review_status,
                "approved_utc": approved_utc,
                "user_text_raw": item.user_text_raw,
            }
            for key in [
                "RISK_GATE_STATUS",
                "RISK_GATE_ACTION",
                "RISK_GATE_PRIMARY_REGIME",
                "RISK_GATE_TAGS",
                "RISK_GATE_RAW_STATUS",
                "RISK_GATE_RAW_PRIMARY_REGIME",
                "RISK_NO_FUTURE_OK",
            ]:
                if key in risk_row:
                    row[key] = risk_row.get(key, "")
            risk_rows.append(row)

    paths = _make_output_paths(round_id, day, approved=approved)
    if approved and not force:
        existing = [path for key, path in paths.items() if key not in {"base", "visual_archive"} and path.exists()]
        if existing:
            raise FileExistsError(
                "approved review artifacts already exist; pass --force to overwrite: "
                + ", ".join(rel(path) for path in existing[:5])
            )
    result = {
        "status": STATUS_APPROVED if approved else STATUS_DRAFT,
        "day": day,
        "round_id": round_id,
        "forward_run_id": source_run_id,
        "forward_run_dir": rel(run_dir),
        "source_candidates_path": rel(source_path),
        "source_rows": int(len(source)),
        "parsed_items": len(items),
        "entry_review_rows": len(entry_rows),
        "risk_review_rows": len(risk_rows),
        "entry_good_ids": _unique_sorted(entry_good_ids),
        "entry_bad_ids": _unique_sorted(entry_bad_ids),
        "risk_bad_ids": _unique_sorted(risk_bad_ids),
        "risk_bad_y_count": len(_unique_sorted(risk_bad_ids)),
        "risk_bad_also_entry_bad_ids": _unique_sorted([cid for cid in risk_bad_ids if cid in entry_bad_ids]),
        "riskgate_good_exception_ids": _unique_sorted(risk_exception_good_ids),
        "riskgate_audit_source": rel(_latest_riskgate_path(run_dir, day)) if _latest_riskgate_path(run_dir, day) else "",
        "source_all_entries_png": rel(all_entries_png) if all_entries_png else "",
        "dry_run": dry_run,
        "outputs": {key: rel(path) for key, path in paths.items() if key not in {"base", "visual_archive"}},
        "rules": {
            "entry": "хорошо/вход/крестик хорошо/ромбик хорошо -> entry_y=1; плохо -> entry_y=0",
            "riskgate": "'риск плохо' -> entry_y=0 + risk_bad_y=1; 'риск хорошо' запрещен",
            "live_x_guard": "manual review/risk labels are teacher/audit only and never X439 live features",
        },
    }

    if dry_run:
        return result

    _write_outputs(
        paths,
        result,
        source_rows=source,
        forward_run_dir=run_dir,
        entry_rows=entry_rows,
        risk_rows=risk_rows,
        all_entries_png=all_entries_png,
    )
    return result


def _entry_reason_ru(label: str, marker: str) -> str:
    marker_ru = {
        "green_triangle": "зеленый треугольник",
        "yellow_diamond": "ромбик",
        "yellow_x": "крестик",
    }.get(marker, "маркер не указан")
    if label == "BAD":
        return f"{marker_ru}; плохой вход"
    if label == "GOOD_MISSED":
        return f"{marker_ru}; хороший пропущенный вход"
    return f"{marker_ru}; хороший вход"


def _risk_reason_ru(hint: str) -> str:
    if hint:
        return f"RiskGate: опасная зона, учить блокировать; hint={hint}"
    return "RiskGate: риск плохо, учить блокировать"


def _unique_sorted(values: list[str]) -> list[str]:
    return sorted(set(values), key=lambda item: int(re.sub(r"\D+", "", item)))


def _prepare_plot_rows(rows: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    out["entry_ts"] = pd.to_datetime(out["entry_time_utc"], utc=True, errors="raise", format="mixed")
    if DECISION_COLUMN not in out.columns:
        out[DECISION_COLUMN] = out.get("model_decision", "")
    out[DECISION_COLUMN] = out[DECISION_COLUMN].astype(str).str.upper()
    if SCORE_COLUMN not in out.columns:
        out[SCORE_COLUMN] = out.get("entry_ml_live_score", 0.0)
    out[SCORE_COLUMN] = pd.to_numeric(out[SCORE_COLUMN], errors="coerce").fillna(0.0)
    if "entry_price_visual" not in out.columns:
        for column in ("entry_price_5bps", "entry_open_price", "entry_price"):
            if column in out.columns:
                out["entry_price_visual"] = pd.to_numeric(out[column], errors="coerce")
                break
    out["entry_price_visual"] = pd.to_numeric(out.get("entry_price_visual", 0.0), errors="coerce")
    return out.sort_values(["entry_ts", "candidate_id"]).reset_index(drop=True)


def _load_day_ohlcv_for_plot(forward_run_dir: Path, day: str) -> pd.DataFrame | None:
    source = _source_csv(PROJECT_ROOT, day, TIMEFRAME, SYMBOL)
    if source.exists():
        return _load_ohlcv(source)
    context_path = _find_context_ohlcv_path(forward_run_dir, day)
    if context_path and context_path.exists():
        context = _load_ohlcv(context_path)
        return context[context["open_time_utc"].dt.strftime("%Y-%m-%d").eq(day)].copy().reset_index(drop=True)
    return None


def _has_next_day_context(strength_df: pd.DataFrame, day: str) -> bool:
    if strength_df.empty or "open_time_utc" not in strength_df.columns:
        return False
    next_day_start = pd.Timestamp(day, tz="UTC") + pd.Timedelta(days=1)
    return bool(strength_df["open_time_utc"].ge(next_day_start).any())


def _review_annotation_map(entry_rows: list[dict[str, Any]], risk_rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for row in entry_rows:
        cid = normalize_candidate_id(str(row["candidate_id"]))
        label = "GOOD" if int(row.get("entry_y", 0)) == 1 else "BAD"
        out.setdefault(cid, [])
        if label not in out[cid]:
            out[cid].append(label)
    for row in risk_rows:
        cid = normalize_candidate_id(str(row["candidate_id"]))
        out.setdefault(cid, [])
        if "BAD" in out[cid]:
            out[cid].remove("BAD")
        if "RISK BAD" not in out[cid]:
            out[cid].append("RISK BAD")
    return out


def _render_annotated_review_png(
    *,
    forward_run_dir: Path,
    day: str,
    source_rows: pd.DataFrame,
    entry_rows: list[dict[str, Any]],
    risk_rows: list[dict[str, Any]],
    out_path: Path,
    bollinger_preview: bool = False,
) -> bool:
    day_df = _load_day_ohlcv_for_plot(forward_run_dir, day)
    if day_df is None or day_df.empty:
        return False
    plot_rows = _prepare_plot_rows(source_rows)
    annotations = _review_annotation_map(entry_rows, risk_rows)

    strength_df = day_df
    context_path = _find_context_ohlcv_path(forward_run_dir, day)
    if context_path and context_path.exists():
        strength_df = _load_ohlcv(context_path)
    strength_rows = _build_strength_strip_rows(strength_df, day, has_next_render_day=_has_next_day_context(strength_df, day))

    render_forward_day_overview(
        day_df=day_df,
        rows=plot_rows,
        strength_hour_rows=strength_rows["hour_rows"],
        strength_macro_wave_rows=strength_rows["macro_wave_rows"],
        day=day,
        symbol=SYMBOL,
        timeframe=TIMEFRAME,
        out_path=out_path,
        review_annotations=annotations,
        bollinger_preview=bollinger_preview,
        bollinger_source_df=strength_df if bollinger_preview else None,
    )
    return True


def _archive_collision_path(path: Path) -> Path:
    if not path.exists():
        return path
    stamp = utc_now().replace(":", "").replace("-", "").replace("T", "_").replace("Z", "")
    candidate = path.with_name(f"{path.stem}_archived_{stamp}{path.suffix}")
    index = 2
    while candidate.exists():
        candidate = path.with_name(f"{path.stem}_archived_{stamp}_{index}{path.suffix}")
        index += 1
    return candidate


def _archive_extra_visual_pngs(base: Path, keep_paths: set[Path] | None = None) -> list[str]:
    keep = {path.resolve() for path in (keep_paths or set())}
    archive = base / "_visual_archive"
    moved: list[str] = []
    if not base.exists():
        return moved
    for png in sorted(base.glob("*.png")):
        if png.resolve() in keep:
            continue
        ensure_parent(archive / png.name)
        target = _archive_collision_path(archive / png.name)
        shutil.move(str(png), str(target))
        moved.append(rel(target))
    return moved


def _write_visual_manifest(
    paths: dict[str, Path],
    result: dict[str, Any],
    *,
    current_source: Path | None,
    archived_root_pngs: list[str],
) -> None:
    manifest = {
        "status": "PASS_V5C_REVIEW_CURRENT_VISUAL_READY_NO_TRAINING",
        "day": result["day"],
        "round_id": result["round_id"],
        "review_status": result["status"],
        "current_review_png": rel(paths["current_review_png"]) if paths["current_review_png"].exists() else "",
        "current_source_png": rel(current_source) if current_source else "",
        "visual_archive_dir": rel(paths["visual_archive"]),
        "archived_root_pngs": archived_root_pngs,
        "all_entries_png": rel(paths["all_entries_png"]) if paths["all_entries_png"].exists() else "",
        "annotated_png": rel(paths["annotated_png"]) if paths["annotated_png"].exists() else "",
        "entry_csv": result["outputs"].get("entry_csv", ""),
        "risk_csv": result["outputs"].get("risk_csv", ""),
        "entry_good_count": len(result["entry_good_ids"]),
        "entry_bad_count": len(result["entry_bad_ids"]),
        "risk_bad_count": len(result["risk_bad_ids"]),
        "entry_good_ids": result["entry_good_ids"],
        "entry_bad_ids": result["entry_bad_ids"],
        "risk_bad_ids": result["risk_bad_ids"],
        "no_training": True,
        "no_forward": True,
        "ml_training_source_of_truth": "APPROVED CSV/JSON ledgers, not PNG files",
    }
    write_json(paths["visual_manifest_json"], manifest)


def _write_outputs(
    paths: dict[str, Path],
    result: dict[str, Any],
    source_rows: pd.DataFrame,
    forward_run_dir: Path,
    entry_rows: list[dict[str, Any]],
    risk_rows: list[dict[str, Any]],
    *,
    all_entries_png: Path | None,
) -> None:
    ensure_parent(paths["entry_csv"])
    pd.DataFrame(entry_rows).to_csv(paths["entry_csv"], index=False, encoding="utf-8-sig")
    pd.DataFrame(risk_rows).to_csv(paths["risk_csv"], index=False, encoding="utf-8-sig")
    if all_entries_png and all_entries_png.exists():
        ensure_parent(paths["all_entries_png"])
        shutil.copy2(all_entries_png, paths["all_entries_png"])
    annotated_created = _render_annotated_review_png(
        forward_run_dir=forward_run_dir,
        day=str(result["day"]),
        source_rows=source_rows,
        entry_rows=entry_rows,
        risk_rows=risk_rows,
        out_path=paths["annotated_png"],
    )
    result["annotated_png_created"] = bool(annotated_created)
    current_source = paths["annotated_png"] if annotated_created and paths["annotated_png"].exists() else None
    if current_source is None and paths["all_entries_png"].exists():
        current_source = paths["all_entries_png"]
    if current_source:
        ensure_parent(paths["current_review_png"])
        shutil.copy2(current_source, paths["current_review_png"])
    archived_root_pngs = _archive_extra_visual_pngs(paths["base"], {paths["current_review_png"]})
    result["current_review_png_created"] = bool(paths["current_review_png"].exists())
    result["archived_root_pngs"] = archived_root_pngs
    write_json(paths["entry_json"], {"status": result["status"], "rows": len(entry_rows), "good_ids": result["entry_good_ids"], "bad_ids": result["entry_bad_ids"]})
    write_json(
        paths["risk_json"],
        {
            "status": result["status"],
            "rows": len(risk_rows),
            "risk_bad_ids": result["risk_bad_ids"],
            "risk_bad_y_count": result["risk_bad_y_count"],
            "risk_bad_also_entry_bad_ids": result["risk_bad_also_entry_bad_ids"],
        },
    )
    result["outputs"]["current_review_png"] = rel(paths["current_review_png"]) if paths["current_review_png"].exists() else ""
    result["outputs"]["visual_archive"] = rel(paths["visual_archive"])
    result["outputs"]["visual_manifest_json"] = rel(paths["visual_manifest_json"])
    _write_visual_manifest(paths, result, current_source=current_source, archived_root_pngs=archived_root_pngs)
    write_json(paths["result_json"], result)
    paths["entry_report"].write_text(_entry_report(result), encoding="utf-8")
    paths["risk_report"].write_text(_risk_report(result), encoding="utf-8")


def _entry_report(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# STAS5 V5C {result['round_id']} user review {result['day']}",
            "",
            f"Статус: `{result['status']}`.",
            "",
            f"Источник forward: `{result['forward_run_id']}`.",
            f"ENTRY rows: `{result['entry_review_rows']}`.",
            f"GOOD ids: `{','.join(result['entry_good_ids'])}`.",
            f"BAD ids: `{','.join(result['entry_bad_ids'])}`.",
            f"Текущий график для открытия: `{result['outputs'].get('current_review_png', '')}`.",
            f"Архив чистого/annotated PNG: `{result['outputs'].get('visual_archive', '')}`.",
            f"Visual manifest: `{result['outputs'].get('visual_manifest_json', '')}`.",
            "",
            "Правило: обычные `хорошо/плохо` идут только в ENTRY teacher layer. Эти поля не являются live X.",
            "",
        ]
    )


def _risk_report(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# STAS5 V5C {result['round_id']} RiskGate review {result['day']}",
            "",
            f"Статус: `{result['status']}`.",
            "",
            f"Risk BAD ids: `{','.join(result['risk_bad_ids'])}`.",
            f"risk_bad_y=1 rows: `{result['risk_bad_y_count']}`.",
            f"GOOD rebound/exception candidates from ENTRY+raw risk: `{','.join(result['riskgate_good_exception_ids'])}`.",
            f"Текущий график для открытия: `{result['outputs'].get('current_review_png', '')}`.",
            f"Visual manifest: `{result['outputs'].get('visual_manifest_json', '')}`.",
            "",
            "Правило: для RiskGate вручную используем только `риск плохо`. `риск хорошо` запрещен; хорошие отскоки отмечаются обычным `хорошо` в ENTRY.",
            "Risk labels остаются teacher/audit layer и не попадают в X439.",
            "",
        ]
    )


def _read_review_text(args: argparse.Namespace) -> str:
    parts: list[str] = []
    if args.review:
        parts.append(str(args.review))
    if args.review_file:
        path = Path(args.review_file)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        parts.append(path.read_text(encoding="utf-8-sig"))
    text = "\n".join(parts).strip()
    if not text:
        raise ValueError("--review or --review-file is required")
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="STAS5 V5C fast user review ladder parser")
    parser.add_argument("--day", required=True)
    parser.add_argument("--round-id", default="R4")
    parser.add_argument("--forward-run-id", default="")
    parser.add_argument("--forward-run-dir", default="")
    parser.add_argument("--review", default="")
    parser.add_argument("--review-file", default="")
    parser.add_argument("--approve", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    result = build_review_ladder(
        day=args.day,
        round_id=args.round_id,
        review_text=_read_review_text(args),
        forward_run_id=args.forward_run_id,
        forward_run_dir=args.forward_run_dir,
        approved=bool(args.approve),
        dry_run=bool(args.dry_run),
        force=bool(args.force),
    )
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
