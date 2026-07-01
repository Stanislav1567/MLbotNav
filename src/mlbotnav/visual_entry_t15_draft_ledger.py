from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from mlbotnav.visual_entry_indicator_hypothesis_review import _rel, _utc_now
from mlbotnav.visual_entry_low_anchor_suggester import _bar_width_days, _draw_candles, _load_ohlcv, _style_axis


STATUS = "T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_RED_ARROW_FIX_READY_NO_SCORER_NO_ML_NO_OPTUNA"
RAIL_POINT = "T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_RED_ARROW_FIX_BEFORE_PASSPORT_NO_ML_NO_OPTUNA"
DAY = "2026-05-15"
SYMBOL = "SOLUSDT"
TIMEFRAME = "1m"
SLIPPAGE_BPS = 5.0

SOURCE_VERDICT = (
    "reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/"
    "priority_zoom_review_v0/user_verdict_v1/T15_USER_VERDICT_V1_20260701.json"
)
SOURCE_TRANSFER = (
    "reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/"
    "day_20260515_compact_v0/LOW_ANCHOR_TRANSFER_REVIEW_V0_20260515.json"
)
SOURCE_CSV = "data/core/bybit_ohlcv/dt=2026-05-15/tf=1m/symbol=SOLUSDT/part-final.csv"
SOURCE_USER_RED_ARROW_PNG = "C:/Users/007/AppData/Local/Temp/codex-clipboard-0493e45c-5222-4b8d-b7c9-15abb9f381ef.png"

RED_ARROW_ENTRY_OVERRIDES: dict[str, dict[str, str]] = {
    "T15L02": {
        "signal_time_utc": "2026-05-15T02:33:00Z",
        "entry_time_utc": "2026-05-15T02:34:00Z",
        "reason_ru": "красная стрелка пользователя: вход на одну свечу левее прежнего marker",
    },
    "T15L07": {
        "signal_time_utc": "2026-05-15T06:20:00Z",
        "entry_time_utc": "2026-05-15T06:21:00Z",
        "reason_ru": "красная стрелка пользователя: вход от low/reclaim зоны раньше прежнего marker",
    },
    "T15L08": {
        "signal_time_utc": "2026-05-15T08:30:00Z",
        "entry_time_utc": "2026-05-15T08:31:00Z",
        "reason_ru": "красная стрелка пользователя: вход на одну свечу левее прежнего marker",
    },
}

