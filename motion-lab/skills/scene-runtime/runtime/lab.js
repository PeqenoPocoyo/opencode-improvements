/* lab.js — the motion-lab core. Vanilla JS, no dependencies, one global: window.Lab
 * Everything here is a PURE function of its inputs (time, seed). See CONVENTIONS.md.
 * Sections: math · easing · springs/keyframes · rng · noise · color(OKLCH) · envelopes/beat · text · path ·
 *           camera · shake · loop · events · scene sequencer · init (player + render contract)
 */
(function (root) {
  'use strict';
  const L = {};
  const TAU = Math.PI * 2;

  /* ───────────────────────── math ───────────────────────── */
  const clamp = L.clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  L.TAU = TAU;
  L.lerp = (a, b, k) => a + (b - a) * k;
  L.sat = x => clamp(x, 0, 1);
  L.fract = x => x - Math.floor(x);
  L.mod = (x, m) => ((x % m) + m) % m;                       // true modulo (positive for negative x)
  L.map = (v, a, b, c, d, doClamp = true) => { let k = (v - a) / (b - a); if (doClamp) k = clamp(k); return c + (d - c) * k; };
  L.seg = (t, a, b) => clamp((t - a) / (b - a));              // progress 0..1 of t through [a,b]
  L.smoothstep = (a, b, x) => { const k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k); };
  L.smootherstep = (a, b, x) => { const k = clamp((x - a) / (b - a)); return k * k * k * (k * (6 * k - 15) + 10); };
  L.mix = L.lerp;
  L.deg = d => d * Math.PI / 180;
  L.dist = (x1, y1, x2, y2) => Math.hypot(x2 - x1, y2 - y1);
  L.snap = (v, step) => Math.round(v / step) * step;          // snap time to a grid (beats!)
  L.rotate = (x, y, a) => [x * Math.cos(a) - y * Math.sin(a), x * Math.sin(a) + y * Math.cos(a)];

  /* ───────────────────────── easing ───────────────────────── */
  const E = L.ease = {};
  E.linear = x => clamp(x);
  const pw = n => ({ in: x => Math.pow(clamp(x), n), out: x => 1 - Math.pow(1 - clamp(x), n),
    inOut: x => { x = clamp(x); return x < .5 ? Math.pow(2 * x, n) / 2 : 1 - Math.pow(-2 * x + 2, n) / 2; } });
  [['Quad', 2], ['Cubic', 3], ['Quart', 4], ['Quint', 5]].forEach(([nm, n]) => { const p = pw(n); E['in' + nm] = p.in; E['out' + nm] = p.out; E['inOut' + nm] = p.inOut; });
  E.inSine = x => 1 - Math.cos(clamp(x) * Math.PI / 2); E.outSine = x => Math.sin(clamp(x) * Math.PI / 2); E.inOutSine = x => -(Math.cos(Math.PI * clamp(x)) - 1) / 2;
  E.inExpo = x => (x = clamp(x), x === 0 ? 0 : Math.pow(2, 10 * x - 10));
  E.outExpo = x => (x = clamp(x), x === 1 ? 1 : 1 - Math.pow(2, -10 * x));
  E.inOutExpo = x => (x = clamp(x), x === 0 ? 0 : x === 1 ? 1 : x < .5 ? Math.pow(2, 20 * x - 10) / 2 : (2 - Math.pow(2, -20 * x + 10)) / 2);
  E.inCirc = x => 1 - Math.sqrt(1 - Math.pow(clamp(x), 2)); E.outCirc = x => Math.sqrt(1 - Math.pow(clamp(x) - 1, 2));
  E.inOutCirc = x => (x = clamp(x), x < .5 ? (1 - Math.sqrt(1 - Math.pow(2 * x, 2))) / 2 : (Math.sqrt(1 - Math.pow(-2 * x + 2, 2)) + 1) / 2);
  E.inBack = (x, s = 1.70158) => (x = clamp(x), (s + 1) * x * x * x - s * x * x);
  E.outBack = (x, s = 1.70158) => (x = clamp(x), 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2));
  E.inOutBack = (x, s = 1.70158 * 1.525) => (x = clamp(x), x < .5 ? (Math.pow(2 * x, 2) * ((s + 1) * 2 * x - s)) / 2 : (Math.pow(2 * x - 2, 2) * ((s + 1) * (x * 2 - 2) + s) + 2) / 2);
  E.outElastic = (x, p = .3) => (x = clamp(x), x === 0 ? 0 : x === 1 ? 1 : Math.pow(2, -10 * x) * Math.sin((x - p / 4) * TAU / p) + 1);
  E.inElastic = (x, p = .3) => 1 - E.outElastic(1 - x, p);
  E.inOutElastic = x => (x = clamp(x), x === 0 ? 0 : x === 1 ? 1 : x < .5 ? -(Math.pow(2, 20 * x - 10) * Math.sin((20 * x - 11.125) * TAU / 4.5)) / 2 : (Math.pow(2, -20 * x + 10) * Math.sin((20 * x - 11.125) * TAU / 4.5)) / 2 + 1);
  E.outBounce = x => { x = clamp(x); const n = 7.5625, d = 2.75; if (x < 1 / d) return n * x * x; if (x < 2 / d) return n * (x -= 1.5 / d) * x + .75; if (x < 2.5 / d) return n * (x -= 2.25 / d) * x + .9375; return n * (x -= 2.625 / d) * x + .984375; };
  E.inBounce = x => 1 - E.outBounce(1 - x);
  E.inOutBounce = x => x < .5 ? (1 - E.outBounce(1 - 2 * x)) / 2 : (1 + E.outBounce(2 * x - 1)) / 2;
  // cubic-bezier(x1,y1,x2,y2) exactly like CSS (Newton + bisection)
  L.bezier = (x1, y1, x2, y2) => {
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx, cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    const sx = u => ((ax * u + bx) * u + cx) * u, sy = u => ((ay * u + by) * u + cy) * u, dx = u => (3 * ax * u + 2 * bx) * u + cx;
    return x => {
      x = clamp(x); let u = x;
      for (let i = 0; i < 8; i++) { const e = sx(u) - x; if (Math.abs(e) < 1e-6) return sy(u); const d = dx(u); if (Math.abs(d) < 1e-6) break; u -= e / d; }
      let lo = 0, hi = 1; u = x; while (lo < hi) { const e = sx(u); if (Math.abs(e - x) < 1e-6) break; if (x > e) lo = u; else hi = u; u = (hi - lo) / 2 + lo; if (hi - lo < 1e-7) break; }
      return sy(u);
    };
  };
  L.steps = (n, jumpEnd = true) => x => { x = clamp(x); return jumpEnd ? Math.floor(x * n) / n : Math.ceil(x * n) / n; };
  // named "feels": pick by personality, never default to inOutCubic everywhere
  L.curves = {
    snap: L.bezier(.16, 1, .3, 1),         // fast start, long soft landing (expo-like) — UI, type slams
    punch: L.bezier(.7, 0, .2, 1),         // slow-fast-slow with weight — camera pushes
    whip: L.bezier(.9, 0, .1, 1),          // very late acceleration — whip pans
    glide: L.bezier(.45, 0, .55, 1),       // symmetric, calm
    settle: L.bezier(.34, 1.56, .64, 1),   // overshoot ~8% — playful pops
    drop: L.bezier(.55, 0, 1, .45),        // ease-in only — things leaving / falling
    linear: x => clamp(x)
  };
  L.ease.get = name => (typeof name === 'function' ? name : (E[name] || L.curves[name] || E.outCubic));

  /* ───────────────────────── springs, tracks, keyframes ───────────────────────── */
  // closed-form damped spring step response 0→1. w = angular speed (6 slow … 14 normal … 24 snappy), z = damping (1 = no overshoot)
  const spring = L.spring = (t, w = 14, z = 0.82) => {
    if (t <= 0) return 0;
    if (z >= 1) return 1 - Math.exp(-w * t) * (1 + w * t);
    const wd = w * Math.sqrt(1 - z * z);
    return 1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + (z * w / wd) * Math.sin(wd * t));
  };
  // value that retargets many times; keys: [[time, value, w?, z?], ...]  → f(t)
  L.track = (v0, keys, w = 14, z = 0.82) => t => { let v = v0, p = v0; for (const k of keys) { v += (k[1] - p) * spring(t - k[0], k[2] ?? w, k[3] ?? z); p = k[1]; } return v; };
  // eased keyframes; keys: [[t0,v0],[t1,v1,ease?],...]; ease applies to the segment ENDING at that key
  L.kf = (keys, defEase = 'inOutCubic') => t => {
    if (t <= keys[0][0]) return keys[0][1];
    for (let i = 1; i < keys.length; i++) {
      const [a, va] = keys[i - 1], [b, vb, e] = keys[i];
      if (t <= b) return va + (vb - va) * L.ease.get(e || defEase)((t - a) / (b - a));
    }
    return keys[keys.length - 1][1];
  };
  // 2D/3D vector keyframes
  L.kfv = (keys, defEase) => { const n = keys[0][1].length, fs = Array.from({ length: n }, (_, i) => L.kf(keys.map(k => [k[0], k[1][i], k[2]]), defEase)); return t => fs.map(f => f(t)); };

  /* ───────────────────────── seeded random ───────────────────────── */
  L.rng = (seed = 1) => {
    let s = seed >>> 0;
    const r = () => { s = (s + 0x6D2B79F5) | 0; let t = Math.imul(s ^ (s >>> 15), 1 | s); t ^= t + Math.imul(t ^ (t >>> 7), 61 | t); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
    r.range = (a, b) => a + (b - a) * r();
    r.int = (a, b) => Math.floor(r.range(a, b + 1));
    r.pick = arr => arr[Math.floor(r() * arr.length)];
    r.gauss = (m = 0, sd = 1) => { const u = 1 - r(), v = r(); return m + sd * Math.sqrt(-2 * Math.log(u)) * Math.cos(TAU * v); };
    r.shuffle = arr => { const a = arr.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
    r.weighted = (items, weights) => { const tot = weights.reduce((a, b) => a + b, 0); let x = r() * tot; for (let i = 0; i < items.length; i++) { x -= weights[i]; if (x <= 0) return items[i]; } return items[items.length - 1]; };
    r.onCircle = (rad = 1) => { const a = r() * TAU; return [Math.cos(a) * rad, Math.sin(a) * rad]; };
    r.inCircle = (rad = 1) => { const a = r() * TAU, d = Math.sqrt(r()) * rad; return [Math.cos(a) * d, Math.sin(a) * d]; };
    return r;
  };
  L.hash = (n) => { n = (n << 13) ^ n; return (1 - ((n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff) / 1073741824) * .5 + .5; };

  /* ───────────────────────── noise (simplex 2D/3D, seeded) ───────────────────────── */
  L.noise = (seed = 1) => {
    const r = L.rng(seed), p = new Uint8Array(256); for (let i = 0; i < 256; i++) p[i] = i;
    for (let i = 255; i > 0; i--) { const j = Math.floor(r() * (i + 1)); const t = p[i]; p[i] = p[j]; p[j] = t; }
    const perm = new Uint8Array(512), pm12 = new Uint8Array(512); for (let i = 0; i < 512; i++) { perm[i] = p[i & 255]; pm12[i] = perm[i] % 12; }
    const g3 = [[1, 1, 0], [-1, 1, 0], [1, -1, 0], [-1, -1, 0], [1, 0, 1], [-1, 0, 1], [1, 0, -1], [-1, 0, -1], [0, 1, 1], [0, -1, 1], [0, 1, -1], [0, -1, -1]];
    const F2 = .5 * (Math.sqrt(3) - 1), G2 = (3 - Math.sqrt(3)) / 6, F3 = 1 / 3, G3 = 1 / 6;
    function n2(x, y) {
      const s = (x + y) * F2, i = Math.floor(x + s), j = Math.floor(y + s), t = (i + j) * G2, x0 = x - (i - t), y0 = y - (j - t);
      const i1 = x0 > y0 ? 1 : 0, j1 = x0 > y0 ? 0 : 1, x1 = x0 - i1 + G2, y1 = y0 - j1 + G2, x2 = x0 - 1 + 2 * G2, y2 = y0 - 1 + 2 * G2, ii = i & 255, jj = j & 255;
      let n = 0, tt = .5 - x0 * x0 - y0 * y0; if (tt > 0) { const g = g3[pm12[ii + perm[jj]]]; tt *= tt; n += tt * tt * (g[0] * x0 + g[1] * y0); }
      tt = .5 - x1 * x1 - y1 * y1; if (tt > 0) { const g = g3[pm12[ii + i1 + perm[jj + j1]]]; tt *= tt; n += tt * tt * (g[0] * x1 + g[1] * y1); }
      tt = .5 - x2 * x2 - y2 * y2; if (tt > 0) { const g = g3[pm12[ii + 1 + perm[jj + 1]]]; tt *= tt; n += tt * tt * (g[0] * x2 + g[1] * y2); }
      return 70 * n;
    }
    function n3(x, y, z) {
      const s = (x + y + z) * F3, i = Math.floor(x + s), j = Math.floor(y + s), k = Math.floor(z + s), t = (i + j + k) * G3;
      const x0 = x - (i - t), y0 = y - (j - t), z0 = z - (k - t); let i1, j1, k1, i2, j2, k2;
      if (x0 >= y0) { if (y0 >= z0) { i1 = 1; j1 = 0; k1 = 0; i2 = 1; j2 = 1; k2 = 0; } else if (x0 >= z0) { i1 = 1; j1 = 0; k1 = 0; i2 = 1; j2 = 0; k2 = 1; } else { i1 = 0; j1 = 0; k1 = 1; i2 = 1; j2 = 0; k2 = 1; } }
      else { if (y0 < z0) { i1 = 0; j1 = 0; k1 = 1; i2 = 0; j2 = 1; k2 = 1; } else if (x0 < z0) { i1 = 0; j1 = 1; k1 = 0; i2 = 0; j2 = 1; k2 = 1; } else { i1 = 0; j1 = 1; k1 = 0; i2 = 1; j2 = 1; k2 = 0; } }
      const x1 = x0 - i1 + G3, y1 = y0 - j1 + G3, z1 = z0 - k1 + G3, x2 = x0 - i2 + 2 * G3, y2 = y0 - j2 + 2 * G3, z2 = z0 - k2 + 2 * G3, x3 = x0 - 1 + 3 * G3, y3 = y0 - 1 + 3 * G3, z3 = z0 - 1 + 3 * G3;
      const ii = i & 255, jj = j & 255, kk = k & 255; let n = 0, tt;
      const c = (X, Y, Z, a, b, d) => { tt = .6 - X * X - Y * Y - Z * Z; if (tt > 0) { const g = g3[pm12[a + perm[b + perm[d]]]]; tt *= tt; n += tt * tt * (g[0] * X + g[1] * Y + g[2] * Z); } };
      c(x0, y0, z0, ii, jj, kk); c(x1, y1, z1, ii + i1, jj + j1, kk + k1); c(x2, y2, z2, ii + i2, jj + j2, kk + k2); c(x3, y3, z3, ii + 1, jj + 1, kk + 1);
      return 32 * n;
    }
    const fbm2 = (x, y, oct = 4, lac = 2, gain = .5) => { let a = 1, f = 1, s = 0, n = 0; for (let o = 0; o < oct; o++) { s += a * n2(x * f, y * f); n += a; a *= gain; f *= lac; } return s / n; };
    const fbm3 = (x, y, z, oct = 4, lac = 2, gain = .5) => { let a = 1, f = 1, s = 0, n = 0; for (let o = 0; o < oct; o++) { s += a * n3(x * f, y * f, z * f); n += a; a *= gain; f *= lac; } return s / n; };
    // curl of a 2D noise field → divergence-free flow (great for particles that never clump)
    const curl2 = (x, y, e = .01) => { const dx = (n2(x, y + e) - n2(x, y - e)) / (2 * e), dy = (n2(x + e, y) - n2(x - e, y)) / (2 * e); return [dx, -dy]; };
    // value that loops: noise sampled on a circle in (x,y) → period seconds
    const loop1 = (t, period, scale = 1, off = 0) => { const a = TAU * t / period; return n3(Math.cos(a) * scale + off, Math.sin(a) * scale + off, off * .37); };
    return { n2, n3, fbm2, fbm3, curl2, loop1 };
  };

  /* ───────────────────────── color: OKLCH ↔ sRGB ───────────────────────── */
  const lin2s = c => (c <= .0031308 ? 12.92 * c : 1.055 * Math.pow(c, 1 / 2.4) - .055), s2lin = c => (c <= .04045 ? c / 12.92 : Math.pow((c + .055) / 1.055, 2.4));
  L.oklch2rgb = (l, c, h) => {            // l 0..1, c 0..~0.37, h degrees → [r,g,b] 0..255 (clamped)
    const hr = h * Math.PI / 180, a = c * Math.cos(hr), b = c * Math.sin(hr);
    const l_ = l + .3963377774 * a + .2158037573 * b, m_ = l - .1055613458 * a - .0638541728 * b, s_ = l - .0894841775 * a - 1.291485548 * b;
    const l3 = l_ ** 3, m3 = m_ ** 3, s3 = s_ ** 3;
    const r = 4.0767416621 * l3 - 3.3077115913 * m3 + .2309699292 * s3, g = -1.2684380046 * l3 + 2.6097574011 * m3 - .3413193965 * s3, bb = -.0041960863 * l3 - .7034186147 * m3 + 1.707614701 * s3;
    return [r, g, bb].map(v => Math.round(clamp(lin2s(clamp(v, 0, 1))) * 255));
  };
  L.rgb2oklch = ([r, g, b]) => {
    r = s2lin(r / 255); g = s2lin(g / 255); b = s2lin(b / 255);
    const l = Math.cbrt(.4122214708 * r + .5363325363 * g + .0514459929 * b), m = Math.cbrt(.2119034982 * r + .6806995451 * g + .1073969566 * b), s = Math.cbrt(.0883024619 * r + .2817188376 * g + .6299787005 * b);
    const L_ = .2104542553 * l + .793617785 * m - .0040720468 * s, A = 1.9779984951 * l - 2.428592205 * m + .4505937099 * s, B = .0259040371 * l + .7827717662 * m - .808675766 * s;
    return [L_, Math.hypot(A, B), (Math.atan2(B, A) * 180 / Math.PI + 360) % 360];
  };
  L.hex2rgb = h => { h = h.replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join(''); return [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16)); };
  L.rgb2hex = ([r, g, b]) => '#' + [r, g, b].map(v => Math.round(clamp(v, 0, 255)).toString(16).padStart(2, '0')).join('');
  L.oklch = (l, c, h, a) => { const [r, g, b] = L.oklch2rgb(l, c, h); return a == null ? `rgb(${r},${g},${b})` : `rgba(${r},${g},${b},${a})`; };
  L.oklchHex = (l, c, h) => L.rgb2hex(L.oklch2rgb(l, c, h));
  L.mixColor = (a, b, k) => { const A = typeof a === 'string' ? L.hex2rgb(a) : a, B = typeof b === 'string' ? L.hex2rgb(b) : b; const oa = L.rgb2oklch(A), ob = L.rgb2oklch(B); let dh = ob[2] - oa[2]; if (dh > 180) dh -= 360; if (dh < -180) dh += 360; return L.oklchHex(L.lerp(oa[0], ob[0], k), L.lerp(oa[1], ob[1], k), oa[2] + dh * k); };
  L.rgba = (hex, a) => { const [r, g, b] = L.hex2rgb(hex); return `rgba(${r},${g},${b},${a})`; };
  L.luminance = ([r, g, b]) => .2126 * s2lin(r / 255) + .7152 * s2lin(g / 255) + .0722 * s2lin(b / 255);
  L.contrast = (a, b) => { const A = typeof a === 'string' ? L.hex2rgb(a) : a, B = typeof b === 'string' ? L.hex2rgb(b) : b; const la = L.luminance(A), lb = L.luminance(B); return (Math.max(la, lb) + .05) / (Math.min(la, lb) + .05); };

  /* ───────────────────────── envelopes & beat ───────────────────────── */
  // hit: 0 before t0, jumps to 1 at t0, decays exponentially (tau seconds). THE building block for "everything reacts to the beat".
  L.hit = (t, t0, tau = .25) => (t < t0 ? 0 : Math.exp(-(t - t0) / tau));
  // attack-decay bump: rises over atk, falls over dec
  L.bump = (t, t0, atk = .08, dec = .4) => (t < t0 ? 0 : t < t0 + atk ? (t - t0) / atk : Math.exp(-(t - t0 - atk) / dec));
  // window: 1 between a and b with fade-in fi and fade-out fo
  L.win = (t, a, b, fi = .15, fo = .15) => clamp((t - a) / Math.max(fi, 1e-6)) * clamp((b - t) / Math.max(fo, 1e-6));
  L.adsr = (t, t0, t1, a = .05, d = .1, s = .7, r = .2) => { if (t < t0) return 0; if (t < t0 + a) return (t - t0) / a; if (t < t0 + a + d) return 1 - (1 - s) * (t - t0 - a) / d; if (t < t1) return s; return s * Math.max(0, 1 - (t - t1) / r); };
  // beat clock: returns {i: beat index, phase 0..1 within beat, pulse: decaying hit on every beat, bar, step16}
  L.beat = (t, bpm, offset = 0, tau = .18) => { const b = 60 / bpm, x = (t - offset) / b, i = Math.floor(x), ph = x - i; return { i, phase: ph, pulse: Math.exp(-ph * b / tau), bar: Math.floor(i / 4), step16: Math.floor(x * 4), t0: offset + i * b }; };
  L.beatTimes = (bpm, dur, offset = 0, sub = 1) => { const out = [], b = 60 / bpm / sub; for (let t = offset; t < dur; t += b) out.push(+t.toFixed(4)); return out; };
  // stagger: start offset of item i of n so that all finish within `total` (or `each` apart)
  L.stagger = (i, n, each = .05, total) => (total != null ? (n > 1 ? total * i / (n - 1) : 0) : i * each);

  /* ───────────────────────── text helpers ───────────────────────── */
  // split element text into spans. mode: 'chars' | 'words' | 'lines'. Returns array of span elements (inline-block).
  L.split = (el, mode = 'chars') => {
    const txt = el.textContent; el.textContent = ''; el.setAttribute('aria-label', txt); const out = [];
    const mk = s => { const sp = document.createElement('span'); sp.style.display = 'inline-block'; sp.style.whiteSpace = 'pre'; sp.textContent = s; el.appendChild(sp); out.push(sp); return sp; };
    if (mode === 'chars') { for (const ch of txt) mk(ch === ' ' ? ' ' : ch); }
    else if (mode === 'words') { txt.split(/(\s+)/).forEach(w => { if (/^\s+$/.test(w)) el.appendChild(document.createTextNode(' ')); else if (w) mk(w); }); }
    else { txt.split('\n').forEach((ln, i) => { if (i) el.appendChild(document.createElement('br')); mk(ln); }); }
    return out;
  };
  L.typed = (str, t, t0, cps = 18) => str.slice(0, clamp(Math.floor((t - t0) * cps), 0, str.length));
  // scramble text toward `str`: progress p 0..1; deterministic
  L.scramble = (str, p, seed = 1, chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789#%&*+<>') => {
    const r = L.rng(seed + Math.floor(p * 40)); let out = ''; const n = str.length;
    for (let i = 0; i < n; i++) out += (str[i] === ' ' || i < p * n) ? str[i] : chars[Math.floor(r() * chars.length)];
    return out;
  };
  L.countUp = (a, b, p, decimals = 0, ease = 'outExpo') => (a + (b - a) * L.ease.get(ease)(p)).toFixed(decimals);
  L.fmt = (n, decimals = 0) => Number(n).toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });

  /* ───────────────────────── SVG path helpers ───────────────────────── */
  L.pathAt = (pathEl, p) => {               // p 0..1 → {x,y,angle(rad)}
    const len = pathEl.getTotalLength(), d = len * clamp(p), pt = pathEl.getPointAtLength(d), pt2 = pathEl.getPointAtLength(Math.min(len, d + .5)), pt1 = pathEl.getPointAtLength(Math.max(0, d - .5));
    return { x: pt.x, y: pt.y, angle: Math.atan2(pt2.y - pt1.y, pt2.x - pt1.x) };
  };
  L.drawStroke = (pathEl, p) => {           // "self-drawing" stroke: p 0..1
    const len = pathEl.getTotalLength(); pathEl.style.strokeDasharray = len; pathEl.style.strokeDashoffset = len * (1 - clamp(p));
  };
  // wobbly hand-drawn polyline through points with deterministic jitter → SVG path d
  L.sketchPath = (pts, seed = 1, jitter = 1.6, closed = false) => {
    const r = L.rng(seed), P = pts.map(p => [p[0] + (r() - .5) * jitter * 2, p[1] + (r() - .5) * jitter * 2]);
    let d = `M${P[0][0].toFixed(1)} ${P[0][1].toFixed(1)}`;
    for (let i = 1; i < P.length; i++) { const a = P[i - 1], b = P[i], mx = (a[0] + b[0]) / 2 + (r() - .5) * jitter, my = (a[1] + b[1]) / 2 + (r() - .5) * jitter; d += ` Q${mx.toFixed(1)} ${my.toFixed(1)} ${b[0].toFixed(1)} ${b[1].toFixed(1)}`; }
    return closed ? d + 'Z' : d;
  };

  /* ───────────────────────── camera (CSS 2D/3D rig) ───────────────────────── */
  // c = Lab.camera(worldEl, {w, h, persp}); c.set({x,y,zoom,rot,rx,ry}) → look at world point (x,y), zoom, roll `rot` rad, tilt rx/ry rad.
  L.camera = (el, o) => {
    const W = o.w, H = o.h, persp = o.persp || 0;
    el.style.transformOrigin = '0 0'; el.style.position = 'absolute'; el.style.left = 0; el.style.top = 0;
    if (persp && el.parentElement) { el.parentElement.style.perspective = persp + 'px'; el.parentElement.style.perspectiveOrigin = '50% 50%'; el.style.transformStyle = 'preserve-3d'; }
    return { set(s) {
      const x = s.x ?? W / 2, y = s.y ?? H / 2, z = s.zoom ?? 1, rot = s.rot ?? 0, rx = s.rx ?? 0, ry = s.ry ?? 0;
      el.style.transform = `translate(${W / 2}px,${H / 2}px) ${persp ? `rotateX(${rx}rad) rotateY(${ry}rad) ` : ''}rotate(${rot}rad) scale(${z}) translate(${-x}px,${-y}px)`;
    } };
  };
  // deterministic camera shake. Use as: const s = Lab.shake(t, {t0:4.15, amp:22, decay:.5, freq:18, seed:3}); x+=s.x; y+=s.y; rot+=s.r
  L.shake = (t, o = {}) => {
    const n = L.shake._n || (L.shake._n = L.noise(77)); const t0 = o.t0 ?? 0, amp = o.amp ?? 10, f = o.freq ?? 14, decay = o.decay ?? Infinity, seed = o.seed ?? 0;
    const e = t < t0 ? 0 : (isFinite(decay) ? Math.exp(-(t - t0) / decay) : 1);
    return { x: amp * e * n.n2(t * f, seed * 13.1), y: amp * e * n.n2(t * f + 40, seed * 7.7 + 5), r: (amp / 900) * e * n.n2(t * f + 80, seed * 3.3 + 9) };
  };
  // handheld drift: slow organic camera sway (always on, tiny). Returns {x,y,r,z}
  L.handheld = (t, amp = 6, seed = 1) => { const n = L.handheld._n || (L.handheld._n = L.noise(5)); return { x: amp * n.n2(t * .35, seed), y: amp * n.n2(t * .31 + 10, seed + 3), r: amp / 1500 * n.n2(t * .27 + 20, seed + 6), z: 1 + amp / 2000 * n.n2(t * .22 + 30, seed + 9) }; };

  /* ───────────────────────── loops ───────────────────────── */
  L.loop = {
    phase: (t, dur) => L.mod(t, dur) / dur,                                // 0..1 across the whole video
    cycles: (t, dur, n = 1) => TAU * n * L.mod(t, dur) / dur,              // angle for sin/cos with n whole cycles per video
    // cross-fade: value a(t) at the end blends into a(t - dur) so frame dur == frame 0 even for non-periodic motion
    blend: (fn, t, dur, fade = 1) => { if (t < dur - fade) return fn(t); const k = L.smoothstep(dur - fade, dur, t); return fn(t) * (1 - k) + fn(t - dur) * k; }
  };

  /* ───────────────────────── events (bridge to sound) ───────────────────────── */
  root.EVENTS = root.EVENTS || [];
  L.ev = (t, type, o = {}) => { root.EVENTS.push(Object.assign({ t: +(+t).toFixed(4), type }, o)); root.EVENTS.sort((a, b) => a.t - b.t); return t; };
  L.evBeats = (type, bpm, dur, offset = 0, sub = 1, o = {}) => L.beatTimes(bpm, dur, offset, sub).forEach(t => L.ev(t, type, o));

  /* ───────────────────────── scene sequencer ─────────────────────────
   * const sq = Lab.sequence([{id:'intro', start:0, dur:2.4, el:el1, draw:(lt,u)=>{...}}, ...], {fade:0})
   * sq(t) → shows scenes whose window contains t (with 1 frame overlap tolerance), calls draw(localTime, u). */
  L.sequence = (list, o = {}) => t => {
    for (const s of list) {
      const on = t >= s.start && t < s.start + s.dur + (o.hold || 0);
      if (s.el) s.el.style.display = on ? '' : 'none';
      if (on && s.draw) s.draw(t - s.start, clamp((t - s.start) / s.dur), t);
    }
  };
  // layout a list of durations back to back → [{start,dur}, ...] (+ optional overlap for transitions)
  L.chain = (durs, overlap = 0) => { let t = 0; return durs.map(d => { const s = { start: t, dur: d }; t += d - overlap; return s; }); };

  /* ───────────────────────── init: video contract + preview player ───────────────────────── */
  L.init = (o) => {
    const V = root.VIDEO = { w: o.w || 1080, h: o.h || 1920, duration: o.duration || 10, fps: o.fps || 30 };
    const isRender = /[?&]render/.test(location.search);
    const stage = o.stage || document.getElementById('stage') || (() => { const s = document.createElement('div'); s.id = 'stage'; document.body.appendChild(s); return s; })();
    Object.assign(stage.style, { position: 'relative', width: V.w + 'px', height: V.h + 'px', overflow: 'hidden', background: o.bg || '#000' });
    Object.assign(document.documentElement.style, { margin: 0, background: isRender ? '#000' : '#0d0d0d' }); document.body.style.margin = '0';
    const draw = o.render;
    root.seek = (t) => { t = o.loop ? L.mod(t, V.duration) : clamp(t, 0, V.duration); L.t = t; draw(t); };
    root.__ready = false;
    const go = () => { root.seek(0); root.__ready = true; };
    (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(() => (o.ready ? Promise.resolve(o.ready()).then(go) : go()));
    if (isRender) return;
    // ---- preview player (never used in render) ----
    const wrap = document.createElement('div'); Object.assign(wrap.style, { position: 'fixed', left: '50%', top: 'calc(50% - 22px)', transformOrigin: '50% 50%' });
    stage.parentElement.insertBefore(wrap, stage); wrap.appendChild(stage);
    const bar = document.createElement('div'); bar.style.cssText = 'position:fixed;left:0;right:0;bottom:0;height:44px;display:flex;gap:10px;align-items:center;padding:0 14px;background:#161616;color:#ddd;font:12px ui-monospace,monospace;z-index:99999';
    bar.innerHTML = '<button id="lp" style="background:#333;color:#fff;border:0;padding:6px 12px;border-radius:6px;cursor:pointer">play</button><input id="ls" type="range" min="0" max="1000" value="0" style="flex:1"><span id="lt" style="min-width:140px;text-align:right"></span>';
    document.body.appendChild(bar);
    const fit = () => { const k = Math.min((innerWidth - 20) / V.w, (innerHeight - 70) / V.h); wrap.style.transform = `translate(-50%,-50%) translate(${0}px,${V.h * k / 2 - V.h * k / 2}px) scale(${k})`; wrap.style.marginTop = 0; wrap.style.top = `calc(50% - 22px)`; };
    addEventListener('resize', fit); fit();
    let playing = false, t0 = 0, base = 0, cur = 0; const audio = o.audio ? new Audio(o.audio) : null;
    const show = t => { cur = t; root.seek(t); document.getElementById('ls').value = String(Math.round(1000 * t / V.duration)); document.getElementById('lt').textContent = `${t.toFixed(2)}s / ${V.duration}s · f${Math.round(t * V.fps)}`; };
    const tick = ts => { if (!playing) return; const t = base + (ts - t0) / 1000; if (t >= V.duration && !o.loop) { playing = false; document.getElementById('lp').textContent = 'play'; show(V.duration); return; } show(L.mod(t, V.duration)); requestAnimationFrame(tick); };
    document.getElementById('lp').onclick = () => { playing = !playing; document.getElementById('lp').textContent = playing ? 'pause' : 'play'; if (playing) { base = cur >= V.duration ? 0 : cur; t0 = performance.now(); if (audio) { audio.currentTime = base; audio.play(); } requestAnimationFrame(tick); } else if (audio) audio.pause(); };
    document.getElementById('ls').oninput = e => { playing = false; if (audio) audio.pause(); document.getElementById('lp').textContent = 'play'; show(e.target.value / 1000 * V.duration); };
    addEventListener('keydown', e => { if (e.code === 'Space') { e.preventDefault(); document.getElementById('lp').click(); } if (e.code === 'ArrowRight') show(clamp(cur + 1 / V.fps, 0, V.duration)); if (e.code === 'ArrowLeft') show(clamp(cur - 1 / V.fps, 0, V.duration)); });
    (document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve()).then(() => show(0));
  };

  root.Lab = L;
})(typeof window !== 'undefined' ? window : globalThis);
