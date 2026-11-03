// VSL roxo · "3 ferramentas grátis do Claude" (38,8 s) · mapa completo em assets/map.md
// Telas do Claude = ilustração (assets/mock/mocks.html). Preços reais: gamma.app/pricing e canva.com/pt_br/precos (27/10/2026).
const A = (p, n = 1, after = 0) => K.at(p, n, after);
const IMG = (f) => `assets/img/${f}`;
const SPLIT_TOP = 240; // topo do conteúdo em SPLIT (zona segura do Reels começa em 220)
const CHEST = 1250;    // linha do peito para pílulas em tela cheia

// 1) GANCHO "O Claude acabou de lançar" — bruto com HUD de filmadora → glitch → grade roxa
const tG = A("três ferramentas") - 0.05;
K.camcorder(0, tG, { label: "NOVIDADE · CLAUDE" });
K.glitch(tG);

// 2) "três ferramentas de IA" — lettering empilhado no peito, uma linha por palavra
K.punch(tG + 0.1, 1.14);
K.stack([
  { text: "3 ferramentas", t: A("três ferramentas") + 0.05, style: "blur" },
  { text: "de IA", t: A("de ia"), style: "glow" },
], { top: 1180, until: A("totalmente") - 0.05 });
K.hideMouth(tG, A("totalmente"));

// 3) "totalmente gratuitas" — flash + GRÁTIS atrás da cabeça + o fato (todos os planos, inclusive Free)
const tFree = A("gratuitas");
K.punch(A("totalmente"), 1.06);
K.flash(tFree - 0.12, { peak: 0.5 });
// (o enquadramento não deixa espaço acima da cabeça: título atrás dela some — lettering no peito)
K.stack([
  { text: "totalmente", t: A("totalmente"), style: "blur" },
  { text: "gratuitas", t: tFree, style: "glow" },
], { top: 1150, until: A("que podem") - 0.05 });
K.hideMouth(A("totalmente"), A("que podem"));
K.pill("Em todos os planos · até no Free", tFree + 0.25, { y: 1390, icon: "check", sm: true, up: true, until: A("que podem") - 0.05 });

// 4) "economizar centenas de dólares por ano" — SPLIT: o que Gamma + Canva custam por ano × R$ 0
const t4 = A("que podem") - 0.08;
K.layout("split", t4);
K.section({ kicker: "Quanto você deixa de pagar", title: "Por ano, sem o Claude", acc: [3, 4] }, t4 + 0.1, { y: SPLIT_TOP, until: A("elas se chamam") - 0.15 });
const ROW = "display:flex;justify-content:space-between;align-items:center;padding:24px 0;border-bottom:1px solid rgba(255,255,255,.12);font:700 42px/1 var(--fS)";
K.panel(`
  <div style="position:absolute;left:40px;right:40px;top:40px">
    <div class="r1" style="${ROW}"><span>Gamma Pro</span><span style="color:#ff9a7a">R$ 840<small style="font-size:24px;opacity:.7">/ano</small></span></div>
    <div class="r2" style="${ROW}"><span>Canva Pro</span><span style="color:#ff9a7a">R$ 290<small style="font-size:24px;opacity:.7">/ano</small></span></div>
    <div class="r3" style="${ROW};border:0;position:relative"><span style="color:var(--lavT)">Total</span><span>R$ 1.130<small style="font-size:24px;opacity:.7">/ano</small></span>
      <i class="x" style="position:absolute;left:-10px;right:-10px;top:46%;height:6px;border-radius:3px;background:#ff5a3a;box-shadow:0 0 14px #ff5a3a"></i></div>
    <div class="r4" style="margin-top:22px;display:flex;align-items:center;gap:18px;padding:22px 26px;border-radius:20px;background:linear-gradient(90deg,var(--btnA),var(--btnB));box-shadow:var(--glow);font:800 44px/1 var(--fS)">
      <img src="${IMG("claude-simbolo.svg")}" style="width:52px;height:52px"><span>Com o Claude</span><span style="margin-left:auto">R$ 0</span></div>
    <div class="src" style="margin-top:18px;font:500 18px/1 var(--fM);color:var(--muted);letter-spacing:.06em">PREÇOS DOS PLANOS ANUAIS · SITES OFICIAIS · OUT/2026</div>
  </div>`, A("economizar") - 0.1, {
  box: { x: 90, y: 390, w: 900, h: 560 },
  steps: [
    { sel: ".r1", t: A("economizar") },
    { sel: ".r2", t: A("centenas") },
    { sel: ".r3", t: A("dólares") },
    { sel: ".x", t: A("por ano"), anim: "strike" },
    { sel: ".r4", t: A("por ano") + 0.2, sfx: "ding" },
    { sel: ".src", t: A("por ano") + 0.3, anim: "fade", sfx: false },
  ],
  until: A("elas se chamam") - 0.15,
});

