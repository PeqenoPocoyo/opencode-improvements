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

## Compatibilidade CSP (artefatos single-file)
Hosts (wikis, viewers) podem servir o HTML em iframe sandboxed com CSP strict.
Regras:
- Preferir `addEventListener` em vez de inline `onclick=""` (inline handlers são bloqueados por CSP strict).
- Não usar `eval`/`new Function` (bloqueado por CSP `unsafe-eval`).
- Não fazer `fetch()` para endpoints internos — bake snapshot JSON em `const DATA = {...}`.
- Nunca deixar API keys/tokens no arquivo (busque `key`, `token`, `Bearer` antes de publicar).
- CDN: versionar pin + fallback se JS falhar.
- Testar em 375px de largura (viewport meta obrigatório).

## Regra de Exibibilidade para Botões Inline (balões de artifacts)

Quando gerar balões de artifacts ao final da resposta:

### Botões inline (links `file://`)
- **Gerar botão inline** APENAS para arquivos que o panel pode exibir:
  - HTML, HTM, SVG, MD, Markdown, CSV, TSV
  - Código (JS, TS, PY, GO, RS, JAVA, C, CPP, CS, PHP, SH, SQL, JSON, YAML, XML, TOML, INI, LOG, DIFF, TXT)
- **NÃO gerar botão** para arquivos binários:
  - Imagens (.png, .jpg, .gif, .webp, .svg binário)
  - Documentos (.pdf)
  - Áudio (.mp3, .wav, .ogg, .m4a, .flac)
  - Arquivos compactados (.zip, .rar, .7z, .tar, .gz)
  - Executáveis (.exe, .dll, .bat, .cmd, .sh executável)
  - Qualquer arquivo que o panel não consiga renderizar
- Para arquivos não exibíveis: apenas listar o path no balão, sem botão

### Por quê?
O OpenCode intercepta TODOS os links `file://` e abre no Review pane.
Se o panel não pode exibir o arquivo, o link abrirá uma tentativa de render que falha.
Portanto, botões inline só fazem sentido para arquivos que o panel pode renderizar.

### Teste de Reinterpretação
```
DADO um balão de artifacts com N arquivos
QUANDO o usuário clica em um botão inline
ENTÃO se o arquivo é exibível pelo panel → abre no Review pane
E se o arquivo NÃO é exibível → não há botão (apenas path listado)
SE um botão abrir um arquivo não exibível no panel → FAIL
```

## Metadata
- **Categoria**: UI/UX
- **Prioridade**: Crítica
- **Aplicável a**: HTML, React, Vue, Svelte, qualquer framework
- **Versão**: 2.0
- **Melhorado**: 2026-10-28 (regra de exibibilidade para botões inline em balões de artifacts)
