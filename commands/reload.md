# /reload

Recarrega e re-sincroniza **somente leitura/contexto da sessão OpenCode** — sem merge, push, adoção de arquivos ou commits. Objetivo: atualizar o ambiente (PATH, configs, hooks, skills ativos) sem tocar no repo.

Uso: /reload
Variações: "reload", "recarregar", "reload session", "se atualize" (alias), "atualizar sessão"

Passos (rápido, fail-open — não abortar em falha):

1. **Ambiente** — restabelecer PATH e verificar toolchain (sem instalar nada):
   `$env:Path = "$env:LOCALAPPDATA\Programs\Git\cmd;$env:LOCALAPPDATA\Microsoft\WindowsApps;C:\Users\augusto.njunior\nodejs\node-v24.22.1-win-x64;$env:Path"`
   Verificar: `git --version`, `node --version`, `python --version`.

2. **Re-lê configs globais** (em ordem):
   - `~/.config/opencode/opencode.json` (plugins, providers, shell)
   - `instructions/global.md` (regras proativas, restrições, PATH nota)
   - `hook/hooks.yaml` (eventos ativos, plugins de hook)
   - `skills/_global/_skills-index.md` (catálogo de skills ativas — só re-resolve se existir)
   - `skills/` — listar pastas atuais (delta vs última verificação)

3. **Re-verificação de hooks** (leve — sem reinstall):
   - confirmar `opencode-yaml-hooks` em opencode.json
   - YAML válido em `hooks.yaml` (parse)
   - listar 10 eventos + contagens
   - api endpoints Node/pw/ git/ py resolved
   - checar last modified dos logs `~/.claude/logs/` (execution recently)

4. **Status local-only (sem operação remota)**:
   `git status --short --branch` no repo OpenCode (workspace) — para visualizar divergências entre device e main; NÃO faz fetch/pull/merge/push.

5. **Relatório mínimo** (5 linhas):
   - Toolchain: git X / node Y / python Z
   - Config: opencode.json ✅ | global.md ✅ | hooks.yaml ✅ (N eventos)
   - Hooks Status: [ativo<|channel|>inativo] — últimos logs: timestamp ou "<never>"
   - Skills globais ativas: N (catálogo)
   - Repo: branch `device-<hostname>` (X commits à frente do origin/device ± divergências)

Princípios: fail-open (erro reporta e segue), sem npm installs ou escrita destrutiva, sem commits/push. Leitura + verificação apenas. Indicador claro no final: "Reloaded ✔" com timestamp.

Uso livre: /reload — aceita variações: "reload", "reload session", "recarregar", "recarregar sessão".