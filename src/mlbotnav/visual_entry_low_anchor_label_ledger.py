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


STATUS = "LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_READY_NO_ML_NO_OPTUNA"
STATUS_RESOLVED = "LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_RESOLVED_BY_USER_NO_ML_NO_OPTUNA"


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


def _records_by_target(feedback: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["target_id"]): item for item in feedback.get("records", [])}


def _targets_by_id(ledger: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["target_id"]): item for item in ledger.get("targets", [])}


def _candidates_by_id(suggester: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["candidate_id"]): item for item in suggester.get("candidates", [])}


def _match_rows(suggester: dict[str, Any]) -> list[dict[str, Any]]:
    return list(suggester.get("target_match_summary", {}).get("per_target", []))


def build_payload(
    *,
    root: Path,
    ledger_path: Path,
    suggester_path: Path,
    feedback_path: Path,
    out_dir: Path,
    ledger_version: str,
    accept_pending_as_user_ok: bool,
) -> dict[str, Any]:
    ledger = _read_json(ledger_path)
    suggester = _read_json(suggester_path)
    feedback = _read_json(feedback_path)
    targets = _targets_by_id(ledger)
    candidates = _candidates_by_id(suggester)
    feedback_by_target = _records_by_target(feedback)

    target_records: list[dict[str, Any]] = []
    candidate_labels: dict[str, str] = {}

    for match in _match_rows(suggester):
        target_id = str(match["target_id"])
        target = targets[target_id]
        candidate_id = str(match["nearest_candidate_id"])
        candidate = candidates[candidate_id]
        diff = int(match["diff_minutes"])

        if target_id in feedback_by_target:
            label_status = "manual_gold_user_feedback_auto_not_gold"
            review_status = "confirmed_user_feedback"
            user_verdict = feedback_by_target[target_id]["user_verdict"]
            candidate_labels[candidate_id] = "auto_near_not_gold_user_feedback"
        elif diff == 0:
            label_status = "manual_gold_exact_auto"
            review_status = "exact_auto_ok"
            user_verdict = "EXACT_AUTO_MATCH"
            candidate_labels[candidate_id] = "positive_auto_exact_to_manual"
        elif abs(diff) <= 3 and accept_pending_as_user_ok:
            label_status = "manual_gold_user_confirmed_auto_near_ok"
            review_status = "confirmed_user_near_ok"
            user_verdict = "USER_CONFIRMED_PENDING_REVIEW_OK"
            candidate_labels[candidate_id] = "positive_auto_near_user_confirmed"
        elif abs(diff) <= 3:
            label_status = "manual_gold_pending_shift_review"
            review_status = "pending_user_review"
            user_verdict = "PENDING_SHIFT_REVIEW"
            candidate_labels[candidate_id] = "auto_near_pending_review"
        else:
            label_status = "manual_gold_auto_far"
            review_status = "needs_investigation"
            user_verdict = "AUTO_FAR_FROM_MANUAL"
            candidate_labels[candidate_id] = "auto_far_from_manual"

        target_records.append(
            {
                "target_id": target_id,
                "target_type": target.get("target_type"),
                "manual_signal_time_utc": target["signal_time_utc"],
                "manual_entry_time_utc": target["entry_time_utc"],
                "manual_entry_open_price": target.get("execution_price", {}).get("entry_open_price"),
                "manual_entry_price_with_slippage": target.get("execution_price", {}).get("entry_price_with_slippage"),
                "nearest_auto_candidate_id": candidate_id,
                "auto_anchor_time_utc": candidate["anchor_time_utc"],
                "auto_anchor_low_price": candidate["anchor_low_price"],
                "auto_signal_time_utc": candidate["signal_time_utc"],
                "auto_entry_time_utc": candidate["entry_time_utc"],
                "auto_entry_open_price": candidate["entry_open_price"],
                "auto_entry_price_with_slippage": candidate["entry_price_plus_5bps"],
                "signal_diff_minutes_auto_minus_manual": diff,
                "label_status": label_status,
                "review_status": review_status,
                "user_verdict": user_verdict,
            }
        )

    candidate_records: list[dict[str, Any]] = []
    nearest_candidate_ids = {item["nearest_auto_candidate_id"] for item in target_records}
    for candidate in suggester.get("candidates", []):
        cid = str(candidate["candidate_id"])
        if cid in candidate_labels:
            label = candidate_labels[cid]
        elif cid in nearest_candidate_ids:
            label = "auto_nearest_needs_manual_context"
        else:
            label = "extra_auto_unlabeled_candidate"
        candidate_records.append(
            {
                "candidate_id": cid,
                "candidate_label": label,
                "signal_time_utc": candidate["signal_time_utc"],
                "entry_time_utc": candidate["entry_time_utc"],
                "nearest_manual_target": candidate.get("nearest_manual_target"),
                "signal_diff_minutes_to_nearest_target": candidate.get("signal_diff_minutes_to_nearest_target"),
                "score": candidate.get("score"),
                "suggested_type": candidate.get("suggested_type"),
            }
        )

    counts: dict[str, int] = {}
    for item in target_records:
        counts[item["label_status"]] = counts.get(item["label_status"], 0) + 1
    candidate_counts: dict[str, int] = {}
    for item in candidate_records:
        candidate_counts[item["candidate_label"]] = candidate_counts.get(item["candidate_label"], 0) + 1

    return {
        "schema_version": 1,
        "status": STATUS_RESOLVED if accept_pending_as_user_ok else STATUS,
        "created_utc": _utc_now(),
        "rail_point": (
            "LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_RESOLVED_NO_ML_NO_OPTUNA"
            if accept_pending_as_user_ok
            else "LOW_ANCHOR_ENTRY_SUGGESTER_V0_LABEL_LEDGER_NO_ML_NO_OPTUNA"
        ),
        "symbol": ledger.get("symbol"),
        "timeframe": ledger.get("timeframe"),
        "day_utc": ledger.get("day_utc"),
        "source_target_ledger": str(ledger_path.relative_to(root)).replace("\\", "/"),
        "source_suggester_json": str(suggester_path.relative_to(root)).replace("\\", "/"),
        "source_user_feedback_json": str(feedback_path.relative_to(root)).replace("\\", "/"),
        "target_label_counts": counts,
        "candidate_label_counts": candidate_counts,
        "target_records": target_records,
        "candidate_records": candidate_records,
        "pending_shift_review_targets": [
            item["target_id"] for item in target_records if item["label_status"] == "manual_gold_pending_shift_review"
        ],
        "user_confirmed_near_ok_targets": [
            item["target_id"] for item in target_records if item["label_status"] == "manual_gold_user_confirmed_auto_near_ok"
        ],
        "rule_implications_ru": [
            "Ручной target-led ledger остается источником positive labels.",
            "Exact auto match можно считать совпадением с ручным эталоном.",
            "User-confirmed near auto match можно считать разрешенным visual-near попаданием, но ручной signal/entry ledger не переписывается.",
            "User-feedback near-candidate нельзя считать gold, даже если он в пределах +/-3m.",
            "Pending shift review нельзя передавать в ML как positive или negative до ручного решения.",
            "Extra auto candidates пока только unlabeled pool для будущего anti-review, не готовые negative labels.",
        ],
        "no_lookahead_boundary": {
            "labeling_only": True,
            "optuna_allowed": False,
            "ml_allowed": False,
            "forbidden_for_selection": ["future_return", "tp_sl", "mfe_mae", "entry_candle_ohlcv"],
        },
        "artifacts": {
            "json": str((out_dir / f"LOW_ANCHOR_ENTRY_SUGGESTER_{ledger_version}_LABEL_LEDGER_20260701.json").relative_to(root)).replace("\\", "/"),
            "csv_targets": str((out_dir / f"LOW_ANCHOR_ENTRY_SUGGESTER_{ledger_version}_LABEL_LEDGER_TARGETS_20260701.csv").relative_to(root)).replace("\\", "/"),
            "csv_candidates": str((out_dir / f"LOW_ANCHOR_ENTRY_SUGGESTER_{ledger_version}_LABEL_LEDGER_CANDIDATES_20260701.csv").relative_to(root)).replace("\\", "/"),
            "report_ru": str((out_dir / f"LOW_ANCHOR_ENTRY_SUGGESTER_{ledger_version}_LABEL_LEDGER_20260701_RU.md").relative_to(root)).replace("\\", "/"),
            "pending_review_png": str((out_dir / f"LOW_ANCHOR_ENTRY_SUGGESTER_{ledger_version}_PENDING_SHIFT_REVIEW_20260701.png").relative_to(root)).replace("\\", "/"),
            "pending_review_svg": str((out_dir / f"LOW_ANCHOR_ENTRY_SUGGESTER_{ledger_version}_PENDING_SHIFT_REVIEW_20260701.svg").relative_to(root)).replace("\\", "/"),
        },
        "optuna_allowed": False,
        "ml_allowed": False,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Low Anchor Suggester V0: label ledger",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: разложить V0-кандидаты на рабочие label-классы до любых scorer/Optuna/ML действий.",
        "",
        "## Target label counts",
        "",
    ]
    for key, value in sorted(payload["target_label_counts"].items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Candidate label counts", ""])
    for key, value in sorted(payload["candidate_label_counts"].items()):
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Pending shift review",
            "",
            f"Оставшиеся цели для проверки глазами: `{', '.join(payload['pending_shift_review_targets']) or 'нет'}`.",
            f"Подтвержденные пользователем near-ok цели: `{', '.join(payload.get('user_confirmed_near_ok_targets', [])) or 'нет'}`.",
            "",
            "| target | type | manual signal -> entry | auto | auto signal -> entry | diff | label |",
            "|---|---|---|---|---|---:|---|",
        ]
    )
    for item in payload["target_records"]:
        lines.append(
            "| {target_id} | {target_type} | {ms} -> {me} | {cid} | {asig} -> {aent} | {diff:+}m | `{label}` |".format(
                target_id=item["target_id"],
                target_type=item["target_type"],
                ms=_fmt_minute(item["manual_signal_time_utc"]),
                me=_fmt_minute(item["manual_entry_time_utc"]),
                cid=item["nearest_auto_candidate_id"],
                asig=_fmt_minute(item["auto_signal_time_utc"]),
                aent=_fmt_minute(item["auto_entry_time_utc"]),
                diff=int(item["signal_diff_minutes_auto_minus_manual"]),
                label=item["label_status"],
            )
        )
    lines.extend(
        [
            "",
            "## Границы",
            "",
            "- Это label-ledger, не стратегия.",
            "- `pending_shift_review` нельзя считать positive/negative до ручного решения.",
            "- `extra_auto_unlabeled_candidate` не является плохим входом автоматически.",
            "- Scorer, Optuna, ML/export/promotion не запускались.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_pending_review_sheet(
    *,
    df: pd.DataFrame,
    payload: dict[str, Any],
    out_png: Path,
    out_svg: Path,
    timeframe: str,
) -> None:
    records = [item for item in payload["target_records"] if item["label_status"] == "manual_gold_pending_shift_review"]
    if not records:
        fig, ax = plt.subplots(figsize=(10, 4))
        fig.patch.set_facecolor("#101418")
        ax.set_facecolor("#101418")
        ax.text(0.5, 0.5, "No pending shift review targets", color="white", ha="center", va="center", fontsize=16)
        ax.axis("off")
        fig.savefig(out_png, dpi=160, facecolor=fig.get_facecolor())
        fig.savefig(out_svg, facecolor=fig.get_facecolor())
        plt.close(fig)
        return

    cols = 2
    rows = ceil(len(records) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(22, 5.5 * rows), sharex=False)
    fig.patch.set_facecolor("#101418")
    flat = list(axes.flatten() if hasattr(axes, "flatten") else [axes])

    for ax, item in zip(flat, records):
        _style_axis(ax)
        manual_signal = pd.Timestamp(item["manual_signal_time_utc"])
        auto_signal = pd.Timestamp(item["auto_signal_time_utc"])
        center = min(manual_signal, auto_signal) + (max(manual_signal, auto_signal) - min(manual_signal, auto_signal)) / 2
        start = center - pd.Timedelta(minutes=22)
        end = center + pd.Timedelta(minutes=34)
        win = df[(df["open_time_utc"] >= start) & (df["open_time_utc"] <= end)].reset_index(drop=True)
        _draw_candles(ax, win, timeframe, linewidth=0.62)

        manual_entry = pd.Timestamp(item["manual_entry_time_utc"]).tz_convert(None)
        auto_entry = pd.Timestamp(item["auto_entry_time_utc"]).tz_convert(None)
        manual_signal_naive = manual_signal.tz_convert(None)
        auto_signal_naive = auto_signal.tz_convert(None)
        anchor_time = pd.Timestamp(item["auto_anchor_time_utc"]).tz_convert(None)

        manual_price = float(item["manual_entry_price_with_slippage"])
        auto_price = float(item["auto_entry_price_with_slippage"])
        anchor_price = float(item["auto_anchor_low_price"])

        ax.axvline(manual_signal_naive, color="#ffd54f", linewidth=2.0, alpha=0.9, zorder=0)
        ax.axvline(manual_entry, color="#00e676", linewidth=1.5, alpha=0.8, zorder=0)
        ax.axvline(auto_signal_naive, color="#26c6da", linewidth=1.3, alpha=0.75, linestyle="--", zorder=0)
        ax.scatter([manual_entry], [manual_price], marker="^", s=150, color="#00e676", edgecolors="white", linewidths=0.7, zorder=8)
        ax.scatter([auto_entry], [auto_price], marker="x", s=90, color="#26c6da", linewidths=2.0, zorder=7)
        ax.scatter([anchor_time], [anchor_price], s=75, color="#ff5252", edgecolors="#0b0f12", linewidths=0.8, zorder=6)

        ax.annotate(
            f"manual {item['target_id']} entry {_fmt_minute(item['manual_entry_time_utc'])}\nprice+5bps {manual_price:.5f}",
            xy=(manual_entry, manual_price),
            xytext=(12, 18),
            textcoords="offset points",
            color="#00e676",
            fontsize=9,
            arrowprops={"arrowstyle": "->", "color": "#00e676", "linewidth": 1.1},
            bbox={"facecolor": "#073b26", "edgecolor": "#00e676", "alpha": 0.86, "boxstyle": "round,pad=0.25"},
        )
        ax.annotate(
            f"auto {item['nearest_auto_candidate_id']} entry {_fmt_minute(item['auto_entry_time_utc'])}",
            xy=(auto_entry, auto_price),
            xytext=(10, -42),
            textcoords="offset points",
            color="#26c6da",
            fontsize=8,
            arrowprops={"arrowstyle": "->", "color": "#26c6da", "linewidth": 1.0},
            bbox={"facecolor": "#0b2730", "edgecolor": "#26c6da", "alpha": 0.72, "boxstyle": "round,pad=0.2"},
        )
        ax.set_title(
            "{target_id} {target_type} | pending review | auto diff {diff:+}m".format(
                target_id=item["target_id"],
                target_type=item["target_type"],
                diff=int(item["signal_diff_minutes_auto_minus_manual"]),
            ),
            color="white",
            fontsize=10,
        )
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.tick_params(axis="x", labelrotation=20)

    for ax in flat[len(records) :]:
        ax.axis("off")
        ax.set_facecolor("#101418")

    fig.suptitle(
        "LOW_ANCHOR V0 pending shift review | yellow=manual signal, green=manual entry, cyan=auto near-candidate | NO ML/OPTUNA",
        color="white",
        fontsize=15,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_png, dpi=170, facecolor=fig.get_facecolor())
    fig.savefig(out_svg, facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build label ledger for low-anchor V0 review.")
    parser.add_argument("--day", default="2026-05-14")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument(
        "--target-ledger",
        default="reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_M01_M19.json",
    )
    parser.add_argument(
        "--suggester-json",
        default="reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_20260514.json",
    )
    parser.add_argument(
        "--feedback-json",
        default=(
            "reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/"
            "user_feedback_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.json"
        ),
    )
    parser.add_argument(
        "--out-dir",
        default="reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/label_ledger_v0",
    )
    parser.add_argument("--ledger-version", default="V0")
    parser.add_argument("--accept-pending-as-user-ok", action="store_true")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    out_dir = root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = build_payload(
        root=root,
        ledger_path=root / args.target_ledger,
        suggester_path=root / args.suggester_json,
        feedback_path=root / args.feedback_json,
        out_dir=out_dir,
        ledger_version=args.ledger_version,
        accept_pending_as_user_ok=bool(args.accept_pending_as_user_ok),
    )

    json_path = out_dir / f"LOW_ANCHOR_ENTRY_SUGGESTER_{args.ledger_version}_LABEL_LEDGER_20260701.json"
    targets_csv = out_dir / f"LOW_ANCHOR_ENTRY_SUGGESTER_{args.ledger_version}_LABEL_LEDGER_TARGETS_20260701.csv"
    candidates_csv = out_dir / f"LOW_ANCHOR_ENTRY_SUGGESTER_{args.ledger_version}_LABEL_LEDGER_CANDIDATES_20260701.csv"
    report_path = out_dir / f"LOW_ANCHOR_ENTRY_SUGGESTER_{args.ledger_version}_LABEL_LEDGER_20260701_RU.md"
    pending_png = out_dir / f"LOW_ANCHOR_ENTRY_SUGGESTER_{args.ledger_version}_PENDING_SHIFT_REVIEW_20260701.png"
    pending_svg = out_dir / f"LOW_ANCHOR_ENTRY_SUGGESTER_{args.ledger_version}_PENDING_SHIFT_REVIEW_20260701.svg"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(targets_csv, payload["target_records"])
    write_csv(candidates_csv, payload["candidate_records"])
    write_report(report_path, payload)

    df = _load_ohlcv(_source_csv(root, args.day, args.timeframe, args.symbol))
    render_pending_review_sheet(df=df, payload=payload, out_png=pending_png, out_svg=pending_svg, timeframe=args.timeframe)
    print(json.dumps(payload["artifacts"], ensure_ascii=False, indent=2))
    print(json.dumps(payload["target_label_counts"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
