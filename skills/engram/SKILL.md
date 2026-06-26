---
name: engram
description: >
  Networked PARA document brain — manages docs by PARA (Projects, Areas, Resources,
  Archives) AND weaves them into one connected knowledge graph via bi-directional
  links, MOC hubs, and integrity linting: a logical link layer over physical folders,
  so the vault grows like an interconnected brain. Also upgrades a legacy folders-only
  PARA vault (`para/`) into a networked `brain/`. Use to manage/organize/search docs,
  save meeting notes, archive or migrate a project, connect notes, find orphans, fix
  broken links, update MOCs, raise neural density, review what the brain gained this
  session, OR manage a brain WORKSPACE — a shared external brain several repos use in
  common (register/assign/switch brains, share knowledge across repos, autosync).
  Matches intent in any language — e.g. "문서 정리", "회의록 저장", "노트 연결", "링크 점검",
  "고아 문서", "MOC 업데이트", "브레인 리뷰", "세션 핸드오프", "다음 세션 이어가기", "브레인 워크스페이스",
  "공유 브레인", "organize docs", "connect notes", "find orphans", "session handoff",
  "para to brain", "shared brain workspace".
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
  orphans, weave lonely spokes into a woven mesh (not just a star of MOC links),
  catch broken links. Links own context. Load
  [references/linking-rules.md](references/linking-rules.md) for the detailed
  rules and follow them.

## Path Resolution (do this first)

Before any operation, resolve the **PARA base** — the location where the four
category folders live. This is the first step of every workflow.

**`brain/` is the default base for every repo** — both standalone document vaults
(brains) and code projects. The source brain lives under `brain/`; the repo root
holds meta files and any exported/published output, kept separate from the source.

A repo may instead be **assigned to a shared workspace brain** (an external brain
several repos share — see **Brain Workspace** below). Run the registry resolver
first — `python "<skill_dir>/scripts/workspace.py" resolve --json` → `{base, label,
source, …}` — then route on `source`:

1. `--base` given (linter) → use it.
2. **`assignment`** (absorb mode) → base = the registered shared brain's PARA base
   (the `brain/` nested inside it, may be **outside** this repo; existing
   `brain/`·`para/`·flat wins, else `<registered-path>/brain`). Wins over local. For
   **knowledge-collection repos** whose docs are mostly cross-cutting.
2b. **`hybrid`** → repo keeps its **own local `brain/`** for code-coupled docs AND
   links a shared brain. `resolve` returns two bases: `base` (repo-local, the linter
   lints this) and `shared_base` (shared). Route code-coupled docs → `base`,
   cross-cutting/reusable → `shared_base`. Default for **product repos**.
3. **`local` / `assignment-local`** → repo-local base: `brain/` if present (nested,
   default); else legacy `para/`; else PARA folders at root → **flat mode** (consider
   the **Upgrade Workflow**). A repo-local `brain/` always wins absent an assignment.
4. **`none`** (fresh repo, no assignment/local base) → run the **Workspace Picker**
   (Brain Workspace below) to assign a shared brain or keep `local`, then proceed.
5. An explicit `CLAUDE.md` doc-layout convention wins over the above.
6. Once determined, stay consistent within that project.

> **Legacy base (`para/` or flat root folders)?** A first-class case: engram *is* the
> upgrade path. "Complete migration to brain" migrates both the **base layout**
> (rename to `brain/`) and the **connection layer** (links/MOCs/lint) → **Upgrade
> Workflow** (a guarded refactor — the base name can be load-bearing in code/CI).

Throughout, `<base>/` denotes the resolved base — `brain/` nested, empty prefix in
flat mode. The linter auto-detects it the same way (force with `--base`).

## Brain Workspace (shared brains across repos)

A repo-local `brain/` traps knowledge in one repo. A **workspace brain** is one
external, independently git-versioned brain a *group* of repos share (e.g. all under
`d:/devel/github` → a `personal` brain; in-house GitLab → a `work` brain), so
knowledge follows you across repos. Engram-only. Like SSH host aliases, a
**user-scope registry** (`<config_dir>/engram/config.json`, managed by
[scripts/workspace.py](scripts/workspace.py)) names the brains and maps each repo (by
git root) to one — assignments live in the registry, **not in the code repo**.

