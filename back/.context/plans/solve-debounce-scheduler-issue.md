---
status: unfilled
progress: 100
generated: 2026-02-10
agents:
  - type: "code-reviewer"
    role: "Review code changes for quality, style, and best practices"
  - type: "bug-fixer"
    role: "Analyze bug reports and error messages"
  - type: "feature-developer"
    role: "Implement new features according to specifications"
  - type: "refactoring-specialist"
    role: "Identify code smells and improvement opportunities"
  - type: "test-writer"
    role: "Write comprehensive unit and integration tests"
  - type: "documentation-writer"
    role: "Create clear, comprehensive documentation"
  - type: "performance-optimizer"
    role: "Identify performance bottlenecks"
  - type: "security-auditor"
    role: "Identify security vulnerabilities"
  - type: "backend-specialist"
    role: "Design and implement server-side architecture"
  - type: "frontend-specialist"
    role: "Design and implement user interfaces"
  - type: "architect-specialist"
    role: "Design overall system architecture and patterns"
  - type: "devops-specialist"
    role: "Design and maintain CI/CD pipelines"
  - type: "database-specialist"
    role: "Design and optimize database schemas"
  - type: "mobile-specialist"
    role: "Develop native and cross-platform mobile applications"
docs:
  - "project-overview.md"
  - "architecture.md"
  - "development-workflow.md"
  - "testing-strategy.md"
  - "glossary.md"
  - "data-flow.md"
  - "security.md"
  - "tooling.md"
phases:
  - id: "phase-1"
    name: "Discovery & Alignment"
    prevc: "P"
  - id: "phase-2"
    name: "Implementation & Iteration"
    prevc: "E"
  - id: "phase-3"
    name: "Validation & Handoff"
    prevc: "V"
lastUpdated: "2026-02-10T18:30:41.949Z"
---

# Refactor Message Polling and Debounce Scheduler Plan

> Optimize the WAHA polling scheduler and message debounce logic to reduce latency, avoid redundant API calls, and ensure reliable message grouping.

