---
name: inline-artifacts
description: Cria artefatos inline (SVG, HTML, Mermaid, cards) diretamente na conversa do OpenCode. Use proativamente quando explicar conceitos, apresentar dados, comparacoes, fluxos, hierarquias ou status. Prioriza visuais inline a blocos de texto longos. Para conteudo interativo/editavel, use artifact-balloon (Review pane).
---

# Skill: inline-artifacts

> **Triggers (auto)**: inline artifacts, inline-artifacts

# Inline Artifacts (OpenCode)

## O que renderiza inline
- **SVG** — vector graphics, icons, charts, ilustracoes
- **HTML blocks** — cards, tables, styled divs (sanitized, no JS)
- **Mermaid** — diagrams via ```mermaid fenced blocks
- **Markdown** — tables, lists, code, callouts

## O que NAO funciona inline
- JavaScript execution (onClick, scripts) — stripped by renderer
- `contenteditable` / form inputs — not interactive inline
- External resources (CDN scripts, iframes) — blocked

Para interactive/editable content, use `artifact-balloon` (opens full HTML in Review pane).

## Regras de criatividade para inline
1. **Nunca usar o mesmo estilo duas vezes consecutivas** — variar paleta, layout, estrutura
2. **Glassmorphism por padrao**: gradiente + border semi-transparente + backdrop-filter
3. **Glow effects**: radial-gradient blur atras de icones para profundidade
4. **Animacoes CSS**: float, blink, shimmer, slide-up, hover (translateY + shadow colorida)
5. **Badges contextuais**: tags por tipo com cores tematicas
6. **Descricoes ricas**: nao apenas o path — incluir nome, descricao curta, tipo e origem
7. **Hover interativo**: card levanta (translateY) + shadow colorida ao passar o mouse
8. **Icones com drop-shadow**: emoji com filter:drop-shadow para profundidade

## Paleta contextual por tipo de artefato
| Tipo | Cor principal | Cor secundaria | Icone |
|---|---|---|---|
| HTML | #6366f1 (indigo) | #8b5cf6 (violet) | 🌐 |
| SVG | #10b981 (emerald) | #34d399 (green) | 🎨 |
| Markdown | #f59e0b (amber) | #fbbf24 (yellow) | 📝 |
| CSV | #0ea5e9 (sky) | #38bdf8 (light blue) | 📊 |
| Codigo | #8b5cf6 (violet) | #a78bfa (light violet) | 💻 |
| Imagem | #f43f5e (rose) | #fb7185 (light rose) | 🖼️ |
| PDF | #ef4444 (red) | #f87171 (light red) | 📄 |

## Regra de exibibilidade para botoes inline
- **Gerar botao inline** APENAS para arquivos que o panel pode exibir (HTML, SVG, MD, CSV, codigo)
- **Nao gerar botao** para arquivos binarios (.zip, .exe, .png, .pdf, .mp3) — apenas listar o path no balao
- Para arquivos exibiveis: link `file://` que abre no Review pane automaticamente

## Decision guide
| Need | Approach |
|---|---|
| Static visual / diagram | Inline SVG or Mermaid |
| Styled card / table | Inline HTML (divs with inline styles) |
| Editable / interactive | `artifact-balloon` → Review pane HTML |
| Large document | `md-document` skill |

## Rules
1. Never paste raw code fences for HTML/SVG — render them directly in the message.
2. Keep inline HTML self-contained (inline styles only, no `<script>`).
3. For Mermaid, use fenced ```mermaid blocks.
4. If interactivity is needed, fall back to `artifact-balloon`.
5. Baloes de artifacts ao final da resposta devem ser criativos e contextuais (ver regras acima).
6. Nunca usar o mesmo estilo de balao duas vezes consecutivas.

## Baloes de Artifacts (inline ao final da resposta)

Quando usar o Review pane, emitir um balao de artifacts ao final da resposta. Os baloes devem ser **criativos e contextuais**:

### Template de balao criativo (2+ artifacts — grid 2 colunas):
```
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;padding:20px;border-radius:20px;background:linear-gradient(135deg,#020617 0%,#0f172a 50%,#1e293b 100%);border:1px solid rgba(99,102,241,0.2);box-shadow:0 20px 60px rgba(0,0,0,0.5),inset 0 1px 0 rgba(255,255,255,0.05);font-family:system-ui;color:#e2e8f0;max-width:560px;">
  <!-- Header com icone animado + indicadores de status -->
  <!-- Cards com glassmorphism, glow radial, badges contextuais, hover 3D -->
  <!-- Descricoes ricas com nome + descricao + tipo + origem -->
</div>
```

### Template de balao criativo (1 artifact — card unico):
```
<div style="display:flex;flex-direction:column;gap:10px;padding:16px;border-radius:16px;background:linear-gradient(135deg,#0f172a,#1e293b);border:1px solid rgba(99,102,241,0.2);box-shadow:0 8px 32px rgba(0,0,0,0.3);font-family:system-ui;color:#e2e8f0;max-width:420px;">
  <!-- Icone grande + nome + descricao + badge + botao abrir -->
</div>
```

### Animacoes CSS obrigatorias:
- `@keyframes float` — icone flutua (translateY 0 → -4px → 0)
- `@keyframes blink` — indicadores de status (opacity 1 → 0.3 → 1)
- `@keyframes slideUp` — cards entram com fade + translateY
- Hover: `transform: translateY(-2px to -4px)` + `box-shadow` colorida

### Anti-Padroes para baloes:
- Balao generico sem contexto (mesmo estilo sempre)
- Card simples de 5 linhas sem glassmorphism/glow
- Responder com 3 paragrafos de texto quando diagrama inline resolve
- HTML completo com `<script>` inline na conversa

## Companion skills
- `artifact-balloon` — for interactive/editable HTML in Review pane
- `web-artifacts-builder` — for React/TSX bundles
- `md-document` — for long-form markdown → HTML

---
name: inline-artifacts
description: Cria artefatos inline (SVG, HTML, Mermaid, cards) diretamente na conversa do OpenCode. Use proativamente quando explicar conceitos, apresentar dados, comparacoes, fluxos, hierarquias ou status. Prioriza visuais inline a blocos de texto longos. Para conteudo interativo/editavel, use artifact-balloon (Review pane). Baloes de artifacts devem ser criativos e contextuais (glassmorphism, glow, animacoes). Botoes inline apenas para arquivos exibiveis pelo panel.
version: 2.0
improved: true
improved_at: "2026-10-28T00:00:00Z"
improved_by: "agent"
test_passed: true
test_scenario: "Balao criativo com glassmorphism, glow, animacoes CSS, hover 3D, badges contextuais, regra de exibibilidade para botoes inline"
---

Base directory for this skill: C:\Users\drici\.config\opencode\skills\inline-artifacts
Relative paths in this skill (e.g., scripts/, reference/) are relative to this base directory.

> **Skill Evolver**: score 70/100 · evoluída em 2026-10-31T02:34:06.147989+00:00Z · versão evolver-1.0
