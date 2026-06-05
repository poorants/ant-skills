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

echo ""
echo "[DONE] Project environment ready!"
