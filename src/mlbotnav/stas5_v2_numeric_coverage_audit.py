from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from mlbotnav.stas5_common import STAS5_ARTIFACTS_DIR, load_manifest_feature_columns, read_csv, rel, utc_now, write_json
from mlbotnav.stas5_v2_feature_snapshot_builder import (
    DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH,
    DEFAULT_V2_FEATURE_SNAPSHOT_PATH,
)


STATUS = "STAS5_V2_NUMERIC_COVERAGE_AUDIT_READY_NO_TRAINING_NO_TP_NO_API_NO_STAS3"
DEFAULT_DAY = "2026-05-04"
DEFAULT_AUDIT_JSON_PATH = STAS5_ARTIFACTS_DIR / "v2_audit" / "stas5_v2_numeric_coverage_audit_20260504_v0.json"
DEFAULT_AUDIT_MD_PATH = STAS5_ARTIFACTS_DIR / "v2_audit" / "STAS5_V2_NUMERIC_COVERAGE_AUDIT_20260504_RU.md"
DEFAULT_VISUAL_MANIFEST_PATH = (
    STAS5_ARTIFACTS_DIR
    / "v2"
    / "visual_approval"
    / "20260504"
    / "STAS5_V2_FEATURE_VISUAL_APPROVAL_20260504.manifest.json"
)


def _matches(columns: list[str], *, prefixes: tuple[str, ...] = (), contains: tuple[str, ...] = ()) -> list[str]:
    out: list[str] = []
    for column in columns:
        text = column.lower()
        if prefixes and any(column.startswith(prefix) for prefix in prefixes):
            out.append(column)
        elif contains and any(token in text for token in contains):
            out.append(column)
    return out


def _block(name: str, status: str, role: str, columns: list[str], note: str) -> dict[str, Any]:
    return {
        "block": name,
        "status": status,
        "role": role,
        "feature_column_count": len(columns),
        "feature_columns": columns,
        "note": note,
    }


def _label_counts(day_rows: pd.DataFrame) -> dict[str, int]:
    labels = day_rows.get("human_label", pd.Series(dtype=str)).astype(str)
    yellow = pd.to_numeric(day_rows.get("yellow_x", pd.Series(dtype=int)), errors="coerce").fillna(0).astype(int)
    conflict = pd.to_numeric(day_rows.get("yellow_x_conflict", pd.Series(dtype=int)), errors="coerce").fillna(0).astype(int)
    return {
        "rows": int(len(day_rows)),
        "KEEP_DRAFT": int((labels == "KEEP_DRAFT").sum()),
        "CUT_DRAFT": int((labels == "CUT_DRAFT").sum()),
        "yellow_x": int((yellow == 1).sum()),
        "keep_yellow_conflict": int(((labels.str.contains("KEEP", case=False, na=False)) & (conflict == 1)).sum()),
    }


