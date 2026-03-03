# Security & Compliance Notes

## Authentication & Authorization
- **API Keys**: Access to the FastAPI endpoints is protected by API keys defined in the `.env` file.
- **JWT / Sessions**: Admin sessions for the dashboard and management endpoints use secure tokens.
- **WAHA Session**: Communication with the WAHA container is authenticated via session names and (optionally) an API key.
- **Role-Based Access**: The system differentiates between `Admin` and `User` (Secretary) roles for dashboard actions.

## Secrets & Sensitive Data
- **Environment Variables**: All sensitive keys (Postgres password, Redis password, OpenAI/Groq/Gemini keys) MUST be stored in the `.env` file and NEVER committed to the repository.
- **Encryption at Rest**: PostgreSQL data volumes should be encrypted on the host system in production.
- **Logging Policy**: Sensitive lead information (like health details) should be treated with care. Logs should avoid printing full message payloads unless necessary for debugging.

## Compliance & Policies
- **GDPR / LGPD**: As a system handling Brazilian clinical data, it must eventually comply with LGPD (Lei Geral de Proteção de Dados).
- **Data Retention**: Lead data and conversation history are kept indefinitely by default but can be purged using administrative scripts.

## Incident Response
- **Monitoring**: Check `diagnose_health.py` and `monitor_workers.py` for system health.
- **Escalation**: System failures (e.g., WAHA connection lost) are logged as ERRORs and should notify clinical administrators if persistent.
- **Recovery**: Database backups are performed via `pg_dump` or managed cloud backups.
