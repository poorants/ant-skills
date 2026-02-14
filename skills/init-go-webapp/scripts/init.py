#!/usr/bin/env python3
"""
init-go-webapp: Initialize a Go + React single-binary web app project.

Usage:
    python init.py <project-name> [--port PORT] [--module MODULE] [--output DIR]

Arguments:
    project-name    Project name (e.g., "My App" or "my-app")
    --port          Server port (default: 9400)
    --module        Go module name (default: project slug)
    --output        Output directory (default: current directory)

Files are generated directly into the output directory (current dir by default).
The output directory is treated as the project root.

Examples:
    cd my-project && python /path/to/init.py "My App"
    python init.py "Team Dashboard" --port 8080 --output ./my-project
"""

import argparse
import os
import re
import shutil
import sys


def slugify(name: str) -> str:
    """Convert project name to kebab-case slug."""
    s = name.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s


def process_template(content: str, replacements: dict) -> str:
    """Replace all {{PLACEHOLDER}} tokens in content."""
    for key, value in replacements.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    return content


def copy_and_process(src_dir: str, dst_dir: str, replacements: dict):
    """Recursively copy files, processing .tmpl files."""
    for root, dirs, files in os.walk(src_dir):
        rel_root = os.path.relpath(root, src_dir)
        dst_root = os.path.join(dst_dir, rel_root) if rel_root != '.' else dst_dir

        os.makedirs(dst_root, exist_ok=True)

        for filename in files:
            src_path = os.path.join(root, filename)

            if filename.endswith('.tmpl'):
                dst_filename = filename[:-5]  # Remove .tmpl extension
                dst_path = os.path.join(dst_root, dst_filename)

                with open(src_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                content = process_template(content, replacements)
                with open(dst_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(content)
            else:
                dst_path = os.path.join(dst_root, filename)
                shutil.copy2(src_path, dst_path)


def main():
    parser = argparse.ArgumentParser(description='Initialize a Go + React web app project')
    parser.add_argument('name', help='Project name')
    parser.add_argument('--port', type=int, default=9400, help='Server port (default: 9400)')
    parser.add_argument('--module', default=None, help='Go module name (default: project slug)')
    parser.add_argument('--output', default='.', help='Output directory (default: current dir)')
    args = parser.parse_args()

    project_name = args.name
    project_slug = slugify(project_name)
    module_name = args.module or project_slug
    port = str(args.port)

    output_dir = os.path.abspath(args.output)

    # Safety check: allow pre-existing non-project items (git, tools, docs)
    ALLOWED_EXISTING = {
        '.git', '.gitignore', '.claude', '.bkit',
        'docs', 'para', 'README.md', 'LICENSE',
        '.pdca-status.json',
    }
    if os.path.exists(output_dir) and os.listdir(output_dir):
        contents = set(os.listdir(output_dir))
        unexpected = contents - ALLOWED_EXISTING
        if unexpected:
            print(f"Error: {output_dir} contains unexpected files: {', '.join(sorted(unexpected))}")
            print(f"Allowed pre-existing: {', '.join(sorted(ALLOWED_EXISTING))}")
            sys.exit(1)

    assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')

    replacements = {
        'PROJECT_NAME': project_name,
        'PROJECT_SLUG': project_slug,
        'MODULE_NAME': module_name,
        'PORT': port,
    }

    print(f"Initializing: {project_name}")
    print(f"  Slug:   {project_slug}")
    print(f"  Module: {module_name}")
    print(f"  Port:   {port}")
    print(f"  Output: {output_dir}")
    print()

    # Copy and process all assets
    copy_and_process(assets_dir, output_dir, replacements)

    # Merge .gitignore (append if existing, rename if new)
    gitignore_src = os.path.join(output_dir, 'gitignore')
    gitignore_dst = os.path.join(output_dir, '.gitignore')
    if os.path.exists(gitignore_src):
        if os.path.exists(gitignore_dst):
            # Merge: read existing lines, append only new ones
            with open(gitignore_dst, 'r', encoding='utf-8') as f:
                existing = set(f.read().splitlines())
            with open(gitignore_src, 'r', encoding='utf-8') as f:
                new_content = f.read()
            new_lines = [l for l in new_content.splitlines() if l not in existing]
            if new_lines:
                with open(gitignore_dst, 'a', encoding='utf-8', newline='\n') as f:
                    f.write('\n# init-go-webapp\n')
                    f.write('\n'.join(new_lines) + '\n')
            os.remove(gitignore_src)
        else:
            os.rename(gitignore_src, gitignore_dst)

    service_src = os.path.join(output_dir, 'configs', 'service')
    service_dst = os.path.join(output_dir, 'configs', f'{project_slug}.service')
    if os.path.exists(service_src):
        os.rename(service_src, service_dst)

    # Create empty directories
    for d in ['.local', 'deploy/linux', 'deploy/windows', 'data',
              'web/src/components/ui', 'web/src/pages', 'web/src/lib',
              'web/src/hooks', 'web/public',
              'cmd']:
        os.makedirs(os.path.join(output_dir, d), exist_ok=True)

    # Create .local/app.config.yaml (copy from configs)
    configs_yaml = os.path.join(output_dir, 'configs', 'app.config.yaml')
    local_yaml = os.path.join(output_dir, '.local', 'app.config.yaml')
    if os.path.exists(configs_yaml):
        shutil.copy2(configs_yaml, local_yaml)

    print("Created:")
    print(f"  cmd/server/          # Web server entry point")
    print(f"  web/                 # React + Tailwind frontend + embed.go")
    print(f"  internal/            # Go backend packages")
    print(f"  configs/             # Deploy configs + INSTALL.md")
    print(f"  scripts/             # build / dev / deploy")
    print(f"  go.mod               # Go module ({module_name})")
    print(f"  .local/              # Local dev config")
    print(f"  .gitignore")
    print(f"  CLAUDE.md")
    print()
    print("Next steps:")
    print(f"  cd web && npm install && npm run build && cd ..")
    print(f"  go mod tidy")
    print(f"  .\\scripts\\dev.ps1")


if __name__ == '__main__':
    main()
