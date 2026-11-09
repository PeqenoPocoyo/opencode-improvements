# motion-lab — pacote para treinar modelos mais fracos a fazer motion graphics

Feito em cima do **Claude Motion + skill pack "Motion Graphics"** que você mandou (o original continua intacto; as versões corrigidas estão em `patched-existing-skills/`).

## O problema e a resposta
| Sintoma que você relatou | Causa provável | O que o pack faz |
|---|---|---|
| Todo vídeo tem a "mesma alma" | O modelo repete a paleta/fonte/easing padrão das skills | **Style DNA**: 12 presets + gerador + *ledger* (`.motion/style-history.json`) + `fingerprint.py` que mede a distância "de alma" entre vídeos. Cruzamento de DNAs (`generative-play`). |
| SFX "meio pá/estranha" | Sample solto no t=0, sem camadas, sem alinhar ao frame | **sound-design-pro**: efeitos em camadas (sub + transiente + corpo + cauda), alinhados ao frame +6 ms, paleta por DNA, mix −14 LUFS (social) ou −16 (conservador), QA numérico. |
| Timing ruim | Tempos adivinhados | Cena declara `Lab.ev(t,tipo)` → `render.mjs --events` → `sync_cues.py`. Grade de batida (`BEAT`). |
| Modelo fraco pula etapas | Nada força o processo | **Hooks** (guard-rails automáticos) + `guard.sh` manual + regras curtas + playbook + prompts prontos. |
| Pouca variedade visual | Só havia o que estava pré-definido | Fundos 3D por shader (28), arte 2D generativa (34), tipografia cinética (32 fontes), transições (43), UI em vídeo, **colagem de papel**, **personagens vetoriais**, **composição sobre filmagem real**. Tudo **sem imagens**. |
| Tarefas grandes se perdem | Contexto único | **agent-orchestration**: divide por arquivos, ≤3 sub-agentes, verifica em disco, plano B sem sub-agentes. |

## Instalação (Windows/PowerShell, passo a passo)
1. Descompacte em `C:\Users\SEU_USUARIO\Desktop\motion-lab` (ou onde quiser).
2. Instale: Node 18+, `npm i -g playwright` e `npx playwright install chromium`, ffmpeg no PATH, Python 3.9+ (`pip install numpy pillow opencv-python`).
3. **Skills:** copie `skills\*` para a pasta de skills do seu harness (no opencode: `%USERPROFILE%\.config\opencode\skills\`). Ex.: `robocopy skills "%USERPROFILE%\.config\opencode\skills" /E`
4. **Regras no prompt do modelo fraco:** cole `instructions\MOTION-LAB-RULES.md` no system prompt / AGENTS.md. É curto de propósito.
5. **Hooks:** se o harness suporta (Claude Code e compatíveis), siga `hooks\README.md` (`setx MOTION_LAB_HOME "C:\...\motion-lab"` e mesclar `settings.snippet.json`). No **Beam** sem hooks: o modelo roda `hooks/guard.sh start|scene|stills|qa` nos momentos indicados pelas regras.
6. (Opcional) Corrigir as skills originais: `python patched-existing-skills\patch_old_skills.py <pasta skills originais> --out patched` e copiar os `SKILL.md` gerados.

## Como o modelo fraco deve usar (resumo de 8 linhas)
1. Ler `CONVENTIONS.md` + `skills/motion-director/SKILL.md`.
2. Gerar **3 DNAs** (`dna_generate.py --candidates 3`), escolher **1**, salvar `dna.json`.
3. Escrever beat sheet (tempos desiguais, gancho, payoff com ≥1 s de respiro).
4. `setup.sh meu-video` e montar a cena com as runtimes (não reinventar).
5. Declarar `Lab.ev` para cada impacto/transição.
6. Renderizar **stills**, **LER as imagens**, corrigir; depois draft.
7. `sync_cues.py` (som) → `qa_video.py` → `contact_sheet.py` → `fingerprint.py`.
8. Entregar dizendo **o que foi verificado** e dando **5 timestamps** para você ouvir.

Modo "sem briefing / quero ser surpreendido": `python skills/generative-play/scripts/play_make.py --project meu-video --n 8 --seed 42`.

## Skills novas nesta versão final
- `collage-paper-texture` — recortes de papel rasgado/tesoura, fita, grampo, carimbo, letras de "ransom note", meio-tom, *boil* stop-motion, som de `paper-slap` ligado a cada pouso.
- `vector-characters` — bípede com IK (andar, correr, acenar, pular, apontar, dançar), blob com squash & stretch, robô, rosto (pisca, olha, fala), eventos de passos.
- `live-action-compositing` — para quando você manda a SUA filmagem: `prep_footage`, `track_points` (tracking planar), `grade_match`, `grain_measure`, `light_direction`, `plan_cutaways` (a partir de legenda .srt) e `render.mjs --alpha` (overlay ProRes 4444 para compor no ffmpeg).

## Limites honestos
- Nenhum modelo (nem eu) **ouve áudio**. O som é construído por receitas procedurais e checado por números; você precisa ouvir os 5 timestamps do relatório.
- O limiar do `fingerprint` (0,18) é heurístico — não tive os 11 vídeos de referência em disco ao calibrar. Ajuste depois de comparar saídas reais.
- Renderização do DOM por software ≈0,45 s/frame em 1080×1920; um draft de 12 s leva minutos.
- Tracking só planar; não há rotoscopia nem chroma key.
- Não consegui gravar direto na sua Desktop (o conector estava desconectado durante a maior parte do trabalho): o pacote vai como `.zip`.
