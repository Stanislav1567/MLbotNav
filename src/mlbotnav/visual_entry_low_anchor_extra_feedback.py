from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from mlbotnav.visual_entry_low_anchor_suggester import _draw_candles, _load_ohlcv, _source_csv, _style_axis


STATUS = "LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE01_FEEDBACK_FIXED_NO_ML_NO_OPTUNA"
DEFAULT_REASON = "bad_noise_shallow_bounce"
DEFAULT_LABEL = "bad_noise"
DEFAULT_POSSIBLE_REASON = "possible_entry_one_percent_followthrough"
POSSIBLE_LABEL = "possible_entry"
DEFAULT_SHIFT_REASON = "auto_entry_not_gold_manual_shift_review"
SHIFT_LABEL = "manual_shift_review"


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


def _feedback_records(
    review: dict[str, Any],
    page: int,
    reason: str,
    possible_ids: set[str],
    possible_reason: str,
    shift_ids: set[str],
    shift_reason: str,
) -> list[dict[str, Any]]:
    page_size = int(review["page_size"])
    start = (page - 1) * page_size
    end = start + page_size
    rows: list[dict[str, Any]] = []
    for item in review["records"][start:end]:
        candidate_id = str(item["candidate_id"])
        is_possible = candidate_id in possible_ids
        is_shift = candidate_id in shift_ids
        if is_possible:
            review_label = POSSIBLE_LABEL
            review_reason = possible_reason
            user_verdict = "keep_for_review"
        elif is_shift:
            review_label = SHIFT_LABEL
            review_reason = shift_reason
            user_verdict = "current_auto_not_gold"
        else:
            review_label = DEFAULT_LABEL
            review_reason = reason
            user_verdict = "reject"
        rows.append(
            {
                "candidate_id": candidate_id,
                "page": page,
                "review_label": review_label,
                "review_reason": review_reason,
                "user_verdict": user_verdict,
                "signal_time_utc": item["signal_time_utc"],
                "entry_time_utc": item["entry_time_utc"],
                "entry_open_price": item["entry_open_price"],
                "entry_price_plus_5bps": item["entry_price_plus_5bps"],
                "anchor_time_utc": item["anchor_time_utc"],
                "anchor_low_price": item["anchor_low_price"],
                "suggested_type": item["suggested_type"],
                "score": item["score"],
                "nearest_manual_target": item["nearest_manual_target"],
                "signal_diff_minutes_to_nearest_target": item["signal_diff_minutes_to_nearest_target"],
                "ml_use_allowed_now": False,
            }
        )
    return rows


def _status_for_page(page: int) -> str:
    return f"LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE{page:02d}_FEEDBACK_FIXED_NO_ML_NO_OPTUNA"


def _prefix_for_page(page: int) -> str:
    return f"LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE{page:02d}_FEEDBACK_20260701"


def _clean_phrase(*, reason: str, possible_ids: set[str]) -> str:
    return _clean_phrase_extended(reason=reason, possible_ids=possible_ids, shift_ids=set())


def _clean_phrase_extended(*, reason: str, possible_ids: set[str], shift_ids: set[str]) -> str:
    if shift_ids:
        return (
            "Пользователь красными X и стрелками показал, что текущие auto-entry на странице не являются готовыми точками входа. "
            "Рядом могут быть более удобные ручные свечи/low, но их нужно выносить в отдельный zoom-review и не переписывать автоматически."
        )
    if possible_ids:
        return (
            "Красным выделены кандидаты, с которыми можно работать: там есть вход и потенциальное движение около одного процента. "
            "Остальные кандидаты на странице формально имеют вход, но визуально не выглядят сделками, в которые стоит заходить."
        )
    if reason == "bad_noise_weak_context":
        return (
            "Все входы на странице слабые: локальный low есть, но контекст не дает уверенного рабочего движения. "
            "Такие входы визуально не похожи на сделки, в которые стоит заходить."
        )
    if reason == "bad_noise_weak_context_entry_mismatch":
        return (
            "Все входы на странице слабые и плохие для работы. В части мест авто-стрелка входа не совпадает с тем low/свечой, "
            "где визуально вообще можно было бы рассматривать вход, поэтому текущие auto-entry rejected."
        )
    if reason == "bad_noise_countertrend_entry":
        return (
            "Все входы на странице плохие: они не идут по рабочему тренду/направлению движения. "
            "Такие countertrend-входы не подходят для нашей системы."
        )
    return (
        "Эти входы не подходят: это мелкие локальные low без нормального продолжения. "
        "После входа цена дает короткий отскок или уходит в шум/стоп, часто без нужного трендового контекста. "
        "Для нашей системы это anti-example, а не рабочий вход."
    )


