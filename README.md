# 🤖 Bot WhatsApp - Atendimento Automatizado com IA

> Sistema de atendimento automatizado para clínicas usando WhatsApp, integrando Google Gemini AI para conversas inteligentes, qualificação de leads e transferência inteligente para atendimento humano.

---

## 🎯 Visão Geral

### O que o Sistema Faz

**Captação e Organização**
- Recebe mensagens de pessoas vindas de campanhas Google Ads e Instagram
- Organiza conversas em filas (Redis Queue) para processamento assíncrono
- Identifica origem da campanha automaticamente
- Armazena todo histórico de interações

**Atendimento Automatizado Inteligente**
- Responde perguntas comuns usando IA (Gemini + LangChain)
- Mantém contexto conversacional usando ChromaDB (vector database)
- Segue scripts pré-aprovados por procedimento
- Conversa natural, indistinguível de atendente humano

**Transferência Inteligente**
- Detecta intenção de agendamento automaticamente
- Transfere para secretária com todo o histórico
- Secretária continua exatamente de onde o bot parou
- Foco humano apenas no que precisa de intervenção

**Métricas e Acompanhamento**
- Dashboard em tempo real (conversas ativas, taxa de conversão)
- Tempo médio de resposta por campanha
- Funil de conversão lead → agendamento
- ROI de campanhas publicitárias

### O que o Sistema NÃO Faz

- ❌ Não substitui completamente a secretária (complementa)
- ❌ Não faz diagnósticos médicos
- ❌ Não integra com outras redes sociais (apenas WhatsApp)
- ❌ Não envia lembretes automáticos de consultas

---

## 📋 Stack Tecnológica

| Categoria | Tecnologia | Versão | Propósito |
|-----------|------------|--------|-----------|
| **Backend** | FastAPI | 0.115+ | API REST |
| **Linguagem** | Python | 3.11+ | Core |
| **Banco de Dados** | PostgreSQL | 18 | Persistência |
| **Cache/Filas** | Redis | 7 | Queue (RQ) + Cache |
| **IA/LLM** | Google Gemini | 1.5 Flash | Conversação |
| **LLM Framework** | LangChain | 1.2.0+ | Orquestração IA |
| **Vector Store** | ChromaDB | Latest | Contexto conversacional |
| **WhatsApp API** | WAHA | Latest | Integração WhatsApp |
| **Package Manager** | UV | Latest | ⚠️ **NÃO USE PIP!** |
| **Containerização** | Docker Compose | Latest | Orquestração |

---

## 🚀 Quick Start

### Pré-requisitos

- **Docker** e **Docker Compose** instalados
- **UV** (Python package manager): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Google AI Studio API Key**: https://ai.google.dev/

### 1. Clonar Repositório

```bash
git clone https://github.com/edyoCampos/bot_wpp.git
cd bot_wpp
```

### 2. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
```

**Edite `.env` e configure:**

```env
# JWT Secret (gere com: uv run python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=seu_secret_key_aqui

# Google Gemini API (OBRIGATÓRIO)
GOOGLE_API_KEY=sua_chave_google_ai_studio

# WAHA WhatsApp (ajustar se necessário)
WAHA_API_KEY=change-me
WAHA_WEBHOOK_URL=http://api:3333/api/v1/webhooks/waha
```

### 3. Subir Todos os Serviços

```bash
cd docker
docker compose up -d --build
```

**Aguarde ~2min para inicialização.** Verifique status:

```bash
docker compose ps
```

Todos devem estar **healthy** ou **running**:

| Serviço | Porta | Status Esperado |
|---------|-------|-----------------|
| postgres_db | 15432 | healthy |
| redis_app | 6379 | healthy |
| api_app | 3333 | healthy |
| worker (2x) | - | healthy |
| wpp_bot_waha | 3000 | running |
| adminer_ui | 8080 | running |

### 4. Validar Health Check

```bash
curl http://localhost:3333/api/v1/health
```

**Resposta esperada:**
```json
{
  "status": "ok",
  "components": {
    "database": {"ok": true, "error": null},
    "redis": {"ok": true, "error": null},
    "waha": {"ok": true, "error": null}
  }
}
```

### 5. Aplicar Migrations (Primeira Vez)

```bash
docker exec -it api_app alembic upgrade head
```

### 6. Acessar Interfaces

| Interface | URL | Credenciais |
|-----------|-----|-------------|
| **API Docs** | http://localhost:3333/docs | - |
| **Adminer** | http://localhost:8080 | Server: `postgres_db`<br>User/Pass: `dba`<br>DB: `BotDB` |
| **WAHA** | http://localhost:3000 | Configurar sessão WhatsApp |

---

## 🛠️ Desenvolvimento Local

### Instalar Dependências

```bash
# Sincronizar ambiente (cria venv + instala deps)
uv sync

