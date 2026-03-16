---
name: doc-review
description: "Review PDCA plan and design documents for critical issues only. Assumes non-critical items will be caught in later phases (design/dev/test for plan review; dev/test for design review). Supports iterative review cycles (1st review > fix > 2nd review). Use when the user says /doc-review, 'review document', 'review plan', 'review design', '문서 리뷰', '리뷰해줘', '검토해줘', or after creating/modifying plan or design documents."
---

# doc-review: Critical-Only Document Reviewer

## Purpose

Plan/Design 문서의 **크리티컬 이슈만** 잡아주는 리뷰어.
모든 걸 다 지적하면 리뷰 피로도만 올라가고, 어차피 후속 단계에서 잡힐 이슈까지
여기서 다 거론할 필요 없다. 이 스킬은 **후속 단계에서 잡기 어려운 핵심 미스**만 집중한다.

## Philosophy: Deferred Trust

| 리뷰 대상 | 신뢰하는 후속 단계 | 여기서 안 잡는 것 |
|-----------|-------------------|-----------------|
| **Plan 문서** | Design, 개발, 테스트 | 상세 API 시그니처, 구현 세부사항, 테스트 케이스 누락, 네이밍 |
| **Design 문서** | 개발, 테스트 | 사소한 타입 미스, 에러 코드 번호, 포맷 일관성, 테스트 벡터 정확도 |

## Usage

```
/doc-review plan <path>              -- Plan 문서 1차 리뷰
/doc-review design <path>            -- Design 문서 1차 리뷰 (코드도 참조)
/doc-review plan <path> --round 2    -- Plan 문서 2차 리뷰 (수정사항 확인)
/doc-review design <path> --round 2  -- Design 문서 2차 리뷰
```

## Execution Steps

### Step 0: Detect Document Type and Path

1. 인자에 `plan` 또는 `design` 키워드와 파일 경로가 있으면 해당 파일 사용
2. 인자가 없으면 사용자에게 리뷰 대상 문서 경로와 타입(plan/design)을 질문
3. `--round 2` 플래그가 있으면 2차 리뷰 모드

### Step 1: Read Context

1. 대상 문서 전체 읽기
2. **Plan 리뷰 시**: 연관 참조문서(요구사항, 스펙 등) 읽기
3. **Design 리뷰 시**: 대응 Plan 문서, 기존 코드베이스 구조, 유사 구현체 참조

### Step 2: Critical Review — Plan 체크리스트 (P-01 ~ P-07)

| ID | 항목 | 설명 |
|----|------|------|
| P-01 | 스코프 경계 불명확 | 이 기능이 어디까지인지 경계가 모호하면 설계·구현이 산으로 간다 |
| P-02 | 의존성 누락/오류 | 필요한 외부 모듈·서비스·라이브러리를 빠뜨렸거나 잘못 참조 |
| P-03 | 기술적 모순 | 문서 내에서 서로 충돌하는 기술적 서술 |
| P-04 | 표준/스펙 오해 | 참조 표준·RFC·스펙을 잘못 이해한 부분 |
| P-05 | 아키텍처 레이어 위반 | 정해진 아키텍처 경계를 넘는 의존이나 책임 배치 |
| P-06 | 빠진 핵심 요구사항 | 요구사항 문서에 있지만 Plan에서 누락된 항목 |
| P-07 | 리스크 미식별 | 명백한 기술적·일정 리스크가 언급되지 않음 |

### Step 2: Critical Review — Design 체크리스트 (D-01 ~ D-08)

| ID | 항목 | 설명 |
|----|------|------|
| D-01 | Plan과 불일치 | Design이 Plan의 결정사항과 다른 방향으로 감 |
| D-02 | 기존 코드와 충돌 | 현재 코드베이스의 구조·패턴과 맞지 않는 설계 |
| D-03 | API 계약 모호 | 입력/출력/에러 처리가 불명확해서 구현자마다 다르게 해석할 수 있음 |
| D-04 | 데이터 흐름 단절 | 데이터가 A→B→C로 흘러야 하는데 중간 경로가 빠져 있음 |
| D-05 | 메모리/리소스 관리 설계 결함 | 할당·해제·수명 관리에서 명백한 설계 결함 |
| D-06 | 알고리즘 구현 오류 | 참조 스펙 대비 알고리즘 로직이 틀린 부분 |
| D-07 | 빌드/플랫폼 호환성 위반 | 타겟 플랫폼에서 동작하지 않을 설계 |
| D-08 | 기존 유사 구현체와 패턴 불일치 | 같은 프로젝트 내 유사 기능과 다른 패턴 사용 |

### Step 3: Code Cross-check (Design 리뷰 전용)

- 기존 코드의 패턴과 컨벤션 확인
- Design에서 참조하는 코드가 실제로 존재하고 올바른지 검증
- 새로 추가되는 인터페이스가 기존 인터페이스와 호환되는지 확인

### Step 4: Output

아래 형식으로 한글 출력:

```markdown
# 문서 리뷰: {문서 제목}

**리뷰 라운드**: 1차 | **문서 타입**: Plan/Design
**리뷰 일시**: {date}

## 🔴 크리티컬 이슈

### [{ID}] {이슈 제목}
- **위치**: {문서 내 섹션/줄}
- **문제**: {무엇이 문제인지 한 문장}
- **근거**: {왜 문제인지 — 표준 참조, 코드 참조 등}
- **제안**: {수정 방향}

## 🟡 주의 사항
- (크리티컬은 아니지만 알아두면 좋은 것, 2~3개 이내)

## 🟢 잘된 점
- (1~2개, 구체적으로)

## 다음 단계
- (리뷰 결과에 따른 권장 액션)
```

### 2차 리뷰 모드 (`--round 2`)

1. 1차 리뷰에서 지적한 크리티컬 이슈들의 해결 여부 확인
2. 수정 과정에서 새로 발생한 이슈 체크
3. 출력에 **1차 대비 변경 사항** 섹션 추가:

```markdown
## 1차 대비 변경 사항
| 1차 이슈 ID | 상태 | 비고 |
|------------|------|------|
| P-03 | ✅ 해결 | 모순 제거됨 |
| P-06 | ⚠️ 부분 해결 | A는 추가했으나 B 누락 |
```

## Important Rules

1. **크리티컬만 잡는다** — 사소한 건 무시. 리뷰 항목이 0개여도 괜찮다.
2. **후속 단계를 신뢰한다** — Design/개발/테스트에서 잡힐 건 넘긴다.
3. **근거를 든다** — "이상합니다" 대신 구체적 근거(표준, 코드, 요구사항)를 제시한다.
4. **코드를 확인한다** — Design 리뷰 시 반드시 관련 코드를 읽고 교차 검증한다.
5. **짧게 쓴다** — 장황한 설명 대신 핵심만.
6. **한글로 피드백한다** — 코드/API명 등 고유명사만 영문.
7. **과잉 리뷰 금지** — 의심스럽지만 확신 없으면 안 적는다. False positive가 가장 해롭다.
