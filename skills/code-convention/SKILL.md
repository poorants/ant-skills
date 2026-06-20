---
name: code-convention
description: "Manage a project's code conventions as a machine-readable contract that steers AI coding across sessions — focused on the rules a linter/formatter CAN'T enforce and an agent CAN'T infer (tooling taxonomies like error/test-id/i18n codes, security and architecture invariants), not formatting trivia. Extract from existing code, check compliance, evolve over the lifecycle, and surface the rules where the agent reads them (CLAUDE.md). Use when user says /code-convention, 'check conventions', 'code style', 'naming rules', 'add convention', 'convention check', 'extract conventions', 'project rules', or asks about coding standards. Triggers include 코드 컨벤션, 코딩 규칙, 네이밍 규칙, 코드 스타일, 컨벤션 검사, 컨벤션 추출, 코딩 표준, 컨벤션 추가, 프로젝트 규칙."
---

# code-convention: project rules as an AI-steering contract

Extract, manage, check, and evolve a project's code conventions — but treat them as a
**machine-readable contract that steers AI coding**, not a human-era style guide.

**Why this still matters when AI writes the code:** an agent infers style by mimicking
surrounding code — which only works when the code is *already* consistent, and breaks
down across many AI sessions (the new "many contributors" problem) and in fresh or
messy codebases. Conventions are the deterministic tiebreaker, and they encode the
decisions an agent can NOT infer from reading code.

**What belongs here vs. what to delegate (the dividing line):**
- ❌ **Delegate to tools — do not author here**: formatting, line length, import
  order, trivial naming — anything a formatter/linter (Prettier, eslint, rustfmt,
  clippy, ruff) already enforces deterministically. Duplicating them just rots.
- ✅ **Own here**: the rules tools CAN'T check and an agent CAN'T infer — *tooling
  contracts* (error-code taxonomy `ERR-*`, `data-testid` schemes E2E depends on, i18n
  key rules), security/architecture invariants, and any arbitrary-but-must-be-
  consistent project decision. These are what actually steer the AI.

The contract must live **where the agent reads it**: keep `CONVENTIONS.md` as the
source of truth and ensure `CLAUDE.md` points to it, so every session loads it.

## Shared base + per-repo deltas (inheritance)

Same-stack projects share most conventions, so a stack-level **base** can be
inherited instead of re-decided (and left to drift) per repo:

- The shared base is a **brain resources doc** — `resources/conventions/<stack>.md`
  (e.g. `tauri-react-rust.md`) — that **engram stores and curates**; this skill only
  **consumes** it. Resolve the brain via the engram workspace (the repo's assigned
  brain); if there is no brain/base, operate standalone.
