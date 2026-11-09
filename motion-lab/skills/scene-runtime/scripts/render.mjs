#!/usr/bin/env node
// render.mjs — turn a seek(t) page into stills or an MP4. Serves the page's folder over http://127.0.0.1 so
// ES modules (three.js), fetch('dna.json') and fonts work. Deterministic: one seek per (sub)frame, no real-time.
//
//   Contact sheet of stills (ALWAYS do this first):
//     node render.mjs scene.html out/stills/sheet.png --stills 0.4,1.2,2.0,3.5  [--cols 3] [--scale 540]
//   Single full-size frame:
//     node render.mjs scene.html out/frame.png --at 2.4
//   Draft (fast review copy):    node render.mjs scene.html out/draft.mp4 --fps 30 --sub 1 --workers 4
//   Final (motion blur):         node render.mjs scene.html out/final.mp4 --fps 60 --sub 8 --workers 4 --audio audio/mix.wav
//   Dump the events the scene registered (feeds sound-design-pro):
//     node render.mjs scene.html - --events out/events.json
//   Transparent overlay (for live footage):  node render.mjs scene.html out/overlay.mov --alpha --fps 30 --sub 1 --workers 4   (ProRes 4444; page + canvas background must be transparent; no --audio)
//   Partial range (debugging):   --range 3.0-6.5
//
// Needs: node 18+, ffmpeg on PATH, playwright (npm i -g playwright && npx playwright install chromium).
import { spawn, execSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { createServer } from 'node:http';
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync, statSync } from 'node:fs';
import path from 'node:path';

const require = createRequire(import.meta.url);
let pw; try { pw = require('playwright'); } catch { pw = createRequire(execSync('npm root -g').toString().trim() + '/')('playwright'); }
const { chromium } = pw;

// ---- args
const argv = process.argv.slice(2);
const pos = []; const opt = {};
for (let i = 0; i < argv.length; i++) { if (argv[i].startsWith('--')) { const k = argv[i].slice(2); const v = (argv[i + 1] && !argv[i + 1].startsWith('--')) ? argv[++i] : true; opt[k] = v; } else pos.push(argv[i]); }
const [html, out] = pos;
if (!html || !out) { console.log(readFileSync(new URL(import.meta.url), 'utf8').split('\n').slice(1, 17).join('\n').replace(/^\/\/ ?/gm, '')); process.exit(1); }
const fps = +(opt.fps || 30), sub = Math.max(1, +(opt.sub || 1)), workers = Math.max(1, +(opt.workers || 4));
const run = (args) => new Promise((res, rej) => { const p = spawn('ffmpeg', ['-hide_banner', '-loglevel', 'error', ...args], { stdio: 'inherit' }); p.on('close', c => c ? rej(new Error('ffmpeg exit ' + c)) : res()); });

// ---- static server rooted at the page's folder (and its parents up to 2 levels, so ../runtime/lab.js works)
const pageAbs = path.resolve(html); const root = path.resolve(opt.root || path.dirname(pageAbs));
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.css': 'text/css', '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf', '.otf': 'font/otf', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.glsl': 'text/plain', '.mp4': 'video/mp4', '.wav': 'audio/wav', '.mp3': 'audio/mpeg' };
const server = createServer((req, res) => {
  const u = decodeURIComponent(req.url.split('?')[0]); const f = path.join(root, u);
  if (!f.startsWith(root) || !existsSync(f) || statSync(f).isDirectory()) { res.writeHead(404); return res.end('nf'); }
  res.writeHead(200, { 'content-type': MIME[path.extname(f)] || 'application/octet-stream', 'cache-control': 'no-store' }); res.end(readFileSync(f));
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const url = `http://127.0.0.1:${server.address().port}/${path.relative(root, pageAbs).split(path.sep).join('/')}?render`;

// Pages are self-contained and served from 127.0.0.1, so NO proxy by default (a proxy would swallow localhost).
// If a page must fetch remote assets, pass --proxy http://host:port ; localhost stays direct.
const proxy = opt.proxy && opt.proxy !== true ? opt.proxy : null;
const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files', '--force-color-profile=srgb', '--disable-lcd-text'], ...(proxy ? { proxy: { server: proxy, bypass: '127.0.0.1,localhost' } } : {}) });

async function open(vp) {
  const page = await browser.newPage(vp ? { viewport: vp, deviceScaleFactor: 1 } : {});
  page.on('console', m => { if (['error', 'warning'].includes(m.type())) console.warn(`[page ${m.type()}]`, m.text()); });
  page.on('pageerror', e => console.error('[page exception]', e.message));
  await page.goto(url);
  await page.waitForFunction(() => window.VIDEO && typeof window.seek === 'function' && window.__ready === true, null, { timeout: 60000 });
  const bad = await page.evaluate(async () => { await Promise.all([...document.fonts].map(f => f.load().catch(() => { }))); await document.fonts.ready; return [...document.fonts].filter(f => f.status !== 'loaded').map(f => f.family); });
  if (bad.length) console.warn('WARNING fonts not loaded (fallback in use):', [...new Set(bad)].join(', '));
  return page;
}
const probe = await open(); const V = await probe.evaluate(() => window.VIDEO); const events = await probe.evaluate(() => window.EVENTS || []); await probe.close();
if (opt.events) { mkdirSync(path.dirname(path.resolve(opt.events)), { recursive: true }); writeFileSync(opt.events, JSON.stringify({ video: V, events }, null, 2)); console.log(`events -> ${opt.events} (${events.length})`); if (out === '-') { await browser.close(); server.close(); process.exit(0); } }
if (!events.length) console.warn('NOTE: scene registered 0 EVENTS. Sound sync will be blind. Use Lab.ev(t, type, opts) at build time.');

const shot = async (page, t, png) => { await page.evaluate(t => window.seek(t), t); await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))); return page.screenshot((png || opt.alpha) ? { type: 'png', omitBackground: !!opt.alpha } : { type: 'jpeg', quality: 95 }); };
mkdirSync(path.dirname(path.resolve(out)), { recursive: true });

