# Weave Workflow — raise neural density (full procedure)

The deepening counterpart to Link & Connect. Link & Connect removes **orphans**
(gets every doc ≥1 inbound link); Weave removes **lonely spokes** — docs whose
only inbound is their folder MOC, so the graph is a star, not a brain. See
[linking-rules.md](linking-rules.md) "Connected vs woven" and rule 3 "No lonely
spokes" before starting.

**When**: orphans are handled but the brain still feels like isolated folders —
the user wants it "more connected / more neural", or `engram_lint.py` reports a low
`woven_ratio` and many `weak_nodes`.

## Steps

1. **Measure** — run `engram_lint.py --json` and read `metrics` (`woven_ratio`,
   `cross_folder_link_ratio`) and the `weak_nodes` list. This is the baseline to
   beat. (orphans=0 with `woven_ratio` near zero = a pristine star.)

2. **Find candidates** — run the muscle:
   ```bash
   python "<skill_dir>/scripts/weave_candidates.py" --json
   ```
   `<skill_dir>` is the dir holding SKILL.md; as a plugin,
   `${CLAUDE_PLUGIN_ROOT}/skills/engram/scripts/weave_candidates.py`. It returns two
   advisory lists (never auto-applied):
   - **missing_links** — a doc already *mentions* another note (by its title or
     filename) in prose but doesn't link it. Adding that link gives the target a
     contextual inbound: the cheapest spoke-dissolver. Entries with
     `target_is_spoke: true` are ranked first (each converts a weak node to woven).
     `mentioned_in` lists where the unlinked mention sits.
   - **concept_candidates** — a term recurs across docs in **different folders**
     with no note of its own. Promote it to a shared atomic concept note
     (`resources/` or `areas/`) and route those docs through it; this builds the
     cross-folder connective tissue a star lacks (Matuschak: concept-oriented AND
     densely linked).

3. **Judge, then weave** — the model decides which candidates are *real*:
   - missing_links → weave the link into the prose **where the mention already
     sits** (contextual, not a trailing "related" list).
   - concept_candidates → if worth promoting, create the concept note via the
     Create Workflow, then link the referring docs to it contextually.
   - **Stay selective.** Skip forced or trivial matches; a spoke that genuinely
     relates to nothing stays an acknowledged leaf. Forcing links is the failure
     mode here (over-structuring), not a win.

4. **Re-measure & report** — re-run `engram_lint.py --json`; report `woven_ratio`
   and `weak_nodes` before→after, plus the links woven and concept notes created.

## Caveat — respect the brain boundary

`weave_candidates.py` can surface clusters that are really **external deliverables**
with their own lifecycle (e.g. generated resumes/portfolios under a
`profiles/output/` tree). Don't over-weave those — if anything they are *separation*
candidates (the user's call; see SKILL.md "Brain boundary"), not density targets.

## Relationship to the metrics

`woven_ratio` = content docs with ≥1 contextual (non-MOC) inbound / all content
docs. `cross_folder_link_ratio` = links crossing a top-folder boundary / all links.
Both rise as you weave; `weak` (the spoke count) falls. These are the scoreboard
for whether the brain is getting more neural over time, beyond the pass/fail orphan
check.
