---
name: self-upgrade
description: Protocolo de auto-aprimoramento do pacote de recursos do OpenCode. Coleta contexto, analisa gaps, propõe melhorias, implementa e testa. Use quando o usuário pedir "melhore", "aprimore", "upgrade", "auto-upgrade" ou quando identificar padrões de problema recorrentes.
improved: true
improved_at: "2026-10-28T00:00:00Z"
improved_by: "agent"
test_passed: true
test_scenario: "Executar auto-upgrade em repo com 3 skills, verificar que pelo menos 1 melhoria é proposta e testada"
---

# Self-Upgrade — Skill

> **Triggers (auto)**: self upgrade, self-upgrade

## Princípio Central
O agente deve ser capaz de **auto-aprimorar** seus recursos de forma **generativa** e **testável**.

## Gatilhos
- Usuário diz: "melhore", "aprimore", "upgrade", "auto-upgrade", "melhore o pacote"
- Identificação de padrão de problema recorrente
- Recurso existente desatualizado ou com bugs

## Processo de Auto-Upgrade

### Fase 1: Coleta (Scan)
```
1. Listar todos os recursos existentes:
   - skills/ (SKILL.md + recursos)
   - hooks/ (scripts de hook)
   - instructions/ (AGENTS.md, CLAUDE.md)
   - configs/ (settings.json, MCP, etc.)
   - notes/ (anotações)
   - docs/ (documentação)

2. Para cada recurso, registrar:
   - Nome, tipo, última modificação
   - Status: ativo, desatualizado, com bugs, incompleto
   - Dependências: quais outros recursos dependem dele
```

### Fase 2: Análise
```
Para cada recurso, verificar:
- [ ] Está atualizado com as práticas atuais?
- [ ] Tem bugs conhecidos?
- [ ] Falta funcionalidade?
- [ ] Há duplicação com outro recurso?
- [ ] A documentação está completa?
- [ ] Os testes passam?

Classificar por prioridade:
- P0: Bug crítico ou segurança
- P1: Funcionalidade faltante importante
- P2: Melhoria de qualidade
- P3: Nice-to-have
```

### Fase 3: Proposta
```
Gerar lista de melhorias priorizadas:
1. [P0] Corrigir bug X em skill Y
2. [P1] Adicionar funcionalidade Z em hook W
3. [P2] Melhorar documentação de config V
4. [P3] Criar novo recurso U

Para cada proposta, incluir:
- Justificativa
- Impacto esperado
- Risco de implementação
- Teste de validação
```

### Fase 4: Implementação
```
Para cada melhoria (em ordem de prioridade):
1. Criar branch: fix/improve-<recurso>
2. Implementar a melhoria
3. Atualizar metadata (improved: true, improved_at, etc.)
4. Commit com mensagem descritiva
```

### Fase 5: Teste de Reinterpretação
```
Para cada melhoria implementada:
1. Criar cenário de teste independente
2. Executar o teste
3. Registrar resultado: PASS ou FAIL
4. Se FAIL: reverter, analisar, tentar abordagem diferente
5. Se PASS: marcar como validado
```

### Fase 6: Validação
```
Verificar que:
- [ ] A melhoria é efetiva (teste passou)
- [ ] Não introduziu regressões
- [ ] A documentação está atualizada
- [ ] O metadata está correto
```

### Fase 7: Commit e Push
```
1. Commit final com todas as melhorias
2. Push para branch apropriada
3. Atualizar docs/changelog.md
```

## Teste de Reinterpretação — Detalhado

### O que é?
Um teste que valida se a melhoria realmente funcionou, executado em um contexto **independente** do que gerou a melhoria.

### Como criar?
1. Identificar o comportamento esperado após a melhoria.
2. Criar um cenário que exercita esse comportamento.
3. Verificar se o resultado corresponde ao esperado.
4. Se não corresponder, a melhoria não foi efetiva.

### Exemplo
```
Melhoria: Adicionada validação de input em hook de segurança.

Teste de Reinterpretação:
- Cenário: Enviar input malicioso (SQL injection) para o hook.
- Esperado: Hook bloqueia a operação.
- Resultado: Se bloqueou → PASS. Se não bloqueou → FAIL.
```

### Marcação de Recursos
Cada recurso melhorado deve ter no frontmatter (YAML) ou header (JSON/JS):
```yaml
improved: true
improved_at: "2026-10-28T00:00:00Z"
improved_by: "agent"
test_passed: true
test_scenario: "descrição do teste"
test_result: "PASS"
```

## Generatividade

### O que significa?
- Não apenas corrigir bugs, mas **criar novas capacidades**.
- Combinar recursos existentes de formas novas.
- Antecipar necessidades futuras.

### Exemplos de Melhoria Generativa
1. Skill de "functional-ui" não existia → criada do zero.
2. Hook de segurança não existia → criado com padrões OWASP.
3. Instrução de auto-upgrade não existia → criada como meta-skill.

### Como ser generativo?
- Perguntar: "O que o usuário vai precisar amanhã?"
- Perguntar: "Que combinação de recursos existentes cria algo novo?"
- Perguntar: "Que padrão de problema se repete e merece automação?"

