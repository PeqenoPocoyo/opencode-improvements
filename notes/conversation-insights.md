# Insights da Conversa — 2026-10-28

## Contexto
Sessão de desenvolvimento de artefatos HTML e melhoria contínua do pacote de recursos do OpenCode.

## Artefatos Criados

| Artefato | Descrição | Destaque |
|---|---|---|
| acme-funnel-fix.html | Case de funil de exportação | Layout grid, 2 celulares |
| acme-funnel-creative.html | Versão criativa do case | Canvas particles, funnel bands, tilt 3D |
| orbital.html | Sandbox de gravidade generativa | Física newtoniana, fusão de corpos |
| synthesia.html | Step sequencer com áudio | Web Audio API, 8 vozes |
| mecatronica-4sem.html | Training hub mecatrônica | 5 abas, ferramentas, checklist |
| eletrica-tecnica.html | Training lab elétrica | 14 leis, 4 canvas, ferramentas |
| pc-builder-25d.html | Sandbox montagem PC 2.5D | 1000 peças, drag&drop |

## Lições Aprendidas

### 1. Funcionalidade é Crítica
- "Por que entregar um botão que não funciona?"
- Todo elemento de UI deve ter handler funcional.
- Inputs devem atualizar outputs.
- Links devem navegar.

### 2. Criatividade e Não-Repetição
- Nunca repetir o mesmo padrão de layout entre artefatos.
- Cada artefato deve ter identidade visual própria.
- Evitar templates genéricos (grid de cards, sidebar + main).

### 3. Congruência e Abrangência
- Funcionalidades devem ser congruentes com o contexto.
- Cobrir casos de uso reais, não apenas happy path.
- Incluir tratamento de erros e estados vazios.

### 4. Metodologias Adaptativas
- Diferentes partes podem usar metodologias diferentes.
- Não se limitar a uma única abordagem.

### 5. Auto-Upgrade
- O pacote de recursos deve ser auto-aprimorável.
- Melhorias devem ser generativas (criar novas capacidades).
- Teste de reinterpretação para validar melhorias.
- Marcar recursos com metadata de melhoria.

## Decisões de Design

1. **Cores**: Rotacionar paletas entre artefatos (cyan/violet, amber/red, green/teal, etc.)
2. **Layouts**: Rotacionar estruturas (hero+scroll, canvas+overlay, split, masonry, radial, timeline)
3. **Animações**: Sempre incluir pelo menos um efeito reativo ao mouse/scroll
4. **Tipografia**: Headlines grandes e ousadas, mix de pesos

## Problemas Identificados (e Corrigidos)

1. **Botões mortos** — corrigido com skill functional-ui
2. **Layouts repetitivos** — corrigido com skill creative-design
3. **Falta de auto-upgrade** — corrigido com skill self-upgrade
4. **Sem hooks de segurança** — corrigido com pre-tool-use-security.sh
5. **Sem instruções globais** — corrigido com AGENTS.md

## Próximos Passos

1. Testar os artefatos em diferentes dispositivos
2. Adicionar mais skills (a11y, performance, testing)
3. Criar hooks adicionais (PostToolUse, SessionStart)
4. Implementar CI/CD para validação de artefatos
5. Criar skill de "image-to-code" (OCR + análise visual)
6. Implementar sistema de versionamento de artefatos

## Metadata
- **Data**: 2026-10-28
- **Dispositivo**: desktop (Windows)
- **Branch**: main
- **Commits**: 2 (initial + cte-dashboard)
