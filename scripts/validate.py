#!/usr/bin/env python3
"""Validate skill directory structure and SKILL.md frontmatter."""

import argparse
import re
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"
NAME_PATTERN = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")
MAX_NAME_LEN = 64
MAX_DESC_LEN = 1024
MAX_SKILL_LINES = 500


def parse_frontmatter(skill_md: Path) -> dict:
    """Parse YAML frontmatter from SKILL.md."""
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    fm = {}
    for line in text[3:end].strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip()
    return fm


def validate_skill(skill_dir: Path) -> list[str]:
    """Return list of errors for a single skill directory."""
    errors = []
    dir_name = skill_dir.name

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append(f"{dir_name}: missing SKILL.md")
        return errors

    fm = parse_frontmatter(skill_md)

    # name checks
    name = fm.get("name", "")
    if not name:
        errors.append(f"{dir_name}: frontmatter missing 'name'")
    elif name != dir_name:
        errors.append(f"{dir_name}: name '{name}' does not match directory name")
    if name and not NAME_PATTERN.match(name):
        errors.append(f"{dir_name}: name '{name}' contains invalid characters")
    if len(name) > MAX_NAME_LEN:
        errors.append(f"{dir_name}: name exceeds {MAX_NAME_LEN} chars")

    # description checks
    desc = fm.get("description", "")
    if not desc:
        errors.append(f"{dir_name}: frontmatter missing 'description'")
    if len(desc) > MAX_DESC_LEN:
        errors.append(f"{dir_name}: description exceeds {MAX_DESC_LEN} chars")

    # line count check
    line_count = len(skill_md.read_text(encoding="utf-8").splitlines())
    if line_count > MAX_SKILL_LINES:
        errors.append(f"{dir_name}: SKILL.md has {line_count} lines (max {MAX_SKILL_LINES})")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate skills")
    parser.add_argument("--all", action="store_true", help="Validate all skills")
    parser.add_argument("skill", nargs="?", help="Single skill directory to validate")
    args = parser.parse_args()

    if args.skill:
        skill_path = Path(args.skill)
        if not skill_path.is_dir():
            print(f"Error: {args.skill} is not a directory", file=sys.stderr)
            sys.exit(1)
        errors = validate_skill(skill_path)
    elif args.all:
        errors = []
        if not SKILLS_DIR.is_dir():
            print(f"No skills directory found at {SKILLS_DIR}", file=sys.stderr)
            sys.exit(1)
        for skill_dir in sorted(SKILLS_DIR.iterdir()):
            if skill_dir.is_dir():
                errors.extend(validate_skill(skill_dir))
    else:
        parser.print_help()
        sys.exit(1)

    if errors:
        for e in errors:
            print(f"  FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    else:
        print("All validations passed.")


if __name__ == "__main__":
    main()
