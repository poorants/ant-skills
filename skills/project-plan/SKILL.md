---
name: project-plan
description: "Manage project roadmap with phase-based planning and PDCA integration. Use when user says /project-plan, 'roadmap', 'project status', 'what phases remain', 'add phase', 'update roadmap', 'project progress', 'what should I work on next', or asks about overall project progress."
---

# project-plan: Project Roadmap Manager

Manage a phase-based project roadmap with automatic progress tracking via PDCA integration.

## Usage

```
/project-plan                 -- show roadmap dashboard (default)
/project-plan status          -- same as above
/project-plan init            -- create PROJECT-OVERVIEW.md + ROADMAP.md
/project-plan add             -- add a new phase
/project-plan update <phase>  -- update a phase
/project-plan next            -- recommend next work based on dependencies
/project-plan sync            -- sync progress from .pdca-status.json
```

## Output Path

Documents are generated in the user's project, not inside the skill directory.
The output path (`{output-dir}`) is determined during `init`:

- Default: `para/areas/` (follows PARA convention — roadmap is an ongoing Area)
- User can specify a custom path (e.g., `.`, `docs/`)

Once set, the path is stored in `.project-plan.json` at the project root:

```json
{
  "outputDir": "para/areas",
  "projectName": "my-project"
}
```

All commands read `.project-plan.json` to locate documents.
If the config file is missing, prompt the user to run `init` first.

## Data Sources

| Source | Purpose |
|--------|---------|
| `{output-dir}/PROJECT-OVERVIEW.md` | Project purpose, goals, scope (user-maintained) |
| `{output-dir}/ROADMAP.md` | Phase list, features, progress (skill-managed) |
| `.pdca-status.json` | Per-feature PDCA state and match rate (bkit-managed) |
| `.project-plan.json` | Output path and project config (skill-managed) |

## Commands

### `init`

Create initial project documents through a guided interview.

1. Ask the user for:
   - **Project name**
   - **Output directory** — where to save documents (default: project root)
   - **Purpose** — why this project exists
   - **Core goals** — 2-5 measurable objectives
   - **Scope** — what is included and excluded
   - **Tech stack** (optional)
2. Save config to `.project-plan.json`
3. Generate `{output-dir}/PROJECT-OVERVIEW.md` using [references/project-overview-template.md](references/project-overview-template.md)
4. Ask the user to define initial phases:
   - Phase number (auto-assign sequentially from 0)
   - Name and description
   - Features (map to PDCA feature names)
   - Dependencies (which phases must complete first)
5. Generate `{output-dir}/ROADMAP.md` using [references/roadmap-template.md](references/roadmap-template.md)
6. If `CONCEPT.md` exists in the project root, reference it for context during the interview

### `status` (default)

Display a progress dashboard.

1. Read `.project-plan.json` for output path
2. Read `{output-dir}/ROADMAP.md`
3. Read `.pdca-status.json` if it exists
4. Calculate progress per phase and overall
5. Present the dashboard:

```
Project Roadmap
================

Phase  Description          Features  Done  Progress  Status
-----  -------------------  --------  ----  --------  -----------
  0    Foundation           3         2     67%       In Progress
  1    Core features        4         0     0%        Planned
  2    Extensions           3         0     0%        Blocked
─────────────────────────────────────────────────────────────────
       Total                10        2     20%

Status: 1/3 phases done, 1 in progress
Next recommended: Phase 0 — finish db-schema
```

### `add`

Add a new phase to the roadmap.

1. Read `.project-plan.json` for output path
2. Read current `{output-dir}/ROADMAP.md`
3. Ask the user for:
   - Phase number (default: next available)
   - Phase name and description
   - Features (list of PDCA feature names)
   - Dependencies (phase numbers that must complete first)
4. Append to `{output-dir}/ROADMAP.md` Phases section
5. Update the Progress table
6. Add a Changelog entry

### `update <phase>`

Modify an existing phase.

1. Find the phase by number or name
2. Ask what to update: description, features, dependencies, status, or notes
3. Update `{output-dir}/ROADMAP.md`
4. Recalculate progress if features changed
5. Add a Changelog entry

### `next`

Recommend what to work on next.

1. Read `{output-dir}/ROADMAP.md` and `.pdca-status.json`
2. Find phases where all dependencies are satisfied (Done)
3. Among those, find phases with status Planned or In Progress
4. Within the selected phase, find features not yet started or in progress
5. Recommend the feature and provide the PDCA command:
   ```
   Next up: Phase 1 — "Core features"
   Suggested feature: user-auth
   Start with: /pdca plan user-auth
   ```

### `sync`

Synchronize ROADMAP.md progress from PDCA state.

1. Read `.pdca-status.json`
2. For each feature listed, update its status in `{output-dir}/ROADMAP.md`:
   - matchRate >= 90% → mark `[x]` with "(Done, {rate}%)"
   - PDCA phase exists → mark `[ ]` with "(In Progress, {phase})"
3. Recalculate phase progress percentages
4. Update the Progress summary table
5. Add a Changelog entry noting what changed

## Status Definitions

| Status | Condition |
|--------|-----------|
| **Done** | All features have matchRate >= 90% in `.pdca-status.json` |
| **In Progress** | At least one feature has a PDCA entry (phase < completed) |
| **Planned** | In roadmap, no features started |
| **Blocked** | Dependencies not yet satisfied (prerequisite phase not Done) |

## Progress Calculation

```
Feature status:
  Done        = .pdca-status.json matchRate >= 90%
  InProgress  = PDCA phase exists (plan, design, do, check)
  Planned     = registered in ROADMAP.md, no PDCA entry

Phase progress  = count(Done features) / count(total features) × 100%
Overall progress = count(all Done features) / count(all features) × 100%
```

## Rules

- Phase numbers are stable once assigned — never renumber
- A phase can contain multiple PDCA features
- A PDCA feature belongs to exactly one phase
- The `sync` command is the bridge between PDCA state and the roadmap
- `PROJECT-OVERVIEW.md` is user-maintained; the skill reads but does not overwrite it
- `ROADMAP.md` is skill-managed; manual edits are preserved during sync
- All generated documents are written in English
- When `CONCEPT.md` exists, use it as context for `init` but do not modify it
