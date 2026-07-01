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
import numpy as np
import pandas as pd

from mlbotnav.visual_entry_low_anchor_suggester import (
    _add_features,
    _bar_width_days,
    _draw_candles,
    _fmt_minute,
    _fmt_ts,
    _load_ohlcv,
    _source_csv,
    _style_axis,
    build_candidates,
)


STATUS = "LOW_ANCHOR_TRANSFER_REVIEW_V0_DAY_20260515_READY_NO_ML_NO_OPTUNA"
RAIL_POINT = "LOW_ANCHOR_TRANSFER_DAY_REVIEW_NO_ML_NO_OPTUNA"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def _add_transfer_features(df: pd.DataFrame) -> pd.DataFrame:
    out = _add_features(df)
    for window in [60, 180]:
        out[f"distance_from_low_{window}_bps"] = (out["close"] - out[f"rolling_low_{window}"]) / out["close"] * 10000.0
        out[f"room_to_high_{window}_bps"] = (out[f"rolling_high_{window}"] - out["close"]) / out["close"] * 10000.0
    out["body"] = (out["close"] - out["open"]).abs()
    out["candle_range"] = out["high"] - out["low"]
    out["close_pos_candle"] = (out["close"] - out["low"]) / out["candle_range"].replace(0, np.nan)
    out["red_signal"] = out["close"] < out["open"]
    out["green_signal"] = out["close"] >= out["open"]
    out["new_low_count_20"] = 0
    out["lower_low_streak_5"] = 0
    for idx in range(len(out)):
        start20 = max(0, idx - 19)
        new_low_count = 0
        for probe_idx in range(start20, idx + 1):
            local_start = max(0, probe_idx - 4)
            local = out.iloc[local_start : probe_idx + 1]
            if float(out.iloc[probe_idx]["low"]) <= float(local["low"].min()) + 1e-12:
                new_low_count += 1
        streak = 0
        for probe_idx in range(idx, max(0, idx - 5), -1):
            if probe_idx <= 0:
                break
            if float(out.iloc[probe_idx]["low"]) < float(out.iloc[probe_idx - 1]["low"]):
                streak += 1
            else:
                break
        out.at[idx, "new_low_count_20"] = int(new_low_count)
        out.at[idx, "lower_low_streak_5"] = int(streak)
    return out


def _row_at_idx(features: pd.DataFrame, idx: int) -> pd.Series:
    if idx < 0 or idx >= len(features):
        raise IndexError(idx)
    return features.iloc[idx]


def _votes(row: pd.Series, candidate: dict[str, Any]) -> tuple[int, list[str], list[str], str]:
    score = 0
    pass_votes: list[str] = []
    risk_votes: list[str] = []

    range_pos_60 = _safe_float(row.get("range_pos_60"), 1.0)
    range_pos_180 = _safe_float(row.get("range_pos_180"), 1.0)
    distance_low_60 = _safe_float(row.get("distance_from_low_60_bps"), 999.0)
    room_high_60 = _safe_float(row.get("room_to_high_60_bps"), 0.0)
    room_high_180 = _safe_float(row.get("room_to_high_180_bps"), 0.0)
    ret30 = _safe_float(row.get("ret_30m_pct"))
    ret60 = _safe_float(row.get("ret_60m_pct"))
    volume_ratio = _safe_float(row.get("volume_ratio20"))
    lower_wick = _safe_float(row.get("lower_wick_to_body"))
    close_pos = _safe_float(row.get("close_pos_candle"))
    reclaim_bps = _safe_float(candidate.get("features_at_signal_close", {}).get("reclaim_from_anchor_low_bps"))
    range_ratio = _safe_float(row.get("range_compression20"), 1.0)
    lower_low_streak = int(_safe_float(row.get("lower_low_streak_5")))
    new_low_count = int(_safe_float(row.get("new_low_count_20")))

    if range_pos_60 <= 0.24 or range_pos_180 <= 0.28 or distance_low_60 <= 18.0:
        score += 3
        pass_votes.append("LOW_IN_RANGE")
    if room_high_60 >= 42.0 or room_high_180 >= 65.0:
        score += 3
        pass_votes.append("ROOM_TO_RECENT_HIGH")
    elif room_high_60 >= 30.0:
        score += 1
        pass_votes.append("SOME_ROOM_TO_HIGH")
    if ret60 <= -0.32 or ret30 <= -0.18:
        score += 2
        pass_votes.append("DIP_CONTEXT")
    if lower_wick >= 0.55 or close_pos >= 0.55 or reclaim_bps >= 3.0:
        score += 2
        pass_votes.append("WICK_OR_RECLAIM")
    if volume_ratio >= 1.25:
        score += 1
        pass_votes.append("VOLUME_PRESENT")
    if range_ratio >= 0.85:
        score += 1
        pass_votes.append("RANGE_NOT_TINY")

    if lower_low_streak >= 4 and lower_wick < 0.55 and close_pos < 0.45:
        score -= 4
        risk_votes.append("FALLING_KNIFE_NO_RECLAIM")
    if room_high_60 < 24.0 and range_pos_60 > 0.22:
        score -= 3
        risk_votes.append("LOW_ROOM_SHALLOW_CONTEXT")
    if new_low_count >= 8 and reclaim_bps < 3.0:
        score -= 2
        risk_votes.append("NOISY_LOW_CHAIN")
    if volume_ratio < 0.75 and range_ratio < 0.75:
        score -= 2
        risk_votes.append("LOW_PARTICIPATION")

    if ret60 <= -0.55 and range_pos_60 <= 0.22:
        label = "DEEP_CAPITULATION_LOW"
    elif ret30 <= -0.20 and room_high_60 >= 35.0:
        label = "SUPPORT_RETEST_LOW"
    elif reclaim_bps >= 4.0 and volume_ratio >= 1.15:
        label = "HOT_RECLAIM_SUPPORT"
    elif room_high_60 >= 45.0 and range_pos_60 <= 0.38:
        label = "SWING_LOW_RECLAIM"
    else:
        label = "LOW_ANCHOR_REVIEW"
    return score, pass_votes, risk_votes, label


