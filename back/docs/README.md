w# 📚 Technical Documentation - Clinica Go Backend

**Project:** AI-powered automated customer service system for a medical clinic  
**Stack:** FastAPI + PostgreSQL + Redis + Gemini AI + WAHA + LangChain + ChromaDB  
**Last Updated:** 2026-01-13

---

## 🎯 Overview

This project implements a WhatsApp bot with artificial intelligence for automated medical clinic service, including:
- Automatic responses with Gemini AI
- Lead and conversion system
- Handoff to human agents
- Comprehensive analytics and metrics
- Robust authentication with MFA

---

## 📖 Documentation Index

### 🏗️ Core Concepts and Services

| Document | Description |
|-----------|-----------|
| [Core Concepts](core/README.md) | Core concepts and cross-cutting concerns. |
| [Services](services/README.md) | Business logic and orchestration services. |

### 🏛️ Architecture and Design

| Document | Description | Status |
|-----------|-----------|--------|
| [Technical Architecture](tic/arquitetura-tecnica.md) | Complete view of the architecture, layers, flows, and integrations | ✅ Complete |
| [ADRs - Architecture Decision Records](architecture/decisions/) | Important architectural decisions documented | ✅ 6 ADRs |
| [Development Roadmap](tic/roadmap-desenvolvimento.md) | Planning, current status, and next steps | ✅ Updated |
| [Logging Guidelines](development/logging-guidelines.md) | Standards and best practices for structured logging | ✅ Complete |

### 🔧 APIs and Integrations

| Document | Description | Status |
|-----------|-----------|--------|
| [Postman Collection](api/postman/WPP_Bot_API.postman_collection.json) | Complete collection of endpoints for testing | ✅ Complete |
| [Postman Environment](api/postman/WPP_Bot_API.postman_environment.json) | Environment variables for dev/prod | ✅ Complete |
| [API README](api/postman/README.md) | API usage instructions | ✅ Complete |

### 🚀 Deployment and Infrastructure

| Document | Description | Status |
|-----------|-----------|--------|
| [Railway Deployment](deployment/railway.md) | Production deployment guide on Railway | ✅ Complete |
| [Docker Compose](../docker-compose.yml) | Local container configuration | ✅ Complete |
| [Dockerfile](../Dockerfile) | Unified Docker image (API + Worker targets) | ✅ Consolidated |

### 📝 Academic Documentation (TCC)

| Document | Description | Status |
|-----------|-----------|--------|
| [Test Cases and Validation](tic/casos-teste-validacao.md) | Test and functional validation scenarios | ✅ Complete |
| [Presentation Slides](tic/slides.md) | Slides for the TCC presentation | ✅ Complete |

### 🎓 Architecture Decision Records (ADRs)

| ADR | Title | Date | Status |
|-----|--------|------|--------|
| [ADR-001](architecture/decisions/ADR-001-credential-separated-from-user.md) | Credential Separated from User | 2026-01-03 | ✅ Implemented |
| [ADR-002](architecture/decisions/ADR-002-analytics-repository-consolidated.md) | Consolidated Analytics Repository | 2026-01-03 | ✅ Implemented |
| [ADR-003](architecture/decisions/ADR-003-custom-exceptions-hierarchy.md) | Custom Exceptions with Hierarchy | 2025-12-30 | ✅ Implemented |
| [ADR-004](architecture/decisions/ADR-004-clean-architecture-adapted.md) | Adapted Clean Architecture | 2026-01-03 | ✅ Implemented |
| [ADR-005](architecture/decisions/ADR-005-quebra-analytics-repository.md) | Analytics Repository Breakdown (God Class) | 2026-01-03 | ✅ Implemented |
| [ADR-006](architecture/decisions/ADR-006-major-technical-refactoring-2026-01.md) | Docker Optimization and Technical Refactoring | 2026-01-05 | ✅ Implemented |

---

## 🗂️ Project Structure

```
back/
├── alembic/                    # Database migrations
│   └── versions/               # 22 migrations (19 original + 3 new)
├── docs/                       # Complete documentation
│   ├── core/                   # Core concepts and cross-cutting concerns
│   ├── services/               # Business logic and orchestration services
│   ├── architecture/           # ADRs and architectural decisions
│   ├── api/postman/            # Postman collections
│   ├── deployment/             # Deployment guides
│   └── tic/                    # Academic documentation
├── scripts/                    # Utility scripts
│   ├── entrypoint.sh           # Container entrypoint
│   └── wait-for-db.sh          # Waits for the DB to be ready
├── src/robbot/                 # Main source code
│   ├── adapters/               # Controllers, Repositories, External APIs
│   ├── api/                    # FastAPI Routers
│   ├── common/                 # Shared utilities
│   ├── config/                 # Configurations and prompts
│   ├── core/                   # Exceptions, security, logging
│   ├── domain/                 # Domain Entities and Enums
│   ├── infra/                  # DB Models, Jobs, Redis, VectorDB
│   ├── schemas/                # Pydantic DTOs
│   ├── services/               # Business logic
│   └── workers/                # RQ Workers
└── tests/                      # Automated tests
    ├── integration/            # Integration tests
    └── unit/                   # Unit tests
```

