#!/usr/bin/env python3
"""reflex capture-loop hook — UserPromptSubmit (remember-flag + wrap-up) + Stop backstop.

Nudges Claude to absorb repeated corrections / standing preferences into the harness
(CLAUDE.md learned-rules block) via the reflex skill. Distributed with the plugin
(see hooks/hooks.json); no per-machine setup.

Design — the hooks are NOT the engine (mirrors engram's brain_reflect.py):
  - Engine (primary): the model judges what's worth absorbing via the Absorption
    Rulebook (SKILL.md). A shell hook cannot decide durable-vs-taste; it only fires
    the reflection at the right moment.
  - Explicit remember-flag (UserPromptSubmit): when the user's message says "remember
    this / 항상 이렇게 / 규칙으로 만들어 …", inject an immediate Absorb instruction.
    Fires in any repo — the user asked directly.
  - Wrap-up reflection (UserPromptSubmit): on an end-of-session phrase, inject a
    reflect-on-corrections instruction. Gated to repos that participate in the harness
    (a CLAUDE.md exists locally or at user scope) to avoid nagging.
  - Backstop (Stop): heavily throttled nudge (loop guard + cooldown) for long
    sessions, same gating.

The hook never fails a session: any error -> silent exit 0.

Env knobs:
  REFLEX_DISABLE=1              -> disable these hooks entirely
  REFLEX_COOLDOWN_MIN=60        -> Stop-backstop minutes between nudges
  REFLEX_REMEMBER_PHRASES="a,b" -> override remember-flag phrases (comma-separated,
                                   case-insensitive substring match)
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

# Explicit standing-preference flags -> absorb immediately.
REMEMBER_PHRASES = [
    "이건 기억해", "기억해둬", "기억해 둬", "기억해라", "기억해 줘", "기억해줘",
    "항상 이렇게", "앞으로 이렇게", "앞으로는 이렇게", "규칙으로", "룰로 만들",
    "룰로 정", "규칙 만들", "넣어둬", "반영해둬",
    "remember this", "from now on", "always do", "always use", "make it a rule",
    "note this preference", "keep doing this",
]

# Session wrap-up signals -> reflect on this session's repeated corrections.
WRAPUP_PHRASES = [
    "고생했", "수고했", "수고하", "오늘은 여기까지", "여기까지 하", "여기까지만",
    "마무리하", "마무리 하", "마치자", "끝내자", "오늘 그만", "그만하자",
    "이만", "wrap up", "wrap it up", "that's all", "thats all", "that's it",
    "done for today", "good work", "well done", "great work",
]


def harness_participates(cwd: str) -> bool:
    """True when this repo uses the CLAUDE.md harness (local or user scope). Gates the
    reflection nudges so reflex doesn't nag in repos that don't use learned rules."""
    try:
        if (Path(cwd) / "CLAUDE.md").is_file():
            return True
        if (Path.home() / ".claude" / "CLAUDE.md").is_file():
            return True
    except Exception:
        pass
    return False


def absorb_instruction() -> str:
    return (
        "[reflex 흡수 신호] 사용자가 영구 규칙으로 남길 만한 선호/지시를 명시했다. "
        "reflex 스킬의 Absorption Rulebook 4관문(durable-not-taste / generalizable / "
        "not-already-covered / no-conflict)으로 판정하라. 통과하면 스코프(레포-로컬 기본, "
        "교차반복 시에만 글로벌)를 정하고, `CLAUDE.md`의 `reflex:start/end` 블록에 "
        "한 줄 규칙(날짜+origin 주석)으로 추가하되 — 먼저 대상 파일과 추가할 줄을 사용자에게 "
        "보여 승인받고 기록하라(상시 승인은 예외). 취향(taste)이면 흡수하지 말고 그 이유를 한 줄로 밝혀라."
    )


def reflect_instruction(wrapup: bool) -> str:
    head = "[reflex 세션 마무리 회고] " if wrapup else "[reflex 회고] "
    body = (
        "이번 세션에서 같은 류의 교정을 두 번 이상 반복했거나, 사용자가 standing으로 원하는 "
        "운영 규칙이 드러났는지 돌아보라. 있으면 reflex 스킬의 Absorption Rulebook으로 판정해 "
        "통과하는 것만, 알맞은 스코프의 `CLAUDE.md` `reflex` 블록에 제안→승인→기록하라. "
        "일회성 취향·이미 적힌 규칙·특정 인스턴스에만 맞는 것은 제외한다(과흡수 금지). "
        "남길 게 없으면 '흡수할 규칙 없음' 한 줄로 마쳐라."
    )
    if wrapup:
        body += " 사용자가 세션을 마무리하려 하니, 응답을 마치기 전에 위를 수행하라."
    return head + body


def emit(obj: dict) -> None:
    sys.stdout.buffer.write(json.dumps(obj, ensure_ascii=False).encode("utf-8"))
    sys.stdout.buffer.flush()


def main() -> int:
    if os.environ.get("REFLEX_DISABLE") == "1":
        return 0
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except Exception:
        return 0

    cwd = data.get("cwd") or os.getcwd()
    event = data.get("hook_event_name", "")

    if event == "UserPromptSubmit":
        prompt = (data.get("prompt") or "").lower()
        raw = os.environ.get("REFLEX_REMEMBER_PHRASES")
        remember = [p.strip().lower() for p in raw.split(",")] if raw else REMEMBER_PHRASES
        if any(p and p in prompt for p in remember):
            emit({"hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": absorb_instruction(),
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
            cooldown_s = max(0.0, float(os.environ.get("REFLEX_COOLDOWN_MIN", "60")) * 60.0)
        except ValueError:
            cooldown_s = 3600.0
        marker = Path(tempfile.gettempdir()) / f"claude-reflex-{session_id}.marker"
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
