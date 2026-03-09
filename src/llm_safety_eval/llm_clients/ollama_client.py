from __future__ import annotations

from typing import Any, Dict

import httpx

from .base import GenerationResult, LLMClient, allow_network, require_network
from ..data_models import ModelConfig, ProviderConfig


class OllamaClient(LLMClient):
    """Ollama local inference client with the same response schema as other backends."""

    def __init__(self, model_config: ModelConfig, provider_config: ProviderConfig) -> None:
        super().__init__(model_config, provider_config)

    def generate(self, prompt: str, parameters: Dict[str, Any], execute: bool = False) -> GenerationResult:
        if not (execute and allow_network()):
            text = f"[ollama stub for {self.model_name}]"
            return GenerationResult(text=text, latency_ms=None, raw={"prompt": prompt, "params": parameters})

        require_network(execute)
        self._respect_rate_limit()
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": parameters,
        }
        timeout_seconds = self._timeout_seconds(30.0)
        timeout = httpx.Timeout(connect=10.0, read=timeout_seconds, write=30.0, pool=30.0)
        with httpx.Client(timeout=timeout) as client:
            response = client.post(f"{self.provider_config.base_url}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return GenerationResult(
                text=data.get("response", ""),
                latency_ms=response.elapsed.total_seconds() * 1000,
                raw=data,
            )
