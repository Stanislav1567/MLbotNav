# TZ Q3 Progress (2026-05-21)

Scope: section-21 SQL/runtime parity for storage and DQ traceability.

Completed:
- Added `dq.gap_events` table to runtime DDL:
  - `sql/postgres_storage_runtime.sql`
- Added Postgres writer for gap events:
  - `src/mlbotnav/postgres_runtime.py` (`pg_append_gap_events`)
- Extended Postgres smoke check to require `dq.gap_events`.
- Added file/postgres unified append API for gap events:
  - `src/mlbotnav/meta_store.py` (`append_gap_events`)
- Added deterministic gap event detection helpers:
  - `src/mlbotnav/dq.py` (`detect_gap_events_for_step`, `detect_gap_events`)
- Switched DQ gap counting to event-based counting (`gap_count = len(gap_events)`).
- Wired gap event persistence into ingestion runtimes:
  - `src/mlbotnav/ingest_day.py`
  - `src/mlbotnav/ingest_incremental.py`
  - `src/mlbotnav/ingest_context_day.py`

Result:
- Runtime now stores both aggregate gap metric (`gap_count`) and per-gap evidence (`gap_events`) in both storage modes (`file` and `postgres`).

Remaining for full Q3 closure:
- Align additional strict CHECK constraints/enums from original section-21 spec where still absent.
- Run live Postgres smoke in target environment and attach report artifact.
