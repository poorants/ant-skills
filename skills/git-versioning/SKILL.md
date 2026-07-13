---
name: git-versioning
description: "Adopt and operate a structure-based MAJOR.MINOR.PATCH versioning scheme computed locally from the git commit graph at build time — no tags, CI, or tokens. MINOR = merge (MR/PR) count, PATCH = direct main commits since the last merge, MAJOR = a human-chosen milestone. Suited to internal/in-house products that need a monotonically increasing version to identify which build is which (for public libraries, prefer standard SemVer). Covers installing version.sh + version.conf, build-system wiring (Make/Go/Node/Python), MAJOR bumps, and tagging vX.Y.Z at actual release. Use when user says /git-versioning, 'set up versioning', 'version scheme', 'how is the version computed', 'bump major', 'tag a release', 'version 붙이기'. 트리거: 버전 관리, 버전 체계, 버전 매기기, 버전 계산, 버전 도입, 메이저 올리기, 릴리스 태그, 버전 스킬."
---

# git-versioning: structure-based version scheme

Adopt and operate a `MAJOR.MINOR.PATCH` version scheme that is **computed locally at
build time** from the git commit graph. It needs no tags, CI, or tokens, and is
**deterministic** — the same commit always yields the same version.

- **MINOR** = merge (MR/PR) count − `MR_BASE` → +1 per merge, resets patch to 0
- **PATCH** = direct main commits since the last merge (first-parent) → +1 per hotfix commit, 0 right after a merge
- **MAJOR** = `MAJOR_BASE` (a human-chosen milestone) + overflow carry (effectively never)

The number is a **monotonically increasing build identifier** pointing at "where in git
this build sits." For the full rationale and the comparison to the standard, see
[references/versioning-policy.md](references/versioning-policy.md).

## When this scheme fits (decide first)

- ✅ **Fits**: internal/in-house products with no external consumers, on-demand shipping,
  QA needing to identify "which build is this," local determinism without CI/tokens.
- ❌ **Does not fit**: public npm/library/SDK where **unknown external consumers judge
  upgrade safety from the number** → prefer standard SemVer + Conventional Commits +
  semantic-release. Confirm with the user before `init`.

## Enforcement: the forge must create a merge commit per MR/PR

MINOR counts merge commits (`git rev-list --merges`), so the scheme has one hard
prerequisite: **every MR/PR merge must actually produce a merge commit.** Two common
merge modes break this silently:

- **Fast-forward merge** — when main has not moved since the branch was cut, git just
  advances the pointer with **no merge commit**. The branch's commits land as
  first-parent commits, counting toward PATCH, not MINOR.
- **Squash merge** — collapses the branch into a single commit on main, also with no
  merge commit.

Either way the MR does not bump MINOR and the work leaks into PATCH, so the version
undercounts real merge activity.

**Enforce it at the forge, not with a git hook.** A client-side git hook cannot do this,
by construction:

1. The MR/PR merge runs **on the forge server**, where the developer's local
   `.git/hooks` never execute.
2. A fast-forward produces **no commit**, so there is no `pre-merge-commit` (or any)
   hook event to hang a check on.
3. Locally the two cases are indistinguishable — an ff-absorbed MR and an *intentional*
   direct PATCH commit both look like new first-parent commits on main. "This was an MR"
   is knowledge only the forge holds.

Set the merge method on the forge (server-side, unbypassable):

- **GitLab** — Settings → Merge requests → **Merge method = "Merge commit"**
  (`merge_method=merge`). Do **not** use "Fast-forward merge".
- **GitHub** — repo Settings → Pull Requests → keep **"Allow merge commits"** and
  **disable** "Allow squash merging" and "Allow rebase merging".

**No forge-admin access?** The fallback is a CI *detective* check on main (recompute the
version and assert it increased, or flag a push that added first-parent commits with no
merge commit). It catches an undercount after the fact but **cannot prevent it** —
prevention lives only at the forge layer.

## Usage

```
/git-versioning                  -- print the currently computed version (default)
/git-versioning status           -- same as above + breakdown (MAJOR/MINOR/PATCH basis)
/git-versioning init             -- install version.sh + version.conf + policy doc, then wire the build system
/git-versioning bump-major       -- manually bump the MAJOR milestone (edit version.conf)
/git-versioning release          -- guide tagging vX.Y.Z at an actual release
/git-versioning explain          -- explain what this scheme is and why it differs from the standard
```

## Commands

### `status` (default)

1. If `scripts/version.sh` exists at the project root, run it; otherwise run this skill's
   [scripts/version.sh](scripts/version.sh) to print the version.
