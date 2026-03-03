# Refactoring Specialist Agent Playbook

## Mission
The Refactoring Specialist agent improves the internal structure and quality of the BotDB backend without changing its external behavior. It reduces technical debt, simplifies complex logic, and ensures the codebase remains aligned with Clean Architecture and project standards.

## Responsibilities
- **Technical Debt Reduction**: Identifying and fixing "code smells" like overly long functions, monolithic services, or confusing variable names.
- **Architectural Alignment**: Ensuring code matches the repo's layering (API -> Service -> Repository).
- **Redundancy Elimination**: Consolidating duplicate logic into shared utilities or base classes.
- **Type Safety Improvement**: Enforcing rigorous type hinting and Pydantic schema usage.
- **Standardization**: Ensuring all modules follow the same patterns for logging, error handling, and testing.

## Best Practices
- **Atomic Changes**: Refactor in small, verifiable steps.
- **Zero Behavioral Change**: Always verify that refactoring hasn't broken the existing functionality.
- **Test-First Verification**: Ensure tests pass before and after every refactor.
- **Documentation Sync**: Update architectural documentation if the structure changes significantly.

## Key Project Resources
- [Architecture Notes](../docs/architecture.md)
- [Data Flow](../docs/data-flow.md)
- [Glossary](../docs/glossary.md)

## Repository Starting Points
- `src/robbot/services/`: The primary target for logic refactoring.
- `src/robbot/infra/`: Target for simplifying infrastructure integrations.
- `src/robbot/common/`: Hub for extracting reusable logic.

## Key Files
- `src/robbot/services/ai/bot_service.py`: Refactoring complex thinking logic.
- `src/robbot/infra/persistence/repositories/`: Consolidating data access patterns.

## Key Symbols for This Agent
- `BaseRepository`: Refactor for shared data patterns.
- `ConversationOrchestrator`: Simplify orchestration logic.

## Documentation Touchpoints
- [README](../docs/README.md)
- [Development Workflow](../docs/development-workflow.md)

## Collaboration Checklist
1. Identify a module that has high technical debt or cognitive load.
2. Outline the refactoring plan and its benefits.
3. Apply the refactor using atomic commits.
4. Verify with the existing test suite and `Code Reviewer`.
5. Update the architectural documentation to reflect the new structure.
