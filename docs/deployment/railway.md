# 🚂 Deploy no Railway

## 📋 Pré-requisitos

- Conta no [Railway.app](https://railway.app)
- Repositório GitHub conectado
- Cartão de crédito (não será cobrado no free tier)

## 🚀 Passo a Passo

### 1. Instalar Railway CLI (opcional)

```bash
npm install -g @railway/cli
railway login
```

### 2. Deploy via Dashboard (Recomendado)

1. Acesse https://railway.app/new
2. Clique em "Deploy from GitHub repo"
3. Selecione `edyoCampos/bot_wpp`
4. Railway detecta `railway.json` automaticamente

### 3. Adicionar Banco de Dados

**PostgreSQL:**

1. No projeto Railway, clique "+ New"
2. Selecione "Database" → "PostgreSQL"
3. Railway injeta `DATABASE_URL` automaticamente

**Redis:**

1. Clique "+ New" novamente
2. Selecione "Database" → "Redis"
3. Railway injeta `REDIS_URL` automaticamente

### 4. Configurar Variáveis de Ambiente

No dashboard Railway, vá em "Variables" e adicione:

```env
SECRET_KEY=<clique em "Generate" no Railway>
ALGORITHM=HS256
PYTHONPATH=/app/src
AUTO_MIGRATE=true
WAHA_API_KEY=<sua chave>
GEMINI_API_KEY=<sua chave>
```

### 5. Deploy do WAHA (Serviço Separado)

1. Clique "+ New" → "Empty Service"
2. Configure:
   - Nome: `bot-wpp-waha`
   - Source: Docker Image
   - Image: `devlikeapro/waha:latest`
3. Adicione variáveis:
   ```env
   WAHA_API_KEY=<mesma do passo 4>
   WAHA_DASHBOARD_USERNAME=admin
   WAHA_DASHBOARD_PASSWORD=<senha forte>
   ```
4. Anote a URL: `https://bot-wpp-waha-production.up.railway.app`
5. Volte no serviço principal e atualize:
   ```env
   WAHA_BASE_URL=<URL do WAHA anotada>
   ```

### 6. Verificar Deploy

Aguarde ~5 minutos e acesse:

```bash
# Health check
curl https://seu-app.railway.app/api/v1/health

# Docs
open https://seu-app.railway.app/docs
```

## 🔍 Monitoramento

- **Logs:** Dashboard Railway → aba "Logs"
- **Métricas:** Dashboard → aba "Metrics"
- **Restart:** Dashboard → "⋯" → "Restart"

## 💰 Custos

**Free Tier:**

- $5 de crédito/mês
- ~500h de uptime
- Suficiente para TCC/MVP

**Uso Estimado:**

- API: ~$2/mês
- PostgreSQL: ~$1/mês
- Redis: ~$0.50/mês
- WAHA: ~$1.50/mês
- **Total: ~$5/mês (dentro do free tier!)**

## 🐛 Troubleshooting

### Build falha

```bash
# Verificar localmente
docker build -t test .
docker run -p 8000:8000 test
```

### Health check falha

- Verificar se `/api/v1/health` existe
- Verificar logs: `railway logs`
- Aumentar `healthcheckTimeout` em `railway.json`

### Banco não conecta

- Verificar se `DATABASE_URL` está injetada
- Testar conexão: `railway run python -c "import psycopg2; print('OK')"`

## 📝 CI/CD (Opcional)

Railway faz deploy automático a cada push em `main`.

Para desabilitar:

1. Settings → "Deploy Triggers"
2. Desmarque "Auto Deploy"

---

## 📧 Suporte

- [Railway Docs](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [GitHub Issues](https://github.com/edyoCampos/bot_wpp/issues)
