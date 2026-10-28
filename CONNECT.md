# Conectar ao Repositório Unificado — OpenCode Improvements

## Comando único (copie e cole no chat do OpenCode em qualquer dispositivo)

```
Conectar este OpenCode ao repositório unificado opencode-improvements no GitHub (https://github.com/PeqenoPocoyo/opencode-improvements.git). Verificar se git está instalado. Se não houver .git, inicializar e conectar ao remote. Fazer fetch. Se houver arquivos locais não rastreados, criar branch device-<nome-do-dispositivo>, commitar e pushar. Se não houver arquivos locais, fazer checkout main e pull. Após sync, listar o que mudou e quais configs globais (skills, hooks, instruções, artefatos) foram adotadas. Reportar status final com os passos para contribuir melhorias.
```

## O que o agente vai fazer

1. Verificar se `git` está instalado
2. Se não houver `.git/`, inicializar e adicionar remote `origin`
3. Fazer `git fetch origin`
4. Se houver arquivos locais não rastreados → criar branch `device-<nome>`, commitar e pushar
5. Se não houver arquivos locais → `git checkout main && git pull origin main`
6. Listar o que mudou e quais configs globais (skills, hooks, instruções, artefatos) foram adotadas
7. Reportar status final com instruções para contribuir

## Depois da primeira conexão

Em qualquer dispositivo já conectado, basta dizer no chat:

> **"sync opencode"**

E o agente (usando a skill `skills/opencode-sync/SKILL.md` do repo) fará o pull automático e reportará as mudanças.

## Scripts disponíveis no repo

| Script | Plataforma | Uso |
|---|---|---|
| `scripts/sync.ps1` | Windows | `.\scripts\sync.ps1` |
| `scripts/sync.sh` | Mac/Linux | `bash scripts/sync.sh` |
| `scripts/onboard-device.ps1` | Windows | `.\scripts\onboard-device.ps1 -DeviceName "notebook"` |

## Documentação completa

- `docs/SYNC.md` — guia detalhado de sincronização multi-dispositivo
- `README.md` — visão geral do projeto e estrutura

## Repositório

https://github.com/PeqenoPocoyo/opencode-improvements
