---
name: skill-doctor
description: >
  Diagnose and fix health issues in local Claude Code skills.
  Runs mechanical checks (orphan files, broken references, size budget,
  trigger overlap) and AI-powered analysis (content consistency, token
  optimization, project alignment, CLAUDE.md sync, merge candidates).
  Triggers: "skill doctor", "스킬 검진", "스킬 체크", "스킬 진단",
  "check skills", "diagnose skills", "skill health", "fix skills",
  "스킬 고쳐줘", "스킬 분석", "skill analyze"
---

# Skill Doctor

Diagnose and fix health issues in local project skills. Combines mechanical checks (scripted) with AI-powered analysis for comprehensive skill quality assessment.

## Health Check Workflow (Default)

**When**: User wants to check skill health, or triggers this skill.

### Step 1: Run Mechanical Checks

Execute the health check script on the target path:

```bash
python scripts/health_check.py <path>
```

Where `<path>` is either:
- A skills directory (e.g., `.claude/skills/`, `skills/`) to check all skills
- A single skill directory (e.g., `skills/para-docs`) to check one skill

The script auto-detects single vs. multi-skill mode by checking for `SKILL.md`.

#### Mechanical Check Summary

| # | Check | What It Finds |
|---|-------|---------------|
| 3 | Orphan files | Files in scripts/references/assets not referenced in SKILL.md |
| 4 | Broken references | Backtick paths in SKILL.md pointing to missing files |
| 5 | Size budget | Line count (>500) and estimated tokens (>5000) |
| 7 | Trigger overlap | Shared trigger words between skills |

Severity levels: **ERR** (functional issue) / **WARN** (quality concern) / **INFO** (improvement opportunity)

### Step 2: AI Checks

After reviewing mechanical results, perform AI-powered analysis. Load `references/ai-checks.md` for detailed procedures.

| # | Check | What to Look For |
|---|-------|-----------------|
| 1 | Content consistency | Contradictory instructions, outdated patterns |
| 2 | Token optimization | Inline content that should be split to scripts/references/assets |
| 6 | Project alignment | Hardcoded paths/commands that don't match the actual project |
| 8 | CLAUDE.md sync | Conflicts between skill instructions and project CLAUDE.md rules |
| 9 | Merge candidates | Functionally similar skills that could be combined |

For each AI check:
1. Read the SKILL.md content
2. Analyze against the criteria in `references/ai-checks.md`
3. Record findings with severity

### Step 3: Integrated Report

Combine mechanical and AI results into a single report:

```
=== Skill Doctor Report ===
Skills: N checked

-- skill-name --
  [orphan]   WARN  references/unused.md -- not referenced in SKILL.md
  [broken]   ERR   references/old.md -- referenced at line 55 but missing
  [budget]   OK    318/500 lines, ~2300/5000 tokens
  [trigger]  INFO  overlap with other-skill: "keyword" (0.25)
  [content]  WARN  Step 3 contradicts Rule 2 (auto-delete vs never-delete)
  [token]    INFO  Inline template at lines 80-120 could move to references/
  [project]  OK    All paths verified
  [claudemd] OK    No conflicts with CLAUDE.md
  [merge]    INFO  Similar scope to other-skill -- consider combining

-- SUMMARY --
ERR: 1 | WARN: 2 | INFO: 3
```

## Fix Workflow

**When**: User explicitly requests fixes (e.g., "fix skills", "스킬 고쳐줘").

### Step 1: Run Health Check

Execute the full Health Check Workflow above to get the current report.

### Step 2: Propose Fixes

For each finding, propose a specific fix:

- **ERR** items: Always propose a fix
- **WARN** items: Propose a fix with explanation
- **INFO** items: Mention as optional improvements

Present all proposals as a numbered list with before/after previews where applicable.

### Step 3: Confirm and Apply

Ask user which fixes to apply. Options:
- "All" — apply everything
- Specific numbers — apply selected fixes
- "ERR only" — fix only errors

Apply approved fixes using Edit tool. Never auto-apply without confirmation.

### Step 4: Re-check

Run the health check again to verify fixes resolved the issues. Report the before/after comparison.

## Rules

1. **Read before diagnosing**: Always read the full SKILL.md before running AI checks. Never diagnose based on filename alone.
2. **Non-destructive**: Health Check is read-only. Fix Workflow requires explicit confirmation for each change.
3. **Context-aware**: AI checks require reading the project's CLAUDE.md and understanding the project structure.
4. **Severity accuracy**: ERR = skill won't work correctly. WARN = quality/maintainability concern. INFO = optional improvement.
5. **User language**: Respond in the user's language. Report format stays in English for consistency.
