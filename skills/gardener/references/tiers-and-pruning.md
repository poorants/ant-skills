# Tiers & Pruning — detail

The SKILL.md ladder is the contract. This file is the working detail: how to read
each tier, the checkable→hook decision that sets gardener apart, and the pruning
criteria — the half of the job nothing else does.

## The rule-strength ladder, in full

A rule's "strength" is **how hard it is to ignore**, and strength has a cost:

| Tier | Form | Ignorable? | Cost to carry | Best for |
|---|---|---|---|---|
| **T1 soft** | preference, background recall (personal memory, session note) | freely | ~0 — invisible until recalled | one-off taste, personal style, low-stakes hints |
| **T2 documented** | a written rule in a `CLAUDE.md` block | by an inattentive pass | small — a line read every session | judgment rules ("error messages in Korean") a script can't check |
| **T3 enforced** | a hook/gate that exits non-zero on violation | not at all | real — maintenance + friction on every run it gates | mechanically checkable, load-bearing invariants ("plan must list the DoD") |

The mistake in both directions:
- **Under-leveling**: keeping a load-bearing, checkable rule at T2 (prose) means it
  gets skipped on a bad day and you re-correct. It earned a hook; give it one.
- **Over-leveling**: making every preference a T3 hook means the harness blocks you
  constantly, accretes maintenance, and fires false positives until you start
  bypassing it — at which point it protects nothing. **An ignored gate is worse than
  no gate**, because it reads as safety while providing none.

The goal is always the *lowest tier that actually holds the rule* — not the highest.

## The checkable→hook decision (what makes gardener more than a note-taker)

When a candidate passes the promotion gate, decide its tier with two questions:

1. **Can a script verify it deterministically?** ("plan text contains the DoD
   checklist" — yes. "this reads better" — no. "error strings aren't English" — mostly,
   with a heuristic.)
2. **Is it load-bearing enough to be worth blocking on?** (A violation that ships a
   bug or breaks a release — yes. A cosmetic nicety — no.)

- **Yes + Yes → T3.** Scaffold a hook (a small script that exits non-zero on
  violation) and wire it in `settings.json` under the right event (`PreToolUse`,
  `Stop`, etc.). Leave a one-line T2 entry in the gardener block pointing at the hook:
  the rule is the *spec*, the hook is the *enforcement*. Both, not either.
- **No to #1 (needs judgment) → T2.** A line in the gardener CLAUDE.md block. The
  model applies it; you can't mechanize it without false positives.
- **No to #2 (checkable but minor) → T2, or leave T1.** Don't pay enforcement cost for
  a rule whose violation doesn't hurt.

This is the graduation that a mature harness is built on: the strong loops in a
well-engineered repo are *hooks*, not prose. gardener's job is to notice when a prose
rule has earned that graduation — and to **stop short** when it hasn't.

## Pruning — demote / retire (the value center)

Capture has an owner (memory). Enforcement has an owner (hooks). **Nobody routinely
asks "is this still worth its weight?"** That question is gardener's reason to exist.
Run it on a periodic review, when the block/hooks have grown, or on "tidy the harness".

### What to look for, per tier

**T2/T1 rules** — flag and propose demote/retire when:
- **Stale** — the file/feature/context the rule referenced is gone.
- **Never-fired** — you cannot recall it ever preventing a correction. A rule that has
  never changed an outcome is noise the agent reads every session for nothing.
- **Redundant** — now covered by a T3 hook (the hook supersedes the prose), or by a
  committed convention doc (`.code-convention/`, `AGENTS.md`). Keep one source.
- **Conflicting** — contradicts another rule; surface, don't silently keep both.

**T3 hooks/gates** — flag and propose demote-to-T2 or retire when:
- **Only-ever-passes** — it has never actually blocked anything real. An enforcement
  gate that never catches a failure is **ceremony, not safety**: it costs friction and
  maintenance and buys nothing. Demote to a T2 reminder, or retire.
- **False-positive-prone** — it blocks correct work often enough that people route
  around it (`--no-verify`, skip flags). A bypassed gate is a lie; fix it or pull it.
- **Superseded** — the thing it guarded moved to a stronger/earlier check, or the risk
  is gone.

**Skills** — flag and propose retirement when:
- **Redundant** — another skill (or a one-line command) already does it.
- **Unused / dormant** — never invoked; its triggers never match real intent.
- **Mis-scoped** — its stated job overlaps something the harness already does better
  (the classic: a capture skill duplicating built-in memory).

### Over-engineering signals (the smell test)

- A gate in the pipeline that **only ever passes** — you've never seen it red.
- A rule **nobody recalls firing** — present for "completeness", read for nothing.
- **Two skills doing one job** — overlap that forces a "which one?" decision every time.
- **Ceremony with no caught failure** — a required step whose skipping has never once
  caused a problem.
- **Tier inflation** — a cosmetic preference enforced as a blocking hook.

When you see these, the harness is accreting. Propose pulling the item **down a tier
or out** — and say what you'd lose (usually: nothing but friction).

## Demote / retire mechanics

- **Never auto-remove.** Propose; the user confirms. Retiring is as outward as adding.
- **Rules**: delete the line from the gardener block — the date/origin in git history
  keeps the trail. If demoting T3→T2, remove the hook + its `settings.json` wiring and
  leave the prose rule with an origin note ("was a hook; demoted <date>, never fired").
- **Hooks**: remove the hook file and the `settings.json` entry together; note why.
- **Skills**: removal is a separate, deliberate change (a skill is more than a line) —
  propose it, point at the replacement, let the user run it.

## The balance to hold

Every session that only **adds** rules drifts toward calcification. A healthy harness
trends toward **fewer, sharper, higher-leverage** controls — a few real hooks that
catch real failures, a short prose block of genuine judgment rules, and not much else.
If the gardener block and the hook list only ever grow, the gardener isn't gardening.
