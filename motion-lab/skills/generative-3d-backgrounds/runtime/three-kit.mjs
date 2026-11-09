/* three-kit.mjs — deterministic three.js helpers for motion-lab (ES module; three r160 vendored next to it in vendor/).
 *   import * as THREE from './vendor/three.module.min.js';
 *   import { Stage, studioEnv, clay, glass, metal, emissive, roundedBox, iconFromPath, pillShape, ring, scatter } from './three-kit.mjs';
 *   const st = new Stage(THREE, { w:1080, h:1920, bg:'#0b0d12', fov:32 });   // renderer + scene + camera + studio lighting
 *   st.add(mesh); st.cam(pos, target); st.render(); ctx.drawImage(st.canvas, 0, 0);  // call st.render() inside seek(t) AFTER setting every transform from t
 * Rules: never use clocks; every object transform is a pure function of t; no shadows maps larger than 1024; antialias OFF in SwiftShader for speed, supersample by rendering at 1.5x if needed.
 */
export function studioEnv(THREE, renderer, { top = '#ffffff', mid = '#8fa0c0', bottom = '#10131a', key = '#fff4e0' } = {}) {
  const c = document.createElement('canvas'); c.width = 1024; c.height = 512; const g = c.getContext('2d');
  const gr = g.createLinearGradient(0, 0, 0, 512); gr.addColorStop(0, top); gr.addColorStop(.5, mid); gr.addColorStop(1, bottom); g.fillStyle = gr; g.fillRect(0, 0, 1024, 512);
  g.fillStyle = key; g.filter = 'blur(10px)'; g.fillRect(180, 70, 220, 90); g.fillRect(700, 120, 40, 260); g.fillStyle = '#ffffff'; g.fillRect(480, 40, 120, 20);      // softboxes + strip light
  const tex = new THREE.CanvasTexture(c); tex.mapping = THREE.EquirectangularReflectionMapping; tex.colorSpace = THREE.SRGBColorSpace;
  const pm = new THREE.PMREMGenerator(renderer); const env = pm.fromEquirectangular(tex).texture; pm.dispose(); tex.dispose(); return env;
}
export class Stage {
  constructor(THREE, { w = 1080, h = 1920, bg = '#0b0d12', fov = 32, env = {}, transparent = false, scale = 1, exposure = 1 } = {}) {
    this.THREE = THREE; this.w = w; this.h = h;
    const r = this.renderer = new THREE.WebGLRenderer({ antialias: false, alpha: transparent, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
    r.setPixelRatio(1); r.setSize(w * scale, h * scale, false); r.toneMapping = THREE.ACESFilmicToneMapping; r.toneMappingExposure = exposure; r.outputColorSpace = THREE.SRGBColorSpace;
    this.canvas = r.domElement; this.scene = new THREE.Scene(); if (!transparent) this.scene.background = new THREE.Color(bg);
    this.scene.environment = studioEnv(THREE, r, env);
    this.camera = new THREE.PerspectiveCamera(fov, w / h, .1, 200); this.camera.position.set(0, 0, 8);
    this.key = new THREE.DirectionalLight('#fff2e0', 2.2); this.key.position.set(-3, 5, 4); this.scene.add(this.key);
    this.fill = new THREE.DirectionalLight('#9bb8ff', .6); this.fill.position.set(4, 1, 2); this.scene.add(this.fill);
    this.rim = new THREE.DirectionalLight('#ffffff', 1.2); this.rim.position.set(0, 3, -5); this.scene.add(this.rim);
  }
  add(...o) { o.forEach(x => this.scene.add(x)); return this; }
  cam(pos, target = [0, 0, 0], fov) { this.camera.position.set(...pos); this.camera.lookAt(...target); if (fov) { this.camera.fov = fov; } this.camera.updateProjectionMatrix(); return this; }
  fog(color, near, far) { this.scene.fog = new this.THREE.Fog(color, near, far); return this; }
  render() { this.renderer.render(this.scene, this.camera); return this.canvas; }
}
// ---- materials (all MeshPhysical, deterministic) ----
export const clay = (T, color = '#e8dcc8', rough = .75) => new T.MeshPhysicalMaterial({ color, roughness: rough, metalness: 0, clearcoat: .15, clearcoatRoughness: .6, sheen: .6, sheenColor: new T.Color('#fff3e0'), sheenRoughness: .8 });
export const glass = (T, color = '#bfe3ff', { transmission = .92, thickness = 1.4, ior = 1.45, rough = .06 } = {}) => new T.MeshPhysicalMaterial({ color, roughness: rough, metalness: 0, transmission, thickness, ior, clearcoat: 1, clearcoatRoughness: .05, attenuationColor: new T.Color(color), attenuationDistance: 2.2, envMapIntensity: 1.4 });
export const metal = (T, color = '#c8ccd6', rough = .22) => new T.MeshPhysicalMaterial({ color, roughness: rough, metalness: 1, envMapIntensity: 1.6 });
export const emissive = (T, color = '#ff4d2e', k = 2.2) => new T.MeshBasicMaterial({ color: new T.Color(color).multiplyScalar(k), toneMapped: false });
export const plastic = (T, color = '#ffffff', rough = .3) => new T.MeshPhysicalMaterial({ color, roughness: rough, metalness: 0, clearcoat: .8, clearcoatRoughness: .15 });
// ---- geometry ----
export function pillShape(T, w, h, r) { const s = new T.Shape(), x = -w / 2, y = -h / 2; r = Math.min(r, w / 2, h / 2);
  s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r); s.lineTo(x + w, y + h - r); s.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  s.lineTo(x + r, y + h); s.quadraticCurveTo(x, y + h, x, y + h - r); s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y); return s; }
