FROM python:3.11-slim

LABEL maintainer="edyoCampos <you@example.com>"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
WORKDIR /app

# Instala dependências do sistema, incluindo postgresql-client (pg_isready) e curl
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       postgresql-client \
       curl \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Atualiza pip/setuptools/wheel
RUN pip install --upgrade pip setuptools wheel

# (Opcional) instala seu cliente 'uv' se existir no PyPI; se não existir, o comando falha e continua
RUN pip install --no-cache-dir uv || true

# Cria usuário não-root antecipadamente para usarmos em chown
RUN useradd --create-home --shell /bin/bash appuser

# Copia todo o projeto para a imagem
COPY . /app

# Copia scripts utilitários para /usr/local/bin, garante permissão executável e ajusta dono
COPY docker/wait-for-db.sh /usr/local/bin/wait-for-db.sh
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/wait-for-db.sh /usr/local/bin/entrypoint.sh \
    && chown -R appuser:appuser /app /usr/local/bin/wait-for-db.sh /usr/local/bin/entrypoint.sh || true

# Instala dependências do projeto via pip usando pyproject.toml
RUN pip install --no-cache-dir -e .

# Garante permissões corretas no diretório da aplicação
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Default command para desenvolvimento; em produção sobreponha o CMD
CMD ["python", "-m", "uvicorn", "robbot.main:app", "--host", "0.0.0.0", "--port", "3333", "--reload"]