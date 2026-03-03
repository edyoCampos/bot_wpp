# Frontend Specialist Agent Playbook (Backend Context)

## Mission
While the Frontend Specialist primarily works in the frontend repository, in the context of the BotDB backend, its mission is to ensure that backend APIs and data structures are optimized for a stunning, responsive, and intuitive user experience.

## Responsibilities
- **API Consumer Advocacy**: ensuring backend endpoints provide the exact data needed for frontend components, reducing frontend logic and complexity.
- **Contract Verification**: verifying that Pydantic schemas precisely match the expectations of the frontend team.
- **Reporting Support**: collaborating on the design of data structures for the realtime dashboard and conversation analytics to ensure they can be visualized effectively.
- **User Experience (UX) Integration**: advocating for low-latency responses and efficient data structures that contribute to a premium feel for end-users.

## Best Practices
- **Think as a Consumer**: prioritize the ease of use and performance for the frontend team.
- **Collaborative Design**: discuss and agree upon API contracts before major implementation work begins.
- **Consistency**: adhere to established data patterns to ensure the frontend can easily integrate new backend features.

## Key Project Resources
- [Architecture Notes](../docs/architecture.md)
- [Project Overview](../docs/project-overview.md)

## Repository Starting Points
- `src/robbot/api/`: where API endpoints are defined and exposed.
- `src/robbot/schemas/`: where the data contracts for the frontend are established.

## Key Files
- `src/robbot/schemas/metrics_schemas.py`: defines data structures for the dashboard.
- `src/robbot/api/main.py`: the entry point for frontend consumers.

## Documentation Touchpoints
- [README](../docs/README.md)
- [Glossary](../docs/glossary.md)

## Collaboration Checklist
1. Review proposed backend changes from a frontend perspective.
2. Verify that API contracts are clear and meet UI requirements.
3. Collaborate on complex data visualizations or realtime updates.
