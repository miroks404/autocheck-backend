# AutoCheckMobile Web Dashboard

SPA для роли **Эксперт/HR**: управление заданиями, просмотр проверок, вердикты и статистика.

## Архитектура

```
src/
  screens/          # Presentation — экраны
  components/ui/    # Переиспользуемые UI-компоненты (дизайн-система)
  state/            # State management (React Context + reducer)
  domain/           # Use cases и доменные модели
  data/api/         # API Client Layer (единственная точка HTTP)
  shared/           # Утилиты (даты, лейблы)
  core/             # Конфигурация
```

Компоненты **не обращаются к сети напрямую** — только через `domain/useCases.ts` → `data/api/autocheckApi.ts`.

## Запуск

```bash
cd frontend-dashboard
npm install
npm run dev
```

Переменные окружения (`.env`):

```
VITE_API_BASE_URL=http://localhost:8000
```

## Реализованные экраны (Модуль Б)

| Экран | Описание |
|-------|----------|
| Авторизация | JWT login/register, обработка 401/403/422/500 |
| Загрузка задания | Assignment + Git/ZIP + ФИО/email кандидата |
| Дашборд эксперта | DataTable, поиск, фильтры, чипы, сортировка |
| Карточка проверки | ScoreCard, ResultRow, AI-анализ, вердикт, хронология |
| Создание задания | Чекеры, ползунки весов (сумма 100%), черновик/публикация |
| Статистика | Метрики, график 30 дней, топ кандидатов |

## Дизайн-система

Токены в `src/index.css` (`--primary`, `--success`, …). Демо смены токена — селектор в шапке.

Компоненты: `Button`, `Input`, `Checkbox`, `StatusBadge`, `ProgressBar`, `ScoreCard`, `DataTable`, `FileUpload`, `ResultRow`, `FilterChip`.

## Адаптивность

Поддержка экранов **320–1920px**: flex/grid, `overflow-x: auto` для таблиц, breakpoints 1024/768/480px.
