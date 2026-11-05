# /screen - Reconhecer e operar a tela via agent-desktop

Uso: /screen [app] [acao]

## Fluxo padrao
1. gent-desktop status (verificar permissoes)
2. gent-desktop snapshot --surface focused -i --compact (ou --app <nome>)
3. Analisar arvore a11y, identificar refs
4. Agir (click/type/set-value/press/scroll) com ref
5. Re-snapshot para verificar

## Exemplos
- /screen -> snapshot da janela focada
- /screen Notepad -> snapshot do Notepad
- /screen click @s...:e1 -> clicar no ref

## Cursor secundario
- Sessao ativa multi-agent: AGENT_DESKTOP_SESSION=run-1793905539455-30792-0
- Para subagente: --agent-id <id> ou AGENT_DESKTOP_AGENT_ID=<id>
- Cursor overlay: accent #4299FF, ripple on

## Regras
- Refs expiram apos mudanca de UI; re-snapshot.
- Headless por padrao; --headed apenas se usuario permitir input fisico.
- Retry apenas quando disposition.retry == safe.
