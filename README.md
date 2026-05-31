# AutoCheckMobile Backend

Backend-модуль конкурсного задания: REST API, очередь асинхронных проверок, оркестратор чекеров, SSE-статусы и AI-review с graceful degradation.

## Технологии

- FastAPI (`/api/v1`, Swagger: `/api/docs`)
- PostgreSQL + SQLAlchemy + Alembic
- Redis + Celery worker
- Docker Compose (api, worker, database, redis)

## Архитектура

- `app/api`: HTTP-контроллеры (Auth, Assignments, Submissions, Candidates, Reports)
- `app/application/use_cases`: бизнес-сценарии (Use Cases)
- `app/domain`: интерфейсы портов и доменные сущности
- `app/infrastructure`: реализации репозиториев (SQLAlchemy adapters)
- `app/checking`: контракты `IChecker`, реальные чекеры, `CheckOrchestrator`, `ResultCalculator`
- `app/worker`: асинхронная обработка проверок в фоне
- `app/services/ai_reviewer.py`: интеграция с LLM API (`/v1/chat/completions`) + fallback и структурированный ответ
- `app/core`: конфиг, безопасность JWT, база данных, единый формат ответов

Принципы:

- **SOLID**: оркестратор зависит от интерфейса чекера, новый чекер добавляется без изменения `CheckOrchestrator`
- **DRY**: общий `ConfigService` через `Settings`, единая JSON-обертка ответа `{data, error, meta}`
- **Error handling**: централизованные обработчики `401/403/422/500` в `app/main.py`
- **Layered Architecture**: API -> Application (Use Cases) -> Domain Ports -> Infrastructure Adapters

## Эндпоинты (Модуль B)

Аутентификация:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/profile`

Задания:

- `GET /api/v1/assignments`
- `POST /api/v1/assignments`
- `GET /api/v1/assignments/{id}`
- `PUT /api/v1/assignments/{id}`
- `DELETE /api/v1/assignments/{id}`

Проверки:

- `POST /api/v1/submissions` (multipart/form-data: `assignment_id` + `git_url` или `zip_file`)
- `GET /api/v1/submissions`
- `GET /api/v1/submissions/{id}`
- `GET /api/v1/submissions/{id}/status`
- `GET /api/v1/submissions/{id}/results`
- `GET /api/v1/submissions/{id}/timeline`
- `POST /api/v1/submissions/{id}/rerun`
- `PUT /api/v1/submissions/{id}/verdict`
- `GET /api/v1/submissions/{id}/report?format=html` (или JSON по умолчанию)
- `GET /api/v1/submissions/{id}/events` (SSE)
- `GET /api/v1/submissions/{id}/ai-review`

Кандидаты и отчеты:

- `GET /api/v1/candidates`
- `GET /api/v1/candidates/{id}`
- `GET /api/v1/reports/stats`

## Быстрый запуск (Docker)

1. Скопировать окружение:

```bash
cp .env.example .env
```

2. Запустить сервисы:

```bash
docker compose up --build
```

3. Выполнить миграции (в отдельном терминале):

```bash
docker compose exec api alembic upgrade head
```

Документация API: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

## Проверяющий движок (Модуль Г)

- После создания submission задача уходит в Celery-очередь (Redis).
- Воркер подготавливает workspace решения:
  - `git clone` для `git_url`
  - распаковка ZIP для `zip_file`
- Каждый чекер запускается отдельно с таймаутом 3 минуты (изолированный Docker контейнер при доступном Docker socket).
- Worker монтирует `/var/run/docker.sock` и использует named volume `autocheck_submission_storage` для workspace кандидата.
- В Docker-образе установлен `docker-cli` (клиент), без него чекеры вернут `docker isolation is required but unavailable`.
- Ошибка одного чекера не останавливает остальные.
- Результаты каждого чекера сохраняются сразу, итоговый балл считается по весам `ResultCalculator`.

Чекеры:

- `StaticAnalysisChecker`
- `ArchitectureChecker`
- `BuildChecker`
- `TestChecker`
- `DocumentationChecker`
- `GitPracticesChecker`

## Что такое checker image

`checker image` — это отдельный Docker-образ с нужным SDK/инструментами для проверки решений.

Зачем:

- изоляция проверки от основного API-контейнера;
- воспроизводимая среда (одинаковая у всех кандидатов);
- можно ставить Android SDK/Gradle один раз в образ.

В проект добавлен готовый Android checker image:

- `docker/checkers/android/Dockerfile`
- тег образа: `autocheck-android-checker:latest`

Для Android-проектов (`gradlew`/`build.gradle`) чекеры `static_analysis`, `build`, `tests`, `git_practices`
запускаются в этом образе автоматически.

### Сборка checker image

Вариант 1 (скрипт):

```bash
./scripts/build-checker-images.sh
```

Вариант 2 (через compose профиль):

```bash
docker compose --profile checker-images build android-checker-image
```

## Ollama (бесплатный AI локально)

Можно запустить AI-анализ полностью локально без внешних платных API.

1. Поднять Ollama контейнер:

```bash
docker compose --profile ai-local up -d ollama
```

2. Загрузить модель (пример):

```bash
docker exec -it autocheck-ollama ollama pull qwen2.5-coder:7b
```

3. В `.env` выставить:

```env
AI_API_KEY=ollama
AI_BASE_URL=http://ollama:11434/v1
AI_MODEL=qwen2.5-coder:7b
```

4. Пересоздать `api` и `worker`, чтобы применить env:

```bash
docker compose up -d --force-recreate api worker
```

После этого endpoint `GET /api/v1/submissions/{id}/ai-review` будет использовать локальный Ollama.

## Production / HTTPS

Для прод-развёртывания добавлен `docker-compose.prod.yml` (Traefik + Let's Encrypt TLS).

1. В `.env` укажи:
   - `APP_DOMAIN`
   - `LETSENCRYPT_EMAIL`
2. Запусти:

```bash
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec api alembic upgrade head
```

После этого API доступен по `https://<APP_DOMAIN>/api/docs`.

## CI/CD

Добавлен GitHub Actions workflow: `.github/workflows/ci.yml`

- срабатывает на любой push/PR
- проверяет компиляцию Python-кода
- собирает Docker image из `Dockerfile`

## Локальный запуск без Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Worker:

```bash
celery -A app.worker.celery_app.celery_app worker --loglevel=info
```
