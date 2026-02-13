# Migration Patterns Reference

## Exclusion Patterns

### Directories to Exclude

These directories are never scanned during migration:

| Pattern | Reason |
|---------|--------|
| `para/` | Already in PARA structure |
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
- **Low / Unclear**: Mark as "수동 분류 필요" (manual classification needed)

## Directory Handling

### Single Files

When a directory contains only one document file (`.md` or `.txt`), flatten it:

```
docs/api/overview.md → para/resources/api-overview.md
```

### Related File Groups

When a directory contains multiple related files, preserve the directory structure:

```
docs/project-alpha/
├── requirements.md
├── design.md
└── timeline.md

→ para/projects/project-alpha/
  ├── requirements.md
  ├── design.md
  └── timeline.md
```

### Mixed Directories

When a directory contains files that belong to different PARA categories, split them:

```
docs/
├── api-reference.md    → para/resources/api-reference.md
├── sprint-plan.md      → para/projects/sprint-plan.md
└── coding-standards.md → para/areas/coding-standards.md
```

## Name Conflict Resolution

When the destination path already exists:

1. **Same content** (identical or near-identical): Skip the file, report as duplicate
2. **Different content**: Append a numeric suffix to the filename

```
para/resources/api-reference.md       (existing)
para/resources/api-reference-2.md     (new file with conflict)
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