def _interpretation(*, reason: str, possible_ids: set[str]) -> list[str]:
    return _interpretation_extended(reason=reason, possible_ids=possible_ids, shift_ids=set())


def _interpretation_extended(*, reason: str, possible_ids: set[str], shift_ids: set[str]) -> list[str]:
    lines = [
        "Сам факт локального low недостаточен для входа.",
        "Нужен low с контекстом, где после reclaim есть пространство и сила движения.",
    ]
    if shift_ids:
        lines.extend(
            [
                "Текущие auto-entry не считаются gold и не переводятся в possible_entry.",
                "Красные ручные места требуют отдельной точной фиксации времени/цены на zoom-графике.",
                "До такой фиксации эти строки остаются manual_shift_review, не обучающая метка.",
            ]
        )
    elif possible_ids:
        lines.extend(
            [
                "Невыделенные кандидаты помечаются как bad_noise_shallow_bounce, чтобы будущий датасет не учил модель брать короткий шумовой отскок.",
                "Выделенные кандидаты остаются possible_entry и требуют отдельного сравнения с ручными good-входами.",
            ]
        )
    elif reason == "bad_noise_weak_context":
        lines.append("Все кандидаты страницы rejected как слабый контекст: вход формально есть, но рабочая структура неубедительная.")
    elif reason == "bad_noise_weak_context_entry_mismatch":
        lines.extend(
            [
                "Все кандидаты страницы rejected: контекст слабый, а часть auto-entry не совпадает с визуально нужной low/entry-зоной.",
                "Это не manual_shift_review, потому что пользователь назвал входы слабыми и плохими, а не рабочими для переноса.",
            ]
        )
    elif reason == "bad_noise_countertrend_entry":
        lines.extend(
            [
                "Все кандидаты страницы rejected: входы не поддержаны рабочим направлением движения.",
                "Причина отделена от weak_context и entry_mismatch: здесь главный reject-смысл именно countertrend.",
            ]
        )
    else:
        lines.append("Кандидаты помечаются как bad_noise_shallow_bounce, чтобы будущий датасет не учил модель брать короткий шумовой отскок.")
    lines.append("Причины основаны на ручном визуальном verdict и не являются правилом выбора входа без no-lookahead признаков.")
    return lines


def build_payload(
    *,
    root: Path,
    review_path: Path,
    out_dir: Path,
    rows: list[dict[str, Any]],
    page: int,
    reason: str,
    possible_reason: str,
    possible_ids: set[str],
    shift_reason: str,
    shift_ids: set[str],
    source_feedback_png: Path | None = None,
) -> dict[str, Any]:
    prefix = _prefix_for_page(page)
    label_counts: dict[str, int] = {}
    reason_counts: dict[str, int] = {}
    for row in rows:
        label_counts[str(row["review_label"])] = label_counts.get(str(row["review_label"]), 0) + 1
        reason_counts[str(row["review_reason"])] = reason_counts.get(str(row["review_reason"]), 0) + 1
    return {
        "schema_version": 1,
        "status": _status_for_page(page),
        "created_utc": _utc_now(),
        "rail_point": f"LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_PAGE{page:02d}_ANTI_REVIEW_NO_ML_NO_OPTUNA",
        "source_extra_review_json": str(review_path.relative_to(root)).replace("\\", "/"),
        "page": page,
        "candidate_count": len(rows),
        "candidate_ids": [row["candidate_id"] for row in rows],
        "possible_candidate_ids": sorted(possible_ids),
        "manual_shift_candidate_ids": sorted(shift_ids),
        "label_counts": label_counts,
        "reason_counts": reason_counts,
        "default_reject_label": DEFAULT_LABEL,
        "default_reject_reason": reason,
        "possible_label": POSSIBLE_LABEL,
        "possible_reason": possible_reason,
        "manual_shift_label": SHIFT_LABEL,
        "manual_shift_reason": shift_reason,
        "source_feedback_png": str(source_feedback_png.relative_to(root)).replace("\\", "/") if source_feedback_png else None,
        "user_phrase_clean_ru": _clean_phrase_extended(reason=reason, possible_ids=possible_ids, shift_ids=shift_ids),
        "interpretation_ru": _interpretation_extended(reason=reason, possible_ids=possible_ids, shift_ids=shift_ids),
        "future_feature_ideas_ru": [
            "дистанция до ближайшего сопротивления до входа",
            "структурный тренд до сигнала",
            "сила reclaim до entry",
            "наличие сжатия/шума перед входом",
            "расположение входа относительно локального диапазона",
        ],
        "records": rows,
        "artifacts": {
            "json": str((out_dir / f"{prefix}.json").relative_to(root)).replace("\\", "/"),
            "csv": str((out_dir / f"{prefix}.csv").relative_to(root)).replace("\\", "/"),
            "report_ru": str((out_dir / f"{prefix}_RU.md").relative_to(root)).replace("\\", "/"),
            "png": str((out_dir / f"{prefix}.png").relative_to(root)).replace("\\", "/"),
        },
        "optuna_allowed": False,
        "ml_allowed": False,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = [
        "candidate_id",
        "page",
        "review_label",
        "review_reason",
        "user_verdict",
        "signal_time_utc",
        "entry_time_utc",
        "entry_open_price",
        "entry_price_plus_5bps",
        "suggested_type",
        "nearest_manual_target",
        "signal_diff_minutes_to_nearest_target",
        "ml_use_allowed_now",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col) for col in columns})