if (opt.at !== undefined) {
  const page = await open({ width: V.w, height: V.h }); writeFileSync(out, await shot(page, +opt.at, true)); console.log('frame ->', out); await browser.close(); server.close(); process.exit(0);
}
if (opt.stills) {
  const page = await open({ width: V.w, height: V.h }); const times = String(opt.stills).split(',').map(Number); const dir = out + '.frames'; mkdirSync(dir, { recursive: true });
  for (let i = 0; i < times.length; i++) writeFileSync(`${dir}/${String(i).padStart(3, '0')}.jpg`, await shot(page, times[i]));
  await browser.close(); server.close();
  const cols = Math.min(+(opt.cols || 3), times.length), rows = Math.ceil(times.length / cols), sc = +(opt.scale || Math.min(540, V.w));
  // label each tile with its time
  const vf = `drawtext=text='%{eif\\:n\\:d}':x=6:y=6:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6,scale=${sc}:-2,tile=${cols}x${rows}:padding=6:color=gray`;
  try { await run(['-y', '-framerate', '1', '-i', `${dir}/%03d.jpg`, '-vf', vf, '-frames:v', '1', out]); } catch { await run(['-y', '-framerate', '1', '-i', `${dir}/%03d.jpg`, '-vf', `scale=${sc}:-2,tile=${cols}x${rows}:padding=6:color=gray`, '-frames:v', '1', out]); }
  writeFileSync(out + '.times.txt', times.map((t, i) => `${i}: ${t}s`).join('\n')); rmSync(dir, { recursive: true });
  console.log('stills ->', out, '(tile index → time in', out + '.times.txt)'); process.exit(0);
}

// ---- video
let [r0, r1] = opt.range ? String(opt.range).split('-').map(Number) : [0, V.duration];
const f0 = Math.round(r0 * fps), f1 = Math.round(r1 * fps), N = f1 - f0;
const base = out.replace(/\.(mp4|mov)$/, ''), silent = base + (opt.alpha ? '_silent.mov' : '_silent.mp4');
const vf = sub > 1 ? ['-vf', `tmix=frames=${sub},select='eq(mod(n\\,${sub})\\,${sub - 1})',setpts=N/(${fps}*TB)`] : [];
const t0 = Date.now(); let done = 0; const per = Math.ceil(N / workers), segs = [];
await Promise.all(Array.from({ length: workers }, async (_, w) => {
  const a = f0 + w * per, b = Math.min(f1, a + per); if (a >= b) return; const seg = `${base}_seg${w}.${opt.alpha ? 'mov' : 'mp4'}`; segs[w] = seg;
  const page = await open({ width: V.w, height: V.h });
  const ff = spawn('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', String(fps * sub), '-i', '-', ...vf, '-r', String(fps), ...(opt.alpha ? ['-c:v', 'prores_ks', '-profile:v', '4', '-pix_fmt', 'yuva444p10le', '-vendor', 'apl0'] : ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', opt.crf || '16', '-preset', opt.preset || 'veryfast']), seg], { stdio: ['pipe', 'inherit', 'inherit'] });
  const closed = new Promise(r => ff.on('close', r));
  for (let f = a; f < b; f++) {
    for (let s = 0; s < sub; s++) {                 // 180° shutter: sub-frames spread over half a frame interval
      const buf = await shot(page, (f + (sub > 1 ? (s / sub) * 0.5 : 0)) / fps);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    if (++done % 15 === 0) process.stdout.write(`\r${done}/${N} frames  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  ff.stdin.end(); await closed; await page.close();
}));
const list = base + '_segs.txt'; writeFileSync(list, segs.filter(Boolean).map(s => `file '${path.resolve(s)}'`).join('\n'));
await run(['-y', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', silent]); segs.filter(Boolean).forEach(s => rmSync(s)); rmSync(list);
console.log(`\nsilent video -> ${silent} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
if (opt.audio) {
  // audio comes from sound-design-pro (already mastered): copy-mux, do NOT re-normalise here.
  await run(['-y', '-i', silent, ...(r0 > 0 ? ['-ss', String(r0)] : []), '-i', opt.audio, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', out]);
  console.log('with audio ->', out);
} else { await run(['-y', '-i', silent, '-c', 'copy', out]); console.log('(no audio) ->', out); }
await browser.close(); server.close();