CLUSTERS: dict[str, dict[str, Any]] = {
    "T15_C01_SUPPORT_RETEST_LOW": {
        "title_ru": "Ретест/возврат от поддержки",
        "entry_ids": ["T15L02", "T15L08", "T15L16"],
        "color": "#00e676",
        "passport_priority": "first_candidate",
        "why_ru": "Похожи на входы после локального low и возврата цены от нижней части диапазона.",
        "must_have_ru": [
            "закрытая signal-свеча уже показала low/reclaim",
            "до входа есть пространство до ближайшей верхней зоны",
            "это не мелкий микролой в боковом шуме",
        ],
        "invalidates_ru": [
            "вход расположен в плотной верхней полке без room/path",
            "после low нет явного reclaim на закрытой signal-свече",
            "появляется серия одинаковых микролоев без главного low",
        ],
    },
    "T15_C02_DEEP_CAPITULATION_LOW": {
        "title_ru": "Глубокий пролив / капитуляционный low",
        "entry_ids": ["T15L06", "T15L13"],
        "color": "#29b6f6",
        "passport_priority": "second_candidate",
        "why_ru": "Похожи на более глубокую остановку продаж после выраженного снижения.",
        "must_have_ru": [
            "сильный предшествующий спад виден до signal",
            "signal находится низко в текущем диапазоне",
            "на закрытой signal-свече есть остановка/absorption/reclaim",
        ],
        "invalidates_ru": [
            "это обычный локальный low без предшествующего пролива",
            "нет признаков остановки продаж на signal-свече",
            "вход поздний после уже отработанного отскока",
        ],
    },
    "T15_C03_HOT_RECLAIM_CONTINUATION": {
        "title_ru": "Быстрый reclaim / продолжение",
        "entry_ids": ["T15L07", "T15L11"],
        "color": "#ffca28",
        "passport_priority": "observe_before_passport",
        "why_ru": "Похожи на более быстрый возврат после low, но требуют осторожности, чтобы не спутать с шумом.",
        "must_have_ru": [
            "low уже сформирован до входа",
            "reclaim виден на закрытой signal-свече",
            "вход не является запоздалой покупкой верхней полки",
        ],
        "invalidates_ru": [
            "нет отдельного значимого low",
            "цена уже слишком далеко от low к моменту signal",
            "контекст похож на шумный боковик",
        ],
    },
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def _fmt_ts(value: Any) -> str:
    return pd.Timestamp(value).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def _fmt_minute(value: Any) -> str:
    return pd.Timestamp(value).tz_convert("UTC").strftime("%H:%M")


def _add_context(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["range"] = out["high"] - out["low"]
    out["body"] = (out["close"] - out["open"]).abs()
    out["lower_wick"] = np.minimum(out["open"], out["close"]) - out["low"]
    out["upper_wick"] = out["high"] - np.maximum(out["open"], out["close"])
    out["lower_wick_to_body"] = out["lower_wick"] / out["body"].replace(0, np.nan)
    out["close_pos_candle"] = (out["close"] - out["low"]) / out["range"].replace(0, np.nan)
    out["volume_ma20_prior"] = out["volume"].rolling(20, min_periods=1).mean().shift(1)
    out["volume_ratio20"] = out["volume"] / out["volume_ma20_prior"]
    out["range_ma20_prior"] = out["range"].rolling(20, min_periods=1).mean().shift(1)
    out["range_ratio20"] = out["range"] / out["range_ma20_prior"]
    for window in [20, 60, 180]:
        out[f"rolling_low_{window}"] = out["low"].rolling(window, min_periods=1).min()
        out[f"rolling_high_{window}"] = out["high"].rolling(window, min_periods=1).max()
        denom = (out[f"rolling_high_{window}"] - out[f"rolling_low_{window}"]).replace(0, np.nan)
        out[f"range_pos_{window}"] = (out["close"] - out[f"rolling_low_{window}"]) / denom
        out[f"room_to_high_{window}_bps"] = (out[f"rolling_high_{window}"] - out["close"]) / out["close"] * 10000.0
        out[f"distance_from_low_{window}_bps"] = (out["close"] - out[f"rolling_low_{window}"]) / out["close"] * 10000.0
    for window in [15, 30, 60, 120]:
        out[f"ret_{window}m_pct"] = out["close"].pct_change(window) * 100.0
    return out


def _row_at(df: pd.DataFrame, time_utc: str) -> pd.Series:
    ts = pd.Timestamp(time_utc).tz_convert("UTC")
    match = df[df["open_time_utc"] == ts]
    if match.empty:
        raise ValueError(f"Missing OHLCV row for {time_utc}")
    return match.iloc[0]


def _entry_open(df: pd.DataFrame, time_utc: str) -> float:
    return _safe_float(_row_at(df, time_utc)["open"])


def _cluster_for(candidate_id: str) -> str:
    for cluster_id, cluster in CLUSTERS.items():
        if candidate_id in cluster["entry_ids"]:
            return cluster_id
    return "T15_CXX_UNASSIGNED"


def _cluster_color(cluster_id: str) -> str:
    cluster = CLUSTERS.get(cluster_id)
    return str(cluster.get("color", "#26c6da")) if cluster else "#26c6da"


def _votes_from_signal(row: pd.Series) -> tuple[list[str], list[str]]:
    must: list[str] = []
    caution: list[str] = []
    if _safe_float(row.get("range_pos_60"), 1.0) <= 0.28:
        must.append("LOW_IN_60M_RANGE")
    if _safe_float(row.get("room_to_high_60_bps")) >= 35.0:
        must.append("ROOM_TO_RECENT_HIGH")
    else:
        caution.append("ROOM_MAY_BE_SMALL")
    if _safe_float(row.get("close_pos_candle")) >= 0.50 or _safe_float(row.get("lower_wick_to_body")) >= 0.55:
        must.append("SIGNAL_RECLAIM_OR_WICK")
    else:
        caution.append("WEAK_SIGNAL_RECLAIM")
    if _safe_float(row.get("volume_ratio20")) >= 1.0:
        must.append("VOLUME_NOT_BELOW_PRIOR20")
    else:
        caution.append("LOW_VOLUME_CONFIRMATION")
    if _safe_float(row.get("ret_60m_pct")) <= -0.45:
        must.append("DIP_CONTEXT")
    if _safe_float(row.get("range_ratio20")) >= 2.4:
        caution.append("WIDE_SIGNAL_CANDLE")
    if _safe_float(row.get("distance_from_low_60_bps")) >= 45.0:
        caution.append("FAR_FROM_60M_LOW")
    return must, caution


def _build_ledger(root: Path, df: pd.DataFrame) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    verdict = _read_json(root / SOURCE_VERDICT)
    transfer = _read_json(root / SOURCE_TRANSFER)
    transfer_by_id = {str(item["candidate_id"]): item for item in transfer["candidates"]}

    records: list[dict[str, Any]] = []
    for item in verdict["records"]:
        if item["review_label"] != "user_confirmed_entry":
            continue
        cid = str(item["candidate_id"])
        correction = RED_ARROW_ENTRY_OVERRIDES.get(cid)
        original_signal_time = str(item["signal_time_utc"])
        original_entry_time = str(item["entry_time_utc"])
        signal_time = correction["signal_time_utc"] if correction else original_signal_time
        entry_time = correction["entry_time_utc"] if correction else original_entry_time
        signal_row = _row_at(df, signal_time)
        entry_open = _entry_open(df, entry_time)
        entry_plus = entry_open * (1.0 + SLIPPAGE_BPS / 10000.0)
        cluster_id = _cluster_for(cid)
        must_votes, caution_votes = _votes_from_signal(signal_row)
        source = transfer_by_id[cid]
        records.append(
            {
                "entry_id": cid,
                "symbol": SYMBOL,
                "timeframe": TIMEFRAME,
                "day_utc": DAY,
                "side": "long",
                "signal_time_utc": _fmt_ts(signal_time),
                "entry_time_utc": _fmt_ts(entry_time),
                "original_signal_time_utc": _fmt_ts(original_signal_time),
                "original_entry_time_utc": _fmt_ts(original_entry_time),
                "user_red_arrow_corrected": bool(correction),
                "user_red_arrow_reason_ru": correction["reason_ru"] if correction else "",
                "entry_open_price": round(entry_open, 8),
                "slippage_bps": SLIPPAGE_BPS,
                "entry_price_plus_5bps": round(entry_plus, 8),
                "source_transfer_type": str(item["transfer_type"]),
                "source_transfer_score": int(item["transfer_score"]),
                "draft_cluster_id": cluster_id,
                "draft_cluster_title_ru": str(CLUSTERS[cluster_id]["title_ru"]),
                "lock_status": "draft_unlocked",
                "label_status": "user_confirmed_entry_not_target_lock",
                "selection_boundary": "signal_candle_close_and_past_context_only",
                "execution_price_role": "execution_only_not_selection_feature",
                "why_good_ru": str(CLUSTERS[cluster_id]["why_ru"]),
                "must_have_ru": CLUSTERS[cluster_id]["must_have_ru"],
                "invalidates_ru": CLUSTERS[cluster_id]["invalidates_ru"],
                "features_at_signal_close": {
                    "signal_open": round(_safe_float(signal_row["open"]), 8),
                    "signal_high": round(_safe_float(signal_row["high"]), 8),
                    "signal_low": round(_safe_float(signal_row["low"]), 8),
                    "signal_close": round(_safe_float(signal_row["close"]), 8),
                    "ret_30m_pct": round(_safe_float(signal_row.get("ret_30m_pct")), 5),
                    "ret_60m_pct": round(_safe_float(signal_row.get("ret_60m_pct")), 5),
                    "ret_120m_pct": round(_safe_float(signal_row.get("ret_120m_pct")), 5),
                    "range_pos_60": round(_safe_float(signal_row.get("range_pos_60")), 5),
                    "range_pos_180": round(_safe_float(signal_row.get("range_pos_180")), 5),
                    "room_to_high_60_bps": round(_safe_float(signal_row.get("room_to_high_60_bps")), 4),
                    "distance_from_low_60_bps": round(_safe_float(signal_row.get("distance_from_low_60_bps")), 4),
                    "volume_ratio20": round(_safe_float(signal_row.get("volume_ratio20")), 5),
                    "range_ratio20": round(_safe_float(signal_row.get("range_ratio20")), 5),
                    "lower_wick_to_body": round(_safe_float(signal_row.get("lower_wick_to_body")), 5),
                    "close_pos_candle": round(_safe_float(signal_row.get("close_pos_candle")), 5),
                },
                "no_lookahead_votes": must_votes,
                "caution_votes": caution_votes,
                "source_transfer_votes": source.get("transfer_pass_votes", []),
                "source_transfer_risks": source.get("transfer_risk_votes", []),
            }
        )
    records.sort(key=lambda row: row["entry_time_utc"])
    summary = {
        "confirmed_count": len(records),
        "red_arrow_corrected_ids": sorted(RED_ARROW_ENTRY_OVERRIDES),
        "cluster_counts": {
            cluster_id: len([row for row in records if row["draft_cluster_id"] == cluster_id]) for cluster_id in CLUSTERS
        },
        "first_passport_candidate_cluster": "T15_C01_SUPPORT_RETEST_LOW",
        "first_passport_candidate_reason_ru": "Самый плотный повторяющийся кластер: 3 входа из 7, близок к уже понятному support/retest-low шаблону.",
    }
    return records, summary


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = [
        "entry_id",
        "draft_cluster_id",
        "draft_cluster_title_ru",
        "signal_time_utc",
        "entry_time_utc",
        "original_signal_time_utc",
        "original_entry_time_utc",
        "user_red_arrow_corrected",
        "entry_open_price",
        "entry_price_plus_5bps",
        "source_transfer_type",
        "source_transfer_score",
        "no_lookahead_votes",
        "caution_votes",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            out = dict(row)
            out["no_lookahead_votes"] = ",".join(out.get("no_lookahead_votes") or [])
            out["caution_votes"] = ",".join(out.get("caution_votes") or [])
            writer.writerow({col: out.get(col) for col in columns})


def _write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# T15 Draft Ledger / Cluster Discussion V1",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: рабочий draft-ledger по 7 подтвержденным входам `SOLUSDT 1m 2026-05-15` перед паспортом, с учетом красных стрелок пользователя на скрине. Это не target-lock, не scorer, не ML dataset и не Optuna.",
        "",
        "## Граница",
        "",
        "- Вход LONG: закрытая `signal`-свеча -> `open` следующей свечи.",
        "- `entry_open_price` и `entry + 5 bps` нужны только для исполнения и визуального контроля.",
        "- Для выбора входа запрещены future return, TP/SL, MFE/MAE и OHLCV entry-свечи.",
        "- EMA не используется как active condition.",
        "",
        "## Правки по красным стрелкам",
        "",
        "| id | было entry | стало entry | правило |",
        "|---|---:|---:|---|",
    ]
    for row in payload["entries"]:
        if row["user_red_arrow_corrected"]:
            lines.append(
                f"| `{row['entry_id']}` | `{row['original_entry_time_utc'][11:16]}` | "
                f"`{row['entry_time_utc'][11:16]}` | `{row['user_red_arrow_reason_ru']}` |"
            )
    lines.extend(
        [
            "",
            "## 7 входов",
            "",
            "| id | cluster | signal UTC | entry UTC | entry open | entry + 5 bps |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for row in payload["entries"]:
        lines.append(
            f"| `{row['entry_id']}` | `{row['draft_cluster_id']}` | `{row['signal_time_utc'][11:16]}` | "
            f"`{row['entry_time_utc'][11:16]}` | `{row['entry_open_price']:.5f}` | `{row['entry_price_plus_5bps']:.5f}` |"
        )
    lines.extend(["", "## Кластеры", ""])
    for cluster_id, cluster in payload["clusters"].items():
        lines.extend(
            [
                f"### `{cluster_id}`",
                "",
                f"- Название: {cluster['title_ru']}.",
                f"- Входы: `{', '.join(cluster['entry_ids'])}`.",
                f"- Приоритет: `{cluster['passport_priority']}`.",
                f"- Смысл: {cluster['why_ru']}",
                f"- Must-have: {'; '.join(cluster['must_have_ru'])}.",
                f"- Invalidates: {'; '.join(cluster['invalidates_ru'])}.",
                "",
            ]
        )
    lines.extend(
        [
            "## Итог для следующего пункта",
            "",
            f"Первый паспортный кандидат: `{payload['summary']['first_passport_candidate_cluster']}`.",
            "",
            "Причина: " + payload["summary"]["first_passport_candidate_reason_ru"],
            "",
            "Следующий шаг: показать этот draft пользователю и после `норм/фиксить` перейти к draft-паспорту только по одному выбранному кластеру.",
            "",
            "## Артефакты",
            "",
        ]
    )
    for value in payload["artifacts"].values():
        lines.append(f"- `{value}`")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _draw_entry_marker(ax: Any, row: dict[str, Any], *, annotate: bool) -> None:
    signal = pd.Timestamp(row["signal_time_utc"]).tz_convert(None)
    entry = pd.Timestamp(row["entry_time_utc"]).tz_convert(None)
    color = _cluster_color(str(row["draft_cluster_id"]))
    price = float(row["entry_price_plus_5bps"])
    ax.axvline(signal, color=color, alpha=0.22, linewidth=1.2)
    ax.axvline(entry, color=color, alpha=0.62, linewidth=1.6)
    ax.scatter([entry], [price], marker="^", s=105, color=color, edgecolors="white", linewidths=0.8, zorder=8)
    if annotate:
        ax.annotate(
            f"{row['entry_id']} {entry.strftime('%H:%M')}\nopen {row['entry_open_price']:.4f} | +5bps {price:.4f}",
            xy=(entry, price),
            xytext=(5, 13),
            textcoords="offset points",
            color=color,
            fontsize=7.5,
        )


def _render_png(df: pd.DataFrame, rows: list[dict[str, Any]], out_path: Path) -> None:
    fig = plt.figure(figsize=(30, 24), facecolor="#101418")
    grid = fig.add_gridspec(5, 4, height_ratios=[2.3, 1.0, 1.0, 1.0, 1.0], hspace=0.30, wspace=0.16)
    ax_full = fig.add_subplot(grid[0, :])
    ax_vol = fig.add_subplot(grid[1, :], sharex=ax_full)
    for ax in [ax_full, ax_vol]:
        _style_axis(ax)
    _draw_candles(ax_full, df, TIMEFRAME, linewidth=0.30)
    for row in rows:
        _draw_entry_marker(ax_full, row, annotate=True)
    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(df["open"], df["close"])]
    ax_vol.bar(df["open_time_utc"].dt.tz_convert(None), df["volume"], width=_bar_width_days(TIMEFRAME), color=colors, alpha=0.70)
    start = pd.Timestamp(f"{DAY}T00:00:00")
    ax_full.set_xlim(start.to_pydatetime(), (start + pd.Timedelta(days=1)).to_pydatetime())
    ax_full.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    ax_vol.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 3)))
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    for idx, row in enumerate(rows):
        ax = fig.add_subplot(grid[2 + idx // 4, idx % 4])
        _style_axis(ax)
        signal = pd.Timestamp(row["signal_time_utc"]).tz_convert("UTC")
        start_win = signal - pd.Timedelta(minutes=26)
        end_win = signal + pd.Timedelta(minutes=38)
        win = df[(df["open_time_utc"] >= start_win) & (df["open_time_utc"] <= end_win)].reset_index(drop=True)
        _draw_candles(ax, win, TIMEFRAME, linewidth=0.62)
        _draw_entry_marker(ax, row, annotate=True)
        ax.set_xlim(start_win.tz_convert(None).to_pydatetime(), end_win.tz_convert(None).to_pydatetime())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        cluster = CLUSTERS[str(row["draft_cluster_id"])]
        ax.set_title(
            f"{row['entry_id']} | {cluster['title_ru']} | signal {row['signal_time_utc'][11:16]} -> entry {row['entry_time_utc'][11:16]}",
            color="white",
            fontsize=8.5,
        )
        ax.tick_params(axis="x", labelrotation=25)

    ax_notes = fig.add_subplot(grid[4, 3])
    _style_axis(ax_notes)
    ax_notes.axis("off")
    notes = [
        "DRAFT ONLY",
        "NO scorer / NO ML / NO Optuna",
        "entry price = execution only",
        "EMA deferred",
        "next: choose one cluster for passport",
    ]
    ax_notes.text(0.02, 0.95, "\n".join(notes), transform=ax_notes.transAxes, color="#cfd8dc", va="top", fontsize=11)

    fig.suptitle(
        "SOLUSDT 1m 2026-05-15 | T15 draft-ledger: 7 confirmed entries | cluster discussion | NO ML/OPTUNA",
        color="white",
        fontsize=16,
    )
    fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def run(out_dir: Path) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    df = _add_context(_load_ohlcv(root / SOURCE_CSV))
    entries, summary = _build_ledger(root, df)

    png_path = out_dir / "T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701.png"
    json_path = out_dir / "T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701.json"
    csv_path = out_dir / "T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701.csv"
    report_path = out_dir / "T15_DRAFT_LEDGER_CLUSTER_DISCUSSION_V1_20260701_RU.md"
    _render_png(df, entries, png_path)

    payload: dict[str, Any] = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "rail_point": RAIL_POINT,
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "day_utc": DAY,
        "source_verdict_json": SOURCE_VERDICT,
        "source_transfer_json": SOURCE_TRANSFER,
        "source_csv": SOURCE_CSV,
        "source_user_red_arrow_png": SOURCE_USER_RED_ARROW_PNG,
        "summary": summary,
        "clusters": CLUSTERS,
        "entries": entries,
        "no_lookahead_boundary": {
            "features_end_at": "closed_signal_candle_and_past_context",
            "entry_rule": "LONG at next candle open after closed signal",
            "entry_open_price_is_execution_only": True,
            "ema_active_condition": False,
            "forbidden_features": ["future_return", "tp_sl", "mfe_mae", "entry_candle_ohlcv_for_selection"],
        },
        "next_step": "USER_REVIEW_DRAFT_LEDGER_THEN_CHOOSE_ONE_CLUSTER_FOR_PASSPORT",
        "artifacts": {
            "png": _rel(root, png_path),
            "json": _rel(root, json_path),
            "csv": _rel(root, csv_path),
            "report_ru": _rel(root, report_path),
        },
        "scorer_allowed": False,
        "target_lock_allowed": False,
        "optuna_allowed": False,
        "ml_allowed": False,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_csv(csv_path, entries)
    _write_report(report_path, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Build T15 draft-ledger and cluster discussion before passport.")
    parser.add_argument(
        "--out-dir",
        default=(
            "reports/final_review/visual_entry_v3/fresh_target_led/indicator_hypothesis_review_v0/"
            "priority_zoom_review_v0/user_verdict_v1/draft_ledger_v1"
        ),
    )
    args = parser.parse_args()
    payload = run(Path(args.out_dir))
    print(
        json.dumps(
            {
                "status": payload["status"],
                "confirmed_count": payload["summary"]["confirmed_count"],
                "cluster_counts": payload["summary"]["cluster_counts"],
                "first_passport_candidate_cluster": payload["summary"]["first_passport_candidate_cluster"],
                "artifacts": payload["artifacts"],
                "scorer_allowed": payload["scorer_allowed"],
                "target_lock_allowed": payload["target_lock_allowed"],
                "optuna_allowed": payload["optuna_allowed"],
                "ml_allowed": payload["ml_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
