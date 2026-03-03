#!/bin/bash
# Teste de Validação: DEV MODE Phone Numbers
# Uso: ./test-dev-mode.sh [número_telefone]
# Exemplo: ./test-dev-mode.sh 555191628223

set -e

PHONE="${1:-555191628223}"
WORKDIR="/d/_projects/clinica_go/back"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  TESTE DE VALIDAÇÃO: DEV MODE - $PHONE${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

cd "$WORKDIR"

# Teste 1: Verificar configuração
echo -e "\n${BLUE}[1/5]${NC} Verificando configuração em .env..."
if grep -q "DEV_PHONE_NUMBERS.*$PHONE" .env 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Número encontrado em DEV_PHONE_NUMBERS"
else
    echo -e "${RED}✗${NC} Número $PHONE NÃO encontrado em DEV_PHONE_NUMBERS"
    grep "DEV_PHONE_NUMBERS" .env
    exit 1
fi

# Teste 2: Verificar containers
echo -e "\n${BLUE}[2/5]${NC} Verificando status dos containers..."
RUNNING=$(docker compose ps --services --filter "status=running" | wc -l)
EXPECTED=8  # Aproximado
if [ "$RUNNING" -ge 6 ]; then
    echo -e "${GREEN}✓${NC} Containers em execução ($RUNNING)"
else
    echo -e "${RED}✗${NC} Esperados ~8 containers, encontrados $RUNNING"
    docker compose ps
fi

# Teste 3: Verificar logs do worker
echo -e "\n${BLUE}[3/5]${NC} Verificando logs do worker para resolução de LID..."
LOGS=$(docker compose logs worker --tail=100 2>/dev/null | grep -i "$PHONE" | head -3)
if [ -n "$LOGS" ]; then
    echo -e "${GREEN}✓${NC} Encontrado no worker:"
    echo "$LOGS" | sed 's/^/  /'
else
    echo -e "${YELLOW}⚠${NC} Nenhuma menção do número nos últimos logs"
    echo "  Verifique se o contato está sincronizado no WhatsApp"
fi

# Teste 4: Verificar cache Redis
echo -e "\n${BLUE}[4/5]${NC} Verificando cache Redis para LID..."
# Primeiro, precisamos achar qual é o LID deste número
CACHE_KEYS=$(docker compose exec -T redis redis-cli KEYS "waha:dev_phone:*" 2>/dev/null | head -10)
if [ -n "$CACHE_KEYS" ]; then
    echo -e "${GREEN}✓${NC} Cache Redis tem chaves:"
    for KEY in $CACHE_KEYS; do
        VALUE=$(docker compose exec -T redis redis-cli GET "$KEY" 2>/dev/null)
        if [ "$VALUE" = "$PHONE" ]; then
            echo -e "  ${GREEN}$KEY${NC} → ${GREEN}$VALUE${NC} ✓"
        else
            echo "  $KEY → $VALUE"
        fi
    done
else
    echo -e "${YELLOW}⚠${NC} Cache Redis vazio - LID ainda não foi resolvido"
fi

# Teste 5: Verificar API logs
echo -e "\n${BLUE}[5/5]${NC} Verificando logs da API para validação de webhook..."
API_LOGS=$(docker compose logs api --tail=100 2>/dev/null | grep -i "dev mode\|$PHONE" | tail -5)
if [ -n "$API_LOGS" ]; then
    echo -e "${GREEN}✓${NC} Encontrado na API:"
    echo "$API_LOGS" | sed 's/^/  /'
else
    echo -e "${YELLOW}⚠${NC} Nenhuma atividade na API para este número"
fi

# Resumo
echo -e "\n${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  RESUMO DO DIAGNÓSTICO${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

echo -e "\n${YELLOW}Próximos passos:${NC}"
echo "1. Se o LID não foi resolvido:"
echo "   - Sincronize o contato: envie uma mensagem no WhatsApp"
echo "   - Aguarde 30 segundos"
echo "   - Execute este script novamente"
echo ""
echo "2. Se quer limpar cache e refazer:"
echo "   docker compose exec redis redis-cli DEL 'waha:dev_phone:*'"
echo "   docker compose restart worker polling-worker"
echo ""
echo "3. Para logs em tempo real:"
echo "   docker compose logs -f worker | grep '$PHONE'"
echo "   docker compose logs -f api | grep 'DEV MODE'"
