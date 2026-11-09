# Projection mapping: put flat art on a tilted plane

Both helpers take a **quad** `[x0,y0, x1,y1, x2,y2, x3,y3]` = pixel positions of the source's corners **TL, TR, BR, BL** in the output. Four points define any perspective (a homography). Verified: corners map exactly.

## 1. DOM element → quad (best for UI-in-video)
```js
el.style.transformOrigin = '0 0';
el.style.width = '600px'; el.style.height = '400px';        // the element's own layout size = w,h you pass
el.style.transform = Trans.matrix3dFromQuad(600, 400, quad);
```
Text stays crisp and the element can contain live UI (buttons, charts). Animate by changing `quad` per frame inside `seek(t)`.

## 2. Canvas → quad (WebGL, antialiased edge)
```js
const wp = Trans.warp(W, H);                 // output size
wp.draw(sourceCanvas, quad, [r,g,b,a]);      // bg colour (default transparent)
ctx.drawImage(wp.canvas, 0, 0);
```

## 3. Building a quad from 3D intent (no 3D engine)
Pick centre `(cx,cy)`, size `(w,h)`, yaw `ry`, pitch `rx`, roll `rz`, camera distance `d` (≈ 1.2–2× the size):
```js
function quad3d(cx,cy,w,h,ry,rx,rz,d=1500){
  const pts=[[-w/2,-h/2],[w/2,-h/2],[w/2,h/2],[-w/2,h/2]].map(([x,y])=>{
    let X=x,Y=y,Z=0;
    let c=Math.cos(ry),s=Math.sin(ry); [X,Z]=[X*c+Z*s,-X*s+Z*c];
    c=Math.cos(rx);s=Math.sin(rx);     [Y,Z]=[Y*c-Z*s,Y*s+Z*c];
    c=Math.cos(rz);s=Math.sin(rz);     [X,Y]=[X*c-Y*s,X*s+Y*c];
    const k=d/(d+Z); return [cx+X*k, cy+Y*k]; });
  return pts.flat();
}
```
Animate `ry,rx,d` with `Lab.spring`/`Lab.curves.settle` for a card that "arrives" in space.

## 4. Recipes
- **Phone/laptop mockup:** draw the UI into a canvas at the device's screen aspect; draw the device body (rounded rect, bezel, notch) in 2D; place the screen with the quad inside the body polygon. Add a gloss sweep (white→transparent gradient with `globalCompositeOperation='screen'`) moving across with time.
- **Floating UI card:** `quad3d` + soft shadow (blurred dark ellipse below, scale with height) + subtle idle float `sin` in `ry` ±0.06.
- **Floor reflection:** warp the same canvas flipped vertically (swap TL/BL and TR/BR) below the object, multiply by a vertical alpha gradient (0.35→0).
- **Billboard in a scene:** quad follows the camera's projection of the plane's 4 corners (use the same `Lab.camera` projection for the quad corners as for other 3D points).
- **Projector beam:** a translucent trapezoid (`lighter`) from a point to the quad, with dust particles (`Lab.noise`) inside the beam.
- **Screen-in-screen zoom:** the quad grows until it equals the frame rectangle → cut to the full-screen version of that UI (invisible match cut).
- **Tilt-shift pages:** a stack of 5–7 quads with increasing offsets and tiny rotation = fanned documents.

## 5. Pitfalls
- Quad corner order wrong → mirrored/flipped result. Always TL,TR,BR,BL clockwise.
- Source canvas must have the same aspect as the quad's "flat" shape or the content looks stretched.
- Self-intersecting quads (bow-tie) produce garbage; keep it convex.
- Warp at 2× supersampled source for crisp text (draw the source at 2× size).
- WebGL context limits: create the `warp` object once, not per frame.
