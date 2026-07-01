from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle


STATUS = "LOW_ANCHOR_ENTRY_SUGGESTER_V0_SEED_DAY_REVIEW_NO_ML_NO_OPTUNA"


@dataclass(frozen=True)
class ManualTarget:
    target_id: str
    signal_time: pd.Timestamp
    entry_time: pd.Timestamp
    target_type: str


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _fmt_ts(value: pd.Timestamp) -> str:
    return value.tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def _fmt_minute(value: pd.Timestamp) -> str:
    return value.tz_convert("UTC").strftime("%H:%M")


def _bar_width_days(timeframe: str) -> float:
    if timeframe.endswith("m"):
        return (int(timeframe[:-1]) / (24 * 60)) * 0.8
    return (1 / (24 * 60)) * 0.8


def _source_csv(root: Path, day: str, timeframe: str, symbol: str) -> Path:
    return root / "data" / "core" / "bybit_ohlcv" / f"dt={day}" / f"tf={timeframe}" / f"symbol={symbol}" / "part-final.csv"


def _load_ohlcv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], utc=True, errors="raise", format="mixed")
    df["close_time_utc"] = pd.to_datetime(df["close_time_utc"], utc=True, errors="raise", format="mixed")
    df = df.sort_values("open_time_utc").reset_index(drop=True)
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)
    return df


def _load_targets(path: Path) -> list[ManualTarget]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    out: list[ManualTarget] = []
    for item in payload.get("targets", []):
        out.append(
            ManualTarget(
                target_id=str(item["target_id"]),
                signal_time=pd.Timestamp(item["signal_time_utc"]).tz_convert("UTC"),
                entry_time=pd.Timestamp(item["entry_time_utc"]).tz_convert("UTC"),
                target_type=str(item.get("target_type") or "UNKNOWN"),
            )
        )
    return out


def _add_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for window in [5, 10, 20, 30, 60, 120, 180]:
        out[f"rolling_low_{window}"] = out["low"].rolling(window, min_periods=1).min()
        out[f"rolling_high_{window}"] = out["high"].rolling(window, min_periods=1).max()
        denom = (out[f"rolling_high_{window}"] - out[f"rolling_low_{window}"]).replace(0, np.nan)
        out[f"range_pos_{window}"] = (out["close"] - out[f"rolling_low_{window}"]) / denom
    for window in [5, 15, 30, 60, 120]:
        out[f"ret_{window}m_pct"] = out["close"].pct_change(window) * 100.0
    out["range"] = out["high"] - out["low"]
    out["body"] = (out["close"] - out["open"]).abs()
    out["lower_wick"] = np.minimum(out["open"], out["close"]) - out["low"]
    out["upper_wick"] = out["high"] - np.maximum(out["open"], out["close"])
    out["lower_wick_to_body"] = out["lower_wick"] / out["body"].replace(0, np.nan)
    out["volume_ma20_prior"] = out["volume"].rolling(20, min_periods=1).mean().shift(1)
    out["volume_ratio20"] = out["volume"] / out["volume_ma20_prior"]
    delta = out["close"].diff()
    gain = delta.clip(lower=0).rolling(14, min_periods=1).mean()
    loss = (-delta.clip(upper=0)).rolling(14, min_periods=1).mean()
    rs = gain / loss.replace(0, np.nan)
    out["rsi14"] = 100.0 - (100.0 / (1.0 + rs))
    ema12 = out["close"].ewm(span=12, adjust=False).mean()
    ema26 = out["close"].ewm(span=26, adjust=False).mean()
    out["macd"] = ema12 - ema26
    out["macd_signal"] = out["macd"].ewm(span=9, adjust=False).mean()
    out["macd_hist"] = out["macd"] - out["macd_signal"]
    out["range_ma20_prior"] = out["range"].rolling(20, min_periods=1).mean().shift(1)
    out["range_compression20"] = out["range"] / out["range_ma20_prior"]
    return out


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def _suggested_type(row: pd.Series) -> str:
    ret30 = _safe_float(row.get("ret_30m_pct"))
    ret60 = _safe_float(row.get("ret_60m_pct"))
    pos60 = _safe_float(row.get("range_pos_60"), 0.5)
    volr = _safe_float(row.get("volume_ratio20"))
    if ret60 <= -0.55 and pos60 <= 0.20:
        return "DEEP_CAPITULATION_LOW"
    if ret30 <= -0.25 and pos60 <= 0.18:
        return "SUPPORT_RETEST_LOW"
    if ret60 >= 0.25 and pos60 >= 0.40:
        return "TREND_DIP_CONTINUATION"
    if volr >= 3.0 or ret30 <= -0.70:
        return "HOT_RECLAIM_SUPPORT"
    if pos60 <= 0.28:
        return "SWING_LOW_RECLAIM"
    return "LOW_ANCHOR_RECLAIM"


