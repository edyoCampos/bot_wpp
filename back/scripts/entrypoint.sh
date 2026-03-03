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
: "${AUTO_MIGRATE:=false}"
: "${WAIT_FOR_DB:=true}"
: "${DB_WAIT_RETRIES:=60}"
: "${DB_WAIT_SLEEP:=2}"

# Garante /app/src no PYTHONPATH (força usar caminho absoluto do container)
if [ -z "${PYTHONPATH}" ] || [ "${PYTHONPATH}" = "" ]; then
  export PYTHONPATH="/app/src"
elif ! echo "${PYTHONPATH}" | grep -q "/app/src"; then
  export PYTHONPATH="/app/src:${PYTHONPATH}"
fi

# Cria diretório ChromaDB com permissões corretas
echo "[ENTRYPOINT] Creating ChromaDB directory..."
mkdir -p /app/data/chroma
chmod -R 755 /app/data/chroma || true
echo "[ENTRYPOINT] ChromaDB directory ready"

# Se DATABASE_URL não estiver definida, tenta construir a partir das variáveis POSTGRES_*
if [ -z "${DATABASE_URL}" ]; then
  DATABASE_URL="postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
fi
export DATABASE_URL

# Timezone BRT (Brasília, UTC-3)
ts() { TZ='America/Sao_Paulo' date +"%H:%M:%S.%3N"; }
LOG_TAG="Entrypoint"
SERVICE_NAME="${SERVICE_NAME:-app}"
LOG_COLOR="${LOG_COLOR:-false}"

# ANSI cores
RESET="\033[0m"
BLUE="\033[34m"; GREEN="\033[32m"; YELLOW="\033[33m"; RED="\033[31m"; BRIGHT_RED="\033[91m"
CYAN="\033[36m"; MAGENTA="\033[35m"; WHITE="\033[37m"

service_color() {
  case "$SERVICE_NAME" in
    api) echo "$CYAN" ;;
    worker) echo "$MAGENTA" ;;
    autoscaler) echo "$YELLOW" ;;
    *) echo "$WHITE" ;;
  esac
}

level_color() {
  case "$1" in
    DEBUG) echo "$BLUE" ;;
    INFO) echo "$GREEN" ;;
    WARNING) echo "$YELLOW" ;;
    ERROR) echo "$RED" ;;
    CRITICAL) echo "$BRIGHT_RED" ;;
    *) echo "$WHITE" ;;
  esac
}

log() { # $1=LEVEL $2=message
  local level="$1"; shift
  local msg="$*"
  if [ "${LOG_COLOR,,}" = "true" ]; then
    printf "%b%s%b | [%s] %b%s%b (%s/%d): %s\n" \
      "$(service_color)" "$SERVICE_NAME" "$RESET" \
      "$(ts)" \
      "$(level_color "$level")" "$level" "$RESET" \
      "$LOG_TAG" "$$" "$msg"
  else
    echo "${SERVICE_NAME} | [$(ts)] ${level} (${LOG_TAG}/$$): ${msg}"
  fi
}
log_info() { log "INFO" "$1"; }
log_warn() { log "WARNING" "$1"; }
log_error() { log "ERROR" "$1"; }

# Exibe de forma segura (mas sem expor senha)
display_db_url() {
  local url="${DATABASE_URL}"
  # mascara senha (simples)
  echo "${url}" | sed -E 's#(://[^:]+):[^@]+@#\1:***@#'
}

log_info "Entrypoint iniciado"
log_info "DATABASE_URL=$(display_db_url)"
log_info "AUTO_MIGRATE=${AUTO_MIGRATE}"
log_info "WAIT_FOR_DB=${WAIT_FOR_DB}"
log_info "DB host=${POSTGRES_HOST} port=${POSTGRES_PORT} user=${POSTGRES_USER} db=${POSTGRES_DB}"
log_info "DB wait retries=${DB_WAIT_RETRIES} sleep=${DB_WAIT_SLEEP}s"

