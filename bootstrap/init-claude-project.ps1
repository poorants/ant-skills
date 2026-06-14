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
    6. Document structure + conventions — mode-aware:
       brain (flat root vault) / project (nested brain/ + stack conventions) / empty (ask the plan)
.EXAMPLE
    iex (irm https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/init-claude-project.ps1)
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# --- Mode & stack detection (run at project root, BEFORE any scaffolding) ---
# Three modes:
#   brain   : standalone doc vault with PARA folders already at root -> flat (root)
#   project : repo with code -> nested (brain/, or existing para/) docs + convention seed
#   empty   : empty repo -> no guessing, leave a note asking the user for the plan
function Get-RootHasPara {
    foreach ($c in @('projects', 'areas', 'resources', 'archives')) {
        if (Test-Path $c) { return $true }
    }
    return $false
}
function Get-ProjectStack {
    $hasReact = $false
    $hasNode = Test-Path "package.json"
    if ($hasNode) {
        try { $pkg = Get-Content "package.json" -Raw } catch { $pkg = "" }
        if ($pkg -match '"(react|next|nuxt|vue|svelte|@angular/core|solid-js|astro)"') { $hasReact = $true }
    }
    $back = @()
    if (Test-Path "Cargo.toml") { $back += "rust" }
    if (Test-Path "go.mod") { $back += "go" }
    if ((Test-Path "build.gradle") -or (Test-Path "build.gradle.kts") -or (Test-Path "pom.xml")) { $back += "java" }
    if ((Test-Path "pyproject.toml") -or (Test-Path "requirements.txt") -or (Test-Path "setup.py")) { $back += "python" }
    return [PSCustomObject]@{ HasReact = $hasReact; HasNode = $hasNode; Backends = $back }
}
function Get-IsEmpty {
    $ignore = @('.git', '.claude', '.gitignore', 'CLAUDE.md', 'README.md', 'LICENSE', '.code-convention.json', '.obsidian', '.bkit', 'docs')
    $items = Get-ChildItem -Force | Where-Object { $ignore -notcontains $_.Name }
    return (@($items).Count -eq 0)
}

$script:Stack = Get-ProjectStack
$script:HasCode = ($script:Stack.HasNode -or $script:Stack.Backends.Count -gt 0)
$script:BrainExists = Test-Path "brain"
if ($script:HasCode) { $script:Mode = 'project' }              # code -> nested brain/ + conventions
elseif ($script:BrainExists) { $script:Mode = 'brain' }        # existing nested brain vault
elseif (Get-RootHasPara) { $script:Mode = 'flat-legacy' }      # old root-level PARA vault (back-compat)
elseif (Get-IsEmpty) { $script:Mode = 'empty' }
else { $script:Mode = 'project' }   # files but no code markers -> generic seed

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
    claude plugin marketplace add $mp.repo 2>&1 | Out-Null   # harmless if already registered
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
    claude plugin install $p.name --scope $p.scope 2>&1 | Out-Null   # harmless if already installed
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

# 6 & 7. Document structure + conventions
# Policy: if detected, apply the recommendation automatically. If undetected
#         (empty repo), prompt for input on the spot. When non-interactive
#         (pipe/CI), input is impossible, so fall back to a CLAUDE.md note.

function Setup-Brain {
    # Standalone vault, new unified layout: docs under brain/, root stays for meta/exports.
    Write-Host "[SETUP] Standalone document vault (brain) — nested brain/ PARA" -ForegroundColor Cyan
    foreach ($cat in @("projects", "areas", "resources", "archives")) {
        $dir = Join-Path "brain" $cat
        if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
        $gitkeep = Join-Path $dir ".gitkeep"
        if (-not (Test-Path $gitkeep)) { New-Item -ItemType File -Path $gitkeep -Force | Out-Null }
    }
    Write-Host "[OK] nested brain/ PARA structure ensured. No code conventions seeded (pure doc repo)." -ForegroundColor Green
}

function Setup-FlatLegacy {
    # Existing repo with PARA folders at the root. Leave the layout; just ensure folders.
    Write-Host "[SETUP] Legacy flat vault — PARA folders at root (back-compat)" -ForegroundColor Cyan
    foreach ($dir in @("projects", "areas", "resources", "archives")) {
        if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    }
    Write-Host "[OK] flat PARA ensured. NOTE: the engram default is now brain/ — to unify, move these under brain/." -ForegroundColor Yellow
}

