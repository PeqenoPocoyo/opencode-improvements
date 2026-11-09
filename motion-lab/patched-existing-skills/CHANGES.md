# patched-existing-skills — o que mudou nas skills ORIGINAIS

Cópias corrigidas (só os `SKILL.md`; as pastas de assets/engine/sfx originais continuam onde estão).
Geradas por `patch_old_skills.py` (não destrutivo, reexecutável).

## Problemas encontrados nas originais → correção
| Problema | Efeito nos modelos fracos | Correção |
|---|---|---|
| Paleta padrão fixa (`#F7F7F8`, `#0C0C0E`, `#FF4F1A`...) | Todo vídeo sai com a mesma cor = "mesma alma" | Rebaixada a **ÚLTIMO RECURSO**; cores vêm de `dna.json` ou da marca |
| "Inter/Geist por padrão" | Mesma tipografia sempre | Fonte vem do DNA (`kinetic-typography/fonts`, embutidas — Google Fonts é bloqueado no sandbox) |
| Sem gate de conceito/variedade | O modelo pula direto para código | **OVERLAY**: DNA gate → ≥3 eixos diferentes do vídeo anterior → fingerprint |
| Helpers escritos à mão em cada vídeo | Easing/loops inconsistentes, bugs de seek | Usar `scene-runtime` (Lab, FX, Type, UI, Art, Bg3D, Trans) |
| `sound-effects`: "Nunca sintetize som" + só samples | SFX "meio pá" quando o sample não casa; sem alternativa | **Regra híbrida**: camadas procedurais (`sound-design-pro`) + samples CC0 onde servem melhor |
| Cues em tempo float arbitrário | Som defasado do frame | Âncora = fronteira de frame + 6 ms; whoosh PICA no corte; riser TERMINA no hit |
| Tempos de corte "adivinhados" do vídeo | Timing ruim | `Lab.ev(t,type)` na cena → `render.mjs --events` → `sync_cues.py` |
| Perfil de loudness único (−16 LUFS / −4 dBTP) | Baixo para social | `--profile conservative` (original) ou `--profile social` (−14 / −1 dBTP) |
| Sem QA | O modelo diz "ficou ótimo" sem olhar | Ritual: lint → stills (LER) → draft → qa_video → contact sheet (LER) → fingerprint; máx. 3 passes |
| Nada sobre grandes jobs | Modelo tenta tudo em um só contexto | `agent-orchestration` |

## Mantido de propósito
Regras de crédito/licença (Vox, CC0), estrutura de cenas, durações-alvo e as regras de legibilidade das originais.

## Como instalar
```bash
python3 patch_old_skills.py <skill-pack-motion-graphics/skills> --out patched
cp -r patched/*/SKILL.md ...   # por skill: copie cada SKILL.md sobre o original
```
`object-separation` não foi alterada (não tinha conflito).
