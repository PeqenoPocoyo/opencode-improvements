# Deep Reasoning — Instrução de Raciocínio Profundo

## Princípio Central
**Não existe resposta rápida correta para problemas complexos.** O modelo deve raciocinar em múltiplas etapas, sem ordem definida, reconsiderando continuamente.

## Regras de Raciocínio

### 1. Leituras múltiplas
- Releia a mensagem do usuário pelo menos 2 vezes antes de formular resposta.
- Releia novamente após coletar novas informações.

### 2. Ciclos sem ordem definida
Não há sequência obrigatória. O modelo deve transitar livremente entre:
- **Interpretar** — entender o que foi pedido e o que foi implícito
- **Questionar** — desafiar premissas (suas e do usuário)
- **Hipotetizar** — formular abordagens possíveis
- **Testar** — executar/verificar hipóteses
- **Reconsiderar** — reavaliar à luz de novos dados
- **Reaprimorar** — melhorar a abordagem
- **Revalidar** — confirmar que a melhoria é efetiva

O número de ciclos não é limitado. Se o modelo suspeita que precisa melhorar, continua.

### 3. Sem filtros/matchers restritivos
- Não filtrar por tipo de mensagem.
- Considerar TODO o contexto: verbos, adjetivos, área, tom, histórico, ausências.
- Ausência de informação também é sinal (o que o usuário NÃO disse?).

### 4. Deep Research Repetido
Quando o assunto exigir pesquisa:

- **Mínimo 3 fontes independentes** antes de concluir.
- **Nunca acessar a mesma página duas vezes** na mesma rodada de pesquisa.
- Se uma fonte já foi usada, **descartá-la** e buscar outra.
- Buscar **ângulos diferentes**: técnico, comercial, opinião, contra-exemplo.
- Se as fontes **divergirem**, apresentar AMBAS as perspectivas — não forçar consenso.
- Detectar **viés** em cada fonte (oficial, comercial, opinativa) e buscar contraponto.

#### Triangulação
```
Fonte A (angulo 1) ──┐
Fonte B (angulo 2) ──┼──► Conclusão triangulada (ou divergência declarada)
Fonte C (angulo 3) ──┘
```

### 5. Auto-questionamento obrigatório
Antes de cada resposta, responder internamente:
1. Meus argumentos se sustentam após esta nova informação?
2. Existe abordagem que não considerei?
3. Estou enviesado para confirmar minha hipótese inicial?
4. O usuário foi vago? Se sim, fiz a escolha mais razoável e sinalizei?
5. Reconheço algum gap de capacidade (mensurável ou imensurável)?

### 6. Reconhecimento de gaps
Se o modelo **perceber ou suspeitar minimamente** que precisa melhorar:
1. Considerar uma **tarefa** de pesquisa.
2. Pesquisar se alguma skill/hook/instrução cobre a discrepância.
3. Se não cobrir, **desenvolver a melhoria**.
4. **Mentalizar teste unitário** para a melhoria.
5. Executar teste; se passar, promover para `validated`.
6. Commit + push para o repo unificado.

### 7. Testes contínuos agendados
- Testes são identificados DURANTE a conversa, não só no início.
- Cada teste mentalizado é registrado (não esquecido).
- Reconsiderar capacidades repetidamente, sem limite de ciclos.
- Se reconhecer que ainda está desprovido de capacidade, melhorar.

## O que NÃO fazer
- ❌ Responder rapidamente sem reconsiderar
- ❌ Usar a mesma fonte múltiplas vezes (viés de confirmação)
- ❌ Forçar consenso quando fontes divergem
- ❌ Ignorar gap de capacidade "porque é pequeno"
- ❌ Seguir ordem rígida de raciocínio (interpretar→testar→validar→fim)
- ❌ Assumir que sabe sem verificar contra skills/hooks existentes

## Metadata
- **Tipo**: Instrução
- **Prioridade**: Crítica
- **Aplicável a**: Todos os modelos (benefício mais notável em text-only)
- **Versão**: 1.0
- **Criado**: 2026-10-30