from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _bar_width_days(tf: str) -> float:
    if tf.endswith("d"):
        return int(tf[:-1]) * 0.7
    if tf.endswith("h"):
        return (int(tf[:-1]) * 60 / (24 * 60)) * 0.8
    return (int(tf[:-1]) / (24 * 60)) * 0.8


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_path(path_text: str) -> Path:
    p = Path(path_text)
    if p.is_absolute():
        return p
    return (_project_root() / p).resolve()


def _load_latest_raw(project_root: Path, day: str, tf: str, symbol: str) -> Path:
    base = project_root / "data" / "raw" / "bybit_ohlcv" / f"dt={day}" / f"tf={tf}" / f"symbol={symbol}"
    direct = base / "part-final.csv"
    if direct.exists():
        return direct
    files = sorted(base.glob("part-*.csv"))
    if not files:
        raise FileNotFoundError(f"No raw OHLCV files in {base}")
    return files[-1]


def _load_raw_range(project_root: Path, start_day: str, end_day: str, tf: str, symbol: str) -> pd.DataFrame:
    chunks: list[pd.DataFrame] = []
    for d in pd.date_range(start=start_day, end=end_day, freq="D"):
        path = _load_latest_raw(project_root, d.strftime("%Y-%m-%d"), tf, symbol)
        x = pd.read_csv(path)
        x["open_time_utc"] = pd.to_datetime(x["open_time_utc"], utc=True, errors="coerce")
        chunks.append(x)
    raw = pd.concat(chunks, ignore_index=True)
    raw = raw.dropna(subset=["open_time_utc"]).sort_values("open_time_utc")
    raw = raw.drop_duplicates(subset=["open_time_utc"]).reset_index(drop=True)
    return raw


def _side_after_thresholds(bt: pd.DataFrame, p_enter_long: float, p_enter_short: float, signal_mode: str) -> pd.Series:
    prob = pd.to_numeric(bt["prob_up"], errors="coerce").fillna(0.5)
    side = pd.Series(0, index=bt.index, dtype="int64")
    side.loc[prob >= float(p_enter_long)] = 1
    side.loc[prob <= float(p_enter_short)] = -1
    if signal_mode == "long_only":
        side.loc[side < 0] = 0
    elif signal_mode == "short_only":
        side.loc[side > 0] = 0
    return side


def _gate_pass(bt: pd.DataFrame, gate_columns: list[str], min_confirmations: int) -> pd.Series:
    if not gate_columns:
        return pd.Series(True, index=bt.index)
    confirmations = pd.Series(0, index=bt.index, dtype="int64")
    applicable = pd.Series(0, index=bt.index, dtype="int64")
    for col in gate_columns:
        if col not in bt.columns:
            continue
        confirmations += (pd.to_numeric(bt[col], errors="coerce").fillna(0.0) >= 1.0).astype("int64")
        applicable += 1
    required = applicable.clip(upper=max(1, int(min_confirmations)))
    return (applicable <= 0) | (confirmations >= required)


def _pred_move_proxy(bt: pd.DataFrame, hold_bars: int) -> pd.Series:
    prob = pd.to_numeric(bt["prob_up"], errors="coerce").fillna(0.5)
    atr = pd.to_numeric(bt.get("atr14", 0.0), errors="coerce").fillna(0.0).abs()
    conf = (prob - 0.5).abs().mul(2.0).clip(lower=0.0, upper=1.0)
    return conf.mul(atr).mul(math.sqrt(max(1, int(hold_bars))))


def _exit_index_for_trade(bt: pd.DataFrame, signal_idx: int, hold_bars: int) -> int:
    row = bt.iloc[signal_idx]
    exit_time = pd.to_datetime(row.get("exit_time_utc"), utc=True, errors="coerce")
    if pd.notna(exit_time) and "close_time_utc" in bt.columns:
        close_times = pd.to_datetime(bt["close_time_utc"], utc=True, errors="coerce")
        matches = close_times[close_times == exit_time]
        if not matches.empty:
            return int(matches.index[0])
    return min(len(bt) - 1, signal_idx + max(1, int(hold_bars)))


