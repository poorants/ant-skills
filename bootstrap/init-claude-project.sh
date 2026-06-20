#!/bin/bash
# Initialize a Claude Code environment (macOS/Linux).
#
# Run anywhere. It does exactly two things:
#   1. Install/update the toolkits at USER scope (marketplaces + plugins).
#   2. Create .claude/settings.json (all permissions) in the CURRENT directory.
#
# Knowledge/brain and code conventions are NOT set up here -- link a repo to a
# shared engram brain yourself via the engram skill (e.g. "use the personal brain
# here"). Re-running is safe (install->update, settings overwritten).
#
# Usage:
#   bash <(curl -sL https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/init-claude-project.sh)

set -euo pipefail

# 1. Toolkits at user scope (register/install if new, ALWAYS update) -----------
if command -v claude &>/dev/null; then
  for entry in "anthropics/skills|anthropic-agent-skills" "poorants/ant-skills|ant-agent-skills"; do
    repo="${entry%%|*}"; name="${entry##*|}"
    echo "[...] marketplace '$repo'"
    claude plugin marketplace add "$repo" 2>&1 | cat || true
    claude plugin marketplace update "$name" 2>&1 | cat || true
  done
  for p in "example-skills@anthropic-agent-skills" "ant-common-kit@ant-agent-skills" "ant-dev-kit@ant-agent-skills"; do
    echo "[...] plugin '$p' (user scope)"
    claude plugin install "$p" --scope user 2>&1 | cat || true
    claude plugin update  "$p" --scope user 2>&1 | cat || true
  done
  echo "[OK] toolkits installed/updated (user scope)"
else
  echo "[WARN] claude CLI not found -- skipped toolkit install. Install Claude Code and re-run."
fi

# 2. .claude/settings.json (all permissions) in the current directory ----------
mkdir -p .claude
cat > .claude/settings.json <<'JSON'
{
  "permissions": {
    "defaultMode": "bypassPermissions",
    "allow": ["Bash", "Read", "Edit", "Write", "Glob", "Grep", "WebFetch", "WebSearch", "Skill", "Task"]
  }
}
JSON
echo "[OK] .claude/settings.json created (all permissions)"

cat <<'NEXT'

[DONE] Toolkits installed + .claude/settings.json written.

Next - set the engram brain (just tell Claude Code):
  - Register a brain once:  register <path-to-brain-repo> as the "personal" brain
  - Link THIS repo to it:    use the "personal" brain for this repo
The engram skill handles the rest (shared knowledge + code conventions).
NEXT
