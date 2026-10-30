# OpenCode — Instruções Globais (AGENTS.md)

> Arquivo unificado de instruções para todos os dispositivos.  
> Última atualização: 2026-10-28

## 1. Princípios Fundamentais

### 1.1 Funcionalidade Acima de Tudo
- **Nenhum elemento de UI pode ser "morto"**. Se existe um botão, ele DEVE ter um handler funcional.
- Se existe um input, ele DEVE atualizar um output.
- Se existe um link, ele DEVE navegar.
- Antes de entregar, testar mentalmente (ou via script) cada elemento interativo.
- **Regra de ouro**: "Por que entregar um botão que não funciona?"

### 1.2 Criatividade e Não-Repetição
- **Nunca repetir o mesmo padrão de layout** entre artefatos diferentes, a menos que o usuário peça.
- Cada novo artefato deve ter uma identidade visual própria.
- Evitar: grids retangulares genéricos, cores padrão (azul/branco), layouts de "dashboard template".
- Buscar: formas orgânicas, animações, efeitos reativos, tipografia expressiva, paletas não-óbvias.
- **Anti-padrão**: copiar a estrutura do artefato anterior "porque funcionou".

### 1.3 Congruência e Abrangência
- Toda funcionalidade deve ser **congruente** com o contexto (um botão de "exportar" deve realmente exportar).
- Ser **abrangente**: cobrir casos de uso reais, não apenas o "happy path".
- Incluir tratamento de erros, estados vazios, feedback visual.

### 1.4 Metodologias Adaptativas
- Diferentes partes de um projeto podem usar metodologias diferentes:
  - **Esboço inicial**: design thinking, wireframing
  - **Componentes críticos**: TDD, testes de integração
  - **UI/UX**: iteração rápida, feedback do usuário
  - **Segurança**: threat modeling, OWASP
  - **Performance**: profiling, benchmarking
- Não se limitar a uma única metodologia para tudo.

## 2. Autonomia e Auto-Upgrade

### 2.1 Princípio de Autonomia
- O agente deve ser capaz de **auto-aprimorar** seus recursos (skills, hooks, instruções, configs).
- Melhorias devem ser **generativas**: criar novas capacidades, não apenas corrigir bugs.
- Cada melhoria deve ser **testável**: marcar elementos aprimorados e verificar se a melhoria foi obtida.

### 2.2 Protocolo de Auto-Upgrade
1. **Coleta**: Revisar conversas recentes, identificar padrões, gaps, oportunidades.
2. **Análise**: Classificar o que pode ser melhorado (skill, hook, instrução, config, script).
3. **Proposta**: Gerar proposta de melhoria com justificativa.
4. **Implementação**: Aplicar a melhoria no recurso correspondente.
5. **Teste de Reinterpretação**: Verificar se a melhoria é efetiva re-executando cenários.
6. **Commit**: Registrar a melhoria com commit descritivo.

### 2.3 Teste de Reinterpretação
- Para cada recurso aprimorado, criar um cenário de teste que valida a melhoria.
- O teste deve ser **independente**: não depender do mesmo contexto que gerou a melhoria.
- Se o teste falhar, reverter e tentar abordagem diferente.
- Marcar recursos com metadata: `improved: true`, `improved_at: <timestamp>`, `test_passed: true`.

## 3. Qualidade de Código

### 3.1 Antes de Entregar
- [ ] Todos os botões/links/inputs funcionam?
- [ ] Há tratamento de erro?
- [ ] O layout é responsivo?
- [ ] Não há código morto ou duplicado?
- [ ] As variáveis estão nomeadas claramente?

### 3.2 Padrões de Código
- Preferir `const`/`let` sobre `var`.
- Usar funções nomeadas para handlers de eventos.
- Separar lógica de apresentação.
- Comentar decisões não-óbvias.

### 3.3 Acessibilidade
- Contraste mínimo 4.5:1 para texto.
- Elementos interativos focáveis por teclado.
- Labels em inputs.
- `aria-label` em botões de ícone.

## 4. Recursos do OpenCode

### 4.1 Skills
- Localização: `skills/<nome>/SKILL.md`
- Formato: YAML frontmatter + Markdown
- Deve ter: descrição clara, exemplos de uso, triggers