// 5) "Elas se chamam Slides, Docs e Design" — 3 cards, cada um entra no nome falado
K.section({ kicker: "Elas se chamam", title: "Slides · Docs · Design", acc: [0, 2, 4] }, A("elas se chamam"), { y: SPLIT_TOP, until: A("que ficam") - 0.12 });
K.grid([
  { img: IMG("slide-01.jpg"), label: "Slides", icon: "film", t: A("slides") },
  { img: IMG("doc.jpg"), label: "Docs", icon: "caption", t: A("docs") },
  { img: IMG("design.jpg"), label: "Design", icon: "image", t: A("design") },
], { top: 420, cols: 3, w: 284, h: 420, gx: 24, until: A("que ficam") - 0.12 });

// 6) "ficam dentro do chat que você já utiliza" — volta pra tela cheia com light leak
K.leak(A("que ficam") - 0.15, 0.55);
K.layout("full", A("que ficam") - 0.1);
K.pill("Dentro do chat do Claude", A("chat"), { y: CHEST + 60, icon: "chat", up: true, until: A("e pra utilizar") - 0.05 });

// 7) "E pra utilizar é muito fácil" — punch de impacto
K.punch(A("e pra utilizar"), 1.16);
K.kickerTop("É muito fácil", A("muito fácil"), { y: 250, until: A("é só você") - 0.1 });

// 8) "é só você pedir pra ele… uma apresentação comercial pro seu negócio" — SPLIT: chat do Claude + pedido digitando
const t8 = A("é só você") - 0.1;
K.layout("split", t8);
K.panel(`
  <div style="position:absolute;left:34px;top:30px;display:flex;align-items:center;gap:16px">
    <img src="${IMG("claude-simbolo.svg")}" style="width:56px;height:56px">
    <div><div style="font:800 32px/1 var(--fS)">Claude</div><div style="font:500 20px/1.4 var(--fS);color:var(--muted)">Nova conversa</div></div>
  </div>
  <div style="position:absolute;left:34px;right:34px;top:130px;font:600 26px/1.4 var(--fS);color:var(--muted)">Como posso te ajudar hoje?</div>`, t8 + 0.1, {
  box: { x: 90, y: SPLIT_TOP, w: 900, h: 700 },
  until: A("a partir daí") - 0.1,
});
K.prompt("Crie uma apresentação comercial pro meu negócio, a Padaria Trigo & Mel", A("pedir pra ele"), {
  x: 120, y: 560, w: 840, cps: 21, send: true, until: A("a partir daí") - 0.1,
});

// 9) "A partir daí ele vai preparar todos os slides pra você" — Claude gerando → leque de slides
K.section({ kicker: "Claude Slides", title: "Sua apresentação pronta", acc: [2] }, A("a partir daí"), { y: SPLIT_TOP, until: A("depois") - 0.15 });
K.progress("Criando os slides", A("a partir daí") + 0.1, A("todos os slides") - A("a partir daí") - 0.25, { box: { x: 90, y: 420, w: 900 }, until: A("todos os slides") });
K.fan([IMG("slide-02.jpg"), IMG("slide-01.jpg"), IMG("slide-04.jpg")], A("todos os slides"), { top: 600, w: 400, h: 225, until: A("depois") - 0.15 });

// 10) "Depois, com seus slides prontos, você pode exportar… pra PowerPoint ou pra Google Slides"
K.layout("full", A("depois") - 0.1);
K.stamp("PRONTOS ✓", A("prontos"), { x: 600, y: 300, rot: -7, until: A("exportar") - 0.05 });
K.panel(`
  <div class="deck" style="position:absolute;left:30px;top:76px;width:330px;height:186px;border-radius:14px;overflow:hidden;border:2px solid rgba(var(--hiRGB),.45)"><img src="${IMG("slide-01.jpg")}" style="width:100%;height:100%;object-fit:cover"></div>
  <svg class="arr" viewBox="0 0 120 40" style="position:absolute;left:378px;top:150px;width:110px;height:40px;fill:none;stroke:var(--lav);stroke-width:4;stroke-linecap:round"><path d="M4 20H104M88 6l16 14-16 14"/></svg>
  <div class="pp" style="position:absolute;left:510px;top:70px;display:flex;align-items:center;gap:18px;font:800 34px/1 var(--fS)"><img src="${IMG("powerpoint.svg")}" style="width:78px;height:78px">PowerPoint</div>
  <div class="gs" style="position:absolute;left:510px;top:180px;display:flex;align-items:center;gap:18px;font:800 34px/1 var(--fS)"><img src="${IMG("google-slides.svg")}" style="width:78px;height:78px">Google Slides</div>`, A("exportar") - 0.05, {
  title: "Exportar apresentação",
  box: { x: 90, y: 1170, w: 900, h: 300 },
  steps: [
    { sel: ".deck", t: A("exportar"), anim: "slide" },
    { sel: ".arr path", t: A("apresentação inteira"), anim: "draw" },
    { sel: ".pp", t: A("powerpoint") },
    { sel: ".gs", t: A("google slides") },
  ],
  until: A("mas a novidade") - 0.05,
});

