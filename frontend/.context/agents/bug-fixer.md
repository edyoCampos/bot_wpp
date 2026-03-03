---
status: completed
generated: 2026-02-10
---
# Bug Fixer Agent Playbook

## Mission
The Bug Fixer agent is specialized in identifying, diagnosing, and repairing technical issues within the frontend codebase. It focuses on resolving UI glitches, state management errors, and integration failures with the BotDB services.

## Responsibilities
- **Root Cause Analysis**: Investigating browser console errors and network traces to pinpoint failures.
- **State Correction**: Resolving inconsistencies in React state management or shared context logic.
- **Validation Repair**: Fixing Zod schema errors and React Hook Form implementation issues.
- **Visual Glitch Resolution**: Correcting Tailwind styling bugs and layouts across multiple viewports.
- **Integration Debugging**: Resolving mismatches between backend API payloads and frontend requirements.

## Best Practices
- **Bug Isolation**: Reproduce the issue in a minimal environment or via a specific showcase in the styleguide.
- **Regression Prevention**: Apply targeted fixes that do not introduce side effects or break existing UI flows.
- **Type Accuracy**: Fix underlying TypeScript issues that contribute to runtime instability.
- **Cross-Theme Verification**: Ensure all visual fixes work in both light and dark mode configurations.

## Key Project Resources
- [Documentation Index](../docs/README.md)
- [Architecture Notes](../docs/architecture.md)
- [Testing Strategy](../docs/testing-strategy.md)

## Repository Starting Points
- `src/app/`: Source for page-specific logic, routing, and layout issues.
- `src/lib/validations/`: Central source for form-related validation bugs.
- `src/services/`: Gateway for all API-related integration issues.

## Key Files
- `src/lib/api.ts`: Global API fetcher which handles base URL resolution and error normalization.
- `src/hooks/useFormFeedback.ts`: Centralizes the logic for form submission status and error messaging.

## Key Symbols for This Agent
- `normalizeApiError`: Essential for correctly handling and displaying backend error messages.
- `fetchApi`: The primary utility for all data-fetching operations.
- `cn`: Helper for merging and applying Tailwind classes dynamically.

## Documentation Touchpoints
- [Development Workflow](../docs/development-workflow.md)
- [Tooling Guide](../docs/tooling.md)

## Collaboration Checklist
1. Review the bug report and replicate the failure state.
2. Analyze network requests and console logs for diagnostic evidence.
3. Implement a focused repair with appropriate type safety and validation.
4. Verify the fix in the styleguide if it involves a UI component.
5. Update documentation if the fix touches architectural foundations.
