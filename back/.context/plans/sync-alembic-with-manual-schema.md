---
status: completed
generated: 2026-02-10
agents:
  - type: "database-specialist"
    role: "Lead implementation of Alembic sync"
  - type: "backend-specialist"
    role: "Verify model alignment with schema"
  - type: "test-writer"
    role: "Verify clean database initialization"
docs:
  - "database_drift.md"
  - "architecture.md"
  - "development-workflow.md"
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
---

# Sync Alembic with Manual Schema Fixes Plan

> Synchronize Alembic migration state with the manually corrected database schema to prevent future drift and migration failures.

## Task Snapshot
- **Primary goal:** Align Alembic's migration history with the manual changes made to `conversations` and `leads` tables to restore a clean automated migration path.
- **Success signal:** `alembic upgrade head` runs successfully on the current database and also on a fresh, empty database.
- **Key references:**
  - [`database_drift.md`](../docs/database_drift.md) — Source of truth for manual changes.
  - `alembic/env.py` — Migration environment configuration.
  - `src/robbot/infra/persistence/models` — Target SQLAlchemy models.

## Codebase Context
The system currently reports being at `HEAD`, but the actual database schema was missing columns defined in the models. Manual `ALTER TABLE` commands were used to bridge this gap. Alembic now needs a "bridge" migration that captures these changes without conflicting with the existing DB state.

### Key Components
- **Migrations**: `alembic/versions/`
- **Models**: `src/robbot/infra/persistence/models/`

## Agent Lineup
| Agent | Role in this plan | Playbook | First responsibility focus |
| --- | --- | --- | --- |
| Database Specialist | Lead | [Database Specialist](../agents/database-specialist.md) | Manage migrations and verify schema integrity. |
| Backend Specialist | Contributor | [Backend Specialist](../agents/backend-specialist.md) | Ensure SQLAlchemy models correctly reflect the intended schema. |
| Test Writer | Validator | [Test Writer](../agents/test-writer.md) | Verify that a fresh database setup works from scratch. |

## Documentation Touchpoints
| Guide | File | Primary Inputs |
| --- | --- | --- |
| Database Drift | [`database_drift.md`](../docs/database_drift.md) | Resolution status and new workflow. |
| Architecture Notes | [`architecture.md`](../docs/architecture.md) | Data persistence layer updates. |
| Development Workflow | [`development-workflow.md`](../docs/development-workflow.md) | Updated migration commands. |

## Risk Assessment
### Identified Risks
| Risk | Probability | Impact | Mitigation Strategy | Owner |
| --- | --- | --- | --- | --- |
| Migration Conflict | High | Medium | Use `if not exists` logic in the migration script. | Database Specialist |
| Data Loss | Low | High | Backup DB before running any Alembic command. | Database Specialist |

### Dependencies
- **Internal:** API and Worker containers must be able to reach Postgres.
- **Technical:** `alembic` CLI installed in the environment.

## Resource Estimation
- **Phase 1 - Discovery**: 1 hour
- **Phase 2 - Implementation**: 2 hours
- **Phase 3 - Validation**: 1 hour
- **Total**: ~4 hours

## Working Phases
### Phase 1 — Discovery & Alignment
**Steps**
1. Run `alembic current` to identify the current tracked revision.
2. verify that `closed_at`, `is_urgent`, and `meta_data` exist in the `conversations` table.
3. Verify that `deleted_at` exists in the `leads` table.

**Commit Checkpoint**
`chore(plan): complete phase 1 discovery for alembic sync`

### Phase 2 — Implementation & Iteration
**Steps**
1. Generate a new migration: `docker-compose exec api alembic revision --autogenerate -m "sync_manual_drift_20260210"`.
2. Edit the generated file. Wrap the `op.add_column` calls in checks or use `postgresql_if_not_exists=True` (if supported) to prevent failure on the current DB.
3. Run `alembic upgrade head`.

**Commit Checkpoint**
`feat(infra): add sync migration for manual schema drift`

### Phase 3 — Validation & Handoff
**Steps**
1. Spin up a fresh Postgres container.
2. Run `alembic upgrade head` on the empty DB and verify the final schema matches the models.
3. Update `database_drift.md` reflecting that the drift is now formally managed.

**Commit Checkpoint**
`chore(plan): complete phase 3 validation for alembic sync`

## Rollback Plan
### Rollback Procedures
1. Restore database snapshot from backup.
2. Delete the created migration file in `alembic/versions/`.
3. Manually update `alembic_version` table to the previous `version_num`.

## Evidence & Follow-up
- PR link with the new migration script.
- Logs of successful `alembic upgrade head` from a clean state.
