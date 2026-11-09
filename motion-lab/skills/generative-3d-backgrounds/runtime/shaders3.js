/* shaders3.js — 12 raymarched / analytic-3D Bg3D worlds. No images, no meshes: signed distance fields and maths.
 * COST: these march rays per pixel. In SwiftShader render them at 540x960 (or half of final) and scale up in a 2D canvas; the gallery runs at 270x480.
 * Each shader computes its own camera from T (flythroughs) — params.camera is ignored unless the header says @camera. */
(function (root) {
  'use strict';
  const S = root.Bg3DShaders = root.Bg3DShaders || {};
  const LK = `
mat3 lookAt(vec3 ro, vec3 ta, float rl){ vec3 f=normalize(ta-ro); vec3 r=normalize(cross(f,vec3(sin(rl),cos(rl),0.))); vec3 u=cross(r,f); return mat3(r,u,f); }
vec3 skyC(vec3 r){ float y=clamp(r.y*.5+.5,0.,1.); return palGrad(pow(y,1.3)); }
`;
  const def = (name, src) => { S[name] = LK + src; };

  def('ray-glass-spheres', `// @mood glossy, calm, 3d, product, marble-run, modern
// @use Endless field of glossy spheres on a mirror floor, camera gliding forward. Premium "3D render" backdrop; keep headlines in the upper third.
// @palette #06070c #1a2036 #5a7dff #b9c8ff #ffffff
uniform float uFloorY; //= 0.9 | floor depth below camera axis
uniform float uSpeedS; //= 0.6 | glide speed
uniform float uGlass; //= 0.6 | refraction vs reflection mix
float radS(vec2 id){ return .28+.2*hash21(id); }
float mapS(vec3 p){ vec2 c=vec2(1.8); vec2 id=floor(p.xz/c+.5); vec2 q=p.xz-id*c; float r=radS(id); return sdSphere(vec3(q.x,p.y+uFloorY-r,q.y), r); }
float map(vec3 p){ return min(mapS(p), p.y+uFloorY); }
float trace(vec3 ro, vec3 rd, float tmax){ float t=.02; for(int i=0;i<72;i++){ float d=map(ro+rd*t); if(d<.0015*t||t>tmax) break; t+=d*.8; } return t; }
vec3 envC(vec3 r){ float y=r.y*.5+.5; vec3 c=palGrad(pow(y,1.5)); c+=P4*2.2*pow(max(0.,dot(r,normalize(vec3(.5,.6,.6)))),28.); c+=P3*.5*smoothstep(.75,1.,y); return c; }
vec3 sphereCol(vec3 p, vec3 rd){
  vec3 n=calcNormal(p); vec2 id=floor(p.xz/1.8+.5); float h=hash21(id);
  vec3 base=mix(P2,P3,h); vec3 rf=reflect(rd,n); vec3 rr=refract(rd,n,.75);
  float fr=fresnel(n,-rd,.06,4.);
  vec3 col=base*(.12+.2*clamp(n.y*.5+.5,0.,1.));
  col+=mix(envC(rr)*base*1.4, envC(rf), clamp(fr+.35*(1.-uGlass),0.,1.));
  return col;
}
vec3 render(vec2 p, vec2 uv){
  vec3 ro=vec3(.5*sin(PH), .25+.15*sin(PH*2.), T*uSpeedS); vec3 ta=ro+vec3(.5*sin(PH+1.), -.22, 2.4);
  vec3 rd=normalize(lookAt(ro,ta,0.)*vec3(p,1.5));
  float t=trace(ro,rd,60.); vec3 pos=ro+rd*t; vec3 col;
  vec3 fogc=mix(P1,P0,.5);
  if(t>=60.) col=envC(rd)*.5;
  else if(pos.y+uFloorY<.01){
    vec3 rf=reflect(rd,vec3(0.,1.,0.)); float t2=trace(pos+vec3(0.,.01,0.),rf,30.);
    vec3 rc = t2>=30. ? envC(rf)*.5 : sphereCol(pos+rf*t2, rf);
    float fr=fresnel(vec3(0.,1.,0.),-rd,.05,3.);
    col=P0*.5+rc*(.35+.5*fr);
  } else col=sphereCol(pos,rd);
  col=mix(col,fogc,1.-exp(-t*.045));
  return col*(1.-.25*dot(p,p));
}
`);

  def('ray-twisted-pillars', `// @mood architectural, cathedral, mysterious, premium, slow
// @use Corridor of twisted columns receding into fog; strong one-point perspective for titles, trailers, luxury. Dolly forward by speed param.
// @palette #04040a #14122a #6a4cff #ff8ad8 #ffffff
uniform float uSpeedP; //= 0.8 | dolly speed
uniform float uTwistP; //= 0.9 | column twist
float map(vec3 p){
  vec3 q=vec3(abs(p.x)-2.1, p.y, mod(p.z+1.5,3.)-1.5);
  vec3 tq=opTwist(vec3(q.x,q.y,q.z), uTwistP);
  float col=sdBox(tq, vec3(.34,3.,.34))-.02;
  return min(col, min(p.y+1.2, 3.-p.y+ .0));
}
float trace(vec3 ro, vec3 rd){ float t=.05; for(int i=0;i<80;i++){ float d=map(ro+rd*t); if(d<.002*t||t>40.) break; t+=d*.75; } return t; }
vec3 render(vec2 p, vec2 uv){
  vec3 ro=vec3(.35*sin(PH), .3+.08*sin(PH*2.), T*uSpeedP); vec3 rd=normalize(lookAt(ro,ro+vec3(0.,0.,3.),.03*sin(PH))*vec3(p,1.5));
  float t=trace(ro,rd); vec3 pos=ro+rd*t; vec3 fogc=mix(P1,P2,.12);
  vec3 col=fogc*.6;
  if(t<40.){
    vec3 n=calcNormal(pos); vec3 l=normalize(vec3(-.4,.7,-.5)); float dif=clamp(dot(n,l),0.,1.); float ao=calcAO(pos,n);
    float isFloor=step(pos.y,-1.15); float isCeil=step(2.9,pos.y);
    vec3 base=mix(mix(P1,P2,.3+.5*n.x*n.x), P0, max(isFloor,isCeil)*.7);
    col=base*(.25+.9*dif)*ao;
    float rim=pow(1.-clamp(dot(n,-rd),0.,1.),3.); col+=P3*rim*.6*(1.-isFloor);
    float strip=smoothstep(.04,.0,abs(fract(pos.z/3.+.5)-.5)*3.-.2)*isFloor; col+=P3*strip*.8;
    if(isFloor>.5){ vec3 rf=reflect(rd,vec3(0.,1.,0.)); col+=P2*.25*pow(max(0.,rf.z),6.)*exp(-length(pos.xz-ro.xz)*.04); }
  }
  col=mix(col,fogc,1.-exp(-t*.07));
  col+=P3*.25*exp(-dot(p,p)*14.)*exp(-0.);
  return col*(1.-.3*dot(p,p));
}
`);

  def('ray-dunes', `// @mood desert, warm, vast, quiet, cinematic, golden hour
// @use Endless sand dunes at low sun, camera drifting forward. Vast, calm; good for travel, wellness, "journey" and slow reveals. Change palette for snow or alien planet.
// @palette #2a1020 #8a3b3a #f0a060 #ffd9a0 #fff6e0
uniform float uSpeedD; //= 0.5 | drift speed
uniform float uSunH; //= 0.22 | sun height
float hD(vec2 q){ return ridge2(q*.28,4)*2.6 + fbm2(q*.9,3)*.35; }
vec3 render(vec2 p, vec2 uv){
  vec3 ro=vec3(sin(PH)*1.5, 0., T*uSpeedD*2.); ro.y=hD(ro.xz)+1.0; vec3 ta=ro+vec3(.6*sin(PH*.7), -.15, 3.);
  vec3 rd=normalize(lookAt(ro,ta,0.)*vec3(p,1.4)); vec3 sun=normalize(vec3(-.5,uSunH,.8));
  float sd=max(0.,dot(rd,sun));
  vec3 sky=mix(P2, mix(P1,P0,smoothstep(.0,.8,rd.y)), smoothstep(-.05,.45,rd.y)); sky+=P3*pow(sd,6.)*.8+P4*pow(sd,120.)*2.;
  float t=.2; bool hit=false;
  for(int i=0;i<90;i++){ vec3 q=ro+rd*t; float h=q.y-hD(q.xz); if(h<.01*t){hit=true;break;} t+=max(h*.45,.02*t); if(t>70.) break; }
  vec3 col=sky;
  if(hit){
    vec3 q=ro+rd*t; float e=.02; float h0=hD(q.xz); vec3 n=normalize(vec3(h0-hD(q.xz+vec2(e,0.)), e*2.5, h0-hD(q.xz+vec2(0.,e))));
    float dif=clamp(dot(n,sun),0.,1.); float sh=1.; 
    vec3 sand=mix(mix(P1,P2,.5),P3,clamp(n.y*n.y,0.,1.)*.6+.1*fbm2(q.xz*2.,2));
    col=sand*(.18+1.15*dif)+P3*pow(1.-n.y,2.)*.25*dif;
    col+=P4*pow(max(0.,dot(reflect(rd,n),sun)),30.)*.15;
    col=mix(col,sky*.85+P2*.1,1.-exp(-t*.028));
  }
  return col*(1.-.25*dot(p,p));
}
`);

  def('ray-gel-orbit', `// @mood soft-3d, playful, tactile, hero object, friendly tech
// @use A single glossy gel/clay blob (metaball cluster) orbiting over a soft floor with real shadow and AO. The "3D hero object" without a model: place text beside or below.
// @palette #efe6ff #cbb8ff #7a5cff #ff7ac0 #ffffff
uniform float uBlobsG; //= 5 | number of orbs (<= 7)
uniform float uSizeG; //= 1.0 | size
float map(vec3 p){
  float d=1e3; float fl=p.y+1.05;
  for(int i=0;i<7;i++){ if(float(i)>=uBlobsG) break; float fi=float(i);
    vec3 c=vec3(.75*cos(PH+fi*1.9)*(.6+.4*sin(fi)), .25*sin(PH*2.+fi*2.7), .75*sin(PH+fi*1.9)*(.6+.4*cos(fi)));
    d=smin(d, sdSphere(p-c, (.32+.12*hash11(fi*3.1))*uSizeG), .55); }
  d=smin(d, sdSphere(p-vec3(0.), .5*uSizeG), .6);
  return smin(d, fl, .06) ;
}
float trace(vec3 ro, vec3 rd){ float t=.1; for(int i=0;i<80;i++){ float d=map(ro+rd*t); if(d<.001*t||t>20.) break; t+=d*.85; } return t; }
vec3 render(vec2 p, vec2 uv){
  vec3 ro=vec3(3.3*sin(PH*.5)*.35, .55, 3.6); vec3 rd=normalize(lookAt(ro,vec3(0.,-.1,0.),0.)*vec3(p,1.55));
  float t=trace(ro,rd); vec3 bgc=mix(P1,P0,smoothstep(-.7,.8,p.y)); vec3 col=bgc;
  if(t<20.){
    vec3 pos=ro+rd*t; vec3 n=calcNormal(pos); vec3 l=normalize(vec3(-.5,.9,.6));
    float dif=clamp(dot(n,l),0.,1.); float sh=softShadow(pos+n*.02,l,.05,6.,10.); float ao=calcAO(pos,n);
    bool isF=pos.y<-.98 && n.y>.9;
    if(isF){ col=mix(P0,P1,.6)*(.5+.6*dif*sh)*ao; col=mix(col,bgc,smoothstep(2.,7.,length(pos.xz))); }
    else {
      float h=clamp(n.y*.5+.5,0.,1.); vec3 base=mix(P2,P3,clamp(.5+.5*sin(pos.x*2.3+pos.z*1.7+PH),0.,1.));
      col=base*(.3+.9*dif*sh)*ao + base*.25*h;
      vec3 rf=reflect(rd,n); col+=envStudio(rf, P4, P1, P0)*.28*fresnel(n,-rd,.06,4.);
      col+=P4*pow(max(0.,dot(rf,l)),50.)*.9*sh;
      col+=P3*pow(1.-clamp(dot(n,-rd),0.,1.),2.5)*.25;
    }
  }
  return col;
}
`);

  def('ray-neon-city', `// @mood cyberpunk, night, flythrough, energetic, urban
// @use Camera skimming above a neon block city at night, windows glowing. High energy; combine with fast whooshes. Speed param raises the pace; add fog with params.
// @palette #05040c #160a35 #ff2fa0 #26e6ff #fff5ff
uniform float uSpeedC; //= 2.0 | flight speed
uniform float uHeightC; //= 1.0 | building height multiplier
float hC(vec2 id){ return (1.+4.5*pow(hash21(id),1.6))*uHeightC; }
float map(vec3 p){
  vec2 c=vec2(3.6); vec2 id=floor(p.xz/c+.5); vec2 q=p.xz-id*c; float h=hC(id); float w=.95+.35*hash21(id+4.);
  float b=sdBox(vec3(q.x,p.y-h*.5,q.y), vec3(w,h*.5,w*.9));
  return min(b, p.y);
}
float trace(vec3 ro, vec3 rd){ float t=.1; for(int i=0;i<90;i++){ float d=map(ro+rd*t); if(d<.003*t||t>70.) break; t+=d*.62; } return t; }
vec3 render(vec2 p, vec2 uv){
  vec3 ro=vec3(1.8*sin(PH*.5), 3.2+1.0*sin(PH*1.5), T*uSpeedC); vec3 rd=normalize(lookAt(ro,ro+vec3(.8*sin(PH*.5),-.55,4.),.12*sin(PH))*vec3(p,1.35));
  float t=trace(ro,rd); vec3 pos=ro+rd*t;
  vec3 hor=mix(P1,P2,.35); vec3 sky=mix(hor,P0,smoothstep(-.05,.5,rd.y)); sky+=P2*.35*exp(-abs(rd.y)*9.);
  vec3 col=sky;
  if(t<70.){
    vec3 n=calcNormal(pos); vec2 id=floor(pos.xz/3.6+.5); float hh=hash21(id);
    if(pos.y<.02){ vec2 g=abs(fract(pos.xz/3.6+.5)-.5); float street=smoothstep(.2,.35,max(g.x,g.y)); col=P0*.8+P3*street*.18+P2*smoothstep(.015,.0,abs(fract(pos.z*.5)-.5)-.47)*street*.5; }
    else {
      vec3 wall=P1*.25; float side=abs(n.x)>.5?pos.z:pos.x; vec2 wp=vec2(side*3.1, pos.y*2.6);
      vec2 wid=floor(wp); vec2 wf=fract(wp);
      float lit=step(.58,hash21(wid+id*7.1)); float win=lit*step(.15,wf.x)*step(wf.x,.8)*step(.2,wf.y)*step(wf.y,.78);
      float notTop=step(abs(n.y),.5);
      vec3 wc=mix(P2,P3,hash21(wid+id)); col=wall+wc*win*notTop*1.7;
      col+=mix(P2,P3,hh)*smoothstep(.06,.0,abs(pos.y-hC(id)))*1.6*step(.5,n.y+.5-notTop*.0);
      col+=P3*.12*pow(1.-abs(n.y),1.)*dot(n,vec3(0.,0.,-1.))*0.;
    }
    col=mix(col,hor*.9,1.-exp(-t*.032));
  }
  return col*(1.-.3*dot(p,p));
}
`);

  def('ray-ocean', `// @mood sea, open, serene, epic, travel, dusk
// @use Open ocean to the horizon with a low sun glint. Camera bobs on the swell. Good for calm intros, "journey", climate and wellness; swap palette for tropical or arctic.
// @palette #0a1a30 #1f5a86 #ff9966 #ffd7a8 #fffbe8
uniform float uChop; //= 1.0 | wave height
uniform float uSunE; //= 0.12 | sun height
float wave(vec2 q){ float t=T*.5; float h=0.;
  h+=.30*sin(q.x*.9+t*1.1+sin(q.y*.4)); h+=.18*sin(q.x*.5+q.y*.8-t*.9); h+=.10*sin(q.y*1.9+q.x*.7+t*1.7); h+=.05*sin(q.x*3.1-q.y*2.3+t*2.3);
  return h*uChop; }
vec3 render(vec2 p, vec2 uv){
  vec3 ro=vec3(0., 1.3+.12*sin(PH*2.), 0.); vec3 rd=normalize(lookAt(ro,ro+vec3(0.,-.16+.02*sin(PH),3.),.015*sin(PH*2.))*vec3(p,1.4));
  vec3 sun=normalize(vec3(.0,uSunE,1.)); float sd=max(0.,dot(rd,sun));
  vec3 sky=mix(P3, mix(P2,P0,smoothstep(.0,.9,rd.y)), smoothstep(-.02,.35,rd.y)); sky+=P3*pow(sd,8.)*.7+P4*pow(sd,200.)*3.;
  float cl=fbm2(rd.xz/(rd.y+.35)*.8+circ(.2,0.),4); sky=mix(sky, sky+P3*.25, smoothstep(.5,.85,cl)*smoothstep(.0,.3,rd.y)*.7);
  vec3 col=sky;
  if(rd.y<0.){
    float t=-ro.y/rd.y;
    for(int i=0;i<5;i++){ vec3 q=ro+rd*t; float h=wave(q.xz); t+=(q.y-h)/(-rd.y)*.8; }
    vec3 q=ro+rd*t; float e=.05; float h0=wave(q.xz);
    vec3 n=normalize(vec3(h0-wave(q.xz+vec2(e,0.)), e*1.2, h0-wave(q.xz+vec2(0.,e))));
    n=normalize(mix(n,vec3(0.,1.,0.),smoothstep(10.,60.,t)));
    vec3 rf=reflect(rd,n); rf.y=abs(rf.y);
    vec3 rsky=mix(P3, mix(P2,P0,smoothstep(.0,.9,rf.y)), smoothstep(-.02,.35,rf.y)); float rsd=max(0.,dot(rf,sun)); rsky+=P3*pow(rsd,8.)*.7+P4*pow(rsd,160.)*4.;
    float fr=fresnel(n,-rd,.02,5.);
    vec3 deep=mix(P0,P1,.4+.6*clamp(n.y*n.y,0.,1.)*0.+.3*pow(1.-n.y,2.)*3.);
    col=mix(deep*(.5+.5*dot(n,sun)), rsky, clamp(fr*1.1,0.,1.));
    float crest=smoothstep(.22,.38,h0/max(uChop,.2)); col+=P4*crest*.12*fr;
    col=mix(col,mix(P2,P3,.4)*.9+P1*.1,1.-exp(-t*.016));
  }
  return col*(1.-.2*dot(p,p));
}
`);

  def('ray-hex-tunnel', `// @mood sci-fi, tech, corridor, fast, clinical
// @use Flight down a hexagonal tech tunnel with glowing seams and ribs; one-point perspective, hero in the centre. Speed up on hits.
// @palette #03060c #0e1c33 #19c4ff #7dffe0 #ffffff
uniform float uSpeedH; //= 2.0 | flight speed
uniform float uRadH; //= 1.5 | tunnel radius
float hexD(vec2 q){ float a=atan(q.y,q.x); float s=PI/3.; float k=mod(a+s*.5,s)-s*.5; return length(q)*cos(k); }
vec2 sway(float z){ return vec2(.35*sin(z*.18+PH*0.), .25*sin(z*.13)); }
float map(vec3 p){
  vec2 q=p.xy-sway(p.z); float d=uRadH-hexD(q);
  float rib=1.-smoothstep(0.,.2,abs(mod(p.z,2.4)-1.2)-.9); 
  return d-.1*(1.-rib)*0.-.14*smoothstep(.0,.3,abs(mod(p.z,2.4)-1.2)-.88)*0.+.0 - .12*step(abs(mod(p.z,2.4)-1.2),.14);
}
float trace(vec3 ro, vec3 rd){ float t=.05; for(int i=0;i<80;i++){ float d=map(ro+rd*t); if(d<.002*t||t>45.) break; t+=d*.8; } return t; }
vec3 render(vec2 p, vec2 uv){
  float z0=T*uSpeedH; vec3 ro=vec3(sway(z0)+vec2(.0,.0), z0); vec3 ta=vec3(sway(z0+4.), z0+4.);
  vec3 rd=normalize(lookAt(ro,ta,.05*sin(PH))*vec3(p,1.3));
  float t=trace(ro,rd); vec3 pos=ro+rd*t; vec3 col=P0;
  if(t<45.){
    vec3 n=calcNormal(pos); vec2 q=pos.xy-sway(pos.z); float a=atan(q.y,q.x); float s=PI/3.; float k=abs(mod(a+s*.5,s)-s*.5)/(s*.5); // 0 mid-panel, 1 at corner
    float seam=smoothstep(.12,.0,1.-k)*1.; 
    float ribz=abs(mod(pos.z,2.4)-1.2); float rib=smoothstep(.2,.0,ribz-.12);
    vec3 base=mix(P1*.5,P1,.5+.5*sin(a*3.+pos.z*.3))*.5;
    float dif=clamp(dot(n,-rd),0.,1.);
    col=base*(.3+.8*dif);
    col+=P2*seam*1.5+P3*rib*1.2*(.6+.4*sin(pos.z*.8+PH*2.));
    float flow=smoothstep(.9,1.,sin(pos.z*.9-T*uSpeedH*3.+a*6.)); col+=P3*seam*flow*1.5;
    col=mix(col,P0+P2*.06,1.-exp(-t*.075));
  }
  col+=P2*.5*exp(-dot(p,p)*30.)*.5;
  return col;
}
`);

  def('ray-monolith', `// @mood cinematic, ominous, minimal, 2001, monumental, luxury
// @use A black monolith on a mirror floor in mist, slow dolly. The most "film" of the set: product reveals, trailers, titles that must feel heavy. Single hue palette (P3 = edge light).
// @palette #020204 #0b0f1a #44506e #9fb2e0 #ffffff
uniform float uHeightM; //= 1.0 | monolith height
uniform float uDolly; //= 0.5 | camera dolly amount
float mapM(vec3 p){ return sdBox(p-vec3(0.,.85*uHeightM,0.), vec3(.5,.85*uHeightM,.1))-.012; }
float map(vec3 p){ return min(mapM(p), p.y+.0); }
float trace(vec3 ro, vec3 rd, float tmax){ float t=.05; for(int i=0;i<70;i++){ float d=map(ro+rd*t); if(d<.0012*t||t>tmax) break; t+=d*.85; } return t; }
vec3 bgM(vec3 rd){ float y=rd.y; vec3 c=mix(P1*.9,P0,smoothstep(.0,.6,y)); c+=P2*.35*exp(-abs(y)*7.)+P3*.25*exp(-abs(y)*30.)*exp(-rd.x*rd.x*1.5); return c; }
vec3 render(vec2 p, vec2 uv){
  float k=.5+.5*sin(PH-1.5708); vec3 ro=vec3(.8*sin(PH*.5)*.4, .55+.1*k, 4.6-uDolly*1.4*k); vec3 rd=normalize(lookAt(ro,vec3(0.,.95*uHeightM*.9,0.),0.)*vec3(p,1.5));
  float t=trace(ro,rd,40.); vec3 pos=ro+rd*t; vec3 col=bgM(rd);
  if(t<40.){
    if(pos.y<.01){
      vec3 rf=reflect(rd,vec3(0.,1.,0.)); float t2=trace(pos+vec3(0.,.01,0.),rf,20.); vec3 rc=bgM(rf);
      if(t2<20.){ vec3 q=pos+rf*t2; vec3 n2=calcNormal(q); rc=P0*.2+P3*pow(1.-clamp(dot(n2,-rf),0.,1.),3.)*.9; }
      float fr=fresnel(vec3(0.,1.,0.),-rd,.04,4.); float r2=length(pos.xz);
      col=P0*.6+rc*(.3+.6*fr); col+=P2*.12*exp(-r2*.5);
      col=mix(col,bgM(vec3(rd.x,.0,rd.z))*.9,1.-exp(-t*.06));
    } else {
      vec3 n=calcNormal(pos); vec3 rf=reflect(rd,n);
      float fr=fresnel(n,-rd,.03,4.); col=P0*.15+bgM(rf)*.25*fr;
      col+=P3*pow(1.-clamp(dot(n,-rd),0.,1.),4.)*1.2;        // edge light
      col+=P4*pow(max(0.,dot(rf,normalize(vec3(-.4,.5,.6)))),60.)*.5;
    }
  }
  float beam=exp(-pow(p.x*3.,2.))*smoothstep(-.9,.4,p.y); col+=P2*.12*beam*(.5+.5*noise2(p*4.+circ(.3,0.)));
  return col*(1.-.35*dot(p,p));
}
`);

  def('layered-mountains', `// @mood serene, layered, atmospheric, dawn, calm, adventure
// @use Layered ridge silhouettes fading into mist with a low sun and gentle parallax. Cheap (no raymarch) and always pretty: use for calm intros, "journey", wellness, travel. Palette sets time of day.
// @palette #14102e #4a2f6b #e0607e #ffb38a #fff0d6
uniform float uLayers; //= 6 | layer count (<= 7)
uniform float uMist; //= 1.0 | mist between layers
uniform float uSunM; //= 0.62 | sun height (0..1 of frame)
vec3 render(vec2 p, vec2 uv){
  vec3 sky=mix(P3, mix(P2,P1,smoothstep(.45,.9,uv.y)), smoothstep(.3,.7,uv.y)); sky=mix(sky,P0,smoothstep(.75,1.,uv.y)*.6);
  vec2 sp=vec2(.12, uSunM); float sd=length((uv-sp)*vec2(ASPECT,1.)); 
  sky+=P4*exp(-sd*sd*180.)*1.3+P3*exp(-sd*sd*10.)*.5; sky+=P4*smoothstep(.07,.065,sd)*.6;
  vec3 col=sky;
  for(int i=0;i<7;i++){
    if(float(i)>=uLayers) break; float fi=float(i); float depth=fi/max(uLayers-1.,1.);
    float base=.56-depth*.40; float amp=.07+depth*.14; float fx=p.x*(1.1+depth*1.6)+fi*13.1+sin(PH)*.05*depth;
    float ridge=base+amp*(ridge2(vec2(fx,fi*3.7),4)-.35)*1.9;
    float m=smoothstep(.0015,-.0015,uv.y-ridge);
    vec3 fogc=mix(P3,P2,.3); vec3 lc=mix(P2*.55,P0,pow(depth,.8)); lc=mix(lc,P1,.25*(1.-depth));
    vec3 layer=mix(lc, fogc, (1.-depth)*.62*uMist);
    layer*=1.-.35*smoothstep(0.,-.18,(uv.y-ridge));   // darker towards the base
    col=mix(col,layer,m);
    float mist=exp(-pow((uv.y-(ridge-.05))/.05,2.))*uMist*.35*(1.-depth*.6); col+=fogc*mist*(1.-m*.0);
  }
  float st=step(.9965,hash21(floor(uv*vec2(ASPECT,1.)*420.)))*smoothstep(.6,1.,uv.y)*smoothstep(.0,.6,1.-uSunM); col+=P4*st*.8;
  return col;
}
`);

  def('dotted-globe', `// @mood global, tech, explainer, data, network
// @use Rotating dot-matrix Earth-like globe (procedural continents, no texture) with atmosphere and star field. Core of "global/network/users worldwide" explainers; place markers by projecting lat/lon yourself (see reference).
// @palette #02050d #08193a #1f6bff #6fd3ff #ffffff
uniform float uTiltG; //= 0.35 | axial tilt (rad)
uniform float uSizeGl; //= 1.0 | globe size
uniform float uLand; //= 0.5 | land fraction (0.35..0.6)
vec3 render(vec2 p, vec2 uv){
  vec3 col=mix(P0,P1,smoothstep(-.8,.7,p.y)*.5);
  vec2 sq=floor(p*260.); float star=step(.997,hash21(sq)); col+=P4*star*.6*(.5+.5*sin(T*2.+hash21(sq+3.)*TAU));
  vec3 ro=vec3(0.,0.,3.2); vec3 rd=normalize(vec3(p,1.6)); float R=1.0*uSizeGl;
  float b=dot(ro,rd); float c=dot(ro,ro)-R*R; float disc=b*b-c;
  float r2=length(p)/ (R/3.2*1.6*.5*2.) ;
  if(disc>0.){
    float t=-b-sqrt(disc); vec3 pos=ro+rd*t; vec3 n=pos/R;
    n=rotX(-uTiltG)*n; n=rotY(PH)*n;
    float lon=atan(n.x,n.z), lat=asin(clamp(n.y,-1.,1.));
    float land=smoothstep(1.-uLand-.02,1.-uLand+.02, fbm3(n*2.2+vec3(1.3,.4,.8),4));
    float rows=42.; float la=lat/PI*rows; float rl=floor(la+.5); float cnt=max(6.,floor(rows*2.*cos(rl/rows*PI)));
    float lo=lon/TAU*cnt; float rlo=floor(lo+.5);
    vec2 cell=vec2(lo-rlo, la-rl); float dd=length(cell*vec2(1.,1.));
    float dotM=smoothstep(.42,.28,dd);
    float cl=smoothstep(1.-uLand-.02,1.-uLand+.02, fbm3(vec3(sin(rlo/cnt*TAU)*cos(rl/rows*PI), sin(rl/rows*PI), cos(rlo/cnt*TAU)*cos(rl/rows*PI))*2.2+vec3(1.3,.4,.8),4));
    vec3 lightD=normalize(vec3(-.5,.4,.8)); vec3 nv=normalize(pos); float dif=clamp(dot(nv,lightD),0.,1.);
    float rim=pow(1.-clamp(dot(nv,-rd),0.,1.),2.2);
    vec3 ocean=mix(P0,P1,.6+.4*dif);
    float grat=smoothstep(.02,.0,abs(fract(lo*.0+lat/PI*12.)-.5)-.48)+smoothstep(.02,.0,abs(fract(lon/TAU*24.)-.5)-.48);
    col=ocean*(.5+.7*dif)+P2*grat*.18;
    col=mix(col, mix(P3,P4,dif)*(.55+.7*dif), dotM*cl*.95);
    col+=P2*dotM*(1.-cl)*.12;
    col+=P3*rim*.9+P2*rim*rim*.8;
  } else {
    float d=sqrt(max(0.,c)*0.+ (dot(ro,ro)-b*b)); float h=max(0.,d-R);
    col+=P2*exp(-h*7.)*.55+P3*exp(-h*22.)*.5;
  }
  return col;
}
`);

  def('plasma-silk', `// @mood luxurious, satin, fabric, soft, fashion, beauty
// @use Flowing satin/silk folds with soft anisotropic highlights. Quiet luxury backdrop for beauty, fashion, finance-premium, quotes. Two close hues + warm white.
// @palette #1a0612 #5a1030 #c93a6b #ff9ab8 #fff0f3
uniform float uFold; //= 1.0 | fold strength
uniform float uFreq; //= 1.0 | fold frequency
float silk(vec2 q){
  float a=.55*sin(q.x*2.6*uFreq+1.7*sin(q.y*1.7*uFreq+PH)+PH);
  a+=.3*sin(q.y*3.9*uFreq+q.x*1.3+1.2*sin(q.x*2.2*uFreq-PH*2.)+PH*2.);
  a+=.15*sin((q.x+q.y)*5.8*uFreq+PH*3.);
  return a*uFold;
}
vec3 render(vec2 p, vec2 uv){
  vec2 q=p*1.15; float e=.01; float h0=silk(q);
  vec3 n=normalize(vec3(-(silk(q+vec2(e,0.))-h0)/e*.28, -(silk(q+vec2(0.,e))-h0)/e*.28, 1.));
  vec3 l=normalize(vec3(-.4,.55,.75)); vec3 v=vec3(0.,0.,1.); vec3 hv=normalize(l+v);
  float dif=clamp(dot(n,l),0.,1.);
  float spec=pow(max(0.,dot(n,hv)),22.); float sheen=pow(1.-abs(dot(n,v)),3.);
  vec3 base=mix(P1,P2,smoothstep(-.4,.8,h0*.8+n.x*.8));
  vec3 col=base*(.22+.95*dif)+P3*spec*.55+P4*pow(spec,3.)*.5+P3*sheen*.22;
  col=mix(P0,col,smoothstep(-.1,.45,dif+.25));
  return col*(1.-.25*dot(p,p));
}
`);

  def('ray-crystal-field', `// @mood crystalline, iridescent, magical, premium tech, awe
// @use Endless field of tumbling faceted crystals with iridescent reflections, camera gliding through. Bright, rich and obviously "3D" - for product reveals, gaming, jewellery, AI "magic" moments.
// @palette #05040f #1b1450 #6a5cff #4de3ff #ffd0f4
uniform float uSpeedK; //= 0.5 | glide speed
uniform float uSizeK; //= 1.0 | crystal size
vec3 cellId(vec3 p){ return floor(p/2.4+.5); }
float map(vec3 p){
  vec3 c=vec3(2.4); vec3 id=cellId(p); vec3 q=p-id*c; float h=hash31(id);
  q=rotY(h*TAU+T*.35*(h-.5)*2.)*rotX(h*5.+T*.25)*q;
  float s=.42*uSizeK*(.6+.6*hash31(id+7.));
  float oct=sdOctahedron(q*vec3(1.,.62,1.), s); return oct*.8;
}
float trace(vec3 ro, vec3 rd){ float t=.05; for(int i=0;i<70;i++){ float d=map(ro+rd*t); if(d<.002*t||t>40.) break; t+=d*.85; } return t; }
vec3 irid(vec3 n, vec3 rd, float h){ float f=1.-clamp(dot(n,-rd),0.,1.); return .5+.5*cos(TAU*(f*1.3+h+vec3(0.,.33,.67))); }
vec3 render(vec2 p, vec2 uv){
  vec3 ro=vec3(.35*sin(PH)+1.2, .35*cos(PH)+1.2, T*uSpeedK*2.); vec3 rd=normalize(lookAt(ro,ro+vec3(.3*sin(PH*2.),.2*cos(PH),3.),.2*sin(PH))*vec3(p,1.4));
  float t=trace(ro,rd); vec3 bgc=mix(P1,P0,smoothstep(-.6,.8,p.y)); vec3 col=bgc*.8;
  if(t<40.){
    vec3 pos=ro+rd*t; vec3 n=calcNormal(pos); float h=hash31(cellId(pos));
    vec3 rf=reflect(rd,n); float y=rf.y*.5+.5;
    vec3 env=palGrad(pow(y,1.2))*1.1+P4*pow(max(0.,dot(rf,normalize(vec3(.4,.8,.3)))),24.)*1.6;
    vec3 ir=irid(n,rd,h); vec3 base=mix(P2,P3,h);
    float fr=fresnel(n,-rd,.08,3.);
    col=base*(.18+.3*clamp(n.y*.5+.5,0.,1.))+mix(env,env*ir*1.8,.55)*(.45+.7*fr)+ir*.12*pow(1.-clamp(dot(n,-rd),0.,1.),2.);
    col=mix(col,bgc*.8,1.-exp(-t*.05));
  }
  return col*(1.-.3*dot(p,p));
}
`);
})(typeof window !== 'undefined' ? window : globalThis);