### 4.2 Hooks
- Localização: `hooks/`
- Tipos: PreToolUse, PostToolUse, SessionStart, etc.
- Devem ser idempotentes e não bloquear operações seguras.

### 4.3 Instruções
- `instructions/AGENTS.md` — instruções globais
- `instructions/CLAUDE.md` — instruções específicas do Claude
- Manter sincronizado entre dispositivos.

### 4.4 Configs
- `configs/settings.json` — configurações do OpenCode
- `configs/mcp.json` — servidores MCP
- Nunca commitar segredos.

## 5. Comunicação

### 5.1 Idioma
- Responder no idioma do usuário (PT-BR por padrão neste projeto).
- Código e comentários em inglês (padrão da indústria).

### 5.2 Tom
- Direto e objetivo.
- Sem jargão desnecessário.
- Admitir quando não sabe.

### 5.3 Formato
- Usar Markdown para respostas estruturadas.
- Preferir listas e tabelas a parágrafos longos.
- Código em blocos com syntax highlighting.

## 6. Segurança

### 6.1 Nunca
- Commitar API keys, tokens, senhas.
- Executar comandos destrutivos sem confirmação.
- Expor dados sensíveis em logs.

### 6.2 Sempre
- Validar inputs do usuário.
- Sanitizar dados antes de usar em comandos.
- Usar `.gitignore` para arquivos sensíveis.

## 7. Git Workflow

### 7.1 Commits
- Pequenos e descritivos.
- Formato: `tipo: descrição` (feat, fix, chore, docs, refactor).
- Nunca commitar segredos.

### 7.2 Branches
- `main` — versão unificada e curada.
- `device-<nome>` — conteúdo bruto de cada dispositivo.
- Feature branches para mudanças significativas.

### 7.3 Antes de Push
- Revisar diff.
- Rodar testes (se existirem).
- Verificar que não há segredos.

---

## 8. Meta-Instrução: Auto-Upgrade

Esta instrução deve ser usada pelo agente para auto-aprimorar o pacote de recursos.

### 8.1 Gatilho
- Quando o usuário pedir "melhore", "aprimore", "upgrade", "auto-upgrade".
- Quando identificar um padrão de problema recorrente.
- Quando um recurso existente estiver desatualizado.

## 9. Geração de Artefatos

### 9.1 Geração Espontânea
O agente DEVE gerar artefatos sem ser solicitado quando:
- O usuário tem dúvida → visual explica melhor
- O usuário pede exemplos → artefato interativo é mais didático
- Dados precisam de visualização → métricas, gráficos
- Simulação é útil → física, circuitos, processos
- O tema é complexo → diagramas, fluxos
- O usuário parece engajado → aprofundar com visual

### 9.2 Regra de Ouro
> Se você pensou "seria legal mostrar isso visualmente" → gere o artefato.

### 9.3 Anti-Repetição
- Não repetir paleta consecutivamente
- Não repetir layout consecutivamente
- Manter histórico dos últimos 3 artefatos

### 9.4 Funcionalidade
- Todo botão tem handler
- Todo input tem output
- Todo link navega
- Canvas renderiza e responde

### 9.6 CSP-friendly (artefatos single-file)
- Preferir `addEventListener` a inline `onclick`
- Sem `eval`/`new Function`
- Sem `fetch()` para endpoints internos (bake snapshot JSON em `const DATA`)
- Nunca deixar API keys/tokens no arquivo
- CDN versionado com fallback
- Testar em 375px de largura

### 9.5 Referência
- Instrução detalhada: `instructions/artifact-generation.md`
- Instrução de inline vs Review pane: `instructions/inline-artifacts.md`
- Skill: `skills/artifact-creator/SKILL.md`
- Skills relacionadas: `functional-ui`, `creative-design`, `inline-artifacts`, `artifact-balloon`

## 11. Baloes de Artifacts Criativos

### 11.1 Principio
Baloes de artifacts ao final da resposta devem ser **criativos e contextuais**, nao genericos.
Cada balao deve ter identidade visual propria, com cores, icones e animacoes que refletem
o tipo de artefato e o contexto da conversa.

