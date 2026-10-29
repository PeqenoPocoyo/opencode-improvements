---
name: artifact-balloon
description: Renderiza artifacts (HTML, SVG, React, Mermaid, CSV, Markdown) como balões clicáveis empilhados ao FIM da resposta do assistente, em vez de inline no meio do texto. Cada balão abre o arquivo no Review pane (browser.preview). Registra a skill que gerou o artifact. Use quando o agente produzir código/arquivo visualizável e você não quiser quebrar o fluxo da conversa.
---

# Artifact Balloon

## Princípio

- **Nunca** renderizar o artifact inline no meio do texto da conversa (causa quebra de layout e "bug" visual).
- Ao final da resposta, anexar um **stack vertical** de balões clicáveis, um por arquivo visualizável.
- Clicar no balão abre o arquivo no **Review pane** via `browser.preview`.
- Cada balão exibe: ícone do tipo, título, skill de origem, tamanho.
- Se houver mais de 1, empilhar verticalmente (stack).

## Fluxo

1. O agente gera a resposta contendo blocos fenced (```html, ```svg, ```jsx, ```mermaid, ```csv, ```md).
2. Antes de exibir, rodar `extractArtifacts(responseText, skill)`:
   - Detecta blocos visualizáveis.
   - Salva cada um em arquivo temporário (server-local).
   - Retorna lista de `Artifact`.
3. Opcionalmente, rodar `stripVisualBlocks(responseText)` para substituir o bloco por um placeholder curto no texto.
4. Renderizar o texto (markdown) normalmente.
5. Ao final, renderizar `<ArtifactStack artifacts={artifacts} onOpen={openInReviewPane} />`.

## Integração com o Review pane

```ts
function openInReviewPane(a: Artifact) {
  // chama a ferramenta browser.preview com o path server-local
  tools.browser.preview({ path: a.path });
}
```

## Vínculo com a skill de origem

- Sempre passe o nome da skill que gerou o conteúdo para `extractArtifacts(text, skill)`.
- O balão exibe "via {skill}" para rastreabilidade.
- Se a resposta não veio de uma skill específica, omitir (skill = undefined).

## Tipos suportados

| Lang fenced | Kind | Extensão |
|-------------|------|----------|
| html, htm   | html | .html |
| svg         | svg  | .svg |
| jsx, tsx, react, vue | react | .jsx |
| md, markdown | markdown | .md |
| mermaid     | mermaid | .mmd |
| csv, tsv    | csv  | .csv |

## O que NÃO fazer

- Não renderizar `<iframe>` inline no meio do markdown.
- Não colar o código completo da resposta no chat quando for visualizável.
- Não criar um balão por parágrafo — apenas por arquivo/bloco visualizável.
- Não esquecer de empilhar quando houver múltiplos.