// smooth shading with a crease angle (ExtrudeGeometry is non-indexed -> computeVertexNormals() gives flat facets = "stair-step" banding)
export function creased(T, geo, angle = Math.PI / 4) {
  const g = geo.index ? geo.toNonIndexed() : geo, p = g.attributes.position, n = p.count, cos = Math.cos(angle);
  const fn = new Float32Array(n * 3), a = new T.Vector3(), b = new T.Vector3(), c = new T.Vector3(), e1 = new T.Vector3(), e2 = new T.Vector3();
  const key = i => Math.round(p.getX(i) * 1e4) + ',' + Math.round(p.getY(i) * 1e4) + ',' + Math.round(p.getZ(i) * 1e4), map = new Map();
  for (let i = 0; i < n; i += 3) { a.fromBufferAttribute(p, i); b.fromBufferAttribute(p, i + 1); c.fromBufferAttribute(p, i + 2); e1.subVectors(b, a); e2.subVectors(c, a); e1.cross(e2).normalize();
    for (let k = 0; k < 3; k++) { fn[(i + k) * 3] = e1.x; fn[(i + k) * 3 + 1] = e1.y; fn[(i + k) * 3 + 2] = e1.z; const kk = key(i + k); (map.get(kk) || map.set(kk, []).get(kk)).push(i + k); } }
  const out = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) { const ox = fn[i * 3], oy = fn[i * 3 + 1], oz = fn[i * 3 + 2]; let x = 0, y = 0, z = 0;
    for (const j of map.get(key(i))) { const dx = fn[j * 3], dy = fn[j * 3 + 1], dz = fn[j * 3 + 2]; if (ox * dx + oy * dy + oz * dz >= cos) { x += dx; y += dy; z += dz; } }
    const l = Math.hypot(x, y, z) || 1; out[i * 3] = x / l; out[i * 3 + 1] = y / l; out[i * 3 + 2] = z / l; }
  g.setAttribute('normal', new T.BufferAttribute(out, 3)); return g; }
// Rounded box: subdivided BoxGeometry pushed onto a rounded shape (smooth normals, no stair-steps). r = corner radius.
export function roundedBox(T, w, h, d, r = .08, seg = 10) { r = Math.min(r, w / 2, h / 2, d / 2) * .999; const g = new T.BoxGeometry(w, h, d, seg, seg, seg), p = g.attributes.position, nm = g.attributes.normal, v = new T.Vector3(), q = new T.Vector3();
  const hx = w / 2 - r, hy = h / 2 - r, hz = d / 2 - r;
  for (let i = 0; i < p.count; i++) { v.fromBufferAttribute(p, i); q.set(Math.max(-hx, Math.min(hx, v.x)), Math.max(-hy, Math.min(hy, v.y)), Math.max(-hz, Math.min(hz, v.z))); const o = v.clone().sub(q).normalize();
    p.setXYZ(i, q.x + o.x * r, q.y + o.y * r, q.z + o.z * r); nm.setXYZ(i, o.x, o.y, o.z); }
  return g; }
