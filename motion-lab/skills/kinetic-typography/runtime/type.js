/* type.js - Type: kinetic typography engine (global `Type`, needs lab.js). 30 reveal/exit styles, ordering, fit-to-box, captions, marquee, highlight/underline.
 *
 *   const T = Type.make(el, 'Ship faster', { by:'chars'|'words'|'lines', mask:false });     // splits into spans (pieces)
 *   Type.apply(T, 'slideUp', t, { t0:0.4, dur:.7, stagger:.035, order:'forward'|'reverse'|'center'|'edges'|'random', seed:3, exit:{ t1:3.2, style:'fadeBlur', dur:.4 } });
 *   Type.list()  Type.styles[name]  (meta: {desc, needsMask, by})
 *   Type.fit(el, boxW, boxH, {min:20,max:900})        // sets the largest font-size that fits (uses scrollWidth)
 *   const C = Type.captions(el, [{w:'Hello',t:.2,e:.5}, ...], {group:3, style:'pop'|'highlight'|'karaoke', active:'#ffd400', dim:.55});  C.at(t)
 *   Type.marquee(el, t, {speed:160, dir:-1})  Type.underline(svgPath, p)  Type.highlight(spanEl, p, color)
 * Pure functions of t. Every style takes progress p (0..1) per piece; pieces that have not started are hidden, finished ones are exactly at rest.
 */
