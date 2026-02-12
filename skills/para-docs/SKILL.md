---
name: para-docs
description: >
  PARA-based project documentation manager. Organizes documents into
  Projects, Areas, Resources, and Archives under a para/ directory.
  Use when the user wants to manage documents, organize docs, create
  meeting notes, archive projects, or review documentation status.
  Triggers: "문서 관리해줘", "프로젝트 문서화해줘", "회의록 저장해줘",
  "para 정리해줘", "문서 아카이브해줘", "문서 리뷰해줘", "문서 검색해줘",
  "manage documents", "organize docs", "archive project", "review docs",
  "create meeting notes", "move document", "list documents", "search docs",
  "para init", "para review"
---

# PARA Document Manager

Manage project documentation using the PARA method. All documents live under `para/` in the project root.

## Quick Reference

| Category | Path | Purpose | Lifespan |
|----------|------|---------|----------|
| **Projects** | `para/projects/` | Active work with deadlines and goals | Temporary — archive on completion |
| **Areas** | `para/areas/` | Ongoing responsibilities without end date | Persistent — review periodically |
| **Resources** | `para/resources/` | Reference material and collected knowledge | Persistent — update as needed |
| **Archives** | `para/archives/` | Completed or inactive items from above | Permanent — read-only storage |

## Init Workflow

**When**: First `para/` interaction OR `para/` directory missing.
**Auto-execute without confirmation** — this operation is idempotent.

Create the directory structure:

```
para/
├── projects/
├── areas/
├── resources/
└── archives/
```

Steps:
1. Check if `para/` exists using Glob
2. Create missing directories using Bash `mkdir -p`
3. Add `.gitkeep` to each empty directory using Write
4. Report what was created

## Create Workflow

**When**: User wants to create a new document or documentation item.

### Step 1: Determine Category

Ask the user or infer from context. Use the classification guide:
- Has a deadline or specific goal? → **Projects**
- Ongoing responsibility, no end date? → **Areas**
- Reference material for future use? → **Resources**

If uncertain, load `references/para-categories.md` for the detailed classification flowchart.

### Step 2: Determine Structure

**Simple item** (single topic, standalone):
→ Create a single `.md` file directly in the category directory.

**Complex item** (multiple deliverables, ongoing outputs):
→ Create a directory containing multiple `.md` files as needed.

### Step 3: Choose Filename

Naming convention: `kebab-case.md`
- Use descriptive, lowercase names with hyphens
- Include date prefix for time-sensitive items: `YYYY-MM-DD-topic-name.md`
- For directories: `kebab-case/<document-name>.md`

Examples:
- `para/projects/website-redesign/requirements.md`
- `para/areas/team-onboarding.md`
- `para/resources/api-reference.md`
- `para/projects/website-redesign/2024-03-15-kickoff-notes.md`

### Step 4: Write Content

Use plain markdown. No frontmatter required. Start with an H1 title.

**Simple document template:**
```markdown
# [Title]

[Content starts here]
```

**Directory with multiple files:**
```
para/projects/website-redesign/
├── requirements.md
├── design-spec.md
├── 2024-03-15-kickoff-notes.md
└── 2024-03-20-review-notes.md
```

**Meeting notes template:**
```markdown
# [Meeting Title] — YYYY-MM-DD

## Attendees

- [Names]

## Agenda

1. [Topic]

## Notes

[Notes here]

## Action Items

- [ ] [Action item with owner]
```

### Step 5: Confirm and Report

After creation, report:
- Full path of the created file
- Which PARA category it was placed in
- Brief summary of what was created

## Move Workflow

**When**: User wants to relocate a document between PARA categories.

Common moves:
- `projects/` → `archives/` (project completed)
- `areas/` → `archives/` (responsibility ended)
- `resources/` → `archives/` (outdated reference)
- `archives/` → `projects/` (reactivating archived work)

Steps:
1. Identify the source file/directory using Glob
2. Determine the target category (ask user or infer)
3. Verify the target path does not already exist
4. Use Bash `mv` to move the item
5. Report the move: source → destination

**IMPORTANT: Never delete documents. Always move to archives instead.**

## List & Search Workflow

**When**: User wants to see what documents exist or find specific content.

### List (Dashboard)

Generate a summary table for each non-empty PARA category:

```
## PARA Dashboard

### Projects (3 items)
| Name | Type | Last Modified |
|------|------|--------------|
| website-redesign | directory | 2024-03-15 |
| api-migration.md | file | 2024-03-10 |
| q2-planning.md | file | 2024-03-01 |

### Areas (2 items)
...
```

Use Glob to discover items and Bash `git log` or file stats for dates.

### Search

Use Grep to search document content across `para/`.
Use Glob to search by filename patterns.
Report results with file paths and matching context.

## Review Workflow

**When**: User requests a documentation review or periodic checkup.

Load `references/review-checklist.md` for the detailed review procedure.

Steps:
1. Generate the PARA Dashboard (see List workflow)
2. For each project: check if it should be archived (completed, stale >30 days)
3. For each area: check if documentation is current
4. For each resource: check if content is still relevant
5. Present findings as a review report
6. **Suggest** archive candidates — **never auto-archive**
7. Execute moves only after explicit user confirmation

Review report format:
```
## PARA Review Report — YYYY-MM-DD

### Archive Candidates
- [ ] projects/old-project — last modified 45 days ago
- [ ] resources/deprecated-api — superseded by new-api

### Needs Update
- areas/onboarding.md — last reviewed 60 days ago

### Summary
- Projects: X active, Y archive candidates
- Areas: X items, Y need review
- Resources: X items, Y outdated
- Archives: X items total
```

## Rules

1. **Auto-init**: If `para/` doesn't exist when any para operation is requested, create it automatically without asking. This is idempotent and safe.

2. **Never delete**: Documents are never deleted. Inactive items are moved to `archives/`. If the user explicitly asks to delete, warn them and suggest archiving instead. Only proceed with deletion after the user confirms twice.

3. **Hybrid structure**: Items can be either a single file (`topic.md`) or a directory with multiple files (`topic/*.md`). Choose based on expected deliverables.

4. **Naming convention**: All files and directories use `kebab-case`. Date prefixes (`YYYY-MM-DD-`) for time-sensitive documents. No spaces, no uppercase in filenames.

5. **Plain markdown**: No frontmatter, no special syntax. Documents are plain markdown files starting with an H1 heading.

6. **Archive confirmation**: Moving items to archives always requires explicit user confirmation. Never auto-archive. Present candidates and wait for approval.

7. **User language**: Respond in the user's language. Document content follows the user's preference. PARA category directory names are always in English.

8. **Relative paths**: When reporting paths to the user, use paths relative to the project root (e.g., `para/projects/my-doc.md`).
