# Session Update Review — read back what this session fed the brain

The Capture loop *writes* to the brain during work; this workflow *reads back*
what landed, so at session close the user can review exactly what changed. It is
**command-triggered** (the user asks for it), not a hook — the read-back
counterpart to the [capture-loop](capture-loop.md).

Triggers: "이번 세션 브레인 업데이트 리뷰", "엔그램 세션 리뷰", "브레인 업데이트
알려줘", "세션 회고", "review brain updates", "engram session review", "what
changed in the brain this session".

## Sources — combine two; model memory is primary

1. **Session memory (primary).** Recall every note you created or edited and every
   link / MOC you touched this session via the Create / Move / Link & Connect
   workflows. You are the source of truth for *intent* — what each change means
   and why it landed.

2. **Git cross-check.** From the repo root, scope to the PARA base (`<base>/` =
   `brain/`, or legacy `para/`):

   ```bash
   git status --short -- <base>/        # ?? = new note this session; M = edited
   git diff --stat -- <base>/           # line-level scope (unstaged)
   git diff --stat --staged -- <base>/  # staged edits too
   ```

   `??` entries are notes added this session; ` M`/`M ` are edits. If notes were
   already **committed** during the session, add the relevant commits with
   judgment (e.g. `git log --oneline -- <base>/`, pick this session's) and say so
   — git alone cannot prove a commit belongs to *this* session.

Reconcile the two lists and de-duplicate. If git shows a change your memory does
not (or vice versa), surface it rather than hiding it.

## Closing check

Run the Integrity Lint Workflow so the recap also confirms the session left the
brain consistent (no new broken links / orphans).

## Report format

```
## engram Session Brain Review — YYYY-MM-DD

### New notes
- [projects/x/decision-y.md](projects/x/decision-y.md) — one-line summary

### Updated notes
- [areas/z.md](areas/z.md) — what changed (e.g. added "Gotcha: …" section)

### Links & MOCs
- wove [[decision-y]] into areas/z.md; updated projects/x/README.md

### Integrity
- engram lint: clean (0 broken, 0 new orphans)

### Summary
- N new · M updated · K links · MOCs: …
```

If nothing landed in the brain this session, say so in one line — do not
manufacture a report (same Brain-boundary discipline as the Capture loop).
