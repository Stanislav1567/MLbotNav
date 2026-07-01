from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
from PIL import Image


@dataclass(frozen=True)
class ArrowComponent:
    pixels: int
    x_min: int
    x_max: int
    y_min: int
    y_max: int
    x_center: float
    y_center: float
    x_tip: float
    y_tip: int


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _format_utc(value: pd.Timestamp | datetime) -> str:
    return pd.Timestamp(value).tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%SZ")


def _bar_width_days(tf: str) -> float:
    if tf.endswith("m"):
        return (int(tf[:-1]) / (24 * 60)) * 0.8
    return (1 / (24 * 60)) * 0.8


def _detect_red_arrow_components(marked_png: Path) -> list[ArrowComponent]:
    image = Image.open(marked_png).convert("RGB")
    arr = np.asarray(image)
    mask = (arr[:, :, 0] > 180) & (arr[:, :, 1] < 90) & (arr[:, :, 2] < 90)
    height, width = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    out: list[ArrowComponent] = []

    for y in range(height):
        for x0 in np.where(mask[y] & ~seen[y])[0]:
            if seen[y, x0] or not mask[y, x0]:
                continue
            queue: deque[tuple[int, int]] = deque([(int(x0), int(y))])
            seen[y, x0] = True
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

            if len(points) < 80:
                continue
            pts = np.asarray(points)
            x_min = int(pts[:, 0].min())
            x_max = int(pts[:, 0].max())
            y_min = int(pts[:, 1].min())
            y_max = int(pts[:, 1].max())
            if y_max > 650:
                continue
            tip_band = pts[pts[:, 1] <= y_min + 3]
            out.append(
                ArrowComponent(
                    pixels=int(len(points)),
                    x_min=x_min,
                    x_max=x_max,
                    y_min=y_min,
                    y_max=y_max,
                    x_center=float(pts[:, 0].mean()),
                    y_center=float(pts[:, 1].mean()),
                    x_tip=float(tip_band[:, 0].mean()),
                    y_tip=y_min,
                )
            )
    return sorted(out, key=lambda item: item.x_tip)


def _pixel_x_to_time(
    *,
    x: float,
    date_utc: str,
    x_utc_0000: float,
    px_per_hour: float,
) -> pd.Timestamp:
    minutes = round(((float(x) - float(x_utc_0000)) / float(px_per_hour)) * 60.0)
    start = pd.Timestamp(f"{date_utc}T00:00:00Z")
    return start + pd.Timedelta(minutes=int(minutes))


