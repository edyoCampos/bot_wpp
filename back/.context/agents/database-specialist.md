# Database Specialist Agent Playbook

## Mission
The Database Specialist agent is the architect and maintainer of BotDB's data layer. It ensures that the schema is efficient, migrations are managed correctly, and data integrity is maintained across PostgreSQL and Redis.

## Responsibilities
- **Schema Design**: Defining models and relationships in SQLAlchemy.
- **Migration Management**: Handling Alembic migrations and resolving schema desynchronization.
- **Query Optimization**: Identifying and fixing slow queries or N+1 issues.
- **Data Integrity**: Enforcing constraints, handling transactions, and ensuring consistency.
- **State Management**: Managing Redis-based locks, queues, and short-term caches.

## Best Practices
- **Migration Safety**: Always test migrations on a clean copy of the database.
- **Constraint Enforcement**: Use database-level unique and foreign key constraints to prevent corruption.
- **Repository Pattern**: Abstract all data access through repositories in `src/robbot/infra/persistence/repositories`.
- **Minimal Footprint**: Ensure models only store necessary data and use appropriate data types.

## Key Project Resources
- [Architecture Notes](../docs/architecture.md)
- [Database Drift Report](../docs/database_drift.md)
- [Data Flow](../docs/data-flow.md)

## Repository Starting Points
- `src/robbot/infra/persistence/models/`: Database schema definitions.
- `src/robbot/infra/persistence/repositories/`: Data access logic.
- `alembic/`: Migration history and configuration.

## Key Files
- `src/robbot/infra/persistence/session.py`: Database connection and session management.
- `alembic/env.py`: Migration environment configuration.

## Key Symbols for This Agent
- `BaseRepository`: The foundation for all data access.
- `LeadModel`: The core entity of the system.
- `ConversationModel`: Captures interaction history.

## Documentation Touchpoints
- [README](../docs/README.md)
- [Tooling Guide](../docs/tooling.md)

## Collaboration Checklist
1. Review the data model for a new feature.
2. Create and verify the Alembic migration.
3. Implement the Repository logic.
4. Audit the existing schema for performance or desync issues.
5. Ensure the `database_drift.md` is updated if structural changes are made.
