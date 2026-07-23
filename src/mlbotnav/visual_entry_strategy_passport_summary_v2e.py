from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap


STATUS = "V2E_SUMMARY_MATRIX_20260514_READY_FOR_USER_REVIEW_NO_SCORER_NO_ML_NO_OPTUNA"
RAIL_POINT = "V2E_SUMMARY_MATRIX"

BLOCKS: list[dict[str, str]] = [
    {"id": "B014", "short": "level", "layer": "V2A", "role": "broad_context"},
    {"id": "B015", "short": "fibo", "layer": "V2A", "role": "context_needs_freshness"},
    {"id": "B017", "short": "retest", "layer": "V2A", "role": "candidate_evidence"},
    {"id": "B018", "short": "bos", "layer": "V2A", "role": "broad_context"},
    {"id": "B010", "short": "volume", "layer": "V2B", "role": "flow_evidence"},
    {"id": "B013", "short": "vpoc", "layer": "V2B", "role": "density_evidence"},
    {"id": "B026", "short": "vwap", "layer": "V2B", "role": "mixed_context"},
    {"id": "B008", "short": "adx", "layer": "V2C", "role": "strength_context"},
    {"id": "B009", "short": "stoch", "layer": "V2C", "role": "too_broad_context"},
    {"id": "B019", "short": "candle", "layer": "V2D", "role": "pattern_evidence"},
    {"id": "B020", "short": "div", "layer": "V2D", "role": "selective_evidence"},
    {"id": "B021", "short": "pqual", "layer": "V2D", "role": "too_broad_context"},
    {"id": "B022", "short": "chart", "layer": "V2D", "role": "too_broad_context"},
    {"id": "B023", "short": "confirm", "layer": "V2D", "role": "broad_context"},
    {"id": "B024", "short": "composite", "layer": "V2D", "role": "broad_context"},
]

