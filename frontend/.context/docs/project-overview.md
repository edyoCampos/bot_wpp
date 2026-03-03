---
status: completed
generated: 2026-02-10
---
# Project Overview

BotDB Frontend is the intelligent interface for the Clínica Go healthcare management platform. It provides a premium, responsive user experience for clinic staff to manage patient interactions, appointments, and dashboard analytics, seamlessly integrated with the backend AI orchestration layer.

## Codebase Reference
> **Detailed Analysis**: For complete symbol counts, architecture layers, and dependency graphs, see [`codebase-map.json`](./codebase-map.json).

## Quick Facts
- Root: `d:\_projects\clinica_go\frontend`
- Languages: TypeScript (Primary), CSS (Tailwind)
- Entry: `src/app/page.tsx`
- Full analysis: [`codebase-map.json`](./codebase-map.json)

## Entry Points
- [Main Application](src/app/page.tsx)
- [Authentication](src/app/(auth)/signin/page.tsx)
- [Styleguide](src/app/styleguide/page.tsx)

## Key Exports
Reference [`codebase-map.json`](./codebase-map.json) for the complete list.

## File Structure & Code Organization
- `src/app/` — Next.js App Router pages and layouts.
- `src/components/` — Reusable React components, including UI primitives.
- `src/services/` — API clients and business logic services.
- `src/lib/` — Utility functions, shared constants, and validations.
- `src/hooks/` — Custom React hooks for state and side effects.
- `src/app/styleguide/` — Living documentation of UI components and layouts.

## Technology Stack Summary
The frontend is built with **Next.js 14** (App Router), **React**, and **TypeScript**. Styling is handled by **Tailwind CSS** and **shadcn/ui** components. It uses **React Hook Form** with **Zod** for form management and validation. The design follows a premium aesthetic with dark mode support and rich interactivity.

## Getting Started Checklist
1. Install dependencies with `npm install`.
2. Configure environment variables in `.env.local` (ensure backend URL is correct).
3. Start the development server with `npm run dev`.
4. Visit `http://localhost:3000/styleguide` to explore available components.

## Next Steps
Future phases include deeper integration with the AI backend for real-time conversation flows and advanced clinical data reporting.

## Cross-References
- [Architecture Notes](./architecture.md)
- [Development Workflow](./development-workflow.md)
- [Tooling Guide](./tooling.md)
