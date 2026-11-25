#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stop - avisa se codigo foi escrito sem evidencia de verificacao. Fail-open."""
import sys, os, json
try:
    raw = sys.stdin.read()
    ws = os.environ.get("WORKSPACE") or os.getcwd()
    dec = os.path.join(ws, "decision.json")
    if not os.path.exists(dec):
        sys.exit(0)
    d = json.load(open(dec, encoding="utf-8"))
    verify = d.get("verify", [])
    if not verify:
        sys.stderr.write("[dev-handler] AVISO: decision.json sem comandos de verify. Cite o que foi verificado antes de terminar.\n")
except Exception:
    pass
sys.exit(0)
