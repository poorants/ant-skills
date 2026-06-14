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

**`brain/` is the default base for every repo** — both standalone document vaults
(brains) and code projects. The source brain lives under `brain/`; the repo root
holds meta files and any exported/published output, kept separate from the source.

1. If `brain/` exists → **nested mode**, base = `brain/`. (Default / recommended.)
2. Else if a legacy `para/` exists → nested mode, base = `para/` (back-compat).
3. Else if the root already contains `projects/`, `areas/`, `resources/`, or
   `archives/` → **flat mode** (legacy standalone vault), base = the root.
   Consider migrating it under `brain/` for the unified layout.
4. Else (fresh repo) → nested mode, base = `brain/` (create it).
5. If the project's `CLAUDE.md` states a documentation-layout convention
   explicitly, that convention wins over the heuristic above.
6. Once the mode is determined, stay consistent within that project.

Throughout this document, `<base>/` denotes the resolved base — `brain/` in the
default nested mode, or an empty prefix in legacy flat mode. Every path below is
written relative to it.

**Scope of the connection layer (links · MOC · lint)**: the integrity linter
(`engram_lint.py`) auto-detects the base the same way as Path Resolution above —
**nested mode scans under `brain/`** (or a legacy `para/`); **legacy flat mode
scans the whole root**. You can force it with `--base`. Contextual link and MOC
rules apply across the resolved `<base>/`.

Two usage shapes (both default to `brain/`):
- **Standalone document vault (brain)**: a doc-only repo. Docs under `brain/`;
  the root holds meta + exports.
- **Another project + document management**: docs under `brain/` inside a code
  repo, alongside the source code.

Legacy flat repos (PARA folders directly at the root) are still detected for
back-compat, but new repos use `brain/`.

## Brain boundary — what stays in the brain vs what separates

The brain (`<base>/`) holds **thinking and knowledge** — everything you link to
and revisit. Under PARA that includes active **planning / spec / strategy
documents**: they are Projects, and they are the highest-value nodes because they
are where your knowledge gets applied. Keep them in the brain — do not pull them
out just because they look "output-like."

Separate a set of documents into a **root sibling folder** (next to `<base>/`,
e.g. `blog/`) only when it has its own **external delivery / publishing
lifecycle** — a workflow, repo, or timeline that lives outside your thinking
network. Examples: a blog (`seeds → drafts → published → static site / social`),
or submission deliverables (resumes/portfolios sent to companies).

Decision test (one line): *Is this linked and re-read as part of your thinking
(→ brain), or an output with its own external workflow/lifecycle (→ separate
sibling)?*

- **Default to keeping documents in the brain.** Separation severs the
  project↔knowledge links that make Networked PARA valuable, so it must earn its
  place with a distinct-lifecycle justification; splitting without one is
  over-structuring.
- A separated sibling sits **outside the link network and the lint base**. It may
  reference brain documents one-directionally; the brain must not depend on it.
  When you separate, move the folder, fix cross-boundary links both ways, and
  note it in the relevant MOC/rules.
- **Separation is the one move you do NOT decide on your own.** Make every other
  organizational call autonomously, but externalize a document set only on an
  explicit user request (e.g. "move the blog out").

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

# nested mode — categories created under brain/ (or a legacy para/ if present)
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
  `projects/`·`areas/`·`resources/`·`archives/`, in nested mode `brain/` or `para/`), and
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

## Unify a Legacy Flat Vault into brain/

**When**: a repo has PARA folders directly at the root (legacy flat) and the user
wants the unified layout (source under `brain/`, root for meta + exports).

1. **Move the folders** with `git mv` to preserve history:
   `git mv projects brain/projects` (and `areas`, `resources`, `archives`). Only
   move folders that exist/are tracked; create `brain/archives/.gitkeep` if empty.
2. **Relative links are mostly preserved** — links between docs that move together
   keep resolving (the relative structure is intact). `[[wikilinks]]` resolve by
   filename, so they survive regardless.
3. **Catch breakage with the linter**: run `engram_lint.py --json` (it now detects
   base `brain/`) and fix every `broken_md_links` entry — these are links that
   crossed the moved/not-moved boundary (e.g. into root-level files).
4. **Update references**: in `CLAUDE.md` change the doc-layout note to nested
   `brain/`; fix any path references in config/memory that pointed at the old
   root paths.
5. **Verify**: re-run the linter; report what moved and what was fixed.

This is a `git mv` move, so it is reversible — but still show the plan and get
user approval first (Migration safety rule).

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

