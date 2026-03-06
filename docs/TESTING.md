# Testing

- Run unit tests (mock-only): `pytest`
- Validate configs against JSON Schemas: `python scripts/validate_configs.py`
- Lint/format (optional): `ruff .` and `black .`
- No network/model calls occur during tests; clients stay in stub mode unless `LSE_ALLOW_NETWORK=1` and `execute=True` are used explicitly.
- To verify stub behavior, keep `LSE_ALLOW_NETWORK` unset; CLI runs stay non-operational by default.
- Matplotlib is optional; plotting tests are light and skip gracefully if import fails.
- Fixture: use `python scripts/generate_fixture_run.py` to create a deterministic mock run for demos/tests.
- Lint prompt suite: `python scripts/lint_prompt_suite.py`; dry-run matrix: `python scripts/dry_run_matrix.py`.
