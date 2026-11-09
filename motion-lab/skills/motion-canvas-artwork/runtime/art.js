/* art.js - Art: 34 deterministic generative 2D artwork generators for Canvas 2D (no images, no clocks, no Math.random).
 *
 *   Art.draw(ctx, 'flowField', t, { x:0, y:0, w:1080, h:1920, pal:['#0b0b12','#ff4d2e','#ffb02e','#2ee6a6','#fff4e0'], seed:3, loop:6, speed:1 });
 *   Art.list() -> names;  Art.meta[name] -> {mood, use, params};  Art.describe(name)
 *   Art.palette(dnaPalette) -> [bg, ink1, ink2, ink3, hi]   (converts a DNA palette object/array to the 5 slots)
 * Options common to all:  x,y,w,h (rect; default 0,0,ctx.canvas size)  pal (5 colours: 0 = background, 1..3 inks, 4 = highlight)  bg:false (do not paint the background)
 *   seed (different drawing per seed)  loop (seconds; if set, the animation repeats EXACTLY every `loop` s)  speed (animation speed multiplier)  alpha (global opacity)  + per-generator params (see Art.meta)
 * Everything is a pure function of (name, t, options). Needs lab.js (Lab.noise, Lab.rng) loaded first.
 * Cost guide: light = <3 ms (dotGrid, rings, sunburst...), medium = 5-30 ms (flowField, contours, voronoi at default sizes). In a 1080x1920 scene use at most 2 heavy layers.
 */
