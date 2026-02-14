---
name: fe-component-rules
description: Component architecture rules for React + TypeScript + shadcn/ui projects. Enforces reusable component structure, naming conventions, props design, and directory organization under web/src/components/. Use when creating new components, refactoring UI, detecting repeated patterns, or reviewing component structure. Triggers include component, 컴포넌트, refactor UI, extract component, reusable, props design.
---

# Component Rules

## Directory Structure

```
web/src/components/
├── ui/               # shadcn/ui primitives (Button, Card, Badge, Dialog...)
├── common/           # Project-wide reusable components
│   ├── UserCard.tsx
│   ├── StatusBadge.tsx
│   └── FilterBar.tsx
├── layout/           # Layout shell components
│   ├── Header.tsx
│   ├── Sidebar.tsx
│   └── PageLayout.tsx
└── {feature}/        # Feature-specific components
    ├── FeatureList.tsx
    └── FeatureDetail.tsx
```

- `ui/`: shadcn/ui only — never hand-edit, use `npx shadcn@latest add`
- `common/`: shared across 2+ features
- `layout/`: page structure shells
- `{feature}/`: scoped to one feature (e.g., `dashboard/`, `settings/`)

## Component File Convention

One component per file. File name = Component name in PascalCase.

```tsx
// web/src/components/common/UserCard.tsx
interface UserCardProps {
  name: string
  email: string
  role?: 'admin' | 'member'
  avatarUrl?: string
}

export function UserCard({ name, email, role, avatarUrl }: UserCardProps) {
  return (...)
}
```

Rules:
- Named export only (no default export)
- Props interface defined in same file, named `{Component}Props`
- Destructure props in function signature

## Variant Pattern

Use `variant` and `size` props for visual variations, following shadcn/ui pattern:

```tsx
import { cva, type VariantProps } from 'class-variance-authority'

const badgeVariants = cva('inline-flex items-center rounded-md px-2 py-1 text-xs font-medium', {
  variants: {
    status: {
      active: 'bg-primary text-primary-foreground',
      inactive: 'bg-secondary text-secondary-foreground',
      pending: 'bg-accent text-accent-foreground',
    },
  },
  defaultVariants: { status: 'active' },
})

interface StatusBadgeProps extends VariantProps<typeof badgeVariants> {
  label: string
}

export function StatusBadge({ status, label }: StatusBadgeProps) {
  return <span className={badgeVariants({ status })}>{label}</span>
}
```

## Componentization Rules

1. **2+ repetitions** = extract to component
   - Same card layout in list and detail view? → `ItemCard`
   - Same badge pattern in multiple places? → `StatusBadge`

2. **Composition over configuration**
   - Prefer children/slots over many boolean props
   - BAD: `<Card showHeader showFooter showIcon type="user" />`
   - GOOD: `<Card><CardHeader>...</CardHeader><CardContent>...</CardContent></Card>`

3. **Keep components focused**
   - One responsibility per component
   - If a component file exceeds 150 lines, consider splitting

4. **Shadcn/ui first**
   - Check if shadcn/ui has the component before building custom
   - Extend shadcn/ui components via wrapper, don't modify `ui/` directly

## Props Guidelines

- Required props: no default value
- Optional props: provide sensible defaults or make nullable with `?`
- Event handlers: `on{Event}` naming (e.g., `onSelect`, `onClose`)
- Render props: `render{Thing}` naming (e.g., `renderItem`)
- Avoid prop drilling beyond 2 levels; use context or composition instead

## Import Convention

```tsx
// External libraries first
import { useState } from 'react'

// Internal components
import { Button } from '@/components/ui/button'
import { UserCard } from '@/components/common/UserCard'

// Utils/types last
import { formatDate } from '@/lib/format'
import type { User } from '@/types'
```

Use `@/` path alias for `web/src/` imports.