- A repo's contract = **base + deltas**: its `CONVENTIONS.md` declares "inherits
  `<stack>` base" and lists only the project-specific rules (its arbitrary-but-
  consistent decisions, product-specific security/architecture invariants). `check`
  evaluates against **base ∪ deltas**; `init`/`evolve` only write rules NOT already in
  the base (don't restate inherited rules).
- **promote**: when a delta proves itself and is genuinely stack-general, propose
  promoting it into the base (an engram capture/update on that resources doc), then
  other repos inherit it. **Promote, don't homogenize** — adoption is opt-in per repo;
  forcing every rule onto all repos produces monoculture, not cross-pollination.
  Project-specific rules stay deltas. (This skill proposes/consumes; engram owns the
  base doc.)

## Usage

```
/code-convention                  -- show convention summary (default)
/code-convention status           -- same as above
/code-convention init             -- extract conventions from existing code + interview
/code-convention check [path]     -- check code against conventions
/code-convention add              -- add a new convention rule
/code-convention update <rule-id> -- update an existing rule
/code-convention evolve           -- re-scan codebase and suggest new rules
```

## Output Location

The repo's contract lives at a **fixed, committed path** — no config file, no
per-repo path choice (uniformity across repos is the point):

```
.code-convention/
  CONVENTIONS.md   # the repo contract: "inherits <stack> base; deltas below"
  CHANGELOG.md     # history of convention changes
```

`.code-convention/` is a **dotfolder on purpose**: conventions are an *agent contract*,
not published docs, so they stay out of doc-site builds, globs, and the engram lint —
while `CLAUDE.md` surfaces them to every session via `@.code-convention/CONVENTIONS.md`.
Both files are **committed** (version-controlled with the code). There is **no
`.code-convention.json`**: the path is fixed, and stack/language is re-detected on
demand (history lives in `CHANGELOG.md`).

> Migrating an older repo? If conventions sit at a legacy path (`para/areas/code-
> convention/`, `docs/conventions/`, …), `git mv` them to `.code-convention/`, repoint
> the `CLAUDE.md` `@import` and any code/README references, and drop the old
> `.code-convention.json` + its `.gitignore` line.

## Data Sources

| Source | Owner | Purpose |
|--------|-------|---------|
| `resources/conventions/<stack>.md` (in the assigned **brain**) | engram | shared stack **base** this repo inherits — resolve the brain with engram's `workspace.py resolve --json` (`base` field); if there is no brain/base, operate standalone |
| `.code-convention/CONVENTIONS.md` | this skill | the repo contract = **base + project deltas** (committed, `@import`ed from `CLAUDE.md`) |
| `.code-convention/CHANGELOG.md` | this skill | history of convention changes |

## Commands

### `init`

Extract conventions from existing code through automated analysis and guided interview.

1. **Scan the codebase** to detect:
   - Primary language(s) and framework(s) — this also names the **stack** (e.g.
     `tauri-react-rust`)
   - Existing linter/formatter configs (`.eslintrc`, `.prettierrc`, `pyproject.toml`, `rustfmt.toml`, etc.)
   - Naming patterns in use (camelCase, snake_case, PascalCase, etc.)
   - File/directory structure patterns
   - Import ordering conventions
   - Comment styles
   - Error handling patterns
2. **Resolve the shared base (inheritance).** Resolve the assigned brain via engram
   (`workspace.py resolve --json` → `base`) and look for `<base>/resources/conventions/
   <stack>.md`:
   - **Base exists** → the repo contract **inherits** it. Author only **deltas** —
     project-specific rules NOT already in the base. Don't restate inherited rules.
   - **No base / no brain** → operate standalone (author the full ruleset here); offer
     to seed a new stack base in the brain so future repos can inherit it (engram owns
     that doc — propose, don't write it from this skill).
3. **Present findings** to the user and ask for confirmation/adjustments:
   - "I detected TypeScript with Next.js App Router. Correct?"
   - "Naming appears to be camelCase for functions, PascalCase for components. Keep this?"
   - "No linter config found. Would you like to establish formatting rules?"
   - Ask about any ambiguous or inconsistent patterns found
4. **Ask additional preferences** not derivable from code:
   - Preferred max line length
   - Import grouping order
   - Comment requirements (e.g., JSDoc for public APIs)
   - Test file conventions
   - Any project-specific rules or prohibited patterns
5. Generate `.code-convention/CONVENTIONS.md` using [references/convention-template.md](references/convention-template.md)
   - Open with a one-line header declaring inheritance: *"Inherits the `<stack>` base
     (`resources/conventions/<stack>.md`); project deltas below."* (omit if standalone)
   - Populate with detected + confirmed **deltas** (or the full ruleset if standalone)
   - Each rule gets a unique ID (e.g., `NAME-01`, `FILE-01`, `STYLE-01`)
6. Create `.code-convention/CHANGELOG.md` with initial entry
7. **Wire the contract where the agent reads it**: ensure `CLAUDE.md` imports it with
   `@.code-convention/CONVENTIONS.md` (add the line if missing) so every session loads it

### `status` (default)

Display convention summary.

1. Read `.code-convention/CONVENTIONS.md` (fixed path)
2. Note inheritance: if it declares a `<stack>` base, the effective ruleset is
   **base + these deltas** — surface both counts
3. Present summary:

```
Code Conventions — my-project
==============================

Language: TypeScript / Next.js
Rules: 24 (Naming: 6, File Structure: 4, Style: 8, Error Handling: 3, Security: 3)
Last updated: 2026-03-16
Last evolved: 2026-03-16

Categories:
  Naming          6 rules   NAME-01 ~ NAME-06
  File Structure  4 rules   FILE-01 ~ FILE-04
  Style           8 rules   STYLE-01 ~ STYLE-08
  Error Handling  3 rules   ERR-01 ~ ERR-03
  Security        3 rules   SEC-01 ~ SEC-03
```

### `check [path]`

Check code against established conventions.

1. Read `.code-convention/CONVENTIONS.md` for the repo deltas, and (if it declares a
   `<stack>` base) resolve the brain via engram and read `resources/conventions/<stack>.md`
   for the inherited rules — check against **base ∪ deltas**
3. Scan target files:
   - If `path` given: scan that file or directory
   - If no path: scan all source files in project (respect `.gitignore`)
4. For each file, check against every applicable rule
5. Report violations grouped by category, prioritized by severity:

```
Convention Check Results
========================

Scanned: 47 files
Violations: 12 (Naming: 5, Style: 4, Error Handling: 3)
Compliance: 87%

[NAME-02] src/utils/getData.ts:3 — function 'fetch_user' should be camelCase → 'fetchUser'
[NAME-04] src/components/card.tsx:1 — component file 'card.tsx' should be PascalCase → 'Card.tsx'
[STYLE-01] src/api/auth.ts:45 — line too long (134 > 120 chars)
[ERR-01]  src/services/db.ts:23 — empty catch block (must log or rethrow)
...

Top 3 most violated rules:
  1. NAME-02 (camelCase functions) — 5 violations
  2. STYLE-01 (line length) — 4 violations
  3. ERR-01 (empty catch) — 3 violations
```

6. Suggest fixes for each violation

### `add`

Add a new convention rule.

1. Read current `.code-convention/CONVENTIONS.md`
2. Ask the user for:
   - **Category** — Naming, File Structure, Style, Error Handling, Security, or new category
   - **Rule description** — what the rule enforces
   - **Rationale** — why this rule exists
   - **Examples** — good and bad code examples
   - **Severity** — error (must fix) or warning (should fix)
3. Assign next available rule ID in the category (e.g., `NAME-07`)
4. Append to the appropriate section in `.code-convention/CONVENTIONS.md` (as a repo
   **delta** — don't duplicate a rule already in the inherited base)
5. Add entry to `.code-convention/CHANGELOG.md`

### `update <rule-id>`

Modify an existing rule.

1. Find the rule by ID (e.g., `NAME-02`) in `.code-convention/CONVENTIONS.md`
2. Show current rule content
3. Ask what to update: description, rationale, examples, severity, or deprecate
4. Update `.code-convention/CONVENTIONS.md`
5. Add entry to `.code-convention/CHANGELOG.md`

### `evolve`

Re-scan codebase and suggest new or updated conventions.

This is the key command for keeping conventions alive throughout the project.

1. Read current `.code-convention/CONVENTIONS.md`
2. Scan the codebase for:
   - **New patterns** not yet covered by any rule
   - **Inconsistencies** where code follows multiple conflicting patterns
   - **Dead rules** that no longer match any code (codebase has moved on)
   - **New file types or directories** that need conventions
3. Present findings as proposals:
   ```
   Convention Evolution Proposals
   ==============================

   New patterns detected:
     [PROPOSE] API route files consistently use try/catch with NextResponse.json()
               → Suggest adding ERR-04: "API routes must wrap handler in try/catch"

   Inconsistencies found:
     [CONFLICT] 60% of utils use default export, 40% use named export
                → Current rule STYLE-05 says "prefer named exports"
                → 12 files violate this. Enforce or relax?

   Potentially stale rules:
     [STALE] SEC-02 references jQuery XSS — no jQuery in project
             → Remove or update?

   New areas without conventions:
     [GAP] 8 new API route files found since last evolve, no API-specific rules
           → Suggest adding API category?

   Promotion candidates (delta → shared base):
     [PROMOTE] Delta ERR-04 has proven out here and is stack-general, not project-
               specific → propose promoting into resources/conventions/<stack>.md so
               sibling repos can inherit it (engram applies it; adoption stays opt-in)
   ```
4. For each proposal, ask the user: accept, reject, or modify
5. Apply accepted changes to `.code-convention/CONVENTIONS.md` (deltas only)
6. For accepted **promotions**, hand the rule + rationale to engram to capture/update
   on `resources/conventions/<stack>.md` — **promote, don't homogenize** (stack-general
   + opt-in only; project-specific rules stay deltas)
7. Add entries to `.code-convention/CHANGELOG.md`

## Rule Structure

Each rule in CONVENTIONS.md follows this format:

```markdown
### RULE-ID: Short title

**Severity:** error | warning
**Rationale:** Why this rule exists

Description of the rule.

**Good:**
\`\`\`
// correct example
\`\`\`

**Bad:**
\`\`\`
// incorrect example
\`\`\`
```

## Default Categories

These are starting categories. `evolve` can suggest new ones based on project needs.

| Category | Prefix | What it covers |
|----------|--------|----------------|
| **Naming** | `NAME-` | Variables, functions, files, directories, components |
| **File Structure** | `FILE-` | Directory layout, file organization, barrel files |
| **Style** | `STYLE-` | **Delegate formatting/line-length/import-order to the formatter.** Only document style decisions a tool can't enforce (e.g. comment requirements for public APIs) |
| **Error Handling** | `ERR-` | try/catch, error types, logging |
| **Security** | `SEC-` | Input validation, secrets, XSS/injection prevention |
| **Verification** | `VERIFY-` | Verify-before-"done" discipline; scratch-artifact hygiene (detailed runbooks belong in troubleshooting docs, not here) |
| **Versioning** | `VER-` | Commit-message format (Conventional Commits) + automated version/release policy |

## Convention Sources (Priority Order)

When extracting conventions during `init`, resolve conflicts in this order:

1. **Existing linter/formatter configs** — these are already enforced, adopt as-is
2. **Dominant codebase patterns** — what >70% of code already does
3. **User preferences** — from the interview
4. **Language/framework community standards** — fallback for gaps

## Rules

- The repo's contract = inherited `<stack>` base (curated in the brain by engram) + the
  deltas in `.code-convention/CONVENTIONS.md`; the latter is the repo's source of truth
- Rules are never deleted silently — use `update` to deprecate with rationale
- `evolve` is non-destructive: it only proposes, never auto-applies
- Convention documents live at the fixed path `.code-convention/` and are
  **version-controlled** (committed, never in `.gitignore`); there is no separate config
  file — the path is fixed and stack/language is re-detected on demand
- `init` respects existing linter configs — conventions complement, never duplicate them. **Do not author a rule a formatter/linter already enforces** (see "the dividing line" above); the skill owns only what tools can't check and an agent can't infer
- **The conventions are an AI contract first, a human doc second**: ensure `CLAUDE.md` references `CONVENTIONS.md` so every agent session loads it. Prefer rules that are *tooling contracts* (taxonomies other automation depends on), security/architecture invariants, and arbitrary-but-consistent decisions over restating mechanical style
- Each rule must have a rationale — "because I said so" is not acceptable
- All generated documents are written in English
- When checking, skip files matched by `.gitignore` and common ignores (`node_modules/`, `dist/`, etc.)
- For UI projects, a **Verification** category is worth seeding: (1) verify visual/layout changes by actually rendering — never report "done" from a guess; (2) throwaway verification artifacts (screenshots, scratch scripts) live in a git-ignored scratch dir (e.g. `.scratch/`). Keep the detailed *how-to* (Playwright/headless setup) out of conventions — that's a troubleshooting runbook, link it
- When releases are automated (Conventional Commits → `semantic-release`/`release-please`), add a **Versioning** category: the commit/PR-squash-title format becomes a hard rule because it *decides* the next version — `fix:`→patch, `feat:`→minor, `feat!:`/`BREAKING CHANGE`→major (major is only ever a deliberate human marker). Map the project's release intent (e.g. "minor per feature MR, patch per fix") onto commit *types*, not raw merge/commit mechanics
