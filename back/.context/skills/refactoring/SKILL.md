---
type: skill
name: Refactoring
description: Safe code refactoring with step-by-step approach
skillSlug: refactoring
phases: [E]
generated: 2026-02-10
status: completed
scaffoldVersion: "2.0.0"
---

# Refactoring Skill

Strategies for safe and effective code restructuring in the BotDB backend.

## Common Code Smells

- **Bloated Services**: A single service handling bot logic, scheduling, and error reporting (target for decomposition).
- **Embedded Infrastructure**: SQL queries or HTTP calls inside business logic services.
- **Generic Catch-Alls**: Large `try...except Exception` blocks that mask specific errors.
- **Inconsistent Naming**: Using `patient` in one place and `lead` in another.
- **Manual Data Mapping**: Manual conversion between DB models and API schemas (target for Pydantic/Automapper patterns).

## Refactoring Procedures

### 1. Incremental Decomposition
When breaking down a large service (like the old `bot_service` into sub-services in `src/robbot/services/`):
- Create the new sub-service.
- Move one logical block at a time.
- Update the injection in the orchestrator.
- Run tests after every step.

### 2. Repository Consolidation
Ensure all data access follows the same pattern:
- Inherit from `BaseRepository`.
- Use specific filter methods instead of exposing raw SQLAlchemy queries to the service layer.
- Ensure consistent return types (Entity vs List[Entity]).

### 3. Type Safety Hardening
- Add strict type hints to all method signatures.
- Replace generic `Dict` return types with specific Pydantic schemas.

## Safe Refactoring Checklist

- [ ] Does the existing test suite pass? (Baseline)
- [ ] Have I identified a clear pattern to move toward (e.g., Strategy pattern for polling)?
- [ ] Are the changes broken into small, atomic commits?
- [ ] Did I update the `codebase-map.json` (if structural) and `.context/docs`?
- [ ] Do all tests pass after the final change?

## Requirements after Refactoring

- **Zero Regression**: Functional tests in `tests/api/` must remain green.
- **Architectural Cleanup**: Delete the old, deprecated code/files once the transition is complete and verified.
- **Review**: Must be reviewed by the `Refactoring Specialist` agent.
