# Session Handoff Workflow — detail

The **forward** counterpart to the Capture loop and Session Update Review (which
look *back* at what the brain gained). Used mid-session, when the context window
is filling up (~half+) and the user wants to continue the *same* work in a fresh
session without losing state. Command/natural-language triggered — **never a
hook**; it's a deliberate act, distinct from the sign-off wrap-up hook.

Triggers: "다음 세션에 이어가게 준비해", "세션 핸드오프", "다음 세션 이어가기 준비",
"prepare handoff", "continue in next session".

## Two artifacts — the second is subordinate to the first

1. **The handoff doc (body, carries the weight)** — a single **rolling** doc at
   `<base>/projects/<repo>/handoff.md`. Route to the **local** `base` in hybrid
   mode — session state is code-coupled and never belongs in the shared brain.
   **One per work-stream, overwritten every time** — never date-stamped, never
   accumulated. It is the living *state board* of the current work, not a log.
2. **The continuation prompt (a thin pointer)** — a short, copy-able code block
   the user pastes into the next session. It **points at the handoff doc; it does
   not inline the context**. This is the whole reason to build this on engram (see
   "Why a pointer" below) — get it wrong and it is just a text dump.

## Steps

1. **Resolve base** (Path Resolution). Hybrid → local `base`. Ensure
   `projects/<repo>/` exists (Init if needed).
2. **Write/overwrite `handoff.md`** (plain markdown, start with an H1, no
   frontmatter):
   - `## Goal` — the work-stream's objective, 1–2 lines.
   - `## Done` — what *this* session accomplished (terse bullets).
   - `## Current state` — where things stand now (branch, what works / what's
     broken).
   - `## Next steps` — the ordered to-do the next session resumes from. **The
     single most important section.**
   - `## Key files & decisions` — files in play + decisions already settled (so
     the next session does not re-litigate them). Weave `[[wikilinks]]` to related
     brain notes here, so the next session pulls connected knowledge for free.
   - `## Open questions` — unresolved forks.
3. **Connect** — keep one inbound link from `projects/<repo>/README.md` (MOC) so
   the doc is not an orphan. Because the doc is rolling, this MOC link is stable
   across overwrites — wire it once.
4. **Emit the continuation prompt** as a fenced code block — a thin pointer, in
   the user's language. Substitute the resolved real path:
   ```
   엔그램 brain/projects/<repo>/handoff.md 읽고, "## Next steps" 부터 이어서 작업해.
   (그 문서 "## Key files & decisions"에 걸린 링크도 따라 읽어.)
   ```
5. **Stamp it as a snapshot** — close with one line: *"이 핸드오프는 지금 시점
   스냅샷이야. 더 작업하면 다시 떠."* A prompt emitted, then kept-working-past,
   becomes a lie.

## Lifecycle

`handoff.md` is *working state*, not durable knowledge — it deliberately bends the
**Brain boundary** (one rolling doc, the opposite of the accumulation that
principle guards against). When the work-stream finishes: distill any genuinely
durable concepts/decisions into proper notes via the **Capture loop**, then
**empty** `handoff.md` (leave a one-line "no active handoff") or archive the
project folder. Never let a dead handoff masquerade as live state.

## Why a pointer, not a dump

Inlining the whole context into the prompt throws away engram's entire value. A
short prompt that points at a brain doc lets the next session read the doc *and
follow its `[[wikilinks]]`* into connected knowledge, costs almost nothing to
paste, and keeps edits in one place (the doc) instead of a stale copied blob.