def _risk_flags(row: pd.Series, anchor_age: int) -> list[str]:
    flags: list[str] = []
    if _safe_float(row.get("ret_30m_pct")) <= -0.75:
        flags.append("strong_drop_context")
    if _safe_float(row.get("range_pos_60"), 0.5) <= 0.05:
        flags.append("very_low_in_60m_range")
    if _safe_float(row.get("volume_ratio20")) < 0.55:
        flags.append("low_volume_confirmation")
    if anchor_age == 0 and _safe_float(row.get("lower_wick_to_body")) < 0.5:
        flags.append("anchor_without_clear_wick")
    if _safe_float(row.get("range_compression20"), 1.0) > 2.5:
        flags.append("wide_signal_range")
    return flags


def _nearest_target(signal_time: pd.Timestamp, targets: list[ManualTarget]) -> tuple[ManualTarget | None, int | None]:
    if not targets:
        return None, None
    target = min(targets, key=lambda item: abs((item.signal_time - signal_time).total_seconds()))
    diff = int(round((signal_time - target.signal_time).total_seconds() / 60.0))
    return target, diff


def build_candidates(
    df: pd.DataFrame,
    *,
    targets: list[ManualTarget],
    anchor_lookback: int,
    max_anchor_age: int,
    cooldown_minutes: int,
    min_score: float,
    slippage_bps: float,
) -> list[dict[str, Any]]:
    raw: list[dict[str, Any]] = []
    for idx in range(max(30, anchor_lookback), len(df) - 1):
        row = df.iloc[idx]
        start = max(0, idx - anchor_lookback + 1)
        recent = df.iloc[start : idx + 1]
        anchor_idx = int(recent["low"].idxmin())
        anchor_age = idx - anchor_idx
        if anchor_age > max_anchor_age:
            continue

        anchor = df.iloc[anchor_idx]
        pos10 = _safe_float(row.get("range_pos_10"), 1.0)
        near_low = pos10 <= 0.55 or _safe_float(anchor["low"]) <= _safe_float(row.get("rolling_low_20")) + 1e-9
        if not near_low:
            continue

        reclaim_bps = (_safe_float(row["close"]) - _safe_float(anchor["low"])) / max(_safe_float(row["close"]), 1e-9) * 10000.0
        wick_ratio = _safe_float(row.get("lower_wick_to_body"))
        volume_ratio = _safe_float(row.get("volume_ratio20"))
        if reclaim_bps < 1.0 and wick_ratio < 0.8 and volume_ratio < 0.55:
            continue
        if abs(_safe_float(row.get("ret_15m_pct"))) < 0.03 and volume_ratio < 0.7 and _safe_float(row["range"]) < 0.03:
            continue

        low_score = (1.0 - min(pos10, 1.0)) * 2.0
        context_score = max(0.0, -_safe_float(row.get("ret_30m_pct"))) * 1.2
        context_score += max(0.0, -_safe_float(row.get("ret_60m_pct"))) * 0.8
        reclaim_score = min(reclaim_bps / 8.0, 2.0)
        volume_score = min(max(volume_ratio, 0.0) / 3.0, 1.5)
        score = low_score + context_score + reclaim_score + volume_score
        if _safe_float(row.get("range_pos_60"), 0.5) > 0.75 and _safe_float(row.get("ret_60m_pct")) > 0.30:
            score += 0.8
        if score < min_score:
            continue

        signal_time = pd.Timestamp(row["open_time_utc"])
        entry_row = df.iloc[idx + 1]
        entry_open = _safe_float(entry_row["open"])
        target, diff = _nearest_target(signal_time, targets)
        raw.append(
            {
                "signal_idx": idx,
                "anchor_idx": anchor_idx,
                "entry_idx": idx + 1,
                "anchor_age_bars": int(anchor_age),
                "score": round(float(score), 6),
                "anchor_time_utc": _fmt_ts(pd.Timestamp(anchor["open_time_utc"])),
                "anchor_low_price": _safe_float(anchor["low"]),
                "signal_time_utc": _fmt_ts(signal_time),
                "entry_time_utc": _fmt_ts(pd.Timestamp(entry_row["open_time_utc"])),
                "entry_open_price": entry_open,
                "entry_price_plus_5bps": entry_open * (1.0 + float(slippage_bps) / 10000.0),
                "slippage_bps": float(slippage_bps),
                "suggested_type": _suggested_type(row),
                "candidate_reason": "recent_local_low_anchor_with_reclaim_or_absorption",
                "risk_flags": _risk_flags(row, anchor_age),
                "nearest_manual_target": target.target_id if target else None,
                "nearest_manual_target_type": target.target_type if target else None,
                "signal_diff_minutes_to_nearest_target": diff,
                "matched_manual_target_within_3m": bool(diff is not None and abs(diff) <= 3),
                "features_at_signal_close": {
                    "range_pos_10": _safe_float(row.get("range_pos_10")),
                    "range_pos_20": _safe_float(row.get("range_pos_20")),
                    "range_pos_60": _safe_float(row.get("range_pos_60")),
                    "range_pos_120": _safe_float(row.get("range_pos_120")),
                    "ret_15m_pct": _safe_float(row.get("ret_15m_pct")),
                    "ret_30m_pct": _safe_float(row.get("ret_30m_pct")),
                    "ret_60m_pct": _safe_float(row.get("ret_60m_pct")),
                    "volume_ratio20": volume_ratio,
                    "lower_wick_to_body": wick_ratio,
                    "reclaim_from_anchor_low_bps": reclaim_bps,
                    "rsi14": _safe_float(row.get("rsi14"), 50.0),
                    "macd_hist": _safe_float(row.get("macd_hist")),
                    "range_compression20": _safe_float(row.get("range_compression20"), 1.0),
                },
                "label": "user_pending",
            }
        )

    selected: list[dict[str, Any]] = []
    for item in sorted(raw, key=lambda x: x["signal_time_utc"]):
        if selected:
            prev_time = pd.Timestamp(selected[-1]["signal_time_utc"])
            item_time = pd.Timestamp(item["signal_time_utc"])
            if (item_time - prev_time).total_seconds() / 60.0 <= cooldown_minutes:
                if float(item["score"]) > float(selected[-1]["score"]):
                    selected[-1] = item
                continue
        selected.append(item)

    for number, item in enumerate(selected, 1):
        item["candidate_id"] = f"LA{number:03d}"
    return selected


