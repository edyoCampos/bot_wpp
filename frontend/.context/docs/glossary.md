---
status: completed
generated: 2026-02-10
---
# Glossary & Domain Concepts

This document defines the key terms, domain entities, and type definitions used throughout the Clínica Go frontend.

## Type Definitions
- **`SignInValues`**: Zod schema for the sign-in form. ([`src/lib/validations/auth.ts`](src/lib/validations/auth.ts))
- **`SignUpValues`**: Zod schema for the sign-up form. ([`src/lib/validations/auth.ts`](src/lib/validations/auth.ts))
- **`NavItem`**: Interface for sidebar navigation items. ([`src/app/styleguide/navigation.ts`](src/app/styleguide/navigation.ts))
- **`MessageBubbleProps`**: Properties for the chat message component. ([`src/components/ui/message-bubble.tsx`](src/components/ui/message-bubble.tsx))

## Core Terms
- **Lead**: A potential patient captured via WhatsApp and qualified by the AI bot.
- **Styleguide**: A dedicated development route (`/styleguide`) for showcasing and testing UI components in isolation.
- **BackendStatus**: A component/indicator reflecting the real-time connectivity state to the BotDB API.
- **SPIN Selling**: The methodology used by the bot to qualify leads through specific question types (Situation, Problem, Implication, Need-payoff).

## Personas / Actors
- **Clinic Administrator**: Manages system configuration and monitors bot performance analytics.
- **Secretary/Staff**: Intervenes in patient conversations when the bot escalates or a manual handoff is required.
- **Patient/Lead**: The end-user interacting with the bot via WhatsApp, whose data is displayed in the dashboard.

## Domain Rules & Invariants
- **Authentication**: All dashboard and management pages require a valid authenticated session.
- **Validation**: All form submissions must be validated using Zod schemas before API transmission.
- **Visual Consistency**: All UI components must strictly adhere to the project's design tokens and premium aesthetic markers.

## Cross-References
- [Project Overview](./project-overview.md)