## Task Snapshot
- **Primary goal:** Reduce polling cycle time, eliminate redundant message fetching, and stabilize the message debounce window.
- **Success signal:** Polling cycles reduced to < 3s; redundant message filtering logs removed; consolidated message processing confirmed for multi-message bursts.
- **Key references:**
  - [Refactoring WAHA Polling (e825288e)](../../brain/e825288e-8d2d-4a1c-8f53-b048be1dda13/overview.txt)
  - [Architecture Notes](../docs/architecture.md)
  - [WAHA API Documentation](https://waha.dev/)

## Codebase Context
- **Total files analyzed:** 267
- **Total symbols discovered:** 913
- **Architecture layers:** Models, Services, Controllers, Config, Utils, Repositories
- **Detected patterns:** Singleton, Repository, Service Layer, Builder

### Key Components
**Core Classes:**
- `TestMessageFilterService` — D:\_projects\clinica_go\back\tests\unit\test_message_filter_service.py:9
- `TestDIInControllers` — D:\_projects\clinica_go\back\tests\unit\test_di_controllers.py:59
- `TestDIErrorHandling` — D:\_projects\clinica_go\back\tests\unit\test_di_controllers.py:137
- `TestControllerIntegration` — D:\_projects\clinica_go\back\tests\unit\test_di_controllers.py:164
- `TestDIContainerInitialization` — D:\_projects\clinica_go\back\tests\unit\test_di_container.py:43
## Agent Lineup
| Agent | Role in this plan | Playbook | First responsibility focus |
| --- | --- | --- | --- |
| Code Reviewer | TODO: Describe why this agent is involved. | [Code Reviewer](../agents/code-reviewer.md) | Review code changes for quality, style, and best practices |
| Bug Fixer | TODO: Describe why this agent is involved. | [Bug Fixer](../agents/bug-fixer.md) | Analyze bug reports and error messages |
| Feature Developer | TODO: Describe why this agent is involved. | [Feature Developer](../agents/feature-developer.md) | Implement new features according to specifications |
| Refactoring Specialist | TODO: Describe why this agent is involved. | [Refactoring Specialist](../agents/refactoring-specialist.md) | Identify code smells and improvement opportunities |
| Test Writer | TODO: Describe why this agent is involved. | [Test Writer](../agents/test-writer.md) | Write comprehensive unit and integration tests |
| Documentation Writer | TODO: Describe why this agent is involved. | [Documentation Writer](../agents/documentation-writer.md) | Create clear, comprehensive documentation |
| Performance Optimizer | TODO: Describe why this agent is involved. | [Performance Optimizer](../agents/performance-optimizer.md) | Identify performance bottlenecks |
| Security Auditor | TODO: Describe why this agent is involved. | [Security Auditor](../agents/security-auditor.md) | Identify security vulnerabilities |
| Backend Specialist | TODO: Describe why this agent is involved. | [Backend Specialist](../agents/backend-specialist.md) | Design and implement server-side architecture |
| Frontend Specialist | TODO: Describe why this agent is involved. | [Frontend Specialist](../agents/frontend-specialist.md) | Design and implement user interfaces |
| Architect Specialist | TODO: Describe why this agent is involved. | [Architect Specialist](../agents/architect-specialist.md) | Design overall system architecture and patterns |
| Devops Specialist | TODO: Describe why this agent is involved. | [Devops Specialist](../agents/devops-specialist.md) | Design and maintain CI/CD pipelines |
| Database Specialist | TODO: Describe why this agent is involved. | [Database Specialist](../agents/database-specialist.md) | Design and optimize database schemas |
| Mobile Specialist | TODO: Describe why this agent is involved. | [Mobile Specialist](../agents/mobile-specialist.md) | Develop native and cross-platform mobile applications |

## Documentation Touchpoints
| Guide | File | Primary Inputs |
| --- | --- | --- |
| Project Overview | [project-overview.md](../docs/project-overview.md) | Roadmap, README, stakeholder notes |
| Architecture Notes | [architecture.md](../docs/architecture.md) | ADRs, service boundaries, dependency graphs |
| Development Workflow | [development-workflow.md](../docs/development-workflow.md) | Branching rules, CI config, contributing guide |
| Testing Strategy | [testing-strategy.md](../docs/testing-strategy.md) | Test configs, CI gates, known flaky suites |
| Glossary & Domain Concepts | [glossary.md](../docs/glossary.md) | Business terminology, user personas, domain rules |
| Data Flow & Integrations | [data-flow.md](../docs/data-flow.md) | System diagrams, integration specs, queue topics |
| Security & Compliance Notes | [security.md](../docs/security.md) | Auth model, secrets management, compliance requirements |
| Tooling & Productivity Guide | [tooling.md](../docs/tooling.md) | CLI scripts, IDE configs, automation workflows |

## Risk Assessment
Identify potential blockers, dependencies, and mitigation strategies before beginning work.

### Identified Risks
| Risk | Probability | Impact | Mitigation Strategy | Owner |
| --- | --- | --- | --- | --- |
| TODO: Dependency on external team | Medium | High | Early coordination meeting, clear requirements | TODO: Name |
| TODO: Insufficient test coverage | Low | Medium | Allocate time for test writing in Phase 2 | TODO: Name |

### Dependencies
- **Internal:** TODO: List dependencies on other teams, services, or infrastructure
- **External:** TODO: List dependencies on third-party services, vendors, or partners
- **Technical:** TODO: List technical prerequisites or required upgrades

### Assumptions
- TODO: Document key assumptions being made (e.g., "Assume current API schema remains stable")
- TODO: Note what happens if assumptions prove false

## Resource Estimation

### Time Allocation
| Phase | Estimated Effort | Calendar Time | Team Size |
| --- | --- | --- | --- |
| Phase 1 - Discovery | 1 person-day | 1 day | 1 person |
| Phase 2 - Implementation | 2 person-days | 2 days | 1 person |
| Phase 3 - Validation | 1 person-day | 1 day | 1 person |
| **Total** | **4 person-days** | **4 days** | **-** |

### Required Skills
- **RQ / Redis knowledge**: To manage debounce jobs and locks.
- **HTTP/Fetch Optimization**: For httpx client pooling.
- **WAHA API Proficiency**: Understanding chat message history constraints.

### Resource Availability
- **Available:** TODO: List team members and their availability
- **Blocked:** TODO: Note any team members with conflicting priorities
- **Escalation:** TODO: Name of person to contact if resources are insufficient

## Working Phases
### Phase 1 — Discovery & Alignment
**Steps**
1. [x] **Analyze Latency**: Profile `poll_waha_messages` to confirm where the 16s are spent (LID resolution vs. sequential HTTP). *(completed: 2026-02-10T18:30:35.953Z)*
2. [x] **Verify Debounce Coherence**: Confirm if 2s window is causing "split" responses for slow typers. *(completed: 2026-02-10T18:30:41.842Z)*
3. [x] **Check Webhook Redundancy**: Evaluate why polling is finding messages that webhooks should have caught (if webhooks are active). *(completed: 2026-02-10T18:30:41.949Z)*

**Commit Checkpoint**
- `git commit -m "docs(plan): finalize discovery for polling optimization"`

### Phase 2 — Implementation & Iteration
**Steps**
1. **Client Pooling**: Modify `WahaMetadataService` to use a persistent `httpx.Client` session.
2. **Stateful Polling**: Update `poll_waha_messages` to store `last_message_id` per chat in Redis.
3. **Efficient Filtering**: Update `MessageFilterService` to only check the `last_message_id` instead of iterating all 10 messages.
4. **Adaptive Debounce**: Increase `MESSAGE_DEBOUNCE_SECONDS` to 5s in `settings.py`.
5. **Webhook Integration**: Add `mark_as_processed` to `webhook_controller.py` to prevent polling race conditions.

**Commit Checkpoint**
- `git commit -m "feat(infra): optimize polling performance and debounce window"`

### Phase 3 — Validation & Handoff
**Steps**
1. **Stress Test**: Simulate 10 rapid messages from one user and verify 1 consolidated AI response.
2. **Load Check**: Verify polling cycle takes < 3s even with 5+ active chats.
3. **Log Audit**: Confirm "já processada" DEBUG logs are minimal or absent during idle periods.

**Commit Checkpoint**
- `git commit -m "test(polling): verify performance and debounce reliability"`

## Rollback Plan
Document how to revert changes if issues arise during or after implementation.

### Rollback Triggers
When to initiate rollback:
- Critical bugs affecting core functionality
- Performance degradation beyond acceptable thresholds
- Data integrity issues detected
- Security vulnerabilities introduced
- User-facing errors exceeding alert thresholds

### Rollback Procedures
#### Phase 1 Rollback
- Action: Discard discovery branch, restore previous documentation state
- Data Impact: None (no production changes)
- Estimated Time: < 1 hour

#### Phase 2 Rollback
- Action: TODO: Revert commits, restore database to pre-migration snapshot
- Data Impact: TODO: Describe any data loss or consistency concerns
- Estimated Time: TODO: e.g., 2-4 hours

#### Phase 3 Rollback
- Action: TODO: Full deployment rollback, restore previous version
- Data Impact: TODO: Document data synchronization requirements
- Estimated Time: TODO: e.g., 1-2 hours

### Post-Rollback Actions
1. Document reason for rollback in incident report
2. Notify stakeholders of rollback and impact
3. Schedule post-mortem to analyze failure
4. Update plan with lessons learned before retry

## Execution History

> Last updated: 2026-02-10T18:30:41.949Z | Progress: 100%

### phase-1 [DONE]
- Started: 2026-02-10T18:30:35.953Z
- Completed: 2026-02-10T18:30:41.949Z

- [x] Step 1: Step 1 *(2026-02-10T18:30:35.953Z)*
  - Notes: Confirmed 16s latency in logs for polling cycle. Analysis shows sequential HTTP calls with new client instances and redundant message filtering as primary bottlenecks.
- [x] Step 2: Step 2 *(2026-02-10T18:30:41.842Z)*
  - Notes: Verified that 2s debounce window is likely too short for human typing patterns. Confirmed that Webhook controller lack of 'mark_as_processed' creates a race condition where polling picks up the same messages.
- [x] Step 3: Step 3 *(2026-02-10T18:30:41.949Z)*
  - Notes: Confirmed redundancy in polling logs. Webhooks and polling are not sharing the processed state effectively in Redis.
