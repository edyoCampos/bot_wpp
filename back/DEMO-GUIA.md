# 🎯 GUIA RÁPIDO - DEMONSTRAÇÃO DO BOT

## 📋 Scripts Prontos

### Windows (PowerShell):
```powershell
cd d:\_projects\clinica_go\back
.\demo-queries.ps1
```

**OU via Git Bash:**
```bash
cd /d/_projects/clinica_go/back
pwsh -File demo-queries.ps1
```

### Linux/Mac (Bash):
```bash
cd /d/_projects/clinica_go/back
chmod +x demo-queries.sh
./demo-queries.sh
```

---

## 🔥 COMANDOS INDIVIDUAIS (Copy/Paste)

### 1️⃣ Última conversa formatada
```bash
docker-compose exec -T db psql -U dba -d BotDB -c "
SELECT 
  ROW_NUMBER() OVER (ORDER BY created_at) as num,
  CASE direction 
    WHEN 'INBOUND' THEN '>> Cliente'
    WHEN 'OUTBOUND' THEN '<< Bot'
  END as origem,
  SUBSTRING(REPLACE(body, E'\n', ' '), 1, 100) || 
    CASE WHEN LENGTH(body) > 100 THEN '...' ELSE '' END as mensagem,
  TO_CHAR(created_at, 'HH24:MI:SS') as hora
FROM conversation_messages 
WHERE conversation_id = (
  SELECT id FROM conversations ORDER BY updated_at DESC LIMIT 1
)
ORDER BY created_at;"
```

### 2️⃣ Stats últimas 24h
```bash
docker-compose exec -T db psql -U dba -d BotDB -c "
SELECT 
  COUNT(*) FILTER (WHERE direction = 'INBOUND') as recebidas,
  COUNT(*) FILTER (WHERE direction = 'OUTBOUND') as enviadas,
  COUNT(DISTINCT conversation_id) as conversas_ativas
FROM conversation_messages
WHERE created_at > NOW() - INTERVAL '24 hours';"
```

### 3️⃣ Logs em tempo real
```bash
# Worker processando mensagens
docker-compose logs -f worker --tail=30

# Polling buscando mensagens no WAHA
docker-compose logs -f polling-worker --tail=20

# API recebendo requests
docker-compose logs -f api --tail=20

# Todos juntos
docker-compose logs -f worker polling-worker api --tail=10
```

### 4️⃣ Fila RQ (Redis)
```bash
# Mensagens pendentes
docker-compose exec -T redis redis-cli LLEN rq:queue:messages

# Jobs AI pendentes
docker-compose exec -T redis redis-cli LLEN rq:queue:ai

# Escalações pendentes
docker-compose exec -T redis redis-cli LLEN rq:queue:escalation
```

### 5️⃣ Leads e Score SPIN
```bash
docker-compose exec -T db psql -U dba -d BotDB -c "
SELECT 
  phone_number as telefone,
  name as nome,
  maturity_score as score,
  status,
  CASE 
    WHEN maturity_score < 30 THEN 'SITUATION'
    WHEN maturity_score < 50 THEN 'PROBLEM'
    WHEN maturity_score < 75 THEN 'IMPLICATION'
    WHEN maturity_score < 85 THEN 'NEED_PAYOFF'
    ELSE 'READY'
  END as fase_spin
FROM leads
ORDER BY created_at DESC
LIMIT 10;"
```

### 6️⃣ Mensagem específica (última resposta do bot)
```bash
docker-compose exec -T db psql -U dba -d BotDB -c "
SELECT 
  body as resposta_bot,
  TO_CHAR(created_at, 'DD/MM/YYYY HH24:MI:SS') as enviada_em
FROM conversation_messages 
WHERE direction = 'OUTBOUND'
ORDER BY created_at DESC 
LIMIT 1;"
```

---

## 🎬 ROTEIRO APRESENTAÇÃO (5 min)