# Função para lidar com sinais e terminar imediatamente
_on_exit() {
  log_warn "Sinal recebido, encerrando..."
  exit 0
}
trap _on_exit INT TERM

# Função que aguarda o banco de dados ficar pronto
wait_for_db() {
  if [ "${WAIT_FOR_DB}" = "false" ]; then
    log_info "WAIT_FOR_DB=false — pulando espera pelo banco"
    return 0
  fi

  log_info "Aguardando disponibilidade do banco de dados..."

  # Se pg_isready estiver disponível (postgres client instalado), usa-o (mais simples e rápido)
  if command -v pg_isready >/dev/null 2>&1; then
    log_info "Usando pg_isready para checar o DB"
    export PGPASSWORD="${POSTGRES_PASSWORD:-}"
    local tries=0
    while [ "${tries}" -lt "${DB_WAIT_RETRIES}" ]; do
      if pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" >/dev/null 2>&1; then
        log_info "Banco de dados está disponível (pg_isready)"
        return 0
      fi
      tries=$((tries + 1))
      sleep "${DB_WAIT_SLEEP}"
    done
    log_error "Timeout aguardando pg_isready. Saindo com erro."
    return 1
  fi

  # Fallback para python + psycopg2 se pg_isready não estiver presente
  if command -v python >/dev/null 2>&1 || command -v python3 >/dev/null 2>&1; then
    log_info "pg_isready não encontrado — tentando conexão via psycopg2 (python)"
    python - <<'PY'
import os, sys, time
dsn = os.environ.get("DATABASE_URL")
if not dsn:
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
        sys.exit(0)
    except Exception as exc:
        time.sleep(sleep_seconds)
sys.exit(1)
PY
    rc=$?
    if [ "$rc" -eq 0 ]; then
      log_info "Banco de dados está disponível (psycopg2)"
    else
      log_error "Timeout aguardando conexão via psycopg2"
    fi
    return "$rc"
  fi

  log_error "Nenhuma ferramenta disponível para checar o DB (pg_isready ou python). Configure WAIT_FOR_DB=false para pular."
  return 2
}

# Executa a espera pelo banco (se configurado)
if ! wait_for_db; then
  log_error "Falha ao aguardar o banco de dados"
  exit 1
fi

# Executa migrações se necessário
if [ -f "./alembic.ini" ] && [ "${AUTO_MIGRATE,,}" = "true" ]; then
  if command -v alembic >/dev/null 2>&1; then
    log_info "AUTO_MIGRATE=true e alembic.ini encontrado — executando alembic upgrade head"
    if ! alembic upgrade head; then
      log_error "Alembic falhou"
      exit 1
    fi
  else
    log_warn "alembic não está disponível no PATH — pulando migrações"
  fi
else
  if [ -f "./alembic.ini" ]; then
    log_info "alembic.ini encontrado, mas AUTO_MIGRATE != true (${AUTO_MIGRATE}) — pulando migrações"
    
    # Apenas exibe o aviso se o serviço for a API (evita logs ruidosos em workers)
    if [ "${SERVICE_NAME}" = "api" ]; then
      echo -e "${YELLOW}"
      echo "========================================================================"
      echo "  AVISO: MIGRAÇÕES AUTOMÁTICAS DESATIVADAS (AUTO_MIGRATE=${AUTO_MIGRATE})"
      echo "  O banco de dados pode estar desatualizado em relação ao código."
      echo ""
      echo "  Para rodar as migrações manualmente, execute:"
      echo "  docker compose exec api alembic upgrade head"
      echo "========================================================================"
      echo -e "${RESET}"
    fi
  else
    log_info "Nenhum alembic.ini encontrado — pulando migrações"
  fi
fi

# Exec do comando final (CMD do Dockerfile ou command do compose)
if [ "$#" -eq 0 ]; then
  log_error "Nenhum comando fornecido para executar. Saindo."
  exit 1
fi

log_info "Iniciando aplicação"
exec "$@"