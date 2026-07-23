from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import PROJECT_ROOT, compact_day, ensure_parent, iter_days, rel, utc_now, write_json
from mlbotnav.stas5_v5c_review_ladder import _load_source_rows, normalize_candidate_id


STATUS_PASS = "PASS_V5C_REVIEW_PACK_GUARD_READY_NO_TRAINING"
STATUS_FAIL = "FAIL_V5C_REVIEW_PACK_GUARD"

V5C_ROOT = PROJECT_ROOT / "STAS5_ML_CORE" / "artifacts" / "v5c"
REVIEW_ROOT = V5C_ROOT / "review"
FORWARD_RUNS_DIR = V5C_ROOT / "forward" / "runs"
PACKS_ROOT = REVIEW_ROOT / "_APPROVED_REVIEW_PACKS"

PACK_ID_DEFAULT = "STAS5_V5C_REVIEW_PACK_R2_R3_R4_20260228_20260320_V1"
ENTRY_ALL_NAME = "STAS5_V5C_R2_R3_R4_ENTRY_REVIEW_APPROVED_ALL_V1.csv"
RISKGATE_ALL_NAME = "STAS5_V5C_R2_R3_R4_RISKGATE_REVIEW_APPROVED_ALL_V1.csv"
MANIFEST_NAME = "STAS5_V5C_R2_R3_R4_REVIEW_PACK_MANIFEST_V1.json"
GUARD_NAME = "STAS5_V5C_R2_R3_R4_REVIEW_PACK_GUARD_V1.json"
AUDIT_NAME = "STAS5_V5C_R2_R3_R4_REVIEW_PACK_AUDIT_RU.md"


@dataclass(frozen=True)
class RoundSpec:
    round_id: str
    start_day: str
    end_day: str
    forward_run_id: str


DEFAULT_ROUND_SPECS = (
    RoundSpec(
        round_id="R2",
        start_day="2026-02-28",
        end_day="2026-03-06",
        forward_run_id="stas5_v5c_continuous_forward_20260228_20260306_20260716_155343",
    ),
    RoundSpec(
        round_id="R3",
        start_day="2026-03-07",
        end_day="2026-03-13",
        forward_run_id="stas5_v5c_r2q_forward_20260307_20260313_wide_v2",
    ),
    RoundSpec(
        round_id="R4",
        start_day="2026-03-14",
        end_day="2026-03-20",
        forward_run_id="stas5_v5c_r3_forward_20260314_20260320_wide_v1",
    ),
)


def _round_review_dir(round_id: str) -> Path:
    return REVIEW_ROOT / f"{round_id.lower()}_user_review"


def _review_paths(round_id: str, day: str) -> dict[str, Path]:
    day_compact = compact_day(day)
    base = _round_review_dir(round_id) / day_compact
    prefix = f"STAS5_V5C_{round_id}_USER_REVIEW_{day_compact}"
    risk_prefix = f"STAS5_V5C_{round_id}_USER_RISKGATE_REVIEW_{day_compact}"
    return {
        "base": base,
        "entry_csv": base / f"{prefix}_APPROVED.csv",
        "entry_json": base / f"{prefix}_APPROVED.json",
        "entry_report": base / f"{prefix}_APPROVED_RU.md",
        "risk_csv": base / f"{risk_prefix}_APPROVED.csv",
        "risk_json": base / f"{risk_prefix}_APPROVED.json",
        "risk_report": base / f"{risk_prefix}_APPROVED_RU.md",
        "result_json": base / f"STAS5_V5C_{round_id}_REVIEW_LADDER_{day_compact}_APPROVED_RESULT.json",
        "current_review_png": base / f"STAS5_V5C_{round_id}_USER_REVIEW_{day_compact}_CURRENT_REVIEW.png",
        "current_visual_manifest": base / f"STAS5_V5C_{round_id}_USER_REVIEW_{day_compact}_CURRENT_VISUAL_MANIFEST_V1.json",
    }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")


