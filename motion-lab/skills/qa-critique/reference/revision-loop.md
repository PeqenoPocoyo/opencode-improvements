# Revision loop (max 3 passes; weak models loop forever otherwise)

```
PASS n:
 1. Run the ritual (lint → stills → draft → qa → sheet → frame_diff → fingerprint)
 2. Score with rubric.md. Write the critique format (verdict, top 3, keep 2).
 3. Fix ONLY the top 3 problems. One commit-sized change each (a parameter, a style, a timing). Do not redesign.
 4. Re-render the affected stills; if they improved, continue to the next pass or ship.
STOP when: all rubric lines ≥ 3 and no FAIL in qa_video → ship.
STOP at pass 3 regardless: ship the best version and list the remaining known issues honestly.
```
## Rules
- Fix order: **hook → hierarchy/legibility → timing → distinctiveness → finish → sound**. Polish never precedes structure.
- If `fingerprint.py` says TOO CLOSE: change at least two of (palette family, type pairing, motion personality, texture, transition set). A new accent colour is not enough.
- If a fix breaks something, revert it (keep a copy `scene.v{n}.html` before each pass).
- When a sub-agent QA critic exists (agent-orchestration role `qa-critic`), give it ONLY the sheet + rubric + DNA, not your reasoning, so it is not anchored on your view.
- Report to the user: what changed in each pass in one line each, plus the final scores. No essays.
