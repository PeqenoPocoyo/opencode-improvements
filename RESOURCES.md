# Pacote de Recursos Funcionais (OpenCode)

Este diretório reúne os motores e skills que estendem o OpenCode com capacidades de criação de vídeo, imagem e áudio — tudo rodando localmente ou por camadas gratuitas, sem provedores pagos.

## Estrutura

| Pasta | O que é | O que produz |
|---|---|---|
| `toolkit-claude-motion/` | Engine procedural de vídeo: Remotion + motor de som `sfx` (Python stdlib) + contact-sheet review loop. Fonte: `claude-motion` (repo separado) | Vídeos 100% gerados a partir de código, do zero (timeline JSON → cena → render → mux → contact sheets). Exemplo: `02-juizo-final` |
| `skill-pack-motion-graphics/` | Skill pack `Barty-Bart/motion-graphics` (MIT): edição de vídeo real, separação de objetos (SAM 2.1), sound pass com samples CC0. | Vídeos de footage real, B-roll, motion graphics, promo, thumbnails. |

## Como os dois se completam

- **claude-motion** é o lado *criativo*: você escreve o vídeo inteiro em código (timeline, cenas, som) e renderiza um MP4. Bom para peças de abertura, títulos, explicativos abstratos.
- **motion-graphics** é o lado *editorial*: você pega um vídeo/gravação real e adiciona motion graphics sobre ele (B-roll sincronizado com áudio, separação de pessoa/produto, sound pass real).

**Exemplo de uso em série:** `claude-motion` produz o título/abertura (como o Juízo Final) → `motion-graphics` coloca isso sobre o produto real (como a loja de roupa).

## Fluxo de entrega padrão (do `claude-motion` AGENTS.md)

1. Acorda tema, formato e hero moment com o usuário.
2. Escreve `timeline-<nome>.json` (storyboard em números, um arquivo por vídeo).
3. Cria componentes de cena em `src/<video>/`, reusa primitivas (`Mask`, `Roll`, `Spark`, `Grain`).
4. Registra `<Composition>` em `src/Root.tsx`.
5. Roda o **review loop**: contact sheets em cada beat → corrige gaps de frame → ajusta timing.
6. Escreve cue sheet `sfx/cues/<nome>.py` no mesmo timeline; renderiza som (-14 LUFS).
7. Render, muxa, checa loudness (`-16 LUFS` para o motion-graphics / `-14 LUFS` para o claude-motion).
8. Adiciona a peça a `examples/` com README: prompt, processo, specs.

## Exemplos entregues

- `toolkit-claude-motion/02-juizo-final` — peça apocalíptica 10s, 1080×1080, 60 fps, som procedural, −14.1 LUFS.
- `toolkit-claude-motion/03-loja-promocao` — promo de loja de roupa 9:16, 15s, 128 BPM, cabide de partículas, tag com cursor clicando tamanho (em render quando você solicitou o sync).

## Repositórios originais

- `claude-motion`: `C:\Users\drici\Documents\claude-motion` (seu próprio repo, motor procedural)
- `motion-graphics`: `C:\Users\drici\Documents\motion-graphics` (clone de Barty-Bart/motion-graphics, MIT)

## Como instalar os skills do motion-graphics no seu OpenCode

```powershell
npx skills add Barty-Bart/motion-graphics
# ou copie as pastas em skill-pack-motion-graphics/skills/ para ~/.config/opencode/skills/
```

## Segurança

- Todo o `skill-pack-motion-graphics` foi auditado (não há patterns de exfiltração, curl|bash hardcoded, ou segredos).
- As chaves de API (BFL, Hugging Face, OpenRouter) ficam **apenas** em `~/.config/opencode/api-keys.json` (§6.3 do AGENTS.md) — nunca commitem.
