# TZ Q4 Progress (2026-05-21)

Scope: security hardening and SLA service contour.

Completed:
- Security provider runtime extended beyond stubs:
  - `src/mlbotnav/security.py`
  - `env` provider: direct env secret resolution
  - `vault` provider: HTTP read path support (`VAULT_ADDR`, `VAULT_TOKEN`, `VAULT_KV_PATH`)
  - `kms` provider: runtime decrypt path support (`KMS_DECRYPT_ENDPOINT`) plus offline b64 fallback for local testing
- Security gate strengthened:
  - Vault now requires both address and token; TLS scheme check preserved.
- Bybit credentials now resolved via provider layer:
  - `src/mlbotnav/settings.py` now reads `BYBIT_API_KEY` and `BYBIT_API_SECRET` through `resolve_secret(...)`.
- Inference SLA service contour added:
  - new probe: `src/mlbotnav/inference_service_probe.py`
  - integrated into cycle: `src/mlbotnav/prod_cycle.py` (`run_inference_service_probe`)
  - SLA monitor extended: `src/mlbotnav/monitor_sla.py`
  - thresholds configured: `configs/prod_policy.yaml`
    - `min_inference_availability_pct: 99.5`
    - `max_inference_p95_latency_ms: 300.0`

Trade size policy alignment:
- Fixed trade notional is now first-class:
  - `notional_usd` default = `10`
  - backward compatibility kept for old `position_size` args.

Remaining for full Q4 closure:
- Run live acceptance in target environment for `vault`/`kms` providers and attach evidence reports.
- Run several production cycles and confirm SLA monitor has no active breaches on inference availability/p95.
