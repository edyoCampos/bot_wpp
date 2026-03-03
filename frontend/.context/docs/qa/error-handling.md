---
slug: error-handling
category: features
generatedAt: 2026-02-10
---

# How are errors handled?

Our error handling strategy ensures that backend errors are normalized and presented to the user in a consistent, user-friendly manner.

## Strategy

1.  **Normalization**: The `normalizeApiError` function in `src/lib/api.ts` parses various backend error shapes (validation arrays, simple messages) into a standard `ApiError` object.
2.  **UI Feedback**: We use the `useFormFeedback` hook to display toast notifications for global errors or bind field-specific errors to form inputs.
3.  **Fallback**: Components are wrapped in React Error Boundaries to prevent a single component failure from crashing the entire application.

## Common Error Types
- **401 Unauthorized**: Redirects to sign-in.
- **422 Validation Error**: Maps backend messages to individual form fields via `react-hook-form`.
- **Network Error**: Displays a "Backend Offline" or "Connectivity Issue" notification.