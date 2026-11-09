/* rig.js - Rig: tiny procedural 2D character rigs for Canvas 2D. NO images. Needs lab.js. Every function is a pure function of (t, options): loops exactly when `loop` (s) is given.
 *
 *   Rig.biped(ctx, t, {x,y,scale,face,action,speed,pal,style,hat,seed,loop,...})   walking/idle/wave/jump/point/dance figure with 2-bone IK legs & arms
 *   Rig.blob (ctx, t, {x,y,scale,action,pal,...})    squash-and-stretch creature (hop, bounce, idle, look)
 *   Rig.bot  (ctx, t, {x,y,scale,action,pal,...})    hovering robot (head tilt, antenna spring, LED face, talk)
 *   Rig.face (ctx, x, y, size, {look:[dx,dy], blink:0..1, mood:'happy'|'sad'|'surprised'|'angry'|'neutral', mouth:0..1, ink, white})   reusable eyes + mouth
 *   Rig.blink(t, seed, period)  -> 0..1 closure   |  Rig.talk(t, t0, t1, seed, rate) -> 0..1 mouth openness (syllable-like, deterministic)
 *   Rig.ik2(ax, ay, l1, l2, tx, ty, bend) -> {x,y,hx,hy} (knee/elbow + clamped end point)
 *   Rig.groundShadow(ctx, x, y, w, k)   |  Rig.pal(dnaPalette) -> {skin,cloth,cloth2,accent,line,white,hair}
 * action (biped): 'walk' | 'run' | 'idle' | 'wave' | 'jump' | 'point' | 'dance' | 'sit-bob'   (params: speed cycles/s, t0/dur for jump, target:[x,y] for point (world coords))
 * style: 'flat' (no outline) | 'outline' (thick dark outline, sticker look) | 'cutout' (outline + white rim)
 * Events: call Rig.steps(t0,t1,speed,{type:'tick'}) at build time to register a footstep event per foot-down (sound sync).
 */
