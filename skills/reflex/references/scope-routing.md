# Scope Routing — detail

reflex is hybrid by design: one engine, output routed by each rule's nature. This
mirrors an engram brain workspace (repo-local brain for code-coupled docs + shared
brain for cross-cutting knowledge) and the 2026 industry pattern **"authored
colocated, served/indexed centrally"** (AGENTS.md nearest-wins, docs-as-code). The
question is never "local or global for the skill" — it's "local or global for *this
rule*".

## The three destinations

| Rule nature | Destination | Why |
|---|---|---|
| This codebase's convention, architecture, command, naming | repo `./CLAUDE.md` | code-coupled; reviewed & committed with the code |
| Cross-cutting / personal working style (any project) | user-scope `~/.claude/CLAUDE.md` | follows you across every repo |
| Stack-level convention shared by several repos | a shared convention base (e.g. engram `resources/conventions/<stack>.md`, consumed via `code-convention`) | reused per-stack, curated centrally |

The third is an advanced path — hand stack-general rules to the `code-convention` /
engram convention-base machinery rather than duplicating them into every repo's
CLAUDE.md. For the MVP, route between the first two.

## Default local

Most corrections are code-coupled, so **repo-local is the default**. Benefits:
- The rule is reviewed and versioned with the code it governs.
- It can't leak this repo's specifics into your global behavior.
- It's discoverable by anyone working in the repo (committed CLAUDE.md).

A repo-local rule that turns out to be broadly useful can always be promoted later. A
global rule that turns out to be repo-specific has *already* polluted every other
project before you notice. So the safe direction is local → (maybe) global, never the
reverse by default.

## The promotion signal

Promote a rule from repo-local to global **only when the same rule has independently
fired in ≥2 repos.** That cross-repo repetition is the evidence that it's genuinely
about *how you work* rather than about *this codebase*.

- One repo wanting it → local. (Could just be this project's quirk.)
- The same correction recurring in a second, unrelated repo → propose promotion to
  `~/.claude/CLAUDE.md`, and remove the now-redundant local copies (or leave a local
  note if the repo needs a stricter variant).

When you promote, **generalize the wording** — strip any phrasing that quietly
assumed the original repo's stack or layout.

## Promote, don't homogenize

Global rules are powerful and therefore dangerous: they apply everywhere, so a
mistaken or over-specific global rule misfires across all your work at once. Keep the
bar high:
- Global adoption is **opt-in and evidence-driven** (the ≥2-repo signal), never
  reflexive.
- A repo may always keep a stricter local override; promotion to global is not a
  mandate on every project.
- Prefer the smallest scope that captures the rule. Bloat at the global level is
  worse than bloat at the repo level — it's read on every session everywhere.

## Nearest-wins, like CLAUDE.md itself

Claude Code already composes `~/.claude/CLAUDE.md` (global) with the project
`./CLAUDE.md` (and nested per-directory files), nearest-wins. reflex writes into that
existing hierarchy rather than inventing a parallel store — a learned rule is just a
CLAUDE.md line in the right file, inside the `reflex` block. That keeps reflex's
output legible, diffable, and removable with no special tooling.
