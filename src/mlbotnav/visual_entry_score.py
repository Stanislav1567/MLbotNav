from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ManualEntry:
    entry_id: str
    side: str
    target_time: datetime
    tolerance_before: int
    tolerance_after: int

    @property
    def window_start(self) -> datetime:
        return self.target_time - timedelta(minutes=self.tolerance_before)

    @property
    def window_end(self) -> datetime:
        return self.target_time + timedelta(minutes=self.tolerance_after)


@dataclass(frozen=True)
class TradeEntry:
    row_index: int
    side: str
    entry_time: datetime
    exit_time_raw: str
    net_return: float
    mae_pct: float | None
    mfe_pct: float | None


def _parse_time(value: str) -> datetime:
    normalized = value.strip().replace(" ", "T")
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _normalize_side(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text in {"1", "1.0", "long", "buy"}:
        return "long"
    if text in {"-1", "-1.0", "short", "sell"}:
        return "short"
    return text


def _float_or_zero(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _float_or_none(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def load_manual_entries(path: str | Path) -> tuple[dict[str, Any], list[ManualEntry]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    entries: list[ManualEntry] = []
    for raw in payload.get("entries", []):
        entries.append(
            ManualEntry(
                entry_id=str(raw["entry_id"]),
                side=_normalize_side(raw.get("side")),
                target_time=_parse_time(str(raw["target_entry_time_utc"])),
                tolerance_before=int(raw.get("tolerance_bars_before", 2)),
                tolerance_after=int(raw.get("tolerance_bars_after", 2)),
            )
        )
    return payload, sorted(entries, key=lambda item: item.target_time)


def load_trade_entries(path: str | Path) -> list[TradeEntry]:
    trades: list[TradeEntry] = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row_index, row in enumerate(reader, 1):
            entry_time_raw = (row.get("entry_time_utc") or "").strip()
            if not entry_time_raw:
                continue
            trades.append(
                TradeEntry(
                    row_index=row_index,
                    side=_normalize_side(row.get("side")),
                    entry_time=_parse_time(entry_time_raw),
                    exit_time_raw=(row.get("exit_time_utc") or "").strip(),
                    net_return=_float_or_zero(row.get("net_return")),
                    mae_pct=_float_or_none(row.get("mae_pct")),
                    mfe_pct=_float_or_none(row.get("mfe_pct")),
                )
            )
    return sorted(trades, key=lambda item: item.entry_time)


def score_entries(
    manual_entries: list[ManualEntry],
    trade_entries: list[TradeEntry],
) -> dict[str, Any]:
    hit_by_entry_id: dict[str, dict[str, Any]] = {}
    false_entries: list[dict[str, Any]] = []
    duplicate_hits: list[dict[str, Any]] = []

    for trade in trade_entries:
        candidates = [
            manual
            for manual in manual_entries
            if manual.side == trade.side
            and manual.window_start <= trade.entry_time <= manual.window_end
        ]
        candidates.sort(
            key=lambda manual: (
                abs((trade.entry_time - manual.target_time).total_seconds()),
                manual.entry_id,
            )
        )
        if not candidates:
            false_entries.append(_trade_public_dict(trade))
            continue

        target = next(
            (manual for manual in candidates if manual.entry_id not in hit_by_entry_id),
            None,
        )
        if target is None:
            target = candidates[0]
            duplicate_hits.append(
                {
                    "manual_entry_id": target.entry_id,
                    "trade": _trade_public_dict(trade),
                    "lag_bars": _lag_bars(trade.entry_time, target.target_time),
                }
            )
            continue

        hit_by_entry_id[target.entry_id] = {
            "manual_entry_id": target.entry_id,
            "target_entry_time_utc": _format_time(target.target_time),
            "matched_entry_time_utc": _format_time(trade.entry_time),
            "lag_bars": _lag_bars(trade.entry_time, target.target_time),
            "trade_row_index": trade.row_index,
            "net_return": trade.net_return,
        }

    missed_targets = [
        {
            "manual_entry_id": manual.entry_id,
            "target_entry_time_utc": _format_time(manual.target_time),
            "side": manual.side,
        }
        for manual in manual_entries
        if manual.entry_id not in hit_by_entry_id
    ]

    target_hits = len(hit_by_entry_id)
    targets_total = len(manual_entries)
    entries_total = len(trade_entries)
    precision = target_hits / entries_total if entries_total else 0.0
    recall = target_hits / targets_total if targets_total else 0.0
    f1_visual = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    lags = [item["lag_bars"] for item in hit_by_entry_id.values()]
    net_return_pct = sum(trade.net_return for trade in trade_entries) * 100.0
    mae_values = [trade.mae_pct for trade in trade_entries if trade.mae_pct is not None]
    mfe_values = [trade.mfe_pct for trade in trade_entries if trade.mfe_pct is not None]

    return {
        "schema_version": 1,
        "targets_total": targets_total,
        "target_hits": target_hits,
        "missed_targets": len(missed_targets),
        "false_entries": len(false_entries),
        "entries_total": entries_total,
        "precision": precision,
        "recall": recall,
        "f1_visual": f1_visual,
        "entry_lag_bars_avg": sum(lags) / len(lags) if lags else None,
        "entry_lag_bars_abs_max": max(abs(item) for item in lags) if lags else None,
        "duplicate_hits": len(duplicate_hits),
        "net_return_pct": net_return_pct,
        "trades": entries_total,
        "mae_pct_avg": sum(mae_values) / len(mae_values) if mae_values else None,
        "mfe_pct_avg": sum(mfe_values) / len(mfe_values) if mfe_values else None,
        "visual_status": _classify_visual_status(
            target_hits=target_hits,
            false_entries=len(false_entries),
            net_return_pct=net_return_pct,
        ),
        "hit_details": list(hit_by_entry_id.values()),
        "missed_target_details": missed_targets,
        "false_entry_details": false_entries,
        "duplicate_hit_details": duplicate_hits,
    }


def _classify_visual_status(
    *,
    target_hits: int,
    false_entries: int,
    net_return_pct: float,
) -> str:
    if target_hits <= 0:
        return "VISUAL_MISS"
    if false_entries > target_hits:
        return "VISUAL_HITS_WITH_TOO_MANY_FALSE_ENTRIES"
    if net_return_pct >= 0:
        return "VISUAL_PASS_TRADEFUL_POSITIVE"
    return "VISUAL_PASS_TRADEFUL_NEGATIVE"


def _trade_public_dict(trade: TradeEntry) -> dict[str, Any]:
    return {
        "trade_row_index": trade.row_index,
        "side": trade.side,
        "entry_time_utc": _format_time(trade.entry_time),
        "exit_time_utc": trade.exit_time_raw,
        "net_return": trade.net_return,
    }


def _lag_bars(entry_time: datetime, target_time: datetime) -> int:
    return round((entry_time - target_time).total_seconds() / 60.0)


def _format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_reports(
    score: dict[str, Any],
    *,
    manual_entries_path: Path,
    trades_csv_path: Path,
    out_dir: Path,
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"visual_entry_score_{manual_entries_path.parent.name}_{trades_csv_path.stem}"
    json_path = out_dir / f"{stem}.json"
    md_path = out_dir / f"{stem}_RU.md"
    json_path.write_text(json.dumps(score, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_build_markdown(score, manual_entries_path, trades_csv_path), encoding="utf-8")
    return json_path, md_path


def _build_markdown(
    score: dict[str, Any],
    manual_entries_path: Path,
    trades_csv_path: Path,
) -> str:
    lines = [
        "# Visual Entry Score",
        "",
        f"Manual entries: `{manual_entries_path}`.",
        f"Trades CSV: `{trades_csv_path}`.",
        "",
        "## Итог",
        "",
        f"- Статус: `{score['visual_status']}`",
        f"- Ручных целей: `{score['targets_total']}`",
        f"- Попаданий: `{score['target_hits']}`",
        f"- Пропусков: `{score['missed_targets']}`",
        f"- Лишних входов: `{score['false_entries']}`",
        f"- Всего входов backtest: `{score['entries_total']}`",
        f"- Precision: `{score['precision']:.6f}`",
        f"- Recall: `{score['recall']:.6f}`",
        f"- F1 visual: `{score['f1_visual']:.6f}`",
        f"- OOS net return pct: `{score['net_return_pct']:.6f}`",
        "",
        "## Попадания",
        "",
        "| manual_entry_id | target | matched | lag_bars | net_return |",
        "|---|---:|---:|---:|---:|",
    ]
    for hit in score["hit_details"]:
        lines.append(
            "| `{manual_entry_id}` | `{target_entry_time_utc}` | `{matched_entry_time_utc}` | `{lag_bars}` | `{net_return}` |".format(
                **hit
            )
        )
    lines.extend(["", "## Пропуски", "", "| manual_entry_id | target | side |", "|---|---:|---:|"])
    for missed in score["missed_target_details"]:
        lines.append(
            f"| `{missed['manual_entry_id']}` | `{missed['target_entry_time_utc']}` | `{missed['side']}` |"
        )
    lines.extend(["", "## Решение", ""])
    lines.append("Этот отчет является diagnostic-only. В ML ничего не передавать без validation/holdout и ручного `APPROVED_FOR_ML`.")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score backtest entries against manual visual entry markup.")
    parser.add_argument("--manual-entries", required=True)
    parser.add_argument("--trades-csv", required=True)
    parser.add_argument("--out-dir", default="reports/qa_gate")
    args = parser.parse_args(argv)

    manual_path = Path(args.manual_entries)
    trades_path = Path(args.trades_csv)
    _, manual_entries = load_manual_entries(manual_path)
    trade_entries = load_trade_entries(trades_path)
    score = score_entries(manual_entries, trade_entries)
    json_path, md_path = write_reports(
        score,
        manual_entries_path=manual_path,
        trades_csv_path=trades_path,
        out_dir=Path(args.out_dir),
    )
    print(json.dumps({"status": "OK", "json": str(json_path), "md": str(md_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
