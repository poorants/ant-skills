---
name: component-prototype
description: >
  UI 컴포넌트/레이아웃을 글이 아니라 "보고 골라서" 정하는 시각적 프로토타이핑 토너먼트. 화면에 무언가를
  어떻게 표현할지(카드, 목록 행, 패널, 컨트롤, 빈 상태 등) 정해야 할 때, 프로젝트의 실제 테마 토큰
  (팔레트·폰트·radii)을 재사용한 단일 오프라인 HTML로 20–30개의 서로 다른 시안을 생성하고 — 브라우저에서
  체크박스로 투표 → 당선작을 잠긴 탭으로 이월 → 빈 슬롯을 새 시안으로 재생성하며 N라운드 반복해 최종안으로
  수렴시킨 뒤 실제 코드에 반영한다. UI 옵션을 탐색/비교하거나, 컴포넌트를 프로토타이핑하거나, 레이아웃이
  어색(너무 길다/비었다/복잡)해서 커밋 전에 대안을 보고 싶을 때 사용. 언어 무관 — 예: "컴포넌트 POC",
  "시안 만들어", "프로토타입", "디자인 시안", "카드 타입", "여러 개 만들어서 고르자", "투표해서 고르자",
  "시안 비교", "component POC", "design bake-off", "compare layouts", "show me options".
---

# component-prototype — UI variant tournament (prototype → vote → iterate → finalize)

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
  you ingest kept[] → round N: locked picks in finalists tab + fresh variants for the empty slots →
  … repeat, walking the stage ladder coarse → fine, until one design remains → finalize into real code
```

## Stage ladder — coarse → fine, advanced by "locks" (NOT by round number)

Variation walks from the **biggest structural swings down to the finest CSS detail**. The stage is
driven by what the user has **locked in**, *not* by the round number — a stage can span several
rounds, or be skipped if the user converges fast. **Never hardcode "round 1 = layout, round 2 = CSS."**

The gradient (and each stage itself runs coarse → fine across its own rounds):

1. **레이아웃 파격 — layout, radical.** Big organizational change: rearrange control/button placement,
   swap the whole rendering paradigm (list ↔ chips ↔ tabs ↔ grid ↔ table ↔ cards ↔ timeline), change
   the information hierarchy and primary affordance. Genuinely different *skeletons*.
   ❌ not "same card, different chip color."
2. **레이아웃 섬세 — layout, refine.** Big frame locked. Tune the arrangement only — ordering,
   grouping, primary/secondary emphasis, proportions, structural spacing rhythm. Same paradigm, better organized.
3. **CSS 파격 — visual, radical.** Layout fully locked. Swing the visual language wide — color/elevation
   systems, typographic scale, density, quiet-vs-loud borders, accent strategy. Different *looks*, identical bones.
4. **CSS 섬세 — visual, refine.** Visual direction locked. Micro-deltas only — exact spacing, radius,
   weight, hover/active states, shadow depth, contrast.

**Advance only on a lock signal.** Read the vote + rationale each round: when the user signals the
current level is decided ("이 레이아웃이다", "배치 확정", "이 색감/스타일이다"), freeze it and step to the
next stage. If the picks still disagree at the current level, run another round **at the same stage,
with smaller amplitude than the last**. If a later stage reopens an earlier doubt, step back up.
Whatever is locked is **baked into every new variant** (and carried in `finalists`); only the current
level varies. Carry the active stage in `roundIntent` so the page header shows what this round is for.

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
- `title` (stable across rounds — it's the localStorage key), `brief`, `round`,
  `roundIntent` (the active stage, e.g. `"레이아웃 파격"` / `"CSS 섬세"`), `themeCss`, `themeSource`.
- `samples`: the states from step 1 (include an overflow case and an empty/placeholder case).
- `candidates`: **20–30 genuinely distinct** variants **for the current stage** (see the Stage ladder),
  at an amplitude finer than the previous round *in this stage*. Round 1 starts at **레이아웃 파격** —
  different *skeletons* (list ↔ chips ↔ tabs ↔ grid ↔ table ↔ cards), controls relocated; not chip restyles.
  Once a level is locked, **bake it into every variant** and vary only the current level. Give each a
  short Korean `title` + `desc` and a **globally-unique id prefixed by round** (`r1-01`, `r2-01`, …).
  `render(data, i)` returns HTML using the theme CSS vars.
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
- **Walk the stage ladder.** From the rationale + whether the kept variants agree at the current level:
  if the user locks it ("이 레이아웃이다", "배치 확정", "이 색감/스타일이다"), **advance the stage** — bake the
  locked level into every new variant and set the next `roundIntent`. If picks still disagree, **stay at
  this stage** and make the next batch finer-amplitude. Step back a stage if a later round reopens an
  earlier doubt.
- Generate ~20–30 fresh `candidates` (new round prefix) for the (possibly advanced) stage — push the
  liked direction, drop dead ends.
- Honor **composite instructions** ("17번 골격에 02번 키캡") by seeding new variants from the named mix.
- Rebuild (`--out poc-round-2.html`) and have them vote again.

Stop when one design remains, or the user picks a winner / says done.

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
