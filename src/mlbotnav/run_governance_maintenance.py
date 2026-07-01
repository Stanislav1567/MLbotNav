from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from mlbotnav.governance import run_governance_maintenance


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    result = run_governance_maintenance(project_root)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = project_root / "reports" / "governance"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"governance_maintenance_{ts}.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report_path": str(out_path), "secret_leak_findings_count": result["secret_leak_findings_count"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
