# `POC_SPEC` data contract + worked example

Each round you author **one JS file** (e.g. `poc-data.js`) that assigns `window.POC_SPEC`.
`build_poc.py` inlines it into the shell at the `/*__POC_DATA__*/` sentinel. The shell owns all
plumbing (voting, tabs, sample toggle, persistence, export) — you only supply tokens + variants.

## Shape

```js
window.POC_SPEC = {
  title: "키 그룹 카드",          // string — page title + localStorage key (keep stable across rounds)
  brief: "한 그룹 = 색 · 팩 · 키 묶음 …", // one-line description shown under the title
  round: 2,                       // integer — shown in the provenance line, included in export
  themeSource: "frontend/src/theme/tokens.ts", // optional — where the palette was extracted from
  themeCss: ":root{ --canvas:#1a1c1f; --card:#22252a; --brand:#a7adb7; … }", // raw CSS, overrides defaults

  // Optional. If >1, a sample toggle appears and re-renders all cards with the chosen `data`.
  // `data` is any shape your render() expects. Omit to render with a single implicit sample.
  samples: [
    { id: "few",   label: "키 적음 (3)",  data: { tint: "#6f8fae", pack: "사운드팩 1", keys: ["S","D","Alt"] } },
    { id: "many",  label: "키 많음 (12)", data: { tint: "#7faf8c", pack: "청축 v2", keys: ["Q","W","E","R","T","Y","U","I","Alt","⏎","⇧","Space"] } },
    { id: "ghost", label: "팩 미지정",    data: { tint: "#a98f6f", pack: null, keys: ["F1","F2"] } },
  ],

  // This round's fresh candidates. id MUST be globally unique & stable (prefix by round: "r2-01").
  // render(data, indexWithinTab) → HTML string for the live preview.
  candidates: [
    { id: "r2-01", title: "한 줄 알약", desc: "점·팩·키칩·액션 한 행, +N",
      render: (g, i) => `<div class="card" style="padding:8px 12px;background:var(--card);border:1px solid var(--line);border-radius:12px">…</div>` },
    // …20–30 of them
  ],

  // Carried forward from earlier rounds (the user's prior picks). Same shape as candidates.
  // Shown in a locked "확정 후보" tab, pre-checked. Copy these verbatim from the prior round's data
  // file, keeping their ids, so votes and identity stay stable. Empty on round 1.
  finalists: [
    { id: "r1-04", title: "데이터 행", desc: "컬럼 정렬, 목록 스캔 최적", render: (g, i) => `…` },
  ],
};
```

## Export shape (what the user pastes back)

The footer's **결과 JSON 복사** button copies just id (번호) + name + description per pick:

```json
{
  "title": "키 그룹 카드",
  "round": 2,
  "kept": [
    { "id": "r1-04", "name": "데이터 행", "desc": "컬럼 정렬, 목록 스캔 최적" },
    { "id": "r2-07", "name": "전부 모노 타이포", "desc": "팩명도 모노로 — 차분" }
  ]
}
```

`kept` is the union of still-checked candidates **and** still-checked finalists → it becomes the
**next round's `finalists`** (carry those objects forward by `id`). The user typically adds their
rationale in the chat message alongside the paste — read it to steer the next batch (push toward what
they liked, drop dead ends). There is no per-card memo field.

## Authoring tips

- **Theme first.** Extract the real palette/fonts from the project (e.g. an AntD `theme/tokens.ts`,
  a Tailwind config, CSS custom properties) and put them in `themeCss` so candidates read as native,
  not generic. Note the source in `themeSource`.
- **Self-contained markup.** Each `render` returns plain HTML using the CSS vars (`var(--card)`,
  `var(--brand)`, `var(--mono)`, …) the shell defines. Define any extra reusable classes inside
  `themeCss`. Don't rely on external stylesheets — the page must open from `file://`.
- **Make variants genuinely distinct** — vary structure (1-line vs 2-row, bar vs dot vs avatar,
  chips vs keycaps vs mini-map), not just spacing. 20–30 per round.
- **Stress-test with samples** — include an overflow case and an empty/placeholder case so density
  and truncation are visible at review time.
- **No `</script>` in data** — if a variant must contain that literal, write `<\/script>`.
