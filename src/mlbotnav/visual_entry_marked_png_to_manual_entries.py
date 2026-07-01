from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from PIL import Image


@dataclass(frozen=True)
class RedMarkComponent:
    pixels: int
    x_min: int
    x_max: int
    y_min: int
    y_max: int
    x_center: float
    y_center: float


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _format_utc(value: Any) -> str:
    return pd.Timestamp(value).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def _bar_width_days(timeframe: str) -> float:
    if timeframe.endswith("m"):
        return (int(timeframe[:-1]) / (24 * 60)) * 0.8
    return (1 / (24 * 60)) * 0.8


def _load_core(source_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(source_csv)
    df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], utc=True, errors="coerce", format="mixed")
    df = df.dropna(subset=["open_time_utc"]).sort_values("open_time_utc").reset_index(drop=True)
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    return df


def detect_red_marks(marked_png: Path, *, max_y: int = 640) -> list[RedMarkComponent]:
    image = Image.open(marked_png).convert("RGB")
    arr = np.asarray(image)
    red = arr[:, :, 0].astype(np.int16)
    green = arr[:, :, 1].astype(np.int16)
    blue = arr[:, :, 2].astype(np.int16)
    mask = (red > 120) & ((red - np.maximum(green, blue)) > 50) & (green < 110) & (blue < 110)
    height, width = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    components: list[RedMarkComponent] = []

    for y in range(min(height, max_y)):
        candidates = np.where(mask[y] & ~seen[y])[0]
        for start_x in candidates:
            if seen[y, start_x] or not mask[y, start_x]:
                continue
            queue: deque[tuple[int, int]] = deque([(int(start_x), int(y))])
            seen[y, start_x] = True
            points: list[tuple[int, int]] = []
            while queue:
                x, yy = queue.popleft()
                points.append((x, yy))
                for nx in (x - 1, x, x + 1):
                    for ny in (yy - 1, yy, yy + 1):
                        if nx < 0 or ny < 0 or nx >= width or ny >= height:
                            continue
                        if seen[ny, nx] or not mask[ny, nx]:
                            continue
                        seen[ny, nx] = True
                        queue.append((nx, ny))
            if len(points) < 25:
                continue
            pts = np.asarray(points)
            x_min = int(pts[:, 0].min())
            x_max = int(pts[:, 0].max())
            y_min = int(pts[:, 1].min())
            y_max = int(pts[:, 1].max())
            box_w = x_max - x_min + 1
            box_h = y_max - y_min + 1
            if y_max > max_y:
                continue
            # User arrows are compact red arrowheads/short strokes. Red candles are
            # either very thin or tall; text is usually too wide.
            if not (8 <= box_w <= 32 and 5 <= box_h <= 24):
                continue
            components.append(
                RedMarkComponent(
                    pixels=int(len(points)),
                    x_min=x_min,
                    x_max=x_max,
                    y_min=y_min,
                    y_max=y_max,
                    x_center=float(pts[:, 0].mean()),
                    y_center=float(pts[:, 1].mean()),
                )
            )
    return sorted(components, key=lambda item: item.x_center)


def pixel_x_to_time(*, x: float, date_utc: str, x_utc_0000: float, px_per_hour: float) -> pd.Timestamp:
    minutes = round(((float(x) - float(x_utc_0000)) / float(px_per_hour)) * 60.0)
    return pd.Timestamp(f"{date_utc}T00:00:00Z") + pd.Timedelta(minutes=int(minutes))


def _snap_to_existing_bar(df: pd.DataFrame, ts: pd.Timestamp) -> int | None:
    if df.empty:
        return None
    start = pd.Timestamp(df.iloc[0]["open_time_utc"])
    idx = int(round((ts - start) / pd.Timedelta(minutes=1)))
    if idx < 0 or idx >= len(df):
        return None
    return idx


