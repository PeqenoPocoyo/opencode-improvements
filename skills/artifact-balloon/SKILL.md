---
name: artifact-balloon
description: Salva arquivos grandes/interativos/editaveis em arquivo temporario e abre no Review pane via browser.preview. Ao final da resposta, emite um balao inline com card por arquivo. Baloes devem ser criativos e contextuais (glassmorphism, glow, animacoes, badges tematicos). Botoes inline apenas para arquivos exibiveis pelo panel. Use para HTML completo com JS, React/TSX, PDF, imagens, audio.
---

# Skill: artifact-balloon

# Artifact Balloon (OpenCode)

## Objetivo
Manter o fluxo do chat leve. Artefatos simples (fluxos, cards, diagramas estaticos) devem ser renderizados inline na conversa. Arquivos grandes, interativos ou editaveis sao salvos em arquivo temporario e abertos no Review pane via `browser.preview`. Ao final da resposta, emite um bloco "Artifacts" com um card por arquivo do Review pane (empilhados), contendo o caminho e a skill de origem.

## Regra de ouro
- **Prefira render inline** (direto na conversa) para fluxos simples, cards, diagramas estaticos, tabelas e esquemas visuais que ajudem a compreensao imediata.
- Use o **Review pane (artifact-balloon)** para arquivos grandes, interativos ou editaveis (HTML completo com JS, React/TSX, PDF, imagens binarias) ou quando o usuario pedir explicitamente para abrir em tela cheia.
- **SEMPRE chamar `browser.preview()` automaticamente** apos salvar o arquivo. Nao esperar o usuario pedir.
- Quando usar o Review pane, coloque o resumo de artifacts **ao final** da resposta.
- Se houver mais de 1 arquivo no Review pane, empilhe (um por linha).

## Baloes criativos e contextuais (OBRIGATORIO)

Os baloes de artifacts ao final da resposta devem ser **criativos e contextuais**, nao genericos. Cada balao deve ter identidade visual propria.

### Regras de criatividade para baloes:
1. **Paleta contextual**: cores variam por tipo de artefato (HTML=indigo, SVG=emerald, MD=amber, CSV=sky, codigo=violet, imagem=rose, PDF=red)
2. **Layout dinamico**: usar grid (2 colunas) quando houver 2+ artifacts, card unico quando 1
3. **Animacoes CSS**: float (icone), blink (indicadores), shimmer (CTA), slide-up (cards), hover (translateY + shadow colorida)
4. **Glassmorphism**: background com gradiente + border semi-transparente + backdrop-filter
5. **Glow effects**: radial-gradient blur atras dos icones para profundidade
6. **Badges contextuais**: tags por tipo (HTML, Interativo, Criativo, Pesado) com cores tematicas
7. **Descricoes ricas**: nome + descricao curta + tipo + origem (nao apenas o path)
8. **Hover interativo**: card levanta (translateY) + shadow colorida ao passar o mouse
9. **Icones com drop-shadow**: emoji com filter:drop-shadow para profundidade
10. **Indicadores de status**: dots animados (blink) para mostrar que esta ativo

### Template de balao criativo (2+ artifacts — grid 2 colunas):
Usar glassmorphism, glow radial, badges contextuais, hover 3D, descricoes ricas, animacoes CSS.

### Template de balao criativo (1 artifact — card unico):
Card com icone grande, nome, descricao, badge de tipo, botao de abrir com shimmer.

### Anti-Padroes para baloes:
- Balao generico sem contexto (mesmo estilo sempre)
- Card simples de 5 linhas sem glassmorphism/glow
- Responder com 3 paragrafos de texto quando diagrama inline resolve
- HTML completo com `<script>` inline na conversa

## Regra de exibibilidade para botoes inline
- **Gerar botao inline** APENAS para arquivos que o panel pode exibir (HTML, SVG, MD, CSV, codigo)
- **Nao gerar botao** para arquivos binarios (.zip, .exe, .png, .pdf, .mp3) — apenas listar o path no balao
- Para arquivos exibiveis: link `file://` que abre no Review pane automaticamente

