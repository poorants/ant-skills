---
name: engram
description: >
  Networked PARA document brain. Organizes documents into Projects, Areas,
  Resources, and Archives, AND weaves them into a connected knowledge graph
  via bi-directional links, MOC hub notes, and integrity linting. Layers a
  logical link network on top of physical folders so the vault grows like an
  interconnected brain rather than isolated folders. Use when the user wants
  to manage/organize docs, create meeting notes, archive projects, review
  documentation status, OR connect notes, check link integrity, find orphan
  documents, build a knowledge graph, or update MOCs.
  Triggers: "manage documents", "organize docs", "document the project",
  "save meeting notes", "tidy para", "archive document", "review docs",
  "search docs", "migrate docs", "import docs", "organize existing docs",
  "archive project", "create meeting notes", "move document", "list documents",
  "para init", "para review", "para migrate",
  "connect notes", "link notes", "tidy the knowledge network", "check links",
  "lint links", "link integrity", "broken links", "find orphans",
  "orphan documents", "orphan nodes", "update moc", "knowledge graph",
  "brain check", "engram lint", "engram link"
---

# engram — Networked PARA Document Brain

Manage documents with the PARA method while weaving them into **one connected
knowledge network (a brain)** through bi-directional links, MOC hubs, and
integrity linting. The core idea is 'Networked PARA' — a logical link layer on
top of physical classification (folders).

It works as two layers:

- **Management layer (PARA)**: create, move, archive, migrate, review. Folders
  own governance.
- **Connection layer (Networked Knowledge)**: link documents by context, remove
  orphans, catch broken links. Links own context. Load
  [references/linking-rules.md](references/linking-rules.md) for the detailed
  rules and follow them.

## Path Resolution (do this first)

Before any operation, resolve the **PARA base** — the location where the four
category folders live. This is the first step of every workflow.

1. If the project root already contains any of `projects/`, `areas/`,
   `resources/`, or `archives/` → **flat mode**. The base is the project root
   itself; categories are `projects/`, `areas/`, `resources/`, `archives/`
   (no `para/` prefix).
2. Otherwise → **nested mode**. The base is `para/`; categories are
   `para/projects/`, `para/areas/`, and so on.
3. If the project's `CLAUDE.md` states a documentation-layout convention
   explicitly, that convention wins over the heuristic above.
4. Once the mode is determined, stay consistent within that project.

Throughout this document, `<base>/` denotes the resolved base — an empty prefix
in flat mode, or `para/` in nested mode. Every path below is written relative to
it.

**Scope of the connection layer (links · MOC · lint)**: the integrity linter
(`engram_lint.py`) auto-detects the base the same way as Path Resolution above —
**flat mode (standalone vault/brain) scans the whole root**, **nested mode (code
project + docs) scans under `para/`**. You can force it with `--base`. Contextual
link and MOC rules apply across the resolved `<base>/`.

Two usage modes:
- **Standalone document vault (brain)**: flat mode with `projects/`, `areas/`,
  etc. directly at the root. Lint base is the root.
- **Another project + document management**: nested mode with docs under `para/`
  inside a code repo. Lint base is `para/`.

## Quick Reference

| Category | Path | Purpose | Lifespan |
|----------|------|---------|----------|
| **Projects** | `<base>/projects/` | Active work with deadlines and goals | Temporary — archive on completion |
| **Areas** | `<base>/areas/` | Ongoing responsibilities without end date | Persistent — review periodically |
| **Resources** | `<base>/resources/` | Reference material and collected knowledge | Persistent — update as needed |
| **Archives** | `<base>/archives/` | Completed or inactive items from above | Permanent — read-only storage |

## Init Workflow

**When**: First PARA interaction OR the category folders are missing.
**Auto-execute without confirmation** — this operation is idempotent.

Resolve the base first (see Path Resolution), then run
[scripts/init.py](scripts/init.py):

```bash
# flat mode — categories created at the project root
python scripts/init.py --output . --flat

# nested mode — categories created under para/
python scripts/init.py --output .
```

Report what was created.

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
- `<base>/projects/website-redesign/requirements.md`
- `<base>/areas/team-onboarding.md`
- `<base>/resources/api-reference.md`
- `<base>/projects/website-redesign/2024-03-15-kickoff-notes.md`

### Step 4: Write Content

Use plain markdown. No frontmatter required. Start with an H1 title.

**Simple document template:**
```markdown
# [Title]

[Content starts here]
```

