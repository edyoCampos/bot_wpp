---
type: skill
name: Pr Review
description: Review pull requests against team standards and best practices
skillSlug: pr-review
phases: [R, V]
generated: 2026-02-10
status: completed
scaffoldVersion: "2.0.0"
---

# PR Review Skill

Guidelines for reviewing pull requests in the BotDB (Clínica Go) project.

## Review Checklist

### 1. Functional Correctness
- [ ] Does the change solve the problem described in the task/plan?
- [ ] Are edge cases (e.g., bot being blocked, LLM rate limits) handled?
- [ ] In `DEV_MODE`, does it respect the authorized sender list?

### 2. Code Quality & Standards
- [ ] **Layering**: Does the code respect the API -> Service -> Repository boundary?
- [ ] **Types**: Are all new functions properly type-hinted?
- [ ] **Naming**: Do variable and function names align with the `glossary.md` (e.g., Lead, Conversation, Maturity)?
- [ ] **DRY**: Is there duplicated logic that should be moved to `src/robbot/common/`?

### 3. Testing
- [ ] are there new unit tests in `tests/unit/` for any new logic?
- [ ] Are integration tests in `tests/integration/` updated if service interaction changed?
- [ ] Did you run `pytest` inside the container to verify everything is green?

### 4. Documentation
- [ ] Is the `.context/docs/` directory updated if architecture or workflow changed?
- [ ] Are new environment variables added to `.env.example`?
- [ ] Is there a new plan or execution report in `.context/plans/` for non-trivial changes?

### 5. Security & Privacy
- [ ] Are there any hardcoded secrets or API keys?
- [ ] Is PII (Personally Identifiable Information) handled securely?
- [ ] Does the code prevent potential SQL injection (using SQLAlchemy properly)?

### 6. Performance
- [ ] Are database queries efficient (checking for N+1 issues)?
- [ ] Is Redis used appropriately for caching and job queuing?
- [ ] Are LLM calls optimized (avoiding unnecessary round-trips)?

## Merging Requirements
- All tests MUST pass.
- Linting (Ruff) MUST be clean.
- At least one approval from a relevant specialist agent (e.g., `Architect Specialist` for structural changes).
- Documentation MUST be synchronized.