# Ativar venv manualmente (se necessário)
source .venv/Scripts/activate  # Windows Git Bash
source .venv/bin/activate       # Linux/Mac
```

### Rodar API Localmente (Hot Reload)

```bash
# Subir apenas DB e Redis
cd docker && docker compose up -d postgres_db redis_app

# Ajustar DATABASE_URL no .env para localhost:
# DATABASE_URL=postgresql://dba:dba@localhost:15432/BotDB

# Rodar API em modo dev
uv run uvicorn robbot.main:app --reload --host 0.0.0.0 --port 3333
```

### Criar Nova Migration

Após alterar models em `src/robbot/infra/db/models/`:

```bash
uv run alembic revision --autogenerate -m "descrição da mudança"
uv run alembic upgrade head
```

### Gerenciar Dependências (UV)

⚠️ **NUNCA USE `pip install`! Sempre use `uv`:**

```bash
# Adicionar dependência de produção
uv add nome-pacote

# Adicionar dependência de dev
uv add --dev pytest

# Sincronizar após pull/checkout
uv sync

# Atualizar todas as dependências
uv sync --upgrade
```

---

## 📂 Arquitetura (Clean Architecture)

```
src/robbot/
├── adapters/
│   ├── controllers/          # Endpoints HTTP (FastAPI)
│   ├── external/             # Clients externos (WAHA, Gemini)
│   └── repositories/         # Acesso a dados (SQLAlchemy)
├── api/v1/
│   ├── routers/              # Roteamento REST
│   └── dependencies.py       # Injeção de dependências (DB, Auth)
├── core/
│   ├── security.py           # JWT, hashing, autenticação
│   ├── exceptions.py         # Exceções base
│   └── custom_exceptions.py  # Exceções tipadas (LLMError, QueueError...)
├── domain/
│   ├── entities/             # Entidades de negócio
│   ├── enums.py              # Enums (ConversationStatus, LeadStatus...)
│   └── dtos/                 # DTOs internos
├── infra/
│   ├── db/                   # ORM, models, migrations (Alembic)
│   ├── redis/                # Redis pool + Queue Manager
│   ├── jobs/                 # RQ Background Jobs
│   └── vectordb/             # ChromaDB client
├── schemas/                  # Pydantic (request/response)
├── services/                 # Lógica de negócio
├── workers/                  # RQ Workers
├── config/
│   ├── settings.py           # Configurações (Pydantic Settings)
│   └── prompts/              # Prompts do Gemini
└── main.py                   # Entrypoint FastAPI
```

### Regras de Ouro

- ✅ **Controllers** apenas mapeiam request → service → response (zero lógica de negócio)
- ✅ **Services** orquestram repositories e regras de negócio
- ✅ **Repositories** encapsulam queries SQL (zero lógica de negócio)
- ✅ **Entities** são objetos de domínio puros (zero dependências de infra)
- ❌ **NUNCA** coloque lógica de negócio em controllers
- ❌ **NUNCA** acesse DB diretamente de controllers (sempre via service)

---

## 🔐 Autenticação e Permissões

### Roles

| Role | Acesso |
|------|--------|
| **ADMIN** | Acesso total (todos os dados, todas as APIs) |
| **USER** (Secretária) | Apenas dados próprios (conversas atribuídas) |

### Autenticação JWT

Todos os endpoints REST (exceto `/health` e webhooks) exigem JWT Bearer Token.

**Exemplo de Fluxo:**

```bash
# 1. Signup (criar usuário admin)
curl -X POST http://localhost:3333/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@clinica.com",
    "password": "Pass123!",
    "role": "admin"
  }'

# 2. Login (obter token)
curl -X POST http://localhost:3333/api/v1/auth/token \
  -d "username=admin@clinica.com&password=Pass123!"

# 3. Usar token em requests
curl http://localhost:3333/api/v1/conversations \
  -H "Authorization: Bearer <access_token>"
```

### Decorators Disponíveis

```python
from robbot.api.v1.dependencies import require_auth, require_role

@router.get("/admin-only")
@require_role(Role.ADMIN)
def admin_endpoint(user: dict = Depends(require_auth)):
    ...

@router.get("/protected")
def protected_endpoint(user: dict = Depends(require_auth)):
    ...
```

---

## 🧪 Testes

```bash
# Rodar todos os testes
uv run pytest

# Com coverage
uv run pytest --cov=robbot --cov-report=html

# Apenas unit tests
uv run pytest tests/unit/

# Apenas integration tests
uv run pytest tests/integration/

