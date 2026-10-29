# Artifact Balloon — Feature para OpenCode Desktop

## Objetivo

Exibir artifacts (HTML, SVG, React, Mermaid, CSV, Markdown) como **balões clicáveis empilhados ao fim da resposta**, em vez de inline no meio do texto. Clicar abre no Review pane.

## Arquivos

- `ArtifactBalloon.tsx` — componente React (balão + stack).
- `artifact-detector.ts` — detecção de blocos fenced visualizáveis + salvamento em arquivo temporário.
- `SKILL.md` — skill que documenta o comportamento.
- `integration-example.tsx` — exemplo de integração no renderer.

## Integração (resumo)

No renderer de mensagens (`route-6Ox02Vqv.js` / source TSX equivalente):

```tsx
import { extractArtifacts, stripVisualBlocks } from "./artifact-detector";
import { ArtifactStack } from "./ArtifactBalloon";

// dentro do componente de mensagem do assistente:
const artifacts = useMemo(
  () => extractArtifacts(message.text, message.skill),
  [message.text, message.skill]
);
const displayText = useMemo(
  () => stripVisualBlocks(message.text),
  [message.text]
);

return (
  <div className="message assistant">
    <Markdown content={displayText} />
    <ArtifactStack artifacts={artifacts} onOpen={(a) => browser.preview({ path: a.path })} />
  </div>
);
```

## Build

1. Clonar o repo do OpenCode Desktop.
2. Copiar `ArtifactBalloon.tsx` e `artifact-detector.ts` para `src/`.
3. Ajustar imports/paths conforme a estrutura do repo.
4. Rebuildar: `npm run build` → reempacotar `app.asar`.

## Notas

- Artifacts são salvos em `os.tmpdir()/opencode-artifacts/` (server-local, consumido pelo Review pane).
- Cada artifact registra a skill de origem (campo `skill`) para rastreabilidade.
- Empilhamento vertical automático quando há mais de 1.