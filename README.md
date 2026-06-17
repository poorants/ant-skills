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

This unified auto-installer registers the marketplaces, installs **both kits** (plus
Anthropic's `example-skills`), sets permissions, and initializes the PARA document
structure / code conventions based on the repo type. Re-running refreshes everything
to the latest. See [bootstrap/README.md](bootstrap/README.md) for the mode-aware details.

### Manual Setup

```bash
claude plugin marketplace add poorants/ant-skills
claude plugin install ant-common-kit@ant-agent-skills --scope user
claude plugin install ant-dev-kit@ant-agent-skills --scope user
```

User scope installs once globally (no per-repo duplication); engram's hooks self-gate
to brain repos, so a single user-scope install is safe everywhere.

## Kits

### ant-common-kit — general / cross-cutting

Tools usable in any project or context. Carries engram's capture-loop hooks
(`hooks/hooks.json`). Grows as more general-purpose tools are added.

| Skill | Description |
|-------|-------------|
| **engram** | Networked PARA document brain — PARA management (Projects/Areas/Resources/Archives) + knowledge-graph linking, MOC hubs, and integrity lint |

```bash
claude plugin install ant-common-kit@ant-agent-skills --scope user
```

### ant-dev-kit — software development

Dev-focused tooling. Grows as more development skills are added.

| Skill | Description |
|-------|-------------|
| **code-convention** | Extract, enforce, and evolve project code conventions |
| **component-prototype** | UI variant prototyping tournament — generate many native-looking variants, vote, iterate to a final design |

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
