---
name: git-versioning
description: "git 커밋 그래프에서 빌드 시 로컬로 계산하는 구조 기반 MAJOR.MINOR.PATCH 버전 체계를 프로젝트에 도입·운영한다 — 태그·CI·토큰 불필요. MINOR=머지(MR/PR) 수, PATCH=마지막 머지 이후 main 직접 커밋 수, MAJOR=사람이 정하는 마일스톤. 어느 빌드인지 식별하는 단조 증가 버전이 필요한 내부/사내 제품에 적합(공개 라이브러리는 표준 SemVer 권장). version.sh+version.conf 설치, 빌드 시스템 배선(Make/Go/Node/Python), MAJOR bump, 실제 출고 시 vX.Y.Z 태깅까지. Use when user says /git-versioning, 'set up versioning', 'version scheme', 'how is the version computed', 'bump major', 'tag a release', 'version 붙이기'. 트리거: 버전 관리, 버전 체계, 버전 매기기, 버전 계산, 버전 도입, 메이저 올리기, 릴리스 태그, 버전 스킬."
---

# git-versioning: 구조 기반 버전 체계

git 커밋 그래프에서 **빌드 시 로컬로 계산**하는 `MAJOR.MINOR.PATCH` 버전 체계를 프로젝트에 도입하고
운영한다. 태그·CI·토큰이 필요 없고, 같은 커밋이면 항상 같은 버전이 나오는 **결정적** 방식이다.

- **MINOR** = 머지(MR/PR) 수 − `MR_BASE` → 머지마다 +1, patch 0 리셋
- **PATCH** = 마지막 머지 이후 main 직접 커밋 수(first-parent) → 핫픽스 커밋마다 +1, 머지 직후 0
- **MAJOR** = `MAJOR_BASE`(사람이 정하는 마일스톤) + 오버플로 캐리(사실상 없음)

번호는 "이 빌드가 git 어디에 있나"를 가리키는 **단조 증가 빌드 식별자**다. 자세한 근거·표준 대비는
[references/versioning-policy.md](references/versioning-policy.md).

## 언제 이 체계가 맞나 (먼저 판단)

- ✅ **적합**: 외부 소비자가 없는 내부/사내 제품, on-demand 출고, QA 가 "어느 빌드인지" 식별해야 함,
  CI/토큰 없이 로컬 결정성을 원함.
- ❌ **부적합**: 공개 npm/라이브러리/SDK 등 **모르는 외부 소비자가 업그레이드 안전성을 번호로 판단**해야
  하는 경우 → 표준 SemVer + Conventional Commits + semantic-release 를 권장. `init` 전에 사용자에게 확인.

## Usage

```
/git-versioning                  -- 현재 계산된 버전 출력 (기본)
/git-versioning status           -- 위와 동일 + 분해(MAJOR/MINOR/PATCH 근거) 표시
/git-versioning init             -- version.sh + version.conf + 정책 문서 설치 후 빌드 시스템에 배선
/git-versioning bump-major       -- MAJOR 마일스톤 수동 bump (version.conf 편집)
/git-versioning release          -- 실제 출고 시 vX.Y.Z 태그 생성 안내
/git-versioning explain          -- 이 체계가 무엇이고 왜 표준과 다른지 설명
```

## Commands

### `status` (기본)

1. 프로젝트 루트에 `scripts/version.sh` 가 있으면 그걸, 없으면 이 스킬의
   [scripts/version.sh](scripts/version.sh) 를 실행해 버전을 출력한다.
2. `status` 는 분해도 보여준다 — 다음 git 사실을 모아 표로:
   - `git rev-list --merges --count HEAD` → MINOR 근거(머지 수)
   - 마지막 머지 이후 `git rev-list --count --first-parent <last-merge>..HEAD` → PATCH 근거
   - `version.conf` 의 `MAJOR_BASE`/`MR_BASE`
   - `git diff-index --quiet HEAD` → dirty 여부
3. `version.sh` 가 아직 설치 안 됐으면 `init` 을 권한다.

### `init`

프로젝트에 체계를 설치한다. **순서대로**:

1. **적합성 확인** — 위 "언제 이 체계가 맞나"를 사용자와 점검. 공개 라이브러리면 표준 SemVer 를 권하고 중단.
2. **`scripts/version.sh` 설치** — 이 스킬의 [scripts/version.sh](scripts/version.sh) 를 프로젝트
   `scripts/version.sh` 로 복사하고 `chmod +x`. 이미 있으면 덮어쓰기 전 확인.
3. **`version.conf` 생성**(리포 루트) — 0.x 동안 기본값:
   ```
   # 빌드 버전 베이스라인 — scripts/version.sh 가 읽음. 정책: docs/versioning.md
   MAJOR_BASE=0
   MR_BASE=0
   ```
4. **정책 문서 복사** — [references/versioning-policy.md](references/versioning-policy.md) 를
   `docs/versioning.md`(또는 프로젝트의 문서 관행 경로)로 복사하고 `{PROJECT}` 치환.
5. **빌드 시스템 배선** — [references/build-wiring.md](references/build-wiring.md) 를 따라 감지된 빌드
   시스템(Make/Go/Node/Python/generic)에 버전 주입을 추가. 여러 개면 어디에 배선할지 사용자에게 확인.
6. **검증** — `bash scripts/version.sh` 와 `--dev` 를 실행해 합리적 값이 나오는지 보여주고, 비-shallow
   clone 필요(머지 수 카운트)임을 안내.

> 출력물은 **사용자 프로젝트**에 생성된다(스킬 디렉터리 안이 아님).

### `bump-major`

마일스톤으로 MAJOR 를 올린다(드뭄). [versioning-policy.md](references/versioning-policy.md) §4 절차:

1. 현재 머지 수 확인: `git rev-list --merges --count <main-branch>` (예: origin/main).
2. `version.conf` 편집 — `MAJOR_BASE` 를 목표 major 로 올리고 `MR_BASE` 를 위 머지 수로 설정 → MINOR 0 리셋.
3. 그 변경을 커밋. 이후 버전은 `<new-major>.0.x` 부터 시작.
4. `version.sh` 로 결과 확인.

### `release`

QA 통과한 빌드를 실제 출고로 태깅한다. 태그는 **실제 출고 때만** 찍는다([정책](references/versioning-policy.md) §3):

1. 출고할 커밋이 체크아웃돼 있고 깨끗한지(`-dirty` 없음) 확인.
2. 그 커밋의 버전 계산: `bash scripts/version.sh` → 예 `0.21.0`.
3. 같은 이름 태그 생성·푸시:
   ```
   git tag v0.21.0
   git push origin v0.21.0
   ```
4. 태그는 마커일 뿐 — 버전 계산은 태그를 보지 않는다(§1). 머지마다 태그를 쌓지 말 것.

### `explain`

[versioning-policy.md](references/versioning-policy.md) 를 근거로, 이 체계가 무엇이고(§1) 표준 SemVer 와
무엇이 다른지(§5) 사용자 수준에 맞게 설명한다. "왜 semantic-release 안 쓰나"는 §0.

## Resources

| 파일 | 용도 |
|------|------|
| [scripts/version.sh](scripts/version.sh) | 버전 계산 단일 원본(언어 무관, 순수 git). `init` 이 프로젝트로 복사. |
| [references/versioning-policy.md](references/versioning-policy.md) | 정책·근거·표준 대비. `init` 이 `docs/versioning.md` 로 복사. |
| [references/build-wiring.md](references/build-wiring.md) | Make/Go/Node/Python/generic 빌드 배선 레시피. |

## 주의

- **머지 수를 세므로 non-shallow clone 필요**. CI/Docker 는 호스트에서 계산해 build-arg 로 전달
  ([build-wiring.md](references/build-wiring.md) Docker/CI 절).
- **GitHub squash-merge** 는 머지 커밋을 안 만들어 MINOR 가 안 오른다 — PR 머지를 "merge commit" 으로
  설정하거나 PATCH 중심으로 본다([정책](references/versioning-policy.md) §1).
- 빌드 버전엔 `v` 없음(`0.21.0`), 릴리스 **태그**만 `vX.Y.Z`.
