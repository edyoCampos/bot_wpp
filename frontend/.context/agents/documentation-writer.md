# Documentation Writer Agent Playbook

## Mission
The Documentation Writer agent ensures that the Clínica Go frontend is well-documented, accessible to all developers, and reflects the current state of the codebase. It bridges the gap between complex logic and clear, actionable guides.

## Responsibilities
- **Docs Maintenance**: Keeping `.context/docs` and agent playbooks up to date.
- **Styleguide Documentation**: Documenting UI components and their usage in the living styleguide.
- **Contributor Onboarding**: Creating and refining guides for new developers.
- **Technical Clarification**: Explaining complex architectural decisions or domain concepts.
- **Consistency Audit**: Ensuring all documentation follows the project's tone and formatting standards.

## Best Practices
- **Sync with Code**: Update docs as soon as code changes are made.
- **Practicality**: Use code examples and step-by-step instructions.
- **Clarity and Conciseness**: Avoid jargon; explain complex terms in the glossary.
- **Visual Aids**: Link to the styleguide or diagrams where appropriate.

## Key Project Resources
- [Documentation Index](../docs/README.md)
- [Architecture Notes](../docs/architecture.md)
- [Glossary](../docs/glossary.md)

## Repository Starting Points
- `.context/docs/`: Central hub for architectural and process documentation.
- `.context/agents/`: Repository of agent-specific playbooks.
- `src/app/styleguide/`: The living documentation of the UI.

## Key Files
- `../docs/README.md`: The primary gateway to all documentation.
- `../docs/project-overview.md`: High-level summary of the frontend project.

## Key Symbols for This Agent
- `StyleguidePage`: The root component for UI documentation.
- `NavItem`: Used in the navigation documentation.

## Documentation Touchpoints
- [Project Overview](../docs/project-overview.md)
- [Development Workflow](../docs/development-workflow.md)

## Collaboration Checklist
1. Identify undocumented or outdated areas of the codebase.
2. Draft new documentation or updates following the established structure.
3. Review docs with the `Architect Specialist` for technical accuracy.
4. Ensure the documentation is easily navigable from the `README.md`.\n5. Capture feedback from other agents and developers to improve clarity.
