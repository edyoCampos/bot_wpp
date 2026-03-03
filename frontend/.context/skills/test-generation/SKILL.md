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

# Test Generation Skill (Frontend)

Guidelines for testing the Clínica Go frontend.

## Frameworks

- **Unit/Integration**: `Jest` + `React Testing Library`.
- **E2E**: (Planned) `Playwright`.

## Testing Layers

### 1. Component Testing (`src/components/`)
- **Focus**: Verify component rendering under different prop configurations.
- **Check**: Interaction handling (clicks, inputs, submissions).
- **Check**: Accessibility (using `@testing-library/jest-dom`).

### 2. Hook Testing (`src/hooks/`)
- **Focus**: Verify state transitions and side effects in isolation.
- **Tool**: `@testing-library/react-hooks`.

### 3. Service Mocking
- **Pattern**: Mock the `api.ts` `fetchApi` function to simulate backend responses and error states.

## File Organization
- Place test files next to the implementation (e.g., `MyComponent.tsx` -> `MyComponent.test.tsx`) or in a `__tests__` folder within the module.

## Example Request
"Generate a test for the `loginForm` component that mocks `loginApi` and verifies that an error message is displayed when the API returns a 401."

## Coverage Priorities
1.  **Form Validations**: Ensure all Zod schemas are challenged with valid/invalid data.
2.  **Shared Hooks**: `useAuth` and `useFormFeedback` logic.
3.  **Critical Components**: Navbars, auth forms, and dynamic charts.