2. `status` also shows the breakdown — gather these git facts into a table:
   - `git rev-list --merges --count HEAD` → MINOR basis (merge count)
   - `git rev-list --count --first-parent <last-merge>..HEAD` → PATCH basis (commits since last merge)
   - `MAJOR_BASE`/`MR_BASE` from `version.conf`
   - `git update-index -q --refresh` then `git diff-index --quiet HEAD` → dirty state (the refresh avoids a stale-stat false "-dirty" after a build step recreated tracked files)
3. If `version.sh` is not installed yet, recommend `init`.

### `init`

Install the scheme into the project. **In order**:

1. **Fit check** — review "When this scheme fits" above with the user. If it is a public
   library, recommend standard SemVer and stop.
2. **Install `scripts/version.sh`** — copy this skill's [scripts/version.sh](scripts/version.sh)
   to the project's `scripts/version.sh` and `chmod +x`. If it already exists, confirm before
   overwriting.
3. **Create `version.conf`** (repo root) — defaults during 0.x:
   ```
   # Build version baseline — read by scripts/version.sh. Policy: <policy doc path chosen in step 4>
   MAJOR_BASE=0
   MR_BASE=0
   ```
4. **Copy the policy doc** — copy [references/versioning-policy.md](references/versioning-policy.md)
   and substitute `{PROJECT}`. **Decide the destination path by first detecting the project's
   doc convention**: check `CLAUDE.md` for a doc-layout convention, or an existing docs folder
   (`brain/`, `docs/`, `para/`, …). The default is `docs/versioning.md`. **But always check
   whether the destination is `.gitignore`d** — e.g. if `docs/` is ignored, the policy doc
   never gets committed and silently disappears (verify with `git check-ignore <path>`). In
   that case place it on a tracked doc path (e.g. `brain/areas/` when the project uses brain),
   and match the policy-path mention in the `version.conf` comment and the `version.sh` header
   accordingly.
5. **Wire the build system** — follow [references/build-wiring.md](references/build-wiring.md)
   to add version injection for the detected build system (Make/Go/Node/Python/generic). If
   several are present, ask the user which one to wire.
6. **Enforce merge commits** — configure the forge so every MR/PR produces a merge commit
   (GitLab `merge_method=merge`; GitHub disable squash & rebase merging). See
   [Enforcement](#enforcement-the-forge-must-create-a-merge-commit-per-mrpr). Without this,
   fast-forward/squash merges silently undercount MINOR. If you lack forge-admin access, note
   the detective-check fallback for the user.
7. **Verify** — run `bash scripts/version.sh` and `--dev`, show that the values are sensible,
   and note that a non-shallow clone is required (it counts merges).

> Outputs are created in the **user's project** (not inside the skill directory).

### `bump-major`

Raise MAJOR for a milestone (rare). Procedure in [versioning-policy.md](references/versioning-policy.md) §4:

1. Check the current merge count: `git rev-list --merges --count <main-branch>` (e.g. origin/main).
2. Edit `version.conf` — raise `MAJOR_BASE` to the target major and set `MR_BASE` to the merge
   count above → MINOR resets to 0.
3. Commit that change. Versions then start from `<new-major>.0.x`.
4. Confirm the result with `version.sh`.

### `release`

Tag a QA-passed build as an actual release. Tags are created **only at actual releases**
([policy](references/versioning-policy.md) §3):

1. Confirm the commit to ship is checked out and clean (no `-dirty`).
2. Compute that commit's version: `bash scripts/version.sh` → e.g. `0.21.0`.
3. Create and push the same-named tag:
   ```
   git tag v0.21.0
   git push origin v0.21.0
   ```
4. The tag is only a marker — version computation does not read tags (§1). Do not pile up a
   tag per merge.

### `explain`

Using [versioning-policy.md](references/versioning-policy.md) as the basis, explain what this
scheme is (§1) and how it differs from standard SemVer (§5), at the user's level. "Why not
semantic-release" is §0.

## Resources

| File | Purpose |
|------|---------|
| [scripts/version.sh](scripts/version.sh) | Single source of version computation (language-agnostic, pure git). `init` copies it into the project. |
| [references/versioning-policy.md](references/versioning-policy.md) | Policy, rationale, comparison to the standard. `init` copies it to the project's doc-convention path. |
| [references/build-wiring.md](references/build-wiring.md) | Make/Go/Node/Python/generic build-wiring recipes. |

## Notes

- **Counts merges, so a non-shallow clone is required.** CI/Docker should compute on the host
  and pass it in via build-arg ([build-wiring.md](references/build-wiring.md) Docker/CI section).
- **Merges must create a merge commit** or MINOR undercounts — fast-forward and squash merges
  skip it. Enforce at the forge, not with a git hook: see
  [Enforcement](#enforcement-the-forge-must-create-a-merge-commit-per-mrpr).
- The build version carries no `v` (`0.21.0`); only release **tags** use `vX.Y.Z`.
