---
name: init-rust-deskapp
description: Initialize a Rust + React desktop application with Tauri. Creates a complete project scaffold with React (Vite + Tailwind CSS) frontend and Rust backend using Tauri's Command-based IPC. Use when the user wants to create a desktop app, start a Tauri project, initialize with "init rust deskapp", "러스트 데스크탑 앱", "타우리 프로젝트", "Tauri setup", "desktop app with Rust".
---

# init-rust-deskapp

Initialize a Rust + React (Tauri) desktop application.

Frontend communicates with Rust backend via Tauri Commands (IPC). Produces native desktop apps for Windows, macOS, and Linux.

## Init Workflow

### Step 1: Collect Parameters

Ask the user via AskUserQuestion:

1. **Project name** (required) - Default: current directory name in kebab-case. Offer as "(Recommended)" option
2. **Window title** (optional) - Default: project name in Title Case

Derive automatically:
- `PROJECT_SLUG`: kebab-case of project name (e.g., "my-app")
- `WINDOW_TITLE`: Title Case of project name (e.g., "My App")

### Step 2: Run Init Script

```bash
python3 scripts/init.py "<project-name>" --output <project-dir>
```

The script outputs files directly into the output directory. The output directory must be empty (or contain only `.git`, `.claude`, etc.).

**IMPORTANT: NEVER delete existing files or directories to make room for init. If the directory is not empty, ask the user to provide an empty directory or confirm the target path.**

### Step 3: Post-Init

After init completes, guide the user:

```bash
# Windows:
.\scripts\windows\dev.ps1

# macOS/Linux:
./scripts/unix/dev.sh
```

Scripts automatically install npm dependencies if needed.

## Generated Structure

```
{project}/
├── src-tauri/              # Rust backend (Tauri)
│   ├── Cargo.toml
│   ├── tauri.conf.json     # Tauri configuration
│   ├── build.rs
│   ├── icons/              # App icons (placeholder)
│   └── src/
│       ├── main.rs         # Entry point
│       ├── lib.rs          # Commands registration
│       └── commands/       # IPC command handlers
│           └── mod.rs
│
├── web/                    # React + Vite + Tailwind CSS
│   ├── src/
│   │   ├── App.tsx         # Main component with example IPC
│   │   ├── main.tsx
│   │   ├── index.css       # Tailwind directives
│   │   ├── components/
│   │   └── lib/
│   │       └── tauri.ts    # Tauri invoke wrapper
│   ├── index.html
│   ├── package.json        # Includes @tauri-apps/cli
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── tsconfig.json
│
├── scripts/
│   ├── windows/
│   │   ├── dev.ps1         # npm run tauri dev
│   │   └── build.ps1       # npm run tauri build
│   └── unix/
│       ├── dev.sh          # npm run tauri dev
│       └── build.sh        # npm run tauri build
│
├── deploy/                 # Build output (gitignored)
│   ├── windows/            # .msi, .exe
│   ├── mac/                # .app, .dmg
│   └── linux/              # .AppImage, .deb
│
├── .gitignore
└── CLAUDE.md               # Development guidelines
```

## Template Placeholders

| Placeholder | Source | Example |
|-------------|--------|---------|
| `{{PROJECT_NAME}}` | User input | My App |
| `{{PROJECT_SLUG}}` | Auto (kebab-case) | my-app |
| `{{WINDOW_TITLE}}` | User input or auto | My App |

## Key Design Decisions

- **`web/`** not `frontend/`: consistent with Go webapp, concise
- **`src-tauri/`**: Tauri standard location
- **`src-tauri/src/commands/`**: organized IPC handlers
- **Command-based IPC**: type-safe communication via `invoke()`
- **No HTML single files**: Always use React + Tailwind for UI

## Development Guidelines (CLAUDE.md)

The generated CLAUDE.md enforces:

1. **Always React + Tailwind**: Never create HTML single-file pages
2. **Command IPC**: Frontend calls Rust via `invoke("command_name", { args })`
3. **Type safety**: Define types for both Rust and TypeScript