## Fluxo obrigatorio

### 1. Detectar blocos/arquivos visualizaveis
**Qualquer arquivo que o Review pane do OpenCode consiga exibir** vira artifact — nao apenas os "visualizaveis" classicos.
Exemplos: `html`, `htm`, `svg`, `jsx`, `tsx`, `react`, `vue`, `svelte`, `md`, `markdown`, `mermaid`, `csv`, `tsv`, codigo (js/ts/py/go/rs/java/c/cpp/cs/php/sh/sql/json/yaml/xml/toml/ini/log/diff/txt), imagens (png/jpg/gif/webp), `pdf`, audio (mp3/wav/ogg/m4a/flac) e qualquer outra extensao que o panel consiga renderizar/exibir.
Se o tipo nao estiver mapeado mas o panel exibir, trate como `file` (extensao original preservada).

### 2. Salvar em arquivo
Use o script helper (ou write tool) para salvar em `os.tmpdir()/opencode-artifacts/`:
```
node C:\Users\drici\.config\opencode\scripts\save-artifact.js <lang> <skill> <<'EOF'
...conteudo...
EOF
```
O script imprime o path absoluto (server-local).

### 3. Abrir no Review pane
Para cada artifact salvo, chamar:
```
browser.preview({ path: "<path impresso>" })
```

### 4. Emitir o balao ao final da resposta
O script imprime `BALLOON=<html>`. Cole esse HTML inline na resposta (o OpenCode renderiza HTML inline). Cada balao e um `<a href="file:///...">` que abre o Review pane ao clicar.

Use o icone correspondente ao tipo:
| kind | icone |
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
| file (generico) | 📎 |

### 5. Vinculo com a skill
- Sempre informar a skill de origem no balao ("via {skill}").
- Se nao houver skill especifica, omitir.

## O que NAO fazer
- Nao colar codigo completo de artifact **no meio do texto** quando o conteudo for longo, interativo ou exija leitura em tela cheia — use o Review pane nesses casos.
- Nao renderizar `<iframe>` inline.
- Nao criar balao para arquivos que o panel nao consiga exibir (binarios arbitrarios como .zip/.exe/.dll, etc.).
- Para arquivos binarios (imagens, pdf, audio), nao passar pelo script (que e texto/utf8): copiar/salvar o binario no diretorio de artifacts e gerar o balao manualmente (HTML `<a href="file:///...">`).
- Nao esquecer de empilhar quando houver multiplos no Review pane.
- Nao usar balao generico sem contexto — sempre aplicar as regras de criatividade.

## Exemplo de balao criativo

Resposta do agente:
> Aqui esta o dashboard solicitado. Gerei um HTML com grafico e uma tabela CSV.

> ---
> [Balao criativo com glassmorphism, glow, animacoes, badges contextuais]
> ---

---
name: artifact-balloon
description: Salva arquivos grandes/interativos/editaveis em arquivo temporario e abre no Review pane via browser.preview. Ao final da resposta, emite um balao inline com card por arquivo. Baloes devem ser criativos e contextuais (glassmorphism, glow, animacoes, badges tematicos). Botoes inline apenas para arquivos exibiveis pelo panel. Use para HTML completo com JS, React/TSX, PDF, imagens, audio.
version: 2.0
improved: true
improved_at: "2026-10-28T00:00:00Z"
improved_by: "agent"
test_passed: true
test_scenario: "Balao criativo com glassmorphism, glow, animacoes CSS, hover 3D, badges contextuais, regra de exibibilidade para botoes inline"
---

Base directory for this skill: C:\Users\drici\.config\opencode\skills\artifact-balloon
Relative paths in this skill (e.g., scripts/, reference/) are relative to this base directory.