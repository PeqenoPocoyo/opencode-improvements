#!/usr/bin/env node
// Lista os efeitos sonoros que o kit criou na composição (eles nascem em tempo de execução) → ../sons.json
// {"efeitos":[{"t","arquivo","volume"}]} — o formato que ferramentas/verificar.py e o aplicativo leem para medir a
// densidade (R2). Rode na pasta do motor depois de montar.mjs:  node ferramentas/sons.mjs [saida]
import { createRequire } from "node:module";
import { writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
const require = createRequire(join(process.cwd(), "package.json"));
const { chromium } = require("playwright");
const saida = process.argv[2] || join("..", "sons.json");
const b = await chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : { channel: "chrome" });
const p = await b.newPage();
await p.goto("file://" + resolve("index.html"), { waitUntil: "domcontentloaded" });
await p.waitForFunction(() => window.__timelines && Object.keys(window.__timelines).length, null, { timeout: 20000 });
const ef = await p.evaluate(() => [...document.querySelectorAll('audio[src^="assets/sfx/"]')]
  .map((a) => ({ t: +(+a.dataset.start).toFixed(3), arquivo: a.getAttribute("src").replace("assets/sfx/", ""), volume: +a.dataset.volume }))
  .sort((x, y) => x.t - y.t));
const dur = await p.evaluate(() => Object.values(window.__timelines)[0].duration());
await b.close();
writeFileSync(saida, JSON.stringify({ efeitos: ef }, null, 1));
const semDig = ef.filter((e) => !/^type\./.test(e.arquivo)).length;
console.log(`${ef.length} efeitos (${semDig} sem a digitação · ${(semDig / dur).toFixed(2)}/s) → ${saida}`);
