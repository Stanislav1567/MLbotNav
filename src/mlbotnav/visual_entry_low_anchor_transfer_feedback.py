from __future__ import annotations

import argparse
import csv
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from mlbotnav.visual_entry_low_anchor_suggester import _bar_width_days, _draw_candles, _load_ohlcv, _style_axis


STATUS = "LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FIXED_NO_ML_NO_OPTUNA"
RAIL_POINT = "LOW_ANCHOR_TRANSFER_USER_FEEDBACK_NO_ML_NO_OPTUNA"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rel(root: Path, path: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def _copy_sources(root: Path, out_dir: Path, paths: list[Path]) -> list[str]:
    copied: list[str] = []
    for idx, source in enumerate(paths, 1):
        if not source.exists():
            continue
        target = out_dir / f"USER_RED_FEEDBACK_SOURCE_{idx:02d}_{source.name}"
        shutil.copy2(source, target)
        copied.append(_rel(root, target))
    return copied


def _feedback_rows(candidates: list[dict[str, Any]], reject_ids: set[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in candidates:
        cid = str(item["candidate_id"])
        rejected = cid in reject_ids
        rows.append(
            {
                "candidate_id": cid,
                "signal_time_utc": item["signal_time_utc"],
                "entry_time_utc": item["entry_time_utc"],
                "entry_price_plus_5bps": item["entry_price_plus_5bps"],
                "transfer_type": item["transfer_type"],
                "transfer_score": item["transfer_score"],
                "review_label": "bad_noise" if rejected else "pending_user_visual_review",
                "review_reason": "user_crossed_out_not_suitable" if rejected else "not_crossed_out_in_current_feedback",
                "user_verdict": "reject" if rejected else "pending",
                "source_candidate_status": item.get("review_status"),
                "transfer_pass_votes": item.get("transfer_pass_votes", []),
                "transfer_risk_votes": item.get("transfer_risk_votes", []),
            }
        )
    return rows


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = [
        "candidate_id",
        "review_label",
        "review_reason",
        "user_verdict",
        "transfer_type",
        "transfer_score",
        "signal_time_utc",
        "entry_time_utc",
        "entry_price_plus_5bps",
        "transfer_pass_votes",
        "transfer_risk_votes",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            out = dict(row)
            out["transfer_pass_votes"] = ",".join(out.get("transfer_pass_votes") or [])
            out["transfer_risk_votes"] = ",".join(out.get("transfer_risk_votes") or [])
            writer.writerow({col: out.get(col) for col in columns})


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    rejected = [row["candidate_id"] for row in payload["records"] if row["review_label"] == "bad_noise"]
    pending = [row["candidate_id"] for row in payload["records"] if row["review_label"] != "bad_noise"]
    lines = [
        "# Low Anchor Transfer Review V0: user feedback",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: зафиксировать пользовательские красные перечеркивания по `T15L01..T15L22` на `SOLUSDT 1m 2026-05-15`.",
        "",
        "Это слой обратной связи, не стратегия, не scorer, не ML dataset и не Optuna.",
        "",
        "## Итог",
        "",
        f"- Всего кандидатов: `{payload['candidate_count']}`.",
        f"- Rejected по красным X: `{payload['rejected_count']}`.",
        f"- Остались pending: `{payload['pending_count']}`.",
        "",
        "Rejected:",
        "",
        "`" + "`, `".join(rejected) + "`",
        "",
        "Pending:",
        "",
        "`" + "`, `".join(pending) + "`",
        "",
        "## Граница",
        "",
        "- Красный X/перечеркивание означает `bad_noise / user_crossed_out_not_suitable`.",
        "- Неперечеркнутые кандидаты пока не являются gold и остаются `pending_user_visual_review`.",
        "- Цена входа остается execution/control, не признак выбора.",
        "- EMA не используется как active condition.",
        "- ML/export/Optuna запрещены.",
        "",
        "## Артефакты",
        "",
        f"- Feedback full-day PNG: `{payload['artifacts']['feedback_full_day_png']}`.",
        f"- JSON: `{payload['artifacts']['json']}`.",
        f"- CSV: `{payload['artifacts']['csv']}`.",
    ]
    for source in payload["artifacts"]["source_feedback_pngs"]:
        lines.append(f"- Source screenshot: `{source}`.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _render_feedback_full_day(
    *,
    root: Path,
    payload: dict[str, Any],
    transfer: dict[str, Any],
    rows: list[dict[str, Any]],
    out_path: Path,
) -> None:
    source = root / str(transfer["source_csv"])
    df = _load_ohlcv(source)
    symbol = str(transfer["symbol"])
    timeframe = str(transfer["timeframe"])
    day = str(transfer["day_utc"])
    by_id = {str(item["candidate_id"]): item for item in transfer["candidates"]}

    fig, (ax_price, ax_vol) = plt.subplots(2, 1, figsize=(28, 12), sharex=True, gridspec_kw={"height_ratios": [4.4, 1.15]})
    fig.patch.set_facecolor("#101418")
    _style_axis(ax_price)
    _style_axis(ax_vol)
    _draw_candles(ax_price, df, timeframe, linewidth=0.34)
    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(df["open"], df["close"])]
    ax_vol.bar(df["open_time_utc"].dt.tz_convert(None), df["volume"], width=_bar_width_days(timeframe), color=colors, alpha=0.72)

    for row in rows:
        item = by_id[row["candidate_id"]]
        entry_time = pd.Timestamp(item["entry_time_utc"]).tz_convert(None)
        anchor_time = pd.Timestamp(item["anchor_time_utc"]).tz_convert(None)
        anchor_low = float(item["anchor_low_price"])
        entry_price = float(item["entry_price_plus_5bps"])
        rejected = row["review_label"] == "bad_noise"
        if rejected:
            ax_price.scatter([entry_time], [entry_price], marker="x", s=130, color="#ff1744", linewidths=2.2, zorder=8)
            ax_price.axvline(entry_time, color="#ff1744", alpha=0.18, linewidth=1.2, zorder=0)
            label_color = "#ff5252"
        else:
            ax_price.scatter([entry_time], [entry_price], marker="^", s=62, color="#26c6da", edgecolors="white", linewidths=0.45, zorder=6)
            label_color = "#26c6da"
        ax_price.scatter([anchor_time], [anchor_low], s=18, color="#ff5252", alpha=0.78, zorder=5)
        ax_price.annotate(
            row["candidate_id"],
            xy=(entry_time, entry_price),
            xytext=(2, 8),
            textcoords="offset points",
            color=label_color,
            fontsize=8,
        )

    start = pd.Timestamp(f"{day}T00:00:00")
    end = start + pd.Timedelta(days=1)
    ax_price.set_xlim(start.to_pydatetime(), end.to_pydatetime())
    ax_price.set_title(
        f"{symbol} {timeframe} {day} | T15 feedback fixed | red X=rejected | cyan=pending | NO ML/OPTUNA",
        color="white",
        fontsize=16,
    )
    ax_price.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    ax_vol.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 3)))
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path, dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)