Detects broken links and orphan nodes under the PARA base (root if flat, `brain/`
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

## Capture loop — keep the brain fed

Durable thinking that stays in the chat and never lands in `<base>/` is lost. Keep
the brain fed continuously; the bundled hooks are triggers/backstops, **not** the
engine — judging what is worth keeping is the model's job.

1. **Capture-as-you-go (primary)**: when a durable concept / decision / good idea
   / research conclusion / important gotcha crystallizes mid-work, record it
   *then* via the Create Workflow (place, link, update MOC) — don't wait for
   session end. Stay selective (Brain boundary + no over-structuring).
2. **Wrap-up trigger** (`UserPromptSubmit` hook): on an end-of-session sign-off
   ("고생했다", "수고했어", "wrap up", …) the hook injects a reflect-and-save
   instruction so the final ideas are captured. Act on it before replying.
3. **Backstop** (`Stop` hook): a throttled nudge (default 30 min) for long
   sessions with no sign-off; if nothing is worth keeping, say so in one line —
   never create filler.

Hooks ship with the plugin (`hooks/hooks.json` → `brain_reflect.py`, beside the
integrity-lint Stop hook); brain-only and non-blocking. Tune
`ENGRAM_CAPTURE_COOLDOWN_MIN` / `ENGRAM_CAPTURE_PHRASES`, disable with
`ENGRAM_CAPTURE_DISABLE=1`. Details: [references/capture-loop.md](references/capture-loop.md).

## Roadmap (planned, not yet implemented)

A **Publish / Export** workflow: extract a curated, portable subset from the brain
(opt-in by frontmatter/tag/MOC) into a separate artifact (`dist/`, a single file,
or a static site), resolving wikilinks and stripping private/unpublished notes —
the source brain stays visible and untouched. Design details in
[references/roadmap.md](references/roadmap.md). If the user asks to "publish",
"export the brain", or "build a doc bundle", follow that design.

## Continuous self-improvement (loop engineering)

This skill is meant to get better through use. During any engram operation, stay
alert for a concrete way to improve the skill itself — a cleaner method, fewer
tokens, faster execution, clearer rules, or a missing workflow. When you spot one,
act on it in the same loop rather than deferring:

1. **Apply it** — edit the skill source (`skills/engram/…`), keeping the change
   small, focused, and reversible (it is under git). Prefer many small verified
   edits over large rewrites.
2. **Sync it** so the running copy reflects the change: push, then
   `claude plugin marketplace update <marketplace>` and
   `claude plugin update <plugin>@<marketplace> --scope <scope>` (a Claude Code
   restart activates it).
3. **Record it** — a one-line note in the commit message (and any changelog or
   memory that tracks skill versions).

If you lack permission to write to the skill source or to run the sync, **do not
silently skip the improvement** — tell the user exactly what you want to change
and why, and ask for access: e.g. "I want to update engram to <X> for a
<token/speed/clarity> gain but don't have write access to <path> — may I?"

Self-improvement targets the **how** (efficiency, clarity, robustness), not the
**contract**: do not change externally observable behavior (the `brain/` model,
link semantics, folder governance) without the user's say-so.

## Rules

1. **Auto-init**: If the category folders don't exist when any PARA operation is requested, create them automatically without asking. This is idempotent and safe.

2. **Never delete**: Documents are never deleted. Inactive items are moved to `archives/`. If the user explicitly asks to delete, warn them and suggest archiving instead. Only proceed with deletion after the user confirms twice.

3. **Hybrid structure**: Items can be either a single file (`topic.md`) or a directory with multiple files (`topic/*.md`). Choose based on expected deliverables.

4. **Naming convention**: All files and directories use `kebab-case`. Date prefixes (`YYYY-MM-DD-`) for time-sensitive documents. No spaces, no uppercase in filenames.

5. **Plain markdown**: No frontmatter, no special syntax. Documents are plain markdown files starting with an H1 heading. **Never use horizontal rules (`---`)** — YAML frontmatter parsers may misinterpret them as frontmatter block delimiters, causing parse errors.

6. **Archive confirmation**: Moving items to archives always requires explicit user confirmation. Never auto-archive. Present candidates and wait for approval.

7. **User language**: Respond in the user's language. Document content follows the user's preference. PARA category directory names are always in English.

8. **Relative paths**: When reporting paths to the user, use paths relative to the project root (e.g., `projects/my-doc.md` in flat mode, `brain/projects/my-doc.md` in nested mode).

9. **Migration safety**: migration moves files, so always show the full migration plan first and execute only after user approval. Never auto-migrate.

10. **No orphans**: every newly created document must receive at least one inbound link (a related document or a MOC `README.md`). Unlinked knowledge gets lost.

11. **Contextual links**: weave links naturally into the prose. Do not dump a "related links" list at the bottom. Avoid forced connections (over-structuring); link only where there is real relevance.

12. **MOC as hub**: each folder's `README.md` is the entry point (MOC) for that folder's documents. When you add or move a document, update the relevant MOC too.

13. **Lint scope**: the integrity linter (`engram_lint.py`) auto-detects the base (root if flat, `brain/` — or a legacy `para/` — if nested). It is non-blocking (reports but never blocks work), and unresolved wikilinks are treated as warnings, not errors, since they may be intended future notes.
