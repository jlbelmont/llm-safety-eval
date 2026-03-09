# Model Backends

## Local
- **Ollama**: `api_type=ollama`, default `http://localhost:11434`. Suitable for fast iteration with quantized models.
- **vLLM**: `api_type=vllm`, OpenAI-compatible route `http://localhost:8000/v1`.
- **llama.cpp server**: `api_type=llamacpp`, lightweight CPU/GPU inference.
- **Text Generation Inference (TGI)**: `api_type=text-generation-inference` at `http://localhost:8081`.

## Remote
- **OpenAI-compatible APIs**: Example config for GPT-4o using `provider_id: openai` and `api_key_env: OPENAI_API_KEY`.

## Mock
- **mock**: Deterministic responses for dry runs and tests; avoids network calls.

## Switching Backends
- Select provider in `configs/providers.yaml`.
- Map models to providers in `configs/models.yaml` (for example, `llama3_ollama` uses the `ollama` provider).
- Use `configs/matrix_ollama.yaml` for a pilot that compares `gpt4o_api` with `llama3_ollama`.
- The client registry instantiates adapters per `api_type`; unsupported types fall back to the mock client for safety.
- Execution guard: network calls happen only if `execute=True` is passed and `LSE_ALLOW_NETWORK=1` is set in the environment. Otherwise adapters return stub responses.
- Optional metadata: `model_version` (models.yaml) and `provider_notes` (providers.yaml) are captured in snapshots and metadata.
- Optional rate control: `rate_limit_per_min` and `backoff_seconds` can be set per provider for polite usage.
- Backoff is enforced client-side as minimal spacing between requests; adjust `backoff_seconds` to fit your deployment.
- Token-bucket limit: set `max_requests_per_minute` to enable a simple token bucket in adapters; uses best-effort sleep with jitter.
- Logged per response: model_id, model_name, provider_id, prompt metadata, generation parameters, raw text, latency, timestamp, heuristics. Use these fields for backend comparisons.
