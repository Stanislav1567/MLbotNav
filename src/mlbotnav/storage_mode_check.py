from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from mlbotnav.postgres_runtime import load_storage_runtime_config, postgres_smoke


def _file_mode_smoke(project_root: Path) -> dict:
    required_dirs = [
        project_root / "data" / "raw",
        project_root / "data" / "core",
        project_root / "data" / "meta",
        project_root / "data" / "dq",
    ]
    missing = [str(p) for p in required_dirs if not p.exists()]
    return {"required_dirs": [str(p) for p in required_dirs], "missing": missing, "ok": len(missing) == 0}


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    cfg = load_storage_runtime_config(project_root)
    out = {
        "run_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "mode": cfg.mode,
    }
    if cfg.mode == "postgres":
        out["smoke"] = postgres_smoke(project_root)
        ok = bool(out["smoke"].get("ok", False))
    else:
        out["smoke"] = _file_mode_smoke(project_root)
        ok = bool(out["smoke"].get("ok", False))
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
