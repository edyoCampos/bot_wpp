# Tooling & Productivity Guide

This guide provides the necessary information about the tools and automation scripts available in the BotDB repository to maximize developer efficiency.

## Required Tooling
- **Docker & Docker Compose**: Orchestrates all services (API, Workers, Postgres, Redis, ChromaDB).
- **Postgres Client (e.g., DBeaver or Adminer)**: For inspecting the database and manual schema fixes. Adminer is often included in the compose setup with a custom dark theme (`adminer-dark.css`).
- **Redis CLI**: For inspecting the queue state and clearing processed message IDs with `FLUSHALL` or targeted `DEL`.
- **Python 3.11+**: Local runtime for running verification scripts.
- **Alembic**: For managing database migrations inside the API container.

## Recommended Automation
The repository includes several utility scripts in `scripts/`:
- **`generate_secrets.py`**: Generates secure `SECRET_KEY` and `API_KEY` values for the `.env` file.
- **`diagnose_health.py`**: Performs health checks on all service components (Database, VectorDB, Redis).
- **`monitor_workers.py`**: Provides a real-time view of queue stats and worker activity.
- **`autoscale_workers.py`**: Example script for dynamically scaling RQ workers based on queue depth.
- **`verify_polling_logic.py`**: A standalone script to verify the message filtering and polling logic without running the full stack.

## IDE / Editor Setup
- **VS Code Extensions**:
    - **Pylance**: For advanced type checking and autocompletion.
    - **Python Debugger**: For step-by-step debugging of services and tests.
    - **Docker**: For managing containers directly from the editor.
    - **Tailwind CSS IntelliSense**: If working on frontend-related files.
- **Workspace Settings**: Use the provided `ruff.toml` to ensure linting matches project standards.

## Productivity Tips
- **Fast Reprocessing**: If testing the message pipeline repeatedly, clear the Redis cache for processed messages: `docker-compose exec redis redis-cli KEYS "waha:processed:*" | xargs docker-compose exec redis redis-cli DEL`.
- **Direct SQL**: For quick fixes or diagnostics, use `docker-compose exec db psql -U <user> -d <db_name>`.
- **Worker Isolation**: Stop the general `worker` and start a specific one if you need to debug a single queue: `docker-compose run --rm worker python -m robbot.workers.rq_worker --queues messages`.

## Cross-References
- [Development Workflow](./development-workflow.md)
- [Architecture Notes](./architecture.md)
