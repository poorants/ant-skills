#!/bin/bash
# Initialize Claude Code project environment (macOS/Linux)
#
# Steps:
#   1. .claude/settings.json (permissions)
#   2. Plugin marketplace registration
#   3. Plugin installation
#   4. .gitignore (exclude docs/)
#   5. Document structure + conventions — mode-aware:
#      brain(flat 루트 문서저장소) / project(nested para/ + 스택 컨벤션) / empty(계획 질문)
#
# Usage:
#   bash <(curl -sL https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/init-claude-project.sh)

set -euo pipefail

# Check claude CLI availability
if ! command -v claude &>/dev/null; then
  echo "[WARN] claude CLI not found. Install Claude Code and re-run."
  exit 1
fi

# --- Mode & stack detection (run at project root, BEFORE any scaffolding) ---
#   brain   : 루트에 PARA 폴더가 이미 있는 단독 문서저장소 → flat(루트) 사용
#   project : 코드가 있는 저장소 → nested(para/)로 문서관리 + 컨벤션 시드
#   empty   : 빈 저장소 → 추측 금지, 사용자에게 계획을 묻도록 노트만 남김
ROOT_HAS_PARA=false
for c in projects areas resources archives; do
  if [ -d "$c" ]; then ROOT_HAS_PARA=true; fi
done

HAS_REACT=false
HAS_NODE=false
if [ -f package.json ]; then
  HAS_NODE=true
  if grep -Eq '"(react|next|nuxt|vue|svelte|@angular/core|solid-js|astro)"' package.json 2>/dev/null; then
    HAS_REACT=true
  fi
fi
BACKENDS=()
if [ -f Cargo.toml ]; then BACKENDS+=("rust"); fi
if [ -f go.mod ]; then BACKENDS+=("go"); fi
if [ -f build.gradle ] || [ -f build.gradle.kts ] || [ -f pom.xml ]; then BACKENDS+=("java"); fi
if [ -f pyproject.toml ] || [ -f requirements.txt ] || [ -f setup.py ]; then BACKENDS+=("python"); fi

HAS_CODE=false
if [ "$HAS_NODE" = true ] || [ "${#BACKENDS[@]}" -gt 0 ]; then HAS_CODE=true; fi

# emptiness: ignore bootstrap/meta artifacts
IS_EMPTY=true
for f in $(ls -A 2>/dev/null); do
  case "$f" in
    .git|.claude|.gitignore|CLAUDE.md|README.md|LICENSE|.code-convention.json|.obsidian|.bkit|docs) ;;
    *) IS_EMPTY=false ;;
  esac
done

if [ "$ROOT_HAS_PARA" = true ]; then MODE=brain
elif [ "$HAS_CODE" = true ]; then MODE=project
elif [ "$IS_EMPTY" = true ]; then MODE=empty
else MODE=project
fi

# 1. .claude/settings.json
mkdir -p .claude
cat > .claude/settings.json <<'JSON'
{
  "permissions": {
    "allow": [
      "Bash",
      "Read",
      "Edit",
      "Write",
      "Glob",
      "Grep",
      "WebFetch",
      "WebSearch",
      "Skill",
      "Task"
    ]
  }
}
JSON
echo "[OK] .claude/settings.json created"

# 2. Plugin marketplaces (register if new, ALWAYS update to latest)
#    "repo|name" 쌍: add 는 repo 로, update 는 marketplace 이름으로 호출
MARKETPLACES=(
  "anthropics/skills|anthropic-agent-skills"
  "poorants/ant-skills|ant-agent-skills"
)

for entry in "${MARKETPLACES[@]}"; do
  repo="${entry%%|*}"
  name="${entry##*|}"
  echo "[...] Registering marketplace '$repo'..."
  claude plugin marketplace add "$repo" 2>&1 | cat || true   # 이미 등록돼 있어도 무해
  echo "[...] Updating marketplace '$name'..."
  claude plugin marketplace update "$name" 2>&1 | cat || true
  echo "[OK] Marketplace '$name' up to date"
done

# 3. Plugin installation (install if new, ALWAYS update so existing envs refresh)
PLUGINS=(
  "example-skills@anthropic-agent-skills"
  "ant-project-kit@ant-agent-skills"
)

for p in "${PLUGINS[@]}"; do
  echo "[...] Installing plugin '$p'..."
  claude plugin install "$p" --scope local 2>&1 | cat || true   # 이미 설치돼 있어도 무해
  echo "[...] Updating plugin '$p'..."
  claude plugin update "$p" --scope local 2>&1 | cat || true
  echo "[OK] Plugin '$p' up to date"
done

# 4. .gitignore
if [ ! -f ".gitignore" ]; then
  touch .gitignore
  echo "[OK] .gitignore created"
fi

if grep -qx 'docs/\?' .gitignore 2>/dev/null; then
  echo "[SKIP] 'docs/' already in .gitignore"
else
  printf '\n# PARA documents (managed outside repo)\ndocs/\n' >> .gitignore
  echo "[OK] Added 'docs/' to .gitignore"
fi

