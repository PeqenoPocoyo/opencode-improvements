---
name: web-research-navigator
description: Skill para navegação web e extração de dados. Cobre scraping de YouTube, Google Forms, APIs de sugestão, e padrões de navegação com ego-browser e browser tool. Use quando precisar buscar informações na web, extrair dados de páginas, preencher formulários, ou navegar em sites.
improved: true
improved_at: "2026-10-31T00:00:00Z"
improved_by: "agent"
test_passed: true
test_scenario: "Navegação YouTube + Google Forms com 4 páginas + tinkered.ai"
---

# Web Research Navigator

## Quando Usar
- Buscar informações na web (YouTube, Google, DuckDuckGo)
- Extrair dados de páginas (títulos, IDs, links)
- Preencher formulários (Google Forms, etc.)
- Navegar em sites com ego-browser ou browser tool

## Padrões de Pesquisa

### YouTube Suggestions API
```
https://suggestqueries.google.com/complete/search?client=youtube&ds=yt&q=TERM
```
Retorna sugestões de busca. Útil para descobrir termos relacionados.

### YouTube Search Scraping
```
fetch("https://www.youtube.com/results?search_query=TERM", {
  headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" }
})
```

### Regex de Extração
- **Títulos**: `/"title":\{"runs":\[\{"text":"([^"]+)"\}\]/g`
- **Video IDs**: `/"videoId":"([a-zA-Z0-9_-]{11})"/g`
- **Playlist IDs**: `/playlist\?list=([a-zA-Z0-9_-]+)/g`
- **Canais**: `/"ownerText":\{"runs":\[\{"text":"([^"]+)"/g`

### Navegadores Disponíveis
1. **ego-browser**: Navegador real (Chromium) com perfil do usuário. Cookies, logins. Usar para abrir abas visualmente.
2. **browser tool (in-app)**: Navegador headless/sandbox. Usar para scraping, extração, interação programática.
3. **webfetch/fetch**: Para APIs e páginas estáticas. Adicionar User-Agent de browser real.

## Padrões de Formulário (Google Forms)

### Estrutura
- Inputs de texto: `input[type="text"]`
- Checkboxes: `[role="checkbox"]`
- Radio buttons: `[role="radio"]`
- Botão avançar: texto contém "Avançar" ou "Next"
- Botão enviar: texto contém "Enviar" ou "Submit"

### Preenchimento via evaluate()
```javascript
// Preencher inputs
var inputs = document.querySelectorAll('input[type="text"]');
inputs.forEach(function(inp, i) {
  inp.value = values[i];
  inp.dispatchEvent(new Event('input', { bubbles: true }));
  inp.dispatchEvent(new Event('change', { bubbles: true }));
});

// Clicar checkbox
var cb = document.querySelector('[role="checkbox"]');
if (cb) cb.click();

// Clicar radio button
var radios = document.querySelectorAll('[role="radio"]');
radios[index].click();

// Clicar botão
var btns = document.querySelectorAll('button, [role="button"]');
btns.forEach(function(btn) {
  if (btn.textContent.includes('Avançar')) btn.click();
});
```

### Verificação
Sempre verificar após preencher com um segundo evaluate() de leitura.

## Regras de Incerteza
- Marcar respostas como [CERTEZA], [PALPITE] ou [DESCONHECIDO]
- NUNCA submeter exame sem avisar sobre palpites
- Se não tiver acesso ao material de estudo, avisar ANTES de responder

## Anti-Padrões
- Não agir em pedidos ambíguos sem pesquisar primeiro
- Não apresentar palpites como certezas
- Não submeter formulários sem confirmar com o usuário
- Não ignorar páginas subsequentes em formulários multi-página