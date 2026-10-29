// artifact-detector.ts
// Detecta, na resposta do assistente, blocos de código/arquivos que podem ser
// visualizados no Review pane e converte-os em Artifact (balão clicável).
//
// Regras:
// - Não renderiza inline no meio do texto (evita quebrar o fluxo).
// - Retorna a lista de artifacts para ser empilhada ao FIM da resposta.
// - Cada artifact registra a skill que o gerou (quando informada).

import { writeFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { randomUUID } from "node:crypto";
import type { Artifact, ArtifactKind } from "./ArtifactBalloon";

export interface DetectedBlock {
  lang: string;
  code: string;
  // índice da ocorrência no texto (para ordenação)
  index: number;
}

// Linguagens que viram artifact visualizável.
const VISUAL_LANGS: Record<string, ArtifactKind> = {
  html: "html",
  htm: "html",
  svg: "svg",
  jsx: "react",
  tsx: "react",
  react: "react",
  vue: "react",
  md: "markdown",
  markdown: "markdown",
  mermaid: "mermaid",
  csv: "csv",
  tsv: "csv",
};

// Regex para blocos de código fenced.
const FENCED_RE = /```([a-zA-Z0-9+#-]*)\n([\s\S]*?)```/g;

export function detectBlocks(text: string): DetectedBlock[] {
  const out: DetectedBlock[] = [];
  let m: RegExpExecArray | null;
  FENCED_RE.lastIndex = 0;
  while ((m = FENCED_RE.exec(text)) !== null) {
    out.push({ lang: (m[1] || "").toLowerCase(), code: m[2], index: m.index });
  }
  return out;
}

export function isVisual(lang: string): boolean {
  return Object.prototype.hasOwnProperty.call(VISUAL_LANGS, lang);
}

export function kindFor(lang: string): ArtifactKind {
  return VISUAL_LANGS[lang] ?? "code";
}

// Diretório temporário para artifacts (server-local, consumido pelo Review pane).
const ARTIFACT_DIR = join(tmpdir(), "opencode-artifacts");

function ensureDir() {
  try {
    mkdirSync(ARTIFACT_DIR, { recursive: true });
  } catch {
    /* ignore */
  }
}

function extFor(kind: ArtifactKind): string {
  switch (kind) {
    case "html":
      return "html";
    case "svg":
      return "svg";
    case "react":
      return "jsx";
    case "markdown":
      return "md";
    case "mermaid":
      return "mmd";
    case "csv":
      return "csv";
    default:
      return "txt";
  }
}

function titleFor(kind: ArtifactKind, index: number): string {
  const base = {
    html: "Visualização HTML",
    svg: "Gráfico SVG",
    react: "Componente React",
    markdown: "Documento",
    mermaid: "Diagrama",
    csv: "Tabela",
    pdf: "PDF",
    image: "Imagem",
    code: "Código",
  }[kind];
  return index > 0 ? `${base} ${index + 1}` : base;
}

/**
 * Processa a resposta do assistente e retorna a lista de artifacts detectados.
 * Cada bloco visualizável é salvo em arquivo temporário (server-local) para que
 * o Review pane possa abri-lo via browser.preview.
 *
 * @param responseText  texto completo da resposta do assistente
 * @param skill         skill que gerou a resposta (para vincular ao artifact)
 */
export function extractArtifacts(
  responseText: string,
  skill?: string
): Artifact[] {
  ensureDir();
  const blocks = detectBlocks(responseText).filter((b) => isVisual(b.lang));
  const artifacts: Artifact[] = [];
  let counter = 0;

  for (const block of blocks) {
    const kind = kindFor(block.lang);
    const ext = extFor(kind);
    const id = randomUUID();
    const filename = `artifact-${id}.${ext}`;
    const path = join(ARTIFACT_DIR, filename);

    // Envolve HTML solto em documento completo se necessário.
    let content = block.code;
    if (kind === "html" && !/<html[\s>]/i.test(content)) {
      content = `<!doctype html><html><head><meta charset="utf-8"><title>Artifact</title></head><body>${content}</body></html>`;
    }
    if (kind === "svg" && !/^<svg/i.test(content.trim())) {
      // tenta extrair <svg>...</svg>
      const m = content.match(/<svg[\s\S]*<\/svg>/i);
      if (m) content = m[0];
    }

    try {
      writeFileSync(path, content, "utf8");
    } catch (err) {
      console.error("[artifact-detector] failed to write", path, err);
      continue;
    }

    artifacts.push({
      id,
      title: titleFor(kind, counter),
      kind,
      path,
      skill,
      size: Buffer.byteLength(content, "utf8"),
      createdAt: Date.now(),
    });
    counter++;
  }

  return artifacts;
}

/**
 * Remove os blocos visualizáveis do texto da resposta (opcional), para que
 * o markdown renderizado não duplique o código. Mantém um placeholder curto.
 */
export function stripVisualBlocks(text: string): string {
  return text.replace(FENCED_RE, (full, lang) => {
    if (!isVisual((lang || "").toLowerCase())) return full;
    return `\n> 📎 _Arquivo visualizável anexado ao fim da resposta._\n`;
  });
}