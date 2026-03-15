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
| 2 | `.claude/settings.local.json` (all permissions) |
| 3 | Plugin marketplace registration (bkit, anthropic, ant-skills) |
| 4 | Plugin installation (bkit, example-skills, ant-project-kit) |
| 5 | `.gitignore` setup (docs/, .bkit/) |
| 6 | PARA directory initialization |

Requires: [Claude Code CLI](https://claude.ai/code) (steps 2-5 skipped if not installed)

## macOS / Linux

### init-claude-project.sh

```bash
bash <(curl -sL https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/init-claude-project.sh)
```

| Step | Action |
|------|--------|
| 1 | `.claude/settings.local.json` (all permissions) |
| 2 | Plugin marketplace registration (bkit, anthropic, ant-skills) |
| 3 | Plugin installation (bkit, example-skills, ant-project-kit) |
| 4 | `.gitignore` setup (docs/, .bkit/) |
| 5 | PARA directory initialization |

Requires: [Claude Code CLI](https://claude.ai/code)

## Optional Plugins

Install additional plugins as needed:

```bash
claude plugin install ant-app-kit@ant-agent-skills --scope local
```
