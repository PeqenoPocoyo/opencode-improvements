// ArtifactBalloon.tsx
// Componente de "balão" clicável que aparece ao FIM da resposta do assistente.
// Não é renderizado inline no meio do texto — evita quebrar o fluxo da conversa.
// Múltiplos artifacts empilham-se verticalmente (stack).
//
// Uso: <ArtifactStack artifacts={artifacts} onOpen={openInReviewPane} />

import React, { useState } from "react";

export type ArtifactKind =
  | "html"
  | "svg"
  | "react"
  | "markdown"
  | "pdf"
  | "image"
  | "csv"
  | "mermaid"
  | "code";

export interface Artifact {
  id: string;
  title: string;
  kind: ArtifactKind;
  path: string;          // caminho server-local do arquivo
  skill?: string;        // skill que gerou o artifact (ex: "web-artifacts-builder")
  size?: number;         // bytes (opcional)
  createdAt?: number;
}

const KIND_ICON: Record<ArtifactKind, string> = {
  html: "🌐",
  svg: "🎨",
  react: "⚛️",
  markdown: "📝",
  pdf: "📄",
  image: "🖼️",
  csv: "📊",
  mermaid: "🔀",
  code: "💻",
};

const KIND_LABEL: Record<ArtifactKind, string> = {
  html: "HTML",
  svg: "SVG",
  react: "React",
  markdown: "Markdown",
  pdf: "PDF",
  image: "Imagem",
  csv: "CSV",
  mermaid: "Mermaid",
  code: "Código",
};

interface ArtifactBalloonProps {
  artifact: Artifact;
  onOpen: (a: Artifact) => void;
  expanded?: boolean;
}

export function ArtifactBalloon({ artifact, onOpen, expanded }: ArtifactBalloonProps) {
  const [hover, setHover] = useState(false);
  return (
    <button
      type="button"
      onClick={() => onOpen(artifact)}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      className={[
        "group flex w-full items-center gap-3 rounded-xl border px-4 py-3 text-left transition-all",
        "border-v2-border-border-base bg-v2-background-bg-layer-01",
        "hover:border-v2-border-border-strong hover:bg-v2-background-bg-layer-02",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-v2-border-border-focus",
        expanded ? "shadow-[var(--v2-elevation-raised)]" : "",
      ].join(" ")}
      aria-label={`Abrir ${artifact.title} no painel de revisão`}
    >
      <span className="text-xl" aria-hidden="true">
        {KIND_ICON[artifact.kind]}
      </span>
      <div className="min-w-0 flex-1">
        <div className="truncate text-[13px] font-[530] text-v2-text-text-strong">
          {artifact.title}
        </div>
        <div className="flex items-center gap-2 text-[11px] text-v2-text-text-muted">
          <span>{KIND_LABEL[artifact.kind]}</span>
          {artifact.skill && (
            <>
              <span aria-hidden="true">·</span>
              <span className="truncate">via {artifact.skill}</span>
            </>
          )}
          {artifact.size != null && (
            <>
              <span aria-hidden="true">·</span>
              <span>{formatSize(artifact.size)}</span>
            </>
          )}
        </div>
      </div>
      <span
        className={[
          "shrink-0 text-v2-text-text-muted transition-transform",
          hover ? "translate-x-0.5" : "",
        ].join(" ")}
        aria-hidden="true"
      >
        ↗
      </span>
    </button>
  );
}

interface ArtifactStackProps {
  artifacts: Artifact[];
  onOpen: (a: Artifact) => void;
}

// Stack vertical de balões. Empilha quando há mais de 1.
export function ArtifactStack({ artifacts, onOpen }: ArtifactStackProps) {
  if (!artifacts || artifacts.length === 0) return null;
  return (
    <div
      className="mt-3 flex flex-col gap-2"
      data-component="artifact-stack"
      role="group"
      aria-label="Arquivos gerados"
    >
      {artifacts.map((a) => (
        <ArtifactBalloon key={a.id} artifact={a} onOpen={onOpen} />
      ))}
    </div>
  );
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}