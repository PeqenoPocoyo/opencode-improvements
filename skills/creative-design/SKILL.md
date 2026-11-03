---
name: creative-design
description: Evita padrões repetitivos e templates genéricos. Cada artefato deve ter identidade visual própria. Use quando criar interfaces, dashboards, landing pages, ou qualquer artefato visual.
improved: true
improved_at: "2026-10-28T00:00:00Z"
improved_by: "agent"
test_passed: true
test_scenario: "Criar 3 artefatos diferentes e verificar que nenhum compartilha o mesmo layout base"
---

# Creative Design — Skill

> **Triggers (auto)**: creative design, creative-design

## Princípio Central
**Nunca repetir o mesmo padrão de layout** entre artefatos diferentes, a menos que o usuário peça.

## Anti-Padrões (EVITAR)

### ❌ Dashboard Template Genérico
- Grid 3x3 de cards brancos
- Sidebar esquerda + conteúdo principal
- Topbar com logo + busca + avatar
- Cores: azul primário, cinza secundário, branco fundo

### ❌ Layout "Copia do Anterior"
- Mesma estrutura de tabs
- Mesma paleta de cores
- Mesmos componentes (cards, tabelas, botões)
- Mesma tipografia

### ❌ Elementos Decorativos Mortos
- Gradientes que não servem a propósito
- Animações sem significado
- Ícones genéricos sem contexto

## Padrões Criativos (BUSCAR)

### ✅ Identidade Visual Única
- Cada artefato tem sua própria paleta
- Cada artefato tem sua própria tipografia
- Cada artefato tem sua própria estrutura de layout

### ✅ Formas Não-Retangulares
- Clip-path, border-radius orgânico
- Formas geométricas (hexágonos, círculos, triângulos)
- Layouts assimétricos

### ✅ Animações com Propósito
- Transições que guiam o olhar
- Feedback visual em interações
- Micro-animações que comunicam estado

### ✅ Efeitos Reativos
- Glow que segue o mouse
- Tilt 3D em cards
- Parallax no scroll
- Partículas/canvas animado

### ✅ Tipografia Expressiva
- Headlines grandes e ousadas
- Mix de pesos (thin + black)
- Texto como elemento gráfico

## Paletas Sugeridas (rotacionar)

1. **Cyan/Violet** — tech, futurista
2. **Amber/Red** — industrial, elétrico
3. **Green/Teal** — natureza, orgânico
4. **Pink/Orange** — criativo, vibrante
5. **Monochrome** — minimalista, elegante
6. **Dark + Neon** — gamer, cyberpunk

## Estruturas de Layout (rotacionar)

1. **Hero + Scroll** — página única com seções
2. **Canvas + Overlay** — visualização principal + HUD
3. **Split Screen** — dois painéis lado a lado
4. **Masonry** — grid assimétrico
5. **Radial** — elementos em círculo
6. **Timeline** — vertical ou horizontal
7. **Card Stack** — cartões empilhados com profundidade

## Checklist de Criatividade

Antes de entregar, verificar:
- [ ] Este layout é diferente do anterior?
- [ ] A paleta é diferente do anterior?
- [ ] Há pelo menos um elemento "surpresa" (animação, efeito, forma)?
- [ ] O usuário diria "isso é criativo" e não "isso é um template"?
- [ ] Existe pelo menos um efeito reativo ao mouse/scroll?

## Teste de Reinterpretação

### Cenário: Três Artefatos
```
DADO três artefatos criados em sequência
QUANDO comparados lado a lado
ENTÃO nenhum deve compartilhar o mesmo layout base
E nenhum deve usar a mesma paleta de cores
E pelo menos um deve ter animação reativa
SE dois forem visualmente similares → FAIL
```

## Balões de Artifacts (Criatividade Obrigatória)

Os balões de artifacts ao final da resposta devem ser **criativos e contextuais**:

### Regras de criatividade para balões:
1. **Paleta contextual**: cores variam por tipo (HTML=indigo, SVG=emerald, MD=amber, CSV=sky, código=violet)
2. **Layout dinâmico**: grid 2 colunas para 2+ artifacts, card único para 1
3. **Animações CSS**: float, blink, shimmer, slide-up, hover (translateY + shadow colorida)
4. **Glassmorphism**: gradiente + border semi-transparente + backdrop-filter
5. **Glow effects**: radial-gradient blur atrás dos ícones
6. **Badges contextuais**: tags por tipo com cores temáticas
7. **Descrições ricas**: nome + descrição curta + tipo + origem
8. **Hover interativo**: card levanta + shadow colorida

### Regra de exibibilidade para botões inline:
- Gerar botão inline APENAS para arquivos que o panel pode exibir (HTML, SVG, MD, CSV, código)
- Não gerar botão para binários (.zip, .exe, .png, .pdf, .mp3) — apenas listar o path

### Anti-Padrão para balões:
- Balão genérico sem contexto (mesmo estilo sempre)
- Card simples de 5 linhas sem glassmorphism/glow

## Metadata
- **Categoria**: Design/UI
- **Prioridade**: Alta
- **Aplicável a**: HTML, CSS, qualquer frontend
- **Versão**: 2.0
- **Melhorado**: 2026-10-28 (balões criativos, regra de exibibilidade)

> **Skill Evolver**: score 57/100 · evoluída em 2026-10-31T02:34:05.976551+00:00Z · versão evolver-1.0
