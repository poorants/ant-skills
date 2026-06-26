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
   `.handoff/handoff.md`, a **project scratchpad at the repo root, outside the
   brain**. Session state is throwaway working state — it does not belong in the
   brain's link network, and it is git-ignored so it never gets committed.
   **One per work-stream, overwritten every time** — never date-stamped, never
   accumulated. It is the living *state board* of the current work, not a log.
2. **The continuation prompt (a thin pointer)** — a short, copy-able code block
   the user pastes into the next session. It **points at the handoff doc; it does
   not inline the context**. This is the whole reason to build this on engram (see
   "Why a pointer" below) — get it wrong and it is just a text dump.

## Steps

1. **Ensure the project scratchpad exists.** Create `.handoff/` at the repo root
   if missing. **Add `.handoff/` to `.gitignore`** if it is not already ignored
   (create `.gitignore` if the repo has none) — the handoff is throwaway state and
   must never be committed. No PARA base resolution is needed: the doc lives
   *outside* the brain.
2. **Write/overwrite `.handoff/handoff.md`** (plain markdown, start with an H1, no
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
     These wikilinks are *pointers the next session follows*, not lint-tracked
     links — the doc sits outside the lint base, so they are never flagged.
3. **No MOC link, no orphan check.** Because the doc lives outside the brain, the
   orphan rule does not apply — skip the MOC wiring entirely. The brain stays
   clean of working state.
4. **Emit the continuation prompt** as a fenced code block — a thin pointer, in
   the user's language:
   ```
   .handoff/handoff.md 읽고, "## Next steps" 부터 이어서 작업해.
   (그 문서 "## Key files & decisions"에 걸린 [[링크]]는 엔그램으로 따라 읽어.)
   ```
5. **Stamp it as a snapshot** — close with one line: *"이 핸드오프는 지금 시점
   스냅샷이야. 더 작업하면 다시 떠."* A prompt emitted, then kept-working-past,
   becomes a lie.

## Lifecycle

`.handoff/handoff.md` is *working state*, not durable knowledge — git-ignored and
deliberately kept **outside** the brain so the accumulation it represents (one
rolling doc, overwritten) never pollutes the knowledge base. When the work-stream
finishes: distill any genuinely durable concepts/decisions into proper brain notes
via the **Capture loop**, then **empty** `.handoff/handoff.md` (leave a one-line
"no active handoff") or delete `.handoff/`. Never let a dead handoff masquerade as
live state.

## Why a pointer, not a dump

Inlining the whole context into the prompt throws away engram's entire value. A
short prompt that points at the handoff doc lets the next session read the doc *and
follow its `[[wikilinks]]`* into connected brain knowledge, costs almost nothing to
paste, and keeps edits in one place (the doc) instead of a stale copied blob.
