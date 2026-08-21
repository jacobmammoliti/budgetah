ARG UV_IMAGE
ARG PYTHON_RUN_IMAGE

# === Build Stage ==============================================================
FROM ${UV_IMAGE} AS builder

# Enable bytecode compilation and use the system Python inside the container.
ENV UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_PREFERENCE=system

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-install-project

# === Run Stage ==============================================================
FROM ${PYTHON_RUN_IMAGE} AS runner

ENV PATH="/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=builder /.venv /.venv
COPY app app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]