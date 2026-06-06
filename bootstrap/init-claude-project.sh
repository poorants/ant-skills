#!/bin/bash
# Initialize Claude Code project environment (macOS/Linux)
#
# Steps:
#   1. .claude/settings.json (permissions)
#   2. Plugin marketplace registration
#   3. Plugin installation
#   4. .gitignore (exclude docs/)
#   5. PARA document initialization
#
# Usage:
#   bash <(curl -sL https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/init-claude-project.sh)

set -euo pipefail

# Check claude CLI availability
if ! command -v claude &>/dev/null; then
  echo "[WARN] claude CLI not found. Install Claude Code and re-run."
  exit 1
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

# 2. Plugin marketplaces
MARKETPLACES=(
  "anthropics/skills"
  "poorants/ant-skills"
)

for mp in "${MARKETPLACES[@]}"; do
  echo "[...] Registering marketplace '$mp'..."
  if claude plugin marketplace add "$mp" 2>&1 | cat; then
    echo "[OK] Marketplace '$mp' registered"
  else
    echo "[SKIP] Marketplace '$mp' already registered, updating..."
    claude plugin marketplace update "$mp" 2>&1 | cat || true
  fi
done

# 3. Plugin installation
PLUGINS=(
  "example-skills@anthropic-agent-skills"
  "ant-project-kit@ant-agent-skills"
)

for p in "${PLUGINS[@]}"; do
  echo "[...] Installing plugin '$p'..."
  claude plugin install "$p" --scope local
  echo "[OK] Plugin '$p' installed"
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

# 5. PARA document initialization
echo ""
echo "[...] Initializing PARA documents..."
for dir in para/projects para/areas para/resources para/archives; do
  mkdir -p "$dir"
  touch "$dir/.gitkeep"
done
echo "[OK] PARA structure initialized"

# 6. Code conventions (house FE standard) — seed doc + CLAUDE.md pointer
echo ""
echo "[...] Seeding code conventions..."
CC_DIR="para/areas/code-convention"
mkdir -p "$CC_DIR"

if [ ! -f "$CC_DIR/CONVENTIONS.md" ]; then
  if curl -sfL "https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/fe-conventions.md" -o "$CC_DIR/CONVENTIONS.md"; then
    echo "[OK] CONVENTIONS.md seeded"
  else
    echo "[WARN] Could not fetch fe-conventions.md (skipping)"
  fi
else
  echo "[SKIP] CONVENTIONS.md already exists"
fi

if [ ! -f "$CC_DIR/CHANGELOG.md" ]; then
  printf '# Code Convention Changelog\n\n## init\nSeeded the house FE standard (i18n + data-testid) via the ant-skills bootstrap.\nExtend with /code-convention add | evolve.\n' > "$CC_DIR/CHANGELOG.md"
fi

if [ ! -f ".code-convention.json" ]; then
  printf '{\n  "outputDir": "para/areas/code-convention",\n  "ruleCount": 26\n}\n' > ".code-convention.json"
fi

if ! grep -qF '.code-convention.json' .gitignore 2>/dev/null; then
  printf '\n# code-convention local config\n.code-convention.json\n' >> .gitignore
fi

# CLAUDE.md pointer (idempotent) — auto-loaded every session, @import pulls the rules in
[ -f CLAUDE.md ] || touch CLAUDE.md
if ! grep -qF 'para/areas/code-convention' CLAUDE.md 2>/dev/null; then
  cat >> CLAUDE.md <<'MD'

## Code conventions

Code conventions live in `para/areas/code-convention/` and are the single source of truth
(naming, style, i18n, data-testid, error handling, security). Read & follow them before
writing or changing code; manage them with the `code-convention` skill.

@para/areas/code-convention/CONVENTIONS.md
MD
  echo "[OK] CLAUDE.md updated with conventions pointer"
else
  echo "[SKIP] CLAUDE.md already references conventions"
fi

echo ""
echo "[DONE] Project environment ready!"
