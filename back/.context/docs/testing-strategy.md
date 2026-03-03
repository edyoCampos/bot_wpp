# Testing Strategy

BotDB uses a multi-layered testing approach to ensure reliability of patient interactions and system stability. Quality is maintained through automated unit tests, integration tests for service collaboration, and API-level tests for end-to-end verification.

## Test Types
- **Unit Tests**: Powered by `pytest`. Focus on individual services and domain logic in `tests/unit/`. Files follow the pattern `test_*.py`.
- **Integration Tests**: Verify the interaction between services (e.g., `ConversationOrchestrator` with `LLMClient` and `Database`). Located in `tests/integration/`.
- **API Tests**: Validate endpoint behavior and end-to-end flows in `tests/api/`. These often require a running environment or heavy mocking of external APIs like WAHA.

## Running Tests
Run tests inside the `api` container for consistency:
- **All Tests**: `docker-compose exec api pytest`
- **Specific Module**: `docker-compose exec api pytest tests/unit/services/test_message_filter_service.py`
- **With Coverage**: `docker-compose exec api pytest --cov=src`
- **Stop on Failure**: `docker-compose exec api pytest -x`

## Quality Gates
- **Functional Verification**: All tests must pass before deployment.
- **Linting**: No Ruff violations allowed.
- **Dependency Check**: No circular dependencies allowed (enforced via project structure).

## Troubleshooting
- **Database Cleanliness**: Use the `db_session` fixture to ensure tests run in transactions that are rolled back.
- **Mocking WAHA**: Use `unittest.mock` or `pytest-mock` to avoid making real HTTP calls to WhatsApp during unit tests.
- **Rate Limits**: Be aware that integration tests hitting real LLM APIs (Groq/Gemini) may fail due to rate limits if run too frequently.

## Cross-References
- [Development Workflow](./development-workflow.md)
- [Architecture Notes](./architecture.md)
