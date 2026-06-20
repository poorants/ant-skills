#!/usr/bin/env python3
"""repo-map scanner — the deterministic muscle.

Walks a repository and emits a JSON *skeleton* of its organization: detected
stack, likely entry points, a module (directory) tree with file/LOC counts, and
internal + external dependency edges derived from import statements. The repo-map
skill (the intelligence) reads this skeleton, samples key files, and writes the
human/agent-facing MAP.md — this script never writes prose.

It is intentionally heuristic and dependency-free (stdlib only): the goal is a
good-enough structural map an agent can navigate, not a perfect AST. Internal
edges are resolved at *directory* granularity (a module = a directory under a
source root), which is the right altitude for a map.

Usage:
    python scan.py [--root DIR] [--json] [--max-files N]
    # default: scans CWD, prints JSON to stdout (UTF-8)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# Directories never worth mapping.
PRUNE = {
    ".git", "node_modules", "dist", "build", "out", "target", ".venv", "venv",
    "__pycache__", ".next", ".nuxt", ".svelte-kit", "coverage", ".turbo",
    ".cache", "vendor", ".idea", ".vscode", "bin", "obj", ".gradle",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", "site-packages",
}

# Per-language: file extensions + import regexes (capture the imported module).
LANGS = {
    "ts/js": {
        "ext": {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"},
        "imports": [
            re.compile(r"""import\s+(?:[\w*{},\s]+\s+from\s+)?["']([^"']+)["']"""),
            re.compile(r"""require\(\s*["']([^"']+)["']\s*\)"""),
            re.compile(r"""export\s+(?:[\w*{},\s]+\s+)?from\s+["']([^"']+)["']"""),
        ],
    },
    "python": {
        "ext": {".py"},
        "imports": [
            re.compile(r"^\s*import\s+([\w.]+)", re.M),
            re.compile(r"^\s*from\s+([\w.]+)\s+import", re.M),
        ],
    },
    "rust": {
        "ext": {".rs"},
        "imports": [re.compile(r"^\s*use\s+([\w:]+)", re.M)],
    },
    "go": {
        "ext": {".go"},
        "imports": [re.compile(r'"([^"]+)"')],  # within import blocks; noisy but ok
    },
}
EXT_TO_LANG = {e: name for name, spec in LANGS.items() for e in spec["ext"]}

# Manifests → (stack label, parser key)
MANIFESTS = {
    "package.json": "Node/JS",
    "tsconfig.json": "TypeScript",
    "Cargo.toml": "Rust",
    "go.mod": "Go",
    "pyproject.toml": "Python",
    "requirements.txt": "Python",
    "setup.py": "Python",
    "pom.xml": "Java/Maven",
    "build.gradle": "Java/Gradle",
    "Gemfile": "Ruby",
    "composer.json": "PHP",
    "pubspec.yaml": "Dart/Flutter",
    "Dockerfile": "Docker",
    "tauri.conf.json": "Tauri",
}

ENTRY_HINTS = (
    "src/main.rs", "src/lib.rs", "main.go", "src/index.ts", "src/index.tsx",
    "src/index.js", "src/main.ts", "src/main.tsx", "src/main.py", "main.py",
    "src/app.tsx", "index.js", "app.py", "__main__.py", "cmd",
)


def is_pruned(parts: tuple[str, ...]) -> bool:
    return any(p in PRUNE or (p.startswith(".") and p not in (".",) and len(p) > 1
               and p not in {".github"}) for p in parts)


def detect_stack(root: Path) -> tuple[list[str], list[str]]:
    """Return (stack labels, declared external deps) from manifests."""
    stack, deps = [], []
    for name, label in MANIFESTS.items():
        for m in root.rglob(name):
            if is_pruned(m.relative_to(root).parts[:-1]):
                continue
            if label not in stack:
                stack.append(label)
            deps += _manifest_deps(m, name)
            break  # one per manifest type is enough for a label
    return stack, sorted(set(deps))


def _manifest_deps(path: Path, name: str) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    out: list[str] = []
    try:
        if name == "package.json":
            data = json.loads(text)
            for key in ("dependencies", "peerDependencies"):
                out += list(data.get(key, {}).keys())
        elif name in ("Cargo.toml", "pyproject.toml"):
            # cheap TOML: grab [dependencies] / [tool.poetry.dependencies] names
            in_dep = False
            for line in text.splitlines():
                s = line.strip()
                if s.startswith("["):
                    in_dep = "dependencies" in s
                    continue
                if in_dep:
                    mname = re.match(r'["\']?([A-Za-z0-9_.\-]+)["\']?\s*=', s)
                    if mname:
                        out.append(mname.group(1))
        elif name in ("requirements.txt",):
            for line in text.splitlines():
                s = line.strip()
                if s and not s.startswith("#"):
                    out.append(re.split(r"[<>=!~\[ ]", s)[0])
        elif name == "go.mod":
            for m in re.finditer(r"^\s+([\w./\-]+)\s+v", text, re.M):
                out.append(m.group(1))
    except Exception:
        pass
    return [d for d in out if d]


def module_key(dir_parts: tuple[str, ...]) -> str:
    """A module = top source dir + immediate subdir, so the map stays at a
    readable altitude (e.g. 'crates/core', 'frontend/src')."""
    if not dir_parts:
        return "(root)"
    if len(dir_parts) == 1:
        return dir_parts[0]
    return "/".join(dir_parts[:2])


def module_of(rel_path: Path, source_roots: set[str]) -> str:
    return module_key(rel_path.parts[:-1])  # drop filename


def internal_packages(root: Path) -> dict[str, str]:
    """Map an internal package/crate NAME -> its module key, so bare imports of
    sibling workspace packages (e.g. Rust `use my_crate::…`) resolve to internal
    edges. Names are normalized so hyphen/underscore variants both match."""
    reg: dict[str, str] = {}

    def add(name: str, dir_parts: tuple[str, ...]):
        if not name:
            return
        key = module_key(dir_parts)
        for variant in {name, name.replace("-", "_"), name.replace("_", "-")}:
            reg[variant] = key

    for cargo in root.rglob("Cargo.toml"):
        rel = cargo.relative_to(root)
        if is_pruned(rel.parts[:-1]):
            continue
        try:
            txt = cargo.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        m = re.search(r'(?ms)^\[package\][^\[]*?^\s*name\s*=\s*"([^"]+)"', txt)
        if m:
            add(m.group(1), rel.parts[:-1])
    for pkg in root.rglob("package.json"):
        rel = pkg.relative_to(root)
        if is_pruned(rel.parts[:-1]) or len(rel.parts) == 1:
            continue  # root package.json isn't an internal sibling
        try:
            data = json.loads(pkg.read_text(encoding="utf-8", errors="ignore"))
            if isinstance(data.get("name"), str):
                add(data["name"], rel.parts[:-1])
        except Exception:
            pass
    return reg


ENTRY_NAMES = {
    "main.rs", "lib.rs", "main.go", "main.py", "__main__.py", "app.py",
    "index.ts", "index.tsx", "index.js", "main.ts", "main.tsx", "main.js",
    "app.ts", "app.tsx", "server.ts", "server.js", "cli.py", "cli.ts",
}


def scan(root: Path, max_files: int) -> dict:
    stack, declared = detect_stack(root)
    reg = internal_packages(root)
    files: list[Path] = []
    lang_count: dict[str, int] = defaultdict(int)
    modules: dict[str, dict] = {}
    edges: dict[tuple[str, str], int] = defaultdict(int)
    external: dict[str, int] = defaultdict(int)
    file_to_module: dict[str, str] = {}
    source_roots: set[str] = set()

    # First pass: collect source files + module buckets.
    all_paths: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        if is_pruned(rel.parts):
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in PRUNE]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in EXT_TO_LANG:
                all_paths.append(Path(dirpath, fn))

    truncated = len(all_paths) > max_files
    for p in all_paths[:max_files]:
        rel = p.relative_to(root)
        lang = EXT_TO_LANG[p.suffix.lower()]
        lang_count[lang] += 1
        if rel.parts:
            source_roots.add(rel.parts[0])
        mod = module_of(rel, source_roots)
        file_to_module[rel.as_posix()] = mod
        m = modules.setdefault(mod, {"path": mod, "files": 0, "loc": 0, "langs": set()})
        m["files"] += 1
        m["langs"].add(lang)
        files.append(p)

    # Second pass: imports → edges.
    for p in files:
        rel = p.relative_to(root)
        mod = file_to_module[rel.as_posix()]
        lang = EXT_TO_LANG[p.suffix.lower()]
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        modules[mod]["loc"] += text.count("\n") + 1
        for rx in LANGS[lang]["imports"]:
            for mm in rx.findall(text):
                target = mm if isinstance(mm, str) else mm[0]
                resolved = _resolve(target, rel, root, source_roots, reg)
                if resolved is None:
                    external[_external_name(target)] += 1
                elif resolved != mod:
                    edges[(mod, resolved)] += 1

    for m in modules.values():
        m["langs"] = sorted(m["langs"])

    # Entry points: root-relative hints + any discovered file with an entry name
    # that sits at a source root (depth <= 3), so nested crates/apps are caught.
    entries = []
    for hint in ENTRY_HINTS:
        if (root / hint).exists():
            entries.append(hint)
    for p in files:
        rel = p.relative_to(root)
        if p.name in ENTRY_NAMES and len(rel.parts) <= 4:
            entries.append(rel.as_posix())
    # manifest-declared bin/main (package.json)
    pkg = root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8", errors="ignore"))
            if isinstance(data.get("main"), str):
                entries.append(data["main"])
            b = data.get("bin")
            if isinstance(b, str):
                entries.append(b)
            elif isinstance(b, dict):
                entries += list(b.values())
        except Exception:
            pass

    top_external = sorted(external.items(), key=lambda kv: -kv[1])[:25]
    edge_list = [{"from": a, "to": b, "weight": w}
                 for (a, b), w in sorted(edges.items(), key=lambda kv: -kv[1])]

    return {
        "root": str(root),
        "stack": stack,
        "languages": dict(sorted(lang_count.items(), key=lambda kv: -kv[1])),
        "entrypoints": _dedupe(entries),
        "module_count": len(modules),
        "file_count": len(files),
        "truncated": truncated,
        "modules": sorted(modules.values(), key=lambda m: (-m["files"], m["path"])),
        "internal_edges": edge_list,
        "declared_dependencies": declared[:50],
        "observed_external": [{"name": n, "uses": c} for n, c in top_external],
    }


def _resolve(target: str, importer_rel: Path, root: Path,
             source_roots: set[str], reg: dict[str, str]):
    """Map an import target to an internal module key, or None if external."""
    # relative import -> resolve against importer's directory
    if target.startswith("."):
        base = (root / importer_rel).parent
        guess = (base / target).resolve()
        try:
            rel = guess.relative_to(root.resolve())
        except Exception:
            return None
        return module_key(rel.parts)
    # internal workspace package / crate by name (Rust `use crate::`, JS pkg)
    head = re.split(r"[/:\\]", target)[0]
    if head in reg:
        return reg[head]
    # bare import starting with a known source root (e.g. "crates/...", "src/...")
    if head in source_roots and head not in ("", "."):
        return module_key(tuple(target.replace("\\", "/").split("/")))
    return None


def _external_name(target: str) -> str:
    t = target.replace("\\", "/")
    if t.startswith("@"):  # scoped npm package
        return "/".join(t.split("/")[:2])
    if "::" in t:  # rust path -> crate
        return t.split("::")[0]
    return t.split("/")[0].split(".")[0]


def _dedupe(seq):
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="repo-map deterministic scanner")
    ap.add_argument("--root", default=".")
    ap.add_argument("--json", action="store_true", help="(default) emit JSON")
    ap.add_argument("--max-files", type=int, default=5000)
    args = ap.parse_args()
    root = Path(os.path.abspath(args.root))
    result = scan(root, args.max_files)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    sys.stdout.buffer.write((payload + "\n").encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