**Directory with multiple files:**
```
<base>/projects/website-redesign/
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

### Step 5: Connect (Networked Knowledge)

Right after creating a document, wire it into the network so it does not stay an
orphan. Follow [references/linking-rules.md](references/linking-rules.md).

1. **Secure an inbound link**: make the new document receive at least one link
   from a related existing document or that folder's `README.md` (MOC). Orphan
   nodes get lost.
2. **Contextual links**: weave `[[filename]]` wikilinks naturally into the prose.
   Do not dump a "related links" list at the bottom.
3. **Update the MOC**: add a one-line link to the new document in that folder's
   `README.md`.
4. **Ground references**: if it is a `resources/` document, also link it to an
   `areas/`/`projects/` document holding your interpretation, grounding it in the
   network.

### Step 6: Confirm and Report

After creation, report:
- Full path of the created file
- Which PARA category it was placed in
- Brief summary of what was created
- Which document/MOC now links to it (connection status)

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

## Migrate Workflow

**When**: bulk-reclassifying documents scattered across an existing project into
the PARA structure.

### Step 1: Scan

Discover all project documents with Glob.

- Targets: `**/*.md`, `**/*.txt`
- Exclude: documents already inside a PARA category (in flat mode the root's
  `projects/`·`areas/`·`resources/`·`archives/`, in nested mode `para/`), and
  non-document directories such as `.git/`, `node_modules/`
- Exclude root metadata files: `README.md`, `LICENSE`, `CHANGELOG.md`, etc.

See `references/migration-patterns.md` for detailed exclusion patterns.

### Step 2: Classify

Read each document's content and decide its PARA classification.

- Use the classification flowchart in `references/para-categories.md`
- Judge by filename/path hints and content keywords
- Mark uncertain documents as "manual classification needed"

See `references/migration-patterns.md` for detailed classification heuristics.

### Step 3: Present Migration Plan

Output the classification as a migration plan. Destination paths follow the
resolved base (flat-mode example shown).

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

If there are name collisions, state them in the plan.

### Step 4: Confirm

**Always execute only after user approval.** The user may change:

- the classification of individual files
- exclude specific files
- specify custom paths

### Step 5: Execute

Move files according to the approved plan.

1. Ensure the `<base>/` structure via the Init Workflow
2. Move files with Bash `mv`
3. Keep directory structure for related file groups (associated files in the same directory)
4. See `references/migration-patterns.md` for detailed directory handling

### Step 6: Report

Report the move results.

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

Use Grep to search document content across the PARA base.
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

## Link & Connect Workflow (Networked Knowledge)

**When**: the user wants to connect notes, tidy the knowledge network, link
orphan documents, or update MOCs. ("connect notes", "tidy the knowledge graph",
"update moc", "link the orphans")

First load [references/linking-rules.md](references/linking-rules.md).

1. **Assess**: run the Integrity Lint Workflow to get the list of orphans and
   broken links.
2. **Connect orphans**: read each orphan's content, find semantically related
   existing documents with Grep/Glob, and either **weave a contextual wikilink
   into that existing document's prose** or add a one-line link in the folder's
   `README.md` (MOC). Link only where there is real relevance, not forced links.
3. **Tidy MOCs**: check that each folder's `README.md` ties its documents
   together as an entry point, and fill in missing links.
4. **Re-check**: run the lint again to confirm orphans/broken links decreased,
   and report.

**Do not force connections.** Linking unrelated documents is over-structuring and
muddies the network's signal. If there is no related note, leave it as an orphan
and tell the user.

## Integrity Lint Workflow

**When**: the user wants to check link integrity, or find broken links/orphans.
Also call it as the closing check of other workflows (Create, Move, Migrate,
Review).

Detects broken links and orphan nodes under the PARA base (root if flat, `para/`
if nested). The base is auto-detected. Run
[scripts/engram_lint.py](scripts/engram_lint.py) from the target repo root.

```bash
# human report (silent if clean) — base auto-detected
python "<skill_dir>/scripts/engram_lint.py"

# machine JSON — the skill parses it for follow-up actions
python "<skill_dir>/scripts/engram_lint.py" --json

# force the base (e.g. root)
python "<skill_dir>/scripts/engram_lint.py" --base . --json
```

`<skill_dir>` is the directory holding this SKILL.md. When installed as a plugin,
call it as `${CLAUDE_PLUGIN_ROOT}/skills/engram/scripts/engram_lint.py`.

Handling results:
- **broken_md_links**: a non-existent path → fix it to the correct path, create
  the target document, or fix the typo.
- **orphans**: connect inbound links via the Link & Connect Workflow.
- **dangling_wikilinks**: warnings only. Fix typos; leave intended future notes
  as-is (deliberate forward links). You may ask the user whether to create them.

The exit code is always 0, so it never blocks work — report and fix together.

## Rules

1. **Auto-init**: If the category folders don't exist when any PARA operation is requested, create them automatically without asking. This is idempotent and safe.

2. **Never delete**: Documents are never deleted. Inactive items are moved to `archives/`. If the user explicitly asks to delete, warn them and suggest archiving instead. Only proceed with deletion after the user confirms twice.

3. **Hybrid structure**: Items can be either a single file (`topic.md`) or a directory with multiple files (`topic/*.md`). Choose based on expected deliverables.

4. **Naming convention**: All files and directories use `kebab-case`. Date prefixes (`YYYY-MM-DD-`) for time-sensitive documents. No spaces, no uppercase in filenames.

5. **Plain markdown**: No frontmatter, no special syntax. Documents are plain markdown files starting with an H1 heading. **Never use horizontal rules (`---`)** — YAML frontmatter parsers may misinterpret them as frontmatter block delimiters, causing parse errors.

6. **Archive confirmation**: Moving items to archives always requires explicit user confirmation. Never auto-archive. Present candidates and wait for approval.

7. **User language**: Respond in the user's language. Document content follows the user's preference. PARA category directory names are always in English.

8. **Relative paths**: When reporting paths to the user, use paths relative to the project root (e.g., `projects/my-doc.md` in flat mode, `para/projects/my-doc.md` in nested mode).

9. **Migration safety**: migration moves files, so always show the full migration plan first and execute only after user approval. Never auto-migrate.

10. **No orphans**: every newly created document must receive at least one inbound link (a related document or a MOC `README.md`). Unlinked knowledge gets lost.

11. **Contextual links**: weave links naturally into the prose. Do not dump a "related links" list at the bottom. Avoid forced connections (over-structuring); link only where there is real relevance.

12. **MOC as hub**: each folder's `README.md` is the entry point (MOC) for that folder's documents. When you add or move a document, update the relevant MOC too.

13. **Lint scope**: the integrity linter (`engram_lint.py`) auto-detects the base (root if flat, `para/` if nested). It is non-blocking (reports but never blocks work), and unresolved wikilinks are treated as warnings, not errors, since they may be intended future notes.
