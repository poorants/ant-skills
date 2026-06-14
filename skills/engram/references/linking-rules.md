# Networked Knowledge — Linking Rules

The rules for the **logical link layer** engram lays on top of PARA folders
(physical classification). They grow the vault into a brain-like network of
connected documents. Apply them whenever creating, moving, or reviewing docs.
The target is the documents under the resolved PARA base.

## Core idea: Networked PARA

PARA folders alone isolate information inside folders. Adding bi-directional
links combines **physical classification (folders)** with **logical
relationships (links)**.

- **Folders (physical)**: own the document's lifecycle and governance (who edits
  it). Projects / Areas / Resources / Archives.
- **Links (logical)**: connect documents by context regardless of which folder
  they live in, forming a web that crosses folder boundaries.

## Linking rules

### 1. Bi-directional linking

- Use `[[filename]]` (Obsidian wikilink) or `[display text](relative/path.md)`
  (markdown relative link). Prefer wikilinks so nodes are recognized in Graph
  View and backlinks activate.
- Wikilinks resolve by filename (stem), so moving a folder does not break them.
  They are fragile to filename changes, so keep names stable.

### 2. Prefer contextual links

Avoid dumping a "related documents" list at the bottom of a file. Weave links
naturally into the prose.

- Bad: a trailing `Related: [[foo]]` list.
- Good: "the encryption module must follow the national standard
  [[nis-kcmvp-petracrypto]]" — the link sits inside the sentence.

### 3. MOC (Map of Content) = hub node

Each folder's `README.md` acts as the default MOC: an entry dashboard that ties
the folder's individual notes together by logical order/category. When you add a
document, add a one-line link to it from that folder's README MOC so it is
reachable from the entry point.

## Knowledge-network management rules

1. **Atomic note (one point)**: a document covers exactly one concept, rule, or
   project. When a topic expands, create a new document and link to it. Oversized
   documents blur the propagation power of links.

   But **atomic means "one linkable idea," not "the smallest possible fragment."**
   Discernment test: *would you ever link to or reuse this concept independently
   from somewhere else?* If yes, it deserves its own note; if it only ever appears
   in one context, keep it inline. Shattering everything into tiny stubs is
   over-structuring (see Pitfalls) — it adds navigation overhead and loses
   cohesion. Some documents are legitimately one concept even when long: a single
   spec, a meeting log (one event, chronological), a reference table.

   **Migrate opportunistically, never big-bang.** Don't rewrite the whole vault at
   once (it invites link rot and wasted effort). Apply atomicity to new notes, and
   split an existing bloated doc only when you're already editing it and notice it
   packs several independently-linkable concepts — then split and wire the links.

2. **No orphan nodes**: every newly added document must receive at least one
   inbound link from an existing MOC (`README.md`) or a related document.
   Unlinked knowledge gets lost. (`engram_lint.py` detects orphans.)

3. **Ground reference material**: when citing external research (`resources/`),
   link it to an `areas/`/`projects/` document that holds your own
   interpretation, grounding the external knowledge in your network.

## Pitfalls (what practitioners warn about)

- **Collector's fallacy**: mistaking *collecting* information for *knowing* it.
  Material that is only collected has not been read. Inboxes (seeds, ideas, etc.)
  become a dead pile without a periodic ritual to digest and promote them.
- **Over-structuring**: when maintaining the system becomes the goal and actual
  thinking/output stops. Do not pile on excessive rules, tags, or numbers.
- **Link rot**: links breaking due to filename changes. Prevent it with stable
  naming and periodic `engram_lint.py` checks.

## Order of operations (when working on docs)

1. After creating or moving a document, weave contextual links into the prose.
2. Add a one-line entry to the folder's `README.md` (MOC) to avoid orphans.
3. Before finishing, run `engram_lint.py` to find and repair broken links and
   orphans.
