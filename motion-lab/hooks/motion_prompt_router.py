#!/usr/bin/env python3
"""UserPromptSubmit hook: when the prompt is about video/motion/sound/UI-in-video, inject the exact skill order for that job (weak models forget to load skills)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib_motion import *

def main():
    inp = read_input(); p = inp.get("prompt") or inp.get("user_prompt") or ""
    if not VIDEO_WORDS.search(p) and not SOUND_WORDS.search(p): sys.exit(0)
    steps = ["1. Read skills/motion-director/SKILL.md (concept + DNA gates). 2. skills/style-dna: generate 3 DNA candidates, choose one, write dna.json."]
    if UI_WORDS.search(p): steps.append("3. UI in the video -> skills/ui-in-video (components, cursor, camera). Use real copy and numbers.")
    steps.append("4. Pick building blocks by need: backgrounds -> generative-3d-backgrounds; artwork/texture -> motion-canvas-artwork; text -> kinetic-typography; cuts -> transitions-projections; paper/zine -> collage-paper-texture; mascot/character -> vector-characters; user's own footage -> live-action-compositing; no brief -> generative-play; screen effects -> scene-runtime/runtime/fx.js.")
    if SOUND_WORDS.search(p) or VIDEO_WORDS.search(p): steps.append("5. Sound -> sound-design-pro (events -> sync_cues.py). Do not use stock samples placed at t=0.")
    steps.append("6. Big task? Use skills/agent-orchestration (partition by files, <=3 agents, verify on disk). 7. Always finish with skills/qa-critique ritual.")
    steps.append("If the user said the result looks 'the same as before': run fingerprint.py and change >=2 of palette family/type/motion personality/texture/transitions.")
    context("[motion-lab router] This looks like a video/motion task. Follow this order:\n" + "\n".join(steps))
safe_main(main)
