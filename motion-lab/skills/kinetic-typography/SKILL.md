---
name: kinetic-typography
description: Kinetic typography for videos - 31 reveal/exit styles (slide masks, blur focus, slam, flip, weight/width morph, scramble, glitch, wipe, zoom-through...), word-level captions (pop/highlight/karaoke/stack), fit-to-box, marquee, highlight/underline, plus type direction (22 embedded offline fonts, pairings, hierarchy, rhythm). Use for any headline, title card, lyric/quote video, captions/subtitles, text-led motion poster, or when text animation looks generic ("fade up on everything").
---

# kinetic-typography — type is the performer

Runtime `runtime/type.js` (global `Type`, needs lab.js). Fonts: `fonts/` (22 families, offline; Google Fonts is blocked) — list with moods in `reference/fonts-catalog.md`.

## Decide before animating
1. **Voice** of the text (shout / whisper / explain / joke). Choose font + weight from DNA `type` and `fonts-catalog.md` (moods, pairsWith). One display family + one text/mono family. Never default to Inter for everything.
2. **Hierarchy:** one hero line (≥ 3× the size of the support line), support line, tiny label. Max 3 sizes.
3. **Rhythm:** read the line aloud; each stressed word gets its own beat (`by:'words'`, stagger = beat spacing). Align reveal times to `Lab.beat`/sound events.
4. **Choose reveal by meaning**, not by novelty:
| Meaning | Style |
|---|---|
| Authority, impact | `slam`, `stampDown`, `zoomThrough` |
| Calm, premium | `fadeBlur`, `riseFade`, `blurFocus`, `trackIn` |
| Clean editorial | `slideUp` (mask), `maskWipe`, `splitReveal` |
| Playful | `pop`, `elastic`, `dropBounce`, `wave`, `swing` |
| Tech / data | `scramble`, `glitchIn`, `typewriter`, `widthMorph` |
| Energy / sport | `cascadeSides`, `slam`, `shuffle`, `weightMorph` |
| Craft | `inkFill`, `maskWipeUp`, `stretchIn` (underline) |
5. **Max 2 reveal styles per video** (hero style + a quieter support style) and different from the previous video's (ledger `type:<style>`).
6. **Exit** is part of the design: `exit:{t1, style:'fadeBlur', dur:.35}` — or cut on the beat; never leave text lingering without motion for > 2.5 s (add slow scale drift 1.00→1.03 or tracking).

## API quick
```js
const T = Type.make(el, 'Ship faster', {by:'chars', mask:true});
Type.apply(T, 'slideUp', t, {t0:.4, dur:.7, stagger:.035, order:'center', exit:{t1:3.2, style:'fadeBlur'}});
Type.fit(el, 900, 360);                          // largest font-size that fits the box
const C = Type.captions(capEl, words, {group:3, style:'highlight', active:'#ffd400'}); C.at(t);   // words:[{w,t,e}]
Type.highlight(spanEl, p, '#ffe14a'); Type.underline(pathEl, p); Type.marquee(el, t, {speed:180});
```
CSS needed for good type: `text-wrap:balance; font-kerning:normal; font-feature-settings:'ss01'` where available; hero tracking −0.03…−0.05em, caps +0.04em; line-height 0.9–1.0 for display.

## Captions (talking-head, reels)
Group 2–4 words; 64–96 px bold at 1080 wide; safe zone: bottom third, above UI (≥ 220 px from bottom); active word colour + scale 1.12; no more than 2 lines; white with 6 px dark stroke or a solid pill for readability; sync to word timestamps (`t,e` from the transcript).

## Typographic layouts that avoid "centered text on gradient"
- Giant word cropped by the frame edge + small caption aligned to a grid line.
- Stacked words with alternating weights/widths (variable font morph).
- Type as texture: repeating word rows at 8% opacity behind the hero.
- Type clipped with artwork (see `motion-canvas-artwork/examples/art-poster.html`).
- Type on a path (SVG `textPath`) with `Lab.pathAt` for motion.
- Numbers as heroes: `Lab.countUp` + tabular numerals.

## Files
`runtime/type.js` · `reference/{styles-catalog,fonts-catalog}.md` · `examples/type-gallery.html` · `fonts/` (woff2 + fonts.css + fonts.json + LICENSES.md)
