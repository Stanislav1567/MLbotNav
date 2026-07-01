from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def _parse_time(value: str) -> datetime:
    normalized = value.strip().replace(" ", "T")
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_core_csv(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                {
                    "open_time_utc": _parse_time(row["open_time_utc"]),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"]),
                }
            )
    return rows


def _ema(values: list[float], span: int) -> list[float | None]:
    alpha = 2.0 / (span + 1.0)
    out: list[float | None] = []
    current: float | None = None
    for value in values:
        current = value if current is None else alpha * value + (1.0 - alpha) * current
        out.append(current)
    return out


def _rolling_min(values: list[float], window: int) -> list[float | None]:
    out: list[float | None] = []
    for i in range(len(values)):
        if i + 1 < window:
            out.append(None)
        else:
            out.append(min(values[i - window + 1 : i + 1]))
    return out


def _rolling_max(values: list[float], window: int) -> list[float | None]:
    out: list[float | None] = []
    for i in range(len(values)):
        if i + 1 < window:
            out.append(None)
        else:
            out.append(max(values[i - window + 1 : i + 1]))
    return out


def _rolling_mean(values: list[float], window: int) -> list[float | None]:
    out: list[float | None] = []
    running = 0.0
    for i, value in enumerate(values):
        running += value
        if i >= window:
            running -= values[i - window]
        out.append(running / window if i + 1 >= window else None)
    return out


def _rolling_std(values: list[float], window: int) -> list[float | None]:
    out: list[float | None] = []
    for i in range(len(values)):
        if i + 1 < window:
            out.append(None)
        else:
            sample = values[i - window + 1 : i + 1]
            mean = sum(sample) / window
            out.append(math.sqrt(sum((item - mean) ** 2 for item in sample) / window))
    return out


def _safe_pct(num: float, den: float) -> float | None:
    if den == 0:
        return None
    return num / den * 100.0


def enrich_rows(rows: list[dict[str, Any]]) -> None:
    closes = [row["close"] for row in rows]
    highs = [row["high"] for row in rows]
    lows = [row["low"] for row in rows]
    volumes = [row["volume"] for row in rows]
    ema20 = _ema(closes, 20)
    ema50 = _ema(closes, 50)
    low60 = _rolling_min(lows, 60)
    high60 = _rolling_max(highs, 60)
    vol_mean20 = _rolling_mean(volumes, 20)
    vol_std20 = _rolling_std(volumes, 20)

    gains: list[float] = [0.0]
    losses: list[float] = [0.0]
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i - 1]
        gains.append(max(delta, 0.0))
        losses.append(abs(min(delta, 0.0)))
    avg_gain14 = _rolling_mean(gains, 14)
    avg_loss14 = _rolling_mean(losses, 14)
    low14 = _rolling_min(lows, 14)
    high14 = _rolling_max(highs, 14)

    for i, row in enumerate(rows):
        row["ema20"] = ema20[i]
        row["ema50"] = ema50[i]
        row["ema_gap_pct"] = _safe_pct((ema20[i] or 0.0) - (ema50[i] or 0.0), row["close"]) if ema20[i] and ema50[i] else None
        row["ema20_slope_5_pct"] = _safe_pct((ema20[i] or 0.0) - (ema20[i - 5] or 0.0), row["close"]) if i >= 5 and ema20[i] and ema20[i - 5] else None
        for n in (1, 3, 6, 12, 24):
            row[f"ret_{n}_pct"] = _safe_pct(row["close"] - closes[i - n], closes[i - n]) if i >= n else None
        if low60[i] is not None and high60[i] is not None and high60[i] != low60[i]:
            row["range_pos_60"] = (row["close"] - low60[i]) / (high60[i] - low60[i])
            row["dist_from_low_60_pct"] = _safe_pct(row["close"] - low60[i], row["close"])
            row["dist_from_high_60_pct"] = _safe_pct(high60[i] - row["close"], row["close"])
        else:
            row["range_pos_60"] = None
            row["dist_from_low_60_pct"] = None
            row["dist_from_high_60_pct"] = None
        if vol_mean20[i] is not None and vol_std20[i] and vol_std20[i] > 0:
            row["vol_z20"] = (row["volume"] - vol_mean20[i]) / vol_std20[i]
        else:
            row["vol_z20"] = None
        if avg_gain14[i] is not None and avg_loss14[i] is not None:
            if avg_loss14[i] == 0:
                row["rsi14"] = 100.0
            else:
                rs = avg_gain14[i] / avg_loss14[i]
                row["rsi14"] = 100.0 - 100.0 / (1.0 + rs)
        else:
            row["rsi14"] = None
        if low14[i] is not None and high14[i] is not None and high14[i] != low14[i]:
            row["stoch_k14"] = (row["close"] - low14[i]) / (high14[i] - low14[i]) * 100.0
        else:
            row["stoch_k14"] = None
        body = row["close"] - row["open"]
        candle_range = row["high"] - row["low"]
        row["green_candle"] = body > 0
        row["body_pct"] = _safe_pct(body, row["open"])
        row["lower_wick_share"] = ((min(row["open"], row["close"]) - row["low"]) / candle_range) if candle_range > 0 else None
        row["upper_wick_share"] = ((row["high"] - max(row["open"], row["close"])) / candle_range) if candle_range > 0 else None


