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

# Commit Message Skill

Follow these guidelines for generating commit messages in the BotDB (Clínica Go) project.

## Conventions

We use **Conventional Commits** to maintain a clean and searchable history.

### Format
`<type>(<scope>): <description>`

### Types
- `feat`: A new feature (e.g., adding a new AI provider).
- `fix`: A bug fix (e.g., fixing the WAHA polling silent drop).
- `refactor`: Code changes that neither fix a bug nor add a feature (e.g., reorganizing `services/` subdirectories).
- `docs`: Documentation changes only (e.g., updating `.context/docs/architecture.md`).
- `test`: Adding missing tests or correcting existing tests.
- `chore`: Changes to the build process or auxiliary tools and libraries (e.g., updating `requirements.txt`).
- `perf`: A code change that improves performance (e.g., optimizing LID resolution).

### Scopes
- `api`: FastAPI routers and application setup.
- `services`: Business logic in `src/robbot/services/`.
- `infra`: Persistence, repositories, and third-party integrations (WAHA, Redis).
- `worker`: RQ worker logic.
- `polling`: Specifically for `message_polling_job.py` and related strategies.
- `schema`: Pydantic models in `src/robbot/schemas/`.
- `tests`: Any changes in the `tests/` directory.
- `config`: Changes in `src/robbot/config/` or `.env`.
- `context`: Changes to the `.context/` documentation and agent playbooks.

## Examples

### Good Commit Messages
- `feat(api): add endpoint for manual lead assignment`
- `fix(polling): fix silent message drop by correcting fromMe default`
- `refactor(services): move AI bot logic to dedicated bot_service.py`
- `docs(context): populate architecture and data-flow guides`
- `test(services): add unit tests for MessageFilterService`
- `chore(config): remove unused OpenAI Whisper environment variables`

### Bad Commit Messages
- `fixed bug` (no type, no scope, vague)
- `update docs` (no scope)
- `feat: added stuff` (missing parentheses for scope, vague)

## Branch Naming
While not strictly enforced by hooks, prefer:
- `feat/feature-name`
- `fix/bug-description`
- `refactor/what-is-being-refactored`

## Semantic Versioning
- **Major**: Breaking changes (rare).
- **Minor**: New features or significant refactors (`feat`).
- **Patch**: Bug fixes and minor improvements (`fix`, `perf`, `docs`).