---

## 🚀 Quick Start


### 1. Setup Inicial

```bash
# Clonar repositório
cd back/

# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar Ambiente

```bash
# Copiar .env de exemplo
cp .env.example .env

# Editar variáveis necessárias:
# - DATABASE_URL
# - REDIS_URL
# - GEMINI_API_KEY
# - WAHA_API_URL
```

### 3. Executar Migrations

```bash
# Aplicar migrations
alembic upgrade head
```

### 4. Rodar Aplicação

```bash
# Desenvolvimento
uvicorn robbot.main:app --reload --port 8000

# Produção
uvicorn robbot.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Rodar Workers

```bash
# Em terminal separado
python -m robbot.workers.worker
```

---

## ⚙️ Autoscaling de Workers (RQ)

Parâmetros configuráveis (via `.env` ou `docker-compose.yml`):

- `AUTOSCALER_MIN_WORKERS`: mínimo de workers ativos. Default: `2`.
- `AUTOSCALER_MAX_WORKERS`: máximo de workers. Default: `5`.
- `AUTOSCALER_SCALE_UP_THRESHOLD`: jobs por worker para escalar para cima. Default: `5`.
- `AUTOSCALER_SCALE_DOWN_THRESHOLD`: condição de jobs para reduzir. Default: `0`.
- `AUTOSCALER_IDLE_TIME_THRESHOLD`: tempo ocioso (segundos) para considerar redução. Default: `300`.

Comportamento:

- Mantém sempre `workers >= AUTOSCALER_MIN_WORKERS`.
- Escala para cima quando `jobs/worker > AUTOSCALER_SCALE_UP_THRESHOLD` até `AUTOSCALER_MAX_WORKERS`.
- Reduz apenas se todas as filas sem pendências e todos os workers ociosos, nunca abaixo do mínimo.

Validação rápida:

```bash
# Rebuild (o autoscaler roda na imagem da API)
docker compose build --no-cache api

# Reiniciar autoscaler
docker compose up -d autoscaler

# Checar recomendação/ação
docker compose exec autoscaler python scripts/autoscale_workers.py
docker compose logs --no-log-prefix autoscaler
docker compose ps
```

Arquivos relacionados:

- Compose: `back/docker-compose.yml` (serviço `autoscaler` com variáveis expostas)
- Serviço: `back/src/robbot/services/worker_analytics_service.py` (leitura das variáveis e regras)

---

## 🧪 Testes

### Rodar Todos os Testes

```bash
pytest tests/ -v
```

### Testes por Categoria

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Testes de autenticação
pytest tests/unit/services/test_auth_service.py -v
pytest tests/integration/test_mfa_login_flow.py -v
```

### Coverage

```bash
pytest tests/ --cov=src/robbot --cov-report=html
```

---

## 📊 Status Atual do Projeto

**Nota Geral:** 9.0/10 🎯 **EXCELENTE**

### Funcionalidades Implementadas

- ✅ Autenticação completa (JWT + MFA + Sessions)
- ✅ Integração WhatsApp (WAHA)
- ✅ IA Conversacional (Gemini AI + RAG)
- ✅ Sistema de filas (Redis Queue)
- ✅ Dashboard e métricas
- ✅ Handoff para humanos
- ✅ Audit logs completo

### Correções Recentes (03/01/2026)

- ✅ Credential separado de User (violação arquitetural corrigida)
- ✅ Repositórios consolidados em `adapters/`
- ✅ Código ML não usado removido (-200 linhas)
- ✅ `lead_status` normalizado
- ✅ God Class eliminado (528→122 linhas)
- ✅ 5 ADRs documentados
- ✅ Documentação unificada criada

### Pendências

- ⏸️ 36 testes falhando (planejado Sprint 4)
- ⏸️ Migrar MetricsService para repos especializados (Sprint 4)
- ⏸️ Coverage 60% → meta 80%

---

## 🔗 Links Importantes

### Ambientes

- **Dev Local:** http://localhost:8000
- **API Docs (Swagger):** http://localhost:8000/docs
- **Redoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/api/v1/health

### Ferramentas

- **MailDev (Email):** http://localhost:1080
- **Redis Commander:** http://localhost:8081 (se configurado)

### Repositórios

- **GitHub:** (adicionar URL quando disponível)
- **Railway:** (adicionar URL de produção)

---

## 👥 Time e Contribuição

**Projeto Acadêmico:** Análise e Desenvolvimento de Sistemas  
**Ano:** 2025-2026

### Como Contribuir

1. Ler [ADRs](architecture/decisions/) para entender decisões
2. Seguir estrutura de Clean Architecture
3. Escrever testes para novas features
4. Documentar decisões importantes em novos ADRs

---

## 📞 Suporte

Para dúvidas ou problemas:

1. Consultar [Arquitetura Técnica](tcc/arquitetura-tecnica.md)
2. Revisar [ADRs](architecture/decisions/)
3. Verificar [Issues no GitHub]() (quando disponível)
4. Consultar documentação no código (docstrings)

---

**Última Atualização:** 03/01/2026  
**Versão:** 1.0.0  
**Status:** 🟢 Produção (com melhorias contínuas)
