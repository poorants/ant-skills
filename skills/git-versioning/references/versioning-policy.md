# Versioning Policy (git-versioning)

> This document is the **policy template** that the `git-versioning` skill copies into a project as
> `docs/versioning.md` (or a path you specify) during `init`. Replace the `{PROJECT}` placeholder with your project name.

This describes how {PROJECT} assigns version numbers.

> **Approach**: **structure-based (git commit graph) `MAJOR.MINOR.PATCH`**, computed from the local git repo at build time —
> **no tags, no CI, no tokens required**. MINOR is the number of merges (MR/PR), PATCH is the number of direct commits to main
> since the last merge, and MAJOR is a human-chosen milestone. The version number is a **monotonically increasing
> build identifier** that points to "where in git this build sits."

## 0. Why this approach instead of the standard (semantic-release) — a record of a deliberate departure

The most orthodox and widely adopted standard is usually **Conventional Commits + semantic-release** (deriving SemVer
automatically from commit-message types). This policy **deliberately sets that standard aside**, and records why. (If you are
building an externally published library, the standard is the right choice — read the adoption criteria in §5 first before deciding.)

1. **Product nature** — this is an **internal product** shipped on-demand to known customers/QA. The core value of a SemVer
   number — a "compatibility contract for external consumers" (major = breaking, etc.) — has no external consumers to read it.
2. **What's actually needed is build identification** — during development we hand multiple builds to QA. QA needs to tell at a
   glance, from the number alone, **"is the one I just got newer, and which build is it?"** → the number must **increase
   monotonically with every commit**.
3. **CI-free, token-free local determinism** — internal and QA builds do not pull tags (tags only happen on actual shipments).
   semantic-release assumes a CI runner + a token + a tag created on every merge; without a token the version **freezes** at the
   last tag, and accumulating a tag per merge clashes with the on-demand shipping model.
4. **Accepting the trade-off** — this approach **cannot tell you compatibility/breaking status from the number**, and you don't
   get a CHANGELOG or release notes for free (§5). We judged the gains in points 1–3 to outweigh those losses.

## 1. The rule — git structure decides the version

`scripts/version.sh` computes it from git at build time:

```
MR_TOTAL  = git rev-list --merges --count HEAD      # merges reachable from HEAD (= MR/PR count)
minor_raw = MR_TOTAL - MR_BASE                       # merges within the current major
MAJOR     = MAJOR_BASE + minor_raw / 1000000         # usually a human-set value (+ overflow carry)
MINOR     = minor_raw % 1000000                      # 0 ~ 999999
PATCH     = git rev-list --count --first-parent <last-merge>..HEAD   # direct main commits since the last merge
```

| Field | What it counts | When it increments |
|------|------------|------------|
| **MAJOR** | Human-chosen milestone | Bumped manually by a human in `version.conf` (rare). Auto-carries when MINOR exceeds 999999 (effectively never). |
| **MINOR** | Number of merges (MR/PR) | **+1 every time a merge lands on main**, resetting PATCH to 0. |
| **PATCH** | Number of direct commits to main | **+1 for every direct commit to main (a hotfix that bypasses a merge).** 0 immediately after a merge. |

- Build versions have **no `v` prefix** (`0.20.2`). Only actual release **tags** use `vX.Y.Z` (§3).
- If you route all work through merges: `0.20.0 → 0.21.0 → 0.22.0` (MINOR only increases, PATCH stays 0). PATCH only rises when
  you commit directly to main.
- Deterministic: the version is a **pure function of the commit + `version.conf`**. The same commit always yields the same version
  (aside from `+dev`/`-dirty`).

> **Enforcement — the forge must create a merge commit per MR/PR.** MINOR counts merge commits, so the scheme assumes every
> MR/PR merge produces one. **Fast-forward** merges (when main has not moved since the branch was cut) and **squash** merges both
> skip the merge commit, so that work counts toward PATCH instead and MINOR undercounts. Enforce this **at the forge, not with a
> git hook** — the merge runs on the forge server (local hooks never run there), a fast-forward creates no commit (so no hook event
> fires), and locally an ff-absorbed MR is indistinguishable from an intentional direct PATCH commit ("this was an MR" is knowledge
> only the forge holds). Set **GitLab** merge method to **"Merge commit"** (`merge_method=merge`, not "Fast-forward merge"), or on
> **GitHub** keep only "Allow merge commits" (disable squash & rebase merging). Without forge-admin access, the fallback is a CI
> *detective* check (recompute the version and assert it rose) — it catches an undercount but cannot prevent it. Under GitLab's
> default (merge commits created) it works as-is.

