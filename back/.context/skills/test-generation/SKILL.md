---
type: skill
name: Test Generation
description: Generate comprehensive test cases for code
skillSlug: test-generation
phases: [E, V]
generated: 2026-02-10
status: completed
scaffoldVersion: "2.0.0"
---

# Test Generation Skill

Guidelines for generating high-quality tests in the BotDB project.

## Framework & Conventions

- **Framework**: `pytest`
- **Location**: `tests/` directory, mirroring the `src/` structure.
- **Naming**: Files prefixed with `test_`, functions prefixed with `test_`.
- **Isolation**: Use `docker-compose exec api pytest` to run tests in the development environment.

## Test Organization Patterns

### 1. Unit Tests (`tests/unit/`)
Focus on single functions or classes. Mock all external dependencies.
- **Goal**: Verify business logic branching (e.g., `MessageFilterService`).
- **Dependencies**: Use `unittest.mock` to replace database, AI, or WAHA calls.

### 2. Integration Tests (`tests/integration/`)
Verify how components work together. Uses a real test database (with transaction rollback).
- **Goal**: Verify state changes across multiple services (e.g., creating a Lead and starting a Conversation).
- **Dependencies**: Real PostgreSQL (via `db_session` fixture), mocked LLM/WAHA APIs.

### 3. API Tests (`tests/api/`)
End-to-end verification of HTTP endpoints.
- **Goal**: Verify auth, routing, and serialized output.
- **Dependencies**: `test_app` fixture providing a `TestClient`.

## Mocking Strategies

- **WAHA API**: Mock `WAHACoreService` to avoid real WhatsApp interaction.
- **LLM APIs**: Mock `LLMClient` to avoid costs and rate limits. Verify that the correct prompts and context are sent.
- **Redis**: Use a separate Redis DB or mock the `QueueService` for unit tests.

## Coverage Requirements

- **Services**: 90%+ coverage.
- **Logic Branching**: All `if/else` and error handlers MUST be covered.
- **API Endpoints**: Every endpoint must have at least one test covering the "Happy Path" and one covering "Unauthorized" access.

## Example Generator Request
"Generate a unit test for `src/robbot/services/bot_service.py` that mocks the `LLMClient` and verifies the bot responds correctly when a lead asks about opening hours."
