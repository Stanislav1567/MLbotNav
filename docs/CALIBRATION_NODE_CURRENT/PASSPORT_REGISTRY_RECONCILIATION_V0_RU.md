# Passport Registry Reconciliation V0

Дата фиксации: `2026-07-01`.

Статус: `V2A0_REGISTRY_RECONCILIATION_READY_NO_SCORER_NO_ML_NO_OPTUNA`.

## Смысл

Паспорта уже собраны. Этот файл фиксирует не создание новых паспортов, а сверку существующих связок перед visual overlay на двух эталонах `M01..M19` и `T15L02/T15L06/T15L07/T15L08/T15L11/T15L13/T15L16`.

Проверенные источники:

```text
configs/calibration_action_passports.yaml
docs/CALIBRATION_NODE_CURRENT/passports/features/*.md
configs/calibration_matrices/passport_actions/*.yaml
```

## Итог сверки

| check | result |
|---|---|
| Блоки `B001..B026` | `26` |
| Активные не отключенные `Fxxx` связки | `82` |
| Активные matrix YAML | `82` |
| Найдены `passport_path` и `active_matrix_path` | `82/82` |
| Отключенный diagnostic | `B001_RET_N_TOURNAMENT` |

Граница: это manifest-сверка, не scorer, не target-lock, не Optuna и не ML.

## Блоки и активные связки

