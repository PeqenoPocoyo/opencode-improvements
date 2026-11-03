# Global Instructions — Artefatos e Configurações OpenCode

## Diretório de configurações e complementos
O diretório padrão para configurações, skills e complementos do OpenCode é:
`%USERPROFILE%\.config\opencode` (equivalente a `$USERPROCESS/.config/opencode`).
Nele ficam `instructions.md`, `opencode.jsonc`, `service.json` e a pasta `skills/`.

## Artefatos inline (skill `inline-artifacts`)
Você tem a skill `inline-artifacts` disponível. Use-a **PROATIVAMENTE** (não apenas quando solicitado):

- Quando explicar um conceito, prefira um visual inline (card, diagrama, SVG) em vez de bloco de texto.
- Ao apresentar dados, comparações, fluxos, hierarquias ou status, renderize um artefato inline (card HTML, diagrama Mermaid, SVG) diretamente na mensagem.
- Quando um visual ajudar a compreensão, gere-o inline mesmo sem pedido explícito.
- Mantenha HTML inline autocontido (apenas estilos inline, sem `<script>`).
- Para conteúdo interativo/editável, recorra a `artifact-balloon` (Review pane).

**Não espere o usuário pedir "mostra visualmente" — decida autonomamente quando um visual ajuda.**

## Artefatos em Review pane (skill `artifact-balloon`)
Use `artifact-balloon` para arquivos grandes, interativos ou editáveis (HTML completo, React/TSX, PDF, imagens binárias). Não é obrigatório enviar tudo para o Review pane — fluxos simples, cards e diagramas devem ficar inline na conversa.


## Proactive AI orientation (mirrors repo instructions/SUPERPROMPT.md)
- Load `%USERPROFILE%\.config\opencode\skills` and any repo-local `skills/`.
- Route every request through `configs/skills-index.json` (id/name/description) when present.
- Select 1-3 best-fit skills, load their SKILL.md, and follow them.
- Respect hooks and security guidance before executing dangerous actions.
- Verify results before claiming completion.
- Do not claim success without evidence.

## Uso autonomo de skills sem @
- Nunca exigir tag @skill do usuario.
- A cada turno, analisar intencao + configs/skills-index.json e carregar skills proativamente.
- Se citar, deve usar na pratica.
- Hooks e instrucoes globais devem rodar sem pedido explicito.