def _selection_key(item: dict[str, Any]) -> tuple[float, float, float, float, float]:
    features = item.get("features_at_signal_close", {})
    return (
        float(item.get("transfer_score") or 0),
        float(features.get("room_to_high_60_bps") or 0),
        float(features.get("volume_ratio20") or 0),
        float(features.get("reclaim_from_anchor_low_bps") or 0),
        -float(features.get("range_pos_60") or 1.0),
    )


def _filter_transfer_candidates(
    features: pd.DataFrame,
    candidates: list[dict[str, Any]],
    *,
    min_transfer_score: int,
    review_cooldown_minutes: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        row = _row_at_idx(features, int(candidate["signal_idx"]))
        score, pass_votes, risk_votes, label = _votes(row, candidate)
        if score < min_transfer_score:
            continue
        item = dict(candidate)
        item["candidate_id"] = ""
        item["transfer_score"] = int(score)
        item["transfer_pass_votes"] = pass_votes
        item["transfer_risk_votes"] = risk_votes
        item["transfer_type"] = label
        item["review_status"] = "pending_user_visual_review"
        item["features_at_signal_close"].update(
            {
                "range_pos_180": _safe_float(row.get("range_pos_180")),
                "distance_from_low_60_bps": _safe_float(row.get("distance_from_low_60_bps")),
                "room_to_high_60_bps": _safe_float(row.get("room_to_high_60_bps")),
                "room_to_high_180_bps": _safe_float(row.get("room_to_high_180_bps")),
                "close_pos_candle": _safe_float(row.get("close_pos_candle")),
                "new_low_count_20": int(_safe_float(row.get("new_low_count_20"))),
                "lower_low_streak_5": int(_safe_float(row.get("lower_low_streak_5"))),
            }
        )
        rows.append(item)

    selected: list[dict[str, Any]] = []
    for item in sorted(rows, key=lambda x: (x["signal_time_utc"], -int(x["transfer_score"]))):
        item_time = pd.Timestamp(item["signal_time_utc"])
        if selected:
            prev_time = pd.Timestamp(selected[-1]["signal_time_utc"])
            if (item_time - prev_time).total_seconds() / 60.0 <= review_cooldown_minutes:
                if _selection_key(item) > _selection_key(selected[-1]):
                    selected[-1] = item
                continue
        selected.append(item)

    for number, item in enumerate(selected, 1):
        item["candidate_id"] = f"T15L{number:02d}"
    return selected


def _render_full_day(*, df: pd.DataFrame, candidates: list[dict[str, Any]], symbol: str, timeframe: str, day: str, out_path: Path) -> None:
    fig, (ax_price, ax_vol) = plt.subplots(2, 1, figsize=(28, 12), sharex=True, gridspec_kw={"height_ratios": [4.4, 1.15]})
    fig.patch.set_facecolor("#101418")
    _style_axis(ax_price)
    _style_axis(ax_vol)
    _draw_candles(ax_price, df, timeframe, linewidth=0.34)
    colors = ["#26a69a" if c >= o else "#ef5350" for o, c in zip(df["open"], df["close"])]
    ax_vol.bar(df["open_time_utc"].dt.tz_convert(None), df["volume"], width=_bar_width_days(timeframe), color=colors, alpha=0.72)

    for item in candidates:
        signal_time = pd.Timestamp(item["signal_time_utc"]).tz_convert(None)
        entry_time = pd.Timestamp(item["entry_time_utc"]).tz_convert(None)
        anchor_time = pd.Timestamp(item["anchor_time_utc"]).tz_convert(None)
        anchor_low = float(item["anchor_low_price"])
        entry_price = float(item["entry_price_plus_5bps"])
        score = int(item["transfer_score"])
        color = "#00e676" if score >= 9 else "#26c6da"
        ax_price.axvline(signal_time, color=color, alpha=0.23, linewidth=1.1, zorder=0)
        ax_price.scatter([anchor_time], [anchor_low], s=24, color="#ff5252", edgecolors="#0b0f12", linewidths=0.4, zorder=5)
        ax_price.scatter([entry_time], [entry_price], marker="^", s=70, color=color, edgecolors="white", linewidths=0.45, zorder=6)
        ax_price.annotate(
            item["candidate_id"],
            xy=(entry_time, entry_price),
            xytext=(2, 9),
            textcoords="offset points",
            color=color,
            fontsize=8,
            arrowprops={"arrowstyle": "-", "color": color, "linewidth": 0.7},
        )

    start = pd.Timestamp(f"{day}T00:00:00")
    end = start + pd.Timedelta(days=1)
    ax_price.set_xlim(start.to_pydatetime(), end.to_pydatetime())
    ax_price.set_title(
        f"{symbol} {timeframe} {day} | transfer review V0 significant long lows | green=strong review | cyan=review | NO ML/OPTUNA",
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


def _render_zoom_pages(*, df: pd.DataFrame, candidates: list[dict[str, Any]], timeframe: str, day: str, out_dir: Path, page_size: int) -> list[Path]:
    page_paths: list[Path] = []
    cols = 3
    rows_per_page = ceil(page_size / cols)
    pages = ceil(len(candidates) / page_size) if candidates else 0
    for page_idx in range(pages):
        chunk = candidates[page_idx * page_size : (page_idx + 1) * page_size]
        fig, axes = plt.subplots(rows_per_page, cols, figsize=(24, 4.9 * rows_per_page), sharex=False)
        fig.patch.set_facecolor("#101418")
        flat = list(axes.flatten() if hasattr(axes, "flatten") else [axes])
        for ax, item in zip(flat, chunk):
            _style_axis(ax)
            signal = pd.Timestamp(item["signal_time_utc"])
            start = signal - pd.Timedelta(minutes=24)
            end = signal + pd.Timedelta(minutes=38)
            win = df[(df["open_time_utc"] >= start) & (df["open_time_utc"] <= end)].reset_index(drop=True)
            _draw_candles(ax, win, timeframe, linewidth=0.6)

            anchor_time = pd.Timestamp(item["anchor_time_utc"]).tz_convert(None)
            signal_time = signal.tz_convert(None)
            entry_time = pd.Timestamp(item["entry_time_utc"]).tz_convert(None)
            anchor_low = float(item["anchor_low_price"])
            entry_price = float(item["entry_price_plus_5bps"])
            color = "#00e676" if int(item["transfer_score"]) >= 9 else "#26c6da"

            ax.axvline(signal_time, color="#ffd54f", linewidth=1.4, alpha=0.78, zorder=0)
            ax.axvline(entry_time, color=color, linewidth=1.1, alpha=0.58, linestyle="--", zorder=0)
            ax.scatter([anchor_time], [anchor_low], s=64, color="#ff5252", edgecolors="#0b0f12", linewidths=0.5, zorder=5)
            ax.scatter([entry_time], [entry_price], marker="^", s=110, color=color, edgecolors="white", linewidths=0.55, zorder=7)
            ax.annotate(
                f"{item['candidate_id']} LONG\nsignal {_fmt_minute(pd.Timestamp(item['signal_time_utc']))} -> entry {_fmt_minute(pd.Timestamp(item['entry_time_utc']))}\nprice+5bps {entry_price:.5f}",
                xy=(entry_time, entry_price),
                xytext=(8, 18),
                textcoords="offset points",
                color=color,
                fontsize=8,
                arrowprops={"arrowstyle": "->", "color": color, "linewidth": 1.0},
                bbox={"facecolor": "#0b2730", "edgecolor": color, "alpha": 0.74, "boxstyle": "round,pad=0.22"},
            )
            votes = ",".join(item.get("transfer_pass_votes", []))
            risks = ",".join(item.get("transfer_risk_votes", []))
            ax.set_title(
                f"{item['candidate_id']} {item['transfer_type']} | score {item['transfer_score']} | {votes[:60]}",
                color="white",
                fontsize=9,
            )
            if risks:
                ax.text(
                    0.02,
                    0.04,
                    risks[:75],
                    transform=ax.transAxes,
                    color="#ffcc80",
                    fontsize=7,
                    bbox={"facecolor": "#2b2114", "edgecolor": "#ffcc80", "alpha": 0.64, "boxstyle": "round,pad=0.18"},
                )
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            ax.tick_params(axis="x", labelrotation=22)
        for ax in flat[len(chunk) :]:
            ax.axis("off")
            ax.set_facecolor("#101418")
        fig.suptitle(
            f"SOLUSDT 1m {day} | transfer review V0 page {page_idx + 1} | entry-only visual check | NO ML/OPTUNA",
            color="white",
            fontsize=15,
        )
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        path = out_dir / f"LOW_ANCHOR_TRANSFER_REVIEW_V0_ZOOM_PAGE_{page_idx + 1:02d}_{day.replace('-', '')}.png"
        fig.savefig(path, dpi=165, facecolor=fig.get_facecolor())
        plt.close(fig)
        page_paths.append(path)
    return page_paths


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    columns = [
        "candidate_id",
        "transfer_type",
        "transfer_score",
        "anchor_time_utc",
        "anchor_low_price",
        "signal_time_utc",
        "entry_time_utc",
        "entry_open_price",
        "entry_price_plus_5bps",
        "transfer_pass_votes",
        "transfer_risk_votes",
        "review_status",
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
    lines = [
        "# Low Anchor Transfer Review V0: 2026-05-15",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        "Назначение: проверить, переносится ли понимание ручных входов `2026-05-14` на новый день `2026-05-15`.",
        "",
        "Это не стратегия, не scorer, не ML dataset и не Optuna. Это список кандидатов для ручного visual verdict.",
        "",
        "## Граница no-lookahead",
        "",
        "- Используется только закрытая `signal`-свеча и прошлый контекст.",
        "- LONG entry считается на `open` следующей свечи + `5 bps` как execution/control.",
        "- `entry`-свеча не используется для выбора.",
        "- Future return, TP/SL, MFE/MAE не используются.",
        "- EMA не используется как active condition.",
        "",
        "## Итог",
        "",
        f"- День: `{payload['day_utc']}`.",
        f"- Broad low-anchor candidates before learned filter: `{payload['broad_candidate_count']}`.",
        f"- Transfer review candidates: `{payload['candidate_count']}`.",
        f"- Zoom pages: `{payload['pages']}`.",
        "",
        "## Артефакты",
        "",
        f"- Full-day PNG: `{payload['artifacts']['full_day_png']}`.",
    ]
    for idx, page in enumerate(payload["artifacts"]["zoom_pages"], 1):
        lines.append(f"- Zoom page {idx}: `{page}`.")
    lines.extend(
        [
            f"- JSON: `{payload['artifacts']['json']}`.",
            f"- CSV: `{payload['artifacts']['csv']}`.",
            "",
            "## Как давать verdict",
            "",
            "По каждому `T15L##`: `норм`, `нет`, `сдвинуть на N свечей`, `дубль`, `не тот тип`, `оставить possible`.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(
    day: str,
    symbol: str,
    timeframe: str,
    out_dir: Path,
    *,
    slippage_bps: float,
    min_transfer_score: int,
    review_cooldown_minutes: int,
) -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    if not out_dir.is_absolute():
        out_dir = root / out_dir
    source = _source_csv(root, day, timeframe, symbol)
    features = _add_transfer_features(_load_ohlcv(source))
    broad = build_candidates(
        features,
        targets=[],
        anchor_lookback=12,
        max_anchor_age=3,
        cooldown_minutes=4,
        min_score=2.5,
        slippage_bps=slippage_bps,
    )
    candidates = _filter_transfer_candidates(
        features,
        broad,
        min_transfer_score=min_transfer_score,
        review_cooldown_minutes=review_cooldown_minutes,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = day.replace("-", "")
    json_path = out_dir / f"LOW_ANCHOR_TRANSFER_REVIEW_V0_{stamp}.json"
    csv_path = out_dir / f"LOW_ANCHOR_TRANSFER_REVIEW_V0_{stamp}.csv"
    report_path = out_dir / f"LOW_ANCHOR_TRANSFER_REVIEW_V0_{stamp}_RU.md"
    full_day_png = out_dir / f"LOW_ANCHOR_TRANSFER_REVIEW_V0_FULL_DAY_{stamp}.png"

    _render_full_day(df=features, candidates=candidates, symbol=symbol, timeframe=timeframe, day=day, out_path=full_day_png)
    zoom_pages = _render_zoom_pages(df=features, candidates=candidates, timeframe=timeframe, day=day, out_dir=out_dir, page_size=12)

    payload = {
        "schema_version": 1,
        "status": STATUS,
        "created_utc": _utc_now(),
        "rail_point": RAIL_POINT,
        "source_learning_day": "2026-05-14",
        "day_utc": day,
        "symbol": symbol,
        "timeframe": timeframe,
        "source_csv": str(source.relative_to(root)).replace("\\", "/"),
        "broad_candidate_count": len(broad),
        "candidate_count": len(candidates),
        "pages": len(zoom_pages),
        "params": {
            "slippage_bps": slippage_bps,
            "broad_anchor_lookback": 12,
            "broad_max_anchor_age": 3,
            "broad_cooldown_minutes": 4,
            "broad_min_score": 2.5,
            "min_transfer_score": min_transfer_score,
            "review_cooldown_minutes": review_cooldown_minutes,
            "ema_active_condition": False,
        },
        "no_lookahead_boundary": {
            "candidate_features_end_at": "signal_candle_close",
            "entry_rule": "next_open_after_signal_close",
            "entry_open_price_is_execution_price_only": True,
            "forbidden_features": ["future_return", "tp_sl", "mfe_mae", "entry_candle_ohlcv_for_selection"],
            "optuna_allowed": False,
            "ml_allowed": False,
        },
        "review_choices_ru": ["норм", "нет", "сдвинуть на N свечей", "дубль", "не тот тип", "оставить possible"],
        "candidates": candidates,
        "artifacts": {
            "json": str(json_path.relative_to(root)).replace("\\", "/"),
            "csv": str(csv_path.relative_to(root)).replace("\\", "/"),
            "report_ru": str(report_path.relative_to(root)).replace("\\", "/"),
            "full_day_png": str(full_day_png.relative_to(root)).replace("\\", "/"),
            "zoom_pages": [str(path.relative_to(root)).replace("\\", "/") for path in zoom_pages],
        },
        "optuna_allowed": False,
        "ml_allowed": False,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_csv(csv_path, candidates)
    _write_report(report_path, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Build transfer visual review candidates for a fresh day.")
    parser.add_argument("--day", default="2026-05-15")
    parser.add_argument("--symbol", default="SOLUSDT")
    parser.add_argument("--timeframe", default="1m")
    parser.add_argument("--slippage-bps", type=float, default=5.0)
    parser.add_argument("--min-transfer-score", type=int, default=6)
    parser.add_argument("--review-cooldown-minutes", type=int, default=24)
    parser.add_argument(
        "--out-dir",
        default="reports/final_review/visual_entry_v3/fresh_target_led/low_anchor_transfer_review_v0/day_20260515",
    )
    args = parser.parse_args()
    payload = run(
        day=args.day,
        symbol=args.symbol,
        timeframe=args.timeframe,
        out_dir=Path(args.out_dir),
        slippage_bps=float(args.slippage_bps),
        min_transfer_score=int(args.min_transfer_score),
        review_cooldown_minutes=int(args.review_cooldown_minutes),
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "day_utc": payload["day_utc"],
                "broad_candidate_count": payload["broad_candidate_count"],
                "candidate_count": payload["candidate_count"],
                "pages": payload["pages"],
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
