#!/usr/bin/env python3
"""
Assumption Probe — Questionamento GENÉRICO de Premissas (auto-expansível).

NÃO é vinculada a domínio. Funciona para qualquer assunto.

Princípio: o modelo frequentemente interpreta termos/conceitos de forma
RESTRITA, assumindo a primeira interpretação que vem à cabeça. Esta hook
força o modelo a questionar SUA premissa antes de assumir.

Ela NÃO sabe o que os termos significam. Ela apenas:
1. Extrai todo termo candidato do contexto (substantivos, siglas, compostos).
2. Pergunta: "que premissa você está assumindo? é a única? qual o subset?"
3. Aprende: registra termos + interpretações assumidas, e quando o modelo
   repete uma interpretação RESTRITA, marca como "viés conhecido".

Auto-expansão: o mapa de ambiguidade cresce com o uso, sem depender de
lista fixa ou sufixos.

Sem matchers: dispara em qualquer contexto.
Fail-open: qualquer erro resultado em saida 0.
"""
import sys
import json
import os
import re
import unicodedata
from datetime import datetime

# Estado que cresce sozinho
STATE_FILE = os.path.expanduser("~/.config/opencode/reasoning-state/assumption-probes.json")
REPO_SEED = os.path.join(os.getcwd(), "configs", "assumption-probes.json")

STOPWORDS_PT = {
    "para", "como", "sobre", "essa", "esse", "isso", "aqui", "ali", "mas",
    "porque", "então", "também", "quando", "onde", "qual", "quais", "muito",
    "mais", "menos", "estou", "está", "estão", "fazer", "feito", "feita",
    "seja", "sendo", "foi", "será", "deve", "poderia", "preciso", "quero",
    "gostaria", "temos", "tudo", "todos", "todas", "cada", "outro", "outra",
    "mesmo", "mesma", "assim", "ainda", "depois", "antes", "desde", "até",
    "the", "and", "for", "with", "this", "that", "from", "have", "has",
    "you", "your", "not", "are", "was", "were", "can", "could", "would",
}

def normalize(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()

def load_state():
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    # Estrutura inicial VAZIA de viés — cresce com o uso
    return {
        "known_terms": {},      # termo -> {interpretations_assumed: [], narrow_bias_count: N}
        "narrow_bias_watch": {}, # termo -> quantas vezes foi interpretado de forma restrita
        "round": 0,
    }

def save_state(state):
    try:
        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def extract_candidate_terms(text):
    """Extrai termos candidatos a interpretação (genérico)."""
    # Remove código/urls para não poluir
    text = re.sub(r'https?://\S+', ' ', text)
    text = re.sub(r'```[\s\S]*?```', ' ', text)
    # Palavras 4+ letras (inclui acentos)
    words = re.findall(r'\b[a-zA-Záàâãéêíóôõúçñ]{4,}\b', text)
    # Siglas 2-5 letras maiúsculas (CLP, MES, IIoT, ERP...)
    acron = re.findall(r'\b[A-Z]{2,5}\b', text)
    # Termos compostos (2 palavras maiúsculas ou com número: Industria 4.0)
    compound = re.findall(r'\b[A-Za-záàâãéêíóôõúçñ]+\s+\d+(\.\d+)?\b', text)

    candidates = []
    for w in words:
        wn = normalize(w)
        if wn not in {normalize(s) for s in STOPWORDS_PT}:
            candidates.append(w)
    candidates.extend(acron)
    candidates.extend([c.strip() for c in compound])
    return list(dict.fromkeys(candidates))

def get_text(data, raw):
    if isinstance(data, dict):
        return data.get("prompt") or data.get("message") or data.get("text") or raw
    return raw

def main():
    try:
        raw = sys.stdin.read()
        if not raw:
            sys.exit(0)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = None

        text = get_text(data, raw)
        state = load_state()
        state["round"] += 1

        candidates = extract_candidate_terms(text)

        # Filtra: mantém termos que são potencialmente categorias/conceitos
        # (genérico: não sabemos o significado, então questionamos todos os relevantes)
        # Limita a 8 por rodada para não sobrecarregar
        focus = candidates[:8]
        if not focus:
            sys.exit(0)

        # Aprende: registra termos vistos
        for term in focus:
            tn = normalize(term)
            if tn not in state["known_terms"]:
                state["known_terms"][tn] = {
                    "term": term,
                    "times_seen": 0,
                    "narrow_bias_count": 0,
                    "first_seen": datetime.utcnow().isoformat() + "Z",
                }
            state["known_terms"][tn]["times_seen"] += 1
        save_state(state)

        # Viés conhecido? (termo já interpretado restritamente antes)
        biased = [t for t in focus
                  if state["known_terms"].get(normalize(t), {}).get("narrow_bias_count", 0) >= 2]

        # Constrói questionamentos GENÉRICOS
        lines = []
        for term in focus:
            lines.append(
                f"'{term}': que premissa VOCÊ está assumindo sobre isto? "
                f"É a ÚNICA interpretação? Que subsets/contextos você NÃO considerou?"
            )

        bias_warning = ""
        if biased:
            bias_warning = (
                f" ALERTA DE VIÉS: você já interpretou {', '.join(biased)} de forma RESTRITA antes. "
                "Amplie obrigatoriamente a interpretação."
            )

        hook_event = (data.get("hook_event_name") if isinstance(data, dict) else None) or "UserPromptSubmit"

        additional = {
            "hookSpecificOutput": {
                "hookEventName": hook_event,
                "additionalContext": (
                    "[PROBE GENÉRICO DE PREMISSAS] Não restrinja a interpretação. "
                    "Para cada termo abaixo, questione sua premissa ANTES de assumir:\n"
                    + "\n".join(" - " + l for l in lines)
                    + "\nREGRA: se qualquer termo for abrangente (domínio, categoria, setor, "
                    "conceito amplo), considere TODOS os subcontextos possíveis ou PERGUNTE "
                    "ao usuário qual subset ele quer. Não assuma o primeiro sentido que veio à cabeça."
                    + bias_warning
                )
            }
        }
        print(json.dumps(additional))
        sys.exit(0)
    except Exception:
        sys.exit(0)

if __name__ == "__main__":
    main()
