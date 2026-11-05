# /cursor - Gerenciar cursor overlay do agent-desktop

Uso: /cursor [enable|disable|status]

## Acoes
- /cursor enable -> gent-desktop cursor-overlay enable
- /cursor disable -> gent-desktop cursor-overlay disable
- /cursor status -> gent-desktop status (mostra cursor_overlay)

## Sessao
- Sessao multi-agent ativa: un-1793905539455-30792-0
- Para criar nova: gent-desktop session start --name <nome> --cursor --multi-agent
- Definir env: $env:AGENT_DESKTOP_SESSION = '<session_id>'

## Estilo padrao
- accent: #4299FF
- size: 1.0
- ripple: on
- highlight: on
- max_words: 6
