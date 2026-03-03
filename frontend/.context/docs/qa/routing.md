---
slug: routing
category: architecture
generatedAt: 2026-02-10
---

# How does routing work?

We use the **Next.js 14 App Router**.

## Routing Conventions

- **File-based**: Every folder in `src/app` with a `page.tsx` becomes a public route.
- **Route Groups**: Folders with parentheses (e.g., `(auth)`) are used to group routes without affecting the URL structure.
- **Layouts**: `layout.tsx` files are used to share UI (like sidebars or navbars) across multiple pages.

## Key Routes
- `/`: Dashboard entry point (Protected).
- `/signin`: Authentication entry.
- `/styleguide`: Development tool for UI components.

## Programmatic Navigation
Always use the `useRouter` hook from `next/navigation` or the `<Link>` component for client-side transitions to ensure optimal performance.
