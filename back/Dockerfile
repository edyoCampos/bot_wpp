# syntax=docker/dockerfile:1.4
# ============================================================================
# DOCKERFILE OTIMIZADO - Build Time: 25min → 8-10min
# Otimizações:
# - BuildKit cache mounts
# - Torch CPU-only (858MB → 200MB)
# - Dependências separadas por peso
# - Parallel stage building
# ============================================================================

# ============================================================================
# STAGE 1: Dependências Leves (cache otimizado)
# ============================================================================
FROM python:3.11-slim AS dependencies-light

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Instala dependências do sistema (camada cacheada)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    curl \
    ca-certificates \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Atualiza pip e instala uv para builds mais rápidos
RUN --mount=type=cache,id=pip-cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel uv

# CRITICO: Copia APENAS arquivos de dependencias primeiro (cache layer)
COPY pyproject.toml ./

# Instala deps do pyproject.toml (exceto ML: torch, transformers, faster-whisper)
# IMPORTANTE: openpyxl e reportlab são necessários para export_service.py
RUN --mount=type=cache,id=uv-cache,target=/root/.cache/uv \
    --mount=type=cache,id=pip-cache,target=/root/.cache/pip \
    uv pip install --system \
    alembic bcrypt chromadb email-validator fastapi google-genai google-api-core httpx \
    langchain langchain-google-genai langchain-groq passlib pillow psycopg2-binary pydantic \
    pydantic-settings pyjwt python-dotenv python-multipart redis redis-om \
    requests rq sqlalchemy tiktoken uvicorn pyotp qrcode sentry-sdk schedule \
    gunicorn watchfiles hiredis python-jose cryptography openai pyyaml

# Instala dependências de exportação separadamente (podem ter deps adicionais)
RUN --mount=type=cache,id=uv-cache,target=/root/.cache/uv \
    --mount=type=cache,id=pip-cache,target=/root/.cache/pip \
    uv pip install --system openpyxl reportlab

# ============================================================================
# STAGE 2: ML Dependencies (separado para paralelização)
# ============================================================================
FROM python:3.11-slim AS dependencies-ml

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instala apenas build essentials
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,id=pip-cache,target=/root/.cache/pip \
    pip install --upgrade pip uv

# Instala PyTorch CPU-only (MUITO menor: 858MB → ~200MB)
RUN --mount=type=cache,id=uv-cache,target=/root/.cache/uv \
    --mount=type=cache,id=pip-cache,target=/root/.cache/pip \
    uv pip install --system \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Instala transformers e faster-whisper
RUN --mount=type=cache,id=uv-cache,target=/root/.cache/uv \
    --mount=type=cache,id=pip-cache,target=/root/.cache/pip \
    uv pip install --system transformers>=4.57.3 faster-whisper>=1.0.0

# ============================================================================
# STAGE 3: Runtime - API (imagem final para servidor HTTP)
# ============================================================================
FROM python:3.11-slim AS runtime-api

LABEL maintainer="edyoCampos <camposevero@gmail.com>"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

# Instala apenas runtime libraries (sem build-essential)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libpq5 \
    postgresql-client \
    curl \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário não-root
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copia dependências leves
COPY --from=dependencies-light /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies-light /usr/local/bin /usr/local/bin

# Copia dependências ML (stage separado)
COPY --from=dependencies-ml /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copia scripts utilitários
COPY scripts/wait-for-db.sh /usr/local/bin/wait-for-db.sh
COPY scripts/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN dos2unix /usr/local/bin/wait-for-db.sh /usr/local/bin/entrypoint.sh \
    && chmod +x /usr/local/bin/wait-for-db.sh /usr/local/bin/entrypoint.sh

# Copia código fonte (última camada para melhor cache)
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY scripts/ ./scripts/
COPY alembic.ini pyproject.toml ./

# Cria diretório ChromaDB com permissões corretas
RUN mkdir -p /app/data/chroma && chmod -R 777 /app/data/chroma

# Ajusta permissões
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Default command com suporte a porta dinâmica (Railway/Render usa $PORT, local usa 3333)
CMD ["/bin/sh", "-c", "python -m uvicorn robbot.main:app --host 0.0.0.0 --port ${PORT:-3333} --workers ${WORKERS:-1}"]

# ============================================================================
# STAGE 4: Runtime - Worker (processamento assíncrono RQ)
# ============================================================================
FROM runtime-api AS runtime-worker

LABEL description="RQ Worker for bot_wpp - Background job processing"

# CRITICO: Define PYTHONPATH com caminho absoluto ANTES de qualquer comando
# Isso garante que o módulo 'robbot' seja encontrado independente do diretório de trabalho
ENV PYTHONPATH="/app/src"

# Healthcheck específico para worker
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "from robbot.infra.redis.client import get_redis_client; get_redis_client().ping()" || exit 1

# Sobrescreve o comando para executar worker
CMD ["python", "-m", "robbot.workers.rq_worker"]

# ============================================================================
# STAGE 5: Runtime - Autoscaler (docker-compose tooling baked in)
# ============================================================================
FROM runtime-api AS runtime-autoscaler

# Autoscaler needs docker CLI and compose binary to talk to host docker via mounted socket
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends docker-cli ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*
RUN curl -L https://github.com/docker/compose/releases/download/v2.32.4/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

# Run as appuser by default; docker-compose will be invoked as root via compose override
USER appuser
