---
type: skill
name: Refactoring
description: Safe code refactoring with step-by-step approach
skillSlug: refactoring
phases: [E]
generated: 2026-02-10
status: completed
scaffoldVersion: "2.0.0"
---

# Refactoring Skill (Frontend)

Safely improving the structure and quality of the Clínica Go frontend.

## Typical Code Smells

- **God Components**: Large `.tsx` files (300+ lines) mixing layout, state, and business logic.
- **Prop Drilling**: Passing down props through multiple container layers.
- **Inline Logic**: Complex data transformations happening directly in the JSX.
- **Tailwind Spaghetti**: Repetitive and long class strings (extract to reusable components or variables).
- **Hardcoded Strings**: UI labels that should be in a constants file or translation bundle.

## Refactoring Tactics

### 1. Component Extraction
- Identify a section of JSX that can be isolated.
- Pass required data via props.
- Move it to `src/components/` or a local `components/` subfolder.

### 2. Logic to Hooks
- Move `useState`, `useEffect`, and data fetching logic from the component into a dedicated Custom Hook.
- Result: The component becomes a cleaner "View" layer.

### 3. Service Abstraction
- Ensure raw `fetch` or complex API logic is removed from components and moved to `src/services/`.

## Safety Checklist
- [ ] No visual regression in the styleguide.
- [ ] Responsive behavior is preserved.
- [ ] No regression in form validation.
- [ ] TypeScript remains strictly typed (no `any`).
- [ ] Linting passes.
