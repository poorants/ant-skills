#!/usr/bin/env python3
"""engram workspace registry — shared brains across repos (SSH-config style).

engram is installed at user scope, so a single user-scope registry holds the
"brains" (named, independently git-versioned local directories) and maps each
repo to the brain it uses. Many repos in a group (e.g. everything under
d:/devel/github) can share ONE brain, so knowledge follows you across repos
instead of being trapped in each repo's local brain/.

Registry file (user scope, JSON — plain, git-diffable, hand-editable):

    <config_dir>/engram/config.json
    {
      "version": 1,
      "brains": {
        "personal": {"path": "D:/devel/github/brain", "autopush": true,
                     "remote": "origin", "branch": "main"},
        "work":     {"path": "D:/work/gitlab/brain", "autopush": false}
      },
      "assignments": {                 # repo root (abs) -> brain name | "local"
        "D:/devel/github/myrepo": "personal",
        "D:/work/gitlab/svc":     "work"
      }
    }

`<config_dir>` = $ENGRAM_CONFIG_DIR, else $CLAUDE_CONFIG_DIR, else ~/.claude.
Override the whole file path with $ENGRAM_CONFIG (used by tests).

Resolution (the engram skill, engram_lint.py and brain_reflect.py all call this):
  1. explicit --base (handled by the caller, not here)
  2. repo has an assignment in the registry -> that brain (or "local")   [explicit]
  3. no assignment but a local brain/ · para/ · flat PARA exists -> local [back-compat]
  4. nothing -> source="none"; the skill prompts a picker (lint/hooks fall back
     to a silent local brain/ default so they never block).

Importable: `from workspace import resolve_brain`. CLI for the skill:
    register <path> [--name N] [--no-autopush] [--remote R] [--branch B]
    assign <brain-name|local> [--repo P] [--no-pointer]
    unassign [--repo P] [--no-pointer]
    link [--repo P] [--remove]
    remove <brain-name>
    list [--repo P] [--json]
    resolve [--repo P] [--json]
All CLI output is UTF-8 regardless of console code page.

Repo-side pointer: the assignment lives only in this user-scope registry (abs
paths must not be committed), so a fresh agent session in an assigned repo would
not know a brain exists. `assign <brain>` therefore also drops a small *portable*
pointer block into the repo's CLAUDE.md (brain name + git remote + in-brain
subpath + "resolve the local path via engram") so every session discovers the
brain; `assign local`/`unassign` strip it again. `link` re-applies it on demand.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PARA_CATEGORIES = ("projects", "areas", "resources", "archives")


# --------------------------------------------------------------------------- #
# config location + load/save
# --------------------------------------------------------------------------- #
def config_path() -> Path:
    override = os.environ.get("ENGRAM_CONFIG")
    if override:
        return Path(override).expanduser()
    base = os.environ.get("ENGRAM_CONFIG_DIR") or os.environ.get("CLAUDE_CONFIG_DIR")
    root = Path(base).expanduser() if base else (Path.home() / ".claude")
    return root / "engram" / "config.json"


def load_config() -> dict:
    p = config_path()
    if not p.is_file():
        return {"version": 1, "brains": {}, "assignments": {}}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {"version": 1, "brains": {}, "assignments": {}}
    data.setdefault("version", 1)
    data.setdefault("brains", {})
    data.setdefault("assignments", {})
    return data


def save_config(cfg: dict) -> Path:
    p = config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p


# --------------------------------------------------------------------------- #
# path / git helpers
# --------------------------------------------------------------------------- #
def _norm(p: str | Path) -> str:
    """Comparison key: absolute, normalized case (Windows-safe)."""
    return os.path.normcase(os.path.abspath(os.path.expanduser(str(p))))


def _display(p: str | Path) -> str:
    """Readable, stable storage form: absolute with forward slashes."""
    return Path(os.path.expanduser(str(p))).resolve().as_posix()


def git_root(cwd: str | Path) -> str:
    """Repo root via git; fall back to walking up for a .git entry, else cwd."""
    cwd = os.path.abspath(str(cwd))
    try:
        out = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            return os.path.abspath(out.stdout.strip())
    except Exception:
        pass
    cur = Path(cwd)
    for d in (cur, *cur.parents):
        if (d / ".git").exists():
            return str(d)
    return cwd


def owning_git_dir(path: str | Path) -> str | None:
    """The git repo root that owns `path` — `path` itself or any ancestor with a
    .git (a brain may be a nested brain/ inside its own git repo)."""
    p = Path(path)
    for d in (p, *p.parents):
        if (d / ".git").exists():
            return str(d)
    return None


def is_git_repo(path: str | Path) -> bool:
    return owning_git_dir(path) is not None


def has_remote(path: str | Path, remote: str = "origin") -> bool:
    root = owning_git_dir(path)
    if not root:
        return False
    try:
        out = subprocess.run(
            ["git", "-C", root, "remote"],
            capture_output=True, text=True, timeout=5,
        )
        return out.returncode == 0 and remote in out.stdout.split()
    except Exception:
        return False


def local_base(repo_root: str | Path) -> tuple[Path, str] | None:
    """Detect a repo-local PARA base: brain/ -> para/ -> flat root."""
    root = Path(repo_root)
    if (root / "brain").is_dir():
        return (root / "brain").resolve(), "brain"
    if (root / "para").is_dir():
        return (root / "para").resolve(), "para"
    if any((root / c).is_dir() for c in PARA_CATEGORIES):
        return root.resolve(), "."
    return None


# --------------------------------------------------------------------------- #
# resolution
# --------------------------------------------------------------------------- #
def find_assignment(cfg: dict, repo_root: str) -> str | None:
    key = _norm(repo_root)
    for stored, brain in cfg.get("assignments", {}).items():
        if _norm(stored) == key:
            return brain
    return None


def resolve_brain(cwd: str | Path | None = None) -> dict:
    """Resolve the brain for a repo. Returns a dict:
        {base, label, source, brain, autopush, remote, branch, warning}
    source in {assignment, assignment-local, local, none}. `base` is None only
    when source == "none" (no assignment and no local base) — callers either
    prompt a picker (skill) or fall back to a local brain/ default (lint/hooks).
    """
    cwd = os.path.abspath(str(cwd or os.getcwd()))
    repo_root = git_root(cwd)
    cfg = load_config()

    result = {"base": None, "label": None, "source": "none", "brain": None,
              "autopush": False, "remote": "origin", "branch": None,
              "repo_root": repo_root, "warning": None}

    assigned = find_assignment(cfg, repo_root)
    if assigned is not None:
        if assigned == "local":
            lb = local_base(repo_root)
            if lb:
                result.update(base=str(lb[0]), label=lb[1], source="assignment-local")
            else:
                result.update(base=str((Path(repo_root) / "brain").resolve()),
                              label="brain", source="assignment-local")
            return result
        brain = cfg.get("brains", {}).get(assigned)
        if brain and brain.get("path"):
            result.update(
                base=str(Path(os.path.expanduser(brain["path"])).resolve()),
                label=assigned, source="assignment", brain=assigned,
                autopush=bool(brain.get("autopush", False)),
                remote=brain.get("remote", "origin"),
                branch=brain.get("branch"),
            )
            return result
        result["warning"] = f"assignment points to unknown brain '{assigned}'"

    # no (valid) assignment -> local base wins (back-compat, don't nag vaults)
    lb = local_base(repo_root)
    if lb:
        result.update(base=str(lb[0]), label=lb[1], source="local")
        return result

    # nothing: skill should prompt; lint/hooks fall back to a silent brain/
    return result


# --------------------------------------------------------------------------- #
# repo-side brain pointer (CLAUDE.md)
# --------------------------------------------------------------------------- #
# A repo assigned to a shared brain keeps that assignment in the user-scope
# registry only — machine-specific absolute paths must never be committed. The
# side effect: a fresh agent session in the repo has no idea a brain exists, so
# durable knowledge in the brain stays undiscovered until someone invokes engram.
# Fix: drop a small *portable* pointer into the repo's CLAUDE.md (which every
# session loads) — brain name + git remote + the in-brain subpath + "resolve the
# local path via engram". The machine-specific checkout path is left out and
# resolved on demand. The block is marker-delimited so it is idempotent: re-runs
# replace it in place, and unassign/assign-local strip it.

POINTER_BEGIN = (
    "<!-- BEGIN engram:brain-pointer (managed by engram — regenerate via the "
    "engram skill / `workspace.py link`; do not hand-edit) -->"
)
POINTER_END = "<!-- END engram:brain-pointer -->"
_POINTER_RE = re.compile(
    r"\n*<!-- BEGIN engram:brain-pointer.*?<!-- END engram:brain-pointer -->[ \t]*\n?",
    re.DOTALL,
)


def remote_url(path: str | Path, remote: str = "origin") -> str | None:
    """The brain repo's remote URL (portable, committable) — None if unavailable."""
    root = owning_git_dir(path)
    if not root:
        return None
    try:
        out = subprocess.run(
            ["git", "-C", root, "remote", "get-url", remote],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:
        pass
    return None


def _pointer_body(brain: str, remote: str | None, subpath: str) -> str:
    remote_line = (
        f"- Brain (git remote): `{remote}`" if remote
        else "- Brain: a shared engram workspace brain (see the engram registry)"
    )
    return (
        "## Project knowledge lives in an engram brain\n\n"
        f"This repo is assigned to the engram **{brain}** brain. Its durable design\n"
        "knowledge, decisions, and history live in that brain — not in this repo's code.\n\n"
        f"{remote_line}\n"
        f"- This repo's notes within the brain: `{subpath}`\n\n"
        "Before answering architecture, history, or \"why is it built this way\"\n"
        "questions, read those brain docs first. The brain's local checkout path is\n"
        "machine-specific, so it is deliberately not hard-coded here — resolve it on\n"
        "this machine with the engram skill (it runs `workspace.py resolve` and reads\n"
        "the `base` field). Manage this pointer and the assignment with `/engram`.\n"
    )


def build_pointer(repo_root: str | Path, r: dict) -> str:
    subpath = f"projects/{Path(repo_root).name}/"
    rurl = remote_url(r["base"], r.get("remote") or "origin") if r.get("base") else None
    body = _pointer_body(r.get("brain") or r.get("label") or "shared", rurl, subpath)
    return f"{POINTER_BEGIN}\n{body}{POINTER_END}"


def write_repo_pointer(repo_root: str | Path, r: dict) -> tuple[str, Path]:
    """Create/refresh the brain-pointer block in <repo>/CLAUDE.md. Idempotent."""
    f = Path(repo_root) / "CLAUDE.md"
    original = f.read_text(encoding="utf-8") if f.is_file() else None
    existed = original is not None
    stripped = _POINTER_RE.sub("\n", original).rstrip() if existed else ""
    block = build_pointer(repo_root, r)
    new = f"{stripped}\n\n{block}\n" if stripped else f"{block}\n"
    if existed and new == original:
        return "unchanged", f
    f.write_text(new, encoding="utf-8")
    return ("updated" if existed else "created"), f


def remove_repo_pointer(repo_root: str | Path) -> tuple[str, Path]:
    """Strip the brain-pointer block from <repo>/CLAUDE.md. Deletes the file only
    if the block was its sole content."""
    f = Path(repo_root) / "CLAUDE.md"
    if not f.is_file():
        return "absent", f
    original = f.read_text(encoding="utf-8")
    stripped = _POINTER_RE.sub("\n", original)
    if stripped == original:
        return "absent", f
    rest = stripped.strip()
    if rest:
        f.write_text(rest + "\n", encoding="utf-8")
        return "removed", f
    f.unlink()
    return "removed-empty", f


def apply_repo_pointer(repo_root: str, *, emit=lambda _m: None) -> None:
    """Sync the repo's CLAUDE.md pointer to its current assignment: write when
    assigned to a shared brain, strip otherwise."""
    r = resolve_brain(repo_root)
    if r["source"] == "assignment" and r.get("brain"):
        state, f = write_repo_pointer(repo_root, r)
        emit(f"brain pointer {state}: {Path(f).as_posix()} (-> {r['brain']})")
    else:
        state, f = remove_repo_pointer(repo_root)
        if state != "absent":
            emit(f"brain pointer {state}: {Path(f).as_posix()}")


# --------------------------------------------------------------------------- #
# CLI commands
# --------------------------------------------------------------------------- #
def _emit(obj: dict) -> None:
    sys.stdout.buffer.write((json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    sys.stdout.buffer.flush()


def _print(msg: str) -> None:
    sys.stdout.buffer.write((msg + "\n").encode("utf-8"))
    sys.stdout.buffer.flush()


def cmd_register(args) -> int:
    path = Path(os.path.expanduser(args.path)).resolve()
    if not path.is_dir():
        _print(f"error: not a directory: {path}")
        return 1
    name = args.name or path.name
    autopush = not args.no_autopush
    warnings = []
    if not is_git_repo(path):
        warnings.append("not a git repo — autopush disabled")
        autopush = False
    elif autopush and not has_remote(path, args.remote):
        warnings.append(f"no '{args.remote}' remote — autopush disabled")
        autopush = False

    cfg = load_config()
    entry = {"path": _display(path), "autopush": autopush, "remote": args.remote}
    if args.branch:
        entry["branch"] = args.branch
    existed = name in cfg["brains"]
    cfg["brains"][name] = entry
    save_config(cfg)

    verb = "updated" if existed else "registered"
    _print(f"brain '{name}' {verb}: {entry['path']} (autopush={autopush})")
    for w in warnings:
        _print(f"  warning: {w}")
    return 0


def cmd_assign(args) -> int:
    repo = git_root(args.repo or os.getcwd())
    cfg = load_config()
    if args.brain != "local" and args.brain not in cfg["brains"]:
        _print(f"error: unknown brain '{args.brain}'. Registered: "
               f"{', '.join(cfg['brains']) or '(none)'}")
        return 1
    # drop any existing key for this repo (case-insensitive), then set fresh
    key = _norm(repo)
    cfg["assignments"] = {k: v for k, v in cfg["assignments"].items() if _norm(k) != key}
    cfg["assignments"][_display(repo)] = args.brain
    save_config(cfg)
    _print(f"assigned {_display(repo)} -> {args.brain}")
    if not getattr(args, "no_pointer", False):
        apply_repo_pointer(repo, emit=_print)
    return 0


def cmd_unassign(args) -> int:
    repo = git_root(args.repo or os.getcwd())
    cfg = load_config()
    key = _norm(repo)
    before = len(cfg["assignments"])
    cfg["assignments"] = {k: v for k, v in cfg["assignments"].items() if _norm(k) != key}
    save_config(cfg)
    _print(f"unassigned {_display(repo)}" if len(cfg["assignments"]) < before
           else f"no assignment for {_display(repo)}")
    if not getattr(args, "no_pointer", False):
        apply_repo_pointer(repo, emit=_print)
    return 0


def cmd_link(args) -> int:
    repo = git_root(args.repo or os.getcwd())
    if args.remove:
        state, f = remove_repo_pointer(repo)
        _print(f"brain pointer {state}: {Path(f).as_posix()}")
        return 0
    r = resolve_brain(repo)
    if not (r["source"] == "assignment" and r.get("brain")):
        _print(f"error: {_display(repo)} is not assigned to a shared brain "
               f"(source={r['source']}). Assign one first: workspace.py assign <name>")
        return 1
    state, f = write_repo_pointer(repo, r)
    _print(f"brain pointer {state}: {Path(f).as_posix()} (-> {r['brain']})")
    return 0


def cmd_remove(args) -> int:
    cfg = load_config()
    if args.name not in cfg["brains"]:
        _print(f"error: no brain '{args.name}'")
        return 1
    del cfg["brains"][args.name]
    refs = [k for k, v in cfg["assignments"].items() if v == args.name]
    save_config(cfg)
    _print(f"removed brain '{args.name}' (directory left untouched)")
    if refs:
        _print(f"  warning: {len(refs)} repo(s) still assigned to it — "
               f"reassign them: {', '.join(refs)}")
    return 0


def cmd_list(args) -> int:
    cfg = load_config()
    repo = git_root(args.repo or os.getcwd())
    current = find_assignment(cfg, repo)
    if args.json:
        _emit({"brains": cfg["brains"], "assignments": cfg["assignments"],
               "current_repo": _display(repo), "current_assignment": current})
        return 0
    _print(f"config: {config_path()}")
    if not cfg["brains"]:
        _print("brains: (none registered)")
    else:
        _print("brains:")
        for name, b in cfg["brains"].items():
            _print(f"  {name}: {b.get('path')} (autopush={b.get('autopush')})")
    _print(f"this repo ({_display(repo)}): {current or '(unassigned)'}")
    return 0


def cmd_resolve(args) -> int:
    r = resolve_brain(args.repo or os.getcwd())
    if args.json:
        _emit(r)
        return 0
    _print(f"base={r['base']} label={r['label']} source={r['source']}"
           + (f" brain={r['brain']} autopush={r['autopush']}" if r["brain"] else ""))
    if r["warning"]:
        _print(f"warning: {r['warning']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="engram workspace brain registry")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("register", help="register a brain directory")
    p.add_argument("path")
    p.add_argument("--name")
    p.add_argument("--no-autopush", action="store_true")
    p.add_argument("--remote", default="origin")
    p.add_argument("--branch")
    p.set_defaults(func=cmd_register)

    p = sub.add_parser("assign", help="assign this repo to a brain (or 'local')")
    p.add_argument("brain")
    p.add_argument("--repo")
    p.add_argument("--no-pointer", action="store_true",
                   help="do not touch the repo's CLAUDE.md brain pointer")
    p.set_defaults(func=cmd_assign)

    p = sub.add_parser("unassign", help="remove this repo's assignment")
    p.add_argument("--repo")
    p.add_argument("--no-pointer", action="store_true",
                   help="do not touch the repo's CLAUDE.md brain pointer")
    p.set_defaults(func=cmd_unassign)

    p = sub.add_parser("link", help="write/refresh (or --remove) this repo's "
                                    "CLAUDE.md brain pointer")
    p.add_argument("--repo")
    p.add_argument("--remove", action="store_true",
                   help="strip the pointer instead of writing it")
    p.set_defaults(func=cmd_link)

    p = sub.add_parser("remove", help="remove a brain from the registry")
    p.add_argument("name")
    p.set_defaults(func=cmd_remove)

    p = sub.add_parser("list", help="list brains and this repo's assignment")
    p.add_argument("--repo")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("resolve", help="resolve the brain base for this repo")
    p.add_argument("--repo")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_resolve)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as e:  # never crash the skill
        sys.stderr.write(f"workspace error: {e}\n")
        raise SystemExit(1)