def build_manual_entries(
    *,
    seed_json: Path,
    marked_png: Path,
    out_dir: Path,
    dataset_role: str,
    x_utc_0000: float,
    px_per_hour: float,
    slippage_bps: float = 5.0,
) -> tuple[dict[str, Any], Path]:
    seed = json.loads(seed_json.read_text(encoding="utf-8"))
    source_csv = Path(seed["source_csv"])
    df = _load_core(source_csv)
    date_utc = str(seed["date_utc"])
    copied_png = out_dir / f"manual_markup_user_marked_{seed['symbol']}_{seed['timeframe']}_{date_utc}_{dataset_role}.png"
    out_dir.mkdir(parents=True, exist_ok=True)
    if Path(marked_png).resolve() != copied_png.resolve():
        shutil.copy2(marked_png, copied_png)

    components = detect_red_marks(copied_png)
    slip = float(slippage_bps) / 10_000.0
    entries: list[dict[str, Any]] = []
    for number, comp in enumerate(components, 1):
        signal_ts = pixel_x_to_time(
            x=comp.x_center,
            date_utc=date_utc,
            x_utc_0000=x_utc_0000,
            px_per_hour=px_per_hour,
        )
        signal_idx = _snap_to_existing_bar(df, signal_ts)
        if signal_idx is None or signal_idx + 1 >= len(df):
            continue
        signal_row = df.iloc[signal_idx]
        entry_row = df.iloc[signal_idx + 1]
        entry_open = float(entry_row["open"])
        entries.append(
            {
                "entry_id": f"ME_{date_utc.replace('-', '')}_{dataset_role}_{number:03d}_LONG",
                "entry_number": number,
                "date_utc": date_utc,
                "side": "long",
                "signal_candle_time_utc": _format_utc(signal_row["open_time_utc"]),
                "target_entry_time_utc": _format_utc(entry_row["open_time_utc"]),
                "entry_rule": "next_bar_open_after_signal_close",
                "execution_price_rule": "market_next_open_with_slippage",
                "slippage_bps": float(slippage_bps),
                "entry_open_price": entry_open,
                "entry_price_with_slippage": entry_open * (1.0 + slip),
                "tolerance_bars_before": 0,
                "tolerance_bars_after": 0,
                "label_type": "manual_user_marked_bottom_next_open",
                "setup_type_hint": "manual_reversal_bottom_knife_drop_long",
                "image_detection": {
                    "pixel_x_center": round(comp.x_center, 3),
                    "pixel_y_center": round(comp.y_center, 3),
                    "pixel_bbox": [comp.x_min, comp.y_min, comp.x_max, comp.y_max],
                    "red_pixels": comp.pixels,
                    "time_mapping": {
                        "x_utc_0000": float(x_utc_0000),
                        "px_per_hour": float(px_per_hour),
                        "time_rounding": "nearest_minute_from_red_mark_center",
                    },
                },
                "signal_candle_check": {
                    "open": float(signal_row["open"]),
                    "high": float(signal_row["high"]),
                    "low": float(signal_row["low"]),
                    "close": float(signal_row["close"]),
                    "volume": float(signal_row["volume"]),
                },
                "entry_candle_check": {
                    "open": float(entry_row["open"]),
                    "high": float(entry_row["high"]),
                    "low": float(entry_row["low"]),
                    "close": float(entry_row["close"]),
                    "volume": float(entry_row["volume"]),
                },
            }
        )

    payload = {
        "schema_version": 3,
        "run_id": f"manual_entries_{seed['symbol']}_{seed['timeframe']}_{date_utc}_{dataset_role}_user_marked_bottoms",
        "status": f"{dataset_role}_USER_MARKED_BOTTOMS_READY_NEEDS_VISUAL_CONFIRM",
        "symbol": seed["symbol"],
        "timeframe": seed["timeframe"],
        "data_layer": seed["data_layer"],
        "dataset_role": dataset_role,
        "entry_contract": {
            "signal_definition": "manual red mark points to a closed bottom/knife-drop signal candle",
            "entry_definition": "enter long at the next candle open after signal candle close",
            "execution_price_formula_long": "entry_open_price * (1 + slippage_bps / 10000)",
            "default_slippage_bps": float(slippage_bps),
        },
        "source_images": [
            {
                "date_utc": date_utc,
                "image_path": str(copied_png),
                "image_sha256": _sha256(copied_png),
                "seed_image_path": seed["image_png"],
                "source_csv": str(source_csv),
                "source_csv_sha256": seed["source_csv_sha256"],
                "rows": int(seed["rows"]),
            }
        ],
        "entries": entries,
        "holdout_policy": {
            "dev_days": ["2026-05-12"],
            "validation_days": ["2026-05-13"],
            "holdout_days": ["2026-05-14"],
            "ml_transfer_allowed": False,
        },
        "notes": [
            "Manual labels are extracted from the user-marked PNG. Auto knife candidates are stored separately and are not ML labels until the user confirms them."
        ],
    }
    manual_path = out_dir / "manual_entries.json"
    manual_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload, manual_path


