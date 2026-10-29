---
name: opencode-sync
description: Conecta este dispositivo ao repositório unificado opencode-improvements no GitHub. Faz onboarding (se novo), sincronização automática, adoção de configs globais, validação progressiva de recursos (marked → validated → proactive) e contribuição de melhorias. Use quando o usuário disser "conectar ao repo", "sync opencode", "adotar configs globais", ou quando precisar sincronizar este OpenCode com o repositório unificado.
---

# OpenCode Sync — Conexão, Auto-Sync e Validação Progressiva

## Objetivo

Conectar este dispositivo ao repositório `https://github.com/PeqenoPocoyo/opencode-improvements.git`,
sincronizar automaticamente, adotar configs globais, validar recursos progressivamente
(marked → validated → proactive) e permitir contribuição de melhorias.

---

## Ciclo de vida de um recurso

```
raw → marked → validated → proactive
  │      │         │           │
  │      │         │           └── Auto-aplicado, confiável
  │      │         └── Sem feedback negativo em 3+ sessões
  │      └── Agente revisou e marcou como validado (provisório)
  └── Recém-criado, não revisado
```

### Estados

| Estado | Descrição | Branch |
|---|---|---|
| `raw` | Recém-criado, não revisado | `device-*` |
| `marked` | Agente marcou como validado (provisório) | `staging` |
| `validated` | Validação final aprovada (sem feedback negativo) | `main` |
| `proactive` | Totalmente confiável, auto-aplicado | `main` |

### Regras de promoção

- `raw → marked`: Agente revisa e aprova (commit em `staging`)
- `marked → validated`: 3+ sessões de uso bem-sucedido sem feedback negativo
- `validated → proactive`: 7+ sessões de uso bem-sucedido sem feedback negativo
- **Feedback negativo** (2+ ocorrências): reverter para `raw`, notificar dispositivo de origem

### Rastreamento

O arquivo `validation.json` na raiz do repo rastreia o estado de cada recurso:
- Estado atual, data de marcação, dispositivo de origem
- Contagem de feedback negativo e uso bem-sucedido
- Threshold de promoção

---

## Passos de execução (seguir na ordem)

### 1. Verificar/instalar git
- Rodar `git --version`. Se não existir, avisar o usuário que precisa instalar o Git.

### 2. Verificar se já está conectado
- Se existir `.git/` na pasta atual ou em `~/Documents/OpenCode` ou `~/OpenCode`, verificar se o remote é o repo correto:
  ```
  git remote get-url origin
  ```
- Se for `https://github.com/PeqenoPocoyo/opencode-improvements.git`, pular para o passo 4 (auto-sync).
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

### 4. Auto-Sync (pull das últimas mudanças)
- `git checkout main`
- `git pull origin main`
- Se houver conflito, resolver ou avisar o usuário
- Reportar o que mudou: `git log --oneline -5` e listar arquivos novos/modificados

### 5. Verificar staging (recursos marcados aguardando validação)
- `git fetch origin`
- Se existir branch `staging`, verificar se há recursos novos:
  - `git log staging --oneline -5`
  - Se houver recursos em staging, avaliar se podem ser promovidos para `main`
- Para cada recurso em staging:
  - Verificar `validation.json` para o estado atual
  - Se `usage_count >= promotion_threshold` e `feedback_negative == 0`:
    - Promover: merge para `main`, atualizar estado para `validated` ou `proactive`
  - Se `feedback_negative >= 2`:
    - Reverter: remover de staging, voltar para `raw`, notificar dispositivo de origem

