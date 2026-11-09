/* fx.js - WebGL2 post-processing for seek(t) scenes. Global: FX.  Zero dependencies, deterministic (no clock, no Math.random).
 *
 *   const fx = FX.create(1080, 1920);                    // fx.canvas = offscreen WebGL2 canvas; append it to the stage if you want it visible
 *   fx.apply(sourceCanvas, [ {pass:'bloom', intensity:.9}, {pass:'grain', amount:.08}, {pass:'vignette'} ], t);
 *   // result is now in fx.canvas (opaque). drawImage(fx.canvas,0,0) into a 2D canvas or show fx.canvas directly.
 *
 * source: <canvas> | <img> | ImageBitmap | <video>. Everything is display-referred sRGB (no linear workflow): thresholds and
 * grading are applied to the encoded values, which is what looks right for stylised motion graphics.
 * t (seconds) and fps (default window.VIDEO.fps or 30) seed grain/glitch per FRAME: the same t always gives the same noise.
 * FX.list() -> [{name, params:{default values}, note}]  FX.chains -> ready-made pass chains by look.
 */
(function (root) {
  'use strict';
  const VS = `#version 300 es
in vec2 p; out vec2 uv; void main(){ uv = p*.5+.5; gl_Position = vec4(p,0.,1.); }`;

  const PRE = `
float h11(float p){ p=fract(p*.1031); p*=p+33.33; p*=p+p; return fract(p); }
float h21(vec2 p){ vec3 q=fract(vec3(p.xyx)*.1031); q+=dot(q,q.yzx+33.33); return fract((q.x+q.y)*q.z); }
vec2 h22(vec2 p){ vec3 q=fract(vec3(p.xyx)*vec3(.1031,.1030,.0973)); q+=dot(q,q.yzx+33.33); return fract((q.xx+q.yz)*q.zy); }
float vn(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.-2.*f);
  return mix(mix(h21(i),h21(i+vec2(1,0)),f.x), mix(h21(i+vec2(0,1)),h21(i+vec2(1,1)),f.x), f.y); }
float fbm(vec2 p){ float a=.5, s=0.; for(int i=0;i<5;i++){ s+=a*vn(p); p=p*2.03+17.1; a*=.5; } return s; }
float luma(vec3 c){ return dot(c, vec3(.2126,.7152,.0722)); }
vec4 T(vec2 q){ return texture(u_tex, q); }
mat2 rot(float a){ float c=cos(a), s=sin(a); return mat2(c,-s,s,c); }
float asp(){ return u_res.x/u_res.y; }
`;

  const hex = s => { s = s.replace('#', ''); if (s.length === 3) s = s.split('').map(c => c + c).join(''); return [0, 2, 4].map(i => parseInt(s.slice(i, i + 2), 16) / 255); };

  /* ---------------------------------------------------------------- single-draw passes: {d: defaults, f: GLSL main body, note} */
  const P = {
    chromatic: { d: { amount: .004, angle: 0, radial: 1 }, note: 'RGB split. radial=1: grows toward the edges (lens); 0: linear along angle. Animate amount on hits (0.002 idle, 0.012 on a hit).', f: `
      void main(){ vec2 c=uv-.5; vec2 dir = radial>.5 ? c*2. : vec2(cos(angle),sin(angle));
        o = vec4(T(uv+dir*amount).r, T(uv).g, T(uv-dir*amount).b, 1.); }` },
    grain: { d: { amount: .08, size: 1, lumaW: 1, color: 0 }, note: 'Film grain. lumaW=1 weights mid-tones. Reseeds every frame from t. 0.04-0.12 typical.', f: `
      void main(){ vec4 c=T(uv); vec2 g=floor(uv*u_res/max(size,1.)) + vec2(u_seed*37.1, u_seed*11.7);
        float n=h21(g)-.5; vec3 nn = color>.5 ? vec3(h21(g+3.1)-.5, h21(g+7.7)-.5, n) : vec3(n);
        float m = mix(1., 1.-abs(luma(c.rgb)-.5)*1.5, lumaW); o=vec4(c.rgb + nn*amount*2.*m, 1.); }` },
    vignette: { d: { amount: .5, size: .7, soft: .55, color: '#000000' }, note: 'Darken corners toward color.', f: `
      void main(){ vec4 c=T(uv); float d=length((uv-.5)*vec2(asp(),1.))*1.15; float v=smoothstep(size-soft*.5, size+soft, d);
        o=vec4(mix(c.rgb, color, v*amount), 1.); }` },
    halftone: { d: { size: 9, angle: .5236, mode: 0, contrast: 1.1, ink: '#14161c', paper: '#f1eadb', blend: 1 }, note: 'mode 0 round dots, 1 lines, 2 CMYK (angles 15/75/0/45, multiply on paper). blend mixes with the original.', f: `
      float scr(vec2 q,float a,float v,float s){ vec2 r=rot(a)*q/s; vec2 f=fract(r)-.5; float d=length(f); float rad=sqrt(clamp(v,0.,1.))*.72; float aa=fwidth(d)+.02; return 1.-smoothstep(rad-aa,rad+aa,d); }
      float lin(vec2 q,float a,float v,float s){ vec2 r=rot(a)*q/s; float d=abs(fract(r.y)-.5); float rad=clamp(v,0.,1.)*.5; float aa=fwidth(d)+.02; return 1.-smoothstep(rad-aa,rad+aa,d); }
      void main(){ vec4 c=T(uv); vec2 q=uv*u_res; vec3 col;
        if(mode<1.5){ float L=clamp((luma(c.rgb)-.5)*contrast+.5,0.,1.); float cov = mode<.5 ? scr(q,angle,1.-L,size) : lin(q,angle,1.-L,size); col=mix(paper,ink,cov); }
        else { vec3 rgb=clamp((c.rgb-.5)*contrast+.5,0.,1.); float k=1.-max(rgb.r,max(rgb.g,rgb.b)); float cy=(1.-rgb.r-k)/(1.-k+1e-3), mg=(1.-rgb.g-k)/(1.-k+1e-3), ye=(1.-rgb.b-k)/(1.-k+1e-3);
          vec3 ink0=vec3(1.); ink0*=1.-scr(q,.2618,cy,size)*vec3(1.,.15,.0)*.95; ink0*=1.-scr(q,1.309,mg,size)*vec3(.0,1.,.35)*.95; ink0*=1.-scr(q,0.,ye,size)*vec3(.0,.1,1.)*.95; ink0*=1.-scr(q,.7854,k,size)*.92; col=paper*ink0; }
        o=vec4(mix(c.rgb,col,blend),1.); }` },
    duotone: { d: { dark: '#10123a', light: '#f4e9c8', contrast: 1 }, note: 'Map luminance to two colours.', f: `
      void main(){ float L=clamp((luma(T(uv).rgb)-.5)*contrast+.5,0.,1.); o=vec4(mix(dark,light,L),1.); }` },
    tritone: { d: { a: '#0b0b2b', b: '#b3262f', c: '#ffe9b0', mid: .5, contrast: 1 }, note: 'Gradient map with three stops (shadows a, mids b, highlights c).', f: `
      void main(){ float L=clamp((luma(T(uv).rgb)-.5)*contrast+.5,0.,1.); vec3 col = L<mid ? mix(a,b,L/mid) : mix(b,c,(L-mid)/(1.-mid)); o=vec4(col,1.); }` },
    posterize: { d: { levels: 5, mixAmt: 1 }, note: 'Quantise each channel.', f: `
      void main(){ vec3 c=T(uv).rgb; vec3 q=floor(c*levels+.5)/levels; o=vec4(mix(c,q,mixAmt),1.); }` },
    grade: { d: { lift: 0, gamma: 1, gain: 1, saturation: 1, contrast: 1, temperature: 0, tint: 0, exposure: 0 }, note: 'Colour grade. temperature + = warm, tint + = magenta.', f: `
      void main(){ vec3 c=T(uv).rgb*pow(2.,exposure); c=c*gain+lift; c=pow(max(c,0.),vec3(1./max(gamma,.01)));
        c.r+=temperature*.1; c.b-=temperature*.1; c.g-=tint*.06; c.rb+=tint*.03; c=(c-.5)*contrast+.5; float L=luma(c); c=mix(vec3(L),c,saturation); o=vec4(clamp(c,0.,1.),1.); }` },
    filmic: { d: { exposure: 1, shoulder: 1 }, note: 'ACES-style tone curve: rolls off highlights; pair with bloom.', f: `
      void main(){ vec3 x=T(uv).rgb*exposure; vec3 y=(x*(2.51*x+.03))/(x*(2.43*x+.59)+.14); o=vec4(clamp(mix(x,y,shoulder),0.,1.),1.); }` },
    scanlines: { d: { count: 540, strength: .18, flicker: .03 }, note: 'Horizontal lines. count = lines per frame height.', f: `
      void main(){ vec4 c=T(uv); float l=.5+.5*sin(uv.y*count*6.2831); float fl=1.+flicker*sin(u_t*60.); o=vec4(c.rgb*(1.-strength*l)*fl,1.); }` },
    crt: { d: { curvature: .07, scan: .2, mask: .15, bleed: .0015, vignette: .3 }, note: 'CRT look: barrel, scanlines, RGB mask, horizontal bleed.', f: `
      void main(){ vec2 c=uv*2.-1.; c*=1.+curvature*dot(c,c); vec2 q=c*.5+.5; if(q.x<0.||q.x>1.||q.y<0.||q.y>1.){ o=vec4(0.,0.,0.,1.); return; }
        vec3 col=vec3(T(q+vec2(bleed,0.)).r, T(q).g, T(q-vec2(bleed,0.)).b);
        col*=1.-scan*(.5+.5*sin(q.y*u_res.y*3.14159)); float m=mod(floor(q.x*u_res.x),3.); col*=1.-mask*vec3(m<1.?0.:1., m>=1.&&m<2.?0.:1., m>=2.?0.:1.);
        col*=1.-vignette*dot(c,c)*.35; o=vec4(col,1.); }` },
    lens: { d: { distortion: .12, zoom: 1 }, note: 'Barrel (+) or pincushion (-) distortion.', f: `
      void main(){ vec2 c=(uv-.5)*2.; c*=1.+distortion*dot(c,c); c/=zoom; vec2 q=c*.5+.5; o = (q.x<0.||q.x>1.||q.y<0.||q.y>1.) ? vec4(0.,0.,0.,1.) : T(q); }` },
    dirblur: { d: { radius: 24, angle: 0, samples: 16 }, note: 'Directional (motion) blur along angle. radius in px. Use on whips.', f: `
      void main(){ vec2 d=vec2(cos(angle),sin(angle))*radius/u_res; vec4 s=vec4(0.); float tw=0.; for(int i=0;i<32;i++){ if(float(i)>=samples) break; float k=(float(i)/(samples-1.))-.5; float w=1.-abs(k)*1.2; s+=T(uv+d*k)*w; tw+=w; } o=vec4(s.rgb/tw,1.); }` },
    radialBlur: { d: { amount: .08, cx: .5, cy: .5, samples: 20 }, note: 'Zoom blur from (cx,cy). Whoosh/zoom-through/impact.', f: `
      void main(){ vec2 c=vec2(cx,cy); vec2 d=uv-c; vec3 s=vec3(0.); float tw=0.; for(int i=0;i<40;i++){ if(float(i)>=samples) break; float k=float(i)/(samples-1.); float w=1.-k*.6; s+=T(c+d*(1.-amount*k)).rgb*w; tw+=w; } o=vec4(s/tw,1.); }` },
    pixelate: { d: { size: 10 }, note: 'Mosaic pixels (px).', f: `
      void main(){ vec2 g=floor(uv*u_res/size)*size+size*.5; o=vec4(T(g/u_res).rgb,1.); }` },
    displace: { d: { amount: .012, scale: 3, speed: .4, seedOffset: 0 }, note: 'Noise displacement (heat haze, liquid). Time-continuous.', f: `
      void main(){ vec2 p=uv*scale*vec2(asp(),1.); float t=u_t*speed; vec2 d=vec2(fbm(p+vec2(t,0.)+seedOffset), fbm(p+vec2(5.2,1.3-t)+seedOffset))-.5; o=vec4(T(uv+d*amount*2.).rgb,1.); }` },
    ripple: { d: { cx: .5, cy: .5, freq: 34, amp: .012, speed: 2.2, decay: 2.2, start: 0 }, note: 'Expanding ring wave from a point; animate start = event time.', f: `
      void main(){ vec2 c=vec2(cx,cy); vec2 d=(uv-c)*vec2(asp(),1.); float r=length(d); float tt=max(u_t-start,0.); float front=tt*speed*.4; float env=exp(-abs(r-front)*12.)*exp(-tt*decay)*step(.0001,tt);
        float w=sin((r-front)*freq*3.)*amp*env; o=vec4(T(uv+normalize(d+1e-5)*w/vec2(asp(),1.)).rgb,1.); }` },
    glitch: { d: { amount: .5, blocks: 14, rgb: .012, speed: 12 }, note: 'Block shifts + RGB split; amount 0 = off. Triggered per frame (deterministic).', f: `
      void main(){ float fr=floor(u_t*speed); float row=floor(uv.y*blocks); float on=step(1.-amount, h11(row*1.7+fr*3.1)); float sh=(h11(row+fr*7.3)-.5)*.25*on;
        vec2 q=uv+vec2(sh,0.); float sp=rgb*on*(h11(fr+row)+.3);
        o=vec4(T(q+vec2(sp,0.)).r, T(q).g, T(q-vec2(sp,0.)).b, 1.); }` },
    kaleido: { d: { segments: 6, angle: 0, zoom: 1, cx: .5, cy: .5 }, note: 'Kaleidoscope mirror.', f: `
      void main(){ vec2 c=(uv-vec2(cx,cy))*vec2(asp(),1.)/zoom; float a=atan(c.y,c.x)+angle; float r=length(c); float s=6.2831853/segments; a=abs(mod(a,s)-s*.5); vec2 q=vec2(cos(a),sin(a))*r; q=q/vec2(asp(),1.)+vec2(cx,cy); o=vec4(T(fract(q)).rgb,1.); }` },
    mirror: { d: { axis: 0, offset: .5 }, note: 'axis 0 mirrors x at offset, 1 mirrors y.', f: `
      void main(){ vec2 q=uv; if(axis<.5){ q.x = q.x>offset ? q.x : 2.*offset-q.x; } else { q.y = q.y>offset ? q.y : 2.*offset-q.y; } o=vec4(T(clamp(q,0.,1.)).rgb,1.); }` },
    lightleak: { d: { strength: .45, a: '#ff8a3d', b: '#ff2d6f', speed: .15, seedOffset: 1 }, note: 'Warm light leak, screen-blended, drifting with t.', f: `
      void main(){ vec4 c=T(uv); float t=u_t*speed+seedOffset; vec2 p=uv*vec2(asp(),1.); float m1=smoothstep(.8,0.,length(p-vec2(.2+.5*sin(t),.3+.3*cos(t*.8))))*(.6+.4*fbm(p*2.+t));
        float m2=smoothstep(.9,0.,length(p-vec2(1.+.4*cos(t*.6),.8+.2*sin(t*.7))))*(.6+.4*fbm(p*2.-t)); vec3 L=a*m1+b*m2; o=vec4(1.-(1.-c.rgb)*(1.-L*strength),1.); }` },
    dust: { d: { density: .5, size: 2, speed: .05, bright: .9 }, note: 'Floating specks, additive. Seeded by cell; moves with t.', f: `
      void main(){ vec4 c=T(uv); vec3 add=vec3(0.); for(int k=0;k<3;k++){ float s=size*(1.+float(k)*1.6); vec2 g=uv*u_res/(s*14.); g.y+=u_t*speed*(1.+float(k)*.5)*8.; g.x+=sin(u_t*.3+float(k))*.5; vec2 id=floor(g); vec2 f=fract(g)-.5; float r=h21(id+float(k)*13.); vec2 off=(h22(id)-.5)*.6; float d=length(f-off); float on=step(1.-density*.12,r); add+=on*smoothstep(.06,.0,d)*bright*(.4+.6*h21(id+7.)); }
        o=vec4(c.rgb+add,1.); }` },
    paperTexture: { d: { strength: .3, scale: 2, warm: .06 }, note: 'Paper fibre/tooth multiplied over the frame (use under ink, or on the whole frame at low strength).', f: `
      void main(){ vec4 c=T(uv); vec2 p=uv*u_res/vec2(220.)*scale; float n=fbm(p)*.6+fbm(p*4.+9.)*.4; float fib=fbm(vec2(p.x*14.,p.y*.7)); float k=(n-.5)*.9+(fib-.5)*.4; c.rgb*=1.+k*strength; c.rgb+=vec3(warm,warm*.6,0.)*strength; o=vec4(c.rgb,1.); }` },
    sharpen: { d: { amount: .5 }, note: 'Unsharp mask.', f: `
      void main(){ vec2 e=1./u_res; vec3 c=T(uv).rgb; vec3 b=(T(uv+vec2(e.x,0.)).rgb+T(uv-vec2(e.x,0.)).rgb+T(uv+vec2(0.,e.y)).rgb+T(uv-vec2(0.,e.y)).rgb)*.25; o=vec4(c+(c-b)*amount*2.,1.); }` },
    edge: { d: { amount: 1, color: '#ffffff', base: .0, threshold: .05 }, note: 'Sobel outline drawn over base (0 = pure lines).', f: `
      void main(){ vec2 e=1./u_res; float tl=luma(T(uv+vec2(-e.x,e.y)).rgb), t=luma(T(uv+vec2(0.,e.y)).rgb), tr=luma(T(uv+e).rgb), l=luma(T(uv-vec2(e.x,0.)).rgb), r=luma(T(uv+vec2(e.x,0.)).rgb), bl=luma(T(uv-e).rgb), b=luma(T(uv-vec2(0.,e.y)).rgb), br=luma(T(uv+vec2(e.x,-e.y)).rgb);
        float gx=-tl-2.*l-bl+tr+2.*r+br, gy=-tl-2.*t-tr+bl+2.*b+br; float g=smoothstep(threshold,threshold+.3,length(vec2(gx,gy))); o=vec4(mix(T(uv).rgb*base,color,g*amount),1.); }` },
    invert: { d: { amount: 1 }, note: 'Invert colours (amount 0..1).', f: `
      void main(){ vec3 c=T(uv).rgb; o=vec4(mix(c,1.-c,amount),1.); }` },
    colorize: { d: { color: '#ff3b6b', amount: .35, mode: 0 }, note: 'Tint: mode 0 multiply-ish, 1 screen, 2 overlay.', f: `
      void main(){ vec3 c=T(uv).rgb; vec3 r = mode<.5 ? c*mix(vec3(1.),color,amount) : mode<1.5 ? 1.-(1.-c)*(1.-color*amount) : mix(c, mix(2.*c*color, 1.-2.*(1.-c)*(1.-color), step(.5,c)), amount); o=vec4(r,1.); }` },
    flash: { d: { amount: 0, color: '#ffffff' }, note: 'Add a flash: animate amount 1 -> 0 over 3-4 frames on a hit.', f: `
      void main(){ o=vec4(mix(T(uv).rgb,color,clamp(amount,0.,1.)),1.); }` },
  };

  const BLUR = `void main(){ vec2 d=dir*radius/u_res; vec3 s=T(uv).rgb*.2270270270; s+=(T(uv+d*1.3846153846).rgb+T(uv-d*1.3846153846).rgb)*.3162162162; s+=(T(uv+d*3.2307692308).rgb+T(uv-d*3.2307692308).rgb)*.0702702703; o=vec4(s,1.); }`;
  const THRESH = `void main(){ vec3 c=T(uv).rgb; float L=luma(c)*.6+max(c.r,max(c.g,c.b))*.4; float k=smoothstep(threshold-knee,threshold+knee,L); o=vec4(c*k,1.); }`;
  const ADD2 = `void main(){ o=vec4(T(uv).rgb + texture(u_tex2,uv).rgb*intensity*tint, 1.); }`;
  const MIX2 = `void main(){ float m=smoothstep(width,width+.25,abs(uv.y-focus)); o=vec4(mix(T(uv).rgb, texture(u_tex2,uv).rgb, m),1.); }`;
  const COPY = `void main(){ o=vec4(T(uv).rgb,1.); }`;
  const ACC = `void main(){ o=vec4(T(uv).rgb*ka + texture(u_tex2,uv).rgb*kb, 1.); }`;

  const MULTI = { bloom: { d: { threshold: .62, knee: .25, intensity: .9, radius: 14, tint: '#ffffff' }, note: 'Glow on highlights. threshold = luminance where glow starts, radius in px at half res (x1.0..x3). 0.5-1.2 intensity.' },
    glow: { d: { threshold: .35, knee: .4, intensity: 1.1, radius: 30, tint: '#ffffff' }, note: 'Wide soft glow (bloom with low threshold and big radius).' },
    blur: { d: { radius: 6 }, note: 'Gaussian blur, radius in px.' },
    tiltshift: { d: { focus: .5, width: .12, radius: 7 }, note: 'Blur away from a horizontal focus band (miniature look). focus/width in uv.' } };

  function create(w, h) {
    const canvas = document.createElement('canvas'); canvas.width = w; canvas.height = h;
    const gl = canvas.getContext('webgl2', { preserveDrawingBuffer: true, antialias: false, alpha: false, premultipliedAlpha: false, powerPreference: 'high-performance' });
    if (!gl) throw new Error('FX: WebGL2 is not available');
    const vbo = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, vbo); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    const vao = gl.createVertexArray(); gl.bindVertexArray(vao); gl.enableVertexAttribArray(0); gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 0, 0);
    const progs = {}; const pool = {};
    const typeOf = v => typeof v === 'number' ? 'float' : typeof v === 'string' ? 'vec3' : Array.isArray(v) ? 'vec' + v.length : 'float';

    function program(key, defaults, body) {
      if (progs[key]) return progs[key];
      let decl = ''; for (const k in defaults) decl += `uniform ${typeOf(defaults[k])} ${k};\n`;
      const fs = `#version 300 es\nprecision highp float;\nin vec2 uv; out vec4 o;\nuniform sampler2D u_tex; uniform sampler2D u_tex2; uniform vec2 u_res; uniform float u_t; uniform float u_seed;\n${decl}${PRE}\n${body}`;
      const mk = (type, src) => { const s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error('FX shader "' + key + '": ' + gl.getShaderInfoLog(s)); return s; };
      const pr = gl.createProgram(); gl.attachShader(pr, mk(gl.VERTEX_SHADER, VS)); gl.attachShader(pr, mk(gl.FRAGMENT_SHADER, fs)); gl.bindAttribLocation(pr, 0, 'p'); gl.linkProgram(pr);
      if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) throw new Error('FX link "' + key + '": ' + gl.getProgramInfoLog(pr));
      const loc = {}; for (const k in defaults) loc[k] = gl.getUniformLocation(pr, k);
      ['u_tex', 'u_tex2', 'u_res', 'u_t', 'u_seed'].forEach(k => loc[k] = gl.getUniformLocation(pr, k));
      return progs[key] = { pr, loc, defaults };
    }
    function target(wd, ht, slot) {
      const key = wd + 'x' + ht + ':' + slot; if (pool[key]) return pool[key];
      const tex = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, tex); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA8, wd, ht, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      const fbo = gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER, fbo); gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0);
      return pool[key] = { tex, fbo, w: wd, h: ht };
    }
    const srcTex = gl.createTexture();
    function draw(pg, params, inTex, inTex2, out, ctx) {
      gl.useProgram(pg.pr); gl.bindFramebuffer(gl.FRAMEBUFFER, out ? out.fbo : null);
      const W = out ? out.w : w, H = out ? out.h : h; gl.viewport(0, 0, W, H);
      gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, inTex); gl.uniform1i(pg.loc.u_tex, 0);
      if (inTex2) { gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, inTex2); gl.uniform1i(pg.loc.u_tex2, 1); }
      gl.uniform2f(pg.loc.u_res, W, H); gl.uniform1f(pg.loc.u_t, ctx.t); gl.uniform1f(pg.loc.u_seed, ctx.seed);
      for (const k in pg.defaults) {
        let v = params[k] !== undefined ? params[k] : pg.defaults[k]; const L = pg.loc[k]; if (L == null) continue;
        if (typeof v === 'string') { const c = hex(v); gl.uniform3f(L, c[0], c[1], c[2]); }
        else if (Array.isArray(v)) { gl['uniform' + v.length + 'fv'](L, v); } else gl.uniform1f(L, v);
      }
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    }
    const blurPG = () => program('_blur', { dir: [1, 0], radius: 4 }, BLUR);
    function blurInto(texIn, wd, ht, radius, slotA, slotB, ctx) { // returns target holding the blurred result (slotB)
      const A = target(wd, ht, slotA), B = target(wd, ht, slotB), pg = blurPG();
      draw(pg, { dir: [1, 0], radius }, texIn, null, A, ctx); draw(pg, { dir: [0, 1], radius }, A.tex, null, B, ctx); return B;
    }
    // large gaussian without ghosting: downsample by 2^m, then one small-radius separable blur, then bilinear upsample
    function bigBlur(texIn, R, tag, ctx) {
      const cp = program('_copy', {}, COPY), m = Math.max(0, Math.ceil(Math.log2(Math.max(R, 1) / 4))); let cur = texIn;
      for (let i = 1; i <= m; i++) { const dn = target(Math.max(2, w >> i), Math.max(2, h >> i), tag + 'd' + i); draw(cp, {}, cur, null, dn, ctx); cur = dn.tex; }
      const wd = Math.max(2, w >> m), ht = Math.max(2, h >> m), b = blurInto(cur, wd, ht, Math.max(.3, R / Math.pow(2, m) / 2.5), tag + 'a', tag + 'b', ctx);
      if (m === 0) return b; const up = target(w, h, tag + 'u'); draw(cp, {}, b.tex, null, up, ctx); return up;
    }
    function runMulti(name, params, inTex, out, ctx) {
      const p = Object.assign({}, MULTI[name].d, params);
      if (name === 'blur') { const b = bigBlur(inTex, p.radius, 'bl', ctx); draw(program('_copy', {}, COPY), {}, b.tex, null, out, ctx); return; }
      if (name === 'tiltshift') { const b = bigBlur(inTex, p.radius, 'ts', ctx); draw(program('_mix2', { focus: .5, width: .12 }, MIX2), p, inTex, b.tex, out, ctx); return; }
      // bloom / glow: threshold -> blur pyramid (1/2..1/32, small radius per level = no ghosting) -> weighted sum by radius -> add
      const th = target(Math.max(2, w >> 1), Math.max(2, h >> 1), 'th'); draw(program('_thr', { threshold: .6, knee: .25 }, THRESH), p, inTex, null, th, ctx);
      const lv = []; let prev = th;
      for (let i = 0; i < 5; i++) {
        const wd = Math.max(2, w >> (i + 1)), ht = Math.max(2, h >> (i + 1));
        let src = prev.tex; if (i > 0) { const dn = target(wd, ht, 'dn' + i); draw(program('_copy', {}, COPY), {}, prev.tex, null, dn, ctx); src = dn.tex; }
        prev = blurInto(src, wd, ht, 1.6, 'la' + i, 'lb' + i, ctx); lv.push(prev);
      }
      const c = Math.min(4, Math.max(0, Math.log2(Math.max(p.radius, 1) / 3) + .5)); const wts = lv.map((_, i) => Math.exp(-Math.pow(i - c, 2) / 1.4)); const sw = wts.reduce((a, b) => a + b, 0);
      const hw = Math.max(2, w >> 1), hh = Math.max(2, h >> 1); const acc = program('_acc', { ka: 1, kb: 1 }, ACC);
      let sum = target(hw, hh, 'sA'); draw(acc, { ka: wts[0] / sw, kb: wts[1] / sw }, lv[0].tex, lv[1].tex, sum, ctx);
      for (let i = 2; i < 5; i++) { const nx = target(hw, hh, i % 2 ? 'sA' : 'sB'); draw(acc, { ka: 1, kb: wts[i] / sw }, sum.tex, lv[i].tex, nx, ctx); sum = nx; }
      draw(program('_add2', { intensity: 1, tint: '#ffffff' }, ADD2), { intensity: p.intensity * 1.6, tint: p.tint }, inTex, sum.tex, out, ctx);
    }
    const api = {
      canvas, gl, w, h,
      apply(source, passes, t, fps) {
        t = t || 0; fps = fps || (root.VIDEO && root.VIDEO.fps) || 30;
        const ctx = { t, seed: (Math.floor(t * fps + 1e-6) % 997) / 997 * 61.7 + 1 };
        gl.bindTexture(gl.TEXTURE_2D, srcTex); gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
        gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, source);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
        gl.bindVertexArray(vao);
        const list = (passes || []).filter(Boolean); let cur = srcTex, ping = 0;
        if (!list.length) list.push({ pass: '_copy' });
        list.forEach((ps, i) => {
          const last = i === list.length - 1, out = last ? null : target(w, h, 'pp' + (ping ^= 1));
          const name = ps.pass;
          if (MULTI[name]) { if (last) { const tmp = target(w, h, 'last'); runMulti(name, ps, cur, tmp, ctx); draw(program('_copy', {}, COPY), {}, tmp.tex, null, null, ctx); } else runMulti(name, ps, cur, out, ctx); }
          else if (name === '_copy') draw(program('_copy', {}, COPY), {}, cur, null, out, ctx);
          else { const d = P[name]; if (!d) throw new Error('FX: unknown pass "' + name + '". Known: ' + Object.keys(P).concat(Object.keys(MULTI)).join(', ')); draw(program(name, d.d, d.f), ps, cur, null, out, ctx); }
          if (out) cur = out.tex;
        });
        return canvas;
      },
      dispose() { const e = gl.getExtension('WEBGL_lose_context'); if (e) e.loseContext(); }
    };
    return api;
  }

  const list = () => Object.keys(P).map(k => ({ name: k, params: P[k].d, note: P[k].note })).concat(Object.keys(MULTI).map(k => ({ name: k, params: MULTI[k].d, note: MULTI[k].note })));
  /* ready-made looks: spread into fx.apply(src, FX.chains.neonBloom(t)) - functions so params can animate with t */
  const chains = {
    neonBloom: (o = {}) => [{ pass: 'bloom', threshold: .55, intensity: o.intensity ?? 1.0, radius: 18 }, { pass: 'chromatic', amount: o.ca ?? .002 }, { pass: 'grain', amount: .05 }, { pass: 'vignette', amount: .5 }],
    halftonePoster: (o = {}) => [{ pass: 'grade', contrast: 1.15, saturation: .9 }, { pass: 'halftone', size: o.size ?? 9, mode: 0, ink: o.ink ?? '#14206b', paper: o.paper ?? '#efe9dc' }, { pass: 'grain', amount: .09 }],
    filmWarm: (o = {}) => [{ pass: 'grade', temperature: .5, contrast: 1.08, saturation: 1.05 }, { pass: 'lightleak', strength: .3 }, { pass: 'grain', amount: .07 }, { pass: 'vignette', amount: .4 }],
    glassDark: (o = {}) => [{ pass: 'bloom', threshold: .5, intensity: .8, radius: 22 }, { pass: 'chromatic', amount: .003 }, { pass: 'vignette', amount: .55 }, { pass: 'grain', amount: .035 }],
    riso: (o = {}) => [{ pass: 'duotone', dark: o.dark ?? '#1b2a6b', light: o.light ?? '#f6e8d0' }, { pass: 'grain', amount: .1, size: 1.5 }, { pass: 'paperTexture', strength: .25 }],
    vhs: (o = {}) => [{ pass: 'chromatic', amount: .004, radial: 0 }, { pass: 'scanlines', strength: .22 }, { pass: 'glitch', amount: o.glitch ?? .12 }, { pass: 'grain', amount: .08, color: 1 }, { pass: 'crt', curvature: .05 }],
    cleanEditorial: (o = {}) => [{ pass: 'grade', saturation: 1.04, contrast: 1.03 }, { pass: 'grain', amount: .02 }, { pass: 'vignette', amount: .12 }]
  };
  root.FX = { create, list, chains, passes: Object.keys(P).concat(Object.keys(MULTI)) };
})(typeof window !== 'undefined' ? window : globalThis);
