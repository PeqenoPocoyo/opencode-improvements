# OpenCode Continuous Improvement Project

Repositório unificado para melhorar continuamente os modelos de IA e o próprio OpenCode,
agregando skills, hooks, instruções, configurações e notas de 3 dispositivos.

## Estrutura sugerida

- `skills/` — skills personalizadas (SKILL.md + recursos)
- `hooks/` — hooks (PreToolUse, etc.)
- `instructions/` — instruções globais (CLAUDE.md, AGENTS.md, etc.)
- `configs/` — configurações (settings.json, MCP, etc.)
- `notes/` — anotações e ideias
- `docs/` — documentação

## Sincronização entre dispositivos

Cada dispositivo mantém uma branch própria até a unificação:

- `main` — versão unificada e curada
- `device-<nome>` — conteúdo bruto de cada dispositivo (ex: `device-laptop`, `device-desktop`, `device-tablet`)

### Fluxo de unificação

1. Em cada dispositivo: `git init` (se ainda não for repo), adicionar remote, criar branch `device-<nome>`, commitar tudo, push da branch.
2. Neste dispositivo: `git fetch --all`, mesclar as branches `device-*` em `main`, resolver conflitos, remover duplicatas/bugs/irrelevâncias.
3. Push de `main` para o GitHub.
4. Nos outros dispositivos: `git checkout main && git pull` para receber a versão unificada.

## Pacote de Recursos

### Skills
- `artifact-creator` — Cria artefatos HTML interativos, funcionais e criativos
- `creative-design` — Evita padrões repetitivos, cada artefato com identidade visual própria
- `functional-ui` — Garante que todo elemento de UI seja funcional (sem botões mortos)
- `inline-artifacts` — Artefatos inline (SVG, HTML, Mermaid) + balões criativos
- `artifact-balloon` — Salva arquivos grandes/interativos no Review pane + balões criativos
- `opencode-sync` — Conexão, auto-sync, validação progressiva, contribuição
- `self-upgrade` — Protocolo de auto-aprimoramento contínuo

### Hooks
- `pre-tool-use-security.sh` — Hook bash portável (PreToolUse: comandos perigosos + segredos)
- `validate_bash_command.py` — Validação robusta de comandos bash (regex, fail-open)
- `validate_sensitive_write.py` — Alerta para escrita em arquivos sensíveis
- `session_start.py` / `session_end.py` — Logging de início/fim de sessão
- `notification_handler.py` — Logging de notificações
- `subagent_start.py` / `subagent_stop.py` — Logging de subagentes

### Instruções
- `AGENTS.md` — Instruções globais (princípios, qualidade, segurança, git workflow, balões criativos)
- `inline-artifacts.md` — Regras de artefatos inline vs Review pane + balões criativos
- `artifact-generation.md` — Instrução de geração de artefatos HTML

### Validação Progressiva
Recursos passam por 4 estados: `raw → marked → validated → proactive`
- `marked → validated`: 3+ usos sem feedback negativo
- `validated → proactive`: 7+ usos sem feedback negativo
- 2+ feedbacks negativos → reverter para `raw`

### Balões de Artifacts (Criativos)
Ao final da resposta, emitir balão de artifacts com:
- Paleta contextual por tipo (HTML=indigo, SVG=emerald, MD=amber, etc.)
- Glassmorphism, glow effects, animações CSS
- Badges contextuais, descrições ricas, hover interativo
- Botões inline APENAS para arquivos exibíveis pelo panel

### Regra de Exibibilidade
- Botão inline: apenas para HTML, SVG, MD, CSV, código
- Binários (.zip, .exe, .png, .pdf): apenas listar path, sem botão

## Pacote de Recursos — Code Development Pack

### Estrutura
```
code-dev-pack/
├── skills/          # 5 skills de desenvolvimento de código
├── hooks/           # 4 hooks de autoteste (2 criados, 2 planejados)
├── instructions/    # 3 instruções de qualidade
├── scripts/         # 1 script de autoteste
├── configs/         # 2 configs (teste + qualidade)
└── docs/            # 2 documentos (guia + auto-melhoria)
```

### Skills de Desenvolvimento
- `code-tdd` — Test-Driven Development (Red-Green-Refactor)
- `code-review` — Code review automático (checklist, severidade, formato)
- `code-refactor` — Refactoring assistido (code smells, catálogo de refactorings)
- `code-debug` — Debugging sistemático (método científico, técnicas, tipos de bugs)
- `code-test-gen` — Geração automática de testes (unit, integration, edge cases)

### Hooks de Autoteste
- `pre-write-quality.py` — Valida código antes de escrever (secrets, complexidade, testes)
- `post-write-test.py` — Roda testes após mudança (pytest/jest)

### Instruções
- `code-quality.md` — Padrões de qualidade (nomenclatura, estrutura, erros, testes, performance, segurança, git)
- `testing-standards.md` — Padrões de teste (tipos, estrutura, cobertura, mocking, fixtures, edge cases)
- `review-standards.md` — Padrões de code review (checklist, severidade, formato, regras)

### Autoteste
```bash
python scripts/autotest.py --all          # Testar todos os recursos
python scripts/autotest.py --skill <name> # Testar uma skill
python scripts/autotest.py --hook <name>  # Testar um hook
python scripts/autotest.py --resource <path>  # Testar um recurso
```

### Auto-Melhoria
- Feedback-driven: melhorias baseadas em feedback real do usuário
- Multi-device: sincronização entre 3 dispositivos via git
- Validação progressiva: raw → marked → validated → proactive
- Autoteste: cada recurso tem teste de reinterpretação

### Regras
- Nunca reusar padrões anteriores — cada recurso com identidade própria
- Não ter pressa — melhorar incrementalmente, testar cada mudança
- Autoteste sempre — toda melhoria deve ter um teste que valida
- Multi-device first — pensar em como o recurso funciona em 3 dispositivos

## Regras

- Nunca commitar segredos (API keys, tokens, .env). Use `.gitignore`.
- Preferir commits pequenos e descritivos.
- Antes de push, revisar diff.

## Licença

Uso pessoal.
