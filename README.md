# 🤖 Bot WhatsApp - Atendimento Automatizado com IA

Sistema de atendimento automatizado para clínicas usando WhatsApp, integrando IA (Gemini) para conversas inteligentes, qualificação de leads e transferência para atendimento humano.

## 📋 Stack Tecnológica

- **Backend:** FastAPI + Python 3.11+
- **Banco de Dados:** PostgreSQL 18
- **Cache/Filas:** Redis 7
- **IA/LLM:** Google Gemini (via LangChain)
- **Vector Store:** ChromaDB
- **WhatsApp API:** WAHA (WhatsApp HTTP API)
- **Gerenciador de Pacotes:** UV (não use pip!)
- **Containerização:** Docker + Docker Compose

## 🚀 Quick Start (Do Zero ao Ar)

### 1️⃣ Pré-requisitos

- **Git**
- **Docker** e **Docker Compose**
- **UV** (gerenciador Python): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Python 3.11+** (para desenvolvimento local sem Docker)

### 2️⃣ Clonar o Repositório

```bash
git clone https://github.com/edyoCampos/bot_wpp.git
cd bot_wpp
```

### 3️⃣ Configurar Variáveis de Ambiente

Copie o template e preencha os valores:

```bash
cp .env.example .env
```

**Edite `.env` e configure:**

```dotenv
# ============================================================================
# SECURITY & JWT
# ============================================================================
SECRET_KEY=<gere-com: uv run python -c "import secrets; print(secrets.token_hex(32))">

# ============================================================================
# GEMINI AI (OBRIGATÓRIO)
# ============================================================================
GOOGLE_API_KEY=<sua-chave-em: https://ai.google.dev/>

# ============================================================================
# WAHA (WhatsApp)
# ============================================================================
WAHA_API_KEY=<mude-se-necessario>
WAHA_WEBHOOK_URL=http://api:3333/api/v1/webhooks/waha
```

**Ajustes para rodar localmente (fora do Docker):**

- `DATABASE_URL=postgresql://dba:dba@localhost:15432/BotDB`
- `REDIS_URL=redis://localhost:6379/0`

### 4️⃣ Subir Todos os Serviços (Docker Compose)

```bash
cd docker
docker compose up -d --build
```

**Aguarde ~2 min** para build e inicialização. Verifique status:

```bash
docker compose ps
```

Todos os containers devem estar **healthy** ou **running**:

- `postgres_db` → porta `15432` (healthy)
- `redis_app` → porta `6379` (healthy)
- `api_app` → porta `3333` (healthy)
- `wpp_bot_waha` → porta `3000` (running)
- `adminer_ui` → porta `8080` (running)

### 5️⃣ Validar Health Check

```bash
curl http://localhost:3333/api/v1/health
```

**Resposta esperada:**

```json
{
	"status": "ok",
	"components": {
		"database": { "ok": true, "error": null },
		"redis": { "ok": true, "error": null }
	},
	"timestamp": "2025-12-09T19:24:33.471823"
}
```

### 6️⃣ Aplicar Migrations (Primeira Vez)

Dentro do container da API:

```bash
docker exec -it api_app alembic upgrade head
```

Ou localmente (com venv ativa):

```bash
uv run alembic upgrade head
```

### 7️⃣ Acessar Interfaces

| Serviço      | URL                        | Credenciais                                                        |
| ------------ | -------------------------- | ------------------------------------------------------------------ |
| **API Docs** | http://localhost:3333/docs | -                                                                  |
| **Adminer**  | http://localhost:8080      | Server: `postgres_db`<br>User: `dba`<br>Pass: `dba`<br>DB: `BotDB` |
| **WAHA**     | http://localhost:3000      | Configurar sessão                                                  |

---

## 🛠️ Desenvolvimento Local (Sem Docker)

### Instalar Dependências

```bash
# Criar/ativar ambiente virtual e instalar deps
uv sync

# Ativar venv manualmente (se necessário)
# Windows Git Bash:
source .venv/Scripts/activate
# Linux/Mac:
source .venv/bin/activate
```

### Rodar API Localmente

```bash
# Certifique-se que DB/Redis estão rodando (via docker compose ou local)
cd docker && docker compose up -d postgres_db redis_app

# Rodar API em modo dev (hot-reload)
uv run uvicorn robbot.main:app --reload --host 0.0.0.0 --port 3333
```

### Criar Nova Migration

Após alterar models em `src/robbot/infra/db/models/`:

```bash
uv run alembic revision --autogenerate -m "descrição da mudança"
uv run alembic upgrade head
```

---

## 📂 Estrutura do Projeto (Clean Architecture)

