<#
.SYNOPSIS
    Initialize Claude Code project environment.
.DESCRIPTION
    1. Windows Terminal keybindings (iTerm2 style)
    --- requires claude CLI below ---
    2. .claude/settings.json (permissions)
    3. Plugin marketplace registration
    4. Plugin installation
    5. .gitignore (exclude docs/)
    6. PARA document initialization
.EXAMPLE
    iex (irm https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/init-claude-project.ps1)
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# 1. Windows Terminal keybindings (iTerm2 style)
$wtSettingsPath = "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json"

if (Test-Path $wtSettingsPath) {
    Write-Host "[...] Configuring Windows Terminal keybindings..."

    $wt = Get-Content $wtSettingsPath -Raw | ConvertFrom-Json

    $desiredActions = @(
        @{ id = "Init.splitPane.right";    command = @{ action = "splitPane"; split = "right" } }
        @{ id = "Init.splitPane.down";     command = @{ action = "splitPane"; split = "down" } }
        @{ id = "Init.newTab";             command = @{ action = "newTab" } }
        @{ id = "Init.prevTab";            command = @{ action = "prevTab" } }
        @{ id = "Init.nextTab";            command = @{ action = "nextTab" } }
        @{ id = "Init.moveFocus.up";       command = @{ action = "moveFocus"; direction = "up" } }
        @{ id = "Init.moveFocus.down";     command = @{ action = "moveFocus"; direction = "down" } }
        @{ id = "Init.moveFocus.left";     command = @{ action = "moveFocus"; direction = "left" } }
        @{ id = "Init.moveFocus.right";    command = @{ action = "moveFocus"; direction = "right" } }
    )
    for ($i = 0; $i -le 8; $i++) {
        $desiredActions += @{ id = "Init.switchToTab.$i"; command = @{ action = "switchToTab"; index = $i } }
    }

    $desiredKeys = @(
        @{ id = "Init.splitPane.right";    keys = "alt+d" }
        @{ id = "Init.splitPane.down";     keys = "alt+shift+d" }
        @{ id = "Init.newTab";             keys = "alt+t" }
        @{ id = "Init.prevTab";            keys = "alt+shift+[" }
        @{ id = "Init.nextTab";            keys = "alt+shift+]" }
        @{ id = "Init.moveFocus.up";       keys = "ctrl+alt+up" }
        @{ id = "Init.moveFocus.down";     keys = "ctrl+alt+down" }
        @{ id = "Init.moveFocus.left";     keys = "ctrl+alt+left" }
        @{ id = "Init.moveFocus.right";    keys = "ctrl+alt+right" }
    )
    for ($i = 0; $i -le 8; $i++) {
        $desiredKeys += @{ id = "Init.switchToTab.$i"; keys = "alt+$($i + 1)" }
    }

    # Merge actions
    if (-not $wt.actions) { $wt | Add-Member -NotePropertyName "actions" -NotePropertyValue @() }
    $actionList = [System.Collections.ArrayList]@($wt.actions)

    foreach ($da in $desiredActions) {
        $existing = $actionList | Where-Object { $_.id -eq $da.id }
        if (-not $existing) {
            $newAction = [PSCustomObject]@{ command = $da.command; id = $da.id }
            $actionList.Add($newAction) | Out-Null
        }
    }
    $wt.actions = @($actionList)

    # Merge keybindings
    if (-not $wt.keybindings) { $wt | Add-Member -NotePropertyName "keybindings" -NotePropertyValue @() }
    $kbList = [System.Collections.ArrayList]@($wt.keybindings)

    $desiredKeysSet = @{}
    foreach ($dk in $desiredKeys) { $desiredKeysSet[$dk.keys] = $true }

    foreach ($kb in $kbList) {
        if ($kb.keys -and $desiredKeysSet.ContainsKey($kb.keys) -and $kb.id -notlike "Init.*") {
            $kb.id = $null
        }
    }

    foreach ($dk in $desiredKeys) {
        $existing = $kbList | Where-Object { $_.id -eq $dk.id }
        if ($existing) {
            $existing.keys = $dk.keys
        } else {
            $newKb = [PSCustomObject]@{ id = $dk.id; keys = $dk.keys }
            $kbList.Add($newKb) | Out-Null
        }
    }
    $wt.keybindings = @($kbList)

    $wt | ConvertTo-Json -Depth 10 | Set-Content $wtSettingsPath -Encoding UTF8
    Write-Host "[OK] Windows Terminal keybindings configured" -ForegroundColor Green
} else {
    Write-Host "[SKIP] Windows Terminal settings not found" -ForegroundColor Yellow
}

# Check claude CLI availability
$claudeCmd = Get-Command claude -ErrorAction SilentlyContinue
if (-not $claudeCmd) {
    Write-Host "`n[WARN] claude CLI not found. Skipping steps 2-5." -ForegroundColor Red
    Write-Host "       Install Claude Code and re-run this script." -ForegroundColor Red
    return
}

# 2. .claude/settings.local.json
$settingsDir = ".claude"
$settingsPath = Join-Path $settingsDir "settings.json"

if (-not (Test-Path $settingsDir)) {
    New-Item -ItemType Directory -Path $settingsDir -Force | Out-Null
}

$settings = @{
    permissions = @{
        allow = @(
            "Bash"
            "Read"
            "Edit"
            "Write"
            "Glob"
            "Grep"
            "WebFetch"
            "WebSearch"
            "Skill"
            "Task"
        )
    }
} | ConvertTo-Json -Depth 3

Set-Content -Path $settingsPath -Value $settings -Encoding UTF8
Write-Host "[OK] $settingsPath created" -ForegroundColor Green

