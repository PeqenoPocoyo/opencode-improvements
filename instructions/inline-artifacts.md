# Instrucao: Artefatos Inline e Review Pane

> Define quando usar artefatos inline (na conversa) vs Review pane (arquivo).
> Baseado nas regras globais do OpenCode do dispositivo Cesar.

## REGRA AUTOMATICA: Abrir no Review Pane

**SEMPRE que gerar um artefato (HTML, SVG, MD, CSV, codigo, etc.), chamar `browser.preview()` automaticamente.**

- Nao esperar o usuario pedir "abre no panel" ou "mostra no review pane".
- Apos salvar o arquivo, chamar `browser.preview({ path: "<caminho>" })` imediatamente.
- Isso vale para QUALQUER artefato gerado, seja inline ou em arquivo.
- A unica excecao: artefatos inline muito simples (cards de 3-4 linhas, SVG pequeno) que cabem na conversa.

### Fluxo obrigatorio:
1. Gerar o conteudo do artefato
2. Salvar em arquivo (write tool ou save-artifact.js)
3. Chamar `browser.preview({ path: "<caminho>" })` IMEDIATAMENTE
4. Emitir balao de artifacts ao final da resposta

### O que NAO fazer:
- Gerar artefato e apenas listar o path sem abrir no panel
- Esperar o usuario pedir para abrir no panel
- Abrir no panel apenas "se necessario"

## Artefatos Inline (skill `inline-artifacts`)

Use **PROATIVAMENTE** (nao apenas quando solicitado):

- Quando explicar um conceito, prefira um visual inline (card, diagrama, SVG) em vez de bloco de texto.
- Ao apresentar dados, comparacoes, fluxos, hierarquias ou status, renderize um artefato inline (card HTML, diagrama Mermaid, SVG) diretamente na mensagem.
- Quando um visual ajudar a compreensao, gere-o inline mesmo sem pedido explicito.
- Mantenha HTML inline autocontido (apenas estilos inline, sem `<script>`).
- Para conteudo interativo/editavel, recorra a `artifact-balloon` (Review pane).

**Nao espere o usuario pedir "mostra visualmente" — decida autonomamente quando um visual ajuda.**

## Artefatos em Review Pane (skill `artifact-balloon`)

Use `artifact-balloon` para arquivos grandes, interativos ou editaveis (HTML completo com JS, React/TSX, PDF, imagens binarias) ou quando o usuario pedir explicitamente para abrir em tela cheia.

Nao e obrigatorio enviar tudo para o Review pane — fluxos simples, cards e diagramas devem ficar inline na conversa.

## Regra de Decisao

| Situacao | Onde renderizar |
|---|---|
| Conceito simples, comparacao curta, status | Inline (card/SVG/Mermaid) |
| Dashboard interativo, simulador, formulario | Review pane (arquivo HTML) |
| Dados tabulares extensos | Inline (tabela) ou Review pane (se > 20 linhas) |
| Diagrama de fluxo/arquitetura | Inline (Mermaid) |
| Artefato editavel pelo usuario | Review pane |

## Baloes de Artifacts (inline ao final da resposta)

Quando usar o Review pane, emitir um balao de artifacts ao final da resposta. Os baloes devem ser **criativos e contextuais**, nao genericos:

### Regras de criatividade para baloes:
1. **Paleta contextual**: cores variam por tipo de artefato (HTML=indigo, SVG=emerald, MD=amber, CSV=sky, codigo=violet, imagem=rose)
2. **Layout dinamico**: usar grid (2 colunas) quando houver 2+ artifacts, lista vertical para 1
3. **Animacoes CSS**: float (icone), blink (indicadores de status), shimmer (CTA), slide-up (cards), hover (translateY + shadow colorida)
4. **Glassmorphism**: background com gradiente + border semi-transparente + backdrop-filter
5. **Glow effects**: radial-gradient blur atras dos icones para profundidade
6. **Badges contextuais**: tags por tipo (HTML, Interativo, Criativo, Pesado) com cores tematicas
7. **Descricoes ricas**: nao apenas o path — incluir nome, descricao curta, tipo e origem
8. **Hover interativo**: card levanta (translateY) + shadow colorida ao passar o mouse
9. **Icones com drop-shadow**: emoji com filter:drop-shadow para profundidade
10. **Indicadores de status**: dots animados (blink) para mostrar que esta ativo

### Regra de exibibilidade para botoes inline:
- **Gerar botao inline** APENAS para arquivos que o panel pode exibir (HTML, SVG, MD, CSV, codigo)
- **Nao gerar botao** para arquivos binarios (.zip, .exe, .png, .pdf, .mp3, etc.) — apenas listar o path no balao
- Para arquivos exibiveis: link `file://` que abre no Review pane automaticamente

## Anti-Padroes

- Nao enviar card simples de 5 linhas para o Review pane
- Nao responder com 3 paragrafos de texto quando um diagrama inline resolve
- Nao gerar HTML completo com `<script>` inline na conversa (usar Review pane)
- Nao usar balao generico sem contexto (sempre o mesmo estilo, sem cores/icones tematicos)
- Nao gerar artefato e apenas listar o path sem abrir no panel

## Metadata

- **Tipo**: Instrucao
- **Prioridade**: Alta
- **Aplicavel a**: Todos os artefatos e respostas visuais
- **Dependencias**: artifact-generation, artifact-creator, inline-artifacts, artifact-balloon
- **Melhorado**: 2026-10-29 (auto-abertura no Review pane, baloes criativos, regra de exibibilidade)