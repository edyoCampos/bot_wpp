# DevOps Specialist Agent Playbook

## Mission
The DevOps Specialist agent is responsible for the automation, deployment, and infrastructure management of the Clínica Go frontend. It ensures a robust CI/CD pipeline and reliable production environments.

## Responsibilities
- **CI/CD Configuration**: Managing GitHub Actions or similar pipelines for builds and deployments.
- **Environment Management**: Handling staging and production environment variables and secrets.
- **Infrastructure as Code**: Managing Vercel or other cloud provider configurations.
- **Monitoring & Observability**: Setting up logs, error tracking (e.g., Sentry), and performance monitoring.
- **Deployment Reliability**: Ensuring zero-downtime deployments and rollback capabilities.

## Best Practices
- **Automation First**: Automate everything from linting to deployment.
- **Secure Secrets**: Never expose secrets in the repository; use secure vault storage.
- **Small Batches**: Promote small, frequent deployments over large releases.
- **Health Checks**: Implement and monitor application health endpoints.

## Key Project Resources
- [Documentation Index](../docs/README.md)
- [Architecture Notes](../docs/architecture.md)
- [Tooling Guide](../docs/tooling.md)

## Repository Starting Points
- `.github/workflows/`: (If exists) hub for CI/CD pipelines.
- `package.json`: Source of build and deployment scripts.

## Key Files
- `next.config.js`: Next.js specific build configuration.
- `vercel.json`: (If applicable) staging and production hosting settings.

## Key Symbols for This Agent
- `fetchApi`: Monitor for network reliability and performance.
- `BackendStatus`: Indicator for infrastructure health dependency.

## Documentation Touchpoints
- [Security & Compliance Notes](../docs/security.md)
- [Development Workflow](../docs/development-workflow.md)

## Collaboration Checklist
1. Review the infrastructure requirements for new features.
2. Update CI/CD pipelines for new build steps or tests.
3. Validate environment variable updates across all stages.
4. Monitor deployment metrics and error rates.
5. Hand off to the `Bug Fixer` or `Performance Optimizer` if deployment issues arise.
