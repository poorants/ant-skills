#!/usr/bin/env python3
"""engram 무결성 검사기 (지식망 린터).

현재 작업 저장소의 PARA base 아래 모든 마크다운 문서를 스캔해
망형 지식 구조의 두 가지 무결성 문제를 찾는다.

  1. 깨진 링크(broken link)
     - 마크다운 상대 링크 `[텍스트](상대/경로.md)`가 실재하지 않는 파일을 가리킴 (오류)
     - 위키링크 `[[이름]]`이 어떤 파일과도 매칭되지 않음 (경고: 아직 안 만든 미래 노트일 수 있음)
  2. 외톨이 문서(orphan node)
     - 어떤 문서로부터도 인바운드 링크를 받지 못한 문서.

engram 스킬(지능)이 이 스크립트(공유 근육)를 호출해 결과를 파싱하고,
끊긴 곳을 잇거나 외톨이에 맥락 링크를 달아 지식망을 복구한다.

PARA base 자동 감지 (스킬은 대상 저장소 루트=cwd 에서 실행):
  - 루트에 projects/·areas/·resources/·archives/ 중 하나라도 있으면 → flat 모드,
    base = 루트(순수 문서저장소/브레인). 단독 문서 repo가 이 경우.
  - 아니고 para/ 가 있으면 → nested 모드, base = para/ (코드 프로젝트 + 문서관리).
  - 둘 다 없으면 → para/ 로 가정(없으면 무음).
  - `--base PATH` 로 강제 지정 가능.

사용법(대상 저장소 루트에서):
    python <스킬경로>/scripts/engram_lint.py            # 사람용 리포트 (문제 없으면 무음)
    python <스킬경로>/scripts/engram_lint.py --json     # 기계용 JSON (스킬이 파싱)
    python <스킬경로>/scripts/engram_lint.py --base .   # base 강제(루트)
    python <스킬경로>/scripts/engram_lint.py --all      # 깨끗해도 요약 출력

종료 코드는 항상 0 (비차단). 위키링크는 미래 노트를 가리킬 수 있어(Obsidian 관행)
무결성 문제를 보고만 하고 작업을 막지 않는다.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path.cwd()
PARA_CATEGORIES = ("projects", "areas", "resources", "archives")

# 외톨이 검사에서 제외할 파일명 (구조적 파일은 링크를 '주는' 쪽이라 외톨이 개념이 무의미)
ORPHAN_EXEMPT_NAMES = {"README.md", "_index.md", "index.md", "CLAUDE.md", "MEMORY.md"}

# 외톨이 검사에서 제외할 (base 기준) 경로 접두사 — blog 등 외부 발행용 격리 구역
ORPHAN_EXEMPT_PREFIXES = ("areas/blog/",)

WIKILINK_RE = re.compile(r"(?<!!)\[\[([^\]\n]+?)\]\]")          # [[target]] / [[target|alias]] (임베드 ![[..]] 제외)
MDLINK_RE = re.compile(r"(?<!!)\[[^\]\n]*\]\(([^)\s]+)\)")       # [text](target) (이미지 ![..](..) 제외)
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)                   # 펜스 코드블록
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")                        # 인라인 코드


def parse_base_arg() -> str | None:
    for i, a in enumerate(sys.argv):
        if a == "--base" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
        if a.startswith("--base="):
            return a.split("=", 1)[1]
    return None


def resolve_base() -> tuple[Path, str]:
    """(base 경로, 표시용 라벨) 반환. flat/nested 자동 감지."""
    arg = parse_base_arg()
    if arg is not None:
        return (REPO / arg).resolve(), arg
    # flat 모드: 루트에 PARA 카테고리 폴더가 있으면 루트가 base (단독 문서저장소)
    if any((REPO / c).is_dir() for c in PARA_CATEGORIES):
        return REPO, "."
    # nested 모드: para/ 가 base (코드 프로젝트 + 문서관리)
    return (REPO / "para").resolve(), "para"


def strip_code(text: str) -> str:
    return INLINE_CODE_RE.sub("", FENCE_RE.sub("", text))


def is_excluded(parts: tuple[str, ...]) -> bool:
    """숨김 디렉토리와 node_modules 제외."""
    return any(p == "node_modules" or (p.startswith(".") and len(p) > 1) for p in parts)


def main() -> int:
    as_json = "--json" in sys.argv
    show_all = "--all" in sys.argv

    base, base_label = resolve_base()

    if not base.is_dir():
        result = {"base": base_label, "scanned": 0, "broken_md_links": [],
                  "dangling_wikilinks": [], "orphans": [], "note": "base 디렉토리 없음"}
        if as_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif show_all:
            print(f"\U0001f9e0 engram: PARA base('{base_label}')를 찾지 못해 검사를 건너뜀.")
        return 0

    def rel(p: Path) -> str:
        try:
            return p.relative_to(REPO).as_posix()
        except ValueError:
            return p.as_posix()

    def rel_base(p: Path) -> str:
        return p.relative_to(base).as_posix()

    files = [p for p in base.rglob("*.md") if not is_excluded(p.relative_to(base).parts)]

    by_stem: dict[str, list[Path]] = {}
    for f in files:
        by_stem.setdefault(f.stem, []).append(f)

    inbound: dict[Path, int] = {f: 0 for f in files}
    broken_md: list[tuple[str, str]] = []
    dangling_wiki: list[tuple[str, str]] = []

    for src in files:
        try:
            text = strip_code(src.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, OSError):
            continue

        for raw in WIKILINK_RE.findall(text):
            name = raw.split("|", 1)[0].split("#", 1)[0].strip()
            if not name:
                continue
            targets = by_stem.get(Path(name).stem, [])
            real_targets = [t for t in targets if t != src]
            if real_targets:
                for t in real_targets:
                    inbound[t] += 1
            elif not targets:
                dangling_wiki.append((rel(src), name))

        for target in MDLINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#", "tel:")):
                continue
            clean = target.split("#", 1)[0].split("?", 1)[0]
            if not clean or not clean.endswith(".md"):
                continue
            resolved = (src.parent / clean).resolve()
            if resolved.exists():
                if resolved != src and resolved in inbound:
                    inbound[resolved] += 1
            else:
                broken_md.append((rel(src), target))

    orphans: list[str] = []
    for f, count in inbound.items():
        if count > 0 or f.name in ORPHAN_EXEMPT_NAMES:
            continue
        rb = rel_base(f)
        if any(rb.startswith(p) for p in ORPHAN_EXEMPT_PREFIXES):
            continue
        orphans.append(rel(f))

    orphans.sort()
    broken_md.sort()
    dangling_wiki.sort()

    result = {
        "base": base_label,
        "scanned": len(files),
        "broken_md_links": [{"source": s, "target": t} for s, t in broken_md],
        "dangling_wikilinks": [{"source": s, "name": n} for s, n in dangling_wiki],
        "orphans": orphans,
    }
    has_issues = bool(broken_md or orphans)

    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if not has_issues and not show_all:
        return 0

    where = "루트" if base_label == "." else f"{base_label}/"
    lines = [f"\U0001f9e0 engram 무결성 검사 ({len(files)}개 문서 / {where})"]
    if broken_md:
        lines.append(f"  ❌ 깨진 링크 {len(broken_md)}건:")
        lines += [f"     - {s} → {t}" for s, t in broken_md]
    if orphans:
        lines.append(f"  \U0001f9ed 외톨이 문서 {len(orphans)}건 (인바운드 링크 없음):")
        lines += [f"     - {o}" for o in orphans]
    if dangling_wiki:
        lines.append(f"  ⚠️  미연결 위키링크 {len(dangling_wiki)}건 (아직 안 만든 노트일 수 있음):")
        lines += [f"     - {s} → [[{n}]]" for s, n in dangling_wiki]
    if not has_issues:
        lines.append("  ✅ 깨진 링크/외톨이 없음.")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
