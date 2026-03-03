---
type: skill
name: Pr Review
description: Review pull requests against team standards and best practices
skillSlug: pr-review
phases: [R, V]
generated: 2026-02-10
status: completed
scaffoldVersion: "2.0.0"
---

# PR Review Skill (Frontend)

Guidelines for reviewing pull requests in the Clínica Go frontend.

## Review Checklist

### 1. Visual & UX Excellence
- [ ] **Responsiveness**: Does it look premium on mobile, tablet, and desktop?
- [ ] **Dark Mode**: Is the UI legible and visually balanced in dark mode?
- [ ] **Animations**: Are transitions smooth and purposeful?
- [ ] **Styleguide**: If a new component was added, is it documented in `/styleguide`?

### 2. Code Quality & Standards
- [ ] **TypeScript**: Are there no `any` types? Are interfaces descriptive?
- [ ] **Components**: Is the component too large? Should it be decomposed into `ui/` elements?
- [ ] **Server/Client Components**: Is the `use client` directive used only where necessary?
- [ ] **Validations**: Do forms use the centralized Zod schemas in `src/lib/validations/`?

### 3. Logic & State
- [ ] **Side Effects**: Are `useEffect` hooks optimized and properly dependency-tracked?
- [ ] **Hooks**: Is shared logic extracted into custom hooks?
- [ ] **API Calls**: Are errors handled gracefully (e.g., using `normalizeApiError`)?

### 4. Tests & Quality
- [ ] **Unit Tests**: Are complex logic or reusable components covered by tests?
- [ ] **Linter**: Does `npm run lint` pass?

### 5. Accessibility
- [ ] **Semantic HTML**: Are appropriate tags used (`button`, `nav`, `main`, etc.)?
- [ ] **Aria Attributes**: Are interactive elements accessible (e.g., screen readers)?

## Merging Requirements
- Zero linting errors.
- Visual verification in the Styleguide.
- Verification of mobile responsiveness.
