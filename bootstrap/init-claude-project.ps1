<#
.SYNOPSIS
    Initialize Claude Code project environment.
.DESCRIPTION
    1. Windows Terminal keybindings (iTerm2 style)
    --- requires claude CLI below ---
    2. .claude/settings.local.json (permissions)
    3. Plugin marketplace registration
    4. Plugin installation
    5. .gitignore (exclude docs/, .bkit/)
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
$settingsPath = Join-Path $settingsDir "settings.local.json"

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

# 3. Plugin marketplaces
$marketplaces = @(
    "popup-studio-ai/bkit-claude-code"
    "anthropics/skills"
    "poorants/ant-skills"
)

foreach ($mp in $marketplaces) {
    Write-Host "[...] Registering marketplace '$mp'..."
    $result = claude plugin marketplace add $mp 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Marketplace '$mp' registered" -ForegroundColor Green
    } else {
        Write-Host "[SKIP] Marketplace '$mp' already registered" -ForegroundColor Yellow
    }
}

Write-Host "[...] Updating all marketplaces..."
claude plugin marketplace update
if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Marketplaces updated" -ForegroundColor Green
} else {
    Write-Host "[WARN] Marketplace update failed" -ForegroundColor Red
}

# 4. Plugin installation
$plugins = @(
    @{ name = "bkit"; scope = "local" }
    @{ name = "example-skills@anthropic-agent-skills"; scope = "local" }
    @{ name = "ant-project-kit@ant-agent-skills"; scope = "local" }
)

foreach ($p in $plugins) {
    Write-Host "[...] Installing plugin '$($p.name)'..."
    claude plugin install $p.name --scope $p.scope
    Write-Host "[OK] Plugin '$($p.name)' installed" -ForegroundColor Green
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
    @{ pattern = '(?m)^\.bkit/?$'; line = ".bkit/"; comment = "# bkit plugin data" }
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

Write-Host "`n[DONE] Project environment ready!" -ForegroundColor Cyan
