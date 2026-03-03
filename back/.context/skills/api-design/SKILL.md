---
type: skill
name: Api Design
description: Design RESTful APIs following best practices
skillSlug: api-design
phases: [P, R]
generated: 2026-02-10
status: completed
scaffoldVersion: "2.0.0"
---

# API Design Skill

Standards for designing and exposing RESTful services in the BotDB backend.

## Design Patterns

- **RESTful Architecture**: Follow standard HTTP methods (`GET`, `POST`, `PUT`, `DELETE`).
- **Pydantic Validation**: All input and output must be typed and validated using Pydantic schemas.
- **Resource-Oriented**: Focus on nouns (e.g., `/conversations`, `/leads`, `/tags`).
- **Sub-resources**: Use nesting where appropriate (e.g., `/conversations/{id}/tags`).

## Naming Conventions

- **Endpoints**: Use `kebab-case` for paths (e.g., `/v1/audit-logs`).
- **Versioning**: Always prefix routes with `/v1`.
- **Query Parameters**: Use `snake_case` (e.g., `?start_date=...`).
- **Payload Keys**: Use `snake_case` (standard Python convention used by FastAPI/Pydantic).

## Standards

### Request/Response Format
- **Success**: Return JSON objects (e.g., `{"success": true, "data": ...}`).
- **Errors**: Use standard HTTP status codes (400, 401, 403, 404, 500) and return a structured JSON body:
  ```json
  {"detail": "Error message description"}
  ```

### Authentication
- Protect all sensitive endpoints with the `API-Key` header or session cookie.
- Use FastAPI dependencies (`Depends`) to enforce auth across routers.

### Versioning Policy
- Introduce breaking changes in `/v2`.
- Keep the current version stable and non-breaking for existing clinic dashboard integrations.

## Codebase Examples

- **Router Setup**: `src/robbot/api/v1/routers/` for modular endpoint definition.
- **Schema Centralization**: `src/robbot/schemas/` for unified data contracts.
- **Controller Logic**: `src/robbot/adapters/controllers/` for separating API handling from business logic.
