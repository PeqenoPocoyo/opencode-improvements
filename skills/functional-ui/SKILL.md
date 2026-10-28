---
name: functional-ui
description: Garante que todo elemento de UI seja funcional — nenhum botão morto, nenhum input sem output, nenhum link quebrado. Use quando criar ou revisar interfaces, dashboards, formulários, ou qualquer artefato com elementos interativos.
improved: true
improved_at: "2026-10-28T00:00:00Z"
improved_by: "agent"
test_passed: true
test_scenario: "Criar artifact com 5 botões, verificar que todos têm onclick handler e executam ação"
---

# Functional UI — Skill

## Princípio Central
**Nenhum elemento de UI pode ser "morto".** Se existe, funciona.

## Checklist de Validação

### Botões
- [ ] Todo `<button>` tem `onclick` ou event listener.
- [ ] O handler executa uma ação observável (visual, console, DOM change).
- [ ] Botões de "submit" realmente submetem.
- [ ] Botões de "reset" realmente resetam.
- [ ] Botões de "export" realmente exportam (download, copy, etc.).

### Inputs
- [ ] Todo `<input>` tem um output associado (display, cálculo, filtro).
- [ ] Sliders atualizam valores em tempo real.
- [ ] Text inputs filtram/buscam/atualizam.

### Links
- [ ] Todo `<a>` tem `href` válido.
- [ ] Links externos abrem em nova aba (`target="_blank"`).
- [ ] Links internos navegam corretamente.

### Selects/Dropdowns
- [ ] Mudança de seleção atualiza o conteúdo.
- [ ] Opções são relevantes e completas.

### Canvas/Gráficos
- [ ] Renderizam ao carregar.
- [ ] Respondem a inputs (zoom, pan, filtro).
- [ ] Redimensionam com a janela.

### Modais/Dialogs
- [ ] Abrir e fechar funciona.
- [ ] Fechar com ESC funciona.
- [ ] Click fora fecha.

## Teste de Reinterpretação

### Cenário 1: Botão Morto
```
DADO um artifact com 5 botões
QUANDO o usuário clica em cada botão
ENTÃO cada botão deve produzir uma ação observável
SE algum botão não responder → FAIL
```

### Cenário 2: Input Sem Output
```
DADO um formulário com 3 inputs
QUANDO o usuário preenche os inputs
ENTÃO pelo menos um output deve ser atualizado
SE nenhum output mudar → FAIL
```

### Cenário 3: Link Quebrado
```
DADO um artifact com links
QUANDO o usuário clica em cada link
ENTÃO o link deve navegar (interno) ou abrir (externo)
SE algum link não responder → FAIL
```

## Anti-Padrões

### ❌ Botão Decorativo
```html
<button class="btn">Exportar</button>  <!-- sem onclick -->
```

### ❌ Input Órfão
```html
<input type="range" id="slider">  <!-- sem oninput, sem output -->
```

### ❌ Link Vazio
```html
<a href="#">Clique aqui</a>  <!-- não navega -->
```

## Padrões Corretos

### ✅ Botão Funcional
```html
<button class="btn" onclick="exportData()">Exportar</button>
<script>
function exportData() {
  const blob = new Blob([JSON.stringify(data)], {type:'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'data.json'; a.click();
  URL.revokeObjectURL(url);
  showToast('Exportado!');
}
</script>
```

### ✅ Input com Output
```html
<input type="range" id="slider" min="0" max="100" oninput="updateOutput(this.value)">
<span id="output">0</span>
<script>
function updateOutput(v) { document.getElementById('output').textContent = v; }
</script>
```

### ✅ Link Funcional
```html
<a href="https://example.com" target="_blank" rel="noopener">Abrir</a>
```

## Regra de Ouro
> "Por que entregar um botão que não funciona?"  
> Se não tem handler, não existe. Remova ou implemente.

## Metadata
- **Categoria**: UI/UX
- **Prioridade**: Crítica
- **Aplicável a**: HTML, React, Vue, Svelte, qualquer framework
