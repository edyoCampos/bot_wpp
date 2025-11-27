#!/usr/bin/env bash
#
# Entry point refatorado
# - Espera pelo banco (usa pg_isready se disponível, senão tenta com psycopg2)
# - Executa alembic upgrade head se AUTO_MIGRATE=true (case-insensitive)
# - Respeita WAIT_FOR_DB=false para pular a espera
# - Forward de sinais durante a execução (termina imediatamente)
set -euo pipefail

# Defaults e tempo de espera configuráveis
: "${DATABASE_URL:=}"
: "${POSTGRES_HOST:=db}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_USER:=${POSTGRES_USER:-postgres}}"
: "${POSTGRES_DB:=${POSTGRES_DB:-postgres}}"
: "${POSTGRES_PASSWORD:=${POSTGRES_PASSWORD:-}}"
: "${AUTO_MIGRATE:=true}"
: "${WAIT_FOR_DB:=true}"
: "${DB_WAIT_RETRIES:=60}"
: "${DB_WAIT_SLEEP:=2}"

# Garante src/ no PYTHONPATH em execução local ou dev container
if [ -d "./src" ]; then
  export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}$(pwd)/src"
fi

# Se DATABASE_URL não estiver definida, tenta construir a partir das variáveis POSTGRES_*
if [ -z "${DATABASE_URL}" ]; then
  DATABASE_URL="postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
fi
export DATABASE_URL

# Exibe de forma segura (mas sem expor senha)
display_db_url() {
  local url="${DATABASE_URL}"
  # mascara senha (simples)
  echo "${url}" | sed -E 's#(://[^:]+):[^@]+@#\1:***@#'
}

echo "Entrypoint iniciado"
echo "DATABASE_URL=$(display_db_url)"
echo "AUTO_MIGRATE=${AUTO_MIGRATE}"
echo "WAIT_FOR_DB=${WAIT_FOR_DB}"
echo "DB host=${POSTGRES_HOST} port=${POSTGRES_PORT} user=${POSTGRES_USER} db=${POSTGRES_DB}"
echo "DB wait retries=${DB_WAIT_RETRIES} sleep=${DB_WAIT_SLEEP}s"

# Função para lidar com sinais e terminar imediatamente
_on_exit() {
  echo "Entrypoint recebendo sinal, encerrando..."
  exit 0
}
trap _on_exit INT TERM

# Função que aguarda o banco de dados ficar pronto
wait_for_db() {
  if [ "${WAIT_FOR_DB}" = "false" ]; then
    echo "WAIT_FOR_DB=false — pulando espera pelo banco"
    return 0
  fi

  echo "Aguardando disponibilidade do banco de dados..."

  # Se pg_isready estiver disponível (postgres client instalado), usa-o (mais simples e rápido)
  if command -v pg_isready >/dev/null 2>&1; then
    echo "Usando pg_isready para checar o DB"
    export PGPASSWORD="${POSTGRES_PASSWORD:-}"
    local tries=0
    while [ "${tries}" -lt "${DB_WAIT_RETRIES}" ]; do
      if pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" >/dev/null 2>&1; then
        echo "Banco de dados está disponível (pg_isready)"
        return 0
      fi
      tries=$((tries + 1))
      printf '.'
      sleep "${DB_WAIT_SLEEP}"
    done
    echo
    echo "Timeout aguardando pg_isready. Saindo com erro." >&2
    return 1
  fi

  # Fallback para python + psycopg2 se pg_isready não estiver presente
  if command -v python >/dev/null 2>&1 || command -v python3 >/dev/null 2>&1; then
    echo "pg_isready não encontrado — tentando conexão via psycopg2 (python)"
    python - <<'PY'
import os, sys, time
dsn = os.environ.get("DATABASE_URL")
if not dsn:
    print("DATABASE_URL não definido", file=sys.stderr)
    sys.exit(2)
# psycopg2 prefere esquema postgresql://
dsn_conn = dsn.replace("postgresql+psycopg2://", "postgresql://")
max_tries = int(os.environ.get("DB_WAIT_RETRIES", "60"))
sleep_seconds = int(os.environ.get("DB_WAIT_SLEEP", "2"))
for attempt in range(max_tries):
    try:
        import psycopg2
        conn = psycopg2.connect(dsn_conn, connect_timeout=3)
        conn.close()
        print("Database is available (psycopg2)")
        sys.exit(0)
    except Exception as exc:
        print(f"Waiting for database... ({attempt+1}/{max_tries}) - {exc}", file=sys.stderr)
        time.sleep(sleep_seconds)
print("Timed out waiting for database", file=sys.stderr)
sys.exit(1)
PY
    return $?
  fi

  echo "Nenhuma ferramenta disponível para checar o DB (pg_isready ou python). Configure WAIT_FOR_DB=false se deseja pular." >&2
  return 2
}

# Executa a espera pelo banco (se configurado)
if ! wait_for_db; then
  echo "Falha ao aguardar o banco de dados" >&2
  exit 1
fi

# Executa migrações se necessário
if [ -f "./alembic.ini" ] && [ "${AUTO_MIGRATE,,}" = "true" ]; then
  if command -v alembic >/dev/null 2>&1; then
    echo "AUTO_MIGRATE=true e alembic.ini encontrado — executando alembic upgrade head"
    if ! alembic upgrade head; then
      echo "Alembic falhou" >&2
      exit 1
    fi
  else
    echo "alembic não está disponível no PATH — pulando migrações" >&2
  fi
else
  if [ -f "./alembic.ini" ]; then
    echo "alembic.ini encontrado, mas AUTO_MIGRATE != true (${AUTO_MIGRATE}) — pulando migrações"
  else
    echo "Nenhum alembic.ini encontrado — pulando migrações"
  fi
fi

# Exec do comando final (CMD do Dockerfile ou command do compose)
if [ "$#" -eq 0 ]; then
  echo "Nenhum comando fornecido para executar. Saindo." >&2
  exit 1
fi

echo "Iniciando aplicação: $*"
exec "$@"