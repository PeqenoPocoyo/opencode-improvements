#!/usr/bin/env node
// Cards estáticos da fase 1 (references/entrega.md): um PNG 1080×1920 por tela da planta, tirado do próprio motor
// no meio de cada tela (ou no "t_card" da tela, se houver), com a câmera real, as peças posicionadas e a legenda.
// Rode na pasta do motor, depois de escrever ../entrega/planta.json (n, layout, de, ate, fala, tela) e montar:
//   node ferramentas/cards.mjs            → ../entrega/cards/P01.png… e o campo "imagem" de cada tela preenchido
// A url da imagem leva ?v=<hash do arquivo>: card que não mudou mantém a url (e o status que a pessoa deu).
import { readFileSync, writeFileSync, existsSync, mkdirSync, copyFileSync, readdirSync, rmSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { join } from "node:path";
const PL = join("..", "entrega", "planta.json"), OUT = join("..", "entrega", "cards"), TMP = join("snapshots", "_cards");
if (!existsSync(PL)) { console.error("falta ../entrega/planta.json"); process.exit(1); }
const planta = JSON.parse(readFileSync(PL, "utf8"));
const tempos = planta.map((p) => +(p.t_card ?? (p.de + (p.ate - p.de) / 2)).toFixed(2));
rmSync(TMP, { recursive: true, force: true }); mkdirSync(OUT, { recursive: true });
execFileSync("npx", ["hyperframes", "snapshot", "--at", tempos.join(","), "-o", TMP], { stdio: ["ignore", "ignore", "inherit"] });
const frames = readdirSync(TMP).filter((f) => /^frame-\d+-at-/.test(f)).sort();
planta.forEach((p, i) => {
  const nome = `P${String(p.n ?? i + 1).padStart(2, "0")}.png`;
  copyFileSync(join(TMP, frames[i]), join(OUT, nome));
  const h = createHash("sha1").update(readFileSync(join(OUT, nome))).digest("hex").slice(0, 8);
  p.imagem = `entrega/cards/${nome}?v=${h}`;
});
writeFileSync(PL, JSON.stringify(planta, null, 2));
console.log(`${planta.length} cards em ../entrega/cards/ (tempos: ${tempos.join(", ")})`);
