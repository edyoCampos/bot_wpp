# Database Drift Report - 2026-02-10

## Issue Summary
During debugging of the WAHA polling bug, it was discovered that the database schema was out of sync with the SQLAlchemy models (`ConversationModel` and `LeadModel`). The Alembic migrations were reported as "up to date" (HEAD), but several columns were missing from the actual Postgres tables.

## Actions Taken
The following columns were manually added to the database to restore functionality without resetting the entire database:

### Table `conversations`
- `closed_at` (TIMESTAMP)
- `is_urgent` (BOOLEAN DEFAULT FALSE)
- `meta_data` (JSONB DEFAULT '{}')

### Table `leads`
- `deleted_at` (TIMESTAMP)

## Resolution Plan
A formal resolution plan has been created to synchronize Alembic with these manual changes and ensure clean migrations moving forward:
- **Plan**: [Sync Alembic with Manual Schema Fixes](../plans/sync-alembic-with-manual-schema.md)

## Recommendation for Future
1. **Always verify migrations**: Before merging changes that modify `models.py`, ensure the auto-generated migration script is checked against the target environment.
2. **Avoid Manual Alterations**: Manual schema changes should be a last resort and immediately followed by an Alembic sync.
3. **Use the Sync Plan**: Follow the [Sync Alembic with Manual Schema Fixes](../plans/sync-alembic-with-manual-schema.md) to formally resolve the current discrepancies.
