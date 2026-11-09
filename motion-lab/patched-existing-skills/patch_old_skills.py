#!/usr/bin/env python3
"""patch_old_skills.py - apply the motion-lab overlay to the ORIGINAL skill-pack-motion-graphics skills (explainer-default/engaging/high-energy, motion-broll, sound-effects).

  python3 patch_old_skills.py <path/to/skill-pack-motion-graphics/skills> [--out patched/]      (default out = ./patched)
Non-destructive: writes patched copies of each SKILL.md (+ CHANGES.md) into --out. Copy them over the originals when satisfied (original asset folders such as sfx/ stay untouched).
What it changes (see CHANGES.md): (1) inserts the MOTION-LAB OVERLAY block (DNA gate, variety rules, QA ritual) right after the frontmatter,
(2) demotes every 'Default palette' / default font line to a LAST-RESORT fallback, (3) sound-effects: replaces the 'never synthesize' rule with the hybrid rule, adds anchor alignment, event-driven cues and the honest-listening rule.
"""
import os, re, sys, argparse

OVERLAY = """
> ## MOTION-LAB OVERLAY (read first; it overrides anything below that conflicts)
> 1. **DNA gate:** before writing any scene run `skills/style-dna` (`dna_generate.py --candidates 3`), choose one DNA, save `dna.json`, `--check` it, `--add` it to `.motion/style-history.json`. Colours, fonts, easing personality, texture, transitions and sound palette come from `dna.json`.
> 2. **The "default palette / default font" lines below are a LAST RESORT** (no DNA and no brand). Never use them two videos in a row; never combine the default palette with Inter-only type. A brand given by the user beats the DNA palette but not the DNA motion/texture.
> 3. **Variety:** change at least 3 axes versus the previous video (palette family, type pairing, motion personality, texture, transitions, camera behaviour, sound palette). `skills/qa-critique/scripts/fingerprint.py` must pass.
> 4. **Toolbox:** use `scene-runtime/runtime/lab.js` (+ `fx.js`, `type.js`, `ui-kit.js`, `art.js`, `bg3d.js`, `transitions.js`) instead of hand-rolled helpers; declare `Lab.ev(t,type)` for every hit/transition.
> 5. **Sound:** `skills/sound-design-pro` (events -> `sync_cues.py`). Cues are frame-locked, layered, palette-matched.
> 6. **QA ritual before delivering:** lint -> stills (READ them) -> draft -> `qa_video.py` -> contact sheet (READ) -> fingerprint. Max 3 revision passes.
> 7. Large job? `skills/agent-orchestration` (partition by files, <=3 agents, verify on disk).
"""

SOUND_RULE_OLD = "- **Never synthesize music or sound effects in code** (no oscillator or sine beeps). Use real recorded files."
SOUND_RULE_NEW = """- **Hybrid rule (motion-lab):** do not use bare oscillator beeps. Build effects as LAYERS (sub + transient + body + tail) with `sound-design-pro/scripts/sfxgen.py`, or place the bundled CC0 recordings through `sync_cues.py --use-library <sfx dir>` where a real recording fits better (typing, clicks, paper). Layered procedural sound is acceptable; one sine blip is not.
- **Anchor:** every cue is aligned to a frame boundary + 6 ms (the first visible frame of the hit), not to an arbitrary float time. Whooshes PEAK at the cut; risers END at the hit.
- **Events first:** the scene declares `Lab.ev(t,type)`; `render.mjs --events` dumps them; the sound pass reads that file instead of guessing cut times from the video.
- **Never place the same sample at the start of every video.** Palette comes from `dna.json` (`sound.palette`).
- **Honesty:** you cannot hear the result. Report numbers (LUFS/true peak/spectral balance/alignment) and give the user 5 timestamps to listen to."""

def patch_skill(name, text):
    m = re.match(r"(---\n.*?\n---\n)(.*)", text, re.S)
    if not m: return text
    head, body = m.groups(); changes = ["overlay"]
    body = OVERLAY + body
    n_before = body
    body = re.sub(r"(^\s*[-*]?\s*\*\*Default palette[^*]*\*\*)(?! \(LAST)", r"\1 (LAST RESORT - overridden by dna.json / brand)", body, flags=re.M)
    body = body.replace("If none, use the default palette below.", "If none, use dna.json (preferred) or, as a last resort, the default palette below.")
    body = body.replace("otherwise Inter or Geist", "otherwise the DNA's display font (never default to Inter)")
    if body != n_before: changes.append("palette/font demoted")
    if name == "sound-effects":
        if SOUND_RULE_OLD in body: body = body.replace(SOUND_RULE_OLD, SOUND_RULE_NEW); changes.append("sound hybrid rule")
        body = body.replace("Measure the **exported MP4**, never the intermediate WAV.\n- Measure the **exported MP4**, never the intermediate WAV.", "Measure the **exported MP4**, never the intermediate WAV.")
        body = body.replace("**-16 LUFS integrated** with **true peak below -4 dBFS**", "**-16 LUFS integrated** with **true peak below -4 dBFS** (this is the `--profile conservative` of sync_cues.py; use `--profile social` = -14 LUFS / -1 dBTP for short social videos)")
    return head + body, changes

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("skills_dir"); ap.add_argument("--out", default="patched"); a = ap.parse_args(); log = ["# CHANGES (generated)\n"]
    for name in sorted(os.listdir(a.skills_dir)):
        p = os.path.join(a.skills_dir, name, "SKILL.md")
        if not os.path.exists(p) or name == "object-separation": continue
        res = patch_skill(name, open(p, encoding="utf-8").read())
        if isinstance(res, str): continue
        txt, ch = res; od = os.path.join(a.out, name); os.makedirs(od, exist_ok=True); open(os.path.join(od, "SKILL.md"), "w", encoding="utf-8").write(txt); log.append(f"- {name}: {', '.join(ch)}")
    open(os.path.join(a.out, "CHANGES.md"), "w").write("\n".join(log) + "\n"); print("\n".join(log))
main()
