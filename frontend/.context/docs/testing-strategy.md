---
status: completed
generated: 2026-02-10
---
# Testing Strategy

The Clínica Go frontend focuses on maintaining a high-quality user experience and reliable clinical data management. Our testing strategy combines automated verification of core logic with visual consistency checks via our internal styleguide.

## Test Types
- **Unit & Logic Tests**: We use **Vitest** for testing critical utility functions, custom hooks, and standalone business logic. Tests are located alongside their respective source files.
- **Visual Verification**: The **Styleguide** (`/styleguide`) is our primary tool for verifying component rendering, interactive states (hover, focus), and design system compliance.
- **API/Service Verification**: Integration tests verify that our services correctly interact with the backend APIs and handle data transformations reliably.
- **E2E/Integration**: (Future) We plan to implement **Playwright** for critical path verification, such as authentication and lead qualification flows.

## Running Tests
- **All Tests**: `npm run test`
- **Linting & Formatting**: `npm run lint`
- **Type Checking**: `npx tsc --noEmit`

## Quality Gates
- **Zero Lint Violations**: Code must pass all ESLint and Prettier checks before merging.
- **TypeScript Stability**: All new code must satisfy the TypeScript compiler without type suppresses or the use of `any`.
- **Review Approval**: Every UI change must be visually verified in the styleguide by a reviewer.

## Troubleshooting
- **Hydration Mismatches**: Be mindful of client-only state or dynamic data (like dates) that might differ between server and client.
- **JIT Refresh**: If Tailwind styles seem stuck, a quick restart of the `npm run dev` process will clear the JIT compilation cache.

## Cross-References
- [Development Workflow](./development-workflow.md)
- [Tooling Guide](./tooling.md)
