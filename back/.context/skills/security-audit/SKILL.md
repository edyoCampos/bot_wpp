---
type: skill
name: Security Audit
description: Security review checklist for code and infrastructure
skillSlug: security-audit
phases: [R, V]
generated: 2026-02-10
status: completed
scaffoldVersion: "2.0.0"
---

# Security Audit Skill

Guidelines for auditing and hardening the BotDB (Clínica Go) environment.

## Security Checklist

### 1. Authentication & Authorization
- [ ] Are all routers in `src/robbot/api/v1/routers/` protected by auth dependencies?
- [ ] Are API keys stored outside the code in `.env`?
- [ ] Is there proper verification of WAHA webhooks/polling requests?

### 2. Data Privacy (PII)
- [ ] Are patient names and phone numbers handled securely?
- [ ] Do logs avoid printing full interaction payloads in `PROD` mode?
- [ ] Is there a mechanism to delete lead data upon request (LGPD compliance)?

### 3. Dependency Security
- [ ] Run `safety check` or `pip-audit` to identify vulnerable libraries.
- [ ] Are third-party clients (LLMs, WAHA) using updated and secure connection settings (TLS)?

### 4. Code Hardening
- [ ] **SQL Injection**: Validate that all database access uses SQLAlchemy models or bound parameters, never raw string interpolation.
- [ ] **Input Sanitization**: Ensure Pydantic schemas enforce strict types to prevent unexpected payload structures.
- [ ] **Error Messages**: Ensure exception handlers don't leak stack traces or internal environment variables to the client.

### 5. Infrastructure
- [ ] Are Redis and PostgreSQL passwords strong and managed via Docker secrets/env?
- [ ] Is the management dashboard served over HTTPS in production?

## Common Vulnerabilities to Check

- **Missing Auth on Management Routes**: Specifically check routes that trigger background jobs or change lead status.
- **Environment Variable Leakage**: Check that CI/CD logs or debug endpoints don't expose `.env` contents.
- **Insecure CORS**: Verify that CORS settings allow only authorized domains.

## Data Validation Requirements

- Every incoming WhatsApp message must be validated through `MessageFilterService`.
- Every API request must match the expected Pydantic schema in `src/robbot/schemas/`.