def build_feedback(
    *,
    transfer_json: Path,
    out_dir: Path,
    reject_ids: list[str],
    source_feedback_pngs: list[Path],
) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    transfer_json = transfer_json if transfer_json.is_absolute() else root / transfer_json
    transfer = _read_json(transfer_json)
    reject_set = {str(item).strip() for item in reject_ids if str(item).strip()}
    rows = _feedback_rows(transfer["candidates"], reject_set)

    stamp = str(transfer["day_utc"]).replace("-", "")
    json_path = out_dir / f"LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_{stamp}.json"
    csv_path = out_dir / f"LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_{stamp}.csv"
    report_path = out_dir / f"LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_{stamp}_RU.md"
    feedback_png = out_dir / f"LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_FULL_DAY_{stamp}.png"
    copied_sources = _copy_sources(root, out_dir, source_feedback_pngs)

    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "rail_point": RAIL_POINT,
        "source_transfer_json": _rel(root, transfer_json),
        "source_day_utc": transfer["day_utc"],
        "symbol": transfer["symbol"],
        "timeframe": transfer["timeframe"],
        "candidate_count": len(rows),
        "rejected_count": sum(1 for row in rows if row["review_label"] == "bad_noise"),
        "pending_count": sum(1 for row in rows if row["review_label"] != "bad_noise"),
        "rejected_ids": [row["candidate_id"] for row in rows if row["review_label"] == "bad_noise"],
        "pending_ids": [row["candidate_id"] for row in rows if row["review_label"] != "bad_noise"],
        "records": rows,
        "no_lookahead_boundary": {
            "visual_feedback_only": True,
            "entry_open_price_is_execution_price_only": True,
            "ema_active_condition": False,
            "optuna_allowed": False,
            "ml_allowed": False,
        },
        "artifacts": {
            "json": _rel(root, json_path),
            "csv": _rel(root, csv_path),
            "report_ru": _rel(root, report_path),
            "feedback_full_day_png": _rel(root, feedback_png),
            "source_feedback_pngs": copied_sources,
        },
        "optuna_allowed": False,
        "ml_allowed": False,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_csv(csv_path, rows)
    _write_report(report_path, payload)
    _render_feedback_full_day(root=root, payload=payload, transfer=transfer, rows=rows, out_path=feedback_png)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Fix user feedback for low-anchor transfer review.")
    parser.add_argument(
        "--transfer-json",
        default="reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_20260515.json",
    )
    parser.add_argument("--reject-ids", nargs="+", required=True)
    parser.add_argument("--source-feedback-png", action="append", default=[])
    parser.add_argument(
        "--out-dir",
        default="reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515_compact_v0/user_feedback_v0",
    )
    args = parser.parse_args()
    payload = build_feedback(
        transfer_json=Path(args.transfer_json),
        out_dir=Path(args.out_dir),
        reject_ids=list(args.reject_ids),
        source_feedback_pngs=[Path(item) for item in args.source_feedback_png],
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "candidate_count": payload["candidate_count"],
                "rejected_count": payload["rejected_count"],
                "pending_count": payload["pending_count"],
                "rejected_ids": payload["rejected_ids"],
                "artifacts": payload["artifacts"],
                "ml_allowed": payload["ml_allowed"],
                "optuna_allowed": payload["optuna_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
