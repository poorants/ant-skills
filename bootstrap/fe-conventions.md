# Front-End Code Conventions — house standard

> Seeded by the ant-skills bootstrap. The single source of truth for code style in this
> project. The **load-bearing, uniform-across-all-projects** standards are **i18n** and
> **Test IDs** — keep these identical everywhere. Everything else is a sensible baseline;
> extend or override per project with the `code-convention` skill (`/code-convention
> add | update | evolve`) and record changes in `CHANGELOG.md`.

Categories: i18n (`I18N-`), Test IDs (`TEST-`), Naming (`NAME-`), Style (`STYLE-`),
Error Handling (`ERR-`), Security (`SEC-`).

---

## 1. i18n / Localization

> The product ships in multiple languages. Treat every user-visible string as translatable.

### I18N-01: No hardcoded user-facing strings

**Severity:** error
**Rationale:** Any literal in the UI is an untranslated leak.

All user-visible text (labels, placeholders, toasts, aria-labels, errors) goes through the
translator (`t(...)`). Exceptions: brand/product names, code identifiers, and template
syntax passed as interpolation values.

**Bad:** `<Button>Save</Button>`  **Good:** `<Button>{t("common.save")}</Button>`

### I18N-02: One typed source-of-truth locale

**Severity:** error
**Rationale:** If every locale is type-checked against the source language, a missing or
renamed key fails the build instead of silently shipping an untranslated/blank string.

Pick one source locale (e.g. `en`). Type every other locale against it (e.g.
`const ko: AppResources = {...}` where `AppResources = typeof en`). Add new keys to the
source first.

### I18N-03: Preserve interpolation placeholders across locales

**Severity:** error
**Rationale:** A dropped or renamed `{{var}}` silently breaks the rendered string at
runtime — the type system can't catch it.

Keep every `{{placeholder}}` verbatim and in place in all translations. Verify parity
(e.g. a placeholder-count diff across locale files).

### I18N-04: Don't translate technical tokens

**Severity:** warning
**Rationale:** Translating identifiers, paths, or flags produces wrong, confusing UI.

Leave untranslated: product/brand names, env var names, file paths, CLI flags, and code
keywords.

### I18N-05: Auto-detect language; English fallback; persist the choice

**Severity:** warning
**Rationale:** Users get their language automatically; an explicit choice should stick.

Default language is detected from the OS/browser locale (not download region). Unknown
locales fall back to English. An explicit user selection is persisted and wins over
detection. Expose a language switcher in settings.

---

## 2. Testing & Test IDs

> `data-testid` is a **stable address** a human (or a test) uses to point at a specific
> element. Uniqueness and a predictable scheme are mandatory.

### TEST-01: Tag interactive and identifiable elements

**Severity:** warning
**Rationale:** Anything a human/test might target needs a handle; decorative wrappers add
only noise.

Add `data-testid` to: interactive elements (button, input, select, switch, tab, menu item,
link), each **list-item root**, each **screen root**, and each **dialog root**. Not to
purely decorative/layout wrappers, icons, or plain text.

### TEST-02: Naming scheme — kebab-case `<area>-<element>[-<id>][-<sub>]`

**Severity:** error
**Rationale:** One predictable grammar makes ids guessable, greppable, and
collision-resistant.

Values are kebab-case and use a fixed element-type suffix vocabulary:
`-screen -dialog -card -row -btn -input -select -switch -tab -menu -nav`.

**Good:** `groups-new-btn`, `group-card-{id}`, `secret-dialog-name-input`

### TEST-03: Repeated elements embed the stable domain id — never the array index

**Severity:** error
**Rationale:** A test id is an address; duplicates are ambiguous. An array index shifts on
sort/filter/delete, so a previously-picked id would drift to a different object. The
domain entity id stays put.

- Singletons (one on screen at a time, incl. dialog fields): static id.
- Repeated elements (cards, rows): append the stable entity id — `group-card-{id}`. Use a
  within-scope-unique name only where no id exists; use the array index **only** as a last
  resort (e.g. editor rows with no entity).

