---
name: artifact-balloon
description: Quando o assistente gera um arquivo visualizável (HTML, SVG, React/JSX, Mermaid, CSV, Markdown), pode render inline quando for fluxo simples/card/diagrama estático, ou salvar em arquivo temporário e abrir no Review pane via browser.preview para arquivos grandes/interativos/editáveis. Ao final da resposta, emite um "balão" (card clicável) empilhado listando os arquivos do Review pane. Use sempre que produzir código/arquivo visualizável.
---

# Artifact Balloon (OpenCode)

## Objetivo
Manter o fluxo do chat leve. Artefatos simples (fluxos, cards, diagramas estáticos) devem ser renderizados inline na conversa. Arquivos grandes, interativos ou editáveis são salvos em arquivo temporário e abertos no Review pane via `browser.preview`. Ao final da resposta, emite um bloco "📎 Artifacts" com um card por arquivo do Review pane (empilhados), contendo o caminho e a skill de origem.

## Regra de ouro
- **Prefira render inline** (direto na conversa) para fluxos simples, cards, diagramas estáticos, tabelas e esquemas visuais que ajudem a compreensão imediata.
- Use o **Review pane (artifact-balloon)** para arquivos grandes, interativos ou editáveis (HTML completo com JS, React/TSX, PDF, imagens binárias) ou quando o usuário pedir explicitamente para abrir em tela cheia.
- Quando usar o Review pane, coloque o resumo de artifacts **ao final** da resposta.
- Se houver mais de 1 arquivo no Review pane, empilhe (um por linha).

## Fluxo obrigatório

### 1. Detectar blocos/arquivos visualizáveis
**Qualquer arquivo que o Review pane do OpenCode consiga exibir** vira artifact — não apenas os "visualizáveis" clássicos.
Exemplos: `html`, `htm`, `svg`, `jsx`, `tsx`, `react`, `vue`, `svelte`, `md`, `markdown`, `mermaid`, `csv`, `tsv`, código (js/ts/py/go/rs/java/c/cpp/cs/php/sh/sql/json/yaml/xml/toml/ini/log/diff/txt), imagens (png/jpg/gif/webp), `pdf`, áudio (mp3/wav/ogg/m4a/flac) e qualquer outra extensão que o panel consiga renderizar/exibir.
Se o tipo não estiver mapeado mas o panel exibir, trate como `file` (extensão original preservada).

### 2. Salvar em arquivo
Use o script helper (ou write tool) para salvar em `os.tmpdir()/opencode-artifacts/`:
```
node C:\Users\drici\.config\opencode\scripts\save-artifact.js <lang> <skill> <<'EOF'
...conteúdo...
EOF
```
O script imprime o path absoluto (server-local).

### 3. Abrir no Review pane
Para cada artifact salvo, chamar:
```
browser.preview({ path: "<path impresso>" })
```

### 4. Emitir o balão ao final da resposta
O script imprime `BALLOON=<html>`. Cole esse HTML inline na resposta (o OpenCode renderiza HTML inline). Cada balão é um `<a href="file:///...">` que abre o Review pane ao clicar.

Exemplo de saída do script:
```
PATH=C:\...\artifact-xxx.html
KIND=html
SKILL=web-artifacts-builder
SIZE=1234
BALLOON=<a href="file:///C:/.../artifact-xxx.html" style="...">🌐 Visualização HTML ... ↗</a>
```

Cole o valor de `BALLOON` diretamente na resposta. Para múltiplos artifacts, cole cada `BALLOON` em uma linha separada (empilham verticalmente).

Use o ícone correspondente ao tipo:
| kind | ícone |
|------|-------|
| html | 🌐 |
| svg  | 🎨 |
| react/jsx | ⚛️ |
| markdown | 📝 |
| mermaid | 🔀 |
| csv | 📊 |
| code | 💻 |
| image | 🖼️ |
| pdf | 📄 |
| audio | 🔊 |
| file (genérico) | 📎 |

### 5. Vínculo com a skill
- Sempre informar a skill de origem no balão ("via {skill}").
- Se não houver skill específica, omitir.

## O que NÃO fazer
- Não colar código completo de artifact **no meio do texto** quando o conteúdo for longo, interativo ou exija leitura em tela cheia — use o Review pane nesses casos.
- Não renderizar `<iframe>` inline.
- Não criar balão para arquivos que o panel não consiga exibir (binários arbitrários como .zip/.exe/.dll, etc.).
- Para arquivos binários (imagens, pdf, áudio), não passar pelo script (que é texto/utf8): copiar/salvar o binário no diretório de artifacts e gerar o balão manualmente (HTML `<a href="file:///...">`).
- Não esquecer de empilhar quando houver múltiplos no Review pane.

## Exemplo

Resposta do agente:
> Aqui está o dashboard solicitado. Gerei um HTML com gráfico e uma tabela CSV.

> ---
> 📎 **Artifacts gerados** (via web-artifacts-builder)
> - 🌐 **Visualização HTML** — `C:\Users\...\opencode-artifacts\artifact-abc.html`
> - 📊 **Tabela CSV** — `C:\Users\...\opencode-artifacts\artifact-def.csv`
> ---