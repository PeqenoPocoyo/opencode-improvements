# Adoção de configs globais — device-W1500CTE85RRJ93 (2026-10-29)

Registro da adoção de recursos do repositório unificado no OpenCode global
(`C:\Users\augusto.njunior\.config\opencode\`).

## Contexto do ambiente desta máquina

- Sem permissão de administrador.
- Sem Node.js / npm / Docker.
- Python disponível (stdlib; PyYAML instalado via pip --user).
- Git instalado em `AppData\Local\Programs\Git` (fora do PATH padrão do shell).
- winget disponível em `AppData\Local\Microsoft\WindowsApps` (fora do PATH padrão do shell).

## Correção aplicada

- `validation.json` (main): JSON inválido — recursos na raiz sem o wrapper
  `"resources"`, com uma chave `}` extra no final (depth -1). Corrigido
  localmente no branch do dispositivo para alinhar com a estrutura da branch
  `staging`. ** Pendente: mesclar a correção na main (curador). **

## Skills adotadas (13) → `.config/opencode/skills/`

| Skill | Estado (validation.json) |
|---|---|
| artifact-balloon | proactive |
| artifact-creator | validated |
| artifacts-feature | validated* |
| creative-design | validated |
| functional-ui | validated |
| inline-artifacts | proactive |
| opencode-sync | validated |
| self-upgrade | validated |
| code-tdd | marked (code-dev-pack, 0 usos) |
| code-review | marked (code-dev-pack) |
| code-refactor | marked (code-dev-pack) |
| code-debug | marked (code-dev-pack) |
| code-test-gen | marked (code-dev-pack) |

* `artifacts-feature` validada em `artifacts-feature/` do repo (pacote TSX).

Preservado: skill global `agent-browser` (versão local divergente e mais completa que a do repo — 295 linhas de diferença).

## Hooks adotados (10) → `.config/opencode/hook/scripts/improvements-*`

- session_start.py, session_end.py, subagent_start.py, subagent_stop.py,
  notification_handler.py (logging, fail-open)
- validate_bash_command.py (bloqueia rm -rf /, curl|bash, chmod 777...)
- validate_sensitive_write.py (alerta .env/.pem/.key..., não bloqueia)
- pre-tool-use-security.sh, cdp-pre-write-quality.py, cdp-post-write-test.py

Registrados em `hook/hooks.yaml` (eventos: session.created, session.idle,
tool.before.write/edit/multiedit, tool.before.bash). Encoding do hooks.yaml
normalizado para UTF-8 (original tinha bytes cp1252). Backup:
`hooks.yaml.bak-pre-adoption`.

## Instruções adotadas (3) → `.config/opencode/instructions/`

- AGENTS.md (proactive), inline-artifacts.md (proactive), artifact-generation.md (validated)

Regras proativas aplicadas também em `instructions/global.md` (seção
"Repositório Unificado opencode-improvements").

## Artefatos

20 HTMLs + 1 .cmd em `artefatos/` disponíveis no workspace para abertura no
Review pane (regra de exibibilidade: HTML listado com botão; .zip sem botão).

## Pendências para o curador (device-cesar)

1. Merge da correção do `validation.json` na main.
2. `skills/agent-browser` — avaliar qual versão vence (repo vs global desta máquina).
3. code-dev-pack: 12 recursos em `marked` com 0 usos — aguardando validação.
