from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from mlbotnav.readiness import enforce_action_allowed


def _latest_csv(project_root: Path, day: str, tf: str, symbol: str) -> Path:
    base = project_root / "data" / "raw" / "bybit_ohlcv" / f"dt={day}" / f"tf={tf}" / f"symbol={symbol}"
    if not base.exists():
        raise FileNotFoundError(f"No ingested data dir: {base}")
    files = sorted(base.glob("part-*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV parts in: {base}")
    return files[-1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Train baseline model from ingested OHLCV")
    parser.add_argument("--date", required=True, help="UTC date YYYY-MM-DD")
    parser.add_argument("--timeframe", default="1m", help="timeframe folder, e.g. 1m")
    parser.add_argument("--symbol", default="SOLUSDT", help="symbol folder, e.g. SOLUSDT")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    enforce_action_allowed(project_root, action="train_baseline")
    csv_path = _latest_csv(project_root, args.date, args.timeframe, args.symbol)
    df = pd.read_csv(csv_path)
    df["open_time_utc"] = pd.to_datetime(df["open_time_utc"], utc=True)
    df = df.sort_values("open_time_utc").reset_index(drop=True)

    # Simple baseline features for first model spin-up.
    df["ret_1"] = df["close"].pct_change(1)
    df["ret_3"] = df["close"].pct_change(3)
    df["hl_spread"] = (df["high"] - df["low"]) / df["open"].replace(0, np.nan)
    df["vol_chg"] = df["volume"].pct_change(1)
    df["target"] = (df["close"].shift(-1) > df["close"]).astype(int)
    df = df.dropna().reset_index(drop=True)

    features = ["ret_1", "ret_3", "hl_spread", "vol_chg"]
    x = df[features]
    y = df["target"]

    split = int(len(df) * 0.8)
    x_train, x_test = x.iloc[:split], x.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]

    model = LogisticRegression(max_iter=400)
    model.fit(x_train, y_train)
    pred = model.predict(x_test)

    metrics = {
        "date": args.date,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "rows_total": int(len(df)),
        "rows_train": int(len(x_train)),
        "rows_test": int(len(x_test)),
        "accuracy": float(accuracy_score(y_test, pred)),
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "f1": float(f1_score(y_test, pred, zero_division=0)),
    }

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    model_dir = project_root / "models" / "baseline"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / f"logreg_{args.symbol}_{args.timeframe}_{args.date}_{ts}.joblib"
    joblib.dump({"model": model, "features": features}, model_path)

    report_dir = project_root / "reports" / "training"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"baseline_{args.symbol}_{args.timeframe}_{args.date}_{ts}.json"
    report_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({"model_path": str(model_path), "report_path": str(report_path), "metrics": metrics}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
