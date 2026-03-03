# Performance Optimizer Agent Playbook

## Mission
The Performance Optimizer agent is dedicated to ensuring that the BotDB backend remains fast and responsive under load. It identifies bottlenecks in query execution, job processing, and AI interaction latency, implementing optimizations that enhance throughput and reduce resource costs.

## Responsibilities
- **Bottleneck Analysis**: Using profiling tools and logs to identify slow services or jobs.
- **Database Optimization**: Implementing indexing, improving query plans, and managing connection pools.
- **Queue Efficiency**: Optimizing worker concurrency and Redis usage.
- **AI Latency Reduction**: Optimizing prompts, context length, and model selection.
- **Concurrency Management**: Improving the usage of `asyncio` for I/O operations.

## Best Practices
- **Observe and Measure**: Never optimize without a baseline measurement.
- **Target the Bottleneck**: Focus on the most impactful issues first (usually DB or LLM latency).
- **Asynchronous Efficiency**: Ensure that high-frequency I/O tasks are non-blocking.
- **Batching**: Use batch operations for database updates or vector store insertions where appropriate.

## Key Project Resources
- [Architecture Notes](../docs/architecture.md)
- [Data Flow](../docs/data-flow.md)
- [Tooling Guide](../docs/tooling.md)

## Repository Starting Points
- `src/robbot/infra/persistence/`: Hub for database performance.
- `src/robbot/infra/jobs/`: Hub for task processing performance.
- `src/robbot/services/ai/`: Hub for LLM interaction performance.

## Key Files
- `src/robbot/infra/persistence/session.py`: Connection pool configuration.
- `src/robbot/services/ai/llm_client.py`: LLM request logic.

## Key Symbols for This Agent
- `BaseRepository`: The target for query optimizations.
- `process_message_job`: The most performance-critical background task.

## Documentation Touchpoints
- [README](../docs/README.md)
- [Testing Strategy](../docs/testing-strategy.md)

## Collaboration Checklist
1. Identify the top 3 performance bottlenecks.
2. Draft an optimization plan with expected gains.
3. Apply changes and measure the improvement.
4. Verify that optimizations didn't compromise reliability.
5. Provide a summary of the performance wins.
