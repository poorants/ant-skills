#!/usr/bin/env python3
"""engram integrity linter (knowledge-network linter).

Scans every markdown document under the current repo's PARA base and finds two
kinds of integrity problems in the networked-knowledge structure.

  1. Broken links
     - Markdown relative link `[text](relative/path.md)` pointing to a file that
       does not exist (error).
     - Wikilink `[[name]]` that matches no file (warning — may be a future note
       not created yet).
  2. Orphan nodes
     - A document that receives no inbound link from any other document.

The engram skill (the intelligence) calls this script (the shared muscle),
parses the result, and repairs the network by reconnecting broken links or
adding contextual links to orphans.

PARA base auto-detection (the skill runs at the target repo root = cwd):
  - If the root contains any of projects/ areas/ resources/ archives/ -> flat
    mode, base = root (a standalone document vault / brain). This is the
    standalone-doc-repo case.
  - Else if para/ exists -> nested mode, base = para/ (a code project + docs).
  - Else -> assume para/ (silent if missing).
  - Override with `--base PATH`.

Usage (from the target repo root):
    python <skill>/scripts/engram_lint.py            # human report (silent if clean)
    python <skill>/scripts/engram_lint.py --json     # machine JSON (skill parses)
    python <skill>/scripts/engram_lint.py --base .   # force base (root)
    python <skill>/scripts/engram_lint.py --all      # print summary even when clean

Exit code is always 0 (non-blocking). Wikilinks may point to future notes
(Obsidian convention), so problems are reported but never block work.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path.cwd()
PARA_CATEGORIES = ("projects", "areas", "resources", "archives")

# Filenames exempt from the orphan check (structural files only give links, so
# the orphan concept does not apply to them).
ORPHAN_EXEMPT_NAMES = {"README.md", "_index.md", "index.md", "CLAUDE.md", "MEMORY.md"}

# Path prefixes (relative to base) exempt from the orphan check — e.g. a blog
# kept isolated for external publishing. Harmless when absent.
ORPHAN_EXEMPT_PREFIXES = ("areas/blog/",)

WIKILINK_RE = re.compile(r"(?<!!)\[\[([^\]\n]+?)\]\]")          # [[target]] / [[target|alias]] (excludes embeds ![[..]])
MDLINK_RE = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\s]+)\)")       # [text](target) (excludes images ![..](..))
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)                   # fenced code blocks
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")                        # inline code


def parse_base_arg() -> str | None:
    for i, a in enumerate(sys.argv):
        if a == "--base" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
        if a.startswith("--base="):
            return a.split("=", 1)[1]
    return None


def resolve_base() -> tuple[Path, str]:
    """Return (base path, display label). Auto-detects flat/nested."""
    arg = parse_base_arg()
    if arg is not None:
        return (REPO / arg).resolve(), arg
    # flat mode: PARA category folders at the root -> root is the base (standalone vault)
    if any((REPO / c).is_dir() for c in PARA_CATEGORIES):
        return REPO, "."
    # nested mode: para/ is the base (code project + docs)
    return (REPO / "para").resolve(), "para"


def strip_code(text: str) -> str:
    return INLINE_CODE_RE.sub("", FENCE_RE.sub("", text))


def is_excluded(parts: tuple[str, ...]) -> bool:
    """Exclude hidden directories and node_modules."""
    return any(p == "node_modules" or (p.startswith(".") and len(p) > 1) for p in parts)


def main() -> int:
    as_json = "--json" in sys.argv
    show_all = "--all" in sys.argv

    base, base_label = resolve_base()

    if not base.is_dir():
        result = {"base": base_label, "scanned": 0, "broken_md_links": [],
                  "dangling_wikilinks": [], "orphans": [], "note": "base directory not found"}
        if as_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif show_all:
            print(f"[engram] PARA base ('{base_label}') not found - skipping check.")
        return 0

    def rel(p: Path) -> str:
        try:
            return p.relative_to(REPO).as_posix()
        except ValueError:
            return p.as_posix()

    def rel_base(p: Path) -> str:
        return p.relative_to(base).as_posix()

    files = [p for p in base.rglob("*.md") if not is_excluded(p.relative_to(base).parts)]

    by_stem: dict[str, list[Path]] = {}
    for f in files:
        by_stem.setdefault(f.stem, []).append(f)

    inbound: dict[Path, int] = {f: 0 for f in files}
    broken_md: list[tuple[str, str]] = []
    dangling_wiki: list[tuple[str, str]] = []

    for src in files:
        try:
            text = strip_code(src.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, OSError):
            continue

        for raw in WIKILINK_RE.findall(text):
            name = raw.split("|", 1)[0].split("#", 1)[0].strip()
            if not name:
                continue
            targets = by_stem.get(Path(name).stem, [])
            real_targets = [t for t in targets if t != src]
            if real_targets:
                for t in real_targets:
                    inbound[t] += 1
            elif not targets:
                dangling_wiki.append((rel(src), name))

        for target in MDLINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#", "tel:")):
                continue
            clean = target.split("#", 1)[0].split("?", 1)[0]
            if not clean or not clean.endswith(".md"):
                continue
            resolved = (src.parent / clean).resolve()
            if resolved.exists():
                if resolved != src and resolved in inbound:
                    inbound[resolved] += 1
            else:
                broken_md.append((rel(src), target))

    orphans: list[str] = []
    for f, count in inbound.items():
        if count > 0 or f.name in ORPHAN_EXEMPT_NAMES:
            continue
        rb = rel_base(f)
        if any(rb.startswith(p) for p in ORPHAN_EXEMPT_PREFIXES):
            continue
        orphans.append(rel(f))

    orphans.sort()
    broken_md.sort()
    dangling_wiki.sort()

    result = {
        "base": base_label,
        "scanned": len(files),
        "broken_md_links": [{"source": s, "target": t} for s, t in broken_md],
        "dangling_wikilinks": [{"source": s, "name": n} for s, n in dangling_wiki],
        "orphans": orphans,
    }
    has_issues = bool(broken_md or orphans)

    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if not has_issues and not show_all:
        return 0

    where = "root" if base_label == "." else f"{base_label}/"
    lines = [f"[engram] integrity check ({len(files)} docs / {where})"]
    if broken_md:
        lines.append(f"  [X] {len(broken_md)} broken link(s):")
        lines += [f"     - {s} -> {t}" for s, t in broken_md]
    if orphans:
        lines.append(f"  [orphan] {len(orphans)} orphan doc(s) (no inbound link):")
        lines += [f"     - {o}" for o in orphans]
    if dangling_wiki:
        lines.append(f"  [!] {len(dangling_wiki)} unresolved wikilink(s) (may be a note not created yet):")
        lines += [f"     - {s} -> [[{n}]]" for s, n in dangling_wiki]
    if not has_issues:
        lines.append("  [ok] no broken links / orphans.")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
