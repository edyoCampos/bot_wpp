---
type: skill
name: Code Review
description: Review code quality, patterns, and best practices
skillSlug: code-review
phases: [R, V]
generated: 2026-02-10
status: completed
scaffoldVersion: "2.0.0"
---

# Code Review Skill

Detailed guidelines for code quality and pattern enforcement in BotDB.

## Common Patterns to Enforce

### 1. Unified Dependency Injection
All controllers and services should use FastAPI's `Depends()` or a consistent DI container pattern.
- **Check**: Avoid global instances of database sessions or clients.
- **Pattern**: `def __init__(self, session: Session = Depends(get_db)):`

### 2. Repository Pattern
Data access logic MUST be encapsulated in repositories in `src/robbot/infra/persistence/repositories/`.
- **Check**: Controllers should NOT call SQLAlchemy `session.query()` directly.
- **Check**: services should NOT contain raw SQL or complex SQLAlchemy filter logic.

### 3. Error Handling
Use the custom exception hierarchy in `src/robbot/core/custom_exceptions.py`.
- **Pattern**: Raise domain-specific exceptions (e.g., `LeadNotFoundError`) and handle them in global FastAPI exception handlers.
- **Check**: Avoid generic `try...except Exception: pass`.

### 4. Logging
Use the centralized logging configuration.
- **Pattern**: `logger.info("[POLLING] Msg processada: %s", msg_id)`
- **Check**: Use consistent prefixes (e.g., `[POLLING]`, `[AI]`, `[API]`) to facilitate log filtering.

### 5. Pydantic Schemas
Use Pydantic for all Request/Response validation.
- **Check**: API endpoints should return `SchemaOut` models, not ORM models directly.

## Security & Performance Checks

- **N+1 Queries**: Ensure that relationships are loaded correctly (e.g., `joinedload`) in repositories when fetching multiple entities.
- **Race Conditions**: Verify that logic creating unique entities (like Leads) handles concurrent requests gracefully (unique constraints + try/except).
- **Async vs Sync**: Ensure that I/O bound operations (API calls to WAHA/LLM) are either properly awaited in async contexts or handled in background jobs (RQ).

## Style & Conventions

- **Ruff Cleanup**: Run ruff before every review to ensure zero linting errors.
- **Docstrings**: Public methods in services should have concise docstrings explaining their purpose and business logic impacts.
- **Variable Names**: Prefer descriptive names (e.g., `authorized_senders`) over generic ones (`allowed`).
