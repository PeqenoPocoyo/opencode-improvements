# Conectar ao Repositório Unificado — OpenCode Improvements

## Comando único (copie e cole no chat do OpenCode em qualquer dispositivo)

```
Conectar este OpenCode ao repositório unificado opencode-improvements no GitHub (https://github.com/PeqenoPocoyo/opencode-improvements.git). Verificar se git está instalado. Se não houver .git, inicializar e conectar ao remote. Fazer fetch. Se houver arquivos locais não rastreados, criar branch device-<nome-do-dispositivo>, commitar e pushar. Se não houver arquivos locais, fazer checkout main e pull. Após sync, verificar staging para recursos marcados aguardando validação, avaliar promoções (marked→validated→proactive) e adotar configs globais (skills, hooks, instruções, artefatos). Reportar status final com o que mudou, o que foi adotado e como contribuir.
```

## O que o agente vai fazer

1. Verificar se `git` está instalado
2. Se não houver `.git/`, inicializar e adicionar remote `origin`
3. Fazer `git fetch origin`
4. Se houver arquivos locais não rastreados → criar branch `device-<nome>`, commitar e pushar
5. Se não houver arquivos locais → `git checkout main && git pull origin main`
6. Verificar branch `staging` para recursos marcados aguardando validação
7. Avaliar promoções: `marked → validated` (3+ usos sem feedback negativo), `validated → proactive` (7+ usos)
8. Adotar configs globais (skills, hooks, instruções, artefatos)
9. Reportar status final com instruções para contribuir

## Ciclo de vida de um recurso

```
raw → marked → validated → proactive
```

| Estado | Descrição | Branch |
|---|---|---|
| `raw` | Recém-criado, não revisado | `device-*` |
| `marked` | Agente marcou como validado (provisório) | `staging` |
| `validated` | Validação final aprovada (sem feedback negativo) | `main` |
| `proactive` | Totalmente confiável, auto-aplicado | `main` |

- **Marked**: agente cria/edita recurso e marca como validado → commit em `staging`
- **Validated**: 3+ sessões de uso bem-sucedido sem feedback negativo → promove para `main`
- **Proactive**: 7+ sessões de uso bem-sucedido → auto-aplicado
- **Feedback negativo** (2+ ocorrências): reverter para `raw`, notificar dispositivo de origem

## Depois da primeira conexão

Em qualquer dispositivo já conectado, basta dizer no chat:

> **"sync opencode"**

E o agente (usando a skill `skills/opencode-sync/SKILL.md` do repo) fará o pull automático, verificará staging, avaliará promoções e reportará as mudanças.

## Scripts disponíveis no repo

| Script | Plataforma | Uso |
|---|---|---|
| `scripts/sync.ps1` | Windows | `.\scripts\sync.ps1` |
| `scripts/sync.sh` | Mac/Linux | `bash scripts/sync.sh` |
| `scripts/onboard-device.ps1` | Windows | `.\scripts\onboard-device.ps1 -DeviceName "notebook"` |

## Documentação completa

- `docs/SYNC.md` — guia detalhado de sincronização multi-dispositivo
- `skills/opencode-sync/SKILL.md` — skill de conexão, auto-sync e validação progressiva
- `validation.json` — rastreamento de validação de recursos
- `README.md` — visão geral do projeto e estrutura

## Repositório

https://github.com/PeqenoPocoyo/opencode-improvements
- Branch `main`: recursos validados e proativos
- Branch `staging`: recursos marcados (provisórios)
- Branch `device-*`: contribuições brutas de cada dispositivo
