---
name: artifacts-feature
description: Detecta blocos de código visualizáveis na resposta do assistente e converte-os em Artifact (balão clicável) que abre no Review pane. Usa artifact-detector.ts para detectar blocos fenced e ArtifactBalloon.tsx para renderizar balões clicáveis. Empilha múltiplos artifacts verticalmente. Vincula à skill de origem. Use quando gerar respostas com blocos de código visualizáveis (HTML, SVG, React, etc.).
---

# Skill: artifacts-feature

# Artifact Feature — Detector & Balloon

## Objetivo
Detectar, na resposta do assistente, blocos de código/arquivos que podem ser
visualizados no Review pane e convertê-los em Artifact (balão clicável).

## Regras
- Não renderiza inline no meio do texto (evita quebrar o fluxo).
- Retorna a lista de artifacts para ser empilhada ao FIM da resposta.
- Cada artifact registra a skill que o gerou (quando informada).
- Balões devem ser criativos e contextuais (glassmorphism, glow, animações, badges temáticos).
- Botões inline apenas para arquivos exibíveis pelo panel.

## Componentes

### artifact-detector.ts
Detector de blocos de código fenced na resposta. Identifica linguagens visualizáveis
(html, svg, jsx, tsx, md, mermaid, csv, etc.) e salva em arquivo temporário
(server-local) para que o Review pane possa abri-los via browser.preview.

### ArtifactBalloon.tsx
Componente React de "balão" clicável que aparece ao FIM da resposta.
Múltiplos artifacts empilham-se verticalmente (stack).
Inclui: ícone por tipo, título, label, skill de origem, tamanho, botão de abrir.

## Linguagens visualizáveis
| Lang | Kind | Extensão |
|---|---|---|
| html, htm | html | .html |
| svg | svg | .svg |
| jsx, tsx, react, vue | react | .jsx |
| md, markdown | markdown | .md |
| mermaid | mermaid | .mmd |
| csv, tsv | csv | .csv |
| (outros) | code | .txt |

## Fluxo de uso
1. Assistente gera resposta com blocos de código fenced
2. `detectBlocks()` identifica blocos visualizáveis
3. `extractArtifacts()` salva cada bloco em arquivo temporário
4. `ArtifactStack` renderiza balões clicáveis ao fim da resposta
5. Usuário clica no balão → abre no Review pane via browser.preview

## Balões criativos (OBRIGATÓRIO)
Os balões devem ser criativos e contextuais:
1. Paleta contextual por tipo (HTML=indigo, SVG=emerald, MD=amber, CSV=sky, código=violet)
2. Layout dinâmico: grid 2 colunas para 2+ artifacts, card único para 1
3. Animações CSS: float, blink, shimmer, slide-up, hover (translateY + shadow colorida)
4. Glassmorphism: gradiente + border semi-transparente + backdrop-filter
5. Glow effects: radial-gradient blur atrás dos ícones
6. Badges contextuais: tags por tipo com cores temáticas
7. Descrições ricas: nome + descrição curta + tipo + origem
8. Hover interativo: card levanta + shadow colorida

## Regra de exibibilidade para botões inline
- Gerar botão inline APENAS para arquivos que o panel pode exibir (HTML, SVG, MD, CSV, código)
- Não gerar botão para binários (.zip, .exe, .png, .pdf, .mp3) — apenas listar o path

## Anti-Padrões
- Não renderizar `<iframe>` inline
- Não criar balão para arquivos que o panel não consiga exibir
- Não esquecer de empilhar quando houver múltiplos no Review pane
- Não usar balão genérico sem contexto

## Metadata
- **Categoria**: Design/Artefatos
- **Prioridade**: Alta
- **Aplicável a**: HTML, React, TypeScript, qualquer framework
- **Dependências**: artifact-balloon, inline-artifacts, artifact-creator
- **Versão**: 1.0
- **Melhorado**: 2026-10-28 (balões criativos, regra de exibibilidade)