def _nearest_row_index(rows: list[dict[str, Any]], target: datetime) -> int:
    return min(
        range(len(rows)),
        key=lambda i: abs((rows[i]["open_time_utc"] - target).total_seconds()),
    )


def build_audit(manual_entries_path: Path) -> dict[str, Any]:
    manual = json.loads(manual_entries_path.read_text(encoding="utf-8"))
    source_csv = Path(manual["source_images"][0]["source_csv"])
    rows = _read_core_csv(source_csv)
    enrich_rows(rows)

    entries: list[dict[str, Any]] = []
    for raw in manual["entries"]:
        target_time = _parse_time(raw["target_entry_time_utc"])
        signal_time = target_time - timedelta(minutes=1)
        target_idx = _nearest_row_index(rows, target_time)
        signal_idx = _nearest_row_index(rows, signal_time)
        target_row = rows[target_idx]
        signal_row = rows[signal_idx]
        entries.append(
            {
                "entry_id": raw["entry_id"],
                "target_entry_time_utc": _format_time(target_time),
                "signal_time_utc": _format_time(signal_time),
                "target_features": _feature_view(target_row),
                "signal_features": _feature_view(signal_row),
                "setup_tags": _setup_tags(signal_row, target_row),
            }
        )

    tag_counts: dict[str, int] = {}
    for entry in entries:
        for tag in entry["setup_tags"]:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    return {
        "schema_version": 1,
        "manual_entries": str(manual_entries_path),
        "source_csv": str(source_csv),
        "source_csv_sha256": manual["source_images"][0].get("source_csv_sha256"),
        "entries_total": len(entries),
        "entries": entries,
        "tag_counts": dict(sorted(tag_counts.items(), key=lambda item: (-item[1], item[0]))),
        "candidate_families": _candidate_families(tag_counts),
    }


def _feature_view(row: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "open_time_utc",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "ret_1_pct",
        "ret_3_pct",
        "ret_6_pct",
        "ret_12_pct",
        "ret_24_pct",
        "ema_gap_pct",
        "ema20_slope_5_pct",
        "range_pos_60",
        "dist_from_low_60_pct",
        "dist_from_high_60_pct",
        "vol_z20",
        "rsi14",
        "stoch_k14",
        "green_candle",
        "body_pct",
        "lower_wick_share",
        "upper_wick_share",
    ]
    out: dict[str, Any] = {}
    for key in keys:
        value = row.get(key)
        if isinstance(value, datetime):
            out[key] = _format_time(value)
        elif isinstance(value, float):
            out[key] = round(value, 6)
        else:
            out[key] = value
    return out


def _setup_tags(signal_row: dict[str, Any], target_row: dict[str, Any]) -> list[str]:
    tags: list[str] = []
    ret12 = signal_row.get("ret_12_pct")
    ret24 = signal_row.get("ret_24_pct")
    range_pos = signal_row.get("range_pos_60")
    rsi = signal_row.get("rsi14")
    stoch = signal_row.get("stoch_k14")
    vol_z = signal_row.get("vol_z20")
    ema_slope = signal_row.get("ema20_slope_5_pct")
    if ret12 is not None and ret12 <= -0.25:
        tags.append("dip_ret12")
    if ret24 is not None and ret24 <= -0.40:
        tags.append("dip_ret24")
    if range_pos is not None and range_pos <= 0.25:
        tags.append("near_local_low_60")
    if rsi is not None and rsi <= 40:
        tags.append("rsi_cold")
    if stoch is not None and stoch <= 35:
        tags.append("stoch_low")
    if vol_z is not None and vol_z >= 1.0:
        tags.append("volume_spike")
    if target_row.get("green_candle"):
        tags.append("green_target_candle")
    if ema_slope is not None and ema_slope < 0:
        tags.append("ema20_down_context")
    return tags


