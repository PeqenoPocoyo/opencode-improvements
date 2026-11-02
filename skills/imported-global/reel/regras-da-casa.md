# Regras da casa — valem para TODOS os estilos

*Lições de produção real. Todo estilo obedece a este bloco. Quando uma regra daqui conflitar com a
regra de um estilo, **vale esta**.*

## R1 · O rosto nunca é coberto
Nenhuma imagem, card, chip, painel, carimbo, título ou motion fica sobre o rosto do apresentador (da
testa ao queixo), nem escurecido, nem "só por um instante". Para mostrar algo enquanto ele fala, em
ordem de preferência:
1. **Tela dividida:** gráficos na metade de cima (y 270–810), câmera na metade de baixo com o rosto
   inteiro (o vídeo desce ≈ 990 − topo da cabeça) e legenda na costura (y ≈ 830). Corte instantâneo
   quando uma cena de tela cheia esconde a troca; senão, um deslize de 0,4 s com a legenda escondida.
2. **Abaixo do rosto:** objetos pequenos (chips, 2–3 cards pequenos, lettering) entre o queixo e a legenda.
3. **Cena de fundo própria:** uma tela sem o apresentador, com os elementos distribuídos.

Títulos "atrás da cabeça" (com recorte do apresentador) só quando sobra espaço acima da cabeça: meça
o topo da cabeça (`ferramentas/rosto.py`). Com menos de ~300 px livres, troque por lettering no
peito. Todo snapshot é conferido para esta regra; um quadro com algo sobre o rosto é reprovado.

## R2 · Efeitos sonoros com parcimônia
No máximo **~0,85 SFX por segundo** (um reel de 40 s tem ~34, não 45).
- O whoosh entra só em troca de cena de verdade.
- A batida/hit entra só em carimbo, X ou momento de impacto.
- Sem som em chip pequeno, em item de lista menor ou em elemento que entra < 0,6 s depois de outro som.
- Volumes baixos (0,1–0,2 do volume da voz).
- Digitação: sample natural, ritmo humano (~9 teclas/s), contínua sobre o trecho inteiro, nunca
  rajada sintética; ≈ 12 dB abaixo da voz.
- Sons gerados localmente, sem licença envolvida (`ferramentas/sfx.sh`):
  - whoosh: `ffmpeg -f lavfi -i "anoisesrc=color=pink:d=0.55" -af "highpass=f=300,lowpass=f=5500,afade=t=in:d=0.28,afade=t=out:st=0.3:d=0.25" whoosh.wav`;
  - hit: seno de 52 Hz com decaimento de 0,6 s;
  - pop: 1,25 kHz por 90 ms;
  - tick: ruído branco de 50 ms com passa-alta.

## R3 · Material real e verificado
- Toda afirmação falada que vira tela é conferida numa **página oficial** (data da consulta anotada).
- Todo número na tela tem fonte (preço oficial, plano, período).
- **Prioridade de imagem:** 1. print/logo oficial; 2. Wikimedia Commons / Openverse com licença;
  3. arquivos do próprio apresentador; 4. **ilustração declarada**: HTML próprio, empresa fictícia,
  rotulada como ilustração.
- **Nunca invente:** logo, capa, print, número, resultado ou contagem de seguidores. Marca sem logo
  livre entra só como texto.
- CAPTCHA/anti-robô nunca se burla: troque de ferramenta ou peça o print ao apresentador.
- Tudo listado em `assets/SOURCES.md` (arquivo, origem, licença, data).
- Se fala e tela usarem moedas ou unidades diferentes, confira a coerência e avise na entrega.

## R4 · Cor natural no rosto
Nada de grade agressiva: o rosto fica natural. A identidade de cor vive nos gráficos (cards,
pílulas, brilhos), não na pele. Valores aprovados quando há grade:
`saturate(1.04) contrast(1.05) brightness(0.97)`; camadas de tinta ≤ 0,3.
Grade mais forte só com antes × depois mostrado e aprovado. Nesta skill a cor da câmera é só o filtro
aprovado do `vsl.json`; qualquer grade a mais respeita este teto.

## R5 · Corte: nenhuma palavra comida
- Tire pausas, respirações, "ééé", gaguejos e retomadas, ficando com a **última** tomada certa. Uma
  frase repetida para corrigir o sentido também conta; quem decide é o sentido.
- O corte pelo som come início e final de palavras em fala rápida. **Toda emenda é conferida** com
  uma transcrição em janelas no fim de cada segmento.
- Palavra comida → proteger o trecho (manter o intervalo do bruto inteiro) e cortar de novo.
- Nunca misture tempos do bruto com os do vídeo limpo. Depois de qualquer recorte, retranscreva e
  remapeie tudo o que dependia dos tempos.
- O corte é do motor de corte (`corte/`); o estilo recebe o vídeo já limpo (`clean.mp4`).

## R6 · Legenda com o texto certo
- Corrija o transcript à mão antes de montar. Erros típicos da transcrição neste nicho:

  | Transcrição | Correto |
  |---|---|
  | Cloud | Claude |
  | A | IA |
  | Gama | Gamma |
  | carrocéis | carrosséis |
  | vim | envio |
  | Powerpoint | PowerPoint |

- Nomes de produto sempre como a marca escreve.
- Palavra-código do CTA em CAIXA ALTA.
- Guarde o original (`transcript-bruto.json`) e corrija por tempo, não por texto, quando a palavra
  se repete ("A" de "IA" × "A partir").

## R7 · Zona segura
- **Reels/Shorts orgânico:** todo texto/UI em x 90–990, y 220–1520, e nada na coluna de botões
  (x > 940 e y > 1150).
- **Anúncio:** x 65–1015, y 270–1248.
- Fundos e decoração podem sangrar.
- Confira com `ferramentas/zona-segura.py` (varredura a cada 0,25 s).

## R8 · Áudio final
- Integrado **−14 LUFS (±0,5)**, pico ≤ −0,5 dBFS, sem recodificar a imagem (`-c:v copy`).
- loudnorm em duas passadas, ou ganho + limitador quando o loudnorm linear deixar o pico em 0 dBFS.
- No zsh, use `${var}` com chaves dentro de filtros.

## R9 · Verificação antes de entregar
1. lint com 0 erros; 2. snapshot em cada beat e em cada transição; 3. rosto (R1), zona segura (R7),
texto legível e nada cortado; 4. render; 5. áudio (R8); 6. folha de quadros do final; 7. `VERIFY.md`
com duração, LUFS, o que foi protegido no corte, as correções da legenda e os pontos abertos.
**Nunca publicar nem enviar o vídeo.**

## R10 · Ambiente isolado
Os caminhos vêm de variáveis de ambiente (`WHISPER_PYTHON`, `FACE_MODEL`, `RVM_MODEL`, `CHROME`),
nunca de pastas fixas do usuário. Problemas já vistos: transcrição "terminando" sem arquivo → fixar
`av==16.1.0`; snapshot quebrando com erro do postcss → `npm ci` na raiz; pasta de cache que não
existe → criar antes de baixar.

## R11 · Perfil do apresentador
Nome, @ e avatar vêm do `perfil.json` do apresentador. O avatar pode ser um quadro do próprio vídeo,
recortado. Contagem de seguidores só se o apresentador informar. **Nenhum nome de terceiro** (outro
criador, curso ou produto que não seja do apresentador) aparece no vídeo ou nos arquivos do projeto.
