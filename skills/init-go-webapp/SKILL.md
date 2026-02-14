---
name: init-go-webapp
description: Initialize a Go + React single-binary web application project. Creates a complete project scaffold with React (Vite + Tailwind CSS + shadcn/ui) frontend and Go backend with SQLite, embedded into a single binary via go:embed. Use when the user wants to create a new Go web app, start a new fullstack project with Go backend, scaffold a single-binary web service, or initialize a project with "init go webapp", "new go project", "Go 웹앱 초기화", "새 프로젝트 만들어줘", "Go+React 프로젝트".
---

# init-go-webapp

Initialize a Go + React (Vite + Tailwind CSS + shadcn/ui) single-binary web application with SQLite.

Frontend is embedded into the Go binary via `go:embed`, producing a single executable that serves both API and SPA.

## Default Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Frontend | React + TypeScript | Vite build |
| Styling | Tailwind CSS | Utility-first |
| UI Components | shadcn/ui | Radix-based components |
| Backend | Go (Golang) | Router + API server |
| Database | SQLite (modernc.org/sqlite) | Dev stage, extensible to Supabase or Litestream |
| Deploy | Go single binary | React build → go:embed → single executable |

## Init Workflow

### Step 1: Collect Parameters

Ask the user via AskUserQuestion:

1. **Project name** (required) - Default: current directory name in kebab-case. Offer as "(Recommended)" option with "Enter manually" alternative
2. **Port** (optional) - Pick a random port in 7000-9999 range (avoid well-known: 8080, 8443, 9090, 9200, 9300) and offer it as "(Recommended)" option with "Enter manually" alternative

Derive automatically:
- `PROJECT_SLUG`: kebab-case of project name (e.g., "team-dashboard")
- `MODULE_NAME`: same as slug unless user specifies a Go module path

### Step 2: Run Init Script

```bash
python scripts/init.py "<project-name>" --port <port> --output <project-dir>
```

The script outputs files directly into the output directory (current dir by default). The output directory is the project root. It must be empty (or contain only `.git`).

**IMPORTANT: NEVER delete existing files or directories to make room for init. If the directory is not empty, ask the user to provide an empty directory or confirm the target path. This skill is for NEW projects only.**

### Step 3: Post-Init

After init completes, guide the user:

```bash
cd web && npm install && npm run build && cd ..
go mod tidy
.\scripts\dev.ps1
```

## Generated Structure

```
{project}/
├── cmd/
│   └── server/main.go      # Web server entry point (-dev flag for dev mode)
│
├── web/                    # React + Vite + Tailwind CSS + shadcn/ui
│   ├── embed.go            # go:embed all:dist (production)
│   ├── embed_dev.go        # empty FS (dev build tag)
│   ├── src/
│   │   ├── components/
│   │   │   └── ui/         # shadcn/ui components (Button included)
│   │   ├── lib/
│   │   │   └── utils.ts    # cn() utility for class merging
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── App.tsx         # Demo with health check + Button
│   │   ├── main.tsx
│   │   └── index.css       # Tailwind + shadcn/ui CSS variables
│   ├── index.html
│   ├── package.json
│   ├── components.json     # shadcn/ui configuration
│   ├── vite.config.ts      # Proxy /api to Go backend
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── postcss.config.js
│
├── internal/               # Go private packages
│   ├── config/config.go    # YAML config loader (server + database)
│   ├── database/database.go # SQLite (modernc.org/sqlite, WAL mode)
│   └── server/server.go    # HTTP server + CORS + health endpoint
│
├── configs/                # Deploy configuration
│   ├── app.config.yaml     # Example config
│   ├── {name}.service      # systemd unit file
│   └── INSTALL.md          # Linux installation guide
│
├── scripts/                # PowerShell scripts
│   ├── build.ps1           # npm build + go build (linux/windows)
│   ├── dev.ps1             # npm build + go run -tags dev (single process)
│   └── deploy.ps1          # Build + SSH deploy (parameterized)
│
├── .local/                 # Dev config (gitignored)
│   └── app.config.yaml
│
├── data/                   # SQLite database (gitignored)
│
├── deploy/                 # Build output (gitignored)
│   ├── linux/
│   └── windows/
│
├── go.mod
├── .gitignore
└── CLAUDE.md               # Project documentation for Claude
```

## Template Placeholders

| Placeholder | Source | Example |
|-------------|--------|---------|
| `{{PROJECT_NAME}}` | User input | Team Dashboard |
| `{{PROJECT_SLUG}}` | Auto (kebab-case) | team-dashboard |
| `{{MODULE_NAME}}` | Auto or user override | team-dashboard |
| `{{PORT}}` | User input or default | 9400 |

## Key Design Decisions

- **`web/`** not `frontend/`: concise, Go ecosystem convention
- **`internal/`** not `backend/`: Go standard layout, enforces package privacy
- **`cmd/`**: standard Go multi-binary layout, easy to add tools (gen-cert, migrate, etc.)
- **`web/embed.go`**: `go:embed` at `web/` level so path is `all:dist`, avoids `..` limitation
- **`embed_dev.go`**: `//go:build dev` tag provides empty FS, avoids needing `web/dist` for compilation
- **Root `go.mod`**: single module, no `go.work` needed
- **`.local/`** not `dev/`: dotfile convention for local-only files
- **`configs/`**: deploy-ready files with INSTALL.md included in build output
- **`scripts/`**: PowerShell for Windows-first dev, cross-compiles to Linux
- **shadcn/ui**: copy-paste component model, no runtime dependency, full customization
- **SQLite (modernc.org/sqlite)**: CGo-free pure Go, WAL mode, single file DB in `data/`
- **Dev mode**: `npm run build` → `go run -tags dev` (single process, no Vite dev server)
