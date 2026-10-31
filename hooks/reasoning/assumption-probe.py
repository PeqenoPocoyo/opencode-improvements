#!/usr/bin/env python3
"""
Assumption Probe — Questionamento de Premissas (auto-expansível).

O modelo frequentemente interpreta termos amplos de forma RESTRITA
(ex: "indústria 4.0" -> só motores/gêmeo digital, ignorando robótica,
agro, café, manufaturas discretas).

Esta hook força o modelo a questionar SUAS premissas de interpretação:
"Será que o usuário quer que eu considere X como Y?"

A hook CRESCE SOZINHA: cada termo ambíguo novo identificado é
adicionado ao arquivo de probes, que serve de memória para conversas
futuras.

Sem matchers: dispara em qualquer contexto.
Fail-open: qualquer erro resultado em saida 0.
"""
import sys
import json
import os
import re
from datetime import datetime

# Onde os probes vivem (crescem com o uso)
PROBE_FILES = [
    os.path.join(os.getcwd(), "configs", "assumption-probes.json"),
    os.path.expanduser("~/.config/opencode/assumption-probes.json"),
]

# Seed mínimo: pares termo -> interpretações possíveis
SEED_PROBES = {
    "dança": ["ballet", "dança contemporânea", "dança de salão", "break", "sapateado", "qual estilo?"],
    "indústria": ["manufatura discreta", "processo contínuo", "agro", "mineração", "alimentos", "qual setor?"],
    "indústria 4.0": ["IIoT", "gêmeo digital", "robótica", "MAN", "agro 4.0", "visão além de motores?"],
    "iiot": ["sensores", "gateway", "edge", "cloud", "protocolos (MQTT/OPC-UA)", "manufatura discreta x contínua"],
    "automação": ["CLP/PLC", "SCADA", "robótica", "MES", "predial", "qual camada?"],
    "café": ["agricultura", "torrefação", "máquinas de café", "bebida", "qual contexto?"],
    "motor": ["elétrico", "combustão", "servo", "passo", "qual tipo?"],
    "arte": ["visual", "musical", "cênica", "digital", "qual forma?"],
    "esporte": ["futebol", "eSports", "automobilismo", "qual modalidade?"],
    "cidade": ["planejamento urbano", "mobilidade", "habitação", "qual aspecto?"],
    "energia": ["elétrica", "renovável", "solar", "eólica", "qual fonte?"],
    "saúde": ["clínica", "hospitalar", "preventiva", "dispositivos", "qual domínio?"],
    "escola": ["ensino fundamental", "médio", "técnico", "superior", "qual nível?"],
    "música": ["produção", "performance", "streaming", "instrumento", "qual contexto?"],
    "robô": ["industrial", "colaborativo", "móvel", "serviço", "qual tipo?"],
    "manufatura": ["discreta", "por processo", "job shop", "lote", "qual modo?"],
}

def load_probes():
    for p in PROBE_FILES:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f), p
            except Exception:
                pass
    return dict(SEED_PROBES), PROBE_FILES[-1]

def save_probes(probes, path):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(probes, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def find_terms(text, probes):
    """Encontra termos semente presentes no texto."""
    found = []
    text_lower = text.lower()
    for term in probes:
        if term.lower() in text_lower:
            found.append(term)
    return found

def detect_new_ambiguous(text, probes):
    """Heurística para detectar NOVOS termos amplos (auto-expansão da hook).

    Critério: palavra com 5+ letras, título ou substantivo comum,
    que não está nos probes e aparece em contexto de dúvida/abrangência.
    """
    new_terms = []
    # palavras candidatas (5+ letras, alfabéticas)
    candidates = re.findall(r'\b[a-záàâãéêíóôõúç]{5,}\b', text.lower())
    for w in candidates:
        if w in probes:
            continue
        # heurística simples: palavras que são categorias amplas conhecidas
        # ou que terminam em sufixos de domínio
        if any(w.endswith(s) for s in ["ção", "mento", "ência", "ano", "ista"]):
            new_terms.append(w)
    # dedup, máx 3 novas por rodada (para não poluir)
    return list(dict.fromkeys(new_terms))[:3]

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            sys.exit(0)

        probes, probe_path = load_probes()

        # Extrair texto do prompt/contexto
        try:
            data = json.loads(input_data)
            text = data.get("prompt", data.get("message", data.get("text", input_data)))
        except json.JSONDecodeError:
            text = input_data

        found = find_terms(text, probes)
        new_terms = detect_new_ambiguous(text, probes)

        # AUTO-EXPANSÃO: adicionar novos termos como probes pendentes
        grew = False
        for term in new_terms:
            if term not in probes:
                probes[term] = ["(interpretação a questionar)",
                                "o que exatamente o usuário quer dizer com isto?"]
                grew = True
        if grew:
            save_probes(probes, probe_path)

        if not found and not new_terms:
            sys.exit(0)

        # Construir questionamentos
        questions = []
        for term in found:
            interps = probes[term]
            formatted = ", ".join(f"'{i}'" for i in interps if not i.startswith("("))
            questions.append(
                f"Você está interpretando '{term}' de forma RESTRITA? "
                f"Considere também: {formatted}. "
                f"PERGUNTE-SE: o usuário quis dizer tudo isso ou só um subset?"
            )

        if new_terms:
            questions.append(
                f"Termos amplos detectados (novos probes registrados): {', '.join(new_terms)}. "
                f"Antes de assumir significado, QUESTIONE a abrangência."
            )

        additional = {
            "hookSpecificOutput": {
                "hookEventName": data.get("hook_event_name", "UserPromptSubmit") if isinstance(data, dict) else "UserPromptSubmit",
                "additionalContext": (
                    "[PROBE DE PREMISSAS] Você pode ter interpretado algo de forma restrita. "
                    + " ".join(questions) + " "
                    "REGRA: não restrinja o sentido do usuário à sua primeira interpretação. "
                    "Se o termo é abrangente, considere TODOS os setores/contextos possíveis "
                    "ou pergunte qual o usuário quer. "
                    + (f"(hooks auto-expandida: {len(new_terms)} novos probes salvos)" if grew else "")
                )
            }
        }
        print(json.dumps(additional))
        sys.exit(0)
    except Exception:
        sys.exit(0)

if __name__ == "__main__":
    main()
