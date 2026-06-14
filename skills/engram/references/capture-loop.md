# Capture loop — keeping the brain fed

A brain is only as good as what reaches it. Durable thinking that stays in the
chat and never lands under the PARA base (`brain/`, or legacy `para/`) is lost.
This reference details the three-layer capture loop summarized in SKILL.md.

The hooks are **triggers and backstops, not the engine**. A shell hook cannot
judge what is worth keeping or write it well — that is the model's job. The hooks
only fire a reflection at the right moment.

## 1. Capture-as-you-go (primary, model-driven)

While working, when a durable piece of knowledge crystallizes, record it *then* —
do not wait for session end. Worth capturing:

- a newly defined concept or piece of terminology,
- a design / architecture decision (and the why),
- a good idea to apply to this project,
- a research conclusion or comparison outcome,
- an important gotcha, constraint, or non-obvious failure mode.

Follow the Create Workflow: choose the PARA category, place the note, weave
contextual links into prose, and update the folder MOC (`README.md`).

Stay selective — this is the Brain boundary and no-over-structuring discipline
applied continuously:

- Skip trivia, status chatter, and one-off conversational turns.
- Skip anything the code, git history, or existing docs already capture.
- Don't force links; link only where there is real relevance.

## 2. Wrap-up trigger — `UserPromptSubmit` hook

When the user's message looks like an end-of-session sign-off, the bundled hook
injects a reflect-and-save instruction so the session's final ideas are captured
before the user leaves. This is the primary automatic trigger because it fires at
the natural closing moment.

Default wrap-up phrases (case-insensitive substring; Korean + English): 고생했 ·
수고했 · 오늘은 여기까지 · 마무리하 · 마치자 · 끝내자 · 이만 · 푹 쉬 · wrap up ·
that's all · done for today · good night · good work · … (see `brain_reflect.py`).

Override the list with `ENGRAM_CAPTURE_PHRASES` (comma-separated). When the
injected instruction appears, do the reflection as part of that turn's reply.

## 3. Backstop — `Stop` hook

`Stop` fires after every assistant turn, so the backstop is heavily gated:

- loop guard via `stop_hook_active` (never re-fires inside a continuation),
- per-session cooldown (default 30 min) via a temp marker file; the first
  encounter only starts the clock, so the first nudge lands later in the session.

It exists for long sessions where the user never types a wrap-up phrase. If
nothing is worth keeping, acknowledge in one line and finish — never create
filler.

## Distribution & configuration

These hooks ship with the plugin and need no per-machine setup:

- `hooks/hooks.json` registers `brain_reflect.py` on `UserPromptSubmit` and `Stop`
  (the latter alongside the integrity-lint `Stop` hook), using
  `${CLAUDE_PLUGIN_ROOT}` paths.
- They act only in repos that have a brain (`brain/` or `para/`) and never fail a
  session on error (any exception → silent exit 0).
- Both stdin reads and stdout writes use explicit UTF-8 so Korean text survives on
  non-UTF-8 locales (e.g. Windows cp949).

Env knobs:

| Variable | Default | Effect |
|---|---|---|
| `ENGRAM_CAPTURE_DISABLE` | unset | `1` disables both reflect hooks |
| `ENGRAM_CAPTURE_COOLDOWN_MIN` | `30` | minutes between `Stop`-backstop nudges |
| `ENGRAM_CAPTURE_PHRASES` | built-in list | comma-separated wrap-up phrases |

When a reflection (from either hook) decides something is worth keeping, run it
through the Create Workflow and close with the Integrity Lint Workflow.