**Bad:** `` `item-card-${index}` ``  **Good:** `` `item-card-${item.id}` ``

### TEST-04: Test ids are a stable contract

**Severity:** warning
**Rationale:** They're referenced externally (pickers, tests). Renaming silently breaks
those references.

Derive child ids from the parent (`group-card-{id}-menu`, `-edit`, `-delete`). Don't
rename existing ids casually.

---

## 3. Naming

### NAME-01: Source files are kebab-case

**Severity:** warning
**Rationale:** Consistent and case-insensitive-filesystem-safe.

`run-action-dialog.tsx` exporting `RunActionDialog`.

### NAME-02: Components are PascalCase with named exports

**Severity:** error
**Rationale:** Named exports stay greppable and refactor-safe; reserve the default export
for the app entry only.

### NAME-03: Identifiers follow per-language case

**Severity:** error
**Rationale:** Idiomatic to each language.

TS: `camelCase` functions/vars/hooks, `PascalCase` types. (Other languages follow their
own idiom — e.g. Rust `snake_case` / `PascalCase`.)

### NAME-04: `interface` for object shapes, `type` for unions

**Severity:** warning
**Rationale:** Reads consistently and matches common TS practice.

### NAME-05: Module-level constant data is SCREAMING_SNAKE_CASE

**Severity:** warning
**Rationale:** Distinguishes fixed config/seed tables from runtime values at a glance.

### NAME-06: i18n keys are camelCase, dot-namespaced by area

**Severity:** error
**Rationale:** Keys map 1:1 to UI areas, staying discoverable.

`t("groups.deleteDesc")`, not `t("deleteGroupDescription")`.

---

## 4. Style

### STYLE-01: Delegate formatting to a formatter

**Severity:** error
**Rationale:** A committed formatter config ends all formatting debate.

Use Prettier (or the language formatter) with the config committed; run before committing.
Don't hand-format.

### STYLE-02: Import order — external before internal

**Severity:** warning
**Rationale:** Scannable imports.

Framework → third-party → internal (`../lib`, `../store`, then `./` relatives).

### STYLE-03: Non-trivial modules open with a doc comment

**Severity:** warning
**Rationale:** Orients the reader; ties code to design docs.

State the module's purpose at the top; link the relevant design doc/section.

### STYLE-04: Comments say "why"; defer with versioned `TODO`

**Severity:** warning
**Rationale:** Code already self-describes "what"; comments add intent.

Mark deferred work as `TODO(vX.Y): ...`.

### STYLE-05: Respect the strict compiler gate

**Severity:** error
**Rationale:** The compiler is the cheapest, most reliable enforcement.

Keep `strict`, no-unused, no-fallthrough on; fix the code rather than disabling. Prefix
intentionally-unused params with `_`.

---

## 5. Error Handling

### ERR-01: No silent failures

**Severity:** error
**Rationale:** A swallowed error is an invisible bug.

Never leave an empty `catch {}`. Surface to the user or rethrow.

### ERR-02: Reset async UI state in `finally`

**Severity:** error
**Rationale:** If the awaited promise throws or never resolves, a spinner/disabled state
must still clear.

Wrap `await` in `try/finally`; reset `busy`/loading flags in `finally`.

### ERR-03: Typed errors at module boundaries

**Severity:** warning
**Rationale:** Typed errors at the library edge; ergonomic context at the app boundary.

---

## 6. Security

### SEC-01: Never commit or log secrets

**Severity:** error
**Rationale:** Secrets in source/logs/transcripts are the most common leak.

No secret values in source, logs, or error payloads. Use env/secret stores; keep secret
files out of git.

### SEC-02: Mask secrets in the UI by default

**Severity:** error
**Rationale:** Shoulder-surfing and screenshots leak visible secrets.

Mask secret values by default; reveal only on explicit, gated user action.

### SEC-03: Validate and escape untrusted input

**Severity:** error
**Rationale:** Untrusted input is the root of injection/XSS.

Validate at boundaries; never interpolate untrusted input into queries/commands/markup.