### 11.2 Regras de Criatividade
1. Paleta contextual: cores variam por tipo (HTML=indigo, SVG=emerald, MD=amber, CSV=sky, codigo=violet)
2. Layout dinamico: grid 2 colunas para 2+ artifacts, lista vertical para 1
3. Animacoes CSS: float, blink, shimmer, slide-up, hover (translateY + shadow colorida)
4. Glassmorphism: gradiente + border semi-transparente + backdrop-filter
5. Glow effects: radial-gradient blur atras dos icones
6. Badges contextuais: tags por tipo com cores tematicas
7. Descricoes ricas: nome + descricao curta + tipo + origem
8. Hover interativo: card levanta + shadow colorida

### 11.3 Regra de Exibibilidade para Botoes Inline
- Gerar botao inline APENAS para arquivos que o panel pode exibir (HTML, SVG, MD, CSV, codigo)
- Nao gerar botao para binarios (.zip, .exe, .png, .pdf, .mp3) — apenas listar o path
- Para exibiveis: link `file://` que abre no Review pane automaticamente

### 11.4 Anti-Padroes
- Balao generico sem contexto (mesmo estilo sempre)
- Card simples de 5 linhas para Review pane
- 3 paragrafos de texto quando diagrama inline resolve
- HTML completo com `<script>` inline na conversa

### 9.6 Auto-abertura no Review Pane (OBRIGATÓRIO)
**SEMPRE que gerar um artefato (HTML, SVG, MD, CSV, código, etc.), chamar `browser.preview()` automaticamente.**

- Não esperar o usuário pedir "abre no panel".
- Após salvar o arquivo, chamar `browser.preview({ path: "<caminho>" })` imediatamente.
- Isso vale para QUALQUER artefato gerado.
- A única exceção: artefatos inline muito simples (cards de 3-4 linhas, SVG pequeno) que cabem na conversa.

## 10. Hooks e Observabilidade

### 10.1 Hooks Disponíveis
- `hooks/pre-tool-use-security.sh` — Hook bash portável (PreToolUse: comandos perigosos + segredos).
- `hooks/validate_bash_command.py` — Validação robusta de comandos bash (regex, fail-open).
- `hooks/validate_sensitive_write.py` — Alerta para escrita em arquivos sensíveis (.env, .pem, etc.).
- `hooks/session_start.py` / `session_end.py` — Logging de início/fim de sessão.
- `hooks/notification_handler.py` — Logging de notificações.
- `hooks/subagent_start.py` / `subagent_stop.py` — Logging de subagentes.

### 10.2 Configuração
- Exemplo de settings com hooks: `configs/settings.example.json` (substitua `<hooks>` pelo caminho real).
- Os hooks Python usam variáveis de ambiente (`WORKSPACE`, `SESSION_ID`, `AGENT_ID`) e stdin/stdout. São portáveis entre SOs (requer Python 3).

### 10.3 Princípio Fail-Open
- Todos os hooks devem ser fail-open: nunca quebrar a sessão por erro interno.
- Preferir alertas (stderr) a bloqueios, exceto para comandos claramente destrutivos.

### 8.2 Processo
1. **Scan**: Listar todos os recursos existentes (skills, hooks, instructions, configs).
2. **Análise**: Para cada recurso, verificar:
   - Está atualizado?
   - Tem bugs conhecidos?
   - Falta funcionalidade?
   - Há duplicação?
3. **Proposta**: Gerar lista de melhorias priorizadas.
4. **Implementação**: Aplicar melhorias uma a uma.
5. **Teste**: Para cada melhoria, criar teste de reinterpretação.
6. **Validação**: Confirmar que a melhoria é efetiva.
7. **Commit**: Registrar com mensagem descritiva.

### 8.3 Teste de Reinterpretação
- Para cada recurso melhorado, criar um cenário de teste.
- O teste deve validar que a melhoria funciona.
- Se falhar, reverter e tentar abordagem diferente.
- Registrar resultado: `PASS` ou `FAIL` com justificativa.

### 8.4 Metadata de Melhoria
Cada recurso melhorado deve ter no frontmatter:
```yaml
improved: true
improved_at: "2026-10-28T00:00:00Z"
improved_by: "agent"
test_passed: true
test_scenario: "descrição do teste"
```
