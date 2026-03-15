#!/bin/bash
# Initialize Claude Code project environment (macOS/Linux)
#
# Steps:
#   1. .claude/settings.local.json (permissions)
#   2. Plugin marketplace registration
#   3. Plugin installation
#   4. .gitignore (exclude docs/, .bkit/)
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

# 1. .claude/settings.local.json
mkdir -p .claude
cat > .claude/settings.local.json <<'JSON'
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
echo "[OK] .claude/settings.local.json created"

# 2. Plugin marketplaces
MARKETPLACES=(
  "popup-studio-ai/bkit-claude-code"
  "anthropics/skills"
  "poorants/ant-skills"
)

for mp in "${MARKETPLACES[@]}"; do
  echo "[...] Registering marketplace '$mp'..."
  if claude plugin marketplace add "$mp" 2>&1 | cat; then
    echo "[OK] Marketplace '$mp' registered"
  else
    echo "[SKIP] Marketplace '$mp' already registered"
  fi
done

echo "[...] Updating all marketplaces..."
if claude plugin marketplace update 2>&1 | cat; then
  echo "[OK] Marketplaces updated"
else
  echo "[WARN] Marketplace update failed"
fi

# 3. Plugin installation
PLUGINS=(
  "bkit"
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

if grep -qx '\.bkit/\?' .gitignore 2>/dev/null; then
  echo "[SKIP] '.bkit/' already in .gitignore"
else
  printf '\n# bkit plugin data\n.bkit/\n' >> .gitignore
  echo "[OK] Added '.bkit/' to .gitignore"
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