# Ver coverage no navegador
open htmlcov/index.html
```

---

## 📊 Status do Projeto

### ✅ Épico 1: Infraestrutura Base (100%)

- [x] Dependências Redis, LangChain, ChromaDB, Gemini
- [x] Docker Compose completo (6 serviços)
- [x] Settings centralizadas (Pydantic)
- [x] Enums de domínio (8 tipos)
- [x] Health check (DB + Redis + WAHA)
- [x] Factory Redis com pool

### ✅ Épico 2: Integração WAHA (95%)

- [x] Client HTTP completo (WAHAClient)
- [x] Métodos: create/start/stop session, send_text/image/document
- [x] Schemas Pydantic para webhooks
- [x] Endpoint POST /webhooks/waha com persistência
- [x] Repositories (WhatsAppSession, WebhookLog)
- [x] Service layer (WAHAService)

### ✅ Épico 3: Sistema de Filas (100%)

- [x] Redis Queue Manager (3 filas: messages, ai, escalation)
- [x] Jobs: MessageProcessing, Gemini, Escalation, Reengagement
- [x] RQ Worker com exception handler customizado
- [x] 2 replicas de workers no docker-compose
- [x] Queue Service (enqueue, stats, retry, cancel)
- [x] Endpoints REST para gestão de filas
- [x] Dead Letter Queue (DLQ)

### ✅ Épico 4: Banco Core (100%)

- [x] 20 tabelas (users, conversations, messages, leads, interactions...)
- [x] 16 Alembic migrations
- [x] Repositories para todos os models
- [x] Relationships + FKs + Cascades
- [x] Índices para performance

### ✅ Épico 5: Integração Gemini AI (100%)

- [x] GeminiClient com retry logic + rate limiting
- [x] LangChainService (memória conversacional)
- [x] ChromaDB para contexto (embeddings)
- [x] ConversationOrchestrator (fluxo completo)
- [x] Prompts templates por procedimento
- [x] Detecção de intenção via LLM

### ✅ Épico 6: Lógica de Negócio (100%)

- [x] ConversationService (CRUD, transições de status)
- [x] LeadService (criação, atribuição, conversão)
- [x] Atribuição automática de leads (load balancing)
- [x] Sistema de notificações in-app
- [x] Detecção de urgência (keywords + LLM)
- [x] Maturidade de leads (scoring automático)
- [x] Transferência inteligente para secretária

### 🔄 Épico 7: Dashboard e Métricas (30%)

- [x] Endpoints REST para métricas básicas
- [x] Filtros por role (admin vê tudo, user vê próprio)
- [ ] Dashboard React (frontend)
- [ ] Gráficos de conversão
- [ ] Analytics por campanha

### 🔄 Épico 8: Melhorias e Testes (40%)

- [x] Unit tests core (security, exceptions)
- [x] Custom exceptions (8 tipos específicos)
- [x] Logging estruturado
- [ ] Integration tests completos
- [ ] CI/CD pipeline
- [ ] Monitoramento (Prometheus/Grafana)

**Status Geral:** 85% concluído | Produção-ready

---

## 🐛 Troubleshooting

### Porta 5432 já em uso (Windows)

Se tiver Postgres local rodando:

```bash
# Parar serviço Windows (admin)
net stop postgresql-x64-XX

# Ou usar porta alternativa (já configurado: 15432)
```

### Erro "GOOGLE_API_KEY is required"

Edite `.env` e adicione sua chave do Google AI Studio (https://ai.google.dev/).

### Container `api_app` unhealthy

```bash
# Verificar logs
docker logs api_app --tail 50

# Verificar se migrations foram aplicadas
docker exec -it api_app alembic current

# Reaplicar migrations se necessário
docker exec -it api_app alembic upgrade head
```

### Redis connection refused

Certifique-se que `REDIS_URL` está correto:
- Docker: `redis://redis:6379/0`
- Local: `redis://localhost:6379/0`

### Workers não processam filas

```bash
# Verificar logs dos workers
docker logs wpp_bot-worker-1
docker logs wpp_bot-worker-2

# Verificar se Redis está acessível
docker exec -it wpp_bot-worker-1 redis-cli -h redis ping
```

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit seguindo padrão: `git commit -m 'feat: adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

### Padrão de Commits

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` nova funcionalidade
- `fix:` correção de bug
- `docs:` apenas documentação
- `style:` formatação (sem mudança de lógica)
- `refactor:` refatoração (sem mudança de comportamento)
- `test:` adicionar/corrigir testes
- `chore:` tarefas de manutenção (build, deps, etc)

---

## 📞 Contato e Suporte

- **Repositório:** https://github.com/edyoCampos/bot_wpp
- **Issues:** https://github.com/edyoCampos/bot_wpp/issues
- **Wiki:** [Em construção]

---

## 📄 Licença

Este projeto é privado. Entre em contato com o proprietário para uso.

---

**⚡ Desenvolvido com FastAPI + UV + Docker + Google Gemini AI**
