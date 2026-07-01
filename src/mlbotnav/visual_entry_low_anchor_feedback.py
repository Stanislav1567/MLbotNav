from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from mlbotnav.visual_entry_low_anchor_suggester import (
    _add_features,
    _draw_candles,
    _load_ohlcv,
    _source_csv,
    _style_axis,
)


STATUS = "LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_NO_ML_NO_OPTUNA"
DEFAULT_TARGET_IDS = ["M03", "M09", "M10", "M11"]


@dataclass(frozen=True)
class FeedbackTarget:
    target_id: str
    verdict: str
    note_ru: str


DEFAULT_FEEDBACK: dict[str, FeedbackTarget] = {
    "M03": FeedbackTarget(
        target_id="M03",
        verdict="AUTO_LATE_BY_2M_PREFER_LEDGER_SIGNAL_ENTRY",
        note_ru="Пользователь отметил, что авто-точка ушла правее нужной свечи. Предпочтение: ручной ledger.",
    ),
    "M09": FeedbackTarget(
        target_id="M09",
        verdict="AUTO_LATE_BY_2M_PREFER_LEDGER_SIGNAL_ENTRY",
        note_ru="Пользователь отметил более удобный вход левее авто-кандидата. Предпочтение: ручной ledger.",
    ),
    "M10": FeedbackTarget(
        target_id="M10",
        verdict="AUTO_EARLY_BY_1M_PREFER_LEDGER_SIGNAL_ENTRY_ANCHOR_REVIEW",
        note_ru=(
            "Авто-кандидат стоит на одну свечу раньше ручного ledger, а пользователь отметил low-anchor зону. "
            "До отдельного сдвига эталоном остается ручной ledger, auto помечается как early near-not-gold."
        ),
    ),
    "M11": FeedbackTarget(
        target_id="M11",
        verdict="AUTO_LATE_BY_2M_PREFER_LEDGER_SIGNAL_ENTRY",
        note_ru="Пользователь отметил, что авто-точка позднее нужной low-свечи. Предпочтение: ручной ledger.",
    ),
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fmt_ts(ts: pd.Timestamp) -> str:
    return ts.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def _fmt_minute(ts: pd.Timestamp | str) -> str:
    value = pd.Timestamp(ts)
    if value.tzinfo is None:
        value = value.tz_localize("UTC")
    else:
        value = value.tz_convert("UTC")
    return value.strftime("%H:%M")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _target_by_id(ledger: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["target_id"]): item for item in ledger.get("targets", [])}


def _candidate_by_id(suggester: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(item["candidate_id"]): item for item in suggester.get("candidates", [])}


def _nearest_candidate_id(suggester: dict[str, Any], target_id: str) -> str:
    for item in suggester.get("target_match_summary", {}).get("per_target", []):
        if item.get("target_id") == target_id:
            return str(item.get("nearest_candidate_id"))
    raise KeyError(f"No nearest candidate for {target_id}")


