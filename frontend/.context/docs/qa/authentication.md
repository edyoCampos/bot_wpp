---
slug: authentication
category: features
generatedAt: 2026-02-10
---

# How does authentication work?

We use JWT-based authentication with cookie storage for secure session management.

## Flow Overview

1.  **Login**: User submits credentials via the `SignInForm`.
2.  **API Response**: Backend returns a session and sets an `HttpOnly` cookie.
3.  **State Management**: The `useAuth` hook tracks the user's status (`isAuthenticated`, `user`).
4.  **Route Protection**: Next.js middleware or layout-level checks redirect unauthenticated users to `/signin`.

## Key Files
- `src/hooks/useAuth.ts`: The primary client-side authority for auth state.
- `src/services/authService.ts`: Low-level API calls.
- `src/app/(auth)/`: Contains the dedicated auth pages (signin, signup).

## MFA Support
The system supports Multi-Factor Authentication (MFA). If the backend requires MFA, the frontend redirects the user to an OTP verification step before granting full access.