def select_auto_knife_candidates(df: pd.DataFrame, *, top_n: int = 8, cooldown_bars: int = 30) -> list[dict[str, Any]]:
    work = df.copy()
    work["ret_6_pct"] = (work["close"] / work["close"].shift(6) - 1.0) * 100.0
    work["ret_12_pct"] = (work["close"] / work["close"].shift(12) - 1.0) * 100.0
    work["ret_24_pct"] = (work["close"] / work["close"].shift(24) - 1.0) * 100.0
    roll_low = work["low"].rolling(60, min_periods=20).min()
    roll_high = work["high"].rolling(60, min_periods=20).max()
    work["low_pos_60"] = (work["low"] - roll_low) / (roll_high - roll_low).replace(0, np.nan)
    vol_mean = work["volume"].rolling(60, min_periods=20).mean()
    vol_std = work["volume"].rolling(60, min_periods=20).std().replace(0, np.nan)
    work["vol_z_60"] = (work["volume"] - vol_mean) / vol_std
    body = (work["close"] - work["open"]).abs().replace(0, np.nan)
    work["lower_wick_to_body"] = (work[["open", "close"]].min(axis=1) - work["low"]) / body
    work["severity"] = (
        (-work["ret_12_pct"]).clip(lower=0) * 1.25
        + (-work["ret_24_pct"]).clip(lower=0) * 0.75
        + work["vol_z_60"].fillna(0).clip(lower=0) * 0.18
        + (1.0 - work["low_pos_60"].fillna(1)).clip(lower=0) * 0.65
        + work["lower_wick_to_body"].fillna(0).clip(lower=0, upper=5) * 0.08
    )
    mask = (
        (work.index >= 20)
        & (work["low_pos_60"].fillna(1) <= 0.22)
        & (
            (work["ret_12_pct"].fillna(0) <= -0.35)
            | (work["ret_24_pct"].fillna(0) <= -0.65)
            | (work["vol_z_60"].fillna(0) >= 2.25)
        )
    )
    ranked = work.loc[mask].sort_values("severity", ascending=False)
    selected: list[int] = []
    for idx in ranked.index:
        idx_int = int(idx)
        if any(abs(idx_int - prev) < cooldown_bars for prev in selected):
            continue
        selected.append(idx_int)
        if len(selected) >= top_n:
            break
    selected.sort()
    out: list[dict[str, Any]] = []
    for number, idx in enumerate(selected, 1):
        row = work.iloc[idx]
        entry_idx = idx + 1 if idx + 1 < len(work) else idx
        entry_row = work.iloc[entry_idx]
        out.append(
            {
                "candidate_id": f"AK_{number:03d}",
                "rank_time_order": number,
                "kind": "auto_knife_drop_candidate",
                "signal_candle_time_utc": _format_utc(row["open_time_utc"]),
                "suggested_entry_time_utc": _format_utc(entry_row["open_time_utc"]),
                "severity": round(float(row["severity"]), 6),
                "low": float(row["low"]),
                "entry_open_price": float(entry_row["open"]),
                "features": {
                    "ret_6_pct": None if pd.isna(row["ret_6_pct"]) else round(float(row["ret_6_pct"]), 6),
                    "ret_12_pct": None if pd.isna(row["ret_12_pct"]) else round(float(row["ret_12_pct"]), 6),
                    "ret_24_pct": None if pd.isna(row["ret_24_pct"]) else round(float(row["ret_24_pct"]), 6),
                    "low_pos_60": None if pd.isna(row["low_pos_60"]) else round(float(row["low_pos_60"]), 6),
                    "vol_z_60": None if pd.isna(row["vol_z_60"]) else round(float(row["vol_z_60"]), 6),
                    "lower_wick_to_body": None
                    if pd.isna(row["lower_wick_to_body"])
                    else round(float(row["lower_wick_to_body"]), 6),
                },
            }
        )
    return out


