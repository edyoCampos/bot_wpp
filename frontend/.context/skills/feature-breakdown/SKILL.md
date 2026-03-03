---
type: skill
name: Feature Breakdown
description: Break down features into implementable tasks
skillSlug: feature-breakdown
phases: [P]
generated: 2026-02-10
status: completed
scaffoldVersion: "2.0.0"
---

# Feature Breakdown Skill (Frontend)

Decomposing requirements into UI and logic tasks for Clínica Go.

## Decomposition Sequence

### 1. UX/UI Design Mapping
- Map the requirement to the Design System.
- Need a new component? (Add to `src/components/ui/`).
- Identify layout changes.

### 2. Contract Definition
- Define the backend API needs.
- Create/Update Zod validation schemas in `src/lib/validations/`.

### 3. Component Implementation
- Build atomic sub-components.
- Add them to the styleguide for visual verification.

### 4. Integration & State
- Create or update business logic hooks.
- Implement API services in `src/services/`.
- Wire up the main page components.

### 5. Polish
- Add loading skeletons, error boundaries, and transitions.

## Integration Checklist
- [ ] Responsive design verified?
- [ ] Dark mode verified?
- [ ] API error handling implemented?
- [ ] Styleguide updated?

## Example: "Dashboard Notifications"
1. **Model**: Define `Notification` type in `src/lib/types.ts`.
2. **UI**: Create `NotificationBell` and `NotificationItem` in `src/components/ui/`.
3. **Service**: Add `getNotifications` to `src/services/userService.ts`.
4. **Hook**: Create `useNotifications` hook.
5. **Page**: Integrate into `src/app/dashboard/layout.tsx`.