Commands (natural language): **register** (`workspace.py register <path>
[--name N]`), **assign**/**switch** (`workspace.py assign <name>` · add `--hybrid`
for hybrid mode), **list**, **unassign** (`assign local`), **remove**
(`workspace.py remove <name>`). **Workspace Picker (rule 4)**: on `source: "none"`,
**confirm before creating anything — but lead with a recommended default, don't
open-endedly ask**: if the repo has code and a shared brain is registered, recommend
`assign <brain> --hybrid` (local brain for code-coupled docs + shared for
cross-cutting); for a pure doc vault recommend `local`; offer the other registered
brains + "register a new path" as alternatives. Persist (`assign`), then Init. Never
silently default a new repo to a shared brain — but never make the user invent the
mode either. Full schema/semantics: [references/workspace.md](references/workspace.md).

### Two ways a repo relates to a shared brain — absorb vs hybrid

"Share a brain" is two things; which fits depends on **what docs the repo holds**:

- **absorb** (`assign <brain>`) — the shared brain *is* the repo's base; no local
  brain. Right for a **knowledge-collection repo** whose docs are mostly cross-cutting
  (e.g. a test/research kit). Fully centralized.
- **hybrid** (`assign <brain> --hybrid`) — the repo **keeps its own local `brain/`**
  for code-coupled docs AND links the shared brain for **cross-cutting** knowledge
  (reusable knowledge, shared convention bases at `resources/conventions/`, the
  cross-repo index). `resolve` returns both `base` (local) and `shared_base`. Right
  for a **product repo** with a large code-coupled dev brain.

**Default a product repo to hybrid** (the 2026 "authored colocated, served/indexed
centrally" pattern — code-coupled docs reviewed with the code, only cross-cutting
knowledge + index centralized); **absorb a knowledge-collection repo.** When unsure,
prefer hybrid (reversible). Per-doc routing is autonomous via the **Routing decision
procedure**; only **wholesale-relocating a repo's entire brain** needs the user's
say-so. `assign` also writes an idempotent, portable **discovery pointer** into the
repo's `CLAUDE.md` (the repo-side counterpart to Init — `workspace.py link` re-applies
it, `--no-pointer` opts out). Full rationale, routing test, and pointer semantics:
[references/workspace.md](references/workspace.md).

## Migration: three operations, one word

"Migrate" is overloaded — it names **three independent operations**. Keep them
distinct (a request can want one, two, or all three); routing to the wrong one is
the most common failure.

| Operation | What it changes | Workflow |
|-----------|-----------------|----------|
| **Classify & Import** | scattered, *unclassified* docs → PARA folders | Classify & Import Workflow |
| **Base migration** | the base *layout/name* → `brain/` (`para/`→`brain/`, or flat→nested) | Upgrade Workflow, Phase A |
| **Connection-layer upgrade** | folders-only vault → *networked brain* (links/MOCs/lint) | Link & Connect Workflow (= Upgrade Workflow, Phase B) |

Route by the *current state of the vault*, not the user's word: docs unfiled →
**Classify & Import**; filed but base is `para/`/flat and user wants `brain/` →
**Upgrade** (Phase A+B); filed and based, only links missing → **Link & Connect**
(Upgrade Phase B alone).

## Brain boundary — what stays in the brain vs what separates

The brain (`<base>/`) holds **thinking and knowledge** — everything you link to and
revisit. Under PARA that includes active **planning / spec / strategy documents**:
they are Projects, the highest-value nodes (where knowledge gets applied). Keep them
in the brain — don't pull them out just because they look "output-like."

Separate a set of documents into a **root sibling folder** (next to `<base>/`, e.g.
`blog/`) only when it has its own **external delivery / publishing lifecycle** — a
workflow/repo/timeline outside your thinking network (e.g. a blog `seeds → drafts →
published`, or submission deliverables). Decision test: *Is this linked and re-read
as part of your thinking (→ brain), or an output with its own external lifecycle
(→ separate sibling)?*

- **Default to keeping documents in the brain.** Separation severs the
  project↔knowledge links that make Networked PARA valuable, so it must earn its
  place with a distinct-lifecycle justification (splitting without one is
  over-structuring).
- A separated sibling sits **outside the link network and the lint base**. It may
  reference brain docs one-directionally; the brain must not depend on it. When you
  separate, move the folder, fix cross-boundary links both ways, note it in the MOC.
- **Separation is the one move you do NOT decide on your own.** Make every other
  call autonomously, but externalize a document set only on explicit user request.

## Quick Reference

| Category | Path | Purpose | Lifespan |
|----------|------|---------|----------|
| **Projects** | `<base>/projects/` | Active work with deadlines and goals | Temporary — archive on completion |
| **Areas** | `<base>/areas/` | Ongoing responsibilities without end date | Persistent — review periodically |
| **Resources** | `<base>/resources/` | Reference material and collected knowledge | Persistent — update as needed |
| **Archives** | `<base>/archives/` | Completed or inactive items from above | Permanent — read-only storage |

**Organizing a shared brain**: PARA folders own one axis (actionability); the repo
axis is a folder **only** in `projects/<repo>/` — `resources`/`areas` mix across
repos by design, and language/domain knowledge stays shallow in `resources/` under a
MOC (not deep folders). Retiring a repo archives only its `projects/<repo>/`; its
reusable knowledge stays. Detail: [references/workspace.md](references/workspace.md).

**Shared code-convention bases — engram curates, `code-convention` consumes.** A
shared brain accumulates **stack-level convention bases** at
`resources/conventions/<stack>.md` — the cross-repo "AI-steering contract" for that
stack. engram **owns the base** (stores/curates them, keeps the
`resources/conventions/README.md` MOC, applies promotions `code-convention` hands up);
`code-convention` **consumes it** — each repo compiles `base + project deltas` into a
repo-local `.code-convention/CONVENTIONS.md` (the applied instance, *not* brain
content). Promote what's genuinely common per stack; never homogenize (adoption is
opt-in, specifics stay deltas). Detail: [references/workspace.md](references/workspace.md).

## Init Workflow

**When**: First PARA interaction OR the category folders are missing.
**Auto-execute without confirmation** — this operation is idempotent.

Resolve the base first (Path Resolution), run [scripts/init.py](scripts/init.py)
(`--output . --flat` for categories at the root, `--output .` for nested under
`brain/`), and report what was created.

## Create Workflow

**When**: User wants to create a new document or documentation item.

Six steps:
1. **Category** — Projects (deadline/goal), Areas (ongoing, no end date), or
   Resources (reference). If unsure, load `references/para-categories.md`.
2. **Structure** — a single `.md` for one topic, or a `kebab-case/` directory for
   multi-deliverable work.
3. **Filename** — `kebab-case.md`; date-prefix time-sensitive items
   (`YYYY-MM-DD-topic.md`).
4. **Write** — plain markdown, start with an H1, no frontmatter, no `---` rules.
5. **Connect** — secure at least one inbound link (a related doc or the folder's
   README MOC), weave contextual `[[wikilinks]]` into the prose, update the MOC,
   and ground a `resources/` doc to an `areas/`/`projects/` doc. Follow
   [references/linking-rules.md](references/linking-rules.md).
6. **Report** — path, PARA category, a brief summary, and what now links to it.

Templates (simple doc, directory tree, meeting notes) and full per-step detail:
[references/create-workflow.md](references/create-workflow.md).

## Move Workflow

**When**: User wants to relocate a document between PARA categories.

Common moves: `projects/`→`archives/` (completed), `areas/`→`archives/` (ended),
`resources/`→`archives/` (outdated), `archives/`→`projects/` (reactivated).

Steps: Glob the source → determine the target category (ask or infer) → verify the
target path is free → `mv` → report `source → destination`.

**IMPORTANT: Never delete documents. Always move to archives instead.**

## Classify & Import Workflow

**When**: bulk-reclassifying documents **scattered outside** the PARA structure
into it — the *classification* sense of migration (one of three; see "Migration:
three operations, one word"). For renaming the base to `brain/` or wiring up links,
use the **Upgrade Workflow** / **Link & Connect Workflow** instead.

> **First check: are the docs already PARA-classified?** If they already live in
> `projects/`·`areas/`·`resources/`·`archives/`, there is nothing to classify — do
> NOT run scan→classify→move. What's actually missing is one of the *other* two
> migrations. Route by what the user wants:
> - the `brain/` layout (from `para/` or flat) → **Upgrade Workflow** (Phase A base
>   rename + Phase B connection layer; this is the "complete migration to brain").
> - links/MOCs only, base is fine → **Link & Connect Workflow** (build per-folder
>   README MOCs first — the highest-leverage orphan fix — then contextual links).
>
> Use this Classify & Import flow only when documents are genuinely unfiled.

Six steps: **1. Scan** (Glob for `**/*.md`·`**/*.txt`, excluding existing PARA
folders, `.git/`/`node_modules/`, and root metadata) → **2. Classify** (read each
doc, assign a PARA category via `references/para-categories.md`, flag the unclear)
→ **3. Present a migration plan** (a Classified/Manual/Skipped table; name the
collisions) → **4. Confirm** (execute only after approval; the user may reclassify,
exclude, or repath) → **5. Execute** (init the base, `mv` files, keep related groups
together) → **6. Report** the moves, then close with the Integrity Lint.

Full step detail, plan/report templates, exclusion and classification heuristics,
directory handling, and conflict rules: `references/migration-patterns.md`.

## Upgrade Workflow — legacy para-docs vault → engram brain

**When**: a repo is a legacy vault — a non-`brain/` nested base (`para/`) or flat
PARA folders at the root — and the user wants to bring it up to the engram brain
model. This is engram's signature migration-support path: the upgrade from
folders-only para-docs to a networked brain. It has **two independent phases**;
"full / complete migration to brain" runs **both**, a lighter "just connect it"
runs only Phase B.

**Decide scope first** (ask if unstated): **full** (A + B) vs **connection-only**
(B). Default the legacy-base case to **full** unless the user opts out — engram's
whole point is the `brain/` model — but never auto-execute Phase A (it touches code;
see Migration safety).

- **Phase A — Base migration**: a **guarded refactor, not a bare `git mv`** (the base
  name can be load-bearing in code import paths / CI). Grep the whole repo for the old
  base name, `git mv` to preserve history, update every non-doc reference, fix links,
  then scope→approve→execute.
- **Phase B — Connection-layer upgrade**: the real value-add — run the **Link &
  Connect Workflow** (per-folder README MOCs first, then contextual links, then
  re-lint).
- **Verify & report** both phases.

Full Phase A step detail (grep targets, the code-import-path smell, `git mv` recipes,
approval gate): [references/migration-patterns.md](references/migration-patterns.md).

## List & Search Workflow

**When**: User wants to see what documents exist or find specific content.

- **List (Dashboard)**: a markdown summary table per non-empty PARA category — rows
  grouped under `### <Category> (N items)`, columns `Name | Type | Last Modified`
  (Glob to discover, `git log`/file stats for dates).
- **Search**: Grep for content, Glob for filename patterns; report paths + matching
  context.

## Review Workflow

**When**: User requests a documentation review or periodic checkup. Load
`references/review-checklist.md` for the detailed procedure and report format.

Generate the PARA Dashboard, then per item flag archival candidates (projects
completed/stale >30 days, areas/resources outdated), present the findings, and
**suggest** archives — **never auto-archive**; execute moves only after confirmation.

Use the Review Report Format in `references/review-checklist.md` for the output.

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
and tell the user. When orphans are already zero but the graph is a **star** (every
doc hangs off its MOC), the next move is the **Weave Workflow** below, not more MOCs.

## Weave Workflow (raise neural density)

**When**: orphans are handled but the brain is a star, not a mesh (low
`woven_ratio`, many `weak_nodes`) — the user wants it "more connected / more
neural". The deepening counterpart to Link & Connect: that removes orphans (≥1
inbound); this removes *lonely spokes* (earns a contextual, cross-folder inbound).

Run `scripts/weave_candidates.py --json` for two advisory candidate lists —
**missing_links** (a doc already names another note but doesn't link it; the
cheapest spoke-dissolver, spokes ranked first) and **concept_candidates** (a term
recurring across folders with no node; promote to a shared concept note). Judge
which are *real*, weave them contextually where the mention sits (don't force —
over-structuring is the failure here), then re-run `engram_lint.py --json` to
confirm `woven_ratio`/`weak_nodes` improved. Full procedure + the brain-boundary
caveat: [references/weave-workflow.md](references/weave-workflow.md).

## Integrity Lint Workflow

**When**: the user wants to check link integrity, or find broken links/orphans.
Also call it as the closing check of other workflows (Create, Move, Classify &
Import, Upgrade, Review).

Detects broken links and orphan nodes under the PARA base (auto-detected). Run
[scripts/engram_lint.py](scripts/engram_lint.py) from the target repo root — no args
for a human report (silent if clean), `--json` for the machine output the skill parses,
`--base .` to force the base (e.g. root).

```bash
python "<skill_dir>/scripts/engram_lint.py" --json
```

`<skill_dir>` is the directory holding this SKILL.md. When installed as a plugin,
call it as `${CLAUDE_PLUGIN_ROOT}/skills/engram/scripts/engram_lint.py`.

Handling results:
- **broken_md_links**: a non-existent path → fix it to the correct path, or create
  the target document, or fix the typo. If the target is **permanently gone** (a
  deleted historical reference in an archive, or a link to source code that no
  longer exists), **de-link it** — convert `[text](dead/path.md)` to a plain code
  span `` `text` `` so the textual reference survives without a broken link. Don't
  turn it into a `[[wikilink]]`: that falsely implies an intended future note.
- **orphans**: connect inbound links via the Link & Connect Workflow. The fastest
  fix is structural — orphans cluster by folder, so one **per-folder README MOC**
  that links every doc in its folder clears the whole folder at once; build MOCs
  before hunting individual contextual links. **Gotcha:** if a folder already has a
  README full of `` `filename.md` `` in backticks and its docs are still orphans,
  that's why — code spans aren't links; rewrite them as `[filename.md](filename.md)`.
- **weak_nodes** + **metrics** (`woven_ratio`, `cross_folder_link_ratio`, …):
  advisory, never blocking. Weak nodes are lonely spokes (only a MOC inbound) — a
  star, not a brain. Don't fix them with more MOC links (that deepens the star);
  route to the **Weave Workflow**. Low `woven_ratio` with orphans=0 = a pristine
  star that needs weaving, not more foldering.
- **dangling_wikilinks**: warnings only. Fix typos; leave intended future notes
  as-is (deliberate forward links). You may ask the user whether to create them.

The exit code is always 0, so it never blocks work — report and fix together.

## Capture loop — keep the brain fed

Durable thinking that stays in the chat and never lands in `<base>/` is lost. Keep
the brain fed; the bundled hooks are triggers/backstops, **not** the engine — judging
what's worth keeping is the model's job. Three triggers:

1. **Capture-as-you-go (primary)**: record a durable concept/decision/gotcha *when it
   crystallizes* via the Create Workflow — don't wait for session end. Stay selective.
2. **Wrap-up** (`UserPromptSubmit` hook): a sign-off ("수고했어", "wrap up", …) injects
   a reflect-and-save instruction; act on it before replying.
3. **Backstop** (`Stop` hook): a throttled nudge (default 30 min) for long sessions
   with no sign-off; if nothing's worth keeping, say so in one line — no filler.

Hooks ship with the plugin (brain-only, non-blocking). Tune
`ENGRAM_CAPTURE_COOLDOWN_MIN` / `ENGRAM_CAPTURE_PHRASES`, disable with
`ENGRAM_CAPTURE_DISABLE=1`. Details: [references/capture-loop.md](references/capture-loop.md).

**Brain autosync** (shared workspace brains only):
[scripts/brain_sync.py](scripts/brain_sync.py) acts **only** on an external
**assigned** brain with `autopush: true`, never on a repo-local `brain/`. The `Stop`
hook commits-on-save (`brain_sync.py auto`); at wrap-up the capture instruction runs
`brain_sync.py push` (`pull --rebase` then `push`, surfacing conflicts not forcing).

## Session Update Review Workflow

**When**: the user asks to see what the brain gained *this session* — a wrap-up
recap of new/changed notes. Command-triggered (not a hook); the read-back
counterpart to the Capture loop. ("이번 세션 브레인 업데이트 리뷰", "엔그램 세션
리뷰", "브레인 업데이트 알려줘", "review brain updates", "engram session review")

Load [references/session-review.md](references/session-review.md) for the full
procedure. In short: reconcile your **session memory** (notes/links/MOCs touched)
with a **git cross-check** (`git status --short`/`git diff --stat -- <base>/`), run
the Integrity Lint as the closing check, then present the report. If nothing landed,
say so in one line.

## Session Handoff Workflow

**When**: mid-session, the context window is filling up (~half+) and the user wants
to continue the *same* work in a fresh session without losing state — the **forward**
counterpart to the Capture loop and Session Update Review (which look *back*).
Command/natural-language triggered, **never a hook**. ("다음 세션에 이어가게 준비해",
"세션 핸드오프", "다음 세션 이어가기 준비", "prepare handoff", "continue in next session")

Produce **two artifacts, the second subordinate to the first**:

1. **The handoff doc (carries the weight)** — a single **rolling** doc at
   `.handoff/handoff.md`, a project scratchpad at the **repo root, outside the
   brain** (git-ignored throwaway working state — add `.handoff/` to `.gitignore`
   if absent). One per work-stream, **overwritten every time**, never date-stamped
   or accumulated: a living state board, not a log. Sections: `## Goal` · `## Done`
   · `## Current state` · `## Next steps` (the resume point — most important) ·
   `## Key files & decisions` (weave `[[wikilinks]]` to related brain notes here) ·
   `## Open questions`. No MOC link — outside the brain, the orphan rule doesn't apply.
2. **The continuation prompt (a thin pointer)** — a short copy-able code block that
   **points at the handoff doc; it does not inline the context** (a dump throws away
   engram's wikilink-network value). Emit it in the user's language, then stamp a
   snapshot warning (a prompt kept-working-past becomes a lie):
   ```
   .handoff/handoff.md 읽고, "## Next steps" 부터 이어서 작업해.
   ```

`.handoff/handoff.md` is *working state*, kept **outside** the brain (git-ignored)
so it never pollutes the knowledge base. When the work-stream finishes, distill
durable bits via the **Capture loop**, then empty it. Full procedure:
[session-handoff.md](references/session-handoff.md).

## Roadmap (planned, not yet implemented)

A **Publish / Export** workflow: extract a curated, portable subset from the brain
(opt-in by frontmatter/tag/MOC) into a separate artifact (`dist/`, a single file,
or a static site), resolving wikilinks and stripping private/unpublished notes —
the source brain stays visible and untouched. Design details in
[references/roadmap.md](references/roadmap.md). If the user asks to "publish",
"export the brain", or "build a doc bundle", follow that design.

## Continuous self-improvement (loop engineering)

This skill is meant to get better through use. During any engram operation, stay
alert for a concrete improvement (cleaner method, fewer tokens, clearer rules, a
missing workflow) and act on it in the same loop: **apply it** (small, reversible
edits to `skills/engram/…`), **sync it** (push, then `claude plugin marketplace
update <marketplace>` + `claude plugin update <plugin>@<marketplace> --scope
<scope>`, restart to activate), **record it** (one line in the commit message). If
you lack write/sync access, don't silently skip — tell the user what you'd change,
why, and ask. Target the **how** (efficiency, clarity, robustness), never the
**contract** (the `brain/` model, link semantics, folder governance) without the
user's say-so.

## Rules

1. **Auto-init**: If the category folders don't exist when any PARA operation is requested, create them automatically without asking. This is idempotent and safe.

2. **Never delete**: Documents are never deleted. Inactive items are moved to `archives/`. If the user explicitly asks to delete, warn them and suggest archiving instead. Only proceed with deletion after the user confirms twice.

3. **Hybrid structure**: Items can be either a single file (`topic.md`) or a directory with multiple files (`topic/*.md`). Choose based on expected deliverables.

4. **Naming convention**: All files and directories use `kebab-case`. Date prefixes (`YYYY-MM-DD-`) for time-sensitive documents. No spaces, no uppercase in filenames.

5. **Plain markdown**: No frontmatter, no special syntax. Documents are plain markdown files starting with an H1 heading. **Never use horizontal rules (`---`)** — YAML frontmatter parsers may misinterpret them as frontmatter block delimiters, causing parse errors.

6. **Archive confirmation**: Moving items to archives always requires explicit user confirmation. Never auto-archive. Present candidates and wait for approval.

7. **User language**: Respond in the user's language. Document content follows the user's preference. PARA category directory names are always in English.

8. **Relative paths**: When reporting paths to the user, use paths relative to the project root (e.g., `projects/my-doc.md` in flat mode, `brain/projects/my-doc.md` in nested mode).

9. **Migration safety**: any operation that moves files or renames the base (Classify & Import, and the Upgrade Workflow's Phase A) — always show the full plan first and execute only after user approval. Never auto-migrate. A base rename also touches **non-doc references** (code import paths, CI/build scripts), so include those in the plan, not just the file moves.

10. **No orphans**: every newly created document must receive at least one inbound link (a related document or a MOC `README.md`). Unlinked knowledge gets lost.

11. **Contextual links**: weave links naturally into the prose. Do not dump a "related links" list at the bottom. Avoid forced connections (over-structuring); link only where there is real relevance.

12. **MOC as hub**: each folder's `README.md` is the entry point (MOC) for that folder's documents. When you add or move a document, update the relevant MOC too.

13. **Lint scope**: the integrity linter (`engram_lint.py`) auto-detects the base (root if flat, `brain/` — or a legacy `para/` — if nested). It is non-blocking (reports but never blocks work), and unresolved wikilinks are treated as warnings, not errors, since they may be intended future notes.
