from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle


TARGET_TYPES = {
    "DEEP_CAPITULATION_LOW",
    "SWING_LOW_RECLAIM",
    "SUPPORT_RETEST_LOW",
    "TREND_DIP_CONTINUATION",
    "BOS_FIBO_RECLAIM",
    "VOLUME_WICK_ABSORPTION",
    "HOT_RECLAIM_SUPPORT",
    "UNKNOWN_OR_MIXED",
}


def _utc_tag() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safe_time(value: str) -> pd.Timestamp:
    return pd.Timestamp(value).tz_convert("UTC")


def _load_manual_payload(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _source_csv(payload: dict[str, Any]) -> Path:
    images = payload.get("source_images") or []
    if not images:
        raise ValueError("manual_entries has no source_images")
    csv_path = images[0].get("source_csv")
    if not csv_path:
        raise ValueError("manual_entries source_images[0] has no source_csv")
    return Path(csv_path)


def _load_rows(source_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(source_csv)
    if "open_time_utc" not in df.columns:
        raise ValueError(f"{source_csv} has no open_time_utc column")
    df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], utc=True)
    return df.sort_values("open_time_utc").reset_index(drop=True)


def _bar_width_days(timeframe: str) -> float:
    minutes = int(timeframe[:-1]) if timeframe.endswith("m") else 1
    return (minutes / (24 * 60)) * 0.8


