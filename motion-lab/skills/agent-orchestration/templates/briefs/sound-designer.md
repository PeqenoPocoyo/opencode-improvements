# Brief — sound designer

You are the SOUND DESIGNER. You may write ONLY under `audio/`. Read `skills/sound-design-pro/SKILL.md` first and follow its protocol.

Inputs: `out/events.json` (from the STITCHED draft; times are final), `dna.json` → `sound` block:
```json
{paste dna.sound}
```
Voice file (optional): {path or none}. Music: {user file | procedural scratch bed | none}. Profile: {social | conservative}.

Deliver: `audio/cues.json`, `audio/mix.wav` (48 kHz stereo), `audio/sound-report.md`.
Required: anchors within 1 frame of events; spectral-balance warnings addressed; `qa_audio.py` run on the result; list the 5 riskiest timestamps for a human to check with headphones. You cannot hear: do not say it sounds good.
Report (<= 15 lines): files, warnings fixed, numbers (LUFS, TP, median alignment error), the 5 timestamps.
