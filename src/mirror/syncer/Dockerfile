FROM python:3.12-alpine
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY . .

RUN uv sync

CMD [ "uv", "run", "src/mirror/syncer/main.py" ]