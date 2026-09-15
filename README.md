# Granatapfel

Гранатовое дерево способно расти и плодоносить в крайне суровых, засушливых условиях, где другие растения погибают.

`Granatapfel` — сервис на Python (FastAPI + GitHub API + S3), который зеркалирует assets релизов GitHub в S3‑совместимое хранилище и отдаёт их через простой веб‑интерфейс в стиле файлового индекса.

## Как это работает

Проект состоит из трёх частей, которые поднимаются вместе через `docker-compose`:

- **syncer** — периодически (раз в сутки) читает `config.yaml`, опрашивает GitHub Releases API, фильтрует assets и заливает их в S3. Лишние старые версии удаляет, оставляя в хранилище не больше заданного количества релизов.
- **api** — FastAPI‑приложение, отдающее содержимое бакета в виде HTML‑индекса (как autoindex у nginx). Закрыто HTTP Basic‑авторизацией.
- **s3** — хранилище [rustfs](https://github.com/rustfs/rustfs) (S3‑совместимое), куда складываются файлы.

Объекты в бакете хранятся по ключу вида `owner/repo/tag/asset_name`.

## Требования

- Python **>= 3.11.9** (см. `pyproject.toml`).
- GitHub‑токен для доступа к Releases API.
- S3‑совместимое хранилище (по умолчанию — `rustfs` из `docker-compose.yaml`).
- Для локального запуска — [`uv`](https://docs.astral.sh/uv/).

## Конфигурация

### config.yaml

Список зеркалируемых репозиториев лежит в `config.yaml`:

```yaml
repos:
  - slug: 2dust/v2rayN
    asset_regexp: '^(?!.*\.dmg$)(?!.*windows-arm)(?!.*(?:loong64|riscv)).*$'
    max_rel_stored: 2
    include_prerel: true

  - slug: Flowseal/zapret-discord-youtube
    max_rel_stored: 1
    include_prerel: false
```

Поля:

- `slug` — репозиторий в формате `owner/name`.
- `asset_regexp` *(необязательно)* — регулярное выражение для фильтрации имён assets; если не задано, берутся все файлы релиза.
- `max_rel_stored` — сколько последних релизов хранить в S3 (более старые удаляются).
- `include_prerel` — учитывать ли предрелизы.

### Переменные окружения (.env)

Настройки читаются из `.env` (см. `src/mirror/config.py`). Пример — в `.env.example`:

```dotenv
GITHUB_TOKEN=example
S3_URL=http://localhost:9000
KEY_S3=rustfsadmin
TOKEN_S3=rustfsadmin
VERSION_S3=s3v4
BUCKET_NAME=pomoyka
LOG_LEVEL=INFO
RUSTFS_ACCESS_KEY=rustfsadmin
RUSTFS_SECRET_KEY=rustfsadmin
USERNAME_API=admin
PASSWORD_API=admin
```

- `GITHUB_TOKEN` — токен GitHub для Releases API.
- `S3_URL`, `KEY_S3`, `TOKEN_S3`, `VERSION_S3` — адрес и доступы к S3 (в `docker-compose` `S3_URL` переопределяется на `http://s3:9000`).
- `BUCKET_NAME` — имя бакета (создаётся автоматически при старте).
- `USERNAME_API` / `PASSWORD_API` — логин и пароль HTTP Basic для веб‑интерфейса.
- `LOG_LEVEL` — уровень логирования (`DEBUG`, `INFO`, ...).

> Значения по умолчанию в коде и примерах — для локальной отладки. В проде так оставлять нельзя.

## Запуск через Docker Compose

Самый простой способ — поднять весь стек (хранилище + api + syncer):

```bash
cp .env.example .env   # и отредактировать под себя
docker compose up -d --build
```

После старта:

- веб‑интерфейс доступен на `http://localhost:8000` (логин/пароль из `USERNAME_API`/`PASSWORD_API`);
- `syncer` сразу выполняет синхронизацию, затем повторяет её ежедневно в 12:00.

## Локальный запуск (uv)

Зависимости разнесены по группам: `api`, `syncer`, `dev`.

```bash
# установить все группы
uv sync

# либо только нужную часть
uv sync --group api
uv sync --group syncer
```

### Syncer

```bash
uv run src/mirror/syncer/main.py
```

Прочитает `config.yaml`, скачает подходящие assets релизов и зальёт их в S3, удалив устаревшие версии сверх `max_rel_stored`.

### API

```bash
uv run src/mirror/api/main.py
# или для разработки:
uvicorn mirror.api.main:app --reload
```

Доступные маршруты (все под HTTP Basic‑авторизацией):

| Маршрут | Описание |
|---|---|
| `GET /` | список зеркалируемых репозиториев |
| `GET /{owner}/{repo}` | список версий (тегов) репозитория |
| `GET /{owner}/{repo}/{version}` | список файлов конкретной версии |
| `GET /{owner}/{repo}/{version}/{key}` | скачивание файла |
| `GET /auth` | проверка учётных данных |

## S3‑клиент

Класс `S3Repository` (`src/mirror/s3/client.py`) — тонкая обёртка над `boto3` с `endpoint_url`, заданной signature‑версией и автосозданием бакета. Методы:

- `create_bucket(bucket_name)`
- `upload_file(data, bucket_name, keys)`
- `download_file(bucket_name, keys)`
- `list_obj(bucket_name)`
- `delete_obj(bucket_name, name_obj_s3)`
- `delete_bucket(bucket_name)`

## Разработка

В группе `dev` — `ruff` и `mypy` (включён `strict`):

```bash
uv run ruff check .
uv run mypy src
```

## Лицензия

Apache-2.0 (см. `LICENSE`).