---
name: project-kickstart
description: Kick off a new project by shaping its concept together. Creates project folder, writes a concept book (CONCEPT.md), and researches relevant data sources/APIs. Trigger on "프로젝트 시작하자", "새 프로젝트 컨셉 잡자", "프로젝트 킥스타트", "프로젝트 기획", "컨셉북 만들어줘", "start a new project", "project kickstart", "let's plan a project".
---

# Project Kickstart

Quickly shape a new project's foundation. Have a conversation with the user to solidify the concept, research relevant tech and data sources along the way, and produce planning documents.

## Workflow

### Phase 1: Concept Interview & Research

Ask the user the following to outline the project. Keep it conversational — don't dump all questions at once.

Required:
- **Project name** and its meaning/origin
- **One-liner** — what does this project do
- **Target users** — who is it for
- **Core features** — at least 3
- **Revenue model** — ads, subscription, SaaS, open-source, etc.

Optional (only if the user has already decided):
- Tech stack preference
- Data sources / external APIs
- Deployment strategy
- Expansion plans

For undecided items, suggest options that fit the project's nature.

When external data or APIs come up in conversation, immediately research with WebSearch to verify availability — actual public APIs, open data portals, SaaS offerings, etc. Share findings in the conversation and save them for Phase 2 documentation.

### Phase 2: Project Folder & Documentation

1. Create the project directory
2. Write `CONCEPT.md` following this structure:

```markdown
# {Project Name} Concept Book

> **{Project Name}** = {name meaning/origin}
> {one-liner}

## 1. Project Overview
## 2. Tech Stack
## 3. Target Data Sources (if applicable)
## 4. Feature Roadmap (Phase 1 MVP / Phase 2 Expansion / Phase 3 Advanced)
## 5. Revenue Model
## 6. Future Expansion Plans
## 7. Directory Structure Blueprint
```

See [references/example_concept.md](references/example_concept.md) for a real example.

Sections can be added or removed to fit the project. E.g., skip "Target Data Sources" if none apply.

3. If research was done in Phase 1, compile it into a separate document (`DATA_SOURCES.md`, `API_RESEARCH.md`, etc.) and link from `CONCEPT.md`.

Research documents should include:
- API name, provider, link
- Key data offered
- Auth method (where to get API keys)
- Rate limits
- MVP priority recommendation

## Guidelines

- This skill produces **planning documents only**. No code scaffolding.
- Do not finalize what the user hasn't decided. Suggest, then confirm.
- Write the concept book in Korean by default (unless the user requests otherwise).
- The directory structure blueprint is markdown only — do not create actual folders.
