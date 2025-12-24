# 📊 Business Analytics - MVP KISS

> Sistema de métricas essenciais para dashboard da clínica.

## 🎯 Objetivo

Fornecer **3 métricas essenciais** para tomada de decisão:

1. **Dashboard Summary**: KPIs principais (conversão, mensagens, tempo resposta)
2. **Conversion Funnel**: Funil de 5 etapas com drop-off
3. **Bot Autonomy**: Taxa de conversas sem handoff

## 📊 Métricas Implementadas

### 1. Dashboard Summary
```
GET /api/v1/metrics/dashboard?period=30d
```

**Retorna:**
- `total_leads`: Total de leads
- `converted_leads`: Leads convertidos  
- `conversion_rate`: Taxa de conversão (%)
- `avg_response_time_seconds`: Tempo médio resposta
- `total_conversations`: Total de conversas
- `active_conversations`: Conversas ativas
- `total_messages`: Total de mensagens
- `avg_messages_per_conversation`: Média msgs/conversa

**Cache:** 5 minutos

### 2. Conversion Funnel
```
GET /api/v1/metrics/conversion-funnel?period=30d
```

**Etapas:**
1. Leads criados (NEW)
2. Engajados (respondeu 1+ msg)
3. Qualificados (maturity_score >= 60)
4. Handoff (transferido humano)
5. Convertidos (CONVERTED)

**Cada etapa retorna:**
- `count`: Quantidade
- `percentage`: % do total inicial
- `drop_off`: % abandono da etapa anterior

**Cache:** 15 minutos

### 3. Bot Autonomy
```
GET /api/v1/metrics/bot-autonomy?period=30d
```

**Retorna:**
- `total_conversations`: Total
- `bot_only`: Sem handoff
- `with_handoff`: Com handoff
- `autonomy_rate`: Taxa autonomia (%)

**Acesso:** Apenas ADMIN  
**Cache:** 15 minutos

## 🏗️ Arquitetura

```
Controller (dashboard_controller.py)
    ↓
Service (metrics_service.py) → Cache Redis
    ↓
Repository (analytics_repository.py) → PostgreSQL
```

### Camadas

**Controller:** Valida inputs, autentica, chama service  
**Service:** Cache + business logic  
**Repository:** Queries SQL otimizadas

### Cache Strategy

- **Dashboard:** TTL 5min (dados operacionais)
- **Funnel/Bot:** TTL 15min (dados analíticos)
- **Pattern:** `metrics:{nome}:{periodo}:{user}`

## 🔐 Segurança

- ✅ JWT obrigatório
- ✅ **ADMIN**: Acesso total
- ✅ **USER**: Métricas globais (sem filtro específico)

## 📈 Próximas Fases (quando necessário)

**Fase 2:** Métricas por usuário (tempo resposta individual)  
**Fase 3:** Horários de pico  
**Fase 4:** NPS/Feedback (requer nova tabela)  
**Fase 5:** Previsão de demanda (ML - quando houver dados suficientes)

## 🚀 Como Testar

```bash
# 1. Login
POST /api/v1/auth/token
{
  "username": "admin@example.com",
  "password": "senha"
}

# 2. Dashboard (últimos 30 dias)
GET /api/v1/metrics/dashboard?period=30d
Authorization: Bearer {token}

# 3. Funil
GET /api/v1/metrics/conversion-funnel?period=30d
Authorization: Bearer {token}

# 4. Bot Autonomy (admin only)
GET /api/v1/metrics/bot-autonomy?period=30d
Authorization: Bearer {token}
```

## ✅ Decisões KISS

❌ **Removido (overengineering):**
- 50+ métricas planejadas
- 9 endpoints (reduzido para 3)
- ForecastService vazio
- Métricas de ROI/receita (sem dados ainda)
- Filtering complexo por usuário
- Endpoints de cache management
- Response time por usuário

✅ **Mantido (essencial):**
- Dashboard summary
- Conversion funnel
- Bot autonomy
- Cache Redis
- Auth JWT + RBAC

---

**Versão:** 1.0 MVP  
**Data:** 18/12/2024  
**Princípio:** KISS (Keep It Simple, Stupid)
