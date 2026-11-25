#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SessionStart - injeta as regras do dev-handler. Fail-open."""
import sys, os
try:
    rules = os.path.join(os.path.dirname(__file__), "..", "instructions", "DEV-HANDLER-RULES.md")
    if os.path.exists(rules):
        sys.stdout.write("[dev-handler] Para tarefas de codigo: trace Avaliando (6/12/20) -> decision.json -> diff minimo -> verify com numeros. Nao explique por 7 min.\n")
except Exception:
    pass
sys.exit(0)
