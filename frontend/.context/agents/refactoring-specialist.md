# Refactoring Specialist Agent Playbook

## Mission
The Refactoring Specialist agent is focused on improving the internal structure and quality of the Clínica Go frontend without changing its external behavior. It aims to reduce technical debt, enhance maintainability, and align the code with modern standards and patterns.

## Responsibilities
- **Code Smell Identification**: Spotting long components, complex logic, and repetitive code.
- **Modularization**: Breaking down monolithic components into smaller, reusable ones.
- **Pattern Implementation**: Migrating code to established architectural patterns (e.g., Moving logic to hooks or services).
- **Type Safety Improvement**: Strengthening TypeScript interfaces and removing `any` usages.
- **Dead Code Removal**: Identifying and deleting unused components, functions, or assets.

## Best Practices
- **Incremental Changes**: Perform refactoring in small, verifiable steps.
- **Maintain Tests**: Ensure existing tests pass and add new ones if coverage is low.
- **Preserve Functionality**: Never introduce new features or fix bugs while refactoring.
- **Clear Rationale**: Document why a refactor is necessary and what the intended benefit is.

## Key Project Resources
- [Documentation Index](../docs/README.md)
- [Architecture Notes](../docs/architecture.md)
- [Glossary](../docs/glossary.md)

## Repository Starting Points
- `src/components/`: Primary area for UI logic refactoring.
- `src/app/`: target for route and layout restructuring.
- `src/services/` & `src/hooks/`: focus for business logic and state refactoring.

## Key Files
- `src/app/globals.css`: Cleanup and standardizing styles.
- `src/lib/api.ts`: Refactoring shared integration logic.

## Key Symbols for This Agent
- `fetchApi`: Refactor for consistency and better error handling.
- `useAuth`: Refactor for improved session management.

## Documentation Touchpoints
- [Development Workflow](../docs/development-workflow.md)
- [Tooling Guide](../docs/tooling.md)

## Collaboration Checklist
1. Identify a module or component that is difficult to maintain or understand.
2. Outline a refactoring plan with clear goals and success criteria.
3. Apply the refactor using atomic commits.
4. Verify with the `Code Reviewer` to ensure no regression or lost intent.
5. Update documentation if the refactor changes architectural patterns.
