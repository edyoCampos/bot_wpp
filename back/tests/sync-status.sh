#!/bin/bash
# Automação: Verificar Status de Sincronização de DEV_PHONE_NUMBERS
# Mostra quais números já estão sincronizados e quais ainda precisam

WORKDIR="/d/_projects/clinica_go/back"
cd "$WORKDIR"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   📱 DEV PHONE NUMBERS - STATUS DE SINCRONIZAÇÃO              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Ler lista de números de .env
DEV_PHONES=$(grep "DEV_PHONE_NUMBERS=" .env | cut -d= -f2 | tr -d ' ')

if [ -z "$DEV_PHONES" ]; then
    echo -e "${RED}✗ DEV_PHONE_NUMBERS não configurado em .env${NC}"
    exit 1
fi

# Converter para array
IFS=',' read -ra PHONES_ARRAY <<< "$DEV_PHONES"

echo -e "${BLUE}Números configurados:${NC} ${#PHONES_ARRAY[@]}"
echo ""

# Verificar cada número
TOTAL=${#PHONES_ARRAY[@]}
SYNCED=0
PENDING=0

for PHONE in "${PHONES_ARRAY[@]}"; do
    PHONE=$(echo "$PHONE" | tr -d ' ')  # Remove espaços
    
    # Procurar nos logs do worker
    RESOLVED=$(docker compose logs worker --tail=200 2>/dev/null | \
      grep "LID encontrado para número $PHONE" | tail -1)
    
    if [ -n "$RESOLVED" ]; then
        # Extrair LID dos logs
        LID=$(echo "$RESOLVED" | grep -oP '(?<=: )[^@]+@lid' | head -1)
        if [ -z "$LID" ]; then
            LID="(pendente de cache)"
        fi
        
        echo -e "${GREEN}✅ SINCRONIZADO${NC}  $PHONE → $LID"
        ((SYNCED++))
    else
        echo -e "${YELLOW}⏳ AGUARDANDO${NC}   $PHONE"
        ((PENDING++))
    fi
done

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "Sincronizados: ${GREEN}${SYNCED}/${TOTAL}${NC}  |  Pendentes: ${YELLOW}${PENDING}/${TOTAL}${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

if [ "$PENDING" -gt 0 ]; then
    echo -e "${YELLOW}📌 AÇÃO NECESSÁRIA:${NC}"
    echo ""
    echo "Para sincronizar os números pendentes:"
    echo ""
    echo "1️⃣  Abra WhatsApp (no celular/desktop conectado ao WAHA)"
    echo "2️⃣  Para cada número, inicie um novo chat:"
    echo ""
    
    for PHONE in "${PHONES_ARRAY[@]}"; do
        PHONE=$(echo "$PHONE" | tr -d ' ')
        RESOLVED=$(docker compose logs worker --tail=200 2>/dev/null | \
          grep "LID encontrado para número $PHONE" | tail -1)
        
        if [ -z "$RESOLVED" ]; then
            echo "    • Número: ${YELLOW}$PHONE${NC}"
        fi
    done
    
    echo ""
    echo "3️⃣  Envie qualquer mensagem (ex: 'test')"
    echo "4️⃣  Aguarde ~30 segundos"
    echo "5️⃣  Execute este script novamente para validar"
    echo ""
    echo "Comando para verificar novamente:"
    echo "  ${BLUE}bash sync-status.sh${NC}"
else
    echo -e "${GREEN}✅ TODOS OS NÚMEROS SINCRONIZADOS!${NC}"
    echo ""
    echo "O bot está pronto para responder:"
    echo ""
    for PHONE in "${PHONES_ARRAY[@]}"; do
        PHONE=$(echo "$PHONE" | tr -d ' ')
        echo "  • $PHONE"
    done
fi

echo ""
