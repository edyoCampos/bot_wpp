---
slug: project-structure
category: architecture
generatedAt: 2026-02-10
---

# How is the project structured?

The project follows a modular Next.js 14 App Router architecture.

## Directory Map

### `src/app/`
Contains the application routes.
- `(auth)/`: Group for authentication routes (`signin`, `signup`).
- `styleguide/`: Dedicated route for component documentation.
- `forgot/`, `reset/`: Password recovery flows.

### `src/components/`
- `ui/`: Fundamental, presentational components (buttons, inputs, cards).
- `layouts/`: Shared layout structures (dashboard grid, list views).

### `src/services/`
Pure logic for API communication. No UI code allowed here.

### `src/hooks/`
Shared stateful logic like `useAuth`, `useTheme`, or data fetching lifecycle hooks.

### `src/lib/`
- `validations/`: Zod schemas used for form validation.
- `utils.ts`: Small helper functions (e.g., `cn` for Tailwind).
- `api.ts`: Centralized fetch client.