(function (root) {
  'use strict';
  const L = root.Lab, TAU = Math.PI * 2, G = {}, meta = {};
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), mod = (a, n) => ((a % n) + n) % n;
  const noises = {}; const getNoise = s => noises[s] || (noises[s] = L.noise(s * 977 + 13));
  const hexRGB = h => { h = String(h).replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join(''); return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16)); };
  const rgba = (c, a) => { if (a >= 1) return c; const [r, g, b] = typeof c === 'string' && c[0] === '#' ? hexRGB(c) : [255, 255, 255]; return `rgba(${r},${g},${b},${a})`; };

  function ctxHelpers(o, t) {
    const sp = o.speed == null ? 1 : o.speed, T = t * sp, loop = o.loop || 0;
    const ph = loop > 0 ? TAU * mod(t, loop) / loop : T * .6;          // phase (radians): loops exactly if `loop` given
    const n = getNoise(o.seed || 1), r0 = o.seed || 1;
    const R = loop > 0 ? .9 : 0;
    const H = {
      T, ph, n, loop,
      rng: k => L.rng((r0 * 7919 + (k || 0) * 104729) >>> 0),
      // time-varying noise that loops: walks on a circle in noise space when `loop` is set, else drifts linearly
      ln: (x, y, k = 0) => loop > 0 ? n.n3(x, y, 0) * 0 + n.n2(x + R * Math.cos(ph + k) + 31 * k, y + R * Math.sin(ph + k) + 17 * k) : n.n2(x + T * .12 + 31 * k, y - T * .09 + 17 * k),
      col: i => o.pal[mod(Math.floor(i), o.pal.length - 1) + 1],       // ink i (1..4 cycling over pal[1..4])
      a: (c, al) => rgba(c, al * (o.alpha == null ? 1 : o.alpha)),
      lw: o.weight || Math.max(1, Math.min(o.w, o.h) / 540)             // base line weight scales with canvas
    };
    return H;
  }
  const add = (name, mood, use, params, fn) => { G[name] = fn; meta[name] = { mood, use, params }; };

  /* ───────── LINES & FIELDS ───────── */
  add('flowField', 'organic, silky, generative-art classic', 'Thousands of thin trails following a noise field; hero texture behind type. Scale controls swirl size.', { count: 700, steps: 36, scale: 1.6, step: .012, width: 1 }, (c, t, o, H) => {
    const { w, h } = o, cnt = o.count || 700, steps = o.steps || 36, sc = o.scale || 1.6, st = (o.step || .012) * Math.max(w, h), r = H.rng(1), m = Math.max(w, h);
    c.lineWidth = H.lw * (o.width || 1); c.lineCap = 'round';
    for (let i = 0; i < cnt; i++) {
      let x = r() * w, y = r() * h; const k = i % 4; c.strokeStyle = H.a(H.col(k), .55); c.beginPath(); c.moveTo(x, y);
      for (let s = 0; s < steps; s++) { const a = H.ln(x / m * sc, y / m * sc) * TAU * 1.1; x += Math.cos(a) * st; y += Math.sin(a) * st; c.lineTo(x, y); }
      c.stroke();
    }
  });
  add('contours', 'topographic, scientific, calm', 'Iso-lines of a moving noise field (marching squares). Map/data feel; very clean on dark bg.', { levels: 12, cell: 12, width: 1.4 }, (c, t, o, H) => {
    const { w, h } = o, cs = o.cell || 12, nx = Math.ceil(w / cs) + 1, ny = Math.ceil(h / cs) + 1, m = Math.max(w, h), lv = o.levels || 12, f = new Float32Array(nx * ny);
    for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) f[j * nx + i] = (H.ln(i * cs / m * 2.2, j * cs / m * 2.2) + .75 * .5 * H.ln(i * cs / m * 4.4, j * cs / m * 4.4, 3)) * .5 + .5;
    c.lineWidth = H.lw * (o.width || 1.4); c.lineCap = 'round';
    for (let L_ = 0; L_ < lv; L_++) {
      const th = (L_ + .5) / lv; c.strokeStyle = H.a(H.col(L_ * .5), L_ % 4 === 0 ? .95 : .5); c.beginPath();
      for (let j = 0; j < ny - 1; j++) for (let i = 0; i < nx - 1; i++) {
        const a = f[j * nx + i], b = f[j * nx + i + 1], d = f[(j + 1) * nx + i], e = f[(j + 1) * nx + i + 1], idx = (a > th ? 8 : 0) | (b > th ? 4 : 0) | (e > th ? 2 : 0) | (d > th ? 1 : 0);
        if (idx === 0 || idx === 15) continue; const x = i * cs, y = j * cs, lx = (p, q) => (th - p) / (q - p);
        const T_ = [x + lx(a, b) * cs, y], R_ = [x + cs, y + lx(b, e) * cs], B_ = [x + lx(d, e) * cs, y + cs], L2 = [x, y + lx(a, d) * cs];
        const seg = (p, q) => { c.moveTo(p[0], p[1]); c.lineTo(q[0], q[1]); };
        switch (idx) { case 1: case 14: seg(L2, B_); break; case 2: case 13: seg(B_, R_); break; case 3: case 12: seg(L2, R_); break; case 4: case 11: seg(T_, R_); break; case 5: seg(T_, L2); seg(B_, R_); break; case 6: case 9: seg(T_, B_); break; case 7: case 8: seg(T_, L2); break; case 10: seg(T_, R_); seg(L2, B_); break; }
      }
      c.stroke();
    }
  });
  add('waveLines', 'unknown-pleasures, signal, moody', 'Stacked ridge lines occluding each other (joy-division). Headline sits above or inside the calm band.', { rows: 38, amp: .09, bump: 1 }, (c, t, o, H) => {
    const { w, h } = o, rows = o.rows || 38, amp = (o.amp || .09) * h, bump = o.bump == null ? 1 : o.bump, pad = h * .12, seg = 90;
    for (let r = 0; r < rows; r++) {
      const yb = pad + (h - pad * 1.4) * r / (rows - 1); c.beginPath();
      for (let i = 0; i <= seg; i++) { const x = i / seg * w, nx = i / seg, env = Math.exp(-Math.pow((nx - .5) * 3.2, 2)) * bump + .15; const y = yb - amp * env * (H.ln(nx * 3, r * .09) * .5 + .5 + .4 * H.ln(nx * 9, r * .2 + 4, 2)); i ? c.lineTo(x, y) : c.moveTo(x, y); }
      c.lineTo(w, h); c.lineTo(0, h); c.closePath(); c.fillStyle = o.pal[0]; c.fill(); c.lineWidth = H.lw * 1.6; c.strokeStyle = H.a(H.col(r > rows * .6 ? 1 : 0), .95); c.stroke();
    }
  });
  add('warpGrid', 'tech, spatial, blueprint', 'A square grid bent by noise; looks like a fabric of space. Pair with glow.', { cells: 22, warp: .06 }, (c, t, o, H) => {
    const { w, h } = o, nC = o.cells || 22, cs = Math.max(w, h) / nC, wp = (o.warp || .06) * Math.max(w, h), seg = 40, m = Math.max(w, h);
    const P = (x, y) => [x + wp * H.ln(x / m * 2, y / m * 2), y + wp * H.ln(x / m * 2 + 9, y / m * 2 + 5, 1)];
    c.lineWidth = H.lw * 1.2;
    for (let pass = 0; pass < 2; pass++) for (let k = 0; k <= nC * Math.max(w, h) / Math.min(w, h) + 1; k++) { c.strokeStyle = H.a(H.col(k % 5 === 0 ? 1 : 0), k % 5 === 0 ? .9 : .4); c.beginPath(); for (let i = 0; i <= seg; i++) { const q = pass ? P(k * cs, i / seg * h) : P(i / seg * w, k * cs); i ? c.lineTo(q[0], q[1]) : c.moveTo(q[0], q[1]); } c.stroke(); }
  });
  add('lissajous', 'oscilloscope, harmonic, hypnotic', 'Layered Lissajous/harmonograph curves with phase drift. Great centrepiece loop.', { curves: 5, a: 3, b: 4, size: .42 }, (c, t, o, H) => {
    const { w, h } = o, N = o.curves || 5, A = o.a || 3, B = o.b || 4, S = (o.size || .42) * Math.min(w, h); c.lineWidth = H.lw * 1.4; c.lineJoin = 'round';
    for (let k = 0; k < N; k++) { c.beginPath(); c.strokeStyle = H.a(H.col(k), .9 - k * .1); for (let i = 0; i <= 600; i++) { const u = i / 600 * TAU; const x = w / 2 + S * Math.sin(A * u + H.ph + k * .35) * (1 - k * .06), y = h / 2 + S * Math.sin(B * u + k * .5) * (1 - k * .06); i ? c.lineTo(x, y) : c.moveTo(x, y); } c.stroke(); }
  });
  add('sineBraid', 'fluid, ribbon, hair', 'Bundles of parallel sine strands that braid and cross. Horizontal band or full bleed.', { strands: 26, amp: .16, freq: 1.4 }, (c, t, o, H) => {
    const { w, h } = o, N = o.strands || 26, amp = (o.amp || .16) * h, fq = o.freq || 1.4; c.lineWidth = H.lw * 1.3;
    for (let s = 0; s < N; s++) { const k = s / (N - 1); c.beginPath(); c.strokeStyle = H.a(H.col(s * .25 + 1), .85); for (let i = 0; i <= 120; i++) { const x = i / 120 * w, u = i / 120 * TAU * fq; const y = h / 2 + amp * Math.sin(u + H.ph + k * 2.2) * Math.cos(u * .5 - H.ph * .0 + k * 3) + (k - .5) * h * .1 * Math.sin(u * .7 + H.ph); i ? c.lineTo(x, y) : c.moveTo(x, y); } c.stroke(); }
  });
  add('stringArt', 'geometric, delicate, mathematical', 'Chords between points on two edges/circle producing envelope curves.', { n: 90, mode: 0 }, (c, t, o, H) => {
    const { w, h } = o, n = o.n || 90, R = Math.min(w, h) * .42, cx = w / 2, cy = h / 2; c.lineWidth = H.lw * .8;
    for (let i = 0; i < n; i++) { const a = i / n * TAU, b = a * (2 + .5 * Math.sin(H.ph)) + H.ph * 0; c.strokeStyle = H.a(H.col(i * 4 / n), .6); c.beginPath(); c.moveTo(cx + Math.cos(a) * R, cy + Math.sin(a) * R); const m2 = (2 + 1.5 * (.5 + .5 * Math.sin(H.ph))) ; c.lineTo(cx + Math.cos(a * m2) * R, cy + Math.sin(a * m2) * R); c.stroke(); }
  });
  add('moire', 'op-art, vibrating, optical', 'Two rotating line gratings interfering. Instantly "designed"; strong at low density.', { lines: 70, angle: .06 }, (c, t, o, H) => {
    const { w, h } = o, N = o.lines || 70, d = Math.hypot(w, h), gap = d / N; c.lineWidth = H.lw * 1.4;
    for (let g = 0; g < 2; g++) { c.save(); c.translate(w / 2, h / 2); c.rotate((g ? (o.angle || .06) * Math.sin(H.ph) : 0) + (g ? .02 : 0)); c.strokeStyle = H.a(H.col(g), .85); c.beginPath(); for (let i = -N; i <= N; i++) { c.moveTo(i * gap, -d); c.lineTo(i * gap, d); } c.stroke(); c.restore(); }
  });
  add('stripesWarp', 'op-art, 60s, psychedelic', 'Parallel stripes displaced by sine/noise into 3D-looking folds.', { stripes: 46, fold: .12 }, (c, t, o, H) => {
    const { w, h } = o, N = o.stripes || 46, fo = (o.fold || .12) * w, seg = 90;
    for (let s = 0; s < N; s++) { const y0 = s / N * h * 1.2 - h * .1, th = h / N * .62; c.beginPath(); for (let i = 0; i <= seg; i++) { const x = i / seg * w, k = x / w, y = y0 + fo * (Math.sin(k * 5 + s * .1 + H.ph) * .5 + H.ln(k * 2, s * .05) * .5) * Math.sin(k * Math.PI); i ? c.lineTo(x, y) : c.moveTo(x, y); } for (let i = seg; i >= 0; i--) { const x = i / seg * w, k = x / w, y = y0 + th + fo * (Math.sin(k * 5 + s * .1 + H.ph) * .5 + H.ln(k * 2, s * .05) * .5) * Math.sin(k * Math.PI); c.lineTo(x, y); } c.closePath(); c.fillStyle = H.col(s % 3 === 0 ? 1 : s % 3 === 1 ? 2 : 0); c.fill(); }
  });

  /* ───────── DOTS, GRIDS, TILES ───────── */
  add('dotGrid', 'pulsing, techno, clean', 'Grid of dots whose size follows a travelling wave. Style: circle|square|ring|plus. Use as a calm texture or a reveal.', { cell: 36, style: 'circle', wave: 6, rings: 1 }, (c, t, o, H) => {
    const { w, h } = o, cs = o.cell || 36, cx = w / 2, cy = h / 2, st = o.style || 'circle', wv = o.wave || 6, md = Math.hypot(cx, cy);
    for (let y = cs / 2; y < h; y += cs) for (let x = cs / 2; x < w; x += cs) {
      const d = Math.hypot(x - cx, y - cy) / md, k = .5 + .5 * Math.sin(d * wv * Math.PI - H.ph + H.ln(x / w * 2, y / h * 2) * 1.2), rr = cs * .5 * (.12 + .78 * k);
      c.fillStyle = H.a(H.col(d * 3 + k), .35 + .65 * k); c.strokeStyle = c.fillStyle; c.lineWidth = H.lw * 1.5;
      if (st === 'square') c.fillRect(x - rr, y - rr, rr * 2, rr * 2); else if (st === 'ring') { c.beginPath(); c.arc(x, y, rr, 0, TAU); c.stroke(); } else if (st === 'plus') { c.beginPath(); c.moveTo(x - rr, y); c.lineTo(x + rr, y); c.moveTo(x, y - rr); c.lineTo(x, y + rr); c.stroke(); } else { c.beginPath(); c.arc(x, y, rr, 0, TAU); c.fill(); }
    }
  });
  add('truchet', 'maze, tile, bauhaus', 'Quarter-arc tiles that flip in a stagger. Reads as pattern design, not "AI noise".', { cell: 90, width: .28 }, (c, t, o, H) => {
    const { w, h } = o, cs = o.cell || 90, r = H.rng(2); c.lineCap = 'butt'; c.lineWidth = cs * (o.width || .28);
    for (let j = 0; j < Math.ceil(h / cs); j++) for (let i = 0; i < Math.ceil(w / cs); i++) {
      const hsh = r(), delay = r(), flip = (hsh > .5) !== ((Math.floor(H.ph / TAU * 2 + delay * .5) | 0) % 2 === 1 && false); const k = clamp(Math.sin(H.ph + delay * TAU) * 2 + .5, 0, 1); const rot = (hsh > .5 ? 0 : 1) + k; const x = i * cs, y = j * cs;
      c.save(); c.translate(x + cs / 2, y + cs / 2); c.rotate(rot * Math.PI / 2); c.strokeStyle = H.a(H.col((i + j) % 3), .95);
      c.beginPath(); c.arc(-cs / 2, -cs / 2, cs / 2, 0, Math.PI / 2); c.stroke(); c.beginPath(); c.arc(cs / 2, cs / 2, cs / 2, Math.PI, Math.PI * 1.5); c.stroke(); c.restore();
    }
  });
  add('hexPulse', 'sci-fi, honeycomb, shield', 'Hexagon lattice where a light wave travels; edges glow when the wave passes.', { size: 44, wave: 1.6 }, (c, t, o, H) => {
    const { w, h } = o, s = o.size || 44, dx = s * 1.5, dy = s * Math.sqrt(3), cx = w / 2, cy = h / 2, md = Math.hypot(cx, cy);
    for (let j = -1; j < h / dy + 1; j++) for (let i = -1; i < w / dx + 1; i++) {
      const x = i * dx, y = j * dy + (i % 2 ? dy / 2 : 0), d = Math.hypot(x - cx, y - cy) / md, k = Math.pow(.5 + .5 * Math.sin(d * (o.wave || 1.6) * TAU - H.ph), 3);
      c.beginPath(); for (let a = 0; a < 6; a++) { const an = a * TAU / 6; c.lineTo(x + Math.cos(an) * s * .93, y + Math.sin(an) * s * .93); } c.closePath();
      c.fillStyle = H.a(H.col(1 + Math.floor(d * 3)), .05 + .6 * k); c.fill(); c.strokeStyle = H.a(H.col(2), .2 + .8 * k); c.lineWidth = H.lw; c.stroke();
    }
  });
  add('pixelMosaic', 'retro, 8-bit, data', 'Grid of squares quantised from a noise field into the palette (stepwise colour change).', { cell: 40, gap: 2 }, (c, t, o, H) => {
    const { w, h } = o, cs = o.cell || 40, g = o.gap == null ? 2 : o.gap, m = Math.max(w, h);
    for (let y = 0; y < h; y += cs) for (let x = 0; x < w; x += cs) { const v = H.ln(x / m * 2.2, y / m * 2.2) * .5 + .5, k = Math.floor(clamp(v * 1.25 - .05, 0, .999) * 5); if (k === 0) continue; c.fillStyle = H.col(k - 1); c.fillRect(x + g, y + g, cs - g * 2, cs - g * 2); }
  });
  add('isoBars', 'isometric, city, data-viz', 'Isometric columns whose heights ripple. Three-face shading from the palette.', { cell: 54, height: 2.4 }, (c, t, o, H) => {
    const { w, h } = o, s = o.cell || 54, hz = (o.height || 2.4) * s, a = s * .5, b = s * .25, D = Math.ceil((w / 2 + s) / a), U = Math.ceil((h + hz) / b) + 4;
    const shade = (hx, k) => { const [r, g, bl] = hexRGB(hx); return `rgb(${Math.round(r * k)},${Math.round(g * k)},${Math.round(bl * k)})`; };
    // painter's order: back (small screen-y) to front. u = gx+gy (depth band), d = gx-gy (lateral)
    for (let u = -4; u < U; u++) for (let d = -D - 2; d <= D + 2; d++) {
      if (((u + d) & 1) !== 0) continue; const gx = (u + d) / 2, gy = (u - d) / 2, x = w / 2 + d * a, y = u * b;
      const k = .5 + .5 * Math.sin(Math.hypot(gx - 6, gy - 6) * .5 - H.ph + H.ln(gx * .12, gy * .12) * 1.5), bh = s * .2 + hz * k, base = H.col(1 + ((gx + gy) & 1));
      c.fillStyle = shade(base, 1.15); c.beginPath(); c.moveTo(x, y - bh); c.lineTo(x + a, y - bh + b); c.lineTo(x, y - bh + 2 * b); c.lineTo(x - a, y - bh + b); c.closePath(); c.fill();
      c.fillStyle = shade(base, .7); c.beginPath(); c.moveTo(x - a, y - bh + b); c.lineTo(x, y - bh + 2 * b); c.lineTo(x, y + 2 * b); c.lineTo(x - a, y + b); c.closePath(); c.fill();
      c.fillStyle = shade(base, .45); c.beginPath(); c.moveTo(x + a, y - bh + b); c.lineTo(x, y - bh + 2 * b); c.lineTo(x, y + 2 * b); c.lineTo(x + a, y + b); c.closePath(); c.fill();
    }
  });
  add('glyphField', 'terminal, data, brutalist', 'Grid of characters that flip/scramble in waves. Good for hacker/data moods; pass font family via o.font.', { cell: 38, chars: '01<>/\\{}+=*#', font: 'monospace' }, (c, t, o, H) => {
    const { w, h } = o, cs = o.cell || 38, ch = (o.chars || '01<>/\\{}+=*#').split(''), r = H.rng(3); c.font = `700 ${cs * .8}px ${o.font || 'monospace'}`; c.textAlign = 'center'; c.textBaseline = 'middle';
    for (let y = 0; y < h; y += cs) for (let x = 0; x < w; x += cs) { const k = r(), tick = Math.floor((H.ph / TAU * (o.loop ? 6 : 1) * 6 + k * 9)), q = H.ln(x / w * 2, y / h * 2) * .5 + .5; if (q < .38) continue; const g = ch[Math.abs(Math.floor(L.hash(tick * 13 + Math.floor(x / cs) * 7 + Math.floor(y / cs) * 131) * ch.length)) % ch.length]; c.fillStyle = H.a(H.col(q > .8 ? 3 : 1), .25 + q * .7); c.fillText(g, x + cs / 2, y + cs / 2); }
  });

  /* ───────── SHAPES, RINGS, RADIAL ───────── */
  add('rings', 'sonar, ripple, calm', 'Concentric rings expanding from one or several centres with interference.', { origins: 3, count: 16, width: 2 }, (c, t, o, H) => {
    const { w, h } = o, r = H.rng(4), N = o.origins || 3, cnt = o.count || 16, md = Math.hypot(w, h) * .7; c.lineWidth = H.lw * (o.width || 2);
    for (let k = 0; k < N; k++) { const ox = w * (.2 + .6 * r()), oy = h * (.25 + .5 * r()); for (let i = 0; i < cnt; i++) { const u = mod(i / cnt + H.ph / TAU, 1), rad = u * md; c.strokeStyle = H.a(H.col(k), (1 - u) * .85); c.beginPath(); c.arc(ox, oy, rad, 0, TAU); c.stroke(); } }
  });
  add('orbits', 'planetary, system, infographic', 'Concentric orbits with dots travelling at different speeds (all whole cycles per loop).', { rings: 7, dots: 2 }, (c, t, o, H) => {
    const { w, h } = o, N = o.rings || 7, R = Math.min(w, h) * .46, r = H.rng(5), cx = w / 2, cy = h / 2; c.lineWidth = H.lw;
    for (let i = 1; i <= N; i++) { const rad = R * i / N; c.strokeStyle = H.a(H.col(0), .25); c.beginPath(); c.arc(cx, cy, rad, 0, TAU); c.stroke(); const nd = 1 + Math.floor(r() * (o.dots || 2) + .5), sp = (r() < .5 ? -1 : 1) * (1 + Math.floor(r() * 3)); for (let d = 0; d < nd; d++) { const a = r() * TAU + H.ph * sp, ds = (3 + r() * 6) * H.lw * 2; c.fillStyle = H.col(i + d); c.beginPath(); c.arc(cx + Math.cos(a) * rad, cy + Math.sin(a) * rad, ds, 0, TAU); c.fill(); } }
  });
  add('sunburst', 'retro, rising, optimistic', 'Alternating rays from a point, slowly rotating. Pair with a hero object in front.', { rays: 28, cx: .5, cy: .5 }, (c, t, o, H) => {
    const { w, h } = o, N = o.rays || 28, cx = w * (o.cx == null ? .5 : o.cx), cy = h * (o.cy == null ? .5 : o.cy), R = Math.hypot(w, h);
    for (let i = 0; i < N; i++) { const a0 = i / N * TAU + H.ph * (1 / (o.loop ? 1 : 1)) * (2 / N) * 1, a1 = a0 + TAU / N * .5; c.fillStyle = H.a(H.col(i % 2 ? 1 : 2), i % 2 ? .35 : .8); c.beginPath(); c.moveTo(cx, cy); c.arc(cx, cy, R, a0, a1); c.closePath(); c.fill(); }
  });
  add('radialBars', 'audio, pulse, energy', 'Bars around a circle whose length is driven by noise or by an explicit array o.levels(t).', { bars: 96, inner: .22, length: .22 }, (c, t, o, H) => {
    const { w, h } = o, N = o.bars || 96, R0 = (o.inner || .22) * Math.min(w, h), LN = (o.length || .22) * Math.min(w, h), cx = w / 2, cy = h / 2; c.lineCap = 'round'; c.lineWidth = Math.max(2, TAU * R0 / N * .55);
    for (let i = 0; i < N; i++) { const a = i / N * TAU - Math.PI / 2, v = o.levels ? o.levels(i / N, t) : Math.pow(.5 + .5 * H.ln(Math.cos(a) * 1.3, Math.sin(a) * 1.3), 1.6); c.strokeStyle = H.col(1 + 3 * i / N); c.beginPath(); c.moveTo(cx + Math.cos(a) * R0, cy + Math.sin(a) * R0); c.lineTo(cx + Math.cos(a) * (R0 + LN * (.08 + v)), cy + Math.sin(a) * (R0 + LN * (.08 + v))); c.stroke(); }
  });
  add('mandala', 'ornamental, symmetrical, meditative', 'N-fold symmetric petals and rings built from layers; each layer rotates at a different whole-number speed.', { folds: 12, layers: 6 }, (c, t, o, H) => {
    const { w, h } = o, F = o.folds || 12, Ln = o.layers || 6, R = Math.min(w, h) * .46; c.save(); c.translate(w / 2, h / 2); c.lineWidth = H.lw * 1.2;
    for (let l = 0; l < Ln; l++) { const rr = R * (l + 1) / Ln, rot = H.ph * (l % 2 ? -1 : 1) * (1 + (l % 3)) / (F * .5); c.strokeStyle = H.a(H.col(l), .9); c.fillStyle = H.a(H.col(l + 1), .12 + .06 * l);
      for (let i = 0; i < F; i++) { c.save(); c.rotate(i / F * TAU + rot); c.beginPath(); c.moveTo(0, rr * .2); c.bezierCurveTo(rr * .22, rr * .5, rr * .18, rr * .85, 0, rr); c.bezierCurveTo(-rr * .18, rr * .85, -rr * .22, rr * .5, 0, rr * .2); c.fill(); c.stroke(); c.restore(); } }
    c.restore();
  });
  add('polyRipples', 'geometric, tunnel, hypnotic', 'Nested polygons (sides 3..8) rotating and scaling outwards; very "motion-poster".', { sides: 6, count: 14 }, (c, t, o, H) => {
    const { w, h } = o, N = o.count || 14, S = o.sides || 6, R = Math.hypot(w, h) * .55; c.save(); c.translate(w / 2, h / 2); c.lineWidth = H.lw * 2;
    for (let i = N; i >= 0; i--) { const u = mod(i / N + H.ph / TAU, 1), rad = Math.pow(u, 1.6) * R; c.save(); c.rotate(u * 1.4 + H.ph * .0); c.beginPath(); for (let s = 0; s < S; s++) { const a = s / S * TAU; s ? c.lineTo(Math.cos(a) * rad, Math.sin(a) * rad) : c.moveTo(Math.cos(a) * rad, Math.sin(a) * rad); } c.closePath(); c.fillStyle = (i % 2) ? H.a(H.col(1), .12) : o.pal[0]; c.fill(); c.strokeStyle = H.a(H.col(i), .9 * (1 - u * .6)); c.stroke(); c.restore(); }
    c.restore();
  });
  add('tunnelRects', 'zoom, perspective, brutalist', 'Rounded rectangles scaling past the camera; instant depth without 3D.', { count: 12, radius: .08 }, (c, t, o, H) => {
    const { w, h } = o, N = o.count || 12; c.lineWidth = H.lw * 3;
    for (let i = N; i >= 0; i--) { const u = mod(i / N + H.ph / TAU, 1), s = Math.pow(u, 2.2) * 1.6, rw = w * s, rh = h * s, rad = (o.radius || .08) * Math.min(rw, rh); c.beginPath(); (c.roundRect ? c.roundRect(w / 2 - rw / 2, h / 2 - rh / 2, rw, rh, rad) : c.rect(w / 2 - rw / 2, h / 2 - rh / 2, rw, rh)); c.fillStyle = (i % 2) ? H.a(H.col(1), .18 * u) : H.a(o.pal[0], .6); c.fill(); c.strokeStyle = H.a(H.col(i), Math.min(1, u * 2.5) * (1 - u * .3)); c.stroke(); }
  });
  add('spiral', 'sunflower, natural, hypnotic', 'Phyllotaxis dots (golden angle) breathing in size; reads as organic maths.', { dots: 900, size: 7 }, (c, t, o, H) => {
    const { w, h } = o, N = o.dots || 900, R = Math.min(w, h) * .47, ga = Math.PI * (3 - Math.sqrt(5));
    for (let i = 1; i <= N; i++) { const r = R * Math.sqrt(i / N), a = i * ga + H.ph * .0, k = .5 + .5 * Math.sin(i * .02 - H.ph), s = (o.size || 7) * H.lw * (.3 + .7 * Math.sqrt(i / N)) * (.6 + .6 * k); c.fillStyle = H.a(H.col(i * .01), .5 + .5 * k); c.beginPath(); c.arc(w / 2 + Math.cos(a) * r, h / 2 + Math.sin(a) * r, s, 0, TAU); c.fill(); }
  });

  /* ───────── ORGANIC, SOFT, COLOUR ───────── */
  add('blobs', 'soft, friendly, flat-design', 'Morphing organic shapes with flat fills and optional offset shadow; "Notion/Stripe" illustration backdrops.', { count: 6, size: .28, wobble: .35 }, (c, t, o, H) => {
    const { w, h } = o, r = H.rng(6), N = o.count || 6, S = (o.size || .28) * Math.min(w, h);
    for (let b = 0; b < N; b++) { const cx = w * (.1 + .8 * r()), cy = h * (.1 + .8 * r()), sz = S * (.5 + r()), dx = Math.sin(H.ph + b * 1.3) * S * .12, dy = Math.cos(H.ph + b * 1.7) * S * .12; c.beginPath(); const seg = 72; for (let i = 0; i <= seg; i++) { const a = i / seg * TAU, rr = sz * (1 + (o.wobble || .35) * H.ln(Math.cos(a) * .9 + b * 3, Math.sin(a) * .9 + b * 5, b)); const x = cx + dx + Math.cos(a) * rr, y = cy + dy + Math.sin(a) * rr; i ? c.lineTo(x, y) : c.moveTo(x, y); } c.closePath(); c.fillStyle = H.a(H.col(b), .9); c.fill(); }
  });
  add('gradientBlobs', 'dreamy, grainy-gradient, premium', 'Big soft colour clouds (radial gradients) + fine grain specks; the 2023 "grainy gradient" look, procedural.', { count: 5, grain: 1 }, (c, t, o, H) => {
    const { w, h } = o, r = H.rng(7), N = o.count || 5, m = Math.max(w, h);
    for (let b = 0; b < N; b++) { const cx = w * (.1 + .8 * r()) + Math.sin(H.ph + b * 2) * m * .06, cy = h * (.1 + .8 * r()) + Math.cos(H.ph + b * 1.4) * m * .06, rad = m * (.28 + .3 * r()); const g = c.createRadialGradient(cx, cy, 0, cx, cy, rad); g.addColorStop(0, H.a(H.col(b + 1), .95)); g.addColorStop(1, H.a(H.col(b + 1), 0)); c.fillStyle = g; c.fillRect(0, 0, w, h); }
    const gr = o.grain == null ? 1 : o.grain, rr = H.rng(8), cnt = Math.floor(w * h / 90 * gr); for (let i = 0; i < cnt; i++) { c.fillStyle = rr() < .5 ? 'rgba(255,255,255,.07)' : 'rgba(0,0,0,.07)'; c.fillRect(rr() * w, rr() * h, 1.5, 1.5); }
  });
  add('lowPoly', 'crystalline, vector, facets', 'Triangulated jittered grid, each facet coloured by a drifting noise through the palette.', { cell: 110, jitter: .35 }, (c, t, o, H) => {
    const { w, h } = o, cs = o.cell || 110, nx = Math.ceil(w / cs) + 2, ny = Math.ceil(h / cs) + 2, r = H.rng(9), P = []; const m = Math.max(w, h);
    for (let j = 0; j < ny; j++) { P[j] = []; for (let i = 0; i < nx; i++) P[j][i] = [(i - .5) * cs + (r() - .5) * cs * (o.jitter || .35) * 2 + Math.sin(H.ph + i + j) * 4, (j - .5) * cs + (r() - .5) * cs * (o.jitter || .35) * 2 + Math.cos(H.ph + i * 1.3 + j) * 4]; }
    const colr = (x, y, k) => { const v = clamp((H.ln(x / m * 1.4, y / m * 1.4) * .5 + .5) * 1.1 + k, 0, .999) * 3, i = Math.floor(v), f = v - i; return L.mixColor(o.pal[1 + i], o.pal[2 + i > 4 ? 4 : 2 + i], f); };
    for (let j = 0; j < ny - 1; j++) for (let i = 0; i < nx - 1; i++) { const a = P[j][i], b = P[j][i + 1], d = P[j + 1][i], e = P[j + 1][i + 1]; for (const [A, B, C, k] of [[a, b, d, -.04], [b, e, d, .05]]) { c.beginPath(); c.moveTo(A[0], A[1]); c.lineTo(B[0], B[1]); c.lineTo(C[0], C[1]); c.closePath(); const cc = colr((A[0] + B[0] + C[0]) / 3, (A[1] + B[1] + C[1]) / 3, k); c.fillStyle = typeof cc === 'string' ? cc : `rgb(${cc.map(Math.round).join(',')})`; c.fill(); c.strokeStyle = c.fillStyle; c.lineWidth = 1; c.stroke(); } }
  });
  add('voronoi', 'cellular, stained-glass, biological', 'Moving seed points; each cell flat-filled from the palette with thin borders. Coarse pixel blocks keep it fast.', { seeds: 22, block: 6 }, (c, t, o, H) => {
    const { w, h } = o, N = o.seeds || 22, r = H.rng(10), bl = o.block || 6, S = []; for (let i = 0; i < N; i++) S.push([r(), r(), r() * TAU, .03 + r() * .05]);
    const P = S.map(s => [w * (s[0] + Math.cos(H.ph + s[2]) * s[3]), h * (s[1] + Math.sin(H.ph + s[2]) * s[3])]);
    for (let y = 0; y < h; y += bl) for (let x = 0; x < w; x += bl) { let d1 = 1e9, d2 = 1e9, k = 0; for (let i = 0; i < N; i++) { const dx = x - P[i][0], dy = y - P[i][1], d = dx * dx + dy * dy; if (d < d1) { d2 = d1; d1 = d; k = i; } else if (d < d2) d2 = d; } const edge = Math.sqrt(d2) - Math.sqrt(d1); c.fillStyle = edge < bl * .9 ? o.pal[0] : (k % 5 === 0 ? o.pal[0] : H.col(k)); c.fillRect(x, y, bl, bl); }
  });
  add('bubbles', 'playful, fresh, underwater', 'Rising translucent bubbles with highlights, wobble and parallax sizes.', { count: 60 }, (c, t, o, H) => {
    const { w, h } = o, r = H.rng(11), N = o.count || 60;
    for (let i = 0; i < N; i++) { const sz = (10 + r() * r() * 90) * (Math.min(w, h) / 540), x0 = r() * w, sp = (.4 + sz / 100), u = mod(r() + H.ph / TAU * Math.max(1, Math.round(sp * 2)) , 1), y = h + sz - u * (h + sz * 2), x = x0 + Math.sin(H.ph * 2 + i) * sz * .35; const g = c.createRadialGradient(x - sz * .3, y - sz * .3, sz * .05, x, y, sz); g.addColorStop(0, H.a('#ffffff', .55)); g.addColorStop(.35, H.a(H.col(i), .12)); g.addColorStop(1, H.a(H.col(i), .45)); c.fillStyle = g; c.beginPath(); c.arc(x, y, sz, 0, TAU); c.fill(); c.strokeStyle = H.a(H.col(i), .8); c.lineWidth = H.lw; c.stroke(); }
  });
  add('plexus', 'network, ai, data', 'Drifting nodes connected by fading lines when close. The "AI network" look; keep node count low for elegance.', { nodes: 70, link: .16 }, (c, t, o, H) => {
    const { w, h } = o, N = o.nodes || 70, r = H.rng(12), P = [], md = (o.link || .16) * Math.max(w, h); for (let i = 0; i < N; i++) { const bx = r() * w, by = r() * h, a = r() * TAU, rad = 20 + r() * 60; P.push([bx + Math.cos(H.ph * (1 + (i % 2)) + a) * rad, by + Math.sin(H.ph * (1 + ((i + 1) % 2)) + a) * rad]); }
    c.lineWidth = H.lw; for (let i = 0; i < N; i++) for (let j = i + 1; j < N; j++) { const d = Math.hypot(P[i][0] - P[j][0], P[i][1] - P[j][1]); if (d < md) { c.strokeStyle = H.a(H.col(1), (1 - d / md) * .7); c.beginPath(); c.moveTo(P[i][0], P[i][1]); c.lineTo(P[j][0], P[j][1]); c.stroke(); } }
    for (let i = 0; i < N; i++) { c.fillStyle = H.col(i % 3 + 1); c.beginPath(); c.arc(P[i][0], P[i][1], (2 + (i % 4)) * H.lw * 1.2, 0, TAU); c.fill(); }
  });
  add('lightning', 'electric, tension, sci-fi', 'Jagged branching arcs between two points, re-rolled at 12 fps (set o.from/o.to as 0..1 points).', { bolts: 3 }, (c, t, o, H) => {
    const { w, h } = o, tick = Math.floor((o.loop ? mod(t, o.loop) : t) * (o.fps || 12) + 1e-6), from = o.from || [.1, .5], to = o.to || [.9, .5];
    const bolt = (x0, y0, x1, y1, d, r, wid) => { const pts = [[x0, y0], [x1, y1]]; for (let k = 0; k < d; k++) { for (let i = pts.length - 2; i >= 0; i--) { const a = pts[i], b = pts[i + 1], mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2, len = Math.hypot(b[0] - a[0], b[1] - a[1]); pts.splice(i + 1, 0, [mx + (r() - .5) * len * .45, my + (r() - .5) * len * .45]); } } c.lineWidth = wid; c.beginPath(); pts.forEach((p, i) => i ? c.lineTo(p[0], p[1]) : c.moveTo(p[0], p[1])); c.stroke(); };
    const r = L.rng(tick * 131 + (o.seed || 1)); c.lineJoin = 'round'; c.lineCap = 'round';
    for (let b = 0; b < (o.bolts || 3); b++) { c.strokeStyle = H.a(H.col(1), .35); bolt(w * from[0], h * from[1], w * to[0], h * to[1], 6, L.rng(tick * 131 + b * 17 + 1), H.lw * 9); c.strokeStyle = H.a(o.pal[4], .95); bolt(w * from[0], h * from[1], w * to[0], h * to[1], 6, L.rng(tick * 131 + b * 17 + 1), H.lw * 2); }
  });
  add('scribble', 'hand-drawn, sketchy, human', 'Rough hatch/scribble fills and wobbly outlines (rough.js style) for hand-made brands. Draws N shapes.', { shapes: 8, hatch: 14 }, (c, t, o, H) => {
    const { w, h } = o, N = o.shapes || 8, r = H.rng(13), tick = Math.floor((o.loop ? mod(t, o.loop) : t) * 8 + 1e-6); c.lineCap = 'round';
    for (let s = 0; s < N; s++) { const cx = w * (.12 + .76 * r()), cy = h * (.1 + .8 * r()), sz = Math.min(w, h) * (.08 + .14 * r()), kind = Math.floor(r() * 3), rj = L.rng(tick * 7 + s * 31 + (o.seed || 1)); const J = () => (rj() - .5) * sz * .06; c.strokeStyle = H.a(H.col(s), .95); c.lineWidth = H.lw * 2.4;
      const path = () => { c.beginPath(); if (kind === 0) for (let i = 0; i <= 28; i++) { const a = i / 28 * TAU * 1.04; const x = cx + Math.cos(a) * sz + J(), y = cy + Math.sin(a) * sz + J(); i ? c.lineTo(x, y) : c.moveTo(x, y); } else { const n = kind === 1 ? 4 : 3; for (let i = 0; i <= n + 1; i++) { const a = (i % n) / n * TAU + (kind === 1 ? Math.PI / 4 : -Math.PI / 2), x = cx + Math.cos(a) * sz * 1.1 + J(), y = cy + Math.sin(a) * sz * 1.1 + J(); i ? c.lineTo(x, y) : c.moveTo(x, y); } } };
      c.save(); path(); c.clip(); c.lineWidth = H.lw * 1.3; c.beginPath(); const hc = o.hatch || 14; for (let i = -hc; i <= hc; i++) { const x = cx + i * sz / hc * 1.5; c.moveTo(x - sz + J(), cy + sz + J()); c.lineTo(x + sz + J(), cy - sz + J()); } c.stroke(); c.restore(); c.lineWidth = H.lw * 2.4; path(); c.stroke(); path(); c.stroke(); }
  });
  add('memphis', 'playful, 80s, pop', 'Scattered Memphis primitives (squiggle, triangle, ring, plus, dots, half-circle) drifting and rotating.', { count: 34, size: 1 }, (c, t, o, H) => {
    const { w, h } = o, N = o.count || 34, r = H.rng(14), S = Math.min(w, h) * .045 * (o.size || 1);
    for (let i = 0; i < N; i++) { const x = r() * w, y = r() * h, k = Math.floor(r() * 6), sc = S * (.8 + r() * 1.4), rot = r() * TAU + H.ph * (r() < .5 ? -1 : 1) * (1 + Math.floor(r() * 2)), dx = Math.sin(H.ph + i) * sc * .4, dy = Math.cos(H.ph * 1 + i * 1.7) * sc * .4; c.save(); c.translate(x + dx, y + dy); c.rotate(rot); c.strokeStyle = H.col(i); c.fillStyle = H.col(i); c.lineWidth = H.lw * 3.5; c.lineCap = 'round';
      if (k === 0) { c.beginPath(); for (let u = 0; u <= 24; u++) { const px = (u / 24 - .5) * sc * 3, py = Math.sin(u / 24 * TAU * 2.5) * sc * .45; u ? c.lineTo(px, py) : c.moveTo(px, py); } c.stroke(); } else if (k === 1) { c.beginPath(); c.moveTo(0, -sc); c.lineTo(sc, sc * .8); c.lineTo(-sc, sc * .8); c.closePath(); c.fill(); } else if (k === 2) { c.beginPath(); c.arc(0, 0, sc, 0, TAU); c.stroke(); } else if (k === 3) { c.beginPath(); c.moveTo(-sc, 0); c.lineTo(sc, 0); c.moveTo(0, -sc); c.lineTo(0, sc); c.stroke(); } else if (k === 4) { c.beginPath(); c.arc(0, 0, sc, 0, Math.PI); c.closePath(); c.fill(); } else { for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) { c.beginPath(); c.arc(a * sc * .6, b * sc * .6, sc * .12, 0, TAU); c.fill(); } } c.restore(); }
  });
  add('confetti', 'celebration, burst, pop', 'Deterministic confetti burst from o.origin at time o.t0 (gravity + drag + flutter). Call every frame; before t0 draws nothing.', { count: 120, t0: 0, power: 1 }, (c, t, o, H) => {
    const { w, h } = o, tt = (o.time != null ? o.time : t) - (o.t0 || 0); if (tt < 0) return; const r = L.rng((o.seed || 1) * 99 + 7), N = o.count || 120, ox = w * (o.origin ? o.origin[0] : .5), oy = h * (o.origin ? o.origin[1] : .55), pw = (o.power || 1) * Math.max(w, h);
    for (let i = 0; i < N; i++) { const a = -Math.PI / 2 + (r() - .5) * 2.2, sp = pw * (.5 + r() * 1.0), life = 1.6 + r(), sz = (6 + r() * 10) * (Math.min(w, h) / 540), fl = r() * TAU, fs = 6 + r() * 8; const u = tt, drag = Math.exp(-u * 2.2), x = ox + Math.cos(a) * sp * (1 - drag) / 2.2, y = oy + Math.sin(a) * sp * (1 - drag) / 2.2 + .5 * pw * .9 * u * u * .5; if (u > life) continue; const al = clamp((life - u) / .5); c.save(); c.translate(x, y); c.rotate(fl + u * fs); c.scale(1, Math.cos(fl + u * fs * .8)); c.fillStyle = H.a(H.col(i), al); c.fillRect(-sz / 2, -sz / 4, sz, sz / 2); c.restore(); }
  });
  add('brushStrokes', 'painterly, expressive, analog', 'Thick translucent brush strokes with dry-edge bristle lines sweeping across the frame.', { strokes: 7, bristles: 22 }, (c, t, o, H) => {
    const { w, h } = o, N = o.strokes || 7, r = H.rng(15), B = o.bristles || 22;
    for (let s = 0; s < N; s++) { const y0 = h * (.1 + .8 * r()), th = h * (.04 + .06 * r()), x0 = -w * .1, x1 = w * (.7 + .4 * r()), prog = clamp(Math.sin(H.ph * 0 + (s * .9)) * 0 + 1), cc = H.col(s); for (let b = 0; b < B; b++) { const yb = y0 + (b / (B - 1) - .5) * th, rj = r(), len = 1 - rj * .2; c.strokeStyle = H.a(cc, .35 + .5 * r()); c.lineWidth = th / B * 1.7; c.beginPath(); for (let i = 0; i <= 32; i++) { const k = i / 32 * len, x = x0 + (x1 - x0) * k, y = yb + Math.sin(k * 5 + s + H.ph) * th * .35 + H.ln(k * 2, s * 3 + b * .1) * th * .2; i ? c.lineTo(x, y) : c.moveTo(x, y); } c.stroke(); } }
  });

  /* ───────── dispatcher ───────── */
  function draw(ctx, name, t, o) {
    const fn = G[name]; if (!fn) throw new Error('Art: unknown generator "' + name + '". Known: ' + Object.keys(G).join(', '));
    o = Object.assign({}, o || {}); const cv = ctx.canvas || { width: 1080, height: 1920 };
    o.x = o.x || 0; o.y = o.y || 0; o.w = o.w || cv.width - o.x; o.h = o.h || cv.height - o.y; o.pal = o.pal || ['#0b0b12', '#ff4d2e', '#ffb02e', '#2ee6a6', '#fff4e0'];
    if (o.pal.length < 5) o.pal = o.pal.concat(Array(5 - o.pal.length).fill(o.pal[o.pal.length - 1]));
    const H = ctxHelpers(o, t); ctx.save(); ctx.beginPath(); ctx.rect(o.x, o.y, o.w, o.h); ctx.clip(); ctx.translate(o.x, o.y);
    if (o.bg !== false) { ctx.fillStyle = o.pal[0]; ctx.fillRect(0, 0, o.w, o.h); }
    ctx.lineCap = 'round'; ctx.lineJoin = 'round'; fn(ctx, t, o, H); ctx.restore();
  }
  // DNA palette (object with bg/ink/accent... or array) -> 5 slots [bg, ink1, ink2, ink3, hi]
  function palette(p) {
    if (Array.isArray(p)) return p.length >= 5 ? p.slice(0, 5) : p.concat(Array(5 - p.length).fill(p[p.length - 1]));
    const pick = k => p[k] || null, list = [pick('bg') || pick('background') || '#0b0b12', pick('primary') || pick('accent') || '#ff4d2e', pick('secondary') || pick('accent2') || pick('accent') || '#ffb02e', pick('tertiary') || pick('accent3') || pick('ink') || '#2ee6a6', pick('highlight') || pick('fg') || pick('text') || '#fff4e0'];
    return list;
  }
  root.Art = { draw, list: () => Object.keys(G), meta, describe: n => Object.assign({ name: n }, meta[n]), palette };
})(typeof window !== 'undefined' ? window : globalThis);
