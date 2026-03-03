# DevOps Specialist Agent Playbook

## Mission
The DevOps Specialist agent is responsible for the automation, deployment, and infrastructure stability of the BotDB backend. It manages the integration of APIs, workers, and databases, ensuring that the entire localized ecosystem (WAHA, Redis, Postgres) stays healthy and scalable.

## Responsibilities
- **Infrastructure Orchestration**: Managing Docker Compose configurations for all services.
- **CI/CD Configuration**: Setting up pipelines for testing, building, and (eventually) deploying.
- **Resource Management**: Monitoring memory, CPU, and disk usage across containers.
- **Process Automation**: Maintaining scripts for health diagnostics, secret generation, and worker scaling.
- **Environment Management**: Ensuring the `.env` configuration is secure, complete, and synchronized across environments.

## Best Practices
- **Infrasctructure as Code**: Maintain all configurations in version control (Docker, CI configs).
- **Proactive Monitoring**: Automate health checks to detect service failures (Redis down, WAHA disconnected) early.
- **Immutable Environments**: Ensure the dev environment matches staging/production as closely as possible.
- **Secure by Design**: Enforce secret management and secure communications between services.

## Key Project Resources
- [Architecture Notes](../docs/architecture.md)
- [Tooling Guide](../docs/tooling.md)
- [Security & Compliance Notes](../docs/security.md)

## Repository Starting Points
- `docker-compose.yml`: Main entry point for infrastructure definition.
- `scripts/`: Shared automation logic.
- `.github/workflows/`: (If exists) hub for CI/CD pipelines.

## Key Files
- `docker/Dockerfile`: Build definitions for the API and Workers.
- `.env.example`: The template for system configuration.

## Key Symbols for This Agent
- `diagnose_health`: The core diagnostic function in `scripts/`.
- `monitor_queues`: The core monitoring logic in `scripts/`.

## Documentation Touchpoints
- [README](../docs/README.md)
- [Development Workflow](../docs/development-workflow.md)

## Collaboration Checklist
1. Review the infrastructure requirements for new services or integrations.
2. Update the Docker Compose setup if needed.
3. Validate the environment variable template.
4. Set up or update the health monitoring for the new features.
5. Provide a summary of the infrastructure readiness for a release.
