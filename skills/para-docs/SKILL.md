---
name: para-docs
description: >
  PARA-based project documentation manager. Organizes documents into
  Projects, Areas, Resources, and Archives under a para/ directory.
  Use when the user wants to manage documents, organize docs, create
  meeting notes, archive projects, or review documentation status.
  Triggers: "문서 관리해줘", "프로젝트 문서화해줘", "회의록 저장해줘",
  "para 정리해줘", "문서 아카이브해줘", "문서 리뷰해줘", "문서 검색해줘",
  "문서 마이그레이션", "기존 문서 정리",
  "manage documents", "organize docs", "archive project", "review docs",
  "create meeting notes", "move document", "list documents", "search docs",
  "para init", "para review", "para migrate", "migrate docs", "import docs"
---

# PARA Document Manager

Manage project documentation using the PARA method. All documents live under `para/` in the project root.

## Quick Reference

| Category | Path | Purpose | Lifespan |
|----------|------|---------|----------|
| **Projects** | `para/projects/` | Active work with deadlines and goals | Temporary — archive on completion |
| **Areas** | `para/areas/` | Ongoing responsibilities without end date | Persistent — review periodically |
| **Resources** | `para/resources/` | Reference material and collected knowledge | Persistent — update as needed |
| **Archives** | `para/archives/` | Completed or inactive items from above | Permanent — read-only storage |

## Init Workflow

**When**: First `para/` interaction OR `para/` directory missing.
**Auto-execute without confirmation** — this operation is idempotent.

Run a single Bash command to create the full structure:

```bash
mkdir -p para/projects para/areas para/resources para/archives && touch para/projects/.gitkeep para/areas/.gitkeep para/resources/.gitkeep para/archives/.gitkeep
```

Report what was created.

## Create Workflow

**When**: User wants to create a new document or documentation item.

### Step 1: Determine Category

Ask the user or infer from context. Use the classification guide:
- Has a deadline or specific goal? → **Projects**
- Ongoing responsibility, no end date? → **Areas**
- Reference material for future use? → **Resources**

If uncertain, load `references/para-categories.md` for the detailed classification flowchart.

### Step 2: Determine Structure

**Simple item** (single topic, standalone):
→ Create a single `.md` file directly in the category directory.

**Complex item** (multiple deliverables, ongoing outputs):
→ Create a directory containing multiple `.md` files as needed.

### Step 3: Choose Filename

Naming convention: `kebab-case.md`
- Use descriptive, lowercase names with hyphens
- Include date prefix for time-sensitive items: `YYYY-MM-DD-topic-name.md`
- For directories: `kebab-case/<document-name>.md`

Examples:
- `para/projects/website-redesign/requirements.md`
- `para/areas/team-onboarding.md`
- `para/resources/api-reference.md`
- `para/projects/website-redesign/2024-03-15-kickoff-notes.md`

### Step 4: Write Content

Use plain markdown. No frontmatter required. Start with an H1 title.

**Simple document template:**
```markdown
# [Title]

[Content starts here]
```

**Directory with multiple files:**
```
para/projects/website-redesign/
├── requirements.md
├── design-spec.md
├── 2024-03-15-kickoff-notes.md
└── 2024-03-20-review-notes.md
```

**Meeting notes template:**
```markdown
# [Meeting Title] — YYYY-MM-DD

## Attendees

- [Names]

## Agenda

1. [Topic]

## Notes

[Notes here]

## Action Items

- [ ] [Action item with owner]
```

### Step 5: Confirm and Report

After creation, report:
- Full path of the created file
- Which PARA category it was placed in
- Brief summary of what was created

## Move Workflow

**When**: User wants to relocate a document between PARA categories.

Common moves:
- `projects/` → `archives/` (project completed)
- `areas/` → `archives/` (responsibility ended)
- `resources/` → `archives/` (outdated reference)
- `archives/` → `projects/` (reactivating archived work)

Steps:
1. Identify the source file/directory using Glob
2. Determine the target category (ask user or infer)
3. Verify the target path does not already exist
4. Use Bash `mv` to move the item
5. Report the move: source → destination

**IMPORTANT: Never delete documents. Always move to archives instead.**

## Migrate Workflow

**When**: 기존 프로젝트에 산재된 문서를 PARA 구조로 일괄 재분류할 때.

### Step 1: Scan

Glob으로 프로젝트 전체 문서를 탐색한다.

- 대상: `**/*.md`, `**/*.txt`
- 제외: `para/`, `.git/`, `node_modules/` 등 비문서 디렉토리
- 루트 메타데이터 파일 제외: `README.md`, `LICENSE`, `CHANGELOG.md` 등

제외 패턴 상세는 `references/migration-patterns.md`를 참조한다.

### Step 2: Classify

각 문서의 내용을 읽고 PARA 분류를 결정한다.

- `references/para-categories.md`의 분류 플로차트를 활용
- 파일명/경로 힌트와 내용 키워드로 판단
- 불확실한 문서는 "수동 분류 필요"로 표시

