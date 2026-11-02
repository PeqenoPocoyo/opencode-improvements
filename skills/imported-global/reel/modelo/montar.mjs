#!/usr/bin/env node
// Monta index.html do estilo 03 · VSL com o kit da referência aprovada (kit/, intocado).
// Rode na pasta do motor do projeto (<P>/motor, a cópia deste modelo/ com vsl.json, src/ e assets/):
//   node montar.mjs                 composição completa
//   node montar.mjs --so-camera     só a câmera nos mesmos layouts e tempos (base da zona segura: render/_camera-so.mp4);
//                                   rode de novo sem a opção depois do render
// O que faz:
// - copia kit/kit.js, kit.css, fonts/ e sfx/ para assets/ e o GSAP 3.14.2 do node_modules (npm install);
// - cria src/index.template.html (do kit), src/beats.js (de beats-modelo.js) e vsl.json (de vsl-padrao.json) se faltarem;
// - lê assets/transcript.json ({"words":[{"text","start","end"}],"audio_duration_secs"}) + assets/caption-fixes.json;
// - liga a legenda que segue a boca se existir assets/face-track.json (ferramentas/rastrear-boca.py);
// - liga o recorte do apresentador se existir assets/matte.webm;
// - aplica a PELE (pele-resolvida.json aqui ou na pasta-mãe): cores → variáveis do kit (assets/pele.css),
//   fontes → assets/fonts/fontes.css; com origem "nativa" nada muda e o resultado é o da referência;
// - aplica o SOM: padrão do vsl.json = "enxuto" (R2); pele com efeitos desligados → nenhum; intensidade 0,3 → enxuto
//   e −3 dB; 0,6 ou ausente → o que o vsl.json diz; 0,85 → "referencia" (o som exato do vídeo aprovado);
// - escreve index.html e meta.json; imprime o resumo.
import { readFileSync, writeFileSync, existsSync, cpSync, mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const MOD = dirname(fileURLToPath(import.meta.url));
const M = join(MOD, "kit");
const SO_CAMERA = process.argv.includes("--so-camera");
const read = (p, d) => (existsSync(p) ? JSON.parse(readFileSync(p, "utf8")) : d);

mkdirSync("assets", { recursive: true });
for (const f of ["kit.js", "kit.css"]) cpSync(join(M, f), join("assets", f));
// GSAP 3.14.2 vem do npm do projeto (mesmo arquivo da referência; a licença da biblioteca fica no node_modules)
const gsapSrc = ["node_modules/gsap/dist/gsap.min.js", join(MOD, "node_modules/gsap/dist/gsap.min.js")].find(existsSync);
if (!gsapSrc) { console.error("falta o GSAP: rode npm install na raiz do projeto (package.json do modelo)"); process.exit(1); }
cpSync(gsapSrc, join("assets", "gsap.min.js"));
cpSync(join(M, "fonts"), join("assets", "fonts"), { recursive: true });
cpSync(join(M, "sfx"), join("assets", "sfx"), { recursive: true });
mkdirSync("src", { recursive: true });
if (!existsSync("src/index.template.html")) cpSync(join(M, "index.template.html"), "src/index.template.html");
if (!existsSync("src/beats.js")) cpSync(join(MOD, "beats-modelo.js"), "src/beats.js");
if (!existsSync("vsl.json")) cpSync(join(MOD, "vsl-padrao.json"), "vsl.json");

const t = JSON.parse(readFileSync("assets/transcript.json", "utf8"));
const cfg = read("vsl.json", {});
for (const k of Object.keys(cfg)) if (k.startsWith("_")) delete cfg[k]; // chaves de comentário
const dur = +(cfg.dur || t.audio_duration_secs).toFixed(3);
cfg.dur = dur;

// correções de transcrição (nomes/termos que o Whisper erra): assets/caption-fixes.json {"errado": "certo"}
const fix = read("assets/caption-fixes.json", {});
const fixW = (s) => { if (s in fix) return fix[s]; const m = s.match(/^(.*?)([.,!?;:]*)$/); return m && m[1] in fix ? fix[m[1]] + m[2] : s; };
const words = t.words.map((w) => ({ text: fixW(w.text), start: +w.start.toFixed(3), end: +w.end.toFixed(3) }));
const face = existsSync("assets/face-track.json") ? JSON.parse(readFileSync("assets/face-track.json", "utf8")) : null;

// ---------------- pele ----------------
const pelePath = ["pele-resolvida.json", "../pele-resolvida.json"].find(existsSync);
const pele = pelePath ? read(pelePath, null) : null;
const hex = (h) => { const x = h.replace("#", ""); const n = parseInt(x.length === 3 ? x.split("").map((c) => c + c).join("") : x, 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };
const toHex = (c) => "#" + c.map((v) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, "0")).join("");
const mix = (a, b, k) => toHex(hex(a).map((v, i) => v + (hex(b)[i] - v) * k)); // k=0 → a, k=1 → b
const lt = (c, k) => mix(c, "#ffffff", k), dk = (c, k) => mix(c, "#000000", k);
const rgb = (c) => hex(c).join(",");
let peleCss = "", peleNota = "nativa (igual à referência)";
const cores = pele && pele.cores;
if (cores && !String(cores.origem || "nativa").startsWith("nativa")) {
  const { fundo: F, texto: T, destaque: D, apoio: A, acento2: X } = cores;
  peleCss += `#vsl{
  --bg0:${dk(F, 0.45)}; --bg1:${F}; --bg2:${lt(F, 0.12)}; --bg3:${lt(F, 0.25)}; --panel2:${dk(F, 0.15)}; --thumb:${lt(F, 0.08)};
  --panelRGB:${rgb(lt(F, 0.1))}; --panel2RGB:${rgb(dk(F, 0.2))}; --shadowRGB:${rgb(dk(F, 0.8))};
  --blob1:${mix(D, F, 0.3)}; --blob2:${mix(dk(D, 0.35), F, 0.3)}; --blob3:${mix(dk(D, 0.2), F, 0.3)};
  --acc:${D}; --acc2:${lt(D, 0.08)}; --deep:${dk(D, 0.1)}; --accRGB:${rgb(D)};
  --btnA:${D}; --btnB:${lt(D, 0.2)};
  --tintTopRGB:${rgb(dk(D, 0.3))}; --tintMidRGB:${rgb(dk(D, 0.6))}; --tintEndRGB:${rgb(dk(D, 0.88))};
  --lav:${A}; --lav2:${dk(A, 0.08)}; --lavT:${lt(A, 0.4)}; --hiRGB:${rgb(A)};
  --tint2:linear-gradient(100deg,rgba(${rgb(A)},.55) 0%,rgba(${rgb(D)},.25) 45%,rgba(${rgb(lt(D, 0.2))},.35) 100%);
  --white:${T}; --muted:${X}; --dim:${dk(X, 0.35)};
}
#vsl, html, body{ color:${T}; }\n`;
  peleNota = `cores ${cores.origem}`;
}
const fontes = pele && pele.fontes;
let fontesLink = "";
if (fontes && existsSync("assets/fonts/fontes.css")) {
  const fam = (s) => s && s.familia && s.nativa !== true && s.familia !== "nativa" ? `"${s.familia}"` : null;
  const fd = fam(fontes.destaque), fs = fam(fontes.texto);
  if (fd || fs) {
    fontesLink = `<link rel="stylesheet" href="assets/fonts/fontes.css">\n`;
    peleCss += `#vsl{ ${fd ? `--fD:${fd},sans-serif;` : ""} ${fs ? `--fS:${fs},sans-serif;` : ""} }\n`;
    peleNota += ` · fontes ${[fd, fs].filter(Boolean).join(" / ")}`;
  }
}
if (peleCss) writeFileSync("assets/pele.css", "/* gerado por montar.mjs a partir de pele-resolvida.json — não edite */\n" + peleCss);

// ---------------- som ----------------
let sfxNota = cfg.sfxModo === "enxuto" ? "enxuto (R2)" : "como na referência";
const som = pele && pele.som;
if (som && som.sfx === false) { cfg.sfx = false; sfxNota = "desligado (pele)"; }
else if (som && som.sfxIntensidade != null) {
  const base = cfg.sfxVol ?? 0.55;
  if (som.sfxIntensidade <= 0.3) { cfg.sfxModo = "enxuto"; cfg.sfxVol = +(base * 0.708).toFixed(3); sfxNota = "enxuto (R2) −3 dB"; }
  else if (som.sfxIntensidade >= 0.85) { cfg.sfxModo = "referencia"; sfxNota = "como na referência (~1,4/s; o verificar.py reprova o item de SFX)"; }
}
if (SO_CAMERA) { cfg.sfx = false; sfxNota = "nenhum (só câmera)"; }
const sfxFiltro = cfg.sfxModo === "enxuto" ? readFileSync(join(MOD, "sfx-enxuto.js"), "utf8") : "";

// ---------------- matte e música ----------------
const matte = existsSync("assets/matte.webm")
  ? `<div class="lens" id="lensMatte"><video id="matte" src="assets/matte.webm" data-start="0" data-duration="${dur}" data-track-index="2" muted playsinline></video></div>`
  : "<!-- sem assets/matte.webm: texto 'atrás da cabeça' fica na frente -->";
let music = "";
if (cfg.music && existsSync(join("assets", cfg.music.file))) {
  const s = cfg.music.start || 0;
  music = `<audio id="music" src="assets/${cfg.music.file}" data-start="${s}" data-duration="${(dur - s).toFixed(3)}" data-track-index="3" data-volume="${cfg.music.volume ?? 0.18}"></audio>`;
}

// ---------------- index.html ----------------
const beats = readFileSync("src/beats.js", "utf8");
let html = readFileSync("src/index.template.html", "utf8")
  .replaceAll("__DUR__", String(dur)).replace("__CFG__", JSON.stringify(cfg)).replace("__WORDS__", JSON.stringify(words)).replace("__FACE__", JSON.stringify(face))
  .replace("__CLASS__", `t-${cfg.theme || "roxo"} f-${cfg.font || "padrao"}`)
  .replace("__MATTE__", matte).replace("__MUSIC__", music).replace("__BEATS__", beats + (sfxFiltro ? "\n" + sfxFiltro : ""));
if (peleCss) html = html.replace('<link rel="stylesheet" href="assets/kit.css">', `<link rel="stylesheet" href="assets/kit.css">\n${fontesLink}<link rel="stylesheet" href="assets/pele.css">`);
if (SO_CAMERA) html = html.replace("</head>", `<style>#ui,#cap,#fx,#behind,#inset,#cover,#under{display:none!important}</style>\n</head>`);
writeFileSync("index.html", html);
const meta = read("meta.json", {});
Object.assign(meta, { id: "vsl", width: 1080, height: 1920, fps: 30 });
writeFileSync("meta.json", JSON.stringify(meta, null, 2));
if (!existsSync("hyperframes.json")) cpSync(join(MOD, "hyperframes.json"), "hyperframes.json");
console.log(`index.html ok${SO_CAMERA ? " (SÓ CÂMERA — rode de novo sem --so-camera depois do render)" : ""} — ${dur}s · ${words.length} palavras · boca: ${face ? "sim" : "NÃO (rode ferramentas/rastrear-boca.py)"} · matte: ${matte.startsWith("<div") ? "sim" : "não"} · música: ${music ? "sim" : "não"} · pele: ${peleNota} · sfx: ${sfxNota}`);
