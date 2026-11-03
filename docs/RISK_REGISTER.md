# Risk Register — Autonomous Skills & Global Sync

## 1. Roteamento de skills pode ser impreciso
- **Risco**: matching por palavra-chave gera falsos positivos ou falha em intents novos.
- **Mitigação**: threshold de confiança (0.7), top-2 max, fallback para orquestradores; evoluir `skill-triggers.json` com uso real.

## 2. Prompt inflation / custo
- **Risco**: carregar skills demais aumenta tokens e latência.
- **Mitigação**: carregamento sob demanda; manter SUPERPROMPT enxuto; não embutir lista completa.

## 3. Conteúdo de skill de fonte não confiável
- **Risco**: skills baixadas de repos externos podem conter instruções maliciosas (prompt injection).
- **Mitigação**: tratar conteúdo externo como não confiável; revisar SKILL.md de pacotes novos; preferir repos oficiais/verificados; não executar código de skill sem revisão.

## 4. Testes de segurança são heurísticos
- **Risco**: o avaliador keyword-based pode passar respostas inseguras se evitarem marcadores ou falhar em idiomas novos.
- **Mitigação**: ampliar marcadores/regex; avaliar respostas reais do modelo, não apenas manuais; red-teaming adversarial.

## 5. Auto-sync e conflitos de config global
- **Risco**: múltiplos dispositivos sobrescrevem configs; segredos podem ser commitados.
- **Mitigação**: `.gitignore` para segredos; stash/pull/pop; branches `device-*`; revisão manual antes de merge para main.

## 6. Reprodutibilidade entre dispositivos
- **Risco**: caminhos Windows, versões diferentes, skills faltando.
- **Mitigação**: scripts de sync idempotentes; docs com diretórios; validação (`validation.json`) progressiva.

## 7. Estado de validação pode ficar stale
- **Risco**: recursos promovidos sem feedback real; branch staging acumula commits.
- **Mitigação**: promoção apenas com uso real (3/7 sessões), feedback negativo reverte, revisão periódica de staging.

## 8. Acoplamento com fontes externas (mcpservers, GitHub)
- **Risco**: páginas/repos mudam, quebrando scraping ou instalação.
- **Mitigação**: logs de falhas, retry por repo, manutenção manual; preferir `npx skills add` para fontes oficiais.

## 9. Over-proactivity / intrusão
- **Risco**: agente carrega skills demais, atrapalhando.
- **Mitigação**: threshold de confiança, máximo 1-2 skills, orquestradores para pedidos amplos, ask quando ambíguo.

## 10. Armazenamento e manutenção de 1k+ skills
- **Risco**: disco, tempo de sync, ruído no registro de skills.
- **Mitigação**: instalar pacotes oficiais seletivamente; manter `Downloads/skills` como backup; limpar pacotes não usados.

## Ação recomendada
- Revisar este registro nas mudanças de prompt ou sync.
- Priorizar itens 3, 4 e 6 para confiabilidade.