분류 휴리스틱 상세는 `references/migration-patterns.md`를 참조한다.

### Step 3: Present Migration Plan

분류 결과를 마이그레이션 계획으로 출력한다.

```
## Migration Plan

### Classified (12 files)
| Source | Destination | Reason |
|--------|-------------|--------|
| docs/api-spec.md | para/resources/api-spec.md | Reference material |
| docs/roadmap.md | para/projects/roadmap.md | Active project with deadline |

### Manual Classification Needed (2 files)
| Source | Notes |
|--------|-------|
| notes/misc.md | Content unclear — user decision needed |

### Skipped (3 files)
| Source | Reason |
|--------|--------|
| README.md | Root metadata file |

### Summary
- Total scanned: 17 files
- Auto-classified: 12 files
- Manual needed: 2 files
- Skipped: 3 files
```

이름 충돌이 있으면 계획에 명시한다.

### Step 4: Confirm

**반드시 사용자 승인 후 실행한다.** 사용자는 다음을 변경할 수 있다:

- 개별 파일의 분류 변경
- 특정 파일 제외
- 커스텀 경로 지정

### Step 5: Execute

승인된 계획에 따라 파일을 이동한다.

1. Init Workflow로 `para/` 구조 보장
2. Bash `mv`로 파일 이동
3. 관련 파일 그룹(같은 디렉토리의 연관 파일)은 디렉토리 구조 유지
4. 디렉토리 처리 상세는 `references/migration-patterns.md` 참조

### Step 6: Report

이동 결과를 보고한다.

```
## Migration Report

### Completed (11 files)
- docs/api-spec.md → para/resources/api-spec.md
- docs/roadmap.md → para/projects/roadmap.md

### Skipped (1 file)
- notes/misc.md — user excluded

### Failed (0 files)

### Next Steps
- `para list`로 결과 확인
- `para review`로 분류 적정성 점검
```

## List & Search Workflow

**When**: User wants to see what documents exist or find specific content.

### List (Dashboard)

Generate a summary table for each non-empty PARA category:

```
## PARA Dashboard

### Projects (3 items)
| Name | Type | Last Modified |
|------|------|--------------|
| website-redesign | directory | 2024-03-15 |
| api-migration.md | file | 2024-03-10 |
| q2-planning.md | file | 2024-03-01 |

### Areas (2 items)
...
```

Use Glob to discover items and Bash `git log` or file stats for dates.

### Search

Use Grep to search document content across `para/`.
Use Glob to search by filename patterns.
Report results with file paths and matching context.

## Review Workflow

**When**: User requests a documentation review or periodic checkup.

Load `references/review-checklist.md` for the detailed review procedure.

Steps:
1. Generate the PARA Dashboard (see List workflow)
2. For each project: check if it should be archived (completed, stale >30 days)
3. For each area: check if documentation is current
4. For each resource: check if content is still relevant
5. Present findings as a review report
6. **Suggest** archive candidates — **never auto-archive**
7. Execute moves only after explicit user confirmation

Review report format:
```
## PARA Review Report — YYYY-MM-DD

### Archive Candidates
- [ ] projects/old-project — last modified 45 days ago
- [ ] resources/deprecated-api — superseded by new-api

### Needs Update
- areas/onboarding.md — last reviewed 60 days ago

### Summary
- Projects: X active, Y archive candidates
- Areas: X items, Y need review
- Resources: X items, Y outdated
- Archives: X items total
```

## Rules

1. **Auto-init**: If `para/` doesn't exist when any para operation is requested, create it automatically without asking. This is idempotent and safe.

2. **Never delete**: Documents are never deleted. Inactive items are moved to `archives/`. If the user explicitly asks to delete, warn them and suggest archiving instead. Only proceed with deletion after the user confirms twice.

3. **Hybrid structure**: Items can be either a single file (`topic.md`) or a directory with multiple files (`topic/*.md`). Choose based on expected deliverables.

4. **Naming convention**: All files and directories use `kebab-case`. Date prefixes (`YYYY-MM-DD-`) for time-sensitive documents. No spaces, no uppercase in filenames.

5. **Plain markdown**: No frontmatter, no special syntax. Documents are plain markdown files starting with an H1 heading. **Never use horizontal rules (`---`)** — YAML frontmatter parsers may misinterpret them as frontmatter block delimiters, causing parse errors.

6. **Archive confirmation**: Moving items to archives always requires explicit user confirmation. Never auto-archive. Present candidates and wait for approval.

7. **User language**: Respond in the user's language. Document content follows the user's preference. PARA category directory names are always in English.

8. **Relative paths**: When reporting paths to the user, use paths relative to the project root (e.g., `para/projects/my-doc.md`).

9. **Migration safety**: Migrate는 파일을 이동하는 작업이므로 반드시 전체 마이그레이션 계획을 먼저 보여주고 사용자 승인을 받은 뒤 실행한다. 절대 자동 마이그레이션하지 않는다.
