#!/usr/bin/env python3
"""
para-docs: Initialize PARA directory structure.

Usage:
    python init.py [--output DIR] [--flat]

Arguments:
    --output    Base directory (default: current directory)
    --flat      Create category folders directly at the base, with no para/
                prefix. Use when the project keeps PARA folders at its root.

Creates (nested, default):
    para/projects/.gitkeep
    para/areas/.gitkeep
    para/resources/.gitkeep
    para/archives/.gitkeep

Creates (--flat):
    projects/.gitkeep
    areas/.gitkeep
    resources/.gitkeep
    archives/.gitkeep
"""

import argparse
import os


PARA_DIRS = ["projects", "areas", "resources", "archives"]


def init_para(base_dir: str, flat: bool = False) -> list[str]:
    """Create PARA directories with .gitkeep files. Returns list of created paths."""
    created = []
    for name in PARA_DIRS:
        if flat:
            dir_path = os.path.join(base_dir, name)
        else:
            dir_path = os.path.join(base_dir, "para", name)
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
        help="Create category folders at the base, without a para/ prefix",
    )
    args = parser.parse_args()

    base = os.path.abspath(args.output)
    created = init_para(base, flat=args.flat)

    mode = "flat" if args.flat else "nested"
    print(f"PARA structure initialized ({mode}):")
    for path in created:
        print(f"  {path}")


if __name__ == "__main__":
    main()