| block | group | name | active count | action ids | overlay role |
|---|---|---|---:|---|---|
| `B001` | `price_volatility` | Цена и волатильность | `5` | `F001_RET1_ALLOW`, `F002_RET3_ALLOW`, `F003_RET6_ALLOW`, `F004_RET12_ALLOW`, `F005_RET24_ALLOW` | context later |
| `B002` | `price_volatility` | Диапазон свечи High-Low | `1` | `F006_HLSPREAD_ALLOW` | context later |
| `B003` | `price_volatility` | Скользящая волатильность 20 | `1` | `F007_RSTD20_ALLOW` | context later |
| `B004` | `price_volatility` | ATR14 волатильность | `1` | `F008_ATR14_ALLOW` | context later |
| `B005` | `trend_momentum` | EMA тренд и наклон | `3` | `F009_EMAGAP_ALLOW`, `F010_EMASLOPE5_ALLOW`, `F011_EMA200GAP_ALLOW` | deferred/reference |
| `B006` | `trend_momentum` | RSI14 impulse | `1` | `F012_RSI14_ALLOW` | momentum layer |
| `B007` | `trend_momentum` | MACD импульс | `3` | `F013_MACDLINE_ALLOW`, `F014_MACDSIGNAL_ALLOW`, `F015_MACDHIST_ALLOW` | momentum layer |
| `B008` | `trend_momentum` | ADX14 сила тренда | `1` | `F016_ADX14_ALLOW` | later |
| `B009` | `trend_momentum` | Stochastic 14 K/D | `1` | `F017_F018_STOCH14_ALLOW` | later |
| `B010` | `volume_flow` | Объем и поток | `3` | `F019_VOLCHG_ALLOW`, `F020_VOLZ20_ALLOW`, `F021_DELTAVOL_ALLOW` | flow layer |
| `B011` | `volume_flow` | OBV slope 5 | `1` | `F022_OBVSLOPE5_ALLOW` | flow later |
| `B012` | `volume_flow` | MFI14 | `1` | `F023_MFI14_ALLOW` | flow later |
| `B013` | `density_profile` | DENSITY_A VPOC core | `10` | `F025_VPOCDIST60_ALLOW`, `F026_BINSHARE60_ALLOW`, `F027_CLUSTERSHARE60_ALLOW`, `F028_VPOCSHARE60_ALLOW`, `F029_VPOCDIST240_ALLOW`, `F030_BINSHARE240_ALLOW`, `F031_CLUSTERSHARE240_ALLOW`, `F032_VPOCSHARE240_ALLOW`, `F033_VPOCDRIFT20_ALLOW`, `F034_CLUSTERRATIO_ALLOW` | density layer |
| `B014` | `structure_ta` | LEVEL_A уровни поддержки/сопротивления | `5` | `F035_SUPPORTDIST_ALLOW`, `F036_RESDIST_ALLOW`, `F037_LEVELSTRENGTH_ALLOW`, `F038_RANGEPOSE_ALLOW`, `F039_CHANNELPOS_ALLOW` | structure layer |
| `B015` | `structure_ta` | FIBONACCI_GRID anchor grid | `2` | `F040_FIB0382DIST_ALLOW`, `F041_FIB0618DIST_ALLOW` | structure layer |
| `B016` | `structure_ta` | ENTRY_QUALITY_CONTEXT контекст входа | `3` | `F042_TPCONTEXT_ALLOW`, `F043_SLCONTEXT_ALLOW`, `F044_RRCONTEXT_ALLOW` | muted/context-only |
| `B017` | `structure_ta` | BREAKOUT_RETEST пробой/ретест | `5` | `F048_SWINGHIGHBREAK_ALLOW`, `F049_SWINGLOWBREAK_ALLOW`, `F045_BREAKOUT_ALLOW`, `F047_RETEST_ALLOW`, `F046_FALSEBREAK_ALLOW` | structure layer |
| `B018` | `structure_ta` | MARKET_STRUCTURE BOS/CHOCH | `3` | `F050_BOSUP_ALLOW`, `F051_BOSDOWN_ALLOW`, `F052_CHOCH_ALLOW` | structure layer |
| `B019` | `pattern` | CANDLE_PATTERNS свечные паттерны | `8` | `F055_PINBULL_ALLOW`, `F056_PINBEAR_ALLOW`, `F059_ENGULFBULL_ALLOW`, `F060_ENGULFBEAR_ALLOW`, `F057_HAMMER_ALLOW`, `F058_SHOOTINGSTAR_ALLOW`, `F054_INSIDEBAR_ALLOW`, `F053_DOJI_ALLOW` | pattern later |
| `B020` | `pattern` | DIVERGENCE_PATTERNS дивергенции | `6` | `F061_RSIBULLDIV_ALLOW`, `F062_RSIBEARDIV_ALLOW`, `F063_MACDBULLDIV_ALLOW`, `F064_MACDBEARDIV_ALLOW`, `F065_OBVBULLDIV_ALLOW`, `F066_OBVBEARDIV_ALLOW` | pattern later |
| `B021` | `pattern` | PATTERN_QUALITY качество паттерна | `2` | `F067_PATTERNSTRENGTH_ALLOW`, `F068_PATTERNAGE_ALLOW` | pattern later |
| `B022` | `pattern` | CHART_PATTERNS графические паттерны | `9` | `F069_DOUBLEBOTTOM_ALLOW`, `F070_DOUBLETOP_ALLOW`, `F071_HEADSHOULDERS_ALLOW`, `F072_INVHEADSHOULDERS_ALLOW`, `F073_TRIANGLE_ALLOW`, `F074_PENNANT_ALLOW`, `F075_WEDGERISING_ALLOW`, `F076_WEDGEFALLING_ALLOW`, `F077_RANGEFLAG_ALLOW` | pattern later |
| `B023` | `pattern` | PATTERN_CONFIRMATION | `2` | `F078_PATTERNVOLCONF_ALLOW`, `F079_PATTERNLEVELCONF_ALLOW` | pattern later |
| `B024` | `pattern` | PATTERN_COMPOSITE_ENTRY | `2` | `F080_PATTERNLONG_ALLOW`, `F081_PATTERNSHORT_ALLOW` | pattern later |
| `B025` | `pattern` | PATTERN_TRADE_CONTEXT | `2` | `F082_PATTERNSLBUF_ALLOW`, `F083_PATTERNTPLADDER_ALLOW` | unsafe/context-only |
| `B026` | `volume_flow` | VWAP distance | `1` | `F024_VWAPDIST_ALLOW` | flow layer |

## Первый порядок overlay

1. `V2A_STRUCTURE_LAYER`: `B014`, `B015`, `B017`, `B018`; `B016` только muted/context.
2. `V2B_FLOW_DENSITY_LAYER`: `B010`, `B013`, `B026`; `B011/B012` позже при необходимости.
3. `V2C_MOMENTUM_LAYER`: `B006`, `B007`; `B005` EMA остается reference/deferred.
4. `V2D_PATTERN_LAYER`: `B019-B024` после отдельной проверки pattern windows; `B025` не брать active из-за SL/TP риска.
5. `V2E_SUMMARY_MATRIX`: входы `19+7` против слоев `structure/flow/momentum/pattern`.

## Правило локального участка

Full-day график остается полной картой дня. Стратегия считается локальным участком внутри дня:

```text
left_context до signal -> signal close -> entry next open -> правая зона только для глаз
```

Fibo натягивать по подтвержденной ноге и pivot pair, BOS/CHOCH считать по scope структуры, retest считать по event memory. Если паспорт светится по всему дню, это шумовой флаг.
