# Granatapfel

Гранатовое дерево способно расти и плодоносить в крайне суровых, засушливых условиях, где другие растения погибают.

`Granatapfel` — небольшой Python‑проект (FastAPI + GitHub API + S3), который собирает метаданные релизов GitHub (assets) по списку репозиториев и предназначен как основа для дальнейшей синхронизации/зеркалирования в S3‑хранилище.

## Возможности (текущий статус)

- Чтение списка репозиториев из `config.yaml`.
- Запрос GitHub Releases API и сбор списка assets (имя + URL скачивания).
- Базовый клиент S3 (boto3) для работы с бакетами/объектами.
- Заготовка FastAPI приложения.

> Проект находится на ранней стадии: часть модулей — пустые заглушки.

## Требования

- Python **>= 3.11** (см. `pyproject.toml`).
- Доступ к GitHub API (желательно с токеном).
- S3‑совместимое хранилище (в документации упоминается **rustfs**).

## Установка

Проект оформлен как пакет для `uv`.

```bash
# установка uv (если ещё не установлен)
# https://docs.astral.sh/uv/

uv sync
```

Либо любым другим способом, который читает `pyproject.toml` (зависимости перечислены в нём).

## Конфигурация

### config.yaml

В корне проекта лежит `config.yaml`:

```yaml
repos:
  - slug: owner/repo
    asset_regexp: '...'
    max_rel_stored: 2
    include_prerel: true
```

Поля (по текущему состоянию кода):

- `slug` — репозиторий в формате `owner/name`.
- Остальные поля (`asset_regexp`, `max_rel_stored`, `include_prerel`) уже есть в примере, но **пока не используются** в логике синхронизации.

### Переменные окружения (.env)

Настройки читаются из `.env` (см. `src/mirror/config.py`). По умолчанию в коде есть значения-заглушки — **в проде так оставлять нельзя**.

Минимально:

```dotenv
GITHUB_TOKEN=ghp_***
S3_URL=http://127.0.0.1:9000
KEY_S3=...
TOKEN_S3=...
VERSION_S3=s3v4
```

## Использование

### Получить список assets релизов GitHub

Скрипт сейчас расположен в `src/mirror/syncer/client.py`:

```bash
python -m mirror.syncer.client
```

Он прочитает `config.yaml` и выведет словарь вида:

```text
{
  "owner/repo": [["asset_name", "download_url"], ...],
  ...
}
```

### S3 клиент

Класс `S3Repository` находится в `src/mirror/s3/client.py` и содержит методы:

- `create_bucket(bucket_name)`
- `upload_file(bucket_name, file, name_obj_s3)`
- `download_file(bucket_name, file, name_obj_s3)`
- `list_obj(bucket_name)`
- `delete_obj(bucket_name, name_obj_s3)`
- `delete_bucket(bucket_name)`

> В текущем виде клиент создаётся без явного `endpoint_url` — для S3‑совместимых решений (MinIO/rustfs и т.п.) это, вероятно, потребуется добавить.

### API (FastAPI)

Заготовка приложения лежит в `src/mirror/api/main.py`:

```bash
uvicorn mirror.api.main:app --reload
```

Пока это только пустой `FastAPI()` без роутов.

## Документация

- `docs/stack.md` — кратко перечисляет зависимости стека (S3 + GitHub API).

## Лицензия

Apache-2.0 (см. `LICENSE`).
