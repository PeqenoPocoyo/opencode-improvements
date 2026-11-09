/* collage.js - Collage: procedural paper-cutout / scrapbook / stop-motion collage for Canvas 2D. NO images needed. Needs lab.js first (Lab.rng, Lab.noise, Lab.ev).
 *
 *   Collage.draw(ctx, t, pieces, opts)      <- data-driven: a list of pieces with timing + animation (the easy way)
 *   Collage.piece(ctx, p, t)                one cutout (shape, fill, edge, shadow, rotation, boil)
 *   Collage.tape / staple / pin / stamp / stain / crease / stitch / ransom / paperBg   decorations
 *   Collage.register(pieces)                registers Lab.ev events for every arrival/exit (sound: paper-slap, tape, stamp, whoosh, pop)
 *
 * piece = { shape:'rect'|'circle'|'blob'|'star'|'arrow'|'strip'|'tag'|'torn'|'poly', pts:[[x,y]...] (poly, -1..1 units), x,y (centre), w,h, rot (deg),
 *           fill:'#hex' | {paper:'#hex'} | {pattern:'grid'|'dots'|'stripes'|'halftone'|'news'|'kraft'|'lined', a:'#hex', b:'#hex', size:n} | {art:'flowField', pal:[...], seed:n}  (art needs art.js)
 *           edge:'torn'|'scissors'|'clean'  rough:px  rim:'#f3eee3' (the white torn-paper fibre edge)  shadow:0..1  z (draw order)
 *           text:'WORD', font:'700 80px "Anton"', ink:'#111', tx,ty (text offset)  label for events
 *           t0 (arrival time), dur (arrival length, .3), anim:'slap'|'slideL'|'slideR'|'slideU'|'slideD'|'pop'|'drop'|'peel'|'none',  t1 (exit time, optional), out:'fade'|'slideL'|...,
 *           boil:true|false (stop-motion jitter, default true)  seed:n  tape:'tl'|'tr'|'both'|'top' (adds tape)  stamp:'TEXT' (stamps over it)  deco:[fn(ctx,t,p)] }
 * opts = { boilFps:8 (variants cycle 3 frames: dur*boilFps must be a multiple of 3 for an exact loop), paper:'#efe6d2' (background), grain:true, light:[-1,-1] (light direction: shadow falls opposite) }
 *
 * Everything is a pure function of (pieces, t, opts). Geometry is cached by key (deterministic).
 */