### 6. Adotar configs globais
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
🔬 Recursos em staging: X (Y prontos para promoção)
💡 Para contribuir: edite, commite e push na main ou staging
```

### 7. Contribuir melhorias (auto-push)
Quando o agente cria, edita ou melhora um recurso E valida que funciona:

1. **Criar/editar o recurso** no diretório apropriado
2. **Marcar como validado**: adicionar/atualizar entrada em `validation.json`:
   ```json
   {
     "path/to/resource": {
       "state": "marked",
       "marked_date": "YYYY-MM-DD",
       "marked_by": "device-<nome>",
       "feedback_negative": 0,
       "usage_count": 0,
       "promotion_threshold": 3,
       "notes": "Descrição da validação"
     }
   }
   ```
3. **Commitar em staging**:
   ```
   git checkout staging
   git add -A
   git commit -m "mark: <recurso> validado por device-<nome>"
   git push origin staging
   ```
4. **Registrar uso bem-sucedido**: quando o recurso for usado sem problemas:
   - Incrementar `usage_count` em `validation.json`
   - Se `usage_count >= promotion_threshold` e `feedback_negative == 0`:
     - Promover para `main`: `git checkout main && git merge staging --no-edit && git push origin main`
     - Atualizar estado para `validated` (ou `proactive` se >= 7 usos)
5. **Registrar feedback negativo**: se o recurso falhar ou causar problemas:
   - Incrementar `feedback_negative` em `validation.json`
   - Se `feedback_negative >= 2`:
     - Reverter: remover de staging, voltar para `raw`
     - Commitar: `git commit -m "revert: <recurso> por feedback negativo"`
     - Notificar dispositivo de origem

### 8. Auto-sync contínuo
Para manter sincronização automática entre dispositivos:

**No início de cada sessão:**
- Executar passos 4 e 5 (auto-sync + verificar staging) silenciosamente
- Se houver mudanças, reportar ao usuário

**No fim de cada sessão (ou quando um recurso é validado):**
- Se houver recursos marcados como validados, commitar e pushar em staging
- Se houver recursos prontos para promoção, promover para main

**Scripts agendados (opcional):**
- Windows: Agendador de Tarefas → `scripts/sync.ps1` a cada hora
- Mac/Linux: Cron → `bash scripts/sync.sh` a cada hora

---

## Feedback-Driven Improvement (OBRIGATÓRIO)

Quando o usuário der feedback sobre um recurso (positivo, negativo ou sugestão):

1. **Analisar o feedback** e identificar o gap
2. **Implementar a melhoria** no recurso (skill, hook, instrução, config, artefato)
3. **Testar** se a melhoria resolve o feedback
4. **Marcar** o recurso com metadata de melhoria
5. **Commitar e pushar** para o repositório
6. **Reportar** ao usuário o que foi melhorado

### Exemplos de feedback-driven improvement:
- "balão de artifacts é genérico" → Adicionar 10 regras de criatividade
- "botão de explorer não funciona" → Adicionar regra de exibibilidade
- "não desperta meu interesse" → Redesign com hero dramático, urgência, gamificação
- "ta todo bugado" → Corrigir layout, animações, interatividade

### Regra de ouro:
> Se o usuário deu feedback, a melhoria DEVE ser implementada no pacote de recursos.
> Não apenas respondida na conversa — implementada no repo.

## Balões de Artifacts Criativos (OBRIGATÓRIO)

Os balões de artifacts ao final da resposta devem ser **criativos e contextuais**:
1. Paleta contextual por tipo (HTML=indigo, SVG=emerald, MD=amber, CSV=sky, código=violet)
2. Layout dinâmico: grid 2 colunas para 2+ artifacts, card único para 1
3. Animações CSS: float, blink, shimmer, slide-up, hover (translateY + shadow colorida)
4. Glassmorphism: gradiente + border semi-transparente + backdrop-filter
5. Glow effects: radial-gradient blur atrás dos ícones
6. Badges contextuais: tags por tipo com cores temáticas
7. Descrições ricas: nome + descrição curta + tipo + origem
8. Hover interativo: card levanta + shadow colorida

### Regra de exibibilidade para botões inline:
- Gerar botão inline APENAS para arquivos que o panel pode exibir (HTML, SVG, MD, CSV, código)
- Não gerar botão para binários (.zip, .exe, .png, .pdf, .mp3) — apenas listar o path

## Auto-Observacao Negativa (CRITICO)

O agente observa suas proprias limitacoes e as registra como feedback negativo:

1. Hook `self-observation.py` detecta padroes negativos automaticamente
2. Registra em `validation.json` (feedback_negative++)
3. Se 2+ observacoes negativas -> reverter para raw
4. Agente analisa o gap -> implementa melhoria
5. Autoteste valida -> marca como melhorado
6. Commit + Push -> Sync para outros dispositivos

### Padroes detectados:
- Erro admissao, Incerteza, Retrabalho, Limitacao

### Regra de ouro:
> Se o agente admite uma limitacao, ela DEVE ser registrada como feedback negativo.
> O ciclo de auto-melhoria nao depende do usuario — e autonomo.

## Regras importantes

- **Nunca sobrescrever mudanças locais sem avisar** — sempre stash/pull/pop
- **Nunca commitar segredos** — verificar .gitignore
- **Sempre reportar** o que foi sincronizado e o que mudou
- **Validação é progressiva** — não promover para main sem uso real sem feedback negativo
- **Feedback negativo reverte** — recursos com 2+ feedbacks negativos voltam para raw
- **Se algo falhar**, não abortar silenciosamente — explicar o erro e sugerir solução

---

## Comando único para o usuário

O usuário pode digitar em qualquer dispositivo:
> "conectar ao repo unificado" ou "sync opencode"

E o agente executará todos os passos acima automaticamente.

## Scripts auxiliares no repo

- `scripts/sync.ps1` — sync Windows
- `scripts/sync.sh` — sync Mac/Linux
- `scripts/onboard-device.ps1` — onboarding Windows
- `docs/SYNC.md` — documentação completa
- `validation.json` — rastreamento de validação
