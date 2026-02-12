---
name: ant-profile
description: >
  Apply ant Claude profile for comfortable development. Grants all permissions
  to the project and configures keybindings (Enter=newline, Ctrl+Enter=submit).
  Triggers: "ant profile", "앤트 프로필", "앤트 프로필로 설정", "앤트 클로드 프로필",
  "ant setup", "앤트 셋업", "apply ant profile"
---

# Ant Profile

Apply ant's preferred Claude Code settings for comfortable development.

## What It Does

1. **Grant all permissions** to the current project
2. **Configure keybindings** for natural multi-line input

## Workflow

### Step 1: Grant Permissions (Project-level)

Create `.claude/settings.local.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash",
      "Read",
      "Edit",
      "Write",
      "Glob",
      "Grep",
      "WebFetch",
      "WebSearch",
      "Skill",
      "Task"
    ]
  }
}
```

### Step 2: Configure Keybindings (User-level)

Create `~/.claude/keybindings.json`:

```json
{
  "submit": "ctrl+enter",
  "newline": "enter"
}
```

This makes:
- **Enter** = New line
- **Ctrl+Enter** = Submit message

## Steps

1. Ask user what to set up:
   - "모두 설정" / "Both" (default)
   - "권한만" / "Permissions only"
   - "키바인딩만" / "Keybindings only"

2. For permissions:
   - Check if `.claude/settings.local.json` exists
   - If exists, ask to overwrite or merge
   - Create `.claude/` directory if needed
   - Write permissions file

3. For keybindings:
   - Check if `~/.claude/keybindings.json` exists
   - If exists, ask to overwrite
   - Write keybindings file

4. Report results:
   ```
   ✓ 권한 설정 완료 (.claude/settings.local.json)
   ✓ 키바인딩 설정 완료 (~/.claude/keybindings.json)

   키바인딩 적용을 위해 Claude Code를 재시작하세요.
   ```

## Rules

1. **Confirm overwrites**: Always ask before overwriting existing files
2. **Selective setup**: Allow user to choose what to configure
3. **Restart reminder**: Always remind to restart for keybindings
4. **User language**: Respond in user's language
