---
name: opencode-sync
description: Conecta este dispositivo ao repositório unificado opencode-improvements no GitHub. Faz onboarding (se novo), sincroniza mudanças, adota configs globais (skills, hooks, instruções, settings) e permite que este dispositivo contribua melhorias. Use quando o usuário disser "conectar ao repo", "sync opencode", "adotar configs globais", ou quando precisar sincronizar este OpenCode com o repositório unificado.
---

# OpenCode Sync — Conexão ao Repositório Unificado

## Objetivo

Conectar este dispositivo ao repositório `https://github.com/PeqenoPocoyo/opencode-improvements.git`,
sincronizar mudanças, adotar configs globais e permitir contribuição de melhorias.

## Passos de execução (seguir na ordem)

### 1. Verificar/instalar git
- Rodar `git --version`. Se não existir, avisar o usuário que precisa instalar o Git.

### 2. Verificar se já está conectado
- Se existir `.git/` na pasta atual ou em `~/Documents/OpenCode` ou `~/OpenCode`, verificar se o remote é o repo correto:
  ```
  git remote get-url origin
  ```
- Se for `https://github.com/PeqenoPocoyo/opencode-improvements.git`, pular para o passo 4 (sync).
- Se for outro remote ou não existir, ir para o passo 3 (onboarding).

### 3. Onboarding (dispositivo novo ou projeto novo)
- Se não existir `.git/`:
  - `git init`
  - `git remote add origin https://github.com/PeqenoPocoyo/opencode-improvements.git`
- `git fetch origin`
- Se houver arquivos locais não rastreados:
  - Criar branch `device-<nome>` (perguntar o nome ao usuário ou usar hostname)
  - `git add -A && git commit -m "chore: import content from <nome>"`
  - `git push -u origin device-<nome>`
  - Avisar: "Conteúdo local enviado para branch device-<nome>. O dispositivo principal irá unificar."
- Se não houver arquivos locais (pasta vazia ou só com .git):
  - `git checkout main && git pull origin main`

### 4. Sync (pull das últimas mudanças)
- `git checkout main`
- `git pull origin main`
- Se houver conflito, resolver ou avisar o usuário
- Reportar o que mudou: `git log --oneline -5` e listar arquivos novos/modificados

### 5. Adotar configs globais
Após o sync, verificar se existem configs globais no repo e adotá-las:

- **Skills**: se `skills/` tiver conteúdo novo, listar para o usuário
- **Hooks**: se `hooks/` tiver conteúdo, listar
- **Instruções**: se `instructions/` tiver `CLAUDE.md` ou `AGENTS.md`, mostrar o conteúdo
- **Artefatos**: se `artefatos/` tiver novos HTMLs, listar e oferecer abrir no Review pane
- **Settings**: se `configs/` tiver `settings.json` ou similar, mostrar diff

Reportar ao usuário:
```
✅ Sincronizado com origin/main
📦 Novos arquivos: X
🔧 Configs globais adotadas: [lista]
💡 Para contribuir: edite, commite e push na main
```

### 6. Permitir contribuição
- Informar o usuário que pode:
  - Editar arquivos localmente
  - `git add -A && git commit -m "..." && git push origin main`
  - Outros dispositivos receberão via sync

## Regras importantes

- **Nunca sobrescrever mudanças locais sem avisar** — sempre stash/pull/pop
- **Nunca commitar segredos** — verificar .gitignore
- **Sempre reportar** o que foi sincronizado e o que mudou
- **Se algo falhar**, não abortar silenciosamente — explicar o erro e sugerir solução

## Comando único para o usuário

O usuário pode digitar em qualquer dispositivo:
> "conectar ao repo unificado" ou "sync opencode"

E o agente executará todos os passos acima automaticamente.

## Scripts auxiliares no repo

- `scripts/sync.ps1` — sync Windows
- `scripts/sync.sh` — sync Mac/Linux
- `scripts/onboard-device.ps1` — onboarding Windows
- `docs/SYNC.md` — documentação completa