def _runtime_stage_masks(
    bt: pd.DataFrame,
    *,
    mode_side: pd.Series,
    gate_ok: pd.Series,
    pred_move_proxy: pd.Series,
    min_expected_move_pct: float,
    hold_bars: int,
    cooldown_bars: int,
) -> tuple[pd.Series, pd.Series, pd.Series]:
    after_mode = pd.Series(False, index=bt.index)
    after_gate = pd.Series(False, index=bt.index)
    after_min = pd.Series(False, index=bt.index)
    final_side = pd.to_numeric(bt["side"], errors="coerce").fillna(0).astype(int)
    i = 0
    n = len(bt)
    while i < n - 1:
        if int(mode_side.iloc[i]) == 0:
            i += 1
            continue
        after_mode.iloc[i] = True

        if not bool(gate_ok.iloc[i]):
            i += 1
            continue
        after_gate.iloc[i] = True

        if float(min_expected_move_pct) > 0 and float(pred_move_proxy.iloc[i]) < float(min_expected_move_pct):
            i += 1
            continue
        after_min.iloc[i] = True

        if int(final_side.iloc[i]) == 0:
            i += 1
            continue
        i = _exit_index_for_trade(bt, i, hold_bars) + 1 + max(0, int(cooldown_bars))
    return after_mode, after_gate, after_min


def _hour_counts(bt: pd.DataFrame, mask: pd.Series) -> dict[str, int]:
    if bt.empty:
        return {}
    x = bt.loc[mask, "open_time_utc"].dt.strftime("%H").value_counts().sort_index()
    return {str(k): int(v) for k, v in x.items()}


def _scatter_candidates(ax: Any, rows: pd.DataFrame, color: str, label: str, marker: str, size: int, alpha: float) -> None:
    if rows.empty:
        return
    ax.scatter(
        rows["open_time_utc"],
        rows["close"],
        marker=marker,
        s=size,
        color=color,
        alpha=alpha,
        label=label,
        zorder=4,
    )


def _trade_points(trades: pd.DataFrame) -> tuple[list[pd.Timestamp], list[float], list[pd.Timestamp], list[float], list[str], int, int]:
    entry_x: list[pd.Timestamp] = []
    entry_y: list[float] = []
    exit_x: list[pd.Timestamp] = []
    exit_y: list[float] = []
    exit_colors: list[str] = []
    long_count = 0
    short_count = 0
    for _, row in trades.iterrows():
        et = pd.to_datetime(row.get("entry_time_utc"), utc=True, errors="coerce")
        xt = pd.to_datetime(row.get("exit_time_utc"), utc=True, errors="coerce")
        ep = pd.to_numeric(pd.Series([row.get("entry_price")]), errors="coerce").iloc[0]
        xp = pd.to_numeric(pd.Series([row.get("exit_price")]), errors="coerce").iloc[0]
        if pd.isna(et) or pd.isna(xt) or pd.isna(ep) or pd.isna(xp):
            continue
        entry_x.append(et)
        entry_y.append(float(ep))
        exit_x.append(xt)
        exit_y.append(float(xp))
        side = int(row.get("side", 0))
        if side > 0:
            long_count += 1
        elif side < 0:
            short_count += 1
        ret = float(pd.to_numeric(pd.Series([row.get("net_return", 0.0)]), errors="coerce").fillna(0.0).iloc[0])
        exit_colors.append("#00e676" if ret > 0 else "#ff1744")
    return entry_x, entry_y, exit_x, exit_y, exit_colors, long_count, short_count