// 11) "Mas a novidade não para só nos slides" — punch + título atrás da cabeça
K.punch(A("mas a novidade"), 1.2);
K.stack([
  { text: "não para", t: A("não para"), style: "blur" },
  { text: "só nos slides", t: A("só nos slides"), style: "letters" },
], { top: 1150, until: A("na mesma conversa") - 0.08 });
K.hideMouth(A("não para"), A("na mesma conversa"));

// 12) "Na mesma conversa… pedir pra ele criar um roteiro" — SPLIT: novo pedido + roteiro cai no quadro
const t12 = A("na mesma conversa") - 0.1;
K.layout("split", t12);
K.hideMouth(t12 - 0.05, t12 + 0.5); // a legenda não acompanha o quadro encolhendo
K.section({ kicker: "Na mesma conversa", title: "Do roteiro ao carrossel", acc: [3] }, t12 + 0.1, { y: SPLIT_TOP, until: A("então ao invés") - 0.15 });
K.prompt("Agora cria um roteiro de carrossel com base nessa apresentação", A("você pode", 2), {
  x: 90, y: 400, w: 900, cps: 24, until: A("transformar") - 0.1,
});
const box = K.dashbox("ROTEIRO", A("criar um roteiro"), { box: { x: 300, y: 580, w: 480, h: 380 } });
box.drop(IMG("doc.jpg"), A("roteiro"), { w: 300, h: 360 });
box.out(A("transformar") - 0.1);

// 13) "transformar em carrosséis no Instagram com base nesse material" — leque do carrossel + Instagram
K.fan([IMG("car-01.jpg"), IMG("car-02.jpg"), IMG("car-03.jpg"), IMG("car-04.jpg")], A("carrosséis"), { top: 470, w: 230, h: 288, until: A("então ao invés") - 0.15 });
K.panel(`<div class="ig" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:16px;font:800 30px/1 var(--fS)"><img src="${IMG("instagram.svg")}" style="width:54px;height:54px">Carrossel no Instagram</div>`, A("instagram"), {
  box: { x: 240, y: 860, w: 600, h: 96 },
  steps: [{ sel: ".ig", t: A("instagram") }],
  until: A("então ao invés") - 0.15,
});

// 14) "ao invés de pagar pelo Gamma ou pelo Canva, você tem tudo em uma única conversa"
K.layout("full", A("então ao invés") - 0.1);
K.pill("Gamma", A("gamma"), { y: CHEST - 40, kind: "strike", up: true, until: A("tudo em uma") - 0.05 });
K.pill("Canva", A("canva"), { y: CHEST + 60, kind: "strike", up: true, until: A("tudo em uma") - 0.05 });
K.flash(A("tudo em uma") - 0.12, { peak: 0.45 });
K.punch(A("tudo em uma"), 1.14);
K.stack([
  { text: "tudo em", t: A("tudo em uma"), style: "blur" },
  { text: "1 conversa", t: A("única conversa"), style: "glow" },
], { top: 1150, until: A("comenta") - 0.05 });
K.hideMouth(A("tudo em uma"), A("comenta"));

// 15) CTA "Comenta SLIDES e eu te envio o link"
K.punch(A("comenta") - 0.02, 1.06);
K.cta("Comenta SLIDES", A("comenta"), { y: 1300, w: 820, clickAt: 1.1 });
K.kickerTop("Link direto na sua DM", A("e eu te envio"), { y: 250 });

// legenda que segue a boca (depois dos layouts: lê o enquadramento de cada quadro)
K.mouthCaps({ accent: ["Claude", "IA", "gratuitas", "economizar", "dólares", "Slides", "Docs", "Design", "chat", "fácil", "apresentação",
  "negócio", "prontos", "PowerPoint", "Google", "novidade", "roteiro", "carrosséis", "Instagram", "Gamma", "Canva", "conversa", "SLIDES", "link"] });
