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
      "D:/devel/github/myrepo": "personal",           # repo-root-abs -> brain | "local"
      "D:/work/gitlab/svc":     "work"
    }
  }
```

- A brain's `path` is a **plain local directory that is already its own git repo**
  (engram never makes it a submodule; it just reads/writes files there and runs git
  in it). It may be the repo root or a nested `brain/` inside that repo.
- Assignments live in the **user-scope registry, not in the code repo**, so a shared
  code repo is never polluted with your machine-local brain path, and teammates who
  clone it never inherit a path that does not exist on their machine.
- Assignments are keyed by the **git repo root** (resolved with `git rev-parse`),
  so any subdirectory of a repo resolves to the same brain. Keys are matched
  case-insensitively (Windows-safe).

## Commands (natural language, any language)

| Intent | Example utterance | Action |
|--------|-------------------|--------|
| **Register** | "이 경로를 personal 브레인으로 등록해" / "register … as a brain" | `workspace.py register <path> [--name N] [--no-autopush] [--remote R] [--branch B]` |
| **Assign** | "이 레포는 personal 써" / "use the work brain here" | `workspace.py assign <name>` |
| **List** | "브레인 목록 / 워크스페이스 보여줘" | `workspace.py list [--json]` |
| **Switch** | "이 레포 work로 바꿔" | `workspace.py assign work` |
| **Unassign** | "이 레포 로컬로 되돌려" | `workspace.py assign local` (or `unassign`) |
| **Remove** | "work 브레인 등록 해제" | `workspace.py remove <name>` (leaves the directory untouched) |

Registering validates the path is a directory inside a git repo; if `autopush` is
on it also checks the remote exists, and disables autopush (with a warning) if not.
`remove` warns if any repo is still assigned to the brain being removed.

## Resolution (used by the skill, engram_lint.py, brain_reflect.py, brain_sync.py)

```bash
python "<skill_dir>/scripts/workspace.py" resolve --json
# -> {base, label, source, brain, autopush, remote, branch, repo_root, warning}
```

`source` is one of:

- **`assignment`** — this repo is assigned to a shared brain; `base` is that brain's
  path (may be outside the repo). Wins over local detection.
- **`local`** — no assignment; a repo-local `brain/` · `para/` · flat base exists.
  A repo-local base still wins when there is no assignment (back-compat — existing
  vaults are never nagged).
- **`assignment-local`** — the repo is explicitly assigned to `"local"`.
- **`none`** — no assignment and no local base (typically a fresh code repo). The
  skill runs the **Workspace Picker**; the linter/hooks fall back to a silent
  `brain/` default so they never block.

Order overall: `--base` (linter flag) > `assignment` > local detection > picker.

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
shared brain in sync. It acts **only** on a repo whose resolved brain is an
external **assigned** brain with `autopush: true`, and **never** touches a
repo-local `brain/` (a local brain is committed together with the code repo).

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
