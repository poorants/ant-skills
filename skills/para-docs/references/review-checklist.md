# PARA Review Checklist

## Review Procedure

### 1. Projects Review

For each item in `para/projects/`:

- [ ] Is this project still active? (Last modified within 30 days)
- [ ] Does it have a clear goal or deadline?
- [ ] Are there any completed deliverables that should be archived?
- [ ] Is the project README/document up to date?

**Archive if**: Project is completed, cancelled, or inactive for >30 days.

### 2. Areas Review

For each item in `para/areas/`:

- [ ] Is this still an ongoing responsibility?
- [ ] Is the documentation current and accurate?
- [ ] Are there any items that have become project-specific?
- [ ] Does the content reflect current practices?

**Archive if**: Responsibility has ended or been transferred.

### 3. Resources Review

For each item in `para/resources/`:

- [ ] Is the information still accurate and relevant?
- [ ] Has this been superseded by newer material?
- [ ] Is it referenced by any active projects or areas?
- [ ] Does it need updates to reflect current tools/practices?

**Archive if**: Content is outdated or superseded.

## Archive Criteria

An item is an archive candidate when ANY of these conditions are met:

| Condition | Applies to |
|-----------|-----------|
| Last modified >30 days ago with no recent references | Projects |
| All tasks/checklist items are completed | Projects |
| Project was explicitly cancelled | Projects |
| Responsibility has been transferred or ended | Areas |
| Content has been superseded by newer material | Resources |
| Referenced tools or APIs are deprecated | Resources |

## Review Report Format

```markdown
## PARA Review Report — YYYY-MM-DD

### Archive Candidates
Items recommended for archiving (requires user confirmation):
- [ ] path/to/item — [reason]
- [ ] path/to/item — [reason]

### Needs Update
Items with potentially outdated content:
- path/to/item — [what needs updating]

### Recently Archived
Items archived since last review:
- path/to/item — archived on YYYY-MM-DD

### Summary
| Category  | Items | Archive Candidates | Needs Update |
|-----------|-------|--------------------|--------------|
| Projects  | X     | Y                  | Z            |
| Areas     | X     | Y                  | Z            |
| Resources | X     | Y                  | Z            |
| Archives  | X     | —                  | —            |
```

## Review Frequency

- **Projects**: Review weekly or at sprint boundaries
- **Areas**: Review monthly
- **Resources**: Review quarterly
- **Full PARA review**: At least once per quarter
