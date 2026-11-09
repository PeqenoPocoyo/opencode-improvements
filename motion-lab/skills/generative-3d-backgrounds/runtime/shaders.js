/* shaders.js — Bg3DShaders: 4 procedural 3D-looking background shaders for Bg3D (runtime/bg3d.js). No images, no clock.
 * Each entry is GLSL ES 3.00 body text; bg3d.js prepends its prelude (noise, SDFs, palette, camera...) and wraps it with intensity/vignette/dither.
 * List them: Bg3D.list()   Metadata (mood, use, default palette, params): Bg3D.describe(name)   Source: Bg3D.source(name)
 * Palette roles used by every shader: P0 deepest background, P1 secondary background, P2 main accent, P3 second accent / light, P4 highlight.
 * GENERATED from one-shader-per-file sources; to add a shader, append  Bg3DShaders['my-name'] = `...glsl...`;  or call Bg3D.register(name, glsl).
 */
(function (root) {
  'use strict';
  const S = root.Bg3DShaders = root.Bg3DShaders || {};

  S['neon-gradient-reflect'] = `// @mood neon monochrome, cinematic, night, sci-fi, hopeful (single hue + black)
// @use One-hue world behind silhouettes / glowing numerals: dark-to-bright vertical gradient, a glossy floor that mirrors it, drifting haze and dust. Pick ONE hue (palette P1..P3 all from the same hue).
// @palette #010503 #04281a #0fbf6b #6dffb0 #eafff3
uniform float uHorizon; //= -0.12 | horizon height (short-side units, y up)
uniform float uHaze; //= 0.6 | drifting haze amount
uniform float uStreak; //= 0.6 | horizontal ripple streaks in the floor reflection
uniform float uDust; //= 0.7 | dust motes
uniform float uSun; //= 0.35 | bright core at the horizon
vec3 sky(float s, float x){        // s: 0 at horizon .. 1 at top edge
  float k = pow(1.-s, 2.2);
  vec3 c = palGrad(k*.82);
  c += P3*uSun*exp(-s*s*40.)*exp(-x*x*3.);
  return c;
}
float dustLayer(vec2 p, float sc, float sp, float seed){
  vec2 q = p*sc + vec2(0., -T*sp*.05) + vec2(sin(T*.2+seed)*.2,0.);
  vec2 id = floor(q), f = fract(q)-.5; vec2 h = hash22(id+seed*13.)-.5;
  float d = length(f-h*.7); float tw = .5+.5*sin(T*(.5+hash21(id+seed)*1.5)+hash21(id)*6.28);
  return smoothstep(.06,.0,d)*tw*step(.55,hash21(id+3.1+seed));
}
vec3 render(vec2 p, vec2 uv){
  float H = uHorizon; float top = .5-H;
  vec3 col;
  float x = p.x;
  if(p.y>=H){
    float s = clamp((p.y-H)/top,0.,1.);
    col = sky(s,x);
  } else {
    float dy = H-p.y;                                    // depth below the horizon
    float persp = 1./(1.+dy*3.5);
    float wob = (noise2(vec2(p.x*(3.+uStreak*10.)*persp, dy*40.+T*.35))-.5)*uStreak*.05*(1.-persp*.5);
    float ys = clamp((dy+wob*dy)/top*1.25,0.,1.);        // mirrored sky coordinate (compressed)
    vec3 refl = sky(ys, x);
    float fres = mix(.9,.12,smoothstep(0.,.45,dy));
    // streaks: soft horizontal bands of brighter reflection
    float st = noise2(vec2(p.x*(1.5+uStreak*5.)*persp, dy*18.));
    refl *= .75+.55*uStreak*(st-.35);
    col = refl*fres + P0*(1.-fres)*.6;
    col += P2*.08*exp(-dy*12.)*exp(-x*x*2.);
  }
  // haze: slow horizontal fbm banks, strongest near the horizon
  float hz = fbm2(vec2(p.x*1.4+T*.03, p.y*5.)+vec2(0.,T*.01),4);
  float band = exp(-pow((p.y-H)/.22,2.));
  col += P2*pow(hz,2.2)*1.3*uHaze*band;
  col += P3*pow(fbm2(p*2.4+7.+vec2(T*.02,0.),3),3.)*.35*uHaze*smoothstep(.0,.5,.5-p.y)*.5;
  // dust: 3 depth layers
  float dd = dustLayer(p,9.,1.,1.)*.8+dustLayer(p,16.,1.6,2.)*.55+dustLayer(p,28.,2.3,3.)*.35;
  col += P3*dd*uDust*(.4+1.6*exp(-pow((p.y-H)/.5,2.)));
  return col;
}
`;

  S['aurora-mesh'] = `// @mood soft, premium, calm, modern product / SaaS, dreamy
// @use Backdrop behind titles, UI cards and product shots. Slow breathing colour fields, never busy. Safe default for "a nice gradient background".
// @palette #0a0d1f #3a2d9c #ff5fa8 #ffb36b #7fe4ff
// @loops
uniform float uWarp; //= 0.7 | liquid warp of the colour field (0 clean blobs .. 1.5 very liquid)
uniform float uBlobs; //= 5 | number of colour blobs (3..6)
uniform float uSoft; //= 1.0 | blob size/softness (0.6 tight .. 2 diffuse)
uniform float uSheen; //= 0.5 | silky highlight ridges (0 none)
vec3 blobCol(int i){ if(i==0) return P2; if(i==1) return P1; if(i==2) return P3; if(i==3) return P4; if(i==4) return P2; return P1; }
vec3 render(vec2 p, vec2 uv){
  vec2 q = p*uScale;
  vec2 w = vec2(noise3(vec3(q*1.4, 0.)+vec3(circ(.6,0.),0.)), noise3(vec3(q*1.4+7.3, 0.)+vec3(circ(.6,2.1),0.))) - .5;
  q += w*uWarp*1.3;
  float sx = PORTRAIT ? .55 : 1.2;
  vec3 acc = P0*.22; float ws = .22;
  for(int i=0;i<6;i++){
    if(float(i)>=uBlobs) break;
    float fi=float(i);
    float k1 = 1.+mod(fi,2.), k2 = 1.+mod(fi+1.,2.);
    vec2 c = vec2(sx*.8*cos(PH*k1+fi*2.39996+SD.x), .55*sin(PH*k2+fi*1.7+SD.y));
    float r = (.26+.14*hash11(fi*3.7+SD.z))*uSoft;
    vec2 d = q-c;
    float wgt = exp(-dot(d,d)/(r*r));
    acc += blobCol(i)*wgt; ws += wgt;
  }
  vec3 col = acc/ws;
  // silky sheen: thin bright ridges following the warped field
  float n1 = noise3(vec3(q*2.4, 1.3)+vec3(circ(.5,1.),0.));
  float ridge = pow(1.-abs(n1*2.-1.), 6.);
  col += P4*ridge*uSheen*.12*smoothstep(.1,.6,luma(col)*2.);
  col *= .85 + .3*smoothstep(-.5,.5,p.y);        // gentle top light
  return col;
}
`;

  S['clay-studio'] = `// @mood warm, tactile, editorial, clay render, calm, monochrome
// @use Backdrop for clay / monochrome editorial scenes (cream paper stage), under big grotesk headings. uObjects adds soft clay primitives with real shadows; uShadowA/B draw contact shadows for objects you overlay yourself.
// @palette #efe7d6 #cfc4ad #8a7f6d #2a2927 #ffffff
// @camera pos=0,1.45,6.4 target=0,0.95,0 fov=34
uniform float uObjects; //= 0 | 0..3 soft clay primitives: sphere, rounded block, torus
uniform float uGrid; //= 0 | 0..1 faint editorial grid over everything
uniform vec3 uShadowA; //= 0 0 0 | fake contact shadow: x, y (short-side units, y up), width (0 = off)
uniform vec3 uShadowB; //= 0 0 0 | second contact shadow
uniform float uLightX; //= -0.7 | key light direction x (negative = from the left)
uniform float uCove; //= 1.3 | softness of the wall/floor curve
float map(vec3 p){
  float cove = smin(p.y, p.z+3.2, uCove);
  float d = cove;
  if(uObjects>0.5){ float bob=.02*sin(PH); d=min(d, sdSphere(p-vec3(-.95,.5+bob,.2),.5)); }
  if(uObjects>1.5){ vec3 q=p-vec3(.25,.42,-.7); q.xz*=rot2(.6+.3*sin(PH)); d=min(d, sdRoundBox(q,vec3(.42),.12)); }
  if(uObjects>2.5){ vec3 q=p-vec3(1.15,.5,.45); q.yz*=rot2(1.2); q.xy*=rot2(.5*sin(PH)); d=min(d, sdTorus(q,vec2(.42,.17))); }
  return d;
}
vec3 render(vec2 p, vec2 uv){
  vec3 ro=camRO(), rd=rayDir(p);
  float t=.5; float hitd=0.;
  for(int i=0;i<64;i++){ float h=map(ro+rd*t); if(h<.002) break; t+=h*.9; if(t>30.) break; }
  vec3 pos=ro+rd*t; vec3 n=calcNormal(pos);
  vec3 L=normalize(vec3(uLightX,1.15,.9));
  float diff=clamp(dot(n,L),0.,1.);
  float sh=softShadow(pos+n*.02, L, .05, 9., 5.);
  float ao=calcAO(pos,n);
  float hemi=.55+.45*n.y;
  bool isObj = pos.y>.02 && pos.z>-3.1 && map(pos) < .01 && (length(pos-vec3(-.95,.5,.2))<.62 || abs(pos.x-.25)<.7 && abs(pos.z+.7)<.7 && pos.y<.95 || length(pos-vec3(1.15,.5,.45))<.7) && uObjects>.5;
  vec3 alb = isObj ? P3 : P0;
  vec3 shadowTint = mix(vec3(1.), P2/max(luma(P2),.02)*.55, .6);
  vec3 lit = vec3(.34*hemi*ao) + vec3(1.05*diff)*mix(shadowTint,vec3(1.),sh)*ao;
  vec3 col = alb*lit;
  if(isObj){ vec3 h=normalize(L-rd); col += P4*pow(clamp(dot(n,h),0.,1.),48.)*.18*sh; col += P4*pow(1.-clamp(dot(n,-rd),0.,1.),3.)*.06; }
  // wall/floor falloff towards the back + very soft vertical gradient so it never looks flat
  col = mix(col, P1*.8, smoothstep(10.,26.,t)*.5);
  // fake contact shadows for foreground objects
  for(int k=0;k<2;k++){ vec3 s = k==0?uShadowA:uShadowB; if(s.z>0.){ vec2 e=(p-s.xy)/vec2(s.z,s.z*.22); float g=exp(-dot(e,e)*1.6); col*=1.-.55*g; col*=mix(vec3(1.),shadowTint,g*.6); } }
  if(uGrid>0.){ vec2 g=abs(fract(p*9.)-.5); float ln=smoothstep(.485,.5,max(g.x,g.y)); col=mix(col,P2,ln*.12*uGrid); }
  col *= vignetteK(uv,.28);
  return tonemap(col*1.05)*.0 + pow(col,vec3(.97));   // keep linear-ish cream; ACES would grey it
}
`;

  S['studio-radial'] = `// @mood dark, premium, product hero stage, tech launch, quiet
// @use Behind glass icons, app icons, a device or one hero object. Quiet on purpose: the foreground carries the light. Turn uHalo on for a ring halo behind the subject.
// @palette #030407 #0a1224 #2f6bff #86b0ff #f4f8ff
// @loops
uniform float uGlowY; //= 0.08 | height of the light pool centre (-0.5 bottom .. 0.5 top)
uniform float uHalo; //= 0.0 | 0..1 ring halo behind the subject
uniform float uHaloR; //= 0.3 | halo radius (short-side units)
uniform float uFloor; //= 0.6 | glossy floor reflection (0 none)
uniform float uHaze; //= 0.5 | fine haze layered over the stage
vec3 render(vec2 p, vec2 uv){
  float hy = uGlowY; vec2 c = vec2(0., hy);
  vec2 d = (p-c)*vec2(1.,1.12)/uScale; float r = length(d);
  vec3 col = mix(P1, P0, smoothstep(.0,.9,r));
  col *= .25 + .75*exp(-r*r*2.0);
  col += P2*.12*exp(-r*r*9.);
  // glossy floor: a line, a darker plane and a mirrored glow
  float fy = hy-.2-.02;
  float below = smoothstep(fy+.004, fy-.004, p.y);
  float depth = clamp((fy-p.y)/.5, 0., 1.);
  vec2 dm = vec2(p.x, 2.*fy-p.y) - c;
  float mirror = exp(-dot(dm*vec2(1.,1.4),dm*vec2(1.,1.4))*7.) * (1.-depth) * uFloor;
  col = mix(col, col*.55 + (P1+P2*.35)*mirror*.9, below);
  col += P3*exp(-abs(p.y-fy)*160.)*.12*uFloor*exp(-p.x*p.x*6.);
  // ring halo with a slowly rotating conic colour
  if(uHalo>0.){
    vec2 hp = p-c; float rr = length(hp); float a = atan(hp.y,hp.x);
    float ring = exp(-pow((rr-uHaloR)/(.012+.01*uHalo),2.));
    float glow = exp(-pow((rr-uHaloR)/.09,2.))*.5;
    float k = .5+.5*sin(a+PH);
    vec3 hc = mix(P2,P3,k);
    col += hc*(ring*1.6+glow*.35)*uHalo;
    col += P2*.25*uHalo*exp(-rr*rr/(uHaloR*uHaloR)*1.6)*.5;
  }
  // haze
  float hz = noise3(vec3(p*1.6+vec2(0.,.2), 0.)+vec3(circ(.5,0.),0.));
  col += P1*(hz-.5)*.35*uHaze*exp(-r*r*1.5);
  return col;
}
`;

})(typeof window !== 'undefined' ? window : globalThis);
