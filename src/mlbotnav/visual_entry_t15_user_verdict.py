from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from mlbotnav.visual_entry_indicator_hypothesis_review import _rel, _utc_now
from mlbotnav.visual_entry_low_anchor_suggester import _bar_width_days, _draw_candles, _load_ohlcv, _style_axis


STATUS = "T15_USER_VERDICT_V1_ALL_SEVEN_ENTRIES_FIXED_NO_ML_NO_OPTUNA"
RAIL_POINT = "T15_USER_VERDICT_ALL_SEVEN_ENTRIES_NO_ML_NO_OPTUNA"
DAY = "2026-05-15"
CONFIRMED_ENTRY_IDS = {"T15L02", "T15L06", "T15L07", "T15L08", "T15L11", "T15L13", "T15L16"}
POSSIBLE_IDS: set[str] = set()
WEAK_NOT_PROMOTED_IDS: set[str] = set()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _status_for(row: dict[str, Any]) -> tuple[str, str, str]:
    cid = str(row["candidate_id"])
    if cid in CONFIRMED_ENTRY_IDS:
        return (
            "user_confirmed_entry",
            "user_corrected_all_seven_entries_norm",
            "entry",
        )
    if cid in POSSIBLE_IDS:
        return (
            "possible_not_primary",
            "assistant_possible_user_norm_but_not_primary",
            "possible",
        )
    if cid in WEAK_NOT_PROMOTED_IDS:
        return (
            "weak_not_promoted_after_priority_review",
            "assistant_weak_not_promoted_user_norm",
            "not_promoted",
        )
    return str(row["review_label"]), str(row["review_reason"]), str(row["user_verdict"])


