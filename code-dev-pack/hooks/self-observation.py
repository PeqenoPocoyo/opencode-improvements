#!/usr/bin/env python3
"""Self-Observation Hook — Detecta padrões negativos nas respostas do agente.

Analisa a saída do agente e identifica:
- Admissões de erro ("não funciona", "falhou", "bug")
- Incerteza ("não tenho certeza", "talvez", "possivelmente")
- Retrabalho ("vou corrigir", "ajustar", "refazer")
- Limitações ("não consigo", "não é possível", "limitação")

Registra observações negativas em validation.json para auto-melhoria
sem depender de feedback do usuário.

Fail-open: qualquer erro resulta em saída 0.
"""
import sys
import os
import json
import re
from datetime import datetime

# Padrões de observação negativa
NEGATIVE_PATTERNS = {
    "error_admission": [
        r"(?i)n[aã]o funciona",
        r"(?i)falhou",
        r"(?i)bug",
        r"(?i)erro",
        r"(?i)quebrou",
        r"(?i)crash",
        r"(?i)exception",
        r"(?i)traceback",
    ],
    "uncertainty": [
        r"(?i)n[aã]o tenho certeza",
        r"(?i)talvez",
        r"(?i)possivelmente",
        r"(?i)provavelmente",
        r"(?i)n[aã]o sei",
        r"(?i)pode ser",
        r"(?i)acho que",
    ],
    "rework": [
        r"(?i)vou corrigir",
        r"(?i)ajustar",
        r"(?i)refazer",
        r"(?i)tentar novamente",
        r"(?i)revisar",
        r"(?i)melhorar",
        r"(?i)aprimorar",
    ],
    "limitation": [
        r"(?i)n[aã]o consigo",
        r"(?i)n[aã]o é possível",
        r"(?i)limitaç[aã]o",
        r"(?i)restric[aã]o",
        r"(?i)n[aã]o suporta",
        r"(?i)nao funciona bem",
    ],
}

def analyze_text(text):
    """Analisa texto e retorna observações negativas encontradas."""
    observations = []
    for category, patterns in NEGATIVE_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                observations.append({
                    "category": category,
                    "pattern": pattern,
                    "count": len(matches),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                })
    return observations

def load_validation():
    """Carrega validation.json."""
    try:
        with open('validation.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"resources": {}}

def save_validation(data):
    """Salva validation.json."""
    try:
        with open('validation.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def main():
    try:
        input_data = sys.stdin.read()
        if not input_data:
            sys.exit(0)
        
        try:
            data = json.loads(input_data)
            text = data.get('response', data.get('text', ''))
            resource = data.get('resource', '')
        except json.JSONDecodeError:
            text = input_data
            resource = ''
        
        if not text:
            sys.exit(0)
        
        observations = analyze_text(text)
        
        if observations and resource:
            # Registrar observação negativa no validation.json
            validation = load_validation()
            if resource in validation.get('resources', {}):
                res = validation['resources'][resource]
                neg_count = res.get('feedback_negative', 0)
                res['feedback_negative'] = neg_count + len(observations)
                res['last_negative_observation'] = datetime.utcnow().isoformat() + "Z"
                res['negative_observations'] = observations
                save_validation(validation)
                
                # Se 2+ feedbacks negativos, reverter para raw
                if res['feedback_negative'] >= 2:
                    res['state'] = 'raw'
                    res['reverted_date'] = datetime.utcnow().isoformat() + "Z"
                    res['reverted_reason'] = 'auto-observation: 2+ negative patterns detected'
                    save_validation(validation)
                    print(f"⚠️ Recurso {resource} revertido para raw (auto-observação negativa)", file=sys.stderr)
        
        # Reportar observações (para logging)
        if observations:
            print(f"📊 {len(observations)} observações negativas detectadas", file=sys.stderr)
            for obs in observations:
                print(f"  - {obs['category']}: {obs['count']} ocorrência(s)", file=sys.stderr)
        
        sys.exit(0)
        
    except Exception:
        sys.exit(0)

if __name__ == "__main__":
    main()