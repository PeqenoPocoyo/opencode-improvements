// ===== modo "enxuto" de efeitos sonoros (vsl.json "sfxModo": "enxuto"; injetado por montar.mjs depois dos beats) =====
// O padrão deste estilo. O kit põe som em toda peça (a referência aprovada tem ~1,4 efeito/s); este filtro aplica a
// regra R2 sem mexer no kit, contando TUDO (a digitação também, como o verificar.py conta):
// 1. mantém os sons das peças grandes (glitch, boom, carimbo, clique, whoosh de troca, ding) e a digitação;
// 2. só deixa um som pequeno (pop, swoosh, tick, shimmer) quando ele cai ≥ 0,6 s depois do último som mantido;
// 3. corta sons pequenos (do fim para o começo, um sim um não, em passadas) até ficar ≤ 0,8 efeito/s;
// 4. se ainda passar, corta whoosh/swoosh e ding (nunca glitch, boom, carimbo, clique nem digitação).
(() => {
  const GRANDE = ["glitch", "boom", "stamp", "click", "whoosh", "ding"], FIXO = ["glitch", "boom", "stamp", "click", "type"];
  const ALVO = 0.8;
  const nome = (a) => a.getAttribute("src").replace(/^.*\/|\.wav$/g, "");
  const all = [...document.querySelectorAll('#vsl audio[src^="assets/sfx/"]')]
    .map((a) => ({ a, n: nome(a), t: +a.dataset.start })).sort((x, y) => x.t - y.t);
  let kept = [];
  let last = -9, lastBig = -9;
  for (const s of all) {
    if (s.n === "type") { kept.push(s); continue; }
    if (GRANDE.includes(s.n)) {
      if (s.t - lastBig < 0.25) { s.a.remove(); continue; }
      kept.push(s); last = lastBig = s.t; continue;
    }
    if (s.t - last >= 0.6) { kept.push(s); last = s.t; } else s.a.remove();
  }
  const dur = CFG.dur || 1, dens = () => kept.length / dur;
  const corta = (filtro) => {
    while (dens() > ALVO) {
      const lista = kept.filter(filtro);
      if (!lista.length) return;
      for (let i = lista.length - 1; i >= 0 && dens() > ALVO; i -= 2) { lista[i].a.remove(); kept = kept.filter((k) => k !== lista[i]); }
    }
  };
  corta((s) => !GRANDE.includes(s.n) && s.n !== "type");   // pequenos
  corta((s) => !FIXO.includes(s.n));                         // whoosh, swoosh, ding
  console.log(`sfx enxuto: ${kept.length} efeitos (${dens().toFixed(2)}/s, digitação incluída)`);
})();
