# ant-skills

Claude Code skills marketplace by poorants.

Skills are organized into two **kits**, split by audience:

- **`ant-common-kit`** — general-purpose, cross-cutting tools usable in any project or context.
- **`ant-dev-kit`** — software-development tooling.

## Quick Start

### One-liner Setup (installs both kits)

**Windows:**

```powershell
iex (irm https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/init-claude-project.ps1)
```

**macOS / Linux:**

```bash
bash <(curl -sL https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/init-claude-project.sh)
```

This does exactly two things: installs/updates **both kits** (plus Anthropic's
`example-skills`) at **user scope**, and writes `.claude/settings.json` (all
permissions) in the current directory. Re-running refreshes everything. It does **not**
scaffold docs or conventions — knowledge and code conventions live in a shared
**engram brain** you link per repo (the script prints how). See
[bootstrap/README.md](bootstrap/README.md).

### Manual Setup

```bash
claude plugin marketplace add poorants/ant-skills
claude plugin install ant-common-kit@ant-agent-skills --scope user
claude plugin install ant-dev-kit@ant-agent-skills --scope user
```

User scope installs once globally (no per-repo duplication); engram's hooks self-gate
to brain repos, so a single user-scope install is safe everywhere.

## Shared brain workspace (engram)

Knowledge and code conventions are no longer scaffolded per repo — they live in one
shared **engram brain** that many repos use in common, so knowledge follows you across
repos. Usage (just tell Claude Code; the `engram` skill understands plain language):

1. **Register a brain once per machine** — point at a local clone of your brain repo:
   *register `<path-to-brain-repo>` as the "personal" brain*.
2. **Link a repo to it** — *use the "personal" brain for this repo*.

From then on that repo shares the brain's PARA knowledge graph and inherits the shared
code-convention base (`resources/conventions/<stack>.md`) plus its own deltas. The
[bootstrap](#one-liner-setup-installs-both-kits) only installs the kits and writes
`.claude/settings.json`; brain linkage is this engram step.

## Kits

### ant-common-kit — general / cross-cutting

Tools usable in any project or context. Carries engram's capture-loop hooks
(`hooks/hooks.json`). Grows as more general-purpose tools are added.

| Skill | Description |
|-------|-------------|
| **engram** | Networked PARA document brain **+ brain workspace** — PARA management (Projects/Areas/Resources/Archives) with knowledge-graph linking, MOC hubs, and integrity lint; and a shared **workspace brain** so many repos use ONE external brain (register/assign), so knowledge follows you across repos. Also curates the shared code-convention base |

```bash
claude plugin install ant-common-kit@ant-agent-skills --scope user
```

### ant-dev-kit — software development

Dev-focused tooling. Grows as more development skills are added.

| Skill | Description |
|-------|-------------|
| **code-convention** | Manage code conventions as an **AI-steering contract** (the rules a linter can't enforce / an agent can't infer); extract, check, and evolve, inheriting a shared stack base from the engram brain |
| **component-prototype** | UI variant prototyping tournament — generate many native-looking variants, vote, iterate to a final design |
| **git-versioning** | Structure-based `MAJOR.MINOR.PATCH` computed from the git commit graph at build time — no tags, CI, or tokens |
| **repo-map** | Agent-friendly link-map (`MAP.md`) of a repo's organization — modules, responsibilities, who-uses-what + a short overview; derived from code, regenerable |

```bash
claude plugin install ant-dev-kit@ant-agent-skills --scope user
```

## Repository Structure

```
ant-skills/
├── .claude-plugin/
│   └── marketplace.json    # Plugin registry (ant-common-kit, ant-dev-kit)
├── bootstrap/              # One-liner setup scripts (the unified auto-installer)
│   ├── init-claude-project.ps1
│   ├── init-claude-project.sh
│   └── README.md
├── hooks/
│   └── hooks.json          # engram capture-loop hooks (owned by ant-common-kit)
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md        # Skill definition (required)
│       ├── scripts/        # Helper scripts (optional)
│       ├── references/     # Reference docs (optional)
│       └── assets/         # Static assets (optional)
├── scripts/validate.py     # Local skill validation
└── template/SKILL.md       # Template for new skills
```

## References

- [Agent Skills Spec](https://agentskills.io/specification)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
