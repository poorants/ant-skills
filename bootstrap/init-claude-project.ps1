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
       brain(flat 루트 문서저장소) / project(nested para/ + 스택 컨벤션) / empty(계획 질문)
.EXAMPLE
    iex (irm https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/init-claude-project.ps1)
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# --- Mode & stack detection (run at project root, BEFORE any scaffolding) ---
# 세 가지 모드를 구분한다:
#   brain   : 루트에 PARA 폴더가 이미 있는 단독 문서저장소 → flat(루트) 사용
#   project : 코드가 있는 저장소 → nested(para/)로 문서관리 + 컨벤션 시드
#   empty   : 빈 저장소 → 추측 금지, 사용자에게 계획을 묻도록 노트만 남김
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
if (Get-RootHasPara) { $script:Mode = 'brain' }
elseif ($script:HasCode) { $script:Mode = 'project' }
elseif (Get-IsEmpty) { $script:Mode = 'empty' }
else { $script:Mode = 'project' }   # 코드 마커는 없지만 파일이 있는 경우 generic 시드로

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

# 6 & 7. Document structure + conventions (mode-aware)
Write-Host ""
if ($script:Mode -eq 'brain') {
    # 단독 문서저장소(브레인) — flat. 루트의 PARA 구조를 사용/보강.
    Write-Host "[MODE] 단독 문서저장소(브레인) — flat(루트) PARA 사용" -ForegroundColor Cyan
    foreach ($dir in @("projects", "areas", "resources", "archives")) {
        if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    }
    Write-Host "[OK] flat PARA structure ensured (root). 코드 컨벤션은 시드하지 않음(순수 문서 repo)." -ForegroundColor Green
}
elseif ($script:Mode -eq 'empty') {
    # 빈 저장소 — 추측 금지. 사용자에게 계획을 묻도록 CLAUDE.md 노트만 남김.
    Write-Host "[MODE] 빈 저장소 — 계획 미정. 스캐폴딩 보류, 사용자에게 물어보도록 노트만 남김." -ForegroundColor Yellow
    $claudeMd = "CLAUDE.md"
    if (-not (Test-Path $claudeMd)) { New-Item -ItemType File -Path $claudeMd -Force | Out-Null }
    $cm = Get-Content $claudeMd -Raw
    if (-not $cm) { $cm = "" }
    if ($cm -notmatch 'Project setup \(pending\)') {
        Add-Content -Path $claudeMd -Encoding UTF8 -Value @'

## Project setup (pending)

This repo was bootstrapped empty. Before scaffolding docs or writing code, ASK the user:

1. 이 저장소를 (a) 코드 프로젝트 + 문서관리(nested `para/`) 로 갈지,
   (b) 순수 문서저장소(브레인, flat 루트) 로 갈지.
2. (코드 프로젝트라면) 어떤 스택인지 (예: rust+react, go+react, 웹/맥 데스크탑).

답에 따라 `engram` 스킬로 PARA 구조를, `code-convention` 스킬로 컨벤션을 셋업한다.
이 섹션은 셋업이 끝나면 지운다.
'@
        Write-Host "[OK] CLAUDE.md에 'Project setup (pending)' 노트 추가 — 다음 세션에 Claude가 계획을 묻는다." -ForegroundColor Green
    } else {
        Write-Host "[SKIP] 'Project setup (pending)' 노트가 이미 있음" -ForegroundColor Yellow
    }
}
else {
    # 코드 프로젝트 — nested(para/)로 문서관리 + 스택 맞춤 컨벤션 시드.
    $stackDesc = @()
    if ($script:Stack.HasReact) { $stackDesc += "react" }
    if ($script:Stack.Backends.Count -gt 0) { $stackDesc += $script:Stack.Backends }
    if ($stackDesc.Count -eq 0) { $stackDesc += "generic" }
    Write-Host "[MODE] 코드 프로젝트 + 문서관리 — nested para/ (감지: $($stackDesc -join '+'))" -ForegroundColor Cyan

    $paraDirs = @("para\projects", "para\areas", "para\resources", "para\archives")
    foreach ($dir in $paraDirs) {
        if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
        $gitkeep = Join-Path $dir ".gitkeep"
        if (-not (Test-Path $gitkeep)) { New-Item -ItemType File -Path $gitkeep -Force | Out-Null }
    }
    Write-Host "[OK] nested PARA structure initialized (para/)" -ForegroundColor Green

    # 컨벤션 시드: React 있으면 큐레이션된 FE 표준, 아니면 얇은 generic 베이스 (없을 때만)
    Write-Host "`n[...] Seeding code conventions..."
    $ccDir = "para\areas\code-convention"
    New-Item -ItemType Directory -Path $ccDir -Force | Out-Null
    $seedFile = if ($script:Stack.HasReact) { "fe-conventions.md" } else { "generic-conventions.md" }

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

    # 백엔드(rust/go 등)는 큐레이션 시드가 없으니 코드에서 추출하도록 안내
    if ($script:Stack.Backends.Count -gt 0) {
        Write-Host "[NOTE] 백엔드($($script:Stack.Backends -join ', ')) 컨벤션은 /code-convention 으로 실제 코드에서 추출하세요." -ForegroundColor Yellow
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
        Set-Content -Path $ccConfig -Encoding UTF8 -Value '{ "outputDir": "para/areas/code-convention" }'
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
(naming, style, error handling, security; FE adds i18n + data-testid). Read & follow them
before writing or changing code; manage them with the `code-convention` skill.

@para/areas/code-convention/CONVENTIONS.md
'@
        Write-Host "[OK] CLAUDE.md updated with conventions pointer" -ForegroundColor Green
    } else {
        Write-Host "[SKIP] CLAUDE.md already references conventions" -ForegroundColor Yellow
    }
}

Write-Host "`n[DONE] Project environment ready!" -ForegroundColor Cyan
