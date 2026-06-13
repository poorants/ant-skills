---
name: engram
description: >
  Networked PARA document brain. Organizes documents into Projects, Areas,
  Resources, and Archives, AND weaves them into a connected knowledge graph
  via bi-directional links, MOC hub notes, and integrity linting. Layers a
  logical link network on top of physical folders so the vault grows like an
  interconnected brain rather than isolated folders. Use when the user wants
  to manage/organize docs, create meeting notes, archive projects, review
  documentation status, OR connect notes, check link integrity, find orphan
  documents, build a knowledge graph, or update MOCs.
  Triggers: "문서 관리해줘", "프로젝트 문서화해줘", "회의록 저장해줘",
  "para 정리해줘", "문서 아카이브해줘", "문서 리뷰해줘", "문서 검색해줘",
  "문서 마이그레이션", "기존 문서 정리",
  "지식망 정리", "노트 연결해줘", "링크 점검", "링크 무결성", "깨진 링크",
  "외톨이 문서", "외톨이 노드", "MOC 갱신", "지식 그래프", "브레인 점검",
  "manage documents", "organize docs", "archive project", "review docs",
  "create meeting notes", "move document", "list documents", "search docs",
  "para init", "para review", "para migrate", "migrate docs", "import docs",
  "connect notes", "link notes", "check links", "lint links", "find orphans",
  "knowledge graph", "update moc", "engram lint", "engram link"
---

# engram — Networked PARA Document Brain

문서를 PARA 방법으로 관리하는 동시에, 쌍방향 링크·MOC 허브·무결성 린트로
**하나의 연결된 지식망(브레인)**으로 키운다. 물리적 분류(폴더) 위에 논리적
연결(링크) 레이어를 얹는 'Networked PARA'가 핵심이다.

두 개의 층으로 동작한다.

- **관리 층 (PARA)**: 생성·이동·아카이브·마이그레이션·리뷰. 폴더가 거버넌스를 맡는다.
- **연결 층 (Networked Knowledge)**: 문서를 맥락 링크로 잇고, 외톨이를 없애고,
  깨진 링크를 잡는다. 링크가 맥락을 맡는다. 상세 규칙은
  [references/linking-rules.md](references/linking-rules.md)를 로드해 따른다.

## Path Resolution (do this first)

Before any operation, resolve the **PARA base** — the location where the four
category folders live. This is the first step of every workflow.

1. If the project root already contains any of `projects/`, `areas/`,
   `resources/`, or `archives/` → **flat mode**. The base is the project root
   itself; categories are `projects/`, `areas/`, `resources/`, `archives/`
   (no `para/` prefix).
2. Otherwise → **nested mode**. The base is `para/`; categories are
   `para/projects/`, `para/areas/`, and so on.
3. If the project's `CLAUDE.md` states a documentation-layout convention
   explicitly, that convention wins over the heuristic above.
4. Once the mode is determined, stay consistent within that project.

Throughout this document, `<base>/` denotes the resolved base — an empty prefix
in flat mode, or `para/` in nested mode. Every path below is written relative to
it.

**연결 층(링크·MOC·린트)의 대상 범위**: 무결성 린트(`engram_lint.py`)는 `para/`
아래만 대상으로 한다(`--base`로 변경 가능). 맥락 링크·MOC 규칙은 해결된 `<base>/`
전반에 적용한다.

## Quick Reference

| Category | Path | Purpose | Lifespan |
|----------|------|---------|----------|
| **Projects** | `<base>/projects/` | Active work with deadlines and goals | Temporary — archive on completion |
| **Areas** | `<base>/areas/` | Ongoing responsibilities without end date | Persistent — review periodically |
| **Resources** | `<base>/resources/` | Reference material and collected knowledge | Persistent — update as needed |
| **Archives** | `<base>/archives/` | Completed or inactive items from above | Permanent — read-only storage |

## Init Workflow

**When**: First PARA interaction OR the category folders are missing.
**Auto-execute without confirmation** — this operation is idempotent.

Resolve the base first (see Path Resolution), then run
[scripts/init.py](scripts/init.py):

```bash
# flat mode — categories created at the project root
python scripts/init.py --output . --flat

# nested mode — categories created under para/
python scripts/init.py --output .
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
- `<base>/projects/website-redesign/requirements.md`
- `<base>/areas/team-onboarding.md`
- `<base>/resources/api-reference.md`
- `<base>/projects/website-redesign/2024-03-15-kickoff-notes.md`

### Step 4: Write Content

Use plain markdown. No frontmatter required. Start with an H1 title.

**Simple document template:**
```markdown
# [Title]