def _match_summary(candidates: list[dict[str, Any]], targets: list[ManualTarget]) -> dict[str, Any]:
    per_target: list[dict[str, Any]] = []
    for target in targets:
        nearest = min(
            candidates,
            key=lambda item: abs((pd.Timestamp(item["signal_time_utc"]) - target.signal_time).total_seconds()),
            default=None,
        )
        if nearest is None:
            per_target.append(
                {
                    "target_id": target.target_id,
                    "target_signal_time_utc": _fmt_ts(target.signal_time),
                    "nearest_candidate_id": None,
                    "diff_minutes": None,
                    "hit_within_3m": False,
                }
            )
            continue
        diff = int(round((pd.Timestamp(nearest["signal_time_utc"]) - target.signal_time).total_seconds() / 60.0))
        per_target.append(
            {
                "target_id": target.target_id,
                "target_type": target.target_type,
                "target_signal_time_utc": _fmt_ts(target.signal_time),
                "nearest_candidate_id": nearest["candidate_id"],
                "nearest_candidate_signal_time_utc": nearest["signal_time_utc"],
                "diff_minutes": diff,
                "hit_within_3m": abs(diff) <= 3,
                "hit_exact": diff == 0,
            }
        )
    return {
        "manual_targets": len(targets),
        "candidate_count": len(candidates),
        "hits_exact": sum(1 for item in per_target if item["hit_exact"]),
        "hits_within_3m": sum(1 for item in per_target if item["hit_within_3m"]),
        "missed_targets_within_3m": [item["target_id"] for item in per_target if not item["hit_within_3m"]],
        "per_target": per_target,
    }


def _draw_candles(ax: Any, df: pd.DataFrame, timeframe: str, *, alpha: float = 0.95, linewidth: float = 0.45) -> None:
    x = mdates.date2num(df["open_time_utc"].dt.tz_convert(None).to_numpy())
    width = _bar_width_days(timeframe)
    up_color = "#26a69a"
    down_color = "#ef5350"
    wick_color = "#cfd8dc"
    ax.vlines(x, df["low"], df["high"], color=wick_color, linewidth=max(linewidth, 0.35), alpha=0.82, zorder=1)
    for i, row in df.iterrows():
        open_px = float(row["open"])
        close_px = float(row["close"])
        lower = min(open_px, close_px)
        height = max(abs(close_px - open_px), 1e-8)
        color = up_color if close_px >= open_px else down_color
        ax.add_patch(
            Rectangle(
                (x[i] - width / 2, lower),
                width,
                height,
                facecolor=color,
                edgecolor=color,
                linewidth=linewidth,
                alpha=alpha,
                zorder=2,
            )
        )


