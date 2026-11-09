# GLSL cookbook for Bg3D (write a NEW shader in ~40 lines)

Contract: your string defines `vec3 render(vec2 p, vec2 uv)` returning LINEAR colour. `p` = centred coordinates (short side −0.5..0.5, y up); `uv` 0..1. Globals: `T` time (×speed), `PH` loop phase (radians, 0..TAU over loopPeriod), `ASPECT`, `PORTRAIT`, `SD` seed vec3, palette `P0..P4` and `palGrad(x)`. Header comments: `// @mood`, `// @use`, `// @palette #…×5`, optional `// @camera`, `// @loops`. Params: `uniform float uGlow; //= 0.5 | what it does` → `params.glow`.

Register: `Bg3D.register('my-world', glslString)` (or add to a shaders*.js file).

## Prelude functions you can rely on
hash11/21/22/…, `vnoise`, noise2/fbm (see source), `palGrad`, `cosPal`, `hsv`, `luma`, `tonemap`, `sat`, SDF 2D (`sdBox2`, `sdRoundBox2`, `sdSeg2`), `tri`, `gain`, `remap`, `disc`, `fogMix`, raymarch helpers (`rayDir`, `camRO`, `calcAO`, `softShadow`, `fresnel`, `hitPlaneY`, `envStudio`), `circ(r,ph)` (loop-safe circular motion), `vignetteK`, `tiltMask`. Check `Bg3D.PRELUDE` for the exact list.

## Skeleton A — layered 2D world
```glsl
// @mood calm dusk, layered, soft
// @use Background with 4 ridge layers and a low sun. Headline fits in the upper third.
// @palette #120a24 #3b1b5e #c2417a #ff9a6b #ffe8c7
uniform float uSun; //= 0.5 | sun size
vec3 render(vec2 p, vec2 uv){
  vec3 col = palGrad(uv.y*.9);                                   // sky
  col += P4*exp(-length(p-vec2(.1,-.05))*8.)*uSun;               // sun glow
  for(int i=0;i<4;i++){
    float fi=float(i), k=fi/3.;
    float h = -.15 - .12*fi + .12*vnoise(vec2(p.x*(2.+fi)+T*.02*(1.+fi)+SD.x, fi*7.)) ;
    float m = smoothstep(.004,-.004,p.y-h);
    col = mix(col, mix(P1,P0,k)*(1.-.15*fi), m);                  // nearer = darker (atmospheric perspective)
  }
  return col;
}
```
## Skeleton B — raymarched
```glsl
float map(vec3 q){ /* return signed distance */ }
vec3 render(vec2 p, vec2 uv){
  vec3 ro=camRO(), rd=rayDir(p); float t=0.; for(int i=0;i<80;i++){ float d=map(ro+rd*t); if(d<.002||t>30.) break; t+=d; }
  vec3 col=palGrad(rd.y*.5+.5);                    // sky if miss
  if(t<30.){ vec3 q=ro+rd*t; /* normal by central differences, light, AO, fog */ }
  return col;
}
```
Raymarch checklist: ≤ 80 steps, step cap, fog to hide the far plane, normal via 4 taps, AO via `calcAO`, `fresnel` for glossy edges, tone-map with `tonemap`.

## Looping
Use `circ(r, phase)` as the input to noise instead of raw `T`; or set `loopPeriod` and let the engine crossfade (`loopFade`), or mark `// @loops` when natively periodic (angle-based).

## Recipes (drop-in snippets)
- **Domain warp:** `vec2 q=p; q+=.3*vec2(vnoise(q*2.+T*.1), vnoise(q*2.+5.-T*.1)); float f=vnoise(q*3.);`
- **Ridged noise:** `1.-abs(2.*vnoise(x)-1.)` summed over octaves → mountains, veins.
- **Voronoi edges (caustics):** nearest/second-nearest distance difference → bright lines.
- **Fake glossy normal from height:** `n = normalize(vec3(h(p+e.xy)-h(p-e.xy), h(p+e.yx)-h(p-e.yx), .2))` then `envStudio(reflect(vec3(0,0,-1),n),…)`.
- **Soft shadow blob:** `exp(-dot(q,q)*k)` ellipse under an object.
- **Light leak:** two big offset gaussians, additive, warm colours, slowly drifting.
- **Dither:** engine already dithers the final pixel; don't add your own unless blending in float.

## Debug
- Magenta tile in the gallery = compile error: console prints the GLSL line.
- Common errors: parameter named like a built-in/function (`luma`, `mix`), int/float mixing (`2*x` → `2.*x`), non-constant loop bounds (use constant bounds + `break`), reading `T` in a function declared before the prelude globals (use params).
