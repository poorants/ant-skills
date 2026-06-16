#!/usr/bin/env python3
"""engram weave finder (the muscle behind the Weave Workflow).

`engram_lint.py` *measures* how neural the network is (woven_ratio, weak nodes).
This script *finds the concrete moves* that raise it — turning lonely spokes
(docs with only a MOC inbound) into woven nodes reachable by context.

It surfaces two kinds of high-leverage candidates; the skill (the intelligence)
judges which are real and weaves them, never blindly applying them:

  1. missing_links — a document mentions another note's concept (by its title or
     filename) in prose but does NOT link to it yet. Adding that link gives the
     target a *contextual* inbound (woven), often across a folder boundary. This
     is the single cheapest way to dissolve a spoke. Candidates whose target is
     currently a weak/spoke node are ranked first (highest impact).

  2. concept_candidates — a term recurs across several docs in DIFFERENT folders
     but has no note of its own. Promoting it to a shared atomic concept note
     (resources/ or areas/) and routing those docs through it creates the
     cross-folder connective tissue a star topology lacks (Matuschak: notes
     should be concept-oriented AND densely linked).

Output is advisory only (exit 0, never mutates files). Be selective — forcing
links is over-structuring. See SKILL.md "Weave Workflow" and linking-rules.md.

Usage (from the target repo root):
    python <skill>/scripts/weave_candidates.py            # human summary
    python <skill>/scripts/weave_candidates.py --json     # machine JSON
    python <skill>/scripts/weave_candidates.py --base .   # force base
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path.cwd()
PARA_CATEGORIES = ("projects", "areas", "resources", "archives")
HUB_NAMES = {"README.md", "_index.md", "index.md", "CLAUDE.md", "MEMORY.md"}

WIKILINK_RE = re.compile(r"(?<!!)\[\[([^\]\n]+?)\]\]")
MDLINK_RE = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
BOLD_RE = re.compile(r"\*\*([^*\n]{2,40})\*\*")
DQUOTE_RE = re.compile(r"[\"“]([^\"“”\n]{2,40})[\"”]")
FORMAT_STRIP_RE = re.compile(r"[`*_\[\]]")

MISSING_LINK_CAP = 50
CONCEPT_CAP = 30


def parse_base_arg() -> str | None:
    for i, a in enumerate(sys.argv):
        if a == "--base" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
        if a.startswith("--base="):
            return a.split("=", 1)[1]
    return None


def resolve_base() -> tuple[Path, str]:
    arg = parse_base_arg()
    if arg is not None:
        return (REPO / arg).resolve(), arg
    if (REPO / "brain").is_dir():
        return (REPO / "brain").resolve(), "brain"
    if (REPO / "para").is_dir():
        return (REPO / "para").resolve(), "para"
    if any((REPO / c).is_dir() for c in PARA_CATEGORIES):
        return REPO, "."
    return (REPO / "brain").resolve(), "brain"


def strip_code(text: str) -> str:
    return INLINE_CODE_RE.sub("", FENCE_RE.sub("", text))


def is_excluded(parts: tuple[str, ...]) -> bool:
    return any(p == "node_modules" or (p.startswith(".") and len(p) > 1) for p in parts)


def is_specific(phrase: str) -> bool:
    """Keep only anchors specific enough to avoid false matches: multi-word, or a
    non-ASCII (e.g. Korean) term. Single common English words are too noisy."""
    p = phrase.strip()
    if len(p) < 4:
        return False
    if " " in p:                       # multi-word phrase
        return True
    return any(ord(c) > 127 for c in p)  # non-ASCII single token (CJK, etc.)


def main() -> int:
    # Output (paths, Korean titles, JSON) is UTF-8 regardless of the console code
    # page (e.g. cp949 on Korean Windows) so non-ASCII never crashes the run.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    as_json = "--json" in sys.argv
    base, base_label = resolve_base()

    if not base.is_dir():
        out = {"base": base_label, "missing_links": [], "concept_candidates": [],
               "note": "base directory not found"}
        print(json.dumps(out, ensure_ascii=False, indent=2) if as_json
              else f"[engram] base '{base_label}' not found.")
        return 0

    files = [p for p in base.rglob("*.md") if not is_excluded(p.relative_to(base).parts)]

    def rel(p: Path) -> str:
        try:
            return p.relative_to(REPO).as_posix()
        except ValueError:
            return p.as_posix()

    def top_folder(p: Path) -> str:
        # immediate parent dir relative to base = the "topic folder". Cross-folder
        # is judged here, not at the PARA top, so a concept recurring across
        # areas/management and areas/meeting-logs counts as genuinely cross-topic.
        return p.relative_to(base).parent.as_posix()

    by_stem: dict[str, list[Path]] = {}
    for f in files:
        by_stem.setdefault(f.stem, []).append(f)

    texts: dict[Path, str] = {}
    anchors: dict[Path, set[str]] = {}     # note -> phrases that should link to it
    outbound: dict[Path, set[Path]] = defaultdict(set)
    inbound_content: dict[Path, int] = {f: 0 for f in files}
    existing_node_terms: set[str] = set()  # lowercased stems + titles already noded

    for f in files:
        try:
            raw = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            raw = ""
        text = strip_code(raw)
        texts[f] = text

        anchor_set: set[str] = set()
        stem_phrase = f.stem.replace("-", " ").strip()
        if is_specific(stem_phrase):
            anchor_set.add(stem_phrase)
            existing_node_terms.add(stem_phrase.lower())
        h1 = H1_RE.search(text)
        if h1:
            title = FORMAT_STRIP_RE.sub("", h1.group(1)).strip()
            existing_node_terms.add(title.lower())
            if is_specific(title) and len(title) <= 40:
                anchor_set.add(title)
        if f.name not in HUB_NAMES:
            anchors[f] = anchor_set

        # outbound links (resolved paths + wikilink stems)
        for stem in (s.split("|", 1)[0].split("#", 1)[0].strip() for s in WIKILINK_RE.findall(text)):
            for t in by_stem.get(Path(stem).stem, []):
                if t != f:
                    outbound[f].add(t)
        for tgt in MDLINK_RE.findall(text):
            if tgt.startswith(("http://", "https://", "mailto:", "#", "tel:")):
                continue
            clean = tgt.split("#", 1)[0].split("?", 1)[0]
            if clean.endswith(".md"):
                resolved = (f.parent / clean).resolve()
                if resolved.exists() and resolved != f:
                    outbound[f].add(resolved)

    # contextual inbound (links FROM a non-hub doc) -> spoke detection
    for src, dsts in outbound.items():
        if src.name in HUB_NAMES:
            continue
        for d in dsts:
            if d in inbound_content:
                inbound_content[d] += 1

    # 1. missing links: doc D mentions note N's anchor but does not link to it
    missing: list[dict] = []
    for note, anchor_set in anchors.items():
        if not anchor_set:
            continue
        target_is_spoke = inbound_content.get(note, 0) == 0
        mentioned_in: list[str] = []
        for d in files:
            if d is note or d.name in HUB_NAMES or note in outbound[d]:
                continue
            low = texts[d].lower()
            if any(a.lower() in low for a in anchor_set):
                mentioned_in.append(rel(d))
        if mentioned_in:
            missing.append({
                "target": rel(note),
                "target_is_spoke": target_is_spoke,
                "anchor": sorted(anchor_set)[0],
                "mentioned_in": sorted(mentioned_in)[:8],
                "mentions": len(mentioned_in),
            })
    # highest leverage first: dissolves a spoke, then by how many docs mention it
    missing.sort(key=lambda m: (not m["target_is_spoke"], -m["mentions"], m["target"]))

    # 2. concept candidates: bold/quoted terms recurring across >=2 folders, no node
    term_docs: dict[str, set[Path]] = defaultdict(set)
    for f, text in texts.items():
        for m in BOLD_RE.findall(text) + DQUOTE_RE.findall(text):
            term = FORMAT_STRIP_RE.sub("", m).strip()
            if is_specific(term) and term.lower() not in existing_node_terms:
                term_docs[term].add(f)
    concepts: list[dict] = []
    for term, docset in term_docs.items():
        folders = {top_folder(d) for d in docset}
        if len(docset) >= 3 and len(folders) >= 2:
            concepts.append({
                "phrase": term,
                "doc_count": len(docset),
                "folders": sorted(folders),
                "sample_docs": sorted(rel(d) for d in docset)[:6],
            })
    concepts.sort(key=lambda c: (-len(c["folders"]), -c["doc_count"], c["phrase"]))

    spoke_fixes = sum(1 for m in missing if m["target_is_spoke"])
    result = {
        "base": base_label,
        "scanned": len(files),
        "summary": {
            "missing_links": len(missing),
            "missing_links_that_dissolve_a_spoke": spoke_fixes,
            "concept_candidates": len(concepts),
        },
        "missing_links": missing[:MISSING_LINK_CAP],
        "concept_candidates": concepts[:CONCEPT_CAP],
    }

    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    where = "root" if base_label == "." else f"{base_label}/"
    lines = [f"[engram] weave candidates ({len(files)} docs / {where})",
             f"  missing links: {len(missing)} ({spoke_fixes} dissolve a spoke) | "
             f"concept candidates: {len(concepts)}"]
    if missing:
        lines.append("  -- top missing links (add a contextual link target<-source) --")
        for m in missing[:15]:
            tag = "[spoke]" if m["target_is_spoke"] else "[      ]"
            lines.append(f"    {tag} {m['target']}  <- mentioned in {m['mentions']} doc(s) "
                         f"(e.g. {m['mentioned_in'][0]})")
    if concepts:
        lines.append("  -- top shared-concept candidates (promote to a node) --")
        for c in concepts[:10]:
            lines.append(f"    \"{c['phrase']}\" - {c['doc_count']} docs across "
                         f"{len(c['folders'])} folders ({', '.join(c['folders'])})")
    if not missing and not concepts:
        lines.append("  [ok] no obvious weave candidates found.")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
