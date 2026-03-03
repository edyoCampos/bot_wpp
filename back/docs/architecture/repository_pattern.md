---
title: "Repository Pattern Implementation"
version: 1.0
date_created: 2026-01-13
last_updated: 2026-01-13
---
# Architecture Note: Repository Pattern Implementation

## 1. Summary
This document clarifies the current implementation of the Repository Pattern in the backend. The investigation was initiated because the `infra/repositories` directory, which was expected to contain the repository implementations according to `ARCHITECTURE.md`, was found to be empty.

The investigation confirms that the project **does** use the Repository Pattern, but the implementations are located in `src/robbot/adapters/repositories/`, not `src/robbot/infra/repositories/`.

## 2. Key Findings

### 2.1. Location of Repositories
All repository classes are located in the following directory:
`d:\_projects\clinica_go\back\src\robbot\adapters\repositories\`

This contradicts the `ARCHITECTURE.md` document, which implies they would be under the `infra` layer. This seems to be a deviation from the original plan, where `adapters` are meant for external interfaces and `infra` for core infrastructure like database access.

### 2.2. Generic `BaseRepository`
A generic `BaseRepository` is implemented in `d:\_projects\clinica_go\back\src\robbot\adapters\repositories\base_repository.py`.

This base class provides standard, reusable CRUD (Create, Read, Update, Delete) methods:
- `get_by_id(entity_id)`
- `get_all(skip, limit)`
- `create(obj)`
- `update(obj)`
- `delete(obj)`
- `count()`

### 2.3. Concrete Implementations
Specific repositories (e.g., `UserRepository`, `ConversationRepository`, `LeadRepository`) inherit from this `BaseRepository`. They are instantiated with a specific SQLAlchemy model class and a database session.

This allows concrete repositories to use the generic CRUD methods while also providing their own specific query methods. For example, `UserRepository` might have a `find_by_email(email)` method.

## 3. Architectural Impact
The current implementation is functional and follows a recognized pattern. However, the location of the repositories in the `adapters` directory is confusing.

- **Adapters Layer:** Typically, this layer contains code that adapts our application to external agents, such as UI, web APIs, or test scripts.
- **Infrastructure Layer:** This layer is usually where the implementation details of external concerns like databases, message queues, or file systems reside. A repository, being a data access mechanism, fits more naturally here.

## 4. Recommendation
1.  **Update `ARCHITECTURE.md`**: The `ARCHITECTURE.md` document should be updated to reflect the actual location of the repositories in `src/robbot/adapters/repositories/`.
2.  **Consider Refactoring (Future):** For better alignment with Clean Architecture principles, the team should consider moving the entire `repositories` directory from `adapters` to `infra`. This would be a low-priority refactoring, as the current structure is functional, but it would improve the conceptual integrity of the architecture.
3.  **Create `repository_pattern.md`**: A new documentation file, `repository_pattern.md`, should be created in `back/docs/architecture/` to serve as the canonical source of truth for this pattern, detailing the role of `BaseRepository` and the location of concrete implementations.