def main() -> int:
    parser = argparse.ArgumentParser(description="Render full-day gate diagnostic: mode -> F-gate -> min_move -> trades.")
    parser.add_argument("--oos-report", required=True)
    args = parser.parse_args()

    root = _project_root()
    report_path = _resolve_path(args.oos_report)
    report = _load_json(report_path)
    symbol = str(report.get("symbol", "SOLUSDT"))
    timeframe = str(report.get("timeframe", "1m"))
    start_day = str(report.get("test_day") or report.get("test_start"))
    end_day = str(report.get("test_end_day") or report.get("test_end") or start_day)
    strategy = dict(report.get("strategy") or {})
    risk = dict(report.get("risk_policy") or {})
    bt_info = dict(report.get("backtest") or {})
    diag = dict(bt_info.get("trend_filter_diagnostics") or {})
    signal_mode = str(risk.get("signal_mode") or bt_info.get("signal_mode") or "both")
    hold_bars = int(bt_info.get("hold_bars") or strategy.get("horizon_bars") or 1)
    p_enter_long = float(strategy.get("p_enter_long", 0.52))
    p_enter_short = float(strategy.get("p_enter_short", 0.48))
    min_move = float(risk.get("min_expected_move_pct") or bt_info.get("min_expected_move_pct") or 0.0)
    cooldown_bars = int(risk.get("cooldown_bars") or bt_info.get("cooldown_bars") or 0)
    gate_columns = [str(x) for x in diag.get("entry_action_gate_columns", [])]
    min_confirmations = int(diag.get("entry_action_min_confirmations") or 1)

    artifacts = dict(report.get("artifacts") or {})
    bt_path = _resolve_path(str(artifacts.get("backtest_path", "")))
    if not bt_path.exists():
        raise FileNotFoundError(f"Backtest CSV not found: {bt_path}")

    raw = _load_raw_range(root, start_day, end_day, timeframe, symbol)
    raw["ema20"] = raw["close"].ewm(span=20, adjust=False).mean()
    raw["ema50"] = raw["close"].ewm(span=50, adjust=False).mean()
    bt = pd.read_csv(bt_path)
    bt["open_time_utc"] = pd.to_datetime(bt["open_time_utc"], utc=True, errors="coerce")
    bt = bt.dropna(subset=["open_time_utc"]).copy()
    bt["close"] = pd.to_numeric(bt["close"], errors="coerce")

    mode_side = _side_after_thresholds(bt, p_enter_long, p_enter_short, signal_mode)
    gate_ok = _gate_pass(bt, gate_columns, min_confirmations)
    proxy = _pred_move_proxy(bt, hold_bars)
    after_mode, after_gate, after_min = _runtime_stage_masks(
        bt,
        mode_side=mode_side,
        gate_ok=gate_ok,
        pred_move_proxy=proxy,
        min_expected_move_pct=min_move,
        hold_bars=hold_bars,
        cooldown_bars=cooldown_bars,
    )
    final_trades = bt[pd.to_numeric(bt["side"], errors="coerce").fillna(0).astype(int) != 0].copy()

    x = mdates.date2num(raw["open_time_utc"].to_numpy())
    width = _bar_width_days(timeframe)
    up = raw["close"] >= raw["open"]

    fig, (ax_price, ax_vol) = plt.subplots(
        2,
        1,
        figsize=(22, 11),
        sharex=True,
        gridspec_kw={"height_ratios": [4.2, 1.2]},
    )
    bg = "#101418"
    fig.patch.set_facecolor(bg)
    ax_price.set_facecolor(bg)
    ax_vol.set_facecolor(bg)

    up_color = "#26a69a"
    down_color = "#ef5350"
    ax_price.vlines(x, raw["low"], raw["high"], color="#cfd8dc", linewidth=0.65, alpha=0.82, zorder=1)
    for i in range(len(raw)):
        o = float(raw.iloc[i]["open"])
        c = float(raw.iloc[i]["close"])
        lower = min(o, c)
        height = max(abs(c - o), 1e-8)
        color = up_color if c >= o else down_color
        ax_price.add_patch(Rectangle((x[i] - width / 2, lower), width, height, facecolor=color, edgecolor=color, linewidth=0.45))

    ax_price.plot(raw["open_time_utc"], raw["ema20"], color="#ffd54f", linewidth=0.95, label="EMA20")
    ax_price.plot(raw["open_time_utc"], raw["ema50"], color="#64b5f6", linewidth=0.95, label="EMA50")
    ax_vol.bar(raw["open_time_utc"], raw["volume"], width=width, color=[up_color if b else down_color for b in up], alpha=0.78)

    _scatter_candidates(ax_price, bt.loc[after_mode], "#8e8e8e", "after mode", ".", 11, 0.22)
    _scatter_candidates(ax_price, bt.loc[after_gate], "#ffb300", "after F-gate", "o", 20, 0.45)
    _scatter_candidates(ax_price, bt.loc[after_min], "#29b6f6", "after min_move", "D", 40, 0.9)

    entry_x, entry_y, exit_x, exit_y, exit_colors, long_count, short_count = _trade_points(final_trades)
    if entry_x:
        entry_marker = "^" if signal_mode == "long_only" else "v" if signal_mode == "short_only" else "^"
        entry_color = "#00e676" if signal_mode == "long_only" else "#ff1744" if signal_mode == "short_only" else "#00e676"
        ax_price.scatter(entry_x, entry_y, marker=entry_marker, s=95, color=entry_color, label="real entry", zorder=6)
    if exit_x:
        ax_price.scatter(exit_x, exit_y, marker="x", s=70, c=exit_colors, linewidths=1.5, label="real exit", zorder=6)

    title = (
        f"{symbol} {timeframe} {start_day}..{end_day} UTC | {signal_mode} | "
        f"mode={int(after_mode.sum())}, F-gate={int(after_gate.sum())}, "
        f"min_move={int(after_min.sum())}, trades={int(len(final_trades))}"
    )
    ax_price.set_title(title, color="white", fontsize=14, pad=10)
    ax_price.set_ylabel("Price", color="white")
    ax_vol.set_ylabel("Volume", color="white")
    ax_vol.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    for ax in (ax_price, ax_vol):
        ax.grid(color="#2f3a40", alpha=0.42, linewidth=0.55)
        ax.tick_params(colors="#e0e0e0")
        for sp in ax.spines.values():
            sp.set_color("#3a444b")
    ax_price.legend(facecolor="#172026", edgecolor="#3a444b", labelcolor="white", fontsize=9, loc="upper left", ncol=6)
    fig.autofmt_xdate()
    plt.tight_layout()

    out_dir = root / "reports" / "final_review"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    day_tag = start_day if end_day == start_day else f"{start_day}_to_{end_day}"
    out_png = out_dir / f"gate_diagnostic_{symbol}_{timeframe}_{day_tag}_{signal_mode}_{ts}.png"
    out_json = out_dir / f"gate_diagnostic_{symbol}_{timeframe}_{day_tag}_{signal_mode}_{ts}.json"
    plt.savefig(out_png, dpi=170, facecolor=fig.get_facecolor())
    plt.close(fig)

    summary = {
        "oos_report": str(report_path),
        "backtest_path": str(bt_path),
        "visual_png": str(out_png),
        "symbol": symbol,
        "timeframe": timeframe,
        "test_start": start_day,
        "test_end": end_day,
        "signal_mode": signal_mode,
        "raw_candles": int(len(raw)),
        "backtest_rows": int(len(bt)),
        "backtest_first_time": str(bt["open_time_utc"].min()),
        "backtest_last_time": str(bt["open_time_utc"].max()),
        "p_enter_long": p_enter_long,
        "p_enter_short": p_enter_short,
        "hold_bars": hold_bars,
        "cooldown_bars": cooldown_bars,
        "entry_action_gate_columns": gate_columns,
        "entry_action_min_confirmations": min_confirmations,
        "min_expected_move_pct": min_move,
        "after_mode": int(after_mode.sum()),
        "after_f_gate": int(after_gate.sum()),
        "after_min_move": int(after_min.sum()),
        "real_trades": int(len(final_trades)),
        "real_long_entries": int(long_count),
        "real_short_entries": int(short_count),
        "after_f_gate_by_hour_utc": _hour_counts(bt, after_gate),
        "after_min_move_by_hour_utc": _hour_counts(bt, after_min),
    }
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"visual_png": str(out_png), "summary_json": str(out_json), "summary": summary}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
