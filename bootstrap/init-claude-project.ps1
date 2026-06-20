<#
.SYNOPSIS
    Initialize a Claude Code environment (Windows; PowerShell 5.1 and 7).
.DESCRIPTION
    Run anywhere. It does exactly two things:
      1. Install/update the toolkits at USER scope (marketplaces + plugins).
      2. Create .claude/settings.json (all permissions) in the CURRENT directory.

    Knowledge/brain and code conventions are NOT set up here -- link a repo to a
    shared engram brain yourself via the engram skill (e.g. "use the personal
    brain here"). Re-running is safe (install->update, settings overwritten).
.EXAMPLE
    iex (irm https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/init-claude-project.ps1)
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# 1. Toolkits at user scope (register/install if new, ALWAYS update) -----------
if (Get-Command claude -ErrorAction SilentlyContinue) {
    foreach ($mp in @(
        @{ repo = "anthropics/skills";   name = "anthropic-agent-skills" }
        @{ repo = "poorants/ant-skills"; name = "ant-agent-skills" }
    )) {
        Write-Host "[...] marketplace '$($mp.repo)'"
        claude plugin marketplace add $mp.repo 2>&1 | Out-Null
        claude plugin marketplace update $mp.name 2>&1 | Out-Null
    }
    foreach ($p in @("example-skills@anthropic-agent-skills", "ant-common-kit@ant-agent-skills", "ant-dev-kit@ant-agent-skills")) {
        Write-Host "[...] plugin '$p' (user scope)"
        claude plugin install $p --scope user 2>&1 | Out-Null
        claude plugin update  $p --scope user 2>&1 | Out-Null
    }
    Write-Host "[OK] toolkits installed/updated (user scope)" -ForegroundColor Green
} else {
    Write-Host "[WARN] claude CLI not found - skipped toolkit install. Install Claude Code and re-run." -ForegroundColor Yellow
}

# 2. .claude/settings.json (all permissions) in the current directory ----------
if (-not (Test-Path ".claude")) { New-Item -ItemType Directory -Path ".claude" -Force | Out-Null }
@'
{
  "permissions": {
    "defaultMode": "bypassPermissions",
    "allow": ["Bash", "Read", "Edit", "Write", "Glob", "Grep", "WebFetch", "WebSearch", "Skill", "Task"]
  }
}
'@ | Set-Content -Path ".claude/settings.json" -Encoding UTF8
Write-Host "[OK] .claude/settings.json created (all permissions)" -ForegroundColor Green

Write-Host ""
Write-Host "[DONE] Toolkits installed + .claude/settings.json written." -ForegroundColor Cyan
Write-Host "Next - set the engram brain (just tell Claude Code):"
Write-Host '  - Register a brain once:  register <path-to-brain-repo> as the "personal" brain'
Write-Host '  - Link THIS repo to it:    use the "personal" brain for this repo'
Write-Host "From there: engram curates shared knowledge + stack convention bases (resources/conventions/<stack>.md);"
Write-Host "the code-convention skill compiles this repo's .code-convention/ (inherited base + project deltas, @import'd from CLAUDE.md)."
