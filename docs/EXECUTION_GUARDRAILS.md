# Execution Guardrails

- Network/model calls are **disabled by default**. Clients return stub responses unless both conditions hold:
  1. `execute=True` is passed to the client `generate` method, and
  2. Environment variable `LSE_ALLOW_NETWORK=1` is set.
- This prevents accidental live calls during development and CI.
- When enabling, ensure prompts remain non-operational and outputs are not executed.
- Suggested usage pattern: set `LSE_ALLOW_NETWORK=1` in a controlled shell, pass `execute=True` explicitly in custom scripts, and log all requests/responses.