def render_overlay(
    *,
    manual_payload: dict[str, Any],
    manual_entries_path: Path,
    auto_candidates: list[dict[str, Any]],
    out_dir: Path,
) -> tuple[Path, Path]:
    source = manual_payload["source_images"][0]
    df = _load_core(Path(source["source_csv"]))
    symbol = str(manual_payload["symbol"])
    timeframe = str(manual_payload["timeframe"])
    date_utc = str(source["date_utc"])

    bg = "#101418"
    fig, (ax_price, ax_vol) = plt.subplots(
        2,
        1,
        figsize=(22, 10.8),
        sharex=True,
        gridspec_kw={"height_ratios": [4.2, 1.2]},
    )
    fig.patch.set_facecolor(bg)
    ax_price.set_facecolor(bg)
    ax_vol.set_facecolor(bg)

    x = mdates.date2num(df["open_time_utc"].to_numpy())
    width = _bar_width_days(timeframe)
    up_color = "#26a69a"
    down_color = "#ef5350"
    wick_color = "#cfd8dc"
    ax_price.vlines(x, df["low"], df["high"], color=wick_color, linewidth=0.65, alpha=0.85, zorder=1)
    for i, row in df.iterrows():
        open_px = float(row["open"])
        close_px = float(row["close"])
        lower = min(open_px, close_px)
        height = max(abs(close_px - open_px), 1e-8)
        color = up_color if close_px >= open_px else down_color
        ax_price.add_patch(
            Rectangle(
                (x[i] - width / 2, lower),
                width,
                height,
                facecolor=color,
                edgecolor=color,
                linewidth=0.45,
                alpha=0.95,
            )
        )
    ax_price.plot(df["open_time_utc"], df["ema20"], color="#ffd54f", linewidth=1.0, label="EMA20")
    ax_price.plot(df["open_time_utc"], df["ema50"], color="#64b5f6", linewidth=1.0, label="EMA50")
    vol_colors = [up_color if close_px >= open_px else down_color for open_px, close_px in zip(df["open"], df["close"])]
    ax_vol.bar(df["open_time_utc"], df["volume"], width=width, color=vol_colors, alpha=0.75)

    time_index = {pd.Timestamp(ts).strftime("%Y-%m-%dT%H:%M:%SZ"): i for i, ts in enumerate(df["open_time_utc"])}
    price_span = max(float(df["high"].max() - df["low"].min()), 1e-6)
    y_offset = price_span * 0.035

    for item in manual_payload["entries"]:
        number = int(item["entry_number"])
        signal_key = str(item["signal_candle_time_utc"])
        entry_key = str(item["target_entry_time_utc"])
        signal_idx = time_index.get(signal_key)
        entry_idx = time_index.get(entry_key)
        if signal_idx is None or entry_idx is None:
            continue
        signal_ts = df.iloc[signal_idx]["open_time_utc"]
        entry_ts = df.iloc[entry_idx]["open_time_utc"]
        signal_y = float(df.iloc[signal_idx]["low"]) - y_offset * 0.2
        entry_y = float(item["entry_open_price"])
        ax_price.annotate(
            f"S{number}",
            xy=(signal_ts, signal_y),
            xytext=(signal_ts, signal_y - y_offset * 0.8),
            ha="center",
            va="top",
            color="#ff1744",
            fontsize=8,
            arrowprops={"arrowstyle": "-|>", "color": "#ff1744", "linewidth": 1.9},
            zorder=8,
        )
        ax_price.scatter([entry_ts], [entry_y], marker="^", s=92, color="#00e676", edgecolors="black", linewidths=0.8, zorder=10)
        ax_price.text(entry_ts, entry_y + y_offset * 0.35, f"E{number}", color="#00e676", fontsize=8, ha="center", va="bottom")

    for item in auto_candidates:
        signal_ts = pd.Timestamp(item["signal_candle_time_utc"])
        entry_ts = pd.Timestamp(item["suggested_entry_time_utc"])
        signal_key = signal_ts.strftime("%Y-%m-%dT%H:%M:%SZ")
        idx = time_index.get(signal_key)
        if idx is None:
            continue
        signal_y = float(df.iloc[idx]["low"]) - y_offset * 1.35
        ax_price.scatter([signal_ts], [signal_y], marker="D", s=58, color="#00e5ff", edgecolors="black", linewidths=0.7, zorder=9)
        ax_price.text(signal_ts, signal_y - y_offset * 0.35, item["candidate_id"], color="#00e5ff", fontsize=7, ha="center", va="top")
        ax_price.axvspan(signal_ts, entry_ts, color="#00e5ff", alpha=0.045, linewidth=0, zorder=0)

    ax_price.set_title(
        f"{symbol} {timeframe} {date_utc} UTC | user bottoms S/E + auto knife candidates AK | no ML",
        color="white",
        fontsize=13,
        pad=10,
    )
    ax_price.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    for ax in (ax_price, ax_vol):
        ax.grid(color="#2f3a40", alpha=0.45, linewidth=0.6)
        ax.tick_params(colors="#e0e0e0")
        for spine in ax.spines.values():
            spine.set_color("#3a444b")
    ax_price.legend(facecolor="#172026", edgecolor="#3a444b", labelcolor="white", fontsize=9, loc="upper left", ncol=3)
    fig.autofmt_xdate()
    plt.tight_layout()

    ts_now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    png_path = out_dir / f"visual_entry_manual_auto_overlay_{date_utc}_{ts_now}.png"
    json_path = out_dir / f"visual_entry_manual_auto_overlay_{date_utc}_{ts_now}.json"
    plt.savefig(png_path, dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)
    json_path.write_text(
        json.dumps(
            {
                "manual_entries": str(manual_entries_path),
                "overlay_png": str(png_path),
                "auto_knife_candidates": auto_candidates,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return png_path, json_path


def write_audit(
    *,
    payload: dict[str, Any],
    manual_path: Path,
    auto_path: Path,
    overlay_path: Path,
    out_dir: Path,
) -> Path:
    date_utc = payload["source_images"][0]["date_utc"]
    lines = [
        f"# Visual Entry manual bottoms {date_utc}",
        "",
        f"Статус: `{payload['status']}`.",
        "",
        f"Manual entries: `{manual_path}`.",
        f"Auto knife candidates: `{auto_path}`.",
        f"Overlay PNG: `{overlay_path}`.",
        "",
        "Правило разметки: красная пользовательская метка означает закрытую сигнальную свечу дна/провала; вход LONG считается на `open` следующей свечи с учетом slippage.",
        "",
        "Важно: `AK#` авто-кандидаты не являются обучающими метками и не идут в ML, пока пользователь не подтвердит их глазами.",
        "",
        "## Ручные входы",
        "",
        "| # | signal | entry | open | slip |",
        "|---:|---|---|---:|---:|",
    ]
    for item in payload["entries"]:
        lines.append(
            "| `{}` | `{}` | `{}` | `{:.6f}` | `{:.6f}` |".format(
                item["entry_number"],
                item["signal_candle_time_utc"],
                item["target_entry_time_utc"],
                float(item["entry_open_price"]),
                float(item["entry_price_with_slippage"]),
            )
        )
    path = out_dir / f"manual_entries_user_bottoms_{date_utc}_{payload['dataset_role']}_RU.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build manual entries and auto knife-drop suggestions from a marked PNG.")
    parser.add_argument("--seed-json", required=True)
    parser.add_argument("--marked-png", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--dataset-role", required=True)
    parser.add_argument("--x-utc-0000", type=float, required=True)
    parser.add_argument("--px-per-hour", type=float, required=True)
    parser.add_argument("--slippage-bps", type=float, default=5.0)
    parser.add_argument("--auto-knife-top-n", type=int, default=8)
    parser.add_argument("--auto-cooldown-bars", type=int, default=30)
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)
    payload, manual_path = build_manual_entries(
        seed_json=Path(args.seed_json),
        marked_png=Path(args.marked_png),
        out_dir=out_dir,
        dataset_role=str(args.dataset_role),
        x_utc_0000=float(args.x_utc_0000),
        px_per_hour=float(args.px_per_hour),
        slippage_bps=float(args.slippage_bps),
    )
    df = _load_core(Path(payload["source_images"][0]["source_csv"]))
    auto_candidates = select_auto_knife_candidates(
        df,
        top_n=int(args.auto_knife_top_n),
        cooldown_bars=int(args.auto_cooldown_bars),
    )
    auto_path = out_dir / "auto_knife_candidates.json"
    auto_path.write_text(json.dumps({"candidates": auto_candidates}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    overlay_path, overlay_json = render_overlay(
        manual_payload=payload,
        manual_entries_path=manual_path,
        auto_candidates=auto_candidates,
        out_dir=out_dir,
    )
    audit_path = write_audit(
        payload=payload,
        manual_path=manual_path,
        auto_path=auto_path,
        overlay_path=overlay_path,
        out_dir=out_dir,
    )
    print(
        json.dumps(
            {
                "status": "OK",
                "manual_entries": str(manual_path),
                "manual_entries_count": len(payload["entries"]),
                "auto_knife_candidates": str(auto_path),
                "auto_knife_count": len(auto_candidates),
                "overlay_png": str(overlay_path),
                "overlay_json": str(overlay_json),
                "audit": str(audit_path),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