(function (root) {
  'use strict';
  const L = root.Lab, TAU = Math.PI * 2, C = {};
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const mod = (a, n) => ((a % n) + n) % n;
  const hexRGB = h => { h = String(h).replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join(''); return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16)); };
  const rgba = (h, a) => { const [r, g, b] = hexRGB(h); return `rgba(${r},${g},${b},${a})`; };
  const shade = (h, k) => { const [r, g, b] = hexRGB(h); const f = v => Math.round(clamp(v * k, 0, 255)); return `rgb(${f(r)},${f(g)},${f(b)})`; };
  const easeOutCubic = x => 1 - Math.pow(1 - x, 3);
  const easeOutBack = (x, s = 1.9) => 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2);
  const easeInCubic = x => x * x * x;
  const rngCache = {}; const R = s => rngCache[s] || (rngCache[s] = L.noise(s * 131 + 7));
  const mk = (w, h) => { const c = document.createElement('canvas'); c.width = Math.max(1, Math.ceil(w)); c.height = Math.max(1, Math.ceil(h)); return c; };

  /* ---------- paper tile (neutral fibrous noise, cached) ---------- */
  const tiles = {};
  function paperTile(seed = 1, size = 256) {
    const key = seed + ':' + size; if (tiles[key]) return tiles[key];
    const c = mk(size, size), x = c.getContext('2d'), r = L.rng(seed * 7 + 3);
    const id = x.createImageData(size, size), d = id.data, n = R(seed);
    for (let j = 0; j < size; j++) for (let i = 0; i < size; i++) {
      // tileable noise: sample on a torus
      const a = i / size * TAU, b = j / size * TAU, rr = 1.2;
      const v = n.n2(Math.cos(a) * rr * 3 + 20, Math.sin(a) * rr * 3 + Math.cos(b) * rr * 3) * .16 + n.n2(Math.cos(a) * 14, Math.sin(b) * 14 + 5) * .22 + (r() - .5) * .28;
      const g = 232 + v * 38; const k = (j * size + i) * 4; d[k] = d[k + 1] = d[k + 2] = clamp(g, 150, 255); d[k + 3] = 255;
    }
    x.putImageData(id, 0, 0);
    x.globalAlpha = .16; x.lineWidth = 1;
    for (let k = 0; k < size * 1.2; k++) { // fibres
      const px = r() * size, py = r() * size, an = r() * TAU, ln = 4 + r() * 14;
      x.strokeStyle = r() < .5 ? '#fff' : '#9a8f78'; x.beginPath(); x.moveTo(px, py); x.quadraticCurveTo(px + Math.cos(an + .7) * ln * .5, py + Math.sin(an + .7) * ln * .5, px + Math.cos(an) * ln, py + Math.sin(an) * ln); x.stroke();
    }
    return tiles[key] = c;
  }
  C.paperTile = paperTile;

  /* full-frame paper background (desk / paper / kraft / graph) */
  C.paperBg = function (ctx, o = {}) {
    const w = o.w || ctx.canvas.width, h = o.h || ctx.canvas.height, base = o.color || '#efe6d2', k = o.grain == null ? .55 : o.grain;
    ctx.save(); ctx.fillStyle = base; ctx.fillRect(o.x || 0, o.y || 0, w, h);
    ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = k; ctx.fillStyle = ctx.createPattern(paperTile(o.seed || 1), 'repeat'); ctx.fillRect(o.x || 0, o.y || 0, w, h);
    ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
    if (o.vignette !== 0) { const g = ctx.createRadialGradient(w / 2, h / 2, Math.min(w, h) * .35, w / 2, h / 2, Math.max(w, h) * .75); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(40,25,10,${o.vignette == null ? .22 : o.vignette})`); ctx.fillStyle = g; ctx.fillRect(o.x || 0, o.y || 0, w, h); }
    ctx.restore();
  };

  /* ---------- outline points (unit shapes scaled to w,h; centre origin) ---------- */
  function outline(p, N = 96) {
    const w = p.w, h = p.h, s = p.shape || 'rect', pts = [], hw = w / 2, hh = h / 2, seed = p.seed || 1, n = R(seed + 50);
    const lerpEdge = (a, b, k) => { for (let i = 0; i < k; i++) pts.push([a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k]); };
    const poly = (v, per) => { for (let i = 0; i < v.length; i++) lerpEdge(v[i], v[(i + 1) % v.length], per); };
    if (s === 'circle') for (let i = 0; i < N; i++) { const a = i / N * TAU; pts.push([Math.cos(a) * hw, Math.sin(a) * hh]); }
    else if (s === 'blob') for (let i = 0; i < N; i++) { const a = i / N * TAU, k = 1 + .18 * n.n2(Math.cos(a) * 1.3 + 3, Math.sin(a) * 1.3) + .08 * n.n2(Math.cos(a * 3) + 9, Math.sin(a * 3)); pts.push([Math.cos(a) * hw * k, Math.sin(a) * hh * k]); }
    else if (s === 'star') { const m = p.points || 5; for (let i = 0; i < m * 2; i++) { const a = i / (m * 2) * TAU - Math.PI / 2, r = i % 2 ? .45 : 1; pts.push([Math.cos(a) * hw * r, Math.sin(a) * hh * r]); } poly(pts.splice(0), 8); }
    else if (s === 'arrow') poly([[-hw, -hh * .28], [hw * .25, -hh * .28], [hw * .25, -hh], [hw, 0], [hw * .25, hh], [hw * .25, hh * .28], [-hw, hh * .28]], 10);
    else if (s === 'tag') poly([[-hw, -hh], [hw * .6, -hh], [hw, 0], [hw * .6, hh], [-hw, hh]], 14);
    else if (s === 'strip') poly([[-hw, -hh], [hw, -hh * .9], [hw, hh * .9], [-hw, hh]], 20);
    else if (s === 'poly' && p.pts) poly(p.pts.map(q => [q[0] * hw, q[1] * hh]), 12);
    else if (s === 'torn') poly([[-hw, -hh], [hw, -hh * .96], [hw * .98, hh], [-hw * .97, hh * .95]], 24);
    else poly([[-hw, -hh], [hw, -hh], [hw, hh], [-hw, hh]], 24);
    return pts;
  }
  /* edge treatment: displace along the normal (torn), or keep few vertices (scissors) */
  function edge(pts, style, rough, seed, variant) {
    const n = R(seed + 9 + variant * 17), out = [], N = pts.length;
    if (style === 'clean') return pts;
    if (style === 'scissors') { const k = Math.max(2, Math.round(N / 22)); for (let i = 0; i < N; i += k) { const q = pts[i], j = (i * 7) % 5 - 2; out.push([q[0] + n.n2(i * .31, 1) * rough * .35, q[1] + n.n2(i * .31, 7) * rough * .35 + j * 0]); } return out; }
    for (let i = 0; i < N; i++) {
      const a = pts[(i - 1 + N) % N], b = pts[(i + 1) % N], q = pts[i]; let nx = b[1] - a[1], ny = -(b[0] - a[0]); const l = Math.hypot(nx, ny) || 1; nx /= l; ny /= l;
      const d = n.n2(i * .45, 3 + variant) * rough + n.n2(i * 1.7, 11 + variant) * rough * .45 + (R(seed + 200 + variant).n2(i * 5, 1)) * rough * .18;
      out.push([q[0] + nx * d, q[1] + ny * d]);
    }
    return out;
  }
  function trace(ctx, pts, smooth) {
    ctx.beginPath();
    if (!smooth) { ctx.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]); ctx.closePath(); return; }
    const N = pts.length, m = i => pts[(i + N) % N]; ctx.moveTo((m(0)[0] + m(1)[0]) / 2, (m(0)[1] + m(1)[1]) / 2);
    for (let i = 1; i <= N; i++) { const a = m(i), b = m(i + 1); ctx.quadraticCurveTo(a[0], a[1], (a[0] + b[0]) / 2, (a[1] + b[1]) / 2); }
    ctx.closePath();
  }

  /* ---------- fills ---------- */
  function fillShape(ctx, p, t, bbox) {
    const f = p.fill == null ? '#e9e2cf' : p.fill, w = p.w, h = p.h, hw = w / 2, hh = h / 2;
    if (typeof f === 'string') { ctx.fillStyle = f; ctx.fill(); ctx.save(); ctx.clip(); ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = p.grain == null ? .42 : p.grain; ctx.fillStyle = ctx.createPattern(paperTile((p.seed || 1) % 5 + 1), 'repeat'); ctx.fillRect(-hw - 20, -hh - 20, w + 40, h + 40); ctx.restore(); return; }
    if (f.paper) return fillShape(ctx, Object.assign({}, p, { fill: f.paper }), t);
    ctx.fillStyle = f.a || '#e9e2cf'; ctx.fill(); ctx.save(); ctx.clip();
    const pat = f.pattern, A = f.a || '#e9e2cf', B = f.b || '#222', sz = f.size || 28, r = L.rng((p.seed || 1) * 31 + 5);
    if (pat === 'grid') { ctx.strokeStyle = rgba(B, .5); ctx.lineWidth = 1.4; ctx.beginPath(); for (let x = -hw; x <= hw; x += sz) { ctx.moveTo(x, -hh); ctx.lineTo(x, hh); } for (let y = -hh; y <= hh; y += sz) { ctx.moveTo(-hw, y); ctx.lineTo(hw, y); } ctx.stroke(); }
    else if (pat === 'lined') { ctx.strokeStyle = rgba(B, .45); ctx.lineWidth = 1.6; ctx.beginPath(); for (let y = -hh + sz; y <= hh; y += sz) { ctx.moveTo(-hw, y); ctx.lineTo(hw, y); } ctx.stroke(); ctx.strokeStyle = 'rgba(220,60,60,.5)'; ctx.beginPath(); ctx.moveTo(-hw + sz * 1.6, -hh); ctx.lineTo(-hw + sz * 1.6, hh); ctx.stroke(); }
    else if (pat === 'dots') { ctx.fillStyle = B; for (let y = -hh; y <= hh + sz; y += sz) for (let x = -hw + ((Math.round((y + hh) / sz) % 2) ? sz / 2 : 0); x <= hw + sz; x += sz) { ctx.beginPath(); ctx.arc(x, y, sz * .2, 0, TAU); ctx.fill(); } }
    else if (pat === 'stripes') { ctx.fillStyle = B; const m = Math.hypot(w, h); ctx.rotate(f.angle == null ? -.5 : f.angle); for (let x = -m; x < m; x += sz * 2) ctx.fillRect(x, -m, sz, m * 2); ctx.rotate(-(f.angle == null ? -.5 : f.angle)); }
    else if (pat === 'halftone' || pat === 'news') { // dots grow along a diagonal gradient; newsprint adds text-like lines
      ctx.fillStyle = B; const s = sz * .7; for (let y = -hh; y <= hh + s; y += s) for (let x = -hw; x <= hw + s; x += s) { const u = clamp(((x + hw) / w + (y + hh) / h) / 2 + (f.bias || 0)); const rad = s * .62 * Math.sqrt(u) * (f.invert ? 1 - u : 1); if (rad > .4) { ctx.beginPath(); ctx.arc(x + (Math.round((y + hh) / s) % 2 ? s / 2 : 0), y, rad, 0, TAU); ctx.fill(); } }
      if (pat === 'news') { ctx.fillStyle = rgba(B, .55); for (let y = -hh + 14; y < hh - 8; y += 11) { let x = -hw + 12; while (x < hw - 12) { const wd = 8 + r() * 46; if (r() > .12) ctx.fillRect(x, y, Math.min(wd, hw - 12 - x), 4); x += wd + 6; } } }
    }
    else if (pat === 'kraft') { ctx.fillStyle = '#b98a55'; ctx.fillRect(-hw, -hh, w, h); ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = .7; ctx.fillStyle = ctx.createPattern(paperTile(3), 'repeat'); ctx.fillRect(-hw, -hh, w, h); }
    else if (f.art && root.Art) { ctx.translate(-hw, -hh); root.Art.draw(ctx, f.art, t, Object.assign({ x: 0, y: 0, w, h, pal: f.pal, seed: f.seed || p.seed || 1, loop: f.loop || 0 }, f.opts || {})); ctx.translate(hw, hh); }
    ctx.restore(); ctx.save(); ctx.clip(); ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = .3; ctx.fillStyle = ctx.createPattern(paperTile(2), 'repeat'); ctx.fillRect(-hw - 20, -hh - 20, w + 40, h + 40); ctx.restore();
  }

  /* ---------- single piece ---------- */
  const geo = {};
  C.piece = function (ctx, p, t, o = {}) {
    const boil = p.boil !== false, bfps = o.boilFps || 8, variant = boil ? mod(Math.floor(t * bfps), 3) : 0, seed = p.seed || 1;
    const key = [p.shape, p.w, p.h, p.edge, p.rough, seed, variant, (p.pts || []).length].join('|');
    let g = geo[key]; if (!g) {
      const style = p.edge || 'torn', rough = p.rough == null ? Math.max(2.5, Math.min(p.w, p.h) * .018) : p.rough, base = outline(p), a = edge(base, style, rough, seed, variant);
      const rim = style === 'torn' ? edge(base, 'torn', rough * 1.4, seed + 77, variant).map(q => { const l = Math.hypot(q[0], q[1]) || 1; const k = (l + (p.rimW == null ? 3.2 : p.rimW)) / l; return [q[0] * k, q[1] * k]; }) : null;
      g = geo[key] = { a, rim, smooth: style !== 'scissors' && style !== 'clean' ? true : (p.shape === 'circle' || p.shape === 'blob') };
    }
    // dynamic jitter of position/rotation (stop-motion)
    const jit = boil ? (p.jitter == null ? 1.6 : p.jitter) : 0, jx = jit * R(seed).n2(Math.floor(t * bfps) * 1.7, 4), jy = jit * R(seed).n2(Math.floor(t * bfps) * 1.7, 9), jr = jit * .002 * R(seed).n2(Math.floor(t * bfps) * 1.7, 14);
    const A = arrival(p, t); if (!A.visible) return;
    const lx = (o.light || [-1, -1])[0], ly = (o.light || [-1, -1])[1];
    ctx.save();
    ctx.globalAlpha *= A.alpha; ctx.translate(p.x + A.dx + jx, p.y + A.dy + jy); ctx.rotate((p.rot || 0) * Math.PI / 180 + A.dr + jr); ctx.scale(A.s * (p.flip ? -1 : 1), A.s);
    const sh = (p.shadow == null ? .5 : p.shadow) * A.shadow, lift = A.lift;
    // shadow: offset opposite to the light, softer and longer when the paper is lifted
    if (sh > 0) { ctx.save(); ctx.shadowColor = `rgba(25,15,5,${.42 * sh})`; ctx.shadowBlur = 6 + lift * 22; ctx.shadowOffsetX = -lx * (4 + lift * 26); ctx.shadowOffsetY = -ly * (5 + lift * 30); ctx.fillStyle = '#000'; trace(ctx, g.rim || g.a, g.smooth); ctx.fill(); ctx.restore(); }
    if (g.rim) { ctx.fillStyle = p.rim || '#f3eee3'; trace(ctx, g.rim, true); ctx.fill(); }
    trace(ctx, g.a, g.smooth); fillShape(ctx, p, t);
    // subtle edge light (top-left) + inner darkening for thickness
    ctx.save(); trace(ctx, g.a, g.smooth); ctx.clip(); ctx.lineWidth = 3; ctx.strokeStyle = 'rgba(255,255,255,.18)'; ctx.translate(-lx * 1.2, -ly * 1.2); trace(ctx, g.a, g.smooth); ctx.stroke(); ctx.restore();
    if (p.crease) C.crease(ctx, -p.w / 2, p.crease * p.h - p.h / 2 + 0, p.w / 2, p.crease * p.h - p.h / 2 + 3, seed);
    if (p.text) { ctx.fillStyle = p.ink || '#161310'; ctx.font = p.font || '800 64px "Anton", Impact, sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; if (p.tracking && 'letterSpacing' in ctx) ctx.letterSpacing = p.tracking; const lines = String(p.text).split('\n'), lh = p.lineH || parseFloat((p.font || '64px').match(/(\d+)px/)[1]) * 1.05; lines.forEach((s, i) => ctx.fillText(s, (p.tx || 0), (p.ty || 0) + (i - (lines.length - 1) / 2) * lh)); if ('letterSpacing' in ctx) ctx.letterSpacing = '0px'; }
    if (p.deco) p.deco.forEach(fn => fn(ctx, t, p));
    if (p.tape) { const w = p.w, h = p.h, tw = p.tapeW || Math.min(w, h) * .45, c = p.tapeColor; if (p.tape === 'tl' || p.tape === 'both') C.tape(ctx, -w / 2 + 12, -h / 2 + 8, tw, tw * .34, -35, c, seed); if (p.tape === 'tr' || p.tape === 'both') C.tape(ctx, w / 2 - 12, -h / 2 + 8, tw, tw * .34, 35, c, seed + 1); if (p.tape === 'top') C.tape(ctx, 0, -h / 2 + 4, tw * 1.1, tw * .34, (R(seed).n2(2, 2)) * 6, c, seed); }
    if (p.stamp) C.stamp(ctx, p.stamp, p.stampX || 0, p.stampY || p.h * .25, { size: p.stampSize || Math.min(p.w, p.h) * .22, rot: p.stampRot == null ? -10 : p.stampRot, color: p.stampColor || '#b02a1e', seed });
    ctx.restore();
  };

  /* ---------- arrival/exit animation (pure function of t) ---------- */
  function arrival(p, t) {
    const t0 = p.t0 || 0, dur = p.dur || .3, a = p.anim || 'slap', t1 = p.t1;
    const o = { visible: true, alpha: 1, dx: 0, dy: 0, dr: 0, s: 1, shadow: 1, lift: 0 };
    if (t < t0 || (t1 != null && t >= t1 + (p.outDur || .25))) { o.visible = false; return o; }
    const k = clamp((t - t0) / dur), W = (p.slide || 900);
    if (a === 'slap') { const e = easeOutCubic(k); o.s = 1 + .28 * (1 - e); o.alpha = clamp(k * 5); o.lift = 1 - easeInCubic(k); o.shadow = .3 + .7 * k; o.dr = (1 - e) * .08 * (p.spin || 1); if (k >= 1) { const q = clamp((t - t0 - dur) / .12); o.s = 1 - .02 * Math.sin(q * Math.PI); } }
    else if (a === 'pop') { const e = easeOutBack(k, 2.2); o.s = Math.max(.001, e); o.alpha = clamp(k * 6); o.lift = 1 - k; }
    else if (a === 'drop') { const e = easeOutCubic(k), bounce = k < 1 ? 0 : 0; o.dy = -(1 - e) * (p.fromY || 700); o.lift = 1 - e; o.dr = (1 - e) * -.12; o.shadow = .4 + .6 * e; if (k >= 1) { const q = clamp((t - t0 - dur) / .22); o.dy = -Math.sin(q * Math.PI) * 14 * (1 - q); } }
    else if (a === 'slideL') { o.dx = -(1 - easeOutCubic(k)) * W; o.lift = 1 - k * .8; }
    else if (a === 'slideR') { o.dx = (1 - easeOutCubic(k)) * W; o.lift = 1 - k * .8; }
    else if (a === 'slideU') { o.dy = -(1 - easeOutCubic(k)) * W; o.lift = 1 - k * .8; }
    else if (a === 'slideD') { o.dy = (1 - easeOutCubic(k)) * W; o.lift = 1 - k * .8; }
    else if (a === 'peel') { const e = easeOutCubic(k); o.s = .85 + .15 * e; o.dr = (1 - e) * .35; o.dy = (1 - e) * 120; o.alpha = clamp(k * 4); o.lift = 1 - e; }
    if (t1 != null && t >= t1) { const q = clamp((t - t1) / (p.outDur || .25)), e = easeInCubic(q), out = p.out || 'fade'; if (out === 'fade') o.alpha *= 1 - q; else if (out === 'slideL') o.dx -= e * W; else if (out === 'slideR') o.dx += e * W; else if (out === 'slideU') o.dy -= e * W; else if (out === 'slideD') o.dy += e * W; else if (out === 'shrink') { o.s *= 1 - e; o.alpha *= 1 - q * .6; } o.lift = Math.max(o.lift, q); }
    return o;
  }
  C.arrival = arrival;

  /* ---------- data-driven scene ---------- */
  C.draw = function (ctx, t, pieces, opts = {}) {
    const bgc = opts.paper === false ? null : (opts.paper || '#efe6d2');
    if (bgc) C.paperBg(ctx, { color: bgc, grain: opts.bgGrain, vignette: opts.vignette, seed: opts.seed });
    const sorted = pieces.map((p, i) => [p, i]).sort((A, B) => ((A[0].z || 0) - (B[0].z || 0)) || A[1] - B[1]);
    for (const [p] of sorted) C.piece(ctx, p, t, opts);
  };
  /* register sound events for every arrival/exit (call once at build time) */
  C.register = function (pieces, map = {}) {
    const defaults = { slap: 'paper-slap', pop: 'pop', drop: 'paper-slap', peel: 'paper-rip', slideL: 'whoosh', slideR: 'whoosh', slideU: 'whoosh', slideD: 'whoosh' };
    pieces.forEach(p => {
      if (p.silent) return; const a = p.anim || 'slap'; if (a === 'none' && !p.t0) return;
      const type = map[a] || defaults[a] || 'paper-slap', land = a.startsWith('slide') ? (p.t0 || 0) : (p.t0 || 0) + (p.dur || .3);
      L.ev(land, type, { intensity: p.hit == null ? clamp((Math.min(p.w, p.h) / 700) + .35, .35, 1) : p.hit, label: p.label || (p.text || p.shape || 'piece'), dur: a.startsWith('slide') ? (p.dur || .3) : undefined });
      if (p.tape) L.ev(land + .12, 'tape', { intensity: .5 });
      if (p.stamp) L.ev(land + .3, 'stamp', { intensity: .7 });
    });
  };

  /* ---------- decorations ---------- */
  C.tape = function (ctx, x, y, w, h, rot, color, seed = 1) {
    const r = L.rng(seed * 5 + 1); ctx.save(); ctx.translate(x, y); ctx.rotate(rot * Math.PI / 180);
    ctx.fillStyle = color || 'rgba(236,222,160,.78)'; ctx.shadowColor = 'rgba(0,0,0,.18)'; ctx.shadowBlur = 4; ctx.shadowOffsetY = 2;
    ctx.beginPath(); const zig = 5; ctx.moveTo(-w / 2, -h / 2); for (let i = 0; i <= zig; i++) ctx.lineTo(-w / 2 + (i % 2 ? 4 : 0), -h / 2 + h * i / zig); ctx.lineTo(w / 2, h / 2); for (let i = zig; i >= 0; i--) ctx.lineTo(w / 2 - (i % 2 ? 4 : 0), -h / 2 + h * i / zig); ctx.closePath(); ctx.fill();
    ctx.shadowColor = 'transparent'; ctx.globalAlpha = .22; ctx.fillStyle = '#fff'; ctx.fillRect(-w / 2 + 6, -h / 2 + 3, w - 12, h * .22); ctx.restore();
  };
  C.staple = function (ctx, x, y, rot = 0, len = 34) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot * Math.PI / 180); ctx.strokeStyle = '#8b8f95'; ctx.lineWidth = 4; ctx.lineCap = 'round'; ctx.shadowColor = 'rgba(0,0,0,.35)'; ctx.shadowBlur = 3; ctx.shadowOffsetY = 2;
    ctx.beginPath(); ctx.moveTo(-len / 2, 0); ctx.lineTo(len / 2, 0); ctx.stroke(); ctx.shadowColor = 'transparent'; ctx.strokeStyle = '#d9dde2'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(-len / 2 + 2, -1); ctx.lineTo(len / 2 - 2, -1); ctx.stroke(); ctx.restore();
  };
  C.pin = function (ctx, x, y, color = '#d9382c', r = 11) {
    ctx.save(); ctx.translate(x, y); ctx.shadowColor = 'rgba(0,0,0,.4)'; ctx.shadowBlur = 8; ctx.shadowOffsetX = 5; ctx.shadowOffsetY = 7; ctx.fillStyle = color; ctx.beginPath(); ctx.arc(0, 0, r, 0, TAU); ctx.fill(); ctx.shadowColor = 'transparent';
    const g = ctx.createRadialGradient(-r * .35, -r * .4, 1, 0, 0, r); g.addColorStop(0, 'rgba(255,255,255,.85)'); g.addColorStop(.35, 'rgba(255,255,255,.1)'); g.addColorStop(1, 'rgba(0,0,0,.25)'); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, r, 0, TAU); ctx.fill(); ctx.restore();
  };
  C.stain = function (ctx, x, y, r, color = '#7a4a22', seed = 1, alpha = .35) { // coffee ring: irregular ring + faint fill
    const n = R(seed + 300); ctx.save(); ctx.translate(x, y); ctx.globalCompositeOperation = 'multiply'; ctx.fillStyle = rgba(color, alpha * .25); ctx.beginPath();
    for (let i = 0; i <= 72; i++) { const a = i / 72 * TAU, rr = r * (1 + .06 * n.n2(Math.cos(a) * 2, Math.sin(a) * 2)); ctx[i ? 'lineTo' : 'moveTo'](Math.cos(a) * rr, Math.sin(a) * rr); } ctx.fill();
    for (let k = 0; k < 2; k++) { ctx.strokeStyle = rgba(color, alpha * (k ? .5 : 1)); ctx.lineWidth = k ? 2 : 5; ctx.beginPath(); for (let i = 0; i <= 90; i++) { const a = i / 90 * TAU, rr = r * (1.02 + k * .03) * (1 + .07 * n.n2(Math.cos(a) * 2 + k * 5, Math.sin(a) * 2 + 4)); ctx[i ? 'lineTo' : 'moveTo'](Math.cos(a) * rr, Math.sin(a) * rr); } ctx.stroke(); } ctx.restore();
  };
  C.crease = function (ctx, x1, y1, x2, y2, seed = 1) { // fold line: thin dark + thin light
    ctx.save(); ctx.lineWidth = 2; ctx.strokeStyle = 'rgba(40,25,10,.28)'; ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke(); ctx.strokeStyle = 'rgba(255,255,255,.45)'; ctx.beginPath(); ctx.moveTo(x1, y1 + 2.5); ctx.lineTo(x2, y2 + 2.5); ctx.stroke(); ctx.restore();
  };
  C.stitch = function (ctx, pts, o = {}) { // dashed thread along a polyline; o:{color,dash:[12,9],width:3}
    ctx.save(); ctx.strokeStyle = o.color || '#c93b2e'; ctx.lineWidth = o.width || 3; ctx.lineCap = 'round'; ctx.setLineDash(o.dash || [12, 9]); ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]); ctx.stroke(); ctx.restore();
  };
  /* ink stamp: text (optionally in a double border), eroded with speckles so it looks pressed */
  C.stamp = function (ctx, text, x, y, o = {}) {
    const size = o.size || 60, seed = o.seed || 1, key = ['st', text, size, o.color, seed, o.border !== false].join('|'); let c = geo[key];
    if (!c) {
      const pad = size * .5, f = `${o.weight || 800} ${size}px ${o.font || '"Alfa Slab One","Anton",Impact,sans-serif'}`, m = mk(10, 10).getContext('2d'); m.font = f; const w = m.measureText(text).width + pad * 2, h = size * 1.5 + pad;
      c = mk(w, h); const x2 = c.getContext('2d'); x2.fillStyle = x2.strokeStyle = o.color || '#b02a1e'; x2.font = f; x2.textAlign = 'center'; x2.textBaseline = 'middle'; x2.fillText(text, w / 2, h / 2 + size * .04);
      if (o.border !== false) { x2.lineWidth = size * .07; x2.strokeRect(size * .12, size * .12, w - size * .24, h - size * .24); x2.lineWidth = size * .025; x2.strokeRect(size * .24, size * .24, w - size * .48, h - size * .48); }
      x2.globalCompositeOperation = 'destination-out'; const r = L.rng(seed * 13 + 2); for (let i = 0; i < w * h / 55; i++) { x2.globalAlpha = .3 + r() * .7; x2.beginPath(); x2.arc(r() * w, r() * h, .5 + r() * (size * .035), 0, TAU); x2.fill(); }
      geo[key] = c;
    }
    ctx.save(); ctx.translate(x, y); ctx.rotate((o.rot || 0) * Math.PI / 180); ctx.globalAlpha *= o.alpha == null ? .88 : o.alpha; ctx.globalCompositeOperation = 'multiply'; ctx.drawImage(c, -c.width / 2, -c.height / 2); ctx.restore();
  };
  /* ransom-note lettering: every character on its own paper chip with its own colour/font/rotation (deterministic per char index) */
  C.ransom = function (ctx, text, x, y, o = {}) {
    const size = o.size || 90, seed = o.seed || 1, r = L.rng(seed * 17 + 3), fonts = o.fonts || ['"Anton"', '"DM Serif Display"', '"Alfa Slab One"', '"Space Mono"', '"Bricolage Grotesque"', '"Permanent Marker"'], cols = o.palette || ['#f4efe2', '#d8362b', '#1b1b1b', '#f2c744', '#2d6cdf', '#f7f3ea'];
    const items = [...String(text)].map((ch, i) => { const f = fonts[Math.floor(r() * fonts.length)], sz = size * (.8 + r() * .5), bg = cols[Math.floor(r() * cols.length)], dark = L.luminance ? L.luminance(bg) < .35 : false; ctx.font = `800 ${sz}px ${f}, Impact, sans-serif`; return { ch, f, sz, bg, ink: dark ? '#f6f1e5' : '#141210', w: ctx.measureText(ch).width + size * .32, rot: (r() - .5) * 14, dy: (r() - .5) * size * .22 }; });
    let tot = items.reduce((a, b) => a + b.w + 4, 0), cx = x - tot / 2; const t = o.t == null ? 0 : o.t, st = o.stagger || 0;
    items.forEach((it, i) => {
      if (it.ch === ' ') { cx += it.w; return; } const k = st ? clamp((t - (o.t0 || 0) - i * st) / .22) : 1; if (k <= 0) { cx += it.w + 4; return; }
      const p = { shape: 'rect', x: cx + it.w / 2, y: y + it.dy + (1 - easeOutCubic(k)) * -60, w: it.w, h: it.sz * 1.2, rot: it.rot, fill: it.bg, edge: o.edge || 'scissors', rough: 3, text: it.ch, font: `800 ${it.sz}px ${it.f}, Impact, sans-serif`, ink: it.ink, seed: seed + i, shadow: .55, boil: o.boil !== false, jitter: 1.1, t0: 0, anim: 'none' };
      ctx.save(); ctx.globalAlpha *= k; C.piece(ctx, p, t, o); ctx.restore(); cx += it.w + 4;
    });
  };

  /* helpers */
  C.stepTime = (t, fps = 8) => Math.floor(t * fps) / fps;      // quantise time for held "on 3s" animation
  C.shade = shade; C.rgba = rgba;
  root.Collage = C;
})(typeof window !== 'undefined' ? window : globalThis);
