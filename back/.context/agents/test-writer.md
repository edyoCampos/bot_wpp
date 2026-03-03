# Test Writer Agent Playbook

## Mission
The Test Writer agent is the guardian of stability in the BotDB backend. It ensures that every service, job, and API endpoint is covered by automated tests, preventing regressions and giving the team confidence to refactor and expand the system.

## Responsibilities
- **Test Coverage Enhancement**: Identifying and filling gaps in unit and integration tests.
- **Regression Prevention**: Writing tests that specifically target known bugs or complex edge cases.
- **Mocking and Fixtures**: Maintaining high-quality test data and mocks for complex systems like WhatsApp or LLMs.
- **Service Verification**: Ensuring that every service in `src/robbot/services` has localized unit tests.
- **Pipeline Validation**: Writing integration tests that verify the full message processing flow.

## Best Practices
- **Test Isolation**: Ensure that tests don't depend on each other or external shared state.
- **Clean State**: Use database transactions that rollback after every test.
- **Meaningful Assertions**: Focus on state changes and business logic outcomes, not just code execution.
- **Maintainable Tests**: Keep test code as clean and well-structured as the production code.

## Key Project Resources
- [Testing Strategy](../docs/testing-strategy.md)
- [Architecture Notes](../docs/architecture.md)
- [Data Flow](../docs/data-flow.md)

## Repository Starting Points
- `tests/unit/`: The primary hub for service-level testing.
- `tests/integration/`: Where multi-service scenarios are verified.
- `tests/api/`: The hub for endpoint and flow verification.

## Key Files
- `tests/api/conftest.py`: Central hub for API test fixtures and auth setup.
- `tests/unit/test_message_filter_service.py`: Example of high-quality localized testing.

## Key Symbols for This Agent
- `pytest.fixture`: The primary tool for managing test state.
- `unittest.mock`: The primary tool for isolating components.

## Documentation Touchpoints
- [README](../docs/README.md)
- [Development Workflow](../docs/development-workflow.md)

## Collaboration Checklist
1. Identify a module with low test coverage or high risk.
2. Outline the test scenarios (happy path, edge cases, error conditions).
3. Implement the tests using the project's standard fixtures.
4. Verify that the tests pass and catch potential issues.
5. Provide a summary of the improved coverage.
