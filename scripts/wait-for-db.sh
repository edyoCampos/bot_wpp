#!/usr/bin/env sh
set -e

HOST=${1:-db}
PORT=${2:-5432}
USER=${3:-postgres}
DB=${4:-postgres}

echo "Aguardando banco em ${HOST}:${PORT} (usuário ${USER}, db ${DB})..."
# Loop até pg_isready responder OK
until pg_isready -h "$HOST" -p "$PORT" -U "$USER" -d "$DB" >/dev/null 2>&1; do
  printf "."
  sleep 1
done

echo "\nBanco de dados pronto."
exec /bin/sh -c "exit 0"