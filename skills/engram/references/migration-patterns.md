# Migration Patterns Reference

This reference covers the **Classify & Import** operation (scattered, unclassified
docs → PARA folders) — one of engram's three "migration" senses. For the **base
migration** (`para/`→`brain/`) and **connection-layer upgrade** senses, see the
Upgrade Workflow and Link & Connect Workflow in SKILL.md.

## Classify & Import Procedure (Steps 1–6)

The full step detail for the Classify & Import Workflow.

### Step 1: Scan

Discover all candidate documents with Glob.

- Targets: `**/*.md`, `**/*.txt`
- Exclude: documents already inside a PARA category (in flat mode the root's
  `projects/`·`areas/`·`resources/`·`archives/`, in nested mode `brain/` or `para/`),
  and non-document directories such as `.git/`, `node_modules/`.
- Exclude root metadata files: `README.md`, `LICENSE`, `CHANGELOG.md`, etc.

See Exclusion Patterns below for the full list.

### Step 2: Classify

Read each document's content and decide its PARA classification.

- Use the classification flowchart in `references/para-categories.md`.
- Judge by filename/path hints and content keywords.
- Mark uncertain documents as "manual classification needed".

See Classification Heuristics below for detail.

### Step 3: Present Migration Plan

Output the classification as a migration plan. Destination paths follow the
resolved base (flat-mode example shown). State any name collisions in the plan.

```
## Migration Plan

### Classified (12 files)
| Source | Destination | Reason |
|--------|-------------|--------|
| docs/api-spec.md | resources/api-spec.md | Reference material |
| old/roadmap.md | projects/roadmap.md | Active project with deadline |

### Manual Classification Needed (2 files)
| Source | Notes |
|--------|-------|
| notes/misc.md | Content unclear — user decision needed |

### Skipped (3 files)
| Source | Reason |
|--------|--------|
| README.md | Root metadata file |

### Summary
- Total scanned: 17 files
- Auto-classified: 12 files
- Manual needed: 2 files
- Skipped: 3 files
```

### Step 4: Confirm

**Always execute only after user approval.** The user may change a file's
classification, exclude specific files, or specify custom paths.

### Step 5: Execute

Move files according to the approved plan.

1. Ensure the `<base>/` structure via the Init Workflow.
2. Move files with Bash `mv`.
3. Keep directory structure for related file groups (associated files in the same
   directory). See Directory Handling below.

### Step 6: Report

Report the move results, then close with the Integrity Lint.

```
## Migration Report

### Completed (11 files)
- docs/api-spec.md → resources/api-spec.md
- old/roadmap.md → projects/roadmap.md

### Skipped (1 file)
- notes/misc.md — user excluded

### Failed (0 files)

### Next Steps
- `para list` to verify the result
- `para review` to check classification appropriateness
```

## Exclusion Patterns

### Directories to Exclude

These directories are never scanned during migration:

| Pattern | Reason |
|---------|--------|
| `brain/` or `para/` (nested), or root `projects/`·`areas/`·`resources/`·`archives/` (flat) | Already in PARA structure |
| `.git/` | Version control |
| `node_modules/` | Dependencies |
| `dist/`, `build/`, `out/` | Build output |
| `.vscode/`, `.idea/` | IDE configuration |
| `.claude/` | Claude Code configuration |
| `.next/`, `.nuxt/` | Framework cache |
| `vendor/`, `__pycache__/` | Language-specific dependencies |
| `coverage/` | Test coverage output |

### Root Metadata Files to Exclude

These files at the project root serve repository-level purposes and should not be migrated:

- `README.md`, `README`
- `LICENSE`, `LICENSE.md`
- `CHANGELOG.md`, `CHANGES.md`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `CLAUDE.md`
- `package.json`, `package-lock.json`
- `tsconfig.json`, `pyproject.toml`
- `.gitignore`, `.editorconfig`

### Source Code Documentation to Exclude

Documentation embedded within source code directories should stay with the code:

- `src/**/README.md` — code module docs belong with the code
- `lib/**/README.md` — library docs belong with the library
- Files in directories that are primarily code (`src/`, `lib/`, `app/`, `components/`)

## Classification Heuristics

### By Filename and Path

| Pattern | Suggested Category | Confidence |
|---------|-------------------|------------|
| `*roadmap*`, `*plan*`, `*sprint*` | Projects | High |
| `*proposal*`, `*rfc*`, `*spec*` | Projects | Medium |
| `*meeting*`, `*minutes*`, `*standup*` | Projects (under related project) | Medium |
| `*guide*`, `*howto*`, `*tutorial*` | Resources | High |
| `*reference*`, `*cheatsheet*`, `*glossary*` | Resources | High |
| `*process*`, `*policy*`, `*standard*` | Areas | High |
| `*onboarding*`, `*runbook*`, `*playbook*` | Areas | Medium |
| `*template*` | Resources | Medium |
| `*adr*`, `*decision*` | Resources | High |
| `*retrospective*`, `*postmortem*` | Projects (or Archives if old) | Medium |

