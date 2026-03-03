# Backend Specialist Agent Playbook

## Mission
The Backend Specialist agent focuses on implementing the server-side logic that powers the BotDB ecosystem. It builds APIs, integrates with AI models, handles message polling, and manages asynchronous tasks to ensure a smooth experience for both leads and clinical staff.

## Responsibilities
- **API Development**: Implementing FastAPI routers and schemas for internal and external consumption.
- **AI Integration**: Orchestrating calls to Gemini and Groq, managing prompts, and handling agentic tool calling.
- **Message Pipeline**: Maintaining the polling and filtering logic that interacts with the WAHA container.
- **Task Scheduling**: Implementing background jobs for reporting, notifications, and lead qualification.
- **Authentication**: Implementing and enforcing secure access patterns for the dashboard.

## Best Practices
- **Pydantic Validation**: Use schemas for ALL incoming and outgoing data to ensure contract consistency.
- **Asynchronous Code**: Leverage `async/await` for I/O bound tasks (API calls, DB queries) but be mindful of blocking operations.
- **Service Layer**: Keep business logic in the `services/` directory, away from the web framework (FastAPI) and the database (SQLAlchemy).
- **Error Handling**: Use custom exceptions and standardized error responses for API consistency.

## Key Project Resources
- [Architecture Notes](../docs/architecture.md)
- [Data Flow](../docs/data-flow.md)
- [Testing Strategy](../docs/testing-strategy.md)

## Repository Starting Points
- `src/robbot/api/`: Routers and endpoints.
- `src/robbot/services/`: Core business logic.
- `src/robbot/infra/`: Client wrappers and external system integrations.

## Key Files
- `src/robbot/services/ai/bot_service.py`: Orchestrates the AI thinking process.
- `src/robbot/infra/jobs/poll_waha_messages.py`: The entry point for WhatsApp data.
- `src/robbot/schemas/`: Data contracts and validation models.

## Key Symbols for This Agent
- `ConversationOrchestrator`: Coordinates message processing.
- `LeadService`: Manages lead lifecycle.
- `AIStatsResponse`: Example of a data contract.

## Documentation Touchpoints
- [README](../docs/README.md)
- [Development Workflow](../docs/development-workflow.md)

## Collaboration Checklist
1.  Define the API contract (Pydantic models) first.
2.  Implement the service logic with unit tests.
3.  Integrate the service into the router.
4.  Verify the end-to-end flow with integration tests.
