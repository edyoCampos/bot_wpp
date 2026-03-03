---
status: completed
generated: 2026-02-10
---
# Architecture Notes

The Clínica Go frontend is a modern web application built on the Next.js framework, designed for scalability, maintainability, and a premium user experience. It follows a component-based architecture with a strong emphasis on reusability, type safety, and clear separation of concerns.

## System Architecture Overview
The frontend serves as the primary client to the BotDB backend, communicating via RESTful APIs. It is implemented as a Next.js application, leveraging Server-Side Rendering (SSR) for SEO and initial load performance, and Client-Side Rendering (CSR) for rich interactivity. Requests are handled by the Next.js App Router, ensuring efficient data fetching and navigation.

## Architectural Layers
- **UI Components**: Reusable interface elements and primitive building blocks (`src/components/`, `src/components/ui/`).
- **Pages & Layouts**: Application routes, route-specific layouts, and page-level state management (`src/app/`).
- **Services**: Abstraction layer for backend API interactions and external service integrations (`src/services/`).
- **Hooks**: Encapsulated stateful logic and shared side effects (`src/hooks/`).
- **Lib**: Shared utility functions, shared constants, and Zod validation schemas (`src/lib/`).

> See [`codebase-map.json`](./codebase-map.json) for complete symbol counts and dependency graphs.

## Detected Design Patterns
| Pattern | Confidence | Locations | Description |
|---------|------------|-----------|-------------|
| Component-Based | 100% | `src/components/` | Modular UI development using reusable React components. |
| Custom Hooks | 95% | `src/hooks/` | Encapsulating complex logic and side effects for reuse across components. |
| Service Layer | 90% | `src/services/` | Centralizing API communication and business logic abstraction. |
| Utility/Lib Pattern | 85% | `src/lib/` | Reusable helper functions and shared configuration assets. |

## Entry Points
- [Root Layout](src/app/layout.tsx)
- [Home Page](src/app/page.tsx)
- [Styleguide Index](src/app/styleguide/page.tsx)
- [Global Styles](src/app/globals.css)

## Public API
| Symbol | Type | Location |
|--------|------|----------|
| `useAuth` | Hook | `src/hooks/useAuth.ts` |
| `fetchApi` | Function | `src/lib/api.ts` |
| `loginApi` | Function | `src/services/authService.ts` |
| `RootLayout` | Component | `src/app/layout.tsx` |

## Top Directories Snapshot
- `src/app/` — Pages and routing structure (approx. 25 files).
- `src/components/` — Reusable UI building blocks (approx. 40 files).
- `src/services/` — Integrated backend services (approx. 10 files).
- `src/lib/` — Shared logic and validation (approx. 15 files).

## Related Resources
- [Project Overview](./project-overview.md)
- [Development Workflow](./development-workflow.md)
- [Testing Strategy](./testing-strategy.md)
