# STAS1 GOOD LOW REVIEW

Статус: `STAS1_V0_BASELINE_MAIN_LOW_REVIEW_SCRIPT_NO_ML_NO_OPTUNA`.

## Блок 1: прогон low-кандидатов зафиксирован

Статус: `STAS1_BLOCK_1_RUN_POOL_LOCKED_NO_ML_NO_OPTUNA`.

Что уже умеем и считаем рабочим baseline:

1. запускать прогон по одному дню или диапазону дней;
2. получать из прогона все найденные low-кандидаты входа;
3. сохранять общий график дня, closeup-страницы, CSV/JSON/Markdown-отчет;
4. открывать результаты через `BROWSE_BY_DAY/`, чтобы по одному дню листать сделки по порядку;
5. показывать `GOOD` и `BAD` вместе для ручной чистки шума;
6. менять целевой процент движения цены:
   - `run_day_1pct.ps1` = проверка `+1%`;
   - `run_day_0p5.ps1` = проверка `+0.5%`;
   - внутри Python-ядра есть параметр `--target-pct`;
7. чем меньше target-процент, тем больше сделок обычно закрывается и тем больше материала для review;
8. проверять закрытие после полуночи через `-OutcomeLookaheadHours`, не создавая новых входов за пределами выбранного периода.

Главный смысл блока: это рабочий генератор review-пула входов. Он не является ML, Optuna, scorer, target-lock или торговым API.

Дальше в новом чате не пересобирать этот блок заново. Следующий рабочий этап: чистить шум low-кандидатов, фиксировать ручной feedback и улучшать фильтр значимого low.

## Carry outcome через ночь

С `2026-07-06` STAS1 поддерживает bounded outcome-window: входы генерируются только внутри выбранного диапазона `-Day .. -EndDay`, но проверка достижения цели может смотреть дальше полуночи.

Это нужно для случаев, когда вход был в конце дня, а `+1%` закрылся на следующем дне.

Граница важная:

1. сделки до `-Day` не подтягиваются;
2. новые входы после `-EndDay` не создаются;
3. будущие свечи используются только как offline outcome label;
4. это не feature входа, не scorer, не target-lock, не Optuna и не ML/export.

В CSV/JSON добавлены поля:

```text
outcome_lookahead_hours
outcome_check_end_time_utc
hit_day_utc
hold_minutes_to_target
carried_overnight
outcome_status
```

Проверочный запуск на два дня с окном `48h`:

```powershell
$env:PYTHONPATH='src'
.\STAS1_GOOD_LOW_REVIEW\run_day_1pct.ps1 -Day 2026-05-07 -EndDay 2026-05-08 -OutcomeLookaheadHours 48 -RunLabel stas1_20260507_20260508_carry48_v0 -RenderGoodLimit 0
```

Открыть дневной просмотр:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open browse
```

## Что это

`STAS1` - видная рабочая папка для текущего основного скрипта поиска long low-кандидатов.

Движок не переносим и не дублируем. Основной Python-скрипт остается в проекте:

```text
src/mlbotnav/visual_entry_good_1pct_review_pool.py
```

Он использует low-кандидаты из:

```text
src/mlbotnav/visual_entry_low_anchor_suggester.py
```

## Для чего

Текущий процесс:

1. Берем один день.
2. Прогоняем `+1%` или `+0.5%`.
3. Смотрим PNG глазами.
4. Пользователь отмечает шум: плохие low, дубли, мимо-входы, места для сдвига.
5. Feedback сохраняем отдельно.
6. После нескольких дней правим фильтр значимого low.
7. Снова прогоняем тем же скриптом и сравниваем.

## Что не делаем

Этот контур не является:

1. ML/export/training;
2. Optuna;
3. scorer;
4. target-lock;
5. торговым API.

`+1%` и `+0.5%` используются только как offline outcome label для ручного review, а не как causal feature входа.

## Быстрый запуск

Один день `+1%`:

```powershell
.\STAS1_GOOD_LOW_REVIEW\run_day_1pct.ps1 -Day 2026-05-02
```

Диапазон дней `+1%`:

```powershell
.\STAS1_GOOD_LOW_REVIEW\run_day_1pct.ps1 -Day 2026-05-03 -EndDay 2026-05-09 -RunLabel stas1_20260503_20260509_1pct_anchor_next_open_fix_v0
```

Один день `+0.5%`:

```powershell
.\STAS1_GOOD_LOW_REVIEW\run_day_0p5.ps1 -Day 2026-05-02
```

Диапазон дней `+0.5%`:

```powershell
.\STAS1_GOOD_LOW_REVIEW\run_day_0p5.ps1 -Day 2026-05-03 -EndDay 2026-05-09 -RunLabel stas1_20260503_20260509_0p5_anchor_next_open_fix_v0
```

Открыть последний результат:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1
```

