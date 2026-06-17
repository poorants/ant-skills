---
name: component-poc
description: >
  Visual prototyping tournament for UI components/layouts. When you need to decide how to
  represent something on screen (a card, list row, panel, control, empty state, page section),
  generate 20–30 distinct variants as a single lightweight HTML page that reuses the PROJECT's own
  theme tokens (palette, fonts, radii) so they look native — then review in the browser, VOTE per
  variant with checkboxes, carry the winners forward into a locked tab, regenerate the empty slots
  with fresh variants, and iterate over N rounds until it converges to the final design, which you
  then wire into the real code. Use when the user wants to explore/compare UI options, prototype a
  component, "see a few designs", run a design bake-off, or says a layout feels off (too much empty
  space, too tall, cluttered) and wants alternatives before committing.
  Triggers: "component POC", "POC 만들어", "프로토타입", "디자인 시안", "카드 타입", "여러 개 만들어서 고르자",
  "샘플 페이지", "design bake-off", "design tournament", "compare layouts", "show me options",
  "이 컴포넌트 다른 방식", "다른 방안", "n개 만들어봐", "투표해서 고르자", "시안 비교".
---

# component-poc — UI variant tournament (prototype → vote → iterate → finalize)

Decide UI by **looking and picking**, not by describing in prose. Generate many native-looking
variants, review them in a browser, vote, keep winners, regenerate the rest, repeat until it
converges. Each round is a single self-contained HTML file the user opens directly.

The interactive plumbing — voting checkboxes, candidate/finalist tabs, sample toggle, persistence,
clipboard export — is **shipped in `assets/poc-shell.html`**. You never rewrite it. Each round you
author only a small data file (theme tokens + variant render functions) and inline it with
`scripts/build_poc.py`. Contract & worked example: **`references/data-contract.md`** (read it before
authoring your first data file).

## When to use vs not

- **Use** for any "how should this look / which layout" decision with a wide solution space, or when
  an existing UI is criticized (too tall, empty, cluttered) and the user wants alternatives to choose
  from before you commit code.
- **Don't** use for logic/behavior decisions, single obvious layouts, or copy/wording-only changes.

## The loop

```
brief + extract theme → round 1: 20–30 variants → user votes (copies JSON) →
  you ingest kept[] → round N: finalists in locked tab + fresh variants for the empty slots →
  … repeat until kept is small (1–3) or the user says done → finalize into real code
```

### Step 1 — Brief + theme extraction (do this first, every time)

1. Pin down the **component & its states**: what it represents, and the variations it must survive
   (e.g. assigned vs empty, few vs many items, active/selected, error). These become the **samples**.
2. **Extract the project's real design tokens** so variants look native, not generic. Hunt for:
   - an AntD theme (`theme/tokens.ts`, `ConfigProvider`), Tailwind config, CSS custom properties,
     a design-tokens file, or the most-used colors/fonts in existing components.
   - Pull palette (bg/surface/text/brand/border), font stacks (incl. mono), radii, spacing.
   Put them into `themeCss` (a raw `:root{…}` block + any reusable classes) and record where you
   got them in `themeSource`. **This step is what makes the POC trustworthy — never skip it.**

### Step 2 — Author the round's data file

Write `poc-data.js` defining `window.POC_SPEC` per `references/data-contract.md`:
- `title` (stable across rounds — it's the localStorage key), `brief`, `round`, `themeCss`, `themeSource`.
- `samples`: the states from step 1 (include an overflow case and an empty/placeholder case).
- `candidates`: **20–30 genuinely distinct** variants. Vary *structure*, not just spacing —
  1-line vs 2-row, dot vs left-bar vs avatar vs number, chips vs keycaps vs mini-map vs segmented,
  collapsed vs expanded, table-row vs card vs chrome-less. Give each a short Korean `title` + `desc`
  and a **globally-unique id prefixed by round** (`r1-01`, `r2-01`, …). `render(data, i)` returns
  HTML using the theme CSS vars.
- `finalists`: empty on round 1; on later rounds, the kept variants from the previous round
  (copied verbatim with their ids and render fns).

### Step 3 — Build & open

```bash
python "<skill>/scripts/build_poc.py" --data poc-data.js --out poc-round-1.html --open
```

Write `poc-data.js` and the output HTML into a throwaway spot in the user's project (e.g. a
`.poc/` dir at repo root, or alongside the target file). Then tell the user: review in the browser,
**check the variants you like**, and click **결과 JSON 복사** → paste it back in chat (adding any
rationale in their own words). (Per-card votes persist in localStorage, so reloading is safe.)

### Step 4 — Ingest the vote, iterate

When the user pastes `{ title, round, kept: [{ id, name, desc }, …] }`:
- The kept `id`s become the **next round's `finalists`** (carry their objects forward verbatim).
- Read the user's chat rationale and the *kinds* of variants that survived to **steer the next batch** —
  generate ~20–30 fresh `candidates` (new round prefix) that push the liked direction and drop dead ends.
- Honor **composite instructions** ("17번 골격에 02번 키캡") by seeding new variants from the named mix.
- Rebuild (`--out poc-round-2.html`) and have them vote again.

Stop when `kept` is down to 1–3, or the user picks a winner / says done.

### Step 5 — Finalize

- Wire the chosen variant into the **real code**, honoring the project's conventions (if a
  `code-convention` skill / `CONVENTIONS.md` exists, follow it — testids, i18n, naming, a11y).
- Record the decision where the project keeps design docs. If this repo uses **engram/`brain/`**,
  drop a one-line decision note (what won, why, which round) and link it from the relevant MOC.
- Offer to delete the `.poc/` scratch files (they're throwaway).

## Conventions

- **Single-file, offline.** Every round HTML must open from `file://` with no network — all CSS/JS
  inline, no external fonts/stylesheets (system-font fallbacks are fine).
- **Stable ids & title.** Never renumber a kept variant across rounds; never change `title` (votes
  are keyed on it). New variants always get a new round-prefixed id.
- **Real tokens, real states.** Native palette + the actual hard cases (overflow, empty) — a POC that
  hides the hard cases makes a decision you'll regret in code.
- **Scratch, not source.** POC files are disposable; keep them out of meaningful commits (use `.poc/`
  or clean up at finalize). Only the finalized component lands in the codebase.

## Files

- `assets/poc-shell.html` — the reusable page shell (voting, tabs, sample toggle, export). Don't edit per-round.
- `scripts/build_poc.py` — inlines a round's `poc-data.js` into the shell → standalone HTML (`--open` to launch).
- `references/data-contract.md` — `POC_SPEC` shape, export shape, and a worked example. Read before authoring.
