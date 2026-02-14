#!/usr/bin/env python3
"""Skill Doctor — mechanical health checks for Claude Code skills."""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

MAX_LINES = 500
MAX_TOKENS_ESTIMATE = 5000
CHARS_PER_TOKEN = 4  # conservative estimate

RESOURCE_DIRS = ("scripts", "references", "assets")

# Match backtick paths like `scripts/foo.py`, `references/bar.md`, `assets/img.png`
BACKTICK_PATH_RE = re.compile(
    r"`((?:scripts|references|assets)/[^`\s]+)`"
)


def parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter from SKILL.md text."""
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


def get_full_description(text: str) -> str:
    """Extract the full description value from frontmatter, handling multi-line."""
    if not text.startswith("---"):
        return ""
    end = text.find("---", 3)
    if end == -1:
        return ""
    fm_text = text[3:end]
    lines = fm_text.strip().splitlines()
    desc_lines = []
    capturing = False
    for line in lines:
        if not capturing:
            if line.startswith("description:"):
                _, _, value = line.partition(":")
                value = value.strip()
                if value.startswith(">") or value.startswith("|"):
                    capturing = True
                    continue
                desc_lines.append(value)
                capturing = True
            continue
        # continuation lines are indented
        if line.startswith("  ") or line.startswith("\t"):
            desc_lines.append(line.strip())
        else:
            break
    return " ".join(desc_lines)


def extract_trigger_words(description: str) -> set[str]:
    """Extract trigger words/phrases from quoted strings in description."""
    triggers = set()
    # Match both single and double quoted strings
    for match in re.finditer(r'"([^"]+)"', description):
        phrase = match.group(1).strip().lower()
        # Split into individual words for overlap detection
        for word in phrase.split():
            # Skip very common words
            if len(word) > 2:
                triggers.add(word)
    return triggers


def check_orphan_files(skill_dir: Path, skill_text: str) -> list[tuple[str, str, str]]:
    """Check 3: Find files in resource dirs not referenced in SKILL.md."""
    # If any scripts/ file is mentioned in SKILL.md, assets/ are implicitly used by it
    has_referenced_script = "scripts/" in skill_text
    assets_implicitly_covered = has_referenced_script and (skill_dir / "assets").is_dir()

    results = []
    for subdir_name in RESOURCE_DIRS:
        subdir = skill_dir / subdir_name
        if not subdir.is_dir():
            continue
        if subdir_name == "assets" and assets_implicitly_covered:
            continue
        for fpath in sorted(subdir.rglob("*")):
            if not fpath.is_file():
                continue
            rel = fpath.relative_to(skill_dir).as_posix()
            # Check if the file itself or any parent directory is referenced
            parts = rel.split("/")
            referenced = rel in skill_text
            if not referenced:
                for i in range(1, len(parts)):
                    parent_ref = "/".join(parts[:i]) + "/"
                    if parent_ref in skill_text:
                        referenced = True
                        break
            if not referenced:
                results.append(("orphan", "WARN", f"{rel} -- not referenced in SKILL.md"))
    return results


def check_broken_refs(skill_dir: Path, skill_text: str) -> list[tuple[str, str, str]]:
    """Check 4: Find backtick paths in SKILL.md that don't exist on disk."""
    results = []
    for lineno, line in enumerate(skill_text.splitlines(), 1):
        for match in BACKTICK_PATH_RE.finditer(line):
            ref_path = match.group(1)
            full_path = skill_dir / ref_path
            if not full_path.exists():
                results.append(("broken", "ERR", f"{ref_path} -- referenced at line {lineno} but missing"))
    return results


def check_size_budget(skill_text: str) -> list[tuple[str, str, str]]:
    """Check 5: Line count and estimated token budget."""
    lines = skill_text.splitlines()
    line_count = len(lines)
    char_count = len(skill_text)
    token_estimate = char_count // CHARS_PER_TOKEN

    severity = "OK"
    if line_count > MAX_LINES:
        severity = "ERR"
    elif token_estimate > MAX_TOKENS_ESTIMATE:
        severity = "WARN"

    msg = f"{line_count}/{MAX_LINES} lines, ~{token_estimate}/{MAX_TOKENS_ESTIMATE} tokens"
    return [("budget", severity, msg)]


