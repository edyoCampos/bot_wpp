# Project Overview

BotDB is an intelligent chatbot automation system specifically designed for medical clinics (**Clínica Go**). It automates patient interactions on WhatsApp using advanced AI models like **Groq (Llama 3)** and **Google Gemini**, following the **SPIN Selling methodology** to qualify leads and facilitate appointment scheduling.

## Codebase Reference
> **Detailed Analysis**: For complete symbol counts, architecture layers, and dependency graphs, see [`codebase-map.json`](./codebase-map.json).

## Quick Facts
- Root: `d:\_projects\clinica_go\\back`
- Languages: Python (Primary), SQL, Shell
- Entry: `src/robbot/api/main.py`
- Full analysis: [`codebase-map.json`](./codebase-map.json)

## Entry Points
- **API Server**: [`src/robbot/api/main.py`](src/robbot/api/main.py)
- **Background Workers**: [`src/robbot/workers/rq_worker.py`](src/robbot/workers/rq_worker.py)
- **Message Polling**: [`src/robbot/infra/jobs/message_polling_job.py`](src/robbot/infra/jobs/message_polling_job.py)

## Key Exports
Reference [`codebase-map.json`](./codebase-map.json) for the complete list of available schemas, models, and services.

## File Structure & Code Organization
- `src/robbot/api/` — FastAPI routers and application entry points.
- `src/robbot/services/` — Core business logic, lead management, and AI orchestration.
- `src/robbot/infra/` — Database models, repositories, and third-party integrations (WAHA, Redis).
- `src/robbot/domain/` — Domain entities and shared business logic.
- `tests/` — Comprehensive test suite including unit, integration, and API tests.
- `alembic/` — Database migration scripts and configuration.
- `scripts/` — Utility scripts for monitoring, secret generation, and autoscaling.

## Technology Stack Summary
BotDB runs on **Python 3.11** and leverages **FastAPI** for its web interface. It uses **PostgreSQL** for data persistence and **Redis** for job queuing (RQ). AI features are powered by **Groq** and **Google Gemini**, with **ChromaDB** serving as a vector store for RAG. Development is managed with **Docker Compose**, and code quality is enforced via **pytest**, **Ruff**, and **Alembic**.

## Getting Started Checklist
1.  **Environment Setup**: Copy `.env.example` to `.env` and configure your API keys (WAHA, GROQ, GEMINI).
2.  **Infrastructure**: Start the services using `docker-compose up -d`.
3.  **Verification**: Check API health at `http://localhost:8000/health`.
4.  **Monitoring**: Monitor logs using `docker-compose logs -f worker` and `docker-compose logs -f polling-worker`.

## Next Steps
The project is currently in active development, focusing on refining the SPIN Selling behavior and optimizing lead qualification accuracy. Stakeholders include clinic administrators and medical staff intended to be offloaded by the bot's automation.

## Cross-References
- [Architecture Notes](./architecture.md)
- [Development Workflow](./development-workflow.md)
- [Tooling Guide](./tooling.md)
- [Database Drift Report](./database_drift.md)
