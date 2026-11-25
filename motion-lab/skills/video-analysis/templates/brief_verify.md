# BRIEF — VERIFY {{FID}}

You are a verification agent. A previous agent was unsure about something. Look at the NEW images and settle it, or say it cannot be settled.

**Original question:** {{QUESTION}}
**What to check ({{T0}} → {{T1}}):** {{WHY}}
**Mode:** {{MODE}}   (burst = consecutive frames at a fixed small step so you can see motion/easing; crop = zoomed region for small text/detail; pair = two moments side by side with a difference map)

**Image(s) to open:** {{IMAGES}}

## Do this
Open the image(s). For `burst`, number the frames and describe how the thing moves from frame to frame (distance per frame: accelerating? decelerating? overshoot?). For `crop`, transcribe text exactly. For `pair`, list what differs (the bright areas of the difference map show where).

## Output — write ONLY this JSON to `reports/{{FID}}.json`
```json
{ "followup_id": "{{FID}}", "t0": {{T0S}}, "t1": {{T1S}}, "finding": "...", "confidence": 0.8, "seen": true, "evidence": ["frame labels you used"], "still_unknown": "..." }
```
Rules: if the images do not settle it, `finding` = "not determinable from these images" and `confidence` ≤ 0.3. Never extend beyond what these images show.