def write_report(path: Path, payload: dict[str, Any]) -> None:
    rows = payload["records"]
    lines = [
        f"# Low Anchor Extra Auto Page {int(payload['page']):02d} Feedback",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        f"Страница: `{payload['page']}`.",
        f"Кандидатов: `{payload['candidate_count']}`.",
        f"Метки: `{payload['label_counts']}`.",
        f"Причины: `{payload['reason_counts']}`.",
        "",
        "## Чистая формулировка пользователя",
        "",
        payload["user_phrase_clean_ru"],
        "",
        "## Смысл для рельсов",
        "",
    ]
    for item in payload["interpretation_ru"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Кандидаты",
            "",
            "| candidate | signal UTC | entry UTC | price + 5 bps | type | nearest manual | label | verdict |",
            "|---|---:|---:|---:|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            "| "
            f"`{row['candidate_id']}` | "
            f"`{_fmt_minute(row['signal_time_utc'])}` | "
            f"`{_fmt_minute(row['entry_time_utc'])}` | "
            f"`{float(row['entry_price_plus_5bps']):.5f}` | "
            f"`{row['suggested_type']}` | "
            f"`{row['nearest_manual_target']}` | "
            f"`{row['review_label']}` | "
            f"`{row['review_reason']}` |"
        )
    lines.extend(
        [
            "",
            "## Граница",
            "",
            "- Это manual feedback layer, не ML dataset.",
            "- Optuna, ML/export/promotion не запускались.",
            "- Для будущего обучения эту причину нужно переводить в признаки, видимые до entry.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_feedback_png(*, df: pd.DataFrame, rows: list[dict[str, Any]], out_path: Path, page: int) -> None:
    fig, axes = plt.subplots(4, 3, figsize=(24, 19.2), sharex=False)
    fig.patch.set_facecolor("#101418")
    flat = list(axes.flatten())
    for ax, item in zip(flat, rows):
        _style_axis(ax)
        signal = pd.Timestamp(item["signal_time_utc"])
        start = signal - pd.Timedelta(minutes=20)
        end = signal + pd.Timedelta(minutes=32)
        win = df[(df["open_time_utc"] >= start) & (df["open_time_utc"] <= end)].reset_index(drop=True)
        _draw_candles(ax, win, "1m", linewidth=0.58)

        signal_naive = signal.tz_convert(None)
        entry = pd.Timestamp(item["entry_time_utc"]).tz_convert(None)
        anchor = pd.Timestamp(item["anchor_time_utc"]).tz_convert(None)
        anchor_low = float(item["anchor_low_price"])
        entry_price = float(item["entry_price_plus_5bps"])

        is_possible = item["review_label"] == POSSIBLE_LABEL
        is_shift = item["review_label"] == SHIFT_LABEL
        if is_possible:
            color = "#00e676"
            text_color = "#69f0ae"
            face_color = "#0b2f1f"
            marker = "^"
            verdict = "POSSIBLE"
        elif is_shift:
            color = "#ffb300"
            text_color = "#ffe082"
            face_color = "#332509"
            marker = "x"
            verdict = "SHIFT REVIEW"
        else:
            color = "#ff5252"
            text_color = "#ff8a80"
            face_color = "#341214"
            marker = "x"
            verdict = "REJECT"

        ax.axvline(signal_naive, color=color, linewidth=1.4, alpha=0.85, zorder=0)
        ax.axvline(entry, color=color, linewidth=1.0, alpha=0.65, linestyle="--", zorder=0)
        ax.scatter([anchor], [anchor_low], s=62, color="#ff5252", edgecolors="#0b0f12", linewidths=0.7, zorder=6)
        ax.scatter([entry], [entry_price], marker=marker, s=120, color=color, linewidths=1.8, zorder=8)
        ax.annotate(
            f"{item['candidate_id']} {verdict}\n{item['review_reason']}\nentry {_fmt_minute(item['entry_time_utc'])} price+5bps {entry_price:.5f}",
            xy=(entry, entry_price),
            xytext=(8, 18),
            textcoords="offset points",
            color=text_color,
            fontsize=8,
            arrowprops={"arrowstyle": "->", "color": color, "linewidth": 0.9},
            bbox={"facecolor": face_color, "edgecolor": color, "alpha": 0.76, "boxstyle": "round,pad=0.2"},
        )
        title = f"{item['candidate_id']} {item['suggested_type']} | {item['review_reason']}"
        ax.set_title(title, color="white", fontsize=9)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.tick_params(axis="x", labelrotation=20)

    for ax in flat[len(rows) :]:
        ax.axis("off")
        ax.set_facecolor("#101418")

    labels = {str(item["review_label"]) for item in rows}
    if labels == {SHIFT_LABEL}:
        verdict_summary = "current auto entries not gold, manual shift review"
    elif labels == {DEFAULT_LABEL}:
        verdict_summary = "all rejected"
    elif POSSIBLE_LABEL in labels:
        verdict_summary = "possible entries kept, others rejected"
    else:
        verdict_summary = "mixed manual feedback"
    fig.suptitle(
        f"LOW_ANCHOR V1 page {page:02d} user feedback | {verdict_summary} | NO ML/OPTUNA",
        color="white",
        fontsize=15,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fix user feedback for extra auto review page 01.")
    parser.add_argument("--day", default="2026-05-14")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--reason", default=DEFAULT_REASON)
    parser.add_argument("--possible-reason", default=DEFAULT_POSSIBLE_REASON)
    parser.add_argument("--possible-ids", nargs="*", default=[])
    parser.add_argument("--manual-shift-reason", default=DEFAULT_SHIFT_REASON)
    parser.add_argument("--manual-shift-ids", nargs="*", default=[])
    parser.add_argument("--source-feedback-png", default=None)
    parser.add_argument(
        "--extra-review-json",
        default="reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/extra_auto_review_v1/LOW_ANCHOR_ENTRY_SUGGESTER_V1_EXTRA_AUTO_REVIEW_20260701.json",
    )
    parser.add_argument(
        "--out-dir",
        default=None,
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    review_path = root / args.extra_review_json
    default_out_dir = (
        "reports/final_review/visual_entry_v3/fresh_target_led/"
        f"low_anchor_entry_suggester_v0/extra_auto_review_v1/user_feedback_page{args.page:02d}_v0"
    )
    out_dir = root / (args.out_dir or default_out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    review = _read_json(review_path)
    possible_ids = {str(item) for item in args.possible_ids}
    shift_ids = {str(item) for item in args.manual_shift_ids}
    records = _feedback_records(
        review,
        args.page,
        args.reason,
        possible_ids,
        args.possible_reason,
        shift_ids,
        args.manual_shift_reason,
    )
    copied_source: Path | None = None
    if args.source_feedback_png:
        source_path = Path(args.source_feedback_png)
        if source_path.exists():
            copied_source = out_dir / f"USER_RED_FEEDBACK_SOURCE_PAGE{args.page:02d}_20260701.png"
            copied_source.write_bytes(source_path.read_bytes())
    payload = build_payload(
        root=root,
        review_path=review_path,
        out_dir=out_dir,
        rows=records,
        page=args.page,
        reason=args.reason,
        possible_reason=args.possible_reason,
        possible_ids=possible_ids,
        shift_reason=args.manual_shift_reason,
        shift_ids=shift_ids,
        source_feedback_png=copied_source,
    )

    prefix = _prefix_for_page(args.page)
    json_path = out_dir / f"{prefix}.json"
    csv_path = out_dir / f"{prefix}.csv"
    report_path = out_dir / f"{prefix}_RU.md"
    png_path = out_dir / f"{prefix}.png"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(csv_path, records)
    write_report(report_path, payload)

    df = _load_ohlcv(_source_csv(root, args.day, args.timeframe, args.symbol))
    render_feedback_png(df=df, rows=records, out_path=png_path, page=args.page)

    print(json.dumps(payload["artifacts"], ensure_ascii=False, indent=2))
    print(json.dumps({"candidate_count": len(records), "review_reason": args.reason}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