[Content starts here]
```

**Directory with multiple files:**
```
<base>/projects/website-redesign/
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

### Step 5: Connect (Networked Knowledge)

문서를 만든 직후, 외톨이로 남지 않게 지식망에 잇는다. 상세는
[references/linking-rules.md](references/linking-rules.md)를 따른다.

1. **인바운드 링크 확보**: 새 문서가 관련된 기존 문서나 해당 폴더 `README.md`(MOC)에서
   최소 1개 이상의 링크를 받게 한다. 외톨이 노드는 유실된다.
2. **맥락적 링크**: 본문 흐름에 `[[파일명]]` 위키링크를 자연스럽게 녹인다. 하단에
   "관련 링크" 목록을 나열하지 않는다.
3. **MOC 갱신**: 해당 폴더 `README.md`에 새 문서로 가는 한 줄 링크를 추가한다.
4. **참고 자료 접지**: `resources/` 문서라면 내 해석이 담긴 `areas/`·`projects/`
   문서로도 연결해 지식망에 접지시킨다.

### Step 6: Confirm and Report

After creation, report:
- Full path of the created file
- Which PARA category it was placed in
- Brief summary of what was created
- 어떤 문서/MOC에서 인바운드 링크를 받게 되었는지 (연결 상태)

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
- 제외: 이미 PARA 카테고리 안에 있는 문서(flat 모드는 루트의
  `projects/`·`areas/`·`resources/`·`archives/`, nested 모드는 `para/`),
  그리고 `.git/`, `node_modules/` 등 비문서 디렉토리
- 루트 메타데이터 파일 제외: `README.md`, `LICENSE`, `CHANGELOG.md` 등

제외 패턴 상세는 `references/migration-patterns.md`를 참조한다.

### Step 2: Classify

각 문서의 내용을 읽고 PARA 분류를 결정한다.

- `references/para-categories.md`의 분류 플로차트를 활용
- 파일명/경로 힌트와 내용 키워드로 판단
- 불확실한 문서는 "수동 분류 필요"로 표시

분류 휴리스틱 상세는 `references/migration-patterns.md`를 참조한다.

### Step 3: Present Migration Plan

분류 결과를 마이그레이션 계획으로 출력한다. 목적지 경로는 해결된 base를 따른다
(flat 모드 예시).

```
## Migration Plan

### Classified (12 files)
| Source | Destination | Reason |
|--------|-------------|--------|
| docs/api-spec.md | resources/api-spec.md | Reference material |
| old/roadmap.md | projects/roadmap.md | Active project with deadline |

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

1. Init Workflow로 `<base>/` 구조 보장
2. Bash `mv`로 파일 이동
3. 관련 파일 그룹(같은 디렉토리의 연관 파일)은 디렉토리 구조 유지
4. 디렉토리 처리 상세는 `references/migration-patterns.md` 참조

### Step 6: Report

이동 결과를 보고한다.

```
## Migration Report

### Completed (11 files)
- docs/api-spec.md → resources/api-spec.md
- old/roadmap.md → projects/roadmap.md

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

Use Grep to search document content across the PARA base.
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

## Link & Connect Workflow (Networked Knowledge)

**When**: 사용자가 노트를 연결하거나, 지식망을 정리하거나, 외톨이 문서를 잇거나,
MOC를 갱신하려 할 때. ("노트 연결해줘", "지식망 정리", "MOC 갱신", "외톨이 이어줘")

먼저 [references/linking-rules.md](references/linking-rules.md)를 로드한다.

1. **현황 파악**: Integrity Lint Workflow를 돌려 외톨이·깨진 링크 목록을 얻는다.
2. **외톨이 연결**: 각 외톨이 문서의 내용을 읽고, 의미적으로 관련된 기존 문서를
   Grep/Glob으로 찾아 **그 기존 문서 본문에 맥락적 위키링크**를 심거나, 해당 폴더
   `README.md`(MOC)에 한 줄 링크를 추가한다. 억지 링크가 아니라 실제 관련이 있는
   곳에만 잇는다.
3. **MOC 정비**: 각 폴더 `README.md`가 그 폴더의 문서들을 입구로서 엮고 있는지
   점검하고, 빠진 링크를 채운다.
4. **재검사**: 다시 lint를 돌려 외톨이/깨진 링크가 줄었는지 확인하고 보고한다.

