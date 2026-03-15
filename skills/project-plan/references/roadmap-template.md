# Roadmap Template

> Used by the `project-plan` skill to generate `ROADMAP.md`.
> Replace `{placeholders}` with actual values.

---

```markdown
# {Project Name} Roadmap

## Progress

| Phase | Description | Features | Done | Progress | Status |
|-------|-------------|----------|------|----------|--------|
| 0 | {phase-0-desc} | {n} | {d} | {p}% | {status} |
| 1 | {phase-1-desc} | {n} | {d} | {p}% | {status} |
| **Total** | | **{N}** | **{D}** | **{P}%** | |

## Phases

### Phase 0: {Phase Name}
- **Status**: {Done | In Progress | Planned | Blocked}
- **Dependencies**: None
- **Description**: {What this phase accomplishes}
- **Features**:
  - [ ] {feature-name-1} (Planned)
  - [ ] {feature-name-2} (Planned)

### Phase 1: {Phase Name}
- **Status**: Planned
- **Dependencies**: Phase 0
- **Description**: {What this phase accomplishes}
- **Features**:
  - [ ] {feature-name-3} (Planned)
  - [ ] {feature-name-4} (Planned)

## Changelog

- {YYYY-MM-DD}: Roadmap created with Phase 0–{N}
```

---

## Status Values

Use these exact strings for consistency:

| Value | Meaning |
|-------|---------|
| `Done` | All features have matchRate >= 90% |
| `In Progress` | At least one feature has a PDCA entry |
| `Planned` | No features started yet |
| `Blocked` | Dependency phase not Done |

## Feature Line Format

Features use GitHub-flavored markdown checkboxes:

```markdown
- [x] {feature-name} (Done, {matchRate}%)
- [ ] {feature-name} (In Progress, {pdca-phase})
- [ ] {feature-name} (Planned)
```

## Changelog Entry Format

```markdown
- {YYYY-MM-DD}: {Action} — {Details}
```

Actions: `Roadmap created`, `Phase added`, `Phase updated`, `Sync completed`, `Feature added`, `Feature completed`
