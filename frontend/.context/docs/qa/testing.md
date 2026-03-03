---
slug: testing
category: development
generatedAt: 2026-02-10
---

# How do I run and write tests?

We prioritize reliability through a mix of unit tests and visual verification.

## Running Tests

- **Unit Tests**: Run `npm run test` to execute our Vitest test suite.
- **Linting**: Run `npm run lint` periodically to catch style and logic errors.
- **Type Check**: Run `npx tsc --noEmit` to ensure type safety across the project.

## Writing Tests

### Unit Tests
Place `.test.tsx` files next to the component or utility you are testing. Use `React Testing Library` for component interactions.

### Component Verification
Before submitting a PR, ensure your component is registered in the `/styleguide`. This acts as our "manual visual test".

## Mocking API
When testing components that fetch data, use the `fetchApi` mock to simulate varying backend states (loading, success, error).