# Brain Workspace — shared brains across repos

A repo-local `brain/` traps knowledge in one repo, so working across many repos
fragments it. A **workspace brain** is one external, independently git-versioned
brain that a *group* of repos share (e.g. everything under `d:/devel/github` → one
`personal` brain; all in-house GitLab repos → a `work` brain), so knowledge follows
you across repos. It is **engram-only** — nothing outside engram's path resolution
is affected.

## Model — a user-scope registry (like SSH host aliases)

A **user-scope registry** names the brains and records which repo uses which.
Managed by [scripts/workspace.py](../scripts/workspace.py) (installed plugin path:
`${CLAUDE_PLUGIN_ROOT}/skills/engram/scripts/workspace.py`):

```
<config_dir>/engram/config.json     # config_dir = $CLAUDE_CONFIG_DIR or ~/.claude
  {
    "version": 1,
    "brains": {                                       # the "host list"
      "personal": {"path": "D:/devel/github/brain", "autopush": true,
                   "remote": "origin", "branch": "main"},
      "work":     {"path": "D:/work/gitlab/brain", "autopush": false}
    },
    "assignments": {                                  # which repo uses what
      "D:/devel/github/myrepo": "personal",           # absorb: repo base = shared brain
      "D:/work/gitlab/svc":     "work",               # absorb (string form)
      "D:/work/gitlab/console": {"brain": "work",     # hybrid: local brain +
                                 "mode": "hybrid"}     #   shared cross-cutting link
    }
  }
```

An assignment value is either a **string** (`"<brain>"` = *absorb* mode, or
`"local"`) or an **object** `{"brain": "<name>", "mode": "hybrid"}` (= *hybrid*
mode). The string form is unchanged for back-compat.

- A brain's `path` is a **plain local directory that is already its own git repo**
  (engram never makes it a submodule; it just reads/writes files there and runs git
  in it) — the **container**. Its PARA **base** nests under `brain/` by default,
  resolved from the container exactly like a repo-local base: an existing
  `brain/`·`para/`·flat base wins, otherwise it defaults to `<path>/brain`. So even
  a repo dedicated as a brain keeps its PARA under `brain/` (not flat at the root);
  registering the `brain/` folder directly still resolves to itself.
- Assignments live in the **user-scope registry, not in the code repo**, so a shared
  code repo is never polluted with your machine-local brain path, and teammates who
  clone it never inherit a path that does not exist on their machine.
- Assignments are keyed by the **git repo root** (resolved with `git rev-parse`),
  so any subdirectory of a repo resolves to the same brain. Keys are matched
  case-insensitively (Windows-safe).

## Absorb vs hybrid — pick by what the repo's docs *are*

A repo shares a brain in one of two modes. Choosing wrong is the most common
workspace mistake.

| | **absorb** (`assign <brain>`) | **hybrid** (`assign <brain> --hybrid`) |
|---|---|---|
| Repo's base | the **shared** brain (no local brain) | the repo's **own local `brain/`** |
| Shared brain holds | *everything* this repo knows | only this repo's **cross-cutting** knowledge + index |
| `resolve` returns | `base` = shared | `base` = local, **`shared_base`** = shared |
| Fits | **knowledge-collection repo** (docs mostly cross-cutting product/domain knowledge — a test/research kit) | **product repo** (large code-coupled dev brain) |
| Autosync target | the shared brain (`base`) | the shared brain (`shared_base`); the local brain commits with the code |

