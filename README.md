# 🤖 Bot WhatsApp - Sistema de Atendimento Automatizado

> Bot inteligente de WhatsApp com IA para atendimento, qualificação de leads e agendamentos

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

- 🤖 **Atendimento Automatizado** com LangChain + Gemini
- 💬 **Integração WhatsApp** via WAHA
- 📊 **Dashboard Analytics** em tempo real
- 🔄 **Sistema de Filas** com Redis + RQ
- 👥 **Handoff Humano** quando necessário
- 📅 **Agendamento Inteligente**
- 🔐 **Autenticação JWT** e controle de acesso

## 🚀 Quick Start

### Pré-requisitos

- Docker & Docker Compose
- Python 3.11+
- Conta Gemini API

### Instalação Local

```bash
# 1. Clone o repositório
git clone https://github.com/edyoCampos/bot_wpp.git
cd bot_wpp

# 2. Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais

# 3. Suba o ambiente
docker compose up -d

# 4. Acesse a aplicação
# API: http://localhost:3333
# Docs: http://localhost:3333/docs
# WAHA: http://localhost:3000
# Adminer (DB): http://localhost:8080
```

### Verificar Status

```bash
# Health check
curl http://localhost:3333/api/v1/health

# Logs
docker compose logs -f api
```

## 📚 Documentação

- 📖 [Documentação Completa](./docs/)
- [🚂 Deploy Railway](./docs/deployment/railway.md)
- [📮 Postman Collection](./docs/api/postman/)

## 🏗️ Arquitetura

### Stack Tecnológico

| Camada | Tecnologia |
|--------|-----------|
| API | FastAPI 0.121+ |
| Database | PostgreSQL 18 |
| Cache/Queue | Redis 7 |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| AI/LLM | LangChain + Google Gemini |
| WhatsApp | WAHA (devlikeapro) |
| Workers | RQ (Redis Queue) |

### Estrutura do Projeto

```
bot_wpp/
├── src/robbot/              # Código-fonte principal
│   ├── api/                 # Controllers & Routes
│   ├── adapters/            # Repositories & External APIs
│   ├── core/                # Config, Security, Logging
│   ├── domain/              # Entities & Business Rules
│   ├── infra/               # Database & Redis
│   ├── schemas/             # Pydantic Models
│   ├── services/            # Business Logic
│   └── main.py              # FastAPI App
├── alembic/                 # Database Migrations
├── tests/                   # Unit & Integration Tests
├── scripts/                 # Utility Scripts
├── docs/                    # Documentation
├── Dockerfile               # Container Image
├── docker-compose.yml       # Local Development
└── railway.json             # Railway Config
```

## 🛠️ Desenvolvimento

### Rodar Testes

```bash
# Todos os testes
pytest

# Com coverage
pytest --cov=src/robbot --cov-report=html

# Apenas unit tests
pytest tests/unit/
```

### Migrations

```bash
# Aplicar migrations
docker compose exec api alembic upgrade head

# Criar nova migration
docker compose exec api alembic revision --autogenerate -m "descrição"
```

### Linting & Formatting

```bash
# Black (formatter)
black src/

# Flake8 (linter)
flake8 src/

# iSort (import organizer)
isort src/
```

### Gerar Estrutura do Projeto

```bash
python scripts/generate-structure.py > PROJECT_STRUCTURE.txt
```

## 🚢 Deploy

### Railway (Recomendado para MVP)

```bash
# Via CLI
npm install -g @railway/cli
railway login
railway up

# Ou via Dashboard
# https://railway.app/new → Deploy from GitHub
```

📖 [Guia completo de deploy Railway](./docs/deployment/railway.md)

### Docker Hub

```bash
# Build
docker build -t seu-usuario/bot-wpp:latest .

# Push
docker push seu-usuario/bot-wpp:latest
```

## 🔐 Segurança

- ✅ Senhas hasheadas com bcrypt
- ✅ JWT tokens com expiração
- ✅ Validação de entrada com Pydantic
- ✅ SQL Injection protection (SQLAlchemy ORM)
- ✅ Rate limiting (Redis)
- ✅ CORS configurável
- ✅ Secrets via variáveis de ambiente

## 📊 Monitoramento

### Health Checks

```bash
# Básico
curl http://localhost:3333/api/v1/health

# Detalhado (DB + Redis)
curl http://localhost:3333/api/v1/health/deep
```

### Logs

```bash
# API
docker compose logs -f api

# Workers
docker compose logs -f worker

# Todos os serviços
docker compose logs -f
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE) para detalhes.

## 🎓 Projeto Acadêmico

Este projeto é parte de um Trabalho de Conclusão de Curso (TCC) em Sistemas de Informação.

- **Autor:** Edyo Campos
- **Ano:** 2025

## 📞 Contato

- GitHub: [@edyoCampos](https://github.com/edyoCampos)
- Email: you@example.com

---

⭐ Se este projeto te ajudou, considere dar uma estrela!
