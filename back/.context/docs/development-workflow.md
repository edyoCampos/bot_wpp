# Development Workflow

## Development Workflow
Engineering at BotDB follows a structured process centered around containerized development and automated testing. Developers work in locally isolated environments using Docker Compose, ensuring consistency across development, staging, and production.

## Branching & Releases
- **Branching Model**: We use a simplified trunk-based development approach. Feature branches are created for specific tasks and merged into the main branch after passing all CI gates.
- **Releases**: Tagged releases are created when major features or stability milestones are reached. CI/CD pipelines automatically deploy these tags to the respective environments.

## Local Development
Commands to manage your local environment:
- **Build Services**: `docker-compose build`
- **Start All**: `docker-compose up -d`
- **Restart Specific Service**: `docker-compose restart <service_name>`
- **View Logs**: `docker-compose logs -f <service_name>`
- **Run Migrations**: `docker-compose exec api alembic upgrade head`
- **Run Tests**: `docker-compose exec api pytest`

## Code Review Expectations
Before merging any change, ensure:
1.  **Tests Pass**: All unit and integration tests must be green.
2.  **Linting**: Code must comply with Ruff rules (monitored by CI).
3.  **Migrations**: Database changes must include a corresponding Alembic migration (verify via `--autogenerate`).
4.  **Documentation**: Relevant `.context` documents must be updated to reflect architectural or workflow changes.

## Onboarding Tasks
1.  Install Docker and Docker Compose.
2.  Clone the repository and set up your `.env`.
3.  Run `docker-compose up -d` and verify the API is reachable.
4.  Pick a "good first issue" from the task board or study existing unit tests in `tests/unit/` to understand service interactions.

## Cross-References
- [Testing Strategy](./testing-strategy.md)
- [Tooling Guide](./tooling.md)
- [Project Overview](./project-overview.md)