**Why hybrid is the default for product repos (2026 industry pattern).** The
dominant, current practice is **"authored colocated, served/indexed centrally"** —
docs that are coupled to code stay in their repo and are reviewed with the code;
only genuinely cross-cutting knowledge plus an index are centralized. Convergent
evidence (verified, 2025–2026): Google SWE practices (docs as code, updated/deleted
in the same change); the **AGENTS.md** convention (nearest-file-wins, a file per
package — OpenAI's repo ships 88); **Backstage TechDocs**' recommended architecture
(source colocated per repo, artifacts aggregated centrally); the Backstage
**`AIContext` RFC** (centralize the *index/metadata/governance*, keep content
colocated via source annotations — still an open proposal, so emerging not settled);
**Anthropic context engineering** (just-in-time: store lightweight references, load
on demand — not one upfront central dump). Physically relocating a product repo's
whole dev brain into the shared brain runs *against* this pattern and hurts in-repo
agent ergonomics. Caveat: "single source of truth" does **not** mean zero
duplication (a common misread), so a hybrid still needs deliberate dedup when it
promotes cross-cutting docs.

### Routing — what goes where in hybrid

| Knowledge kind | Where | Why |
|----------------|-------|-----|
| Architecture, FE/BE dev & UX guides, page/nav maps, repo troubleshooting, repo project archives | **local `brain/`** | code-coupled — changes with the code, reviewed with it |
| Repo's compiled code-convention contract (`.code-convention/…`) | **local repo** (committed) | the applied instance; not brain content |
| Reusable product/domain knowledge several repos cite (protocols, error codes, KMS/DBMS ops) | **shared `resources/`** | cross-cutting, reused across repos (dedup on promote) |
| Stack-general convention **base** | **shared `resources/conventions/<stack>.md`** | engram curates; `code-convention` skill consumes |
| This repo's cross-repo index / pointers | **shared `projects/<repo>/`** | the repo's slot in the shared brain |

Separating cross-cutting from repo-specific is a **judgment call** — never
auto-relocate a repo's whole brain. Default to leaving a doc local unless it is
clearly reused across repos.

## Commands (natural language, any language)

| Intent | Example utterance | Action |
|--------|-------------------|--------|
| **Register** | "이 경로를 personal 브레인으로 등록해" / "register … as a brain" | `workspace.py register <path> [--name N] [--no-autopush] [--remote R] [--branch B]` |
| **Assign** (absorb) | "이 레포는 personal 써" / "use the work brain here" | `workspace.py assign <name>` |
| **Assign** (hybrid) | "이 레포는 로컬 브레인 두고 work는 공용지식만 공유" | `workspace.py assign <name> --hybrid` |
| **List** | "브레인 목록 / 워크스페이스 보여줘" | `workspace.py list [--json]` |
| **Switch** | "이 레포 work로 바꿔" | `workspace.py assign work` |
| **Unassign** | "이 레포 로컬로 되돌려" | `workspace.py assign local` (or `unassign`) |
| **Remove** | "work 브레인 등록 해제" | `workspace.py remove <name>` (leaves the directory untouched) |
| **Link** | "이 레포에 브레인 포인터 다시 박아줘" | `workspace.py link` (write/refresh) · `link --remove` (strip) |

Registering validates the path is a directory inside a git repo; if `autopush` is
on it also checks the remote exists, and disables autopush (with a warning) if not.
`remove` warns if any repo is still assigned to the brain being removed.

## Repo-side pointer — so an assigned repo advertises its brain

Assignments live only in the user-scope registry (so machine-local abs paths never
land in a shared code repo). The cost: a fresh agent session opening an assigned
repo has **no signal that a brain exists** — the durable knowledge sits in the brain
undiscovered until someone explicitly invokes engram. The pointer closes that gap.

`assign <brain>` writes a **portable, marker-delimited block** into the repo's
`CLAUDE.md` (which every session auto-loads):

```
<!-- BEGIN engram:brain-pointer (managed by engram …) -->
## Project knowledge lives in an engram brain
… brain name + git remote + in-brain subpath (projects/<repo>/) +
  "resolve the local checkout path via the engram skill" …
<!-- END engram:brain-pointer -->
```

- **Only portable facts are committed**: brain name, the brain repo's **git remote
  URL** (cross-machine identity), and the `projects/<repo>/` subpath. The
  machine-specific local checkout path is **never** written — it is resolved on
  demand via `workspace.py resolve` (the `base` field).
- **Idempotent**: the block is delimited by `BEGIN/END engram:brain-pointer`
  markers, so re-runs replace it in place (never duplicate). It coexists with any
  other CLAUDE.md content (appended once, updated thereafter).
- **Lifecycle**: `assign <brain>` writes/refreshes it; `assign local` and `unassign`
  strip it (deleting CLAUDE.md only if the block was its sole content). Re-apply
  anytime with `workspace.py link`; remove with `link --remove`; skip the auto-write
  with `assign --no-pointer`.
- **Relationship to Init**: Init wires the **brain side** (PARA folders at the
  resolved base); `link` wires the **repo side** (the discovery pointer). A complete
  "connect this repo to a shared brain" is `assign` (which now does both) → Init.

## Resolution (used by the skill, engram_lint.py, brain_reflect.py, brain_sync.py)

```bash
python "<skill_dir>/scripts/workspace.py" resolve --json
# -> {base, label, source, brain, mode, autopush, remote, branch,
#     shared_base, shared_brain, shared_remote, shared_branch, shared_autopush,
#     repo_root, warning}
```

`source` is one of:

- **`assignment`** (mode `absorb`) — this repo is assigned to a shared brain; `base`
  is that brain's PARA base — `brain/` nested in the registered directory (may be
  outside the repo), detected like a local base, defaulting to `<path>/brain`. Wins
  over local detection.
