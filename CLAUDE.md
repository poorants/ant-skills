# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code skills marketplace repository following the [Anthropic official structure](https://github.com/anthropics/skills) and [Agent Skills spec](https://agentskills.io/specification). Skills are distributed via `/plugin install my-skills@ant-skills`.

## Architecture

```
ant-skills/
├── .claude-plugin/
│   └── marketplace.json    # Marketplace registration — new skills must be added here
├── skills/<skill-name>/    # Each skill is a directory
│   ├── SKILL.md            # Required: metadata frontmatter + instructions
│   ├── scripts/            # Optional: helper scripts (loaded on demand)
│   ├── references/         # Optional: reference docs (loaded on demand)
│   └── assets/             # Optional: static assets (loaded on demand)
├── template/SKILL.md       # Template for new skills
└── scripts/validate.py     # Optional local validation
```

## SKILL.md Conventions

- Frontmatter requires `name` (must match directory name, max 64 chars, lowercase/digits/hyphens only) and `description` (max 1024 chars)
- Body instructions should be under 5000 tokens; keep file under 500 lines
- Detailed references go in separate files under `scripts/`, `references/`, or `assets/`
- Progressive disclosure: metadata loads at startup, instructions load on activation, resources load on demand

## Validation

```bash
skills-ref validate ./skills/<skill-name>
python scripts/validate.py --all
```

## Notes

- Design documents are written in Korean
- Project-specific skills (e.g. concept-pool-generator) stay in their respective project repos; only reusable skills belong here