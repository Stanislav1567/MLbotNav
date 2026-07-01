# Passport Result Register F001-F083

Status: `CLOSED_NO_PRODUCTION_GO`
Updated UTC: `2026-06-23T09:15:00Z`

This file is the compact result register for the current passport-driven calibration route.
It is a human control artifact, not an executable Optuna matrix.

## Source Chain

1. Main control index: `docs/CALIBRATION_NODE_CURRENT/PASSPORT_CONTROL_INDEX_RU.md`.
2. Passport registry: `configs/calibration_action_passports.yaml`.
3. Executable matrices: `configs/calibration_matrices/passport_actions/*.yaml`.
4. Result/audit artifacts: `reports/qa_gate/*`.

Old chronology and old broad Optuna matrices stay frozen references unless a feature is explicitly migrated through passport review.

## Decision Classes

| Class | Meaning |
|---|---|
| `NO_GO` | Do not promote. Result is negative, zero-trade, or not reliable enough. |
| `POSITIVE_TEST_CANDIDATE` | Positive isolated OOS result exists, but it is not production GO. Needs follow-up validation. |
| `ACCEPT_COMBINED` | Passport design decision accepted; this is not a performance promotion. |
| `DIAGNOSTIC_ONLY` | Run can be used for analysis, not as a selected candidate. |

## Current Top Decision

No feature from `F001-F083` is production GO.

Route closeout audit: `reports/qa_gate/f001_f083_route_closeout_audit_20260623T091500Z.md`.

Only one historical positive test candidate was found on the original one-day window:

| Feature | Side | Result | Trades | Status | Required Next Step |
|---|---:|---:|---:|---|---|
| `F051 BOS down` / `F051_BOSDOWN_ALLOW` | SHORT | `+2.810523%` | `1` | `VALIDATION_FAIL_NO_PROMOTION` | Multi-day validation failed on adjacent windows |

`F051 SHORT` must not be mixed into ML, combined blocks, or production routing. Follow-up validation on `2026-05-29`, `2026-05-30`, and `2026-05-31` OOS windows produced `0` trades.

## Compact Block Register

| Block | Feature IDs | Russian Comment | Current Decision | Notes |
|---|---|---|---|---|
| `B001` | `F001 F002 F003 F004 F005` | RET_N, return filters | `NO_GO / DIAGNOSTIC_ONLY` | Tournament/result traces are diagnostic; no production candidate. |
| `B002` | `F006` | HL spread | `NO_GO` | Standalone passport closed. |
| `B003` | `F007` | Rolling std20 | `NO_GO` | Standalone passport closed. |
| `B004` | `F008` | ATR14 | `NO_GO` | Standalone passport closed. |
| `B005` | `F009 F010 F011` | EMA filters | `NO_GO` | Group passport closed. |
| `B006` | `F012` | RSI14 | `NO_GO` | Standalone combined RSI passport closed. |
| `B007` | `F013 F014 F015` | MACD filters | `NO_GO` | Group passport closed. |
| `B008` | `F016` | ADX14 | `NO_GO` | Standalone passport closed. |
| `B009` | `F017 F018` | Stochastic %K/%D | `NO_GO / ACCEPT_COMBINED` | Keep one combined Stochastic passport; split is not required now. |
| `B010` | `F019 F020 F021` | Volume filters | `NO_GO` | Group passport closed. |
| `B011` | `F022` | OBV slope5 | `NO_GO` | Standalone passport closed. |
| `B012` | `F023` | MFI14 | `NO_GO` | Standalone passport closed. |
| `B026` | `F024` | VWAP distance | `NO_GO` | Late closure gap closed. |
| `B013` | `F025 F026 F027 F028 F029 F030 F031 F032 F033 F034` | Density / VPOC | `NO_GO` | All density/VPOC gaps closed; no promoted candidate. |
| `B014` | `F035 F036 F037 F038 F039` | Level / range / channel | `NO_GO` | F038/F039 stale-column risk fixed by allowlist hardening. |
| `B015` | `F040 F041` | Fibonacci anchor grid | `NO_GO` | Group passport closed. |
| `B016` | `F042 F043 F044` | Entry quality context | `NO_GO` | Group passport closed. |
| `B017` | `F045 F046 F047 F048 F049` | Breakout / retest | `NO_GO` | Group passport closed. |
| `B018` | `F050 F051 F052` | Market structure BOS/CHOCH | `VALIDATION_FAIL_NO_PROMOTION` for `F051 SHORT`; all other routes `NO_GO` | Original one-day positive did not reproduce on adjacent windows. |
| `B019` | `F053 F054 F055 F056 F057 F058 F059 F060` | Candle patterns | `NO_GO` | Group passport closed. |
| `B020` | `F061 F062 F063 F064 F065 F066` | Divergence patterns | `NO_GO` | Group passport closed. |
| `B021` | `F067 F068` | Pattern quality | `NO_GO` | Group passport closed. |
| `B022` | `F069 F070 F071 F072 F073 F074 F075 F076 F077` | Chart patterns | `NO_GO` | Group passport closed. |
| `B023` | `F078 F079` | Pattern confirmation | `NO_GO` | Group passport closed. |
| `B024` | `F080 F081` | Pattern composite entry | `NO_GO` | Group passport closed. |
| `B025` | `F082 F083` | Pattern trade context | `NO_GO` | Group passport closed. |

## Explicit Coverage IDs

`F001 F002 F003 F004 F005 F006 F007 F008 F009 F010 F011 F012 F013 F014 F015 F016 F017 F018 F019 F020 F021 F022 F023 F024 F025 F026 F027 F028 F029 F030 F031 F032 F033 F034 F035 F036 F037 F038 F039 F040 F041 F042 F043 F044 F045 F046 F047 F048 F049 F050 F051 F052 F053 F054 F055 F056 F057 F058 F059 F060 F061 F062 F063 F064 F065 F066 F067 F068 F069 F070 F071 F072 F073 F074 F075 F076 F077 F078 F079 F080 F081 F082 F083`

## Promotion Rules

1. `NO_GO` rows cannot be used as active candidates.
2. `F051 SHORT` failed follow-up validation and is not production GO.
3. Combined experiments must start from selected candidates only, not from whole historical blocks.
4. ML export is forbidden until a candidate has a separate acceptance audit.
5. Exit logic, timeout, TP, SL, and dynamic exit rules need their own passports before calibration changes.

## Next Action

Next strict task: choose a new passport/feature route, define a new validation idea, or start separate exit/risk passports. `F001-F083` is closed as `NO_PRODUCTION_GO` in the current route.
