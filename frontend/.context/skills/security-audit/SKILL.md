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

# Security Audit Skill (Frontend)

Safeguarding the Clínica Go frontend.

## Security Checklist

### 1. Authentication & Session
- [ ] Are protected routes shielded by server-side or middleware auth checks?
- [ ] Is the JWT/Session cookie handled with `HttpOnly` and `Secure` flags?
- [ ] Is sensitive user data cleared from state on logout?

### 2. Input & Data Handling
- [ ] **XSS**: Does the UI avoid using `dangerouslySetInnerHTML`? Is string input properly sanitized by React?
- [ ] **Validation**: Are Zod schemas strictly enforcing types and lengths?
- [ ] **Logs**: Are sensitive inputs (passwords, tokens) excluded from `console.log` in development and error reporting in production?

### 3. API Communication
- [ ] Is all communication performed over HTTPS?
- [ ] Are CSRF tokens implemented (if using cookie-based auth)?

### 4. Infrastructure & Dependencies
- [ ] Check for vulnerable NPM packages (`npm audit`).
- [ ] Are environment variables (`.env`) for API base URLs or service keys handled correctly and NOT leaked in the browser bundle?

## Common Vulnerabilities to Check

- **Sensitive Info in URLs**: Avoid putting PII or tokens in query parameters.
- **Insecure Storage**: Avoid `localStorage` for sensitive session data; prefer secure cookies.
- **Exposure of Backend Schema**: Ensure internal backend error details (stack traces) are not shown to the end-user.

## Requirements
- Regular dependency updates.
- Use of secure coding headers (CSP).
