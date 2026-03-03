---
type: skill
name: Code Review
description: Review code quality, patterns, and best practices
skillSlug: code-review
phases: [R, V]
generated: 2026-02-10
status: completed
scaffoldVersion: "2.0.0"
---

# Code Review Skill (Frontend)

Technical patterns and best practices for the Clínica Go frontend.

## Patterns to Enforce

### 1. Atomic UI Architecture
- **Check**: Keep `src/components/ui/` pure and presentational.
- **Check**: Business logic should reside in Custom Hooks or App Page components.

### 2. Tailored Tailwind
- **Check**: Use consistent spacing and color tokens defined in `tailwind.config.ts`.
- **Check**: Avoid arbitrary values (e.g., `w-[123px]`) unless absolutely necessary.
- **Guidance**: Use the `cn()` utility for conditional class merging.

### 3. API Consumption Layer
- **Check**: All API calls must go through `src/services/` using `fetchApi`.
- **Check**: Normalize backend errors using `normalizeApiError` to ensure consistent feedback to the user.

### 4. Form Handling
- **Pattern**: Use `react-hook-form` with `zod` resolver.
- **Guidance**: Use `useFormFeedback` hook for standardizing success/error toast notifications.

## Common Checks

- **Prop Drilling**: If props are passed through more than 2 levels, consider a Context or Refactor.
- **Conditional Rendering**: Handle loading and error states for all asynchronous data fetching.
- **Performance**: Use `React.memo` or `useMemo` for heavy components/computations only after identifying a bottleneck.

## Style & Convention
- **File Naming**: `PascalCase` for components, `camelCase` for hooks and utilities.
- **Imports**: Organize imports (React first, then external libs, then local components/hooks).