(function (root) {
  'use strict';
  const L = root.Lab, TAU = Math.PI * 2, R = {};
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), lerp = (a, b, k) => a + (b - a) * k, mod = (a, n) => ((a % n) + n) % n;
  const smooth = x => x * x * (3 - 2 * x);

  R.pal = function (p) {
    p = p || {}; const s = p.support || [];
    return { skin: p.skin || '#f2c9a5', cloth: p.accent || '#e8553f', cloth2: p.accent2 || '#2f66d0', accent: p.accent || '#f4c542', line: p.ink || '#1a1512', white: '#fffaf0', hair: s[0] || '#3a2418' };
  };
  R.ik2 = function (ax, ay, l1, l2, tx, ty, bend = 1) {
    let dx = tx - ax, dy = ty - ay, d = Math.hypot(dx, dy); const max = l1 + l2 - .001, min = Math.abs(l1 - l2) + .001;
    if (d > max) { dx *= max / d; dy *= max / d; d = max; } if (d < min) { const k = d ? min / d : 1; dx *= k; dy *= k; d = min; }
    const a = Math.atan2(dy, dx), c = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), ang = a + bend * Math.acos(clamp(c, -1, 1));
    return { x: ax + Math.cos(ang) * l1, y: ay + Math.sin(ang) * l1, hx: ax + dx, hy: ay + dy };
  };
  R.blink = function (t, seed = 1, period = 3.2) { // closes briefly once per `period` (jittered per cycle). returns 0 open .. 1 closed
    const n = Math.floor(t / period), r = L.rng(seed * 97 + n * 13)(), at = n * period + period * (.25 + .6 * r), d = t - at; if (d < 0 || d > .16) return 0; return Math.sin(d / .16 * Math.PI);
  };
  R.talk = function (t, t0, t1, seed = 1, rate = 7) { // syllable stream: open amount changes ~rate times/s, each syllable has its own size
    if (t < t0 || t > t1) return 0; const k = Math.floor((t - t0) * rate), f = ((t - t0) * rate) % 1, v = L.rng(seed * 31 + k)(); return (v < .18 ? .08 : .25 + v * .75) * Math.sin(Math.min(1, f * 1.15) * Math.PI) ;
  };
  R.groundShadow = function (ctx, x, y, w, k = 1) { ctx.save(); ctx.translate(x, y); ctx.scale(1, .18); const g = ctx.createRadialGradient(0, 0, 0, 0, 0, w / 2); g.addColorStop(0, `rgba(0,0,0,${.32 * k})`); g.addColorStop(1, 'rgba(0,0,0,0)'); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(0, 0, w / 2, 0, TAU); ctx.fill(); ctx.restore(); };

  /* ---------- drawing helpers ---------- */
  function limb(ctx, pts, w, color, style, line) { // thick rounded polyline with optional outline
    const path = () => { ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); for (let i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]); };
    ctx.lineCap = ctx.lineJoin = 'round';
    if (style !== 'flat') { path(); ctx.lineWidth = w + (style === 'cutout' ? 14 : 8); ctx.strokeStyle = style === 'cutout' ? '#fffaf0' : line; ctx.stroke(); if (style === 'cutout') { path(); ctx.lineWidth = w + 6; ctx.strokeStyle = line; ctx.stroke(); } }
    path(); ctx.lineWidth = w; ctx.strokeStyle = color; ctx.stroke();
  }
  function shape(ctx, drawPath, fill, style, line, lw = 4) {
    if (style === 'cutout') { drawPath(); ctx.lineWidth = lw * 3.2; ctx.strokeStyle = '#fffaf0'; ctx.lineJoin = 'round'; ctx.stroke(); }
    drawPath(); ctx.fillStyle = fill; ctx.fill(); if (style !== 'flat') { ctx.lineWidth = lw; ctx.strokeStyle = line; ctx.lineJoin = 'round'; ctx.stroke(); }
  }
  const rr = (ctx, x, y, w, h, r) => { ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); };

  /* ---------- face ---------- */
  R.face = function (ctx, x, y, size, o = {}) {
    const look = o.look || [0, 0], bl = o.blink || 0, ink = o.ink || '#1a1512', white = o.white || '#fffaf0', mood = o.mood || 'happy', mouth = o.mouth == null ? .0 : o.mouth, ew = size * .22, eh = size * .26 * (1 - bl * .92);
    ctx.save(); ctx.translate(x, y);
    [-1, 1].forEach(sx => {
      const ex = sx * size * .3; ctx.fillStyle = white; ctx.beginPath(); ctx.ellipse(ex, 0, ew, Math.max(1.2, eh), 0, 0, TAU); ctx.fill(); ctx.lineWidth = size * .04; ctx.strokeStyle = ink; ctx.stroke();
      if (bl < .85) { ctx.fillStyle = ink; ctx.beginPath(); ctx.ellipse(ex + look[0] * ew * .6, look[1] * eh * .6, ew * .45, Math.max(1, eh * .5), 0, 0, TAU); ctx.fill(); }
      ctx.strokeStyle = ink; ctx.lineWidth = size * .05; ctx.lineCap = 'round';
      if (mood === 'angry') { ctx.beginPath(); ctx.moveTo(ex - sx * ew, -eh * 1.6 - sx * 0); ctx.lineTo(ex + sx * ew * 1.1, -eh * 1.05 + 0); ctx.stroke(); ctx.beginPath(); ctx.moveTo(ex - sx * ew, -eh * 1.0); ctx.lineTo(ex + sx * ew * 1.1, -eh * 1.7); ctx.stroke(); }
      else if (mood === 'sad') { ctx.beginPath(); ctx.moveTo(ex - sx * ew, -eh * 1.2); ctx.lineTo(ex + sx * ew, -eh * 1.7); ctx.stroke(); }
      else if (mood === 'surprised') { ctx.beginPath(); ctx.arc(ex, -eh * 1.7, ew * .9, Math.PI * 1.1, Math.PI * 1.9); ctx.stroke(); }
    });
    const my = size * .62, mw = size * .34; ctx.strokeStyle = ink; ctx.lineWidth = size * .06; ctx.lineCap = 'round'; ctx.fillStyle = '#7a2420';
    if (mouth > .06 || mood === 'surprised') { const oh = Math.max(size * .05, mouth * size * .34) + (mood === 'surprised' ? size * .1 : 0); ctx.beginPath(); ctx.ellipse(0, my, mw * (mood === 'surprised' ? .55 : .85), oh, 0, 0, TAU); ctx.fill(); ctx.stroke(); }
    else { ctx.beginPath(); if (mood === 'happy') { ctx.moveTo(-mw, my - size * .05); ctx.quadraticCurveTo(0, my + size * .22, mw, my - size * .05); } else if (mood === 'sad') { ctx.moveTo(-mw, my + size * .08); ctx.quadraticCurveTo(0, my - size * .12, mw, my + size * .08); } else { ctx.moveTo(-mw * .7, my); ctx.lineTo(mw * .7, my); } ctx.stroke(); }
    ctx.restore();
  };

  /* ---------- biped ---------- */
  R.biped = function (ctx, t, o = {}) {
    const S = (o.scale || 1), face = o.face === -1 ? -1 : 1, pal = o.pal || R.pal(), style = o.style || 'outline', act = o.action || 'idle', sp = o.speed == null ? (act === 'run' ? 2.4 : 1.2) : o.speed, seed = o.seed || 1;
    const loopT = o.loop ? o.loop : 0, ph = TAU * sp * t;   // loops exactly if sp*loop is an integer
    const U = { l1: 62, l2: 62, torso: 96, head: 40, a1: 46, a2: 46, lw: 20, aw: 15 };
    const hipRest = (U.l1 + U.l2) * .93; let hipX = 0, hipY = -hipRest, lean = 0, headTilt = 0, mouth = o.mouth || 0, mood = o.mood || 'happy', look = o.look || [face * .6, 0];
    const feet = [[0, 0], [0, 0]], hands = [[0, 0], [0, 0]], stride = (act === 'run' ? 58 : 40) * (o.stride || 1), lift = act === 'run' ? 34 : 20; let squash = 1, jumpY = 0;
    const sw = (a) => Math.sin(a);
    if (act === 'walk' || act === 'run') {
      const bob = Math.abs(sw(ph)) * (act === 'run' ? 14 : 7); hipY = -hipRest + bob * (act === 'run' ? 1 : .6) * 1; lean = (act === 'run' ? .16 : .05) * face;
      for (let i = 0; i < 2; i++) { const p = ph + i * Math.PI; const fx = sw(p) * stride; const fy = Math.max(0, -Math.cos(p)) * lift * (act === 'run' ? 1.4 : 1); feet[i] = [fx, -fy]; hands[i] = [-sw(p) * (act === 'run' ? 66 : 48), U.a1 + U.a2 - 22 - (act === 'run' ? 30 : 0) - Math.abs(sw(p)) * 6]; }
      hipX = Math.sin(ph) * 2; headTilt = Math.sin(ph * 2) * .02;
    } else if (act === 'jump') {
      const t0 = o.t0 || 0, d = o.dur || .8, k = clamp((t - t0) / d), crouch = k < .18 ? smooth(k / .18) : (k > .85 ? smooth((1 - k) / .15) : 0), air = k >= .18 && k <= .85 ? (k - .18) / .67 : 0;
      jumpY = -Math.sin(air * Math.PI) * (o.height || 220); squash = 1 - crouch * .18 + (air > 0 && air < 1 ? .1 * Math.sin(air * Math.PI) : 0); hipY = -hipRest + crouch * 26 + jumpY;
      const tuck = air > 0 ? Math.sin(air * Math.PI) : 0; feet[0] = [-18, -tuck * 36 + (crouch ? 0 : 0)]; feet[1] = [18, -tuck * 46]; hands[0] = [-34, U.a1 + U.a2 - 40 - tuck * 70]; hands[1] = [34, U.a1 + U.a2 - 40 - tuck * 70]; mood = air > 0 ? 'surprised' : mood; mouth = air > 0 ? .5 : 0;
    } else if (act === 'dance') {
      const b = ph * 1; hipY = -hipRest + Math.abs(sw(b)) * 12; hipX = sw(b) * 14; lean = sw(b) * .09;
      feet[0] = [-24 + sw(b) * 6, -Math.max(0, sw(b * 1)) * 22]; feet[1] = [24 + sw(b) * 6, -Math.max(0, -sw(b)) * 22];
      hands[0] = [-52 - sw(b) * 12, -40 - Math.abs(sw(b)) * 60]; hands[1] = [52 - sw(b) * 12, -40 - Math.abs(sw(b + 1.5)) * 60]; mood = 'happy'; mouth = .25 + .2 * Math.abs(sw(b));
    } else { // idle / wave / point / sit-bob
      const br = sw(TAU * (sp * .35) * t); hipY = -hipRest + (act === 'sit-bob' ? 18 : 0) + br * 1.6; feet[0] = [-22, 0]; feet[1] = [22, 0]; hands[0] = [-34, U.a1 + U.a2 - 30 + br * 2]; hands[1] = [34, U.a1 + U.a2 - 30 + br * 2];
      if (act === 'wave') { const wv = sw(TAU * 2.2 * t); hands[1] = [face * 0 + 48 + wv * 16, -90 - 30 + wv * 4 + 20]; hands[1][0] *= face; hands[0][0] *= 1; }
      if (act === 'point') { const tg = o.target || [face * 300, -100]; hands[1] = [(tg[0] - (o.x || 0)) / S, (tg[1] - ((o.y || 0) + hipY * S - U.torso * S * .85)) / S]; look = [face * .9, -.2]; }
    }
    // ---- build skeleton in character space (origin = ground under hips; y up is negative) ----
    ctx.save(); ctx.translate(o.x || 0, (o.y || 0)); ctx.scale(S * face, S);
    R.groundShadow(ctx, hipX, 0, 150, clamp(1 + jumpY / 400, .3, 1));
    const hip = [hipX, hipY], sh = [hipX + Math.sin(lean) * U.torso, hipY - Math.cos(lean) * U.torso * squash], hd = [sh[0] + Math.sin(lean) * 8 + Math.sin(headTilt) * 10, sh[1] - U.head * .95];
    const pose = i => { const side = i ? 1 : -1, hipJ = [hip[0] + side * 9, hip[1]], k = R.ik2(hipJ[0], hipJ[1], U.l1, U.l2, feet[i][0] + side * (act === 'idle' ? 0 : 0), feet[i][1], 1); return { hipJ, k }; };
    // back leg & arm first
    const legs = [0, 1].map(pose), order = (feet[0][0] < feet[1][0]) ? [0, 1] : [1, 0];
    const shoulder = [sh[0], sh[1] + 10];
    const arms = [0, 1].map(i => { const ax = shoulder[0] + (i ? 8 : -8), ay = shoulder[1]; const tgt = [ax + hands[i][0], ay + hands[i][1]]; return R.ik2(ax, ay, U.a1, U.a2, tgt[0], tgt[1], i ? -1 : 1); });
    const armPts = i => { const a = arms[i], ax = shoulder[0] + (i ? 8 : -8), ay = shoulder[1]; return [[ax, ay], [a.x, a.y], [a.hx, a.hy]]; };
    const legPts = i => { const l = legs[i]; return [[l.hipJ[0], l.hipJ[1]], [l.k.x, l.k.y], [l.k.hx, l.k.hy]]; };
    const col2 = pal.cloth2, skin = pal.skin;
    limb(ctx, armPts(0), U.aw, pal.cloth, style, pal.line);
    limb(ctx, legPts(order[0]), U.lw, col2, style, pal.line);
    // shoes
    const shoe = i => { const f = legs[i].k; shape(ctx, () => { ctx.beginPath(); ctx.ellipse(f.hx + 8, f.hy - 4, 17, 9, 0, 0, TAU); }, pal.line === '#1a1512' ? pal.accent : pal.line, style, pal.line, 3); };
    shoe(order[0]);
    limb(ctx, legPts(order[1]), U.lw, col2, style, pal.line); shoe(order[1]);
    // torso
    shape(ctx, () => { ctx.save(); ctx.translate(hip[0], hip[1]); ctx.rotate(lean); rr(ctx, -27, -U.torso * squash, 54, U.torso * squash + 6, 22); ctx.restore(); }, pal.cloth, style, pal.line, 4);
    // neck/head
    shape(ctx, () => { ctx.beginPath(); ctx.arc(hd[0], hd[1], U.head, 0, TAU); }, skin, style, pal.line, 4);
    if (o.hat !== 'none') { ctx.save(); ctx.translate(hd[0], hd[1]); ctx.rotate(headTilt); const hc = pal.hair; if (o.hat === 'cap') { shape(ctx, () => { ctx.beginPath(); ctx.arc(0, -4, U.head * 1.02, Math.PI, 0); ctx.closePath(); }, pal.accent, style, pal.line, 4); shape(ctx, () => rr(ctx, 4, -8, U.head * 1.1, 10, 5), pal.accent, style, pal.line, 3); } else if (o.hat === 'antenna') { ctx.strokeStyle = pal.line; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(0, -U.head); ctx.lineTo(Math.sin(t * 4) * 5, -U.head - 24); ctx.stroke(); ctx.fillStyle = pal.accent; ctx.beginPath(); ctx.arc(Math.sin(t * 4) * 5, -U.head - 28, 8, 0, TAU); ctx.fill(); } else { shape(ctx, () => { ctx.beginPath(); ctx.ellipse(0, -U.head * .55, U.head * 1.02, U.head * .62, 0, Math.PI, 0); ctx.closePath(); }, hc, style, pal.line, 4); } ctx.restore(); }
    R.face(ctx, hd[0] + face * 4 * 0, hd[1] + 2, U.head * 1.15, { look: [look[0] * face, look[1]], blink: R.blink(t, seed), mood, mouth, ink: pal.line, white: pal.white });
    limb(ctx, armPts(1), U.aw, pal.cloth, style, pal.line);
    [0, 1].forEach(i => { const a = arms[i]; shape(ctx, () => { ctx.beginPath(); ctx.arc(a.hx, a.hy, 10, 0, TAU); }, skin, style, pal.line, 3); });
    ctx.restore();
  };
  /* footstep events for a walk segment: one event per foot-down (when sin(ph) crosses zero => foot passes under hip, planted at -cos<=0 ...) */
  R.steps = function (t0, t1, speed = 1.2, o = {}) { const type = o.type || 'tick', per = 1 / (speed * 2); for (let t = t0 + per * (o.offset == null ? .0 : o.offset); t < t1; t += per) L.ev(t, type, { intensity: o.intensity == null ? .3 : o.intensity, pan: o.pan || 0, label: 'step' }); };

  /* ---------- blob creature ---------- */
  R.blob = function (ctx, t, o = {}) {
    const S = o.scale || 1, pal = o.pal || R.pal(), style = o.style || 'outline', act = o.action || 'hop', per = o.period || 1.2, seed = o.seed || 1, n = L.noise(seed * 5 + 1);
    const ph = mod(t / per, 1); let sx = 1, sy = 1, y = 0, look = o.look || [Math.sin(TAU * t / (o.loop || 6)) * .7, 0], mouth = o.mouth || 0, mood = o.mood || 'happy';
    if (act === 'hop') { const air = ph < .6 ? ph / .6 : 0, crouch = ph < .6 ? 0 : Math.sin((ph - .6) / .4 * Math.PI); y = -Math.sin(air * Math.PI) * (o.height || 200); const stretch = air > 0 ? Math.sin(air * Math.PI) * .22 : 0; sy = 1 + stretch - crouch * .28; sx = 1 / sy; mood = air > 0 ? 'surprised' : 'happy'; }
    else if (act === 'bounce') { const k = Math.abs(Math.sin(Math.PI * t / per)); y = -k * (o.height || 120); sy = 1 + (1 - k) * -.22 + k * .12; sx = 1 / sy; }
    else { const br = Math.sin(TAU * t / (per * 2.4)); sy = 1 + br * .03; sx = 1 / sy; }
    ctx.save(); ctx.translate(o.x || 0, o.y || 0); R.groundShadow(ctx, 0, 0, 220 * S, clamp(1 + y / 300, .35, 1)); ctx.translate(0, y * S); ctx.scale(S * sx, S * sy);
    const body = () => { ctx.beginPath(); const N = 48; for (let i = 0; i <= N; i++) { const a = i / N * TAU, w = 1 + .05 * n.n2(Math.cos(a) * 1.5 + 2, Math.sin(a) * 1.5 + t * .3 * 0) + .04 * Math.sin(a * 3 + t * 2), rx = 92 * w, ry = 100 * w, flat = a > .3 && a < Math.PI - .3 ? .88 : 1; const px = Math.cos(a) * rx, py = -100 + Math.sin(a) * ry * flat; ctx[i ? 'lineTo' : 'moveTo'](px, py); } ctx.closePath(); };
    shape(ctx, body, pal.cloth, style, pal.line, 5);
    ctx.save(); body(); ctx.clip(); ctx.fillStyle = 'rgba(255,255,255,.16)'; ctx.beginPath(); ctx.ellipse(-30, -150, 36, 22, -.5, 0, TAU); ctx.fill(); ctx.fillStyle = 'rgba(0,0,0,.12)'; ctx.beginPath(); ctx.ellipse(30, -22, 100, 40, 0, 0, TAU); ctx.fill(); ctx.restore();
    R.face(ctx, 0, -112, 108, { look, blink: R.blink(t, seed), mood, mouth, ink: pal.line, white: pal.white });
    // feet
    [-1, 1].forEach(s => shape(ctx, () => { ctx.beginPath(); ctx.ellipse(s * 40, -4, 22, 10, 0, 0, TAU); }, pal.cloth2, style, pal.line, 4));
    ctx.restore();
  };

  /* ---------- hovering robot ---------- */
  R.bot = function (ctx, t, o = {}) {
    const S = o.scale || 1, pal = o.pal || R.pal(), style = o.style || 'outline', seed = o.seed || 1, loop = o.loop || 6, act = o.action || 'hover';
    const hov = Math.sin(TAU * t / (o.hoverPeriod || 2.4)) * 10, tilt = Math.sin(TAU * t / loop * 1) * .06 + (act === 'nod' ? Math.sin(TAU * t * 2) * .08 : 0), mouth = o.mouth || 0, ant = Math.sin(TAU * t / (o.hoverPeriod || 2.4) - .9) * 9;
    ctx.save(); ctx.translate(o.x || 0, o.y || 0); R.groundShadow(ctx, 0, 0, 200 * S, clamp(1 - hov / 60, .4, 1)); ctx.translate(0, (-70 + hov) * S); ctx.scale(S, S);
    // thruster glow
    const g = ctx.createRadialGradient(0, 60, 0, 0, 60, 60); g.addColorStop(0, 'rgba(255,220,120,.9)'); g.addColorStop(1, 'rgba(255,160,60,0)'); ctx.fillStyle = g; ctx.beginPath(); ctx.ellipse(0, 70 + Math.sin(t * 30) * 0, 40, 24 + Math.sin(TAU * t * 5) * 3, 0, 0, TAU); ctx.fill();
    // arms (2-bone IK waving slightly)
    [-1, 1].forEach(s => { const sh = [s * 62, 0], tg = [s * (96 + Math.sin(TAU * t / loop + s) * 6), 46 + Math.sin(TAU * t * .5 / (o.hoverPeriod || 2.4) + s) * 6]; const k = R.ik2(sh[0], sh[1], 34, 34, tg[0], tg[1], -s); limb(ctx, [sh, [k.x, k.y], [k.hx, k.hy]], 12, pal.cloth2, style, pal.line); shape(ctx, () => { ctx.beginPath(); ctx.arc(k.hx, k.hy, 11, 0, TAU); }, pal.accent, style, pal.line, 3); });
    shape(ctx, () => rr(ctx, -64, -44, 128, 110, 26), pal.cloth, style, pal.line, 5);
    // chest panel
    ctx.fillStyle = 'rgba(0,0,0,.22)'; rr(ctx, -34, 14, 68, 30, 10); ctx.fill(); for (let i = 0; i < 4; i++) { ctx.fillStyle = [pal.accent, '#7ee0a8', '#f06a6a', '#8fd0ff'][i]; ctx.globalAlpha = .55 + .45 * (Math.sin(TAU * t / (loop / (i + 1)) ) > 0 ? 1 : 0); ctx.beginPath(); ctx.arc(-22 + i * 15, 29, 5, 0, TAU); ctx.fill(); } ctx.globalAlpha = 1;
    // head
    ctx.save(); ctx.translate(0, -62); ctx.rotate(tilt); ctx.strokeStyle = pal.line; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(0, -52); ctx.lineTo(ant * .6, -76); ctx.stroke(); shape(ctx, () => { ctx.beginPath(); ctx.arc(ant * .6, -82, 9, 0, TAU); }, pal.accent, style, pal.line, 3);
    shape(ctx, () => rr(ctx, -66, -52, 132, 104, 34), pal.cloth2, style, pal.line, 5); ctx.fillStyle = '#10151c'; rr(ctx, -50, -34, 100, 68, 24); ctx.fill();
    // LED face (eyes = rounded bars; mouth = equaliser)
    const bl = R.blink(t, seed, 3.6), ey = -8, ew = 15, eh = 18 * (1 - bl * .9); ctx.fillStyle = pal.accent; [-1, 1].forEach(s => { ctx.beginPath(); ctx.ellipse(s * 22, ey, ew, Math.max(1.5, eh), 0, 0, TAU); ctx.fill(); });
    const bars = 5; for (let i = 0; i < bars; i++) { const h = 3 + mouth * 20 * (.5 + .5 * Math.sin(i * 1.9 + Math.floor(t * 14) * 1.3)); ctx.fillRect(-26 + i * 11, 20 - h / 2, 7, h); }
    ctx.restore(); ctx.restore();
  };
  root.Rig = R;
})(typeof window !== 'undefined' ? window : globalThis);
