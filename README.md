# ant-skills

Claude Code skills marketplace by poorants.

## Quick Start

### 1. Add Marketplace

```bash
claude plugin marketplace add poorants/ant-skills
```

### 2. Install Plugin

**Global:**

```bash
claude plugin install docs-tools@ant-agent-skills
```

**Local (development):**

```bash
claude plugin install docs-tools@ant-agent-skills --scope local
```

### 3. Update Plugin

**Manual:**

```bash
claude plugin update docs-tools@ant-agent-skills
```

**Auto-update:**

```
/plugin → Marketplaces → ant-agent-skills → Enable auto-update
```

### 4. Use Skills

Skills activate automatically based on triggers. You can also invoke directly:

```
문서 관리해줘
manage my documents
para init
```

## Available Skills

| Skill | Description | Triggers |
|-------|-------------|----------|
| **para-docs** | PARA-based document manager | `para init`, `문서 관리해줘` |
| **ant-profile** | Ant's Claude Code profile | `ant profile`, `앤트 프로필` |

## Skill Examples

### para-docs

Organize project documents using the PARA method.

```
para init              # Initialize PARA structure
회의록 저장해줘          # Create a document
para review            # Review documents
```

### ant-profile

Apply ant's preferred settings for comfortable development.

```
ant profile            # Apply permissions + keybindings
앤트 프로필로 설정해줘    # Same in Korean
```

Includes:
- **Permissions**: All tools allowed in project
- **Keybindings**: Enter=newline, Ctrl+Enter=submit

## For Contributors

### Repository Structure

```
ant-skills/
├── .claude-plugin/
│   └── marketplace.json    # Marketplace configuration
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md        # Skill definition (required)
│       ├── scripts/        # Helper scripts (optional)
│       ├── references/     # Reference docs (optional)
│       └── assets/         # Static assets (optional)
└── template/SKILL.md       # Template for new skills
```

### Creating a New Skill

1. Copy template: `cp template/SKILL.md skills/<skill-name>/SKILL.md`
2. Edit frontmatter: set `name` and `description`
3. Write instructions in the body
4. Register in `.claude-plugin/marketplace.json`
5. Test locally with `claude plugin marketplace add .`

### Validation

```bash
python scripts/validate.py skills/<skill-name>
python scripts/validate.py --all
```

## References

- [Agent Skills Spec](https://agentskills.io/specification)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
