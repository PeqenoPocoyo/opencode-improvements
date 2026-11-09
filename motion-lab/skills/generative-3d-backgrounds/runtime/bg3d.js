/* bg3d.js — Bg3D: zero-dependency WebGL2 fullscreen-shader engine for procedural 3D-looking backgrounds.
 * One global: window.Bg3D. No images, no clock, no Math.random: every pixel is a pure function of (shader, t, params).
 *
 *   const bg = Bg3D.create(540, 960);                       // WebGL2 canvas, preserveDrawingBuffer
 *   bg.draw('spotlight-dust', t, { seed: 4, palette: ['#07080d', '#1a2238', '#ff9f43', '#ffd8a8', '#fff6e6'] });
 *   ctx.drawImage(bg.canvas, 0, 0, W, H);                   // composite under DOM/canvas text
 *
 * Shader contract (what a shader string must define):   vec3 render(vec2 p, vec2 uv)  -> LINEAR color
 *   p  = (fragCoord - res/2) / min(res.x, res.y), y up  (short side spans -0.5..0.5; 9:16 -> x in +-0.28, y in +-0.5)
 *   uv = fragCoord / res (0..1, y up).   Globals: T (shader time = t*speed), PH, LP, ASPECT, PORTRAIT, SD (seed offsets).
 * The engine multiplies by intensity, optionally vignettes, converts linear->sRGB and adds 1/255 triangular dither.
 *
 * Shader header comments (parsed by the engine):
 *   // @mood  one line      // @use  when to use      // @palette #hex #hex #hex #hex #hex   (default palette)
 *   // @camera pos=0,1,5 target=0,0,0 fov=40      // @loops  (shader is natively periodic, skip cross-fade)
 *   uniform float uDensity; //= 0.5 | what it does      -> custom param  params.density  (float | vec2 | vec3 hex ok)
 */
