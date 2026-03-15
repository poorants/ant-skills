---
name: init-permissions
description: >
  Grant all tool permissions to the current project for comfortable development.
  Triggers: "init permissions", "권한 설정", "권한 초기화", "grant permissions",
  "setup permissions", "퍼미션 설정"
---

# Init Permissions

Grant all Claude Code tool permissions to the current project.

## What It Does

Create `.claude/settings.local.json` with all permissions enabled:

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

## Steps

1. Check if `.claude/settings.local.json` exists
2. If exists, ask to overwrite or merge
3. Create `.claude/` directory if needed
4. Write permissions file
5. Report result:
   ```
   ✓ 권한 설정 완료 (.claude/settings.local.json)
   ```

## Rules

1. **Confirm overwrites**: Always ask before overwriting existing files
2. **User language**: Respond in user's language
