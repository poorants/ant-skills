---
name: fe-style-guide
description: Tailwind CSS styling conventions and patterns for consistent UI development. Covers class ordering, responsive design, dark mode, animation, and layout patterns. Use when writing JSX/TSX with Tailwind classes, reviewing styling consistency, implementing responsive layouts, or adding dark mode support. Triggers include style, styling, CSS, Tailwind, responsive, dark mode, layout, animation, 스타일, 반응형, 다크모드.
---

# Style Guide

## Tailwind Class Ordering

Follow consistent ordering in className:

```
layout → sizing → spacing → typography → colors → borders → effects → states
```

```tsx
// Example with correct ordering
<div className="
  flex items-center justify-between   /* layout */
  w-full h-12                         /* sizing */
  px-4 py-2 gap-3                     /* spacing */
  text-sm font-medium                 /* typography */
  bg-background text-foreground       /* colors */
  border border-border rounded-md     /* borders */
  shadow-sm                           /* effects */
  hover:bg-accent transition-colors   /* states */
"/>
```

## Responsive Breakpoints

```
sm: 640px    → Mobile landscape
md: 768px    → Tablet
lg: 1024px   → Desktop
xl: 1280px   → Wide desktop
```

Mobile-first approach. Base styles = mobile, add breakpoints for larger screens:

```tsx
// GOOD - mobile first
<div className="flex flex-col md:flex-row" />
<div className="text-sm md:text-base lg:text-lg" />
<div className="p-4 md:p-6 lg:p-8" />

// BAD - desktop first (requires overriding)
<div className="flex flex-row sm:flex-col" />
```

### Sidebar + Content Layout

```tsx
// Mobile: content full, sidebar as bottom sheet or hidden
// Desktop: sidebar left, content right
<div className="flex flex-col lg:flex-row h-screen">
  <aside className="w-full lg:w-80 lg:h-full border-b lg:border-b-0 lg:border-r">
    {/* sidebar */}
  </aside>
  <main className="flex-1 overflow-auto">
    {/* content */}
  </main>
</div>
```

## Dark Mode

Use Tailwind `dark:` prefix. All dark mode colors come from design tokens:

```tsx
// GOOD - uses tokens (auto-switches via CSS variables)
<div className="bg-background text-foreground" />

// ACCEPTABLE - explicit dark override when tokens aren't enough
<div className="bg-white dark:bg-gray-900" />

// BAD - inline color that breaks dark mode
<div className="bg-[#ffffff]" />
```

Prefer token-based colors (bg-background, text-foreground) which auto-switch via CSS variables over explicit `dark:` prefixes.

## Spacing Rules

- Use Tailwind spacing scale: `0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10, 12, 16, 20, 24`
- Consistent gaps: `gap-2` for tight, `gap-4` for normal, `gap-6` for loose
- Page padding: `p-4` mobile, `p-6` tablet, `p-8` desktop
- Section spacing: `space-y-4` for lists, `space-y-6` for sections

## Animation & Transitions

```tsx
// Interactive elements: always add transition
<button className="transition-colors hover:bg-accent" />
<div className="transition-transform hover:scale-105" />

// Loading states
<div className="animate-pulse bg-muted rounded-md h-4 w-32" />
<div className="animate-spin h-5 w-5 border-2 border-primary border-t-transparent rounded-full" />
```

Transition rules:
- Color changes: `transition-colors`
- Size/position changes: `transition-transform`
- Multiple properties: `transition-all` (use sparingly)
- Duration: default (150ms) is fine for most cases

## Prohibited Patterns

```tsx
// NEVER: inline styles
<div style={{ color: 'red', padding: '20px' }} />

// NEVER: CSS modules or styled-components
import styles from './Component.module.css'

// NEVER: arbitrary values for standard scales
<div className="p-[13px] text-[15px] rounded-[7px]" />

// NEVER: @apply in CSS (defeats the purpose of utility-first)
.card { @apply flex p-4 bg-white; }
```

## cn() Utility for Conditional Classes

Use `cn()` (clsx + tailwind-merge) for conditional and merged classes:

```tsx
import { cn } from '@/lib/utils'

<div className={cn(
  'flex items-center rounded-md px-3 py-2',
  isActive && 'bg-primary text-primary-foreground',
  isDisabled && 'opacity-50 cursor-not-allowed',
  className  // allow parent override
)} />
```
