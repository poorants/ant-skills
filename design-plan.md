# Claude Skills 저장소 설계 계획서

## Context

Claude Code 스킬을 중앙에서 개발, 관리, 배포하기 위한 전용 저장소를 만든다. 현재 프로젝트별 `.claude/skills/`에 흩어진 범용 스킬을 한곳에서 관리하고, 공식 마켓플레이스 배포를 지원한다.

기존 docs 프로젝트의 스킬(concept-pool-generator, sprint-report 등)은 해당 프로젝트 전용이므로 이동하지 않는다.

## 공식 구조 조사 결과

> 출처: [github.com/anthropics/skills](https://github.com/anthropics/skills), [agentskills.io/specification](https://agentskills.io/specification)

### 마켓플레이스 등록 핵심

공식 저장소(`anthropics/skills`)의 구조를 분석한 결과, 마켓플레이스 등록에 필요한 핵심 요소는 다음과 같다.

**1. `.claude-plugin/marketplace.json`**

이 파일이 마켓플레이스 등록의 핵심이다. Anthropic 공식 예시:

```json
{
  "name": "anthropic-agent-skills",
  "owner": {
    "name": "Keith Lazuka",
    "email": "klazuka@anthropic.com"
  },
  "metadata": {
    "description": "Anthropic example skills",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "document-skills",
      "description": "Collection of document processing suite...",
      "source": "./",
      "strict": false,
      "skills": [
        "./skills/xlsx",
        "./skills/docx",
        "./skills/pptx",
        "./skills/pdf"
      ]
    },
    {
      "name": "example-skills",
      "description": "Collection of example skills...",
      "source": "./",
      "strict": false,
      "skills": ["./skills/algorithmic-art", "./skills/brand-guidelines"]
    }
  ]
}
```

- `plugins` 배열: 스킬을 논리적 그룹(플러그인)으로 묶음
- 각 플러그인의 `skills` 배열: 해당 플러그인에 포함되는 스킬 디렉토리 경로
- 설치 명령: `/plugin install my-skills@ant-skills`

**2. Agent Skills 스펙 (SKILL.md)**

| 필드            | 필수 | 제약                                                                             |
| --------------- | ---- | -------------------------------------------------------------------------------- |
| `name`          | Yes  | 최대 64자. 소문자, 숫자, 하이픈만. 시작/끝에 하이픈 불가. 디렉토리명과 일치 필수 |
| `description`   | Yes  | 최대 1024자. 스킬의 기능과 사용 시점을 설명                                      |
| `license`       | No   | 라이선스명 또는 파일 참조                                                        |
| `compatibility` | No   | 최대 500자. 환경 요구사항                                                        |
| `metadata`      | No   | 임의 key-value                                                                   |
| `allowed-tools` | No   | 공백 구분 도구 목록 (실험적)                                                     |

**3. Progressive Disclosure 원칙**

1. **메타데이터** (~100 토큰): `name`/`description` → 모든 스킬에서 시작 시 로드
2. **Instructions** (< 5000 토큰 권장): `SKILL.md` 본문 → 스킬 활성화 시 로드
3. **Resources** (필요 시): `scripts/`, `references/`, `assets/` → 필요할 때만 로드

`SKILL.md`는 500줄 이하로 유지. 상세 레퍼런스는 별도 파일로 분리.

### Anthropic 저장소 실제 구조

```
anthropics/skills/
├── .claude-plugin/
│   └── marketplace.json    ← 마켓플레이스 등록 설정
├── skills/                 ← 스킬 소스
│   ├── xlsx/
│   ├── docx/
│   ├── pptx/
│   ├── pdf/
│   ├── algorithmic-art/
│   ├── brand-guidelines/
│   └── ...
├── spec/                   ← 공식 스펙 (→ agentskills.io로 이전됨)
├── template/
│   └── SKILL.md            ← 스킬 템플릿
├── .gitignore
├── README.md
└── THIRD_PARTY_NOTICES.md
```

## 수정된 저장소 구조

기존 계획의 커스텀 스크립트(deploy.py, package.py 등) 대신, 공식 마켓플레이스 구조를 따른다.

```
claude-skills/
├── .claude-plugin/
│   └── marketplace.json    # 마켓플레이스 등록 (핵심)
├── CLAUDE.md               # 프로젝트 규칙 (스킬 작성 컨벤션)
├── README.md               # 저장소 설명, 설치 방법
├── skills/                 # 스킬 소스
│   ├── my-first-skill/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   ├── references/
│   │   └── assets/
│   └── another-skill/
│       └── SKILL.md
├── template/
│   └── SKILL.md            # 새 스킬 생성용 템플릿
├── scripts/                # 저장소 관리 도구
│   └── validate.py         # 스킬 구조 검증 (선택)
└── .gitignore
```

### 변경 사항 요약

| 기존 계획                    | 수정 계획                              | 이유                                                     |
| ---------------------------- | -------------------------------------- | -------------------------------------------------------- |
| `deploy.py` (유저 레벨 배포) | 제거                                   | 마켓플레이스 설치로 대체 (`/plugin install`)             |
| `package.py` (.skill 패키징) | 제거                                   | GitHub 저장소 자체가 배포 단위                           |
| `validate.py`                | 유지 (선택)                            | 로컬 검증용. 공식 도구 `skills-ref validate`도 사용 가능 |
| `dist/`                      | 제거                                   | 패키징 불필요                                            |
| (없음)                       | `.claude-plugin/marketplace.json` 추가 | 마켓플레이스 등록 필수                                   |
| (없음)                       | `template/SKILL.md` 추가               | 새 스킬 생성 편의                                        |

## 배포 워크플로우 (수정)

```
[스킬 개발]                    [배포]                        [사용자 설치]
skills/ 에서 작성           →  GitHub에 push               → /plugin install my-skills@ant-skills
marketplace.json에 등록                                       자동으로 스킬 사용 가능
```

### 사용자 설치 방법

```bash
# 마켓플레이스 등록 (1회)
/plugin marketplace add poorants/ant-skills

# 플러그인 설치
/plugin install my-skills@ant-skills
```

## marketplace.json (우리 저장소)

```json
{
  "name": "ant-skills",
  "owner": {
    "name": "Donghun Kim"
  },
  "metadata": {
    "description": "Custom Claude skills collection by poorants",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "my-skills",
      "description": "범용 스킬 모음",
      "source": "./",
      "strict": false,
      "skills": ["./skills/my-first-skill"]
    }
  ]
}
```

## SKILL.md 템플릿

```yaml
---
name: template-skill
description: Replace with description of the skill and when Claude should use it.
---
# Insert instructions below
```

## 검증 방법

1. 공식 도구: `skills-ref validate ./skills/스킬명`
2. 로컬 검증: `python scripts/validate.py --all` (선택적으로 유지)
3. GitHub에 push 후 `/plugin install`로 실제 설치 테스트

## 참고 링크

- [Agent Skills 공식 스펙](https://agentskills.io/specification)
- [Anthropic 공식 스킬 저장소](https://github.com/anthropics/skills)
- [스킬이란?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [스킬 사용법](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [커스텀 스킬 생성](https://support.claude.com/en/articles/12512198-creating-custom-skills)
