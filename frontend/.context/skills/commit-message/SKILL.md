---
type: skill
name: Commit Message
description: Generate commit messages following conventional commits with scope detection
skillSlug: commit-message
phases: [E, C]
generated: 2026-02-10
status: completed
scaffoldVersion: "2.0.0"
---

# Commit Message Skill (Frontend)

Follow these guidelines for generating commit messages in the Clínica Go frontend project.

## Conventions

We use **Conventional Commits**.

### Format
`<type>(<scope>): <description>`

### Types
- `feat`: New feature (e.g., adding a new chart component).
- `fix`: Bug fix (e.g., fixing alignment in mobile view).
- `refactor`: Structural changes (e.g., breaking down a large page component).
- `style`: UI/UX changes, CSS/Tailwind updates.
- `docs`: Documentation changes (`.context/docs`).
- `test`: Adding or updating tests.
- `chore`: Infrastructure, dependencies, build tasks.

### Scopes
- `ui`: Primitive components in `src/components/ui/`.
- `app`: Routing, layouts, or pages in `src/app/`.
- `services`: API interaction logic in `src/services/`.
- `hooks`: Custom React hooks in `src/hooks/`.
- `lib`: Utilities and validations in `src/lib/`.
- `config`: Tailwind, Next.js, or environment configuration.
- `context`: Updates to the AI context files.

## Examples

- `feat(ui): add GaugeChart component for dashboard`
- `style(app): optimize sidebar responsiveness for tablet`
- `fix(services): handle 401 errors in authService`
- `refactor(lib): move auth validation to shared Zod schema`
- `docs(context): document frontend authentication flow`