### Abertura (30s)
"Vou mostrar como o bot funciona em tempo real, desde a mensagem chegando até a resposta sendo enviada."

### DEMO 1: Enviar mensagem (1 min)
1. Abrir WhatsApp
2. Enviar: "Onde fica a clínica?"
3. Mostrar logs em tempo real:
   ```bash
   docker-compose logs -f worker polling-worker --tail=50
   ```
4. Apontar no log:
   - `[POLLING] Iniciando busca` → Capturou mensagem
   - `process_message_job` → Worker processou
   - `Gemini response generated` → IA respondeu

### DEMO 2: Ver mensagens no DB (1 min)
```bash
pwsh -File demo-queries.ps1
```
Mostrar query #1 (última conversa)

### DEMO 3: Código - Fluxo (2 min)
Abrir arquivos e apontar:
1. `message_polling_job.py` linha 67 → "Aqui busco do WAHA"
2. `conversation_orchestrator.py` linha 150 → "Aqui a IA decide o que fazer"
3. `templates.py` linha 330 → "Aqui está o prompt que ensina o tom humanizado"

### DEMO 4: Estatísticas (30s)
```bash
pwsh -File demo-queries.ps1
```
Queries #2, #4, #6 (stats, leads, SPIN)

### Fechamento (30s)
"Sistema completo: WhatsApp → WAHA → Polling → RQ Queue → Worker → Gemini AI → PostgreSQL → WhatsApp"

---

## 📊 MÉTRICAS IMPORTANTES

### Performance
- ⏱️ Tempo médio de resposta: 2-5 segundos
- 📦 Mensagens processadas/dia: Ver query #2
- 🔄 Uptime workers: `docker-compose ps`

### Qualidade IA
- 🎯 Score SPIN médio: Ver query #6
- 📈 Taxa conversão (READY): Ver query #6
- 💬 Mensagens por conversa: Calcular na query #1

### Infraestrutura
- 🐳 Containers ativos: 9 (api, worker x2, polling, autoscaler, waha, db, redis, adminer)
- 💾 DB Size: `docker-compose exec -T db psql -U dba -d BotDB -c "\l+"`
- 🔴 Redis memory: `docker-compose exec -T redis redis-cli INFO memory | grep used_memory_human`

---

## 🐛 TROUBLESHOOTING DURANTE DEMO

### Bot não responde?
```bash
# 1. Verificar se polling está rodando
docker-compose ps polling-worker

# 2. Verificar logs de erro
docker-compose logs worker --tail=50 | grep ERROR

# 3. Verificar fila travada
docker-compose exec -T redis redis-cli LLEN rq:queue:messages
```

### Mensagem não aparece no DB?
```bash
# Verificar se WAHA está funcionando
curl http://localhost:3000/api/default/sessions

# Verificar logs do polling
docker-compose logs polling-worker --tail=20
```

### Query vazia?
```bash
# Ver todas conversas
docker-compose exec -T db psql -U dba -d BotDB -c "SELECT COUNT(*) FROM conversations;"

# Ver todas mensagens
docker-compose exec -T db psql -U dba -d BotDB -c "SELECT COUNT(*) FROM conversation_messages;"
```

---

## ✅ CHECKLIST PRÉ-APRESENTAÇÃO

- [ ] Containers rodando: `docker-compose ps`
- [ ] API healthy: `curl http://localhost:3333/health`
- [ ] WAHA conectado: `curl http://localhost:3000/api/default/sessions`
- [ ] Workers processando: `docker-compose logs worker --tail=5`
- [ ] DB acessível: `docker-compose exec -T db psql -U dba -d BotDB -c "SELECT 1;"`
- [ ] Scripts testados: `pwsh -File demo-queries.ps1`
- [ ] Arquivos abertos no VSCode:
  - `conversation_orchestrator.py`
  - `templates.py`
  - `message_polling_job.py`

---

Boa apresentação! 🚀
