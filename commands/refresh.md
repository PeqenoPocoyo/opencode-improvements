# /refresh

Força um "refresh" completo da sessão OpenCode: recarrega PATH-ferramentas, re-lê configs globais, re-sincroniza o repo unificado, adota mudanças novas e re-verifica o status de hooks/skills. Equivalente a dizer "sync opencode" ampliado com verificação operacional.

Uso: /refresh

Passos (executar na ordem, reportar o que mudou):

1. **Ambiente/PATH** — restabelecer PATH para tooling via terminal:
   `$env:Path = "$env:LOCALAPPDATA\Programs\Git\cmd;$env:LOCALAPPDATA\Microsoft\WindowsApps;C:\Users\augusto.njunior\nodejs\node-v24.22.1-win-x64;$env:Path"`
   Confirme `git --version`, `node --version`, `python --version`.

2. **Re-lê config global** — leia:
   `~/.config/opencode/opencode.json`, `instructions/global.md`, `hook/hooks.yaml` e o índice de skills (`skills/_global/_skills-index.md` quando existir). Detecte edições manuais.

3. **Repo sync** — se houver repo OpenCode (`~/Documents/OpenCode`):
   - `git fetch origin` (`git status --short --branch`)
   - Merge `origin/main` em `device-<hostname>` se houver commits novos (autmerge).
   - Verificar `staging` (fetch) e avaliar promoções (marked→validated: 3+ usos, validated→proactive: 7+ usos, feedback negativo ≥2 → reverter para `raw`).
   - Push da branch device ao final.

4. **Adotar configs novas** — copie/adote em `~/.config/opencode/`:
   - skills novas/modificadas em `skills/` (exceto as já ativas) para `~/.config/opencode/skills/`
   - instruções (AGENTS.md, inline-artifacts.md, artifact-generation.md) quando alteradas
   - hooks/*.py novos/mudanças → `hook/scripts/improvements-*` e registre em `hooks.yaml`
   - artefatos novos → liste e ofereça abrir (`browser.preview`)

5. **Re-verificar hooks** — executar mentalmente `/hook-status` ou `~/.config/opencode/scripts/hook_status.py`:
   - plugin `opencode-yaml-hooks` listado?
   - hooks.yaml válido?
   - API Node ativa? (se não, `npm install -g opencode-yaml-hooks`)

6. **Hooks de log** — checar `~/.claude/logs/` para confirmar execução recente (session_start.log etc.).

7. **Relatório final** — reporte no formato:
   - "Pull: X commits novos (+N arquivos)" ou "Sincronizado (0)"
   - "Adotado: [lista de skills/hooks/instruções]"
   - "Staging: X aguardando; promoções: Y"
   - Erros (se houver) e como resolver.

Princípio: não bloquer a sessão por falta de ferramenta (fail-open). Se um passo falhar, reporte o erro, sugira solução e siga. Sempre preferir Python stdlib e configs de user-scope sobre administrador.

Uso livre: /refresh  (aceita variações: "refresh", "recarregar", "se atualize", "reload").