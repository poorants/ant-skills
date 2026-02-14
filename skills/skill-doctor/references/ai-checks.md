# AI Checks — Detailed Guide

Procedures for AI-powered skill analysis. Each check includes what to look for, how to analyze, and how to report findings.

## Check 1: Content Consistency

**Goal**: Find contradictory or outdated instructions within SKILL.md.

### Procedure

1. Read the full SKILL.md
2. List all rules, constraints, and behavioral instructions
3. Cross-check each pair for conflicts

### What to Flag

- A rule says "never do X" but a workflow step does X
- Two workflow steps give contradictory instructions for the same scenario
- Deprecated tool names or patterns (e.g., old API names)
- Inconsistent terminology (same concept called different names)

### Report Format

```
[content]  WARN  {description of contradiction} (lines N and M)
[content]  ERR   {outdated pattern}: {what it should be}
```

## Check 2: Token Optimization

**Goal**: Identify inline content that should be extracted to scripts/references/assets.

### Procedure

1. Identify large blocks in SKILL.md:
   - Code blocks > 15 lines
   - Tables > 10 rows
   - Repeated templates or boilerplate
   - Reference material not needed for core workflow understanding
2. Estimate token savings from extraction

### What to Flag

- Templates that could be `references/template-name.md`
- Long code examples that could be `scripts/example.py`
- Static data tables that could be `references/data.md`
- Content only needed in specific workflows (progressive disclosure candidate)

### Report Format

```
[token]    INFO  Lines {N}-{M}: {description} (~{tokens} tokens, move to {target})
[token]    WARN  SKILL.md at ~{N} estimated tokens, {percentage}% over budget
```

## Check 6: Project Alignment

**Goal**: Verify hardcoded paths, commands, and assumptions match the actual project.

### Procedure

1. Extract all file paths mentioned in SKILL.md
2. Extract all shell commands
3. Verify paths exist in the project
4. Verify commands are valid for the project's tech stack
5. Check that referenced tools/languages are actually used

### What to Flag

- Path references to files/dirs that don't exist in the project
- Commands using tools not installed or not relevant
- Assumptions about project structure that don't hold
- Platform-specific commands without cross-platform alternatives (when relevant)

### Report Format

```
[project]  ERR   Path `{path}` referenced but does not exist
[project]  WARN  Command `{cmd}` assumes {tool} which is not in project
[project]  OK    All paths and commands verified
```

## Check 8: CLAUDE.md Sync

**Goal**: Detect conflicts between skill instructions and project CLAUDE.md rules.

### Procedure

1. Read the project's CLAUDE.md (project root)
2. Extract key rules and conventions
3. Compare with SKILL.md instructions
4. Check for contradictions or redundancies

### What to Flag

- Skill says "use X" but CLAUDE.md says "use Y" for the same thing
- Skill overrides a CLAUDE.md convention without acknowledgment
- Skill duplicates CLAUDE.md rules unnecessarily (token waste)
- Skill references CLAUDE.md conventions that have been removed

### Report Format

```
[claudemd] ERR   Skill says "{X}" but CLAUDE.md says "{Y}"
[claudemd] WARN  Skill duplicates CLAUDE.md rule: {rule summary}
[claudemd] OK    No conflicts with CLAUDE.md
```

## Check 9: Merge Candidates

**Goal**: Identify functionally similar skills that could be combined.

### Procedure

1. Read descriptions of all skills in the same plugin/directory
2. Compare scopes: do two skills address the same domain?
3. Check for workflow overlap: do they share similar steps?
4. Evaluate whether merging would simplify or complicate

### What to Flag

- Two skills that handle the same domain (e.g., two doc managers)
- Skills with >50% trigger word overlap (from mechanical check)
- Skills that are always used together
- Skills where one is a strict subset of another

### Report Format

```
[merge]    WARN  {skill-a} and {skill-b}: overlapping scope ({description})
[merge]    INFO  {skill-a} could absorb {skill-b} ({rationale})
[merge]    OK    No merge candidates found
```

## General Guidelines

- Always read full SKILL.md content before analysis — never judge by filename
- Use ERR only when the issue would cause the skill to malfunction
- Use WARN for quality/maintainability concerns that affect effectiveness
- Use INFO for optional improvements
- Include line numbers when referencing specific SKILL.md content
- Keep findings actionable — always suggest what to do about it
