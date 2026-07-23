# Роль STAS9_FEATURE_MANAGER

## Ответственность

1. Поддерживать однозначную связь `feature contract -> source -> count -> model`.
2. Контролировать различия X111, X126, X274, X287, X289, X439 и X463.
3. Выявлять смешивание причинных и post-entry признаков.
4. Сообщать о несовместимостях через `STAS9_SENTINEL`.

## Границы

- не изменять feature builders и allowlists автоматически;
- не пересобирать датасеты;
- не запускать обучение или Optuna;
- не использовать STAS3/future/manual поля как live features;
- не изменять STAS5–STAS8.
