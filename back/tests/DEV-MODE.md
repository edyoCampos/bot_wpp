# DEV_MODE - Referência Rápida

## O que é
Restringe bot para números de teste em `DEV_PHONE_NUMBERS`. Quando desativado (`DEV_MODE=false`), funciona normalmente para qualquer número.

## Problema: Bot não responde
Contato não foi sincronizado no WAHA. Solução: enviar uma mensagem do número.

## Scripts
```bash
bash sync-status.sh                 # Ver quais números estão prontos
bash test-dev-mode.sh [número]      # Testar um número específico
```

## Sincronizar um número (30 segundos)
1. Abra WhatsApp no celular/desktop conectado ao WAHA
2. Envie mensagem para o número de teste
3. Aguarde 30 segundos
4. Execute `bash sync-status.sh` para confirmar

## Desativar DEV_MODE
```bash
# Edite .env
DEV_MODE=false

# Reinicie
docker compose up -d --build api worker polling-worker
```

## Como funciona internamente
- **Polling**: Resolve LID (ID do contato) e cacheia em Redis (24h)
- **Webhook**: Valida via lookup direto + Redis cache
- **Resultado**: Bot responde apenas para números em DEV_PHONE_NUMBERS
