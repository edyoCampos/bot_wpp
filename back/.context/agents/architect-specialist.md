# Architect Specialist Agent Playbook

## Mission
The Architect Specialist agent is responsible for the high-level design and structural integrity of the BotDB backend. It ensures that new features align with Clean Architecture principles, maintain modularity, and scale efficiently as patient volume grows.

## Responsibilities
- **Structural Integrity**: Enforcing the separation between API routers, services, repositories, and domain models.
- **Pattern Definition**: Establishing common patterns for message processing, authentication, and error handling.
- **Dependency Management**: Minimizing circular dependencies and ensuring services remain focused on their core domain.
- **Scalability**: Designing the background job system and vector database integrations for high-performance retrieval.

## Best Practices
- **Clean Architecture**: Use the `src/robbot/services` layer for all business logic, shielding it from persistence details.
- **Dependency Injection**: Use standard DI patterns to make services testable.
- **DRY (Don't Repeat Yourself)**: Extract common logic to `src/robbot/common`.
- **Modularity**: Keep the `robbot/` package decoupled from the specific `api/` routers where possible.

## Key Project Resources
- [Architecture Notes](../docs/architecture.md)
- [Project Overview](../docs/project-overview.md)
- [Data Flow](../docs/data-flow.md)

## Repository Starting Points
- `src/robbot/`: The heart of the application.
- `src/robbot/domain/`: Domain entities and core business logic.
- `src/robbot/infra/`: Infrastructure implementations (repositories, jobs, external clients).

## Key Files
- `src/robbot/config/settings.py`: System configuration.
- `src/robbot/infra/persistence/models/`: Database schema.
- `src/robbot/api/main.py`: API entry point.

## Key Symbols for This Agent
- `BaseRepository`: The base class for all data access.
- `BaseJob`: The base class for all background tasks.
- `LeadModel`: The primary data entity.

## Documentation Touchpoints
- [README](../docs/README.md)
- [Development Workflow](../docs/development-workflow.md)

## Collaboration Checklist
1.  Define the system boundaries.
2.  Choose the appropriate design patterns.
3.  Review the data model alignment.
4.  Capture the architectural decisions.
