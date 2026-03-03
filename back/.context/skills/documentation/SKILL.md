---
type: skill
name: Documentation
description: Generate and update technical documentation
skillSlug: documentation
phases: [P, C]
generated: 2026-02-10
status: completed
scaffoldVersion: "2.0.0"
---

# Documentation Skill

Guidelines for maintaining the knowledge base of the BotDB (Clínica Go) project.

## Standards

- **Location**: Primary technical documentation resides in `.context/`.
- **Format**: Generic Markdown (GitHub flavored).
- **Tone**: Technical, concise, and actionable for developers/architects.

## Core Documentation Layers

### 1. The .context/docs Directory
This is the source of truth for the system's design and state.
- **README.md**: The index. Keep updated when adding new guide files.
- **architecture.md**: Updates required for structural changes (new layers, new major dependencies).
- **data-flow.md**: Updates required for pipeline changes or new external integrations.
- **glossary.md**: Add new business terms or technical concepts as they emerge.

### 2. Agent Playbooks (.context/agents/)
Keep these synchronized with the project's evolving best practices and key files.
- Update "Key Files" and "Key Symbols" sections to prevent agents from searching outdated paths.

### 3. Plans & Reports (.context/plans/)
Every significant task or bug fix should have a corresponding plan or report.
- **Purpose**: Document the "Why" and "How" of complex changes.
- **Requirement**: Complete the "Execution Report" section after the work is verified.

## Conventions

- **Links**: Use relative markdown links (e.g., `[Architecture](./architecture.md)`).
- **Callouts**: Use Blockquotes for critical information (e.g., `> **CRITICAL**: Manual DB schema drift`).
- **Code Blocks**: Always specify the language for syntax highlighting (e.g., ` ```python `).
- **Auto-Sync**: When a tool updates the codebase structure (e.g., refactoring services), immediately prompt the `Documentation Writer` agent to update the docs.

## README Structure
The project root `README.md` should remain a high-level entry point pointing to the detailed docs in `.context/`.

## API Documentation
The FastAPI Swagger UI is available at `/docs`. Ensure that all route handlers have clear docstrings and annotated return types to make the automated documentation useful.
