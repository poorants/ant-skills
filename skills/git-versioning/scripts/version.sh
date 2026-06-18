#!/usr/bin/env bash
# Structure-based build version — derived from the git commit graph (no tags / CI
# / token). Single source of truth for the build system and any version stamp.
# Full rationale: ../references/versioning-policy.md (copied into the project as
# docs/versioning.md by `git-versioning init`).
#
#   VERSION = MAJOR.MINOR.PATCH[-dirty][+dev]
#     MR_TOTAL  = merge commits reachable from HEAD            (each merge/MR/PR = one)
#     minor_raw = MR_TOTAL - MR_BASE                           (merges in this major)
#     MAJOR     = MAJOR_BASE + minor_raw / 1000000             (overflow carry; ~never)
#     MINOR     = minor_raw % 1000000                          (0..999999)
#     PATCH     = first-parent commits since the last merge    (0 right after a merge,
#                                                               grows with direct-to-main commits)
#
# Baseline (MAJOR_BASE / MR_BASE) lives in repo-root `version.conf` (defaults 0/0).
# A manual MAJOR bump edits version.conf: MAJOR_BASE++ and MR_BASE=<current MR_TOTAL>
# so MINOR resets to 0. The build version carries NO `v` prefix (release *tags* use
# `vX.Y.Z`). Deterministic: a pure function of the commit + version.conf.
#
# Flags:
#   --dev        append "+dev" (developer / lab build marker)
#   --no-dirty   never append "-dirty" even with uncommitted tracked changes
#
# NOTE: counts merges reachable from HEAD, so a non-shallow clone is required for an
# accurate number. Compute on the host and pass VERSION into a Docker/CI build so the
# container never needs git history.
set -u

dev=""; allow_dirty=1
for arg in "$@"; do
  case "$arg" in
    --dev) dev="+dev" ;;
    --no-dirty) allow_dirty=0 ;;
  esac
done

root=$(git rev-parse --show-toplevel 2>/dev/null || true)
[ -n "$root" ] && cd "$root"

conf_get() { [ -f version.conf ] && grep -E "^$1=" version.conf 2>/dev/null | tail -1 | cut -d= -f2 | tr -dc '0-9'; }
MAJOR_BASE=$(conf_get MAJOR_BASE); MAJOR_BASE=${MAJOR_BASE:-0}
MR_BASE=$(conf_get MR_BASE);       MR_BASE=${MR_BASE:-0}

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "0.0.0${dev}"
  exit 0
fi

mr_total=$(git rev-list --merges --count HEAD 2>/dev/null || echo 0)
last_merge=$(git rev-list --merges -1 HEAD 2>/dev/null || true)
if [ -n "$last_merge" ]; then
  patch=$(git rev-list --count --first-parent "${last_merge}..HEAD" 2>/dev/null || echo 0)
else
  patch=$(git rev-list --count --first-parent HEAD 2>/dev/null || echo 0)
fi

mr_total=${mr_total:-0}; patch=${patch:-0}
minor_raw=$(( mr_total - MR_BASE ))
[ "$minor_raw" -lt 0 ] && minor_raw=0
major=$(( MAJOR_BASE + minor_raw / 1000000 ))
minor=$(( minor_raw % 1000000 ))

dirty=""
if [ "$allow_dirty" -eq 1 ]; then
  git diff-index --quiet HEAD -- 2>/dev/null || dirty="-dirty"
fi

echo "${major}.${minor}.${patch}${dirty}${dev}"
