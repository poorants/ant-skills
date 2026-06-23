---
name: reflex
description: >
  Self-reinforcing agent harness — captures the corrections you repeat and absorbs
  the durable ones into the agent's operating rules (CLAUDE.md), so the harness
  strengthens itself instead of you re-correcting the same thing. Loop engineering
  applied to the harness: an absorption rulebook decides what to keep (durable rule
  vs one-off taste, generalizable, not duplicate, no conflict), routes each rule to
  the right scope (repo-local vs global, promote on cross-repo repetition), and
  proposes every write for approval. Sibling of engram: engram captures knowledge
  into linked docs, reflex captures how-to-work into the harness. Use to turn a
  repeated correction into a durable rule, remember a working preference, or
  review/prune learned rules. Matches intent in any language — e.g. "이건 기억해",
  "항상 이렇게 해", "규칙으로 만들어줘", "또 같은 걸 고치네", "학습한 규칙 정리",
  "remember this preference", "absorb this as a rule", "review learned rules".
---

# reflex — Self-Reinforcing Harness

reflex turns your **repeated corrections into durable rules** so the agent stops
making you say the same thing twice. It is **loop engineering applied to the harness
itself**: every time you intervene, that intervention is a signal that a rule is
missing — reflex captures it, judges whether it's worth keeping, and writes it where
the agent reads it next time.

It is the operating-rules sibling of **engram**: engram captures *knowledge* into a
linked document brain; reflex captures *how to work* into the harness. Same
capture-loop philosophy (the hooks are triggers, **the model is the engine** — a
shell hook can't judge what's worth keeping), different target.

**The boundary that matters:** reflex absorbs only what does **not** need your
intuition. Objective rules ("don't do X", "always run Y") and unwritten conventions
get absorbed; genuine *taste* (one-off "this reads better here") stays with you.
Absorbing taste makes the harness rigid — that's the failure mode, not the goal.

## What reflex manages

reflex owns a marked, idempotent block in the target `CLAUDE.md` — never free-form
edits scattered through the file:

```
<!-- reflex:start -->
## Learned rules (reflex)
- [2026-06-23] 에러 메시지는 한글로 작성한다. <!-- origin: repeated correction ×2 -->
- [2026-06-23] 새 컴포넌트엔 테스트를 같은 PR에 포함한다. <!-- origin: explicit, "항상" -->
<!-- reflex:end -->
```

Every rule is one imperative line + a date + an `origin` comment (why it exists).
The markers make the block **identifiable, reversible, and prunable** — exactly like
engram's portable pointer block. Never write a learned rule outside this block.

## When reflex activates (triggers)

1. **Explicit flag (primary, immediate)** — the user says "이건 기억해 / 항상 이렇게
   해 / 규칙으로 만들어 / remember this / from now on always …". Run the Absorb
   Workflow right away.
2. **Repeated correction** — you notice you're giving the *same kind* of correction a
   second time in a session (or the user says "또 같은 걸 고치네"). That repetition is
   the signal; propose absorbing it.
3. **Wrap-up reflection** — at session end, scan the session for interventions that
   recur or that the user clearly wants standing, and propose the worthwhile ones.

The capture-loop hooks (`reflex_reflect.py`, see below) fire 2 and 3 at the right
moment; 1 you act on directly. **Do not wait for a hook** — when a rule crystallizes
mid-work, run the Absorb Workflow then.

## The Absorption Rulebook (the heart)

A candidate correction/preference must pass **all four gates** to be absorbed. This
judgment is the whole skill — the plumbing is trivial, the decision is not. When a
candidate fails a gate, say which one and drop it. Full heuristics and worked
examples: load [references/absorption-rulebook.md](references/absorption-rulebook.md).

