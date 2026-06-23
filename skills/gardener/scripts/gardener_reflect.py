#!/usr/bin/env python3
"""gardener capture-loop hook — UserPromptSubmit (grow-flag / prune-flag / wrap-up) + Stop backstop.

Nudges Claude to tend the harness via the gardener skill — both directions:
  GROW  : promote a repeated correction / standing preference UP a tier
          (soft → CLAUDE.md rule → mechanical hook).
  PRUNE : demote/retire over-engineered gates, dead rules, redundant skills.
Distributed with the plugin (see hooks/gardener-hooks.json); no per-machine setup.

Design — the hooks are NOT the engine (mirrors engram's brain_reflect.py):
  - Engine (primary): the model judges what to grow (Promotion Gate, SKILL.md) and
    what to prune (tiers-and-pruning.md). A shell hook cannot decide durable-vs-taste
    or worth-a-hook; it only fires the reflection at the right moment.
  - Explicit grow-flag (UserPromptSubmit): "remember this / 항상 이렇게 / 규칙으로
    만들어 / 이거 훅으로 …" → inject an immediate Grow instruction. Fires in any repo.
  - Explicit prune-flag (UserPromptSubmit): "규칙 정리 / 오버엔지니어링 / tidy the
    harness …" → inject a Prune instruction.
  - Wrap-up reflection (UserPromptSubmit): on an end-of-session phrase, inject a
    bidirectional reflect instruction. Gated to repos that participate in the harness
    (a CLAUDE.md exists locally or at user scope) to avoid nagging.
  - Backstop (Stop): heavily throttled nudge (loop guard + cooldown) for long
    sessions, same gating.

The hook never fails a session: any error -> silent exit 0.

Env knobs:
  GARDENER_DISABLE=1              -> disable these hooks entirely
  GARDENER_COOLDOWN_MIN=60        -> Stop-backstop minutes between nudges
  GARDENER_REMEMBER_PHRASES="a,b" -> override grow-flag phrases (comma-separated,
                                     case-insensitive substring match)
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

# Explicit grow flags -> promote immediately (to the tier it earns).
REMEMBER_PHRASES = [
    "이건 기억해", "기억해둬", "기억해 둬", "기억해라", "기억해 줘", "기억해줘",
    "항상 이렇게", "앞으로 이렇게", "앞으로는 이렇게", "규칙으로", "룰로 만들",
    "룰로 정", "규칙 만들", "넣어둬", "반영해둬", "이거 훅으로", "훅으로 만들",
    "remember this", "from now on", "always do", "always use", "make it a rule",
    "promote to a hook", "make it a hook", "note this preference", "keep doing this",
]

# Explicit prune flags -> review the harness for debt (demote/retire).
PRUNE_PHRASES = [
    "규칙 정리", "훅 정리", "하니스 정리", "규칙 가지치기", "가지치기",
    "오버엔지니어링", "오버 엔지니어링", "과한 규칙", "규칙 솎",
    "prune the rules", "prune learned rules", "tidy the harness", "garden the harness",
    "over-engineered", "over engineered", "this is overkill",
]

# Session wrap-up signals -> reflect bidirectionally on this session.
WRAPUP_PHRASES = [
    "고생했", "수고했", "수고하", "오늘은 여기까지", "여기까지 하", "여기까지만",
    "마무리하", "마무리 하", "마치자", "끝내자", "오늘 그만", "그만하자",
    "이만", "wrap up", "wrap it up", "that's all", "thats all", "that's it",
    "done for today", "good work", "well done", "great work",
]


def harness_participates(cwd: str) -> bool:
    """True when this repo uses the CLAUDE.md harness (local or user scope). Gates the
    reflection nudges so gardener doesn't nag in repos that don't use learned rules."""
    try:
        if (Path(cwd) / "CLAUDE.md").is_file():
            return True
        if (Path.home() / ".claude" / "CLAUDE.md").is_file():
            return True
    except Exception:
        pass
    return False


def grow_instruction() -> str:
    return (
        "[gardener 성장 신호] 사용자가 영구 규칙으로 남길 만한 선호/지시를 명시했다. "
        "gardener 스킬의 Promotion Gate 4관문(durable-not-taste / generalizable / "
        "not-already-covered / no-conflict)으로 판정하라. 통과하면 (1) 어느 티어인지 정하라 "
        "— 기계적 검사 가능 + 강제할 값어치 → T3 훅(스캐폴드 + settings 연결), 판단 필요 → "
        "T2(`CLAUDE.md`의 `gardener:start/end` 블록 한 줄, 날짜+origin), 소프트/일회성 → T1 유지 "
        "또는 드롭. 과승격(전부 훅) 금지. (2) 스코프(레포-로컬 기본, 교차반복 시에만 글로벌). "
        "먼저 대상 파일과 변경(줄 또는 훅 파일+settings)을 사용자에게 보여 승인받고 기록하라(상시 승인 예외). "
        "취향(taste)이면 흡수하지 말고 사유를 한 줄로 밝혀라."
    )


def prune_instruction() -> str:
    return (
        "[gardener 가지치기 신호] 사용자가 하니스 정리를 요청했다. 학습 규칙(`CLAUDE.md`의 "
        "`gardener` 블록)·훅/게이트·스킬을 티어별로 훑어 debt를 찾아라 — 죽은 규칙(stale / "
        "never-fired / redundant / conflicting), 헛도는 게이트(한 번도 안 막은 것·오탐 잦은 것·"
        "superseded), 중복/미사용 스킬. 발견분은 강등(T3→T2) 또는 은퇴를 **제안**하라(자동 삭제 금지; "
        "날짜+origin으로 이력 보존). 무엇을 잃는지 한 줄로 밝혀라(대개 마찰뿐). 기준: gardener 스킬의 "
        "references/tiers-and-pruning.md."
    )


def reflect_instruction(wrapup: bool) -> str:
    head = "[gardener 세션 마무리 회고] " if wrapup else "[gardener 회고] "
    body = (
        "하니스를 양방향으로 돌아보라. (성장↑) 같은 류의 교정을 두 번 이상 반복했거나 standing "
        "운영 규칙이 드러났으면 Promotion Gate로 판정해 통과분만 알맞은 티어(검사가능+값어치→훅, "
        "판단필요→규칙)·스코프로 제안→승인→기록하라. (가지치기↓) 기존 학습 규칙·훅·게이트 중 "
        "죽은 것(한 번도 안 터진 게이트·아무도 발동 기억 못 하는 규칙·중복 스킬·의식만 남은 단계)이 "
        "있으면 강등/은퇴를 제안하라 — 하니스는 커지기만 하면 안 되고 더 날카로워져야 한다. "
        "과흡수·과강제 금지. 남기거나 뺄 게 없으면 '변경 없음' 한 줄로 마쳐라."
    )
    if wrapup:
        body += " 사용자가 세션을 마무리하려 하니, 응답을 마치기 전에 위를 수행하라."
    return head + body


def emit(obj: dict) -> None:
    sys.stdout.buffer.write(json.dumps(obj, ensure_ascii=False).encode("utf-8"))
    sys.stdout.buffer.flush()


def main() -> int:
    if os.environ.get("GARDENER_DISABLE") == "1":
        return 0
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except Exception:
        return 0

    cwd = data.get("cwd") or os.getcwd()
    event = data.get("hook_event_name", "")

    if event == "UserPromptSubmit":
        prompt = (data.get("prompt") or "").lower()
        raw = os.environ.get("GARDENER_REMEMBER_PHRASES")
        remember = [p.strip().lower() for p in raw.split(",")] if raw else REMEMBER_PHRASES
        if any(p and p in prompt for p in remember):
            emit({"hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": grow_instruction(),
            }})
            return 0
        if any(p and p in prompt for p in PRUNE_PHRASES):
            emit({"hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": prune_instruction(),
            }})
            return 0
        if harness_participates(cwd) and any(p and p in prompt for p in WRAPUP_PHRASES):
            emit({"hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": reflect_instruction(wrapup=True),
            }})
        return 0

    if event == "Stop":
        if data.get("stop_hook_active"):
            return 0
        if not harness_participates(cwd):
            return 0
        session_id = data.get("session_id") or "nosession"
        try:
            cooldown_s = max(0.0, float(os.environ.get("GARDENER_COOLDOWN_MIN", "60")) * 60.0)
        except ValueError:
            cooldown_s = 3600.0
        marker = Path(tempfile.gettempdir()) / f"claude-gardener-{session_id}.marker"
        now = time.time()
        try:
            if not marker.exists():
                marker.write_text(str(now), encoding="utf-8")  # start the clock
                return 0
            if now - marker.stat().st_mtime < cooldown_s:
                return 0
            os.utime(marker, (now, now))
        except Exception:
            return 0
        emit({"decision": "block", "reason": reflect_instruction(wrapup=False)})
        return 0

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        raise SystemExit(0)  # never break a session