Открыть папку последнего результата:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open folder
```

## Где будут результаты

Новые `STAS1`-прогоны сохраняются сюда:

```text
STAS1_GOOD_LOW_REVIEW/runs/
```

Ручные пометки пользователя складывать сюда:

```text
STAS1_GOOD_LOW_REVIEW/feedback/
```

Слепки рабочих версий и zip-архивы складывать сюда:

```text
STAS1_GOOD_LOW_REVIEW/snapshots/
```

## Базовые уже существующие runs

Старые рабочие 21-дневные прогоны остаются архивом и источником сравнения:

```text
reports/final_review/visual_entry_v3/fresh_target_led/good_1pct_review_pool/W18_W20_learning_20260702_082819
reports/final_review/visual_entry_v3/fresh_target_led/good_1pct_review_pool/W18_W20_learning_0p5_20260702_124701
```

`1%` run: `1528` кандидатов, `573` GOOD, `955` BAD.

`0.5%` run: `1528` кандидатов, `938` GOOD, `590` BAD.

## Главное правило

Правим не смысл `+1%`, а шум в выборе low. Главная зона будущей калибровки:

```text
src/mlbotnav/visual_entry_low_anchor_suggester.py
```

После фикса `2026-07-03` базовый контракт входа такой:

1. `anchor_idx` = фактическая low-свеча;
2. `signal_idx = anchor_idx`;
3. `entry_idx = anchor_idx + 1`;
4. LONG-цена для проверки = `entry_open * (1 + 5 / 10000)`;
5. `confirmation_idx` хранится только как справка, но не двигает вход.

Контрольный run: `STAS1_GOOD_LOW_REVIEW/runs/stas1_20260502_1pct_anchor_next_open_fix_v0_20260703_165034`.

Фикс считается примененным в STAS1: wrapper-скрипты `run_day_1pct.ps1` и `run_day_0p5.ps1` поддерживают `-EndDay`, а ядро входа держит правило `low -> next open +5bps`.

## ALL closeups: GOOD + BAD

С `2026-07-06` в STAS1 добавлен отдельный визуальный слой для ручной чистки датасета:

1. `GOOD` остается зеленым треугольником;
2. `BAD` показывается красным полупрозрачным крестом;
3. оба класса попадают в отдельные страницы `GOOD_1PCT_REVIEW_POOL_ALL_CLOSEUPS_PAGE_*.png`;
4. старые страницы `GOOD_1PCT_REVIEW_POOL_GOOD_CLOSEUPS_PAGE_*.png` сохранены и по-прежнему показывают только хорошие входы.

Открыть последние страницы со всеми входами:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open allcloseups
```

Открыть overview, GOOD closeups и ALL closeups вместе:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open all
```

Контрольный run:

```text
STAS1_GOOD_LOW_REVIEW/runs/stas1_20260503_all_closeups_bad_x_v0_20260706_060244
```

Итог контрольного run `2026-05-03`: `58` кандидатов, `36` GOOD, `22` BAD, `8` страниц ALL closeups.

## Browse by day

С `2026-07-06` каждый новый STAS1 run создает удобную папку просмотра:

```text
BROWSE_BY_DAY/
  00_RUN_INDEX.png
  00_RUN_INDEX_RU.md
  2026-05-04/
    00_20260504_OVERVIEW.png
    01_20260504_ALL_CLOSEUPS_PAGE_01.png
    02_20260504_ALL_CLOSEUPS_PAGE_02.png
    ...
    20260504_RECORDS.csv
```

Смысл: открыть день один раз и листать стрелками только его графики по времени, без десятков окон.

Открыть индекс последнего run:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open index
```

Открыть папку дневного просмотра последнего run:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open browse
```

Открыть конкретный день последнего run:

```powershell
.\STAS1_GOOD_LOW_REVIEW\open_last_run.ps1 -Open day -Day 2026-05-04
```

`-Open all` и `-Open allcloseups` больше не открывают все PNG отдельными окнами; они открывают один стартовый файл для просмотра.
