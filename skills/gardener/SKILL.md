---
name: gardener
description: >
  Tends the agent harness like a garden: grows rules that prove their worth UP the
  enforcement ladder (soft preference → CLAUDE.md rule → mechanical hook) and prunes
  the overgrown (over-engineered gates, dead rules, redundant skills) back down or
  out. Bidirectional tier curation, not one-way capture — the value is as much in
  demoting/retiring over-engineering as in promoting what recurs. A promotion gate
  decides what's durable enough to grow and which tier it earns; a prune review
  catches what has calcified. Every change is proposed for approval. Sibling of engram
  (engram curates knowledge; gardener curates how-to-work). Use to grow a repeated
  correction into a rule or hook, prune learned rules and over-built gates, or
  right-size the harness. Triggers (any language): 이건 기억해, 규칙으로 만들어,
  이거 훅으로, 또 같은 걸 고치네, 오버엔지니어링, 규칙 정리, 하니스 정리, remember this,
  make it a rule, promote to a hook, prune the rules, this is over-engineered, tidy
  the harness.
---

# gardener — Harness Tier Curator

gardener tends the **agent harness** — the rules, hooks, and skills that shape how the
agent works — like a garden: it **grows** what proves valuable and **prunes** what
overgrows. It is **loop engineering applied to the harness itself**, but bidirectional
on purpose. Capturing a repeated correction is only half the job; the other half —
the one nothing else does — is catching when a rule, gate, or skill has become **dead
weight or over-engineering** and pulling it back down.

It is the operating-rules sibling of **engram**: engram curates *knowledge* into a
linked document brain; gardener curates *how to work* into the harness. Same
gardener's discipline — grow the strong, prune the weak — different target.

**The core idea: a rule lives at a strength tier, and the goal is the RIGHT tier —
not the highest.** Under-growing means re-correcting forever; over-growing (every
preference a blocking hook) calcifies the harness so it fights you. gardener moves
each rule to where it belongs and removes what no longer earns its place.

## The rule-strength ladder (the model everything hangs on)

| Tier | Form | Enforcement | Where it lives |
|---|---|---|---|
| **T1 soft** | a hint / preference / background recall | the agent *may* follow it | personal memory, session context |
| **T2 documented** | a written rule | the agent *should* follow it (still skippable) | a marked block in `CLAUDE.md` |
| **T3 enforced** | a hook / gate that **blocks on violation** | deterministic — *cannot* be skipped | `.claude/hooks/` + `settings.json` |

Loop engineering = moving a rule to the tier it has earned: **up** when it recurs and
proves load-bearing, **down/out** when it has calcified or gone dead. Full ladder,
the checkable→hook decision, and the pruning criteria: load
[references/tiers-and-pruning.md](references/tiers-and-pruning.md).

## Two operations

- **Grow (promote ↑)** — a recurring, generalizable pattern earns a higher tier.
- **Prune (demote / retire ↓)** — an over-built gate, a never-firing rule, a
  redundant skill gets pulled down a tier or removed. **This is the value center** —
  capture and enforcement already have owners (memory, hooks); *nobody* routinely
  asks "is this still worth its weight?".

## Grow workflow (promote ↑)

1. **Identify** the candidate — a correction just repeated, an explicit "remember
   this", or a rule that keeps getting hand-enforced.
2. **Promotion gate.** Pass all four gates or drop it (name the gate that failed).
   Detail + worked examples: [references/promotion-gate.md](references/promotion-gate.md).
   1. **Durable, not taste** — applies to future similar cases without re-judging.
   2. **Generalizable, not incidental** — stateable without naming this one file/value.
   3. **Not already covered** — dedup against existing rules, hooks, CLAUDE.md,
      convention docs. Sharpen an existing rule rather than add a twin.
   4. **No silent conflict** — if it contradicts an existing rule, surface it; never
      overwrite silently.
3. **Pick the tier it earned** (the decision that makes gardener more than a note-taker):
   - **Mechanically checkable AND worth enforcing** → **T3**: propose a hook (scaffold
     it; wire it in `settings.json`). A rule a script can verify deterministically
     belongs at the tier that can't be skipped — that's where a mature harness's power
     lives.
   - **Needs judgment to apply** → **T2**: a line in the `gardener` CLAUDE.md block.
   - **Soft / personal / one-off-ish** → leave at **T1** (or drop). Don't over-promote.