def _normalize_entry_df(df: pd.DataFrame, round_id: str, day: str) -> pd.DataFrame:
    out = df.copy()
    round_target = f"{round_id.lower()}_entry_y"
    if "entry_y" not in out.columns and round_target in out.columns:
        out["entry_y"] = out[round_target]
    if "entry_y" not in out.columns:
        raise ValueError(f"entry_y not found in {round_id} {day} ENTRY review")
    out["day"] = day
    out["candidate_id"] = out["candidate_id"].map(lambda value: normalize_candidate_id(str(value)))
    out["entry_y"] = pd.to_numeric(out["entry_y"], errors="coerce").fillna(-1).astype(int)
    if round_target not in out.columns:
        out[round_target] = out["entry_y"]
    return out


def _normalize_risk_df(df: pd.DataFrame, round_id: str, day: str) -> pd.DataFrame:
    out = df.copy()
    round_target = f"{round_id.lower()}_risk_bad_y"
    if "risk_bad_y" not in out.columns and round_target in out.columns:
        out["risk_bad_y"] = out[round_target]
    if "risk_bad_y" not in out.columns and "risk_bad_target" in out.columns:
        out["risk_bad_y"] = out["risk_bad_target"]
    if "risk_bad_y" not in out.columns:
        raise ValueError(f"risk_bad_y not found in {round_id} {day} RiskGate review")
    out["day"] = day
    out["candidate_id"] = out["candidate_id"].map(lambda value: normalize_candidate_id(str(value)))
    out["risk_bad_y"] = pd.to_numeric(out["risk_bad_y"], errors="coerce").fillna(-1).astype(int)
    if round_target not in out.columns:
        out[round_target] = out["risk_bad_y"]
    return out


def _ordered_columns(rows: list[dict[str, Any]], preferred: list[str]) -> list[str]:
    columns = list(preferred)
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)
    return columns


def _write_csv(path: Path, rows: list[dict[str, Any]], preferred: list[str]) -> None:
    ensure_parent(path)
    columns = _ordered_columns(rows, preferred)
    pd.DataFrame(rows, columns=columns).to_csv(path, index=False, encoding="utf-8-sig")


def _copy_visual(src: Path, dst: Path) -> str:
    ensure_parent(dst)
    shutil.copy2(src, dst)
    return rel(dst)


def _check(name: str, passed: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"check": name, "status": "PASS" if passed else "FAIL", "details": details or {}}


def _duplicate_keys(df: pd.DataFrame, columns: list[str]) -> list[str]:
    if df.empty or any(column not in df.columns for column in columns):
        return []
    dup = df[df.duplicated(columns, keep=False)]
    return sorted({"|".join(str(row[column]) for column in columns) for row in dup.to_dict("records")})


def _ids(df: pd.DataFrame) -> set[tuple[str, str]]:
    if df.empty:
        return set()
    return {(str(row["day"]), str(row["candidate_id"])) for row in df.to_dict("records")}