def build_feedback_payload(
    *,
    root: Path,
    ledger_path: Path,
    suggester_path: Path,
    target_ids: list[str],
    source_feedback_png: str | None,
    copied_feedback_png: Path | None,
    out_dir: Path,
) -> dict[str, Any]:
    ledger = _read_json(ledger_path)
    suggester = _read_json(suggester_path)
    targets = _target_by_id(ledger)
    candidates = _candidate_by_id(suggester)
    records: list[dict[str, Any]] = []

    for target_id in target_ids:
        target = targets[target_id]
        candidate_id = _nearest_candidate_id(suggester, target_id)
        candidate = candidates[candidate_id]
        feedback = DEFAULT_FEEDBACK[target_id]
        signal_diff = int(round((pd.Timestamp(candidate["signal_time_utc"]) - pd.Timestamp(target["signal_time_utc"])).total_seconds() / 60.0))
        entry_diff = int(round((pd.Timestamp(candidate["entry_time_utc"]) - pd.Timestamp(target["entry_time_utc"])).total_seconds() / 60.0))
        records.append(
            {
                "target_id": target_id,
                "target_type": target.get("target_type"),
                "user_verdict": feedback.verdict,
                "user_note_ru": feedback.note_ru,
                "preferred_signal_time_utc": target["signal_time_utc"],
                "preferred_entry_time_utc": target["entry_time_utc"],
                "preferred_entry_open_price": target.get("execution_price", {}).get("entry_open_price"),
                "preferred_entry_price_with_slippage": target.get("execution_price", {}).get("entry_price_with_slippage"),
                "current_auto_candidate_id": candidate_id,
                "current_auto_anchor_time_utc": candidate["anchor_time_utc"],
                "current_auto_anchor_low_price": candidate["anchor_low_price"],
                "current_auto_signal_time_utc": candidate["signal_time_utc"],
                "current_auto_entry_time_utc": candidate["entry_time_utc"],
                "current_auto_entry_open_price": candidate["entry_open_price"],
                "current_auto_entry_price_with_slippage": candidate["entry_price_plus_5bps"],
                "current_auto_score": candidate["score"],
                "current_auto_risk_flags": candidate.get("risk_flags", []),
                "signal_diff_minutes_auto_minus_preferred": signal_diff,
                "entry_diff_minutes_auto_minus_preferred": entry_diff,
                "dataset_label_recommendation": "preferred_is_positive_auto_near_is_not_gold",
            }
        )

    png_rel = None
    if copied_feedback_png is not None:
        png_rel = str(copied_feedback_png.relative_to(root)).replace("\\", "/")

    return {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "rail_point": "LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_NO_ML_NO_OPTUNA",
        "symbol": ledger.get("symbol"),
        "timeframe": ledger.get("timeframe"),
        "day_utc": ledger.get("day_utc"),
        "source_target_ledger": str(ledger_path.relative_to(root)).replace("\\", "/"),
        "source_suggester_json": str(suggester_path.relative_to(root)).replace("\\", "/"),
        "source_user_feedback_png": source_feedback_png,
        "copied_user_feedback_png": png_rel,
        "feedback_targets": target_ids,
        "records": records,
        "rule_implications_ru": [
            "Метрика hit_within_3m больше не равна gold-попаданию для обучения или lock.",
            "Exact/gold берется из ручного ledger и пользовательского визуального подтверждения.",
            "Auto-кандидат в пределах +/-3m остается near-candidate для review, но получает метку near-not-gold, если пользователь показал другую свечу.",
            "M10 оставлен как early anchor-zone-review: без отдельной ручной команды не сдвигать ledger, но auto не считать gold.",
        ],
        "no_lookahead_boundary": {
            "feedback_is_visual_review_only": True,
            "entry_rule": "LONG at next open after closed signal candle",
            "entry_open_price_is_execution_price_only": True,
            "forbidden_for_selection": ["future_return", "tp_sl", "mfe_mae", "entry_candle_ohlcv"],
        },
        "artifacts": {
            "json": str((out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.json").relative_to(root)).replace("\\", "/"),
            "report_ru": str((out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701_RU.md").relative_to(root)).replace("\\", "/"),
            "png": str((out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.png").relative_to(root)).replace("\\", "/"),
            "svg": str((out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.svg").relative_to(root)).replace("\\", "/"),
        },
        "optuna_allowed": False,
        "ml_allowed": False,
    }


def write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Low Anchor Suggester V0: пользовательский feedback M03/M09/M10/M11",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: зафиксировать красные правки пользователя по тем точкам, где авто-кандидат был рядом, но попал не в ту свечу для рабочего эталона.",
        "",
        "## Главное решение",
        "",
        "`hit_within_3m` теперь считается только near-review, а не gold. Для будущего event dataset положительной точкой остается ручной ledger, если пользователь глазами показал другую свечу.",
        "",
        "## Таблица",
        "",
        "| target | type | preferred signal -> entry | preferred entry + 5 bps | auto | auto signal -> entry | diff signal | verdict |",
        "|---|---|---|---:|---|---|---:|---|",
    ]
    for item in payload["records"]:
        lines.append(
            "| {target_id} | {target_type} | {ps} -> {pe} | {price:.8f} | {cid} | {asig} -> {aent} | {diff:+}m | `{verdict}` |".format(
                target_id=item["target_id"],
                target_type=item["target_type"],
                ps=_fmt_minute(item["preferred_signal_time_utc"]),
                pe=_fmt_minute(item["preferred_entry_time_utc"]),
                price=float(item["preferred_entry_price_with_slippage"]),
                cid=item["current_auto_candidate_id"],
                asig=_fmt_minute(item["current_auto_signal_time_utc"]),
                aent=_fmt_minute(item["current_auto_entry_time_utc"]),
                diff=int(item["signal_diff_minutes_auto_minus_preferred"]),
                verdict=item["user_verdict"],
            )
        )
    lines.extend(
        [
            "",
            "## Правки для следующей версии",
            "",
            "1. Не считать `±3m` финальным попаданием без ручного визуального verdict.",
            "2. Для M03/M09/M11 текущий авто-кандидат пометить как поздний near-candidate, а positive брать из ledger.",
            "3. Для M10 не делать молчаливый сдвиг ledger: auto стоит на одну свечу раньше, пользователь отметил low-anchor зону, поэтому авто-кандидат остается early near-not-gold.",
            "4. В обучающий event dataset добавлять оба слоя: `preferred_manual_positive` и `auto_near_not_gold`, чтобы модель не училась на поздней/неудобной свечке.",
            "",
            "## Границы",
            "",
            "- Scorer, Optuna, ML/export/promotion не запускались.",
            "- Цены входа записаны только для исполнения и визуального контроля.",
            "- Запрещенные признаки выбора входа остаются запрещенными: future return, TP/SL, MFE/MAE, OHLCV entry-свечи.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_feedback_sheet(
    *,
    df: pd.DataFrame,
    payload: dict[str, Any],
    out_png: Path,
    out_svg: Path,
    timeframe: str,
) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(22, 12), sharex=False)
    fig.patch.set_facecolor("#101418")
    flat = list(axes.flatten())

    for ax, item in zip(flat, payload["records"]):
        _style_axis(ax)
        center = pd.Timestamp(item["preferred_signal_time_utc"])
        start = center - pd.Timedelta(minutes=18)
        end = center + pd.Timedelta(minutes=32)
        win = df[(df["open_time_utc"] >= start) & (df["open_time_utc"] <= end)].reset_index(drop=True)
        _draw_candles(ax, win, timeframe, linewidth=0.62)

        preferred_signal = pd.Timestamp(item["preferred_signal_time_utc"]).tz_convert(None)
        preferred_entry = pd.Timestamp(item["preferred_entry_time_utc"]).tz_convert(None)
        auto_signal = pd.Timestamp(item["current_auto_signal_time_utc"]).tz_convert(None)
        auto_entry = pd.Timestamp(item["current_auto_entry_time_utc"]).tz_convert(None)
        anchor_time = pd.Timestamp(item["current_auto_anchor_time_utc"]).tz_convert(None)
        anchor_price = float(item["current_auto_anchor_low_price"])
        preferred_price = float(item["preferred_entry_price_with_slippage"])
        auto_price = float(item["current_auto_entry_price_with_slippage"])

        ax.axvline(preferred_signal, color="#ffd54f", linewidth=2.0, alpha=0.9, zorder=0)
        ax.axvline(preferred_entry, color="#00e676", linewidth=1.4, alpha=0.85, zorder=0)
        ax.axvline(auto_signal, color="#26c6da", linewidth=1.3, alpha=0.75, linestyle="--", zorder=0)
        ax.scatter([anchor_time], [anchor_price], s=85, color="#ff5252", edgecolors="#0b0f12", linewidths=0.8, zorder=6)
        ax.scatter([preferred_entry], [preferred_price], marker="^", s=160, color="#00e676", edgecolors="white", linewidths=0.8, zorder=8)
        ax.scatter([auto_entry], [auto_price], marker="x", s=90, color="#26c6da", linewidths=2.0, zorder=7)

        ax.annotate(
            f"{item['target_id']} preferred entry {_fmt_minute(item['preferred_entry_time_utc'])}\nprice+5bps {preferred_price:.5f}",
            xy=(preferred_entry, preferred_price),
            xytext=(12, 22),
            textcoords="offset points",
            color="#00e676",
            fontsize=9,
            arrowprops={"arrowstyle": "->", "color": "#00e676", "linewidth": 1.2},
            bbox={"facecolor": "#073b26", "edgecolor": "#00e676", "alpha": 0.86, "boxstyle": "round,pad=0.25"},
        )
        ax.annotate(
            f"auto {item['current_auto_candidate_id']} entry {_fmt_minute(item['current_auto_entry_time_utc'])}",
            xy=(auto_entry, auto_price),
            xytext=(10, -48),
            textcoords="offset points",
            color="#26c6da",
            fontsize=8,
            arrowprops={"arrowstyle": "->", "color": "#26c6da", "linewidth": 1.0},
            bbox={"facecolor": "#0b2730", "edgecolor": "#26c6da", "alpha": 0.72, "boxstyle": "round,pad=0.2"},
        )
        ax.annotate(
            "auto anchor",
            xy=(anchor_time, anchor_price),
            xytext=(-10, -24),
            textcoords="offset points",
            color="#ff5252",
            fontsize=8,
            arrowprops={"arrowstyle": "->", "color": "#ff5252", "linewidth": 1.0},
        )
        ax.set_title(
            "{target_id} {target_type} | auto diff {diff:+}m | {verdict}".format(
                target_id=item["target_id"],
                target_type=item["target_type"],
                diff=int(item["signal_diff_minutes_auto_minus_preferred"]),
                verdict=item["user_verdict"],
            ),
            color="white",
            fontsize=10,
        )
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.tick_params(axis="x", labelrotation=20)

    fig.suptitle(
        "SOLUSDT 1m 2026-05-14 | user red feedback: preferred ledger vs auto near-candidate | NO ML/OPTUNA",
        color="white",
        fontsize=15,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_png, dpi=170, facecolor=fig.get_facecolor())
    fig.savefig(out_svg, facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build user feedback pack for low-anchor suggester target review.")
    parser.add_argument("--day", default="2026-05-14")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--target-ids", nargs="+", default=DEFAULT_TARGET_IDS)
    parser.add_argument(
        "--target-ledger",
        default="reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_M01_M19.json",
    )
    parser.add_argument(
        "--suggester-json",
        default="reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/LOW_ANCHOR_ENTRY_SUGGESTER_V0_20260514.json",
    )
    parser.add_argument(
        "--source-feedback-png",
        default=None,
        help="Optional user screenshot to copy into the feedback artifact folder.",
    )
    parser.add_argument(
        "--out-dir",
        default="reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0/user_feedback_v0",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    out_dir = root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    copied_feedback_png: Path | None = None
    if args.source_feedback_png:
        source = Path(args.source_feedback_png)
        if source.exists():
            copied_feedback_png = out_dir / "USER_RED_FEEDBACK_SOURCE_M03_M09_M10_M11_20260701.png"
            shutil.copy2(source, copied_feedback_png)

    payload = build_feedback_payload(
        root=root,
        ledger_path=root / args.target_ledger,
        suggester_path=root / args.suggester_json,
        target_ids=list(args.target_ids),
        source_feedback_png=args.source_feedback_png,
        copied_feedback_png=copied_feedback_png,
        out_dir=out_dir,
    )

    json_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.json"
    report_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701_RU.md"
    png_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.png"
    svg_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V0_USER_FEEDBACK_M03_M09_M10_M11_20260701.svg"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(report_path, payload)
    df = _add_features(_load_ohlcv(_source_csv(root, args.day, args.timeframe, args.symbol)))
    render_feedback_sheet(df=df, payload=payload, out_png=png_path, out_svg=svg_path, timeframe=args.timeframe)

    print(json.dumps(payload["artifacts"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