def _build_records(feedback_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in feedback_payload["records"]:
        label, reason, verdict = _status_for(item)
        rows.append(
            {
                **item,
                "review_label": label,
                "review_reason": reason,
                "user_verdict": verdict,
                "source_feedback_label": item["review_label"],
                "source_feedback_reason": item["review_reason"],
            }
        )
    return rows


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = [
        "candidate_id",
        "review_label",
        "review_reason",
        "user_verdict",
        "source_feedback_label",
        "transfer_type",
        "signal_time_utc",
        "entry_time_utc",
        "entry_price_plus_5bps",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column) for column in columns})


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# T15 User Verdict V1",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: зафиксировать уточнение пользователя: на `2026-05-15` должно быть `7` входов, то есть все неперечеркнутые кандидаты из feedback v2 являются входами.",
        "",
        "Это ручной verdict-layer, не scorer, не target-lock, не ML dataset и не Optuna.",
        "",
        "## Итог",
        "",
        f"- Confirmed entries: `{', '.join(payload['confirmed_entry_ids'])}`.",
        f"- Possible not primary: `{', '.join(payload['possible_not_primary_ids']) or 'нет'}`.",
        f"- Weak not promoted: `{', '.join(payload['weak_not_promoted_ids']) or 'нет'}`.",
        f"- Rejected остаются из feedback v2: `{payload['rejected_count']}`.",
        "",
        "## Правило дальше",
        "",
        "`T15L02`, `T15L06`, `T15L07`, `T15L08`, `T15L11`, `T15L13`, `T15L16` можно использовать как ручные confirmed entries для следующего draft-ledger/passport discussion. Это еще не target-lock.",
        "",
        "ML/export/Optuna запрещены.",
        "",
        "## Артефакты",
        "",
    ]
    for value in payload["artifacts"].values():
        lines.append(f"- `{value}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _render_full_day(root: Path, transfer_payload: dict[str, Any], records: list[dict[str, Any]], out_path: Path) -> None:
    df = _load_ohlcv(root / str(transfer_payload["source_csv"]))
    fig, (ax_price, ax_vol) = plt.subplots(2, 1, figsize=(30, 13), sharex=True, gridspec_kw={"height_ratios": [4.6, 1.1]})
    fig.patch.set_facecolor("#101418")
    _style_axis(ax_price)
    _style_axis(ax_vol)
    _draw_candles(ax_price, df, "1m", linewidth=0.34)
    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(df["open"], df["close"])]
    ax_vol.bar(df["open_time_utc"].dt.tz_convert(None), df["volume"], width=_bar_width_days("1m"), color=colors, alpha=0.70)

    for row in records:
        entry = pd.Timestamp(row["entry_time_utc"]).tz_convert(None)
        signal = pd.Timestamp(row["signal_time_utc"]).tz_convert(None)
        price = float(row["entry_price_plus_5bps"])
        cid = str(row["candidate_id"])
        label = str(row["review_label"])
        if label == "user_confirmed_entry":
            color = "#00e676"
            marker = "^"
            size = 110
            alpha = 0.90
        elif label == "possible_not_primary":
            color = "#ffca28"
            marker = "o"
            size = 80
            alpha = 0.80
        elif label == "weak_not_promoted_after_priority_review":
            color = "#90a4ae"
            marker = "x"
            size = 70
            alpha = 0.62
        elif label == "bad_noise":
            color = "#ff1744"
            marker = "x"
            size = 60
            alpha = 0.38
        else:
            color = "#26c6da"
            marker = "o"
            size = 60
            alpha = 0.55

        ax_price.axvline(signal, color=color, alpha=0.12 if label == "bad_noise" else 0.22, linewidth=1.0)
        ax_price.scatter([entry], [price], marker=marker, s=size, color=color, edgecolors="white" if marker not in {"x", "o"} else None, linewidths=0.8, alpha=alpha, zorder=8)
        if label in {"user_confirmed_entry", "possible_not_primary", "weak_not_promoted_after_priority_review"}:
            ax_price.annotate(
                f"{cid} {row['user_verdict']} {pd.Timestamp(row['entry_time_utc']).strftime('%H:%M')} p={price:.4f}",
                xy=(entry, price),
                xytext=(4, 10),
                textcoords="offset points",
                color=color,
                fontsize=8,
            )

    start = pd.Timestamp(f"{DAY}T00:00:00")
    ax_price.set_xlim(start.to_pydatetime(), (start + pd.Timedelta(days=1)).to_pydatetime())
    ax_price.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    ax_vol.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 3)))
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.suptitle(
        "SOLUSDT 1m 2026-05-15 | user verdict v1 | green=7 confirmed entries | NO ML/OPTUNA",
        color="white",
        fontsize=15,
    )
    fig.savefig(out_path, dpi=170, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def run(out_dir: Path) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    feedback_path = (
        root
        / "reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/"
        "day_20260515_compact_v0/user_feedback_v2/LOW_ANCHOR_TRANSFER_REVIEW_V0_USER_FEEDBACK_20260515.json"
    )
    transfer_path = root / str(_read_json(feedback_path)["source_transfer_json"])
    feedback_payload = _read_json(feedback_path)
    transfer_payload = _read_json(transfer_path)
    records = _build_records(feedback_payload)

    png_path = out_dir / "T15_USER_VERDICT_V1_FULL_DAY_20260515.png"
    json_path = out_dir / "T15_USER_VERDICT_V1_20260701.json"
    csv_path = out_dir / "T15_USER_VERDICT_V1_20260701.csv"
    report_path = out_dir / "T15_USER_VERDICT_V1_20260701_RU.md"
    _render_full_day(root, transfer_payload, records, png_path)

    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "rail_point": RAIL_POINT,
        "source_feedback_json": _rel(root, feedback_path),
        "source_priority_zoom_json": "reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/T15_PRIORITY_ZOOM_REVIEW_V0_20260701.json",
        "day_utc": DAY,
        "confirmed_entry_ids": sorted(CONFIRMED_ENTRY_IDS),
        "gold_candidate_ids": sorted(CONFIRMED_ENTRY_IDS),
        "possible_not_primary_ids": sorted(POSSIBLE_IDS),
        "weak_not_promoted_ids": sorted(WEAK_NOT_PROMOTED_IDS),
        "rejected_count": len([row for row in records if row["review_label"] == "bad_noise"]),
        "records": records,
        "artifacts": {
            "full_day_png": _rel(root, png_path),
            "json": _rel(root, json_path),
            "csv": _rel(root, csv_path),
            "report_ru": _rel(root, report_path),
        },
        "ml_allowed": False,
        "optuna_allowed": False,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_csv(csv_path, records)
    _write_report(report_path, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Fix user verdict after T15 priority zoom review.")
    parser.add_argument(
        "--out-dir",
        default="reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/priority_zoom_review_v0/user_verdict_v1",
    )
    args = parser.parse_args()
    payload = run(Path(args.out_dir))
    print(
        json.dumps(
            {
                "status": payload["status"],
                "confirmed_entry_ids": payload["confirmed_entry_ids"],
                "possible_not_primary_ids": payload["possible_not_primary_ids"],
                "weak_not_promoted_ids": payload["weak_not_promoted_ids"],
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