LAYER_FILES = {
    "V2A": "strategy_passport_overlay_v2a/V2A_STRUCTURE_OVERLAY_20260514.csv",
    "V2B": "strategy_passport_overlay_v2b/V2B_FLOW_DENSITY_OVERLAY_20260514.csv",
    "V2C": "strategy_passport_overlay_v2c_adx_stoch/V2C_ADX_STOCH_OVERLAY_20260514.csv",
    "V2D": "strategy_passport_overlay_v2d_patterns/V2D_PATTERN_OVERLAY_20260514.csv",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _base_dir(root: Path) -> Path:
    return root / "reports/final_review/visual_entry_v3/fresh_target_led"


def _split_blocks(value: Any) -> set[str]:
    if value is None or pd.isna(value):
        return set()
    return {part.strip() for part in str(value).split(",") if part.strip()}


def _has_block(tokens: set[str], block_id: str) -> bool:
    return any(token == block_id or token.startswith(f"{block_id}_") for token in tokens)


def _state_for(row: pd.Series, block_id: str) -> str:
    supporting = _split_blocks(row.get("supporting_blocks"))
    conflict = _split_blocks(row.get("conflict_blocks"))
    if _has_block(conflict, block_id):
        return "conflict"
    if _has_block(supporting, block_id):
        return "support"
    return "silent"


def _load_layer(root: Path, layer: str) -> pd.DataFrame:
    path = _base_dir(root) / LAYER_FILES[layer]
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def _build_matrix(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    layers = {name: _load_layer(root, name) for name in LAYER_FILES}
    by_target: dict[str, dict[str, pd.Series]] = {}
    target_meta: dict[str, dict[str, Any]] = {}
    for layer, df in layers.items():
        for _, row in df.iterrows():
            target_id = str(row["target_id"])
            by_target.setdefault(target_id, {})[layer] = row
            target_meta.setdefault(
                target_id,
                {
                    "target_id": target_id,
                    "target_type": str(row.get("target_type", "")),
                    "signal_time_utc": str(row.get("signal_time_utc", "")),
                    "entry_time_utc": str(row.get("entry_time_utc", "")),
                    "entry_open_price": row.get("entry_open_price", ""),
                    "entry_price_plus_5bps": row.get("entry_price_plus_5bps", ""),
                },
            )

    rows: list[dict[str, Any]] = []
    target_ids = sorted(target_meta, key=lambda item: int(item[1:]) if item.startswith("M") and item[1:].isdigit() else item)
    for target_id in target_ids:
        record = dict(target_meta[target_id])
        support_count = 0
        conflict_count = 0
        silent_count = 0
        for block in BLOCKS:
            row = by_target[target_id].get(block["layer"])
            state = _state_for(row, block["id"]) if row is not None else "silent"
            record[f"{block['id']}_state"] = state
            if state == "support":
                support_count += 1
            elif state == "conflict":
                conflict_count += 1
            else:
                silent_count += 1
        record["support_count"] = support_count
        record["conflict_count"] = conflict_count
        record["silent_count"] = silent_count
        record["summary_note"] = _row_note(record)
        rows.append(record)

    block_summary: list[dict[str, Any]] = []
    for block in BLOCKS:
        states = [row[f"{block['id']}_state"] for row in rows]
        support = states.count("support")
        conflict = states.count("conflict")
        silent = states.count("silent")
        block_summary.append(
            {
                "block_id": block["id"],
                "short": block["short"],
                "layer": block["layer"],
                "role": block["role"],
                "support": support,
                "conflict": conflict,
                "silent": silent,
                "audit": _block_audit(block["id"], support, conflict, silent),
            }
        )
    return rows, block_summary


def _block_audit(block_id: str, support: int, conflict: int, silent: int) -> str:
    if support >= 17 and conflict <= 1:
        return "too_broad_context"
    if 7 <= support <= 15 and conflict <= 2:
        return "candidate_evidence"
    if conflict >= 4:
        return "mixed_or_conflicting"
    if support <= 3:
        return "mostly_silent"
    return "context"


def _row_note(record: dict[str, Any]) -> str:
    support = int(record["support_count"])
    conflict = int(record["conflict_count"])
    if conflict >= 3:
        return "mixed_needs_visual_review"
    if support >= 11 and conflict == 0:
        return "many_layers_support_but_check_broad_blocks"
    if support >= 8:
        return "moderate_support"
    return "thin_support"


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _state_value(state: str) -> int:
    if state == "support":
        return 1
    if state == "conflict":
        return -1
    return 0


def _render_matrix(path: Path, rows: list[dict[str, Any]], block_summary: list[dict[str, Any]]) -> None:
    block_ids = [block["block_id"] for block in block_summary]
    values = np.array([[_state_value(str(row[f"{block}_state"])) for block in block_ids] for row in rows], dtype=float)
    cmap = ListedColormap(["#b54545", "#142027", "#12b886"])

    fig, ax = plt.subplots(figsize=(18, 10), facecolor="#0f1419")
    ax.set_facecolor("#0f1419")
    ax.imshow(values, aspect="auto", cmap=cmap, vmin=-1, vmax=1)

    labels = [f"{row['target_id']} {str(row['target_type']).replace('_', ' ')[:18]}" for row in rows]
    col_labels = [f"{item['block_id']}\n{item['short']}" for item in block_summary]
    ax.set_yticks(np.arange(len(rows)))
    ax.set_yticklabels(labels, fontsize=9, color="#dfe5ea")
    ax.set_xticks(np.arange(len(block_ids)))
    ax.set_xticklabels(col_labels, fontsize=9, color="#dfe5ea", rotation=0)
    ax.xaxis.tick_top()

    for y, row in enumerate(rows):
        for x, block_id in enumerate(block_ids):
            state = row[f"{block_id}_state"]
            text = "S" if state == "support" else "C" if state == "conflict" else "."
            color = "#06130e" if state == "support" else "#f5d3d3" if state == "conflict" else "#6f7f88"
            ax.text(x, y, text, ha="center", va="center", fontsize=8, color=color, fontweight="bold")

    for x in range(len(block_ids) + 1):
        ax.axvline(x - 0.5, color="#26333d", linewidth=0.7)
    for y in range(len(rows) + 1):
        ax.axhline(y - 0.5, color="#26333d", linewidth=0.7)

    for boundary in [4, 7, 9]:
        ax.axvline(boundary - 0.5, color="#d6a94a", linewidth=2.0)

    ax.set_title(
        "SOLUSDT 1m 2026-05-14 | V2E summary matrix | S=support C=conflict .=silent | NO ML/OPTUNA",
        color="#edf2f7",
        fontsize=16,
        pad=36,
    )
    ax.set_xlabel("blocks: V2A structure | V2B flow/density | V2C ADX/Stoch | V2D patterns", color="#b8c2cc", labelpad=16)
    ax.tick_params(colors="#dfe5ea")
    for spine in ax.spines.values():
        spine.set_color("#33424d")

    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _write_report(
    path: Path,
    *,
    root: Path,
    matrix_png: Path,
    matrix_csv: Path,
    block_csv: Path,
    json_path: Path,
    rows: list[dict[str, Any]],
    block_summary: list[dict[str, Any]],
) -> None:
    broad = [item for item in block_summary if item["audit"] == "too_broad_context"]
    candidates = [item for item in block_summary if item["audit"] == "candidate_evidence"]
    conflicts = [item for item in block_summary if item["conflict"]]
    lines = [
        "# V2E Summary Matrix 2026-05-14",
        "",
        f"Статус: `{STATUS}`.",
        "",
        "Назначение: свести уже готовые visual/passport слои `V2A/V2B/V2C/V2D` по ручному эталону `SOLUSDT 1m 2026-05-14 M01..M19`.",
        "",
        "Это не scorer, не target-lock, не Optuna и не ML/export.",
        "",
        "## Артефакты",
        "",
        f"- `{_rel(root, matrix_png)}`",
        f"- `{_rel(root, matrix_csv)}`",
        f"- `{_rel(root, block_csv)}`",
        f"- `{_rel(root, json_path)}`",
        "",
        "## Широкие контекстные блоки",
        "",
    ]
    if broad:
        for item in broad:
            lines.append(f"- `{item['block_id']}` `{item['short']}`: support `{item['support']}/19`, conflict `{item['conflict']}/19`.")
    else:
        lines.append("- Нет блоков с широким покрытием по текущему правилу.")
    lines.extend(["", "## Кандидаты evidence", ""])
    if candidates:
        for item in candidates:
            lines.append(f"- `{item['block_id']}` `{item['short']}`: support `{item['support']}/19`, conflict `{item['conflict']}/19`.")
    else:
        lines.append("- Нет явных кандидатов.")
    lines.extend(["", "## Конфликты", ""])
    if conflicts:
        for item in conflicts:
            lines.append(f"- `{item['block_id']}` `{item['short']}`: conflict `{item['conflict']}/19`.")
    else:
        lines.append("- Конфликтов нет.")
    lines.extend(
        [
            "",
            "## Следующий подпункт",
            "",
            "После user review по этой матрице выбрать первый рабочий кластер/паспорт-кандидат по 14 мая. Не переходить к scorer, target-lock, Optuna или ML без отдельного решения пользователя.",
            "",
            "## Target notes",
            "",
        ]
    )
    for row in rows:
        lines.append(
            f"- `{row['target_id']}` `{row['target_type']}`: support `{row['support_count']}`, conflict `{row['conflict_count']}`, note `{row['summary_note']}`."
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(day: str) -> dict[str, Any]:
    if day != "2026-05-14":
        raise ValueError("V2E summary matrix is fixed to the first manual benchmark: 2026-05-14 M01-M19.")
    root = _repo_root()
    out_dir = _base_dir(root) / "strategy_passport_summary_v2e"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows, block_summary = _build_matrix(root)
    matrix_csv = out_dir / "V2E_SUMMARY_MATRIX_20260514.csv"
    block_csv = out_dir / "V2E_BLOCK_SUMMARY_20260514.csv"
    json_path = out_dir / "V2E_SUMMARY_MATRIX_20260514.json"
    report_ru = out_dir / "V2E_SUMMARY_MATRIX_20260514_RU.md"
    matrix_png = out_dir / "V2E_SUMMARY_MATRIX_20260514.png"

    matrix_fields = [
        "target_id",
        "target_type",
        "signal_time_utc",
        "entry_time_utc",
        "entry_open_price",
        "entry_price_plus_5bps",
    ] + [f"{block['id']}_state" for block in BLOCKS] + ["support_count", "conflict_count", "silent_count", "summary_note"]
    block_fields = ["block_id", "short", "layer", "role", "support", "conflict", "silent", "audit"]
    _write_csv(matrix_csv, rows, matrix_fields)
    _write_csv(block_csv, block_summary, block_fields)
    json_path.write_text(
        json.dumps(
            {
                "status": STATUS,
                "rail_point": RAIL_POINT,
                "generated_at_utc": _utc_now(),
                "day": day,
                "rows": rows,
                "block_summary": block_summary,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _render_matrix(matrix_png, rows, block_summary)
    _write_report(
        report_ru,
        root=root,
        matrix_png=matrix_png,
        matrix_csv=matrix_csv,
        block_csv=block_csv,
        json_path=json_path,
        rows=rows,
        block_summary=block_summary,
    )
    return {
        "status": STATUS,
        "artifacts": {
            "matrix_png": _rel(root, matrix_png),
            "matrix_csv": _rel(root, matrix_csv),
            "block_csv": _rel(root, block_csv),
            "json": _rel(root, json_path),
            "report_ru": _rel(root, report_ru),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", default="2026-05-14")
    args = parser.parse_args()
    print(json.dumps(run(args.day), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
