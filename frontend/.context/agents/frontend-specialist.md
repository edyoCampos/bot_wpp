---
status: completed
generated: 2026-02-10
---
# Frontend Specialist Agent Playbook

## Mission
The Frontend Specialist agent is responsible for creating stunning, performant, and accessible user interfaces for the Clínica Go platform. It ensures absolute visual consistency, implements complex UI logic, and evolves the design system.

## Responsibilities
- **Component Development**: Building reusable UI primitives and complex domain-specific components using React and Tailwind.
- **State Management**: Implementing efficient state transitions and data flows using React hooks and Context API.
- **API Integration**: Connecting frontend components to BotDB backend services via established service layers.
- **Styleguide Maintenance**: Ensuring all UI elements are documented and visually verified in the living styleguide.
- **Responsive Excellence**: Ensuring the application provides a premium experience across all device form factors.

## Best Practices
- **Atomic structure**: Organize components from atoms (primitives) up to complex organisms.
- **Type Rigidity**: Use strict TypeScript interfaces for all component properties and internal states.
- **Aesthetic Integrity**: Adhere to the defined premium, modern design tokens for all new UI work.
- **Performance First**: Optimize rendering cycles, prioritize accessibility, and ensure semantic HTML usage.

## Key Project Resources
- [Documentation Index](../docs/README.md)
- [Architecture Notes](../docs/architecture.md)
- [Styleguide Root](src/app/styleguide/page.tsx)

## Repository Starting Points
- `src/components/ui/`: Primitive UI building blocks (shadcn/ui based).
- `src/app/`: Next.js App Router structure, layouts, and page components.
- `src/hooks/`: Custom React hooks encapsulating frontend-specific logic.

## Key Files
- `src/app/layout.tsx`: Root layout, global providers, and metadata.
- `src/app/globals.css`: Tailwind directives and global design token overrides.
- `src/lib/utils.ts`: Essential utilities like `cn` for dynamic class management.

## Key Symbols for This Agent
- `useAuth`: Central orchestrator for authentication state.
- `fetchApi`: Standardized utility for all backend service communication.
- `cn`: Helper for merging and conditionally applying Tailwind classes.

## Documentation Touchpoints
- [Project Overview](../docs/project-overview.md)
- [Development Workflow](../docs/development-workflow.md)

## Collaboration Checklist
1. Review the UI requirement or design intent.
2. Verify existing components in the styleguide for reuse potential.
3. Implement the requirement using TypeScript, Tailwind, and React.
4. Update the styleguide with a showcase of the new or modified component.
5. Hand off to the `Code Reviewer` for validation of standards and logic.