def _style_axis(ax: Any) -> None:
    ax.set_facecolor("#101418")
    ax.grid(color="#2f3a40", alpha=0.45, linewidth=0.6)
    ax.tick_params(colors="#e0e0e0")
    for spine in ax.spines.values():
        spine.set_color("#3a444b")


def render_full_day(
    *,
    df: pd.DataFrame,
    candidates: list[dict[str, Any]],
    targets: list[ManualTarget],
    symbol: str,
    timeframe: str,
    day: str,
    out_path: Path,
) -> None:
    fig, (ax_price, ax_vol) = plt.subplots(2, 1, figsize=(24, 11), sharex=True, gridspec_kw={"height_ratios": [4.3, 1.2]})
    fig.patch.set_facecolor("#101418")
    _style_axis(ax_price)
    _style_axis(ax_vol)
    _draw_candles(ax_price, df, timeframe, linewidth=0.35)
    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(df["open"], df["close"])]
    ax_vol.bar(df["open_time_utc"].dt.tz_convert(None), df["volume"], width=_bar_width_days(timeframe), color=colors, alpha=0.72)

    for item in candidates:
        signal_time = pd.Timestamp(item["signal_time_utc"]).tz_convert(None)
        entry_time = pd.Timestamp(item["entry_time_utc"]).tz_convert(None)
        anchor_time = pd.Timestamp(item["anchor_time_utc"]).tz_convert(None)
        anchor_low = float(item["anchor_low_price"])
        entry_price = float(item["entry_price_plus_5bps"])
        matched = bool(item["matched_manual_target_within_3m"])
        color = "#00e676" if matched else "#26c6da"
        ax_price.axvline(signal_time, color=color, alpha=0.18 if matched else 0.08, linewidth=1.0, zorder=0)
        ax_price.scatter([anchor_time], [anchor_low], s=14 if matched else 8, color="#ff5252", alpha=0.85, zorder=5)
        ax_price.scatter([entry_time], [entry_price], marker="^", s=46 if matched else 24, color=color, edgecolors="#0b0f12", linewidths=0.45, alpha=0.95, zorder=6)
        if matched:
            label = f"{item['candidate_id']}->{item['nearest_manual_target']}"
            ax_price.annotate(label, xy=(entry_time, entry_price), xytext=(2, 8), textcoords="offset points", color=color, fontsize=7)

    for target in targets:
        ax_price.axvline(target.signal_time.tz_convert(None), color="#ffd54f", alpha=0.32, linewidth=0.8, zorder=0)
        ax_price.text(target.signal_time.tz_convert(None), ax_price.get_ylim()[0], target.target_id, color="#ffd54f", fontsize=7, rotation=90, va="bottom")

    start = pd.Timestamp(f"{day} 00:00:00")
    end = start + pd.Timedelta(days=1)
    ax_price.set_xlim(start.to_pydatetime(), end.to_pydatetime())
    ax_price.set_title(
        f"{symbol} {timeframe} {day} | LOW_ANCHOR_ENTRY_SUGGESTER_V0 | green=near M target | cyan=extra | NO ML/OPTUNA",
        color="white",
        fontsize=14,
    )
    ax_price.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    ax_vol.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 3)))
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path, dpi=155, facecolor=fig.get_facecolor())
    plt.close(fig)