def _render_clean_chart(df: pd.DataFrame, payload: dict[str, Any], out_dir: Path) -> Path:
    symbol = payload.get("symbol", "UNKNOWN")
    timeframe = payload.get("timeframe", "1m")
    day = (payload.get("source_images") or [{}])[0].get("date_utc") or payload.get("day_utc") or "unknown_day"

    work = df.copy()
    work["ema20"] = work["close"].ewm(span=20, adjust=False).mean()
    work["ema50"] = work["close"].ewm(span=50, adjust=False).mean()

    x = mdates.date2num(work["open_time_utc"].to_numpy())
    width = _bar_width_days(str(timeframe))

    fig, (ax_price, ax_vol) = plt.subplots(
        2,
        1,
        figsize=(18, 9),
        sharex=True,
        gridspec_kw={"height_ratios": [4, 1.35]},
    )
    bg = "#101418"
    fig.patch.set_facecolor(bg)
    ax_price.set_facecolor(bg)
    ax_vol.set_facecolor(bg)

    up_color = "#26a69a"
    down_color = "#ef5350"
    wick_color = "#cfd8dc"
    is_up = work["close"] >= work["open"]

    ax_price.vlines(x, work["low"], work["high"], color=wick_color, linewidth=0.8, alpha=0.85, zorder=1)
    for i, row in work.iterrows():
        lower = min(float(row["open"]), float(row["close"]))
        height = max(abs(float(row["close"]) - float(row["open"])), 1e-8)
        color = up_color if row["close"] >= row["open"] else down_color
        ax_price.add_patch(
            Rectangle((x[i] - width / 2, lower), width, height, facecolor=color, edgecolor=color, linewidth=0.55)
        )

    ax_price.plot(work["open_time_utc"], work["ema20"], color="#ffd54f", linewidth=1.0, label="EMA20")
    ax_price.plot(work["open_time_utc"], work["ema50"], color="#64b5f6", linewidth=1.0, label="EMA50")
    ax_vol.bar(
        work["open_time_utc"],
        work["volume"],
        width=width,
        color=[up_color if item else down_color for item in is_up],
        alpha=0.8,
    )

    ax_price.set_title(f"{symbol} {timeframe} {day} UTC | CLEAN TARGET-LED START | NO SIGNALS", color="white", fontsize=14)
    ax_price.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    ax_price.legend(facecolor="#172026", edgecolor="#3a444b", labelcolor="white", fontsize=9, loc="upper left")

    for ax in (ax_price, ax_vol):
        ax.grid(color="#2f3a40", alpha=0.45, linewidth=0.6)
        ax.tick_params(colors="#e0e0e0")
        for spine in ax.spines.values():
            spine.set_color("#3a444b")
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate()

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"fresh_target_led_clean_chart_{symbol}_{timeframe}_{day}_{_utc_tag()}.png"
    plt.tight_layout()
    plt.savefig(path, dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


def _context_features(df: pd.DataFrame, signal_time: pd.Timestamp) -> dict[str, Any]:
    matches = df.index[df["open_time_utc"] == signal_time]
    if len(matches) == 0:
        return {"status": "missing_signal_candle"}
    idx = int(matches[0])
    row = df.iloc[idx]
    prev60 = df.iloc[max(0, idx - 59) : idx + 1]
    prev180 = df.iloc[max(0, idx - 179) : idx + 1]
    prior20 = df.iloc[max(0, idx - 20) : idx] if idx > 0 else df.iloc[0:0]

    low60 = float(prev60["low"].min())
    high60 = float(prev60["high"].max())
    low180 = float(prev180["low"].min())
    high180 = float(prev180["high"].max())
    close = float(row["close"])
    open_ = float(row["open"])
    high = float(row["high"])
    low = float(row["low"])
    denom60 = max(high60 - low60, 1e-9)
    denom180 = max(high180 - low180, 1e-9)

    ret30 = None
    ret120 = None
    if idx >= 30:
        ret30 = close / float(df.iloc[idx - 30]["close"]) - 1.0
    if idx >= 120:
        ret120 = close / float(df.iloc[idx - 120]["close"]) - 1.0

    lower_wick = min(open_, close) - low
    body = abs(close - open_)
    upper_wick = high - max(open_, close)
    vol_mean = float(prior20["volume"].mean()) if len(prior20) else 0.0
    vol_ratio = float(row["volume"]) / vol_mean if vol_mean > 0 else None

    return {
        "status": "ok",
        "row_index": idx,
        "signal_open": open_,
        "signal_high": high,
        "signal_low": low,
        "signal_close": close,
        "ret_30m_pct": None if ret30 is None else round(ret30 * 100, 4),
        "ret_120m_pct": None if ret120 is None else round(ret120 * 100, 4),
        "range_pos_60": round((close - low60) / denom60, 4),
        "range_pos_180": round((close - low180) / denom180, 4),
        "is_low_60": bool(low <= low60 + 1e-9),
        "is_low_180": bool(low <= low180 + 1e-9),
        "body_pct_of_price": round(body / max(close, 1e-9) * 100, 4),
        "lower_wick_to_body": round(lower_wick / max(body, 1e-9), 4),
        "upper_wick_to_body": round(upper_wick / max(body, 1e-9), 4),
        "volume_to_prior20": None if vol_ratio is None else round(vol_ratio, 4),
        "green_signal": bool(close >= open_),
    }


def _classify(features: dict[str, Any]) -> tuple[str, list[str]]:
    if features.get("status") != "ok":
        return "UNKNOWN_OR_MIXED", ["сигнальная свеча не найдена в CSV"]

    reasons: list[str] = []
    ret120 = features.get("ret_120m_pct")
    ret30 = features.get("ret_30m_pct")
    range60 = float(features.get("range_pos_60", 1.0))
    range180 = float(features.get("range_pos_180", 1.0))
    wick = float(features.get("lower_wick_to_body", 0.0))
    vol = features.get("volume_to_prior20")
    is_low60 = bool(features.get("is_low_60"))
    is_low180 = bool(features.get("is_low_180"))
    green = bool(features.get("green_signal"))

    if ret120 is not None and ret120 <= -0.7 and range180 <= 0.35:
        reasons.append("сильное предыдущее снижение и свеча около нижней части 180-минутного диапазона")
        if wick >= 1.2 or (vol is not None and vol >= 1.8):
            reasons.append("есть фитиль/объемный признак остановки продажи")
            return "VOLUME_WICK_ABSORPTION", reasons
        return "DEEP_CAPITULATION_LOW", reasons

    if ret120 is not None and ret120 >= 0.25 and range180 >= 0.55 and range60 <= 0.65:
        reasons.append("восходящий/горячий контекст и локальный откат без глубокого слома")
        return "TREND_DIP_CONTINUATION", reasons

    if is_low60 and green:
        reasons.append("локальный low 60m с закрытием не ниже открытия")
        return "SWING_LOW_RECLAIM", reasons

    if range60 <= 0.28 and ret30 is not None and ret30 < 0 and green:
        reasons.append("откат к нижней зоне 60m после локального снижения и reclaim-свеча")
        return "SUPPORT_RETEST_LOW", reasons

    if range60 <= 0.22 and range180 <= 0.18:
        reasons.append("свеча стоит в нижней части локального и дневного диапазона")
        return "SUPPORT_RETEST_LOW", reasons

    if range180 >= 0.42 and range60 <= 0.62:
        reasons.append("высокий общий диапазон дня и локальный откат к поддержке")
        return "HOT_RECLAIM_SUPPORT", reasons

    reasons.append("тип пока смешанный, нужен ручной визуальный выбор")
    return "UNKNOWN_OR_MIXED", reasons


def build_target_ledger(manual_entries_path: Path, out_dir: Path, *, limit: int = 10) -> dict[str, Any]:
    manual_payload = _load_manual_payload(manual_entries_path)
    source_csv = _source_csv(manual_payload)
    df = _load_rows(source_csv)
    clean_chart = _render_clean_chart(df, manual_payload, out_dir)

    symbol = str(manual_payload.get("symbol", "SOLUSDT"))
    timeframe = str(manual_payload.get("timeframe", "1m"))
    day = str((manual_payload.get("source_images") or [{}])[0].get("date_utc", ""))
    entries = sorted(manual_payload.get("entries", []), key=lambda item: str(item.get("target_entry_time_utc", "")))[:limit]

    targets = []
    for idx, entry in enumerate(entries, 1):
        signal_time = _safe_time(str(entry["signal_candle_time_utc"]))
        context_features = _context_features(df, signal_time)
        target_type, reasons = _classify(context_features)
        if target_type not in TARGET_TYPES:
            target_type = "UNKNOWN_OR_MIXED"
        target_id = f"T{idx:02d}"
        targets.append(
            {
                "target_id": target_id,
                "source_entry_id": entry.get("entry_id"),
                "source_entry_number": entry.get("entry_number"),
                "symbol": symbol,
                "timeframe": timeframe,
                "day_utc": day,
                "signal_time_utc": entry.get("signal_candle_time_utc"),
                "entry_time_utc": entry.get("target_entry_time_utc"),
                "side": "long",
                "target_type": target_type,
                "status": "candidate_needs_visual_confirm",
                "why_good": "автоматически перенесено из пользовательской v2-разметки красных стрелок; требуется визуальное подтверждение на чистом графике",
                "must_have": "сигнал формируется на закрытой signal-свече; вход LONG только на open следующей свечи с slippage_bps=5",
                "invalidates": "сдвиг ручной стрелки при визуальной проверке; использование entry-candle OHLCV/future return/TP/SL/MFE/MAE для выбора входа",
                "linked_strategy": "",
                "linked_passport": "",
                "lock_status": "unlocked",
                "classification_reasons_ru": reasons,
                "context_features": context_features,
                "visual_confirm_required": bool(entry.get("visual_confirm_required", True)),
            }
        )

    clusters: dict[str, list[str]] = {}
    for target in targets:
        clusters.setdefault(str(target["target_type"]), []).append(str(target["target_id"]))
    first_cluster_type = ""
    first_cluster_targets: list[str] = []
    cluster_candidates = [
        (target_type, ids)
        for target_type, ids in clusters.items()
        if 2 <= len(ids) <= 4 and target_type != "UNKNOWN_OR_MIXED"
    ]
    if cluster_candidates:
        first_cluster_type, first_cluster_targets = max(
            cluster_candidates,
            key=lambda item: (len(item[1]), item[0]),
        )
    else:
        for target_type, ids in clusters.items():
            if len(ids) >= 2 and target_type != "UNKNOWN_OR_MIXED":
                first_cluster_type = target_type
                first_cluster_targets = ids[:4]
                break

    payload = {
        "schema_version": 1,
        "status": "FRESH_TARGET_LED_WORKFLOW_READY_NO_ML",
        "created_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_manual_entries": str(manual_entries_path),
        "source_csv": str(source_csv),
        "clean_chart_png": str(clean_chart),
        "symbol": symbol,
        "timeframe": timeframe,
        "day_utc": day,
        "target_limit": limit,
        "contract": {
            "entry_only": True,
            "signal_rule": "signal candle is closed",
            "entry_rule": "LONG at next candle open",
            "slippage_bps": 5,
            "forbidden": [
                "future_return",
                "TP_SL_for_entry_selection",
                "MFE_MAE_for_entry_selection",
                "entry_candle_OHLCV_for_entry_selection",
                "ML_export_without_APPROVED_FOR_ML",
                "Optuna_before_passport_contract",
            ],
        },
        "targets": targets,
        "type_summary": {key: len(value) for key, value in sorted(clusters.items())},
        "first_cluster_candidate": {
            "target_type": first_cluster_type,
            "target_ids": first_cluster_targets,
            "status": "candidate_needs_visual_confirm" if first_cluster_targets else "not_selected",
        },
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"target_ledger_{symbol}_{timeframe}_{day}_T01_T{limit:02d}.json"
    md_path = out_dir / f"target_ledger_{symbol}_{timeframe}_{day}_T01_T{limit:02d}_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_build_markdown(payload), encoding="utf-8")
    payload["target_ledger_json"] = str(json_path)
    payload["target_ledger_md"] = str(md_path)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def _build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        f"# Fresh target-led ledger {payload['symbol']} {payload['timeframe']} {payload['day_utc']}",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        f"Чистый график: `{payload['clean_chart_png']}`.",
        f"Источник ручных точек: `{payload['source_manual_entries']}`.",
        "",
        "## Контракт",
        "",
        "1. Сигнал берется только на закрытой signal-свече.",
        "2. Вход LONG выполняется на `open` следующей свечи с `slippage_bps=5`.",
        "3. Optuna, ML/export/promotion запрещены до отдельного решения.",
        "4. Future return, TP/SL, MFE/MAE и OHLCV entry-свечи нельзя использовать для выбора входа.",
        "",
        "## T01..T10",
        "",
        "| target_id | signal_time_utc | entry_time_utc | type | status |",
        "|---|---|---|---|---|",
    ]
    for target in payload["targets"]:
        lines.append(
            "| {target_id} | {signal_time_utc} | {entry_time_utc} | {target_type} | {status} |".format(**target)
        )
    lines.extend(["", "## Сводка типов", ""])
    for target_type, count in payload["type_summary"].items():
        lines.append(f"- `{target_type}`: {count}")
    cluster = payload["first_cluster_candidate"]
    lines.extend(
        [
            "",
            "## Первый кластер-кандидат",
            "",
            f"Тип: `{cluster['target_type'] or 'NOT_SELECTED'}`.",
            f"Точки: `{', '.join(cluster['target_ids']) if cluster['target_ids'] else 'нет'}`.",
            "",
            "Решение: кластер пока не является стратегией и не является lock. Его нужно подтвердить глазами на чистом графике.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build fresh target-led T01..T10 ledger without Optuna or ML export.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/fresh_target_led")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    payload = build_target_ledger(Path(args.manual_entries), Path(args.out_dir), limit=int(args.limit))
    print(payload["target_ledger_json"])
    print(payload["target_ledger_md"])
    print(payload["clean_chart_png"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
