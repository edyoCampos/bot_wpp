---
type: skill
name: Bug Investigation
description: Systematic bug investigation and root cause analysis
skillSlug: bug-investigation
phases: [E, V]
generated: 2026-02-10
status: completed
scaffoldVersion: "2.0.0"
---

# Bug Investigation Skill (Frontend)

Systematic diagnosis of issues in the Clínica Go frontend.

## Investigation Flow

1.  **Console Analysis**: Check for React errors (hydratation mismatches), prop-type warnings, or uncaught exceptions.
2.  **Network Tab**: Inspect API request/response payloads. Verify status codes and timing.
3.  **Local State Check**: Use React DevTools to inspect component props and current state.
4.  **Reproduction**: Create a minimal scenario (URL + Interaction) that triggers the bug.

## Common Issue Types

- **Hydration Mismatch**: Inconsistent data between server and client (common in Next.js).
- **Zod Validation Failure**: Form values not meeting schema requirements, causing silent submission failures.
- **Responsive Glitches**: Layout breaking at specific breakpoints.
- **Auth Token Expiration**: Improper handling of 401/403 responses from the backend.

## Debugging Tools

- **Next.js Debugger**: `NODE_OPTIONS='--inspect' next dev`.
- **Network Interceptors**: Log every `fetchApi` call in dev mode.
- **Styleguide**: Test individual components in isolation to see if the bug is atomic or contextual.

## Fix Verification
- Create a test case in `Jest` that asserts the bug is fixed.
- Manually verify across at least two screen sizes (Mobile/Desktop).
