# Security Runtime Policy Minimum (ML Non-Calibration)

Дата (UTC): 2026-05-27T07:36:34Z
Контур: основной ML runtime, без отдельного калибровочного блока.

## Минимум, который теперь обязателен
1. `deployment_gate` по умолчанию включает `require_security_gate=true`.
2. Promote блокируется, если `run_security_gate` вернул `allowed=false`.
3. Проверки security-gate:
   - валидный `required_provider` (`env|vault|kms`);
   - TLS для `vault` (`https`);
   - KMS-key и endpoint при `allow_fallback=false`;
   - at-rest encryption включен (`STORAGE_ENCRYPTION_ENABLED=true`);
   - provider parity для at-rest (`STORAGE_ENCRYPTION_PROVIDER` соответствует `required_provider` для `vault/kms`).

## Проверка
1. Регресс-тест:
   - `tests/test_release_gate.py::test_security_gate_defaults_to_hard_enabled`
2. Профильные security-тесты:
   - `tests/test_security_gate.py`
   - `tests/test_security_providers.py`

## Что это дает
1. Security-policy больше не опциональна по умолчанию в release-контуре.
2. Любой promote без минимально корректной secret/encryption конфигурации блокируется автоматически.
