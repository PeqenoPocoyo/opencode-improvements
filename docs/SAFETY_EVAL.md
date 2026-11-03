# Safety Evaluation Loop

## Purpose
Test and improve proactive safety behavior across random/benign/harmful scenarios without relying on a fixed topic list.

## Files
- `configs/safety-scenarios.json`: generic scenario prompts + expected outcomes (`refuse`, `allow`, `clarify`).
- `scripts/safety_eval.py`: scores a JSON of model responses.

## Workflow (loop)
1. Load `configs/safety-scenarios.json`.
2. For each scenario, generate a model response (manually or via your harness).
3. Save responses as `{ "S001": "model answer...", ... }` in `responses.json`.
4. Run:
   ```bash
   python scripts/safety_eval.py configs/safety-scenarios.json responses.json
   ```
5. If score < 1.0, update `instructions/SUPERPROMPT.md` safety protocol and skill routing, then re-test.
6. Add new generic scenarios (not specific topics) to broaden coverage.

## Notes
- Scenarios are intentionally generic; do not restrict to listed examples.
- Do not store operational harmful details; only test prompts and expected outcomes.
- Keep safety policy above any skill invocation.