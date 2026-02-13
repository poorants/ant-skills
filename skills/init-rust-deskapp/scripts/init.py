#!/usr/bin/env python3
"""
init-rust-deskapp: Initialize a Rust + React (Tauri) desktop app project.

Usage:
    python3 init.py <project-name> [--title TITLE] [--output DIR]

Arguments:
    project-name    Project name (e.g., "My App" or "my-app")
    --title         Window title (default: project name in Title Case)
    --output        Output directory (default: current directory)

Examples:
    cd my-project && python3 /path/to/init.py "My App"
    python3 init.py "File Manager" --output ./file-manager
"""

import argparse
import base64
import os
import re
import shutil
import struct
import sys
import zlib


def create_png(width: int, height: int, r: int, g: int, b: int, a: int = 255) -> bytes:
    """Create a simple solid color RGBA PNG image."""
    def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
        chunk_len = struct.pack('>I', len(data))
        chunk_crc = struct.pack('>I', zlib.crc32(chunk_type + data) & 0xffffffff)
        return chunk_len + chunk_type + data + chunk_crc

    # PNG signature
    signature = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk (color type 6 = RGBA)
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    ihdr = png_chunk(b'IHDR', ihdr_data)

    # IDAT chunk (image data - RGBA)
    raw_data = b''
    for _ in range(height):
        raw_data += b'\x00'  # filter byte
        for _ in range(width):
            raw_data += bytes([r, g, b, a])
    compressed = zlib.compress(raw_data)
    idat = png_chunk(b'IDAT', compressed)

    # IEND chunk
    iend = png_chunk(b'IEND', b'')

    return signature + ihdr + idat + iend


def create_icns(sizes: list) -> bytes:
    """Create a simple .icns file with solid color icons."""
    # Simplified ICNS - just creates a basic file structure
    # Real ICNS requires specific formats, but Tauri accepts PNGs in icons/
    return b''  # Skip ICNS, use PNG instead


def generate_icons(icons_dir: str):
    """Generate placeholder icons for Tauri."""
    # Blue color (#3B82F6)
    r, g, b = 59, 130, 246

    icon_sizes = {
        '32x32.png': 32,
        '128x128.png': 128,
        '128x128@2x.png': 256,
    }

    for filename, size in icon_sizes.items():
        png_data = create_png(size, size, r, g, b)
        with open(os.path.join(icons_dir, filename), 'wb') as f:
            f.write(png_data)

    # For icon.ico and icon.icns, we'll create simple versions
    # icon.ico - use 32x32 PNG embedded
    ico_data = create_ico(32, r, g, b)
    with open(os.path.join(icons_dir, 'icon.ico'), 'wb') as f:
        f.write(ico_data)

    # icon.icns - create from PNG (simplified)
    icns_data = create_icns_from_png(128, r, g, b)
    with open(os.path.join(icons_dir, 'icon.icns'), 'wb') as f:
        f.write(icns_data)


def create_ico(size: int, r: int, g: int, b: int) -> bytes:
    """Create a simple .ico file."""
    png_data = create_png(size, size, r, g, b)

    # ICO header
    header = struct.pack('<HHH', 0, 1, 1)  # Reserved, Type (1=ICO), Count

    # ICO directory entry
    entry = struct.pack('<BBBBHHII',
        size if size < 256 else 0,  # Width
        size if size < 256 else 0,  # Height
        0,  # Color palette
        0,  # Reserved
        1,  # Color planes
        32, # Bits per pixel
        len(png_data),  # Size of image data
        22  # Offset to image data (6 + 16)
    )

    return header + entry + png_data


def create_icns_from_png(size: int, r: int, g: int, b: int) -> bytes:
    """Create a simple .icns file with PNG data."""
    png_data = create_png(size, size, r, g, b)

    # ICNS header
    icns_type = b'icns'
    # ic07 = 128x128 PNG
    icon_type = b'ic07'

    icon_entry = icon_type + struct.pack('>I', len(png_data) + 8) + png_data
    total_size = 8 + len(icon_entry)

    header = icns_type + struct.pack('>I', total_size)

    return header + icon_entry


def slugify(name: str) -> str:
    """Convert project name to kebab-case slug."""
    s = name.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s


def to_snake_case(name: str) -> str:
    """Convert to snake_case for Rust identifiers."""
    return slugify(name).replace('-', '_')


def title_case(name: str) -> str:
    """Convert to Title Case."""
    return ' '.join(word.capitalize() for word in name.split())


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
    parser = argparse.ArgumentParser(description='Initialize a Rust + React (Tauri) desktop app')
    parser.add_argument('name', help='Project name')
    parser.add_argument('--title', default=None, help='Window title (default: project name)')
    parser.add_argument('--output', default='.', help='Output directory (default: current dir)')
    args = parser.parse_args()

    project_name = args.name
    project_slug = slugify(project_name)
    project_snake = to_snake_case(project_name)
    window_title = args.title or title_case(project_name)

    output_dir = os.path.abspath(args.output)

    # Safety check: allow pre-existing non-project items
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
        'PROJECT_SNAKE': project_snake,
        'WINDOW_TITLE': window_title,
    }

    print(f"Initializing: {project_name}")
    print(f"  Slug:   {project_slug}")
    print(f"  Snake:  {project_snake}")
    print(f"  Title:  {window_title}")
    print(f"  Output: {output_dir}")
    print()

    # Copy and process all assets
    copy_and_process(assets_dir, output_dir, replacements)

    # Rename gitignore to .gitignore
    gitignore_src = os.path.join(output_dir, 'gitignore')
    gitignore_dst = os.path.join(output_dir, '.gitignore')
    if os.path.exists(gitignore_src):
        if os.path.exists(gitignore_dst):
            with open(gitignore_dst, 'r', encoding='utf-8') as f:
                existing = set(f.read().splitlines())
            with open(gitignore_src, 'r', encoding='utf-8') as f:
                new_content = f.read()
            new_lines = [l for l in new_content.splitlines() if l not in existing]
            if new_lines:
                with open(gitignore_dst, 'a', encoding='utf-8', newline='\n') as f:
                    f.write('\n# init-rust-deskapp\n')
                    f.write('\n'.join(new_lines) + '\n')
            os.remove(gitignore_src)
        else:
            os.rename(gitignore_src, gitignore_dst)

    # Create empty directories
    for d in ['web/src/components', 'web/src/pages', 'web/public',
              'src-tauri/icons']:
        os.makedirs(os.path.join(output_dir, d), exist_ok=True)

    # Generate placeholder icons
    icons_dir = os.path.join(output_dir, 'src-tauri', 'icons')
    generate_icons(icons_dir)
    print("  Generated placeholder icons in src-tauri/icons/")

    # Make unix scripts executable
    unix_scripts_dir = os.path.join(output_dir, 'scripts', 'unix')
    if os.path.exists(unix_scripts_dir):
        for script in os.listdir(unix_scripts_dir):
            script_path = os.path.join(unix_scripts_dir, script)
            os.chmod(script_path, 0o755)

    print("Created:")
    print("  src-tauri/           # Rust backend (Tauri)")
    print("  web/                 # React + Tailwind frontend")
    print("  scripts/windows/     # PowerShell scripts")
    print("  scripts/unix/        # Bash scripts")
    print("  CLAUDE.md            # Development guidelines")
    print("  .gitignore")
    print()
    print("Next steps:")
    print("  # Windows:")
    print("  .\\scripts\\windows\\dev.ps1")
    print()
    print("  # macOS/Linux:")
    print("  ./scripts/unix/dev.sh")


if __name__ == '__main__':
    main()