// icon from SVG-like path: array of ['M',x,y] ['L',x,y] ['Q',cx,cy,x,y] ['C',..] ['Z'] in a unit box (-.5..+.5); returns ExtrudeGeometry with a soft bevel (the "3D glass icon" look)
export function iconFromPath(T, cmds, { depth = .25, bevel = .06, size = 1, segments = 6 } = {}) {
  const s = new T.Shape(); cmds.forEach(c => { const [k, ...a] = c; const f = a.map(v => v * size);
    if (k === 'M') s.moveTo(f[0], f[1]); else if (k === 'L') s.lineTo(f[0], f[1]); else if (k === 'Q') s.quadraticCurveTo(f[0], f[1], f[2], f[3]); else if (k === 'C') s.bezierCurveTo(f[0], f[1], f[2], f[3], f[4], f[5]); else if (k === 'Z') s.closePath(); });
  const g = new T.ExtrudeGeometry(s, { depth, bevelEnabled: true, bevelThickness: bevel, bevelSize: bevel, bevelSegments: segments, curveSegments: 16 }); g.center(); return creased(T, g, Math.PI / 3.2); }
export function ring(T, R = 1, tube = .12, seg = 64) { return new T.TorusGeometry(R, tube, 24, seg); }
// seeded scatter: returns n points [{p:[x,y,z], r, s, c}] in a box/sphere; deterministic from seed
export function scatter(n, seed, { box = [4, 6, 3], minDist = .6 } = {}) {
  let a = seed >>> 0 || 1; const rnd = () => (a = (a * 1664525 + 1013904223) >>> 0) / 4294967296; const pts = []; let tries = 0;
  while (pts.length < n && tries++ < n * 40) { const p = [(rnd() - .5) * box[0], (rnd() - .5) * box[1], (rnd() - .5) * box[2]]; if (pts.every(q => Math.hypot(p[0] - q.p[0], p[1] - q.p[1], p[2] - q.p[2]) > minDist)) pts.push({ p, r: rnd() * 6.283, s: .6 + rnd() * .8, c: rnd() }); }
  return pts; }
// stock icon outlines (unit box): bolt, heart, star, check, play, chat bubble
export const ICONS = {
  bolt: [['M', .08, .5], ['L', -.28, -.04], ['L', -.02, -.04], ['L', -.1, -.5], ['L', .3, .08], ['L', .04, .08], ['Z']],
  heart: [['M', 0, -.42], ['C', -.7, .1, -.4, .52, 0, .22], ['C', .4, .52, .7, .1, 0, -.42], ['Z']],
  star: (() => { const c = [['M', 0, .5]]; for (let i = 1; i < 10; i++) { const a = Math.PI / 2 + i * Math.PI / 5, r = i % 2 ? .2 : .5; c.push(['L', Math.cos(a) * r, Math.sin(a) * r]); } c.push(['Z']); return c; })(),
  check: [['M', -.42, 0], ['L', -.26, -.16], ['L', -.08, -.0], ['L', .26, -.4], ['L', .44, -.24], ['L', -.08, .36], ['Z']],
  play: [['M', -.28, .42], ['L', -.28, -.42], ['L', .42, 0], ['Z']],
  chat: [['M', -.42, .3], ['Q', -.42, .42, -.3, .42], ['L', .3, .42], ['Q', .42, .42, .42, .3], ['L', .42, -.12], ['Q', .42, -.24, .3, -.24], ['L', -.02, -.24], ['L', -.26, -.46], ['L', -.22, -.24], ['L', -.3, -.24], ['Q', -.42, -.24, -.42, -.12], ['Z']]
};
