FROM python:3.12-alpine
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock config.yaml README.md ./
RUN uv sync --no-install-project --no-group dev --no-group api --group syncer

COPY src/ ./src

RUN uv sync --no-group dev --no-group api --group syncer

CMD [ "uv", "run", "src/mirror/syncer/main.py" ]