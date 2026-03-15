# Project Overview Template

> Used by the `project-plan` skill to generate `PROJECT-OVERVIEW.md`.
> Replace `{placeholders}` with actual values.

---

```markdown
# {Project Name}

## Purpose

{Why this project exists. What problem does it solve?}

## Goals

1. {Goal 1 — specific, measurable}
2. {Goal 2}
3. {Goal 3}

## Scope

### Included

- {What this project covers}
- {Key deliverables}

### Excluded

- {What is explicitly out of scope}
- {Boundaries and limitations}

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | {e.g., TypeScript, Go, Rust} |
| Framework | {e.g., Next.js, Gin, Actix} |
| Database | {e.g., PostgreSQL, SQLite} |
| Deployment | {e.g., Vercel, Docker, K8s} |

## Related Documents

- [ROADMAP.md](ROADMAP.md) — Phase plan and progress tracking
- [CONCEPT.md](CONCEPT.md) — Project concept (if exists)
```

---

## Field Guidelines

| Field | Required | Notes |
|-------|----------|-------|
| Project Name | Yes | Use the canonical project name |
| Purpose | Yes | 1-3 sentences explaining the "why" |
| Goals | Yes | 2-5 goals, keep them measurable |
| Scope — Included | Yes | What the project delivers |
| Scope — Excluded | Recommended | Prevents scope creep |
| Tech Stack | Optional | Fill in what is decided; skip unknowns |
| Related Documents | Auto | Skill adds links automatically |
