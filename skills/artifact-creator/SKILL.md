---
name: artifact-creator
description: Cria artefatos HTML interativos, funcionais e criativos sob demanda ou espontaneamente. Cada artefato tem identidade visual única, elementos funcionais (sem botões mortos), efeitos reativos e animações com propósito. Gera espontaneamente quando o usuário pode se beneficiar (dúvidas, exemplos, visualização de dados, simulações). Use quando criar dashboards, simulações, visualizações, ferramentas interativas, ou quando o usuário pedir exemplos/explorações.
improved: true
improved_at: "2026-10-28T00:00:00Z"
improved_by: "agent"
test_passed: true
test_scenario: "Gerar 3 artefatos diferentes espontaneamente e verificar que nenhum compartilha layout/paleta e todos têm elementos funcionais"
---

# Artifact Creator — Skill

> **Triggers (auto)**: artifact creator, artifact-creator

## Princípio Central
**Artefatos não são sites.** São peças visuais interativas, funcionais e criativas que comunicam informação de forma dinâmica.

## Quando Gerar Espontaneamente

O agente deve gerar um artefato **sem ser solicitado** quando:

1. **O usuário tem dúvida** — um visual explica melhor que texto.
2. **O usuário pede exemplos** — um artefato interativo é mais didático.
3. **Dados precisam de visualização** — métricas, gráficos, comparações.
4. **Simulação é útil** — física, circuitos, processos, sistemas.
5. **O tema é complexo** — diagramas, fluxos, arquiteturas.
6. **O usuário parece engajado** — aprofundar com visual.
7. **Há oportunidade de "mostrar"** — não apenas "dizer".

### Regra de Ouro de Geração Espontânea
> Se você pensou "seria legal mostrar isso visualmente" → gere o artefato.  
> Não espere o usuário pedir "crie um artefato".

## Estrutura de um Artefato

### 1. HTML Auto-contido
- Um único arquivo `.html`
- CSS inline (no `<style>`)
- JS inline (no `<script>`)
- Sem dependências externas (exceto CDNs opcionais para libs específicas)
- Funciona offline

### 2. Identidade Visual Única
Cada artefato deve ter:
- **Paleta própria** (rotacionar entre: cyan/violet, amber/red, green/teal, pink/orange, monochrome, dark+neon)
- **Tipografia própria** (não sempre Inter — usar JetBrains Mono, Space Grotesk, Playfair, etc.)
- **Layout próprio** (não repetir estrutura do anterior)
- **Pelo menos um elemento "surpresa"** (animação, efeito, forma não-retangular)

### 3. Funcionalidade Completa
- Todo botão tem handler
- Todo input tem output
- Todo link navega
- Canvas renderiza e responde
- Modais abrem/fecham
- Estados vazios são tratados

### 4. Efeitos e Animações
- Pelo menos um efeito reativo ao mouse/scroll
- Transições suaves (cubic-bezier)
- Animações com propósito (não decorativas)
- Glow, tilt, parallax, partículas quando apropriado

## Tipos de Artefato

### A. Visualização de Dados
- Gráficos interativos (canvas/SVG)
- Dashboards com métricas animadas
- Comparadores (antes/depois, A/B)
- Mapas de calor, árvores, grafos

### B. Simulação
- Física (gravidade, colisões, fluidos)
- Circuitos elétricos
- Processos (manufatura, logística)
- Sistemas (ecossistemas, redes)

### C. Ferramenta Interativa
- Calculadoras
- Conversores
- Configuradores
- Editores

### D. Experiência Imersiva
- Generative art
- Audio-visual
- 3D/2.5D
- Scrollytelling

### E. Educacional
- Tutoriais interativos
- Quizzes
- Diagramas anotados
- Step-by-step guides

## Checklist de Qualidade

### Antes de Entregar
- [ ] Todos os botões/inputs/links funcionam?
- [ ] Há tratamento de erro?
- [ ] O layout é responsivo (min 320px)?
- [ ] Não há código morto?
- [ ] As variáveis estão nomeadas claramente?
- [ ] A paleta é diferente do artefato anterior?
- [ ] Há pelo menos um efeito reativo?
- [ ] Há pelo menos uma animação com propósito?
- [ ] O artefato é auto-contido (funciona offline)?
- [ ] O título é descritivo?
- [ ] CSP-friendly: usar addEventListener em vez de inline onclick; sem eval; sem fetch interno; sem keys/tokens no arquivo.

### Teste de Reinterpretação
```
DADO um artefato gerado
QUANDO o usuário interage com cada elemento
ENTÃO cada elemento deve responder
E a experiência deve ser fluida (sem lag, sem bugs)
SE algum elemento não responder → FAIL
```

## Padrões de Código

### HTML
```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Título Descritivo</title>
<style>
  /* CSS inline, variáveis CSS, responsive */
</style>
</head>
<body>
  <!-- Estrutura semântica -->
  <script>
    // JS inline, funções nomeadas, event listeners
  </script>
</body>
</html>
```

### CSS
- Usar CSS variables (`:root`)
- Mobile-first com media queries
- `transform` e `opacity` para animações (GPU-accelerated)
- `backdrop-filter` para glassmorphism
- Gradientes para profundidade