## 2. Where the version lives

- **`scripts/version.sh`** — the computation logic (single source of truth). Invoked by the build system.
- **`version.conf`** (repo root) — the baselines `MAJOR_BASE` / `MR_BASE` (`0` / `0` during 0.x).
- **The build system** → injects `version.sh` output into the binary/artifact (language-specific wiring in §6).
- **No manifest stamp**: the version is not stored in a file; it is read from git at build time.

> A non-shallow clone is required (since it counts merges). Dev machines / host builds are always full clones, so this is moot.

## 3. Two deployment processes — tags only on actual shipments

| Stage | Build | Version | Tag |
|------|------|------|------|
| Developer local/lab iteration | dev build | `0.20.5+dev` (increments per commit, dev tools ON) | ❌ |
| **① QA deployment (test)** | release mode | `0.20.5` (increments per commit → QA distinguishes builds) | ❌ |
| **② Product release (after QA passes)** | the **exact build** QA passed in ① | `0.21.0` | ✅ `git tag v0.21.0 && git push origin v0.21.0` |

- QA iterations **only increment the number; zero tags**. Tags accumulate **only as many times as actual shipments**.
- A tag is merely a **marker** saying "this commit is the shipped one"; version computation **does not look at tags** (§1). At
  ship time, you take the computed value `0.21.0` and stamp a same-named tag `v0.21.0`, and that's it.

## 4. Manual MAJOR bump + overflow

- **Manual bump (milestone)**: in `version.conf`, raise `MAJOR_BASE` and set `MR_BASE` to the current
  `git rev-list --merges --count <main>` value → MINOR resets to 0. From that commit on, `1.0.x`.
- **Auto-carry (failsafe)**: when MINOR (= merges in the current major range) exceeds 999999, the `/1000000` carries into MAJOR
  and MINOR wraps. In practice a human will have bumped manually long before, so this almost never fires.
- During 0.x, leave both at their defaults (`0`/`0`); when promoting to `1.0`, decide via the procedure above.

## 5. How this differs from the global standard — adoption criteria

The format (`MAJOR.MINOR.PATCH`) is the same; **the meaning of the numbers differs**.

| Axis | Global standard (SemVer + semantic-release) | **Structure-based (this policy)** |
|---|---|---|
| Meaning of the numbers | **Compatibility contract** | **Build identification / progress (odometer)** |
| major / minor / patch | breaking / feature (`feat`) / bug (`fix`) | milestone / merge count / direct-commit count |
| Question it answers | "Is it safe to upgrade?" | "Which build is it / is it newer?" |
| Bump trigger | commit **message type** | git **structure** (merges/commits) |
| Where & when computed | CI runner, on main merge | **local, at build time** |
| Dependencies | CI + token + Conventional Commits discipline | **none (pure git)** |
| Tags | automatic on every releasable merge (many) | manual, only on actual product releases (few) |
| Extras | CHANGELOG · release notes automatic | none (manual if you want them) |

**Projects this policy suits**: internal/in-house products with no external consumers, on-demand shipping, where QA build
identification is the priority and you want local determinism without CI/tokens.

**Projects that should use the standard (semantic-release) instead**: public npm packages / libraries / SDKs and the like, where
**unknown external consumers must judge upgrade safety from the number**. In that case, do not adopt this policy.

## 6. Distinguishing dev / release builds (wiring is language-specific)

- **dev build** → `+dev` suffix (`0.20.2+dev`), dev-only routes/tools ON. For the developer's own / lab verification.
  Add the suffix with `version.sh --dev`.
- **release build** → no suffix (`0.20.2`), dev tools OFF. **Identical to the QA/customer shipment.**
- If there are uncommitted tracked changes, `-dirty` is appended (`0.20.2-dirty`, same meaning as `git describe --dirty` —
  untracked files are ignored).
- For the concrete wiring that injects the version into the build system, see [references/build-wiring.md](references/build-wiring.md) (Make/Go/Node/Python/generic).