**억지로 연결하지 않는다.** 관련 없는 문서를 링크로 잇는 것은 over-structuring이며
지식망의 신호를 흐린다. 관련 노트가 없으면 외톨이로 남겨두고 사용자에게 알린다.

## Integrity Lint Workflow

**When**: 사용자가 링크 무결성을 점검하거나, 깨진 링크/외톨이를 찾으려 할 때.
다른 워크플로우(Create·Move·Migrate·Review)의 마무리 점검으로도 호출한다.

`para/` 아래 문서의 깨진 링크와 외톨이 노드를 탐지한다. 대상 저장소 루트에서
[scripts/engram_lint.py](scripts/engram_lint.py)를 실행한다.

```bash
# 사람용 리포트 (문제 없으면 무음)
python "<skill_dir>/scripts/engram_lint.py"

# 기계용 JSON — 스킬이 파싱해 후속 조치
python "<skill_dir>/scripts/engram_lint.py" --json

# base 디렉토리 변경 (기본 para)
python "<skill_dir>/scripts/engram_lint.py" --base docs --json
```

`<skill_dir>`는 이 SKILL.md가 있는 디렉토리다. 플러그인으로 설치된 경우
`${CLAUDE_PLUGIN_ROOT}/skills/engram/scripts/engram_lint.py` 형태로 호출한다.

결과 처리:
- **깨진 마크다운 링크(broken_md_links)**: 실재하지 않는 경로 → 올바른 경로로
  고치거나, 대상 문서를 만들거나, 오타면 수정한다.
- **외톨이(orphans)**: Link & Connect Workflow로 인바운드 링크를 잇는다.
- **미연결 위키링크(dangling_wikilinks)**: 경고일 뿐이다. 오타면 고치고, 아직 안 만든
  미래 노트면 그대로 둔다(의도된 forward link). 사용자에게 만들지 물어볼 수 있다.

종료 코드는 항상 0이라 작업을 막지 않는다 — 보고하고 함께 고친다.

## Rules

1. **Auto-init**: If the category folders don't exist when any PARA operation is requested, create them automatically without asking. This is idempotent and safe.

2. **Never delete**: Documents are never deleted. Inactive items are moved to `archives/`. If the user explicitly asks to delete, warn them and suggest archiving instead. Only proceed with deletion after the user confirms twice.

3. **Hybrid structure**: Items can be either a single file (`topic.md`) or a directory with multiple files (`topic/*.md`). Choose based on expected deliverables.

4. **Naming convention**: All files and directories use `kebab-case`. Date prefixes (`YYYY-MM-DD-`) for time-sensitive documents. No spaces, no uppercase in filenames.

5. **Plain markdown**: No frontmatter, no special syntax. Documents are plain markdown files starting with an H1 heading. **Never use horizontal rules (`---`)** — YAML frontmatter parsers may misinterpret them as frontmatter block delimiters, causing parse errors.

6. **Archive confirmation**: Moving items to archives always requires explicit user confirmation. Never auto-archive. Present candidates and wait for approval.

7. **User language**: Respond in the user's language. Document content follows the user's preference. PARA category directory names are always in English.

8. **Relative paths**: When reporting paths to the user, use paths relative to the project root (e.g., `projects/my-doc.md` in flat mode, `para/projects/my-doc.md` in nested mode).

9. **Migration safety**: Migrate는 파일을 이동하는 작업이므로 반드시 전체 마이그레이션 계획을 먼저 보여주고 사용자 승인을 받은 뒤 실행한다. 절대 자동 마이그레이션하지 않는다.

10. **No orphans**: 새로 만든 모든 문서는 최소 1개 이상의 인바운드 링크(연관 문서 또는 MOC `README.md`)를 받아야 한다. 연결되지 않은 지식은 유실된다.

11. **Contextual links**: 링크는 본문 서술 흐름에 자연스럽게 녹인다. 문서 하단에 "관련 링크" 목록을 나열하지 않는다. 억지 연결(over-structuring)은 지양하고 실제 관련 있는 곳에만 잇는다.

12. **MOC as hub**: 각 폴더의 `README.md`는 그 폴더 문서들의 입구(MOC)다. 문서를 추가·이동하면 관련 MOC도 함께 갱신한다.

13. **Lint scope**: 무결성 린트(`engram_lint.py`)는 `para/` 아래만 대상으로 한다. 비차단(보고만 하고 작업을 막지 않음)이며, 미연결 위키링크는 의도된 미래 노트일 수 있으므로 오류가 아닌 경고로 다룬다.
