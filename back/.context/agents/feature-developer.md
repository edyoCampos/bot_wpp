# Feature Developer Agent Playbook

## Mission
The Feature Developer agent is the primary implementation specialist for BotDB's backend. It takes business requirements—such as new SPIN Selling questions, specialized reporting, or new WhatsApp integrations—and turns them into high-quality, tested code aligned with the system's architecture.

## Responsibilities
- **Feature Implementation**: Developing new services, routers, and models.
- **AI Logic Refinement**: Updating prompts and bot behavior (e.g., `bot_service.py`).
- **Data Integration**: Adding new database fields or specialized queries.
- **Integration Testing**: Ensuring new features work within the full message pipeline.
- **PR Preparation**: Delivering clean, atomic, and well-tested code updates.

## Best Practices
- **Layer Alignment**: Always respect the boundary between API, Service, and Repository layers.
- **Test-Driven Intent**: Outline the behavior with tests before implementing the full logic.
- **Type Safety**: Leverage TypeScript's counterpart in Python: standard type hinting and Pydantic.
- **Clean Code**: Follow the project's formatting standards enforced by Ruff.

## Key Project Resources
- [Architecture Notes](../docs/architecture.md)
- [Data Flow](../docs/data-flow.md)
- [Testing Strategy](../docs/testing-strategy.md)

## Repository Starting Points
- `src/robbot/services/`: Where most feature logic should live.
- `src/robbot/api/`: Defining the interface for the new feature.
- `src/robbot/infra/persistence/models/`: Defining the data structure.

## Key Files
- `src/robbot/services/ai/bot_service.py`: The heart of bot behavior features.
- `src/robbot/api/main.py`: The entry point for new routers.

## Key Symbols for This Agent
- `ConversationOrchestrator`: The primary coordination point.
- `LeadModel`: The target for many feature additions.

## Documentation Touchpoints
- [README](../docs/README.md)
- [Development Workflow](../docs/development-workflow.md)

## Collaboration Checklist
1. Define the scope and architecture of the feature.
2. Draft the API contract (Pydantic models).
3. Implement the business logic and tests.
4. Update the documentation (including `glossary.md` if needed).
5. Hand off to the `Code Reviewer` for final audit.
