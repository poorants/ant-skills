# Absorption Rulebook — detail

The four gates in SKILL.md are the contract. This file is the working detail: how to
read each gate, worked examples, and the edge cases that trip people up. The gates
exist because **the hard part of a self-reinforcing harness is not the plumbing — it
is deciding what deserves to become permanent.** Get this wrong and the harness
either learns nothing (too strict) or calcifies around noise (too loose).

## The three layers of a correction

Every correction you make is one of three things. Only the first two are absorbable.

1. **Objective** — "this doesn't compile / the test is missing / you didn't do what I
   asked / wrong format". Checkable. Often better expressed as a *signal* (a test, a
   lint rule) than a prose rule, but a prose rule is fine when no cheap signal exists.
2. **Unwritten convention** — "we always name it this way / we don't use that
   pattern / error messages are in Korean". A rule that lives in your head and hasn't
   been written down. **This is reflex's sweet spot.**
3. **Taste** — "this paragraph reads better / put it here instead / this feels off".
   Context-bound judgment that won't transfer cleanly to the next case. **Never
   absorb.** It stays the human's call; encoding it makes the agent confidently wrong
   in cases where your taste would actually differ.

Worked example — the request "add email validation to the login form" drew four
corrections:

| Correction | Layer | Absorb? |
|---|---|---|
| "empty string passes — fix it" | objective | maybe (better as a test) |
| "you didn't write a test" | objective/convention | yes → "new logic ships with tests in the same change" |
| "error message is English; we use Korean" | unwritten convention | **yes** → the textbook reflex rule |
| "move the validation above the form" | taste | **no** |

Three of four were not intuition. The Korean-message one is the clean absorb: a
standing convention you'd otherwise repeat forever.

## Gate 1 — Durable, not taste

Test: *"If a similar situation comes up next week, does this exact correction still
apply — without me looking at the specifics?"*
- Yes, mechanically → durable. Absorb.
- "Depends on the specifics / I'd want to judge case by case" → taste. Drop.

Tie-breaker: **drop when unsure.** Asymmetric cost — a missed rule costs you one more
correction later; a wrong rule silently misfires on every future session where your
real judgment would have differed. Under-absorbing is recoverable; over-absorbing
rots quietly.

## Gate 2 — Generalizable, not incidental

Test: *"Can I state this as a rule without naming this one file / value / number?"*
- "Error messages are in Korean" → generalizes. Keep.
- "Line 42 of auth.ts should be 500ms not 300ms" → cannot be stated without the
  specific instance → overfit. Drop, or **narrow to the general form** if one exists
  ("default network timeouts to 500ms" — if that's actually a standing preference).

A rule you can only phrase by quoting the instance is a fix, not a rule.

## Gate 3 — Not already covered

Before adding, scan: the existing `reflex` block, the repo's `CLAUDE.md`, and any
convention docs (e.g. `.code-convention/`, `AGENTS.md`). 
- Exact restatement of an existing rule → drop.
- A sharper/expanded version of an existing rule → **edit that rule in place**, don't
  add a near-duplicate. Two rules saying almost the same thing is how the block rots.
- reflex and the `code-convention` skill can overlap: if the project already runs
  `code-convention`, durable *code* conventions belong there (its committed
  contract); reflex is for the lighter, faster-moving operating preferences. Don't
  duplicate a code-convention rule into the reflex block.

## Gate 4 — No silent conflict

If the candidate contradicts an existing learned rule (or an existing CLAUDE.md
rule): **stop and surface it.** Show both, ask the user which wins. Resolving a
conflict silently — overwriting or adding the opposite — is the worst failure: the
harness now contains two contradictory instructions and the agent's behavior becomes
nondeterministic. A conflict is a signal that context changed; let the human say how.

## Frequency: how many times before absorbing?

- **Explicit flag** ("이건 기억해 / always …"): absorb on the first occurrence — the
  user told you it's standing.
- **Inferred from corrections**: the signal is **the second occurrence**. The first
  time, just fix it. The second time you reach for the same correction, that's
  repetition → propose absorbing. (One occurrence is indistinguishable from a one-off;
  waiting for the third over-collects corrections you could have prevented.)

## What to drop without a second thought

- One-off taste and aesthetic calls.
- Anything you can only state by quoting a specific line/value.
- Restatements of rules already written somewhere the agent reads.
- Project-specific facts that belong in **engram** (knowledge/decisions to revisit),
  not as an operating rule. reflex = "how to act"; engram = "what to know". If it's a
  fact to remember rather than a behavior to repeat, route it to engram instead.
