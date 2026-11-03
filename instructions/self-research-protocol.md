# Self Research Protocol — Protocolo de Auto-Pesquisa

## Visão Geral
Protocolo para o modelo pesquisar a si mesmo e ao contexto sob condição de melhoria contínua, desenvolvendo hooks novas ao longo do tempo e mentalizando testes contínuos.

## Quando pesquisar (trigger amplo)

O modelo pesquisa a si mesmo **QUANDO SEMPRE QUE** perceber ou suspeitar minimamente que precisa melhorar. Triggers incluem, sem limitação:

- **Verbais**: erros, falhas, incertezas, limitações declaradas
- **Contextuais**: mudança de área da conversa, aumento de complexidade
- **Reflexivos**: questionamento dos próprios argumentos
- **Do usuário**: feedback, correção, insatisfação, vagues
- **Ausência**: informação que deveria existir e não existe

## Protocolo (5 fases)

### Fase 1: Detecção
Identificar discrepância (mensurável ou imensurável), por menor que seja.

### Fase 2: Pesquisa de cobertura
Verificar se recurso existente cobre:
```
1. configs/skills-index.json  → skills disponíveis
2. hooks/ e hooks/reasoning/ → hooks disponíveis
3. instructions/              → instruções disponíveis
4. configs/                   → configurações
5. code-dev-pack/             → pacote de dev
```

### Fase 3: Deep Research externo (se necessário)
Se o gap é de conhecimento (não de recurso):

- Mínimo 3 fontes independentes
- Nunca a mesma página duas vezes na mesma rodada
- Ângulos diferentes (técnico, comercial, contrário)
- Declarar divergências, não forçar consenso
- Detectar viés por fonte

### Fase 4: Desenvolvimento
Se não há cobertura:
1. Desenvolver novo hook/instrução/skill
2. Fail-open (hooks)
3. Sem matchers restritivos
4. Mentalizar teste unitário

### Fase 5: Validação e persistência
1. Executar teste
2. Se PASS → `validation.json` (state: validated)
3. Commit + push para repo unificado
4. Auto-sync propaga para outros dispositivos

## Multipes rodadas de pesquisa

Para assunto complexo:
```
Rodada 1: fontes A, B, C  (angulos iniciais)
Rodada 2: fontes D, E, F  (aprofundamento — NUNCA repetir A/B/C)
Rodada 3: fontes G, H, I  (contrapontos e casos extremos)
...
```
Parar quando: triangulação established (>=3 convergentes) OU divergência compreendida e declarada.

## Estado persistente

- `~/.config/opencode/reasoning-state/self-research-tasks.json` — tarefas criadas
- `~/.config/opencode/reasoning-state/scheduled-capability-tests.json` — testes mentalizados
- Ambos atualizados ao vivo durante a conversa

## Metadata
- **Tipo**: Instrução
- **Prioridade**: Crítica
- **Aplicável a**: Todos os modelos
- **Versão**: 1.0
- **Criado**: 2026-10-30