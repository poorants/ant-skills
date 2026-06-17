#!/usr/bin/env python3
"""Guard that the release surface stays in sync: marketplace.json ↔ README ↔ bootstrap ↔ skills.

This catches the drift class where a plugin/skill is added, renamed, or removed in
marketplace.json but the install scripts or docs are left pointing at the old shape
(exactly what bit us when ant-project-kit / ant-app-kit / ant-dev-tools diverged).

Modes:
    python3 scripts/check_release_sync.py          # standalone report — exit 0 clean, 1 on drift
    python3 scripts/check_release_sync.py --hook    # PreToolUse hook — reads JSON on stdin,
                                                     # only acts on `git commit` Bash calls,
                                                     # exits 2 to BLOCK the commit on drift

The gists are synced FROM the bootstrap scripts (single source of truth), so this checks the
local invariants and, on drift, reminds you to re-run scripts/sync_gists.sh.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Plugin names that have been retired — must not linger in any doc/script.
KNOWN_STALE = ["ant-project-kit", "ant-app-kit", "ant-dev-tools"]


def check() -> list[str]:
    errors: list[str] = []

    mp = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    plugins = mp.get("plugins", [])
    plugin_names = [p["name"] for p in plugins]

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    sh = (ROOT / "bootstrap" / "init-claude-project.sh").read_text(encoding="utf-8")
    ps1 = (ROOT / "bootstrap" / "init-claude-project.ps1").read_text(encoding="utf-8")
    doc_targets = [("README.md", readme),
                   ("bootstrap/init-claude-project.sh", sh),
                   ("bootstrap/init-claude-project.ps1", ps1)]

    # 1. every live plugin is mentioned in README + installed by both bootstrap scripts
    for name in plugin_names:
        for fname, text in doc_targets:
            if name not in text:
                errors.append(f"plugin '{name}' is in marketplace.json but missing from {fname}")

    # 2. no retired plugin name still referenced anywhere
    for stale in KNOWN_STALE:
        if stale in plugin_names:
            continue
        for fname, text in doc_targets:
            if stale in text:
                errors.append(f"retired plugin name '{stale}' still referenced in {fname}")

    # 3. registered skills ⇔ skills/ on disk
    referenced = set()
    for p in plugins:
        for s in p.get("skills", []):
            rel = s.replace("./", "", 1)
            referenced.add(Path(rel).name)
            if not (ROOT / rel / "SKILL.md").exists():
                errors.append(f"plugin '{p['name']}' lists '{s}' but {rel}/SKILL.md does not exist")
    skills_dir = ROOT / "skills"
    if skills_dir.is_dir():
        for d in sorted(skills_dir.iterdir()):
            if d.is_dir() and (d / "SKILL.md").exists() and d.name not in referenced:
                errors.append(f"skill '{d.name}' exists under skills/ but is registered in no marketplace plugin")

    # 4. spec compliance (reuse the existing validator)
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from validate import validate_skill
        if skills_dir.is_dir():
            for d in sorted(skills_dir.iterdir()):
                if d.is_dir() and (d / "SKILL.md").exists():
                    errors.extend(validate_skill(d))
    except Exception as e:  # validator import/parse problems shouldn't crash the guard
        errors.append(f"could not run skill spec validation: {e}")

    return errors


def main() -> int:
    hook = "--hook" in sys.argv

    if hook:
        # Only gate `git commit`; everything else passes through untouched. Fail OPEN on any
        # parsing/checker error so a guard bug never blocks unrelated Bash calls.
        try:
            data = json.load(sys.stdin)
            cmd = (data.get("tool_input") or {}).get("command", "")
        except Exception:
            return 0
        if "git commit" not in cmd:
            return 0
        try:
            errors = check()
        except Exception:
            return 0
    else:
        errors = check()

    if not errors:
        if not hook:
            print("release sync OK — marketplace.json ↔ README ↔ bootstrap ↔ skills consistent")
        return 0

    lines = ["release sync check FAILED — fix before committing:"]
    lines += [f"  - {e}" for e in errors]
    lines += ["", "After fixing marketplace.json / README / bootstrap, re-sync the gists:",
              "    bash scripts/sync_gists.sh"]
    print("\n".join(lines), file=sys.stderr)
    return 2 if hook else 1


if __name__ == "__main__":
    raise SystemExit(main())