4. **Scope it** — repo-local by default; global only on the ≥2-repo signal. See
   [references/scope-routing.md](references/scope-routing.md).
5. **Propose, don't auto-write.** Show the exact target + the diff (a CLAUDE.md line,
   or a hook file + settings wiring). Write only after approval (standing approval —
   "그냥 알아서" — is fine, but default to proposing).
6. **Report**: what grew, to which tier, where, and why (origin).

## Prune workflow (demote / retire ↓) — the part nothing else does

**When:** a periodic review, the block/hooks have grown, or the user says "this is
over-engineered / tidy the harness / 규칙 정리".

Walk the harness across tiers and flag debt:

- **T2/T1 rules** — **stale** (the context it referenced is gone), **never-fired**
  (you can't recall it preventing a correction), **redundant** (now covered by a hook
  or a convention doc), **conflicting** → demote or retire.
- **T3 hooks/gates** — **only-ever-passes** (never actually blocked anything real),
  **false-positive-prone** (more friction than failures prevented), **superseded** →
  demote to a T2 rule or retire. An enforcement gate that never catches anything is
  ceremony, not safety.
- **Skills** — **redundant** with another skill or a one-liner, **unused**, **dormant**
  → propose retirement.

Over-engineering signals (full list in tiers-and-pruning.md): a gate that only ever
passes · a rule nobody recalls firing · two skills doing one job · ceremony with no
caught failure. **Propose** demotions/retirements — never auto-remove; the date+origin
on each rule keeps the history legible.

## What gardener manages — the marked block

Grown T2 rules live in one idempotent block in the target `CLAUDE.md`, never scattered:

```
<!-- gardener:start -->
## Learned rules (gardener)
- [2026-06-23] 브랜치 push 는 `-u origin <branch>` 명시. <!-- origin: 반복 교정 ×2 · T2 -->
- [2026-06-23] 코드 변경 플랜은 DoD 1–3 포함. <!-- origin: 반복 → T3 hook validate-plan.sh; rule kept as the spec -->
<!-- gardener:end -->
```

One imperative line + date + an `origin` comment (why it exists, and if it graduated
to a hook, which one). Markers make the block **identifiable, reversible, prunable**.
A T3 promotion writes the hook **and** leaves a one-line T2 entry pointing at it (the
rule is the spec; the hook is the enforcement). Never write a learned rule outside the
block.

## Triggers & the capture loop

`scripts/gardener_reflect.py` (wired via `hooks/gardener-hooks.json`) is a **trigger,
not the engine** — a shell hook can't judge durable-vs-taste or worth-a-hook; the
model does, via this skill.

1. **Explicit flag** ("이건 기억해 / 규칙으로 만들어 / 이거 훅으로 / remember this") →
   run Grow immediately.
2. **Repeated correction** — the *second* time you reach for the same correction →
   propose growing it.
3. **Wrap-up / periodic** — at session end or on a throttled backstop, reflect for
   both directions: corrections worth growing **and** rules/gates worth pruning.

Env knobs: `GARDENER_DISABLE=1`, `GARDENER_COOLDOWN_MIN` (Stop cooldown, default 60),
`GARDENER_REMEMBER_PHRASES`. The hook never fails a session (errors exit 0).

## Rules

1. **Bidirectional.** Promotion *and* pruning. The harness should get **sharper, not
   just bigger** — every session that only adds rules is drifting toward calcification.
2. **Right tier, not highest tier.** Over-promotion (everything a blocking hook)
   rigidifies as badly as under-promotion leaves you re-correcting. Checkable + worth
   it → hook; needs judgment → rule; soft/one-off → leave it.
3. **Prune is first-class.** A gate that never blocks and a rule nobody recalls are
   debt. Surface them; don't let the harness accrete.
4. **Propose before writing.** Outward, semi-permanent change to how the agent
   behaves — show the diff, get approval (standing approval excepted).
5. **Reversible always.** Date + origin, in the marked block (rules) or as a tracked
   hook file (gates). Anything grown can be traced and pruned.
6. **Default local, promote across repos conservatively.** Repo-local first; global
   only on cross-repo (≥2) evidence. Promote, don't homogenize.
7. **Drop / keep-soft when unsure.** A missed rule costs one correction; a wrong rule
   or an over-built gate quietly taxes every future session. Bias toward the lighter
   tier.
