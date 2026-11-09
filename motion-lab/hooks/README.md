# Hooks — automatic guard-rails for motion work

Hooks are small scripts the harness runs at fixed moments. They **cannot make a weak model creative**, but they stop it from skipping the steps that cause "same soul" and broken renders.

| Hook | Event | What it does |
|---|---|---|
| `motion_session_start.py` | SessionStart | injects the 12 rules + project state (dna.json present? ledger size) |
| `motion_prompt_router.py` | UserPromptSubmit | detects video/sound/UI prompts (pt-BR + en) and injects the exact skill order |
| `pre_write_guard.py` | PreToolUse Write/Edit | lints scene HTML; **blocks** Math.random/Date/rAF/timers/CSS animation/Google Fonts/external URLs, and blocks a new scene before `dna.json` exists |
| `post_render_qa.py` | PostToolUse Bash | after `render.mjs`: stills → "READ the PNG"; mp4 → auto `qa_video.py`; records what QA was done |
| `stop_gate.py` | Stop | blocks finishing (once) if a video was rendered without QA + contact sheet + fingerprint |

All hooks **fail open** (a bug never blocks you). Unit tests: `python3 hooks/tests/test_hooks.py` (12 tests).

## Install (Claude Code / compatible harnesses)
1. Put the pack somewhere stable and export `MOTION_LAB_HOME` (e.g. `export MOTION_LAB_HOME=~/motion-lab`).
2. Merge `settings.snippet.json` into `.claude/settings.json` (project) or `~/.claude/settings.json` (global).
3. Windows PowerShell: `setx MOTION_LAB_HOME "C:\Users\you\motion-lab"` and replace `python3` with `python` in the snippet.
4. Restart the session; run `echo '{}' | python3 "$MOTION_LAB_HOME/hooks/motion_session_start.py"` to verify output.

## Harness without hooks (Beam / OpenCode / chat agents)
Use `hooks/guard.sh` — the model runs it manually at the same moments (`guard.sh start | scene | stills | qa`). The system-prompt snippet in `instructions/MOTION-LAB-RULES.md` tells the model when to call it. If the harness supports only a system prompt: paste `instructions/MOTION-LAB-RULES.md` + `instructions/weak-model-playbook.md`.

## Other instruction types you can add later
- **Slash commands / prompts:** `instructions/prompts/*.md` (paste or register as commands).
- **Subagents:** `skills/agent-orchestration/templates/briefs/*.md` (role briefs).
- **Output styles / persona:** `instructions/weak-model-playbook.md` section "Voice of the director".
