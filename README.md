# ant-skills

Custom Claude Code skills collection by poorants.

## Installation

```bash
# Install plugin
/plugin install my-skills@ant-skills
```

## Structure

```
ant-skills/
├── .claude-plugin/
│   └── marketplace.json    # Marketplace registration
├── skills/                 # Skill sources
│   └── <skill-name>/
│       ├── SKILL.md        # Required: metadata + instructions
│       ├── scripts/        # Optional: helper scripts
│       ├── references/     # Optional: reference docs
│       └── assets/         # Optional: static assets
├── template/SKILL.md       # Template for new skills
└── scripts/validate.py     # Local validation tool
```

## Creating a New Skill

1. Copy `template/SKILL.md` to `skills/<your-skill-name>/SKILL.md`
2. Update the frontmatter `name` (must match directory name) and `description`
3. Write instructions in the body
4. Add the skill path to `.claude-plugin/marketplace.json`
5. Validate: `python scripts/validate.py skills/<your-skill-name>`

## Validation

```bash
# Validate a single skill
python scripts/validate.py skills/<skill-name>

# Validate all skills
python scripts/validate.py --all
```

## References

- [Agent Skills Spec](https://agentskills.io/specification)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
