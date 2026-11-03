// ============================================================================================================
// beats.js — o roteiro visual do reel no estilo 03 · VSL (motor da referência aprovada).
// Só chamadas K.* com tempos de K.at("frase exata do transcript"). K.at LANÇA ERRO se a frase não existir:
// corrija a frase, nunca chute segundos. Palavra repetida: K.at("frase", n) = n-ésima ocorrência;
// mais contexto resolve ("te entregar" em vez de "entregar"). Exemplo completo e aprovado: exemplo/beats-exemplo.js.
//
// Gramática (fala → câmera → peça), na ordem em que aparece num reel típico:
//   gancho "novidade/antes"     FULL bruto      K.camcorder(0, t, {label}) → K.glitch(t)
//   frase-tese / número         FULL + punch    K.punch(t, 1.14–1.2) + K.stack([...]) no PEITO (top ~1150) + K.hideMouth
//   fato com fonte              FULL            K.pill("texto curto", t, {y: ~1390, icon, sm, up})
//   preço / comparação          SPLIT           K.section + K.panel(tabela com .r1 .r2 … revelados em steps na palavra)
//   lista de 2–4 coisas         SPLIT           K.section + K.grid([{img,label,icon,t}])
//   "é só pedir…"               SPLIT           K.panel(chat) + K.prompt("pedido", t, {cps, send})
//   "ele faz…"                  SPLIT           K.progress(label, t, d) → K.fan([imgs], t)
//   resultado pronto            FULL            K.stamp("PRONTOS ✓", t, {x, y}) NO PEITO + K.panel(exportar) y ≥ 1170
//   virada "mas não para…"      FULL + punch    K.stack no peito
//   jeito antigo × novo         FULL            K.pill(nome, t, {kind:"strike"}) → K.flash → K.stack
//   CTA                         FULL            K.cta("Comenta PALAVRA", t, {y:1300, clickAt}) + kicker NO PEITO
//   (fim)                                       K.mouthCaps({accent:[palavras-chave]}) — SEMPRE por último
//
// Regras que fazem o resultado ficar no nível da referência:
// - toda troca FULL↔SPLIT com K.layout (animada, 0,45 s) e K.hideMouth(t − 0.05, t + 0.5) no mesmo instante;
// - nada sobre o rosto (R1): lettering, pílulas, carimbo e kicker no peito (y ≥ ~1150 no FULL); topo só no SPLIT;
// - algo novo a cada 1,5–3 s; FULL ~50 % / SPLIT ~50 % (sem PIP na referência);
// - cada número e cada fato da tela com fonte em assets/SOURCES.md; tela de produto sem print = ilustração declarada.
// ============================================================================================================
const A = (p, n = 1, after = 0) => K.at(p, n, after);
const IMG = (f) => `assets/img/${f}`;
const SPLIT_TOP = 240;  // topo do conteúdo em SPLIT (zona segura começa em 220)
const CHEST = 1250;     // linha do peito para pílulas em tela cheia

// --- ponto de partida neutro (funciona com qualquer transcript; troque pelo mapa do vídeo) -------------------
const w = WORDS, t2 = w.length > 3 ? w[3].start : 1;
K.camcorder(0, t2 - 0.05, { label: "NOVIDADE" });
K.glitch(t2 - 0.05);
K.punch(t2 + 0.05, 1.14);

// --- 1) GANCHO ---------------------------------------------------------------------------------------------
// const tG = A("primeiras palavras da tese") - 0.05;
// K.camcorder(0, tG, { label: "NOVIDADE · PRODUTO" });
// K.glitch(tG);
// K.punch(tG + 0.1, 1.14);
// K.stack([{ text: "palavra 1", t: A("palavra 1") + 0.05, style: "blur" }, { text: "palavra 2", t: A("palavra 2"), style: "glow" }],
//         { top: 1180, until: A("próxima frase") - 0.05 });
// K.hideMouth(tG, A("próxima frase"));

// --- 2) SPLIT com painel revelado na palavra --------------------------------------------------------------
// const t4 = A("frase do painel") - 0.08;
// K.layout("split", t4);
// K.hideMouth(t4 - 0.05, t4 + 0.5);
// K.section({ kicker: "Kicker curto", title: "Título de 3–5 palavras", acc: [3, 4] }, t4 + 0.1, { y: SPLIT_TOP, until: A("frase seguinte") - 0.15 });
// K.panel(`<div class="r1">…</div><div class="r2">…</div>`, A("palavra do 1º item") - 0.1, {
//   box: { x: 90, y: 390, w: 900, h: 560 },
//   steps: [{ sel: ".r1", t: A("palavra do 1º item") }, { sel: ".r2", t: A("palavra do 2º item"), sfx: "ding" }],
//   until: A("frase seguinte") - 0.15 });

// --- 3) volta para FULL -----------------------------------------------------------------------------------
// K.leak(A("frase de volta") - 0.15, 0.55);
// K.layout("full", A("frase de volta") - 0.1);
// K.pill("Texto curto com fonte", A("palavra"), { y: CHEST + 60, icon: "chat", up: true, until: A("próxima") - 0.05 });

// --- 4) CTA -----------------------------------------------------------------------------------------------
// K.punch(A("comenta") - 0.02, 1.06);
// K.cta("Comenta PALAVRA", A("comenta"), { y: 1300, w: 820, clickAt: 1.1 });

// legenda que segue a boca — SEMPRE por último (lê o enquadramento de cada quadro)
K.mouthCaps({ accent: [] });
