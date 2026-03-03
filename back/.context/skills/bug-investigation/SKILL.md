---
type: skill
name: Bug Investigation
description: Systematic bug investigation and root cause analysis
skillSlug: bug-investigation
phases: [E, V]
generated: 2026-02-10
status: completed
scaffoldVersion: "2.0.0"
---

# Bug Investigation Skill

Procedures for diagnosing and fixing issues in the BotDB backend.

## Debugging Workflow

### 1. Reproduce & Isolate
- Can the bug be reproduced with a script? Use the existing `scripts/diagnose_health.py` or create a minimal reproduction script.
- Is it an infrastructure issue (Redis down, WAHA session expired) or a logic issue?

### 2. Log Analysis
Check the logs of the relevant service using Docker:
- `docker-compose logs -f api` (for request/response issues)
- `docker-compose logs -f worker` (for message processing issues)
- `docker-compose logs -f polling-worker` (for message ingestion issues)

### 3. Trace the Pipeline
For message processing bugs, follow the data flow defined in `data-flow.md`:
1. Check if the message was fetched by `polling-worker`.
2. Check if it passed the `MessageFilterService` (look for `REJECTED` logs).
3. Check if it was enqueued in Redis (`rq-dashboard` or CLI).
4. Check the worker output for exceptions during AI processing.

## Common Bug Patterns

- **WAHA Silent Drop**: Messages fetched but rejected by filter logic (often due to `fromMe` default or sender format mismatch).
- **Database Drift**: Schema out of sync with models. Symptoms: `ProgrammingError` (missing column) despite migrations being "HEAD".
- **LLM Rate Limits (429)**: Groq/Gemini returning errors. Investigation should check retry logic and exponential backoff.
- **Race Conditions**: Duplicate leads being created simultaneously. Check unique constraints and `MERGE`/`UPSERT` patterns.

## Verification Steps

- **Tests**: Create a regression test in `tests/` that fails without the fix.
- **Environment**: Restart the Docker containers to ensure fresh state.
- **Audit**: Log the fix and root cause in a new report in `.context/plans/` (e.g., `fix-waha-polling-silent-drop.md`).

## Tools for Investigation

- `scripts/diagnose_health.py`: Verifies connectivity to DB, Redis, and WAHA.
- `scripts/monitor_workers.py`: Checks queue health and worker stats.
- `alembic current`: Verifies migration state.
- `pytest -vv`: Detailed test failure output.