def _candidate_families(tag_counts: dict[str, int]) -> list[dict[str, Any]]:
    families: list[dict[str, Any]] = []
    dip_votes = (
        tag_counts.get("near_local_low_60", 0)
        + tag_counts.get("dip_ret12", 0)
        + tag_counts.get("dip_ret24", 0)
        + tag_counts.get("rsi_cold", 0)
        + tag_counts.get("stoch_low", 0)
    )
    if dip_votes >= 7:
        families.append(
            {
                "family_id": "REVERSAL_DIP_BUY_LONG",
                "status": "DESIGN_CANDIDATE",
                "purpose_ru": "Ловить ручные LONG-входы после локального снижения, где B001 momentum либо молчит, либо входит поздно.",
                "draft_conditions_ru": [
                    "контекст падения: ret_12/ret_24 отрицательные или цена близко к low за 60 баров",
                    "триггер разворота: зеленая свеча, нижняя тень или восстановление от low",
                    "подтверждение: объемный всплеск, RSI/Stoch в холодной зоне или возврат к EMA20",
                ],
            }
        )
    if tag_counts.get("ema20_down_context", 0) >= 4 and tag_counts.get("green_target_candle", 0) >= 2:
        families.append(
            {
                "family_id": "EMA_DOWN_PULLBACK_REVERSAL_LONG",
                "status": "DESIGN_CANDIDATE",
                "purpose_ru": "Отдельно проверить входы, где EMA20 еще смотрит вниз, но появляется первая попытка разворота.",
                "draft_conditions_ru": [
                    "EMA20 slope за 5 баров отрицательный",
                    "цена не должна быть далеко от локального low",
                    "триггером должен быть первый зеленый или wick/reclaim бар",
                ],
            }
        )
    if tag_counts.get("volume_spike", 0) >= 2:
        families.append(
            {
                "family_id": "VOLUME_REVERSAL_CONFIRM_LONG",
                "status": "DESIGN_CANDIDATE",
                "purpose_ru": "Использовать объем как подтверждение ручного входа, а не как самостоятельный вход.",
            }
        )
    return families


def write_reports(audit: dict[str, Any], out_dir: Path) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "visual_entry_feature_audit_20260512_DEV.json"
    md_path = out_dir / "visual_entry_feature_audit_20260512_DEV_RU.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(audit), encoding="utf-8")
    return json_path, md_path


def _markdown(audit: dict[str, Any]) -> str:
    lines = [
        "# Visual Entry Feature Audit 2026-05-12",
        "",
        "Статус: `DEV_DIAGNOSTIC_ONLY`.",
        "",
        f"Manual entries: `{audit['manual_entries']}`.",
        f"Core CSV: `{audit['source_csv']}`.",
        f"Core SHA256: `{audit['source_csv_sha256']}`.",
        "",
        "## Теги",
        "",
    ]
    for tag, count in audit["tag_counts"].items():
        lines.append(f"- `{tag}`: `{count}`")
    lines.extend(
        [
            "",
            "## Входы",
            "",
            "| entry_id | time | tags | ret12 | ret24 | range_pos_60 | rsi14 | stoch_k14 | vol_z20 |",
            "|---|---:|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for entry in audit["entries"]:
        f = entry["signal_features"]
        tags = ", ".join(f"`{tag}`" for tag in entry["setup_tags"])
        lines.append(
            "| `{entry_id}` | `{time}` | {tags} | `{ret12}` | `{ret24}` | `{range_pos}` | `{rsi}` | `{stoch}` | `{vol_z}` |".format(
                entry_id=entry["entry_id"],
                time=entry["target_entry_time_utc"],
                tags=tags,
                ret12=f.get("ret_12_pct"),
                ret24=f.get("ret_24_pct"),
                range_pos=f.get("range_pos_60"),
                rsi=f.get("rsi14"),
                stoch=f.get("stoch_k14"),
                vol_z=f.get("vol_z20"),
            )
        )
    lines.extend(["", "## Кандидатные семьи", ""])
    for family in audit["candidate_families"]:
        lines.append(f"- `{family['family_id']}`: {family.get('purpose_ru', '')}")
    lines.extend(
        [
            "",
            "## Решение",
            "",
            "Это diagnostic-only слой. Он не передает ничего в ML и не выбирает победителя по прибыли. Его задача: выбрать, какие паспорта и новые family стоит проверять через visual scorer.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit manual visual entries against derived OHLCV features.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/qa_gate")
    args = parser.parse_args(argv)
    audit = build_audit(Path(args.manual_entries))
    json_path, md_path = write_reports(audit, Path(args.out_dir))
    print(json.dumps({"status": "OK", "json": str(json_path), "md": str(md_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
