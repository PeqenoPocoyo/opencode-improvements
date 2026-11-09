/* transitions.js - GLSL scene transitions + perspective projection helpers. Global: Trans.  Zero dependencies, deterministic.
 *
 *   const tr = Trans.create(1080, 1920);                       // tr.canvas (WebGL2, opaque)
 *   tr.render(canvasA, canvasB, progress, 'whipPan', {angle: 0}); // progress 0..1 ALREADY EASED by you (Trans.meta[name].ease is the recommended curve)
 *   Trans.list() -> [{name, category, ease, frames, sound, params, note}]
 *   Trans.matrix3dFromQuad(w, h, [x0,y0, x1,y1, x2,y2, x3,y3]) -> 'matrix3d(...)' for a DOM element of size w x h (transform-origin: 0 0)
 *   Trans.warp(W, H) -> {canvas, draw(source, quad)}  WebGL perspective quad warp of a canvas onto a quad (pixel corners TL,TR,BR,BL)
 * Render BOTH scenes at the same moment (scene A at its time t, scene B at its pre-rolled time), draw each into a canvas of the same size, then call render.
 * Source canvases are flipped on upload so the output is upright. Output is opaque.
 */
(function (root) {
  'use strict';
  const VS = `#version 300 es
in vec2 pp; out vec2 uv; void main(){ uv = pp*.5+.5; gl_Position = vec4(pp,0.,1.); }`;
  const PRE = `
float h11(float x){ x=fract(x*.1031); x*=x+33.33; x*=x+x; return fract(x); }
float h21(vec2 q){ vec3 r=fract(vec3(q.xyx)*.1031); r+=dot(r,r.yzx+33.33); return fract((r.x+r.y)*r.z); }
vec2 h22(vec2 q){ vec3 r=fract(vec3(q.xyx)*vec3(.1031,.1030,.0973)); r+=dot(r,r.yzx+33.33); return fract((r.xx+r.yz)*r.zy); }
float vn(vec2 q){ vec2 i=floor(q), f=fract(q); f=f*f*(3.-2.*f); return mix(mix(h21(i),h21(i+vec2(1,0)),f.x), mix(h21(i+vec2(0,1)),h21(i+vec2(1,1)),f.x), f.y); }
float fbm(vec2 q){ float a=.5, s=0.; for(int i=0;i<5;i++){ s+=a*vn(q); q=q*2.03+17.1; a*=.5; } return s; }
float luma(vec3 c){ return dot(c, vec3(.2126,.7152,.0722)); }
mat2 rot(float a){ float c=cos(a), s=sin(a); return mat2(c,-s,s,c); }
float asp(){ return res.x/res.y; }
vec4 A(vec2 q){ return texture(tA, clamp(q,0.,1.)); }
vec4 B(vec2 q){ return texture(tB, clamp(q,0.,1.)); }
bool inside(vec2 q){ return q.x>=0. && q.x<=1. && q.y>=0. && q.y<=1.; }
float PI=3.14159265359, TAU=6.28318530718;
// coordinate along direction d (0..1 across the frame)
float along(vec2 q, vec2 d){ float ext=abs(d.x)*.5+abs(d.y)*.5; return dot(q-.5,d)/(2.*ext)+.5; }
`;
  const hex = s => { s = s.replace('#', ''); if (s.length === 3) s = s.split('').map(c => c + c).join(''); return [0, 2, 4].map(i => parseInt(s.slice(i, i + 2), 16) / 255); };

  /* T[name] = { c: category, e: recommended Lab ease, f: frames @30fps, s: sound event, d: defaults, n: note, g: GLSL body defining vec4 tr(vec2 u) } */
  const T = {};
  const add = (name, c, e, f, s, d, n, g) => { T[name] = { c, e, f, s, d, n, g }; };

  /* ----------------------------------------------------------------------------------------------- basic */
  add('crossfade', 'basic', 'inOutSine', 15, 'swipe', {}, 'Plain dissolve. Weakest; dreamy or neutral only.', `vec4 tr(vec2 u){ return mix(A(u),B(u),p); }`);
  add('dipToColor', 'basic', 'inOutCubic', 18, 'whoosh', { color: '#000000', hold: .15 }, 'Fade to a colour and out. Chapter changes (use an accent or bg tone, not black by default).', `
    vec4 tr(vec2 u){ float a=smoothstep(0.,.5-hold*.5,p), b=smoothstep(.5+hold*.5,1.,p); vec3 c = p<.5 ? mix(A(u).rgb,color,a) : mix(color,B(u).rgb,b); return vec4(c,1.); }`);
  add('whiteFlash', 'basic', 'linear', 4, 'impact', { color: '#ffffff', width: .3 }, 'Hard cut hidden by a 2-4 frame flash peaking at the cut. Energy spikes. Max 3 per second.', `
    vec4 tr(vec2 u){ vec3 s = p<.5 ? A(u).rgb : B(u).rgb; float k=1.-clamp(abs(p-.5)/(width*.5),0.,1.); k=k*k*(3.-2.*k); return vec4(mix(s,color,k),1.); }`);
  add('wipeLinear', 'basic', 'inOutCubic', 14, 'swipe', { angle: 0, soft: .05 }, 'Straight wipe along angle (rad). 0 = left to right, 1.5708 = top to bottom.', `
    vec4 tr(vec2 u){ vec2 d=vec2(cos(angle),sin(angle)); float s=along(u,d); float e=p*(1.+2.*soft)-soft; float cov=1.-smoothstep(e-soft,e+soft,s); return mix(A(u),B(u),cov); }`);
  add('wipeRadial', 'basic', 'inOutSine', 18, 'swipe', { soft: .02, start: 0 }, 'Clock wipe from the top. Counters, timers, "time passes".', `
    vec4 tr(vec2 u){ vec2 c=(u-.5)*vec2(asp(),1.); float a=fract(atan(c.x,-c.y)/TAU - start); float e=p*(1.+2.*soft)-soft; return mix(A(u),B(u),1.-smoothstep(e-soft,e+soft,a)); }`);
  add('irisCircle', 'basic', 'inOutCubic', 18, 'whoosh', { cx: .5, cy: .5, soft: .01 }, 'B grows as a circle from (cx,cy). Hero-object reveals; set cx,cy on the object.', `
    vec4 tr(vec2 u){ vec2 c=vec2(cx,cy); float maxR=length(max(c,1.-c)*vec2(asp(),1.)); float d=length((u-c)*vec2(asp(),1.)); float r=p*maxR*1.02; return mix(A(u),B(u),1.-smoothstep(r-soft,r+soft+.002,d)); }`);
  add('irisOut', 'basic', 'inOutCubic', 18, 'whoosh', { cx: .5, cy: .5, soft: .01 }, 'A shrinks to a circle that closes on (cx,cy) revealing B (classic cartoon iris).', `
    vec4 tr(vec2 u){ vec2 c=vec2(cx,cy); float maxR=length(max(c,1.-c)*vec2(asp(),1.)); float d=length((u-c)*vec2(asp(),1.)); float r=(1.-p)*maxR*1.02; return mix(B(u),A(u),1.-smoothstep(r-soft,r+soft+.002,d)); }`);
  add('barnDoors', 'basic', 'inOutCubic', 16, 'whoosh', { horizontal: 0 }, 'A splits in two panels that slide apart (shadowed) revealing B. horizontal=1 splits top/bottom.', `
    vec4 tr(vec2 u){ vec2 q = horizontal>.5 ? u.yx : u; float dx=abs(q.x-.5)*2.; vec2 ua=q; ua.x += (q.x<.5 ? 1. : -1.)*p*.5; if(horizontal>.5) ua=ua.yx;
      if(dx>p) return A(ua); vec3 b=B(u).rgb; b*=1.-.55*(1.-smoothstep(0.,.35,p-dx))*(1.-p); return vec4(b,1.); }`);
  add('blinds', 'basic', 'inOutCubic', 16, 'swipe', { count: 10, angle: 0, soft: .08 }, 'Venetian strips open one by one.', `
    vec4 tr(vec2 u){ vec2 d=vec2(cos(angle),sin(angle)); vec2 n=vec2(-d.y,d.x); float s=along(u,d), c=fract(along(u,n)*count); float e=p*(1.+soft)*1.; float cov=1.-smoothstep(e-soft,e,abs(c-.5)*2.); return mix(A(u),B(u),cov*step(.001,p)); }`);
  add('bars', 'basic', 'inOutCubic', 18, 'swipe', { count: 12, stagger: .5 }, 'Vertical bars of A slide up/down alternately with a stagger, uncovering B.', `
    vec4 tr(vec2 u){ float i=floor(u.x*count); float delay=(i/count)*stagger; float t=clamp((p-delay)/(1.-stagger),0.,1.); t=t*t*(3.-2.*t); float dir=mod(i,2.)*2.-1.; vec2 ua=vec2(u.x,u.y+dir*t*1.02); return inside(ua)?A(ua):B(u); }`);

  /* ----------------------------------------------------------------------------------------------- camera / motion */
  add('slidePush', 'motion', 'inOutCubic', 14, 'whoosh', { angle: 0 }, 'A is pushed off by B. angle 0 = content moves left.', `
    vec4 tr(vec2 u){ vec2 d=vec2(cos(angle),sin(angle)); vec2 ua=u+d*p; return inside(ua)?A(ua):B(u+d*(p-1.)); }`);
  add('parallaxSlide', 'motion', 'inOutCubic', 18, 'whoosh', { angle: 0, shadow: .5 }, 'A slides off fast, B arrives slower underneath with shadow = depth.', `
    vec4 tr(vec2 u){ vec2 d=vec2(cos(angle),sin(angle)); vec2 ua=u+d*p; if(inside(ua)) return A(ua);
      vec2 ub=u+d*(p-1.)*.35; vec3 b=B(ub).rgb; float edge=along(ua,d)-1.; b*=1.-shadow*(1.-smoothstep(0.,.25,edge))*(1.-p*.6); return vec4(b*(1.-(1.-p)*.35),1.); }`);
  add('whipPan', 'motion', 'whip', 10, 'whip', { angle: 0, blur: 80 }, 'Fast pan with directional motion blur on both scenes. 8-14 frames; use curve "whip". Pre-sound: whip.', `
    vec4 push(vec2 u,float k){ vec2 d=vec2(cos(angle),sin(angle)); vec2 ua=u+d*k; return inside(ua)?A(ua):B(u+d*(k-1.)); }
    vec4 tr(vec2 u){ float amt=sin(p*PI); vec2 d=vec2(cos(angle),sin(angle)); vec3 s=vec3(0.); float tw=0.; for(int i=0;i<14;i++){ float k=float(i)/13.-.5; s+=push(u+d*k*amt*blur/res.x*1.0, p).rgb; tw+=1.; } return vec4(s/tw,1.); }`);
  add('zoomThrough', 'motion', 'inCubic', 14, 'whoosh', { strength: 2.6, blur: .28 }, 'Camera flies through A into B: A zooms in with radial blur, B settles from zoomed-in. Match the zoom centre to an object.', `
    vec4 tr(vec2 u){ float amt=sin(p*PI)*blur; vec2 c=vec2(.5); vec3 s=vec3(0.); for(int i=0;i<16;i++){ float k=float(i)/15.; vec2 q=c+(u-c)*(1.-amt*k*.5);
        float zA=1.+(strength-1.)*p*p, zB=mix(strength,1.,smoothstep(0.,1.,p)); vec3 a=A(c+(q-c)/zA).rgb, b=B(c+(q-c)/zB).rgb; s+=mix(a,b,smoothstep(.38,.62,p)); } return vec4(s/16.,1.); }`);
  add('zoomOutIn', 'motion', 'inOutCubic', 18, 'whoosh', { strength: 2.2 }, 'A scales down and away revealing B that scales up into place (pull-back then push).', `
    vec4 tr(vec2 u){ float zA=1.-p*(1.-1./strength); vec2 ua=.5+(u-.5)/zA; if(inside(ua)&&p<.75) return mix(A(ua),B(u),smoothstep(.45,.75,p)); float zB=mix(1./strength,1.,p); vec2 ub=.5+(u-.5)/zB; return inside(ub)?B(ub):B(u); }`);
  add('spinZoom', 'motion', 'inOutCubic', 18, 'whoosh', { turns: .25, strength: 1.7 }, 'Rotate and zoom A out, B in with the opposite spin.', `
    vec4 tr(vec2 u){ vec2 c=(u-.5)*vec2(asp(),1.); vec2 ca=rot(p*turns*TAU)*c/(1.+p*(strength-1.)); vec2 cb=rot(-(1.-p)*turns*TAU)*c/(1.+(1.-p)*(strength-1.)); vec2 ua=ca/vec2(asp(),1.)+.5, ub=cb/vec2(asp(),1.)+.5; return mix(A(ua),B(ub),smoothstep(.4,.6,p)); }`);
  add('radialBlurSpin', 'motion', 'inOutCubic', 16, 'whoosh', { turns: .5, blur: .18 }, 'Spin around the centre with rotational blur, swapping scenes mid-spin.', `
    vec4 tr(vec2 u){ vec2 c=(u-.5)*vec2(asp(),1.); float amt=sin(p*PI)*blur; vec3 s=vec3(0.); for(int i=0;i<16;i++){ float k=float(i)/15.-.5; float a=amt*k; vec2 ca=rot(p*turns*TAU+a)*c, cb=rot((p-1.)*turns*TAU+a)*c;
        s+=mix(A(ca/vec2(asp(),1.)+.5).rgb,B(cb/vec2(asp(),1.)+.5).rgb,smoothstep(.4,.6,p)); } return vec4(s/16.,1.); }`);
  add('perspectiveTilt', '3d', 'inOutCubic', 20, 'whoosh', { tilt: 1.25, bg: '#0a0a0a' }, 'A rotates away about a vertical axis in perspective while B rotates in from the other side.', `
    vec4 plane(sampler2D t,vec2 u,float th,out float depth){ float f=1.4; vec2 q=(u-.5); q.x*=asp(); q/= asp(); float tn=tan(th); float den=f-q.x*tn; depth=1e9; if(den<=.05) return vec4(0.); float tt=f/den; float X=tt*q.x/cos(th), Y=tt*q.y; vec2 uv2=vec2(X,Y)+.5; if(!inside(uv2)) return vec4(0.); depth=tt; return vec4(texture(t,uv2).rgb,1.); }
    vec4 tr(vec2 u){ float dA, dB; vec4 a=plane(tA,u,p*tilt,dA), b=plane(tB,u,-(1.-p)*tilt,dB); vec3 base=bg; vec3 col=base; if(b.a>0.) col=b.rgb*mix(.55,1.,p); if(a.a>0. && (b.a<.5||dA<=dB)) col=a.rgb*mix(1.,.55,p); return vec4(col,1.); }`);
  add('cubeRotate', '3d', 'inOutCubic', 20, 'whoosh', { bg: '#050505' }, 'Fake cube turn: A and B are two faces squeezed with perspective and shaded at the seam.', `
    vec4 tr(vec2 u){ float s1=1.-p; vec3 col=bg; if(u.x<s1){ float s=u.x/max(s1,1e-3); vec2 ua=vec2(s,.5+(u.y-.5)/(1.+.28*s*p)); if(inside(ua)) col=A(ua).rgb*(1.-.45*s*p); } else { float s=(u.x-s1)/max(p,1e-3); vec2 ub=vec2(s,.5+(u.y-.5)/(1.+.28*(1.-s)*(1.-p))); if(inside(ub)) col=B(ub).rgb*(1.-.45*(1.-s)*(1.-p)); } return vec4(col,1.); }`);
  add('flip', '3d', 'inOutCubic', 18, 'whoosh', { bg: '#0a0a0a', axis: 0 }, 'Card flip around the vertical (axis 0) or horizontal (axis 1) centre line.', `
    vec4 tr(vec2 u){ vec2 q = axis>.5 ? u.yx : u; float k=cos(p*PI); float sc=max(abs(k),1e-3); vec2 qa=vec2(.5+(q.x-.5)/sc,q.y); vec2 persp=vec2(0.); float shade=mix(.55,1.,abs(k)); vec3 col=bg;
      if(inside(qa)){ vec2 s=axis>.5?qa.yx:qa; col=(p<.5?A(s):B(s)).rgb*shade; } return vec4(col,1.); }`);
  add('mirrorFold', '3d', 'inOutCubic', 16, 'whoosh', { }, 'A squeezes into the vertical centre line, B opens from it.', `
    vec4 tr(vec2 u){ float w=1.-p; vec2 ua=vec2(.5+(u.x-.5)/max(w,1e-3),u.y); if(inside(ua)) return A(ua); float x=abs(u.x-.5)*2.; return vec4(B(u).rgb*(1.-.4*smoothstep(0.,.3,x-w)*(1.-p)),1.); }`);
  add('pagePeel', '3d', 'inCubic', 22, 'swipe', { }, 'Page folds over from the right edge showing a darkened back side, then leaves B.', `
    vec4 tr(vec2 u){ float e=1.-p; if(u.x>=e){ vec3 b=B(u).rgb; b*=1.-.5*(1.-smoothstep(0.,.18,u.x-e))*step(.001,p); return vec4(b,1.); }
      if(u.x>2.*e-1.){ float x0=2.*e-u.x; vec3 a=A(vec2(x0,u.y)).rgb; float d=e-u.x; a=mix(a,vec3(luma(a)),.5)*mix(.5,.9,smoothstep(0.,.3,d)); a+=.25*smoothstep(.04,0.,d); return vec4(a,1.); } return A(u); }`);
  add('doorOpen', '3d', 'inOutCubic', 20, 'whoosh', { bg: '#000000' }, 'A is a double door hinged at the edges, swinging open in perspective onto B.', `
    vec4 tr(vec2 u){ float half_=.5*(1.-p); float dx=min(u.x,1.-u.x); vec3 back=mix(bg*.5,B(u).rgb,smoothstep(0.,.25,p));
      if(dx>=half_) return vec4(back,1.);
      float s=dx/max(half_,1e-4); float shrink=1.-.4*p*s; float sx=s*.5; sx=(u.x<.5)?sx:1.-sx; float sy=.5+(u.y-.5)/shrink;
      if(abs(u.y-.5)*2.>shrink) return vec4(back,1.);
      vec3 c=A(vec2(sx,sy)).rgb*(1.-.35*p*s); return vec4(c,1.); }`);

  /* ----------------------------------------------------------------------------------------------- dissolves */
  add('rippleDissolve', 'dissolve', 'inOutSine', 22, 'shimmer', { cx: .5, cy: .5, freq: 22, amp: .03 }, 'Ring wave expands from a point; B appears inside the ring (water, sonar, glass).', `
    vec4 tr(vec2 u){ vec2 c=vec2(cx,cy); vec2 d=(u-c)*vec2(asp(),1.); float r=length(d); float front=p*.8; float w=sin((r-front)*freq)*amp*exp(-abs(r-front)*5.)*sin(p*PI); vec2 o2=normalize(d+1e-5)*w/vec2(asp(),1.); float cov=1.-smoothstep(front-.06,front+.06,r); return mix(A(u+o2),B(u+o2),cov); }`);
  add('liquidWarp', 'dissolve', 'inOutSine', 24, 'whoosh', { amount: .12, scale: 2.5 }, 'Both scenes melt with noise displacement while crossfading.', `
    vec4 tr(vec2 u){ float k=sin(p*PI); vec2 n=vec2(fbm(u*scale+seed+p), fbm(u*scale+vec2(7.3,2.1)-p))-.5; vec2 ua=u+n*amount*k*2.*p, ub=u-n*amount*k*2.*(1.-p); float m=smoothstep(.3,.7,p+(fbm(u*scale*1.7+seed)-.5)*.35); return mix(A(ua),B(ub),m); }`);
  add('pixelDissolve', 'dissolve', 'linear', 16, 'glitch', { size: 18, pixelate: 1 }, 'Blocks switch at random times; the swapping blocks show pixelated.', `
    vec4 tr(vec2 u){ vec2 cell=floor(u*res/size); float h=h21(cell+seed); vec2 cu=(cell+.5)*size/res; float near=smoothstep(.12,0.,abs(p-h)); vec2 q=mix(u,cu,near*pixelate); return mix(A(q),B(q),step(h,p)); }`);
  add('halftoneDissolve', 'dissolve', 'inOutCubic', 20, 'swipe', { size: 16, angle: .5236 }, 'B appears as growing halftone dots until they merge (print/poster looks).', `
    vec4 tr(vec2 u){ vec2 q=rot(angle)*(u*res)/size; vec2 f=fract(q)-.5; float d=length(f); float lb=luma(B(u).rgb); float R=p*.78+(lb-.5)*.18*sin(p*PI); float aa=fwidth(d)+.02; float cov=1.-smoothstep(R-aa,R+aa,d); return mix(A(u),B(u),cov); }`);
  add('noiseDissolve', 'dissolve', 'inOutCubic', 20, 'riser', { scale: 3, edge: .07, color: '#ffb04a' }, 'Organic fbm dissolve with a glowing burning edge.', `
    vec4 tr(vec2 u){ float n=fbm(u*scale*vec2(asp(),1.)+seed); float t=p*(1.+edge*2.)-edge; float cov=step(n,t); float g=smoothstep(edge,0.,abs(n-t))*step(.002,p)*step(p,.998); vec3 c=mix(A(u).rgb,B(u).rgb,cov); return vec4(c+color*g*1.4,1.); }`);
  add('inkBleed', 'dissolve', 'inOutCubic', 24, 'whoosh', { scale: 8 }, 'B spreads like ink from several seeds with irregular edges.', `
    vec4 tr(vec2 u){ float dmin=9.; for(int i=0;i<5;i++){ vec2 c=h22(vec2(float(i)*3.7,seed+1.3)); dmin=min(dmin,length((u-c)*vec2(asp(),1.))); } float f=dmin+(fbm(u*scale+seed)-.5)*.22; float R=p*.95; return mix(A(u),B(u),1.-smoothstep(R-.015,R+.015,f)); }`);
  add('paperTear', 'dissolve', 'inOutCubic', 12, 'paper-rip', { angle: 0, rough: .05, fiber: .014 }, 'A is torn away along a ragged line: white fibre edge on A, soft shadow on B. Pair with a rip sound and a 3-frame flash.', `
    vec4 tr(vec2 u){ vec2 d=vec2(cos(angle),sin(angle)); vec2 n=vec2(-d.y,d.x); float s=along(u,d); float jag=(fbm(vec2(along(u,n)*9.,seed))-.5)*rough*2.+(fbm(vec2(along(u,n)*38.,seed+4.))-.5)*rough*.5; float e=p*(1.+rough*4.)-rough*2.+jag;
      if(s<e){ vec3 b=B(u).rgb; b*=1.-.5*smoothstep(.05,0.,e-s)*step(.001,p); return vec4(b,1.); }
      float f=s-e; if(f<fiber*(.6+.8*fbm(u*vec2(60.,60.)+seed))) return vec4(vec3(.95,.93,.88)*(.9+.1*vn(u*300.)),1.);
      vec2 ua=u+d*.04*smoothstep(0.,.2,f)*p; return vec4(A(ua).rgb,1.); }`);
  add('brushWipe', 'dissolve', 'inOutCubic', 18, 'swipe', { angle: -.15, rough: .05, bands: 6 }, 'Painted strokes sweep across in staggered bands with rough edges.', `
    vec4 tr(vec2 u){ vec2 d=vec2(cos(angle),sin(angle)); vec2 n=vec2(-d.y,d.x); float s=along(u,d), c=along(u,n); float b=floor(c*bands); float delay=h11(b+seed)*.35; float t=clamp((p-delay)/.65,0.,1.); float e=t*1.2-.1+(fbm(u*14.+seed)-.5)*rough*4.; return mix(A(u),B(u),step(s,e)); }`);
  add('hexGrid', 'dissolve', 'inOutCubic', 20, 'tick', { size: 14 }, 'Hexagonal cells open to B at random times (tech, honeycomb).', `
    vec2 hc(vec2 q){ vec2 r=vec2(1.,1.7320508); vec2 h=r*.5; vec2 a=mod(q,r)-h, b=mod(q-h,r)-h; return dot(a,a)<dot(b,b)?a:b; }
    vec4 tr(vec2 u){ vec2 g=u*vec2(asp(),1.)*res.y/(res.y/size*1.); g=u*vec2(asp(),1.)*size; vec2 l=hc(g); vec2 id=g-l; float h=h21(id+seed); float t=clamp((p*1.5-h*.5)/.5,0.,1.); float cov=1.-smoothstep(t*.62-.03,t*.62+.03,length(l)); return mix(A(u),B(u),cov); }`);
  add('gridFlip', 'dissolve', 'inOutCubic', 22, 'tick', { cols: 6, rows: 10, bg: '#0a0a0a' }, 'Tiles flip over one by one from the centre outward.', `
    vec4 tr(vec2 u){ vec2 g=vec2(cols,rows); vec2 id=floor(u*g), f=fract(u*g); float d=length((id+.5)/g-.5); float t=clamp(p*1.8-d*1.1,0.,1.); float k=cos(t*PI); float sc=max(abs(k),1e-3); float lx=(f.x-.5)/sc+.5; if(lx<0.||lx>1.) return vec4(bg,1.); vec2 q=(id+vec2(lx,f.y))/g; return vec4((t<.5?A(q):B(q)).rgb*mix(.6,1.,abs(k)),1.); }`);
  add('shapeFlood', 'dissolve', 'inOutCubic', 20, 'impact', { cx: .5, cy: .5, color: '#ff3b6b' }, 'A flat colour floods from a point over A, then B opens from the same point (brand-colour transition).', `
    vec4 tr(vec2 u){ vec2 c=vec2(cx,cy); float maxR=length(max(c,1.-c)*vec2(asp(),1.))*1.05; float d=length((u-c)*vec2(asp(),1.)); vec3 s=A(u).rgb; float r1=clamp(p*2.,0.,1.)*maxR, r2=clamp(p*2.-1.,0.,1.)*maxR;
      s=mix(s,color,1.-smoothstep(r1-.01,r1+.01,d)); s=mix(s,B(u).rgb,(1.-smoothstep(r2-.01,r2+.01,d))*step(.5,p)); return vec4(s,1.); }`);

  /* ----------------------------------------------------------------------------------------------- glitch / light / texture */
  add('glitchSwap', 'glitch', 'linear', 10, 'glitch', { blocks: 16, rgb: .02 }, 'Rows switch at random times with horizontal tears and RGB split.', `
    vec4 tr(vec2 u){ float row=floor(u.y*blocks); float h=h11(row+seed*3.1+floor(p*14.)); float k=sin(p*PI); float sh=(h11(row*3.7+floor(p*10.))-.5)*.25*k; float sw=step(.5,p+(h-.5)*.6); vec2 q=u+vec2(sh,0.); float s=rgb*k;
      vec3 a=vec3(A(q+vec2(s,0.)).r,A(q).g,A(q-vec2(s,0.)).b), b=vec3(B(q+vec2(s,0.)).r,B(q).g,B(q-vec2(s,0.)).b); return vec4(mix(a,b,sw),1.); }`);
  add('dataMoshLite', 'glitch', 'inOutCubic', 14, 'glitch', { block: 48, amount: .5 }, 'Blocks smear with random motion vectors while switching (datamosh look).', `
    vec4 tr(vec2 u){ vec2 cell=floor(u*res/block); vec2 v=(h22(cell+seed)-.5)*amount*sin(p*PI)*.35; float cov=step(h21(cell+3.1),p); return mix(A(u+v*p),B(u+v*(p-1.)),cov); }`);
  add('vhsRewind', 'glitch', 'inOutSine', 14, 'glitch', { bands: 14, bleed: .02 }, 'Tracking tears, colour bleed and noise like a tape rewind.', `
    vec4 tr(vec2 u){ float k=pow(sin(p*PI),.6); float band=floor(u.y*bands+seed); float r=h11(band+floor(p*24.)); float sh=(r-.5)*.3*k*step(.5,h11(band*1.7+floor(p*24.))); vec2 q=u+vec2(sh,0.); float m=smoothstep(.45,.55,p);
      vec3 a=vec3(A(q+vec2(bleed*k,0.)).r,A(q).g,A(q-vec2(bleed*k,0.)).b), b=vec3(B(q+vec2(bleed*k,0.)).r,B(q).g,B(q-vec2(bleed*k,0.)).b); vec3 c=mix(a,b,m);
      float bar=smoothstep(.02,0.,abs(fract(u.y*.5-p*3.)-.5)-.45); c+=bar*.25*k; c+=(h21(u*res+floor(p*30.))-.5)*.25*k; return vec4(c,1.); }`);
  add('scanlineWipe', 'glitch', 'inOutCubic', 14, 'zap', { angle: 1.5708, lines: 120, soft: .02 }, 'Wipe whose edge is a band of interlaced scanlines and a bright line.', `
    vec4 tr(vec2 u){ vec2 d=vec2(cos(angle),sin(angle)); float s=along(u,d); float e=p*1.12-.06; float band=.08; float cov=step(s,e); float inb=1.-smoothstep(0.,band,abs(s-e)); float il=step(.5,fract(u.y*lines)); cov=mix(cov,il,inb*step(abs(s-e),band));
      vec3 c=mix(A(u).rgb,B(u).rgb,cov); c+=vec3(.9,1.,1.)*smoothstep(.008,0.,abs(s-e))*.9; return vec4(c,1.); }`);
  add('glassRefract', 'light', 'inOutCubic', 20, 'shimmer', { angle: 0, width: .2, ior: .07 }, 'A glass edge sweeps across, refracting and dispersing colours; A on one side, B on the other.', `
    vec4 tr(vec2 u){ vec2 d=vec2(cos(angle),sin(angle)); float s=along(u,d); float e=p*(1.+2.*width)-width; float x=(s-e)/width; float m=exp(-x*x*2.5); vec2 off=d*x*m*ior; float cov=1.-smoothstep(-.05,.05,x*width);
      vec3 a=vec3(A(u+off*1.0).r,A(u+off*1.25).g,A(u+off*1.5).b), b=vec3(B(u+off*1.0).r,B(u+off*1.25).g,B(u+off*1.5).b); vec3 c=mix(a,b,cov); c+=m*.08; return vec4(c,1.); }`);
  add('lightLeakWipe', 'light', 'inOutSine', 20, 'whoosh', { angle: 0, soft: .35, color: '#ff8a3d' }, 'Soft wipe whose edge is a warm light leak.', `
    vec4 tr(vec2 u){ vec2 d=vec2(cos(angle),sin(angle)); float s=along(u,d); float e=p*(1.+2.*soft)-soft; float cov=1.-smoothstep(e-soft,e+soft,s); float band=exp(-pow((s-e)/(soft*.6),2.)); vec3 c=mix(A(u).rgb,B(u).rgb,cov); c=1.-(1.-c)*(1.-color*band*1.1*(.6+.4*fbm(u*4.+seed))); return vec4(c,1.); }`);
  add('filmBurn', 'light', 'inOutSine', 22, 'riser', { color: '#ff7a1a', intensity: 1.6 }, 'Film-burn bloom: orange-white burn swells over A and clears onto B.', `
    vec4 tr(vec2 u){ float n=fbm(u*3.+seed+p*2.); float b=sin(p*PI); b=b*b; vec3 s=mix(A(u).rgb,B(u).rgb,smoothstep(.45,.55,p)); float g=b*(.35+1.2*n*n); vec3 c=s+color*g*intensity+vec3(1.)*pow(b,4.)*.8*n; return vec4(c,1.); }`);
  add('lumaWipe', 'light', 'inOutSine', 20, 'swipe', { invert: 0, soft: .1 }, 'The luminance of A decides what changes first (dark areas first; invert=1 for bright first).', `
    vec4 tr(vec2 u){ float L=luma(A(u).rgb); L=mix(L,1.-L,invert); float t=p*(1.+2.*soft)-soft; return mix(A(u),B(u),smoothstep(L-soft,L+soft,t)); }`);
  add('kaleidoscope', 'light', 'inOutSine', 20, 'shimmer', { segments: 6 }, 'Both scenes fold through a kaleidoscope mid-transition.', `
    vec4 tr(vec2 u){ float k=sin(p*PI); vec2 c=(u-.5)*vec2(asp(),1.); float a=atan(c.y,c.x)+p*1.2; float r=length(c); float s=TAU/segments; a=abs(mod(a,s)-s*.5); vec2 f=vec2(cos(a),sin(a))*r/vec2(asp(),1.)+.5; vec2 q=mix(u,f,k); q=1.-abs(1.-mod(q,2.)); return mix(A(q),B(q),smoothstep(.4,.6,p)); }`);

  const list = () => Object.keys(T).map(k => ({ name: k, category: T[k].c, ease: T[k].e, frames: T[k].f, sound: T[k].s, params: T[k].d, note: T[k].n }));
  const meta = {}; Object.keys(T).forEach(k => meta[k] = { category: T[k].c, ease: T[k].e, frames: T[k].f, sound: T[k].s, params: T[k].d, note: T[k].n });

  function create(w, h) {
    const canvas = document.createElement('canvas'); canvas.width = w; canvas.height = h;
    const gl = canvas.getContext('webgl2', { preserveDrawingBuffer: true, antialias: false, alpha: false });
    if (!gl) throw new Error('Trans: WebGL2 is not available');
    const vbo = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, vbo); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    const vao = gl.createVertexArray(); gl.bindVertexArray(vao); gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
    const progs = {}; const typeOf = v => typeof v === 'number' ? 'float' : typeof v === 'string' ? 'vec3' : 'vec' + v.length;
    function prog(name) {
      if (progs[name]) return progs[name]; const t = T[name]; if (!t) throw new Error('Trans: unknown transition "' + name + '". Known: ' + Object.keys(T).join(', '));
      let decl = ''; for (const k in t.d) decl += `uniform ${typeOf(t.d[k])} ${k};\n`;
      const fs = `#version 300 es\nprecision highp float;\nin vec2 uv; out vec4 o;\nuniform sampler2D tA; uniform sampler2D tB; uniform vec2 res; uniform float p; uniform float seed;\n${decl}${PRE}\n${t.g}\nvoid main(){ o=vec4(tr(uv).rgb,1.); }`;
      const mk = (ty, src) => { const s = gl.createShader(ty); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error('Trans shader "' + name + '": ' + gl.getShaderInfoLog(s)); return s; };
      const pr = gl.createProgram(); gl.attachShader(pr, mk(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, mk(gl.FRAGMENT_SHADER, fs)); gl.bindAttribLocation(pr, 0, 'pp'); gl.linkProgram(pr);
      if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) throw new Error('Trans link "' + name + '": ' + gl.getProgramInfoLog(pr));
      const loc = {}; ['tA', 'tB', 'res', 'p', 'seed'].forEach(k => loc[k] = gl.getUniformLocation(pr, k)); for (const k in t.d) loc[k] = gl.getUniformLocation(pr, k);
      return progs[name] = { pr, loc, d: t.d };
    }
    const mkTex = () => { const t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE); return t; };
    const texA = mkTex(), texB = mkTex();
    const up = (tex, src) => { gl.bindTexture(gl.TEXTURE_2D, tex); gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, src); gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false); };
    return {
      canvas, gl,
      render(from, to, progress, name, params) {
        params = params || {}; const P = prog(name); up(texA, from); up(texB, to);
        gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.viewport(0, 0, w, h); gl.useProgram(P.pr); gl.bindVertexArray(vao);
        gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, texA); gl.uniform1i(P.loc.tA, 0);
        gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, texB); gl.uniform1i(P.loc.tB, 1);
        gl.uniform2f(P.loc.res, w, h); gl.uniform1f(P.loc.p, Math.min(1, Math.max(0, progress))); gl.uniform1f(P.loc.seed, params.seed != null ? params.seed : 3.7);
        for (const k in P.d) { const v = params[k] !== undefined ? params[k] : P.d[k], L = P.loc[k]; if (L == null) continue; if (typeof v === 'string') { const c = hex(v); gl.uniform3f(L, c[0], c[1], c[2]); } else if (Array.isArray(v)) gl['uniform' + v.length + 'fv'](L, v); else gl.uniform1f(L, v); }
        gl.drawArrays(gl.TRIANGLES, 0, 3); return canvas;
      },
      dispose() { const e = gl.getExtension('WEBGL_lose_context'); if (e) e.loseContext(); }
    };
  }

  /* ---------------------------------------------------------------------------------------------- projection helpers */
  // Homography mapping the unit rectangle corners (0,0),(w,0),(w,h),(0,h) to quad q=[x0,y0,x1,y1,x2,y2,x3,y3] (TL,TR,BR,BL). Returns 3x3 row-major [h11..h33].
  function homography(w, h, q) {
    const src = [[0, 0], [w, 0], [w, h], [0, h]], A = [], b = [];
    for (let i = 0; i < 4; i++) { const [x, y] = src[i], X = q[2 * i], Y = q[2 * i + 1];
      A.push([x, y, 1, 0, 0, 0, -x * X, -y * X]); b.push(X); A.push([0, 0, 0, x, y, 1, -x * Y, -y * Y]); b.push(Y); }
    const n = 8; for (let i = 0; i < n; i++) { let m = i; for (let r = i + 1; r < n; r++) if (Math.abs(A[r][i]) > Math.abs(A[m][i])) m = r; [A[i], A[m]] = [A[m], A[i]]; [b[i], b[m]] = [b[m], b[i]];
      for (let r = i + 1; r < n; r++) { const f = A[r][i] / A[i][i]; for (let c = i; c < n; c++) A[r][c] -= f * A[i][c]; b[r] -= f * b[i]; } }
    const x = new Array(n); for (let i = n - 1; i >= 0; i--) { let s = b[i]; for (let c = i + 1; c < n; c++) s -= A[i][c] * x[c]; x[i] = s / A[i][i]; }
    return [x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], 1];
  }
  const apply = (H, x, y) => { const W = H[6] * x + H[7] * y + H[8]; return [(H[0] * x + H[1] * y + H[2]) / W, (H[3] * x + H[4] * y + H[5]) / W]; };
  function matrix3dFromQuad(w, h, q) { const H = homography(w, h, q); return `matrix3d(${H[0]},${H[3]},0,${H[6]},${H[1]},${H[4]},0,${H[7]},0,0,1,0,${H[2]},${H[5]},0,${H[8]})`; }

  // WebGL perspective warp of a source canvas onto a quad (pixel corners TL,TR,BR,BL) in a W x H output. Background transparent-black unless bg given.
  function warp(W, H) {
    const canvas = document.createElement('canvas'); canvas.width = W; canvas.height = H; const gl = canvas.getContext('webgl2', { preserveDrawingBuffer: true, antialias: true, alpha: true, premultipliedAlpha: false });
    const vs = `#version 300 es\nin vec2 pp; out vec2 px; uniform vec2 R; void main(){ px=(pp*.5+.5)*R; px.y=R.y-px.y; gl_Position=vec4(pp,0.,1.); }`;
    const fs = `#version 300 es\nprecision highp float; in vec2 px; out vec4 o; uniform sampler2D t; uniform mat3 Hi; uniform vec2 S; uniform vec4 bg;
      void main(){ vec3 q=Hi*vec3(px,1.); vec2 s=q.xy/q.z; if(s.x<0.||s.y<0.||s.x>S.x||s.y>S.y){ o=bg; return; } vec2 e=min(s,S-s); float a=smoothstep(0.,1.2,min(e.x,e.y)); o=mix(bg,texture(t,s/S),a); }`;
    const mk = (ty, s) => { const sh = gl.createShader(ty); gl.shaderSource(sh, s); gl.compileShader(sh); if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(sh)); return sh; };
    const pr = gl.createProgram(); gl.attachShader(pr, mk(gl.VERTEX_SHADER, vs)); gl.attachShader(pr, mk(gl.FRAGMENT_SHADER, fs)); gl.bindAttribLocation(pr, 0, 'pp'); gl.linkProgram(pr);
    const vbo = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, vbo); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW); gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
    const tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, tex); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    return { canvas, draw(source, quad, bg) {
      const sw = source.width, sh = source.height, Hm = homography(sw, sh, quad);
      // inverse of the 3x3 (row-major) -> column-major for GL
      const [a, b, c, d, e, f, g, h, i] = Hm; const det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g);
      const inv = [(e * i - f * h), (c * h - b * i), (b * f - c * e), (f * g - d * i), (a * i - c * g), (c * d - a * f), (d * h - e * g), (b * g - a * h), (a * e - b * d)].map(v => v / det);
      gl.bindTexture(gl.TEXTURE_2D, tex); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, source);
      gl.viewport(0, 0, W, H); gl.useProgram(pr); gl.uniform2f(gl.getUniformLocation(pr, 'R'), W, H); gl.uniform2f(gl.getUniformLocation(pr, 'S'), sw, sh);
      gl.uniformMatrix3fv(gl.getUniformLocation(pr, 'Hi'), false, [inv[0], inv[3], inv[6], inv[1], inv[4], inv[7], inv[2], inv[5], inv[8]]);
      const B = bg || [0, 0, 0, 0]; gl.uniform4f(gl.getUniformLocation(pr, 'bg'), B[0], B[1], B[2], B[3]); gl.uniform1i(gl.getUniformLocation(pr, 't'), 0); gl.drawArrays(gl.TRIANGLES, 0, 3); return canvas; } };
  }

  root.Trans = { create, list, meta, matrix3dFromQuad, homography, applyHomography: apply, warp, ease: n => (meta[n] || {}).ease || 'inOutCubic', names: Object.keys(T) };
})(typeof window !== 'undefined' ? window : globalThis);
