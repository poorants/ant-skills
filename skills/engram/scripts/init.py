#!/usr/bin/env python3
"""
engram: Initialize PARA directory structure.

Usage:
    python init.py [--output DIR] [--flat] [--nested-dir NAME]

Arguments:
    --output      Base directory (default: current directory)
    --flat        Create category folders directly at the base, with no nested
                  prefix. Use when the project keeps PARA folders at its root
                  (a standalone document vault / brain).
    --nested-dir  Nested folder name (default: brain). Ignored with --flat.
                  If omitted and a legacy `para/` already exists (and `brain/`
                  does not), `para` is reused for back-compat.

Creates (nested, default):
    brain/projects/.gitkeep
    brain/areas/.gitkeep
    brain/resources/.gitkeep
    brain/archives/.gitkeep

Creates (--flat):
    projects/.gitkeep
    areas/.gitkeep
    resources/.gitkeep
    archives/.gitkeep
"""

import argparse
import os


PARA_DIRS = ["projects", "areas", "resources", "archives"]


def resolve_nested_dir(base_dir: str, requested: str | None) -> str:
    """Pick the nested folder name: explicit request wins; else prefer brain/,
    reuse a legacy para/ if present, otherwise default to brain."""
    if requested:
        return requested
    if os.path.isdir(os.path.join(base_dir, "brain")):
        return "brain"
    if os.path.isdir(os.path.join(base_dir, "para")):
        return "para"
    return "brain"


def init_para(base_dir: str, flat: bool = False, nested_dir: str | None = None) -> list[str]:
    """Create PARA directories with .gitkeep files. Returns list of created paths."""
    prefix = None if flat else resolve_nested_dir(base_dir, nested_dir)
    created = []
    for name in PARA_DIRS:
        if flat:
            dir_path = os.path.join(base_dir, name)
        else:
            dir_path = os.path.join(base_dir, prefix, name)
        gitkeep = os.path.join(dir_path, ".gitkeep")

        os.makedirs(dir_path, exist_ok=True)

        if not os.path.exists(gitkeep):
            with open(gitkeep, "w") as f:
                f.write("")
            created.append(gitkeep)
        else:
            created.append(f"{dir_path}/ (already exists)")

    return created


def main():
    parser = argparse.ArgumentParser(description="Initialize PARA directory structure")
    parser.add_argument("--output", default=".", help="Base directory (default: current directory)")
    parser.add_argument(
        "--flat",
        action="store_true",
        help="Create category folders at the base, without a nested prefix",
    )
    parser.add_argument(
        "--nested-dir",
        default=None,
        help="Nested folder name (default: brain; reuses legacy para/ if present)",
    )
    args = parser.parse_args()

    base = os.path.abspath(args.output)
    created = init_para(base, flat=args.flat, nested_dir=args.nested_dir)

    mode = "flat" if args.flat else "nested"
    print(f"PARA structure initialized ({mode}):")
    for path in created:
        print(f"  {path}")


if __name__ == "__main__":
    main()
