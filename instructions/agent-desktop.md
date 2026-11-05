# Agent Desktop (computer-use) - Instrucoes globais

## Reconhecimento de tela automatico
- Sempre que o usuario pedir para ver/operar a tela, use o MCP gent-desktop.
- Fluxo padrao: desktop_snapshot (surface=focused ou window) -> analisar arvore a11y -> agir -> re-snapshot para verificar.
- Use --interactive-only e --compact para reduzir ruido.
- Refs (@snapshot_id:eN) expiram; re-snapshot apos mudanca de UI.

## Cursor secundario (overlay)
- Sessao ativa: AGENT_DESKTOP_SESSION=run-1793905539455-30792-0 (multi-agent).
- Cursor overlay habilitado (accent #4299FF, ripple on, size 1.0).
- Para subagentes, passe --agent-id <id> ou AGENT_DESKTOP_AGENT_ID.
- Cada agente distinto recebe cursor proprio.

## Comandos uteis
- status, permissions, version
- session start --cursor --multi-agent
- cursor-overlay enable/disable
- snapshot, find, get, is, screenshot
- click, type, set-value, press, scroll, drag
- launch, close-app, list-windows, focus-window
- clipboard-get/set, wait, batch
- list-notifications, dismiss-notification
