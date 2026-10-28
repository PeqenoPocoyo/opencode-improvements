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

## Regras

- Nunca commitar segredos (API keys, tokens, .env). Use `.gitignore`.
- Preferir commits pequenos e descritivos.
- Antes de push, revisar diff.

## Licença

Uso pessoal.
