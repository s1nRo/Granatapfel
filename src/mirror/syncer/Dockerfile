# Builder stage
FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder

ARG PYPI_URL="https://pypi.org/simple"

ENV UV_INDEX_URL=${PYPI_URL} \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-group dev --no-group api --group syncer

COPY src/ ./src
RUN uv sync --frozen --no-group dev --no-group api --group syncer

# Runtime stage
FROM python:3.12-alpine AS runner

RUN adduser -D -u 10001 unprivileged

WORKDIR /app

COPY --from=builder --chown=unprivileged:unprivileged /app/.venv /app/.venv
COPY --from=builder --chown=unprivileged:unprivileged /app/src ./src

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "src/mirror/syncer/main.py"]
