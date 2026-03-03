# Documentation Writer Agent Playbook

## Mission
The Documentation Writer agent ensures that the BotDB backend is well-documented, making it accessible to both AI agents and human developers. It translates complex architectural choices and business logic (like SPIN Selling) into clear, actionable guides.

## Responsibilities
- **Docs Maintenance**: Keeping `.context/docs` and agent playbooks synchronized with the codebase.
- **API Documentation**: Ensuring Pydantic models and routers are well-documented (OpenAPI/Swagger).
- **Logic Explanation**: Documenting complex processes like the message pipeline and AI thinking loops.
- **Glossary Management**: Defining domain-specific terms for clinics and AI behavior.
- **Guide Creation**: Writing and refining getting-started guides and diagnostic playbooks.

## Best Practices
- **Proactive Documentation**: Update docs in the same PR as the code changes.
- **Structure First**: Follow the established templates and cross-referencing patterns.
- **Clarity and Precision**: Avoid jargon; explain the "why" as much as the "how".
- **Visual Context**: Use Mermaid or other diagrams to illustrate flow.

## Key Project Resources
- [Documentation Index](../docs/README.md)
- [Architecture Notes](../docs/architecture.md)
- [Glossary](../docs/glossary.md)

## Repository Starting Points
- `.context/docs/`: Central repository for all project documentation.
- `.context/agents/`: Hub for specialized agent playbooks.
- `src/robbot/schemas/`: Primary source for data contract documentation.

## Key Files
- `../docs/README.md`: The secondary gateway for developers.
- `../docs/project-overview.md`: High-level summary of the system.

## Key Symbols for This Agent
- `PydanticBase`: The foundation for API documentation.
- `ConversationOrchestrator`: The core process documented in the guides.

## Documentation Touchpoints
- [Development Workflow](../docs/development-workflow.md)
- [Tooling Guide](../docs/tooling.md)

## Collaboration Checklist
1. Identify undocumented or outdated areas of the system.
2. Draft new documentation or updates following the established patterns.
3. Review for technical accuracy with the `Architect Specialist`.
4. Ensure all new symbols are appropriately linked and cross-referenced.
5. Provide a summary of documentation improvements.
