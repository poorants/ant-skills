---
name: code-convention
description: "Manage and enforce project code conventions. Extract conventions from existing code, check compliance, and evolve rules over the project lifecycle. Use when user says /code-convention, 'check conventions', 'code style', 'naming rules', 'add convention', 'convention check', 'extract conventions', or asks about coding standards. Triggers include 코드 컨벤션, 코딩 규칙, 네이밍 규칙, 코드 스타일, 컨벤션 검사, 컨벤션 추출, 코딩 표준, 컨벤션 추가."
---

# code-convention: Code Convention Manager

Extract, manage, check, and evolve project code conventions throughout the project lifecycle.

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

## Output Path

Documents are generated in the user's project, not inside the skill directory.
The output path (`{output-dir}`) is determined during `init`:

- Default: `para/areas/code-convention/`
- User can specify a custom path (e.g., `docs/conventions/`, `.conventions/`)

Once set, the path is stored in `.code-convention.json` at the project root:

```json
{
  "outputDir": "para/areas/code-convention",
  "language": "typescript",
  "framework": "next.js",
  "ruleCount": 24,
  "lastEvolvedAt": "2026-03-16"
}
```

All commands read `.code-convention.json` to locate documents.
If the config file is missing, prompt the user to run `init` first.

## Data Sources

| Source | Purpose |
|--------|---------|
| `{output-dir}/CONVENTIONS.md` | Full convention ruleset (skill-managed, user-extendable) |
| `{output-dir}/CHANGELOG.md` | History of convention changes |
| `.code-convention.json` | Config and metadata (skill-managed) |

## Commands

### `init`

Extract conventions from existing code through automated analysis and guided interview.

1. **Scan the codebase** to detect:
   - Primary language(s) and framework(s)
   - Existing linter/formatter configs (`.eslintrc`, `.prettierrc`, `pyproject.toml`, `rustfmt.toml`, etc.)
   - Naming patterns in use (camelCase, snake_case, PascalCase, etc.)
   - File/directory structure patterns
   - Import ordering conventions
   - Comment styles
   - Error handling patterns
2. **Present findings** to the user and ask for confirmation/adjustments:
   - "I detected TypeScript with Next.js App Router. Correct?"
   - "Naming appears to be camelCase for functions, PascalCase for components. Keep this?"
   - "No linter config found. Would you like to establish formatting rules?"
   - Ask about any ambiguous or inconsistent patterns found
3. **Ask additional preferences** not derivable from code:
   - Preferred max line length
   - Import grouping order
   - Comment requirements (e.g., JSDoc for public APIs)
   - Test file conventions
   - Any project-specific rules or prohibited patterns
4. Save config to `.code-convention.json`
5. Ensure `.code-convention.json` is in `.gitignore`:
   - If `.gitignore` exists: check if already listed; if not, append with comment:
     ```
     # Added by code-convention skill
     .code-convention.json
     ```
   - If `.gitignore` does not exist: create it with the above
6. Generate `{output-dir}/CONVENTIONS.md` using [references/convention-template.md](references/convention-template.md)
   - Populate with detected + confirmed rules
   - Each rule gets a unique ID (e.g., `NAME-01`, `FILE-01`, `STYLE-01`)
7. Create `{output-dir}/CHANGELOG.md` with initial entry

### `status` (default)

Display convention summary.

1. Read `.code-convention.json` for output path
2. Read `{output-dir}/CONVENTIONS.md`
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

1. Read `.code-convention.json` for config
2. Read `{output-dir}/CONVENTIONS.md` for the full ruleset
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

1. Read current `{output-dir}/CONVENTIONS.md`
2. Ask the user for:
   - **Category** — Naming, File Structure, Style, Error Handling, Security, or new category
   - **Rule description** — what the rule enforces
   - **Rationale** — why this rule exists
   - **Examples** — good and bad code examples
   - **Severity** — error (must fix) or warning (should fix)
3. Assign next available rule ID in the category (e.g., `NAME-07`)
4. Append to the appropriate section in `{output-dir}/CONVENTIONS.md`
5. Update rule count in `.code-convention.json`
6. Add entry to `{output-dir}/CHANGELOG.md`

### `update <rule-id>`

Modify an existing rule.

1. Find the rule by ID (e.g., `NAME-02`) in `{output-dir}/CONVENTIONS.md`
2. Show current rule content
3. Ask what to update: description, rationale, examples, severity, or deprecate
4. Update `{output-dir}/CONVENTIONS.md`
5. Add entry to `{output-dir}/CHANGELOG.md`

### `evolve`

Re-scan codebase and suggest new or updated conventions.

This is the key command for keeping conventions alive throughout the project.

1. Read current `{output-dir}/CONVENTIONS.md`
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
   ```
4. For each proposal, ask the user: accept, reject, or modify
5. Apply accepted changes to `{output-dir}/CONVENTIONS.md`
6. Update `.code-convention.json` metadata (`lastEvolvedAt`, `ruleCount`)
7. Add entries to `{output-dir}/CHANGELOG.md`

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
| **Style** | `STYLE-` | Formatting, imports, comments, line length |
| **Error Handling** | `ERR-` | try/catch, error types, logging |
| **Security** | `SEC-` | Input validation, secrets, XSS/injection prevention |

## Convention Sources (Priority Order)

When extracting conventions during `init`, resolve conflicts in this order:

1. **Existing linter/formatter configs** — these are already enforced, adopt as-is
2. **Dominant codebase patterns** — what >70% of code already does
3. **User preferences** — from the interview
4. **Language/framework community standards** — fallback for gaps

## Rules

- CONVENTIONS.md is the single source of truth for the project's code style
- Rules are never deleted silently — use `update` to deprecate with rationale
- `evolve` is non-destructive: it only proposes, never auto-applies
- Convention documents are version-controlled (not in `.gitignore`)
- `.code-convention.json` config is local-only (in `.gitignore`)
- `init` respects existing linter configs — conventions complement, not duplicate them
- Each rule must have a rationale — "because I said so" is not acceptable
- All generated documents are written in English
- When checking, skip files matched by `.gitignore` and common ignores (`node_modules/`, `dist/`, etc.)
