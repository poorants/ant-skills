#!/bin/bash
# Initialize Claude Code project environment (macOS/Linux)
#
# Steps:
#   1. .claude/settings.json (permissions)
#   2. Plugin marketplace registration
#   3. Plugin installation
#   4. .gitignore (exclude docs/)
#   5. Document structure + conventions — mode-aware:
#      brain (flat root vault) / project (nested brain/ + stack conventions) / empty (ask the plan)
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
#   brain   : standalone doc vault with PARA folders already at root -> flat (root)
#   project : repo with code -> nested (brain/, or existing para/) docs + convention seed
#   empty   : empty repo -> no guessing, leave a note asking the user for the plan
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

BRAIN_EXISTS=false
if [ -d brain ]; then BRAIN_EXISTS=true; fi

if [ "$HAS_CODE" = true ]; then MODE=project
elif [ "$BRAIN_EXISTS" = true ]; then MODE=brain
elif [ "$ROOT_HAS_PARA" = true ]; then MODE=flat-legacy
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
#    "repo|name" pairs: add uses the repo, update uses the marketplace name
MARKETPLACES=(
  "anthropics/skills|anthropic-agent-skills"
  "poorants/ant-skills|ant-agent-skills"
)

for entry in "${MARKETPLACES[@]}"; do
  repo="${entry%%|*}"
  name="${entry##*|}"
  echo "[...] Registering marketplace '$repo'..."
  claude plugin marketplace add "$repo" 2>&1 | cat || true   # harmless if already registered
  echo "[...] Updating marketplace '$name'..."
  claude plugin marketplace update "$name" 2>&1 | cat || true
  echo "[OK] Marketplace '$name' up to date"
done

# 3. Plugin installation (install if new, ALWAYS update so existing envs refresh)
# name|scope — ant-project-kit at user scope (install once globally; hooks self-gate
# to brain repos, so one install covers every repo and updates land in one place).
# example-skills is a heavy demo pack, kept opt-in per repo (local).
PLUGINS=(
  "example-skills@anthropic-agent-skills|local"
  "ant-project-kit@ant-agent-skills|user"
)

for entry in "${PLUGINS[@]}"; do
  p="${entry%%|*}"
  scope="${entry##*|}"
  echo "[...] Installing plugin '$p' (scope: $scope)..."
  claude plugin install "$p" --scope "$scope" 2>&1 | cat || true   # harmless if already installed
  echo "[...] Updating plugin '$p'..."
  claude plugin update "$p" --scope "$scope" 2>&1 | cat || true
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

# 5 & 6. Document structure + conventions
# Policy: if detected, apply the recommendation automatically. If undetected
#         (empty repo), prompt for input on the spot. When non-interactive
#         (pipe/CI, stdin not a tty), fall back to a CLAUDE.md note.

setup_brain() {
  # Standalone vault, new unified layout: docs under brain/, root stays for meta/exports.
  echo "[SETUP] Standalone document vault (brain) — nested brain/ PARA"
  for cat in projects areas resources archives; do
    mkdir -p "brain/$cat"
    touch "brain/$cat/.gitkeep"
  done
  echo "[OK] nested brain/ PARA structure ensured. No code conventions seeded (pure doc repo)."
}

setup_flat_legacy() {
  # Existing repo with PARA folders at the root. Leave the layout; just ensure folders.
  echo "[SETUP] Legacy flat vault — PARA folders at root (back-compat)"
  for dir in projects areas resources archives; do
    [ -d "$dir" ] || mkdir -p "$dir"
  done
  echo "[OK] flat PARA ensured. NOTE: the engram default is now brain/ — to unify, move these under brain/."
}

