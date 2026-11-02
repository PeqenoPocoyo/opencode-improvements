# skill reel

Skill de Claude Code que **corta e edita um reel** (9:16) a partir da gravação bruta de alguém falando, sem
painel e sem escolhas: manda o vídeo, ela corta e edita.

- **Corte**: tira silêncios, respirações, "éé", gaguejos, erros, retomadas e repetições. Corte pelo som (volume +
  timbre, calibrado pelo nível da gravação), bordas no vale de energia, cortes J/L e conferência de cada emenda
  por transcrição. É o motor de corte aprovado em produção (out/2026), copiado intacto.
- **Edição**: o motor **VSL com interface animada** — a câmera alterna tela cheia com punch-in e tela dividida com
  o apresentador num card; cada palavra-chave falada vira uma peça de interface que entra exatamente na palavra;
  legenda que segue a boca; efeitos sonoros enxutos; áudio a −14 LUFS. É o mesmo kit (intocado) e as mesmas
  regras que produziram o reel de referência aprovado; remontado, o exemplo sai idêntico pixel a pixel.

Entrega `render/reel-v1.mp4` verificado (`VERIFY.md`, folha de quadros, zona segura, LUFS) e itera a pedido.

## Instalar
```bash
git clone https://github.com/Felpborges/skill-reel.git ~/.claude/skills/reel
```
Depois, no Claude Code, é só mandar o vídeo e pedir "edita esse reel" (ou `/reel`).

## O que a máquina precisa
| Para | Ferramenta |
|---|---|
| corte e transcrição | `ffmpeg`, `whisper-cli` (whisper.cpp) + modelo `ggml-large-v3-turbo.bin` em `~/.cache/whisper-cpp/` (ou `WHISPER_MODEL`), Python 3 com `numpy` |
| enquadramento, zona segura, legenda que segue a boca | `opencv-python-headless` (e, se quiser o rastreio fino, `mediapipe` num Python apontado por `VSL_PYTHON`) |
| composição e render | Node 20+ (o `preparar.sh` instala `hyperframes` 0.7.109, `gsap` 3.14.2 e `playwright`), Google Chrome (ou `CHROME=<executável>`) |

`python3 corte/scripts/0-checar.py` diz o que falta e como instalar. Mac: `brew install ffmpeg whisper-cpp`.

## Como funciona (o fluxo que o `SKILL.md` segue)
1. **Corte** (`corte/`): mapa de tomadas pela energia → escolha editorial dos *keeps* → transcrição que não esconde
   vícios → motor de corte → conferência (texto, repetições, emendas, pausas). Sai `clean.mp4` + `cortepalavras.json`.
2. **Motor VSL** (`modelo/`): `preparar.sh` (câmera 9:16 com a voz, transcript, rastreio da boca) → transcript
   corrigido → enquadramento medido (`vsl.json`) → material real com fontes (`SOURCES.md`) → mapa de beats →
   `src/beats.js` (só chamadas `K.*` ancoradas na fala) → lint → snapshots → zona segura → render → áudio final →
   `verificar.py` → `reel-v1.mp4`.

## Estrutura
```
SKILL.md              o fluxo que o Claude segue
regras-da-casa.md     R1–R11 (rosto nunca coberto, SFX com parcimônia, material real, nenhuma palavra comida, −14 LUFS…)
ESTILO.md             a especificação do motor VSL (layouts, movimento, legenda, peças, som, aceite, lições de produção)
pele.json             valores nativos (fontes, cores, invariantes)
corte/                motor de corte: CORTE.md · references/EDICAO-BRUTA.md · scripts/ · exemplo/ (gabarito aprovado)
modelo/               motor VSL: kit/ · montar.mjs · preparar.sh · ferramentas/ · exemplo/ (o reel aprovado inteiro)
ferramentas/          preparar.py · rosto.py · ancoras.py · verificar.py · zona-segura.py · recortar.py · audio-final.sh
anexos/               quadros da referência e o antes × depois da cor
```

## Licenças do material embutido
Fontes Anybody, Plus Jakarta Sans e JetBrains Mono sob OFL (arquivos `OFL-*.txt` em `modelo/kit/fonts/`); os efeitos
sonoros de `modelo/kit/sfx/` são procedurais (gerados por `modelo/ferramentas/gerar-sfx.mjs`); GSAP e HyperFrames vêm
pelo `npm`. Os logos do exemplo vêm do Wikimedia Commons e estão listados em `modelo/exemplo/SOURCES.md`.
