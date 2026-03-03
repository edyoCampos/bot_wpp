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

# API Design (Consumption) Skill (Frontend)

Guidelines for interacting with the BotDB backend and external services.

## Consumption Standards

- **Centralization**: All API interaction logic must live in `src/services/`.
- **Client**: Use the standard wrapper `fetchApi` (from `src/lib/api.ts`).
- **Typing**: Use TypeScript `interface` or `type` to strictly define every request payload and response body.

## Interaction Patterns

### 1. Data Normalization
- The frontend should map backend response payloads (snake_case) to frontend conventions (camelCase) if necessary, using a mapper utility.
- Use `normalizeApiError` to map varied backend error responses into a unified error object for the UI.

### 2. Form Logic
- Map Zod validation errors to backend field error messages.

### 3. State Management
- Prefer server actions or lightweight context/hooks for API-driven state.
- Avoid redundant local state for values that are managed by the backend.

## Conventions

- **Paths**: Keep service paths consistent with backend router paths (e.g., `services/authService.ts` calls `/v1/auth/...`).
- **Methods**: Correctly use `GET` for fetching and `POST/PUT/DELETE` for actions.
- **Headers**: Ensure `Content-Type: application/json` and `Authorization` tokens are handled by the `fetchApi` wrapper.

## Code Examples
- See `src/services/authService.ts` for standard implementation.
- See `src/lib/api.ts` for error normalization logic.