(function (root) {
  'use strict';
  const TAU = Math.PI * 2;

  const PRELUDE = `#version 300 es
precision highp float; precision highp int;
out vec4 fragColor;
uniform vec2 uRes; uniform float uTime; uniform float uTL; uniform float uLoopP; uniform float uXf;
uniform float uSeed; uniform float uScale; uniform float uIntensity; uniform float uVig; uniform float uGrain; uniform float uGrainSeed;
uniform vec3 uPal[5]; uniform int uNPal;
uniform vec3 uCamPos; uniform vec3 uCamTarget; uniform float uFov; uniform float uRoll;
#define PI 3.14159265359
#define TAU 6.28318530718
#define P0 uPal[0]
#define P1 uPal[1]
#define P2 uPal[2]
#define P3 uPal[3]
#define P4 uPal[4]
float T; float PH; float LP; float ASPECT; bool PORTRAIT; vec3 SD;

// ---- hashes (pure) ----
float hash11(float p){ p=fract(p*.1031); p*=p+33.33; p*=p+p; return fract(p); }
float hash21(vec2 p){ vec3 p3=fract(vec3(p.xyx)*.1031); p3+=dot(p3,p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
vec2 hash22(vec2 p){ vec3 p3=fract(vec3(p.xyx)*vec3(.1031,.1030,.0973)); p3+=dot(p3,p3.yzx+33.33); return fract((p3.xx+p3.yz)*p3.zy); }
float hash31(vec3 p3){ p3=fract(p3*.1031); p3+=dot(p3,p3.zyx+31.32); return fract((p3.x+p3.y)*p3.z); }
vec3 hash33(vec3 p3){ p3=fract(p3*vec3(.1031,.1030,.0973)); p3+=dot(p3,p3.yxz+33.33); return fract((p3.xxy+p3.yxx)*p3.zyx); }
float ign(vec2 p){ return fract(52.9829189*fract(dot(p,vec2(.06711056,.00583715)))); }   // interleaved gradient noise

// ---- gradient noise, ~0..1 (mean .5). Seeded through SD. ----
float noise2(vec2 p){
  p+=SD.xy; vec2 i=floor(p), f=fract(p); vec2 u=f*f*f*(f*(f*6.-15.)+10.);
  float a=dot(hash22(i)*2.-1., f), b=dot(hash22(i+vec2(1,0))*2.-1., f-vec2(1,0));
  float c=dot(hash22(i+vec2(0,1))*2.-1., f-vec2(0,1)), d=dot(hash22(i+vec2(1,1))*2.-1., f-vec2(1,1));
  return .5+.7*mix(mix(a,b,u.x), mix(c,d,u.x), u.y);
}
float noise3(vec3 p){
  p+=SD; vec3 i=floor(p), f=fract(p); vec3 u=f*f*f*(f*(f*6.-15.)+10.);
  #define G3(o) dot(hash33(i+o)*2.-1., f-o)
  float a=mix(mix(G3(vec3(0,0,0)),G3(vec3(1,0,0)),u.x), mix(G3(vec3(0,1,0)),G3(vec3(1,1,0)),u.x), u.y);
  float b=mix(mix(G3(vec3(0,0,1)),G3(vec3(1,0,1)),u.x), mix(G3(vec3(0,1,1)),G3(vec3(1,1,1)),u.x), u.y);
  return .5+.6*mix(a,b,u.z);
}
mat2 rot2(float a){ float c=cos(a), s=sin(a); return mat2(c,-s,s,c); }
mat3 rotX(float a){ float c=cos(a), s=sin(a); return mat3(1,0,0, 0,c,-s, 0,s,c); }
mat3 rotY(float a){ float c=cos(a), s=sin(a); return mat3(c,0,s, 0,1,0, -s,0,c); }
mat3 rotZ(float a){ float c=cos(a), s=sin(a); return mat3(c,-s,0, s,c,0, 0,0,1); }
// fbm: oct <= 5, result ~0..1
float fbm2(vec2 p, int oct){ float a=.5, s=0., n=0.; mat2 r=rot2(.5)*2.03; for(int i=0;i<5;i++){ if(i>=oct) break; s+=a*noise2(p); n+=a; p=r*p+11.7; a*=.5; } return s/n; }
float fbm3(vec3 p, int oct){ float a=.5, s=0., n=0.; for(int i=0;i<5;i++){ if(i>=oct) break; s+=a*noise3(p); n+=a; p=p*2.02+vec3(11.7,3.1,7.3); a*=.5; } return s/n; }
// ridged fbm (mountains, veins): ~0..1
float ridge2(vec2 p, int oct){ float a=.5, s=0., n=0.; mat2 r=rot2(.5)*2.03; for(int i=0;i<5;i++){ if(i>=oct) break; float v=1.-abs(noise2(p)*2.-1.); s+=a*v*v; n+=a; p=r*p+11.7; a*=.5; } return s/n; }
// voronoi: x=F1, y=F2, z=hash of nearest cell, w=cell hash2. anim = phase for jittering feature points (0 = static)
vec4 voronoi2(vec2 p, float anim){
  p+=SD.xy*.37; vec2 n=floor(p), f=fract(p); float d1=8., d2=8.; float id=0.; float id2=0.;
  for(int j=-1;j<=1;j++) for(int i=-1;i<=1;i++){
    vec2 g=vec2(float(i),float(j)); vec2 h=hash22(n+g); vec2 o=.5+.5*sin(anim+TAU*h);
    vec2 r=g+o-f; float d=dot(r,r);
    if(d<d1){ d2=d1; d1=d; id=hash21(n+g); id2=hash21(n+g+7.3); } else if(d<d2){ d2=d; }
  }
  return vec4(sqrt(d1), sqrt(d2), id, id2);
}

// ---- SDF primitives and operators ----
float sdSphere(vec3 p, float r){ return length(p)-r; }
float sdBox(vec3 p, vec3 b){ vec3 q=abs(p)-b; return length(max(q,0.))+min(max(q.x,max(q.y,q.z)),0.); }
float sdRoundBox(vec3 p, vec3 b, float r){ return sdBox(p,b-r)-r; }
float sdTorus(vec3 p, vec2 t){ vec2 q=vec2(length(p.xz)-t.x,p.y); return length(q)-t.y; }
float sdCapsule(vec3 p, vec3 a, vec3 b, float r){ vec3 pa=p-a, ba=b-a; float h=clamp(dot(pa,ba)/dot(ba,ba),0.,1.); return length(pa-ba*h)-r; }
float sdCylinder(vec3 p, float h, float r){ vec2 d=abs(vec2(length(p.xz),p.y))-vec2(r,h); return min(max(d.x,d.y),0.)+length(max(d,0.)); }
float sdPlane(vec3 p, float h){ return p.y-h; }
float sdOctahedron(vec3 p, float s){ p=abs(p); return (p.x+p.y+p.z-s)*.57735027; }
float smin(float a, float b, float k){ float h=max(k-abs(a-b),0.)/k; return min(a,b)-h*h*k*.25; }     // polynomial smooth union
float smax(float a, float b, float k){ return -smin(-a,-b,k); }                                      // smooth intersection/subtraction
vec2 opRep(vec2 p, vec2 c){ return mod(p+.5*c,c)-.5*c; }
vec3 opRep3(vec3 p, vec3 c){ return mod(p+.5*c,c)-.5*c; }
vec3 opTwist(vec3 p, float k){ float c=cos(k*p.y), s=sin(k*p.y); vec2 q=mat2(c,-s,s,c)*p.xz; return vec3(q.x,p.y,q.y); }   // twist about Y
vec3 opBend(vec3 p, float k){ float c=cos(k*p.x), s=sin(k*p.x); vec2 q=mat2(c,-s,s,c)*p.xy; return vec3(q,p.z); }

// ---- raymarch helpers (shader must define: float map(vec3 p)) ----
float map(vec3 p);
vec3 calcNormal(vec3 p){ const vec2 k=vec2(1,-1); const float e=.0012;
  return normalize(k.xyy*map(p+k.xyy*e)+k.yyx*map(p+k.yyx*e)+k.yxy*map(p+k.yxy*e)+k.xxx*map(p+k.xxx*e)); }
float calcAO(vec3 p, vec3 n){ float o=0., s=1.; for(int i=0;i<5;i++){ float h=.01+.12*float(i)/4.; float d=map(p+h*n); o+=(h-d)*s; s*=.95; } return clamp(1.-3.*o,0.,1.); }
float softShadow(vec3 ro, vec3 rd, float tmin, float tmax, float k){
  float res=1., t=tmin, ph=1e10;
  for(int i=0;i<32;i++){ float h=map(ro+rd*t); float y=h*h/(2.*ph); float d=sqrt(max(h*h-y*y,0.)); res=min(res,k*d/max(1e-4,t-y)); ph=h; t+=clamp(h,.02,.4); if(res<.003||t>tmax) break; }
  res=clamp(res,0.,1.); return res*res*(3.-2.*res);
}
mat3 camBasis(){ vec3 f=normalize(uCamTarget-uCamPos); vec3 r=normalize(cross(f,vec3(0,1,0))); vec3 u=cross(r,f);
  float c=cos(uRoll), s=sin(uRoll); return mat3(r*c+u*s, u*c-r*s, f); }
vec3 rayDir(vec2 p){ return normalize(camBasis()*vec3(p*2.*tan(.5*uFov),1.)); }   // p = render()'s p; uFov applies to the SHORT side
vec3 camRO(){ return uCamPos; }
float fresnel(vec3 n, vec3 v, float f0, float pw){ return f0+(1.-f0)*pow(clamp(1.-dot(n,v),0.,1.),pw); }

// ---- color ----
vec3 cosPal(float t, vec3 a, vec3 b, vec3 c, vec3 d){ return a+b*cos(TAU*(c*t+d)); }
vec3 palGrad(float x){   // smooth gradient through the user palette (x 0..1 -> P0..P(n-1))
  float n=float(uNPal-1); x=clamp(x,0.,1.)*n; int i=int(floor(x)); float f=x-float(i); f=f*f*(3.-2.*f);
  vec3 a=uPal[0], b=uPal[0]; for(int k=0;k<5;k++){ if(k==i) a=uPal[k]; if(k==min(i+1,uNPal-1)) b=uPal[k]; } return mix(a,b,f); }
vec3 hsv(float h, float s, float v){ vec3 k=clamp(abs(mod(h*6.+vec3(0,4,2),6.)-3.)-1.,0.,1.); return v*mix(vec3(1),k,s); }
float luma(vec3 c){ return dot(c,vec3(.2126,.7152,.0722)); }
vec3 tonemap(vec3 x){ x*=.85; return clamp((x*(2.51*x+.03))/(x*(2.43*x+.59)+.14),0.,1.); }           // ACES (Narkowicz). Call it in lit/HDR shaders.
vec3 sat(vec3 c, float s){ return mix(vec3(luma(c)),c,s); }
float sstep(float a, float b, float x){ return smoothstep(a,b,x); }
float sdBox2(vec2 p, vec2 b){ vec2 d=abs(p)-b; return length(max(d,0.))+min(max(d.x,d.y),0.); }
float sdRoundBox2(vec2 p, vec2 b, float r){ return sdBox2(p,b-r)-r; }
float sdSeg2(vec2 p, vec2 a, vec2 b){ vec2 pa=p-a, ba=b-a; float h=clamp(dot(pa,ba)/dot(ba,ba),0.,1.); return length(pa-ba*h); }
float tri(float x){ return abs(fract(x)-.5)*2.; }                                                      // triangle wave 0..1, period 1
float gain(float x, float k){ float a=.5*pow(2.*((x<.5)?x:1.-x),k); return (x<.5)?a:1.-a; }          // iq gain: k>1 steeper middle
float remap(float x, float a, float b, float c, float d){ return c+(d-c)*clamp((x-a)/(b-a),0.,1.); }
float disc(float d, float r, float soft){ return 1.-smoothstep(r-soft,r+soft,d); }                   // soft disc from a distance
vec3 fogMix(vec3 col, vec3 fogc, float dist, float dens){ return mix(fogc,col,exp(-dist*dens)); }     // exponential distance fog
float hitPlaneY(vec3 ro, vec3 rd, float h){ return (h-ro.y)/rd.y; }                                    // ray/plane y=h distance (negative = behind)
vec3 envStudio(vec3 r, vec3 top, vec3 horizon, vec3 floorc){                                           // cheap studio environment for reflections
  float y=r.y; vec3 c=mix(horizon, y>0.?top:floorc, pow(abs(y),.6));
  c+=2.5*vec3(1.,.97,.92)*(1.-smoothstep(.35,.55,length(vec2(r.x*.8+.3, r.y-.55))))*smoothstep(-.1,.4,r.z+.4);   // key softbox
  c+=1.6*(1.-smoothstep(.0,.12,abs(r.x-.75)))*smoothstep(-.3,.5,y)*(1.-smoothstep(.2,1.,abs(y-.2)));             // vertical strip light
  return c; }
float vnoise(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f); return mix(mix(hash21(i),hash21(i+vec2(1,0)),f.x), mix(hash21(i+vec2(0,1)),hash21(i+vec2(1,1)),f.x), f.y); }  // cheap value noise 0..1, UNSEEDED
vec2 circ(float r, float ph){ return r*vec2(cos(PH+ph), sin(PH+ph)); }                                  // point on a circle; feed to noise for loopable animation

float vignetteK(vec2 uv, float k){ vec2 q=uv-.5; return 1.-k*smoothstep(.15,.85,dot(q,q)*2.2); }
// tilt-shift: blur-amount mask, 0 at focus band (uv.y==focus) growing to 1 at +-width
float tiltMask(float y, float focus, float width){ return smoothstep(0.,width,abs(y-focus)); }
// banding-free gradients: add .5/255-scale noise yourself only if you blend in float; the engine already dithers the final pixel.
// ---- user code below ----
`;

  const MAIN = `
vec3 shade(vec2 p, vec2 uv){
  vec3 col;
  if(uLoopP>0.){
    T=uTL; PH=TAU*uTL/uLoopP; col=render(p,uv);
    if(uXf>0.){ float k=smoothstep(uLoopP*(1.-uXf),uLoopP,uTL); if(k>0.){ T=uTL-uLoopP; col=mix(col,render(p,uv),k); } }
  } else { T=uTime; PH=uTime*.8; col=render(p,uv); }
  return col;
}
void main(){
  vec2 fc=gl_FragCoord.xy; vec2 uv=fc/uRes; vec2 p=(fc-.5*uRes)/min(uRes.x,uRes.y);
  ASPECT=uRes.x/uRes.y; PORTRAIT=uRes.y>uRes.x; LP=uLoopP; SD=vec3(uSeed*12.9898,uSeed*78.233,uSeed*37.719);
  vec3 col=shade(p,uv);
  col*=uIntensity; if(uVig>0.) col*=vignetteK(uv,uVig);
  col=pow(max(col,vec3(0)),vec3(1./2.2));
  float n=ign(fc+uSeed*3.1)+ign(fc*1.37+11.7)-1.;   // triangular dither (+-1/255)
  col+=n/255.;
  if(uGrain>0.) col+=uGrain*(hash21(fc+uGrainSeed*17.31)-.5)*(1.-.6*luma(col));   // film grain, seeded by frame index
  fragColor=vec4(clamp(col,0.,1.),1.);
}
`;
  const VERT = `#version 300 es
void main(){ vec2 p=vec2((gl_VertexID<<1)&2, gl_VertexID&2); gl_Position=vec4(p*2.-1.,0.,1.); }`;

  const hexToLin = (h) => {
    if (Array.isArray(h)) return h;
    h = String(h).replace('#', ''); if (h.length === 3) h = h.split('').map(c => c + c).join('');
    return [0, 2, 4].map(i => Math.pow(parseInt(h.slice(i, i + 2), 16) / 255, 2.2));
  };
  const DEFAULT_PAL = ['#07080d', '#1c2540', '#ff6b4a', '#ffc46b', '#fff4e0'];

  function parseMeta(src) {
    const m = { mood: '', use: '', palette: null, camera: null, loops: false, params: [] };
    let r;
    if ((r = /^\s*\/\/\s*@mood\s+(.*)$/m.exec(src))) m.mood = r[1].trim();
    if ((r = /^\s*\/\/\s*@use\s+(.*)$/m.exec(src))) m.use = r[1].trim();
    if ((r = /^\s*\/\/\s*@palette\s+(.*)$/m.exec(src))) m.palette = r[1].trim().split(/[\s,]+/).filter(Boolean);
    if (/^\s*\/\/\s*@loops/m.test(src)) m.loops = true;
    if ((r = /^\s*\/\/\s*@camera\s+(.*)$/m.exec(src))) {
      m.camera = {}; r[1].split(/\s+/).forEach(kv => { const [k, v] = kv.split('='); if (!v) return; const a = v.split(',').map(Number); m.camera[k] = a.length === 1 ? a[0] : a; });
    }
    const re = /^\s*uniform\s+(float|vec2|vec3)\s+u([A-Z]\w*)\s*;\s*(?:\/\/\s*=\s*([^|\n]*?)\s*(?:\|\s*(.*))?)?$/gm;
    while ((r = re.exec(src))) {
      const type = r[1], name = r[2], key = name[0].toLowerCase() + name.slice(1);
      const def = (r[3] || '').trim();
      let val; if (/^#/.test(def)) val = def; else val = def ? def.split(/[\s,]+/).map(Number) : [];
      m.params.push({ key, uniform: 'u' + name, type, def: val, desc: (r[4] || '').trim() });
    }
    return m;
  }

  function create(w, h, opts) {
    opts = opts || {};
    const canvas = opts.canvas || document.createElement('canvas');
    canvas.width = w; canvas.height = h;
    const gl = canvas.getContext('webgl2', { antialias: false, alpha: false, preserveDrawingBuffer: true, premultipliedAlpha: false, powerPreference: 'high-performance' });
    if (!gl) throw new Error('[Bg3D] WebGL2 not available');
    const cache = new Map();
    const vao = gl.createVertexArray();
    const bg = { canvas, gl, w, h, error: null };

    function build(key, src) {
      let meta = parseMeta(src);
      const hasMap = /float\s+map\s*\(\s*vec3/.test(src);
      const frag = PRELUDE + (hasMap ? '' : 'float map(vec3 p){ return 1e3; }\n') + src + '\n' + MAIN;
      const preLines = (PRELUDE + (hasMap ? '' : 'float map(vec3 p){ return 1e3; }\n')).split('\n').length - 1;
      const mk = (type, s) => { const sh = gl.createShader(type); gl.shaderSource(sh, s); gl.compileShader(sh); return sh; };
      const vs = mk(gl.VERTEX_SHADER, VERT), fs = mk(gl.FRAGMENT_SHADER, frag);
      const prog = gl.createProgram(); gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
      if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
        let log = (gl.getShaderInfoLog(fs) || '') + (gl.getProgramInfoLog(prog) || '');
        log = log.replace(/ERROR: 0:(\d+)/g, (_, n) => 'ERROR: shader line ' + (Math.max(1, +n - preLines)));
        const e = '[Bg3D] shader "' + key + '" failed to compile:\n' + log; console.error(e); bg.error = e;
        return { failed: true, meta };
      }
      const U = {}; const n = gl.getProgramParameter(prog, gl.ACTIVE_UNIFORMS);
      for (let i = 0; i < n; i++) { const info = gl.getActiveUniform(prog, i); U[info.name.replace(/\[0\]$/, '')] = gl.getUniformLocation(prog, info.name); }
      return { prog, U, meta, failed: false };
    }

    function resolve(shader) {
      if (typeof shader === 'string') {
        const lib = root.Bg3DShaders || {}; const reg = Bg3D._registry;
        const src = reg[shader] || lib[shader];
        if (!src) throw new Error('[Bg3D] unknown shader "' + shader + '". Known: ' + Bg3D.list().join(', '));
        return { key: shader, src };
      }
      return { key: shader.name || ('custom:' + (shader.glsl.length) + ':' + hashStr(shader.glsl)), src: shader.glsl };
    }
    function hashStr(s) { let h = 2166136261; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0).toString(16); }

    // build (compile+link) a shader without drawing; returns null when OK or the error text. Use in tests.
    bg.compile = (shader) => { const { key, src } = resolve(shader); let e = cache.get(key); if (!e) { bg.error = null; e = build(key, src); cache.set(key, e); } return e.failed ? (bg.error || 'failed') : null; };
    bg.resize = (nw, nh) => { canvas.width = nw; canvas.height = nh; bg.w = nw; bg.h = nh; return bg; };

    bg.draw = (shader, t, params) => {
      params = params || {};
      const { key, src } = resolve(shader);
      let entry = cache.get(key); if (!entry) { entry = build(key, src); cache.set(key, entry); }
      gl.viewport(0, 0, canvas.width, canvas.height);
      if (entry.failed) { gl.clearColor(1, 0, 1, 1); gl.clear(gl.COLOR_BUFFER_BIT); return canvas; }   // magenta = compile error (see console)
      const { prog, U, meta } = entry;
      gl.useProgram(prog);
      const set1 = (n, v) => { if (U[n] != null) gl.uniform1f(U[n], v); };
      const speed = params.speed == null ? 1 : params.speed;
      const loopP = params.loopPeriod || 0;
      set1('uTime', t * speed);
      if (U.uRes != null) gl.uniform2f(U.uRes, canvas.width, canvas.height);
      if (loopP > 0) { const tl = ((t % loopP) + loopP) % loopP; set1('uTL', tl * speed); set1('uLoopP', loopP * speed); set1('uXf', meta.loops ? 0 : (params.loopFade == null ? 0.3 : params.loopFade)); }
      else { set1('uTL', t * speed); set1('uLoopP', 0); set1('uXf', 0); }
      set1('uSeed', params.seed == null ? 1 : params.seed);
      set1('uScale', params.scale == null ? 1 : params.scale);
      set1('uIntensity', params.intensity == null ? 1 : params.intensity);
      set1('uVig', params.vignette || 0);
      set1('uGrain', params.grain || 0); set1('uGrainSeed', Math.round(t * (params.fps || 30)) % 997);
      // palette (sRGB hex -> linear). Missing slots are derived lighter from the last given color.
      let pal = (params.palette && params.palette.length ? params.palette : (meta.palette || DEFAULT_PAL)).map(hexToLin);
      const n = Math.min(5, pal.length); const full = [];
      for (let i = 0; i < 5; i++) full.push(i < n ? pal[i] : pal[n - 1].map(c => c + (1 - c) * 0.35 * (i - n + 1)));
      if (U['uPal'] != null) gl.uniform3fv(U['uPal'], new Float32Array(full.flat()));
      if (U.uNPal != null) gl.uniform1i(U.uNPal, Math.max(2, n));
      // camera
      const dc = meta.camera || {}, c = params.camera || {};
      const pos = c.pos || dc.pos || [0, 0, 4], tgt = c.target || dc.target || [0, 0, 0];
      const fov = c.fov || dc.fov || 40, roll = c.roll != null ? c.roll : (dc.roll || 0);
      if (U.uCamPos != null) gl.uniform3f(U.uCamPos, pos[0], pos[1], pos[2]);
      if (U.uCamTarget != null) gl.uniform3f(U.uCamTarget, tgt[0], tgt[1], tgt[2]);
      set1('uFov', fov * Math.PI / 180); set1('uRoll', roll * Math.PI / 180);
      // custom params
      for (const p of meta.params) {
        const loc = U[p.uniform]; if (loc == null) continue;
        let v = params[p.key]; if (v == null) v = p.def;
        if (p.type === 'float') gl.uniform1f(loc, Array.isArray(v) ? v[0] : +v);
        else if (p.type === 'vec2') { v = Array.isArray(v) ? v : [v, v]; gl.uniform2f(loc, v[0], v[1] == null ? v[0] : v[1]); }
        else { const rgb = (typeof v === 'string') ? hexToLin(v) : v; gl.uniform3f(loc, rgb[0], rgb[1], rgb[2]); }
      }
      gl.bindVertexArray(vao); gl.drawArrays(gl.TRIANGLES, 0, 3);
      bg.error = null; return canvas;
    };
    // copy the last drawn frame into a 2D context (do this right after draw, same task)
    bg.blit = (ctx, x, y, w2, h2) => { ctx.drawImage(canvas, x || 0, y || 0, w2 || canvas.width, h2 || canvas.height); };
    bg.dispose = () => { cache.forEach(e => e.prog && gl.deleteProgram(e.prog)); cache.clear(); const x = gl.getExtension('WEBGL_lose_context'); if (x) x.loseContext(); };
    return bg;
  }

  /* ---- pure camera helpers (all return {pos,target,fov,roll}; pass the result as params.camera) ---- */
  const clamp01 = (x) => Math.min(1, Math.max(0, x));
  const sm = (x) => { x = clamp01(x); return x * x * x * (x * (6 * x - 15) + 10); };
  const lerp3 = (a, b, k) => [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k];
  const cam = {
    // two keyframes + ease (fn(0..1)->0..1; default smootherstep, pass Lab.curves.punch etc). k0 = [pos,target,fov,roll]
    between(t, t0, t1, a, b, ease) {
      const k = (ease || sm)(clamp01((t - t0) / (t1 - t0)));
      return { pos: lerp3(a.pos, b.pos, k), target: lerp3(a.target || [0, 0, 0], b.target || [0, 0, 0], k),
        fov: (a.fov || 40) + ((b.fov || a.fov || 40) - (a.fov || 40)) * k, roll: (a.roll || 0) + ((b.roll || 0) - (a.roll || 0)) * k };
    },
    // orbit around `center`: angle = a0 + (a1-a0)*k over [t0,t1]; radius/height fixed
    orbit(t, o) {
      const c = o.center || [0, 0, 0], k = o.t1 > o.t0 ? sm((t - o.t0) / (o.t1 - o.t0)) : (t / (o.period || 10));
      const a = (o.a0 || 0) + ((o.a1 == null ? TAU : o.a1) - (o.a0 || 0)) * k;
      return { pos: [c[0] + Math.sin(a) * o.radius, c[1] + (o.height || 0), c[2] + Math.cos(a) * o.radius], target: c, fov: o.fov || 40, roll: o.roll || 0 };
    },
    // organic drift: sum of incommensurate sines. period = seconds for the slowest component; if period divides the loop length the drift loops.
    // returns offsets to ADD to a base camera: cam.drift(t, {amp:.15, period:12, seed:3}) -> {dx,dy,dz,droll}
    drift(t, o) {
      o = o || {}; const A = o.amp == null ? 0.1 : o.amp, P = o.period || 12, s = (o.seed || 0) * 1.7, w = TAU / P;
      return { dx: A * (Math.sin(w * t + s) + .5 * Math.sin(2 * w * t + 1.3 + s)) / 1.5, dy: A * .6 * (Math.sin(w * t + 2.1 + s) + .5 * Math.sin(3 * w * t + .4 + s)) / 1.5,
        dz: A * .5 * Math.sin(2 * w * t + .7 + s), droll: (o.roll == null ? 0.6 : o.roll) * Math.sin(w * t + 4 + s) };
    },
    // apply drift to a camera
    withDrift(c, d) { return { pos: [c.pos[0] + d.dx, c.pos[1] + d.dy, c.pos[2] + d.dz], target: c.target || [0, 0, 0], fov: c.fov, roll: (c.roll || 0) + d.droll }; },
  };

  const Bg3D = {
    create, PRELUDE, TAU, cam, _registry: {},
    register(nameOrObj, glsl) { if (typeof nameOrObj === 'string') this._registry[nameOrObj] = glsl; else Object.assign(this._registry, nameOrObj); },
    list() { return Object.keys(Object.assign({}, root.Bg3DShaders || {}, this._registry)); },
    source(name) { return this._registry[name] || (root.Bg3DShaders || {})[name]; },
    describe(name) { const s = this.source(name); if (!s) return null; const m = parseMeta(s); m.name = name; return m; },
    hexToLinear: hexToLin,
  };
  root.Bg3D = Bg3D;
})(typeof window !== 'undefined' ? window : globalThis);