### JS
- Funções nomeadas para handlers
- `requestAnimationFrame` para animações
- `IntersectionObserver` para lazy loading
- Event delegation quando possível
- Cleanup de event listeners

## Efeitos Recomendados

### Reativos ao Mouse
- Glow radial que segue cursor
- Tilt 3D em cards (rotateX/Y baseado em posição)
- Parallax em camadas
- Hover scale com transition

### Animações
- Count-up em números (easing cúbico)
- Barras de progresso com grow
- Fade-in com IntersectionObserver
- Slide-in de elementos
- Pulse em elementos importantes

### Visuais
- Partículas (canvas) com conexões
- Gradientes animados
- Glassmorphism (blur + transparência)
- Sombras coloridas
- Clip-path para formas não-retangulares

## Paletas (rotacionar)

| # | Nome | Primária | Secundária | Fundo | Uso |
|---|---|---|---|---|---|
| 1 | Tech | #5eead4 | #a78bfa | #0a0c12 | Tech, futurista |
| 2 | Industrial | #ffc850 | #ff6b6b | #0c1117 | Elétrica, mecânica |
| 3 | Organic | #4ade80 | #5eead4 | #0a1410 | Natureza, saúde |
| 4 | Creative | #f472b6 | #fbbf24 | #120a14 | Arte, design |
| 5 | Minimal | #ffffff | #8a9bb0 | #0a0a0a | Clean, elegante |
| 6 | Cyberpunk | #00ff88 | #ff00ff | #0a0014 | Gamer, neon |

## Layouts (rotacionar)

| # | Nome | Estrutura | Uso |
|---|---|---|---|
| 1 | Canvas+Overlay | Canvas principal + HUD | Simulações, generative art |
| 2 | Hero+Scroll | Seções verticais | Storytelling, documentação |
| 3 | Split Screen | 2 painéis lado a lado | Comparadores, A/B |
| 4 | Masonry | Grid assimétrico | Galerias, cards |
| 5 | Radial | Elementos em círculo | Métricas, dashboards |
| 6 | Timeline | Vertical/horizontal | Processos, histórico |
| 7 | Card Stack | Cartões com profundidade | Apresentações, slides |

## Geração Dinâmica

### Algoritmo de Decisão
```
1. Analisar a mensagem do usuário
2. Identificar se há oportunidade visual:
   - Dúvida? → explicar com visual
   - Exemplo pedido? → artefato interativo
   - Dados? → visualização
   - Complexo? → diagrama/simulação
   - Engajado? → aprofundar
3. Se sim:
   a. Escolher tipo de artefato (A-E)
   b. Escolher paleta (rotacionar, não repetir anterior)
   c. Escolher layout (rotacionar, não repetir anterior)
   d. Implementar com funcionalidade completa
   e. Adicionar efeitos reativos
   f. Validar checklist
   g. Entregar
4. Se não:
   a. Responder com texto
   b. Oferecer "posso criar um visual se quiser"
```

### Anti-Repetição
- Manter histórico mental dos últimos 3 artefatos
- Não repetir paleta consecutivamente
- Não repetir layout consecutivamente
- Não repetir estrutura de abas/seções

## Balões de Artifacts (regra de criatividade)

Quando usar o Review pane, emitir balão de artifacts ao final da resposta.
Os balões devem ser **criativos e contextuais**, não genéricos:

1. Paleta contextual por tipo (HTML=indigo, SVG=emerald, MD=amber, CSV=sky, código=violet)
2. Layout dinâmico: grid 2 colunas para 2+ artifacts, card único para 1
3. Animações CSS: float, blink, shimmer, slide-up, hover (translateY + shadow colorida)
4. Glassmorphism: gradiente + border semi-transparente + backdrop-filter
5. Glow effects: radial-gradient blur atrás dos ícones
6. Badges contextuais: tags por tipo com cores temáticas
7. Descrições ricas: nome + descrição curta + tipo + origem
8. Hover interativo: card levanta + shadow colorida

### Regra de exibibilidade para botões inline
- Gerar botão inline APENAS para arquivos que o panel pode exibir (HTML, SVG, MD, CSV, código)
- Não gerar botão para binários (.zip, .exe, .png, .pdf, .mp3) — apenas listar o path
- Para exibíveis: link `file://` que abre no Review pane automaticamente

### Auto-abertura no Review Pane (OBRIGATORIO)
**SEMPRE chamar `browser.preview()` automaticamente** apos salvar o arquivo.
Nao esperar o usuario pedir. Isso vale para QUALQUER artefato gerado.

## Metadata
- **Prioridade**: Alta
- **Aplicavel a**: Qualquer artefato HTML
- **Dependencias**: functional-ui, creative-design, inline-artifacts, artifact-balloon
- **Generativa**: Sim — cria novas capacidades de visualizacao
- **Versao**: 2.1
- **Melhorado**: 2026-10-29 (auto-abertura no Review pane, baloes criativos, regra de exibibilidade)

> **Skill Evolver**: score 66/100 · evoluída em 2026-10-31T02:34:05.806709+00:00Z · versão evolver-1.0
