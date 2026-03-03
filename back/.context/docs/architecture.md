# Architecture Notes

The BotDB system is designed as a modular service with a clear separation between infrastructure, domain logic, and API endpoints. It follows a **Clean Architecture** inspired structure, where the core logic is isolated from external dependencies like WAHA (WhatsApp API), Redis, and Postgres.

## System Architecture Overview
The system is a distributed application composed of:
- **API Server**: A FastAPI application handling REST requests and webhooks.
- **Workers**: RQ (Redis Queue) workers processing background jobs like message processing, polling, and scaling.
- **Polling Workers**: Specialized workers that poll external APIs (like WAHA) to fetch new messages and enqueue them for processing.
- **Database**: PostgreSQL for persistent storage of leads, conversations, and audit logs.
- **Cache/Queue**: Redis for job queuing, session management, and caching.
- **Vector DB**: ChromaDB for storing conversation embeddings and providing RAG (Retrieval-Augmented Generation) context to the LLM.

Requests typically enter via webhooks or are pulled by the polling worker. They are then enqueued, processed by a worker (which may interact with LLMs), and responses are sent back via the WAHA API.

## Architectural Layers
- **API/Controllers**: Entry points handled by FastAPI (`src/robbot/api/` and `src/robbot/adapters/controllers/`).
- **Services**: Core business logic and use cases (`src/robbot/services/`).
- **Persistence**: Database models and repositories (`src/robbot/infra/persistence/`).
- **Jobs**: Background task definitions (`src/robbot/infra/jobs/`).
- **Domain**: Core entities and value objects (`src/robbot/domain/`).

> See [`codebase-map.json`](./codebase-map.json) for complete symbol counts and dependency graphs.

## Detected Design Patterns
| Pattern | Confidence | Locations | Description |
|---------|------------|-----------|-------------|
| Repository | 95% | `src/robbot/infra/persistence/repositories/` | Abstracts data access logic. |
| Singleton | 90% | `LLMClient`, `ChromaClient` | Ensures one instance per process. |
| Job/Worker | 100% | `src/robbot/infra/jobs/` | Handles asynchronous processing. |
| Strategy | 85% | `PollingStrategy` | Allows different ways to poll chats (All vs Restricted). |

## Entry Points
- API Server: `src/robbot/api/main.py`
- Worker: `src/robbot/workers/rq_worker.py`
- Message Polling: `src/robbot/infra/jobs/message_polling_job.py`

## Public API
The system exposes a REST API for management and receives webhooks from WAHA. Key endpoints include:
- `/v1/auth/`: Authentication and session management.
- `/v1/conversations/`: Conversation listing and details.
- `/v1/leads/`: Lead management and status tracking.
- `/v1/waha/`: WAHA integration and messaging.

## Internal System Boundaries
- **Queue Seam**: The boundary between the API/Polling and the actual message processing logic is handled via Redis queues.
- **Database Schema**: Shared between the API and Workers, managed via Alembic.

## External Service Dependencies
- **WAHA**: WhatsApp HTTP API for messaging.
- **Groq/Gemini**: LLM providers for AI-generated responses.
- **Redis**: Queue and cache backing.
- **PostgreSQL**: Primary data store.

## Risks & Constraints
- **Race Conditions**: Parallel workers may attempt to create the same conversation for a new lead simultaneously (handled via unique constraints).
- **Rate Limits**: LLM providers (Groq/Gemini) have rate limits (e.g., 429 errors observed and handled via retries).
- **State Drift**: Database schema and Alembic migrations must be kept in sync; manual drift was recently corrected.

## Top Directories Snapshot
- `src/robbot/services/`: Core logic (approx. 50 files)
- `src/robbot/infra/persistence/`: Data layer (approx. 30 files)
- `src/robbot/api/`: Web endpoints (approx. 20 files)
- `tests/`: Extensive unit and integration test suites.

## Related Resources
- [Project Overview](./project-overview.md)
- [Data Flow](./data-flow.md)
- [Database Drift Report](./database_drift.md)
