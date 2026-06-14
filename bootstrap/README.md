# Bootstrap Scripts

One-liner scripts to initialize Claude Code project environments.

## Windows

### init-claude-project.ps1

```powershell
iex (irm https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/init-claude-project.ps1)
```

| Step | Action |
|------|--------|
| 1 | Windows Terminal keybindings (iTerm2 style) |
| 2 | `.claude/settings.json` (all permissions) |
| 3 | Plugin marketplace registration + **update** (anthropic, ant-skills) |
| 4 | Plugin installation + **update** (example-skills, ant-project-kit) |
| 5 | `.gitignore` setup (docs/) |
| 6 | Document structure + conventions — **mode-aware** (see below) |

Re-running refreshes existing environments (marketplaces and plugins are always
updated). Requires: [Claude Code CLI](https://claude.ai/code) (steps 2-6 skipped if not installed)

## macOS / Linux

### init-claude-project.sh

```bash
bash <(curl -sL https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/init-claude-project.sh)
```

| Step | Action |
|------|--------|
| 1 | `.claude/settings.json` (all permissions) |
| 2 | Plugin marketplace registration + **update** (anthropic, ant-skills) |
| 3 | Plugin installation + **update** (example-skills, ant-project-kit) |
| 4 | `.gitignore` setup (docs/) |
| 5 | Document structure + conventions — **mode-aware** (see below) |

Re-running refreshes existing environments. Requires: [Claude Code CLI](https://claude.ai/code)

## Mode-aware document setup

The final step detects the repo type and sets up accordingly:

| Mode | Detected when | Result |
|------|---------------|--------|
| **project** | code markers present (`package.json`, `Cargo.toml`, `go.mod`, …) | nested `brain/` PARA + stack-detected conventions |
| **brain** | `brain/` exists, no code | nested `brain/` PARA; **no** code conventions (pure doc vault) |
| **flat-legacy** | PARA folders at the root, no `brain/` | left as-is for back-compat; hints to unify under `brain/` |
| **empty** | nothing to detect | prompts you in-place (interactive) for mode + stack; falls back to a `CLAUDE.md` "Project setup (pending)" note when non-interactive |

`brain/` is the default base for new repos (both standalone vaults and code
projects); the root is reserved for repo meta and exported output.

In **project** mode, conventions are seeded under `brain/areas/code-convention/`
(reusing a legacy `para/` if one already exists): the curated front-end standard
(i18n + `data-testid`, `bootstrap/fe-conventions.md`) when React is detected, else
a thin generic base (`bootstrap/generic-conventions.md`). Backends (rust/go/…) are
flagged to be extracted from real code with `/code-convention`. A `## Code
conventions` section is added to `CLAUDE.md` that `@import`s the rules so every
session auto-loads them. All writes are idempotent (existing files untouched).

## Optional Plugins

Install additional plugins as needed:

```bash
claude plugin install ant-app-kit@ant-agent-skills --scope local
```
