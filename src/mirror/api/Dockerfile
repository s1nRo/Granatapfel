# Builder stage
FROM ghcr.io/astral-sh/uv:python3.12-alpine AS builder

ARG PYPI_URL="https://pypi.org/simple"

ENV UV_DEFAULT_INDEX=${PYPI_URL} \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv venv \
 && uv export --frozen --no-emit-project --no-group dev --no-group syncer --group api -o /tmp/requirements.txt \
 && uv pip install --require-hashes -r /tmp/requirements.txt

COPY README.md ./
COPY src/ ./src
RUN uv pip install --no-deps .

# Runtime stage
FROM python:3.12-alpine AS runner

RUN adduser -D -u 10001 unprivileged

WORKDIR /app

COPY --from=builder --chown=unprivileged:unprivileged /app/.venv /app/.venv
COPY --from=builder --chown=unprivileged:unprivileged /app/src ./src

ENV PATH="/app/.venv/bin:$PATH"

USER unprivileged

CMD ["python", "src/mirror/api/main.py"]
