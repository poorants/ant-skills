#!/usr/bin/env python3
"""
para-docs: Initialize PARA directory structure.

Usage:
    python init.py [--output DIR]

Arguments:
    --output    Base directory (default: current directory)

Creates:
    para/projects/.gitkeep
    para/areas/.gitkeep
    para/resources/.gitkeep
    para/archives/.gitkeep
"""

import argparse
import os


PARA_DIRS = ["projects", "areas", "resources", "archives"]


def init_para(base_dir: str) -> list[str]:
    """Create PARA directories with .gitkeep files. Returns list of created paths."""
    created = []
    for name in PARA_DIRS:
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
    args = parser.parse_args()

    base = os.path.abspath(args.output)
    created = init_para(base)

    print("PARA structure initialized:")
    for path in created:
        print(f"  {path}")


if __name__ == "__main__":
    main()
