# Guia: Uso de DEV_MODE para Desenvolvimento Local

## Contexto

Implementamos o `DEV_MODE` para facilitar o desenvolvimento local sem afetar seus contatos pessoais do WhatsApp.

## O que faz

Filtra mensagens do WhatsApp por número de telefone. Quando ativado, o bot **só responde** para o número especificado em `DEV_PHONE_NUMBER`, ignorando todas as outras mensagens.

## Por que precisamos disso

Quando conectamos nossa conta pessoal do WhatsApp ao WAHA para testes, sem essa proteção o bot responderia automaticamente para TODOS os seus contatos. Isso evita spam acidental para amigos e família.

## Como configurar (.env)

```env
# Ativar modo desenvolvimento
DEV_MODE=true

# Número que vai receber respostas do bot (formato: código país + DDD + número, sem espaços)
DEV_PHONE_NUMBER=5511999999999
```

## Formato do número

- Brasil: `5511999999999` (55 = país, 11 = DDD, 999999999 = número)
- Sem espaços, sem caracteres especiais
- Apenas dígitos

## Como funciona

1. Webhook recebe mensagem do WAHA
2. Sistema extrai o número do campo `from` (ex: `5511999999999@c.us`)
3. Se `DEV_MODE=true`:
   - Número == `DEV_PHONE_NUMBER`? → Processa ✅
   - Número != `DEV_PHONE_NUMBER`? → Ignora ❌ (apenas loga)
4. Se `DEV_MODE=false`: Processa todas as mensagens (produção)

## Logs

```log
# Mensagem ignorada
[INFO] [DEV MODE] Mensagem ignorada - número não autorizado: 5511888888888 (permitido: 5511999999999)

# Mensagem aceita
[INFO] [DEV MODE] Mensagem aceita de número autorizado: 5511999999999
[SUCCESS] Mensagem enfileirada para processamento
```

## Cenários de Uso

### Desenvolvimento Local

```env
DEV_MODE=true
DEV_PHONE_NUMBER=5511999999999  # Seu número de teste
```

### Múltiplos Desenvolvedores

Cada desenvolvedor roda sua própria instância com seu número:

**Desenvolvedor A** (`.env`):
```env
DEV_MODE=true
DEV_PHONE_NUMBER=5511111111111
```

**Desenvolvedor B** (`.env`):
```env
DEV_MODE=true
DEV_PHONE_NUMBER=5511222222222
```

### Produção/Staging

```env
DEV_MODE=false
# DEV_PHONE_NUMBER não é necessário
```

## Importante

### ✅ Faça

- Sempre usar `DEV_MODE=true` quando testar localmente com sua conta pessoal
- Configurar `DEV_PHONE_NUMBER` com o número que você vai usar para enviar mensagens de teste ao bot
- Documentar seu número de teste na wiki do time
- Testar com um contato dedicado (não seu próprio número)

### ❌ Não Faça

- **Nunca** deixar `DEV_MODE=true` em produção
- Usar números de produção em ambientes de desenvolvimento
- Commitar números reais no git (usar `.env.example` apenas)
- Testar com números de clientes

## Troubleshooting

### Problema: Bot não está respondendo minhas mensagens de teste

**Verificar**:
1. `DEV_MODE=true` está configurado no `.env`
2. `DEV_PHONE_NUMBER` corresponde ao formato do seu WhatsApp
3. Containers foram reconstruídos após alterar `.env`
4. Verificar logs procurando por "Mensagem ignorada" ou "Mensagem aceita"

**Validar configuração**:
```bash
# Verificar variáveis de ambiente atuais
docker compose exec api env | grep DEV

# Saída esperada:
# DEV_MODE=true
# DEV_PHONE_NUMBER=5511999999999
```

### Problema: Bot respondendo para todos os contatos

**Solução**:
1. Configurar `DEV_MODE=true` no `.env`
2. Adicionar seu número em `DEV_PHONE_NUMBER`
3. Reconstruir: `docker compose up api worker --build -d`

### Problema: Não sei qual é o formato do meu número

**Extrair dos logs do WAHA**:
```bash
docker compose logs waha | grep "from"
```

Procurar por: `"from": "5511999999999@c.us"` → Usar `5511999999999`

## Referência de Código

**Implementação**: `back/src/robbot/adapters/controllers/webhook_controller.py`

```python
# DEV MODE: Filtrar mensagens por número de telefone
if settings.DEV_MODE and settings.DEV_PHONE_NUMBER:
    if phone != settings.DEV_PHONE_NUMBER:
        logger.info(
            "[DEV MODE] Mensagem ignorada - número não autorizado: %s",
            phone
        )
        return log  # Pula processamento
```

**Configuração**: `back/src/robbot/config/settings.py`

```python
DEV_MODE: bool = Field(default=False, description="Ativar modo desenvolvimento")
DEV_PHONE_NUMBER: str | None = Field(default=None, description="Número autorizado")
```

## Documentação Relacionada

- [Guia de Logging](logging-guidelines.md)
- [Setup WAHA](../deployment/railway.md)
- [Variáveis de Ambiente](../../.env.example)
- [Visão Geral da Arquitetura](../../ARCHITECTURE.md#security--authentication)