- **`hybrid`** (mode `hybrid`) — assigned with `--hybrid`. `base` is the repo's
  **local** brain (the linter lints this; it commits with the code), and the shared
  brain rides in **`shared_base`/`shared_brain`/`shared_remote`/`shared_branch`/
  `shared_autopush`**. brain_sync syncs the shared brain (never the local one).
  Route code-coupled docs → `base`, cross-cutting → `shared_base`.
- **`local`** — no assignment; a repo-local `brain/` · `para/` · flat base exists.
  A repo-local base still wins when there is no assignment (back-compat — existing
  vaults are never nagged).
- **`assignment-local`** — the repo is explicitly assigned to `"local"`.
- **`none`** — no assignment and no local base (typically a fresh code repo). The
  skill runs the **Workspace Picker**; the linter/hooks fall back to a silent
  `brain/` default so they never block.

Order overall: `--base` (linter flag) > `assignment`/`hybrid` > local detection > picker.

## Workspace Picker (Path Resolution rule 4)

When resolution returns `source: "none"`, **ask before creating anything**: list
`local` + every registered brain + "register a new path", let the user choose, then
persist (`workspace.py assign <choice>`, or `register` then `assign` for a new
path). Only then run the Init Workflow against the resolved base. Never silently
default a brand-new repo to a shared brain.

## Organizing a shared brain (two axes — don't fold both into folders)

When many repos share one brain, the urge is to add folder axes by repo and by
language. Resist it: PARA folders own **one** axis (actionability); "what the
knowledge is about" (repo · language · domain) is the **logical link layer** —
MOC hubs and contextual links, not more physical folders. A second/third folder
axis is over-structuring and kills cross-folder links (neural density).

| Knowledge kind | Where | How to group |
|----------------|-------|--------------|
| **Repo-specific active work** | `projects/<repo-name>/…` | One folder level is fine — projects are bound to a repo |
| **Language / domain reusable knowledge** (e.g. Go error patterns, React hook rules) | `resources/` | **Shallow.** `resources/go-error-handling.md` + a `go` MOC; avoid deep `resources/go/…` trees |
| **Repo-independent ongoing responsibility** | `areas/` | As usual — mixes across repos on purpose |

- **`projects/<repo>/` is the only place the repo axis becomes a folder** (active
  work is strongly repo-bound). `resources`/`areas` mix across repos by design —
  that cross-repo reuse is the whole point of a shared brain.
- **A dead repo does not mean dead knowledge.** Go patterns learned in a retired
  repo are still valid Go patterns — keep them in `resources/`. Conflating "repo
  deprecated" with "knowledge stale" is the most common classification error.

## Cleanup when a repo is deprecated

The shared brain accumulates from many repos, so retiring one needs a clean sweep
— but **structural, not statistical**: move that repo's whole `projects/<repo>/`
folder into `archives/<repo>/` in one Move (archives are read-only and already
excluded from orphan/density metrics, so the knowledge is set aside, not lost).
Leave its `resources`/`areas` contributions in place — they outlive the repo.
Requires confirmation like any archive move (never auto-archive). The periodic
**Review Workflow** surfaces stale candidates from git mtime + inbound-link count;
there is no access-frequency log (rarely-read reference material is exactly what
`resources/` is meant to preserve, so low read-count must never trigger cleanup).

## Brain autosync

[scripts/brain_sync.py](../scripts/brain_sync.py) is the muscle for keeping a
shared brain in sync. It acts **only** on the external **shared** brain a repo maps
to with `autopush: true` — the `base` in absorb mode, the `shared_base` in hybrid
mode — and **never** touches a repo-local `brain/` (a local brain, including a
hybrid repo's own `brain/`, is committed together with the code repo).

- **Commit on save (automatic)**: the `Stop` hook runs `brain_sync.py auto`, which
  commits the assigned brain if it changed (cheap, local, no-op when clean; no
  network, never blocks).
- **Push at wrap-up (model-supervised)**: pushing can conflict, so it is not
  silent — the capture-loop wrap-up instruction tells the model to run
  `brain_sync.py push`, which does `git pull --rebase` then `push` and **surfaces
  conflicts** (aborts the rebase and reports) instead of forcing.

Manual forms: `brain_sync.py commit [--repo P]`, `brain_sync.py push [--repo P]`,
`brain_sync.py status [--repo P] --json`. Autopush is per-brain opt-in (set at
register time, disabled automatically if the brain has no remote).