def _load_core(source_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(source_csv)
    df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], utc=True, errors="coerce", format="mixed")
    df = df.dropna(subset=["open_time_utc"]).sort_values("open_time_utc").reset_index(drop=True)
    df["ema20"] = df["close"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["close"].ewm(span=50, adjust=False).mean()
    return df


def build_signal_entry_contract(
    *,
    seed_json: Path,
    marked_png: Path,
    out_dir: Path,
    side: str = "long",
    slippage_bps: float = 5.0,
    x_utc_0000: float = 137.0,
    px_per_hour: float = 52.730769,
) -> tuple[dict[str, Any], Path]:
    seed = json.loads(seed_json.read_text(encoding="utf-8"))
    source_csv = Path(seed["source_csv"])
    df = _load_core(source_csv)
    by_time = {pd.Timestamp(ts): idx for idx, ts in enumerate(df["open_time_utc"])}
    components = _detect_red_arrow_components(marked_png)
    date_utc = str(seed["date_utc"])
    slip = float(slippage_bps) / 10_000.0
    side_norm = side.lower().strip()
    side_mult = 1.0 if side_norm == "long" else -1.0

    entries: list[dict[str, Any]] = []
    for number, comp in enumerate(components, 1):
        signal_time = _pixel_x_to_time(
            x=comp.x_tip,
            date_utc=date_utc,
            x_utc_0000=x_utc_0000,
            px_per_hour=px_per_hour,
        )
        if signal_time not in by_time:
            continue
        signal_idx = by_time[signal_time]
        entry_idx = signal_idx + 1
        if entry_idx >= len(df):
            continue
        signal_row = df.iloc[signal_idx]
        entry_row = df.iloc[entry_idx]
        entry_open = float(entry_row["open"])
        entry_price_with_slippage = entry_open * (1.0 + slip * side_mult)
        entries.append(
            {
                "entry_id": f"ME_{date_utc.replace('-', '')}_{number:03d}_LONG",
                "entry_number": number,
                "date_utc": date_utc,
                "side": side_norm,
                "signal_candle_time_utc": _format_utc(signal_row["open_time_utc"]),
                "target_entry_time_utc": _format_utc(entry_row["open_time_utc"]),
                "entry_rule": "next_bar_open_after_signal_close",
                "execution_price_rule": "market_next_open_with_slippage",
                "slippage_bps": float(slippage_bps),
                "entry_open_price": entry_open,
                "entry_price_with_slippage": entry_price_with_slippage,
                "tolerance_bars_before": 0,
                "tolerance_bars_after": 0,
                "label_type": "manual_signal_wick_entry_next_open",
                "setup_type_hint": "manual_bottom_reversal_long",
                "image_detection": {
                    "pixel_x_tip": round(comp.x_tip, 3),
                    "pixel_y_tip": comp.y_tip,
                    "pixel_x_center": round(comp.x_center, 3),
                    "pixel_y_center": round(comp.y_center, 3),
                    "pixel_bbox": [comp.x_min, comp.y_min, comp.x_max, comp.y_max],
                    "red_pixels": comp.pixels,
                    "time_mapping": {
                        "x_utc_0000": float(x_utc_0000),
                        "px_per_hour": float(px_per_hour),
                        "time_rounding": "nearest_minute_from_arrow_tip",
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
        "schema_version": 2,
        "run_id": f"manual_entries_{seed['symbol']}_{seed['timeframe']}_{date_utc}_DEV_v2_signal_entry",
        "status": "DEV_DAY_SIGNAL_ENTRY_CONTRACT_NEEDS_USER_VISUAL_CONFIRM",
        "symbol": seed["symbol"],
        "timeframe": seed["timeframe"],
        "data_layer": seed["data_layer"],
        "dataset_role": "DEV_DAY",
        "entry_contract": {
            "signal_definition": "manual arrow tip points to the closed signal candle wick/bottom",
            "entry_definition": "enter at next candle open after signal candle close",
            "execution_price_formula_long": "entry_open_price * (1 + slippage_bps / 10000)",
            "execution_price_formula_short": "entry_open_price * (1 - slippage_bps / 10000)",
            "default_slippage_bps": float(slippage_bps),
        },
        "source_images": [
            {
                "date_utc": date_utc,
                "image_path": str(marked_png),
                "image_sha256": _sha256(marked_png),
                "seed_image_path": seed["image_png"],
                "source_csv": str(source_csv),
                "source_csv_sha256": seed["source_csv_sha256"],
                "rows": int(seed["rows"]),
            }
        ],
        "entries": entries,
        "holdout_policy": {
            "dev_days": [date_utc],
            "validation_days_locked": ["2026-05-13"],
            "holdout_days_locked": ["2026-05-14"],
            "ml_transfer_allowed": False,
        },
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "manual_entries.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload, path


def render_signal_entry_overlay(*, manual_entries_path: Path, out_dir: Path) -> tuple[Path, Path]:
    payload = json.loads(manual_entries_path.read_text(encoding="utf-8"))
    source = payload["source_images"][0]
    df = _load_core(Path(source["source_csv"]))
    symbol = payload["symbol"]
    timeframe = payload["timeframe"]
    day = source["date_utc"]

    bg = "#101418"
    fig, (ax_price, ax_vol) = plt.subplots(
        2,
        1,
        figsize=(22, 10.5),
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
    for item in payload["entries"]:
        signal_time = pd.Timestamp(item["signal_candle_time_utc"])
        entry_time = pd.Timestamp(item["target_entry_time_utc"])
        signal_idx = time_index.get(signal_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
        entry_idx = time_index.get(entry_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
        if signal_idx is None or entry_idx is None:
            continue
        signal_low = float(df.iloc[signal_idx]["low"])
        entry_price = float(item["entry_price_with_slippage"])
        entry_open = float(item["entry_open_price"])
        num = int(item["entry_number"])
        ax_price.annotate(
            f"S{num}",
            xy=(signal_time, signal_low),
            xytext=(signal_time, signal_low - 0.42),
            ha="center",
            va="top",
            color="#ff1744",
            fontsize=8,
            arrowprops={"arrowstyle": "-|>", "color": "#ff1744", "linewidth": 2.0},
            zorder=8,
        )
        ax_price.scatter(
            [entry_time],
            [entry_price],
            marker="^",
            s=120,
            color="#00e676",
            edgecolors="black",
            linewidths=0.8,
            zorder=10,
        )
        label = f"{num}: ENTRY {entry_time.strftime('%H:%M')}\nopen {entry_open:.4f}\nslip {entry_price:.4f}"
        ax_price.annotate(
            label,
            xy=(entry_time, entry_price),
            xytext=(8, 18),
            textcoords="offset points",
            ha="left",
            va="bottom",
            color="#00e676",
            fontsize=8,
            bbox={"boxstyle": "round,pad=0.25", "facecolor": "#10251c", "edgecolor": "#00e676", "alpha": 0.85},
            arrowprops={"arrowstyle": "->", "color": "#00e676", "linewidth": 1.2},
            zorder=11,
        )
        ax_price.axvspan(signal_time, entry_time, color="#00e676", alpha=0.04, linewidth=0, zorder=0)

    ax_price.set_title(
        f"{symbol} {timeframe} {day} UTC | signal wick -> next candle open entry | slippage-aware",
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

    out_dir.mkdir(parents=True, exist_ok=True)
    ts_now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    png_path = out_dir / f"visual_entry_signal_entry_overlay_{day}_{ts_now}.png"
    json_path = out_dir / f"visual_entry_signal_entry_overlay_{day}_{ts_now}.json"
    plt.savefig(png_path, dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)
    summary = {
        "manual_entries": str(manual_entries_path),
        "visual_png": str(png_path),
        "source_csv": source["source_csv"],
        "entry_contract": payload["entry_contract"],
        "entries": payload["entries"],
    }
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return png_path, json_path


def write_audit(payload: dict[str, Any], manual_path: Path, png_path: Path, out_dir: Path) -> Path:
    lines = [
        "# Visual Entry Signal -> Entry Contract",
        "",
        "Статус: `DEV_SIGNAL_ENTRY_CONTRACT_NEEDS_USER_VISUAL_CONFIRM`.",
        "",
        f"Manual entries: `{manual_path}`.",
        f"Overlay: `{png_path}`.",
        "",
        "Правило: красная метка `S#` показывает закрытую сигнальную свечу с фитилем/дном; зеленая метка `ENTRY #` показывает вход на открытии следующей свечи.",
        "",
        f"Slippage: `{payload['entry_contract']['default_slippage_bps']}` bps.",
        "",
        "| # | signal candle | entry candle | entry open | entry with slippage |",
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
    lines.extend(
        [
            "",
            "До подтверждения пользователем этот v2-файл не является финальной разметкой для ML. В ML ничего не передавать.",
            "",
        ]
    )
    path = out_dir / "manual_entries_signal_entry_audit_20260512_DEV_RU.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build and render manual signal candle -> next open entry contract.")
    parser.add_argument("--seed-json", required=True)
    parser.add_argument("--marked-png", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--slippage-bps", type=float, default=5.0)
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)
    payload, manual_path = build_signal_entry_contract(
        seed_json=Path(args.seed_json),
        marked_png=Path(args.marked_png),
        out_dir=out_dir,
        slippage_bps=args.slippage_bps,
    )
    png_path, json_path = render_signal_entry_overlay(manual_entries_path=manual_path, out_dir=out_dir)
    audit_path = write_audit(payload, manual_path, png_path, out_dir)
    print(
        json.dumps(
            {
                "status": "OK",
                "manual_entries": str(manual_path),
                "overlay_png": str(png_path),
                "overlay_json": str(json_path),
                "audit": str(audit_path),
                "entries": len(payload["entries"]),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
