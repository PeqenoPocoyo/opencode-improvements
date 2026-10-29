# Changelog

## [1.3.0] — 2026-10-28

### Melhorado (auto-upgrade v2 — feedback-driven)
- `instructions/inline-artifacts.md` — secao de baloes criativos e contextuais (10 regras de criatividade), regra de exibibilidade para botoes inline (so para arquivos exibiveis pelo panel)
- `instructions/AGENTS.md` — secao 11 (baloes criativos, regra de exibibilidade, anti-padroes de balao generico)
- `validation.json` — incrementado usage_count (sessao 2), promovidos 3 recursos para `proactive`: inline-artifacts.md, pre-tool-use-security.sh, AGENTS.md
- Artefato Kawasaki v3 criado (redesign completo: hero dramático, partículas, gamificação, timeline visual, urgência)
- Artefato Versys-X criado (SVG estilizado da moto, specs, animações)

### Promovido para Proactive
- `instructions/inline-artifacts.md` — 3+ usos, 0 feedback negativo → auto-aplicado
- `hooks/pre-tool-use-security.sh` — 3+ usos, 0 feedback negativo → auto-aplicado
- `instructions/AGENTS.md` — 3+ usos, 0 feedback negativo → auto-aplicado

## [1.2.1] — 2026-10-28

### Melhorado
- `hooks/pre-tool-use-security.sh` — padrões regex mais robustos (alinhados com validate_bash_command.py), detecção de segredos em Write/Edit, fail-open, mensagens mais claras.

## [1.2.0] — 2026-10-28

### Adicionado (contribuição do dispositivo Cesar)
- `hooks/validate_bash_command.py` — validação robusta de comandos bash (regex, fail-open)
- `hooks/validate_sensitive_write.py` — alerta para escrita em arquivos sensíveis
- `hooks/session_start.py` / `session_end.py` — logging de início/fim de sessão
- `hooks/notification_handler.py` — logging de notificações
- `hooks/subagent_start.py` / `subagent_stop.py` — logging de subagentes
- `instructions/inline-artifacts.md` — regras de proatividade de visuais inline vs Review pane
- `configs/settings.example.json` — exemplo de hooks configurados (placeholders)
- Atualizado `configs/mcp.example.json` — adicionado MCP rea (reverse engineering) como exemplo opcional
- Atualizado `instructions/AGENTS.md` — seção 10 (hooks e observabilidade) + referência inline-artifacts

### Melhorado
- Hooks: de 1 hook bash para 8 hooks (1 bash + 7 Python) cobrindo mais eventos
- Instruções: proatividade de artefatos inline documentada

## [1.1.0] — 2026-10-28

### Adicionado
- `instructions/AGENTS.md` — Instruções globais do OpenCode
- `instructions/artifact-generation.md` — Instrução de geração de artefatos
- `skills/functional-ui/SKILL.md` — Garantia de UI funcional
- `skills/creative-design/SKILL.md` — Criatividade e não-repetição
- `skills/self-upgrade/SKILL.md` — Protocolo de auto-upgrade
- `skills/artifact-creator/SKILL.md` — Criação de artefatos HTML
- `hooks/pre-tool-use-security.sh` — Hook de segurança PreToolUse
- `configs/mcp.example.json` — Configuração MCP de exemplo
- `notes/conversation-insights.md` — Insights da conversa
- `docs/self-upgrade-protocol.md` — Documentação do protocolo
- `docs/SYNC.md` — Guia de sincronização multi-dispositivo
- `scripts/sync.ps1`, `sync.sh`, `onboard-device.ps1` — Scripts de sync
- `docs/CHANGELOG.md` — Este arquivo
- 7 novos artefatos HTML:
  - acme-funnel-fix.html
  - acme-funnel-creative.html
  - orbital.html
  - synthesia.html
  - mecatronica-4sem.html
  - eletrica-tecnica.html
  - pc-builder-25d.html

### Melhorado
- Estrutura do repositório organizada
- Artefatos movidos para `artefatos/`
- .gitignore atualizado

## [1.0.0] — 2026-10-27

### Adicionado
- Scaffold inicial do projeto
- `artefatos/cte-dashboard-estoque.html`
- README.md com estrutura e regras
