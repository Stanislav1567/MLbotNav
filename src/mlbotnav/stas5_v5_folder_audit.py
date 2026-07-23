from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import PROJECT_ROOT, compact_day, ensure_parent, rel, utc_now, write_json


STATUS_PASS = "PASS_V5_FOLDER_AUDIT_NO_TRAINING"
STATUS_WARN = "WARN_V5_FOLDER_AUDIT_PARTIAL"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"_read_error": str(exc)}


def _read_csv_shape(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
        out: dict[str, Any] = {"exists": True, "rows": int(len(df)), "columns": int(len(df.columns))}
        if "entry_y" in df.columns:
            out["entry_y_counts"] = {
                str(k): int(v) for k, v in df["entry_y"].value_counts(dropna=False).sort_index().items()
            }
        if "entry_label" in df.columns:
            out["entry_label_counts"] = {str(k): int(v) for k, v in df["entry_label"].value_counts().items()}
        if "rank_label" in df.columns:
            out["rank_label_counts"] = {str(k): int(v) for k, v in df["rank_label"].value_counts().items()}
        return out
    except Exception as exc:
        return {"exists": True, "read_error": str(exc)}


def _guard_status(path: Path) -> dict[str, Any]:
    data = _read_json(path)
    if not data:
        return {"exists": False}
    checks = data.get("checks", [])
    check_map = {}
    if isinstance(checks, list):
        for item in checks:
            if isinstance(item, dict) and "check" in item:
                check_map[str(item["check"])] = str(item.get("status", ""))
    return {
        "exists": True,
        "status": data.get("status", ""),
        "rows": data.get("rows"),
        "feature_count": data.get("feature_count"),
        "base_feature_count": data.get("base_feature_count"),
        "full_causal_feature_count": data.get("full_causal_feature_count"),
        "artifact_counts": data.get("artifact_counts", {}),
        "checks": check_map,
        "read_error": data.get("_read_error", ""),
    }


def _full274_runs(root: Path) -> list[dict[str, Any]]:
    runs_dir = root / "STAS5_ML_CORE" / "runs"
    rows: list[dict[str, Any]] = []
    if not runs_dir.exists():
        return rows
    pattern = re.compile(r"^full274_feature_collect_(\d{8})_(\d{8}_\d{6})$")
    for item in sorted(runs_dir.iterdir()):
        if not item.is_dir():
            continue
        match = pattern.match(item.name)
        if not match:
            continue
        day_compact = match.group(1)
        day = f"{day_compact[:4]}-{day_compact[4:6]}-{day_compact[6:8]}"
        summary = _read_json(item / "STAS5_FULL274_FEATURE_COLLECT_SUMMARY.json")
        rows.append(
            {
                "day": day,
                "run_id": item.name,
                "path": rel(item, root),
                "status": summary.get("status", "UNKNOWN" if summary else "NO_SUMMARY"),
                "rows": summary.get("rows"),
                "feature_count": summary.get("feature_count"),
                "graph_png": summary.get("graph_png", ""),
                "training_started": bool(summary.get("training_started", False)),
            }
        )
    return rows


def _day_paths(v5_root: Path, day_compact: str) -> dict[str, Path]:
    base = v5_root / "market_passports" / day_compact
    prefix = f"STAS5_V5_MARKET_PASSPORT_{day_compact}"
    return {
        "base": base,
        "open_first": base / "00_OPEN_FIRST_RU.md",
        "readme": base / "README_RU.md",
        "approved_ledger": base / f"{prefix}_ENTRY_PHASE_STATE_REASON_LEDGER_USER_APPROVED_V2.csv",
        "phase_segments": base / f"{prefix}_PHASE_SEGMENTS_USER_APPROVED_V1.csv",
        "market_structure_numeric": base / f"{prefix}_MARKET_STRUCTURE_NUMERIC_V1.csv",
        "baseline_ml_ready": base / f"{prefix}_ML_READY_274F_ENTRY_PHASE_STATE_REASON_TARGETS_V2.csv",
        "baseline_allowlist": base / f"{prefix}_FEATURE_ALLOWLIST_274_ENTRY_PHASE_STATE_REASON_V2.json",
        "baseline_guard": base / f"{prefix}_PHASE_STATE_REASON_GUARD_V2.json",
        "cs_features": base / f"{prefix}_CAUSAL_STRUCTURE_FEATURES_V1.csv",
        "cs_ml_ready": base / f"{prefix}_ML_READY_274F_PLUS_CAUSAL_STRUCTURE_TARGETS_V1.csv",
        "cs_allowlist": base / f"{prefix}_FEATURE_ALLOWLIST_274_PLUS_CAUSAL_STRUCTURE_V1.json",
        "cs_guard": base / f"{prefix}_CAUSAL_STRUCTURE_GUARD_V1.json",
        "fcs_features": base / f"{prefix}_FULL_STRUCTURE_CANDIDATE_FEATURES_CAUSAL_V1.csv",
        "fcs_ml_ready": base / f"{prefix}_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv",
        "fcs_allowlist": base / f"{prefix}_FEATURE_ALLOWLIST_274_PLUS_FULL_CAUSAL_STRUCTURE_V1.json",
        "fcs_guard": base / f"{prefix}_FULL_CAUSAL_STRUCTURE_GUARD_V1.json",
        "levels": base / f"{prefix}_LEVELS_CAUSAL_V1.csv",
        "channels": base / f"{prefix}_CHANNELS_CAUSAL_V1.csv",
        "regimes": base / f"{prefix}_REGIMES_CAUSAL_V1.csv",
        "events": base / f"{prefix}_EVENTS_CAUSAL_V1.csv",
        "full_map": base / f"DAY_MARKET_PASSPORT_{day_compact}_FULL_CAUSAL_STRUCTURE_MAP_V1.png",
    }


def _audit_day(v5_root: Path, day_compact: str, full274_by_day: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    paths = _day_paths(v5_root, day_compact)
    base = paths["base"]
    required_for_full = [
        "open_first",
        "readme",
        "approved_ledger",
        "phase_segments",
        "market_structure_numeric",
        "baseline_ml_ready",
        "baseline_allowlist",
        "baseline_guard",
        "cs_features",
        "cs_ml_ready",
        "cs_allowlist",
        "cs_guard",
        "fcs_features",
        "fcs_ml_ready",
        "fcs_allowlist",
        "fcs_guard",
        "levels",
        "channels",
        "regimes",
        "events",
        "full_map",
    ]
    missing = [name for name in required_for_full if not paths[name].exists()]
    baseline_guard = _guard_status(paths["baseline_guard"])
    cs_guard = _guard_status(paths["cs_guard"])
    fcs_guard = _guard_status(paths["fcs_guard"])
    full_ready = (
        base.exists()
        and not missing
        and str(fcs_guard.get("status", "")).startswith("PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY")
    )
    day = f"{day_compact[:4]}-{day_compact[4:6]}-{day_compact[6:8]}"
    return {
        "day": day,
        "day_compact": day_compact,
        "path": rel(base),
        "exists": base.exists(),
        "status": "FULL_READY" if full_ready else ("PARTIAL" if base.exists() else "NO_MARKET_PASSPORT"),
        "missing_required_for_full": missing,
        "full274_runs": full274_by_day.get(day, []),
        "baseline": {
            "ml_ready": _read_csv_shape(paths["baseline_ml_ready"]),
            "guard": baseline_guard,
        },
        "cs": {
            "features": _read_csv_shape(paths["cs_features"]),
            "ml_ready": _read_csv_shape(paths["cs_ml_ready"]),
            "guard": cs_guard,
        },
        "full": {
            "features": _read_csv_shape(paths["fcs_features"]),
            "ml_ready": _read_csv_shape(paths["fcs_ml_ready"]),
            "guard": fcs_guard,
            "level_rows": _read_csv_shape(paths["levels"]).get("rows"),
            "channel_rows": _read_csv_shape(paths["channels"]).get("rows"),
            "regime_rows": _read_csv_shape(paths["regimes"]).get("rows"),
            "event_rows": _read_csv_shape(paths["events"]).get("rows"),
            "map_exists": paths["full_map"].exists(),
        },
    }


def build_audit(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    v5_root = project_root / "STAS5_ML_CORE" / "artifacts" / "v5"
    passport_root = v5_root / "market_passports"
    full274 = _full274_runs(project_root)
    full274_by_day: dict[str, list[dict[str, Any]]] = {}
    for run in full274:
        full274_by_day.setdefault(str(run["day"]), []).append(run)

    day_compacts: set[str] = set()
    if passport_root.exists():
        for item in passport_root.iterdir():
            if item.is_dir() and re.fullmatch(r"\d{8}", item.name):
                day_compacts.add(item.name)
    for day in full274_by_day:
        day_compacts.add(compact_day(day))

    days = [_audit_day(v5_root, day_compact, full274_by_day) for day_compact in sorted(day_compacts)]
    full_ready_days = [day for day in days if day["status"] == "FULL_READY"]
    partial_days = [day for day in days if day["status"] != "FULL_READY"]

    model_dir = v5_root / "model"
    forward_dir = v5_root / "forward"
    payload = {
        "status": STATUS_PASS if full_ready_days else STATUS_WARN,
        "created_utc": utc_now(),
        "scope": "STAS5 V5 folder audit",
        "training_started": False,
        "forward_started": False,
        "v5_root": rel(v5_root),
        "current_contract": "manual passport y + causal/live-safe X = 274 + cs_* + fcs_*",
        "full_ready_day_count": len(full_ready_days),
        "partial_day_count": len(partial_days),
        "days": days,
        "full274_runs": full274,
        "v5_folder_presence": {
            "labels": (v5_root / "labels").exists(),
            "market_passports": passport_root.exists(),
            "features": (v5_root / "features").exists(),
            "model": model_dir.exists(),
            "forward": forward_dir.exists(),
            "guard": (v5_root / "guard").exists(),
        },
        "rails": [
            "Текущий дневной источник правды: ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv.",
            "Старый PLUS_CAUSAL_STRUCTURE_TARGETS_V1.csv является source/base для full-слоя, а не финальным файлом.",
            "FULL274 run без approved passport не является обучающим днем.",
            "entry_y/phase_y/state_y/reason_y и ручные зоны не входят в X.",
            "Обучение запускать только после batch dataset и batch guard по нескольким approved дням.",
        ],
    }
    return payload


def write_report(payload: dict[str, Any], out_md: Path, out_json: Path) -> None:
    ensure_parent(out_md)
    write_json(out_json, payload)
    lines: list[str] = [
        "# STAS5 V5 Folder Audit",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Обучение V5 не запускалось. Forward V5 не запускался.",
        "",
        "## Текущий Контракт",
        "",
        "```text",
        str(payload["current_contract"]),
        "```",
        "",
        "Главный дневной файл после утверждения дня:",
        "",
        "```text",
        "STAS5_V5_MARKET_PASSPORT_YYYYMMDD_ML_READY_274F_PLUS_FULL_CAUSAL_STRUCTURE_TARGETS_V1.csv",
        "```",
        "",
        "## Сводка",
        "",
        f"- full-ready дней: `{payload['full_ready_day_count']}`",
        f"- partial/not-ready дней: `{payload['partial_day_count']}`",
        f"- full274 runs: `{len(payload['full274_runs'])}`",
        f"- model folder exists: `{payload['v5_folder_presence']['model']}`",
        f"- forward folder exists: `{payload['v5_folder_presence']['forward']}`",
        "",
        "## Дни",
        "",
        "| day | status | full274 | rows | features | entry_y | guard | missing |",
        "|---|---|---:|---:|---:|---|---|---|",
    ]
    for day in payload["days"]:
        full = day.get("full", {})
        ml_ready = full.get("ml_ready", {})
        guard = full.get("guard", {})
        entry_y = ml_ready.get("entry_y_counts", {})
        entry_y_text = ", ".join(f"{k}:{v}" for k, v in entry_y.items()) if entry_y else ""
        missing = day.get("missing_required_for_full", [])
        lines.append(
            "| {day} | {status} | {full274} | {rows} | {features} | {entry_y} | {guard} | {missing} |".format(
                day=day["day"],
                status=day["status"],
                full274=len(day.get("full274_runs", [])),
                rows=ml_ready.get("rows", ""),
                features=guard.get("feature_count", ""),
                entry_y=entry_y_text,
                guard=guard.get("status", ""),
                missing=len(missing),
            )
        )
    lines.extend(
        [
            "",
            "## Рельсы",
            "",
        ]
    )
    for item in payload["rails"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Что Делать Дальше",
            "",
            "1. Для нового дня сначала собрать или найти `FULL274` run.",
            "2. По графику сделать ручной паспорт и approved labels.",
            "3. Когда approved files лежат в `artifacts/v5/market_passports/YYYYMMDD`, запускать `cs_*` и `fcs_*` builders.",
            "4. День считается готовым только при `FULL_CAUSAL_STRUCTURE_GUARD_V1 = PASS_NO_TRAINING_FULL_CAUSAL_STRUCTURE_READY`.",
            "5. Обучение запускать только после batch-аудита нескольких таких дней.",
            "",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit STAS5 V5 folder and market-passport rails.")
    parser.add_argument("--out-md", default="")
    parser.add_argument("--out-json", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_root = PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5"
    out_md = Path(args.out_md) if args.out_md else out_root / "STAS5_V5_FOLDER_AUDIT_20260715_RU.md"
    out_json = Path(args.out_json) if args.out_json else out_root / "STAS5_V5_FOLDER_AUDIT_20260715.json"
    payload = build_audit(PROJECT_ROOT)
    write_report(payload, out_md, out_json)
    print(
        json.dumps(
            {
                "status": payload["status"],
                "full_ready_day_count": payload["full_ready_day_count"],
                "partial_day_count": payload["partial_day_count"],
                "out_md": rel(out_md),
                "out_json": rel(out_json),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
