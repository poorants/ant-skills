# 빌드 배선 레시피 — version.sh 를 빌드에 주입하기

`scripts/version.sh` 는 버전 **문자열**만 계산한다. 그 문자열을 실제 아티팩트(바이너리/패키지/런타임)에
넣는 "배선"은 빌드 시스템마다 다르다. `init` 은 프로젝트를 감지해 아래 레시피 중 맞는 것을 적용한다.

감지 우선순위: `Makefile` → `go.mod` → `package.json` → `pyproject.toml`/`setup.py` → 그 외(generic).
여러 개가 보이면 사용자에게 어느 빌드 시스템에 배선할지 묻는다.

---

## Make (언어 무관, petra-console 원형)

`Makefile` 상단:

```makefile
VERSION     ?= $(shell scripts/version.sh 2>/dev/null || echo 0.0.0)
DEV_VERSION := $(shell scripts/version.sh --dev 2>/dev/null || echo 0.0.0+dev)

.PHONY: version
version:
	@echo "VERSION=$(VERSION)"
```

이후 `build` 타깃은 `$(VERSION)`, `build-dev` 타깃은 `$(DEV_VERSION)` 을 사용한다.

## Go (ldflags 주입)

`internal/buildinfo/buildinfo.go`(또는 유사):

```go
package buildinfo

import "strings"

var (
	Version   = "dev"     // 빌드 시 -ldflags 로 주입
	Commit    = "unknown"
	BuildTime = "unknown"
)

// IsDevBuild: dev 빌드(+dev 접미사)에서만 켜지는 표면 게이팅용.
func IsDevBuild() bool { return strings.HasSuffix(Version, "+dev") }
```

Makefile 의 build 타깃:

```makefile
COMMIT     := $(shell git rev-parse --short HEAD 2>/dev/null || echo unknown)
LDFLAGS    := -X your-module/internal/buildinfo.Version=$(VERSION) \
              -X your-module/internal/buildinfo.Commit=$(COMMIT)

build:
	go build -ldflags "$(LDFLAGS)" -o output/app ./cmd/app
build-dev:
	go build -tags dev -ldflags "-X your-module/internal/buildinfo.Version=$(DEV_VERSION) -X your-module/internal/buildinfo.Commit=$(COMMIT)" -o output/app ./cmd/app
```

> Makefile 이 없으면 위 ldflags 를 `go build` 명령에 직접 넣거나 작은 `build.sh` 로 감싼다.

## Node / npm

`package.json` 의 `version` 필드는 **건드리지 않는다**(npm 도구 호환을 위해 그대로 두거나 `0.0.0` 고정).
대신 빌드 직전 생성 파일에 주입한다.

`scripts/gen-version.sh` 또는 `package.json` 스크립트:

```json
{
  "scripts": {
    "prebuild": "node -e \"require('fs').writeFileSync('src/version.ts', 'export const VERSION = \\''+require('child_process').execSync('bash scripts/version.sh').toString().trim()+'\\';\\n')\"",
    "build": "vite build"
  }
}
```

또는 빌드 타임 define(Vite 예):

```js
// vite.config.js
import { execSync } from 'node:child_process'
const VERSION = execSync('bash scripts/version.sh').toString().trim()
export default { define: { __APP_VERSION__: JSON.stringify(VERSION) } }
```

런타임에서 `__APP_VERSION__` 또는 생성된 `src/version.ts` 를 읽는다.

## Python

빌드/패키징 직전 생성 파일에 stamp:

```bash
# scripts/gen-version.sh
echo "__version__ = \"$(bash scripts/version.sh)\"" > src/yourpkg/_version.py
```

`yourpkg/__init__.py` → `from ._version import __version__`. `pyproject.toml` 의 정적 `version` 은
플레이스홀더로 두고 실제 식별은 `__version__` 로 한다(또는 `hatch`/`setuptools-scm` 대신 이 stamp 사용).

## Generic (빌드 시스템 무관)

배선 없이 `scripts/version.sh` 만 노출한다. 패키징 스크립트나 CI 에서 직접 호출:

```bash
VER=$(bash scripts/version.sh)
tar czf "myapp-${VER}.tar.gz" dist/
```

---

## Docker / CI 주의

`version.sh` 는 머지 수를 세므로 **full clone** 이 필요하다. 컨테이너 빌드는 보통 shallow 이거나 git 히스토리가
없으니, **호스트에서 계산해 build-arg/env 로 전달**한다:

```dockerfile
ARG VERSION=0.0.0
ENV APP_VERSION=$VERSION
```

```bash
docker build --build-arg VERSION="$(bash scripts/version.sh)" -t myapp .
```

GitLab CI 라면 `GIT_DEPTH: 0`(full clone) 설정 후 잡 안에서 `version.sh` 를 호출해도 된다.