# 5 & 6. Document structure + conventions (mode-aware)
echo ""
if [ "$MODE" = "brain" ]; then
  # 단독 문서저장소(브레인) — flat. 루트의 PARA 구조를 사용/보강.
  echo "[MODE] 단독 문서저장소(브레인) — flat(루트) PARA 사용"
  for dir in projects areas resources archives; do
    [ -d "$dir" ] || mkdir -p "$dir"
  done
  echo "[OK] flat PARA structure ensured (root). 코드 컨벤션은 시드하지 않음(순수 문서 repo)."

elif [ "$MODE" = "empty" ]; then
  # 빈 저장소 — 추측 금지. 사용자에게 계획을 묻도록 CLAUDE.md 노트만 남김.
  echo "[MODE] 빈 저장소 — 계획 미정. 스캐폴딩 보류, 사용자에게 물어보도록 노트만 남김."
  [ -f CLAUDE.md ] || touch CLAUDE.md
  if ! grep -qF 'Project setup (pending)' CLAUDE.md 2>/dev/null; then
    cat >> CLAUDE.md <<'MD'

## Project setup (pending)

This repo was bootstrapped empty. Before scaffolding docs or writing code, ASK the user:

1. 이 저장소를 (a) 코드 프로젝트 + 문서관리(nested `para/`) 로 갈지,
   (b) 순수 문서저장소(브레인, flat 루트) 로 갈지.
2. (코드 프로젝트라면) 어떤 스택인지 (예: rust+react, go+react, 웹/맥 데스크탑).

답에 따라 `engram` 스킬로 PARA 구조를, `code-convention` 스킬로 컨벤션을 셋업한다.
이 섹션은 셋업이 끝나면 지운다.
MD
    echo "[OK] CLAUDE.md에 'Project setup (pending)' 노트 추가 — 다음 세션에 Claude가 계획을 묻는다."
  else
    echo "[SKIP] 'Project setup (pending)' 노트가 이미 있음"
  fi

else
  # 코드 프로젝트 — nested(para/)로 문서관리 + 스택 맞춤 컨벤션 시드.
  STACK_DESC=""
  [ "$HAS_REACT" = true ] && STACK_DESC="react"
  if [ "${#BACKENDS[@]}" -gt 0 ]; then
    STACK_DESC="${STACK_DESC:+$STACK_DESC+}$(IFS=+; echo "${BACKENDS[*]}")"
  fi
  [ -z "$STACK_DESC" ] && STACK_DESC="generic"
  echo "[MODE] 코드 프로젝트 + 문서관리 — nested para/ (감지: $STACK_DESC)"

  for dir in para/projects para/areas para/resources para/archives; do
    mkdir -p "$dir"
    touch "$dir/.gitkeep"
  done
  echo "[OK] nested PARA structure initialized (para/)"

  echo ""
  echo "[...] Seeding code conventions..."
  CC_DIR="para/areas/code-convention"
  mkdir -p "$CC_DIR"
  if [ "$HAS_REACT" = true ]; then SEED_FILE="fe-conventions.md"; else SEED_FILE="generic-conventions.md"; fi

  if [ ! -f "$CC_DIR/CONVENTIONS.md" ]; then
    if curl -sfL "https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/$SEED_FILE" -o "$CC_DIR/CONVENTIONS.md"; then
      echo "[OK] CONVENTIONS.md seeded ($SEED_FILE)"
    else
      echo "[WARN] Could not fetch $SEED_FILE (skipping)"
    fi
  else
    echo "[SKIP] CONVENTIONS.md already exists"
  fi

  if [ "${#BACKENDS[@]}" -gt 0 ]; then
    echo "[NOTE] 백엔드($(IFS=,; echo "${BACKENDS[*]}")) 컨벤션은 /code-convention 으로 실제 코드에서 추출하세요."
  fi

  if [ ! -f "$CC_DIR/CHANGELOG.md" ]; then
    printf '# Code Convention Changelog\n\n## init\nSeeded a stack-detected starter via the ant-skills bootstrap.\nExtract real, stack-specific rules from code with /code-convention, then evolve.\n' > "$CC_DIR/CHANGELOG.md"
  fi

  if [ ! -f ".code-convention.json" ]; then
    printf '{\n  "outputDir": "para/areas/code-convention"\n}\n' > ".code-convention.json"
  fi

  if ! grep -qF '.code-convention.json' .gitignore 2>/dev/null; then
    printf '\n# code-convention local config\n.code-convention.json\n' >> .gitignore
  fi

  [ -f CLAUDE.md ] || touch CLAUDE.md
  if ! grep -qF 'para/areas/code-convention' CLAUDE.md 2>/dev/null; then
    cat >> CLAUDE.md <<'MD'

## Code conventions

Code conventions live in `para/areas/code-convention/` and are the single source of truth
(naming, style, error handling, security; FE adds i18n + data-testid). Read & follow them
before writing or changing code; manage them with the `code-convention` skill.

@para/areas/code-convention/CONVENTIONS.md
MD
    echo "[OK] CLAUDE.md updated with conventions pointer"
  else
    echo "[SKIP] CLAUDE.md already references conventions"
  fi
fi

echo ""
echo "[DONE] Project environment ready!"
