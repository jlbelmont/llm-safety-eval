# Threat Model

## Adversary Goals
- Elicit restricted code-generation behavior from aligned LLMs.
- Probe partial or unsafe compliance under prompt obfuscation, roleplay, or decomposition.

## Adversary Capabilities
- Text-only prompts; no tool or code execution privileges.
- Access to public model endpoints or local inference servers.

## Out of Scope
- Real exploit development, malware distribution, device-specific payloads.
- Physical device access or side-channel attacks.

## Defensive Controls in Study
- Safety prefixes and sanitization transforms.
- Refusal heuristics (string matching / classifiers) tracked but not enforced.
- Human labeling to categorize compliance levels.

## Ethical Guardrails
- Non-operational prompts with placeholders.
- Artifacts are for analysis; do not deploy or execute outputs.
