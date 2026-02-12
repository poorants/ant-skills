# PARA Categories Reference

## Category Definitions

### Projects
**Active work with a clear goal and deadline.**

- Has a defined outcome or deliverable
- Has a deadline (explicit or implicit)
- Requires multiple steps or tasks to complete
- Will eventually be "done" and archived

Examples: product launch, website redesign, hiring process, quarterly report, feature implementation

### Areas
**Ongoing responsibilities with a standard to maintain.**

- No end date — continues indefinitely
- Has a standard or level to maintain
- Requires regular attention and updates
- Part of your role or ongoing commitments

Examples: team management, product quality, customer support processes, security practices, onboarding documentation

### Resources
**Reference material and collected knowledge.**

- Information you want to keep for future reference
- Not tied to a specific project or responsibility
- Useful across multiple contexts
- Collected over time, updated as needed

Examples: coding style guides, API documentation, design patterns, meeting templates, tool comparisons, how-to guides

### Archives
**Completed, cancelled, or inactive items from other categories.**

- Items that are no longer active
- Preserved for historical reference
- Should not be modified (read-only by convention)
- Can be reactivated by moving back to the original category

Examples: completed projects, ended responsibilities, outdated references

## Classification Flowchart

When deciding where a new document belongs, follow this decision tree:

```
Is this item actively being worked on?
├── YES: Does it have a specific end goal or deadline?
│   ├── YES → Projects
│   └── NO: Is it an ongoing responsibility?
│       ├── YES → Areas
│       └── NO → Resources
└── NO: Was it previously active?
    ├── YES → Archives
    └── NO: Is it reference material?
        ├── YES → Resources
        └── NO → Ask the user for clarification
```

## Common Mistakes

| Mistake | Why it's wrong | Correct approach |
|---------|---------------|-----------------|
| Putting a one-off task in Areas | Areas are ongoing, not temporary | Use Projects for tasks with end dates |
| Putting meeting notes in Resources | Meeting notes are project-specific | Put under the relevant project directory |
| Keeping completed projects in Projects | Clutters active workspace | Move to Archives when done |
| Putting style guides in Areas | Style guides are reference material | Use Resources for knowledge base items |
| Creating top-level docs outside para/ | Breaks the PARA structure | All managed docs go under para/ |

## Movement Patterns

### Project Lifecycle
```
Projects → Archives          (completed or cancelled)
Archives → Projects          (reactivated)
```

### Area Transitions
```
Areas → Archives             (responsibility ended)
Areas → Projects             (specific initiative spun off)
Archives → Areas             (responsibility resumed)
```

### Resource Updates
```
Resources → Archives         (outdated, superseded)
Projects → Resources         (reusable artifacts extracted)
```

### When to Move

- **Project → Archive**: All deliverables complete, or project cancelled
- **Area → Archive**: You are no longer responsible for this area
- **Resource → Archive**: Information is outdated or superseded by newer material
- **Archive → Original**: Item becomes active again — move back to its original category
