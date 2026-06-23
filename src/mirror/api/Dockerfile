FROM python:3.12-alpine
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY . .

CMD ["uv", "run", "src/mirror/api/main.py"]