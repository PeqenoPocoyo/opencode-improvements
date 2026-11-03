#!/usr/bin/env node
// Exporta cada tela ilustrativa (elemento com id) de um HTML próprio em JPG — "ilustração declarada" (R3).
//   node render-ilustracoes.mjs <arquivo.html> <pasta de saída> [id1 id2 …]
// Sem ids, exporta todo elemento com class="shot". Usa o playwright do projeto de composição (rode na raiz dele)
// e o Chrome do sistema (ou CHROME=<executável>). Registre cada arquivo em assets/SOURCES.md como ilustração.
import { createRequire } from "node:module";
import { resolve, join } from "node:path";
const require = createRequire(join(process.cwd(), "package.json"));
const { chromium } = require("playwright");
const [html, outDir, ...ids] = process.argv.slice(2);
if (!html || !outDir) { console.error("uso: render-ilustracoes.mjs <arquivo.html> <pasta> [ids…]"); process.exit(1); }
const b = await chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : { channel: "chrome" });
const p = await b.newPage({ viewport: { width: 1700, height: 1000 }, deviceScaleFactor: 1 });
await p.goto("file://" + resolve(html), { waitUntil: "networkidle" });
await p.evaluate(() => document.fonts.ready);
const lista = ids.length ? ids : await p.$$eval(".shot[id]", (els) => els.map((e) => e.id));
for (const id of lista) { await (await p.$("#" + id)).screenshot({ path: join(outDir, `${id}.jpg`), quality: 90, type: "jpeg" }); }
console.log(`${lista.length} ilustrações → ${outDir}`); await b.close();
