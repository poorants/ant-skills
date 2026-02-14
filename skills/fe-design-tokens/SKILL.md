---
name: fe-design-tokens
description: Manage design tokens (CSS variables) for Tailwind CSS + shadcn/ui theming. Single source of truth for all design values in web/src/index.css. Use when adding colors, changing themes, creating new design values, or when hardcoded CSS values are detected. Triggers include design tokens, color, theme, radius, shadow, dark mode, CSS variables, 디자인 토큰, 테마, 다크모드.
---

# Design Tokens

All design values live as CSS variables in `web/src/index.css` under `:root`. Tailwind references these via `hsl(var(--token))`. Components use Tailwind classes only. No hardcoded values.

## Base Tokens (shadcn/ui Standard)

These are provided by default. Use as-is.

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --card: 0 0% 100%;           --card-foreground: 222.2 84% 4.9%;
  --popover: 0 0% 100%;        --popover-foreground: 222.2 84% 4.9%;
  --primary: 222.2 47.4% 11.2%;   --primary-foreground: 210 40% 98%;
  --secondary: 210 40% 96.1%;     --secondary-foreground: 222.2 47.4% 11.2%;
  --muted: 210 40% 96.1%;         --muted-foreground: 215.4 16.3% 46.9%;
  --accent: 210 40% 96.1%;        --accent-foreground: 222.2 47.4% 11.2%;
  --destructive: 0 84.2% 60.2%;   --destructive-foreground: 210 40% 98%;
  --border: 214.3 31.8% 91.4%;
  --input: 214.3 31.8% 91.4%;
  --ring: 222.2 84% 4.9%;
  --radius: 0.5rem;
}
```

Values are HSL **without** `hsl()` wrapper. Tailwind config wraps them:
```js
primary: "hsl(var(--primary))"
```

## Theme Switching

Themes override variables via CSS class on `<html>`:

```css
.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  /* override only what changes */
}
```

Rules:
- Theme classes ONLY override existing variables, never add new CSS rules
- Default: light (no class), Dark: `.dark`

## Adding Project-Specific Tokens

When your project needs custom colors beyond the base set:

### Step 1: Define in `web/src/index.css`

```css
:root {
  /* ... base tokens ... */

  /* Project-specific */
  --success: 142 76% 36%;
  --success-foreground: 0 0% 100%;
  --warning: 38 92% 50%;
  --warning-foreground: 0 0% 100%;
}

.dark {
  --success: 142 70% 45%;
  --warning: 38 85% 55%;
}
```

### Step 2: Map in `web/tailwind.config.js`

```js
theme: {
  extend: {
    colors: {
      // ... base colors ...
      success: {
        DEFAULT: "hsl(var(--success))",
        foreground: "hsl(var(--success-foreground))",
      },
      warning: {
        DEFAULT: "hsl(var(--warning))",
        foreground: "hsl(var(--warning-foreground))",
      },
    },
  },
}
```

### Step 3: Use in components

```tsx
<Badge className="bg-success text-success-foreground">Active</Badge>
<Badge className="bg-warning text-warning-foreground">Pending</Badge>
```

## Prohibited Patterns

```tsx
// BAD - hardcoded values
<div className="bg-[#ff0000] text-[14px] p-[20px] rounded-[8px]" />

// GOOD - token-based
<div className="bg-primary text-sm p-4 rounded-md" />
```

Never use Tailwind arbitrary values (`[...]`) for colors, spacing, radius, or font sizes. If a value doesn't exist as a token, add it to the token system first.