(function (root) {
  'use strict';
  const L = root.Lab, clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), E = n => L.ease.get(n), Type = {};
  const lerp = (a, b, k) => a + (b - a) * k;
  // each style: (p, ctx) -> {o, tf, filter, extra:{prop:value}} ; ctx = {i,n,k (index 0..1), seed, rnd(), el, w(width px), h}
  const S = {}, meta = {};
  const def = (name, desc, fn, m = {}) => { S[name] = fn; meta[name] = Object.assign({ desc }, m); };
  const e = E('snap'), eo = E('outCubic'), ep = E('punch');
  def('fade', 'plain opacity', p => ({ o: eo(p) }));
  def('fadeBlur', 'fade in from a blur (calm, cinematic)', p => ({ o: eo(p), filter: `blur(${(1 - eo(p)) * 18}px)`, tf: `scale(${1.06 - .06 * eo(p)})` }));
  def('slideUp', 'rise from a mask line (needs mask)', p => ({ o: 1, tf: `translateY(${(1 - e(p)) * 112}%)` }), { needsMask: true });
  def('slideDown', 'drop in from above a mask line', p => ({ o: 1, tf: `translateY(${-(1 - e(p)) * 112}%)` }), { needsMask: true });
  def('slideRight', 'wipe in from the left edge of a mask', p => ({ o: 1, tf: `translateX(${-(1 - e(p)) * 112}%)` }), { needsMask: true });
  def('riseFade', 'small rise + fade (editorial)', p => ({ o: eo(p), tf: `translateY(${(1 - eo(p)) * 40}px)` }));
  def('slam', 'scale down from huge with overshoot', p => { const k = L.curves.settle(p); return { o: clamp(p * 6), tf: `scale(${lerp(2.6, 1, k)})`, filter: `blur(${(1 - e(p)) * 8}px)` }; });
  def('pop', 'spring pop from 0 (playful)', (p, c) => { const k = L.spring(p * .8, 16, .55); return { o: clamp(p * 8), tf: `scale(${k})` }; });
  def('rotateIn', 'tilts in from rotation', (p, c) => ({ o: clamp(p * 4), tf: `rotate(${(1 - e(p)) * (c.i % 2 ? 40 : -40)}deg) translateY(${(1 - e(p)) * 30}px)` }));
  def('flip3d', 'flips up around X axis (3D)', p => ({ o: clamp(p * 5), tf: `perspective(600px) rotateX(${(1 - e(p)) * -95}deg)`, origin: '50% 100%' }));
  def('flipY', 'card flip around Y axis', p => ({ o: clamp(p * 5), tf: `perspective(700px) rotateY(${(1 - e(p)) * 100}deg)` }));
  def('dropBounce', 'falls from above and bounces', p => { const y = -(1 - L.ease.get('outBounce')(p)) * 260; return { o: clamp(p * 8), tf: `translateY(${y}px)` }; });
  def('elastic', 'stretches like rubber and settles', p => { const k = L.ease.get('outElastic')(p); return { o: clamp(p * 6), tf: `scale(${lerp(.2, 1, k)}, ${lerp(1.8, 1, k)})` }; });
  def('trackIn', 'letter-spacing collapses (whole line)', p => ({ o: eo(p), extra: { letterSpacing: `${(1 - e(p)) * .5}em` } }), { by: 'lines' });
  def('weightMorph', 'variable weight 100→900 (needs variable font)', p => ({ o: clamp(p * 5), extra: { fontVariationSettings: `'wght' ${Math.round(lerp(100, 900, e(p)))}` } }));
  def('widthMorph', 'variable width 62→125 (Archivo)', p => ({ o: clamp(p * 5), extra: { fontVariationSettings: `'wdth' ${Math.round(lerp(62, 125, e(p)))}, 'wght' 800` } }));
  def('scramble', 'decodes random glyphs into the text', (p, c) => ({ o: 1, text: L.scramble(c.txt, clamp(p * 1.1), c.i * 17 + c.seed) }), { by: 'chars-or-lines' });
  def('typewriter', 'types in with a caret (use by:chars, stagger .04)', p => ({ o: p > 0 ? 1 : 0 }));
  def('blurFocus', 'sharpens from heavy blur + scale (hero)', p => ({ o: eo(p), filter: `blur(${(1 - e(p)) * 30}px)`, tf: `scale(${1.25 - .25 * e(p)})` }));
  def('wave', 'letters rise in a wave and settle', (p, c) => ({ o: clamp(p * 6), tf: `translateY(${(1 - e(p)) * 60 + Math.sin(p * Math.PI) * -22}px)` }));
  def('stretchIn', 'scaleX from 0 (bars, underlines, tags)', p => ({ o: 1, tf: `scaleX(${e(p)})`, origin: '0 50%' }));
  def('maskWipe', 'clip-path wipe left→right', p => ({ o: 1, clip: `inset(0 ${(1 - e(p)) * 100}% 0 0)` }));
  def('maskWipeUp', 'clip-path wipe bottom→top', p => ({ o: 1, clip: `inset(${(1 - e(p)) * 100}% 0 0 0)` }));
  def('splitReveal', 'two halves slide apart to reveal', p => ({ o: 1, clip: `inset(${(1 - e(p)) * 50}% 0 ${(1 - e(p)) * 50}% 0)` }));
  def('glitchIn', 'jittery RGB-split glitch in (digital)', (p, c) => { const r = L.rng(c.i * 31 + Math.floor(p * 14) + c.seed), g = (1 - p); return { o: p > 0 ? (r() > g * .8 ? 1 : .0) : 0, tf: `translate(${(r() - .5) * 40 * g}px, ${(r() - .5) * 10 * g}px) skewX(${(r() - .5) * 20 * g}deg)`, shadow: `${(r() - .5) * 20 * g}px 0 rgba(255,0,80,.8), ${(r() - .5) * -20 * g}px 0 rgba(0,220,255,.8)` }; });
  def('zoomThrough', 'starts huge and pulls to place (camera through the letter)', p => ({ o: clamp(p * 5), tf: `scale(${lerp(9, 1, ep(p))})`, filter: `blur(${(1 - ep(p)) * 10}px)` }));
  def('swing', 'hangs and swings into place (words)', p => ({ o: clamp(p * 6), tf: `rotate(${(1 - e(p)) * -25 * Math.cos(p * 9)}deg)`, origin: '50% -20%' }));
  def('cascadeSides', 'alternate words enter from left/right', (p, c) => ({ o: clamp(p * 5), tf: `translateX(${(1 - e(p)) * (c.i % 2 ? 420 : -420)}px)` }));
  def('inkFill', 'outline draws, then fills (stroke→fill)', (p, c) => ({ o: 1, extra: { color: p < .5 ? 'transparent' : '', WebkitTextStroke: `${Math.max(0, 2.5 - Math.max(0, p - .5) * 5)}px currentColor`, opacity: clamp(p * 4) } }));
  def('shuffle', 'letters swap positions into place', (p, c) => { const r = L.rng(c.i * 7 + c.seed); return { o: clamp(p * 6), tf: `translate(${(r() - .5) * 300 * (1 - e(p))}px, ${(r() - .5) * 200 * (1 - e(p))}px) rotate(${(r() - .5) * 180 * (1 - e(p))}deg)` }; });
  def('stampDown', 'stamps down hard with a tiny rebound', p => { const k = L.ease.get('outBack')(p); return { o: clamp(p * 10), tf: `scale(${lerp(1.9, 1, k)}) rotate(${(1 - k) * -6}deg)` }; });
  Type.styles = S; Type.meta = meta; Type.list = () => Object.keys(S);

  /* ───────── make / apply ───────── */
  Type.make = (el, text, o = {}) => { if (text != null) el.textContent = text; const by = o.by || 'chars'; const pieces = L.split(el, by);
    if (o.mask || (by !== 'chars' && o.mask !== false && 0)) pieces.forEach(sp => { const w = document.createElement('span'); w.style.cssText = 'display:inline-block;overflow:hidden;vertical-align:bottom;padding:.12em 0 .18em;margin:-.12em 0 -.18em'; sp.parentNode.insertBefore(w, sp); w.appendChild(sp); sp._mask = w; });
    pieces.forEach(sp => { sp._txt = sp.textContent; }); return { el, pieces, by, text: el.textContent }; };
  const order = (i, n, mode, seed) => mode === 'reverse' ? n - 1 - i : mode === 'center' ? Math.abs(i - (n - 1) / 2) * 2 : mode === 'edges' ? ((n - 1) / 2 - Math.abs(i - (n - 1) / 2)) * 2 : mode === 'random' ? Math.floor(L.hash(i * 13 + seed) * n) : i;
  Type.apply = (T, style, t, o = {}) => { const fn = S[style]; if (!fn) throw new Error('Type: unknown style ' + style + '. Known: ' + Object.keys(S).join(', ')); const P = T.pieces, n = P.length, t0 = o.t0 || 0, dur = o.dur || .7, st = o.stagger == null ? .035 : o.stagger, seed = o.seed || 1; const ex = o.exit;
    P.forEach((sp, i) => { const idx = order(i, n, o.order || 'forward', seed), ts = t0 + idx * st; let p = clamp((t - ts) / dur), k = 1; let fnx = fn;
      if (ex) { const te = ex.t1 + order(i, n, ex.order || o.order || 'forward', seed) * (ex.stagger == null ? st : ex.stagger), q = clamp((t - te) / (ex.dur || .4)); if (q > 0) { fnx = S[ex.style || 'fade']; p = 1 - q; } }
      const r = fnx(p, { i, n, k: n > 1 ? i / (n - 1) : 0, seed, txt: sp._txt, el: sp });
      const hide = (t < ts) ? true : false; sp.style.opacity = hide ? 0 : (r.o == null ? 1 : r.o); sp.style.transform = r.tf || ''; sp.style.transformOrigin = r.origin || ''; sp.style.filter = r.filter || ''; sp.style.clipPath = r.clip || ''; sp.style.textShadow = r.shadow || '';
      if (r.text != null) sp.textContent = p >= 1 ? sp._txt : r.text; else if (sp.textContent !== sp._txt && p >= 1) sp.textContent = sp._txt;
      if (r.extra) for (const kx in r.extra) sp.style[kx] = r.extra[kx]; });
  };

  /* ───────── fit ───────── */
  Type.fit = (el, bw, bh, o = {}) => { let lo = o.min || 20, hi = o.max || 900; el.style.whiteSpace = o.nowrap ? 'nowrap' : 'normal'; el.style.width = bw + 'px'; for (let k = 0; k < 18; k++) { const m = (lo + hi) / 2; el.style.fontSize = m + 'px'; if (el.scrollWidth <= bw + 1 && el.scrollHeight <= bh + 1) lo = m; else hi = m; } el.style.fontSize = lo + 'px'; return lo; };

  /* ───────── captions (word-level, TikTok/Reels style) ───────── */
  // words: [{w,t,e}] seconds. group: words per screen. style: 'pop' (active word scales), 'highlight' (active word gets a bg box), 'karaoke' (colour fill), 'stack' (one word at a time, huge)
  Type.captions = (el, words, o = {}) => { const g = o.group || 3, groups = []; for (let i = 0; i < words.length; i += g) groups.push(words.slice(i, i + g)); const st = o.style || 'pop', act = o.active || '#ffd400', dim = o.dim == null ? .6 : o.dim; el.style.textAlign = 'center';
    return { el, groups, at(t) { let gi = -1; groups.forEach((gr, i) => { if (t >= gr[0].t - .05) gi = i; }); const gr = groups[gi]; if (!gr || t > gr[gr.length - 1].e + (o.hold == null ? .6 : o.hold)) { el.innerHTML = ''; el.style.opacity = 0; return; } el.style.opacity = 1; const enterK = L.spring(t - gr[0].t, 22, .75);
        if (st === 'stack') { const cur = gr.filter(w => t >= w.t).pop() || gr[0]; el.innerHTML = `<span style="display:inline-block;transform:scale(${.8 + .2 * L.spring(t - cur.t, 24, .6)})">${cur.w}</span>`; return; }
        el.innerHTML = gr.map(w => { const on = t >= w.t && t < w.e + .02, past = t >= w.e; const sc = st === 'pop' && on ? 1 + .18 * L.spring(t - w.t, 26, .5) : 1; const style = st === 'highlight' && on ? `background:${act};color:${o.onActive || '#111'};border-radius:.18em;padding:0 .18em;` : st === 'karaoke' ? `color:${(on || past) ? act : 'inherit'};opacity:${(on || past) ? 1 : dim};` : `color:${on ? act : 'inherit'};opacity:${on || past ? 1 : dim};`; return `<span style="display:inline-block;margin:0 .12em;transform:scale(${sc});${style}">${w.w}</span>`; }).join(''); el.style.transform = `translateY(${(1 - enterK) * 14}px)`; } }; };

  /* ───────── misc ───────── */
  Type.marquee = (el, t, o = {}) => { const sp = o.speed || 160, dir = o.dir == null ? -1 : o.dir, w = el.firstElementChild ? el.firstElementChild.offsetWidth : el.scrollWidth / 2; const x = ((t * sp * dir) % (w || 1)); el.style.transform = `translateX(${x - (dir < 0 ? 0 : w)}px)`; };   // el contains the same run twice
  Type.underline = (path, p) => L.drawStroke(path, E('outCubic')(clamp(p)));
  Type.highlight = (span, p, color = '#ffe14a') => { span.style.backgroundImage = `linear-gradient(${color},${color})`; span.style.backgroundRepeat = 'no-repeat'; span.style.backgroundPosition = '0 85%'; span.style.backgroundSize = `${E('outCubic')(clamp(p)) * 100}% 40%`; };
  root.Type = Type;
})(typeof window !== 'undefined' ? window : globalThis);
