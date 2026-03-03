---
status: completed
generated: 2026-02-10
---
# Security & Compliance Notes

Maintaining the security and privacy of sensitive patient data is paramount for Clínica Go. This document outlines the security measures and compliance guardrails implemented within the frontend application.

## Authentication & Authorization
- **Identity Management**: Established via the `useAuth` hook and `authService`, managing session states and secure tokens. ([`src/hooks/useAuth.ts`](src/hooks/useAuth.ts))
- **Session Strategy**: Uses secure, cookie-based sessions or JWTs established by the backend AI orchestration layer.
- **Role-Based Access**: UI components and routes are conditionally rendered/restricted based on the authenticated user's permissions (e.g., Admin vs. Staff).

## Secrets & Sensitive Data
- **Environment Configuration**: API endpoints and non-sensitive keys are managed via `.env.local`.
- **Zero Secrets Policy**: No sensitive API keys or credentials should ever be hardcoded or committed to the repository.
- **Secure Storage**: Sensitive patient identifiers and tokens are handled through secure transmission and never stored in insecure client-side locations like `localStorage`.

## Compliance & Policies
- **Data Privacy**: The frontend is designed to support compliance with health data regulations (like HIPAA or LGPD in Brazil).
- **Data Minimization**: The UI only requests and displays the minimum necessary data required for the user's specific workflow.
- **Auditability**: Significant user actions are tracked via backend logging for security auditing purposes.

## Cross-References
- [Architecture Notes](./architecture.md)
- [Project Overview](./project-overview.md)
