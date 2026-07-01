from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from mlbotnav.visual_entry_low_anchor_suggester import _draw_candles, _load_ohlcv, _source_csv, _style_axis


STATUS = "LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_READY_NO_ML_NO_OPTUNA"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fmt_minute(value: str | pd.Timestamp) -> str:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        ts = ts.tz_localize("UTC")
    else:
        ts = ts.tz_convert("UTC")
    return ts.strftime("%H:%M")


def _candidate_map(suggester: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["candidate_id"]): item for item in suggester.get("candidates", [])}


def _target_map(ledger: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["target_id"]): item for item in ledger.get("targets", [])}


def _extra_rows(label_ledger: dict[str, Any], suggester: dict[str, Any], targets: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = _candidate_map(suggester)
    rows: list[dict[str, Any]] = []
    for label in label_ledger.get("candidate_records", []):
        if label.get("candidate_label") != "extra_auto_unlabeled_candidate":
            continue
        candidate = candidates[str(label["candidate_id"])]
        nearest_target_id = str(candidate.get("nearest_manual_target") or "")
        nearest_target = targets.get(nearest_target_id, {})
        rows.append(
            {
                "candidate_id": candidate["candidate_id"],
                "review_label": "pending_user_anti_review",
                "review_choices": ["bad_noise", "duplicate", "possible_entry", "wrong_type", "ignore_unclear"],
                "signal_time_utc": candidate["signal_time_utc"],
                "entry_time_utc": candidate["entry_time_utc"],
                "anchor_time_utc": candidate["anchor_time_utc"],
                "anchor_low_price": candidate["anchor_low_price"],
                "entry_open_price": candidate["entry_open_price"],
                "entry_price_plus_5bps": candidate["entry_price_plus_5bps"],
                "score": candidate["score"],
                "suggested_type": candidate["suggested_type"],
                "risk_flags": candidate.get("risk_flags", []),
                "nearest_manual_target": nearest_target_id,
                "nearest_manual_target_type": nearest_target.get("target_type"),
                "signal_diff_minutes_to_nearest_target": candidate.get("signal_diff_minutes_to_nearest_target"),
                "matched_manual_target_within_3m": candidate.get("matched_manual_target_within_3m"),
            }
        )
    rows.sort(key=lambda item: item["signal_time_utc"])
    return rows


def build_payload(
    *,
    root: Path,
    label_ledger_path: Path,
    suggester_path: Path,
    target_ledger_path: Path,
    out_dir: Path,
    rows: list[dict[str, Any]],
    page_size: int,
) -> dict[str, Any]:
    pages = ceil(len(rows) / page_size) if rows else 0
    page_artifacts = [
        str((out_dir / f"LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_PAGE_{idx:02d}_20260701.png").relative_to(root)).replace("\\", "/")
        for idx in range(1, pages + 1)
    ]
    return {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "rail_point": "LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_ANTI_REVIEW_NO_ML_NO_OPTUNA",
        "source_label_ledger": str(label_ledger_path.relative_to(root)).replace("\\", "/"),
        "source_suggester_json": str(suggester_path.relative_to(root)).replace("\\", "/"),
        "source_target_ledger": str(target_ledger_path.relative_to(root)).replace("\\", "/"),
        "candidate_count": len(rows),
        "page_size": page_size,
        "pages": pages,
        "records": rows,
        "review_choices_ru": {
            "bad_noise": "плохой шумовой вход, не нужен",
            "duplicate": "дубль рядом с хорошей ручной точкой",
            "possible_entry": "возможно полезный вход, надо отдельно рассмотреть",
            "wrong_type": "другой тип входа, не для этого low-anchor слоя",
            "ignore_unclear": "непонятно, оставить без label",
        },
        "rule_implications_ru": [
            "Extra auto candidates не являются negative labels автоматически.",
            "До ручного verdict эти строки нельзя использовать для ML/export.",
            "Если пользователь пометит часть как bad_noise, они станут anti-examples для event dataset draft.",
            "Если пользователь пометит possible_entry, их нужно вынести в отдельный target-led review, а не смешивать с M01..M19.",
        ],
        "no_lookahead_boundary": {
            "review_only": True,
            "optuna_allowed": False,
            "ml_allowed": False,
            "entry_open_price_is_execution_price_only": True,
            "forbidden_for_selection": ["future_return", "tp_sl", "mfe_mae", "entry_candle_ohlcv"],
        },
        "artifacts": {
            "json": str((out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_20260701.json").relative_to(root)).replace("\\", "/"),
            "csv": str((out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_20260701.csv").relative_to(root)).replace("\\", "/"),
            "report_ru": str((out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_20260701_RU.md").relative_to(root)).replace("\\", "/"),
            "page_pngs": page_artifacts,
        },
        "optuna_allowed": False,
        "ml_allowed": False,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = [
        "candidate_id",
        "review_label",
        "signal_time_utc",
        "entry_time_utc",
        "entry_open_price",
        "entry_price_plus_5bps",
        "score",
        "suggested_type",
        "risk_flags",
        "nearest_manual_target",
        "nearest_manual_target_type",
        "signal_diff_minutes_to_nearest_target",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            out = dict(row)
            out["risk_flags"] = ",".join(out.get("risk_flags") or [])
            writer.writerow({col: out.get(col) for col in columns})


def write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Low Anchor Suggester V1: extra auto review",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: показать лишние auto-кандидаты как anti-review pool. Это не negative labels автоматически.",
        "",
        f"Кандидатов на review: `{payload['candidate_count']}`.",
        f"Страниц PNG: `{payload['pages']}`.",
        "",
        "## Как размечать",
        "",
        "| label | смысл |",
        "|---|---|",
    ]
    for key, text in payload["review_choices_ru"].items():
        lines.append(f"| `{key}` | {text} |")
    lines.extend(
        [
            "",
            "## Страницы",
            "",
        ]
    )
    for idx, png in enumerate(payload["artifacts"]["page_pngs"], 1):
        lines.append(f"{idx}. `{png}`")
    lines.extend(
        [
            "",
            "## Границы",
            "",
            "- Scorer, Optuna, ML/export/promotion не запускались.",
            "- До ручной оценки эти кандидаты остаются `pending_user_anti_review`.",
            "- Цена входа показана только как execution/visual control, не как признак выбора.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_pages(
    *,
    df: pd.DataFrame,
    rows: list[dict[str, Any]],
    out_dir: Path,
    timeframe: str,
    page_size: int,
) -> list[Path]:
    page_paths: list[Path] = []
    cols = 3
    rows_per_page = ceil(page_size / cols)
    for page_idx in range(ceil(len(rows) / page_size)):
        chunk = rows[page_idx * page_size : (page_idx + 1) * page_size]
        fig, axes = plt.subplots(rows_per_page, cols, figsize=(24, 4.8 * rows_per_page), sharex=False)
        fig.patch.set_facecolor("#101418")
        flat = list(axes.flatten() if hasattr(axes, "flatten") else [axes])
        for ax, item in zip(flat, chunk):
            _style_axis(ax)
            signal = pd.Timestamp(item["signal_time_utc"])
            start = signal - pd.Timedelta(minutes=20)
            end = signal + pd.Timedelta(minutes=32)
            win = df[(df["open_time_utc"] >= start) & (df["open_time_utc"] <= end)].reset_index(drop=True)
            _draw_candles(ax, win, timeframe, linewidth=0.58)

            signal_naive = signal.tz_convert(None)
            entry = pd.Timestamp(item["entry_time_utc"]).tz_convert(None)
            anchor = pd.Timestamp(item["anchor_time_utc"]).tz_convert(None)
            anchor_low = float(item["anchor_low_price"])
            entry_price = float(item["entry_price_plus_5bps"])

            ax.axvline(signal_naive, color="#26c6da", linewidth=1.4, alpha=0.85, zorder=0)
            ax.axvline(entry, color="#00e676", linewidth=1.0, alpha=0.65, linestyle="--", zorder=0)
            ax.scatter([anchor], [anchor_low], s=62, color="#ff5252", edgecolors="#0b0f12", linewidths=0.7, zorder=6)
            ax.scatter([entry], [entry_price], marker="^", s=95, color="#26c6da", edgecolors="white", linewidths=0.55, zorder=8)
            ax.annotate(
                f"{item['candidate_id']} entry {_fmt_minute(item['entry_time_utc'])}\nprice+5bps {entry_price:.5f}",
                xy=(entry, entry_price),
                xytext=(8, 15),
                textcoords="offset points",
                color="#26c6da",
                fontsize=8,
                arrowprops={"arrowstyle": "->", "color": "#26c6da", "linewidth": 0.9},
                bbox={"facecolor": "#0b2730", "edgecolor": "#26c6da", "alpha": 0.72, "boxstyle": "round,pad=0.2"},
            )
            diff = item.get("signal_diff_minutes_to_nearest_target")
            nearest = item.get("nearest_manual_target") or "-"
            flags = ",".join(item.get("risk_flags") or [])
            title = (
                f"{item['candidate_id']} {item['suggested_type']} | "
                f"nearest {nearest} {diff:+}m | score {float(item['score']):.2f}"
            )
            ax.set_title(title, color="white", fontsize=9)
            if flags:
                ax.text(
                    0.02,
                    0.04,
                    flags[:80],
                    transform=ax.transAxes,
                    color="#ffcc80",
                    fontsize=7,
                    bbox={"facecolor": "#2b2114", "edgecolor": "#ffcc80", "alpha": 0.65, "boxstyle": "round,pad=0.18"},
                )
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            ax.tick_params(axis="x", labelrotation=20)

        for ax in flat[len(chunk) :]:
            ax.axis("off")
            ax.set_facecolor("#101418")

        fig.suptitle(
            f"LOW_ANCHOR V1 extra auto review page {page_idx + 1} | pending user anti-review | NO ML/OPTUNA",
            color="white",
            fontsize=15,
        )
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        out_path = out_dir / f"LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_PAGE_{page_idx + 1:02d}_20260701.png"
        fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor())
        plt.close(fig)
        page_paths.append(out_path)
    return page_paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Build extra auto candidate anti-review pack for low-anchor labels.")
    parser.add_argument("--day", default="2026-05-14")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--page-size", type=int, default=12)
    parser.add_argument(
        "--label-ledger",
        default="reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_LABEL_LEDGER_20260701.json",
    )
    parser.add_argument(
        "--suggester-json",
        default="reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_20260514.json",
    )
    parser.add_argument(
        "--target-ledger",
        default="reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_M01_M19.json",
    )
    parser.add_argument(
        "--out-dir",
        default="reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    out_dir = root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    label_ledger_path = root / args.label_ledger
    suggester_path = root / args.suggester_json
    target_ledger_path = root / args.target_ledger

    label_ledger = _read_json(label_ledger_path)
    suggester = _read_json(suggester_path)
    target_ledger = _read_json(target_ledger_path)
    targets = _target_map(target_ledger)
    records = _extra_rows(label_ledger, suggester, targets)

    payload = build_payload(
        root=root,
        label_ledger_path=label_ledger_path,
        suggester_path=suggester_path,
        target_ledger_path=target_ledger_path,
        out_dir=out_dir,
        rows=records,
        page_size=args.page_size,
    )

    json_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_20260701.json"
    csv_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_20260701.csv"
    report_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_20260701_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(csv_path, records)
    write_report(report_path, payload)

    df = _load_ohlcv(_source_csv(root, args.day, args.timeframe, args.symbol))
    render_pages(df=df, rows=records, out_dir=out_dir, timeframe=args.timeframe, page_size=args.page_size)
    print(json.dumps(payload["artifacts"], ensure_ascii=False, indent=2))
    print(json.dumps({"candidate_count": len(records), "pages": payload["pages"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
