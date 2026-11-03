#!/usr/bin/env python3
"""
Bias Tracker — Aprende quais termos o modelo interpreta RESTRITAMENTE.

Analisa a saída do modelo (tool results, respostas) e detecta sinais de
interpretação restrita:
- "focando em X", "os principais são", "apenas X", "basicamente X"
- pouca diversidade de subcontextos para termo sabidamente abrangente

Registra narrow_bias_count no estado. Quando >= 2, a assumption-probe
passa a emitir ALERTA DE VIÉS obrigando ampliação.

Auto-alimenta: quanto mais o modelo restringe, mais alerts são gerados.

Sem matchers: dispara em qualquer contexto.
Fail-open: qualquer erro resultado em saida 0.
"""
import sys
import json
import os
import unicodedata

STATE_FILE = os.path.expanduser("~/.config/opencode/reasoning-state/assumption-probes.json")

NARROW_SIGNALS = [
    "focando em", "foco em", "os principais", "principalmente",
    "apenas", "somente", "basicamente", "em suma", "o essencial",
    "de forma simplificada", "em geral", "tipicamente", "normalmente",
    "o mais comum", "o mais importante", "o principal",
    "focusing on", "mainly", "primarily", "only", "just", "essentially",
    "the main", "typically", "generally", "the most important",
]

def normalize(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii").lower()

def main():
    try:
        raw = sys.stdin.read()
        if not raw:
            sys.exit(0)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {"raw": raw}

        # Texto a analisar (resultado de tool ou resposta)
        text = ""
        if isinstance(data, dict):
            text = json.dumps({
                k: data.get(k) for k in ("tool_result", "result", "response", "output", "text")
            }, ensure_ascii=False)
        else:
            text = raw

        text_norm = normalize(text)

        # Detecta sinais de restrição
        found_signals = [s for s in NARROW_SIGNALS if normalize(s) in text_norm]
        if not found_signals:
            sys.exit(0)

        # Carrega estado e marca TODOS os termos conhecidos vistos recentemente
        try:
            os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
            state = {}
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    state = json.load(f)
        except Exception:
            state = {"known_terms": {}, "narrow_bias_watch": {}, "round": 0}

        if "known_terms" not in state:
            state["known_terms"] = {}

        # Estratégia: se há sinal de restrição e há termos conhecidos no texto,
        # incrementa viés para os termos que aparecem no texto restrito.
        affected = []
        for tn, info in state["known_terms"].items():
            term_original = info.get("term", tn)
            if normalize(term_original) and normalize(term_original) in text_norm:
                info["narrow_bias_count"] = info.get("narrow_bias_count", 0) + 1
                affected.append(term_original)

        try:
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

        if not affected:
            sys.exit(0)

        hook_event = (data.get("hook_event_name") if isinstance(data, dict) else None) or "PostToolUse"

        additional = {
            "hookSpecificOutput": {
                "hookEventName": hook_event,
                "additionalContext": (
                    "[BIAS TRACKER] Detectada interpretação RESTRITA (sinais: "
                    + ", ".join(f"'{s}'" for s in found_signals[:3]) + "). "
                    + f"Termos marcados com viés: {', '.join(affected[:5])}. "
                    "Nas próximas interações com esses termos, você será FORÇADO a ampliar. "
                    "Agora: reformule considerando subsets/contextos que você ignorou."
                )
            }
        }
        print(json.dumps(additional))
        sys.exit(0)
    except Exception:
        sys.exit(0)

if __name__ == "__main__":
    main()
