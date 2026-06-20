#!/usr/bin/env python3
"""engram capture-loop hook — UserPromptSubmit (wrap-up detection) + Stop backstop.

Nudges Claude to reflect on the session and capture durable new concepts /
decisions / ideas into the repo's engram brain. Distributed with the plugin
(see hooks/hooks.json), so no per-machine setup is needed.

Design — three layers (the hooks are NOT the engine):
  - Engine (primary): the model saves things proactively as they crystallize
    during work. See SKILL.md "Capture loop". A shell hook cannot judge what is
    worth keeping, so it only fires the reflection at the right moment.
  - Primary trigger = UserPromptSubmit wrap-up detection: when the user's message
    looks like end-of-session ("고생했다", "수고했어", "wrap up", ...), inject a
    reflect-and-save instruction. Fires at the natural closing moment so the
    final ideas are not lost.
  - Backstop = Stop: time-throttled nudge for long sessions with no wrap-up
    phrase. Stop fires every turn, so it is heavily gated (loop guard + cooldown).

Scope: only repos with an engram brain (brain/ or legacy para/). The hook never
fails a session: any error -> silent exit 0.

Env knobs:
  ENGRAM_CAPTURE_DISABLE=1         -> disable these reflect hooks entirely
  ENGRAM_CAPTURE_COOLDOWN_MIN=30   -> Stop-backstop minutes between nudges
  ENGRAM_CAPTURE_PHRASES="a,b,c"   -> override wrap-up phrases (comma-separated,
                                      case-insensitive substring match)
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from workspace import resolve_brain
except Exception:  # degrade to local-only detection if registry unavailable
    resolve_brain = None

DEFAULT_PHRASES = [
    # Korean wrap-up signals (the user's common forms)
    "고생했", "수고했", "수고하", "오늘은 여기까지", "여기까지 하", "여기까지만",
    "마무리하", "마무리 하", "마치자", "끝내자", "오늘 그만", "그만하자",
    "푹 쉬", "내일 보", "다음에 보", "이만",
    # English
    "wrap up", "wrap it up", "that's all", "thats all", "that's it",
    "done for today", "good night", "goodnight", "see you", "good work",
    "well done", "great work",
]


def brain_info(cwd: str) -> dict | None:
    """Resolve the brain for this repo. Returns {display, external_autopush} or
    None when there is no brain to feed. Honors a workspace assignment (a shared
    external brain) before falling back to a repo-local brain/ · para/."""
    if resolve_brain is not None:
        try:
            r = resolve_brain(cwd)
            if r.get("source") == "assignment" and r.get("base"):
                disp = f"{r.get('brain')} ({r['base']})"
                return {"display": disp, "external_autopush": bool(r.get("autopush"))}
            if r.get("source") in ("local", "assignment-local") and r.get("base") \
                    and Path(r["base"]).is_dir():
                return {"display": r.get("label") or "brain", "external_autopush": False}
        except Exception:
            pass
    for name in ("brain", "para"):
        if (Path(cwd) / name).is_dir():
            return {"display": name, "external_autopush": False}
    return None


def instruction(info: dict, wrapup: bool) -> str:
    base = info["display"]
    head = "[engram 세션 마무리 감지] " if wrapup else "[engram 뇌 회고] "
    body = (
        "이 저장소엔 engram 브레인(`" + base + "`)이 연결돼 있다. 이번 세션 대화를 돌아보고 "
        "'브레인에 남길 가치가 있는' 것이 나왔는지 판단하라 — 새로 정립된 개념·설계 결정·"
        "이 프로젝트에 적용할 좋은 아이디어·리서치 결론·중요한 함정/제약 등 나중에 다시 읽고 "
        "링크할 지식. 있으면 engram 스킬로 알맞은 PARA 폴더에 기록하고, 본문 "
        "맥락에 링크를 녹이고, 해당 폴더 MOC(README.md)를 갱신하고, engram lint로 무결성을 "
        "확인하라. 선별 원칙: 사소한 잡담·진행확인·코드/이력으로 이미 남는 것·이미 문서화된 "
        "것은 적지 마라(과잉 문서화·억지 링크 금지). 남길 게 없으면 '기록할 만한 것 없음' 한 "
        "줄로 밝히고 마쳐라."
    )
    if wrapup:
        body += " 사용자가 세션을 마무리하려 하니, 응답을 마치기 전에 위를 수행하라."
        if info.get("external_autopush"):
            body += (" 이 브레인은 공유(autopush) 브레인이므로, 기록을 마친 뒤 "
                     "`scripts/brain_sync.py push`로 동기화하라(충돌 시 그대로 보고).")
    return head + body


def emit(obj: dict) -> None:
    # UTF-8 bytes: a plain print of Korean on a non-UTF-8 locale (Windows cp949)
    # raises UnicodeEncodeError and emits broken JSON.
    sys.stdout.buffer.write(json.dumps(obj, ensure_ascii=False).encode("utf-8"))
    sys.stdout.buffer.flush()


def main() -> int:
    if os.environ.get("ENGRAM_CAPTURE_DISABLE") == "1":
        return 0
    try:
        # Read stdin as UTF-8 bytes: Claude Code sends UTF-8 JSON, but
        # sys.stdin's text decoder uses the locale (cp949 on Korean Windows),
        # which corrupts/raises on Korean prompts — exactly the wrap-up case.
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    except Exception:
        return 0

    cwd = data.get("cwd") or os.getcwd()
    info = brain_info(cwd)
    if info is None:
        return 0

    event = data.get("hook_event_name", "")

    if event == "UserPromptSubmit":
        prompt = (data.get("prompt") or "").lower()
        raw = os.environ.get("ENGRAM_CAPTURE_PHRASES")
        phrases = [p.strip().lower() for p in raw.split(",")] if raw else DEFAULT_PHRASES
        if any(p and p in prompt for p in phrases):
            emit({
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": instruction(info, wrapup=True),
                }
            })
        return 0

    if event == "Stop":
        if data.get("stop_hook_active"):
            return 0
        session_id = data.get("session_id") or "nosession"
        try:
            cooldown_s = max(0.0, float(os.environ.get("ENGRAM_CAPTURE_COOLDOWN_MIN", "30")) * 60.0)
        except ValueError:
            cooldown_s = 1800.0
        marker = Path(tempfile.gettempdir()) / f"claude-engram-capture-{session_id}.marker"
        now = time.time()
        try:
            if not marker.exists():
                marker.write_text(str(now), encoding="utf-8")  # first encounter: start the clock
                return 0
            if now - marker.stat().st_mtime < cooldown_s:
                return 0
            os.utime(marker, (now, now))
        except Exception:
            return 0
        emit({"decision": "block", "reason": instruction(info, wrapup=False)})
        return 0

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        raise SystemExit(0)  # never break a session
