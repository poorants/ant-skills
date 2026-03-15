# ant-skills

Claude Code skills marketplace by poorants.

## Quick Start

### One-liner Setup

**Windows:**

```powershell
iex (irm https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/init-claude-project.ps1)
```

**macOS / Linux:**

```bash
bash <(curl -sL https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/init-claude-project.sh)
```

This registers the marketplace, installs plugins, sets permissions, and initializes PARA documents.

### Manual Setup

```bash
claude plugin marketplace add poorants/ant-skills
claude plugin install ant-project-kit@ant-agent-skills --scope local
```

## Plugins

### ant-project-kit

Project lifecycle management — kickstart, planning, tracking, and retrospective.

| Skill | Description |
|-------|-------------|
| **project-kickstart** | Project concept shaping → `CONCEPT.md` |
| **project-plan** | Phase-based roadmap with PDCA integration |
| **project-retrospective** | Git history → resume/portfolio STAR document |
| **work-report** | Work report generation |
| **para-docs** | PARA-based document management |
| **init-permissions** | Grant all Claude Code permissions to project |
| **skill-doctor** | Skill validation and debugging |

```bash
claude plugin install ant-project-kit@ant-agent-skills --scope local
```

### ant-app-kit

App scaffolding, frontend tooling, and external service integrations.

| Skill | Description |
|-------|-------------|
| **init-go-webapp** | Go + React single-binary web app scaffolding |
| **init-rust-deskapp** | Rust + Tauri desktop app scaffolding |
| **fe-component-rules** | Frontend component conventions |
| **fe-design-tokens** | Design token management |
| **fe-style-guide** | Frontend style guide |
| **naver-maps** | Naver Maps API integration |

```bash
claude plugin install ant-app-kit@ant-agent-skills --scope local
```

## Repository Structure

```
ant-skills/
├── .claude-plugin/
│   └── marketplace.json    # Plugin registry
├── bootstrap/              # One-liner setup scripts
│   ├── init-claude-project.ps1
│   └── init-claude-project.sh
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md        # Skill definition (required)
│       ├── scripts/        # Helper scripts (optional)
│       ├── references/     # Reference docs (optional)
│       └── assets/         # Static assets (optional)
└── template/SKILL.md       # Template for new skills
```

## References

- [Agent Skills Spec](https://agentskills.io/specification)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
