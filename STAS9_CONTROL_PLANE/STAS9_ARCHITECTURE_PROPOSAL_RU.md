# Предлагаемая архитектура STAS9

Статус: `PROPOSAL_READY_NOT_IMPLEMENTED`.

Дата: `2026-07-23`.

## 1. Роль STAS9

STAS9 должен быть не новой торговой моделью, а control plane над существующими исследовательскими и ML-контурами.

Главная формула:

```text
реестры + lineage + guards + approvals + read-only adapters
-> однозначный выбор разрешенного артефакта
-> воспроизводимый запуск
-> отчет без изменения старой истории
```

## 2. Слои

### 2.1. Registry Layer

Хранит:

1. карту STAS-версий;
2. модельный реестр;
3. feature contracts;
4. технические задания;
5. статусы approval и quarantine.

Текущие файлы этого слоя уже созданы в `STAS9_CONTROL_PLANE/`.

### 2.2. Read-Only Adapter Layer

Отдельный adapter на каждый контур:

```text
stas1_adapter -> candidate manifests
stas2_adapter -> causal context manifests
stas3_adapter -> post-entry audit only
stas4_adapter -> teacher/hypothesis metadata
stas5_adapter -> model/feature/guard manifests
stas8_adapter -> disabled preview metadata
```

Adapter не импортирует старый контур как бесконтрольную библиотеку. Он читает только документированный manifest и проверяет контракт.

### 2.3. Lineage Layer

Для каждого результата строится цепочка:

```text
source data
-> candidate set
-> feature allowlist
-> labels/targets
-> train run
-> model artifact
-> forward run
-> review decision
```

Каждое ребро содержит path, SHA256, date range и status.

### 2.4. Gate Layer

Предлагаемые обязательные gates:

1. `PATH_EXISTENCE_GATE`;
2. `SOURCE_OF_TRUTH_GATE`;
3. `FEATURE_CONTRACT_GATE`;
4. `NO_FUTURE_GATE`;
5. `TRAIN_FORWARD_SPLIT_GATE`;
6. `MODEL_MANIFEST_GATE`;
7. `HUMAN_APPROVAL_GATE`;
8. `LEGACY_MUTATION_GATE`;
9. `PRODUCTION_POINTER_GATE`.

Любой FAIL блокирует изменение внешнего состояния, но не блокирует read-only аудит.

### 2.5. Orchestration Layer

STAS9 должен запускать не внутренние функции старых версий, а утвержденные команды через декларативный run plan:

```yaml
action_id: STAS9_RUN_...
source_version: STAS5_V5C_R4BB
mode: audit_only
dataset_id: ...
feature_contract: STAS5_V5C_X463
model_id: ...
forward_window: ...
required_gates: [...]
write_scope: STAS9_CONTROL_PLANE/runs/<run_id>
```

Первая реализация orchestration должна поддерживать только `inventory`, `validate` и `report`. `train`, `forward` и `promote` добавляются позже отдельными разрешениями.

### 2.6. Report Layer

Единый отчет должен показывать:

1. что выбрано;
2. почему выбрано;
3. какие источники прочитаны;
4. какие gates прошли;
5. какие файлы отсутствуют;
6. какие артефакты являются blind/teacher/audit;
7. что было записано;
8. что осталось неизменным.

## 3. Предлагаемая структура каталогов

```text
STAS9_CONTROL_PLANE/
  README_RU.md
  PROJECT_MAP.md
  MODEL_REGISTRY.yaml
  FEATURE_REGISTRY.yaml
  TASK_REGISTRY.md
  ARCHIVE_POLICY.md
  STAS9_ARCHITECTURE_PROPOSAL_RU.md

  schemas/          # будущие JSON Schema для registries/manifests
  adapters/         # будущие read-only readers STAS1..STAS8
  gates/            # будущие проверки
  run_plans/        # декларативные планы, без секретов
  runs/             # только новые STAS9 manifests/reports
  reports/          # агрегированные аудиты
```

Эти будущие подкаталоги пока не создаются: сначала нужно утвердить архитектуру и схемы.

## 4. Владение

| Данные/решение | Владелец |
|---|---|
| low candidates | STAS1 |
| causal market context | STAS2 |
| post-entry TP audit | STAS3 |
| hypotheses/teacher review | STAS4 |
| entry/phase/risk models | STAS5 |
| STAS6/STAS7 | не определено |
| move-capacity preview | STAS8 |
| выбор разрешенной версии, lineage и gates | STAS9 |

STAS9 не переписывает семантику владельца. Он только проверяет и связывает контракты.

## 5. Жизненный цикл

```text
DRAFT
-> AUDIT_READY
-> GUARD_PASS
-> REVIEW_APPROVED
-> CANDIDATE
-> ACTIVE
-> SUPERSEDED
-> FROZEN_HISTORY
```

Дополнительные блокирующие статусы:

```text
BROKEN_POINTER
MISSING_ARTIFACT
LEAKAGE_RISK
BLIND_FORWARD_QUARANTINE
OFFLINE_ONLY_NOT_LIVE_SAFE
REJECTED_BY_QUALITY_GATE
```

## 6. Первая практическая итерация

Рекомендуемый порядок после утверждения:

1. создать схемы YAML/JSON для model и feature registry;
2. реализовать read-only inventory command;
3. реализовать проверку model pointers;
4. реализовать проверку feature count/allowlist hash;
5. реализовать lineage report для текущего R4BB;
6. реализовать проверку, что R5 остается вне train;
7. только затем обсуждать единый run orchestrator.

## 7. Что не делать в первой итерации

1. Не обучать новую STAS9-модель.
2. Не исправлять автоматически старый champion pointer.
3. Не переносить STAS8 из STAS5 физически.
4. Не заполнять задним числом STAS6/STAS7 выдуманной логикой.
5. Не удалять 6 043 legacy model artifacts.
6. Не включать RiskGate или STAS8 без отдельного quality/visual approval.

## 8. Рекомендуемое архитектурное решение

Принять STAS9 как `read-only governance and reproducibility layer`.

После этого отдельными ТЗ решить:

1. нужны ли реальные STAS6 и STAS7 или нумерация остается историческим пробелом;
2. должен ли STAS8 стать самостоятельным проектом;
3. какой model pointer является проектным production candidate;
4. нужна ли очистка legacy model archive и по каким правилам восстановления.