```
src/robbot/
├── adapters/
│   ├── controllers/       # Endpoints HTTP (FastAPI)
│   └── repositories/      # Acesso a dados (SQLAlchemy)
├── api/v1/
│   ├── routers/           # Roteamento de endpoints
│   └── dependencies.py    # Injeção de dependências (DB, Auth)
├── core/
│   ├── security.py        # JWT, hashing, tokens
│   └── exceptions.py      # Exceções customizadas
├── domain/
│   ├── entities/          # Entidades de domínio
│   ├── enums.py           # Enums de negócio
│   └── dtos/              # DTOs internos
├── infra/
│   ├── db/                # ORM, models, migrations
│   └── redis/             # Cliente Redis (pool)
├── schemas/               # Pydantic (request/response)
├── services/              # Lógica de negócio
├── config/
│   └── settings.py        # Configurações (Pydantic Settings)
└── main.py                # Entrypoint FastAPI
```

**Regras de Ouro:**

- ❌ **Nunca** coloque lógica de negócio em controllers
- ✅ Controllers apenas mapeiam request → service → response
- ✅ Services orquestram repositories e core
- ✅ Repositories encapsulam queries SQL

---

## 🔐 Autenticação e Permissões

- **JWT Bearer Token** em todos os endpoints (exceto `/health` e webhooks)
- **Roles:** `ADMIN` (acesso total) | `USER` (dados próprios)
- **Decorators:** `@require_auth`, `@require_role(Role.ADMIN)`

**Exemplo de uso:**

```bash
# 1. Signup
curl -X POST http://localhost:3333/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"Pass123!","role":"admin"}'

# 2. Login
curl -X POST http://localhost:3333/api/v1/auth/token \
  -d "username=admin@example.com&password=Pass123!"

# 3. Usar token
curl http://localhost:3333/api/v1/protected-endpoint \
  -H "Authorization: Bearer <access_token>"
```

---

## 📦 Gerenciamento de Dependências (UV)

**⚠️ NUNCA USE `pip install`! Use `uv` para tudo:**

```bash
# Adicionar dependência de produção
uv add nome-do-pacote

# Adicionar dependência de dev
uv add --dev pytest

# Sincronizar ambiente (após pull/checkout)
uv sync

# Atualizar todas as dependências
uv sync --upgrade
```

---

## 🧪 Testes

```bash
# Rodar todos os testes
uv run pytest

# Rodar com coverage
uv run pytest --cov=robbot --cov-report=html

# Rodar apenas unit tests
uv run pytest tests/unit/

# Rodar apenas integration tests
uv run pytest tests/integration/
```

---

## 📊 Status do Projeto

### ✅ Épico 1: Infraestrutura Base (CONCLUÍDO)

- [x] Dependências Redis, LangChain, ChromaDB, Gemini
- [x] Docker Compose (DB, Redis, WAHA, Adminer, API)
- [x] Settings para Redis/Gemini/WAHA/Chroma
- [x] Enums de domínio (ConversationStatus, LeadStatus, etc.)
- [x] Health check DB + Redis (HTTP 200/503)
- [x] Factory Redis com pool e timeouts

### 🔄 Próximos Épicos

- **Épico 2:** Integração WAHA (Client HTTP, webhooks)
- **Épico 3:** Sistema de Filas (Redis Queue, workers)
- **Épico 4:** Banco Core (Tabelas conversations, leads, sessions)
- **Épico 5:** Integração Gemini AI (LangChain, ChromaDB)
- **Épico 6:** Lógica de Negócio (Intenção, maturidade, transferência)
- **Épico 7:** Dashboard e Métricas (KPIs por role)
- **Épico 8:** Melhorias e Testes

---

## 🐛 Troubleshooting

### Porta 5432 já em uso (Windows)

Se tiver Postgres local rodando:

- Parar serviço: `net stop postgresql-x64-XX` (admin)
- Ou usar porta alternativa no docker-compose (já configurado 15432)

### Erro "GOOGLE_API_KEY is required"

Edite `.env` e adicione sua chave do Google AI Studio.

### Container `api_app` unhealthy

```bash
docker logs api_app --tail 50
```

Verifique se migrations foram aplicadas e `.env` está correto.

### Redis timeout / connection refused

Certifique-se que `REDIS_URL` aponta para `redis://localhost:6379/0` (local) ou `redis://redis:6379/0` (Docker).

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'feat: adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

**Padrão de commits:** `<tipo>: <descrição>`

- `feat`: nova funcionalidade
- `fix`: correção de bug
- `docs`: documentação
- `refactor`: refatoração sem mudança de comportamento
- `chore`: tarefas de manutenção

---

## 📄 Licença

Este projeto é privado. Entre em contato com o proprietário para uso.

---

## 📞 Contato

- **Repositório:** https://github.com/edyoCampos/bot_wpp
- **Issues:** https://github.com/edyoCampos/bot_wpp/issues

---

**⚡ Desenvolvido com FastAPI + UV + Docker + IA**
