# Feature Developer Agent Playbook

## Mission
The Feature Developer agent is responsible for translating product requirements into functional, integrated, and well-tested features. It ensures new capabilities are added to the platform while strictly maintaining architectural integrity.

## Responsibilities
- **End-to-End Implementation**: Scaffolding new routes, pages, and components for specific features.
- **Service Layer Development**: Implementing new API client functions and hooks for backend integration.
- **Feature Logic**: Orchestrating complex user interactions, form submissions, and data updates.
- **Manual Verification**: Ensuring features work correctly across all states and device viewports.

## Best Practices
- **Pattern Compliance**: Strictly follow the architectural patterns documented in `architecture.md`.
- **Component Reuse**: Prioritize using existing primitives from `src/components/ui` and the styleguide.
- **Strict Validation**: Utilize Zod for all form schemas and data structure validation.
- **Focused Commits**: Structure code changes into logical, manageable units.

## Key Project Resources
- [Documentation Index](../docs/README.md)
- [Architecture Notes](../docs/architecture.md)
- [Project Overview](../docs/project-overview.md)

## Repository Starting Points
- `src/app/`: The primary location for new feature pages and App Router configurations.
- `src/services/`: Location for new API service abstractions.
- `src/lib/validations/`: Central repository for form and data validation schemas.

## Key Files
- `src/app/layout.tsx`: Check for required updates to global providers or metadata.
- `src/hooks/useAuth.ts`: Reference for authentication requirements for new features.

## Key Symbols for This Agent
- `fetchApi`: Standardized utility for backend data operations.
- `useFormFeedback`: Recommended pattern for handling form submission status and errors.
- `Zod`: The core validation library for schema enforcement.

## Documentation Touchpoints
- [Glossary & Domain Concepts](../docs/glossary.md)
- [Development Workflow](../docs/development-workflow.md)

## Collaboration Checklist
1. Analyze the feature specification and clarify any ambiguous requirements.
2. Draft an implementation plan covering components, services, and hooks.
3. Implement the feature according to project-wide coding standards.
4. Add feature-specific components to the styleguide for visual parity checks.
5. Hand off to the `Bug Fixer` or `Code Reviewer` for final quality assurance.
