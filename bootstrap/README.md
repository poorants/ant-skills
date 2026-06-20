# Bootstrap

A single one-liner that prepares a machine + directory for Claude Code. It does
exactly two things:

1. **Install/update the toolkits at user scope** — registers the marketplaces
   (`anthropic-agent-skills`, `ant-agent-skills`) and installs/updates the plugins
   (`example-skills`, `ant-common-kit`, `ant-dev-kit`). Idempotent: re-running
   updates them.
2. **Create `.claude/settings.json` (all permissions)** in the current directory.

That's it — no per-repo brain/PARA scaffolding and no convention seeding. Knowledge
and code conventions live in a shared **engram workspace brain** now; you link a repo
to it yourself (see "Next" below).

## Windows (PowerShell 5.1 or 7)

```powershell
iex (irm https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/init-claude-project.ps1)
```

## macOS / Linux

```bash
bash <(curl -sL https://raw.githubusercontent.com/poorants/ant-skills/main/bootstrap/init-claude-project.sh)
```

Requires the [Claude Code CLI](https://claude.ai/code) for step 1 (step 2 still runs
without it).

## Next — link the repo to a shared brain

After the script, set up the engram brain by telling Claude Code (the `engram` skill
understands plain language):

- **Register a brain once** (per machine): *register `<path-to-brain-repo>` as the
  "personal" brain*. The path is a local clone of your brain repo (its own git repo).
- **Link this repo to it**: *use the "personal" brain for this repo*.

From then on, that repo shares the brain's knowledge and inherits its code
conventions (the shared base + per-repo deltas) — managed by the `engram` and
`code-convention` skills.

## Installing kits individually

The bootstrap installs all kits. To install just one:

```bash
claude plugin install ant-common-kit@ant-agent-skills --scope user   # engram (PARA brain + capture-loop hooks)
claude plugin install ant-dev-kit@ant-agent-skills --scope user      # dev tooling (code-convention, component-prototype, git-versioning, repo-map)
```
