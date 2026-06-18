# Build Wiring Recipes — injecting version.sh into the build

`scripts/version.sh` only computes the version **string**. The "wiring" that puts that string into the actual artifact
(binary/package/runtime) differs per build system. `init` detects the project and applies whichever recipe below fits.

Detection priority: `Makefile` → `go.mod` → `package.json` → `pyproject.toml`/`setup.py` → otherwise (generic).
If several are present, it asks the user which build system to wire into.

---

## Make (language-agnostic, the petra-console archetype)

Top of the `Makefile`:

```makefile
VERSION     ?= $(shell scripts/version.sh 2>/dev/null || echo 0.0.0)
DEV_VERSION := $(shell scripts/version.sh --dev 2>/dev/null || echo 0.0.0+dev)

.PHONY: version
version:
	@echo "VERSION=$(VERSION)"
```

After that, the `build` target uses `$(VERSION)` and the `build-dev` target uses `$(DEV_VERSION)`.

## Go (ldflags injection)

`internal/buildinfo/buildinfo.go` (or similar):

```go
package buildinfo

import "strings"

var (
	Version   = "dev"     // injected at build time via -ldflags
	Commit    = "unknown"
	BuildTime = "unknown"
)

// IsDevBuild: gates surfaces that turn on only in dev builds (+dev suffix).
func IsDevBuild() bool { return strings.HasSuffix(Version, "+dev") }
```

The build target in the Makefile:

```makefile
COMMIT     := $(shell git rev-parse --short HEAD 2>/dev/null || echo unknown)
LDFLAGS    := -X your-module/internal/buildinfo.Version=$(VERSION) \
              -X your-module/internal/buildinfo.Commit=$(COMMIT)

build:
	go build -ldflags "$(LDFLAGS)" -o output/app ./cmd/app
build-dev:
	go build -tags dev -ldflags "-X your-module/internal/buildinfo.Version=$(DEV_VERSION) -X your-module/internal/buildinfo.Commit=$(COMMIT)" -o output/app ./cmd/app
```

> If there is no Makefile, put the ldflags above directly on the `go build` command or wrap it in a small `build.sh`.

## Node / npm

**Do not touch** the `version` field in `package.json` (leave it as-is, or pin it to `0.0.0`, for npm-tool compatibility).
Instead, inject into a generated file right before the build.

`scripts/gen-version.sh` or a `package.json` script:

```json
{
  "scripts": {
    "prebuild": "node -e \"require('fs').writeFileSync('src/version.ts', 'export const VERSION = \\''+require('child_process').execSync('bash scripts/version.sh').toString().trim()+'\\';\\n')\"",
    "build": "vite build"
  }
}
```

Or a build-time define (Vite example):

```js
// vite.config.js
import { execSync } from 'node:child_process'
const VERSION = execSync('bash scripts/version.sh').toString().trim()
export default { define: { __APP_VERSION__: JSON.stringify(VERSION) } }
```

At runtime, read `__APP_VERSION__` or the generated `src/version.ts`.

## Python

Stamp a generated file right before building/packaging:

```bash
# scripts/gen-version.sh
echo "__version__ = \"$(bash scripts/version.sh)\"" > src/yourpkg/_version.py
```

`yourpkg/__init__.py` → `from ._version import __version__`. Leave the static `version` in `pyproject.toml` as a placeholder and
use `__version__` as the real identifier (or use this stamp instead of `hatch`/`setuptools-scm`).

## Generic (build-system-agnostic)

Expose only `scripts/version.sh`, with no wiring. Call it directly from a packaging script or CI:

```bash
VER=$(bash scripts/version.sh)
tar czf "myapp-${VER}.tar.gz" dist/
```

---

## Docker / CI caveat

`version.sh` counts merges, so it needs a **full clone**. Container builds are usually shallow or have no git history, so
**compute it on the host and pass it in via build-arg/env**:

```dockerfile
ARG VERSION=0.0.0
ENV APP_VERSION=$VERSION
```

```bash
docker build --build-arg VERSION="$(bash scripts/version.sh)" -t myapp .
```

With GitLab CI, you can also set `GIT_DEPTH: 0` (full clone) and then call `version.sh` inside the job.