# setup_project <has_react:true|false> [backend ...]
setup_project() {
  local has_react="$1"; shift
  local backends=("$@")
  local desc=""
  [ "$has_react" = true ] && desc="react"
  if [ "${#backends[@]}" -gt 0 ]; then
    desc="${desc:+$desc+}$(IFS=+; echo "${backends[*]}")"
  fi
  [ -z "$desc" ] && desc="generic"

  # Nested base: prefer brain/ (on-brand). Reuse an existing para/ for back-compat.
  local base="brain"
  if [ -d brain ]; then base="brain"; elif [ -d para ]; then base="para"; fi
  echo "[SETUP] Code project + document management — nested $base/ (stack: $desc)"

  for cat in projects areas resources archives; do
    mkdir -p "$base/$cat"
    touch "$base/$cat/.gitkeep"
  done
  echo "[OK] nested PARA structure initialized ($base/)"

  echo ""
  echo "[...] Seeding code conventions..."
  local cc_dir="$base/areas/code-convention"
  mkdir -p "$cc_dir"
  local seed_file
  if [ "$has_react" = true ]; then seed_file="fe-conventions.md"; else seed_file="generic-conventions.md"; fi

  if [ ! -f "$cc_dir/CONVENTIONS.md" ]; then
    if curl -sfL "https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/$seed_file" -o "$cc_dir/CONVENTIONS.md"; then
      echo "[OK] CONVENTIONS.md seeded ($seed_file)"
    else
      echo "[WARN] Could not fetch $seed_file (skipping)"
    fi
  else
    echo "[SKIP] CONVENTIONS.md already exists"
  fi

  if [ "${#backends[@]}" -gt 0 ]; then
    echo "[NOTE] Backend ($(IFS=,; echo "${backends[*]}")) conventions: extract them from real code with /code-convention."
  fi

  [ -f "$cc_dir/CHANGELOG.md" ] || printf '# Code Convention Changelog\n\n## init\nSeeded a stack-detected starter via the ant-skills bootstrap.\nExtract real, stack-specific rules from code with /code-convention, then evolve.\n' > "$cc_dir/CHANGELOG.md"
  [ -f ".code-convention.json" ] || printf '{\n  "outputDir": "%s/areas/code-convention"\n}\n' "$base" > ".code-convention.json"

  if ! grep -qF '.code-convention.json' .gitignore 2>/dev/null; then
    printf '\n# code-convention local config\n.code-convention.json\n' >> .gitignore
  fi

  [ -f CLAUDE.md ] || touch CLAUDE.md
  if ! grep -qF 'areas/code-convention' CLAUDE.md 2>/dev/null; then
    cat >> CLAUDE.md <<MD

## Code conventions

Code conventions live in \`$base/areas/code-convention/\` and are the single source of truth
(naming, style, error handling, security; FE adds i18n + data-testid). Read & follow them
before writing or changing code; manage them with the \`code-convention\` skill.

@$base/areas/code-convention/CONVENTIONS.md
MD
    echo "[OK] CLAUDE.md updated with conventions pointer ($base/areas/code-convention)"
  else
    echo "[SKIP] CLAUDE.md already references conventions"
  fi
}

write_pending_note() {
  [ -f CLAUDE.md ] || touch CLAUDE.md
  if ! grep -qF 'Project setup (pending)' CLAUDE.md 2>/dev/null; then
    cat >> CLAUDE.md <<'MD'

## Project setup (pending)

This repo was bootstrapped empty (non-interactive run). Before scaffolding docs or writing
code, ASK the user:

1. Whether this repo should be (a) a code project + document management (nested `brain/`),
   or (b) a standalone document vault (brain, flat root).
2. (If a code project) which stack (e.g. rust+react, go+react, web / macOS desktop).

Based on the answer, set up the PARA structure with the `engram` skill and conventions with
the `code-convention` skill. Delete this section once setup is done.
MD
    echo "[OK] Added 'Project setup (pending)' note to CLAUDE.md — Claude will ask for the plan next session."
  else
    echo "[SKIP] 'Project setup (pending)' note already present"
  fi
}

# --- dispatch ---
echo ""
if [ "$MODE" = "brain" ]; then
  echo "[MODE] Detected: standalone document vault (brain) -> nested brain/"
  setup_brain

elif [ "$MODE" = "flat-legacy" ]; then
  echo "[MODE] Detected: legacy flat vault (PARA at root) -> keeping as-is (back-compat)"
  setup_flat_legacy

elif [ "$MODE" = "project" ]; then
  SD=""
  [ "$HAS_REACT" = true ] && SD="react"
  if [ "${#BACKENDS[@]}" -gt 0 ]; then SD="${SD:+$SD+}$(IFS=+; echo "${BACKENDS[*]}")"; fi
  [ -z "$SD" ] && SD="generic"
  echo "[MODE] Detected: code project -> recommending nested brain/ (stack: $SD)"
  # Expanding an empty "${BACKENDS[@]}" errors under macOS bash 3.2 + set -u -> guard by count
  if [ "${#BACKENDS[@]}" -gt 0 ]; then
    setup_project "$HAS_REACT" "${BACKENDS[@]}"
  else
    setup_project "$HAS_REACT"
  fi

else
  # Empty repo — undetected. Prompt if stdin is a tty, else fall back to a note.
  if [ ! -t 0 ]; then
    echo "[MODE] Empty repo (non-interactive) — cannot prompt, leaving a note only."
    write_pending_note
  else
    echo "[MODE] Empty repo — auto-detection failed. Asking how to use it."
    echo "  [1] Standalone document vault (brain) — flat, projects/areas/... at root"
    echo "  [2] Code project + document management — nested brain/"
    read -r -p "Choose [1/2] (default 2): " ans
    if [ "$ans" = "1" ]; then
      setup_brain
    else
      echo "Which stack?"
      echo "  [1] rust + react   [2] go + react   [3] react only   [4] other (manual)   [5] generic"
      read -r -p "Choose [1-5] (default 1): " s
      case "$s" in
        2) setup_project true go ;;
        3) setup_project true ;;
        4)
          read -r -p "React frontend? [y/N]: " r
          read -r -p "Backends (space-separated, e.g. rust go) — blank if none: " custom
          hr=false
          case "$r" in [yY]*) hr=true ;; esac
          # shellcheck disable=SC2086
          setup_project "$hr" $custom
          ;;
        5) setup_project false ;;
        *) setup_project true rust ;;   # 1 or empty -> primary stack
      esac
    fi
  fi
fi

echo ""
echo "[DONE] Project environment ready!"
