from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

from mlbotnav.visual_entry_combo_search import (
    _compute_extra_features,
    render_simple_entry_arrows,
)
from mlbotnav.visual_entry_feature_audit import _read_core_csv, enrich_rows
from mlbotnav.visual_entry_score import TradeEntry, load_manual_entries, score_entries


def _value(row: dict[str, Any], key: str, default: float) -> float:
    value = row.get(key)
    if value is None:
        return default
    return float(value)


def _prepare_rows(manual_entries_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manual_payload = json.loads(manual_entries_path.read_text(encoding="utf-8"))
    source_csv = Path(manual_payload["source_images"][0]["source_csv"])
    rows = _read_core_csv(source_csv)
    enrich_rows(rows)
    _compute_extra_features(rows)
    for idx, row in enumerate(rows):
        window = rows[max(0, idx - 59) : idx + 1]
        low_60 = min(item["low"] for item in window)
        high_60 = max(item["high"] for item in window)
        candle_range = row["high"] - row["low"]
        row["low_range_pos_60"] = (row["low"] - low_60) / (high_60 - low_60) if high_60 > low_60 else 1.0
        row["close_pos_candle"] = (row["close"] - row["low"]) / candle_range if candle_range > 0 else 0.0
        for lookback in (5, 10, 20, 60):
            local_window = rows[max(0, idx - lookback + 1) : idx + 1]
            row[f"local_low_{lookback}"] = row["low"] <= min(item["low"] for item in local_window) + 1e-12
    return manual_payload, rows


def _deep_capitulation(signal: dict[str, Any]) -> tuple[bool, list[str]]:
    votes: list[str] = []
    if signal["local_low_20"]:
        votes.append("LOCAL_LOW_20")
    if _value(signal, "range_pos_60", 1.0) <= 0.25 or _value(signal, "low_range_pos_60", 1.0) <= 0.05:
        votes.append("RANGE_LOW")
    if _value(signal, "ret_12_pct", 999.0) <= -0.30 or _value(signal, "ret_24_pct", 999.0) <= -0.50:
        votes.append("DIP_RET")
    if _value(signal, "rsi14", 999.0) <= 35.0:
        votes.append("RSI_COLD")
    if _value(signal, "stoch_k14", 999.0) <= 35.0:
        votes.append("STOCH_LOW")
    if _value(signal, "mfi14", 999.0) <= 35.0:
        votes.append("MFI_LOW")
    if _value(signal, "ema20_slope_5_pct", 999.0) < 0.0:
        votes.append("EMA_DOWN")
    return "LOCAL_LOW_20" in votes and len(votes) >= 5, votes


def _shallow_support(signal: dict[str, Any]) -> tuple[bool, list[str]]:
    votes: list[str] = []
    if signal["local_low_10"]:
        votes.append("LOCAL_LOW_10")
    if _value(signal, "range_pos_60", 1.0) <= 0.35 or _value(signal, "low_range_pos_60", 1.0) <= 0.08:
        votes.append("RANGE_LOW")
    if _value(signal, "ret_12_pct", 999.0) <= 0.10:
        votes.append("NOT_EXTENDED_UP")
    if _value(signal, "rsi14", 999.0) <= 60.0:
        votes.append("RSI_NOT_HOT")
    if _value(signal, "stoch_k14", 999.0) <= 60.0:
        votes.append("STOCH_NOT_HOT")
    if _value(signal, "ema_gap_pct", 999.0) < 0.0 or _value(signal, "ema20_slope_5_pct", 999.0) < 0.0:
        votes.append("EMA_WEAK")
    if _value(signal, "lower_wick_share", 0.0) >= 0.25 or _value(signal, "close_pos_candle", 0.0) >= 0.50:
        votes.append("WICK_OR_RECLAIM")
    return "LOCAL_LOW_10" in votes and "RANGE_LOW" in votes and len(votes) >= 5, votes


def _volume_wick(signal: dict[str, Any]) -> tuple[bool, list[str]]:
    votes: list[str] = []
    if signal["local_low_20"]:
        votes.append("LOCAL_LOW_20")
    if _value(signal, "low_range_pos_60", 1.0) <= 0.10:
        votes.append("LOW_NEAR_RANGE_LOW")
    if _value(signal, "vol_z20", -999.0) >= 1.0:
        votes.append("VOLUME_SPIKE")
    if _value(signal, "lower_wick_share", 0.0) >= 0.35:
        votes.append("LOWER_WICK")
    if _value(signal, "rsi14", 999.0) <= 50.0 or _value(signal, "mfi14", 999.0) <= 50.0:
        votes.append("COLD_OSC")
    return "LOCAL_LOW_20" in votes and len(votes) >= 4, votes


def _union(signal: dict[str, Any]) -> tuple[bool, list[str]]:
    out: list[str] = []
    ok_any = False
    for prefix, checker in (
        ("A", _deep_capitulation),
        ("B", _shallow_support),
        ("C", _volume_wick),
    ):
        ok, votes = checker(signal)
        if ok:
            ok_any = True
            out.extend(f"{prefix}:{vote}" for vote in votes)
    return ok_any, out


def _run_family(
    *,
    rows: list[dict[str, Any]],
    family_id: str,
    checker: Callable[[dict[str, Any]], tuple[bool, list[str]]],
    cooldown_bars: int,
    manual_entries: list[Any],
) -> dict[str, Any]:
    trades: list[TradeEntry] = []
    details: list[dict[str, Any]] = []
    last_idx = -10_000
    for idx in range(60, len(rows) - 1):
        if idx - last_idx < cooldown_bars:
            continue
        signal = rows[idx]
        ok, votes = checker(signal)
        if not ok:
            continue
        entry = rows[idx + 1]
        last_idx = idx
        trades.append(
            TradeEntry(
                row_index=idx + 1,
                side="long",
                entry_time=entry["open_time_utc"],
                exit_time_raw="",
                net_return=0.0,
                mae_pct=None,
                mfe_pct=None,
            )
        )
        details.append(
            {
                "signal_time_utc": signal["open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_time_utc": entry["open_time_utc"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "entry_open_price": float(entry["open"]),
                "context_votes": votes,
                "trigger_votes": ["NO_LOOKAHEAD_NEXT_OPEN"],
            }
        )
    score = score_entries(manual_entries, trades)
    return {
        "family_id": family_id,
        "params": {"cooldown_bars": cooldown_bars},
        "score": {
            key: score[key]
            for key in [
                "targets_total",
                "target_hits",
                "missed_targets",
                "false_entries",
                "entries_total",
                "precision",
                "recall",
                "f1_visual",
                "entry_lag_bars_abs_max",
                "visual_status",
            ]
        },
        "hit_details": score["hit_details"],
        "missed_target_details": score["missed_target_details"],
        "false_entry_details": score["false_entry_details"][:50],
        "first_signals": details[:100],
    }


def build_report(manual_entries_path: Path) -> dict[str, Any]:
    _, manual_entries = load_manual_entries(manual_entries_path)
    _, rows = _prepare_rows(manual_entries_path)
    candidates = [
        ("DEEP_CAPITULATION_NEXT_OPEN", _deep_capitulation, 20),
        ("SHALLOW_SUPPORT_PULLBACK_NEXT_OPEN", _shallow_support, 20),
        ("VOLUME_WICK_BOTTOM_NEXT_OPEN", _volume_wick, 20),
        ("DEEP_CAPITULATION_COOLDOWN45", _deep_capitulation, 45),
        ("SHALLOW_SUPPORT_COOLDOWN45", _shallow_support, 45),
        ("VOLUME_WICK_COOLDOWN45", _volume_wick, 45),
        ("UNION_ABC_NEXT_OPEN", _union, 20),
        ("UNION_ABC_COOLDOWN45", _union, 45),
    ]
    results = [
        _run_family(
            rows=rows,
            family_id=family_id,
            checker=checker,
            cooldown_bars=cooldown,
            manual_entries=manual_entries,
        )
        for family_id, checker, cooldown in candidates
    ]
    results.sort(
        key=lambda item: (
            item["score"]["f1_visual"],
            item["score"]["target_hits"],
            -item["score"]["false_entries"],
        ),
        reverse=True,
    )
    return {
        "schema_version": 1,
        "status": "DEV_NO_LOOKAHEAD_CANDIDATES_NO_ML",
        "manual_entries": str(manual_entries_path),
        "top_results": results,
    }


def write_reports(payload: dict[str, Any], manual_entries_path: Path, out_dir: Path, render_top: int) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[dict[str, str]] = []
    for index, result in enumerate(payload["top_results"][:render_top], 1):
        png = render_simple_entry_arrows(
            manual_entries_path=manual_entries_path,
            result=result,
            out_dir=out_dir,
            label=f"nolook_{index}_{result['family_id'].lower()}",
        )
        rendered.append({"rank": str(index), "family_id": result["family_id"], "visual_png": str(png)})
    payload["rendered"] = rendered
    json_path = out_dir / "visual_entry_no_lookahead_candidates_20260512_DEV.json"
    md_path = out_dir / "visual_entry_no_lookahead_candidates_20260512_DEV_RU.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    return json_path, md_path


def _markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Visual Entry v3 no-lookahead candidates",
        "",
        "Статус: `DEV_NO_LOOKAHEAD_CANDIDATES_NO_ML`.",
        "",
        f"Manual entries: `{payload['manual_entries']}`.",
        "",
        "| rank | family | hits | false | entries | precision | recall | f1 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for index, item in enumerate(payload["top_results"], 1):
        score = item["score"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{:.4f}` | `{:.4f}` | `{:.4f}` |".format(
                index,
                item["family_id"],
                score["target_hits"],
                score["false_entries"],
                score["entries_total"],
                score["precision"],
                score["recall"],
                score["f1_visual"],
            )
        )
    lines.extend(["", "## Rendered", ""])
    for item in payload.get("rendered", []):
        lines.append(f"- `{item['family_id']}`: `{item['visual_png']}`")
    lines.extend(
        [
            "",
            "## Решение",
            "",
            "Это честные диагностические кандидаты: используются только сигнальная свеча и прошлый контекст, вход ставится на следующий open. В ML ничего не передавать.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run no-lookahead visual-entry candidate families.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--out-dir", default="reports/final_review/visual_entry_v3/no_lookahead_candidates")
    parser.add_argument("--render-top", type=int, default=5)
    args = parser.parse_args(argv)
    manual_path = Path(args.manual_entries)
    payload = build_report(manual_path)
    json_path, md_path = write_reports(payload, manual_path, Path(args.out_dir), args.render_top)
    print(json.dumps({"status": "OK", "json": str(json_path), "md": str(md_path), "rendered": payload.get("rendered", [])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
