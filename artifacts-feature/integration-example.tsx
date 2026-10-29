// integration-example.tsx
// Exemplo de integração do Artifact Balloon no renderer de mensagens do OpenCode Desktop.
// Adapte imports/paths conforme a estrutura do repo.

import React, { useMemo } from "react";
import { extractArtifacts, stripVisualBlocks } from "./artifact-detector";
import { ArtifactStack } from "./ArtifactBalloon";

// Tipo mínimo de mensagem do assistente (adapte ao tipo real do repo).
interface AssistantMessage {
  id: string;
  text: string;
  skill?: string; // skill que gerou a resposta (opcional)
}

// Hook de preview do Review pane (wrapper da ferramenta browser.preview).
function useReviewPane() {
  return (path: string) => {
    // No desktop real, chamar a ferramenta RPC browser.preview.
    // Aqui, apenas log para o esboço.
    // eslint-disable-next-line no-console
    console.log("[review-pane] preview", path);
  };
}

export function AssistantMessageView({ message }: { message: AssistantMessage }) {
  const openInReviewPane = useReviewPane();

  // Detecta artifacts visualizáveis (salva arquivos temporários).
  const artifacts = useMemo(
    () => extractArtifacts(message.text, message.skill),
    [message.text, message.skill]
  );

  // Remove blocos visualizáveis do texto renderizado (evita duplicação).
  const displayText = useMemo(() => stripVisualBlocks(message.text), [message.text]);

  return (
    <div className="message assistant" data-message-id={message.id}>
      {/* Texto normal da resposta (markdown) — sem artifacts no meio */}
      <div className="message-body">
        {/* <Markdown content={displayText} /> */}
        <pre className="whitespace-pre-wrap text-[13px]">{displayText}</pre>
      </div>

      {/* Balões empilhados ao FIM da resposta */}
      <ArtifactStack
        artifacts={artifacts}
        onOpen={(a) => openInReviewPane(a.path)}
      />
    </div>
  );
}