---
slug: api-endpoints
category: features
generatedAt: 2026-02-10
---

# What API endpoints are available?

The frontend consumes the BotDB API version 1.

## API Integration

All endpoints are abstracted in the `src/services/` directory.

### Key Service Modules
- **`authService.ts`**: Handles `/v1/auth/login`, `/v1/auth/signup`, and MFA.
- **`passwordService.ts`**: Handles `/v1/auth/forgot-password` and `/v1/auth/reset-password`.
- **`leadService.ts`**: (Planned) Operations for lead management.
- **`conversationService.ts`**: (Planned) Operations for chat and messages.

### Global Client
We use a centralized `fetchApi` wrapper in `src/lib/api.ts` which handled:
- Base URL configuration.
- Authorization header injection.
- Error normalization.

### Environment Variable
The API base URL is configured via `NEXT_PUBLIC_API_URL`.