## Checklist de Auto-Upgrade

- [ ] Scan completo dos recursos existentes
- [ ] Análise de gaps e bugs
- [ ] Propostas priorizadas (P0-P3)
- [ ] Implementação incremental
- [ ] Teste de reinterpretação para cada melhoria
- [ ] Metadata atualizada em cada recurso
- [ ] Changelog atualizado
- [ ] Commit e push

## Auto-Observacao Negativa (CRITICO)

### O que e?
O agente observa suas proprias limitacoes, erros e incertezas e as registra
como feedback negativo para auto-melhoria, **sem depender do usuario**.

### Como funciona?
1. O agente gera uma resposta
2. O hook self-observation.py analisa a resposta
3. Se padroes negativos sao detectados, registra em validation.json
4. Se 2+ observacoes negativas -> recurso e revertido para raw
5. O agente analisa o gap -> implementa melhoria
6. Autoteste valida -> marca como melhorado
7. Commit + Push -> Sync para outros dispositivos

### Padroes detectados:
- **Erro admissao**: "nao funciona", "falhou", "bug", "erro", "quebrou"
- **Incerteza**: "nao tenho certeza", "talvez", "possivelmente", "acho que"
- **Retrabalho**: "vou corrigir", "ajustar", "refazer", "tentar novamente"
- **Limitacao**: "nao consigo", "nao e possivel", "limitacao", "nao suporta"

### Regra de ouro:
> Se o agente admite uma limitacao, ela DEVE ser registrada como feedback negativo.
> O ciclo de auto-melhoria nao depende do usuario — e autonomo.

## Feedback-Driven Improvement (CRITICO)

### O que e?
Melhoria baseada em feedback real do usuario durante o uso. Nao e melhoria teorica — e melhoria que acontece quando o usuario diz "isso nao funciona" ou "pode ser melhor".

### Como funciona?
1. **Usuario usa o recurso** (skill, hook, instrucao, artefato)
2. **Usuario da feedback** (positivo, negativo, ou sugestao de melhoria)
3. **Agente analisa o feedback** e identifica o gap
4. **Agente implementa a melhoria** no recurso
5. **Agente testa** se a melhoria resolve o feedback
6. **Agente marca** o recurso com metadata de melhoria
7. **Agente commita e pusha** para o repositorio

### Exemplos de feedback-driven improvement:
- Usuario: "o balao de artifacts e generico" → Agente: adiciona 10 regras de criatividade
- Usuario: "o botao de explorer nao funciona" → Agente: adiciona regra de exibibilidade
- Usuario: "nao desperta meu interesse" → Agente: redesign com hero dramático, urgência, gamificação
- Usuario: "ta todo bugado" → Agente: corrige layout, animações, interatividade

### Regra de ouro:
> Se o usuario deu feedback, a melhoria DEVE ser implementada no pacote de recursos.
> Nao apenas respondida na conversa — implementada no repo.

## Multi-Device Contribution Flow

### Cenario: 3 dispositivos em momentos diferentes
```
Dispositivo A (manha)     Dispositivo B (tarde)     Dispositivo C (noite)
       |                        |                        |
   usa + feedback            usa + feedback          usa + feedback
       |                        |                        |
   melhora recurso           melhora recurso         melhora recurso
       |                        |                        |
   commit + push staging     commit + push staging    commit + push staging
       |                        |                        |
       v                        v                        v
   origin/staging  <--------  origin/staging  -------->  origin/staging
       |                        |                        |
       v                        v                        v
   origin/main (promovido quando 3+ usos sem feedback negativo)
```

### Fluxo de contribuicao:
1. **Dispositivo usa recurso** → identifica gap ou oportunidade
2. **Agente melhora o recurso** → implementa a melhoria
3. **Agente marca como `marked`** → commit em `staging`
4. **Outros dispositivos recebem** → via auto-sync (a cada hora)
5. **Uso bem-sucedido** → incrementa `usage_count`
6. **3+ usos sem feedback negativo** → promove para `main` (estado `validated`)
7. **7+ usos sem feedback negativo** → promove para `proactive` (auto-aplicado)

### Regra de feedback negativo:
- 2+ feedbacks negativos → reverter para `raw`, notificar dispositivo de origem
- O dispositivo de origem pode corrigir e re-marcar

## Metadata
- **Categoria**: Meta/DevOps
- **Prioridade**: Crítica
- **Aplicável a**: Todo o pacote de recursos
- **Dependências**: Nenhuma (é a skill raiz)
- **Versão**: 2.0
- **Melhorado**: 2026-10-28 (feedback-driven improvement, multi-device contribution flow)

## Anti-padrões (auto-evoluídos)

- ❌ Usar a skill sem validar o contexto de entrada.
- ❌ Ignorar os triggers documentados e forçar ativação manual.
- ❌ Entregar resultado sem verificar se todos os elementos são funcionais.
- ❌ Repetir o mesmo padrão de saída sem adaptar ao domínio.

> **Skill Evolver**: score 66/100 · evoluída em 2026-10-31T02:34:06.373355+00:00Z · versão evolver-1.0