def _build_guard(
    *,
    manifest: dict[str, Any],
    entry_df: pd.DataFrame,
    risk_df: pd.DataFrame,
    expected_days: int,
    expected_rounds: list[str],
    expected_day_keys: set[tuple[str, str]],
    source_missing_ids: dict[str, list[str]],
    missing_files: list[str],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    checks.append(_check("expected_rounds_present", sorted(manifest["rounds"].keys()) == sorted(expected_rounds), {"expected": expected_rounds, "actual": sorted(manifest["rounds"].keys())}))
    checks.append(_check("expected_21_days_present", int(manifest["days"]) == expected_days, {"expected": expected_days, "actual": manifest["days"]}))
    checks.append(_check("no_required_files_missing", not missing_files, {"missing_files": missing_files}))
    forward_run_ids = {round_id: str(row.get("forward_run_id", "")).strip() for round_id, row in manifest["rounds"].items()}
    checks.append(_check("source_forward_run_ids_present", all(forward_run_ids.values()), {"forward_run_ids": forward_run_ids}))
    checks.append(_check("entry_review_has_rows", int(manifest["entry_rows"]) > 0, {"entry_rows": manifest["entry_rows"]}))
    checks.append(_check("riskgate_review_has_rows", int(manifest["risk_rows"]) > 0, {"risk_rows": manifest["risk_rows"]}))

    entry_bad = set(zip(entry_df.loc[entry_df["entry_y"].eq(0), "day"], entry_df.loc[entry_df["entry_y"].eq(0), "candidate_id"]))
    entry_good = set(zip(entry_df.loc[entry_df["entry_y"].eq(1), "day"], entry_df.loc[entry_df["entry_y"].eq(1), "candidate_id"]))
    risk_bad = _ids(risk_df.loc[risk_df["risk_bad_y"].eq(1)].copy()) if not risk_df.empty else set()
    conflict_good_risk = sorted(f"{day}:{cid}" for day, cid in (entry_good & risk_bad))
    risk_not_entry_bad = sorted(f"{day}:{cid}" for day, cid in (risk_bad - entry_bad))

    checks.append(_check("entry_y_values_are_0_1", set(entry_df["entry_y"].astype(int).unique()).issubset({0, 1}), {"values": sorted(set(entry_df["entry_y"].astype(int).unique()))}))
    checks.append(_check("risk_bad_y_values_are_1", set(risk_df["risk_bad_y"].astype(int).unique()).issubset({1}), {"values": sorted(set(risk_df["risk_bad_y"].astype(int).unique())) if not risk_df.empty else []}))
    checks.append(_check("risk_bad_also_entry_bad", not risk_not_entry_bad, {"risk_not_entry_bad": risk_not_entry_bad}))
    checks.append(_check("no_good_vs_risk_conflicts", not conflict_good_risk, {"conflicts": conflict_good_risk}))

    duplicate_details = {
        "entry_day_candidate": _duplicate_keys(entry_df, ["day", "candidate_id"]),
        "entry_day_record": _duplicate_keys(entry_df, ["day", "record_id"]),
        "risk_day_candidate": _duplicate_keys(risk_df, ["day", "candidate_id"]),
        "risk_day_record": _duplicate_keys(risk_df, ["day", "record_id"]),
    }
    checks.append(_check("no_duplicate_day_candidate_or_record", not any(duplicate_details.values()), duplicate_details))

    actual_day_keys = set(zip(entry_df["round_id"].astype(str), entry_df["day"].astype(str)))
    missing_day_keys = sorted(f"{round_id}:{day}" for round_id, day in expected_day_keys - actual_day_keys)
    checks.append(_check("entry_rows_cover_expected_day_keys", not missing_day_keys, {"missing_day_keys": missing_day_keys}))
    checks.append(_check("review_ids_exist_in_source_forward_entries", not any(source_missing_ids.values()), {"missing_source_ids": source_missing_ids}))
    checks.append(_check("png_is_visual_only_not_training_source", bool(manifest["rules"]["png_is_visual_only"]), {"visual_files": manifest["visual_files"]}))
    checks.append(_check("manual_targets_not_live_x439", bool(manifest["rules"]["manual_targets_not_live_x439"]), {"target_columns": manifest["rules"]["teacher_target_columns"]}))
    checks.append(_check("no_training_or_forward_was_run", bool(manifest["no_training"]) and bool(manifest["no_forward"]), {"no_training": manifest["no_training"], "no_forward": manifest["no_forward"]}))

    failed = [check for check in checks if check["status"] != "PASS"]
    return {
        "status": STATUS_PASS if not failed else STATUS_FAIL,
        "created_utc": utc_now(),
        "pack_id": manifest["pack_id"],
        "pack_dir": manifest["pack_dir"],
        "checks": checks,
        "failed_checks": failed,
        "summary": {
            "days": manifest["days"],
            "entry_rows": manifest["entry_rows"],
            "entry_good": manifest["entry_good"],
            "entry_bad": manifest["entry_bad"],
            "risk_bad": manifest["risk_bad"],
        },
    }


def _write_audit(path: Path, manifest: dict[str, Any], guard: dict[str, Any]) -> None:
    lines = [
        "# STAS5 V5C Review Pack R2/R3/R4",
        "",
        f"Статус guard: `{guard['status']}`.",
        "",
        "Этот пакет только собирает утвержденную ручную разметку. Обучение, forward и пересборка дневных паспортов этим шагом не запускались.",
        "",
        "## Контракт",
        "",
        "```text",
        "ENTRY: хорошо/вход -> entry_y=1; плохо -> entry_y=0",
        "RiskGate: риск плохо -> entry_y=0 + risk_bad_y=1",
        "PNG: только визуальная проверка, не источник обучения",
        "Live X: только causal X439; manual/target/review поля запрещены как features",
        "```",
        "",
        "## Итог",
        "",
        f"- Дней: `{manifest['days']}`.",
        f"- ENTRY rows: `{manifest['entry_rows']}`.",
        f"- ENTRY GOOD: `{manifest['entry_good']}`.",
        f"- ENTRY BAD: `{manifest['entry_bad']}`.",
        f"- RISK BAD: `{manifest['risk_bad']}`.",
        "",
        "## Выходы",
        "",
        f"- ENTRY CSV: `{manifest['outputs']['entry_csv']}`.",
        f"- RiskGate CSV: `{manifest['outputs']['riskgate_csv']}`.",
        f"- Manifest: `{manifest['outputs']['manifest_json']}`.",
        f"- Guard: `{manifest['outputs']['guard_json']}`.",
        "",
        "## По дням",
        "",
        "| round | day | ENTRY rows | GOOD | BAD | RISK BAD | current PNG |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in manifest["day_rows"]:
        lines.append(
            f"| {row['round_id']} | {row['day']} | {row['entry_rows']} | {row['entry_good']} | {row['entry_bad']} | {row['risk_bad']} | `{row['pack_current_review_png']}` |"
        )
    lines.extend(
        [
            "",
            "## Guard Checks",
            "",
            "| check | status |",
            "|---|---|",
        ]
    )
    for check in guard["checks"]:
        lines.append(f"| `{check['check']}` | `{check['status']}` |")
    ensure_parent(path)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_review_pack(
    *,
    pack_id: str = PACK_ID_DEFAULT,
    round_specs: tuple[RoundSpec, ...] = DEFAULT_ROUND_SPECS,
    output_root: Path | None = None,
    force: bool = False,
    strict: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any], dict[str, Any]]:
    created_utc = utc_now()
    output_root = output_root or PACKS_ROOT
    pack_dir = output_root / pack_id
    if pack_dir.exists() and not force:
        raise FileExistsError(f"review pack already exists; pass --force to overwrite: {pack_dir}")

    entry_rows: list[dict[str, Any]] = []
    risk_rows: list[dict[str, Any]] = []
    day_rows: list[dict[str, Any]] = []
    visual_files: list[str] = []
    manifest_files: list[str] = []
    missing_files: list[str] = []
    source_missing_ids: dict[str, list[str]] = {}
    expected_day_keys: set[tuple[str, str]] = set()

    for spec in round_specs:
        round_id = spec.round_id.upper()
        forward_run_dir = FORWARD_RUNS_DIR / spec.forward_run_id
        for day in iter_days(spec.start_day, spec.end_day):
            expected_day_keys.add((round_id, day))
            day_compact = compact_day(day)
            paths = _review_paths(round_id, day)
            required_paths = [paths[key] for key in ["entry_csv", "entry_json", "risk_csv", "risk_json", "result_json", "current_review_png", "current_visual_manifest"]]
            day_missing = [rel(path) for path in required_paths if not path.exists()]
            missing_files.extend(day_missing)
            if day_missing:
                day_rows.append(
                    {
                        "round_id": round_id,
                        "day": day,
                        "compact_day": day_compact,
                        "forward_run_id": spec.forward_run_id,
                        "entry_rows": 0,
                        "entry_good": 0,
                        "entry_bad": 0,
                        "risk_bad": 0,
                        "missing_files": day_missing,
                        "pack_current_review_png": "",
                    }
                )
                continue

            entry_df_day = _normalize_entry_df(_read_csv(paths["entry_csv"]), round_id, day)
            risk_df_day = _normalize_risk_df(_read_csv(paths["risk_csv"]), round_id, day)
            source_df, source_path = _load_source_rows(forward_run_dir, day)
            source_ids = {normalize_candidate_id(str(value)) for value in source_df["candidate_id"].astype(str).tolist()} if "candidate_id" in source_df.columns else set()
            review_ids = set(entry_df_day["candidate_id"].astype(str).tolist()) | set(risk_df_day["candidate_id"].astype(str).tolist())
            missing_source_for_day = sorted(review_ids - source_ids)
            if missing_source_for_day:
                source_missing_ids[f"{round_id}:{day}"] = missing_source_for_day

            pack_png = pack_dir / "visual" / round_id / day_compact / f"STAS5_V5C_{round_id}_{day_compact}_CURRENT_REVIEW.png"
            pack_visual_manifest = pack_dir / "manifests" / round_id / day_compact / f"STAS5_V5C_{round_id}_{day_compact}_CURRENT_VISUAL_MANIFEST_V1.json"
            pack_png_rel = _copy_visual(paths["current_review_png"], pack_png)
            pack_visual_manifest_rel = _copy_visual(paths["current_visual_manifest"], pack_visual_manifest)
            visual_files.append(pack_png_rel)
            manifest_files.append(pack_visual_manifest_rel)

            source_meta = {
                "round_id": round_id,
                "compact_day": day_compact,
                "pack_id": pack_id,
                "pack_created_utc": created_utc,
                "source_forward_run_id": spec.forward_run_id,
                "source_forward_entries_csv": rel(source_path),
                "source_entry_review_csv": rel(paths["entry_csv"]),
                "source_riskgate_review_csv": rel(paths["risk_csv"]),
                "source_review_result_json": rel(paths["result_json"]),
                "source_current_review_png": rel(paths["current_review_png"]),
                "pack_current_review_png": pack_png_rel,
                "pack_current_visual_manifest": pack_visual_manifest_rel,
            }

            for row in entry_df_day.to_dict("records"):
                entry_rows.append({**row, **source_meta})
            for row in risk_df_day.to_dict("records"):
                risk_rows.append({**row, **source_meta})

            entry_y = entry_df_day["entry_y"].astype(int)
            risk_y = risk_df_day["risk_bad_y"].astype(int)
            day_rows.append(
                {
                    "round_id": round_id,
                    "day": day,
                    "compact_day": day_compact,
                    "forward_run_id": spec.forward_run_id,
                    "source_forward_entries_csv": rel(source_path),
                    "entry_review_csv": rel(paths["entry_csv"]),
                    "riskgate_review_csv": rel(paths["risk_csv"]),
                    "current_visual_manifest": rel(paths["current_visual_manifest"]),
                    "entry_rows": int(len(entry_df_day)),
                    "entry_good": int(entry_y.eq(1).sum()),
                    "entry_bad": int(entry_y.eq(0).sum()),
                    "risk_bad": int(risk_y.eq(1).sum()),
                    "pack_current_review_png": pack_png_rel,
                    "pack_current_visual_manifest": pack_visual_manifest_rel,
                    "missing_files": [],
                }
            )

    entry_df = pd.DataFrame(entry_rows)
    risk_df = pd.DataFrame(risk_rows)
    entry_good = int(entry_df["entry_y"].astype(int).eq(1).sum()) if not entry_df.empty else 0
    entry_bad = int(entry_df["entry_y"].astype(int).eq(0).sum()) if not entry_df.empty else 0
    risk_bad = int(risk_df["risk_bad_y"].astype(int).eq(1).sum()) if not risk_df.empty else 0

    outputs = {
        "entry_csv": rel(pack_dir / "entry" / ENTRY_ALL_NAME),
        "riskgate_csv": rel(pack_dir / "riskgate" / RISKGATE_ALL_NAME),
        "manifest_json": rel(pack_dir / MANIFEST_NAME),
        "guard_json": rel(pack_dir / GUARD_NAME),
        "audit_ru": rel(pack_dir / AUDIT_NAME),
    }
    manifest = {
        "status": "V5C_REVIEW_PACK_BUILT_NO_TRAINING",
        "pack_id": pack_id,
        "pack_dir": rel(pack_dir),
        "created_utc": created_utc,
        "rounds": {
            spec.round_id.upper(): {
                "start_day": spec.start_day,
                "end_day": spec.end_day,
                "forward_run_id": spec.forward_run_id,
                "days": len(iter_days(spec.start_day, spec.end_day)),
            }
            for spec in round_specs
        },
        "days": len([row for row in day_rows if not row.get("missing_files")]),
        "expected_days": sum(len(iter_days(spec.start_day, spec.end_day)) for spec in round_specs),
        "entry_rows": int(len(entry_df)),
        "entry_good": entry_good,
        "entry_bad": entry_bad,
        "risk_rows": int(len(risk_df)),
        "risk_bad": risk_bad,
        "day_rows": day_rows,
        "visual_files": visual_files,
        "visual_manifest_files": manifest_files,
        "outputs": outputs,
        "rules": {
            "entry_label_contract": "plain good/input -> entry_y=1; plain bad -> entry_y=0; risk bad -> entry_y=0",
            "riskgate_label_contract": "risk bad -> risk_bad_y=1",
            "png_is_visual_only": True,
            "manual_targets_not_live_x439": True,
            "teacher_target_columns": ["entry_y", "risk_bad_y", "phase_y", "state_y", "reason_y", "entry_review_label", "risk_review_label", "user_text_raw"],
        },
        "no_training": True,
        "no_forward": True,
    }

    guard = _build_guard(
        manifest=manifest,
        entry_df=entry_df,
        risk_df=risk_df,
        expected_days=manifest["expected_days"],
        expected_rounds=[spec.round_id.upper() for spec in round_specs],
        expected_day_keys=expected_day_keys,
        source_missing_ids=source_missing_ids,
        missing_files=missing_files,
    )
    manifest["guard_status"] = guard["status"]

    _write_csv(
        pack_dir / "entry" / ENTRY_ALL_NAME,
        entry_rows,
        [
            "round_id",
            "day",
            "candidate_id",
            "record_id",
            "entry_time_utc",
            "entry_y",
            "user_label",
            "entry_review_label",
            "entry_from_risk_bad",
            "model_decision",
            "marker",
            "marker_user",
            "entry_ml_live_score",
            "source_forward_run_id",
            "source_entry_review_csv",
            "pack_current_review_png",
        ],
    )
    _write_csv(
        pack_dir / "riskgate" / RISKGATE_ALL_NAME,
        risk_rows,
        [
            "round_id",
            "day",
            "candidate_id",
            "record_id",
            "entry_time_utc",
            "risk_bad_y",
            "risk_review_label",
            "model_decision",
            "marker",
            "marker_user",
            "risk_user_hint",
            "source_forward_run_id",
            "source_riskgate_review_csv",
            "pack_current_review_png",
        ],
    )
    write_json(pack_dir / MANIFEST_NAME, manifest)
    write_json(pack_dir / GUARD_NAME, guard)
    _write_audit(pack_dir / AUDIT_NAME, manifest, guard)

    if strict and guard["status"] != STATUS_PASS:
        failed = ", ".join(check["check"] for check in guard["failed_checks"])
        raise RuntimeError(f"review pack guard failed: {failed}")

    return entry_df, risk_df, manifest, guard


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build STAS5 V5C approved review pack for R2/R3/R4")
    parser.add_argument("--pack-id", default=PACK_ID_DEFAULT)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--no-strict", action="store_true")
    args = parser.parse_args(argv)

    _entry_df, _risk_df, manifest, guard = build_review_pack(
        pack_id=args.pack_id,
        force=bool(args.force),
        strict=not bool(args.no_strict),
    )
    print(
        json.dumps(
            {
                "status": guard["status"],
                "pack_id": manifest["pack_id"],
                "pack_dir": manifest["pack_dir"],
                "days": manifest["days"],
                "entry_rows": manifest["entry_rows"],
                "entry_good": manifest["entry_good"],
                "entry_bad": manifest["entry_bad"],
                "risk_bad": manifest["risk_bad"],
                "outputs": manifest["outputs"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
