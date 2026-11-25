#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UserPromptSubmit - detecta pedido de desenvolvimento e injeta a ordem do handler. Fail-open."""
import sys, re, os

try:
    raw = sys.stdin.read()
    prompt = ""
    if raw:
        try:
            import json
            d = json.loads(raw)
            prompt = str(d.get("prompt") or d.get("user_prompt") or "")
        except Exception:
            prompt = raw
    if not prompt:
        prompt = os.environ.get("PROMPT", "") or os.environ.get("USER_PROMPT", "")

    DEV = re.compile(
        r"(codig|code|bug|fix|refactor|migrat|implement|feature|api|endpoint|test|"
        r"deploy|function|classe|handler|integrat|compile|build|erro|error|"
        r"corrigir|melhorar o codigo|desenvolv)",
        re.I,
    )
    if DEV.search(prompt):
        sys.stdout.write(
            "[dev-handler] Tarefa de codigo detectada. Ordem: "
            "(1) trace Avaliando 6/12/20 -> (2) decision.json -> "
            "(3) diff minimo -> (4) verify com numeros. Nao pule e nao divague.\n"
        )
except Exception:
    pass
sys.exit(0)
