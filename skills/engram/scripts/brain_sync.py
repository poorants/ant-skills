#!/usr/bin/env python3
"""engram brain autosync — commit (and push) a shared, assigned brain repo.

A workspace brain (see workspace.py) is an independent git repo at an external
path that several code repos share. When engram writes into it, those changes
must be committed there — not in the code repo you happen to be working in — and,
for shared use, pushed so other repos/machines see them.

Decision (see SKILL.md "Brain autosync"):
  - commit on save: cheap, local, automatic. Wired to the Stop hook via `auto`.
  - push at wrap-up: network + may conflict, so it is model-supervised — the
    capture-loop wrap-up instruction tells the model to run `push`, which surfaces
    conflicts instead of forcing.

Scope guard — this acts ONLY on an external **assigned** brain with autopush=true
(resolve source == "assignment"). It never touches a repo-local brain/, because a
local brain is part of the code repo and is committed together with code; this
tool must never auto-commit the user's code working tree.

Usage:
    python brain_sync.py auto            # Stop hook: commit if dirty (reads stdin cwd)
    python brain_sync.py commit [--repo P] [-m MSG]
    python brain_sync.py push   [--repo P]     # pull --rebase then push
    python brain_sync.py status [--repo P] [--json]

Never fails a session: any error -> exit 0.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from workspace import resolve_brain
except Exception:  # pragma: no cover - degrade silently if registry missing
    resolve_brain = None


def _print(msg: str) -> None:
    sys.stdout.buffer.write((msg + "\n").encode("utf-8"))
    sys.stdout.buffer.flush()


def _git(base: str, *args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", base, *args],
                          capture_output=True, text=True, timeout=timeout)


def _git_dir(base: str) -> str | None:
    """The git repo root that owns `base` (base may be brain/ inside the repo)."""
    p = Path(base)
    for d in (p, *p.parents):
        if (d / ".git").exists():
            return str(d)
    return None


def _autopush_brain(cwd: str | None) -> dict | None:
    """Return a normalized sync target {base, remote, branch, brain} only if this
    repo maps to an external **shared** brain with autopush enabled that lives in a
    git repo; otherwise None (nothing to autosync).

    Two shapes resolve to a syncable shared brain:
    - **absorb** (source=="assignment"): the base IS the shared brain → sync base.
    - **hybrid** (source=="hybrid"): base is the repo-local brain (committed with
      the code, never touched here); the shared brain rides in shared_* → sync it.
    A plain repo-local brain is never synced here — it belongs to the code repo."""
    if resolve_brain is None:
        return None
    r = resolve_brain(cwd or os.getcwd())
    if (r.get("source") == "assignment" and r.get("autopush") and r.get("base")
            and _git_dir(r["base"])):
        return {"base": r["base"], "remote": r.get("remote", "origin"),
                "branch": r.get("branch"), "brain": r.get("brain")}
    if (r.get("source") == "hybrid" and r.get("shared_autopush")
            and r.get("shared_base") and _git_dir(r["shared_base"])):
        return {"base": r["shared_base"], "remote": r.get("shared_remote", "origin"),
                "branch": r.get("shared_branch"), "brain": r.get("shared_brain")}
    return None


def do_commit(base: str, message: str) -> tuple[bool, str]:
    root = _git_dir(base)
    if not root:
        return False, "not inside a git repo"
    # stage everything under the repo root, then commit only if something changed
    _git(root, "add", "-A")
    st = _git(root, "status", "--porcelain")
    if not st.stdout.strip():
        return False, "nothing to commit"
    cm = _git(root, "commit", "-m", message)
    if cm.returncode != 0:
        return False, (cm.stderr or cm.stdout).strip()
    return True, "committed"


def do_push(base: str, remote: str, branch: str | None) -> tuple[bool, str]:
    root = _git_dir(base)
    if not root:
        return False, "not inside a git repo"
    # rebase onto remote first so concurrent writers don't clobber each other
    pull = _git(root, "pull", "--rebase", remote, *( [branch] if branch else [] ))
    if pull.returncode != 0:
        _git(root, "rebase", "--abort")
        return False, ("pull --rebase failed (conflict) — resolve in the brain "
                       f"repo at {root}, then push manually:\n"
                       + (pull.stderr or pull.stdout).strip())
    push = _git(root, "push", remote, *( [branch] if branch else [] ))
    if push.returncode != 0:
        return False, (push.stderr or push.stdout).strip()
    return True, "pushed"


def cmd_auto(_args) -> int:
    # Stop hook: cwd comes via stdin JSON (like brain_reflect.py)
    cwd = None
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        cwd = data.get("cwd")
    except Exception:
        cwd = None
    r = _autopush_brain(cwd)
    if not r:
        return 0
    do_commit(r["base"], "engram: brain update")  # silent, push deferred to wrap-up
    return 0


def cmd_commit(args) -> int:
    r = _autopush_brain(args.repo)
    if not r:
        _print("no external assigned autopush brain for this repo — skipped")
        return 0
    ok, msg = do_commit(r["base"], args.message)
    _print(f"{r['brain']}: {msg}")
    return 0


def cmd_push(args) -> int:
    r = _autopush_brain(args.repo)
    if not r:
        _print("no external assigned autopush brain for this repo — skipped")
        return 0
    do_commit(r["base"], "engram: brain update")
    ok, msg = do_push(r["base"], r.get("remote", "origin"), r.get("branch"))
    _print(f"{r['brain']}: {msg}")
    return 0


def cmd_status(args) -> int:
    if resolve_brain is None:
        _print("workspace registry unavailable")
        return 0
    r = resolve_brain(args.repo or os.getcwd())
    if args.json:
        sys.stdout.buffer.write((json.dumps(r, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        return 0
    _print(f"base={r['base']} source={r['source']} brain={r['brain']} autopush={r['autopush']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="engram brain autosync")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("auto").set_defaults(func=cmd_auto)

    p = sub.add_parser("commit")
    p.add_argument("--repo")
    p.add_argument("-m", "--message", default="engram: brain update")
    p.set_defaults(func=cmd_commit)

    p = sub.add_parser("push")
    p.add_argument("--repo")
    p.set_defaults(func=cmd_push)

    p = sub.add_parser("status")
    p.add_argument("--repo")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_status)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        raise SystemExit(0)  # never break a session