1. **Durable, not taste.** Would the *same* correction apply to a future similar
   situation regardless of this specific case? → durable rule (absorb). If it's
   "this particular spot reads better this way" → taste (**drop**; that stays the
   user's call). When unsure, lean drop — a missed rule costs one more correction; a
   wrong rule quietly distorts every future session.
2. **Generalizable, not incidental.** Can it be stated as a rule without naming this
   one file/value/number? If you can only express it by referencing the specific
   instance, it overfits → **drop or narrow** until it generalizes.
3. **Not already covered.** Dedup against existing learned rules *and* the repo's
   existing CLAUDE.md / convention docs. If it restates something already written →
   **drop**. If it sharpens an existing rule → edit that rule, don't add a twin.
4. **No silent conflict.** If it contradicts an existing rule, **do not overwrite** —
   surface the conflict to the user and let them resolve. Absorbing a contradiction
   silently corrupts the harness.

## Scope routing — repo-local vs global

reflex is a hybrid like an engram workspace: the same engine, output routed by the
rule's nature. Decide scope per absorbed rule; detail in
[references/scope-routing.md](references/scope-routing.md).

- **Repo-specific** (this codebase's convention, architecture, commands, naming) →
  the repo's `./CLAUDE.md`. **This is the default** — most corrections are
  code-coupled, and the rule should be reviewed/committed with the code.
- **Cross-cutting / personal style** (applies to any project) → the user-scope
  `~/.claude/CLAUDE.md`.
- **Promotion signal:** keep a rule local until the *same* rule has fired in **≥2
  repos** — that cross-repo repetition is the evidence to promote it to global. Never
  promote on a single repo's say-so (that homogenizes; engram's "promote, don't
  homogenize").

## Absorb Workflow

1. **Identify** the candidate (a correction just made, an explicit flag, or a
   reflection hit).
2. **Gate it** through the Absorption Rulebook. If it fails, name the gate and stop.
3. **Scope it** (repo-local default; global only on the promotion signal).
4. **Draft** the rule: one imperative line + today's date + an `origin` comment.
5. **Propose, don't auto-write.** Show the user the exact target file and the line to
   add (a small diff). Absorb only after they approve. (Approval can be standing —
   "그냥 알아서 넣어" — but default to proposing.)
6. **Write** into the `reflex:start/end` block of the target `CLAUDE.md` (create the
   block if absent; keep it idempotent — never duplicate a line).
7. **Report**: what was absorbed, where, and why (the origin).

## Review Workflow (bloat control)

**When:** the user asks to review/prune learned rules, or the block has grown large.
Knowledge that only accumulates becomes noise — a learned-rules block that never gets
pruned stops being read.

1. List the `reflex` block's rules with their origin/date.
2. Flag: **stale** (the code/context it referenced is gone), **never-fired** (you
   can't recall it ever preventing a correction), **redundant** (now covered by
   another rule or by an explicit convention doc), **conflicting**.
3. **Propose** merges/retirements — never auto-remove. Retire by deleting the line
   (the date/origin makes the history legible); the user confirms.
4. If a rule keeps firing across repos, propose **promoting** it to global.

## Capture loop — hooks

`scripts/reflex_reflect.py` ships with the plugin (`hooks/hooks.json`), mirroring
engram's capture hook. It is a **trigger, not the engine**:

- **UserPromptSubmit** — if the prompt is an explicit remember-flag, inject an
  immediate Absorb instruction; if it's a session wrap-up phrase, inject a
  reflect-on-corrections instruction.
- **Stop** — a heavily throttled backstop nudge (loop-guarded + cooldown) for long
  sessions, asking you to reflect on repeated corrections.

Env knobs: `REFLEX_DISABLE=1` (off), `REFLEX_COOLDOWN_MIN` (Stop cooldown, default
60), `REFLEX_REMEMBER_PHRASES` (override the explicit-flag phrases). The hook never
fails a session — any error exits 0.

## Rules

1. **Model is the engine.** The hook only picks the moment; *you* judge what's worth
   absorbing via the Absorption Rulebook. Never absorb mechanically.
2. **Propose before writing.** Outward, semi-permanent change to how the agent
   behaves — show the diff and get approval (unless the user grants standing
   approval). 
3. **Reversible always.** Every rule carries a date + origin and lives in the marked
   block, so any rule can be traced and removed. Never edit learned rules outside the
   block.
4. **Default local, promote conservatively.** Repo-local is the default scope; global
   promotion needs cross-repo evidence.
5. **Drop when unsure.** A missed rule costs one correction; a wrong/taste rule
   silently distorts every future session. Bias toward dropping.
6. **No bloat.** Prefer editing/merging an existing rule over adding a new one;
   surface pruning candidates in Review.
