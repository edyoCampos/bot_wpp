---
status: completed
generated: 2026-02-10
---
# Tooling & Productivity Guide

The Clínica Go frontend project incorporates a curated set of tools and configurations designed to ensure code quality, design consistency, and a highly efficient developer experience.

## Tooling & Productivity Guide
This guide outlines the scripts, automation, and editor settings that help our team stay productive and maintain our high standards for visual excellence.

## Required Tooling
- **Node.js 18+**: The essential runtime environment for Modern Next.js development.
- **npm**: Our package manager for handling all dependencies and scripts.
- **Next.js CLI**: Manages our development server, builds, and production runs.
- **Tailwind CSS CLI**: Enforces our utility-first styling system and premium design tokens.

## Recommended Automation
- **ESLint**: Our primary linting engine for identifying problematic patterns.
- **Prettier**: Ensures consistent code formatting across the entire repository.
- **TypeScript**: Provides static type safety to catch errors during development.
- **shadcn/ui CLI**: Used for rapidly adding and updating our core UI primitives.

## IDE / Editor Setup
- **Recommended VS Code Extensions**:
    - **ESLint**: For real-time feedback on code quality.
    - **Prettier**: To automate code formatting on save.
    - **Tailwind CSS IntelliSense**: For instant access to design tokens and utilities.
    - **Next.js Snippets**: To accelerate page and component creation.
- **Editor Configuration**: Ensure that format-on-save is enabled to maintain repository cleanliness.

## Productivity Tips
- **Styleguide Navigation**: Keep a styleguide tab open while developing to verify UI changes in isolation.
- **Fast Refresh**: Leverage Next.js's instantaneous feedback cycle for a smooth development rhythm.
- **Component Reusability**: Always check `src/components/ui` before building a new primitive to avoid duplication.

## Cross-References
- [Development Workflow](./development-workflow.md)
- [Architecture Notes](./architecture.md)
- [Testing Strategy](./testing-strategy.md)
