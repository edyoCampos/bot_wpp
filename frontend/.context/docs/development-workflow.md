---
status: completed
generated: 2026-02-10
---
# Development Workflow

Development on the Clínica Go frontend is iterative and component-driven, prioritizing a premium aesthetic and rapid feature delivery. We leverage a living styleguide to ensure design consistency and allow for parallel development of UI components and application logic.

## Branching & Releases
- **Branching Model**: We follow trunk-based development with short-lived feature branches for specific tasks or bugs.
- **Releases**: Deployments are automated via CI/CD pipelines, triggered by merges to the main branch after passing all quality gates.

## Local Development
Commands for day-to-day engineering tasks:
- **Install Dependencies**: `npm install`
- **Start Development Server**: `npm run dev`
- **Build Production Bundle**: `npm run build`
- **Run Linting**: `npm run lint`

## Code Review Expectations
- Ensure all new UI components are showcased in the styleguide (`src/app/styleguide/`).
- Verify full responsiveness (mobile-first) and dark mode compatibility.
- Ensure strict TypeScript typing and avoid using `any`.
- All form logic must use Zod for validation schemas in `src/lib/validations/`.

## Onboarding Tasks
1. Clone the repository and set up your local environment.
2. Run `npm install` to set up dependencies.
3. Start the dev server and explore the `/styleguide` route to understand the design system.
4. Review existing components in `src/components/ui/` to align with the project's visual standards.

## Cross-References
- [Testing Strategy](./testing-strategy.md)
- [Tooling Guide](./tooling.md)
- [Project Overview](./project-overview.md)