function Setup-Project {
    param([bool]$HasReact, [string[]]$Backends)
    if (-not $Backends) { $Backends = @() }
    $stackDesc = @()
    if ($HasReact) { $stackDesc += "react" }
    if ($Backends.Count -gt 0) { $stackDesc += $Backends }
    if ($stackDesc.Count -eq 0) { $stackDesc += "generic" }

    # Nested base: prefer brain/ (on-brand). Reuse an existing para/ for back-compat.
    $base = if (Test-Path "brain") { "brain" } elseif (Test-Path "para") { "para" } else { "brain" }
    Write-Host "[SETUP] Code project + document management — nested $base/ (stack: $($stackDesc -join '+'))" -ForegroundColor Cyan

    foreach ($cat in @("projects", "areas", "resources", "archives")) {
        $dir = Join-Path $base $cat
        if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
        $gitkeep = Join-Path $dir ".gitkeep"
        if (-not (Test-Path $gitkeep)) { New-Item -ItemType File -Path $gitkeep -Force | Out-Null }
    }
    Write-Host "[OK] nested PARA structure initialized ($base/)" -ForegroundColor Green

    # Convention seed: curated FE standard if React, else a thin generic base (only when absent)
    Write-Host "`n[...] Seeding code conventions..."
    $ccRel = "$base/areas/code-convention"
    $ccDir = Join-Path (Join-Path $base "areas") "code-convention"
    New-Item -ItemType Directory -Path $ccDir -Force | Out-Null
    $seedFile = if ($HasReact) { "fe-conventions.md" } else { "generic-conventions.md" }

    $convPath = Join-Path $ccDir "CONVENTIONS.md"
    if (-not (Test-Path $convPath)) {
        try {
            Invoke-WebRequest -UseBasicParsing `
                -Uri "https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/$seedFile" `
                -OutFile $convPath
            Write-Host "[OK] CONVENTIONS.md seeded ($seedFile)" -ForegroundColor Green
        } catch {
            Write-Host "[WARN] Could not fetch $seedFile (skipping)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[SKIP] CONVENTIONS.md already exists" -ForegroundColor Yellow
    }

    if ($Backends.Count -gt 0) {
        Write-Host "[NOTE] Backend ($($Backends -join ', ')) conventions: extract them from real code with /code-convention." -ForegroundColor Yellow
    }

    $changelogPath = Join-Path $ccDir "CHANGELOG.md"
    if (-not (Test-Path $changelogPath)) {
        Set-Content -Path $changelogPath -Encoding UTF8 -Value @'
# Code Convention Changelog

## init
Seeded a stack-detected starter via the ant-skills bootstrap.
Extract real, stack-specific rules from code with /code-convention, then evolve.
'@
    }

    $ccConfig = ".code-convention.json"
    if (-not (Test-Path $ccConfig)) {
        Set-Content -Path $ccConfig -Encoding UTF8 -Value ('{ "outputDir": "__BASE__/areas/code-convention" }' -replace '__BASE__', $base)
    }
    if (Test-Path ".gitignore") {
        $gi = Get-Content ".gitignore" -Raw
        if (-not $gi) { $gi = "" }
        if ($gi -notmatch '\.code-convention\.json') {
            Add-Content -Path ".gitignore" -Value "`n# code-convention local config`n.code-convention.json" -Encoding UTF8
        }
    }

    $claudeMd = "CLAUDE.md"
    if (-not (Test-Path $claudeMd)) { New-Item -ItemType File -Path $claudeMd -Force | Out-Null }
    $cm = Get-Content $claudeMd -Raw
    if (-not $cm) { $cm = "" }
    if ($cm -notmatch 'areas/code-convention') {
        $pointer = @'

## Code conventions

Code conventions live in `__BASE__/areas/code-convention/` and are the single source of truth
(naming, style, error handling, security; FE adds i18n + data-testid). Read & follow them
before writing or changing code; manage them with the `code-convention` skill.

@__BASE__/areas/code-convention/CONVENTIONS.md
'@ -replace '__BASE__', $base
        Add-Content -Path $claudeMd -Encoding UTF8 -Value $pointer
        Write-Host "[OK] CLAUDE.md updated with conventions pointer ($ccRel)" -ForegroundColor Green
    } else {
        Write-Host "[SKIP] CLAUDE.md already references conventions" -ForegroundColor Yellow
    }
}

function Write-PendingNote {
    $claudeMd = "CLAUDE.md"
    if (-not (Test-Path $claudeMd)) { New-Item -ItemType File -Path $claudeMd -Force | Out-Null }
    $cm = Get-Content $claudeMd -Raw
    if (-not $cm) { $cm = "" }
    if ($cm -notmatch 'Project setup \(pending\)') {
        Add-Content -Path $claudeMd -Encoding UTF8 -Value @'

## Project setup (pending)

This repo was bootstrapped empty (non-interactive run). Before scaffolding docs or writing
code, ASK the user:

1. Whether this repo should be (a) a code project + document management (nested `brain/`),
   or (b) a standalone document vault (brain, flat root).
2. (If a code project) which stack (e.g. rust+react, go+react, web / macOS desktop).

Based on the answer, set up the PARA structure with the `engram` skill and conventions with
the `code-convention` skill. Delete this section once setup is done.
'@
        Write-Host "[OK] Added 'Project setup (pending)' note to CLAUDE.md — Claude will ask for the plan next session." -ForegroundColor Green
    } else {
        Write-Host "[SKIP] 'Project setup (pending)' note already present" -ForegroundColor Yellow
    }
}

# --- dispatch ---
Write-Host ""
$interactive = [Environment]::UserInteractive -and -not [Console]::IsInputRedirected

if ($script:Mode -eq 'brain') {
    Write-Host "[MODE] Detected: standalone document vault (brain) -> nested brain/" -ForegroundColor Cyan
    Setup-Brain
}
elseif ($script:Mode -eq 'flat-legacy') {
    Write-Host "[MODE] Detected: legacy flat vault (PARA at root) -> keeping as-is (back-compat)" -ForegroundColor Cyan
    Setup-FlatLegacy
}
elseif ($script:Mode -eq 'project') {
    $sd = @()
    if ($script:Stack.HasReact) { $sd += "react" }
    if ($script:Stack.Backends.Count -gt 0) { $sd += $script:Stack.Backends }
    if ($sd.Count -eq 0) { $sd += "generic" }
    Write-Host "[MODE] Detected: code project -> recommending nested brain/ (stack: $($sd -join '+'))" -ForegroundColor Cyan
    Setup-Project -HasReact $script:Stack.HasReact -Backends $script:Stack.Backends
}
else {
    # Empty repo — undetected. Prompt if interactive, else fall back to a note.
    if (-not $interactive) {
        Write-Host "[MODE] Empty repo (non-interactive) — cannot prompt, leaving a note only." -ForegroundColor Yellow
        Write-PendingNote
    } else {
        Write-Host "[MODE] Empty repo — auto-detection failed. Asking how to use it." -ForegroundColor Yellow
        Write-Host "  [1] Standalone document vault (brain) — flat, projects/areas/... at root"
        Write-Host "  [2] Code project + document management — nested brain/"
        $ans = Read-Host "Choose [1/2] (default 2)"
        if ($ans -eq '1') {
            Setup-Brain
        } else {
            Write-Host "Which stack?"
            Write-Host "  [1] rust + react   [2] go + react   [3] react only   [4] other (manual)   [5] generic"
            $s = Read-Host "Choose [1-5] (default 1)"
            $hr = $true; $bk = @("rust")
            switch ($s) {
                '2' { $hr = $true;  $bk = @("go") }
                '3' { $hr = $true;  $bk = @() }
                '4' {
                    $r = Read-Host "React frontend? [y/N]"
                    $hr = ($r -match '^[yY]')
                    $custom = Read-Host "Backends (comma-separated, e.g. rust,go) — blank if none"
                    if ($custom) { $bk = @($custom -split '\s*,\s*' | Where-Object { $_ }) } else { $bk = @() }
                }
                '5' { $hr = $false; $bk = @() }
                default { $hr = $true; $bk = @("rust") }   # 1 or empty -> primary stack
            }
            Setup-Project -HasReact $hr -Backends $bk
        }
    }
}

Write-Host "`n[DONE] Project environment ready!" -ForegroundColor Cyan
