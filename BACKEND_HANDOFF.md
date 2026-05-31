# Backend Handoff

Этот файл нужен, чтобы другой человек быстро развернул backend у себя.

## Что передать

- Папку проекта целиком (или архив `autocheckmobile-backend`)
- `swagger-openapi.json` (если нужно отдельно для интеграции)

Не передавать:

- `.env` (локальные секреты)
- `storage/` (временные артефакты проверок)

## Быстрый запуск у получателя

1. Распаковать проект и перейти в папку:

```bash
cd autocheckmobile-backend
```

2. Подготовить переменные окружения:

```bash
cp .env.example .env
```

3. Запустить сервисы:

```bash
docker compose up -d --build
```

4. Применить миграции:

```bash
docker compose exec api alembic upgrade head
```

5. Проверить API:

```bash
curl http://localhost:8000/health
```

6. Swagger UI:

- `http://localhost:8000/api/docs`

## Если нужен Android checker image

```bash
docker compose --profile checker-images build android-checker-image
```

или

```bash
./scripts/build-checker-images.sh
```