def build_numeric_coverage_audit_from_frames(
    *,
    snapshot: pd.DataFrame,
    feature_columns: list[str],
    day: str,
    visual_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    feature_columns = [str(column) for column in feature_columns]
    feature_set = set(feature_columns)
    day_rows = snapshot[snapshot["day"].astype(str) == day].copy() if "day" in snapshot else pd.DataFrame()

    block_rows = [
        _block(
            "Свечи и сырой volume на графике",
            "VISUAL_REFERENCE_ONLY_WITH_DERIVED_FEATURES",
            "помогают глазами сверить рынок; ML не получает PNG или сырые свечи пачкой",
            _matches(feature_columns, prefixes=("stas4_v2_volume_",), contains=("volume",)),
            "В ML идут производные pre-entry признаки объема/волатильности, а не сама картинка.",
        ),
        _block(
            "Сессии и заливка фона",
            "FEATURE_READY",
            "контекст времени/сессии",
            _matches(feature_columns, contains=("session", "weekend", "day_type")),
            "Цветовая заливка renderer-only, но session/day признаки есть в feature matrix.",
        ),
        _block(
            "FON / background phase",
            "FEATURE_READY",
            "общий фон до входа",
            _matches(feature_columns, contains=("background_phase", "phase_metric", "phase_rank")),
            "Используются pre-entry окна 5/15/30/60m, не закрытый час как готовый сигнал.",
        ),
        _block(
            "LONG wave",
            "FEATURE_READY",
            "LONG-движение до входа",
            _matches(feature_columns, contains=("long_wave",)),
            "В ML идут pre-entry LONG-wave признаки по окнам 5/15/30/60m.",
        ),
        _block(
            "SHORT wave",
            "FEATURE_READY",
            "SHORT-давление до входа",
            _matches(feature_columns, prefixes=("stas5_v2_short_wave_",)),
            "Добавлен causal short-wave слой по окнам 5/15/30/60m: падение от high, bounce, rank.",
        ),
        _block(
            "Macro WAVE полоса",
            "AUDIT_VISUAL_NOT_DIRECT_FEATURE",
            "крупный обзор волны на картинке",
            _matches(feature_columns, contains=("long_wave", "short_wave")),
            "Саму macro WAVE-полосу не переносим напрямую: она обзорная. Вместо нее в ML идут causal LONG/SHORT window features.",
        ),
        _block(
            "Human KEEP/CUT",
            "TARGET_ONLY",
            "цель обучения",
            [column for column in ["human_label", "label_status", "label_source"] if column in snapshot.columns and column not in feature_set],
            "Это target/metadata. В feature_columns не входит.",
        ),
        _block(
            "Yellow X / conflict",
            "AUDIT_ONLY_METADATA",
            "контроль старых X и конфликтов с ручным KEEP",
            [column for column in ["yellow_x", "yellow_x_role", "yellow_x_conflict"] if column in snapshot.columns and column not in feature_set],
            "В feature_columns запрещено. KEEP с yellow_x сохраняются как строки, но X не давит на ML как label.",
        ),
        _block(
            "STAS4 Audit: 4 выбранных блока",
            "FEATURE_READY_AS_NUMERIC_CONTEXT",
            "числовой контекст стратегических блоков, не фильтр",
            _matches(feature_columns, prefixes=("stas4_v2_block_",)),
            "Добавлены support/conflict/net для density+structure, pattern+structure, structure+volume, structure+trend.",
        ),
        _block(
            "Pattern / свечные конфликты",
            "FEATURE_READY",
            "pattern слой для pattern+structure",
            _matches(feature_columns, prefixes=("stas4_v2_pattern_",)),
            "Добавлены pattern_strength, age, bull/bear candles, chart/confirm flags, все до anchor.",
        ),
        _block(
            "Density / Structure",
            "FEATURE_READY",
            "уровни, плотность, поддержка/конфликт",
            _matches(feature_columns, prefixes=("stas4_v2_density_", "stas4_v2_structure_")),
            "Уже было в ML, осталось и используется в новых block scores.",
        ),
        _block(
            "Risk / Gate",
            "FEATURE_READY",
            "risk/noise диагностика",
            _matches(feature_columns, prefixes=("stas5_v2_risk_", "stas5_v2_gate_")),
            "Это признаки для анализа/будущего gate, не финальное разрешение на сделку.",
        ),
        _block(
            "V2 Combo indicators",
            "FEATURE_READY",
            "RSI/MACD/Stoch/ATR/EMA/pressure/recovery",
            _matches(feature_columns, prefixes=("stas4_v2_combo_", "stas4_v2_indicator_")),
            "Нижний combo-индикатор превращен в candidate-time числа.",
        ),
        _block(
            "COMBO SPECTRUM continuous panel",
            "FEATURE_READY_PARTIAL_CANDIDATE_SNAPSHOT",
            "непрерывная нижняя визуальная панель",
            _matches(feature_columns, prefixes=("stas4_v2_combo_", "stas4_v2_indicator_", "stas4_v2_div_")),
            "ML не видит всю линию как картинку; он видит snapshot компонентов на anchor_time.",
        ),
    ]

    missing_or_visual_only = [
        item
        for item in block_rows
        if item["status"] in {"VISUAL_REFERENCE_ONLY_WITH_DERIVED_FEATURES", "AUDIT_VISUAL_NOT_DIRECT_FEATURE", "TARGET_ONLY", "AUDIT_ONLY_METADATA"}
    ]
    samples: list[dict[str, Any]] = []
    sample_columns = [
        "candidate_id",
        "human_label",
        "stas4_v2_block_density_structure_net_score",
        "stas4_v2_block_pattern_structure_net_score",
        "stas4_v2_block_structure_volume_net_score",
        "stas4_v2_block_structure_trend_net_score",
        "stas5_v2_short_wave_15m_down_from_high_pct",
        "stas5_v2_short_wave_60m_phase_rank",
        "stas4_v2_pattern_strength",
        "stas5_v2_risk_knife_pre_entry",
    ]
    if not day_rows.empty:
        for _, row in day_rows.head(8).iterrows():
            samples.append({column: row.get(column, "") for column in sample_columns if column in day_rows.columns})

    return {
        "status": STATUS,
        "created_utc": utc_now(),
        "day": day,
        "rows_for_day": int(len(day_rows)),
        "label_counts_for_day": _label_counts(day_rows),
        "feature_count": int(len(feature_columns)),
        "block_coverage": block_rows,
        "visual_manifest_strategy_audit_counts": (visual_manifest or {}).get("strategy_audit_counts", {}),
        "feature_group_counts": dict(Counter(item["status"] for item in block_rows)),
        "not_direct_ml_blocks": missing_or_visual_only,
        "sample_rows": samples,
        "conclusion": {
            "main_gap_fixed": "STAS4 Audit blocks, pattern layer, and causal SHORT-wave are now numeric features.",
            "still_not_direct_features_by_design": "raw PNG/candles, human labels, yellow X/conflict, and macro WAVE overview strip.",
            "training_started": False,
            "tp_stas3_api_optuna_used": False,
        },
    }


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# STAS5 V2 Numeric Coverage Audit 2026-05-04",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        f"День: `{payload['day']}`. Строк за день: `{payload['rows_for_day']}`. Feature columns: `{payload['feature_count']}`.",
        "",
        "Граница: обучение, TP/Stas3, API, Optuna и threshold tuning не запускались.",
        "",
        "## Итог",
        "",
        "- Основная дырка закрыта: четыре STAS4 audit-блока теперь представлены числовыми `stas4_v2_block_*` признаками.",
        "- Добавлен pattern layer `stas4_v2_pattern_*` для `pattern+structure`.",
        "- Добавлен causal SHORT-wave слой `stas5_v2_short_wave_*`, чтобы ML видел давление вниз до входа.",
        "- Human KEEP/CUT остается target, yellow X/conflict остается metadata/audit-only.",
        "- Macro WAVE-полоса не перенесена напрямую, потому что это обзорный visual layer; вместо нее используются causal LONG/SHORT window features.",
        "",
        "## Покрытие Блоков",
        "",
        "| Блок | Статус | Колонок | Роль | Примечание |",
        "|---|---|---:|---|---|",
    ]
    for item in payload["block_coverage"]:
        lines.append(
            f"| {item['block']} | `{item['status']}` | {item['feature_column_count']} | {item['role']} | {item['note']} |"
        )
    lines.extend(["", "## STAS4 Audit Counts С Графика", ""])
    counts = payload.get("visual_manifest_strategy_audit_counts") or {}
    if counts:
        lines.extend(["| Блок | X old | UP new |", "|---|---:|---:|"])
        for name, item in counts.items():
            lines.append(f"| `{name}` | {item.get('old_removed', 0)} | {item.get('new_candidates', 0)} |")
    else:
        lines.append("Visual manifest не найден или не содержит `strategy_audit_counts`.")
    lines.extend(["", "## Пример Новых Чисел", ""])
    samples = payload.get("sample_rows") or []
    if samples:
        columns = list(samples[0].keys())
        lines.append("| " + " | ".join(columns) + " |")
        lines.append("|" + "|".join("---" for _ in columns) + "|")
        for row in samples:
            lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    else:
        lines.append("Нет строк для примера.")
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_numeric_coverage_audit(
    *,
    day: str = DEFAULT_DAY,
    snapshot_path: Path = DEFAULT_V2_FEATURE_SNAPSHOT_PATH,
    manifest_path: Path = DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH,
    visual_manifest_path: Path = DEFAULT_VISUAL_MANIFEST_PATH,
    output_json: Path = DEFAULT_AUDIT_JSON_PATH,
    output_md: Path = DEFAULT_AUDIT_MD_PATH,
) -> dict[str, Any]:
    snapshot = read_csv(snapshot_path)
    feature_columns = load_manifest_feature_columns(manifest_path)
    visual_manifest: dict[str, Any] | None = None
    if visual_manifest_path.exists():
        visual_manifest = json.loads(visual_manifest_path.read_text(encoding="utf-8"))
    payload = build_numeric_coverage_audit_from_frames(
        snapshot=snapshot,
        feature_columns=feature_columns,
        day=day,
        visual_manifest=visual_manifest,
    )
    payload["source_snapshot"] = rel(snapshot_path)
    payload["source_manifest"] = rel(manifest_path)
    payload["source_visual_manifest"] = rel(visual_manifest_path) if visual_manifest_path.exists() else ""
    payload["output_json"] = rel(output_json)
    payload["output_md"] = rel(output_md)
    write_json(output_json, payload)
    _write_markdown(output_md, payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="STAS5 V2 numeric coverage audit, no ML training.")
    parser.add_argument("--day", default=DEFAULT_DAY)
    parser.add_argument("--snapshot-path", type=Path, default=DEFAULT_V2_FEATURE_SNAPSHOT_PATH)
    parser.add_argument("--manifest-path", type=Path, default=DEFAULT_V2_FEATURE_SNAPSHOT_MANIFEST_PATH)
    parser.add_argument("--visual-manifest-path", type=Path, default=DEFAULT_VISUAL_MANIFEST_PATH)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_AUDIT_JSON_PATH)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_AUDIT_MD_PATH)
    args = parser.parse_args()
    payload = run_numeric_coverage_audit(
        day=args.day,
        snapshot_path=args.snapshot_path,
        manifest_path=args.manifest_path,
        visual_manifest_path=args.visual_manifest_path,
        output_json=args.output_json,
        output_md=args.output_md,
    )
    print({"status": payload["status"], "day": payload["day"], "rows": payload["rows_for_day"], "feature_count": payload["feature_count"]})


if __name__ == "__main__":
    main()