def render_target_zoom_sheet(
    *,
    df: pd.DataFrame,
    candidates: list[dict[str, Any]],
    targets: list[ManualTarget],
    symbol: str,
    timeframe: str,
    day: str,
    out_path: Path,
) -> None:
    rows = 5
    cols = 4
    fig, axes = plt.subplots(rows, cols, figsize=(22, 18), sharex=False)
    fig.patch.set_facecolor("#101418")
    flat = list(axes.flatten())
    by_target = _match_summary(candidates, targets)["per_target"]
    candidate_by_id = {item["candidate_id"]: item for item in candidates}
    for ax, target_info in zip(flat, by_target):
        _style_axis(ax)
        target = next(item for item in targets if item.target_id == target_info["target_id"])
        candidate = candidate_by_id.get(str(target_info["nearest_candidate_id"]))
        center = target.signal_time if candidate is None else pd.Timestamp(candidate["signal_time_utc"])
        start = center - pd.Timedelta(minutes=22)
        end = center + pd.Timedelta(minutes=34)
        win = df[(df["open_time_utc"] >= start) & (df["open_time_utc"] <= end)].reset_index(drop=True)
        _draw_candles(ax, win, timeframe, linewidth=0.55)
        ax.axvline(target.signal_time.tz_convert(None), color="#ffd54f", linewidth=1.3, alpha=0.72)
        if candidate is not None:
            anchor_time = pd.Timestamp(candidate["anchor_time_utc"]).tz_convert(None)
            signal_time = pd.Timestamp(candidate["signal_time_utc"]).tz_convert(None)
            entry_time = pd.Timestamp(candidate["entry_time_utc"]).tz_convert(None)
            anchor_low = float(candidate["anchor_low_price"])
            entry_price = float(candidate["entry_price_plus_5bps"])
            color = "#00e676" if bool(target_info["hit_within_3m"]) else "#26c6da"
            ax.axvline(signal_time, color=color, linewidth=1.0, alpha=0.6)
            ax.scatter([anchor_time], [anchor_low], s=70, color="#ff5252", edgecolors="#0b0f12", zorder=5)
            ax.scatter([entry_time], [entry_price], marker="^", s=110, color=color, edgecolors="#0b0f12", zorder=6)
            ax.annotate(
                f"{candidate['candidate_id']} entry {_fmt_minute(pd.Timestamp(candidate['entry_time_utc']))}",
                xy=(entry_time, entry_price),
                xytext=(6, 10),
                textcoords="offset points",
                color=color,
                fontsize=8,
                arrowprops={"arrowstyle": "->", "color": color, "linewidth": 1.0},
            )
            diff = target_info["diff_minutes"]
            title = f"{target.target_id} {target.target_type} | nearest {candidate['candidate_id']} diff {diff:+}m"
        else:
            title = f"{target.target_id} {target.target_type} | no candidate"
        ax.set_title(title, color="white", fontsize=9)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.tick_params(axis="x", labelrotation=25)
    for ax in flat[len(by_target) :]:
        ax.axis("off")
        ax.set_facecolor("#101418")
    fig.suptitle(f"{symbol} {timeframe} {day} | nearest auto low-anchor candidate for each M target | yellow=manual signal", color="white", fontsize=15)
    fig.tight_layout(rect=[0, 0, 1, 0.975])
    fig.savefig(out_path, dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def write_csv(path: Path, candidates: list[dict[str, Any]]) -> None:
    columns = [
        "candidate_id",
        "anchor_time_utc",
        "anchor_low_price",
        "signal_time_utc",
        "entry_time_utc",
        "entry_open_price",
        "entry_price_plus_5bps",
        "score",
        "suggested_type",
        "nearest_manual_target",
        "signal_diff_minutes_to_nearest_target",
        "matched_manual_target_within_3m",
        "label",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for item in candidates:
            writer.writerow({col: item.get(col) for col in columns})


def build_report(path: Path, payload: dict[str, Any]) -> None:
    summary = payload["target_match_summary"]
    lines = [
        "# LOW_ANCHOR_ENTRY_SUGGESTER_V0 seed-day review",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Пункт рельсов: `LOW_ANCHOR_ENTRY_SUGGESTER_V0_NO_ML_NO_OPTUNA`.",
        "",
        "Назначение: автоматом предложить low-anchor входы на seed-дне, чтобы пользователь проверял готовые точки, а не искал весь день руками.",
        "",
        "## Итог V0",
        "",
        f"- День: `{payload['day_utc']}`.",
        f"- Symbol/timeframe: `{payload['symbol']} {payload['timeframe']}`.",
        f"- Кандидатов после cooldown/score filter: `{summary['candidate_count']}`.",
        f"- Ручных целей M: `{summary['manual_targets']}`.",
        f"- Exact hits по signal time: `{summary['hits_exact']}`.",
        f"- Hits в пределах `±3m`: `{summary['hits_within_3m']}`.",
        f"- Пропуски `±3m`: `{', '.join(summary['missed_targets_within_3m']) or 'нет'}`.",
        "",
        "## Артефакты",
        "",
        f"- Full-day PNG: `{payload['artifacts']['full_day_png']}`.",
        f"- Target zoom sheet: `{payload['artifacts']['target_zoom_sheet_png']}`.",
        f"- JSON: `{payload['artifacts']['json']}`.",
        f"- CSV: `{payload['artifacts']['csv']}`.",
        "",
        "## Границы",
        "",
        "- Это не стратегия и не торговый сигнал.",
        "- Это не Optuna и не ML.",
        "- Features считаются на `signal close` или раньше.",
        "- `entry_time_utc` используется только для цены исполнения `next open + 5 bps`, не как feature выбора входа.",
        "- Следующий шаг: пользовательский visual review `да / нет / сдвинуть / дубль / рано / поздно`.",
        "",
        "## Что смотреть глазами",
        "",
        "На full-day PNG зеленые треугольники возле `M##` показывают, где V0 попал рядом с ручной целью. Голубые треугольники — лишние low-кандидаты, потенциальные anti-примеры для будущего датасета.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build low-anchor entry suggestions for visual target-led review.")
    parser.add_argument("--day", default="2026-05-14")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--slippage-bps", type=float, default=5.0)
    parser.add_argument("--anchor-lookback", type=int, default=12)
    parser.add_argument("--max-anchor-age", type=int, default=3)
    parser.add_argument("--cooldown-minutes", type=int, default=4)
    parser.add_argument("--min-score", type=float, default=2.5)
    parser.add_argument("--target-ledger", default="reports/final_review/visual_entry_v3/fresh_target_led/target_ledger_SOLUSDT_1m_2026-05-14_M01_M19.json")
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_entry_suggester_v0")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    source = _source_csv(root, args.day, args.timeframe, args.symbol)
    df = _add_features(_load_ohlcv(source))
    targets = _load_targets(root / args.target_ledger)
    candidates = build_candidates(
        df,
        targets=targets,
        anchor_lookback=args.anchor_lookback,
        max_anchor_age=args.max_anchor_age,
        cooldown_minutes=args.cooldown_minutes,
        min_score=args.min_score,
        slippage_bps=args.slippage_bps,
    )

    out_dir = root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V0_20260514.json"
    csv_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V0_20260514.csv"
    report_path = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V0_20260514_RU.md"
    full_day_png = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V0_full_day_20260514.png"
    target_zoom_png = out_dir / "LOW_ANCHOR_ENTRY_SUGGESTER_V0_target_nearest_zoom_20260514.png"

    summary = _match_summary(candidates, targets)
    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "rail_point": "LOW_ANCHOR_ENTRY_SUGGESTER_V0_NO_ML_NO_OPTUNA",
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "day_utc": args.day,
        "source_csv": str(source.relative_to(root)).replace("\\", "/"),
        "manual_target_ledger": args.target_ledger.replace("\\", "/"),
        "params": {
            "slippage_bps": args.slippage_bps,
            "anchor_lookback": args.anchor_lookback,
            "max_anchor_age": args.max_anchor_age,
            "cooldown_minutes": args.cooldown_minutes,
            "min_score": args.min_score,
            "target_match_tolerance_minutes": 3,
        },
        "no_lookahead_boundary": {
            "candidate_features_end_at": "signal_candle_close",
            "entry_rule": "next_open_after_signal_close",
            "entry_open_price_is_execution_price_only": True,
            "forbidden_features": ["future_return", "tp_sl", "mfe_mae", "entry_candle_ohlcv_for_selection"],
        },
        "target_match_summary": summary,
        "candidates": candidates,
        "artifacts": {
            "json": str(json_path.relative_to(root)).replace("\\", "/"),
            "csv": str(csv_path.relative_to(root)).replace("\\", "/"),
            "report_ru": str(report_path.relative_to(root)).replace("\\", "/"),
            "full_day_png": str(full_day_png.relative_to(root)).replace("\\", "/"),
            "target_zoom_sheet_png": str(target_zoom_png.relative_to(root)).replace("\\", "/"),
        },
        "optuna_allowed": False,
        "ml_allowed": False,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(csv_path, candidates)
    build_report(report_path, payload)
    render_full_day(df=df, candidates=candidates, targets=targets, symbol=args.symbol, timeframe=args.timeframe, day=args.day, out_path=full_day_png)
    render_target_zoom_sheet(df=df, candidates=candidates, targets=targets, symbol=args.symbol, timeframe=args.timeframe, day=args.day, out_path=target_zoom_png)
    print(json.dumps(payload["artifacts"], ensure_ascii=False, indent=2))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