def check_trigger_overlap(
    skill_name: str,
    triggers_by_skill: dict[str, set[str]],
) -> list[tuple[str, str, str]]:
    """Check 7: Find overlapping trigger words between skills."""
    results = []
    my_triggers = triggers_by_skill.get(skill_name, set())
    if not my_triggers:
        return results

    for other_name, other_triggers in sorted(triggers_by_skill.items()):
        if other_name == skill_name:
            continue
        overlap = my_triggers & other_triggers
        if overlap:
            # Calculate overlap ratio (Jaccard similarity)
            union = my_triggers | other_triggers
            ratio = len(overlap) / len(union) if union else 0
            words = ", ".join(sorted(overlap)[:5])
            if len(overlap) > 5:
                words += f" (+{len(overlap) - 5} more)"
            results.append((
                "trigger",
                "WARN" if ratio > 0.3 else "INFO",
                f"overlap with {other_name}: {words} ({ratio:.2f})",
            ))
    return results


def check_skill(
    skill_dir: Path,
    triggers_by_skill: dict[str, set[str]],
) -> list[tuple[str, str, str]]:
    """Run all mechanical checks on a single skill."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [("structure", "ERR", "SKILL.md not found")]

    text = skill_md.read_text(encoding="utf-8")
    results = []
    results.extend(check_orphan_files(skill_dir, text))
    results.extend(check_broken_refs(skill_dir, text))
    results.extend(check_size_budget(text))
    results.extend(check_trigger_overlap(skill_dir.name, triggers_by_skill))
    return results


def discover_skills(base_dir: Path) -> list[Path]:
    """Find all skill directories under base_dir."""
    skills = []
    for child in sorted(base_dir.iterdir()):
        if child.is_dir() and (child / "SKILL.md").exists():
            skills.append(child)
    return skills


def build_trigger_map(skill_dirs: list[Path]) -> dict[str, set[str]]:
    """Build trigger word sets for all skills."""
    triggers = {}
    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        text = skill_md.read_text(encoding="utf-8")
        desc = get_full_description(text)
        triggers[skill_dir.name] = extract_trigger_words(desc)
    return triggers


def format_report(
    results_by_skill: dict[str, list[tuple[str, str, str]]],
) -> str:
    """Format check results into a text report."""
    lines = ["=== Skill Doctor ==="]
    lines.append(f"Skills: {len(results_by_skill)} found")
    lines.append("")

    total_err = 0
    total_warn = 0
    total_info = 0

    for skill_name, results in results_by_skill.items():
        lines.append(f"-- {skill_name} --")
        if not results:
            lines.append("  All checks passed.")
        for check_type, severity, msg in results:
            pad_type = f"[{check_type}]".ljust(11)
            pad_sev = severity.ljust(5)
            lines.append(f"  {pad_type}{pad_sev} {msg}")
            if severity == "ERR":
                total_err += 1
            elif severity == "WARN":
                total_warn += 1
            elif severity == "INFO":
                total_info += 1
        lines.append("")

    lines.append("-- SUMMARY --")
    lines.append(f"ERR: {total_err} | WARN: {total_warn} | INFO: {total_info}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Skill Doctor - health checks for Claude Code skills",
    )
    parser.add_argument(
        "path",
        help="Path to a skills directory or a single skill directory",
    )
    args = parser.parse_args()

    target = Path(args.path).resolve()
    if not target.is_dir():
        print(f"Error: {args.path} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Determine if this is a single skill or a directory of skills
    if (target / "SKILL.md").exists():
        # Single skill — but we still need sibling skills for trigger overlap
        parent = target.parent
        all_skills = discover_skills(parent)
        if not all_skills:
            all_skills = [target]
        skill_dirs = [target]
    else:
        all_skills = discover_skills(target)
        skill_dirs = all_skills

    if not skill_dirs:
        print(f"No skills found in {args.path}", file=sys.stderr)
        sys.exit(1)

    triggers_by_skill = build_trigger_map(all_skills)

    results_by_skill = {}
    for skill_dir in skill_dirs:
        results_by_skill[skill_dir.name] = check_skill(skill_dir, triggers_by_skill)

    report = format_report(results_by_skill)
    print(report)

    # Exit with error code if any ERR found
    has_errors = any(
        sev == "ERR"
        for results in results_by_skill.values()
        for _, sev, _ in results
    )
    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()
