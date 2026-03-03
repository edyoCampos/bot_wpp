---
type: skill
name: Feature Breakdown
description: Break down features into implementable tasks
skillSlug: feature-breakdown
phases: [P]
generated: 2026-02-10
status: completed
scaffoldVersion: "2.0.0"
---

# Feature Breakdown Skill

How to decompose complex requirements into actionable technical tasks in BotDB.

## Decomposion Approach

Follow this layer-based breakdown for new features:

### 1. Requirements Analysis
- What is the business goal (e.g., "Allow secretaries to tag urgent patients")?
- What are the success criteria?

### 2. Domain & Persistence (The Foundation)
- Update `Lead` or `Conversation` domain entities.
- Create Alembic migration for schema changes.
- Add or update methods in corresponding repositories.

### 3. Service Layer (The Logic)
- Create or update services in `src/robbot/services/`.
- Define how the AI or background workers will interact with the new data.

### 4. API & Interface (The Entry Point)
- Define new Pydantic schemas in `src/robbot/schemas/`.
- Implement FastAPI routes and dependency injection.
- Update management endpoints for the dashboard.

### 5. Verification (The Confidence)
- Write unit tests for new service methods.
- Write API/Integration tests for end-to-end verification.

## Integration Points to Consider

- **WAHA**: Does this feature require new WhatsApp capabilities?
- **AI**: Does this require new prompts or RAG context?
- **Analytics**: Should this feature emit new metrics (e.g., "Time to urgent tag")?

## Example Breakdown: "Urgent Flagging"
1. **Infra**: Add `is_urgent` boolean to `ConversationModel`. Create migration.
2. **Persistence**: Add `mark_urgent(id)` to `ConversationRepository`.
3. **Service**: Update `InteractionService` to detect specific keywords and call `mark_urgent(id)`.
4. **API**: Add `PUT /v1/conversations/{id}/urgent` endpoint.
5. **Specs**: Update `.context/docs/glossary.md` with the new attribute definition.