### By Content Keywords

When filenames are not conclusive, scan the first ~50 lines of content:

| Keywords | Suggested Category |
|----------|-------------------|
| "deadline", "due date", "milestone", "Q1/Q2/Q3/Q4" | Projects |
| "TODO", "in progress", "blocked", "sprint" | Projects |
| "policy", "must", "always", "never", "standard" | Areas |
| "responsible for", "ownership", "maintain" | Areas |
| "how to", "step 1", "usage", "example" | Resources |
| "reference", "see also", "documentation" | Resources |

### Confidence Levels

- **High**: Auto-classify with the suggested category
- **Medium**: Auto-classify but flag for user review in the migration plan
- **Low / Unclear**: Mark as "manual classification needed"

## Directory Handling

### Single Files

When a directory contains only one document file (`.md` or `.txt`), flatten it:

```
docs/api/overview.md → <base>/resources/api-overview.md
```

### Related File Groups

When a directory contains multiple related files, preserve the directory structure:

```
docs/project-alpha/
├── requirements.md
├── design.md
└── timeline.md

→ <base>/projects/project-alpha/
  ├── requirements.md
  ├── design.md
  └── timeline.md
```

### Mixed Directories

When a directory contains files that belong to different PARA categories, split them:

```
docs/
├── api-reference.md    → <base>/resources/api-reference.md
├── sprint-plan.md      → <base>/projects/sprint-plan.md
└── coding-standards.md → <base>/areas/coding-standards.md
```

## Name Conflict Resolution

When the destination path already exists:

1. **Same content** (identical or near-identical): Skip the file, report as duplicate
2. **Different content**: Append a numeric suffix to the filename

```
<base>/resources/api-reference.md       (existing)
<base>/resources/api-reference-2.md     (new file with conflict)
```

Always report conflicts in the migration plan so the user can decide.

## Edge Cases

| Case | Action |
|------|--------|
| Empty file (0 bytes) | Skip, report in skipped list |
| Binary file | Skip, report in skipped list |
| Symbolic link | Skip, report in skipped list |
| File >10MB | Skip, report in skipped list |
| File without extension | Skip unless `.md` or `.txt` |
| Nested deep (>5 levels) | Include but flag for user review |
| File with same name in multiple directories | Treat each independently, resolve conflicts per rules above |

## Upgrade Phase A — Base migration (guarded refactor to `brain/`)

Renaming the base (`para/`→`brain/`, or flat root folders→`brain/`) is a **guarded
refactor, not a bare `git mv`** — the base folder name can be load-bearing far beyond
doc links. Skip if the user wants connection-only, or if `CLAUDE.md` pins a different
base by convention and the user keeps it. Steps:

1. **Grep the whole repo for the old base name** (`para`, or the moved folder names) —
   not just markdown links. It may appear in **code import paths**
   (`module/para/resources/...`), build/CI configs, scripts, or code comments. The
   linter only sees markdown, so these never surface, and a bare `git mv` would break
   compilation, not just links.
   - If the base has become a **code import path**, that's an architectural smell: move
     the embedded/imported package *out* of the doc tree as part of the upgrade, rather
     than carrying `brain/` into source code.
2. **Move with `git mv`** to preserve history:
   - nested rename (`para/`): `git mv para brain`.
   - flat unify (root folders): `git mv projects brain/projects` (and `areas`,
     `resources`, `archives`). Only move folders that exist/are tracked; create
     `brain/archives/.gitkeep` if empty.
3. **Update every non-doc reference** found in step 1: the `CLAUDE.md` doc-layout note,
   config/memory, CI/build scripts, and code (import paths, comments).
4. **Fix doc links**: relative links between docs that move together keep resolving;
   `[[wikilinks]]` resolve by filename and survive. Run `engram_lint.py --json` (it
   auto-detects the new `brain/` base) and fix every `broken_md_links` entry — these
   crossed the moved/not-moved boundary (e.g. into root-level files).
5. **Scope, approve, execute**: because this touches code and not just docs, show the
   full reference-update plan and get approval first (Migration safety rule). It is a
   `git mv`, so it stays reversible.

**Phase B** is the connection-layer upgrade — run the Link & Connect Workflow (per-
folder README MOCs first, then contextual links, then re-lint). **Verify & report**
both phases: base before→after and references updated (A); MOCs created and
orphans/broken links resolved (B).
