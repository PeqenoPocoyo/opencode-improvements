/* shaders2.js — 12 more Bg3D worlds (field / pseudo-3D, cheap). Same contract as shaders.js. Palette roles P0 deepest .. P4 highlight. */
(function (root) {
  'use strict';
  const S = root.Bg3DShaders = root.Bg3DShaders || {};

  S['liquid-chrome'] = `// @mood chrome, liquid metal, glossy, premium, futuristic, calm
// @use Hero backdrop behind a logo/product/number: slow molten-metal surface with studio reflections. Single hue + white reads most expensive.
// @palette #04050a #141a2c #6d8dff #cfdcff #ffffff
uniform float uWarp; //= 1.0 | domain-warp strength (more = more molten)
uniform float uFeat; //= 1.5 | feature scale (bigger = smaller ripples)
uniform float uBump; //= 0.55 | surface relief
float hgt(vec2 p){
  vec2 q = p*uFeat; vec2 c1 = circ(.7,0.), c2 = circ(.7,2.1);
  vec2 w = vec2(fbm2(q+c1,4), fbm2(q+vec2(5.2,1.3)+c2,4)) - .5;
  return fbm2(q + uWarp*2.4*w + circ(.3,4.), 4);
}
vec3 render(vec2 p, vec2 uv){
  float e = .006; float a = hgt(p);
  vec2 g = vec2(hgt(p+vec2(e,0.))-a, hgt(p+vec2(0.,e))-a)/e;
  vec3 n = normalize(vec3(-g*uBump*.55, 1.));
  vec3 r = reflect(vec3(0.,0.,-1.), n);
  float y = r.y*.5+.5;
  vec3 env = palGrad(pow(y,1.6));
  env += P4*2.2*smoothstep(.72,.95,y)*smoothstep(-.4,.4,r.x);       // top softbox
  env += P3*1.4*pow(max(0.,1.-abs(r.x-.5)*3.),3.)*smoothstep(.2,.6,y);   // vertical strip
  env *= .55 + .9*smoothstep(.2,.9,a);
  float fr = fresnel(n, vec3(0.,0.,1.), .25, 4.);
  vec3 col = env*(.45+.8*fr);
  col += P4*pow(max(0.,dot(r, normalize(vec3(.4,.7,.6)))),40.)*.9;
  return col*(1.-.35*length(p));
}
`;

  S['ink-in-water'] = `// @mood organic, smoky, elegant, mysterious, slow
// @use Billowing ink/smoke clouds as a mood backdrop for titles, quotes, music and fashion; looks hand-made, not geometric.
// @palette #05050a #17122b #7b3fe4 #ff7ac6 #fff1f8
uniform float uFlow; //= 1.0 | how far the smoke is folded
uniform float uDens; //= 1.0 | cloud density
vec3 render(vec2 p, vec2 uv){
  vec2 q = p*1.7; vec2 c = circ(.45,0.), c2 = circ(.45,2.);
  for(int i=0;i<3;i++){ float fi=float(i); q += uFlow*(vec2(noise2(q*1.25+c+fi*3.1), noise2(q*1.25+c2+fi*7.7))-.5)*1.25; }
  float d = fbm2(q*1.1, 5);
  float s = smoothstep(.34, .72, d*uDens);
  vec3 col = mix(P0, P1, smoothstep(-.6,.8,p.y));
  col = mix(col, mix(P2,P3,smoothstep(.45,.85,d)), s*.92);
  col += P4*exp(-pow((d-.56)/.035,2.))*.55*uDens;                      // lit edge of the smoke
  col *= .55 + .75*fbm2(q*3.+5.,3)*s + .45*(1.-s);
  return col;
}
`;

  S['topographic-lines'] = `// @mood technical, cartographic, calm, data-art, minimal
// @use Contour-map backdrop for data/finance/tech explainers; lines slowly breathe. Works light or dark.
// @palette #07120f #0e2a22 #2fd69a #9affd2 #eafff6
uniform float uLevels; //= 14 | number of contour levels
uniform float uZoom; //= 1.6 | feature scale
uniform float uThick; //= 1.0 | line thickness
vec3 render(vec2 p, vec2 uv){
  float h = fbm2(p*uZoom + circ(.35,0.), 5);
  float x = h*uLevels; float w = fwidth(x);
  float d = abs(fract(x+.5)-.5);
  float line = 1.-smoothstep(0., w*1.1*uThick+.012*uThick, d);
  float major = 1.-smoothstep(0., w*1.6*uThick+.02, abs(fract(x/5.+.5)-.5)*5.);
  vec3 col = mix(P0, P1, smoothstep(.25,.75,h));
  col += P2*.14*smoothstep(.55,.9,h);
  col = mix(col, P2, line*.75);
  col = mix(col, P4, major*.9);
  col *= 1.-.4*length(p);
  return col;
}
`;

  S['grid-horizon'] = `// @mood retro-futuristic, synthwave, night, driving, energetic
// @use Infinite perspective grid floor under a striped sun; strong depth for titles floating above the horizon. Speed param drives the feeling of travel.
// @palette #0a0320 #2a0a4e #ff2e93 #ffb02e #fff3c4
uniform float uSpeed; //= 1.0 | travel speed
uniform float uHor; //= 0.0 | horizon height in p units (relative to frame centre)
uniform float uSunR; //= 0.28 | sun radius
vec3 render(vec2 p, vec2 uv){
  float H = uHor - .12; vec3 col;
  if(p.y > H){
    float s = clamp((p.y-H)/.9, 0., 1.);
    col = mix(P3*.9, P1, pow(s,.55)); col = mix(col, P0, smoothstep(.25,1.,s));
    vec2 sp = p - vec2(0., H+.30); float d = length(sp);
    float stripes = smoothstep(.0,.03, sin((sp.y*55.) - T*.0 ) + .55 + (sp.y<0.? -sp.y*3.2 : 0.)*0. - (sp.y<.04 ? (.04-sp.y)*1.3 : 0.));
    stripes = mix(1., smoothstep(-.1,.1, sin(sp.y*60.)+ (sp.y+.3)*4.-.8), step(sp.y,.0));
    float sun = 1.-smoothstep(uSunR-.006, uSunR+.006, d);
    vec3 sc = mix(P3, P2, smoothstep(-uSunR, uSunR, sp.y));
    col = mix(col, sc*1.3, sun*stripes);
    col += P2*.5*exp(-d*3.5)*.6 + P3*.3*exp(-d*9.);
  } else {
    float dy = H - p.y; float z = .5/dy;
    float zz = z + T*.9*uSpeed; float xx = p.x*z*1.2;
    vec2 g = vec2(xx, zz); vec2 gf = abs(fract(g-.5)-.5)/fwidth(g);
    float line = 1.-min(min(gf.x,gf.y),1.);
    float fade = exp(-z*.09);
    col = mix(P0, P1, .35) * .6;
    col += P2*line*fade*1.6 + P3*line*fade*.25;
    col += P2*.25*exp(-dy*7.);                               // reflected glow at the horizon
  }
  col += P2*.35*exp(-abs(p.y-H)*40.);
  return col;
}
`;

  S['tunnel-rings'] = `// @mood hypnotic, tunnel, fast, club, sci-fi
// @use Infinite ring tunnel for energy beats, countdowns and transitions; speed up on hits via params.speed. Centre is the vanishing point: keep the hero there.
// @palette #020208 #0b1a4a #3d7bff #ff3dcb #ffffff
uniform float uSides; //= 8 | segments around
uniform float uDepth; //= 1.0 | ring spacing (1 = default)
uniform float uTwist; //= 0.25 | twist along depth
vec3 render(vec2 p, vec2 uv){
  float r = length(p); float a = atan(p.y,p.x);
  float z = .30/(r+.02) + T*1.3;
  float seg = a/TAU*uSides + z*uTwist;
  float zd = z/uDepth; float id = floor(zd+.5);
  float dr = abs(fract(zd+.5)-.5);                                    // 0 on a ring
  float ring = 1.-smoothstep(.0, .035+r*.12, dr);
  float rib = 1.-smoothstep(.0, .03+r*.05, abs(fract(seg+.5)-.5));
  vec3 c1 = mix(P2,P3,hash11(id*1.7));
  vec3 col = mix(P0,P1,smoothstep(.0,.9,r));
  col += mix(P1,P2,.5)*.35*smoothstep(.5,.0,abs(fract(zd)-.5))*(.4+.6*smoothstep(.0,.6,r));
  col += c1*ring*(1.1+.5*sin(id*1.3))*smoothstep(.0,.25,r);
  col += mix(P2,P3,.5+.5*sin(seg))*rib*.22*smoothstep(.02,.4,r);
  col *= smoothstep(.0,.3,r);                                       // dark centre = depth
  col += P4*exp(-r*r*90.)*.25;
  return col;
}
`;

  S['starfield-warp'] = `// @mood space, hyperspace, speed, awe
// @use Parallax stars or warp streaks. streak=0 gives a calm drifting starfield, streak=1 hyperspace; animate params.streak with a hit curve for jump moments.
// @palette #010208 #060b24 #5b8cff #bfe3ff #ffffff
uniform float uStreak; //= 0.35 | 0 = dots, 1+ = long streaks
uniform float uSpeedF; //= 0.35 | travel speed
uniform float uNeb; //= 0.6 | nebula glow amount
vec3 render(vec2 p, vec2 uv){
  float r = length(p)+1e-3; float a = atan(p.y,p.x);
  vec3 col = mix(P0,P1,.5+.5*p.y);
  float neb = fbm2(p*1.6+circ(.3,0.),4); col += mix(P1,P2,neb)*neb*neb*uNeb*.7;
  for(int L=0;L<4;L++){
    float fl = float(L);
    float N = 46.+fl*34.;
    vec2 q = vec2(a/TAU*N, log(r)*(5.+fl*2.5) - T*uSpeedF*(1.+fl*.6));
    vec2 id = floor(q), f = fract(q)-.5; vec2 h = hash22(id+fl*17.);
    float on = step(.62-fl*.04, h.x);
    vec2 d = f-(h-.5)*.7; d.y /= (1.+uStreak*(6.+fl*3.)); 
    float sz = .06+.05*h.y;
    float s = smoothstep(sz,0.,length(d))*on;
    s *= smoothstep(.02,.35,r)*(.5+r*1.3);
    col += mix(P3,P4,h.y)*s*(1.4+.8*uStreak);
  }
  return col;
}
`;

  S['bokeh-lights'] = `// @mood warm, dreamy, night city, celebratory, cinematic
// @use Out-of-focus lights drifting behind a hero (portrait, product, quote). Soft and expensive; use few, large discs for calm, many small for party.
// @palette #07060d #1a1030 #ff7a3d #ffc46b #fff2d6
uniform float uCount; //= 1.0 | density multiplier
uniform float uSoft; //= 0.35 | edge softness (0 = crisp discs with ring)
uniform float uDrift; //= 1.0 | drift speed
vec3 render(vec2 p, vec2 uv){
  vec3 col = mix(P0,P1,smoothstep(-.7,.7,p.y)+.15*noise2(p*1.5));
  for(int L=0;L<3;L++){
    float fl=float(L); float sc = (2.2+fl*1.9)/ (uCount*.7+.3);
    vec2 q = p*sc + vec2(circ(.4,fl*2.).x, -T*.05*uDrift*(1.+fl*.4)+circ(.4,fl).y);
    vec2 id=floor(q), f=fract(q)-.5;
    for(int j=-1;j<=1;j++) for(int i=-1;i<=1;i++){
      vec2 g=vec2(float(i),float(j)); vec2 cid=id+g; vec2 h=hash22(cid+fl*13.7);
      if(h.x<.45) continue;
      vec2 c = g+(h-.5)*.7-f-.0; float rad=.18+.26*hash21(cid+4.1);
      float d=length(c);
      float disc=smoothstep(rad,rad*(1.-uSoft),d); float ring=exp(-pow((d-rad)/(rad*.08),2.))*(1.-uSoft)*.5;
      float tw=.6+.4*sin(T*.8+hash21(cid)*TAU);
      vec3 lc=mix(P2,P3,hash21(cid+9.));
      col += lc*(disc*.35+ring)*tw*(.5+.5*hash21(cid+2.2))*(1.-.15*fl);
    }
  }
  col += P4*.04;
  return col;
}
`;

  S['caustics-pool'] = `// @mood underwater, summer, fresh, calm, liquid
// @use Light patterns on a pool floor / underwater. Great under product shots or text for "clean, fresh, water". Palette: teal to white.
// @palette #02202e #0a5a7a #19b7d6 #7fe9ff #ffffff
uniform float uCells; //= 4.0 | caustic cell scale
uniform float uSharp; //= 1.0 | sharpness of bright lines
float caust(vec2 q, float ph){
  vec4 v = voronoi2(q, ph); float d = v.y-v.x;
  return pow(1.-smoothstep(0.,.3,d), 2.2);
}
vec3 render(vec2 p, vec2 uv){
  vec2 q = p*uCells + vec2(noise2(p*1.3+circ(.5,0.)), noise2(p*1.3+circ(.5,2.)))*1.2;
  float c = caust(q, PH) *.65 + caust(q*1.7+3.1, PH*1.0+1.7)*.45;
  c = pow(c, 1./uSharp+.0);
  vec3 col = mix(P1, P0, smoothstep(-.6,.9,p.y));
  col = mix(col, P2, .35*(1.-uv.y));
  col += P3*c*.75 + P4*pow(c,3.)*.6;
  float shaft = pow(max(0.,noise2(vec2(p.x*3.+p.y*1.2, 0.)+circ(.4,0.))), 3.);
  col += P3*shaft*.08*smoothstep(-.8,.7,p.y);
  return col*(1.-.3*length(p));
}
`;

  S['metaball-gel'] = `// @mood playful, gel, soft-3d, friendly, candy
// @use Glossy blobs merging and splitting, lit like gel/clay. Good for app/product/kids and "friendly tech". Palette: 2 hues + light.
// @palette #fbe9ff #f7c6ff #7a5cff #ff6fb5 #ffffff
uniform float uBlobs; //= 6 | number of blobs (<= 8)
uniform float uSize; //= 1.0 | blob size
uniform float uGloss; //= 1.0 | highlight strength
vec3 render(vec2 p, vec2 uv){
  float f=0.; vec2 g=vec2(0.); float ci=0.;
  for(int i=0;i<8;i++){
    if(float(i)>=uBlobs) break; float fi=float(i);
    vec2 c = vec2(.33*cos(PH*(1.+mod(fi,2.))+fi*1.9), .55*sin(PH*(1.+mod(fi,3.))*.5+fi*2.3));
    float rr = (.11+.07*hash11(fi+3.))*uSize; vec2 d=p-c; float d2=dot(d,d)+.18*rr*rr;
    float v = rr*rr*1.18/d2; f+=v; g += -2.*rr*rr*1.18*d/(d2*d2); ci += v*hash11(fi*1.3);
  }
  vec3 bgc = mix(P0,P1,smoothstep(-.8,.8,p.y));
  float k = smoothstep(.95,1.15,f);
  vec3 n = normalize(vec3(-g*.006, 1.));
  float ndl = clamp(dot(n, normalize(vec3(-.4,.6,.7))),0.,1.);
  vec3 base = mix(P2,P3, clamp(ci/max(f,1e-3),0.,1.));
  vec3 col = base*(.4+.75*ndl);
  col += P4*pow(max(0.,dot(reflect(-normalize(vec3(-.4,.6,.7)),n), vec3(0.,0.,1.))),24.)*.8*uGloss;
  float fr = pow(1.-clamp(n.z,0.,1.),2.); col += P4*fr*.5;
  col = mix(col, base*.5, smoothstep(2.4,5.,f)*.5);
  vec3 sh = bgc*(1.-.25*exp(-pow((f-.7)/.5,2.))*(1.-k));
  return mix(sh, col, k);
}
`;

  S['halftone-field'] = `// @mood print, pop, poster, editorial, riso, tactile
// @use Flat halftone dot field on paper, slowly swelling. Pairs with the halftone/poster DNA; misregistered second ink gives riso feel.
// @palette #f2ead8 #ece2cc #e8412c #1d3fbf #151515
uniform float uCell; //= 0.034 | dot spacing (p units)
uniform float uMis; //= 0.012 | misregistration of the second ink
uniform float uAngle; //= 0.26 | screen angle (rad)
float inkDots(vec2 p, float ang, float val){
  mat2 R = rot2(ang); vec2 q = R*p/uCell; vec2 f = fract(q)-.5;
  float rad = sqrt(clamp(val,0.,1.))*.72; return 1.-smoothstep(rad-.06, rad+.06, length(f));
}
vec3 render(vec2 p, vec2 uv){
  float a = fbm2(p*1.4+circ(.35,0.), 4); float b = fbm2(p*1.2+vec2(7.,3.)+circ(.35,2.), 4);
  float va = smoothstep(.25,.85,a + .25*sin(p.y*3.+PH)); float vb = smoothstep(.3,.9,b);
  vec3 paper = mix(P0,P1,fbm2(p*7.,3));
  vec3 col = paper;
  col = mix(col, P3, inkDots(p+vec2(uMis,-uMis), uAngle+.52, vb)*.92);
  col = mix(col, col*P2/max(vec3(.001),P0)*.0+P2, inkDots(p, uAngle, va)*.9);
  return col;
}
`;

  S['isometric-cubes'] = `// @mood graphic, isometric, playful, architectural, bold
// @use Isometric cube lattice with shaded faces, each cube breathing in height-colour; strong 3D feel without 3D. Great behind bold type or icons.
// @palette #14122b #3b2f8f #7c6cff #ffd166 #fff6df
uniform float uTile; //= 7.0 | tiles across the short side
uniform float uHeight; //= 1.0 | colour breathing amount
vec3 render(vec2 p, vec2 uv){
  vec2 q = (p + vec2(0.,T*.0)) * uTile; vec2 r = vec2(1.,1.7320508); vec2 h = r*.5;
  vec2 a = mod(q,r)-h, b = mod(q-h,r)-h; vec2 gv = dot(a,a)<dot(b,b)?a:b; vec2 id = q-gv;
  float ang = atan(gv.y,gv.x); float sector = floor(mod(ang-.5235988+TAU, TAU)/(TAU/3.));
  float hv = hash21(id); float br = .5+.5*sin(PH+hv*TAU);
  vec3 top = mix(P3,P4,br*uHeight); vec3 left = mix(P1,P2,.35+.4*br*uHeight); vec3 right = mix(P0,P1,.6+.3*br*uHeight);
  vec3 col = sector<.5 ? top : (sector<1.5 ? right : left);
  float hex = max(abs(gv.y), abs(gv.x)*.8660254+abs(gv.y)*.5);
  float edgeSector = abs(fract(((ang-.5235988+TAU)/(TAU/3.)))-.5);
  float line = smoothstep(.485,.5,edgeSector*1.0+.0) ;
  float seam = smoothstep(.04,.0,abs(fract((ang-.5235988+TAU)/(TAU/3.))-.0)*.5)*0.;
  float ed = abs(fract((ang-.5235988+TAU)/(TAU/3.)+.0)); ed = min(ed,1.-ed);
  col *= 1.-smoothstep(.06,.0,ed)*.5*smoothstep(.0,.2,length(gv));
  col *= .75+.4*smoothstep(1.1,.0,length(p));
  return col;
}
`;

  S['light-rays'] = `// @mood divine, cinematic, hopeful, epic, dusty
// @use Volumetric god-rays from a point (top by default) through haze and dust. Put the hero in the beam. Move the source with params.src (x,y in p units).
// @palette #05070e #101a2e #ffb347 #ffe2a8 #ffffff
uniform float uRays; //= 1.0 | ray contrast
uniform vec2 uSrc; //= 0.0 0.75 | light source position (p units)
uniform float uDustF; //= 1.0 | dust amount
vec3 render(vec2 p, vec2 uv){
  vec2 d = p-uSrc; float r = length(d); float a = atan(d.y,d.x);
  float rays = noise2(vec2(a*9., PH*.6)) *.6 + noise2(vec2(a*23.+3., -PH*.8))*.4;
  rays = pow(clamp(rays*1.25,0.,1.), 2.2*uRays+.6);
  float cone = exp(-pow((a+1.5708)/1.0,2.)) ;  // pointing down
  float fall = exp(-r*1.35);
  vec3 col = mix(P0,P1,smoothstep(-.8,.8,p.y));
  col += P3*rays*fall*cone*1.2 + P2*.35*exp(-r*2.4)*cone;
  col += P4*exp(-r*r*55.)*1.2;                                     // source core
  for(int L=0;L<2;L++){ float fl=float(L); vec2 q=p*(14.+fl*9.)+vec2(circ(.6,fl).x, T*.25*(1.+fl)); vec2 id=floor(q),f=fract(q)-.5; vec2 h=hash22(id+fl*5.);
    float dd=length(f-(h-.5)*.6); float m=smoothstep(.06,.0,dd)*step(.6,hash21(id*1.3+fl)); col += P4*m*rays*fall*cone*uDustF*1.5; }
  return col;
}
`;
})(typeof window !== 'undefined' ? window : globalThis);
