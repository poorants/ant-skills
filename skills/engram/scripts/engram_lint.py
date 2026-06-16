#!/usr/bin/env python3
"""engram integrity linter (knowledge-network linter).

Scans every markdown document under the current repo's PARA base and reports
integrity problems AND network-shape (neural density) metrics.

  1. Broken links
     - Markdown relative link `[text](relative/path.md)` pointing to a file that
       does not exist (error).
     - Wikilink `[[name]]` that matches no file (warning — may be a future note
       not created yet).
  2. Orphan nodes
     - A document that receives no inbound link from any other document.
  3. Weak nodes (lonely spokes) — the "connected but not woven" signal
     - A document whose ONLY inbound links come from MOC/hub files (README,
       index, …). It passes the orphan check but is just a folder spoke: it is
       reachable by a single path (its folder), so the graph is a star, not a
       brain. A MOC link is necessary but not sufficient; a node becomes woven
       only when a content document links it (ideally across a folder boundary).
       Weak nodes are advisory warnings, surfaced in --json always and in the
       human report under --all. (See linking-rules: "no lonely spokes".)
  4. Density metrics — woven_ratio, cross-folder + hub edge ratios, indeg
     histogram. These quantify how neural the network is, beyond pass/fail.

The engram skill (the intelligence) calls this script (the shared muscle),
parses the result, and repairs the network by reconnecting broken links, adding
contextual links to orphans, and weaving lonely spokes into the wider network
(see the Weave Workflow and scripts/weave_candidates.py).

PARA base auto-detection (the skill runs at the target repo root = cwd):
  - brain/ is the default base for BOTH standalone vaults and code projects; the
    root holds repo meta and any exported/published output.
  - If brain/ exists -> nested mode, base = brain/.
  - Else if para/ exists -> nested mode, base = para/ (legacy, back-compat).
  - Else if the root contains projects/ areas/ resources/ archives/ -> flat mode,
    base = root (a legacy standalone vault).
  - Else -> assume brain/ (silent if missing).
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
    # nested mode (default): brain/ is the base for standalone vaults AND code
    # projects; the root holds repo meta and any exported output.
    if (REPO / "brain").is_dir():
        return (REPO / "brain").resolve(), "brain"
    if (REPO / "para").is_dir():
        return (REPO / "para").resolve(), "para"
    # legacy flat: PARA category folders directly at the root (old standalone vault)
    if any((REPO / c).is_dir() for c in PARA_CATEGORIES):
        return REPO, "."
    # fresh repo -> default to brain/ (silent if it does not exist yet)
    return (REPO / "brain").resolve(), "brain"


def strip_code(text: str) -> str:
    return INLINE_CODE_RE.sub("", FENCE_RE.sub("", text))


def is_excluded(parts: tuple[str, ...]) -> bool:
    """Exclude hidden directories and node_modules."""
    return any(p == "node_modules" or (p.startswith(".") and len(p) > 1) for p in parts)


def main() -> int:
    # Output is UTF-8 regardless of console code page (e.g. cp949 on Korean
    # Windows) so non-ASCII paths/titles never crash the run.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

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

    def is_hub(p: Path) -> bool:
        """A MOC/structural file — gives links but the orphan concept does not
        apply to it. Inbound links FROM a hub only make a target a folder spoke."""
        return p.name in ORPHAN_EXEMPT_NAMES

    def top_folder(p: Path) -> str:
        parts = p.relative_to(base).parts
        return parts[0] if len(parts) > 1 else ""

    # Split inbound by source type: links from a hub (README/index) replicate the
    # folder tree (a spoke); links from a content doc are what actually weave the
    # network. A node with only hub-inbound is a "weak node" (lonely spoke).
    inbound_hub: dict[Path, int] = {f: 0 for f in files}
    inbound_content: dict[Path, int] = {f: 0 for f in files}
    broken_md: list[tuple[str, str]] = []
    dangling_wiki: list[tuple[str, str]] = []
    total_edges = hub_edges = cross_folder_edges = 0

    for src in files:
        try:
            text = strip_code(src.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, OSError):
            continue

        src_is_hub = is_hub(src)
        src_top = top_folder(src)

        def record(dst: Path) -> None:
            nonlocal total_edges, hub_edges, cross_folder_edges
            if dst == src:
                return
            total_edges += 1
            if src_is_hub:
                hub_edges += 1
                inbound_hub[dst] += 1
            else:
                inbound_content[dst] += 1
            if src_top != top_folder(dst):
                cross_folder_edges += 1

        for raw in WIKILINK_RE.findall(text):
            name = raw.split("|", 1)[0].split("#", 1)[0].strip()
            if not name:
                continue
            targets = by_stem.get(Path(name).stem, [])
            real_targets = [t for t in targets if t != src]
            if real_targets:
                for t in real_targets:
                    record(t)
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
                if resolved != src and resolved in inbound_hub:
                    record(resolved)
            else:
                broken_md.append((rel(src), target))

    inbound = {f: inbound_hub[f] + inbound_content[f] for f in files}

    def is_exempt(f: Path) -> bool:
        if f.name in ORPHAN_EXEMPT_NAMES:
            return True
        rb = rel_base(f)
        return any(rb.startswith(p) for p in ORPHAN_EXEMPT_PREFIXES)

    orphans: list[str] = []
    weak_nodes: list[str] = []
    hist = {"0": 0, "1": 0, "2": 0, "3+": 0}
    content_total = woven = 0
    for f in files:
        if is_exempt(f):
            continue
        content_total += 1
        deg = inbound[f]
        hist["0" if deg == 0 else "1" if deg == 1 else "2" if deg == 2 else "3+"] += 1
        if inbound_content[f] > 0:
            woven += 1
        if deg == 0:
            orphans.append(rel(f))            # no inbound at all
        elif inbound_content[f] == 0:
            weak_nodes.append(rel(f))          # only MOC/hub inbound -> lonely spoke

    orphans.sort()
    weak_nodes.sort()
    broken_md.sort()
    dangling_wiki.sort()

    def ratio(n: int, d: int) -> float:
        return round(n / d, 3) if d else 0.0

    metrics = {
        "content_docs": content_total,
        "woven": woven,                        # has >=1 contextual (non-MOC) inbound
        "weak": len(weak_nodes),               # only MOC inbound (folder spoke)
        "orphans": len(orphans),
        "woven_ratio": ratio(woven, content_total),
        "total_edges": total_edges,
        "hub_edge_ratio": ratio(hub_edges, total_edges),
        "cross_folder_link_ratio": ratio(cross_folder_edges, total_edges),
        "indegree_histogram": hist,
    }

    result = {
        "base": base_label,
        "scanned": len(files),
        "broken_md_links": [{"source": s, "target": t} for s, t in broken_md],
        "dangling_wikilinks": [{"source": s, "name": n} for s, n in dangling_wiki],
        "orphans": orphans,
        "weak_nodes": weak_nodes,
        "metrics": metrics,
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
    if show_all or weak_nodes:
        m = metrics
        lines.append(
            f"  [density] woven {m['woven']}/{m['content_docs']} "
            f"({m['woven_ratio']:.0%}) | weak/spoke {m['weak']} | "
            f"cross-folder links {m['cross_folder_link_ratio']:.0%}")
    if show_all and weak_nodes:
        lines.append(f"  [weak] {len(weak_nodes)} lonely spoke(s) (only MOC-inbound - weave a contextual link):")
        lines += [f"     - {w}" for w in weak_nodes]
    if not has_issues:
        lines.append("  [ok] no broken links / orphans.")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
