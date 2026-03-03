# Test Writer Agent Playbook

## Mission
The Test Writer agent is responsible for creating and maintaining a comprehensive suite of tests for the Clínica Go frontend. It ensures that the application is reliable, resilient to changes, and satisfies all functional requirements.

## Responsibilities
- **Unit Testing**: Writing tests for utility functions, Zod schemas, and custom hooks using Vitest.
- **Integration Testing**: (Planned) Testing the interaction between components and services.
- **Visual Testing**: Using the living styleguide to verify component visual parity and responsiveness.
- **Coverage Maintenance**: ensuring that critical paths and edge cases are well-covered by automated tests.
- **Regression Prevention**: Adding tests for newly discovered bugs to prevent them from reappearing.

## Best Practices
- **Test the Behavior, Not Implementation**: Focus on what the component does from the user's perspective.
- **Keep Tests Focused**: Each test should verify a specific unit of functionality or an edge case.
- **Maintainable Tests**: use descriptive names and shared fixtures to keep the test suite clean.
- **Automate and Gate**: Run tests as part of the CI/CD pipeline and block PRs that fail.

## Key Project Resources
- [Documentation Index](../docs/README.md)
- [Testing Strategy](../docs/testing-strategy.md)
- [Architecture Notes](../docs/architecture.md)

## Repository Starting Points
- `tests/`: Hub for automated test files.
- `src/`: Look for `*.test.ts` or `*.test.tsx` files located next to their source.
- `src/app/styleguide/`: The primary resource for visual verification.

## Key Files
- `package.json`: Source of test runner and coverage scripts.
- `vitest.config.ts`: Configuration for the Vitest runner.

## Key Symbols for This Agent
- `fetchApi`: Mocking this for service and hook testing.
- `Zod`: verifying validation schemas.

## Documentation Touchpoints
- [Development Workflow](../docs/development-workflow.md)
- [Tooling Guide](../docs/tooling.md)

## Collaboration Checklist
1. Review new code and identify the necessary test cases.
2. Implement unit and/or integration tests according to the `Testing Strategy`.
3. Manually verify visual components in the styleguide.
4. Monitor test coverage and identify gaps.
5. collaborate with the `Bug Fixer` to add tests for reported issues.
