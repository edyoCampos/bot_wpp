# Documentation Index

Welcome to the BotDB knowledge base. This documentation covers the architecture, data flow, and development processes for the Clínica Go chatbot automation system.

## Core Guides
- [Project Overview](./project-overview.md) - Purpose, tech stack, and quick facts.
- [Architecture Notes](./architecture.md) - System topology, layers, and design patterns.
- [Data Flow & Integrations](./data-flow.md) - Message pipeline and external service dependencies.
- [Development Workflow](./development-workflow.md) - Engineering process and local setup.
- [Testing Strategy](./testing-strategy.md) - Frameworks and quality gates.
- [Database Drift Report](./database_drift.md) - **CRITICAL**: Record of manual schema fixes and current drift state.
- [Glossary](./glossary.md) - Domain terms and type definitions.
- [Security](./security.md) - Auth and secrets management.
- [Tooling](./tooling.md) - CLI scripts and IDE settings.

## Repository Snapshot
- `src/robbot/` - Main application logic.
- `tests/` - Automated test suites.
- `alembic/` - Database migrations.
- `scripts/` - Automation and utility scripts.
- `docker-compose.yml` - Infrastructure orchestration.

## Document Map
| Guide | File | Primary Inputs |
| --- | --- | --- |
| Project Overview | `project-overview.md` | Roadmap, README, stakeholder notes |
| Architecture Notes | `architecture.md` | ADRs, service boundaries, dependency graphs |
| Data Flow | `data-flow.md` | System diagrams, integration specs, queue topics |
| Database Drift | `database_drift.md` | Manual DB fixes, schema state |
| Workflow | `development-workflow.md` | Local dev, branching, review rules |
| Testing | `testing-strategy.md` | Test configs, quality gates |