# 3. Plugin marketplaces (register if new, ALWAYS update to latest)
$marketplaces = @(
    @{ repo = "anthropics/skills";   name = "anthropic-agent-skills" }
    @{ repo = "poorants/ant-skills"; name = "ant-agent-skills" }
)

foreach ($mp in $marketplaces) {
    Write-Host "[...] Registering marketplace '$($mp.repo)'..."
    claude plugin marketplace add $mp.repo 2>&1 | Out-Null   # 이미 등록돼 있어도 무해
    Write-Host "[...] Updating marketplace '$($mp.name)'..."
    claude plugin marketplace update $mp.name 2>&1 | Out-Null
    Write-Host "[OK] Marketplace '$($mp.name)' up to date" -ForegroundColor Green
}

# 4. Plugin installation (install if new, ALWAYS update so existing envs refresh)
$plugins = @(
    @{ name = "example-skills@anthropic-agent-skills"; scope = "local" }
    @{ name = "ant-project-kit@ant-agent-skills"; scope = "local" }
)

foreach ($p in $plugins) {
    Write-Host "[...] Installing plugin '$($p.name)'..."
    claude plugin install $p.name --scope $p.scope 2>&1 | Out-Null   # 이미 설치돼 있어도 무해
    Write-Host "[...] Updating plugin '$($p.name)'..."
    claude plugin update $p.name --scope $p.scope 2>&1 | Out-Null
    Write-Host "[OK] Plugin '$($p.name)' up to date" -ForegroundColor Green
}

# 5. .gitignore
if (-not (Test-Path ".gitignore")) {
    New-Item -Path ".gitignore" -ItemType File -Force | Out-Null
    Write-Host "[OK] .gitignore created" -ForegroundColor Green
}

$content = Get-Content ".gitignore" -Raw
if (-not $content) { $content = "" }

$entries = @(
    @{ pattern = '(?m)^docs/?$';   line = "docs/";  comment = "# PARA documents (managed outside repo)" }
)

foreach ($entry in $entries) {
    if ($content -notmatch $entry.pattern) {
        Add-Content -Path ".gitignore" -Value "`n$($entry.comment)`n$($entry.line)" -Encoding UTF8
        Write-Host "[OK] Added '$($entry.line)' to .gitignore" -ForegroundColor Green
    } else {
        Write-Host "[SKIP] '$($entry.line)' already in .gitignore" -ForegroundColor Yellow
    }
}

# 6. PARA document initialization
Write-Host "`n[...] Initializing PARA documents..."
$paraDirs = @("para\projects", "para\areas", "para\resources", "para\archives")
foreach ($dir in $paraDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    $gitkeep = Join-Path $dir ".gitkeep"
    if (-not (Test-Path $gitkeep)) {
        New-Item -ItemType File -Path $gitkeep -Force | Out-Null
    }
}
Write-Host "[OK] PARA structure initialized" -ForegroundColor Green

# 7. Code conventions (house FE standard) — seed doc + CLAUDE.md pointer
Write-Host "`n[...] Seeding code conventions..."
$ccDir = "para\areas\code-convention"
New-Item -ItemType Directory -Path $ccDir -Force | Out-Null

$convPath = Join-Path $ccDir "CONVENTIONS.md"
if (-not (Test-Path $convPath)) {
    try {
        Invoke-WebRequest -UseBasicParsing `
            -Uri "https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/fe-conventions.md" `
            -OutFile $convPath
        Write-Host "[OK] CONVENTIONS.md seeded" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Could not fetch fe-conventions.md (skipping)" -ForegroundColor Yellow
    }
} else {
    Write-Host "[SKIP] CONVENTIONS.md already exists" -ForegroundColor Yellow
}

$changelogPath = Join-Path $ccDir "CHANGELOG.md"
if (-not (Test-Path $changelogPath)) {
    Set-Content -Path $changelogPath -Encoding UTF8 -Value @'
# Code Convention Changelog

## init
Seeded the house FE standard (i18n + data-testid) via the ant-skills bootstrap.
Extend with /code-convention add | evolve.
'@
}

$ccConfig = ".code-convention.json"
if (-not (Test-Path $ccConfig)) {
    Set-Content -Path $ccConfig -Encoding UTF8 -Value '{ "outputDir": "para/areas/code-convention", "ruleCount": 26 }'
}
if (Test-Path ".gitignore") {
    $gi = Get-Content ".gitignore" -Raw
    if (-not $gi) { $gi = "" }
    if ($gi -notmatch '\.code-convention\.json') {
        Add-Content -Path ".gitignore" -Value "`n# code-convention local config`n.code-convention.json" -Encoding UTF8
    }
}

# CLAUDE.md pointer (idempotent) — auto-loaded every session, @import pulls the rules in
$claudeMd = "CLAUDE.md"
if (-not (Test-Path $claudeMd)) { New-Item -ItemType File -Path $claudeMd -Force | Out-Null }
$cm = Get-Content $claudeMd -Raw
if (-not $cm) { $cm = "" }
if ($cm -notmatch 'para/areas/code-convention') {
    Add-Content -Path $claudeMd -Encoding UTF8 -Value @'

## Code conventions

Code conventions live in `para/areas/code-convention/` and are the single source of truth
(naming, style, i18n, data-testid, error handling, security). Read & follow them before
writing or changing code; manage them with the `code-convention` skill.

@para/areas/code-convention/CONVENTIONS.md
'@
    Write-Host "[OK] CLAUDE.md updated with conventions pointer" -ForegroundColor Green
} else {
    Write-Host "[SKIP] CLAUDE.md already references conventions" -ForegroundColor Yellow
}

Write-Host "`n[DONE] Project environment ready!" -ForegroundColor Cyan
